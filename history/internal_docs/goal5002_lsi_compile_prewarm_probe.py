#!/usr/bin/env python3
"""Goal5002 probe: generic LSI pipeline prewarm before a fresh RayJoin route.

This script is intentionally internal. It does not add a product API. It tests
whether the exact LSI pipeline/split-kernel ensure cost is a generic one-time
initialization that can be triggered before the top4 fresh overlay route.
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


def _build_run_args(left: Path, right: Path, summary: Path | None) -> SimpleNamespace:
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
        bounded_exact_lsi_capacity=1_000_000,
        point_location_device_face_columns=True,
        fast_scaled_point_pack=True,
        validate_device_order=False,
        compiled_group=False,
        compiled_group_side_order="0,1",
        device_resident_carrier=True,
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
    elapsed = time.perf_counter() - start
    return {
        "schema": "rtdl.goal5002.generic_lsi_tiny_prewarm.v1",
        "elapsed_sec": elapsed,
        "row_count": row_count,
        "traversal_seconds": traversal_seconds,
        "extended_timings": timings,
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

    run_args = _build_run_args(Path(args.left), Path(args.right), None)
    route_start = time.perf_counter()
    summary = app.run_pipeline(run_args)
    route_elapsed = time.perf_counter() - route_start

    result = {
        "schema": "rtdl.goal5002.lsi_compile_prewarm_probe.v1",
        "prewarm_enabled": bool(args.prewarm),
        "prewarm_result": prewarm_result,
        "route_elapsed_sec": route_elapsed,
        "summary": summary,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
