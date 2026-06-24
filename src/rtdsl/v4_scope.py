from __future__ import annotations

from dataclasses import dataclass


V4_0_SCOPE_STATUS = "v4_0_development_scope_defined_not_release"

V4_0_INCLUDED_SURFACES = (
    "v4_fixed_radius_count_threshold_2d_device_arrays",
    "v4_closest_hit_grouped_argmin_3d_device_arrays",
    "v4_ray_triangle_any_hit_flags_2d_device_arrays",
)

V4_0_INCLUDED_CAPABILITIES = (
    "unified_python_frontdoor",
    "torch_cuda_device_array_input",
    "torch_cuda_device_array_output",
    "tier2_fused_generic_rt_operators",
    "operator_callback_planner",
)

V4_X_DEFERRED_CAPABILITIES = (
    "tier3_numba_ptx_generation_spike_only",
    "tier3_numba_bare_ptx_direct_optix_module_link_blocked",
    "tier3_wrapper_direct_callable_abi",
    "raw_optix_callback_public_api",
    "cupy_measured_performance_claims",
    "embedding_c_abi",
    "non_python_host_bindings",
    "app_specific_native_engine_kernels",
)

V4_RELEASE_BLOCKING_REASONS = (
    "external_release_review_not_obtained",
    "release_decision_record_not_obtained",
    "v4_review_debt_open",
)


@dataclass(frozen=True)
class V4ScopeGate:
    status: str
    included_surfaces: tuple[str, ...]
    included_capabilities: tuple[str, ...]
    deferred_capabilities: tuple[str, ...]
    release_authorized: bool
    blocking_reasons: tuple[str, ...]
    required_next_actions: tuple[str, ...]
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    tier3_callback_claim_authorized: bool = False
    raw_optix_callback_claim_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    embedding_c_abi_claim_authorized: bool = False
    non_python_host_binding_claim_authorized: bool = False
    app_specific_native_kernel_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "included_surfaces": self.included_surfaces,
            "included_capabilities": self.included_capabilities,
            "deferred_capabilities": self.deferred_capabilities,
            "release_authorized": self.release_authorized,
            "blocking_reasons": self.blocking_reasons,
            "required_next_actions": self.required_next_actions,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "tier3_callback_claim_authorized": self.tier3_callback_claim_authorized,
            "raw_optix_callback_claim_authorized": self.raw_optix_callback_claim_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "embedding_c_abi_claim_authorized": self.embedding_c_abi_claim_authorized,
            "non_python_host_binding_claim_authorized": self.non_python_host_binding_claim_authorized,
            "app_specific_native_kernel_authorized": self.app_specific_native_kernel_authorized,
        }


def v4_0_scope_gate() -> V4ScopeGate:
    """Return the current V4.0 scope gate.

    This gate is intentionally conservative: it defines the engineering scope
    already built and measured, while keeping release authorization false until
    the required external release review and decision record exist.
    """

    return V4ScopeGate(
        status=V4_0_SCOPE_STATUS,
        included_surfaces=V4_0_INCLUDED_SURFACES,
        included_capabilities=V4_0_INCLUDED_CAPABILITIES,
        deferred_capabilities=V4_X_DEFERRED_CAPABILITIES,
        release_authorized=False,
        blocking_reasons=V4_RELEASE_BLOCKING_REASONS,
        required_next_actions=(
            "obtain external release review for the V4.0 release-candidate packet",
            "obtain a release decision record",
            "close or explicitly waive V4 review debt before public release",
        ),
    )


def validate_v4_0_scope_gate(payload: V4ScopeGate | dict[str, object] | None = None) -> dict[str, object]:
    """Validate the V4.0 scope gate and return a machine-readable result."""

    if payload is None:
        payload_dict = v4_0_scope_gate().as_dict()
    elif isinstance(payload, V4ScopeGate):
        payload_dict = payload.as_dict()
    else:
        payload_dict = dict(payload)

    missing: list[str] = []
    if payload_dict.get("status") != V4_0_SCOPE_STATUS:
        missing.append("status")
    if tuple(payload_dict.get("included_surfaces", ())) != V4_0_INCLUDED_SURFACES:
        missing.append("included_surfaces")
    deferred = tuple(payload_dict.get("deferred_capabilities", ()))
    for required_deferred in V4_X_DEFERRED_CAPABILITIES:
        if required_deferred not in deferred:
            missing.append("deferred_capabilities")
            break
    forbidden_true = [
        key
        for key in (
            "release_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "embedding_c_abi_claim_authorized",
            "non_python_host_binding_claim_authorized",
            "app_specific_native_kernel_authorized",
        )
        if payload_dict.get(key) is not False
    ]
    if forbidden_true:
        missing.append("forbidden_claim_flags_false")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "release_authorized": False,
        "checked_surfaces": V4_0_INCLUDED_SURFACES,
    }
