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
changes to queries.

TODO compare query statistics, best of 10 each.

TODO strings last() ints mean()

## Overview

TODO

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
