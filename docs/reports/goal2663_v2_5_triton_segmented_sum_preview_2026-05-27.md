# Goal2663: v2.5 Triton Segmented-Sum Preview

Status: preview implementation, pod validation required.

Date: 2026-05-27

## Purpose

This goal adds the first concrete v2.5 Triton-targeted partner-continuation
backend for the generic `segmented_sum_f64` operation defined in Goal2662.

The purpose is to start replacing hand-written CuPy RawKernel-style
continuations with a friendlier Python+Triton path while preserving the v2.3
and v2.4 benchmark principle:

```text
Python app
  -> partner-owned typed columns
  -> RTDL/OptiX or RTDL/Embree performs generic RT traversal
  -> Triton performs generic continuation/reduction
  -> Python consumes the result
```

This is not a benchmark promotion and makes no public speedup claim.

## Implemented Surface

New module:

- `src/rtdsl/triton_partner_continuation.py`

New exported API:

- `triton_partner_available()`
- `describe_triton_segmented_sum_f64()`
- `run_triton_segmented_sum_f64()`
- `TRITON_SEGMENTED_SUM_F64_OPERATION`
- `TRITON_PARTNER_CONTINUATION_STATUS`

New test:

- `tests/goal2663_v2_5_triton_segmented_sum_test.py`

## Contract

`run_triton_segmented_sum_f64()` accepts CUDA Torch tensors:

- `group_ids`: `torch.int64`, shape `(row_count,)`
- `values`: `torch.float64`, shape `(row_count,)`
- `group_count`: non-negative integer

The output is a CUDA Torch tensor `sums[group] = sum(values[row])` for rows
whose `group_ids[row] == group`.

The wrapper rejects invalid group ids outside `[0, group_count)`, matching the
Goal2662 Python reference semantics. The kernel uses Triton `tl.atomic_add`
over partner-owned device tensors. It does not replace RT traversal, does not
embed app semantics, and does not require CuPy RawKernel.

## Boundary

This preview is intentionally conservative:

- `status = preview_not_promoted`
- `raw_kernel_required = False`
- `replaces_rt_traversal = False`
- `promoted_performance_path = False`
- `rt_core_speedup_claim_authorized = False`

The Triton continuation is only the post-RT generic reduction step. Any RT-core
claim must still come from a same-contract RTDL/OptiX traversal path, with
phase-separated evidence.

## Local Environment Result

The current Mac environment is Apple Silicon (`arm64`) with Homebrew Python
3.14 and no NVIDIA CUDA stack. Local imports reported no available `triton`,
`torch`, `numba`, or `numpy` packages.

Therefore, this goal is local source/test backed only. Executable Triton
correctness and performance validation require a Linux NVIDIA pod with CUDA,
Torch, and Triton installed.

## Validation

Run locally:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2663_v2_5_triton_segmented_sum_test \
  tests.goal2662_v2_5_partner_continuation_contract_test
```

Expected on this Mac:

- descriptor and lazy-import tests pass;
- CUDA execution test is skipped when Triton/Torch CUDA are unavailable;
- no performance claim is made.

## Pod Gate

Before promoting this path, run on a CUDA pod from a committed revision:

```bash
git fetch origin
git reset --hard origin/main
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2663_v2_5_triton_segmented_sum_test
```

Then add a larger benchmark that compares:

- Python reference semantics;
- existing CuPy conformance where applicable;
- Triton continuation time;
- the same RTDL traversal path with phase-separated timing.

Promotion is blocked until the Triton continuation preserves benchmark
performance instead of merely improving ease of use.
