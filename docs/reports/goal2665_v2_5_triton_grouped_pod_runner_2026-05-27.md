# Goal2665: v2.5 Triton Grouped Continuation Pod Runner

Status: local dry-run backed, CUDA pod execution required.

Date: 2026-05-27

## Purpose

Goal2663 and Goal2664 added preview Triton kernels for generic segmented sum
and segmented count. Goal2677 extends the same runner to segmented min/max.
This goal adds the runner needed to validate them on a Linux NVIDIA pod from a
committed Git revision.

The runner exists so v2.5 does not drift into undocumented local experiments.
It records correctness, timings, environment, and commit identity in one JSON
artifact.

## Implemented Surface

New script:

- `scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py`

New test:

- `tests/goal2665_v2_5_triton_grouped_runner_test.py`

The script is safe to dry-run on this Mac without Triton, Torch, or CUDA:

```bash
PYTHONPATH=src:. python3 \
  scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py \
  --dry-run
```

## Pod Command

On a CUDA pod:

```bash
git fetch origin
git reset --hard origin/main
PYTHONPATH=src:. python3 \
  scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py \
  --row-counts 100000,1000000,5000000 \
  --group-count 4096 \
  --repeats 5 \
  --output docs/reports/artifacts/goal2665_v2_5_triton_grouped_continuation_pod.json
```

## What It Measures

For each scale, the runner generates partner-owned CUDA Torch tensors:

- `group_ids:int64`
- `values:float64`

It validates:

- `run_triton_partner_continuation("segmented_count_i64", ...)` against `torch.bincount()`;
- `run_triton_partner_continuation("segmented_sum_f64", ...)` against Torch `scatter_add_()`;
- `run_triton_partner_continuation("segmented_min_f64", ...)` against Torch `scatter_reduce_(amin)`;
- `run_triton_partner_continuation("segmented_max_f64", ...)` against Torch `scatter_reduce_(amax)`;
- `run_triton_partner_continuation("compact_mask_i64", ...)` against Torch mask indexing;
- `run_triton_partner_continuation("grouped_argmin_f64", ...)` against Torch `scatter_reduce_(amin)` with lowest-item tie-break;
- `run_triton_partner_continuation("bounded_collect_finalize_i64", ...)` against Torch group-sort plus equivalent per-group row sets.
- optionally, with `--include-numba`, `run_numba_segmented_count_i64()` and
  `run_numba_segmented_sum_f64()` against the same Torch outputs.

It records:

- per-repeat timings;
- median timings;
- speedups versus the Torch device baselines;
- correctness status;
- Python, Torch, Triton, CUDA, GPU, and Git commit identity.

The Numba path is optional because Numba may not be installed on every pod. If
enabled, the runner uses the same generated in-range data and disables Numba's
per-call host validation for timing. This is acceptable only for runner
evidence; promotion still requires a device-resident validation design.

## Boundary

This runner does not measure RT traversal and does not authorize RT-core
wording. It measures generic post-RT partner continuation only.

The claim boundary remains:

- `preview_not_promoted = True`
- `no_public_speedup_claim = True`
- `not_rt_traversal_replacement = True`
- `partner_continuation_only = True`

Promotion requires later same-contract benchmark integration showing that the
Triton continuation preserves RTDL's existing OptiX-vs-Embree benchmark basis.
