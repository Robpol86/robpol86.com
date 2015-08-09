.. _imagecfg:

========
ImageCFG
========

.. note::

    I've been hosting this file
    `since before 2003 <https://web.archive.org/web/20031203173758fw_/http://www.robpol86.com/tutorials/imagecfg.php>`_.
    Too bad I don't have a copy of an older version of this page.


ImageCFG is a utility that probably does a lot of things (I cannot find any official documentation), but the only reason
I use it is to fix old games (UT99 for example) which have problems on multicore/multicpu systems. It does so by
assigning an executable to specific logical CPUs permanently (by modifying the .exe file, so backup the original in case
you want to restore it).

This utility will work in pretty much any modern Windows operating system (2000/XP/Vista/7) and it is meant to be used
on computers with multiple CPUs, multiple cores, or Hyper Threading.

History
=======

Many years ago, sometime in 2001 or 2002, I was looking for a utility that would permanently set which CPU a program
would run under. To my dismay checking the affinity boxes in the task manager was only temporary, and unless I set the
affinity of tribes2.exe to one CPU instead of both, my dual Pentium III Windows XP computer would blue screen (it turned
out a faulty VP6 motherboard and dissimilar CPUs were to blame).

After many days of searching the internet and Direct Connect, I finally found the utility. While searching I noticed a
lot of other people looking for the same tool, so at that time I decided to host the tool and make it easy for anyone to
find. Since it's a small tool that hardly takes up disk space or bandwidth, I have decided to keep hosting this file
indefinitely.

Usage
=====

ImageCFG will work from any directory, but for ease of use it can be placed in **%systemroot%\system32** (or
C:\Windows\system32 or C:\Windows\SysWOW64 (thanks chris.xudo333) if system32 doesn't work) and
**%systemroot%\system32\dllcache** (or C:\Windows\system32\dllcache). Doing so will make ``imagecfg`` a system command
(run it from anywhere in any cmd window or the run dialog). This article assumes you have done so.

The ``-u`` option sets a specified executable to only run in "uni-processor" mode on multi-processor systems. This is
probably optional but I run it anyways.

The ``-a`` option sets a process affinity mask (hexadecimal value) to the specified executable, so that it always runs
using the specified CPU. You can also add up the bits to set multiple CPUs (thanks LigH). Examples (hex = decimal =
CPU):

* 0x01 = 1 = CPU0
* 0x02 = 2 = CPU1
* 0x04 = 4 = CPU2
* 0x08 = 8 = CPU3
* 0x10 = 16 = CPU4
* 0x20 = 32 = CPU5
* 0x40 = 64 = CPU6
* 0x80 = 128 = CPU7
* 0x0f = 15 = CPU0, CPU1, CPU2, and CPU3 (1+2+4+8 = 15)

Examples
========

The following examples will use UT99 from Steam to fix the speed issues I have been experiencing on my FX-60 (AMD
dual core) computer running Windows 7 Ultimate 64bit.

This first command is probably optional. It sets the exe to use only one CPU:

.. code-block:: bat

    imagecfg -u "C:\Program Files (x86)\Steam\steamapps\common\unreal tournament\System\unrealtournament.exe"

This is the important one. It sets the exe to use CPU0:

.. code-block:: bat

    imagecfg -a 0x1 "C:\Program Files (x86)\Steam\steamapps\common\unreal tournament\System\unrealtournament.exe"

Download
========

:download:`You can download ImageCFG from here. <Imagecfg.zip>`

Comments
========

.. disqus::
