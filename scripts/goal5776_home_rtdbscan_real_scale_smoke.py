#!/usr/bin/env python3
"""Untimed Home correctness/capacity/true-OptiX gate for RT-DBSCAN N=4096."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

import numba
import numpy as np

import rtdsl as rt
from rtdsl import optix_runtime
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load_app(source_root: Path):
    path = source_root / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"
    spec = importlib.util.spec_from_file_location("goal5776_rtdbscan_v4", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load RT-DBSCAN V4 front door")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _runtime(native: Path, optix_include: Path, cuda_include: Path):
    return {
        "target": ReferenceTargetProfile(
            provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
            native_sha256=_sha(native), supports_custom_aabb=True,
            supports_builtin_triangle=True),
        "compute_capability": (6, 1),
        "optix_include": optix_include,
        "cuda_include": cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def _project(columns, point_count: int) -> dict[str, object]:
    point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
    labels_in = np.asarray(
        columns["component_labels"].copy_to_host(), dtype=np.int64)
    core_in = np.asarray(columns["is_core"].copy_to_host(), dtype=np.int64)
    labels = [-1] * point_count
    core = [False] * point_count
    for index, point_id in enumerate(point_ids.tolist()):
        labels[int(point_id)] = int(labels_in[index])
        core[int(point_id)] = bool(core_in[index])
    return {
        "canonical_component_labels": rt.canonical_partition_labels(labels),
        "core_flags": tuple(core),
    }


def _v2(data: dict[str, object], native: Path) -> dict[str, object]:
    points = np.asarray(data["points"], dtype=np.float32)
    rows = tuple(rt.Point3D(
        id=index, x=float(row[0]), y=float(row[1]), z=float(row[2]))
        for index, row in enumerate(points))
    started = time.perf_counter()
    owner = rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
        rows, radius=float(data["epsilon"]), partner="numba")
    prepare_seconds = time.perf_counter() - started
    library = optix_runtime._load_optix_library()
    try:
        with OptixTraversalAuditSession.open(
            library=library, library_path=native) as audit:
            execute_started = time.perf_counter()
            physical = rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                owner, min_neighbors=int(data["min_points"]), return_metadata=True)
            execute_seconds = time.perf_counter() - execute_started
            actual = _project(physical["columns"], len(points))
            output_sha = _digest(actual)
            receipt = audit.finish(
                semantic_digest=str(data["input_sha256"]),
                output_digest=output_sha,
                route_identity="goal5776:rtdbscan:v2_direct:true_optix:clustered4096")
    finally:
        owner.close()
    if actual != data["expected"]:
        raise RuntimeError("V2 RT-DBSCAN output disagrees with frozen oracle")
    if not _receipt_ok(receipt):
        raise RuntimeError("V2 RT-DBSCAN behavioral receipt failed")
    return {
        "matched": True, "output_sha256": output_sha,
        "prepare_seconds_observed_not_formal": prepare_seconds,
        "execute_seconds_observed_not_formal": execute_seconds,
        "traversal_receipt": receipt,
    }


def _v4(app, data: dict[str, object], runtime: dict[str, object]):
    with app.prepare_v4(
        **runtime, points=data["points"], initial_radius=data["epsilon"],
        frozen_expected=data["expected"],
        frozen_input_sha256=data["input_sha256"],
        frozen_epsilon=data["epsilon"],
        frozen_min_points=data["min_points"],
        # The callback emits broad-phase candidates; the exact paper oracle
        # counts only distance-filtered directed edges.  Therefore the safe
        # pre-launch bound is N^2, not the expected exact-edge count.
        maximum_event_capacity=int(len(data["points"])) ** 2,
    ) as owner:
        prepare_seconds = owner.total_prepare_seconds
        result = owner.execute(
            epsilon=data["epsilon"], min_points=data["min_points"])
    if not result["matched"] or not _receipt_ok(result["traversal_receipt"]):
        raise RuntimeError("V4 RT-DBSCAN functional/behavioral gate failed")
    return {
        "matched": True, "output_sha256": _digest(result["output"]),
        "prepare_seconds_observed_not_formal": prepare_seconds,
        "execute_seconds_observed_not_formal": result[
            "registered_prepared_execution_seconds"],
        "traversal_receipt": result["traversal_receipt"],
        "lifecycle_receipt": result["lifecycle_receipt"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load_app(args.source_root.resolve())
    data = app.load_real_scale_v4_input(args.input_root)
    v2 = _v2(data, native)
    v4 = _v4(app, data, _runtime(
        native, args.optix_include.resolve(), args.cuda_include.resolve()))
    if v2["output_sha256"] != v4["output_sha256"]:
        raise RuntimeError("V2/V4 RT-DBSCAN output digest disagreement")
    manifest = data["real_scale_manifest"]
    result = {
        "schema": "rtdl.goal5776.rtdbscan_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "host": platform.node(),
        "gpu_scope": "Home GTX1070 CC6.1 behavioral OptiX; no RT-silicon claim",
        "native_library_sha256": _sha(native),
        "input_manifest_sha256": str(data["input_sha256"]),
        "point_count": int(len(data["points"])),
        "epsilon": data["epsilon"], "min_points": data["min_points"],
        "directed_edge_count": manifest["oracle"]["directed_edge_count"],
        "expected_output_sha256": v2["output_sha256"],
        "v2_direct": v2, "v4": v4,
        "correct_method_count": 2,
        "behavioral_true_optix_method_count": 2,
        "claim_boundary": {
            "largest_declared_admissible_point_count": True,
            "paper_dataset_claimed": False,
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "point_count": result["point_count"],
        "v2_execute": v2["execute_seconds_observed_not_formal"],
        "v4_execute": v4["execute_seconds_observed_not_formal"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
