from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .current_embree_cpu_partner_reference import (
    CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
    current_embree_cpu_partner_reference_rows,
)
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


EMBREE_OPTIMIZATION_AUDIT_VERSION = "rtdl.v2_11.embree_optimization_audit.goal4343.v1"
EMBREE_OPTIMIZATION_AUDIT_STATUS = "internal_embree_optimization_audit_not_comparison_or_release_authorization"
EMBREE_OPTIMIZATION_AUDIT_CLAIM_BOUNDARY = (
    "Goal4343 audits the current Embree CPU campaign for optimized-comparison "
    "readiness. It does not authorize release action, public speedup wording, "
    "whole-app acceleration wording, Intel GPU performance wording, broad RT-core "
    "wording, paper reproduction wording, automatic partner selection, or "
    "app-specific native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HISTORICAL_PACKET = ROOT / "docs" / "reports" / "goal4298_v2_11_embree_cpu_partner_reference_local_linux.json"
DEFAULT_RTNN_FOLLOWUP = ROOT / "docs" / "reports" / "goal4308_rtnn_embree_front_door_local_linux.json"
DEFAULT_LIBRTS_OPTIMIZED_SUMMARY = (
    ROOT / "docs" / "reports" / "goal4340_embree_native_aabb_index_local_linux" / "summary.json"
)
DEFAULT_SAME_CONTRACT_SCALE_PROBE_SUMMARY = (
    ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe" / "summary.json"
)


GOAL4344_SCALE_CASES_BY_APP = {
    "hausdorff_xhd": "hausdorff_embree_threshold_1024",
    "robot_collision": "robot_embree_prepared_buffers_1024_128_4_50000",
    "contact_manifold": "contact_embree_grid64_witness128",
    "raydb_style": "raydb_embree_count_generated_262144_1024",
    "triangle_counting": "triangle_embree_rtgraph2a1_2048",
}


EMBREE_ROUTE_AUDIT: dict[str, dict[str, str]] = {
    "hausdorff_xhd": {
        "optimization_status": "scaled_threshold_count_route_available",
        "comparison_readiness": "same_contract_scale_row_ready",
        "next_action": "carry the threshold-count scale row into the internal comparison packet as a query-ratio candidate",
        "reason": "Goal4344 supplies the Embree threshold contract at copies=1024 with the current OptiX repeat/warmup policy.",
    },
    "spatial_rayjoin": {
        "optimization_status": "python_continuation_route_present_contract_split",
        "comparison_readiness": "needs_contract_split_before_optimization",
        "next_action": "choose PIP count, LSI scalar count, or overlay active count before optimizing/running Embree",
        "reason": "Current Embree row is PIP count via generic kernel plus Python continuation, while OptiX evidence is mixed-route RayJoin.",
    },
    "rt_dbscan": {
        "optimization_status": "prepared_rows_tiny_python_continuation",
        "comparison_readiness": "needs_summary_or_signature_contract_choice",
        "next_action": "choose fixed-radius neighbor rows or grouped-signature contract, then optimize Embree at scale",
        "reason": "Current Embree row is tiny prepared rows; OptiX configured route is grouped-stream plus Numba signature.",
    },
    "robot_collision": {
        "optimization_status": "scaled_prepared_buffer_route_available",
        "comparison_readiness": "same_scale_boundary_limited_row_ready",
        "next_action": "use traversal-only internal comparison, or run an OptiX prepared-buffer flags row if a clean output-contract ratio is needed",
        "reason": "Goal4344 supplies the scaled Embree prepared-buffer row; the current OptiX scale row is an OptiX-only device-count path.",
    },
    "contact_manifold": {
        "optimization_status": "scaled_collect_k_route_available",
        "comparison_readiness": "same_contract_scale_row_ready",
        "next_action": "carry the collect-k scale row into the internal comparison packet as a query-ratio candidate",
        "reason": "Goal4344 supplies the same grid size, witness capacity, and repeat count as the current OptiX collect-k row.",
    },
    "raydb_style": {
        "optimization_status": "scaled_primitive_first_grouped_count_available",
        "comparison_readiness": "same_scale_boundary_limited_row_ready",
        "next_action": "compare native grouped-reduction traversal cautiously, or add a prepared Embree resident row before clean end-to-end ratios",
        "reason": "Goal4344 supplies the generated 262144-row / 1024-group Embree row; the current OptiX row is a prepared resident v2.5 path.",
    },
    "barnes_hut": {
        "optimization_status": "node_coverage_contract_split",
        "comparison_readiness": "needs_contract_choice_before_optimization",
        "next_action": "choose node-coverage or exact-force configured route before optimizing Embree/CPU side",
        "reason": "Embree row is prepared node coverage, while current NVIDIA scale row is Numba exact-force.",
    },
    "librts_spatial_index": {
        "optimization_status": "optimized_native_aabb_route_available",
        "comparison_readiness": "first_measured_pair_ready",
        "next_action": "scale the optimized native AABB row and keep validation row separate from performance rows",
        "reason": "Goal4340 replaced the old columnar fallback with native Embree AABB collision traversal.",
    },
    "rtnn": {
        "optimization_status": "embree_front_door_present_contract_split",
        "comparison_readiness": "needs_3d_ranked_or_2d_ann_contract_choice",
        "next_action": "decide between current 2-D ANN candidate-quality route and OptiX 3-D ranked-summary contract",
        "reason": "Goal4308 added an Embree 2-D ANN candidate-quality front door, not the OptiX 3-D ranked-summary contract.",
    },
    "triangle_counting": {
        "optimization_status": "scaled_native_summary_route_available",
        "comparison_readiness": "same_contract_scale_row_ready",
        "next_action": "carry the RT-Graph 2A1 scale row into the internal comparison packet as a query-ratio candidate",
        "reason": "Goal4344 supplies the same RT-Graph fixture, copy count, output detail, repeat, and warmup as the current OptiX row.",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _rows_by_app(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {}
    return {str(row.get("app")): row for row in rows if isinstance(row, dict) and row.get("app")}


def embree_optimization_audit(
    *,
    historical_packet_path: Path | None = None,
    rtnn_followup_path: Path | None = None,
    librts_optimized_summary_path: Path | None = None,
    same_contract_scale_probe_summary_path: Path | None = None,
) -> dict[str, Any]:
    historical_path = historical_packet_path or DEFAULT_HISTORICAL_PACKET
    rtnn_path = rtnn_followup_path or DEFAULT_RTNN_FOLLOWUP
    librts_path = librts_optimized_summary_path or DEFAULT_LIBRTS_OPTIMIZED_SUMMARY
    scale_probe_path = same_contract_scale_probe_summary_path or DEFAULT_SAME_CONTRACT_SCALE_PROBE_SUMMARY
    historical = _load_json(historical_path)
    rtnn_followup = _load_json(rtnn_path)
    librts_summary = _load_json(librts_path)
    scale_probe = _load_json(scale_probe_path)
    historical_rows = _rows_by_app(historical)
    rtnn_rows = _rows_by_app(rtnn_followup)
    registry = {row["app"]: row for row in current_embree_cpu_partner_reference_rows()}
    scale_cases = {str(case.get("name")): case for case in scale_probe.get("cases", []) if isinstance(case, dict)}

    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for app in V2_8_PROMOTED_BENCHMARK_APPS:
        if app not in registry:
            errors.append(f"{app}: missing current Embree registry row")
            continue
        audit = EMBREE_ROUTE_AUDIT[app]
        registry_row = registry[app]
        historical_row = historical_rows.get(app)
        followup_row = rtnn_rows.get(app)
        if app == "rtnn":
            artifact_status = "current_followup_pass" if followup_row and followup_row.get("status") == "pass" else "missing_current_followup"
            artifact_row_id = followup_row.get("row_id") if followup_row else None
            historical_row_id = historical_row.get("row_id") if historical_row else None
            if artifact_row_id != registry_row["row_id"]:
                errors.append("rtnn: current follow-up artifact does not match registry row")
        elif app == "librts_spatial_index":
            artifact_status = "optimized_goal4340_summary_available"
            artifact_row_id = registry_row["row_id"]
            historical_row_id = historical_row.get("row_id") if historical_row else None
            if librts_summary.get("large_1024_skip_counts", {}).get("native_index") != "embree_native_aabb_collision_index":
                errors.append("librts_spatial_index: optimized native AABB summary is missing")
        elif app in GOAL4344_SCALE_CASES_BY_APP:
            artifact_name = GOAL4344_SCALE_CASES_BY_APP[app]
            scale_case = scale_cases.get(artifact_name)
            artifact_status = (
                "goal4344_same_contract_scale_probe_pass"
                if scale_case and scale_case.get("status") == 0 and scale_case.get("json_parseable") is True
                else "missing_or_failed_goal4344_scale_probe"
            )
            artifact_row_id = registry_row["row_id"]
            historical_row_id = historical_row.get("row_id") if historical_row else None
            if artifact_status != "goal4344_same_contract_scale_probe_pass":
                errors.append(f"{app}: Goal4344 scale probe missing or failed")
        else:
            artifact_status = "historical_packet_pass" if historical_row and historical_row.get("status") == "pass" else "missing_or_failed_historical_row"
            artifact_row_id = historical_row.get("row_id") if historical_row else None
            historical_row_id = artifact_row_id
            if artifact_row_id != registry_row["row_id"]:
                errors.append(f"{app}: historical artifact row does not match registry row")

        rows.append(
            {
                "app": app,
                "registry_row_id": registry_row["row_id"],
                "route_class": registry_row["route_class"],
                "optimization_status": audit["optimization_status"],
                "comparison_readiness": audit["comparison_readiness"],
                "next_action": audit["next_action"],
                "reason": audit["reason"],
                "artifact_status": artifact_status,
                "artifact_row_id": artifact_row_id,
                "historical_artifact_row_id": historical_row_id,
                "uses_embree": bool(registry_row["uses_embree"]),
                "uses_numba": bool(registry_row["uses_numba"]),
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )

    optimized_ready = [row for row in rows if row["comparison_readiness"] == "first_measured_pair_ready"]
    same_contract_needed = [row for row in rows if row["comparison_readiness"] == "needs_same_contract_scale_pair"]
    scale_evidence_ready = [
        row
        for row in rows
        if row["comparison_readiness"]
        in {
            "same_contract_scale_row_ready",
            "same_scale_boundary_limited_row_ready",
            "first_measured_pair_ready",
        }
    ]
    boundary_limited_ready = [
        row for row in rows if row["comparison_readiness"] == "same_scale_boundary_limited_row_ready"
    ]
    contract_choice_needed = [
        row
        for row in rows
        if row["comparison_readiness"]
        in {
            "needs_contract_split_before_optimization",
            "needs_summary_or_signature_contract_choice",
            "needs_contract_choice_before_optimization",
            "needs_3d_ranked_or_2d_ann_contract_choice",
        }
    ]
    if historical.get("all_pass") is not True:
        errors.append("historical Embree packet is not all-pass")
    if rtnn_followup.get("all_pass") is not True:
        errors.append("RTNN Embree follow-up packet is not all-pass")
    if scale_probe.get("all_status_zero") is not True:
        errors.append("Goal4344 Embree scale probe summary is not all-status-zero")

    return {
        "version": EMBREE_OPTIMIZATION_AUDIT_VERSION,
        "status": EMBREE_OPTIMIZATION_AUDIT_STATUS,
        "claim_boundary": EMBREE_OPTIMIZATION_AUDIT_CLAIM_BOUNDARY,
        "sources": {
            "historical_packet": _relative(historical_path),
            "rtnn_followup": _relative(rtnn_path),
            "librts_optimized_summary": _relative(librts_path),
            "same_contract_scale_probe_summary": _relative(scale_probe_path),
        },
        "registry_version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
        "rows": tuple(rows),
        "summary": {
            "app_count": len(rows),
            "row_count": len(rows),
            "optimized_measured_pair_ready_count": len(optimized_ready),
            "embree_scale_evidence_ready_count": len(scale_evidence_ready),
            "boundary_limited_scale_evidence_ready_count": len(boundary_limited_ready),
            "same_contract_scale_pair_needed_count": len(same_contract_needed),
            "contract_choice_needed_count": len(contract_choice_needed),
            "historical_packet_is_stale_for_current_registry": True,
            "librts_query_median_speedup_vs_old_columnar_fallback": float(
                librts_summary["query_median_speedup_vs_columnar_fallback"]
            ),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "intel_gpu_performance_claim_authorized": False,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
    }


def validate_embree_optimization_audit() -> dict[str, Any]:
    return embree_optimization_audit()["validation"]
