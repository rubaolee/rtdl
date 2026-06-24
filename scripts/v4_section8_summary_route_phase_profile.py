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


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _profile_once(copies: int) -> dict[str, Any]:
    import rtdsl as rt
    from examples.current.apps.ml import rtdl_outlier_detection_app as app

    case_start = time.perf_counter()
    case = app.make_outlier_case(copies=copies)
    case_sec = time.perf_counter() - case_start

    rows_start = time.perf_counter()
    neighbor_rows = app._run_rows("optix", case)
    rows_emit_sec = time.perf_counter() - rows_start

    rows_reduce_start = time.perf_counter()
    density_rows_from_rows = app.density_rows_from_neighbor_rows(case["points"], neighbor_rows)
    rows_reduce_sec = time.perf_counter() - rows_reduce_start

    summary_prepare_start = time.perf_counter()
    with rt.prepare_generic_fixed_radius_count_threshold_2d(
        search_points=case["points"],
        backend="optix",
        max_radius=app.RADIUS,
        prepare_scene=rt.prepare_optix_fixed_radius_count_threshold_2d,
    ) as prepared:
        summary_prepare_sec = time.perf_counter() - summary_prepare_start

        summary_run_start = time.perf_counter()
        summary_result = prepared.run(
            case["points"],
            radius=app.RADIUS,
            threshold=app.MIN_NEIGHBORS_INCLUDING_SELF,
        )
        summary_run_sec = time.perf_counter() - summary_run_start

        scalar_run_start = time.perf_counter()
        scalar_result = prepared.count_threshold_reached(
            case["points"],
            radius=app.RADIUS,
            threshold=app.MIN_NEIGHBORS_INCLUDING_SELF,
        )
        scalar_run_sec = time.perf_counter() - scalar_run_start

    summary_convert_start = time.perf_counter()
    density_rows_from_summary = app._density_rows_from_count_rows(case["points"], summary_result["rows"])
    summary_convert_sec = time.perf_counter() - summary_convert_start

    oracle_rows = app.expected_tiled_density_rows(copies=copies)
    return {
        "copies": int(copies),
        "point_count": len(case["points"]),
        "neighbor_row_count": len(neighbor_rows),
        "summary_row_count": int(summary_result["row_count"]),
        "case_sec": case_sec,
        "rows_emit_sec": rows_emit_sec,
        "rows_reduce_sec": rows_reduce_sec,
        "rows_total_sec": rows_emit_sec + rows_reduce_sec,
        "summary_prepare_sec": summary_prepare_sec,
        "summary_native_run_sec": summary_run_sec,
        "summary_python_convert_sec": summary_convert_sec,
        "summary_total_without_prepare_sec": summary_run_sec + summary_convert_sec,
        "summary_total_with_prepare_sec": summary_prepare_sec + summary_run_sec + summary_convert_sec,
        "scalar_native_run_sec": scalar_run_sec,
        "scalar_threshold_reached_count": int(scalar_result["threshold_reached_count"]),
        "summary_matches_oracle": density_rows_from_summary == oracle_rows,
        "rows_matches_oracle": density_rows_from_rows == oracle_rows,
        "summary_run_phases": summary_result.get("run_phases", {}),
        "scalar_run_phases": scalar_result.get("run_phases", {}),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile V4 Section 8 fixed-radius summary route phases.")
    parser.add_argument("--copies", type=int, action="append", default=[])
    parser.add_argument("--repeat", type=int, default=5)
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

    if args.dry_run:
        payload: dict[str, Any] = {
            "status": "dry_run",
            "protocol": "v4_section8_summary_route_phase_profile",
            "copies": list(copies),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
        }
    else:
        results: list[dict[str, Any]] = []
        for copy_count in copies:
            _progress(args.progress, f"[size-start] copies={copy_count}")
            for index in range(args.warmup):
                _progress(args.progress, f"[warmup] copies={copy_count} {index + 1}/{args.warmup}")
                _profile_once(copy_count)
            repeats = []
            for index in range(args.repeat):
                _progress(args.progress, f"[repeat-start] copies={copy_count} {index + 1}/{args.repeat}")
                item = _profile_once(copy_count)
                repeats.append(item)
                _progress(
                    args.progress,
                    (
                        f"[repeat-done] copies={copy_count} {index + 1}/{args.repeat} "
                        f"rows_total_s={item['rows_total_sec']:.6f} "
                        f"summary_total_s={item['summary_total_without_prepare_sec']:.6f} "
                        f"scalar_s={item['scalar_native_run_sec']:.6f}"
                    ),
                )

            fields = [
                "rows_emit_sec",
                "rows_reduce_sec",
                "rows_total_sec",
                "summary_prepare_sec",
                "summary_native_run_sec",
                "summary_python_convert_sec",
                "summary_total_without_prepare_sec",
                "summary_total_with_prepare_sec",
                "scalar_native_run_sec",
            ]
            medians = {field + "_median": _median([float(item[field]) for item in repeats]) for field in fields}
            first = repeats[-1]
            results.append(
                {
                    "copies": int(copy_count),
                    "point_count": first["point_count"],
                    "neighbor_row_count": first["neighbor_row_count"],
                    "summary_row_count": first["summary_row_count"],
                    "rows_matches_oracle": all(bool(item["rows_matches_oracle"]) for item in repeats),
                    "summary_matches_oracle": all(bool(item["summary_matches_oracle"]) for item in repeats),
                    "medians": medians,
                    "repeats": repeats,
                }
            )
            _progress(args.progress, f"[size-done] copies={copy_count}")
        payload = {
            "status": "measured",
            "protocol": "v4_section8_summary_route_phase_profile",
            "copies": list(copies),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "results": results,
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
