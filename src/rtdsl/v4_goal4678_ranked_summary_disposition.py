from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


V4_GOAL4678_RANKED_SUMMARY_DISPOSITION_STATUS = (
    "goal4678_defer_ranked_summary_no_open_candidate_no_release"
)
V4_GOAL4678_CANONICAL_EVIDENCE = (
    "future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json"
)


@dataclass(frozen=True)
class V4Goal4678RankedSummaryDisposition:
    status: str
    deferred: bool
    removed_from_candidate_frontdoor: bool
    surface: str
    generic_primitive: str
    source_evidence: str
    decision_label: str
    serious_scale_ratios: dict[str, dict[str, float]]
    release_authorized: bool = False
    broad_v4_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    public_speedup_claim_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "deferred": self.deferred,
            "removed_from_candidate_frontdoor": self.removed_from_candidate_frontdoor,
            "surface": self.surface,
            "generic_primitive": self.generic_primitive,
            "source_evidence": self.source_evidence,
            "decision_label": self.decision_label,
            "serious_scale_ratios": self.serious_scale_ratios,
            "release_authorized": self.release_authorized,
            "broad_v4_speedup_claim_authorized": self.broad_v4_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
        }


def _load_summary(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_ranked_summary_no_go(summary: Mapping[str, Any]) -> dict[str, object]:
    missing: list[str] = []
    decision = dict(summary.get("decision", {}))
    if decision.get("label") != "rtnn_candidate_does_not_move_app_level_bar":
        missing.append("decision_label")
    if decision.get("may_count_as_formal_high_performance_v4_evidence") is not False:
        missing.append("may_count_false")
    if decision.get("may_trigger_full_all_app_rerun") is not False:
        missing.append("may_trigger_all_app_false")

    rows = {int(row["point_count"]): row for row in summary.get("scales", ())}
    for point_count in (262144, 1048576):
        row = rows.get(point_count)
        if not row:
            missing.append(f"scale_{point_count}")
            continue
        if float(row.get("speedup_hot_median_v4_over_v2_14", 0.0)) >= 1.01:
            missing.append(f"scale_{point_count}_v2_ratio_below_material")
        if float(row.get("speedup_hot_median_v4_over_v3_0_2", 0.0)) >= 1.01:
            missing.append(f"scale_{point_count}_v3_ratio_below_material")
        candidate = dict(row.get("v4_candidate_route", {}))
        if candidate.get("validation_passed") is not True:
            missing.append(f"scale_{point_count}_validation")
        if candidate.get("runtime_executed") is not True:
            missing.append(f"scale_{point_count}_runtime_executed")
        if candidate.get("hot_path_host_materialization") is not False:
            missing.append(f"scale_{point_count}_no_hot_host_materialization")

    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "release_authorized": False,
    }


def v4_goal4678_ranked_summary_disposition(
    evidence_path: str | Path = V4_GOAL4678_CANONICAL_EVIDENCE,
) -> V4Goal4678RankedSummaryDisposition:
    summary = _load_summary(evidence_path)
    validation = validate_ranked_summary_no_go(summary)
    rows = {int(row["point_count"]): row for row in summary.get("scales", ())}
    serious_scale_ratios = {
        str(point_count): {
            "v4_over_v2_14_hot": float(rows[point_count]["speedup_hot_median_v4_over_v2_14"]),
            "v4_over_v3_0_2_hot": float(rows[point_count]["speedup_hot_median_v4_over_v3_0_2"]),
        }
        for point_count in (262144, 1048576)
        if point_count in rows
    }
    decision = dict(summary.get("decision", {}))
    passed = validation["status"] == "passed"
    return V4Goal4678RankedSummaryDisposition(
        status=(
            V4_GOAL4678_RANKED_SUMMARY_DISPOSITION_STATUS
            if passed
            else "goal4678_reopen_ranked_summary_evidence"
        ),
        deferred=passed,
        removed_from_candidate_frontdoor=passed,
        surface="v4_fixed_radius_ranked_summary_3d_prepared_runner",
        generic_primitive="FIXED_RADIUS_RANKED_SUMMARY_3D",
        source_evidence=str(evidence_path),
        decision_label=str(decision.get("label", "")),
        serious_scale_ratios=serious_scale_ratios,
    )


def validate_v4_goal4678_ranked_summary_disposition(
    evidence_path: str | Path = V4_GOAL4678_CANONICAL_EVIDENCE,
) -> dict[str, object]:
    decision = v4_goal4678_ranked_summary_disposition(evidence_path)
    missing: list[str] = []
    if not decision.deferred:
        missing.append("deferred")
    if not decision.removed_from_candidate_frontdoor:
        missing.append("removed_from_candidate_frontdoor")
    for key in (
        "release_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "public_speedup_claim_authorized",
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
    "V4_GOAL4678_RANKED_SUMMARY_DISPOSITION_STATUS",
    "V4_GOAL4678_CANONICAL_EVIDENCE",
    "V4Goal4678RankedSummaryDisposition",
    "validate_ranked_summary_no_go",
    "v4_goal4678_ranked_summary_disposition",
    "validate_v4_goal4678_ranked_summary_disposition",
]
