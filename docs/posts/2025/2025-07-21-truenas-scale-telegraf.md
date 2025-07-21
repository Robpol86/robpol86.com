---
blogpost: true
date: 2025-07-21
author: Robpol86
location: Melbourne
category: Tutorials
tags: homelab, nas
---

# TrueNAS Telegraf, Influx, Grafana

```{list-table}
* - :::{imgur} UZEhmk5
  - :::{imgur} 8HI9Usi
* - :::{imgur} u1VnBj4
  - :::{imgur} EuNZltU
```

This guide will explain how to run Telegraf on TrueNAS SCALE, as well as running InfluxDB and Grafana apps to collect metrics
and show graphs. This is how I run all three apps on my
[Beelink Me Mini](https://www.bee-link.com/products/beelink-me-mini-n150) NAS. As of this writing I'm running TrueNAS SCALE
25.04.1 (Fangtooth).

## Prerequisites

Before starting there are a few things we need to setup:

1. Choose a pool for apps if you haven't used apps in TrueNAS before
1. Create datasets for each application

### Choose a Pool

For this guide we're using **Vault** as the pool. To enable apps in TrueNAS:

1. In the TrueNAS UI go to ➡️ Apps
1. Click on **Configuration** and then **Choose Pool**
1. Select a pool (e.g. Vault)

### Create Datasets

Next we'll be creating a few datasets. We'll create a dataset named **Apps** just for organization, and within it we'll
create datasets for each individual app. This is the structure we'll be using:

```
Vault (pool)
└── Apps
    ├── InfluxDB
    ├── Grafana
    └── Telegraf
```

1. In the TrueNAS UI go to ➡️ Datasets
1. Click on **Vault** then **Add Dataset**
    1. **Name**: Apps
    1. **Dataset Preset**: Apps
    1. Save
1. Click on the new **Apps** dataset then **Add Dataset** again
    1. **Name**: InfluxDB
    1. **Dataset Preset**: Apps
    1. Save
    1. Return to Pool List
    1. *Repeat for Grafana and Telegraf*

```{imgur-figure} TODO
You should now see something like this.
```

## InfluxDB

I use [InfluxDB](https://www.influxdata.com/) version 1 as the timeseries database to store all my metrics. Because the
official InfluxDB TrueNAS app [uses v2](https://apps.truenas.com/catalog/influxdb/) I'm deploying mine as a custom app. If
you'd rather run the official app feel free to use it instead and skip to the [Telegraf](#telegraf) section of this guide.

```{note}
I'm running v1 because the latest version (as of this writing it's v3) has an absurd 3-day data limit for the free license
(lol). It also removed Flux (lol). I guess I could have gone with v2 but it looks like enabling InfluxQL requires additional
steps. I don't want to rewrite all of my Grafana dashboard's queries in a dead language and nothing's wrong with v1 so I've
decided to stick with that.
```

1. In the TrueNAS UI go to ➡️ Apps
1. Click on **Discover Apps**
1. Click on "⋮" menu button then **Install via YAML**
    1. **Name**: influxdb
    1. **Custom Config**: *paste the following; change "Vault" to your pool name*
        ```yaml
        services:
          influxdb:
            hostname: influxdb
            # 1.11.8 is the latest version of v1
            image: influxdb:1.11.8
            pull_policy: always
            restart: always
            environment:
              # Without this you can read/write to InfluxDB without a password
              INFLUXDB_HTTP_AUTH_ENABLED: "true"
              # Allows you to use Flux in your Grafana queries
              INFLUXDB_HTTP_FLUX_ENABLED: "true"
            ports:
            - mode: ingress
              protocol: tcp
              published: 8086
              target: 8086
            # This is the UID for the "apps" user in TrueNAS
            user: "568:568"
            # Change "Vault" to your pool name
            volumes: [/mnt/Vault/Apps/InfluxDB:/var/lib/influxdb]
        ```

```{imgur-figure} TODO
After you click "Save" you should see something like this.
```

### InfluxDB Configuration

Now that InfluxDB is running it's time to configure it.

1. In the TrueNAS UI go to ➡️ Apps
1. Click on the running **influxdb** application
1. Under "Workloads" next to "influxdb - Running" click the command line icon to shell into the container
1. Run the command `influx` and then execute these queries to create the **admin** user:
    ```sql
    CREATE USER admin WITH PASSWORD 'REPLACE_ME' WITH ALL PRIVILEGES
    AUTH
    ```
1. Then run these queries to create the telegraf database and the user which Telegraf will use:
    ```sql
    CREATE DATABASE telegraf
    CREATE USER truenas WITH PASSWORD 'REPLACE_ME'
    GRANT WRITE ON telegraf TO truenas
    ```
1. Finally run these queries to create the user Grafana will use:
    ```sql
    CREATE USER grafana WITH PASSWORD 'REPLACE_ME'
    GRANT READ ON telegraf TO grafana
    ```

:::{tip}
You can ignore this error:

```
There was an error writing history file: open /.influx_history: permission denied
```

After a while it becomes annoying. You can avoid it by running `HOME= influx` instead of just `influx`.
:::

## Telegraf

Most guides and posts on the internet show how to run Telegraf from a Docker container with `/sys` and other filesystems
mounted as well as running in privileged mode. I personally don't like that approach, so instead I just run Telegraf as root
on "bare metal" (as in not in a container or in a VM).

```{warning}
Running Telegraf on bare metal is not officially supported by TrueNAS. This implementation may stop working on future
versions of TrueNAS SCALE if they stop including the commands we need.
```

To get started download three files and save them in `/mnt/Vault/Apps/Telegraf/`:

1. [telegraf.conf](/_static/telegraf.conf) unmodified
1. [telegraf.env](/_static/telegraf.env) with "REPLACE_ME" replaced
    - Use the telegraf password you used in the [InfluxDB Configuration](#influxdb-configuration)
  section in place of REPLACE_ME
1. `telegraf` from the latest [amd64 Linux](https://github.com/influxdata/telegraf/releases) release
    - Extract the tar.gz file and look for the `telegraf` file in `usr/bin`

:::{hint}
If you run `ls -lah /mnt/Vault/Apps/Telegraf` you should see something like this:

```
total 119M
drwxrwx--- 2 root          root    5 Jul 21 21:59 .
drwxrwx--- 5 root          root    5 Jul  4 15:47 ..
-rwxrwx--- 1 truenas_admin root   44 Jul  4 16:00 env
-rwxrwx--- 1 truenas_admin root 279M Jul  4 16:00 telegraf
-rwxrwx--- 1 truenas_admin root 2.2K Jul  6 19:42 telegraf.conf
```
:::

TODO systemd-run

TODO alerts with health endpoint

```bash
## Download from https://github.com/influxdata/telegraf/releases on macOS, then:
scp ~/Downloads/telegraf-1.35.1/usr/bin/telegraf truenas_admin@10.192.168.10:/mnt/Vault/Apps/Telegraf/
```

➡️ System > Advanced Settings > Init/Shutdown Scripts > Add

1. **Description**: Telegraf
1. **When**: Post Init

```bash
/bin/systemd-run --no-block --unit telegraf -p User=root -p Restart=always -p RestartSec=30 -p EnvironmentFile=/mnt/Vault/Apps/Telegraf/telegraf.env /mnt/Vault/Apps/Telegraf/telegraf --config /mnt/Vault/Apps/Telegraf/telegraf.conf
```

Then reboot.

### Configure TrueNAS Graphite Exporter

➡️ Reporting > Exporters > Add

1. **Name**: Telegraf
1. **Type**: GRAPHITE
1. **Destination IP**: localhost
1. **Destination Port**: 2003
1. **Prefix**: graphite
1. **Namespace**: truenas_reporting
1. **Update Every**: 50

### Alerts

➡️ System > Advanced Settings > Cron Jobs > Add

1. **Description**: Telegraf Alerts
1. **Run As User**: root
1. **Schedule**: `*/10 * * * *`
1. **Hide Standard Output/Error**: Uncheck

```bash
(curl -sSf http://localhost:12121 -o /dev/null || journalctl --since "1 minute ago" -u telegraf)
```

## Grafana


➡️ Apps > Discover Apps > ... > Install via YAML

1. **Name**: grafana
1. **Custom Config**: *paste app-grafana.yaml*

```yaml
services:
  grafana:
    hostname: grafana
    image: grafana/grafana:12.0.2
    pull_policy: always
    restart: always
    ports:
      - mode: ingress
        protocol: tcp
        published: 3000
        target: 3000
    user: "568:568"
    volumes: [/mnt/Vault/Apps/Grafana:/var/lib/grafana]
x-portals:
  - host: 0.0.0.0
    name: Grafana UI
    path: /
    port: 3000
    scheme: http
```

➡️ Apps > grafana > Application Info > Grafana UI

1. Login with admin/admin
    1. Set new password
1. Connections > Data sources > Add data source > InfluxDB
    1. **URL**: http://172.16.0.1:8086
    1. Basic Auth Details > **User**: grafana
    1. InfluxDB Details > **Database**: telegraf
1. Dashboards > New > Import
    1. Browse to [grafana.json](/_static/grafana.json)
    1. **Select a InfluxDB data source**: influxdb
    1. Upper right avatar > Profile > Preferences
        1. **Home Dashboard**: Dashboards/TNAS
