#!/usr/bin/env python3
"""Goal5007 probe: P3 safe fresh optimizations on the fast-pack route.

This probe intentionally does not add a product API.  It measures the current
v2.14.3 headline route (fast-pack writer-free binary route, no
device-resident-carrier) with and without a tiny generic LSI prewarm.  The
prewarm time is recorded separately and never hidden inside the route window.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def _load_app(repo: Path):
    app_dir = repo / "Paper-reproduction-apps" / "rayjoin-paper"
    src_dir = repo / "src"
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, str(src_dir))
    import section57_overlay_columnar_binary as app  # type: ignore

    return app


def _build_fastpack_run_args(left: Path, right: Path, summary: Path | None) -> SimpleNamespace:
    return SimpleNamespace(
        left=str(left),
        right=str(right),
        summary=str(summary) if summary is not None else None,
        pair_name="top4_county_zipcode",
        author_overlay_compute_sec=None,
        cache_dir=None,
        swap_query_map_ids=False,
        no_numba_warmup=True,
        repeat=1,
        warmup_runs=0,
        prepared_operator_session=False,
        prepared_lsi_replay=False,
        device_columnar=True,
        exact_lsi_device_columns=False,
        bounded_exact_lsi_device_columns=True,
        bounded_exact_lsi_capacity=600_000,
        point_location_device_face_columns=True,
        fast_scaled_point_pack=True,
        validate_device_order=False,
        compiled_group=True,
        compiled_group_side_order="0,1",
        device_resident_carrier=False,
        bounded_exact_lsi_repeat_diagnostic=0,
    )


def _generic_lsi_tiny_prewarm(app) -> dict[str, object]:
    base = app.base
    right = base.pack_segments(
        ids=np.array([1], dtype=np.int64),
        x0=np.array([0.0], dtype=np.float64),
        y0=np.array([1.0], dtype=np.float64),
        x1=np.array([1.0], dtype=np.float64),
        y1=np.array([0.0], dtype=np.float64),
    )
    left = base.pack_segments(
        ids=np.array([2], dtype=np.int64),
        x0=np.array([0.0], dtype=np.float64),
        y0=np.array([0.0], dtype=np.float64),
        x1=np.array([1.0], dtype=np.float64),
        y1=np.array([1.0], dtype=np.float64),
    )
    start = time.perf_counter()
    with base.prepare_planar_map_lsi_2d_optix(right) as lsi:
        with lsi.prepare_query(left) as query:
            columns = query.run_bounded_pair_id_device_columns(max_rows=8)
            try:
                row_count = int(columns.row_count)
                traversal_seconds = float(columns.traversal_seconds)
            finally:
                columns.close()
            timings = lsi.prepared.last_extended_phase_timings() or {}
    return {
        "schema": "rtdl.goal5007.generic_lsi_tiny_prewarm.v1",
        "elapsed_sec": time.perf_counter() - start,
        "row_count": row_count,
        "traversal_seconds": traversal_seconds,
        "extended_timings": timings,
    }


def _compact(summary: dict[str, object]) -> dict[str, object]:
    phase = summary.get("phase_seconds", {})
    if not isinstance(phase, dict):
        phase = {}
    floor = summary.get("downstream_floor_breakdown", {})
    if not isinstance(floor, dict):
        floor = {}
    consumer = summary.get("downstream_consumer", {})
    if not isinstance(consumer, dict):
        consumer = {}
    return {
        "writer_free_hot_sec": float(summary.get("writer_free_hot_sec", 0.0)),
        "lsi_phase_sec": float(floor.get("lsi_phase_sec", 0.0)),
        "downstream_floor_sec": float(floor.get("downstream_floor_sec", 0.0)),
        "lsi_row_count": int(summary.get("lsi_row_count", 0)),
        "descriptor_pair_count": int(consumer.get("pair_count", 0)),
        "key_phase_seconds": {
            key: float(phase[key])
            for key in (
                "lsi_bounded_exact_pair_id_device_columns_sec",
                "intersection_reprojection_device_columnar_sec",
                "sort_map0_device_columnar_sec",
                "sort_map1_device_columnar_sec",
                "vertex_pip_map0_in_map1_sec",
                "vertex_pip_map1_in_map0_sec",
                "midpoint_points_map0_columnar_sec",
                "midpoint_points_map1_columnar_sec",
                "midpoint_pip_map0_sec",
                "midpoint_pip_map1_sec",
                "grouped_compiled_columnar_carrier_construction_sec",
                "grouped_descriptor_pair_count_consumer_sec",
            )
            if key in phase
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prewarm", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    app = _load_app(repo)
    prewarm_result = _generic_lsi_tiny_prewarm(app) if args.prewarm else None

    run_args = _build_fastpack_run_args(Path(args.left), Path(args.right), None)
    route_start = time.perf_counter()
    summary = app.run_pipeline(run_args)
    route_elapsed = time.perf_counter() - route_start
    result = {
        "schema": "rtdl.goal5007.p3_fastpack_fresh_probe.v1",
        "regime": "warm_process_fresh_fastpack_route_window",
        "prewarm_enabled": bool(args.prewarm),
        "prewarm_result": prewarm_result,
        "route_elapsed_sec": route_elapsed,
        "summary_compact": _compact(summary),
        "claim_boundary": {
            "route": "fast_pack_writer_free_binary",
            "device_resident_carrier": False,
            "prewarm_time_excluded_from_route_window": bool(args.prewarm),
            "fresh_one_shot_headline": False,
            "true_query_many_measurement": False,
            "ten_x_claim_authorized": False,
        },
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
