# Goals5468-5469: LibRTS Ray-Multicast Feasibility And Generic Fanout Contract

Date: 2026-07-11

## Objective

Determine whether the LibRTS paper's Ray-Multicast mechanism represents a
reusable RTDL system capability or an app-specific implementation detail.  Do
not start a native implementation until the author mechanism, existing RTDL
assets, missing capabilities, non-LibRTS consumer, and falsifiable benefit gate
are explicit.

Goal5468 is the paper/source/history feasibility audit.  Goal5469 implements a
CPU-reference contract only after that audit passes the genericity kill gate.

## Pinned Primary Sources

Paper:

```text
LibRTS: A Spatial Indexing Library by Ray Tracing
PPoPP 2025
Section 3.4, Figure 5, Equations 3-5
official PDF: https://gengl.me/public/publications/ppopp25.pdf
publication pages 401-402
```

Author source:

```text
repository: https://github.com/RTSpatial/RTSpatial
commit: 7c54c181b1058c87768767998c00e225cc58666e
```

The exact file hashes and line anchors are recorded in:

```text
Paper-reproduction-apps/librts-paper/data/author_source/
goal5468_ray_multicast_source_manifest.json
```

The audit used the pinned AE checkout on `lestat@192.168.1.20`.  It did not use
a POD and does not contain a performance result.

## What Ray-Multicast Actually Is

Ray-Multicast is not ordinary query batching and not multiple CUDA streams. It
is a static decomposition of one skewed traversal workload:

1. In the Range-Intersects backward stage, the query AABBs are the traversal
   primitives and indexed geometries generate anti-diagonal rays.
2. Query primitive ordinal `i` is assigned to partition `i % k`.
3. The prepared query AABBs are embedded in disjoint z layers.
4. Every indexed-geometry ray is duplicated across all `k` layers through a
   two-dimensional OptiX launch.
5. The payload layer must equal `primitive_id % launch_dim_y`; this prevents a
   ray from processing primitives assigned to another layer.
6. Every primitive belongs to exactly one layer and every original ray visits
   every layer, so complete pair coverage has neither omission nor duplication.
7. `k` is selected from powers of two using sampled pair selectivity and a
   weighted ray-cast/intersection cost model.

The intended tradeoff is explicit:

```text
maximum primitive load per ray: N -> ceil(N/k)
ray count:                         R -> R*k
```

The optimization is only useful when reduced per-ray intersection work repays
the additional rays and partition preparation.

## Author Source Mapping

`include/rtspatial/spatial_index.cuh`:

- `IntersectsWhatQueryProfiling`, lines 566-683, prepares query AABBs with
  `layer = i % parallelism`, builds the query GAS, and launches backward rays
  with dimensions `(indexed_geometry_count, parallelism)`.
- `CalculateBestParallelism`, lines 690-759, samples geometries and queries,
  estimates selectivity, evaluates power-of-two candidates, and returns the
  least-cost parallelism.

`src/shaders/shaders_intersects_envelope_query_2d.cu`:

- backward intersection lines 76-96 compare the ray payload layer with
  `query_id % launch_dim_y`;
- backward raygen lines 98-127 emit one anti-diagonal ray for each
  `(indexed_geometry, layer)` launch coordinate.

`examples/spatial_index.cu` exposes the computed and command-selected
parallelism.  `examples/flags.cpp` calls this the number of BVHs and rays.

## Historical RTDL Audit

RTDL already has useful pieces:

- a generic prepared OptiX AABB index;
- a prepared box-query GAS;
- two-pass Range-Intersects counts and pair rows;
- prepared multi-operation execution on independent CUDA streams;
- sorted, duplicate-free `(query_id, indexed_id)` relation rows;
- generic row buffers, worklists, and query status streams from earlier apps.

None of these is Ray-Multicast equivalence.  In particular:

- query batching divides queries into launches but does not divide the
  intersection workload of one ray;
- multiple streams overlap independent work but do not bound per-ray hits;
- prepared replay removes setup but does not create disjoint layers;
- X-HD deferred/status worklists implement dynamic scheduling, not static
  partition fanout.

The native gaps are therefore real and narrow:

1. partition-id encoding into disjoint traversal layers;
2. two-dimensional per-ray partition fanout;
3. layer-aware payload filtering;
4. per-ray/per-partition intersection telemetry;
5. a native sampled-selectivity policy handoff.

## Goal5469 Generic System Contract

The new public reference module is:

```text
src/rtdsl/partitioned_traversal.py
```

Public app-neutral APIs:

```python
partitioned_traversal_fanout_plan(...)
estimate_partitioned_traversal_selectivity(...)
select_partitioned_traversal_fanout(...)
```

The plan returns parallel columns for:

```text
primitive_ids
primitive_partition_ids
fanout_ray_ids
fanout_partition_ids
partition_loads
```

It validates non-negative unique IDs, power-of-two partition counts, complete
pair coverage, and cost-model bounds.  Its metadata explicitly says
`python_reference`, `native_backend=false`, `app_semantics=none`, and
`runtime_speedup_claimed=false`.

No LibRTS, RTSpatial, paper, author, or Ray-Multicast identity appears in the
core module.

## Non-LibRTS Consumer

`tests/goal5469_partitioned_traversal_fanout_contract_test.py` contains a
Contact-Manifold-style broad-phase scheduler:

```text
8 obstacle primitives
3 moving-shape traversal rays
k = 4 partitions
```

The consumer directly calls the generic fanout plan.  It does not call a
LibRTS wrapper.  It proves:

```text
baseline maximum primitive load = 8
partitioned maximum load         = 2
fanout rays                       = 12
expected Cartesian pairs         = 24
scheduled pairs                  = 24, exactly equal
```

This is a behavioral non-app proof, not only a naming scan.  It satisfies the
project rule that a paper-driven system API needs an independent consumer.

## Kill-Gate Decision

The direction passes the bounded genericity gate:

```text
generic capability produced                 true
app identity required in core               false
non-LibRTS consumer complete                true
static benefit metric                       max load N -> ceil(N/k)
runtime benefit metric reachable            true
native implementation already complete      false
```

Exit label:

```text
generic_contract_and_non_librts_consumer_complete__
native_optix_pod_spike_authorized__review_pending
```

This authorizes one bounded native OptiX spike after strict review.  It does
not authorize an open-ended implementation campaign.

## Required POD Gate

The next native gate must use the same prepared boxes and query boxes for:

```text
k = 1 baseline
at least two power-of-two k candidates
```

It must report:

- exact canonical pair-row equality against `k=1`;
- per-partition and maximum per-ray hit telemetry;
- preparation/build time separately from query time;
- fresh and prepared timing regimes separately;
- one LibRTS skewed Range-Intersects workload;
- one Contact-Manifold non-app smoke.

Stop the native track if any of these occurs:

- pair-row mismatch;
- measured traversal falls back to host-side partition loops;
- no same-POD end-to-end win over `k=1` on a skewed workload;
- the native ABI requires LibRTS or paper identity.

## Validation

```text
py -m unittest \
  tests.goal5468_librts_ray_multicast_feasibility_audit_test \
  tests.goal5469_partitioned_traversal_fanout_contract_test

Ran 6 tests in 1.206s
OK
```

The generator and new system module also pass `py_compile`. The same focused
suite passes on `lestat@192.168.1.20` (`Ran 6 tests`, `OK`). After forcing LF
output, Windows and Linux independently generate the identical audit artifact:

```text
SHA-256 5a062a04123f7299ac7aefe64190a0816dbea137aec6212d2c1458a320f2baef
```

The complete current LibRTS Goal5453-5469 local suite is `66 tests OK` with
five OptiX-runtime skips on the Windows host.

## Claim Boundary

Authorized:

- the paper and author-source mechanism is pinned;
- existing RTDL assets and missing native capabilities are distinguished;
- an app-neutral reference contract exists;
- a non-LibRTS behavioral consumer exists;
- a bounded POD spike is justified.

Not authorized:

- native Ray-Multicast completion;
- author implementation equivalence;
- runtime speedup;
- Figure 9 reproduction;
- Figure 12 PIP performance reproduction;
- full LibRTS paper reproduction;
- Embree evidence.
