from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from functools import cmp_to_key
import json
import math
from pathlib import Path
import struct
from typing import Iterable


THRESHOLD = 0.5
GRAVITATIONAL_CONSTANT = 0.1
BUCKET_SIZE = 32


@dataclass(frozen=True)
class Body:
    id: int
    mass: float
    x: float
    y: float
    z: float


@dataclass
class Node:
    x: float
    y: float
    z: float
    s: float
    point_id: int
    node_type: str = "leaf"
    mass: float = 0.0
    particles: list[int] = field(default_factory=list)
    children: list["Node | None"] = field(default_factory=lambda: [None] * 8)


def _float32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


def _float_exp(bits: int) -> int:
    unsigned = bits & 0x7FFFFFFF
    if unsigned == 0 or unsigned >= 0x7F800000:
        return 0
    exp = unsigned >> 23
    return -126 if exp == 0 else int(exp) - 127


def _float_sig(bits: int) -> int:
    return bits & 0x007FFFFF


def _uint_log_base2(value: int) -> int:
    if value <= 0:
        raise ValueError("UIntLogBase2 requires a positive value")
    return value.bit_length() - 1


def _float_xor_msb(p: float, q: float) -> int:
    if p == q or p == -q:
        return -(2**31)
    p_bits = _float32_bits(p)
    q_bits = _float32_bits(q)
    p_exp = _float_exp(p_bits)
    q_exp = _float_exp(q_bits)
    if p_exp == q_exp:
        xor_sig = _float_sig(p_bits) ^ _float_sig(q_bits)
        if xor_sig > 0:
            return p_exp + _uint_log_base2(xor_sig) - 23
        return p_exp
    return max(p_exp, q_exp)


def zorder_compare(lhs: Body, rhs: Body) -> int:
    p = (lhs.x, lhs.y, lhs.z)
    q = (rhs.x, rhs.y, rhs.z)
    best = -(2**31)
    axis = 0
    for j in (2, 1, 0):
        if (p[j] < 0.0) != (q[j] < 0.0):
            return -1 if p[j] < q[j] else 1
        candidate = _float_xor_msb(p[j], q[j])
        if best < candidate:
            best = candidate
            axis = j
    if p[axis] < q[axis]:
        return -1
    if p[axis] > q[axis]:
        return 1
    return 0


def read_treelogy_input(path: Path, *, limit: int | None = None) -> list[Body]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 5:
        raise ValueError("Treelogy input must contain five header rows")
    expected = int(float(lines[0].strip()))
    if limit is not None:
        expected = min(expected, limit)
    bodies: list[Body] = []
    for row_index, line in enumerate(lines[5:], start=0):
        if len(bodies) >= expected:
            break
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"invalid body row {row_index}: {line!r}")
        mass, x, y, z = (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
        bodies.append(Body(id=len(bodies), mass=mass, x=x, y=y, z=z))
    if len(bodies) != expected:
        raise ValueError(f"expected {expected} bodies, read {len(bodies)}")
    return bodies


def write_treelogy_input(path: Path, bodies: Iterable[Body]) -> None:
    rows = list(bodies)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"{len(rows)}\n")
        handle.write("1\n")
        handle.write("0.025000\n")
        handle.write("0.050000\n")
        handle.write(f"{THRESHOLD:.6f}\n")
        for body in rows:
            handle.write(f"{body.mass:.9g} {body.x:.9g} {body.y:.9g} {body.z:.9g} 0 0 0\n")


def make_synthetic_bodies(count: int) -> list[Body]:
    if count < 1:
        raise ValueError("count must be positive")
    side = math.ceil(count ** (1.0 / 3.0))
    bodies: list[Body] = []
    for index in range(count):
        gx = index % side
        gy = (index // side) % side
        gz = index // (side * side)
        denom = max(1, side - 1)
        x = (gx / denom) * 8.0 - 4.0 + (((index * 17) % 11) - 5) * 0.001
        y = (gy / denom) * 8.0 - 4.0 + (((index * 31) % 13) - 6) * 0.001
        z = (gz / denom) * 8.0 - 4.0 + (((index * 43) % 17) - 8) * 0.001
        mass = 10.0 + (index % 1991)
        bodies.append(Body(id=index, mass=mass, x=x, y=y, z=z))
    return bodies


def _distance(body: Body, node: Node) -> float:
    dx = body.x - node.x
    dy = body.y - node.y
    dz = body.z - node.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def _insert_node(parent: Node, point: Node, s: float) -> None:
    octant = 0
    offset_x = offset_y = offset_z = 0.0
    if parent.z < point.z:
        octant = 4
        offset_z = s
    if parent.y < point.y:
        octant += 2
        offset_y = s
    if parent.x < point.x:
        octant += 1
        offset_x = s
    child = parent.children[octant]
    if child is None:
        point.s = s
        parent.children[octant] = point
        return
    half_r = 0.5 * s
    if child.node_type == "leaf":
        inner = Node(
            x=(parent.x - half_r) + offset_x,
            y=(parent.y - half_r) + offset_y,
            z=(parent.z - half_r) + offset_z,
            s=half_r,
            point_id=-1,
            node_type="nonleaf",
        )
        _insert_node(inner, point, half_r)
        _insert_node(inner, child, half_r)
        parent.children[octant] = inner
    else:
        _insert_node(child, point, half_r)


def _compute_com(node: Node) -> None:
    if node.node_type != "nonleaf":
        return
    total_mass = 0.0
    cofm_x = cofm_y = cofm_z = 0.0
    for child in node.children:
        if child is None:
            continue
        _compute_com(child)
        total_mass += child.mass
        cofm_x += child.x * child.mass
        cofm_y += child.y * child.mass
        cofm_z += child.z * child.mass
    if total_mass != 0.0:
        node.mass = total_mass
        node.x = cofm_x / total_mass
        node.y = cofm_y / total_mass
        node.z = cofm_z / total_mass


def build_author_bucket_tree(input_bodies: list[Body]) -> tuple[list[Body], Node, dict[str, object]]:
    if not input_bodies:
        raise ValueError("body list must not be empty")
    max_abs = max(max(abs(body.x), abs(body.y), abs(body.z)) for body in input_bodies)
    grid_size = math.ceil(max_abs) * 2.0
    sorted_bodies = sorted(input_bodies, key=cmp_to_key(zorder_compare))
    bodies = [
        Body(id=index, mass=body.mass, x=body.x, y=body.y, z=body.z)
        for index, body in enumerate(sorted_bodies)
    ]
    leaves = [
        Node(x=body.x, y=body.y, z=body.z, s=grid_size * 0.5, point_id=body.id, mass=body.mass)
        for body in bodies
    ]
    root = Node(x=0.0, y=0.0, z=0.0, s=grid_size, point_id=-1, node_type="nonleaf")
    leaf_count = math.ceil(len(leaves) / float(BUCKET_SIZE))
    for leaf_index in range(leaf_count):
        members = leaves[leaf_index * BUCKET_SIZE : (leaf_index + 1) * BUCKET_SIZE]
        mass = sum(member.mass for member in members)
        if mass == 0.0:
            raise ValueError("zero-mass bucket is unsupported")
        bucket = Node(
            x=sum(member.x * member.mass for member in members) / mass,
            y=sum(member.y * member.mass for member in members) / mass,
            z=sum(member.z * member.mass for member in members) / mass,
            s=grid_size * 0.5,
            point_id=-1,
            node_type="leaf",
            mass=mass,
            particles=[member.point_id for member in members],
        )
        _insert_node(root, bucket, grid_size * 0.5)
    _compute_com(root)
    summary = {
        "input_body_count": len(input_bodies),
        "sorted_body_count": len(bodies),
        "bucket_leaf_count": leaf_count,
        "grid_size": grid_size,
    }
    return bodies, root, summary


def author_sorted_bodies(input_bodies: list[Body]) -> list[Body]:
    sorted_bodies = sorted(input_bodies, key=cmp_to_key(zorder_compare))
    return [
        Body(id=index, mass=body.mass, x=body.x, y=body.y, z=body.z)
        for index, body in enumerate(sorted_bodies)
    ]


def _compute_node_attraction(source: Body, node: Node, bodies: list[Body]) -> float:
    if node.node_type == "leaf":
        result = 0.0
        for target_id in node.particles:
            if target_id == source.id:
                continue
            target = bodies[target_id]
            dx = source.x - target.x
            dy = source.y - target.y
            dz = source.z - target.z
            dist_sq = dx * dx + dy * dy + dz * dz
            if dist_sq != 0.0:
                result += ((source.mass * target.mass) / dist_sq) * GRAVITATIONAL_CONSTANT
        return result
    dx = source.x - node.x
    dy = source.y - node.y
    dz = source.z - node.z
    dist_sq = dx * dx + dy * dy + dz * dz
    return 0.0 if dist_sq == 0.0 else ((source.mass * node.mass) / dist_sq) * GRAVITATIONAL_CONSTANT


def _force_on(source: Body, node: Node) -> float:
    if node.node_type == "leaf":
        if node.mass != 0.0 and not (source.x == node.x and source.y == node.y and source.z == node.z):
            raise AssertionError("leaf force requires bodies context")
        return 0.0
    raise AssertionError("internal helper should not be called directly")


def force_on_author_tree(source: Body, node: Node, bodies: list[Body]) -> float:
    if node.node_type == "leaf":
        if node.mass != 0.0 and not (source.x == node.x and source.y == node.y and source.z == node.z):
            return _compute_node_attraction(source, node, bodies)
        return 0.0
    if node.s < _distance(source, node) * THRESHOLD:
        return _compute_node_attraction(source, node, bodies)
    total = 0.0
    for child in node.children:
        if child is not None:
            total += force_on_author_tree(source, child, bodies)
    return total


def compute_author_contract_forces(input_bodies: list[Body]) -> dict[str, object]:
    bodies, root, tree_summary = build_author_bucket_tree(input_bodies)
    rows = [{"source_id": body.id, "scalar_force": force_on_author_tree(body, root, bodies)} for body in bodies]
    return {
        "contract": "author_cpu_bucket_tree_scalar_force_reference_v1",
        "force_rows": rows,
        "summary": {
            **tree_summary,
            "checksum_scalar_force": sum(float(row["scalar_force"]) for row in rows),
        },
    }


def author_tree_prepared_arrays_payload(input_bodies: list[Body]) -> dict[str, object]:
    bodies, root, tree_summary = build_author_bucket_tree(input_bodies)
    mutable_nodes: list[dict[str, object]] = []

    def visit(node: Node, *, depth: int) -> int:
        node_id = len(mutable_nodes) + 1
        dfs_index = len(mutable_nodes)
        mutable_nodes.append(
            {
                "id": node_id,
                "cx": node.x,
                "cy": node.y,
                "cz": node.z,
                "half_size": node.s,
                "mass": node.mass,
                "member_ids": [int(item) for item in node.particles],
                "child_ids": [],
                "depth": depth,
                "dfs_index": dfs_index,
                "resume_index": None,
                "cell_cx": 0.0,
                "cell_cy": 0.0,
                "cell_cz": 0.0,
                "is_leaf": node.node_type == "leaf",
            }
        )
        child_ids: list[int] = []
        for child in node.children:
            if child is not None:
                child_ids.append(visit(child, depth=depth + 1))
        mutable_nodes[dfs_index]["child_ids"] = child_ids
        return node_id

    visit(root, depth=0)
    id_to_index = {int(node["id"]): index for index, node in enumerate(mutable_nodes)}

    def subtree_end_index(index: int) -> int:
        child_ids = [int(child_id) for child_id in mutable_nodes[index]["child_ids"]]
        if not child_ids:
            return index + 1
        return max(subtree_end_index(id_to_index[child_id]) for child_id in child_ids)

    for index, node in enumerate(mutable_nodes):
        end_index = subtree_end_index(index)
        node["resume_index"] = end_index if end_index < len(mutable_nodes) else None
    return {
        "schema": "generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1",
        "contract_source": "rt_barneshut_author_bucket_tree_v1",
        "tree_summary": tree_summary,
        "points": [
            {
                "id": body.id,
                "mass": body.mass,
                "x": body.x,
                "y": body.y,
                "z": body.z,
            }
            for body in bodies
        ],
        "nodes": mutable_nodes,
    }


def write_prepared_arrays(path: Path, input_bodies: list[Body]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(author_tree_prepared_arrays_payload(input_bodies), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_force_rows(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(f"{int(row['source_id'])} {float(row['scalar_force']):.9g}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Author-contract CPU reference for RT-BarnesHut scalar forces.")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--synthetic-count", type=int, default=None)
    parser.add_argument("--write-synthetic-input", type=Path, default=None)
    parser.add_argument("--write-author-sorted-input", type=Path, default=None)
    parser.add_argument("--write-rtdl-prepared-arrays", type=Path, default=None)
    parser.add_argument("--force-output", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args()

    if args.input is None and args.synthetic_count is None:
        raise SystemExit("provide --input or --synthetic-count")
    bodies = read_treelogy_input(args.input) if args.input is not None else make_synthetic_bodies(int(args.synthetic_count))
    if args.write_synthetic_input is not None:
        write_treelogy_input(args.write_synthetic_input, bodies)
    if args.write_author_sorted_input is not None:
        write_treelogy_input(args.write_author_sorted_input, author_sorted_bodies(bodies))
    if args.write_rtdl_prepared_arrays is not None:
        write_prepared_arrays(args.write_rtdl_prepared_arrays, bodies)
    payload = compute_author_contract_forces(bodies)
    if args.force_output is not None:
        write_force_rows(args.force_output, payload["force_rows"])
    summary_payload = {
        key: value for key, value in payload.items() if key != "force_rows"
    }
    summary_payload["force_output"] = None if args.force_output is None else str(args.force_output)
    summary_payload["author_sorted_input"] = None if args.write_author_sorted_input is None else str(args.write_author_sorted_input)
    summary_payload["rtdl_prepared_arrays"] = None if args.write_rtdl_prepared_arrays is None else str(args.write_rtdl_prepared_arrays)
    summary_payload["force_rows_materialized_in_summary"] = False
    text = json.dumps(summary_payload, indent=2, sort_keys=True) + "\n"
    if args.summary is not None:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
