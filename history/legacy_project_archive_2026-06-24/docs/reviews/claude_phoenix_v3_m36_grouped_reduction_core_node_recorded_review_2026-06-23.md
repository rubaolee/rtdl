# Recorded External Review: Claude Phoenix V3 M36 Grouped-Reduction Core Node

Date: 2026-06-23

Reviewer: Claude

Status: `external_verdict_obtained_claude_accept_m36_grouped_reduction_core_node_continue_not_release`

Raw capture:

- `docs/reviews/claude_phoenix_v3_m36_grouped_reduction_core_node_review_2026-06-23.raw.md`
- stderr: `scratch/claude_phoenix_v3_m36_grouped_reduction_core_node_review_2026-06-23.err.txt`
- runner log: `scratch/claude_phoenix_v3_m36_grouped_reduction_core_node_review_2026-06-23.log`

## Verdict

```text
verdict: accept_m36_grouped_reduction_core_node_continue
release_authorized: false
all_app_pod_spend_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
v4_work_authorized: false
c_abi_work_authorized: false
embedding_work_authorized: false
true_zero_copy_wording_authorized: false
automatic_partner_selection_authorized: false
app_specific_native_engine_logic_authorized: false
```

## Accepted Findings

- `run_grouped_vector_sum_2d_prepared_session` is app-agnostic and generic.
- The explicit partner boundary is correct: no automatic partner selection.
- Step-3 and Step-4 audit fields are strict enough to prevent weak output
  metadata from becoming trunk success.
- The M36 surface ledger is correct at 12 public helpers: eight Step-4-ready
  local-audit families, one blocked Set-A seed, and three blocked Set-B
  controls.
- M36 stays inside V3 and avoids V4/C ABI/embedding/true external zero-copy
  territory.

## Findings

Blocking findings: none.

Required amendments: none.

Non-blocking observation: focused evidence collection must verify that the real
`run_grouped_vector_sum_2d_partner_columns_session` adapter reports both
`row_count` and `group_count`. If either is missing, the new helper correctly
fails closed by setting `output_counts_match_requested=false` and refusing
runtime-trunk success.

## Goal-Level Decision Audit

Decision: accept Claude's M36 external review and keep M36 as local contract
work only.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be treating the accepted core-node shape as
   performance evidence or all-app authorization.

3. Was there another path?

   Yes. Demote M36 pending more tests, but Claude found no blocking defect and
   the current tests/gate already fail closed on weak metadata.

4. Can I now try a different path that actually solves the problem?

   Yes. Preserve M36 as accepted contract work, then move to the next bounded
   step: either verify real adapter metadata for focused grouped-reduction
   evidence, or start M37 component-union accounting as planned.

## Non-Authorization

This review and this record authorize no V3 release, no all-app POD spend, no
public speedup claims, no broad V3-over-V2.x claims, no true-zero-copy wording,
no automatic partner selection, no V4 work, no C ABI work, and no embedding
work.
