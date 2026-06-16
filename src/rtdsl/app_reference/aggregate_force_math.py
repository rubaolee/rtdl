from __future__ import annotations

import math
import time
from typing import Iterable, Sequence

from ..aggregate_tree_reference import AggregateNodeRow
from ..aggregate_tree_reference import AggregateTreeNodeRow
from ..aggregate_tree_reference import WeightedPointRow
from ..aggregate_tree_reference import _get_value
from ..aggregate_tree_reference import _node_contains_source
from ..aggregate_tree_reference import _source_leaf_dfs_by_id
from ..aggregate_tree_reference import _tree_node_rows
from ..aggregate_tree_reference import _tree_roots
from ..aggregate_tree_reference import _tree_subtree_end_by_id
from ..aggregate_tree_reference import normalize_weighted_point_rows


WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT = (
    "generic_weighted_inverse_square_contribution_rows_2d_v1"
)
GROUPED_VECTOR_SUM_ROWS_2D_CONTRACT = "generic_grouped_vector_sum_rows_2d_v1"
WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT = (
    "generic_weighted_inverse_square_vector_sum_2d_v1"
)
VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT = (
    "generic_vector_sum_materialization_pressure_2d_v1"
)
AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT = (
    "generic_aggregate_frontier_weighted_vector_sum_2d_v1"
)
AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT = (
    "generic_aggregate_frontier_device_columns_weighted_vector_sum_2d_v1"
)


def _optional_value(row, names: Sequence[str]):
    try:
        return _get_value(row, names, "row")
    except ValueError:
        return None


def _aggregate_node_lookup(
    rows: Iterable[object] | None,
) -> dict[int, AggregateNodeRow | AggregateTreeNodeRow]:
    if rows is None:
        return {}
    lookup: dict[int, AggregateNodeRow | AggregateTreeNodeRow] = {}
    for row in rows:
        node_id = int(_get_value(row, ("id", "node_id", "aggregate_id"), "aggregate node"))
        if node_id in lookup:
            raise ValueError(f"duplicate aggregate node id: {node_id}")
        member_ids = _get_value(row, ("member_ids", "members", "point_ids", "body_ids"), "aggregate node")
        child_ids = _optional_value(row, ("child_ids", "children"))
        if child_ids is None:
            lookup[node_id] = AggregateNodeRow(
                id=node_id,
                cx=float(_get_value(row, ("cx", "x"), "aggregate node")),
                cy=float(_get_value(row, ("cy", "y"), "aggregate node")),
                half_size=float(_get_value(row, ("half_size", "radius", "extent"), "aggregate node")),
                mass=float(_get_value(row, ("mass", "weight"), "aggregate node")),
                member_ids=tuple(int(item) for item in member_ids),
            )
        else:
            resume_index = _get_value(row, ("resume_index", "next_dfs_index", "autorope_index"), "aggregate node")
            lookup[node_id] = AggregateTreeNodeRow(
                id=node_id,
                cx=float(_get_value(row, ("cx", "x"), "aggregate node")),
                cy=float(_get_value(row, ("cy", "y"), "aggregate node")),
                half_size=float(_get_value(row, ("half_size", "radius", "extent"), "aggregate node")),
                mass=float(_get_value(row, ("mass", "weight"), "aggregate node")),
                member_ids=tuple(int(item) for item in member_ids),
                child_ids=tuple(int(item) for item in child_ids),
                depth=int(_get_value(row, ("depth",), "aggregate node")),
                dfs_index=int(_get_value(row, ("dfs_index",), "aggregate node")),
                resume_index=None if resume_index is None else int(resume_index),
                cell_cx=float(_get_value(row, ("cell_cx", "spatial_cx"), "aggregate node")),
                cell_cy=float(_get_value(row, ("cell_cy", "spatial_cy"), "aggregate node")),
                is_leaf=bool(_get_value(row, ("is_leaf",), "aggregate node")),
            )
    return lookup


def _contribution_vector(
    source: WeightedPointRow,
    *,
    target_x: float,
    target_y: float,
    target_mass: float,
    softening: float,
) -> tuple[float, float, float]:
    dx = target_x - source.x
    dy = target_y - source.y
    dist_sq = dx * dx + dy * dy + softening * softening
    if dist_sq == 0.0:
        return 0.0, 0.0, dist_sq
    inv_dist = 1.0 / math.sqrt(dist_sq)
    scale = source.mass * target_mass * inv_dist * inv_dist * inv_dist
    return dx * scale, dy * scale, dist_sq


def evaluate_weighted_inverse_square_contribution_rows_2d(
    source_points: Iterable[object],
    target_points: Iterable[object],
    *,
    accepted_aggregate_rows: Iterable[object] = (),
    fallback_exact_rows: Iterable[object] = (),
    aggregate_nodes: Iterable[object] | None = None,
    softening: float = 0.0,
) -> dict[str, object]:
    """App-reference Barnes-Hut inverse-square contribution rows."""

    softening = float(softening)
    if softening < 0.0:
        raise ValueError("softening must be non-negative")
    sources = normalize_weighted_point_rows(source_points)
    targets = normalize_weighted_point_rows(target_points)
    source_by_id = {source.id: source for source in sources}
    target_by_id = {target.id: target for target in targets}
    aggregate_by_id = _aggregate_node_lookup(aggregate_nodes)

    rows: list[dict[str, object]] = []
    per_source: dict[int, dict[str, int]] = {
        source.id: {
            "aggregate_contribution_count": 0,
            "exact_contribution_count": 0,
        }
        for source in sources
    }

    for row in accepted_aggregate_rows:
        source_id = int(_get_value(row, ("source_id", "query_id", "point_id"), "accepted aggregate"))
        aggregate_id = int(_get_value(row, ("aggregate_id", "node_id", "neighbor_id"), "accepted aggregate"))
        if source_id not in source_by_id:
            raise ValueError(f"accepted aggregate source_id {source_id} is not present")
        aggregate_mass = _optional_value(row, ("aggregate_mass", "mass", "weight"))
        aggregate_cx = _optional_value(row, ("aggregate_cx", "cx", "x"))
        aggregate_cy = _optional_value(row, ("aggregate_cy", "cy", "y"))
        if aggregate_mass is None or aggregate_cx is None or aggregate_cy is None:
            if aggregate_id not in aggregate_by_id:
                raise ValueError(
                    f"accepted aggregate row {aggregate_id} lacks aggregate fields and no aggregate node was provided"
                )
            aggregate = aggregate_by_id[aggregate_id]
            aggregate_mass = aggregate.mass
            aggregate_cx = aggregate.cx
            aggregate_cy = aggregate.cy
        vector_x, vector_y, dist_sq = _contribution_vector(
            source_by_id[source_id],
            target_x=float(aggregate_cx),
            target_y=float(aggregate_cy),
            target_mass=float(aggregate_mass),
            softening=softening,
        )
        rows.append(
            {
                "source_id": source_id,
                "contribution_kind": "aggregate",
                "aggregate_id": aggregate_id,
                "target_id": None,
                "vector_x": vector_x,
                "vector_y": vector_y,
                "distance_sq": dist_sq,
            }
        )
        per_source[source_id]["aggregate_contribution_count"] += 1

    for row in fallback_exact_rows:
        source_id = int(_get_value(row, ("source_id", "query_id", "point_id"), "fallback exact"))
        target_id = int(_get_value(row, ("target_id", "neighbor_id", "body_id"), "fallback exact"))
        if source_id not in source_by_id:
            raise ValueError(f"fallback source_id {source_id} is not present")
        if target_id not in target_by_id:
            raise ValueError(f"fallback target_id {target_id} is not present")
        target = target_by_id[target_id]
        vector_x, vector_y, dist_sq = _contribution_vector(
            source_by_id[source_id],
            target_x=target.x,
            target_y=target.y,
            target_mass=target.mass,
            softening=softening,
        )
        rows.append(
            {
                "source_id": source_id,
                "contribution_kind": "exact",
                "aggregate_id": _optional_value(row, ("aggregate_id", "node_id")),
                "target_id": target_id,
                "vector_x": vector_x,
                "vector_y": vector_y,
                "distance_sq": dist_sq,
            }
        )
        per_source[source_id]["exact_contribution_count"] += 1

    summary = {
        "source_count": len(sources),
        "target_count": len(targets),
        "contribution_row_count": len(rows),
        "aggregate_contribution_row_count": sum(
            row["aggregate_contribution_count"] for row in per_source.values()
        ),
        "exact_contribution_row_count": sum(row["exact_contribution_count"] for row in per_source.values()),
        "sources_with_contributions": sum(
            1
            for row in per_source.values()
            if row["aggregate_contribution_count"] or row["exact_contribution_count"]
        ),
    }
    return {
        "contribution_rows": tuple(rows),
        "per_source_summary": per_source,
        "summary": summary,
        "metadata": {
            "contract": WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT,
            "softening": softening,
            "app_reference_math": True,
            "aggregate_rows_supported": True,
            "exact_rows_supported": True,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def sum_vector_contribution_rows_2d(
    contribution_rows: Iterable[object],
    *,
    source_ids: Iterable[int] | None = None,
) -> dict[str, object]:
    """Group app-reference vector contribution rows by source and sum components."""

    sums: dict[int, list[float]] = {}
    counts: dict[int, int] = {}
    if source_ids is not None:
        for source_id in source_ids:
            normalized_source_id = int(source_id)
            sums[normalized_source_id] = [0.0, 0.0]
            counts[normalized_source_id] = 0
    for row in contribution_rows:
        source_id = int(_get_value(row, ("source_id", "query_id", "point_id"), "vector contribution"))
        vector_x = float(_get_value(row, ("vector_x", "x", "force_x"), "vector contribution"))
        vector_y = float(_get_value(row, ("vector_y", "y", "force_y"), "vector contribution"))
        if source_id not in sums:
            sums[source_id] = [0.0, 0.0]
            counts[source_id] = 0
        sums[source_id][0] += vector_x
        sums[source_id][1] += vector_y
        counts[source_id] += 1

    rows = tuple(
        {
            "source_id": source_id,
            "vector_x": vector[0],
            "vector_y": vector[1],
            "contribution_count": counts[source_id],
        }
        for source_id, vector in sorted(sums.items())
    )
    return {
        "vector_sum_rows": rows,
        "summary": {
            "source_count": len(rows),
            "contribution_row_count": sum(counts.values()),
            "sources_with_contributions": sum(1 for count in counts.values() if count),
        },
        "metadata": {
            "contract": GROUPED_VECTOR_SUM_ROWS_2D_CONTRACT,
            "group_by": "source_id",
            "app_reference_math": True,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def sum_weighted_inverse_square_contributions_2d(
    source_points: Iterable[object],
    target_points: Iterable[object],
    *,
    accepted_aggregate_rows: Iterable[object] = (),
    fallback_exact_rows: Iterable[object] = (),
    aggregate_nodes: Iterable[object] | None = None,
    softening: float = 0.0,
) -> dict[str, object]:
    """Stream app-reference inverse-square contributions directly into vector sums."""

    softening = float(softening)
    if softening < 0.0:
        raise ValueError("softening must be non-negative")
    sources = normalize_weighted_point_rows(source_points)
    targets = normalize_weighted_point_rows(target_points)
    source_by_id = {source.id: source for source in sources}
    target_by_id = {target.id: target for target in targets}
    aggregate_by_id = _aggregate_node_lookup(aggregate_nodes)
    sums: dict[int, list[float]] = {source.id: [0.0, 0.0] for source in sources}
    aggregate_count_by_source: dict[int, int] = {source.id: 0 for source in sources}
    exact_count_by_source: dict[int, int] = {source.id: 0 for source in sources}

    for row in accepted_aggregate_rows:
        source_id = int(_get_value(row, ("source_id", "query_id", "point_id"), "accepted aggregate"))
        aggregate_id = int(_get_value(row, ("aggregate_id", "node_id", "neighbor_id"), "accepted aggregate"))
        if source_id not in source_by_id:
            raise ValueError(f"accepted aggregate source_id {source_id} is not present")
        aggregate_mass = _optional_value(row, ("aggregate_mass", "mass", "weight"))
        aggregate_cx = _optional_value(row, ("aggregate_cx", "cx", "x"))
        aggregate_cy = _optional_value(row, ("aggregate_cy", "cy", "y"))
        if aggregate_mass is None or aggregate_cx is None or aggregate_cy is None:
            if aggregate_id not in aggregate_by_id:
                raise ValueError(
                    f"accepted aggregate row {aggregate_id} lacks aggregate fields and no aggregate node was provided"
                )
            aggregate = aggregate_by_id[aggregate_id]
            aggregate_mass = aggregate.mass
            aggregate_cx = aggregate.cx
            aggregate_cy = aggregate.cy
        vector_x, vector_y, _ = _contribution_vector(
            source_by_id[source_id],
            target_x=float(aggregate_cx),
            target_y=float(aggregate_cy),
            target_mass=float(aggregate_mass),
            softening=softening,
        )
        sums[source_id][0] += vector_x
        sums[source_id][1] += vector_y
        aggregate_count_by_source[source_id] += 1

    for row in fallback_exact_rows:
        source_id = int(_get_value(row, ("source_id", "query_id", "point_id"), "fallback exact"))
        target_id = int(_get_value(row, ("target_id", "neighbor_id", "body_id"), "fallback exact"))
        if source_id not in source_by_id:
            raise ValueError(f"fallback source_id {source_id} is not present")
        if target_id not in target_by_id:
            raise ValueError(f"fallback target_id {target_id} is not present")
        target = target_by_id[target_id]
        vector_x, vector_y, _ = _contribution_vector(
            source_by_id[source_id],
            target_x=target.x,
            target_y=target.y,
            target_mass=target.mass,
            softening=softening,
        )
        sums[source_id][0] += vector_x
        sums[source_id][1] += vector_y
        exact_count_by_source[source_id] += 1

    rows = tuple(
        {
            "source_id": source.id,
            "vector_x": sums[source.id][0],
            "vector_y": sums[source.id][1],
            "aggregate_contribution_count": aggregate_count_by_source[source.id],
            "exact_contribution_count": exact_count_by_source[source.id],
            "contribution_count": aggregate_count_by_source[source.id] + exact_count_by_source[source.id],
        }
        for source in sources
    )
    contribution_count = sum(row["contribution_count"] for row in rows)
    return {
        "vector_sum_rows": rows,
        "summary": {
            "source_count": len(sources),
            "target_count": len(targets),
            "contribution_row_count": contribution_count,
            "aggregate_contribution_row_count": sum(aggregate_count_by_source.values()),
            "exact_contribution_row_count": sum(exact_count_by_source.values()),
            "sources_with_contributions": sum(1 for row in rows if row["contribution_count"]),
            "materialized_contribution_rows": False,
        },
        "metadata": {
            "contract": WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT,
            "softening": softening,
            "app_reference_math": True,
            "intermediate_contribution_rows_materialized": False,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def estimate_vector_sum_materialization_pressure_2d(
    *,
    accepted_aggregate_row_count: int,
    fallback_exact_row_count: int,
    source_count: int,
    native_contribution_row_bytes: int = 64,
    python_contribution_row_bytes: int = 320,
    python_warning_bytes: int = 256 * 1024 * 1024,
) -> dict[str, object]:
    """Estimate intermediate-row materialization pressure for app-reference sums."""

    accepted_aggregate_row_count = int(accepted_aggregate_row_count)
    fallback_exact_row_count = int(fallback_exact_row_count)
    source_count = int(source_count)
    if accepted_aggregate_row_count < 0:
        raise ValueError("accepted_aggregate_row_count must be non-negative")
    if fallback_exact_row_count < 0:
        raise ValueError("fallback_exact_row_count must be non-negative")
    if source_count < 0:
        raise ValueError("source_count must be non-negative")
    if native_contribution_row_bytes < 1:
        raise ValueError("native_contribution_row_bytes must be positive")
    if python_contribution_row_bytes < 1:
        raise ValueError("python_contribution_row_bytes must be positive")
    if python_warning_bytes < 1:
        raise ValueError("python_warning_bytes must be positive")
    contribution_row_count = accepted_aggregate_row_count + fallback_exact_row_count
    native_bytes = contribution_row_count * native_contribution_row_bytes
    python_bytes = contribution_row_count * python_contribution_row_bytes
    rows_per_source = contribution_row_count / source_count if source_count else 0.0
    return {
        "summary": {
            "source_count": source_count,
            "accepted_aggregate_row_count": accepted_aggregate_row_count,
            "fallback_exact_row_count": fallback_exact_row_count,
            "contribution_row_count": contribution_row_count,
            "rows_per_source": rows_per_source,
            "native_contribution_row_bytes": native_contribution_row_bytes,
            "python_contribution_row_bytes": python_contribution_row_bytes,
            "estimated_native_intermediate_bytes": native_bytes,
            "estimated_python_intermediate_bytes": python_bytes,
            "python_warning_bytes": python_warning_bytes,
            "python_materialization_warning": python_bytes >= python_warning_bytes,
            "recommended_execution": (
                "streamed_or_native_fused"
                if python_bytes >= python_warning_bytes
                else "materialized_reference_allowed"
            ),
        },
        "metadata": {
            "contract": VECTOR_SUM_MATERIALIZATION_PRESSURE_2D_CONTRACT,
            "app_reference_math": True,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def sum_aggregate_frontier_weighted_vectors_2d(
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    theta: float,
    softening: float = 0.0,
    deduplicate_fallback_targets: bool = True,
) -> dict[str, object]:
    """App-reference fused aggregate-frontier inverse-square vector sum."""

    theta = float(theta)
    softening = float(softening)
    if theta <= 0.0:
        raise ValueError("theta must be positive")
    if softening < 0.0:
        raise ValueError("softening must be non-negative")

    sources = normalize_weighted_point_rows(source_points)
    targets = normalize_weighted_point_rows(target_points)
    nodes = _tree_node_rows(tree_nodes)
    target_by_id = {target.id: target for target in targets}
    node_by_id = {node.id: node for node in nodes}
    node_member_sets = {node.id: set(node.member_ids) for node in nodes}
    root_ids = _tree_roots(nodes)
    subtree_end_by_id = _tree_subtree_end_by_id(nodes)
    source_leaf_dfs_by_id = _source_leaf_dfs_by_id(nodes)

    rows: list[dict[str, object]] = []
    total_visited = 0
    total_accepted = 0
    total_exact = 0

    def add_contribution(
        source: WeightedPointRow,
        *,
        target_x: float,
        target_y: float,
        target_mass: float,
    ) -> tuple[float, float]:
        vector_x, vector_y, _ = _contribution_vector(
            source,
            target_x=target_x,
            target_y=target_y,
            target_mass=target_mass,
            softening=softening,
        )
        return vector_x, vector_y

    for source in sources:
        sums = [0.0, 0.0]
        visited_count = 0
        accepted_count = 0
        exact_count = 0
        fallback_seen: set[int] = set()

        def visit(node: AggregateTreeNodeRow) -> None:
            nonlocal visited_count, accepted_count, exact_count
            visited_count += 1
            dx = node.cx - source.x
            dy = node.cy - source.y
            distance = math.hypot(dx, dy)
            opening_ratio = math.inf if distance == 0.0 else (2.0 * node.half_size) / distance
            contains_source = _node_contains_source(
                node,
                source.id,
                source_leaf_dfs_by_id=source_leaf_dfs_by_id,
                subtree_end_by_id=subtree_end_by_id,
                node_member_sets=node_member_sets,
            )
            if not contains_source and opening_ratio < theta:
                vector_x, vector_y = add_contribution(
                    source,
                    target_x=node.cx,
                    target_y=node.cy,
                    target_mass=node.mass,
                )
                sums[0] += vector_x
                sums[1] += vector_y
                accepted_count += 1
                return
            if node.child_ids:
                for child_id in node.child_ids:
                    visit(node_by_id[child_id])
                return
            for target_id in node.member_ids:
                if target_id == source.id:
                    continue
                if deduplicate_fallback_targets and target_id in fallback_seen:
                    continue
                fallback_seen.add(target_id)
                if target_id not in target_by_id:
                    raise ValueError(f"fallback target_id {target_id} is not present")
                target = target_by_id[target_id]
                vector_x, vector_y = add_contribution(
                    source,
                    target_x=target.x,
                    target_y=target.y,
                    target_mass=target.mass,
                )
                sums[0] += vector_x
                sums[1] += vector_y
                exact_count += 1

        for root_id in root_ids:
            visit(node_by_id[root_id])

        total_visited += visited_count
        total_accepted += accepted_count
        total_exact += exact_count
        rows.append(
            {
                "source_id": source.id,
                "vector_x": sums[0],
                "vector_y": sums[1],
                "aggregate_contribution_count": accepted_count,
                "exact_contribution_count": exact_count,
                "contribution_count": accepted_count + exact_count,
                "visited_node_count": visited_count,
            }
        )

    return {
        "vector_sum_rows": tuple(rows),
        "summary": {
            "source_count": len(sources),
            "target_count": len(targets),
            "tree_node_count": len(nodes),
            "root_count": len(root_ids),
            "leaf_node_count": sum(1 for node in nodes if node.is_leaf),
            "visited_node_total": total_visited,
            "contribution_row_count": total_accepted + total_exact,
            "aggregate_contribution_row_count": total_accepted,
            "exact_contribution_row_count": total_exact,
            "sources_with_contributions": sum(1 for row in rows if row["contribution_count"]),
            "materialized_frontier_rows": False,
            "materialized_contribution_rows": False,
        },
        "metadata": {
            "contract": AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "theta": theta,
            "softening": softening,
            "deduplicate_fallback_targets": deduplicate_fallback_targets,
            "app_reference_math": True,
            "intermediate_frontier_rows_materialized": False,
            "intermediate_contribution_rows_materialized": False,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
    frontier_device_columns: object,
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    softening: float = 0.0,
) -> dict[str, object]:
    """Consume M36 frontier device columns with a CuPy Barnes-Hut-style partner.

    This is deliberately app-scoped partner math. It consumes the generic
    frontier schema on device and computes inverse-square vector sums without
    materializing frontier rows on host.
    """

    softening = float(softening)
    if softening < 0.0:
        raise ValueError("softening must be non-negative")
    if not hasattr(frontier_device_columns, "as_cupy_columns"):
        raise ValueError("frontier_device_columns must expose as_cupy_columns()")
    if bool(getattr(frontier_device_columns, "overflow", False)):
        raise ValueError("cannot consume overflowed aggregate-frontier device columns")

    import cupy as cp  # type: ignore

    sources = normalize_weighted_point_rows(source_points)
    targets = normalize_weighted_point_rows(target_points)
    nodes = _tree_node_rows(tree_nodes)
    if not sources:
        raise ValueError("at least one source point is required")
    if not targets:
        raise ValueError("at least one target point is required")
    if not nodes:
        raise ValueError("at least one aggregate tree node is required")

    source_ids_host = [int(point.id) for point in sources]
    target_ids_host = [int(point.id) for point in targets]
    node_ids_host = [int(node.id) for node in nodes]
    if min(source_ids_host) < 0 or min(target_ids_host) < 0 or min(node_ids_host) < 0:
        raise ValueError("CuPy aggregate-frontier vector continuation requires non-negative dense ids")
    max_point_id = max(max(source_ids_host), max(target_ids_host))
    max_node_id = max(node_ids_host)

    columns = frontier_device_columns.as_cupy_columns()
    row_count = int(getattr(frontier_device_columns, "row_count", len(columns["source_id"])))
    if row_count != int(columns["source_id"].shape[0]):
        raise ValueError("frontier row_count does not match source_id column length")

    cp.cuda.Stream.null.synchronize()
    start = time.perf_counter()

    source_ids = cp.asarray(source_ids_host, dtype=cp.int64)
    target_ids = cp.asarray(target_ids_host, dtype=cp.int64)
    node_ids = cp.asarray(node_ids_host, dtype=cp.int64)

    point_x_by_id = cp.zeros((max_point_id + 1,), dtype=cp.float64)
    point_y_by_id = cp.zeros((max_point_id + 1,), dtype=cp.float64)
    point_mass_by_id = cp.zeros((max_point_id + 1,), dtype=cp.float64)
    source_x_values = cp.asarray([float(point.x) for point in sources], dtype=cp.float64)
    source_y_values = cp.asarray([float(point.y) for point in sources], dtype=cp.float64)
    source_mass_values = cp.asarray([float(point.mass) for point in sources], dtype=cp.float64)
    target_x = cp.asarray([float(point.x) for point in targets], dtype=cp.float64)
    target_y = cp.asarray([float(point.y) for point in targets], dtype=cp.float64)
    target_mass = cp.asarray([float(point.mass) for point in targets], dtype=cp.float64)
    point_x_by_id[source_ids] = source_x_values
    point_y_by_id[source_ids] = source_y_values
    point_mass_by_id[source_ids] = source_mass_values
    point_x_by_id[target_ids] = target_x
    point_y_by_id[target_ids] = target_y
    point_mass_by_id[target_ids] = target_mass

    source_ordinal_by_id = cp.zeros((max_point_id + 1,), dtype=cp.int64)
    source_ordinal_by_id[source_ids] = cp.arange(len(sources), dtype=cp.int64)

    node_cx_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
    node_cy_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
    node_mass_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
    node_cx_by_id[node_ids] = cp.asarray([float(node.cx) for node in nodes], dtype=cp.float64)
    node_cy_by_id[node_ids] = cp.asarray([float(node.cy) for node in nodes], dtype=cp.float64)
    node_mass_by_id[node_ids] = cp.asarray([float(node.mass) for node in nodes], dtype=cp.float64)

    if row_count == 0:
        sum_x = cp.zeros((len(sources),), dtype=cp.float64)
        sum_y = cp.zeros((len(sources),), dtype=cp.float64)
        aggregate_count = 0
        exact_count = 0
    else:
        frontier_source_ids = columns["source_id"].astype(cp.int64, copy=False)
        kind_codes = columns["frontier_kind_code"].astype(cp.int64, copy=False)
        item_ids = columns["item_id"].astype(cp.int64, copy=False)
        aggregate_mask = kind_codes == 1
        exact_mask = kind_codes == 2
        safe_node_item_ids = cp.where(aggregate_mask, item_ids, 0)
        safe_point_item_ids = cp.where(exact_mask, item_ids, 0)

        source_x = point_x_by_id[frontier_source_ids]
        source_y = point_y_by_id[frontier_source_ids]
        source_mass = point_mass_by_id[frontier_source_ids]

        aggregate_x = node_cx_by_id[safe_node_item_ids]
        aggregate_y = node_cy_by_id[safe_node_item_ids]
        aggregate_mass = node_mass_by_id[safe_node_item_ids]
        exact_x = point_x_by_id[safe_point_item_ids]
        exact_y = point_y_by_id[safe_point_item_ids]
        exact_mass = point_mass_by_id[safe_point_item_ids]

        contribution_x_target = cp.where(aggregate_mask, aggregate_x, exact_x)
        contribution_y_target = cp.where(aggregate_mask, aggregate_y, exact_y)
        contribution_mass_target = cp.where(aggregate_mask, aggregate_mass, exact_mass)
        dx = contribution_x_target - source_x
        dy = contribution_y_target - source_y
        dist_sq = dx * dx + dy * dy + softening * softening
        safe_dist_sq = cp.where(dist_sq == 0.0, 1.0, dist_sq)
        inv_dist = 1.0 / cp.sqrt(safe_dist_sq)
        scale = source_mass * contribution_mass_target * inv_dist * inv_dist * inv_dist
        scale = cp.where(dist_sq == 0.0, 0.0, scale)
        values_x = dx * scale
        values_y = dy * scale

        group_ids = source_ordinal_by_id[frontier_source_ids]
        sum_x = cp.bincount(group_ids, weights=values_x, minlength=len(sources)).astype(cp.float64, copy=False)
        sum_y = cp.bincount(group_ids, weights=values_y, minlength=len(sources)).astype(cp.float64, copy=False)
        aggregate_count = int(cp.count_nonzero(aggregate_mask).item())
        exact_count = int(cp.count_nonzero(exact_mask).item())

    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - start
    return {
        "columns": {
            "source_ids": source_ids,
            "vector_x": sum_x,
            "vector_y": sum_y,
        },
        "metadata": {
            "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "logical_reference_contract": AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "partner": "cupy",
            "softening": softening,
            "source_count": len(sources),
            "frontier_row_count": row_count,
            "aggregate_contribution_row_count": aggregate_count,
            "exact_contribution_row_count": exact_count,
            "partner_seconds": elapsed,
            "frontier_columns_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "app_reference_math": True,
            "native_engine_app_specific": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }
