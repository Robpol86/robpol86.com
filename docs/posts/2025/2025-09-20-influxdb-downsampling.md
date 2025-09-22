---
blogpost: true
date: 2025-09-20
author: Robpol86
location: Taipei
category: Tutorials
tags: homelab, nas
---

# InfluxDB v2 Downsampling

In this guide I will show you how I've implemented InfluxDB 2.x downsampling that plays nicely with Grafana with minimal
changes to queries. Integers and floats are downsampled with `mean()` and all other types are downsampled with `last()`.
A three line change to Grafana queries will enable it to read narrowed down time ranges for each bucket and combine the
output with `union()`.

This implementation builds on the very brief
[InfluxDB v2 example](https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/) and shows how
to consume the downsampled data in Grafana. It turns out the latter was the hardest part to get right.

This guide will walk you through implementing downsampling for your Telegraf data, but it should work with all data types.
I'll also touch on [backfilling](#backfill-data), which is when you've been collecting data for some time and wish to
retroactively downsample it.

```{list-table}
* - :::{imgur-image} 0m3qdla.png
    :::
```

## Overview

Downsampling is implemented in two parts: the InfluxDB side and the Grafana side.

### InfluxDB Side

On the InfluxDB side we'll have a task that runs on a timer, downsampling data from a main bucket (e.g. "telegraf") into a
separate downsample bucket (e.g. "telegraf_1m"). Multiple downsample buckets are supported, so in theory you can have three
buckets:

1. **telegraf**: raw data written by telegraf every 10 seconds (10 second resolution)
2. **telegraf_1m**: downsampled data, averaged out to every minute (1 minute resolution)
3. **telegraf_5m**: downsampled to an average of every 5 minutes (5 minute resolution)

For each bucket you can set different retention policies.

### Grafana Side

On the Grafana side we'll need to tell it to query the main bucket as well as the downsample buckets. The goal of this
project is to see very detailed recent metrics and then use downsampled metrics at a lower resolution for historical data. We
want to avoid having to process thousands or millions of data points per panel when we have Grafana zoom out to month or year
time frames. Another goal I set for this project is to minimize the changes needed to be done to each query to enable
downsampling. My solution is basically to add three short lines to each query. An example before and after downsampling:

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

### Performance

TODO compare query statistics (or profiling), best of 10 each.

## Prerequisites

TODO plan. TODO InfluxDB v2 tested, Flux required, Grafana.

TODO in this guide telegraf, telegraf_1m and 5m.

* telegraf: 30 days
* telegraf_1m: 90 days
* telegraf_5m: forever (never)

TODO docker example

## Create Buckets

In the InfluxDB web UI (http://localhost:8086) create your downsample buckets:

1. Load Data
1. Buckets
1. Create Bucket
    1. **Name**: telegraf_1m
    1. **Delete Data** > Older Than: 90 days
1. Create

Repeat for **telegraf_5m** but instead of "Older Than" click on "Never".

```{imgur-figure} qEbiR2z.png
TODO
```

## Create Tasks

```{warning}
Due to an [InfluxDB bug](https://github.com/influxdata/influxdb/issues/26781) you should avoid cloning tasks and instead
create each one from scratch as outlined here.
```

In the InfluxDB web UI create a task:

1. Load Data
1. Buckets
1. Create Bucket
    1. **Name**: telegraf_1m
    1. **Delete Data** > Older Than: 90 days
1. Create

TODO reduce docstring and document here instead

```
// ## Install
//
// 1. In your InfluxDB UI go to Tasks > Create Task > New Task
// 2. In the left pane/column you can name your task "dsTask-<bucket>_<every>" (e.g. dsTask-telegraf_1m)
// 3. Set "Every" to "1m" to downsample data to 1 minute intervals (don't use CRON)
// 4. For offset I use "15s" to give Telegraf enough time to finish writing data to InfluxDB for each iteration.
// 5. To work around an InfluxDB bug (#25197) put a space in the right pane and save the new empty task. Then edit it, you'll
//    see it auto-inserted "option task". Delete that (everything in the right pane) for now.
// 6. On the right pane paste this entire script. You only need to make changes to the script if your bucket names are
//    different. Everything in the "option task" variable in the right pane will be overridden by what's in the left pane.
// 7. Click save.
//
// If you have additional buckets you can just clone the task then edit the new task to change its name and "Every" value.
//
```

```{literalinclude} /_static/dsTask.flux
:language: koka
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

```{literalinclude} /_static/dsPost.flux
:language: koka
```

## Update Queries

TODO gif with production ranges showing zooming out and panning

TODO [dsGrafana.json](/_static/dsGrafana.json)

TODO toFloat()

## Conclusion

TODO telegraf retention

TODO revisit original flux docstrings instructions.
