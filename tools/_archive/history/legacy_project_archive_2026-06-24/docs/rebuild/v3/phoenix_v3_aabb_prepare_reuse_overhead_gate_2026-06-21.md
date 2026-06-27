# Phoenix V3 AABB Prepare-Reuse Overhead Gate

Status: `aabb_prepare_reuse_overhead_gate_blocked_not_m7`

AABB prepare-reuse is a useful V3 engine target, but the current evidence is blocked. The 32,768 row was only 1.140x cold-plus-collect wall versus Embree, below the 1.20 material floor; the 65,536 rerun fell to 1.087x. OptiX prepare is slower on both rows, query-total wins are not valid public claims without wall clearance, and collect is neutral or slower. This is not a V3 performance win yet.

## Verdict

- M7 candidate reopen authorized: `false`
- M7 promotion authorized: `false`
- Release authorized: `false`
- Public speedup claim authorized: `false`
- Material wall-speedup floor: `1.200x`

## Observed Ratios

| AABBs | Repeat | Prepare | Query total | Collect | Cold+collect wall | Runner wall |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32768 | 50 | 0.624x | 1.178x | 1.005x | 1.140x | 1.137x |
| 65536 | 50 | 0.742x | 1.109x | 0.906x | 1.087x | 1.084x |

## Blocker Summary

- Best cold+collect wall speedup: `1.140x`
- Latest cold+collect wall speedup: `1.087x`
- Best query-total speedup: `1.178x`
- Best prepare speedup: `0.742x`
- Best collect speedup: `1.005x`

## Required Blockers Before M7

- `optix_prepare_slower_than_embree`
- `material_wall_floor_not_met`
- `larger_scale_not_better`
- `query_only_claim_forbidden`
- `collect_not_material_win`
- `external_m7_review_missing_for_new_row`
- `generic_overhead_reduction_required`
- `same_contract_public_wording_review_missing`

## Next Engine Action

Do generic AABB overhead work before any new M7 attempt: reduce OptiX prepare cost, reduce repeated query overhead, improve collect/compaction cost, or propose a separately justified prepared-session contract that clears the wall floor without contact-specific native logic.

## Forbidden Shortcuts

- Do not promote AABB prepare-reuse to M7 from 1.140x or 1.087x wall evidence.
- Do not quote query-total speedup as a V3 win while cold-plus-collect wall is below 1.20x.
- Do not keep scale-shopping this contract without a new reviewer-approved rationale.
- Do not claim full contact solving, broad AABB-index acceleration, or broad V3-over-V2 speedup.

## Checks

- `serious_evidence_exists`: `true`
- `scale_evidence_exists`: `true`
- `serious_evidence_not_m7`: `true`
- `scale_evidence_not_m7`: `true`
- `rows_cover_32768_and_65536`: `true`
- `all_wall_speedups_below_material_floor`: `true`
- `larger_scale_not_better`: `true`
- `optix_prepare_slower_on_all_rows`: `true`
- `query_total_positive_but_not_promotable`: `true`
- `collect_is_not_material_win`: `true`
- `scale_shopping_already_blocked`: `true`
- `claim_flags_false`: `true`

Failed checks: `[]`

## Goal-Level Decision Audit

Decision: Add a hard overhead gate for AABB prepare-reuse instead of treating sub-floor ratios as V3 progress.

1. Was I foolish?
   No. This gate prevents a low-margin 1.140x row and a worse 1.087x scale row from being mistaken for a major V3 optimization.
2. If yes, what actions made the decision foolish?
   The foolish action would be to promote query-only wins, keep increasing scale until a ratio looks good, or call this full contact/AABB acceleration.
3. Was there another path that would have avoided getting stuck on that idea?
   I could have moved straight to code tuning. That might be useful, but without this gate the current evidence would remain easy to misread.
4. Can I now try a different path that actually solves the problem?
   Use the gate as the work order for real generic overhead reduction: prepare, query, and collect/compaction must improve before AABB can reopen M7.
