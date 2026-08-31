"""Route-independent fixtures for Goal5764/M6.

Application names occur only in this evidence layer.  Product code receives an
app-neutral aggregate hierarchy and one closed reducer enum.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-barneshut-paper"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _threaded_hierarchy_from_payload(payload: dict[str, Any]):
    points = payload["points"]
    nodes = payload["nodes"]
    id_to_index = {int(node["id"]): index for index, node in enumerate(nodes)}
    member_offsets = [0]
    member_indices: list[int] = []
    child_offsets = [0]
    child_indices: list[int] = []
    source_leaf = [-1] * len(points)
    subtree_end: list[int] = []
    for node_index, node in enumerate(nodes):
        members = [int(value) for value in node["member_ids"]]
        member_indices.extend(members)
        member_offsets.append(len(member_indices))
        for point_index in members:
            source_leaf[point_index] = node_index
        child_indices.extend(id_to_index[int(value)] for value in node["child_ids"])
        child_offsets.append(len(child_indices))
        resume = node["resume_index"]
        subtree_end.append(len(nodes) if resume is None else int(resume))
    if any(index < 0 for index in source_leaf):
        raise RuntimeError("author fixture failed to bind every point to a leaf")
    node_next = [
        index + 1 if index + 1 < len(nodes) else -1
        for index in range(len(nodes))
    ]
    node_rope = [
        -1 if node["resume_index"] is None else int(node["resume_index"])
        for node in nodes
    ]
    return rt.aggregate_hierarchy_3d(
        point_x=[row["x"] for row in points],
        point_y=[row["y"] for row in points],
        point_z=[row["z"] for row in points],
        point_weight=[row["mass"] for row in points],
        node_cx=[row["cx"] for row in nodes],
        node_cy=[row["cy"] for row in nodes],
        node_cz=[row["cz"] for row in nodes],
        node_half_size=[row["half_size"] for row in nodes],
        node_weight=[row["mass"] for row in nodes],
        member_offsets=member_offsets,
        member_indices=member_indices,
        child_offsets=child_offsets,
        child_indices=child_indices,
        node_next_index=node_next,
        node_rope_index=node_rope,
        source_leaf_node_index=source_leaf,
        node_subtree_end_index=subtree_end,
    )


def rt_barneshut_author_fixture(body_count: int = 256):
    """Return the paper reference, a threaded spec, and exact scalar rows."""

    author = _load(
        "goal5764_rt_barneshut_author_reference",
        APP_DIR / "author_contract_reference.py",
    )
    bodies = author.make_synthetic_bodies(body_count)
    payload = author.author_tree_prepared_arrays_payload(bodies)
    expected = tuple(author.compute_author_contract_forces(bodies)["force_rows"])
    hierarchy = _threaded_hierarchy_from_payload(payload)
    spec = rt.aggregate_frontier_reduce_spec_3d(
        rt.prepare_aggregate_hierarchy_3d(hierarchy),
        opening=rt.ContinuationPayloadOpening(max_ratio=author.THRESHOLD),
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    )
    return spec, expected, {
        "author_contract": "author_cpu_bucket_tree_scalar_force_reference_v1",
        "body_count": body_count,
        "node_count": hierarchy.node_count,
        "force_scale": author.GRAVITATIONAL_CONSTANT,
    }


def hierarchy_coverage_fixture():
    """A real non-paper spatial-coverage consumer of aggregate-count.

    Three sensors occupy two near cells and one distant cell.  The hierarchy is
    intentionally threaded through a rope-distinguishing branch.  The output
    counts accepted aggregate cells or exact leaf peers per source.
    """

    hierarchy = rt.aggregate_hierarchy_3d(
        point_x=[0.0, 0.1, 10.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 0.0, 0.0],
        point_weight=[1.0, 1.0, 1.0],
        node_cx=[0.0, 10.0, 0.0, 10.0],
        node_cy=[0.0, 0.0, 0.0, 0.0],
        node_cz=[0.0, 0.0, 0.0, 0.0],
        node_half_size=[100.0, 1.0, 0.1, 0.1],
        node_weight=[3.0, 2.0, 2.0, 1.0],
        member_offsets=[0, 0, 0, 2, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 3, 3, 3],
        child_indices=[1, 3, 2],
        node_next_index=[1, 2, 3, -1],
        node_rope_index=[-1, 3, 3, -1],
        source_leaf_node_index=[2, 2, 3],
        node_subtree_end_index=[4, 3, 3, 4],
    )
    spec = rt.aggregate_frontier_reduce_spec_3d(
        rt.prepare_aggregate_hierarchy_3d(hierarchy),
        opening=rt.ContinuationPayloadOpening(max_ratio=1.0),
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    )
    return spec, {
        "consumer_contract": "hierarchical_spatial_coverage_count_v1",
        "dataset": "three_station_two_cluster_coverage_v1",
        "expected_reducer_values": (2.0, 2.0, 2.0),
    }


__all__ = (
    "hierarchy_coverage_fixture",
    "rt_barneshut_author_fixture",
)
