# MIB2 Composition Media Hacking

My US 2019 Golf Alltrack SE came with the MIB2 Composition Media infotainment system made by Delphi running
[QNX 6.5.0](http://www.qnx.com/developers/docs/6.5.0SP1.update/#./com.qnx.doc.momentics_quickstart/about.html) (with firmware
MST2_US_VW_P0890D release 0890). This unit has CarPlay/Android Auto but lacks navigation or maps of its own (though it has
GPS). Lucky for me, it's possible to gain root access to the unit.

I used these resources to learn about this:

* https://www.youtube.com/watch?v=R9WlrkBioi8&ab_channel=mr-fix
* https://mibsolution.one/#/1/9/MST2%20%20-%20DELPHI/Instruction

## Root Shell

To get root access you'll need to buy two items:

1. [OBD11/OBDeleven](https://obdeleven.com/en/) or [VCDS/VAG-COM](https://www.ross-tech.com/vag-com/)
2. A [USB network adapter](http://wiki.mr-fix.info/index.php?title=MIB2#USB_to_RJ45)
   1. I used an old [ASIX AX88772A chipset based adapter](https://plugable.com/products/usb2-otge100) I had lying around
3. A laptop

To access the root shell follow these steps:

1. Enable development mode
2. Enable ethernet support
3. Reboot
4. Telnet

### Enabling Development Mode

```{danger}

Accessing development features can irreversibly damage your infotainment system for your car, bricking it or physically
damaging its electronics (voltage settings are exposed when in development mode).

Proceed with caution at your own risk. Don't do any of this if you're not familiar with embedded devices or if you're not
familiar with Linux or Unix.
```

Using your OBD11 or VCDS enable development mode (I'll be using OBD11):

1. 5F Multimedia
2. Change service
   1. Set to **Development mode**
3. Adaptation
4. Developer mode
   1. Set to **Activated**
5. Write

```{imgur-figure} dba8LPe
:width: 100%
```

```{tip}
After enabling development mode you can now take screenshots by holding down the {kbd}`Media` button for 3 seconds. They'll
be saved to your SD card.
```

### Enabling Ethernet

Next we need to enable ethernet mode, otherwise the USB network adapter will be ignored by the head unit.

1. Hold down the {kbd}`Menu` button for 10 seconds
   1. The **Testmode Menue** hidden menu will appear
2. Green Engineering Menu
3. debugging mlp
4. Using the tuning knob (not volume knob) select **Ethernet** and press the knob to enable it
5. Reboot
   1. Reboot by holding down the power/volume knob for 10 seconds. First the clock will appear, keep holding, then the screen
      will go black. Let go and wait for it to finish starting back up automatically.
6. Plug in the USB network adapter into the USB port you usually use for music or Android Auto/CarPlay
7. Configure your laptop to use the static IP `192.168.1.10` with subnet mask `255.255.255.0` (no gateway or DNS needed)
8. Connect your laptop to the USB network adapter's ethernet port
9. Ping `192.168.1.4` to confirm the head unit's network is up
   1. You can confirm this is the head unit's IP by going back to the green menu debugging mlp screen

```{imgur-figure} 0kQqbaI
:width: 100%
```

### Telnet or FTP

The last step is to confirm you can telnet and/or FTP into the head unit.

```{imgur-figure} LlmTirV
:width: 100%
```

My unit exposed three services over the network:

* 21/tcp (FTP, user/pass both *ftpuser*)
* 23/tcp (Telnet, user is *root* with no password)
* 513/tcp (Rlogin, haven't used it yet)

[FTP](https://filezilla-project.org/) and [telnet](https://www.putty.org/) both grant you full access to the running OS and
filesystems. Some notes:

* SD card is mounted as read/write on `/sdc1`
* You can keep Ethernet enabled, CarPlay still worked for me
* Files added to `/media` and `/persistence` survive reboots, together there's about 542 MiB of free space available
* Looks like my unit has 1 GiB of RAM installed, with about half of it unused
* Use [pidin](https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/p/pidin.html) instead of
  `ps`
* Use `showmem` instead of `free`

## Dumps

This section is where I put a bunch of random outputs I got during my investigation.

### Filesystem

https://mega.nz/file/a4xTUIKa#do9uQA3p30hKfn-blXom4ff3-8uUah2O61z6IOdvtIY

### `uname -a`

```text
QNX localhost 6.5.0 2015/12/01-11:00:56EST TI-DRA74X-PG1.0 armle
```

### `df -h`

```text
/dev/sdc0t12                 30G       19G       11G      63%  /sdc1/
/dev/fs1p0                   16M      1.0M       14M       8%  /ramdisk
/dev/mmc0t179               400M       39M      361M      10%  /media/
/dev/mmc0t178               2.0G      383M      1.6G      19%  /lng/
/dev/mmc0t180               220M       39M      181M      18%  /persistence/
/dev/mmc0t177               760M      428M      332M      57%  /extbin/
/dev/fs0p3                  384K      4.5K      379K       2%  /home
/dev/fs0p1                  9.5M      5.3M      4.1M      57%  /ffs
/dev/sdc0                    30G       30G         0     100%
/dev/cdd0                      0         0         0     100%
/dev/mmc0                   3.3G      3.3G         0     100%
```

### `mount`

```text
/dev/sdc0t12 on /sdc1 type dos (fat32)
/dev/fs1p0 on /ramdisk type flash
/dev/mmc0t179 on /media type qnx6
/dev/mmc0t178 on /lng type qnx6
/dev/mmc0t180 on /persistence type qnx6
/dev/mmc0t177 on /extbin type qnx6
/dev/fs0p3 on /home type flash
/dev/fs0p1 on /ffs type flash
```

### `showmem -S`

```text
System RAM:      896M (     939524096)
Total Used:      406M (     426565660)
 Used Private:   326M (     342616416)
 Used Shared:     77M (      80973824)
       Other:   2905K (       2975420) (includes IFS and reserved RAM)
```

### `ls -lah /dev`

```{literalinclude} _static/mib2_ls_dev.txt
:language: text
```

### `top -i 1 -d`

https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/t/top.html

```{literalinclude} _static/mib2_top.txt
:language: text
```

### `lsusb`

```{literalinclude} _static/mib2_lsusb.txt
:language: text
```

### `pidin arguments`

```{literalinclude} _static/mib2_pidin_arguments.txt
:language: text
```

### `pidin env`

```{literalinclude} _static/mib2_pidin_env.txt
:language: text
```

## Comments

```{disqus}
```
