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

```{literalinclude} /_static/dsPost.flux
:language: abap
```

```{literalinclude} /_static/dsPost.flux
:language: amdgpu
```

```{literalinclude} /_static/dsPost.flux
:language: apl
```

```{literalinclude} /_static/dsPost.flux
:language: abnf
```

```{literalinclude} /_static/dsPost.flux
:language: actionscript3
```

```{literalinclude} /_static/dsPost.flux
:language: actionscript
```

```{literalinclude} /_static/dsPost.flux
:language: ada
```

```{literalinclude} /_static/dsPost.flux
:language: adl
```

```{literalinclude} /_static/dsPost.flux
:language: agda
```

```{literalinclude} /_static/dsPost.flux
:language: aheui
```

```{literalinclude} /_static/dsPost.flux
:language: alloy
```

```{literalinclude} /_static/dsPost.flux
:language: ambienttalk
```

```{literalinclude} /_static/dsPost.flux
:language: ampl
```

```{literalinclude} /_static/dsPost.flux
:language: html+ng2
```

```{literalinclude} /_static/dsPost.flux
:language: ng2
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-actionscript
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-csharp
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-cpp
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-java
```

```{literalinclude} /_static/dsPost.flux
:language: antlr
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-objc
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-perl
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-python
```

```{literalinclude} /_static/dsPost.flux
:language: antlr-ruby
```

```{literalinclude} /_static/dsPost.flux
:language: apacheconf
```

```{literalinclude} /_static/dsPost.flux
:language: applescript
```

```{literalinclude} /_static/dsPost.flux
:language: arduino
```

```{literalinclude} /_static/dsPost.flux
:language: arrow
```

```{literalinclude} /_static/dsPost.flux
:language: arturo
```

```{literalinclude} /_static/dsPost.flux
:language: asc
```

```{literalinclude} /_static/dsPost.flux
:language: asn1
```

```{literalinclude} /_static/dsPost.flux
:language: aspectj
```

```{literalinclude} /_static/dsPost.flux
:language: asymptote
```

```{literalinclude} /_static/dsPost.flux
:language: augeas
```

```{literalinclude} /_static/dsPost.flux
:language: autoit
```

```{literalinclude} /_static/dsPost.flux
:language: autohotkey
```

```{literalinclude} /_static/dsPost.flux
:language: awk
```

```{literalinclude} /_static/dsPost.flux
:language: bbcbasic
```

```{literalinclude} /_static/dsPost.flux
:language: bbcode
```

```{literalinclude} /_static/dsPost.flux
:language: bc
```

```{literalinclude} /_static/dsPost.flux
:language: bqn
```

```{literalinclude} /_static/dsPost.flux
:language: bst
```

```{literalinclude} /_static/dsPost.flux
:language: bare
```

```{literalinclude} /_static/dsPost.flux
:language: basemake
```

```{literalinclude} /_static/dsPost.flux
:language: bash
```

```{literalinclude} /_static/dsPost.flux
:language: console
```

```{literalinclude} /_static/dsPost.flux
:language: batch
```

```{literalinclude} /_static/dsPost.flux
:language: bdd
```

```{literalinclude} /_static/dsPost.flux
:language: befunge
```

```{literalinclude} /_static/dsPost.flux
:language: berry
```

```{literalinclude} /_static/dsPost.flux
:language: bibtex
```

```{literalinclude} /_static/dsPost.flux
:language: blitzbasic
```

```{literalinclude} /_static/dsPost.flux
:language: blitzmax
```

```{literalinclude} /_static/dsPost.flux
:language: blueprint
```

```{literalinclude} /_static/dsPost.flux
:language: bnf
```

```{literalinclude} /_static/dsPost.flux
:language: boa
```

```{literalinclude} /_static/dsPost.flux
:language: boo
```

```{literalinclude} /_static/dsPost.flux
:language: boogie
```

```{literalinclude} /_static/dsPost.flux
:language: brainfuck
```

```{literalinclude} /_static/dsPost.flux
:language: bugs
```

```{literalinclude} /_static/dsPost.flux
:language: camkes
```

```{literalinclude} /_static/dsPost.flux
:language: c
```

```{literalinclude} /_static/dsPost.flux
:language: cmake
```

```{literalinclude} /_static/dsPost.flux
:language: c-objdump
```

```{literalinclude} /_static/dsPost.flux
:language: cpsa
```

```{literalinclude} /_static/dsPost.flux
:language: css+ul4
```

```{literalinclude} /_static/dsPost.flux
:language: aspx-cs
```

```{literalinclude} /_static/dsPost.flux
:language: csharp
```

```{literalinclude} /_static/dsPost.flux
:language: ca65
```

```{literalinclude} /_static/dsPost.flux
:language: cadl
```

```{literalinclude} /_static/dsPost.flux
:language: capdl
```

```{literalinclude} /_static/dsPost.flux
:language: capnp
```

```{literalinclude} /_static/dsPost.flux
:language: carbon
```

```{literalinclude} /_static/dsPost.flux
:language: cbmbas
```

```{literalinclude} /_static/dsPost.flux
:language: cddl
```

```{literalinclude} /_static/dsPost.flux
:language: ceylon
```

```{literalinclude} /_static/dsPost.flux
:language: cfengine3
```

```{literalinclude} /_static/dsPost.flux
:language: chaiscript
```

```{literalinclude} /_static/dsPost.flux
:language: chapel
```

```{literalinclude} /_static/dsPost.flux
:language: charmci
```

```{literalinclude} /_static/dsPost.flux
:language: html+cheetah
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+cheetah
```

```{literalinclude} /_static/dsPost.flux
:language: cheetah
```

```{literalinclude} /_static/dsPost.flux
:language: xml+cheetah
```

```{literalinclude} /_static/dsPost.flux
:language: cirru
```

```{literalinclude} /_static/dsPost.flux
:language: clay
```

```{literalinclude} /_static/dsPost.flux
:language: clean
```

```{literalinclude} /_static/dsPost.flux
:language: clojure
```

```{literalinclude} /_static/dsPost.flux
:language: clojurescript
```

```{literalinclude} /_static/dsPost.flux
:language: cobolfree
```

```{literalinclude} /_static/dsPost.flux
:language: cobol
```

```{literalinclude} /_static/dsPost.flux
:language: codeql
```

```{literalinclude} /_static/dsPost.flux
:language: coffeescript
```

```{literalinclude} /_static/dsPost.flux
:language: cfc
```

```{literalinclude} /_static/dsPost.flux
:language: cfm
```

```{literalinclude} /_static/dsPost.flux
:language: cfs
```

```{literalinclude} /_static/dsPost.flux
:language: comal
```

```{literalinclude} /_static/dsPost.flux
:language: common-lisp
```

```{literalinclude} /_static/dsPost.flux
:language: componentpascal
```

```{literalinclude} /_static/dsPost.flux
:language: coq
```

```{literalinclude} /_static/dsPost.flux
:language: cplint
```

```{literalinclude} /_static/dsPost.flux
:language: cpp
```

```{literalinclude} /_static/dsPost.flux
:language: cpp-objdump
```

```{literalinclude} /_static/dsPost.flux
:language: crmsh
```

```{literalinclude} /_static/dsPost.flux
:language: croc
```

```{literalinclude} /_static/dsPost.flux
:language: cryptol
```

```{literalinclude} /_static/dsPost.flux
:language: cr
```

```{literalinclude} /_static/dsPost.flux
:language: csound-document
```

```{literalinclude} /_static/dsPost.flux
:language: csound
```

```{literalinclude} /_static/dsPost.flux
:language: csound-score
```

```{literalinclude} /_static/dsPost.flux
:language: css+django
```

```{literalinclude} /_static/dsPost.flux
:language: css+ruby
```

```{literalinclude} /_static/dsPost.flux
:language: css+genshitext
```

```{literalinclude} /_static/dsPost.flux
:language: css
```

```{literalinclude} /_static/dsPost.flux
:language: css+php
```

```{literalinclude} /_static/dsPost.flux
:language: css+smarty
```

```{literalinclude} /_static/dsPost.flux
:language: cuda
```

```{literalinclude} /_static/dsPost.flux
:language: cypher
```

```{literalinclude} /_static/dsPost.flux
:language: cython
```

```{literalinclude} /_static/dsPost.flux
:language: d
```

```{literalinclude} /_static/dsPost.flux
:language: d-objdump
```

```{literalinclude} /_static/dsPost.flux
:language: dpatch
```

```{literalinclude} /_static/dsPost.flux
:language: dart
```

```{literalinclude} /_static/dsPost.flux
:language: dasm16
```

```{literalinclude} /_static/dsPost.flux
:language: dax
```

```{literalinclude} /_static/dsPost.flux
:language: debcontrol
```

```{literalinclude} /_static/dsPost.flux
:language: debian.sources
```

```{literalinclude} /_static/dsPost.flux
:language: delphi
```

```{literalinclude} /_static/dsPost.flux
:language: desktop
```

```{literalinclude} /_static/dsPost.flux
:language: devicetree
```

```{literalinclude} /_static/dsPost.flux
:language: dg
```

```{literalinclude} /_static/dsPost.flux
:language: diff
```

```{literalinclude} /_static/dsPost.flux
:language: django
```

```{literalinclude} /_static/dsPost.flux
:language: zone
```

```{literalinclude} /_static/dsPost.flux
:language: docker
```

```{literalinclude} /_static/dsPost.flux
:language: dtd
```

```{literalinclude} /_static/dsPost.flux
:language: duel
```

```{literalinclude} /_static/dsPost.flux
:language: dylan-console
```

```{literalinclude} /_static/dsPost.flux
:language: dylan
```

```{literalinclude} /_static/dsPost.flux
:language: dylan-lid
```

```{literalinclude} /_static/dsPost.flux
:language: ecl
```

```{literalinclude} /_static/dsPost.flux
:language: ec
```

```{literalinclude} /_static/dsPost.flux
:language: earl-grey
```

```{literalinclude} /_static/dsPost.flux
:language: easytrieve
```

```{literalinclude} /_static/dsPost.flux
:language: ebnf
```

```{literalinclude} /_static/dsPost.flux
:language: eiffel
```

```{literalinclude} /_static/dsPost.flux
:language: iex
```

```{literalinclude} /_static/dsPost.flux
:language: elixir
```

```{literalinclude} /_static/dsPost.flux
:language: elm
```

```{literalinclude} /_static/dsPost.flux
:language: elpi
```

```{literalinclude} /_static/dsPost.flux
:language: emacs-lisp
```

```{literalinclude} /_static/dsPost.flux
:language: email
```

```{literalinclude} /_static/dsPost.flux
:language: erb
```

```{literalinclude} /_static/dsPost.flux
:language: erlang
```

```{literalinclude} /_static/dsPost.flux
:language: erl
```

```{literalinclude} /_static/dsPost.flux
:language: html+evoque
```

```{literalinclude} /_static/dsPost.flux
:language: evoque
```

```{literalinclude} /_static/dsPost.flux
:language: xml+evoque
```

```{literalinclude} /_static/dsPost.flux
:language: execline
```

```{literalinclude} /_static/dsPost.flux
:language: ezhil
```

```{literalinclude} /_static/dsPost.flux
:language: fsharp
```

```{literalinclude} /_static/dsPost.flux
:language: fstar
```

```{literalinclude} /_static/dsPost.flux
:language: factor
```

```{literalinclude} /_static/dsPost.flux
:language: fancy
```

```{literalinclude} /_static/dsPost.flux
:language: fan
```

```{literalinclude} /_static/dsPost.flux
:language: felix
```

```{literalinclude} /_static/dsPost.flux
:language: fennel
```

```{literalinclude} /_static/dsPost.flux
:language: fift
```

```{literalinclude} /_static/dsPost.flux
:language: fish
```

```{literalinclude} /_static/dsPost.flux
:language: flatline
```

```{literalinclude} /_static/dsPost.flux
:language: floscript
```

```{literalinclude} /_static/dsPost.flux
:language: forth
```

```{literalinclude} /_static/dsPost.flux
:language: fortranfixed
```

```{literalinclude} /_static/dsPost.flux
:language: fortran
```

```{literalinclude} /_static/dsPost.flux
:language: foxpro
```

```{literalinclude} /_static/dsPost.flux
:language: freefem
```

```{literalinclude} /_static/dsPost.flux
:language: func
```

```{literalinclude} /_static/dsPost.flux
:language: futhark
```

```{literalinclude} /_static/dsPost.flux
:language: gap-console
```

```{literalinclude} /_static/dsPost.flux
:language: gap
```

```{literalinclude} /_static/dsPost.flux
:language: gdscript
```

```{literalinclude} /_static/dsPost.flux
:language: glsl
```

```{literalinclude} /_static/dsPost.flux
:language: gsql
```

```{literalinclude} /_static/dsPost.flux
:language: gas
```

```{literalinclude} /_static/dsPost.flux
:language: gcode
```

```{literalinclude} /_static/dsPost.flux
:language: genshi
```

```{literalinclude} /_static/dsPost.flux
:language: genshitext
```

```{literalinclude} /_static/dsPost.flux
:language: pot
```

```{literalinclude} /_static/dsPost.flux
:language: gherkin
```

```{literalinclude} /_static/dsPost.flux
:language: gleam
```

```{literalinclude} /_static/dsPost.flux
:language: gnuplot
```

```{literalinclude} /_static/dsPost.flux
:language: go
```

```{literalinclude} /_static/dsPost.flux
:language: golo
```

```{literalinclude} /_static/dsPost.flux
:language: gooddata-cl
```

```{literalinclude} /_static/dsPost.flux
:language: googlesql
```

```{literalinclude} /_static/dsPost.flux
:language: gosu
```

```{literalinclude} /_static/dsPost.flux
:language: gst
```

```{literalinclude} /_static/dsPost.flux
:language: graphql
```

```{literalinclude} /_static/dsPost.flux
:language: graphviz
```

```{literalinclude} /_static/dsPost.flux
:language: groff
```

```{literalinclude} /_static/dsPost.flux
:language: groovy
```

```{literalinclude} /_static/dsPost.flux
:language: hlsl
```

```{literalinclude} /_static/dsPost.flux
:language: html+ul4
```

```{literalinclude} /_static/dsPost.flux
:language: haml
```

```{literalinclude} /_static/dsPost.flux
:language: html+handlebars
```

```{literalinclude} /_static/dsPost.flux
:language: handlebars
```

```{literalinclude} /_static/dsPost.flux
:language: hare
```

```{literalinclude} /_static/dsPost.flux
:language: haskell
```

```{literalinclude} /_static/dsPost.flux
:language: haxe
```

```{literalinclude} /_static/dsPost.flux
:language: hexdump
```

```{literalinclude} /_static/dsPost.flux
:language: hsail
```

```{literalinclude} /_static/dsPost.flux
:language: hspec
```

```{literalinclude} /_static/dsPost.flux
:language: html+django
```

```{literalinclude} /_static/dsPost.flux
:language: html+genshi
```

```{literalinclude} /_static/dsPost.flux
:language: html
```

```{literalinclude} /_static/dsPost.flux
:language: html+php
```

```{literalinclude} /_static/dsPost.flux
:language: html+smarty
```

```{literalinclude} /_static/dsPost.flux
:language: http
```

```{literalinclude} /_static/dsPost.flux
:language: haxeml
```

```{literalinclude} /_static/dsPost.flux
:language: hylang
```

```{literalinclude} /_static/dsPost.flux
:language: hybris
```

```{literalinclude} /_static/dsPost.flux
:language: idl
```

```{literalinclude} /_static/dsPost.flux
:language: icon
```

```{literalinclude} /_static/dsPost.flux
:language: idris
```

```{literalinclude} /_static/dsPost.flux
:language: igor
```

```{literalinclude} /_static/dsPost.flux
:language: inform6
```

```{literalinclude} /_static/dsPost.flux
:language: i6t
```

```{literalinclude} /_static/dsPost.flux
:language: inform7
```

```{literalinclude} /_static/dsPost.flux
:language: ini
```

```{literalinclude} /_static/dsPost.flux
:language: io
```

```{literalinclude} /_static/dsPost.flux
:language: ioke
```

```{literalinclude} /_static/dsPost.flux
:language: irc
```

```{literalinclude} /_static/dsPost.flux
:language: isabelle
```

```{literalinclude} /_static/dsPost.flux
:language: j
```

```{literalinclude} /_static/dsPost.flux
:language: jmespath
```

```{literalinclude} /_static/dsPost.flux
:language: jslt
```

```{literalinclude} /_static/dsPost.flux
:language: jags
```

```{literalinclude} /_static/dsPost.flux
:language: janet
```

```{literalinclude} /_static/dsPost.flux
:language: jasmin
```

```{literalinclude} /_static/dsPost.flux
:language: java
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+django
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+ruby
```

```{literalinclude} /_static/dsPost.flux
:language: js+genshitext
```

```{literalinclude} /_static/dsPost.flux
:language: javascript
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+php
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+smarty
```

```{literalinclude} /_static/dsPost.flux
:language: js+ul4
```

```{literalinclude} /_static/dsPost.flux
:language: jcl
```

```{literalinclude} /_static/dsPost.flux
:language: jsgf
```

```{literalinclude} /_static/dsPost.flux
:language: json5
```

```{literalinclude} /_static/dsPost.flux
:language: jsonld
```

```{literalinclude} /_static/dsPost.flux
:language: json
```

```{literalinclude} /_static/dsPost.flux
:language: jsonnet
```

```{literalinclude} /_static/dsPost.flux
:language: jsp
```

```{literalinclude} /_static/dsPost.flux
:language: jsx
```

```{literalinclude} /_static/dsPost.flux
:language: jlcon
```

```{literalinclude} /_static/dsPost.flux
:language: julia
```

```{literalinclude} /_static/dsPost.flux
:language: juttle
```

```{literalinclude} /_static/dsPost.flux
:language: k
```

```{literalinclude} /_static/dsPost.flux
:language: kal
```

```{literalinclude} /_static/dsPost.flux
:language: kconfig
```

```{literalinclude} /_static/dsPost.flux
:language: kmsg
```

```{literalinclude} /_static/dsPost.flux
:language: koka
```

```{literalinclude} /_static/dsPost.flux
:language: kotlin
```

```{literalinclude} /_static/dsPost.flux
:language: kuin
```

```{literalinclude} /_static/dsPost.flux
:language: kql
```

```{literalinclude} /_static/dsPost.flux
:language: lsl
```

```{literalinclude} /_static/dsPost.flux
:language: css+lasso
```

```{literalinclude} /_static/dsPost.flux
:language: html+lasso
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+lasso
```

```{literalinclude} /_static/dsPost.flux
:language: lasso
```

```{literalinclude} /_static/dsPost.flux
:language: xml+lasso
```

```{literalinclude} /_static/dsPost.flux
:language: ldapconf
```

```{literalinclude} /_static/dsPost.flux
:language: ldif
```

```{literalinclude} /_static/dsPost.flux
:language: lean
```

```{literalinclude} /_static/dsPost.flux
:language: lean4
```

```{literalinclude} /_static/dsPost.flux
:language: less
```

```{literalinclude} /_static/dsPost.flux
:language: lighttpd
```

```{literalinclude} /_static/dsPost.flux
:language: lilypond
```

```{literalinclude} /_static/dsPost.flux
:language: limbo
```

```{literalinclude} /_static/dsPost.flux
:language: liquid
```

```{literalinclude} /_static/dsPost.flux
:language: literate-agda
```

```{literalinclude} /_static/dsPost.flux
:language: literate-cryptol
```

```{literalinclude} /_static/dsPost.flux
:language: literate-haskell
```

```{literalinclude} /_static/dsPost.flux
:language: literate-idris
```

```{literalinclude} /_static/dsPost.flux
:language: livescript
```

```{literalinclude} /_static/dsPost.flux
:language: llvm
```

```{literalinclude} /_static/dsPost.flux
:language: llvm-mir-body
```

```{literalinclude} /_static/dsPost.flux
:language: llvm-mir
```

```{literalinclude} /_static/dsPost.flux
:language: logos
```

```{literalinclude} /_static/dsPost.flux
:language: logtalk
```

```{literalinclude} /_static/dsPost.flux
:language: lua
```

```{literalinclude} /_static/dsPost.flux
:language: luau
```

```{literalinclude} /_static/dsPost.flux
:language: mcfunction
```

```{literalinclude} /_static/dsPost.flux
:language: mcschema
```

```{literalinclude} /_static/dsPost.flux
:language: mime
```

```{literalinclude} /_static/dsPost.flux
:language: mips
```

```{literalinclude} /_static/dsPost.flux
:language: moocode
```

```{literalinclude} /_static/dsPost.flux
:language: doscon
```

```{literalinclude} /_static/dsPost.flux
:language: macaulay2
```

```{literalinclude} /_static/dsPost.flux
:language: make
```

```{literalinclude} /_static/dsPost.flux
:language: css+mako
```

```{literalinclude} /_static/dsPost.flux
:language: html+mako
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+mako
```

```{literalinclude} /_static/dsPost.flux
:language: mako
```

```{literalinclude} /_static/dsPost.flux
:language: xml+mako
```

```{literalinclude} /_static/dsPost.flux
:language: maple
```

```{literalinclude} /_static/dsPost.flux
:language: maql
```

```{literalinclude} /_static/dsPost.flux
:language: markdown
```

```{literalinclude} /_static/dsPost.flux
:language: mask
```

```{literalinclude} /_static/dsPost.flux
:language: mason
```

```{literalinclude} /_static/dsPost.flux
:language: mathematica
```

```{literalinclude} /_static/dsPost.flux
:language: matlab
```

```{literalinclude} /_static/dsPost.flux
:language: matlabsession
```

```{literalinclude} /_static/dsPost.flux
:language: maxima
```

```{literalinclude} /_static/dsPost.flux
:language: meson
```

```{literalinclude} /_static/dsPost.flux
:language: minid
```

```{literalinclude} /_static/dsPost.flux
:language: miniscript
```

```{literalinclude} /_static/dsPost.flux
:language: modelica
```

```{literalinclude} /_static/dsPost.flux
:language: modula2
```

```{literalinclude} /_static/dsPost.flux
:language: trac-wiki
```

```{literalinclude} /_static/dsPost.flux
:language: mojo
```

```{literalinclude} /_static/dsPost.flux
:language: monkey
```

```{literalinclude} /_static/dsPost.flux
:language: monte
```

```{literalinclude} /_static/dsPost.flux
:language: moonscript
```

```{literalinclude} /_static/dsPost.flux
:language: mosel
```

```{literalinclude} /_static/dsPost.flux
:language: css+mozpreproc
```

```{literalinclude} /_static/dsPost.flux
:language: mozhashpreproc
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+mozpreproc
```

```{literalinclude} /_static/dsPost.flux
:language: mozpercentpreproc
```

```{literalinclude} /_static/dsPost.flux
:language: xul+mozpreproc
```

```{literalinclude} /_static/dsPost.flux
:language: mql
```

```{literalinclude} /_static/dsPost.flux
:language: mscgen
```

```{literalinclude} /_static/dsPost.flux
:language: mupad
```

```{literalinclude} /_static/dsPost.flux
:language: mxml
```

```{literalinclude} /_static/dsPost.flux
:language: mysql
```

```{literalinclude} /_static/dsPost.flux
:language: css+myghty
```

```{literalinclude} /_static/dsPost.flux
:language: html+myghty
```

```{literalinclude} /_static/dsPost.flux
:language: javascript+myghty
```

```{literalinclude} /_static/dsPost.flux
:language: myghty
```

```{literalinclude} /_static/dsPost.flux
:language: xml+myghty
```

```{literalinclude} /_static/dsPost.flux
:language: ncl
```

```{literalinclude} /_static/dsPost.flux
:language: nsis
```

```{literalinclude} /_static/dsPost.flux
:language: nasm
```

```{literalinclude} /_static/dsPost.flux
:language: objdump-nasm
```

```{literalinclude} /_static/dsPost.flux
:language: nemerle
```

```{literalinclude} /_static/dsPost.flux
:language: nesc
```

```{literalinclude} /_static/dsPost.flux
:language: nestedtext
```

```{literalinclude} /_static/dsPost.flux
:language: newlisp
```

```{literalinclude} /_static/dsPost.flux
:language: newspeak
```

```{literalinclude} /_static/dsPost.flux
:language: nginx
```

```{literalinclude} /_static/dsPost.flux
:language: nimrod
```

```{literalinclude} /_static/dsPost.flux
:language: nit
```

```{literalinclude} /_static/dsPost.flux
:language: nixos
```

```{literalinclude} /_static/dsPost.flux
:language: nodejsrepl
```

```{literalinclude} /_static/dsPost.flux
:language: notmuch
```

```{literalinclude} /_static/dsPost.flux
:language: nusmv
```

```{literalinclude} /_static/dsPost.flux
:language: numpy
```

```{literalinclude} /_static/dsPost.flux
:language: numba_ir
```

```{literalinclude} /_static/dsPost.flux
:language: objdump
```

```{literalinclude} /_static/dsPost.flux
:language: objective-c
```

```{literalinclude} /_static/dsPost.flux
:language: objective-c++
```

```{literalinclude} /_static/dsPost.flux
:language: objective-j
```

```{literalinclude} /_static/dsPost.flux
:language: ocaml
```

```{literalinclude} /_static/dsPost.flux
:language: octave
```

```{literalinclude} /_static/dsPost.flux
:language: odin
```

```{literalinclude} /_static/dsPost.flux
:language: omg-idl
```

```{literalinclude} /_static/dsPost.flux
:language: ooc
```

```{literalinclude} /_static/dsPost.flux
:language: opa
```

```{literalinclude} /_static/dsPost.flux
:language: openedge
```

```{literalinclude} /_static/dsPost.flux
:language: openscad
```

```{literalinclude} /_static/dsPost.flux
:language: org
```

```{literalinclude} /_static/dsPost.flux
:language: output
```

```{literalinclude} /_static/dsPost.flux
:language: pacmanconf
```

```{literalinclude} /_static/dsPost.flux
:language: pan
```

```{literalinclude} /_static/dsPost.flux
:language: parasail
```

```{literalinclude} /_static/dsPost.flux
:language: pawn
```

```{literalinclude} /_static/dsPost.flux
:language: pddl
```

```{literalinclude} /_static/dsPost.flux
:language: peg
```

```{literalinclude} /_static/dsPost.flux
:language: perl6
```

```{literalinclude} /_static/dsPost.flux
:language: perl
```

```{literalinclude} /_static/dsPost.flux
:language: phix
```

```{literalinclude} /_static/dsPost.flux
:language: php
```

```{literalinclude} /_static/dsPost.flux
:language: pig
```

```{literalinclude} /_static/dsPost.flux
:language: pike
```

```{literalinclude} /_static/dsPost.flux
:language: pkgconfig
```

```{literalinclude} /_static/dsPost.flux
:language: plpgsql
```

```{literalinclude} /_static/dsPost.flux
:language: pointless
```

```{literalinclude} /_static/dsPost.flux
:language: pony
```

```{literalinclude} /_static/dsPost.flux
:language: portugol
```

```{literalinclude} /_static/dsPost.flux
:language: postscript
```

```{literalinclude} /_static/dsPost.flux
:language: psql
```

```{literalinclude} /_static/dsPost.flux
:language: postgres-explain
```

```{literalinclude} /_static/dsPost.flux
:language: postgresql
```

```{literalinclude} /_static/dsPost.flux
:language: pov
```

```{literalinclude} /_static/dsPost.flux
:language: powershell
```

```{literalinclude} /_static/dsPost.flux
:language: pwsh-session
```

```{literalinclude} /_static/dsPost.flux
:language: praat
```

```{literalinclude} /_static/dsPost.flux
:language: procfile
```

```{literalinclude} /_static/dsPost.flux
:language: prolog
```

```{literalinclude} /_static/dsPost.flux
:language: promql
```

```{literalinclude} /_static/dsPost.flux
:language: promela
```

```{literalinclude} /_static/dsPost.flux
:language: properties
```

```{literalinclude} /_static/dsPost.flux
:language: protobuf
```

```{literalinclude} /_static/dsPost.flux
:language: prql
```

```{literalinclude} /_static/dsPost.flux
:language: psysh
```

```{literalinclude} /_static/dsPost.flux
:language: ptx
```

```{literalinclude} /_static/dsPost.flux
:language: pug
```

```{literalinclude} /_static/dsPost.flux
:language: puppet
```

```{literalinclude} /_static/dsPost.flux
:language: pypylog
```

```{literalinclude} /_static/dsPost.flux
:language: python2
```

```{literalinclude} /_static/dsPost.flux
:language: py2tb
```

```{literalinclude} /_static/dsPost.flux
:language: pycon
```

```{literalinclude} /_static/dsPost.flux
:language: python
```

```{literalinclude} /_static/dsPost.flux
:language: pytb
```

```{literalinclude} /_static/dsPost.flux
:language: py+ul4
```

```{literalinclude} /_static/dsPost.flux
:language: qbasic
```

```{literalinclude} /_static/dsPost.flux
:language: q
```

```{literalinclude} /_static/dsPost.flux
:language: qvto
```

```{literalinclude} /_static/dsPost.flux
:language: qlik
```

```{literalinclude} /_static/dsPost.flux
:language: qml
```

```{literalinclude} /_static/dsPost.flux
:language: rconsole
```

```{literalinclude} /_static/dsPost.flux
:language: rng-compact
```

```{literalinclude} /_static/dsPost.flux
:language: spec
```

```{literalinclude} /_static/dsPost.flux
:language: racket
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-c
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-cpp
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-d
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-em
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-java
```

```{literalinclude} /_static/dsPost.flux
:language: ragel
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-objc
```

```{literalinclude} /_static/dsPost.flux
:language: ragel-ruby
```

```{literalinclude} /_static/dsPost.flux
:language: rd
```

```{literalinclude} /_static/dsPost.flux
:language: reasonml
```

```{literalinclude} /_static/dsPost.flux
:language: rebol
```

```{literalinclude} /_static/dsPost.flux
:language: red
```

```{literalinclude} /_static/dsPost.flux
:language: redcode
```

```{literalinclude} /_static/dsPost.flux
:language: registry
```

```{literalinclude} /_static/dsPost.flux
:language: rego
```

```{literalinclude} /_static/dsPost.flux
:language: resourcebundle
```

```{literalinclude} /_static/dsPost.flux
:language: rexx
```

```{literalinclude} /_static/dsPost.flux
:language: rhtml
```

```{literalinclude} /_static/dsPost.flux
:language: ride
```

```{literalinclude} /_static/dsPost.flux
:language: rita
```

```{literalinclude} /_static/dsPost.flux
:language: roboconf-graph
```

```{literalinclude} /_static/dsPost.flux
:language: roboconf-instances
```

```{literalinclude} /_static/dsPost.flux
:language: robotframework
```

```{literalinclude} /_static/dsPost.flux
:language: rql
```

```{literalinclude} /_static/dsPost.flux
:language: rsl
```

```{literalinclude} /_static/dsPost.flux
:language: restructuredtext
```

```{literalinclude} /_static/dsPost.flux
:language: trafficscript
```

```{literalinclude} /_static/dsPost.flux
:language: rbcon
```

```{literalinclude} /_static/dsPost.flux
:language: ruby
```

```{literalinclude} /_static/dsPost.flux
:language: rust
```

```{literalinclude} /_static/dsPost.flux
:language: sas
```

```{literalinclude} /_static/dsPost.flux
:language: splus
```

```{literalinclude} /_static/dsPost.flux
:language: sml
```

```{literalinclude} /_static/dsPost.flux
:language: snbt
```

```{literalinclude} /_static/dsPost.flux
:language: sarl
```

```{literalinclude} /_static/dsPost.flux
:language: sass
```

```{literalinclude} /_static/dsPost.flux
:language: savi
```

```{literalinclude} /_static/dsPost.flux
:language: scala
```

```{literalinclude} /_static/dsPost.flux
:language: scaml
```

```{literalinclude} /_static/dsPost.flux
:language: scdoc
```

```{literalinclude} /_static/dsPost.flux
:language: scheme
```

```{literalinclude} /_static/dsPost.flux
:language: scilab
```

```{literalinclude} /_static/dsPost.flux
:language: scss
```

```{literalinclude} /_static/dsPost.flux
:language: sed
```

```{literalinclude} /_static/dsPost.flux
:language: shexc
```

```{literalinclude} /_static/dsPost.flux
:language: shen
```

```{literalinclude} /_static/dsPost.flux
:language: sieve
```

```{literalinclude} /_static/dsPost.flux
:language: silver
```

```{literalinclude} /_static/dsPost.flux
:language: singularity
```

```{literalinclude} /_static/dsPost.flux
:language: slash
```

```{literalinclude} /_static/dsPost.flux
:language: slim
```

```{literalinclude} /_static/dsPost.flux
:language: slurm
```

```{literalinclude} /_static/dsPost.flux
:language: smali
```

```{literalinclude} /_static/dsPost.flux
:language: smalltalk
```

```{literalinclude} /_static/dsPost.flux
:language: sgf
```

```{literalinclude} /_static/dsPost.flux
:language: smarty
```

```{literalinclude} /_static/dsPost.flux
:language: smithy
```

```{literalinclude} /_static/dsPost.flux
:language: snobol
```

```{literalinclude} /_static/dsPost.flux
:language: snowball
```

```{literalinclude} /_static/dsPost.flux
:language: solidity
```

```{literalinclude} /_static/dsPost.flux
:language: androidbp
```

```{literalinclude} /_static/dsPost.flux
:language: sophia
```

```{literalinclude} /_static/dsPost.flux
:language: sp
```

```{literalinclude} /_static/dsPost.flux
:language: debsources
```

```{literalinclude} /_static/dsPost.flux
:language: sparql
```

```{literalinclude} /_static/dsPost.flux
:language: spice
```

```{literalinclude} /_static/dsPost.flux
:language: sql+jinja
```

```{literalinclude} /_static/dsPost.flux
:language: sql
```

```{literalinclude} /_static/dsPost.flux
:language: sqlite3
```

```{literalinclude} /_static/dsPost.flux
:language: squidconf
```

```{literalinclude} /_static/dsPost.flux
:language: srcinfo
```

```{literalinclude} /_static/dsPost.flux
:language: ssp
```

```{literalinclude} /_static/dsPost.flux
:language: stan
```

```{literalinclude} /_static/dsPost.flux
:language: stata
```

```{literalinclude} /_static/dsPost.flux
:language: supercollider
```

```{literalinclude} /_static/dsPost.flux
:language: swift
```

```{literalinclude} /_static/dsPost.flux
:language: swig
```

```{literalinclude} /_static/dsPost.flux
:language: systemverilog
```

```{literalinclude} /_static/dsPost.flux
:language: systemd
```

```{literalinclude} /_static/dsPost.flux
:language: tap
```

```{literalinclude} /_static/dsPost.flux
:language: tnt
```

```{literalinclude} /_static/dsPost.flux
:language: toml
```

```{literalinclude} /_static/dsPost.flux
:language: tablegen
```

```{literalinclude} /_static/dsPost.flux
:language: tact
```

```{literalinclude} /_static/dsPost.flux
:language: tads3
```

```{literalinclude} /_static/dsPost.flux
:language: tal
```

```{literalinclude} /_static/dsPost.flux
:language: tasm
```

```{literalinclude} /_static/dsPost.flux
:language: tcl
```

```{literalinclude} /_static/dsPost.flux
:language: tcsh
```

```{literalinclude} /_static/dsPost.flux
:language: tcshcon
```

```{literalinclude} /_static/dsPost.flux
:language: tea
```

```{literalinclude} /_static/dsPost.flux
:language: teal
```

```{literalinclude} /_static/dsPost.flux
:language: teratermmacro
```

```{literalinclude} /_static/dsPost.flux
:language: termcap
```

```{literalinclude} /_static/dsPost.flux
:language: terminfo
```

```{literalinclude} /_static/dsPost.flux
:language: terraform
```

```{literalinclude} /_static/dsPost.flux
:language: tex
```

```{literalinclude} /_static/dsPost.flux
:language: text
```

```{literalinclude} /_static/dsPost.flux
:language: ti
```

```{literalinclude} /_static/dsPost.flux
:language: thrift
```

```{literalinclude} /_static/dsPost.flux
:language: tid
```

```{literalinclude} /_static/dsPost.flux
:language: tlb
```

```{literalinclude} /_static/dsPost.flux
:language: tls
```

```{literalinclude} /_static/dsPost.flux
:language: todotxt
```

```{literalinclude} /_static/dsPost.flux
:language: tsql
```

```{literalinclude} /_static/dsPost.flux
:language: treetop
```

```{literalinclude} /_static/dsPost.flux
:language: tsx
```

```{literalinclude} /_static/dsPost.flux
:language: turtle
```

```{literalinclude} /_static/dsPost.flux
:language: html+twig
```

```{literalinclude} /_static/dsPost.flux
:language: twig
```

```{literalinclude} /_static/dsPost.flux
:language: typescript
```

```{literalinclude} /_static/dsPost.flux
:language: typoscriptcssdata
```

```{literalinclude} /_static/dsPost.flux
:language: typoscripthtmldata
```

```{literalinclude} /_static/dsPost.flux
:language: typoscript
```

```{literalinclude} /_static/dsPost.flux
:language: typst
```

```{literalinclude} /_static/dsPost.flux
:language: ul4
```

```{literalinclude} /_static/dsPost.flux
:language: ucode
```

```{literalinclude} /_static/dsPost.flux
:language: unicon
```

```{literalinclude} /_static/dsPost.flux
:language: unixconfig
```

```{literalinclude} /_static/dsPost.flux
:language: urbiscript
```

```{literalinclude} /_static/dsPost.flux
:language: urlencoded
```

```{literalinclude} /_static/dsPost.flux
:language: usd
```

```{literalinclude} /_static/dsPost.flux
:language: vbscript
```

```{literalinclude} /_static/dsPost.flux
:language: vcl
```

```{literalinclude} /_static/dsPost.flux
:language: vclsnippets
```

```{literalinclude} /_static/dsPost.flux
:language: vctreestatus
```

```{literalinclude} /_static/dsPost.flux
:language: vgl
```

```{literalinclude} /_static/dsPost.flux
:language: vala
```

```{literalinclude} /_static/dsPost.flux
:language: aspx-vb
```

```{literalinclude} /_static/dsPost.flux
:language: vb.net
```

```{literalinclude} /_static/dsPost.flux
:language: html+velocity
```

```{literalinclude} /_static/dsPost.flux
:language: velocity
```

```{literalinclude} /_static/dsPost.flux
:language: xml+velocity
```

```{literalinclude} /_static/dsPost.flux
:language: verifpal
```

```{literalinclude} /_static/dsPost.flux
:language: verilog
```

```{literalinclude} /_static/dsPost.flux
:language: vhdl
```

```{literalinclude} /_static/dsPost.flux
:language: vim
```

```{literalinclude} /_static/dsPost.flux
:language: visualprologgrammar
```

```{literalinclude} /_static/dsPost.flux
:language: visualprolog
```

```{literalinclude} /_static/dsPost.flux
:language: vue
```

```{literalinclude} /_static/dsPost.flux
:language: vyper
```

```{literalinclude} /_static/dsPost.flux
:language: wdiff
```

```{literalinclude} /_static/dsPost.flux
:language: wast
```

```{literalinclude} /_static/dsPost.flux
:language: webidl
```

```{literalinclude} /_static/dsPost.flux
:language: wgsl
```

```{literalinclude} /_static/dsPost.flux
:language: whiley
```

```{literalinclude} /_static/dsPost.flux
:language: wikitext
```

```{literalinclude} /_static/dsPost.flux
:language: wowtoc
```

```{literalinclude} /_static/dsPost.flux
:language: wren
```

```{literalinclude} /_static/dsPost.flux
:language: x10
```

```{literalinclude} /_static/dsPost.flux
:language: xml+ul4
```

```{literalinclude} /_static/dsPost.flux
:language: xquery
```

```{literalinclude} /_static/dsPost.flux
:language: xml+django
```

```{literalinclude} /_static/dsPost.flux
:language: xml+ruby
```

```{literalinclude} /_static/dsPost.flux
:language: xml
```

```{literalinclude} /_static/dsPost.flux
:language: xml+php
```

```{literalinclude} /_static/dsPost.flux
:language: xml+smarty
```

```{literalinclude} /_static/dsPost.flux
:language: xorg.conf
```

```{literalinclude} /_static/dsPost.flux
:language: xpp
```

```{literalinclude} /_static/dsPost.flux
:language: xslt
```

```{literalinclude} /_static/dsPost.flux
:language: xtend
```

```{literalinclude} /_static/dsPost.flux
:language: extempore
```

```{literalinclude} /_static/dsPost.flux
:language: yaml+jinja
```

```{literalinclude} /_static/dsPost.flux
:language: yaml
```

```{literalinclude} /_static/dsPost.flux
:language: yang
```

```{literalinclude} /_static/dsPost.flux
:language: yara
```

```{literalinclude} /_static/dsPost.flux
:language: zeek
```

```{literalinclude} /_static/dsPost.flux
:language: zephir
```

```{literalinclude} /_static/dsPost.flux
:language: zig
```

```{literalinclude} /_static/dsPost.flux
:language: ansys
```

### Update Queries

TODO [dsGrafana.json](/_static/dsGrafana.json)

TODO toFloat()
