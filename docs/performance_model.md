# RTDL Performance Model

This page explains how to read RTDL performance claims in the current v1.6
release line. It is intentionally stricter than marketing language: a
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
- v1.6 keeps the v1.0 app-shaped proof history and publishes the first
  Python+RTDL architecture milestone for the supported Embree+OptiX primitive
  surface.
- Some native entry points remain workload-shaped compatibility/proof surfaces;
  v1.6 is not a zero-app-knowledge native-engine release.
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
- [v1.5 Release Package](release_reports/v1_5/README.md)
- [v1.0 RTX App Status](v1_0_rtx_app_status.md)
- [v1.0 App Acceleration Inventory](v1_0_app_acceleration_inventory.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- `rtdsl.rtx_public_wording_matrix()`

## v1.5 App Performance Reality

v1.5 is the current standalone Embree+OptiX language/runtime release for the
supported surface. It keeps the v1.0 app-shaped proof history, so performance
is still mixed by design:

- RT traversal-heavy sub-paths can be fast.
- Full apps may still be slow when Python owns ranking, clustering, exact
  polygon refinement, graph reductions, or force computation.
- Some app-specific or workload-shaped native continuations exist to make the
  proof apps measurable.
- Those continuations are proof machinery, not the final app-independent native
  engine architecture.

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
  materialization outside traversal, that is v1.6.x/v2.0 design input rather
  than a failed OptiX proof.

## What v1.6 Publishes

The released v1.6 package has Windows, Linux, and OptiX validation evidence for
the supported Python+RTDL architecture boundary. Those subpaths express more app
continuations through reviewed backend primitives instead of hardcoded app
logic:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`

`COLLECT_K_BOUNDED` remains experimental and is deferred to follow-up
performance work. v1.6 is
not a claim that every app is automatically fast. App-level continuations such
as ranking, clustering, graph analytics, SQL-style materialization,
exact-distance rows, and force-vector reduction remain outside the verified
v1.6 subpath boundary unless a later report explicitly moves them.

## What v1.7-v2.0 Should Fix

v1.7-v2.0 are the broader partner-interoperability performance track. They
should preserve the Python-facing DSL while removing Python from hot data
movement and heavy non-RT continuation work:

- stable compiled plans
- flat native-ready buffers
- direct backend dispatch
- thin result views
- zero-copy or low-copy interop with GPU compute tools
- explicit boundaries between RT traversal, compute reductions, and Python
  presentation

Until that architecture exists, public docs should say v1.6 provides the first
Python+RTDL architecture milestone for the bounded release surface and selected
sub-path evidence, not universal whole-app speedup.

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
