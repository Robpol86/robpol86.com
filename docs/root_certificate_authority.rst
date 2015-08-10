.. _root_certificate_authority:

=========================
Setting Up a Home Root CA
=========================

.. warning::
    This guide is incomplete! I'm still writing it.

Tired of getting those SSL error pages when accessing your router's admin interface? Sick of having to click three times
to get to your IPMI web interface? Have I got a guide for you!

This guide will go over setting up an offline root certificate authority for your home network. It is based on what I
learned from https://jamielinux.com/docs/openssl-certificate-authority/create-the-root-pair.html with a few changes:

1. This guide will include steps on setting up the root CA on a Raspberry Pi, though it should really work on any linux
   computer.
2. I will not be creating an intermediate pair here. Since my intentions are just setting up SSL certs on a handful of
   internal web interfaces and maybe even WPA2 Enterprise one day, I didn't think it was worth setting this up. It might
   make revoking certs not as quick, but I don't see myself signing very many certs after my initial run.

The goal here is to setup an offline root CA. It will be online at first to get updates (this is optional) but right
before generating the root pair we will remove any network connectivity from the host and never EVER connect it to any
networks or USB devices. This will be an offline and air gapped root CA.

Preparing the Raspberry Pi
==========================

If you aren't using a Raspberry Pi for your root CA (perhaps you're using a Chromebook or an old Linux laptop) you can
safely skip this section. The gist of this section is I'll be setting up LUKS full disk encryption. You'll need to
install OpenSSL and ``qrencode`` (for transmitting keys over the air gap).

1. Install Raspbian and boot up the Raspberry Pi. It's ok to have network access for now. If you have internet access go
   ahead and ``sudo apt-get update && sudo apt-get upgrade``. I followed
   `Raspbian Setup (Raspberry Pi) <https://gist.github.com/Robpol86/3d4730818816f866452e>`_ (you don't need to install
   any additional packages in this step, just upgrade).
2. Install required packages: ``sudo apt-get install busybox cryptsetup pv qrencode``

Full Disk Encryption
--------------------

I got most of these steps from: http://paxswill.com/blog/2013/11/04/encrypted-raspberry-pi/#. You'll need a Linux
computer (or a VM that can mount an SD card using a USB adapter) to perform the initial encryption since the Raspbian
can't encrypt itself.

On the Raspberry Pi:

1. ``sudo mkinitramfs -o /boot/initramfs.gz``
2. Append ``initramfs initramfs.gz followkernel`` to ``/boot/config.txt``.

Now shut down the Raspberry Pi and mount the SD card on another Linux computer. Run these commands on that computer
(``/dev/sdb2`` here is the SD card's OS partition). The ``luksFormat`` command will nuke your SD card and it will also
be asking you for a LUKS password. Make sure it's a long password with lots of special characters.

.. code-block:: bash

    sudo dd if=/dev/sdb2 bs=4M |pv |dd of=/tmp/raspbian-plain.img  # Dumps data to file.
    e2fsck -f /tmp/raspbian-plain.img  # Check the dump file.
    resize2fs -M /tmp/raspbian-plain.img  # Shrink the dump file to save time.
    sudo cryptsetup -v -y --cipher aes-cbc-essiv:sha256 --key-size 256 luksFormat /dev/sdb2
    sudo cryptsetup -v luksOpen /dev/sdb2 sdcard  # Mount empty encrypted partition.
    dd if=/tmp/raspbian-plain.img |pv |sudo dd of=/dev/mapper/sdcard bs=4M  # Restore data.
    sudo e2fsck /dev/mapper/sdcard  # Check the encrypted SD card partition.
    sudo resize2fs /dev/mapper/sdcard  # Expand back to full size.
    mkdir /tmp/pi_root /tmp/pi_boot  # Use these to finish setting up LUKS.
    sudo mount /dev/sdb1 /tmp/pi_boot
    sudo mount /dev/mapper/sdcard /tmp/pi_root

We still need to setup the last steps that allows the Raspberry Pi to mount encrypted partitions. Run these steps on the
Linux computer:

1. In ``/tmp/pi_boot/cmdline.txt`` change ``root=/dev/mmcblk0p2`` to ``root=/dev/mapper/sdcard`` and append
   ``cryptdevice=/dev/mmcblk0p2:sdcard`` to the end of the file.
2. In ``/tmp/pi_root/etc/fstab`` change ``/dev/mmcblk0p2`` to ``/dev/mapper/sdcard``.
3. In ``/tmp/pi_root/etc/crypttab`` append ``sdcard  /dev/mmcblk0p2  none    luks`` to the end of the file.

Now go ahead and unmount the SD card and put it back in the Raspberry Pi:

1. ``sudo umount /tmp/pi_boot /tmp/pi_root``
2. ``sudo cryptsetup luksClose sdcard``

When you try to boot the Raspberry Pi it will fail and drop to the ``initramfs`` prompt. This will happen every time
from now on. When you get the prompt you'll be running:

* ``cryptsetup luksOpen /dev/mmcblk0p2 sdcard``

After putting in your LUKS password just exit and it will keep booting like usual.
