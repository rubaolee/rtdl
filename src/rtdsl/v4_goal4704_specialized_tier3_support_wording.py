from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4704_SPECIALIZED_TIER3_SUPPORT_WORDING_STATUS = (
    "goal4704_specialized_tier3_support_candidate_wording_gate_not_public_support"
)
V4_GOAL4704_CANDIDATE_LABEL = "specialized_numba_scalar_callback_support_candidate"
V4_GOAL4704_NEXT_GOAL = "Goal4705 source-level PTX canonicalization and repeated compile cache-stability gate"


@dataclass(frozen=True)
class V4Goal4704SupportWordingGate:
    status: str
    candidate_label: str
    allowed_internal_wording: tuple[str, ...]
    prohibited_public_wording: tuple[str, ...]
    evidence_chain: tuple[str, ...]
    remaining_public_support_gates: tuple[str, ...]
    next_goal: str
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    app_level_speed_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "candidate_label": self.candidate_label,
            "allowed_internal_wording": self.allowed_internal_wording,
            "prohibited_public_wording": self.prohibited_public_wording,
            "evidence_chain": self.evidence_chain,
            "remaining_public_support_gates": self.remaining_public_support_gates,
            "next_goal": self.next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "app_level_speed_claim_authorized": self.app_level_speed_claim_authorized,
        }


def v4_goal4704_specialized_tier3_support_wording_gate() -> V4Goal4704SupportWordingGate:
    return V4Goal4704SupportWordingGate(
        status=V4_GOAL4704_SPECIALIZED_TIER3_SUPPORT_WORDING_STATUS,
        candidate_label=V4_GOAL4704_CANDIDATE_LABEL,
        allowed_internal_wording=(
            "specialized Tier-3 support candidate",
            "module-specialized Numba C-ABI scalar callback route",
            "passed one app-route gate and one 20-attempt reliability matrix",
            "not public support and not release wording",
        ),
        prohibited_public_wording=(
            "V4 supports arbitrary callbacks",
            "V4 supports raw OptiX callbacks",
            "Tier-3 callbacks are public API",
            "custom callback path is a V4 performance win",
            "callback support is release-ready",
            "app-level high-performance V4 is proven by Tier-3",
        ),
        evidence_chain=(
            "Goal4696 productization decision",
            "Goal4697 API contract scaffold",
            "Goal4698 compile/cache/error-reporting scaffold",
            "Goal4699 app-route validation protocol",
            "Goal4700 POD app-route pass",
            "Goal4701 support-candidate packet",
            "Goal4702 reliability matrix protocol",
            "Goal4703 POD reliability matrix pass",
        ),
        remaining_public_support_gates=(
            "external 3-AI review of Goals4696-4703",
            "source-level PTX canonicalization or explicit artifact-level cache documentation",
            "negative user-facing validation for rejected callback shapes",
            "bounded user docs with examples that compile in a clean environment",
            "final support authorization separate from V4 release authorization",
        ),
        next_goal=V4_GOAL4704_NEXT_GOAL,
    )


def validate_v4_goal4704_specialized_tier3_support_wording() -> dict[str, object]:
    gate = v4_goal4704_specialized_tier3_support_wording_gate()
    payload = gate.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4704_SPECIALIZED_TIER3_SUPPORT_WORDING_STATUS:
        missing.append("status")
    if "support_candidate" not in str(payload["candidate_label"]):
        missing.append("candidate_label")
    if "not public support and not release wording" not in payload["allowed_internal_wording"]:
        missing.append("allowed_boundary_wording")
    for phrase in ("V4 supports arbitrary callbacks", "Tier-3 callbacks are public API"):
        if phrase not in payload["prohibited_public_wording"]:
            missing.append(f"prohibited_{phrase}")
    for goal in ("Goal4696", "Goal4700", "Goal4703"):
        if not any(str(item).startswith(goal) for item in payload["evidence_chain"]):
            missing.append(goal)
    for gate_name in ("external 3-AI review", "source-level PTX canonicalization", "bounded user docs"):
        if not any(gate_name in str(item) for item in payload["remaining_public_support_gates"]):
            missing.append(gate_name)
    for key in (
        "tier3_public_support_authorized",
        "release_authorized",
        "performance_claim_authorized",
        "arbitrary_callback_authorized",
        "raw_optix_callback_authorized",
        "app_level_speed_claim_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "gate": payload,
    }


__all__ = [
    "V4_GOAL4704_SPECIALIZED_TIER3_SUPPORT_WORDING_STATUS",
    "V4_GOAL4704_CANDIDATE_LABEL",
    "V4_GOAL4704_NEXT_GOAL",
    "V4Goal4704SupportWordingGate",
    "v4_goal4704_specialized_tier3_support_wording_gate",
    "validate_v4_goal4704_specialized_tier3_support_wording",
]
