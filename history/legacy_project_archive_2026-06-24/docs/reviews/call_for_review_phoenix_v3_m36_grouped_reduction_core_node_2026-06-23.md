# Call For Review: Phoenix V3 M36 Grouped-Reduction Core Node

Date: 2026-06-23

Status: `request_m36_grouped_reduction_core_node_review_not_release`

Review targets:

- `docs/reports/phoenix_v3_m36_grouped_vector_sum_prepared_session_core_node_2026-06-23.md`
- `docs/reports/phoenix_v3_m36_prepared_session_step4_surface_ledger_2026-06-23.md`
- `src/rtdsl/prepared_execution.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py`
- `tests/v3_phoenix_prepared_session_surface_ledger_gate_test.py`

This asks whether M36 correctly promotes grouped reduction into a generic
runner-callable prepared-session core node without making release or performance
claims.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
```

## Questions

1. Is `run_grouped_vector_sum_2d_prepared_session` app-agnostic and generic?
2. Is the explicit partner boundary correct, with no automatic partner
   selection?
3. Are the Step-3 and Step-4 audit fields strict enough to prevent weak output
   metadata from becoming trunk success?
4. Is the M36 surface ledger correct at 12 public helpers: eight Step-4-ready
   local-audit families, one blocked Set-A seed, and three blocked Set-B
   controls?
5. Does M36 stay inside V3 and avoid V4/C ABI/embedding/true external
   zero-copy territory?
6. Does this review authorize release, all-app POD spend, public speedup
   wording, broad V3-over-V2 wording, or V4 work?

## Requested Verdict Labels

Choose exactly one:

- `accept_m36_grouped_reduction_core_node_continue`
- `accept_with_amendments`
- `blocked_needs_code_or_ledger_changes`
- `reject_wrong_boundary_or_app_specific`

Include blocking findings, required amendments if any, explicit answers to the
six questions, and an explicit non-authorization block.
