# Goal4158 Predicate All-True Fast Path Pod Result

Date: 2026-06-09

Status: accepted as a candidate-route improvement, not promoted as a default route.

## Purpose

Goal4157 proved that the predicate-aware direct-status route could preserve the current RT-DBSCAN grouped-stream signature, but its performance was mixed because the predicate route still paid for border-candidate work even on rows where every point is predicate-true.

Goal4158 adds a generic fast path for that case: when caller-supplied predicate flags are all true, the predicate signature route reuses the generic direct-status component-size signature and wraps it as the predicate signature columns. This keeps the runtime app-agnostic: the primitive sees caller-supplied predicate flags and fixed-radius component structure, not DBSCAN semantics.

## Implementation Correction

The first Goal4158 commit placed the shortcut in the plain component-signature helper, where `predicate_flags` is not in scope. The follow-up commit `b1d220ed` moved it into `_run_predicate_direct_status_union_signature_from_prepared_columns_cupy_3d`, after the predicate flags are normalized and validated.

The corrected pod artifact is:

- `docs/reports/goal4158_predicate_all_true_fast_path_scale_factor025_pod.json`
- Commit: `b1d220ed`
- GPU: RTX 4000 Ada pod using the existing CUDA 12.4 / OptiX environment
- Scale: `clustered3d`, `road3d`, `ngsim_dense` at 65,536 / 131,072 / 262,144 points
- Repeat/warmup: repeat 4, warmup 1
- Cell factor: 0.25

## Results

All 18 candidate/current comparisons preserved the same grouped signature as the current grouped-stream Numba route.

| Dataset | Points | Until-stable ratio | Single-pass ratio |
| --- | ---: | ---: | ---: |
| clustered3d | 65,536 | 2.807x | 6.040x |
| clustered3d | 131,072 | 3.141x | 6.371x |
| clustered3d | 262,144 | 3.108x | 6.229x |
| road3d | 65,536 | 1.705x | 3.460x |
| road3d | 131,072 | 1.548x | 3.223x |
| road3d | 262,144 | 1.423x | 2.914x |
| ngsim_dense | 65,536 | 0.950x | 1.796x |
| ngsim_dense | 131,072 | 1.386x | 2.711x |
| ngsim_dense | 262,144 | 1.667x | 3.136x |

Ratio is current grouped-stream elapsed time divided by candidate elapsed time. Values above 1.0 mean the Goal4158 candidate is faster.

Summary:

- Same-contract correctness: 18/18 matched.
- Fast path observed: 18/18 candidate rows had `candidate_all_predicate_fast_path: true`.
- Border-candidate work avoided: 18/18 candidate rows had `candidate_border_candidate_updates: 0`.
- Until-stable route: faster on 8/9 rows; only `ngsim_dense` 65,536 was slightly slower at 0.950x.
- Single-pass candidate route: faster on 9/9 rows, from 1.796x to 6.371x.

## Boundary

This result does not authorize route promotion yet. It proves that the all-predicate subset of the predicate-aware direct-status route is now useful. It does not prove the mixed predicate case, where non-core/border/noise behavior must still use the full predicate path and convergence policy.

The artifact keeps all claim flags false:

- `route_promotion_authorized: false`
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_rt_core_claim_authorized: false`
- `whole_app_claim_authorized: false`

## Next Engineering Step

The next useful RT-DBSCAN target is a mixed-predicate scale packet that deliberately forces border/noise points, then decides whether the predicate direct-status route needs a second fast path for sparse predicate-true cases or should stay as a narrow all-predicate acceleration.
