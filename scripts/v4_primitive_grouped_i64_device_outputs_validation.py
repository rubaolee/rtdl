#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


DEFAULT_RAY_COUNTS = (8192, 32768)
DEFAULT_GROUP_WIDTH = 16


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _require_torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch with CUDA is required for this V4 candidate gate") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is not available")
    return torch


def _u32_range(torch, count: int, *, device):
    return torch.arange(count, dtype=torch.int64, device=device).to(torch.uint32).contiguous()


def _make_fixture(torch, *, ray_count: int, group_width: int, device) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    if group_width <= 0:
        raise ValueError("group_width must be positive")
    if ray_count % group_width != 0:
        raise ValueError("ray_count must be divisible by group_width")

    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    coords = ids_i64.to(torch.float64)
    x = ((coords % 256) * 2.0).contiguous()
    y = (torch.div(coords, 256, rounding_mode="floor") * 2.0).contiguous()
    z0 = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.40, dtype=torch.float64, device=device)
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)

    triangle_columns = {
        "ids": ids,
        "x0": (x - half).contiguous(),
        "y0": (y - half).contiguous(),
        "z0": z0.contiguous(),
        "x1": (x + half).contiguous(),
        "y1": (y - half).contiguous(),
        "z1": z0.contiguous(),
        "x2": x.contiguous(),
        "y2": (y + half).contiguous(),
        "z2": z0.contiguous(),
    }
    ray_columns = {
        "ids": ids,
        "ox": x.contiguous(),
        "oy": y.contiguous(),
        "oz": zero.contiguous(),
        "dx": zero.contiguous(),
        "dy": zero.contiguous(),
        "dz": one.contiguous(),
        "tmax": torch.full((ray_count,), 10.0, dtype=torch.float64, device=device),
    }
    group_count = ray_count // group_width
    primitive_group_ids = (np.arange(ray_count, dtype=np.uint32) // np.uint32(group_width)).astype(np.uint32)
    primitive_values = (np.arange(ray_count, dtype=np.uint64) + np.uint64(1)).astype(np.uint64)
    group_ids = np.arange(group_count, dtype=np.uint64)
    first = group_ids * np.uint64(group_width) + np.uint64(1)
    last = first + np.uint64(group_width - 1)
    expected = {
        "counts": np.full((group_count,), group_width, dtype=np.uint64),
        "sums": ((first + last) * np.uint64(group_width) // np.uint64(2)).astype(np.uint64),
        "mins": first.astype(np.uint64),
        "maxs": last.astype(np.uint64),
    }
    return {
        "triangle_columns": triangle_columns,
        "ray_columns": ray_columns,
        "primitive_group_ids": primitive_group_ids,
        "primitive_values": primitive_values,
        "group_count": group_count,
        "expected": expected,
    }


def _measure(callable_obj, *, torch, repeat: int, warmup: int, progress: bool, label: str) -> dict[str, Any]:
    for index in range(warmup):
        _progress(progress, f"[warmup] {label} {index + 1}/{warmup}")
        callable_obj()
        torch.cuda.synchronize()

    timings: list[float] = []
    payload = None
    for index in range(repeat):
        _progress(progress, f"[repeat-start] {label} {index + 1}/{repeat}")
        start = time.perf_counter()
        payload = callable_obj()
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        _progress(progress, f"[repeat-done] {label} {index + 1}/{repeat} elapsed_s={elapsed:.6f}")
    return {
        "timings_s": timings,
        "median_s": _median(timings),
        "min_s": min(timings) if timings else 0.0,
        "max_s": max(timings) if timings else 0.0,
        "payload": payload,
    }


def _rows_to_arrays(rows: tuple[dict[str, int], ...], *, group_count: int, reduction: str) -> dict[str, np.ndarray]:
    counts = np.zeros((group_count,), dtype=np.uint64)
    sums = np.zeros((group_count,), dtype=np.uint64)
    mins = np.full((group_count,), np.iinfo(np.uint64).max, dtype=np.uint64)
    maxs = np.zeros((group_count,), dtype=np.uint64)
    for row in rows:
        group_id = int(row["group_id"])
        if reduction == "sum_count":
            counts[group_id] = np.uint64(row["count"])
            sums[group_id] = np.uint64(row["sum"])
        elif reduction == "min":
            mins[group_id] = np.uint64(row["min"])
        elif reduction == "max":
            maxs[group_id] = np.uint64(row["max"])
        else:
            raise ValueError(f"unsupported reduction: {reduction}")
    return {"counts": counts, "sums": sums, "mins": mins, "maxs": maxs}


def _device_outputs_to_arrays(outputs: dict[str, object]) -> dict[str, np.ndarray]:
    return {
        "counts": outputs["group_counts"].detach().cpu().numpy().astype(np.uint64, copy=False),
        "sums": outputs["group_sums"].detach().cpu().numpy().astype(np.uint64, copy=False),
        "mins": outputs["group_mins"].detach().cpu().numpy().astype(np.uint64, copy=False),
        "maxs": outputs["group_maxs"].detach().cpu().numpy().astype(np.uint64, copy=False),
    }


def _compact_legacy_payload(payload: dict[str, object]) -> dict[str, object]:
    rows = tuple(payload.get("rows", ()))
    return {
        key: value
        for key, value in payload.items()
        if key != "rows"
    } | {
        "row_count": len(rows),
        "row_sample": rows[:8],
    }


def _array_match(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.array_equal(a, b))


def _check_parity(
    *,
    old_rows: tuple[dict[str, int], ...],
    outputs: dict[str, object],
    expected: dict[str, np.ndarray],
    group_count: int,
    reduction: str,
) -> dict[str, object]:
    host_arrays = _rows_to_arrays(old_rows, group_count=group_count, reduction=reduction)
    device_arrays = _device_outputs_to_arrays(outputs)
    if reduction == "sum_count":
        fields = ("counts", "sums")
    elif reduction == "min":
        fields = ("mins",)
    elif reduction == "max":
        fields = ("maxs",)
    else:
        raise ValueError(f"unsupported reduction: {reduction}")

    field_results = {}
    mismatch_samples = {}
    for field in fields:
        host_match = _array_match(device_arrays[field], host_arrays[field])
        analytic_match = _array_match(device_arrays[field], expected[field])
        field_results[field] = {
            "device_matches_legacy_host_output": host_match,
            "device_matches_analytic_fixture": analytic_match,
        }
        if not (host_match and analytic_match):
            mismatch_indices = np.nonzero(device_arrays[field] != expected[field])[0][:8]
            mismatch_samples[field] = [
                {
                    "group_id": int(index),
                    "device": int(device_arrays[field][index]),
                    "expected": int(expected[field][index]),
                    "legacy_host": int(host_arrays[field][index]),
                }
                for index in mismatch_indices
            ]
    parity = all(
        item["device_matches_legacy_host_output"] and item["device_matches_analytic_fixture"]
        for item in field_results.values()
    )
    return {
        "parity_passed": bool(parity),
        "fields": field_results,
        "mismatch_samples": mismatch_samples,
    }


def _measure_size(
    ray_count: int,
    *,
    group_width: int,
    repeat: int,
    warmup: int,
    progress: bool,
) -> dict[str, Any]:
    import rtdsl.v4_ray_triangle as rt_v4

    torch = _require_torch()
    device = torch.device("cuda:0")
    fixture = _make_fixture(torch, ray_count=ray_count, group_width=group_width, device=device)
    torch.cuda.synchronize()

    prepare_start = time.perf_counter()
    with rt_v4.prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(
        fixture["triangle_columns"],
        fixture["ray_columns"],
        primitive_group_ids=fixture["primitive_group_ids"],
        primitive_values=fixture["primitive_values"],
        group_count=fixture["group_count"],
        partner="torch",
    ) as session:
        prepare_seconds = time.perf_counter() - prepare_start
        output_columns = session.allocate_outputs()

        def run_device_frontdoor() -> dict[str, object]:
            return session.run(reduction="sum_count", output_columns=output_columns, return_metadata=True)

        def run_legacy_host_output() -> dict[str, object]:
            return session.prepared_scene.ray_batch_prepared_primitive_grouped_i64_reduction(
                session.ray_batch,
                session.primitive_payload,
                reduction="sum_count",
            )

        device_frontdoor = _measure(
            run_device_frontdoor,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=device_output",
        )
        legacy_host_output = _measure(
            run_legacy_host_output,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=legacy_host_output",
        )

        parity_by_reduction = {}
        for reduction in ("sum_count", "min", "max"):
            old = session.prepared_scene.ray_batch_prepared_primitive_grouped_i64_reduction(
                session.ray_batch,
                session.primitive_payload,
                reduction=reduction,
            )
            outputs = session.allocate_outputs()
            new = session.run(reduction=reduction, output_columns=outputs, return_metadata=True)
            torch.cuda.synchronize()
            parity_by_reduction[reduction] = {
                **_check_parity(
                    old_rows=tuple(old["rows"]),
                    outputs=outputs,
                    expected=fixture["expected"],
                    group_count=int(fixture["group_count"]),
                    reduction=reduction,
                ),
                "legacy_hit_event_count_before_dedup": int(old["hit_event_count_before_dedup"]),
                "device_hit_event_count_before_dedup": int(new["metadata"]["hit_event_count_before_dedup"]),
                "metadata": dict(new["metadata"]),
            }

    device_payload = device_frontdoor.pop("payload") or {}
    legacy_payload = legacy_host_output.pop("payload") or {}
    device_median = float(device_frontdoor["median_s"])
    legacy_median = float(legacy_host_output["median_s"])
    ratio = legacy_median / device_median if device_median > 0.0 else None
    return {
        "ray_count": int(ray_count),
        "triangle_count": int(ray_count),
        "group_count": int(fixture["group_count"]),
        "group_width": int(group_width),
        "prepare_seconds": float(prepare_seconds),
        "parity_passed": all(item["parity_passed"] for item in parity_by_reduction.values()),
        "parity_by_reduction": parity_by_reduction,
        "routes": {
            "device_output_frontdoor": {
                **device_frontdoor,
                "tier": "tier2_generic_fused_rt_primitive_device_array_frontdoor_candidate",
                "generic_primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
                "input_contract": "caller_supplied_torch_device_triangle_and_ray_columns_prepared_primitive_payload",
                "output_contract": "caller_owned_torch_device_grouped_i64_columns",
                "host_materialization_in_hot_path": False,
                "group_rows_downloaded_to_host_in_hot_path": False,
                "metadata": dict(device_payload.get("metadata", {})),
            },
            "legacy_host_output": {
                **legacy_host_output,
                "tier": "prepared_native_route_with_host_grouped_result_output",
                "generic_primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
                "host_materialization_in_hot_path": True,
                "metadata": _compact_legacy_payload(dict(legacy_payload)),
            },
        },
        "comparison": {
            "legacy_host_output_over_device_output_median_speedup": ratio,
            "speedup_claim_authorized": False,
            "interpretation": (
                "candidate gate only; this same-contract comparison does not authorize "
                "V4 public performance claims, whole-app claims, or release promotion"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the V4 primitive grouped-i64 direct device-output measured surface."
    )
    parser.add_argument("--ray-counts", default=",".join(str(item) for item in DEFAULT_RAY_COUNTS))
    parser.add_argument("--group-width", type=int, default=DEFAULT_GROUP_WIDTH)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()

    torch = _require_torch()
    counts = tuple(int(item) for item in str(args.ray_counts).split(",") if item.strip())
    if not counts:
        raise ValueError("--ray-counts must contain at least one positive integer")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results = [
        _measure_size(
            count,
            group_width=int(args.group_width),
            repeat=int(args.repeat),
            warmup=int(args.warmup),
            progress=bool(args.progress),
        )
        for count in counts
    ]
    payload = {
        "gate": "v4_primitive_grouped_i64_device_outputs_measured_gate",
        "surface": "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        "surface_status": "measured_on_v4_goal4617_pod_optix8",
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_partner_scope": "torch 2.8.0+cu128",
        "optix_9_1_validated": False,
        "started_utc": started,
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": {
            "hostname": platform.node(),
            "python": sys.version,
            "torch": getattr(torch, "__version__", "unknown"),
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
        "parameters": {
            "ray_counts": counts,
            "group_width": int(args.group_width),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
        },
        "results": results,
        "passed": all(item["parity_passed"] for item in results),
        "authorization": {
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "rt_core_pod_performance_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
