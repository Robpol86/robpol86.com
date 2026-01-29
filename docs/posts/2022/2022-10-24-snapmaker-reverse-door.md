---
blogpost: true
date: 2022-10-24
author: Robpol86
location: Austin
category: Tutorials
tags: 3d-printing
---

# Snapmaker Enclosure Door Reversal

[enclosure]: https://us.snapmaker.com/products/enclosure-for-snapmaker-2-0

I recently moved my Snapmaker 2.0 A350T printer to another part of my home. The [official enclosure][enclosure] has a solid
panel on the left side, a large door on the right, and a smaller door on the front. These panels are only designed to be
installed in one specific order and orientation.

In this post I describe the steps I took to swap the solid panel and large door as well as "flip" the front panel so it opens
on the opposite side. There are a few minor drawbacks to this modification but the solutions I came up with neutralizes them.
These workarounds are also non-desctructive so I can restore my enclosure back to its original design.

```{seealso}
https://forum.snapmaker.com/t/enclosure-door-sides/9503/9
```

## Drawbacks

[t-nuts]: https://www.amazon.com/Socell-180Pcs-Hammer-Fastener-Assortment/dp/B07Z4YH6NP
[stripping]: https://www.amazon.com/uxcell-Thick-Adhesive-Weather-Strip/dp/B07L6LB49S

* **Foot fixtures**: The bottom rails have extra screw holes and indentations so that the foot fixtures can be installed
  precisely. The top rails lack these indentations and screw holes.
    * Solution: If you have bought the emergency stop button you may have four spare T-nuts and M4x8 screws you can use (if
      not you can buy extra [M4 2020 T-nuts][t-nuts] or you can just drill and tap new threaded holes in the rails). You
      should also measure the distance between the indentation and the end of the bottom rails and mark them on the top rails
      with a marker.
* **Touchscreen**: Since we're rotating everything 180 degrees the touchscreen cutout on the front door will be at the top
  instead of the bottom. We'll be fixing this by flipping the panel but this will place the foam strips facing out instead of
  in.
    * Solution: Buy some 10 mm wide by 3 mm thick self-adhesive [weather stripping][stripping] (or cut yours to size).
* **Top panel**: The bottom side of the enclosure doesn't have as many screw holes as the top. Only the two narrow sides of
  the top panel will have holes that align.
    * Solution: You can drill additional holes on the plexiglass top panel or using more T-nuts but I ended up just relying
      on the four screws to hold the top panel in place, so this was a non-issue for me.

## Steps

1. Remove all plexiglass panels and doors.
2. Remove the rear top (with the converter hub) and rear bottom 24 BEAM A350-4 rails.
3. Measure the offsets of the **foot fixture** indentations on the bottom rails (my enclosure measured 123 mm offset).
4. Facing front to back flip the entire enclosure 180 degrees (e.g. top is now on the bottom).
5. Relocate the LED strips from the bottom to the top rails (the tiny screws aren't necessary).
6. Flip the hall sensor (little black box on a vertical rail) 180 degrees so you can run the cable along the top.
7. For the **foot fixtures** insert two M4 2020 T-nuts into each bottom rail.
8. Mark on the now-bottom rails the **foot fixture** offsets.
9. Reinstall the rear rails, keeping the one with the converter hub at the top.
10. Install the doors. Flip the small-door panel with the **touchscreen** cutout and apply the self-adhesive weather
    stripping on the flipped panel.

## Pictures

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-J09tdcy.jpg
    %
    Finished project.
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-D1sV4X8.jpg
    %
    Removed the LED strips from the now-bottom rails to relocate them back to the top of the enclosure.
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-5cDGBUU.jpg
    %
    Flip the hall/door sensor. I used a zip tie to help keep the plastic washers in place. The sensor actually has bright white
    LEDs that light up when it detects when the two doors are closed.
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-yJP9vVH.jpg
    %
    Half way through I put the doors on to verify they fit and close properly. The magnets are aligned just fine.
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-wGu1uNO.jpg
    %
    Mark where the foot fixtures will go and use T-nuts to fasten them in place.
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-J03jTjo.jpg
    %
    The touchscreen cord is long enough to reach its new location. I used a spare screw to ensure it won't ride up and touch the
    hot platform or get pinched by the moving platform.
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-osjlmEC.jpg
    %
    Installed some additional weather stripping after flipping this enclosure panel with the touchscreen cutout.
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-Rbld72t.jpg
    %
    Unrelated: for my new coffee table setup I'm moving the power supply to be on top of the UPS and not take up table space.
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-iFNKJxn.jpg
    %
    I bought a filament dry box from Amazon instead of relocating the spool holder which would have required cutting or drilling
    into the enclosure panels. This works for me because I already use a PTFE/Teflon tube with my printer.
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-bNa6Ul4.jpg
    %
    Done!
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-B6j9Ws3.jpg
    %
    Teflon tube routing: dry box
    :::
  - :::{thumb-figure} /_images/pictures/imgur-import/imgur-XJZNBUH.jpg
    %
    Teflon tube routing: enclosure through-hole
    :::
* - :::{thumb-figure} /_images/pictures/imgur-import/imgur-aDOjJnX.jpg
    %
    Teflon tube routing: print head
    :::
  -
```
