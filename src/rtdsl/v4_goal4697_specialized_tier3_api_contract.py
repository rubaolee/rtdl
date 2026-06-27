from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4697_SPECIALIZED_TIER3_API_CONTRACT_STATUS = (
    "goal4697_constrained_specialized_tier3_api_contract_scaffold_not_public_support"
)
V4_GOAL4697_NEXT_GOAL = "Goal4698 specialized Tier-3 compile/cache/error-reporting scaffold"

V4_GOAL4697_ACCEPTED_STATUS = "tier3_specialized_candidate_contract_accepted_not_public_support"
V4_GOAL4697_REJECTED_ARBITRARY_PYTHON_STATUS = "rejected_goal4697_arbitrary_python_callback"
V4_GOAL4697_REJECTED_ACTION_STATUS = "rejected_goal4697_action_or_side_effect_callback"
V4_GOAL4697_REJECTED_EXTERNAL_MEMORY_STATUS = "rejected_goal4697_external_memory_mutation_callback"
V4_GOAL4697_REJECTED_SBT_STATUS = "rejected_goal4697_dynamic_sbt_direct_callable_hot_path"
V4_GOAL4697_REJECTED_NON_SCALAR_STATUS = "rejected_goal4697_non_scalar_callback_signature"

V4_GOAL4697_ACCEPTED_CALLBACK_SHAPES = (
    "custom_scalar_reduce",
    "custom_score",
    "custom_threshold",
    "custom_minmax",
)
V4_GOAL4697_ACCEPTED_SCALAR_TYPES = (
    "bool",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "float32",
    "float64",
)


@dataclass(frozen=True)
class V4Goal4697SpecializedTier3ApiContract:
    status: str
    candidate_surface: str
    supported_callback_shape: str
    callback_language: str
    compiler_contract: str
    wrapper_strategy: str
    accepted_signature: str
    accepted_scalar_types: tuple[str, ...]
    accepted_callback_shapes: tuple[str, ...]
    rejected_shapes: tuple[str, ...]
    next_goal: str
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "candidate_surface": self.candidate_surface,
            "supported_callback_shape": self.supported_callback_shape,
            "callback_language": self.callback_language,
            "compiler_contract": self.compiler_contract,
            "wrapper_strategy": self.wrapper_strategy,
            "accepted_signature": self.accepted_signature,
            "accepted_scalar_types": self.accepted_scalar_types,
            "accepted_callback_shapes": self.accepted_callback_shapes,
            "rejected_shapes": self.rejected_shapes,
            "next_goal": self.next_goal,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


@dataclass(frozen=True)
class V4Goal4697CallbackContractPlan:
    callback_shape: str
    status: str
    accepted: bool
    reason: str
    guidance: str
    internal_candidate_surface: str | None
    internal_productization_compile_path_allowed: bool
    app_route_validation_required: bool = True
    tier3_public_support_authorized: bool = False
    raw_optix_callback_authorized: bool = False
    release_authorized: bool = False
    performance_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "callback_shape": self.callback_shape,
            "status": self.status,
            "accepted": self.accepted,
            "reason": self.reason,
            "guidance": self.guidance,
            "internal_candidate_surface": self.internal_candidate_surface,
            "internal_productization_compile_path_allowed": self.internal_productization_compile_path_allowed,
            "app_route_validation_required": self.app_route_validation_required,
            "tier3_public_support_authorized": self.tier3_public_support_authorized,
            "raw_optix_callback_authorized": self.raw_optix_callback_authorized,
            "release_authorized": self.release_authorized,
            "performance_claim_authorized": self.performance_claim_authorized,
        }


def v4_goal4697_specialized_tier3_api_contract() -> V4Goal4697SpecializedTier3ApiContract:
    return V4Goal4697SpecializedTier3ApiContract(
        status=V4_GOAL4697_SPECIALIZED_TIER3_API_CONTRACT_STATUS,
        candidate_surface="module_specialized_direct_device_callback",
        supported_callback_shape="pure_scalar_return_numba_cabi_device_function",
        callback_language="numba_cuda_device_function_only",
        compiler_contract="Numba C-ABI device function PTX composed into an RTDL-generated OptiX module",
        wrapper_strategy="specialize_hit_program_module_and_call_callback_as_direct_device_function",
        accepted_signature=(
            "one scalar state output from fixed scalar inputs; Goal4695 validated "
            "float64 state, uint32 primitive_id, float64 hit_distance, float64 weight"
        ),
        accepted_scalar_types=V4_GOAL4697_ACCEPTED_SCALAR_TYPES,
        accepted_callback_shapes=V4_GOAL4697_ACCEPTED_CALLBACK_SHAPES,
        rejected_shapes=(
            "arbitrary_python_callback",
            "action_or_side_effect_callback",
            "external_memory_mutation_callback",
            "dynamic_sbt_direct_callable_hot_path",
            "non_scalar_signature",
        ),
        next_goal=V4_GOAL4697_NEXT_GOAL,
    )


def plan_v4_goal4697_specialized_tier3_callback_contract(
    *,
    callback_shape: str,
    callback_language: str = "numba",
    numba_cabi_device_function: bool = False,
    returns_scalar: bool = True,
    scalar_arguments_only: bool = True,
    mutates_shared_state: bool = False,
    writes_external_memory: bool = False,
    dynamic_allocation: bool = False,
    variable_length_output: bool = False,
    sbt_direct_callable_hot_path: bool = False,
    raw_optix_callback: bool = False,
    action_semantics: bool = False,
) -> V4Goal4697CallbackContractPlan:
    shape = str(callback_shape).strip().lower().replace("-", "_").replace(" ", "_")
    language = str(callback_language).strip().lower()

    def rejected(status: str, reason: str, guidance: str) -> V4Goal4697CallbackContractPlan:
        return V4Goal4697CallbackContractPlan(
            callback_shape=shape,
            status=status,
            accepted=False,
            reason=reason,
            guidance=guidance,
            internal_candidate_surface=None,
            internal_productization_compile_path_allowed=False,
        )

    if sbt_direct_callable_hot_path:
        return rejected(
            V4_GOAL4697_REJECTED_SBT_STATUS,
            "dynamic SBT direct-callable hot path was yellow in Goal4691",
            "Use the module-specialized hit-program path or keep this as research; do not expose it as support.",
        )
    if raw_optix_callback:
        return rejected(
            V4_GOAL4697_REJECTED_ACTION_STATUS,
            "raw OptiX callbacks are not the RTDL V4 programming model",
            "Rewrite as a generic reduce/filter operator or a constrained scalar Numba device callback.",
        )
    if language != "numba" or not numba_cabi_device_function:
        return rejected(
            V4_GOAL4697_REJECTED_ARBITRARY_PYTHON_STATUS,
            "only Numba C-ABI device functions are accepted by this scaffold",
            "Python callbacks, closures, host functions, and dynamic dispatch remain rejected.",
        )
    if writes_external_memory:
        return rejected(
            V4_GOAL4697_REJECTED_EXTERNAL_MEMORY_STATUS,
            "callback writes outside RTDL-owned fixed scalar state",
            "Return scalar state only; external memory mutation is deferred.",
        )
    if mutates_shared_state or dynamic_allocation or variable_length_output or action_semantics:
        return rejected(
            V4_GOAL4697_REJECTED_ACTION_STATUS,
            "callback has action or side-effect semantics",
            "Action-shaped callbacks are not V4.0 support; rewrite as a scalar reduce or defer.",
        )
    if not returns_scalar or not scalar_arguments_only:
        return rejected(
            V4_GOAL4697_REJECTED_NON_SCALAR_STATUS,
            "callback signature is outside the scalar-only contract",
            "Use fixed scalar inputs and one scalar return value for this candidate.",
        )
    if shape not in V4_GOAL4697_ACCEPTED_CALLBACK_SHAPES:
        return rejected(
            V4_GOAL4697_REJECTED_NON_SCALAR_STATUS,
            "callback shape is not in the accepted scalar candidate set",
            "Use custom_scalar_reduce, custom_score, custom_threshold, or custom_minmax for the scaffold.",
        )

    return V4Goal4697CallbackContractPlan(
        callback_shape=shape,
        status=V4_GOAL4697_ACCEPTED_STATUS,
        accepted=True,
        reason="matches the constrained module-specialized Numba scalar callback contract",
        guidance=(
            "Internal productization may compile this candidate through the specialized hit-program path. "
            "Public support remains blocked until compile/cache/error handling, app-route validation, and 3-AI review pass."
        ),
        internal_candidate_surface="module_specialized_direct_device_callback",
        internal_productization_compile_path_allowed=True,
    )


def validate_v4_goal4697_specialized_tier3_api_contract() -> dict[str, object]:
    contract = v4_goal4697_specialized_tier3_api_contract()
    accepted = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
    )
    rejected_python = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_scalar_reduce",
        callback_language="python",
        numba_cabi_device_function=False,
    )
    rejected_action = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_action",
        callback_language="numba",
        numba_cabi_device_function=True,
        mutates_shared_state=True,
    )
    rejected_external = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        writes_external_memory=True,
    )
    rejected_sbt = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        sbt_direct_callable_hot_path=True,
    )
    rejected_non_scalar = plan_v4_goal4697_specialized_tier3_callback_contract(
        callback_shape="custom_scalar_reduce",
        callback_language="numba",
        numba_cabi_device_function=True,
        returns_scalar=False,
    )

    payload = contract.as_dict()
    plans = {
        "accepted": accepted.as_dict(),
        "rejected_python": rejected_python.as_dict(),
        "rejected_action": rejected_action.as_dict(),
        "rejected_external_memory": rejected_external.as_dict(),
        "rejected_sbt": rejected_sbt.as_dict(),
        "rejected_non_scalar": rejected_non_scalar.as_dict(),
    }
    missing: list[str] = []
    if payload["status"] != V4_GOAL4697_SPECIALIZED_TIER3_API_CONTRACT_STATUS:
        missing.append("status")
    if payload["candidate_surface"] != "module_specialized_direct_device_callback":
        missing.append("candidate_surface")
    if accepted.status != V4_GOAL4697_ACCEPTED_STATUS or not accepted.accepted:
        missing.append("accepted_plan")
    expected_rejections = {
        "rejected_python": V4_GOAL4697_REJECTED_ARBITRARY_PYTHON_STATUS,
        "rejected_action": V4_GOAL4697_REJECTED_ACTION_STATUS,
        "rejected_external_memory": V4_GOAL4697_REJECTED_EXTERNAL_MEMORY_STATUS,
        "rejected_sbt": V4_GOAL4697_REJECTED_SBT_STATUS,
        "rejected_non_scalar": V4_GOAL4697_REJECTED_NON_SCALAR_STATUS,
    }
    for key, expected in expected_rejections.items():
        if plans[key]["status"] != expected or plans[key]["accepted"] is not False:
            missing.append(key)
    for key in ("tier3_public_support_authorized", "raw_optix_callback_authorized", "release_authorized", "performance_claim_authorized"):
        if payload[key] is not False:
            missing.append(key)
    for plan_name, plan in plans.items():
        if plan["tier3_public_support_authorized"] is not False:
            missing.append(f"{plan_name}_tier3_public_support_authorized")
        if plan["raw_optix_callback_authorized"] is not False:
            missing.append(f"{plan_name}_raw_optix_callback_authorized")
        if plan["release_authorized"] is not False:
            missing.append(f"{plan_name}_release_authorized")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "contract": payload,
        "plans": plans,
    }


__all__ = [
    "V4_GOAL4697_SPECIALIZED_TIER3_API_CONTRACT_STATUS",
    "V4_GOAL4697_NEXT_GOAL",
    "V4_GOAL4697_ACCEPTED_STATUS",
    "V4_GOAL4697_REJECTED_ARBITRARY_PYTHON_STATUS",
    "V4_GOAL4697_REJECTED_ACTION_STATUS",
    "V4_GOAL4697_REJECTED_EXTERNAL_MEMORY_STATUS",
    "V4_GOAL4697_REJECTED_SBT_STATUS",
    "V4_GOAL4697_REJECTED_NON_SCALAR_STATUS",
    "V4_GOAL4697_ACCEPTED_CALLBACK_SHAPES",
    "V4Goal4697SpecializedTier3ApiContract",
    "V4Goal4697CallbackContractPlan",
    "v4_goal4697_specialized_tier3_api_contract",
    "plan_v4_goal4697_specialized_tier3_callback_contract",
    "validate_v4_goal4697_specialized_tier3_api_contract",
]
