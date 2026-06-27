# Phoenix V3 AABB Raw Oracle Evidence

Status: `aabb_raw_oracle_pass_not_m7`

This packet checks raw generic `AABB_INDEX_QUERY_2D`
`range_intersection_rows` output against an independent closed-boundary CPU
AABB oracle. It is not release evidence and not a performance claim.

## Fixtures

| fixture | indexed boxes | query boxes | expected rows | boundary |
|---|---:|---:|---:|---|
| mixed_overlap_zero_touch_duplicate | 5 | 5 | 10 | multiple overlaps, duplicate-prone identical indexed bounds, zero-overlap query, and closed-boundary edge-touch cases |
| dense_capacity_pressure | 4 | 4 | 13 | dense many-to-many overlaps for capacity and duplicate-row pressure |

## Backend Results

| backend | fixture | rows | matches oracle |
|---|---|---:|---|
| embree | mixed_overlap_zero_touch_duplicate | 10 | true |
| embree | dense_capacity_pressure | 13 | true |
| optix | mixed_overlap_zero_touch_duplicate | 10 | true |
| optix | dense_capacity_pressure | 13 | true |

## Capacity Pressure

`{'backend': 'optix', 'fixture': 'dense_capacity_pressure', 'low_capacity': 2, 'expected_required_unique_rows': 13, 'overflow_fail_closed_observed': True, 'error': 'OptiX AABB_INDEX_QUERY_2D range_intersection_rows overflowed capacity 2; emitted at least 13; failure_mode=fail_closed_overflow'}`

## Source Provenance

- Local git head: `fatal: not a git repository (or any of the parent directories): .git`
- Source manifest sha256: `f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422`

## Boundaries

- Release authorized: `false`
- Public speedup claim authorized: `false`
- Broad V3-over-V2 claim authorized: `false`
- M7 promotion authorized: `false`

## Checks

- `all_requested_backends_ran_without_errors`: `true`
- `all_requested_backends_have_all_fixtures`: `true`
- `all_rows_match_independent_cpu_oracle`: `true`
- `embree_backend_checked_if_requested`: `true`
- `optix_backend_checked_if_requested`: `true`
- `optix_capacity_pressure_fail_closed_if_requested`: `true`

Failed checks: `[]`

## Interpretation

This packet validates raw generic AABB range_intersection_rows against an independent closed-boundary CPU oracle. It is correctness/provenance evidence only; it does not authorize M7 promotion, release wording, full Contact Manifold wording, or broad V3-over-V2 claims.

## Goal-Level Decision Self-Audit

Decision: Add an independent raw AABB oracle gate for the native-query-handle candidate instead of relying on Contact Manifold final witness correctness.

1. Was I foolish? No. This directly targets the Huygens P0 correctness blocker without creating a new performance claim.
2. If yes, what actions made the decision foolish? The foolish action would be to call Contact Manifold final witness parity the same as generic AABB candidate-row parity.
3. Was there another path? I could rerun the large benchmark again. That would test timing stability but would not prove the raw AABB row contract.
4. Can I now try a different path? Use this oracle as a blocker-closure artifact, then separately add fresh-run stability before requesting another review.
