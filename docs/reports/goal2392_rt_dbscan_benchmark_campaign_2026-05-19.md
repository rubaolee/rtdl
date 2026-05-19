# Goal2392 RT-DBSCAN Benchmark Campaign

Date: 2026-05-19

Status: initial implementation slice and paper-grounded gap audit

## Paper

The target paper is:

- Vani Nagarajan and Milind Kulkarni, "RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware," IPDPS 2023.
- DOI: `10.1109/IPDPS54959.2023.00100`
- arXiv: `https://arxiv.org/abs/2303.09655`

The paper maps DBSCAN's fixed-radius neighbor queries onto ray tracing hardware.
Its abstract states that RT-DBSCAN translates DBSCAN fixed-radius nearest-neighbor
queries to ray tracing queries and reports 1.3x to 4x speedups over current
GPU DBSCAN implementations. The paper's algorithmic split matters for RTDL:

1. Convert points into fixed-radius query geometry.
2. Count or discover epsilon-neighborhoods to identify core points.
3. Build clusters through repeated neighbor/core reachability.

The important design lesson is that DBSCAN is not an app-specific native
function. It is a composition of generic contracts:

```text
3-D fixed-radius neighbor traversal
3-D fixed-radius count/threshold columns
radius-graph component labels
device-resident grouped continuation / union-find
```

## What Changed

This goal starts upgrading DBSCAN from a small app/demo into a serious research
benchmark app:

- Added `examples/v2_0/research_benchmarks/rt_dbscan/README.md`.
- Added `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`.
- Added the study to `examples/v2_0/research_benchmarks/README.md`.
- Added `scripts/goal2392_rt_dbscan_pod_runner.sh` for progress-logged
  NVIDIA timing collection.
- Extended `point_rows_to_partner_columns(...)` so 3-D points preserve a `z`
  partner column.
- Added generic partner 3-D fixed-radius count/threshold columns:
  `fixed_radius_count_threshold_3d_partner_columns(...)`.
- Added generic partner 3-D spatial-bucket radius-graph component labels:
  `radius_graph_components_3d_spatial_bucket_partner_columns(...)`.
- Added a generic CuPy device-grid 3-D radius-graph component baseline:
  `radius_graph_components_3d_cupy_grid_partner_columns(...)`.

No DBSCAN-specific native ABI was added.

## Current Benchmark Modes

| Mode | Purpose | Release claim boundary |
| --- | --- | --- |
| `cpu_reference` | Exact CPU spatial-bucket DBSCAN reference | Correctness oracle only |
| `rtdl_cpu_rows` | Generic RTDL 3-D fixed-radius rows plus Python component labels | Same contract, no GPU claim |
| `partner_spatial_bucket_3d` | Generic 3-D radius-graph components over partner columns | Full labels, but host-built bucket index |
| `partner_cupy_grid_components_3d` | Generic CuPy device-grid radius-graph components | Strong CUDA-core baseline, no RT-core claim |
| `partner_core_flags_3d` | Generic 3-D fixed-radius core flags | Core-point phase only, not full DBSCAN |
| `optix_prepared_rows` | Prepared OptiX 3-D fixed-radius rows plus Python component labels | RT-core path, but materializes rows |

## Initial Local Evidence

The CPU-only smoke path now runs without OptiX or partner packages:

```text
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode cpu_reference --dataset tiny --include-rows
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode rtdl_cpu_rows --dataset tiny --include-rows
```

The unit test for this goal verifies:

- the new benchmark directory and README are present;
- no DBSCAN-specific native ABI is introduced;
- the CPU reference and generic RTDL CPU row path match on the tiny fixture;
- the new 3-D partner primitives are exported and documented.

## Current Design Gap

The current RTDL stack is closer to RT-DBSCAN than the old demo, but not yet at
the paper's implementation level.

What RTDL has:

- generic 3-D fixed-radius neighbor rows across the native engine surface;
- prepared OptiX 3-D fixed-radius neighbor row execution;
- aggregate prepared OptiX 3-D fixed-radius summaries;
- 2-D OptiX device-column count/threshold handoff;
- exact 2-D and now 3-D partner radius-graph component labeling.
- a first generic CuPy device-grid 3-D radius-graph component baseline.

What RTDL still needs for a serious RT-DBSCAN fight:

- first-class 3-D OptiX device-column count/threshold handoff, analogous to the
  existing 2-D path;
- a reusable device-resident radius-graph component continuation that can accept
  OptiX-produced device rows/counts without materializing all neighbor rows or
  building the sparse bucket index on the host;
- representative paper-style datasets and a reviewed pod timing protocol;
- comparison against the new CuPy device-grid baseline on the same datasets.

## Next Pod Target

When an NVIDIA pod is available, run:

```text
bash scripts/goal2392_rt_dbscan_pod_runner.sh
```

The runner records the commit, CUDA/driver probe, CPU correctness smoke, CuPy
partner rows when CuPy is available, and OptiX prepared-row rows when
`RTDL_OPTIX_LIBRARY` or `OPTIX_PREFIX` is configured. That will not be enough
for a paper-level claim. It is the first same-dataset sanity check before
implementing the stronger 3-D device-column and device-resident continuation
primitives.

## Verdict

Goal2392 is an `accept-with-boundary` implementation slice:

- Accept: DBSCAN is now represented as a research benchmark with generic 3-D
  contracts and an explicit paper-grounded gap list.
- Boundary: this is not yet a full RT-DBSCAN reproduction, not a paper-speedup
  claim, and not evidence that RTDL beats FDBSCAN or CUDA DBSCAN.
