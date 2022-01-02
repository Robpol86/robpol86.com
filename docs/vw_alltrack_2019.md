# Golf Alltrack SE

This page is a log book of all the modifications I've done to my 2019 Alltrack.

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

```{imgur-figure} gwoUm7V
:width: 100%
```

```{seealso}
https://www.youtube.com/watch?v=R9WlrkBioi8&ab_channel=mr-fix
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
https://www.youtube.com/watch?v=p5LA7dU4_WI&ab_channel=mr-fix
https://mst2fecgen.mibsolution.one/
```

## Dec &#39;21 Euro Tail Lights

```{imgur-embed} QlhDVvr
```

I've always preferred amber turn signals over flashing brake lights in my vehicles. My 2010 JSW had them but my 2019 Alltrack
lacked the amber turn signals.

I bought my 2019 Golf Alltrack SE with the
[Driver Assistance and Appearance Package](https://media.vw.com/en-us/press-kits/2019-golf-alltrack-press-kit). It came with
North American Region LED tail lights (not sure if this is a standard feature of 2019 models or only for vehicles with the
appearance package) so when I bought the EUR LED kit I had to take this into account when choosing the wiring harness. Even
with this choice I still had to make modifications to the harness before installing, which I'll go over below.

```{seealso}
https://www.vwvortex.com/threads/installing-euro-led-tail-lights-on-my-us-2019-alltrack-se-nar-led-to-euro-led.9491919/
```

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

```{imgur-figure} 6hayUFc
:width: 100%
```

### Euro Switch

```{imgur-figure} jzNrO3j
:width: 100%
```

Since I'll be installing new tail lights with fog lights I had to purchase the Euro light switch. Installation is very easy,
at position **0** push in the switch and turn it towards **Auto** then pull it out.

### Modify Harness

```{list-table}
* - ```{imgur-figure} pZKVVDG
    Outer harness before modification
    ```
  - ```{imgur-figure} JVCZV7i
    Outer harness trimmed
    ```
  - ```{imgur-figure} 5NiYmRk
    Inner harness trimmed
    ```
```

Before getting to my car I had to make some modifications to four wiring harness connectors with an
[X-ACTO knife](https://www.amazon.com/gp/product/B00JWFIKOC). It would have been easier to trim off plastic from the
connectors in my car but I wanted to avoid irreversibly modifying anything in my car if I could help it.

On both outer taillight wiring harnesses I had to trim off a plastic key rail that was in the way. Since I didn't have X-ACTO
blades narrow enough I had to sacrifice the guiding rail right next to the key rail. Thankfully the connector still fit
snugly with no play. For the inner harness connectors I had to remove one key rail but ended up having to sacrifice a second
key rail.

```{tip} Before removing any taillight I suggest checking if all the wiring harnesses connect to the new lights and your
car's connectors.
```

### Outer Taillights

```{list-table}
* - ```{imgur-figure} Bh72jOs
    ```
  - ```{imgur-figure} YgeEq3D
    ```
```

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

```{imgur-figure} idiFM0N
:width: 100%
```

First remove both taillights by removing the plastic access cover and using an **8 mm** hex socket. Each light has two nuts
that need to be removed. Then you can remove the lights by pivoting them away from the center of the tailgate. Install the
new inner taillights in the reverse order and tighten the four nuts.

```{list-table}
* - ```{imgur-figure} H1Vr4p6
    :ext: png
    ```
  - ```{imgur-figure} y3ZL67J
    Hatch with all inner body trim pieces removed. The main piece to remove is the largest one, but I found it easier to
    first pop off the long piece spanning the top (when closed) of the hatch and then popping off the two side pieces.
    ```
```

You have a couple of options when wiring the inner lights. You can take the easy route and follow the included instructions,
which is to blindly snake the wire and harness from one side to the other using the access panels for the inner lights. I
didn't like the idea of a wire being loose back there so I went with the slightly (but not much) harder route and remove the
hatch inner plastic trim to get a complete unobstructed view of where the wire will go.

```{list-table}
* - ```{imgur-figure} H0Q7sZT
    ```
  - ```{imgur-figure} wqQeEvP
    ```
* - ```{imgur-figure} QcbOFMP
    ```
  - ```{imgur-figure} leahnOj
    ```
```

I ended up zip tying the harness wire to the existing wiring in the hatch. I then put back all the body trim pieces.

### Coding

```{imgur-figure} pzLtcvk.gif
:width: 100%
Without coding the wrong lights will be designated as brakes and blinkers.
```

The final step is to apply coding so the right LEDs light up when braking or signaling. The instructions given were for
[VCDS/VAG-COM](https://www.ross-tech.com/vag-com/) but all I have is [OBD11/OBDeleven](https://obdeleven.com/en/). Luckily
the settings are very similar. Set aside **20 to 30 minutes** to do all the coding. You'll need to write changes **before**
tapping "Back" since OBD11 doesn't queue up new settings.

To start you'll need to enter an **access code** to enable writing:

1. 09 Central Electrics
2. Security access
3. Login code: **31347**
4. Tap "Enter", it should say "Verifying login code" then "Success"

```{imgur-figure} k1UTy0N
:width: 100%
```

The next step I believe is to enable the rear fog lights to work with the Euro switch I mentioned above.

1. 09 Central Electrics
2. Adaptation
3. Aussenlicht uebergreifend (search for "ueb")
4. LDS mit Nebel Schlusslicht
   1. Set to **Yes**
5. Write

```{imgur-figure} RSlu0wb
:width: 100%
```

Finally it's time for the main event; grab some coffee for this. Go through each setting and either make the change or verify
the settings match the values below:

Leuchte18
: * Dimming Direction CD: **Minimize**
  * Dimming Direction EF: **Maximize**
  * Dimming Direction GH: **Minimize**
  * Dimmwert AB: **0**
  * Dimmwert CD: **0**
  * Dimmwert EF: **127**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **16**
  * Lampendefektbitposition: **8**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A-H: **Nicht aktiv**

Leuchte19
: * Dimming Direction CD: **Minimize**
  * Dimming Direction EF: **Maximize**
  * Dimming Direction GH: **Minimize**
  * Dimmwert AB: **0**
  * Dimmwert CD: **0**
  * Dimmwert EF: **127**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **18**
  * Lampendefektbitposition: **18**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A-H: **Nicht aktiv**

Leuchte20
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **127**
  * Dimmwert EF: **0**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **3D**
  * Lampendefektbitposition: **13**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Brake light**
  * Lichtfunktion B-H: **Nicht aktiv**

Leuchte21
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **127**
  * Dimmwert EF: **0**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **3E**
  * Lampendefektbitposition: **23**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Brake light**
  * Lichtfunktion B-H: **Nicht aktiv**

Leuchte23
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **0**
  * Dimmwert GH: **10**
  * Byte DTC-DFCC: **29**
  * Lampendefektbitposition: **A**
  * Lasttyp: **38 - LED Blinkleuchten**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Blinken links Hellphase**
  * Lichtfunktion B-E: **Nicht aktiv**
  * Lichtfunktion F: **Parklicht links (beidseitiges Parklicht aktiviert li & re)**
  * Lichtfunktion G: **Nicht aktiv**
  * Lichtfunktion H: **Parklicht links (beidseitiges Parklicht aktiviert li & re)**

Leuchte24
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **0**
  * Dimmwert GH: **10**
  * Byte DTC-DFCC: **2A**
  * Lampendefektbitposition: **1A**
  * Lasttyp: **38 - LED Blinkleuchten**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Blinken rechts Hellphase**
  * Lichtfunktion B-E: **Nicht aktiv**
  * Lichtfunktion F: **Parklicht rechts**
  * Lichtfunktion G: **Nicht aktiv**
  * Lichtfunktion H: **Parklicht rechts**

Leuchte25
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **127**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **30**
  * Lampendefektbitposition: **28**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Standlicht allgemein (Schlusslicht, Positionslicht, Begrenzungslicht)**
  * Lichtfunktion B-H: **Nicht aktiv**

Leuchte26
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **0**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **54**
  * Lampendefektbitposition: **0**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Standlicht allgemein (Schlusslicht, Positionslicht, Begrenzungslicht)**
  * Lichtfunktion B-H: **Nicht aktiv**

Leuchte27
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **0**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **53**
  * Lampendefektbitposition: **0**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Standlicht allgemein (Schlusslicht, Positionslicht, Begrenzungslicht)**
  * Lichtfunktion B-H: **Nicht aktiv**

Leuchte28
: * Dimming Direction CD-GH: **Maximize**
  * Dimmwert AB: **127**
  * Dimmwert CD: **0**
  * Dimmwert EF: **0**
  * Dimmwert GH: **0**
  * Byte DTC-DFCC: **31**
  * Lampendefektbitposition: **B**
  * Lasttyp: **43 - allgemeine LED**
  * Lichtansteuerung HD AB: **Always**
  * Lichtfunktion A: **Nebelschlusslicht wenn kein Anhaenger gesteckt**
  * Lichtfunktion B-H: **Nicht aktiv**

## Oct &#39;21 EcoHitch Install

I decided to go with the [EcoHitch x7315](https://torkliftcentral.com/2015-2017-volkswagen-golf-sportwagen-alltrack-tsi-ecohitch).
Installing was straight forward, but it ended up taking my entire Sunday to complete. Overall I'm very happy with how it
turned out.

I ended up getting my own bolts instead of using the bolts that came with the hitch based on what
[jjvincent](https://www.vwvortex.com/threads/hitch-vs-warranty.8489450/#post-103482505) said, but this is optional. If you
want to do the same I bought them from [McMaster-Carr](https://www.mcmaster.com/91029A107/) (from:
https://www.mcmaster.com/bolts/fastener-strength-grade-class~class-12-9/extreme-strength-metric-class-12-9-steel-hex-head-screws/thread-size~m8/).

```{seealso}
https://www.vwvortex.com/threads/installing-2-ecohitch-on-my-us-2019-alltrack-se.9487399
```

I used the following tools:

* [Precision Instruments PREC2FR100F Torque Wrench](https://www.amazon.com/gp/product/B000YOX568)
* 13mm and 10mm sockets
* 1 ft socket extension
* Ratchet
* T25 and T15 Torx drivers
* Crescent wrench (adjustable spanner)
* [Plastic trim removal tools](https://www.amazon.com/gp/product/B005NMCE04) and a flat screwdriver
* [X-ACTO knife](https://www.amazon.com/gp/product/B00JWFIKOC)

```{imgur-embed} a/uD7nNgv
:og_imgur_id: 0Yt6Rpz
```

## Sept &#39;21 Rear Dashcam Pair

```{imgur-figure} 3ypCZaP
:width: 100%
```

Installed a second pair of cameras to get a better view out of the rear of my car for read-end crashes as well as another IR
camera pointed towards the front of the car. This way I have a sort of 360 view from both inside-pointing cameras. Like the
front camera I also bought a tamper-proof case for the rear one. Similarly I also use BlackVue batteries to keep the camera
powered overnight.

### Items Purchased

BlackVue DR750-2CH IR LTE Dashcam
: * $450
  * 1080p main camera
  * 1080p infrared second camera
  * LTE, WiFi, GPS, microSD slot
  * LTE seems to only use about 6 MiB a day on average

Blackvue B-124X Power Magic Ultra Battery Pack
: * $330
  * Installed in the cargo area

BlackVue B-124E Power Magic Ultra Battery Expansion
: * $269

### Photos

```{imgur-embed} a/Sq4ENiu
```

## Sept &#39;21 OBDeleven

These modifications are done with an [OBDeleven](https://obdeleven.com) device.

### Refuel Quantity

Adds a screen in my MFD where the car estimates how much fuel it would take to fill the tank. Handy for when I have to
prepay with cash at gas stations.

* Apps > Refuel quantity in dashboard > ON
* https://forum.obdeleven.com/thread/536/refuel-quantity-dashboard

```{imgur-figure} cJgOPtJ
:alt: Refuel quantity in dashboard
:width: 100%
```

### Automatic DST

Instead of having to toggle DST manually the car does it automatically.

* Vehicle > 5F Multimedia > Long Coding > Summertime-automatic > USA
* https://www.golfmk7.com/forums/index.php?threads/automatic-summer-time.341637

```{imgur-figure} 6UlKtvf
:alt: Automatic daylight saving time switchover
:width: 100%
```

## Aug &#39;21 Drag Race

Taken off of Shoreline Hwy in Stinson Beach CA.

```{imgur-figure} kh7I65B
:alt: Alltrack Photo 2021-08-23
:width: 100%
```

Also took it to the drag strip.

```{youtube} 8T0vEKU7lGg
:width: 100%
```

&nbsp;

```{youtube} imPz7bAErr8
:width: 100%
:url_parameters: ?start=18538
```

## Aug &#39;21 P3 Vent Gauge

Installed this to have a boost gauge in my air vent:
[P3 V3 OBD2 - VW Mk7 / Mk7.5 Gauge (2014-2020)](https://www.p3cars.com/volkswagen/p3-v3-obd2-vw-mk7-mk7-5-gauge-2014-2019/)

I didn't bother hooking up the dimmer wire since you can dim it manually by holding the right button. I mounted the
controller box using zip ties (it's on tight and doesn't move at all) and I heatshrinked the unused wires to avoid any
potential shorts.

```{imgur-figure} qAFrhWS
:alt: Vent Gauge
:width: 100%
```

```{imgur-figure} KXQqsg6
:alt: Controller Mount
:width: 100%
```

## June &#39;21 Fire Extinguisher

Bought a rechargeable 2.5 lb fire extinguisher from Amazon:
[Amerex Dry Chemical Fire Extinguisher B417T](https://www.amazon.com/gp/product/B001VXRYCM)

I then zip tied it to my car placing some velcro around the fire extinguisher, so it's easy to pull out during an emergency.
It stays put after driving for weeks and doesn't get in the way of lifting the cover to access my spare tire.

```{imgur-figure} 705hYoS
:alt: Fire Extinguisher
:width: 100%
```

### Oct &#39;21 Update

Every now and then the fire extinguisher would move a bit, getting in the way of the bottom cover/floor. I fixed this by
using some zip ties to hold the extinguisher in place. I made sure it's still easy to remove during an emergency, just slide
off the zip tie with my thumb.

```{imgur-figure} CJUFaP7
:alt: Fire Extinguisher Update
:width: 100%
```

## Feb &#39;20 Front Dashcam Pair

```{imgur-figure} 9dVe8pY
:width: 100%
```

I installed a BlackVue dashcam along with multiple batteries to get about 2 days of recording time while my vehicle is
parked. I live in San Francisco and while my car is parked overnight in a garage, I occasionally park my car in the street
and after a year nobody has broken in to steal the camera.

As a precaution I bought the tamper-proof case so a thief can't just pull out the wires and take the camera. Additionally I
zip tied the wires tightly to the internal metal part of my rearview mirror (and threaded it through a narrow hole for more
strength). Hopefully this means anyone that wants to steal the camera will need to bring a knife or scissors along, and I'm
hoping those are the minority of opportunistic thieves in the city.

```{note}
I suggest covering up unused ports on the BlackVue battery with electrical tape. When I was unplugging and plugging in wires
I accidentally plugged the input power cable in the expansion port of the main battery, sending 12v from the battery back to
my car. Luckily nothing broke but I kept getting ABS errors until I figured out my mistake.
```

### Items Purchased

BlackVue DR900S-2CH Dashcam
: * $490
  * Installed behind rearview mirror
  * 4K main camera
  * 1080p infrared second camera
  * WiFi, GPS, microSD slot

Blackvue B-124X Power Magic Ultra Battery Pack
: * $330
  * Installed in the cargo area
  * Comes with 3 meter long cables which just barely reached with no slack left

BlackVue B-124E Power Magic Ultra Battery Expansion
: * $267

### Front Camera Pair

I first installed just the two cameras in the front and wired them to the batteries in my cargo area. For now I didn't wire
the batteries to my fuse panel, using the rear 12v outlet instead.

```{imgur-embed} a/Z3HBWOX
```

### Hardwire Batteries

Once I was happy with the cameras I finished the project by hardwiring the batteries to my fuse box. I used the included fuse
taps and I used **15 amp** fuses. In the photos below you'll see two pairs of wires from my fusebox. I ran a second wire from
a second tapped fuse since I may add a second pair of cameras in the future. I tapped
[fuse 48 and 36](https://fuse-box.info/volkswagen/volkswagen-golf-vii-mk7-2013-2020-fuses). These are switched fuses so when
the ignition is off they'll lose power and prevent the BlackVue battery from draining my car's battery when parked.

```{imgur-embed} a/HHRnuuV
```

## Feb &#39;20 Under-Seat Drawer

Just like my old TDI I wanted the OEM drawer under the driver seat to store things. Unlike my old TDI there is no passenger
seat drawer available for the Alltrack. While installing, I also lined the drawer and the dash cubby that came with the car
with felt so things wouldn't rattle.

I bought the drawer for $156 on ECS Tuning:
[Driver's Seat Tray Kit Titanium Black 5GM 882 599 KT](https://www.ecstuning.com/b-genuine-volkswagen-audi-parts/drivers-seat-tray-kit-titanium-black/5gm882599kt/)

```{imgur-figure} W7T6lmB
:width: 100%
```

```{imgur-embed} a/7PauDgm
```

## Jan &#39;20 Trashcan

Bought this from Amazon:
[display4top Auto Car Trash Can Bin Waste Container](https://www.amazon.com/gp/product/B07TCT96SH)

Sadly it's no longer available.

```{imgur-figure} BwicdEg
:alt: Trashcan
:width: 100%
```

## Comments

```{disqus}
```
