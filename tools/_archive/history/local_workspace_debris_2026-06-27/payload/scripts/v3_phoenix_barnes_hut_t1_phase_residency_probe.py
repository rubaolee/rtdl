#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.barnes_hut import (  # noqa: E402
    rtdl_barnes_hut_benchmark_app as barnes_app,
)


SCHEMA = "rtdl.phoenix_v3.barnes_hut_t1_phase_residency_probe.v1"
STATUS = "barnes_hut_t1_phase_residency_probe_collected_not_release"
SCORECARD_BLOCKER_ID = "set_a_barnes_hut_app_geomean_0_844x"
SCORECARD_CURRENT_VALUE = 0.8441965065233041
SCORECARD_SOURCE = "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md"

HISTORICAL_OPTIX = "historical_prepared_optix_frontier_numba_reference"
FUSED_CONTROL = "existing_app_front_door_fused_numba_cuda_control"
RUNNER = "runner_prepared_execution_fused_numba_cuda"
NATIVE_RT_ATTEMPT = "native_rt_fused_optix_attempt"

ROUTE_MODES = {
    HISTORICAL_OPTIX: "prepared_aggregate_frontier_weighted_vector_optix",
    FUSED_CONTROL: "fused_frontier_force_sum_bucketized_numba_cuda",
    RUNNER: "prepared_execution_fused_vector_sum_numba_cuda",
}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_packet(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_ready(payload["summary"]), indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phoenix V3 Barnes-Hut T1 focused probe: phase/residency diagnosis "
            "for the 0.844x scorecard blocker. This is measurement only, not a "
            "release or all-app authorization."
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--body-counts", type=int, nargs="+", default=[32768, 65536, 131072])
    parser.add_argument("--query-repeat", type=int, default=11)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--frontier-capacity-multiplier", type=int, default=700)
    parser.add_argument(
        "--skip-native-rt-attempt",
        action="store_true",
        help="Skip the native RT fused fail-closed probe.",
    )
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    routes = [HISTORICAL_OPTIX, FUSED_CONTROL, RUNNER]
    if not bool(args.skip_native_rt_attempt):
        routes.append(NATIVE_RT_ATTEMPT)

    for body_count in [int(value) for value in args.body_counts]:
        for sample in range(1, int(args.samples) + 1):
            for route_id in routes:
                print(
                    "[phoenix-v3-barnes-t1] "
                    f"{route_id} body_count={body_count} sample={sample}/{int(args.samples)} "
                    f"repeat={int(args.query_repeat)} warmup={int(args.warmup)}",
                    flush=True,
                )
                output_path = args.output_dir / f"{route_id}_{body_count}_s{sample:02d}.json"
                if route_id == NATIVE_RT_ATTEMPT:
                    row, payload = _run_native_rt_attempt(
                        args,
                        body_count=body_count,
                        sample=sample,
                        output_path=output_path,
                    )
                else:
                    row, payload = _run_benchmark_route(
                        args,
                        body_count=body_count,
                        route_id=route_id,
                        sample=sample,
                        output_path=output_path,
                    )
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(
                    json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                rows.append(row)

    route_summaries = _summarize_routes(rows)
    comparison_rows = _build_comparison_rows(route_summaries)
    diagnosis = _diagnose(route_summaries, comparison_rows)
    checks = _build_checks(rows, comparison_rows)
    failed_checks = [name for name, ok in checks.items() if not ok]
    payload = {
        "schema": SCHEMA,
        "status": "fail" if failed_checks else STATUS,
        "summary": {
            "status": STATUS,
            "scorecard_blocker": {
                "id": SCORECARD_BLOCKER_ID,
                "set": "A",
                "app": "barnes_hut",
                "metric": "set_a_app_geomean_v3_vs_v2_14",
                "current_value": SCORECARD_CURRENT_VALUE,
                "source": SCORECARD_SOURCE,
                "target": "move_toward_or_above_parity",
            },
            "body_counts": [int(value) for value in args.body_counts],
            "samples": int(args.samples),
            "query_repeat": int(args.query_repeat),
            "warmup": int(args.warmup),
            "theta": float(args.theta),
            "bucket_size": int(args.bucket_size),
            "max_depth": int(args.max_depth),
            "route_summaries": route_summaries,
            "comparison_rows": comparison_rows,
            "diagnosis": diagnosis,
            "release_authorized": False,
            "all_app_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "rows": rows,
        "non_authorization": {
            "release_authorized": False,
            "all_app_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
        },
    }
    return payload


def _run_benchmark_route(
    args: argparse.Namespace,
    *,
    body_count: int,
    route_id: str,
    sample: int,
    output_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    start = time.perf_counter()
    payload = barnes_app.run_benchmark(
        ROUTE_MODES[route_id],
        body_count=int(body_count),
        theta=float(args.theta),
        bucket_size=int(args.bucket_size),
        max_depth=int(args.max_depth),
        partner="numba",
        skip_validation=True,
        query_repeat=int(args.query_repeat),
        warmup=int(args.warmup),
        force_output_mode="force_summary",
        frontier_capacity_multiplier=int(args.frontier_capacity_multiplier),
    )
    process_wall_sec = time.perf_counter() - start
    return (
        _extract_route_row(
            payload,
            route_id=route_id,
            body_count=body_count,
            sample=sample,
            output_path=output_path,
            process_wall_sec=process_wall_sec,
        ),
        payload,
    )


def _run_native_rt_attempt(
    args: argparse.Namespace,
    *,
    body_count: int,
    sample: int,
    output_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    start = time.perf_counter()
    failure_reason = ""
    symbol_available = False
    runtime_implemented = False
    prepare_sec = 0.0
    payload: dict[str, Any] = {
        "app": "barnes_hut_force_app",
        "mode": NATIVE_RT_ATTEMPT,
        "body_count": int(body_count),
        "theta": float(args.theta),
        "bucket_size": int(args.bucket_size),
        "max_depth": int(args.max_depth),
    }
    try:
        bodies = barnes_app._make_bodies(body_count)  # type: ignore[attr-defined]
        tree = rt.build_bucketized_aggregate_tree_2d(
            bodies,
            bucket_size=int(args.bucket_size),
            max_depth=int(args.max_depth),
        )
        tree_nodes = tuple(tree["nodes"])
        prepare_start = time.perf_counter()
        prepared = rt.prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix(
            bodies,
            tree_nodes,
        )
        prepare_sec = time.perf_counter() - prepare_start
        symbol_available = True
        try:
            prepared.run_cupy(bodies, theta=float(args.theta), softening=barnes_app.app.SOFTENING)
            runtime_implemented = True
        finally:
            prepared.close()
    except Exception as exc:  # noqa: BLE001 - this route is an availability probe.
        failure_reason = str(exc)
        if "does not export" not in failure_reason:
            symbol_available = True
        if "not implemented yet" in failure_reason:
            runtime_implemented = False
    process_wall_sec = time.perf_counter() - start
    payload.update(
        {
            "native_rt_fused_symbol_available": symbol_available,
            "native_rt_fused_runtime_implemented": runtime_implemented,
            "native_rt_fused_failure_reason": failure_reason,
            "run_phases": {
                "prepare_attempt_wall_sec": prepare_sec,
                "total_sec": process_wall_sec,
            },
            "claim_flags": {
                "rt_cores_used": runtime_implemented,
                "rt_core_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }
    )
    row = {
        "route_id": NATIVE_RT_ATTEMPT,
        "mode": NATIVE_RT_ATTEMPT,
        "body_count": int(body_count),
        "sample": int(sample),
        "output_json": str(output_path),
        "process_wall_sec": float(process_wall_sec),
        "phase_seconds": {
            "prepare": float(prepare_sec),
            "traverse": 0.0,
            "accumulate": 0.0,
            "boundary": 0.0,
        },
        "primary_hot_call_wall_sec": None,
        "kernel_or_native_hot_sec": None,
        "runtime_executed": False,
        "internal_residency_measured": False,
        "host_materialization_in_hot_path": False,
        "win_source": "",
        "same_contract_incumbent": SCORECARD_BLOCKER_ID,
        "result_vs_incumbent": None,
        "projected_scorecard_value": None,
        "rt_cores_used": False,
        "native_rt_fused_symbol_available": bool(symbol_available),
        "native_rt_fused_runtime_implemented": bool(runtime_implemented),
        "native_rt_fused_failure_reason": failure_reason,
        "scorecard_blocker_bound": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
    }
    return row, payload


def _extract_route_row(
    payload: dict[str, Any],
    *,
    route_id: str,
    body_count: int,
    sample: int,
    output_path: Path,
    process_wall_sec: float,
) -> dict[str, Any]:
    medians = dict(payload.get("medians") or {})
    phases = dict(payload.get("run_phases") or {})
    vector_summary = dict(payload.get("vector_sum_summary") or {})
    claim_flags = dict(payload.get("claim_flags") or {})
    runner_metadata = dict(payload.get("prepared_execution_session_runner") or {})
    if route_id == HISTORICAL_OPTIX:
        primary_sec = _required_float(medians, "wall_seconds")
        kernel_sec = _required_float(medians, "hot_seconds_native_plus_partner")
        phase_seconds = {
            "prepare": _sum_optional(
                phases.get("frontier_prepare_wall_sec"),
                phases.get("vector_prepare_wall_sec"),
                phases.get("partner_prepare_seconds"),
            ),
            "traverse": _optional_float(medians.get("frontier_traversal_seconds")) or 0.0,
            "accumulate": _optional_float(medians.get("partner_seconds")) or 0.0,
            "boundary": max(0.0, primary_sec - kernel_sec),
        }
        win_source = ""
        runtime_executed = False
        scorecard_bound = False
    elif route_id == FUSED_CONTROL:
        primary_sec = _required_float(medians, "fused_numba_cuda_call_wall_seconds")
        kernel_sec = _optional_float(medians.get("fused_numba_cuda_kernel_event_seconds"))
        phase_seconds = {
            "prepare": _optional_float(phases.get("vector_prepare_sec")) or 0.0,
            "traverse": 0.0,
            "accumulate": primary_sec,
            "boundary": _optional_float(phases.get("vector_copy_to_host_sec")) or 0.0,
        }
        win_source = ""
        runtime_executed = False
        scorecard_bound = False
    elif route_id == RUNNER:
        primary_sec = _required_float(medians, "prepared_execution_runner_measured_seconds")
        kernel_sec = _optional_float(medians.get("fused_numba_cuda_kernel_event_seconds"))
        phase_seconds = {
            "prepare": _optional_float(phases.get("runner_prepare_or_cache_sec")) or 0.0,
            "traverse": 0.0,
            "accumulate": primary_sec,
            "boundary": _optional_float(phases.get("vector_copy_to_host_sec")) or 0.0,
        }
        win_source = str(runner_metadata.get("win_source") or vector_summary.get("win_source") or "")
        runtime_executed = bool(
            runner_metadata.get("runtime_trunk_executes_end_to_end")
            or runner_metadata.get("runtime_executed")
            or vector_summary.get("runtime_trunk_executes_end_to_end")
        )
        scorecard_bound = bool(
            runner_metadata.get("scorecard_blocker_bound")
            or vector_summary.get("scorecard_blocker_bound")
        )
    else:
        raise ValueError(f"unsupported route_id: {route_id}")

    frontier_materialized = bool(
        vector_summary.get("frontier_rows_materialized_on_host")
        or vector_summary.get("materialized_frontier_rows")
        or claim_flags.get("frontier_columns_materialized_on_host")
    )
    contribution_materialized = bool(
        vector_summary.get("contribution_rows_materialized_on_host")
        or vector_summary.get("materialized_contribution_rows")
        or claim_flags.get("contribution_rows_materialized_on_host")
    )
    hot_materialization = bool(
        frontier_materialized
        or contribution_materialized
        or runner_metadata.get("hot_path_host_materialization")
        or vector_summary.get("hot_path_host_materialization")
    )
    internal_residency = bool(
        vector_summary.get("prepared_lookup_columns_resident")
        and vector_summary.get("aggregate_tree_columns_resident")
        and vector_summary.get("source_columns_reused")
        and vector_summary.get("target_columns_reused")
        and not hot_materialization
    )
    if route_id == RUNNER:
        internal_residency = bool(
            internal_residency
            and runner_metadata.get("internal_device_residency_between_rtdl_phases")
        )
    return {
        "route_id": route_id,
        "mode": str(payload.get("mode") or ROUTE_MODES[route_id]),
        "body_count": int(body_count),
        "sample": int(sample),
        "output_json": str(output_path),
        "process_wall_sec": float(process_wall_sec),
        "phase_seconds": phase_seconds,
        "primary_hot_call_wall_sec": primary_sec,
        "kernel_or_native_hot_sec": kernel_sec,
        "runtime_executed": runtime_executed,
        "internal_residency_measured": internal_residency,
        "host_materialization_in_hot_path": hot_materialization,
        "win_source": win_source,
        "same_contract_incumbent": SCORECARD_BLOCKER_ID,
        "result_vs_incumbent": None,
        "projected_scorecard_value": None,
        "rt_cores_used": bool(claim_flags.get("rt_cores_used") or payload.get("rt_core_accelerated")),
        "native_rt_fused_symbol_available": None,
        "native_rt_fused_runtime_implemented": None,
        "native_rt_fused_failure_reason": "",
        "scorecard_blocker_bound": scorecard_bound,
        "tree_node_count": int(vector_summary.get("tree_node_count") or payload.get("tree_summary", {}).get("node_count") or 0),
        "contribution_row_count": int(
            vector_summary.get("contribution_row_count")
            or vector_summary.get("frontier_row_count")
            or 0
        ),
        "aggregate_contribution_row_count": int(vector_summary.get("aggregate_contribution_row_count") or 0),
        "exact_contribution_row_count": int(vector_summary.get("exact_contribution_row_count") or 0),
        "checksum_force_x": _optional_float(vector_summary.get("checksum_force_x")),
        "checksum_force_y": _optional_float(vector_summary.get("checksum_force_y")),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
    }


def _summarize_routes(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for route_id in sorted({str(row["route_id"]) for row in rows}):
        route_rows = [row for row in rows if str(row["route_id"]) == route_id]
        for body_count in sorted({int(row["body_count"]) for row in route_rows}):
            size_rows = [row for row in route_rows if int(row["body_count"]) == body_count]
            hot_values = [
                float(row["primary_hot_call_wall_sec"])
                for row in size_rows
                if row["primary_hot_call_wall_sec"] is not None
            ]
            summaries[f"{route_id}:{body_count}"] = {
                "route_id": route_id,
                "body_count": int(body_count),
                "sample_count": len(size_rows),
                "primary_hot_call_wall_sec_median": _median(hot_values),
                "process_wall_sec_median": _median([float(row["process_wall_sec"]) for row in size_rows]),
                "phase_seconds_median": _median_phase_seconds(size_rows),
                "runtime_executed_all_samples": all(bool(row["runtime_executed"]) for row in size_rows),
                "internal_residency_measured_all_samples": all(
                    bool(row["internal_residency_measured"]) for row in size_rows
                ),
                "hot_materialization_any_sample": any(
                    bool(row["host_materialization_in_hot_path"]) for row in size_rows
                ),
                "scorecard_bound_all_samples": all(bool(row["scorecard_blocker_bound"]) for row in size_rows),
                "native_rt_fused_symbol_available_any": any(
                    bool(row.get("native_rt_fused_symbol_available")) for row in size_rows
                ),
                "native_rt_fused_runtime_implemented_any": any(
                    bool(row.get("native_rt_fused_runtime_implemented")) for row in size_rows
                ),
                "native_rt_fused_failure_reasons": sorted(
                    {
                        str(row.get("native_rt_fused_failure_reason"))
                        for row in size_rows
                        if row.get("native_rt_fused_failure_reason")
                    }
                ),
            }
    return summaries


def _build_comparison_rows(route_summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    body_counts = sorted(
        {
            int(summary["body_count"])
            for summary in route_summaries.values()
            if str(summary["route_id"]) in {HISTORICAL_OPTIX, FUSED_CONTROL, RUNNER}
        }
    )
    rows: list[dict[str, Any]] = []
    for body_count in body_counts:
        historical = route_summaries.get(f"{HISTORICAL_OPTIX}:{body_count}")
        control = route_summaries.get(f"{FUSED_CONTROL}:{body_count}")
        runner = route_summaries.get(f"{RUNNER}:{body_count}")
        if control is None or runner is None:
            continue
        runner_vs_control = _ratio(
            runner.get("primary_hot_call_wall_sec_median"),
            control.get("primary_hot_call_wall_sec_median"),
        )
        historical_vs_runner = (
            _ratio(runner.get("primary_hot_call_wall_sec_median"), historical.get("primary_hot_call_wall_sec_median"))
            if historical is not None
            else None
        )
        projected = SCORECARD_CURRENT_VALUE * float(runner_vs_control) if runner_vs_control is not None else None
        rows.append(
            {
                "body_count": int(body_count),
                "runner_vs_existing_fused_control_speedup": runner_vs_control,
                "historical_optix_frontier_vs_runner_speedup": historical_vs_runner,
                "scorecard_current_value": SCORECARD_CURRENT_VALUE,
                "projected_scorecard_value_if_this_route_replaces_current_control": projected,
                "moves_0_844_blocker_toward_parity": projected is not None and projected > SCORECARD_CURRENT_VALUE,
                "crosses_parity": projected is not None and projected >= 0.98,
                "runner_sec_median": runner.get("primary_hot_call_wall_sec_median"),
                "existing_fused_control_sec_median": control.get("primary_hot_call_wall_sec_median"),
                "historical_optix_frontier_sec_median": (
                    historical.get("primary_hot_call_wall_sec_median") if historical is not None else None
                ),
            }
        )
    return rows


def _diagnose(
    route_summaries: dict[str, dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    runner_speedups = [
        float(row["runner_vs_existing_fused_control_speedup"])
        for row in comparison_rows
        if row.get("runner_vs_existing_fused_control_speedup") is not None
    ]
    projected_values = [
        float(row["projected_scorecard_value_if_this_route_replaces_current_control"])
        for row in comparison_rows
        if row.get("projected_scorecard_value_if_this_route_replaces_current_control") is not None
    ]
    native_summaries = [
        summary
        for summary in route_summaries.values()
        if str(summary["route_id"]) == NATIVE_RT_ATTEMPT
    ]
    native_runtime_implemented = any(
        bool(summary["native_rt_fused_runtime_implemented_any"])
        for summary in native_summaries
    )
    native_symbol_available = any(
        bool(summary["native_rt_fused_symbol_available_any"])
        for summary in native_summaries
    )
    runner_vs_control_geomean = _geomean(runner_speedups)
    projected_geomean = _geomean(projected_values)
    movement = projected_geomean is not None and projected_geomean > SCORECARD_CURRENT_VALUE
    crosses_parity = projected_geomean is not None and projected_geomean >= 0.98
    if not native_runtime_implemented:
        t2_action = (
            "native_rt_fused_required_before_rt_traversal_claim"
            if native_symbol_available
            else "native_rt_fused_symbol_missing_or_backend_unavailable"
        )
    elif not movement:
        t2_action = "runner_wrapper_does_not_move_blocker_revisit_kernel_or_scorecard_binding"
    else:
        t2_action = "continue_t2_route_front_door_and_confirm_scorecard_movement"
    if not movement:
        exit_statement = (
            "current scorecard metric is not moved by the existing Numba CUDA prepared-session trunk; "
            "native RT fused traversal is not live, so a true RT traversal T2 requires native implementation."
        )
    elif crosses_parity:
        exit_statement = "0.844x crosses parity under the measured prepared-session trunk replacement."
    else:
        exit_statement = "0.844x moves toward parity under the measured prepared-session trunk replacement."
    return {
        "runner_vs_existing_fused_control_geomean": runner_vs_control_geomean,
        "projected_scorecard_value_geomean": projected_geomean,
        "moves_0_844_blocker_toward_parity": movement,
        "crosses_parity": crosses_parity,
        "native_rt_fused_symbol_available": native_symbol_available,
        "native_rt_fused_runtime_implemented": native_runtime_implemented,
        "t1_exit_statement": exit_statement,
        "next_t2_action": t2_action,
    }


def _build_checks(rows: list[dict[str, Any]], comparison_rows: list[dict[str, Any]]) -> dict[str, bool]:
    runner_rows = [row for row in rows if str(row["route_id"]) == RUNNER]
    non_native_rows = [row for row in rows if str(row["route_id"]) != NATIVE_RT_ATTEMPT]
    return {
        "rows_collected": bool(rows),
        "comparison_rows_present": bool(comparison_rows),
        "runner_rows_present": bool(runner_rows),
        "runner_runtime_executed_all_samples": bool(runner_rows)
        and all(bool(row["runtime_executed"]) for row in runner_rows),
        "runner_internal_residency_all_samples": bool(runner_rows)
        and all(bool(row["internal_residency_measured"]) for row in runner_rows),
        "runner_hot_materialization_absent": bool(runner_rows)
        and not any(bool(row["host_materialization_in_hot_path"]) for row in runner_rows),
        "runner_scorecard_bound_all_samples": bool(runner_rows)
        and all(bool(row["scorecard_blocker_bound"]) for row in runner_rows),
        "claim_flags_closed": bool(rows)
        and not any(
            bool(row["release_authorized"])
            or bool(row["public_speedup_claim_authorized"])
            or bool(row["broad_v3_faster_than_v2_claim_authorized"])
            or bool(row["true_zero_copy_claim_authorized"])
            or bool(row["v4_embedding_or_external_zero_copy_authorized"])
            for row in rows
        ),
        "non_native_hot_times_present": bool(non_native_rows)
        and all(row["primary_hot_call_wall_sec"] is not None for row in non_native_rows),
    }


def _median_phase_seconds(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for name in ("prepare", "traverse", "accumulate", "boundary"):
        result[name] = _median(
            [
                float(row["phase_seconds"][name])
                for row in rows
                if row.get("phase_seconds") and row["phase_seconds"].get(name) is not None
            ]
        )
    return result


def _required_float(mapping: dict[str, Any], key: str) -> float:
    value = _optional_float(mapping.get(key))
    if value is None:
        raise KeyError(f"required numeric field missing: {key}")
    return value


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def _sum_optional(*values: Any) -> float:
    return float(sum(value for value in (_optional_float(value) for value in values) if value is not None))


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _ratio(candidate_sec: Any, baseline_sec: Any) -> float | None:
    candidate = _optional_float(candidate_sec)
    baseline = _optional_float(baseline_sec)
    if candidate is None or baseline is None or candidate <= 0.0:
        return None
    return float(baseline / candidate)


def _geomean(values: list[float]) -> float | None:
    positives = [float(value) for value in values if float(value) > 0.0]
    if not positives:
        return None
    return float(math.exp(sum(math.log(value) for value in positives) / len(positives)))


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
