# Goal5188 - X-HD Full Public Phase-Boundary Matrix

Date: 2026-07-08

## Verdict

```text
completed_full_public_phase_boundary_matrix__no_ratio__implemented_review_pending
```

Goal5188 builds a phase-boundary matrix for the full public Stanford
Dragon/HappyBuddha Level-B candidate. It places author `hd_exec` phase evidence
beside RTDL all-source route evidence without reporting an author-vs-RTDL
performance ratio.

This is phase disclosure and bottleneck evidence. It is not exact paper dataset
reproduction, not full paper reproduction, and not a speedup/parity claim.

## Inputs

Candidate:

```text
Dragon source points:      437645
HappyBuddha target points: 543652
Level:                     Level B same-source public Stanford candidate
```

Correctness anchor:

```text
author HDResult:     0.12572988867759705
RTDL route distance: 0.12572988629271128
abs diff:            2.3848857610975216e-09
tolerance:           1e-6
matched:             true
exact oracle used:   false
```

## Implementation

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py
```

The author gate now records subprocess `wall_sec` when it runs `hd_exec`.

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_full_public_phase_matrix.py
```

The matrix builder consumes:

```text
Goal5188 author raw JSON
Goal5188 author summary with process wall
Goal5187 RTDL all-source route-only summary
```

It does not run algorithms itself and does not compute any ratio.

New test:

```text
tests/goal5188_xhd_full_public_phase_matrix_test.py
```

The test verifies:

- author internal timing and author process wall are separate fields;
- RTDL route wall and total are separate fields;
- no ratio is computed;
- full paper / exact paper / performance claims remain false.

## POD Author Timed Run

POD:

```text
root@213.173.108.24 -p 13502
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

Command:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py \
  --bridge Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --author-json Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5188_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5188_graphics_dragon_happy_buddha_2026-07-08.json \
  --run-goal Goal5188 \
  --tolerance 1e-6
```

Key author values:

```text
author HDResult = 0.12572988867759705
paper-log abs diff = 1.9371509552001953e-07
author Running.AvgTime = 7.603 ms
author process wall = 1.973201423883438 s
matched = true
```

Author internal phase evidence:

```text
BVHBuildTime = 0.336 ms
GridResolution = [10, 24, 10]
LargeCells = 674

Iteration 1:
  NumInputPoints = 437645
  NumOutputPoints = 150
  RTTime = 2.667 ms
  CUDATime = 0.799 ms
  OffloadingSize = 58994

Iteration 2:
  NumInputPoints = 150
  NumOutputPoints = 0
  RTTime = 0.463 ms
  CUDATime = 0.196 ms
  OffloadingSize = 4427
```

## RTDL All-Source Route Evidence

Source:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json
```

Key RTDL values:

```text
route_wall_sec = 7.303133897483349
total_sec = 10.011082544922829
load_full_inputs_sec = 2.5199945867061615
case_total_sec = 7.490384787321091
frontier_row_count = 2052249
frontier_row_capacity = 4000000
native symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
initial_cell_mbr_tests = 2824560830
total_candidate_distance_evaluations = 342424979
```

RTDL route subphases:

```text
source_columns = 0.060262925922870636 s
target_columns = 0.07752387970685959 s
grid_cell_mbrs = 0.18383577466011047 s
radius_selection = 0.02942413091659546 s
initial_state_seed = 4.041994109749794 s
frontier_rows = 1.9368688240647316 s
nearest_continuation = 0.5595467016100883 s
max_nearest_reduction = 0.07290426641702652 s
direction_total = 6.962371997535229 s
```

Dominant RTDL route phases:

```text
initial_state_seed ~= 4.04 s
frontier_rows       ~= 1.94 s
```

These two phases explain most of the current RTDL route wall.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.full_public_phase_matrix.v1
```

## Why No Ratio Is Reported

No author-vs-RTDL performance ratio is authorized here.

Reason:

```text
Author Running.AvgTime is an internal author algorithm phase.
RTDL route_wall_sec and total_sec include different Python/RTDL phase boundaries.
Author process wall includes author executable startup/loading under a different
implementation and process boundary.
A ratio requires a separate denominator review.
```

The matrix intentionally records:

```text
author_running_avg_vs_rtdl_route_ratio_computed = false
author_process_wall_vs_rtdl_total_ratio_computed = false
ratio_reported = false
```

## Claim Boundary

This goal claims:

- full public author run evidence exists;
- full public RTDL all-source route evidence exists;
- both agree on HDResult within tolerance;
- author and RTDL phase evidence is now placed side by side;
- current RTDL route bottlenecks are visible.

This goal does **not** claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- Figure 5 reproduction;
- exact-oracle validation of the all-source route;
- author performance parity;
- author-vs-RTDL speedup or slowdown ratio.

## Validation

Commands:

```text
py -m unittest \
  tests.goal5188_xhd_full_public_phase_matrix_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5186_xhd_full_public_author_gate_test

py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_full_public_phase_matrix.py \
  --author-summary Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5188_graphics_dragon_happy_buddha_2026-07-08.json \
  --author-json Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5188_graphics_dragon_happy_buddha_2026-07-08.json \
  --rtdl-route-summary Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_phase_matrix_goal5188_graphics_dragon_happy_buddha_2026-07-08.json \
  --run-goal Goal5188
```

Result:

```text
Ran 5 tests in 8.198s
OK

matched = True
ratio_reported = False
```

Known local Python noise:

```text
Could not find platform independent libraries <prefix>
```

The commands exit successfully despite this environment message.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5188 raw author JSON, timed author summary,
and phase matrix artifact.

## Next Recommended Goal

Goal5189 should target the largest RTDL route phase:

```text
initial_state_seed ~= 4.04 s
```

This must remain a generic RTDL system improvement. It should not introduce an
X-HD-specific primitive. Candidate directions:

1. reduce the `437645 x 6454` cell-MBR seed test volume;
2. move more of the nearest-cell-MBR seed into native/OptiX or a generic CUDA
   kernel;
3. preserve lower-distance / lower-cell-id / lower-target-id tie-breaks;
4. keep Goal5187 correctness against author HDResult as the gate.
