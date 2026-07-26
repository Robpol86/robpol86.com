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

SNAPSHOTS_DIR=snapshots
LIST_ONLY=
PARENTS_CREATE=
SUBVOLUME_DIR=/
VERBOSE=
SNAPSHOT_NAME=

# Parse command line arguments.
while getopts :c:d:hlps:v OPT; do
  case "$OPT" in
    \?) echo "unknown flag: '$OPTARG'" >&2
        exit 1 ;;
    :) echo "flag needs an argument: '$OPTARG'" >&2
       exit 1 ;;
    c) echo "comment arg: $OPTARG" ;;  # TODO
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

# List only.
if [ ${LIST_ONLY:-false} = true ]; then
  echo NotImplementedError >&2  # TODO
  exit 1
fi

SNAPSHOTS_DIR_FULL="${SUBVOLUME_DIR%/}/${SNAPSHOTS_DIR%/}"
SNAPSHOT_PATH="$SNAPSHOTS_DIR_FULL/$SNAPSHOT_NAME"

# Fail if snapshot already exists.
if [ -e "$SNAPSHOT_PATH" ]; then
  echo "Snapshot '$SNAPSHOT_NAME' already exists." >&2
  echo "Run 'snapshot-take -l' to list existing snapshots." >&2
  exit 1
fi

# Create parent directories if requested.
if [ ! -d "$SNAPSHOTS_DIR_FULL" ]; then
  if [ ${PARENTS_CREATE:-false} = true ]; then
    mkdir -p "$SNAPSHOTS_DIR_FULL"
  else
    echo "Snapshots directory '$SNAPSHOTS_DIR_FULL' does not exist." >&2
    echo "See 'snapshot-take -h'." >&2
    exit 1
  fi
fi

# Remount subvolume as readwrite if it is mounted as readonly.
IS_READONLY=
if findmnt -O ro "$SUBVOLUME_DIR" > /dev/null; then
  IS_READONLY=true
  mount -oremount,rw "$SUBVOLUME_DIR"
fi

# TODO btrfs snapshot

# Remount subvolume as readonly if it was originally in that state.
if [ ${IS_READONLY:-false} = true ]; then
  mount -oremount,ro "$SUBVOLUME_DIR"
fi

# TODO:
# - Manual (from .md):
#       mount -oremount,rw /sysroot
#       btrfs subvolume snapshot -r /sysroot /sysroot/snapshots/root-p
# - @root and @home: can snapshots live in other subvols? Probably not.
#   - Support non-root (arbitrary) subvolumes
# - if VERBOSE==true use verbose options in all commands, may need VERBOSE_NOT=false
# - Support rd.break and running environment with sudo/su.
# - Test with subvol_dir=.
# - Metadata: maybe let users specify a comment like in VMware? Save it in a file before snapshotting?
#   - Also store date
#   - Allow EOF for multi-line comment. Maybe stdin?
#   - Store wether snapshot was taken from initramfs or from running system
# - Name collisions?
# - Checks:
#   - sudo or write access to btrfs paths?
#   - is subvolume path btrfs?
#   - is subvolume path a btrfs subvolume?
#   - if snapshots-dir has a leading / is it the same as subvolume?
#     - subv=/my/sub/vol/ume; snapshots-dir=/snap/shots == /my/sub/vol/ume/snap/shots
#   - does snapshots-dir exist sans -p?
# - cli examples:
#       snapshot-take [-h|--help]
#       snapshot-take [-l|--list-only]
#       snapshot-take [-v|--verbose][-p|--create-parents] name
#       snapshot-take [-s|--subvolume=/sysroot] [-d|--snapshots-dir=snapshots] name
#       snapshot-take -c|--comment="comment" name
#       snapshot-take -c- name < comment.txt
