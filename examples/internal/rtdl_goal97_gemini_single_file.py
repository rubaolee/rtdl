from __future__ import annotations

import argparse
import json

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sort_kernel():
    """RTDL kernel to find intersections between horizontal and vertical segments."""
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    hits = rt.refine(
        rt.traverse(left, right, accel="bvh"),
        predicate=rt.segment_intersection(exact=False),
    )
    return rt.emit(hits, fields=["left_id", "right_id"])


def main() -> int:
    """
    A compact, single-file demonstration of using RTDL for sorting.

    This script takes a list of integers, represents them as geometric segments,
    and uses the number of ray-tracing intersections to sort the original list.
    The result is verified against Python's built-in sorting.
    """
    parser = argparse.ArgumentParser(
        description="Compact RTDL Goal 97 demo (Gemini variant)"
    )
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("values", nargs="*", type=int)
    args = parser.parse_args()

    values = args.values or [3, 1, 4, 1, 5, 9, 2, 6]
    if any(v < 0 for v in values):
        raise ValueError("This demo supports only non-negative integers.")

    # --- Geometry Generation ---
    # Create horizontal segments for 'left' and vertical for 'right'.
    # The number of intersections a 'left' segment gets is proportional to its value.
    far_x = max(values, default=0) + 1
    case = {
        "left": tuple(
            rt.Segment(id=i, x0=0.0, y0=v + 0.5, x1=float(far_x), y1=v + 0.5)
            for i, v in enumerate(values)
        ),
        "right": tuple(
            rt.Segment(id=i, x0=float(v), y0=0.0, x1=float(v), y1=float(v + 1.0))
            for i, v in enumerate(values)
        ),
    }

    # --- Kernel Execution ---
    try:
        run_func = getattr(rt, f"run_{args.backend}")
    except AttributeError:
        raise ValueError(f"Unsupported backend: {args.backend}") from None
    rows = run_func(ray_hit_sort_kernel, **case)

    # --- Sorting via Hit Counts ---
    counts = [0] * len(values)
    for row in rows:
        counts[int(row["left_id"])] += 1

    # Sort original values based on hit counts. A stable sort is used by sorting
    # indices and using the original index as a tie-breaker.
    indices = list(range(len(values)))
    ascending_indices = sorted(indices, key=lambda i: (counts[i], i))
    rtdl_ascending = [values[i] for i in ascending_indices]
    descending_indices = sorted(indices, key=lambda i: (-counts[i], i))
    rtdl_descending = [values[i] for i in descending_indices]

    # --- Verification and Output ---
    py_sorted_asc = sorted(values)
    py_sorted_desc = sorted(values, reverse=True)
    if rtdl_ascending != py_sorted_asc or rtdl_descending != py_sorted_desc:
        raise AssertionError("RTDL sort result does not match Python's sorted().")

    print(
        json.dumps(
            {
                "backend": args.backend,
                "values": values,
                "hit_counts": counts,
                "rtdl_ascending": rtdl_ascending,
                "rtdl_descending": rtdl_descending,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
