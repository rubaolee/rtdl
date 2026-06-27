from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


V4_GOAL4681_SHAPE_PAIR_RELATION_RESULT_STATUS = (
    "goal4681_correct_same_primitive_but_no_speed_credit_do_not_promote"
)
V4_GOAL4681_CANONICAL_EVIDENCE = (
    "tools/_archive/future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json"
)


@dataclass(frozen=True)
class V4Goal4681ShapePairRelationResult:
    status: str
    source_evidence: str
    decision_label: str
    correctness_passed: bool
    serious_active_count_parity: bool
    no_v4_host_row_stream_materialization: bool
    speed_credit_passed: bool
    ratios: dict[str, float | None]
    release_authorized: bool = False
    promote_to_measured_catalog_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "source_evidence": self.source_evidence,
            "decision_label": self.decision_label,
            "correctness_passed": self.correctness_passed,
            "serious_active_count_parity": self.serious_active_count_parity,
            "no_v4_host_row_stream_materialization": self.no_v4_host_row_stream_materialization,
            "speed_credit_passed": self.speed_credit_passed,
            "ratios": dict(self.ratios),
            "release_authorized": self.release_authorized,
            "promote_to_measured_catalog_authorized": self.promote_to_measured_catalog_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
        }


def _load_summary(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def v4_goal4681_shape_pair_relation_result(
    evidence_path: str | Path = V4_GOAL4681_CANONICAL_EVIDENCE,
) -> V4Goal4681ShapePairRelationResult:
    summary = _load_summary(evidence_path)
    pass_fail = dict(summary.get("pass_fail", {}))
    ratios = {
        key: (float(value) if isinstance(value, (int, float)) else None)
        for key, value in dict(summary.get("ratios", {})).items()
    }
    speed_credit_passed = bool(pass_fail.get("goal4681_speed_credit_pass"))
    return V4Goal4681ShapePairRelationResult(
        status=(
            "goal4681_material_speed_credit_passed_review_before_promotion"
            if speed_credit_passed
            else V4_GOAL4681_SHAPE_PAIR_RELATION_RESULT_STATUS
        ),
        source_evidence=str(evidence_path),
        decision_label=str(summary.get("decision_label", "")),
        correctness_passed=bool(pass_fail.get("correctness_companion_ok")),
        serious_active_count_parity=bool(pass_fail.get("serious_active_count_parity")),
        no_v4_host_row_stream_materialization=(
            pass_fail.get("v4_host_row_stream_materialization_in_hot_path") is False
        ),
        speed_credit_passed=speed_credit_passed,
        ratios=ratios,
    )


def validate_v4_goal4681_shape_pair_relation_result(
    evidence_path: str | Path = V4_GOAL4681_CANONICAL_EVIDENCE,
) -> dict[str, object]:
    result = v4_goal4681_shape_pair_relation_result(evidence_path)
    payload = result.as_dict()
    ratios = dict(payload["ratios"])
    missing: list[str] = []
    if payload["status"] != V4_GOAL4681_SHAPE_PAIR_RELATION_RESULT_STATUS:
        missing.append("status_expected_no_speed_credit")
    if payload["correctness_passed"] is not True:
        missing.append("correctness_passed")
    if payload["serious_active_count_parity"] is not True:
        missing.append("serious_active_count_parity")
    if payload["no_v4_host_row_stream_materialization"] is not True:
        missing.append("no_v4_host_row_stream_materialization")
    if payload["speed_credit_passed"] is not False:
        missing.append("speed_credit_false")
    if float(ratios.get("v4_hot_over_v2_14_same_primitive") or 0.0) >= 1.20:
        missing.append("unexpected_v2_hot_bar_pass")
    if float(ratios.get("v4_wall_over_v2_14_same_primitive") or 0.0) >= 1.10:
        missing.append("unexpected_v2_wall_bar_pass")
    for key in (
        "release_authorized",
        "promote_to_measured_catalog_authorized",
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "broad_v4_speedup_claim_authorized",
    ):
        if payload.get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "decision": payload,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4681_SHAPE_PAIR_RELATION_RESULT_STATUS",
    "V4_GOAL4681_CANONICAL_EVIDENCE",
    "V4Goal4681ShapePairRelationResult",
    "v4_goal4681_shape_pair_relation_result",
    "validate_v4_goal4681_shape_pair_relation_result",
]
