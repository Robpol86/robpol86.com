---
blogpost: true
date: 2025-07-21
author: Robpol86
location: Melbourne
category: Tutorials
tags: homelab, nas
---

# TrueNAS Telegraf, Influx, Grafana

This guide will explain how to run Telegraf on TrueNAS SCALE, as well as running InfluxDB and Grafana apps to collect metrics
and show graphs. This is how I run all three apps on my Beelink Me Mini NAS. Af of this writing I'm running TrueNAS SCALE
25.04.1.

Most guides and posts on the internet show how to run Telegraf from a Docker container with /sys and other filesystems
mounted as well as running in privileged mode. I personally don't like that approach, so instead I just run Telegraf as root
on "bare metal" (as in not in a container or in a VM).

```{warning}
Running Telegraf on bare metal is not supported by TrueNAS. This implementation may stop working on future versions of
TrueNAS SCALE if they stop including the commands we need.
```

## Prerequisites

Before starting we need to configure TrueNAS to use apps. For this guide we're using **Vault** as the pool and we'll be
creating a few datasets. One dataset per app and one all-encompassing dataset for organizational purposes. This is the layout
we'll be using:

```
Vault (pool)
└─ Apps
   ├─ InfluxDB
   ├─ Grafana
   └─ Telegraf
```

### Create Apps Dataset

TODO

If you haven't used apps yet on your TrueNAS system you'll need to pick a pool to enable them. First create the **Apps**
dataset. Substitute "Vault" with your pool's name.

➡️ Datasets > Vault > Add Dataset

1. **Name**: Apps
1. **Dataset Preset**: Apps

### Configure Apps

Next TODO

➡️ Apps > Configuration

1. **Choose Pool**: Vault

➡️ Datasets > Vault/Apps > Add Dataset

1. **Name**: InfluxDB
1. **Dataset Preset**: Apps
1. Save > Return to Pool List
1. *Repeat for Grafana*
1. *Repeat for Telegraf*

## InfluxDB

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
