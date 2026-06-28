# Sorting Rows

This is a V4 tutorial-path lesson for the RTDL language layer. It restores the
original ray-hit sorting demo, but it is not a claim that RTDL should replace
ordinary Python sorting. It teaches a more important skill: how to turn a
non-obvious problem into an RTDL geometric query.

Boundary: this lesson has no V4 sorting operator surface and no V4 segment-intersection runtime surface. It is here because V4 includes the current
RTDL kernel/relation language path, not because V4 exposes a `sort` operator.

The input is a list of nonnegative integers:

```text
3 1 4 1 5 0 2 5
```

The RTDL trick is geometric:

- make one horizontal probe segment for each value;
- make one vertical key segment for each value;
- a probe for value `v` hits every key segment whose value is `>= v`;
- therefore the hit count becomes a rank signal.

The kernel uses the same RTDL shape you saw in hello world:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sort_kernel():
    probes = rt.input("probes", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    keys = rt.input("keys", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(probes, keys, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id"])
```

Read it as:

1. `probes` are horizontal segments made from the input values.
2. `keys` are vertical segments made from the same values.
3. `rt.traverse(...)` finds candidate segment pairs.
4. `rt.refine(... segment_intersection ...)` keeps real intersections.
5. `rt.emit(...)` returns hit rows.

Python then counts hits per probe and reconstructs a stable ascending or
descending order.

## Run It

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\sorting_rows.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
```

Expected output excerpt:

```json
{
  "values": [3, 1, 4, 1, 5, 0, 2, 5],
  "hit_counts": [4, 7, 3, 7, 2, 8, 5, 2],
  "ascending_from_hits": [0, 1, 1, 2, 3, 4, 5, 5],
  "descending_from_hits": [5, 5, 4, 3, 2, 1, 1, 0]
}
```

## What You Should Learn

- RTDL can help when a ranking signal can be expressed as hits or relation rows.
- The RTDL part is the geometric query: `input -> traverse -> refine -> emit`.
- Python can still own the ordinary program logic after rows are emitted.
- A V4 tutorial can be a language-layer lesson without having a V4 operator
  surface.
- This tutorial is intentionally restricted to nonnegative integers.
- For arbitrary comparators, use ordinary sorting instead of pretending it is
  an RT-core problem.

Next: [Relations And Operators](04_relations_and_operators.md)
