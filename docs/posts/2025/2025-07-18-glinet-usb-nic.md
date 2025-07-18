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

```
root@GL-BE3600:/usr/lib/lua# uci set board_special.hardware.lan2='eth2'
root@GL-BE3600:/usr/lib/lua# uci commit board_special
root@GL-BE3600:/usr/lib/lua# cat /etc/config/board_special

config service 'hardware'
	option wan 'eth0'
	option lan2 'eth2'

config switch 'switch'

config network 'network'
	option wan 'eth0'
	option lan 'eth1'
```

## Originals

### /etc/config/board_special

```
config service 'hardware'
	option wan 'eth0'

config switch 'switch'

config network 'network'
	option wan 'eth0'
	option lan 'eth1'
```

### `uci show board_special`

```
board_special.hardware=service
board_special.hardware.wan='eth0'
board_special.switch=switch
board_special.network=network
board_special.network.wan='eth0'
board_special.network.lan='eth1'
```
