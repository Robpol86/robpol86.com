# Netgear Nighthawk M1 Hacking

```{tags} hacking, hotspot
```

I'm replacing my old [T-Mobile Franklin T9](../../franklin_t9) with a more capable hotspot. The
[Netgear Nighthawk M1](https://www.netgear.com/home/mobile-wifi/hotspots/mr1100/) is easy to root, supports USB and microSD
cards for storage (with a caveat that this is disabled when USB tethering is enabled), has a lot more RAM (relatively
speaking), and works fine with [Google Fi](https://fi.google.com/about). At the time of writing I had my M1 on the latest
firmware, which is `NTG9X50C_12.06.39.00` (since my SKU is for AT&T but is unlocked and also works with T-Mobile bands).

## Telnet and Root

The first step is to get root access. Luckily it's pretty easy to do using a Python script written by
[bkerler](https://github.com/bkerler).

Get access to the hotspot's modem console
:   * From the web UI go to: Settings > Setup > Mobile Router Setup
    * Under "Tethering" select: **Charge + tether**
    * Connect your computer to the hotspot only using a USB cable (disconnect from WiFi/Ethernet)
    * Telnet to the hotspot using port **5510** (e.g. `telnet 192.168.1.1 5510`)
    * Run the command `AT` (it should reply with "OK")

## Static DHCP

TODO

## Disable WiFi When Home

TODO

## Interesting Info

TODO

## Comments

```{disqus}
```
