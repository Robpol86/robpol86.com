#!/bin/sh -e

# Copy resize2fs, fdisk, and other kernel modules into initramfs image.
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/resize2fs.sh
# Save as (chmod +x): /etc/initramfs-tools/hooks/resize2fs

COMPATIBILITY=true  # Set to false to skip copying other kernel's modules.

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
  case "${version}" in
    *-v7+) other_version="$(echo ${version} |sed 's/-v7+$/+/')" ;;
    *+) other_version="$(echo ${version} |sed 's/+$/-v7+/')" ;;
    *)
      echo "Warning: kernel version doesn't end with +, ignoring."
      exit 0
  esac
  cp -r /lib/modules/${other_version} ${DESTDIR}/lib/modules/
fi
