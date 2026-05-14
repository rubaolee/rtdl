# Goal1981 Exact Radius-Graph Components DBSCAN Partner Reference

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

`dbscan_clustering` previously had a fast v2 row for the fixed-radius core
predicate. That is useful, but it is not full DBSCAN clustering: the richer
requirement is cluster expansion over connected core neighborhoods plus border
point assignment.

Goal1981 adds a generic partner continuation:

```text
radius_graph_components_2d_partner_columns(point_columns,
                                           radius=...,
                                           min_neighbors=...)
```

The helper computes radius-neighborhood counts, marks core points, propagates
connected-component labels across the core graph, and assigns border points to
adjacent core components. The DBSCAN example now exposes:

```text
--backend partner_exact_clusters --partner torch|cupy
```

## Boundary

This is not DBSCAN inside the native engine. The native engine receives no
DBSCAN ABI, cluster-expansion continuation, or app-shaped primitive. The
partner adapter is phrased as generic radius-graph component labeling over
point columns.

This goal does not authorize v2.0 release, broad whole-app acceleration,
arbitrary partner acceleration, or RT-core acceleration claims.

## Pod Timing

The RTX 2000 Ada pod ran the exact CuPy radius-graph component path:

| Copies | Points | Clusters | CPU Python exact median s | v2 CuPy exact median s | Ratio | Correct |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64 | 512 | 128 | 0.117993 | 0.070320 | 0.59596x | yes |
| 256 | 2048 | 512 | not run | 0.969669 | n/a | yes |
| 512 | 4096 | 1024 | not run | 3.807111 | n/a | yes |

This is semantically better than the old core-point threshold proxy, but it is
not yet the final high-performance DBSCAN design. The current implementation
uses dense radius-graph labeling, so the next optimization target is a generic
partner spatial-bucketing or sparse radius-edge contract.

Artifact:

- `docs/reports/goal1981_pod_exact_radius_graph_components_dbscan_cupy_perf.json`
