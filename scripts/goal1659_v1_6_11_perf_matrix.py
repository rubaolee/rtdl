#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from rtdsl.python_rtdl_app_purity import python_rtdl_app_purity_matrix


VERSION = "v1.6.11"
GOAL = "Goal1659"
REPORT_STEM = "goal1659_v1_6_11_perf_matrix_2026-05-10"
DEFAULT_JSON = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _cmd(*parts: str) -> tuple[str, ...]:
    return tuple(parts)


def _entry(
    *,
    app: str,
    scope: str,
    local_command: tuple[str, ...] | None,
    pod_command: tuple[str, ...] | None,
    baseline: tuple[str, ...],
    acceptance: tuple[str, ...],
    notes: str,
) -> dict[str, Any]:
    purity = python_rtdl_app_purity_matrix()[app]
    support = rt.optix_app_performance_support(app)
    readiness = rt.optix_app_benchmark_readiness(app)
    return {
        "app": app,
        "purity_status": purity["status"],
        "generic_surface": purity["generic_surface"],
        "optix_performance_class": support.performance_class,
        "benchmark_readiness": readiness.status,
        "scope": scope,
        "local_command": None if local_command is None else list(local_command),
        "pod_command": None if pod_command is None else list(pod_command),
        "baseline": list(baseline),
        "acceptance": list(acceptance),
        "notes": notes,
        "public_claim_allowed_from_this_manifest_alone": False,
    }


def build_manifest() -> dict[str, Any]:
    entries = [
        _entry(
            app="database_analytics",
            scope="compact-summary DB prepared session only",
            local_command=_cmd("python", "scripts/goal756_db_prepared_session_perf.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal756_db_prepared_session_perf.py", "--backend", "optix", "--scenario", "sales_risk", "--copies", "20000", "--iterations", "10", "--output-mode", "compact_summary", "--strict", "--output-json", "docs/reports/goal1659_db_sales_risk_optix.json"),
            baseline=("cpu compact summary", "embree compact summary", "PostgreSQL/PostGIS when available"),
            acceptance=("strict parity", "phase timing", "same scenario/copies", "no DBMS-wide claim"),
            notes="Legacy native-customized surface; measure honestly but do not use as app-generic proof.",
        ),
        _entry(
            app="graph_analytics",
            scope="visibility-edge and native graph-ray candidate-generation subpaths",
            local_command=_cmd("python", "scripts/goal889_graph_visibility_optix_gate.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal889_graph_visibility_optix_gate.py", "--copies", "20000", "--output-mode", "summary", "--validation-mode", "analytic_summary", "--chunk-copies", "0", "--strict", "--output-json", "docs/reports/goal1659_graph_visibility_optix.json"),
            baseline=("cpu visibility/BFS/triangle reference", "embree graph-ray when available"),
            acceptance=("strict row digest", "phase status", "no graph-system claim"),
            notes="Measure RT-shaped graph subpaths only; Python graph bookkeeping remains outside RTDL performance claim.",
        ),
        _entry(
            app="apple_rt_demo",
            scope="excluded from v1.6.11 Embree+OptiX performance release",
            local_command=None,
            pod_command=None,
            baseline=("none",),
            acceptance=("documented exclusion",),
            notes="Apple RT is frozen/proof before v2.1 and not an NVIDIA pod target.",
        ),
        _entry(
            app="service_coverage_gaps",
            scope="prepared fixed-radius gap-summary decision",
            local_command=_cmd("python", "scripts/goal811_spatial_optix_summary_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal811_spatial_optix_summary_phase_profiler.py", "--scenario", "service_coverage_gaps", "--mode", "optix", "--copies", "20000", "--output-json", "docs/reports/goal1659_service_coverage_optix.json"),
            baseline=("cpu oracle summary", "embree prepared summary", "SciPy when used"),
            acceptance=("same generated data", "summary parity", "phase timing"),
            notes="Pure Python+RTDL candidate if public route uses generic fixed-radius primitives.",
        ),
        _entry(
            app="event_hotspot_screening",
            scope="prepared fixed-radius hotspot count-summary",
            local_command=_cmd("python", "scripts/goal811_spatial_optix_summary_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal811_spatial_optix_summary_phase_profiler.py", "--scenario", "event_hotspot_screening", "--mode", "optix", "--copies", "20000", "--output-json", "docs/reports/goal1659_event_hotspot_optix.json"),
            baseline=("cpu oracle summary", "embree prepared summary", "SciPy when used"),
            acceptance=("same generated data", "summary parity", "phase timing"),
            notes="Pure Python+RTDL candidate if public route uses generic fixed-radius primitives.",
        ),
        _entry(
            app="facility_knn_assignment",
            scope="coverage-threshold prepared decision only",
            local_command=_cmd("python", "scripts/goal887_prepared_decision_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal887_prepared_decision_phase_profiler.py", "--scenario", "facility_service_coverage", "--mode", "optix", "--copies", "20000", "--iterations", "10", "--radius", "1.0", "--skip-validation", "--output-json", "docs/reports/goal1659_facility_coverage_optix.json"),
            baseline=("cpu coverage-threshold oracle", "embree threshold summary"),
            acceptance=("same radius", "same generated points", "no ranked-KNN claim"),
            notes=(
                "Scalar-only route; ranked KNN assignment remains outside this performance scope. "
                "`--skip-validation` is used for the pod timing command because correctness must be "
                "checked in the matching focused gate while this row isolates the prepared threshold "
                "decision timing from unrelated ranked-KNN validation."
            ),
        ),
        _entry(
            app="road_hazard_screening",
            scope="prepared segment/polygon compact road-hazard summary",
            local_command=_cmd("python", "scripts/goal933_prepared_segment_polygon_optix_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal933_prepared_segment_polygon_optix_profiler.py", "--scenario", "road_hazard_prepared_summary", "--copies", "20000", "--iterations", "5", "--mode", "run", "--output-json", "docs/reports/goal1659_road_hazard_optix.json"),
            baseline=("cpu reference", "embree same semantics", "PostGIS when available"),
            acceptance=("strict parity", "prepared warm-query split", "no routing/GIS claim"),
            notes="Legacy native-customized surface; include to measure, not to claim app-generic purity.",
        ),
        _entry(
            app="segment_polygon_hitcount",
            scope="prepared segment/polygon hit-count summary",
            local_command=_cmd("python", "scripts/goal933_prepared_segment_polygon_optix_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal933_prepared_segment_polygon_optix_profiler.py", "--scenario", "segment_polygon_hitcount_prepared", "--copies", "256", "--iterations", "5", "--mode", "run", "--output-json", "docs/reports/goal1659_segment_polygon_hitcount_optix.json"),
            baseline=("cpu reference", "embree same semantics", "PostGIS when available"),
            acceptance=("strict parity", "prepared warm-query split", "no row-output claim"),
            notes="Legacy native-customized surface; likely not a v1.6.11 positive claim unless timing proves otherwise.",
        ),
        _entry(
            app="segment_polygon_anyhit_rows",
            scope="bounded pair-row output with overflow metadata",
            local_command=_cmd("python", "scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py", "--copies", "256", "--iterations", "5", "--output-capacity", "4096", "--mode", "run", "--output-json", "docs/reports/goal1659_segment_polygon_anyhit_rows_optix.json"),
            baseline=("cpu row digest", "embree row digest", "PostGIS when available"),
            acceptance=("strict row digest", "overflow false or fail-closed", "capacity recorded"),
            notes="Depends on experimental bounded collection; do not promote collect-k from this alone.",
        ),
        _entry(
            app="polygon_pair_overlap_area_rows",
            scope="native-assisted LSI/PIP candidate discovery plus exact-area continuation",
            local_command=_cmd("python", "scripts/goal877_polygon_overlap_optix_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal877_polygon_overlap_optix_phase_profiler.py", "--app", "pair_overlap", "--mode", "optix", "--copies", "20000", "--output-mode", "summary", "--validation-mode", "analytic_summary", "--chunk-copies", "100", "--output-json", "docs/reports/goal1659_pair_overlap_optix.json"),
            baseline=("cpu exact reference", "embree native-assisted candidate discovery", "PostGIS when available"),
            acceptance=("candidate and exact phases split", "summary parity", "no monolithic overlay claim"),
            notes="Legacy/native-assisted route; measure exact subpath only.",
        ),
        _entry(
            app="polygon_set_jaccard",
            scope="bounded candidate discovery plus exact Jaccard summary",
            local_command=_cmd("python", "scripts/goal877_polygon_overlap_optix_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal877_polygon_overlap_optix_phase_profiler.py", "--app", "jaccard", "--mode", "optix", "--copies", "20000", "--output-mode", "summary", "--validation-mode", "analytic_summary", "--chunk-copies", "20", "--output-json", "docs/reports/goal1659_jaccard_optix.json"),
            baseline=("cpu exact reference", "embree native-assisted candidate discovery", "PostGIS when available"),
            acceptance=("chunk-copies recorded", "summary parity", "no broad Jaccard claim"),
            notes="Collection-dependent; keep chunk boundary explicit.",
        ),
        _entry(
            app="hausdorff_distance",
            scope="directed threshold decision only",
            local_command=_cmd("python", "scripts/goal887_prepared_decision_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal887_prepared_decision_phase_profiler.py", "--scenario", "hausdorff_threshold", "--mode", "optix", "--copies", "20000", "--iterations", "10", "--radius", "0.4", "--output-json", "docs/reports/goal1659_hausdorff_threshold_optix.json"),
            baseline=("cpu directed-threshold oracle", "embree threshold summary"),
            acceptance=("same radius", "same point sets", "no exact Hausdorff claim"),
            notes="Scalar decision route; exact distance rows remain outside scope.",
        ),
        _entry(
            app="ann_candidate_search",
            scope="candidate-coverage threshold decision only",
            local_command=_cmd("python", "scripts/goal887_prepared_decision_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal887_prepared_decision_phase_profiler.py", "--scenario", "ann_candidate_coverage", "--mode", "optix", "--copies", "20000", "--iterations", "10", "--radius", "0.2", "--output-json", "docs/reports/goal1659_ann_candidate_optix.json"),
            baseline=("cpu candidate-coverage oracle", "embree threshold summary"),
            acceptance=("same radius", "same fixture", "no ANN-index claim"),
            notes="Scalar decision route; ranking/indexing remains outside scope.",
        ),
        _entry(
            app="outlier_detection",
            scope="prepared fixed-radius scalar threshold-count",
            local_command=_cmd("python", "scripts/goal757_optix_fixed_radius_prepared_perf.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal757_optix_fixed_radius_prepared_perf.py", "--copies", "20000", "--iterations", "10", "--result-mode", "threshold_count", "--output-json", "docs/reports/goal1659_outlier_fixed_radius_optix.json"),
            baseline=("cpu scalar threshold oracle", "embree scalar threshold summary", "SciPy when used"),
            acceptance=("same radius/threshold", "summary parity", "no label/row claim"),
            notes=(
                "Pure Python+RTDL candidate if kept on generic fixed-radius primitive route. "
                "This shares the Goal757 fixed-radius prepared fixture with dbscan_clustering; "
                "independent app meaning comes from the separate threshold-count/core-count "
                "interpretation, not a different native kernel."
            ),
        ),
        _entry(
            app="dbscan_clustering",
            scope="prepared fixed-radius scalar core-count",
            local_command=_cmd("python", "scripts/goal757_optix_fixed_radius_prepared_perf.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal757_optix_fixed_radius_prepared_perf.py", "--copies", "20000", "--iterations", "10", "--result-mode", "threshold_count", "--output-json", "docs/reports/goal1659_dbscan_fixed_radius_optix.json"),
            baseline=("cpu scalar core-count oracle", "embree scalar threshold summary", "SciPy when used"),
            acceptance=("same eps/minpts semantics", "summary parity", "no cluster-expansion claim"),
            notes=(
                "Pure Python+RTDL candidate for scalar core-count only. This shares the Goal757 "
                "fixed-radius prepared fixture with outlier_detection; independent app meaning "
                "comes from the separate threshold-count/core-count interpretation, not a "
                "different native kernel."
            ),
        ),
        _entry(
            app="robot_collision_screening",
            scope="prepared ray/triangle any-hit pose-count summary",
            local_command=_cmd("python", "scripts/goal760_optix_robot_pose_flags_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal760_optix_robot_pose_flags_phase_profiler.py", "--mode", "optix", "--pose-count", "200000", "--obstacle-count", "1024", "--iterations", "10", "--input-mode", "packed_arrays", "--result-mode", "pose_count", "--skip-validation", "--output-json", "docs/reports/goal1659_robot_pose_count_optix.json"),
            baseline=("cpu pose-count oracle", "embree any-hit pose-count"),
            acceptance=("same poses/obstacles", "validation separated", "no full-planning claim"),
            notes=(
                "Important positive-control candidate; still exact subpath only. "
                "`--skip-validation` is used for the pod timing command because validation is "
                "a separate correctness gate; this row isolates traversal/pose-count timing "
                "from mesh correctness and oracle-validation cost."
            ),
        ),
        _entry(
            app="barnes_hut_force_app",
            scope="node-coverage threshold decision only",
            local_command=_cmd("python", "scripts/goal887_prepared_decision_phase_profiler.py", "--help"),
            pod_command=_cmd("python3", "scripts/goal887_prepared_decision_phase_profiler.py", "--scenario", "barnes_hut_node_coverage", "--mode", "optix", "--body-count", "200000", "--iterations", "10", "--radius", "10.0", "--output-json", "docs/reports/goal1659_barnes_hut_node_coverage_optix.json"),
            baseline=("cpu node-coverage oracle", "embree threshold summary"),
            acceptance=("same body/node fixture", "summary parity", "no force-vector claim"),
            notes="Scalar decision route; force reduction remains Python/out of scope.",
        ),
        _entry(
            app="hiprt_ray_triangle_hitcount",
            scope="excluded from v1.6.11 Embree+OptiX performance release",
            local_command=None,
            pod_command=None,
            baseline=("none",),
            acceptance=("documented exclusion",),
            notes="HIPRT is frozen/proof before v2.1 and not an NVIDIA OptiX pod target.",
        ),
    ]
    return {
        "goal": GOAL,
        "version": VERSION,
        "release_intent": "final_python_rtdl_release_candidate_before_python_partner_rtdl",
        "release_authorized": False,
        "tag_authorized": False,
        "pod_required_for_final_perf_evidence": True,
        "pod_needed_now": False,
        "entries": entries,
        "entry_count": len(entries),
        "covered_apps": [entry["app"] for entry in entries],
        "all_public_apps_covered": set(entry["app"] for entry in entries) == set(rt.public_apps()),
        "blocked_claims": [
            "whole_app_speedup",
            "broad_rtx_or_gpu_acceleration",
            "true_zero_copy",
            "stable_collect_k_bounded_promotion",
            "python_partner_rtdl",
            "release_tag_action_before_perf_evidence_and_3ai_consensus",
        ],
        "pod_pass_criteria": {
            "active_pod_rows": 16,
            "minimum_completed_rows_for_release_candidate": 16,
            "required_positive_control_apps": ["robot_collision_screening"],
            "required_artifact_properties": [
                "commit_hash",
                "gpu_model",
                "driver_version",
                "optix_sdk_or_runtime_version",
                "command",
                "parity_or_strict_status",
                "phase_timing",
                "baseline_contract",
                "claim_boundary",
            ],
            "release_candidate_pass_rule": (
                "All 16 active pod rows must either produce accepted artifacts or the "
                "release candidate remains blocked. At least the robot positive-control "
                "row must complete. Every completed artifact must record parity/strict "
                "status and phase timing. Positive public speedup wording still requires "
                "a separate per-row review; mixed or slower rows may be published only as "
                "honest engineering evidence."
            ),
            "public_speedup_wording_rule": (
                "A row can be considered for positive wording only after same-contract "
                "baseline comparison, strict parity, at least three repeated timing samples "
                "where available, phase separation, and 3-AI review. This matrix alone "
                "authorizes no positive wording."
            ),
        },
        "boundary": (
            "This manifest prepares the detailed v1.6.11 performance test. It does "
            "not publish v1.6.11, does not authorize a tag, and does not authorize "
            "public speedup wording. Final NVIDIA OptiX evidence requires a pod "
            "after local commands and review gates are ready."
        ),
    }


def validate_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["version"] != VERSION:
        raise ValueError("Goal1659 version must remain v1.6.11")
    if payload["release_authorized"] is not False or payload["tag_authorized"] is not False:
        raise ValueError("Goal1659 must not authorize release/tag before evidence")
    if payload["pod_required_for_final_perf_evidence"] is not True:
        raise ValueError("Goal1659 final OptiX performance evidence requires a pod")
    if payload["pod_needed_now"] is not False:
        raise ValueError("Goal1659 local preparation must finish before starting a pod")
    public_apps = set(rt.public_apps())
    covered = set(payload["covered_apps"])
    if covered != public_apps:
        raise ValueError(f"Goal1659 app coverage mismatch: missing={sorted(public_apps - covered)} extra={sorted(covered - public_apps)}")
    if payload["entry_count"] != len(public_apps):
        raise ValueError("Goal1659 entry count must match public app count")
    pod_commands = [entry for entry in payload["entries"] if entry["pod_command"]]
    if len(pod_commands) < 12:
        raise ValueError("Goal1659 must define a broad OptiX pod command batch")
    for entry in payload["entries"]:
        if entry["public_claim_allowed_from_this_manifest_alone"] is not False:
            raise ValueError("Goal1659 manifest alone must not authorize claims")
        if not entry["scope"] or not entry["acceptance"] or not entry["baseline"]:
            raise ValueError(f"Goal1659 entry incomplete: {entry['app']}")
    for claim in (
        "whole_app_speedup",
        "broad_rtx_or_gpu_acceleration",
        "true_zero_copy",
        "stable_collect_k_bounded_promotion",
        "python_partner_rtdl",
    ):
        if claim not in payload["blocked_claims"]:
            raise ValueError(f"Goal1659 blocked claim missing: {claim}")
    criteria = payload.get("pod_pass_criteria")
    if not isinstance(criteria, dict):
        raise ValueError("Goal1659 requires pod_pass_criteria")
    if criteria.get("active_pod_rows") != len(pod_commands):
        raise ValueError("Goal1659 pod_pass_criteria active row count mismatch")
    if criteria.get("minimum_completed_rows_for_release_candidate") != len(pod_commands):
        raise ValueError("Goal1659 release candidate requires all active pod rows")
    if "robot_collision_screening" not in tuple(criteria.get("required_positive_control_apps", ())):
        raise ValueError("Goal1659 requires robot positive-control row")
    for phrase in (
        "All 16 active pod rows",
        "robot positive-control",
        "parity/strict status",
        "phase timing",
        "separate per-row review",
    ):
        if phrase not in str(criteria.get("release_candidate_pass_rule", "")):
            raise ValueError("Goal1659 pod pass rule is incomplete")
    if "authorizes no positive wording" not in str(criteria.get("public_speedup_wording_rule", "")):
        raise ValueError("Goal1659 public speedup wording rule is incomplete")
    return payload


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1659 v1.6.11 Performance Matrix",
        "",
        "## Verdict",
        "",
        "`v1_6_11_perf_matrix_prepared_not_released`",
        "",
        "`v1.6.11` is proposed as the final Python+RTDL-only release candidate before Python+partner+RTDL. This file prepares the detailed performance test matrix; it does not publish the release or authorize a tag.",
        "",
        "## Pod Need",
        "",
        "- Pod needed now: `False`.",
        "- Pod required for final NVIDIA OptiX performance evidence: `True`.",
        "- Start a pod only after local command/help checks, manifest validation, and review gates pass.",
        "",
        "## App Matrix",
        "",
        "| App | Purity | Scope | Pod command? | Claim from manifest? |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in payload["entries"]:
        lines.append(
            "| `{app}` | `{purity}` | {scope} | `{pod}` | `False` |".format(
                app=entry["app"],
                purity=entry["purity_status"],
                scope=entry["scope"],
                pod=bool(entry["pod_command"]),
            )
        )
    lines.extend(
        [
            "",
            "## Pod Pass Criteria",
            "",
            payload["pod_pass_criteria"]["release_candidate_pass_rule"],
            "",
            payload["pod_pass_criteria"]["public_speedup_wording_rule"],
            "",
            "## Blocked Claims",
            "",
        ]
    )
    for claim in payload["blocked_claims"]:
        lines.append(f"- `{claim}`")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the v1.6.11 all-app performance matrix.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = validate_manifest(build_manifest())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"version": VERSION, "entry_count": payload["entry_count"], "pod_required": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
