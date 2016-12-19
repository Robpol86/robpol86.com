.. _postfix_gmail_forwarding:

============================
Postfix and Gmail Forwarding
============================

You may be familiar with the `local mail spool`_ on your Linux system. Often error messages from failed cron jobs are
sent there. However this isn't much use if the server goes down or loses network connectivity. It would be nice to have
it send those emails out to an external email inbox instead. That way you can be notified when disks fail in a RAID
array or when applications/services fail or produce errors.

We'll be setting up email forwarding for the root mail spool. Most ISPs block SMTP port 25 for anti-spam and other
reasons so we'll need an SMTP server we can authenticate to. You can have two choices here:

* Obtain the SMTP server and port from your ISP and use your account's credentials.
* Use a dedicated Google Apps/G Suite/Gmail account.

This guide will use the Gmail route since I plan on using it for my home Fedora server and for my
:ref:`cellular Raspberry Pi <raspberry_pi_project_fi>`. Using non-ISP credentials allows you to use the same SMTP
account on different WiFi networks as well. However these instructions should work for ISP and any other SMTP provider.

.. tip::

    I highly recommend using a dedicated email account for this. It's not a good idea to put your main email credentials
    in plain-text in any file even if it's protected by file permissions. If a system gets remotely or physically
    compromised you don't want someone having access to your main email account.

The steps outlined in this guide have been tested on the following operating systems but should work for basically any
Linux distro:

* Fedora Server 25 (Fedora-Server-dvd-x86_64-25-1.3.iso)
* Debian Jessie (2016-11-25-raspbian-jessie-lite.img)

Install Postfix
===============

First we must install software to forward mail and handle authenticating to the external SMTP server. There are several
MTAs (message transfer agents) available but I'll be using `Postfix <http://www.postfix.org/>`_. Let's install it:

.. note::

    On Debian the postfix install script will prompt you for some info. Select ``Internet Site`` as the general type of
    configuration and use either ``gmail.com`` or your G Suite domain name for the system mail name.

.. code-block:: bash

    # On Fedora:
    sudo dnf install postfix cyrus-sasl{,-plain}
    # On Debian:
    sudo apt-get install postfix libsasl2-modules

Configuration
-------------

Next we'll need to configure the SASL file. This is used by Postfix to authenticate to Google's strict SMTP
requirements.

.. warning::

    If you're using Gmail/G Suite, you'll need to log into your account's "Sign-in & Security" section, scroll to the
    bottom, and enable "Allow less secure apps" so Google will allow Postfix to authenticate. More information:
    https://support.google.com/accounts/answer/6010255?hl=en

First touch and lock down the ``sasl_passwd`` file since this will hold your Gmail password in plain-text. Then populate
it with either opening it with a text editor or having ``tee`` do it for you.

.. code-block:: bash

    sudo touch /etc/postfix/sasl_passwd; sudo chmod 600 $_
    sudo tee /etc/postfix/sasl_passwd <<< '[smtp.gmail.com]:587 SENDER@gmail.com:PASSWORD'

Next open ``/etc/postfix/main.cf`` and configure it with:

.. note::

    On Debian ``myorigin`` will point to ``/etc/mailname``. Verify the contents of that file is ``gmail.com`` (or your
    G Suite domain).

.. code::

    myorigin = gmail.com
    mydestination = gmail.com, $myhostname, localhost.$mydomain, localhost
    relayhost = [smtp.gmail.com]:587
    smtp_sasl_auth_enable = yes
    smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
    smtp_sasl_security_options = noanonymous
    smtp_sasl_tls_security_options = noanonymous
    smtp_tls_security_level = encrypt

Finally re-build configs and start/restart postfix:

.. code-block:: bash

    sudo postmap hash:/etc/postfix/sasl_passwd
    sudo systemctl restart postfix.service
    sudo systemctl enable postfix

Everything should work now. Test it out with:

.. code-block:: bash

    # On Fedora:
    sudo dnf install mailx
    # On Debian:
    sudo apt-get install bsd-mailx

    mail -s "Test Email $(date)" RECIPIENT@gmail.com <<< "This is a test email."

Forward Root Email
==================

Now that we've got Postfix successfully sending out email we need to configure the system to forward all of root's mail
to your email address. Things like failed root cronjobs and other system-related mails will be forwarded to you.

First update ``/etc/aliases`` with the following at the bottom:

.. code::

    root:   RECIPIENT@gmail.com

Then run ``newaliases`` to apply changes and run the mail command to test.

.. code-block:: bash

    sudo newaliases
    mail -s "Test Email for Root $(date)" root <<< "This is a test email."

Within a couple of minutes you should have received an email.

Comments
========

.. disqus::

.. _local mail spool: http://superuser.com/questions/306163/what-is-the-you-have-new-mail-message-in-linux-unix
