# Handoff: Gemini Review For Goal3629 Segment-Pair Dense Count Oracle

Please review Goal3629.

Read:

1. `docs/reports/goal3629_segment_pair_dense_count_reference_oracle_2026-06-06.md`
2. `src/rtdsl/segment_pair_contracts.py`, especially `segment_pair_left_id_dense_counts_reference`
3. `tests/goal3629_segment_pair_dense_count_reference_oracle_test.py`

Context:

- Goal3625 created the strict-v0 segment-pair predicate contract.
- Goal3627 created the typed output residency target.
- Goal3629 adds a Python same-contract dense left-id count oracle for future CuPy/OptiX conformance.
- Claude is quota-blocked, so this is Gemini-only review and must not be represented as 3-AI consensus.

Please verify:

1. The oracle uses the strict-v0 predicate instead of inventing a new LSI meaning.
2. Counts are keyed only by generic left segment index.
3. Ambiguous and rejected pair counts are separated for future fallback/conformance.
4. The oracle is clearly not a performance path and not public claim evidence.
5. The report/tests keep app-specific RayJoin semantics outside the engine.

Use one verdict only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Save the review to:

`docs/reviews/goal3630_gemini_review_goal3629_segment_pair_oracle_2026-06-06.md`
