# T-Mobile Franklin T9 Hacking

My goal for this project is to have an LTE hotspot in my car that shuts off automatically when I get home to avoid wasting
data. I'll be using it with [Google Fi](https://fi.google.com/) (using APN **h2g2**) to avoid paying any monthly fees for
another "line".

## Downgrade Firmware

I bought my unit from a seller on eBay brand new locked to the T-Mobile network (which is fine, Google Fi is a T-Mobile MVNO)
for $37 in November 2021. Sadly it came with firmware `R717F21.FR.2602` which removed the hidden menus. Thankfully someone
figured out how to downgrade this.

Follow these instructions to downgrade to firmware `R717F21.FR.1311`:
https://snt.sh/2021/09/rooting-the-t-mobile-t9-franklin-wireless-r717-again/

For me, once I downgraded the firmware the hotspot could no longer get service even though the Google Fi data-only SIM
wasn't removed. The only fix I found was to upgrade the firmware to a more recent version. Firmware `R717F21.FR.2000` fixed
the issue and still has the hidden pages. Download `R717F21.FR.2000_ota_update_all.enc` from:
https://mega.nz/folder/FJ8wWYAJ#Q1oUEtIUJrtjB1atkOAXrA

(Got that link from:
https://www.howardforums.com/showthread.php/1921612-Franklin-T9-Test-Drive-stuck-on-Welcome-This-is-the-fix)

## SSH and Root

After downgrading the firmware the next step is to enable SSH access so I can log in as root and have full control. These
steps came from: https://snt.sh/2020/09/rooting-the-t-mobile-t9-franklin-wireless-r717/

Download current configuration
: * Go to http://192.168.0.1/settings/device-backup_and_restore.html
  * Click on **Back Up Now**
  * Save the downloaded file as **hotspot_cfg.bin**

Unpack the configuration file
:   ```bash
    # Decrypt.
    openssl enc -aes-128-cbc -d -k "frkenc##KEY@R717" -md md5 -in hotspot_cfg.bin -out hotspot_cfg.tgz
    # Extract nested tar.gz files.
    mkdir -p hotspot_cfg/hotspot_cfg
    tar -xzf hotspot_cfg.tgz -C hotspot_cfg
    tar -xzf hotspot_cfg/hotspot_cfg.tar -C hotspot_cfg/hotspot_cfg
    ```

Edit hotspot_cfg/hotspot_cfg/data/configs/mobileap_cfg.xml
: * Look for **&lt;Ssh>0&lt;/Ssh>** and change it to **1**

Repack the configuration file
:   ```bash
    # Package inner tar.gz file.
    tar -czf hotspot_cfg/hotspot_cfg.tar -C hotspot_cfg/hotspot_cfg .
    rm -r hotspot_cfg/hotspot_cfg
    # Update hash from new inner tar.gz file.
    openssl dgst -md5 < hotspot_cfg/hotspot_cfg.tar |awk '{print "hotspot_cfg.tar="$2}' > hotspot_cfg/hashfile
    # Package outer tar.gz file.
    tar -czf hotspot_cfg.tgz -C hotspot_cfg .
    rm -r hotspot_cfg
    # Encrypt.
    openssl enc -aes-128-cbc -k "frkenc##KEY@R717" -md md5 -in hotspot_cfg.tgz -out hotspot_cfg_new.bin
    ```

Upload new configuration file
: * Go back to http://192.168.0.1/settings/device-backup_and_restore.html
  * Select **hotspot_cfg_new.bin** and click on **Restore Now**
  * Visit http://192.168.0.1/webpst/service_setting.html (password {guilabel}`frk@r717`) and confirm SSH is On
  * Finally `ssh root@192.168.0.1` with password {guilabel}`frk9x07`
  * Prevent new firmware from auto-installing by running: `mv /etc/init.d/start_omadm /home/root/`

## Static DHCP

One feature that I need for my project that's missing is static DHCP. I want certain clients to always get the same IP
address without having to configure them to use a static IP (since they also connect to other networks). I enabled this by
running the following commands:

```bash
# Enable dnsmasq conf-dir.
echo "conf-dir=/etc/dnsmasq.d" >> /etc/default/dnsmasq.conf

# Add configuration to separate file (last column optional).
cat > /etc/dnsmasq.d/static_dhcp.conf <<EOF
dhcp-host=bridge0,74:72:f3:90:ef:f6,192.168.0.10,raspberrypi
dhcp-host=bridge0,96:9c:a2:b5:ae:70,192.168.0.11
EOF
```

This survives reboots and user re-configurations from the hotspot web interface.

## Disable WiFi When Home

The main goal of this project is to kick off wireless users when the hotspot sees my home WiFi. I'm accomplishing this by
having a bash script that starts when the hotspot boots and does a WiFi scan every minute looking for my home SSID. When it
sees it the script will turn off the WiFi access point of the hotspot.

It will keep scanning every minute until it no longer sees my home SSID for a couple of scans (sometimes SSIDs intermittently
don't show up). Once that condition is met the script will re-enable the hotspot's WiFi access point.

Save to /etc/default/wifi_toggle
:   ```bash
    HOME_SSID="your home ssid here"
    ```

Save to /usr/bin/wifi_toggle.sh
:   ```{literalinclude} _static/wifi_toggle.sh
    :language: bash
    ```

Save to /etc/init.d/start_wifi_toggle
:   ```{literalinclude} _static/start_wifi_toggle.sh
    :language: bash
    ```

Enable the service
:   ```bash
    chmod +x /usr/bin/wifi_toggle.sh /etc/init.d/start_wifi_toggle
    update-rc.d start_wifi_toggle defaults
    /etc/init.d/start_wifi_toggle start
    ```

## Custom Logos

You can easily change the logo on the little LCD by editing a PNG file. Since my unit is locked to T-Mobile I used:

* `/usr/franklin/mwin/resource/image/default/BW/t_mobile_idle_logo.png`

I edited that file using Paint 3D to keep the transparency.

```{image} _static/img/t9_logo.jpg
:alt: Hacked Logo
:width: 100%
```

## Fastboot

There are a couple of ways to get the device to boot into
[fastboot mode](https://developer.android.com/studio/command-line#tools-platform): the hard way and the easy way. This
hotspot is basically an Android device without the screen or phone part.

### Hard Way

The hard way to get into fastboot is to open up the device and short a couple of pins:

1. Remove circuit board from case
1. Plug in USB power
1. Short the two pins circled in red in the image below
1. Power on with the power button

```{imgur-image} gi7e24z
```

The device should show up when you run `fastboot devices` within a couple of seconds, and the hotspot's display will just
say "Welcome" the entire time.

```{imgur-image} pJ9WuSf
```

To get out of fastboot mode just power cycle it or run `fastboot continue`.

Since I posted one side of the circuit board here's the other side even thought it's irrelevant to this section:

```{imgur-image} aC7SUuC
```

### Easy Way

There's an easier way to get into fastboot mode if you have root SSH access. There's no need to open up the device either.
Just SSH in and run the command:

```bash
reboot-bootloader
```

## ADB

Enabling ADB takes more than just running `/sbin/adbd`. You need to change the USB mode with a conveniently installed
command: `usb_composition`

When you run `usb_composition` you'll get the current setting, the list of available settings, and a prompt where you can
change the current setting. In my case the original setting was `9057 - RNDIS : ECM`.  To enable ADB I chose
`902D - RNDIS + DIAG + ADB [Android]`. This setting enabled ADB and still kept USB networking so I could still SSH and have
network access over USB.

```
Pid number : 902D
Choose core: y - hsic, n - hsusb  ? (y/n)n
Would you like it to be the default composition ? (y/n)y
Would you like the composition to change immediately? (y/n)y
Are you performing the composition switch from adbd? (y/n)n
ln: /sbin/usb/compositions/hsusb_next: File exists
```

The device should immediately show up when you run `adb devices`.

```{imgur-image} dFVo3HQ
```

## Automatic Power On

Unfortunately this hotspot does not automatically boot up upon being powered, you have to press the power button. I spent an
entire day trying to find a software solution for this but sadly I could not. Not even `fastboot oem off-mode-charge 0`
worked. I ended up with a physical solution instead.

It turns out if you hold down the power button when you plug in the device, it will fully boot up. Luckily if you continue
to hold the button it won't shut back down. Knowing this the solution is to cut a piece of plastic into a "U" shape and wedge
it between the case and the button so it's always pressed down.

```{image} _static/img/t9_power_wedge.jpg
:alt: T9 Power Button Wedge
:width: 100%
```

## Interesting Information

For anyone who's curious here are some dumps:

`cat /sys/devices/1800000.qcom,debug/uevent`
:   ```bash
    DRIVER=qcom,cc-debug-mdm9607
    OF_NAME=qcom,debug
    OF_FULLNAME=/soc/qcom,debug@1874000
    OF_COMPATIBLE_0=qcom,cc-debug-mdm9607
    OF_COMPATIBLE_N=1
    MODALIAS=of:Nqcom,debugT<NULL>Cqcom,cc-debug-mdm9607
    ```

`cat /sys/class/power_supply/usb/device/uevent`
:   ```bash
    DRIVER=msm_otg
    OF_NAME=usb
    OF_FULLNAME=/soc/usb@78d9000
    OF_COMPATIBLE_0=qcom,hsusb-otg
    OF_COMPATIBLE_N=1
    MODALIAS=of:NusbT<NULL>Cqcom,hsusb-otg
    ```

`gzip -dc /proc/config.gz |grep -v "^#" |grep -iE "swap|otg|mass"`
:   ```bash
    CONFIG_SWAP=y
    CONFIG_ARCH_USE_BUILTIN_BSWAP=y
    CONFIG_USB_MSM_OTG=y
    CONFIG_USB_F_MASS_STORAGE=y
    ```

`df -h`
:   ```text
    Filesystem                Size      Used Available Use% Mounted on
    ubi0:rootfs              49.2M     45.8M      3.3M  93% /
    tmpfs                    64.0K      4.0K     60.0K   6% /dev
    tmpfs                    78.0M     36.0K     77.9M   0% /run
    tmpfs                    78.0M      5.2M     72.7M   7% /var/volatile
    tmpfs                    78.0M         0     78.0M   0% /media/ram
    ubi0:usrfs                8.1M    724.0K      7.4M   9% /data
    ubi0:cachefs             63.1M     55.5M      4.3M  93% /cache
    /dev/ubi1_0              29.9M     26.5M      3.4M  89% /firmware
    ```

`free -m`
:   ```text
                 total         used         free       shared      buffers
    Mem:           169          112           56            5            0
    -/+ buffers:                112           56
    Swap:            0            0            0
    ```

`cat /proc/mtd`
:   ```text
    dev:    size   erasesize  name
    mtd0: 00140000 00020000 "sbl"
    mtd1: 00140000 00020000 "mibib"
    mtd2: 00c00000 00020000 "efs2"
    mtd3: 000c0000 00020000 "tz"
    mtd4: 00060000 00020000 "rpm"
    mtd5: 000a0000 00020000 "aboot"
    mtd6: 007e0000 00020000 "boot"
    mtd7: 01040000 00020000 "scrub"
    mtd8: 02900000 00020000 "modem"
    mtd9: 00140000 00020000 "misc"
    mtd10: 007e0000 00020000 "recovery"
    mtd11: 00180000 00020000 "fota"
    mtd12: 011e0000 00020000 "recoveryfs"
    mtd13: 00040000 00020000 "sec"
    mtd14: 091e0000 00020000 "system"
    ```

`cat /proc/cpuinfo`
:   ```text
    processor       : 0
    model name      : ARMv7 Processor rev 5 (v7l)
    BogoMIPS        : 38.40
    Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpv4 idiva idivt vfpd32 lpae
    CPU implementer : 0x41
    CPU architecture: 7
    CPU variant     : 0x0
    CPU part        : 0xc07
    CPU revision    : 5
    Hardware        : Qualcomm Technologies, Inc MDM9207
    Revision        : 0000
    Serial          : 0000000000000000
    Processor       : ARMv7 Processor rev 5 (v7l)
    ```

`cat /proc/cmdline`
:   ```text
    noinitrd rw console=ttyHSL0,115200,n8 androidboot.hardware=qcom ehci-hcd.park=3 msm_rtb.filter=0x37 lpm_levels.sleep_disabled=1 earlycon=msm_hsl_uart,0x78b3000 androidboot.serialno=12345678 androidboot.authorized_kernel=true androidboot.baseband=msm rootfstype=ubifs rootflags=bulk_read root=ubi0:rootfs ubi.mtd=14
    ```

`usb_composition`
:   ```text
    boot hsusb composition: 9057
    boot hsic composition: empty
    Choose Composition by Pid:
       901D -       DIAG + ADB
       9021 -       DIAG + QMI_RMNET (Android)
       9022 -       DIAG + ADB + QMI_RMNET (Android)
       9024 -       RNDIS + ADB [Android]
       9025 -       DIAG + ADB + MODEM + NMEA + QMI_RMNET + Mass Storage (Android)
       902B -       RNDIS + ADB + Mass Storage
       902D -       RNDIS + DIAG + ADB [Android]
       9039 -       MTP + ADB(Android)
       9049 -       DIAG + ADB + DUN + RMNET + Mass Storage + QDSS [Android]
       904A -       DIAG + QDSS [Android]
       9056 -       DIAG + ADB + SERIAL + RMNET + Mass Storage + Audio [Android]
       9057 -       RNDIS : ECM
       9059 -       DIAG+ADB+RNDIS : ECM
       905B -       MBIM
       9060 -       DIAG + QDSS + ADB
       9063 -       RNDIS : ECM : MBIM
       9064 -       DIAG + ADB + MODEM + QMI_RMNET : ECM : MBIM
       9067 -       Mass storage + QMI_RMNET : Mass Storage + MBIM
       9084 -       DIAG + QDSS + ADB + RMNET
       9085 -       DIAG+ADB+MBIM+GNSS
       9091 -       DIAG + MODEM + QMI_RMNET + ADB
       90A1 -       DIAG + ADB + (multiplexed) QMI_RMNET (Android)
       90A9 -       DIAG + ADB + MODEM + NMEA + QDSS (bulk in) + RMNET : ECM : MBIM
       90AD -       DIAG + ADB + MODEM + NMEA (Disable in 9x07 only : + QMI_RMNET + Mass Storage + DPL)
       90B1 -       ECM
       90CA -       DIAG + ADB + UAC2
       90CD -       DIAG + ADB + GNSS
       90D5 -       DIAG + ADB + MBIM + GNSS + DUN
       90D6 -       DIAG + MBIM + GNSS + DUN
       90F3 -       DIAG + RmNet + IPC_ROUTER
       F000 -       Mass Storage
       __emptyfile__ -
       empty -      it is used to allow either hsic or hsusb to have no composition at all(must reboot to take effect).
       hsic_next -
       hsusb_next -
    Pid number :
    ```

`iw list`
:   ```text
    Wiphy phy0
            Band 1:
                    Capabilities: 0x9072
                            HT20/HT40
                            Static SM Power Save
                            RX Greenfield
                            RX HT20 SGI
                            RX HT40 SGI
                            No RX STBC
                            Max AMSDU length: 3839 bytes
                            DSSS/CCK HT40
                            L-SIG TXOP protection
                    Maximum RX AMPDU length 65535 bytes (exponent: 0x003)
                    Minimum RX AMPDU time spacing: 16 usec (0x07)
                    HT TX/RX MCS rate indexes supported: 0-7
                    Frequencies:
                            * 2412 MHz [1] (30.0 dBm)
                            * 2417 MHz [2] (30.0 dBm)
                            * 2422 MHz [3] (30.0 dBm)
                            * 2427 MHz [4] (30.0 dBm)
                            * 2432 MHz [5] (30.0 dBm)
                            * 2437 MHz [6] (30.0 dBm)
                            * 2442 MHz [7] (30.0 dBm)
                            * 2447 MHz [8] (30.0 dBm)
                            * 2452 MHz [9] (30.0 dBm)
                            * 2457 MHz [10] (30.0 dBm)
                            * 2462 MHz [11] (30.0 dBm)
                            * 2467 MHz [12] (disabled)
                            * 2472 MHz [13] (disabled)
                            * 2484 MHz [14] (disabled)
                    Bitrates (non-HT):
                            * 1.0 Mbps
                            * 2.0 Mbps
                            * 5.5 Mbps
                            * 11.0 Mbps
                            * 6.0 Mbps
                            * 9.0 Mbps
                            * 12.0 Mbps
                            * 18.0 Mbps
                            * 24.0 Mbps
                            * 36.0 Mbps
                            * 48.0 Mbps
                            * 54.0 Mbps
            Band 2:
                    Capabilities: 0x9072
                            HT20/HT40
                            Static SM Power Save
                            RX Greenfield
                            RX HT20 SGI
                            RX HT40 SGI
                            No RX STBC
                            Max AMSDU length: 3839 bytes
                            DSSS/CCK HT40
                            L-SIG TXOP protection
                    Maximum RX AMPDU length 65535 bytes (exponent: 0x003)
                    Minimum RX AMPDU time spacing: 16 usec (0x07)
                    HT TX/RX MCS rate indexes supported: 0-7
                    Frequencies:
                            * 5180 MHz [36] (30.0 dBm)
                            * 5200 MHz [40] (30.0 dBm)
                            * 5220 MHz [44] (30.0 dBm)
                            * 5240 MHz [48] (30.0 dBm)
                            * 5260 MHz [52] (24.0 dBm) (radar detection)
                            * 5280 MHz [56] (24.0 dBm) (radar detection)
                            * 5300 MHz [60] (24.0 dBm) (radar detection)
                            * 5320 MHz [64] (24.0 dBm) (radar detection)
                            * 5500 MHz [100] (24.0 dBm) (radar detection)
                            * 5520 MHz [104] (24.0 dBm) (radar detection)
                            * 5540 MHz [108] (24.0 dBm) (radar detection)
                            * 5560 MHz [112] (24.0 dBm) (radar detection)
                            * 5580 MHz [116] (24.0 dBm) (radar detection)
                            * 5600 MHz [120] (24.0 dBm) (radar detection)
                            * 5620 MHz [124] (24.0 dBm) (radar detection)
                            * 5640 MHz [128] (24.0 dBm) (radar detection)
                            * 5660 MHz [132] (24.0 dBm) (radar detection)
                            * 5680 MHz [136] (24.0 dBm) (radar detection)
                            * 5700 MHz [140] (24.0 dBm) (radar detection)
                            * 5720 MHz [144] (24.0 dBm) (radar detection)
                            * 5745 MHz [149] (30.0 dBm)
                            * 5765 MHz [153] (30.0 dBm)
                            * 5785 MHz [157] (30.0 dBm)
                            * 5805 MHz [161] (30.0 dBm)
                            * 5825 MHz [165] (30.0 dBm)
                            * 5845 MHz [169] (disabled)
                            * 5865 MHz [173] (20.0 dBm) (passive scanning, no IBSS, radar detection)
                    Bitrates (non-HT):
                            * 6.0 Mbps
                            * 9.0 Mbps
                            * 12.0 Mbps
                            * 18.0 Mbps
                            * 24.0 Mbps
                            * 36.0 Mbps
                            * 48.0 Mbps
                            * 54.0 Mbps
            max # scan SSIDs: 10
            max scan IEs length: 500 bytes
            Coverage class: 0 (up to 0m)
            Supported Ciphers:
                    * WEP40 (00-0f-ac:1)
                    * WEP104 (00-0f-ac:5)
                    * TKIP (00-0f-ac:2)
                    * CCMP (00-0f-ac:4)
                    * WPI-SMS4 (00-14-72:1)
                    * CMAC (00-0f-ac:6)
            Available Antennas: TX 0 RX 0
            Supported interface modes:
                     * IBSS
                     * managed
                     * AP
                     * P2P-client
                     * P2P-GO
            software interface modes (can always be added):
            valid interface combinations:
                     * #{ managed } <= 3,
                       total <= 3, #channels <= 2
                     * #{ managed } <= 1, #{ IBSS } <= 1,
                       total <= 2, #channels <= 1
                     * #{ AP } <= 3,
                       total <= 3, #channels <= 2
                     * #{ P2P-client } <= 1, #{ P2P-GO } <= 1,
                       total <= 2, #channels <= 2
                     * #{ managed } <= 2, #{ AP } <= 2,
                       total <= 4, #channels <= 2, STA/AP BI must match
                     * #{ managed } <= 2, #{ P2P-client, P2P-GO } <= 2,
                       total <= 4, #channels <= 2, STA/AP BI must match
                     * #{ managed } <= 2, #{ P2P-GO } <= 1, #{ AP } <= 1,
                       total <= 4, #channels <= 2, STA/AP BI must match
            Supported commands:
                     * new_interface
                     * set_interface
                     * new_key
                     * start_ap
                     * new_station
                     * set_bss
                     * join_ibss
                     * set_pmksa
                     * del_pmksa
                     * flush_pmksa
                     * remain_on_channel
                     * frame
                     * frame_wait_cancel
                     * set_channel
                     * testmode
                     * connect
                     * disconnect
            Supported TX frame types:
                     * IBSS: 0x00 0x10 0x20 0x30 0x40 0x50 0x60 0x70 0x80 0x90 0xa0 0xb0 0xc0 0xd0 0xe0 0xf0
                     * managed: 0x00 0x10 0x20 0x30 0x40 0x50 0x60 0x70 0x80 0x90 0xa0 0xb0 0xc0 0xd0 0xe0 0xf0
                     * AP: 0x00 0x10 0x20 0x30 0x40 0x50 0x60 0x70 0x80 0x90 0xa0 0xb0 0xc0 0xd0 0xe0 0xf0
                     * P2P-client: 0x00 0x10 0x20 0x30 0x40 0x50 0x60 0x70 0x80 0x90 0xa0 0xb0 0xc0 0xd0 0xe0 0xf0
                     * P2P-GO: 0x00 0x10 0x20 0x30 0x40 0x50 0x60 0x70 0x80 0x90 0xa0 0xb0 0xc0 0xd0 0xe0 0xf0
            Supported RX frame types:
                     * IBSS: 0x00 0x20 0x40 0xa0 0xb0 0xc0 0xd0
                     * managed: 0x40 0x60 0xd0
                     * AP: 0x00 0x20 0x40 0xa0 0xb0 0xc0 0xd0
                     * P2P-client: 0x40 0xd0
                     * P2P-GO: 0x00 0x20 0x40 0xa0 0xb0 0xc0 0xd0
            WoWLAN support:
                     * wake up on anything (device continues operating normally)
                     * wake up on disconnect
                     * wake up on magic packet
                     * wake up on pattern match, up to 4 patterns of 6-64 bytes
                     * can do GTK rekeying
                     * wake up on GTK rekey failure
                     * wake up on EAP identity request
                     * wake up on 4-way handshake
                     * wake up on rfkill release
            Device supports roaming.
            Device supports HT-IBSS.
    ```

## Comments

```{disqus}
```
