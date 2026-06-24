# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Prepared-Query Contract

Date: 2026-06-20

Status: accepted as prepared-query contract draft, not M7 promotion.

This is not V3 release authorization and not public speedup wording.

## Scope

Bounded goal:

```text
Turn the fresh grouped_reduction M7 pod evidence into a user-understandable
prepared-query contract that can support a later M7 public-row wording review
without misreading hot-query numbers as end-to-end or whole-app speedups.
```

Primary packet:

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

## External Review

External reviewer:

```text
Claude (claude-sonnet-4-6)
```

Initial review:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_prepared_query_contract_review_2026-06-20.md
verdict: approve-with-required-fixes
P0 issues: 0
P1 issues: 4
```

Re-review after fixes:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_prepared_query_contract_rereview_2026-06-20.md
verdict: approved
P0 issues: 0
P1 issues: 0
2ai_consensus_authorized: true
```

Claude's recommended next action:

```text
Advance sum rows (262144/sum and 524288/sum) to M7 candidate wording review;
keep count rows as internal evidence only; no additional pod run required.
```

## Required Fixes Applied

The four Claude P1 fixes are applied before this consensus:

1. User-facing contract language now uses external-user terms: fixed-schema
   table, row count, group-key count, integer value column, query/filter shape,
   one output row per group key, and CPU reference.
2. Repeat-scenario values are explicitly marked as formula projections from
   measured cold prepare plus measured hot-query median, not independently
   measured multi-query loops.
3. Each candidate row now carries a repeat profile for 1, 2, 5, 10, 25, 50,
   and 100 repeats, plus a repeat-profile basis field.
4. Count rows no longer receive a recommended public repeat count; both count
   rows carry `count_mode_high_breakeven_blocks_public_claim`.

An additional non-blocking test gap from the re-review was fixed by asserting
the high-break-even blocker on both count rows.

## Contract State Accepted

The contract is accepted only as:

```text
prepared_query_contract_draft_not_release
```

Current flags remain:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

Accepted facts:

- grouped_reduction has a reviewed user contract for a fixed-schema prepared
  repeated-query workload;
- the contract discloses cold/setup cost, hot-query timing, break-even repeat
  count, and modeled repeat profiles;
- sum rows are valid next candidates for M7 wording review;
- count rows remain internal because they require 14 repeats to break even;
- no public claim can quote repeat 100 without saying it is modeled from the
  measured hot-query median;
- no whole-app or whole-database speedup wording is authorized.

## Verification

Focused tests after P1 fixes:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_prepared_query_contract_test tests.v3_release_wording_gate_test
8 tests OK
```

Release wording gate after P1 fixes:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
missing_required_strings: []
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

The final full `v3_rebuild` matrix must still be run after this consensus is
linked from current V3 docs.

## Consensus Decision

Codex accepts Claude's re-review and the required fixes as complete.

This contract closes the immediate prepared-query contract blocker for
grouped_reduction, but it does not promote any row to M7. The next bounded
Phoenix step is a sum-only M7 candidate wording packet for
`262144/sum` and `524288/sum`. That packet must keep count rows internal and
must decide whether modeled repeat 100 wording is acceptable for user-facing
docs.

## Goal-Level Decision Audit

Decision: accept the corrected grouped_reduction prepared-query contract as a
reviewed draft, not as M7 promotion.

1. Was I foolish?

   No. The decision uses Claude's P1 findings to prevent hot-query and modeled
   repeat-100 numbers from becoming misleading public wording.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to publish the repeat-100 speedups
   without disclosing that they are formula projections, or to promote count
   rows despite a 14-repeat break-even.

3. Was there another path?

   Yes. I could have moved to another candidate immediately after the pod run.
   That would have left the strongest reusable grouped_reduction evidence
   without a user contract.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is narrow: write a sum-only M7 candidate wording packet,
   keep count rows internal, and require final external review before any
   tutorial or public performance wording changes.
