from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class RtnnBaselineDecisionId(Enum):
    KEEP_POSTGIS_SCIPY_BOUNDED = "goal266_keep_postgis_scipy_bounded"
    EXTEND_SCIPY_AFTER_3D_TRUTH = "goal266_extend_scipy_after_3d_truth"
    PRIORITIZE_RADIUS_LIBRARIES_FIRST = "goal266_prioritize_radius_libraries_first"
    TREAT_PCL_AS_HIGH_FRICTION = "goal266_treat_pcl_as_high_friction"
    REQUIRE_PACKAGED_BUILDS_FOR_NATIVE_SET = "goal266_require_packaged_builds_for_native_set"


@dataclass(frozen=True)
class RtnnBaselineLibrary:
    handle: str
    paper_label: str
    target_dimension: str
    workload_shape: str
    adapter_kind: str
    integration_boundary: str
    current_status: str
    notes: str


@dataclass(frozen=True)
class RtnnBaselineDecision:
    decision_id: RtnnBaselineDecisionId
    library_handle: str
    verdict: str
    reason: str
    next_step: str


RTNN_BASELINE_LIBRARIES: tuple[RtnnBaselineLibrary, ...] = (
    RtnnBaselineLibrary(
        handle="cunsearch",
        paper_label="cuNSearch",
        target_dimension="3d",
        workload_shape="fixed_radius_neighbors",
        adapter_kind="native_or_cli_wrapper",
        integration_boundary="optional external comparison baseline on Linux with CUDA-capable GPU",
        current_status="planned",
        notes="Candidate fixed-radius GPU comparison library from the RTNN comparison set.",
    ),
    RtnnBaselineLibrary(
        handle="frnn",
        paper_label="FRNN",
        target_dimension="3d",
        workload_shape="fixed_radius_neighbors",
        adapter_kind="python_or_native_wrapper",
        integration_boundary="optional external comparison baseline with explicit version pinning",
        current_status="planned",
        notes="Radius-neighbor library that should remain a comparison path rather than contract authority.",
    ),
    RtnnBaselineLibrary(
        handle="pcl_octree",
        paper_label="PCLOctree",
        target_dimension="3d",
        workload_shape="fixed_radius_neighbors|bounded_knn_rows",
        adapter_kind="native_binary_wrapper",
        integration_boundary="optional external comparison baseline through a bounded command or library wrapper",
        current_status="planned",
        notes="Likely highest-friction dependency because it pulls in a larger native stack.",
    ),
    RtnnBaselineLibrary(
        handle="fastrnn",
        paper_label="FastRNN",
        target_dimension="3d",
        workload_shape="fixed_radius_neighbors|bounded_knn_rows",
        adapter_kind="native_binary_wrapper",
        integration_boundary="optional external comparison baseline only after reproducible build instructions exist",
        current_status="planned",
        notes="Needs explicit packaging and version-lock decisions before any parity claims.",
    ),
    RtnnBaselineLibrary(
        handle="scipy_ckdtree",
        paper_label="SciPy cKDTree",
        target_dimension="2d|3d",
        workload_shape="fixed_radius_neighbors|knn_rows|bounded_knn_rows",
        adapter_kind="python_direct",
        integration_boundary="already-usable bounded external baseline for local development loops",
        current_status="online_2d_only",
        notes="Current repo already uses SciPy for 2D external checks; 3D extension belongs to a later bounded goal.",
    ),
    RtnnBaselineLibrary(
        handle="postgis",
        paper_label="PostGIS",
        target_dimension="2d",
        workload_shape="fixed_radius_neighbors|knn_rows",
        adapter_kind="sql_direct",
        integration_boundary="indexed external comparison baseline for the released 2D line only",
        current_status="online_2d_only",
        notes="Useful external credibility baseline, but not part of the RTNN paper comparison set.",
    ),
)


RTNN_BASELINE_DECISIONS: tuple[RtnnBaselineDecision, ...] = (
    RtnnBaselineDecision(
        decision_id=RtnnBaselineDecisionId.KEEP_POSTGIS_SCIPY_BOUNDED,
        library_handle="postgis",
        verdict="keep_as_existing_nonpaper_baseline",
        reason="PostGIS remains useful for released 2D credibility checks but should not be reframed as a paper-set baseline.",
        next_step="Keep it out of the RTNN exact-reproduction path.",
    ),
    RtnnBaselineDecision(
        decision_id=RtnnBaselineDecisionId.EXTEND_SCIPY_AFTER_3D_TRUTH,
        library_handle="scipy_ckdtree",
        verdict="extend_later",
        reason="SciPy is already online for 2D and can become a cheap 3D bounded baseline after the 3D truth path is broader.",
        next_step="Add explicit 3D SciPy parity only after 3D CPU/oracle closure exists.",
    ),
    RtnnBaselineDecision(
        decision_id=RtnnBaselineDecisionId.PRIORITIZE_RADIUS_LIBRARIES_FIRST,
        library_handle="cunsearch",
        verdict="prioritize_first_adapter",
        reason="Radius-neighbor libraries are the closest external comparison fit for the fixed-radius RTNN line.",
        next_step="Evaluate packaging friction and wrapper shape on Linux before coding the first adapter.",
    ),
    RtnnBaselineDecision(
        decision_id=RtnnBaselineDecisionId.TREAT_PCL_AS_HIGH_FRICTION,
        library_handle="pcl_octree",
        verdict="defer_until_packaging_plan",
        reason="PCLOctree likely has the heaviest dependency stack and should not block earlier bounded reproduction work.",
        next_step="Write an acquisition/build note before any adapter code.",
    ),
    RtnnBaselineDecision(
        decision_id=RtnnBaselineDecisionId.REQUIRE_PACKAGED_BUILDS_FOR_NATIVE_SET,
        library_handle="fastrnn",
        verdict="defer_until_reproducible_build",
        reason="Native comparison libraries should not be called online until version pinning and repeatable build steps are documented.",
        next_step="Fold build/package expectations into the first adapter-harness goal.",
    ),
)


def rtnn_baseline_libraries(*, handle: Optional[str] = None, current_status: Optional[str] = None) -> tuple[RtnnBaselineLibrary, ...]:
    libraries = RTNN_BASELINE_LIBRARIES
    if handle is not None:
        libraries = tuple(library for library in libraries if library.handle == handle)
    if current_status is not None:
        libraries = tuple(library for library in libraries if library.current_status == current_status)
    return libraries


def rtnn_baseline_decisions(
    *,
    library_handle: Optional[str] = None,
    verdict: Optional[str] = None,
    decision_id: Optional[RtnnBaselineDecisionId] = None,
) -> tuple[RtnnBaselineDecision, ...]:
    decisions = RTNN_BASELINE_DECISIONS
    if library_handle is not None:
        decisions = tuple(decision for decision in decisions if decision.library_handle == library_handle)
    if verdict is not None:
        decisions = tuple(decision for decision in decisions if decision.verdict == verdict)
    if decision_id is not None:
        decisions = tuple(decision for decision in decisions if decision.decision_id == decision_id)
    return decisions
