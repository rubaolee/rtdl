from __future__ import annotations

import argparse
import json
import math
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


def make_scaled_case(*, pose_count: int, obstacle_count: int) -> dict[str, object]:
    if pose_count < 1:
        raise ValueError("pose_count must be positive")
    if obstacle_count < 1:
        raise ValueError("obstacle_count must be positive")

    grid = int(math.ceil(math.sqrt(obstacle_count)))
    obstacle_triangles: list[rt.Triangle] = []
    for obstacle_index in range(obstacle_count):
        gx = obstacle_index % grid
        gy = obstacle_index // grid
        x0 = gx * 1.5 + 0.35
        y0 = gy * 1.2 - 0.25
        obstacle_triangles.extend(_rect_triangles(1000 + obstacle_index, x0, y0, x0 + 0.55, y0 + 0.45))

    poses: list[dict[str, object]] = []
    edge_rays: list[rt.Ray2D] = []
    for pose_id in range(1, pose_count + 1):
        gx = (pose_id - 1) % grid
        gy = ((pose_id - 1) // grid) % grid
        # Alternate clear and obstacle-crossing poses on a deterministic grid.
        center_x = gx * 1.5 + (0.45 if pose_id % 2 == 0 else -0.35)
        center_y = gy * 1.2
        poses.append(
            {
                "pose_id": pose_id,
                "link_id": 1,
                "center_x": center_x,
                "center_y": center_y,
                "label": "crossing" if pose_id % 2 == 0 else "clear",
            }
        )
        edge_rays.extend(
            _edge_rays_for_link_rect(
                pose_id=pose_id,
                link_id=1,
                center_x=center_x,
                center_y=center_y,
                width=0.75,
                height=0.25,
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
        "edge_rays": tuple(edge_rays),
        "obstacle_triangles": tuple(obstacle_triangles),
        "poses": tuple(poses),
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


def _run_optix_prepared_hit_edge_count(
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
) -> dict[str, object]:
    with rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles) as prepared_scene:
        with rt.prepare_optix_rays_2d(edge_rays) as prepared_rays:
            hit_edge_count = prepared_scene.count(prepared_rays)
    return {
        "mode": "optix_prepared_hit_edge_count",
        "hit_edge_count": int(hit_edge_count),
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
    }


def _run_optix_prepared_pose_flags(
    edge_rays: tuple[rt.Ray2D, ...],
    obstacle_triangles: tuple[rt.Triangle, ...],
    poses: tuple[dict[str, object], ...],
    ray_metadata: dict[int, dict[str, int]],
) -> dict[str, object]:
    pose_ids = tuple(int(pose["pose_id"]) for pose in poses)
    pose_index_by_id = {pose_id: index for index, pose_id in enumerate(pose_ids)}
    pose_indices = tuple(pose_index_by_id[int(ray_metadata[int(ray.id)]["pose_id"])] for ray in edge_rays)
    with rt.prepare_optix_ray_triangle_any_hit_2d(obstacle_triangles) as prepared_scene:
        with rt.prepare_optix_rays_2d(edge_rays) as prepared_rays:
            pose_flags = prepared_scene.pose_flags_packed(prepared_rays, pose_indices, pose_count=len(pose_ids))
    return {
        "mode": "optix_prepared_pose_flags",
        "pose_collision_flags": tuple(
            {"pose_id": pose_id, "collides": bool(pose_flags[index])}
            for index, pose_id in enumerate(pose_ids)
        ),
        "colliding_pose_ids": tuple(pose_id for index, pose_id in enumerate(pose_ids) if pose_flags[index]),
        "colliding_pose_count": sum(1 for flag in pose_flags if flag),
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
    }


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


def _compact_collision_payload(
    *,
    mode: str,
    summary: dict[str, object],
    rows: tuple[dict[str, object], ...],
    oracle_summary: dict[str, object],
) -> dict[str, object]:
    hit_edge_count = sum(1 for row in rows if bool(row["any_hit"]))
    oracle_hit_edge_count = sum(1 for row in oracle_summary["edge_any_hit_rows"] if bool(row["any_hit"]))
    if mode == "full":
        return {
            "rows": rows,
            "edge_any_hit_rows": summary["edge_any_hit_rows"],
            "pose_collision_flags": summary["pose_collision_flags"],
            "colliding_pose_ids": summary["colliding_pose_ids"],
            "pose_summaries": summary["pose_summaries"],
            "oracle": oracle_summary,
            "matches_oracle": summary == oracle_summary,
        }
    if mode == "pose_flags":
        return {
            "pose_collision_flags": summary["pose_collision_flags"],
            "colliding_pose_ids": summary["colliding_pose_ids"],
            "colliding_pose_count": len(summary["colliding_pose_ids"]),
            "oracle_colliding_pose_ids": oracle_summary["colliding_pose_ids"],
            "matches_oracle": summary["pose_collision_flags"] == oracle_summary["pose_collision_flags"],
        }
    if mode == "hit_count":
        return {
            "hit_edge_count": int(hit_edge_count),
            "oracle_hit_edge_count": int(oracle_hit_edge_count),
            "matches_oracle": int(hit_edge_count) == int(oracle_hit_edge_count),
        }
    raise ValueError("output_mode must be 'full', 'pose_flags', or 'hit_count'")


def run_app(
    backend: str = "cpu_python_reference",
    optix_summary_mode: str = "rows",
    output_mode: str = "full",
    *,
    pose_count: int | None = None,
    obstacle_count: int | None = None,
) -> dict[str, object]:
    if optix_summary_mode not in {"rows", "prepared_count", "prepared_pose_flags"}:
        raise ValueError("optix_summary_mode must be 'rows', 'prepared_count', or 'prepared_pose_flags'")
    if optix_summary_mode != "rows" and backend != "optix":
        raise ValueError("prepared OptiX summary modes require backend='optix'")
    if output_mode not in {"full", "pose_flags", "hit_count"}:
        raise ValueError("output_mode must be 'full', 'pose_flags', or 'hit_count'")

    if (pose_count is None) != (obstacle_count is None):
        raise ValueError("pose_count and obstacle_count must be provided together")

    case = (
        make_demo_case()
        if pose_count is None
        else make_scaled_case(pose_count=pose_count, obstacle_count=int(obstacle_count))
    )
    edge_rays = case["edge_rays"]
    obstacle_triangles = case["obstacle_triangles"]
    poses = case["poses"]
    ray_metadata = case["ray_metadata"]

    oracle_rows = rt.ray_triangle_any_hit_cpu(edge_rays, obstacle_triangles)
    oracle_summary = _summarize_collisions(oracle_rows, poses, ray_metadata)

    if backend == "optix" and optix_summary_mode == "prepared_count":
        prepared_summary = _run_optix_prepared_hit_edge_count(edge_rays, obstacle_triangles)
        expected_hit_count = sum(1 for row in oracle_rows if row["any_hit"])
        return {
            "app": "robot_collision_screening",
            "backend": backend,
            "optix_summary_mode": optix_summary_mode,
            "output_mode": "hit_count",
            "pose_count": len(poses),
            "edge_ray_count": len(edge_rays),
            "obstacle_triangle_count": len(obstacle_triangles),
            "prepared_summary": prepared_summary,
            "oracle_hit_edge_count": int(expected_hit_count),
            "matches_oracle": int(prepared_summary["hit_edge_count"]) == int(expected_hit_count),
            "native_continuation_active": True,
            "native_continuation_backend": "optix_prepared_any_hit_count",
            "rtdl_role": "RTDL uses a prepared OptiX ray/triangle any-hit scene and returns a native scalar hit-edge count, avoiding per-ray Python dict row materialization for this summary path.",
            "boundary": "Prepared count mode returns only the total hit-edge count. Use optix_summary_mode='rows' when pose-level witnesses and edge rows are needed.",
        }

    if backend == "optix" and optix_summary_mode == "prepared_pose_flags":
        prepared_summary = _run_optix_prepared_pose_flags(edge_rays, obstacle_triangles, poses, ray_metadata)
        return {
            "app": "robot_collision_screening",
            "backend": backend,
            "optix_summary_mode": optix_summary_mode,
            "output_mode": "pose_flags",
            "pose_count": len(poses),
            "edge_ray_count": len(edge_rays),
            "obstacle_triangle_count": len(obstacle_triangles),
            "prepared_summary": prepared_summary,
            "oracle_colliding_pose_ids": oracle_summary["colliding_pose_ids"],
            "matches_oracle": tuple(prepared_summary["pose_collision_flags"]) == tuple(oracle_summary["pose_collision_flags"]),
            "native_continuation_active": True,
            "native_continuation_backend": "optix_prepared_pose_flags",
            "rtdl_role": "RTDL uses a prepared OptiX ray/triangle any-hit scene and returns native pose collision flags, avoiding per-ray Python dict row materialization for this app summary path.",
            "boundary": "Prepared pose-flags mode returns one collision flag per pose. Use optix_summary_mode='rows' when edge-level witnesses or hit-ray IDs are needed.",
        }

    rows = _run_backend(backend, edge_rays, obstacle_triangles)
    summary = _summarize_collisions(rows, poses, ray_metadata)

    payload = {
        "app": "robot_collision_screening",
        "backend": backend,
        "optix_summary_mode": optix_summary_mode,
        "output_mode": output_mode,
        "pose_count": len(poses),
        "edge_ray_count": len(edge_rays),
        "obstacle_triangle_count": len(obstacle_triangles),
        "native_continuation_active": False,
        "native_continuation_backend": "none",
        "rtdl_role": "RTDL emits per-edge ray/triangle any-hit rows; rt.reduce_rows(any) converts edge rows into pose collision flags, and Python maps witnesses back to pose/link summaries.",
        "boundary": "Bounded 2D discrete-pose screening only; this is not continuous CCD, not full robot kinematics, and not a full mesh collision engine. Compact output modes reduce app-interface row volume but do not replace a native OptiX pose-level summary ABI.",
    }
    payload.update(_compact_collision_payload(mode=output_mode, summary=summary, rows=rows, oracle_summary=oracle_summary))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-derived discrete robot collision screening app using RTDL ray/triangle any-hit rows."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix"),
        default="cpu_python_reference",
    )
    parser.add_argument(
        "--optix-summary-mode",
        choices=("rows", "prepared_count", "prepared_pose_flags"),
        default="rows",
        help="For --backend optix, prepared_count returns a native scalar hit-edge count and prepared_pose_flags returns native pose flags instead of materializing per-ray rows.",
    )
    parser.add_argument(
        "--output-mode",
        choices=("full", "pose_flags", "hit_count"),
        default="full",
        help="For row mode, choose full witness rows, compact pose flags, or compact hit-count output.",
    )
    parser.add_argument("--pose-count", type=int, default=None, help="use a generated scalable pose fixture")
    parser.add_argument("--obstacle-count", type=int, default=None, help="use a generated scalable obstacle fixture")
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                args.optix_summary_mode,
                args.output_mode,
                pose_count=args.pose_count,
                obstacle_count=args.obstacle_count,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
