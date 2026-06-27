from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4702_SPECIALIZED_TIER3_RELIABILITY_PROTOCOL_STATUS = (
    "goal4702_specialized_tier3_reliability_matrix_protocol_frozen_not_run"
)
V4_GOAL4702_NEXT_GOAL = "Goal4703 specialized Tier-3 reliability matrix POD run"


@dataclass(frozen=True)
class V4Goal4702ReliabilityProtocol:
    status: str
    callback_variants: tuple[str, ...]
    attempts_per_variant: int
    total_attempts: int
    datasets: tuple[str, ...]
    compile_link_launch_success_floor: float
    correctness_requirement: str
    cache_requirement: str
    failure_classification_requirement: str
    next_goal: str
    pod_required_for_next_goal: bool = True
    public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False
    arbitrary_callback_authorized: bool = False
    raw_optix_callback_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "callback_variants": self.callback_variants,
            "attempts_per_variant": self.attempts_per_variant,
            "total_attempts": self.total_attempts,
            "datasets": self.datasets,
            "compile_link_launch_success_floor": self.compile_link_launch_success_floor,
            "correctness_requirement": self.correctness_requirement,
            "cache_requirement": self.cache_requirement,
            "failure_classification_requirement": self.failure_classification_requirement,
            "next_goal": self.next_goal,
            "pod_required_for_next_goal": self.pod_required_for_next_goal,
            "public_support_authorized": self.public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
            "arbitrary_callback_authorized": self.arbitrary_callback_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
        }


def v4_goal4702_specialized_tier3_reliability_protocol() -> V4Goal4702ReliabilityProtocol:
    variants = (
        "custom_scalar_reduce_weighted_sum",
        "custom_score_affine",
        "custom_threshold_flag",
        "custom_minmax_score",
    )
    return V4Goal4702ReliabilityProtocol(
        status=V4_GOAL4702_SPECIALIZED_TIER3_RELIABILITY_PROTOCOL_STATUS,
        callback_variants=variants,
        attempts_per_variant=5,
        total_attempts=len(variants) * 5,
        datasets=("dense_hits", "sparse_hits", "no_hit_empty_reduction"),
        compile_link_launch_success_floor=0.95,
        correctness_requirement="100% exact or tolerance-bounded parity for every variant x dataset row",
        cache_requirement=(
            "same callback PTX/toolchain/symbol must reuse the same deterministic cache key; "
            "changed PTX or toolchain fingerprint must produce a different key"
        ),
        failure_classification_requirement=(
            "every failed attempt must carry a Goal4698 stage-specific error code before the result can be reviewed"
        ),
        next_goal=V4_GOAL4702_NEXT_GOAL,
    )


def validate_v4_goal4702_specialized_tier3_reliability_protocol() -> dict[str, object]:
    protocol = v4_goal4702_specialized_tier3_reliability_protocol()
    payload = protocol.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4702_SPECIALIZED_TIER3_RELIABILITY_PROTOCOL_STATUS:
        missing.append("status")
    if len(payload["callback_variants"]) < 4:
        missing.append("callback_variants")
    if int(payload["total_attempts"]) < 20:
        missing.append("total_attempts")
    if int(payload["attempts_per_variant"]) * len(payload["callback_variants"]) != int(payload["total_attempts"]):
        missing.append("attempt_count_consistency")
    for dataset in ("dense_hits", "sparse_hits", "no_hit_empty_reduction"):
        if dataset not in payload["datasets"]:
            missing.append(dataset)
    if float(payload["compile_link_launch_success_floor"]) < 0.95:
        missing.append("success_floor")
    if "100%" not in str(payload["correctness_requirement"]):
        missing.append("correctness_requirement")
    if "same deterministic cache key" not in str(payload["cache_requirement"]):
        missing.append("cache_requirement")
    if "stage-specific error code" not in str(payload["failure_classification_requirement"]):
        missing.append("failure_classification")
    for key in (
        "public_support_authorized",
        "release_authorized",
        "performance_claim_authorized",
        "arbitrary_callback_authorized",
        "raw_optix_callback_authorized",
    ):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "protocol": payload,
    }


__all__ = [
    "V4_GOAL4702_SPECIALIZED_TIER3_RELIABILITY_PROTOCOL_STATUS",
    "V4_GOAL4702_NEXT_GOAL",
    "V4Goal4702ReliabilityProtocol",
    "v4_goal4702_specialized_tier3_reliability_protocol",
    "validate_v4_goal4702_specialized_tier3_reliability_protocol",
]
