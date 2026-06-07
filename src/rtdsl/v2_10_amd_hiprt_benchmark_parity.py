from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine_feature_matrix import COMPATIBILITY_FALLBACK
from .engine_feature_matrix import NATIVE
from .engine_feature_matrix import NATIVE_ASSISTED
from .engine_feature_matrix import engine_feature_support
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION = "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3776.v1"
V2_10_AMD_HIPRT_BENCHMARK_PARITY_STATUS = "planning_gate_not_amd_hardware_evidence"

PARITY_STAGES = (
    "ready_for_amd_functional_pod",
    "needs_generic_hiprt_extension",
    "compatibility_only_not_amd_perf_ready",
)

CLAIM_BOUNDARY = (
    "This AMD/HIPRT benchmark parity map is a planning gate. It does not "
    "authorize AMD performance claims, HIPRT release claims, public speedup "
    "wording, whole-app acceleration wording, or RTDL-beats-paper wording."
)


@dataclass(frozen=True)
class V210AmdHiprtBenchmarkParityRow:
    app: str
    required_engine_features: tuple[str, ...]
    missing_generic_contracts: tuple[str, ...]
    parity_stage: str
    first_amd_goal: str
    rationale: str
    needs_amd_pod: bool
    release_authorized: bool = False
    amd_perf_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.parity_stage not in PARITY_STAGES:
            raise ValueError(f"{self.app}: invalid parity stage {self.parity_stage!r}")
        if not self.required_engine_features and not self.missing_generic_contracts:
            raise ValueError(f"{self.app}: at least one required or missing contract must be listed")
        if not self.first_amd_goal.strip() or not self.rationale.strip():
            raise ValueError(f"{self.app}: first AMD goal and rationale must be explicit")
        for feature in self.required_engine_features:
            engine_feature_support(feature, "hiprt")
        for flag in (
            "release_authorized",
            "amd_perf_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def hiprt_feature_statuses(self) -> dict[str, str]:
        return {
            feature: engine_feature_support(feature, "hiprt").status
            for feature in self.required_engine_features
        }

    def to_metadata(self) -> dict[str, Any]:
        statuses = self.hiprt_feature_statuses()
        return {
            "version": V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "app": self.app,
            "required_engine_features": self.required_engine_features,
            "hiprt_feature_statuses": statuses,
            "missing_generic_contracts": self.missing_generic_contracts,
            "parity_stage": self.parity_stage,
            "first_amd_goal": self.first_amd_goal,
            "rationale": self.rationale,
            "needs_amd_pod": self.needs_amd_pod,
            "native_feature_count": sum(1 for status in statuses.values() if status == NATIVE),
            "native_or_assisted_feature_count": sum(
                1 for status in statuses.values() if status in {NATIVE, NATIVE_ASSISTED}
            ),
            "compatibility_fallback_feature_count": sum(
                1 for status in statuses.values() if status == COMPATIBILITY_FALLBACK
            ),
            "release_authorized": self.release_authorized,
            "amd_perf_claim_authorized": self.amd_perf_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CLAIM_BOUNDARY,
        }


V2_10_AMD_HIPRT_BENCHMARK_PARITY_ROWS: tuple[V210AmdHiprtBenchmarkParityRow, ...] = (
    V210AmdHiprtBenchmarkParityRow(
        app="hausdorff_xhd",
        required_engine_features=(
            "point_nearest_segment_2d",
            "knn_rows_2d",
            "point_group_nearest_witness_2d",
            "point_group_nearest_witness_output_columns_2d",
            "point_group_nearest_max_distance_2d",
        ),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="Hausdorff/X-HD HIPRT functional parity on AMD hardware",
        rationale=(
            "HIPRT has nearest/knn primitives, and Goal3773 adds generic prepared point-group nearest witness rows "
            "plus max-distance reduction on the NVIDIA CUDA/Orochi route. Goal3774 adds the generic nearest-witness "
            "output-column contract on the same route, so the lane is ready for AMD functional pod validation but "
            "has no AMD hardware evidence yet."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="spatial_rayjoin",
        required_engine_features=(
            "point_in_polygon_2d",
            "line_segment_intersection_2d",
            "overlay_compose_2d",
            "prepared_segment_pair_exact_count_2d",
            "prepared_shape_pair_active_count_2d",
        ),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="RayJoin HIPRT functional parity on AMD hardware",
        rationale=(
            "HIPRT has base PIP/LSI/overlay proof paths, and Goal3766 adds the generic prepared "
            "segment-pair exact-count scalar executor on the NVIDIA CUDA/Orochi path. "
            "Goal3767 adds a prepared right-shape payload plus scalar active-count query, also on the NVIDIA CUDA/Orochi path. "
            "The RayJoin lane is ready for AMD functional pod validation, but has no AMD hardware evidence yet."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="rt_dbscan",
        required_engine_features=(
            "fixed_radius_neighbors_3d",
            "fixed_radius_threshold_reached_count_3d",
            "fixed_radius_grouped_stream_flags_3d",
        ),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="RT-DBSCAN HIPRT functional parity on AMD hardware",
        rationale=(
            "The base 3D fixed-radius path exists, and Goal3768 adds a scalar threshold-reached count path "
            "on the NVIDIA CUDA/Orochi HIPRT route. Goal3769 adds per-query threshold/core flags for downstream "
            "grouped/component continuations. The lane is ready for AMD functional pod validation, but has no AMD hardware evidence yet."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="robot_collision",
        required_engine_features=("ray_triangle_any_hit_2d", "visibility_rows", "prepared_grouped_visibility_flags_2d"),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="HIPRT prepared grouped visibility flags functional parity on robot-collision batches",
        rationale=(
            "Goal3755 exposes the robot collision app's Ray2D/Triangle2D row route through --backend hiprt. "
            "Goal3763 confirms the HIPRT CUDA/Orochi path builds and passes focused HIPRT tests on an NVIDIA A5000, "
            "but that is not AMD hardware evidence. "
            "Goal3765 adds a generic HIPRT prepared grouped visibility-flag summary for the same app route, "
            "validated on the NVIDIA CUDA/Orochi path but still awaiting AMD hardware evidence."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="contact_manifold",
        required_engine_features=("ray_triangle_closest_hit_3d", "ray_triangle_any_hit_3d", "collect_k_bounded_i64"),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="Contact-manifold HIPRT functional parity on AMD hardware",
        rationale=(
            "Goal3775 makes the generic HIPRT 3D ray/triangle closest-hit primitive executable on the "
            "NVIDIA CUDA/Orochi path, and any-hit already exists. Goal3776 adds the generic HIPRT "
            "COLLECT_K_BOUNDED i64 host-native materializer for bounded witness rows. The lane is ready "
            "for AMD functional pod validation, but has no AMD hardware evidence yet."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="raydb_style",
        required_engine_features=("bounded_db_conjunctive_scan", "bounded_db_grouped_count", "bounded_db_grouped_sum"),
        missing_generic_contracts=("native_hiprt_grouped_i64_count_sum_fastpath",),
        parity_stage="compatibility_only_not_amd_perf_ready",
        first_amd_goal="HIPRT grouped DB count/sum primitive promotion beyond compatibility fallback",
        rationale="The current HIPRT DB entries are compatibility fallback and explicitly not AMD performance evidence.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="barnes_hut",
        required_engine_features=("fixed_radius_neighbors_2d", "point_in_polygon_2d"),
        missing_generic_contracts=("grouped_vector_force_reduction", "hierarchical_node_coverage_summary"),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT membership summary plus grouped vector reduction parity",
        rationale="The scalar/membership pieces exist, but the benchmark's force-vector continuation is not a HIPRT primitive yet.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="librts_spatial_index",
        required_engine_features=("visibility_rows", "ray_triangle_any_hit_3d", "prepared_aabb_query_2d"),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="LibRTS HIPRT prepared AABB query functional parity on AMD hardware",
        rationale=(
            "Goal3770 adds a generic HIPRT prepared AABB_INDEX_QUERY_2D count path for point_contains, "
            "range_contains, and range_intersects on the NVIDIA CUDA/Orochi route. The lane is ready for "
            "AMD functional pod validation, but has no AMD hardware or row-output evidence yet."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="rtnn",
        required_engine_features=(
            "fixed_radius_neighbors_3d",
            "knn_rows_3d",
            "fixed_radius_ranked_summary_aggregate_3d",
            "fixed_radius_ranked_summary_batched_sweep_3d",
        ),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="RTNN HIPRT functional parity on AMD hardware",
        rationale=(
            "Base fixed-radius/KNN entries exist, and Goal3771 adds the generic prepared fixed-radius "
            "ranked-summary aggregate on the NVIDIA CUDA/Orochi HIPRT route. Goal3772 adds the generic "
            "prepared ranked-summary batched sweep, so the RTNN lane is ready for AMD functional pod "
            "validation but still has no AMD hardware evidence."
        ),
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="triangle_counting",
        required_engine_features=("graph_triangle_count",),
        missing_generic_contracts=("native_hiprt_graph_summary_fastpath",),
        parity_stage="compatibility_only_not_amd_perf_ready",
        first_amd_goal="HIPRT graph-summary primitive promotion beyond compatibility fallback",
        rationale="The current HIPRT graph triangle-count surface is compatibility fallback with known scaling limits.",
        needs_amd_pod=True,
    ),
)


def v2_10_amd_hiprt_benchmark_parity_rows() -> tuple[V210AmdHiprtBenchmarkParityRow, ...]:
    return V2_10_AMD_HIPRT_BENCHMARK_PARITY_ROWS


def v2_10_amd_hiprt_benchmark_parity() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_10_AMD_HIPRT_BENCHMARK_PARITY_ROWS)


def summarize_v2_10_amd_hiprt_benchmark_parity(rows: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_10_amd_hiprt_benchmark_parity()
    stage_counts = {stage: 0 for stage in PARITY_STAGES}
    for row in matrix:
        stage_counts[str(row["parity_stage"])] += 1
    return {
        "version": V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
        "status": V2_10_AMD_HIPRT_BENCHMARK_PARITY_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "stage_counts": stage_counts,
        "ready_for_amd_functional_pod_apps": tuple(
            row["app"] for row in matrix if row["parity_stage"] == "ready_for_amd_functional_pod"
        ),
        "needs_generic_hiprt_extension_apps": tuple(
            row["app"] for row in matrix if row["parity_stage"] == "needs_generic_hiprt_extension"
        ),
        "compatibility_only_not_amd_perf_ready_apps": tuple(
            row["app"] for row in matrix if row["parity_stage"] == "compatibility_only_not_amd_perf_ready"
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "release_authorized": False,
        "amd_perf_claim_authorized": False,
    }


def validate_v2_10_amd_hiprt_benchmark_parity(rows: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_10_amd_hiprt_benchmark_parity()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        if row.get("parity_stage") not in PARITY_STAGES:
            errors.append(f"{app}: invalid parity stage")
        if not row.get("required_engine_features") and not row.get("missing_generic_contracts"):
            errors.append(f"{app}: missing feature/contract coverage")
        for feature in row.get("required_engine_features", ()):
            try:
                engine_feature_support(str(feature), "hiprt")
            except ValueError as exc:
                errors.append(f"{app}: unknown HIPRT feature {feature!r}: {exc}")
        if row.get("parity_stage") == "ready_for_amd_functional_pod" and row.get("missing_generic_contracts"):
            errors.append(f"{app}: ready stage must not list missing generic contracts")
        if row.get("parity_stage") == "compatibility_only_not_amd_perf_ready":
            statuses = row.get("hiprt_feature_statuses", {})
            if not any(status == COMPATIBILITY_FALLBACK for status in statuses.values()):
                errors.append(f"{app}: compatibility-only stage must reference at least one compatibility fallback feature")
        for flag in (
            "release_authorized",
            "amd_perf_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": CLAIM_BOUNDARY,
    }
