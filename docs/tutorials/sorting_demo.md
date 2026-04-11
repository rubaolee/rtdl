# Tutorial: Sorting Demo

This demo shows how RTDL acts as a geometric engine inside an ordinary Python
program. The final output is a sorted list. The ranking signal comes from RTDL.

This is not a claim that RTDL should replace Python sorting. It is a compact
demonstration that RTDL query results can drive arbitrary downstream Python
logic.

---

## Run it

```bash
PYTHONPATH=src:. python scripts/rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

Expected output excerpt:

```json
{
  "backend": "cpu_python_reference",
  "values": [3, 1, 4, 1, 5, 0, 2, 5],
  "ascending_from_hits": [0, 1, 1, 2, 3, 4, 5, 5],
  "descending_from_hits": [5, 5, 4, 3, 2, 1, 1, 0]
}
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python scripts\rtdl_sorting_demo.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

---

## How it works

The key geometric trick is:

- a horizontal ray at height `y`
- intersects all vertical segments whose `x` position is `<= y`

That means hit count becomes rank.

For input values `[3, 1, 4, ...]`, the program constructs:

- one horizontal ray per input value
- one vertical segment per input value

Each ray hits the segments corresponding to values less than or equal to that
ray's level. Python then reconstructs ascending and descending order from those
counts.

---

## The Python/RTDL split

RTDL handles the geometric query:

```python
rows = rt.run_cpu_python_reference(sort_kernel, rays=rays, segments=segments)
```

Python does the rest:

- counting hits
- reconstructing rank
- sorting the original values
- comparing against the ordinary Python reference sort

That is the important lesson. RTDL returns rows; Python can do anything with
those rows.

---

## Main files

- [scripts/rtdl_sorting_demo.py](../../scripts/rtdl_sorting_demo.py)
- [examples/internal/rtdl_sorting.py](../../examples/internal/rtdl_sorting.py)
- [examples/internal/rtdl_sorting_single_file.py](../../examples/internal/rtdl_sorting_single_file.py)
- [tests/rtdl_sorting_test.py](../../tests/rtdl_sorting_test.py)

---

## Why it belongs in the tutorials

Beginners usually need two separate lessons:

- how to write a workload kernel
- how RTDL can sit inside a larger Python program

The sorting demo is mainly for the second lesson.

---

## Next

- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
