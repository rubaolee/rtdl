# Goal2519 Partner-Resident Grouped I64 Dispatch Boundary

Date: 2026-05-23

## Purpose

Goal2519 stabilizes the Python boundary for the experimental OptiX
partner-resident grouped i64 aggregate path. Previous goals added native
entry points for `count`, `sum`, `min`, `max`, and generic fused `sum_count`.
The RayDB-style benchmark app could still select those low-level functions
itself. This goal moves symbol selection behind one runtime dispatcher:

`run_optix_partner_resident_columnar_grouped_i64_reduction(...)`

The low-level functions remain exported for focused validation, but app code
uses the dispatcher.

## Boundary

Supported dispatcher reductions:

- `count`
- `sum`
- `min`
- `max`
- `sum_count`

The dispatcher is fail-closed:

- `allow_experimental_native=True` is required.
- `group_capacity` is required for every reduction.
- exactly one dense non-negative group key is supported.
- `sum`, `min`, `max`, and `sum_count` require `value_field`.
- unsupported reduction names fail before native symbol lookup.

## App Migration

The RayDB-style app now maps app result modes to generic reductions:

- `count` -> `count`
- `sum` -> `sum`
- `min` -> `min`
- `max` -> `max`
- `avg_as_sum_count` -> semantic aggregate `avg_as_sum_count`, reduction
  `sum_count`, composite lowering `["sum", "count"]`

This keeps `avg_as_sum_count` as a Python/app semantic while the runtime sees
only the generic fused grouped reduction.

## Metadata Contract

The dispatcher standardizes metadata for all five modes:

- `partner_resident_grouped_i64_dispatcher`
- `operation` / `reduction`
- `semantic_aggregate`
- `group_keys`, `group_key_field`, `value_field`
- `group_capacity`, `group_capacity_explicit`
- `native_reduction_symbol`
- `native_launch_count`
- `fused_native_reduction`
- `fused_native_reduction_symbol`
- `generic_sum_count_abi_used`
- `native_avg_abi_added`
- `native_abi_added`
- `compact_grouped_output_materialized`
- `input_table_copied_back_to_python_rows`
- `true_zero_copy_authorized`
- `public_speedup_claim_authorized`

## Claim Boundary

This is an experimental Python+partner+RTDL runtime boundary for CUDA tensor
descriptors. It does not reproduce RayDB, expose SQL or DBMS behavior,
authorize true zero-copy wording, authorize whole-app performance wording, or
add an average-specific native ABI.

No public speedup claim is authorized by this goal.

## Verification

Local:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal2519_partner_resident_grouped_i64_dispatch_boundary_test
```

Executed locally with the project venv:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2512_raydb_style_partner_resident_experimental_backend_test \
  tests.goal2513_partner_resident_group_capacity_contract_test \
  tests.goal2514_partner_resident_compact_grouped_output_test \
  tests.goal2515_partner_resident_grouped_min_max_i64_test \
  tests.goal2516_partner_resident_composite_avg_sum_count_test \
  tests.goal2517_partner_resident_fused_sum_count_i64_test \
  tests.goal2518_partner_resident_fused_sum_count_timing_test \
  tests.goal2519_partner_resident_grouped_i64_dispatch_boundary_test
```

Result: 43 tests passed.

Pod:

```bash
ssh -i ~/.ssh/id_ed25519_rtdl_codex -p 15902 root@213.173.108.13
cd /root/rtdl_python_only_goal2517
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/compat:/usr/local/cuda/lib64:${LD_LIBRARY_PATH:-}
export RTDL_OPTIX_LIB=/root/rtdl_python_only_goal2517/build/librtdl_optix.so
PYTHONPATH=src:. python3 scripts/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod.py
```

Evidence artifact:

`docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json`

Pod result:

- status: `ok`
- CUDA available: `true`
- dispatcher reductions: `["count", "sum", "min", "max", "sum_count"]`
- app uses dispatcher: `true`
- app direct low-level grouped symbols absent: `true`
- direct dispatcher cases match CPU reference: `true`
- app suite matches CPU reference: `true`
- `avg_as_sum_count` metadata records semantic aggregate `avg_as_sum_count`,
  runtime reduction `sum_count`, one native launch, generic sum_count ABI, and
  no native average ABI.

Pod focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2517_partner_resident_fused_sum_count_i64_test \
  tests.goal2518_partner_resident_fused_sum_count_timing_test \
  tests.goal2519_partner_resident_grouped_i64_dispatch_boundary_test
```

Result: 15 tests passed.
