# Goal2665: v2.5 Triton Grouped Continuation Pod Runner

Status: local dry-run backed, CUDA pod execution required.

Date: 2026-05-27

## Purpose

Goal2663 and Goal2664 added preview Triton kernels for generic segmented sum
and segmented count. This goal adds the runner needed to validate them on a
Linux NVIDIA pod from a committed Git revision.

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

- `run_triton_segmented_count_i64()` against `torch.bincount()`;
- `run_triton_segmented_sum_f64()` against Torch `scatter_add_()`.

It records:

- per-repeat timings;
- median timings;
- speedups versus the Torch device baselines;
- correctness status;
- Python, Torch, Triton, CUDA, GPU, and Git commit identity.

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
