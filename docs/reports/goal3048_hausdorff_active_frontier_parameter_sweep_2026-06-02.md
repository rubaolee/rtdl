# Goal3048 Hausdorff Active-Frontier Parameter Sweep

Date: 2026-06-02

Status: harness landed; A4000 run passed; active-frontier seed default promoted to 1024.

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

## A4000 Run

Pod:

- SSH target: `root@157.157.221.29 -p 19771`
- GPU: NVIDIA RTX A4000
- Source commit: `0bc6f39fd4744c9638b3e99e566ad2ec8934cb6c`

Command shape:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/.venvs/rtdl_goal3042/bin/python \
  scripts/goal3048_hausdorff_active_frontier_parameter_sweep.py \
  --sizes 65536 131072 \
  --trials 3 \
  --warmup 1 \
  --seed-sample-counts 512 1024 2048 8192 \
  --target-points-per-groups 512 1024 2048 \
  --current-seed-sample-count 1024 \
  --current-target-points-per-group 512
```

All swept configurations matched the exact CuPy grouped-grid distance.

| Dataset | Points | Best seed | Best group | Best/current median ratio | Best median sec | Current median sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `adversarial_tail_outlier` | 65536 | 512 | 1024 | 0.951 | 0.077359158 | 0.081347729 |
| `adversarial_tail_outlier` | 131072 | 1024 | 1024 | 0.984 | 0.164214011 | 0.166819938 |
| `clustered_shift` | 65536 | 1024 | 2048 | 0.959 | 0.072961992 | 0.076090010 |
| `clustered_shift` | 131072 | 1024 | 1024 | 0.997 | 0.160328566 | 0.160876777 |
| `demo_offset` | 65536 | 2048 | 1024 | 0.979 | 0.075424777 | 0.077053518 |
| `demo_offset` | 131072 | 1024 | 2048 | 0.991 | 0.162254011 | 0.163667865 |
| `ring_vs_spiral` | 65536 | 512 | 512 | 0.993 | 0.075475843 | 0.076045566 |
| `ring_vs_spiral` | 131072 | 1024 | 1024 | 0.999 | 0.162010349 | 0.162111721 |

Summary:

- `seed_sample_count=8192` was never the best configuration.
- `seed_sample_count=1024` won five of eight cases.
- Best-vs-current median ratio was 0.951 at best and 0.988 at median, so the
  current 1024/512 evidence policy is already close to the local optimum.
- Group-size winners vary by dataset, so Goal3048 does not change the
  scale-aware group default.

Artifact:

- `docs/reports/goal3048_hausdorff_active_frontier_parameter_sweep_a4000_2026-06-02.json`

## Narrow Code Action

Goal3048 promotes the active-frontier default seed sample count from the older
8192 value to `1024` in:

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`

This is a user-facing app-layer default change only. It does not touch the
native engine or ABI. It also does not authorize public speedup wording; it only
keeps the default path aligned with the measured Goal3045/3046/3048 policy.
