# Goal669: Cross-Engine Performance Optimization Lessons From Apple RT Visibility Count

Date: 2026-04-20

Status: draft for Claude/Gemini review and consensus

## Purpose

This report records the engineering experience from optimizing the Apple RT
2D visibility/collision count path, and extracts reusable lessons for other
RTDL workloads and engines.

The concrete case was narrow:

- workload: 2D visibility/collision blocked-ray count
- engine: Apple Metal/MPS RT on Apple M4
- optimized output contract: one scalar `blocked_ray_count`
- not optimized output contract: full emitted `{ray_id, any_hit}` rows

The goal here is not to claim that the same speedup applies everywhere. The
goal is to document a repeatable optimization method that can be applied to
Embree, OptiX, Vulkan, HIPRT, and Apple RT when a workload has similar reuse
and output-shape opportunities.

## Starting Point

Before the final optimization, Apple RT could execute the 2D any-hit workload
and match other backends, but the app-level timing was not competitive with
Embree for full row output.

The key observation from Goal665 profiling was:

Native Apple RT traversal was already relatively small. The expensive parts of
the Python-facing path were:

- Python-side ray packing repeated for every query
- Python dictionary row materialization for every ray
- repeated wrapper overhead around output conversion

This changed the optimization target. Instead of immediately trying to make the
MPS traversal itself faster, we first changed the app contract for workloads
that only need a summary count.

## Final Measured Result

After adding a prepared scene, prepacked rays, and a scalar count path, Goal666
measured the following on Apple M4:

| Case | Apple RT packed count | Embree row count | Shapely/GEOS count |
| --- | ---: | ---: | ---: |
| dense blocked, 32768 rays / 8192 triangles | 0.001330064 s | 0.015297282 s | 0.297816304 s |
| mixed visibility, 32768 rays / 8192 triangles | 0.001182773 s | 0.015251223 s | 0.252873766 s |
| sparse clear, 32768 rays / 8192 triangles | 0.000910397 s | 0.014742673 s | 0.196451636 s |

Setup costs were reported separately:

| Case | Apple RT scene prepare | Apple RT ray pack |
| --- | ---: | ---: |
| dense blocked | 0.075947 s | 0.014594 s |
| mixed visibility | 0.027678 s | 0.014007 s |
| sparse clear | 0.027287 s | 0.013420 s |

Approximate break-even against the measured Embree row-count path:

| Case | Apple RT setup total | Per-query Apple-vs-Embree delta | Approximate break-even repeated queries |
| --- | ---: | ---: | ---: |
| dense blocked | 0.090541 s | 0.013967218 s | 7 |
| mixed visibility | 0.041685 s | 0.014068450 s | 3 |
| sparse clear | 0.040707 s | 0.013832276 s | 3 |

This break-even estimate is only for the tested scalar count contract and the
tested Apple M4 harness. It should not be reused as a general Apple RT or
full-row-output claim.

Correct interpretation:

Apple RT is faster in this harness for repeated scalar blocked-ray count when
the scene and rays can be reused.

Incorrect interpretation:

Apple RT is broadly faster than Embree, faster for full emitted rows, or faster
for all RTDL workloads.

## Optimizations Used

### 1. Prepared Build-Side Data

The blocker triangles are converted into a prepared Apple RT acceleration
structure once and reused across repeated queries.

General lesson:

Any RTDL workload with stable build-side data should have a prepared API.
This applies to:

- static triangle meshes
- static obstacle fields
- static point sets for nearest-neighbor workloads
- static graph CSR data
- static DB/columnar tables for repeated predicates

Engine-specific notes:

- Embree: prepared scenes and committed geometry should be reused.
- OptiX: GAS/IAS builds should be reused when build data is stable.
- Vulkan: acceleration structures and descriptor sets should be reused.
- HIPRT: scene/BVH and traversal state should be reused, but memory growth must
  be profiled because previous HIPRT graph evidence showed OOM risk.
- Apple RT: MPS acceleration structures and command queues should be reused.

### 2. Prepacked Probe-Side Data

The rays are converted from Python objects into native records once through
`prepare_apple_rt_rays_2d(...)`.

General lesson:

When an app repeatedly queries the same probes, Python object normalization and
native packing must not be repeated in the hot loop.

Useful targets:

- repeated visibility rays
- repeated sensor rays
- repeated query points in kNN/fixed-radius workloads
- repeated graph frontier blocks in iterative graph algorithms when shape is
  stable
- repeated predicate batches in DB-style workloads

This is especially important for Python-hosted RTDL because Python should
orchestrate, not perform heavy repeated data marshaling.

### 3. Output-Contract Reduction

The optimized path returns one scalar blocked-ray count instead of full
`{ray_id, any_hit}` rows.

General lesson:

The fastest useful result is often not the most general row table. If an app
only needs:

- any collision?
- number of blocked rays?
- number of neighbors?
- max nearest-neighbor distance?
- grouped count?
- grouped sum?

then the engine should expose a reduced output path that avoids full row
materialization.

This does not replace row output. RTDL still needs row output for debugging,
composition, correctness, and general app logic. But hot app paths should be
allowed to request a bounded reduction when the app semantics permit it.

### 4. Native Profile Split Before Optimization

Goal665 split native timing into:

- buffer setup
- ray packing
- dispatch/wait
- result scan
- output

General lesson:

Do not optimize blindly. First measure where the time goes. In this case, the
biggest win was not a low-level traversal change; it was avoiding Python row
materialization and repeated packing.

Every serious backend optimization should include this split:

- prepare/build time
- probe packing time
- native dispatch time
- native result scan/reduction time
- Python materialization time
- total wall time

### 5. Reusable Native Work Buffers

The prepared Apple RT handle owns reusable Metal ray and intersection buffers
sized to the largest query seen so far.

General lesson:

Backend hot paths should avoid repeated allocation. Allocation is often hidden
inside "simple" wrappers and can dominate short kernels.

Engine-specific notes:

- Embree: avoid rebuilding temporary scene objects in tight loops.
- OptiX/Vulkan/HIPRT: reuse device buffers, descriptor records, launch params,
  and output buffers.
- Apple RT: reuse Metal buffers and command infrastructure where safe.

### 6. Correctness-Preserving Narrowing

The optimized path changed the output contract but not the meaning:

- full rows answer: which rays are blocked?
- scalar count answer: how many rays are blocked?

Correctness was still checked through backend agreement on the same generated
cases.

General lesson:

Optimized reduced-output paths must be derived from and cross-checked against
the canonical row-output semantics. The reduction cannot silently change the
predicate.

## What Did Not Generalize Automatically

### 1. Scalar Count Is Not Full Row Output

The Apple RT packed-count result is not evidence that Apple RT beats Embree for
full emitted rows. Full rows still pay Python dictionary materialization and
larger output transfer costs.

Reusable rule:

Always compare equal output contracts. If contracts differ, report them
separately.

### 2. Repeated Query Is Not First Query

Prepared APIs shift cost out of the hot loop. This is correct for repeated
apps but misleading for one-shot apps if setup is ignored.

Reusable rule:

Always report:

- first-query time including prepare and pack
- repeated-query time excluding one-time setup
- break-even estimate when possible

### 3. Engine Semantics Differ

Apple RT does not expose the same programmable any-hit model as OptiX or
Vulkan. The current scalar count path uses nearest-hit existence over a
prepared MPS prism acceleration structure. Claude correctly identified this as
a future optimization opportunity, not a correctness bug.

Reusable rule:

Do not force all engines to claim the same internal mechanism. Public API
parity is not the same as identical backend semantics.

### 4. Hardware Backend Is Not Always RT-Hardware Backend

Apple DB/graph paths are Metal compute/native-assisted paths, not Apple
ray-tracing-hardware traversal. Similar distinctions exist elsewhere:

- HIPRT-on-NVIDIA is HIPRT through Orochi/CUDA, not AMD GPU validation.
- GTX 1070 results are GPU backend evidence, not RT-core evidence.
- `reduce_rows` is Python standard library logic, not native RT acceleration.

Reusable rule:

Every performance report should say which hardware mechanism was actually
used.

## Cross-Workload Application Plan

### Visibility And Collision

Best fit for the learned pattern.

Why:

- build-side obstacles are often static
- probe rays can be reused or generated in batches
- apps often need `any`, `count`, or per-object flags instead of full rows

Recommended next optimizations:

- prepared packed count for Embree, OptiX, Vulkan, HIPRT
- grouped count by object/pose/link when app needs collision flags
- batch many ray sets per launch where backend launch overhead matters

### Nearest Neighbor

Good fit, but output contract must be chosen carefully.

Potential reduced outputs:

- neighbor count within radius
- any neighbor within radius
- min distance
- max nearest-neighbor distance for Hausdorff

Recommended next optimizations:

- prepared query-point buffers
- reduced native outputs for `count`, `min`, `max`
- avoid materializing all neighbor rows when only density or max-distance is
  required

Boundary:

For kNN, exact row output may still be needed for app logic. Do not replace
ranked rows with summary reductions unless the app accepts that contract.

### Graph Workloads

Mixed fit.

Potentially useful:

- prepared CSR graph data
- prepared frontier buffers for repeated BFS levels
- count-only or changed-frontier-only outputs

Harder parts:

- frontier changes every iteration
- graph outputs often need exact vertex IDs, not just counts
- memory layout can dominate performance more than traversal

Recommended next optimizations:

- profile data movement and output materialization first
- add reduced outputs only for algorithms that truly need counts or flags
- keep PostgreSQL/reference correctness for graph result semantics

### DB-Style Workloads

Good conceptual fit, but the backend representation matters.

Potential reduced outputs:

- count of matching rows
- grouped count
- grouped sum
- boolean exists

Recommended next optimizations:

- prepared columnar table buffers
- prepared predicate batches
- native aggregation where backend supports efficient atomics/reductions
- compare against PostgreSQL with indexing/preparation/query phases reported
  separately

Boundary:

RTDL is not a DBMS. These are bounded analytical kernels, not arbitrary SQL,
transactions, joins, or query planning.

### Spatial Overlay / Polygon Workloads

Partial fit.

Useful:

- prepared polygon/segment geometry
- candidate count or any-overlap summaries
- batch repeated probes against static map layers

Harder:

- exact polygon output often requires rich row materialization
- topology and geometry repair can dominate

Recommended next optimizations:

- separate candidate discovery from exact refinement time
- use reduced outputs only when the app needs flags/counts rather than exact
  geometry rows

## Cross-Engine Priorities

### OptiX

Priority: highest.

Expected approach:

- use true any-hit / early termination where possible
- keep data on GPU for reduced outputs
- provide prepared scene and packed probe buffers
- implement native count/reduction paths before Python row materialization

Risk:

- launch overhead and device transfers can hide traversal gains on small cases

### Embree

Priority: high CPU baseline.

Expected approach:

- prepared `RTCScene` reuse
- `rtcOccluded1` for any-hit
- native count/reduction APIs for scalar outputs
- avoid Python row dictionaries when apps only need counts

Risk:

- Embree is already mature; wins mostly come from output contract and data
  reuse, not from beating its traversal

### Vulkan

Priority: correctness first, then avoid slow paths.

Expected approach:

- reuse acceleration structures, descriptor sets, and buffers
- use `terminateRayEXT` for any-hit
- reduce output on device when possible

Risk:

- engineering overhead and driver variability can exceed kernel gains

### HIPRT

Priority: correct and optimized after OptiX/Embree, with memory caution.

Expected approach:

- prepared HIPRT scene/BVH reuse
- count/reduced outputs
- profile memory scaling before large graph-like workloads

Risk:

- previous large graph evidence showed `std::bad_alloc`
- NVIDIA-through-Orochi results are not AMD GPU results

### Apple RT

Priority: correct, honest, and app-useful on Apple Silicon.

Expected approach:

- use MPS RT where available
- prepare MPS acceleration structures
- prepack probes
- expose reduced-output paths for repeated Mac apps

Risk:

- Apple MPS RT does not expose the same programmable any-hit model as OptiX or
  Vulkan
- some workloads are Metal compute/native-assisted rather than Apple
  ray-tracing-hardware traversal

## Proposed Optimization Checklist For Future Workloads

For each workload-engine pair, answer these questions before claiming
performance:

1. Is the build side stable enough for a prepared object?
2. Is the probe side stable enough for prepacking?
3. Does the app need full rows, or only `any`, `count`, `min`, `max`, `sum`, or
   grouped reductions?
4. Is the measured path first-query, repeated-query, or both?
5. Are setup costs reported separately?
6. Is Python doing heavy work in the hot loop?
7. Is the backend using RT traversal, GPU compute, CPU fallback, or mixed
   native-assisted execution?
8. Is correctness checked against the canonical row semantics or oracle?
9. Is the comparison output-contract fair?
10. Is the claim bounded to the tested host, scale, and backend?

## Recommended RTDL API Direction

The Apple RT result supports this API direction:

```python
prepared = rt.prepare_backend_workload(build_data)
packed_probe = rt.prepare_backend_probe(probe_data)
summary, profile = prepared.reduce_packed(
    packed_probe,
    op="count",
    predicate="ray_triangle_any_hit",
)
```

But the public API should remain workload-specific first, not too generic too
soon. The safer evolution is:

- add prepared/reduced paths for proven hot workloads
- keep canonical row-output APIs as the semantic source of truth
- later unify common patterns if multiple workloads converge on the same shape

## Main Lessons

1. Performance came from matching the app's real output need, not from only
   tuning traversal.
2. Python-hosted RTDL must keep Python out of repeated hot loops.
3. Prepared build data and prepacked probe data are first-class optimization
   concepts.
4. Reduced-output contracts are powerful but must be documented separately from
   full row output.
5. Backend parity at the API level does not mean identical backend mechanisms.
6. Every engine needs mechanism-specific honesty: RT hardware, GPU compute,
   CPU refinement, and Python post-processing must be separated.
7. Performance reports should include first-query cost, repeated-query cost,
   output contract, setup cost, and correctness method.

## Consensus Request

Claude and Gemini should review this report for:

- whether the lessons are technically valid
- whether any claim is overstated
- whether the cross-workload and cross-engine recommendations are actionable
- whether the output-contract boundary is strong enough
- whether this report is suitable as a future optimization playbook for RTDL
