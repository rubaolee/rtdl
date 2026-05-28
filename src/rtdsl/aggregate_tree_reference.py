from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence


AGGREGATE_OPENING_ROWS_2D_CONTRACT = "generic_aggregate_opening_rows_2d_v1"
AGGREGATE_BUCKETIZED_TREE_2D_CONTRACT = "generic_bucketized_aggregate_tree_2d_v1"
AGGREGATE_TREE_OPENING_FRONTIER_2D_CONTRACT = "generic_aggregate_tree_opening_frontier_2d_v1"
AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE = "AGGREGATE_FRONTIER_COLLECT_2D"
AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT = "generic_aggregate_frontier_collect_2d_v1"
AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT = (
    "generic_aggregate_frontier_collect_2d_native_abi_v1"
)
AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA = (
    "source_id",
    "frontier_kind_code",
    "item_id",
    "owner_aggregate_id",
    "dfs_index",
    "resume_index",
    "metadata_flags",
)
AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE = 0
AGGREGATE_FRONTIER_KIND_AGGREGATE = "aggregate"
AGGREGATE_FRONTIER_KIND_EXACT = "exact"
AGGREGATE_FRONTIER_KIND_CODES = {
    AGGREGATE_FRONTIER_KIND_AGGREGATE: 1,
    AGGREGATE_FRONTIER_KIND_EXACT: 2,
}
AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY = "fail_closed_before_result_materialization"
AGGREGATE_FRONTIER_COLLECT_NATIVE_REQUIRED_SYMBOLS = (
    "rtdl_embree_collect_aggregate_frontier_2d",
    "rtdl_optix_collect_aggregate_frontier_2d",
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


class AggregateFrontierOverflowError(RuntimeError):
    """Raised when aggregate-frontier collection exceeds an exact capacity."""


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


def _tree_roots(nodes: Sequence[AggregateTreeNodeRow]) -> tuple[int, ...]:
    child_ids = {child_id for node in nodes for child_id in node.child_ids}
    root_ids = tuple(node.id for node in nodes if node.id not in child_ids)
    if not root_ids:
        raise ValueError("aggregate tree must contain at least one root")
    return root_ids


def _tree_subtree_end_by_id(nodes: Sequence[AggregateTreeNodeRow]) -> dict[int, int]:
    return {node.id: (node.resume_index if node.resume_index is not None else len(nodes)) for node in nodes}


def _source_leaf_dfs_by_id(nodes: Sequence[AggregateTreeNodeRow]) -> dict[int, int]:
    source_leaf: dict[int, int] = {}
    for node in nodes:
        if not node.is_leaf:
            continue
        for member_id in node.member_ids:
            source_leaf.setdefault(member_id, node.dfs_index)
    return source_leaf


def _node_contains_source(
    node: AggregateTreeNodeRow,
    source_id: int,
    *,
    source_leaf_dfs_by_id: Mapping[int, int],
    subtree_end_by_id: Mapping[int, int],
    node_member_sets: Mapping[int, set[int]] | None = None,
) -> bool:
    """Return whether a DFS-ordered aggregate subtree contains a source id."""

    source_leaf_dfs = source_leaf_dfs_by_id.get(source_id)
    if source_leaf_dfs is not None:
        return node.dfs_index <= source_leaf_dfs < subtree_end_by_id[node.id]
    if node_member_sets is None:
        return source_id in node.member_ids
    return source_id in node_member_sets[node.id]


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
    root_ids = _tree_roots(nodes)
    subtree_end_by_id = _tree_subtree_end_by_id(nodes)
    source_leaf_dfs_by_id = _source_leaf_dfs_by_id(nodes)
    node_member_sets = {node.id: set(node.member_ids) for node in nodes}

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
        contains_source = _node_contains_source(
            node,
            source.id,
            source_leaf_dfs_by_id=source_leaf_dfs_by_id,
            subtree_end_by_id=subtree_end_by_id,
            node_member_sets=node_member_sets,
        )
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


def collect_aggregate_frontier_2d(
    source_points: Iterable[object],
    tree_nodes: Iterable[object],
    *,
    theta: float,
    max_rows_per_source: int | None = None,
    max_total_rows: int | None = None,
    deduplicate_fallback_targets: bool = True,
    include_debug_diagnostics: bool = False,
) -> dict[str, object]:
    """Collect aggregate-frontier IDs without applying app/workload math.

    This is the app-agnostic frontier row-emission contract for future
    native/partner lowerings. It walks prepared aggregate tree rows and emits
    only generic IDs, kind codes, offsets, and reserved metadata flags by
    default. Optional debug diagnostics are returned as a separate side channel.
    Force laws, scoring, and reductions remain app or partner code.
    """

    theta = float(theta)
    if theta <= 0.0:
        raise ValueError("theta must be positive")
    if max_rows_per_source is not None and int(max_rows_per_source) < 0:
        raise ValueError("max_rows_per_source must be non-negative when provided")
    if max_total_rows is not None and int(max_total_rows) < 0:
        raise ValueError("max_total_rows must be non-negative when provided")
    per_source_capacity = None if max_rows_per_source is None else int(max_rows_per_source)
    total_capacity = None if max_total_rows is None else int(max_total_rows)

    sources = normalize_weighted_point_rows(source_points)
    nodes = _tree_node_rows(tree_nodes)
    node_by_id = {node.id: node for node in nodes}
    node_member_sets = {node.id: set(node.member_ids) for node in nodes}
    root_ids = _tree_roots(nodes)
    subtree_end_by_id = _tree_subtree_end_by_id(nodes)
    source_leaf_dfs_by_id = _source_leaf_dfs_by_id(nodes)

    frontier_rows: list[dict[str, object]] = []
    debug_diagnostics: list[dict[str, object]] = []
    row_offsets = [0]
    per_source: dict[int, dict[str, int]] = {}
    total_visited = 0
    total_aggregate = 0
    total_exact = 0

    def check_capacity(*, source_id: int, source_count: int, total_count: int) -> None:
        if per_source_capacity is not None and source_count > per_source_capacity:
            raise AggregateFrontierOverflowError(
                "AGGREGATE_FRONTIER_COLLECT_2D overflowed per-source capacity "
                f"{per_source_capacity} for source {source_id}; attempted {source_count}; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )
        if total_capacity is not None and total_count > total_capacity:
            raise AggregateFrontierOverflowError(
                "AGGREGATE_FRONTIER_COLLECT_2D overflowed total capacity "
                f"{total_capacity}; attempted {total_count}; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )

    for source in sources:
        source_rows: list[dict[str, object]] = []
        source_debug_diagnostics: list[dict[str, object]] = []
        visited_count = 0
        aggregate_count = 0
        exact_count = 0
        fallback_seen: set[int] = set()

        def append_row(row: dict[str, object], diagnostic: dict[str, object]) -> None:
            source_rows.append(row)
            if include_debug_diagnostics:
                source_debug_diagnostics.append(diagnostic)
            check_capacity(
                source_id=source.id,
                source_count=len(source_rows),
                total_count=len(frontier_rows) + len(source_rows),
            )

        def visit(node: AggregateTreeNodeRow) -> None:
            nonlocal visited_count, aggregate_count, exact_count
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
                append_row(
                    {
                        "source_id": source.id,
                        "frontier_kind": AGGREGATE_FRONTIER_KIND_AGGREGATE,
                        "frontier_kind_code": AGGREGATE_FRONTIER_KIND_CODES[
                            AGGREGATE_FRONTIER_KIND_AGGREGATE
                        ],
                        "item_id": node.id,
                        "aggregate_id": node.id,
                        "target_id": None,
                        "owner_aggregate_id": node.id,
                        "dfs_index": node.dfs_index,
                        "resume_index": node.resume_index,
                        "metadata_flags": AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
                    },
                    {
                        "source_id": source.id,
                        "frontier_kind_code": AGGREGATE_FRONTIER_KIND_CODES[
                            AGGREGATE_FRONTIER_KIND_AGGREGATE
                        ],
                        "item_id": node.id,
                        "owner_aggregate_id": node.id,
                        "distance": distance,
                        "opening_ratio": opening_ratio,
                    }
                )
                aggregate_count += 1
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
                append_row(
                    {
                        "source_id": source.id,
                        "frontier_kind": AGGREGATE_FRONTIER_KIND_EXACT,
                        "frontier_kind_code": AGGREGATE_FRONTIER_KIND_CODES[
                            AGGREGATE_FRONTIER_KIND_EXACT
                        ],
                        "item_id": target_id,
                        "aggregate_id": node.id,
                        "target_id": target_id,
                        "owner_aggregate_id": node.id,
                        "dfs_index": node.dfs_index,
                        "resume_index": node.resume_index,
                        "metadata_flags": AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
                    },
                    {
                        "source_id": source.id,
                        "frontier_kind_code": AGGREGATE_FRONTIER_KIND_CODES[
                            AGGREGATE_FRONTIER_KIND_EXACT
                        ],
                        "item_id": target_id,
                        "owner_aggregate_id": node.id,
                        "distance": distance,
                        "opening_ratio": opening_ratio,
                    }
                )
                exact_count += 1

        for root_id in root_ids:
            visit(node_by_id[root_id])

        frontier_rows.extend(source_rows)
        if include_debug_diagnostics:
            debug_diagnostics.extend(source_debug_diagnostics)
        row_offsets.append(len(frontier_rows))
        per_source[source.id] = {
            "frontier_offset": row_offsets[-2],
            "frontier_count": len(source_rows),
            "visited_node_count": visited_count,
            "accepted_aggregate_count": aggregate_count,
            "fallback_exact_count": exact_count,
        }
        total_visited += visited_count
        total_aggregate += aggregate_count
        total_exact += exact_count

    i64_rows = tuple(
        (
            int(row["source_id"]),
            int(row["frontier_kind_code"]),
            int(row["item_id"]),
            int(row["owner_aggregate_id"]),
            int(row["dfs_index"]),
            -1 if row["resume_index"] is None else int(row["resume_index"]),
            int(row["metadata_flags"]),
        )
        for row in frontier_rows
    )
    result = {
        "frontier_rows": tuple(frontier_rows),
        "frontier_i64_rows": i64_rows,
        "source_ids": tuple(source.id for source in sources),
        "row_offsets": tuple(row_offsets),
        "row_schema": AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
        "per_source_summary": per_source,
        "summary": {
            "source_count": len(sources),
            "tree_node_count": len(nodes),
            "root_count": len(root_ids),
            "leaf_node_count": sum(1 for node in nodes if node.is_leaf),
            "frontier_row_count": len(frontier_rows),
            "accepted_aggregate_row_count": total_aggregate,
            "fallback_exact_row_count": total_exact,
            "visited_node_total": total_visited,
            "sources_with_any_output": sum(1 for row in per_source.values() if row["frontier_count"]),
            "max_rows_per_source": per_source_capacity,
            "max_total_rows": total_capacity,
            "overflowed": False,
            "partial_result_returned": False,
            "app_math_embedded": False,
        },
        "metadata": {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "theta": theta,
            "row_schema": AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
            "kind_codes": dict(AGGREGATE_FRONTIER_KIND_CODES),
            "metadata_flags_semantics": {
                AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE: (
                    "no flags set; partners must ignore unknown future non-zero flags "
                    "unless a later contract revision documents them"
                ),
            },
            "output_layout": "source_offsets_plus_row_major_i64_frontier_ids",
            "overflow_policy": AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY,
            "failure_mode": "fail_closed_overflow",
            "deduplicate_fallback_targets": deduplicate_fallback_targets,
            "uses_dfs_subtree_membership": True,
            "frontier_ids_only": True,
            "frontier_row_extra_fields_reference_only": (
                "frontier_kind",
                "aggregate_id",
                "target_id",
            ),
            "debug_diagnostics_included": include_debug_diagnostics,
            "app_math_embedded": False,
            "force_law_embedded": False,
            "native_engine_app_specific": False,
            "native_lowering_status": "cpu_reference_contract_native_backend_separate_lowering",
            "partner_lowering_status": "row_major_i64_frontier_ids_partner_ready",
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
        },
    }
    if include_debug_diagnostics:
        result["debug_diagnostics"] = tuple(debug_diagnostics)
    return result


def aggregate_frontier_collect_to_columnar_record_set(
    collection: Mapping[str, object],
) -> dict[str, object]:
    """Adapt a frontier collection result into generic columnar row payloads."""

    if not isinstance(collection, Mapping):
        raise ValueError("aggregate frontier collection must be a mapping")
    metadata = collection.get("metadata")
    if not isinstance(metadata, Mapping) or metadata.get("contract") != AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT:
        raise ValueError("aggregate frontier collection uses an unsupported contract")
    row_schema = tuple(str(item) for item in collection.get("row_schema", ()))
    if row_schema != AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA:
        raise ValueError("aggregate frontier collection row schema mismatch")
    rows = tuple(tuple(int(value) for value in row) for row in collection.get("frontier_i64_rows", ()))
    for row in rows:
        if len(row) != len(row_schema):
            raise ValueError("aggregate frontier i64 row width mismatch")
    columns = {
        name: tuple(row[index] for row in rows)
        for index, name in enumerate(row_schema)
    }
    return {
        "row_ids": tuple(range(len(rows))),
        "columns": columns,
        "source_ids": tuple(int(value) for value in collection.get("source_ids", ())),
        "row_offsets": tuple(int(value) for value in collection.get("row_offsets", ())),
        "metadata": {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "record_count": len(rows),
            "row_schema": row_schema,
            "source_offset_layout": "source_ids_plus_row_offsets",
            "partner_i64_row_layout_ready": True,
            "metadata_flags_semantics": {
                AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE: (
                    "no flags set; partners must ignore unknown future non-zero flags "
                    "unless a later contract revision documents them"
                ),
            },
            "native_engine_app_specific": False,
            "app_math_embedded": False,
            "force_law_embedded": False,
            "claim_boundary": (
                "Columnar adapter for generic aggregate-frontier IDs only. "
                "App math, force laws, device-resident execution, native backend "
                "execution, speedup claims, and paper reproduction claims are not "
                "authorized."
            ),
        },
    }


def aggregate_frontier_collect_native_abi_contract() -> dict[str, object]:
    """Return the app-independent native ABI target for future backend work."""

    prototype = (
        "int {symbol}(const RtdlAggregateFrontierSource2D* sources, size_t source_count, "
        "const RtdlAggregateFrontierNode2D* nodes, size_t node_count, "
        "const uint64_t* child_offsets, const int64_t* child_ids, "
        "const uint64_t* member_offsets, const int64_t* member_ids, "
        "double theta, uint64_t max_rows_per_source, uint64_t row_capacity, "
        "uint32_t deduplicate_fallback_targets, int64_t* frontier_rows_out, "
        "uint64_t* row_offsets_out, uint64_t* emitted_count_out, "
        "uint64_t* attempted_count_out, uint32_t* overflowed_out, "
        "char* error_out, size_t error_size)"
    )
    return {
        "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
        "contract": AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT,
        "python_reference_contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
        "status": "specified_native_implementation_pending",
        "executable": False,
        "app_generic": True,
        "required_native_symbols": AGGREGATE_FRONTIER_COLLECT_NATIVE_REQUIRED_SYMBOLS,
        "symbol_prototype_template": prototype,
        "source_point_struct": (
            "id:int64",
            "x:float64",
            "y:float64",
        ),
        "tree_node_struct": (
            "id:int64",
            "cx:float64",
            "cy:float64",
            "half_size:float64",
            "depth:int32",
            "dfs_index:int64",
            "resume_index:int64_sentinel_minus_one",
            "is_leaf:uint8",
        ),
        "tree_csr_inputs": (
            "child_offsets:uint64[node_count+1]",
            "child_ids:int64[child_count]",
            "member_offsets:uint64[node_count+1]",
            "member_ids:int64[member_count]",
        ),
        "parameters": (
            "theta:float64_positive",
            "max_rows_per_source:uint64_or_UINT64_MAX_for_unbounded",
            "row_capacity:uint64_total_frontier_row_capacity",
            "deduplicate_fallback_targets:uint32_bool",
        ),
        "output_row_schema": AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA,
        "output_row_width": len(AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA),
        "outputs": (
            "frontier_rows_out:int64[row_capacity][output_row_width]",
            "row_offsets_out:uint64[source_count+1]",
            "emitted_count_out:uint64",
            "attempted_count_out:uint64",
            "overflowed_out:uint32_bool",
        ),
        "row_schema_semantics": {
            "source_id": "input source id",
            "frontier_kind_code": "1=aggregate, 2=exact",
            "item_id": "aggregate id for aggregate rows, target id for exact rows",
            "owner_aggregate_id": "aggregate tree node owning this emitted row",
            "dfs_index": "DFS index of the owner aggregate node",
            "resume_index": "DFS resume index or -1 sentinel",
            "metadata_flags": "0 means no flags set; unknown non-zero values are reserved",
        },
        "overflow_policy": AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY,
        "overflow_semantics": (
            "If overflowed_out is 1, emitted_count_out must be 0 and the caller must "
            "treat frontier_rows_out and row_offsets_out as invalid partial workspace. "
            "attempted_count_out is diagnostic only. No partial result may be surfaced."
        ),
        "engine_exclusions": (
            "force_law",
            "scoring",
            "app_reduction",
            "time_integration",
            "benchmark_specific_logic",
            "paper_specific_shortcuts",
        ),
        "claim_boundary": (
            "Native ABI contract only. It specifies generic aggregate-frontier row "
            "collection for future Embree/OptiX implementations; it does not provide "
            "native execution, RT-core timing, speedup wording, or app math."
        ),
    }


def validate_aggregate_frontier_collect_native_abi_contract() -> dict[str, object]:
    """Validate and return the future native ABI contract."""

    contract = aggregate_frontier_collect_native_abi_contract()
    required = (
        "primitive",
        "contract",
        "python_reference_contract",
        "status",
        "executable",
        "app_generic",
        "required_native_symbols",
        "symbol_prototype_template",
        "source_point_struct",
        "tree_node_struct",
        "tree_csr_inputs",
        "parameters",
        "output_row_schema",
        "output_row_width",
        "outputs",
        "row_schema_semantics",
        "overflow_policy",
        "overflow_semantics",
        "engine_exclusions",
        "claim_boundary",
    )
    for field in required:
        if field not in contract:
            raise ValueError(f"missing aggregate-frontier native ABI field: {field}")
    if contract["primitive"] != AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE:
        raise ValueError("aggregate-frontier native ABI primitive mismatch")
    if contract["contract"] != AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT:
        raise ValueError("aggregate-frontier native ABI contract mismatch")
    if contract["python_reference_contract"] != AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT:
        raise ValueError("aggregate-frontier native ABI must point to the CPU reference contract")
    if contract["executable"] is not False:
        raise ValueError("aggregate-frontier native ABI is not executable until backend symbols exist")
    if contract["app_generic"] is not True:
        raise ValueError("aggregate-frontier native ABI must remain app-generic")
    if tuple(contract["required_native_symbols"]) != AGGREGATE_FRONTIER_COLLECT_NATIVE_REQUIRED_SYMBOLS:
        raise ValueError("aggregate-frontier native ABI symbol list mismatch")
    if tuple(contract["output_row_schema"]) != AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA:
        raise ValueError("aggregate-frontier native ABI output row schema mismatch")
    if int(contract["output_row_width"]) != len(AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA):
        raise ValueError("aggregate-frontier native ABI output row width mismatch")
    boundary_text = " ".join(str(value) for value in contract.values()).lower()
    for forbidden in ("barnes", "force law", "inverse-square", "collision"):
        if forbidden in boundary_text:
            raise ValueError(f"aggregate-frontier native ABI leaked app vocabulary: {forbidden}")
    for phrase in ("invalid partial workspace", "no partial result", "native abi contract only"):
        if phrase not in boundary_text:
            raise ValueError("aggregate-frontier native ABI claim boundary is incomplete")
    return contract


def plan_aggregate_frontier_collect_lowering(target: str) -> dict[str, object]:
    """Return the current lowering status for aggregate-frontier collection."""

    normalized = str(target).strip().lower()
    if normalized in {"cpu", "cpu_python_reference", "python"}:
        return {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "target": normalized,
            "status": "implemented_cpu_reference",
            "executable": True,
            "native_engine_app_specific": False,
            "outputs": ("frontier_rows", "frontier_i64_rows", "source_ids", "row_offsets"),
            "claim_boundary": "CPU reference only; no native RT performance claim.",
        }
    if normalized in {"partner", "partner_columns", "torch", "cupy"}:
        return {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "target": normalized,
            "status": "implemented_partner_column_adapter",
            "executable": normalized in {"torch", "cupy"},
            "native_engine_app_specific": False,
            "outputs": ("row_major_i64_columns", "source_ids", "row_offsets"),
            "claim_boundary": (
                "Partner-column adapter only. It moves generic frontier IDs into "
                "partner-owned tensors; it does not implement native RT traversal, "
                "force math, speedup claims, or zero-copy claims."
            ),
        }
    if normalized in {"embree", "optix", "native_embree", "native_optix"}:
        backend = "embree" if "embree" in normalized else "optix"
        symbol = next(item for item in AGGREGATE_FRONTIER_COLLECT_NATIVE_REQUIRED_SYMBOLS if backend in item)
        if backend == "embree":
            return {
                "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
                "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
                "target": normalized,
                "status": "implemented_embree_native_symbol_optix_parity_validated_timing_baseline_recorded",
                "executable": True,
                "native_engine_app_specific": False,
                "native_abi_contract": AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT,
                "native_abi_status": "implemented_for_embree",
                "native_output_row_width": len(AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA),
                "required_native_symbol": symbol,
                "required_next_steps": (
                    "design true RT-core aggregate-frontier traversal before any RT-core speedup wording",
                    "request external review before promotion",
                ),
                "claim_boundary": (
                    "Embree native row collection is implemented for the generic ABI, "
                    "and Goal2639 records OptiX parity evidence. Do not claim RT-core "
                    "acceleration, speedup, or paper reproduction from this row-collection "
                    "milestone."
                ),
            }
        return {
            "primitive": AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE,
            "contract": AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
            "target": normalized,
            "status": "implemented_optix_native_symbol_pod_parity_validated_timing_baseline_recorded",
            "executable": True,
            "native_engine_app_specific": False,
            "native_abi_contract": AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT,
            "native_abi_status": "implemented_for_optix",
            "native_output_row_width": len(AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA),
            "required_native_symbol": symbol,
            "required_next_steps": (
                "validate same-contract parity against CPU reference",
                "design true RT-core aggregate-frontier traversal before any RT-core speedup wording",
                "request external review before promotion",
            ),
            "claim_boundary": (
                "OptiX native row collection is implemented for the generic ABI, "
                "and Goal2639 records pod parity plus host-side timing evidence. "
                "This does not authorize RT-core acceleration, speedup, or paper "
                "reproduction wording."
            ),
        }
    raise ValueError("aggregate-frontier lowering target must be cpu, partner, torch, cupy, embree, or optix")


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
