# Goal 1428 External Review Request

Please independently review Goal 1428 for RTDL v1.5.1.

## Scope

Goal 1428 reruns polygon-pair parity after Goal 1427 routed candidate rows
through the Python generic i64 adapter.

Current intended status:

- Windows optional parity: accepted
- Linux required-Embree parity: accepted
- Linux required-OptiX parity: not accepted because `librtdl_optix` is missing
- old NVIDIA pod endpoint: unreachable, returned `Connection refused`
- stable promotion, speedup, zero-copy, whole-app, release, and built generic
  i64 symbol validation remain blocked

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `tests/goal1428_v1_5_1_collect_k_adapter_parity_rerun_test.py`
- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_rerun_2026-05-06.md`
- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.md`
- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.md`
- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.md`

## Validation Already Run

Windows focused slice:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 29 tests` / `OK`.

Linux focused slice on `192.168.1.20` with the same working-tree files applied
over pushed `origin/main`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 29 tests` / `OK`.

## Review Questions

Please answer:

1. Does the contract/report correctly say Embree post-adapter parity is
   accepted while OptiX post-adapter parity remains pending?
2. Does the report isolate the exact OptiX blocker without speculation?
3. Does the report avoid overclaiming stable promotion, speedup, zero-copy,
   built generic symbol validation, whole-app claims, or release action?
4. Are there any blocking issues before committing this partial parity rerun
   state?
