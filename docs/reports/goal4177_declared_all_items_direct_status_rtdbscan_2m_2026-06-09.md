# Goal4177: Declared RTDBSCAN All-Items Direct-Status 2M Pod Timing

Status: accepted pod evidence; no automatic route promotion.

## Purpose

Goal4176 refactored the caller-declared all-predicate RT-DBSCAN route so it
uses the generic all-items direct-status component-signature primitive directly
instead of materializing synthetic predicate and neighbor-count columns.

Goal4177 measures that post-refactor route on the same 2,097,152-point road3d
shape used by Goal4173.

## Environment

- Commit: `d9b9d60f605440f4c16e182f3ebd38ece0fa958e`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.08`
- Dataset: `road3d`
- Point count: `2,097,152`
- Seed: `20260519`
- Partition cell factor: `0.25`
- Repeat/warmup: `repeat = 1`, `warmup = 0`
- Warmup policy: per-route 4,096-point warmup before each large measurement
- Artifact: `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json`

## Results

| Route | Elapsed sec | Wall sec | Same signature | Predicate columns | RT count-threshold | Generic all-items signature |
| --- | ---: | ---: | --- | --- | --- | --- |
| current grouped-stream Numba | `34.321601` | `48.446151` | yes | n/a | no | no |
| measured all-true predicate direct-status | `25.557633` | `39.713658` | yes | yes | yes | no |
| declared all-items direct-status | `20.144741` | `29.236318` | yes | no | no | yes |

Elapsed speedups:

- Declared all-items versus current grouped-stream: `1.704x`
- Declared all-items versus measured all-true predicate direct-status: `1.269x`

Wall-clock speedups:

- Declared all-items versus current grouped-stream: `1.657x`
- Declared all-items versus measured all-true predicate direct-status: `1.358x`

All three routes preserve the same RT-DBSCAN app signature:

`cluster_sizes = {1: 2097152}, core_count = 2097152, noise_count = 0`

## Interpretation

The Goal4176 refactor was both cleaner and faster. The declared route now avoids
the predicate-column wrapper entirely and reports:

- `predicate_columns_materialized = false`
- `rt_count_threshold_executed = false`
- `uses_generic_all_items_direct_status_signature = true`
- `rt_core_accelerated = false` for the declared subpath

This is a runtime-level improvement because it promotes the reusable pattern:
when a caller has an external proof that every item satisfies the predicate,
the app can invoke the generic all-items component primitive and adapt the
signature at the app boundary.

## Boundary

This evidence does not authorize release, public speedup wording, broad RT-core
wording, whole-app claims, paper-reproduction claims, automatic partner
selection, automatic route selection, automatic factor selection, hidden
border-policy selection, mixed-predicate direct-status promotion, AMD
performance claims, app-specific native-engine logic, or true-zero-copy claims.

The declared route requires explicit caller selection and external proof that
all predicate flags are true. Mixed-predicate RT-DBSCAN rows remain on the
grouped-stream Numba route unless a future generic border-assignment policy
primitive is designed, implemented, measured, and reviewed.
