from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .current_benchmark_scale_profiles import CURRENT_BENCHMARK_SCALE_PROFILE_VERSION
from .prepared_session_residency import (
    PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
    PREPARED_SESSION_RESIDENCY_VERSION,
    RtdlPreparedSessionResidencyPolicy,
    RtdlPreparedSessionTimingRecord,
    make_prepared_session_cache_key,
    summarize_prepared_session_timing_records,
)
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION = (
    "rtdl.v2_10.current_prepared_session_residency_profiles.goal3874.v1"
)
CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_STATUS = (
    "internal_profile_registry_not_release_authorization"
)
CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_CLAIM_BOUNDARY = (
    "Goal3874 records current prepared-session residency profiles for measured "
    "scene-heavy benchmark rows. It does not authorize release action, public "
    "speedup wording, broad RT-core wording, true-zero-copy wording, automatic "
    "partner/backend selection, or app-specific native-engine logic."
)


@dataclass(frozen=True)
class CurrentPreparedSessionResidencyProfile:
    app: str
    row_id: str
    scale_profile_row_id: str
    primitive: str
    backend: str
    partner: str
    device: str
    input_fingerprints: Mapping[str, Any]
    parameters: Mapping[str, Any]
    prepare_sec: float
    hot_query_sec: float
    repeat: int
    warmup: int
    evidence_refs: tuple[str, ...]
    cache_enabled_by_default: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown benchmark app: {self.app}")
        if not self.row_id or not self.scale_profile_row_id:
            raise ValueError("prepared-session profile requires explicit row ids")
        if float(self.prepare_sec) <= 0.0:
            raise ValueError("prepare_sec must be positive")
        if float(self.hot_query_sec) <= 0.0:
            raise ValueError("hot_query_sec must be positive")
        if int(self.repeat) <= 0:
            raise ValueError("repeat must be positive")
        if int(self.warmup) < 0:
            raise ValueError("warmup must be non-negative")
        if not self.evidence_refs:
            raise ValueError("prepared-session profile requires evidence refs")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.row_id}: {flag} must remain false")

    @property
    def cache_key(self):
        return make_prepared_session_cache_key(
            primitive=self.primitive,
            backend=self.backend,
            input_fingerprints=self.input_fingerprints,
            parameters=self.parameters,
            partner=self.partner,
            device=self.device,
        )

    @property
    def policy(self) -> RtdlPreparedSessionResidencyPolicy:
        return RtdlPreparedSessionResidencyPolicy(
            cache_key=self.cache_key,
            cache_enabled=self.cache_enabled_by_default,
            lifetime_state="session_retained",
            reuse_scope="explicit_user_session",
            invalidation_events=("explicit_invalidate", "backend_context_reset", "close"),
        )

    @property
    def timing_record(self) -> RtdlPreparedSessionTimingRecord:
        return RtdlPreparedSessionTimingRecord(
            row_id=self.row_id,
            prepare_sec=self.prepare_sec,
            hot_query_sec=self.hot_query_sec,
            repeat=self.repeat,
            warmup=self.warmup,
            request_count=1,
            prepared_session_policy=self.policy,
        )

    def to_metadata(self) -> dict[str, Any]:
        timing = self.timing_record.to_metadata()
        return {
            "version": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION,
            "status": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_STATUS,
            "app": self.app,
            "row_id": self.row_id,
            "scale_profile_row_id": self.scale_profile_row_id,
            "scale_profile_version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
            "prepared_session_contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "primitive": self.primitive,
            "backend": self.backend,
            "partner": self.partner,
            "device": self.device,
            "cache_key": self.cache_key.to_metadata(),
            "policy": self.policy.to_metadata(),
            "timing": timing,
            "prepared_session_reuse_recommended": (
                float(timing["prepare_to_hot_query_ratio"]) >= 10.0
            ),
            "cache_enabled_by_default": bool(self.cache_enabled_by_default),
            "evidence_refs": self.evidence_refs,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_CLAIM_BOUNDARY,
        }


CURRENT_PREPARED_SESSION_RESIDENCY_PROFILES: tuple[CurrentPreparedSessionResidencyProfile, ...] = (
    CurrentPreparedSessionResidencyProfile(
        app="hausdorff_xhd",
        row_id="hausdorff_xhd_prepared_threshold_residency",
        scale_profile_row_id="hausdorff_xhd_scale_default_optix_threshold",
        primitive="fixed_radius_threshold_2d",
        backend="optix",
        partner="none",
        device="cuda:0",
        input_fingerprints={"query_points": "copies_1024", "search_points": "goal3872_fixture"},
        parameters={"threshold": 0.25},
        prepare_sec=0.7434872528538108,
        hot_query_sec=0.010264009535312653,
        repeat=50,
        warmup=5,
        evidence_refs=("Goal3872",),
    ),
    CurrentPreparedSessionResidencyProfile(
        app="librts_spatial_index",
        row_id="librts_spatial_index_aabb_residency",
        scale_profile_row_id="librts_spatial_index_optix_scale_default_32768",
        primitive="aabb_index_query_2d",
        backend="optix",
        partner="none",
        device="cuda:0",
        input_fingerprints={"boxes": "32768_uniform", "queries": "32768_uniform"},
        parameters={"operation": "all"},
        prepare_sec=0.40261318255215883,
        hot_query_sec=0.02966476557776332,
        repeat=50,
        warmup=5,
        evidence_refs=("Goal3872",),
    ),
    CurrentPreparedSessionResidencyProfile(
        app="rtnn",
        row_id="rtnn_ranked_summary_residency",
        scale_profile_row_id="rtnn_prepared_optix_scale_default_65536",
        primitive="fixed_radius_neighbors_3d_ranked_summary",
        backend="optix",
        partner="none",
        device="cuda:0",
        input_fingerprints={"points": "65536_uniform", "queries": "65536_uniform"},
        parameters={"radius": 0.02, "k": 50},
        prepare_sec=1.7026465376839042,
        hot_query_sec=0.00013345852494239807,
        repeat=50,
        warmup=5,
        evidence_refs=("Goal3872",),
    ),
    CurrentPreparedSessionResidencyProfile(
        app="triangle_counting",
        row_id="triangle_counting_weighted_sum_residency",
        scale_profile_row_id="triangle_counting_optix_rt_graph_2a1_scale_default_2048",
        primitive="ray_triangle_weighted_any_hit_sum_3d",
        backend="optix",
        partner="none",
        device="cuda:0",
        input_fingerprints={"triangle_scene": "degree_oriented_two_triangles_2048"},
        parameters={"detail": "summary"},
        prepare_sec=0.39183870516717434,
        hot_query_sec=0.00015036482363939285,
        repeat=50,
        warmup=5,
        evidence_refs=("Goal3872",),
    ),
)


def current_prepared_session_residency_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_PREPARED_SESSION_RESIDENCY_PROFILES)


def summarize_current_prepared_session_residency_profiles(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_prepared_session_residency_profiles()
    timing_rows = tuple(
        RtdlPreparedSessionTimingRecord(
            row_id=str(row["row_id"]),
            prepare_sec=float(row["timing"]["prepare_sec"]),
            hot_query_sec=float(row["timing"]["hot_query_sec"]),
            repeat=int(row["timing"]["repeat"]),
            warmup=int(row["timing"]["warmup"]),
        )
        for row in matrix
    )
    timing_summary = summarize_prepared_session_timing_records(timing_rows)
    return {
        "version": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION,
        "status": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_STATUS,
        "row_count": len(matrix),
        "app_count": len({row["app"] for row in matrix}),
        "prepared_session_contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
        "geomean_prepare_to_hot_query_ratio": timing_summary[
            "geomean_prepare_to_hot_query_ratio"
        ],
        "max_prepare_to_hot_query_ratio": timing_summary["max_prepare_to_hot_query_ratio"],
        "reuse_recommended_rows": tuple(
            row["row_id"] for row in matrix if row["prepared_session_reuse_recommended"]
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "claim_boundary": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_CLAIM_BOUNDARY,
    }


def validate_current_prepared_session_residency_profiles(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_prepared_session_residency_profiles()
    errors: list[str] = []
    row_ids = [str(row.get("row_id", "")) for row in matrix]
    if len(row_ids) != len(set(row_ids)):
        errors.append("prepared-session residency row ids must be unique")
    if len(matrix) < 4:
        errors.append("current prepared-session residency profiles must cover the Goal3872 rows")
    for row in matrix:
        label = str(row.get("row_id", "<missing>"))
        if row.get("prepared_session_contract_version") != PREPARED_SESSION_RESIDENCY_VERSION:
            errors.append(f"{label}: unexpected prepared-session contract version")
        if not row.get("scale_profile_row_id"):
            errors.append(f"{label}: missing scale-profile row id")
        if float(row.get("timing", {}).get("prepare_to_hot_query_ratio", 0.0)) < 10.0:
            errors.append(f"{label}: ratio is too small for residency profile")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{label}: {flag} must remain false")
        cache_key = row.get("cache_key", {})
        primitive = str(cache_key.get("primitive", ""))
        for term in ("hausdorff", "rayjoin", "dbscan", "barnes", "database", "pip", "polygon", "knn"):
            if term in primitive.lower():
                errors.append(f"{label}: primitive contains app-shaped term {term}")
    return {
        "version": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "row_count": len(matrix),
        "claim_boundary": CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_CLAIM_BOUNDARY,
        "prepared_session_claim_boundary": PREPARED_SESSION_RESIDENCY_CLAIM_BOUNDARY,
    }


__all__ = [
    "CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_CLAIM_BOUNDARY",
    "CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_STATUS",
    "CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION",
    "CURRENT_PREPARED_SESSION_RESIDENCY_PROFILES",
    "CurrentPreparedSessionResidencyProfile",
    "current_prepared_session_residency_profiles",
    "summarize_current_prepared_session_residency_profiles",
    "validate_current_prepared_session_residency_profiles",
]
