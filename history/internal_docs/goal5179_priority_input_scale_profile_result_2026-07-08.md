# Goal5179 Priority Input Scale Profile: Dragon-HappyBuddha

Date: 2026-07-08

## Verdict

```text
completed_priority_input_scale_profile__no_route_run__implemented_review_pending
```

Goal5179 profiles the full public Stanford Dragon/HappyBuddha Level B candidate
from Goal5178. It records geometry scale, grid occupancy, and the size of a
naive pairwise route.

This is planning/scale evidence. It is not a route run, figure reproduction,
full paper reproduction, exact paper dataset reproduction, or a performance
ratio.

## Why This Goal Exists

Goal5178 found that local public Stanford full-resolution Dragon/HappyBuddha
files match the author paper-branch log point counts:

```text
dragon.ply:        437645
happy_buddha.ply:  543652
```

The old exact pairwise reference route is not appropriate for this scale.
Goal5179 quantifies that rather than relying on intuition.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/profile_xhd_priority_input_scale.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\profile_xhd_priority_input_scale.py \
  --bridge Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json \
  --grid-shapes "8,8,8;16,16,16;32,32,32"
```

The profiler streams ASCII PLY vertices and does not materialize a point-pair
matrix.

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.priority_input_scale_profile.v1
```

Status:

```text
graphics_dragon_happy_buddha_full_public_candidate_profiled__no_route_run
```

## Geometry Profile

```text
dragon.ply:
  vertices: 437645
  faces:    871414
  MBR extents: [0.2048902, 0.1444435, 0.0916218]
  MBR diagonal: 0.2669053633472546

happy_buddha.ply:
  vertices: 543652
  faces:    1087716
  MBR extents: [0.081322, 0.1980229, 0.0814178]
  MBR diagonal: 0.2290309908402136
```

## Pairwise Exact Route Estimate

```text
point pairs: 237926579540
scientific: 2.379266e+11

float32 distance matrix:       951706318160 bytes
float64 distance matrix:      1903412636320 bytes
16-byte candidate rows:       3806825272640 bytes
24-byte candidate rows:       5710237908960 bytes
32-byte candidate rows:       7613650545280 bytes

pairwise_exact_route_allowed: false
```

This is the hard reason not to run the old materialized exact path.

## Grid Occupancy Profile

Dragon:

```text
8^3:
  occupied cells: 271 / 512
  max points per cell: 6348
  median points per occupied cell: 1327
  p95 points per occupied cell: 3975.0

16^3:
  occupied cells: 1253 / 4096
  max points per cell: 1894
  median points per occupied cell: 311
  p95 points per occupied cell: 830.6

32^3:
  occupied cells: 5252 / 32768
  max points per cell: 599
  median points per occupied cell: 73.5
  p95 points per occupied cell: 199.45
```

HappyBuddha:

```text
8^3:
  occupied cells: 294 / 512
  max points per cell: 7202
  median points per occupied cell: 1594.0
  p95 points per occupied cell: 4638.8

16^3:
  occupied cells: 1469 / 4096
  max points per cell: 1732
  median points per occupied cell: 305
  p95 points per occupied cell: 996.6

32^3:
  occupied cells: 6454 / 32768
  max points per cell: 510
  median points per occupied cell: 65.0
  p95 points per occupied cell: 234.0
```

## Route Feasibility Decision

The artifact records:

```text
do_not_run_naive_pairwise_exact: true
requires_scalable_route: true
```

Candidate route components:

```text
author-directed mode from Goal5173
generic grid/cell-MBR construction
nearest-cell-MBR seed
native 3-D cell-MBR frontier
native inline-nearest for inline cells
grouped Numba nearest continuation for offload rows
```

Next gate:

```text
bounded full-public-candidate feasibility gate with fail-closed row capacities
and phase counters, not a performance ratio
```

## Validation

Commands:

```text
py -m unittest tests.goal5179_xhd_priority_input_scale_profile_test tests.goal5178_xhd_priority_input_bridge_test
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_scale_profile_goal5179_graphics_dragon_happy_buddha_2026-07-08.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
```

Result:

```text
Ran 2 tests in 0.117s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite this Windows Python noise.

## What This Proves

Goal5179 proves:

```text
the full public Stanford candidate scale is known;
the old materialized pairwise route is infeasible for this target;
the next step must be a scalable seeded/frontier route feasibility gate;
grid occupancy is available to choose fail-closed row capacity and grid policy.
```

## What This Does Not Prove

Goal5179 does not prove:

```text
the scalable route runs on full 437645 x 543652;
author-vs-RTDL performance;
Figure 5 reproduction;
exact paper dataset reproduction;
full paper reproduction.
```

## Next Recommended Goal

Goal5180 should implement a **dry-run / bounded feasibility gate** for the
full public Dragon-HappyBuddha candidate:

```text
load full inputs
build grid/cell-MBR structures
choose row capacities fail-closed
run either a safe limited source subset or a metadata-only frontier estimate
record phase counters
do not report performance ratio
do not materialize pairwise rows
```

If Goal5180 can run the actual scalable route on a bounded source subset with
author-directed correctness against an exact subset oracle, then the following
goal can attempt full-route execution on POD.
