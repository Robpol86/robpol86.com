---
blogpost: true
date: 2025-07-12
author: Robpol86
location: Sydney
category: Tutorials
tags: homelab, beelink
---

# TrueNAS Slots Tool for Me Mini

```{list-table}
* - :::{imgur-image} XObiRqa
    :::
* - :::{imgur-image} KjFxyXB
    :::
```

I wrote a script to show which slot number each SSD is in in the TrueNAS web UI since all the labels face inward. If an SSD
needs to be replaced I'd rather not have to pull each one out to see if the serial matches.

```{imgur-figure} OSU97Ou
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
# Immediately exit when a command fails
set -e

cd /dev

# Loop through all NVMe devices in /dev such as nvme0n1, nvme1n1, etc.
for d in nvme?n1; do
    # TrueNAS stores each NVMe device in its internal database using a unique ID
    # beyond just a serial number. An example: "{serial_lunid}QC5616R_25012616c"
    # Here we find this unique ID associated with a specific NVMe device and
    # store it in the variable `id`.
    id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$d\").identifier")"
    # TODO
    slot="$(awk -F'[. ]' '
        BEGIN {
            # TODO
            split("RP03 RP04 RP07 RP09 RP11 RP12", list)
            # TODO
            for(item in list) {
                mapping[list[item]] = item
            }
        }
        {
            # TODO
            print mapping[$3] ? mapping[$3] : "?"
            # TODO
            exit
        }
    ' /sys/block/$d/device/device/firmware_node/path)"
    # TODO
    address="$(cat "/sys/block/$d/device/address")"
    # TODO sudo
    lsta="$(lspci -s "$address" -vv |grep -Po 'LnkSta:\s\K.+')"
    # Finally we'll issue an API call to TrueNAS to update the description for
    # the NVMe device with its slot number and PCIe link speed and width.
    midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"
done
```

## Reddit Post

I also posted this script on Reddit:

* https://www.reddit.com/r/BeelinkOfficial/comments/1lldlb8/script_show_me_mini_slot_numbers_in_truenas_scale/
