#!/bin/sh
set -e
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
copy_exec /sbin/resize2fs /sbin
copy_exec /sbin/fdisk /sbin
