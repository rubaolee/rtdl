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
        "n0_foundation_goal": "Goal2990",
        "n0_foundation_report": "docs/reports/goal2990_v2_6_neutral_partner_handoff_2026-06-01.md",
        "n0_foundation_status": "neutral_descriptor_and_lease_packet_landed_pod_runtime_demonstrator_pending",
        "pod_runner_goal": "Goal2991",
        "pod_runner_report": "docs/reports/goal2991_v2_6_numba_neutral_handoff_pod_runner_2026-06-01.md",
        "pod_runner_status": "executed_on_l4_pod_via_goal2993",
        "pod_evidence_goal": "Goal2993",
        "pod_evidence_report": "docs/reports/goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.md",
        "pod_evidence_artifact": "docs/reports/goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.json",
        "pod_evidence_status": "l4_pod_runtime_conformance_passed_not_release_or_speedup_evidence",
        "local_smoke_goal": "Goal2992",
        "local_smoke_report": "docs/reports/goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.md",
        "local_smoke_artifact": "docs/reports/goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.json",
        "local_smoke_status": "passed_on_gtx1070_not_release_or_performance_evidence",
        "benchmark_demonstrator_goal": "Goal2994",
        "benchmark_demonstrator_report": "docs/reports/goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.md",
        "benchmark_demonstrator_artifact": "docs/reports/goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.json",
        "benchmark_demonstrator_status": "raydb_style_avg_sum_count_l4_pod_conformance_passed_not_speedup_evidence",
        "benchmark_minmax_goal": "Goal2995",
        "benchmark_minmax_report": "docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md",
        "benchmark_minmax_artifact": "docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json",
        "benchmark_minmax_status": "raydb_style_all_five_scalar_modes_l4_pod_conformance_passed_not_speedup_evidence",
        "compact_mask_goal": "Goal2997",
        "compact_mask_report": "docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md",
        "compact_mask_artifact": "docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.json",
        "compact_mask_status": "compact_mask_i64_l4_pod_conformance_passed_stable_order_host_prefix_sum_not_speedup_evidence",
        "triangle_compact_mask_goal": "Goal2999",
        "triangle_compact_mask_report": "docs/reports/goal2999_triangle_counting_numba_compact_mask_wiring_2026-06-01.md",
        "triangle_compact_mask_status": "triangle_counting_witness_row_compact_mask_wiring_prepared_l4_runtime_passed_via_goal3000_not_speedup_evidence",
        "triangle_compact_mask_pod_goal": "Goal3000",
        "triangle_compact_mask_pod_report": "docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.md",
        "triangle_compact_mask_pod_artifact": "docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.json",
        "triangle_compact_mask_pod_status": "l4_pod_conformance_passed_clean_source_not_speedup_evidence",
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
                "foundation_status": "Goal2990 neutral descriptor/lease packet landed",
                "exit_gate": (
                    "CuPy and Numba CUDA arrays pass through a neutral descriptor "
                    "without torch conversion on the data path; copy/borrow status "
                    "is runtime-observed and labeled; large L4 pod continuation "
                    "conformance passed for Numba segmented count/sum in Goal2993."
                ),
            },
            {
                "step": "N-1",
                "title": "numba_op_coverage_for_one_demonstrator",
                "exit_gate": "Goal2995 covers count/sum/min/max and avg-as-sum-count for the RayDB-style demonstrator with CPU reference parity",
            },
            {
                "step": "N-2",
                "title": "benchmark_app_numba_user_selected_path",
                "exit_gate": "Goal2994 and Goal2995 route RayDB-style continuations through user-selected Numba; Goal2999 wires triangle witness compaction and Goal3000 proves it on L4 without changing the fused scalar fast path",
            },
            {
                "step": "N-3",
                "title": "conformance_matrix_and_readiness_refresh",
                "exit_gate": "Numba demonstrated ops carry runtime conformance, including Goal2997 compact_mask_i64, while release_conformance_complete remains false",
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
    if roadmap.get("n0_foundation_goal") != "Goal2990":
        errors.append("v2.6 roadmap must index Goal2990 as the N-0 foundation")
    if "pod_runtime_demonstrator_pending" not in str(roadmap.get("n0_foundation_status", "")):
        errors.append("v2.6 roadmap must keep the pod runtime demonstrator pending")
    if not (root / str(roadmap.get("n0_foundation_report", ""))).exists():
        errors.append("Goal2990 N-0 foundation report is missing")
    if roadmap.get("pod_runner_goal") != "Goal2991":
        errors.append("v2.6 roadmap must index Goal2991 as the Numba neutral-handoff pod runner")
    if roadmap.get("pod_runner_status") != "executed_on_l4_pod_via_goal2993":
        errors.append("Goal2991 runner must point to Goal2993 L4 pod evidence")
    if not (root / str(roadmap.get("pod_runner_report", ""))).exists():
        errors.append("Goal2991 pod-runner report is missing")
    if roadmap.get("pod_evidence_goal") != "Goal2993":
        errors.append("v2.6 roadmap must index Goal2993 as the L4 pod evidence")
    if "not_release_or_speedup_evidence" not in str(roadmap.get("pod_evidence_status", "")):
        errors.append("Goal2993 pod evidence must not be treated as release or speedup evidence")
    if not (root / str(roadmap.get("pod_evidence_report", ""))).exists():
        errors.append("Goal2993 L4 pod evidence report is missing")
    if not (root / str(roadmap.get("pod_evidence_artifact", ""))).exists():
        errors.append("Goal2993 L4 pod evidence artifact is missing")
    if roadmap.get("local_smoke_goal") != "Goal2992":
        errors.append("v2.6 roadmap must index Goal2992 as the local Linux smoke checkpoint")
    if "not_release_or_performance_evidence" not in str(roadmap.get("local_smoke_status", "")):
        errors.append("Goal2992 local smoke must not be treated as release or performance evidence")
    if not (root / str(roadmap.get("local_smoke_report", ""))).exists():
        errors.append("Goal2992 local smoke report is missing")
    if not (root / str(roadmap.get("local_smoke_artifact", ""))).exists():
        errors.append("Goal2992 local smoke artifact is missing")
    if roadmap.get("benchmark_demonstrator_goal") != "Goal2994":
        errors.append("v2.6 roadmap must index Goal2994 as the first benchmark-app demonstrator")
    if "not_speedup_evidence" not in str(roadmap.get("benchmark_demonstrator_status", "")):
        errors.append("Goal2994 benchmark demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("benchmark_demonstrator_report", ""))).exists():
        errors.append("Goal2994 benchmark demonstrator report is missing")
    if not (root / str(roadmap.get("benchmark_demonstrator_artifact", ""))).exists():
        errors.append("Goal2994 benchmark demonstrator artifact is missing")
    if roadmap.get("benchmark_minmax_goal") != "Goal2995":
        errors.append("v2.6 roadmap must index Goal2995 as the RayDB min/max Numba demonstrator")
    if "all_five_scalar_modes" not in str(roadmap.get("benchmark_minmax_status", "")):
        errors.append("Goal2995 benchmark min/max status must cover all five scalar modes")
    if "not_speedup_evidence" not in str(roadmap.get("benchmark_minmax_status", "")):
        errors.append("Goal2995 benchmark min/max demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("benchmark_minmax_report", ""))).exists():
        errors.append("Goal2995 benchmark min/max report is missing")
    if not (root / str(roadmap.get("benchmark_minmax_artifact", ""))).exists():
        errors.append("Goal2995 benchmark min/max artifact is missing")
    if roadmap.get("compact_mask_goal") != "Goal2997":
        errors.append("v2.6 roadmap must index Goal2997 as the Numba compact-mask demonstrator")
    if "compact_mask_i64" not in str(roadmap.get("compact_mask_status", "")):
        errors.append("Goal2997 compact-mask status must name compact_mask_i64")
    if "not_speedup_evidence" not in str(roadmap.get("compact_mask_status", "")):
        errors.append("Goal2997 compact-mask demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("compact_mask_report", ""))).exists():
        errors.append("Goal2997 compact-mask report is missing")
    if not (root / str(roadmap.get("compact_mask_artifact", ""))).exists():
        errors.append("Goal2997 compact-mask artifact is missing")
    if roadmap.get("triangle_compact_mask_goal") != "Goal2999":
        errors.append("v2.6 roadmap must index Goal2999 as triangle-counting compact-mask app wiring")
    if "triangle_counting" not in str(roadmap.get("triangle_compact_mask_status", "")):
        errors.append("Goal2999 triangle compact-mask status must name triangle_counting")
    if "not_speedup_evidence" not in str(roadmap.get("triangle_compact_mask_status", "")):
        errors.append("Goal2999 triangle compact-mask wiring must not be treated as speedup evidence")
    if not (root / str(roadmap.get("triangle_compact_mask_report", ""))).exists():
        errors.append("Goal2999 triangle compact-mask wiring report is missing")
    if roadmap.get("triangle_compact_mask_pod_goal") != "Goal3000":
        errors.append("v2.6 roadmap must index Goal3000 as triangle-counting compact-mask pod evidence")
    if "l4_pod_conformance_passed" not in str(roadmap.get("triangle_compact_mask_pod_status", "")):
        errors.append("Goal3000 triangle compact-mask pod status must record L4 conformance")
    if "not_speedup_evidence" not in str(roadmap.get("triangle_compact_mask_pod_status", "")):
        errors.append("Goal3000 triangle compact-mask pod evidence must not be treated as speedup evidence")
    if not (root / str(roadmap.get("triangle_compact_mask_pod_report", ""))).exists():
        errors.append("Goal3000 triangle compact-mask pod report is missing")
    if not (root / str(roadmap.get("triangle_compact_mask_pod_artifact", ""))).exists():
        errors.append("Goal3000 triangle compact-mask pod artifact is missing")
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
