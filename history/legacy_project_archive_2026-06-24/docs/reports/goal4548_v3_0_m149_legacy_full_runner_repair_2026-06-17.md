# Goal4548 / V3 M149 Legacy Full Runner Repair

Status: `legacy_full_runner_repaired`

## Conclusion

Goal4548 repairs the legacy canonical `run_test_matrix.py --group full` path. Goal15 native comparison now resolves archived source files, uses a private compatibility shim for old `rtdl_embree_run_lsi/pip` app symbols, and prefers the local `librtdl_embree` build artifact instead of recompiling the whole native API into each smoke exe.

## Suite

- Group: `full`
- Module count: `41`
- Suite ok: `True`
- Command: `C:\Python311\python.exe -m unittest tests.baseline_contracts_test tests.dsl_negative_test tests.goal10_workloads_test tests.goal15_compare_test tests.goal17_prepared_runtime_test tests.goal18_result_mode_test tests.goal19_compare_test tests.goal22_reproduction_test tests.goal23_reproduction_test tests.goal28b_staging_test tests.goal28c_conversion_test tests.goal28d_execution_test tests.goal30_precision_abi_test tests.goal31_lsi_gap_closure_test tests.goal32_lsi_sort_sweep_test tests.goal36_performance_test tests.goal40_native_oracle_test tests.paper_reproduction_test tests.report_smoke_test tests.rtdsl_language_test tests.rtdsl_py_test tests.rtdsl_ray_query_test tests.rtdsl_simulator_test tests.section_5_6_scalability_test tests.test_core_quality tests.baseline_integration_test tests.cpu_embree_parity_test tests.evaluation_test tests.goal44_optix_benchmark_test tests.optix_embree_interop_test tests.rtdsl_embree_test tests.rtdsl_vulkan_test tests.goal34_performance_test tests.goal35_blockgroup_waterbodies_test tests.goal37_lkau_pkau_test tests.goal38_feasibility_test tests.goal43_optix_validation_test tests.goal45_optix_county_zipcode_test tests.goal47_optix_goal41_large_checks_test tests.goal50_postgis_ground_truth_test tests.goal54_lkau_pkau_four_system_test`

## Checks

| Check | Passed |
| --- | --- |
| `archive_lsi_source_resolves` | `True` |
| `archive_pip_source_resolves` | `True` |
| `legacy_shim_maps_lsi_symbol` | `True` |
| `legacy_shim_maps_pip_symbol` | `True` |
| `local_embree_library_preferred` | `True` |
| `resolver_test_added` | `True` |
| `full_runner_ok` | `True` |
| `full_runner_module_count_41` | `True` |
| `full_runner_reports_296_tests` | `True` |

## Boundary

- This repairs a test runner and native-compare smoke path.
- It does not add legacy `rtdl_embree_run_lsi/pip` symbols back to the public native ABI.
- It does not authorize benchmark or performance claims.
