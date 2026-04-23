from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


THETA = 0.75
SOFTENING = 0.05
NODE_DISCOVERY_RADIUS = 10.0
K_MAX = 16


@dataclass(frozen=True)
class Body:
    id: int
    x: float
    y: float
    mass: float


@dataclass(frozen=True)
class QuadNode:
    id: int
    cx: float
    cy: float
    half_size: float
    mass: float
    body_ids: tuple[int, ...]


@rt.kernel(backend="rtdl", precision="float_approx")
def barnes_hut_node_candidate_kernel():
    bodies = rt.input("bodies", rt.Points, role="probe")
    nodes = rt.input("nodes", rt.Points, role="build")
    candidates = rt.traverse(bodies, nodes, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=NODE_DISCOVERY_RADIUS, k_max=K_MAX))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_bodies() -> tuple[Body, ...]:
    return (
        Body(id=1, x=-1.40, y=-0.45, mass=2.0),
        Body(id=2, x=-1.10, y=0.15, mass=1.0),
        Body(id=3, x=-0.65, y=0.70, mass=1.5),
        Body(id=4, x=0.80, y=-0.60, mass=2.5),
        Body(id=5, x=1.15, y=0.10, mass=1.2),
        Body(id=6, x=1.55, y=0.65, mass=1.7),
    )


def make_generated_bodies(body_count: int) -> tuple[Body, ...]:
    if body_count < 1:
        raise ValueError("body_count must be positive")
    grid = int(math.ceil(math.sqrt(body_count)))
    bodies: list[Body] = []
    for index in range(body_count):
        gx = index % grid
        gy = index // grid
        x = (gx / max(1, grid - 1)) * 4.0 - 2.0
        y = (gy / max(1, grid - 1)) * 4.0 - 2.0
        # Deterministic perturbation prevents exact distance ties in perf runs.
        x += ((index * 17) % 11 - 5) * 0.001
        y += ((index * 31) % 13 - 6) * 0.001
        mass = 1.0 + (index % 7) * 0.1
        bodies.append(Body(id=index + 1, x=x, y=y, mass=mass))
    return tuple(bodies)


def build_one_level_quadtree(bodies: tuple[Body, ...]) -> tuple[QuadNode, ...]:
    if not bodies:
        raise ValueError("Barnes-Hut app requires at least one body")

    min_x = min(body.x for body in bodies)
    max_x = max(body.x for body in bodies)
    min_y = min(body.y for body in bodies)
    max_y = max(body.y for body in bodies)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    half_size = max(max_x - min_x, max_y - min_y) / 2.0 + 0.25

    buckets: dict[int, list[Body]] = {10: [], 11: [], 12: [], 13: []}
    for body in bodies:
        east = body.x >= center_x
        north = body.y >= center_y
        node_id = 10 + (1 if east else 0) + (2 if north else 0)
        buckets[node_id].append(body)

    nodes: list[QuadNode] = []
    child_half_size = half_size / 2.0
    offsets = {
        10: (-child_half_size, -child_half_size),
        11: (child_half_size, -child_half_size),
        12: (-child_half_size, child_half_size),
        13: (child_half_size, child_half_size),
    }
    for node_id, node_bodies in buckets.items():
        if not node_bodies:
            continue
        mass = sum(body.mass for body in node_bodies)
        com_x = sum(body.x * body.mass for body in node_bodies) / mass
        com_y = sum(body.y * body.mass for body in node_bodies) / mass
        nodes.append(
            QuadNode(
                id=node_id,
                cx=com_x,
                cy=com_y,
                half_size=child_half_size,
                mass=mass,
                body_ids=tuple(body.id for body in node_bodies),
            )
        )
    nodes.sort(key=lambda node: node.id)
    return tuple(nodes)


def _body_points(bodies: tuple[Body, ...]) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=body.id, x=body.x, y=body.y) for body in bodies)


def _node_points(nodes: tuple[QuadNode, ...]) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=node.id, x=node.cx, y=node.cy) for node in nodes)


def _run_node_candidates(backend: str, bodies: tuple[Body, ...], nodes: tuple[QuadNode, ...]):
    inputs = {"bodies": _body_points(bodies), "nodes": _node_points(nodes)}
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(barnes_hut_node_candidate_kernel, **inputs))
    if backend == "cpu":
        return tuple(rt.run_cpu(barnes_hut_node_candidate_kernel, **inputs))
    if backend == "embree":
        return tuple(rt.run_embree(barnes_hut_node_candidate_kernel, **inputs))
    if backend == "optix":
        return tuple(rt.run_optix(barnes_hut_node_candidate_kernel, **inputs))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(barnes_hut_node_candidate_kernel, **inputs))
    raise ValueError(f"unsupported backend `{backend}`")


def _optix_performance() -> dict[str, str]:
    support = rt.optix_app_performance_support("barnes_hut_force_app")
    return {"class": support.performance_class, "note": support.note}


def _enforce_rt_core_requirement(backend: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    raise RuntimeError(
        "barnes_hut_force_app OptiX path is CUDA-through-OptiX radius candidate generation today, not NVIDIA RT-core traversal"
    )


def _force_from_mass(body: Body, mass: float, cx: float, cy: float) -> tuple[float, float]:
    dx = cx - body.x
    dy = cy - body.y
    dist_sq = dx * dx + dy * dy + SOFTENING * SOFTENING
    inv_dist = 1.0 / math.sqrt(dist_sq)
    scale = body.mass * mass * inv_dist * inv_dist * inv_dist
    return dx * scale, dy * scale


def brute_force_forces(bodies: tuple[Body, ...]) -> dict[int, tuple[float, float]]:
    forces: dict[int, tuple[float, float]] = {}
    for body in bodies:
        fx = 0.0
        fy = 0.0
        for other in bodies:
            if other.id == body.id:
                continue
            dfx, dfy = _force_from_mass(body, other.mass, other.x, other.y)
            fx += dfx
            fy += dfy
        forces[body.id] = (fx, fy)
    return forces


def approximate_forces_from_candidates(
    bodies: tuple[Body, ...],
    nodes: tuple[QuadNode, ...],
    candidate_rows: tuple[dict[str, object], ...],
    *,
    theta: float,
) -> tuple[dict[str, object], ...]:
    body_by_id = {body.id: body for body in bodies}
    node_by_id = {node.id: node for node in nodes}
    candidate_node_ids: dict[int, set[int]] = {body.id: set() for body in bodies}
    for row in candidate_rows:
        candidate_node_ids[int(row["query_id"])].add(int(row["neighbor_id"]))

    rows: list[dict[str, object]] = []
    for body in bodies:
        fx = 0.0
        fy = 0.0
        accepted_nodes: list[int] = []
        exact_body_ids: list[int] = []
        for node_id in sorted(candidate_node_ids[body.id]):
            node = node_by_id[node_id]
            contains_self = body.id in node.body_ids
            dx = node.cx - body.x
            dy = node.cy - body.y
            distance = math.sqrt(dx * dx + dy * dy)
            opening_ratio = math.inf if distance == 0.0 else (2.0 * node.half_size) / distance
            if not contains_self and opening_ratio < theta:
                dfx, dfy = _force_from_mass(body, node.mass, node.cx, node.cy)
                fx += dfx
                fy += dfy
                accepted_nodes.append(node.id)
                continue

            for other_id in node.body_ids:
                if other_id == body.id:
                    continue
                other = body_by_id[other_id]
                dfx, dfy = _force_from_mass(body, other.mass, other.x, other.y)
                fx += dfx
                fy += dfy
                exact_body_ids.append(other.id)
        rows.append(
            {
                "body_id": body.id,
                "force_x": fx,
                "force_y": fy,
                "accepted_node_ids": accepted_nodes,
                "exact_body_ids": sorted(exact_body_ids),
            }
        )
    return tuple(rows)


def _force_error_rows(
    approximate_rows: tuple[dict[str, object], ...],
    exact_forces: dict[int, tuple[float, float]],
) -> tuple[dict[str, object], ...]:
    errors: list[dict[str, object]] = []
    for row in approximate_rows:
        body_id = int(row["body_id"])
        exact_x, exact_y = exact_forces[body_id]
        approx_x = float(row["force_x"])
        approx_y = float(row["force_y"])
        abs_error = math.hypot(approx_x - exact_x, approx_y - exact_y)
        exact_norm = max(math.hypot(exact_x, exact_y), 1.0e-12)
        errors.append(
            {
                "body_id": body_id,
                "abs_error": abs_error,
                "relative_error": abs_error / exact_norm,
            }
        )
    return tuple(errors)


def _candidate_summary(candidate_rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "candidate_row_count": len(candidate_rows),
        "body_count_with_candidates": len({int(row["query_id"]) for row in candidate_rows}),
        "node_count_seen": len({int(row["neighbor_id"]) for row in candidate_rows}),
    }


def _force_summary(force_rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "force_row_count": len(force_rows),
        "accepted_node_total": sum(len(row["accepted_node_ids"]) for row in force_rows),
        "exact_body_total": sum(len(row["exact_body_ids"]) for row in force_rows),
    }


def run_app(
    backend: str = "cpu_python_reference",
    *,
    theta: float = THETA,
    body_count: int | None = None,
    output_mode: str = "full",
    require_rt_core: bool = False,
) -> dict[str, object]:
    if output_mode not in {"full", "candidate_summary", "force_summary"}:
        raise ValueError("output_mode must be 'full', 'candidate_summary', or 'force_summary'")
    _enforce_rt_core_requirement(backend, require_rt_core)
    bodies = make_bodies() if body_count is None else make_generated_bodies(body_count)
    nodes = build_one_level_quadtree(bodies)
    candidate_rows = _run_node_candidates(backend, bodies, nodes)
    candidate_summary = _candidate_summary(tuple(candidate_rows))
    base_payload = {
        "app": "barnes_hut_force_app",
        "backend": backend,
        "theta": theta,
        "body_count": len(bodies),
        "node_count": len(nodes),
        **candidate_summary,
        "output_mode": output_mode,
        "rtdl_role": "RTDL emits body-to-quadtree-node candidate rows; Python applies the Barnes-Hut opening rule and computes force vectors.",
        "optix_performance": _optix_performance(),
        "rt_core_accelerated": False,
        "boundary": "Bounded one-level 2D approximation only; RTDL does not yet expose hierarchical tree-node primitives, Barnes-Hut opening predicates, or vector force reductions. Compact output modes characterize the RTDL candidate-generation slice separately from Python force rows.",
    }
    if output_mode == "candidate_summary":
        return base_payload

    approximate_rows = approximate_forces_from_candidates(bodies, nodes, candidate_rows, theta=theta)
    base_payload.update(_force_summary(approximate_rows))
    if output_mode == "force_summary":
        return base_payload

    exact_forces = brute_force_forces(bodies)
    error_rows = _force_error_rows(approximate_rows, exact_forces)

    return {
        **base_payload,
        "candidate_rows": candidate_rows,
        "force_rows": approximate_rows,
        "exact_force_rows": [
            {"body_id": body_id, "force_x": force[0], "force_y": force[1]}
            for body_id, force in sorted(exact_forces.items())
        ],
        "error_rows": error_rows,
        "max_relative_error": max(row["relative_error"] for row in error_rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived Barnes-Hut force app using RTDL node candidate rows plus Python force reduction."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--theta", type=float, default=THETA)
    parser.add_argument("--body-count", type=int, default=None, help="use a generated scalable body fixture")
    parser.add_argument(
        "--output-mode",
        choices=("full", "candidate_summary", "force_summary"),
        default="full",
        help="choose full rows, RTDL candidate summary only, or force-reduction summary",
    )
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                theta=args.theta,
                body_count=args.body_count,
                output_mode=args.output_mode,
                require_rt_core=args.require_rt_core,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
