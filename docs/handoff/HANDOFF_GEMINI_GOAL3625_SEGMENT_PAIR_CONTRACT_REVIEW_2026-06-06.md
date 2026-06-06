# Handoff: Gemini Review For Goal3625 Segment-Pair Contract Foundation

Please review the Goal3625 work.

Read:

1. `docs/reports/goal3625_segment_pair_intersection_contract_foundation_2026-06-06.md`
2. `src/rtdsl/segment_pair_contracts.py`
3. `src/rtdsl/primitive_hierarchy.py` around `rows.segment_pair_intersection_rows_2d`
4. `docs/rtdl_primitive_catalog.md` around `SEGMENT_PAIR_INTERSECTION_ROWS_2D`
5. `tests/goal3625_segment_pair_intersection_contract_foundation_test.py`

Context:

- Goal3618 recorded a policy candidate for segment-pair count semantics after the RayJoin LSI repair.
- Goal3625 turns that policy into executable, app-agnostic contract metadata and a discoverable candidate primitive node.
- Claude is quota-blocked until Jun 7, 7pm America/New_York, so this is a Gemini review only; do not claim 3-AI consensus.

Please verify:

1. The contract is app-agnostic and does not turn RayJoin into engine semantics.
2. The v0 predicate is honestly bounded: non-collinear, endpoint-inclusive, absolute denominator threshold, collinear excluded/ambiguous.
3. The adversarial fixture set is a valid first foundation, while still leaving enough future work before public promotion.
4. The primitive hierarchy and catalog expose this as `candidate_behavior`, not stable public primitive.
5. The report does not authorize release, public speedup wording, paper reproduction, broad RT-core speedup, true zero-copy, or automatic partner selection.

Use one verdict only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Save the review to:

`docs/reviews/goal3626_gemini_review_goal3625_segment_pair_contract_foundation_2026-06-06.md`
