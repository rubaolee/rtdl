#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.barnes_hut import (  # noqa: E402
    rtdl_barnes_hut_benchmark_app as barnes_app,
)
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.barnes_hut_runner_parity_pod_ab.v1"
STATUS_NOT_RELEASE = "barnes_hut_runner_parity_pod_ab_collected_not_release"
HISTORICAL_OPTIX = "historical_prepared_optix_frontier_numba_reference"
FUSED_CONTROL = "existing_app_front_door_fused_numba_cuda_control"
RUNNER = "runner_prepared_execution_fused_numba_cuda"
SCORECARD_BLOCKER_ID = "set_a_barnes_hut_app_geomean_0_844x"
SCORECARD_BLOCKER_APP = "barnes_hut"
SCORECARD_BLOCKER_METRIC = "set_a_app_geomean_v3_vs_v2_14"
SCORECARD_BLOCKER_CURRENT_VALUE = 0.8441965065233041
SCORECARD_BLOCKER_SOURCE = "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md"
VARIANT_MODES = {
    HISTORICAL_OPTIX: "prepared_aggregate_frontier_weighted_vector_optix",
    FUSED_CONTROL: "fused_frontier_force_sum_bucketized_numba_cuda",
    RUNNER: "prepared_execution_fused_vector_sum_numba_cuda",
}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = run_packet(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Focused Phoenix V3 Barnes-Hut POD A/B: productized prepared-execution "
            "runner-wrapped fused Numba CUDA route versus the existing app-front-door "
            "fused route, with the old prepared OptiX frontier route kept only as a "
            "historical no-go reference."
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--body-counts", type=int, nargs="+", default=[32768, 65536, 131072])
    parser.add_argument("--query-repeat", type=int, default=11)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--frontier-capacity-multiplier", type=int, default=700)
    parser.add_argument(
        "--skip-historical-optix",
        action="store_true",
        help="Collect only fused-control vs runner parity rows.",
    )
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    variants = [FUSED_CONTROL, RUNNER] if args.skip_historical_optix else [HISTORICAL_OPTIX, FUSED_CONTROL, RUNNER]
    for body_count in [int(value) for value in args.body_counts]:
        for sample in range(1, int(args.samples) + 1):
            for variant in variants:
                print(
                    "[phoenix-v3-barnes-runner-ab] "
                    f"{variant} body_count={body_count} sample={sample}/{int(args.samples)} "
                    f"repeat={int(args.query_repeat)} warmup={int(args.warmup)}",
                    flush=True,
                )
                output_path = args.output_dir / f"{variant}_{body_count}_s{sample:02d}.json"
                row = _run_variant(
                    args,
                    body_count=body_count,
                    variant=variant,
                    sample=sample,
                    output_path=output_path,
                )
                rows.append(row)

    by_variant_size = _summarize_by_variant_size(rows)
    equivalence_rows = _build_equivalence_rows(by_variant_size)
    checks = _build_checks(
        rows,
        historical_required=not bool(args.skip_historical_optix),
        equivalence_rows=equivalence_rows,
    )
    failed_checks = [name for name, ok in checks.items() if not ok]
    parity_rows = _build_parity_rows(by_variant_size)
    historical_rows = _build_historical_rows(by_variant_size)
    parity_geomean = _geomean(
        [
            float(row["runner_vs_existing_fused_control_speedup"])
            for row in parity_rows
            if row["runner_vs_existing_fused_control_speedup"] is not None
        ]
    )
    historical_geomean = _geomean(
        [
            float(row["historical_optix_over_runner_speedup"])
            for row in historical_rows
            if row["historical_optix_over_runner_speedup"] is not None
        ]
    )
    parity_pass = bool(
        parity_rows
        and all(float(row["runner_vs_existing_fused_control_speedup"]) >= 0.95 for row in parity_rows)
        and parity_geomean is not None
        and float(parity_geomean) >= 0.98
    )
    historical_reference_material = bool(
        not bool(args.skip_historical_optix)
        and historical_rows
        and all(float(row["historical_optix_over_runner_speedup"]) >= 1.20 for row in historical_rows)
        and historical_geomean is not None
        and float(historical_geomean) >= 1.20
    )
    runner_rows = [row for row in rows if row["variant"] == RUNNER]
    blocker_metadata_ready = bool(
        checks["runner_scorecard_blocker_bound_all_samples"]
        and checks["runner_scorecard_blocker_id_all_samples"]
        and checks["runner_scorecard_blocker_app_all_samples"]
        and checks["runner_win_source_partner_continuation_all_samples"]
        and checks["runner_m43_reuse_scope_present_all_samples"]
        and checks["control_not_scorecard_bound"]
    )
    runner_step3_audit_rows = [
        {
            "body_count": int(row["body_count"]),
            "sample": int(row["sample"]),
            "status": row["step3_audit_status"],
            "step3_residency_default_ready": bool(row["step3_residency_default_ready"]),
            "missing_step3_fields": list(row["step3_audit_missing_fields"]),
        }
        for row in runner_rows
    ]
    step1_replacement_candidate = bool(
        checks["runner_used_all_samples"]
        and checks["runner_runtime_trunk_executes_all_samples"]
        and checks["runner_internal_device_residency_all_samples"]
        and checks["runner_step3_residency_default_ready_all_samples"]
        and blocker_metadata_ready
        and checks["runner_hot_path_host_materialization_absent"]
        and checks["runner_control_output_equivalence_all_sizes"]
        and checks["all_claim_flags_false"]
        and parity_pass
        and historical_reference_material
    )
    summary = {
        "status": STATUS_NOT_RELEASE,
        "body_counts": [int(value) for value in args.body_counts],
        "query_repeat": int(args.query_repeat),
        "warmup": int(args.warmup),
        "samples": int(args.samples),
        "theta": float(args.theta),
        "bucket_size": int(args.bucket_size),
        "max_depth": int(args.max_depth),
        "variants": variants,
        "scorecard_blocker": {
            "id": SCORECARD_BLOCKER_ID,
            "set": "A",
            "app": SCORECARD_BLOCKER_APP,
            "metric": SCORECARD_BLOCKER_METRIC,
            "current_value": SCORECARD_BLOCKER_CURRENT_VALUE,
            "source": SCORECARD_BLOCKER_SOURCE,
            "target": "move_toward_or_above_parity",
            "route_kind": "trunk_fix_candidate",
        },
        "incumbent_route_declaration": {
            "baseline_variant": FUSED_CONTROL,
            "baseline_mode": VARIANT_MODES[FUSED_CONTROL],
            "candidate_variant": RUNNER,
            "candidate_mode": VARIANT_MODES[RUNNER],
            "historical_reference_variant": HISTORICAL_OPTIX,
            "historical_reference_mode": VARIANT_MODES[HISTORICAL_OPTIX],
            "body_counts": [int(value) for value in args.body_counts],
            "theta": float(args.theta),
            "bucket_size": int(args.bucket_size),
            "max_depth": int(args.max_depth),
            "query_repeat": int(args.query_repeat),
            "warmup": int(args.warmup),
            "samples": int(args.samples),
            "same_pod_session_required": True,
            "scorecard_row_id": SCORECARD_BLOCKER_ID,
            "scorecard_current_value": SCORECARD_BLOCKER_CURRENT_VALUE,
            "scorecard_source": SCORECARD_BLOCKER_SOURCE,
            "prior_evidence_reference": (
                "docs/rebuild/v3/evidence/"
                "phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/summary.json"
            ),
        },
        "variant_size_summaries": by_variant_size,
        "runner_control_equivalence_rows": equivalence_rows,
        "parity_rows": parity_rows,
        "historical_reference_rows": historical_rows,
        "runner_vs_existing_fused_control_geomean": parity_geomean,
        "historical_optix_over_runner_geomean": historical_geomean,
        "runner_parity_with_existing_fused_partner": parity_pass,
        "historical_reference_material": historical_reference_material,
        "runner_step3_audit_rows": runner_step3_audit_rows,
        "runner_step3_residency_default_ready": checks["runner_step3_residency_default_ready_all_samples"],
        "m72_blocker_metadata_ready": blocker_metadata_ready,
        "runtime_sourced_material_gain_scope": (
            "step1_replacement_candidate requires scorecard-bound runner metadata, current-control parity, "
            "and historical no-go displacement; it is not a wrapper-faster-than-current-control claim"
        ),
        "step1_replacement_candidate": step1_replacement_candidate,
        "runtime_sourced_material_gain": step1_replacement_candidate,
        "skip_historical_optix_smoke_only": bool(args.skip_historical_optix),
        "wrapper_itself_faster_than_existing_fused_partner_claim_authorized": False,
        "historical_optix_reference_is_primary_claim": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }
    return {
        "schema": SCHEMA,
        "status": "fail" if failed_checks else STATUS_NOT_RELEASE,
        "summary": summary,
        "checks": checks,
        "failed_checks": failed_checks,
        "rows": rows,
        "environment": {
            "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "git_dirty": (_command_output(["git", "status", "--short"]) or "").splitlines(),
            "nvidia_smi": _command_output(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]
            ),
        },
        "goal_level_decision_audit": {
            "decision": (
                "Run Barnes-Hut as a focused Step-1 replacement productized-runner A/B before any all-app run."
            ),
            "was_i_foolish": "No. This follows the redirect: trunk first, all-app later.",
            "foolish_actions": (
                "The foolish move would be to count only the large speedup versus the known slow OptiX frontier "
                "route and ignore whether the runner preserves the existing fused partner speed."
            ),
            "other_path": (
                "A full all-app run is possible, but it would mix Set A and Set B before this trunk candidate "
                "has a focused, productized-path result."
            ),
            "different_path_now": (
                "Use the dual comparison: runner versus existing fused partner for parity, and runner versus "
                "historical OptiX frontier only as a no-go reference."
            ),
        },
        "non_authorization": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "full_all_app_rerun_authorized_by_this_packet": False,
        },
    }


def _run_variant(
    args: argparse.Namespace,
    *,
    body_count: int,
    variant: str,
    sample: int,
    output_path: Path,
) -> dict[str, Any]:
    start = time.perf_counter()
    payload = barnes_app.run_benchmark(
        VARIANT_MODES[variant],
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _extract_row(
        payload,
        variant=variant,
        body_count=body_count,
        sample=sample,
        output_path=output_path,
        process_wall_sec=process_wall_sec,
    )


def _extract_row(
    payload: dict[str, Any],
    *,
    variant: str,
    body_count: int,
    sample: int,
    output_path: Path,
    process_wall_sec: float,
) -> dict[str, Any]:
    medians = dict(payload.get("medians") or {})
    vector_summary = dict(payload.get("vector_sum_summary") or {})
    claim_flags = dict(payload.get("claim_flags") or {})
    runner_metadata = dict(payload.get("prepared_execution_session_runner") or {})
    m72_payload = dict(payload.get("phoenix_v3_m72") or {})
    scorecard_binding = dict(runner_metadata.get("scorecard_binding") or {})
    runner_step3_audit = audit_prepared_execution_session_metadata(runner_metadata)
    if variant == HISTORICAL_OPTIX:
        primary_sec = float(medians["wall_seconds"])
        kernel_sec = float(medians["hot_seconds_native_plus_partner"])
    elif variant == FUSED_CONTROL:
        primary_sec = float(medians["fused_numba_cuda_call_wall_seconds"])
        kernel_sec = _optional_float(medians.get("fused_numba_cuda_kernel_event_seconds"))
    elif variant == RUNNER:
        primary_sec = float(medians["prepared_execution_runner_measured_seconds"])
        kernel_sec = _optional_float(medians.get("fused_numba_cuda_kernel_event_seconds"))
    else:
        raise ValueError(f"unknown variant: {variant}")
    validation = dict(payload.get("validation") or {})
    return {
        "variant": variant,
        "mode": str(payload.get("mode")),
        "body_count": int(body_count),
        "sample": int(sample),
        "output_json": str(output_path),
        "process_wall_sec": float(process_wall_sec),
        "primary_hot_call_wall_sec": primary_sec,
        "kernel_or_native_hot_sec": kernel_sec,
        "tree_node_count": int(vector_summary.get("tree_node_count", 0) or payload.get("tree_summary", {}).get("node_count", 0) or 0),
        "contribution_row_count": int(
            vector_summary.get("contribution_row_count")
            or vector_summary.get("frontier_row_count")
            or 0
        ),
        "aggregate_contribution_row_count": int(vector_summary.get("aggregate_contribution_row_count", 0) or 0),
        "exact_contribution_row_count": int(vector_summary.get("exact_contribution_row_count", 0) or 0),
        "checksum_force_x": _optional_float(vector_summary.get("checksum_force_x")),
        "checksum_force_y": _optional_float(vector_summary.get("checksum_force_y")),
        "validation_skipped": bool(validation.get("skipped", False)),
        "validation_reason": validation.get("reason"),
        "frontier_rows_materialized_on_host": bool(
            vector_summary.get("frontier_rows_materialized_on_host", False)
            or vector_summary.get("materialized_frontier_rows", False)
            or claim_flags.get("frontier_columns_materialized_on_host", False)
        ),
        "contribution_rows_materialized_on_host": bool(
            vector_summary.get("contribution_rows_materialized_on_host", False)
            or vector_summary.get("materialized_contribution_rows", False)
            or claim_flags.get("contribution_rows_materialized_on_host", False)
        ),
        "prepared_execution_session_runner_used": bool(runner_metadata),
        "step3_audit": runner_step3_audit,
        "step3_audit_status": str(runner_step3_audit.get("status")),
        "step3_audit_missing_fields": tuple(runner_step3_audit.get("missing_step3_fields") or ()),
        "step3_residency_default_ready": bool(runner_step3_audit.get("step3_residency_default_ready")),
        "runtime_trunk_executes_end_to_end": bool(
            runner_metadata.get("runtime_trunk_executes_end_to_end", False)
            or vector_summary.get("runtime_trunk_executes_end_to_end", False)
            or claim_flags.get("runtime_trunk_executes_end_to_end", False)
        ),
        "phoenix_v3_m72_present": bool(m72_payload),
        "scorecard_blocker_bound": bool(
            m72_payload.get("scorecard_blocker_bound", False)
            or runner_metadata.get("scorecard_blocker_bound", False)
            or vector_summary.get("scorecard_blocker_bound", False)
            or claim_flags.get("scorecard_blocker_bound", False)
        ),
        "scorecard_blocker_id": str(
            scorecard_binding.get("id")
            or runner_metadata.get("m72_target_blocker")
            or m72_payload.get("scorecard_blocker_id")
            or ""
        ),
        "scorecard_blocker_app": str(
            m72_payload.get("scorecard_blocker_app")
            or runner_metadata.get("scorecard_blocker_app")
            or vector_summary.get("scorecard_blocker_app")
            or claim_flags.get("scorecard_blocker_app")
            or ""
        ),
        "scorecard_blocker_current_value": _optional_float(
            m72_payload.get("scorecard_blocker_current_value")
            or runner_metadata.get("scorecard_blocker_current_value")
            or vector_summary.get("scorecard_blocker_current_value")
            or claim_flags.get("scorecard_blocker_current_value")
        ),
        "scorecard_blocker_route_kind": str(
            m72_payload.get("scorecard_blocker_route_kind")
            or runner_metadata.get("scorecard_blocker_route_kind")
            or claim_flags.get("scorecard_blocker_route_kind")
            or ""
        ),
        "win_source": str(
            m72_payload.get("win_source")
            or runner_metadata.get("win_source")
            or vector_summary.get("win_source")
            or claim_flags.get("win_source")
            or ""
        ),
        "m43_reuse_scope": str(
            m72_payload.get("m43_reuse_scope")
            or runner_metadata.get("m43_reuse_scope")
            or vector_summary.get("m43_reuse_scope")
            or claim_flags.get("m43_reuse_scope")
            or ""
        ),
        "internal_device_residency_between_rtdl_phases": bool(
            runner_metadata.get("internal_device_residency_between_rtdl_phases", False)
            or vector_summary.get("internal_device_residency_between_rtdl_phases", False)
        ),
        "hot_path_host_materialization": bool(
            runner_metadata.get("hot_path_host_materialization", False)
            or vector_summary.get("hot_path_host_materialization", False)
            or claim_flags.get("hot_path_host_materialization", False)
        ),
        "release_authorized": bool(payload.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(
            payload.get("public_speedup_claim_authorized", False)
            or claim_flags.get("public_speedup_claim_authorized", False)
        ),
        "broad_v3_faster_than_v2_claim_authorized": bool(
            payload.get("broad_v3_faster_than_v2_claim_authorized", False)
            or claim_flags.get("broad_v3_faster_than_v2_claim_authorized", False)
        ),
        "rt_core_speedup_claim_authorized": bool(
            payload.get("rt_core_speedup_claim_authorized", False)
            or claim_flags.get("rt_core_speedup_claim_authorized", False)
        ),
        "true_zero_copy_claim_authorized": bool(
            payload.get("true_zero_copy_claim_authorized", False)
            or claim_flags.get("true_zero_copy_claim_authorized", False)
        ),
        "v4_embedding_or_external_zero_copy_authorized": bool(
            payload.get("v4_embedding_or_external_zero_copy_authorized", False)
            or runner_metadata.get("v4_embedding_or_external_zero_copy_authorized", False)
            or claim_flags.get("v4_embedding_or_external_zero_copy_authorized", False)
        ),
        "full_all_app_rerun_authorized_by_this_packet": bool(
            payload.get("full_all_app_rerun_authorized_by_this_packet", False)
            or runner_metadata.get("full_all_app_rerun_authorized_by_this_packet", False)
            or claim_flags.get("full_all_app_rerun_authorized_by_this_packet", False)
        ),
        "automatic_partner_selection_authorized": bool(
            payload.get("automatic_partner_selection_authorized", False)
            or claim_flags.get("automatic_partner_selection_authorized", False)
        ),
        "native_engine_app_specific": bool(claim_flags.get("native_engine_app_specific", False)),
    }


def _summarize_by_variant_size(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for variant in sorted({str(row["variant"]) for row in rows}):
        variant_rows = [row for row in rows if row["variant"] == variant]
        for body_count in sorted({int(row["body_count"]) for row in variant_rows}):
            size_rows = [row for row in variant_rows if int(row["body_count"]) == body_count]
            key = f"{variant}:{body_count}"
            result[key] = {
                "variant": variant,
                "body_count": body_count,
                "sample_count": len(size_rows),
                "primary_hot_call_wall_sec_median": _median(
                    [float(row["primary_hot_call_wall_sec"]) for row in size_rows]
                ),
                "kernel_or_native_hot_sec_median": _median(
                    [
                        float(row["kernel_or_native_hot_sec"])
                        for row in size_rows
                        if row["kernel_or_native_hot_sec"] is not None
                    ]
                ),
                "process_wall_sec_median": _median([float(row["process_wall_sec"]) for row in size_rows]),
                "contribution_row_count_median": _median(
                    [float(row["contribution_row_count"]) for row in size_rows]
                ),
                "checksum_force_x_median": _median(
                    [
                        float(row["checksum_force_x"])
                        for row in size_rows
                        if row["checksum_force_x"] is not None
                    ]
                ),
                "checksum_force_y_median": _median(
                    [
                        float(row["checksum_force_y"])
                        for row in size_rows
                        if row["checksum_force_y"] is not None
                    ]
                ),
                "checksum_force_x_values": sorted(
                    {round(float(row["checksum_force_x"]), 9) for row in size_rows if row["checksum_force_x"] is not None}
                ),
                "checksum_force_y_values": sorted(
                    {round(float(row["checksum_force_y"]), 9) for row in size_rows if row["checksum_force_y"] is not None}
                ),
                "runner_used_all_samples": all(bool(row["prepared_execution_session_runner_used"]) for row in size_rows),
                "runtime_trunk_executes_all_samples": all(bool(row["runtime_trunk_executes_end_to_end"]) for row in size_rows),
                "internal_device_residency_all_samples": all(
                    bool(row["internal_device_residency_between_rtdl_phases"]) for row in size_rows
                ),
                "hot_path_host_materialization_any_sample": any(
                    bool(row["hot_path_host_materialization"]) for row in size_rows
                ),
            }
    return result


def _build_equivalence_rows(by_variant_size: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    body_counts = sorted(
        {
            int(summary["body_count"])
            for summary in by_variant_size.values()
            if str(summary["variant"]) in {FUSED_CONTROL, RUNNER}
        }
    )
    rows: list[dict[str, Any]] = []
    for body_count in body_counts:
        control = by_variant_size.get(f"{FUSED_CONTROL}:{body_count}")
        runner = by_variant_size.get(f"{RUNNER}:{body_count}")
        if control is None or runner is None:
            continue
        contribution_count_match = _close(
            control.get("contribution_row_count_median"),
            runner.get("contribution_row_count_median"),
            abs_tol=0.0,
            rel_tol=0.0,
        )
        checksum_x_match = _close(
            control.get("checksum_force_x_median"),
            runner.get("checksum_force_x_median"),
            abs_tol=1.0e-6,
            rel_tol=1.0e-12,
        )
        checksum_y_match = _close(
            control.get("checksum_force_y_median"),
            runner.get("checksum_force_y_median"),
            abs_tol=1.0e-6,
            rel_tol=1.0e-12,
        )
        rows.append(
            {
                "body_count": body_count,
                "contribution_count_match": contribution_count_match,
                "checksum_force_x_match": checksum_x_match,
                "checksum_force_y_match": checksum_y_match,
                "equivalence_pass": bool(contribution_count_match and checksum_x_match and checksum_y_match),
                "existing_fused_control_checksum_force_x_median": control.get("checksum_force_x_median"),
                "runner_checksum_force_x_median": runner.get("checksum_force_x_median"),
                "existing_fused_control_checksum_force_y_median": control.get("checksum_force_y_median"),
                "runner_checksum_force_y_median": runner.get("checksum_force_y_median"),
                "existing_fused_control_contribution_row_count_median": control.get(
                    "contribution_row_count_median"
                ),
                "runner_contribution_row_count_median": runner.get("contribution_row_count_median"),
            }
        )
    return rows


def _build_parity_rows(by_variant_size: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    body_counts = sorted(
        {
            int(summary["body_count"])
            for key, summary in by_variant_size.items()
            if str(summary["variant"]) in {FUSED_CONTROL, RUNNER}
        }
    )
    rows: list[dict[str, Any]] = []
    for body_count in body_counts:
        control = by_variant_size.get(f"{FUSED_CONTROL}:{body_count}")
        runner = by_variant_size.get(f"{RUNNER}:{body_count}")
        if control is None or runner is None:
            continue
        speedup = _ratio(
            runner["primary_hot_call_wall_sec_median"],
            control["primary_hot_call_wall_sec_median"],
        )
        rows.append(
            {
                "body_count": body_count,
                "runner_vs_existing_fused_control_speedup": speedup,
                "runner_sec_median": runner["primary_hot_call_wall_sec_median"],
                "existing_fused_control_sec_median": control["primary_hot_call_wall_sec_median"],
                "parity_floor_0_95_pass": speedup is not None and float(speedup) >= 0.95,
            }
        )
    return rows


def _build_historical_rows(by_variant_size: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    body_counts = sorted(
        {
            int(summary["body_count"])
            for key, summary in by_variant_size.items()
            if str(summary["variant"]) in {HISTORICAL_OPTIX, RUNNER}
        }
    )
    rows: list[dict[str, Any]] = []
    for body_count in body_counts:
        historical = by_variant_size.get(f"{HISTORICAL_OPTIX}:{body_count}")
        runner = by_variant_size.get(f"{RUNNER}:{body_count}")
        if historical is None or runner is None:
            continue
        speedup = _ratio(
            runner["primary_hot_call_wall_sec_median"],
            historical["primary_hot_call_wall_sec_median"],
        )
        rows.append(
            {
                "body_count": body_count,
                "historical_optix_over_runner_speedup": speedup,
                "runner_sec_median": runner["primary_hot_call_wall_sec_median"],
                "historical_optix_sec_median": historical["primary_hot_call_wall_sec_median"],
                "historical_reference_floor_1_20_pass": speedup is not None and float(speedup) >= 1.20,
            }
        )
    return rows


def _build_checks(
    rows: list[dict[str, Any]],
    *,
    historical_required: bool,
    equivalence_rows: list[dict[str, Any]],
) -> dict[str, bool]:
    runner_rows = [row for row in rows if row["variant"] == RUNNER]
    control_rows = [row for row in rows if row["variant"] == FUSED_CONTROL]
    historical_rows = [row for row in rows if row["variant"] == HISTORICAL_OPTIX]
    return {
        "samples_collected": bool(runner_rows) and bool(control_rows) and (bool(historical_rows) or not historical_required),
        "same_body_counts_for_runner_and_control": {row["body_count"] for row in runner_rows}
        == {row["body_count"] for row in control_rows},
        "historical_rows_present_when_required": bool(historical_rows) if historical_required else True,
        "runner_used_all_samples": all(bool(row["prepared_execution_session_runner_used"]) for row in runner_rows),
        "control_does_not_use_runner": all(not bool(row["prepared_execution_session_runner_used"]) for row in control_rows),
        "runner_runtime_trunk_executes_all_samples": all(
            bool(row["runtime_trunk_executes_end_to_end"]) for row in runner_rows
        ),
        "runner_internal_device_residency_all_samples": all(
            bool(row["internal_device_residency_between_rtdl_phases"]) for row in runner_rows
        ),
        "runner_step3_residency_default_ready_all_samples": all(
            bool(row["step3_residency_default_ready"]) for row in runner_rows
        ),
        "runner_scorecard_blocker_bound_all_samples": all(
            bool(row["scorecard_blocker_bound"]) for row in runner_rows
        ),
        "runner_scorecard_blocker_id_all_samples": all(
            str(row["scorecard_blocker_id"]) == SCORECARD_BLOCKER_ID for row in runner_rows
        ),
        "runner_scorecard_blocker_app_all_samples": all(
            str(row["scorecard_blocker_app"]) == SCORECARD_BLOCKER_APP for row in runner_rows
        ),
        "runner_win_source_partner_continuation_all_samples": all(
            str(row["win_source"]) == "partner_continuation" for row in runner_rows
        ),
        "runner_m43_reuse_scope_present_all_samples": all(
            "not the M43 CuPy grouped-reduction kernel" in str(row["m43_reuse_scope"])
            for row in runner_rows
        ),
        "control_not_scorecard_bound": all(not bool(row["scorecard_blocker_bound"]) for row in control_rows),
        "runner_hot_path_host_materialization_absent": all(
            not bool(row["hot_path_host_materialization"]) for row in runner_rows
        ),
        "runner_no_frontier_or_contribution_host_materialization": all(
            not bool(row["frontier_rows_materialized_on_host"])
            and not bool(row["contribution_rows_materialized_on_host"])
            for row in runner_rows
        ),
        "runner_control_output_equivalence_all_sizes": bool(equivalence_rows)
        and all(bool(row["equivalence_pass"]) for row in equivalence_rows),
        "all_claim_flags_false": all(
            not bool(row["release_authorized"])
            and not bool(row["public_speedup_claim_authorized"])
            and not bool(row["broad_v3_faster_than_v2_claim_authorized"])
            and not bool(row["rt_core_speedup_claim_authorized"])
            and not bool(row["true_zero_copy_claim_authorized"])
            and not bool(row["v4_embedding_or_external_zero_copy_authorized"])
            and not bool(row["full_all_app_rerun_authorized_by_this_packet"])
            and not bool(row["automatic_partner_selection_authorized"])
            for row in rows
        ),
        "native_engine_app_specific_absent": all(not bool(row["native_engine_app_specific"]) for row in rows),
    }


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Phoenix V3 Barnes-Hut Runner Parity Focused POD A/B",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"- body counts: `{summary['body_counts']}`",
        f"- repeat/warmup/samples: `{summary['query_repeat']}` / `{summary['warmup']}` / `{summary['samples']}`",
        f"- runner vs existing fused-control geomean: `{summary['runner_vs_existing_fused_control_geomean']}`",
        f"- historical OptiX over runner geomean: `{summary['historical_optix_over_runner_geomean']}`",
        f"- runner/control output equivalence rows: `{summary.get('runner_control_equivalence_rows')}`",
        f"- scorecard blocker: `{summary.get('scorecard_blocker')}`",
        f"- incumbent route declaration: `{summary.get('incumbent_route_declaration')}`",
        f"- M72 blocker metadata ready: `{summary.get('m72_blocker_metadata_ready')}`",
        f"- runner parity with existing fused partner: `{summary['runner_parity_with_existing_fused_partner']}`",
        f"- runner Step-3 residency audit ready: `{summary.get('runner_step3_residency_default_ready')}`",
        f"- step-1 replacement candidate: `{summary['step1_replacement_candidate']}`",
        f"- skip-historical smoke only: `{summary.get('skip_historical_optix_smoke_only')}`",
        "",
        "The primary control is the existing app-front-door fused Numba CUDA route.",
        "The prepared OptiX frontier route is included only as a historical no-go reference.",
        "If the historical leg is skipped, the packet is smoke-only and cannot become",
        "a Step-1 replacement candidate.",
        "This packet authorizes no release, broad V3-over-V2 wording, true-zero-copy wording,",
        "wrapper-is-faster wording, or all-app rerun.",
        "",
    ]
    return "\n".join(lines)


def _median(values: list[float]) -> float | None:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(finite)) if finite else None


def _geomean(values: list[float]) -> float | None:
    positive = [float(value) for value in values if float(value) > 0.0 and math.isfinite(float(value))]
    if not positive:
        return None
    return float(math.exp(sum(math.log(value) for value in positive) / len(positive)))


def _ratio(denominator: float | None, numerator: float | None) -> float | None:
    if denominator is None or numerator is None or float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _close(value_a: Any, value_b: Any, *, abs_tol: float, rel_tol: float) -> bool:
    if value_a is None or value_b is None:
        return False
    return math.isclose(float(value_a), float(value_b), abs_tol=float(abs_tol), rel_tol=float(rel_tol))


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


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


if __name__ == "__main__":
    raise SystemExit(main())
