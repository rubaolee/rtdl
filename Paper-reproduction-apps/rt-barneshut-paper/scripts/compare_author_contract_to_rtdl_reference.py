from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(APP_DIR))

import author_contract_reference as author_ref


RTDL_CONTRACT_CURRENT = "current-rtdl-diagnostic-tree"
RTDL_CONTRACT_AUTHOR_PREPARED = "author-prepared-arrays"


def _load_rtdl_diag_module():
    path = ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"
    spec = importlib.util.spec_from_file_location("rtdl_goal2547_bh_diag", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _author_tree_to_rtdl_prepared_arrays(
    rtdl_diag,
    bodies: list[author_ref.Body],
    root: author_ref.Node,
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    """Flatten the author bucket tree into the generic RTDL diagnostic node shape.

    This is deliberately kept in the paper app: the author z-order bucket tree
    is part of the RT-BarnesHut workload contract, while the flattened
    aggregate-node/member/child representation is the generic continuation
    shape consumed by the existing diagnostic reference.
    """

    points = tuple(
        rtdl_diag.Point3D(
            id=body.id,
            x=body.x,
            y=body.y,
            z=body.z,
            mass=body.mass,
        )
        for body in bodies
    )
    mutable_nodes: list[dict[str, object]] = []

    def visit(node: author_ref.Node, *, depth: int) -> int:
        node_id = len(mutable_nodes) + 1
        dfs_index = len(mutable_nodes)
        mutable_nodes.append(
            {
                "id": node_id,
                "cx": node.x,
                "cy": node.y,
                "cz": node.z,
                "s": node.s,
                "mass": node.mass,
                "member_ids": tuple(int(item) for item in node.particles),
                "child_ids": (),
                "depth": depth,
                "dfs_index": dfs_index,
                "resume_index": None,
                "is_leaf": node.node_type == "leaf",
            }
        )
        child_ids: list[int] = []
        for child in node.children:
            if child is not None:
                child_ids.append(visit(child, depth=depth + 1))
        mutable_nodes[dfs_index]["child_ids"] = tuple(child_ids)
        return node_id

    visit(root, depth=0)
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
        rtdl_diag.TreeNode3D(
            id=int(node["id"]),
            cx=float(node["cx"]),
            cy=float(node["cy"]),
            cz=float(node["cz"]),
            half_size=float(node["s"]),
            mass=float(node["mass"]),
            member_ids=tuple(int(item) for item in node["member_ids"]),
            child_ids=tuple(int(item) for item in node["child_ids"]),
            depth=int(node["depth"]),
            dfs_index=int(node["dfs_index"]),
            resume_index=None if node["resume_index"] is None else int(node["resume_index"]),
            cell_cx=0.0,
            cell_cy=0.0,
            cell_cz=0.0,
            is_leaf=bool(node["is_leaf"]),
        )
        for node in mutable_nodes
    )
    return points, nodes


def _reference_author_traversal_over_prepared_arrays(
    points: tuple[object, ...],
    nodes: tuple[object, ...],
    *,
    theta: float,
    softening: float,
) -> dict[str, object]:
    point_by_id = {int(point.id): point for point in points}
    node_by_id = {int(node.id): node for node in nodes}
    child_ids = {int(child_id) for node in nodes for child_id in node.child_ids}
    root_ids = tuple(int(node.id) for node in nodes if int(node.id) not in child_ids)
    total_visited = 0
    total_accepted = 0
    total_exact = 0
    rows: list[dict[str, object]] = []

    for source in points:
        scalar_sum = 0.0
        visited = 0
        accepted = 0
        exact = 0

        def visit(node) -> None:
            nonlocal scalar_sum, visited, accepted, exact
            visited += 1
            dx = float(source.x) - float(node.cx)
            dy = float(source.y) - float(node.cy)
            dz = float(source.z) - float(node.cz)
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if not node.is_leaf and float(node.half_size) < distance * theta:
                dist_sq = dx * dx + dy * dy + dz * dz + softening * softening
                if dist_sq != 0.0:
                    scalar_sum += float(source.mass) * float(node.mass) / dist_sq
                accepted += 1
                return
            if node.child_ids:
                for child_id in node.child_ids:
                    visit(node_by_id[int(child_id)])
                return
            for target_id in node.member_ids:
                if int(target_id) == int(source.id):
                    continue
                target = point_by_id[int(target_id)]
                ex = float(source.x) - float(target.x)
                ey = float(source.y) - float(target.y)
                ez = float(source.z) - float(target.z)
                dist_sq = ex * ex + ey * ey + ez * ez + softening * softening
                if dist_sq != 0.0:
                    scalar_sum += float(source.mass) * float(target.mass) / dist_sq
                exact += 1

        for root_id in root_ids:
            visit(node_by_id[root_id])
        total_visited += visited
        total_accepted += accepted
        total_exact += exact
        rows.append(
            {
                "source_id": int(source.id),
                "scalar_force": scalar_sum,
                "visited_node_count": visited,
                "aggregate_contribution_count": accepted,
                "exact_contribution_count": exact,
            }
        )
    return {
        "scalar_sum_rows": tuple(rows),
        "summary": {
            "source_count": len(points),
            "tree_node_count": len(nodes),
            "root_count": len(root_ids),
            "leaf_node_count": sum(1 for node in nodes if node.is_leaf),
            "visited_node_total": total_visited,
            "aggregate_contribution_row_count": total_accepted,
            "exact_contribution_row_count": total_exact,
            "contribution_row_count": total_accepted + total_exact,
        },
    }


def compare_contracts(
    bodies: list[author_ref.Body],
    *,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    rtdl_force_scale: float,
    rtdl_contract: str,
) -> dict[str, object]:
    rtdl_diag = _load_rtdl_diag_module()
    sorted_bodies = author_ref.author_sorted_bodies(bodies)
    author_payload = author_ref.compute_author_contract_forces(bodies)
    if rtdl_contract == RTDL_CONTRACT_CURRENT:
        rtdl_points = tuple(
            rtdl_diag.Point3D(
                id=index + 1,
                x=body.x,
                y=body.y,
                z=body.z,
                mass=body.mass,
            )
            for index, body in enumerate(sorted_bodies)
        )
        rtdl_tree = rtdl_diag.build_bucketized_aggregate_tree_3d(
            rtdl_points,
            bucket_size=bucket_size,
            max_depth=max_depth,
        )
        rtdl_reference = rtdl_diag.reference_scalar_sum_3d(
            rtdl_points,
            tuple(rtdl_tree["nodes"]),
            theta=theta,
            softening=softening,
        )
        rtdl_contract_label = "goal2547_python_reference_over_rtdl_bucketized_tree"
        rtdl_tree_node_count = len(rtdl_tree["nodes"])
        rtdl_ordered_source_ids = list(rtdl_tree["ordered_source_ids"])[:32]
    elif rtdl_contract == RTDL_CONTRACT_AUTHOR_PREPARED:
        author_tree_bodies, author_root, _ = author_ref.build_author_bucket_tree(bodies)
        rtdl_points, rtdl_nodes = _author_tree_to_rtdl_prepared_arrays(
            rtdl_diag,
            author_tree_bodies,
            author_root,
        )
        rtdl_reference = _reference_author_traversal_over_prepared_arrays(
            rtdl_points,
            rtdl_nodes,
            theta=theta,
            softening=softening,
        )
        rtdl_contract_label = "author_bucket_tree_over_generic_flat_aggregate_arrays"
        rtdl_tree_node_count = len(rtdl_nodes)
        rtdl_ordered_source_ids = [int(point.id) for point in rtdl_points[:32]]
    else:
        raise ValueError(f"unsupported RTDL contract: {rtdl_contract}")
    author_forces = [float(row["scalar_force"]) for row in author_payload["force_rows"]]
    rtdl_forces = [float(row["scalar_force"]) * rtdl_force_scale for row in rtdl_reference["scalar_sum_rows"]]
    if len(author_forces) != len(rtdl_forces):
        raise RuntimeError("author and RTDL force vectors have different lengths")
    max_abs_error = 0.0
    max_rel_error = 0.0
    max_error_index: int | None = None
    mismatch_count = 0
    for index, (author_force, rtdl_force) in enumerate(zip(author_forces, rtdl_forces)):
        abs_error = abs(author_force - rtdl_force)
        denom = max(abs(author_force), abs(rtdl_force), 1.0)
        rel_error = abs_error / denom
        if abs_error > max_abs_error or rel_error > max_rel_error:
            max_abs_error = max(max_abs_error, abs_error)
            max_rel_error = max(max_rel_error, rel_error)
            max_error_index = index
        if abs_error > 1.0e-6 + 1.0e-6 * denom:
            mismatch_count += 1
    return {
        "mode": "author_contract_vs_rtdl_python_reference",
        "body_count": len(bodies),
        "author_contract": author_payload["contract"],
        "rtdl_contract": rtdl_contract_label,
        "rtdl_contract_mode": rtdl_contract,
        "alignment": "RTDL input is author-sorted so force vector indices match author output order.",
        "rtdl_force_scale": rtdl_force_scale,
        "author_summary": author_payload["summary"],
        "rtdl_summary": rtdl_reference["summary"],
        "rtdl_tree_node_count": rtdl_tree_node_count,
        "rtdl_ordered_source_ids": rtdl_ordered_source_ids,
        "max_abs_error": max_abs_error,
        "max_rel_error": max_rel_error,
        "max_error_index": max_error_index,
        "mismatch_count": mismatch_count,
        "matched": mismatch_count == 0,
        "claim_boundary": (
            "Local contract diagnostic only. A mismatch localizes differences "
            "between the selected RTDL-reference contract and the author "
            "bucket-tree contract; a match shows local contract alignment only. "
            "The patched author binary remains the paper comparator."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare author CPU contract reference against RTDL Python reference.")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--synthetic-count", type=int, default=64)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--softening", type=float, default=0.0)
    parser.add_argument("--rtdl-force-scale", type=float, default=0.1)
    parser.add_argument(
        "--rtdl-contract",
        choices=(RTDL_CONTRACT_CURRENT, RTDL_CONTRACT_AUTHOR_PREPARED),
        default=RTDL_CONTRACT_CURRENT,
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    bodies = (
        author_ref.read_treelogy_input(args.input)
        if args.input is not None
        else author_ref.make_synthetic_bodies(args.synthetic_count)
    )
    payload = compare_contracts(
        bodies,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        theta=args.theta,
        softening=args.softening,
        rtdl_force_scale=args.rtdl_force_scale,
        rtdl_contract=args.rtdl_contract,
    )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
