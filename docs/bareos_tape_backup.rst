.. _bareos_tape_backup:

============================
Bareos Tape Backup on a 124T
============================

I use `Bareos <https://www.bareos.org/en/>`_ (a fork of `Bacula <http://bacula.org/>`_) to backup my data at home from a
Linux computer to tape. Backing up to tape is a lot more convenient that backing up to DVD-R/BD-R, though it's probably
debatable when compared to backing up to an external hard drive. But having a tape autoloader is so cool!

.. imgur-embed:: 7DZQt
    :hide_post_details:

Equipment Used
==============

This guide should work with other pieces of equipment but it has been written with these devices in mind:

* CentOS 7.1
* `Dell PowerVault 124T Tape Autoloader <http://www.dell.com/us/business/p/powervault-124t-lto4hh/pd>`_
* `IBM Ultrium-TD3 Tape Drive <http://www-01.ibm.com/support/docview.wss?uid=swg21193425>`_ (inside the autoloader).

The plan is to rsync data from my OS X client to a directory on my Linux server, and to run all Bareos software on just
the server. I didn't like the idea of having some process running as root on OS X and trust that it only accessed a
specific volume, which isn't even configured on OS X (it's set in the Bareos director config on the Linux server).

I'll be running backups manually. I won't have any running schedules in Bareos and I'll have MariaDB (MySQL on CentOS)
and Bareos not start on boot. After every backup I'll stop those services.

I'll also only be defining full backups. I won't be defining any differential/incremental jobs in this guide.

Installation
============

We'll be installing Bareos and its dependencies from scratch on a new CentOS install. Some things I'd like to point out:

1. The giant ``bareos-dir.conf`` will be split up into 3 files for easier manageability.
2. I won't be using any kind of monitoring, emailing, or any sort of notifications. I'll just manually check the
   progress through the ``bconsole``. Since my CentOS server doesn't run a GUI I don't have a tray-monitor.

Verify Tape Drive/Autoloader
----------------------------

First we need to make sure the tape drive and autoloader have been detected by the OS. Do this by running ``lsscsi -g``
(don't need to be root). You should see something like this:

.. code-block:: none

    $ lsscsi -g
    [0:0:6:0]    tape    IBM      ULTRIUM-TD3      93GM  /dev/st0   /dev/sg2
    [0:0:6:1]    mediumx DELL     PV-124T          0085  /dev/sch0  /dev/sg3

If you don't see any ``sg`` devices you can try these commands, I had to run them on my CentOS installation:

.. code-block:: bash

    sudo su -c 'echo "sg" > /etc/modules-load.d/sg.conf'
    sudo systemctl restart systemd-modules-load.service

Install Bareos
--------------

We'll be using MariaDB as the backend database. Install it and secure it.

.. code-block:: bash

    sudo yum install mariadb-server
    sudo systemctl start mariadb.service
    sudo systemctl disable mariadb.service
    mysql_secure_installation  # Ignore find_mysql_client error.

Next install Bareos.

.. code-block:: bash

    wget "http://download.bareos.org/bareos/release/latest/CentOS_7/bareos.repo"
    sudo cp bareos.repo /etc/yum.repos.d/
    sudo yum install bareos bareos-database-mysql bareos-storage-tape
    sudo systemctl disable bareos-dir.service
    sudo systemctl disable bareos-sd.service
    sudo systemctl disable bareos-fd.service
    sudo /usr/lib/bareos/scripts/create_bareos_database mysql -u root -p
    sudo /usr/lib/bareos/scripts/make_bareos_tables mysql -u root -p
    dbpw=$(openssl rand -base64 45)
    sudo db_password="$dbpw" /usr/lib/bareos/scripts/grant_bareos_privileges mysql -u root -p
    sudo sed -i.bak 's@\(dbpassword =\) ""@\1 "'$dbpw'"@g' /etc/bareos/bareos-dir.conf
    unset dbpw

I'll be using ``/home/bareos`` to rsync files to. I'll need to grant the ``bareos`` user access to this so it may backup
and restore files there, and I'll also need to grant another user (e.g. ``support``) access to login through rsync (it's
a bad idea to grant login privileges to bareos).

.. code-block:: bash

    sudo mkdir -m0700 /home/bareos
    sudo chown bareos:bareos /home/bareos
    sudo setfacl -d -m u:bareos:rwx -m g:support:rwx /home/bareos
    sudo setfacl -m u:bareos:rwx -m g:support:rwx /home/bareos

File/Storage Daemon Config
--------------------------

Overwrite these two files. Make sure to substitute ``moops`` with the original setting. Omit the PKI lines if you do
not plan on
`encrypting your backup file data <http://doc.bareos.org/master/html/bareos-manual-main-reference.html#x1-30500027.2>`_.

.. warning::

    While Bareos does support encryption, ``bscan`` and ``bextract`` do not! This means if you ever lose your Bareos
    server and you do not have a clear-text backup of your MySQL database, you won't be able to restore the catalog
    from tape (even if you have your encryption keys) without a lot of manual and unsupported work.

.. literalinclude:: _static/bareos-fd.conf
    :language: kconfig

For the storage daemon substitute ``/dev/sg3`` and ``/dev/nst0`` below with the device files found on your system. We'll
be verifying them in the next section.

.. literalinclude:: _static/bareos-sd.conf
    :language: kconfig

Verify Storage Config
---------------------

Before we go any further we should make sure the storage daemon configuration file is valid. We can easily test this
with the commands below. Load up a tape inside the **tape drive** and another tape in **slot 1** in your autoloader. I
did this using my autoloader's web interface.

First we make sure the tape drive works. Substitute ``/dev/nst0`` with what you have in the storage daemon config:

.. code-block:: bash

    sudo mt -f /dev/nst0 rewind
    mkdir src dst && date > ./src/date.txt
    sudo tar -cvf /dev/nst0 src
    sudo mt -f /dev/nst0 rewind
    sudo tar -xvf /dev/nst0 -C dst
    ls -lah src/ dst/src/; cat src/date.txt dst/src/date.txt

Next we'll test the autoloader as well as the storage daemon config:

.. code-block:: bash

    sudo mtx -f /dev/sg3 inquiry  # Test autoloader.
    sudo btape /dev/nst0  # Run "test" in the console.

This is what I got when I ran those two commands:

.. code-block:: none

    $ sudo mtx -f /dev/sg3 inquiry
    Product Type: Medium Changer
    Vendor ID: 'DELL    '
    Product ID: 'PV-124T         '
    Revision: '0085'
    Attached Changer API: No
    $ sudo btape /dev/nst0
    Tape block granularity is 1024 bytes.
    btape: butil.c:301-0 Using device: "/dev/nst0" for writing.
    btape: btape.c:484-0 open device "ULTRIUM-TD3" (/dev/nst0): OK
    *test

    === Write, rewind, and re-read test ===

    I'm going to write 10000 records and an EOF
    then write 10000 records and an EOF, then rewind,
    and re-read the data to verify that it is correct.

    This is an *essential* feature ...

    btape: btape.c:1171-0 Wrote 10000 blocks of 64412 bytes.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1187-0 Wrote 10000 blocks of 64412 bytes.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1229-0 Rewind OK.
    10000 blocks re-read correctly.
    Got EOF on tape.
    10000 blocks re-read correctly.
    === Test Succeeded. End Write, rewind, and re-read test ===

    btape: btape.c:1297-0 Block position test
    btape: btape.c:1309-0 Rewind OK.
    Reposition to file:block 0:4
    Block 5 re-read correctly.
    Reposition to file:block 0:200
    Block 201 re-read correctly.
    Reposition to file:block 0:9999
    Block 10000 re-read correctly.
    Reposition to file:block 1:0
    Block 10001 re-read correctly.
    Reposition to file:block 1:600
    Block 10601 re-read correctly.
    Reposition to file:block 1:9999
    Block 20000 re-read correctly.
    === Test Succeeded. End Write, rewind, and re-read test ===



    === Append files test ===

    This test is essential to Bareos.

    I'm going to write one record  in file 0,
                       two records in file 1,
                 and three records in file 2

    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:484-0 open device "ULTRIUM-TD3" (/dev/nst0): OK
    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1441-0 Now moving to end of medium.
    btape: btape.c:637-0 Moved to end of medium.
    We should be in file 3. I am at file 3. This is correct!

    Now the important part, I am going to attempt to append to the tape.

    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    Done appending, there should be no I/O errors

    Doing Bareos scan of blocks:
    1 block of 64448 bytes in file 1
    End of File mark.
    2 blocks of 64448 bytes in file 2
    End of File mark.
    3 blocks of 64448 bytes in file 3
    End of File mark.
    1 block of 64448 bytes in file 4
    End of File mark.
    Total files=4, blocks=7, bytes = 451,136
    End scanning the tape.
    We should be in file 4. I am at file 4. This is correct!

    The above Bareos scan should have output identical to what follows.
    Please double check it ...
    === Sample correct output ===
    1 block of 64448 bytes in file 1
    End of File mark.
    2 blocks of 64448 bytes in file 2
    End of File mark.
    3 blocks of 64448 bytes in file 3
    End of File mark.
    1 block of 64448 bytes in file 4
    End of File mark.
    Total files=4, blocks=7, bytes = 451,136
    === End sample correct output ===

    If the above scan output is not identical to the
    sample output, you MUST correct the problem
    or Bareos will not be able to write multiple Jobs to
    the tape.


    === Write, backup, and re-read test ===

    I'm going to write three records and an EOF
    then backup over the EOF and re-read the last record.
    Bareos does this after writing the last block on the
    tape to verify that the block was written correctly.

    This is not an *essential* feature ...

    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:823-0 Wrote first record of 64412 bytes.
    btape: btape.c:834-0 Wrote second record of 64412 bytes.
    btape: btape.c:845-0 Wrote third record of 64412 bytes.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:861-0 Backspaced over EOF OK.
    btape: btape.c:866-0 Backspace record OK.
    btape: btape.c:884-0
    Block re-read correct. Test succeeded!
    === End Write, backup, and re-read test ===



    === Forward space files test ===

    This test is essential to Bareos.

    I'm going to write five files then test forward spacing

    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1928-0 Wrote one record of 64412 bytes.
    btape: btape.c:1930-0 Wrote block to device.
    btape: btape.c:616-0 Wrote 1 EOF to "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1655-0 Now forward spacing 1 file.
    We should be in file 1. I am at file 1. This is correct!
    btape: btape.c:1667-0 Now forward spacing 2 files.
    We should be in file 3. I am at file 3. This is correct!
    btape: btape.c:586-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1680-0 Now forward spacing 4 files.
    We should be in file 4. I am at file 4. This is correct!

    btape: btape.c:1698-0 Now forward spacing 1 more file.
    We should be in file 5. I am at file 5. This is correct!

    === End Forward space files test ===


    Ah, I see you have an autochanger configured.
    To test the autochanger you must have a blank tape
     that I can write on in Slot 1.

    Do you wish to continue with the Autochanger test? (y/n): y


    === Autochanger test ===

    3301 Issuing autochanger "loaded" command.
    Slot 1 loaded. I am going to unload it.
    3302 Issuing autochanger "unload 1 0" command.
    unload status=OK 0
    3303 Issuing autochanger "load 1 0" command.
    3303 Autochanger "load 1 0" status is OK.
    btape: btape.c:484-0 open device "ULTRIUM-TD3" (/dev/nst0): OK
    btape: btape.c:1585-0 Rewound "ULTRIUM-TD3" (/dev/nst0)
    btape: btape.c:1592-0 Wrote EOF to "ULTRIUM-TD3" (/dev/nst0)

    The test autochanger worked!!

    *q

Director Daemon Config
----------------------

Finally we configure the Bareos director. I'll be defining three separate directories to backup. You may substitute this
for one directory or however many you need. These directories will be owned by ``bareos:bareos`` and will be populated
remotely using ``rsync`` (e.g. pushed from my OS X desktop computer).

.. note::
    The `Bareos documentation <http://doc.bareos.org/master/html/bareos-manual-main-reference.html#x1-730005.12>`_
    encourages you not to use ``localhost`` in your configuration. Instead use the FQDN and make sure you can resolve it
    properly.

We'll be splitting up the director configuration into a few files since otherwise it would be pretty big. If you don't
like that you can just merge these into ``bareos-dir.conf`` and it'll work just the same.

.. literalinclude:: _static/filesets.conf
    :language: kconfig

.. literalinclude:: _static/jobs.conf
    :language: kconfig

.. literalinclude:: _static/bareos-dir.conf
    :language: kconfig

Start Services
--------------

Everything should work.

.. code-block:: bash

    sudo systemctl start bareos-fd.service
    sudo systemctl start bareos-sd.service
    sudo systemctl start bareos-dir.service
    sudo systemctl status bareos-fd.service
    sudo systemctl status bareos-sd.service
    sudo systemctl status bareos-dir.service

Test Everything
---------------

Here we'll do a quick test. We'll create a bunch of files in ``/home/bareos/selftest`` (defined in
``/etc/bareos/bareos-dir.d/filesets.conf``) and back them up to one or two
tapes. Then we'll restore them to ``/home/bareos/tmp/restores`` (defined in ``/etc/bareos/bareos-dir.d/jobs.conf``).
We'll compare them with ``sha1sum``.

.. tip::
    Since we're starting with an empty Bareos database, it will consider all tapes empty. Remove any tapes from the
    autoloader that you don't want overridden. You can use my
    `tape_bulk_eject.py <https://github.com/Robpol86/tape_bulk_eject>`_ tool to automate this.

.. code-block:: bash

    # Create files.
    rm -rf /home/bareos/selftest; mkdir /home/bareos/selftest
    date |tee /home/bareos/selftest/current_date.txt
    openssl rand -base64 $(( 2**30 * 3/4 * 2 )) -out /home/bareos/selftest/2_gb_random.bin
    mkdir -p /home/bareos/selftest/subdir1/subdir2
    (cd /home/bareos/selftest; for i in {1..15}; do cat 2_gb_random.bin >> subdir1/subdir2/30_gb_random.bin; done)
    find /home/bareos/selftest -type f -exec sha1sum {} \+

    # Backup through bconsole.
    sudo bconsole

In the Bareos console we'll type these commands to backup the above files and then restore them to a separate directory.
Remove any tapes from the drive.

.. code-block:: bash

    update slots  # Read the status of all slots in the autoloader.
    label barcodes  # Initialize all tapes. Select Full pool. ETA 30 mins for 16 tapes.
    list volumes  # Verify all tapes have been detected.
    run BackupSelfTest
    status client  # Check the status of the job. You can also run "messages".
    restore  # After backup is done do this. Follow the directions.
    q

Finally run ``find /home/bareos/tmp/restores/home/bareos/selftest/ -type f -exec sha1sum {} \+`` and compare sha sums.
You can test if your data is actually encrypted by temporarily removing the PKI lines from ``bareos-fd.conf`` and
running the ``restore`` command again.

Reusing Old Tapes
=================

Several years ago before Bareos I used Bacula. I consider the data on my old tapes as disposable and I want to start
fresh. Unfortunately Bareos (and Bacula) doesn't have an easy way to reuse tapes. The best method I've found was to
manually wipe them. I run these commands:

.. code-block:: bash

    # Stop Bareos services.
    for s in dir sd fd; do sudo systemctl stop bareos-$s.service; done
    # Make sure drive is unlocked and unloaded. Also which slots tapes are in.
    sudo mtx -f /dev/sg3 status
    # Wipe selected tapes. Here {1..16} expands to all 16 slots.
    for t in {1..16}; do
        sudo mtx -f /dev/sg3 load $t 0
        sudo mt -f /dev/nst0 weof
        sudo mtx -f /dev/sg3 unload $t 0
    done

Backing Up Data
===============

These are the commands I run to backup my data.

.. code-block:: bash

    # On the client.
    rsync -irtv --delete Main Old moops:/home/bareos/bosco

.. code-block:: bash

    # On the server.
    sudo su -c 'for f in /sys/class/scsi_host/host*/scan; do echo "- - -" > $f; done'
    lsscsi -g  # Verify autoloader and tape drive are present.
    sudo systemctl start mariadb.service
    for s in fd sd dir; do sudo systemctl start bareos-$s.service; done
    sudo mtx -f /dev/sg3 status  # Verify tape drive (element 0) is empty.
    sudo bconsole

.. code-block:: bash

    # In bconsole on the server.
    update slots
    # New tapes: label slot=8,12,14-16 barcodes
    list volumes
    run job=BackupBoscoMain
    run job=BackupBoscoOld
    run job=BackupCatalog
    status client

Once all three jobs finish (you can queue them up at the same time) you're done. I always eject all tapes and store them
off-site, so I run these commands within ``bconsole``:

.. code-block:: bash

    unmount Tape  # Unloads the last tape from the drive.
    list jobs
    list volumes jobid=1 jobid=2 jobid=3

Finally you'll want to backup your Bareos database somewhere in case you need to restore the catalog on another machine
or if you lose your Bareos/MySQL server. You only need to do this if you encrypt your tapes.

.. code-block:: bash

    sudo cat /var/lib/bareos/bareos.sql |gzip -9 > ~/bareos.sql.gz
    sudo rm /var/lib/bareos/bareos.sql

Then I use my `tape_bulk_eject.py <https://github.com/Robpol86/tape_bulk_eject>`_ tool to eject all those tapes. I also
stop all services since I don't leave my autoloader running all the time (it's too loud for my living room).

.. code-block:: bash

    for s in dir sd fd; do sudo systemctl stop bareos-$s.service; done
    sudo systemctl stop mariadb.service
    ./tape_bulk_eject.py "000039L3|000031L3" "000031L3|000021L3|000032L3|000033L3|000030L3"

Comments
========

.. disqus::
