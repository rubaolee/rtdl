# Goal5187 - X-HD Full Public RTDL All-Source Route-Only Gate

Date: 2026-07-08

## Verdict

```text
completed_full_public_rtdl_all_source_route_only_matched_author_hdresult__level_b_only__implemented_review_pending
```

Goal5187 runs the scalable RTDL route over **all** Dragon source points and all
HappyBuddha target points for the public Stanford Level-B candidate, then
compares the route result to the Goal5186 author `HDResult`.

This is the first all-source RTDL route gate for the full public
Dragon/HappyBuddha candidate. It is route-only author-comparison evidence. It
is not exact-oracle validated, not exact paper dataset reproduction, not full
paper reproduction, and not a performance ratio.

## Why This Goal Exists

Goal5185 validated source_limit `8192` against an exact subset oracle, but the
oracle already required:

```text
4453597184 point-pair evaluations
62.34s exact subset reference time
```

The full candidate would require:

```text
437645 * 543652 = 237926579540 directed point pairs
```

So Goal5187 explicitly switches to route-only all-source validation against the
Goal5186 author `HDResult`.

## Implementation

Updated script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

New route-only controls:

```text
--source-limits all
--skip-exact-oracle
--author-summary <Goal5186 author JSON or summary>
--author-hd-result <value>
--author-tolerance <tol>
```

The old exact-subset mode remains available. The new all-source mode requires
an author comparator when exact oracle validation is skipped.

New test:

```text
tests/goal5187_xhd_full_public_route_only_gate_test.py
```

The test proves:

- `source_limits=all` resolves to the full source count;
- `--skip-exact-oracle` does not create an exact reference;
- author comparison is required fail-closed;
- claim flags distinguish route-only all-source evidence from exact paper or
  performance claims.

## POD Run

POD:

```text
root@213.173.108.24 -p 13502
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

Command:

```text
cd /root/rtdl_goal5093

python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  --bridge Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --profile Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json \
  --run-goal Goal5187 \
  --backend optix \
  --grid-shape 32,32,32 \
  --source-limits all \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --max-inline-points 64 \
  --frontier-nearest-executor auto \
  --frontier-row-order native \
  --frontier-inline-nearest \
  --frontier-row-capacity 4000000 \
  --skip-exact-oracle \
  --author-summary Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json \
  --author-tolerance 1e-6
```

The command succeeded.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json
```

Key values:

```text
source_count = 437645
target_count = 543652
backend = optix
native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
grid_shape = 32,32,32
frontier_row_capacity = 4000000
frontier_row_count = 2052249
exact_oracle_used = false
match_basis = author_hd_result
author_hd_result = 0.12572988867759705
rtdl_route_distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
author_tolerance = 1e-6
matched = true
```

Route phase timings:

```text
load_full_inputs = 2.535542368888855s
rtdl_route_wall = 7.303133897483349s
total = 10.011082544922829s

direction_total = 6.962371997535229s
source_columns = 0.060262925922870636s
target_columns = 0.07752387970685959s
grid_cell_mbrs = 0.18383577466011047s
radius_selection = 0.02942413091659546s
initial_state_seed = 4.041994109749794s
frontier_rows = 1.9368688240647316s
nearest_continuation = 0.5595467016100883s
max_nearest_reduction = 0.07290426641702652s
```

Work counters:

```text
initial_cell_mbr_tests = 2824560830
initial_candidate_distance_evaluations = 55041996
continuation_candidate_distance_evaluations = 287382983
total_candidate_distance_evaluations = 342424979
```

The naive full pairwise exact route would require:

```text
237926579540 point-pair evaluations
```

## Relationship To Goal5186 Author Run

Goal5186 author full-public run:

```text
author_hd_result = 0.12572988867759705
author_running_avg_time_ms = 7.823
```

Goal5187 RTDL route-only all-source run:

```text
rtdl_route_distance = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
matched = true
```

Do **not** report an author-vs-RTDL performance ratio from these values. Author
`Running.AvgTime` is an internal author algorithm phase. RTDL `rtdl_route_wall`
includes the current Python/RTDL route phases under a different denominator.
Any performance comparison needs a separate phase-boundary review.

## Claim Boundary

This goal claims:

- the RTDL scalable route ran over the full public Dragon source and full public
  HappyBuddha target;
- the RTDL route-only result matched the Goal5186 author `HDResult`;
- the gate avoided full pairwise exact materialization and exact-oracle
  validation by design.

This goal does **not** claim:

- exact-oracle validation for the all-source result;
- exact paper dataset reproduction;
- full paper reproduction;
- Figure 5 reproduction;
- author performance parity;
- author-vs-RTDL speedup or slowdown ratio;
- that public Stanford files are byte-identical to author local dataset files.

## Validation

Commands:

```text
py -m unittest \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5186_xhd_full_public_author_gate_test \
  tests.goal5182_xhd_explicit_frontier_capacity_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5180_xhd_full_public_feasibility_gate_test

py -m json.tool \
  Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json
```

Result:

```text
Ran 10 tests in 2.202s
OK
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

The manifest now includes the Goal5187 all-source route-only artifact under
`evidence.result_artifacts`.

## Next Recommended Goal

Goal5188 should build a fair phase-boundary matrix for the full public
Dragon/HappyBuddha candidate:

- author raw JSON `Running.AvgTime` and author process/wall fields;
- RTDL load, route, and route subphases;
- explicit statement that no ratio is authorized unless a reviewer accepts a
  matched denominator;
- current dominant RTDL phases: initial seed (`~4.04s`) and native frontier
  rows (`~1.94s`).

If performance work continues, the next generic RTDL targets are:

1. reduce the generic all-source nearest-cell-MBR seed cost;
2. reduce native frontier row production cost or row volume;
3. keep all changes app-neutral and validated on non-X-HD fixtures where
   promoted to system API.
