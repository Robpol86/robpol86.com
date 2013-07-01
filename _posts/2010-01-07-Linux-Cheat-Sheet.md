---
layout: post
title: Linux Cheat Sheet
description: "Computer Notes/One Liners for Linux"
modified: 2013-04-30
category: cheatsheet
tags: [cheat sheet, linux, unix, sunos, vmware, esx]
comments: true
showseries: true
---

# Command Line

{% highlight bash %}
ip a
{% endhighlight %}

{% highlight bash %}
sshfs
{% endhighlight %}

{% highlight bash %}
knockd
{% endhighlight %}

{% highlight bash %}
ssh-copy-id
{% endhighlight %}

{% highlight bash %}
strings
{% endhighlight %}

{% highlight bash %}
at
{% endhighlight %}

{% highlight bash %}
service iptables save
{% endhighlight %}

{% highlight bash %}
netstat -tulpn
{% endhighlight %}

{% highlight bash %}
mutt
{% endhighlight %}

{% highlight bash %}
alternatives --config
{% endhighlight %}

{% highlight bash %}
/etc/aliases
{% endhighlight %}

{% highlight bash %}
grep --color
{% endhighlight %}

{% highlight bash %}
shopt -s histappend
{% endhighlight %}

{% highlight bash %}
for ((i=0; i <= 10 ; i++)); do echo $i; done
{% endhighlight %}

# Flush DNS Cache

This fixed the weird problem where ping couldn't resolve hostnames but dig/host/wget could.

{% highlight bash %}
service nscd reload
{% endhighlight %}

# Dump HTTP Payload

{% highlight bash %}
tcpdump -i eth0 -s 0 -A 'tcp dst port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354)'
{% endhighlight %}

# Convert TIFs to JPGs

{% highlight bash %}
mkdir convert &>/dev/null; for file in $(ls *.tif); do file_new="./convert/$(echo $file |sed "s/tif$/jpg/g")"; convert $file $file_new; exiftool -tagsFromFile $file $file_new; done
{% endhighlight %}

# Find Duplicate Files

{% highlight bash %}
data=$(find . -type f -exec cksum {} \; |sort); data_uniq=$(echo -e "$data" |cut -d" " -f1 |uniq -d); for line in $(echo -e "$data_uniq"); do echo; echo -e "$data" |grep $line; done
{% endhighlight %}

# Fattest Directories

{% highlight bash %}
sudo du -s /home /tmp /root |sort -nr |awk '{print $2}' |xargs sudo du -hs
{% endhighlight %}

# Bash Colors

[https://wiki.archlinux.org/index.php/Color_Bash_Prompt](https://wiki.archlinux.org/index.php/Color_Bash_Prompt)

{% highlight bash %}
txtblk='\e[0;30m' # Black - Regular
txtred='\e[0;31m' # Red
txtgrn='\e[0;32m' # Green
txtylw='\e[0;33m' # Yellow
txtblu='\e[0;34m' # Blue
txtpur='\e[0;35m' # Purple
txtcyn='\e[0;36m' # Cyan
txtwht='\e[0;37m' # White
bldblk='\e[1;30m' # Black - Bold
bldred='\e[1;31m' # Red
bldgrn='\e[1;32m' # Green
bldylw='\e[1;33m' # Yellow
bldblu='\e[1;34m' # Blue
bldpur='\e[1;35m' # Purple
bldcyn='\e[1;36m' # Cyan
bldwht='\e[1;37m' # White
unkblk='\e[4;30m' # Black - Underline
undred='\e[4;31m' # Red
undgrn='\e[4;32m' # Green
undylw='\e[4;33m' # Yellow
undblu='\e[4;34m' # Blue
undpur='\e[4;35m' # Purple
undcyn='\e[4;36m' # Cyan
undwht='\e[4;37m' # White
bakblk='\e[40m'   # Black - Background
bakred='\e[41m'   # Red
badgrn='\e[42m'   # Green
bakylw='\e[43m'   # Yellow
bakblu='\e[44m'   # Blue
bakpur='\e[45m'   # Purple
bakcyn='\e[46m'   # Cyan
bakwht='\e[47m'   # White
txtrst='\e[0m'    # Text Reset
{% endhighlight %}

# MD

#### Replace RAID Disk

In this example, the scenario is /dev/sdd will be replaced with a larger capacity drive. NOTE: To see drive sizes: **cat /proc/partitions \|grep sd.1$**

* fdisk drive and partition as **fd** (Linux raid auto)
* To get current state: **mdadm --detail /dev/md0**
* Add the newly formatted partition to the array: **mdadm /dev/md0 -a /dev/sdd1**
* Array will rebuild in the background: **watch -n1 sudo mdadm --detail /dev/md0**

#### Add RAID Disk

The scenario is that a new disk (5) will be added to the array, the device is /dev/sde.

* fdisk drive and partition as **fd** (make sure all devices are the same type with **fdisk -l**)
* Add the newly formatted partition to the array: **mdadm /dev/md0 -a /dev/sdd1** (this will add it as a hot spare)
* Find out the current number of active disks: **mdadm --detail /dev/md0** (Active Devices)
* Increment the number of active devices by one: **mdadm --grow -n5 /dev/md0** (was 4, now 5) (with 5x1TB drives, this took 24 hours)
* Update **/etc/mdadm.conf** by replacing the ARRAY line with the output of **mdadm -Es**

#### Grow RAID Device

NOTE: This section assumes you have the following drive layout: MD (linux software raid) -> LUKS (linux software full disk encryption encompassing the entire MD device) -> LVM (sitting directly on top of LUKS/dm-crypt).

After increasing the size of all hard disks, or adding another hard disk, do the following. The encrypted file system name was obtained from PV Name (/dev/mapper/luks-[...]) in **/usr/sbin/pvdisplay**

* Grow the multi-disk device: **mdadm --grow --size=max /dev/md0** (not necessary but doesn't hurt if md0 is already max)
* Grow the encrypted file system: **cryptsetup resize luks-5c9f9294-5a3c-4e5a-8180-f00821fecc46**
* Resize the LVM PV: **pvresize /dev/mapper/luks-5c9f9294-5a3c-4e5a-8180-f00821fecc46**
* Run **vgdisplay** to verify the new VG Size, and get the current Free PE. In this example you see: Free PE / Size **95** / 2.97 GB
* Expand the home logical volume: **lvresize -l +95 /dev/vg0/home**
* Verify vgdisplay has 0 free PE, and lvdisplay shows /dev/vg0/home with the new size
* Finally, expand the /home file system: **resize2fs /dev/mapper/vg0-home** (resizing from 3 TB to 4 TB took about an hour)

# NagiosGraph

This is how I got nagiosgraph 1.4.4-1.el6 working on SELinux (CentOS 6.2).

{% highlight bash %}
cat > nagiosgraph.te << EOF
module nagiosgraph 1.0;

require {
    type nagios_t;
    type nagios_log_t;
    class dir create;
}

#============= nagios_t ==============
allow nagios_t nagios_log_t:dir create;
EOF

checkmodule -Mmo nagiosgraph.mod nagiosgraph.te
semodule_package -o nagiosgraph.pp -m nagiosgraph.mod
sudo semodule -i nagiosgraph.pp

sudo chcon -R -t httpd_nagios_script_exec_t /usr/lib/nagiosgraph/cgi-bin
sudo chcon -R -t nagios_log_t /var/log/nagiosgraph
sudo chcon -t httpd_log_t /var/log/nagiosgraph/nagiosgraph-cgi.log
sudo chcon -R -t nagios_log_t /var/spool/nagiosgraph
{% endhighlight %}

I used these commands to help troubleshoot:

{% highlight bash %}
(IFS=$'\n'; for line in $(sudo grep denied /var/log/audit/audit.log |sort |uniq); do echo; echo $line; echo; done) #show all SELinux denied
sudo kill -s SIGUSR1 auditd #force a rotate of the audit log
{% endhighlight %}

# SunOS

#### Non-Truncated PS

{% highlight bash %}
/usr/ucb/ps auxwww
{% endhighlight %}

# VMware ESX 3.5

#### Kill VM with vmid

{% highlight bash %}
killvm() { for a in "$@"; do /usr/lib/vmware/bin/vmkload_app -k 9 $(perl -ne 'print if s/.*vm\.(\d*).*/\1/' /proc/vmware/vm/$a/cpu/status); done; }
{% endhighlight %}

#### Get VMX path from vmid

{% highlight bash %}
function getvmx() { sed 's/.*cfgFile="\([^"]*\)".*/\1/' /proc/vmware/vm/$1/names ;}
{% endhighlight %}

