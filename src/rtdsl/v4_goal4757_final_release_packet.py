from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


V4_GOAL4757_STATUS = "ready_for_external_review_not_public_tag_authorized"
V4_GOAL4757_DECISION = "final_v4_0_release_packet_ready_after_goal4756_not_authorized"
V4_GOAL4757_LABEL = (
    "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim"
)


@dataclass(frozen=True)
class V4Goal4757FinalReleasePacket:
    status: str
    decision: str
    current_decision_label: str
    packet: str
    call_for_review: str
    review_debt: str
    matrix_analysis: str
    full_v4_test_log: str
    app_count: int
    matrix_row_count: int
    material_candidate_apps: tuple[str, ...]
    regression_apps: tuple[str, ...]
    v4_over_v2_14_hot_geomean: float
    embree_primary_denominator_used: bool
    release_authorized: bool
    public_tag_authorized: bool
    external_review_debt_open: bool
    forbidden_claims: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "decision": self.decision,
            "current_decision_label": self.current_decision_label,
            "packet": self.packet,
            "call_for_review": self.call_for_review,
            "review_debt": self.review_debt,
            "matrix_analysis": self.matrix_analysis,
            "full_v4_test_log": self.full_v4_test_log,
            "app_count": self.app_count,
            "matrix_row_count": self.matrix_row_count,
            "material_candidate_apps": self.material_candidate_apps,
            "regression_apps": self.regression_apps,
            "v4_over_v2_14_hot_geomean": self.v4_over_v2_14_hot_geomean,
            "embree_primary_denominator_used": self.embree_primary_denominator_used,
            "release_authorized": self.release_authorized,
            "public_tag_authorized": self.public_tag_authorized,
            "external_review_debt_open": self.external_review_debt_open,
            "forbidden_claims": self.forbidden_claims,
            "all_benchmark_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
            "barnes_hut_new_v4_over_v3_speedup_authorized": False,
            "spatial_rayjoin_speedup_authorized": False,
        }


def _repo(root: Path | None) -> Path:
    return root or Path(__file__).resolve().parents[2]


def v4_goal4757_final_release_packet(root: Path | None = None) -> dict[str, Any]:
    repo = _repo(root)
    matrix_analysis = "tools/_archive/future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json"
    analysis = json.loads((repo / matrix_analysis).read_text(encoding="utf-8"))
    summary = analysis["summary"]

    return V4Goal4757FinalReleasePacket(
        status=V4_GOAL4757_STATUS,
        decision=V4_GOAL4757_DECISION,
        current_decision_label=V4_GOAL4757_LABEL,
        packet="tools/_archive/future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md",
        call_for_review=(
            "tools/_archive/future/v4/reviews/"
            "call_for_review_v4_goal4757_final_v4_0_release_after_goal4756_2026-06-26.md"
        ),
        review_debt="tools/_archive/future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md",
        matrix_analysis=matrix_analysis,
        full_v4_test_log=(
            "tools/_archive/future/v4/evidence/"
            "v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log"
        ),
        app_count=int(summary["app_count"]),
        matrix_row_count=len(analysis["raw_rows"]),
        material_candidate_apps=tuple(summary["material_candidate_apps"]),
        regression_apps=tuple(summary["regression_apps"]),
        v4_over_v2_14_hot_geomean=float(summary["v4_over_v2_14_hot_geomean"]),
        embree_primary_denominator_used=bool(summary["embree_primary_denominator_used"]),
        release_authorized=False,
        public_tag_authorized=False,
        external_review_debt_open=True,
        forbidden_claims=(
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "app-specific native kernels",
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
            "LibRTS paper reproduction",
        ),
    ).as_dict()


def validate_v4_goal4757_final_release_packet(root: Path | None = None) -> dict[str, Any]:
    repo = _repo(root)
    decision = v4_goal4757_final_release_packet(repo)

    if decision["status"] != V4_GOAL4757_STATUS:
        raise ValueError("Goal4757 status drift")
    if decision["decision"] != V4_GOAL4757_DECISION:
        raise ValueError("Goal4757 decision drift")
    if decision["current_decision_label"] != V4_GOAL4757_LABEL:
        raise ValueError("Goal4757 decision label drift")
    for key in ("packet", "call_for_review", "review_debt", "matrix_analysis", "full_v4_test_log"):
        if not (repo / decision[key]).exists():
            raise ValueError(f"Goal4757 missing required artifact: {decision[key]}")

    packet_text = (repo / decision["packet"]).read_text(encoding="utf-8")
    call_text = (repo / decision["call_for_review"]).read_text(encoding="utf-8")
    debt_text = (repo / decision["review_debt"]).read_text(encoding="utf-8")
    log_text = (repo / decision["full_v4_test_log"]).read_text(encoding="utf-8")

    for required in (
        "V2/V3 superset",
        "complete NVIDIA RT-core app matrix",
        "30/30",
        "no `n/a` rows",
        "Embree is not used as a primary denominator",
        "Barnes-Hut new V4-over-V3 speedup",
        "Spatial RayJoin speedup",
        "does not by itself authorize",
        "public V4.0 tag",
    ):
        if required not in packet_text:
            raise ValueError(f"Goal4757 packet missing required text: {required}")
    for verdict in (
        "approve_v4_0_release_candidate_for_public_tag",
        "approve_with_required_wording_or_evidence_amendments",
        "block_release_pending_specific_fixes",
        "reject_release_reframe_required",
    ):
        if verdict not in call_text:
            raise ValueError(f"Goal4757 review request missing verdict: {verdict}")
    if "stdout_bytes=0" not in debt_text or "not a" not in debt_text or "review verdict" not in debt_text:
        raise ValueError("Goal4757 external review debt must record empty Antigravity result")
    if "Ran 601 tests" not in log_text or "OK" not in log_text:
        raise ValueError("Goal4757 full V4 unittest log must show the 601-test pass")

    if decision["app_count"] != 10:
        raise ValueError("Goal4757 app count drift")
    if decision["matrix_row_count"] != 30:
        raise ValueError("Goal4757 matrix row count drift")
    if set(decision["material_candidate_apps"]) != {"triangle_counting", "barnes_hut"}:
        raise ValueError("Goal4757 material candidate set drift")
    if decision["regression_apps"]:
        raise ValueError("Goal4757 must not carry hot-path regression apps")
    if decision["embree_primary_denominator_used"]:
        raise ValueError("Goal4757 must not use Embree as primary denominator")
    if abs(decision["v4_over_v2_14_hot_geomean"] - 2.100691970706828) > 1e-9:
        raise ValueError("Goal4757 V4/V2.14 hot geomean drift")
    if decision["release_authorized"] or decision["public_tag_authorized"]:
        raise ValueError("Goal4757 must not self-authorize public tag")
    if not decision["external_review_debt_open"]:
        raise ValueError("Goal4757 must keep external review debt open until verdicts arrive")
    for flag in (
        "all_benchmark_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "broad_v4_speedup_claim_authorized",
        "barnes_hut_new_v4_over_v3_speedup_authorized",
        "spatial_rayjoin_speedup_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4757 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4757_STATUS",
    "V4_GOAL4757_DECISION",
    "V4_GOAL4757_LABEL",
    "V4Goal4757FinalReleasePacket",
    "v4_goal4757_final_release_packet",
    "validate_v4_goal4757_final_release_packet",
]
