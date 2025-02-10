---
blogpost: true
date: 2025-02-10
author: Robpol86
location: Santiago
category: Tutorials
tags: homelab, runbook
---

# TrueNAS SCALE Aiffro Runbook

```{imgur-image} a9XxG0G
```

This is my runbook for setting up and maintaining [TrueNAS SCALE](https://www.truenas.com/truenas-scale/) on my
[Aiffro K100](https://www.aiffro.com/products/all-ssd-nas-k100) portable NAS.

## 1. Installation Procedure

### Prerequisites:

- A compatible system (64-bit CPU, 8GB+ RAM recommended)
- At least one dedicated boot drive (SSD preferred)
- Storage drives for data (ZFS recommended)
- USB drive (8GB+ for installation media)
- A backup of any existing data

### Steps:

1. **Download TrueNAS SCALE ISO:**
   - Get the latest ISO from [truenas.com](https://www.truenas.com/)
2. **Create Bootable USB:**
   - Use Rufus (Windows) or `dd` (Linux/macOS) to write the ISO.
   - Example command: `dd if=truenas-scale.iso of=/dev/sdX bs=4M status=progress`
3. **Boot From USB:**
   - Enter BIOS and set USB as the primary boot device.
   - Select "Install TrueNAS SCALE."
4. **Installation Steps:**
   - Choose the boot device.
   - Configure network settings if needed.
   - Set root password.
   - Reboot and remove installation media.
5. **Initial Configuration:**
   - Access TrueNAS Web UI at `http://<your-ip>`.
   - Complete initial setup (storage pools, network, users, etc.).

---

## 2. Backup Procedure

### Recommended Backup Strategy:

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

## 3. Replacing a Failed Drive

### Identifying a Failed Drive:

- Check alerts in the Web UI.
- Run `zpool status` via SSH to see degraded pools.

### Replacement Procedure:
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

## 4. Troubleshooting (Placeholder)

_This section is under development. Common issues and solutions will be documented here._
