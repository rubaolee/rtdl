#!/usr/bin/env python3
"""Home-GPU Triangle frontdoor validation for Goal5778.

This is functional evidence only.  It records the checked-reduction receipt
for every RT-2A1 segment and verifies that the unweighted RT-1A2 path remains
separate.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import time

import numba
import numpy as np

from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile
from scripts.goal5776_home_triangle_real_scale_smoke import (
    _load,
    _receipt_ok,
    _sha,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--edge-file", required=True, type=Path)
    parser.add_argument("--expected-triangle-count", required=True, type=int)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        "goal5778_triangle_v4",
    )
    runtime = {
        "target": ReferenceTargetProfile(
            provider="optix",
            optix_sdk="9.0.0",
            compute_capability="6.1",
            native_sha256=_sha(native),
            supports_custom_aabb=True,
            supports_builtin_triangle=True,
        ),
        "compute_capability": (6, 1),
        "optix_include": args.optix_include.resolve(),
        "cuda_include": args.cuda_include.resolve(),
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }
    rows = []
    for algorithm in ("RT-1A2", "RT-2A1"):
        prepared = app.prepare_v4_segmented(
            algorithm,
            **runtime,
            edge_file=str(args.edge_file.resolve()),
            expected_triangle_count=args.expected_triangle_count,
            max_relation_rows=args.max_relation_rows,
        )
        try:
            started = time.perf_counter()
            result = prepared.execute()
            observed_seconds = time.perf_counter() - started
        finally:
            prepared.close()
        if not result["matched"] or int(result["output"]["triangle_count"]) \
                != args.expected_triangle_count:
            raise RuntimeError(f"{algorithm} output mismatch")
        if not result["traversal_receipts"] or not all(
            _receipt_ok(item) for item in result["traversal_receipts"]
        ):
            raise RuntimeError(f"{algorithm} behavioral OptiX receipt failed")
        reductions = tuple(
            segment["checked_u64_weighted_reduction"]
            for segment in result["segments"]
        )
        if algorithm == "RT-1A2":
            if any(item is not None for item in reductions):
                raise RuntimeError("unweighted RT-1A2 unexpectedly used weighted reduction")
        else:
            if not reductions or any(item is None for item in reductions):
                raise RuntimeError("RT-2A1 did not use checked reduction in every segment")
            for item in reductions:
                if item["device_kernel_launch_count"] != 1 \
                        or item["host_synchronization_count"] != 1 \
                        or not item["provisional_sum_trusted_only_after_bounds"] \
                        or item["maximum_value"] > item["value_upper_bound"]:
                    raise RuntimeError("checked reduction receipt is invalid")
        rows.append({
            "paper_algorithm": algorithm,
            "matched": True,
            "segment_count": len(result["segments"]),
            "checked_reduction_receipts": reductions,
            "behavioral_true_optix": True,
            "execute_seconds_observed_not_formal": observed_seconds,
        })
    payload = {
        "schema": "rtdl.goal5778.home_triangle_checked_reduction_validation.v1",
        "status": "passed",
        "scope": "functional_and_behavioral_only__timings_nonformal",
        "source": {
            "checked_reduction_sha256": _sha(
                source / "src/rtdsl/v4_checked_u64_device_reduction.py"),
            "triangle_runtime_sha256": _sha(
                source / "src/rtdsl/v4_triangle_reduction_device_runtime.py"),
            "triangle_app_sha256": _sha(
                source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"),
            "native_sha256": _sha(native),
            "edge_file_sha256": _sha(args.edge_file.resolve()),
        },
        "expected_triangle_count": args.expected_triangle_count,
        "rows": rows,
        "claim_boundary": {
            "registered_performance_result": False,
            "target_rtx_saving_predicted": False,
            "paper_algorithm_changed": False,
            "native_changed": False,
            "pod_used": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "passed",
        "algorithms": len(rows),
        "rt2a1_checked_segments": sum(
            len(row["checked_reduction_receipts"])
            for row in rows if row["paper_algorithm"] == "RT-2A1"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
