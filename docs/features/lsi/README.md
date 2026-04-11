# Line-Segment Intersection (LSI)

## Purpose

`lsi` is RTDL's line-segment intersection workload.

Use it when both sides of the query are segment sets and you want one emitted
row per accepted segment/segment intersection.

## Docs

- canonical kernel pattern:
  - [rtdl_language_reference.py](../../../examples/reference/rtdl_language_reference.py)
- language contracts:
  - [dsl_reference.md](../../rtdl/dsl_reference.md)
  - [workload_cookbook.md](../../rtdl/workload_cookbook.md)

Kernel shape:

```python
left = rt.input("left", rt.Segments, role="probe")
right = rt.input("right", rt.Segments, role="build")
candidates = rt.traverse(left, right, accel="bvh")
hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
return rt.emit(
    hits,
    fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
)
```

## Code

- predicate:
  - `rt.segment_intersection(exact=False)`
- canonical reference kernel:
  - [county_zip_join_reference](../../../examples/reference/rtdl_language_reference.py)

## Example

Start here:

- [rtdl_language_reference.py](../../../examples/reference/rtdl_language_reference.py)

Run from the repository root:

```bash
python examples/reference/rtdl_language_reference.py
```

Use `python3` instead if that is what your shell exposes.

This file contains the current minimal language-reference `lsi` kernel.

## Best Practices

- use `Segments` on both sides and keep roles explicit
- treat `lsi` as a row-materialization workload, not an aggregate
- validate new kernels through `rt.run_cpu(...)` before backend comparisons
- compare accepted larger packages against PostGIS on Linux when the goal is external correctness

## Try

- road/boundary crossing joins
- segment/segment audit rows
- exact-follow-up pipelines where the output row ids matter

## Try Not

- nearest-neighbor tasks
- polygon containment tasks
- pretending `lsi` alone closes segment-vs-polygon semantics

## Limitations

- current implementation is float-based, not exact arithmetic
- backend maturity is not uniform across every historical package
- this feature is part of the accepted RTDL surface, but the strongest public-facing live v0.2 stories are the newer segment/polygon families
