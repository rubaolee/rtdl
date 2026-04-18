# RTDL v0.8 Release-Candidate Statement

Date: 2026-04-18
Status: release candidate / not yet tagged

## Statement

RTDL `v0.8` is the app-building line on top of the released `v0.7.0`
language/runtime surface.

The current released version remains `v0.7.0` until an explicit `v0.8.0` tag is
authorized and created.

The v0.8 claim is not that RTDL became a full application framework. The claim
is narrower and intentional:

> RTDL can serve as the heavy query/candidate-row kernel inside useful Python
> applications, while Python owns orchestration, reductions, labels, metrics,
> and output.

The programming model remains:

```text
input -> traverse -> refine -> emit
```

In practical app terms:

```text
RTDL emits rows; Python turns those rows into an application answer.
```

## What v0.8 Adds

The accepted v0.8 app suite contains six RTDL-plus-Python applications:

| App | RTDL-owned kernel work | Python-owned application work |
| --- | --- | --- |
| Hausdorff distance | `knn_rows(k=1)` nearest-neighbor rows in both directions | directed/undirected max reduction and witness reporting |
| ANN candidate search | `knn_rows(k=1)` over a Python-selected candidate subset | candidate construction, recall, and distance-ratio reporting |
| Outlier detection | `fixed_radius_neighbors` rows | density counting and outlier thresholding |
| DBSCAN clustering | `fixed_radius_neighbors` rows | core/border/noise detection and cluster expansion |
| Robot collision screening | `ray_triangle_hit_count` rows | pose/link construction and collision aggregation |
| Barnes-Hut force approximation | `fixed_radius_neighbors` body-to-node candidate rows | quadtree construction, opening rule, fallback bodies, and force reduction |

## What v0.8 Proves

v0.8 proves that the existing RTDL row-emission surface can support multiple
paper-derived app workloads without changing language internals first.

This is the important product-level result:

- users can write the app in Python
- RTDL owns the spatial/proximity/ray-query kernel
- the same app shape can run across available RTDL backends where the underlying
  workload supports them
- the docs now expose a concrete app-building path instead of presenting RTDL
  only as a fixed workload catalog

## Evidence Trail

Core app and scope evidence:

- Goal499: paper-workload feasibility for RTDL+Python apps
- Goal503: robot collision screening app
- Goal504: Barnes-Hut force approximation app
- Goal505: v0.8 app-suite consolidation
- Goal517: ITRE app programming model
- Goal519: RT workload-universe roadmap from the survey paper
- Goal520: Stage-1 proximity apps
- Goal521: workload-scope decision matrix

Performance and validation evidence:

- Goal507: Hausdorff Linux performance evidence
- Goal509: robot/Barnes-Hut Linux performance evidence
- Goal523: Linux public command validation
- Goal524: Stage-1 proximity Linux performance characterization
- Goal528: macOS post-doc-refresh local audit
- Goal529: Linux post-doc-refresh validation

Documentation and history evidence:

- Goal525: public-doc refresh after Goal524
- Goal526: stale v0.8 app-count cleanup
- Goal527: examples and capability-boundary refresh
- Goal495 and follow-up history registrations: complete history map remains
  valid through Goal529

## Current Validation Snapshot

Latest macOS post-doc-refresh audit:

- full unit discovery: `232` tests, `OK`
- public command harness: `62` passed, `0` failed, `26` skipped
- local macOS backends available: CPU Python reference, oracle/CPU, Embree
- local macOS OptiX/Vulkan unavailable as expected

Latest Linux post-doc-refresh validation on `lestat-lx1`:

- full unit discovery: `232` tests, `OK`
- public command harness: `88` passed, `0` failed, `0` skipped
- backend probes: CPU Python reference, oracle/CPU, Embree, OptiX, Vulkan all
  available
- PostgreSQL accepts local connections
- GPU visible: NVIDIA GeForce GTX 1070

## What v0.8 Does Not Claim

v0.8 does not claim:

- a new released language/internal surface beyond the documented app usage
- that RTDL is a full application framework
- that RTDL is a full ANN system, FAISS replacement, HNSW/IVF/PQ index, or
  learned vector-search engine
- that RTDL is a production anomaly-detection or clustering system
- that RTDL is a full robotics stack or continuous collision-detection engine
- that RTDL is a full Barnes-Hut or N-body solver
- that every RTDL backend is faster for every app
- that Stage-1 proximity apps beat SciPy, scikit-learn, FAISS, or other
  production baselines

## Performance Boundary

v0.8 performance evidence is intentionally app-specific:

- Goal507 shows Hausdorff multi-backend Linux evidence and external nearest
  neighbor baselines. RTDL OptiX/Vulkan beat RTDL Embree in that run, but mature
  exact 2D nearest-neighbor baselines such as SciPy `cKDTree` and FAISS
  `IndexFlatL2` remain stronger in that evidence.
- Goal509 accepts CPU/Embree/OptiX for robot collision screening and rejects
  robot Vulkan because of a per-edge hit-count parity mismatch. It also accepts
  CPU/Embree/OptiX/Vulkan for Barnes-Hut candidate generation while keeping
  Python force reduction separate.
- Goal524 characterizes ANN candidate search, outlier detection, and DBSCAN
  across RTDL CPU/oracle, Embree, OptiX, and Vulkan on Linux. It is not an
  external-baseline speedup claim; SciPy was not installed in that validation
  checkout.

## Release Candidate Position

This package is ready for external release review as a bounded v0.8
release-candidate package.

It is not a tag by itself. Tagging `v0.8.0` requires explicit release
authorization after final release review.
