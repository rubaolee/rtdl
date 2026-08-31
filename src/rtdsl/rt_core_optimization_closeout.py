from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .current_benchmark_scale_profiles import (
    CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
    current_benchmark_scale_profiles,
)
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


RT_CORE_OPTIMIZATION_CLOSEOUT_VERSION = "rtdl.v2_11.rt_core_optimization_closeout.goal4342.v1"
RT_CORE_OPTIMIZATION_CLOSEOUT_STATUS = "internal_rt_core_optimization_closeout_not_comparison_or_release_authorization"
RT_CORE_OPTIMIZATION_CLOSEOUT_CLAIM_BOUNDARY = (
    "Goal4342 closes the current NVIDIA RT-core optimization audit with boundaries. "
    "It does not authorize release action, public speedup wording, whole-app "
    "acceleration wording, broad RT-core wording, paper reproduction wording, "
    "true-zero-copy wording, automatic partner selection, or app-specific "
    "native-engine logic. It is also not the final OptiX-vs-Embree comparison."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCALE_SUMMARY = ROOT / "docs" / "reports" / "goal4329_current_pod_validation" / "scale_summary_allpass.json"


ROUTE_AUDIT: dict[str, dict[str, str]] = {
    "hausdorff_xhd": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_internal_evidence",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "Prepared OptiX threshold route is current and pass-validated; prepared-session "
            "reuse is already documented, but the row is smoke/internal rather than "
            "decision-grade timing."
        ),
    },
    "spatial_rayjoin": {
        "route_class": "rtdl_optix_plus_numba_configured_route",
        "optimization_status": "closed_configured_route",
        "remaining_high_leverage_rt_core_work": "none_obvious_for_current_mixed_route",
        "comparison_table": "configured_route_only",
        "reason": (
            "The current row intentionally mixes Numba one-shot PIP with RTDL/OptiX PIP, "
            "LSI, and overlay phases. Do not report it as a pure RT-core backend row."
        ),
    },
    "rt_dbscan": {
        "route_class": "rtdl_optix_plus_numba_configured_route",
        "optimization_status": "closed_configured_route",
        "remaining_high_leverage_rt_core_work": "none_obvious_for_current_grouped_stream_route",
        "comparison_table": "configured_route_only",
        "reason": (
            "The current high-performance route is OptiX threshold flags plus Numba "
            "component signature, with CPU validation intentionally separated."
        ),
    },
    "robot_collision": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_floor_met",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "Prepared device-count route is resident/high-repeat and the current pod "
            "artifact meets its internal hot-path floor."
        ),
    },
    "contact_manifold": {
        "route_class": "pure_rtdl_optix_collect_k_experimental",
        "optimization_status": "closed_internal_evidence_collect_k_checkpointed",
        "remaining_high_leverage_rt_core_work": "none_before_v2_5_collect_k_checkpoint",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "The current route is OptiX native collect-k. Collect-k optimization was "
            "explicitly checkpointed, so this campaign should not restart that lane."
        ),
    },
    "raydb_style": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_floor_met",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "Primitive-first grouped count route is resident/high-repeat and the "
            "current pod artifact meets its internal hot-path floor."
        ),
    },
    "barnes_hut": {
        "route_class": "numba_partner_only_current_scale_row",
        "optimization_status": "not_a_pure_rt_core_row",
        "remaining_high_leverage_rt_core_work": "no_current_pure_rt_core_route_to_optimize_for_this_row",
        "comparison_table": "configured_route_only_or_requires_new_pure_rtdl_contract",
        "reason": (
            "The current scale row is a Numba exact-force partner route; it belongs in "
            "a configured-route table, not a pure OptiX-vs-Embree RTDL table."
        ),
    },
    "librts_spatial_index": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_internal_evidence",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "Prepared OptiX AABB index is current; Goal4340/4341 already supplied the "
            "first optimized same-contract Embree-vs-OptiX comparison row at 1024x1024."
        ),
    },
    "rtnn": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_internal_evidence",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "Prepared OptiX ranked-summary route is current and pass-validated; the "
            "comparison campaign still needs an equivalent Embree contract choice."
        ),
    },
    "triangle_counting": {
        "route_class": "pure_rtdl_optix_rt_core",
        "optimization_status": "closed_internal_evidence",
        "remaining_high_leverage_rt_core_work": "none_obvious",
        "comparison_table": "pure_rtdl_candidate_after_same_contract_embree_pair",
        "reason": (
            "RT-Graph 2A1 prepared generic ray-triangle summary is current and "
            "pass-validated; same-contract Embree scale pairing remains future work."
        ),
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _artifact_rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {}
    return {str(row.get("app")): row for row in rows if isinstance(row, dict) and row.get("app")}


def rt_core_optimization_closeout(*, scale_summary_path: Path | None = None) -> dict[str, Any]:
    artifact_path = scale_summary_path or DEFAULT_SCALE_SUMMARY
    artifact = _load_json(artifact_path)
    artifact_by_app = _artifact_rows(artifact)
    registry = {row["app"]: row for row in current_benchmark_scale_profiles()}

    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for app in V2_8_PROMOTED_BENCHMARK_APPS:
        if app not in registry:
            errors.append(f"{app}: missing current OptiX registry row")
            continue
        if app not in ROUTE_AUDIT:
            errors.append(f"{app}: missing Goal4342 route audit row")
            continue
        registry_row = registry[app]
        artifact_row = artifact_by_app.get(app)
        semantic = artifact_row.get("semantic_stdout_check", {}) if isinstance(artifact_row, dict) else {}
        floor = artifact_row.get("hot_path_floor_evaluation", {}) if isinstance(artifact_row, dict) else {}
        audit = ROUTE_AUDIT[app]
        if artifact_row is None:
            errors.append(f"{app}: missing current pod artifact row")
        elif artifact_row.get("status") != "pass":
            errors.append(f"{app}: current pod artifact row did not pass")
        if isinstance(semantic, dict) and semantic.get("claim_flag_violations") not in (None, []):
            errors.append(f"{app}: current pod artifact has claim-flag violations")

        rows.append(
            {
                "app": app,
                "row_id": registry_row["row_id"],
                "command": registry_row["command"],
                "requires_numba": bool(registry_row["requires_numba"]),
                "route_class": audit["route_class"],
                "optimization_status": audit["optimization_status"],
                "remaining_high_leverage_rt_core_work": audit["remaining_high_leverage_rt_core_work"],
                "comparison_table": audit["comparison_table"],
                "reason": audit["reason"],
                "artifact_status": artifact_row.get("status") if isinstance(artifact_row, dict) else "missing",
                "hot_path_floor_status": floor.get("status") if isinstance(floor, dict) else "missing",
                "representative_hot_path_metric": registry_row["representative_hot_path_metric"],
                "hot_path_duration_target_sec": registry_row["hot_path_duration_target_sec"],
                "public_speedup_claim_authorized": False,
                "broad_rt_core_claim_authorized": False,
                "release_authorized": False,
            }
        )

    pure_rows = [row for row in rows if row["route_class"].startswith("pure_rtdl_optix")]
    configured_rows = [row for row in rows if "configured_route" in row["route_class"]]
    partner_only_rows = [row for row in rows if row["route_class"] == "numba_partner_only_current_scale_row"]
    floor_met_rows = [row for row in rows if row["hot_path_floor_status"] == "floor_met_internal_evidence_only"]
    smoke_rows = [row for row in rows if row["hot_path_floor_status"] == "smoke_scale_or_internal_not_claim_grade"]
    remaining_implementation_rows = [
        row
        for row in rows
        if row["remaining_high_leverage_rt_core_work"] not in {
            "none_obvious",
            "none_obvious_for_current_mixed_route",
            "none_obvious_for_current_grouped_stream_route",
            "none_before_v2_5_collect_k_checkpoint",
            "no_current_pure_rt_core_route_to_optimize_for_this_row",
        }
    ]
    if remaining_implementation_rows:
        errors.append("unexpected remaining high-leverage RT-core implementation work found")
    if artifact.get("all_pass") is not True:
        errors.append("current pod scale summary is not all-pass")
    if artifact.get("hot_path_floor_summary", {}).get("status") != "accept":
        errors.append("current pod hot-path floor summary is not accept")

    return {
        "version": RT_CORE_OPTIMIZATION_CLOSEOUT_VERSION,
        "status": RT_CORE_OPTIMIZATION_CLOSEOUT_STATUS,
        "claim_boundary": RT_CORE_OPTIMIZATION_CLOSEOUT_CLAIM_BOUNDARY,
        "source": _relative(artifact_path),
        "scale_profile_version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
        "rows": tuple(rows),
        "summary": {
            "app_count": len(rows),
            "row_count": len(rows),
            "pure_rtdl_optix_row_count": len(pure_rows),
            "configured_route_row_count": len(configured_rows),
            "partner_only_current_scale_row_count": len(partner_only_rows),
            "floor_met_internal_row_count": len(floor_met_rows),
            "smoke_or_internal_row_count": len(smoke_rows),
            "remaining_high_leverage_rt_core_implementation_work_count": len(remaining_implementation_rows),
            "surprise_findings": (
                "No obvious high-leverage OptiX/RT-core implementation optimization remains in the current campaign.",
                "Barnes-Hut's current NVIDIA scale row is a Numba partner route, not a pure RT-core row.",
                "Most rows remain smoke/internal timing evidence rather than decision-grade public speedup evidence.",
            ),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def validate_rt_core_optimization_closeout() -> dict[str, Any]:
    return rt_core_optimization_closeout()["validation"]
