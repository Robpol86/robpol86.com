---
blogpost: true
date: 2025-07-12
author: Robpol86
location: Sydney
category: Tutorials
tags: homelab, beelink
---

# TrueNAS Slots Tool for Me Mini

TODO

```{imgur-image} ILLt9Ur
```

➡️ System > Advanced Settings > Init/Shutdown Scripts

```bash
# Description: Slots Tool

# Command:
set -e; cd /dev; for d in nvme?n1; do id="$(midclt call disk.query |jq -er ".[]|select(.name==\"$d\").identifier")"; slot="$(awk -F'[. ]' 'BEGIN{split("RP03 RP04 RP07 RP09 RP11 RP12", list); for(item in list) mapping[list[item]] = item} {print mapping[$3] ? mapping[$3] : "?"; exit}' /sys/block/$d/device/device/firmware_node/path)"; lsta="$(lspci -s "$(cat "/sys/block/$d/device/address")" -vv |grep -Po 'LnkSta:\s\K.+')"; midclt call disk.update "$id" "{\"description\": \"Slot $slot, $lsta\"}"; done

# When: Post Init
```

TODO screenshots and photos
