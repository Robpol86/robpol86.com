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

Get the OpenLock challenge key from the hotspot
:   * Run the command: `AT!OPENLOCK?`
    * Copy the code it responded with (e.g. `ABA5463E8FBDA36B`)

Generate the unlock code using the script
:   * Download [sierrakeygen.py](../../_static/sierrakeygen.py)
    * Run the script: `python3 sierrakeygen.py -d MDM9x50_V1 -l PUT_CODE_HERE`
    * Copy the AT command it printed (e.g. `AT!OPENLOCK="058052AB497C8E84"`)

Enable root access
:   * WARNING: Root will be accessible **without a password** over USB, Ethernet, and WiFi!
    * Run the AT command the script printed in the telnet session (it should reply with "OK")
    * Run the command: `AT!TELEN=1;!CUSTOM="RDENABLE",1;!CUSTOM="TELNETENABLE",1`
    * Reboot the hotspot and wait until you regain access to the web UI
    * Access root by telnetting to port **23** (e.g. `telnet 192.168.1.1 23`)

## Static DHCP

TODO

## Disable WiFi When Home

TODO

## Interesting Info

TODO

## Comments

```{disqus}
```
