.. _root_certificate_authority:

=========================
Setting Up a Home Root CA
=========================

.. warning::
    This guide is incomplete! I'm still writing it.

Tired of getting those SSL error pages when accessing your router's admin interface? Sick of having to click three times
to get to your IPMI web interface? Have I got a guide for you!

This guide will go over setting up an offline root certificate authority for your home network. It is based on what I
learned from https://jamielinux.com/docs/openssl-certificate-authority/index.html with a few changes:

1. This guide will include steps on setting up the root CA on a Raspberry Pi, though it should really work on any linux
   computer.
2. I will not be creating an intermediate pair here. Since my intentions are just setting up SSL certs on a handful of
   internal web interfaces and maybe even WPA2 Enterprise one day, I didn't think it was worth setting this up. It might
   make revoking certs not as quick, but I don't see myself signing very many certs after my initial run.
3. I'll include steps on how to bridge the `air gap <https://en.wikipedia.org/wiki/Air_gap_(networking)>`_. For maximum
   paranoid-tier security we will not be plugging in any USB flash drives (or USB anything excluding keyboards) or
   network cables. WiFi adapters are also obviously forbidden. For this we'll be using
   `qrencode <http://fukuchi.org/works/qrencode/>`_.
4. I'll also include a note about setting up a dedicated domain name for your home network.

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
(``/dev/sdb2`` here is the SD card's OS partition).

.. warning::
    The ``luksFormat`` command will nuke your SD card and it will also be asking you for a LUKS password. Make sure it's
    a long password with lots of special characters.

.. note::
    The ``pv`` command below just lets use see a pretty progress bar since copying data to/from the SD card takes a long
    time. It's not required and you can omit it if you want.

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

We still need to setup the last steps that allows the Raspberry Pi to mount encrypted partitions. Keep running these
steps on the Linux computer:

1. In ``/tmp/pi_boot/cmdline.txt`` change ``root=/dev/mmcblk0p2`` to ``root=/dev/mapper/sdcard`` and append
   ``cryptdevice=/dev/mmcblk0p2:sdcard`` to the end of the file.
2. In ``/tmp/pi_root/etc/fstab`` change ``/dev/mmcblk0p2`` to ``/dev/mapper/sdcard``.
3. In ``/tmp/pi_root/etc/crypttab`` append ``sdcard  /dev/mmcblk0p2  none    luks`` to the end of the file.

Now go ahead and unmount the SD card and put it back in the Raspberry Pi:

1. ``sudo umount /tmp/pi_boot /tmp/pi_root``
2. ``sudo cryptsetup luksClose sdcard``

When you try to boot the Raspberry Pi it will fail and drop to the ``initramfs`` prompt. This will happen every time
from now on. When you get that prompt should run:

* ``cryptsetup luksOpen /dev/mmcblk0p2 sdcard``

After putting in your LUKS password just exit and it will keep booting like usual.

In the section

Copy the OpenSSL Config
=======================

.. note::

    Based on a few `articles <http://www.mdmarra.com/2012/11/why-you-shouldnt-use-local-in-your.html>`_ I've
    `found <http://serverfault.com/questions/71052/choosing-local-versus-public-domain-name-for-active-directory>`_
    while `considering <http://serverfault.com/questions/17255/top-level-domain-domain-suffix-for-private-network>`_
    which domain to use at home, I thought I would mention it here even though it's more of a
    network-related topic rather than an SSL/Certificate topic. I highly encourage you to either purchase a dedicated
    domain name for your home network or at least use a dedicated subdomain on a domain you already own.

    In the table below I'll use ``myhome.net`` as an example. Org Name is just a name so in this case the value would be
    "MyHome.net". If you used ``home.mycooldomain.com`` then the Org Name equivalent may be "Home.MyCoolDomain.com". It
    can actually be set to anything but this is what I've done for my home network.

Copy the following to ``/etc/ssl/openssl.cnf``. Paste/copy the following and overwrite whatever was in there
before. It's still ok to have network access for this part.

You'll have to replace the following values:

=================== =================================================== =============
To Replace          Replace With                                        Example
=================== =================================================== =============
SUB_COUNTRY_NAME    Two-letter ISO abbreviation for your country.       US
SUB_STATE_NAME      State or province where you live. No abbreviations. California
SUB_LOCALITY        City where you are located.                         San Francisco
SUB_ORG_NAME        Name of your organization.                          MyHome.net
SUB_UNIT_NAME       Section of the organization.                        Home
SUB_EMAIL           Your contact email.                                 xx@yy.zz
=================== =================================================== =============

.. code-block:: ini

    # /etc/ssl/openssl.cnf
    [ ca ]
    default_ca = CA_default

    [ CA_default ]
    # Directory and file locations.
    dir               = /root/ca
    certs             = $dir/certs
    crl_dir           = $dir/crl
    new_certs_dir     = $dir/newcerts
    database          = $dir/index.txt
    serial            = $dir/serial
    RANDFILE          = $dir/private/.rand

    # The root key and root certificate.
    private_key       = $dir/private/ca.key.pem
    certificate       = $dir/certs/ca.cert.pem

    # For certificate revocation lists.
    crlnumber         = $dir/crlnumber
    crl               = $dir/crl/ca.crl.pem
    crl_extensions    = crl_ext
    default_crl_days  = 30

    default_md        = sha512
    name_opt          = ca_default
    cert_opt          = ca_default
    default_days      = 375
    preserve          = no
    policy            = policy_loose

    [ policy_loose ]
    # See the POLICY FORMAT section of the `ca` man page.
    countryName             = optional
    stateOrProvinceName     = optional
    localityName            = optional
    organizationName        = optional
    organizationalUnitName  = optional
    commonName              = supplied
    emailAddress            = optional

    [ req ]
    # Options for the `req` tool (`man req`).
    default_bits        = 4096
    distinguished_name  = req_distinguished_name
    string_mask         = utf8only
    default_md          = sha512

    # Extension to add when the -x509 option is used.
    x509_extensions     = v3_ca

    [ req_distinguished_name ]
    # See <https://en.wikipedia.org/wiki/Certificate_signing_request>.
    countryName                     = Country Name (2 letter code)
    stateOrProvinceName             = State or Province Name
    localityName                    = Locality Name
    0.organizationName              = Organization Name
    organizationalUnitName          = Organizational Unit Name
    commonName                      = Common Name
    emailAddress                    = Email Address

    # Optionally, specify some defaults.
    countryName_default             = SUB_COUNTRY_NAME
    stateOrProvinceName_default     = SUB_STATE_NAME
    localityName_default            = SUB_LOCALITY
    0.organizationName_default      = SUB_ORG_NAME
    organizationalUnitName_default  = SUB_UNIT_NAME
    emailAddress_default            = SUB_EMAIL

    [ v3_ca ]
    # Extensions for a typical CA (`man x509v3_config`).
    subjectKeyIdentifier = hash
    authorityKeyIdentifier = keyid:always,issuer
    basicConstraints = critical, CA:true, pathlen:0
    keyUsage = critical, digitalSignature, cRLSign, keyCertSign

    [ usr_cert ]
    # Extensions for client certificates (`man x509v3_config`).
    basicConstraints = CA:FALSE
    nsCertType = client, email
    nsComment = "OpenSSL Generated Client Certificate"
    subjectKeyIdentifier = hash
    authorityKeyIdentifier = keyid,issuer
    keyUsage = critical, nonRepudiation, digitalSignature, keyEncipherment
    extendedKeyUsage = clientAuth, emailProtection

    [ server_cert ]
    # Extensions for server certificates (`man x509v3_config`).
    basicConstraints = CA:FALSE
    nsCertType = server
    nsComment = "OpenSSL Generated Server Certificate"
    subjectKeyIdentifier = hash
    authorityKeyIdentifier = keyid,issuer:always
    keyUsage = critical, digitalSignature, keyEncipherment
    extendedKeyUsage = serverAuth

    [ crl_ext ]
    # Extension for CRLs (`man x509v3_config`).
    authorityKeyIdentifier=keyid:always

    [ ocsp ]
    # Extension for OCSP signing certificates (`man ocsp`).
    basicConstraints = CA:FALSE
    subjectKeyIdentifier = hash
    authorityKeyIdentifier = keyid,issuer
    keyUsage = critical, digitalSignature
    extendedKeyUsage = critical, OCSPSigning

Air Gap
=======

This is the moment we've all been waiting for! Remove all USB devices (sans keyboard) and network cables/connections. If
this is on a Raspberry Pi either swap it out with a Model A (the one without an ethernet port), or fill in the ethernet
port with hot glue. Do the same with all but one USB ports. Or just be super duper sure never to plug in things when
using this SD card.

OpenSSL Directory Structure
===========================

Everything will live in ``/root/ca``. It will also all be owned by root. Remember this computer is a dedicated CA so it
won't be doing anything else at all except hosting your very important root certificate private key and the root
certificate itself.

Run these commands as root:

.. code-block:: bash

    mkdir /root/ca; cd /root/ca; mkdir certs crl csr newcerts private
    chmod 700 private; touch index.txt
    echo 1000 > serial

Finally Generate the Pair
=========================

This is where we actually generate the root key and certificate. The root key is used to sign additional certificate
pairs for specific devices/servers, and the root certificate is what you'll export to clients that should trust any of
these additional certificates.

.. note::
    The ``openssl req`` command will prompt you for some information. The defaults you've specified in openssl.cnf will
    be fine. However it will prompt you for "Common Name". Put in the fully qualified domain name of this certificate
    authority.

.. code-block:: bash

    touch private/ca.key.pem
    chmod 400 private/ca.key.pem
    openssl genrsa -aes256 -out private/ca.key.pem 8192  # This took 15 minutes to run.
    touch certs/ca.cert.pem
    chmod 444 certs/ca.cert.pem
    openssl req -key private/ca.key.pem -new -x509 -days 1827 -sha256 -extensions v3_ca -out certs/ca.cert.pem
    openssl x509 -noout -text -in certs/ca.cert.pem |more  # Confirm everything looks good.