#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference


def _build_records(count: int):
    segments = []
    polygons = []
    for index in range(count):
        base_y = float(index) * 2.0
        segment_id = index + 1
        polygon_id = 1_000_001 + index
        segments.append(rt.Segment(segment_id, -0.25, base_y + 0.25, 1.25, base_y + 0.25))
        polygons.append(
            rt.Polygon(
                polygon_id,
                (
                    (0.0, base_y),
                    (1.0, base_y),
                    (0.0, base_y + 1.0),
                ),
            )
        )
    return tuple(segments), tuple(polygons)


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


def _build_partner_columns(segments, polygons, partner: str):
    runtime = _partner_tensor_factory(partner)
    t0 = time.perf_counter()
    ray_columns = {
        "ids": runtime["tensor"]([segment.id for segment in segments], runtime["uint32"]),
        "ox": runtime["tensor"]([segment.x0 for segment in segments], runtime["float64"]),
        "oy": runtime["tensor"]([segment.y0 for segment in segments], runtime["float64"]),
        "dx": runtime["tensor"]([segment.x1 - segment.x0 for segment in segments], runtime["float64"]),
        "dy": runtime["tensor"]([segment.y1 - segment.y0 for segment in segments], runtime["float64"]),
        "tmax": runtime["tensor"]([1.0 for _ in segments], runtime["float64"]),
    }
    triangle_ids = []
    x0 = []
    y0 = []
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    aabbs = []
    for polygon in polygons:
        (ax, ay), (bx, by), (cx, cy) = polygon.vertices
        triangle_ids.append(polygon.id)
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
    return ray_columns, triangle_columns, triangle_aabbs, runtime, time.perf_counter() - t0


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min_s": min(values),
        "median_s": statistics.median(values),
        "max_s": max(values),
    }


def _canonical_counts(rows) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(row["segment_id"]), int(row["hit_count"])) for row in rows))


def _columns_to_rows(columns: dict[str, object], runtime: dict) -> tuple[dict[str, int], ...]:
    segment_ids = runtime["to_host"](columns["segment_ids"])
    hit_counts = runtime["to_host"](columns["hit_counts"])
    return tuple({"segment_id": segment_id, "hit_count": hit_count} for segment_id, hit_count in zip(segment_ids, hit_counts))


def _time_call(label: str, iterations: int, fn):
    print(f"[timing] {label} iterations={iterations}", flush=True)
    samples = []
    last_result = None
    for index in range(iterations):
        t0 = time.perf_counter()
        last_result = fn()
        elapsed = time.perf_counter() - t0
        samples.append(elapsed)
        print(f"[timing] {label} iter={index + 1} elapsed_s={elapsed:.6f}", flush=True)
    return samples, last_result


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
    parser = argparse.ArgumentParser(description="Goal1863 v2.0 partner hitcount same-contract timing row.")
    parser.add_argument("--count", type=int, default=512)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--partners", default="cupy,torch")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be positive")
    if args.iterations <= 0:
        raise ValueError("--iterations must be positive")
    partners = tuple(part.strip() for part in args.partners.split(",") if part.strip())
    segments, polygons = _build_records(args.count)
    output_capacity = args.count * 2
    expected_rows = tuple({"segment_id": segment.id, "hit_count": 1} for segment in segments)
    expected_canonical = _canonical_counts(expected_rows)
    print(f"[setup] count={args.count} output_capacity={output_capacity}", flush=True)

    v18_one_shot_samples, v18_rows = _time_call(
        "v1_8_one_shot_native_optix_hitcount_rows",
        args.iterations,
        lambda: rt.run_optix(segment_polygon_hitcount_reference, segments=segments, polygons=polygons),
    )
    if _canonical_counts(v18_rows) != expected_canonical:
        raise RuntimeError("v1.8 native OptiX hitcount rows did not match expected rows")
    prepared = rt.prepare_optix_segment_polygon_hitcount_2d(polygons)
    try:
        v18_prepared_samples, v18_prepared_rows = _time_call(
            "v1_8_prepared_native_optix_hitcount_rows",
            args.iterations,
            lambda: prepared.run(segments),
        )
    finally:
        prepared.close()
    if _canonical_counts(v18_prepared_rows) != expected_canonical:
        raise RuntimeError("v1.8 prepared native OptiX hitcount rows did not match expected rows")

    partner_results = {}
    for partner in partners:
        print(f"[setup] building caller-owned {partner} columns", flush=True)
        ray_columns, triangle_columns, triangle_aabbs, runtime, build_s = _build_partner_columns(segments, polygons, partner)
        samples, result = _time_call(
            f"v2_0_partner_device_count_columns_{partner}",
            args.iterations,
            lambda: rt.segment_polygon_hitcount_optix_partner_device_count_columns(
                ray_columns,
                triangle_columns,
                triangle_aabbs,
                partner=partner,
                output_capacity=output_capacity,
            ),
        )
        rows = _columns_to_rows(result, runtime)
        if _canonical_counts(rows) != expected_canonical:
            raise RuntimeError(f"v2.0 partner device count columns did not match expected rows for {partner}")
        partner_results[partner] = {
            "column_build_s": build_s,
            "query_samples_s": samples,
            "query_summary": _summary(samples),
            "query_median_ratio_vs_v1_8_one_shot_native": statistics.median(samples) / statistics.median(v18_one_shot_samples),
            "query_median_ratio_vs_v1_8_prepared_native": statistics.median(samples) / statistics.median(v18_prepared_samples),
            "row_count": len(rows),
            "output_contract": "partner_owned_device_count_columns",
        }

    payload = {
        "status": "pass",
        "goal": "Goal1863",
        "git_commit": _git_commit(),
        "gpu": _gpu_name(),
        "count": args.count,
        "iterations": args.iterations,
        "output_capacity": output_capacity,
        "baseline": {
            "name": "v1_8_one_shot_native_optix_hitcount_rows",
            "query_samples_s": v18_one_shot_samples,
            "query_summary": _summary(v18_one_shot_samples),
            "row_count": len(v18_rows),
        },
        "prepared_baseline": {
            "name": "v1_8_prepared_native_optix_hitcount_rows",
            "query_samples_s": v18_prepared_samples,
            "query_summary": _summary(v18_prepared_samples),
            "row_count": len(v18_prepared_rows),
        },
        "partners": partner_results,
        "parity": {
            "expected_row_count": len(expected_rows),
            "strict_counts_match": True,
        },
        "claim_boundary": {
            "same_contract_timing_row": True,
            "partner_output_columns_true_zero_copy_authorized": True,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "package_install_claim_authorized": False,
        },
    }
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"[artifact] wrote {path}", flush=True)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
