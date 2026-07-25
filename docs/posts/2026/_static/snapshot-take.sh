#!/bin/sh -e

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
#               Default: ${SNAPSHOTS_DIR}
#   -h          Display this help and exit.
#   -l          List existing snapshots and exit. SNAPSHOT_NAME argument will be
#               ignored.
#   -p          Create snapshots directories as required. If this option is not
#               specified, the full path prefix of the snapshots directory must
#               already exist.
#   -s dir      Mounted subvolume directory.
#               Default: ${SUBVOLUME_DIR}
#   -v          Enable verbose/debug output.

SNAPSHOTS_DIR=snapshots
SUBVOLUME_DIR=/sysroot
VERBOSE=false

# TODO if -h: print and exit. Avoid getopts while loop?

# TODO if -v: set -x and enable debug() output

# TODO badargs error on unknown args

# TODO check btrfs, SNAPSHOTS_DIR, and SUBVOLUME_DIR

# TODO if -l: print and exit

# TODO badargs error on argv != 1

echo "Hello World Take"
echo "SNAPSHOTS_DIR=$SNAPSHOTS_DIR"
echo "SUBVOLUME_DIR=$SUBVOLUME_DIR"
echo "VERBOSE=$VERBOSE"

# TODO:
# - Manual (from .md):
#       mount -oremount,rw /sysroot
#       btrfs subvolume snapshot -r /sysroot /sysroot/snapshots/root-p
# - Include in rd.break:
#   - envsubst
#   - date
# - @root and @home: can snapshots live in other subvols? Probably not.
#   - Support non-root (arbitrary) subvolumes
# - Support rd.break and running environment with sudo/su.
# - Metadata: maybe let users specify a comment like in VMware? Save it in a file before snapshotting?
#   - Also store date
#   - Allow EOF for multi-line comment. Maybe stdin?
#   - Store wether snapshot was taken from initramfs or from running system
# - Name collisions?
# - Allow module-setup to override defaults (/sysoot/ and ./snapshots/)
#   - How can user specify overrides in dracut?
# - Checks:
#   - sudo or write access to btrfs paths?
#   - is subvolume path btrfs?
#   - is subvolume path a btrfs subvolume?
#   - if snapshots-dir has a leading / is it the same as subvolume?
#   - does snapshots-dir exist sans -p?
# - cli examples:
#       snapshot-take [-h|--help]
#       snapshot-take [-l|--list-only]
#       snapshot-take [-v|--verbose][-p|--create-parents] name
#       snapshot-take [-s|--subvolume=/sysroot] [-d|--snapshots-dir=snapshots] name
#       snapshot-take -c|--comment="comment" name
#       snapshot-take -c- name < comment.txt
