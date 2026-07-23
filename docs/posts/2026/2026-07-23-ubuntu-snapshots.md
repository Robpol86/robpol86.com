---
blogpost: true
date: 2026-07-23
author: Robpol86
location: Helsinki
category: Tutorials
tags: linux
---

# Ubuntu Root Snapshots

TODO like a virtual machine.

## Prerequisits

```{tip}
TODO vim grub

From: https://medium.com/@leijerry888/get-grub-menu-back-after-installing-ubuntu-20-04-alongside-windows-dab5de5afc37
```

TODO

ubuntu-26.04-live-server-amd64.iso

Your Ubuntu must be installed on a btrfs fileystem.

If `sudo btrfs subvolume list /` is empty you must migrate to a subvolume.

In `rd.break`:

```bash
mkdir /mnt
mount /dev/mmcblk0p4 /mnt
btrfs subvolume snapshot /mnt /mnt/@
btrfs subvolume set-default /mnt/@
umount /mnt
reboot
```

To clean the top-level filesystem do this (no need for rd.break):

```bash
sudo mount -o subvolid=5 /dev/mmcblk0p4 /mnt
sudo rm -rf /mnt/[a-z]*
sudo umount /mnt
```

## Taking Snapshots

1. Reboot and enter grub
1. Select **Ubuntu** and press `e`
1. Append `rd.break` to the `linux` boot line and press `Ctrl-X`
1. To create a snapshot

```bash
mkdir /mnt
mount /dev/mmcblk0p4 /mnt
btrfs subvolume snapshot -r /mnt /mnt/s/root-p
umount /mnt
reboot
```

## Restoring Snapshots

```bash
mkdir /mnt
mount -o subvolid=5 /dev/mmcblk0p4 /mnt
mv /mnt/@ /mnt/@_old
btrfs subvolume snapshot /mnt/@_old/s/root-p /mnt/@
btrfs subvolume set-default /mnt/@
umount /mnt
reboot
```

## Script

```bash
snapshot-take name
snapshot-restore name
```

## TODO

- Test with non-custom partitions, but then replace xfs with btrfs
- TODO better name for @_old? Or maybe keep name for easy walkthrough, and use a dated name for scripts.
- Create scripts, insert into rd as per rob86.com/rpi-luks instructions
- Automate mmcblk0p4. Test on install that uses mmcblk0p3 (no swap), maybe also sda (USB)
- Test with @home and @root fs setup?
- Test with Ubuntu Server (non-minimized)
- Test with Ubuntu Desktop
- Test without zfs
- Test cleanup with large file and compare `df` or `btrfs df` before/after `rm -rf`
- Test with a lot of snapshots, revert, make more snapshots, revert. How does this complex tree look?
- Test with LUKS
