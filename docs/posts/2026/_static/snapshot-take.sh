#!/bin/sh -e

# TODO.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/snapshot-take.sh
# Save as (chmod +x): /sbin/snapshot-take

echo "Hello World Take"

# TODO:
# - Manual (from .md):
#       mount -oremount,rw /sysroot
#       btrfs subvolume snapshot -r /sysroot /sysroot/snapshots/root-p
# - @root and @home: can snapshots live in other subvols? Probably not.
# - Metadata: maybe let users specify a comment like in VMware? Save it in a file before snapshotting?
#   - Also store date
#   - Allow EOF for multi-line comment. Maybe stdin?
#   - Store wether snapshot was taken from initramfs or from running system
# - Name collisions?
# - Allow module-setup to override defaults (/sysoot/ and ./snapshots/)
#   - How can user specify overrides in dracut?
# - Checks:
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
