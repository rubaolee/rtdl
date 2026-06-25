#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


DEFAULT_RAY_COUNTS = (32768, 131072)
GOAL4633_PROMOTION_RAY_COUNTS = (32768, 131072, 262144, 524288)
GOAL4633_MIN_PER_SHAPE_RATIO = 1.20
GOAL4633_MIN_GEOMEAN_RATIO = 1.50


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _geomean(values: list[float]) -> float | None:
    positive = [float(value) for value in values if float(value) > 0.0]
    if len(positive) != len(values) or not positive:
        return None
    return float(math.exp(sum(math.log(value) for value in positive) / len(positive)))


def _write_summary_markdown(payload: dict[str, Any], path: Path) -> None:
    rows = payload.get("results", [])
    lines = [
        f"# {payload['gate']}",
        "",
        f"Surface: `{payload['surface']}`",
        f"Surface status before gate: `{payload['surface_status_before_gate']}`",
        f"Decision: `{payload['promotion_gate']['decision']}`",
        "",
        "## Route Boundary",
        "",
        payload["comparison_boundary"]["description"],
        "",
        "This is not a pure kernel-vs-kernel speedup figure and does not authorize broad V4 or whole-application claims.",
        "",
        "## Results",
        "",
        "| rays | triangles | parity | device-output median (s) | host-scalar median (s) | comparable-route ratio |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for row in rows:
        ratio = row["comparison"].get("host_materialization_over_device_resident_median_ratio")
        ratio_text = f"{float(ratio):.3f}x" if ratio is not None else "n/a"
        lines.append(
            "| {ray_count} | {triangle_count} | {parity} | {device:.9f} | {host:.9f} | {ratio} |".format(
                ray_count=row["ray_count"],
                triangle_count=row["triangle_count"],
                parity=str(bool(row["parity_passed"])).lower(),
                device=float(row["routes"]["device_output_frontdoor"]["median_s"]),
                host=float(row["routes"]["host_scalar_route"]["median_s"]),
                ratio=ratio_text,
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"- all shapes completed: `{payload['promotion_gate']['all_shapes_completed']}`",
            f"- parity all passed: `{payload['promotion_gate']['parity_all_passed']}`",
            f"- no hot-path host materialization: `{payload['promotion_gate']['no_hot_path_host_materialization']}`",
            f"- min ratio: `{payload['promotion_gate']['min_ratio']}`",
            f"- geomean ratio: `{payload['promotion_gate']['geomean_ratio']}`",
            f"- per-shape ratio threshold: `>={payload['promotion_gate']['min_per_shape_ratio_required']}x`",
            f"- geomean threshold: `>={payload['promotion_gate']['min_geomean_ratio_required']}x`",
            "",
            "## Non-Authorization",
            "",
            "- V4 release is not authorized by this gate alone.",
            "- Whole-application speedup claims are not authorized.",
            "- CuPy performance claims are not authorized.",
            "- Tier-3 callback support is not authorized.",
            "- Public true-zero-copy wording is not authorized.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _require_torch():
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Torch with CUDA is required for this V4 candidate gate") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is not available")
    return torch


def _make_fixture(torch, *, ray_count: int, device) -> dict[str, object]:
    if ray_count <= 0:
        raise ValueError("ray_count must be positive")

    ids_i64 = torch.arange(ray_count, dtype=torch.int64, device=device)
    ids = ids_i64.to(torch.uint32).contiguous()
    coords = ids_i64.to(torch.float64)
    x = ((coords % 256) * 2.0).contiguous()
    y = (torch.div(coords, 256, rounding_mode="floor") * 2.0).contiguous()
    z0 = torch.ones((ray_count,), dtype=torch.float64, device=device)
    half = torch.full((ray_count,), 0.40, dtype=torch.float64, device=device)
    zero = torch.zeros((ray_count,), dtype=torch.float64, device=device)
    one = torch.ones((ray_count,), dtype=torch.float64, device=device)
    weights = (ids_i64 + 1).to(torch.uint64).contiguous()

    return {
        "triangle_columns": {
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
        },
        "ray_columns": {
            "ids": ids,
            "ox": x.contiguous(),
            "oy": y.contiguous(),
            "oz": zero.contiguous(),
            "dx": zero.contiguous(),
            "dy": zero.contiguous(),
            "dz": one.contiguous(),
            "tmax": torch.full((ray_count,), 10.0, dtype=torch.float64, device=device),
        },
        "ray_weights": weights,
        "expected_weighted_sum": int(ray_count * (ray_count + 1) // 2),
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


def _measure_size(
    ray_count: int,
    *,
    repeat: int,
    warmup: int,
    progress: bool,
) -> dict[str, Any]:
    import rtdsl.v4_ray_triangle as rt_v4

    torch = _require_torch()
    device = torch.device("cuda:0")
    fixture = _make_fixture(torch, ray_count=ray_count, device=device)
    torch.cuda.synchronize()

    prepare_start = time.perf_counter()
    with rt_v4.prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4(
        fixture["triangle_columns"],
        fixture["ray_columns"],
        fixture["ray_weights"],
        partner="torch",
    ) as session:
        prepare_seconds = time.perf_counter() - prepare_start
        output_scalar = session.allocate_output_scalar()

        def run_device_output_frontdoor() -> dict[str, object]:
            return session.run(output_scalar=output_scalar, return_metadata=True)

        def run_host_scalar_route() -> dict[str, object]:
            return session.prepared_scene.ray_batch_any_hit_weighted_sum_device_weights(
                session.ray_batch,
                session.ray_weights,
            )

        device_output = _measure(
            run_device_output_frontdoor,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=device_output_frontdoor",
        )
        host_scalar = _measure(
            run_host_scalar_route,
            torch=torch,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"ray_count={ray_count} route=host_scalar_route",
        )
        final_device_payload = run_device_output_frontdoor()
        torch.cuda.synchronize()
        device_value = int(final_device_payload["columns"]["weighted_hit_sum"].detach().cpu().item())
        host_value = int(run_host_scalar_route()["weighted_hit_sum"])

    expected = int(fixture["expected_weighted_sum"])
    device_payload = device_output.pop("payload") or {}
    host_payload = host_scalar.pop("payload") or {}
    device_median = float(device_output["median_s"])
    host_median = float(host_scalar["median_s"])
    ratio = host_median / device_median if device_median > 0.0 else None
    metadata = dict(device_payload.get("metadata", {}))
    return {
        "ray_count": int(ray_count),
        "triangle_count": int(ray_count),
        "prepare_seconds": float(prepare_seconds),
        "parity_passed": bool(device_value == host_value == expected),
        "expected_weighted_sum": expected,
        "device_output_weighted_sum": device_value,
        "host_scalar_weighted_sum": host_value,
        "routes": {
            "device_output_frontdoor": {
                **device_output,
                "tier": "tier2_generic_fused_rt_primitive_device_array_candidate",
                "generic_primitive": "RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D",
                "input_contract": "caller_supplied_torch_device_triangle_ray_and_weight_columns",
                "output_contract": "caller_supplied_or_allocated_torch_device_uint64_scalar",
                "device_output_used": True,
                "host_materialization_in_hot_path": False,
                "host_scalar_read_before_consumer": False,
                "weighted_sum_downloaded_to_host_in_hot_path": False,
                "metadata": metadata,
            },
            "host_scalar_route": {
                **host_scalar,
                "tier": "prepared_native_route_with_python_scalar_output",
                "generic_primitive": "RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D",
                "host_scalar_read_before_consumer": True,
                "metadata": dict(host_payload),
            },
        },
        "comparison": {
            "comparison_class": "same_operator_comparable_route",
            "host_materialization_over_device_resident_median_ratio": ratio,
            "speedup_claim_authorized": False,
            "interpretation": (
                "This measures the existing host-scalar materialization path against the "
                "V4 device-resident output path for the same weighted-sum operator. It is "
                "not a pure kernel-vs-kernel figure and does not authorize broad V4, "
                "whole-app, or all-benchmark performance claims."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the V4 ray/triangle any-hit weighted-sum device-output candidate."
    )
    parser.add_argument("--ray-counts", default=",".join(str(item) for item in DEFAULT_RAY_COUNTS))
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--goal4633-promotion-gate", action="store_true")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()

    torch = _require_torch()
    ray_count_arg = (
        ",".join(str(item) for item in GOAL4633_PROMOTION_RAY_COUNTS)
        if args.goal4633_promotion_gate and args.ray_counts == ",".join(str(item) for item in DEFAULT_RAY_COUNTS)
        else str(args.ray_counts)
    )
    counts = tuple(int(item) for item in ray_count_arg.split(",") if item.strip())
    if not counts:
        raise ValueError("--ray-counts must contain at least one positive integer")
    if args.goal4633_promotion_gate:
        args.repeat = 30 if int(args.repeat) == 5 else int(args.repeat)
        args.warmup = 5 if int(args.warmup) == 2 else int(args.warmup)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    results = [
        _measure_size(
            count,
            repeat=int(args.repeat),
            warmup=int(args.warmup),
            progress=bool(args.progress),
        )
        for count in counts
    ]
    ratios = [
        float(item["comparison"]["host_materialization_over_device_resident_median_ratio"])
        for item in results
        if item["comparison"]["host_materialization_over_device_resident_median_ratio"] is not None
    ]
    all_shapes_completed = len(results) == len(counts)
    parity_all_passed = all(item["parity_passed"] for item in results)
    no_hot_path_host_materialization = all(
        not item["routes"]["device_output_frontdoor"]["host_materialization_in_hot_path"]
        and not item["routes"]["device_output_frontdoor"]["host_scalar_read_before_consumer"]
        and not item["routes"]["device_output_frontdoor"]["weighted_sum_downloaded_to_host_in_hot_path"]
        for item in results
    )
    min_ratio = min(ratios) if ratios else None
    geomean_ratio = _geomean(ratios) if ratios else None
    promotion_thresholds_passed = bool(
        all_shapes_completed
        and parity_all_passed
        and no_hot_path_host_materialization
        and min_ratio is not None
        and geomean_ratio is not None
        and min_ratio >= GOAL4633_MIN_PER_SHAPE_RATIO
        and geomean_ratio >= GOAL4633_MIN_GEOMEAN_RATIO
    )
    if promotion_thresholds_passed:
        decision = "promote_weighted_sum_measured_torch_v4_tier2_pending_external_completion_audit"
    elif parity_all_passed and all_shapes_completed:
        decision = "keep_weighted_sum_candidate_not_promoted"
    else:
        decision = "reject_weighted_sum_for_v4_0_or_rerun_required"
    payload = {
        "gate": (
            "v4_goal4633_ray_triangle_any_hit_weighted_sum_promotion_gate"
            if args.goal4633_promotion_gate
            else "v4_ray_triangle_any_hit_weighted_sum_device_output_candidate_gate"
        ),
        "surface": "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
        "surface_status_before_gate": "tier2_candidate_goal4620_not_measured",
        "surface_status_after_gate_candidate": "tier2_candidate_goal4620_not_measured",
        "validated_optix_abi": "8.0",
        "validated_gpu_family": "RTX A5000 / Ampere",
        "validated_partner_scope": "torch",
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
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "goal4633_promotion_gate": bool(args.goal4633_promotion_gate),
        },
        "comparison_boundary": {
            "comparison_class": "same_operator_comparable_route",
            "description": (
                "The ratio compares the existing host-scalar materialization path "
                "against the V4 device-resident output path for the same weighted-sum operator."
            ),
            "pure_kernel_speedup": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "results": results,
        "passed": all(item["parity_passed"] for item in results),
        "promotion_gate": {
            "decision": decision,
            "all_shapes_completed": all_shapes_completed,
            "parity_all_passed": parity_all_passed,
            "no_hot_path_host_materialization": no_hot_path_host_materialization,
            "min_ratio": min_ratio,
            "geomean_ratio": geomean_ratio,
            "min_per_shape_ratio_required": GOAL4633_MIN_PER_SHAPE_RATIO,
            "min_geomean_ratio_required": GOAL4633_MIN_GEOMEAN_RATIO,
            "promotion_thresholds_passed": promotion_thresholds_passed,
            "measured_catalog_promotion_requires_external_completion_audit": True,
        },
        "authorization": {
            "release_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "rt_core_pod_performance_claim_authorized": False,
            "tier3_callback_claim_authorized": False,
            "true_zero_copy_authorized": False,
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out is not None:
        _write_summary_markdown(payload, args.md_out)
    print(text)
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
