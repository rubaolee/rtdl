# RTDL Performance Model

This page explains how to read RTDL performance claims in the current v1.0
foundation line. It is intentionally stricter than marketing language: a
backend flag, a native code path, and a public speedup claim are different
things.

## Short Version

RTDL can improve performance when the hot work is inside a prepared/native
backend path and the comparison uses the same contract. RTDL can be slower when
the app still returns large Python row materializations or when non-RT
post-processing dominates.

The current public performance model is:

- Python is the authoring/control plane.
- Backend/native code should own traversal and candidate discovery.
- v1.0 still uses app-specific native continuations for some demos.
- Python convenience row output is useful for development but can dominate
  runtime.
- Raw/prepared/native summary paths are the serious performance path.
- Public RTX wording is only allowed for reviewed bounded sub-paths.

## Timing Boundaries

RTDL performance evidence must name the boundary being timed.

| Boundary | What it means | How to read it |
| --- | --- | --- |
| Python dict rows | End-to-end convenience output with Python materialization | Good for usability; often not the fastest path |
| Raw rows / thin views | Native result buffers exposed with less Python rematerialization | Better measure of backend execution plus thin host overhead |
| Prepared execution | Build-side data and/or rays are reused | Best for repeated-query workloads |
| Compact/native summary | Backend or native continuation returns reduced app output | Useful when users do not need full witness rows |
| Whole app | Data construction, RTDL execution, post-processing, and output | Only claim this when the evidence explicitly covers it |

## NVIDIA RTX Claim Boundary

For NVIDIA paths, distinguish four levels:

1. `--backend optix` selected an OptiX-capable path.
2. Native OptiX traversal ran for the selected mode.
3. `--require-rt-core` was accepted for a documented bounded path.
4. Same-contract evidence and review authorize public speedup wording.

Only level 4 is a public speedup claim.

Current public RTX wording is governed by:

- [v1.1 OptiX/Embree Status](v1_1_optix_status.md)
- [v1.0 RTX App Status](v1_0_rtx_app_status.md)
- [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- `rtdsl.rtx_public_wording_matrix()`

## v1.0 App Performance Reality

v1.0 intentionally proves app-shaped targets. That makes the demos meaningful,
but it also means performance is mixed by design:

- RT traversal-heavy sub-paths can be fast.
- Full apps may still be slow when Python owns ranking, clustering, exact
  polygon refinement, graph reductions, or force computation.
- Some app-specific native continuations exist to make v1.0 demos measurable.
- Those continuations are v1.0 proof machinery, not the final architecture.

Examples:

- Hausdorff has reviewed bounded prepared threshold-decision wording, but exact
  Hausdorff distance remains outside that RTX claim.
- ANN candidate coverage can be reviewed as a bounded threshold decision, but
  ANN ranking/index speedup remains outside the claim.
- DBSCAN core-count summaries can be native/prepared, but full cluster
  expansion remains outside the RT-core claim.
- Barnes-Hut node coverage can be reviewed as a bounded query, but opening-rule
  and force-vector reduction remain outside the claim.
- Robot collision `prepared_pose_flags` has normalized per-pose wording only,
  not same-total-work or whole-app robot-planning wording.

## Why RTDL Can Be Slower Than Native Code

The convenience path has overhead:

- Python object creation
- input normalization
- `ctypes` marshaling
- result rematerialization into dictionaries
- repeated validation and dispatch

The older [Runtime Overhead Architecture](runtime_overhead_architecture.md)
shows the same lesson with Embree: dict-return paths can be far slower than
native, while raw/prepared raw paths are much closer to the native wrapper
baseline.

## When OptiX Is Slower Than Embree

Embree is a ray-tracing/BVH backend, not a plain Python baseline. For supported
Embree app paths, the CPU comparison is still an RT-style traversal comparison
with native continuation where documented.

A slower OptiX result is acceptable engineering evidence when the same-contract
comparison is clean and the bottleneck is identified. It can close a v1.1/v1.2
investigation as `optix_still_slower_with_reason`, but it cannot authorize
positive public RTX speedup wording.

Use slower-than-Embree results to decide the next architecture step:

- if native traversal is fast but host input construction, scene/ray prepare,
  ray packing, or Python output dominates, the v1.2 target is overhead removal;
- if native traversal itself is slower, the target is backend kernel/layout
  work or a narrower claim boundary;
- if parity or same-contract timing is incomplete, the result stays
  `baseline_contract_incomplete`;
- if the app needs reductions, grouping, ranking, graph analytics, or SQL-style
  materialization outside traversal, that is v1.5/v2.0 design input rather than
  a failed OptiX proof.

## What Current Main Fixed Internally For v1.5

Current `main` has internally pod-verified v1.5 generic subpaths for the
supported migration inventory. Those subpaths express more app continuations
through reviewed backend primitives instead of hardcoded app logic:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- limited `COLLECT_K_BOUNDED`

This is not a public v1.5 release yet and not a claim that every app is
automatically fast. App-level continuations such as ranking, clustering, graph
analytics, SQL-style materialization, exact-distance rows, and force-vector
reduction remain outside the verified v1.5 subpath boundary unless a later
report explicitly moves them.

## What v2.0 Should Fix

v2.0 is the broader performance target. It should preserve the Python-facing
DSL while removing Python from hot data movement and heavy non-RT continuation
work:

- stable compiled plans
- flat native-ready buffers
- direct backend dispatch
- thin result views
- zero-copy or low-copy interop with GPU compute tools
- explicit boundaries between RT traversal, compute reductions, and Python
  presentation

Until that architecture exists, public docs should say v1.0 proves bounded
RTDL app targets and selected sub-path acceleration, not universal whole-app
speedup.

## Public Wording Rule

When writing docs, use this template:

```text
RTDL accelerates <exact prepared/native sub-path> for <app/workload> under
<backend/mode>, with <evidence/report>. This is not a whole-app speedup claim
and does not include <excluded phases>.
```

Do not write:

```text
RTDL accelerates the whole app.
OptiX means RT cores were used.
All graph/DB/polygon workloads are faster with RT.
```
