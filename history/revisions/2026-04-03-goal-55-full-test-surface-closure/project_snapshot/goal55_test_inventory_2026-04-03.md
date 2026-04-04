# Goal 55 Test Inventory

Date: 2026-04-03

## Current Full-Suite Baseline

Command:

- `python3 -m unittest discover -s tests -p '*test.py'`

Observed result:

- `179` tests
- `1` skip
- `OK`

## Current Classification

This classification is a working Goal 55 audit taxonomy, not a claim that every
file name already reflects the final intended test layer.

### Unit / Regression Tests

Count: `24`

- `baseline_contracts_test.py`
- `dsl_negative_test.py`
- `goal10_workloads_test.py`
- `goal15_compare_test.py`
- `goal17_prepared_runtime_test.py`
- `goal18_result_mode_test.py`
- `goal19_compare_test.py`
- `goal22_reproduction_test.py`
- `goal23_reproduction_test.py`
- `goal28b_staging_test.py`
- `goal28c_conversion_test.py`
- `goal28d_execution_test.py`
- `goal30_precision_abi_test.py`
- `goal31_lsi_gap_closure_test.py`
- `goal32_lsi_sort_sweep_test.py`
- `goal36_performance_test.py`
- `goal40_native_oracle_test.py`
- `paper_reproduction_test.py`
- `report_smoke_test.py`
- `rtdsl_language_test.py`
- `rtdsl_py_test.py`
- `rtdsl_ray_query_test.py`
- `rtdsl_simulator_test.py`
- `section_5_6_scalability_test.py`

### Backend Integration Tests

Count: `7`

- `baseline_integration_test.py`
- `cpu_embree_parity_test.py`
- `evaluation_test.py`
- `goal44_optix_benchmark_test.py`
- `optix_embree_interop_test.py`
- `rtdsl_embree_test.py`
- `rtdsl_vulkan_test.py`

### System / Accepted-Package Tests

Count: `9`

- `goal34_performance_test.py`
- `goal35_blockgroup_waterbodies_test.py`
- `goal37_lkau_pkau_test.py`
- `goal38_feasibility_test.py`
- `goal43_optix_validation_test.py`
- `goal45_optix_county_zipcode_test.py`
- `goal47_optix_goal41_large_checks_test.py`
- `goal50_postgis_ground_truth_test.py`
- `goal54_lkau_pkau_four_system_test.py`

## Main Gaps

### 1. No explicit canonical test matrix

The repo has enough tests to validate many behaviors, but not yet one clear
release-style command matrix such as:

- fast unit gate
- backend integration gate
- full accepted-system gate

### 2. System tests are present but fragmented

The accepted bounded packages are covered by multiple goal-specific tests, but
that coverage is not yet consolidated into one explicit acceptance layer.

### 3. Backend coverage is not equally visible

Embree, OptiX, Vulkan, and PostGIS all appear in the suite, but the final
verification story is still distributed across goal-specific files rather than a
single test policy surface.
