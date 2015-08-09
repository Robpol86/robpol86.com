.. _atrix_lapdock:

========================
Atrix Lapdock Other Uses
========================

I bought the Atrix Lapdock since I couldn't find any sub $100 portable HDMI displays. The only affordable displays I
could find were USB only. With the Atrix Lapdock and some adapters, I was able to use it as a portable display for
several devices, which is great for traveling.

It's a good idea to remove the plate on the docking area (underneath where the phone would be). It makes it easier to
plug in the adapters or have to sand/shave them less. You can easily pull it off with your finger nails (the plate
actually has a couple of magnets to keep it in place, and two small plastic clips).

.. image:: https://i.imgur.com/WpsmIm.jpg
    :target: https://imgur.com/WpsmI
    :width: 49%
.. image:: https://i.imgur.com/5HAGwm.jpg
    :target: https://imgur.com/5HAGw
    :width: 49%

Pictures and Videos
===================

.. imgur-embed:: a/zEkwz

.. raw:: html

    <iframe width="560" height="315" src="http://www.youtube.com/embed/VfdKq33WgHw?rel=0" frameborder="0"></iframe>

.. raw:: html

    <iframe width="560" height="315" src="http://www.youtube.com/embed/zCxTTrTZSSM?rel=0" frameborder="0"></iframe>

.. raw:: html

    <iframe width="560" height="315" src="http://www.youtube.com/embed/x_yhJ_QBfaU?rel=0" frameborder="0"></iframe>

.. raw:: html

    <iframe width="560" height="315" src="http://www.youtube.com/embed/P1zKD66GSYo?rel=0" frameborder="0"></iframe>

With a Nexus 4
==============

Works with the Nexus 4 just fine, appears to maintain aspect ratio. Adapters used:

* `HDMI Male to Micro HDMI Female <https://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079>`_
* `Micro USB B Male to Female <https://www.ebay.com/itm/ws/eBayISAPI.dll?ViewItem&item=270928425953>`_
* `SlimPort SP1002 (HDMI) <https://www.amazon.com/dp/B009UZBLSG/>`_
* `HDMI Port Saver (Male to Female) 90 Degree <https://www.monoprice.com/products/product.asp?p_id=3733>`_

.. image:: https://i.imgur.com/MJs3n49m.jpg
    :target: https://imgur.com/MJs3n49
    :width: 49%
.. image:: https://i.imgur.com/MUViVQIm.jpg
    :target: https://imgur.com/MUViVQI
    :width: 49%

Using USB OTG
-------------

Using a modified kernel with OTG_USER_CONTROL set, I was able to get the Lapdock's keyboard, mouse, and USB hub working
with my Nexus 4! While I wait for my Miracast adapter to arrive, I had to put something on the Lapdock's HDMI port to
make it turn on, so I used a Raspberry Pi for now. Here are a few observations:

* I'm using an unmodified 5-wire Micro USB B Male to Female.
* The phone **does not charge** even though the lapdock is sending power and data to the phone. Perhaps the kernel
  needs additional modification?
* In the second and third pictures I removed the small WiFi USB adapter that was plugged into the Lapdock to show that
  the phone detected it, confirming the USB hub works.
* Once I get my `PTV3000 <https://www.amazon.com/Netgear-PTV3000-100NAS-Push2TV/dp/B00904JILO>`_ I can try using the
  Lapdock's full potential with my phone.
* No multitouch mouse/touchpad :(

Steps taken to accomplish:

1. `Download <https://forum.xda-developers.com/showpost.php?p=38621573&postcount=121>`_ the modified kernel at the
   bottom of that post.
2. `Boot the new kernel <https://forum.xda-developers.com/showthread.php?t=2151159>`_ following the instructions in the
   original post.
3. Plug and play!

.. note::

    Ignore the Raspberry Pi in the images below, I'm just using it to trick the Lapdock into powering on. Notice the
    mouse cursor on my phone!

    If you can see, I ran ``lsusb`` on the phone, removed the USB WiFi adapter, and ran ``lsusb`` again. Notice the
    shorter "paragraph" on my phone. Definitely working.

.. image:: https://i.imgur.com/qbs7sWgb.jpg
    :target: https://imgur.com/qbs7sWg
    :width: 33%
.. image:: https://i.imgur.com/yNgacICb.jpg
    :target: https://imgur.com/yNgacIC
    :width: 33%
.. image:: https://i.imgur.com/K7glCXNb.jpg
    :target: https://imgur.com/K7glCXN
    :width: 33%

Using USB OTG and Miracast
--------------------------

It works, but it's not really pleasant. If we can get Keyboard/Mouse to Bluetooth working that would be much better.

With a Raspberry Pi
===================

The Lapdock works great with the Raspberry Pi, but with a few caveats:

* Every time the Lapdock's lid is opened or closed, power is cut off the RPI for a second, causing it to reboot.
* There is no "off" mode. When the lid is closed, power is cut off for a second, but then returned, so the RPI will
  power back on.

Adapters used:

* `HDMI Male to Micro HDMI Female <https://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079>`_
* `Micro USB B Male to Female <https://www.ebay.com/itm/ws/eBayISAPI.dll?ViewItem&item=270928425953>`_

.. note::

    The Raspberry Pi only supports power from its micro USB port, and the regular USB ports on the RPI won't allow
    enough power through. So I had to splice another USB cable into the micro USB extension and route the USB data
    cables (green and white) to the spliced cable.

.. image:: https://i.imgur.com/cZR03m.jpg
    :target: https://imgur.com/cZR03
    :width: 33%
.. image:: https://i.imgur.com/MrTBNm.jpg
    :target: https://imgur.com/MrTBN
    :width: 33%
.. image:: https://i.imgur.com/vCYfGm.jpg
    :target: https://imgur.com/vCYfG
    :width: 33%

With a Laptop
=============

I can use the Atrix Lapdock as a secondary display for my laptop. At home my laptop is docked to two monitors, so every
time I traveled I had to deal with a single monitor. Not anymore! Adapters used:

* `HDMI Male to Micro HDMI Female <https://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079>`_
* HDMI Female/Female Coupler

.. image:: https://i.imgur.com/ldQ0cl.jpg
    :target: https://imgur.com/ldQ0c
    :width: 49%
.. image:: https://i.imgur.com/KONZZl.jpg
    :target: https://imgur.com/KONZZ
    :width: 49%

With a Wii
==========

I don't have a 360 or PS3, but I have a Wii and after I found an HDMI adapter I tried it with the Lapdock. Turns out it
works just fine. The Lapdock takes care of changing resolution as long as it's at or below 1366x768. Audio works too by
the way. This should work just fine with the Xbox 360, PS3, or any other HDMI devices. Adapters used:

* `HDMI Male to Micro HDMI Female <https://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079>`_
* HDMI Female/Female Coupler
* `Wii HDMI Adapter <https://www.amazon.com/gp/product/B0057UNPQO/>`_

.. image:: https://i.imgur.com/TXiVxm.jpg
    :target: https://imgur.com/TXiVx
    :width: 33%
.. image:: https://i.imgur.com/UkdYJm.jpg
    :target: https://imgur.com/UkdYJ
    :width: 33%
.. image:: https://i.imgur.com/cc5TKm.jpg
    :target: https://imgur.com/cc5TK
    :width: 33%

Lapdock 500 Teardown
====================

.. imgur-embed:: a/UDZs7

Comments
========

.. disqus::
