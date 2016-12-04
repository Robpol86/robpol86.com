.. _raspberry_pi_project_fi:

==========================
Raspberry Pi on Project Fi
==========================

This guide will go over how to get a Raspberry Pi (or really any Linux system) on Google's
`Project Fi <https://fi.google.com>`_ cellular service. If you already use Project Fi as your main cellphone service
provider then you can use their `data only SIM cards <https://support.google.com/fi?p=data_only_SIM>`_ to get your
Raspberry Pi online for relatively cheap depending on your use case. I was able to power the 3G modem directly from the
USB port on my Pi Zero. You'll probably need a good USB power supply to power everything.

.. imgur-image:: PmqSPyj
    :width: 49%
.. imgur-image:: dE4GgBg
    :width: 49%

You will need:

1. Raspberry Pi running Raspbian (I used a Pi Zero version 1.3).
2. Project Fi data only SIM card (I've previously activated mine on a Nexus 5).
3. T-Mobile locked or unlocked USB 3G modem (I used a Jet 2.0 HSPA+ USB stick).

.. note::

    The Jet 2.0 is basically a **Huawei UMG366**, similar to the **Huawei E366** modem.

Installing on Linux
===================

The first step is getting the OS to recognize the modem. There is a problem with some 3G USB modems in that they
simulate a virtual CD-ROM drive (ZeroCD mode). This drive has drivers and software needed by Windows and OS X to control
the modem. However this trick doesn't work well on Linux. It usually sees the CD-ROM drive and stops probing for more
hardware so the modem isn't available.

You can see this for yourself: plug in the modem into a USB port on the Raspberry Pi and run ``lsusb``. You should see
something like this:

.. code::

    pi@raspberrypi:~ $ lsusb |grep Huawei
    Bus 001 Device 007: ID 12d1:1446 Huawei Technologies Co., Ltd. E1552/E1800/E173 (HSPA modem)

The above is **NOT** what we want. Even though it says "HSPA modem" it is in fact in ZeroCD mode. You won't have wwan0
in ``ifconfig``.

.. tip::

    If you do see ``wwan0`` in ifconfig then you can probably skip the entire USB Mode Switch section below. On Raspbian
    Lite I had to use usb_modeswitch but on Raspbian with PIXEL I didn't need it.

USB Mode Switch
---------------

We'll be using ``usb_modeswitch`` to fix that problem. Luckily it comes pre-installed in Raspbian. If for some reason
you don't have it you can just run ``sudo apt-get install usb-modeswitch``.

First cherry pick the correct file from configPack.tar.gz and put it in /etc/usb_modeswitch.d. Remember that if you had
something other than "12d1:1446" in your ``lsusb`` output you'll want to use that device ID instead in the command
below.

.. code-block:: bash

    cd /etc/usb_modeswitch.d/
    sudo tar -xzvf /usr/share/usb_modeswitch/configPack.tar.gz "12d1:1446"

Now we need to open ``/etc/usb_modeswitch.d/12d1:1446`` in a text editor and put "DefaultVendor=0x12d1" and
"DefaultProduct=0x1446" at the top. It'll end up looking something like this:

.. code::

    DefaultVendor=0x12d1
    DefaultProduct=0x1446
    # Huawei, newer modems, and rebrandings
    TargetVendor=0x12d1
    TargetProductList="1001,1404,1406,140b,140c,1412,1417,141b,1429,1432,1433,1436,14ac,1506,150c,1511"
    HuaweiNewMode=1

Now we can test it:

.. code::

    pi@raspberrypi:~ $ sudo usb_modeswitch -c /etc/usb_modeswitch.d/12d1:1446
    Look for target devices ...
     No devices in target mode or class found
    Look for default devices ...
       product ID matched
     Found devices in default mode (1)
    Access device 014 on bus 001
    Current configuration number is 1
    Use interface number 0
    Use endpoints 0x01 (out) and 0x81 (in)

    USB description data (for identification)
    -------------------------
    Manufacturer: Huawei Technologies
         Product: HUAWEI Mobile
      Serial No.: not provided
    -------------------------
    Using standard Huawei switching message
    Looking for active driver ...
     OK, driver detached
    Set up interface 0
    Use endpoint 0x01 for message sending ...
    Trying to send message 1 to endpoint 0x01 ...
     OK, message successfully sent
    Reset response endpoint 0x81
     Could not reset endpoint (probably harmless): -99
    Reset message endpoint 0x01
     Could not reset endpoint (probably harmless): -99
    -> Run lsusb to note any changes. Bye!

And now we've got wwan0:

.. code::

    pi@raspberrypi:~ $ ifconfig wwan0
    wwan0     Link encap:Ethernet  HWaddr a2:6e:8e:8e:6e:a2
              inet addr:169.254.198.80  Bcast:169.254.255.255  Mask:255.255.0.0
              inet6 addr: fe80::e30f:63c4:d2f4:52c2/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:41 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:0 (0.0 B)  TX bytes:8393 (8.1 KiB)

Reboot your Raspberry Pi to make sure wwan0 is persistent.

Authenticating
==============

While we have wwan0 present we still don't have internet (notice the 169.254.*.* fallback IP address). To get network
service we'll need to setup PPP with the proper APN settings. We'll be using ``wvdial`` for this.

First install it:

.. code-block:: bash

    sudo apt-get install wvdial

Then open ``/etc/wvdial.conf`` and make it look like this (**h2g2** is the Project Fi APN):

.. code-block:: ini

    [Dialer Defaults]
    Init1 = ATZ
    Init2 = ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
    Init3 = AT+CGDCONT=1,"IP","h2g2"
    Modem Type = Analog Modem
    Baud = 460800
    New PPPD = yes
    Modem = /dev/ttyUSB0
    ISDN = 0
    Phone = *99#
    Password = { }
    Username = { }
    Stupid Mode = 1

Now dial into to Project Fi. You should see something like this:

.. note::

    ``vwdial`` will hang at the end if it works. When you ctrl+c it will hang up the modem. This is fine for now. On
    success you will also see a new interface ``ppp0`` whilst ``wwan0`` keeps its current useless IP.

.. code::

    pi@raspberrypi:~ $ sudo wvdial defaults
    --> WvDial: Internet dialer version 1.61
    --> Initializing modem.
    --> Sending: ATZ
    ATZ
    OK
    --> Sending: ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
    ATQ0 V1 E1 S0=0 &C1 &D2 +FCLASS=0
    OK
    --> Sending: AT+CGDCONT=1,"IP","h2g2"
    AT+CGDCONT=1,"IP","h2g2"
    OK
    --> Modem initialized.
    --> Sending: ATDT*99#
    --> Waiting for carrier.
    ATDT*99#
    CONNECT
    --> Carrier detected.  Starting PPP immediately.
    --> Starting pppd at Fri Dec  2 20:43:24 2016
    --> Pid of pppd: 3600
    --> Using interface ppp0
    --> pppd: 8??[01]p??[01]h??[01]
    --> pppd: 8??[01]p??[01]h??[01]
    --> pppd: 8??[01]p??[01]h??[01]
    --> pppd: 8??[01]p??[01]h??[01]
    --> pppd: 8??[01]p??[01]h??[01]
    --> pppd: 8??[01]p??[01]h??[01]
    --> local  IP address 25.9.82.116
    --> pppd: 8??[01]p??[01]h??[01]
    --> remote IP address 10.64.64.64
    --> pppd: 8??[01]p??[01]h??[01]
    --> primary   DNS address 10.177.0.34
    --> pppd: 8??[01]p??[01]h??[01]
    --> secondary DNS address 10.177.0.210
    --> pppd: 8??[01]p??[01]h??[01]

Once it hangs with no errors you can open another terminal (or re-run wvdial in the background) and ping out:

.. code::

    pi@raspberrypi:~ $ ping -I ppp0 4.2.2.1
    PING 4.2.2.1 (4.2.2.1) from 33.250.225.165 ppp0: 56(84) bytes of data.
    64 bytes from 4.2.2.1: icmp_seq=1 ttl=55 time=961 ms
    64 bytes from 4.2.2.1: icmp_seq=2 ttl=55 time=603 ms
    64 bytes from 4.2.2.1: icmp_seq=3 ttl=55 time=341 ms
    64 bytes from 4.2.2.1: icmp_seq=4 ttl=55 time=221 ms
    ^C
    --- 4.2.2.1 ping statistics ---
    4 packets transmitted, 4 received, 0% packet loss, time 3001ms
    rtt min/avg/max/mdev = 221.998/532.237/961.983/283.804 ms
    pi@raspberrypi:~ $

Automatically Connect
---------------------

We've got network service, however every time you want to use it you need to run the ``wvdial`` command in another
terminal. Wouldn't it be nice if it auto-dialed on boot?

Write this to ``/etc/network/interfaces.d/ppp0``:

.. code::

    auto ppp0
    iface ppp0 inet wvdial

Now reboot. When you log back in you should see ppp0 connected and you should be able to ping out. It is pretty slow
though (I get around 15 KiB/s). Good enough for my use case however.

.. imgur-image:: zTRT6Ja
    :width: 49%
.. imgur-image:: 87aSM89
    :width: 49%

References
==========

* https://www.thefanclub.co.za/how-to/how-setup-usb-3g-modem-raspberry-pi-using-usbmodeswitch-and-wvdial
* https://www.instructables.com/id/Raspberry-Pi-as-a-3g-Huawei-E303-wireless-Edima/
* http://www.frank-d.info/cellular-backup-again-via-googles-project-fi-a-cisco-3825-and-an-hwic-3g-gsm
* http://knilluz.buurnet.nl/?p=1327

Comments
========

.. disqus::
