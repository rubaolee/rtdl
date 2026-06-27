# Call For Review: Phoenix V3 M37 Component-Union Core Node

Date: 2026-06-23

Status: `request_m37_component_union_core_node_review_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Review Request

Please critically review M37 as a Phoenix V3 runtime-trunk step, not as a
release packet.

M37 claims only:

1. `run_radius_graph_component_union_3d_prepared_session` is a generic
   runner-callable component-union core node.
2. It separates component-union accounting from component-signature accounting.
3. It fails closed if signature output is treated as union output.
4. The current prepared-session surface ledger has 13 helpers, with 9 Step-4
   ready by local audit, 1 blocked Set-A seed, and 3 blocked Set-B controls.
5. The real grouped-vector adapter metadata path preserves `row_count` and
   `group_count`, addressing the M36 carry-forward before any focused
   grouped-reduction POD evidence.

M37 does not claim material speedup, release readiness, all-app authorization,
true zero-copy, V4 embedding, automatic partner selection, or broad V3-over-V2
performance.

## Files To Review

- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/__init__.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_m37_adapter_metadata_contract_test.py`
- `scripts/v3_phoenix_prepared_session_surface_ledger_gate.py`
- `tests/v3_phoenix_prepared_session_surface_ledger_gate_test.py`
- `docs/reports/phoenix_v3_m37_prepared_session_step4_surface_ledger_2026-06-23.md`
- `docs/reports/phoenix_v3_m37_component_union_core_node_and_adapter_metadata_gate_2026-06-23.md`

## Specific Questions

1. Does M37 correctly split component-union accounting from
   component-signature accounting?
2. Is `runtime_trunk_executes_end_to_end` fail-closed enough, especially for
   signature-output confusion, missing union phase accounting, residency, and
   hot-path host materialization?
3. Is the helper generic RTRDL runtime work, or does it leak RTDBSCAN/app
   semantics?
4. Does the top-level export repair matter for user-facing V3 surface quality?
5. Does the M36 adapter metadata gate adequately close the carry-forward
   concern before focused grouped-reduction POD evidence?
6. Are any non-authorization boundaries accidentally weakened?
7. What should be the next step after M37 if accepted?

## Acceptable Verdict Labels

Use exactly one:

- `accept_m37_component_union_core_node_continue`
- `accept_with_amendments`
- `blocked_needs_code_or_ledger_changes`
- `reject_wrong_boundary_or_app_specific`

If you choose an amendment/block/reject label, list exact required changes.

## Explicit Non-Authorization Block

No matter the verdict, this review must not authorize V3 release, all-app POD
spend, public speedup wording, broad V3-over-V2.x wording, true-zero-copy
wording, automatic partner selection, V4 work, C ABI work, or embedding work.
