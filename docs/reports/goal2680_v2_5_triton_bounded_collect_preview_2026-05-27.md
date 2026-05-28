# Goal2680: v2.5 Triton Bounded Collect/Finalize Preview

Status: local implementation slice; CUDA pod validation still required.

Date: 2026-05-27

## Purpose

`bounded_collect_finalize_i64` is the generic continuation needed by bounded
witness/contact, DBSCAN-style bounded adjacency, and top-k row materialization
paths. This goal moves it from descriptor/reference-only to an executable
Triton preview while preserving the core rule: the primitive says bounded row
collection, not collision, contact, DBSCAN, or any app-specific vocabulary.

## Contract

Inputs:

- `group_ids:int64`;
- `item_ids:int64`;
- `group_count`;
- `k`;
- optional `total_row_capacity`.

Outputs:

- `group_ids:int64`;
- `item_ids:int64`;
- `row_offsets:int64`;
- `counts:int64`.

Semantics:

- fail closed if any group would exceed `k`;
- fail closed if `total_row_capacity` is provided and would be exceeded;
- return no partial result on overflow;
- row order within a group is explicitly non-semantic in the Triton preview;
- app/domain interpretation of the rows remains outside the engine and
  primitive.

## Implementation

Added to `src/rtdsl/triton_partner_continuation.py`:

- `describe_triton_bounded_collect_finalize_i64()`;
- `run_triton_bounded_collect_finalize_i64()`;
- `_triton_bounded_collect_scatter_i64_kernel()`;
- generic dispatcher support through `run_triton_partner_continuation()`.

The preview uses the existing generic Triton segmented-count kernel to count
rows per group, checks overflow before materialization, builds `row_offsets`
with the tensor carrier prefix sum, and scatters all rows with a generic Triton
kernel. Torch remains a CUDA tensor carrier and prefix-sum helper, not the
v2.5 partner.

## Portfolio Impact

After this goal, every v2.5 generic partner-continuation operation has a local
Triton preview implementation:

- `segmented_count_i64`;
- `segmented_sum_f64`;
- `segmented_min_f64`;
- `segmented_max_f64`;
- `compact_mask_i64`;
- `grouped_argmin_f64`;
- `bounded_collect_finalize_i64`.

This removes the last local descriptor-only blocker for migrating the promoted
benchmark apps away from legacy CuPy/PyTorch continuations. It does not prove
performance or benchmark-app completion; app wiring and CUDA pod evidence are
still required.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test
```

Expected locally on this Mac:

```text
Ran 4 tests
OK (skipped=1)
```

The skipped test requires Triton plus Torch CUDA on a Linux NVIDIA pod.

## Claim Boundary

This is a generic post-RT continuation preview only. It does not replace RTDL
RT traversal, does not authorize public speedup claims, does not define stable
within-group row order, and does not complete v2.5. Promotion requires CUDA
correctness/timing evidence, app integration, and review.
