---
blogpost: true
date: 2025-09-20
author: Robpol86
location: Taipei
category: Tutorials
tags: homelab, nas
---

# InfluxDB Downsampling

```{list-table}
* - :::{imgur-image} 0m3qdla.png
    :::
```

In this guide I will show you how I've implemented InfluxDB v2 downsampling that plays nicely with Grafana with minimal
changes to queries. I use it to downsample Telegraf metrics but it should work with any data. Ints and floats are downsampled
using `mean()` whilst all other types are downsampled with `last()`. Grafana will read metrics from your main bucket and one
or more downsample buckets. It will then combine data from the buckets with `union()`. The last part I've automated into a
single Grafana variable to avoid copying and pasting a lot of code for each of your queries.

The official [InfluxDB v2 documentation](https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/)
implements downsampling in a strange way that doesn't seem usable for real time metrics such as with Telegraf. They also
don't cover consuming the downsampled data. It turns out that was the hardest part to get right.

TODO top image with four buckets is hard to read when shown as an og embed. Make it three or two buckets.

## Overview

Downsampling is implemented in two parts: the [InfluxDB side](/_static/dsTask.flux) which does the downsampling, and the
[Grafana side](/_static/dsPost.flux) which reads data from one or more buckets.

On the InfluxDB side you will have a [Flux task](https://docs.influxdata.com/influxdb/v2/process-data/get-started/) that runs
on a schedule downsampling recent data into a separate downsample bucket. You may wish to have multiple downsample buckets
with different granularity/resolution of data each with their own retention policies. If you have old data you want to
downsample instead of just the new data I'm covering that in the [Backfilling Data](#backfilling-data) section below.

On the Grafana side we'll need to tell it to query the main bucket as well as the downsample buckets. The goal of this
project is to see very detailed recent metrics and then use downsampled metrics at a lower resolution for historical data. We
want to avoid having to process thousands or millions of data points per panel when we have Grafana zoom out to month or year
time frames. Another goal I set for this project is to minimize the changes needed to be done to each query to enable
downsampling. My solution is basically to add three short lines to each query. An example before and after downsampling:

```
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

TODO compare query statistics (or profiling), best of 10 each.

TODO revisit all pygments lexers

```bash
# REMOVE ME
for lexer in $(poetry run python -c 'from pygments.lexers._mapping import LEXERS; print(" ".join([l[2][0] for l in LEXERS.values() if len(l[2]) >= 1]))'); do echo ">$lexer"; gsed -i '/^:language:/s/:[^:]*$/: '"$lexer"'/' docs/posts/2025/2025-09-20-influxdb-downsampling.md; sleep 5; echo; done
```

## InfluxDB Side

TODO

### Flux Tasks

TODO reduce docstring and document here instead

```
// InfluxDB v2 Flux task. All numerical values (int, uint, float) will be downsampled with mean(), whilst every other value
// (string, bool, etc.) will be downsampled with last() (the last entry within the time range specified in task.every).
//
// ## Prerequisites
//
// Create the downsample buckets before running this task. An example pattern:
//
// * "telegraf" is your main bucket with raw data, added every 10 seconds or so.
// * "telegraf_1m" is your downsample bucket that this tasks writes to, averaging data to every 1 minute.
//
// Set an appropriate retention policy for each bucket. I personally keep data in InfluxDB longer than what I have Grafana
// query in case I want to adjust how much raw data I want to display before the graph starts to smooth out.
//
// As an example these are the buckets I use and their retentions:
//
// * telegraf: 30 days
// * telegraf_1m: 90 days
// * telegraf_5m: 1 year
// * telegraf_10m: forever
//
// Proceed on to the Backfill section if you've got old data you want to backfill into the new downsample buckets. If you
// don't have any old data to preserve then skip to the Install section below. 
//
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
:language: text
```

### Backfilling Data

TODO

## Grafana Side

TODO gif with production ranges showing zooming out and panning

### Grafana Query Variable

TODO

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

#### actionscript3

```{literalinclude} /_static/dsPost.flux
:language: actionscript3
```

#### actionscript

```{literalinclude} /_static/dsPost.flux
:language: actionscript
```

#### javascript+cheetah

```{literalinclude} /_static/dsPost.flux
:language: javascript+cheetah
```

#### croc

```{literalinclude} /_static/dsPost.flux
:language: croc
```

#### d

```{literalinclude} /_static/dsPost.flux
:language: d
```

#### dax

```{literalinclude} /_static/dsPost.flux
:language: dax
```

#### dylan

```{literalinclude} /_static/dsPost.flux
:language: dylan
```

#### fan

```{literalinclude} /_static/dsPost.flux
:language: fan
```

#### fift

```{literalinclude} /_static/dsPost.flux
:language: fift
```

#### gosu

```{literalinclude} /_static/dsPost.flux
:language: gosu
```

#### igor

```{literalinclude} /_static/dsPost.flux
:language: igor
```

#### javascript

```{literalinclude} /_static/dsPost.flux
:language: javascript
```

#### javascript+smarty

```{literalinclude} /_static/dsPost.flux
:language: javascript+smarty
```

#### jsgf

```{literalinclude} /_static/dsPost.flux
:language: jsgf
```

#### juttle

```{literalinclude} /_static/dsPost.flux
:language: juttle
```

#### k

```{literalinclude} /_static/dsPost.flux
:language: k
```

#### koka

```{literalinclude} /_static/dsPost.flux
:language: koka
```

#### javascript+lasso

```{literalinclude} /_static/dsPost.flux
:language: javascript+lasso
```

#### mcschema

```{literalinclude} /_static/dsPost.flux
:language: mcschema
```

#### modula2

```{literalinclude} /_static/dsPost.flux
:language: modula2
```

#### objective-j

```{literalinclude} /_static/dsPost.flux
:language: objective-j
```

#### q

```{literalinclude} /_static/dsPost.flux
:language: q
```

#### qml

```{literalinclude} /_static/dsPost.flux
:language: qml
```

#### scilab

```{literalinclude} /_static/dsPost.flux
:language: scilab
```

#### supercollider

```{literalinclude} /_static/dsPost.flux
:language: supercollider
```

#### typescript

```{literalinclude} /_static/dsPost.flux
:language: typescript
```

#### x10

```{literalinclude} /_static/dsPost.flux
:language: x10
```

#### yara

```{literalinclude} /_static/dsPost.flux
:language: yara
```

#### zephir

```{literalinclude} /_static/dsPost.flux
:language: zephir
```

### Update Queries

TODO [dsGrafana.json](/_static/dsGrafana.json)

TODO toFloat()
