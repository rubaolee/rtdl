#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GROUP_KEYS = (
    "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE",
    "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE",
    "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE",
    "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER",
    "RTDL_RAYJOIN_CDB_GROUP_MODE",
    "RTDL_RAYJOIN_CDB_GROUP_MAX_SIZE",
    "RTDL_RAYJOIN_CDB_GROUP_AREA_ENLARGE",
    "RTDL_RAYJOIN_CDB_GROUP_MAX_ITER",
)


def _fnv64_uint32(values: np.ndarray) -> str:
    h = 1469598103934665603
    for value in values.astype(np.uint32, copy=False):
        h ^= int(value)
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return f"{h:016x}"


def _read_work_count(locator) -> int | None:
    library = getattr(locator, "library", None)
    if library is None and hasattr(locator, "prepared"):
        library = getattr(locator.prepared, "library", None)
    if library is None:
        return None
    symbol = getattr(library, "rtdl_optix_rayjoin_cdb_point_location_get_last_work_count", None)
    if symbol is None:
        return None
    symbol.argtypes = (ctypes.POINTER(ctypes.c_size_t),)
    symbol.restype = ctypes.c_int
    value = ctypes.c_size_t(0)
    status = symbol(ctypes.byref(value))
    if status != 0:
        return None
    return int(value.value)


@contextmanager
def _group_env(config: dict[str, str]):
    previous = {key: os.environ.get(key) for key in GROUP_KEYS}
    for key in GROUP_KEYS:
        os.environ.pop(key, None)
    os.environ.update(config)
    try:
        yield
    finally:
        for key in GROUP_KEYS:
            old = previous[key]
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def _run_stage(base, segments, points, point_count: int, query_map_id: int, bounds) -> dict[str, object]:
    start_prepare = time.perf_counter()
    with base.prepare_planar_map_point_location_2d_optix(
        segments,
        query_map_id=query_map_id,
        scale_bounds=bounds,
    ) as locator:
        prepare_sec = time.perf_counter() - start_prepare
        start_run = time.perf_counter()
        faces = base.run_point_location(locator, points, point_count)
        run_sec = time.perf_counter() - start_run
        timings = locator.last_phase_timings() or {}
        work_count = _read_work_count(locator)
    return {
        "prepare_sec": prepare_sec,
        "run_sec": run_sec,
        "point_count": int(point_count),
        "positive_face_count": int(np.count_nonzero(faces)),
        "face_hash_fnv64": _fnv64_uint32(faces),
        "raw_candidate_count": int(work_count) if work_count is not None else None,
        "native_timings": timings,
    }


def _mode_matrix() -> list[tuple[str, dict[str, str]]]:
    rows: list[tuple[str, dict[str, str]]] = [("fixed8_default", {})]
    for max_size in (8, 16, 32, 64):
        for enlarge in (1.5, 2.0, 3.5):
            rows.append(
                (
                    f"adaptive_ms{max_size}_e{enlarge}",
                    {
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "adaptive",
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE": str(max_size),
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": str(enlarge),
                    },
                )
            )
    for max_iter in (0, 1, 2, 5):
        for enlarge in (1.5, 2.0, 3.5):
            rows.append(
                (
                    f"block_merge64_i{max_iter}_e{enlarge}",
                    {
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "block_merge64",
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": str(max_iter),
                        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": str(enlarge),
                    },
                )
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-harness", required=True)
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--max-modes", type=int)
    args = parser.parse_args()

    base = _load_module(Path(args.base_harness), "goal4893_base_harness")
    load_start = time.perf_counter()
    left = base.load_dataset_arrays(Path(args.left))
    right = base.load_dataset_arrays(Path(args.right))
    bounds = base.shared_bounds(left, right)
    load_sec = time.perf_counter() - load_start

    rows = []
    matrix = _mode_matrix()
    if args.max_modes is not None:
        matrix = matrix[: args.max_modes]
    baseline: dict[str, object] | None = None

    for label, config in matrix:
        with _group_env(config):
            stage0 = _run_stage(
                base,
                right.cdb_segments,
                left.points,
                left.point_count,
                query_map_id=0,
                bounds=bounds,
            )
            stage1 = _run_stage(
                base,
                left.cdb_segments,
                right.points,
                right.point_count,
                query_map_id=1,
                bounds=bounds,
            )
        row = {
            "label": label,
            "env": config,
            "map0_in_map1": stage0,
            "map1_in_map0": stage1,
        }
        if baseline is None:
            baseline = row
        else:
            for stage_name in ("map0_in_map1", "map1_in_map0"):
                current = row[stage_name]
                base_stage = baseline[stage_name]  # type: ignore[index]
                base_count = base_stage["raw_candidate_count"]  # type: ignore[index]
                current_count = current["raw_candidate_count"]  # type: ignore[index]
                current["candidate_reduction_vs_fixed8"] = (
                    float(base_count) / float(current_count)
                    if base_count and current_count
                    else None
                )
                current["face_hash_matches_fixed8"] = (
                    current["face_hash_fnv64"] == base_stage["face_hash_fnv64"]  # type: ignore[index]
                )
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    payload = {
        "schema": "rtdl.goal4893.pip_group_mode_matrix.v1",
        "left": str(args.left),
        "right": str(args.right),
        "load_sec": load_sec,
        "rows": rows,
    }
    Path(args.summary).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
