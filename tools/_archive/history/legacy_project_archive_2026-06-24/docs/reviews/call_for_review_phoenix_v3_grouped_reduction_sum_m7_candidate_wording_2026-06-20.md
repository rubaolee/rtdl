# Call For Review: Phoenix V3 Grouped-Reduction Sum M7 Candidate Wording

Date: 2026-06-20

Reviewer requested: Claude

## Review Target

Please critically review the sum-only grouped_reduction M7 candidate wording
packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_sum_m7_candidate_wording.py
tests/v3_phoenix_grouped_reduction_sum_m7_candidate_wording_test.py
```

Prior contract closure:

```text
docs/reviews/codex_phoenix_v3_grouped_reduction_prepared_query_contract_2ai_consensus_2026-06-20.md
docs/reviews/claude_phoenix_v3_grouped_reduction_prepared_query_contract_rereview_2026-06-20.md
```

Fresh evidence lineage:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_pod_evidence_2ai_consensus_2026-06-20.md
```

## Current Claim State

The packet intentionally keeps:

```text
status: sum_only_m7_candidate_wording_not_release
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## Review Questions

1. Is the sum-only candidate wording understandable and safe for external users?
2. Does the wording disclose that repeat 100 is modeled from measured cold
   prepare plus measured hot-query median, not independently measured?
3. Is it acceptable to advance one or both sum rows to M7 qualification after
   this wording review, or should the rows remain candidate-only?
4. Are count rows clearly excluded and protected from accidental promotion?
5. Are there any P0/P1 defects in wording, math, lineage, or tests?

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_sum_m7_candidate_wording_review_2026-06-20.md
```

Verdict format requested:

```text
verdict: approve | approve-with-required-fixes | reject
P0 issues: N
P1 issues: N
2ai_consensus_authorized: true/false after listed fixes
m7_qualification_recommendation: promote none | promote 262144/sum | promote 524288/sum | promote both sum rows
recommended_next_action: ...
```
