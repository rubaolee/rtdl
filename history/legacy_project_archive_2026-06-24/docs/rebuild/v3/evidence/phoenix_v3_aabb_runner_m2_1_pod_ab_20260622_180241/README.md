# Phoenix V3 AABB Prepare-Reuse POD Evidence

Status: `aabb_prepare_reuse_pod_evidence_pending_2ai_not_m7`.

This is a generic `aabb_index_query_2d` prepared-session evidence packet.
Contact Manifold is only the harness that supplies AABB rows and a CPU oracle.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
```

## Parameters

- `dataset`: `jittered_grid`
- `grid_count`: `32768`
- `indexed_aabb_count`: `32768`
- `query_aabb_count`: `32768`
- `resolution`: `None`
- `witness_capacity`: `32768`
- `discovery_row_capacity`: `65536`
- `warmup`: `3`
- `repeat`: `50`
- `backends`: `['embree', 'optix']`

## Phase Rows

### embree

- Prepare: `0.423815832` sec
- Query median: `0.307346899` sec
- Query total: `15.479086533` sec
- Collect-k: `0.083268881` sec
- Broadphase wall: `23.321652398` sec
- Cold-plus-collect wall: `23.404921278` sec

### optix

- Prepare: `0.605639882` sec
- Query median: `0.160014741` sec
- Query total: `8.906914480` sec
- Collect-k: `0.088071145` sec
- Broadphase wall: `17.300975583` sec
- Cold-plus-collect wall: `17.389046729` sec

## Comparisons

- `optix_over_embree_prepare_speedup`: `0.700x`
- `optix_over_embree_query_median_speedup`: `1.921x`
- `optix_over_embree_query_total_speedup`: `1.738x`
- `optix_over_embree_collect_speedup`: `0.945x`
- `optix_over_embree_broadphase_wall_speedup`: `1.348x`
- `optix_over_embree_cold_plus_collect_wall_speedup`: `1.346x`
- `optix_over_embree_runner_wall_speedup`: `1.337x`

## Checks

- `runner_completed_without_backend_errors`: `true`
- `serious_fixture_scale`: `true`
- `has_32768_indexed_aabbs`: `true`
- `has_32768_query_aabbs`: `true`
- `prepare_once_query_many_requested`: `true`
- `embree_and_optix_present`: `true`
- `all_payloads_match_cpu_reference`: `true`
- `all_payloads_complete_candidate_coverage`: `true`
- `all_payloads_observed_reuse`: `true`
- `productized_runner_visible_for_prepared_backends`: `true`
- `phase_table_has_prepare_query_collect_wall`: `true`
- `optix_rt_hardware_gate_passed_if_required`: `true`
- `material_optix_wall_win_after_prepare_reuse`: `true`

## Goal-Level Decision Audit

Decision: Run or stage serious AABB prepare-reuse POD evidence through a reusable runner instead of ad hoc app timing.

1. Was I foolish?
   No. The runner keeps the candidate generic and preserves release flags false.
2. If yes, what actions made the decision foolish?
   It would be foolish to quote hot-query-only speedups, to use sub-32768 toy fixtures as release evidence, or to treat contact-specific wording as a V3 engine result.
3. Was there another path that would have avoided getting stuck on that idea?
   Continue optimizing Contact Manifold directly. That could improve one app but would not prove the reusable AABB prepared-session contract.
4. Can I now try a different path that actually solves the problem?
   Use the same runner on an RTX pod, require material cold-plus-repeat wall win, then send the packet for 2-AI review before any M7 promotion.
