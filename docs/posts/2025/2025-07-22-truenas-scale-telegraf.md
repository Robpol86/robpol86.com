---
blogpost: true
date: 2025-07-22
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

This guide will explain how to run [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) on
[TrueNAS SCALE](https://www.truenas.com/truenas-scale/), as well as running the [InfluxDB](https://www.influxdata.com/) and
[Grafana](https://grafana.com/oss/grafana/) apps to collect NAS metrics and show graphs. This is how I run all three apps on
my [Beelink Me Mini](https://www.bee-link.com/products/beelink-me-mini-n150) NAS. As of this writing I'm running TrueNAS
SCALE 25.04.1 (Fangtooth).

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

I use [InfluxDB version 1](https://docs.influxdata.com/influxdb/v1/) as the timeseries database to store all my metrics.
Because the official InfluxDB TrueNAS app [uses v2](https://apps.truenas.com/catalog/influxdb/) I'm deploying mine as a
custom app. If you'd rather run the official app feel free to use it instead and skip to the [Telegraf](#telegraf) section of
this guide.

```{note}
I'm running v1 because the latest version (as of this writing it's v3) has an absurd 3-day data limit for the free license
(lol). It also removed Flux (lol). Try as I might I can't find any justifiable reason to use v2. Even the
[CTO and cofounder of InfluxData](https://community.influxdata.com/t/in-2024-which-influxdb-should-i-use-to-get-started-and-then-go-to-production/32840)
suggest starting with v1 over v2 for future proofing.
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
    - Use the telegraf password you used in the [InfluxDB Configuration](#influxdb-configuration) section in place of REPLACE_ME
1. [telegraf](https://github.com/influxdata/telegraf/releases) from the latest **amd64 Linux** release
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

```{note}
I set `agent.interval=50s` in [telegraf.conf](/_static/telegraf.conf) as a compromise.

Back in 2021 my InfluxDB v1 instance on a Xeon server suddenly started not responding to 50% of HTTP requests after 4 years
of running with no issues. I suspect this was due to too much granular data.

Unfortunately implementing downsampling and retention policies is ugly and overly complicated in InfluxDB v1 or v2,
especially if you want to show these data in Grafana. I gave up on downsampling and instead I'm collecting less data than the
10s default interval, to at least delay this problem until the future.
```

### Run on Boot

Here we'll configure TrueNAS to run Telegraf on boot by using a post-init command. This command will use `systemd-run` to launch Telegraf and handle things such as logging, restarting on failures, and environment variables.

1. In the TrueNAS UI go to ➡️ System > Advanced Settings
1. Add an Init/Shutdown script
    1. **Description**: Telegraf
    1. **Type**: Command
    1. **When**: Post Init
    1. **Command**:
        ```bash
        /bin/systemd-run --no-block --unit telegraf -p User=root -p Restart=always -p RestartSec=30 -p EnvironmentFile=/mnt/Vault/Apps/Telegraf/telegraf.env /mnt/Vault/Apps/Telegraf/telegraf --config /mnt/Vault/Apps/Telegraf/telegraf.conf
        ```

You can now reboot, or if you don't want to you can run the command with `sudo`.

```{tip}
To view Telegraf logs run: `sudo journalctl -u telegraf`

To stop Telegraf run: `sudo systemctl stop telegraf`
```

### TrueNAS Graphite Exporter

TrueNAS supports exporting some metrics. Here we'll tell it to export them to Telegraf. They're not used in my dashboard but
you might find a use for them.

1. In the TrueNAS UI go to ➡️ Reporting
1. Click on **Exporters** then **Add**
    1. **Name**: Telegraf
    1. **Type**: GRAPHITE
    1. **Destination IP**: localhost
    1. **Destination Port**: 2003
    1. **Prefix**: graphite
    1. **Namespace**: truenas_reporting
    1. **Update Every**: 50
        1. This matches `agent.interval` in [telegraf.conf](/_static/telegraf.conf)

### Alerts

Finally we'll set up alerts. I configured my TrueNAS with email alerts, and I'd like to be notified if Telegraf isn't
recording metrics. We'll accomplish this by using a cronjob that checks the `outputs.health` endpoint in
[telegraf.conf](/_static/telegraf.conf). The cronjob will fail if Telegraf isn't running or if Telegraf hasn't sent metrics
to InfluxDB in a while (usually after 5 minutes of downtime).

1. In the TrueNAS UI go to ➡️ System > Advanced Settings
1. Add a Cron Job
    1. **Description**: Telegraf Alerts
    1. **Run As User**: root
    1. **Schedule**: Custom
        1. **Minutes**: `*`
        1. **Hours**: `*`
    1. **Hide Standard Output/Error**: Uncheck
    1. **Command** (include the parenthesis):
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
