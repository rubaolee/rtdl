# Goal2678: v2.5 Triton Compact Mask Preview

Status: local implementation slice, CUDA pod validation still required.

Date: 2026-05-27

## Purpose

Several benchmark apps need generic row/filter compaction before they can move
off legacy CuPy/PyTorch continuations. This goal adds an executable-preview
Triton continuation for:

- `compact_mask_i64`

The operation compacts int64 values by a boolean mask and emits the kept values
plus original row indices. It is app-independent.

## Boundary

This remains preview work:

- no public speedup claim;
- no promoted benchmark path;
- no RT traversal replacement;
- no CuPy requirement;
- no PyTorch partner requirement.

The current implementation uses Triton kernels for per-block keep counting and
scatter. It uses the tensor carrier for the temporary block-prefix sum, recorded
as `tensor_carrier_prefix_sum_used=True`. That is acceptable for preview but
must be revisited before any pure Triton continuation claim.

## Implementation

Updated file:

- `src/rtdsl/triton_partner_continuation.py`

New public functions:

- `describe_triton_compact_mask_i64()`
- `run_triton_compact_mask_i64()`

The generic dispatcher `run_triton_partner_continuation()` now routes
`compact_mask_i64` through this preview kernel.

Goal2679 later adds `grouped_argmin_f64`; Goal2680 later adds
`bounded_collect_finalize_i64`.

## App Impact

This reduces the gap for RT-DBSCAN, triangle counting, Spatial RayJoin optional
row post-processing, and robot/contact witness filtering. Bounded witness
finalization remains the main missing generic Triton operation until Goal2680.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2678_v2_5_triton_compact_mask_preview_test
```

On non-CUDA macOS, descriptor/source tests run and executable validation is
skipped. CUDA pod validation must run before promotion.
