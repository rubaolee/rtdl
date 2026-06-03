# Goal3161: v2.8 Runtime-Gap Hausdorff Generic-Alias Refresh

Date: 2026-06-03

Status: `implemented`

## Purpose

Goal3160 added the generic
`directed_max_of_nearest_distance_2d_partner_columns(...)` front-door alias and
routed the Hausdorff benchmark app's `partner_exact` path through it. The v2.8
runtime-gap matrix still described Hausdorff as if the Python adapter name were
the unresolved issue.

Goal3161 refreshes that matrix so it separates:

- **Solved:** the recommended exact partner path now uses a generic max-nearest
  continuation name and generic contract metadata.
- **Still open:** the RT-core nearest-witness path is still a benchmark research
  harness, not yet a reusable typed producer stream that can feed the partner
  continuation directly.

## Change

Updated the `hausdorff_xhd` row in `src/rtdsl/v2_8_benchmark_runtime_gap.py`:

- `current_best_path` now mentions the generic directed max-of-nearest-distance
  front door and keeps the active-frontier RTDL/OptiX path as the RT-core
  research harness.
- `partner_position` now names Numba as the recommended scalar exact partner
  continuation while keeping CuPy as the CUDA-core fairness baseline.
- `current_bottleneck` now points to typed RT nearest-witness producer streams,
  not app-shaped adapter naming.
- `evidence_refs` now includes `Goal3143` and `Goal3160`.

## Boundary

This is a matrix/status refresh only. It does not change execution behavior,
timing, native code, partner kernels, release status, or public claims.

Claim flags remain blocked:

- `release_authorized: False`
- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3161_v2_8_runtime_gap_hausdorff_generic_alias_refresh_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
........
----------------------------------------------------------------------
Ran 8 tests in 0.017s

OK
```
