.. _root_certificate_authority:

=========================
Setting Up a Home Root CA
=========================

Tired of getting those SSL error pages when accessing your router's admin interface? Sick of having to click three times
to get to your IPMI web interface? Have I got a guide for you!

.. imgur-embed:: a/PFrHX

Preface
=======

This guide will go over setting up an offline root certificate authority for your home network. It is based on what I've
learned from https://jamielinux.com/docs/openssl-certificate-authority/index.html with a few changes:

1. This guide will include steps on setting up the root CA on a Raspberry Pi, though it should really work on any linux
   computer. If you plan on using something else as your root CA (a $200 Chromebook, an old Linux computer, etc) then
   substitute "Raspberry Pi" used throughout this guide for whatever you're using.
2. We will not be creating an intermediate pair here. Since my intentions are just setting up SSL certs on a handful of
   internal web interfaces and maybe even WPA2 Enterprise one day, I didn't think it was worth setting this up. It might
   make revoking certs not as quick, but I don't see myself signing very many certs after my initial run.
3. I'll include steps on how to bridge the `air gap <https://en.wikipedia.org/wiki/Air_gap_(networking)>`_. For maximum
   paranoid-tier security we will not be plugging in any USB flash drives (or USB anything excluding keyboards) or
   network cables. WiFi adapters are also obviously forbidden. For this we'll be using
   `qrencode <https://fukuchi.org/works/qrencode/>`_.
4. For additional paranoid-tier security we'll generate a 8192-bit long RSA key for our root CA. 4096-bit keys are fine
   too but I'm crazy. We'll also be creating 4096-bit SSL keys instead of the usual 2048-bit. If you're using OS X and
   you get an error trying to install the root certificate, read
   https://apple.stackexchange.com/questions/110261/mac-os-x-10-9-and-8192-bit-certificates-error-67762/ .

The goal here is to setup an offline root CA. It will be online at first to get updates (this is optional) but right
before generating the root pair we will remove any network connectivity from the host and never EVER connect it to any
networks or USB devices. This will be an offline and air gapped root CA.

Preparing the Raspberry Pi
==========================

If you aren't using a Raspberry Pi for your root CA you can safely skip this section. The gist of this section is we'll
be setting up LUKS full disk encryption. You'll need to install OpenSSL and ``qrencode`` (for transmitting keys over the
air gap).

1. Install Raspbian and boot up the Raspberry Pi. It's ok to have network access for now. If you have internet access go
   ahead and ``sudo apt-get update && sudo apt-get upgrade``. I followed
   `Raspbian Setup (Raspberry Pi) <https://gist.github.com/Robpol86/3d4730818816f866452e>`_ (you don't need to install
   any of those packages in that link, just upgrade).
2. Ok now install these required packages: ``sudo apt-get install busybox cryptsetup pv qrencode``

Full Disk Encryption
--------------------

I got most of these steps from: http://paxswill.com/blog/2013/11/04/encrypted-raspberry-pi/ . You'll need a Linux
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

Copy the OpenSSL Config
=======================

.. note::

    Based on a few `articles <http://www.mdmarra.com/2012/11/why-you-shouldnt-use-local-in-your.html>`_ I've
    `found <https://serverfault.com/questions/71052/choosing-local-versus-public-domain-name-for-active-directory>`_
    while `considering <https://serverfault.com/questions/17255/top-level-domain-domain-suffix-for-private-network>`_
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

    mkdir -p /root/ca/{certs,crl,csr,newcerts,private}
    setfacl -d -m u::rx -m g::- -m o::- /root/ca/private
    setfacl -d -m u::rx -m g::rx -m o::rx /root/ca/certs
    chmod 700 /root/ca/private; touch /root/ca/index.txt
    echo 1000 > /root/ca/serial

Those ``setfacl`` commands set filesystem ACLs which enforce default maximum file permissions for new files/directories.
A brief description for these directories:

======================= =============================
Directory               Description
======================= =============================
``/root/ca/certs``      Certificates are dumped here.
``/root/ca/crl``        Certificate revocation lists.
``/root/ca/csr``        Certificate signing request.
``/root/ca/newcerts``   Not used in this guide.
``/root/ca/private``    Private keys. VERY SENSITIVE.
======================= =============================

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

    cd /root/ca
    openssl genrsa -aes256 -out private/ca.key.pem 8192  # This took 15 minutes to run.
    openssl req -key private/ca.key.pem -new -x509 -days 1827 -sha256 -extensions v3_ca -out certs/ca.cert.pem
    openssl x509 -noout -text -in certs/ca.cert.pem |more  # Confirm everything looks good.

You're done generating your root certificate and private key. You're technically "done". However you'll probably want
to do these two steps:

1. Install the public root certificate on client computers so they can trust your servers instead of getting SSL errors.
2. Creating an SSL certificate to install on your web servers (router admin pages, IPMI interfaces, etc.).

For the former you'll want to export the ``/root/ca/certs/ca.cert.pem`` file and install it on client computers/devices.
For example the "Keychain Access" app in OS X can install that file in the System keychain (not System Roots), an you'll
need to manually set the trust to "Always Trust". You may also have to restart web browsers (or just reboot) to get rid
of SSL errors. Instructions for exporting this file is available in the `Bridging the Air Gap`_ section below.

For the ladder you'll have to scroll down to the `Issuing Server Certificates`_ section for more information.

Frequent Tasks
==============

This section will contain additional sub sections with instructions on how to complete some tasks you may repeat for
different use cases.

Bridging the Air Gap
--------------------

We can use ``qrencode`` to encode small bits of data into QR codes to be scanned by your phone and reassembled on
another computer. This is a one-way data transfer so your Raspberry Pi remains secure and air gapped.

Create QR Codes
```````````````

With these commands we will tar up the files we intend to transmit, encrypt them for safety, base64 the encrypted binary
data into a string, pass it to ``qrencode``, and finally display the QR codes(s) to be scanned by a phone/tablet/laptop.
Run these commands on your Raspberry Pi. Be sure to replace ``FILES`` with one or more files you want to transmit.

.. note::
    Since certificates and keys are relatively large we need the "high resolution" provided by a graphical user
    interface. Having a 1024x768 terminal screen buffer isn't enough to transmit data unless you really enjoy scanning
    tons of QR codes and reassembling them manually.

.. note::
    The large command involving "openssl enc" will prompt you for a password. You'll only use this password once when
    you decrypt the data on the receiving computer in the next section.

.. code-block:: bash

    rm /tmp/qr*.png  # Remove any previously created QR codes.
    tar -czv FILES |openssl enc -aes-256-cfb -salt |base64 -w0 |qrencode -o /tmp/qr.png -Sv40
    startx  # Only needed if you don't already run a GUI.

This creates either one or more QR codes in ``/tmp`` suffixed with numbers. After ``startx`` loads the GUI open the
images and scan them with your phone or whatever device you are using.

Reconstructing Data
```````````````````

This section presumes you've scanned the QR codes and saved the large strings of data somewhere on a Linux or OS X
computer. If you're scanning QR codes with an Android phone using "Barcode Scanner" you can "Share via email" which
gives you the option to share to Dropbox (for some dumb reason) which makes it easy to get encrypted data on your
computer.

Run these commands to reassemble and decrypt data:

.. code-block:: bash

    mkdir ~/inbound_certs
    cat [1-3].txt |base64 -D |openssl enc -aes-256-cfb -d |tar -xzvC ~/inbound_certs

Issuing Server Certificates
---------------------------

This section covers issuing SSL certificates for web servers such as router admin pages. We will generate an SSL
certificate and its private key. You'll need to install both files on the web server. Keep in mind the private key is
very sensitive and is used to sign SSL sessions to keep it secure as you transfer it to the web server!

.. note::
    Two things. When prompted for a pass phrase, enter nothing. Leave it blank and just press enter. Usually when your
    web server restarts you don't want it asking for a password to unlock the private key. Second, when asked for a
    "Common Name" you'll need to enter the web server's FQDN. So instead of accessing your router admin page using
    http://192.168.0.1 you'll instead be using https://router.myhome.net for example. Common Name here will be
    ``router.myhome.net``.

On the Raspberry Pi run these commands. The substitute ``router.myhome.net`` with whatever FQDN your target web server
will use.

.. code-block:: bash

    cd /root/ca
    openssl genrsa -out private/router.myhome.net.key.pem 4096
    openssl req -key private/router.myhome.net.key.pem -new -sha256 -out csr/router.myhome.net.csr.pem  # No pass phrase; CN is FQDN.
    openssl ca -extensions server_cert -days 365 -notext -md sha256 -in csr/router.myhome.net.csr.pem -out certs/router.myhome.net.cert.pem
    rm csr/router.myhome.net.csr.pem
    openssl x509 -noout -text -in certs/router.myhome.net.cert.pem |more  # Confirm everything looks good.

Verify that the **Issuer** is the root CA and the **Subject** is the certificate itself. Also verify
``/root/ca/index.txt`` mentions the new certificate. You will need to install both
``/root/ca/certs/router.myhome.net.cert.pem`` and ``/root/ca/private/router.myhome.net.key.pem`` on the web server. Read
`Bridging the Air Gap`_ for instructions on how to do this securely.

Comments
========

.. disqus::
