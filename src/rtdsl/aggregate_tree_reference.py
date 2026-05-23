from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence


AGGREGATE_OPENING_ROWS_2D_CONTRACT = "generic_aggregate_opening_rows_2d_v1"
AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT = "generic_bucketized_aggregate_tree_2d_v1"
AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT = "generic_aggregate_tree_opening_frontier_2d_v1"
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


@dataclass(frozen=True)
class WeightedPointRow:
    id: int
    x: float
    y: float
    mass: float


@dataclass(frozen=True)
class AggregateNodeRow:
    id: int
    cx: float
    cy: float
    half_size: float
    mass: float
    member_ids: tuple[int, ...]


@dataclass(frozen=True)
class AggregateTreeNodeRow:
    id: int
    cx: float
    cy: float
    half_size: float
    mass: float
    member_ids: tuple[int, ...]
    child_ids: tuple[int, ...]
    depth: int
    dfs_index: int
    resume_index: int | None
    cell_cx: float
    cell_cy: float
    is_leaf: bool


def _get_value(row, names: Sequence[str], label: str):
    if isinstance(row, Mapping):
        for name in names:
            if name in row:
                return row[name]
    for name in names:
        if hasattr(row, name):
            return getattr(row, name)
    raise ValueError(f"{label} row is missing one of: {', '.join(names)}")


def normalize_weighted_point_rows(rows: Iterable[object]) -> tuple[WeightedPointRow, ...]:
    normalized: list[WeightedPointRow] = []
    seen: set[int] = set()
    for row in rows:
        point_id = int(_get_value(row, ("id", "point_id", "body_id", "source_id"), "weighted point"))
        if point_id in seen:
            raise ValueError(f"duplicate weighted point id: {point_id}")
        seen.add(point_id)
        normalized.append(
            WeightedPointRow(
                id=point_id,
                x=float(_get_value(row, ("x",), "weighted point")),
                y=float(_get_value(row, ("y",), "weighted point")),
                mass=float(_get_value(row, ("mass", "weight"), "weighted point")),
            )
        )
    if not normalized:
        raise ValueError("at least one weighted point row is required")
    return tuple(normalized)


def normalize_aggregate_node_rows(rows: Iterable[object]) -> tuple[AggregateNodeRow, ...]:
    normalized: list[AggregateNodeRow] = []
    seen: set[int] = set()
    for row in rows:
        node_id = int(_get_value(row, ("id", "node_id", "aggregate_id"), "aggregate node"))
        if node_id in seen:
            raise ValueError(f"duplicate aggregate node id: {node_id}")
        seen.add(node_id)
        member_ids = _get_value(row, ("member_ids", "members", "point_ids", "body_ids"), "aggregate node")
        normalized.append(
            AggregateNodeRow(
                id=node_id,
                cx=float(_get_value(row, ("cx", "x"), "aggregate node")),
                cy=float(_get_value(row, ("cy", "y"), "aggregate node")),
                half_size=float(_get_value(row, ("half_size", "radius", "extent"), "aggregate node")),
                mass=float(_get_value(row, ("mass", "weight"), "aggregate node")),
                member_ids=tuple(int(item) for item in member_ids),
            )
        )
    if not normalized:
        raise ValueError("at least one aggregate node row is required")
    for node in normalized:
        if node.half_size < 0:
            raise ValueError("aggregate node half_size must be non-negative")
        if node.mass < 0:
            raise ValueError("aggregate node mass must be non-negative")
    return tuple(normalized)


def morton_code_2d(
    x: float,
    y: float,
    *,
    min_x: float,
    min_y: float,
    span: float,
    bits: int = 16,
) -> int:
    """Return a 2-D Morton/Z-order code for a point in a square domain."""

    if bits < 1 or bits > 30:
        raise ValueError("bits must be between 1 and 30")
    if span <= 0.0:
        raise ValueError("span must be positive")
    scale = (1 << bits) - 1
    xi = int(max(0, min(scale, round(((float(x) - min_x) / span) * scale))))
    yi = int(max(0, min(scale, round(((float(y) - min_y) / span) * scale))))
    code = 0
    for bit in range(bits):
        code |= ((xi >> bit) & 1) << (2 * bit)
        code |= ((yi >> bit) & 1) << (2 * bit + 1)
    return code


def _tree_node_rows(rows: Iterable[object]) -> tuple[AggregateTreeNodeRow, ...]:
    normalized: list[AggregateTreeNodeRow] = []
    seen: set[int] = set()
    for row in rows:
        node_id = int(_get_value(row, ("id", "node_id", "aggregate_id"), "aggregate tree node"))
        if node_id in seen:
            raise ValueError(f"duplicate aggregate tree node id: {node_id}")
        seen.add(node_id)
        member_ids = _get_value(row, ("member_ids", "members", "point_ids", "body_ids"), "aggregate tree node")
        child_ids = _get_value(row, ("child_ids", "children"), "aggregate tree node")
        resume_index = _get_value(row, ("resume_index", "next_dfs_index", "autorope_index"), "aggregate tree node")
        normalized.append(
            AggregateTreeNodeRow(
                id=node_id,
                cx=float(_get_value(row, ("cx", "x"), "aggregate tree node")),
                cy=float(_get_value(row, ("cy", "y"), "aggregate tree node")),
                half_size=float(_get_value(row, ("half_size", "radius", "extent"), "aggregate tree node")),
                mass=float(_get_value(row, ("mass", "weight"), "aggregate tree node")),
                member_ids=tuple(int(item) for item in member_ids),
                child_ids=tuple(int(item) for item in child_ids),
                depth=int(_get_value(row, ("depth",), "aggregate tree node")),
                dfs_index=int(_get_value(row, ("dfs_index",), "aggregate tree node")),
                resume_index=None if resume_index is None else int(resume_index),
                cell_cx=float(_get_value(row, ("cell_cx", "spatial_cx"), "aggregate tree node")),
                cell_cy=float(_get_value(row, ("cell_cy", "spatial_cy"), "aggregate tree node")),
                is_leaf=bool(_get_value(row, ("is_leaf",), "aggregate tree node")),
            )
        )
    if not normalized:
        raise ValueError("at least one aggregate tree node row is required")
    ids = {node.id for node in normalized}
    dfs_indices = {node.dfs_index for node in normalized}
    if dfs_indices != set(range(len(normalized))):
        raise ValueError("aggregate tree node dfs_index values must be contiguous from zero")
    for node in normalized:
        if node.half_size < 0:
            raise ValueError("aggregate tree node half_size must be non-negative")
        if node.mass < 0:
            raise ValueError("aggregate tree node mass must be non-negative")
        for child_id in node.child_ids:
            if child_id not in ids:
                raise ValueError(f"aggregate tree node child id {child_id} is not present")
    return tuple(sorted(normalized, key=lambda node: node.dfs_index))


def build_bucketized_aggregate_tree_2d(
    source_points: Iterable[object],
    *,
    bucket_size: int = 32,
    max_depth: int = 32,
    morton_bits: int = 16,
    bounds_padding: float = 1.0e-9,
) -> dict[str, object]:
    """Build an app-agnostic bucketized 2-D aggregate tree reference.

    The builder deliberately exposes generic aggregate rows only: weighted
    points, bucketized leaves, DFS order, and resume indices. It does not encode
    a Barnes-Hut ABI, force law, or native RT traversal policy.
    """

    if bucket_size < 1:
        raise ValueError("bucket_size must be positive")
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    if bounds_padding < 0.0:
        raise ValueError("bounds_padding must be non-negative")
    points = normalize_weighted_point_rows(source_points)
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    span = max(max_x - min_x, max_y - min_y)
    if span == 0.0:
        span = 1.0
    span += bounds_padding * 2.0
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    half_size = span / 2.0
    square_min_x = center_x - half_size
    square_min_y = center_y - half_size

    ordered_points = tuple(
        sorted(
            points,
            key=lambda point: (
                morton_code_2d(
                    point.x,
                    point.y,
                    min_x=square_min_x,
                    min_y=square_min_y,
                    span=span,
                    bits=morton_bits,
                ),
                point.id,
            ),
        )
    )

    mutable_nodes: list[dict[str, object]] = []

    def add_node(
        members: tuple[WeightedPointRow, ...],
        *,
        cell_cx: float,
        cell_cy: float,
        node_half_size: float,
        depth: int,
    ) -> int:
        mass = sum(point.mass for point in members)
        if mass == 0.0:
            center_mass_x = sum(point.x for point in members) / len(members)
            center_mass_y = sum(point.y for point in members) / len(members)
        else:
            center_mass_x = sum(point.x * point.mass for point in members) / mass
            center_mass_y = sum(point.y * point.mass for point in members) / mass
        node_id = len(mutable_nodes) + 1
        dfs_index = len(mutable_nodes)
        is_leaf = len(members) <= bucket_size or depth >= max_depth or node_half_size == 0.0
        mutable_nodes.append(
            {
                "id": node_id,
                "cx": center_mass_x,
                "cy": center_mass_y,
                "half_size": node_half_size,
                "mass": mass,
                "member_ids": tuple(point.id for point in members),
                "child_ids": (),
                "depth": depth,
                "dfs_index": dfs_index,
                "resume_index": None,
                "cell_cx": cell_cx,
                "cell_cy": cell_cy,
                "is_leaf": is_leaf,
            }
        )
        if not is_leaf:
            quadrants: list[list[WeightedPointRow]] = [[], [], [], []]
            for point in members:
                east = point.x >= cell_cx
                north = point.y >= cell_cy
                quadrant = (1 if east else 0) + (2 if north else 0)
                quadrants[quadrant].append(point)
            child_half_size = node_half_size / 2.0
            offsets = (
                (-child_half_size, -child_half_size),
                (child_half_size, -child_half_size),
                (-child_half_size, child_half_size),
                (child_half_size, child_half_size),
            )
            child_ids: list[int] = []
            for quadrant, quadrant_members in enumerate(quadrants):
                if not quadrant_members:
                    continue
                offset_x, offset_y = offsets[quadrant]
                child_ids.append(
                    add_node(
                        tuple(quadrant_members),
                        cell_cx=cell_cx + offset_x,
                        cell_cy=cell_cy + offset_y,
                        node_half_size=child_half_size,
                        depth=depth + 1,
                    )
                )
            mutable_nodes[dfs_index]["child_ids"] = tuple(child_ids)
            mutable_nodes[dfs_index]["is_leaf"] = not child_ids
        return node_id

    add_node(ordered_points, cell_cx=center_x, cell_cy=center_y, node_half_size=half_size, depth=0)
    id_to_index = {int(node["id"]): index for index, node in enumerate(mutable_nodes)}

    def subtree_end_index(index: int) -> int:
        child_ids = tuple(int(child_id) for child_id in mutable_nodes[index]["child_ids"])
        if not child_ids:
            return index + 1
        return max(subtree_end_index(id_to_index[child_id]) for child_id in child_ids)

    for index, node in enumerate(mutable_nodes):
        end_index = subtree_end_index(index)
        node["resume_index"] = end_index if end_index < len(mutable_nodes) else None

    nodes = tuple(
        AggregateTreeNodeRow(
            id=int(node["id"]),
            cx=float(node["cx"]),
            cy=float(node["cy"]),
            half_size=float(node["half_size"]),
            mass=float(node["mass"]),
            member_ids=tuple(int(item) for item in node["member_ids"]),
            child_ids=tuple(int(item) for item in node["child_ids"]),
            depth=int(node["depth"]),
            dfs_index=int(node["dfs_index"]),
            resume_index=None if node["resume_index"] is None else int(node["resume_index"]),
            cell_cx=float(node["cell_cx"]),
            cell_cy=float(node["cell_cy"]),
            is_leaf=bool(node["is_leaf"]),
        )
        for node in mutable_nodes
    )
    leaf_nodes = tuple(node for node in nodes if node.is_leaf)
    return {
        "nodes": nodes,
        "ordered_source_ids": tuple(point.id for point in ordered_points),
        "summary": {
            "source_count": len(points),
            "tree_node_count": len(nodes),
            "leaf_node_count": len(leaf_nodes),
            "max_depth": max(node.depth for node in nodes),
            "bucket_size": bucket_size,
            "max_leaf_member_count": max(len(node.member_ids) for node in leaf_nodes),
            "morton_bits": morton_bits,
        },
        "metadata": {
            "contract": AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT,
            "bucket_size": bucket_size,
            "max_depth": max_depth,
            "morton_ordered": True,
            "dfs_ordered": True,
            "resume_index_metadata": True,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def evaluate_aggregate_tree_opening_frontier_2d(
    source_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    theta: float,
    deduplicate_fallback_targets: bool = True,
) -> dict[str, object]:
    """Traverse aggregate tree rows with the generic opening predicate."""

    theta = float(theta)
    if theta <= 0.0:
        raise ValueError("theta must be positive")
    sources = normalize_weighted_point_rows(source_points)
    nodes = _tree_node_rows(tree_nodes)
    node_by_id = {node.id: node for node in nodes}
    child_ids = {child_id for node in nodes for child_id in node.child_ids}
    root_ids = tuple(node.id for node in nodes if node.id not in child_ids)
    if not root_ids:
        raise ValueError("aggregate tree must contain at least one root")

    accepted_rows: list[dict[str, object]] = []
    fallback_rows: list[dict[str, object]] = []
    fallback_seen: set[tuple[int, int]] = set()
    per_source: dict[int, dict[str, int]] = {
        source.id: {
            "visited_node_count": 0,
            "accepted_aggregate_count": 0,
            "fallback_exact_count": 0,
        }
        for source in sources
    }

    def visit(source: WeightedPointRow, node: AggregateTreeNodeRow) -> None:
        per_source[source.id]["visited_node_count"] += 1
        dx = node.cx - source.x
        dy = node.cy - source.y
        distance = math.hypot(dx, dy)
        opening_ratio = math.inf if distance == 0.0 else (2.0 * node.half_size) / distance
        contains_source = source.id in node.member_ids
        if not contains_source and opening_ratio < theta:
            accepted_rows.append(
                {
                    "source_id": source.id,
                    "aggregate_id": node.id,
                    "distance": distance,
                    "opening_ratio": opening_ratio,
                    "aggregate_mass": node.mass,
                    "aggregate_cx": node.cx,
                    "aggregate_cy": node.cy,
                    "dfs_index": node.dfs_index,
                    "resume_index": node.resume_index,
                }
            )
            per_source[source.id]["accepted_aggregate_count"] += 1
            return
        if node.child_ids:
            for child_id in node.child_ids:
                visit(source, node_by_id[child_id])
            return
        for target_id in node.member_ids:
            if target_id == source.id:
                continue
            key = (source.id, target_id)
            if deduplicate_fallback_targets and key in fallback_seen:
                continue
            fallback_seen.add(key)
            fallback_rows.append(
                {
                    "source_id": source.id,
                    "target_id": target_id,
                    "aggregate_id": node.id,
                    "distance_to_aggregate": distance,
                    "opening_ratio": opening_ratio,
                    "dfs_index": node.dfs_index,
                    "resume_index": node.resume_index,
                }
            )
            per_source[source.id]["fallback_exact_count"] += 1

    for source in sources:
        for root_id in root_ids:
            visit(source, node_by_id[root_id])

    summary = {
        "source_count": len(sources),
        "tree_node_count": len(nodes),
        "root_count": len(root_ids),
        "leaf_node_count": sum(1 for node in nodes if node.is_leaf),
        "max_depth": max(node.depth for node in nodes),
        "visited_node_total": sum(row["visited_node_count"] for row in per_source.values()),
        "accepted_aggregate_row_count": len(accepted_rows),
        "fallback_exact_row_count": len(fallback_rows),
        "sources_with_any_output": sum(
            1
            for row in per_source.values()
            if row["accepted_aggregate_count"] or row["fallback_exact_count"]
        ),
    }
    return {
        "accepted_aggregate_rows": tuple(accepted_rows),
        "fallback_exact_rows": tuple(fallback_rows),
        "per_source_summary": per_source,
        "summary": summary,
        "metadata": {
            "contract": AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT,
            "theta": theta,
            "deduplicate_fallback_targets": deduplicate_fallback_targets,
            "hierarchical_frontier": True,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


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
    """Convert opening-frontier rows into generic weighted vector contributions."""

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
    """Group generic vector contribution rows by source and sum x/y components."""

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
    """Stream weighted inverse-square contributions directly into vector sums."""

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
    """Estimate intermediate-row materialization pressure for vector sums."""

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
    """Fuse aggregate-tree opening traversal with weighted vector accumulation.

    This is the app-agnostic reference for the native/partner lowering target.
    It deliberately does not materialize opening-frontier rows or contribution
    rows, and it does not encode Barnes-Hut app names or timestep semantics.
    """

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
    child_ids = {child_id for node in nodes for child_id in node.child_ids}
    root_ids = tuple(node.id for node in nodes if node.id not in child_ids)
    if not root_ids:
        raise ValueError("aggregate tree must contain at least one root")

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
            contains_source = source.id in node_member_sets[node.id]
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
            "intermediate_frontier_rows_materialized": False,
            "intermediate_contribution_rows_materialized": False,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }


def _candidate_node_ids_by_source(
    candidate_rows: Iterable[object] | None,
    *,
    source_ids: set[int],
    node_ids: set[int],
) -> dict[int, tuple[int, ...]] | None:
    if candidate_rows is None:
        return None
    by_source: dict[int, list[int]] = {source_id: [] for source_id in source_ids}
    seen: dict[int, set[int]] = {source_id: set() for source_id in source_ids}
    for row in candidate_rows:
        source_id = int(_get_value(row, ("query_id", "source_id", "point_id"), "candidate"))
        node_id = int(_get_value(row, ("neighbor_id", "aggregate_id", "node_id"), "candidate"))
        if source_id not in source_ids:
            raise ValueError(f"candidate source_id {source_id} is not present in source rows")
        if node_id not in node_ids:
            raise ValueError(f"candidate aggregate node id {node_id} is not present in aggregate nodes")
        if node_id in seen[source_id]:
            continue
        seen[source_id].add(node_id)
        by_source[source_id].append(node_id)
    return {source_id: tuple(nodes) for source_id, nodes in by_source.items()}


def evaluate_aggregate_opening_rows_2d(
    source_points: Iterable[object],
    aggregate_nodes: Iterable[object],
    *,
    theta: float,
    candidate_rows: Iterable[object] | None = None,
    deduplicate_fallback_targets: bool = True,
) -> dict[str, object]:
    """Evaluate a generic 2-D aggregate opening predicate.

    The contract is intentionally app-name-free. It accepts weighted source
    points and aggregate nodes, then emits rows that either accept an aggregate
    node as a source's approximation target or fall back to exact member IDs.
    """

    theta = float(theta)
    if theta <= 0.0:
        raise ValueError("theta must be positive")
    sources = normalize_weighted_point_rows(source_points)
    nodes = normalize_aggregate_node_rows(aggregate_nodes)
    source_by_id = {source.id: source for source in sources}
    node_by_id = {node.id: node for node in nodes}
    candidate_by_source = _candidate_node_ids_by_source(
        candidate_rows,
        source_ids=set(source_by_id),
        node_ids=set(node_by_id),
    )
    accepted_rows: list[dict[str, object]] = []
    fallback_rows: list[dict[str, object]] = []
    fallback_seen: set[tuple[int, int]] = set()
    per_source: dict[int, dict[str, int]] = {
        source.id: {
            "candidate_node_count": 0,
            "accepted_aggregate_count": 0,
            "fallback_exact_count": 0,
        }
        for source in sources
    }

    for source in sources:
        candidate_node_ids = (
            tuple(sorted(candidate_by_source[source.id]))
            if candidate_by_source is not None
            else tuple(node.id for node in nodes)
        )
        per_source[source.id]["candidate_node_count"] = len(candidate_node_ids)
        for node_id in candidate_node_ids:
            node = node_by_id[node_id]
            dx = node.cx - source.x
            dy = node.cy - source.y
            distance = math.hypot(dx, dy)
            opening_ratio = math.inf if distance == 0.0 else (2.0 * node.half_size) / distance
            contains_source = source.id in node.member_ids
            if not contains_source and opening_ratio < theta:
                accepted_rows.append(
                    {
                        "source_id": source.id,
                        "aggregate_id": node.id,
                        "distance": distance,
                        "opening_ratio": opening_ratio,
                        "aggregate_mass": node.mass,
                        "aggregate_cx": node.cx,
                        "aggregate_cy": node.cy,
                    }
                )
                per_source[source.id]["accepted_aggregate_count"] += 1
                continue
            for target_id in node.member_ids:
                if target_id == source.id:
                    continue
                key = (source.id, target_id)
                if deduplicate_fallback_targets and key in fallback_seen:
                    continue
                fallback_seen.add(key)
                fallback_rows.append(
                    {
                        "source_id": source.id,
                        "target_id": target_id,
                        "aggregate_id": node.id,
                        "distance_to_aggregate": distance,
                        "opening_ratio": opening_ratio,
                    }
                )
                per_source[source.id]["fallback_exact_count"] += 1

    summary = {
        "source_count": len(sources),
        "aggregate_node_count": len(nodes),
        "candidate_node_total": sum(row["candidate_node_count"] for row in per_source.values()),
        "accepted_aggregate_row_count": len(accepted_rows),
        "fallback_exact_row_count": len(fallback_rows),
        "sources_with_any_output": sum(
            1
            for row in per_source.values()
            if row["accepted_aggregate_count"] or row["fallback_exact_count"]
        ),
    }
    return {
        "accepted_aggregate_rows": tuple(accepted_rows),
        "fallback_exact_rows": tuple(fallback_rows),
        "per_source_summary": per_source,
        "summary": summary,
        "metadata": {
            "contract": AGGREGATE_OPENING_ROWS_2D_CONTRACT,
            "theta": theta,
            "candidate_rows_required": candidate_rows is not None,
            "deduplicate_fallback_targets": deduplicate_fallback_targets,
            "native_engine_app_specific": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }
