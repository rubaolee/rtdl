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


ROUTE_CONFIGS: dict[str, dict[str, Any]] = {
    "optix_rows": {
        "description": "Tier-1 separated route: OptiX neighbor rows plus Python reduction",
        "kwargs": {
            "backend": "optix",
            "output_mode": "full",
            "optix_summary_mode": "rows",
        },
        "tier": "tier1_separated",
        "requires_gpu": True,
    },
    "optix_fused_prepared_scalar": {
        "description": "Tier-2 fused route: prepared OptiX count-threshold scalar",
        "kwargs": {
            "backend": "optix",
            "output_mode": "density_count",
        },
        "tier": "tier2_fused_native_primitive",
        "requires_gpu": True,
    },
    "optix_fused_prepared_summary": {
        "description": "Tier-2 fused route: prepared OptiX count-threshold compact rows",
        "kwargs": {
            "backend": "optix",
            "output_mode": "density_summary",
            "optix_summary_mode": "rt_count_threshold_prepared",
        },
        "tier": "tier2_fused_native_primitive",
        "requires_gpu": True,
    },
    "embree_rows": {
        "description": "CPU native control: Embree neighbor rows plus Python reduction",
        "kwargs": {
            "backend": "embree",
            "output_mode": "full",
            "embree_summary_mode": "rows",
        },
        "tier": "cpu_native_control",
        "requires_gpu": False,
    },
    "embree_fused_prepared_summary": {
        "description": "CPU native control: prepared Embree count-threshold compact rows",
        "kwargs": {
            "backend": "embree",
            "output_mode": "density_summary",
            "embree_summary_mode": "rt_count_threshold_prepared",
        },
        "tier": "cpu_native_control",
        "requires_gpu": False,
    },
    "scipy_density_count": {
        "description": "External CPU scalar control",
        "kwargs": {
            "backend": "scipy",
            "output_mode": "density_count",
        },
        "tier": "external_cpu_control",
        "requires_gpu": False,
    },
}


DEFAULT_ROUTES = (
    "optix_rows",
    "optix_fused_prepared_scalar",
    "optix_fused_prepared_summary",
)

SCALAR_SPEEDUP_GATE = 2.0
SUMMARY_SPEEDUP_GATE = 1.5
MIN_PASSING_SERIOUS_SIZES = 2


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _run_outlier_route(route: str, *, copies: int) -> dict[str, Any]:
    from examples.current.apps.ml.rtdl_outlier_detection_app import run_app

    config = ROUTE_CONFIGS[route]
    kwargs = dict(config["kwargs"])
    return run_app(copies=int(copies), **kwargs)


def _signature(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "point_count": payload.get("point_count"),
        "outlier_count": payload.get("outlier_count"),
        "threshold_reached_count": payload.get("threshold_reached_count"),
        "matches_oracle": payload.get("matches_oracle"),
    }


def _signature_match(reference: dict[str, Any], candidate: dict[str, Any]) -> bool:
    if reference.get("matches_oracle") is not True or candidate.get("matches_oracle") is not True:
        return False
    for key in ("point_count", "outlier_count"):
        if reference.get(key) != candidate.get(key):
            return False
    ref_threshold = reference.get("threshold_reached_count")
    cand_threshold = candidate.get("threshold_reached_count")
    if ref_threshold is not None and cand_threshold is not None and ref_threshold != cand_threshold:
        return False
    return True


def _correctness_details(size_results: list[dict[str, Any]]) -> dict[str, Any]:
    if not size_results:
        return {
            "correctness_passed": False,
            "reason": "no_route_results",
            "reference_route": None,
            "signature_matches": {},
        }
    reference = size_results[0]
    reference_signature = reference["signature"]
    matches = {
        item["route"]: _signature_match(reference_signature, item["signature"])
        for item in size_results
    }
    return {
        "correctness_passed": all(matches.values()),
        "reference_route": reference["route"],
        "reference_signature": reference_signature,
        "signature_matches": matches,
        "route_signatures": {
            item["route"]: item["signature"]
            for item in size_results
        },
    }


def _measure_route(
    route: str,
    *,
    copies: int,
    repeat: int,
    warmup: int,
    progress: bool = False,
) -> dict[str, Any]:
    _progress(progress, f"[start] copies={copies} route={route}")
    for index in range(int(warmup)):
        _progress(progress, f"[warmup] copies={copies} route={route} {index + 1}/{warmup}")
        _run_outlier_route(route, copies=copies)

    timings: list[float] = []
    payload: dict[str, Any] | None = None
    for index in range(int(repeat)):
        _progress(progress, f"[repeat-start] copies={copies} route={route} {index + 1}/{repeat}")
        start = time.perf_counter()
        payload = _run_outlier_route(route, copies=copies)
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        _progress(
            progress,
            f"[repeat-done] copies={copies} route={route} {index + 1}/{repeat} elapsed_s={elapsed:.6f}",
        )

    if payload is None:
        raise RuntimeError("repeat must be positive")

    median_s = statistics.median(timings)
    _progress(progress, f"[done] copies={copies} route={route} median_s={median_s:.6f}")

    return {
        "route": route,
        "tier": ROUTE_CONFIGS[route]["tier"],
        "description": ROUTE_CONFIGS[route]["description"],
        "copies": int(copies),
        "point_count": payload.get("point_count"),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "timings_s": timings,
        "median_s": median_s,
        "min_s": min(timings),
        "max_s": max(timings),
        "signature": _signature(payload),
        "native_continuation_active": payload.get("native_continuation_active"),
        "native_continuation_backend": payload.get("native_continuation_backend"),
        "generic_primitive": payload.get("generic_primitive"),
        "summary_primitive": payload.get("summary_primitive"),
        "summary_mode": payload.get("summary_mode"),
        "neighbor_row_count": payload.get("neighbor_row_count"),
        "native_summary_row_count": payload.get("native_summary_row_count"),
        "boundary": payload.get("boundary"),
    }


def _compare(size_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_route = {item["route"]: item for item in size_results}
    baseline = by_route.get("optix_rows")
    if baseline is None:
        return {"status": "no_optix_rows_baseline"}

    comparisons: dict[str, Any] = {}
    for route in ("optix_fused_prepared_scalar", "optix_fused_prepared_summary"):
        candidate = by_route.get(route)
        if candidate is None:
            continue
        comparisons[route] = {
            "speedup_over_optix_rows_median": (
                float(baseline["median_s"]) / float(candidate["median_s"])
                if float(candidate["median_s"]) > 0.0
                else None
            ),
            "baseline_median_s": baseline["median_s"],
            "candidate_median_s": candidate["median_s"],
        }
    return comparisons


def _is_fused_fixed_radius_route(route_result: dict[str, Any]) -> bool:
    if route_result.get("tier") != "tier2_fused_native_primitive":
        return False
    if route_result.get("native_continuation_active") is not True:
        return False
    primitive_text = " ".join(
        str(route_result.get(key) or "")
        for key in ("native_continuation_backend", "generic_primitive", "summary_primitive", "summary_mode")
    )
    return "threshold_count" in primitive_text or "fixed_radius_count_threshold" in primitive_text


def _evaluate_gate(results: list[dict[str, Any]]) -> dict[str, Any]:
    scalar_passes: list[dict[str, Any]] = []
    summary_passes: list[dict[str, Any]] = []
    failures: list[str] = []
    for size in results:
        copies = int(size["copies"])
        if not size.get("correctness_passed"):
            failures.append(f"copies={copies}: correctness failed")
            continue
        by_route = {item["route"]: item for item in size.get("route_results", [])}
        comparisons = size.get("comparisons", {})
        scalar = comparisons.get("optix_fused_prepared_scalar", {})
        scalar_speedup = scalar.get("speedup_over_optix_rows_median")
        if (
            scalar_speedup is not None
            and float(scalar_speedup) >= SCALAR_SPEEDUP_GATE
            and _is_fused_fixed_radius_route(by_route.get("optix_fused_prepared_scalar", {}))
        ):
            scalar_passes.append({"copies": copies, "speedup": float(scalar_speedup)})
        else:
            failures.append(f"copies={copies}: scalar route below gate or not fused")

        summary = comparisons.get("optix_fused_prepared_summary", {})
        summary_speedup = summary.get("speedup_over_optix_rows_median")
        if (
            summary_speedup is not None
            and float(summary_speedup) >= SUMMARY_SPEEDUP_GATE
            and _is_fused_fixed_radius_route(by_route.get("optix_fused_prepared_summary", {}))
        ):
            summary_passes.append({"copies": copies, "speedup": float(summary_speedup)})
        else:
            failures.append(f"copies={copies}: summary route below gate or not fused")

    scalar_ok = len(scalar_passes) >= MIN_PASSING_SERIOUS_SIZES
    summary_ok = len(summary_passes) >= MIN_PASSING_SERIOUS_SIZES
    return {
        "status": "pass" if scalar_ok and summary_ok else "fail",
        "v4_tier2_thesis_locally_validated": bool(scalar_ok and summary_ok),
        "scalar_speedup_gate": SCALAR_SPEEDUP_GATE,
        "summary_speedup_gate": SUMMARY_SPEEDUP_GATE,
        "min_passing_serious_sizes": MIN_PASSING_SERIOUS_SIZES,
        "scalar_passing_sizes": scalar_passes,
        "summary_passing_sizes": summary_passes,
        "failures": failures,
        "authorized_next_step": (
            "external_review_then_promote_tier2_primitive_library"
            if scalar_ok and summary_ok
            else "stop_v4_performance_release_and_revisit_architecture"
        ),
    }


def _build_plan(routes: tuple[str, ...], copies: tuple[int, ...], repeat: int, warmup: int) -> dict[str, Any]:
    return {
        "protocol": "v4_section8_fixed_radius_count_threshold_validation",
        "routes": [
            {
                "route": route,
                "tier": ROUTE_CONFIGS[route]["tier"],
                "description": ROUTE_CONFIGS[route]["description"],
                "requires_gpu": ROUTE_CONFIGS[route]["requires_gpu"],
                "kwargs": ROUTE_CONFIGS[route]["kwargs"],
            }
            for route in routes
        ],
        "copies": list(copies),
        "repeat": int(repeat),
        "warmup": int(warmup),
        "independent_handwritten_optix_reference_available": False,
        "near_handwritten_optix_claim_authorized": False,
        "claim_boundary": (
            "This harness can validate fused primitive vs separated RTDL route. "
            "It cannot authorize near-handwritten OptiX wording without an independent reference route."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="V4 Section 8 fixed-radius count-threshold fused primitive validation harness."
    )
    parser.add_argument("--copies", type=int, action="append", default=[])
    parser.add_argument("--route", choices=sorted(ROUTE_CONFIGS), action="append", default=[])
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--progress", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copies = tuple(args.copies) if args.copies else (8192, 32768, 131072)
    routes = tuple(args.route) if args.route else DEFAULT_ROUTES
    if args.repeat <= 0:
        raise SystemExit("--repeat must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup must be non-negative")

    plan = _build_plan(routes, copies, args.repeat, args.warmup)
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        all_results: list[dict[str, Any]] = []
        for copy_count in copies:
            _progress(args.progress, f"[size-start] copies={copy_count}")
            size_results = [
                _measure_route(
                    route,
                    copies=copy_count,
                    repeat=args.repeat,
                    warmup=args.warmup,
                    progress=args.progress,
                )
                for route in routes
            ]
            correctness = _correctness_details(size_results)
            all_results.append(
                {
                    "copies": int(copy_count),
                    "point_count": size_results[0].get("point_count") if size_results else None,
                    "correctness_passed": correctness["correctness_passed"],
                    "correctness": correctness,
                    "route_results": size_results,
                    "comparisons": _compare(size_results),
                }
            )
            _progress(args.progress, f"[size-done] copies={copy_count} correctness={correctness['correctness_passed']}")
        gate = _evaluate_gate(all_results)
        payload = {
            "status": "measured",
            **plan,
            "results": all_results,
            "performance_gate": gate,
            "release_claim_authorized": False,
            "near_handwritten_optix_claim_authorized": False,
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
