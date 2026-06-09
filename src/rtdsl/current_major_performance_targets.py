from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION = "rtdl.v2_10.current_major_performance_targets.goal4261.v1"
CURRENT_MAJOR_PERFORMANCE_TARGET_STATUS = "internal_direction_map_not_release_authorization"
CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY = (
    "Goal4249 summarizes the major performance direction after Goal4215, "
    "Goal4218, Goal4222, Goal4223, Goal4230, Goal4235, Goal4239, Goal4243, "
    "the Goal4248 public-doc claim-boundary scan, and the Goal4254/4258 "
    "public-claim wording repair closure. It is a route/runtime planning map, not "
    "a release packet, not "
    "a public speedup claim, not a whole-app acceleration claim, not a broad "
    "RT-core claim, not a paper-reproduction claim, not a true-zero-copy claim, "
    "not automatic partner selection, not AMD performance evidence, and not "
    "permission for app-specific native-engine logic."
)


TARGET_STATUSES = (
    "done_internal_evidence",
    "available_explicit_not_default",
    "needs_broader_evidence",
    "blocked_pending_hardware",
    "pending_user_release_decision",
)


@dataclass(frozen=True)
class CurrentMajorPerformanceTarget:
    target_id: str
    theme: str
    status: str
    current_reading: str
    next_action: str
    evidence_refs: tuple[str, ...]
    pod_needed_next: bool
    amd_hardware_needed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    rtdl_beats_rayjoin_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.target_id or not self.theme:
            raise ValueError("major performance target id/theme must be explicit")
        if self.status not in TARGET_STATUSES:
            raise ValueError(f"{self.target_id}: unsupported status")
        if not self.current_reading or not self.next_action:
            raise ValueError(f"{self.target_id}: current reading and next action are required")
        if not self.evidence_refs:
            raise ValueError(f"{self.target_id}: evidence refs must not be empty")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.target_id}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION,
            "status": CURRENT_MAJOR_PERFORMANCE_TARGET_STATUS,
            "target_id": self.target_id,
            "theme": self.theme,
            "target_status": self.status,
            "current_reading": self.current_reading,
            "next_action": self.next_action,
            "evidence_refs": self.evidence_refs,
            "pod_needed_next": self.pod_needed_next,
            "amd_hardware_needed": self.amd_hardware_needed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "rtdl_beats_rayjoin_claim_authorized": self.rtdl_beats_rayjoin_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
            "claim_boundary": CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY,
        }


CURRENT_MAJOR_PERFORMANCE_TARGETS: tuple[CurrentMajorPerformanceTarget, ...] = (
    CurrentMajorPerformanceTarget(
        target_id="ten_app_current_route_health",
        theme="broad current-route execution evidence",
        status="done_internal_evidence",
        current_reading=(
            "Goal4235 proves all ten current benchmark front doors pass on RTX 4000 Ada "
            "at clean source commit 72690687 after measurement closure and external review."
        ),
        next_action=(
            "Use Goal4235 as the current internal health packet; do not treat it as a final "
            "release/performance table without a separate release packet and consensus."
        ),
        evidence_refs=("Goal4215", "Goal4216", "Goal4217", "Goal4225", "Goal4235"),
        pod_needed_next=False,
    ),
    CurrentMajorPerformanceTarget(
        target_id="ten_app_measurement_adequacy_closure",
        theme="second-level timing evidence for all promoted benchmark apps",
        status="done_internal_evidence",
        current_reading=(
            "Goal4230 reconciles Goal4185/4186/4189/4225/4228/4229 and shows every "
            "promoted benchmark app has at least one second-level measurement source "
            "above the one-second hot-path or representative-profile floor. Goal4243 "
            "refreshes the Hausdorff, contact-manifold, and triangle-counting short rows "
            "with current-head dedicated long-repeat evidence."
        ),
        next_action=(
            "Use this as internal measurement-readiness evidence only. A public release "
            "still needs exact claim wording, docs audit, and multi-AI release consensus."
        ),
        evidence_refs=("Goal4185", "Goal4186", "Goal4189", "Goal4225", "Goal4228", "Goal4229", "Goal4230", "Goal4243"),
        pod_needed_next=False,
    ),
    CurrentMajorPerformanceTarget(
        target_id="rayjoin_contract_split_route_policy",
        theme="explicit mixed-route policy for RayJoin-style contracts",
        status="done_internal_evidence",
        current_reading=(
            "Goal4218 confirms the route split, Goal4223 broadens it across "
            "seven public-CDB contract/scale rows, and Goal4239 reruns the "
            "representative mixed route as a 20.76s dedicated long-repeat profile: "
            "bounded PIP one-shot favors Numba, while repeated PIP, LSI, and overlay "
            "active-count contracts favor prepared RTDL/OptiX primitives."
        ),
        next_action=(
            "Use the split as internal route-policy evidence only. Future work should "
            "improve generic primitives or run a formal release packet; do not collapse "
            "the contracts into one RayJoin paper-reproduction number."
        ),
        evidence_refs=("Goal4218", "Goal4220", "Goal4221", "Goal4223", "Goal4239"),
        pod_needed_next=False,
    ),
    CurrentMajorPerformanceTarget(
        target_id="rtdbscan_profile_aware_boundary_policy",
        theme="profile-aware fixed-radius component route policy",
        status="done_internal_evidence",
        current_reading=(
            "Goals4205-4212 prove canonical policy parity, while Goal4222 shows "
            "the unblocked single-pass grouped stream beats the blocked grouped "
            "variant on clustered3d, road3d, and ngsim_dense at 65k and 262k."
        ),
        next_action=(
            "Keep unblocked single-pass as the current default route shape, and keep "
            "blocked grouped stream explicit/profile-specific unless future evidence "
            "shows a shape where it wins."
        ),
        evidence_refs=("Goal4205", "Goal4206", "Goal4212", "Goal4222"),
        pod_needed_next=False,
    ),
    CurrentMajorPerformanceTarget(
        target_id="prepared_session_residency_surface",
        theme="prepare-once/query-many runtime ergonomics",
        status="available_explicit_not_default",
        current_reading=(
            "Prepared-session cache keys, timing records, explicit invalidation, and "
            "get_or_prepare_explicit_session already exist; Goal4215 again shows high "
            "prepare-to-hot-query ratios on scene-heavy rows."
        ),
        next_action=(
            "Keep reuse explicit and user-owned. Future work may improve front-door ergonomics, "
            "but must not enable hidden global caching or automatic backend/partner selection."
        ),
        evidence_refs=("Goal3872", "Goal3877", "Goal3884", "Goal4215"),
        pod_needed_next=False,
    ),
    CurrentMajorPerformanceTarget(
        target_id="release_grade_long_run_packet",
        theme="release-grade long-run and cross-profile evidence",
        status="needs_broader_evidence",
        current_reading=(
            "Goal4230 closes the basic ten-app measurement-adequacy floor on RTX 4000 Ada, "
            "Goal4235 proves the current clean head still runs all ten front doors, "
            "Goal4239 adds a dedicated RayJoin long-repeat profile, and Goal4243 "
            "refreshes the former short current-head rows with dedicated long-repeat "
            "evidence. Goal4248 scans the current public learner/user docs and leaves "
            "zero hard claim-boundary blockers. Goal4254 drafts exact public claim "
            "wording, and Goal4258 closes the Goal4255 repair items with focused "
            "Claude/Gemini acceptance. This is still not a formal public release "
            "matrix across consensus, final release commit validation, and hardware classes."
        ),
        next_action=(
            "Before any formal major release, assemble an explicit release packet with "
            "exact artifact provenance and fresh multi-AI consensus over the final packet; "
            "rerun a final pod validation at the exact release commit, and run additional "
            "long timing only if the release claim requires a public performance table."
        ),
        evidence_refs=(
            "Goal4215",
            "Goal4222",
            "Goal4223",
            "Goal4230",
            "Goal4235",
            "Goal4239",
            "Goal4243",
            "Goal4248",
            "Goal4254",
            "Goal4258",
            "Goal4259",
            "Goal4260",
        ),
        pod_needed_next=True,
    ),
    CurrentMajorPerformanceTarget(
        target_id="amd_hiprt_functional_parity",
        theme="multi-hardware RT backend validation",
        status="blocked_pending_hardware",
        current_reading=(
            "NVIDIA/OptiX current routes are healthy, but AMD/HIPRT functional and timing "
            "evidence still requires actual AMD GPU hardware."
        ),
        next_action=(
            "When an AMD pod is available, run HIPRT functional parity first, then only make "
            "performance claims after same-contract AMD evidence exists."
        ),
        evidence_refs=("Goal3784", "Goal3785", "Goal4215"),
        pod_needed_next=True,
        amd_hardware_needed=True,
    ),
    CurrentMajorPerformanceTarget(
        target_id="major_release_candidate_packet",
        theme="release gating and multi-AI consensus",
        status="pending_user_release_decision",
        current_reading=(
            "The project has current NVIDIA internal evidence and strict claim boundaries, "
            "and Goal4248 confirms the current public docs scan has zero hard claim-boundary "
            "blockers. Goal4257 drafts the release-candidate packet and Goal4258/4259/4260 "
            "close the public claim-wording repair loop, but this map does not authorize a release."
        ),
        next_action=(
            "A formal major release needs explicit user release decision, final pod validation "
            "at the release commit, and the required multi-AI consensus over the exact release packet."
        ),
        evidence_refs=(
            "Goal4215",
            "Goal4216",
            "Goal4217",
            "Goal4218",
            "Goal4235",
            "Goal4248",
            "Goal4251",
            "Goal4254",
            "Goal4257",
            "Goal4258",
            "Goal4259",
            "Goal4260",
        ),
        pod_needed_next=False,
    ),
)


def current_major_performance_targets() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in CURRENT_MAJOR_PERFORMANCE_TARGETS)


def summarize_current_major_performance_targets(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_major_performance_targets()
    return {
        "version": CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION,
        "status": CURRENT_MAJOR_PERFORMANCE_TARGET_STATUS,
        "target_count": len(matrix),
        "done_internal_evidence_count": sum(
            1 for row in matrix if row["target_status"] == "done_internal_evidence"
        ),
        "needs_broader_evidence_count": sum(
            1 for row in matrix if row["target_status"] == "needs_broader_evidence"
        ),
        "blocked_pending_hardware_count": sum(
            1 for row in matrix if row["target_status"] == "blocked_pending_hardware"
        ),
        "pod_needed_next_targets": tuple(
            row["target_id"] for row in matrix if row["pod_needed_next"]
        ),
        "amd_hardware_needed_targets": tuple(
            row["target_id"] for row in matrix if row["amd_hardware_needed"]
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
        "claim_boundary": CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY,
    }


def validate_current_major_performance_targets(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else current_major_performance_targets()
    errors: list[str] = []
    ids = [row.get("target_id") for row in matrix]
    if len(ids) != len(set(ids)):
        errors.append("major performance target ids must be unique")
    if len(matrix) < 5:
        errors.append("major performance target map must cover evidence, route, hardware, and release targets")
    statuses = {row.get("target_status") for row in matrix}
    for required in (
        "done_internal_evidence",
        "available_explicit_not_default",
        "needs_broader_evidence",
        "blocked_pending_hardware",
        "pending_user_release_decision",
    ):
        if required not in statuses:
            errors.append(f"missing target status: {required}")
    for row in matrix:
        if row.get("target_status") not in TARGET_STATUSES:
            errors.append(f"{row.get('target_id')}: unsupported status")
        if not row.get("evidence_refs"):
            errors.append(f"{row.get('target_id')}: missing evidence refs")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{row.get('target_id')}: {flag} must remain false")
    return {
        "version": CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "target_count": len(matrix),
        "claim_boundary": CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY,
    }


__all__ = [
    "CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY",
    "CURRENT_MAJOR_PERFORMANCE_TARGET_STATUS",
    "CURRENT_MAJOR_PERFORMANCE_TARGET_VERSION",
    "CURRENT_MAJOR_PERFORMANCE_TARGETS",
    "CurrentMajorPerformanceTarget",
    "current_major_performance_targets",
    "summarize_current_major_performance_targets",
    "validate_current_major_performance_targets",
]
