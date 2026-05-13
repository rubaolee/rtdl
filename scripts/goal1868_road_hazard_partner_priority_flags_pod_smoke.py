#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import rtdsl as rt


def _partner_tensor_factory(partner: str):
    if partner == "cupy":
        import cupy

        return {
            "tensor": lambda values, dtype: cupy.asarray(values, dtype=dtype),
            "sync": cupy.cuda.runtime.deviceSynchronize,
            "to_host": lambda value: [int(item) for item in cupy.asnumpy(value).tolist()],
            "uint32": cupy.uint32,
            "float64": cupy.float64,
            "float32": cupy.float32,
        }
    if partner == "torch":
        import torch

        device = torch.device("cuda:0")
        return {
            "tensor": lambda values, dtype: torch.tensor(values, dtype=dtype, device=device),
            "sync": torch.cuda.synchronize,
            "to_host": lambda value: [int(item) for item in value.detach().cpu().tolist()],
            "uint32": torch.uint32,
            "float64": torch.float64,
            "float32": torch.float32,
        }
    raise ValueError(f"unsupported partner: {partner!r}")


def _build_records(count: int):
    roads = []
    hazards = []
    expected_counts = []
    for index in range(count):
        base_y = float(index) * 3.0
        road_id = index + 1
        roads.append(rt.Segment(road_id, -0.25, base_y + 0.25, 2.25, base_y + 0.25))
        hazards.append(
            rt.Polygon(
                10_000 + index * 2,
                (
                    (0.0, base_y),
                    (1.0, base_y),
                    (0.0, base_y + 1.0),
                ),
            )
        )
        hit_count = 1
        if index % 2 == 0:
            hazards.append(
                rt.Polygon(
                    10_001 + index * 2,
                    (
                        (1.0, base_y),
                        (2.0, base_y),
                        (1.0, base_y + 1.0),
                    ),
                )
            )
            hit_count = 2
        expected_counts.append(hit_count)
    return tuple(roads), tuple(hazards), expected_counts


def _build_partner_columns(roads, hazards, partner: str):
    runtime = _partner_tensor_factory(partner)
    ray_columns = {
        "ids": runtime["tensor"]([road.id for road in roads], runtime["uint32"]),
        "ox": runtime["tensor"]([road.x0 for road in roads], runtime["float64"]),
        "oy": runtime["tensor"]([road.y0 for road in roads], runtime["float64"]),
        "dx": runtime["tensor"]([road.x1 - road.x0 for road in roads], runtime["float64"]),
        "dy": runtime["tensor"]([road.y1 - road.y0 for road in roads], runtime["float64"]),
        "tmax": runtime["tensor"]([1.0 for _ in roads], runtime["float64"]),
    }
    triangle_ids = []
    x0 = []
    y0 = []
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    aabbs = []
    for hazard in hazards:
        (ax, ay), (bx, by), (cx, cy) = hazard.vertices
        triangle_ids.append(hazard.id)
        x0.append(float(ax))
        y0.append(float(ay))
        x1.append(float(bx))
        y1.append(float(by))
        x2.append(float(cx))
        y2.append(float(cy))
        aabbs.append([min(ax, bx, cx), min(ay, by, cy), -1.0e-4, max(ax, bx, cx), max(ay, by, cy), 1.0e-4])
    triangle_columns = {
        "ids": runtime["tensor"](triangle_ids, runtime["uint32"]),
        "x0": runtime["tensor"](x0, runtime["float64"]),
        "y0": runtime["tensor"](y0, runtime["float64"]),
        "x1": runtime["tensor"](x1, runtime["float64"]),
        "y1": runtime["tensor"](y1, runtime["float64"]),
        "x2": runtime["tensor"](x2, runtime["float64"]),
        "y2": runtime["tensor"](y2, runtime["float64"]),
    }
    triangle_aabbs = runtime["tensor"](aabbs, runtime["float32"])
    runtime["sync"]()
    return ray_columns, triangle_columns, triangle_aabbs, runtime


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _gpu_name() -> str:
    try:
        return subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"], text=True).strip()
    except Exception:
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1868 road-hazard partner priority flag pod smoke.")
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--threshold", type=int, default=2)
    parser.add_argument("--partners", default="cupy,torch")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be positive")
    partners = tuple(part.strip() for part in args.partners.split(",") if part.strip())
    roads, hazards, expected_counts = _build_records(args.count)
    expected_flags = [1 if count >= args.threshold else 0 for count in expected_counts]
    output_capacity = max(1, len(roads) * len(hazards))
    print(
        f"[setup] count={args.count} hazards={len(hazards)} threshold={args.threshold} output_capacity={output_capacity}",
        flush=True,
    )

    results = {}
    for partner in partners:
        print(f"[partner] building {partner} columns", flush=True)
        ray_columns, triangle_columns, triangle_aabbs, runtime = _build_partner_columns(roads, hazards, partner)
        print(f"[partner] running {partner} priority flags", flush=True)
        result = rt.road_hazard_priority_flags_optix_partner_device_columns(
            ray_columns,
            triangle_columns,
            triangle_aabbs,
            threshold=args.threshold,
            partner=partner,
            output_capacity=output_capacity,
            return_metadata=True,
        )
        runtime["sync"]()
        columns = result["columns"]
        road_ids = runtime["to_host"](columns["road_ids"])
        hit_counts = runtime["to_host"](columns["hit_counts"])
        priority_flags = runtime["to_host"](columns["priority_flags"])
        if hit_counts != expected_counts:
            raise RuntimeError(f"{partner} hit counts mismatch: {hit_counts} != {expected_counts}")
        if priority_flags != expected_flags:
            raise RuntimeError(f"{partner} priority flags mismatch: {priority_flags} != {expected_flags}")
        results[partner] = {
            "columns": {
                "road_ids": road_ids,
                "hit_counts": hit_counts,
                "priority_flags": priority_flags,
            },
            "metadata": result["metadata"],
        }

    payload = {
        "status": "pass",
        "goal": "Goal1868",
        "git_commit": _git_commit(),
        "gpu": _gpu_name(),
        "count": args.count,
        "threshold": args.threshold,
        "expected_counts": expected_counts,
        "expected_flags": expected_flags,
        "results": results,
        "claim_boundary": {
            "local_contract_goal": False,
            "pod_smoke_goal": True,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
        },
    }
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[artifact] wrote {output}", flush=True)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
