---
blogpost: true
date: 2025-07-12
author: Robpol86
location: Sydney
category: Tutorials
tags: homelab, beelink
---

# TrueNAS Slots Tool for Me Mini

TODO TrueNAS screenshots

I wrote a script to show which slot number each SSD is in in the TrueNAS web UI since all the labels face inward. If an SSD
needs to be replaced I'd rather not have to pull each one out to see if the serial matches.

```{imgur-figure} AWIy6pV
Some SSDs have the serial numbers facing the heatsink.
```

## Requirements

This script is designed for TrueNAS SCALE running on the [Beelink Me Mini](https://www.bee-link.com/products/beelink-me-mini-n150).
The NAS I have has the Intel N150 CPU, but I've read on Reddit that the newer ones ship with the N200 CPU. If you have one of
those, please let me know in the comments whether the script works for you or not.

## Installing the Script

To install go to the **Init/Shutdown Scripts** section under *System > Advanced Settings* and add a new script:

1. **Description**: Slots Tool
1. **Type**: Command
1. **When**: Post Init
1. **Command**: *paste the below command*

```bash
set -e; cd /dev; for d in nvme?n1; do id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$d\").identifier")"; slot="$(awk -F'[. ]' 'BEGIN{split("RP03 RP04 RP07 RP09 RP11 RP12", list); for(item in list) mapping[list[item]] = item} {print mapping[$3] ? mapping[$3] : "?"; exit}' /sys/block/$d/device/device/firmware_node/path)"; lsta="$(lspci -s "$(cat "/sys/block/$d/device/address")" -vv |grep -Po 'LnkSta:\s\K.+')"; midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"; done
```

## Explanation

TODO BIOS screenshot

```bash
set -e

cd /dev

for d in nvme?n1; do
    id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$d\").identifier")"
    slot="$(awk -F'[. ]' '
        BEGIN {
            split("RP03 RP04 RP07 RP09 RP11 RP12", list)
            for(item in list) {
                mapping[list[item]] = item
            }
        }
        {
            print mapping[$3] ? mapping[$3] : "?"
            exit
        }
    ' /sys/block/$d/device/device/firmware_node/path)"
    address="$(cat "/sys/block/$d/device/address")"
    lsta="$(lspci -s "$address" -vv |grep -Po 'LnkSta:\s\K.+')"
    midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"
done
```
