from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def robot_edge_any_hit_kernel():
    edge_rays = rt.input("edge_rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    obstacle_triangles = rt.input(
        "obstacle_triangles",
        rt.Triangles,
        layout=rt.Triangle2DLayout,
        role="build",
    )
    candidates = rt.traverse(edge_rays, obstacle_triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def _rect_triangles(rect_id: int, x0: float, y0: float, x1: float, y1: float) -> tuple[rt.Triangle, rt.Triangle]:
    return (
        rt.Triangle(id=rect_id * 2, x0=x0, y0=y0, x1=x1, y1=y0, x2=x1, y2=y1),
        rt.Triangle(id=rect_id * 2 + 1, x0=x0, y0=y0, x1=x1, y1=y1, x2=x0, y2=y1),
    )


def _edge_rays_for_link_rect(
    *,
    pose_id: int,
    link_id: int,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
) -> tuple[rt.Ray2D, ...]:
    half_w = width / 2.0
    half_h = height / 2.0
    vertices = (
        (center_x - half_w, center_y - half_h),
        (center_x + half_w, center_y - half_h),
        (center_x + half_w, center_y + half_h),
        (center_x - half_w, center_y + half_h),
    )
    rays: list[rt.Ray2D] = []
    for edge_index, ((x0, y0), (x1, y1)) in enumerate(zip(vertices, vertices[1:] + vertices[:1])):
        ray_id = pose_id * 1000 + link_id * 10 + edge_index
        rays.append(rt.Ray2D(id=ray_id, ox=x0, oy=y0, dx=x1 - x0, dy=y1 - y0, tmax=1.0))
    return tuple(rays)


def make_demo_case() -> dict[str, object]:
    poses = (
        {"pose_id": 1, "link_id": 1, "center_x": 0.0, "center_y": 0.0, "label": "clear_left"},
        {"pose_id": 2, "link_id": 1, "center_x": 1.65, "center_y": 0.0, "label": "boundary_crossing"},
        {"pose_id": 3, "link_id": 1, "center_x": 2.5, "center_y": 0.0, "label": "inside_obstacle"},
        {"pose_id": 4, "link_id": 1, "center_x": 3.8, "center_y": 0.0, "label": "clear_right"},
    )
    obstacle_triangles = _rect_triangles(rect_id=100, x0=2.0, y0=-0.6, x1=3.0, y1=0.6)
    edge_rays = tuple(
        ray
        for pose in poses
        for ray in _edge_rays_for_link_rect(
            pose_id=int(pose["pose_id"]),
            link_id=int(pose["link_id"]),
            center_x=float(pose["center_x"]),
            center_y=float(pose["center_y"]),
            width=0.8,
            height=0.3,
        )
    )
    ray_metadata = {
        ray.id: {
            "pose_id": ray.id // 1000,
            "link_id": (ray.id % 1000) // 10,
            "edge_id": ray.id % 10,
        }
        for ray in edge_rays
    }
    return {
        "edge_rays": edge_rays,
        "obstacle_triangles": obstacle_triangles,
        "poses": poses,
        "ray_metadata": ray_metadata,
    }


def _run_backend(backend: str, edge_rays: tuple[rt.Ray2D, ...], obstacle_triangles: tuple[rt.Triangle, ...]):
    inputs = {"edge_rays": edge_rays, "obstacle_triangles": obstacle_triangles}
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(robot_edge_any_hit_kernel, **inputs)
    if backend == "cpu":
        return rt.run_cpu(robot_edge_any_hit_kernel, **inputs)
    if backend == "embree":
        return rt.run_embree(robot_edge_any_hit_kernel, **inputs)
    if backend == "optix":
        return rt.run_optix(robot_edge_any_hit_kernel, **inputs)
    raise ValueError(f"unsupported backend `{backend}`")


def _attach_pose_metadata(
    rows: tuple[dict[str, object], ...],
    ray_metadata: dict[int, dict[str, int]],
) -> tuple[dict[str, object], ...]:
    enriched_rows: list[dict[str, object]] = []
    for row in rows:
        ray_id = int(row["ray_id"])
        metadata = ray_metadata[ray_id]
        enriched_rows.append(
            {
                "ray_id": ray_id,
                "pose_id": metadata["pose_id"],
                "link_id": metadata["link_id"],
                "edge_id": metadata["edge_id"],
                "any_hit": int(bool(row["any_hit"])),
            }
        )
    return tuple(enriched_rows)


def _summarize_collisions(
    rows: tuple[dict[str, object], ...],
    poses: tuple[dict[str, object], ...],
    ray_metadata: dict[int, dict[str, int]],
) -> dict[str, object]:
    enriched_rows = _attach_pose_metadata(rows, ray_metadata)
    pose_flags = {
        int(row["pose_id"]): bool(row["collides"])
        for row in rt.reduce_rows(
            enriched_rows,
            group_by="pose_id",
            op="any",
            value="any_hit",
            output_field="collides",
        )
    }
    pose_summaries = {
        int(pose["pose_id"]): {
            "pose_id": int(pose["pose_id"]),
            "label": str(pose["label"]),
            "collides": pose_flags.get(int(pose["pose_id"]), False),
            "hit_edge_count": 0,
            "hit_ray_ids": [],
        }
        for pose in poses
    }
    for row in enriched_rows:
        ray_id = int(row["ray_id"])
        any_hit = bool(row["any_hit"])
        if not any_hit:
            continue
        pose_id = int(row["pose_id"])
        summary = pose_summaries[pose_id]
        summary["hit_edge_count"] = int(summary["hit_edge_count"]) + 1
        summary["hit_ray_ids"].append(ray_id)

    colliding_pose_ids = sorted(pose_id for pose_id, summary in pose_summaries.items() if summary["collides"])
    return {
        "edge_any_hit_rows": enriched_rows,
        "pose_collision_flags": tuple(
            {"pose_id": pose_id, "collides": bool(pose_summaries[pose_id]["collides"])}
            for pose_id in sorted(pose_summaries)
        ),
        "colliding_pose_ids": colliding_pose_ids,
        "pose_summaries": [pose_summaries[pose_id] for pose_id in sorted(pose_summaries)],
    }


def run_app(backend: str = "cpu_python_reference") -> dict[str, object]:
    case = make_demo_case()
    edge_rays = case["edge_rays"]
    obstacle_triangles = case["obstacle_triangles"]
    poses = case["poses"]
    ray_metadata = case["ray_metadata"]

    rows = _run_backend(backend, edge_rays, obstacle_triangles)
    oracle_rows = rt.ray_triangle_any_hit_cpu(edge_rays, obstacle_triangles)
    summary = _summarize_collisions(rows, poses, ray_metadata)
    oracle_summary = _summarize_collisions(oracle_rows, poses, ray_metadata)

    return {
        "app": "robot_collision_screening",
        "backend": backend,
        "pose_count": len(poses),
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
        "rows": rows,
        "edge_any_hit_rows": summary["edge_any_hit_rows"],
        "pose_collision_flags": summary["pose_collision_flags"],
        "colliding_pose_ids": summary["colliding_pose_ids"],
        "pose_summaries": summary["pose_summaries"],
        "oracle": oracle_summary,
        "matches_oracle": summary == oracle_summary,
        "rtdl_role": "RTDL emits per-edge ray/triangle any-hit rows; rt.reduce_rows(any) converts edge rows into pose collision flags, and Python maps witnesses back to pose/link summaries.",
        "boundary": "Bounded 2D discrete-pose screening only; this is not continuous CCD, not full robot kinematics, and not a full mesh collision engine.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived discrete robot collision screening app using RTDL ray/triangle any-hit rows."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix"),
        default="cpu_python_reference",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
