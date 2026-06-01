from __future__ import annotations

from pathlib import Path
from typing import Any


V2_6_ROADMAP_VERSION = "rtdl.v2_6.roadmap.v1"
V2_6_ROADMAP_STATUS = "v2_6_started_planning_not_release_authorization"
V2_6_CLAUDE_REFERENCE_REPORT = (
    "docs/reports/claude_v2_6_numba_first_class_partner_work_for_main_ai_2026-05-31.md"
)
V2_6_ROADMAP_CLAIM_BOUNDARY = (
    "v2.6 begins from the v2.5 closeout as an internal development lane. It "
    "does not authorize v2.6 release, public speedup wording, whole-app "
    "speedup wording, broad RT-core wording, true-zero-copy wording, automatic "
    "partner selection, automatic Triton selection, Numba speedup wording, or "
    "app-specific native-engine behavior."
)


def v2_6_roadmap() -> dict[str, Any]:
    """Return the initial v2.6 roadmap after the v2.5 closeout cleanup."""

    return {
        "roadmap_version": V2_6_ROADMAP_VERSION,
        "status": V2_6_ROADMAP_STATUS,
        "source_reference": V2_6_CLAUDE_REFERENCE_REPORT,
        "opening_goal": "neutral_buffer_seam_runtime_cleanup_before_first_class_numba",
        "primary_partner_track": "numba_first_class_user_selectable_partner",
        "partner_choice_rule": "users_choose_supported_partners_explicitly",
        "supported_partner_duty": "provide_high_performance_support_for_supported_partners_without_forcing_a_partner",
        "benchmark_app_role": "reference_or_recommended_implementations_with_project_chosen_partner_paths",
        "generic_engine_boundary": "native_engine_exposes_generic_app_agnostic_primitives_only",
        "triton_status": "paused_ignored_for_recommended_paths_until_new_same_contract_evidence",
        "numba_support_boundary": "support_means_user_selectable_correct_app_path_not_speedup_claim",
        "minimum_demonstration": {
            "one_benchmark_app_enough_for_initial_first_class_claim": True,
            "real_partner_continuation_required": True,
            "cpu_reference_parity_required": True,
            "partner_free_reference_path_required": True,
            "same_contract_perf_gate_required_before_speedup_claim": True,
        },
        "sequenced_work": (
            {
                "step": "N-0",
                "title": "neutral_buffer_seam_cleanup",
                "exit_gate": (
                    "CuPy and Numba CUDA arrays pass through a neutral descriptor "
                    "without torch conversion on the data path; copy/borrow status "
                    "is runtime-observed and labeled."
                ),
            },
            {
                "step": "N-1",
                "title": "numba_op_coverage_for_one_demonstrator",
                "exit_gate": "only the ops used by the chosen benchmark app gain Numba coverage, each with reference parity",
            },
            {
                "step": "N-2",
                "title": "benchmark_app_numba_user_selected_path",
                "exit_gate": "one benchmark app routes a real continuation through user-selected Numba and matches CPU reference",
            },
            {
                "step": "N-3",
                "title": "conformance_matrix_and_readiness_refresh",
                "exit_gate": "Numba demonstrated ops carry runtime conformance while release_conformance_complete remains false",
            },
            {
                "step": "N-4",
                "title": "honest_v2_6_closeout_line",
                "exit_gate": "documents support as correctness/choosability, not performance",
            },
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_allowed": False,
        "automatic_triton_selection_allowed": False,
        "numba_speedup_claim_authorized": False,
        "app_specific_native_engine_logic_authorized": False,
        "claim_boundary": V2_6_ROADMAP_CLAIM_BOUNDARY,
    }


def validate_v2_6_roadmap(
    roadmap: dict[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    roadmap = v2_6_roadmap() if roadmap is None else roadmap
    root = Path.cwd() if repo_root is None else Path(repo_root)
    errors: list[str] = []
    if roadmap.get("roadmap_version") != V2_6_ROADMAP_VERSION:
        errors.append("unexpected v2.6 roadmap version")
    if roadmap.get("status") != V2_6_ROADMAP_STATUS:
        errors.append("unexpected v2.6 roadmap status")
    if "neutral_buffer_seam" not in str(roadmap.get("opening_goal", "")):
        errors.append("v2.6 must begin with the neutral buffer seam cleanup")
    if "numba" not in str(roadmap.get("primary_partner_track", "")):
        errors.append("v2.6 must name Numba as the first-class partner track")
    if "users_choose" not in str(roadmap.get("partner_choice_rule", "")):
        errors.append("v2.6 must keep partner choice user-owned")
    if "high_performance_support" not in str(roadmap.get("supported_partner_duty", "")):
        errors.append("v2.6 must state RTDL's duty for supported partners")
    if "reference_or_recommended" not in str(roadmap.get("benchmark_app_role", "")):
        errors.append("v2.6 must keep benchmark apps as reference/recommended implementations")
    if "app_agnostic" not in str(roadmap.get("generic_engine_boundary", "")):
        errors.append("v2.6 must preserve the app-agnostic native-engine boundary")
    if "ignored" not in str(roadmap.get("triton_status", "")):
        errors.append("Triton must remain ignored for recommended v2.6 kickoff paths")
    demonstration = roadmap.get("minimum_demonstration", {})
    for field in (
        "one_benchmark_app_enough_for_initial_first_class_claim",
        "real_partner_continuation_required",
        "cpu_reference_parity_required",
        "partner_free_reference_path_required",
        "same_contract_perf_gate_required_before_speedup_claim",
    ):
        if demonstration.get(field) is not True:
            errors.append(f"{field} must remain true")
    steps = tuple(row.get("step") for row in roadmap.get("sequenced_work", ()))
    if steps != ("N-0", "N-1", "N-2", "N-3", "N-4"):
        errors.append("v2.6 roadmap step order must remain N-0 through N-4")
    if not (root / V2_6_CLAUDE_REFERENCE_REPORT).exists():
        errors.append("Claude v2.6 reference report is missing")
    for field in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "automatic_partner_selection_allowed",
        "automatic_triton_selection_allowed",
        "numba_speedup_claim_authorized",
        "app_specific_native_engine_logic_authorized",
    ):
        if roadmap.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "roadmap_version": roadmap.get("roadmap_version"),
        "errors": tuple(errors),
    }
