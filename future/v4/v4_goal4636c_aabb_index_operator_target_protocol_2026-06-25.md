# V4 Goal4636C AABB Index Operator Target Protocol

Status: `goal4636c_aabb_index_target_predeclared_pending_pod_gate_not_measured`

## Context

Goal4636 has already rejected two serious candidates:

- `fixed_radius_threshold_summary_2d`: passed the Embree material floor but failed
  the legacy phase-total no-regression floor.
- `ray_triangle_grouped_any_hit_flags_3d`: passed correctness and had strong
  tail/traversal ratios, but failed wrapper-wall floors.

Goal4636C selects a different generic relation/query class that does not require
CuPy and has an existing all-ops prepared runner.

## Target

- generic operator: `aabb_index_query_2d_all_ops_count`
- proposed API surface: `v4_aabb_index_query_2d_all_ops_count_prepared_runner`
- generic primitive: `AABB_INDEX_QUERY_2D`
- target coverage row: `librts_spatial_index`
- continuation class: `aabb_index_all_ops_count`
- scope: `rtdl_native_prepared_runner`
- output contract family: `generic_prepared_aabb_index_query_2d`
- accepted contracts:
  `generic_prepared_aabb_index_query_2d`,
  `generic_prepared_aabb_index_query_2d_count`,
  `generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count`
- runner: `scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`

This is not a LibRTS authors-code or paper-reproduction claim. LibRTS supplies
the spatial-index benchmark row; the engine surface under test is the generic
app-name-free AABB query primitive.

## Promotion Gate

The POD gate must run the large all-ops fixture:

```powershell
python scripts/v3_0_m30_librts_prepared_all_ops_refresh.py `
  --box-count 1000000 `
  --query-count 1000 `
  --seed 2025 `
  --max-box-width 0.005 `
  --max-box-height 0.005 `
  --max-query-width 0.005 `
  --max-query-height 0.005 `
  --operation all `
  --backends embree,optix `
  --warmup 1 `
  --repeat-overrides embree=240,optix=240 `
  --output future/v4/evidence/v4_goal4636c_aabb_index_all_ops_pod_gate_2026-06-25/m30_all_ops.json
```

Promotion requires all of the following:

- cross-backend counts match;
- Embree and OptiX use the same `AABB_INDEX_QUERY_2D` primitive and an accepted
  `generic_prepared_aabb_index_query_2d` contract-family member;
- all rows remain primitive-first and require no partner continuation;
- public speedup flags remain false;
- CPU reference is explicitly skipped for the large gate because the direct
  O(n*m) oracle is impractical at 1,000,000 x 1,000; correctness is the
  cross-backend count-signature match on the same fixture;
- `embree_over_optix_query_median >= 10.0x`;
- `embree_query_total_sec / optix_query_total_sec >= 10.0x`;
- no LibRTS paper, authors-code, or whole-app spatial-index speedup wording is
  authorized by this gate.

If this gate passes, the next action is a separate front-door/catalog goal that
adds the public V4 surface and refreshes coverage. The gate itself does not
directly authorize release or public V4 speedup wording.

## Review Amendments Applied

Claude's protocol review required two corrections before POD execution:

- Contract handling is now family-based instead of exact-string equality. The
  runner accepts the base contract, the Embree count contract, and the qualified
  OptiX prepared-count contract as members of the same generic AABB
  prepared-query family, while still requiring the same primitive and count
  signatures.
- Repeat counts are now symmetric (`embree=240,optix=240`). This keeps the
  median and total-time floors equivalent; the old asymmetric 240/3200 setting
  would have made a nominal 10x total floor imply roughly 133x per-query
  speedup.

## Expected Coverage Effect

If the gate passes, `librts_spatial_index` may move from
`deferred_or_uncovered_v4_0` to `strong_measured_operator_coverage` because its
core spatial-index query path maps to a measured generic AABB all-ops count
surface.

If the gate fails, `librts_spatial_index` remains deferred and Goal4636 must
select another target or stop with an explicit coverage-limit decision.

## Local Validation

```powershell
py -m unittest tests.v4_goal4636_aabb_index_target_test
```

## Non-Authorization

This protocol does not authorize V4 release, release-candidate wording, broad
speedup claims, whole-app speedup claims, LibRTS paper reproduction claims,
authors-code comparison claims, public true-zero-copy claims, Tier-3 callback
support, raw OptiX callback support, CuPy performance claims, C ABI, embedding,
non-Python host claims, or app-specific native kernels.
