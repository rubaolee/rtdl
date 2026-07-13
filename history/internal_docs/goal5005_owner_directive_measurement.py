#!/usr/bin/env python3
"""Goal5005 measurement: enforce owner directive after Goal4997-5004 review.

Runs independent fresh processes for the fast-pack and device-resident routes,
then computes both the current writer_free_hot_sec and the pre-fix accounting
value from the same phase_seconds. This isolates accounting delta from run
variance.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path


OLD_DEVICE_RESIDENT_WRITER_KEYS = [
    "lsi_bounded_exact_pair_id_device_columns_sec",
    "",
    "intersection_reprojection_device_columnar_sec",
    "sort_map0_device_columnar_sec",
    "sort_map1_device_columnar_sec",
    "vertex_pip_map0_in_map1_sec",
    "vertex_pip_map1_in_map0_sec",
    "midpoint_points_map0_columnar_sec",
    "midpoint_points_map1_columnar_sec",
    "midpoint_pip_map0_sec",
    "midpoint_pip_map1_sec",
    "assign_midpoint_faces_map0_device_scatter_sec",
    "assign_midpoint_faces_map1_device_scatter_sec",
    "device_resident_carrier_construction_sec",
    "device_resident_descriptor_pair_count_consumer_sec",
]


def _sum_keys(phase_seconds: dict[str, object], keys: list[str]) -> float:
    total = 0.0
    for key in keys:
        if key:
            total += float(phase_seconds.get(key, 0.0))
    return total


def _stats(values: list[float]) -> dict[str, float | int | list[float]]:
    clean = [float(value) for value in values]
    return {
        "count": len(clean),
        "median": statistics.median(clean),
        "min": min(clean),
        "max": max(clean),
        "range": max(clean) - min(clean),
        "mean": statistics.fmean(clean),
        "pstdev": statistics.pstdev(clean) if len(clean) > 1 else 0.0,
        "values": clean,
    }


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def _route_summary(path: Path, *, accounting_mode: str) -> dict[str, object]:
    summary = _load(path)
    phase_seconds = summary.get("phase_seconds", {})
    if not isinstance(phase_seconds, dict):
        phase_seconds = {}
    current = float(summary["writer_free_hot_sec"])
    old = None
    accounting_delta = None
    if accounting_mode == "device_resident":
        old = _sum_keys(phase_seconds, OLD_DEVICE_RESIDENT_WRITER_KEYS)
        accounting_delta = current - old
    floor = summary.get("downstream_floor_breakdown", {})
    if not isinstance(floor, dict):
        floor = {}
    consumer = summary.get("downstream_consumer", {})
    if not isinstance(consumer, dict):
        consumer = {}
    return {
        "path": str(path),
        "writer_free_hot_sec": current,
        "old_prefix_writer_free_hot_sec": old,
        "accounting_delta_sec": accounting_delta,
        "lsi_phase_sec": float(floor.get("lsi_phase_sec", 0.0)),
        "downstream_floor_sec": float(floor.get("downstream_floor_sec", 0.0)),
        "recomputed_writer_free_sec": float(floor.get("writer_free_hot_recomputed_sec", 0.0)),
        "lsi_row_count": int(summary.get("lsi_row_count", 0)),
        "descriptor_pair_count": int(consumer.get("pair_count", 0)),
        "phase_seconds": {
            key: float(value)
            for key, value in phase_seconds.items()
            if key
            in {
                "lsi_bounded_exact_pair_id_device_columns_sec",
                "intersection_reprojection_device_columnar_sec",
                "sort_map0_device_columnar_sec",
                "sort_map1_device_columnar_sec",
                "midpoint_points_map0_columnar_sec",
                "midpoint_points_map1_columnar_sec",
                "midpoint_points_map0_device_query_points_sec",
                "midpoint_points_map1_device_query_points_sec",
                "device_resident_carrier_construction_sec",
                "grouped_compiled_columnar_carrier_construction_sec",
                "device_resident_descriptor_pair_count_consumer_sec",
                "grouped_descriptor_pair_count_consumer_sec",
            }
        },
    }


def _repeat_summary(path: Path) -> dict[str, object]:
    summary = _load(path)
    measured = summary.get("measured_rows", [])
    if not isinstance(measured, list):
        measured = []
    rows = []
    for row in measured:
        if isinstance(row, dict):
            rows.append(
                {
                    "writer_free_hot_sec": float(row["writer_free_hot_sec"]),
                    "lsi_phase_sec": float(row["lsi_phase_sec"]),
                    "downstream_floor_sec": float(row["downstream_floor_sec"]),
                    "lsi_row_count": int(row["lsi_row_count"]),
                    "descriptor_pair_count": int(row["descriptor_pair_count"]),
                    "key_phase_seconds": row.get("key_phase_seconds", {}),
                }
            )
    return {
        "path": str(path),
        "median_writer_free_hot_sec": float(summary["median_writer_free_hot_sec"]),
        "median_lsi_phase_sec": float(summary["median_lsi_phase_sec"]),
        "median_downstream_floor_sec": float(summary["median_downstream_floor_sec"]),
        "measured_rows": rows,
        "writer_free_stats": _stats([row["writer_free_hot_sec"] for row in rows]) if rows else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--capacity", type=int, default=600_000)
    args = parser.parse_args()

    app = args.repo / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"
    prewarm_probe = args.repo / "goal5002_lsi_compile_prewarm_probe.py"
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    common = [
        sys.executable,
        str(app),
        "--left",
        str(args.left),
        "--right",
        str(args.right),
        "--pair-name",
        "top4_county_zipcode",
        "--device-columnar",
        "--bounded-exact-lsi-device-columns",
        "--bounded-exact-lsi-capacity",
        str(args.capacity),
        "--point-location-device-face-columns",
        "--fast-scaled-point-pack",
    ]
    fast_pack_paths: list[Path] = []
    device_paths: list[Path] = []
    for index in range(1, int(args.runs) + 1):
        path = out / f"fast_pack_fresh_run{index}.json"
        fast_pack_paths.append(path)
        _run(common + ["--compiled-group", "--summary", str(path)])
    for index in range(1, int(args.runs) + 1):
        path = out / f"device_resident_fresh_run{index}.json"
        device_paths.append(path)
        _run(common + ["--device-resident-carrier", "--summary", str(path)])

    replay_path = out / "device_resident_prepared_replay_repeat5_postfix.json"
    _run(
        common
        + [
            "--device-resident-carrier",
            "--prepared-operator-session",
            "--warmup-runs",
            "1",
            "--repeat",
            "5",
            "--summary",
            str(replay_path),
        ]
    )

    compile_prewarm_path = out / "device_resident_compile_prewarm_postfix.json"
    if prewarm_probe.exists():
        _run(
            [
                sys.executable,
                str(prewarm_probe),
                "--repo",
                str(args.repo),
                "--left",
                str(args.left),
                "--right",
                str(args.right),
                "--output",
                str(compile_prewarm_path),
                "--prewarm",
            ]
        )

    fast_runs = [_route_summary(path, accounting_mode="fast_pack") for path in fast_pack_paths]
    device_runs = [_route_summary(path, accounting_mode="device_resident") for path in device_paths]
    replay = _repeat_summary(replay_path)
    prewarm = _load(compile_prewarm_path) if compile_prewarm_path.exists() else None

    result = {
        "schema": "rtdl.paper_reproduction.rayjoin.goal5005.owner_directive_measurement.v1",
        "runs": int(args.runs),
        "capacity": int(args.capacity),
        "left": str(args.left),
        "right": str(args.right),
        "fresh_fast_pack": {
            "route": "--compiled-group --fast-scaled-point-pack, no --device-resident-carrier",
            "runs": fast_runs,
            "writer_free_stats": _stats([row["writer_free_hot_sec"] for row in fast_runs]),
            "lsi_stats": _stats([row["lsi_phase_sec"] for row in fast_runs]),
            "downstream_stats": _stats([row["downstream_floor_sec"] for row in fast_runs]),
        },
        "fresh_device_resident": {
            "route": "--device-resident-carrier --fast-scaled-point-pack",
            "runs": device_runs,
            "writer_free_stats": _stats([row["writer_free_hot_sec"] for row in device_runs]),
            "old_prefix_writer_free_stats": _stats(
                [float(row["old_prefix_writer_free_hot_sec"]) for row in device_runs]
            ),
            "accounting_delta_stats": _stats([float(row["accounting_delta_sec"]) for row in device_runs]),
            "lsi_stats": _stats([row["lsi_phase_sec"] for row in device_runs]),
            "downstream_stats": _stats([row["downstream_floor_sec"] for row in device_runs]),
        },
        "postfix_prepared_replay": replay,
        "postfix_compile_prewarm": prewarm,
        "claim_boundary": {
            "fresh_headline_should_use_fast_pack": True,
            "device_resident_fresh_is_experimental_track": True,
            "true_query_many_demonstrated": False,
            "top4_author_ratio_measured": False,
            "author_parity_claim_authorized": False,
        },
    }
    result["fresh_delta_device_minus_fast_pack_median_sec"] = (
        result["fresh_device_resident"]["writer_free_stats"]["median"]
        - result["fresh_fast_pack"]["writer_free_stats"]["median"]
    )
    summary_path = out / "goal5005_owner_directive_measurement_summary.json"
    summary_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
