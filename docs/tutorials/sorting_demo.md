# Tutorial: Sorting Demo

This tutorial is for the question:

- can RTDL be used for a compact programmable demo, not only named workload
  families?

The answer is yes, but with an honesty boundary:

- this is a tutorial/demo path
- it is not a release-facing workload family like `segment_polygon_hitcount` or
  `fixed_radius_neighbors`

## What You Will Learn

- how RTDL can be embedded in a small Python program
- how Python can own comparison/reference logic around an RTDL kernel
- how a nonstandard demo still follows the same RTDL execution shape

## Run It

From the repo root:

```bash
PYTHONPATH=src:. python3 scripts/rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python scripts\rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

## What The Program Shows

The sorting demo uses RTDL-derived hit counts as an ordering signal, then the
Python layer reconstructs ascending and descending sequences and compares them
to ordinary Python reference sorts.

The point is not that RTDL should replace Python sorting.

The point is:

- RTDL can serve as the geometric/query engine inside a larger Python program
- Python can validate, transform, and present the final result

## Main Files

- public demo script:
  - [scripts/rtdl_sorting_demo.py](../../scripts/rtdl_sorting_demo.py)
- supporting tutorial example:
  - [examples/internal/rtdl_sorting.py](../../examples/internal/rtdl_sorting.py)
- compact single-file variant:
  - [examples/internal/rtdl_sorting_single_file.py](../../examples/internal/rtdl_sorting_single_file.py)
- tests:
  - [tests/rtdl_sorting_test.py](../../tests/rtdl_sorting_test.py)

## Why It Belongs In The Tutorials

Beginners usually need two different lessons:

1. how to use RTDL’s named workload surface
2. how RTDL fits inside a normal Python program

The sorting demo teaches the second lesson in a small, readable way.

## Next Tutorial

For released workload-family examples, go to:

- [Segment And Polygon Workloads](segment_polygon_workloads.md)

For the active nearest-neighbor line, go to:

- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
