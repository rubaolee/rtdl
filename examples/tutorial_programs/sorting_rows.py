from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sort_kernel():
    probes = rt.input("probes", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    keys = rt.input("keys", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(probes, keys, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id"])


def make_case(values: tuple[int, ...] | list[int]) -> dict[str, tuple[rt.Segment, ...]]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError("this tutorial supports only nonnegative integers")
    far_x = max(normalized, default=0) + 1
    probes = []
    keys = []
    for index, value in enumerate(normalized):
        probes.append(
            rt.Segment(
                id=index,
                x0=0.0,
                y0=float(value) + 0.5,
                x1=float(far_x),
                y1=float(value) + 0.5,
            )
        )
        keys.append(
            rt.Segment(
                id=index,
                x0=float(value),
                y0=0.0,
                x1=float(value),
                y1=float(value) + 1.0,
            )
        )
    return {"probes": tuple(probes), "keys": tuple(keys)}


def expected_hit_counts(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    by_value = Counter(normalized)
    running = 0
    count_by_value = {}
    for value in sorted(by_value, reverse=True):
        running += by_value[value]
        count_by_value[value] = running
    return tuple(count_by_value[value] for value in normalized)


def hit_counts_from_rows(row_count: int, rows: tuple[dict[str, object], ...]) -> tuple[int, ...]:
    counts = [0] * row_count
    for row in rows:
        counts[int(row["left_id"])] += 1
    return tuple(counts)


def stable_sort_from_hit_counts(
    values: tuple[int, ...] | list[int],
    hit_counts: tuple[int, ...],
    *,
    descending: bool,
) -> tuple[int, ...]:
    records = tuple(
        {"value": int(value), "hit_count": int(hit_count), "original_index": index}
        for index, (value, hit_count) in enumerate(zip(values, hit_counts))
    )
    if descending:
        ordered = sorted(records, key=lambda row: (row["hit_count"], row["original_index"]))
    else:
        ordered = sorted(records, key=lambda row: (-row["hit_count"], row["original_index"]))
    return tuple(int(row["value"]) for row in ordered)


def stable_python_sort(values: tuple[int, ...] | list[int], *, descending: bool) -> tuple[int, ...]:
    indexed = tuple((index, int(value)) for index, value in enumerate(values))
    if descending:
        ordered = sorted(indexed, key=lambda item: (-item[1], item[0]))
    else:
        ordered = sorted(indexed, key=lambda item: (item[1], item[0]))
    return tuple(value for _, value in ordered)


def run(values: tuple[int, ...] | list[int], *, backend: str) -> dict[str, object]:
    normalized = tuple(int(value) for value in values)
    case = make_case(normalized)
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

    hit_counts = hit_counts_from_rows(len(normalized), rows)
    formula_counts = expected_hit_counts(normalized)
    ascending = stable_sort_from_hit_counts(normalized, hit_counts, descending=False)
    descending = stable_sort_from_hit_counts(normalized, hit_counts, descending=True)
    ascending_reference = stable_python_sort(normalized, descending=False)
    descending_reference = stable_python_sort(normalized, descending=True)
    if hit_counts != formula_counts:
        raise AssertionError(f"unexpected hit counts: {hit_counts} != {formula_counts}")
    if ascending != ascending_reference or descending != descending_reference:
        raise AssertionError("RTDL-derived order does not match stable Python sort")

    return {
        "status": "ok",
        "backend": backend,
        "values": normalized,
        "lesson_layer": "rtdl_kernel_relation",
        "v4_operator_surface": None,
        "v4_runtime_claim": "none; this lesson has no V4 sort or segment-intersection operator surface",
        "teaching_model": "values -> segment geometry -> hit rows -> hit counts -> stable sorted output",
        "restriction": "nonnegative integers only; this is a tutorial for RTDL lowering, not a general sorting library",
        "kernel": "rt.input -> rt.traverse -> rt.refine(segment_intersection) -> rt.emit",
        "hit_count_law": "hit_count(value_i) = number of input values >= value_i",
        "hit_counts": hit_counts,
        "ascending_from_hits": ascending,
        "descending_from_hits": descending,
        "ascending_python_sorted": ascending_reference,
        "descending_python_sorted": descending_reference,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL ray-hit sorting tutorial")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("values", nargs="*", type=int)
    args = parser.parse_args()
    values = tuple(args.values) if args.values else (3, 1, 4, 1, 5, 0, 2, 5)
    print(json.dumps(run(values, backend=args.backend), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
