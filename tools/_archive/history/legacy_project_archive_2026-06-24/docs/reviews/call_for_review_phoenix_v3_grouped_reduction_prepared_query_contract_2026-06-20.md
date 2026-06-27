# Call For Review: Phoenix V3 Grouped-Reduction Prepared-Query Contract

Date: 2026-06-20

Reviewer requested: Claude

## Review Target

Please critically review the Phoenix V3 grouped_reduction prepared-query
contract packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_prepared_query_contract_2026-06-20.json
scripts/v3_phoenix_grouped_reduction_prepared_query_contract.py
tests/v3_phoenix_grouped_reduction_prepared_query_contract_test.py
```

Evidence lineage:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620/m7_grouped_reduction_post_run_intake.json
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_pod_evidence_2ai_consensus_2026-06-20.md
```

## Current Claim State

The contract intentionally keeps:

```text
status: prepared_query_contract_draft_not_release
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## Review Questions

1. Does the contract correctly define a user-understandable prepared-query
   model for grouped_reduction, or does it still rely on project-internal
   assumptions?
2. Does it correctly distinguish hot prepared-query speedup from repeat-aware
   end-to-end timing and from whole-app/database timing?
3. Are the repeat 100 grouped_sum candidate rows reasonable M7 candidates for
   further review, or should they remain internal despite the strong numbers?
4. Are there any P0/P1 wording, math, lineage, or test defects that must be
   fixed before Codex consensus?
5. What exact next action should Phoenix take: promote a repeat-aware prepared
   grouped_sum row through final review, require another measured pod run, or
   move grouped_reduction back to internal-only?

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_prepared_query_contract_review_2026-06-20.md
```

Verdict format requested:

```text
verdict: approve | approve-with-required-fixes | reject
P0 issues: N
P1 issues: N
2ai_consensus_authorized: true/false after listed fixes
recommended_next_action: ...
```
