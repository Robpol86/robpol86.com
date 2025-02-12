---
blogpost: true
date: 2025-02-10
author: Robpol86
location: Santiago
category: Tutorials
tags: homelab, runbook, aiffro
---

# TrueNAS SCALE Aiffro Runbook

This is the runbook I've been developing since 2022 for setting up and maintaining
[TrueNAS SCALE](https://www.truenas.com/truenas-scale/) on my portable/travel NAS as of this date. Originally developed for a
more traditional 24/7 server, it's now scoped to a NAS that is frequently powered off and no longer has access to the
intenret.

As of this writing my NAS is an [Aiffro K100](https://www.aiffro.com/products/all-ssd-nas-k100). The machine only has 8 GiB
of RAM with no ECC so I had to make some consessions. The no ECC part is a gamble but so far I haven't run into any data
corruption issues, and my use case does not require running apps on TrueNAS so 8 GiB of RAM is sufficient (I still hit
near-2.5Gbps speeds consistently). This is purely for data storage and access over Samba with my macOS single client.

TODO: confirm mobile view.

---

## 1.0.0 Installation Procedure

This section will go over listing the prerequisites, preparing the installation media, and installing the OS onto the Aiffro.
Avoid using the USB-A ports on the Aiffro since they're limited to USB 2.0 speeds.

### 1.1.0 Prerequisites

- [Aiffro K100](https://www.aiffro.com/products/all-ssd-nas-k100)
- One **16 GiB** or greater SSD on a [USB-C to M.2 adapter](https://www.amazon.com/ORICO-Enclosure-10Gbps-Adapter-Supports/dp/B0CQ4NXK7Q)
    - This will be called the **OS drive** in this runbook
    - This will be the OS drive/boot pool
    - TrueNAS [recommends against](https://www.reddit.com/r/truenas/comments/16yg23m/truenas_recommends_against_using_a_usb_key_for/)
      using regular USB flash drives as the boot pool
- One **2 GiB** or greater USB-C flash drive
    - This will be called the **USB installer drive** in this runbook
    - This will be the installation media with the ISO "burned" onto it
- Four NVMe SSDs for storage
- An [AURGA Viewer](https://www.aurga.com/products/aurga-viewer)
    - You can also use a regular USB keyboard and HDMI display, however this runbook is written with the AURGA in mind since
      that's what I bring with me whilst traveling
- The AURGA Viewer app on your laptop/workstation

### 1.2.0 Prepare USB Installer

1. **Download TrueNAS SCALE ISO:**
    - Get the latest **stable** ISO from https://www.truenas.com/download-truenas-scale/
2. **Create Bootable USB:**
    - Plug the **USB installer drive** into your laptop/workstation
    - If you're using Windows:
        - Use [Rufus](https://rufus.ie/en/) in `dd` mode (it will prompt you when you click START)
    - If you're using macOS or Linux:
        - Find the device name of the USB drive (using Disk Utility on macOS or looking in `/dev` on Linux) e.g. `disk6` or `sdb`.
        - Run in Terminal: `sudo dd if=TrueNAS-SCALE-24.10.1.iso of=/dev/disk6`

### 1.3.0 Configure BIOS

```{note}
AURGA will not apply a keypress until the SHIFT key is released, so don't hold it for consecutive capital letters.
```

1. **Setup AURGA:**
    - Plug in AURGA and power on the Aiffro
        - Wait for AURGA LED to turn from red to amber
    - Connect to AURGA via WiFi and open the viewer app
        - On the viewer Welcome screen click "Skip Sign In"
    - Click on the auto-detected AURGA-XXXXXX device, you should now see the HDMI output (LED should turn solid green)
    - The BIOS should be displayed
        - If not sent Ctrl+Alt+Del via the AURGA right click menu, then choose Input -> Absolute Mouse, then press ESC until you're in the BIOS
2. **BIOS Settings:**
    - **Insert Adapter Auto Power On**: Enabled

### 1.4.0 Boot to Installer

1. Power off the Aiffro
1. Do not plug in the **OS drive** yet
1. Plug in AURGA, the **USB installer drive**, and power cable
1. Connect to AURGA
1. Installer should have booted up
1. Plug in the **OS drive**

### 1.5.0 Install TrueNAS

Once the installer has booted up the following should be true:

- `/dev/sda` is the **USB installer drive**
- `/dev/sdb` is the **OS drive**
- `/dev/nvme?n1` are the four storage NVMe devices

Install TrueNAS SCALE with the following options:

- **Console setup**: Install/Upgrade
- **Destination media**: sdb
- **Authentication method**: Administrative user (truenas_admin)
- **Password**: *type in a simple password for now, you can choose a stronger password in the web UI after installation*

After installation is complete select **Shutdown System** and unplug the **USB installer drive** after it powered down.

---

## 2.0.0 Configure TrueNAS

This section will cover all relevant TrueNAS settings and Samba shares.

### 2.1.0 Console Setup

Power on the Aiffro and wait for the TrueNAS console setup menu to appear:

1. **Configure network interfaces:**
    - enp2s0 > Edit
        - **ipv4_dhcp**: No
        - **ipv6_auto**: No
        - **aliases**: 192.168.27.1/24

```{note}
When password console is enabled run `sudo cli_console` to get to this menu. To exit you have to start a Linux shell and then
`killall cli_console`.
```

### 2.2.0 Web UI General Config

Remember to set your laptop/workstation to a static IP address within the same subnet as the NAS.

1. Network > Global Configuration > Settings
    1. **Hostname**: anas
1. Credentials > Users > truenas_admin > Edit
    1. *Change password*
1. System > General Settings > Localization > Settings
    1. **Timezone**: *current time zone*
    1. **Time Format**: dd:dd:dd AM
1. System > Advanced Settings > Console > Configure
    1. **Show Text Console without Password Prompt**: Uncheck
1. System > Services > SMB > Edit
    1. **NetBIOS Name**: anas
    1. **Description**: AiffroNAS
    1. Advanced Options
        1. **Enable Apple SMB2/3 Protocol Extensions**: Check
    1. Save
    1. Start the service and enable on boot
1. System > Services > SSH > Edit
    1. **Password Login Groups**: truenas_admin
    1. **Allow TCP Port Forwarding**: Check
    1. Save
    1. Start the service

### 2.3.0 Synchronizing Time

Because the NAS is permanently offline, NTP services do nothing and the clock will inevitably drift. Here is a workaround
solution using Google as the time source over an SSH reverse proxy. Your laptop/workstation must be connected to the internet
over WiFi and simultaneously be connected to the NAS over wired ethernet.

```bash
# On your laptop/workstation:
ssh -R 8443:google.com:443 truenas_admin@192.168.27.1

# Run three times for sudo password prompt time delay
curl -sI --connect-to google.com:443:localhost:8443 https://google.com |grep -Pom1 "^date: \K.*" |xargs -I{} sudo date -s "{}"

# Finally update the hardware clock
sudo /sbin/hwclock -w
```

You'll need to repeat this step periodically, about once a month.

### 2.4.0 Setup Storage

The NAS will use a regular key-encrypted pool with a passphrase-encrypted "top" dataset under which all other datasets will
reside with inherited encryption.

Because NVMe SSDs don't fail as often as mechanical hard drives, we'll be using RAIDZ1. The Aiffro only has four NVMe slots
after all.

#### 2.4.1 Create Pool

Storage > Create Pool

1. **Name**: Vault
1. **Encryption**: Check
1. **Layout**: RAIDZ1
1. Manual Disk Selection
    1. Add (creates one RAIDZ1)
    1. Drag all drives from left to RAIDZ1
    1. Save Selection
1. Save And Go To Review > Create Pool
1. Download encryption key and store in 1Password

#### 2.4.2 Create Top Dataset

Datasets > Add Dataset

1. **Name**: Lockbox
1. **Inherit (encrypted)**: Uncheck
1. **Encryption Type**: Passphrase

### 2.5.0 Scrubbing and Snapshots

Scrubbing will be done every 60 days and snapshots will be taken every night at 5 AM. Because this is a **portable NAS** it
may not be powered on at that time. The workaround is to add a shutdown script to create snapshots on poweroff.

#### 2.5.1 Scrub Task

Data Protection > Scrub Tasks > Vault (click to edit)

1. **Threshold Days**: 60
1. **Schedule**: Hourly

#### 2.5.2 Snapshot Task

Data Protection > Periodic Snapshot Tasks > Add

1. **Dataset**: Vault
1. **Snapshot Lifetime**: 24 MONTH
1. **Recursive**: Check
1. **Schedule**: Custom
    1. **Presets**: Daily
    1. **Hours**: 5

#### 2.5.3 Snapshot on Shutdown

System > Advanced Settings > Init/Shutdown Scripts

```bash
# Description: Snapshot on Shutdown

# Command:
cli -c 'storage snapshot create dataset="Vault" naming_schema="shutdown-%Y-%m-%d_%H-%M" recursive=true'

# When: Shutdown
```

### 2.6.0 Samba Shares and Datasets

Each user will have a "main" share and a Temporary share, which will be excluded from backups. Below are the steps for the
user "Robpol86".

#### 2.6.1 Add User Account

Credentials > Users > Add

1. **Full Name**: Robpol86

#### 2.6.2 Add User Dataset

Datasets > Vault/Lockbox > Add Dataset

1. **Name**: Robpol86
1. **Dataset Preset**: SMB
1. **Create SMB Share**: Uncheck

#### 2.6.3 Add Leaf Datasets

Datasets > Vault/Lockbox/Robpol86 > Add Dataset

1. **Name**: Robpol86
1. **Dataset Preset**: SMB
1. Save > Return to Pool List
1. *Repeat for Name:TemporaryR*

#### 2.6.4 Update Samba Shares

Shares > SMB > *Name* > Edit

1. **Purpose**: No presets
1. Advanced Options
    1. **Access Based Share Enumeration**: Check
    1. **Export Recycle Bin**: Check
1. Save
1. Repeat for all
1. Edit **Share** ACL for each:
    1. **Who**: User
    1. **User**: robpol86

---

## 3.0.0 Backup Procedure

This section will cover backing up non-temporary datasets to a USB hard drive.

### 3.1.0 Activate Pool

Hot plug the USB backup drive and wait **15 seconds**.

1. If it's a new drive create a new pool
    1. Storage > Create Pool
    1. **Name**: Backup-YYYY-MM-DD
    1. **Encryption**: *leave unchecked*
    1. **Layout**: Stripe
    1. Save and Go To Review > Create Pool
1. If it's an old drive import the pool
    1. Storage > Import Pool
    1. **Pool**: *select Backup-YYYY-MM-DD|...*

### 3.2.0 Create and Run Task

Data Protection > Replication Tasks > Add

1. What and Where
    1. **Source/Destination Location**: On this System
    1. **Source**: check `Lockbox` and all child datasets except `Temporary*`
    1. **Destination**: Backup-YYYY-MM-DD/Lockbox (manually type `/Lockbox`)
    1. **Encryption**: *leave unchecked*
    1. **Recursive**: *leave unchecked*
    1. **Replicate Custom Snapshots**: Check
    1. **Snapshot Name Regular Expression**: `.*`
    1. Next
1. When
    1. **Replication Schedule**: Run Once
    1. Save (replication will start immediately)
1. Monitor IO with: `watch -c -d "S_COLORS=always iostat -m -y /dev/sdb 1 1"`

### 3.3.0 Export Backup Pool

When done export the pool and eject the drive. The replication task will be automatically deleted.

1. Visit Jobs History to confirm replication.run task succeeded and confirm elapsed time is sane
1. Storage > Backup-YYYY-MM-DD
    1. Note space usage, confirm it's not 0
    1. Export/Disconnect
    1. **Delete saved configurations from TrueNAS**: *leave checked*
    1. If middleware and other processes are using this pool either wait or reboot

### 3.4.0 Save Configuration

Save TrueNAS configuration to 1Password in case of failed boot-pool scenario.

System > General Settings > Manage Configuration > Download File

1. **Export Password Secret Seed**: Check

---

## 4.0.0 Disaster Recovery

This section will cover known disaster events and their recovery steps.

### 4.1.0 Failed Boot Pool

Steps to restore the pool from original storage SSDs. In this scenario I lose the boot SSD but not my storage SSDs.

1. Reinstall TrueNAS
    1. Stop before the "General Configuration" section
1. System > General Settings > Manage Configuration > Upload File
    1. Wait for automatic reboot
1. Confirm everything looks good

### 4.2.0 Replace Storage Device

Steps for replacing failed or failing storage SSDs. You'll need another USB-C to NVMe adapter (do not use the adapter used by
the **OS drive**).

#### 4.2.1 Validate New SSD

Power off and move the failed drive to a USB-C NVMe adapter and install the new drive in the now-open M.2 slot. Boot the
system and then:

```bash
scp ./f3probe truenas_admin@10.96.96.96:~
ssh truenas_admin@10.96.96.96

# New drive
sudo smartctl -a /dev/nvmeXn1
sudo smartctl -x /dev/nvmeXn1
sudo fdisk -l /dev/nvmeXn1

cp ~/f3probe /dev/shm/
sudo /dev/shm/f3probe --destructive --time-ops /dev/nvmeXn1
```

#### 4.2.2 Replace

Storage > Topology > Manage Devices > RAIDZ1

1. Select the device to be replaced (old drive, e.g. sdb)
1. **Replace** > Member Disk: *new drive's name* > Replace Disk
    1. If an error occurs reboot and try again
1. View the resilvering process in the upper right animated 🔄️ icon

#### 4.2.3 Wipe Old Drive

Storage > Disks

Verify old drive Pool column is **N/A**

```bash
sudo nvme format -s2 /dev/nvmeXn1  # if it fails try -s1
sudo blkdiscard /dev/nvmeXn1
```

Run `sudo smartctl -a /dev/nvmeXn1` on the old drive for RMA purposes

#### 4.2.4 Expand

Storage > Vault > Expand

1. After replacing smaller drives with larger ones click this to enable the new free space

### 4.3.0 Restore from Backup

Steps to restore the pool from a backup. In this scenario I lose my NAS but I still have access to a backup HDD.

#### 4.3.1 Prepare System

1. Reinstall TrueNAS
    1. Stop before the "General Configuration" section
1. System > General Settings > Manage Configuration > Upload File
    1. Wait for automatic reboot
1. Ensure SSDs are all wiped
1. Storage > Vault > Export/Disconnect
    1. **Delete saved configurations from TrueNAS**: Uncheck
1. Create pool but no datasets

#### 4.3.2 Restore

1. Insert backup HDD
1. Storage > Import Pool > "Backup-XXXX"
1. Data Protection > Replication Tasks > Add
    1. **Source/Destination Location**: On this System
    1. **Source**: check `Lockbox` only
    1. **Destination**: Vault/Lockbox (manually type `/Lockbox`)
    1. **Encryption**: *leave unchecked*
    1. **Recursive**: Check
    1. **Replicate Custom Snapshots**: Check
    1. **Snapshot Name Regular Expression**: `.*`
    1. Next
    1. **Replication Schedule**: Run Once
    1. **Make Destination Dataset Read-only**: Uncheck
    1. **Destination Snapshot Lifetime** Same as Source
    1. Save (replication will start immediately)
1. Export and remove backup HDD

#### 4.3.3 Final Steps

1. Unlock Lockbox and all child datasets
1. Datasets > Vault/Lockbox/Robpol86 > ZFS Encryption > Edit
    1. **Inherit encryption properties from parent**: Check
    1. *Repeat for all other child datasets*
1. Datasets > Vault/Lockbox > Dataset Details > Edit > Advanced Options
    1. **Read-only**: Inherit
    1. *Repeat for all other child datasets*
    1. NOTE: If you get user/group quota errors try rebooting
1. System > Shell > `rmdir -v /mnt/Vault/Lockbox/*/Temporary*`
1. Create `Temporary*` datasets
1. Reapply SMB ACLs
1. Reboot
1. Run through runbooks again to confirm settings

---

## 5.0.0 Troubleshooting Playbook

Common or occasional issues and their solutions. Includes notes if the issue resolved itself (which is never a good thing
because the root cause is not fixed and the issue may reoccur).

### 5.1.0 Invalid argument during seek

I got this error when creating a pool on a single drive:

```
Error: Invalid argument during seek for write on /dev/sdh
```

Happened even when I removed one drive and installed another.

#### 5.1.1 Solution

Solution was to reboot.

### 5.2.0 Checksum Error: 1

This happened when the NVMe SSDs dissappeared on boot. This happened the first time I installed the four WD Black SSDs back
in late December 2024, all four were missing from `/dev`. A power cycle fixed it that time.

It appeared to have happened again. On February 8th 2025 on boot my main pool was missing. In my haste I didn't check if any
SSD was in `/dev`. I powercycled (gracefully) the Aiffro and only three SSDs showed up in the UI's Disks section. A second
powercycle restored the fourth SSD but the TrueNAS UI showwed the ZFS Pool with an error (yet its state was Online).

In the Dashboard screen it said Disks with Errors: 1. In `/ui/storage/1/devices/` one of the devices showed 1 checksum error.
I put off fixing the issue for the next day and used the NAS like normal and powered it off at night. The next morning the
error was gone and everything was healthy with no manual intervention.

#### 5.2.1 Solution

Solution was to power cycle multiple times.

---
