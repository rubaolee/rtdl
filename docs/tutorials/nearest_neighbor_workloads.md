# Tutorial: Nearest-Neighbor Workloads

This tutorial covers the active `v0.4` nearest-neighbor line.

Current public workloads:

- `fixed_radius_neighbors`
- `knn_rows`

These are released v0.4.0 features.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`

## What You Will Learn

- how to write and run the current nearest-neighbor workloads
- when to choose radius-based output versus top-`k` output
- how the same workload can grow into a small RTDL-plus-Python application

## Start With `fixed_radius_neighbors`

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

This workload answers:

- which search points fall within radius `r` of each query point?

It emits:

- `query_id`
- `neighbor_id`
- `distance`

Use it when you want:

- service-radius screening
- local density row materialization
- bounded neighborhood joins

## Then Learn `knn_rows`

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend cpu_python_reference
```

This workload answers:

- what are the nearest `k` search points for each query point?

It emits:

- `query_id`
- `neighbor_id`
- `distance`
- `neighbor_rank`

Use it when you want:

- top-`k` facility matching
- graph-edge candidate generation
- deterministic nearest-neighbor row output

## Backend Progression

Once the CPU truth path is clear, the same public example programs can be run
on:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend embree
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend embree
```

Honest boundary:

- the public top-level nearest-neighbor example CLIs currently expose:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
- OptiX and Vulkan nearest-neighbor closure exists in the runtime and test
  surface, but those backend values are not exposed through these two public
  example CLIs yet
- Embree is the current accelerated backend available through the public
  nearest-neighbor examples

## Application-Shaped Examples

After the bare workload examples, move to:

- [examples/rtdl_service_coverage_gaps.py](../../examples/rtdl_service_coverage_gaps.py)
- [examples/rtdl_event_hotspot_screening.py](../../examples/rtdl_event_hotspot_screening.py)
- [examples/rtdl_facility_knn_assignment.py](../../examples/rtdl_facility_knn_assignment.py)

These teach the intended composition model:

- RTDL does the neighbor query
- Python does grouping, summaries, and app-specific decisions

See also:

- [RTDL v0.4 Application Examples](../v0_4_application_examples.md)

## Next Pages

For exact frozen contracts:

- [Fixed-Radius Neighbors Feature Home](../features/fixed_radius_neighbors/README.md)
- [KNN Rows Feature Home](../features/knn_rows/README.md)

For app/demo composition:

- [RTDL Plus Python Rendering](rendering_and_visual_demos.md)
