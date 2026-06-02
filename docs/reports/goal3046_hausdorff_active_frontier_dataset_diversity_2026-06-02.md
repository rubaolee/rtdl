# Goal3046 Hausdorff Active-Frontier Dataset-Diversity Harness

Date: 2026-06-02

Status: harness landed; A4000 run pending.

## Purpose

Goal3045 confirmed that the active-frontier Hausdorff path remains faster than
the CuPy grouped-grid reference across repeated same-process trials for the
original dense demo generator. Goal3046 adds a dataset-diversity harness so the
next pod run can test whether that result survives more than one point-set
shape.

The harness is:

- `scripts/goal3046_hausdorff_active_frontier_dataset_diversity.py`

It compares the same two methods as Goal3045:

- `cupy_grouped_grid_rawkernel`
- `rtdl_rt_grouped_active_frontier_nearest_witness`

Each case uses warmup, alternating measurement order, median/IQR summaries, and
per-trial exact-distance validation.

## Dataset Shapes

The first A4000 run is expected to use:

- `demo_offset`: the original dense synthetic generator.
- `clustered_shift`: four shifted Gaussian-like clusters.
- `ring_vs_spiral`: structured curved point sets with anisotropic offset.
- `adversarial_tail_outlier`: a mostly overlapping cloud with a late outlier,
  used to ensure a seed sample that may miss the witness cannot break exactness.

## Boundary

This is internal v2.6 engineering evidence. It does not authorize release,
public speedup wording, broad RT-core speedup wording, whole-app speedup
wording, or true-zero-copy wording.

The expected output artifact is:

- `docs/reports/goal3046_hausdorff_active_frontier_dataset_diversity_a4000_2026-06-02.json`
