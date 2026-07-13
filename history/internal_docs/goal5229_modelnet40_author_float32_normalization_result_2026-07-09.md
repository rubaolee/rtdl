# Goal5229 - ModelNet40 Author-Float32 Normalization Result

Date: 2026-07-09

## Verdict

```text
completed_modelnet40_all400_author_float32_normalization__400_of_400_at_1e_minus_6
```

Goal5229 resolves the two Goal5227 near-threshold failures without loosening the
official tolerance. The fix is to match the author paper-branch input arithmetic:
ModelNet40 normalization must use the author's default float coordinate
semantics.

## Why This Goal Was Needed

Goal5227 executed all 400 unique ModelNet40 pairs with double-precision
app-owned normalization and the strict `1e-6` float-author gate:

```text
matched_case_count = 398
failed_case_count = 2
max diff = 1.4973206821644602e-06
```

Goal5228 showed those two failures pass at diagnostic `2e-6`, but changing the
tolerance would have been weaker than explaining the source of the difference.

## Root Cause

The author paper-branch executable dispatches the 3D run through:

```text
RunHausdorffDistanceImpl<float, 3>
```

Author source evidence:

```text
/tmp/xhd-goal5222_author_paper/src/run_hausdorff_distance.cu
```

Relevant behavior:

```text
double dist = -1;
...
dist = RunHausdorffDistanceImpl<float, 3>(config);
...
stats.Log("HDResult", dist);
```

The author `NormalizePoints` transform is templated on the same coordinate
type, so for the paper branch's default ModelNet40 path the lower-bound,
max-extent, and division arithmetic occur with float coordinates.

RTDL's app-owned OFF bridge had been normalizing with NumPy `float64`. That was
more precise, but not the same input arithmetic as the author comparator.

## Implementation

Added app-owned helper:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
normalize_point_matrix_to_author_float32_unit_box(...)
```

The helper:

```text
casts input coordinates to float32
computes lower / upper / max_extent with float32 coordinate semantics
normalizes in float32
returns a float64 matrix for the generic RTDL route
```

The generic route still receives plain numeric coordinate columns. No X-HD,
OFF, ModelNet40, or paper-specific behavior is added to RTDL core.

The route gate gained:

```text
--author-float32-normalization
```

The ModelNet40 batch runner forwards that flag into the route gate.

## Validation

Local validation:

```text
py -m unittest tests.goal5219_xhd_off_normalize_input_contract_test tests.goal5223_modelnet40_algorithm_aware_comparator_test tests.goal5203_numpy_point_matrix_input_loader_test tests.goal5205_fast_ascii_ply_matrix_loader_test
Ran 25 tests OK

py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py tests/goal5219_xhd_off_normalize_input_contract_test.py tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

POD validation:

```text
python3 -m unittest tests.goal5219_xhd_off_normalize_input_contract_test tests.goal5223_modelnet40_algorithm_aware_comparator_test
Ran 16 tests OK
```

## Full All-400 Result

The full all-400 unique-pair run was repeated with:

```text
--author-float32-normalization
--selection-strategy all_unique_pairs
--max-pairs 400
--chunk-size 25
--skip-completed
--continue-on-error
--tolerance 1e-6
```

Aggregate result:

```text
selected_count = 400
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
```

Error distribution:

```text
max RTDL-vs-author HDResult diff = 6.59728109919655e-08
cases above 1e-6 = 0
```

Timing totals:

```text
RTDL route_wall_sec sum = 396.20282135903835
RTDL full total_sec sum = 593.3385793119669
author process_wall_sec sum = 256.336787045002
```

Timing is reported as an operational measurement only. It is not an
author-vs-RTDL performance ratio or parity claim.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_aggregate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5229_modelnet40_all400_float32norm_case_artifacts_2026-07-09.tar.gz
```

Diagnostic predecessors:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5227_modelnet40_all400_aggregate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5228_tolerance_probe_case063_tol2e-6_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5228_tolerance_probe_case114_tol2e-6_summary_2026-07-09.json
```

## Claim Boundary

Allowed:

```text
With author-float32 normalization, the algorithm-aware public-OFF normalized
ModelNet40 route matches all 400 unique pairs at the original strict 1e-6
tolerance.
```

Forbidden:

```text
All 2000 ModelNet40 paper-log records are complete.
Exact paper input byte identity is proved.
Author-vs-RTDL performance parity is established.
The timing totals are a fair author-vs-RTDL ratio.
Full X-HD paper reproduction is complete.
```

## Next Step

Use author-float32 normalization as the ModelNet40 app-owned input contract and
extend from the 400 unique pairs to the full 2000 ModelNet40 paper-log records,
or produce a fair denominator-aligned performance matrix before making any
performance comparison.
