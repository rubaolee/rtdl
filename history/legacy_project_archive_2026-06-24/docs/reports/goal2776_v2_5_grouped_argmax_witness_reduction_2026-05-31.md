# Goal2776 - v2.5 Grouped Argmax Witness Reduction

Date: 2026-05-31

## Purpose

Goal2776 adds the symmetric highest-score witness primitive for the existing
v2.5 grouped-argmin path:

`grouped_argmax_f64`

This is a generic grouped reduction, not an app-specific Hausdorff, nearest
neighbor, RayJoin, or DBSCAN operation. It selects one item per group by
highest-score value and uses deterministic lowest-item-id tie-breaks.

## Contract

Inputs:

- `group_ids:int64`
- `item_ids:int64`
- `scores:float64`
- `group_count`

Outputs:

- `group_ids:int64`
- `item_ids:int64`
- `scores:float64`
- `missing_group_ids:int64`

Semantics:

- group ids must be in `[0, group_count)`
- each non-empty group returns the item with the highest score
- equal-score ties return the lowest item id
- missing groups are reported explicitly
- NaN scores are rejected by the Triton preview path

## Implementation

Added:

- Python reference execution in `execute_v2_5_partner_continuation_reference`
- Triton descriptor `describe_triton_grouped_argmax_f64`
- Triton runner `run_triton_grouped_argmax_f64`
- score pass using `tl.atomic_max`
- item pass using `tl.atomic_min` over equal best-score rows
- support-matrix exposure through `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`

Partner status:

| Partner | Status |
| --- | --- |
| `python_reference` | `reference_contract` |
| `triton` | `preview_not_promoted` |
| `numba` | `unsupported_fail_closed` |
| `cupy_conformance` | `descriptor_only` |

## Boundary

This is not a public speedup claim, release claim, true-zero-copy claim, or
whole-app benchmark result. It is a generic continuation primitive that unlocks
future witness-style app adapters while keeping the engine and partner contract
app-agnostic.

## Validation Plan

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test
```

## Validation Results

Local Windows validation:

```text
Ran 52 tests in 0.035s

OK (skipped=5)
```

Pod validation on `69.30.85.171:22167`, RTX A5000, driver `570.211.01`,
Torch `2.8.0+cu128`, Triton `3.4.0`:

```text
PYTHONPATH=src:. timeout 240 python3 -m unittest \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test

Ran 6 tests in 2.771s

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
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test

Ran 52 tests in 4.012s

OK
```

The pod artifact is recorded in
`docs/reports/goal2776_pod_artifacts/goal2776_triton_grouped_argmax_pod_69_30_85_171_2026-05-31.json`.
This validates CUDA execution, not a promoted performance path.
