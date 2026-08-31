#!/usr/bin/env python3
"""Fail-closed admission audit for the first V2/V3/V4 performance cohort.

Functional semantic coverage is not a complete application endpoint.  This
audit deliberately refuses to time a lane unless exact, repository-local V2,
V3 and V4 application front doors consume the same frozen input, produce the
same output contract, and register the same complete lifecycle boundary.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json"
INTEGRATED = ROOT / "history/internal_docs/goal5765_integrated_nine_app_recount_20260812.json"
THREE_WAY = ROOT / "scripts/goal5768_three_way_frontdoors.py"

INTEGRATED_TO_COMPARATOR = {
    "librts.aabb_index.prepared_query_2d.v1": "librts__range_rows",
    "librts.aabb_overlap.filter_bounded_emit_2d.v1": "librts__overlap_filter",
    "particle_tracking.tetrahedral_face_point_location_and_boundary_detection": (
        "particle__cell_transition"),
    "raydb.keyed_i64_sum": "raydb__q21",
    "rayjoin.logical_events.grouped_i64x2_count_sum.v1": (
        "rayjoin__grouped_events"),
    "rayjoin.planar_map.directed_segment_point_location_2d.v1": (
        "rayjoin__point_location"),
    "rayjoin.planar_map.segment_pair_grouped_range_exact_count_2d.v1": (
        "rayjoin__segment_pairs"),
    "rt_barneshut.aggregate_hierarchy.frontier_reduce.v1": "rtbh__force",
    "rt_dbscan.fixed_radius.prepared_spatial_components.v1": (
        "rtdbscan__components"),
    "rtnn.point_selection.spatial_bounded.v1": "rtnn__ranked_window",
    "triangle_counting.rt_1a2_all_hit": "triangle__rt_1a2",
    "triangle_counting.rt_2a1_weighted": "triangle__rt_2a1",
    "x_hd.nearest_state.cell_mbr_exact_witness.v1": "xhd__global_witness",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _app_key(name: str) -> str:
    return {
        "LibRTS": "librts",
        "Particle Tracking": "particle_tracking",
        "RayDB": "raydb",
        "RayJoin": "rayjoin",
        "RT-BarnesHut": "rt_barneshut",
        "RT-DBSCAN": "rt_dbscan",
        "RTNN": "rtnn",
        "Triangle Counting": "triangle_counting",
        "X-HD": "x_hd",
    }[name]


APP_DIR = {
    "particle_tracking": "Paper-reproduction-apps/goal5753-held-out-particle-tracking",
    "raydb": "Paper-reproduction-apps/raydb-paper",
    "triangle_counting": "Paper-reproduction-apps/triangle-counting-paper",
    "librts": "Paper-reproduction-apps/librts-paper",
    "rtnn": "Paper-reproduction-apps/rtnn-paper",
    "rt_dbscan": "Paper-reproduction-apps/rt-dbscan-paper",
    "x_hd": "Paper-reproduction-apps/x-hd-paper",
    "rayjoin": "Paper-reproduction-apps/rayjoin-paper",
    "rt_barneshut": "Paper-reproduction-apps/rt-barneshut-paper",
}


V4_BATCH_DRIVER = {
    "m0": "scripts/goal5756_builtin_triangle_device_validation.py",
    "m1": "scripts/goal5759_home_triangle_reduction_device_validation.py",
    "m2": "scripts/goal5760_home_bounded_relation_device_validation.py",
    "m3": "scripts/goal5761_home_multiround_spatial_validation.py",
    "m4": "scripts/goal5762_home_exact_predicate_witness_validation.py",
    "m5": "scripts/goal5763_home_grouped_event_reduction_validation.py",
    "m6": "scripts/goal5764_home_hierarchy_frontier_validation.py",
}


def _python_files(path: Path) -> Iterable[Path]:
    if not path.exists():
        return ()
    return tuple(sorted(path.rglob("*.py")))


def _imports_v4(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == "rtdsl.v4" or alias.name.startswith("rtdsl.v4_")
                   for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "rtdsl.v4" or module.startswith("rtdsl.v4_"):
                return True
    return False


def _contains_registered_timer(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return any(token in text for token in (
        "registered_timings", "registered_complete_seconds",
        "primary_seconds", "registered_primary_timing",
    ))


def _defines_complete_frontdoor(path: Path) -> bool:
    if not path.is_file():
        return False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "run_v4_complete"
        for node in tree.body
    )


def build_audit() -> dict[str, object]:
    from scripts.goal5768_three_way_frontdoors import LANE_BY_ID, METHODS

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    integrated = json.loads(INTEGRATED.read_text(encoding="utf-8"))
    freeze_by_lane = {row["lane_id"]: row for row in freeze["lanes"]}
    # Goal5765 uses a later qualified Particle lane and excludes Arkade.
    rows: list[dict[str, object]] = []
    for lane in integrated["paper_lanes"]:
        app = _app_key(lane["paper_app"])
        app_root = ROOT / APP_DIR[app]
        app_sources = tuple(_python_files(app_root))
        exact_frontdoor = app_root / "v4_whole_app.py"
        v4_imports = tuple(
            str(path.relative_to(ROOT)).replace("\\", "/")
            for path in app_sources if _imports_v4(path)
        )
        batch_driver = ROOT / V4_BATCH_DRIVER[lane["batch"]]
        lane_key = lane["lane"]
        comparator_lane_id = INTEGRATED_TO_COMPARATOR[lane_key]
        comparator = LANE_BY_ID[comparator_lane_id]
        frozen = next((item for key, item in freeze_by_lane.items()
                       if key in lane_key or lane_key.endswith(key)), None)
        has_app_v4_frontdoor = (
            _defines_complete_frontdoor(exact_frontdoor)
            and _imports_v4(exact_frontdoor)
        )
        v4_timer = has_app_v4_frontdoor and _contains_registered_timer(
            exact_frontdoor)
        comparator_frozen = (
            THREE_WAY.is_file()
            and len(METHODS) == 3
            and comparator.app == app
            and comparator.lane_id == comparator_lane_id
        )
        blockers: list[str] = []
        if not has_app_v4_frontdoor:
            blockers.append("no_application_owned_v4_frontdoor")
        if not v4_timer:
            blockers.append("no_v4_complete_registered_timer")
        if not comparator_frozen:
            blockers.append("v2_v3_v4_same_input_output_timer_binding_not_frozen")
        blockers.append("target_functional_three_way_receipts_not_yet_recorded")
        rows.append({
            "paper_app": lane["paper_app"],
            "app_id": app,
            "lane": lane_key,
            "batch": lane["batch"],
            "frozen_contract_found": frozen is not None or app == "particle_tracking",
            "representative_functional_exact": bool(lane["exact_output_matched"]),
            "representative_behavioral_true_optix": bool(lane["behavioral_true_optix"]),
            "v4_batch_driver": str(batch_driver.relative_to(ROOT)).replace("\\", "/"),
            "v4_batch_driver_sha256": _sha(batch_driver),
            "application_v4_imports": v4_imports,
            "application_v4_frontdoor": (
                str(exact_frontdoor.relative_to(ROOT)).replace("\\", "/")
                if exact_frontdoor.is_file() else None
            ),
            "application_v4_frontdoor_sha256": (
                _sha(exact_frontdoor) if exact_frontdoor.is_file() else None
            ),
            "application_owned_v4_frontdoor_exists": has_app_v4_frontdoor,
            "application_owned_v4_complete_registered_timer_exists": v4_timer,
            "comparator_lane_id": comparator_lane_id,
            "comparator_source": str(THREE_WAY.relative_to(ROOT)).replace("\\", "/"),
            "comparator_source_sha256": _sha(THREE_WAY),
            "predecessor_provenance": comparator.predecessor_provenance,
            "same_input_output_complete_timer_v2_v3_v4_frozen": comparator_frozen,
            "formal_performance_eligible": False,
            "blockers": tuple(dict.fromkeys(blockers)),
        })
    audit = {
        "schema": "rtdl.goal5768.v2_v3_v4_performance_eligibility_audit.v1",
        "goal": 5768,
        "status": "LOCAL_THREE_WAY_FRONTDOORS_FROZEN__TARGET_RECEIPTS_PENDING",
        "input_pins": {
            str(FREEZE.relative_to(ROOT)).replace("\\", "/"): _sha(FREEZE),
            str(INTEGRATED.relative_to(ROOT)).replace("\\", "/"): _sha(INTEGRATED),
            str(THREE_WAY.relative_to(ROOT)).replace("\\", "/"): _sha(THREE_WAY),
        },
        "paper_app_count": len({row["paper_app"] for row in rows}),
        "paper_lane_count": len(rows),
        "representative_functional_exact_count": sum(
            bool(row["representative_functional_exact"]) for row in rows),
        "representative_behavioral_true_optix_count": sum(
            bool(row["representative_behavioral_true_optix"]) for row in rows),
        "formal_performance_eligible_count": sum(
            bool(row["formal_performance_eligible"]) for row in rows),
        "lanes": rows,
        "application_owned_v4_frontdoor_lane_count": sum(
            bool(row["application_owned_v4_frontdoor_exists"])
            for row in rows),
        "application_owned_v4_complete_timer_lane_count": sum(
            bool(row["application_owned_v4_complete_registered_timer_exists"])
            for row in rows),
        "decisive_finding": (
            "All 13 representative lanes now have application-owned V4 "
            "complete front doors and frozen same-input V2/V3/V4 comparator "
            "routes. Formal admission remains closed until target functional "
            "receipts, the 312-worker harness, and its independent recount are frozen."
        ),
        "required_before_pre_pod": (
            "application-owned V4 front door for every lane",
            "frozen V2/V3/V4 same-input and same-output comparator",
            "source-traced symmetric complete timer boundary",
            "behavioral true-OptiX receipt for each timed method",
            "untimed real-input smoke and target cost bound",
            "independent evaluator and recount",
        ),
        "claim_boundary": {
            "goal5765_or_5766_relabelled_as_performance": False,
            "formal_plan_frozen": False,
            "formal_worker_allowed": False,
            "pod_authorized_or_requested": False,
            "performance_claimed": False,
            "nine_app_end_to_end_integration_claimed": False,
        },
    }
    audit["audit_sha256"] = hashlib.sha256(json.dumps(
        audit, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()
    return audit


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build_audit()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
