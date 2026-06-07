from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_9_BENCHMARK_ADEQUACY_VERSION = "rtdl.v2_9.benchmark_adequacy_after_goal3746.v1"
V2_9_BENCHMARK_ADEQUACY_STATUS = "internal_perf_triage_not_release_authorization"
V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY = (
    "Goal3740 records internal benchmark-app adequacy after the Goal3737 "
    "RayJoin executor packet. It does not authorize release action, public "
    "speedup wording, whole-app acceleration wording, broad RT-core wording, "
    "RayJoin paper reproduction wording, true-zero-copy wording, automatic "
    "partner selection, or app-specific native-engine logic."
)

ADEQUACY_LEVELS = (
    "strong",
    "adequate",
    "near_parity",
    "needs_major_followup",
)


@dataclass(frozen=True)
class V29BenchmarkAdequacyRow:
    app: str
    promoted_reader_view: str
    current_performance_reading: str
    adequacy: str
    current_recommended_path: str
    current_partner_role: str
    needs_numba_reference: bool
    numba_reference_reason: str
    amd_hiprt_readiness: str
    next_generic_runtime_action: str
    evidence_refs: tuple[str, ...]
    pod_needed_next: bool
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown promoted benchmark app: {self.app}")
        if self.adequacy not in ADEQUACY_LEVELS:
            raise ValueError(f"unknown adequacy level: {self.adequacy}")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        for field in (
            "promoted_reader_view",
            "current_performance_reading",
            "current_recommended_path",
            "current_partner_role",
            "numba_reference_reason",
            "amd_hiprt_readiness",
            "next_generic_runtime_action",
        ):
            value = getattr(self, field)
            if not value or value.strip().lower() == "n/a":
                raise ValueError(f"{self.app}: {field} must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_9_BENCHMARK_ADEQUACY_VERSION,
            "app": self.app,
            "promoted_reader_view": self.promoted_reader_view,
            "current_performance_reading": self.current_performance_reading,
            "adequacy": self.adequacy,
            "current_recommended_path": self.current_recommended_path,
            "current_partner_role": self.current_partner_role,
            "needs_numba_reference": self.needs_numba_reference,
            "numba_reference_reason": self.numba_reference_reason,
            "amd_hiprt_readiness": self.amd_hiprt_readiness,
            "next_generic_runtime_action": self.next_generic_runtime_action,
            "evidence_refs": self.evidence_refs,
            "pod_needed_next": self.pod_needed_next,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
        }


V2_9_BENCHMARK_ADEQUACY_ROWS: tuple[V29BenchmarkAdequacyRow, ...] = (
    V29BenchmarkAdequacyRow(
        app="hausdorff_xhd",
        promoted_reader_view="exact Hausdorff/X-HD-style nearest-witness computation",
        current_performance_reading=(
            "adequate: v2.9 packet row is positive versus v2.3 at 1.019555x, and "
            "separate X-HD lab evidence shows the RTDL/OptiX path uses RT traversal; "
            "not a claim to beat the X-HD paper implementation"
        ),
        adequacy="adequate",
        current_recommended_path="RTDL/OptiX nearest-witness primitives plus generic grouped max continuation",
        current_partner_role="Numba exists as an exact partner/front-door reference; promoted RT path is primitive-first",
        needs_numba_reference=False,
        numba_reference_reason="already has a Numba exact continuation reference and a primitive-first promoted path",
        amd_hiprt_readiness="needs HIPRT mapping for nearest-witness output columns and grouped max reduction",
        next_generic_runtime_action="keep as reference; use for AMD parity once HIPRT nearest-witness columns exist",
        evidence_refs=("Goal2801", "Goal3143", "Goal3567"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="spatial_rayjoin",
        promoted_reader_view="RayJoin-style spatial joins with PIP, LSI, and overlay active-count subcontracts",
        current_performance_reading=(
            "strong but contract-specific: Goal3737 safe-mixed public-CDB composite reaches "
            "324.324x geomean versus all-CuPy across 1024/2048/4096, with 4096 at 624.255x; "
            "still not a RayJoin paper-reproduction or RTDL-beats-RayJoin claim"
        ),
        adequacy="strong",
        current_recommended_path=(
            "mixed explicit route: CuPy dense PIP for the conservative leg, exact RTDL/OptiX "
            "prepared segment-pair count for LSI, and RTDL/OptiX prepared-left shape-pair "
            "active-count executor for overlay active count"
        ),
        current_partner_role="CuPy remains in the conservative PIP leg; RTDL/OptiX owns the high-gain LSI and overlay legs",
        needs_numba_reference=True,
        numba_reference_reason=(
            "the user-facing reference should not require CuPy RawKernel-style custom logic for closed-shape "
            "membership/topology continuation when Numba can express the app-owned policy"
        ),
        amd_hiprt_readiness="needs HIPRT equivalents for segment-pair exact count and shape-pair active-count executor",
        next_generic_runtime_action=(
            "either make native closed-shape/PIP exact across broad CDB slices or reduce overlay active-scan/"
            "containment work with a generic scalar-count/correction executor"
        ),
        evidence_refs=("Goal3733", "Goal3734", "Goal3737"),
        pod_needed_next=True,
    ),
    V29BenchmarkAdequacyRow(
        app="rt_dbscan",
        promoted_reader_view="RT-DBSCAN-style fixed-radius grouped stream and component labeling",
        current_performance_reading=(
            "adequate with boundary: v2.9 packet row is 0.997206x versus v2.3; Goal3742 adds a "
            "Numba grid component reference and Goal3744 bridges OptiX RT-core threshold flags into "
            "Numba continuation with mixed but real A5000 evidence"
        ),
        adequacy="adequate",
        current_recommended_path="RTDL/OptiX fixed-radius grouped stream plus app-owned component continuation",
        current_partner_role="CuPy and Numba component continuations both exist; users choose explicitly",
        needs_numba_reference=False,
        numba_reference_reason="Numba grid component labeling and OptiX-to-Numba bridge now exist as measured references",
        amd_hiprt_readiness="needs HIPRT fixed-radius grouped stream parity before AMD performance work",
        next_generic_runtime_action="treat as covered for Numba-reference purposes; next major work is HIPRT fixed-radius parity",
        evidence_refs=("Goal2802", "Goal3567", "Goal3742", "Goal3744"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="robot_collision",
        promoted_reader_view="prepared any-hit collision flags",
        current_performance_reading="near parity: v2.9 packet row is 0.987619x versus v2.3",
        adequacy="near_parity",
        current_recommended_path="prepared RTDL/OptiX any-hit flag primitive",
        current_partner_role="no partner needed for the promoted path",
        needs_numba_reference=False,
        numba_reference_reason="no custom GPU continuation is required by the promoted flag contract",
        amd_hiprt_readiness="needs HIPRT prepared any-hit parity on the same pose/shape contract",
        next_generic_runtime_action="treat as no-regression unless a larger pose batch exposes material overhead",
        evidence_refs=("Goal2654", "Goal3567"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="contact_manifold",
        promoted_reader_view="bounded contact-witness collection",
        current_performance_reading="adequate: v2.9 packet row is 1.219528x versus v2.3",
        adequacy="adequate",
        current_recommended_path="prepared bounded witness collection primitive",
        current_partner_role="no partner needed on the accepted current path",
        needs_numba_reference=False,
        numba_reference_reason="the promoted path is primitive-only; richer exact refinement can stay future work",
        amd_hiprt_readiness="needs HIPRT bounded witness collection parity",
        next_generic_runtime_action="keep as a primitive-only reference row; retest after HIPRT mapping",
        evidence_refs=("Goal2654", "Goal3567"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="raydb_style",
        promoted_reader_view="RayDB-style grouped count and sum reductions",
        current_performance_reading="adequate/strong: count is 1.009085x and sum is 1.585627x versus v2.3 after the generic fast path",
        adequacy="adequate",
        current_recommended_path="primitive-first RTDL/OptiX fused grouped count/sum reductions",
        current_partner_role="no partner is recommended for fused scalar reductions; Triton/CuPy are not promoted here",
        needs_numba_reference=False,
        numba_reference_reason="the generic primitive outperforms partner continuation for this fused reduction shape",
        amd_hiprt_readiness="needs HIPRT grouped i64 count/sum primitive mapping",
        next_generic_runtime_action="preserve primitive-first path; use as AMD grouped-reduction parity target",
        evidence_refs=("Goal3565", "Goal3567"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="barnes_hut",
        promoted_reader_view="Barnes-Hut node membership plus grouped force-vector reduction",
        current_performance_reading=(
            "adequate with boundary: current packet no longer has a silent partial, and Goal3746 adds "
            "a Numba CUDA JIT exact-force reference that matches the CPU oracle and reaches 0.754x to "
            "0.893x of the CuPy RawKernel path across 1024-8192 bodies on the A5000"
        ),
        adequacy="adequate",
        current_recommended_path="RTDL/OptiX membership primitive plus explicit partner exact-force/vector continuation",
        current_partner_role="CuPy remains fastest in the measured exact-force route; Numba is the no-RawKernel reference",
        needs_numba_reference=False,
        numba_reference_reason="Goal3746 adds the Numba CUDA JIT exact-force reference; richer hierarchical force acceleration remains separate future work",
        amd_hiprt_readiness="needs HIPRT membership primitive and grouped vector output contract mapping",
        next_generic_runtime_action="treat as covered for Numba-reference purposes; next major work is HIPRT membership parity or deeper hierarchical vector primitive design",
        evidence_refs=("Goal2803", "Goal3599", "Goal3567", "Goal3746"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="librts_spatial_index",
        promoted_reader_view="prepared AABB spatial-index query",
        current_performance_reading="near parity/adequate: clean resident same-contract evidence is 1.005864x; composite row is 0.991776x",
        adequacy="adequate",
        current_recommended_path="prepared generic AABB index query primitive",
        current_partner_role="no partner needed",
        needs_numba_reference=False,
        numba_reference_reason="the promoted path is prepared primitive-only",
        amd_hiprt_readiness="needs HIPRT AABB query parity",
        next_generic_runtime_action="keep as no-regression prepared-index row; retest on AMD functional pass",
        evidence_refs=("Goal2798", "Goal3601"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="rtnn",
        promoted_reader_view="RTNN-style prepared 3D ranked nearest summary",
        current_performance_reading="adequate: v2.9 packet row is 1.061225x versus v2.3",
        adequacy="adequate",
        current_recommended_path="prepared RTDL/OptiX fixed-radius ranked-summary aggregate with graph replay evidence",
        current_partner_role="no partner on the promoted RTDL path; CuPy grid remains the opponent/reference",
        needs_numba_reference=False,
        numba_reference_reason="current promoted path is a generic prepared primitive/aggregate path",
        amd_hiprt_readiness="needs HIPRT fixed-radius ranked-summary mapping and conformance",
        next_generic_runtime_action="keep as a prepared-input residency reference; use for AMD fixed-radius aggregate parity",
        evidence_refs=("Goal2800", "Goal2822", "Goal3567"),
        pod_needed_next=False,
    ),
    V29BenchmarkAdequacyRow(
        app="triangle_counting",
        promoted_reader_view="triangle-counting generic RT graph summary",
        current_performance_reading="adequate: v2.9 packet row is 1.029580x versus v2.3",
        adequacy="adequate",
        current_recommended_path="generic RT graph summary primitive",
        current_partner_role="no partner needed on the fastest primitive row",
        needs_numba_reference=False,
        numba_reference_reason="the fastest path is primitive-only; Numba alternate is not required for the reference story",
        amd_hiprt_readiness="needs HIPRT graph-summary primitive parity",
        next_generic_runtime_action="keep as primitive-only; use as AMD graph-summary smoke after HIPRT work starts",
        evidence_refs=("Goal2797", "Goal3567"),
        pod_needed_next=False,
    ),
)


def v2_9_benchmark_adequacy_rows() -> tuple[V29BenchmarkAdequacyRow, ...]:
    return V2_9_BENCHMARK_ADEQUACY_ROWS


def v2_9_benchmark_adequacy() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_9_BENCHMARK_ADEQUACY_ROWS)


def summarize_v2_9_benchmark_adequacy(rows: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_9_benchmark_adequacy()
    adequacy_counts = {level: 0 for level in ADEQUACY_LEVELS}
    for row in matrix:
        adequacy_counts[str(row["adequacy"])] += 1
    numba_apps = tuple(row["app"] for row in matrix if row["needs_numba_reference"])
    pod_apps = tuple(row["app"] for row in matrix if row["pod_needed_next"])
    return {
        "version": V2_9_BENCHMARK_ADEQUACY_VERSION,
        "status": V2_9_BENCHMARK_ADEQUACY_STATUS,
        "app_count": len({row["app"] for row in matrix}),
        "row_count": len(matrix),
        "adequacy_counts": adequacy_counts,
        "numba_reference_needed_apps": numba_apps,
        "pod_needed_next_apps": pod_apps,
        "claim_boundary": V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def validate_v2_9_benchmark_adequacy(rows: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_9_benchmark_adequacy()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    expected_apps = set(V2_8_PROMOTED_BENCHMARK_APPS)
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: got={sorted(apps)} expected={sorted(expected_apps)}")
    for row in matrix:
        app = str(row.get("app", "<missing>"))
        if row.get("adequacy") not in ADEQUACY_LEVELS:
            errors.append(f"{app}: invalid adequacy level")
        if not row.get("evidence_refs"):
            errors.append(f"{app}: missing evidence refs")
        for key in (
            "promoted_reader_view",
            "current_performance_reading",
            "current_recommended_path",
            "current_partner_role",
            "numba_reference_reason",
            "amd_hiprt_readiness",
            "next_generic_runtime_action",
        ):
            value = row.get(key)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() == "n/a":
                errors.append(f"{app}: {key} must be explicit")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{app}: {flag} must remain false")
    return {
        "version": V2_9_BENCHMARK_ADEQUACY_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY,
    }
