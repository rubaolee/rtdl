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
AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT = (
    "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_v1"
)
AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT = (
    "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_numba_v1"
)
AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT = (
    "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1"
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


class PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy:
    """Prepared app partner for M36 aggregate-frontier device columns.

    The RTDL engine boundary remains the generic aggregate-frontier
    device-column primitive. This class is app-owned inverse-square math that
    keeps source, target, and aggregate lookup columns resident across hot
    frontier runs.
    """

    def __init__(
        self,
        source_points: Iterable[object],
        target_points: Iterable[object],
        tree_nodes: Iterable[object],
    ) -> None:
        import cupy as cp  # type: ignore

        self.cp = cp
        self.sources = normalize_weighted_point_rows(source_points)
        self.targets = normalize_weighted_point_rows(target_points)
        self.nodes = _tree_node_rows(tree_nodes)
        if not self.sources:
            raise ValueError("at least one source point is required")
        if not self.targets:
            raise ValueError("at least one target point is required")
        if not self.nodes:
            raise ValueError("at least one aggregate tree node is required")

        source_ids_host = [int(point.id) for point in self.sources]
        target_ids_host = [int(point.id) for point in self.targets]
        node_ids_host = [int(node.id) for node in self.nodes]
        if min(source_ids_host) < 0 or min(target_ids_host) < 0 or min(node_ids_host) < 0:
            raise ValueError("CuPy aggregate-frontier vector continuation requires non-negative dense ids")
        if len(set(source_ids_host)) != len(source_ids_host):
            raise ValueError("source point ids must be unique")
        if len(set(target_ids_host)) != len(target_ids_host):
            raise ValueError("target point ids must be unique")
        if len(set(node_ids_host)) != len(node_ids_host):
            raise ValueError("aggregate tree node ids must be unique")

        cp.cuda.Stream.null.synchronize()
        start = time.perf_counter()

        self.source_ids = cp.asarray(source_ids_host, dtype=cp.int64)
        self.source_x = cp.asarray([float(point.x) for point in self.sources], dtype=cp.float64)
        self.source_y = cp.asarray([float(point.y) for point in self.sources], dtype=cp.float64)
        self.source_mass = cp.asarray([float(point.mass) for point in self.sources], dtype=cp.float64)

        target_ids = cp.asarray(target_ids_host, dtype=cp.int64)
        node_ids = cp.asarray(node_ids_host, dtype=cp.int64)
        max_source_id = max(source_ids_host)
        max_target_id = max(target_ids_host)
        max_node_id = max(node_ids_host)

        self.source_x_by_id = cp.zeros((max_source_id + 1,), dtype=cp.float64)
        self.source_y_by_id = cp.zeros((max_source_id + 1,), dtype=cp.float64)
        self.source_mass_by_id = cp.zeros((max_source_id + 1,), dtype=cp.float64)
        self.source_x_by_id[self.source_ids] = self.source_x
        self.source_y_by_id[self.source_ids] = self.source_y
        self.source_mass_by_id[self.source_ids] = self.source_mass

        self.target_x_by_id = cp.zeros((max_target_id + 1,), dtype=cp.float64)
        self.target_y_by_id = cp.zeros((max_target_id + 1,), dtype=cp.float64)
        self.target_mass_by_id = cp.zeros((max_target_id + 1,), dtype=cp.float64)
        self.target_x_by_id[target_ids] = cp.asarray([float(point.x) for point in self.targets], dtype=cp.float64)
        self.target_y_by_id[target_ids] = cp.asarray([float(point.y) for point in self.targets], dtype=cp.float64)
        self.target_mass_by_id[target_ids] = cp.asarray(
            [float(point.mass) for point in self.targets],
            dtype=cp.float64,
        )

        self.source_ordinal_by_id = cp.zeros((max_source_id + 1,), dtype=cp.int64)
        self.source_ordinal_by_id[self.source_ids] = cp.arange(len(self.sources), dtype=cp.int64)

        self.node_cx_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
        self.node_cy_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
        self.node_mass_by_id = cp.zeros((max_node_id + 1,), dtype=cp.float64)
        self.node_cx_by_id[node_ids] = cp.asarray([float(node.cx) for node in self.nodes], dtype=cp.float64)
        self.node_cy_by_id[node_ids] = cp.asarray([float(node.cy) for node in self.nodes], dtype=cp.float64)
        self.node_mass_by_id[node_ids] = cp.asarray([float(node.mass) for node in self.nodes], dtype=cp.float64)

        cp.cuda.Stream.null.synchronize()
        self.prepare_seconds = time.perf_counter() - start

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def source_ids_device_ptr(self) -> int:
        return int(self.source_ids.data.ptr)

    @property
    def source_x_device_ptr(self) -> int:
        return int(self.source_x.data.ptr)

    @property
    def source_y_device_ptr(self) -> int:
        return int(self.source_y.data.ptr)

    def frontier_source_device_args(self) -> dict[str, object]:
        return {
            "source_ids_device_ptr": self.source_ids_device_ptr,
            "source_x_device_ptr": self.source_x_device_ptr,
            "source_y_device_ptr": self.source_y_device_ptr,
            "source_count": self.source_count,
            "source_column_owners": (self,),
        }

    def sum(
        self,
        frontier_device_columns: object,
        *,
        softening: float = 0.0,
    ) -> dict[str, object]:
        softening = float(softening)
        if softening < 0.0:
            raise ValueError("softening must be non-negative")
        if not hasattr(frontier_device_columns, "as_cupy_columns"):
            raise ValueError("frontier_device_columns must expose as_cupy_columns()")
        if bool(getattr(frontier_device_columns, "overflow", False)):
            raise ValueError("cannot consume overflowed aggregate-frontier device columns")

        cp = self.cp
        columns = frontier_device_columns.as_cupy_columns()
        row_count = int(getattr(frontier_device_columns, "row_count", len(columns["source_id"])))
        if row_count != int(columns["source_id"].shape[0]):
            raise ValueError("frontier row_count does not match source_id column length")

        cp.cuda.Stream.null.synchronize()
        start = time.perf_counter()

        if row_count == 0:
            sum_x = cp.zeros((self.source_count,), dtype=cp.float64)
            sum_y = cp.zeros((self.source_count,), dtype=cp.float64)
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

            source_x = self.source_x_by_id[frontier_source_ids]
            source_y = self.source_y_by_id[frontier_source_ids]
            source_mass = self.source_mass_by_id[frontier_source_ids]

            aggregate_x = self.node_cx_by_id[safe_node_item_ids]
            aggregate_y = self.node_cy_by_id[safe_node_item_ids]
            aggregate_mass = self.node_mass_by_id[safe_node_item_ids]
            exact_x = self.target_x_by_id[safe_point_item_ids]
            exact_y = self.target_y_by_id[safe_point_item_ids]
            exact_mass = self.target_mass_by_id[safe_point_item_ids]

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

            group_ids = self.source_ordinal_by_id[frontier_source_ids]
            sum_x = cp.bincount(group_ids, weights=values_x, minlength=self.source_count).astype(
                cp.float64,
                copy=False,
            )
            sum_y = cp.bincount(group_ids, weights=values_y, minlength=self.source_count).astype(
                cp.float64,
                copy=False,
            )
            aggregate_count = int(cp.count_nonzero(aggregate_mask).item())
            exact_count = int(cp.count_nonzero(exact_mask).item())

        cp.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        return {
            "columns": {
                "source_ids": self.source_ids,
                "vector_x": sum_x,
                "vector_y": sum_y,
            },
            "metadata": {
                "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "one_shot_contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "logical_reference_contract": AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "partner": "cupy",
                "softening": softening,
                "source_count": self.source_count,
                "frontier_row_count": row_count,
                "aggregate_contribution_row_count": aggregate_count,
                "exact_contribution_row_count": exact_count,
                "prepare_seconds": self.prepare_seconds,
                "partner_seconds": elapsed,
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "setup_seconds_excluded_from_hot_path": True,
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

    def run_with_prepared_frontier(
        self,
        prepared_frontier: object,
        *,
        row_capacity: int,
        softening: float = 0.0,
    ) -> dict[str, object]:
        if not hasattr(prepared_frontier, "run_device_columns"):
            raise ValueError("prepared_frontier must expose run_device_columns()")
        frontier = prepared_frontier.run_device_columns(
            row_capacity=int(row_capacity),
            **self.frontier_source_device_args(),
        )
        vector_sum = self.sum(frontier, softening=softening)
        return {
            "frontier": frontier,
            "vector_sum": vector_sum,
            "metadata": {
                "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "frontier_traversal_seconds": float(getattr(frontier, "traversal_seconds", 0.0)),
                "partner_seconds": float(vector_sum["metadata"]["partner_seconds"]),
                "hot_seconds": float(getattr(frontier, "traversal_seconds", 0.0))
                + float(vector_sum["metadata"]["partner_seconds"]),
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "frontier_columns_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


def prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
) -> PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy:
    return PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy(
        source_points,
        target_points,
        tree_nodes,
    )


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
    materializing frontier rows on host. Hot-loop callers should use
    prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy().
    """

    prepared = prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
        source_points,
        target_points,
        tree_nodes,
    )
    actual = prepared.sum(frontier_device_columns, softening=softening)
    actual["metadata"]["contract"] = AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT
    actual["metadata"]["prepared_contract"] = (
        AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT
    )
    actual["metadata"]["one_shot_wrapper"] = True
    actual["metadata"]["setup_seconds_excluded_from_hot_path"] = False
    return actual


def _numba_device_pointer(array: object) -> int:
    pointer = getattr(array, "device_ctypes_pointer", None)
    value = getattr(pointer, "value", None)
    if value is None:
        raise ValueError("Numba CUDA device array does not expose a device pointer")
    return int(value)


def _numba_aggregate_frontier_vector_sum_zero_kernel(cuda):
    @cuda.jit
    def kernel(sum_x, sum_y, counts, source_count):
        index = cuda.grid(1)
        if index < source_count:
            sum_x[index] = 0.0
            sum_y[index] = 0.0
        if index < 2:
            counts[index] = 0

    return kernel


def _numba_aggregate_frontier_weighted_vector_sum_kernel(cuda):
    import math

    @cuda.jit(fastmath=True)
    def kernel(
        frontier_source_ids,
        kind_codes,
        item_ids,
        source_x_by_id,
        source_y_by_id,
        source_mass_by_id,
        target_x_by_id,
        target_y_by_id,
        target_mass_by_id,
        node_cx_by_id,
        node_cy_by_id,
        node_mass_by_id,
        source_ordinal_by_id,
        softening_sq,
        sum_x,
        sum_y,
        counts,
        row_count,
        source_count,
    ):
        index = cuda.grid(1)
        if index >= row_count:
            return

        kind = kind_codes[index]
        if kind != 1 and kind != 2:
            return

        source_id = frontier_source_ids[index]
        source_x = source_x_by_id[source_id]
        source_y = source_y_by_id[source_id]
        source_mass = source_mass_by_id[source_id]
        item_id = item_ids[index]
        if kind == 1:
            target_x = node_cx_by_id[item_id]
            target_y = node_cy_by_id[item_id]
            target_mass = node_mass_by_id[item_id]
            cuda.atomic.add(counts, 0, 1)
        else:
            target_x = target_x_by_id[item_id]
            target_y = target_y_by_id[item_id]
            target_mass = target_mass_by_id[item_id]
            cuda.atomic.add(counts, 1, 1)

        dx = target_x - source_x
        dy = target_y - source_y
        dist_sq = dx * dx + dy * dy + softening_sq
        if dist_sq == 0.0:
            return
        inv_dist = 1.0 / math.sqrt(dist_sq)
        scale = source_mass * target_mass * inv_dist * inv_dist * inv_dist
        group = source_ordinal_by_id[source_id]
        if 0 <= group < source_count:
            cuda.atomic.add(sum_x, group, dx * scale)
            cuda.atomic.add(sum_y, group, dy * scale)

    return kernel


class PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba:
    """Prepared no-C++ Numba partner for M36 aggregate-frontier device columns.

    CuPy is used only as the current OptiX device-column carrier exposed by
    `as_cupy_columns()`. The continuation math and output accumulation are
    Numba CUDA JIT kernels.
    """

    def __init__(
        self,
        source_points: Iterable[object],
        target_points: Iterable[object],
        tree_nodes: Iterable[object],
        *,
        block_size: int = 256,
    ) -> None:
        from ..numba_partner_continuation import _import_numba_stack

        self.cuda, self.np = _import_numba_stack()
        self.block_size = int(block_size)
        if self.block_size <= 0:
            raise ValueError("block_size must be positive")
        self.sources = normalize_weighted_point_rows(source_points)
        self.targets = normalize_weighted_point_rows(target_points)
        self.nodes = _tree_node_rows(tree_nodes)
        if not self.sources:
            raise ValueError("at least one source point is required")
        if not self.targets:
            raise ValueError("at least one target point is required")
        if not self.nodes:
            raise ValueError("at least one aggregate tree node is required")

        source_ids_host = [int(point.id) for point in self.sources]
        target_ids_host = [int(point.id) for point in self.targets]
        node_ids_host = [int(node.id) for node in self.nodes]
        if min(source_ids_host) < 0 or min(target_ids_host) < 0 or min(node_ids_host) < 0:
            raise ValueError("Numba aggregate-frontier vector continuation requires non-negative dense ids")
        if len(set(source_ids_host)) != len(source_ids_host):
            raise ValueError("source point ids must be unique")
        if len(set(target_ids_host)) != len(target_ids_host):
            raise ValueError("target point ids must be unique")
        if len(set(node_ids_host)) != len(node_ids_host):
            raise ValueError("aggregate tree node ids must be unique")

        self.cuda.synchronize()
        start = time.perf_counter()

        np = self.np
        cuda = self.cuda
        self.source_ids = cuda.to_device(np.asarray(source_ids_host, dtype=np.int64))
        self.source_x = cuda.to_device(np.asarray([float(point.x) for point in self.sources], dtype=np.float64))
        self.source_y = cuda.to_device(np.asarray([float(point.y) for point in self.sources], dtype=np.float64))
        self.source_mass = cuda.to_device(np.asarray([float(point.mass) for point in self.sources], dtype=np.float64))

        target_ids = np.asarray(target_ids_host, dtype=np.int64)
        node_ids = np.asarray(node_ids_host, dtype=np.int64)
        max_source_id = max(source_ids_host)
        max_target_id = max(target_ids_host)
        max_node_id = max(node_ids_host)

        source_x_by_id = np.zeros((max_source_id + 1,), dtype=np.float64)
        source_y_by_id = np.zeros((max_source_id + 1,), dtype=np.float64)
        source_mass_by_id = np.zeros((max_source_id + 1,), dtype=np.float64)
        source_x_by_id[source_ids_host] = [float(point.x) for point in self.sources]
        source_y_by_id[source_ids_host] = [float(point.y) for point in self.sources]
        source_mass_by_id[source_ids_host] = [float(point.mass) for point in self.sources]
        source_ordinal_by_id = np.zeros((max_source_id + 1,), dtype=np.int64)
        source_ordinal_by_id[source_ids_host] = np.arange(len(self.sources), dtype=np.int64)

        target_x_by_id = np.zeros((max_target_id + 1,), dtype=np.float64)
        target_y_by_id = np.zeros((max_target_id + 1,), dtype=np.float64)
        target_mass_by_id = np.zeros((max_target_id + 1,), dtype=np.float64)
        target_x_by_id[target_ids] = [float(point.x) for point in self.targets]
        target_y_by_id[target_ids] = [float(point.y) for point in self.targets]
        target_mass_by_id[target_ids] = [float(point.mass) for point in self.targets]

        node_cx_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
        node_cy_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
        node_mass_by_id = np.zeros((max_node_id + 1,), dtype=np.float64)
        node_cx_by_id[node_ids] = [float(node.cx) for node in self.nodes]
        node_cy_by_id[node_ids] = [float(node.cy) for node in self.nodes]
        node_mass_by_id[node_ids] = [float(node.mass) for node in self.nodes]

        self.source_x_by_id = cuda.to_device(source_x_by_id)
        self.source_y_by_id = cuda.to_device(source_y_by_id)
        self.source_mass_by_id = cuda.to_device(source_mass_by_id)
        self.source_ordinal_by_id = cuda.to_device(source_ordinal_by_id)
        self.target_x_by_id = cuda.to_device(target_x_by_id)
        self.target_y_by_id = cuda.to_device(target_y_by_id)
        self.target_mass_by_id = cuda.to_device(target_mass_by_id)
        self.node_cx_by_id = cuda.to_device(node_cx_by_id)
        self.node_cy_by_id = cuda.to_device(node_cy_by_id)
        self.node_mass_by_id = cuda.to_device(node_mass_by_id)
        self.vector_x = cuda.device_array((len(self.sources),), dtype=np.float64)
        self.vector_y = cuda.device_array((len(self.sources),), dtype=np.float64)
        self.counts = cuda.device_array((2,), dtype=np.int64)

        cuda.synchronize()
        self.prepare_seconds = time.perf_counter() - start

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def source_ids_device_ptr(self) -> int:
        return _numba_device_pointer(self.source_ids)

    @property
    def source_x_device_ptr(self) -> int:
        return _numba_device_pointer(self.source_x)

    @property
    def source_y_device_ptr(self) -> int:
        return _numba_device_pointer(self.source_y)

    def frontier_source_device_args(self) -> dict[str, object]:
        return {
            "source_ids_device_ptr": self.source_ids_device_ptr,
            "source_x_device_ptr": self.source_x_device_ptr,
            "source_y_device_ptr": self.source_y_device_ptr,
            "source_count": self.source_count,
            "source_column_owners": (self,),
        }

    def sum(
        self,
        frontier_device_columns: object,
        *,
        softening: float = 0.0,
    ) -> dict[str, object]:
        softening = float(softening)
        if softening < 0.0:
            raise ValueError("softening must be non-negative")
        if not hasattr(frontier_device_columns, "as_cupy_columns"):
            raise ValueError("frontier_device_columns must expose as_cupy_columns()")
        if bool(getattr(frontier_device_columns, "overflow", False)):
            raise ValueError("cannot consume overflowed aggregate-frontier device columns")

        from ..numba_partner_continuation import _as_numba_cuda_vector
        from ..numba_partner_continuation import _cached_numba_kernel

        columns = frontier_device_columns.as_cupy_columns()
        row_count = int(getattr(frontier_device_columns, "row_count", len(columns["source_id"])))
        if row_count != int(columns["source_id"].shape[0]):
            raise ValueError("frontier row_count does not match source_id column length")
        cuda = self.cuda
        np = self.np
        frontier_source_ids = _as_numba_cuda_vector(
            columns["source_id"],
            name="frontier_source_ids",
            dtype=np.int64,
            cuda=cuda,
            np=np,
        )
        kind_codes = _as_numba_cuda_vector(
            columns["frontier_kind_code"],
            name="kind_codes",
            dtype=np.int64,
            cuda=cuda,
            np=np,
        )
        item_ids = _as_numba_cuda_vector(
            columns["item_id"],
            name="item_ids",
            dtype=np.int64,
            cuda=cuda,
            np=np,
        )

        cuda.synchronize()
        start = time.perf_counter()

        zero_grid = ((max(self.source_count, 2) + self.block_size - 1) // self.block_size,)
        _cached_numba_kernel(cuda, _numba_aggregate_frontier_vector_sum_zero_kernel)[
            zero_grid,
            self.block_size,
        ](self.vector_x, self.vector_y, self.counts, self.source_count)
        if row_count:
            grid = ((row_count + self.block_size - 1) // self.block_size,)
            _cached_numba_kernel(cuda, _numba_aggregate_frontier_weighted_vector_sum_kernel)[
                grid,
                self.block_size,
            ](
                frontier_source_ids,
                kind_codes,
                item_ids,
                self.source_x_by_id,
                self.source_y_by_id,
                self.source_mass_by_id,
                self.target_x_by_id,
                self.target_y_by_id,
                self.target_mass_by_id,
                self.node_cx_by_id,
                self.node_cy_by_id,
                self.node_mass_by_id,
                self.source_ordinal_by_id,
                softening * softening,
                self.vector_x,
                self.vector_y,
                self.counts,
                row_count,
                self.source_count,
            )
        counts_host = self.counts.copy_to_host()
        cuda.synchronize()
        elapsed = time.perf_counter() - start
        return {
            "columns": {
                "source_ids": self.source_ids,
                "vector_x": self.vector_x,
                "vector_y": self.vector_y,
            },
            "metadata": {
                "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT,
                "logical_reference_contract": AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "partner": "numba",
                "softening": softening,
                "source_count": self.source_count,
                "frontier_row_count": row_count,
                "aggregate_contribution_row_count": int(counts_host[0]),
                "exact_contribution_row_count": int(counts_host[1]),
                "prepare_seconds": self.prepare_seconds,
                "partner_seconds": elapsed,
                "block_size": self.block_size,
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "output_columns_reused": True,
                "setup_seconds_excluded_from_hot_path": True,
                "frontier_columns_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "requires_cupy_frontier_adapter": True,
                "numba_cuda_jit_used": True,
                "global_atomic_add_used": True,
                "raw_cuda_kernel_required": False,
                "app_reference_math": True,
                "native_engine_app_specific": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }

    def run_with_prepared_frontier(
        self,
        prepared_frontier: object,
        *,
        row_capacity: int,
        softening: float = 0.0,
    ) -> dict[str, object]:
        if not hasattr(prepared_frontier, "run_device_columns"):
            raise ValueError("prepared_frontier must expose run_device_columns()")
        frontier = prepared_frontier.run_device_columns(
            row_capacity=int(row_capacity),
            **self.frontier_source_device_args(),
        )
        vector_sum = self.sum(frontier, softening=softening)
        return {
            "frontier": frontier,
            "vector_sum": vector_sum,
            "metadata": {
                "contract": AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT,
                "frontier_traversal_seconds": float(getattr(frontier, "traversal_seconds", 0.0)),
                "partner_seconds": float(vector_sum["metadata"]["partner_seconds"]),
                "hot_seconds": float(getattr(frontier, "traversal_seconds", 0.0))
                + float(vector_sum["metadata"]["partner_seconds"]),
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "output_columns_reused": True,
                "frontier_columns_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "requires_cupy_frontier_adapter": True,
                "numba_cuda_jit_used": True,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


def prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba(
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    block_size: int = 256,
) -> PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba:
    return PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba(
        source_points,
        target_points,
        tree_nodes,
        block_size=block_size,
    )


def _numba_aggregate_tree_fused_weighted_vector_sum_kernel(cuda):
    import math

    @cuda.jit
    def kernel(
        source_ids,
        source_x,
        source_y,
        source_mass,
        target_ids,
        target_x,
        target_y,
        target_mass,
        node_cx,
        node_cy,
        node_half_size,
        node_mass,
        node_resume_index,
        node_subtree_end_index,
        source_leaf_node_index,
        member_offsets,
        member_indices,
        child_offsets,
        child_indices,
        root_index,
        theta,
        softening_sq,
        out_x,
        out_y,
        out_visited,
        out_aggregate,
        out_exact,
        status,
    ):
        source_index = cuda.grid(1)
        source_count = source_ids.shape[0]
        if source_index >= source_count:
            return

        node_count = node_cx.shape[0]
        if node_count < 1:
            cuda.atomic.max(status, 0, 1)
            return
        if root_index < 0 or root_index >= node_count:
            cuda.atomic.max(status, 0, 2)
            return

        source_leaf = source_leaf_node_index[source_index]
        if source_leaf < 0 or source_leaf >= node_count:
            cuda.atomic.max(status, 0, 4)
            return

        source_id = source_ids[source_index]
        sx = source_x[source_index]
        sy = source_y[source_index]
        smass = source_mass[source_index]
        sum_x = 0.0
        sum_y = 0.0
        visited = 0
        aggregate_count = 0
        exact_count = 0
        node_index = root_index

        while node_index >= 0:
            if node_index >= node_count:
                cuda.atomic.max(status, 0, 3)
                return
            visited += 1
            dx_node = node_cx[node_index] - sx
            dy_node = node_cy[node_index] - sy
            distance = math.sqrt(dx_node * dx_node + dy_node * dy_node)
            if distance == 0.0:
                opening_ratio = 1.0e300
            else:
                opening_ratio = (2.0 * node_half_size[node_index]) / distance

            subtree_end = node_subtree_end_index[node_index]
            contains_source = node_index <= source_leaf and source_leaf < subtree_end

            if (not contains_source) and opening_ratio < theta:
                dist_sq = dx_node * dx_node + dy_node * dy_node + softening_sq
                if dist_sq != 0.0:
                    inv_dist = 1.0 / math.sqrt(dist_sq)
                    scale = smass * node_mass[node_index] * inv_dist * inv_dist * inv_dist
                    sum_x += dx_node * scale
                    sum_y += dy_node * scale
                aggregate_count += 1
                node_index = node_resume_index[node_index]
                continue

            child_begin = child_offsets[node_index]
            child_end = child_offsets[node_index + 1]
            if child_begin < child_end:
                node_index = child_indices[child_begin]
                continue

            member_begin = member_offsets[node_index]
            member_end = member_offsets[node_index + 1]
            for offset in range(member_begin, member_end):
                target_index = member_indices[offset]
                target_id = target_ids[target_index]
                if target_id == source_id:
                    continue
                dx = target_x[target_index] - sx
                dy = target_y[target_index] - sy
                dist_sq = dx * dx + dy * dy + softening_sq
                if dist_sq != 0.0:
                    inv_dist = 1.0 / math.sqrt(dist_sq)
                    scale = smass * target_mass[target_index] * inv_dist * inv_dist * inv_dist
                    sum_x += dx * scale
                    sum_y += dy * scale
                exact_count += 1
            node_index = node_resume_index[node_index]

        out_x[source_index] = sum_x
        out_y[source_index] = sum_y
        out_visited[source_index] = visited
        out_aggregate[source_index] = aggregate_count
        out_exact[source_index] = exact_count

    return kernel


class PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda:
    """Prepared no-C++ Numba CUDA fused aggregate-tree vector-sum partner.

    This consumes generic weighted points and DFS/resume-index aggregate tree
    rows. It fuses tree traversal, opening-rule acceptance, exact fallback, and
    vector accumulation in one Numba CUDA kernel without emitting frontier rows.
    """

    def __init__(
        self,
        source_points: Iterable[object],
        target_points: Iterable[object],
        tree_nodes: Iterable[object],
        *,
        block_size: int = 128,
    ) -> None:
        from ..numba_partner_continuation import _import_numba_stack

        self.cuda, self.np = _import_numba_stack()
        self.block_size = int(block_size)
        if self.block_size <= 0:
            raise ValueError("block_size must be positive")
        self.sources = normalize_weighted_point_rows(source_points)
        self.targets = normalize_weighted_point_rows(target_points)
        self.nodes = _tree_node_rows(tree_nodes)
        roots = _tree_roots(self.nodes)
        if len(roots) != 1:
            raise ValueError("Numba CUDA fused aggregate-tree vector sum requires exactly one tree root")
        self.root_id = int(roots[0])

        source_ids_host = [int(point.id) for point in self.sources]
        target_ids_host = [int(point.id) for point in self.targets]
        if min(source_ids_host) < 0 or min(target_ids_host) < 0:
            raise ValueError("Numba CUDA fused aggregate-tree vector sum requires non-negative point ids")
        target_id_to_index = {point_id: index for index, point_id in enumerate(target_ids_host)}
        if len(target_id_to_index) != len(target_ids_host):
            raise ValueError("target point ids must be unique")
        source_leaf_by_id = _source_leaf_dfs_by_id(self.nodes)
        missing_sources = [source_id for source_id in source_ids_host if source_id not in source_leaf_by_id]
        if missing_sources:
            raise ValueError("every source point id must appear in exactly one aggregate-tree leaf")

        node_id_to_index = {int(node.id): index for index, node in enumerate(self.nodes)}
        self.root_index = int(node_id_to_index[self.root_id])
        node_count = len(self.nodes)
        child_offsets = [0]
        child_indices: list[int] = []
        member_offsets = [0]
        member_indices: list[int] = []
        for node in self.nodes:
            for child_id in node.child_ids:
                child_indices.append(int(node_id_to_index[int(child_id)]))
            child_offsets.append(len(child_indices))
            for member_id in node.member_ids:
                if int(member_id) not in target_id_to_index:
                    raise ValueError("aggregate tree member ids must all be present in target points")
                member_indices.append(int(target_id_to_index[int(member_id)]))
            member_offsets.append(len(member_indices))

        cuda = self.cuda
        np = self.np
        cuda.synchronize()
        start = time.perf_counter()

        self.source_ids = cuda.to_device(np.asarray(source_ids_host, dtype=np.int64))
        self.source_x = cuda.to_device(np.asarray([float(point.x) for point in self.sources], dtype=np.float64))
        self.source_y = cuda.to_device(np.asarray([float(point.y) for point in self.sources], dtype=np.float64))
        self.source_mass = cuda.to_device(np.asarray([float(point.mass) for point in self.sources], dtype=np.float64))
        self.target_ids = cuda.to_device(np.asarray(target_ids_host, dtype=np.int64))
        self.target_x = cuda.to_device(np.asarray([float(point.x) for point in self.targets], dtype=np.float64))
        self.target_y = cuda.to_device(np.asarray([float(point.y) for point in self.targets], dtype=np.float64))
        self.target_mass = cuda.to_device(np.asarray([float(point.mass) for point in self.targets], dtype=np.float64))
        self.node_cx = cuda.to_device(np.asarray([float(node.cx) for node in self.nodes], dtype=np.float64))
        self.node_cy = cuda.to_device(np.asarray([float(node.cy) for node in self.nodes], dtype=np.float64))
        self.node_half_size = cuda.to_device(
            np.asarray([float(node.half_size) for node in self.nodes], dtype=np.float64)
        )
        self.node_mass = cuda.to_device(np.asarray([float(node.mass) for node in self.nodes], dtype=np.float64))
        self.node_resume_index = cuda.to_device(
            np.asarray(
                [-1 if node.resume_index is None else int(node.resume_index) for node in self.nodes],
                dtype=np.int64,
            )
        )
        self.node_subtree_end_index = cuda.to_device(
            np.asarray(
                [node_count if node.resume_index is None else int(node.resume_index) for node in self.nodes],
                dtype=np.int64,
            )
        )
        self.source_leaf_node_index = cuda.to_device(
            np.asarray([int(source_leaf_by_id[source_id]) for source_id in source_ids_host], dtype=np.int64)
        )
        self.member_offsets = cuda.to_device(np.asarray(member_offsets, dtype=np.int64))
        self.member_indices = cuda.to_device(np.asarray(member_indices, dtype=np.int64))
        self.child_offsets = cuda.to_device(np.asarray(child_offsets, dtype=np.int64))
        self.child_indices = cuda.to_device(np.asarray(child_indices, dtype=np.int64))
        self.vector_x = cuda.device_array((len(self.sources),), dtype=np.float64)
        self.vector_y = cuda.device_array((len(self.sources),), dtype=np.float64)
        self.visited_counts = cuda.device_array((len(self.sources),), dtype=np.int64)
        self.aggregate_counts = cuda.device_array((len(self.sources),), dtype=np.int64)
        self.exact_counts = cuda.device_array((len(self.sources),), dtype=np.int64)
        self.status = cuda.to_device(np.zeros((1,), dtype=np.int32))

        cuda.synchronize()
        self.prepare_seconds = time.perf_counter() - start

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def target_count(self) -> int:
        return len(self.targets)

    @property
    def tree_node_count(self) -> int:
        return len(self.nodes)

    def sum(
        self,
        *,
        theta: float,
        softening: float = 0.0,
        use_cuda_events: bool = False,
    ) -> dict[str, object]:
        from ..numba_partner_continuation import _cached_numba_kernel

        theta = float(theta)
        softening = float(softening)
        if theta <= 0.0:
            raise ValueError("theta must be positive")
        if softening < 0.0:
            raise ValueError("softening must be non-negative")

        cuda = self.cuda
        np = self.np
        self.status.copy_to_device(np.zeros((1,), dtype=np.int32))
        grid = ((self.source_count + self.block_size - 1) // self.block_size,)
        stream = cuda.stream()
        kernel = _cached_numba_kernel(cuda, _numba_aggregate_tree_fused_weighted_vector_sum_kernel)
        start_event = cuda.event(timing=True) if use_cuda_events else None
        end_event = cuda.event(timing=True) if use_cuda_events else None

        cuda.synchronize()
        start = time.perf_counter()
        if start_event is not None:
            start_event.record(stream)
        kernel[grid, self.block_size, stream](
            self.source_ids,
            self.source_x,
            self.source_y,
            self.source_mass,
            self.target_ids,
            self.target_x,
            self.target_y,
            self.target_mass,
            self.node_cx,
            self.node_cy,
            self.node_half_size,
            self.node_mass,
            self.node_resume_index,
            self.node_subtree_end_index,
            self.source_leaf_node_index,
            self.member_offsets,
            self.member_indices,
            self.child_offsets,
            self.child_indices,
            self.root_index,
            theta,
            softening * softening,
            self.vector_x,
            self.vector_y,
            self.visited_counts,
            self.aggregate_counts,
            self.exact_counts,
            self.status,
        )
        if end_event is not None:
            end_event.record(stream)
            end_event.synchronize()
            kernel_event_ms = float(start_event.elapsed_time(end_event))
        else:
            stream.synchronize()
            kernel_event_ms = None

        status = int(self.status.copy_to_host()[0])
        if status != 0:
            raise RuntimeError(f"Numba CUDA fused aggregate-tree vector sum failed with status {status}")
        aggregate_host = self.aggregate_counts.copy_to_host()
        exact_host = self.exact_counts.copy_to_host()
        visited_host = self.visited_counts.copy_to_host()
        cuda.synchronize()
        elapsed = time.perf_counter() - start
        aggregate_count = int(aggregate_host.sum())
        exact_count = int(exact_host.sum())
        return {
            "columns": {
                "source_ids": self.source_ids,
                "vector_x": self.vector_x,
                "vector_y": self.vector_y,
                "visited_counts": self.visited_counts,
                "aggregate_counts": self.aggregate_counts,
                "exact_counts": self.exact_counts,
            },
            "metadata": {
                "contract": AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT,
                "logical_reference_contract": AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
                "partner": "numba_cuda",
                "theta": theta,
                "softening": softening,
                "source_count": self.source_count,
                "target_count": self.target_count,
                "tree_node_count": self.tree_node_count,
                "aggregate_contribution_row_count": aggregate_count,
                "exact_contribution_row_count": exact_count,
                "contribution_row_count": aggregate_count + exact_count,
                "visited_node_count": int(visited_host.sum()),
                "prepare_seconds": self.prepare_seconds,
                "partner_seconds": elapsed,
                "kernel_event_ms": kernel_event_ms,
                "block_size": self.block_size,
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "target_columns_reused": True,
                "aggregate_tree_columns_resident": True,
                "output_columns_reused": True,
                "setup_seconds_excluded_from_hot_path": True,
                "frontier_rows_emitted": False,
                "frontier_rows_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "count_columns_copied_to_host_for_metadata": True,
                "numba_cuda_jit_used": True,
                "raw_cuda_kernel_required": False,
                "app_reference_math": True,
                "native_engine_app_specific": False,
                "rt_cores_used": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


def prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    block_size: int = 128,
) -> PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda:
    return PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda(
        source_points,
        target_points,
        tree_nodes,
        block_size=block_size,
    )


def sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
    source_points: Iterable[object],
    target_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    theta: float,
    softening: float = 0.0,
    block_size: int = 128,
) -> dict[str, object]:
    prepared = prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
        source_points,
        target_points,
        tree_nodes,
        block_size=block_size,
    )
    actual = prepared.sum(theta=theta, softening=softening)
    actual["metadata"]["one_shot_wrapper"] = True
    actual["metadata"]["setup_seconds_excluded_from_hot_path"] = False
    return actual
