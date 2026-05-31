from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .partner_continuation_protocol import validate_v2_5_partner_continuation_contract
from .partner_continuation_protocol import validate_v2_5_partner_preview_gate
from .v2_5_determinism_policy import validate_v2_5_continuation_determinism_policies
from .v2_5_execution_path_policy import validate_v2_5_execution_path_policy
from .v2_5_partner_selection_guidance import validate_v2_5_partner_selection_guidance
from .v2_5_partner_support_matrix import validate_v2_5_partner_support_matrix
from .v2_5_triton_app_migration import validate_v2_5_tiered_benchmark_manifest
from .v2_5_triton_app_migration import v2_5_tiered_benchmark_manifest


V2_5_INTERNAL_READINESS_PACKET_VERSION = "rtdl.v2_5.internal_readiness_packet.v1"
V2_5_INTERNAL_READINESS_STATUS = "internal_evidence_packet_coherent_not_release_ready"
V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY = (
    "v2.5 internal readiness means the current source-tree evidence packet is "
    "coherent for engineering review. It does not authorize release, public "
    "speedup wording, broad RT-core wording, whole-app speedup wording, true "
    "zero-copy wording, package-install wording, Triton preview auto-selection, "
    "or app-specific native engine logic."
)

V2_5_INTERNAL_READINESS_REQUIRED_REPORTS = (
    "docs/reports/goal2773_v2_5_status_next_goals_review_packet_2026-05-31.md",
    "docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md",
    "docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_2026-05-31.md",
    "docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md",
    "docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md",
    "docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md",
    "docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md",
    "docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md",
    "docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md",
    "docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md",
    "docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md",
    "docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md",
    "docs/reports/goal2785_presegmented_vector_sum_triton_offsets_2026-05-31.md",
    "docs/reports/goal2786_batched_vector_sum_offsets_tuning_2026-05-31.md",
    "docs/reports/goal2787_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md",
    "docs/reports/goal2788_dense_point_nearest_hausdorff_strategy_2026-05-31.md",
    "docs/reports/goal2789_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md",
    "docs/reports/goal2790_tiled_dense_point_nearest_hausdorff_strategy_2026-05-31.md",
    "docs/reports/goal2792_partner_selection_explain_plan_2026-05-31.md",
    "docs/reports/goal2793_v2_5_partner_role_reconciliation_2026-05-31.md",
    "docs/reports/goal2794_v2_5_continuation_determinism_policy_2026-05-31.md",
    "docs/reports/goal2795_v2_5_tier_label_reconciliation_2026-05-31.md",
    "docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md",
    "docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md",
    "docs/reports/goal2798_librts_v2_5_warm_median_harness_2026-05-31.md",
    "docs/reports/goal2799_spatial_rayjoin_v2_5_prepared_count_harness_2026-05-31.md",
    "docs/reports/goal2800_rtnn_v2_5_live_ranked_summary_harness_2026-05-31.md",
    "docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md",
    "docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_2026-05-31.md",
    "docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md",
    "docs/reports/goal2804_v2_5_clean_artifact_metadata_refresh_2026-05-31.md",
    "docs/reports/goal2805_v2_5_broad_clean_pod_regression_gate_2026-05-31.md",
    "docs/reports/goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
    "docs/reports/goal2836_goal2835_primitive_payload_entrypoint_metadata_consensus_2026-05-31.md",
    "docs/reports/goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
    "docs/reports/goal2838_goal2837_fixed_radius_graph_entrypoint_metadata_consensus_2026-05-31.md",
    "docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
    "docs/reports/goal2840_goal2839_rtnn_same_stream_runner_mode_consensus_2026-05-31.md",
    "docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
    "docs/reports/goal2842_goal2841_rtnn_same_stream_scale_probe_consensus_2026-05-31.md",
    "docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md",
    "docs/reports/goal2844_goal2843_execution_path_policy_consensus_2026-05-31.md",
    "docs/reports/goal2847_current_head_canonical_harness_refresh_2026-05-31.md",
    "docs/reports/goal2848_goal2847_current_head_canonical_harness_consensus_2026-05-31.md",
    "docs/reports/goal2851_barnes_hut_harness_progress_logging_2026-05-31.md",
    "docs/reports/goal2852_goal2851_barnes_hut_progress_logging_consensus_2026-05-31.md",
)

V2_5_INTERNAL_READINESS_TIER_B_CLEAN_ARTIFACTS = {
    "rtnn": (
        "docs/reports/goal2800_pod_artifacts/"
        "rtnn_v25_live_ranked_summary_65536_clean_from_git.json"
    ),
    "hausdorff_xhd": (
        "docs/reports/goal2801_pod_artifacts/"
        "hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json"
    ),
    "rt_dbscan": (
        "docs/reports/goal2802_pod_artifacts/"
        "rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json"
    ),
    "barnes_hut": (
        "docs/reports/goal2803_pod_artifacts/"
        "barnes_hut_v25_consolidated_harness_clean_from_git.json"
    ),
}

V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY = (
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2847_summary.json"
)
V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_ARTIFACTS = (
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2797_triangle_counting.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2798_librts.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2799_spatial_rayjoin.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2800_rtnn.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2801_hausdorff_xhd.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2802_rt_dbscan.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2803_barnes_hut.json",
)

V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS = (
    "docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md",
    "docs/reviews/goal2800_claude_review_rtnn_live_ranked_summary_harness_2026-05-31.md",
    "docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md",
    "docs/reviews/goal2802_claude_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md",
    "docs/reviews/goal2802_gemini_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md",
    "docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md",
    "docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md",
    "docs/reviews/goal2804_gemini_review_v2_5_clean_artifact_metadata_refresh_2026-05-31.md",
    "docs/reviews/goal2806_claude_review_v2_5_internal_readiness_packet_2026-05-31.md",
    "docs/reviews/goal2806_gemini_review_v2_5_internal_readiness_packet_2026-05-31.md",
    "docs/reviews/goal2836_gemini_review_goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
    "docs/reviews/goal2838_gemini_review_goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
    "docs/reviews/goal2840_gemini_review_goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
    "docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
    "docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md",
    "docs/reviews/goal2848_gemini_review_goal2847_current_head_canonical_harness_2026-05-31.md",
    "docs/reviews/goal2852_gemini_review_goal2851_barnes_hut_progress_logging_2026-05-31.md",
)

V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS = (
    "v2_5_release",
    "release_tag_action",
    "public_speedup_wording",
    "broad_rt_core_speedup_wording",
    "whole_app_speedup_wording",
    "true_zero_copy_wording",
    "package_install_wording",
    "triton_preview_auto_selection",
    "native_app_specific_engine_logic",
)

V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS = (
    "keep_current_canonical_harness_and_observability_guards_green",
    "continue_internal_v2_5_hardening_or_prepare_user_requested_release_packet",
    "request_fresh_3ai_release_review_only_if_user_requests_release",
)


def v2_5_internal_readiness_packet(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the current v2.5 internal evidence index.

    This is a source-tree engineering gate. Passing it means the current
    v2.5 evidence packet is indexed, internally coherent, and bounded. It is
    intentionally not a release authorization.
    """

    root = Path.cwd() if repo_root is None else Path(repo_root)
    manifest = v2_5_tiered_benchmark_manifest()
    tier_b_artifacts = _tier_b_artifact_metadata(root)
    current_canonical_harness = _current_canonical_harness_metadata(root)
    required_report_presence = _path_presence(root, V2_5_INTERNAL_READINESS_REQUIRED_REPORTS)
    review_presence = _path_presence(root, V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS)

    return {
        "packet_version": V2_5_INTERNAL_READINESS_PACKET_VERSION,
        "status": V2_5_INTERNAL_READINESS_STATUS,
        "milestone": "v2.5",
        "scope": "internal_source_tree_engineering_readiness_index",
        "manifest": manifest,
        "manifest_validation": validate_v2_5_tiered_benchmark_manifest(),
        "core_validations": {
            "partner_continuation_contract": validate_v2_5_partner_continuation_contract(),
            "partner_preview_gate": validate_v2_5_partner_preview_gate(),
            "partner_support_matrix": validate_v2_5_partner_support_matrix(),
            "partner_selection_guidance": validate_v2_5_partner_selection_guidance(
                repo_root=root
            ),
            "execution_path_policy": validate_v2_5_execution_path_policy(),
            "determinism_policy": validate_v2_5_continuation_determinism_policies(),
        },
        "benchmark_app_count": manifest["benchmark_app_count"],
        "tier_counts": manifest["tier_counts"],
        "tier_b_clean_artifacts": tier_b_artifacts,
        "tier_b_clean_artifact_count": len(tier_b_artifacts),
        "current_canonical_harness": current_canonical_harness,
        "required_reports": V2_5_INTERNAL_READINESS_REQUIRED_REPORTS,
        "required_report_presence": required_report_presence,
        "missing_required_reports": tuple(
            path for path, present in required_report_presence.items() if not present
        ),
        "external_review_paths": V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS,
        "external_review_presence": review_presence,
        "missing_external_reviews": tuple(
            path for path, present in review_presence.items() if not present
        ),
        "broad_clean_pod_gate": {
            "goal": "Goal2805",
            "commit": "6faf7de8",
            "test_modules": 50,
            "test_count": 239,
            "result": "OK",
            "report": (
                "docs/reports/"
                "goal2805_v2_5_broad_clean_pod_regression_gate_2026-05-31.md"
            ),
        },
        "claim_authorization": {
            "v2_5_release_authorized": False,
            "release_tag_action_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "package_install_claim_authorized": False,
            "triton_preview_auto_selection_authorized": False,
            "native_app_specific_engine_logic_authorized": False,
        },
        "blocked_actions": V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS,
        "allowed_next_actions": V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS,
        "claim_boundary": V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY,
    }


def validate_v2_5_internal_readiness_packet(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    packet = v2_5_internal_readiness_packet(repo_root=repo_root)
    errors: list[str] = []
    if packet["packet_version"] != V2_5_INTERNAL_READINESS_PACKET_VERSION:
        errors.append("unexpected v2.5 internal readiness packet version")
    if packet["status"] != V2_5_INTERNAL_READINESS_STATUS:
        errors.append("unexpected v2.5 internal readiness status")
    if packet["manifest_validation"]["status"] != "accept":
        errors.append("v2.5 tiered benchmark manifest does not validate")
    if packet["benchmark_app_count"] != 10:
        errors.append("v2.5 internal packet must cover exactly 10 benchmark apps")
    if packet["tier_counts"] != {"A": 3, "B": 4, "C": 3}:
        errors.append("v2.5 internal packet tier counts changed")
    for name, validation in packet["core_validations"].items():
        if validation["status"] != "accept":
            errors.append(f"core validation failed: {name}")
    if tuple(packet["missing_required_reports"]) != ():
        errors.append("required v2.5 reports are missing")
    if tuple(packet["missing_external_reviews"]) != ():
        errors.append("required v2.5 external review paths are missing")
    if packet["tier_b_clean_artifact_count"] != 4:
        errors.append("expected four Tier B clean artifacts")
    current_harness = packet["current_canonical_harness"]
    if current_harness.get("summary_status") != "pass":
        errors.append("current canonical harness summary did not pass")
    if current_harness.get("artifact_count") != 7:
        errors.append("expected seven current canonical harness artifacts")
    if not _looks_like_sha(str(current_harness.get("source_commit", ""))):
        errors.append("current canonical harness lacks source commit")
    for name, artifact in current_harness.get("artifacts", {}).items():
        if artifact.get("status") != "pass":
            errors.append(f"{name} current canonical artifact did not pass")
        if artifact.get("source_dirty") != []:
            errors.append(f"{name} current canonical artifact is not source clean")
        if artifact.get("source_commit") != current_harness.get("source_commit"):
            errors.append(f"{name} source commit differs from current canonical summary")
        if "NVIDIA" not in str(artifact.get("gpu", "")):
            errors.append(f"{name} current canonical artifact lacks NVIDIA pod identity")
    for app_id, artifact in packet["tier_b_clean_artifacts"].items():
        if artifact.get("status") != "pass":
            errors.append(f"{app_id} clean artifact did not pass")
        if not _looks_like_sha(str(artifact.get("source_commit", ""))):
            errors.append(f"{app_id} clean artifact lacks source commit")
        if artifact.get("source_dirty") != []:
            errors.append(f"{app_id} clean artifact is not source clean")
        if "NVIDIA" not in str(artifact.get("gpu", "")):
            errors.append(f"{app_id} clean artifact lacks NVIDIA pod identity")
        boundary = artifact.get("claim_boundary", {})
        if isinstance(boundary, dict):
            for flag in (
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "native_engine_customization",
            ):
                if boundary.get(flag) is not False:
                    errors.append(f"{app_id} clean artifact boundary changed: {flag}")
    for flag, value in packet["claim_authorization"].items():
        if value is not False:
            errors.append(f"v2.5 internal packet must not authorize {flag}")
    boundary = str(packet["claim_boundary"])
    for phrase in (
        "internal readiness",
        "does not authorize release",
        "public speedup wording",
        "broad RT-core wording",
        "whole-app speedup wording",
        "true zero-copy wording",
        "package-install wording",
        "Triton preview auto-selection",
        "app-specific native engine logic",
    ):
        if phrase not in boundary:
            errors.append("v2.5 internal readiness claim boundary is incomplete")
    return {
        "status": "accept" if not errors else "reject",
        "packet_version": packet["packet_version"],
        "benchmark_app_count": packet["benchmark_app_count"],
        "tier_counts": packet["tier_counts"],
        "tier_b_clean_artifact_count": packet["tier_b_clean_artifact_count"],
        "current_canonical_harness_artifact_count": packet["current_canonical_harness"]["artifact_count"],
        "broad_clean_pod_gate_result": packet["broad_clean_pod_gate"]["result"],
        "blocked_actions": packet["blocked_actions"],
        "errors": tuple(errors),
    }


def _path_presence(root: Path, paths: tuple[str, ...]) -> dict[str, bool]:
    return {path: (root / path).exists() for path in paths}


def _tier_b_artifact_metadata(root: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    for app_id, relative_path in V2_5_INTERNAL_READINESS_TIER_B_CLEAN_ARTIFACTS.items():
        path = root / relative_path
        if not path.exists():
            artifacts[app_id] = {"path": relative_path, "status": "missing"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifacts[app_id] = {
            "path": relative_path,
            "status": payload.get("status"),
            "source_commit": payload.get("source_commit"),
            "source_dirty": payload.get("source_dirty"),
            "gpu": payload.get("gpu"),
            "claim_boundary": payload.get("claim_boundary", {}),
        }
    return artifacts


def _current_canonical_harness_metadata(root: Path) -> dict[str, Any]:
    summary_path = root / V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY
    if not summary_path.exists():
        return {
            "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY,
            "summary_status": "missing",
            "source_commit": None,
            "artifact_count": 0,
            "artifacts": {},
        }
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    artifacts: dict[str, dict[str, Any]] = {}
    for relative_path in V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_ARTIFACTS:
        path = root / relative_path
        name = path.name
        if not path.exists():
            artifacts[name] = {"path": relative_path, "status": "missing"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifacts[name] = {
            "path": relative_path,
            "goal": payload.get("goal"),
            "status": payload.get("status"),
            "source_commit": payload.get("source_commit"),
            "source_dirty": payload.get("source_dirty"),
            "gpu": payload.get("gpu"),
        }
    return {
        "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY,
        "summary_status": "pass" if summary.get("all_pass") is True else "reject",
        "goal": summary.get("goal"),
        "source_commit": summary.get("source_commit"),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "claim_boundary": (
            "The current canonical harness packet is engineering health evidence. "
            "It does not authorize v2.5 release or broad public speedup claims."
        ),
    }


def _looks_like_sha(value: str) -> bool:
    return len(value) == 40 and all(char in "0123456789abcdef" for char in value)
