# Goal5151 - X-HD Sample256 Cell-MBR Frontier Route Gate Result

## Verdict

`completed_representative_sample256_cell_mbr_frontier_route_gate`

## What Changed

Goal5151 runs the Goal5150 cell-MBR frontier route on the existing Level B
Stanford graphics sample256 same-source fixture:

```text
input1 = stanford_dragon_res4_sample256.ply
input2 = stanford_happy_res4_sample256.ply
preprocessing = translate_each_input_to_min_bound
```

The route remains:

```text
point_grid_cell_mbrs_numpy_columns
  -> cell_mbr_nearest_frontier_{numpy|native_3d_optix}_columns
  -> nearest_witness_from_cell_mbr_frontier_numpy_columns
  -> max_nearest_distance_witness_numpy_columns
```

## Local NumPy Evidence

Evidence file:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_route_numpy_summary.json
```

Key values:

```text
matched = true
backend = numpy
author_hd_result = 0.11612465232610703
author_comparison_reference = directed_a_to_b
author_comparison_distance = 0.11612464969699586
author_abs_diff = 2.6291111648868437e-09
rtdl_matches_exact_reference = true
rtdl_exact_abs_diff = 0.0
candidate_distance_evaluations = 65536 in each directed pass
```

## POD OptiX Evidence

Evidence file:

```text
Paper-reproduction-apps/x-hd-paper/results/stanford_graphics_sample256_cell_mbr_frontier_route_optix_summary_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Key values:

```text
matched = true
backend = optix
author_hd_result = 0.11612465232610703
author_comparison_reference = directed_a_to_b
author_comparison_distance = 0.11612464969699586
author_abs_diff = 2.6291111648868437e-09
rtdl_matches_exact_reference = true
rtdl_exact_abs_diff = 0.0
directed_a_to_b.frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
directed_b_to_a.frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
directed_a_to_b.frontier_row_count = 40192
directed_b_to_a.frontier_row_count = 38912
candidate_distance_evaluations = 65536 in each directed pass
```

## Interpretation

This is the first representative Stanford sample route using the generic native
3-D cell-MBR frontier producer. It proves that the bounded route shape survives
the move from tiny WKT fixtures to a same-source PLY sample that has an existing
author `hd_exec` JSON.

It is not a performance win. With the current full-cover radius and partner
nearest-witness continuation, the route still evaluates every source-target
pair:

```text
256 * 256 = 65536
```

The next algorithmic gap is not "can the native frontier row producer match?"
but "can the nearest-state/radius/offload loop prune work before the partner
continuation scans all points?"

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author fused RT-core algorithm equivalence;
- performance parity or speedup;
- completion of the full 2-D/3-D Goal5140 native ABI backend.

It is Level B representative correctness evidence for the generic cell-MBR
frontier route.
