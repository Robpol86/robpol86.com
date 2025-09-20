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

## Backend

```{literalinclude} /_static/dsTask.flux
:language: text
```

## Frontend

```{literalinclude} /_static/dsPost.flux
:language: text
```

TODO [dsGrafana.json](/_static/dsGrafana.json)
