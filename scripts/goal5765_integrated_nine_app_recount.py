#!/usr/bin/env python3
"""Route-independent integration recount for the Goal5765 nine-app matrix.

This program deliberately imports no RTDL product, compiler, paper-app, or
primary validation module.  It treats the seven raw result documents and the
six independently-produced batch recounts as untrusted input, rechecks the
physical receipts and fixed lane inventory, and writes one integration record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PAPER_LANES = {
    "particle_tracking.tetrahedral_face_point_location_and_boundary_detection": "Particle Tracking",
    "raydb.keyed_i64_sum": "RayDB",
    "triangle_counting.rt_1a2_all_hit": "Triangle Counting",
    "triangle_counting.rt_2a1_weighted": "Triangle Counting",
    "librts.aabb_index.prepared_query_2d.v1": "LibRTS",
    "librts.aabb_overlap.filter_bounded_emit_2d.v1": "LibRTS",
    "rtnn.point_selection.spatial_bounded.v1": "RTNN",
    "rt_dbscan.fixed_radius.prepared_spatial_components.v1": "RT-DBSCAN",
    "x_hd.nearest_state.cell_mbr_exact_witness.v1": "X-HD",
    "rayjoin.planar_map.directed_segment_point_location_2d.v1": "RayJoin",
    "rayjoin.planar_map.segment_pair_grouped_range_exact_count_2d.v1": "RayJoin",
    "rayjoin.logical_events.grouped_i64x2_count_sum.v1": "RayJoin",
    "rt_barneshut.aggregate_hierarchy.frontier_reduce.v1": "RT-BarnesHut",
}

NONPAPER_LANES = {
    "polygon_set_jaccard.aabb_candidate_stage.v1",
    "polygon_set_jaccard.grouped_overlap_incidence.v1",
    "hierarchical_spatial_coverage.aggregate_count.v1",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _receipt_ok(receipt: dict, native_sha: str) -> bool:
    snap = receipt["native_snapshot"]
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and receipt["provider_library_sha256"] == native_sha
        and int(snap["successful_launch_count"]) > 0
        and snap["successful_launch_count"] == snap["complete_context_launch_count"]
        and snap["attempted_launch_count"] == snap["successful_launch_count"]
        and int(snap["failed_launch_count"]) == 0
        and int(snap["incomplete_context_launch_count"]) == 0
        and int(snap["incomplete_callsite_record_count"]) == 0
        and int(snap["pending_context_at_finish"]) == 0
        and int(snap["session_error"]) == 0
        and int(snap["first_traversable"]) != 0
        and int(snap["last_traversable"]) != 0
        and int(snap["raygen_invocation_count"]) > 0
        and bool(receipt["expected_program_observed_at_receipt_edge"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--recount-root", required=True, type=Path)
    parser.add_argument("--source-archive", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    raw_paths = {
        "m0": args.raw_root / "m0_particle_tracking/RESULT.json",
        "m1": args.raw_root / "m1_triangle_reduction/RESULT.json",
        "m2": args.raw_root / "m2_bounded_relation/RESULT.json",
        "m3": args.raw_root / "m3_multiround_spatial/RESULT.json",
        "m4": args.raw_root / "m4_exact_predicate/RESULT.json",
        "m5": args.raw_root / "m5_grouped_events/RESULT.json",
        "m6": args.raw_root / "m6_hierarchy/RESULT.json",
    }
    raw = {key: _load(path) for key, path in raw_paths.items()}
    native_sha = _sha(args.native)

    # M0 is a historical coverage lane supported by Goal5756.  It must not be
    # relabelled as a pass of the immutable Goal5753 held-out exam.
    m0 = raw["m0"]
    if m0["device_output"] != m0["cpu_output"]:
        raise RuntimeError("M0 CPU/device output mismatch")
    if not m0["claims"]["cpu_device_differential_exact"]:
        raise RuntimeError("M0 exact differential missing")
    if m0["claims"]["held_out_generalization_claimed"]:
        raise RuntimeError("Goal5753 held-out failure was relabelled")
    if m0["native_library_sha256"] != native_sha:
        raise RuntimeError("M0 native identity mismatch")
    if not _receipt_ok(m0["traversal_receipt"], native_sha):
        raise RuntimeError("M0 behavioral traversal receipt failed")

    observed: dict[str, dict] = {
        "particle_tracking.tetrahedral_face_point_location_and_boundary_detection": {
            "paper_app": "Particle Tracking",
            "batch": "m0",
            "exact_output_matched": True,
            "behavioral_true_optix": True,
            "output_sha256": m0["output_sha256"],
        }
    }
    all_lane_names = set()
    for batch in ("m1", "m2", "m3", "m4", "m5", "m6"):
        result = raw[batch]
        if int(result["registered_performance_timing_count"]) != 0:
            raise RuntimeError(f"{batch} registered performance timing")
        for lane in result["lanes"]:
            lane_name = lane["lane"]
            if lane_name in all_lane_names:
                raise RuntimeError(f"duplicate lane {lane_name}")
            all_lane_names.add(lane_name)
            if not lane["exact_output_matched"]:
                raise RuntimeError(f"inexact lane {lane_name}")
            if not _receipt_ok(lane["traversal_receipt"], native_sha):
                raise RuntimeError(f"invalid traversal receipt {lane_name}")
            lane_native = lane.get("native_library_sha256", native_sha)
            if lane_native != native_sha:
                raise RuntimeError(f"native mismatch {lane_name}")
            if lane_name in PAPER_LANES:
                observed[lane_name] = {
                    "paper_app": PAPER_LANES[lane_name],
                    "batch": batch,
                    "exact_output_matched": True,
                    "behavioral_true_optix": True,
                    "output_sha256": lane["output_sha256"],
                }

    expected_all = set(PAPER_LANES) - {
        "particle_tracking.tetrahedral_face_point_location_and_boundary_detection"
    }
    if all_lane_names != expected_all | NONPAPER_LANES:
        raise RuntimeError(
            f"raw lane inventory mismatch: missing={sorted((expected_all | NONPAPER_LANES) - all_lane_names)!r}, "
            f"extra={sorted(all_lane_names - (expected_all | NONPAPER_LANES))!r}"
        )
    if set(observed) != set(PAPER_LANES):
        raise RuntimeError("paper lane inventory did not close 13/13")
    if set(PAPER_LANES.values()) != {
        "Particle Tracking", "RayDB", "Triangle Counting", "LibRTS", "RTNN",
        "RT-DBSCAN", "X-HD", "RayJoin", "RT-BarnesHut",
    }:
        raise AssertionError("paper app inventory is not nine")

    recount_paths = {
        batch: args.recount_root / f"goal5765_{batch}_recount_20260812.json"
        for batch in ("m1", "m2", "m3", "m4", "m5", "m6")
    }
    recounts = {key: _load(path) for key, path in recount_paths.items()}
    for batch, recount in recounts.items():
        if int(recount["lane_count"]) != len(raw[batch]["lanes"]):
            raise RuntimeError(f"{batch} recount lane count mismatch")
        if recount.get("native_library_sha256", native_sha) != native_sha:
            raise RuntimeError(f"{batch} recount native mismatch")
        raw_key = "raw_sha256" if batch == "m6" else (
            "result_sha256" if batch == "m5" else "raw_result_sha256")
        if recount[raw_key] != _sha(raw_paths[batch]):
            raise RuntimeError(f"{batch} recount raw binding mismatch")
        if recount.get("verdict", "pass") != "pass":
            raise RuntimeError(f"{batch} recount failed")

    result = {
        "schema": "rtdl.goal5765.integrated_nine_app_recount.v1",
        "goal": 5765,
        "scope": "functional_only_no_registered_performance_timing",
        "source_archive_sha256": _sha(args.source_archive),
        "native_library_sha256": native_sha,
        "paper_app_count": 9,
        "paper_lane_count": 13,
        "paper_lanes_exact_count": 13,
        "paper_lanes_behavioral_true_optix_count": 13,
        "nonpaper_second_consumer_lane_count": 3,
        "raw_lane_count": 16,
        "native_identity_count": 1,
        "registered_performance_timing_count": 0,
        "imports_product_compiler_runtime_or_paper_app": False,
        "goal5753_held_out_failure_relabelled": False,
        "goal5756_current_particle_coverage_used": True,
        "paper_lanes": [
            {"lane": name, **observed[name]} for name in sorted(observed)
        ],
        "raw_results": {
            key: {"path": str(path).replace("\\", "/"), "sha256": _sha(path)}
            for key, path in raw_paths.items()
        },
        "batch_recounts": {
            key: {"path": str(path).replace("\\", "/"), "sha256": _sha(path)}
            for key, path in recount_paths.items()
        },
        "claim_boundary": {
            "nine_app_functional_coverage_claimed": True,
            "performance_claimed": False,
            "modern_rtx_claimed": False,
            "rt_silicon_claimed": False,
            "public_production_submission_claimed": False,
            "pod_used_or_authorized": False,
        },
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "paper_apps": 9, "paper_lanes": 13, "exact": 13,
        "behavioral_true_optix": 13, "native": native_sha,
        "source": result["source_archive_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
