# Goal2201 RayJoin Same-Query Evidence Summary

Status: generated from pod artifacts; claim boundaries remain locked unless a later reviewed report changes them.

## Scope

This report summarizes RayJoin-generated PIP/LSI query streams and RTDL replay over the same streams.
It is not by itself a RayJoin paper reproduction or a v2.0 release authorization.

## RayJoin Query Phase

| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `grid` | 4.6893 | 2.72202 | n/a | 0 | 8921 | n/a |
| `lsi` | `lbvh` | 1.52763 | 4.31705 | n/a | 0 | 8921 | n/a |
| `lsi` | `rt` | 0.611623 | 0.721931 | 0.431061 | 4 | 8921 | n/a |
| `pip` | `grid` | 16.8404 | 1.86205 | n/a | 0 | n/a | n/a |
| `pip` | `lbvh` | 10.2307 | 21.0481 | n/a | 0 | n/a | pass |
| `pip` | `rt` | 0.575066 | 0.818968 | 0.550985 | 4 | n/a | pass |

## RTDL Same-Stream Replay

| Workload | Query count | Reference rows | CPU sec | Embree sec | OptiX sec | OptiX/CPU | OptiX/Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lsi` | 100000 | 8921 | 1.153435 | 106.047649 | 0.083064 | 0.072x | 0.001x |
| `pip` | 100000 | 8686 | 2.758106 | 0.106248 | 4.107544 | 1.489x | 38.660x |

## Boundary

The summary keeps these claims unauthorized:

- paper-scale RayJoin reproduction
- RTDL beats RayJoin
- broad RT-core speedup
- v2.0 release readiness

A stronger public performance claim needs the raw artifacts, external review, and a separate consensus report.
