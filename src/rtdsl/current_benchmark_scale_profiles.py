from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_BENCHMARK_SCALE_PROFILE_VERSION = "rtdl.v2_10.current_benchmark_scale_profiles.goal3828.v1"
CURRENT_BENCHMARK_SCALE_PROFILE_STATUS = "internal_scale_profile_registry_not_release_authorization"
CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY = (
    "Goal3828 records calibrated scale-profile commands for the ten benchmark apps "
    "after the Goal3827 file-stdout correction. It does not authorize release action, "
    "package-install wording, public speedup wording, whole-app acceleration wording, "
    "broad RT-core wording, paper-reproduction wording, true-zero-copy wording, AMD "
    "performance wording, automatic partner selection, or app-specific native-engine logic."
)


@dataclass(frozen=True)
class CurrentBenchmarkScaleProfile:
    app: str
    row_id: str
    purpose: str
    profile_kind: str
    command: tuple[str, ...]
    timeout_sec: int
    evidence_refs: tuple[str, ...]
    expected_runtime_class: str
    stdout_policy: str = "file_backed_stdout_required"
    requires_optix_library: bool = True
    requires_numba: bool = False
    timing_metric_scope: str = "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric"
    representative_hot_path_metric: str = "payload_timing_summary_or_app_phase_timing"
    hot_path_duration_target_sec: float | None = None
    scale_calibration_status: str = "internal_current_scale_not_claim_grade"
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.profile_kind not in {"default_scale", "stress_scale"}:
            raise ValueError(f"{self.app}: profile_kind must be default_scale or stress_scale")
        if self.stdout_policy != "file_backed_stdout_required":
            raise ValueError(f"{self.app}: scale profiles must use file-backed stdout")
        if not self.row_id or not self.purpose:
            raise ValueError(f"{self.app}: row_id and purpose must be explicit")
        if not self.command or self.command[0] not in {"python", "py"}:
            raise ValueError(f"{self.app}: command must start with python or py")
        if self.timeout_sec <= 0:
            raise ValueError(f"{self.app}: timeout_sec must be positive")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence_refs must not be empty")
        if not self.expected_runtime_class:
            raise ValueError(f"{self.app}: expected_runtime_class must be explicit")
        if self.timing_metric_scope != "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric":
            raise ValueError(f"{self.app}: timing_metric_scope must keep wrapper elapsed out of hot-path claims")
        if not self.representative_hot_path_metric:
            raise ValueError(f"{self.app}: representative_hot_path_metric must be explicit")
        if self.hot_path_duration_target_sec is not None and self.hot_path_duration_target_sec <= 0:
            raise ValueError(f"{self.app}: hot_path_duration_target_sec must be positive when set")
        if not self.scale_calibration_status:
            raise ValueError(f"{self.app}: scale_calibration_status must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
            "status": CURRENT_BENCHMARK_SCALE_PROFILE_STATUS,
            "app": self.app,
            "row_id": self.row_id,
            "purpose": self.purpose,
            "profile_kind": self.profile_kind,
            "command": self.command,
            "timeout_sec": self.timeout_sec,
            "evidence_refs": self.evidence_refs,
            "expected_runtime_class": self.expected_runtime_class,
            "stdout_policy": self.stdout_policy,
            "requires_optix_library": self.requires_optix_library,
            "requires_numba": self.requires_numba,
            "timing_metric_scope": self.timing_metric_scope,
            "representative_hot_path_metric": self.representative_hot_path_metric,
            "hot_path_duration_target_sec": self.hot_path_duration_target_sec,
            "scale_calibration_status": self.scale_calibration_status,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY,
        }


CURRENT_BENCHMARK_SCALE_PROFILES: tuple[CurrentBenchmarkScaleProfile, ...] = (
    CurrentBenchmarkScaleProfile(
        app="hausdorff_xhd",
        row_id="hausdorff_xhd_scale_default_optix_threshold",
        purpose="scale-profile Hausdorff/X-HD OptiX threshold decision run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "optix",
            "--require-rt-core",
            "--optix-summary-mode",
            "directed_threshold_prepared",
            "--hausdorff-threshold",
            "0.25",
            "--copies",
            "1024",
            "--repeat",
            "5",
            "--warmup",
            "1",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3827",),
        expected_runtime_class="safe_but_short",
        representative_hot_path_metric="run_phases.query_fixed_radius_threshold_reached_count_sec",
    ),
    CurrentBenchmarkScaleProfile(
        app="spatial_rayjoin",
        row_id="spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
        purpose=(
            "scale-profile RayJoin-style bounded public-CDB representative mixed route: "
            "Numba one-shot PIP, RTDL/OptiX repeated PIP batch executor, RTDL/OptiX LSI, "
            "and RTDL/OptiX overlay active count"
        ),
        profile_kind="default_scale",
        command=(
            "python",
            "scripts/goal3866_rayjoin_representative_scale_profile.py",
            "--repeat",
            "50",
            "--warmup",
            "5",
            "--pip-batch-single-repeat",
            "12",
            "--pip-batch-repeat",
            "8",
            "--pip-batch-request-counts",
            "1",
            "100",
        ),
        timeout_sec=360,
        evidence_refs=("Goal3834", "Goal3838", "Goal3842", "Goal3866", "Goal3936", "Goal4039"),
        expected_runtime_class="representative_mixed_route_public_cdb",
        requires_numba=True,
        representative_hot_path_metric="representative_hot_path_summary",
    ),
    CurrentBenchmarkScaleProfile(
        app="rt_dbscan",
        row_id="rt_dbscan_optix_numba_scale_default_65536_no_validation",
        purpose=(
            "scale-profile RT-DBSCAN OptiX threshold flags plus Numba component signature "
            "without CPU validation or Python row materialization"
        ),
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
            "--mode",
            "optix_rt_core_grouped_stream_numba_column_signature_3d",
            "--dataset",
            "clustered3d",
            "--point-count",
            "65536",
            "--repeat",
            "3",
            "--warmup",
            "1",
            "--no-validation",
        ),
        timeout_sec=120,
        evidence_refs=("Goal3826", "Goal3827", "Goal3830", "Goal3851", "Goal3859"),
        expected_runtime_class="default_scale_prepared_repeat_no_validation",
        requires_numba=True,
        representative_hot_path_metric="metadata.prepared_query_repeat_protocol.elapsed_sec_median",
    ),
    CurrentBenchmarkScaleProfile(
        app="robot_collision",
        row_id="robot_collision_optix_scale_default_1024_no_probe_reference",
        purpose="scale-profile robot-collision prepared OptiX device-count run with CPU probe validation separated",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py",
            "--mode",
            "optix_prepared_device_count",
            "--dataset",
            "scaled",
            "--pose-count",
            "1024",
            "--obstacle-count",
            "128",
            "--link-count",
            "4",
            "--repeats",
            "50000",
            "--warmup",
            "100",
            "--no-probe-reference",
            "--summary-only-runs",
        ),
        timeout_sec=300,
        evidence_refs=("Goal3826", "Goal3827", "Goal3831", "Goal3983", "Goal3984"),
        expected_runtime_class="resident_high_repeat_hot_path_summary_no_probe_reference",
        representative_hot_path_metric="run_summary.phase_timing_seconds.traversal.total_sec",
        hot_path_duration_target_sec=1.0,
        scale_calibration_status="resident_high_repeat_summary_contract_goal3984",
    ),
    CurrentBenchmarkScaleProfile(
        app="contact_manifold",
        row_id="contact_manifold_optix_scale_default_grid64",
        purpose="scale-profile contact-manifold bounded collect-k run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
            "--mode",
            "native_collect_k",
            "--backend",
            "optix",
            "--dataset",
            "grid",
            "--grid-count",
            "64",
            "--witness-capacity",
            "128",
            "--repeat-count",
            "3",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3827",),
        expected_runtime_class="safe_but_short",
        representative_hot_path_metric="native_collect_elapsed_sec",
    ),
    CurrentBenchmarkScaleProfile(
        app="raydb_style",
        row_id="raydb_style_optix_count_scale_default_262k",
        purpose="scale-profile RayDB-style primitive-first grouped count run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "--mode",
            "count",
            "--backend",
            "paper_rt_optix_v2_5_primitive_first",
            "--fixture-kind",
            "generated",
            "--generated-rows",
            "262144",
            "--generated-groups",
            "1024",
            "--repeat",
            "5000",
            "--warmup",
            "50",
            "--summary-only-iterations",
        ),
        timeout_sec=360,
        evidence_refs=("Goal3827", "Goal3983", "Goal3984"),
        expected_runtime_class="resident_high_repeat_hot_path_summary",
        representative_hot_path_metric="metadata.prepared_phase_timing_summary.native_call_wall.total_sec",
        hot_path_duration_target_sec=1.0,
        scale_calibration_status="resident_high_repeat_summary_contract_goal3984",
    ),
    CurrentBenchmarkScaleProfile(
        app="barnes_hut",
        row_id="barnes_hut_numba_scale_default_8192",
        purpose=(
            "scale-profile Barnes-Hut no-RawKernel Numba exact-force run with resident output reuse; "
            "Goal4053 separately covers prepared grouped-vector stream reductions"
        ),
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
            "--mode",
            "partner_exact_force",
            "--partner",
            "numba",
            "--force-output-mode",
            "force_summary",
            "--body-count",
            "8192",
            "--skip-validation",
            "--repeat",
            "3",
            "--warmup",
            "1",
        ),
        timeout_sec=300,
        evidence_refs=("Goal3827", "Goal3853", "Goal3869", "Goal4052", "Goal4053"),
        expected_runtime_class="safe_summary_output",
        requires_numba=True,
        representative_hot_path_metric="partner_metadata.prepared_force_repeat_protocol.median_force_kernel_sec",
    ),
    CurrentBenchmarkScaleProfile(
        app="librts_spatial_index",
        row_id="librts_spatial_index_optix_scale_default_32768",
        purpose="scale-profile LibRTS-style prepared OptiX AABB-index run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
            "--mode",
            "optix_aabb_index",
            "--dataset",
            "uniform",
            "--box-count",
            "32768",
            "--query-count",
            "32768",
            "--operation",
            "all",
            "--repeat",
            "3",
            "--warmup",
            "1",
            "--skip-counts",
        ),
        timeout_sec=240,
        evidence_refs=("Goal3827",),
        expected_runtime_class="safe_medium",
        representative_hot_path_metric="run_phases.query_median_sec",
    ),
    CurrentBenchmarkScaleProfile(
        app="rtnn",
        row_id="rtnn_prepared_optix_scale_default_65536",
        purpose="scale-profile RTNN prepared OptiX ranked-summary run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py",
            "--mode",
            "prepared_optix_ranked_summary",
            "--point-count",
            "65536",
            "--radius",
            "0.02",
            "--k",
            "50",
            "--repeat",
            "3",
            "--query-batch-size",
            "65536",
            "--distribution",
            "uniform",
        ),
        timeout_sec=180,
        evidence_refs=("Goal3827",),
        expected_runtime_class="safe_medium",
        representative_hot_path_metric="runner_payload.elapsed_median_sec",
    ),
    CurrentBenchmarkScaleProfile(
        app="triangle_counting",
        row_id="triangle_counting_optix_rt_graph_2a1_scale_default_2048",
        purpose="scale-profile triangle-counting RT-Graph 2A1 prepared generic ray-triangle summary run",
        profile_kind="default_scale",
        command=(
            "python",
            "examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "rt_graph_2a1_generic_rt",
            "--backend",
            "optix",
            "--fixture",
            "degree_oriented_two_triangles",
            "--rt-graph-copies",
            "2048",
            "--detail",
            "summary",
            "--repeat",
            "3",
            "--warmup",
            "1",
        ),
        timeout_sec=240,
        evidence_refs=("Goal3827", "Goal3856"),
        expected_runtime_class="safe_but_short",
        representative_hot_path_metric="timing_ms.query_median_ms",
    ),
)


def current_benchmark_scale_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_BENCHMARK_SCALE_PROFILES)


def summarize_current_benchmark_scale_profiles(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_scale_profiles()
    return {
        "version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
        "status": CURRENT_BENCHMARK_SCALE_PROFILE_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "profile_kinds": tuple(sorted({row["profile_kind"] for row in matrix})),
        "file_backed_stdout_rows": tuple(
            row["row_id"] for row in matrix if row["stdout_policy"] == "file_backed_stdout_required"
        ),
        "numba_required_rows": tuple(row["row_id"] for row in matrix if row["requires_numba"]),
        "optix_required_rows": tuple(row["row_id"] for row in matrix if row["requires_optix_library"]),
        "timing_metric_scope": "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric",
        "scale_calibration_statuses": tuple(sorted({row["scale_calibration_status"] for row in matrix})),
        "claim_boundary": CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def validate_current_benchmark_scale_profiles(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_benchmark_scale_profiles()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    row_ids = [str(row.get("row_id", "")) for row in matrix]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row_id values must be unique")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        command = row.get("command")
        if not isinstance(command, tuple) or not command:
            errors.append(f"{app}: command must be a non-empty tuple")
        if row.get("profile_kind") not in {"default_scale", "stress_scale"}:
            errors.append(f"{app}: profile_kind must be default_scale or stress_scale")
        if row.get("stdout_policy") != "file_backed_stdout_required":
            errors.append(f"{app}: stdout_policy must require file-backed stdout")
        if not row.get("purpose"):
            errors.append(f"{app}: purpose must be explicit")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: evidence_refs must be non-empty")
        if not row.get("expected_runtime_class"):
            errors.append(f"{app}: expected_runtime_class must be explicit")
        if not isinstance(row.get("timeout_sec"), int) or int(row.get("timeout_sec", 0)) <= 0:
            errors.append(f"{app}: timeout_sec must be positive")
        if row.get("timing_metric_scope") != "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric":
            errors.append(f"{app}: timing_metric_scope must keep wrapper elapsed out of hot-path claims")
        if not row.get("representative_hot_path_metric"):
            errors.append(f"{app}: representative_hot_path_metric must be explicit")
        target = row.get("hot_path_duration_target_sec")
        if target is not None and (not isinstance(target, (int, float)) or float(target) <= 0.0):
            errors.append(f"{app}: hot_path_duration_target_sec must be positive when set")
        if not row.get("scale_calibration_status"):
            errors.append(f"{app}: scale_calibration_status must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_BENCHMARK_SCALE_PROFILE_CLAIM_BOUNDARY,
    }
