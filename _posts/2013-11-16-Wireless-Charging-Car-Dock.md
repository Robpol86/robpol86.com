---
layout: post
title: Wireless Charging Car Dock
category: guides
modified: 2013-12-08
comments: true
share: true
---

So I was tired of having to hold my phone while plugging in a microusb cable after I've docked it in my car. I couldn't
find very many car docks out there with wireless charging, and I read that Nokia's wireless charging car dock didn't
work very well on the Nexus 5.

[![](http://i.imgur.com/7WTPx0v.gif)](http://imgur.com/7WTPx0v){: .pull-right .annotparent}
Previously I made my own Qi car dock by taking apart an LG Qi charger. But now that I have Google's new charger I made
a new one that's much better. The magnets in Google's charger are stronger and it looks a lot cleaner. I didn't need
any glue, tape, or additional magnets either. To make your own all you need is:

1. [Nexus Wireless Charger (Model A010)](https://play.google.com/store/devices/details?id=nexus_wireless_charger)
2. [Mountek nGroove Snap Magnetic Vehicle Mount](http://www.amazon.com/dp/B00E9L0HGI) (or a magnetic flat surface)
3. A 2 amp USB car adapter (I used [PowerGen 2.4Amps / 12W Dual USB](http://www.amazon.com/gp/product/B006SU0SX0))

The magnets in the nGroove Snap are just strong enough to attract the magnets in the wireless charger. The silicon
material on the foot of the charger is also very good at sticking to certain surfaces like the nGroove Snap. Because of
that I was able to drive around for three hours with my phone on the charger without any problems.

All you need to do is mount the nGroove Snap and then place the charger on it, and that's it! I routed the cable behind
my dash to make it look a bit cleaner ([instructions here]({% post_url 2010-07-03-Jetta-SportWagen-TDI %})).

<figure class="third">
    <!-- qi_attempt4_2.jpg -->
    <a href="http://imgur.com/GJE9zkv"><div class="annotparent"><img src="http://i.imgur.com/GJE9zkvm.jpg">
    </div></a>
    <!-- qi_attempt4_17.jpg -->
    <a href="http://imgur.com/55krwnA"><div class="annotparent"><img src="http://i.imgur.com/55krwnAm.jpg">
    </div></a>
    <!-- qi_attempt4_18.jpg -->
    <a href="http://imgur.com/7lHFKUv"><div class="annotparent"><img src="http://i.imgur.com/7lHFKUvm.jpg">
    </div></a>
    <figcaption></figcaption>
</figure>

# Previous Implementation

So I built my own. I originally posted everything
[on the XDA forums](http://forum.xda-developers.com/showthread.php?p=47509705#post47509705). Since the Nexus 5 has
[four metal discs](http://www.ifixit.com/Teardown/Nexus+5+Teardown/19016#s53717) inside it, it self-aligns when placed
on the dock and stays put in that position. You can see it self-align in the gif below. I drove 45mins from San
Francisco to San Jose and it never fell off. I was using GPS (Google Maps) and it looks like the magnets don't add too
much distance between the phone and the transmitting coil, my battery meter went up a little bit. More pictures
[here](http://imgur.com/a/dhFnO).

I used the following items:

* [30 Neodymium Magnets 5/16 x 1/8 inch Disc N48](http://www.amazon.com/gp/product/B008PT6P1Q/)
* [LG Electronics WCP-300 Wireless Charging Pad](http://www.amazon.com/gp/product/B00C6VP03I/)
* [Mountek nGroove Snap Magnetic Vehicle Mount](http://www.amazon.com/gp/product/B00E9L0HGI/)

[![](http://i.imgur.com/X8fbOGl.gif)](http://imgur.com/X8fbOGl){: .pull-right .annotparent}
For the final iteration, I reassembled the charging pad and everything holds together with just the magnetic force.
This is what I did:

1. Remove the feet of the charging pad and remove the four screws underneath. The charging pad's top should easily come
off.
2. Set aside the coil/ferrite plate/circuit board assembly for now.
3. The top half of the casing, with the LG logo, can disassemble further. The soft material (which you place your phone
on) should effortlessly pop off. Dispose of the remaining plastic ring.
4. The nGroove mount comes with two metal plates with adhesive. Apply one of the plates onto the soft material top,
covering up the LG logo.
5. Now place the soft material top onto the nGroove mount. It should magnetically stick together.
6. Get three magnets and place them on top of the underside of the soft material top. Make sure the polarity of the
magnets all face the same direction (the magnets will repel one another when placed next to each other). Place them in
the correct orientation as to get the most magnetic force between them and the nGroove magnet. This will hold the soft
material top firmly against the nGroove mount.
7. Now place the coil/plate/board with the four screws already inserted on top, having the coil face you. The magnets
will pull it so make sure you grab on to everything well while you try to align the screws with the holes. You'll
probably want to get some rubber washers between the plastic holes and the circuit board to give the three magnets some
room. I had a large piece of ~2mm thick rubber I cut up and pierced.
8. Screw everything together.
9. Place four additional magnets on top of the ferrite plate, next to each screw. Again make sure the polarity is the
same on all four, so they all repel each other.

Ok and that's it. The part about the three magnets and the plastic washers was done after I took these pictures. I
initially didn't do that and found after a few hours that the nGroove metal plate's adhesive has come off the soft
material top and the coil/ferrite/board fell off.

While this works great with my black Nexus 5, the white Nexus 5's back is less grippy, so you might have to plastidip
the magnets or add some kind of grippy material between them and the phone. I also tried this on the 2013 Nexus 7 but
that requires more magnets since it is heavier. Also on my Nexus 4, since it has less metal inside, has a smooth glass
back, and is heavier than the Nexus 5, it doesn't work very well on this dock. You'll probably need to get a grippy
case for it and add more magnets.

Here are some pictures of the final version, sans washers.

<figure class="third">
    <a href="http://imgur.com/COavxfY"><div class="annotparent"><img src="http://i.imgur.com/COavxfYm.jpg">
    </div></a>
    <a href="http://imgur.com/qJONaXG"><div class="annotparent"><img src="http://i.imgur.com/qJONaXGm.jpg">
    </div></a>
    <a href="http://imgur.com/GhOvZg9"><div class="annotparent"><img src="http://i.imgur.com/GhOvZg9m.jpg">
    </div></a>
</figure>

<figure class="half">
    <a href="http://imgur.com/OvXMV5w"><div class="annotparent"><img src="http://i.imgur.com/OvXMV5wm.jpg">
    </div></a>
    <a href="http://imgur.com/dRQ4q77"><div class="annotparent"><img src="http://i.imgur.com/dRQ4q77m.jpg">
    </div></a>
    <figcaption></figcaption>
</figure>

And here are some pictures after I routed the [wire inside the](http://www.amazon.com/gp/product/B003YKX6WW/) center
console. After you take out the shifter boot, little cubby, head unit, and air vents there is a ton of room inside to
route the wire. The front plate of the AC vents snaps on so I was able to pry it open just enough to squeeze the thin
wire in. I cut out a small notch of plastic to give the wire some room without blocking any of the vents' moving parts.
The only downside is I can't close the little cubby anymore. Oh well.

<figure class="third">
    <a href="http://imgur.com/sRKNN6F"><div class="annotparent"><img src="http://i.imgur.com/sRKNN6Fm.jpg">
    </div></a>
    <a href="http://imgur.com/8R5ROC4"><div class="annotparent"><img src="http://i.imgur.com/8R5ROC4m.jpg">
    </div></a>
    <a href="http://imgur.com/7jA3c1J"><div class="annotparent"><img src="http://i.imgur.com/7jA3c1Jm.jpg">
    </div></a>
    <figcaption>I didn't take a picture with the head unit and air vents removed, and damned if I take them out now. The
    clips around the head unit are fragile (I was lucky I didn't break any) and the air vent assembly is a total pain to
    put back in. Same goes for the shifter boot.</figcaption>
</figure>
