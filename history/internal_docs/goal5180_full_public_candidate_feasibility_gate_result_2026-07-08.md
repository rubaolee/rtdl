# Goal5180 Full Public Candidate Feasibility Gate

Date: 2026-07-08

## Verdict

```text
completed_full_public_candidate_bounded_subset_route_feasibility__implemented_review_pending
```

Goal5180 runs the first bounded feasibility gate on the full public Stanford
Dragon/HappyBuddha Level B candidate from Goal5178/Goal5179.

This is a bounded subset route run against the full public target. It is not an
all-source route run, not exact paper dataset reproduction, not figure
reproduction, not full paper reproduction, and not a performance ratio.

## Why This Goal Exists

Goal5179 proved that naive pairwise exact materialization is infeasible:

```text
source points: 437645
target points: 543652
point pairs:   237926579540
16-byte candidate rows: ~3.8 TB
```

Goal5180 therefore exercises the scalable route safely:

```text
full source file loaded for deterministic subset selection;
full target file loaded and used by the route;
16 evenly-spaced source rows selected;
exact subset oracle computed without pairwise matrix materialization;
generic seeded/frontier/nearest route run against the full target;
route compared to exact subset oracle.
```

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_full_public_feasibility_gate.py \
  --bridge Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --profile Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json \
  --backend numpy \
  --grid-shape 32,32,32 \
  --source-limit 16 \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --frontier-nearest-executor auto \
  --frontier-row-order native \
  --tolerance 1e-9
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.full_public_feasibility_gate.v1
```

Status:

```text
full_public_candidate_bounded_subset_route_feasibility_checked
```

## Result

```text
matched: true
route_abs_diff: 0.0

full source count: 437645
full target count: 543652
source subset size: 16
source subset policy: evenly-spaced
grid shape: 32 x 32 x 32
backend: numpy
```

The selected source indices were:

```text
0, 29176, 58353, 87529, 116705, 145881, 175058, 204234,
233410, 262586, 291763, 320939, 350115, 379291, 408468, 437644
```

Exact subset oracle:

```text
distance: 0.11575949084515705
source_id: 8
target_id: 293420
pair_evaluations: 8698432
strategy: vectorized per-source exact nearest over the full target;
          no pairwise matrix materialization
```

RTDL route:

```text
distance: 0.11575949084515705
source_id: 8
target_id: 293420
frontier_row_count: 58518
grid_cell_count: 6454
initial_cell_mbr_tests: 103264
initial_candidate_distance_evaluations: 2157
continuation_candidate_distance_evaluations: 10584
total_candidate_distance_evaluations: 12741
nearest_executor: numba_parallel
frontier_contract: generic_cell_mbr_nearest_frontier_reference
```

## Phase Timing

These timings are diagnostic only and are not a performance ratio:

```text
load_full_inputs:        5.045158499851823 s
exact_subset_reference:  0.27420439990237355 s
rtdl_route_wall:         2.5646470999345183 s
total:                   8.104382100049406 s
```

Direction subphases:

```text
target_columns:          0.16545230010524392 s
grid_cell_mbrs:          0.2828173004090786 s
initial_state_seed:      0.7264362000860274 s
frontier_rows:           0.8454946000128984 s
nearest_continuation:    0.1858831001445651 s
max_nearest_reduction:   0.0001471000723540783 s
direction_total:         2.206302599981427 s
```

## Capacity Boundary

This is a **local NumPy bounded-subset gate**, not the POD/native fail-closed
capacity gate:

```text
this_gate: local_numpy_bounded_subset_no_native_row_capacity
actual_frontier_row_count_recorded: true
next_pod_optix_gate_must_use_fail_closed_row_capacity: true
```

The actual frontier row count (`58518`) is recorded so a later POD/OptiX gate
can choose explicit fail-closed capacity. This goal does not claim that native
capacity has been validated.

## What This Proves

Goal5180 proves:

```text
the full public target can be loaded and used by the scalable route;
a deterministic bounded source subset can be selected from the full source;
the scalable route matches an exact subset oracle against the full target;
the route avoids full pairwise row materialization;
the next gate can safely increase subset size or move to POD/OptiX capacity
planning.
```

## What This Does Not Prove

Goal5180 does not prove:

```text
all-source full public Dragon-HappyBuddha route completion;
author-vs-RTDL performance;
Figure 5 reproduction;
exact paper dataset reproduction;
full X-HD paper reproduction;
native/POD fail-closed row-capacity validation.
```

## Validation

Commands:

```text
py -m unittest tests.goal5180_xhd_full_public_feasibility_gate_test
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_full_public_feasibility_gate_goal5180_graphics_dragon_happy_buddha_2026-07-08.json > $null
```

Result:

```text
Ran 2 tests in 8.796s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite this Windows Python noise.

## Next Recommended Goal

Goal5181 should run a POD/OptiX feasibility gate for the same Level B candidate:

```text
increase the bounded source subset;
use native OptiX frontend where available;
set explicit fail-closed row capacity from Goal5180 row counts;
record route phase counters;
still do not claim performance ratio or full all-source reproduction.
```
