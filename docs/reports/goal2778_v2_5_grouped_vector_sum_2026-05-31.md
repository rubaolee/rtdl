# Goal2778 - v2.5 Grouped Vector Sum

Date: 2026-05-31

## Purpose

Goal2778 adds the generic two-component vector reduction needed before
Barnes-Hut-style benchmark adapters can move from legacy CuPy/Torch continuation
paths toward the v2.5 Triton partner surface:

`grouped_vector_sum_f64x2`

This is not a Barnes-Hut force primitive. It sums paired float64 components per
integer group. App code owns the meaning of those components.

## Contract

Inputs:

- `group_ids:int64`
- `values_x:float64`
- `values_y:float64`
- `group_count`

Outputs:

- `sum_x:float64`
- `sum_y:float64`

Semantics:

- group ids must be in `[0, group_count)`
- values are paired component columns with identical shape
- each output component is independently summed per group
- empty groups return zero for both components

## Implementation

Added:

- Python reference execution in `execute_v2_5_partner_continuation_reference`
- Triton descriptor `describe_triton_grouped_vector_sum_f64x2`
- Triton runner `run_triton_grouped_vector_sum_f64x2`
- one Triton JIT kernel using paired `tl.atomic_add` operations
- support-matrix exposure through `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`

Partner status:

| Partner | Status |
| --- | --- |
| `python_reference` | `reference_contract` |
| `triton` | `preview_not_promoted` |
| `numba` | `unsupported_fail_closed` |
| `cupy_conformance` | `descriptor_only` |

## Boundary

This is not a public speedup claim, release claim, true-zero-copy claim,
Barnes-Hut force-accuracy claim, or whole-app benchmark result. It is a generic
v2.5 continuation primitive that closes the two-component grouped vector-sum
operation-shape gap for future app adapters.

## Validation Plan

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test
```

## Validation Results

Local Windows validation:

```text
Ran 66 tests in 0.062s

OK (skipped=7)
```

Pod validation on `69.30.85.171:22167`, RTX A5000, driver `570.211.01`,
Torch `2.8.0+cu128`, Triton `3.4.0`:

```text
PYTHONPATH=src:. timeout 240 python3 -m unittest \
  tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test

Ran 6 tests in 2.196s

OK
```

```text
PYTHONPATH=src:. timeout 300 python3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2678_v2_5_triton_compact_mask_preview_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test \
  tests.goal2777_v2_5_triton_grouped_topk_preview_test \
  tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test

Ran 66 tests in 4.360s

OK
```

The pod artifact is recorded in
`docs/reports/goal2778_pod_artifacts/goal2778_triton_grouped_vector_sum_pod_69_30_85_171_2026-05-31.json`.
This validates CUDA execution, not a promoted performance path.
