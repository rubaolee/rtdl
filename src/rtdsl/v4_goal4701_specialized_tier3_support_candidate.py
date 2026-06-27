from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4701_SPECIALIZED_TIER3_SUPPORT_CANDIDATE_STATUS = (
    "goal4701_specialized_tier3_support_candidate_packet_not_public_support"
)
V4_GOAL4701_CANDIDATE_LABEL = "specialized_numba_scalar_callback_support_candidate"
V4_GOAL4701_NEXT_GOAL = "Goal4702 specialized Tier-3 reliability matrix protocol"


@dataclass(frozen=True)
class V4Goal4701SupportCandidate:
    status: str
    candidate_label: str
    candidate_scope: str
    evidence_chain: tuple[str, ...]
    satisfied_gates: tuple[str, ...]
    missing_before_public_support: tuple[str, ...]
    next_goal: str
    public_support_authorized: bool = False
    release_authorized: bool = False
    broad_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    arbitrary_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "candidate_label": self.candidate_label,
            "candidate_scope": self.candidate_scope,
            "evidence_chain": self.evidence_chain,
            "satisfied_gates": self.satisfied_gates,
            "missing_before_public_support": self.missing_before_public_support,
            "next_goal": self.next_goal,
            "public_support_authorized": self.public_support_authorized,
            "release_authorized": self.release_authorized,
            "broad_speedup_claim_authorized": self.broad_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
        }


def v4_goal4701_specialized_tier3_support_candidate() -> V4Goal4701SupportCandidate:
    return V4Goal4701SupportCandidate(
        status=V4_GOAL4701_SPECIALIZED_TIER3_SUPPORT_CANDIDATE_STATUS,
        candidate_label=V4_GOAL4701_CANDIDATE_LABEL,
        candidate_scope=(
            "module-specialized Numba C-ABI scalar device callback called as a "
            "direct device function from an RTDL-generated OptiX hit-program route"
        ),
        evidence_chain=(
            "Goal4689 minimal launch correctness for scalar callback",
            "Goal4691 SBT direct-callable overhead measured yellow at 1.6705538933080346x",
            "Goal4692 pivot away from SBT direct-callable support",
            "Goal4693 specialized hit-program callback correctness",
            "Goal4695 specialized hit-program callback overhead passed at 1.0355240926982583x",
            "Goal4696 productization decision for constrained specialized candidate",
            "Goal4697 API contract and negative validation scaffold",
            "Goal4698 compile/cache/error-reporting scaffold",
            "Goal4699 app-route validation protocol frozen",
            "Goal4700 weighted-sum app-route POD gate passed against Tier-2 denominator",
        ),
        satisfied_gates=(
            "single scalar callback PTX generation",
            "OptiX module composition and launch correctness",
            "specialized hit-program overhead under 1.50x focused gate",
            "one weighted-sum app-route parity/performance gate passed",
            "fail-closed rejection for arbitrary Python/action/external-memory/dynamic-SBT shapes",
            "public support flags remain false",
        ),
        missing_before_public_support=(
            "external 3-AI review of Goals4696-4700",
            "20 compile/link/launch attempts across at least 4 accepted scalar callback variants",
            "dense/sparse/no-hit correctness datasets for the candidate route",
            "cache reuse and error-reporting behavior tested under repeated compiles",
            "user-facing docs wording reviewed and bounded",
            "final release/support authorization gate",
        ),
        next_goal=V4_GOAL4701_NEXT_GOAL,
    )


def validate_v4_goal4701_specialized_tier3_support_candidate() -> dict[str, object]:
    candidate = v4_goal4701_specialized_tier3_support_candidate()
    payload = candidate.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4701_SPECIALIZED_TIER3_SUPPORT_CANDIDATE_STATUS:
        missing.append("status")
    if payload["candidate_label"] != V4_GOAL4701_CANDIDATE_LABEL:
        missing.append("candidate_label")
    if len(payload["evidence_chain"]) < 8:
        missing.append("evidence_chain")
    required_missing = tuple(payload["missing_before_public_support"])
    for required in (
        "external 3-AI review of Goals4696-4700",
        "20 compile/link/launch attempts across at least 4 accepted scalar callback variants",
        "final release/support authorization gate",
    ):
        if required not in required_missing:
            missing.append(required)
    for key in (
        "public_support_authorized",
        "release_authorized",
        "broad_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "raw_optix_callback_authorized",
        "arbitrary_callback_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "candidate": payload,
    }


__all__ = [
    "V4_GOAL4701_SPECIALIZED_TIER3_SUPPORT_CANDIDATE_STATUS",
    "V4_GOAL4701_CANDIDATE_LABEL",
    "V4_GOAL4701_NEXT_GOAL",
    "V4Goal4701SupportCandidate",
    "v4_goal4701_specialized_tier3_support_candidate",
    "validate_v4_goal4701_specialized_tier3_support_candidate",
]
