#!/usr/bin/env python3
"""Build Goal5424 post-Level-B blocker prioritization for X-HD."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5423 = RESULTS / "xhd_goal5423_level_b_matrix_consolidation_after_geo.json"
GOAL5309 = RESULTS / "xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json"
OUT = RESULTS / "xhd_goal5424_post_level_b_blocker_priority.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _service_summary(goal5309: dict[str, Any], key: str) -> dict[str, Any]:
    service = goal5309["services"][key]
    return {
        "paper_basename": service["paper_basename"],
        "classification": service["classification"],
        "paper_point_count": service["paper_point_count"],
        "observed_author_loader_point_count": service["author_loader_point_count"],
        "point_count_delta": service["point_count_delta"],
        "point_count_relative_delta": service["point_count_relative_delta"],
        "max_abs_mbr_delta": service["max_abs_mbr_delta"],
        "features_seen": service["features_seen"],
        "pages_seen": service["pages_seen"],
    }


def build_payload() -> dict[str, Any]:
    goal5423 = _load(GOAL5423)
    goal5309 = _load(GOAL5309)
    water = _service_summary(goal5309, "waterbodies")
    block = _service_summary(goal5309, "blockgroups")
    county = _service_summary(goal5309, "county")
    zcta = _service_summary(goal5309, "zcta")

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5424.post_level_b_blocker_priority.v1",
        "goal": "Goal5424",
        "status": "post_level_b_next_branch_selected__full_public_water_bg_feasibility_first__no_route_tuning",
        "matched": bool(goal5423["matched"]),
        "current_level_b_coverage": goal5423["coverage"],
        "decision": {
            "recommended_next_goal": "Goal5425_full_public_waterbodies_blockgroups_wkt_generation_feasibility",
            "technical_branch": "full_public_waterbodies_blockgroups_before_more_route_work",
            "route_micro_optimization": False,
            "explicit_lb": False,
            "county_zcta_full_public_now": False,
            "brats_now": False,
            "osm_now": False,
            "strict_review_packet_available": True,
        },
        "why_this_branch": [
            "Goal5423 already provides a Level-B same-POD matrix; the next full-reproduction blocker is dataset identity / full-public coverage, not another route timing column.",
            "Goal5309 shows WaterBodies and BlockGroups are the strongest full-public geo candidates by point-count and MBR proximity.",
            "County-ZCTA should not be the next full-public execution branch because County is +32.2% by author-loader point count.",
            "BraTS remains access/license blocked and OSM remains snapshot/filter blocked.",
            "Explicit -lb remains fail-closed under the stop-loss gate and is not a next branch.",
        ],
        "candidate_ranking": [
            {
                "rank": 1,
                "candidate": "full_public_waterbodies_blockgroups",
                "action": "feasibility_and_generation_plan_first",
                "services": {
                    "waterbodies": water,
                    "blockgroups": block,
                },
                "reason": (
                    "WaterBodies point count delta is +6,129 (+0.0269%) and "
                    "BlockGroups delta is +127 (+0.000243%); both MBR deltas "
                    "are below 1e-5 degrees. This is strong Level-B full-public "
                    "candidate evidence but not exact file/hash provenance."
                ),
                "claim_if_executed": "Level-B full-public geo candidate only",
            },
            {
                "rank": 2,
                "candidate": "alternate_county_source_or_simplification_search",
                "action": "investigate_before_full_public_execution",
                "services": {
                    "county": county,
                    "zcta": zcta,
                },
                "reason": (
                    "ZCTA is close, but County has +3,039,134 points (+32.2%), "
                    "so County-ZCTA cannot be promoted toward exact/Figure status "
                    "without an alternate County source or simplification match."
                ),
                "claim_if_executed": "source/provenance investigation only",
            },
            {
                "rank": 3,
                "candidate": "brats_2020",
                "action": "requires_access_or_license_before_execution",
                "reason": "Registration/license and author image-list provenance remain blocked.",
                "claim_if_executed": "not executable under current evidence",
            },
            {
                "rank": 4,
                "candidate": "osm_lakes_parks_allnodes",
                "action": "requires_snapshot_filter_conversion_plan_before_execution",
                "reason": "Public in principle but exact snapshot/filter/conversion parameters are unresolved.",
                "claim_if_executed": "not executable under current evidence",
            },
        ],
        "goal5425_requirements": {
            "must_not_run_author_or_rtdl_yet": True,
            "must_estimate_or_bound_wkt_size_and_disk": True,
            "must_define_resume_checkpoint_plan": True,
            "must_define_author_loader_semantics": True,
            "must_define_pod_upload_or_generation_location": True,
            "must_keep_claim_level": "Level-B full-public candidate, not exact paper input",
            "must_define_kill_conditions": [
                "generated point counts diverge materially from Goal5309 probe",
                "disk or runtime requirements exceed available POD resources",
                "ArcGIS service export cannot be made deterministic/reproducible",
            ],
        },
        "claim_boundary": {
            "level_b_same_pod_matrix_claimed": True,
            "next_branch_decision_claimed": True,
            "full_public_water_bg_execution_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "dataset_provenance_and_full_public_candidate_selection / no app-artifact parity work",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "pass_no_app_artifact_parity_work_authorized",
        },
        "source_artifacts": {
            "goal5423": str(GOAL5423),
            "goal5309": str(GOAL5309),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
