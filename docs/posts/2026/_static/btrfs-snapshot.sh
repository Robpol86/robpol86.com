#!/bin/sh

# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot.sh
# Save as (chmod +x): /sbin/btrfs-snapshot

# Usage: btrfs-snapshot [OPTIONS] SNAPSHOT_NAME
#
# Take named BTRFS snapshots with comments.
#
# TODO Long description goes here. Explain SNAPSHOT_NAME will become
# /sysroot/snapshots/SNAPSHOT_NAME. TODO also show examples.
#
# Options:
#   -c comment  Snapshot description. If comment is '-' then comment will be
#               read from stdin.
#   -d dir      Snapshots directory, relative to the subvolume.
#               Default: @SNAPSHOTS_DIR
#   -h          Display this help and exit.
#   -l          List existing snapshots and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

set -o errexit  # Exit script if a command fails.
set -o nounset  # Treat unset variables as errors and exit immediately.

COMMENT=
SNAPSHOTS_DIR=.bsnaps
LIST_ONLY=
SUBVOLUME_DIR=/  # @MODULE-SETUP-REPLACE@
VERBOSE=
SNAPSHOT_NAME=

# Parse command line arguments.
while getopts :c:d:hls:v OPT; do
  case "$OPT" in
    \?) echo "unknown flag: '$OPTARG'" >&2
        exit 1 ;;
    :) echo "flag needs an argument: '$OPTARG'" >&2
       exit 1 ;;
    c) COMMENT="$OPTARG" ;;
    d) SNAPSHOTS_DIR="$OPTARG" ;;
    h) grep -A40 -m1 "^# Usage:" "$0" |grep -B40 -m1 '^ *$' |
        sed -e 's/^# \?//' \
            -e "s|@SNAPSHOTS_DIR|$SNAPSHOTS_DIR|" \
            -e "s|@SUBVOLUME_DIR|$SUBVOLUME_DIR|"
       exit 0 ;;
    l) LIST_ONLY=true ;;
    s) SUBVOLUME_DIR="$OPTARG" ;;
    v) VERBOSE=true ;;
  esac
done
shift "$((OPTIND-1))"
if [ $# != 1 ] && [ ${LIST_ONLY:-false} = false ]; then
  echo "'btrfs-snapshot' requires exactly 1 argument." >&2
  echo "See 'btrfs-snapshot -h'." >&2
  exit 1
fi
SNAPSHOT_NAME="${1:-}"

# Enable verbose/debug.
if [ ${VERBOSE:-false} = true ]; then
  set -o xtrace  # Print commands before executing them.
fi

# Check if SUBVOLUME_DIR is a BTRFS fs and subvolume.
if ! stat -f --format=%T "$SUBVOLUME_DIR" |grep -q '^btrfs$'; then
  echo "Path '$SUBVOLUME_DIR' is not a BTRFS filesystem." >&2
  exit 1
fi
if ! stat --format=%i "$SUBVOLUME_DIR" |grep -q '^256$'; then
  echo "Path '$SUBVOLUME_DIR' is not a BTRFS subvolume." >&2
  exit 1
fi

SNAPSHOTS_DIR_FULL="${SUBVOLUME_DIR%/}/${SNAPSHOTS_DIR%/}"
read -r UUID < "${KERNEL_UUID_FILE:-/proc/sys/kernel/random/uuid}"

# Y64 encode function.
y64_encode() {
  base64 -w0 |sed -e 's/+/./g' -e 's|/|_|g' -e 's/=/-/g'
}

# List only.
if [ ${LIST_ONLY:-false} = true ]; then
  # Get list of snapshots.
  snapshot_list_file="/tmp/bsnaps-snapshot_list.$UUID.txt"
  if ! btrfs subvolume list -rst / > "$snapshot_list_file"; then  # TODO test with no snapshots, still exit 0?
    echo "Failed to get list of snapshots." >&2
    echo "Are you running this as root or with sudo?" >&2
    exit 1
  fi
  if ! grep -q -P "\t.bsnaps/" "$snapshot_list_file"; then  # TODO antipattern, move into awk, echo stderr and exit.
    echo "No snapshots found." >&2
    exit 1
  fi

  awk -v FS='\t+' '
    BEGIN {
      padding_id = 3
      padding_date = 20
      padding_running = 1
      padding_name = 15
    }

    # Skip irrelevant snapshots.
    !/\t.bsnaps\// { next }

    # First pass.
    NR==FNR {
      # Dynamic name column.
      # TODO.
      next
    }

    # Print header.
    BEGINFILE {
      if (NR!=FNR) {
        printf("%-"padding_id"s %-"padding_date-7"s %-"padding_running+7"s %-"padding_name"s   %s\n",
               "ID", "Date", "Running?", "Name", "Comment")
        hr = sprintf("%*s", 79, "-")
        gsub(/ /, "-", hr)
        print(hr)
      }
    }

    # Y64 decode function.
    function y64_decode(encoded) {
      gsub(/\./, "+", encoded)
      gsub(/_/, "/", encoded)
      gsub(/-/, "=", encoded)
      # TODO avoid getline.
      cmd = "printf %s " "\"" encoded "\" | base64 -d"
      first = 1
      while ((cmd | getline line) > 0) {
        if (first) { decoded = line; first = 0 }
        else       { decoded = decoded "\n" line }
      }
      close(cmd)
      return decoded
    }

    # Second pass.
    NR!=FNR {
      # Extract fields.
      id = $1
      date = $5
      split($6, arr, "/")
      name = arr[2]
      running = substr(arr[3], 1, 1) == "1" ? "*" : ""
      comment = y64_decode(substr(arr[3], 2))

      # Print row.
      if (!comment) {
        # No comment.
        printf("%-"padding_id"s %-"padding_date"s %-"padding_running"s %s\n",
               id, date, running, name)
      } else if (comment !~ /\n/) {
        # Single-line comment.
        printf("%-"padding_id"s %-"padding_date"s %-"padding_running"s %-"padding_name"s   %s\n",
               id, date, running, name, comment)
      } else {
        # Multi-line comment.
        split(comment, arr, "\n")
        printf("%-"padding_id"s %-"padding_date"s %-"padding_running"s %-"padding_name"s   %s\n",
               id, date, running, name, arr[1])
        for (i=2; i<=length(arr); i++) {
          printf("%*s", padding_id+padding_date+padding_running+padding_name+6, "")
          print arr[i]
        }
      }
    }
  ' "$snapshot_list_file" "$snapshot_list_file"


  exit 0
  set -- "$SNAPSHOTS_DIR_FULL"/*/"$METADATA_FILE"
  if [ ! -e "$1" ]; then
    echo "No snapshots found." >&2
    exit 1
  fi
  stat_output_file="/tmp/nfo_mtimes.$UUID.txt"
  stat -c "%y %n" "$@" |sort > "$stat_output_file"
  y_col_width="$(stat -c "%y " "$1" |wc -c)"
  name_col_width="$(grep -hPo ":name:\K.+" "$@" |wc -L)"  # TODO -L is GNU, avoid
  # shellcheck disable=SC2016
  cut -c"$y_col_width"- "$stat_output_file" |xargs awk -v y_col_width="$y_col_width" -v name_col_width="$name_col_width" '
    BEGIN {
      col_padding_mtime = 20
      col_padding_running = 1
      col_padding_name = 15
      # Dynamic name column.
      max_padding = 30
      if (name_col_width > max_padding) col_padding_name = max_padding
      else if (name_col_width > col_padding_name) col_padding_name = col_length
      # Print header.
      printf("%-"col_padding_mtime-7"s %-"col_padding_running+7"s %-"col_padding_name"s   %s\n", "Date", "Running?", "Name", "Comment")
      hr = sprintf("%*s", 79, "-")
      gsub(/ /, "-", hr)
      print(hr)
    }
    NR==FNR {  # First file.
      # in e.g.  2026-07-29 10:36:22.135998514 +0000 /snapshots/uuiduuid-uuid-uuiduuid/.snapshot.nfo
      # out e.g. mtimes["/snapshots/uuiduuid-uuid-uuiduuid/.snapshot.nfo"]="2026-07-29 10:36:22"
      filedate = gensub(/(^[0-9 :-]+).*/, "\\1", "1")
      filepath = substr($0, y_col_width)
      mtimes[filepath] = filedate
      next
    }
    BEGINFILE {
      mtime = mtimes[FILENAME]
      snapshot_name = ""
      running = ""
      in_comment = 0
    }
    match($0, /^:name:(.+)/, arr) {
      snapshot_name = arr[1]
    }
    /^:running:t/ { running = "*"; next }
    /^:comment:$/ {
      # No comment.
      printf("%-"col_padding_mtime"s %-"col_padding_running"s %s\n", mtime, running, snapshot_name)
      nextfile
    }
    /^:comment:[^-]/ {
      # Single-line commment.
      match($0, /^:comment:(.+)/, arr)
      comment = arr[1]
      printf("%-"col_padding_mtime"s %-"col_padding_running"s %-"col_padding_name"s   %s\n", mtime, running, snapshot_name, comment)
      nextfile
    }
    /^:comment:-/ {
      # Multil-line comment begin.
      in_comment = 1
      next
    }
    /^:comment-end:/ { nextfile }
    in_comment==1 {
      in_comment = 2
      printf("%-"col_padding_mtime"s %-"col_padding_running"s %-"col_padding_name"s   %s\n", mtime, running, snapshot_name, $0)
      next
    }
    in_comment==2 {
      printf("%*s", col_padding_mtime+col_padding_running+col_padding_name+5, "")
      print
    }
  ' "$stat_output_file"
  exit 0
fi

# Check if snapshot name has invalid characters.
# TODO

COMMENT_B64=

# Encode comment.
if [ "${COMMENT:-}" = "-" ]; then
  if [ -t 0 ]; then
    echo "Press Ctrl+D to finish" >&2
  fi
  COMMENT_B64="$(y64_encode)"
elif [ -n "${COMMENT:-}" ]; then
  COMMENT_B64="$(echo "$COMMENT" |y64_encode)"
fi
# TODO if comment > limit: fail.

IS_READONLY=
SNAPSHOT_PATH=

# Determine snapshot path.
SNAPSHOT_PATH_MKDIR="$SNAPSHOTS_DIR_FULL/$SNAPSHOT_NAME"
if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
  IS_READONLY=true
  SNAPSHOT_PATH="$SNAPSHOT_PATH_MKDIR/0$COMMENT_B64"
else
  SNAPSHOT_PATH="$SNAPSHOT_PATH_MKDIR/1$COMMENT_B64"
fi

# Fail if snapshot already exists.
if [ -e "$SNAPSHOT_PATH" ]; then
  echo "Snapshot '$SNAPSHOT_PATH' already exists." >&2
  # TODO like before, suggest -l
  exit 1
fi

#
# Done with checks. Above here nothing changed in the BTRFS filesystem. Below
# here is when the script starts making changes.
#

# Remount subvolume as readwrite if it is mounted as readonly.
if [ ${IS_READONLY:-false} = true ]; then
  if ! mount -oremount,rw "$SUBVOLUME_DIR"; then
    echo "Failed to remount '$SUBVOLUME_DIR' as read-write." >&2
    echo "Are you running this as root or with sudo?" >&2
    exit 1
  else
    echo "Remounted '$SUBVOLUME_DIR' as read-write"
  fi
fi

# Create snapshots parent directories.
if ! mkdir -p "$SNAPSHOT_PATH_MKDIR"; then
  echo "Failed to create directory '$SNAPSHOT_PATH_MKDIR'." >&2
  echo "Are you running this as root or with sudo?" >&2
  exit 1
fi

# Create snapshot
btrfs subvolume snapshot -r "$SUBVOLUME_DIR" "$SNAPSHOT_PATH"

# Remount subvolume as readonly if it was originally in that state.
if [ ${IS_READONLY:-false} = true ]; then
  mount -oremount,ro "$SUBVOLUME_DIR"
  echo "Remounted '$SUBVOLUME_DIR' as read-only"
fi

# TODO:
# - Abandon Y64, use safer characters, avoid '-'.
# - Running/not flag: r or _
# - Strip head/tail newlines/spaces in comment.
# - Refactor AGAIN:
#   - No need to mount before snapshot.
#   - Restore: use btrfs subvol ID: "ID 257 gen 251 top level 5 path snapshots/three-run"
#   - No metadata file, instead: .bsnaps/2026-08-02T10:48:01Z/snapshot-name/0MWNvbW1lbnQK
#     - dir/date/name/runningComment (0this-is-a-comment == not running, 1 = running with no comment)
#     - running is not b64 encoded, comment is, and that's catted to 0/1 prefix.
# - Snapshot name validation (no nl, / *, etc)
# - Delete all snapshots on me-mini and create four new ones with latest script.
#   - Restore middle snapshot manually with btrfs commands, then update -l to traverse and show 4-5 snapshots
#   - Create a new snapshot from the restored middle. Now there should be one more in -l.
# - @root and @home: can snapshots live in other subvols? Probably not.
# - Unify with other scripts? btrfs-snapshot [list|take|restore|delete|revert]
#   - Support non-root (arbitrary) subvolumes
#   - If restore uses the same list and unify not good, break out into own script: snapshot-list
#   - alias in rd.break as `bss`
#   - btrfs-snapshot list -p  # show paths instead of comments
# - Test with subvol_dir=.
# - Test with spaces in snapshot names (taking and listing).
# - Handle special characters in "snapshot name" e.g. *.
# - Checks:
#   - if snapshots-dir has a leading / is it the same as subvolume?
#     - subv=/my/sub/vol/ume; snapshots-dir=/snap/shots == /my/sub/vol/ume/snap/shots
# - Don't use awk.
# - Integration tests for take+restore interaction (tests/integration_tests/test_snapshot_take_restore.py)
# - Cleanup tmp files.
# - Test missing snapshot name in nfo file
# - Optimize: drop Dracut dependencies for POSIX shell tricks
# - Test different locales, does btrfs and other command outputs change (e.g. btrfs subv l otime timestamp)
# TODOs restore:
# - No no args or bad name list available snapshots
#   - To save typing in rd.break maybe prefix each snapshot with a number and let user specify snapshot-restore -1
# - Test take+restore multiple times, creating complex nesting.
# - Restore: mv nfo to .restored.17234567899
#   - If user makes a new snapshot from a restored one we don’t want a collision.
# - When run from mounted:
#       Restore 0:"name"?
#       Y
#       Restored 0 to default.
#       Reboot for changes to take effect.
#       Run "..." to revert.
# - When run from rd.break:
#       Restore 0:"name"?
#       Y
#       Remounted ... rw
#       Restored 0 to default.
#       Remounted ... ro
#       Run "..." to revert.
