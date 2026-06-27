# Goal 1427 External Review Request

Please independently review Goal 1427 for RTDL v1.5.1.

## Scope

Goal 1427 routes existing Embree/OptiX polygon-pair bounded collection wrappers
through a named Python generic i64 adapter:

- `adapt_native_i64_rows_to_collect_k_bounded_result(...)`

This adapter canonicalizes native candidate rows through the app-generic
`COLLECT_K_BOUNDED` row contract while built native generic i64 symbol
validation remains pending.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `tests/goal1427_v1_5_1_collect_k_python_i64_adapter_route_test.py`
- `docs/reports/goal1427_v1_5_1_collect_k_python_i64_adapter_route_2026-05-06.md`

## Validation Already Run

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

## Known Boundaries

This is an adapter-routing step only.

It does not claim:

- built-library validation of `rtdl_embree_collect_k_bounded_i64`
- built-library validation of `rtdl_optix_collect_k_bounded_i64`
- stable primitive promotion
- public speedup wording
- zero-copy wording
- whole-app claims
- release action

## Review Questions

Please answer:

1. Does the adapter preserve the generic `COLLECT_K_BOUNDED` fail-closed,
   canonical row semantics?
2. Do the Embree/OptiX wrappers now route polygon-pair candidate rows through
   the named generic adapter without claiming built native generic symbols?
3. Does the report avoid overclaiming stable promotion, speedup, zero-copy, or
   built-library validation?
4. Are there any blocking issues before committing this adapter-routing step?
