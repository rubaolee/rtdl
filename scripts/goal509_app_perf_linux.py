from __future__ import annotations

import argparse
import gc
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.rtdl_barnes_hut_force_app import SOFTENING
from examples.rtdl_barnes_hut_force_app import THETA
from examples.rtdl_barnes_hut_force_app import approximate_forces_from_candidates
from examples.rtdl_barnes_hut_force_app import barnes_hut_node_candidate_kernel
from examples.rtdl_barnes_hut_force_app import brute_force_forces
from examples.rtdl_barnes_hut_force_app import build_one_level_quadtree
from examples.rtdl_barnes_hut_force_app import Body
from examples.rtdl_barnes_hut_force_app import QuadNode
from examples.rtdl_robot_collision_screening_app import robot_edge_ray_hitcount_kernel


BACKENDS = ("cpu", "embree", "optix", "vulkan")


def _safe_version(fn: Callable[[], object]) -> str | None:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def _host_info() -> dict[str, object]:
    def _command(cmd: list[str]) -> str | None:
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=5).strip()
        except Exception:
            return None

    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "processor": platform.processor(),
        "nvidia_smi": _command(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "embree_version": _safe_version(rt.embree_version),
        "optix_version": _safe_version(rt.optix_version),
        "vulkan_version": _safe_version(rt.vulkan_version),
    }


def _run_kernel_backend(backend: str, kernel_fn, **inputs):
    if backend == "cpu":
        return rt.run_cpu(kernel_fn, **inputs)
    if backend == "embree":
        return rt.run_embree(kernel_fn, **inputs)
    if backend == "optix":
        return rt.run_optix(kernel_fn, **inputs)
    if backend == "vulkan":
        return rt.run_vulkan(kernel_fn, **inputs)
    raise ValueError(f"unsupported backend: {backend}")


def _measure(name: str, fn: Callable[[], dict[str, object]], iterations: int) -> dict[str, object]:
    samples: list[float] = []
    payload: dict[str, object] | None = None
    for _ in range(iterations):
        gc.collect()
        start = time.perf_counter()
        try:
            payload = fn()
        except Exception as exc:
            return {"name": name, "status": "error", "error": f"{type(exc).__name__}: {exc}"}
        samples.append(time.perf_counter() - start)
    assert payload is not None
    return {
        "name": name,
        "status": "ok",
        "iterations": iterations,
        "median_sec": statistics.median(samples),
        "min_sec": min(samples),
        "max_sec": max(samples),
        "last_result": payload,
    }


def _rect_triangles(rect_id: int, x0: float, y0: float, x1: float, y1: float) -> tuple[rt.Triangle, rt.Triangle]:
    return (
        rt.Triangle(id=rect_id * 2, x0=x0, y0=y0, x1=x1, y1=y0, x2=x1, y2=y1),
        rt.Triangle(id=rect_id * 2 + 1, x0=x0, y0=y0, x1=x1, y1=y1, x2=x0, y2=y1),
    )


def _edge_rays_for_rect(pose_id: int, cx: float, cy: float, width: float, height: float) -> tuple[rt.Ray2D, ...]:
    half_w = width / 2.0
    half_h = height / 2.0
    vertices = (
        (cx - half_w, cy - half_h),
        (cx + half_w, cy - half_h),
        (cx + half_w, cy + half_h),
        (cx - half_w, cy + half_h),
    )
    rays: list[rt.Ray2D] = []
    for edge_index, ((x0, y0), (x1, y1)) in enumerate(zip(vertices, vertices[1:] + vertices[:1])):
        rays.append(rt.Ray2D(id=pose_id * 10 + edge_index, ox=x0, oy=y0, dx=x1 - x0, dy=y1 - y0, tmax=1.0))
    return tuple(rays)


def make_robot_case(pose_count: int, obstacle_count: int) -> dict[str, object]:
    if pose_count < 1 or obstacle_count < 1:
        raise ValueError("pose_count and obstacle_count must be positive")
    obstacle_triangles: list[rt.Triangle] = []
    grid = int(math.ceil(math.sqrt(obstacle_count)))
    for i in range(obstacle_count):
        gx = i % grid
        gy = i // grid
        x0 = gx * 1.5 + 0.35
        y0 = gy * 1.2 - 0.25
        obstacle_triangles.extend(_rect_triangles(1000 + i, x0, y0, x0 + 0.55, y0 + 0.45))

    edge_rays: list[rt.Ray2D] = []
    for pose_id in range(1, pose_count + 1):
        gx = (pose_id - 1) % grid
        gy = ((pose_id - 1) // grid) % grid
        # Alternate clear and obstacle-crossing poses on the same deterministic grid.
        offset = 0.45 if pose_id % 2 == 0 else -0.35
        cx = gx * 1.5 + offset
        cy = gy * 1.2
        edge_rays.extend(_edge_rays_for_rect(pose_id, cx, cy, width=0.75, height=0.25))
    return {"edge_rays": tuple(edge_rays), "obstacle_triangles": tuple(obstacle_triangles)}


def _robot_summary(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    hit_rows = sum(1 for row in rows if int(row["hit_count"]) > 0)
    total_hits = sum(int(row["hit_count"]) for row in rows)
    colliding_poses = sorted({int(row["ray_id"]) // 10 for row in rows if int(row["hit_count"]) > 0})
    return {"row_count": len(rows), "hit_rows": hit_rows, "total_hits": total_hits, "colliding_pose_count": len(colliding_poses)}


def run_robot_perf(sizes: tuple[int, ...], obstacle_count: int, iterations: int, backends: tuple[str, ...]) -> list[dict[str, object]]:
    cases = []
    for pose_count in sizes:
        case = make_robot_case(pose_count, obstacle_count)
        oracle = _robot_summary(tuple(rt.ray_triangle_hit_count_cpu(case["edge_rays"], case["obstacle_triangles"])))
        measurements = []
        for backend in backends:
            measurements.append(
                _measure(
                    f"robot_{backend}",
                    lambda backend=backend, case=case: {
                        **_robot_summary(tuple(_run_kernel_backend(backend, robot_edge_ray_hitcount_kernel, **case))),
                    },
                    iterations,
                )
            )
        for measurement in measurements:
            if measurement["status"] == "ok":
                measurement["matches_oracle"] = measurement["last_result"] == oracle
        cases.append(
            {
                "pose_count": pose_count,
                "edge_ray_count": len(case["edge_rays"]),
                "obstacle_triangle_count": len(case["obstacle_triangles"]),
                "oracle": oracle,
                "measurements": measurements,
            }
        )
    return cases


def make_barnes_bodies(body_count: int) -> tuple[Body, ...]:
    if body_count < 1:
        raise ValueError("body_count must be positive")
    grid = int(math.ceil(math.sqrt(body_count)))
    bodies: list[Body] = []
    for i in range(body_count):
        gx = i % grid
        gy = i // grid
        x = (gx / max(1, grid - 1)) * 4.0 - 2.0
        y = (gy / max(1, grid - 1)) * 4.0 - 2.0
        # Deterministic perturbation prevents too many exact ties.
        x += ((i * 17) % 11 - 5) * 0.001
        y += ((i * 31) % 13 - 6) * 0.001
        mass = 1.0 + (i % 7) * 0.1
        bodies.append(Body(id=i + 1, x=x, y=y, mass=mass))
    return tuple(bodies)


def _body_points(bodies: tuple[Body, ...]) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=body.id, x=body.x, y=body.y) for body in bodies)


def _node_points(nodes: tuple[QuadNode, ...]) -> tuple[rt.Point, ...]:
    return tuple(rt.Point(id=node.id, x=node.cx, y=node.cy) for node in nodes)


def _barnes_candidate_summary(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "candidate_row_count": len(rows),
        "body_count_with_candidates": len({int(row["query_id"]) for row in rows}),
        "node_count_seen": len({int(row["neighbor_id"]) for row in rows}),
    }


def _barnes_full_summary(
    bodies: tuple[Body, ...],
    nodes: tuple[QuadNode, ...],
    candidate_rows: tuple[dict[str, object], ...],
    *,
    include_oracle: bool,
) -> dict[str, object]:
    force_rows = approximate_forces_from_candidates(bodies, nodes, candidate_rows, theta=THETA)
    payload = {
        **_barnes_candidate_summary(candidate_rows),
        "force_row_count": len(force_rows),
        "accepted_node_total": sum(len(row["accepted_node_ids"]) for row in force_rows),
        "exact_body_total": sum(len(row["exact_body_ids"]) for row in force_rows),
    }
    if include_oracle:
        exact = brute_force_forces(bodies)
        max_rel = 0.0
        for row in force_rows:
            body_id = int(row["body_id"])
            exact_x, exact_y = exact[body_id]
            abs_error = math.hypot(float(row["force_x"]) - exact_x, float(row["force_y"]) - exact_y)
            exact_norm = max(math.hypot(exact_x, exact_y), 1.0e-12)
            max_rel = max(max_rel, abs_error / exact_norm)
        payload["max_relative_error"] = max_rel
    return payload


def run_barnes_perf(sizes: tuple[int, ...], iterations: int, backends: tuple[str, ...]) -> list[dict[str, object]]:
    cases = []
    for body_count in sizes:
        bodies = make_barnes_bodies(body_count)
        nodes = build_one_level_quadtree(bodies)
        inputs = {"bodies": _body_points(bodies), "nodes": _node_points(nodes)}
        oracle_rows = tuple(rt.run_cpu(barnes_hut_node_candidate_kernel, **inputs))
        oracle = _barnes_candidate_summary(oracle_rows)
        full_reference = _barnes_full_summary(bodies, nodes, oracle_rows, include_oracle=body_count <= 512)
        candidate_measurements = []
        full_measurements = []
        for backend in backends:
            candidate_measurements.append(
                _measure(
                    f"barnes_candidate_{backend}",
                    lambda backend=backend, inputs=inputs: _barnes_candidate_summary(
                        tuple(_run_kernel_backend(backend, barnes_hut_node_candidate_kernel, **inputs))
                    ),
                    iterations,
                )
            )
            full_measurements.append(
                _measure(
                    f"barnes_full_app_{backend}",
                    lambda backend=backend, bodies=bodies, nodes=nodes, inputs=inputs: _barnes_full_summary(
                        bodies,
                        nodes,
                        tuple(_run_kernel_backend(backend, barnes_hut_node_candidate_kernel, **inputs)),
                        include_oracle=False,
                    ),
                    iterations,
                )
            )
        for measurement in candidate_measurements:
            if measurement["status"] == "ok":
                measurement["matches_oracle"] = measurement["last_result"] == oracle
        for measurement in full_measurements:
            if measurement["status"] == "ok":
                comparable = dict(measurement["last_result"])
                comparable.pop("max_relative_error", None)
                ref = dict(full_reference)
                ref.pop("max_relative_error", None)
                measurement["matches_reference_reduction"] = comparable == ref
        cases.append(
            {
                "body_count": body_count,
                "node_count": len(nodes),
                "oracle_candidate_summary": oracle,
                "full_reference_summary": full_reference,
                "candidate_measurements": candidate_measurements,
                "full_measurements": full_measurements,
            }
        )
    return cases


def _parse_ints(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(",") if part.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal509 Linux performance benchmark for v0.8 robot and Barnes-Hut apps.")
    parser.add_argument("--robot-sizes", default="1000,5000,10000")
    parser.add_argument("--robot-obstacles", type=int, default=256)
    parser.add_argument("--barnes-sizes", default="256,1024,4096")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--backends", default="cpu,embree,optix,vulkan")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    backends = tuple(part.strip() for part in args.backends.split(",") if part.strip())
    payload = {
        "goal": "goal509_v0_8_robot_barnes_perf",
        "host": _host_info(),
        "pid": os.getpid(),
        "iterations": args.iterations,
        "fairness_contract": {
            "robot": "all backends run the same ray/triangle hit-count kernel on identical rays and triangles; CPU ray_triangle_hit_count_cpu defines correctness",
            "barnes_candidate": "all backends run the same fixed_radius_neighbors body-to-node candidate kernel on identical one-level quadtree nodes",
            "barnes_full_app": "full timing includes Python opening-rule and force reduction; report candidate timing separately to avoid claiming RTDL owns Python reduction work",
        },
        "robot_cases": run_robot_perf(_parse_ints(args.robot_sizes), args.robot_obstacles, args.iterations, backends),
        "barnes_cases": run_barnes_perf(_parse_ints(args.barnes_sizes), args.iterations, backends),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "robot_cases": len(payload["robot_cases"]), "barnes_cases": len(payload["barnes_cases"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
