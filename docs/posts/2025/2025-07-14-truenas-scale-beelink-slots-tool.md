---
blogpost: true
date: 2025-07-14
author: Robpol86
location: Sydney
category: Tutorials
tags: homelab, nas, beelink
---

# TrueNAS Slots Tool for ME Mini

```{list-table}
* - :::{thumb-image} /_images/pictures/travel-nas/beelink-slots/beelink-slots-column.png
    :::
* - :::{thumb-image} /_images/pictures/travel-nas/beelink-slots/beelink-slots.png
    :::
```

I wrote a script that displays the slot number of each SSD in the TrueNAS web UI, since all the labels face inward. If an SSD
needs to be replaced I'd rather not have to pull each one out to see if the serial matches. The script also shows the PCIe
generation (by way of the link speed) and width (how many PCIe lanes the SSD is using). It also shows if the SSD is operating
below its maximum capability.

```{thumb-figure} /_images/pictures/travel-nas/beelink-slots/beelink-no-lid.jpeg
Some SSDs have the serial numbers facing the heatsink.
```

## Requirements

This script is designed for TrueNAS SCALE running on the [Beelink ME Mini](https://www.bee-link.com/products/beelink-me-mini-n150).
The NAS I have has the Intel N150 CPU, but I've read on Reddit that the newer ones ship with the N200 CPU. If you have one of
those, please let me know in the comments whether the script works for you or not.

## Installing the Script

To install go to the **Init/Shutdown Scripts** section under *System > Advanced Settings* and add a new script. Restart the
NAS afterwards.

1. **Description**: Slots Tool
1. **Type**: Command
1. **When**: Post Init
1. **Command**: *paste the below command*

```bash
set -eu; cd /dev; for device in nvme?n1; do id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$device\").identifier")"; slot="$(awk -F'[. ]' -v PORTS="RP03 RP04 RP07 RP09 RP11 RP12" 'BEGIN{split(PORTS, list); for(item in list) mapping[list[item]] = item} {print mapping[$3] ? mapping[$3] : "?"; exit}' "/sys/block/$device/device/device/firmware_node/path")"; address="$(head -1 "/sys/block/$device/device/address")"; lsta="$(lspci -s "$address" -vv |grep -Po 'LnkSta:\s\K.+')"; midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"; done
```

## Explanation

The script reads the PCIe Root Port number for each NVMe drive. It compares them to a known mapping between these port
numbers and the corresponding slot number on the Beelink ME Mini motherboard.

```{thumb-figure} /_images/pictures/travel-nas/beelink-slots/beelink-bios-rp.png
Chipset > PCH-IO Configuration > PCI Express Configuration
```

Below is the same script as above but broken down with comments.

```bash
# Immediately exit when a command fails.
set -e
# Immediately exit if a referenced variable is not set.
set -u

cd /dev

# Loop through all NVMe devices in /dev such as nvme0n1, nvme1n1, etc.
# For example the variable $device may be set to "nvme0n1".
for device in nvme?n1; do
    # TrueNAS stores each NVMe device in its internal database using a unique ID
    # beyond just a serial number. An example: "{serial_lunid}QC5616R_25012616c"
    # Here we find this unique ID associated with a specific NVMe device and
    # store it in the variable $id.
    # Here I'm also using the `-e` option for the jq command, which "sets the
    # exit status of jq to [...] 1 if the last output value was [...] null".
    # Because we're using `set -e` if $device is not found in the TrueNAS
    # database for any reason, jq will fail and stop this script from running
    # any further.
    id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$device\").identifier")"
    # Here we find the slot number for the particular device. We're using PCIe
    # root ports to map devices to slot numbers. In the BIOS screenshot above we
    # see a list of PCI Express Root Ports available in the system. Some of
    # these are dedicated to NVMe slots on the motherboard. The goal here is to
    # figure out which RP maps to which slot. Lucky for us the RP number is
    # available in the special file "firmware_node/path" available in the "/sys"
    # filesystem. To get the NVMe serial number run: lsblk -o name,serial
    slot="$(awk -F'[. ]' -v PORTS="RP03 RP04 RP07 RP09 RP11 RP12" '
        BEGIN {
            # Order the RP numbers above by slot number so when the string is
            # split into the `list` array it maps to list[1]="RP03",
            # list[2]="RP04", etc. In awk arrays start with 1, not 0.
            split(PORTS, list)
            # Invert the `list` array into a `mapping` associative array.
            # So instead of `list[1]="RP03"` we have `mapping["RP03"]=1`.
            for(item in list) {
                mapping[list[item]] = item
            }
        }
        {
            # The `firmware_node/path` file contains something like this:
            # \_SB_.PC00.RP07.PXSX
            # In the -F awk option we passed "." as a field separator. So $3
            # has the value of RP07. We check if that value is in the `mapping`
            # assoc array and if so print that. If not we print out a question
            # mark.
            print mapping[$3] ? mapping[$3] : "?"
            # The `firmware_node/path` file only has one line. We exit here just
            # in case.
            exit
        }
    ' "/sys/block/$device/device/device/firmware_node/path")"
    # Besides slot numbers I'm also showing the PCIe generation and width. One
    # of the NVMe slots on the ME Mini has two lanes instead of one. We can show
    # this in the TrueNAS UI. The PCIe generation is shown as the link speed.
    address="$(head -1 "/sys/block/$device/device/address")"
    # If you're running this script manually you'll need sudo because of this
    # lspci command.
    lsta="$(lspci -s "$address" -vv |grep -Po 'LnkSta:\s\K.+')"
    # Finally we'll issue an API call to TrueNAS to update the description for
    # the NVMe device with its slot number and PCIe link speed and width.
    midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"
done
```

## Reddit Post

I also posted this script on Reddit:

* https://www.reddit.com/r/BeelinkOfficial/comments/1lldlb8/script_show_me_mini_slot_numbers_in_truenas_scale/
