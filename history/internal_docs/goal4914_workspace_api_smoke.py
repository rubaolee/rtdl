#!/usr/bin/env python3
"""Goal4914 smoke: run the Section 5.7 app through the public workspace API."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np


THIS_DIR = Path(__file__).resolve().parent
NUMBA_WRAPPER = THIS_DIR / "goal4886_section57_public_primitives_overlay_numba_harness.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _timed(label: str, fn, timings: dict[str, float]):
    start = time.perf_counter()
    value = fn()
    timings[label] = time.perf_counter() - start
    return value


def _file_summary(path: Path) -> dict[str, object]:
    import hashlib

    h = hashlib.sha256()
    lines = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return {"path": str(path), "bytes": path.stat().st_size, "lines": lines, "sha256": h.hexdigest()}


def _install_numba_app_continuation(wrapper) -> None:
    base = wrapper.base
    base.midpoint_points = wrapper.midpoint_points_numba_enabled
    base.dedupe_point_pairs = wrapper.dedupe_point_pairs_numba_enabled
    base.write_output_chains_streaming = wrapper.write_output_chains_streaming_numba_skip


def _pair_rows_to_array(row_view):
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


def run_workspace_body(wrapper, workspace, args, repeat_index: int) -> dict[str, object]:
    base = wrapper.base
    timings: dict[str, float] = {}
    point_timings = {}
    total_start = time.perf_counter()

    pairs = _timed(
        "workspace_lsi_pair_id_rows_sec",
        lambda: _pair_rows_to_array(workspace.run_lsi_pair_id_rows()),
        timings,
    )
    xsects = _timed(
        "intersection_reprojection_sec",
        lambda: base.intersection_rows_from_pairs(pairs, workspace.left, workspace.right, scale_bounds=workspace.bounds),
        timings,
    )
    xsects0 = _timed("sort_map0_sec", lambda: base.sort_xsects_for_map(list(xsects), workspace.left, 0, workspace.bounds), timings)
    xsects1 = _timed("sort_map1_sec", lambda: base.sort_xsects_for_map(list(xsects), workspace.right, 1, workspace.bounds), timings)

    point_faces0 = _timed(
        "vertex_pip_map0_in_map1_sec",
        lambda: base.run_point_location(workspace.left_in_right, workspace.left.points, workspace.left.point_count),
        timings,
    )
    point_timings["vertex_pip_map0_in_map1"] = workspace.left_in_right.last_phase_timings() or {}

    point_faces1 = _timed(
        "vertex_pip_map1_in_map0_sec",
        lambda: base.run_point_location(workspace.right_in_left, workspace.right.points, workspace.right.point_count),
        timings,
    )
    point_timings["vertex_pip_map1_in_map0"] = workspace.right_in_left.last_phase_timings() or {}

    for map_index, locator, sorted_rows in (
        (0, workspace.left_in_right, xsects0),
        (1, workspace.right_in_left, xsects1),
    ):
        midpoints, scaled_midpoints, owners = _timed(
            f"midpoint_points_map{map_index}_sec",
            lambda sorted_rows=sorted_rows, map_index=map_index: wrapper.midpoint_points_numba_enabled(
                sorted_rows,
                map_index,
                scale_bounds=workspace.bounds,
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
            (workspace.left, workspace.right),
            (xsects0, xsects1),
            (point_faces0, point_faces1),
            output_path,
        ),
        timings,
    )
    generated = _timed("file_summary_generated_sec", lambda: _file_summary(output_path), timings)
    author = _timed("file_summary_author_sec", lambda: _file_summary(Path(args.author_output)), timings)
    elapsed = time.perf_counter() - total_start
    return {
        "repeat": repeat_index,
        "elapsed_sec": elapsed,
        "timed_sum_sec": sum(timings.values()),
        "unattributed_sec": elapsed - sum(timings.values()),
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
    args = parser.parse_args()

    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected before Goal4914 start")

    startup_timings: dict[str, float] = {}
    wrapper = _timed(
        "import_goal4886_wrapper_sec",
        lambda: _load_module(NUMBA_WRAPPER, "goal4886_section57_public_primitives_overlay_numba_harness"),
        startup_timings,
    )
    _timed("install_numba_app_continuation_sec", lambda: _install_numba_app_continuation(wrapper), startup_timings)

    from rtdsl import prepare_planar_map_workspace_2d_optix

    workspace = _timed(
        "prepare_planar_map_workspace_sec",
        lambda: prepare_planar_map_workspace_2d_optix(
            args.left,
            args.right,
            cache_dir=args.cache_dir,
            prepare_lsi=True,
            prepare_point_location=True,
        ),
        startup_timings,
    )
    try:
        runs = [run_workspace_body(wrapper, workspace, args, index) for index in range(args.repeat)]
        workspace_metadata = workspace.metadata()
    finally:
        _timed("destroy_planar_map_workspace_sec", workspace.close, startup_timings)

    payload = {
        "schema": "rtdl.goal4914.workspace_api_smoke.v1",
        "claim_boundary": {
            "public_planar_map_workspace_used": True,
            "public_lsi_used": True,
            "public_point_location_used": True,
            "numba_on_app_continuation_path": bool(wrapper.kernels.NUMBA_AVAILABLE),
            "numba_on_rtdl_primitive_path": False,
            "bundled_rayjoin_overlay_imported": False,
            "broad_performance_claim": False,
            "single_run_speedup_claim": False,
        },
        "startup_phase_seconds": startup_timings,
        "workspace_metadata": workspace_metadata,
        "runs": runs,
    }
    Path(args.summary).write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
