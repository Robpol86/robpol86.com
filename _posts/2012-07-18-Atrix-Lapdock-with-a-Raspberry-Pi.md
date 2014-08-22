---
category: lapdock
layout: post
modified: 2012-07-19
title: Atrix Lapdock with a Raspberry Pi
---

The Lapdock works great with the Raspberry Pi, but with a few caveats:

* Every time the Lapdock's lid is opened or closed, power is cut off the RPI for a second, causing it to reboot.
* There is no "off" mode. When the lid is closed, power is cut off for a second, but then returned, so the RPI will
  power back on.

By itself, the Lapdock is incompatible with the Raspberry Pi's USB hub+Ethernet chip (Model B only) when you introduce
a WiFi adapter (basically, there is a problem when you mix the Raspberry Pi, the Atrix Lapdock, and a WiFi adapter). I
found a workaround by disabling the Ethernet device in software. You can test it by running this command as root:

{% highlight bash %}
echo 1-1.1:1.0 > /sys/bus/usb/drivers/smsc95xx/unbind
{% endhighlight %}

Then re-insert the WiFi adapter and it should start working. I wrote a script to handle this problem easily. Here are
some pointers:

* To enable the script during boot, run: **sudo insserv disable-ethernet**
* To disable the script from running during boot: **sudo insserv -r disable-ethernet**
* To disable Ethernet and fix WiFi, run: **sudo service disable-ethernet start**
* To re-enable Ethernet (be sure to remove the WiFi device before running), run: **sudo service disable-ethernet stop**

Here is the script. Save it in **/etc/init.d/disable-ethernet** and then run **sudo chmod 755
/etc/init.d/disable-ethernet**:

{% gist 5894185 %}

* Adapters used:
    * [HDMI Male to Micro HDMI Female](http://www.dealextreme.com/p/hdmi-male-to-micro-hdmi-female-adapter-66079)
      (delivery took one month)
    * [Micro USB B Male to Female](http://www.ebay.com/itm/ws/eBayISAPI.dll?ViewItem&item=270928425953)
      (delivery took one month)

<div class="thumbnail">
    <div class="row">
        <div class="col-xs-12 col-sm-6 col-lg-4">
            <a href="http://imgur.com/cZR03" target="_blank">
                <img src="http://i.imgur.com/cZR03l.jpg" class="img-responsive img-thumbnail">
            </a>
        </div>
        <div class="col-xs-12 col-sm-6 col-lg-4">
            <a href="http://imgur.com/MrTBN" target="_blank">
                <img src="http://i.imgur.com/MrTBNl.jpg" class="img-responsive img-thumbnail">
            </a>
        </div>
        <div class="col-xs-12 col-sm-6 col-lg-4">
            <a href="http://imgur.com/vCYfG" target="_blank">
                <img src="http://i.imgur.com/vCYfGl.jpg" class="img-responsive img-thumbnail">
            </a>
        </div>
    </div>
    <div class="caption">
        The Raspberry Pi only supports power from its micro USB port, and the regular USB ports on the RPI won't allow
        enough power through. So I had to splice another USB cable into the micro USB extension and route the USB data
        cables (green and white) to the spliced cable.
    </div>
</div>
