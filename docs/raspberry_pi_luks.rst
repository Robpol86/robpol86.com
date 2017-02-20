.. _raspberry_pi_luks:

=================================
Raspberry Pi LUKS Root Encryption
=================================

In this short guide I'll go over how I implemented full disk encryption using LUKS on my Raspberry Pi's root file system
**without needing a second Linux computer** to run commands on. All you need is your Raspberry Pi running Raspbian and a
USB flash drive.

An overview of the process:

1. Install software on your Raspberry Pi's Raspbian OS.
2. Build a custom and boot into the `initramfs <https://pi-ltsp.net/advanced/kernels.html#initramfs>`_.
3. Shrink your main file system.
4. Back up your main file system from the SD card to the USB drive.
5. Wipe SD card and create an empty encrypted partition.
6. Copy back your backed-up file system from USB on to your encrypted SD card.

.. warning::

    This guide involves backing up your data to a USB drive and destroying all data on your SD card. Though slim there
    is a possibility of failure. Be sure to have **proper backups of your Raspberry Pi** in case something goes wrong.
    Also note that **all data on your USB drive will be destroyed** during the process since it will temporarily hold
    all of your Raspberry Pi's data.

At the time of this writing I've tested this guide against *2017-01-11-raspbian-jessie.zip* and
*2017-01-11-raspbian-jessie-lite.zip* on a *Raspberry Pi 3 Model B V1.2* and a *Raspberry Pi Zero V1.3*.

Install Software
================

We'll begin by installing software and creating a new initramfs for your Raspberry Pi. This new initramfs will have the
``cryptsetup`` program needed to unlock the encrypted partition on every boot. We'll also include other tools to assist
in the initial encryption of your existing data.

First install some software:

.. code-block:: bash

    sudo apt-get install busybox cryptsetup initramfs-tools

Next we'll need to add a kernel post-install script. Since Raspbian doesn't normally use an initrd/initramfs it doesn't
auto-update the one we're about to create when a new kernel version comes out. Our initramfs holds kernel modules since
they're needed before the encrypted root file system can be mounted. When the kernel version changes it won't be able to
find its new modules. To fix this write the following to ``/etc/kernel/postinst.d/initramfs-rebuild``:

.. literalinclude:: _static/initramfs-rebuild.sh
    :language: bash

Now we want ``resize2fs`` and ``fdisk`` to be included in our initramfs so we'll need to create a hook file. Write the
following to ``/etc/initramfs-tools/hooks/resize2fs``:

.. literalinclude:: _static/resize2fs.sh
    :language: bash

.. note::

    Raspbian ships with two Linux kernels: one for the Raspberry Pi 1 (including Pi Zero), and another for the Raspberry
    Pi 2 and 3. In order to keep the ability of using one SD card on all Raspberry Pis the above script will include the
    other kernel's modules (the current kernel's modules are the only ones included by default). This will double the
    size of the ``initramfs.gz`` file. If you don't plan on using this SD card on a different Raspberry Pi you can set
    ``COMPATIBILITY`` to ``false`` and re-run ``mkinitramfs`` below.

Finally let's build the new initramfs and make sure our utilities have been installed. The ``mkinitramfs`` command may
print some WARNINGs from cryptsetup, but that should be fine since we're using ``CRYPTSETUP=y``. As long as cryptsetup
itself is present in the initramfs it won't be a problem.

.. code-block:: bash

    sudo chmod +x /etc/kernel/postinst.d/initramfs-rebuild
    sudo chmod +x /etc/initramfs-tools/hooks/resize2fs
    sudo -E CRYPTSETUP=y mkinitramfs -o /boot/initramfs.gz
    lsinitramfs /boot/initramfs.gz |grep -P "sbin/(cryptsetup|resize2fs|fdisk)"

Make sure you see ``sbin/resize2fs``, ``sbin/cryptsetup``, and ``sbin/fdisk`` in the output.

Prepare Boot Files
==================

Next step is to make some changes to some configuration files telling the Raspberry Pi to boot our soon-to-be-created
encrypted partition. We'll make these changes first since they're relatively easily reversible if you mount your SD card
on another computer, should you wish to abort this process. Edit these files with these changes:

.. describe:: /boot/config.txt

    Append ``initramfs initramfs.gz followkernel`` to the end of the file.

.. describe:: /boot/cmdline.txt

    1. Append ``cryptdevice=/dev/mmcblk0p2:sdcard`` to the end of the line.
    2. Replace ``root=/dev/mmcblk0p2`` with ``root=/dev/mapper/sdcard``

.. describe:: /etc/fstab

    Replace ``/dev/mmcblk0p2`` with ``/dev/mapper/sdcard``

.. describe:: /etc/crypttab

    Append ``sdcard  /dev/mmcblk0p2  none    luks`` to the end of the file.

Now run ``sudo reboot``. The Raspberry Pi will fail to boot and drop you into the initramfs shell.

Shrink and Encrypt
==================

To speed up this process we'll be shrinking the file system since all of this will be done on the Raspberry Pi. Long
running commands should take around 9 minutes each on a Raspberry Pi 3 with a clean Raspbian PIXEL OS and a fast SD
card.

.. note::

    When running ``resize2fs`` it will print out the new size of the file system. Keep track of the number of 4k blocks
    it tells you since you need to give that number to ``dd``. For reference my resize2fs said:

    .. code-block:: text

        The file system on /dev/mmcblk0p2 is now 1397823 (4k) blocks long.

    So "1397823" is my number of interest.

First we'll shrink and copy to the USB drive. **Insert your USB drive** and run these commands.

.. code-block:: bash

    e2fsck -f /dev/mmcblk0p2  # Check SD card for errors for safety.
    resize2fs -fM /dev/mmcblk0p2  # Shrink the file system on the SD card.
    # Write down the number of 4k blocks long in the resize2fs output.
    # Substitute "1397823" below with your number of interest.
    dd bs=4k count=1397823 if=/dev/mmcblk0p2 |sha1sum # Write down the SHA1.
    fdisk -l /dev/sda  # Make sure /dev/sda is your USB drive. If not check dmesg.
    dd bs=4k count=1397823 if=/dev/mmcblk0p2 of=/dev/sda  # Copy data to USB drive.
    dd bs=4k count=1397823 if=/dev/sda |sha1sum # Make sure it's the same value!

Now it's time to wipe your SD card's main partition and create an empty encrypted one in its place. The first
``cryptsetup`` command will prompt you for the password you want to use for your encrypted partition. Make sure it's a
strong one.

.. note::

    While copying data back to the SD card I got a bunch of these messages:

    .. code-block:: text

        [ 2280.148837] INFO: task kworker/u8:5:357 blocked for more than 120 seconds.
                             Not tainted 4.4.38-v7+ #938

    I ignored these since the ``sha1sum`` command I ran afterward assured me the data was copied over correctly.

.. code-block:: bash

    cryptsetup --cipher aes-cbc-essiv:sha256 luksFormat /dev/mmcblk0p2
    cryptsetup luksOpen /dev/mmcblk0p2 sdcard  # Mounts the encrypted file system.
    dd bs=4k count=1397823 if=/dev/sda of=/dev/mapper/sdcard # Copy back your data.
    dd bs=4k count=1397823 if=/dev/mapper/sdcard |sha1sum # Make sure it's the same!
    e2fsck -f /dev/mapper/sdcard  # Check encrypted SD card for errors.
    resize2fs -f /dev/mapper/sdcard  # Expand back to full size.
    # Remove USB drive, no longer needed.
    exit  # Continue to boot into your encrypted SD card.

Your Raspberry Pi should successfully boot into your desktop or command line (depending if you use Raspbian Lite or
PIXEL). Test everything out by rebooting. You'll need to run ``cryptsetup luksOpen /dev/mmcblk0p2 sdcard`` on every boot
from now on.

Pretty Password Prompt
======================

Everything should work fine now, except for the fact that every time the Raspberry Pi boots it drops you into the
initramfs shell and you need to remember to type in the luksOpen command since there is no bash history. It would be
nice to just have to enter your password.

It's actually really easy! The only drawback is that you'll need to disable the pretty PIXEL splash screen (if you're
not using the Raspbian Lite image) in order to see the prompt. If you're on the PIXEL image go ahead and disable the
splash screen:

.. describe:: /boot/cmdline.txt

    If you're on the PIXEL image edit this file and remove ``splash`` from the line.

Now build a new initramfs. This time there should be no WARNINGs at all. Again make sure our three programs are present
in our new initramfs:

.. code-block:: bash

    sudo mkinitramfs -o /tmp/initramfs.gz
    lsinitramfs /tmp/initramfs.gz |grep -P "sbin/(cryptsetup|resize2fs|fdisk)"
    sudo cp /tmp/initramfs.gz /boot/initramfs.gz
    sudo reboot

And that's it. It should prompt you with something like "Please unlock disk /dev/mmcblk0p2 (sdcard)". If you're running
Raspbian Lite the password prompt may be lost with other start-up messages. Just press the Enter key once it calms down
and you should see the prompt again.

References
==========

* http://paxswill.com/blog/2013/11/04/encrypted-raspberry-pi/
* https://github.com/NicoHood/NicoHood.github.io/wiki/Raspberry-Pi-Encrypt-Root-Partition-Tutorial

Comments
========

.. disqus::
