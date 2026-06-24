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


def _make_fixture(torch, *, ray_count: int, device) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")
    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    centers = ids_i64.to(torch.float64) * 2.0
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.45, dtype=torch.float64, device=device)

    triangle_columns = {
        "ids": ids,
        "x0": (centers - half).contiguous(),
        "y0": (-half).contiguous(),
        "x1": (centers + half).contiguous(),
        "y1": (-half).contiguous(),
        "x2": centers.contiguous(),
        "y2": half.contiguous(),
    }
    triangle_aabbs = torch.stack(
        (
            triangle_columns["x0"],
            triangle_columns["y0"],
            torch.full((ray_count,), -1.0e-4, dtype=torch.float32, device=device),
            triangle_columns["x1"],
            triangle_columns["y2"],
            torch.full((ray_count,), 1.0e-4, dtype=torch.float32, device=device),
        ),
        dim=1,
    ).to(torch.float32).contiguous()
    ray_columns = {
        "ids": ids,
        "ox": centers.contiguous(),
        "oy": (-one).contiguous(),
        "dx": zero.contiguous(),
        "dy": one.contiguous(),
        "tmax": torch.full((ray_count,), 2.0, dtype=torch.float64, device=device),
    }
    return {
        "triangle_columns": triangle_columns,
        "triangle_aabbs": triangle_aabbs,
        "ray_columns": ray_columns,
        "expected_flags": torch.ones((ray_count,), dtype=torch.uint32, device=device),
    }


def _fixture_analytic_torch_reference(torch, fixture: dict[str, object]):
    rays = fixture["ray_columns"]
    triangles = fixture["triangle_columns"]
    ox = rays["ox"].reshape(-1, 1)
    x0 = triangles["x0"].reshape(1, -1)
    x1 = triangles["x1"].reshape(1, -1)
    hits_x = (x0 <= ox) & (ox <= x1)
    flags = torch.any(hits_x, dim=1).to(torch.uint32)
    return flags


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


def _measure_size(
    ray_count: int,
    *,
    repeat: int,
    warmup: int,
    max_torch_reference_count: int,
    progress: bool,
) -> dict[str, Any]:
    import rtdsl.v4_ray_triangle as rt_v4

    torch = _require_torch()
    device = torch.device("cuda:0")
    fixture = _make_fixture(torch, ray_count=ray_count, device=device)
    torch.cuda.synchronize()

    prepare_start = time.perf_counter()
    with rt_v4.prepare_ray_triangle_any_hit_flags_2d_device_arrays_v4(
        fixture["triangle_columns"],
        fixture["triangle_aabbs"],
        partner="torch",
    ) as session:
        prepare_seconds = time.perf_counter() - prepare_start
        output_flags = session.allocate_outputs(ray_count, device=device)

        def run_device_frontdoor() -> dict[str, object]:
            return session.run(fixture["ray_columns"], output_flags=output_flags, return_metadata=True)

        device_frontdoor = _measure(
            run_device_frontdoor,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=device_any_hit_flags",
        )

    device_payload = device_frontdoor.pop("payload") or {}
    correctness_passed = bool(torch.equal(output_flags, fixture["expected_flags"]))
    reference_payload = None
    comparison: dict[str, object] = {
        "torch_reference_measured": False,
        "torch_reference_reason": "skipped_above_max_torch_reference_count",
        "torch_reference_to_device_frontdoor_ratio": None,
        "device_frontdoor_faster_than_torch_reference": None,
    }
    if ray_count <= max_torch_reference_count:
        def run_reference():
            return _fixture_analytic_torch_reference(torch, fixture)

        reference_payload = _measure(
            run_reference,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=torch_fixture_analytic_reference",
        )
        ref_flags = reference_payload.pop("payload")
        reference_match = bool(torch.equal(ref_flags, fixture["expected_flags"]))
        correctness_passed = correctness_passed and reference_match
        device_median = float(device_frontdoor["median_s"])
        reference_median = float(reference_payload["median_s"])
        ratio = reference_median / device_median if device_median > 0.0 else None
        comparison = {
            "torch_reference_measured": True,
            "torch_reference_reason": None,
            "torch_reference_to_device_frontdoor_ratio": ratio,
            "device_frontdoor_faster_than_torch_reference": bool(ratio is not None and ratio > 1.0),
            "torch_reference_contract": (
                "fixture-analytic same-data device reference for separated one-hit triangles; "
                "not a general ray/triangle implementation or handwritten OptiX ceiling"
            ),
            "torch_reference_match": reference_match,
        }

    return {
        "ray_count": int(ray_count),
        "triangle_count": int(ray_count),
        "correctness_passed": correctness_passed,
        "prepare_seconds": float(prepare_seconds),
        "routes": {
            "device_array_frontdoor": {
                **device_frontdoor,
                "tier": "tier2_generic_fused_rt_primitive_device_array_frontdoor",
                "generic_primitive": "RAY_TRIANGLE_ANY_HIT_FLAGS_2D",
                "input_contract": "caller_supplied_torch_device_triangle_aabb_and_ray_columns",
                "output_contract": "caller_owned_torch_device_any_hit_flag_column",
                "host_materialization_in_hot_path": False,
                "metadata": dict(device_payload.get("metadata", {})),
            },
            "torch_fixture_analytic_reference": reference_payload,
        },
        "comparison": {
            **comparison,
            "claim_scope": (
                "This is a third V4 Tier-2 device-array surface validation, not a broad V4 "
                "speedup, whole-app result, or release claim."
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 ray/triangle any-hit flag device-array front-door validation harness."
    )
    parser.add_argument("--ray-count", type=int, action="append", default=[])
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--max-torch-reference-count", type=int, default=8192)
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
    if args.max_torch_reference_count < 0:
        raise SystemExit("--max-torch-reference-count must be non-negative")
    if any(int(count) <= 0 for count in ray_counts):
        raise SystemExit("all --ray-count values must be positive")

    payload: dict[str, Any] = {
        "schema": "rtdl.v4.section8.ray_triangle_any_hit_flags_device_frontdoor.v1",
        "status": "dry_run" if args.dry_run else "measured",
        "parameters": {
            "ray_counts": tuple(int(count) for count in ray_counts),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "max_torch_reference_count": int(args.max_torch_reference_count),
            "partner": "torch",
        },
        "claim_boundary": {
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "measured_surface": "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        },
        "timing_boundary": (
            "fixture construction and prepare excluded; hot route includes prepared native any-hit "
            "flag output into caller-owned device columns; correctness host reads are outside timed repeats"
        ),
    }
    if args.dry_run:
        payload["results"] = []
    else:
        results = [
            _measure_size(
                int(ray_count),
                repeat=int(args.repeat),
                warmup=int(args.warmup),
                max_torch_reference_count=int(args.max_torch_reference_count),
                progress=bool(args.progress),
            )
            for ray_count in ray_counts
        ]
        ratios = [
            float(result["comparison"]["torch_reference_to_device_frontdoor_ratio"])
            for result in results
            if result["comparison"]["torch_reference_to_device_frontdoor_ratio"] is not None
        ]
        payload["results"] = results
        payload["summary"] = {
            "all_correct": all(bool(result["correctness_passed"]) for result in results),
            "measured_ray_count_count": len(results),
            "torch_reference_measured_count": sum(
                1 for result in results if bool(result["comparison"]["torch_reference_measured"])
            ),
            "median_torch_reference_to_device_frontdoor_ratio": _median(ratios),
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
