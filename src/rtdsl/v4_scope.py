from __future__ import annotations

from dataclasses import dataclass


V4_0_SCOPE_STATUS = "v4_0_0_formal_release_scope_authorized"
V4_0_AUTHORIZED_RELEASE_LABEL = "RTDL v4.0.0 formal high-performance generic RT-core operator release"

V4_0_INCLUDED_SURFACES = (
    "v4_fixed_radius_count_threshold_2d_device_arrays",
    "v4_closest_hit_grouped_argmin_3d_device_arrays",
    "v4_ray_triangle_any_hit_flags_2d_device_arrays",
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
    "v4_point_group_nearest_witness_2d_device_arrays",
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
    "v4_fixed_radius_graph_component_union_3d_device_arrays",
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
)

V4_0_CANDIDATE_SURFACES = ()

V4_0_INCLUDED_CAPABILITIES = (
    "unified_python_frontdoor",
    "torch_cuda_device_array_input",
    "torch_cuda_device_array_output",
    "rtdl_native_prepared_runner",
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

V4_RELEASE_BLOCKING_REASONS = ()


@dataclass(frozen=True)
class V4ScopeGate:
    status: str
    included_surfaces: tuple[str, ...]
    candidate_surfaces: tuple[str, ...]
    included_capabilities: tuple[str, ...]
    deferred_capabilities: tuple[str, ...]
    release_authorized: bool
    authorized_release_label: str
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
            "candidate_surfaces": self.candidate_surfaces,
            "included_capabilities": self.included_capabilities,
            "deferred_capabilities": self.deferred_capabilities,
            "release_authorized": self.release_authorized,
            "authorized_release_label": self.authorized_release_label,
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

    This gate defines the narrow V4.0.0 release scope. The release is formal
    for the included generic operator surfaces, while deferred V4.x
    capabilities and broad speedup claims remain explicitly unauthorized.
    """

    return V4ScopeGate(
        status=V4_0_SCOPE_STATUS,
        included_surfaces=V4_0_INCLUDED_SURFACES,
        candidate_surfaces=V4_0_CANDIDATE_SURFACES,
        included_capabilities=V4_0_INCLUDED_CAPABILITIES,
        deferred_capabilities=V4_X_DEFERRED_CAPABILITIES,
        release_authorized=True,
        authorized_release_label=V4_0_AUTHORIZED_RELEASE_LABEL,
        blocking_reasons=V4_RELEASE_BLOCKING_REASONS,
        required_next_actions=(
            "keep post-release guardrails passing",
            "record deferred Claude review debt when available",
            "treat Tier-3, CuPy performance, embedding, and whole-app speedups as V4.x work",
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
    if tuple(payload_dict.get("candidate_surfaces", ())) != V4_0_CANDIDATE_SURFACES:
        missing.append("candidate_surfaces")
    deferred = tuple(payload_dict.get("deferred_capabilities", ()))
    for required_deferred in V4_X_DEFERRED_CAPABILITIES:
        if required_deferred not in deferred:
            missing.append("deferred_capabilities")
            break
    forbidden_true = [
        key
        for key in (
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
    if payload_dict.get("release_authorized") is not True:
        missing.append("release_authorized")
    if payload_dict.get("authorized_release_label") != V4_0_AUTHORIZED_RELEASE_LABEL:
        missing.append("authorized_release_label")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "release_authorized": True,
        "checked_surfaces": V4_0_INCLUDED_SURFACES,
        "checked_candidate_surfaces": V4_0_CANDIDATE_SURFACES,
    }
