from __future__ import annotations

from dataclasses import dataclass

from .v4_partner_promotion_contract import V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR
from .v4_partner_promotion_contract import V4_PARTNER_PROMOTION_PARITY_FLOOR
from .v4_partner_promotion_contract import v4_partner_promotion_candidate_allowed


V4_GOAL4649_CUPY_CERTIFICATION_STATUS = "goal4649_cupy_frontdoor_certification_gate"
V4_GOAL4649_CUPY_READY_FOR_POD = "ready_for_pod_certification"
V4_GOAL4649_CUPY_REQUIRES_MAPPING = "requires_v4_adapter_mapping_before_pod"


@dataclass(frozen=True)
class V4CuPyCertificationTarget:
    candidate_id: str
    operator: str
    gate_status: str
    representative_rows: int | None
    representative_groups: int | None
    warmup: int
    repeat: int
    correctness_parity_required: float
    representative_speedup_floor: float
    partner_parity_floor: float
    denominator: str
    v4_frontdoor_route: str | None
    public_claim_authorized: bool = False
    partner_migration_counts_as_v4_speed_win: bool = False
    partner_parity_counts_as_v4_speed_win: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "operator": self.operator,
            "gate_status": self.gate_status,
            "representative_rows": self.representative_rows,
            "representative_groups": self.representative_groups,
            "warmup": self.warmup,
            "repeat": self.repeat,
            "correctness_parity_required": self.correctness_parity_required,
            "representative_speedup_floor": self.representative_speedup_floor,
            "partner_parity_floor": self.partner_parity_floor,
            "denominator": self.denominator,
            "v4_frontdoor_route": self.v4_frontdoor_route,
            "public_claim_authorized": self.public_claim_authorized,
            "partner_migration_counts_as_v4_speed_win": self.partner_migration_counts_as_v4_speed_win,
            "partner_parity_counts_as_v4_speed_win": self.partner_parity_counts_as_v4_speed_win,
        }


V4_GOAL4649_CUPY_TARGETS = (
    V4CuPyCertificationTarget(
        candidate_id="cupy_grouped_reduction_device_columns_262144",
        operator="grouped_vector_sum_f64x2",
        gate_status=V4_GOAL4649_CUPY_READY_FOR_POD,
        representative_rows=262144,
        representative_groups=1024,
        warmup=3,
        repeat=100,
        correctness_parity_required=1.0,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        denominator="same_contract_python_cpu_row_loop_and_optional_numba_partner_control",
        v4_frontdoor_route="prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
    ),
    V4CuPyCertificationTarget(
        candidate_id="cupy_grouped_reduction_device_columns_524288",
        operator="grouped_vector_sum_f64x2",
        gate_status=V4_GOAL4649_CUPY_READY_FOR_POD,
        representative_rows=524288,
        representative_groups=2048,
        warmup=3,
        repeat=100,
        correctness_parity_required=1.0,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        denominator="same_contract_python_cpu_row_loop_and_optional_numba_partner_control",
        v4_frontdoor_route="prepare_grouped_vector_sum_2d_partner_columns_session(partner='cupy')",
    ),
    V4CuPyCertificationTarget(
        candidate_id="cupy_segment_polygon_hitcount_prepared_scaling",
        operator="any_hit_flags_or_hitcount_columns",
        gate_status=V4_GOAL4649_CUPY_REQUIRES_MAPPING,
        representative_rows=None,
        representative_groups=None,
        warmup=0,
        repeat=0,
        correctness_parity_required=1.0,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        denominator="not_frozen_until_adapter_mapping_exists",
        v4_frontdoor_route=None,
    ),
    V4CuPyCertificationTarget(
        candidate_id="cupy_hausdorff_witness_continuation",
        operator="nearest_witness_or_witness_continuation",
        gate_status=V4_GOAL4649_CUPY_REQUIRES_MAPPING,
        representative_rows=None,
        representative_groups=None,
        warmup=0,
        repeat=0,
        correctness_parity_required=1.0,
        representative_speedup_floor=V4_PARTNER_PROMOTION_DEFAULT_SPEEDUP_FLOOR,
        partner_parity_floor=V4_PARTNER_PROMOTION_PARITY_FLOOR,
        denominator="not_frozen_until_adapter_mapping_exists",
        v4_frontdoor_route=None,
    ),
)


def v4_goal4649_cupy_certification_targets() -> list[dict[str, object]]:
    return [target.as_dict() for target in V4_GOAL4649_CUPY_TARGETS]


def v4_goal4649_ready_cupy_targets() -> list[dict[str, object]]:
    return [
        target.as_dict()
        for target in V4_GOAL4649_CUPY_TARGETS
        if target.gate_status == V4_GOAL4649_CUPY_READY_FOR_POD
        and v4_partner_promotion_candidate_allowed(target.candidate_id, partner="cupy")
    ]


def v4_goal4649_target_by_id(candidate_id: str) -> dict[str, object]:
    for target in V4_GOAL4649_CUPY_TARGETS:
        if target.candidate_id == candidate_id:
            return target.as_dict()
    raise ValueError(f"unknown Goal4649 CuPy candidate: {candidate_id}")
