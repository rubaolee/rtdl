# Goal4785 Restore Goal97 Sorting Tutorial

Status: `implemented_pending_antigravity_review`

Goal4785 restores the original Goal97 ray-hit sorting example as the second V4
tutorial lesson. This replaces the unreviewed planner/predecessor-row rewrite
that was incorrectly left in `examples/tutorial_programs/sorting_rows.py`.

## Decision

Use the original Goal97 design:

```text
values -> segment geometry -> segment-intersection hit rows -> hit counts -> stable sorted output
```

Do not use:

```text
planner/catalog lookup
```

Do not use:

```text
generic predecessor-row story with no real RTDL kernel
```

## Historical Source

The restored design comes from the archived Goal97 assets:

```text
tools/_archive/history/legacy_project_archive_2026-06-24/examples/internal/rtdl_sorting_single_file.py
tools/_archive/history/legacy_project_archive_2026-06-24/examples/internal/rtdl_sorting.py
tools/_archive/history/tutorial_archive/sorting_demo.md
tools/_archive/history/legacy_project_archive_2026-06-24/docs/reports/goal97_ray_hit_sorting_kernel_2026-04-05.md
```

Goal97 had already validated the accepted duplicate-containing case:

```text
values:      (3, 1, 4, 1, 5, 0, 2, 5)
hit counts:  (4, 7, 3, 7, 2, 8, 5, 2)
ascending:   (0, 1, 1, 2, 3, 4, 5, 5)
descending:  (5, 5, 4, 3, 2, 1, 1, 0)
```

## Files Changed

| File | Action |
| --- | --- |
| `examples/tutorial_programs/sorting_rows.py` | Replaced the unreviewed planner/predecessor rewrite with the Goal97 ray-hit sorting kernel. |
| `tutorials/current/03_sorting_rows.md` | Rewrote the second lesson around segment geometry, hit rows, hit counts, and rank. |
| `examples/tutorial_programs/README.md` | Updated the sorting row description to match the restored example. |
| `docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md` | Updated the lesson plan to preserve Goal97 rather than inventing a new sorting story. |

## Current Kernel

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sort_kernel():
    probes = rt.input("probes", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    keys = rt.input("keys", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(probes, keys, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id"])
```

## Teaching Boundary

This lesson teaches:

- how to encode a non-obvious problem as geometry;
- how `traverse/refine/emit` carries over from hello world;
- how RTDL rows become a rank signal;
- how Python can own the surrounding application logic.

This lesson does not claim:

- RTDL is a general sorting library;
- RT cores should replace ordinary sort for arbitrary comparators;
- this is a performance benchmark;
- negative integers or arbitrary keys are supported by this tutorial program.

## Linux Verification

Validation ran on local Linux `192.168.1.20`, in:

```text
/tmp/rtdl_goal4783_check
```

Commands:

```bash
cd /tmp/rtdl_goal4783_check
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py --backend cpu_python_reference 3 1 4 1 5 0 2 5
PYTHONPATH=src:. python3 examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python3 -m py_compile examples/tutorial_programs/sorting_rows.py
grep -R -n 'ray_hit_sort_kernel\|segment-intersection\|hit counts as rank\|ascending_from_hits\|RTDL sorting demo' \
  tutorials/current/03_sorting_rows.md \
  examples/tutorial_programs/sorting_rows.py \
  examples/tutorial_programs/README.md
```

Observed output included:

```json
{
  "values": [3, 1, 4, 1, 5, 0, 2, 5],
  "hit_counts": [4, 7, 3, 7, 2, 8, 5, 2],
  "ascending_from_hits": [0, 1, 1, 2, 3, 4, 5, 5],
  "descending_from_hits": [5, 5, 4, 3, 2, 1, 1, 0],
  "ascending_python_sorted": [0, 1, 1, 2, 3, 4, 5, 5],
  "descending_python_sorted": [5, 5, 4, 3, 2, 1, 1, 0]
}
```

`py_compile` passed.

## Goal-Level Decision Check

1. Did I make a stupid decision?
   - Yes, earlier. I replaced the Goal97 design without first reading the
     archive.
2. What action made it stupid?
   - Treating a new abstract predecessor-row/planner story as better than the
     already validated ray-hit sorting kernel.
3. Was there another path?
   - Yes: restore Goal97, modernize only paths and wording, then validate.
4. Did I switch to the better path?
   - Yes. The current tutorial now inherits Goal97 and validates on Linux.

## Non-Authorization

This does not authorize:

- claiming the whole tutorial ladder is complete;
- claiming sorting performance;
- treating this as a general sorting API;
- skipping nearest-neighbor, partner, continuation, or benchmark bridge goals.
