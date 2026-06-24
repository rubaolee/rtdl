# Phoenix V3 AABB Query-Cache Evidence

Status: `aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met`

The prepared-query record cache is real and generic: both serious rows show one range-intersection cache entry with one miss and 52 hits per backend. However, the material wall result still fails the V3 floor. The 32,768-row cold-plus-collect wall ratio is below 1.20x, and the 65,536-row ratio is lower again. This is a correct engine cleanup, not a V3 performance promotion.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Observed Rows

| AABBs | Repeat | Cache hits | Prepare | Query total | Collect | Cold+collect wall | Runner wall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32768 | 50 | 52 | 0.577x | 1.238x | 0.936x | 1.188x | 1.181x |
| 65536 | 50 | 52 | 0.803x | 1.161x | 0.878x | 1.135x | 1.129x |

## Blocker Summary

- Material wall-speedup floor: `1.200x`
- Best cold+collect wall speedup: `1.188x`
- Largest-row cold+collect wall speedup: `1.135x`
- Best query-total speedup: `1.238x`
- Cache observed: `true`

## Next Engine Action

Keep AABB prepare-reuse in the open generic-engine queue. The next useful work is below Python query-record reuse: cache or reuse native packed query buffers, reduce OptiX prepare cost, and reduce row-output collect/compaction overhead. Do not run more scale-only AABB attempts without a new contract rationale.

## Forbidden Shortcuts

- Do not promote AABB prepare-reuse to M7 from these cache-hit rows.
- Do not quote query-total speedup as a V3 win while cold-plus-collect wall is below 1.20x.
- Do not treat contact_manifold as the optimized product; it is only the evidence harness.
- Do not claim full contact solving, broad AABB acceleration, or broad V3-over-V2 speedup.
- Do not keep scale-shopping this contract without a new reviewed rationale.

## Checks

- `summaries_exist`: `true`
- `rows_are_32768_and_65536`: `true`
- `all_runner_completed`: `true`
- `all_backend_errors_empty`: `true`
- `all_have_embree_and_optix`: `true`
- `all_cpu_reference_match`: `true`
- `all_complete_candidate_coverage`: `true`
- `all_cache_stats_observed`: `true`
- `all_query_total_positive`: `true`
- `all_wall_below_material_floor`: `true`
- `larger_scale_not_better`: `true`
- `optix_prepare_slower_on_all_rows`: `true`
- `collect_not_material_win`: `true`
- `hardware_gate_pass`: `true`
- `claim_flags_false`: `true`

Failed checks: `[]`

## Goal-Level Decision Audit

Decision: Record the AABB prepared-query record cache as a correct generic cleanup but not as a V3 M7 performance row.

1. Was I foolish?
   No. The packet accepts the cache evidence but refuses to turn sub-floor wall speedups into a release claim.
2. If yes, what actions made the decision foolish?
   The foolish action would be to celebrate 1.188x as close enough, or quote query-total speedup while hiding prepare and collect costs.
3. Was there another path that would have avoided getting stuck on that idea?
   I could keep trying larger AABB sizes. The 65,536 row already got worse, so that would be scale-shopping rather than solving the engine bottleneck.
4. Can I now try a different path that actually solves the problem?
   Move the AABB route to deeper generic overhead work: native packed query buffer reuse, prepare-cost reduction, and collect/compaction improvement.
