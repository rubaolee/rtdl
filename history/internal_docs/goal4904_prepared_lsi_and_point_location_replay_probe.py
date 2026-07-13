#!/usr/bin/env python3
"""Goal4904 probe: reuse prepared LSI query and point-location sessions.

This internal benchmark validates an existing generic RTDL shape:

    prepare LSI base/query and point-location base maps once
    -> run repeated overlay bodies

It keeps the public LSI/PIP primitives and the Numba app continuation route. It
does not change RTDL semantics, and it does not import ``rtdsl.rayjoin_overlay``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
NUMBA_WRAPPER = THIS_DIR / "goal4886_section57_public_primitives_overlay_numba_harness.py"


def _timed(label: str, fn, timings: dict[str, float]):
    start = time.perf_counter()
    value = fn()
    timings[label] = time.perf_counter() - start
    return value


def _file_summary(path: Path) -> dict[str, object]:
    h = __import__("hashlib").sha256()
    lines = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return {"path": str(path), "bytes": path.stat().st_size, "lines": lines, "sha256": h.hexdigest()}


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _install_numba_app_continuation(wrapper) -> None:
    base = wrapper.base
    base.midpoint_points = wrapper.midpoint_points_numba_enabled
    base.dedupe_point_pairs = wrapper.dedupe_point_pairs_numba_enabled
    base.write_output_chains_streaming = wrapper.write_output_chains_streaming_numba_skip


def run_body(wrapper, state: dict[str, object], args, repeat_index: int) -> dict[str, object]:
    base = wrapper.base
    left = state["left"]
    right = state["right"]
    bounds = state["bounds"]
    lsi_query = state["lsi_query"]
    map0_in_map1 = state["map0_in_map1"]
    map1_in_map0 = state["map1_in_map0"]
    timings: dict[str, float] = {}
    total_start = time.perf_counter()

    def run_lsi():
        row_view = lsi_query.run_pair_id_rows()
        try:
            columns = row_view.to_numpy_columns(copy=True)
            return np.column_stack(
                (
                    columns["left_id"].astype(np.uint32, copy=False),
                    columns["right_id"].astype(np.uint32, copy=False),
                )
            )
        finally:
            row_view.close()

    pairs = _timed("lsi_public_pair_id_rows_sec", run_lsi, timings)
    xsects = _timed(
        "intersection_reprojection_sec",
        lambda: base.intersection_rows_from_pairs(pairs, left, right, scale_bounds=bounds),
        timings,
    )
    xsects0 = _timed("sort_map0_sec", lambda: base.sort_xsects_for_map(list(xsects), left, 0, bounds), timings)
    xsects1 = _timed("sort_map1_sec", lambda: base.sort_xsects_for_map(list(xsects), right, 1, bounds), timings)

    point_timings = {}
    point_faces0 = _timed(
        "vertex_pip_map0_in_map1_sec",
        lambda: base.run_point_location(map0_in_map1, left.points, left.point_count),
        timings,
    )
    point_timings["vertex_pip_map0_in_map1"] = map0_in_map1.last_phase_timings() or {}

    point_faces1 = _timed(
        "vertex_pip_map1_in_map0_sec",
        lambda: base.run_point_location(map1_in_map0, right.points, right.point_count),
        timings,
    )
    point_timings["vertex_pip_map1_in_map0"] = map1_in_map0.last_phase_timings() or {}

    for map_index, locator, sorted_rows in (
        (0, map0_in_map1, xsects0),
        (1, map1_in_map0, xsects1),
    ):
        midpoints, scaled_midpoints, owners = _timed(
            f"midpoint_points_map{map_index}_sec",
            lambda sorted_rows=sorted_rows, map_index=map_index: wrapper.midpoint_points_numba_enabled(
                sorted_rows,
                map_index,
                scale_bounds=bounds,
            ),
            timings,
        )
        scaled_points = _timed(
            f"pack_midpoint_points_map{map_index}_sec",
            lambda midpoints=midpoints, scaled_midpoints=scaled_midpoints: base.pack_rayjoin_cdb_scaled_points(
                ids=np.arange(1, len(midpoints) + 1, dtype=np.int64),
                x=np.fromiter((p[0] for p in midpoints), dtype=np.float64, count=len(midpoints)),
                y=np.fromiter((p[1] for p in midpoints), dtype=np.float64, count=len(midpoints)),
                sx=np.fromiter((p[0] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints)),
                sy=np.fromiter((p[1] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints)),
            ),
            timings,
        )
        faces = _timed(
            f"midpoint_pip_map{map_index}_sec",
            lambda locator=locator, scaled_points=scaled_points, count=len(midpoints): base.run_point_location(
                locator,
                scaled_points,
                count,
            ),
            timings,
        )
        point_timings[f"midpoint_pip_map{map_index}"] = locator.last_phase_timings() or {}
        _timed(
            f"assign_midpoint_faces_map{map_index}_sec",
            lambda owners=owners, faces=faces, map_index=map_index: base.assign_midpoint_faces(owners, faces, map_index),
            timings,
        )

    output_path = Path(args.output_template.format(repeat=repeat_index))
    writer_result = _timed(
        "output_chain_write_sec",
        lambda: wrapper.write_output_chains_streaming_numba_skip(
            (left, right),
            (xsects0, xsects1),
            (point_faces0, point_faces1),
            output_path,
        ),
        timings,
    )
    generated = _timed("file_summary_generated_sec", lambda: _file_summary(output_path), timings)
    author = _timed("file_summary_author_sec", lambda: _file_summary(Path(args.author_output)), timings)

    elapsed = time.perf_counter() - total_start
    timed_sum = sum(timings.values())
    return {
        "repeat": repeat_index,
        "elapsed_sec": elapsed,
        "timed_sum_sec": timed_sum,
        "unattributed_sec": elapsed - timed_sum,
        "phase_seconds": timings,
        "native_point_location_timings": point_timings,
        "byte_equal_to_author": generated["sha256"] == author["sha256"] and generated["bytes"] == author["bytes"],
        "generated_output": generated,
        "author_output": author,
        "writer_result": writer_result,
        "counts": {
            "lsi_row_count": int(pairs.shape[0]),
            "xsects_map0": len(xsects0),
            "xsects_map1": len(xsects1),
            "vertex_positive_map0_in_map1": int(np.count_nonzero(point_faces0)),
            "vertex_positive_map1_in_map0": int(np.count_nonzero(point_faces1)),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output-template", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--swap-query-map-ids", action="store_true")
    args = parser.parse_args()

    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected before Goal4904 start")

    startup_timings: dict[str, float] = {}
    wrapper = _timed(
        "import_goal4886_wrapper_sec",
        lambda: _load_module(NUMBA_WRAPPER, "goal4886_section57_public_primitives_overlay_numba_harness"),
        startup_timings,
    )
    _timed("install_numba_app_continuation_sec", lambda: _install_numba_app_continuation(wrapper), startup_timings)
    base = wrapper.base

    setup_timings: dict[str, float] = {}
    old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
    os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))
    try:
        left = _timed("load_pack_left_sec", lambda: base.load_dataset_arrays(Path(args.left)), setup_timings)
        right = _timed("load_pack_right_sec", lambda: base.load_dataset_arrays(Path(args.right)), setup_timings)
    finally:
        if old_cache_dir is None:
            os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
        else:
            os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir

    bounds = _timed("shared_bounds_sec", lambda: base.shared_bounds(left, right), setup_timings)
    lsi_base = _timed(
        "prepare_lsi_base_sec",
        lambda: base.prepare_planar_map_lsi_2d_optix(right.lsi_segments),
        setup_timings,
    )
    lsi_query = _timed(
        "prepare_lsi_query_sec",
        lambda: lsi_base.prepare_query(left.lsi_segments),
        setup_timings,
    )
    map0_query_map_id = 1 if args.swap_query_map_ids else 0
    map1_query_map_id = 0 if args.swap_query_map_ids else 1
    map0_in_map1 = _timed(
        "prepare_point_location_map0_in_map1_sec",
        lambda: base.prepare_planar_map_point_location_2d_optix(
            right.cdb_segments,
            query_map_id=map0_query_map_id,
            scale_bounds=bounds,
        ),
        setup_timings,
    )
    map1_in_map0 = _timed(
        "prepare_point_location_map1_in_map0_sec",
        lambda: base.prepare_planar_map_point_location_2d_optix(
            left.cdb_segments,
            query_map_id=map1_query_map_id,
            scale_bounds=bounds,
        ),
        setup_timings,
    )

    try:
        state = {
            "left": left,
            "right": right,
            "bounds": bounds,
            "lsi_base": lsi_base,
            "lsi_query": lsi_query,
            "map0_in_map1": map0_in_map1,
            "map1_in_map0": map1_in_map0,
        }
        runs = [run_body(wrapper, state, args, index) for index in range(args.repeat)]
    finally:
        _timed(
            "destroy_reused_sessions_sec",
            lambda: (lsi_query.close(), lsi_base.close(), map0_in_map1.close(), map1_in_map0.close()),
            setup_timings,
        )

    payload = {
        "schema": "rtdl.goal4904.prepared_lsi_and_point_location_replay_probe.v1",
        "claim_boundary": {
            "public_lsi_used": True,
            "public_point_location_used": True,
            "lsi_prepared_query_reused": True,
            "point_location_base_sessions_reused": True,
            "numba_on_app_continuation_path": bool(wrapper.kernels.NUMBA_AVAILABLE),
            "numba_on_rtdl_primitive_path": False,
            "bundled_rayjoin_overlay_imported": False,
            "broad_performance_claim": False,
            "single_run_speedup_claim": False,
        },
        "startup_phase_seconds": startup_timings,
        "setup_phase_seconds": setup_timings,
        "runs": runs,
    }
    Path(args.summary).write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
