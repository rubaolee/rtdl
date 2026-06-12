#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    rayjoin_point_location_positive_hits_reference,
)
from examples.reference.rtdl_language_reference import county_zip_join_reference  # noqa: E402
from rtdsl.baseline_runner import segments_from_records  # noqa: E402
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import chains_to_segments  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.optix_runtime import pack_points  # noqa: E402
from rtdsl.optix_runtime import pack_polygons  # noqa: E402
from rtdsl.optix_runtime import pack_segments  # noqa: E402
from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix  # noqa: E402
from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix  # noqa: E402
from scripts.goal2192_rayjoin_same_query_stream_runner import _stream_points  # noqa: E402
from scripts.goal2192_rayjoin_same_query_stream_runner import _stream_segments  # noqa: E402
from scripts.goal2192_rayjoin_same_query_stream_runner import load_query_stream  # noqa: E402
from scripts.goal2201_rayjoin_same_query_evidence_report import parse_rayjoin_log  # noqa: E402


SCHEMA = "rtdl.goal4354.rayjoin_original_vs_rtdl_same_stream_scalar_count.v1"
WORKLOADS = ("lsi", "pip")
RAYJOIN_MODES = ("grid", "lbvh", "rt")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize an empty timing list")
    return float(statistics.median(values))


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.{digits}f}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return str(value)


def _phase(label: str, fn: Callable[[], Any]) -> tuple[float, Any]:
    start = time.perf_counter()
    value = fn()
    elapsed = time.perf_counter() - start
    print(f"[goal4354] {label} elapsed={elapsed:.6f}s", flush=True)
    return elapsed, value


def _extract_row_count(value: Any) -> int:
    if isinstance(value, dict):
        for key in ("row_count", "count"):
            if key in value:
                return int(value[key])
    return int(value)


def _run_repeats(
    *,
    label: str,
    warmups: int,
    repeats: int,
    fn: Callable[[], Any],
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    measured_sec: list[float] = []
    measured_counts: list[int] = []
    native_traversal_sec: list[float] = []
    for index in range(warmups + repeats):
        start = time.perf_counter()
        value = fn()
        elapsed = time.perf_counter() - start
        row_count = _extract_row_count(value)
        is_warmup = index < warmups
        print(
            f"[goal4354] {label} {'warmup' if is_warmup else 'repeat'} "
            f"{index + 1}/{warmups + repeats} elapsed={elapsed:.6f}s row_count={row_count}",
            flush=True,
        )
        run: dict[str, Any] = {
            "iteration": index,
            "is_warmup": is_warmup,
            "elapsed_sec": float(elapsed),
            "row_count": row_count,
        }
        if isinstance(value, dict):
            for key, item in value.items():
                if key not in {"row_count", "count"}:
                    run[key] = _json_safe(item)
            if "native_traversal_seconds" in value:
                native_traversal_sec.append(float(value["native_traversal_seconds"]))
            if "traversal_seconds" in value:
                native_traversal_sec.append(float(value["traversal_seconds"]))
        runs.append(run)
        if not is_warmup:
            measured_sec.append(float(elapsed))
            measured_counts.append(row_count)

    if len(set(measured_counts)) != 1:
        raise RuntimeError(f"{label} row count changed across measured repeats: {measured_counts}")
    return {
        "warmups": int(warmups),
        "repeats": int(repeats),
        "hot_median_sec": _median(measured_sec),
        "hot_total_sec": float(sum(measured_sec)),
        "hot_min_sec": float(min(measured_sec)),
        "hot_max_sec": float(max(measured_sec)),
        "hot_repeat_secs": measured_sec,
        "row_count": int(measured_counts[-1]),
        "counts_stable": True,
        "native_traversal_median_sec": _median(native_traversal_sec) if native_traversal_sec else None,
        "runs": runs,
    }


def _resolve(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def _find_stream(artifact_dir: Path, workload: str) -> Path:
    candidates = sorted(artifact_dir.glob(f"rayjoin_{workload}_*_stream.json"))
    if not candidates:
        raise FileNotFoundError(f"missing RayJoin-exported {workload} stream in {artifact_dir}")
    if len(candidates) > 1:
        exact = sorted(artifact_dir.glob(f"rayjoin_{workload}_gen100000_stream.json"))
        if len(exact) == 1:
            return exact[0]
        raise RuntimeError(f"multiple RayJoin {workload} streams found: {candidates}")
    return candidates[0]


def _load_base(stream: dict[str, Any]):
    base = Path(str(stream["base_cdb"]))
    if not base.is_absolute():
        base = _resolve(base)
    return load_cdb(base)


def _input_shape(workload: str, stream: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    if workload == "lsi":
        return {
            "query_count": int(stream["query_count"]),
            "left_segments": len(inputs["left"]),
            "right_segments": len(inputs["right"]),
            "base_cdb": str(stream["base_cdb"]),
        }
    return {
        "query_count": int(stream["query_count"]),
        "points": len(inputs["points"]),
        "polygons": len(inputs["polygons"]),
        "base_cdb": str(stream["base_cdb"]),
    }


def _inputs_from_stream(stream: dict[str, Any]) -> dict[str, Any]:
    base = _load_base(stream)
    if stream["workload"] == "lsi":
        return {
            "left": _stream_segments(stream),
            "right": segments_from_records(chains_to_segments(base)),
        }
    return {
        "points": _stream_points(stream),
        "polygons": chains_to_polygons(base),
    }


def _run_lsi_optix(stream: dict[str, Any], *, warmups: int, repeats: int) -> dict[str, Any]:
    inputs = _inputs_from_stream(stream)
    phases: dict[str, float] = {}
    phases["query_pack_sec"], packed_left = _phase(
        "lsi optix pack left/query segments",
        lambda: pack_segments(records=inputs["left"]),
    )
    phases["static_segment_pack_sec"], packed_right = _phase(
        "lsi optix pack right/static segments",
        lambda: pack_segments(records=inputs["right"]),
    )
    phases["prepare_static_scene_sec"], prepared = _phase(
        "lsi optix prepare static scene",
        lambda: prepare_segment_pair_intersection_optix(packed_right),
    )
    phases["prepare_left_set_sec"], prepared_left = _phase(
        "lsi optix prepare left query set",
        lambda: prepare_segment_pair_left_set_optix(packed_left),
    )
    try:
        def run_once() -> dict[str, Any]:
            result = prepared.count_prepared_left_exact_intersections(prepared_left)
            return {
                "row_count": int(result["count"]),
                "right_group_count": int(result["right_group_count"]),
                "route": result["route"],
                "native_symbol": result["native_symbol"],
                "row_stream_materialized": False,
            }

        timing = _run_repeats(
            label="lsi/rtdl_optix_prepared_left_exact_count",
            warmups=warmups,
            repeats=repeats,
            fn=run_once,
        )
    finally:
        prepared_left.close()
        prepared.close()

    return {
        "backend": "optix",
        "execution_route": "prepared_left_exact_segment_pair_scalar_count",
        "rt_core_accelerated": True,
        "row_stream_materialized": False,
        "input_shape": _input_shape("lsi", stream, inputs),
        "prepare_sec": phases,
        "timing": timing,
        "row_count": int(timing["row_count"]),
        "hot_median_sec": float(timing["hot_median_sec"]),
        "output_contract": "scalar_exact_count",
    }


def _run_pip_optix(
    stream: dict[str, Any],
    *,
    warmups: int,
    repeats: int,
    point_eps: float,
    include_fast_diagnostic: bool,
) -> dict[str, Any]:
    inputs = _inputs_from_stream(stream)
    phases: dict[str, float] = {}
    phases["query_point_pack_sec"], packed_points = _phase(
        "pip optix pack query points",
        lambda: pack_points(records=inputs["points"], dimension=2),
    )
    phases["static_shape_pack_sec"], packed_shapes = _phase(
        "pip optix pack static polygons",
        lambda: pack_polygons(records=inputs["polygons"]),
    )
    phases["prepare_static_scene_sec"], prepared = _phase(
        "pip optix prepare static scene",
        lambda: prepare_point_closed_shape_membership_2d_optix(packed_shapes),
    )
    diagnostics: dict[str, Any] = {}
    try:
        def run_once() -> dict[str, Any]:
            return {
                "row_count": int(prepared.count(packed_points)),
                "row_stream_materialized": False,
                "exact_host_refined_scalar_count": True,
                "native_symbol": "rtdl_optix_count_prepared_point_closed_shape_membership_2d",
            }

        timing = _run_repeats(
            label="pip/rtdl_optix_exact_scalar_count",
            warmups=warmups,
            repeats=repeats,
            fn=run_once,
        )

        if include_fast_diagnostic:
            diagnostic_phases: dict[str, float] = {}
            prepared_points = None
            executor = None
            diagnostic_phases["prepare_query_points_sec"], prepared_points = _phase(
                "pip optix diagnostic prepare query point columns",
                lambda: prepared.prepare_point_probe_columns(packed_points),
            )
            diagnostic_phases["prepare_scalar_count_executor_sec"], executor = _phase(
                "pip optix diagnostic prepare native scalar-count executor",
                lambda: prepared.prepare_relation_status_corrected_scalar_count_executor(
                    prepared_points,
                    point_eps=point_eps,
                ),
            )
            try:
                diagnostic_phases["device_filtered_prepared_points_sec"], device_filtered = _phase(
                    "pip optix diagnostic device-filtered prepared-points count",
                    lambda: prepared.count_device_filtered_prepared_points(prepared_points),
                )
                diagnostic_phases["relation_status_executor_sec"], status_result = _phase(
                    "pip optix diagnostic relation-status corrected executor count",
                    lambda: executor.run(),
                )
                diagnostics["rejected_fast_route"] = {
                    "not_used_for_speedup": True,
                    "reason": "same-stream PIP count did not match exact prepared.count/Embree semantics",
                    "exact_row_count": int(timing["row_count"]),
                    "device_filtered_prepared_points_count": int(device_filtered),
                    "relation_status_corrected_row_count": int(status_result["row_count"]),
                    "candidate_row_count": int(status_result["candidate_row_count"]),
                    "boundary_candidate_row_count": int(status_result["boundary_candidate_row_count"]),
                    "dropped_candidate_row_count": int(status_result["dropped_candidate_row_count"]),
                    "native_traversal_seconds": float(status_result["traversal_seconds"]),
                    "diagnostic_phases_sec": diagnostic_phases,
                }
            finally:
                if executor is not None:
                    executor.close()
                if prepared_points is not None:
                    prepared_points.close()
    finally:
        prepared.close()

    return {
        "backend": "optix",
        "execution_route": "prepared_exact_closed_shape_membership_scalar_count",
        "rt_core_accelerated": True,
        "row_stream_materialized": False,
        "input_shape": _input_shape("pip", stream, inputs),
        "prepare_sec": phases,
        "diagnostics": diagnostics,
        "timing": timing,
        "row_count": int(timing["row_count"]),
        "hot_median_sec": float(timing["hot_median_sec"]),
        "output_contract": "scalar_exact_positive_membership_count",
    }


def _run_embree(
    workload: str,
    stream: dict[str, Any],
    *,
    warmups: int,
    repeats: int,
) -> dict[str, Any]:
    inputs = _inputs_from_stream(stream)
    kernel = rayjoin_point_location_positive_hits_reference if workload == "pip" else county_zip_join_reference
    phases: dict[str, float] = {}
    phases["prepare_kernel_sec"], prepared_kernel = _phase(
        f"{workload} embree prepare kernel",
        lambda: rt.prepare_embree(kernel),
    )
    phases["bind_inputs_sec"], prepared = _phase(
        f"{workload} embree bind inputs",
        lambda: prepared_kernel.bind(**inputs),
    )
    try:
        def run_once() -> dict[str, Any]:
            count = prepared.count(require_prepared=True)
            return {
                "row_count": int(count),
                "native_traversal_seconds": float(prepared.last_count_traversal_seconds),
                "row_stream_materialized": False,
            }

        timing = _run_repeats(
            label=f"{workload}/rtdl_embree_prepared_scalar_count",
            warmups=warmups,
            repeats=repeats,
            fn=run_once,
        )
    finally:
        prepared.close()

    return {
        "backend": "embree",
        "execution_route": "prepared_embree_native_scalar_count",
        "rt_core_accelerated": False,
        "row_stream_materialized": False,
        "input_shape": _input_shape(workload, stream, inputs),
        "prepare_sec": phases,
        "timing": timing,
        "row_count": int(timing["row_count"]),
        "hot_median_sec": float(timing["hot_median_sec"]),
        "output_contract": "scalar_count",
    }


def _parse_rayjoin(artifact_dir: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for workload in WORKLOADS:
        rows[workload] = {}
        for mode in RAYJOIN_MODES:
            rows[workload][mode] = parse_rayjoin_log(artifact_dir / f"rayjoin_{workload}_{mode}.log")
    return rows


def _correctness_for_workload(
    workload: str,
    rayjoin: dict[str, Any],
    backends: dict[str, Any],
) -> dict[str, Any]:
    counts = {name: int(row["row_count"]) for name, row in backends.items()}
    cross_backend_counts_match = len(set(counts.values())) <= 1
    rayjoin_rt = rayjoin[workload]["rt"]
    if workload == "lsi":
        rayjoin_count = rayjoin_rt.get("intersections")
        return {
            "rtdl_backend_counts": counts,
            "cross_backend_counts_match": cross_backend_counts_match,
            "rayjoin_rt_intersections": rayjoin_count,
            "rtdl_matches_rayjoin_rt_intersections": (
                rayjoin_count is not None and all(value == int(rayjoin_count) for value in counts.values())
            ),
        }
    return {
        "rtdl_backend_counts": counts,
        "cross_backend_counts_match": cross_backend_counts_match,
        "rayjoin_rt_builtin_check_passed": bool(rayjoin_rt.get("built_in_check_passed")),
        "rayjoin_pip_count_available_in_log": False,
    }


def _build_payload(args: argparse.Namespace) -> dict[str, Any]:
    artifact_dir = _resolve(args.artifact_dir)
    workloads = tuple(item.strip() for item in args.workloads.split(",") if item.strip())
    invalid = sorted(set(workloads) - set(WORKLOADS))
    if invalid:
        raise ValueError(f"invalid workloads: {invalid}")
    rayjoin = _parse_rayjoin(artifact_dir)
    rtdl: dict[str, Any] = {}
    for workload in workloads:
        stream_path = _find_stream(artifact_dir, workload)
        stream = load_query_stream(stream_path)
        if stream["producer"] != "rayjoin_query_exec_export_patch":
            raise ValueError(f"{stream_path} is not a RayJoin query_exec exported stream")
        backends: dict[str, Any] = {}
        if workload == "lsi":
            backends["optix"] = _run_lsi_optix(stream, warmups=args.warmups, repeats=args.repeats)
        else:
            backends["optix"] = _run_pip_optix(
                stream,
                warmups=args.warmups,
                repeats=args.repeats,
                point_eps=args.point_eps,
                include_fast_diagnostic=args.include_pip_fast_diagnostic,
            )
        if args.include_embree:
            embree_warmups = args.embree_warmups if args.embree_warmups is not None else args.warmups
            embree_repeats = args.embree_repeats if args.embree_repeats is not None else args.repeats
            backends["embree"] = _run_embree(
                workload,
                stream,
                warmups=embree_warmups,
                repeats=embree_repeats,
            )
        rtdl[workload] = {
            "query_stream": str(stream_path),
            "query_stream_schema": stream["schema"],
            "query_stream_producer": stream["producer"],
            "workload": workload,
            "query_count": int(stream["query_count"]),
            "base_cdb": str(stream["base_cdb"]),
            "backends": backends,
            "correctness": _correctness_for_workload(workload, rayjoin, backends),
        }

    comparisons: list[dict[str, Any]] = []
    for workload, row in rtdl.items():
        rayjoin_rt_ms = rayjoin[workload]["rt"].get("query_ms")
        for backend, backend_row in row["backends"].items():
            rtdl_ms = float(backend_row["hot_median_sec"]) * 1000.0
            comparisons.append(
                {
                    "workload": workload,
                    "backend": backend,
                    "rayjoin_rt_query_ms": rayjoin_rt_ms,
                    "rtdl_hot_query_ms": rtdl_ms,
                    "rayjoin_rt_over_rtdl": (
                        float(rayjoin_rt_ms) / rtdl_ms if rayjoin_rt_ms is not None and rtdl_ms > 0.0 else None
                    ),
                    "meaning": "greater_than_1_means_rtdl_backend_faster_than_rayjoin_rt",
                }
            )

    return {
        "schema": SCHEMA,
        "generated_at_utc": _utc_now(),
        "artifact_dir": str(artifact_dir),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short", "--untracked-files=no"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cuda": _command_output(["nvcc", "--version"]),
        "protocol": {
            "rayjoin_source": "external RayJoin query_exec built from upstream commit 02bf6220d6d20b04af77ee20364eced75cc029c9 plus query stream export patch",
            "dataset_basis": "RayJoin official sample base CDB/path from exported stream",
            "query_basis": "same RayJoin-exported query stream consumed by RTDL",
            "timed_metric": "hot scalar-count query phase; no Python row materialization in RTDL measured path",
            "rayjoin_timing_basis": "RayJoin query_exec reported Query ms from log",
            "rtdl_timing_basis": "Python wall time around current prepared native scalar-count front door",
            "warmups": int(args.warmups),
            "repeats": int(args.repeats),
            "include_embree": bool(args.include_embree),
        },
        "rayjoin": rayjoin,
        "rtdl": rtdl,
        "comparisons": comparisons,
        "claim_boundary": {
            "same_query_stream_with_rayjoin_query_exec": True,
            "full_rayjoin_paper_reproduction": False,
            "whole_application_end_to_end_claim": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "public_paper_claim_authorized": False,
        },
    }


def _ratio_text(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}x"


def _render_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Goal4354 RayJoin Original vs RTDL+Partner Same-Stream Comparison",
        "",
        "Status: measured on the pod from RayJoin-exported query streams. Speedup column is "
        "`RayJoin RT Query ms / RTDL hot query ms`; values above 1 mean RTDL is faster.",
        "",
        "## Scope",
        "",
        "- RayJoin side: original `query_exec` logs for `grid`, `lbvh`, and `rt` modes.",
        "- RTDL side: current prepared scalar-count hot paths, consuming the same exported queries.",
        "- Contract: scalar count only; RTDL measured paths do not materialize match rows.",
        "- Boundary: this is not a full RayJoin paper reproduction claim.",
        "",
        "## RayJoin Original Logs",
        "",
        "| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for workload in WORKLOADS:
        if workload not in payload["rayjoin"]:
            continue
        for mode in RAYJOIN_MODES:
            row = payload["rayjoin"][workload][mode]
            lines.append(
                "| "
                f"`{workload}` | `{mode}` | {_fmt(row.get('query_ms'), 6)} | "
                f"{_fmt(row.get('build_index_ms'), 6)} | {_fmt(row.get('adaptive_grouping_ms'), 6)} | "
                f"{row.get('optix_launch_count')} | "
                f"{row.get('intersections') if row.get('intersections') is not None else 'n/a'} | "
                f"{'pass' if row.get('built_in_check_passed') else 'n/a'} |"
            )

    lines.extend(
        [
            "",
            "## RTDL Same-Stream Results",
            "",
            "| Workload | Backend | Query count | Row count | Hot median ms | Hot total s | Repeats | Native traversal ms | Route |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for workload, row in payload["rtdl"].items():
        for backend, backend_row in row["backends"].items():
            timing = backend_row["timing"]
            native_ms = (
                float(timing["native_traversal_median_sec"]) * 1000.0
                if timing.get("native_traversal_median_sec") is not None
                else None
            )
            lines.append(
                "| "
                f"`{workload}` | `{backend}` | {row['query_count']} | {backend_row['row_count']} | "
                f"{_fmt(float(backend_row['hot_median_sec']) * 1000.0, 6)} | "
                f"{_fmt(timing['hot_total_sec'], 6)} | {timing['repeats']} | "
                f"{_fmt(native_ms, 6)} | `{backend_row['execution_route']}` |"
            )

    lines.extend(
        [
            "",
            "## Direct Comparison",
            "",
            "| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | Speedup | Readout |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["comparisons"]:
        ratio = row["rayjoin_rt_over_rtdl"]
        if ratio is None:
            readout = "not comparable"
        elif ratio >= 1.05:
            readout = "RTDL faster on the same stream"
        elif ratio <= 0.95:
            readout = "RayJoin RT faster on the same stream"
        else:
            readout = "roughly tied on the same stream"
        lines.append(
            "| "
            f"`{row['workload']}` | `{row['backend']}` | {_fmt(row['rayjoin_rt_query_ms'], 6)} | "
            f"{_fmt(row['rtdl_hot_query_ms'], 6)} | {_ratio_text(ratio)} | {readout} |"
        )

    lines.extend(
        [
            "",
            "## Correctness Checks",
            "",
            "| Workload | RTDL counts | Cross-backend match | External check |",
            "| --- | --- | --- | --- |",
        ]
    )
    for workload, row in payload["rtdl"].items():
        correctness = row["correctness"]
        counts = ", ".join(f"{key}={value}" for key, value in correctness["rtdl_backend_counts"].items())
        if workload == "lsi":
            external = (
                f"RayJoin RT intersections={correctness['rayjoin_rt_intersections']}; "
                f"match={correctness['rtdl_matches_rayjoin_rt_intersections']}"
            )
        else:
            external = (
                "RayJoin RT built-in check="
                f"{correctness['rayjoin_rt_builtin_check_passed']}; "
                "RayJoin PIP log has no exported count"
            )
        lines.append(
            "| "
            f"`{workload}` | {counts} | {correctness['cross_backend_counts_match']} | {external} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Notes",
            "",
            "- `lsi`: the RTDL route is the current exact prepared-left segment-pair scalar count front door.",
            "- `pip`: the RTDL route is the exact prepared closed-shape scalar count. The faster relation-status executor is recorded only as a rejected diagnostic when it disagrees with exact semantics.",
            "- Differences versus RayJoin RT can come from specialization: RayJoin is a purpose-built C++/CUDA/OptiX program, while RTDL keeps a generic runtime contract and Python front-door orchestration outside the timed native call.",
            "- The table separates hot query time from one-time pack/prepare work in the JSON artifact.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare RayJoin original query_exec with current RTDL same-stream scalar counts.")
    parser.add_argument("--artifact-dir", required=True, help="Directory containing rayjoin_* logs and exported streams.")
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--workloads", default="lsi,pip")
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--include-embree", action="store_true")
    parser.add_argument("--embree-warmups", type=int, default=None)
    parser.add_argument("--embree-repeats", type=int, default=None)
    parser.add_argument("--include-pip-fast-diagnostic", action="store_true")
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    args = parser.parse_args()
    if args.warmups < 0 or args.repeats <= 0:
        raise ValueError("--warmups must be non-negative and --repeats must be positive")
    if args.embree_warmups is not None and args.embree_warmups < 0:
        raise ValueError("--embree-warmups must be non-negative")
    if args.embree_repeats is not None and args.embree_repeats <= 0:
        raise ValueError("--embree-repeats must be positive")
    artifact_dir = _resolve(args.artifact_dir)
    if args.output_json is None:
        args.output_json = artifact_dir / "goal4354_rayjoin_original_vs_rtdl_same_stream_summary.json"
    if args.output_md is None:
        args.output_md = artifact_dir / "goal4354_rayjoin_original_vs_rtdl_same_stream_summary.md"
    return args


def main() -> int:
    args = parse_args()
    payload = _build_payload(args)
    output_json = _resolve(args.output_json)
    output_md = _resolve(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    output_md.write_text(_render_markdown(payload), encoding="utf-8")
    print(f"[goal4354] wrote {output_json}", flush=True)
    print(f"[goal4354] wrote {output_md}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
