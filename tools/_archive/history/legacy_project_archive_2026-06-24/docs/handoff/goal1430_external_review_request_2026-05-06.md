# Goal 1430 External Review Request

Please independently review Goal 1430 for RTDL v1.5.1.

## Scope

Goal 1430 validates the built generic `COLLECT_K_BOUNDED` i64 symbols in Embree
and OptiX libraries:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`

Current intended status:

- source symbols present
- Python adapter route present
- Embree and OptiX adapter parity accepted
- built Embree and OptiX generic i64 symbols present
- direct same-ABI smoke validation accepted
- stable promotion still blocked pending 3-AI stable-promotion review
- speedup, zero-copy, whole-app, broad workload, release, and release-tag claims
  remain blocked

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1424_v1_5_1_collect_k_native_app_generic_audit_test.py`
- `tests/goal1425_v1_5_1_collect_k_native_generic_abi_contract_test.py`
- `tests/goal1426_v1_5_1_collect_k_native_i64_source_test.py`
- `tests/goal1427_v1_5_1_collect_k_python_i64_adapter_route_test.py`
- `tests/goal1428_v1_5_1_collect_k_adapter_parity_rerun_test.py`
- `tests/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test.py`
- `tests/goal1430_v1_5_1_collect_k_generic_i64_binary_validation_test.py`
- `docs/reports/goal1430_v1_5_1_collect_k_generic_i64_binary_validation_2026-05-06.md`
- `docs/reports/goal1430_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt`

## Validation Already Run

Windows focused slice:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal1430_v1_5_1_collect_k_generic_i64_binary_validation_test tests.goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 36 tests` / `OK`.

Linux focused slice on `192.168.1.20` with the same working-tree files applied
over pushed `origin/main`:

```sh
PYTHONPATH=src:. python3 -m unittest tests.goal1430_v1_5_1_collect_k_generic_i64_binary_validation_test tests.goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_test tests.goal1428_v1_5_1_collect_k_adapter_parity_rerun_test tests.goal1427_v1_5_1_collect_k_python_i64_adapter_route_test tests.goal1426_v1_5_1_collect_k_native_i64_source_test tests.goal1425_v1_5_1_collect_k_native_generic_abi_contract_test tests.goal1424_v1_5_1_collect_k_native_app_generic_audit_test tests.goal1416_v1_5_1_collect_k_native_parity_test tests.goal1411_v1_5_1_polygon_collect_k_helper_bridge_test
```

Result: `Ran 36 tests` / `OK`.

## Direct Binary Evidence

Embree on `192.168.1.20`:

- `nm -D build/librtdl_embree.so` found `rtdl_embree_collect_k_bounded_i64`
- ctypes smoke success: canonical rows `[1, 10, 2, 20]`
- ctypes overflow smoke: `overflow=1`, no partial rows copied

OptiX on RTX A5000 pod `69.30.85.196:22030`:

- rebuilt `build/librtdl_optix.so` at git HEAD `217bd991a1a6cefdd581e4faf43d80192c7dae94`
- `nm -D build/librtdl_optix.so` found `rtdl_optix_collect_k_bounded_i64`
- ctypes smoke success: canonical rows `[1, 10, 2, 20]`
- ctypes overflow smoke: `overflow=1`, no partial rows copied

## Review Questions

Please answer:

1. Does the evidence support marking native generic i64 binary validation present?
2. Does the contract/report keep production-wrapper direct use and stable
   promotion review as pending where appropriate?
3. Does the report avoid overclaiming speedup, zero-copy, whole-app behavior,
   broad workload coverage, release action, or stable primitive wording?
4. Are there any blocking issues before committing Goal 1430?
