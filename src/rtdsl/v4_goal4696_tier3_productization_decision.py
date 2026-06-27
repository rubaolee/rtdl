from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4696_TIER3_PRODUCTIZATION_DECISION_STATUS = (
    "goal4696_productize_constrained_specialized_tier3_candidate_not_public_support"
)
V4_GOAL4696_NEXT_GOAL = "Goal4697 constrained specialized Tier-3 API contract scaffold"


@dataclass(frozen=True)
class V4Goal4696Tier3ProductizationDecision:
    status: str
    decision: str
    productization_candidate: str
    supported_callback_shape: str
    rejected_callback_shapes: tuple[str, ...]
    required_before_public_support: tuple[str, ...]
    next_goal: str
    sbt_direct_callable_status: str = "experimental_yellow_not_public_support"
    tier3_public_support_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "decision": self.decision,
            "productization_candidate": self.productization_candidate,
            "supported_callback_shape": self.supported_callback_shape,
            "rejected_callback_shapes": self.rejected_callback_shapes,
            "required_before_public_support": self.required_before_public_support,
            "next_goal": self.next_goal,
            "sbt_direct_callable_status": self.sbt_direct_callable_status,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4696_tier3_productization_decision() -> V4Goal4696Tier3ProductizationDecision:
    return V4Goal4696Tier3ProductizationDecision(
        status=V4_GOAL4696_TIER3_PRODUCTIZATION_DECISION_STATUS,
        decision=(
            "productize a constrained candidate surface for module-specialized "
            "Numba scalar callbacks, but do not authorize public Tier-3 support"
        ),
        productization_candidate="module_specialized_direct_device_callback",
        supported_callback_shape="pure_scalar_return_numba_cabi_device_function",
        rejected_callback_shapes=(
            "arbitrary_python_callback",
            "action_or_side_effect_callback",
            "external_memory_mutation_callback",
            "dynamic_sbt_direct_callable_hot_path",
        ),
        required_before_public_support=(
            "stable API contract",
            "negative validation for rejected callback shapes",
            "compile/cache/error-reporting behavior",
            "at least one app-route validation using the specialized callback path",
            "external 3-AI review",
        ),
        next_goal=V4_GOAL4696_NEXT_GOAL,
    )


def validate_v4_goal4696_tier3_productization_decision() -> dict[str, object]:
    decision = v4_goal4696_tier3_productization_decision()
    payload = decision.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4696_TIER3_PRODUCTIZATION_DECISION_STATUS:
        missing.append("status")
    if payload["productization_candidate"] != "module_specialized_direct_device_callback":
        missing.append("candidate")
    if payload["supported_callback_shape"] != "pure_scalar_return_numba_cabi_device_function":
        missing.append("supported_shape")
    rejected = tuple(payload["rejected_callback_shapes"])
    for required in ("arbitrary_python_callback", "action_or_side_effect_callback", "dynamic_sbt_direct_callable_hot_path"):
        if required not in rejected:
            missing.append(required)
    required_before = tuple(payload["required_before_public_support"])
    for required in ("stable API contract", "at least one app-route validation using the specialized callback path", "external 3-AI review"):
        if required not in required_before:
            missing.append(required)
    if payload["sbt_direct_callable_status"] != "experimental_yellow_not_public_support":
        missing.append("sbt_direct_callable_status")
    for key in ("tier3_public_support_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "decision": payload,
    }


__all__ = [
    "V4_GOAL4696_TIER3_PRODUCTIZATION_DECISION_STATUS",
    "V4_GOAL4696_NEXT_GOAL",
    "V4Goal4696Tier3ProductizationDecision",
    "v4_goal4696_tier3_productization_decision",
    "validate_v4_goal4696_tier3_productization_decision",
]
