# Goal5165 - X-HD Sample4096 Level-B Scaling Result

Date: 2026-07-08

## Objective

Extend the current post-Goal5163 X-HD representative route beyond sample2048 by
adding a deterministic 4096-point Stanford graphics sample and running the same
production-style POD matrix.

This goal is movement toward full paper reproduction by increasing Level B
same-source scale. It is not exact paper dataset reproduction and it does not
authorize an author-vs-RTDL performance ratio.

## Changes

### New Level-B Fixtures

Generated deterministic even-index samples:

```text
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_dragon_res4_sample4096.ply
Paper-reproduction-apps/x-hd-paper/data/fixtures/stanford_happy_res4_sample4096.ply
```

Source files:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip_res4.ply
Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip_res4.ply
```

Fixture summaries:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_dragon_res4_sample4096_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_happy_res4_sample4096_summary.json
```

Counts:

```text
dragon res4 input points = 5205
happy  res4 input points = 7108
sample point count       = 4096 each
```

Claim boundary in both fixture summaries:

```text
same_source_sample = true
exact_paper_dataset_reproduction_claimed = false
performance_claimed = false
```

### Runner Support

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
```

Added case:

```text
sample4096:
  stanford_dragon_res4_sample4096.ply
  stanford_happy_res4_sample4096.ply
```

### Tests

Added:

```text
tests/goal5165_xhd_sample4096_scaling_test.py
```

It verifies:

- the matrix runner supports `sample4096`;
- the sample4096 fixture summaries preserve Level B boundaries;
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

Preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Matrix command:

```text
cd /root/rtdl_goal5093 &&
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample4096 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample4096_post_goal5163_matrix_pod.json
```

Result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample4096_post_goal5163_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_sample4096_author_hd_exec_output_pod.json
```

## Results

```text
case = sample4096
matched = true
point_count_a = 4096
point_count_b = 4096
validation_mode = author-only

author HDResult = 0.12403063476085663
RTDL author_comparison_distance = 0.12403064103157131
author_abs_diff = 6.270714683620504e-09

author Running.AvgTime = 4.301 ms
author process wall = 1.1219238340854645 s
RTDL route median = 0.041182391345500946 s
RTDL total median = 0.06723665446043015 s

ratios_authorized = false
```

Per-direction median phases:

```text
directed_a_to_b:
  direction_total = 0.021413490176200867 s
  grid_cell_mbrs = 0.005570501089096069 s
  initial_state_seed = 0.007090121507644653 s
  frontier_rows = 0.0042383745312690735 s
  nearest_continuation = 0.0029087886214256287 s
  max_nearest_reduction = 0.0005464553833007812 s

directed_b_to_a:
  direction_total = 0.019603773951530457 s
  grid_cell_mbrs = 0.005108408629894257 s
  initial_state_seed = 0.005923256278038025 s
  frontier_rows = 0.0040505677461624146 s
  nearest_continuation = 0.0028658881783485413 s
  max_nearest_reduction = 0.0005688667297363281 s
```

Candidate work:

```text
directed_a_to_b:
  initial_candidate_distance_evaluations = 92449
  continuation_candidate_distance_evaluations = 260908
  total_candidate_distance_evaluations = 353357
  initial_cell_mbr_tests = 1138688
  frontier_row_count = 12635

directed_b_to_a:
  initial_candidate_distance_evaluations = 87193
  continuation_candidate_distance_evaluations = 246626
  total_candidate_distance_evaluations = 333819
  initial_cell_mbr_tests = 1028096
  frontier_row_count = 12492
```

## Interpretation

The current post-Goal5163 route continues to match author HDResult at sample4096
and scales to a larger representative same-source sample.

The sample4096 route median is about 0.041s, up from the Goal5164 sample1024
and sample2048 medians of about 0.025s. The route is now relatively balanced:
grid MBR construction, Numba seed, native frontier rows, and Numba continuation
all contribute measurable time. There is no single stale bottleneck as clear as
pre-Goal5161 seed or pre-Goal5163 continuation.

The first repeat includes warmup/JIT/native setup effects, visible in the raw
phase run arrays, but the matrix reports median-of-5 route time. This remains a
production-style route metric, not a cold process or author `Running.AvgTime`
equivalent.

## What This Proves

- The current X-HD Level B route matches author HDResult on a 4096-point
  Stanford graphics representative sample.
- The matrix runner can now handle sample4096.
- The current RTDL route lock point extends beyond sample2048.
- The next performance target should be selected from fresh phase evidence;
  current evidence suggests a balanced route rather than a single dominant
  old bottleneck.

## What This Does Not Prove

- It does not prove exact X-HD paper dataset reproduction.
- It does not prove full paper reproduction or Figure 5-11 reproduction.
- It does not prove author algorithm equivalence.
- It does not authorize an author-vs-RTDL speedup/parity ratio.
- It does not prove author `Running.AvgTime` and RTDL route time are comparable
  denominators.

## Validation

Local:

```text
py -m unittest tests.goal5165_xhd_sample4096_scaling_test \
  tests.goal5164_xhd_post_goal5163_three_sample_matrix_test

Ran 4 tests OK (skipped=1)
```

POD:

```text
python3 -m unittest tests.goal5165_xhd_sample4096_scaling_test \
  tests.goal5164_xhd_post_goal5163_three_sample_matrix_test

Ran 4 tests OK (skipped=1)
```

Local after pulling POD artifacts:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample4096_post_goal5163_matrix_pod.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/perf_sample4096_author_hd_exec_output_pod.json
py -m unittest tests.goal5165_xhd_sample4096_scaling_test \
  tests.goal5164_xhd_post_goal5163_three_sample_matrix_test \
  tests.goal5163_numba_frontier_nearest_continuation_test

Ran 10 tests OK
```

## Status

```text
goal5165_xhd_sample4096_scaling_complete__review_pending
```
