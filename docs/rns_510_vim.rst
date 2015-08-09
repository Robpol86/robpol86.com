.. _rns_510_vim:

==========================
US RNS-510 Video In Motion
==========================

.. warning::

    Obviously playing DVDs while driving is dangerous and in the USA you'll probably get pulled over for it if a cop
    sees it depending if your state has made it illegal. Making any changes to your RNS-510 head unit always has the
    possibility of bricking the device and you'll be left with a $2000 paper weight. Proceed at your own risk.

Background
==========

After purchasing a VW 2010 Jetta SportWagen TDI with the DVD/Navigation option I've been searching for a way to get the
head unit to play DVD video while driving so that my passengers can watch their DVDs while I drive on long road trips.
I finally discovered a way to enable this feature. You will not need to purchase anything or make any prior changes.
All you need is a CD-R and a CD burner.

The original thread on vwnavi.com was deleted so I will be mirroring my steps and the files here. I'm assuming these
files were created by Berto89 from VWItalia.it [1]_, thanks to him I was able to get VIM working on my US unit. In the
download link below you will find a zip file containing two files:

VIM_Berto89.iso
---------------

This file contains a script that changes the DVD playback speed limit from 10 km/h to 300 km/h. This means that the
screen won't be blanked until you are doing 300 km/h. The script also enables Test Mode (or the "Secret Menu"), which
you can access by pressing and holding the Setup button for several seconds. I believe there will be a total of three
different Setup screens while holding down the button.

If you want to get technical, the magic happens in the file ``\WA\VIM.WSH``

* MD5 checksum: 5eca311f5de010132bbb47d29f2a0ad7
* Size: 156 KB

RECODE_Berto89.iso
------------------

This optional file reverts the changes from VIM_Berto89.iso back to the default factory settings (10 km/h and disables
Test Mode). Use this if you want to undo changes.

* MD5 checksum: 0acc8989a2cf0ab2e4de75b7c71bcebc
* Size: 156 KB

Procedure
=========

I have amended this section after reading a few forums about this topic with an alternate solution. [2]_ [3]_ [4]_ [5]_

If you get any errors when attempting to enable VIM (Video In Motion) try burning the files using another CD burning
program and try another brand of CD-R. That seems to fix the problem for most people from what I can see.

For some people, simply turning on the RNS-510 unit (no need to start the ignition) and inserting the CD will start the
update process. Be sure to press OK on the white screen when it appears. Other than that, everything should be hands
off, it will even automatically eject the CD when it's done.
`Someone made a video using this procedure <https://www.youtube.com/watch?v=ed-sDo7k5Sg>`_.

That didn't work for me, so I went the long way. These are the steps I took to enable VIM on my factory RNS-510 unit
that came with my VW I bought in Texas. Again, proceed at your own risk:

1. Start the car.
2. Press and hold the ``Eject``, ``Day/Night``, and ``Guide`` buttons.
3. Quickly insert your burned VIM CD-R, keep holding the three buttons.
4. The RNS-510 unit should automatically restart, once it does that let go of the buttons.
5. The unit will reboot a few times, even saying something like "failed to start, insert cd". Ignore that and keep
   waiting.
6. After a few more reboots you will see a white screen with OK and Cancel buttons. Tap on **OK**.
7. Again the unit will reboot a few more times.
8. When it shows a screen with a green rectangle saying "Success", eject the CD with the ``eject`` button.
9. The unit will automatically reboot one last time.
10. Once it boots up everything should be like normal.

At this point you should be able to insert a DVD while driving and the screen will not be blanked.

Download
========

:download:`Here is the zip file with both ISOs. <RECODE_VIM_Berto89.zip>`

References
==========

.. [1] http://www.vwitalia.it/forum/members/berto89/
.. [2] https://forums.tdiclub.com/showthread.php?t=326199
.. [3] http://www.golfmk6.com/forums/showthread.php?t=22712
.. [4] http://forums.vwvortex.com/showthread.php?5395639-RNS-510-Video-In-Motion-via-firmware-change-5-min-job-and-free
.. [5] http://myturbodiesel.com/forum/f9/how-unlock-rns510-vim-tv-free-free-video-motion-play-dvd-while-driving-9150/

Comments
========

.. disqus::
