#!/usr/bin/env python3
"""Goal4911 focused point-location prepare/run tradeoff probe.

This is measurement-only. It imports the public-primitives harness and compares
generic directed point-location group/range construction modes on the Australia
representative pair.
"""

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


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def _group_env(config: dict[str, str]):
    old = {key: os.environ.get(key) for key in GROUP_KEYS}
    for key in GROUP_KEYS:
        os.environ.pop(key, None)
    os.environ.update(config)
    try:
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


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


def _run_stage(base, segments, points, point_count: int, query_map_id: int, bounds) -> dict[str, object]:
    start = time.perf_counter()
    locator = base.prepare_planar_map_point_location_2d_optix(
        segments,
        query_map_id=query_map_id,
        scale_bounds=bounds,
    )
    prepare_sec = time.perf_counter() - start
    try:
        start = time.perf_counter()
        faces = base.run_point_location(locator, points, point_count)
        run_sec = time.perf_counter() - start
        timings = locator.last_phase_timings() or {}
        work_count = _read_work_count(locator)
    finally:
        start = time.perf_counter()
        locator.close()
        destroy_sec = time.perf_counter() - start
    return {
        "prepare_sec": prepare_sec,
        "run_sec": run_sec,
        "destroy_sec": destroy_sec,
        "point_count": int(point_count),
        "positive_face_count": int(np.count_nonzero(faces)),
        "face_hash_fnv64": _fnv64_uint32(faces),
        "raw_candidate_count": int(work_count) if work_count is not None else None,
        "native_timings": timings,
    }


def _modes() -> list[tuple[str, dict[str, str]]]:
    return [
        ("default_current", {}),
        ("legacy_fixed8", {"RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "fixed8"}),
        (
            "adaptive_ms8_e1.5",
            {
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "adaptive",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE": "8",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": "1.5",
            },
        ),
        (
            "block_merge64_i0_e1.5",
            {
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "block_merge64",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": "0",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": "1.5",
            },
        ),
        (
            "block_merge64_i1_e1.5",
            {
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "block_merge64",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": "1",
                "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": "1.5",
            },
        ),
        ("default_current_repeat", {}),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-harness", required=True)
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--cache-dir")
    args = parser.parse_args()

    base = _load_module(Path(args.base_harness), "goal4911_base_harness")

    old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
    if args.cache_dir:
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))
    start = time.perf_counter()
    try:
        left = base.load_dataset_arrays(Path(args.left))
        right = base.load_dataset_arrays(Path(args.right))
    finally:
        if args.cache_dir:
            if old_cache_dir is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir
    bounds = base.shared_bounds(left, right)
    load_sec = time.perf_counter() - start

    rows = []
    baseline: dict[str, object] | None = None
    for label, config in _modes():
        with _group_env(config):
            map0 = _run_stage(base, right.cdb_segments, left.points, left.point_count, 0, bounds)
            map1 = _run_stage(base, left.cdb_segments, right.points, right.point_count, 1, bounds)
        row = {"label": label, "env": config, "map0_in_map1": map0, "map1_in_map0": map1}
        if baseline is not None:
            for key in ("map0_in_map1", "map1_in_map0"):
                current = row[key]
                base_stage = baseline[key]  # type: ignore[index]
                current["face_hash_matches_default"] = (
                    current["face_hash_fnv64"] == base_stage["face_hash_fnv64"]  # type: ignore[index]
                )
                base_candidates = base_stage.get("raw_candidate_count")  # type: ignore[union-attr]
                current_candidates = current.get("raw_candidate_count")  # type: ignore[union-attr]
                current["candidate_reduction_vs_default"] = (
                    float(base_candidates) / float(current_candidates)
                    if base_candidates and current_candidates
                    else None
                )
        else:
            baseline = row
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    payload = {
        "schema": "rtdl.goal4911.point_location_prepare_tradeoff_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "load_sec": load_sec,
        "rows": rows,
    }
    Path(args.summary).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
