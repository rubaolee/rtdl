# Gemini External Review: Goal4317 Grouped Reduction Adapter Route

Date: 2026-06-11
Reviewer: Gemini CLI
Verdict: `accept-with-boundary`

## Executive Summary

Goal4317 successfully establishes `rtdsl.adapters.reductions` as the canonical import route for grouped and summary reduction front doors. This is a surgical refactoring step that decouples public exports and generic stream adapters from the `partner_adapters.py` monolith without moving the underlying implementation bodies. The change is strictly limited to import routing and does not authorize any new performance or architectural claims.

## Requested Checks

### 1. Public `rtdsl` reduction exports route through `rtdsl.adapters.reductions`
**Confirmed.** I verified that `src/rtdsl/__init__.py` has been rewired to import the following symbols from `.adapters.reductions` instead of `.partner_adapters`:
- Key/Value Reductions: `partner_group_sum_by_key`, `partner_group_min_by_key`, `partner_group_max_by_key`, `partner_group_count_by_key`, `partner_group_any_by_key`.
- Metric-Table Reductions: `partner_metric_table_reduce_batch`, `partner_metric_table_reduce_by_key`, `partner_metric_table_reduce_repeated_pattern`.
- Unique-Pair Keys: `partner_unique_pair_keys`, `partner_group_count_unique_pairs_by_key`.
- Ranked/Vector/Witness: `grouped_argmin_f64_partner_columns`, `grouped_argmax_f64_partner_columns`, `grouped_topk_f64_partner_columns`, `grouped_vector_sum_2d_partner_columns`, `global_argmax_u32_f64_partner_columns`, `group_argmin_then_global_argmax_partner_columns`.
- Prepared Sessions/Selection: `prepare_grouped_vector_sum_2d_partner_columns_session`, `run_grouped_vector_sum_2d_partner_columns_session`, `measured_grouped_vector_sum_2d_partner_selection`.

### 2. `v2_8_segmented_typed_stream_adapter.py` import routing
**Confirmed.** The following imports in `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` have been moved to `.adapters.reductions`:
- `grouped_vector_sum_2d_partner_columns` (inside `execute_grouped_vector_sum_typed_stream_partner_columns`)
- `grouped_argmin_f64_partner_columns`, `grouped_argmax_f64_partner_columns`, `grouped_topk_f64_partner_columns` (inside `_execute_partner_front_door`)

### 3. Implementation bodies remain in `partner_adapters.py`
**Confirmed.** `src/rtdsl/adapters/reductions.py` acts as a routing layer and continues to import the actual implementation from `..partner_adapters`. The report is honest in stating that this is an incremental split, not a full migration of logic.

### 4. Boundary Enforcement
**Confirmed.** The report explicitly denies authorization for:
- Release action / Release readiness.
- Public speedup or RT-core claims.
- True zero-copy or device residency proofs.
- Package installation or paper reproduction claims.
- Automatic partner selection or app-specific native engine logic.

The implementation in `v2_8_segmented_typed_stream_adapter.py` continues to enforce these boundaries by raising `ValueError` if any promotion/authorization flags are set.

## Validation Results

The following test suite was executed:
```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4317_grouped_reduction_adapter_route_test tests.goal2781_grouped_vector_sum_adapter_test tests.goal3008_numba_group_argmin_global_argmax_front_door_test
```
**Result:** 11 tests ran successfully, with 2 expected skips (Windows environment skips for CUDA-specific tests). The new test `tests/goal4317_grouped_reduction_adapter_route_test.py` specifically verifies the import routing through source inspection and attribute identity checks.

## Final Assessment

Goal4317 is a clean, well-bounded refactor that successfully reduces direct dependency on the `partner_adapters` monolith for high-level surfaces. It adheres to the requested scope and maintains architectural integrity.
