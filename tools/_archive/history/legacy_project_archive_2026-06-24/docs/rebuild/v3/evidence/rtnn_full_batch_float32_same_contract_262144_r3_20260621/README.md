# Phoenix V3 RTNN Full-Batch Float32 Same-Contract Evidence

Status: `rtnn_full_batch_float32_same_contract_pod_evidence_pending_2ai_not_m7`.

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
- `repeat`: `3`
- `routes`: `['optix', 'cupy_grid']`
- `result_mode`: `ranked-summary-aggregate-prepared-query-batch-float32`
- `dry_run`: `False`

## Phase Rows

### cupy_grid

- Hot query median: `0.002199262` sec
- Cold-plus-query wall: `0.597401291` sec
- Runner wall: `1.123590373` sec

### optix

- Hot query median: `0.000891380` sec
- Cold-plus-query wall: `3.494303070` sec
- Runner wall: `4.042359449` sec

## Comparisons

- `rtdl_optix_over_cupy_grid_hot_speedup`: `2.467256`
- `rtdl_optix_over_cupy_grid_cold_plus_query_speedup`: `0.170964`
- `rtdl_optix_over_cupy_grid_runner_wall_speedup`: `0.277954`

## Parity

- Same-contract signature match: `True`
- Integer signature match: `True`
- Sum-distance relative error: `2.6153052160286284e-10`

## Checks

- `runner_completed_without_route_errors`: `True`
- `serious_fixture_scale`: `True`
- `rtdl_optix_route_present`: `True`
- `cupy_grid_reference_route_present`: `True`
- `all_routes_ok`: `True`
- `same_contract_signature_match`: `True`
- `phase_table_has_load_prepare_query_wall`: `True`
- `optix_rt_hardware_gate_passed_if_required`: `True`
- `material_rtdl_over_reference_speedup`: `True`

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
