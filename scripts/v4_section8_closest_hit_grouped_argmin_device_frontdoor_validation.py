#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


DEFAULT_RAY_COUNTS = (8192, 32768, 131072)
DEFAULT_GROUP_WIDTH = 8


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _require_torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch with CUDA is required for this measured V4 surface") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is not available")
    return torch


def _u32_range(torch, count: int, *, device):
    return torch.arange(count, dtype=torch.int64, device=device).to(torch.uint32)


def _make_fixture(torch, *, ray_count: int, group_width: int, device) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    if group_width <= 0:
        raise ValueError("group_width must be positive")
    if ray_count % group_width != 0:
        raise ValueError("ray_count must be divisible by group_width")

    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    centers = ids_i64.to(torch.float64) * 2.0
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    minus_one = -one
    half = torch.full((ray_count,), 0.45, dtype=torch.float64, device=device)

    triangle_columns = {
        "ids": ids,
        "x0": (centers - half).contiguous(),
        "y0": (-half).contiguous(),
        "z0": zero.contiguous(),
        "x1": (centers + half).contiguous(),
        "y1": (-half).contiguous(),
        "z1": zero.contiguous(),
        "x2": centers.contiguous(),
        "y2": half.contiguous(),
        "z2": zero.contiguous(),
    }
    ray_columns = {
        "ids": ids,
        "ox": centers.contiguous(),
        "oy": zero.contiguous(),
        "oz": one.contiguous(),
        "dx": zero.contiguous(),
        "dy": zero.contiguous(),
        "dz": minus_one.contiguous(),
        "tmax": torch.full((ray_count,), 2.0, dtype=torch.float64, device=device),
    }
    local = ids_i64 % int(group_width)
    per_ray_group_ids = (ids_i64 // int(group_width)).to(torch.uint32).contiguous()
    candidate_values = (int(group_width) - local).to(torch.float64).contiguous()
    candidate_indices = (ids_i64 + 1000000).to(torch.uint32).contiguous()
    group_count = ray_count // int(group_width)
    expected_group_i64 = torch.arange(group_count, dtype=torch.int64, device=device)
    expected_index = (expected_group_i64 * int(group_width) + int(group_width) - 1 + 1000000).to(torch.int64)
    expected_value = torch.ones((group_count,), dtype=torch.float64, device=device)
    expected_has_value = torch.ones((group_count,), dtype=torch.uint8, device=device)
    return {
        "triangle_columns": triangle_columns,
        "ray_columns": ray_columns,
        "per_ray_group_ids": per_ray_group_ids,
        "candidate_values": candidate_values,
        "candidate_indices": candidate_indices,
        "group_count": group_count,
        "expected": {
            "group_has_value": expected_has_value,
            "group_index_i64": expected_index,
            "group_value": expected_value,
        },
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
        "min_s": min(timings),
        "max_s": max(timings),
        "payload": payload,
    }


def _check_correctness(torch, outputs: dict[str, object], expected: dict[str, object]) -> dict[str, object]:
    has_value = outputs["group_has_value"]
    group_index = outputs["group_index"]
    group_value = outputs["group_value"]
    has_match = bool(torch.equal(has_value, expected["group_has_value"]))
    index_match = bool(torch.equal(group_index.to(torch.int64), expected["group_index_i64"]))
    value_match = bool(torch.allclose(group_value, expected["group_value"], rtol=0.0, atol=0.0))
    mismatch_count = int(torch.count_nonzero(group_index.to(torch.int64) != expected["group_index_i64"]).detach().cpu().item())
    return {
        "correctness_passed": has_match and index_match and value_match,
        "has_value_match": has_match,
        "index_match": index_match,
        "value_match": value_match,
        "index_mismatch_count": mismatch_count,
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
    with rt_v4.prepare_closest_hit_grouped_argmin_3d_device_arrays_v4(
        fixture["triangle_columns"],
        fixture["ray_columns"],
        per_ray_group_ids=fixture["per_ray_group_ids"],
        candidate_values=fixture["candidate_values"],
        candidate_indices=fixture["candidate_indices"],
        group_count=fixture["group_count"],
        partner="torch",
    ) as session:
        prepare_seconds = time.perf_counter() - prepare_start
        output_columns = session.allocate_outputs()

        def run_device_frontdoor() -> dict[str, object]:
            return session.run(output_columns=output_columns, return_metadata=True)

        def run_legacy_host_materialize() -> dict[str, object]:
            native_result = session.prepared_scene.ray_closest_hit_prepared_grouped_argmin_device(
                session.ray_batch,
                session.grouped_inputs,
            )
            materialized = session.grouped_inputs.materialize_grouped_results()
            return {"native_result": native_result, "materialized": materialized}

        device_frontdoor = _measure(
            run_device_frontdoor,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=device_array_frontdoor",
        )
        legacy_host_materialize = _measure(
            run_legacy_host_materialize,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=legacy_host_materialize",
        )

    device_payload = device_frontdoor.pop("payload") or {}
    legacy_payload = legacy_host_materialize.pop("payload") or {}
    correctness = _check_correctness(torch, output_columns, fixture["expected"])
    device_median = float(device_frontdoor["median_s"])
    legacy_median = float(legacy_host_materialize["median_s"])
    ratio = legacy_median / device_median if device_median > 0.0 else None
    return {
        "ray_count": int(ray_count),
        "triangle_count": int(ray_count),
        "group_count": int(fixture["group_count"]),
        "group_width": int(group_width),
        "correctness": correctness,
        "correctness_passed": bool(correctness["correctness_passed"]),
        "prepare_seconds": float(prepare_seconds),
        "routes": {
            "device_array_frontdoor": {
                **device_frontdoor,
                "tier": "tier2_generic_fused_rt_primitive_device_array_frontdoor",
                "generic_primitive": "CLOSEST_HIT_GROUPED_ARGMIN_3D",
                "input_contract": "caller_supplied_torch_device_triangle_ray_and_group_columns",
                "output_contract": "caller_owned_torch_device_grouped_argmin_columns",
                "host_materialization_in_hot_path": False,
                "grouped_results_downloaded_to_host_in_hot_path": False,
                "metadata": dict(device_payload.get("metadata", {})),
            },
            "legacy_host_materialize": {
                **legacy_host_materialize,
                "tier": "prepared_native_route_with_host_grouped_result_materialization",
                "generic_primitive": "CLOSEST_HIT_GROUPED_ARGMIN_3D",
                "host_materialization_in_hot_path": True,
                "metadata": dict((legacy_payload.get("native_result") or {}).get("metadata", {})),
                "materialize_metadata": dict((legacy_payload.get("materialized") or {}).get("metadata", {})),
            },
        },
        "comparison": {
            "legacy_host_materialize_to_device_frontdoor_ratio": ratio,
            "device_frontdoor_faster_than_host_materialize": bool(ratio is not None and ratio > 1.0),
            "claim_scope": (
                "This is a second V4 Tier-2 device-array surface validation, not a broad V4 "
                "speedup or release claim."
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 closest-hit grouped-argmin device-array front-door validation harness."
    )
    parser.add_argument("--ray-count", type=int, action="append", default=[])
    parser.add_argument("--group-width", type=int, default=DEFAULT_GROUP_WIDTH)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ray_counts = tuple(args.ray_count) if args.ray_count else DEFAULT_RAY_COUNTS
    if args.repeat <= 0:
        raise SystemExit("--repeat must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup must be non-negative")
    if args.group_width <= 0:
        raise SystemExit("--group-width must be positive")
    if any(int(count) <= 0 for count in ray_counts):
        raise SystemExit("all --ray-count values must be positive")
    if any(int(count) % int(args.group_width) != 0 for count in ray_counts):
        raise SystemExit("all --ray-count values must be divisible by --group-width")

    payload: dict[str, Any] = {
        "schema": "rtdl.v4.section8.closest_hit_grouped_argmin_device_frontdoor.v1",
        "status": "dry_run" if args.dry_run else "measured",
        "parameters": {
            "ray_counts": tuple(int(count) for count in ray_counts),
            "group_width": int(args.group_width),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "partner": "torch",
        },
        "claim_boundary": {
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "measured_surface": "v4_closest_hit_grouped_argmin_3d_device_arrays",
        },
        "timing_boundary": (
            "fixture construction and prepare excluded; hot route includes prepared native "
            "closest-hit grouped argmin plus either device-to-device output export or host "
            "grouped result materialization; correctness host reads are outside timed repeats"
        ),
    }
    if args.dry_run:
        payload["results"] = []
    else:
        results = [
            _measure_size(
                int(ray_count),
                group_width=int(args.group_width),
                repeat=int(args.repeat),
                warmup=int(args.warmup),
                progress=bool(args.progress),
            )
            for ray_count in ray_counts
        ]
        payload["results"] = results
        payload["summary"] = {
            "all_correct": all(bool(result["correctness_passed"]) for result in results),
            "measured_ray_count_count": len(results),
            "device_frontdoor_wins_host_materialize_count": sum(
                1
                for result in results
                if bool(result["comparison"]["device_frontdoor_faster_than_host_materialize"])
            ),
            "median_host_materialize_to_device_frontdoor_ratio": _median(
                [
                    float(result["comparison"]["legacy_host_materialize_to_device_frontdoor_ratio"])
                    for result in results
                    if result["comparison"]["legacy_host_materialize_to_device_frontdoor_ratio"] is not None
                ]
            ),
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
