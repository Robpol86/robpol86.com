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

TODO

### Fresh Install

TODO

```
sudo su -

sfdisk /dev/mmcblk0 <<EOF
label: gpt
,1G,U
,2G,L
,2G,S
,,L
EOF

mkfs.btrfs --label=ubuntu /dev/mmcblk0p4
mount /dev/mmcblk0p4 /mnt
btrfs subvolume create /mnt/@
btrfs subvolume set-default /mnt/@
umount /mnt
```

### Migrate

TODO

## Taking Snapshots

1. Reboot and enter grub
1. Select **Ubuntu** and press `e`
1. Append `rd.break` to the `linux` boot line and press `Ctrl-X`
1. To create a snapshot

```bash
mkdir /mnt
mount /dev/mmcblk0p4 /mnt
btrfs subvolume snapshot -r /mnt /mnt/snapshots/root-pristine2
umount /mnt
reboot
```

## Restoring Snapshots

```bash
mkdir /mnt
mount /dev/mmcblk0p4 /mnt
btrfs subvolume snapshot /mnt/snapshots/root-pristine2 /mnt/@
umount /mnt
reboot
```

## TODO next:

1. echo one > ~/log.log;; take another snapshot;; cat ~/log.log (confirm one)
1. echo two > ~/log.log;; restore snapshot;; cat ~/log.log (confirm one)
1. Create scripts, insert into rd as per rob86.com/rpi-luks instructions
1. Maybe put this on my website instead.
    1. If I do this I'll need to add a migration step (into root subvolume)
