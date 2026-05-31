from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from statistics import median
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _build_disjoint_triangle_ray_fixture(count: int):
    import rtdsl as rt

    side = max(1, int(math.ceil(math.sqrt(count))))
    triangles = []
    rays = []
    for index in range(count):
        gx = index % side
        gy = index // side
        x = float(gx * 2)
        y = float(gy * 2)
        triangles.append(
            rt.Triangle3D(
                id=index,
                x0=x,
                y0=y,
                z0=0.0,
                x1=x + 0.8,
                y1=y,
                z1=0.0,
                x2=x,
                y2=y + 0.8,
                z2=0.0,
            )
        )
        rays.append(
            rt.Ray3D(
                id=index,
                ox=x + 0.25,
                oy=y + 0.25,
                oz=-1.0,
                dx=0.0,
                dy=0.0,
                dz=1.0,
                tmax=4.0,
            )
        )
    return tuple(triangles), rt.pack_rays(tuple(rays), dimension=3)


def _summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        return {"sample_count": 0}
    totals = [float(sample["total_sec"]) for sample in samples]
    native_calls = [float(sample["native_call_sec"]) for sample in samples]
    traversals = [float(sample["traversal_sec"]) for sample in samples]
    rows = [int(sample["row_count"]) for sample in samples]
    return {
        "sample_count": len(samples),
        "median_total_sec": median(totals),
        "median_native_call_sec": median(native_calls),
        "median_traversal_sec": median(traversals),
        "min_total_sec": min(totals),
        "max_total_sec": max(totals),
        "row_count_min": min(rows),
        "row_count_max": max(rows),
    }


def _run_mode(scene, packed_rays, *, mode: str, capacity: int, iterations: int, warmups: int):
    if mode not in {"native_owned", "caller_owned_reusable"}:
        raise ValueError("unsupported mode")
    buffers = None
    if mode == "caller_owned_reusable":
        buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(capacity)
    samples: list[dict[str, Any]] = []
    try:
        for iteration in range(warmups + iterations):
            started = time.perf_counter()
            if mode == "native_owned":
                handoff = scene.ray_triangle_hit_stream_device_columns(
                    packed_rays,
                    max_rows=capacity,
                    deduplicate_primitives=False,
                )
                try:
                    pass
                finally:
                    if handoff.owner is not None and hasattr(handoff.owner, "close"):
                        handoff.owner.close()
            else:
                handoff = scene.ray_triangle_hit_stream_into_device_columns(
                    packed_rays,
                    buffers,
                    max_rows=capacity,
                    deduplicate_primitives=False,
                )
            elapsed = time.perf_counter() - started
            if iteration >= warmups:
                timing = dict(handoff.phase_timing_seconds)
                samples.append(
                    {
                        "iteration": iteration - warmups,
                        "total_sec": elapsed,
                        "native_call_sec": float(timing.get("native_call", 0.0)),
                        "traversal_sec": float(timing.get("traversal", 0.0)),
                        "row_count": int(handoff.row_count),
                        "overflow": bool(handoff.overflow),
                    }
                )
    finally:
        if buffers is not None:
            buffers.close()
    return samples


def run_probe(*, sizes: list[int], iterations: int, warmups: int) -> dict[str, Any]:
    import torch
    import rtdsl as rt

    payload: dict[str, Any] = {
        "goal": "goal2758",
        "rtdl_commit": os.environ.get("RTDL_SOURCE_COMMIT", ""),
        "rtdl_optix_library": os.environ.get("RTDL_OPTIX_LIBRARY", ""),
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "torch_cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "sizes": {},
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "host_synchronized_before_consumer": True,
            "compares_output_allocation_strategy_only": True,
        },
    }
    if not torch.cuda.is_available():
        raise RuntimeError("Goal2758 requires CUDA-capable torch")

    for size in sizes:
        print(f"[goal2758] building fixture size={size}", flush=True)
        triangles, packed_rays = _build_disjoint_triangle_ray_fixture(size)
        with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
            mode_payload: dict[str, Any] = {}
            for mode in ("native_owned", "caller_owned_reusable"):
                print(
                    f"[goal2758] running size={size} mode={mode} warmups={warmups} iterations={iterations}",
                    flush=True,
                )
                samples = _run_mode(
                    scene,
                    packed_rays,
                    mode=mode,
                    capacity=size,
                    iterations=iterations,
                    warmups=warmups,
                )
                mode_payload[mode] = {
                    "samples": samples,
                    "summary": _summarize(samples),
                }
                print(
                    f"[goal2758] done size={size} mode={mode} "
                    f"median_total={mode_payload[mode]['summary']['median_total_sec']:.6f}s",
                    flush=True,
                )
        native_total = mode_payload["native_owned"]["summary"]["median_total_sec"]
        reusable_total = mode_payload["caller_owned_reusable"]["summary"]["median_total_sec"]
        native_call = mode_payload["native_owned"]["summary"]["median_native_call_sec"]
        reusable_call = mode_payload["caller_owned_reusable"]["summary"]["median_native_call_sec"]
        mode_payload["ratios"] = {
            "reusable_vs_native_owned_total": reusable_total / native_total if native_total else None,
            "reusable_vs_native_owned_native_call": reusable_call / native_call if native_call else None,
        }
        payload["sizes"][str(size)] = mode_payload
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="1024,8192,32768")
    parser.add_argument("--iterations", type=int, default=12)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sizes = [int(part) for part in args.sizes.split(",") if part.strip()]
    if any(size <= 0 for size in sizes):
        raise ValueError("all sizes must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = run_probe(sizes=sizes, iterations=args.iterations, warmups=args.warmups)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal2758] wrote {args.output}", flush=True)


if __name__ == "__main__":
    main()
