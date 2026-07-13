# Goal5166 - X-HD Full Public Stanford Res4 Level-B Scaling Result

Date: 2026-07-08

## Objective

Run the current post-Goal5163 X-HD route on the full public Stanford res4
Dragon/HappyBuddha PLY fixtures available in this repository.

This is a stronger Level B same-source representative gate than sample4096. It
is still not exact X-HD paper dataset reproduction, because the paper's exact
input files and hashes remain unavailable.

## New Fixtures

Generated normalized full-res4 fixtures by reusing the app-owned deterministic
PLY preparation path with a count larger than the input:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_full.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_full.ply
```

Source files:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip_res4.ply
Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip_res4.ply
```

Fixture summaries:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_full_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_full_summary.json
```

Counts:

```text
dragon res4 full fixture = 5205 points
happy  res4 full fixture = 7108 points
```

Claim boundary in both fixture summaries:

```text
same_source_sample = true
exact_paper_dataset_reproduction_claimed = false
performance_claimed = false
```

## Code Changes

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
```

Added case:

```text
res4full:
  stanford_dragon_res4_full.ply
  stanford_happy_res4_full.ply
```

Added test:

```text
tests/goal5166_xhd_res4full_scaling_test.py
```

It verifies:

- the runner supports `res4full`;
- full-res4 fixture summaries preserve Level B boundaries;
- the POD artifact, when present, keeps `ratios_authorized=false`,
  `performance_claim_authorized=false`, `validation_mode=author-only`, and no
  ratio fields.

## POD Execution

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Matrix command:

```text
cd /root/rtdl_goal5093 &&
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases res4full \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_post_goal5163_matrix_pod.json
```

Result artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_post_goal5163_matrix_pod.json
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

author Running.AvgTime = 4.56 ms
author process wall = 1.1186843365430832 s
RTDL route median = 0.059233590960502625 s
RTDL total median = 0.0998341366648674 s

ratios_authorized = false
```

Per-direction median phases:

```text
directed_a_to_b:
  direction_total = 0.028984278440475464 s
  grid_cell_mbrs = 0.006306082010269165 s
  initial_state_seed = 0.009569711983203888 s
  frontier_rows = 0.005480028688907623 s
  nearest_continuation = 0.005010224878787994 s
  max_nearest_reduction = 0.0007196888327598572 s

directed_b_to_a:
  direction_total = 0.029935002326965332 s
  grid_cell_mbrs = 0.0052251145243644714 s
  initial_state_seed = 0.009871728718280792 s
  frontier_rows = 0.0070023685693740845 s
  nearest_continuation = 0.005072072148323059 s
  max_nearest_reduction = 0.0010123774409294128 s
```

Candidate work:

```text
directed_a_to_b:
  initial_candidate_distance_evaluations = 193317
  continuation_candidate_distance_evaluations = 612923
  total_candidate_distance_evaluations = 806240
  initial_cell_mbr_tests = 1478220
  frontier_row_count = 17964

directed_b_to_a:
  initial_candidate_distance_evaluations = 188251
  continuation_candidate_distance_evaluations = 539093
  total_candidate_distance_evaluations = 727344
  initial_cell_mbr_tests = 1798324
  frontier_row_count = 21910
```

## Interpretation

The current route matches author HDResult on the largest public Stanford res4
fixture pair currently prepared in the app:

```text
Dragon res4 full:       5205 points
HappyBuddha res4 full:  7108 points
```

Compared with Goal5165 sample4096, the route median rises from about 0.041s to
about 0.059s. The phase table remains balanced: seed, grid construction,
native frontier rows, and nearest continuation all contribute. This suggests
the next performance step should be chosen from fresh full-res4 profile
evidence rather than from old pre-5163 bottlenecks.

The first repeat includes warmup/JIT/native setup effects. The reported route
number is median-of-5 in a long-lived process. It is not comparable to author
`Running.AvgTime` as a ratio.

## What This Proves

- Current RTDL route correctness extends to full public Stanford res4 fixtures.
- The current Level B route handles unequal input sizes: 5205 vs 7108 points.
- The latest same-source scale point is now `res4full`, not `sample4096`.
- The full-res4 phase profile gives a better basis for choosing the next
  system-performance target.

## What This Does Not Prove

- It does not prove exact paper dataset reproduction.
- It does not prove full X-HD paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Validation

Local:

```text
py -m unittest tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5165_xhd_sample4096_scaling_test

Ran 6 tests OK (skipped=1)
```

POD:

```text
python3 -m unittest tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5165_xhd_sample4096_scaling_test

Ran 6 tests OK (skipped=1)
```

Local after pulling artifacts:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_post_goal5163_matrix_pod.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
py -m unittest tests.goal5166_xhd_res4full_scaling_test \
  tests.goal5165_xhd_sample4096_scaling_test \
  tests.goal5164_xhd_post_goal5163_three_sample_matrix_test \
  tests.goal5163_numba_frontier_nearest_continuation_test

Ran 13 tests OK
```

## Status

```text
goal5166_xhd_res4full_scaling_complete__review_pending
```
