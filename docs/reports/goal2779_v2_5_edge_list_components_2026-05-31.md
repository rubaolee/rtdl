# Goal2779 - v2.5 Edge-List Components

Date: 2026-05-31

## Purpose

Goal2779 adds the generic component-labeling primitive needed before
DBSCAN-style benchmark adapters can move from legacy CuPy component continuations
toward the v2.5 Triton partner surface:

`edge_list_components_i64`

This is not a DBSCAN primitive. It labels connected components over a caller
supplied undirected edge list. App code owns the meaning of the edges and any
cluster policy.

## Contract

Inputs:

- `source_ids:int64`
- `target_ids:int64`
- `node_count`
- `max_iterations`

Outputs:

- `component_ids:int64`

Semantics:

- source and target ids must be in `[0, node_count)`
- labels use the smallest node id in each component
- the Triton preview uses fixed-iteration min-label propagation
- `max_iterations` must be chosen by the caller to cover the component diameter

## Implementation

Added:

- Python reference execution in `execute_v2_5_partner_continuation_reference`
- Triton descriptor `describe_triton_edge_list_components_i64`
- Triton runner `run_triton_edge_list_components_i64`
- a relaxation kernel using `tl.atomic_min`
- a compression kernel for iterative label propagation
- support-matrix exposure through `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`

Partner status:

| Partner | Status |
| --- | --- |
| `python_reference` | `reference_contract` |
| `triton` | `preview_not_promoted` |
| `numba` | `unsupported_fail_closed` |
| `cupy_conformance` | `descriptor_only` |

## Boundary

This is not a public speedup claim, release claim, true-zero-copy claim, DBSCAN
cluster-quality claim, or whole-app benchmark result. It is a generic v2.5
continuation primitive that closes the component-labeling operation-shape gap
for future app adapters.

The Triton preview is deliberately conservative. It is exact when the caller's
`max_iterations` covers the component diameter; benchmark promotion requires a
canonical app adapter, convergence policy, and large-scale pod evidence.

## Validation Plan

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2779_v2_5_triton_edge_list_components_preview_test
```

## Validation Results

Local Windows validation:

```text
Ran 74 tests in 0.053s

OK (skipped=8)
```

Pod validation on `69.30.85.171:22167`, RTX A5000, driver `570.211.01`,
Torch `2.8.0+cu128`, Triton `3.4.0`:

```text
PYTHONPATH=src:. timeout 240 python3 -m unittest \
  tests.goal2779_v2_5_triton_edge_list_components_preview_test

Ran 6 tests in 2.799s

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
  tests.goal2778_v2_5_triton_grouped_vector_sum_preview_test \
  tests.goal2779_v2_5_triton_edge_list_components_preview_test

Ran 73 tests in 5.186s

OK
```

The pod artifact is recorded in
`docs/reports/goal2779_pod_artifacts/goal2779_triton_edge_list_components_pod_69_30_85_171_2026-05-31.json`.
This validates CUDA execution, not a promoted performance path.
