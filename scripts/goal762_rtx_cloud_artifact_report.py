#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SUPPORTED_ARTIFACT_APPS = frozenset(
    {
        "database_analytics",
        "outlier_detection",
        "dbscan_clustering",
        "robot_collision_screening",
        "service_coverage_gaps",
        "event_hotspot_screening",
        "hausdorff_distance",
        "ann_candidate_search",
        "facility_knn_assignment",
        "barnes_hut_force_app",
        "graph_analytics",
        "road_hazard_screening",
        "segment_polygon_hitcount",
        "segment_polygon_anyhit_rows",
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
    }
)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _output_path(command: list[str]) -> Path | None:
    for index, token in enumerate(command):
        if token == "--output-json" and index + 1 < len(command):
            return ROOT / command[index + 1]
    return None


def _median(stats: Any) -> float | None:
    if isinstance(stats, dict) and isinstance(stats.get("median_sec"), (int, float)):
        return float(stats["median_sec"])
    return None


def _find_result_for_app(payload: dict[str, Any], app: str) -> dict[str, Any] | None:
    results = payload.get("results")
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("app") == app:
            return result
    return None


def _sum_phase_key(phases: Any, key: str) -> float | None:
    if not isinstance(phases, dict):
        return None
    total = 0.0
    found = False
    for value in phases.values():
        if isinstance(value, dict) and isinstance(value.get(key), (int, float)):
            total += float(value[key])
            found = True
    return total if found else None


def _sum_phase_prefix(phases: Any, prefix: str) -> float | None:
    if not isinstance(phases, dict):
        return None
    total = 0.0
    found = False
    for value in phases.values():
        if not isinstance(value, dict):
            continue
        for phase_key, phase_value in value.items():
            if phase_key.startswith(prefix) and isinstance(phase_value, (int, float)):
                total += float(phase_value)
                found = True
    return total if found else None


def _record_by_label(records: Any, label: str) -> dict[str, Any]:
    if not isinstance(records, list):
        return {}
    for record in records:
        if isinstance(record, dict) and record.get("label") == label:
            return record
    return {}


def _contract_check(contract: Any, phase_source: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {
            "cloud_contract_status": "missing",
            "cloud_contract_missing_phases": [],
        }
    required = contract.get("required_phase_groups")
    if not isinstance(required, (list, tuple)):
        return {
            "cloud_contract_status": "malformed",
            "cloud_contract_missing_phases": [],
        }
    if not isinstance(phase_source, dict):
        phase_source = {}
    missing = [str(key) for key in required if str(key) not in phase_source]
    return {
        "cloud_contract_status": "ok" if not missing else "missing_required_phases",
        "cloud_contract_missing_phases": missing,
        "cloud_contract_claim_scope": contract.get("claim_scope"),
        "cloud_contract_non_claim": contract.get("non_claim"),
    }


def _baseline_review_contract_check(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {"baseline_review_contract_status": "missing"}
    required = {
        "status",
        "minimum_repeated_runs",
        "requires_correctness_parity",
        "requires_phase_separation",
        "forbidden_comparison",
        "comparable_metric_scope",
        "required_baselines",
        "required_phases",
        "claim_limit",
    }
    missing = sorted(required - set(contract))
    status = "ok"
    if missing:
        status = "malformed"
    elif contract.get("status") != "required_before_public_speedup_claim":
        status = "bad_status"
    elif not contract.get("requires_correctness_parity"):
        status = "missing_correctness_parity"
    elif not contract.get("requires_phase_separation"):
        status = "missing_phase_separation"
    elif not isinstance(contract.get("required_baselines"), list) or not contract.get("required_baselines"):
        status = "missing_required_baselines"
    elif not isinstance(contract.get("required_phases"), list) or not contract.get("required_phases"):
        status = "missing_required_phases"
    return {
        "baseline_review_contract_status": status,
        "baseline_review_contract_missing_fields": missing,
        "baseline_review_contract_scope": contract.get("comparable_metric_scope"),
        "baseline_review_contract_claim_limit": contract.get("claim_limit"),
    }


def _extract_artifact_metrics(entry: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    app = str(entry["app"])
    if app == "database_analytics":
        results = artifact.get("results")
        optix = None
        if isinstance(results, list):
            optix = next((row for row in results if isinstance(row, dict) and row.get("backend") == "optix"), None)
        if not isinstance(optix, dict):
            return {"artifact_status": "unrecognized", "note": "no optix result row found"}
        metrics = {
            "artifact_status": "ok",
            "schema_version": optix.get("schema_version", artifact.get("schema_version")),
            "one_shot_total_sec": optix.get("one_shot_total_sec"),
            "prepare_total_sec": optix.get("prepared_session_prepare_total_sec"),
            "prepare_sec": optix.get("prepared_session_prepare_total_sec"),
            "warm_query_median_sec": _median(optix.get("prepared_session_warm_query_sec")),
            "close_sec": optix.get("prepared_session_close_sec"),
            "speedup_one_shot_over_warm_query_median": optix.get("speedup_one_shot_over_warm_query_median"),
            "phase_contract_present": isinstance(optix.get("phase_contract"), dict),
            "db_query_total_sec": _sum_phase_prefix(optix.get("reported_run_phases_sec"), "query_"),
            "postprocess_median_sec": _sum_phase_key(
                optix.get("reported_run_phases_sec"),
                "python_summary_postprocess_sec",
            ),
            "db_run_phase_modes": optix.get("reported_run_phase_modes"),
            "db_run_phase_totals": optix.get("reported_run_phase_totals_sec"),
            "db_native_phase_groups": sorted((optix.get("reported_native_db_phases_sec") or {}).keys())
            if isinstance(optix.get("reported_native_db_phases_sec"), dict)
            else [],
            "db_native_phase_totals": optix.get("reported_native_db_phase_totals_sec"),
            "db_review_observation": optix.get("db_review_observation"),
        }
        metrics.update(_contract_check(optix.get("cloud_claim_contract"), optix))
        return metrics
    if app in {"outlier_detection", "dbscan_clustering"}:
        result = _find_result_for_app(artifact, app)
        if result is None:
            return {"artifact_status": "unrecognized", "note": f"no {app} result row found"}
        metrics = {
            "artifact_status": "ok",
            "schema_version": result.get("schema_version", artifact.get("schema_version")),
            "one_shot_total_sec": result.get("one_shot_total_sec"),
            "pack_points_sec": result.get("prepared_optix_pack_points_sec"),
            "prepare_sec": result.get("prepared_optix_prepare_sec"),
            "warm_query_median_sec": _median(result.get("prepared_optix_warm_query_sec")),
            "postprocess_median_sec": _median(result.get("prepared_optix_postprocess_sec")),
            "validation_median_sec": _median(result.get("prepared_optix_validation_sec")),
            "validation_mode": result.get("validation_mode"),
            "result_mode": result.get("result_mode"),
            "threshold_reached_count": (result.get("prepared_output") or {}).get("threshold_reached_count")
            if isinstance(result.get("prepared_output"), dict)
            else None,
            "speedup_one_shot_over_warm_query_median": result.get("speedup_one_shot_over_warm_query_median"),
            "phase_contract_present": isinstance(result.get("phase_contract"), dict),
        }
        metrics.update(_contract_check(result.get("cloud_claim_contract"), result))
        return metrics
    if app == "robot_collision_screening":
        phases = artifact.get("phases")
        if not isinstance(phases, dict):
            return {"artifact_status": "unrecognized", "note": "no phases object found"}
        metrics = {
            "artifact_status": "ok",
            "schema_version": artifact.get("schema_version"),
            "mode": artifact.get("mode"),
            "input_mode": artifact.get("input_mode"),
            "result_mode": artifact.get("result_mode"),
            "pose_count": artifact.get("pose_count"),
            "edge_ray_count": artifact.get("edge_ray_count"),
            "colliding_pose_count": (artifact.get("result") or {}).get("colliding_pose_count")
            if isinstance(artifact.get("result"), dict)
            else None,
            "prepare_scene_sec": phases.get("optix_prepare_scene_sec"),
            "prepare_rays_sec": phases.get("optix_prepare_rays_sec"),
            "prepare_pose_indices_sec": phases.get("optix_prepare_pose_indices_sec"),
            "warm_query_median_sec": _median(phases.get("prepared_pose_flags_warm_query_sec")),
            "oracle_validate_sec": phases.get("oracle_validate_sec"),
            "matches_oracle": artifact.get("matches_oracle"),
            "validated": artifact.get("validated"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), phases))
        return metrics
    if app in {"service_coverage_gaps", "event_hotspot_screening"}:
        scenario = artifact.get("scenario")
        if not isinstance(scenario, dict):
            return {"artifact_status": "unrecognized", "note": "no scenario object found"}
        timings = scenario.get("timings_sec")
        if not isinstance(timings, dict):
            return {"artifact_status": "unrecognized", "note": "no scenario timings object found"}
        metrics = {
            "artifact_status": "ok",
            "schema_version": artifact.get("schema_version"),
            "mode": scenario.get("mode"),
            "input_build_sec": timings.get("input_build"),
            "prepare_sec": timings.get("optix_prepare"),
            "warm_query_median_sec": timings.get("optix_query"),
            "postprocess_median_sec": timings.get("python_postprocess"),
            "native_summary_row_count": (scenario.get("result") or {}).get("native_summary_row_count")
            if isinstance(scenario.get("result"), dict)
            else None,
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), timings))
        return metrics
    if app in {"hausdorff_distance", "ann_candidate_search", "facility_knn_assignment", "barnes_hut_force_app"}:
        scenario = artifact.get("scenario")
        if not isinstance(scenario, dict):
            return {"artifact_status": "unrecognized", "note": "no scenario object found"}
        timings = scenario.get("timings_sec")
        if not isinstance(timings, dict):
            return {"artifact_status": "unrecognized", "note": "no scenario timings object found"}
        result = scenario.get("result") if isinstance(scenario.get("result"), dict) else {}
        metrics = {
            "artifact_status": "ok",
            "schema_version": artifact.get("schema_version"),
            "scenario": scenario.get("scenario"),
            "mode": scenario.get("mode"),
            "input_build_sec": timings.get("input_build_sec"),
            "pack_points_sec": timings.get("point_pack_sec"),
            "prepare_sec": timings.get("optix_prepare_sec"),
            "warm_query_median_sec": _median(timings.get("optix_query_sec")),
            "postprocess_median_sec": _median(timings.get("python_postprocess_sec")),
            "validation_median_sec": _median(timings.get("validation_sec")),
            "close_sec": timings.get("optix_close_sec"),
            "threshold_reached_count": result.get("threshold_reached_count"),
            "matches_oracle": result.get("matches_oracle"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), timings))
        return metrics
    if app == "graph_analytics":
        records = artifact.get("records")
        if not isinstance(records, list):
            return {"artifact_status": "unrecognized", "note": "no records array found"}
        by_label = {
            str(record.get("label")): record
            for record in records
            if isinstance(record, dict) and record.get("label") is not None
        }
        cpu = (
            by_label.get("cpu_python_reference_visibility_edges")
            or by_label.get("cpu_python_reference")
            or {}
        )
        analytic = by_label.get("analytic_expected_visibility_edges", {})
        optix = by_label.get("optix_visibility_anyhit", {})
        metrics = {
            "artifact_status": "ok",
            "output_mode": artifact.get("output_mode"),
            "validation_mode": artifact.get("validation_mode"),
            "chunk_copies": artifact.get("chunk_copies"),
            "strict_pass": artifact.get("strict_pass"),
            "strict_failure_count": len(artifact.get("strict_failures", ()))
            if isinstance(artifact.get("strict_failures"), list)
            else None,
            "cpu_reference_sec": cpu.get("sec"),
            "analytic_reference_present": bool(analytic),
            "warm_query_median_sec": optix.get("sec"),
            "optix_native_status": optix.get("status"),
            "optix_native_parity": (
                optix.get("parity_vs_cpu_python_reference")
                if "parity_vs_cpu_python_reference" in optix
                else optix.get("parity_vs_analytic_expected")
            ),
        }
        phase_source = dict(by_label)
        phase_source.update({
            "cpu_python_reference": cpu,
            "cpu_python_reference_visibility_edges": cpu,
            "analytic_expected_visibility_edges": analytic,
            "optix_visibility_anyhit": optix,
            "strict_pass": artifact.get("strict_pass"),
            "strict_failures": artifact.get("strict_failures"),
        })
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), phase_source))
        return metrics
    if app == "road_hazard_screening":
        records = artifact.get("records")
        if not isinstance(records, list):
            return {"artifact_status": "unrecognized", "note": "no records array found"}
        cpu = _record_by_label(records, "cpu_python_reference")
        optix = _record_by_label(records, "optix_native")
        metrics = {
            "artifact_status": "ok",
            "output_mode": artifact.get("output_mode"),
            "strict_pass": artifact.get("strict_pass"),
            "strict_failure_count": len(artifact.get("strict_failures", ()))
            if isinstance(artifact.get("strict_failures"), list)
            else None,
            "cpu_reference_sec": cpu.get("sec"),
            "warm_query_median_sec": optix.get("sec"),
            "optix_native_status": optix.get("status"),
            "optix_native_parity": optix.get("parity_vs_cpu_python_reference"),
        }
        phase_source = {
            "cpu_python_reference": cpu,
            "optix_native": optix,
            "strict_pass": artifact.get("strict_pass"),
            "strict_failures": artifact.get("strict_failures"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), phase_source))
        return metrics
    if app == "segment_polygon_hitcount":
        records = artifact.get("records")
        if not isinstance(records, list):
            return {"artifact_status": "unrecognized", "note": "no records array found"}
        by_label = {
            str(record.get("label")): record
            for record in records
            if isinstance(record, dict)
        }
        metrics = {
            "artifact_status": "ok",
            "schema_version": artifact.get("schema_version"),
            "strict_pass": artifact.get("strict_pass"),
            "strict_failure_count": len(artifact.get("strict_failures", ()))
            if isinstance(artifact.get("strict_failures"), list)
            else None,
            "cpu_reference_sec": by_label.get("cpu_python_reference", {}).get("sec"),
            "optix_host_indexed_sec": by_label.get("optix_host_indexed", {}).get("sec"),
            "optix_native_sec": by_label.get("optix_native", {}).get("sec"),
            "optix_native_status": by_label.get("optix_native", {}).get("status"),
            "optix_native_parity": by_label.get("optix_native", {}).get("parity_vs_cpu_python_reference"),
            "postgis_sec": by_label.get("postgis", {}).get("sec"),
            "postgis_parity": by_label.get("postgis", {}).get("parity_vs_cpu_python_reference"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), artifact))
        return metrics
    if app == "segment_polygon_anyhit_rows":
        records = artifact.get("records")
        if not isinstance(records, list):
            return {"artifact_status": "unrecognized", "note": "no records array found"}
        cpu = _record_by_label(records, "cpu_python_reference")
        native = _record_by_label(records, "optix_native_bounded")
        metrics = {
            "artifact_status": "ok",
            "strict_pass": artifact.get("strict_pass"),
            "strict_failure_count": len(artifact.get("strict_failures", ()))
            if isinstance(artifact.get("strict_failures"), list)
            else None,
            "output_capacity": artifact.get("output_capacity"),
            "cpu_reference_sec": cpu.get("sec"),
            "warm_query_median_sec": native.get("sec"),
            "optix_native_status": native.get("status"),
            "optix_native_parity": native.get("parity_vs_cpu_python_reference"),
            "emitted_count": native.get("emitted_count"),
            "copied_count": native.get("copied_count"),
            "overflowed": native.get("overflowed"),
        }
        phase_source = {
            "records": records,
            "row_digest": native.get("row_digest"),
            "emitted_count": native.get("emitted_count"),
            "copied_count": native.get("copied_count"),
            "overflowed": native.get("overflowed"),
            "strict_pass": artifact.get("strict_pass"),
            "strict_failures": artifact.get("strict_failures"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), phase_source))
        return metrics
    if app in {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
        phases = artifact.get("phases")
        if not isinstance(phases, dict):
            return {"artifact_status": "unrecognized", "note": "no phases object found"}
        metrics = {
            "artifact_status": "ok",
            "mode": artifact.get("mode"),
            "output_mode": artifact.get("output_mode"),
            "validation_mode": artifact.get("validation_mode"),
            "chunk_copies": artifact.get("chunk_copies"),
            "input_build_sec": phases.get("input_build_sec"),
            "cpu_reference_sec": phases.get("cpu_reference_sec"),
            "warm_query_median_sec": phases.get("optix_candidate_discovery_sec"),
            "postprocess_median_sec": phases.get("cpu_exact_refinement_sec"),
            "parity_vs_cpu": artifact.get("parity_vs_cpu"),
            "rt_core_candidate_discovery_active": (artifact.get("optix_metadata") or {}).get(
                "rt_core_candidate_discovery_active"
            )
            if isinstance(artifact.get("optix_metadata"), dict)
            else None,
        }
        phase_source = {
            "input_build_sec": phases.get("input_build_sec"),
            "cpu_reference_sec": phases.get("cpu_reference_sec"),
            "optix_candidate_discovery_sec": phases.get("optix_candidate_discovery_sec"),
            "cpu_exact_refinement_sec": phases.get("cpu_exact_refinement_sec"),
            "parity_vs_cpu": artifact.get("parity_vs_cpu"),
            "rt_core_candidate_discovery_active": metrics["rt_core_candidate_discovery_active"],
            "validation_mode": artifact.get("validation_mode"),
            "output_mode": artifact.get("output_mode"),
        }
        metrics.update(_contract_check(artifact.get("cloud_claim_contract"), phase_source))
        return metrics
    return {"artifact_status": "not_applicable", "note": "no extractor for app"}


def analyze(summary_path: Path) -> dict[str, Any]:
    summary = _load_json(summary_path)
    rows: list[dict[str, Any]] = []
    for item in summary.get("results", []):
        if not isinstance(item, dict):
            continue
        result = item.get("result", {})
        command = result.get("command", []) if isinstance(result, dict) else []
        artifact_path = _output_path(command) if isinstance(command, list) else None
        row = {
            "app": item.get("app"),
            "path_name": item.get("path_name"),
            "claim_scope": item.get("claim_scope"),
            "non_claim": item.get("non_claim"),
            "runner_status": result.get("status") if isinstance(result, dict) else "unknown",
            "runner_returncode": result.get("returncode") if isinstance(result, dict) else None,
            "artifact_path": str(artifact_path) if artifact_path is not None else None,
        }
        row.update(_baseline_review_contract_check(item.get("baseline_review_contract")))
        if row["runner_status"] == "dry_run":
            row["artifact_status"] = "dry_run_not_expected"
        elif artifact_path is None:
            row["artifact_status"] = "missing_output_json_argument"
        elif not artifact_path.exists():
            row["artifact_status"] = "missing"
        else:
            try:
                artifact = _load_json(artifact_path)
                row.update(_extract_artifact_metrics(item, artifact))
            except Exception as exc:
                row["artifact_status"] = "parse_failed"
                row["note"] = str(exc)
        rows.append(row)
    failures = [
        row for row in rows
        if row.get("runner_status") not in {"ok", "dry_run"}
        or row.get("artifact_status") in {"missing", "parse_failed", "unrecognized", "missing_output_json_argument"}
        or row.get("cloud_contract_status") in {"missing", "malformed", "missing_required_phases"}
        or (row.get("runner_status") != "dry_run" and row.get("baseline_review_contract_status") != "ok")
    ]
    return {
        "suite": "goal762_rtx_cloud_artifact_report",
        "summary_path": str(summary_path),
        "runner_status": summary.get("status"),
        "dry_run": bool(summary.get("dry_run")),
        "git_head": summary.get("git_head"),
        "nvidia_smi": summary.get("nvidia_smi"),
        "entry_count": len(rows),
        "failure_count": len(failures),
        "rows": rows,
        "status": "ok" if not failures else "needs_attention",
        "boundary": (
            "This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; "
            "claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal762 RTX Cloud Artifact Report",
        "",
        "## Verdict",
        "",
        f"Status: `{payload['status']}`.",
        "",
        payload["boundary"],
        "",
        "## Run Metadata",
        "",
        f"- summary_path: `{payload['summary_path']}`",
        f"- runner_status: `{payload.get('runner_status')}`",
        f"- dry_run: `{payload.get('dry_run')}`",
        f"- git_head: `{payload.get('git_head')}`",
        f"- failure_count: `{payload.get('failure_count')}`",
        "",
        "## Artifact Table",
        "",
        "| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        validation = row.get("validation_median_sec", row.get("oracle_validate_sec"))
        input_pack = row.get("pack_points_sec", row.get("prepare_pose_indices_sec"))
        if input_pack is None:
            input_pack = row.get("input_build_sec", row.get("prepare_sec"))
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row.get("app")),
                    _fmt(row.get("path_name")),
                    _fmt(row.get("runner_status")),
                    _fmt(row.get("artifact_status")),
                    _fmt(input_pack),
                    _fmt(row.get("warm_query_median_sec")),
                    _fmt(row.get("postprocess_median_sec")),
                    _fmt(validation),
                    _fmt(row.get("non_claim")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Baseline Review Contracts",
            "",
            "| App | Path | Status | Comparable metric scope | Claim limit |",
            "|---|---|---:|---|---|",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row.get("app")),
                    _fmt(row.get("path_name")),
                    _fmt(row.get("baseline_review_contract_status")),
                    _fmt(row.get("baseline_review_contract_scope")),
                    _fmt(row.get("baseline_review_contract_claim_limit")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Required Review",
            "",
            "- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.",
            "- Confirm all `artifact_status` cells are `ok` before interpreting timings.",
            "- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.",
            "- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze Goal761 RTX cloud artifacts and write a conservative report.")
    parser.add_argument("--summary-json", default="docs/reports/goal761_rtx_cloud_run_all_summary.json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md", default="docs/reports/goal762_rtx_cloud_artifact_report.md")
    args = parser.parse_args(argv)
    payload = analyze(ROOT / args.summary_json)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
