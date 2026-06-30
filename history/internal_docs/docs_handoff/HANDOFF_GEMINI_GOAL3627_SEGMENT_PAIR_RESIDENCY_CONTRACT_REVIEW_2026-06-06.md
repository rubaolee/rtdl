# Handoff: Gemini Review For Goal3627 Segment-Pair Typed Output Residency Contract

Please review Goal3627.

Read:

1. `docs/reports/goal3627_segment_pair_typed_output_residency_contract_2026-06-06.md`
2. `src/rtdsl/segment_pair_contracts.py`, especially `segment_pair_left_id_dense_count_output_residency_contract`
3. `tests/goal3627_segment_pair_typed_output_residency_contract_test.py`
4. `docs/reports/goal3625_segment_pair_intersection_contract_foundation_2026-06-06.md` for predicate-contract context

Context:

- Goal3625 made the segment-pair predicate contract executable and Gemini accepted that foundation.
- Goal3627 makes the next device-residency target concrete for the same primitive: dense left-id count output plus overflow and ambiguity/status columns.
- The implementation intentionally reuses `RtdlPrimitivePayloadColumnDescriptor` and neutral-buffer seam metadata instead of inventing a second residency seam.
- Claude is quota-blocked, so this is Gemini-only review and must not be represented as 3-AI consensus.

Please verify:

1. The residency contract remains app-agnostic and does not encode RayJoin semantics.
2. The helper reuses existing primitive payload/neutral-seam machinery rather than inventing conflicting authority.
3. Device-resident fake-pointer descriptors are honestly marked as borrowed/unmeasured and do not authorize true zero-copy.
4. Host-reference fallback is explicit when device pointers are absent.
5. The ambiguity/status column is the right contract hook for future fast-path fallback decisions.
6. The report and tests do not authorize release, public speedup wording, broad RT-core speedup, true zero-copy, automatic partner selection, or paper reproduction.

Use one verdict only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Save the review to:

`docs/reviews/goal3628_gemini_review_goal3627_segment_pair_residency_contract_2026-06-06.md`
