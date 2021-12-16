# Installing Windows 11 on a Mac

This guide lays out the steps I take to install Windows 11 on my Apple computers using a custom ISO. This allows me to bypass
the current TPM 2.0 requirement, since at this time Boot Camp does not provide TPM 2.0 to Windows.

## Create ISO

```{imgur} 1J45UMB
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
    hdiutil makehybrid Win10_21H1_English_x64.iso -hfs -o Win10_To_11.dmg
    hdiutil resize -size 6g Win10_To_11.dmg
    hdiutil attach Win10_To_11.dmg -readwrite -mountpoint /Volumes/Win10_To_11
    ```

Copy the payload file from the Windows 11 ISO into the temporary image
:   ```bash
    chmod +w /Volumes/Win10_To_11/sources
    rm -fv /Volumes/Win10_To_11/sources/install.wim
    cp -v /Volumes/Win11/sources/install.wim /Volumes/Win10_To_11/sources/
    ```

Unmount and convert the temporary image file into the final Boot Camp ISO file
:   ```bash
    hdiutil detach /Volumes/Win10_To_11
    hdiutil makehybrid Win10_To_11.dmg -udf -iso -eltorito-specification "( \
        {no-emul-boot = 1; boot-load-size = 8; eltorito-boot = boot/etfsboot.com;}, \
        {no-emul-boot = 1; boot-load-size = 2880; eltorito-boot = efi/microsoft/boot/efisys.bin; eltorito-platform = 0xEF;} \
        )" -o Win11_English_x64v1_Boot_Camp.iso
    ```

Clean up
:   ```bash
    rm -v Win10_To_11.dmg
    hdiutil detach /Volumes/Win11
    ```

```{admonition} For the Curious
:class: seealso

* The `eltorito-specification` string is a NeXTSTEP plist defining the boot catalog. This isn't needed when using the ISO
  exclusively with Boot Camp, but it's needed to make the ISO properly bootable in both traditional BIOS and modern EFI
  non-Apple computers. This way you can use the same ISO with virtual machines on hosts without TPM 2.0.
* `boot-load-size` was derived from the eltorito-boot file size in bytes divided by the 512 byte sector size.
* I found the value of `eltorito-platform` by doing a diff of the [dumpet](https://github.com/rhboot/dumpet) output.
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

```{admonition} For the Curious
:class: seealso

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

## Tweaks and Software

This section is mainly for my own reference. It's the usual software and configuration I use on most of my Windows machines.

### Registry Settings

Require pressing Ctrl+Alt+Del to log in
:   ```powershell
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /f /v DisableCAD /t REG_DWORD /d 0
    ```

Folder options
:   ```powershell
    $key = "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    # Set new explorer windows' default folder to Downloads (undocumented).
    reg add $key /f /v LaunchTo /t REG_DWORD /d 3
    # Unhide system files and file extensions.
    reg add $key /f /v Hidden /t REG_DWORD /d 1
    reg add $key /f /v HideFileExt /t REG_DWORD /d 0
    # Other folder options.
    reg add $key /f /v UseCompactMode /t REG_DWORD /d 1
    reg add $key /f /v SeparateProcess /t REG_DWORD /d 1
    ```

Always default folder types to "Documents" instead of unpredictably opening in videos/images/etc. modes
:   ```powershell
    $pfx = "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell"
    reg delete "$pfx\Bags" /f
    reg delete "$pfx\BagMRU" /f
    reg add "$pfx" /f /v "BagMRU Size" /t REG_DWORD /d 10000
    reg add "$pfx\Bags\AllFolders\Shell" /f /v FolderType /d Documents
    ```

Fix default explorer search bar size and default folder view sorting and columns
:   ```powershell
    $pfx = "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell"
    reg add "$pfx\Bags\AllFolders\Shell" /f /v NavBar /t REG_BINARY /d 000000000000000000000000000000008b000000870000003153505305d5cdd59c2e1b10939708002b2cf9ae6b0000005a000000007b00360044003800420042003300440033002d0039004400380037002d0034004100390031002d0041004200350036002d003400460033003000430046004600450046004500390046007d005f0057006900640074006800000013000000960000000000000000000000
    $key = "$pfx\Bags\AllFolders\Shell\{7D49D726-3C21-4F05-99AA-FDC2C9474656}"
    reg add $key /f /v ColInfo /t REG_BINARY /d 00000000000000000000000000000000fddfdffd100000000000000000000000040000001800000030f125b7ef471a10a5f102608c9eebac0a0000001001000030f125b7ef471a10a5f102608c9eebac0c0000005000000030f125b7ef471a10a5f102608c9eebac040000007800000030f125b7ef471a10a5f102608c9eebac0e00000090000000
    reg add $key /f /v GroupByDirection /t REG_DWORD /d 1
    reg add $key /f /v GroupByKey:FMTID /d "{00000000-0000-0000-0000-000000000000}"
    reg add $key /f /v GroupByKey:PID /t REG_DWORD /d 0
    reg add $key /f /v GroupView /t REG_DWORD /d 0
    reg add $key /f /v Mode /t REG_DWORD /d 4
    reg add $key /f /v Sort /t REG_BINARY /d 000000000000000000000000000000000100000030f125b7ef471a10a5f102608c9eebac0a00000001000000
    # Restart explorer.
    taskkill /f /im explorer.exe; explorer.exe
    ```

### Remove Bloat

```powershell
Get-ProvisionedAppxPackage -online |
    Where-Object { $_.DisplayName -like "Microsoft.Xbox*" -or $_.DisplayName -eq "Microsoft.GamingApp" } |
    ForEach-Object { Remove-ProvisionedAppxPackage -online -allusers -PackageName $_.PackageName }

Get-AppxPackage -allusers -name Microsoft.549981C3F5F10 |Remove-AppxPackage -allusers  # Cortana
Get-AppxPackage -allusers -name Microsoft.BingNews |Remove-AppxPackage -allusers  # Microsoft News
Get-AppxPackage -allusers -name Microsoft.GetHelp |Remove-AppxPackage -allusers  # Get Help
Get-AppxPackage -allusers -name Microsoft.Getstarted |Remove-AppxPackage -allusers  # Tips
Get-AppxPackage -allusers -name Microsoft.MicrosoftOfficeHub |Remove-AppxPackage -allusers  # Office
Get-AppxPackage -allusers -name Microsoft.MicrosoftStickyNotes |Remove-AppxPackage -allusers  # Sticky Notes
Get-AppxPackage -allusers -name Microsoft.Todos |Remove-AppxPackage -allusers  # Microsoft To Do
Get-AppxPackage -allusers -name Microsoft.WindowsCommunicationsApps |Remove-AppxPackage -allusers  # Mail and Calendar
Get-AppxPackage -allusers -name Microsoft.WindowsFeedbackHub |Remove-AppxPackage -allusers  # Feedback Hub
Get-AppxPackage -allusers -name Microsoft.WindowsMaps |Remove-AppxPackage -allusers  # Maps
Get-AppxPackage -allusers -name Microsoft.YourPhone |Remove-AppxPackage -allusers  # Your Phone
Get-AppxPackage -allusers -name Microsoft.ZuneMusic |Remove-AppxPackage -allusers  # Groove Music
Get-AppxPackage -allusers -name Microsoft.ZuneVideo |Remove-AppxPackage -allusers  # Movies & TV
Get-AppxPackage -allusers -name MicrosoftTeams |Remove-AppxPackage -allusers  # Microsoft Teams
```

Afterwards I had to reboot to get the Microsoft Store to sync.

### Software

```{attention} Update all packages in the Microsoft Store Library first.
```

`winget install --name "Windows Subsystem for Linux" -s msstore`
:   * `DISM /online /enable-feature /featurename:VirtualMachinePlatform`
    * `Set-Service -StartupType Automatic ssh-agent`
    * `Start-Service ssh-agent`
    * `wsl --install Ubuntu`
    * `sudo apt-get update && sudo apt-get install -y zsh`
    * https://github.com/Robpol86/dotfiles
    * https://gist.github.com/Robpol86/3d4730818816f866452e
    ```bash
    sudo ln -s /usr/bin/wslview /usr/bin/open
    ```

`winget install -e --id Docker.DockerDesktop`
:   * Reboot
    * Launch Docker Desktop > Settings > General
        * Start Docker Desktop when you log in: **Uncheck**
        * Open Docker Dashboard at startup: **Uncheck**

`winget install -e --id Microsoft.PowerToys -s winget`
:   * Keyboard Manager > Remap a key
        * {kbd}`Caps Lock` -> {kbd}`Esc`
    * PowerRename > Use Boost library: **On**

`winget install -e --id Microsoft.VisualStudioCode`
:   * Enable Settings Sync
        * Sign in with Microsoft

`winget install -e --id JetBrains.PyCharm.Professional`
:   * Open project > File > Manage IDE Settings
        * Sync Settings to JetBrains Account > Get Settings from Account

## Comments

```{disqus}
```
