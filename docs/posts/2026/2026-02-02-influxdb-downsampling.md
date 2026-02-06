---
blogpost: true
date: 2026-02-02
author: Robpol86
location: Hong Kong
category: Tutorials
tags: homelab, nas
---

# InfluxDB v2 Downsampling

In this guide I will show you how I've implemented InfluxDB 2.x downsampling that plays nicely with Grafana with minimal
changes to queries. Integers and floats are downsampled with `mean()` and all other types are downsampled with `last()`.
A three line change to Grafana queries will enable it to read narrowed down time ranges for each bucket and combine the
output with `union()`. Below is an example Grafana panel query change:

```koka
// Before
from(bucket: "${BUCKET}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r.host == "${HOST}")
  |> filter(fn: (r) => r._measurement == "mem")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

// After
dsQuery = (bucket, start, stop) =>
from(bucket)
  |> range(start, stop)
  |> filter(fn: (r) => r.host == "${HOST}")
  |> filter(fn: (r) => r._measurement == "mem")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
${dsPost}
```

This implementation builds on the very brief
[InfluxDB v2 example](https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/) and shows how
to consume the downsampled data in Grafana. It turns out the latter was the hardest part to get right.

This guide will walk you through implementing downsampling on a demo TIG stack (Telegraf, InfluxDB, Grafana) using
[Docker Compose](https://docs.docker.com/compose/). We'll implement the following buckets with these retention policies:

* **telegraf**: 30 day retention policy, 10 second data resolution, main ingestion bucket
* **telegraf_1m**: 90 day retention policy, 1 minute data resolution
* **telegraf_5m**: no retention policy, 5 minute data resolution, keep historical data forever

I'll also cover backfilling existing data into the new downsample buckets.

```{thumb-image} /_images/pictures/influxdb-downsampling/downsample.png
```

## Prerequisites

Before starting you'll need to have Docker Compose installed. You can find those instructions here:
https://docs.docker.com/compose/install

Next start the demo TIG stack. This is a basic example with an InfluxDB container, a Telegraf container to send it some data,
and a Grafana container to show the data using four graphs. I've written a Docker Compose file that starts everything up with
one command, pre-configured.

1. Download [docker-compose-dsdemo.yml](_static/docker-compose-dsdemo.yml)
2. Start the apps by running:
    ```bash
    docker-compose -f docker-compose-dsdemo.yml -p dsdemo up -d
    ```
3. Access the Grafana dashboard (username is **admin** and password is **Stand&Deliver**): http://localhost:13000/
3. Access the InfluxDB dashboard (username and password are the same as Grafana's): http://localhost:18086/

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/tig-demo-oob-grafana.png
    You should now see something like this.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/tig-demo-oob-influxdb.png
    You should also see something like this.
    :::
```

```{note}
In the demo we'll be using InfluxDB 2.8 but this should work with InfluxDB 2.7 as well. The downsampling is implemented in
the Flux language so unfortunately InfluxDB v3 and v1 are not supported.
```

## Create Buckets

Currently Telegraf writes data to the **telegraf** bucket every 10 seconds. And this bucket stores those data indefinitely.
Our goal is to create new buckets to downsample data into and then set a retention policy on the **telegraf** bucket so high
resolution data is only stored for 30 days. We'll create a **telegraf_1m** bucket to store data with 1 minute
resolution (instead of 10 second) with a 90 day retention policy, and we'll create a **telegraf_5m** bucket to store data with
5 minute resolution with no retention policy. This last bucket will store our historical data indefinitely.

In the InfluxDB web UI (http://localhost:18086) create your downsample buckets:

1. Load Data
1. Buckets
1. Create Bucket
    1. **Name**: telegraf_1m
    1. **Delete Data** > Older Than: 90 days
1. Create

Repeat for **telegraf_5m** but instead of "Older Than" click on "Never".

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/imgur-qEbiR2z.png
    Creating the telegraf_1m bucket.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/create-buckets-done.png
    After creating buckets you should see something like this.
    :::
```

## Create Tasks

```{warning}
Due to an [InfluxDB bug](https://github.com/influxdata/influxdb/issues/26781) you should avoid cloning tasks and instead
create each one from scratch as outlined here.
```

```{note}
If you get the error "Failed to create new task: Invalid flux script. Please check your query text." when creating a task
this is due to [another InfluxDB bug](https://github.com/influxdata/influxdb/issues/25197). The workaround I found was to
create an empty task first (just put a space), then edit it and paste the task you originally intended.
```

Each downsample bucket will need its own task. The task script below can be pasted without modification (unless your bucket names
are different) for both tasks because InfluxDB automatically updates the `option task` statement with whatever you put in the
web UI form. Let's create the task for `telegraf_1m`:

1. In your InfluxDB web UI go to Tasks > Create Task > New Task
1. In the left pane/column you can name your task `dsTask-telegraf_1m`
1. Set "Every" to `1m` (don't use CRON)
1. For offset I use `15s` to give Telegraf enough time to finish writing data to InfluxDB for each iteration (this won't
   affect data timestamps)
1. On the right pane paste the entire script shown below unmodified
1. Click save
1. Repeat for `dsTask-telegraf_5m` with "Every" set to `5m`

```{literalinclude} _static/dsTask.flux
:language: koka
```

```{thumb-figure} /_images/pictures/influxdb-downsampling/imgur-3HBbsW4.png
TODO After you click "Install" you should see something like this.
```

## Backfill Data

TODO chunking

```
// ## Backfill
//
// To backfill a new downsample bucket with historical data you'll want to do it in chunks. It could take 1-16 minutes to
// backfill just one day of data for one telegraf host. To backfill, make a copy of this file (e.g. dsTask-backfill.flux)
// with the following changes:
//
// 1. Set backfill.enabled to true
// 2. Set backfill.everyResolution to the resolution if your target bucket (e.g. 1m for telegraf_1m, 5m for telegraf_5m)
// 3. Set backfill.chunkStart to a date before your earliest data point (for simplicity keep the time to all zeros)
// 4. Set backfill.chunkStop to however much data you wish to process in one go (set the time to the last possible nanosecond
//    before the next chunk window to avoid potential data loss)
//
// Then execute the file using the influx CLI. Here's an example command:
//      influx query - < ./dsTask-backfill.flux > backfill.log
//
```

## Set Remaining Retention Policy

TODO

## Set Grafana Variables

```
// Grafana Flux query variable. Helps combine InfluxDB v2 downsample buckets into output to be displayed in a Grafana panel.
// When the user zooms in, downsampled buckets that are no longer within the scope of the current time range won't be
// queried. This query will run once per dashboard load, refresh, or time range change before any panels queries are run.
//
// ## Prerequisites
//
// 1. Decide which buckets shall be queried for which time ranges. For example if you want the "telegraf" bucket to be used
//    for metrics from "now-5m" to "now" you'll specify it with "telegraf=now:-5m". And if you want the rest of the graph to
//    use the bucket "telegraf_1m" you'll specify that with "telegraf_1m=-5m:inf".
// 2. Set a Grafana constant variable named "dsBuckets" to your bucket name and range specification, separated with "|". Your
//    first range must start with "now" and your last range must end with "inf". You can specify two or more buckets, here
//    are some examples:
//      telegraf=now:-5m|telegraf_1m=-5m:inf
//      telegraf=now:-30m|telegraf_1m=-30m:-1h|telegraf_5m=-1h:inf
//      telegraf=now:-1d|telegraf_1m=-1d:-2d|telegraf_5m=-2d:-3d|telegraf_10m=-3d:inf
//
// ## Install
//
// 1. In your Grafana dashboard settings go to the Variables section and add a new variable.
// 2. The variable type is "Query", the variable name must be "dsPost", set the data source to your influxdb instance, you
//    must set the refresh setting to "On time range change", and uncheck "multi-value", "allow custom values", and "include
//    All option" (as of Grafana v12.0.2). Disable sorting and leave Regex empty as well.
// 3. Paste this script below the "PASTE EVERYTHING BELOW THIS LINE IN GRAFANA" line into the "Query" field. Test it by
//    clicking on "Run query", you should see a preview value. Then click "Back to list". Then go back to your dashboard.
// 4. If you didn't hide the variable you should see "dsPost" at the top of your dashboard. When you change the dashboard
//    time range you should see your buckets appear/disappear from the value of this variable. Every refresh, time range
//    change, and browser refresh will update dsPost.
//
// ## Usage
//
// Finally to use dsPost in your panels you'll need to update all of the queries. For most queries all you need to do is add
// "dsQuery = (bucket, start, stop) =>" to the top and "${dsPost}" to the bottom (without quotes) and set your bucket and
// range to the bucket, start, and stop variables. Here's an example panel query:
//
//      dsQuery = (bucket, start, stop) =>
//      from(bucket)
//      |> range(start, stop)
//      |> filter(fn: (r) =>
//          r._measurement == "cpu" and
//          r.host == "tnas" and
//          r.cpu == "cpu-total" and
//          r._field == "usage_user"
//      )
//      ${dsPost}
//

// PASTE EVERYTHING BELOW THIS LINE IN GRAFANA
```

```{literalinclude} _static/dsPost.flux
:language: koka
```

## Update Queries

TODO gif with production ranges showing zooming out and panning

TODO [dsGrafana.json](_static/dsGrafana.json)

TODO toFloat()

### Performance

TODO compare query statistics (or profiling), best of 10 each.

## Conclusion

TODO telegraf retention

TODO revisit original flux docstrings instructions.

TODO test with influxdb 2.7.

TODO all new screenshots

TODO copy final screenshots to tnas
