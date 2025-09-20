// dsPost.flux: Query one or more downsample buckets in Grafana.
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

import "array"
import "date"
import "strings"

// Take in any string array and outputs it as a stream so Grafana can ingest it as a single
// or multi-value variable.
exportAsStream = (arr) =>
    array.from(rows: array.map(arr: arr, fn: (x) => ({ _value: x })))

// Convert time strings (e.g. "now" or "-3d") into time objects.
stringToTime = (s) =>
    if s == "now" then now()
    else if s == "inf" or s == "-inf" then date.time(t: inf)
    else date.time(t: duration(v: s))

// Parse dsBuckets string into array of strings and stop/stop time objects bound within the
// range of trStart/trStop.
parseBucketsString = (buckets, trStop, trStart) =>
    // Split dsBuckets string with pipe delimiter.
    // Valid string example: telegraf=now:-5m|telegraf_1m=-5m:-inf
    strings.split(v: buckets, t: "|")
        |> array.map(fn: (x) => strings.trimSpace(v: x))
        // Filter out invalid substrings.
        |> array.filter(fn: (x) => x =~ /^[a-zA-Z0-9_-]+=[a-z0-9-]+:[a-z0-9-]+$/)
        // Get bucket names and convert start/stop to time objects.
        |> array.map(fn: (x) => {
            // Split and get the bucket name.
            splitEquals = strings.splitN(v: x, t: "=", i: 2)
            name = splitEquals[0]
            // Split and get the bucket time range.
            splitColon = strings.splitN(v: splitEquals[1], t: ":", i: 2)
            bStop = stringToTime(s: splitColon[0])
            bStart = stringToTime(s: splitColon[1])
            return {name, bStop, bStart}
            })
        // Filter out buckets outside of selected time range.
        |> array.filter(fn: (x) => x.bStart < trStop and x.bStop > trStart)
        // Adjust start/stop time boundaries for outer buckets.
        |> array.map(fn: (x) => {
            name = x.name
            stop = if trStop < x.bStop then trStop else x.bStop
            start = if trStart > x.bStart then trStart else x.bStart
            return {name, stop, start}
            })

// Return the dsQuery() Flux function call that Grafana will execute for one bucket.
dsPostSingle = (bucket) =>
    "dsQuery(bucket: \"${bucket.name}\", start: ${bucket.start}, stop: ${bucket.stop})"

// Return one dsQuery() call per bucket and route the outputs into union() to merge them
// into one metric. Normalize start/stop boundary times so Grafana displays them as one
// line.
dsPostMulti = (parsedBuckets, trStop, trStart) => {
    dsQueryCalls = array.map(arr: parsedBuckets, fn: (x) => dsPostSingle(bucket: x))
    dsQueryArr = "[" + strings.joinStr(arr: dsQueryCalls, v: ", ") + "]"
    dsQueryUnion = "union(tables: ${dsQueryArr})"
    dsStartStop = "({ r with _start: ${trStart}, _stop: ${trStop} })"
    return "map(tables: ${dsQueryUnion}, fn: (r) => ${dsStartStop})"
}

// Main.
buckets = ${dsBuckets:doublequote}
dsPost =
    if buckets !~ /\b(now)\b/
    then "error: 'now' is missing"
    else if buckets !~ /\b(inf)\b/
    then "error: 'inf' is missing"
    else () => {
        trStop = v.timeRangeStop
        trStart = v.timeRangeStart
        parsedBuckets = parseBucketsString(buckets, trStop, trStart)
        return
            if length(arr: parsedBuckets) < 1
            then "error: no valid buckets"
            else if length(arr: parsedBuckets) == 1
            then dsPostSingle(bucket: parsedBuckets[0])
            else dsPostMulti(parsedBuckets, trStop, trStart)
    }()
exportAsStream(arr: [dsPost])
