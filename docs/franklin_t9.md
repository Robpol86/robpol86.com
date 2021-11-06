# T-Mobile Franklin T9 Hacking

My goal for this project is to have an LTE hot spot in my car that shuts off automatically when I get home to avoid wasting
data. I'll be using it with [Google Fi](https://fi.google.com/) (using APN **h2g2**) to avoid paying any monthly fees for
another "line".

## Downgrade Firmware

I bought my unit from a seller on eBay brand new locked to the T-Mobile network (which is fine, Google Fi is a T-Mobile MVNO)
for $37 in November 2021. Sadly it came with firmware `R717F21.FR.2602` which removed the hidden menus. Thankfully someone
figured out how to downgrade this.

Follow these instructions to downgrade to firmware `R717F21.FR.1311`:
https://snt.sh/2021/09/rooting-the-t-mobile-t9-franklin-wireless-r717-again/

For me, once I downgraded the firmware the hot spot could no longer get service even though the Google Fi data-only SIM
wasn't removed. The only fix I found was to upgrade the firmware to a more recent version. Firmware `R717F21.FR.2000` fixed
the issue and still has the hidden pages. Download `R717F21.FR.2000_ota_update_all.enc` from:
https://mega.nz/folder/FJ8wWYAJ#Q1oUEtIUJrtjB1atkOAXrA

(Got that link from:
https://www.howardforums.com/showthread.php/1921612-Franklin-T9-Test-Drive-stuck-on-Welcome-This-is-the-fix)

## SSH and Root

After downgrading the firmware the next step is to enable SSH access so I can log in as root and have full control. These
steps came from: https://snt.sh/2020/09/rooting-the-t-mobile-t9-franklin-wireless-r717/

Download current configuration
: * Go to http://192.168.0.1/settings/device-backup_and_restore.html
  * Click on **Back Up Now**
  * Save the downloaded file as **hotspot_cfg.bin**

Unpack the configuration file
:   ```bash
    # Decrypt.
    openssl enc -aes-128-cbc -d -k "frkenc##KEY@R717" -md md5 -in hotspot_cfg.bin -out hotspot_cfg.tgz
    # Extract nested tar.gz files.
    mkdir -p hotspot_cfg/hotspot_cfg
    tar -xzf hotspot_cfg.tgz -C hotspot_cfg
    tar -xzf hotspot_cfg/hotspot_cfg.tar -C hotspot_cfg/hotspot_cfg
    ```

Edit hotspot_cfg/hotspot_cfg/data/configs/mobileap_cfg.xml
: * Look for **&lt;Ssh>0&lt;/Ssh>** and change it to **1**

Repack the configuration file
:   ```bash
    # Package inner tar.gz file.
    tar -czf hotspot_cfg/hotspot_cfg.tar -C hotspot_cfg/hotspot_cfg .
    rm -r hotspot_cfg/hotspot_cfg
    # Update hash from new inner tar.gz file.
    openssl dgst -md5 < hotspot_cfg/hotspot_cfg.tar |awk '{print "hotspot_cfg.tar="$2}' > hotspot_cfg/hashfile
    # Package outer tar.gz file.
    tar -czf hotspot_cfg.tgz -C hotspot_cfg .
    rm -r hotspot_cfg
    # Encrypt.
    openssl enc -aes-128-cbc -k "frkenc##KEY@R717" -md md5 -in hotspot_cfg.tgz -out hotspot_cfg_new.bin
    ```

Upload new configuration file
: * Go back to http://192.168.0.1/settings/device-backup_and_restore.html
  * Select **hotspot_cfg_new.bin** and click on **Restore Now**
  * Visit http://192.168.0.1/webpst/service_setting.html (password {guilabel}`frk@r717`) and confirm SSH is On
  * Finally `ssh root@192.168.0.1` with password {guilabel}`frk9x07`
  * Prevent new firmware from auto-installing by running: `mv /etc/init.d/start_omadm /home/root/`

## Static DHCP

One feature that I need for my project that's missing is static DHCP. I want certain clients to always get the same IP
address without having to configure them to use a static IP (since they also connect to other networks). I enabled this by
running the following commands:

```bash
# Enable dnsmasq conf-dir.
echo "conf-dir=/etc/dnsmasq.d" >> /etc/default/dnsmasq.conf

# Add configuration to separate file (last column optional).
cat > /etc/dnsmasq.d/static_dhcp.conf <<EOF
dhcp-host=bridge0,74:72:f3:90:ef:f6,192.168.0.10,raspberrypi
dhcp-host=bridge0,96:9c:a2:b5:ae:70,192.168.0.11
EOF
```

This survives reboots and user re-configurations from the hot spot web interface.

## Disable WiFi When Home

The main goal of this project is to kick off wireless users when the hot spot sees my home WiFi. I'm accomplishing this by
having a bash script that starts when the hot spot boots and does a WiFi scan every minute looking for my home SSID. When it
sees it the script will turn off the WiFi access point of the hot spot.

It will keep scanning every minute until it no longer sees my home SSID for a couple of scans (sometimes SSIDs intermittently
don't show up). Once that condition is met the script will re-enable the hot spot's WiFi access point.

Save to /etc/default/wifi_toggle
:   ```bash
    HOME_SSID="your home ssid here"
    ```

Save to /usr/bin/wifi_toggle.sh
:   ```{literalinclude} _static/wifi_toggle.sh
    :language: bash
    ```

Save to /etc/init.d/start_wifi_toggle
:   ```{literalinclude} _static/start_wifi_toggle.sh
    :language: bash
    ```

Enable the service
:   ```bash
    chmod +x /usr/bin/wifi_toggle.sh /etc/init.d/start_wifi_toggle
    update-rc.d start_wifi_toggle defaults
    /etc/init.d/start_wifi_toggle start
    ```

## Custom Logos

You can easily change the logo on the little LCD by editing some PNG files. Since my unit is locked to T-Mobile the file to
edit is:

* `/usr/franklin/mwin/resource/image/default/BW/t_mobile_idle_logo.png`

I edited that file using Paint 3D to keep the transparency.

```{image} _static/img/t9_logo.jpg
:alt: Hacked Logo
:width: 100%
```

## Telegraf

TODO make my own init script since theirs doesn't do single instance. Also telegraf wasn't sending data.

Build and copy telegraf
:   ```bash
    git clone -b franklin_t9 https://github.com/Robpol86/telegraf.git
    cd telegraf
    GOARCH=arm GOARM=7 GOOS=linux LDFLAGS="-s -w" make all
    upx --best --lzma telegraf
    scp telegraf root@192.168.0.1:/data/
    ```

Save to /etc/default/telegraf
:   ```bash
    INFLUX_BUCKET="replace me"
    INFLUX_ORG="replace me"
    INFLUX_TOKEN="replace me"
    INFLUX_URL="https://us-west-2-1.aws.cloud2.influxdata.com"
    STDOUT=/dev/null
    STDERR=/dev/null
    ```

Save to /etc/telegraf/telegraf.conf
:   ```{literalinclude} _static/telegraf_t9.conf
    :language: toml
    ```

Enable the service
:   ```bash
    # Verify telegraf runs.
    /data/telegraf --config /etc/telegraf/telegraf.conf --test
    # Permissions.
    addgroup telegraf
    adduser -H -S -s /bin/false telegraf telegraf
    chown telegraf /etc/default/telegraf
    chmod 0640 /etc/default/telegraf
    # Install the init script.
    wget https://raw.githubusercontent.com/influxdata/telegraf/master/scripts/init.sh -O /etc/init.d/start_telegraf
    chmod +x /etc/init.d/start_telegraf
    ln -s /data/telegraf /usr/bin/telegraf
    # Start.
    update-rc.d start_telegraf defaults
    /etc/init.d/start_telegraf start
    ```

## Comments

```{disqus}
```
