---
title: Golf Alltrack SE
date: 2021-08-27T16:56:04-07:00
tags:
  - alltrack
  - vehicle
disqus_identifier: Golf Alltrack SE
---

This page is a log book of all the modifications I've done to my 2019 Alltrack.

## Dec &#39;22 Clutch Bleeder Block Mod

I posted the installation steps in a dedicated post here:

* TODO

## Oct &#39;22 Jack Pads

This modification makes it easier to put my car on jack stands in my garage. It adds a second set of jacking points to the
car so I don't have to jack up the car from the opposite side when rotating my tires. It was really easy to install too. In
fact I installed this kit without needing to jack up the car at all and removing the old trim pieces was really effortless.

Items used:

* [Audi Jack Kit for MK7 Models](https://www.shopdap.com/catalog/product/view/id/721670)
* Pick tool to pull out old covers and push in tabs, you can probably also use a flathead screwdriver.

Instructions:

TODO

Pictures:

TODO

## Aug &#39;22 OEMTools 24938 Gauge Mod

Another dedicated post loosely related to my Alltrack:

* [](posts/2022/2022-08-23-oemtools-gauge.md)

## Jun &#39;22 HomeLink Rearview Mirror

I posted the installation steps in a dedicated post here:

* [](posts/2022/2022-06-05-alltrack-homelink-mirror.md)

## Jan &#39;22 MIB2 Developer Mode

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

TODO

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

TODO

## Dec &#39;21 Euro Tail Lights

TODO

I've always preferred amber turn signals over flashing brake lights in my vehicles. My 2010 JSW had them but my 2019 Alltrack
lacked the amber turn signals.

I bought my 2019 Golf Alltrack SE with the
[Driver Assistance and Appearance Package](https://media.vw.com/en-us/press-kits/2019-golf-alltrack-press-kit). It came with
North American Region LED tail lights (not sure if this is a standard feature of 2019 models or only for vehicles with the
appearance package) so when I bought the EUR LED kit I had to take this into account when choosing the wiring harness. Even
with this choice I still had to make modifications to the harness before installing, which I'll go over below.

TODO

Items purchased:

* [Mk7 European Light Switch 5GG941431D](https://www.thebeardeddetailer.com/swag-store/mk7-european-light-switch)
  * [Chinese switch](https://www.golfmk7.com/forums/index.php?threads/oem-vw-euro-headlight-switch.365237/) (works fine)
  * Auto Lights: **Yes**
  * Front Fogs: **Yes**
  * Rear Fog: **Yes**
* [OEM Euro LED Tail Lamps 5G9945095G 5G9945093L 5G9945094K 5G9945096G](https://www.thebeardeddetailer.com/swag-store/sportwagen-alltrack-led-tails)
  * Do you need an adapter harness?: **Tail lamps and adapter harness**
  * Rear Fog: **2**
  * Style: **2018+ NAR LED to Euro LED, tinted**

TODO

### Euro Switch

TODO

Since I'll be installing new tail lights with fog lights I had to purchase the Euro light switch. Installation is very easy,
at position **0** push in the switch and turn it towards **Auto** then pull it out.

### Modify Harness

TODO

Before getting to my car I had to make some modifications to four wiring harness connectors with an
[X-ACTO knife](https://www.amazon.com/gp/product/B00JWFIKOC). It would have been easier to trim off plastic from the
connectors in my car but I wanted to avoid irreversibly modifying anything in my car if I could help it.

On both outer taillight wiring harnesses I had to trim off a plastic key rail that was in the way. Since I didn't have X-ACTO
blades narrow enough I had to sacrifice the guiding rail right next to the key rail. Thankfully the connector still fit
snugly with no play. For the inner harness connectors I had to remove one key rail but ended up having to sacrifice a second
key rail.

TODO

### Outer Taillights

TODO

This is the easy part. Installing the outer lights is as easy as:

1. Access the taillight connectors by removing the felt covers in the cargo area.
2. Unplug the existing connectors.
3. Remove the plastic screw with your hands by twisting them off.
4. Pull out the old taillights and install the new lights.
5. Connect them using the modified outer wiring harnesses.

My passenger side taillight fit fine and flush but the driver side seemed to stick out a bit. I fixed this by turning the
plastic adjustment screw with a **T15** bit and [ratchet](https://www.amazon.com/dp/B000XYOUS6).

### Inner Taillights

Since I bought taillights with two fog lights (one for each side) the included inner wiring harness came with two wires
connecting the two. This means the two inner lights will connect to each other with these two wires that must be routed
behind the inner plastic body trim. *If you didn't get fog lights and only received the outer lights with the amber turn
signals then you can skip this section.*

TODO

First remove both taillights by removing the plastic access cover and using an **8 mm** hex socket. Each light has two nuts
that need to be removed. Then you can remove the lights by pivoting them away from the center of the tailgate. Install the
new inner taillights in the reverse order and tighten the four nuts.

TODO

You have a couple of options when wiring the inner lights. You can take the easy route and follow the included instructions,
which is to blindly snake the wire and harness from one side to the other using the access panels for the inner lights. I
didn't like the idea of a wire being loose back there so I went with the slightly (but not much) harder route and remove the
hatch inner plastic trim to get a complete unobstructed view of where the wire will go.

TODO
