# Claude Review Record: Phoenix V3 M37 Component-Union Core Node

Date: 2026-06-23

Raw review:
`docs/reviews/claude_phoenix_v3_m37_component_union_core_node_review_2026-06-23.raw.md`

Prompt:
`docs/reviews/call_for_review_phoenix_v3_m37_component_union_core_node_2026-06-23.md`

Execution log:
`scratch/claude_phoenix_v3_m37_component_union_core_node_review_2026-06-23.log`

Status: `external_review_obtained_claude_accept_m37_component_union_core_node_continue`

Verdict: `accept_m37_component_union_core_node_continue`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Review Summary

Claude accepted M37 as a runtime-trunk step only. The review found that:

- component-union and component-signature accounting are cleanly split;
- the helper is generic RTRDL runtime work and does not leak RTDBSCAN/app
  semantics;
- `runtime_trunk_executes_end_to_end` fails closed for the named failure modes:
  signature-output confusion, missing union phase accounting, residency loss,
  and hot-path host materialization;
- the top-level `rtdsl` export repair matters and is now gate-enforced;
- the M36 grouped-vector adapter metadata carry-forward is adequately closed
  for the local contract level;
- non-authorization boundaries are not weakened.

## Non-Blocking Follow-Ups

Claude requested two non-blocking checks before the next milestone:

1. Confirm the `min_neighbors >= 1` union-helper requirement versus the
   signature helper's legacy `>= 0` allowance.
2. Consider tightening `component_label_pass_accounted` so it verifies an
   actual `component_labels` output column, not only a policy string.

## Codex Response To Follow-Ups

Follow-up 1:

The union-helper `min_neighbors >= 1` requirement is intentional for M37 because
the real union adapter path
`PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D.run` also requires
`min_neighbors` to be at least 1. M37 follows the concrete union adapter
contract. The signature helper's older `>= 0` front-door allowance remains a
separate legacy asymmetry to revisit only if a future milestone changes the
signature helper contract.

Follow-up 2:

Applied before M37 closure. `run_radius_graph_component_union_3d_prepared_session`
now sets `component_label_columns_present` and requires both a
`component_label_policy` and an actual `component_labels` output column before
`component_label_pass_accounted` can be true. Focused tests and full
`v3_rebuild` were rerun after this change.

## Validation After Claude Follow-Up

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_m37_component_union_core_node_gate_test \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test
Ran 45 tests in 0.309s
OK

PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 117
Ran 608 tests in 74.624s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stderr.txt
```

## Other External Tool Attempts

Gemini was attempted once as a bounded fallback while Claude was still running.
It returned `IneligibleTierError` / `UNSUPPORTED_CLIENT`; raw stdout/stderr:

- `docs/reviews/gemini_phoenix_v3_m37_component_union_core_node_review_2026-06-23.raw.md`
- `scratch/gemini_phoenix_v3_m37_component_union_core_node_review_2026-06-23.err.txt`

Antigravity AgentAPI was checked once and returned
`ANTIGRAVITY_LS_ADDRESS is not set`; logs:

- `scratch/antigravity_m37_help.stdout.txt`
- `scratch/antigravity_m37_help.err.txt`

Neither Gemini nor Antigravity is counted as consensus for M37.

## Non-Authorization

This recorded review authorizes no V3 release, no all-app POD spend, no public
speedup claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no
automatic partner selection, no V4 work, no C ABI work, and no embedding work.
