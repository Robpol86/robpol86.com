---
layout: post
title: Windows Cheat Sheet
description: "Computer Notes/One Liners for Windows"
modified: 2012-12-07
category: cheatsheet
tags: [cheat sheet, windows, putty]
comments: true
showseries: true
share: true
---

# Command Line/Cygwin

#### Convert *.mkv files in folder B:\Videos to *.mp4 files in current folder:

[http://stackoverflow.com/.../how-to-get-folder-path-from-file-path-...](http://stackoverflow.com/questions/659647/how-to-get-folder-path-from-file-path-with-cmd)

{% highlight bat %}
for /r "B:\Videos" %i in (*.mkv) do ffmpeg -i "%i" "%~ni.mp4"
{% endhighlight %}

#### Commands for ripping Dragon Ball DVDs:

{% highlight bat %}
for %i in (t*.mkv) do mkvmerge.exe -o _%i --default-track 2:no --default-track 3:yes --default-track 5:yes -a 2,3 -d 1 -s 5 %i --track-order 0:1,0:3,0:2,0:5
{% endhighlight %}

{% highlight bat %}
for %i in (t*.mkv) do mkvmerge.exe -o _%i --default-track 2:no --default-track 3:yes --default-track 4:yes -a 2,3 -d 1 -s 4 %i --track-order 0:1,0:3,0:2,0:4
{% endhighlight %}

{% highlight bat %}
grep TimeStart source.txt |sed -ne "1~5p" |sed -e "1d" |cut -d" " -f7 |tr "\n" ","
{% endhighlight %}

# PuTTY

[http://dag.wieers.com/blog/content/improving-putty-settings-on-windows](http://dag.wieers.com/blog/content/improving-putty-settings-on-windows)

* Window
    * Lines of scrollback: **2000000**
    * Check only:
        * Display scrollbar
        * Reset scrollback on keypress
        * Push erased text into scrollback
* Window/Appearance
    * Font: Source Code Pro (Regular), 10-point
    * Font quality: **ClearType**
* Window/Translation
    * Character set: **UTF-8**
    * Use Unicode line drawing code points
* Connection
    * Seconds between keepalives: **25**
* Connection/Data
    * Terminal-type string: **xterm-color**

# Videos to DVD

* Install AVStoDVD 2.4.1
* Configure AVStoDVD Labels.ini:
    * TitleFontSize: 30
    * ThumbsFontSize: 15
* Configure AVStoDVD Preferences:
    * DVD Output/Assets Path
    * DVD Video Standard

* Create DVD ISO:
    * Set DVD Label in "Settings".
    * Add files to Source Titles.
    * Set Output to "ISO UDF Image"
    * Create DVD Menu:
        * Still Pictures.
        * Set relevant aspect ratio.
        * Text Based Titles.
        * 5 titles per page.
        * Enable "Play All" Button.
    * Start.
* If ISO is greater than 4450 MB:
    * Use DVD Shrink once or twice on the ISO.

