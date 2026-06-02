# Goal3048 Hausdorff Active-Frontier Parameter Sweep

Date: 2026-06-02

Status: harness landed; A4000 run pending.

## Purpose

Goal3046 showed that the active-frontier Hausdorff path is not only a
single-generator win. Goal3048 asks the next narrower engineering question:
whether the app-level default policy for seed sample count and target points per
group should change.

The harness is:

- `scripts/goal3048_hausdorff_active_frontier_parameter_sweep.py`

It uses the Goal3046 dataset factories, validates each dataset/size against
`cupy_grouped_grid_rawkernel`, then sweeps:

- seed sample counts,
- target points per group,
- repeated active-frontier trials per configuration.

The current policy reference in this harness is `seed_sample_count=1024` and
`target_points_per_group=512`, matching the Goal3045/3046 evidence runs.

## Boundary

This harness is internal tuning evidence only. It does not authorize a public
speedup claim, release claim, broad RT-core claim, whole-app claim, true
zero-copy claim, or automatic default-policy change.

The expected output artifact is:

- `docs/reports/goal3048_hausdorff_active_frontier_parameter_sweep_a4000_2026-06-02.json`
