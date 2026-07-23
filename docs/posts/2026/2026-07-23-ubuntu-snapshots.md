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
btrfs subvolume snapshot -r /mnt "/mnt/snapshots/root-whatever"
umount /mnt
reboot
```

## Restoring Snapshots

TODO

## TODO next:

1. echo one > ~/log.log;; take another snapshot;; cat ~/log.log (confirm one)
1. echo two > ~/log.log;; restore snapshot;; cat ~/log.log (confirm one)
1. Create scripts, insert into rd as per rob86.com/rpi-luks instructions
1. Maybe put this on my website instead.
    1. If I do this I'll need to add a migration step (into root subvolume)
