# Goal5167 - Generic Grid Cell-MBR Reduceat Result

Date: 2026-07-08

## Objective

Optimize the generic `point_grid_cell_mbrs_numpy_columns` helper by replacing
per-cell Python min/max loops with NumPy segmented reductions. This attacks a
measured full-res4 route phase without introducing any X-HD-specific core API.

## Code Change

Updated:

```text
src/rtdsl/partner_continuations.py
```

Inside `point_grid_cell_mbrs_numpy_columns`, each coordinate axis now computes
tight cell MBR min/max columns with:

```text
np.minimum.reduceat(sorted_axis, begin_offsets)
np.maximum.reduceat(sorted_axis, begin_offsets)
```

The public column contract is unchanged. Metadata now records:

```text
cell_mbr_reduction = numpy_reduceat
```

Added:

```text
tests/goal5167_grid_cell_mbr_reduceat_test.py
```

The test compares the reduceat path against an independent slow reference on a
sparse 3-D grid and keeps the app-neutral source scan.

## Local Validation

```text
py -m unittest tests.goal5167_grid_cell_mbr_reduceat_test \
  tests.goal5138_generic_grid_cell_candidate_api_test \
  tests.goal5145_dimension_generic_cell_mbr_frontdoor_test \
  tests.goal5166_xhd_res4full_scaling_test

Ran 13 tests OK
```

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

POD tests:

```text
python3 -m unittest tests.goal5167_grid_cell_mbr_reduceat_test \
  tests.goal5138_generic_grid_cell_candidate_api_test \
  tests.goal5145_dimension_generic_cell_mbr_frontdoor_test \
  tests.goal5166_xhd_res4full_scaling_test

Ran 13 tests OK
```

POD matrix command:

```text
cd /root/rtdl_goal5093 &&
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5167_reduceat_matrix_pod.json
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5167_reduceat_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Result

```text
case = res4full
matched = true
point_count_a = 5205
point_count_b = 7108
validation_mode = author-only

author HDResult = 0.1241602823138237
RTDL author_comparison_distance = 0.12416027787377293
author_abs_diff = 4.440050771492565e-09

author Running.AvgTime = 4.549 ms
author process wall = 1.1355813145637512 s
RTDL route median = 0.051644258201122284 s
RTDL total median = 0.09228210896253586 s

ratios_authorized = false
```

Per-direction median phases after Goal5167:

```text
directed_a_to_b:
  direction_total = 0.025322578847408295 s
  grid_cell_mbrs = 0.0021681413054466248 s
  initial_state_seed = 0.009955748915672302 s
  frontier_rows = 0.005600467324256897 s
  nearest_continuation = 0.0051597654819488525 s
  max_nearest_reduction = 0.0007293224334716797 s

directed_b_to_a:
  direction_total = 0.025966204702854156 s
  grid_cell_mbrs = 0.0015785619616508484 s
  initial_state_seed = 0.010062150657176971 s
  frontier_rows = 0.006355516612529755 s
  nearest_continuation = 0.005056560039520264 s
  max_nearest_reduction = 0.001039348542690277 s
```

## Comparison To Goal5166

Goal5166 full-res4 route median:

```text
0.059233590960502625 s
```

Goal5167 full-res4 route median:

```text
0.051644258201122284 s
```

The route improves by about 7.6 ms on this POD run. The intended grid phase
improves more directly:

```text
Goal5166 combined grid cell-MBR median:
  0.006306082010269165 + 0.0052251145243644714
  = 0.011531196534633637 s

Goal5167 combined grid cell-MBR median:
  0.0021681413054466248 + 0.0015785619616508484
  = 0.003746703267097473 s
```

So the measured grid construction phase falls by about 7.8 ms.

## Interpretation

This is a small, generic system optimization. It proves that one measured
full-res4 route phase was still paying avoidable Python-loop overhead and that
the public grid cell-MBR helper can remove it without changing the route
contract.

The post-Goal5167 full-res4 route is now more balanced. The largest measured
subphase is the nearest-cell-MBR seed, followed by native frontier rows and
nearest continuation. Further work should be selected from the new phase table,
not from stale pre-Goal5167 bottlenecks.

## What This Proves

- The generic grid cell-MBR helper preserves tight MBR semantics under the
  reduceat implementation.
- The full public res4 Level B route still matches author HDResult.
- The measured grid construction phase improves on the POD run.

## What This Does Not Prove

- It does not prove exact paper dataset reproduction.
- It does not prove full X-HD paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Status

```text
goal5167_grid_cell_mbr_reduceat_complete__review_pending
```
