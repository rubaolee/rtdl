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

from examples.current.research_benchmarks.spatial_rayjoin import (  # noqa: E402
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.rayjoin_point_location_runner_pod_ab.v1"
STATUS_NOT_RELEASE = "rayjoin_point_location_runner_pod_ab_collected_not_release"
LEGACY_VARIANT = "legacy_optix_relation_status_corrected_executor"
RUNNER_VARIANT = "runner_point_location_topology_stream_prepared_execution"
OUTPUT_CONTRACT = "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated"


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
            "Focused Phoenix V3 Spatial RayJoin POD A/B: current OptiX relation-status "
            "route vs the productized point-location topology-stream runner."
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset", default="data/rayjoin_public_cdb/br_county.cdb")
    parser.add_argument(
        "--point-order-mode",
        choices=("natural", "x_then_y", "y_then_x", "morton_xy"),
        default="y_then_x",
    )
    parser.add_argument("--query-repeat", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--samples", type=int, default=7)
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for sample in range(1, int(args.samples) + 1):
        for variant in (LEGACY_VARIANT, RUNNER_VARIANT):
            print(
                "[phoenix-v3-rayjoin-runner-ab] "
                f"{variant} sample={sample}/{int(args.samples)} "
                f"dataset={args.dataset} point_order={args.point_order_mode}",
                flush=True,
            )
            output_path = args.output_dir / f"{variant}_s{sample:02d}.json"
            row = _run_variant(args, variant=variant, sample=sample, output_path=output_path)
            rows.append(row)

    checks = _build_checks(rows)
    failed_checks = [name for name, ok in checks.items() if not ok]
    variant_summaries = {
        LEGACY_VARIANT: _summarize_variant([row for row in rows if row["variant"] == LEGACY_VARIANT]),
        RUNNER_VARIANT: _summarize_variant([row for row in rows if row["variant"] == RUNNER_VARIANT]),
    }
    legacy_summary = variant_summaries[LEGACY_VARIANT]
    runner_summary = variant_summaries[RUNNER_VARIANT]
    speedups = {
        "median_per_call_speedup_legacy_over_runner": _ratio(
            legacy_summary["prepared_query_sec_median"],
            runner_summary["prepared_query_sec_median"],
        ),
        "median_total_repeat_speedup_legacy_over_runner": _ratio(
            legacy_summary["prepared_query_total_sec_median"],
            runner_summary["prepared_query_total_sec_median"],
        ),
        "process_wall_speedup_control_legacy_over_runner": _ratio(
            legacy_summary["process_wall_sec_median"],
            runner_summary["process_wall_sec_median"],
        ),
    }
    runner_rows = [row for row in rows if row["variant"] == RUNNER_VARIANT]
    runner_step3_audit_rows = [
        {
            "sample": int(row["sample"]),
            "status": row["step3_audit_status"],
            "step3_residency_default_ready": bool(row["step3_residency_default_ready"]),
            "missing_step3_fields": list(row["step3_audit_missing_fields"]),
        }
        for row in runner_rows
    ]
    material = bool(
        speedups["median_per_call_speedup_legacy_over_runner"] is not None
        and speedups["median_total_repeat_speedup_legacy_over_runner"] is not None
        and float(speedups["median_per_call_speedup_legacy_over_runner"]) >= 1.20
        and float(speedups["median_total_repeat_speedup_legacy_over_runner"]) >= 1.20
        and checks["runner_runtime_trunk_executes_all_samples"]
        and checks["runner_internal_device_residency_all_samples"]
        and checks["runner_step3_residency_default_ready_all_samples"]
        and checks["runner_hot_path_host_materialization_absent"]
        and checks["all_claim_flags_false"]
    )
    summary = {
        "status": STATUS_NOT_RELEASE,
        "dataset": str(args.dataset),
        "point_order_mode": str(args.point_order_mode),
        "query_repeat": int(args.query_repeat),
        "warmup": int(args.warmup),
        "samples": int(args.samples),
        "row_count": runner_summary["row_count"],
        "output_contract": OUTPUT_CONTRACT,
        "variant_summaries": variant_summaries,
        "speedups": speedups,
        "runner_step3_audit_rows": runner_step3_audit_rows,
        "runner_step3_residency_default_ready": checks[
            "runner_step3_residency_default_ready_all_samples"
        ],
        "material_set_a_candidate": material,
        "runtime_sourced_material_gain": material,
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
                "Run RayJoin as a focused Step-2 productized-runner A/B before any all-app Phoenix V3 run."
            ),
            "was_i_foolish": "No. This follows the redesign dependency order and avoids another blended all-app run.",
            "foolish_actions": (
                "The foolish move would be to compare runner vs Embree or toy data, then call it a V3 win."
            ),
            "other_path": (
                "A broader all-app run is possible, but it would burn pod time before a second trunk family "
                "has shown material runtime-sourced gain."
            ),
            "different_path_now": (
                "Use this same-contract RayJoin packet to decide whether the point-location topology-stream "
                "family should advance, be redesigned, or be marked structural-only like RTDBSCAN."
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
    variant: str,
    sample: int,
    output_path: Path,
) -> dict[str, Any]:
    start = time.perf_counter()
    if variant == LEGACY_VARIANT:
        payload = rayjoin_app.run_rayjoin_prepared_optix_workload(
            "pip",
            dataset=str(args.dataset),
            result_mode="count",
            include_rows=False,
            count_mode="relation_status_corrected_executor_validated",
            point_order_mode=str(args.point_order_mode),
            query_repeat=int(args.query_repeat),
            warmup=int(args.warmup),
        )
    elif variant == RUNNER_VARIANT:
        payload = rayjoin_app.run_rayjoin_prepared_execution_point_location_topology_stream_workload(
            "pip",
            dataset=str(args.dataset),
            point_order_mode=str(args.point_order_mode),
            query_repeat=int(args.query_repeat),
            warmup=int(args.warmup),
        )
    else:
        raise ValueError(f"unknown variant: {variant}")
    process_wall_sec = time.perf_counter() - start
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _extract_row(
        payload,
        variant=variant,
        sample=sample,
        output_path=output_path,
        process_wall_sec=process_wall_sec,
    )


def _extract_row(
    payload: dict[str, Any],
    *,
    variant: str,
    sample: int,
    output_path: Path,
    process_wall_sec: float,
) -> dict[str, Any]:
    summary = dict(payload.get("summary") or {})
    phases = dict(payload.get("phases_sec") or {})
    native_phase_timings = dict(payload.get("native_phase_timings") or {})
    runner_metadata = dict(payload.get("prepared_execution_session_runner") or {})
    runner_step3_audit = audit_prepared_execution_session_metadata(runner_metadata)
    if variant == RUNNER_VARIANT:
        prepared_query_sec = float(runner_metadata.get("measured_median_sec"))
        prepared_query_total_sec = float(runner_metadata.get("measured_total_sec"))
    else:
        prepared_query_sec = float(phases.get("prepared_query_sec"))
        prepared_query_total_sec = float(phases.get("prepared_query_sec_total_sec", prepared_query_sec))
    return {
        "variant": variant,
        "sample": int(sample),
        "output_json": str(output_path),
        "process_wall_sec": float(process_wall_sec),
        "row_count": int(payload["row_count"]),
        "validation_exact_count": int(summary.get("validation_exact_count", payload["row_count"])),
        "output_contract": str(summary.get("output_contract")),
        "point_order_mode": summary.get("point_order_mode"),
        "prepared_query_sec": prepared_query_sec,
        "prepared_query_total_sec": prepared_query_total_sec,
        "prepared_query_repeat": int(phases.get("prepared_query_sec_repeat", runner_metadata.get("measured_repeat_count", 1))),
        "prepared_query_warmup": int(phases.get("prepared_query_sec_warmup", 0)),
        "native_phase_timings": native_phase_timings,
        "row_stream_materialized": bool(native_phase_timings.get("row_stream_materialized", False)),
        "boundary_candidate_row_stream_materialized": bool(
            native_phase_timings.get("boundary_candidate_row_stream_materialized", False)
        ),
        "candidate_download_sec": float(native_phase_timings.get("candidate_download", 0.0) or 0.0),
        "runtime_trunk_executes_end_to_end": bool(payload.get("runtime_trunk_executes_end_to_end", False)),
        "internal_device_residency_between_rtdl_phases": bool(
            payload.get("internal_device_residency_between_rtdl_phases", False)
        ),
        "hot_path_host_materialization": bool(payload.get("hot_path_host_materialization", False)),
        "prepared_execution_session_runner_used": bool(runner_metadata),
        "prepared_execution_session_runner": runner_metadata,
        "step3_audit": runner_step3_audit,
        "step3_audit_status": str(runner_step3_audit.get("status")),
        "step3_audit_missing_fields": tuple(runner_step3_audit.get("missing_step3_fields") or ()),
        "step3_residency_default_ready": bool(
            runner_step3_audit.get("step3_residency_default_ready")
        ),
        "release_authorized": bool(payload.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(payload.get("public_speedup_claim_authorized", False)),
        "broad_v3_faster_than_v2_claim_authorized": bool(
            payload.get("broad_v3_faster_than_v2_claim_authorized", False)
        ),
        "true_zero_copy_claim_authorized": bool(payload.get("true_zero_copy_claim_authorized", False)),
        "v4_embedding_or_external_zero_copy_authorized": bool(
            payload.get("v4_embedding_or_external_zero_copy_authorized", False)
            or runner_metadata.get("v4_embedding_or_external_zero_copy_authorized", False)
        ),
        "full_all_app_rerun_authorized_by_this_packet": bool(
            payload.get("full_all_app_rerun_authorized_by_this_packet", False)
            or runner_metadata.get("full_all_app_rerun_authorized_by_this_packet", False)
        ),
    }


def _summarize_variant(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "sample_count": len(rows),
        "row_count": rows[-1]["row_count"] if rows else None,
        "row_count_consistent": len({int(row["row_count"]) for row in rows}) <= 1,
        "output_contracts": sorted({str(row["output_contract"]) for row in rows}),
        "point_order_modes": sorted({str(row["point_order_mode"]) for row in rows}),
        "prepared_query_sec_median": _median([float(row["prepared_query_sec"]) for row in rows]),
        "prepared_query_total_sec_median": _median([float(row["prepared_query_total_sec"]) for row in rows]),
        "process_wall_sec_median": _median([float(row["process_wall_sec"]) for row in rows]),
        "runner_used_all_samples": all(bool(row["prepared_execution_session_runner_used"]) for row in rows),
        "step3_audit_statuses": sorted(
            {str(row["step3_audit_status"]) for row in rows if row["step3_audit_status"] is not None}
        ),
        "step3_audit_missing_fields": sorted(
            {
                str(field)
                for row in rows
                for field in tuple(row["step3_audit_missing_fields"] or ())
            }
        ),
        "step3_residency_default_ready_all_samples": all(
            bool(row["step3_residency_default_ready"]) for row in rows
        ),
        "runtime_trunk_executes_all_samples": all(bool(row["runtime_trunk_executes_end_to_end"]) for row in rows),
        "internal_device_residency_all_samples": all(
            bool(row["internal_device_residency_between_rtdl_phases"]) for row in rows
        ),
        "hot_path_host_materialization_any_sample": any(bool(row["hot_path_host_materialization"]) for row in rows),
        "row_stream_materialized_any_sample": any(bool(row["row_stream_materialized"]) for row in rows),
    }


def _build_checks(rows: list[dict[str, Any]]) -> dict[str, bool]:
    legacy_rows = [row for row in rows if row["variant"] == LEGACY_VARIANT]
    runner_rows = [row for row in rows if row["variant"] == RUNNER_VARIANT]
    all_row_counts = {int(row["row_count"]) for row in rows}
    all_contracts = {str(row["output_contract"]) for row in rows}
    all_point_orders = {str(row["point_order_mode"]) for row in rows}
    return {
        "samples_collected": bool(legacy_rows) and bool(runner_rows),
        "same_sample_count": len(legacy_rows) == len(runner_rows),
        "same_row_count_all_samples": len(all_row_counts) == 1,
        "validation_exact_matches_all_samples": all(
            int(row["row_count"]) == int(row["validation_exact_count"]) for row in rows
        ),
        "same_output_contract_all_samples": all_contracts == {OUTPUT_CONTRACT},
        "same_point_order_all_samples": len(all_point_orders) == 1,
        "runner_used_all_samples": all(bool(row["prepared_execution_session_runner_used"]) for row in runner_rows),
        "legacy_does_not_use_runner": all(not bool(row["prepared_execution_session_runner_used"]) for row in legacy_rows),
        "runner_runtime_trunk_executes_all_samples": all(
            bool(row["runtime_trunk_executes_end_to_end"]) for row in runner_rows
        ),
        "runner_internal_device_residency_all_samples": all(
            bool(row["internal_device_residency_between_rtdl_phases"]) for row in runner_rows
        ),
        "runner_step3_residency_default_ready_all_samples": all(
            bool(row["step3_residency_default_ready"]) for row in runner_rows
        ),
        "runner_hot_path_host_materialization_absent": all(
            not bool(row["hot_path_host_materialization"]) for row in runner_rows
        ),
        "runner_v4_external_zero_copy_absent": all(
            not bool(row["v4_embedding_or_external_zero_copy_authorized"]) for row in runner_rows
        ),
        "all_claim_flags_false": all(
            not bool(row["release_authorized"])
            and not bool(row["public_speedup_claim_authorized"])
            and not bool(row["broad_v3_faster_than_v2_claim_authorized"])
            and not bool(row["true_zero_copy_claim_authorized"])
            and not bool(row["v4_embedding_or_external_zero_copy_authorized"])
            and not bool(row["full_all_app_rerun_authorized_by_this_packet"])
            for row in rows
        ),
    }


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    speedups = summary["speedups"]
    lines = [
        "# Phoenix V3 RayJoin Point-Location Runner Focused POD A/B",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"- dataset: `{summary['dataset']}`",
        f"- point order: `{summary['point_order_mode']}`",
        f"- repeat/warmup/samples: `{summary['query_repeat']}` / `{summary['warmup']}` / `{summary['samples']}`",
        f"- row count: `{summary['row_count']}`",
        f"- output contract: `{summary['output_contract']}`",
        f"- median per-call speedup, legacy over runner: `{speedups['median_per_call_speedup_legacy_over_runner']}`",
        f"- median total-repeat speedup, legacy over runner: `{speedups['median_total_repeat_speedup_legacy_over_runner']}`",
        f"- runner Step-3 residency audit ready: `{summary.get('runner_step3_residency_default_ready')}`",
        f"- material Set-A candidate: `{summary['material_set_a_candidate']}`",
        "",
        "This packet compares the productized Phoenix V3 prepared-execution runner",
        "against the current OptiX relation-status corrected executor, not against Embree.",
        "It authorizes no release, broad V3-over-V2 wording, true-zero-copy wording,",
        "or all-app rerun.",
        "",
    ]
    return "\n".join(lines)


def _median(values: list[float]) -> float | None:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return float(statistics.median(finite)) if finite else None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
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
