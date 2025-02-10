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
[Aiffro K100](https://www.aiffro.com/products/all-ssd-nas-k100) portable NAS.

---

## 1.0.0 Installation Procedure

This section will go over listing the prerequisites, preparing the installation media, and installing the OS onto the Aiffro.
I avoid using the USB-A ports on the Aiffro since they're limited to USB 2.0 speeds.

### 1.1.0 Prerequisites

- Aiffro K100
- **Two** USB drives:
    - One for the TrueNAS installer at least 2 GiB in capacity
    - Another as the USB boot pool at least 16 GiB in capacity (I use a 2230 M.2 NVMe to USB-C adapter with an SSD)
- Four NVMe SSDs for storage
- An [AURGA Viewer](https://www.aurga.com/products/aurga-viewer)
    - You can also use a regular USB keyboard and HDMI display, however this runbook is written with the AURGA in mind since
      that's what I bring with me whilst traveling.

### 1.2.0 Prepare USB Installer

1. **Download TrueNAS SCALE ISO:**
    - Get the latest **stable** ISO from https://www.truenas.com/download-truenas-scale/
2. **Create Bootable USB:**
    - Plug installer USB drive into your laptop/workstation
    - If you're using Windows:
        - Use [Rufus](https://rufus.ie/en/) in `dd` mode (it will prompt you when you click START)
    - If you're using macOS or Linux:
        - Find the device name of the USB drive (using Disk Utility on macOS or looking in `/dev` on Linux) e.g. `disk6` or `sdb`.
        - Run in Terminal: `sudo dd if=TrueNAS-SCALE-24.10.1.iso of=/dev/disk6`

### 1.3.0 Boot to Installer

TODO

1. Do not plug in USB-C SSD yet
1. Plug in AURGA, USB-C installer, and power
    1. Wait for AURGA LED to turn from red to amber
1. Connect to AURGA via WiFi and open viewer
    1. On the viewer Welcome screen click **Skip for now**
1. Click **Search Now** and then click **Connect** under "Devices", you should now see the HDMI output (LED should turn solid green)
1. Installer should have booted up
1. Plug in USB-C SSD
1. NOTE: AURGA will not apply a keypress until the SHIFT key is released, so don't hold it for consecutive caps

---

## 2.0.0 Backup Procedure

### 2.1.0 Recommended Backup Strategy

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

## 3.0.0 Replacing a Failed Drive

### 3.1.0 Identifying a Failed Drive

- Check alerts in the Web UI.
- Run `zpool status` via SSH to see degraded pools.

### 3.2.0 Replacement Procedure

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

## 4.0.0 Troubleshooting (Placeholder)

_This section is under development. Common issues and solutions will be documented here._
