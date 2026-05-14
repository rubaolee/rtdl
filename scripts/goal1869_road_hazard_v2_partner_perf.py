#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_road_hazard_screening import road_hazard_hitcount


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


def _build_partner_columns(roads, hazards, partner: str):
    runtime = _partner_tensor_factory(partner)
    t0 = time.perf_counter()
    ray_columns = {
        "ids": runtime["tensor"]([road.id for road in roads], runtime["uint32"]),
        "ox": runtime["tensor"]([road.x0 for road in roads], runtime["float32"]),
        "oy": runtime["tensor"]([road.y0 for road in roads], runtime["float32"]),
        "dx": runtime["tensor"]([road.x1 - road.x0 for road in roads], runtime["float32"]),
        "dy": runtime["tensor"]([road.y1 - road.y0 for road in roads], runtime["float32"]),
        "tmax": runtime["tensor"]([1.0 for _ in roads], runtime["float32"]),
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
    return ray_columns, triangle_columns, triangle_aabbs, runtime, time.perf_counter() - t0


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min_s": min(values),
        "median_s": statistics.median(values),
        "max_s": max(values),
    }


def _canonical_counts(rows) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(row["segment_id"]), int(row["hit_count"])) for row in rows))


def _flags_from_counts(rows, threshold: int) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(row["segment_id"]), 1 if int(row["hit_count"]) >= threshold else 0) for row in rows))


def _columns_to_flags(columns: dict[str, object], runtime: dict) -> tuple[tuple[int, int], ...]:
    road_ids = runtime["to_host"](columns["road_ids"])
    priority_flags = runtime["to_host"](columns["priority_flags"])
    return tuple(sorted((road_id, flag) for road_id, flag in zip(road_ids, priority_flags)))


def _result_columns(result):
    if isinstance(result, dict) and "columns" in result:
        return result["columns"]
    return result


def _result_metadata(result) -> dict:
    if isinstance(result, dict) and isinstance(result.get("metadata"), dict):
        return dict(result["metadata"])
    return {}


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
    parser = argparse.ArgumentParser(description="Goal1869 v2.0 road-hazard partner priority timing row.")
    parser.add_argument("--count", type=int, default=512)
    parser.add_argument("--threshold", type=int, default=2)
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
    roads, hazards, expected_counts = _build_records(args.count)
    expected_rows = tuple({"segment_id": road.id, "hit_count": count} for road, count in zip(roads, expected_counts))
    expected_counts_canonical = _canonical_counts(expected_rows)
    expected_flags = _flags_from_counts(expected_rows, args.threshold)
    output_capacity = max(1, len(roads) * len(hazards))
    print(
        f"[setup] count={args.count} hazards={len(hazards)} threshold={args.threshold} output_capacity={output_capacity}",
        flush=True,
    )

    v18_one_shot_samples, v18_rows = _time_call(
        "v1_8_one_shot_native_optix_road_hazard_rows",
        args.iterations,
        lambda: rt.run_optix(road_hazard_hitcount, roads=roads, hazards=hazards),
    )
    if _canonical_counts(v18_rows) != expected_counts_canonical:
        raise RuntimeError("v1.8 one-shot road-hazard rows did not match expected counts")
    prepared = rt.prepare_optix_segment_polygon_hitcount_2d(hazards)
    try:
        v18_prepared_samples, v18_prepared_rows = _time_call(
            "v1_8_prepared_native_optix_road_hazard_rows",
            args.iterations,
            lambda: prepared.run(roads),
        )
    finally:
        prepared.close()
    if _canonical_counts(v18_prepared_rows) != expected_counts_canonical:
        raise RuntimeError("v1.8 prepared road-hazard rows did not match expected counts")

    partner_results = {}
    for partner in partners:
        print(f"[setup] building caller-owned {partner} columns", flush=True)
        ray_columns, triangle_columns, triangle_aabbs, runtime, build_s = _build_partner_columns(roads, hazards, partner)
        samples, result = _time_call(
            f"v2_0_partner_road_hazard_priority_flags_{partner}",
            args.iterations,
            lambda: rt.road_hazard_priority_flags_optix_partner_device_columns(
                ray_columns,
                triangle_columns,
                triangle_aabbs,
                threshold=args.threshold,
                partner=partner,
                output_capacity=output_capacity,
                return_metadata=True,
            ),
        )
        flags = _columns_to_flags(_result_columns(result), runtime)
        if flags != expected_flags:
            raise RuntimeError(f"v2.0 partner priority flags did not match expected flags for {partner}")
        print(f"[setup] preparing reusable {partner} triangle scene and witness outputs", flush=True)
        prepared_partner_scene = rt.prepare_segment_polygon_anyhit_optix_partner_device_scene(
            triangle_columns,
            triangle_aabbs,
        )
        witness_output_columns = rt.allocate_segment_polygon_witness_partner_device_output_columns(
            output_capacity,
            partner=partner,
        )
        try:
            prepared_samples, prepared_result = _time_call(
                f"v2_0_prepared_partner_road_hazard_priority_flags_{partner}",
                args.iterations,
                lambda: rt.road_hazard_priority_flags_optix_prepared_partner_device_columns(
                    prepared_partner_scene,
                    ray_columns,
                    threshold=args.threshold,
                    partner=partner,
                    output_capacity=output_capacity,
                    witness_output_columns=witness_output_columns,
                    return_metadata=True,
                ),
            )
        finally:
            prepared_partner_scene.close()
        prepared_flags = _columns_to_flags(_result_columns(prepared_result), runtime)
        if prepared_flags != expected_flags:
            raise RuntimeError(f"v2.0 prepared partner priority flags did not match expected flags for {partner}")
        metadata = _result_metadata(result)
        prepared_metadata = _result_metadata(prepared_result)
        partner_results[partner] = {
            "column_build_s": build_s,
            "query_samples_s": samples,
            "query_summary": _summary(samples),
            "query_median_ratio_vs_v1_8_one_shot_native": statistics.median(samples) / statistics.median(v18_one_shot_samples),
            "query_median_ratio_vs_v1_8_prepared_native": statistics.median(samples) / statistics.median(v18_prepared_samples),
            "row_count": len(flags),
            "output_contract": "partner_owned_road_hazard_priority_columns",
            "metadata": {
                "native_engine_row_contract": metadata.get("native_engine_row_contract"),
                "app_exact_filter": metadata.get("app_exact_filter"),
                "app_exact_filter_device_materialization": metadata.get("app_exact_filter_device_materialization"),
                "app_count_materialization": metadata.get("app_count_materialization"),
                "whole_app_true_zero_copy_authorized": metadata.get("whole_app_true_zero_copy_authorized"),
            },
            "goal1889_prepared_reuse": {
                "query_samples_s": prepared_samples,
                "query_summary": _summary(prepared_samples),
                "query_median_ratio_vs_v1_8_one_shot_native": statistics.median(prepared_samples)
                / statistics.median(v18_one_shot_samples),
                "query_median_ratio_vs_v1_8_prepared_native": statistics.median(prepared_samples)
                / statistics.median(v18_prepared_samples),
                "query_median_ratio_vs_goal1869_unprepared_partner": statistics.median(prepared_samples)
                / statistics.median(samples),
                "row_count": len(prepared_flags),
                "output_contract": "prepared_partner_owned_road_hazard_priority_columns",
                "prepared_scene_reused": True,
                "witness_output_columns_reused": True,
                "metadata": {
                    "native_engine_row_contract": prepared_metadata.get("native_engine_row_contract"),
                    "app_exact_filter": prepared_metadata.get("app_exact_filter"),
                    "app_exact_filter_device_materialization": prepared_metadata.get("app_exact_filter_device_materialization"),
                    "app_count_materialization": prepared_metadata.get("app_count_materialization"),
                    "whole_app_true_zero_copy_authorized": prepared_metadata.get("whole_app_true_zero_copy_authorized"),
                },
            },
        }

    payload = {
        "status": "pass",
        "goal": "Goal1869",
        "goal_extension": "Goal1889",
        "git_commit": _git_commit(),
        "source_commit_label": os.environ.get("RTDL_SOURCE_COMMIT_LABEL", ""),
        "gpu": _gpu_name(),
        "count": args.count,
        "threshold": args.threshold,
        "iterations": args.iterations,
        "output_capacity": output_capacity,
        "baseline": {
            "name": "v1_8_one_shot_native_optix_road_hazard_rows",
            "query_samples_s": v18_one_shot_samples,
            "query_summary": _summary(v18_one_shot_samples),
            "row_count": len(v18_rows),
        },
        "prepared_baseline": {
            "name": "v1_8_prepared_native_optix_road_hazard_rows",
            "query_samples_s": v18_prepared_samples,
            "query_summary": _summary(v18_prepared_samples),
            "row_count": len(v18_prepared_rows),
        },
        "partners": partner_results,
        "parity": {
            "expected_row_count": len(expected_rows),
            "strict_priority_flags_match": True,
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
