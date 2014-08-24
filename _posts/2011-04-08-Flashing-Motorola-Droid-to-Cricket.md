---
category: guides
layout: post
modified: 2012-06-12
title: Flashing Motorola Droid to Cricket
---

This guide will explain how to flash a Motorola Droid from Verizon to Cricket based on my experiences. The two
(similar) guides I followed had some inconsistencies and confused me until I pieced together clues from other sources.
My guide will explain the exact steps I took to get my Droid working on **Cricket's $55 Android plan**.

I used the following resources for my guide:

* [http://forum.xda-developers.com/showthread.ph...](hlinkttp://forum.xda-developers.com/showthread.php?t=708937)
* [http://www.mycricketforum.com/verizon-motorol...](http://www.mycricketforum.com/verizon-motorola-droid/5057-*sticky*-how-flash-motorola-droid-cricket-2-2-froyo-talk-text-mms-internet.html)
* [http://www.mycricketforum.com/flashing-tools-...](http://www.mycricketforum.com/flashing-tools-files-programming/6450-%2Asticky%2A-qpst-tutorial-pictures-cricket.html)
* [http://www.whiterabbit.org/android/](http://www.whiterabbit.org/android/)

After flashing, everything works for me except sending [long SMS](http://en.wikipedia.org/wiki/Concatenated_SMS)
(multipart texts that require two or more messages to be sent).

* Placing and receiving calls work.
* Writing and receiving normal SMS works.
    * Receiving long SMS works.
* Receiving MMS works.
    * Sending MMS started working magically after 12 hours.
* Data works fine, including the Market.

This guide will explain how to get a Motorola Droid (US, CDMA, Verizon version; not the GSM Milestone) from Verizon to
Cricket using a new $55/mo Android plan.

# Preface

I decided to break my contract with Verizon and incur a $95 ETF to port my number to Google Voice once I discovered I
could make/receive Gvoice calls for free [using a $50 device](http://www.obihai.com/product-primer.html) with my
landline telephones. When I ported my number on Saturday, it took 23.5 hours to finish porting on Sunday. On that day I
called Verizon to get a new phone number, but the representative informed me I will have to wait 7 days to reactivate
my phone without disturbing the porting process. I didn't want to risk losing my number so I decided to just wait a
week.

I checked how much the rate would be on Verizon without a contract (I'm waiting on a Webtop phone with an unlocked
bootloader) thinking it would be the same, but I found out it was $5/mo more than with a contract. Since then, I made
my mind up to move to Cricket while I waited for a phone I liked to come out.

# Prerequisites

## Software

1. Motorola Droid (US version, not the Milestone), rooted (probably) with SPRecovery (probably).
2. [Drivers for your phone](http://www.motorola.com/consumers/v/index.jsp?vgnextoid=bda09ec8009a0210VgnVCM1000008806b00aRCRD).
3. (probably?) [Android SDK](http://developer.android.com/sdk/index.html).
4. [42900.zip]({{ site.baseurl }}/static/binaries/42900.zip) (unzip this to get 42900.prl).
5. [HW VSP Singleport 3.1.2](http://www.hw-group.com/products/hw_vsp/index_en.html#DOWNLOAD)
6. CDMA Workshop 2.7 (google it).
7. QPST 2.7.355 (google it).

## Service

You will need an `MIN` (Mobile Identification Number) and an `MDN` (Mobile Device Number). Your `MDN` is your phone
number, from this point on I will refer to it as your **phone number**. In order to obtain these two values, you will
need to already have an account with Cricket. If you already have these two values from Cricket, skip this section.
Otherwise I will explain how to get these numbers by signing up with Cricket before flashing your phone. You will have
to pay for service up front ($55 for the first month, $15 activation, and tax). You can probably do this online but I
went to a local Cricket store.

In order to sign up with Cricket, you will need your `MEID` (Mobile Equipment Identifier) from your phone. You can get
your `MEID` from Android but it will be the HEX version, and Cricket needs it in DEC. To avoid converting hex to dec,
poweroff your phone and remove the battery. On the label beneath the battery on your phone you will find both HEX and
DEC `MEID`. You can either write down the DEC `MEID`, or better yet, take your phone to Cricket so they can scan the
barcode beneath it instead of manually typing the `MEID`.

Go to the Cricket store with your phone/`MEID` and ask to sign up for the $55 Android plan. Tell them you will flash
your phone later and all you will need is your phone number and your `MIN`. When they sign you up, they will print out
a paper with both of these values. Make sure your `MIN` and phone number are on it.

When you have your phone number and `MIN`, continue on to the next section.

## NVRAM Items

Once you have your `MIN` and phone number:

1. Generate a **CDMA Workshop 2.7** NVRAM file from here: [http://www.whiterabbit.org/android/](http://www.whiterabbit.org/android/)
    1. Where it says **Enter your login string**: enter **0000000000@mycricket.com** (replace zeros with your ten-digit
       phone number).
    2. Click **Generate**, it will download a text file roughly 6 KB in size.
    3. This is your NVRAM Items file.

# Installing Service

<div class="row">
    <div class="col-xs-12 col-sm-6 col-lg-3">
        <div class="thumbnail">
            <a href="http://imgur.com/SndBdi5" target="_blank">
                <img src="http://i.imgur.com/SndBdi5m.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 1</div>
        </div>
    </div>
    <div class="col-xs-12 col-sm-6 col-lg-3">
        <div class="thumbnail">
            <a href="http://imgur.com/2s0oJBW" target="_blank">
                <img src="http://i.imgur.com/2s0oJBWm.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 2</div>
        </div>
    </div>
    <div class="col-xs-12 col-sm-6 col-lg-3">
        <div class="thumbnail">
            <a href="http://imgur.com/sWaejkq" target="_blank">
                <img src="http://i.imgur.com/sWaejkqm.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 3</div>
        </div>
    </div>
    <div class="col-xs-12 col-sm-6 col-lg-3">
        <div class="thumbnail">
            <a href="http://imgur.com/IJgDFM4" target="_blank">
                <img src="http://i.imgur.com/IJgDFM4m.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 4</div>
        </div>
    </div>
</div>



## Flashing the Phone

1. Plug your phone into your computer and turn off the phone.
2. Slide out the keyboard and hold the `T` key while you press the power button for five seconds (probably unnecessary
but that's what I did).
3. Keep holding `T` until Android boots up as normal.
4. Open HW Virtual Serial Port.
    1. Click on the Settings tab.
    2. Uncheck **NVT Enabled**.
    3. Click on the Virtual Serial Port tab.
    4. Set Port Name to **COM10**.
    5. Set IP Address to **192.168.16.2**.
    6. Set Port to **11008**.
    7. Click on **Create COM** at the bottom and wait about 10 seconds.
    8. Make sure VSP Status is **Created** and LAN Status is **Connected** <cite>(Figure 1)</cite>.
5. Open CDMA Workshop v2.7.0
    1. Under "COM Settings (AT mode)" set Port to **COM10** and click **Connect**.
        1. The status bar at the bottom should read "Connected to COM10 port successfully".
    2. Click on the Security tab, and in the small text field under "SPC" type **000000** and click on SPC, then Send.
        1. A box will pop up and say "SPC is correct. Phone unlocked".
    3. Click on the Other tab, and under "PRL" click on Write and browse to **42900.prl**.
    4. Click on the Nam tab.
        1. Type your ten-digit `MIN` where it says MIN.
        2. Type your ten-digit phone number where it says **Dir_Number** <cite>(Figure 2)</cite>.
        3. Click on Write.
    5. Click on the Memory tab, and under "NV Items" click Write.
        1. It will say "You must send current SPC..." click OK.
        2. Browse to the NVRAM items text file you generated earlier.
        3. It should say it wrote 12 items to the phone.
    6. Click on the Main tab, and at the bottom click on the Mode button, then Reset.
    7. Your phone should reboot. Hold down `T` again like you did before.
    8. Close CDMA Workshop.
6. Go back to HW Virtual Serial Port and click **Delete COM**. Then do Create COM like you did before.
    1. If both statuses aren't Created and Connected, power off your phone and hold `T` while powering it on like
       before.
7. Open QPST Configuration from the Start Menu.
    1. Click on the Ports tab and click on the **Add New Port...** button.
        1. Select **COM10 - Serial** and click OK.
    2. After a few seconds the Phone column should have **SURFQSC6055 (NAND)...** underneath it.
    3. Click on Start Clients at the top, then Service Programming.
    4. A new window will open, you should see **Sholes P3** under Banner. Click OK.
    5. At the bottom click on **Read from Phone**. If not already, type **000000** and click OK.
        1. The progress bar should gradually increase and complete after about two or four minutes.
    6. Click on the M.IP tab, and set "Mobile IP Behavior" to **Mob + Simp f/back**.
    7. Double click on the first row in User Profile.
        1. Set NAI and Tethered NAI to **0000000000@mycricket.com** (replace zeros with your phone number) and click OK
           <cite>(Figure 3)</cite>.
    8. Click on the PPP Config tab and click on the **Um** button.
        1. Set Tethered NAI and User ID to the same thing (phonenumber@mycricket.com) and Password to **cricket**
           <cite>(Figure 4)</cite>.
        2. Click on the **AN** button at the top and do the same.
    9. Click on **Write to Phone** on the bottom. If your phone does not reboot, reboot it.
8. Close all QPST windows as well as the HW Virtual Serial Port (Delete COM first).

## Configuring APNs

<div class="row">
    <div class="col-xs-12 col-sm-6">
        <div class="thumbnail">
            <a href="http://imgur.com/NqeznNP" target="_blank">
                <img src="http://i.imgur.com/NqeznNPl.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 5</div>
        </div>
    </div>
    <div class="col-xs-12 col-sm-6">
        <div class="thumbnail">
            <a href="http://imgur.com/aHlRCy6" target="_blank">
                <img src="http://i.imgur.com/aHlRCy6l.jpg" class="img-responsive img-thumbnail">
            </a>
            <div class="caption">Figure 6</div>
        </div>
    </div>
</div>


1. Once Android boots back up, open the app **Voice Dialer**.
    1. Say aloud "Open APNs" and tap OK <cite>(Figure 5)</cite>.
2. Tap on the text **verizon** and set the following settings <cite>(Figure 6)</cite>:
    1. Name: Cricket
    2. APN: internet
    3. Proxy: (blank the field)
    4. Port: (blank the field)
    5. Username: phonenumber@mycricket.com
    6. Password: cricket
    7. Server: wap.mycricket.com
    8. MMSC: http://mms.mycricket.com/servlets/mms
    9. MMS proxy: wap.mycricket.com
    10. MMS port: 8080
    11. MCC: 310
    12. MNC: 004
    13. Authentication type: PAP or CHAP
    14. APN type: (blank the field)
3. Reboot your phone and you are done.
