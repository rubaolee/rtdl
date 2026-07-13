from __future__ import annotations

from math import log10
from typing import Iterable, Sequence


PARTITIONED_TRAVERSAL_FANOUT_CONTRACT = "generic_partitioned_traversal_fanout_v1"
PARTITIONED_TRAVERSAL_COST_MODEL_CONTRACT = (
    "generic_partitioned_traversal_cost_model_v1"
)


def _normalized_ids(values: Iterable[int], *, name: str) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in values)
    if any(value < 0 for value in normalized):
        raise ValueError(f"{name} must contain non-negative ids")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must contain unique ids")
    return normalized


def _require_power_of_two(value: int, *, name: str) -> int:
    normalized = int(value)
    if normalized <= 0 or normalized & (normalized - 1):
        raise ValueError(f"{name} must be a positive power of two")
    return normalized


def partitioned_traversal_fanout_plan(
    *,
    primitive_ids: Iterable[int],
    ray_ids: Iterable[int],
    partition_count: int,
) -> dict[str, object]:
    """Build a stable disjoint-partition and ray-fanout reference plan."""

    primitives = _normalized_ids(primitive_ids, name="primitive_ids")
    rays = _normalized_ids(ray_ids, name="ray_ids")
    partitions = _require_power_of_two(partition_count, name="partition_count")

    primitive_partition_ids = tuple(
        ordinal % partitions for ordinal in range(len(primitives))
    )
    partition_loads = tuple(
        sum(1 for partition_id in primitive_partition_ids if partition_id == current)
        for current in range(partitions)
    )
    fanout_ray_ids = tuple(ray_id for ray_id in rays for _ in range(partitions))
    fanout_partition_ids = tuple(
        partition_id for _ in rays for partition_id in range(partitions)
    )
    cartesian_pair_count = len(primitives) * len(rays)
    partitioned_pair_count = sum(partition_loads) * len(rays)
    if partitioned_pair_count != cartesian_pair_count:
        raise RuntimeError("partitioned traversal plan lost pair coverage")

    return {
        "columns": {
            "primitive_ids": primitives,
            "primitive_partition_ids": primitive_partition_ids,
            "fanout_ray_ids": fanout_ray_ids,
            "fanout_partition_ids": fanout_partition_ids,
            "partition_loads": partition_loads,
        },
        "metadata": {
            "contract": PARTITIONED_TRAVERSAL_FANOUT_CONTRACT,
            "app_semantics": "none",
            "execution": "python_reference",
            "native_backend": False,
            "partition_count": partitions,
            "primitive_count": len(primitives),
            "ray_count": len(rays),
            "fanout_ray_count": len(fanout_ray_ids),
            "max_primitives_per_partition": max(partition_loads, default=0),
            "cartesian_pair_count": cartesian_pair_count,
            "partitioned_pair_count": partitioned_pair_count,
            "complete_pair_coverage_by_construction": True,
            "duplicate_pair_coverage_by_construction": False,
            "runtime_speedup_claimed": False,
        },
    }


def estimate_partitioned_traversal_selectivity(
    *,
    sampled_hit_count: int,
    sampled_ray_count: int,
    sampled_primitive_count: int,
) -> float:
    hits = int(sampled_hit_count)
    rays = int(sampled_ray_count)
    primitives = int(sampled_primitive_count)
    if hits < 0:
        raise ValueError("sampled_hit_count must be non-negative")
    if rays <= 0 or primitives <= 0:
        raise ValueError("sampled ray and primitive counts must be positive")
    pair_count = rays * primitives
    if hits > pair_count:
        raise ValueError("sampled_hit_count cannot exceed sampled pair count")
    return hits / pair_count


def select_partitioned_traversal_fanout(
    *,
    ray_count: int,
    primitive_count: int,
    selectivity: float,
    intersection_cost_weight: float,
    candidate_partition_counts: Sequence[int] = (1, 2, 4, 8, 16, 32, 64, 128),
) -> dict[str, object]:
    """Select a fanout using an explicit ray-versus-intersection cost model."""

    rays = int(ray_count)
    primitives = int(primitive_count)
    normalized_selectivity = float(selectivity)
    weight = float(intersection_cost_weight)
    if rays <= 0 or primitives <= 0:
        raise ValueError("ray_count and primitive_count must be positive")
    if not 0.0 <= normalized_selectivity <= 1.0:
        raise ValueError("selectivity must be within [0, 1]")
    if not 0.0 <= weight <= 1.0:
        raise ValueError("intersection_cost_weight must be within [0, 1]")

    candidates = tuple(
        _require_power_of_two(value, name="candidate partition count")
        for value in candidate_partition_counts
    )
    if not candidates:
        raise ValueError("candidate_partition_counts must not be empty")
    if tuple(sorted(set(candidates))) != candidates:
        raise ValueError("candidate_partition_counts must be unique and increasing")

    search_cost = log10(max(primitives, 2))
    rows: list[dict[str, float | int]] = []
    for partitions in candidates:
        ray_cast_cost = rays * partitions * search_cost
        intersection_cost = (
            rays * primitives * normalized_selectivity / partitions
        )
        weighted_cost = (1.0 - weight) * ray_cast_cost + weight * intersection_cost
        rows.append(
            {
                "partition_count": partitions,
                "ray_cast_cost": ray_cast_cost,
                "intersection_cost": intersection_cost,
                "weighted_cost": weighted_cost,
            }
        )
    selected = min(rows, key=lambda row: (float(row["weighted_cost"]), int(row["partition_count"])))
    return {
        "selected_partition_count": int(selected["partition_count"]),
        "cost_rows": tuple(rows),
        "metadata": {
            "contract": PARTITIONED_TRAVERSAL_COST_MODEL_CONTRACT,
            "app_semantics": "none",
            "ray_count": rays,
            "primitive_count": primitives,
            "selectivity": normalized_selectivity,
            "intersection_cost_weight": weight,
            "candidate_partition_counts": candidates,
            "search_cost_model": "log10_primitive_count",
            "runtime_speedup_claimed": False,
        },
    }


__all__ = [
    "PARTITIONED_TRAVERSAL_COST_MODEL_CONTRACT",
    "PARTITIONED_TRAVERSAL_FANOUT_CONTRACT",
    "estimate_partitioned_traversal_selectivity",
    "partitioned_traversal_fanout_plan",
    "select_partitioned_traversal_fanout",
]
