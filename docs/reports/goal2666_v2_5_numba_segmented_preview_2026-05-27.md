# Goal2666: v2.5 Numba Segmented Continuation Preview

Status: preview implementation, CUDA pod validation required.

Date: 2026-05-27

## Purpose

Goal2662 defined Triton-first with Numba fallback as the v2.5 partner
direction. Goal2663 to Goal2665 started the Triton side. This goal adds the
matching Numba fallback preview for the same generic grouped continuation
operations:

- `segmented_count_i64`
- `segmented_sum_f64`

The goal is not to make Numba the preferred partner. The goal is to keep the
fallback path concrete and testable without weakening the Triton-first
architecture.

## Implemented Surface

New module:

- `src/rtdsl/numba_partner_continuation.py`

New exported API:

- `numba_partner_available()`
- `describe_numba_segmented_count_i64()`
- `describe_numba_segmented_sum_f64()`
- `run_numba_segmented_count_i64()`
- `run_numba_segmented_sum_f64()`
- `NUMBA_SEGMENTED_COUNT_I64_OPERATION`
- `NUMBA_SEGMENTED_SUM_F64_OPERATION`
- `NUMBA_PARTNER_CONTINUATION_STATUS`

New test:

- `tests/goal2666_v2_5_numba_segmented_preview_test.py`

## Contract

The Numba preview accepts Numba CUDA device arrays:

- `group_ids:int64`
- `values:float64` for the sum path

It returns Numba CUDA device arrays:

- `counts:int64`
- `sums:float64`

The wrapper defaults to fail-fast validation of group ids with a device
validation kernel. The kernel scans `group_ids` on device, writes a single
device error flag, and the wrapper copies back only that one flag before
rejecting ids outside `[0, group_count)`. That validation is not a performance
claim; it preserves the Goal2662 reference semantics while avoiding the earlier
full `group_ids` host copy.

## Boundary

This is a Numba fallback preview, not a promoted benchmark row.

The claim boundary remains:

- `status = preview_not_promoted`
- `raw_kernel_required = False`
- `replaces_rt_traversal = False`
- `promoted_performance_path = False`
- `rt_core_speedup_claim_authorized = False`

Numba does not replace RTDL/OptiX traversal. It only covers generic post-RT
continuation over device arrays.

## Local Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2666_v2_5_numba_segmented_preview_test
```

On this Mac the test verifies descriptor safety, lazy imports, source-level
boundaries, and docs. Executable correctness requires a CUDA pod with Numba and
NumPy installed.

## Next Work

Before this fallback can be promoted, a pod-backed runner must compare:

- Numba count/sum correctness against the Goal2662 Python reference;
- Numba timing against Triton and Torch device baselines;
- integration cost inside one real benchmark row.

No public speedup claim is authorized by this preview; in test wording, this
means no public speedup claim.
