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
:language: text
```

### Update Queries

TODO [dsGrafana.json](/_static/dsGrafana.json)

TODO toFloat()

#### abap

```{literalinclude} /_static/dsPost.flux
:language: abap
```

#### amdgpu

```{literalinclude} /_static/dsPost.flux
:language: amdgpu
```

#### apl

```{literalinclude} /_static/dsPost.flux
:language: apl
```

#### abnf

```{literalinclude} /_static/dsPost.flux
:language: abnf
```

#### actionscript3

```{literalinclude} /_static/dsPost.flux
:language: actionscript3
```

#### actionscript

```{literalinclude} /_static/dsPost.flux
:language: actionscript
```

#### ada

```{literalinclude} /_static/dsPost.flux
:language: ada
```

#### adl

```{literalinclude} /_static/dsPost.flux
:language: adl
```

#### agda

```{literalinclude} /_static/dsPost.flux
:language: agda
```

#### aheui

```{literalinclude} /_static/dsPost.flux
:language: aheui
```

#### alloy

```{literalinclude} /_static/dsPost.flux
:language: alloy
```

#### ambienttalk

```{literalinclude} /_static/dsPost.flux
:language: ambienttalk
```

#### ampl

```{literalinclude} /_static/dsPost.flux
:language: ampl
```

#### html+ng2

```{literalinclude} /_static/dsPost.flux
:language: html+ng2
```

#### ng2

```{literalinclude} /_static/dsPost.flux
:language: ng2
```

#### antlr-actionscript

```{literalinclude} /_static/dsPost.flux
:language: antlr-actionscript
```

#### antlr-csharp

```{literalinclude} /_static/dsPost.flux
:language: antlr-csharp
```

#### antlr-cpp

```{literalinclude} /_static/dsPost.flux
:language: antlr-cpp
```

#### antlr-java

```{literalinclude} /_static/dsPost.flux
:language: antlr-java
```

#### antlr

```{literalinclude} /_static/dsPost.flux
:language: antlr
```

#### antlr-objc

```{literalinclude} /_static/dsPost.flux
:language: antlr-objc
```

#### antlr-perl

```{literalinclude} /_static/dsPost.flux
:language: antlr-perl
```

#### antlr-python

```{literalinclude} /_static/dsPost.flux
:language: antlr-python
```

#### antlr-ruby

```{literalinclude} /_static/dsPost.flux
:language: antlr-ruby
```

#### apacheconf

```{literalinclude} /_static/dsPost.flux
:language: apacheconf
```

#### applescript

```{literalinclude} /_static/dsPost.flux
:language: applescript
```

#### arduino

```{literalinclude} /_static/dsPost.flux
:language: arduino
```

#### arrow

```{literalinclude} /_static/dsPost.flux
:language: arrow
```

#### arturo

```{literalinclude} /_static/dsPost.flux
:language: arturo
```

#### asc

```{literalinclude} /_static/dsPost.flux
:language: asc
```

#### asn1

```{literalinclude} /_static/dsPost.flux
:language: asn1
```

#### aspectj

```{literalinclude} /_static/dsPost.flux
:language: aspectj
```

#### asymptote

```{literalinclude} /_static/dsPost.flux
:language: asymptote
```

#### augeas

```{literalinclude} /_static/dsPost.flux
:language: augeas
```

#### autoit

```{literalinclude} /_static/dsPost.flux
:language: autoit
```

#### autohotkey

```{literalinclude} /_static/dsPost.flux
:language: autohotkey
```

#### awk

```{literalinclude} /_static/dsPost.flux
:language: awk
```

#### bbcbasic

```{literalinclude} /_static/dsPost.flux
:language: bbcbasic
```

#### bbcode

```{literalinclude} /_static/dsPost.flux
:language: bbcode
```

#### bc

```{literalinclude} /_static/dsPost.flux
:language: bc
```

#### bqn

```{literalinclude} /_static/dsPost.flux
:language: bqn
```

#### bst

```{literalinclude} /_static/dsPost.flux
:language: bst
```

#### bare

```{literalinclude} /_static/dsPost.flux
:language: bare
```

#### basemake

```{literalinclude} /_static/dsPost.flux
:language: basemake
```

#### bash

```{literalinclude} /_static/dsPost.flux
:language: bash
```

#### console

```{literalinclude} /_static/dsPost.flux
:language: console
```

#### batch

```{literalinclude} /_static/dsPost.flux
:language: batch
```

#### bdd

```{literalinclude} /_static/dsPost.flux
:language: bdd
```

#### befunge

```{literalinclude} /_static/dsPost.flux
:language: befunge
```

#### berry

```{literalinclude} /_static/dsPost.flux
:language: berry
```

#### bibtex

```{literalinclude} /_static/dsPost.flux
:language: bibtex
```

#### blitzbasic

```{literalinclude} /_static/dsPost.flux
:language: blitzbasic
```

#### blitzmax

```{literalinclude} /_static/dsPost.flux
:language: blitzmax
```

#### blueprint

```{literalinclude} /_static/dsPost.flux
:language: blueprint
```

#### bnf

```{literalinclude} /_static/dsPost.flux
:language: bnf
```

#### boa

```{literalinclude} /_static/dsPost.flux
:language: boa
```

#### boo

```{literalinclude} /_static/dsPost.flux
:language: boo
```

#### boogie

```{literalinclude} /_static/dsPost.flux
:language: boogie
```

#### brainfuck

```{literalinclude} /_static/dsPost.flux
:language: brainfuck
```

#### bugs

```{literalinclude} /_static/dsPost.flux
:language: bugs
```

#### camkes

```{literalinclude} /_static/dsPost.flux
:language: camkes
```

#### c

```{literalinclude} /_static/dsPost.flux
:language: c
```

#### cmake

```{literalinclude} /_static/dsPost.flux
:language: cmake
```

#### c-objdump

```{literalinclude} /_static/dsPost.flux
:language: c-objdump
```

#### cpsa

```{literalinclude} /_static/dsPost.flux
:language: cpsa
```

#### css+ul4

```{literalinclude} /_static/dsPost.flux
:language: css+ul4
```

#### aspx-cs

```{literalinclude} /_static/dsPost.flux
:language: aspx-cs
```

#### csharp

```{literalinclude} /_static/dsPost.flux
:language: csharp
```

#### ca65

```{literalinclude} /_static/dsPost.flux
:language: ca65
```

#### cadl

```{literalinclude} /_static/dsPost.flux
:language: cadl
```

#### capdl

```{literalinclude} /_static/dsPost.flux
:language: capdl
```

#### capnp

```{literalinclude} /_static/dsPost.flux
:language: capnp
```

#### carbon

```{literalinclude} /_static/dsPost.flux
:language: carbon
```

#### cbmbas

```{literalinclude} /_static/dsPost.flux
:language: cbmbas
```

#### cddl

```{literalinclude} /_static/dsPost.flux
:language: cddl
```

#### ceylon

```{literalinclude} /_static/dsPost.flux
:language: ceylon
```

#### cfengine3

```{literalinclude} /_static/dsPost.flux
:language: cfengine3
```

#### chaiscript

```{literalinclude} /_static/dsPost.flux
:language: chaiscript
```

#### chapel

```{literalinclude} /_static/dsPost.flux
:language: chapel
```

#### charmci

```{literalinclude} /_static/dsPost.flux
:language: charmci
```

#### html+cheetah

```{literalinclude} /_static/dsPost.flux
:language: html+cheetah
```

#### javascript+cheetah

```{literalinclude} /_static/dsPost.flux
:language: javascript+cheetah
```

#### cheetah

```{literalinclude} /_static/dsPost.flux
:language: cheetah
```

#### xml+cheetah

```{literalinclude} /_static/dsPost.flux
:language: xml+cheetah
```

#### cirru

```{literalinclude} /_static/dsPost.flux
:language: cirru
```

#### clay

```{literalinclude} /_static/dsPost.flux
:language: clay
```

#### clean

```{literalinclude} /_static/dsPost.flux
:language: clean
```

#### clojure

```{literalinclude} /_static/dsPost.flux
:language: clojure
```

#### clojurescript

```{literalinclude} /_static/dsPost.flux
:language: clojurescript
```

#### cobolfree

```{literalinclude} /_static/dsPost.flux
:language: cobolfree
```

#### cobol

```{literalinclude} /_static/dsPost.flux
:language: cobol
```

#### codeql

```{literalinclude} /_static/dsPost.flux
:language: codeql
```

#### coffeescript

```{literalinclude} /_static/dsPost.flux
:language: coffeescript
```

#### cfc

```{literalinclude} /_static/dsPost.flux
:language: cfc
```

#### cfm

```{literalinclude} /_static/dsPost.flux
:language: cfm
```

#### cfs

```{literalinclude} /_static/dsPost.flux
:language: cfs
```

#### comal

```{literalinclude} /_static/dsPost.flux
:language: comal
```

#### common-lisp

```{literalinclude} /_static/dsPost.flux
:language: common-lisp
```

#### componentpascal

```{literalinclude} /_static/dsPost.flux
:language: componentpascal
```

#### coq

```{literalinclude} /_static/dsPost.flux
:language: coq
```

#### cplint

```{literalinclude} /_static/dsPost.flux
:language: cplint
```

#### cpp

```{literalinclude} /_static/dsPost.flux
:language: cpp
```

#### cpp-objdump

```{literalinclude} /_static/dsPost.flux
:language: cpp-objdump
```

#### crmsh

```{literalinclude} /_static/dsPost.flux
:language: crmsh
```

#### croc

```{literalinclude} /_static/dsPost.flux
:language: croc
```

#### cryptol

```{literalinclude} /_static/dsPost.flux
:language: cryptol
```

#### cr

```{literalinclude} /_static/dsPost.flux
:language: cr
```

#### csound-document

```{literalinclude} /_static/dsPost.flux
:language: csound-document
```

#### csound

```{literalinclude} /_static/dsPost.flux
:language: csound
```

#### csound-score

```{literalinclude} /_static/dsPost.flux
:language: csound-score
```

#### css+django

```{literalinclude} /_static/dsPost.flux
:language: css+django
```

#### css+ruby

```{literalinclude} /_static/dsPost.flux
:language: css+ruby
```

#### css+genshitext

```{literalinclude} /_static/dsPost.flux
:language: css+genshitext
```

#### css

```{literalinclude} /_static/dsPost.flux
:language: css
```

#### css+php

```{literalinclude} /_static/dsPost.flux
:language: css+php
```

#### css+smarty

```{literalinclude} /_static/dsPost.flux
:language: css+smarty
```

#### cuda

```{literalinclude} /_static/dsPost.flux
:language: cuda
```

#### cypher

```{literalinclude} /_static/dsPost.flux
:language: cypher
```

#### cython

```{literalinclude} /_static/dsPost.flux
:language: cython
```

#### d

```{literalinclude} /_static/dsPost.flux
:language: d
```

#### d-objdump

```{literalinclude} /_static/dsPost.flux
:language: d-objdump
```

#### dpatch

```{literalinclude} /_static/dsPost.flux
:language: dpatch
```

#### dart

```{literalinclude} /_static/dsPost.flux
:language: dart
```

#### dasm16

```{literalinclude} /_static/dsPost.flux
:language: dasm16
```

#### dax

```{literalinclude} /_static/dsPost.flux
:language: dax
```

#### debcontrol

```{literalinclude} /_static/dsPost.flux
:language: debcontrol
```

#### debian.sources

```{literalinclude} /_static/dsPost.flux
:language: debian.sources
```

#### delphi

```{literalinclude} /_static/dsPost.flux
:language: delphi
```

#### desktop

```{literalinclude} /_static/dsPost.flux
:language: desktop
```

#### devicetree

```{literalinclude} /_static/dsPost.flux
:language: devicetree
```

#### dg

```{literalinclude} /_static/dsPost.flux
:language: dg
```

#### diff

```{literalinclude} /_static/dsPost.flux
:language: diff
```

#### django

```{literalinclude} /_static/dsPost.flux
:language: django
```

#### zone

```{literalinclude} /_static/dsPost.flux
:language: zone
```

#### docker

```{literalinclude} /_static/dsPost.flux
:language: docker
```

#### dtd

```{literalinclude} /_static/dsPost.flux
:language: dtd
```

#### duel

```{literalinclude} /_static/dsPost.flux
:language: duel
```

#### dylan-console

```{literalinclude} /_static/dsPost.flux
:language: dylan-console
```

#### dylan

```{literalinclude} /_static/dsPost.flux
:language: dylan
```

#### dylan-lid

```{literalinclude} /_static/dsPost.flux
:language: dylan-lid
```

#### ecl

```{literalinclude} /_static/dsPost.flux
:language: ecl
```

#### ec

```{literalinclude} /_static/dsPost.flux
:language: ec
```

#### earl-grey

```{literalinclude} /_static/dsPost.flux
:language: earl-grey
```

#### easytrieve

```{literalinclude} /_static/dsPost.flux
:language: easytrieve
```

#### ebnf

```{literalinclude} /_static/dsPost.flux
:language: ebnf
```

#### eiffel

```{literalinclude} /_static/dsPost.flux
:language: eiffel
```

#### iex

```{literalinclude} /_static/dsPost.flux
:language: iex
```

#### elixir

```{literalinclude} /_static/dsPost.flux
:language: elixir
```

#### elm

```{literalinclude} /_static/dsPost.flux
:language: elm
```

#### elpi

```{literalinclude} /_static/dsPost.flux
:language: elpi
```

#### emacs-lisp

```{literalinclude} /_static/dsPost.flux
:language: emacs-lisp
```

#### email

```{literalinclude} /_static/dsPost.flux
:language: email
```

#### erb

```{literalinclude} /_static/dsPost.flux
:language: erb
```

#### erlang

```{literalinclude} /_static/dsPost.flux
:language: erlang
```

#### erl

```{literalinclude} /_static/dsPost.flux
:language: erl
```

#### html+evoque

```{literalinclude} /_static/dsPost.flux
:language: html+evoque
```

#### evoque

```{literalinclude} /_static/dsPost.flux
:language: evoque
```

#### xml+evoque

```{literalinclude} /_static/dsPost.flux
:language: xml+evoque
```

#### execline

```{literalinclude} /_static/dsPost.flux
:language: execline
```

#### ezhil

```{literalinclude} /_static/dsPost.flux
:language: ezhil
```

#### fsharp

```{literalinclude} /_static/dsPost.flux
:language: fsharp
```

#### fstar

```{literalinclude} /_static/dsPost.flux
:language: fstar
```

#### factor

```{literalinclude} /_static/dsPost.flux
:language: factor
```

#### fancy

```{literalinclude} /_static/dsPost.flux
:language: fancy
```

#### fan

```{literalinclude} /_static/dsPost.flux
:language: fan
```

#### felix

```{literalinclude} /_static/dsPost.flux
:language: felix
```

#### fennel

```{literalinclude} /_static/dsPost.flux
:language: fennel
```

#### fift

```{literalinclude} /_static/dsPost.flux
:language: fift
```

#### fish

```{literalinclude} /_static/dsPost.flux
:language: fish
```

#### flatline

```{literalinclude} /_static/dsPost.flux
:language: flatline
```

#### floscript

```{literalinclude} /_static/dsPost.flux
:language: floscript
```

#### forth

```{literalinclude} /_static/dsPost.flux
:language: forth
```

#### fortranfixed

```{literalinclude} /_static/dsPost.flux
:language: fortranfixed
```

#### fortran

```{literalinclude} /_static/dsPost.flux
:language: fortran
```

#### foxpro

```{literalinclude} /_static/dsPost.flux
:language: foxpro
```

#### freefem

```{literalinclude} /_static/dsPost.flux
:language: freefem
```

#### func

```{literalinclude} /_static/dsPost.flux
:language: func
```

#### futhark

```{literalinclude} /_static/dsPost.flux
:language: futhark
```

#### gap-console

```{literalinclude} /_static/dsPost.flux
:language: gap-console
```

#### gap

```{literalinclude} /_static/dsPost.flux
:language: gap
```

#### gdscript

```{literalinclude} /_static/dsPost.flux
:language: gdscript
```

#### glsl

```{literalinclude} /_static/dsPost.flux
:language: glsl
```

#### gsql

```{literalinclude} /_static/dsPost.flux
:language: gsql
```

#### gas

```{literalinclude} /_static/dsPost.flux
:language: gas
```

#### gcode

```{literalinclude} /_static/dsPost.flux
:language: gcode
```

#### genshi

```{literalinclude} /_static/dsPost.flux
:language: genshi
```

#### genshitext

```{literalinclude} /_static/dsPost.flux
:language: genshitext
```

#### pot

```{literalinclude} /_static/dsPost.flux
:language: pot
```

#### gherkin

```{literalinclude} /_static/dsPost.flux
:language: gherkin
```

#### gleam

```{literalinclude} /_static/dsPost.flux
:language: gleam
```

#### gnuplot

```{literalinclude} /_static/dsPost.flux
:language: gnuplot
```

#### go

```{literalinclude} /_static/dsPost.flux
:language: go
```

#### golo

```{literalinclude} /_static/dsPost.flux
:language: golo
```

#### gooddata-cl

```{literalinclude} /_static/dsPost.flux
:language: gooddata-cl
```

#### googlesql

```{literalinclude} /_static/dsPost.flux
:language: googlesql
```

#### gosu

```{literalinclude} /_static/dsPost.flux
:language: gosu
```

#### gst

```{literalinclude} /_static/dsPost.flux
:language: gst
```

#### graphql

```{literalinclude} /_static/dsPost.flux
:language: graphql
```

#### graphviz

```{literalinclude} /_static/dsPost.flux
:language: graphviz
```

#### groff

```{literalinclude} /_static/dsPost.flux
:language: groff
```

#### groovy

```{literalinclude} /_static/dsPost.flux
:language: groovy
```

#### hlsl

```{literalinclude} /_static/dsPost.flux
:language: hlsl
```

#### html+ul4

```{literalinclude} /_static/dsPost.flux
:language: html+ul4
```

#### haml

```{literalinclude} /_static/dsPost.flux
:language: haml
```

#### html+handlebars

```{literalinclude} /_static/dsPost.flux
:language: html+handlebars
```

#### handlebars

```{literalinclude} /_static/dsPost.flux
:language: handlebars
```

#### hare

```{literalinclude} /_static/dsPost.flux
:language: hare
```

#### haskell

```{literalinclude} /_static/dsPost.flux
:language: haskell
```

#### haxe

```{literalinclude} /_static/dsPost.flux
:language: haxe
```

#### hexdump

```{literalinclude} /_static/dsPost.flux
:language: hexdump
```

#### hsail

```{literalinclude} /_static/dsPost.flux
:language: hsail
```

#### hspec

```{literalinclude} /_static/dsPost.flux
:language: hspec
```

#### html+django

```{literalinclude} /_static/dsPost.flux
:language: html+django
```

#### html+genshi

```{literalinclude} /_static/dsPost.flux
:language: html+genshi
```

#### html

```{literalinclude} /_static/dsPost.flux
:language: html
```

#### html+php

```{literalinclude} /_static/dsPost.flux
:language: html+php
```

#### html+smarty

```{literalinclude} /_static/dsPost.flux
:language: html+smarty
```

#### http

```{literalinclude} /_static/dsPost.flux
:language: http
```

#### haxeml

```{literalinclude} /_static/dsPost.flux
:language: haxeml
```

#### hylang

```{literalinclude} /_static/dsPost.flux
:language: hylang
```

#### hybris

```{literalinclude} /_static/dsPost.flux
:language: hybris
```

#### idl

```{literalinclude} /_static/dsPost.flux
:language: idl
```

#### icon

```{literalinclude} /_static/dsPost.flux
:language: icon
```

#### idris

```{literalinclude} /_static/dsPost.flux
:language: idris
```

#### igor

```{literalinclude} /_static/dsPost.flux
:language: igor
```

#### inform6

```{literalinclude} /_static/dsPost.flux
:language: inform6
```

#### i6t

```{literalinclude} /_static/dsPost.flux
:language: i6t
```

#### inform7

```{literalinclude} /_static/dsPost.flux
:language: inform7
```

#### ini

```{literalinclude} /_static/dsPost.flux
:language: ini
```

#### io

```{literalinclude} /_static/dsPost.flux
:language: io
```

#### ioke

```{literalinclude} /_static/dsPost.flux
:language: ioke
```

#### irc

```{literalinclude} /_static/dsPost.flux
:language: irc
```

#### isabelle

```{literalinclude} /_static/dsPost.flux
:language: isabelle
```

#### j

```{literalinclude} /_static/dsPost.flux
:language: j
```

#### jmespath

```{literalinclude} /_static/dsPost.flux
:language: jmespath
```

#### jslt

```{literalinclude} /_static/dsPost.flux
:language: jslt
```

#### jags

```{literalinclude} /_static/dsPost.flux
:language: jags
```

#### janet

```{literalinclude} /_static/dsPost.flux
:language: janet
```

#### jasmin

```{literalinclude} /_static/dsPost.flux
:language: jasmin
```

#### java

```{literalinclude} /_static/dsPost.flux
:language: java
```

#### javascript+django

```{literalinclude} /_static/dsPost.flux
:language: javascript+django
```

#### javascript+ruby

```{literalinclude} /_static/dsPost.flux
:language: javascript+ruby
```

#### js+genshitext

```{literalinclude} /_static/dsPost.flux
:language: js+genshitext
```

#### javascript

```{literalinclude} /_static/dsPost.flux
:language: javascript
```

#### javascript+php

```{literalinclude} /_static/dsPost.flux
:language: javascript+php
```

#### javascript+smarty

```{literalinclude} /_static/dsPost.flux
:language: javascript+smarty
```

#### js+ul4

```{literalinclude} /_static/dsPost.flux
:language: js+ul4
```

#### jcl

```{literalinclude} /_static/dsPost.flux
:language: jcl
```

#### jsgf

```{literalinclude} /_static/dsPost.flux
:language: jsgf
```

#### json5

```{literalinclude} /_static/dsPost.flux
:language: json5
```

#### jsonld

```{literalinclude} /_static/dsPost.flux
:language: jsonld
```

#### json

```{literalinclude} /_static/dsPost.flux
:language: json
```

#### jsonnet

```{literalinclude} /_static/dsPost.flux
:language: jsonnet
```

#### jsp

```{literalinclude} /_static/dsPost.flux
:language: jsp
```

#### jsx

```{literalinclude} /_static/dsPost.flux
:language: jsx
```

#### jlcon

```{literalinclude} /_static/dsPost.flux
:language: jlcon
```

#### julia

```{literalinclude} /_static/dsPost.flux
:language: julia
```

#### juttle

```{literalinclude} /_static/dsPost.flux
:language: juttle
```

#### k

```{literalinclude} /_static/dsPost.flux
:language: k
```

#### kal

```{literalinclude} /_static/dsPost.flux
:language: kal
```

#### kconfig

```{literalinclude} /_static/dsPost.flux
:language: kconfig
```

#### kmsg

```{literalinclude} /_static/dsPost.flux
:language: kmsg
```

#### koka

```{literalinclude} /_static/dsPost.flux
:language: koka
```

#### kotlin

```{literalinclude} /_static/dsPost.flux
:language: kotlin
```

#### kuin

```{literalinclude} /_static/dsPost.flux
:language: kuin
```

#### kql

```{literalinclude} /_static/dsPost.flux
:language: kql
```

#### lsl

```{literalinclude} /_static/dsPost.flux
:language: lsl
```

#### css+lasso

```{literalinclude} /_static/dsPost.flux
:language: css+lasso
```

#### html+lasso

```{literalinclude} /_static/dsPost.flux
:language: html+lasso
```

#### javascript+lasso

```{literalinclude} /_static/dsPost.flux
:language: javascript+lasso
```

#### lasso

```{literalinclude} /_static/dsPost.flux
:language: lasso
```

#### xml+lasso

```{literalinclude} /_static/dsPost.flux
:language: xml+lasso
```

#### ldapconf

```{literalinclude} /_static/dsPost.flux
:language: ldapconf
```

#### ldif

```{literalinclude} /_static/dsPost.flux
:language: ldif
```

#### lean

```{literalinclude} /_static/dsPost.flux
:language: lean
```

#### lean4

```{literalinclude} /_static/dsPost.flux
:language: lean4
```

#### less

```{literalinclude} /_static/dsPost.flux
:language: less
```

#### lighttpd

```{literalinclude} /_static/dsPost.flux
:language: lighttpd
```

#### lilypond

```{literalinclude} /_static/dsPost.flux
:language: lilypond
```

#### limbo

```{literalinclude} /_static/dsPost.flux
:language: limbo
```

#### liquid

```{literalinclude} /_static/dsPost.flux
:language: liquid
```

#### literate-agda

```{literalinclude} /_static/dsPost.flux
:language: literate-agda
```

#### literate-cryptol

```{literalinclude} /_static/dsPost.flux
:language: literate-cryptol
```

#### literate-haskell

```{literalinclude} /_static/dsPost.flux
:language: literate-haskell
```

#### literate-idris

```{literalinclude} /_static/dsPost.flux
:language: literate-idris
```

#### livescript

```{literalinclude} /_static/dsPost.flux
:language: livescript
```

#### llvm

```{literalinclude} /_static/dsPost.flux
:language: llvm
```

#### llvm-mir-body

```{literalinclude} /_static/dsPost.flux
:language: llvm-mir-body
```

#### llvm-mir

```{literalinclude} /_static/dsPost.flux
:language: llvm-mir
```

#### logos

```{literalinclude} /_static/dsPost.flux
:language: logos
```

#### logtalk

```{literalinclude} /_static/dsPost.flux
:language: logtalk
```

#### lua

```{literalinclude} /_static/dsPost.flux
:language: lua
```

#### luau

```{literalinclude} /_static/dsPost.flux
:language: luau
```

#### mcfunction

```{literalinclude} /_static/dsPost.flux
:language: mcfunction
```

#### mcschema

```{literalinclude} /_static/dsPost.flux
:language: mcschema
```

#### mime

```{literalinclude} /_static/dsPost.flux
:language: mime
```

#### mips

```{literalinclude} /_static/dsPost.flux
:language: mips
```

#### moocode

```{literalinclude} /_static/dsPost.flux
:language: moocode
```

#### doscon

```{literalinclude} /_static/dsPost.flux
:language: doscon
```

#### macaulay2

```{literalinclude} /_static/dsPost.flux
:language: macaulay2
```

#### make

```{literalinclude} /_static/dsPost.flux
:language: make
```

#### css+mako

```{literalinclude} /_static/dsPost.flux
:language: css+mako
```

#### html+mako

```{literalinclude} /_static/dsPost.flux
:language: html+mako
```

#### javascript+mako

```{literalinclude} /_static/dsPost.flux
:language: javascript+mako
```

#### mako

```{literalinclude} /_static/dsPost.flux
:language: mako
```

#### xml+mako

```{literalinclude} /_static/dsPost.flux
:language: xml+mako
```

#### maple

```{literalinclude} /_static/dsPost.flux
:language: maple
```

#### maql

```{literalinclude} /_static/dsPost.flux
:language: maql
```

#### markdown

```{literalinclude} /_static/dsPost.flux
:language: markdown
```

#### mask

```{literalinclude} /_static/dsPost.flux
:language: mask
```

#### mason

```{literalinclude} /_static/dsPost.flux
:language: mason
```

#### mathematica

```{literalinclude} /_static/dsPost.flux
:language: mathematica
```

#### matlab

```{literalinclude} /_static/dsPost.flux
:language: matlab
```

#### matlabsession

```{literalinclude} /_static/dsPost.flux
:language: matlabsession
```

#### maxima

```{literalinclude} /_static/dsPost.flux
:language: maxima
```

#### meson

```{literalinclude} /_static/dsPost.flux
:language: meson
```

#### minid

```{literalinclude} /_static/dsPost.flux
:language: minid
```

#### miniscript

```{literalinclude} /_static/dsPost.flux
:language: miniscript
```

#### modelica

```{literalinclude} /_static/dsPost.flux
:language: modelica
```

#### modula2

```{literalinclude} /_static/dsPost.flux
:language: modula2
```

#### trac-wiki

```{literalinclude} /_static/dsPost.flux
:language: trac-wiki
```

#### mojo

```{literalinclude} /_static/dsPost.flux
:language: mojo
```

#### monkey

```{literalinclude} /_static/dsPost.flux
:language: monkey
```

#### monte

```{literalinclude} /_static/dsPost.flux
:language: monte
```

#### moonscript

```{literalinclude} /_static/dsPost.flux
:language: moonscript
```

#### mosel

```{literalinclude} /_static/dsPost.flux
:language: mosel
```

#### css+mozpreproc

```{literalinclude} /_static/dsPost.flux
:language: css+mozpreproc
```

#### mozhashpreproc

```{literalinclude} /_static/dsPost.flux
:language: mozhashpreproc
```

#### javascript+mozpreproc

```{literalinclude} /_static/dsPost.flux
:language: javascript+mozpreproc
```

#### mozpercentpreproc

```{literalinclude} /_static/dsPost.flux
:language: mozpercentpreproc
```

#### xul+mozpreproc

```{literalinclude} /_static/dsPost.flux
:language: xul+mozpreproc
```

#### mql

```{literalinclude} /_static/dsPost.flux
:language: mql
```

#### mscgen

```{literalinclude} /_static/dsPost.flux
:language: mscgen
```

#### mupad

```{literalinclude} /_static/dsPost.flux
:language: mupad
```

#### mxml

```{literalinclude} /_static/dsPost.flux
:language: mxml
```

#### mysql

```{literalinclude} /_static/dsPost.flux
:language: mysql
```

#### css+myghty

```{literalinclude} /_static/dsPost.flux
:language: css+myghty
```

#### html+myghty

```{literalinclude} /_static/dsPost.flux
:language: html+myghty
```

#### javascript+myghty

```{literalinclude} /_static/dsPost.flux
:language: javascript+myghty
```

#### myghty

```{literalinclude} /_static/dsPost.flux
:language: myghty
```

#### xml+myghty

```{literalinclude} /_static/dsPost.flux
:language: xml+myghty
```

#### ncl

```{literalinclude} /_static/dsPost.flux
:language: ncl
```

#### nsis

```{literalinclude} /_static/dsPost.flux
:language: nsis
```

#### nasm

```{literalinclude} /_static/dsPost.flux
:language: nasm
```

#### objdump-nasm

```{literalinclude} /_static/dsPost.flux
:language: objdump-nasm
```

#### nemerle

```{literalinclude} /_static/dsPost.flux
:language: nemerle
```

#### nesc

```{literalinclude} /_static/dsPost.flux
:language: nesc
```

#### nestedtext

```{literalinclude} /_static/dsPost.flux
:language: nestedtext
```

#### newlisp

```{literalinclude} /_static/dsPost.flux
:language: newlisp
```

#### newspeak

```{literalinclude} /_static/dsPost.flux
:language: newspeak
```

#### nginx

```{literalinclude} /_static/dsPost.flux
:language: nginx
```

#### nimrod

```{literalinclude} /_static/dsPost.flux
:language: nimrod
```

#### nit

```{literalinclude} /_static/dsPost.flux
:language: nit
```

#### nixos

```{literalinclude} /_static/dsPost.flux
:language: nixos
```

#### nodejsrepl

```{literalinclude} /_static/dsPost.flux
:language: nodejsrepl
```

#### notmuch

```{literalinclude} /_static/dsPost.flux
:language: notmuch
```

#### nusmv

```{literalinclude} /_static/dsPost.flux
:language: nusmv
```

#### numpy

```{literalinclude} /_static/dsPost.flux
:language: numpy
```

#### numba_ir

```{literalinclude} /_static/dsPost.flux
:language: numba_ir
```

#### objdump

```{literalinclude} /_static/dsPost.flux
:language: objdump
```

#### objective-c

```{literalinclude} /_static/dsPost.flux
:language: objective-c
```

#### objective-c++

```{literalinclude} /_static/dsPost.flux
:language: objective-c++
```

#### objective-j

```{literalinclude} /_static/dsPost.flux
:language: objective-j
```

#### ocaml

```{literalinclude} /_static/dsPost.flux
:language: ocaml
```

#### octave

```{literalinclude} /_static/dsPost.flux
:language: octave
```

#### odin

```{literalinclude} /_static/dsPost.flux
:language: odin
```

#### omg-idl

```{literalinclude} /_static/dsPost.flux
:language: omg-idl
```

#### ooc

```{literalinclude} /_static/dsPost.flux
:language: ooc
```

#### opa

```{literalinclude} /_static/dsPost.flux
:language: opa
```

#### openedge

```{literalinclude} /_static/dsPost.flux
:language: openedge
```

#### openscad

```{literalinclude} /_static/dsPost.flux
:language: openscad
```

#### org

```{literalinclude} /_static/dsPost.flux
:language: org
```

#### output

```{literalinclude} /_static/dsPost.flux
:language: output
```

#### pacmanconf

```{literalinclude} /_static/dsPost.flux
:language: pacmanconf
```

#### pan

```{literalinclude} /_static/dsPost.flux
:language: pan
```

#### parasail

```{literalinclude} /_static/dsPost.flux
:language: parasail
```

#### pawn

```{literalinclude} /_static/dsPost.flux
:language: pawn
```

#### pddl

```{literalinclude} /_static/dsPost.flux
:language: pddl
```

#### peg

```{literalinclude} /_static/dsPost.flux
:language: peg
```

#### perl6

```{literalinclude} /_static/dsPost.flux
:language: perl6
```

#### perl

```{literalinclude} /_static/dsPost.flux
:language: perl
```

#### phix

```{literalinclude} /_static/dsPost.flux
:language: phix
```

#### php

```{literalinclude} /_static/dsPost.flux
:language: php
```

#### pig

```{literalinclude} /_static/dsPost.flux
:language: pig
```

#### pike

```{literalinclude} /_static/dsPost.flux
:language: pike
```

#### pkgconfig

```{literalinclude} /_static/dsPost.flux
:language: pkgconfig
```

#### plpgsql

```{literalinclude} /_static/dsPost.flux
:language: plpgsql
```

#### pointless

```{literalinclude} /_static/dsPost.flux
:language: pointless
```

#### pony

```{literalinclude} /_static/dsPost.flux
:language: pony
```

#### portugol

```{literalinclude} /_static/dsPost.flux
:language: portugol
```

#### postscript

```{literalinclude} /_static/dsPost.flux
:language: postscript
```

#### psql

```{literalinclude} /_static/dsPost.flux
:language: psql
```

#### postgres-explain

```{literalinclude} /_static/dsPost.flux
:language: postgres-explain
```

#### postgresql

```{literalinclude} /_static/dsPost.flux
:language: postgresql
```

#### pov

```{literalinclude} /_static/dsPost.flux
:language: pov
```

#### powershell

```{literalinclude} /_static/dsPost.flux
:language: powershell
```

#### pwsh-session

```{literalinclude} /_static/dsPost.flux
:language: pwsh-session
```

#### praat

```{literalinclude} /_static/dsPost.flux
:language: praat
```

#### procfile

```{literalinclude} /_static/dsPost.flux
:language: procfile
```

#### prolog

```{literalinclude} /_static/dsPost.flux
:language: prolog
```

#### promql

```{literalinclude} /_static/dsPost.flux
:language: promql
```

#### promela

```{literalinclude} /_static/dsPost.flux
:language: promela
```

#### properties

```{literalinclude} /_static/dsPost.flux
:language: properties
```

#### protobuf

```{literalinclude} /_static/dsPost.flux
:language: protobuf
```

#### prql

```{literalinclude} /_static/dsPost.flux
:language: prql
```

#### psysh

```{literalinclude} /_static/dsPost.flux
:language: psysh
```

#### ptx

```{literalinclude} /_static/dsPost.flux
:language: ptx
```

#### pug

```{literalinclude} /_static/dsPost.flux
:language: pug
```

#### puppet

```{literalinclude} /_static/dsPost.flux
:language: puppet
```

#### pypylog

```{literalinclude} /_static/dsPost.flux
:language: pypylog
```

#### python2

```{literalinclude} /_static/dsPost.flux
:language: python2
```

#### py2tb

```{literalinclude} /_static/dsPost.flux
:language: py2tb
```

#### pycon

```{literalinclude} /_static/dsPost.flux
:language: pycon
```

#### python

```{literalinclude} /_static/dsPost.flux
:language: python
```

#### pytb

```{literalinclude} /_static/dsPost.flux
:language: pytb
```

#### py+ul4

```{literalinclude} /_static/dsPost.flux
:language: py+ul4
```

#### qbasic

```{literalinclude} /_static/dsPost.flux
:language: qbasic
```

#### q

```{literalinclude} /_static/dsPost.flux
:language: q
```

#### qvto

```{literalinclude} /_static/dsPost.flux
:language: qvto
```

#### qlik

```{literalinclude} /_static/dsPost.flux
:language: qlik
```

#### qml

```{literalinclude} /_static/dsPost.flux
:language: qml
```

#### rconsole

```{literalinclude} /_static/dsPost.flux
:language: rconsole
```

#### rng-compact

```{literalinclude} /_static/dsPost.flux
:language: rng-compact
```

#### spec

```{literalinclude} /_static/dsPost.flux
:language: spec
```

#### racket

```{literalinclude} /_static/dsPost.flux
:language: racket
```

#### ragel-c

```{literalinclude} /_static/dsPost.flux
:language: ragel-c
```

#### ragel-cpp

```{literalinclude} /_static/dsPost.flux
:language: ragel-cpp
```

#### ragel-d

```{literalinclude} /_static/dsPost.flux
:language: ragel-d
```

#### ragel-em

```{literalinclude} /_static/dsPost.flux
:language: ragel-em
```

#### ragel-java

```{literalinclude} /_static/dsPost.flux
:language: ragel-java
```

#### ragel

```{literalinclude} /_static/dsPost.flux
:language: ragel
```

#### ragel-objc

```{literalinclude} /_static/dsPost.flux
:language: ragel-objc
```

#### ragel-ruby

```{literalinclude} /_static/dsPost.flux
:language: ragel-ruby
```

#### rd

```{literalinclude} /_static/dsPost.flux
:language: rd
```

#### reasonml

```{literalinclude} /_static/dsPost.flux
:language: reasonml
```

#### rebol

```{literalinclude} /_static/dsPost.flux
:language: rebol
```

#### red

```{literalinclude} /_static/dsPost.flux
:language: red
```

#### redcode

```{literalinclude} /_static/dsPost.flux
:language: redcode
```

#### registry

```{literalinclude} /_static/dsPost.flux
:language: registry
```

#### rego

```{literalinclude} /_static/dsPost.flux
:language: rego
```

#### resourcebundle

```{literalinclude} /_static/dsPost.flux
:language: resourcebundle
```

#### rexx

```{literalinclude} /_static/dsPost.flux
:language: rexx
```

#### rhtml

```{literalinclude} /_static/dsPost.flux
:language: rhtml
```

#### ride

```{literalinclude} /_static/dsPost.flux
:language: ride
```

#### rita

```{literalinclude} /_static/dsPost.flux
:language: rita
```

#### roboconf-graph

```{literalinclude} /_static/dsPost.flux
:language: roboconf-graph
```

#### roboconf-instances

```{literalinclude} /_static/dsPost.flux
:language: roboconf-instances
```

#### robotframework

```{literalinclude} /_static/dsPost.flux
:language: robotframework
```

#### rql

```{literalinclude} /_static/dsPost.flux
:language: rql
```

#### rsl

```{literalinclude} /_static/dsPost.flux
:language: rsl
```

#### restructuredtext

```{literalinclude} /_static/dsPost.flux
:language: restructuredtext
```

#### trafficscript

```{literalinclude} /_static/dsPost.flux
:language: trafficscript
```

#### rbcon

```{literalinclude} /_static/dsPost.flux
:language: rbcon
```

#### ruby

```{literalinclude} /_static/dsPost.flux
:language: ruby
```

#### rust

```{literalinclude} /_static/dsPost.flux
:language: rust
```

#### sas

```{literalinclude} /_static/dsPost.flux
:language: sas
```

#### splus

```{literalinclude} /_static/dsPost.flux
:language: splus
```

#### sml

```{literalinclude} /_static/dsPost.flux
:language: sml
```

#### snbt

```{literalinclude} /_static/dsPost.flux
:language: snbt
```

#### sarl

```{literalinclude} /_static/dsPost.flux
:language: sarl
```

#### sass

```{literalinclude} /_static/dsPost.flux
:language: sass
```

#### savi

```{literalinclude} /_static/dsPost.flux
:language: savi
```

#### scala

```{literalinclude} /_static/dsPost.flux
:language: scala
```

#### scaml

```{literalinclude} /_static/dsPost.flux
:language: scaml
```

#### scdoc

```{literalinclude} /_static/dsPost.flux
:language: scdoc
```

#### scheme

```{literalinclude} /_static/dsPost.flux
:language: scheme
```

#### scilab

```{literalinclude} /_static/dsPost.flux
:language: scilab
```

#### scss

```{literalinclude} /_static/dsPost.flux
:language: scss
```

#### sed

```{literalinclude} /_static/dsPost.flux
:language: sed
```

#### shexc

```{literalinclude} /_static/dsPost.flux
:language: shexc
```

#### shen

```{literalinclude} /_static/dsPost.flux
:language: shen
```

#### sieve

```{literalinclude} /_static/dsPost.flux
:language: sieve
```

#### silver

```{literalinclude} /_static/dsPost.flux
:language: silver
```

#### singularity

```{literalinclude} /_static/dsPost.flux
:language: singularity
```

#### slash

```{literalinclude} /_static/dsPost.flux
:language: slash
```

#### slim

```{literalinclude} /_static/dsPost.flux
:language: slim
```

#### slurm

```{literalinclude} /_static/dsPost.flux
:language: slurm
```

#### smali

```{literalinclude} /_static/dsPost.flux
:language: smali
```

#### smalltalk

```{literalinclude} /_static/dsPost.flux
:language: smalltalk
```

#### sgf

```{literalinclude} /_static/dsPost.flux
:language: sgf
```

#### smarty

```{literalinclude} /_static/dsPost.flux
:language: smarty
```

#### smithy

```{literalinclude} /_static/dsPost.flux
:language: smithy
```

#### snobol

```{literalinclude} /_static/dsPost.flux
:language: snobol
```

#### snowball

```{literalinclude} /_static/dsPost.flux
:language: snowball
```

#### solidity

```{literalinclude} /_static/dsPost.flux
:language: solidity
```

#### androidbp

```{literalinclude} /_static/dsPost.flux
:language: androidbp
```

#### sophia

```{literalinclude} /_static/dsPost.flux
:language: sophia
```

#### sp

```{literalinclude} /_static/dsPost.flux
:language: sp
```

#### debsources

```{literalinclude} /_static/dsPost.flux
:language: debsources
```

#### sparql

```{literalinclude} /_static/dsPost.flux
:language: sparql
```

#### spice

```{literalinclude} /_static/dsPost.flux
:language: spice
```

#### sql+jinja

```{literalinclude} /_static/dsPost.flux
:language: sql+jinja
```

#### sql

```{literalinclude} /_static/dsPost.flux
:language: sql
```

#### sqlite3

```{literalinclude} /_static/dsPost.flux
:language: sqlite3
```

#### squidconf

```{literalinclude} /_static/dsPost.flux
:language: squidconf
```

#### srcinfo

```{literalinclude} /_static/dsPost.flux
:language: srcinfo
```

#### ssp

```{literalinclude} /_static/dsPost.flux
:language: ssp
```

#### stan

```{literalinclude} /_static/dsPost.flux
:language: stan
```

#### stata

```{literalinclude} /_static/dsPost.flux
:language: stata
```

#### supercollider

```{literalinclude} /_static/dsPost.flux
:language: supercollider
```

#### swift

```{literalinclude} /_static/dsPost.flux
:language: swift
```

#### swig

```{literalinclude} /_static/dsPost.flux
:language: swig
```

#### systemverilog

```{literalinclude} /_static/dsPost.flux
:language: systemverilog
```

#### systemd

```{literalinclude} /_static/dsPost.flux
:language: systemd
```

#### tap

```{literalinclude} /_static/dsPost.flux
:language: tap
```

#### tnt

```{literalinclude} /_static/dsPost.flux
:language: tnt
```

#### toml

```{literalinclude} /_static/dsPost.flux
:language: toml
```

#### tablegen

```{literalinclude} /_static/dsPost.flux
:language: tablegen
```

#### tact

```{literalinclude} /_static/dsPost.flux
:language: tact
```

#### tads3

```{literalinclude} /_static/dsPost.flux
:language: tads3
```

#### tal

```{literalinclude} /_static/dsPost.flux
:language: tal
```

#### tasm

```{literalinclude} /_static/dsPost.flux
:language: tasm
```

#### tcl

```{literalinclude} /_static/dsPost.flux
:language: tcl
```

#### tcsh

```{literalinclude} /_static/dsPost.flux
:language: tcsh
```

#### tcshcon

```{literalinclude} /_static/dsPost.flux
:language: tcshcon
```

#### tea

```{literalinclude} /_static/dsPost.flux
:language: tea
```

#### teal

```{literalinclude} /_static/dsPost.flux
:language: teal
```

#### teratermmacro

```{literalinclude} /_static/dsPost.flux
:language: teratermmacro
```

#### termcap

```{literalinclude} /_static/dsPost.flux
:language: termcap
```

#### terminfo

```{literalinclude} /_static/dsPost.flux
:language: terminfo
```

#### terraform

```{literalinclude} /_static/dsPost.flux
:language: terraform
```

#### tex

```{literalinclude} /_static/dsPost.flux
:language: tex
```

#### text

```{literalinclude} /_static/dsPost.flux
:language: text
```

#### ti

```{literalinclude} /_static/dsPost.flux
:language: ti
```

#### thrift

```{literalinclude} /_static/dsPost.flux
:language: thrift
```

#### tid

```{literalinclude} /_static/dsPost.flux
:language: tid
```

#### tlb

```{literalinclude} /_static/dsPost.flux
:language: tlb
```

#### tls

```{literalinclude} /_static/dsPost.flux
:language: tls
```

#### todotxt

```{literalinclude} /_static/dsPost.flux
:language: todotxt
```

#### tsql

```{literalinclude} /_static/dsPost.flux
:language: tsql
```

#### treetop

```{literalinclude} /_static/dsPost.flux
:language: treetop
```

#### tsx

```{literalinclude} /_static/dsPost.flux
:language: tsx
```

#### turtle

```{literalinclude} /_static/dsPost.flux
:language: turtle
```

#### html+twig

```{literalinclude} /_static/dsPost.flux
:language: html+twig
```

#### twig

```{literalinclude} /_static/dsPost.flux
:language: twig
```

#### typescript

```{literalinclude} /_static/dsPost.flux
:language: typescript
```

#### typoscriptcssdata

```{literalinclude} /_static/dsPost.flux
:language: typoscriptcssdata
```

#### typoscripthtmldata

```{literalinclude} /_static/dsPost.flux
:language: typoscripthtmldata
```

#### typoscript

```{literalinclude} /_static/dsPost.flux
:language: typoscript
```

#### typst

```{literalinclude} /_static/dsPost.flux
:language: typst
```

#### ul4

```{literalinclude} /_static/dsPost.flux
:language: ul4
```

#### ucode

```{literalinclude} /_static/dsPost.flux
:language: ucode
```

#### unicon

```{literalinclude} /_static/dsPost.flux
:language: unicon
```

#### unixconfig

```{literalinclude} /_static/dsPost.flux
:language: unixconfig
```

#### urbiscript

```{literalinclude} /_static/dsPost.flux
:language: urbiscript
```

#### urlencoded

```{literalinclude} /_static/dsPost.flux
:language: urlencoded
```

#### usd

```{literalinclude} /_static/dsPost.flux
:language: usd
```

#### vbscript

```{literalinclude} /_static/dsPost.flux
:language: vbscript
```

#### vcl

```{literalinclude} /_static/dsPost.flux
:language: vcl
```

#### vclsnippets

```{literalinclude} /_static/dsPost.flux
:language: vclsnippets
```

#### vctreestatus

```{literalinclude} /_static/dsPost.flux
:language: vctreestatus
```

#### vgl

```{literalinclude} /_static/dsPost.flux
:language: vgl
```

#### vala

```{literalinclude} /_static/dsPost.flux
:language: vala
```

#### aspx-vb

```{literalinclude} /_static/dsPost.flux
:language: aspx-vb
```

#### vb.net

```{literalinclude} /_static/dsPost.flux
:language: vb.net
```

#### html+velocity

```{literalinclude} /_static/dsPost.flux
:language: html+velocity
```

#### velocity

```{literalinclude} /_static/dsPost.flux
:language: velocity
```

#### xml+velocity

```{literalinclude} /_static/dsPost.flux
:language: xml+velocity
```

#### verifpal

```{literalinclude} /_static/dsPost.flux
:language: verifpal
```

#### verilog

```{literalinclude} /_static/dsPost.flux
:language: verilog
```

#### vhdl

```{literalinclude} /_static/dsPost.flux
:language: vhdl
```

#### vim

```{literalinclude} /_static/dsPost.flux
:language: vim
```

#### visualprologgrammar

```{literalinclude} /_static/dsPost.flux
:language: visualprologgrammar
```

#### visualprolog

```{literalinclude} /_static/dsPost.flux
:language: visualprolog
```

#### vue

```{literalinclude} /_static/dsPost.flux
:language: vue
```

#### vyper

```{literalinclude} /_static/dsPost.flux
:language: vyper
```

#### wdiff

```{literalinclude} /_static/dsPost.flux
:language: wdiff
```

#### wast

```{literalinclude} /_static/dsPost.flux
:language: wast
```

#### webidl

```{literalinclude} /_static/dsPost.flux
:language: webidl
```

#### wgsl

```{literalinclude} /_static/dsPost.flux
:language: wgsl
```

#### whiley

```{literalinclude} /_static/dsPost.flux
:language: whiley
```

#### wikitext

```{literalinclude} /_static/dsPost.flux
:language: wikitext
```

#### wowtoc

```{literalinclude} /_static/dsPost.flux
:language: wowtoc
```

#### wren

```{literalinclude} /_static/dsPost.flux
:language: wren
```

#### x10

```{literalinclude} /_static/dsPost.flux
:language: x10
```

#### xml+ul4

```{literalinclude} /_static/dsPost.flux
:language: xml+ul4
```

#### xquery

```{literalinclude} /_static/dsPost.flux
:language: xquery
```

#### xml+django

```{literalinclude} /_static/dsPost.flux
:language: xml+django
```

#### xml+ruby

```{literalinclude} /_static/dsPost.flux
:language: xml+ruby
```

#### xml

```{literalinclude} /_static/dsPost.flux
:language: xml
```

#### xml+php

```{literalinclude} /_static/dsPost.flux
:language: xml+php
```

#### xml+smarty

```{literalinclude} /_static/dsPost.flux
:language: xml+smarty
```

#### xorg.conf

```{literalinclude} /_static/dsPost.flux
:language: xorg.conf
```

#### xpp

```{literalinclude} /_static/dsPost.flux
:language: xpp
```

#### xslt

```{literalinclude} /_static/dsPost.flux
:language: xslt
```

#### xtend

```{literalinclude} /_static/dsPost.flux
:language: xtend
```

#### extempore

```{literalinclude} /_static/dsPost.flux
:language: extempore
```

#### yaml+jinja

```{literalinclude} /_static/dsPost.flux
:language: yaml+jinja
```

#### yaml

```{literalinclude} /_static/dsPost.flux
:language: yaml
```

#### yang

```{literalinclude} /_static/dsPost.flux
:language: yang
```

#### yara

```{literalinclude} /_static/dsPost.flux
:language: yara
```

#### zeek

```{literalinclude} /_static/dsPost.flux
:language: zeek
```

#### zephir

```{literalinclude} /_static/dsPost.flux
:language: zephir
```

#### zig

```{literalinclude} /_static/dsPost.flux
:language: zig
```

#### ansys

```{literalinclude} /_static/dsPost.flux
:language: ansys
```
