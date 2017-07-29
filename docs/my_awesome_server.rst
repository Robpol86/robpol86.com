.. _my_awesome_server:

=================
My Awesome Server
=================

.. tip::

    This page is still under development. I'll be changing it a lot as I perfect how I'll setup my new server before I
    "put it in production" in my home.

I've had home servers since I was in high school in 2002. However I've never documented how I set them up before. Here
I'll be outlining the steps I took in setting up my current home Linux server. It's a general purpose server, acting as:

#. A file server for all of my media/backups/etc.
#. Apple Time Machine backup server.
#. `Docker <https://www.docker.com/>`_ server.
#. `Metrics <https://robpol86.github.io/influxdb/>`_ collecting and email alerting.
#. `Plex <https://www.plex.tv/>`_ media server.
#. Automated Bluray/DVD ripping (backups) station.
#. TODO: Automated video file transcoder.
#. TODO: Audio/video file ID3/metadata validator.
#. TODO: Usenet/Torrent downloader.

Hardware
========

My server will be going inside my `TV stand/cabinet`_. It'll share a case with my `pfSense <https://pfsense.org/>`_
custom router and be on a `UPS`_.

=============== ===========================================================================================
Case            `Travla T2241`_ dual mini-ITX with `Seasonic 250 watt`_ power supplies
Motherboard/CPU `Supermicro X10SDV-TLN4F-O`_ with Xeon D-1541
Memory          Kingston KVR24R17D8K4/64 (64GB)
M.2 SSD         Samsung 960 PRO 512GB
Storage HDDs    6x Seagate 10TB IronWolf Pro (ST10000NE0004)
=============== ===========================================================================================

.. _TV stand/cabinet: https://www.standoutdesigns.com/products/media-console-solid-wood-majestic-ex-70-inch-wide
.. _UPS: http://www.apc.com/shop/us/en/products/APC-Smart-UPS-1500VA-LCD-RM-2U-120V/P-SMT1500RM2U
.. _Travla T2241: http://www.travla.com/business/index.php?id_product=49&controller=product
.. _Seasonic 250 watt: https://seasonic.com/product/ss-250-su-active-pfc-f0/
.. _Supermicro X10SDV-TLN4F-O: http://www.supermicro.com/products/motherboard/Xeon/D/X10SDV-TLN4F.cfm

Network
=======

This section describes my home network topology.

VLANs
-----

.. describe:: VLAN1: Default

    The default VLAN. Used for managing the switch.

.. describe:: VLAN2: General

    The general VLAN for my home network. Every normal device communicates through it. Includes normal internet traffic.
    DHCP served by my pfSense box.

.. describe:: VLAN3: Guest

    Only used by the guest WiFi SSID. In case neighbors need to borrow my internet they can use this network, which will
    be separate from my general network. DHCP served by my pfSense box.

.. describe:: VLAN5: WAN

    Internet traffic comes into this VLAN, along with my pfSense box. Instead of plugging it directly to my pfSense box
    both will plug into my switch but be on their own VLAN. Easier cable management and if I ever want to get a second
    internet line I can plug that into my switch.

Switchports
-----------

======= ============ ==================
Port    Device       VLAN
======= ============ ==================
1       pfSense      2 (3+5 tagged)
2       Server       2
3       UPS          2
4       Chromecast   2
5       WiFi AP      2 (2+3 tagged)
6       Desk         2
7       Mac Pro      2
8       *empty*      2
9       *empty*      2
10      *empty*      2
11      *empty*      1
12      *empty*      3
13      *empty*      2
14      *empty*      2
15      *empty*      2
16      Upstream     5
======= ============ ==================

Operating System
================

I'm using Fedora 26 Server installed on my M.2 SSD using `LUKS`_. I'll also be encrypting all of my non-SSD hard drives
using the same password since `Plymouth`_ on Fedora does password caching.

I follow https://gist.github.com/Robpol86/6226495 when setting up any Linux system, including my server. However I don't
setup my HDDs during setup, I leave them alone.

.. _LUKS: https://fedoraproject.org/wiki/Disk_Encryption_User_Guide
.. _Plymouth: https://en.wikipedia.org/wiki/Plymouth_(software)

Fixing ATA Errors
-----------------

I've been seeing these messages for all of my Seagate 10 TB drives periodically in ``dmesg``:

.. code-block:: text

    ata2.00: exception Emask 0x0 SAct 0x0 SErr 0x0 action 0x6 frozen
    ata2.00: failed command: FLUSH CACHE EXT
    ata2.00: cmd ea/00:00:00:00:00/00:00:00:00:00/a0 tag 16
             res 40/00:00:00:4f:c2/00:00:00:00:00/00 Emask 0x4 (timeout)
    ata2.00: status: { DRDY }
    ata2: hard resetting link
    ata2: SATA link up 6.0 Gbps (SStatus 133 SControl 300)
    ata2.00: configured for UDMA/133
    ata2.00: retrying FLUSH 0xea Emask 0x4
    ata2: EH complete

The only solution that worked for me was to disable `NCQ <https://en.wikipedia.org/wiki/Native_Command_Queuing>`_. I did
this by adding the `libata.force=noncq` kernel boot option:

.. code-block:: bash

    sudo vim /etc/default/grub
    # Append libata.force=noncq to GRUB_CMDLINE_LINUX.
    sudo grub2-mkconfig -o $(sudo find /boot -name grub.cfg)

Sending Email
-------------

I want my server to send email alerts to me when events happen (e.g. a disk fails). I did write a guide about this at
:ref:`postfix_gmail_forwarding`. However instead of using Gmail to send email I'm going with https://www.sparkpost.com/
since they have a free tier and I can send emails in scripts using simple HTTP requests. Also email templates are a nice
feature.

To setup run:

.. code-block:: bash

    sudo dnf install postfix mailx cyrus-sasl{,-plain}

Then edit ``/etc/postfix/main.cf`` with the following. Replace ``<API-KEY>`` and ``<SENDING-DOMAIN>``.

.. code-block:: ini

    smtp_sasl_auth_enable = yes
    smtp_sasl_password_maps = static:SMTP_Injection:<API-KEY>
    relayhost = [smtp.sparkpostmail.com]:587
    smtp_sasl_security_options = noanonymous
    smtp_tls_security_level = encrypt
    header_size_limit = 4096000
    myorigin = <SENDING-DOMAIN>.com
    mydestination = <SENDING-DOMAIN>.com $myhostname localhost.$mydomain localhost

Then run:

.. code-block:: bash

    sudo tee /etc/aliases <<< 'root: <YOU>@gmail.com'
    sudo newaliases
    sudo systemctl start postfix.service
    sudo systemctl enable postfix.service
    mail -s "Test Email $(date)" <YOU>@gmail.com <<< "This is a test email."
    mail -s "Test Email for Root $(date)" root <<< "This is a test email."

You should receive both emails in your personal email account. If not make sure the numbers in your SparkPost's
dashboard's usage report have increased.

LUKS and Btrfs
==============

Here is where I format my storage HDDs. I want to use Btrfs since ZFS isn't first-class on Fedora and I want
Copy-On-Write with snapshots for backing up.

I also want to use Btrfs for RAID10 (RAID5 is a bad idea with 6x10TB and RAID6 still stresses all drives when one fails,
vs RAID10 stressing just one other drive). Since encryption isn't supported by Btrfs at this time I need to use LUKS.
Since I want to use LUKS with Btrfs my only option is to LUKS the drives first and then use Btrfs RAID ontop of them.

Run the following to set LUKS up:

.. code-block:: bash

    sudo dnf install cryptsetup btrfs-progs
    (set -ex; for d in /dev/sd[a-f]; do
        name=storage_$(lsblk -dno SERIAL $d |grep . || basename $d)
        (! sudo grep -q "$name" /etc/crypttab)
        sudo fdisk -l $d |grep "Disk $d"
        sudo cryptsetup --cipher aes-cbc-essiv:sha256 luksFormat $d
        sudo tee -a /etc/crypttab <<< "$name UUID=$(lsblk -dno UUID $d) none"
    done)
    sudo systemctl daemon-reload && sudo systemctl restart cryptsetup.target

Make sure all disks are in ``/dev/mapper``.

Btrfs
-----

Now it's time to create the Btrfs partition on top of LUKS as well as Btrfs subvolumes (for future snapshotting):

.. code-block:: bash

    # Create the Btrfs top volume.
    sudo mkfs.btrfs -L storage -m raid10 -d raid10 /dev/mapper/storage_*
    uuid=$(sudo btrfs filesystem show storage |grep -Po '(?<=uuid: )[0-9a-f-]+$')
    sudo tee -a /etc/fstab <<< "UUID=$uuid /storage btrfs autodefrag 0 2"
    sudo mkdir /storage; sudo mount -a
    # Create subvolumes.
    for n in Local Main Media Old Stuff Temporary TimeMachine; do
        sudo btrfs subvolume create /storage/$n
    done

Reboot to make sure ``/storage`` is mounted.

Users and Permissions
---------------------

Then create users and chown directories. Users will need passwords defined so they'll work with Samba.

.. code-block:: bash

    # Users/groups.
    sudo groupadd shared
    sudo groupadd timemachine
    sudo useradd -M -s /sbin/nologin -p "$(openssl rand 32 |openssl passwd -1 -stdin)" printer
    sudo useradd -M -s /sbin/nologin -p "$(openssl rand 32 |openssl passwd -1 -stdin)" stuff
    sudo useradd -M -s /sbin/nologin media
    sudo usermod -a -G media,printer,shared,timemachine robpol86
    sudo usermod -a -G shared stuff
    # TimeMachine: multiple users can access. Their files readable only by them.
    sudo chgrp timemachine /storage/TimeMachine && sudo chmod 0770 $_
    sudo setfacl -d -m u::rwx -m g::- -m o::- /storage/TimeMachine
    # Shared: multiple users can access. Their files readable and writable by members.
    sudo mkdir -m 0770 /storage/Local/Shared && sudo chgrp shared $_
    sudo setfacl -d -m u::rwx -m g::rwx -m o::- /storage/Local/Shared
    # Printer: a place for my printer to drop scanned documents.
    sudo mkdir -m 0770 /storage/Local/Printer && sudo chown printer:printer $_
    sudo setfacl -d -m u::rwx -m g::rwx -m o::- /storage/Local/Printer
    # Media: a place for MakeMKV to write video files to and Plex to playback.
    sudo mkdir -m 0770 /storage/Local/MakeMKV && sudo chown media:media $_
    sudo setfacl -d -m u::rwx -m g::rwx -m o::- /storage/Local/MakeMKV
    sudo chown robpol86:media /storage/Media && sudo chmod 2750 $_
    # Others.
    sudo chown stuff:stuff /storage/Stuff
    sudo chown robpol86:robpol86 /storage/{Main,Old,Temporary}
    sudo chmod 0750 /storage/{Main,Old,Stuff,Temporary}
    sudo setfacl -d -m u::rwx -m g::rx -m o::- /storage/{Main,Media,Old,Stuff,Temporary}

Samba
=====

I'll have three Samba users on my server. Each user will have a separate password in Samba's database since things such
as printers may not store them 100% securely and I wouldn't want that to be an attack vector for my server (lifting the
password from the printer and then logging in and running sudo on my server).

Normally I'd then install Samba the usual way with dnf. However at this time support for Apple's Time Machine `isn't`_
yet `available`_. My workaround is to build a custom RPM with the ``F_FULLSYNC`` feature patched in until Samba
officially supports it.

.. code-block:: bash

    sudo dnf install @development-tools fedora-packager
    fedpkg co -ab f26 samba && cd $_
    fedpkg sources
    curl -L https://github.com/samba-team/samba/pull/64.patch -o samba-fullsync.patch
    # Edit samba.spec to add: Patch1: samba-fullsync.patch
    fedpkg prep
    sudo dnf builddep --spec samba.spec
    fedpkg local
    sudo dnf install noarch/samba-common-4.6.* \
        x86_64/{libwbclient,libsmbclient,samba{,-libs,-client,-client-libs,-common{-libs,-tools}}}-4.6.*

Next I'll install set Samba-specific passwords used by remote clients and configure SELinux (other Samba guides love to
disable SELinux or set ``samba_export_all_rw`` which is basically the same as disabling SELinux).

.. code-block:: bash

    sudo dnf install avahi policycoreutils-python-utils
    sudo smbpasswd -a printer && sudo smbpasswd -e $_
    sudo smbpasswd -a robpol86 && sudo smbpasswd -e $_
    sudo smbpasswd -a stuff && sudo smbpasswd -e $_
    sudo semanage fcontext -a -t samba_share_t /storage
    sudo semanage fcontext -a -t samba_share_t "/storage/(Main|Media|Old|Stuff|Temporary|TimeMachine)(/.*)?"
    sudo semanage fcontext -a -t samba_share_t "/storage/Local/(MakeMKV|Printer|Shared)(/.*)?"
    sudo restorecon -R -v /storage

Then write the following to ``/usr/local/bin/dfree_btrfs``:

.. literalinclude:: _static/dfree_btrfs.sh
    :language: bash

And write the following to ``/etc/avahi/services/timemachine.service``:

.. literalinclude:: _static/timemachine.service
    :language: bash

Now replace ``/etc/samba/smb.conf`` with:

.. literalinclude:: _static/smb.conf
    :language: ini

Finally run the following.

.. code-block:: bash

    sudo chmod +x /usr/local/bin/dfree_btrfs
    sudo firewall-cmd --permanent --add-service=samba
    sudo systemctl restart firewalld.service
    sudo systemctl start smb.service nmb.service avahi-daemon.service
    sudo systemctl enable smb.service nmb.service avahi-daemon.service

.. _isn't: https://bugzilla.samba.org/show_bug.cgi?id=12380
.. _available: https://github.com/samba-team/samba/pull/64

apcupsd
=======

My UPS has a `Network Management Card`_ which I'll use for graphing and email alerts. I also want my Server (and Mac Pro
desktop) to shut down when there's a power outage and low battery.

.. code-block:: bash

    sudo dnf install apcupsd
    sudo chmod 640 /etc/apcupsd/apcupsd.conf
    # Set: UPSCABLE ether; UPSTYPE pcnet; DEVICE <nmc IP>:device:<admin user phrase>
    # Also: NETSERVER off
    sudo firewall-cmd --permanent --add-port=3052/udp
    sudo systemctl restart firewalld.service
    sudo systemctl start apcupsd.service
    sudo systemctl enable apcupsd.service

Then write the following to ``/etc/apcupsd/doshutdown``:

.. literalinclude:: _static/doshutdown.sh
    :language: bash

.. _Network Management Card: http://www.apc.com/shop/us/en/products/UPS-Network-Management-Card-2-with-Environmental-Monitoring/P-AP9631

Monitoring/Graphing/Alerting
============================

TODO: Use subdomains for Grafana/etc.

I want everything I would normally check periodically on my server to be emailed to me instead. This will involve simple
cron jobs and more complicated emails derived from metrics.

.. code-block:: bash

    sudo dnf install smartmontools
    sudo systemctl start smartd

Then write the following to ``/usr/local/bin/filtered_journalctl``:

.. literalinclude:: _static/filtered_journalctl.sh
    :language: bash

Add these to the **root** crontab. The email configuration from earlier in this document will take care of forwarding
root emails to my real email address.

.. code-block:: bash

    0 20 * * * dnf check-update -C |wc -l |xargs test 20 -lt && dnf check-update -C
    1 20 * * * dnf updateinfo -C list sec |grep -v "Last metadata expiration check"
    @hourly /usr/local/bin/filtered_journalctl --since "1 hour ago" --priority warning
    @monthly /usr/sbin/btrfs scrub start -Bd /storage

Setup InfluxDB and friends by following this guide (takes care of installing Docker too):
https://robpol86.github.io/influxdb/

Plex
====

To give Plex access to my media I'll use sticky bits (setgid) to grant read access to my files to the media group. I'll
also run Plex within Docker.

.. code-block:: bash

    sudo docker run -d --name plex --restart always -h $HOSTNAME \
        -e "ADVERTISE_IP=http://$HOSTNAME:32400/" \
        -e "ALLOWED_NETWORKS=10.192.168.0/24" \
        -e "PLEX_GID=$(id media -g)" \
        -e "PLEX_UID=$(id media -u)" \
        -e "TZ=$(realpath --relative-to /usr/share/zoneinfo /etc/localtime)" \
        -e "VERSION=latest" \
        -p 1900:1900/udp \
        -p 3005:3005/tcp \
        -p 32400:32400/tcp \
        -p 32410:32410/udp \
        -p 32412:32412/udp \
        -p 32413:32413/udp \
        -p 32414:32414/udp \
        -p 32469:32469/tcp \
        -p 8324:8324/tcp \
        -v /storage/Local/MakeMKV:/data2:ro \
        -v /storage/Local/plex/config:/config \
        -v /storage/Media:/data:ro \
        -v /transcode \
        plexinc/pms-docker
    for p in $(sudo docker inspect plex |jq -r '.[].NetworkSettings.Ports |keys |join(" ")'); do
        sudo firewall-cmd --permanent --add-port=$p
    done
    sudo systemctl restart firewalld.service

Then browse to http://filesrv.rob86.net:32400/web/index.html to do the initial setup. Enable settings such as:

* Update my library automatically
* Run a partial scan when changes are detected
* Update my library periodically

BD/DVD Backups
==============

Follow the README at: https://github.com/Robpol86/makemkv/tree/robpol86

GitLab CE
=========

GitLab's Docker image hosts its own sshd service. First I need to create an interface alias for it to listen on:

.. code-block:: bash

    sudo vim /etc/sysconfig/network-scripts/ifcfg-eno3
    # Add: IPADDR2=10.192.168.40
    # Add: NETMASK2=255.255.255.0
    sudo ifdown eno3; sudo ifup $_

Next I need to tell my main sshd to listen on just the main interface instead of all interfaces.

.. code-block:: bash

    sudo vim /etc/ssh/sshd_config
    # ListenAddress 10.192.168.4
    sudo systemctl reload sshd.service

Start:

.. code-block:: bash

    sudo docker run -d --name gitlab --restart always -h git.$HOSTNAME \
        -p 10.192.168.40:80:80 -p 10.192.168.40:443:443 -p 10.192.168.40:22:22 \
        -v /etc/filesrv.rob86.net.cert.pem:/etc/ssl/git.filesrv.rob86.net.crt:ro \
        -v /etc/filesrv.rob86.net.key.pem:/etc/ssl/git.filesrv.rob86.net.key:ro \
        -v /storage/Local/gitlab/etc:/etc/gitlab:Z \
        -v /storage/Local/gitlab/log:/var/log/gitlab:Z \
        -v /storage/Local/gitlab/opt:/var/opt/gitlab:Z \
        gitlab/gitlab-ce:latest

Configure SMTP by editing ``/storage/Local/gitlab/etc/gitlab.rb``:

.. code-block:: ruby

    external_url 'https://git.filesrv.rob86.net'
    nginx['redirect_http_to_https'] = true
    nginx['ssl_certificate'] = "/etc/ssl/git.filesrv.rob86.net.crt"
    nginx['ssl_certificate_key'] = "/etc/ssl/git.filesrv.rob86.net.key"
    gitlab_rails['smtp_enable'] = true
    gitlab_rails['smtp_address'] = 'smtp.sparkpostmail.com'
    gitlab_rails['smtp_port'] = 587
    gitlab_rails['smtp_user_name'] = 'SMTP_Injection'
    gitlab_rails['smtp_password'] = '<API_KEY>'
    gitlab_rails['smtp_domain'] = 'robpol86.com'
    gitlab_rails['smtp_authentication'] = 'login'
    gitlab_rails['smtp_enable_starttls_auto'] = true
    gitlab_rails['gitlab_email_from'] = 'gitlab@robpol86.com'

Then run:

.. code-block:: bash

    sudo docker restart gitlab

Finally navigate to https://git.filesrv.rob86.net/

Backup Strategy
===============

For backups my main threat model is two-fold:

#. **Physical security**: someone breaking into my apartment and stealing my equipment and hard drives. This extends to
   my backups (I don't want a thief getting all of my data if they steal my backup hard drive).
#. **Ransomware**: I could make a mistake one day (nobody's perfect) or get infected via a 0-day. If all of my data is
   encrypted by ransomware the only road to recovery is a good backup strategy.

I was planning on using LTO7 tapes for backup but the $3000+ drive and $85 for each tape would add up to a lot of money
up front. Instead I'm going with regular hard drives for my backup. I'll secure each hard drive using LUKS full disk
encryption along with native `Btrfs compression <https://btrfs.wiki.kernel.org/index.php/Compression>`_. When restoring
I'll mount the drive with `enforced read-only`_ mode to prevent any possibility of malware infecting my backups.

I've got four 8 TB archive drives sitting around so I'll put them to good use as my backup drives. In the future once
all of my data results in more than 8 TB of storage I'll manually span my backups by assigning Btrfs subvolumes to
different disks. If a subvolume exceeds 8 TB of data then I'll have to go with more granular spanning but I'll worry
about that in the future.

.. _enforced read-only: https://www.amazon.com/Coolgear-SATA-Adapter-Write-Protect-Selection/dp/B005C55OYA

First Run
---------

On a new system we need to prepare it for backups. Run these commands:

.. code-block:: bash

    sudo mkdir /backup
    sudo dnf install rsync

Then write the following to ``/usr/local/bin/backup``:

.. literalinclude:: _static/backup.sh
    :language: bash

New Drives
----------

I initialize a new backup hard drive with:

.. code-block:: bash

    sudo fdisk -l /dev/sdg  # Make sure this is the right drive.
    sudo cryptsetup --cipher aes-cbc-essiv:sha256 luksFormat /dev/sdg
    sudo cryptsetup luksOpen /dev/sdg backup
    sudo mkfs.btrfs -L backup$(date +%Y%m%d) /dev/mapper/backup
    sudo cryptsetup luksClose /dev/mapper/backup

Backup Procedure
----------------

Using the script I wrote backup the subvolumes to the drive:

.. code-block:: bash

    until [ -b /dev/sdg ]; do sleep 1; done
    sudo cryptsetup luksOpen /dev/sdg backup
    sudo mount -o compress /dev/mapper/backup /backup
    sudo backup Local Main Media Old Stuff TimeMachine
    sudo umount /backup
    sudo cryptsetup luksClose /dev/mapper/backup

Restore Procedure
-----------------

If I need to restore data from a backup I'll run these commands. Remember to switch the Coolgear adapter to
**read-only** before plugging in the drive.

.. code-block:: bash

    sudo cryptsetup luksOpen --readonly /dev/sdg backup
    sudo mount -o ro /dev/mapper/backup /backup
    sudo umount /backup
    sudo cryptsetup luksClose /dev/mapper/backup

References
==========

* http://nyeggen.com/post/2014-04-05-full-disk-encryption-with-btrfs-and-multiple-drives-in-ubuntu/
