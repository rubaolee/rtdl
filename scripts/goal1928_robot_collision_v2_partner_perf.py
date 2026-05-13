#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import rtdsl as rt
import goal760_optix_robot_pose_flags_phase_profiler as robot_profiler


def _partner_module(partner: str):
    if partner == "torch":
        import torch

        return {
            "name": "torch",
            "module": torch,
            "device": torch.device("cuda:0"),
            "uint32": torch.uint32,
            "float64": torch.float64,
            "float32": torch.float32,
            "tensor": lambda values, dtype, device: torch.tensor(values, dtype=dtype, device=device),
            "sync": torch.cuda.synchronize,
            "to_host_sum": lambda value: int(value.to(torch.int64).sum().item()),
            "to_host_uint32": lambda value: [int(item) for item in value.detach().cpu().tolist()],
        }
    if partner == "cupy":
        import cupy

        return {
            "name": "cupy",
            "module": cupy,
            "device": None,
            "uint32": cupy.uint32,
            "float64": cupy.float64,
            "float32": cupy.float32,
            "tensor": lambda values, dtype, device: cupy.asarray(values, dtype=dtype),
            "sync": cupy.cuda.runtime.deviceSynchronize,
            "to_host_sum": lambda value: int(cupy.asnumpy(cupy.sum(value, dtype=cupy.uint64)).item()),
            "to_host_uint32": lambda value: [int(item) for item in cupy.asnumpy(value).tolist()],
        }
    raise ValueError("partner must be 'torch' or 'cupy'")


def _stats(samples: list[float]) -> dict[str, float]:
    return {
        "min_s": min(samples),
        "median_s": statistics.median(samples),
        "max_s": max(samples),
    }


def _time(label: str, repeat: int, fn, *, sync=None):
    samples = []
    last = None
    print(f"[goal1928] timing {label} repeat={repeat}", flush=True)
    for index in range(repeat):
        start = time.perf_counter()
        last = fn()
        if sync is not None:
            sync()
        elapsed = time.perf_counter() - start
        samples.append(elapsed)
        print(f"[goal1928] {label} iter={index + 1} elapsed_s={elapsed:.6f}", flush=True)
    return _stats(samples), last


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _ray_columns(packed_rays, runtime: dict) -> dict[str, object]:
    records = list(packed_rays.records)
    device = runtime["device"]
    return {
        "ids": runtime["tensor"]([int(row.id) for row in records], runtime["uint32"], device),
        "ox": runtime["tensor"]([float(row.ox) for row in records], runtime["float64"], device),
        "oy": runtime["tensor"]([float(row.oy) for row in records], runtime["float64"], device),
        "dx": runtime["tensor"]([float(row.dx) for row in records], runtime["float64"], device),
        "dy": runtime["tensor"]([float(row.dy) for row in records], runtime["float64"], device),
        "tmax": runtime["tensor"]([float(row.tmax) for row in records], runtime["float64"], device),
    }


def _triangle_columns(triangles, runtime: dict) -> tuple[dict[str, object], object]:
    device = runtime["device"]
    aabbs = []
    for triangle in triangles:
        min_x = min(float(triangle.x0), float(triangle.x1), float(triangle.x2))
        min_y = min(float(triangle.y0), float(triangle.y1), float(triangle.y2))
        max_x = max(float(triangle.x0), float(triangle.x1), float(triangle.x2))
        max_y = max(float(triangle.y0), float(triangle.y1), float(triangle.y2))
        aabbs.append([min_x, min_y, -1.0e-4, max_x, max_y, 1.0e-4])
    return (
        {
            "ids": runtime["tensor"]([int(t.id) for t in triangles], runtime["uint32"], device),
            "x0": runtime["tensor"]([float(t.x0) for t in triangles], runtime["float64"], device),
            "y0": runtime["tensor"]([float(t.y0) for t in triangles], runtime["float64"], device),
            "x1": runtime["tensor"]([float(t.x1) for t in triangles], runtime["float64"], device),
            "y1": runtime["tensor"]([float(t.y1) for t in triangles], runtime["float64"], device),
            "x2": runtime["tensor"]([float(t.x2) for t in triangles], runtime["float64"], device),
            "y2": runtime["tensor"]([float(t.y2) for t in triangles], runtime["float64"], device),
        },
        runtime["tensor"](aabbs, runtime["float32"], device),
    )


def _pose_indices(values, runtime: dict):
    return runtime["tensor"]([int(item) for item in values], runtime["uint32"], runtime["device"])


def _v1_pose_flags(case: dict[str, object]) -> tuple[int, ...]:
    scene = rt.prepare_optix_ray_triangle_any_hit_2d(case["obstacle_triangles"])
    rays = None
    pose_indices = None
    try:
        rays = rt.prepare_optix_rays_2d(case["edge_rays"])
        pose_indices = rt.prepare_optix_pose_indices_2d(case["pose_indices"])
        flags = scene.pose_flags_prepared_indices(
            rays,
            pose_indices,
            pose_count=int(case["pose_count"]),
        )
        return tuple(1 if bool(flag) else 0 for flag in flags)
    finally:
        if pose_indices is not None:
            pose_indices.close()
        if rays is not None:
            rays.close()
        scene.close()


def run_case(*, pose_count: int, obstacle_count: int, repeat: int, partner: str) -> dict[str, object]:
    print(
        f"[goal1928] start robot_collision_screening partner={partner} "
        f"pose_count={pose_count} obstacle_count={obstacle_count}",
        flush=True,
    )
    runtime = _partner_module(partner)
    case = robot_profiler._make_scaled_case_packed_arrays(
        pose_count=pose_count,
        obstacle_count=obstacle_count,
    )
    ray_columns = _ray_columns(case["edge_rays"], runtime)
    triangle_cols, triangle_aabbs = _triangle_columns(case["obstacle_triangles"], runtime)
    pose_index_col = _pose_indices(case["pose_indices"], runtime)
    scene = rt.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        triangle_cols,
        triangle_aabbs,
    )
    output_cols = rt.allocate_robot_collision_pose_partner_device_output_columns(
        pose_count,
        int(case["edge_rays"].count),
        partner=partner,
    )
    try:
        v1_payload = robot_profiler.run_suite(
            mode="optix",
            pose_count=pose_count,
            obstacle_count=obstacle_count,
            iterations=repeat,
            validate=False,
            input_mode="packed_arrays",
            result_mode="pose_flags",
        )
        v1_stats = {
            "min_s": v1_payload["phases"]["prepared_pose_flags_warm_query_sec"]["min_sec"],
            "median_s": v1_payload["phases"]["prepared_pose_flags_warm_query_sec"]["median_sec"],
            "max_s": v1_payload["phases"]["prepared_pose_flags_warm_query_sec"]["max_sec"],
        }
        v2_stats, v2_result = _time(
            f"robot_collision_screening:v2_prepared_partner:{partner}",
            repeat,
            lambda: rt.robot_collision_pose_flags_optix_prepared_partner_device_columns(
                scene,
                ray_columns,
                pose_index_col,
                pose_count=pose_count,
                partner=partner,
                output_columns=output_cols,
                return_metadata=True,
            ),
            sync=runtime["sync"],
        )
        v1_count = int(v1_payload["result"]["colliding_pose_count"])
        v1_flags = _v1_pose_flags(case)
        v2_flags = tuple(runtime["to_host_uint32"](v2_result["columns"]["pose_collision_flags"]))
        v2_count = runtime["to_host_sum"](v2_result["columns"]["pose_collision_flags"])
        return {
            "app": "robot_collision_screening",
            "partner": partner,
            "pose_count": pose_count,
            "obstacle_count": obstacle_count,
            "ray_count": int(case["edge_rays"].count),
            "triangle_count": len(case["obstacle_triangles"]),
            "v1_8_prepared_optix_pose_flags": v1_stats,
            "v2_prepared_native_optix_partner_pose_flags": v2_stats,
            "v2_vs_v1_8_prepared_ratio": (
                v2_stats["median_s"] / v1_stats["median_s"] if v1_stats["median_s"] > 0.0 else None
            ),
            "parity": {
                "colliding_pose_count_match": v1_count == v2_count,
                "pose_collision_flags_match": v1_flags == v2_flags,
                "v1_colliding_pose_count": v1_count,
                "v2_colliding_pose_count": v2_count,
            },
            "metadata": v2_result["metadata"],
            "status": "pass" if v1_count == v2_count and v1_flags == v2_flags else "fail",
        }
    finally:
        scene.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1928 robot collision v2 partner performance harness.")
    parser.add_argument("--pose-count", type=int, default=4096)
    parser.add_argument("--obstacle-count", type=int, default=256)
    parser.add_argument("--partners", default="cupy,torch")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument(
        "--source-commit-label",
        default=None,
        help="Explicit source label for copied-source pod runs that lack .git metadata.",
    )
    parser.add_argument("--output", default="docs/reports/goal1928_robot_collision_v2_partner_perf.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    partners = [item.strip() for item in args.partners.split(",") if item.strip()]
    results = [
        run_case(
            pose_count=args.pose_count,
            obstacle_count=args.obstacle_count,
            repeat=args.repeat,
            partner=partner,
        )
        for partner in partners
    ]
    commit = args.source_commit_label or _git_commit()
    payload = {
        "goal": "Goal1928",
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "git_commit": commit,
        "source_commit_label": commit,
        "gpu": _gpu_name(),
        "results": results,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "package_install_claim_authorized": False,
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
