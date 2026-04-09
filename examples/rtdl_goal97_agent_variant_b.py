from __future__ import annotations

import argparse

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def goal97_variant_b_ray_rank():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    ranks = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(ranks, fields=["ray_id", "hit_count"])


def _normalize_values(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError("Goal 97 variant_b accepts only nonnegative integers")
    return normalized


def _stable_key_stride(count: int) -> int:
    return count + 1


def encoded_keys(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    normalized = _normalize_values(values)
    stride = _stable_key_stride(len(normalized))
    return tuple(value * stride + index + 1 for index, value in enumerate(normalized))


def make_goal97_variant_b_case(values: tuple[int, ...] | list[int]) -> dict[str, tuple[object, ...]]:
    normalized = _normalize_values(values)
    keys = encoded_keys(normalized)
    triangles = []
    rays = []

    for index, key in enumerate(keys):
        x = float(key)
        triangles.append(
            rt.Triangle(
                id=index,
                x0=x,
                y0=-0.45,
                x1=x,
                y1=0.45,
                x2=x + 0.35,
                y2=0.0,
            )
        )
        rays.append(
            rt.Ray2D(
                id=index,
                ox=0.0,
                oy=0.0,
                dx=1.0,
                dy=0.0,
                tmax=x + 0.20,
            )
        )

    return {"rays": tuple(rays), "triangles": tuple(triangles)}


def expected_hit_counts(values: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    keys = encoded_keys(values)
    sorted_keys = sorted(keys)
    rank_by_key = {key: rank + 1 for rank, key in enumerate(sorted_keys)}
    return tuple(rank_by_key[key] for key in keys)


def hit_counts_from_rows(values: tuple[int, ...] | list[int], rows: tuple[dict[str, object], ...]) -> tuple[int, ...]:
    normalized = _normalize_values(values)
    counts = [0] * len(normalized)
    for row in rows:
        counts[int(row["ray_id"])] = int(row["hit_count"])
    return tuple(counts)


def stable_sorted_indices_from_hit_counts(
    values: tuple[int, ...] | list[int],
    hit_counts: tuple[int, ...] | list[int],
    *,
    descending: bool = False,
) -> tuple[int, ...]:
    normalized = _normalize_values(values)
    counts = tuple(int(count) for count in hit_counts)
    if len(normalized) != len(counts):
        raise ValueError("values and hit_counts must have the same length")

    ordered = [None] * len(normalized)
    for index, count in enumerate(counts):
        slot = count - 1
        if slot < 0 or slot >= len(normalized):
            raise ValueError("hit_counts do not form a valid stable rank sequence")
        if ordered[slot] is not None:
            raise ValueError("duplicate rank detected in hit_counts")
        ordered[slot] = index

    result = tuple(int(index) for index in ordered)
    if descending:
        return tuple(reversed(result))
    return result


def stable_sort_from_hit_counts(
    values: tuple[int, ...] | list[int],
    hit_counts: tuple[int, ...] | list[int],
    *,
    descending: bool = False,
) -> tuple[int, ...]:
    normalized = _normalize_values(values)
    order = stable_sorted_indices_from_hit_counts(normalized, hit_counts, descending=descending)
    return tuple(normalized[index] for index in order)


def stable_sort_reference(values: tuple[int, ...] | list[int], *, descending: bool = False) -> tuple[int, ...]:
    normalized = _normalize_values(values)
    ranked = list(enumerate(normalized))
    ranked.sort(key=lambda item: (item[1], item[0]))
    if descending:
        ranked.reverse()
    return tuple(value for _, value in ranked)


def run_goal97_variant_b(backend: str, values: tuple[int, ...] | list[int]) -> dict[str, object]:
    case = make_goal97_variant_b_case(values)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(goal97_variant_b_ray_rank, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(goal97_variant_b_ray_rank, **case)
    elif backend == "embree":
        rows = rt.run_embree(goal97_variant_b_ray_rank, **case)
    elif backend == "optix":
        rows = rt.run_optix(goal97_variant_b_ray_rank, **case)
    elif backend == "vulkan":
        rows = rt.run_vulkan(goal97_variant_b_ray_rank, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    counts = hit_counts_from_rows(values, rows)
    return {
        "rows": rows,
        "hit_counts": counts,
        "ascending": stable_sort_from_hit_counts(values, counts),
        "descending": stable_sort_from_hit_counts(values, counts, descending=True),
    }


def _demo(values: tuple[int, ...], backend: str) -> None:
    result = run_goal97_variant_b(backend, values)
    print(f"backend={backend}")
    print(f"values={values}")
    print(f"encoded_keys={encoded_keys(values)}")
    print(f"expected_hit_counts={expected_hit_counts(values)}")
    print(f"observed_hit_counts={result['hit_counts']}")
    print(f"ascending={result['ascending']}")
    print(f"descending={result['descending']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Goal 97 variant_b ray-hit stable integer sorting demo")
    parser.add_argument(
        "values",
        nargs="*",
        type=int,
        default=[4, 1, 4, 0, 2, 2],
        help="nonnegative integers to rank via RTDL ray hit counts",
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        help="backend to execute",
    )
    args = parser.parse_args()
    _demo(tuple(args.values), args.backend)


if __name__ == "__main__":
    main()
