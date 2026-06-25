# Phoenix V3 RTNN Full-Batch Float32 Same-Contract Evidence

Status: `rtnn_full_batch_float32_same_contract_runner_plan_not_m7`.

This is a generic `ranked_summary` evidence packet. RTNN is only the
harness for fixed-radius 3-D ranked-summary aggregate work.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
```

## Parameters

- `point_count`: `262144`
- `distribution`: `uniform`
- `seed`: `4502`
- `radius`: `0.02`
- `k_max`: `50`
- `query_batch_size`: `262144`
- `repeat`: `5`
- `routes`: `['optix', 'cupy_grid']`
- `result_mode`: `ranked-summary-aggregate-prepared-query-batch-float32`
- `point_column_source`: `npz`
- `dry_run`: `True`

## Phase Rows

## Parity

- Same-contract signature match: `False`
- Integer signature match: `None`
- Sum-distance relative error: `None`

## Checks

- `runner_completed_without_route_errors`: `False`
- `serious_fixture_scale`: `True`
- `rtdl_optix_route_present`: `False`
- `cupy_grid_reference_route_present`: `False`
- `all_routes_ok`: `False`
- `same_contract_signature_match`: `False`
- `phase_table_has_load_prepare_query_wall`: `False`
- `point_column_source_recorded`: `True`
- `optix_rt_hardware_gate_passed_if_required`: `False`
- `material_rtdl_over_reference_speedup`: `False`

## Forbidden Public Wording

- RTNN is solved
- V3 proves universal nearest-neighbor acceleration
- M106 787x is a public RTNN row
- float32 same-contract runner is M7 without 2-AI review
- RTDL beats the RTNN paper implementation for the whole app

## Goal-Level Decision Audit

Decision: Stage RTNN full-batch float32 same-contract evidence through a reusable runner instead of promoting M106 directly.

1. Was I foolish? No. This follows the M112-approved rerun path and keeps all release flags false.
2. If yes, what actions made the decision foolish? It would be foolish to quote the M106 787.53x-vs-Embree or 2.26x-vs-author figures as a public RTNN win without same-contract reference parity.
3. Was there another path that would have avoided getting stuck on that idea? Repair the exact float64 tie policy first. That remains valid, but it is a semantic review path rather than the fastest route to fresh full-batch evidence.
4. Can I now try a different path that actually solves the problem? Run this checked-in runner on an RTX pod with OptiX plus CuPy grid reference, then seek 2-AI review before reopening any RTNN M7 row.
