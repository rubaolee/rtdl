# Goal4955: v2.14.3 RayJoin+Numba Generic Pipeline Convergence

Date: 2026-07-04
Status: active

## Objective

Build the v2.14.3 RayJoin-focused, Numba-focused pipeline convergence target:
turn the v2.14.2 numeric binary route into a cleaner generic columnar execution
pipeline, while preserving the invariant:

```text
RTDL is a generic system.
RayJoin is an app and stress test on top of it.
Numba is the selected continuation partner for this stage.
```

The target is not V3/V4 revival, not a new V4 front door, and not a RayJoin
kernel hidden in RTDL core.

## Baseline

The current best v2.14.2 route is Goal4954-E:

```text
route: numeric_binary_route_public_lsi_pip_plus_grouped_carrier
median writer-free hot path: 2.921366s
ratio vs AuthorOfficial overlay compute: 69.39x slower
```

Median phase table:

| Phase | Median seconds |
|---|---:|
| LSI rows | 1.196542 |
| numeric reprojection | 0.221340 |
| numeric sort total | 0.444451 |
| grouped carrier construction | 0.909884 |
| grouped descriptor consumer | 0.059860 |
| total writer-free hot path | 2.921366 |

## What Must Improve

The largest v2.14.2 remaining pre-fusion costs are:

1. LSI row production/materialization.
2. Grouped carrier construction.
3. Numeric sort/group work.
4. Reprojection is smaller but still part of the same pipeline.

Goal4955 focuses on pre-fusion convergence only. It may reduce Python object
construction, repeated row materialization, and app-local glue code. It must not
claim author-class performance.

## Reuse From V3/V4 And Earlier Work

This goal must reuse lessons and assets from:

- v1.5.1 `COLLECT_K_BOUNDED` and explicit app-generic buffer contracts.
- v2.5 neutral buffer / partner choice / device-resident hit-stream guidance.
- V3/V4 operator, fused reduction, row-buffer, device-column, and partner
  continuation experiments.
- Goal4954 grouped carrier and non-RayJoin proof.

Reuse means converging useful mechanisms, not reviving public V3/V4 surfaces.

## Required System Boundary

### RTDL-generic mechanisms may include

- columnar event buffers;
- grouped carriers;
- descriptor-pair or grouped descriptor consumers;
- numeric map/reproject helpers when expressed as generic column transforms;
- Numba continuation hooks over typed columns;
- explicit metadata for host/device/copy status.

### RayJoin app remains responsible for

- CDB loading and paper-specific inputs;
- AuthorOfficial comparison;
- output-chain text writer;
- Section 5.2/5.3/5.7 paper semantics;
- deciding how generic columns map to overlay interpretation.

### Forbidden

- no RayJoin-specific RTDL core primitive;
- no `rayjoin_overlay_fused_kernel`;
- no V4 front-door resurrection;
- no public high-performance claim;
- no Layer 4 traversal-side callback/fusion in this goal;
- no hidden dependency on AuthorOfficial in the generic pipeline layer.

## Work Plan

### Goal4955-A: Baseline Reproduction On POD

Rerun Goal4954-E on the active POD from a clean source tree and record the
current baseline. Do not compare against stale numbers without rerun.

Exit: `baseline_reproduced` or `blocked_by_environment`.

### Goal4955-B: Pipeline Refactor Prototype

Create a v2.14.3 pipeline script/module that factors the numeric binary route
into named stages:

```text
load/pack
public LSI/PIP
numeric event columns
event ordering/grouping
grouped carrier
Numba descriptor consumer
```

The first implementation may live under `history/internal_docs` while being
measured, but the code must be structured so it can later move into a real
RayJoin paper-reproduction app module without dragging internal reports into the
public surface.

Exit: `pipeline_structured_no_perf_claim`.

### Goal4955-C: Remove Avoidable Python Object Work

Replace `OverlayIntersection` object construction in the binary route where
possible with typed numpy column arrays. Keep the exact paper route unchanged.

Priority order:

1. event coordinate/id columns;
2. map-specific ordered event indices;
3. grouped carrier construction from column arrays;
4. descriptor-pair consumer through Numba if useful.

Exit: `columnar_pipeline_measured`.

### Goal4955-D: Numba-Focused Continuation

Use Numba only where the work is numeric array work. Do not force Numba onto
string formatting, file output, or Python object orchestration.

Candidate Numba stages:

- descriptor-pair consumer;
- per-group length/offset computation if it is numeric and stable;
- simple group statistics over typed columns.

Exit: `numba_used_where_structurally_fit` or `numba_not_beneficial_recorded`.

### Goal4955-E: POD Measurement And Decision

Measure at least three runs on the public sample and compare against the rerun
Goal4954-E baseline.

Success thresholds:

- minimum useful win: >= 1.15x vs rerun v2.14.2 numeric binary baseline;
- target win: >= 1.5x vs rerun baseline;
- stretch win: >= 2.0x vs rerun baseline.

The result must preserve the generic boundary and must not claim paper byte
identity for the numeric route.

Exit labels:

- `v2_14_3_pipeline_win_productize_next`;
- `v2_14_3_pipeline_small_win_keep_as_internal`;
- `v2_14_3_pipeline_no_go_pre_fusion_exhausted`;
- `blocked_by_environment`.

## Verification

Required artifacts:

- baseline rerun JSON;
- new pipeline run JSONs;
- median comparison table;
- phase table;
- claim-boundary section;
- non-RayJoin genericity note, either by reusing Goal4954-D proof or adding a
  small new synthetic proof if new generic carrier semantics are introduced.

## Expected Honest Outcome

This goal is expected to improve the v2.14.2 numeric binary route, but it is not
expected to close the author-class performance gap. If the best result remains
far slower than AuthorOfficial, that is an honest result, not failure.

The real question is narrower:

```text
Can we turn the v2.14.2 numeric route into a cleaner, faster, reusable
RayJoin+Numba pipeline without violating the generic RTDL boundary?
```
