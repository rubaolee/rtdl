#!/usr/bin/env python3
"""Home functional validation for the explicit V4 multiround lifecycle.

This script creates three owners and performs two semantically distinct calls
through each.  It records no formal performance row and makes no speed claim.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

import numba
import numpy as np

from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


ROOT = Path(__file__).resolve().parents[1]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def _receipt(record: dict[str, object]) -> dict[str, object]:
    traversal = dict(record["traversal_receipt"])
    snapshot = dict(traversal["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    if (
        record["matched"] is not True
        or traversal["physical_executor_classification"]
        != "optix_traversal_observed"
        or successful <= 0
        or int(snapshot["complete_context_launch_count"]) != successful
        or any(int(snapshot[name]) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error"))
        or not snapshot["first_traversable"]
        or not snapshot["last_traversable"]
    ):
        raise RuntimeError("prepared application call lacked exact bound traversal")
    lifecycle = dict(record["lifecycle_receipt"])
    if (
        lifecycle["prepare_seconds_reported_separately"] is not True
        or record["cold_result_replaced"] is not False
        or lifecycle["process_bound"] is not True
        or lifecycle["thread_bound"] is not True
    ):
        raise RuntimeError("prepared application lifecycle receipt is incomplete")
    return {
        "input_sha256": record["input_sha256"],
        "matched": True,
        "output": record["output"],
        "expected": record["expected"],
        "output_sha256": traversal["output_digest"],
        "traversal_receipt_sha256": traversal["receipt_sha256"],
        "provider_library_sha256": traversal["provider_library_sha256"],
        "physical_executor_classification": traversal[
            "physical_executor_classification"],
        "successful_launch_count": successful,
        "complete_context_launch_count": int(
            snapshot["complete_context_launch_count"]),
        "failed_launch_count": int(snapshot["failed_launch_count"]),
        "incomplete_context_launch_count": int(
            snapshot["incomplete_context_launch_count"]),
        "pending_context_at_finish": int(snapshot["pending_context_at_finish"]),
        "session_error": int(snapshot["session_error"]),
        "first_traversable": int(snapshot["first_traversable"]),
        "last_traversable": int(snapshot["last_traversable"]),
        "session_identity": lifecycle["session_identity"],
        "execution_count": lifecycle["execution_count"],
        "registered_prepared_execution_seconds": record[
            "registered_prepared_execution_seconds"],
        "reported_total_prepare_seconds": record[
            "reported_total_prepare_seconds"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    native_sha = _sha(args.native)
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=native_sha, supports_custom_aabb=True,
        supports_builtin_triangle=True)
    kwargs = {
        "target": target,
        "compute_capability": (6, 1),
        "optix_include": args.optix_include,
        "cuda_include": args.cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": args.native,
    }
    modules = {
        "rtnn": _load("goal5773_home_rtnn",
                      "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py"),
        "rt_dbscan": _load(
            "goal5773_home_dbscan",
            "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"),
        "x_hd": _load("goal5773_home_xhd",
                      "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py"),
    }
    records: list[dict[str, object]] = []

    rtnn_data = modules["rtnn"].build_v4_input()
    with modules["rtnn"].prepare_v4(**kwargs) as prepared:
        split = max(1, len(rtnn_data["queries"]) // 2)
        for index, queries in enumerate((
            rtnn_data["queries"][:split], rtnn_data["queries"][split:],
        )):
            if not len(queries):
                queries = rtnn_data["queries"][::-1]
            records.append({
                "application": "rtnn", "call_index": index,
                **_receipt(prepared.execute(queries)),
            })

    with modules["rt_dbscan"].prepare_v4(**kwargs) as prepared:
        # The canonical optimized grouped-union owner prepares an exact
        # fixed-radius OptiX program.  Reuse across clustering requests may
        # vary the algebraic core threshold, but changing epsilon requires a
        # separately prepared owner (and must never be disguised as reuse).
        for index, parameters in enumerate(((0.35, 5), (0.35, 4))):
            records.append({
                "application": "rt_dbscan", "call_index": index,
                "parameters": {"epsilon": parameters[0],
                               "min_points": parameters[1]},
                **_receipt(prepared.execute(
                    epsilon=parameters[0], min_points=parameters[1])),
            })

    xhd_data = modules["x_hd"].build_v4_input()
    with modules["x_hd"].prepare_v4(**kwargs) as prepared:
        sources = xhd_data["sources"]
        split = max(1, len(sources) // 2)
        for index, batch in enumerate((sources[:split], sources[split:])):
            if not len(batch):
                batch = sources[::-1]
            records.append({
                "application": "x_hd", "call_index": index,
                **_receipt(prepared.execute(batch)),
            })

    for application in modules:
        rows = [row for row in records if row["application"] == application]
        if (
            len(rows) != 2
            or len({row["input_sha256"] for row in rows}) != 2
            or len({row["session_identity"] for row in rows}) != 1
            or [row["execution_count"] for row in rows] != [1, 2]
        ):
            raise RuntimeError(f"{application} did not prove distinct cross-call reuse")
    result = {
        "schema": "rtdl.goal5773.home_multiround_lifecycle.v1",
        "native_library_sha256": native_sha,
        "application_count": 3,
        "prepared_owner_count": 3,
        "distinct_dynamic_call_count": 6,
        "exact_output_count": sum(row["matched"] is True for row in records),
        "behavioral_true_optix_count": sum(
            row["physical_executor_classification"]
            == "optix_traversal_observed" for row in records),
        "records": records,
        "formal_performance_row_created": False,
        "cold_result_replaced": False,
        "speed_or_no_slower_claimed": False,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
