from __future__ import annotations

from collections.abc import Iterable

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def goal97_variant_a_ray_rank():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    counts = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(counts, fields=["ray_id", "hit_count"])


def _coerce_values(values: Iterable[int]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError("Goal 97 variant A accepts only nonnegative integers")
    return normalized


def build_ray_rank_case(
    values: Iterable[int],
    *,
    far_x: float | None = None,
) -> dict[str, tuple[object, ...]]:
    items = _coerce_values(values)
    max_value = max(items, default=0)
    horizon = float(len(items) + max_value + 4) if far_x is None else float(far_x)
    if horizon <= 1.0:
        raise ValueError("far_x must be positive")

    triangles: list[rt.Triangle] = []
    rays: list[rt.Ray2D] = []
    for index, value in enumerate(items):
        spine_x = float(index + 1)
        triangles.append(
            rt.Triangle(
                id=index,
                x0=spine_x,
                y0=0.0,
                x1=horizon,
                y1=0.0,
                x2=spine_x,
                y2=float(value) + 1.0,
            )
        )
        rays.append(
            rt.Ray2D(
                id=index,
                ox=0.0,
                oy=float(value) + 0.5,
                dx=1.0,
                dy=0.0,
                tmax=horizon + 1.0,
            )
        )
    return {"rays": tuple(rays), "triangles": tuple(triangles)}


def oracle_hit_counts(values: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    return tuple(sum(1 for other in items if other >= value) for value in items)


def rows_to_hit_counts(values: Iterable[int], rows: Iterable[dict[str, object]]) -> tuple[int, ...]:
    items = _coerce_values(values)
    counts = [0] * len(items)
    for row in rows:
        ray_id = int(row["ray_id"])
        counts[ray_id] = int(row["hit_count"])
    return tuple(counts)


def stable_ascending_indices(values: Iterable[int], hit_counts: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    counts = tuple(int(count) for count in hit_counts)
    if len(items) != len(counts):
        raise ValueError("values and hit counts must have matching lengths")
    order = list(range(len(items)))
    order.sort(key=lambda index: (-counts[index], index))
    return tuple(order)


def stable_descending_indices(values: Iterable[int], hit_counts: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    counts = tuple(int(count) for count in hit_counts)
    if len(items) != len(counts):
        raise ValueError("values and hit counts must have matching lengths")
    order = list(range(len(items)))
    order.sort(key=lambda index: (counts[index], index))
    return tuple(order)


def reorder(values: Iterable[int], indices: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    return tuple(items[index] for index in indices)


def expected_stable_ascending(values: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    return tuple(value for _, value in sorted(enumerate(items), key=lambda pair: (pair[1], pair[0])))


def expected_stable_descending(values: Iterable[int]) -> tuple[int, ...]:
    items = _coerce_values(values)
    return tuple(value for _, value in sorted(enumerate(items), key=lambda pair: (-pair[1], pair[0])))


def run_variant_a(values: Iterable[int], *, backend: str = "cpu_python_reference") -> dict[str, object]:
    items = _coerce_values(values)
    case = build_ray_rank_case(items)

    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(goal97_variant_a_ray_rank, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(goal97_variant_a_ray_rank, **case)
    elif backend == "embree":
        rows = rt.run_embree(goal97_variant_a_ray_rank, **case)
    elif backend == "optix":
        rows = rt.run_optix(goal97_variant_a_ray_rank, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(goal97_variant_a_ray_rank, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    hit_counts = rows_to_hit_counts(items, rows)
    ascending_indices = stable_ascending_indices(items, hit_counts)
    descending_indices = stable_descending_indices(items, hit_counts)
    return {
        "values": items,
        "rows": rows,
        "hit_counts": hit_counts,
        "oracle_hit_counts": oracle_hit_counts(items),
        "ascending_indices": ascending_indices,
        "descending_indices": descending_indices,
        "ascending_values": reorder(items, ascending_indices),
        "descending_values": reorder(items, descending_indices),
        "expected_ascending_values": expected_stable_ascending(items),
        "expected_descending_values": expected_stable_descending(items),
    }


def _demo() -> None:
    sample = (4, 1, 4, 0, 2, 2, 5)
    result = run_variant_a(sample, backend="cpu_python_reference")
    print("Goal 97 variant A")
    print("input:", result["values"])
    print("hit counts:", result["hit_counts"])
    print("oracle hit counts:", result["oracle_hit_counts"])
    print("ascending indices:", result["ascending_indices"])
    print("ascending values:", result["ascending_values"])
    print("expected ascending:", result["expected_ascending_values"])
    print("descending indices:", result["descending_indices"])
    print("descending values:", result["descending_values"])
    print("expected descending:", result["expected_descending_values"])


GOAL97_AGENT_VARIANT_A_KERNELS = (goal97_variant_a_ray_rank,)


if __name__ == "__main__":
    _demo()
