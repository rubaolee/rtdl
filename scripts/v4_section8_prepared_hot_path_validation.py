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


SUMMARY_SPEEDUP_GATE = 1.5
MIN_PASSING_SERIOUS_SIZES = 2


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _run_rows_hot(case: dict[str, tuple[object, ...]]) -> tuple[dict[str, object], ...]:
    from examples.current.apps.ml import rtdl_outlier_detection_app as app

    neighbor_rows = app._run_rows("optix", case)
    return app.density_rows_from_neighbor_rows(case["points"], neighbor_rows)


def _run_summary_hot(prepared, points: tuple[object, ...]) -> tuple[dict[str, object], ...]:
    from examples.current.apps.ml import rtdl_outlier_detection_app as app

    result = prepared.run(
        points,
        radius=app.RADIUS,
        threshold=app.MIN_NEIGHBORS_INCLUDING_SELF,
    )
    return app._density_rows_from_count_rows(points, result["rows"])


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


def _outlier_ids(rows: tuple[dict[str, object], ...]) -> tuple[int, ...]:
    return tuple(int(row["point_id"]) for row in rows if bool(row["is_outlier"]))


def _measure_size(copies: int, *, repeat: int, warmup: int, progress: bool) -> dict[str, Any]:
    import rtdsl as rt
    from examples.current.apps.ml import rtdl_outlier_detection_app as app

    case = app.make_outlier_case(copies=copies)
    oracle_rows = app.expected_tiled_density_rows(copies=copies)
    oracle_outliers = _outlier_ids(oracle_rows)

    _progress(progress, f"[route-start] copies={copies} route=rows_emit_reduce")
    rows_result = _measure(
        lambda: _run_rows_hot(case),
        repeat=repeat,
        warmup=warmup,
        progress=progress,
        label=f"copies={copies} route=rows_emit_reduce",
    )
    rows_payload = rows_result.pop("payload")

    _progress(progress, f"[prepare-start] copies={copies} route=summary_prepared")
    prepare_start = time.perf_counter()
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=case["points"],
        backend="optix",
        max_radius=app.RADIUS,
        prepare_scene=rt.prepare_optix_fixed_radius_count_threshold_2d,
    ) as prepared:
        prepare_sec = time.perf_counter() - prepare_start
        _progress(progress, f"[prepare-done] copies={copies} route=summary_prepared elapsed_s={prepare_sec:.6f}")
        summary_result = _measure(
            lambda: _run_summary_hot(prepared, case["points"]),
            repeat=repeat,
            warmup=warmup,
            progress=progress,
            label=f"copies={copies} route=summary_prepared_hot",
        )
    summary_payload = summary_result.pop("payload")

    rows_outliers = _outlier_ids(rows_payload)
    summary_outliers = _outlier_ids(summary_payload)
    correctness = {
        "correctness_passed": rows_outliers == oracle_outliers and summary_outliers == oracle_outliers,
        "oracle_outlier_count": len(oracle_outliers),
        "rows_outlier_count": len(rows_outliers),
        "summary_outlier_count": len(summary_outliers),
        "rows_matches_oracle": rows_outliers == oracle_outliers,
        "summary_matches_oracle": summary_outliers == oracle_outliers,
    }
    speedup = (
        float(rows_result["median_s"]) / float(summary_result["median_s"])
        if float(summary_result["median_s"]) > 0.0
        else None
    )
    return {
        "copies": int(copies),
        "point_count": len(case["points"]),
        "correctness": correctness,
        "correctness_passed": correctness["correctness_passed"],
        "prepare_sec": prepare_sec,
        "routes": {
            "rows_emit_reduce": {
                **rows_result,
                "tier": "tier1_separated_hot_path",
                "native_continuation_active": False,
                "neighbor_row_materialization": True,
            },
            "summary_prepared_hot": {
                **summary_result,
                "tier": "tier2_fused_native_primitive_hot_path",
                "native_continuation_active": True,
                "native_continuation_backend": "optix_threshold_count",
                "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "neighbor_row_materialization": False,
            },
        },
        "comparisons": {
            "summary_prepared_hot": {
                "baseline_median_s": rows_result["median_s"],
                "candidate_median_s": summary_result["median_s"],
                "speedup_over_rows_emit_reduce_median": speedup,
            }
        },
    }


def _evaluate_gate(results: list[dict[str, Any]]) -> dict[str, Any]:
    passing = []
    failures = []
    for result in results:
        copies = int(result["copies"])
        if not result.get("correctness_passed"):
            failures.append(f"copies={copies}: correctness failed")
            continue
        candidate = result["routes"]["summary_prepared_hot"]
        speedup = result["comparisons"]["summary_prepared_hot"]["speedup_over_rows_emit_reduce_median"]
        if (
            speedup is not None
            and float(speedup) >= SUMMARY_SPEEDUP_GATE
            and candidate.get("native_continuation_active") is True
            and candidate.get("generic_primitive") == "FIXED_RADIUS_COUNT_THRESHOLD_2D"
        ):
            passing.append({"copies": copies, "speedup": float(speedup)})
        else:
            failures.append(f"copies={copies}: summary hot path below gate or not fused")
    ok = len(passing) >= MIN_PASSING_SERIOUS_SIZES
    return {
        "status": "pass" if ok else "fail",
        "v4_prepared_hot_path_summary_locally_validated": bool(ok),
        "summary_speedup_gate": SUMMARY_SPEEDUP_GATE,
        "min_passing_serious_sizes": MIN_PASSING_SERIOUS_SIZES,
        "summary_passing_sizes": passing,
        "failures": failures,
        "authorized_next_step": (
            "external_review_then_consider_summary_hot_path_credit"
            if ok
            else "stop_summary_route_credit_and_revisit_architecture"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V4 Section 8 prepared-session hot-path validation harness.")
    parser.add_argument("--copies", type=int, action="append", default=[])
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=1)
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
        "protocol": "v4_section8_prepared_hot_path_validation",
        "copies": list(copies),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "timing_boundary": "case/oracle/prepare excluded; rows emit+reduce and prepared summary query+convert included",
        "release_claim_authorized": False,
        "near_handwritten_optix_claim_authorized": False,
    }
    if args.dry_run:
        payload = {"status": "dry_run", **plan}
    else:
        results = [
            _measure_size(copy_count, repeat=args.repeat, warmup=args.warmup, progress=args.progress)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
