# Goal3855: Current Scale Refresh After Numba Hot-Path Accounting

Date: 2026-06-08

Status: A5000 scale-profile refresh complete

## Purpose

Goal3851 changed the RT-DBSCAN scale-profile row from a cold single
OptiX+Numba component pass to a prepared repeat column-signature route. Goal3853
made the Barnes-Hut Numba force-summary row forward `repeat` / `warmup` and
report the real prepared force-kernel median.

Goal3855 refreshes all ten promoted benchmark scale-profile rows after those
two accounting fixes.

## A5000 Result

Artifact:

- `docs/reports/goal3855_current_scale_after_numba_hot_accounting_a5000/summary.json`

Runner:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-json docs/reports/goal3855_current_scale_after_numba_hot_accounting_a5000/summary.json \
  --output-dir docs/reports/goal3855_current_scale_after_numba_hot_accounting_a5000/outputs \
  --timeout-scale 1.25 --heartbeat-sec 10 --stdout-tail 1600 --stderr-tail 1600
```

All ten rows passed:

| App | Process sec | Hot metric sec | Note |
| --- | ---: | ---: | --- |
| `hausdorff_xhd` | `1.752` | `0.0504` | prepared directed-threshold query total |
| `spatial_rayjoin` | `1.753` | `0.00307` | prepared PIP count query median |
| `rt_dbscan` | `4.504` | `0.282` | Goal3851 prepared OptiX+Numba column signature |
| `robot_collision` | `1.834` | not yet extracted | needs similar hot/cold split audit |
| `contact_manifold` | `1.002` | not yet extracted | needs similar hot/cold split audit |
| `raydb_style` | `2.252` | not yet extracted | output has rich nested timing; not normalized here |
| `barnes_hut` | `2.002` | `0.00895` | Goal3853 prepared Numba force-kernel median |
| `librts_spatial_index` | `2.002` | `0.0310` | prepared AABB query median |
| `rtnn` | `3.003` | not yet extracted | runner progress has per-repeat timings; not normalized here |
| `triangle_counting` | `1.752` | `0.897` | current host-indexed fallback hot query |

Top-level claim flags remained false:

- `release_authorized=false`
- `public_speedup_claim_authorized=false`
- `broad_rt_core_claim_authorized=false`
- `paper_reproduction_claim_authorized=false`

## Interpretation

The refresh confirms the current next engineering target:

- RT-DBSCAN is no longer the largest hot path after Goal3851. Its prepared
  payload is about `0.282s`, while process time is dominated by startup/JIT.
- Barnes-Hut exact force is not the next kernel target at this 8192-body scale.
  Its prepared force kernel median is about `0.009s`; process time is startup
  and setup dominated.
- Triangle counting is now the clearest hot path. Its current OptiX row reports
  `query_raw_view_sec=0.896843162` and explicitly describes the path as a
  `host_indexed_fallback`, not an RT-core graph acceleration claim.

## Boundary

This packet is an internal scale-profile refresh and target-selection report.
It does not authorize release action, public speedup wording, broad RT-core
wording, paper-reproduction wording, true-zero-copy wording, or app-specific
native-engine logic.

