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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


RADIUS = 0.35
THRESHOLD = 3
BASE_POINTS_PER_COPY = 8
EXPECTED_THRESHOLD_REACHED_PER_COPY = 6
EXPECTED_OUTLIERS_PER_COPY = 2
EXPECTED_NEIGHBOR_COUNT_SUM_PER_COPY = 20

MIN_GAP_REDUCTION_FACTOR = 10.0
MAX_DEVICE_ARRAY_TO_ROUTE_D_ROWS_GAP = 100.0
MIN_PASSING_SERIOUS_SIZES = 2

DEFAULT_ROUTE_D_JSON = ROOT / "future" / "v4" / "evidence" / "v4_section8_route_d_result_2026-06-24.json"
DEFAULT_PREPARED_SUMMARY_JSON = (
    ROOT / "future" / "v4" / "evidence" / "v4_section8_prepared_hot_path_result_2026-06-24.json"
)


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _route_d_rows_by_copies(payload: dict[str, Any]) -> dict[int, float]:
    return {
        int(result["copies"]): float(result["routes"]["route_d_count_rows"]["median_s"])
        for result in payload.get("results", [])
    }


def _prepared_summary_by_copies(payload: dict[str, Any]) -> dict[int, float]:
    return {
        int(result["copies"]): float(result["routes"]["summary_prepared_hot"]["median_s"])
        for result in payload.get("results", [])
    }


def _make_device_outlier_columns(module, copies: int, *, partner: str) -> dict[str, object]:
    if copies < 1:
        raise ValueError("copies must be positive")
    if partner == "torch":
        torch = module
        device = torch.device("cuda:0")
        base_ids_i64 = torch.tensor([1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.int64, device=device)
        base_x = torch.tensor([0.00, 0.12, -0.10, 2.00, 2.14, 1.88, 4.50, -3.00], dtype=torch.float64, device=device)
        base_y = torch.tensor([0.00, 0.04, 0.08, 2.00, 2.05, 1.94, 0.00, 2.50], dtype=torch.float64, device=device)
        copy_ids_i64 = torch.arange(copies, dtype=torch.int64, device=device)
        copy_ids_f64 = torch.arange(copies, dtype=torch.float64, device=device)
        ids_i64 = base_ids_i64.repeat(copies) + torch.repeat_interleave(copy_ids_i64 * 100, BASE_POINTS_PER_COPY)
        ids = ids_i64.to(torch.uint32)
        x = base_x.repeat(copies) + torch.repeat_interleave(copy_ids_f64 * 7.0, BASE_POINTS_PER_COPY)
        y = base_y.repeat(copies)
        return {"ids": ids.contiguous(), "x": x.contiguous(), "y": y.contiguous()}
    if partner == "cupy":
        cupy = module
        base_ids = cupy.asarray([1, 2, 3, 4, 5, 6, 7, 8], dtype=cupy.uint32)
        base_x = cupy.asarray([0.00, 0.12, -0.10, 2.00, 2.14, 1.88, 4.50, -3.00], dtype=cupy.float64)
        base_y = cupy.asarray([0.00, 0.04, 0.08, 2.00, 2.05, 1.94, 0.00, 2.50], dtype=cupy.float64)
        copy_ids_u32 = cupy.arange(copies, dtype=cupy.uint32)
        copy_ids_f64 = cupy.arange(copies, dtype=cupy.float64)
        ids = cupy.tile(base_ids, copies) + cupy.repeat(copy_ids_u32 * cupy.uint32(100), BASE_POINTS_PER_COPY)
        x = cupy.tile(base_x, copies) + cupy.repeat(copy_ids_f64 * 7.0, BASE_POINTS_PER_COPY)
        y = cupy.tile(base_y, copies)
        return {"ids": ids, "x": x, "y": y}
    raise ValueError("partner must be 'torch' or 'cupy'")


def _sync_partner(module, *, partner: str) -> None:
    if partner == "torch":
        module.cuda.synchronize()
        return
    if partner == "cupy":
        module.cuda.runtime.deviceSynchronize()
        return
    raise ValueError("partner must be 'torch' or 'cupy'")


def _device_sum_int(module, value, *, partner: str) -> int:
    if partner == "torch":
        return int(module.sum(value).detach().cpu().item())
    if partner == "cupy":
        return int(module.asnumpy(module.sum(value)).item())
    raise ValueError("partner must be 'torch' or 'cupy'")


def _measure(callable_obj, *, repeat: int, warmup: int, progress: bool, label: str) -> dict[str, Any]:
    for index in range(warmup):
        _progress(progress, f"[warmup] {label} {index + 1}/{warmup}")
        callable_obj()

    timings: list[float] = []
    payload = None
    for index in range(repeat):
        _progress(progress, f"[repeat-start] {label} {index + 1}/{repeat}")
        start = time.perf_counter()
        payload = callable_obj()
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
    copies: int,
    *,
    partner: str,
    repeat: int,
    warmup: int,
    progress: bool,
    route_d_rows_median_s: float,
    prior_prepared_summary_median_s: float,
) -> dict[str, Any]:
    import rtdsl.v4_fixed_radius as rt_v4

    if partner == "torch":
        import torch as array_module
    elif partner == "cupy":
        import cupy as array_module
    else:
        raise ValueError("partner must be 'torch' or 'cupy'")

    point_count = int(copies) * BASE_POINTS_PER_COPY
    columns = _make_device_outlier_columns(array_module, copies, partner=partner)
    _sync_partner(array_module, partner=partner)
    prepare_start = time.perf_counter()
    with rt_v4.prepare_fixed_radius_count_threshold_2d_device_arrays_v4(
        columns,
        max_radius=RADIUS,
        partner=partner,
    ) as session:
        prepare_sec = time.perf_counter() - prepare_start
        output_columns = session.allocate_outputs(point_count)

        def run_once() -> dict[str, object]:
            return session.run(
                columns,
                radius=RADIUS,
                threshold=THRESHOLD,
                output_columns=output_columns,
                return_metadata=True,
            )

        measured = _measure(
            run_once,
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"copies={copies} route=device_array_frontdoor_prepared",
        )

    last_payload = measured.pop("payload") or {}
    threshold_flags = output_columns["threshold_flags"]
    neighbor_counts = output_columns["neighbor_counts"]
    threshold_reached_count = _device_sum_int(array_module, threshold_flags, partner=partner)
    neighbor_count_sum = _device_sum_int(array_module, neighbor_counts, partner=partner)
    outlier_count = point_count - threshold_reached_count
    expected_threshold_reached = EXPECTED_THRESHOLD_REACHED_PER_COPY * int(copies)
    expected_outliers = EXPECTED_OUTLIERS_PER_COPY * int(copies)
    expected_neighbor_count_sum = EXPECTED_NEIGHBOR_COUNT_SUM_PER_COPY * int(copies)
    correctness = {
        "correctness_passed": (
            threshold_reached_count == expected_threshold_reached
            and outlier_count == expected_outliers
            and neighbor_count_sum == expected_neighbor_count_sum
        ),
        "expected_threshold_reached_count": expected_threshold_reached,
        "threshold_reached_count": threshold_reached_count,
        "expected_outlier_count": expected_outliers,
        "outlier_count": outlier_count,
        "expected_neighbor_count_sum": expected_neighbor_count_sum,
        "neighbor_count_sum": neighbor_count_sum,
    }
    candidate_median_s = float(measured["median_s"])
    prior_gap = (
        float(prior_prepared_summary_median_s) / float(route_d_rows_median_s)
        if route_d_rows_median_s > 0.0
        else None
    )
    candidate_gap = candidate_median_s / float(route_d_rows_median_s) if route_d_rows_median_s > 0.0 else None
    gap_reduction = (
        float(prior_gap) / float(candidate_gap)
        if prior_gap is not None and candidate_gap is not None and candidate_gap > 0.0
        else None
    )
    metadata = dict(last_payload.get("metadata", {}))
    native_metadata = dict(metadata.get("native_metadata", {}))
    return {
        "copies": int(copies),
        "point_count": point_count,
        "correctness": correctness,
        "correctness_passed": correctness["correctness_passed"],
        "prepare_sec": prepare_sec,
        "routes": {
            "device_array_frontdoor_prepared": {
                **measured,
                "tier": "tier2_fused_native_primitive_device_array_frontdoor",
                "partner": partner,
                "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "input_contract": f"caller_supplied_{partner}_device_point_columns",
                "python_point_object_boundary_in_hot_path": False,
                "app_row_materialization_in_hot_path": False,
                "host_materialization_in_hot_path": False,
                "output_columns_reused": True,
                "native_continuation_active": True,
                "native_continuation_backend": "optix_threshold_count",
                "metadata": metadata,
                "native_metadata": native_metadata,
            },
        },
        "comparisons": {
            "route_d_count_rows": {
                "baseline_median_s": route_d_rows_median_s,
                "candidate_median_s": candidate_median_s,
                "device_array_to_route_d_rows_gap": candidate_gap,
            },
            "prior_prepared_summary_gap": {
                "prior_prepared_summary_median_s": prior_prepared_summary_median_s,
                "prior_summary_to_route_d_rows_gap": prior_gap,
                "device_array_gap_reduction_over_prior_summary": gap_reduction,
            },
        },
    }


def _evaluate_gate(results: list[dict[str, Any]]) -> dict[str, Any]:
    passing: list[dict[str, Any]] = []
    failures: list[str] = []
    for result in results:
        copies = int(result["copies"])
        route = result["routes"]["device_array_frontdoor_prepared"]
        gap = result["comparisons"]["route_d_count_rows"]["device_array_to_route_d_rows_gap"]
        reduction = result["comparisons"]["prior_prepared_summary_gap"]["device_array_gap_reduction_over_prior_summary"]
        if not result.get("correctness_passed"):
            failures.append(f"copies={copies}: correctness failed")
            continue
        if route.get("python_point_object_boundary_in_hot_path") is not False:
            failures.append(f"copies={copies}: Python point boundary still in hot path")
            continue
        if route.get("host_materialization_in_hot_path") is not False:
            failures.append(f"copies={copies}: host materialization still in hot path")
            continue
        if (
            gap is not None
            and reduction is not None
            and float(gap) <= MAX_DEVICE_ARRAY_TO_ROUTE_D_ROWS_GAP
            and float(reduction) >= MIN_GAP_REDUCTION_FACTOR
        ):
            passing.append(
                {
                    "copies": copies,
                    "device_array_to_route_d_rows_gap": float(gap),
                    "gap_reduction_over_prior_summary": float(reduction),
                }
            )
        else:
            failures.append(f"copies={copies}: product-boundary gap did not shrink enough")
    ok = len(passing) >= MIN_PASSING_SERIOUS_SIZES
    return {
        "status": "pass" if ok else "fail",
        "v4_device_array_frontdoor_locally_validated": bool(ok),
        "min_gap_reduction_factor": MIN_GAP_REDUCTION_FACTOR,
        "max_device_array_to_route_d_rows_gap": MAX_DEVICE_ARRAY_TO_ROUTE_D_ROWS_GAP,
        "min_passing_serious_sizes": MIN_PASSING_SERIOUS_SIZES,
        "passing_sizes": passing,
        "failures": failures,
        "authorized_next_step": (
            "external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive"
            if ok
            else "stop_second_primitive_work_and_continue_product_boundary_reduction"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V4 Section 8 device-array front-door validation harness.")
    parser.add_argument("--copies", type=int, action="append", default=[])
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--route-d-json", type=Path, default=DEFAULT_ROUTE_D_JSON)
    parser.add_argument("--prepared-summary-json", type=Path, default=DEFAULT_PREPARED_SUMMARY_JSON)
    parser.add_argument("--partner", choices=("torch", "cupy"), default="torch")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copies = tuple(args.copies) if args.copies else (8192, 32768, 131072)
    if args.repeat <= 0:
        raise SystemExit("--repeat must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup must be non-negative")

    plan = {
        "protocol": "v4_section8_device_array_frontdoor_validation",
        "copies": list(copies),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "route_d_json": str(args.route_d_json),
        "prepared_summary_json": str(args.prepared_summary_json),
        "partner": args.partner,
        "timing_boundary": (
            "fixture/device-array construction and prepared scene excluded; "
            "prepared RTDL device-column query, native launch, sync, and output writes included; "
            "correctness host reductions are outside timed repeats"
        ),
        "frontdoor_contract": {
            "input": f"caller_supplied_{args.partner}_device_point_columns",
            "measured_partner": args.partner,
            "measured_partners": [args.partner],
            "partner_support_declared_unmeasured": [
                partner for partner in ("torch", "cupy") if partner != args.partner
            ],
            "no_python_point_rows_in_hot_path": True,
            "output": f"reused_{args.partner}_device_output_columns",
            "route_d_ceiling": "independent hand-written OptiX count-row route",
        },
        "product_boundary_gate": {
            "min_gap_reduction_factor": MIN_GAP_REDUCTION_FACTOR,
            "max_device_array_to_route_d_rows_gap": MAX_DEVICE_ARRAY_TO_ROUTE_D_ROWS_GAP,
            "min_passing_serious_sizes": MIN_PASSING_SERIOUS_SIZES,
        },
        "release_claim_authorized": False,
        "near_handwritten_optix_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
    }
    if args.dry_run:
        payload: dict[str, Any] = {
            "status": "dry_run",
            **plan,
            "baseline_files_present": {
                "route_d_json": args.route_d_json.exists(),
                "prepared_summary_json": args.prepared_summary_json.exists(),
            },
        }
    else:
        route_d_rows = _route_d_rows_by_copies(_load_json(args.route_d_json))
        prepared_summary = _prepared_summary_by_copies(_load_json(args.prepared_summary_json))
        missing = [
            copy_count
            for copy_count in copies
            if int(copy_count) not in route_d_rows or int(copy_count) not in prepared_summary
        ]
        if missing:
            raise SystemExit(f"missing Route D or prepared-summary baselines for copies: {missing}")
        results = [
            _measure_size(
                int(copy_count),
                partner=args.partner,
                repeat=args.repeat,
                warmup=args.warmup,
                progress=args.progress,
                route_d_rows_median_s=route_d_rows[int(copy_count)],
                prior_prepared_summary_median_s=prepared_summary[int(copy_count)],
            )
            for copy_count in copies
        ]
        payload = {
            "status": "measured",
            **plan,
            "results": results,
            "performance_gate": _evaluate_gate(results),
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"dry_run", "measured"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
