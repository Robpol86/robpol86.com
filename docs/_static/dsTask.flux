// dsTask.flux: Flux task that downsamples one bucket into another.
//
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
// BSD 2-Clause License
// Copyright (c) 2025, Robpol86
// All rights reserved.
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
// 1. Redistributions of source code must retain the above copyright notice, this
//    list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright notice,
//    this list of conditions and the following disclaimer in the documentation
//    and/or other materials provided with the distribution.
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
// CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
// OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import "types"

// Options for InfluxDB task (no need to edit).
option task = {
    name: "Everything in 'option task' will be overridden when saving the task",
    every: 1m,
    offset: 15s
}

// Set your main bucket name here.
option bucketRootName = "telegraf"

// Set backfill.enabled to true when backfilling a new downsample bucket with "influx query ...".
option backfill = {
    bfEnabled: false,
    bfEveryResolution: 1m,
    bfChunkStart: 2025-08-01T00:00:00.000000000Z,
    bfChunkStop: 2025-08-01T23:59:59.999999999Z,
}

// No need to edit anything beyond this line.

resolution = if backfill.bfEnabled then backfill.bfEveryResolution else task.every
buckets = {
    source: bucketRootName,
    target: "${bucketRootName}_${resolution}"
}

// Select all data into this variable.
dataAll =
    if backfill.bfEnabled
    then from(bucket: buckets.source) |> range(start: backfill.bfChunkStart, stop: backfill.bfChunkStop)
    else from(bucket: buckets.source) |> range(start: -resolution)

// Integers and floats will be averaged together with mean().
dataToMean = dataAll
    |> filter(fn: (r) =>
        types.isType(v: r._value, type: "int") or
        types.isType(v: r._value, type: "uint") or
        types.isType(v: r._value, type: "float")
    )

// For all other data types (e.g. strings) we'll select the last value within the time range.
dataToLast = dataAll
    |> filter(fn: (r) =>
        not types.isType(v: r._value, type: "int") and
        not types.isType(v: r._value, type: "uint") and
        not types.isType(v: r._value, type: "float")
    )

// Write aggregated data into the target bucket.
dataToMean
    |> aggregateWindow(every: resolution, fn: mean, createEmpty: false)
    |> to(bucket: buckets.target)
dataToLast
    |> aggregateWindow(every: resolution, fn: last, createEmpty: false)
    |> to(bucket: buckets.target)
