# 3-AI Consensus: Goal 1427 v1.5.1 COLLECT_K_BOUNDED Python I64 Adapter Route

## Verdict

Codex, Claude, and Gemini agree that Goal 1427 is acceptable as an
adapter-routing step.

The existing Embree and OptiX polygon-pair bounded collection wrappers now route
native candidate rows through:

- `adapt_native_i64_rows_to_collect_k_bounded_result(...)`

## Consensus Basis

Codex implemented and validated the adapter route.

Claude review:

- `docs/reports/claude_goal1427_v1_5_1_collect_k_python_i64_adapter_route_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Gemini review:

- `docs/reports/gemini_goal1427_v1_5_1_collect_k_python_i64_adapter_route_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Implementation report:

- `docs/reports/goal1427_v1_5_1_collect_k_python_i64_adapter_route_2026-05-06.md`

External review request:

- `docs/handoff/goal1427_external_review_request_2026-05-06.md`

## Accepted Scope

The accepted behavior is:

- native polygon-pair candidate rows route through a named generic i64 adapter
- the adapter uses the app-generic `COLLECT_K_BOUNDED` row contract
- canonical `emitted_count` remains the generic post-dedup count
- raw native output count is preserved separately as `native_emitted_count`
- `binary_symbol_validation_present` remains `False`
- wrapper overflow policy follows the collect-k contract value

## Still Blocked

This consensus does not authorize stable promotion or public claims beyond the
adapter-routing step.

Still pending:

- prove existing polygon-pair parity is unchanged after the adapter route
- validate Embree/OptiX generic i64 symbols in built libraries
- add generic ABI parity tests against built native symbols
- rerun stable-promotion review
- speedup, zero-copy, whole-app, release, or broad workload wording

## Validation

Windows focused slice:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 26 tests` / `OK`.

Linux focused slice on `192.168.1.20` with the same working-tree files applied
over pushed `origin/main`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 26 tests` / `OK`.
