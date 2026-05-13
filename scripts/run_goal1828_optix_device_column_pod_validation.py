from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _device_columns(torch):
    device = torch.device("cuda:0")
    triangles = {
        "ids": torch.tensor([11], dtype=torch.uint32, device=device),
        "x0": torch.tensor([0.0], dtype=torch.float64, device=device),
        "y0": torch.tensor([0.0], dtype=torch.float64, device=device),
        "x1": torch.tensor([1.0], dtype=torch.float64, device=device),
        "y1": torch.tensor([0.0], dtype=torch.float64, device=device),
        "x2": torch.tensor([0.0], dtype=torch.float64, device=device),
        "y2": torch.tensor([1.0], dtype=torch.float64, device=device),
    }
    rays = {
        "ids": torch.tensor([101, 102], dtype=torch.uint32, device=device),
        "ox": torch.tensor([-0.25, 2.0], dtype=torch.float64, device=device),
        "oy": torch.tensor([0.25, 2.0], dtype=torch.float64, device=device),
        "dx": torch.tensor([1.0, 1.0], dtype=torch.float64, device=device),
        "dy": torch.tensor([0.0, 0.0], dtype=torch.float64, device=device),
        "tmax": torch.tensor([2.0, 2.0], dtype=torch.float64, device=device),
    }
    return rays, triangles


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal1828 OptiX partner device-column RTX validation")
    parser.add_argument("--output", default="docs/reports/goal1828_optix_device_column_pod_validation.json")
    args = parser.parse_args()

    import rtdsl as rt
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Goal1828 requires a CUDA-capable RTX pod with torch.cuda available")

    start = time.perf_counter()
    rays, triangles = _device_columns(torch)
    ray_packet = rt.pack_optix_ray_any_hit_2d_device_ray_inputs(rays)
    triangle_packet = rt.pack_optix_ray_any_hit_2d_device_triangle_inputs(triangles)

    scene = rt.prepare_optix_ray_triangle_any_hit_2d_device_triangles(triangles)
    try:
        torch.cuda.synchronize()
        execute_start = time.perf_counter()
        observed_count = scene.count_device_rays(rays)
        torch.cuda.synchronize()
        execute_seconds = time.perf_counter() - execute_start
    finally:
        scene.close()

    expected_count = 1
    passed = observed_count == expected_count
    result = {
        "goal": "Goal1828",
        "status": "pass" if passed else "fail",
        "expected_count": expected_count,
        "observed_count": observed_count,
        "device": torch.cuda.get_device_name(0),
        "torch_version": torch.__version__,
        "python": platform.python_version(),
        "elapsed_s": time.perf_counter() - start,
        "execute_s": execute_seconds,
        "ray_metadata": ray_packet["metadata"],
        "triangle_metadata": triangle_packet["metadata"],
        "claim_boundary": {
            "direct_device_column_execution_observed": passed,
            "true_zero_copy_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    output_path = _repo_root() / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
