---
blogpost: true
date: 2025-02-10
author: Robpol86
location: Santiago
category: Tutorials
tags: homelab, runbook
---

# TrueNAS SCALE Aiffro Runbook

This is my runbook for setting up and maintaining [TrueNAS SCALE](https://www.truenas.com/truenas-scale/) on my
[Aiffro K100](https://www.aiffro.com/products/all-ssd-nas-k100).

However this isn't any ordinary NAS. At this time I'm traveling around the world and brining my data with me. Because of this
my NAS frequently is powered down and has no direct access to the internet. This runbook has mitigations for the lack of 24/7
uptime when it comes to scheduled tasks, as well as workarounds for the lack of internet (it's configured with a static IP
and so is the network adapter on my laptop).

---

## 1.0.0 Installation Procedure

This section will go over listing the prerequisites, preparing the installation media, and installing the OS onto the Aiffro.
Avoid using the USB-A ports on the Aiffro since they're limited to USB 2.0 speeds.

### 1.1.0 Prerequisites

- Aiffro K100
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

### 1.5.0 Install TrueNAS SCALE

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

## 2.0.0 Configure TrueNAS SCALE

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

# Run three times for sudo password prompt time overhead:
curl -sI --connect-to google.com:443:localhost:8443 https://google.com |grep -Pom1 "^date: \K.*" |xargs -I{} sudo date -s "{}"

# Finally update the hardware clock
sudo /sbin/hwclock -w
```

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

TODO

---

## 3.0.0 Backup Procedure

### 3.1.0 Recommended Backup Strategy

- **System Configuration Backup:**
    - Go to System Settings → General → Save Config.
    - Store it in a safe location (offsite/cloud).
- **Data Backup Options:**
    - Use built-in TrueNAS replication tasks for ZFS snapshots.
    - Set up periodic Rsync jobs to an external storage device.
    - Cloud sync to AWS, Backblaze, or other providers.
- **Automate Backups:**
    - Configure scheduled snapshots (Storage → Snapshots → Add).
    - Set up automated replication (Storage → Replication Tasks).

---

## 4.0.0 Disaster Recovery

### 4.1.0 Identifying a Failed Drive

- Check alerts in the Web UI.
- Run `zpool status` via SSH to see degraded pools.

### 4.2.0 Replacement Procedure

1. **Offline the Failed Drive:**
    - `zpool offline <poolname> <device>`
2. **Physically Replace the Drive:**
    - Ensure the new drive has the same or larger capacity.
    - Insert the new drive and verify it is detected (`lsblk` or `dmesg`).
3. **Attach the New Drive:**
    - `zpool replace <poolname> <old_device> <new_device>`
4. **Verify Resilvering:**
    - Run `zpool status` to monitor progress.
    - Once complete, pool should return to "ONLINE" status.

---

## 5.0.0 Troubleshooting Playbook

### 5.1.0 Common Issues and Resolutions

#### 5.1.1 Issue: TrueNAS Web UI is Not Accessible

**Symptoms:** Unable to access the TrueNAS web UI at the expected IP address.

**Troubleshooting Steps:**
1. Verify the server is powered on.
2. Check network connectivity:
   - Run `ping <truenas-ip>` from another device.
   - Ensure the correct IP address is being used.
3. Restart the TrueNAS networking service:
   - Run `systemctl restart networking` via SSH.
4. If using a static IP, confirm correct settings:
   - `ifconfig` or `ip a` to verify assigned IP.
   - Update settings in `System Settings → Network`.
5. Reboot the system as a last resort.

#### 5.1.2 Issue: Pool is Degraded

**Symptoms:** Alerts indicate a degraded pool, possible disk failure.

**Troubleshooting Steps:**
1. Check `zpool status` for the failed drive.
2. Attempt a manual `zpool scrub <poolname>`.
3. If drive failure is confirmed, follow Section 3.0.0 for drive replacement.
4. If issue persists, consult logs with `dmesg | grep ZFS`.

#### 5.1.3 Issue: SMB/CIFS Shares Not Working

**Symptoms:** Network shares are inaccessible.

**Troubleshooting Steps:**
1. Verify `smbd` and `nmbd` services are running:
   - `systemctl status smbd nmbd`
   - Restart if needed: `systemctl restart smbd nmbd`
2. Check share permissions in `Sharing → SMB`.
3. Ensure user permissions match configured share access.
4. Reboot the NAS if necessary.

#### 5.1.4 Issue: High CPU or Memory Usage

**Symptoms:** TrueNAS is slow or unresponsive.

**Troubleshooting Steps:**
1. Check system load:
   - `top` or `htop` to view resource usage.
2. Identify high-resource services:
   - `ps aux --sort=-%cpu` or `ps aux --sort=-%mem`
3. Restart problematic services if necessary.
4. Review logs in `/var/log/` for anomalies.

#### 5.1.5 Issue: No Internet Access from TrueNAS

**Symptoms:** Unable to update or access remote repositories.

**Troubleshooting Steps:**
1. Verify network settings:
   - `ip a` and `ip route`
2. Check DNS configuration:
   - Ensure `/etc/resolv.conf` contains valid nameservers.
3. Test external connectivity:
   - `ping 8.8.8.8`
   - `curl -I https://www.google.com`
4. Restart networking service: `systemctl restart networking`
