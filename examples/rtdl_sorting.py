from __future__ import annotations

from collections import Counter

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_hit_sorting_reference():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


def make_ray_hit_sort_case(values: tuple[int, ...] | list[int], *, far_x: int | None = None) -> dict[str, tuple[rt.Segment, ...]]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError("this example currently supports only nonnegative integers")
    max_value = max(normalized, default=0)
    final_x = max_value + 1 if far_x is None else int(far_x)
    if final_x <= max_value:
        raise ValueError("far_x must be greater than the maximum input value")

    left = []
    right = []
    for index, value in enumerate(normalized):
        y = float(value) + 0.5
        x = float(value)
        left.append(rt.Segment(id=index, x0=0.0, y0=y, x1=float(final_x), y1=y))
        right.append(rt.Segment(id=index, x0=x, y0=0.0, x1=x, y1=float(value) + 1.0))
    return {"left": tuple(left), "right": tuple(right)}


def expected_hit_counts(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError("this example currently supports only nonnegative integers")
    by_value = Counter(normalized)
    running = 0
    hit_map: dict[int, int] = {}
    for value in sorted(by_value, reverse=True):
        running += by_value[value]
        hit_map[value] = running
    return tuple(hit_map[value] for value in normalized)


def hit_counts_from_rows(values: tuple[int, ...] | list[int], rows: tuple[dict[str, object], ...]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    counts = [0] * len(normalized)
    for row in rows:
        left_id = int(row["left_id"])
        counts[left_id] += 1
    return tuple(counts)


def rank_records_from_hit_counts(values: tuple[int, ...] | list[int], hit_counts: tuple[int, ...] | list[int]) -> tuple[dict[str, int], ...]:
    normalized = tuple(int(value) for value in values)
    counts = tuple(int(count) for count in hit_counts)
    if len(normalized) != len(counts):
        raise ValueError("values and hit_counts must have the same length")
    return tuple(
        {"value": value, "hit_count": count, "original_index": index}
        for index, (value, count) in enumerate(zip(normalized, counts))
    )


def stable_sort_from_hit_counts(
    values: tuple[int, ...] | list[int],
    hit_counts: tuple[int, ...] | list[int],
    *,
    descending: bool = False,
) -> tuple[int, ...]:
    records = list(rank_records_from_hit_counts(values, hit_counts))
    if descending:
        records.sort(key=lambda row: (row["hit_count"], row["original_index"]))
    else:
        records.sort(key=lambda row: (-row["hit_count"], row["original_index"]))
    return tuple(int(row["value"]) for row in records)


def stable_sort_reference(values: tuple[int, ...] | list[int], *, descending: bool = False) -> tuple[int, ...]:
    indexed = list(enumerate(int(value) for value in values))
    if descending:
        indexed.sort(key=lambda item: (-item[1], item[0]))
    else:
        indexed.sort(key=lambda item: (item[1], item[0]))
    return tuple(value for _, value in indexed)


def quicksort_reference(values: tuple[int, ...] | list[int], *, descending: bool = False) -> tuple[int, ...]:
    indexed = [(index, int(value)) for index, value in enumerate(values)]

    def key(item: tuple[int, int]) -> tuple[int, int]:
        index, value = item
        return ((-value) if descending else value, index)

    def sort_items(items: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(items) <= 1:
            return items
        pivot = key(items[len(items) // 2])
        lower = [item for item in items if key(item) < pivot]
        equal = [item for item in items if key(item) == pivot]
        upper = [item for item in items if key(item) > pivot]
        return sort_items(lower) + equal + sort_items(upper)

    return tuple(value for _, value in sort_items(indexed))


def derive_sorts_from_rows(
    values: tuple[int, ...] | list[int],
    rows: tuple[dict[str, object], ...],
) -> dict[str, tuple[int, ...]]:
    counts = hit_counts_from_rows(values, rows)
    return {
        "hit_counts": counts,
        "ascending": stable_sort_from_hit_counts(values, counts, descending=False),
        "descending": stable_sort_from_hit_counts(values, counts, descending=True),
    }


def run_sorting_backend(backend: str, values: tuple[int, ...] | list[int]) -> dict[str, object]:
    case = make_ray_hit_sort_case(values)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(ray_hit_sorting_reference, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(ray_hit_sorting_reference, **case)
    elif backend == "embree":
        rows = rt.run_embree(ray_hit_sorting_reference, **case)
    elif backend == "optix":
        rows = rt.run_optix(ray_hit_sorting_reference, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(ray_hit_sorting_reference, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")
    derived = derive_sorts_from_rows(values, rows)
    return {
        "rows": rows,
        "hit_counts": derived["hit_counts"],
        "ascending": derived["ascending"],
        "descending": derived["descending"],
    }
