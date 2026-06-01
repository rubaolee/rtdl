#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _maybe_load(path: Path) -> dict[str, Any] | None:
    return _load(path) if path.exists() else None


def _round(value: Any, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _max(values: list[float]) -> float | None:
    return max(values) if values else None


def _min(values: list[float]) -> float | None:
    return min(values) if values else None


def _status(problem: bool) -> str:
    return "performance_target" if problem else "current_path_acceptable"


def _triangle(path: Path) -> dict[str, Any]:
    data = _load(path)
    rows = data.get("rows", [])
    query_ms = [float(row["query_median_ms"]) for row in rows if "query_median_ms" in row]
    return {
        "app": "triangle_counting",
        "status": data.get("status"),
        "performance_status": "current_path_acceptable",
        "route": "primitive_first_optix_summary",
        "row_count": len(rows),
        "max_query_median_ms": _round(_max(query_ms), 3),
        "claim_boundary": "canonical app harness; no public speedup claim",
        "next_action": "keep primitive-first; add partner only for row-stream/compact-mask continuations",
    }


def _librts(path: Path) -> dict[str, Any]:
    data = _load(path)
    rows = data.get("rows", [])
    query_ms = [float(row["query_median_ms"]) for row in rows if "query_median_ms" in row]
    max_query_ms = _max(query_ms)
    cpu_ref = float(data.get("cpu_reference_sec", 0.0) or 0.0)
    ratio = None
    if max_query_ms and max_query_ms > 0:
        ratio = cpu_ref / (max_query_ms / 1000.0)
    return {
        "app": "librts_spatial_index",
        "status": data.get("status"),
        "performance_status": "tier_c_no_regression",
        "route": "primitive_first_prepared_aabb_index_query_2d",
        "max_query_median_ms": _round(max_query_ms, 3),
        "cpu_reference_sec": _round(cpu_ref),
        "cpu_over_max_query_ratio": _round(ratio, 3),
        "claim_boundary": "Tier C no-regression; no partner parity claim",
        "next_action": "keep as RT-core prepared AABB no-regression baseline",
    }


def _rayjoin(path: Path) -> dict[str, Any]:
    data = _load(path)
    rows = data.get("rows", [])
    query_ms = []
    workloads = []
    for row in rows:
        workloads.append(row.get("workload"))
        med = (row.get("phase_medians_ms") or {}).get("prepared_query_sec")
        if med is not None:
            query_ms.append(float(med))
    return {
        "app": "spatial_rayjoin",
        "status": data.get("status"),
        "performance_status": "current_path_acceptable_but_rows_overlay_deferred",
        "route": "primitive_first_prepared_count_or_parity",
        "workloads": workloads,
        "max_prepared_query_ms": _round(_max(query_ms), 6),
        "claim_boundary": "count/parity only; row/overlay continuation deferred",
        "next_action": "do not force Triton for count/parity; future work is row/overlay device continuation",
    }


def _rtnn(path: Path) -> dict[str, Any]:
    data = _load(path)
    rows = data.get("rows", [])
    ratios = [float(row["cupy_grid_over_rtdl_elapsed_ratio"]) for row in rows]
    weak = [row.get("distribution") for row in rows if float(row["cupy_grid_over_rtdl_elapsed_ratio"]) < 1.0]
    return {
        "app": "rtnn",
        "status": data.get("status"),
        "performance_status": _status(bool(weak)),
        "severity_ratio": _round((1.0 / min(ratios)) if weak and min(ratios) > 0 else 1.0, 3),
        "route": "optix_prepared_ranked_summary_aggregate_vs_cupy_grid",
        "min_cupy_over_rtdl_ratio": _round(_min(ratios), 3),
        "max_cupy_over_rtdl_ratio": _round(_max(ratios), 3),
        "weak_distributions": weak,
        "claim_boundary": "Tier B same-contract opponent; distribution dependent",
        "next_action": (
            "if weak distributions remain, tune packed/prepared column input and distribution-aware query batching"
            if weak
            else "keep current ranked-summary route green"
        ),
    }


def _hausdorff(path: Path) -> dict[str, Any]:
    data = _load(path)
    ratio = float(data.get("rtdl_over_cupy_grid_elapsed_ratio", 0.0) or 0.0)
    return {
        "app": "hausdorff_xhd",
        "status": data.get("status"),
        "performance_status": _status(ratio > 1.0),
        "severity_ratio": _round(ratio if ratio > 1.0 else 1.0, 3),
        "route": "rtdl_rt_grouped_adaptive_nearest_witness_vs_cupy_grid_rawkernel",
        "rtdl_over_cupy_ratio": _round(ratio, 3),
        "rtdl_median_sec": _round((data.get("rtdl") or {}).get("median_elapsed_sec")),
        "cupy_median_sec": _round((data.get("baseline") or {}).get("median_elapsed_sec")),
        "claim_boundary": "exact RTDL/OptiX path; no claim to beat optimized CuPy grid",
        "next_action": "largest current performance target: reduce adaptive RT threshold iterations or add fused tiled nearest-witness continuation",
    }


def _dbscan(path: Path) -> dict[str, Any]:
    data = _load(path)
    return {
        "app": "rt_dbscan",
        "status": data.get("status"),
        "performance_status": "current_path_acceptable",
        "route": "optix_grouped_stream_plus_cupy_components",
        "min_speedup_vs_prepared_cupy_grid": _round(data.get("min_grouped_stream_speedup_vs_prepared_cupy_grid"), 3),
        "max_speedup_vs_prepared_cupy_grid": _round(data.get("max_grouped_stream_speedup_vs_prepared_cupy_grid"), 3),
        "claim_boundary": "grouped stream continuation evidence; no paper reproduction claim",
        "next_action": "keep grouped stream; pure Triton components remain blocked until same-contract win",
    }


def _barnes(path: Path) -> dict[str, Any]:
    data = _load(path)
    vector = data.get("vector_sum", {})
    triton_over_torch = float(vector.get("triton_over_torch_ratio", 0.0) or 0.0)
    return {
        "app": "barnes_hut",
        "status": data.get("status"),
        "performance_status": _status(triton_over_torch > 1.0),
        "severity_ratio": _round(triton_over_torch if triton_over_torch > 1.0 else 1.0, 3),
        "route": "optix_membership_plus_partner_vector_sum",
        "max_optix_membership_speedup_vs_embree": _round(data.get("max_optix_membership_speedup_vs_embree"), 3),
        "triton_over_torch_vector_sum_ratio": _round(triton_over_torch, 3),
        "claim_boundary": "membership/vector-sum harness; Triton vector path not promoted",
        "next_action": "do not auto-select Triton vector sum; optimize segmented/block vector reduction or keep Torch/CuPy partner",
    }


def _raydb(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {
            "app": "raydb_style",
            "status": "not_indexed_in_current_packet",
            "performance_status": "covered_by_goal2896_external_gate",
            "route": "primitive_first_fused_grouped_reduction",
            "next_action": "keep Goal2896 gate current; external review and compiler/second-arch cautions remain",
        }
    data = _load(path)
    slowdowns = [
        float(row["prepared_hit_stream_triton_slowdown_vs_primitive_first"])
        for row in data.get("comparisons", [])
    ]
    return {
        "app": "raydb_style",
        "status": data.get("status"),
        "performance_status": "current_path_acceptable",
        "route": "primitive_first_fused_grouped_reduction",
        "min_hit_stream_triton_slowdown_vs_primitive_first": _round(_min(slowdowns), 3),
        "max_hit_stream_triton_slowdown_vs_primitive_first": _round(_max(slowdowns), 3),
        "claim_boundary": "internal decision gate only; no public speedup claim",
        "next_action": "primitive-first for exact fused reductions; hit-stream partner for unfused continuations",
    }


def analyze(packet_dir: Path, *, raydb_gate: Path | None = None) -> dict[str, Any]:
    summary = _load(packet_dir / "goal2855_summary.json")
    apps = [
        _raydb(raydb_gate),
        _triangle(packet_dir / "goal2797_triangle_counting.json"),
        _librts(packet_dir / "goal2798_librts.json"),
        _rayjoin(packet_dir / "goal2799_spatial_rayjoin.json"),
        _rtnn(packet_dir / "goal2800_rtnn.json"),
        _hausdorff(packet_dir / "goal2801_hausdorff_xhd.json"),
        _dbscan(packet_dir / "goal2802_rt_dbscan.json"),
        _barnes(packet_dir / "goal2803_barnes_hut.json"),
        {
            "app": "contact_manifold",
            "status": "tier_c_not_in_seven_app_packet",
            "performance_status": "tier_c_no_regression",
            "route": "prepared_bounded_witness_collection",
            "claim_boundary": "no partner parity claim",
            "next_action": "measure no-regression only unless exact refinement is partnerized",
        },
        {
            "app": "robot_collision",
            "status": "tier_c_not_in_seven_app_packet",
            "performance_status": "tier_c_no_regression",
            "route": "prepared_anyhit_pose_flag",
            "claim_boundary": "no partner parity claim",
            "next_action": "keep prepared RT any-hit no-regression track",
        },
    ]
    targets = [
        app for app in apps if str(app.get("performance_status")).startswith("performance_target")
    ]
    targets = sorted(targets, key=lambda app: float(app.get("severity_ratio", 1.0)), reverse=True)
    return {
        "goal": "Goal2902 v2.5 current packet performance triage",
        "status": "pass" if summary.get("all_pass") is True else "fail",
        "source_commit": summary.get("source_commit"),
        "gpu": summary.get("gpu") or (summary.get("runner_metadata") or {}).get("gpu"),
        "packet_elapsed_sec": _round(summary.get("elapsed_sec"), 3),
        "artifact_count": summary.get("artifact_count"),
        "claim_boundary_violations": summary.get("claim_boundary_violations"),
        "apps": apps,
        "performance_targets": targets,
        "top_priority": targets[0]["app"] if targets else None,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", required=True, type=Path)
    parser.add_argument("--raydb-gate", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    result = analyze(args.packet_dir, raydb_gate=args.raydb_gate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"[goal2902] status={result['status']} apps={len(result['apps'])} "
        f"targets={len(result['performance_targets'])} output={args.output}",
        flush=True,
    )
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
