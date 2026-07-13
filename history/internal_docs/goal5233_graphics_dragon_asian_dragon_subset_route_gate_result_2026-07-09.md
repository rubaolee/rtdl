# Goal5233 Graphics Dragon -> AsianDragon Subset Route Gate Result

Date: 2026-07-09

## Verdict

```text
completed_graphics_dragon_asian_dragon_bounded_subset_route_gate__level_b_only
```

Goal5233 takes the Goal5232 Dragon -> AsianDragon same-source bridge past
provenance-only status and runs a bounded RTDL route gate on the real public
Stanford candidate files.

This is still a Level-B same-source candidate result. It is not exact paper
dataset identity, not Figure 6 reproduction, not full X-HD paper reproduction,
and not a performance win.

## What Changed

Three practical blockers were removed.

1. The public bridge now records the directed author basename order:

```text
author_basename_order = ["dragon.ply", "asian_dragon.ply"]
source_basename = "dragon.ply"
target_basename = "asian_dragon.ply"
```

The subset route no longer relies on a hard-coded Dragon -> HappyBuddha target.
It resolves source/target from the bridge's author basename fields.

2. The app-owned PLY loader now supports Stanford binary PLY vertex matrices.
The existing ASCII-only loader is preserved, but `load_points_matrix(...,
input_type="ply")` can now consume:

```text
format ascii 1.0
format binary_little_endian 1.0
format binary_big_endian 1.0
```

This was required because the public AsianDragon file is:

```text
format = binary_big_endian 1.0
vertices = 3,609,600
```

This is input handling for the X-HD paper app. It does not add an RTDL core
mesh or X-HD primitive.

3. A scale-profile artifact was added for the new target:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_scale_profile_2026-07-09.json
```

The full pairwise size is:

```text
source_count = 437,645
target_count = 3,609,600
pair_count = 1,579,441,392,000
pairwise_exact_route_allowed = false
```

## Execution Artifact

Route result:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_subset16_numpy_2026-07-09.json
```

Command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  --bridge Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json \
  --profile Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_scale_profile_2026-07-09.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_goal5233_graphics_dragon_asian_dragon_subset16_numpy_2026-07-09.json \
  --backend numpy \
  --source-limits 16 \
  --grid-shape 32,32,32 \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --max-inline-points 512 \
  --initial-state local-grid-cell \
  --frontier-nearest-executor numba \
  --frontier-row-order native \
  --frontier-inline-nearest \
  --global-bound-early-break \
  --max-exact-pair-evaluations 100000000 \
  --tolerance 1e-9 \
  --run-goal Goal5233
```

## Result

```text
target = graphics_dragon_asian_dragon
full source points = 437,645
full target points = 3,609,600
source limit = 16
exact subset pair evaluations = 57,753,600
all_matched = true
route_abs_diff = 0.0
max_frontier_rows = 32
```

The route and exact subset oracle agree:

```text
RTDL route distance = 52.403860063228066
RTDL route source_id = 12
RTDL route target_id = 1069665

Exact subset distance = 52.403860063228066
Exact subset source_id = 12
Exact subset target_id = 1069665
```

Timing from this local run:

```text
load_full_inputs_sec = 0.7262587998993695
exact_subset_reference_sec = 2.104934800416231
rtdl_route_wall_sec = 13.79907640023157
total_sec = 29.107510400004685
```

This timing is not favorable to RTDL. Goal5233 is a correctness and route
capacity gate, not a speedup claim. The route is slower than the exact
per-source oracle on this 16-source bounded run.

## Validation

Unit tests:

```text
py -m unittest \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5178_xhd_priority_input_bridge_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5231_modelnet40_performance_matrix_test

Ran 13 tests in 1.884s
OK
```

Compile validation:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
```

Diff whitespace validation:

```text
git diff --check -- \
  Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py \
  tests/goal5205_fast_ascii_ply_matrix_loader_test.py \
  tests/goal5178_xhd_priority_input_bridge_test.py \
  tests/goal5181_xhd_full_public_subset_scaling_gate_test.py
```

No whitespace errors.

## Claim Boundary

Allowed:

```text
Dragon -> AsianDragon public Stanford same-source candidate files can now feed
the RTDL bounded subset route, and the 16-source route matches an exact subset
oracle.
```

Forbidden:

```text
Dragon -> AsianDragon exact paper input identity is proved.
Dragon -> AsianDragon all-source HDResult is reproduced.
Figure 6 is reproduced.
The RTDL route is faster than exact or author code.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next useful goal is not another input bridge. The next goal should choose
one of:

1. Run a larger bounded Dragon -> AsianDragon subset on POD/OptiX with explicit
   frontier capacity and no exact full-pair materialization.
2. Run the author binary on the same public Dragon -> AsianDragon candidate to
   learn whether the public candidate HDResult equals the paper-log HDResult
   `0.06536811590194702`.
3. Analyze why this route is slower than the exact 16-source oracle before
   attempting all-source execution.

Any next step must keep the Level-B boundary until exact input bytes or hashes
are proved.
