# Point/Nearest Segment

## Purpose

`point_nearest_segment` maps each probe point to its nearest segment and emits a
distance row.

Use it when you want nearest-road, nearest-boundary, or nearest-line style
answers and do not need full k-nearest search.

## Docs

- canonical kernel pattern:
  - [rtdl_workload_reference.py](../../../examples/reference/rtdl_workload_reference.py)
- language contracts:
  - [dsl_reference.md](../../rtdl/dsl_reference.md)
  - [workload_cookbook.md](../../rtdl/workload_cookbook.md)

Kernel shape:

```python
points = rt.input("points", rt.Points, role="probe")
segments = rt.input("segments", rt.Segments, role="build")
candidates = rt.traverse(points, segments, accel="bvh")
nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])
```

## Code

- predicate:
  - `rt.point_nearest_segment(exact=False)`
- canonical reference kernel:
  - [point_nearest_segment_reference](../../../examples/reference/rtdl_workload_reference.py)

## Example

Start here:

- [rtdl_workload_reference.py](../../../examples/reference/rtdl_workload_reference.py)

Run from the repository root:

```bash
python examples/reference/rtdl_workload_reference.py
```

Use `python3` instead if that is what your shell exposes.

That file includes both authored and fixture-backed helper cases for this
feature family.

## Best Practices

- use stable point and segment ids so downstream nearest rows stay auditable
- validate with `rt.run_cpu(...)` first
- keep expectations modest: this is a supported workload, but not the current main release story

## Try

- nearest road to hydrant
- nearest boundary to event point
- compact point-to-line attachment rows

## Try Not

- k-nearest search
- polygon overlap or containment tasks
- overclaiming backend maturity beyond the accepted validated surfaces

## Limitations

- current implementation is float-based
- this family is supported, but its documentation and validation surface are lighter than the newer segment/polygon families
- current examples live inside shared reference files rather than a large standalone app example
