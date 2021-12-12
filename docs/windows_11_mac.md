# Installing Windows 11 on a Mac

This guide lays out the steps I take to install Windows 11 on my Apple computers using a custom ISO. This allows me to bypass
the current TPM 2.0 requirement, since at this time Boot Camp does not provide TPM 2.0 to Windows.

## Create ISO

```{imgur} hwUiK7j
:ext: png
```

| File Name                  | sha1sum / Get-FileHash -Algorithm SHA1   |
| -------------------------- | ---------------------------------------- |
| Win10_21H1_English_x64.iso | 78AA5FA0FD332EE0822EF5A533CD2CFE12333274 |
| Win11_English_x64v1.iso    | 9CBBB18B244511BF1D4C68A33FE6EE35D2EDA2AE |

The key ingredient in this guide is the custom ISO we'll be creating. Essentially it's a Windows 10 ISO, but with the payload
file being replaced with the one from Windows 11. Think of it as the Windows 10 installer installing Windows 11 for you.

You'll need to download the [Windows 11 ISO](https://www.microsoft.com/software-download/windows11) as well as a
[Windows 10 ISO](https://www.microsoft.com/en-us/software-download/windows10). The table above shows the files I used at the
time of writing. To create the custom ISO follow these steps:

Mount the Windows 11 ISO
:   ```bash
    hdiutil attach Win11_English_x64v1.iso -mountpoint /Volumes/Win11
    ```

Convert the Windows 10 ISO to a temporary writable image and mount it
:   ```bash
    hdiutil makehybrid -hfs -o Win10_To_11.dmg Win10_21H1_English_x64.iso
    hdiutil resize -size 6g Win10_To_11.dmg
    hdiutil attach Win10_To_11.dmg -readwrite -mountpoint /Volumes/Win10_To_11
    ```

Copy the payload file from the Windows 11 ISO into the temporary image
:   ```bash
    chmod +w /Volumes/Win10_To_11/sources
    rm /Volumes/Win10_To_11/sources/install.wim
    cp /Volumes/Win11/sources/install.wim /Volumes/Win10_To_11/sources/
    ```

Unmount and convert the temporary image file into the final Boot Camp ISO file
:   ```bash
    hdiutil detach /Volumes/Win10_To_11
    hdiutil makehybrid -iso -udf -o Win11_English_x64v1_Boot_Camp.iso Win10_To_11.dmg
    ```

Clean up
:   ```bash
    rm Win10_To_11.dmg
    hdiutil detach /Volumes/Win11
    ```

## Install

```{list-table}
* - ```{imgur-figure} TjJUZ4T
    :ext: png
    Boot Camp Assistant
    ```
  - ```{imgur-figure} gF0n0oK
    :ext: png
    Installing Windows 11
    ```
  - ```{imgur-figure} Cvx57Ac
    :ext: png
    Boot Camp Drivers
    ```
```

This step is pretty straightforward. You follow the same steps as you would when installing Windows 10 on your Mac.

1. Run the **Boot Camp Assistant** and choose the ISO you've just created.
2. Since I plan on removing macOS at the end I gave all the space I could to the Windows partition.
3. Your Mac should automatically reboot into the Windows installer.
4. After Windows 11 boots up the Boot Camp software installer should auto start to install drivers. Finish setting that up
   and reboot.
5. If you plan on removing macOS don't enable BitLocker yet.

```{tip}
In case you were wondering how I took screen shots during the Windows installation:

1. Downloaded [NirCmd](https://www.nirsoft.net/utils/nircmd.html) onto an SD card and inserted it into my MacBook.
1. Pressed {kbd}`Shift+F10` to bring up a cmd.exe window.
1. Ran `diskpart` then `LIST VOLUME` to find the SD card was mounted as {guilabel}`C:`.
1. From {guilabel}`C:` I ran: `nircmd savescreenshot screen.png`
```

## Remove macOS

```{list-table}
* - ```{imgur-figure} 58oJm7t
    :ext: png
    Before Repartitioning
    ```
  - ```{imgur-figure} gPd6laP
    :ext: png
    After Repartitioning
    ```
```

This optional last step walks you through removing the macOS partition so your Windows installation can use the full capacity
of your SSD. We'll be using [MiniTool Partition Wizard Free](https://www.partitionwizard.com/free-partition-manager.html) to
do the repartitioning from Windows.

1. Install and open MiniTool.
2. You should see four partitions, remove the middle two ({guilabel}`*:` and {guilabel}`*:OSXRESERVED`) so that only
   {guilabel}`*:EFI` and {guilabel}`C:BOOTCAMP` remains.
3. Resize {guilabel}`C:BOOTCAMP` to use up the empty space left by step 2.
4. Apply and reboot.

## BitLocker

```{list-table}
* - ```{imgur-figure} EKbY5zv
    :ext: png
    Use gpedit.msc to disable the TPM check
    ```
  - ```{imgur-figure} I6XTevu
    :ext: png
    Now you can enable BitLocker
    ```
  - ```{imgur-figure} mop8gO7
    :ext: png
    This error is expected
    ```
```

I always enable BitLocker full disk encryption on all of my machines. This is what I do to enable it on Macs (steps taken
from: https://www.howtogeek.com/howto/6229/how-to-use-bitlocker-on-drives-without-tpm/).

* Run as Administrator: `gpedit.msc`
  * Computer Configuration
    * Administrative Templates
      * Windows Components
        * BitLocker Drive Encryption
          * Operating System Drives
            * **Require additional authentication at startup**

Once you follow the above steps you'll want to:

1. Select **Enabled**
2. Make sure checkbox is checked: **Allow BitLocker without a compatible TPM**
3. Leave subsequent fields configured to: **Allow ...**
4. Click OK

Now you can enable BitLocker the usual way.

## Restore macOS

```{list-table}
* - ```{imgur-figure} ICGyjGt
    Main Menu
    ```
  - ```{imgur-figure} sDNXbxm
    Erase the SSD
    ```
```

If you ever want to get your Mac back to macOS you can use the built-in "Internet Recovery" mode to download the latest macOS
over the internet and remove Windows.

1. Power off the Mac.
2. Power on whilst holding {kbd}`Command+Option+R` or {kbd}`Win+Alt+R` and connect to WiFi.
3. It will start Internet Recovery mode. It should take about 10 minutes to load depending on your internet connection.
4. When you get to the main menu select **Disk Utility**.
5. Show all devices (under the View menu) and erase your SSD. I chose to format my SSD as APFS with GUID Partition Map.
6. Then close Disk Utility and proceed with "Reinstall macOS".

## Comments

```{disqus}
```
