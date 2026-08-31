#!/usr/bin/env python3
"""Untimed Home gate for LibRTS parks 11.5M x 100K count queries."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

import rtdsl as rt
from rtdsl.optix_runtime import _load_optix_library
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


EXPECTED = {"point_contains": 112729, "range_contains": 105826}


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


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    row = dict(receipt["native_snapshot"])
    successful = int(row["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(row["complete_context_launch_count"]) == successful
        and all(int(row[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        and bool(row["first_traversable"]) and bool(row["last_traversable"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--cache-npz", required=True, type=Path)
    parser.add_argument("--cache-json", required=True, type=Path)
    parser.add_argument("--point-queries", required=True, type=Path)
    parser.add_argument("--range-queries", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load(root / "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
                "goal5776_librts_v4")
    loaders = _load(
        root / "Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py",
        "goal5776_librts_loaders")
    metadata = json.loads(args.cache_json.read_text(encoding="utf-8"))
    with np.load(args.cache_npz, allow_pickle=False) as arrays:
        indexed = rt.Aabb2DColumns(
            ids=arrays["ids"], min_x=arrays["min_x"], min_y=arrays["min_y"],
            max_x=arrays["max_x"], max_y=arrays["max_y"])
    if len(indexed) != 11_544_398 or len(indexed) != int(metadata["row_count"]):
        raise RuntimeError("unexpected LibRTS parks cache cardinality")
    point_queries = loaders.load_point_queries(args.point_queries)
    range_columns = loaders.load_geometry_mbr_columns_fast(args.range_queries)
    range_queries = tuple(range_columns)
    if len(point_queries) != 100_000 or len(range_queries) != 100_000:
        raise RuntimeError("unexpected LibRTS query cardinality")
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(native), supports_custom_aabb=True,
        supports_builtin_triangle=True)

    v4_rows = {}
    for operation, kwargs in (
        ("point_contains", {"point_queries": point_queries}),
        ("range_contains", {"box_queries": range_queries}),
    ):
        prepare_started = time.perf_counter()
        with app.prepare_v4_real_scale_count(
            target=target, indexed_columns=indexed, operation=operation,
            native_library_path=native) as owner:
            prepare_seconds = time.perf_counter() - prepare_started
            execute_started = time.perf_counter()
            observed = owner.execute_count(**kwargs)
            execute_seconds = time.perf_counter() - execute_started
            lifecycle = owner.lifecycle_receipt
        if observed["count"] != EXPECTED[operation] \
                or not _receipt_ok(observed["traversal_receipt"]):
            raise RuntimeError(f"V4 LibRTS {operation} gate failed")
        v4_rows[operation] = {
            "count": observed["count"],
            "prepare_seconds_observed_not_formal": prepare_seconds,
            "execute_seconds_observed_not_formal": execute_seconds,
            "physical_lowering": observed["physical_lowering"],
            "lifecycle_receipt": lifecycle,
            "traversal_receipt": observed["traversal_receipt"],
        }

    library = _load_optix_library()
    v2_prepare_started = time.perf_counter()
    owner = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    try:
        v2_prepare = time.perf_counter() - v2_prepare_started
        v2_rows = {}
        for operation, kwargs in (
            ("point_contains", {"point_queries": point_queries}),
            ("range_contains", {"box_queries": range_queries}),
        ):
            with OptixTraversalAuditSession.open(
                    library=library, library_path=native) as audit:
                started = time.perf_counter()
                observed = owner.count(operation=operation, **kwargs)
                elapsed = time.perf_counter() - started
                value = int(observed["counts"][operation])
                receipt = audit.finish(
                    semantic_digest=_digest({
                        "operation": operation,
                        "indexed": len(indexed), "queries": 100_000}),
                    output_digest=_digest({"count": value}),
                    route_identity=f"goal5776:librts:v2_direct:{operation}:optix")
            if value != EXPECTED[operation] or not _receipt_ok(receipt):
                raise RuntimeError(f"V2 LibRTS {operation} gate failed")
            v2_rows[operation] = {
                "count": value,
                "execute_seconds_observed_not_formal": elapsed,
                "traversal_receipt": receipt,
            }
    finally:
        owner.close()

    result = {
        "schema": "rtdl.goal5776.librts_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "indexed_box_count": len(indexed), "query_count_per_operation": 100_000,
        "cache_npz_sha256": _sha(args.cache_npz),
        "point_query_sha256": _sha(args.point_queries),
        "range_query_sha256": _sha(args.range_queries),
        "native_library_sha256": _sha(native),
        "expected_counts": EXPECTED,
        "v4": v4_rows,
        "v2_direct": {"prepare_seconds_observed_not_formal": v2_prepare,
                      "operations": v2_rows},
        "claim_boundary": {
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "author_runtime_ratio_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({"status": "passed", "counts": EXPECTED}, sort_keys=True))


if __name__ == "__main__":
    main()
