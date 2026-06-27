from __future__ import annotations

from dataclasses import dataclass


V4_0_SCOPE_STATUS = "v4_python_edsl_operator_pushdown_scope_goal4756_complete_rt_core_matrix"
V4_0_AUTHORIZED_RELEASE_LABEL = (
    "RTDL V4.0 Python eDSL/operator-pushdown release candidate and V2/V3 "
    "superset: complete 10-app NVIDIA RT-core V2.14/V3.0.2/V4.0 matrix, "
    "bounded material wins, and measured generic operator surfaces; broad "
    "all-benchmark speedup remains unauthorized"
)

V4_0_INCLUDED_SURFACES = (
    "v4_fixed_radius_count_threshold_2d_device_arrays",
    "v4_closest_hit_grouped_argmin_3d_device_arrays",
    "v4_ray_triangle_any_hit_flags_2d_device_arrays",
    "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
    "v4_point_group_nearest_witness_2d_device_arrays",
    "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
    "v4_fixed_radius_graph_component_union_3d_device_arrays",
    "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
    "v4_aggregate_frontier_device_columns_2d_prepared_runner",
    "v4_ray_triangle_custom_predicate_early_exit_3d_numba",
)

V4_0_CANDIDATE_SURFACES: tuple[str, ...] = ()

V4_0_INCLUDED_CAPABILITIES = (
    "unified_python_frontdoor",
    "torch_cuda_device_array_input",
    "torch_cuda_device_array_output",
    "rtdl_native_prepared_runner",
    "tier2_fused_generic_rt_operators",
    "operator_callback_planner",
    "constrained_numba_custom_predicate_early_exit",
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
    "goal4756_broad_all_benchmark_speedup_claim_not_supported",
)


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

    This gate defines the current bounded V4 operator scope after Goal4756.
    The included generic operator surfaces remain available, while formal
    app-level high-performance release wording and deferred V4.x capabilities
    remain explicitly unauthorized.
    """

    return V4ScopeGate(
        status=V4_0_SCOPE_STATUS,
        included_surfaces=V4_0_INCLUDED_SURFACES,
        candidate_surfaces=V4_0_CANDIDATE_SURFACES,
        included_capabilities=V4_0_INCLUDED_CAPABILITIES,
        deferred_capabilities=V4_X_DEFERRED_CAPABILITIES,
        release_authorized=False,
        authorized_release_label=V4_0_AUTHORIZED_RELEASE_LABEL,
        blocking_reasons=V4_RELEASE_BLOCKING_REASONS,
        required_next_actions=(
            "keep current bounded operator guardrails passing",
            "keep Goal4756 public docs/examples wording current before public tag",
            "do not advertise broad legacy all-app high-performance V4 until a new app-level gate passes",
            "do not count ranked-summary/RTNN as a V4 measured surface without a new generic lever and new evidence",
            "treat aggregate-frontier as a measured V2.14 host-frontier bottleneck route, not a V4-over-V3 speed win",
            "treat arbitrary callbacks, raw OptiX callbacks, embedding, and non-Python host work as future scoped work",
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
    if payload_dict.get("release_authorized") is not False:
        missing.append("release_authorized")
    if payload_dict.get("authorized_release_label") != V4_0_AUTHORIZED_RELEASE_LABEL:
        missing.append("authorized_release_label")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "release_authorized": False,
        "checked_surfaces": V4_0_INCLUDED_SURFACES,
        "checked_candidate_surfaces": V4_0_CANDIDATE_SURFACES,
    }
