# Goal5150 - X-HD Cell-MBR Frontier Route Gate Result

## Verdict

`completed_bounded3d_xhd_cell_mbr_frontier_route_gate`

## What Changed

Goal5150 adds a bounded X-HD route gate that connects the generic system pieces
from Goals5138-5149 into an executable same-input route:

```text
point_grid_cell_mbrs_numpy_columns
  -> cell_mbr_nearest_frontier_{numpy|native_3d_optix}_columns
  -> nearest_witness_from_cell_mbr_frontier_numpy_columns
  -> max_nearest_distance_witness_numpy_columns
```

The gate lives in:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

It currently supports bounded 3-D inputs. It is not a full author X-HD RT-core
implementation: the native OptiX part produces generic cell-MBR frontier rows,
and the final nearest-witness continuation still runs as a generic partner
continuation outside the native shader.

## Local NumPy Evidence

Command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py \
  --input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_a.wkt \
  --input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_b.wkt \
  --n-dims 3 \
  --input-type wkt \
  --backend numpy \
  --grid-shape 2,1,1 \
  --author-json Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json \
  --summary Paper-reproduction-apps/x-hd-paper/results/bounded3d_cell_mbr_frontier_route_numpy_summary.json
```

Result:

```text
schema = rtdl.paper_reproduction.xhd.cell_mbr_frontier_route_gate.v1
backend = numpy
matched = true
author_hd_result = 2.0
author_comparison_reference = directed_a_to_b
author_comparison_distance = 2.0
rtdl_matches_exact_reference = true
rtdl_exact_abs_diff = 0.0
directed_a_to_b.distance = 2.0
directed_b_to_a.distance = 0.1
hausdorff = 2.0
```

Local tests:

```text
py -m unittest tests.goal5150_xhd_cell_mbr_frontier_route_gate_test \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test

Ran 8 tests OK
```

## POD OptiX Evidence

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD regression:

```text
python3 -m unittest \
  tests.goal5149_cell_mbr_frontier_nearest_continuation_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 5 tests OK
```

POD route:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py \
  --input1 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_a.wkt \
  --input2 Paper-reproduction-apps/x-hd-paper/data/fixtures/bounded3d_b.wkt \
  --n-dims 3 \
  --input-type wkt \
  --backend optix \
  --grid-shape 2,1,1 \
  --author-json Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json \
  --summary Paper-reproduction-apps/x-hd-paper/results/bounded3d_cell_mbr_frontier_route_optix_summary_pod.json
```

Result:

```text
backend = optix
matched = true
author_hd_result = 2.0
author_comparison_distance = 2.0
rtdl_matches_exact_reference = true
rtdl_exact_abs_diff = 0.0
directed_a_to_b.frontier_contract = generic_cell_mbr_nearest_frontier_native_3d_optix
directed_a_to_b.frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
directed_a_to_b.frontier_row_count = 18
directed_a_to_b.candidate_distance_evaluations = 72
directed_b_to_a.frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d
directed_b_to_a.frontier_row_count = 16
```

Evidence file:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_cell_mbr_frontier_route_optix_summary_pod.json
```

## Claim Boundary

This goal proves a bounded same-input route that uses generic RTDL APIs and a
generic native 3-D OptiX frontier producer.

It does not prove:

- full X-HD paper reproduction;
- exact paper dataset reproduction;
- author fused RT-core algorithm equivalence;
- performance parity or speedup;
- complete 2-D/3-D Goal5140 native ABI backend.

The route uses the native OptiX frontier producer, but the nearest-witness
continuation still runs as a generic partner continuation after frontier rows.
That remaining boundary is the next algorithmic gap if the objective is to
approach the author's fused X-HD RT-core.
