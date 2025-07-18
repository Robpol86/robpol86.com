---
blogpost: true
date: 2025-07-18
author: Robpol86
location: Sydney
category: Tutorials
tags: homelab, glinet
---

# GL.iNet USB Network Adapter

TODO

- Slate 7 GL-BE3600
- Beryl AX GL-MT3000

## Notes

Plug in USB adapter, it should show up as eth2.

luci/admin/network/network devices eth2 Configure

Add eth2 to /etc/board.json

luci/admin/network/network interfaces add > "lan2" "static" "eth2" "192.168.9.1/24"
