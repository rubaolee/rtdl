#!/usr/bin/env python3
"""Home-only one-shot trial of every non-RayDB/RayJoin formal front door."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from goal5776_real_scale_formal_contract import UNITS, V2, V4
from goal5776_real_scale_frontdoors import run_real_scale_endpoint
from rtdsl.v4_callback_numba_codegen import (
    formal_numba_leaf_cache_lifecycle_metadata,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cache_delta(before: dict[str, object], after: dict[str, object]) -> dict[str, int]:
    return {
        key: int(after[key]) - int(before[key])
        for key in ("hit_count", "miss_count", "disabled_count")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--leaf-cache-root", required=True, type=Path)
    parser.add_argument("--leaf-cache-manifest", required=True, type=Path)
    parser.add_argument("--populate-unsealed-cache", action="store_true")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--rtdbscan-evidence", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--only-unit-id", action="append")
    args = parser.parse_args()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=False)
    native = args.native.resolve()
    manifest = args.leaf_cache_manifest.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(args.leaf_cache_root.resolve())
    if args.populate_unsealed_cache:
        os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST", None)
        os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256", None)
    else:
        os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST"] = str(manifest)
        os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256"] = _sha(manifest)
    data = args.data_root.resolve()
    snap = Path("/home/lestat/data/goal5776_snap/edges")
    librts = data / "librts/parks"
    rtbh = data / "rt_barneshut"
    runtime = {
        "source_root": str(args.source_root.resolve()),
        "native_library_path": str(native),
        "compute_capability": [6, 1],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(args.optix_include.resolve()),
        "cuda_include": str(args.cuda_include.resolve()),
        "inputs": {},
    }
    inputs = runtime["inputs"]
    inputs["particle__microfluidics_5000"] = {
        "input_root": "/home/lestat/data/goal5776_particle_prepared_v2"
    }
    inputs["rtnn__kitti12m_q4096_k4"] = {
        "input_root": "/home/lestat/data/goal5776_rtnn_prepared_v1"
    }
    inputs["xhd__dragon_to_happy"] = {
        "input_root": "/home/lestat/data/goal5776_xhd_prepared_v1"
    }
    prepared_arrays = rtbh / "prepared_arrays.json"
    expected_forces = rtbh / "expected_forces.txt"
    inputs["rtbh__author_32768"] = {
        "prepared_arrays": str(prepared_arrays),
        "expected_forces": str(expected_forces),
        "expected_prepared_sha256": _sha(prepared_arrays),
        "expected_forces_sha256": _sha(expected_forces),
    }
    triangle = {
        "com_dblp": (snap / "com-dblp.edge", 2_224_385),
        "cit_patents": (snap / "cit-Patents.edge", 7_515_023),
        "soc_livejournal1": (snap / "soc-LiveJournal1.edge", 285_730_264),
    }
    for dataset, (edge, count) in triangle.items():
        for algorithm in ("rt_1a2", "rt_2a1"):
            inputs[f"triangle__{dataset}__{algorithm}"] = {
                "edge_file": str(edge),
                "expected_triangle_count": count,
                "max_relation_rows": 1_000_000,
            }
    for unit in UNITS:
        if unit.app == "rt_dbscan":
            inputs[unit.unit_id] = (
                {"input_root": "/home/lestat/work/goal5776_rtdbscan_prepared_v1"}
                if unit.unit_id.endswith("goal5776_clustered3d_4096")
                else {"refinement_evidence_path": str(args.rtdbscan_evidence.resolve())}
            )
    cache_npz = librts / "cache/parks_bz2.npz"
    cache_json = librts / "cache/parks_bz2.json"
    inputs["librts__parks_point_contains"] = {
        "cache_npz": str(cache_npz), "cache_json": str(cache_json),
        "point_queries": str(librts / "queries/point_contains_100000.wkt"),
        "expected_count": 112_729,
    }
    inputs["librts__parks_range_contains"] = {
        "cache_npz": str(cache_npz), "cache_json": str(cache_json),
        "range_queries": str(librts / "queries/range_contains_100000.wkt"),
        "expected_count": 105_826,
    }
    selected = [unit for unit in UNITS if unit.app not in ("raydb", "rayjoin")]
    if args.only_unit_id:
        requested = set(args.only_unit_id)
        selected = [unit for unit in selected if unit.unit_id in requested]
        if {unit.unit_id for unit in selected} != requested:
            raise ValueError("unknown Goal5776 --only-unit-id")
    trial_count = sum(len(unit.supported_lifecycles) * 2 for unit in selected)
    completed = 0
    for unit in selected:
        for lifecycle in unit.supported_lifecycles:
            for method in (V2, V4):
                cache_before = formal_numba_leaf_cache_lifecycle_metadata()
                endpoint = run_real_scale_endpoint(
                    unit_id=unit.unit_id, method=method, lifecycle=lifecycle,
                    runtime=runtime,
                )
                cache_after = formal_numba_leaf_cache_lifecycle_metadata()
                cache_delta = _cache_delta(cache_before, cache_after)
                if method == V4 and not args.populate_unsealed_cache:
                    if unit.v4_numba_leaf_cache_required and (
                        cache_delta["hit_count"] <= 0
                        or cache_delta["miss_count"] != 0
                        or cache_delta["disabled_count"] != 0
                    ):
                        raise RuntimeError(
                            f"sealed V4 trial did not use only cache hits: {cache_delta}")
                    if not unit.v4_numba_leaf_cache_required and any(
                        cache_delta[key] != 0 for key in cache_delta
                    ):
                        raise RuntimeError(
                            f"non-leaf V4 trial touched callback cache: {cache_delta}")
                record = {
                    "schema": "rtdl.goal5776.home_formal_frontdoor_trial.v1",
                    "unit_id": unit.unit_id, "app": unit.app,
                    "method": method, "lifecycle": lifecycle,
                    "matched": endpoint["matched"],
                    "rows": endpoint["rows"],
                    "phase_accounting": endpoint["phase_accounting"],
                    "traversal_receipt": endpoint["traversal_receipt"],
                    "formal_leaf_cache_delta": (
                        {
                            **cache_delta,
                            "mode": (
                                "sealed_read_only_manifest"
                                if unit.v4_numba_leaf_cache_required
                                else "not_applicable_no_numba_leaf"
                            ),
                        }
                        if method == V4
                        else {"mode": "not_applicable_to_v2_direct"}
                    ),
                    "formal_performance_result_created": False,
                }
                path = output / f"{completed:03d}.json"
                path.write_text(
                    json.dumps(record, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                completed += 1
                print(json.dumps({
                    "completed": completed, "expected": trial_count,
                    "unit_id": unit.unit_id, "method": method,
                    "lifecycle": lifecycle,
                }, sort_keys=True), flush=True)
    summary = {
        "schema": "rtdl.goal5776.home_remaining_frontdoor_trial.v1",
        "status": "passed", "paper_app_count": len({unit.app for unit in selected}),
        "trial_count": completed, "expected_trial_count": trial_count,
        "formal_performance_result_created": False,
        "modern_rtx_claimed": False,
        "unsealed_cache_population_mode": bool(args.populate_unsealed_cache),
    }
    (output / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
