#!/usr/bin/env python3
"""Build Goal5425 feasibility plan for full-public WaterBodies->BlockGroups WKT."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5424 = RESULTS / "xhd_goal5424_post_level_b_blocker_priority.json"
GOAL5309 = RESULTS / "xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json"
GOAL5306_MANIFEST = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "data"
    / "generated"
    / "goal5306_arcgis_water_bg_bounded"
    / "manifest.json"
)
OUT = RESULTS / "xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _estimate(service: dict[str, Any], bounded: dict[str, Any]) -> dict[str, Any]:
    raw_path = ROOT / str(service["source_file"])
    raw = _load(raw_path)
    # The raw service files contain a single service entry keyed by the probe
    # service name.  Pull it without relying on the paper basename.
    raw_service = next(iter(raw["services"].values()))
    bounded_points = int(bounded["outer_ring_point_count_author_loader_estimate"])
    bounded_bytes = int(bounded["bytes"])
    full_points = int(service["author_loader_point_count"])
    bytes_per_point = bounded_bytes / float(bounded_points)
    estimated_bytes = int(round(bytes_per_point * full_points))
    return {
        "paper_basename": service["paper_basename"],
        "features": int(service["features_seen"]),
        "pages": int(service["pages_seen"]),
        "probe_elapsed_sec": float(raw_service["elapsed_sec"]),
        "author_loader_point_count": full_points,
        "paper_point_count": int(service["paper_point_count"]),
        "point_count_delta": int(service["point_count_delta"]),
        "point_count_relative_delta": float(service["point_count_relative_delta"]),
        "max_abs_mbr_delta": float(service["max_abs_mbr_delta"]),
        "bounded_bytes": bounded_bytes,
        "bounded_author_loader_points": bounded_points,
        "bounded_bytes_per_point": bytes_per_point,
        "estimated_full_wkt_bytes": estimated_bytes,
        "estimated_full_wkt_mib": estimated_bytes / (1024.0 * 1024.0),
        "estimated_full_wkt_gib": estimated_bytes / (1024.0 * 1024.0 * 1024.0),
    }


def build_payload() -> dict[str, Any]:
    goal5424 = _load(GOAL5424)
    goal5309 = _load(GOAL5309)
    bounded = _load(GOAL5306_MANIFEST)
    water = _estimate(goal5309["services"]["waterbodies"], bounded["outputs"]["waterbodies"])
    block = _estimate(goal5309["services"]["blockgroups"], bounded["outputs"]["blockgroups"])
    total_bytes = int(water["estimated_full_wkt_bytes"] + block["estimated_full_wkt_bytes"])
    safety_factor = 3.0
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5425.full_public_water_bg_wkt_generation_feasibility.v1",
        "goal": "Goal5425",
        "status": "full_public_water_bg_wkt_generation_feasible_with_checkpoint_gate__no_execution",
        "matched": bool(goal5424["matched"]),
        "selected_candidate": "full_public_waterbodies_blockgroups",
        "feasibility": {
            "author_or_rtdl_execution_claimed": False,
            "wkt_generation_executed": False,
            "full_public_candidate_level": "Level-B full-public candidate, not exact paper input",
            "estimated_total_wkt_bytes": total_bytes,
            "estimated_total_wkt_mib": total_bytes / (1024.0 * 1024.0),
            "estimated_total_wkt_gib": total_bytes / (1024.0 * 1024.0 * 1024.0),
            "recommended_free_disk_gib": (total_bytes * safety_factor) / (1024.0 * 1024.0 * 1024.0),
            "safety_factor": safety_factor,
            "estimated_generation_time_sec_from_probe_floor": (
                float(water["probe_elapsed_sec"]) + float(block["probe_elapsed_sec"])
            ),
            "estimated_generation_time_note": (
                "Probe time is a floor because full WKT generation must also format and write geometries."
            ),
        },
        "services": {
            "waterbodies": water,
            "blockgroups": block,
        },
        "generation_plan": {
            "next_goal": "Goal5426_full_public_water_bg_wkt_generation_dry_run_or_execute_if_resources_pass",
            "preferred_generation_location": "POD /tmp/xhd_goal5426/full_public_water_bg",
            "local_generation_allowed": False,
            "reason_for_pod_generation": (
                "Full WKT artifacts are large and the next author/RTDL gates run on POD; "
                "avoid local disk churn and upload costs if POD disk is sufficient."
            ),
            "checkpoint_files": [
                "USADetailedWaterBodies_full_public.checkpoint.json",
                "USACensusBlockGroupBoundaries_full_public.checkpoint.json",
            ],
            "output_files": [
                "USADetailedWaterBodies_full_public.wkt",
                "USACensusBlockGroupBoundaries_full_public.wkt",
                "manifest.json",
            ],
            "author_loader_semantics": {
                "input_type": "wkt",
                "n_dims": 2,
                "normalize": False,
                "one_geometry_per_line": True,
                "polygon_outer_ring_only_for_author_point_count": True,
                "close_polygon_outer_rings_if_needed": True,
                "ignore_holes": True,
            },
            "resource_preflight_required": [
                "POD wrapper preflight",
                "df -BG /tmp",
                "verify ArcGIS service reachability",
                "write permission for /tmp/xhd_goal5426/full_public_water_bg",
            ],
        },
        "kill_conditions": [
            {
                "condition": "free_disk_below_recommended_gib",
                "threshold_gib": (total_bytes * safety_factor) / (1024.0 * 1024.0 * 1024.0),
            },
            {
                "condition": "generated_author_loader_point_count_differs_from_goal5309_probe",
                "waterbodies_expected": water["author_loader_point_count"],
                "blockgroups_expected": block["author_loader_point_count"],
            },
            {
                "condition": "ArcGIS export becomes non-deterministic or service schema changes",
                "required_order": "OBJECTID",
                "required_out_sr": 4326,
            },
            {
                "condition": "generation cannot checkpoint/resume after interruption",
                "required": "atomic checkpoint and output writes",
            },
        ],
        "claim_boundary": {
            "feasibility_plan_claimed": True,
            "full_public_wkt_generated": False,
            "author_rtdl_correctness_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "route_micro_optimization_goal_authorized": False,
            "explicit_lb_reopened": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "dataset_generation_feasibility / no app-artifact parity work",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "pass_no_app_artifact_parity_work_authorized",
        },
        "source_artifacts": {
            "goal5424": str(GOAL5424),
            "goal5309": str(GOAL5309),
            "goal5306_manifest": str(GOAL5306_MANIFEST),
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
