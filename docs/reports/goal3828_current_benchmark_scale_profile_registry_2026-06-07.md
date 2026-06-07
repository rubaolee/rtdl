# Goal3828 Current Benchmark Scale-Profile Registry

Date: 2026-06-07

Status: implemented and A5000-validated.

## Purpose

Goal3823 records fast executable front doors for the ten benchmark apps. Goal3828
adds the next layer: calibrated scale-profile commands that are large enough to
be useful for future performance packets while staying bounded enough for repeat
pod runs.

This goal is a direct follow-up to Goal3827. Future scale-profile runners must
not use undrained stdout pipes for JSON-heavy apps. The Goal3828 runner writes
each row's stdout and stderr to files, prints heartbeat progress, then parses
the completed stdout file for JSON validity and forbidden claim flags.

## Source Of Truth

Registry:

`src/rtdsl/current_benchmark_scale_profiles.py`

Runner:

`scripts/goal3828_current_benchmark_scale_profile_runner.py`

Dry run:

```bash
PYTHONPATH=src:. python scripts/goal3828_current_benchmark_scale_profile_runner.py --dry-run
```

Pod run:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_EMBREE_LIBRARY=$PWD/build/librtdl_embree.so \
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-json docs/reports/goal3828_current_benchmark_scale_profiles_a5000/summary.json
```

## Calibrated Default Rows

| App | Row | Calibrated role |
| --- | --- | --- |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | safe but short OptiX threshold scale row |
| `spatial_rayjoin` | `spatial_rayjoin_pip_count_scale_default_prepared_optix` | safe but short repeated prepared PIP count row |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_8192` | default 8192-point row; 65k remains too heavy |
| `robot_collision` | `robot_collision_optix_scale_default_1024` | default 1024-pose row; 4096 is stress-only |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | safe grid64 bounded collect-k row |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | safe medium primitive-first grouped count row |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | safe when stdout is file-backed |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | safe medium prepared AABB-index row |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | safe medium prepared ranked-summary row |
| `triangle_counting` | `triangle_counting_optix_scale_default_native_2048` | safe but short explicit native timing row |

## Runner Discipline

The runner records:

- selected command and timeout for every row,
- stdout/stderr file paths and byte counts,
- per-row elapsed time,
- JSON parse status,
- forbidden true claim-flag paths, and
- an aggregate `all_pass` value.

Rows fail closed if stdout is not JSON or if a forbidden claim flag is set to
true anywhere in the emitted payload.

## A5000 Pod Evidence

Artifact:

`docs/reports/goal3828_current_benchmark_scale_profiles_a5000/summary.json`

Result: all ten calibrated default scale profiles passed on the A5000 pod at
commit `a24f2812`. Every row emitted parseable JSON and zero forbidden true
claim flags.

| Row | Status | Elapsed seconds | JSON bytes |
| --- | --- | ---: | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.752 | 4006 |
| `spatial_rayjoin_pip_count_scale_default_prepared_optix` | pass | 1.502 | 3155 |
| `rt_dbscan_optix_numba_scale_default_8192` | pass | 7.755 | 4932 |
| `robot_collision_optix_scale_default_1024` | pass | 10.506 | 41592 |
| `contact_manifold_optix_scale_default_grid64` | pass | 1.002 | 7672 |
| `raydb_style_optix_count_scale_default_262k` | pass | 2.253 | 40920 |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 | 3400 |
| `librts_spatial_index_optix_scale_default_32768` | pass | 2.003 | 1849 |
| `rtnn_prepared_optix_scale_default_65536` | pass | 2.753 | 4810 |
| `triangle_counting_optix_scale_default_native_2048` | pass | 1.502 | 2258 |

This is calibrated execution evidence, not a performance leaderboard. Several
rows are still intentionally marked `safe_but_short`, so a later performance
packet may choose larger or repeated variants after separate calibration.

## Boundary

Goal3828 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a scale-profile registry and file-backed runner only.
