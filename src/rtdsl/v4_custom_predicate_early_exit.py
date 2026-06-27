from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE = (
    "v4_ray_triangle_custom_predicate_early_exit_3d_numba"
)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS = (
    "tier2_measured_goal4715_operator_pushdown_surface_not_release"
)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE = (
    "RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_3D"
)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS = ("numba",)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_DECLARED_UNMEASURED_PARTNERS = (
    "torch",
    "cupy",
    "rtdl_native",
)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES = (
    "pure_boolean_numba_cabi_device_function",
    "boolean_numba_cabi_device_function",
)
V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS = (
    "terminate_on_first_accept",
    "filter_accept_flags",
)


def _normalize_token(value: object) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _require_partner(partner: str) -> str:
    partner = _normalize_token(partner)
    allowed = (
        *V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS,
        *V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_DECLARED_UNMEASURED_PARTNERS,
    )
    if partner not in allowed:
        raise ValueError(f"partner must be one of: {', '.join(allowed)}")
    return partner


def _require_action(action: str) -> str:
    action = _normalize_token(action)
    if action not in V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS:
        allowed = ", ".join(V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS)
        raise ValueError(f"action must be one of: {allowed}")
    return action


def _require_callback_shape(callback_shape: str) -> str:
    callback_shape = _normalize_token(callback_shape)
    if callback_shape not in V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES:
        allowed = ", ".join(V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES)
        raise ValueError(f"callback_shape must be one of: {allowed}")
    return callback_shape


def ray_triangle_custom_predicate_early_exit_claim_boundary_v4(
    *,
    partner: str = "numba",
    callback_shape: str = "pure_boolean_numba_cabi_device_function",
    action: str = "terminate_on_first_accept",
) -> dict[str, object]:
    """Return the V4 boundary for custom predicate early-exit pushdown.

    This surface is deliberately narrower than raw OptiX callback support. The
    user supplies a pure boolean/scalar Numba C-ABI device function; RTDL owns
    the traversal action, such as terminating on the first accepted hit.
    """

    partner = _require_partner(partner)
    callback_shape = _require_callback_shape(callback_shape)
    action = _require_action(action)
    measured = partner in V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS
    return {
        "status": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS,
        "v4_api_surface": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
        "generic_primitive": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE,
        "continuation_class": "custom_predicate_early_exit",
        "partner": partner,
        "measured_partner": measured,
        "measured_partners": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS,
        "partner_support_declared_unmeasured": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_DECLARED_UNMEASURED_PARTNERS,
        "partner_claim_status": (
            "measured_on_v4_goal4715_pod_optix8_numba_callback"
            if measured
            else "declared_unmeasured_not_performance_ready"
        ),
        "callback_shape": callback_shape,
        "allowed_callback_shapes": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES,
        "action": action,
        "allowed_actions": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS,
        "user_callback_semantics": "pure_boolean_or_scalar_predicate_only",
        "rtdl_owned_action": True,
        "external_memory_mutation_authorized": False,
        "dynamic_allocation_authorized": False,
        "variable_length_output_authorized": False,
        "arbitrary_python_callback_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "constrained_user_predicate_authorized": measured,
        "host_materialization_in_hot_path": False,
        "hot_path_candidate_materialization": "avoided_for_primary_early_accept_regimes",
        "v2_v3_denominator": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback",
        "goal4715_primary_v2_speedup_geomean": 3.608025018751732,
        "goal4715_primary_v3_speedup_geomean": 3.608025018751732,
        "goal4715_min_primary_v3_speedup": 1.9761904761904763,
        "goal4715_max_primary_v3_speedup": 8.130865199087879,
        "goal4715_control_v3_speedup_geomean": 1.5585401086027044,
        "goal4717_serious_scale_primary_v2_speedup_geomean": 4.632757911153888,
        "goal4717_serious_scale_primary_v3_speedup_geomean": 4.632757911153888,
        "goal4717_serious_scale_min_primary_v3_speedup": 2.054686620906942,
        "goal4717_serious_scale_max_primary_v3_speedup": 9.673329274891774,
        "goal4717_serious_scale_control_v3_speedup_geomean": 1.6303665522050805,
        "serious_scale_primary_v2_speedup_geomean": 4.632757911153888,
        "serious_scale_primary_v3_speedup_geomean": 4.632757911153888,
        "serious_scale_min_primary_v3_speedup": 2.054686620906942,
        "serious_scale_max_primary_v3_speedup": 9.673329274891774,
        "serious_scale_control_v3_speedup_geomean": 1.6303665522050805,
        "goal4715_correctness_all_passed": True,
        "goal4717_serious_scale_correctness_all_passed": True,
        "serious_scale_correctness_all_passed": True,
        "goal4715_pod_gpu": "NVIDIA RTX A5000",
        "goal4715_driver": "570.195.03",
        "validated_optix_abi": "8.0",
        "validated_partner_scope": "numba C-ABI device predicate generated as PTX and linked into generated OptiX any-hit route",
        "comparison_class": "operator_pushdown_vs_materialized_device_fallback",
        "performance_caveat": (
            "focused custom predicate early-exit timing gate; not an all-app "
            "or arbitrary callback speed claim"
        ),
        "source_evidence": (
            "future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json",
            "future/v4/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md",
            "future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json",
        ),
        "release_claim_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "app_level_speed_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "public_tier3_support_authorized": False,
        "true_zero_copy_authorized": False,
        "embedding_c_abi_claim_authorized": False,
        "non_python_host_binding_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


@dataclass(frozen=True)
class V4CustomPredicateEarlyExitPlan:
    """Validated plan for the constrained V4 predicate early-exit surface."""

    callback_shape: str
    action: str
    partner: str = "numba"
    numba_device_function: bool = True
    mutates_shared_state: bool = False
    variable_length_output: bool = False
    dynamic_allocation: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "surface": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
            "generic_primitive": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE,
            "callback_shape": self.callback_shape,
            "action": self.action,
            "partner": self.partner,
            "numba_device_function": self.numba_device_function,
            "mutates_shared_state": self.mutates_shared_state,
            "variable_length_output": self.variable_length_output,
            "dynamic_allocation": self.dynamic_allocation,
            "claim_boundary": ray_triangle_custom_predicate_early_exit_claim_boundary_v4(
                partner=self.partner,
                callback_shape=self.callback_shape,
                action=self.action,
            ),
        }


def plan_ray_triangle_custom_predicate_early_exit_v4(
    *,
    callback_shape: str = "pure_boolean_numba_cabi_device_function",
    action: str = "terminate_on_first_accept",
    partner: str = "numba",
    numba_device_function: bool = True,
    mutates_shared_state: bool = False,
    variable_length_output: bool = False,
    dynamic_allocation: bool = False,
) -> V4CustomPredicateEarlyExitPlan:
    """Validate the supported V4 custom predicate early-exit contract."""

    partner = _require_partner(partner)
    if partner != "numba":
        raise RuntimeError("custom predicate early-exit is measured only for Numba C-ABI callbacks")
    callback_shape = _require_callback_shape(callback_shape)
    action = _require_action(action)
    if not bool(numba_device_function):
        raise RuntimeError("custom predicate early-exit requires a Numba C-ABI device function")
    if mutates_shared_state or variable_length_output or dynamic_allocation:
        raise RuntimeError(
            "custom predicate early-exit accepts only pure predicates; shared mutation, "
            "dynamic allocation, and variable-length output are rejected"
        )
    return V4CustomPredicateEarlyExitPlan(
        callback_shape=callback_shape,
        action=action,
        partner=partner,
        numba_device_function=True,
        mutates_shared_state=False,
        variable_length_output=False,
        dynamic_allocation=False,
    )


@dataclass
class V4RayTriangleCustomPredicateEarlyExit3DNumbaSession:
    """Thin V4 product surface over a generated OptiX predicate early-exit executor.

    The executor is owned by RTDL-generated code. This wrapper provides the
    public contract, metadata, close semantics, and claim boundary. It does not
    expose raw OptiX module/SBT/pipeline controls to the user.
    """

    executor: Any
    plan: V4CustomPredicateEarlyExitPlan

    def __post_init__(self) -> None:
        self._closed = False

    @property
    def claim_boundary(self) -> dict[str, object]:
        return ray_triangle_custom_predicate_early_exit_claim_boundary_v4(
            partner=self.plan.partner,
            callback_shape=self.plan.callback_shape,
            action=self.plan.action,
        )

    def __enter__(self) -> "V4RayTriangleCustomPredicateEarlyExit3DNumbaSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        close = getattr(self.executor, "close", None)
        if callable(close):
            close()
        self._closed = True

    def run(self, *args, return_metadata: bool = True, **kwargs):
        if self._closed:
            raise RuntimeError("V4 custom predicate early-exit session is closed")
        run = getattr(self.executor, "run", None)
        if not callable(run):
            raise RuntimeError("executor must provide a run method")
        result = run(*args, **kwargs)
        if not return_metadata:
            return result
        metadata = {
            **self.claim_boundary,
            "adapter": V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE,
            "native_route": "generated_optix_any_hit_predicate_early_exit",
            "result_payload_type": type(result).__name__,
        }
        if isinstance(result, dict):
            existing_metadata = result.get("metadata")
            if isinstance(existing_metadata, dict):
                result = dict(result)
                result["metadata"] = {**existing_metadata, **metadata}
                return result
            result = dict(result)
            result["metadata"] = metadata
            return result
        return {"result": result, "metadata": metadata}


def prepare_ray_triangle_custom_predicate_early_exit_3d_numba_v4(
    executor: Any,
    *,
    callback_shape: str = "pure_boolean_numba_cabi_device_function",
    action: str = "terminate_on_first_accept",
    numba_device_function: bool = True,
) -> V4RayTriangleCustomPredicateEarlyExit3DNumbaSession:
    """Prepare the measured V4 custom predicate early-exit API wrapper.

    `executor` is the RTDL-generated OptiX/Numba route. The wrapper exists so
    users interact with an RTDL eDSL surface instead of raw OptiX handles.
    """

    plan = plan_ray_triangle_custom_predicate_early_exit_v4(
        callback_shape=callback_shape,
        action=action,
        partner="numba",
        numba_device_function=numba_device_function,
    )
    return V4RayTriangleCustomPredicateEarlyExit3DNumbaSession(executor=executor, plan=plan)


__all__ = [
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_SURFACE",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_STATUS",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_PRIMITIVE",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ALLOWED_PARTNERS",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_CALLBACK_SHAPES",
    "V4_RAY_TRIANGLE_CUSTOM_PREDICATE_EARLY_EXIT_ACTIONS",
    "V4CustomPredicateEarlyExitPlan",
    "V4RayTriangleCustomPredicateEarlyExit3DNumbaSession",
    "ray_triangle_custom_predicate_early_exit_claim_boundary_v4",
    "plan_ray_triangle_custom_predicate_early_exit_v4",
    "prepare_ray_triangle_custom_predicate_early_exit_3d_numba_v4",
]
