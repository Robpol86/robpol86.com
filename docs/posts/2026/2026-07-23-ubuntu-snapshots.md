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

:::{tip}
If you're having trouble getting into the GRUB menu on boot you can set the timeout to be 3 seconds, giving you the
opportunity to enter the ramdisk environment on boot.

Run these commands:

```bash
sudo sed -i.bak \
  -e '/GRUB_TIMEOUT/s/=[0-9]\+/=3/' \
  -e '/GRUB_TIMEOUT_STYLE/s/=[a-z]\+/=menu/' /etc/default/grub
sudo update-grub
```
:::

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

```shell
$ sudo btrfs subvolume list -t /
ID	gen	top level	path
--	---	---------	----
```

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
$ sudo btrfs subvolume list -t /
ID	gen	top level	path
--	---	---------	----
256	41	5		@
```

To clean the top-level filesystem do this (no need for rd.break):

```bash
sudo mount -o subvolid=5 "$(findmnt -nvo SOURCE /)" /mnt
sudo rm -rf /mnt/[a-z]*
sudo umount /mnt
```

## Taking Snapshots

1. `sudo mkdir /s`
1. Reboot and enter grub
1. Select **Ubuntu** and press `e`
1. Append `rd.break` to the `linux` boot line and press `Ctrl-X`
1. To create a snapshot

::::{tab-set}
:::{tab-item} rd.break
```bash
mount -oremount,rw /sysroot
btrfs subvolume snapshot -r /sysroot /sysroot/s/root-p
reboot
```
:::
::::

## Restoring Snapshots

::::{tab-set}
:::{tab-item} rd.break
```bash
findmnt -nvo SOURCE /sysroot
umount /sysroot
mount -o subvolid=5 /dev/FINDMNT_PATH /sysroot  # Replace FINDMNT_PATH
mv /sysroot/@ /sysroot/@_old
btrfs subvolume snapshot /sysroot/@_old/s/root-p /sysroot/@
btrfs subvolume set-default /sysroot/@
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

- Test with LUKS
- Create scripts, insert into rd as per rob86.com/rpi-luks instructions
- Test with @home and @root fs setup?
  - Find a popular guide on Ubuntu and btrfs
- Test with Ubuntu Server (non-minimized)
- Test with Ubuntu Desktop
- Test cleanup with large file and compare `df` or `btrfs df` before/after `rm -rf`
  - Copy large file to system before migration
  - Migrate but don't clean
  - `df`; delete large file from mounted fs; `df` should remain the same
  - Clean; `df` should now shrink
- Test with a lot of snapshots, revert, make more snapshots, revert. How does this complex tree look?
- Test with fresh install, no apt-get from gist, no zfs
- Install ubuntu without btrfs and run `sudo btrfs subvolume list -t /`
