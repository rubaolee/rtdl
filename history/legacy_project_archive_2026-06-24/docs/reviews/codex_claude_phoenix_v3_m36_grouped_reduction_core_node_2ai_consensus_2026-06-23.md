# Codex + Claude Consensus: Phoenix V3 M36 Grouped-Reduction Core Node

Date: 2026-06-23

Status: `codex_claude_consensus_accept_m36_grouped_reduction_core_node_not_release`

## Inputs

- M36 report:
  `docs/reports/phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md`
- M36 surface ledger:
  `docs/reports/phoenix_v3_m36_prepared_session_step4_surface_ledger_2026-06-23.md`
- M36 call for review:
  `docs/reviews/call_for_review_phoenix_v3_m36_grouped_reduction_core_node_2026-06-23.md`
- Claude recorded review:
  `docs/reviews/claude_phoenix_v3_m36_grouped_reduction_core_node_recorded_review_2026-06-23.md`
- Raw Claude review:
  `docs/reviews/claude_phoenix_v3_m36_grouped_reduction_core_node_review_2026-06-23.raw.md`

## Consensus

Codex accepts Claude's verdict:

```text
accept_m36_grouped_reduction_core_node_continue
```

M36 is accepted as local V3 runtime-trunk contract work:

- `run_grouped_vector_sum_2d_prepared_session` is a generic runner-callable
  grouped-reduction helper.
- The helper requires explicit `partner="numba"`.
- Weak output metadata fails closed.
- The current surface ledger is 12 public helpers: eight Step-4-ready, one
  blocked Set-A seed, three blocked Set-B controls.

## Carry-Forward

Before focused grouped-reduction POD evidence, verify the real
`run_grouped_vector_sum_2d_partner_columns_session` adapter reports both
`row_count` and `group_count`. This is not a release blocker for M36, but it is
a precondition for any focused evidence run.

## Non-Authorization

```text
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

## Goal-Level Decision Audit

Decision: close M36 as accepted local core-node work and carry the real-adapter
metadata check into the next focused evidence step.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be using M36 consensus as proof of performance.

3. Was there another path?

   Yes. Start M37 immediately. The better near-term path is to record M36 and
   preserve the adapter-metadata precondition before any grouped-reduction
   focused evidence.

4. Can I now try a different path that actually solves the problem?

   Yes. Either run a bounded local metadata probe for the real adapter, then
   decide whether POD focused evidence is justified, or proceed to M37
   component-union accounting.
