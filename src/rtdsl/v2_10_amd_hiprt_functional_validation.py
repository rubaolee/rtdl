from __future__ import annotations

from typing import Any

from .v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity


V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION = (
    "rtdl.v2_10.amd_hiprt_functional_validation_runbook_after_goal3783.v1"
)
V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_STATUS = "pending_actual_amd_hardware"

AMD_FUNCTIONAL_ARTIFACT = "docs/reports/goal3784_amd_hiprt_functional_pod_validation.json"

CLAIM_BOUNDARY = {
    "release_authorized": False,
    "amd_perf_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "broad_rt_core_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "zero_copy_claim_authorized": False,
    "app_specific_native_engine_logic_allowed": False,
}

REQUIRED_AMD_ARTIFACT_FIELDS = (
    "goal",
    "version",
    "hardware_vendor",
    "gpu",
    "driver",
    "hiprt_sdk",
    "hiprt_library",
    "git_commit",
    "build_command",
    "focused_test_modules",
    "focused_tests_passed",
    "stage_counts",
    "ready_for_amd_functional_pod_apps",
    "functional_results_by_app",
    "parity_validation",
    "scoped_source_dirty",
    "claim_boundary",
)

AMD_FUNCTIONAL_TEST_MODULES = (
    "tests.goal3753_amd_hiprt_benchmark_parity_plan_test",
    "tests.goal3755_robot_collision_hiprt_route_readiness_test",
    "tests.goal3763_hiprt_context_probe_tail_repair_test",
    "tests.goal3764_robot_collision_hiprt_cuda_path_app_smoke_test",
    "tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test",
    "tests.goal3766_hiprt_prepared_segment_pair_count_test",
    "tests.goal3767_hiprt_prepared_shape_pair_active_count_test",
    "tests.goal3768_hiprt_fixed_radius_threshold_count_test",
    "tests.goal3769_hiprt_fixed_radius_threshold_flags_test",
    "tests.goal3770_hiprt_prepared_aabb_index_test",
    "tests.goal3771_hiprt_fixed_radius_ranked_aggregate_test",
    "tests.goal3772_hiprt_fixed_radius_ranked_batch_sweep_test",
    "tests.goal3773_hiprt_point_group_nearest_witness_test",
    "tests.goal3774_hiprt_point_group_nearest_device_columns_test",
    "tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test",
    "tests.goal3776_hiprt_collect_k_bounded_i64_test",
    "tests.goal3777_hiprt_aggregate_frontier_collect_2d_test",
    "tests.goal3779_hiprt_grouped_i64_count_sum_test",
    "tests.goal3780_hiprt_grouped_vector_sum_f64x2_test",
    "tests.goal3781_hiprt_columnar_i64_predicate_scan_test",
    "tests.goal3782_hiprt_graph_cycle_count_test",
    "tests.goal3783_v2_10_hiprt_parity_closeout_packet_test",
    "tests.goal3784_amd_hiprt_functional_validation_runbook_test",
)


def build_v2_10_amd_hiprt_functional_validation_runbook() -> dict[str, Any]:
    parity = summarize_v2_10_amd_hiprt_benchmark_parity()
    return {
        "version": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
        "status": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_STATUS,
        "purpose": (
            "Run the already-implemented HIPRT generic contracts on actual AMD "
            "hardware and record functional parity evidence without authorizing "
            "AMD performance claims."
        ),
        "required_artifact": AMD_FUNCTIONAL_ARTIFACT,
        "required_hardware_vendor": "amd",
        "required_backend": "hiprt",
        "ready_for_amd_functional_pod_apps": parity["ready_for_amd_functional_pod_apps"],
        "stage_counts": parity["stage_counts"],
        "parity_version": parity["version"],
        "focused_test_modules": AMD_FUNCTIONAL_TEST_MODULES,
        "required_artifact_fields": REQUIRED_AMD_ARTIFACT_FIELDS,
        "acceptance": (
            "hardware_vendor must be amd; focused_tests_passed must be true; "
            "all ten ready apps must report pass; scoped_source_dirty must be "
            "false; parity_validation.status must be accept; claim flags must "
            "remain false."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _as_bool(value: Any) -> bool:
    return bool(value)


def validate_v2_10_amd_hiprt_functional_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
    ready_apps = tuple(runbook["ready_for_amd_functional_pod_apps"])

    for field in REQUIRED_AMD_ARTIFACT_FIELDS:
        if field not in artifact:
            errors.append(f"missing required artifact field: {field}")

    vendor = str(artifact.get("hardware_vendor", "")).strip().lower()
    if vendor != "amd":
        errors.append("hardware_vendor must be amd for AMD functional evidence")

    gpu = str(artifact.get("gpu", "")).lower()
    backend_route = str(artifact.get("backend_route", "")).lower()
    if "nvidia" in gpu or "nvidia" in backend_route:
        errors.append("NVIDIA/Orochi evidence must not be counted as AMD functional evidence")
    if "not amd hardware evidence" in backend_route:
        errors.append("artifact explicitly says it is not AMD hardware evidence")

    if artifact.get("version") != V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION:
        errors.append("artifact version must match the AMD functional validation runbook")
    if not _as_bool(artifact.get("focused_tests_passed")):
        errors.append("focused_tests_passed must be true")
    if _as_bool(artifact.get("scoped_source_dirty")):
        errors.append("scoped_source_dirty must be false")

    stage_counts = artifact.get("stage_counts", {})
    if stage_counts.get("ready_for_amd_functional_pod") != 10:
        errors.append("stage_counts.ready_for_amd_functional_pod must be 10")
    if stage_counts.get("needs_generic_hiprt_extension") != 0:
        errors.append("stage_counts.needs_generic_hiprt_extension must be 0")
    if stage_counts.get("compatibility_only_not_amd_perf_ready") != 0:
        errors.append("stage_counts.compatibility_only_not_amd_perf_ready must be 0")

    reported_apps = tuple(artifact.get("ready_for_amd_functional_pod_apps", ()))
    if set(reported_apps) != set(ready_apps):
        errors.append("ready app coverage must match the v2.10 parity map")

    results_by_app = artifact.get("functional_results_by_app", {})
    if isinstance(results_by_app, dict):
        missing = [app for app in ready_apps if results_by_app.get(app) != "pass"]
        if missing:
            errors.append(f"functional_results_by_app must mark every ready app pass: {missing}")
    else:
        errors.append("functional_results_by_app must be a dict")

    parity_validation = artifact.get("parity_validation", {})
    if not isinstance(parity_validation, dict) or parity_validation.get("status") != "accept":
        errors.append("parity_validation.status must be accept")

    boundary = artifact.get("claim_boundary", {})
    if not isinstance(boundary, dict):
        errors.append("claim_boundary must be a dict")
    else:
        for key in CLAIM_BOUNDARY:
            if boundary.get(key):
                errors.append(f"claim boundary flag must remain false: {key}")

    return {
        "version": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "validated_ready_app_count": len(ready_apps),
        "claim_boundary": CLAIM_BOUNDARY,
    }
