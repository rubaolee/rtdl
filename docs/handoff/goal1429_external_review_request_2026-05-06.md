# Goal 1429 External Review Request

Please independently review Goal 1429 for RTDL v1.5.1.

## Scope

Goal 1429 uses a newly provided RTX A5000 pod to close the pending OptiX
post-adapter parity blocker from Goal 1428.

Current intended status:

- Windows optional parity: accepted
- Linux required-Embree parity: accepted
- RTX A5000 pod required-OptiX parity: accepted
- adapter-routed polygon-pair parity is accepted for Embree and OptiX
- built generic i64 symbol validation remains pending
- generic ABI parity tests against built `rtdl_*_collect_k_bounded_i64` symbols
  remain pending
- stable promotion, speedup, zero-copy, whole-app, broad workload, and release
  wording remain blocked

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `tests/goal1428_v1_5_1_collect_k_adapter_parity_rerun_test.py`
- `tests/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test.py`
- `docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_2026-05-06.md`
- `docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md`
- `docs/reports/goal1429_v1_5_1_collect_k_pod_env_2026-05-06.json`
- `docs/reports/goal1429_v1_5_1_collect_k_build_optix_2026-05-06.txt`

## Validation Already Run

Windows focused slice:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 33 tests` / `OK`.

Linux focused slice on `192.168.1.20` with the same working-tree files applied
over pushed `origin/main`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 33 tests` / `OK`.

RTX A5000 pod required-OptiX parity:

```sh
PYTHONPATH=src:. python3 scripts/goal1416_v1_5_1_collect_k_native_parity.py --backend optix --require-backend optix --json-out docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.json --markdown-out docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md
```

Result: accepted; `optix: pass=4, fail=0, skipped=0`.

## Review Questions

Please answer:

1. Does the evidence support closing the OptiX post-adapter parity blocker?
2. Does the contract/report correctly keep built generic i64 symbol validation
   and generic ABI parity tests pending?
3. Does the report avoid overclaiming stable promotion, speedup, zero-copy,
   whole-app behavior, broad workload coverage, or release action?
4. Are there any blocking issues before committing this Goal 1429 closure state?
