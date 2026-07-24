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

If you don't know which one you have:

::::{tab-set}
:::{tab-item} With LVM
:sync: with-lvm
```shell
$ sudo lvm vgs
  VG        #PV #LV #SN Attr   VSize   VFree
  ubuntu-vg   1   1   0 wz--n- <55.19g    0
$ sudo lvm lvs
  LV        VG        Attr       LSize   Pool Origin Data%  Meta%  Move Log
  ubuntu-lv ubuntu-vg -wi-ao---- <55.19g
$ sudo btrfs filesystem show
Label: none  uuid: fb5a711e-1f82-42fe-8ce8-1349acc7448d
	Total devices 1 FS bytes used 7.06GiB
	devid    1 size 55.19GiB used 11.02GiB path /dev/mapper/ubuntu--vg-ubuntu--lv
```
:::
:::{tab-item} No LVM
:sync: no-lvm
```shell
echo TODO
```
:::
::::

### Migrate Root to a Subvolume

Your Ubuntu must be installed on a BTRFS fileystem.

If `sudo btrfs subvolume list /` is empty you must migrate to a subvolume.

In `rd.break`:

::::{tab-set}
:::{tab-item} rd.break
```bash
mount -oremount,rw /sysroot
btrfs subvolume snapshot /sysroot /sysroot/@
btrfs subvolume set-default /sysroot/@
reboot
```
:::
::::

Now you should see:

```shell
$ sudo btrfs subvolume list /
ID 256 gen 71 top level 5 path @
```

To clean the top-level filesystem do this (no need for rd.break):

```bash
sudo mount -o subvolid=5 "$(findmnt -nvo SOURCE --target /)" /mnt
sudo rm -rf /mnt/[a-z]*
sudo umount /mnt
```

## Taking Snapshots

1. Reboot and enter grub
1. Select **Ubuntu** and press `e`
1. Append `rd.break` to the `linux` boot line and press `Ctrl-X`
1. To create a snapshot

::::{tab-set}
:::{tab-item} With LVM
:sync: with-lvm
```bash
echo TODO
```
:::
:::{tab-item} No LVM
:sync: no-lvm
```bash
mkdir /mnt
mount /dev/mmcblk0p4 /mnt
btrfs subvolume snapshot -r /mnt /mnt/s/root-p
umount /mnt
reboot
```
:::
::::

## Restoring Snapshots

::::{tab-set}
:::{tab-item} With LVM
:sync: with-lvm
```bash
echo TODO
```
:::
:::{tab-item} No LVM
:sync: no-lvm
```bash
mkdir /mnt
mount -o subvolid=5 /dev/mmcblk0p4 /mnt
mv /mnt/@ /mnt/@_old
btrfs subvolume snapshot /mnt/@_old/s/root-p /mnt/@
btrfs subvolume set-default /mnt/@
umount /mnt
reboot
```
:::
::::

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
  - Copy large file to system before migration
  - Migrate but don't clean
  - `df`; delete large file from mounted fs; `df` should remain the same
  - Clean; `df` should now shrink
- Test with a lot of snapshots, revert, make more snapshots, revert. How does this complex tree look?
- Test with LUKS
- Test with fresh install, no apt-get from gist
