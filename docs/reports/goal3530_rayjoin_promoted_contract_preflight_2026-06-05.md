# Goal3530: RayJoin Promoted-Contract Preflight

Date: 2026-06-05

Status: Goal3527 implementation preflight. This is not a performance result and
does not authorize any public claim.

## Purpose

Goal3527 requires a RayJoin preflight before promoted v2.8 RayJoin rows are
measured. The point is to separate runnable contracts from contracts that have
lower-level pieces but still need a promoted runner. Without this split, the
old single `spatial_rayjoin` row can hide different levels of readiness:
count/parity, relation columns, shape-pair payload, and overlay-area
continuation are not the same contract.

## Source Surfaces Inspected

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `src/rtdsl/geometry_relation_continuations.py`
- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`
- RayJoin relation and overlay probes under `scripts/goal3447*`,
  `scripts/goal3453*`, `scripts/goal3456*`, `scripts/goal3465*`,
  `scripts/goal3488*`, `scripts/goal3489*`, and `scripts/goal3492*`.

## Contract Readiness Table

| Promoted RayJoin contract | Current status | Runnable surface | Measurement decision |
| --- | --- | --- | --- |
| Count/parity | `runnable_app_cli` | `--execution-route prepared_optix --result-mode count`, `prepared_optix_compact_grouped_count`, `prepared_optix_left_id_dense_count`, `prepared_optix_shape_pair_active_count` | Can be measured first, but each subroute must be reported as its own row. |
| Relation columns | `runnable_app_method` | `PreparedRayJoinOptixShapePairActiveCount.active_relation_device_columns`, `run_packed_left_active_relation_device_columns`, and `run_packed_left_active_relation_grouped_count_by_left` | Can be measured after adding a normalized promoted-runner entry point or direct probe packet. Do not fold into count/parity. |
| Shape-pair payload | `runnable_script_or_rtdsl_surface` | `shape_pair_relation_active_shape_ordinals_cupy`, `shape_pair_relation_witness_cupy`, `shape_pair_relation_complexity_cupy`, `shape_pair_relation_convex_overlay_area_cupy`, and geometry-payload probe scripts | Needs a promoted runner before table timing. Existing pieces prove the contract surface, not a comparable promoted app row. |
| Overlay-area continuation | `runnable_script_or_rtdsl_surface` | `v2_8_overlay_area_continuation_plan`, `prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals`, `evaluate_prepared_overlay_area_tile_task_cupy_inputs`, and the public CDB tile-task executor | Needs a promoted runner and scale/repeat guard before timing. Full overlay-area claims remain blocked. |

## Detailed Findings

### Count/Parity

The app CLI already exposes the count path. `prepared_optix` can run PIP, LSI,
and overlay-seed workloads with `result_mode=count`. More specialized prepared
routes exist for LSI compact grouped count, LSI left-id dense count, and
overlay-seed shape-pair active count. These rows should be timed separately
because their contracts are different:

- PIP count/parity: closed-shape membership count.
- LSI count/parity: segment-pair intersection count.
- Overlay seed count/parity: active shape-pair dependency count.

This is ready for pod timing, provided the artifact records route, dataset,
scale, repeat policy, phase timings, and claim boundary.

### Relation Columns

The shape-pair active relation column route exists behind the prepared
shape-pair handle. It can produce resident relation columns, metadata, and a
grouped count by left id. This is stronger than a scalar count and should be
reported as a separate promoted contract.

However, the main CLI does not yet expose a normalized relation-column row that
matches the Goal3527 promoted-path table shape. Before performance timing, add
or use a direct packet that records row count, overflow status, column metadata,
grouped-count correctness, and phase timing.

### Shape-Pair Payload

The lower-level payload surfaces exist in RTDSL and probes. They can derive
active shape ordinals, witness columns, shape-complexity columns, and convex
overlay-area continuations from generic relation columns and geometry payload.

This is not yet a clean promoted app row. Treat it as runnable substrate, not
as table-ready evidence. A promoted runner must define:

- input dataset and scale;
- maximum relation capacity and overflow policy;
- payload columns included;
- correctness oracle;
- partner used, if any;
- whether the output is row materialization, scalar summary, or continuation
  input.

### Overlay-Area Continuation

The overlay-area continuation contract and prepared payload evaluator exist,
including a tiled CuPy path and public CDB tile-task executor. These are exactly
the kind of promoted v2.8 pieces that should replace the old single RayJoin
row, but they need a normalized performance packet before comparison.

The next timing artifact must not claim full RayJoin reproduction or full
general polygon overlay. It may only report the specific prepared simple-shape
overlay-area continuation contract that was actually executed.

## Required Next Authoring Before RayJoin Timing

1. Add a compact promoted RayJoin runner or packet generator that emits one row
   per contract: count/parity, relation columns, shape-pair payload, and
   overlay-area continuation.
2. For sub-millisecond rows, include larger scale or repeat metadata so launch
   noise is visible.
3. Keep all routes app-layer or partner-layer. Do not add RayJoin-specific
   native engine shortcuts.
4. Record partner status explicitly. Current continuation surfaces use CuPy
   where partner kernels are required; no hidden PyTorch path is allowed.
5. Carry claim-boundary fields that keep release, public speedup, broad RT-core,
   true-zero-copy, whole-app speedup, and paper-reproduction claims false.

## Goal3527 Decision

RayJoin promoted-path measurement is authorized only after a runner or packet
normalizes the four contracts above. The count/parity contract is immediately
runnable from the app CLI. Relation columns are runnable from app methods but
need a table-shaped runner. Shape-pair payload and overlay-area continuation
have runnable substrate and scripts but need promoted-runner integration before
they can appear in the v2.8 performance table.

