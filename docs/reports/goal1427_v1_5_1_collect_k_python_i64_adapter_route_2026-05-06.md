# Goal 1427 v1.5.1 COLLECT_K_BOUNDED Python I64 Adapter Route

## Verdict

The Embree and OptiX polygon-pair bounded collection wrappers now route their
native candidate rows through a named Python generic i64 adapter:

- `adapt_native_i64_rows_to_collect_k_bounded_result(...)`

This is an adapter-routing step only. It does not claim built-library validation
of `rtdl_embree_collect_k_bounded_i64` or `rtdl_optix_collect_k_bounded_i64`,
does not authorize stable primitive promotion, and does not authorize speedup,
zero-copy, whole-app, or release wording.

## What Changed

- Added `adapt_native_i64_rows_to_collect_k_bounded_result(...)` to the v1.5.1
  collect-k contract module.
- Updated `collect_polygon_pair_candidates_bounded_embree(...)` to use the
  generic i64 adapter after native polygon-pair candidate discovery.
- Updated `collect_polygon_pair_candidates_bounded_optix(...)` to use the
  generic i64 adapter after native polygon-pair candidate discovery.
- Updated the native generic ABI contract status to
  `source_symbols_present_python_adapter_routed_binary_validation_pending`.
- Preserved canonical `emitted_count` metadata from the generic adapter and
  records raw native output count separately as `native_emitted_count`.
- Propagated `binary_symbol_validation_present: False` and the contract overflow
  policy through the wrapper result metadata.
- Kept native binary validation and stable promotion explicitly blocked.

## Still Pending

- prove existing polygon-pair parity is unchanged after this adapter route
- validate Embree/OptiX generic i64 symbols in built libraries
- add generic ABI parity tests against built native symbols
- rerun stable-promotion review before any stable wording

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
