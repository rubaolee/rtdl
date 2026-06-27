# Phoenix V3 AABB Native Query-Handle Stability Evidence

Status: `aabb_native_query_handle_stability_pass_not_m7`

This packet checks fresh-run stability for the generic AABB
`range_intersection_rows` native query-handle route. It is not release
authorization and not a broad speedup claim.

## Summary

- Fresh runs: `6`
- Material wall-speedup floor: `1.20x`
- Weakest cold-plus-collect wall speedup: `1.644x`
- Mean cold-plus-collect wall speedup: `1.668x`
- Best cold-plus-collect wall speedup: `1.687x`

## By Scale

| grid_count | samples | weakest cold+collect | mean cold+collect | weakest runner wall |
|---:|---:|---:|---:|---:|
| 32768 | 3 | 1.680x | 1.683x | 1.648x |
| 65536 | 3 | 1.644x | 1.654x | 1.610x |

## Samples

| sample | grid_count | cold+collect | runner wall | oracle | native cache |
|---|---:|---:|---:|---|---|
| 32768_s01_20260621 | 32768 | 1.680x | 1.648x | true | true |
| 32768_s02_20260621 | 32768 | 1.687x | 1.649x | true | true |
| 32768_s03_20260621 | 32768 | 1.680x | 1.649x | true | true |
| 65536_s01_20260621 | 65536 | 1.669x | 1.633x | true | true |
| 65536_s02_20260621 | 65536 | 1.650x | 1.616x | true | true |
| 65536_s03_20260621 | 65536 | 1.644x | 1.610x | true | true |

## Checks

- `all_summaries_exist`: `true`
- `six_fresh_runs_present`: `true`
- `three_runs_per_scale`: `true`
- `all_runner_completed`: `true`
- `all_backend_errors_empty`: `true`
- `all_matches_cpu_reference`: `true`
- `all_complete_candidate_coverage`: `true`
- `all_optix_native_cache_observed`: `true`
- `all_cold_plus_collect_wall_clear_floor`: `true`
- `all_runner_wall_positive`: `true`

Failed checks: `[]`

## Boundaries

- Release authorized: `false`
- Public speedup claim authorized: `false`
- Broad V3-over-V2 claim authorized: `false`
- M7 promotion authorized: `false`

## Interpretation

Six fresh POD runs across 32,768 and 65,536 AABBs preserve the material cold-plus-collect wall win for the generic AABB candidate-stream route. This closes the fresh-run stability blocker only; it does not authorize M7 promotion or any public/broad speedup wording.

## Goal-Level Decision Self-Audit

Decision: Add fresh-run AABB native-query-handle stability evidence instead of relying on repeat timing inside one benchmark process.

1. Was I foolish? No. Huygens specifically called for run-to-run stability, and this packet answers that blocker directly.
2. If yes, what actions made the decision foolish? The foolish action would be to treat repeat=50 inside one process as fresh-run stability or to use the stability packet as M7 approval.
3. Was there another path? I could have requested review immediately after raw oracle closure. That would leave a known Huygens blocker unresolved.
4. Can I now try a different path? Use this packet to close only the stability blocker, then keep external review and stable row materialization as the remaining gates.
