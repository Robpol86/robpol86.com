#!/bin/sh
set -e
COMPATIBILITY=true
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
# Raspberry Pi 1 and 2+3 use different kernels. Include the other.
if ${COMPATIBILITY}; then
    other=$(ls /lib/modules |grep -v $(uname -r))
    cp -r /lib/modules/${other} ${DESTDIR}/lib/modules/
fi
