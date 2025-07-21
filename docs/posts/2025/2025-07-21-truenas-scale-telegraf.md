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
and show graphs. This is how I run all three apps on my Beelink Me Mini NAS. As of this writing I'm running TrueNAS SCALE
25.04.1.

Most guides and posts on the internet show how to run Telegraf from a Docker container with /sys and other filesystems
mounted as well as running in privileged mode. I personally don't like that approach, so instead I just run Telegraf as root
on "bare metal" (as in not in a container or in a VM).

```{warning}
Running Telegraf on bare metal is not officially supported by TrueNAS. This implementation may stop working on future
versions of TrueNAS SCALE if they stop including the commands we need.
```

## Prerequisites

Before starting there are a few things we need to setup:

- Choose a pool for apps if you haven't used apps in TrueNAS before
- Create datasets for each application

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

I use [InfluxDB](https://www.influxdata.com/) as the timeseries database to store all my metrics. Here I'll explain two ways
you can install it.

::::{tab-set}

:::{tab-item} Simple Install
TODO
:::

:::{tab-item} Custom Install
This is what I use on my NAS. I personally don't want my InfluxDB version to be upgraded unexpectedly and without my
knoweldge by the catalog maintainer.

```{note}
I'm running v1 because:

- The latest version as of this writing is v3 but that has an absurd 3-day data limit for the free license (lol).
- I started working on my Grafana dashboard way back in 2017 so all of my queries are in
  [InfluxQL](https://docs.influxdata.com/influxdb/v1/query_language/). v3 uses SQL, v2 uses Flux, TODO
```

I like having control over the version of InfluxDB I'm running. Here I'm using v1 for a few reasons. Mainly: The latest
version as of this writing is v3 but that has an absurd 3-day data limit for the free license (lol). I chose v1 over v2 mostly because Flux is now deprecated so it's not worth upgrading all of the queries on my dashboard to it. Even though v2 has an endpoint for my existing InfluxQL dashboard queries
TODO version 1 2 and 3.

➡️ Apps > Discover Apps > ... > Install via YAML

1. **Name**: influxdb
1. **Custom Config**: *paste app-influxdb.yaml*

```yaml
services:
  influxdb:
    hostname: influxdb
    image: influxdb:1.11.8
    pull_policy: always
    restart: always
    environment:
      INFLUXDB_DATA_QUERY_LOG_ENABLED: "false"
      INFLUXDB_HTTP_AUTH_ENABLED: "true"
      INFLUXDB_HTTP_FLUX_ENABLED: "true"
      INFLUXDB_HTTP_LOG_ENABLED: "false"
    ports:
      - mode: ingress
        protocol: tcp
        published: 8086
        target: 8086
    user: "568:568"
    volumes: [/mnt/Vault/Apps/InfluxDB:/var/lib/influxdb]
```
:::

::::

### Configuration

➡️ Apps > influxdb > Workloads > Containers > influxdb > Shell

Run `HOME= influx` and then execute these queries:

```sql
CREATE USER admin WITH PASSWORD 'REPLACE_ME' WITH ALL PRIVILEGES
AUTH

CREATE DATABASE telegraf
CREATE USER truenas WITH PASSWORD 'REPLACE_ME'
GRANT WRITE ON telegraf TO truenas
CREATE USER grafana WITH PASSWORD 'REPLACE_ME'
GRANT READ ON telegraf TO grafana
```

## Telegraf

```bash
echo 'INFLUX_PASSWORD_TRUENAS="REPLACE_ME"' > env
scp ./env ./telegraf.conf truenas_admin@10.192.168.10:/mnt/Vault/Apps/Telegraf/
## Download from https://github.com/influxdata/telegraf/releases on macOS, then:
scp ~/Downloads/telegraf-1.35.1/usr/bin/telegraf truenas_admin@10.192.168.10:/mnt/Vault/Apps/Telegraf/
```

➡️ System > Advanced Settings > Init/Shutdown Scripts > Add

1. **Description**: Telegraf
1. **When**: Post Init

```bash
/bin/systemd-run --no-block --unit telegraf -p User=root -p Restart=always -p RestartSec=30 -p EnvironmentFile=/mnt/Vault/Apps/Telegraf/env /mnt/Vault/Apps/Telegraf/telegraf --config /mnt/Vault/Apps/Telegraf/telegraf.conf
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
