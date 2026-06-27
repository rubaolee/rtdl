from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4684_TARGET_RESET_STATUS = (
    "goal4684_no_clean_existing_tier2_app_target_select_tier3_wrapper_spike_protocol"
)
V4_GOAL4684_SELECTED_NEXT_TRACK = "TIER3_WRAPPER_DIRECT_CALLABLE_ABI_SPIKE"
V4_GOAL4684_NEXT_GOAL = "Goal4685 tier3 wrapper/direct-callable ABI protocol gate"


@dataclass(frozen=True)
class V4Goal4684CandidateDisposition:
    target: str
    disposition: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "target": self.target,
            "disposition": self.disposition,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class V4Goal4684HighPerformanceTargetReset:
    status: str
    decision: str
    selected_next_track: str
    candidate_dispositions: tuple[V4Goal4684CandidateDisposition, ...]
    next_goal: str
    formal_high_performance_release_authorized: bool = False
    pod_authorized: bool = False
    implementation_authorized: bool = False
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "decision": self.decision,
            "selected_next_track": self.selected_next_track,
            "candidate_dispositions": tuple(row.as_dict() for row in self.candidate_dispositions),
            "next_goal": self.next_goal,
            "formal_high_performance_release_authorized": self.formal_high_performance_release_authorized,
            "pod_authorized": self.pod_authorized,
            "implementation_authorized": self.implementation_authorized,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_kernel_authorized": self.app_identity_kernel_authorized,
        }


def v4_goal4684_high_performance_target_reset() -> V4Goal4684HighPerformanceTargetReset:
    dispositions = (
        V4Goal4684CandidateDisposition(
            target="existing benchmark app route selection",
            disposition="no_clean_target",
            reason=(
                "Goal4672 found V2.14 already had a primitive or explicit mixed "
                "partner route for every promoted benchmark app."
            ),
        ),
        V4Goal4684CandidateDisposition(
            target="RTDBSCAN fixed-radius/grouped-union",
            disposition="no_go",
            reason=(
                "Goals4670/4671 found only modest gains; the best true grouped-union "
                "probe stayed below the 1.20x second-win bar and V2.14 already had the core route."
            ),
        ),
        V4Goal4684CandidateDisposition(
            target="ranked fixed-radius summary / RTNN",
            disposition="deferred",
            reason="Goal4678 deferred the candidate after serious-scale parity or below-parity evidence.",
        ),
        V4Goal4684CandidateDisposition(
            target="shape-pair relation active count",
            disposition="no_promotion",
            reason="Goal4681 passed correctness but failed speed bars: V4/V2.14 hot 0.963x and wall 0.605x.",
        ),
        V4Goal4684CandidateDisposition(
            target="contact/witness device columns",
            disposition="no_go",
            reason=(
                "Goal4683 found the target reuses V2.14 bounded collect-k and current "
                "exact-witness partner-column plumbing."
            ),
        ),
        V4Goal4684CandidateDisposition(
            target="aggregate-frontier device columns",
            disposition="measured_productization_win_not_second_v4_over_v3_win",
            reason=(
                "Goal4676 removed a V2.14 host-frontier bottleneck but was parity "
                "with V3.0.2 hot path at 0.998x."
            ),
        ),
        V4Goal4684CandidateDisposition(
            target="Tier-3 wrapper/direct-callable ABI",
            disposition="selected_as_spike_only_next_track",
            reason=(
                "It is the remaining V4 design path that is genuinely absent from V2.14, "
                "app-name-free, and directly addresses custom scalar callback logic. It is "
                "not a release feature unless the full protocol later passes."
            ),
        ),
    )
    return V4Goal4684HighPerformanceTargetReset(
        status=V4_GOAL4684_TARGET_RESET_STATUS,
        decision=(
            "No clean existing Tier-2/app target remains for a near-term formal "
            "high-performance V4 release. Continue only by testing a genuinely new "
            "V4 architecture lever: the Tier-3 wrapper/direct-callable ABI spike. "
            "If that spike fails its protocol, the honest current V4 outcome stays "
            "bounded-operator/productization rather than formal high-performance release."
        ),
        selected_next_track=V4_GOAL4684_SELECTED_NEXT_TRACK,
        candidate_dispositions=dispositions,
        next_goal=(
            "Goal4685 must create a protocol/local gate for a real OptiX traversal "
            "shell or direct-callable ABI composition of Numba PTX. It must not "
            "repeat the old bare-PTX optixModuleCreate probe."
        ),
    )


def validate_v4_goal4684_high_performance_target_reset() -> dict[str, object]:
    reset = v4_goal4684_high_performance_target_reset()
    payload = reset.as_dict()
    dispositions = payload["candidate_dispositions"]
    reasons = " ".join(str(row) for row in dispositions)
    missing: list[str] = []
    if payload["status"] != V4_GOAL4684_TARGET_RESET_STATUS:
        missing.append("status")
    if payload["selected_next_track"] != V4_GOAL4684_SELECTED_NEXT_TRACK:
        missing.append("selected_next_track")
    if "V2.14 already had" not in reasons:
        missing.append("v2_14_preexisting_denominator")
    if "Goal4683" not in reasons:
        missing.append("goal4683_contact_no_go")
    if "Tier-3" not in reasons:
        missing.append("tier3_selected_disposition")
    if "bare-PTX optixModuleCreate probe" not in str(payload["next_goal"]):
        missing.append("no_repeat_bare_ptx_probe")
    for key in (
        "formal_high_performance_release_authorized",
        "pod_authorized",
        "implementation_authorized",
        "tier3_public_support_authorized",
        "raw_optix_callback_authorized",
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_identity_kernel_authorized",
    ):
        if payload.get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "reset": payload,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4684_TARGET_RESET_STATUS",
    "V4_GOAL4684_SELECTED_NEXT_TRACK",
    "V4_GOAL4684_NEXT_GOAL",
    "V4Goal4684CandidateDisposition",
    "V4Goal4684HighPerformanceTargetReset",
    "v4_goal4684_high_performance_target_reset",
    "validate_v4_goal4684_high_performance_target_reset",
]
