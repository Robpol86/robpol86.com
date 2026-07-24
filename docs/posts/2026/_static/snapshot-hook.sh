#!/bin/sh -e

# Copy snapshot-take and snapshot-restore into initramfs image.
# https://github.com/Robpol86/robpol86.com/blob/main/docs/posts/2026/_static/snapshot-hook.sh
# Save as (chmod +x): /etc/initramfs-tools/hooks/snapshot-hook

PREREQ=""
prereqs () {
  echo "${PREREQ}"
}
case "${1}" in
  prereqs)
    prereqs
    exit 0
  ;;
esac

. /usr/share/initramfs-tools/hook-functions

copy_exec /sbin/snapshot-take /sbin
copy_exec /sbin/snapshot-restore /sbin
