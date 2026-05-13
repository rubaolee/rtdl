from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _torch_device_columns(torch):
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
    triangle_aabbs = torch.tensor(
        [[0.0, 0.0, -1.0e-4, 1.0, 1.0, 1.0e-4]],
        dtype=torch.float32,
        device=device,
    )
    rays = {
        "ids": torch.tensor([101, 102], dtype=torch.uint32, device=device),
        "ox": torch.tensor([-0.25, 2.0], dtype=torch.float64, device=device),
        "oy": torch.tensor([0.25, 2.0], dtype=torch.float64, device=device),
        "dx": torch.tensor([1.0, 1.0], dtype=torch.float64, device=device),
        "dy": torch.tensor([0.0, 0.0], dtype=torch.float64, device=device),
        "tmax": torch.tensor([2.0, 2.0], dtype=torch.float64, device=device),
    }
    return rays, triangles, triangle_aabbs


def _cupy_device_columns(cupy):
    triangles = {
        "ids": cupy.asarray([11], dtype=cupy.uint32),
        "x0": cupy.asarray([0.0], dtype=cupy.float64),
        "y0": cupy.asarray([0.0], dtype=cupy.float64),
        "x1": cupy.asarray([1.0], dtype=cupy.float64),
        "y1": cupy.asarray([0.0], dtype=cupy.float64),
        "x2": cupy.asarray([0.0], dtype=cupy.float64),
        "y2": cupy.asarray([1.0], dtype=cupy.float64),
    }
    triangle_aabbs = cupy.asarray(
        [[0.0, 0.0, -1.0e-4, 1.0, 1.0, 1.0e-4]],
        dtype=cupy.float32,
    )
    rays = {
        "ids": cupy.asarray([101, 102], dtype=cupy.uint32),
        "ox": cupy.asarray([-0.25, 2.0], dtype=cupy.float64),
        "oy": cupy.asarray([0.25, 2.0], dtype=cupy.float64),
        "dx": cupy.asarray([1.0, 1.0], dtype=cupy.float64),
        "dy": cupy.asarray([0.0, 0.0], dtype=cupy.float64),
        "tmax": cupy.asarray([2.0, 2.0], dtype=cupy.float64),
    }
    return rays, triangles, triangle_aabbs


def _partner_runtime(partner_name: str):
    if partner_name == "torch":
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("Goal1828 requires a CUDA-capable RTX pod with torch.cuda available")
        return {
            "module": torch,
            "version": torch.__version__,
            "device": torch.cuda.get_device_name(0),
            "sync": torch.cuda.synchronize,
            "factory": _torch_device_columns,
            "zeros": lambda shape, dtype: torch.zeros(shape, dtype=dtype, device=torch.device("cuda:0")),
            "uint32_dtype": torch.uint32,
            "to_host_list": lambda value: [int(item) for item in value.detach().cpu().tolist()],
        }
    if partner_name == "cupy":
        import cupy

        count = int(cupy.cuda.runtime.getDeviceCount())
        if count <= 0:
            raise RuntimeError("Goal1836 requires a CUDA-capable RTX pod with cupy.cuda available")
        props = cupy.cuda.runtime.getDeviceProperties(0)
        device_name = props.get("name", "cuda:0")
        if isinstance(device_name, bytes):
            device_name = device_name.decode("utf-8", errors="replace")
        return {
            "module": cupy,
            "version": cupy.__version__,
            "device": str(device_name),
            "sync": cupy.cuda.runtime.deviceSynchronize,
            "factory": _cupy_device_columns,
            "zeros": lambda shape, dtype: cupy.zeros(shape, dtype=dtype),
            "uint32_dtype": cupy.uint32,
            "to_host_list": lambda value: [int(item) for item in cupy.asnumpy(value).tolist()],
        }
    raise ValueError(f"unsupported partner: {partner_name!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal1828 OptiX partner device-column RTX validation")
    parser.add_argument("--output", default="docs/reports/goal1828_optix_device_column_pod_validation.json")
    parser.add_argument("--goal", default="Goal1828")
    parser.add_argument("--partner", choices=("torch", "cupy"), default="torch")
    parser.add_argument("--output-flags", action="store_true")
    parser.add_argument("--output-witnesses", action="store_true")
    args = parser.parse_args()
    if args.output_flags and args.output_witnesses:
        raise SystemExit("--output-flags and --output-witnesses are mutually exclusive")

    import rtdsl as rt

    partner = _partner_runtime(args.partner)
    start = time.perf_counter()
    rays, triangles, triangle_aabbs = partner["factory"](partner["module"])
    ray_packet = rt.pack_optix_ray_any_hit_2d_device_ray_inputs(rays)
    triangle_packet = rt.pack_optix_ray_any_hit_2d_device_triangle_zero_copy_scene_inputs(
        triangles,
        triangle_aabbs,
    )

    scene = rt.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        triangles,
        triangle_aabbs,
    )
    output_packet = None
    observed_flags = None
    try:
        partner["sync"]()
        execute_start = time.perf_counter()
        if args.output_witnesses:
            witness_ray_ids = partner["zeros"]((2,), partner["uint32_dtype"])
            witness_primitive_ids = partner["zeros"]((2,), partner["uint32_dtype"])
            output_packet = scene.write_device_any_hit_witnesses(
                rays,
                witness_ray_ids,
                witness_primitive_ids,
            )
            partner["sync"]()
            observed_witness_ray_ids = partner["to_host_list"](witness_ray_ids)
            observed_witness_primitive_ids = partner["to_host_list"](witness_primitive_ids)
            observed_count = sum(1 for value in observed_witness_primitive_ids if value != 0xFFFFFFFF)
        elif args.output_flags:
            output_flags = partner["zeros"]((2,), partner["uint32_dtype"])
            output_packet = scene.write_device_any_hit_flags(rays, output_flags)
            partner["sync"]()
            observed_flags = partner["to_host_list"](output_flags)
            observed_count = sum(observed_flags)
            observed_witness_ray_ids = None
            observed_witness_primitive_ids = None
        else:
            observed_count = scene.count_device_rays(rays)
            observed_witness_ray_ids = None
            observed_witness_primitive_ids = None
        partner["sync"]()
        execute_seconds = time.perf_counter() - execute_start
    finally:
        scene.close()

    expected_count = 1
    passed = observed_count == expected_count
    result = {
        "goal": args.goal,
        "status": "pass" if passed else "fail",
        "expected_count": expected_count,
        "observed_count": observed_count,
        "device": partner["device"],
        "partner": args.partner,
        "partner_version": partner["version"],
        f"{args.partner}_version": partner["version"],
        "python": platform.python_version(),
        "elapsed_s": time.perf_counter() - start,
        "execute_s": execute_seconds,
        "ray_metadata": ray_packet["metadata"],
        "triangle_metadata": triangle_packet["metadata"],
        "output_metadata": None if output_packet is None else output_packet["metadata"],
        "observed_flags": observed_flags,
        "observed_witness_ray_ids": observed_witness_ray_ids,
        "observed_witness_primitive_ids": observed_witness_primitive_ids,
        "claim_boundary": {
            "direct_device_column_execution_observed": passed,
            "ray_column_true_zero_copy_observed": bool(
                passed and ray_packet["metadata"].get("ray_columns_true_zero_copy_authorized")
            ),
            "triangle_scene_true_zero_copy_observed": bool(
                passed and triangle_packet["metadata"].get("triangle_scene_true_zero_copy_authorized")
            ),
            "whole_primitive_true_zero_copy_authorized": bool(
                passed
                and ray_packet["metadata"].get("ray_columns_true_zero_copy_authorized")
                and triangle_packet["metadata"].get("triangle_scene_true_zero_copy_authorized")
            ),
            "output_flags_true_zero_copy_observed": bool(
                passed
                and output_packet is not None
                and output_packet["metadata"].get("output_flags_true_zero_copy_authorized")
            ),
            "witness_outputs_true_zero_copy_observed": bool(
                passed
                and output_packet is not None
                and output_packet["metadata"].get("witness_outputs_true_zero_copy_authorized")
            ),
            "first_hit_witness_identity_observed": bool(
                passed
                and observed_witness_ray_ids == [101, 102]
                and observed_witness_primitive_ids == [11, 0xFFFFFFFF]
            ),
            "true_zero_copy_authorized": bool(
                passed
                and ray_packet["metadata"].get("ray_columns_true_zero_copy_authorized")
                and triangle_packet["metadata"].get("triangle_scene_true_zero_copy_authorized")
                and (
                    output_packet is None
                    or output_packet["metadata"].get("output_flags_true_zero_copy_authorized")
                    or output_packet["metadata"].get("witness_outputs_true_zero_copy_authorized")
                )
            ),
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
