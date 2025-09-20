// dsTask.flux: Flux task that downsamples one bucket into another.
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
