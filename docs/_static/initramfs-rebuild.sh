#!/bin/sh -e

# Rebuild initramfs.gz after kernel upgrade to include new kernel's modules.
# https://github.com/Robpol86/robpol86.com/blob/master/docs/_static/initramfs-rebuild.sh
# Save as (chmod +x): /etc/kernel/postinst.d/initramfs-rebuild

# Remove splash from cmdline
if grep -q '\bsplash\b' /boot/cmdline.txt; then
    sed -i 's/ \?splash \?/ /' /boot/cmdline.txt
fi

# Rebuild only if needed.
version="$1"
[ -x /usr/sbin/mkinitramfs ] || exit 0
[ -f /boot/initramfs.gz ] || exit 0
lsinitramfs /boot/initramfs.gz |grep -q "/$version$" && exit 0
mkinitramfs -o /boot/initramfs.gz "$version"
