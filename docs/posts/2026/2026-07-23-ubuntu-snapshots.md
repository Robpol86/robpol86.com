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

Works with btrfs bare metal, LVM, and LVM with LUKS.

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
sudo mount -osubvolid=5 "$(findmnt -nvo SOURCE /)" /mnt
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
mount -osubvolid=5 /dev/FINDMNT_PATH /sysroot  # Replace FINDMNT_PATH
mv /sysroot/@ /sysroot/@_old
btrfs subvolume snapshot /sysroot/@_old/s/root-p /sysroot/@
btrfs subvolume set-default /sysroot/@
reboot
```
:::
::::

## Scripts

Install scripts:

```{literalinclude} _static/snapshot-take.sh
:language: bash
```

```{literalinclude} _static/snapshot-restore.sh
:language: bash
```

```{literalinclude} _static/snapshot-module-setup.sh
:language: bash
```

Then run:

```bash
sudo update-initramfs -u
sudo lsinitramfs /boot/initrd.img |grep snap
```

::::{tab-set}
:::{tab-item} rd.break
```bash
snapshot-take name
snapshot-restore name
```
:::
::::

## TODO

- Create scripts, insert into rd as per rob86.com/rpi-luks instructions
  - snapshot-take should work from initfs and normal environment with sudo
- Install ubuntu without btrfs and run `sudo btrfs subvolume list -t /`
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
