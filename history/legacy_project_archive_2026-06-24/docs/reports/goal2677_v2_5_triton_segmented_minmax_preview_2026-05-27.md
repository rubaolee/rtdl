# Goal2677: v2.5 Triton Segmented Min/Max Preview

Status: local implementation slice, CUDA pod validation still required.

Date: 2026-05-27

## Purpose

The v2.5 Triton pivot cannot stop at count/sum. RayDB needs grouped min/max,
and other benchmark apps need max-style or min-style ranked summaries. This
goal adds generic Triton preview kernels for:

- `segmented_min_f64`
- `segmented_max_f64`

These are app-independent segmented reductions over `group_ids`, `values`, and
`group_count`.

## Boundary

This is still preview work:

- no public speedup claim;
- no promoted benchmark path;
- no RT traversal replacement;
- no CuPy requirement;
- no PyTorch partner requirement.

Torch CUDA tensors are still used as the carrier for Triton launch and for
temporary output compaction (`group_ids`, reduced values, and
`missing_group_ids`). The metadata records `tensor_carrier_compaction_used=True`
so this is not overclaimed as a pure finalized Triton-only pipeline.

## Implementation

Updated file:

- `src/rtdsl/triton_partner_continuation.py`

New public functions:

- `describe_triton_segmented_min_f64()`
- `describe_triton_segmented_max_f64()`
- `run_triton_segmented_min_f64()`
- `run_triton_segmented_max_f64()`

The generic dispatcher `run_triton_partner_continuation()` now routes min/max
through these preview kernels. At Goal2677, the v2.5 preview operation set is:

- `segmented_count_i64`
- `segmented_sum_f64`
- `segmented_min_f64`
- `segmented_max_f64`

Goal2678 later adds `compact_mask_i64` to the preview set, and Goal2679 later
adds `grouped_argmin_f64`.

## App Impact

RayDB grouped `min` and `max` now have a Triton executable-preview plan instead
of descriptor-only Triton metadata. They are still not promoted until CUDA pod
correctness/performance evidence is collected.

Hausdorff and RTNN still need grouped argmin/top-k style kernels; this goal only
covers the segmented max/min subproblem.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test
```

On non-CUDA macOS, descriptor/source tests run and executable validation is
skipped. CUDA pod validation must run before promotion.
