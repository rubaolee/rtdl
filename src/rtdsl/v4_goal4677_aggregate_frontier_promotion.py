from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


V4_GOAL4677_AGGREGATE_FRONTIER_PROMOTION_STATUS = (
    "goal4677_promote_aggregate_frontier_device_columns_measured_route_no_release"
)
V4_GOAL4677_CANONICAL_EVIDENCE = (
    "future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json"
)


@dataclass(frozen=True)
class V4Goal4677AggregateFrontierPromotionDecision:
    status: str
    promoted: bool
    promoted_surface: str
    generic_primitive: str
    measured_partners: tuple[str, ...]
    declared_unmeasured_partners: tuple[str, ...]
    source_evidence: str
    pass_fail: dict[str, object]
    ratios: dict[str, float]
    v3_0_2_caveat: str
    release_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_authorized: bool = False
    cupy_performance_claim_authorized: bool = False
    partner_migration_counts_as_v4_speed_win: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "promoted": self.promoted,
            "promoted_surface": self.promoted_surface,
            "generic_primitive": self.generic_primitive,
            "measured_partners": self.measured_partners,
            "declared_unmeasured_partners": self.declared_unmeasured_partners,
            "source_evidence": self.source_evidence,
            "pass_fail": self.pass_fail,
            "ratios": self.ratios,
            "v3_0_2_caveat": self.v3_0_2_caveat,
            "release_authorized": self.release_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "cupy_performance_claim_authorized": self.cupy_performance_claim_authorized,
            "partner_migration_counts_as_v4_speed_win": self.partner_migration_counts_as_v4_speed_win,
        }


def _load_summary(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_goal4676_summary_for_promotion(summary: Mapping[str, Any]) -> dict[str, object]:
    pass_fail = dict(summary.get("pass_fail", {}))
    ratios = dict(summary.get("ratios", {}))
    missing: list[str] = []
    required_true = (
        "all_subprocesses_returned_zero",
        "correctness_companion_ok",
        "large_run_checksum_parity",
        "goal4676_pass",
        "v4_frontier_only_hot_bar_pass",
        "v4_full_hot_bar_pass",
        "v4_full_wall_bar_pass",
    )
    for key in required_true:
        if pass_fail.get(key) is not True:
            missing.append(key)
    if pass_fail.get("v4_host_frontier_materialization_in_hot_path") is not False:
        missing.append("v4_host_frontier_materialization_in_hot_path_false")
    if pass_fail.get("partner_migration_counted_as_speed") is not False:
        missing.append("partner_migration_counted_as_speed_false")
    if float(ratios.get("v4_frontier_only_hot_over_v2_14", 0.0)) < 1.20:
        missing.append("v4_frontier_only_hot_over_v2_14_min_1_20")
    if float(ratios.get("v4_full_hot_over_v2_14", 0.0)) < 1.20:
        missing.append("v4_full_hot_over_v2_14_min_1_20")
    if float(ratios.get("v4_full_wall_over_v2_14", 0.0)) < 1.10:
        missing.append("v4_full_wall_over_v2_14_min_1_10")
    if float(ratios.get("v4_full_hot_over_v3_0_2_control", 0.0)) < 0.98:
        missing.append("v4_full_hot_over_v3_0_2_parity_floor_0_98")
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "release_authorized": False,
    }


def v4_goal4677_aggregate_frontier_promotion_decision(
    evidence_path: str | Path = V4_GOAL4677_CANONICAL_EVIDENCE,
) -> V4Goal4677AggregateFrontierPromotionDecision:
    summary = _load_summary(evidence_path)
    validation = validate_goal4676_summary_for_promotion(summary)
    promoted = validation["status"] == "passed"
    pass_fail = dict(summary.get("pass_fail", {}))
    ratios = {key: float(value) for key, value in dict(summary.get("ratios", {})).items()}
    return V4Goal4677AggregateFrontierPromotionDecision(
        status=(
            V4_GOAL4677_AGGREGATE_FRONTIER_PROMOTION_STATUS
            if promoted
            else "goal4677_reject_aggregate_frontier_promotion_reopen_goal4676"
        ),
        promoted=promoted,
        promoted_surface="v4_aggregate_frontier_device_columns_2d_prepared_runner",
        generic_primitive="AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D",
        measured_partners=("rtdl_native", "cupy") if promoted else (),
        declared_unmeasured_partners=("torch", "numba"),
        source_evidence=str(evidence_path),
        pass_fail=pass_fail,
        ratios=ratios,
        v3_0_2_caveat=(
            "Goal4676 promotes a V2.14 host-frontier bottleneck fix. It does not "
            "prove a V4-over-V3 speedup because V3.0.2 already contains the same "
            "aggregate-frontier device-column primitive family."
        ),
        partner_migration_counts_as_v4_speed_win=False,
    )


def validate_v4_goal4677_aggregate_frontier_promotion(
    evidence_path: str | Path = V4_GOAL4677_CANONICAL_EVIDENCE,
) -> dict[str, object]:
    decision = v4_goal4677_aggregate_frontier_promotion_decision(evidence_path)
    missing: list[str] = []
    if not decision.promoted:
        missing.append("promoted")
    for key in (
        "release_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_authorized",
        "cupy_performance_claim_authorized",
        "partner_migration_counts_as_v4_speed_win",
    ):
        if decision.as_dict().get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "decision": decision.as_dict(),
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4677_AGGREGATE_FRONTIER_PROMOTION_STATUS",
    "V4_GOAL4677_CANONICAL_EVIDENCE",
    "V4Goal4677AggregateFrontierPromotionDecision",
    "validate_goal4676_summary_for_promotion",
    "v4_goal4677_aggregate_frontier_promotion_decision",
    "validate_v4_goal4677_aggregate_frontier_promotion",
]
