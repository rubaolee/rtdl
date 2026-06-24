from __future__ import annotations

import argparse
import json

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sort_kernel():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    hits = rt.refine(
        rt.traverse(left, right, accel="bvh"),
        predicate=rt.segment_intersection(exact=False),
    )
    return rt.emit(hits, fields=["left_id", "right_id"])


def make_case(values: list[int]) -> dict[str, tuple[rt.Segment, ...]]:
    if any(value < 0 for value in values):
        raise ValueError("this demo supports only nonnegative integers")
    far_x = max(values, default=0) + 1
    left = tuple(
        rt.Segment(id=index, x0=0.0, y0=value + 0.5, x1=float(far_x), y1=value + 0.5)
        for index, value in enumerate(values)
    )
    right = tuple(
        rt.Segment(id=index, x0=float(value), y0=0.0, x1=float(value), y1=float(value + 1))
        for index, value in enumerate(values)
    )
    return {"left": left, "right": right}


def hit_counts(rows: tuple[dict[str, object], ...], size: int) -> list[int]:
    counts = [0] * size
    for row in rows:
        counts[int(row["left_id"])] += 1
    return counts


def sort_from_hits(values: list[int], counts: list[int], *, descending: bool) -> list[int]:
    indexed = list(enumerate(zip(values, counts)))
    if descending:
        indexed.sort(key=lambda item: (item[1][1], item[0]))
    else:
        indexed.sort(key=lambda item: (-item[1][1], item[0]))
    return [value for _, (value, _) in indexed]


def run(values: list[int], backend: str) -> dict[str, object]:
    case = make_case(values)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(ray_hit_sort_kernel, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(ray_hit_sort_kernel, **case)
    elif backend == "embree":
        rows = rt.run_embree(ray_hit_sort_kernel, **case)
    elif backend == "optix":
        rows = rt.run_optix(ray_hit_sort_kernel, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(ray_hit_sort_kernel, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")
    counts = hit_counts(rows, len(values))
    ascending = sort_from_hits(values, counts, descending=False)
    descending = sort_from_hits(values, counts, descending=True)
    ascending_python = sorted(values)
    descending_python = sorted(values, reverse=True)
    if ascending != ascending_python or descending != descending_python:
        raise AssertionError("RTDL result does not match Python sorting")
    return {
        "backend": backend,
        "values": values,
        "hit_counts": counts,
        "ascending_from_hits": ascending,
        "descending_from_hits": descending,
        "ascending_python_sorted": ascending_python,
        "descending_python_sorted": descending_python,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact RTDL sorting demo")
    parser.add_argument("--backend", default="cpu_python_reference")
    parser.add_argument("values", nargs="*", type=int)
    args = parser.parse_args()
    values = args.values or [3, 1, 4, 1, 5, 0, 2, 5]
    print(json.dumps(run(values, args.backend), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
