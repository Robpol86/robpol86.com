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

* **telegraf**: 7 day retention policy, 10 second data resolution, main ingestion bucket
* **telegraf_1m**: 14 day retention policy, 1 minute data resolution
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

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/0-tig-demo-oob-grafana.png
    You should now see something like this.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/0-tig-demo-oob-influxdb.png
    You should also see something like this.
    :::
```

```{note}
In the demo we'll be using InfluxDB 2.8 but this should work with InfluxDB 2.7 as well. The downsampling is implemented in
the Flux language so unfortunately InfluxDB v3 and v1 are not supported.
```

## Create Buckets

Currently Telegraf writes data to the **telegraf** bucket every 10 seconds, and this bucket stores those data indefinitely.
Our goal is to create new buckets to downsample data into and then set a retention policy on the **telegraf** bucket so high
resolution data is only stored for 7 days. We'll create a **telegraf_1m** bucket to store data with 1 minute resolution
(instead of 10 second) with a 14 day retention policy, and we'll create a **telegraf_5m** bucket to store data with
5 minute resolution with no retention policy. This last bucket will store our historical data indefinitely.

In the InfluxDB web UI (http://localhost:18086) create your downsample buckets:

1. Load Data
1. Buckets
1. Create Bucket
    1. **Name**: telegraf_1m
    1. **Delete Data** > Older Than: 14 days
1. Create

Repeat for **telegraf_5m** but instead of "Older Than" select "Never".

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/1-create-bucket.png
    Creating the telegraf_1m bucket.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/1-create-buckets-done.png
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
create an empty task first (just put a space instead of the script), then edit it and paste the script you originally
intended.
```

Each downsample bucket will need its own task. The task script below can be pasted without modification for both tasks
because InfluxDB automatically updates the `option task` statement with whatever you put in the web UI form. Let's create the
task for `telegraf_1m`:

1. In your InfluxDB web UI (http://localhost:18086) go to Tasks > Create Task > New Task
1. In the left pane/column you can name your task `dsTask-telegraf_1m`
1. Set "Every" to `1m` (don't use CRON for this demo)
1. For offset I use `15s` to give Telegraf enough time to finish writing data to InfluxDB for each iteration (this won't
   affect data timestamps)
1. On the right pane paste the entire script shown below unmodified
1. Click save
1. Repeat for `dsTask-telegraf_5m` with "Every" set to `5m`

```{literalinclude} _static/dsTask.flux
:language: koka
```

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/create-tasks-done.png
    After creating tasks you should see something like this.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/create-tasks-done-query.png
    After 5 minutes the telegraf_1m bucket should start having data with `_time` every minute.
    :::
```

## Set Grafana Variables

In Grafana we will create two variables. The first one will contain the Flux script that does the heavy lifting and decides
which buckets need to be queried for the current time range. The second variable will be used to define which buckets are
queried for which time ranges.

### dsPost Variable

1. In the Grafana Dashboard (http://localhost:13000) click on "Edit" and then "Settings"
1. Go to the "Variables" tab then click "New variable"
1. The variable type is `Query`, the variable name must be `dsPost`, the data source should be `influxdb`
1. In the "Query options" text area paste the entire script shown below unmodified
1. Scroll down and set the refresh setting to `On time range change`
1. Uncheck "Multi-value", "Allow custom values", and "Include All option"
1. Leave sorting disabled and leave Regex empty
1. Click "Back to list"

```{literalinclude} _static/dsPost.flux
:language: koka
```

### dsBuckets Variable

1. In the "Variables" tab click "New variable"
1. The variable type is `Custom`, the variable name must be `dsBuckets`
1. In the "Values separated by comma" text area paste the following code block shown below unmodified
1. Uncheck "Multi-value", "Allow custom values", and "Include All option"
1. Click "Back to list" then "Back to dashboard"
1. Click on "Save dashboard" to save these changes

```bash
${BUCKET}=now:-20m|
${BUCKET}_1m=-20m:-40m|
${BUCKET}_5m=-40m:inf
```

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/grafana-ds-vars.png
    Your "Variables" tab should look like this.
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/grafana-ds-dashboard-pre.png
    Your dashboard should now look like this.
    :::
```

## Update Grafana Queries

```{note}
Wait for one hour for the downsample tasks you created to downsample enough data to show up in the graphs.
```

It's time to tie everything together. For each of the four graphs edit the queries and make these changes:

1. Insert `dsQuery = (bucket, start, stop) =>` as the first line
1. Append `${dsPost}` as the last line
1. Replace `"${BUCKET}"` with `bucket`
1. Replace `v.timeRangeStart` with `start`
1. Replace `v.timeRangeStop` with `stop`

For example, the following is the before and after for the Memory graph:

```koka
// Before
from(bucket: "${BUCKET}")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r.host == "${NAS_HOST}")
  |> filter(fn: (r) => r._measurement == "mem" or r._measurement == "swap")
  |> filter(fn: (r) => r._field == "used" or r._field == "active")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")

// After
dsQuery = (bucket, start, stop) =>
from(bucket: bucket)
  |> range(start: start, stop: stop)
  |> filter(fn: (r) => r.host == "${NAS_HOST}")
  |> filter(fn: (r) => r._measurement == "mem" or r._measurement == "swap")
  |> filter(fn: (r) => r._field == "used" or r._field == "active")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
${dsPost}
```

```{list-table-thumbs}
:resize-width: 400
:widths: 10 10

* - :::{thumb-figure} /_images/pictures/influxdb-downsampling/4-memory-graph.png
    The Memory graph should look like this when you click on `Refresh`
    :::
  - :::{thumb-figure} /_images/pictures/influxdb-downsampling/4-grafana-ds-dashboard.png
    Your dashboard should now look like this.
    :::
```

:::{note}
If you get the error "invalid: runtime error: schema collision detected: column "raw_value" is both of type int and float"
you'll need to add `toFloat()` to cast integers from the main bucket to floats since that's the datatype used in downsample
buckets.

An example before and after of the fix:

```koka
// Before
dsQuery = (bucket, start, stop) =>
from(bucket)
  |> range(start, stop)
  |> filter(fn: (r) => r.host == "${NAS_HOST}")
  |> filter(fn: (r) => r._measurement == "smart_attribute")
  |> filter(fn: (r) => r._field == "raw_value")
  |> filter(fn: (r) => r.name == "Temperature_Celsius")
  |> drop(columns: ["device"])
  |> aggregateWindow(every: v.windowPeriod, fn: max, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
${dsPost}

// After
dsQuery = (bucket, start, stop) =>
from(bucket)
  |> range(start, stop)
  |> filter(fn: (r) => r.host == "${NAS_HOST}")
  |> filter(fn: (r) => r._measurement == "smart_attribute")
  |> filter(fn: (r) => r._field == "raw_value")
  |> filter(fn: (r) => r.name == "Temperature_Celsius")
  |> drop(columns: ["device"])
  |> toFloat()
  |> aggregateWindow(every: v.windowPeriod, fn: max, createEmpty: false)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
${dsPost}
```
:::

## Backfill Data Guidance

If you have existing data that you'd like to keep you'll need to backfill it into the newly created downsample buckets. In
this section we'll populate the new buckets with the downsampled old data written by Telegraf before any dsTask has run.

Depending on how much data you have backfilling may take a long time (days, weeks, maybe even months for everything), so
we'll be doing it in chunks. Bigger chunks mean more memory usage in the InfluxDB container, so keeping chunks small avoids
OOMKill. When I backfilled my homelab production data for a single telegraf host it took up to 16 minutes for 24 hours of
data.

The [dsTask.flux](_static/dsTask.flux) file provided in the [Create Tasks](#create-tasks) section can also be used for
backfilling from the command line. Below is a bash script that modifies the file to backfill a chunk:

```bash
resolution="1m"
chunkstart="2025-08-25T02:00:00.000000000Z"
chunkstop="2025-08-25T02:59:59.999999999Z"
sed \
    -e '/bfEnabled:/s/:[^,]\+,/: true,/' \
    -e '/bfEveryResolution:/s/:[^,]\+,/: '"$resolution"',/' \
    -e '/bfChunkStart:/s/:[^,]\+,/: '"$chunkstart"',/' \
    -e '/bfChunkStop:/s/:[^,]\+,/: '"$chunkstop"',/' \
    ./dsTask.flux > backfill.flux

token=""  # Create an influxdb token with read+write to downsample buckets.
influx query --org homelab --token "$token" - < backfill.flux
```

## Main Bucket Retention Policy

TODO telegraf

## Performance

TODO compare query statistics (or profiling), best of 10 each.

## Conclusion

TODO revisit original flux docstrings instructions.

TODO test with influxdb 2.7.

TODO all new screenshots using Safari on macbook display

TODO copy final screenshots to tnas

TODO [dsGrafana.json](_static/dsGrafana.json)

TODO confirm on podman

TODO run through guide fast

TODO then run through slow (wait 1h after oob, another 1h after create tasks)
