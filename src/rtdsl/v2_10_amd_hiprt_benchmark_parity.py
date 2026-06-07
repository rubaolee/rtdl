from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .engine_feature_matrix import COMPATIBILITY_FALLBACK
from .engine_feature_matrix import NATIVE
from .engine_feature_matrix import NATIVE_ASSISTED
from .engine_feature_matrix import engine_feature_support
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION = "rtdl.v2_10.amd_hiprt_benchmark_parity_plan.v1"
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
        required_engine_features=("point_nearest_segment_2d", "knn_rows_2d"),
        missing_generic_contracts=("nearest_witness_output_columns", "grouped_max_distance_reduction"),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT nearest-witness columns plus grouped max reduction parity",
        rationale="HIPRT has nearest/knn primitives, but the benchmark needs the v2.x witness-column and reduction contract.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="spatial_rayjoin",
        required_engine_features=("point_in_polygon_2d", "line_segment_intersection_2d", "overlay_compose_2d"),
        missing_generic_contracts=("prepared_segment_pair_exact_count", "prepared_shape_pair_active_count"),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT prepared segment-pair count and shape-pair active-count parity",
        rationale="HIPRT has base PIP/LSI/overlay proof paths, but the fast RayJoin route depends on prepared scalar executors.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="rt_dbscan",
        required_engine_features=("fixed_radius_neighbors_3d",),
        missing_generic_contracts=("fixed_radius_grouped_stream_flags",),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT fixed-radius grouped stream and component-continuation handoff parity",
        rationale="The base 3D fixed-radius path exists, but the benchmark needs grouped stream flags matching the OptiX bridge.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="robot_collision",
        required_engine_features=("ray_triangle_any_hit_3d", "visibility_rows"),
        missing_generic_contracts=(),
        parity_stage="ready_for_amd_functional_pod",
        first_amd_goal="HIPRT prepared any-hit functional parity on robot-collision batches",
        rationale="The benchmark is closest to existing HIPRT any-hit/visibility surfaces.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="contact_manifold",
        required_engine_features=("ray_triangle_closest_hit_3d", "ray_triangle_any_hit_3d"),
        missing_generic_contracts=("bounded_contact_witness_collection",),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT bounded witness collection parity",
        rationale="Closest/any-hit primitives exist, but the benchmark needs the bounded contact-witness output contract.",
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
        required_engine_features=("visibility_rows", "ray_triangle_any_hit_3d"),
        missing_generic_contracts=("prepared_aabb_query",),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT prepared AABB query parity",
        rationale="The current app needs a prepared AABB/index contract rather than only generic ray-triangle any-hit rows.",
        needs_amd_pod=True,
    ),
    V210AmdHiprtBenchmarkParityRow(
        app="rtnn",
        required_engine_features=("fixed_radius_neighbors_3d", "knn_rows_3d"),
        missing_generic_contracts=("ranked_summary_aggregate", "batched_prepared_query_sweep"),
        parity_stage="needs_generic_hiprt_extension",
        first_amd_goal="HIPRT fixed-radius ranked-summary aggregate parity",
        rationale="Base fixed-radius/KNN entries exist, but the benchmark depends on ranked summaries and batched prepared sweeps.",
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
