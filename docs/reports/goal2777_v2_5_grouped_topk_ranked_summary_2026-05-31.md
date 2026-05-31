# Goal2777 - v2.5 Grouped Top-K Ranked Summary

Date: 2026-05-31

## Purpose

Goal2777 adds the generic ranked-summary primitive needed before RTNN-style
nearest-neighbor benchmark adapters can move from legacy CuPy/Torch continuation
paths toward the v2.5 Triton partner surface:

`grouped_topk_f64`

This is not an RTNN-specific primitive. It selects up to `k` lowest-score items
per integer group with deterministic score-then-item-id ordering. App code can
interpret scores as distances, costs, penalties, or any other caller-owned
metric.

## Contract

Inputs:

- `group_ids:int64`
- `item_ids:int64`
- `scores:float64`
- `group_count`
- `k`

Outputs:

- `group_ids:int64`
- `item_ids:int64`
- `scores:float64`
- `ranks:int64`
- `row_offsets:int64`
- `missing_group_ids:int64`

Semantics:

- group ids must be in `[0, group_count)`
- `k` must be positive
- the Triton preview supports `k <= 64`
- duplicate `(group_id, item_id)` rows use the lowest score for that item
- rows are ordered by lowest score, then lowest item id
- empty groups are reported explicitly
- NaN scores are rejected

## Implementation

Added:

- Python reference execution in `execute_v2_5_partner_continuation_reference`
- Triton descriptor `describe_triton_grouped_topk_f64`
- Triton runner `run_triton_grouped_topk_f64`
- iterative score/item selection kernels using `tl.atomic_min`
- ranked fixed-width dense scratch columns plus compact output rows
- support-matrix exposure through `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`

Partner status:

| Partner | Status |
| --- | --- |
| `python_reference` | `reference_contract` |
| `triton` | `preview_not_promoted` |
| `numba` | `unsupported_fail_closed` |
| `cupy_conformance` | `descriptor_only` |

## Boundary

This is not a public speedup claim, release claim, true-zero-copy claim, RTNN
paper reproduction claim, or whole-app benchmark result. It is a generic v2.5
continuation primitive that closes the ranked/top-k operation-shape gap for
future RTNN-style app adapters.

## Validation Plan

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2777_v2_5_triton_grouped_topk_preview_test
```

## Validation Results

Local Windows validation:

```text
Ran 59 tests in 0.047s

OK (skipped=6)
```

Pod validation on `69.30.85.171:22167`, RTX A5000, driver `570.211.01`,
Torch `2.8.0+cu128`, Triton `3.4.0`:

```text
PYTHONPATH=src:. timeout 240 python3 -m unittest \
  tests.goal2777_v2_5_triton_grouped_topk_preview_test

Ran 6 tests in 3.720s

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
  tests.goal2777_v2_5_triton_grouped_topk_preview_test

Ran 59 tests in 3.613s

OK
```

The pod artifact is recorded in
`docs/reports/goal2777_pod_artifacts/goal2777_triton_grouped_topk_pod_69_30_85_171_2026-05-31.json`.
This validates CUDA execution, not a promoted performance path.
