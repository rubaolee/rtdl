from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin import (  # noqa: E402
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


SCHEMA = "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1"
CLAIM_BOUNDARY = {
    "public_speedup_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "release_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
}


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _min(values: list[float]) -> float | None:
    return float(min(values)) if values else None


def _max(values: list[float]) -> float | None:
    return float(max(values)) if values else None


def _command_output(command: list[str]) -> str | None:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None


def _git_commit() -> str | None:
    return _command_output(["git", "rev-parse", "HEAD"])


def _git_dirty() -> list[str]:
    return (_command_output(["git", "status", "--short"]) or "").splitlines()


def _gpu_name() -> str | None:
    return _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])


def parse_rayjoin_query_log(text: str) -> dict[str, Any]:
    """Parse RayJoin query_exec logs without treating them as a parity oracle."""
    timings: dict[str, float] = {}
    for label, value in re.findall(r"^\s*-\s*([^:]+):\s*([0-9.]+)\s*ms\s*$", text, re.MULTILINE):
        timings[label.strip().lower().replace(" ", "_")] = float(value)
    intersections = None
    match = re.search(r"Intersections:\s*([0-9]+)", text)
    if match:
        intersections = int(match.group(1))
    checker_passed = bool(re.search(r"Map:\s*[0-9]+\s+passed check", text))
    launch_counts = [int(value) for value in re.findall(r"optixLaunch,\s*\[w,h,d\]\s*=\s*([0-9]+),", text)]
    return {
        "timings_ms": timings,
        "query_ms": timings.get("query"),
        "warmup_ms": timings.get("warmup"),
        "build_index_ms": timings.get("build_index"),
        "intersections": intersections,
        "positive_assignment_count_available": False,
        "checker_passed": checker_passed,
        "optix_launch_widths": launch_counts,
    }


def summarize_samples(values: list[float]) -> dict[str, Any]:
    return {
        "samples": values,
        "median": _median(values),
        "min": _min(values),
        "max": _max(values),
        "count": len(values),
    }


def summarize_int_samples(values: list[int]) -> dict[str, Any]:
    return {
        "samples": values,
        "last": values[-1] if values else None,
        "consistent": len(set(values)) <= 1,
        "count": len(values),
    }


@contextlib.contextmanager
def temporary_env(name: str, value: str | None):
    if value is None:
        yield
        return
    previous = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


def run_rayjoin_process_samples(
    *,
    query_exec: Path,
    workload: str,
    data_dir: Path,
    poly1_override: Path | None = None,
    poly2_override: Path | None = None,
    warmup: int,
    repeat: int,
    process_repeats: int,
    timeout_seconds: int,
    log_dir: Path,
) -> dict[str, Any]:
    if workload not in {"lsi", "pip"}:
        raise ValueError(f"unsupported RayJoin workload: {workload}")
    if poly1_override is not None or poly2_override is not None:
        if poly1_override is None or poly2_override is None:
            raise ValueError("RayJoin poly override requires both poly1 and poly2")
        poly1 = poly1_override
        poly2 = poly2_override
    elif workload == "lsi":
        poly1 = data_dir / "br_county_start256_count512.cdb"
        poly2 = data_dir / "br_soil_start256_count512.cdb"
    else:
        poly1 = data_dir / "br_county_start0_count512.cdb"
        poly2 = data_dir / "br_county_start0_count512.cdb"

    query_ms: list[float] = []
    warmup_ms: list[float] = []
    build_index_ms: list[float] = []
    intersections: list[int] = []
    parsed_samples: list[dict[str, Any]] = []

    for index in range(process_repeats):
        log_path = log_dir / f"rayjoin_{workload}_process_{index + 1}.log"
        command = [
            str(query_exec),
            f"-poly1={poly1}",
            f"-poly2={poly2}",
            "-mode=rt",
            f"-query={workload}",
            f"-warmup={int(warmup)}",
            f"-repeat={int(repeat)}",
            "-check=false",
            "-logtostderr=true",
        ]
        print(f"[goal3244] RayJoin {workload} process {index + 1}/{process_repeats}", flush=True)
        proc = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        text = proc.stdout + proc.stderr
        log_path.write_text(text, encoding="utf-8")
        parsed = parse_rayjoin_query_log(text)
        parsed["returncode"] = proc.returncode
        parsed["log"] = str(log_path)
        parsed_samples.append(parsed)
        if proc.returncode != 0:
            continue
        if isinstance(parsed.get("query_ms"), float):
            query_ms.append(float(parsed["query_ms"]))
        if isinstance(parsed.get("warmup_ms"), float):
            warmup_ms.append(float(parsed["warmup_ms"]))
        if isinstance(parsed.get("build_index_ms"), float):
            build_index_ms.append(float(parsed["build_index_ms"]))
        if isinstance(parsed.get("intersections"), int):
            intersections.append(int(parsed["intersections"]))

    return {
        "system": "rayjoin_upstream_query_exec",
        "workload": workload,
        "mode": "rt",
        "internal_warmup": int(warmup),
        "internal_repeat": int(repeat),
        "process_repeats": int(process_repeats),
        "query_ms_reported": summarize_samples(query_ms),
        "warmup_ms_reported": summarize_samples(warmup_ms),
        "build_index_ms_reported": summarize_samples(build_index_ms),
        "intersection_counts": summarize_int_samples(intersections),
        "positive_assignment_count_available": False,
        "input_poly1": str(poly1),
        "input_poly2": str(poly2),
        "samples": parsed_samples,
        "command_template": [
            str(query_exec),
            f"-poly1={poly1}",
            f"-poly2={poly2}",
            "-mode=rt",
            f"-query={workload}",
            f"-warmup={int(warmup)}",
            f"-repeat={int(repeat)}",
            "-check=false",
            "-logtostderr=true",
        ],
    }


def run_rtdl_samples(
    *,
    workload: str,
    dataset: str,
    warmup: int,
    repeat: int,
    count_mode: str = "exact",
    query_axis: str | None = None,
    boundary_mode: str | None = None,
    point_order_mode: str = "natural",
) -> dict[str, Any]:
    if count_mode != "exact" and workload != "pip":
        raise ValueError("non-exact count_mode is only supported for RTDL PIP samples")
    if point_order_mode != "natural" and workload != "pip":
        raise ValueError("point_order_mode is only supported for RTDL PIP samples")

    query_sec: list[float] = []
    validation_exact_query_sec: list[float] = []
    query_pack_sec: list[float] = []
    prepare_sec: list[float] = []
    static_shape_pack_sec: list[float] = []
    counts: list[int] = []
    native_phase_samples: list[dict[str, Any] | None] = []

    def one() -> dict[str, Any]:
        with temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", query_axis):
            return rayjoin_app.run_rayjoin_prepared_optix_workload(
                workload,
                dataset=dataset,
                result_mode="count",
                include_rows=False,
                count_mode=count_mode,
                device_filtered_boundary_mode=boundary_mode,
                point_order_mode=point_order_mode,
            )

    for index in range(warmup):
        print(f"[goal3244] RTDL {workload} warmup {index + 1}/{warmup}", flush=True)
        one()
    for index in range(repeat):
        print(f"[goal3244] RTDL {workload} repeat {index + 1}/{repeat}", flush=True)
        payload = one()
        phases = dict(payload.get("phases_sec") or {})
        summary = dict(payload.get("summary") or {})
        query_sec.append(float(phases.get("prepared_query_sec", 0.0)))
        if "validation_exact_query_sec" in phases:
            validation_exact_query_sec.append(float(phases["validation_exact_query_sec"]))
        query_pack_sec.append(float(phases.get("query_pack_sec", 0.0)))
        prepare_sec.append(float(phases.get("prepare_static_scene_sec", 0.0)))
        static_shape_pack_sec.append(float(phases.get("static_shape_pack_sec", 0.0)))
        counts.append(int(payload.get("row_count", 0)))
        native_phase_samples.append(payload.get("native_phase_timings"))
        expected_key = "intersection_count" if workload == "lsi" else "positive_assignment_count"
        if expected_key in summary and int(summary[expected_key]) != int(payload.get("row_count", 0)):
            raise RuntimeError(f"{workload}: summary count does not match row_count")
        if count_mode in {
            "device_filtered_validated",
            "point_id_count_device_columns_validated",
        } and not summary.get("device_filtered_count_matches_exact"):
            raise RuntimeError(f"{workload}: validated device-side count was not validated against exact count")

    return {
        "system": "rtdl_prepared_optix",
        "workload": workload,
        "route": "prepared_optix",
        "result_mode": "count",
        "count_mode": count_mode,
        "query_axis": query_axis,
        "device_filtered_boundary_mode": (
            boundary_mode
            if count_mode in {
                "device_filtered_validated",
                "point_id_count_device_columns_validated",
            }
            else None
        ),
        "point_order_mode": point_order_mode if workload == "pip" else None,
        "warmup": int(warmup),
        "repeat": int(repeat),
        "prepared_query_ms": summarize_samples([value * 1000.0 for value in query_sec]),
        "validation_exact_query_ms": summarize_samples([value * 1000.0 for value in validation_exact_query_sec]),
        "query_pack_ms": summarize_samples([value * 1000.0 for value in query_pack_sec]),
        "prepare_static_scene_ms": summarize_samples([value * 1000.0 for value in prepare_sec]),
        "static_shape_pack_ms": summarize_samples([value * 1000.0 for value in static_shape_pack_sec if value != 0.0]),
        "counts": summarize_int_samples(counts),
        "native_phase_samples": native_phase_samples,
    }


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return float(numerator / denominator)


def build_comparison_rows(rayjoin_rows: dict[str, dict[str, Any]], rtdl_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workload in ("lsi", "pip"):
        ray = rayjoin_rows[workload]
        rtdl = rtdl_rows[workload]
        ray_ms = ray["query_ms_reported"]["median"]
        rtdl_ms = rtdl["prepared_query_ms"]["median"]
        rows.append(
            {
                "workload": workload,
                "rayjoin_query_ms_reported_median": ray_ms,
                "rtdl_prepared_query_ms_median": rtdl_ms,
                "rtdl_over_rayjoin_query_ratio": ratio(rtdl_ms, ray_ms),
                "rayjoin_visible_count": ray["intersection_counts"]["last"] if workload == "lsi" else None,
                "rayjoin_positive_assignment_count_available": False if workload == "pip" else None,
                "rtdl_count": rtdl["counts"]["last"],
                "count_contract_status": (
                    "matching_visible_lsi_count"
                    if workload == "lsi" and ray["intersection_counts"]["last"] == rtdl["counts"]["last"]
                    else "rayjoin_pip_count_not_visible"
                    if workload == "pip"
                    else "count_mismatch_or_missing"
                ),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3244 repeated RTDL/RayJoin same-slice count runner.")
    parser.add_argument("--rayjoin-query-exec", type=Path, required=True)
    parser.add_argument("--rayjoin-data-dir", type=Path, required=True)
    parser.add_argument(
        "--rayjoin-lsi-poly1",
        type=Path,
        help="Optional RayJoin LSI poly1 input. Defaults to the historical Goal3244 county slice.",
    )
    parser.add_argument(
        "--rayjoin-lsi-poly2",
        type=Path,
        help="Optional RayJoin LSI poly2 input. Defaults to the historical Goal3244 soil slice.",
    )
    parser.add_argument(
        "--rayjoin-pip-poly1",
        type=Path,
        help="Optional RayJoin PIP poly1 input. Defaults to the historical Goal3244 county slice.",
    )
    parser.add_argument(
        "--rayjoin-pip-poly2",
        type=Path,
        help="Optional RayJoin PIP poly2 input. Defaults to the historical Goal3244 county slice.",
    )
    parser.add_argument("--rtdl-lsi-dataset", required=True)
    parser.add_argument("--rtdl-pip-dataset", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path)
    parser.add_argument("--rayjoin-warmup", type=int, default=3)
    parser.add_argument("--rayjoin-repeat", type=int, default=15)
    parser.add_argument("--rayjoin-process-repeats", type=int, default=5)
    parser.add_argument("--rtdl-warmup", type=int, default=2)
    parser.add_argument("--rtdl-repeat", type=int, default=7)
    parser.add_argument(
        "--rtdl-pip-count-mode",
        choices=("exact", "device_filtered_validated", "point_id_count_device_columns_validated"),
        default="exact",
        help=(
            "RTDL PIP count mode. Validated device-side modes time the selected device-side count "
            "only after each sample validates it against the exact prepared count."
        ),
    )
    parser.add_argument(
        "--rtdl-pip-query-axis",
        choices=("z_point", "z", "point_z", "aabb_point", "vertical", "y_segment", "default"),
        help=(
            "Optional generic closed-shape membership query-axis specialization for RTDL PIP. "
            "When set, the runner records it in the artifact and exports "
            "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS only around RTDL PIP calls."
        ),
    )
    parser.add_argument(
        "--rtdl-pip-boundary-mode",
        choices=("inclusive", "crossing_only"),
        help=(
            "Optional boundary mode for the RTDL PIP device-filtered count lane. "
            "The app still validates each sample against an inclusive exact prepared count."
        ),
    )
    parser.add_argument(
        "--rtdl-pip-point-order",
        choices=("natural", "x_then_y", "y_then_x", "morton_xy"),
        default="natural",
        help=(
            "Optional generic PIP probe ordering before point packing. "
            "Caller point ids are preserved; artifacts record the selected order."
        ),
    )
    parser.add_argument("--timeout-seconds", type=int, default=int(os.environ.get("STEP_TIMEOUT_SECONDS", "300")))
    args = parser.parse_args(argv)

    if args.rayjoin_process_repeats <= 0 or args.rtdl_repeat <= 0:
        raise ValueError("repeat counts must be positive")
    log_dir = args.log_dir or args.output.with_suffix("")
    log_dir.mkdir(parents=True, exist_ok=True)

    rayjoin_rows = {
        workload: run_rayjoin_process_samples(
            query_exec=args.rayjoin_query_exec,
            workload=workload,
            data_dir=args.rayjoin_data_dir,
            poly1_override=args.rayjoin_lsi_poly1 if workload == "lsi" else args.rayjoin_pip_poly1,
            poly2_override=args.rayjoin_lsi_poly2 if workload == "lsi" else args.rayjoin_pip_poly2,
            warmup=args.rayjoin_warmup,
            repeat=args.rayjoin_repeat,
            process_repeats=args.rayjoin_process_repeats,
            timeout_seconds=args.timeout_seconds,
            log_dir=log_dir,
        )
        for workload in ("lsi", "pip")
    }
    rtdl_rows = {
        "lsi": run_rtdl_samples(
            workload="lsi",
            dataset=args.rtdl_lsi_dataset,
            warmup=args.rtdl_warmup,
            repeat=args.rtdl_repeat,
        ),
        "pip": run_rtdl_samples(
            workload="pip",
            dataset=args.rtdl_pip_dataset,
            warmup=args.rtdl_warmup,
            repeat=args.rtdl_repeat,
            count_mode=args.rtdl_pip_count_mode,
            query_axis=args.rtdl_pip_query_axis,
            boundary_mode=args.rtdl_pip_boundary_mode,
            point_order_mode=args.rtdl_pip_point_order,
        ),
    }
    comparisons = build_comparison_rows(rayjoin_rows, rtdl_rows)
    status = (
        "pass_with_optimization_gap"
        if all(row["count_contract_status"] in {"matching_visible_lsi_count", "rayjoin_pip_count_not_visible"} for row in comparisons)
        else "needs_more_evidence"
    )
    payload = {
        "goal": 3244,
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "rtdl_commit": _git_commit(),
        "source_dirty": _git_dirty(),
        "gpu": _gpu_name(),
        "rayjoin": rayjoin_rows,
        "rtdl": rtdl_rows,
        "comparisons": comparisons,
        "interpretation": {
            "scope": "Repeated bounded same-slice query/count timing for RayJoin query_exec RT and RTDL prepared OptiX count.",
            "rayjoin_query_timing_semantics": "RayJoin query_exec reports a query timing after its own warmup/repeat loop; Goal3244 records that reported timing directly and does not divide it by repeat.",
            "pip_count_boundary": "RayJoin query_exec PIP still does not expose positive assignment count in this unpatched upstream binary.",
            "rtdl_pip_count_mode": (
                "When set to a validated device-side mode, RTDL validates each PIP sample with exact prepared count "
                "and reports the selected device-side count timing as the prepared_query_ms lane."
            ),
            "rtdl_pip_query_axis": (
                "When --rtdl-pip-query-axis is supplied, the runner exports "
                "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS around RTDL PIP calls and records the chosen generic mode."
            ),
            "rtdl_pip_boundary_mode": (
                "When --rtdl-pip-boundary-mode is supplied with device_filtered_validated, "
                "the app runs the exact validation count with inclusive boundary checks and runs only the "
                "device-filtered timing lane with the requested generic boundary mode."
            ),
            "rtdl_pip_point_order": (
                "When --rtdl-pip-point-order is supplied, the app reorders only PIP probe points before "
                "packing while preserving caller point ids; this is a generic locality probe, not a "
                "RayJoin-specific native engine path."
            ),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0 if status in {"pass_with_optimization_gap", "pass"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
