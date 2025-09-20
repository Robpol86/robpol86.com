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
* - :::{imgur-image} q04bUPy
    :::
```

In this guide I will show you how I've implemented InfluxDB v2 downsampling that plays nicely with Grafana with minimal
changes to queries. I use it to downsample Telegraf metrics but it should work with any data. Ints and floats are downsampled
using `mean()` whilst all other types are downsampled with `last()`. Grafana will read metrics from your main and downsample
buckets and combine them with `union()`. The last part I've automated into a single Grafana variable to avoid copying and
pasting a lot of code for each of your queries.

The official [InfluxDB v2 documentation](https://docs.influxdata.com/influxdb/v2/process-data/common-tasks/downsample-data/)
implements downsampling in a strange way that doesn't seem usable for real time metrics such as with Telegraf. They also
don't cover consuming the downsampled data. Turns out that was the hard part.

## Overview

TODO strings last() ints mean()

TODO compare query statistics (or profiling), best of 10 each.

## Backend

TODO

### Flux Tasks

TODO reduce docstring and document here instead

```{literalinclude} /_static/dsTask.flux
:language: text
```

### Backfilling Data

TODO

## Frontend

TODO gif with production ranges showing zooming out and panning

### Grafana Query Variable

TODO eliminate "PASTE EVERYTHING BELOW THIS LINE IN GRAFANA"

```{literalinclude} /_static/dsPost.flux
:language: text
```

### Update Queries

TODO [dsGrafana.json](/_static/dsGrafana.json)
