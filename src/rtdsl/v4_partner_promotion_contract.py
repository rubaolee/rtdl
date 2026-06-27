from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS = "goal4648_partner_promotion_contract_numeric_bars"
V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR = 1.20
V4_PARTNER_PROMOTION_PARITY_FLOOR = 0.98
V4_PARTNER_PROMOTION_CORRECTNESS_PARITY = 1.0


@dataclass(frozen=True)
class V4PartnerPromotionContract:
    """Pre-run contract for promoting a partner into a V4 certified surface."""

    partner: str
    contract_class: str
    status: str
    candidate_ids: tuple[str, ...]
    generic_operator_fits: tuple[str, ...]
    accepted_dtypes: tuple[str, ...]
    required_layout: str
    cuda_device_ownership: str
    stream_synchronization: str
    output_ownership: str
    telemetry_required: tuple[str, ...]
    correctness_parity_required: float
    representative_speedup_floor: float
    partner_parity_floor: float
    fixed_operator_only: bool
    arbitrary_callback_supported: bool
    accepted_signatures: tuple[str, ...]
    compile_cache_timing_boundary: str | None
    partner_migration_counts_as_v4_speed_win: bool
    cupy_performance_claim_authorized: bool
    arbitrary_numba_callback_claim_authorized: bool
    partner_parity_counts_as_v4_speed_win: bool
    broad_v4_speedup_claim_authorized: bool
    whole_app_speedup_claim_authorized: bool
    release_claim_authorized: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "partner": self.partner,
            "contract_class": self.contract_class,
            "status": self.status,
            "candidate_ids": self.candidate_ids,
            "generic_operator_fits": self.generic_operator_fits,
            "accepted_dtypes": self.accepted_dtypes,
            "required_layout": self.required_layout,
            "cuda_device_ownership": self.cuda_device_ownership,
            "stream_synchronization": self.stream_synchronization,
            "output_ownership": self.output_ownership,
            "telemetry_required": self.telemetry_required,
            "correctness_parity_required": self.correctness_parity_required,
            "representative_speedup_floor": self.representative_speedup_floor,
            "partner_parity_floor": self.partner_parity_floor,
            "fixed_operator_only": self.fixed_operator_only,
            "arbitrary_callback_supported": self.arbitrary_callback_supported,
            "accepted_signatures": self.accepted_signatures,
            "compile_cache_timing_boundary": self.compile_cache_timing_boundary,
            "partner_migration_counts_as_v4_speed_win": self.partner_migration_counts_as_v4_speed_win,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "arbitrary_numba_callback_claim_authorized": self.arbitrary_numba_callback_claim_authorized,
            "partner_parity_counts_as_v4_speed_win": self.partner_parity_counts_as_v4_speed_win,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "release_claim_authorized": self.release_claim_authorized,
        }


V4_PARTNER_PROMOTION_CONTRACTS = {
    "cupy": V4PartnerPromotionContract(
        partner="cupy",
        contract_class="device_array_frontdoor_certification",
        status=V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS,
        candidate_ids=(
            "cupy_grouped_reduction_device_columns_262144",
            "cupy_grouped_reduction_device_columns_524288",
            "cupy_segment_polygon_hitcount_prepared_scaling",
            "cupy_hausdorff_witness_continuation",
        ),
        generic_operator_fits=(
            "grouped_sum_or_grouped_reduction",
            "any_hit_flags_or_hitcount_columns",
            "group_argmin_then_global_argmax_with_witness",
            "nearest_witness",
        ),
        accepted_dtypes=("float32", "float64", "int32", "int64", "uint64", "bool"),
        required_layout="contiguous_1d_or_column_major_device_columns_no_python_rows",
        cuda_device_ownership="caller_owned_cupy_cuda_device_array_same_device_as_v4_session",
        stream_synchronization=(
            "caller must declare default-stream or explicit-stream mode before the run; "
            "Goal4649 must record the mode and any synchronization points"
        ),
        output_ownership="v4_allocated_or_caller_provided_cupy_device_outputs_no_hot_host_materialization",
        telemetry_required=(
            "correctness_parity",
            "representative_speedup",
            "partner_parity",
            "host_materialization_in_hot_path",
            "denominator",
            "scale",
            "stream_mode",
            "output_ownership",
        ),
        correctness_parity_required=V4_PARTNER_PROMOTION_CORRECTNESS_PARITY,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        fixed_operator_only=True,
        arbitrary_callback_supported=False,
        accepted_signatures=(
            "cupy.ndarray device columns -> cupy.ndarray grouped reductions",
            "cupy.ndarray device columns -> cupy.ndarray hit flags/count columns",
            "cupy.ndarray device columns -> cupy.ndarray witness columns",
        ),
        compile_cache_timing_boundary=None,
        partner_migration_counts_as_v4_speed_win=False,
        cupy_performance_claim_authorized=False,
        arbitrary_numba_callback_claim_authorized=False,
        partner_parity_counts_as_v4_speed_win=False,
        broad_v4_speedup_claim_authorized=False,
        whole_app_speedup_claim_authorized=False,
        release_claim_authorized=False,
    ),
    "numba_fixed": V4PartnerPromotionContract(
        partner="numba",
        contract_class="fixed_continuation_certification",
        status=V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS,
        candidate_ids=("numba_component_union_current_v4_surface",),
        generic_operator_fits=("fixed_radius_graph_component_union",),
        accepted_dtypes=("float32", "float64", "int32", "int64"),
        required_layout="fixed_signature_device_columns_no_python_rows",
        cuda_device_ownership="rtdl_prepared_session_or_caller_owned_device_columns_same_cuda_context",
        stream_synchronization=(
            "compile/cache timing must be separated from hot run timing; "
            "Goal4650 must record synchronization points"
        ),
        output_ownership="v4_or_partner_allocated_device_columns_with_canonical_component_signature",
        telemetry_required=(
            "correctness_parity",
            "representative_speedup",
            "partner_parity",
            "host_materialization_in_hot_path",
            "compile_time_seconds",
            "cache_hit",
            "denominator",
            "scale",
        ),
        correctness_parity_required=V4_PARTNER_PROMOTION_CORRECTNESS_PARITY,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        fixed_operator_only=True,
        arbitrary_callback_supported=False,
        accepted_signatures=("fixed_radius_graph_component_union_3d(device columns) -> component labels",),
        compile_cache_timing_boundary="compile_time_excluded_from_hot_path_but_reported_as_phase_telemetry",
        partner_migration_counts_as_v4_speed_win=False,
        cupy_performance_claim_authorized=False,
        arbitrary_numba_callback_claim_authorized=False,
        partner_parity_counts_as_v4_speed_win=False,
        broad_v4_speedup_claim_authorized=False,
        whole_app_speedup_claim_authorized=False,
        release_claim_authorized=False,
    ),
}


def v4_partner_promotion_contracts() -> list[dict[str, object]]:
    """Return all Goal4648 pre-run partner promotion contracts."""

    return [contract.as_dict() for contract in V4_PARTNER_PROMOTION_CONTRACTS.values()]


def v4_partner_promotion_contract(partner: str, *, fixed: bool = False) -> dict[str, object]:
    """Return one Goal4648 contract or fail closed for unsupported partners."""

    key = "numba_fixed" if partner == "numba" and fixed else str(partner).strip().lower()
    if key not in V4_PARTNER_PROMOTION_CONTRACTS:
        raise ValueError("partner promotion contract must be one of: cupy, numba with fixed=True")
    return V4_PARTNER_PROMOTION_CONTRACTS[key].as_dict()


def v4_partner_promotion_candidate_allowed(candidate_id: str, *, partner: str) -> bool:
    """Return whether a candidate is allowed to enter Goal4649/4650 certification."""

    normalized_partner = str(partner).strip().lower()
    if normalized_partner not in {"cupy", "numba"}:
        return False
    for key, contract in V4_PARTNER_PROMOTION_CONTRACTS.items():
        if normalized_partner == "numba" and key != "numba_fixed":
            continue
        if normalized_partner == "cupy" and key != "cupy":
            continue
        if candidate_id in contract.candidate_ids:
            return True
    return False
