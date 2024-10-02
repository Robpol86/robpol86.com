---
blogpost: true
date: 2022-01-02
author: Robpol86
location: San Francisco
category: Projects
tags: car, alltrack
---

# MIB2 Developer Mode

My Alltrack came with an MIB2 Composition Media infotainment system. These are the steps I took to enable development mode
and get some information about it. Enabling development mode also lets me take screenshots by holding down the **Media**
button for 3 seconds and have them saved to the SD card. You'll need an [OBD11/OBDeleven](https://obdeleven.com/en/) or VCDS.

1. 5F Multimedia
2. Change service
   1. Set to **Development mode**
3. Adaptation
4. Developer mode
   1. Set to **Activated**
5. Write
6. Reboot head unit by holding down the power button/knob for 10 seconds.
   1. It will first go to sleep mode (with the clock), then the display will turn off and it will automatically boot back up.

```{imgur-figure} gwoUm7V
:width: 100%
```

```{seealso}
https://www.youtube.com/watch?v=R9WlrkBioi8
```

In the FEC/SWaP menu I have the following features enabled and disabled:

Installed Codes
: * `00070100` (VoiceControl / SDS)
  * `00050000` (Bluetooth)
  * `00030000` (AMI / USB)
  * `00060100` (Vehicle Data Interface)
  * `00060300` (MirrorLink)
  * `00060800` (Apple CarPlay)
  * `00060900` (Google AndroidAuto)

Disabled Codes
: * `00040100` (Navigation)
  * `00060200` (AudiConnect / VW CarNet)
  * `00060500` (Porsche SportChrono)
  * `00070400` (Electronic Voice Amplifier / ICC)

```{seealso}
* https://www.youtube.com/watch?v=p5LA7dU4_WI
* https://mst2fecgen.mibsolution.one/
```
