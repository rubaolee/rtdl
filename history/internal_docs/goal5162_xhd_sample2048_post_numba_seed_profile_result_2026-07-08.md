# Goal5162 - X-HD Sample2048 Post-Numba-Seed Profile Result

## Verdict

`completed_sample2048_post_numba_seed_profile`

## What Changed

Goal5162 extends the seeded X-HD performance matrix script to accept:

```text
sample2048
```

It then runs the current post-Goal5161 route on the existing Stanford graphics
Level B sample2048 fixture:

```text
stanford_dragon_res4_sample2048.ply
stanford_happy_res4_sample2048.ply
```

This is a measurement/profile goal. It does not add a new X-HD algorithm and it
does not change RTDL core.

## Files Changed

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5162_xhd_sample2048_post_numba_seed_profile_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_post_numba_seed_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample2048 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_post_numba_seed_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample2048_post_numba_seed_profile_pod.json
```

## Results

```text
case = sample2048
point_count_a = 2048
point_count_b = 2048
matched = true
author Running.AvgTime = 4.147 ms
RTDL route median = 0.05855253338813782 s
RTDL total median = 0.07209980487823486 s
validation_mode = author-only
ratios_authorized = false
```

Directional median phase profile:

```text
A->B:
  grid_cell_mbrs = 0.004936255514621735 s
  seed = 0.0034295693039894104 s
  frontier_rows = 0.003653004765510559 s
  nearest_continuation = 0.017481721937656403 s
  max_nearest_reduction = 0.0002675354480743408 s
  frontier_row_count = 5852
  total_candidate_distance_evaluations = 85761

B->A:
  grid_cell_mbrs = 0.004449993371963501 s
  seed = 0.002872273325920105 s
  frontier_rows = 0.0034774988889694214 s
  nearest_continuation = 0.0164177268743515 s
  max_nearest_reduction = 0.0002753138542175293 s
  frontier_row_count = 5594
  total_candidate_distance_evaluations = 80737
```

## Interpretation

Goal5162 confirms that Goal5161's Numba seed improvement scales to sample2048:
seed is no longer the dominant phase. On the larger representative fixture, the
dominant measured route phase is now nearest continuation:

```text
nearest continuation combined ~= 0.0339s
grid construction combined     ~= 0.0094s
frontier rows combined         ~= 0.0071s
seed combined                  ~= 0.0063s
```

Therefore the next route-performance target should be the generic nearest
continuation over active frontier rows, not seed or pruned-row frontier
materialization.

This result still does not authorize an author-vs-RTDL ratio. Author
`Running.AvgTime`, author process wall, RTDL route time, and RTDL total time are
different phase boundaries.

## Validation

Local:

```text
py -m unittest tests.goal5162_xhd_sample2048_post_numba_seed_profile_test \
  tests.goal5161_numba_nearest_cell_mbr_seed_test
Ran 7 tests OK (skipped=1 before artifact existed)
```

POD:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --cases sample2048 ... --validation-mode author-only
matched = true
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a sample2048 representative same-source route profile for the
current post-Goal5161 RTDL route.
