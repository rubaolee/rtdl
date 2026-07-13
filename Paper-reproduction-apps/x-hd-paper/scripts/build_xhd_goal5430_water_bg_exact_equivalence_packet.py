#!/usr/bin/env python3
"""Build Goal5430 Water/BG exact-equivalence review and artifact request packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5429 = RESULTS / "xhd_goal5429_exact_input_or_equivalence_decision_refresh.json"
GOAL5318 = RESULTS / "xhd_goal5318_water_bg_exact_provenance_search.json"
GOAL5309 = RESULTS / "xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json"
GOAL5314 = RESULTS / "xhd_goal5314_water_bg_corrected_comparison_summary.json"
OUT = RESULTS / "xhd_goal5430_water_bg_exact_equivalence_packet.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _service_summary(goal5318: dict[str, Any], goal5309: dict[str, Any], name: str) -> dict[str, Any]:
    arcgis = goal5318["arcgis_metadata"][name]
    candidate = goal5318["local_full_public_wkt_candidate"][name]
    probe = goal5309["services"][name]
    return {
        "paper_basename": candidate["paper_basename"],
        "service_item_id": arcgis["service_item_id"],
        "service_url": arcgis["service_url"],
        "item_title": arcgis["item"]["title"],
        "item_created_iso": arcgis["item"]["created_iso"],
        "item_modified_iso": arcgis["item"]["modified_iso"],
        "item_owner": arcgis["item"]["owner"],
        "item_size": arcgis["item"]["size"],
        "service_has_static_data": arcgis["service"].get("hasStaticData"),
        "layer_has_static_data": arcgis["layer"].get("hasStaticData"),
        "layer_data_last_edit_iso": arcgis["layer"].get("editingInfoIso", {}).get("dataLastEditDate"),
        "linked_layer_package_id": (arcgis.get("linked_layer_package") or {}).get("id"),
        "linked_layer_package_modified_iso": (arcgis.get("linked_layer_package") or {}).get("modified_iso"),
        "generated_wkt_sha256": candidate["sha256"],
        "generated_wkt_bytes": candidate["bytes"],
        "generated_author_loader_point_count": candidate["author_loader_point_count"],
        "paper_point_count": candidate["paper_point_count"],
        "point_count_delta": candidate["point_count_delta"],
        "point_count_relative_delta": candidate["relative_delta"],
        "mbr": candidate["mbr"],
        "paper_mbr": candidate["paper_mbr"],
        "mbr_delta": candidate["mbr_delta"],
        "max_abs_mbr_delta": probe["max_abs_mbr_delta"],
        "features_seen": candidate["features"],
        "geometry_types": probe["geometry_types"],
    }


def build_payload() -> dict[str, Any]:
    goal5429 = _load(GOAL5429)
    goal5318 = _load(GOAL5318)
    goal5309 = _load(GOAL5309)
    goal5314 = _load(GOAL5314)

    water = _service_summary(goal5318, goal5309, "waterbodies")
    blockgroups = _service_summary(goal5318, goal5309, "blockgroups")
    paper_config = goal5314["author"]["paper_config_rerun_n_points_cell_8"]
    rtdl = goal5314["rtdl"]["exact_witness"]
    tolerance = goal5314["tolerance_boundary"]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5430.water_bg_exact_equivalence_packet.v1",
        "goal": "Goal5430",
        "date": "2026-07-10",
        "status": "water_bg_exact_equivalence_packet_ready__await_external_decision_or_author_artifacts",
        "purpose": (
            "Prepare the WaterBodies->BlockGroups exact-equivalence review packet and "
            "author artifact/hash request after Goal5429.  This is an evidence/request "
            "packet, not a claim of exact paper reproduction."
        ),
        "source_decision": {
            "from_goal5429": goal5429["full_reproduction_decision"]["full_reproduction_next_blocker"],
            "route_micro_optimization_authorized": False,
            "explicit_lb_authorized": False,
            "pod_expected_now": False,
        },
        "case": {
            "case_id": "geo_water_bg_full_public_paper_config",
            "paper_pair": "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt",
            "input_identity_level": "level_b_full_public_same_source_geo_not_exact_file_hash",
            "paper_log_path_root": "/local/storage/shared/HDDatasets",
            "paper_config": {
                "num_points_cell": paper_config["num_points_per_cell"],
                "hd_result": paper_config["hd_result"],
                "matches_paper_log": paper_config["matches_paper_log"],
                "avg_time_ms": paper_config["avg_time_ms"],
            },
            "rtdl_exact_witness": {
                "hd_result_float64": rtdl["hd_result_float64"],
                "abs_diff_vs_author": rtdl["abs_diff_vs_author_paper_config"],
                "comparison_tolerance": 2e-6,
                "matched_with_declared_tolerance": rtdl["correctness_gate"],
                "per_source_witness_exact": rtdl["per_source_witness_exact"],
                "same_witness_float32_distance": goal5314["rtdl"]["witness_numeric_probe"][
                    "distance_float32_numpy"
                ],
                "route_sec": rtdl["route_sec"],
                "entrypoint_total_sec": rtdl["entrypoint_total_sec"],
            },
        },
        "public_reconstruction_evidence": {
            "waterbodies": water,
            "blockgroups": blockgroups,
            "summary": {
                "mbrs_match_paper_logs_with_small_delta": True,
                "waterbodies_point_count_delta": water["point_count_delta"],
                "waterbodies_relative_delta": water["point_count_relative_delta"],
                "blockgroups_point_count_delta": blockgroups["point_count_delta"],
                "blockgroups_relative_delta": blockgroups["point_count_relative_delta"],
                "author_paper_config_value_reproduced": True,
                "rtdl_matches_author_with_tolerance": True,
                "still_not_exact": True,
            },
        },
        "why_not_exact_yet": goal5429["current_best_exact_equivalence_candidate"]["why_not_exact_yet"],
        "author_artifact_request": {
            "recipient": "X-HD authors / artifact owner",
            "preferred_hash_algorithm": "sha256",
            "request_items": [
                "USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree.",
                "USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree.",
                "If files cannot be shared, exact source URLs, snapshot dates, export parameters, and conversion scripts sufficient to regenerate the paper-run WKT files.",
                "The exact command line or config for the paper-log run confirming num_points_cell=8 for this pair.",
                "Any preprocessing, simplification, precision, coordinate, or ring/vertex extraction policy used to produce the paper-run WKT inputs.",
            ],
            "request_message": (
                "We are reproducing the X-HD WaterBodies->BlockGroups case.  Our public ArcGIS "
                "reconstruction matches the paper-log scalar under the author paper config and "
                "RTDL matches the author rerun, but we cannot claim exact paper reproduction "
                "without the paper-run WKT files, hashes, or byte-identical regeneration details. "
                "Could you provide sha256 hashes or sufficient regeneration provenance for "
                "USADetailedWaterBodies.wkt and USACensusBlockGroupBoundaries.wkt?"
            ),
        },
        "external_exact_equivalence_review_packet": {
            "question": (
                "Can the current deterministic public ArcGIS reconstruction be accepted as "
                "exact-equivalent for a renamed bounded public-reconstruction claim, or must it "
                "remain Level-B same-source evidence?"
            ),
            "evidence_for_acceptance": [
                "Both services are public ArcGIS sources matching the paper pair names.",
                "WaterBodies and BlockGroups MBR deltas are under 1e-5 degrees.",
                "Point-count deltas are small relative to paper logs: +6129 WaterBodies and +127 BlockGroups.",
                "Author hd_exec with paper-config n_points_cell=8 reproduces the paper-log HDResult.",
                "RTDL exact-witness route matches the author paper-config rerun within 2e-6.",
                "Generated WKT sha256 values are recorded.",
            ],
            "evidence_against_acceptance": [
                "No author-provided WKT file hashes are available.",
                "No proof current ArcGIS services are the author's exact snapshot.",
                "No byte-identical regeneration proof exists.",
                "Point-count deltas are nonzero.",
                "Statistics and scalar agreement do not prove byte identity.",
            ],
            "allowed_review_outcomes": [
                "exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim",
                "bounded_public_reconstruction_only_keep_level_b",
                "not_accepted_keep_level_b",
            ],
            "recommended_default_without_external_acceptance": "bounded_public_reconstruction_only_keep_level_b",
        },
        "decision_matrix": [
            {
                "condition": "author WKT files or sha256 hashes acquired",
                "next": "run same-input author/RTDL verification and build denominator-aligned matrix",
                "pod_expected": True,
            },
            {
                "condition": "byte-identical regeneration path acquired",
                "next": "regenerate, record sha256, then run same-input author/RTDL verification",
                "pod_expected": True,
            },
            {
                "condition": "external exact-equivalence accepted",
                "next": "rename claim exactly and run bounded public-reconstruction matrix under accepted scope",
                "pod_expected": True,
            },
            {
                "condition": "no artifacts and no exact-equivalence acceptance",
                "next": "keep Water/BG at Level-B and do not claim Figure 5 or full paper reproduction",
                "pod_expected": False,
            },
        ],
        "claim_boundary": {
            "packet_claimed": True,
            "author_artifact_request_prepared": True,
            "exact_equivalence_review_packet_prepared": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "exact_equivalence_accepted_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "new_pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "author artifact/hash request and external exact-equivalence review packet; no app-artifact parity implementation",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: this is a provenance/review packet, not row/hash/offload-stream implementation work.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "POD is useful only after author artifacts, hashes, byte-identical regeneration, or external exact-equivalence acceptance changes the blocker.",
        },
        "recommended_next_goal": "Goal5431_wait_for_external_artifacts_or_review_decision_then_run_same_input_gate_if_available",
        "allowed_summary": (
            "Goal5430 prepares the WaterBodies->BlockGroups exact-equivalence review packet and author artifact/hash request. "
            "It makes the strongest Level-B public reconstruction evidence actionable while keeping exact paper, Figure 5, full paper, and ratio claims closed."
        ),
        "not_allowed": [
            "claiming exact paper WKT files were recovered",
            "claiming current ArcGIS exports are byte-identical to author inputs",
            "claiming exact-equivalence acceptance before review",
            "claiming geo Figure 5 reproduction",
            "claiming full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
            "reopening explicit -lb or row identity work",
            "starting route micro-optimization as paper-reproduction progress",
        ],
        "source_artifacts": {
            "goal5429": str(GOAL5429),
            "goal5318": str(GOAL5318),
            "goal5309": str(GOAL5309),
            "goal5314": str(GOAL5314),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "recommended_next_goal": payload["recommended_next_goal"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
