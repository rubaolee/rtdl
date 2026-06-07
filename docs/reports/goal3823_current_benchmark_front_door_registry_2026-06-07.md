# Goal3823 Current Benchmark Front-Door Registry

Date: 2026-06-07

Status: implemented locally.

## Purpose

Goal3823 turns the Goal3818-3822 benchmark-front-door evidence into a
single current command registry and one bounded runner.

The registry lives at:

`src/rtdsl/current_benchmark_front_doors.py`

The runner lives at:

`scripts/goal3823_current_benchmark_front_door_runner.py`

This is not a long-run performance matrix. It is the operational source of
truth for the current app smoke commands: a reviewer can run the same ten
front-door commands, see per-row progress, and receive a single JSON summary.

## Registered Commands

| App | Registered row |
| --- | --- |
| `hausdorff_xhd` | repaired OptiX `directed_threshold_prepared` command |
| `spatial_rayjoin` | prepared OptiX PIP count command |
| `rt_dbscan` | OptiX threshold flags plus Numba prepared-grid components |
| `robot_collision` | OptiX prepared device-count command |
| `contact_manifold` | repaired OptiX `native_collect_k` command with witness capacity |
| `raydb_style` | primitive-first OptiX grouped count command |
| `barnes_hut` | no-RawKernel Numba exact-force command |
| `librts_spatial_index` | prepared OptiX AABB-index command |
| `rtnn` | executable `prepared_optix_ranked_summary` command |
| `triangle_counting` | explicit `--optix-graph-mode native` command |

## Runner

Dry-run:

```bash
PYTHONPATH=src:. python scripts/goal3823_current_benchmark_front_door_runner.py --dry-run
```

Pod smoke:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3823_current_benchmark_front_door_runner.py \
  --output-json docs/reports/goal3823_current_benchmark_front_door_registry_a5000/summary.json
```

The runner prints one start line and one completion line for every row, so a
pod run does not go silent while a benchmark command is active. Each row keeps
its own timeout from the registry.

## Boundary

Goal3823 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a command registry and smoke runner only.
