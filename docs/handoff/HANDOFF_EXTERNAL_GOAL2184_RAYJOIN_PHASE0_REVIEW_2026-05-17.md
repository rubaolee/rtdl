# External Review Handoff: Goal2184 RayJoin Phase 0/1 Evidence

Please perform an independent review of Goal2184's RayJoin phase-0/protocol/sample evidence.

## Files To Read

- `docs/reports/goal2184_rayjoin_full_reproduction_project_goal_2026-05-17.md`
- `docs/reports/goal2184_rayjoin_phase0_protocol_and_sample_evidence_2026-05-17.md`
- `docs/reports/goal2184_rayjoin_build_protocol_linux_raw_2026-05-17.txt`
- `docs/reports/goal2184_rtdl_same_rayjoin_sample_bounded_linux_2026-05-17.json`
- `tests/goal2184_rayjoin_full_reproduction_project_goal_test.py`
- `tests/goal2184_rayjoin_phase0_protocol_and_sample_evidence_test.py`

## Review Questions

1. Does the evidence actually complete the local source/protocol/sample portion of Goal2184?
2. Are the RayJoin build patches correctly framed as external comparison-checkout build compatibility patches, not RTDL engine changes?
3. Does the report accurately separate local GTX 1070 smoke/build evidence from future RTX pod paper-scale performance evidence?
4. Does the RTDL same-RayJoin-sample artifact support the bounded PIP/LSI/overlay parity claims in the report?
5. Are the claim boundaries strict enough: no RayJoin paper reproduction claim, no RTDL-beats-RayJoin claim, no broad RT-core speedup claim, and no v2.0 release authorization?
6. Is the next required pod work clear enough to continue toward full RayJoin reproduction?

## Expected Output

Write a review file under `docs/reviews/`:

- Gemini: `docs/reviews/goal2185_gemini_review_goal2184_rayjoin_phase0_2026-05-17.md`
- Claude: `docs/reviews/goal2186_claude_review_goal2184_rayjoin_phase0_2026-05-17.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This review must not authorize public RayJoin paper-reproduction or performance claims. At most, it may accept the local source/protocol/sample evidence and authorize the next RTX pod phase.
