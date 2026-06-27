from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def numpy_columns():
    import numpy as np

    rays = {
        "ids": np.asarray([0, 1], dtype=np.uint32),
        "ox": np.asarray([-0.25, 2.0], dtype=np.float64),
        "oy": np.asarray([0.25, 2.0], dtype=np.float64),
        "dx": np.asarray([1.0, 1.0], dtype=np.float64),
        "dy": np.asarray([0.0, 0.0], dtype=np.float64),
        "tmax": np.asarray([2.0, 2.0], dtype=np.float64),
    }
    triangles = {
        "ids": np.asarray([0], dtype=np.uint32),
        "x0": np.asarray([0.0], dtype=np.float64),
        "y0": np.asarray([0.0], dtype=np.float64),
        "x1": np.asarray([1.0], dtype=np.float64),
        "y1": np.asarray([0.0], dtype=np.float64),
        "x2": np.asarray([0.0], dtype=np.float64),
        "y2": np.asarray([1.0], dtype=np.float64),
    }
    return rays, triangles


def torch_columns(device: str):
    import torch

    rays_np, triangles_np = numpy_columns()
    rays = {name: torch.as_tensor(value, device=device) for name, value in rays_np.items()}
    triangles = {name: torch.as_tensor(value, device=device) for name, value in triangles_np.items()}
    return rays, triangles


def cupy_columns():
    import cupy

    rays_np, triangles_np = numpy_columns()
    rays = {name: cupy.asarray(value) for name, value in rays_np.items()}
    triangles = {name: cupy.asarray(value) for name, value in triangles_np.items()}
    return rays, triangles


def build_columns(partner: str):
    if partner == "numpy":
        return numpy_columns()
    if partner == "torch-cuda":
        return torch_columns("cuda:0")
    if partner == "cupy-cuda":
        return cupy_columns()
    raise ValueError("partner must be one of: numpy, torch-cuda, cupy-cuda")


def run_demo(*, partner: str, backend: str) -> dict[str, object]:
    rays, triangles = build_columns(partner)
    result = rt.run_partner_ray_triangle_any_hit_2d(rays, triangles, backend=backend)
    return {
        "example": "rtdl_partner_anyhit",
        "partner_input": partner,
        "backend": backend,
        "hit_count": result["hit_count"],
        "ray_count": result["ray_count"],
        "triangle_count": result["triangle_count"],
        "source_protocols": list(result["source_protocols"]),
        "source_devices": list(result["source_devices"]),
        "transfer_mode": result["transfer_mode"],
        "true_zero_copy_authorized": result["true_zero_copy_authorized"],
        "rt_core_speedup_claim_authorized": result["rt_core_speedup_claim_authorized"],
        "partner_phase_timing_keys": sorted(result["partner_phase_timings_s"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a Python+partner RTDL any-hit example through explicit host staging."
    )
    parser.add_argument("--partner", choices=("numpy", "torch-cuda", "cupy-cuda"), default="numpy")
    parser.add_argument("--backend", choices=("embree", "optix"), default="embree")
    args = parser.parse_args()

    print(json.dumps(run_demo(partner=args.partner, backend=args.backend), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
