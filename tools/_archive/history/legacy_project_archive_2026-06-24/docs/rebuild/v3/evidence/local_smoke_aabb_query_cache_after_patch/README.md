# Phoenix V3 AABB Prepare-Reuse POD Evidence

Status: `aabb_prepare_reuse_pod_evidence_collected_not_m7`.

This is a generic `aabb_index_query_2d` prepared-session evidence packet.
Contact Manifold is only the harness that supplies AABB rows and a CPU oracle.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
```

## Parameters

- `dataset`: `grid`
- `grid_count`: `3`
- `indexed_aabb_count`: `3`
- `query_aabb_count`: `3`
- `resolution`: `None`
- `witness_capacity`: `3`
- `discovery_row_capacity`: `8`
- `warmup`: `0`
- `repeat`: `1`
- `backends`: `['cpu']`

## Phase Rows

### cpu

- Prepare: `0.000198200` sec
- Query median: `0.000092400` sec
- Query total: `0.000092400` sec
- Collect-k: `0.000079000` sec
- Broadphase wall: `0.000359700` sec
- Cold-plus-collect wall: `0.000438700` sec

## Comparisons

- No Embree/OptiX comparison is available in this packet.

## Checks

- `runner_completed_without_backend_errors`: `true`
- `serious_fixture_scale`: `false`
- `has_32768_indexed_aabbs`: `false`
- `has_32768_query_aabbs`: `false`
- `prepare_once_query_many_requested`: `false`
- `embree_and_optix_present`: `false`
- `all_payloads_match_cpu_reference`: `true`
- `all_payloads_complete_candidate_coverage`: `true`
- `all_payloads_observed_reuse`: `false`
- `phase_table_has_prepare_query_collect_wall`: `true`
- `optix_rt_hardware_gate_passed_if_required`: `true`
- `material_optix_wall_win_after_prepare_reuse`: `false`

Failed checks:

- `serious_fixture_scale`
- `has_32768_indexed_aabbs`
- `has_32768_query_aabbs`
- `prepare_once_query_many_requested`
- `embree_and_optix_present`
- `all_payloads_observed_reuse`
- `material_optix_wall_win_after_prepare_reuse`

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
