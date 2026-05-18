# Goal2340: Hausdorff v2.1 Benchmark Refresh

Date: 2026-05-18

Status: local implementation and pre-pod gate complete; fresh pod timing pending

## Purpose

This goal refreshes the Hausdorff/X-HD benchmark app on the current v2.1
branch. The app already had strong May 16 RTX A5000 evidence, but the learner
docs and one-method CLI still reflected the earlier v2.0-era shape. The goal is
to make the app easier to use, improve the default grouped RT path for large
rows, and prepare a clean current-main pod rerun.

## Change Summary

| Area | Operation |
| --- | --- |
| User API | Added `default_target_points_per_group(point_count)` for grouped point-set RT traversal. |
| RT grouped methods | Changed grouped RT witness methods so `target_points_per_group=None` selects a scale-aware default. Explicit integers still reproduce old sweeps. |
| CLI | Added `--target-points-per-group` and `--seed-sample-count` to `rtdl_hausdorff_v2_function.py`. |
| Public perf harness | Changed the default public-dataset group-size rule to use the same scale-aware helper. |
| Pod runner | Added `scripts/goal2340_hausdorff_v2_1_pod_runner.sh` with progress logging, CuPy/OptiX setup, and two X-HD graphics sweeps. |
| Learner docs | Updated the Hausdorff/X-HD README to describe the v2.1-compatible exact RT path and the new tuning knobs. |
| Tests | Repaired stale post-reorg test paths that still read the old root-level example filenames. |

## Scale-Aware Default

The new default keeps small runs unchanged but avoids tiny groups on large
X-HD-style rows:

| Target point count | Default group size |
| ---: | ---: |
| 1,024 | 64 |
| 8,192 | 64 |
| 131,072 | 1,024 |
| 262,144 | 2,048 |
| 524,288 | 4,096 |
| 1,048,576 | 8,192 |

This does not change the native engine. It is app-level Python policy over the
existing generic point-group traversal and reduction primitives. The goal is to
make the default user path closer to the group sizes that produced the strongest
public X-HD graphics/dense evidence, while leaving explicit reproducibility
knobs available.

## Current Evidence Boundary

Accepted prior evidence remains:

- RTDL/OptiX exact 2D projected-point Hausdorff beat optimized grouped CuPy on
  substantial public graphics and geo rows on RTX A5000 in Goals 2134, 2136,
  and 2139.
- The strongest prior dense row was Thai Statuette vs Asian Dragon at 1,048,576
  requested points, group size 8192: grouped CuPy 17.380398 s, RTDL/OptiX
  1.248008 s, 13.93x.
- The native engine surface stayed app-agnostic: point groups, threshold flags,
  nearest witnesses, and max-distance reduction; no native Hausdorff or X-HD
  ABI names.

This goal does not create a new public performance claim yet. Fresh pod timing
from current `main` is still required before replacing the May 16 numbers.

## Pod Rerun Plan

Use a clean NVIDIA pod from pushed/current source. The checked-in runner is:

```bash
bash scripts/goal2340_hausdorff_v2_1_pod_runner.sh
```

Expanded command shape:

```bash
git fetch origin main
git reset --hard origin/main
mkdir -p /root/vendor
git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk || true
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export PYTHONPATH=src:.
python scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite xhd-graphics \
  --sample-count 262144 \
  --warmup 1 \
  --json-out docs/reports/goal2340_hausdorff_v2_1_pod/xhd_graphics_262144_auto_group.json
python scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite xhd-graphics \
  --sample-count 1048576 \
  --warmup 1 \
  --json-out docs/reports/goal2340_hausdorff_v2_1_pod/xhd_graphics_1048576_auto_group.json
```

The rerun should record the pod SSH target, GPU, driver, commit, OptiX SDK tag,
CUDA prefix, and whether each row matches grouped CuPy exactly.

## Local Validation

Ran on Windows with `PYTHONPATH=src;.`:

```text
py -3 -m py_compile examples\v2_0\research_benchmarks\hausdorff_xhd\rtdl_hausdorff_v2_function.py scripts\goal2126_public_hausdorff_dataset_perf.py
py -3 -m unittest tests.goal2110_hausdorff_exact_rt_nearest_witness_test tests.goal2112_hausdorff_v2_language_lab_test tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test tests.goal2123_xhd_point_group_nearest_reduction_test tests.goal2131_xhd_seeded_pruned_hausdorff_test tests.goal2126_public_hausdorff_dataset_perf_test
py -3 -m unittest tests.goal2340_hausdorff_v2_1_benchmark_refresh_test
bash -n scripts/goal2340_hausdorff_v2_1_pod_runner.sh
```

Result: the focused pre-existing Hausdorff slice passed 28 tests; the broader
Hausdorff refresh slice passed 65 tests; shell syntax check passed.

## Verdict

Local v2.1 Hausdorff benchmark refresh: `accept`.

Fresh current-main pod performance claim: `needs-pod-evidence`.

Full X-HD reproduction, full 3D surface Hausdorff, MRI/BraTS reproduction,
original X-HD WKT-file reproduction, universal CUDA-vs-RT speedup, and release
authorization remain `not-claimed`.
