---
category: lapdock
layout: post
modified: 2013-03-02
title: Atrix Lapdock with a Nexus 4
---

Works with the Nexus 4 just fine, appears to maintain aspect ratio. <del>As with the Galaxy Nexus, no
keyboard/mouse/USB. Just power to charge the phone and HDMI from the phone.</del>

* Adapters used:
    * [HDMI Male to Micro HDMI Female](http://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079)
      (delivery took one month)
    * [Micro USB B Male to Female](http://www.ebay.com/itm/ws/eBayISAPI.dll?ViewItem&item=270928425953)
      (delivery took one month)
    * [SlimPort SP1002 (HDMI)](http://www.amazon.com/dp/B009UZBLSG/)
    * [HDMI Port Saver (Male to Female) 90 Degree](http://www.monoprice.com/products/product.asp?p_id=3733)

<div class="row">
    <div class="col-xs-12 col-sm-6">
        <a href="http://imgur.com/MJs3n49" target="_blank">
            <img src="http://i.imgur.com/MJs3n49l.jpg" class="img-responsive thumbnail">
        </a>
    </div>
    <div class="col-xs-12 col-sm-6">
        <a href="http://imgur.com/MUViVQI" target="_blank">
            <img src="http://i.imgur.com/MUViVQIl.jpg" class="img-responsive thumbnail">
        </a>
    </div>
</div>

# Using USB OTG

Using a modified kernel with OTG_USER_CONTROL set, I was able to get the Lapdock's keyboard, mouse, and USB hub working
with my Nexus 4! While I wait for my Miracast adapter to arrive, I had to put something on the Lapdock's HDMI port to
make it turn on, so I used a Raspberry Pi for now. Here are a few observations:

* I'm using an unmodified 5-wire Micro USB B Male to Female.
* The phone **does not charge** even though the lapdock is sending power and data to the phone. Perhaps the kernel
  needs additional modification?
* In the second and third pictures I removed the small WiFi USB adapter that was plugged into the Lapdock to show that
  the phone detected it, confirming the USB hub works.
* Once I get my [PTV3000](http://www.amazon.com/Netgear-PTV3000-100NAS-Push2TV/dp/B00904JILO) I can try using the
  Lapdock's full potential with my phone.
* No multitouch mouse/touchpad :(

Steps taken to accomplish:

1. [Download](http://forum.xda-developers.com/showpost.php?p=38621573&postcount=121) the modified kernel at the bottom
   of that post.
2. [Boot the new kernel](http://forum.xda-developers.com/showthread.php?t=2151159) following the instructions in the
   original post.
3. Plug and play!

<div class="thumbnail">
    <div class="row">
        <div class="col-xs-12 col-sm-6">
            <a href="http://imgur.com/qbs7sWg" target="_blank">
                <img src="http://i.imgur.com/qbs7sWgl.jpg" class="img-responsive img-thumbnail">
            </a>
        </div>
        <div class="col-xs-12 col-sm-6">
            <a href="http://imgur.com/yNgacIC" target="_blank">
                <img src="http://i.imgur.com/yNgacICl.jpg" class="img-responsive img-thumbnail">
            </a>
        </div>
    </div>
    <div class="caption">
        Ignore the Raspberry Pi, I'm just using it to trick the Lapdock into powering on. Notice the mouse cursor on my
        phone!<br/>
        If you can see, I ran lsusb on the phone, removed the USB WiFi adapter, and ran lsusb again. Notice the shorter
        "paragraph" on my phone. Definitely working.
    </div>
</div>

<div class="row">
    <div class="col-xs-12">
        <div class="thumbnail">
            <a href="http://imgur.com/K7glCXN" target="_blank">
                <img src="http://i.imgur.com/K7glCXNh.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">
                First group is with the USB WiFi adapter, second group is after I removed it. The phone can detect
                things on the USB hub.
            </div>
        </div>
    </div>
</div>

# Using USB OTG and Miracast

It works, but it's not really pleasant. If we can get Keyboard/Mouse to Bluetooth working that would be much better.

<div class="well well-sm">
    <div class="embed-responsive embed-responsive-16by9">
        <iframe class="embed-responsive-item" src="http://www.youtube.com/embed/P1zKD66GSYo"></iframe>
    </div>
</div>
