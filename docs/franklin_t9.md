# T-Mobile Franklin T9 Hacking

```{tags} hacking, hotspot
```

My goal for this project is to have an LTE hotspot in my car that shuts off automatically when I get home to avoid wasting
data. I'm using it with [Google Fi](https://fi.google.com/).

```{imgur-embed} a/mwJuieo
:og_imgur_id: yZjfLix
```

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

Generate SSH key to use instead of password authentication
:   ```bash
    # On local computer
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/franklin_t9
    cat ~/.ssh/franklin_t9.pub
    # On hotspot
    mkdir /home/root/.ssh
    touch /home/root/.ssh/authorized_keys  # Paste public key in this file
    ```

## Flash Dumps

https://mega.nz/folder/K1ITBaqY#ess3TbmfhzrKCe_EyU5jSg

The dumps in the above link were created using the below command. I wasn't able to dump `mtd2`. Every time I tried to read it
the hotspot started to hang and I had to power cycle it.

```bash
for i in 0 1 {3..14}; do ssh 192.168.0.1 dd "if=/dev/mtd${i}ro" |pv > "mtd${i}ro.bin"; done
```

Something funny I noticed when running `strings mtd0ro-sbl.bin`:

```text
gcc_spmi_ser_clk
gcc_spmi_ahb_clk
`i9FBj
 pGO
BF1F F
fs_pm_ptable_nand.c
@!hF
FJx@
@"|@
`a|
DBGP
 pGpGp
DENTAL PLAN!
`BiB
 pGo
zppG
fs_efs2.c
fs_efs2.c
```

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

## Auto Reboot When No LTE

During long road trips I've noticed the hotspot doesn't automatically reconnect LTE even when I'm back in the service area.
Connecting via the web UI manually doesn't seem to work, but rebooting fixes it. Here I'll add a script that checks every 15
minutes for internet connectivity and if there isn't any it will automatically reboot the hotspot.

Save to /etc/default/auto_reboot
:   ```bash
    PING_HOSTS[0]=1.1.1.1  # Cloudflare DNS
    PING_HOSTS[1]=8.8.8.8  # Google DNS
    ```

Save to /usr/bin/auto_reboot.sh
:   ```{literalinclude} _static/auto_reboot.sh
    :language: bash
    ```

Save to /etc/init.d/start_auto_reboot
:   ```{literalinclude} _static/start_auto_reboot.sh
    :language: bash
    ```

Enable the service
:   ```bash
    chmod +x /usr/bin/auto_reboot.sh /etc/init.d/start_auto_reboot
    update-rc.d start_auto_reboot defaults
    /etc/init.d/start_auto_reboot start
    ```

## Custom Logos

You can easily change the logo on the little LCD by editing a PNG file. Since my unit is locked to T-Mobile I used:

* `/usr/franklin/mwin/resource/image/default/BW/t_mobile_idle_logo.png`

I edited that file using Paint 3D to keep the transparency.

```{imgur} MUdUSiT
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

```{imgur} 4Pdh8oi
:alt: T9 Power Button Wedge
:width: 100%
```

## Notes

Miscellaneous notes I took during my investigation.

### Datasheets

* https://datasheets.maximintegrated.com/en/ds/MAX77818.pdf

### Extract Kernel

Retrieve boot image from flash
:   ```bash
    # Shelled into hotspot
    grep boot /proc/mtd  # Mine says mtd6: 007e0000 00020000 "boot"
    # Local computer
    ssh root@192.168.0.1 dd if=/dev/mtd6ro |dd of=mtd6ro-boot.bin
    ```

Extract compressed kernel image
:   ```bash
    git clone https://github.com/xiaolu/mkbootimg_tools.git
    mkbootimg_tools/mkboot mtd6ro-boot.bin mtd6ro-boot
    binwalk mtd6ro-boot/kernel  # Mine says 16431 0x402F gzip compressed data
    dd if=mtd6ro-boot/kernel of=piggy.gz bs=1 skip=16431
    ```

## Interesting Info

### `free -m`

```text
             total         used         free       shared      buffers
Mem:           169          112           56            5            0
-/+ buffers:                112           56
Swap:            0            0            0
```

### `df -h`

```text
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

### `cat /proc/cpuinfo`

```text
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

### `uname -a`

```text
Linux mdm9607 3.18.48 #1 PREEMPT Fri Nov 13 14:21:47 KST 2020 armv7l GNU/Linux
```

### `lsmod`

```text
shortcut_fe_cm 6828 0 - Live 0xbf470000 (O)
shortcut_fe_ipv6 66440 1 shortcut_fe_cm, Live 0xbf45a000 (O)
shortcut_fe 68047 1 shortcut_fe_cm, Live 0xbf444000 (O)
wlan 4467738 0 - Live 0xbf000000 (O)
```

### `cat /proc/cmdline`

```{literalinclude} _static/t9_cmdline.txt
:language: text
```

### `cat /build.prop`

```text
ro.build.version.release=202011131402
ro.product.name=mdm9607-base
```

### `cat /proc/mtd`

```text
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

### `iw list`

```{literalinclude} _static/t9_iw_list.txt
:language: text
```

### `cat /sys/devices/1800000.qcom,debug/uevent`

```bash
DRIVER=qcom,cc-debug-mdm9607
OF_NAME=qcom,debug
OF_FULLNAME=/soc/qcom,debug@1874000
OF_COMPATIBLE_0=qcom,cc-debug-mdm9607
OF_COMPATIBLE_N=1
MODALIAS=of:Nqcom,debugT<NULL>Cqcom,cc-debug-mdm9607
```

### `cat /sys/class/power_supply/usb/device/uevent`

```bash
DRIVER=msm_otg
OF_NAME=usb
OF_FULLNAME=/soc/usb@78d9000
OF_COMPATIBLE_0=qcom,hsusb-otg
OF_COMPATIBLE_N=1
MODALIAS=of:NusbT<NULL>Cqcom,hsusb-otg
```

### `lsusb  # From host computer`

Powered on normally
:   ```text
    Bus 001 Device 031: ID 05c6:902d Qualcomm, Inc. MDM9207-MTP _SN:26F711A1
    ```

Fastboot mode
:   ```text
    Bus 001 Device 030: ID 18d1:d00d Google Inc. Xiaomi Mi/Redmi 2 (fastboot)
    ```

### `cat /proc/tty/drivers`

```text
/dev/tty             /dev/tty        5       0 system:/dev/tty
/dev/console         /dev/console    5       1 system:console
/dev/ptmx            /dev/ptmx       5       2 system
/dev/vc/0            /dev/vc/0       4       0 system:vtmaster
g_serial             /dev/ttyGS    239 0-3 serial
acm                  /dev/ttyACM   166 0-31 serial
smd_tty_driver       /dev/smd      245 0-36 serial
msm_serial_hsl       /dev/ttyHSL   246 0-2 serial
msm_serial_hs        /dev/ttyHS    247 0-255 serial
pty_slave            /dev/pts      136 0-1048575 pty:slave
pty_master           /dev/ptm      128 0-1048575 pty:master
unknown              /dev/tty        4 1-63 console
```

### `fastboot getvar all`

```text
(bootloader) version:0.5
(bootloader) variant:modem UFS
(bootloader) secure:no
(bootloader) version-baseband:
(bootloader) version-bootloader:
(bootloader) display-panel:
(bootloader) off-mode-charge:0
(bootloader) charger-screen-enabled:0
(bootloader) max-download-size: 0x8000000
(bootloader) serialno:12345678
(bootloader) kernel:lk
(bootloader) product:
all:
Finished. Total time: 0.021s
```

### `fastboot oem device-info`

```text
(bootloader)    Device tampered: false
(bootloader)    Device unlocked: false
(bootloader)    Device critical unlocked: false
(bootloader)    Charger screen enabled: false
(bootloader)    Display panel:
OKAY [  0.006s]
Finished. Total time: 0.007s
```

### `usb_composition`

```{literalinclude} _static/t9_usb_composition.txt
:language: text
```

### `cat /proc/kmsg  # dmesg`

```{literalinclude} _static/t9_dmsg.txt
```

### `dtc -I fs -O dts /proc/device-tree`

```{literalinclude} _static/t9_device_tree.dts
:language: dts
```

### `gzip -dc /proc/config.gz`

```{literalinclude} _static/t9_kernel_config.txt
:language: text
```

## Comments

```{disqus}
```
