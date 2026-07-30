#!/bin/sh

# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/snapshot-take.sh
# Save as (chmod +x): /sbin/snapshot-take

# Usage: snapshot-take [OPTIONS] SNAPSHOT_NAME
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
#   -p          Create snapshots directories as required. If this option is not
#               specified, the full path prefix of the snapshots directory must
#               already exist.
#   -s dir      Mounted subvolume directory.
#               Default: @SUBVOLUME_DIR
#   -v          Enable verbose/debug output.

set -o errexit  # Exit script if a command fails.
set -o nounset  # Treat unset variables as errors and exit immediately.

METADATA_FILE=.snapshot.nfo

COMMENT=
SNAPSHOTS_DIR=snapshots
LIST_ONLY=
PARENTS_CREATE=
SUBVOLUME_DIR=/  # @MODULE-SETUP-REPLACE@
VERBOSE=
SNAPSHOT_NAME=

# Parse command line arguments.
while getopts :c:d:hlps:v OPT; do
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
    p) PARENTS_CREATE=true ;;
    s) SUBVOLUME_DIR="$OPTARG" ;;
    v) VERBOSE=true ;;
  esac
done
shift "$((OPTIND-1))"
if [ $# != 1 ] && [ ${LIST_ONLY:-false} = false ]; then
  echo "'snapshot-take' requires exactly 1 argument." >&2
  echo "See 'snapshot-take -h'." >&2
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
SNAPSHOT_PATH="$SNAPSHOTS_DIR_FULL/$SNAPSHOT_NAME"
read -r UUID < "${KERNEL_UUID_FILE:-/proc/sys/kernel/random/uuid}"

# List only.
if [ ${LIST_ONLY:-false} = true ]; then
  set -- "$SNAPSHOTS_DIR_FULL"/*/"$METADATA_FILE"
  if [ ! -e "$1" ]; then
    echo "No snapshots found." >&2
    exit 1
  fi
  stat_output_file="/tmp/nfo_mtimes.$UUID.txt"
  stat -c "%y %n" "$@" |sort > "$stat_output_file"
  y_col_width="$(stat -c "%y" "$1" |wc -c)"
  cut -c"$((y_col_width+1))"- "$stat_output_file" |xargs awk '
    NR==FNR {
      # in e.g.  2026-07-29 10:36:22.135998514 +0000 /snapshots/snapshot-name/.snapshot.nfo
      # out e.g. mtimes["/snapshots/snapshot-name/.snapshot.nfo"]="2026-07-29 10:36:22"
      filedate = gensub(/(^[0-9 :-]+).*/, "\\1", "1")
      filepath = substr($0, length($1$2$3)+4)
      mtimes[filepath] = filedate
      next
    }
    FNR==1 {
      # Reset state when reading the next file.
      running = 0
    }
    /^:running:t/ { running = 1; next }
    {
      print "2026-07-29 10:36:22    test-name (running)    This is a comment."  # TODO
    }
  ' "$stat_output_file"
  exit 0
fi

# Fail if snapshot already exists.
if [ -e "$SNAPSHOT_PATH" ]; then
  echo "Snapshot '$SNAPSHOT_NAME' already exists." >&2
  echo "Run 'snapshot-take -l' to list existing snapshots." >&2
  exit 1
fi

# Check if snapshots parent directories exist.
if [ ! -d "$SNAPSHOTS_DIR_FULL" ] && [ ${PARENTS_CREATE:-false} = false ]; then
  echo "Snapshots directory '$SNAPSHOTS_DIR_FULL' does not exist." >&2
  echo "See 'snapshot-take -h'." >&2
  exit 1
  # TODO confirm conditional works
fi

METADATA_FILE_FULL="${SUBVOLUME_DIR%/}/$METADATA_FILE"

# Check if metadata file already exists.
if [ -s "$METADATA_FILE_FULL" ]; then
  echo "Stale file '$METADATA_FILE_FULL' found." >&2
  echo "File must be removed before trying again." >&2
  exit 1
fi

METADATA_FILE_TEMP="/tmp/$METADATA_FILE.$UUID"
IS_READONLY=

# Create snapshot metadata file in a temporary location.
if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
  IS_READONLY=true
  (umask 022; echo ":running:false" > "$METADATA_FILE_TEMP")
else
  (umask 022; echo ":running:true" > "$METADATA_FILE_TEMP")
fi
echo ":comment:$COMMENT" >> "$METADATA_FILE_TEMP"
if [ "${COMMENT:-}" = "-" ]; then
  if [ -t 0 ]; then
    echo "Press Ctrl+D to finish" >&2
  fi
  cat >> "$METADATA_FILE_TEMP"
fi
echo ":comment-end:" >> "$METADATA_FILE_TEMP"

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
  # TODO atexit ro? Or move remount,ro to function then: || { unmount; exit 1; }
fi

# Create snapshots parent directories if requested.
if [ ! -d "$SNAPSHOTS_DIR_FULL" ] && [ ${PARENTS_CREATE:-false} = true ]; then
  if ! mkdir -p "$SNAPSHOTS_DIR_FULL"; then
    echo "Failed to create directory '$SNAPSHOTS_DIR_FULL'." >&2
    echo "Are you running this as root or with sudo?" >&2
    exit 1
  fi
fi

# Move metadata file into subvolume before snapshot.
if ! mv "$METADATA_FILE_TEMP" "$METADATA_FILE_FULL"; then
  echo "Failed to create file '$METADATA_FILE_FULL'." >&2
  echo "Are you running this as root or with sudo?" >&2
  exit 1
fi

# Create snapshot
btrfs subvolume snapshot -r "$SUBVOLUME_DIR" "$SNAPSHOT_PATH"

# Remove snapshot metadata file.
rm -f "$METADATA_FILE_FULL"

# Remount subvolume as readonly if it was originally in that state.
if [ ${IS_READONLY:-false} = true ]; then
  mount -oremount,ro "$SUBVOLUME_DIR"
  echo "Remounted '$SUBVOLUME_DIR' as read-only"
fi

# TODO:
# - @root and @home: can snapshots live in other subvols? Probably not.
# - After take is done, unify? btrfs-snapshot [take|restore]
#   - Support non-root (arbitrary) subvolumes
# - if VERBOSE==true use verbose options in all commands, may need VERBOSE_NOT=false
# - Test -l with no /snapshots
#   - Name collisions won't happen with snapshots outside of that dir. How to display them? Maybe -l and -L?
# - Test with subvol_dir=.
# - Name collisions?
# - Test with spaces in snapshot names (taking and listing).
# - Checks:
#   - if snapshots-dir has a leading / is it the same as subvolume?
#     - subv=/my/sub/vol/ume; snapshots-dir=/snap/shots == /my/sub/vol/ume/snap/shots
# - Integration tests for take+restore interaction (tests/integration_tests/test_snapshot_take_restore.py)
# - Ensure most runs output less than 80chars per line.
