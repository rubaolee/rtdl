# Goal5204 Linear Max-Nearest Reduction Result

Date: 2026-07-08

## Verdict

```text
completed_linear_max_nearest_reduction__small_generic_reducer_floor_removed
```

## Purpose

After Goal5203 removed the public PLY tuple-row / matrix repack path, the
remaining full-public Dragon -> HappyBuddha Level-B route profile was:

```text
route_wall ~= 1.238-1.239s
frontier_rows ~= 0.74s
initial_state_seed ~= 0.23s
max_nearest_reduction ~= 0.072s
```

Goal5204 attacks the generic max-nearest reduction. Before this goal,
`max_nearest_distance_witness_numpy_columns(...)` used a full
`np.lexsort((item_ids, group_ids, -distances))` over every row to return one
winner. That is correct but unnecessarily O(n log n) for the common finite case
where the maximum distance has a single winner.

## Implementation

Changed `src/rtdsl/partner_continuations.py`:

- finite distances: compute `max(distances)` in O(n);
- sort only rows exactly tied for the maximum;
- preserve the existing tie-break semantics:
  - maximum nearest distance;
  - then smallest group/source index;
  - then smallest nearest item id;
- non-finite distances: fall back to the previous full-lexsort path;
- expose metadata:
  - `reduction_strategy`;
  - `tie_candidate_count`.

Changed `run_xhd_cell_mbr_frontier_route_gate.py` and
`run_xhd_full_public_subset_scaling_gate.py` to surface this metadata in the
paper-app route summary. This makes the artifact self-verifying.

No X-HD-specific RTDL primitive was added. This is a generic reducer
optimization.

## Validation

Local:

```text
py -m unittest \
  tests.goal5204_max_nearest_linear_reduction_test \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5187_xhd_full_public_route_only_gate_test

Ran 19 tests OK

py_compile = OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

python -m unittest \
  tests.goal5204_max_nearest_linear_reduction_test \
  tests.goal5203_numpy_point_matrix_input_loader_test \
  tests.goal5127_xhd_generic_nearest_pipeline_extraction_test \
  tests.goal5128_non_hausdorff_max_nearest_consumer_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5187_xhd_full_public_route_only_gate_test

Ran 19 tests OK
```

The first POD attempt lacked `tests.goal5127...` and `tests.goal5128...`; those
historical tests were uploaded and the final 19-test run passed.

## Full-Public Evidence

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5204_linear_max_reduction_final2_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5204_linear_max_reduction_final3_graphics_dragon_happy_buddha_2026-07-08.json
```

Both full-public Dragon -> HappyBuddha Level-B runs:

```text
all_matched = true
author_abs_diff ~= 2.3849e-9
max_reduction_strategy = finite_max_then_tie_lexsort
max_tie_candidate_count = 1
```

Final2:

```text
route_wall ~= 1.172s
case_total ~= 1.387s
initial_state_seed ~= 0.224s
frontier_rows ~= 0.753s
max_nearest_reduction ~= 0.00083s
```

Final3 confirmation:

```text
route_wall ~= 1.183s
case_total ~= 1.398s
initial_state_seed ~= 0.231s
frontier_rows ~= 0.756s
max_nearest_reduction ~= 0.00066s
```

Comparison to Goal5203:

```text
Goal5203 route_wall             ~= 1.238-1.239s
Goal5204 route_wall             ~= 1.172-1.183s

Goal5203 max_nearest_reduction  ~= 0.072s
Goal5204 max_nearest_reduction  ~= 0.0007-0.0008s
```

A prior Goal5204 run before warmup had `initial_state_seed ~= 4.47s` from
cold/JIT seed noise. It matched correctness and proved the reducer movement,
but is not used as a route headline.

## Claim Boundary

This goal claims:

- a generic max-nearest reducer improvement;
- route-local Level-B improvement on the public Dragon -> HappyBuddha route;
- continued correctness against the Goal5186 author HDResult.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- X-HD-specific RTDL primitive;
- native backend completion beyond the existing route.

## Next

After Goal5204, the solved costs are:

```text
source+target columns ~= 0.001-0.002s
max_nearest_reduction ~= 0.001s
```

The remaining route-local floor is now dominated by:

```text
frontier_rows ~= 0.75s
initial_state_seed ~= 0.23s
grid_cell_mbrs ~= 0.10s
input loading ~= 1.68s outside route wall
```

The next meaningful route work is not max-reduction, tuple repacking, scalar
ray `tmax`, or accel-build caching. It should either attack the generic native
inline-nearest/frontier execution model and work ordering, or pause for
review/provenance/figure planning.
