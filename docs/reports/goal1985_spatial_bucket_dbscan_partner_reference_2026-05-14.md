# Goal1985 Spatial-Bucket DBSCAN Partner Reference

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

Goal1981 made `dbscan_clustering` semantically exact by computing radius-graph
component labels, but the first implementation used a dense point-by-point
radius matrix. That was correct, yet it did not scale like a useful DBSCAN path.

Goal1985 adds a second generic continuation:

```text
radius_graph_components_2d_spatial_bucket_partner_columns(...)
```

The helper builds a sparse spatial bucket graph, checks only neighboring cells,
and then labels connected core components. The example exposes it as:

```text
examples/rtdl_dbscan_clustering_app.py --backend partner_spatial_exact_clusters --partner cupy
```

Large timing rows use `--skip-validation` after a smaller validation row proves
oracle parity, because the Python brute-force oracle is O(n^2) and otherwise
pollutes the v2 timing.

## Boundary

This is not DBSCAN inside the native engine. It does not add a DBSCAN native ABI
or app-shaped engine continuation.

This is also not yet true zero-copy: the sparse bucket index is currently built
on the host from partner point columns and then returns partner-owned result
columns. That is a deliberate transitional implementation, not a release claim.

## Pod Timing

The RTX 2000 Ada pod ran the CuPy spatial-bucket exact path:

| Copies | Points | Candidate edges | Dense exact median s | Spatial exact median s | Spatial/Dense | Correctness |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64 | 512 | 576 | 0.008993 | 0.002598 | 0.28891x | validation row matches oracle |
| 256 | 2048 | 2304 | 0.032810 | 0.009209 | 0.28067x | shape recorded |
| 512 | 4096 | 4608 | 0.072968 | 0.018703 | 0.25631x | shape recorded |
| 1024 | 8192 | 9216 | not run | 0.037252 | n/a | shape recorded |
| 2048 | 16384 | 18432 | not run | 0.087784 | n/a | shape recorded |
| 4096 | 32768 | 36864 | not run | 0.168975 | n/a | shape recorded |

Artifact:

- `docs/reports/goal1985_pod_spatial_bucket_dbscan_cupy_perf.json`

## Design Lesson

The previous scary DBSCAN numbers were partly a measurement bug: the timing path
was running the O(n^2) Python oracle after the v2 result. Once validation is
separated from timing, the reusable design direction is clear:

```text
generic candidate graph -> partner component/reduction algebra -> app-level labels
```

The next real engineering step is to move the spatial bucket index itself onto
the partner side so the same sparse contract can become true zero-copy later.
