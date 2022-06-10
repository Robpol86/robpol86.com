# Rooting the Netgear Nighthawk M1

```{tags} hacking, hotspot
```

This post will detail the steps I took to root my Netgear MR1100 LTE hotspot. My device was running firmware version
**NTG9X50C_12.06.39.00** at the time of this writing.

For this to work you must connect your computer to the hotspot using **USB tethering**.

## Access AT Commands

First thing I had to do was find a way to issue [AT](https://en.wikipedia.org/wiki/Hayes_command_set) commands to the
hotspot.

1. Verify you can ping the hotspot's LAN IP address (I'll be using `192.168.1.1`)
2. Telnet using port 5510: `telnet 192.168.1.1 5510`
3. Verify things look good so far by running `AT` and pressing enter
4. It should reply with "AT" and "OK" in two lines

## Enable Root Telnet

To enable telnet I had to enable engineering mode on the device via an OpenLock request. This was done using a handy Python
script available at two places:

* https://gist.github.com/jkinred/73689e463a08af963c45c137df6646d0
* [sierrakeygen.py](../../_static/sierrakeygen.py)

You'll need to find out what kind of device your MR1100 is based on. Since my firmware version contains the substring `9X50`
this tells me I have an `MDM9x50` device.

1. First run `AT!OPENLOCK?` to retrieve the openlock request code, it should respond with a code consisting of numbers and
   capital letters followed by "OK"
2. Now using the Python script run: `./sierrakeygen.py -l <request code> -d <device type>`
   1. I ran: `./sierrakeygen.py -l 09AEE80FB396B936 -d MDM9x50_V1`
   2. It should print an AT command, mine printed: `AT!OPENLOCK="A793A917DA37DD9A"`
3. Run the `AT!OPENLOCK` command the Python script printed out, it should reply with "OK"
4. Run `AT!TELEN=1`, `AT!CUSTOM="RDENABLE", 1`, and `AT!CUSTOM="TELNETENABLE", 1`, all three should have "OK" as responses
5. Reboot the hotspot

Once the hotspot comes back up you should now be able to `telnet 192.168.1.1 23` to get a root shell without a password
prompt. This should work over USB and ethernet.

To disable telnet replace the 1 with a 0 in the AT commands. You'll need to run the Python script and submit a new openlock
code after reboots.

## Interesting Info

### `free -m`

```text
             total         used         free       shared      buffers
Mem:           390          201          189            0            3
-/+ buffers:                197          193
Swap:            0            0            0
```

### `df -h`

```text
Filesystem                Size      Used Available Use% Mounted on
ubi0:rootfs              81.1M     59.2M     21.9M  73% /
tmpfs                    64.0K      4.0K     60.0K   6% /dev
tmpfs                   195.3M     20.0K    195.2M   0% /run
tmpfs                   195.3M    280.0K    195.0M   0% /var/volatile
tmpfs                   195.3M         0    195.3M   0% /media/ram
ubi0:usrfs               23.9M     24.0K     23.9M   0% /data
/dev/ubi1_0              50.8M     36.7M     14.1M  72% /firmware
ubi2:userrw               4.8M    880.0K      3.9M  18% /mnt/userrw
ubi3:hdata               43.5M     10.8M     32.7M  25% /mnt/hdata
tmpfs                     4.0K         0      4.0K   0% /media/drives
var                     195.3M    280.0K    195.0M   0% /var
/dev/loop0              896.0K    896.0K         0 100% /mnt/hdata/licenses
/dev/sda1                29.8G     32.0K     29.8G   0% /media/drives/card/sda1
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

Hardware        : Qualcomm Technologies, Inc MDM9650
Revision        : 0000
Serial          : 0000000000000000
Processor       : ARMv7 Processor rev 5 (v7l)
```

### `uname -a`

```text
Linux mdm9650 3.18.31 #1 PREEMPT Mon May 10 18:31:49 PDT 2021 armv7l GNU/Linux
```

### `lsmod`

```text
wlan 4312703 0 - Live 0xbf0fd000 (O)
xt_physdev 1810 8 - Live 0xbf0aa000
br_netfilter 9692 1 xt_physdev, Live 0xbf00a000
shortcut_fe_cm 6816 0 - Live 0xbf0fa000 (O)
shortcut_fe_ipv6 56811 1 shortcut_fe_cm, Live 0xbf0e8000 (O)
shortcut_fe 55924 1 shortcut_fe_cm, Live 0xbf0d6000 (O)
alx 79934 0 - Live 0xbf0bb000 (O)
ufsd 626321 0 - Live 0xbf00e000 (PO)
jnl 33481 1 ufsd, Live 0xbf000000 (O)
```

### `cat /proc/cmdline`

TODO

### `cat /build.prop`

```text
ro.build.version.release=202105101845
```

### `cat /proc/mtd`

```text
dev:    size   erasesize  name
mtd0: 00280000 00040000 "sbl"
mtd1: 00280000 00040000 "mibib"
mtd2: 01680000 00040000 "efs2"
mtd3: 00100000 00040000 "tz"
mtd4: 000c0000 00040000 "rpm"
mtd5: 00100000 00040000 "aboot"
mtd6: 00a40000 00040000 "boot"
mtd7: 00080000 00040000 "scrub"
mtd8: 046c0000 00040000 "modem"
mtd9: 00180000 00040000 "misc"
mtd10: 00a80000 00040000 "recovery"
mtd11: 000c0000 00040000 "fota_none"
mtd12: 016c0000 00040000 "recoveryfs"
mtd13: 08880000 00040000 "system"
mtd14: 00f80000 00040000 "pad1"
mtd15: 01440000 00040000 "userrw"
mtd16: 03ac0000 00040000 "hdata"
mtd17: 075c0000 00040000 "ntgfota"
mtd18: 008c0000 00040000 "cust"
mtd19: 00740000 00040000 "persist"
```

### `iw list`

TODO

### `cat /proc/kmsg  # dmesg`

TODO

## References

* https://gist.github.com/wombat/49f7c1b87b8c6918290a11504a624f62
* https://wirelessjoint.com/viewtopic.php?t=2988
* https://github.com/bkerler/edl/blob/master/sierrakeygen_README.md

## Comments

TODO

## TODOs

* SMS commands like STOP to pause fetching for n time. Authenticate with OTP codes

