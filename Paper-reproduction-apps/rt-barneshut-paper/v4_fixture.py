"""Application-owned author fixture adapter for the V4 RT-BarnesHut lane."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any

import rtdsl as rt


APP_DIR = Path(__file__).resolve().parent


def _load_author():
    name = "rtdl_v4_rt_barneshut_author_reference"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = APP_DIR / "author_contract_reference.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _threaded_hierarchy(payload: dict[str, Any]):
    points = payload["points"]
    nodes = payload["nodes"]
    id_to_index = {int(node["id"]): index for index, node in enumerate(nodes)}
    member_offsets = [0]
    member_indices = []
    child_offsets = [0]
    child_indices = []
    source_leaf = [-1] * len(points)
    subtree_end = []
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
        raise RuntimeError("author fixture did not bind every body to a leaf")
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
        node_next_index=[
            index + 1 if index + 1 < len(nodes) else -1
            for index in range(len(nodes))
        ],
        node_rope_index=[
            -1 if node["resume_index"] is None else int(node["resume_index"])
            for node in nodes
        ],
        source_leaf_node_index=source_leaf,
        node_subtree_end_index=subtree_end,
    )


def rt_barneshut_author_fixture(body_count: int = 256):
    author = _load_author()
    bodies = author.make_synthetic_bodies(body_count)
    payload = author.author_tree_prepared_arrays_payload(bodies)
    expected = tuple(author.compute_author_contract_forces(bodies)["force_rows"])
    hierarchy = _threaded_hierarchy(payload)
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


__all__ = ["rt_barneshut_author_fixture"]
