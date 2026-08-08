#!/bin/sh

# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/btrfs-snapshot.sh
# Save as (chmod +x): /sbin/btrfs-snapshot

# Usage: btrfs-snapshot <command> [OPTIONS] [<args>]
#
# These are the available commands:
#   take        Create a btrfs snapshot of the subvolume.
#   list        TODO
#   restore     TODO
#   delete      TODO
#   revert      TODO
#
# Each command has its own -h. For example, see 'btrfs-snapshot take -h' for
# more information on creating snapshots.

# Usage: btrfs-snapshot take [OPTIONS] <snapshot-name>
#
# Take named btrfs snapshots with comments.
#
# Comments are Y64 encoded to make them path friendly. Snapshot names and comments
# are encoded into the snapshot directory path. An example:
#   .bsnaps/snapshot-name/0U2luZ2xlIGxpbmUgY29tbWVudC4-
# If the snapshot is taken when the btrfs subvolume is mounted it is considered
# a "running" snapshot, and this is recorded as a 1 in the snapshot directory
# path (e.g. .bsnaps/snapshot-name/1).
#
# Options:
#   -c comment  Snapshot description. If comment is '-' then comment will be
#               read from stdin.
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

# Usage: btrfs-snapshot list [OPTIONS]
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

# Usage: btrfs-snapshot restore [OPTIONS] <snapshot-name|snapshot-id>
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

# Usage: btrfs-snapshot delete [OPTIONS] <snapshot-name|snapshot-id>
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

# Usage: btrfs-snapshot revert [OPTIONS]
#
# TODO
#
# TODO long
#
# Options:
#   -h          Display this help and exit.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

set -o errexit  # Exit script if a command fails.
set -o nounset  # Treat unset variables as errors and exit immediately.
# shellcheck disable=SC3040  # TODO remove in ++v0.11.0 https://github.com/koalaman/shellcheck/pull/3305
set -o pipefail  # Exit script if pipes fail instead of just the last program.

SUBCOMMAND=
COMMENT=  # TODO s/^/TAKE_/
SUBVOLUME_DIR=/  # @MODULE-SETUP-REPLACE@
VERBOSE=

# Handle top level help (no args == -h).
if [ $# -eq 0 ] || [ "$1" = "-h" ]; then
  awk '
    /^# Usage:/ {doit=1}
    !/^#/ && doit==1 {exit}
    doit==1 {print substr($0, 3)}
  ' "$0"
  exit 0
fi

# Handle "--help" special case.
if [ "$1" = "--help" ]; then
  echo "unknown option: '--help'" >&2
  echo "See 'btrfs-snapshot -h'." >&2
  exit 1
fi

# Read subcommand and handle aliases.
case "$1" in
  create) SUBCOMMAND="take" ;;
  ls) SUBCOMMAND="list" ;;
  undo) SUBCOMMAND="revert" ;;
  take|list|restore|delete|revert) SUBCOMMAND="$1" ;;
  *) echo "unknown subcommand: '$1'" >&2
     echo "See 'btrfs-snapshot -h'." >&2
     exit 1 ;;
esac
shift

# Parse command line arguments.
case "$SUBCOMMAND" in
  take) GETOPTS=":c:hs:v" ;;
  *) GETOPTS=":hs:v" ;;
esac
while getopts "$GETOPTS" OPT; do
  case "$SUBCOMMAND-$OPT" in
    *-\?)   echo "unknown flag: '$OPTARG'" >&2
            exit 1 ;;
    *-:)    echo "flag needs an argument: '$OPTARG'" >&2
            exit 1 ;;
    *-h)    awk -v SUBCOMMAND="$SUBCOMMAND" -v SUBVOLUME_DIR="$SUBVOLUME_DIR" '
              /@SUBVOLUME_DIR/ {gsub(/@SUBVOLUME_DIR/, SUBVOLUME_DIR)}
              /^# Usage:/ && $4==SUBCOMMAND {doit=1}
              !/^#/ && doit==1 {exit}
              doit==1 {print substr($0, 3)}
            ' "$0"
            exit 0 ;;
    *-s)    SUBVOLUME_DIR="$OPTARG" ;;
    *-v)    VERBOSE=true ;;
    take-c) COMMENT="$OPTARG" ;;
    *)      echo "BUG" >&2
            exit 1 ;;
  esac
done
shift "$((OPTIND-1))"

# Enable verbose/debug.
if [ ${VERBOSE:-false} = true ]; then
  set -o xtrace  # Print commands before executing them.
fi

# Check if SUBVOLUME_DIR is a btrfs fs and subvolume.
if ! stat -f --format=%T "$SUBVOLUME_DIR" |grep -q '^btrfs$'; then
  echo "ERROR: Path '$SUBVOLUME_DIR' is not a btrfs filesystem." >&2
  exit 1
fi
if ! stat --format=%i "$SUBVOLUME_DIR" |grep -q '^256$'; then
  echo "ERROR: Path '$SUBVOLUME_DIR' is not a btrfs subvolume." >&2
  exit 1
fi

SNAPSHOTS_DIR="${SUBVOLUME_DIR%/}/.bsnaps"
read -r UUID < "${KERNEL_UUID_FILE:-/proc/sys/kernel/random/uuid}"

# Subcommand list.
if [ "$SUBCOMMAND" = "list" ]; then
  # Get list of snapshots.
  snapshot_list_file="/tmp/bsnaps-snapshot_list.$UUID.txt"
  if ! btrfs subvolume list -rst "$SUBVOLUME_DIR" > "$snapshot_list_file"; then
    echo "ERROR: Failed to get list of snapshots." >&2
    echo "Are you running this as root or with sudo?" >&2
    rm -f "$snapshot_list_file"
    exit 1
  fi
  if ! grep -q -P "\t.bsnaps/" "$snapshot_list_file"; then  # TODO eliminate anti-pattern.
    echo "No snapshots found." >&2
    rm -f "$snapshot_list_file"
    exit 1
  fi

  awk -v FS='\t+' '
    BEGIN {
      padding_id = 3
      padding_date = 20
      padding_running = 1
      padding_name = 15
      padding_name_max = 30
    }

    # Skip irrelevant snapshots.
    !/\t.bsnaps\// { next }

    # First pass.
    NR==FNR {
      # Dynamic name column.
      split($6, arr, "/")
      name_width = length(arr[2])
      if (name_width > padding_name_max) padding_name = padding_name_max
      else if (name_width > padding_name) padding_name = name_width
      next
    }

    # Print header.
    BEGINFILE {
      if (NR!=FNR) {
        printf("%-"padding_id"s  %-"padding_date-7"s %-"padding_running+7"s %-"padding_name"s  %s\n",
               "ID", "Date", "Running?", "Name", "Comment")
        hr = sprintf("%*s", 79, "-")
        gsub(/ /, "-", hr)
        print(hr)
      }
    }

    # Y64 decode function.
    function y64_decode(encoded) {
      if (!encoded) return encoded
      gsub(/\./, "+", encoded)
      gsub(/_/, "/", encoded)
      gsub(/-/, "=", encoded)
      # https://dnshane.wordpress.com/2017/03/10/decoding-base64-in-awk/
      # https://github.com/shane-kerr/AWK-base64decode
      # TODO abandon AGPL code, find another way to decode b64.
      # Initialize base64 decoder.
      for (i=0; i<26; i++) { BASE64[sprintf("%c", i+65)] = i; BASE64[sprintf("%c", i+97)] = i+26 }
      for (i=0; i<10; i++) BASE64[sprintf("%c", i+48)] = i+52
      BASE64["+"] = 62; BASE64["/"] = 63; BASE64["="] = -1
      result[1]=""
      n = 1
      # Decode base64.
      while (length(encoded) >= 4) {
        g0 = BASE64[substr(encoded, 1, 1)]
        g1 = BASE64[substr(encoded, 2, 1)]
        g2 = BASE64[substr(encoded, 3, 1)]
        g3 = BASE64[substr(encoded, 4, 1)]
        if (g0 == "") {
          printf("Unrecognized character %c in Base 64 encoded string\n", g0) >> "/dev/stderr"
          exit 1
        }
        if (g1 == "") {
          printf("Unrecognized character %c in Base 64 encoded string\n", g1) >> "/dev/stderr"
          exit 1
        }
        if (g2 == "") {
          printf("Unrecognized character %c in Base 64 encoded string\n", g2) >> "/dev/stderr"
          exit 1
        }
        if (g3 == "") {
          printf("Unrecognized character %c in Base 64 encoded string\n", g3) >> "/dev/stderr"
          exit 1
        }
        result[n++] = (g0 * 4) + int(g1 / 16)
        if (g2 != -1) {
          result[n++] = ((g1 * 16) % 256) + int(g2 / 4)
          if (g3 != -1) result[n++] = ((g2 * 64) % 256) + g3
        }
        encoded = substr(encoded, 5)
      }
      # Concat result array.
      decoded = ""
      for (i=1; i in result; i++) {
        decoded = decoded sprintf("%c", result[i])
        delete result[i]
      }
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
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %s\n",
               id, date, running, name)
      } else if (comment !~ /\n/) {
        # Single-line comment.
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %-"padding_name"s  %s\n",
               id, date, running, name, comment)
      } else {
        # Multi-line comment.
        split(comment, arr, "\n")
        printf("%-"padding_id"s  %-"padding_date"s %-"padding_running"s %-"padding_name"s  %s\n",
               id, date, running, name, arr[1])
        for (i=2; i<=length(arr); i++) {
          printf("%*s", padding_id+padding_date+padding_running+padding_name+6, "")
          print arr[i]
        }
      }
    }
  ' "$snapshot_list_file" "$snapshot_list_file"
  rm -f "$snapshot_list_file"
  
  exit 0
fi

# Subcommand take.
if [ "$SUBCOMMAND" = "take" ]; then
  # Parse subcommand arguments.
  if [ $# != 1 ]; then
    echo "'btrfs-snapshot take' requires exactly 1 argument." >&2
    echo "See 'btrfs-snapshot take -h'." >&2
    exit 1
  else
    snapshot_name="$1"
    shift
  fi

  # Check if snapshot name has invalid characters.
  # TODO

  # Encode comment.
  y64_encode() {
    base64 -w0 |sed -e 's/+/./g' -e 's|/|_|g' -e 's/=/-/g'
  }
  if [ "${COMMENT:-}" = "-" ]; then
    if [ -t 0 ]; then
      echo "Press Ctrl+D to finish" >&2
    fi
    comment_b64="$(y64_encode)"
  elif [ -n "${COMMENT:-}" ]; then
    comment_b64="$(printf "%s" "$COMMENT" |y64_encode)"
  else
    comment_b64=
  fi
  # TODO if comment > limit: fail.

  # Determine snapshot path.
  snapshot_path_mkdir="$SNAPSHOTS_DIR/$snapshot_name"
  if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
    is_readonly=true
    snapshot_path="$snapshot_path_mkdir/0$comment_b64"
  else
    is_readonly=
    snapshot_path="$snapshot_path_mkdir/1$comment_b64"
  fi

  # Fail if snapshot already exists.
  if [ -e "$snapshot_path" ]; then
    echo "ERROR: Snapshot '$snapshot_path' already exists." >&2
    echo "Run 'btrfs-snapshot list' to list existing snapshots." >&2
    exit 1
  fi

  #
  # Done with checks. Above here nothing changed in the btrfs filesystem. Below
  # here is when the script starts making changes.
  #

  # Remount subvolume as readwrite if it is mounted as readonly.
  if [ ${is_readonly:-false} = true ]; then
    if ! mount -oremount,rw "$SUBVOLUME_DIR"; then
      echo "ERROR: Failed to remount '$SUBVOLUME_DIR' as read-write." >&2
      echo "Are you running this as root or with sudo?" >&2
      exit 1
    else
      echo "Remounted '$SUBVOLUME_DIR' as read-write"
    fi
  fi

  # Create snapshots parent directories.
  if ! mkdir -p "$snapshot_path_mkdir"; then
    echo "ERROR: Failed to create directory '$snapshot_path_mkdir'." >&2
    echo "Are you running this as root or with sudo?" >&2
    exit 1
  fi

  # Create snapshot
  btrfs subvolume snapshot -r "$SUBVOLUME_DIR" "$snapshot_path"

  # Remount subvolume as readonly if it was originally in that state.
  if [ ${is_readonly:-false} = true ]; then
    mount -oremount,ro "$SUBVOLUME_DIR"
    echo "Remounted '$SUBVOLUME_DIR' as read-only"
  fi

  exit 0
fi

# Subcommand restore.
if [ "$SUBCOMMAND" = "restore" ]; then
  # Parse subcommand arguments.
  if [ $# != 1 ]; then
    echo "'btrfs-snapshot $SUBCOMMAND' requires exactly 1 argument." >&2
    echo "See 'btrfs-snapshot $SUBCOMMAND -h'." >&2
    exit 1
  elif ! btrfs subvolume list -rs "$SUBVOLUME_DIR" |awk -v ID="$1" '/^ID /{if ($2==ID) exit 0} ENDFILE{exit 1}'; then
    echo "ERROR: Cannot find btrfs snapshot ID '$1'." >&2
    echo "Run 'btrfs-snapshot list' to list existing snapshots." >&2
    exit 1
  else
    snapshot_id="$1"
    shift
  fi

  # Get the btrfs subvolume's device.
  subvolume_device="$(findmnt -nvo SOURCE "$SUBVOLUME_DIR")"

  # TODO: prompt user before making changes

  # Mount the snapshot as read-only.
  dir_restore_from="$SUBVOLUME_DIR/.bsnaps/restore-from-$UUID"
  mount -oremount,rw "$SUBVOLUME_DIR"
  mkdir -p "$dir_restore_from"
  mount -o "subvolid=$snapshot_id,ro" "$subvolume_device" "$dir_restore_from"

  # Clone the snapshot as read-write and set-default it.
  dir_restore_to="$SUBVOLUME_DIR/.bsnaps/restored-$UUID"
  btrfs subvolume snapshot "$dir_restore_from" "$dir_restore_to"
  btrfs subvolume set-default "$dir_restore_to"
  umount "$dir_restore_from"
  rmdir "$dir_restore_from"  # TODO || true

  # Remount $SUBVOLUME_DIR using the now-restored subvolume.
  new_id="$(btrfs subvolume get-default "$SUBVOLUME_DIR" |awk '/^ID /{print $2}')"
  umount "$SUBVOLUME_DIR"
  mount -o "subvolid=$new_id,ro" "$subvolume_device" "$SUBVOLUME_DIR"  # TODO if was rw don't ro.

  exit 0
fi

# Subcommand delete.
if [ "$SUBCOMMAND" = "delete" ]; then
  echo "TODO"
  exit 0
fi

# Subcommand revert.
if [ "$SUBCOMMAND" = "revert" ]; then
  echo "TODO"
  exit 0
fi

echo "BUG" >&2
exit 1

# TODO:
# - Strip head/tail newlines/spaces in comment.
#   - Only when creating. gensub, https://stackoverflow.com/questions/9175801/how-to-remove-leading-and-trailing-whitespaces
# - awk y64_encode/decode function defs in env variables set by shell script
# - All "block-scoped" variables should be lowercase
# - Snapshot name validation (no nl, / *, etc)
# - Test with LC_ALL=C and other values.
# - Test with malformed b64: warn and keep decoded in output
#   - Prefix/postifx magic string?
#   - \0 not supported in awk strings. How to handle?
# - Delete all snapshots on me-mini and create four new ones with latest script.
#   - Restore middle snapshot manually with btrfs commands, then update -l to traverse and show 4-5 snapshots
#   - Create a new snapshot from the restored middle. Now there should be one more in -l.
# - @root and @home: can snapshots live in other subvols? Probably not.
# - Support non-root (arbitrary) subvolumes
# - Alias in rd.break as `bss`
# - Test with subvol_dir=.
# - Test with spaces in snapshot names (taking and listing).
# - Handle special characters in "snapshot name" e.g. *.
# - Checks:
#   - if snapshots-dir has a leading / is it the same as subvolume?
#     - subv=/my/sub/vol/ume; snapshots-dir=/snap/shots == /my/sub/vol/ume/snap/shots
# - Replace grep/sed/etc with awk.
# - Integration tests for take+restore interaction (tests/integration_tests/test_snapshot_take_restore.py)
# - Cleanup tmp files.
# - Test missing snapshot name in nfo file
# - Optimize: drop Dracut dependencies for POSIX shell tricks
# - Test different locales, does btrfs and other command outputs change (e.g. btrfs subv l otime timestamp)
# - Reformat ubuntu and test all subcommands with no snapshots.
# - bss not a symlink, sed PROGRAM name to bss.
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
