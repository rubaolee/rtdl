# Goal4156 - Predicate-Aware Direct-Status Candidate Surface

Date: 2026-06-09

Verdict: implementation-candidate-exposed

## Purpose

Goal4155 defined the next same-contract target after Goal4153 showed that the
fast direct-status component signature was not comparable with the current
RT-DBSCAN core/border/noise contract. Goal4156 exposes the first executable
candidate surface for that target without changing defaults.

## What Changed

- Added a prepared CuPy preview handle for generic predicate-aware
  direct-status grouped-union signatures:
  `prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d`.
- Added a run helper:
  `run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d`.
- Added an explicit benchmark mode:
  `optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d`.

The benchmark mode uses OptiX only for the generic fixed-radius count-threshold
predicate columns, then uses the new generic predicate-aware direct-status
continuation to produce signature columns. It is not a default route.

## Generic Contract

Inputs:

- point coordinate columns
- prepared partition columns and partition AABBs
- caller-supplied predicate flags
- optional caller-supplied count columns
- fixed-radius threshold
- explicit convergence mode

Outputs:

- `label_counts`
- `flag_true_count`
- `negative_label_count`
- `neighbor_counts`
- direct-status telemetry counters

The deterministic neighbor candidate policy is
`lowest_predicate_true_point_id_within_radius`, matching the existing
grouped-stream fallback-candidate policy.

## Boundary

No native ABI was added or renamed. No native ABI may contain `dbscan`,
`cluster`, `core`, `border`, or `noise`. The candidate does not authorize route
promotion, release, public speedup wording, broad RT-core wording, whole-app
benchmark claims, paper reproduction, hidden dispatch, automatic partner
selection, automatic convergence-mode selection, app-specific engine logic, AMD
claims, or true-zero-copy claims.

## Next Validation

The required next step is pod validation:

1. Small same-contract smoke against the current grouped-stream route.
2. Scale probe on `clustered3d`, `road3d`, and `ngsim_dense`.
3. If signatures mismatch, keep the candidate rejected and document the exact
   mismatch. Timings are useful only after same-contract parity is proven.
