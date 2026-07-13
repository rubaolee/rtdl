# Goal5153 - Vectorized Nearest-Cell-MBR Seed Result

## Verdict

`completed_vectorized_nearest_cell_mbr_seed`

## What Changed

Goal5153 keeps the Goal5152 public API:

```text
seed_nearest_witness_from_nearest_cell_mbr_numpy_columns
```

but changes the internal nearest-cell-MBR selection from a Python nested
query-by-cell loop to NumPy vectorized point-to-AABB lower-bound distance
matrices. Tie-breaking remains deterministic: nearest lower-bound distance,
then lower cell id.

The route summaries now report:

```text
initial_cell_mbr_selection = numpy_vectorized_min_distance_then_cell_id
```

## Verification

Local regression:

```text
py -m unittest tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test

Ran 8 tests OK
```

POD regression:

```text
python3 -m unittest \
  tests.goal5152_nearest_cell_mbr_seed_pruning_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 5 tests OK
```

## Representative Sample256 Evidence

Local NumPy vectorized seeded route:

```text
matched = true
author_abs_diff = 2.6291111648868437e-09
rtdl_exact_abs_diff = 0.0
initial_cell_mbr_selection = numpy_vectorized_min_distance_then_cell_id
a_to_b total_candidate_distance_evaluations = 1197
b_to_a total_candidate_distance_evaluations = 1228
rtdl_route_sec = 0.7092482000589371
total_sec = 0.9821724998764694
```

POD OptiX vectorized seeded route:

```text
matched = true
backend = optix
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
author_abs_diff = 2.6291111648868437e-09
rtdl_exact_abs_diff = 0.0
initial_cell_mbr_selection = numpy_vectorized_min_distance_then_cell_id
a_to_b total_candidate_distance_evaluations = 1201
b_to_a total_candidate_distance_evaluations = 1237
rtdl_route_sec = 0.3735104948282242
total_sec = 0.47989489138126373
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_vectorized_numpy_summary.json
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_seeded_vectorized_optix_summary_pod.json
```

## Interpretation

Goal5153 converts Goal5152's work reduction into a more credible route
improvement. The candidate point-distance work stays around 1,200 per direction
instead of 65,536, and the POD OptiX route time in this single run is about
0.37s route / 0.48s total.

This still is not a fair X-HD performance claim. The run is one representative
sample on one POD, not a matrix against author phases under aligned timing
boundaries. The route also still has Python/NumPy seed and continuation pieces.

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author fused RT-core algorithm equivalence;
- author performance parity;
- a final performance matrix.

It proves a generic vectorized seed path that preserves correctness and moves
the representative route materially closer to a performance-relevant shape.
