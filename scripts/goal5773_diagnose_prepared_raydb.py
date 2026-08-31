#!/usr/bin/env python3
"""Create-only, functional-only diagnostic for Goal5773 RayDB preparation."""

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


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load():
    path = ROOT / "Paper-reproduction-apps/raydb-paper/v4_whole_app.py"
    spec = importlib.util.spec_from_file_location("goal5773_raydb_diagnostic", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    app = _load()
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(args.native), supports_custom_aabb=True,
        supports_builtin_triangle=True)
    kwargs = {
        "target": target, "compute_capability": (6, 1),
        "optix_include": args.optix_include, "cuda_include": args.cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": args.native,
    }
    prepared_input = app.build_v4_input()
    with app.prepare_v4(**kwargs) as prepared:
        raw = prepared.owner.execute(prepared_input.queries, query_metadata={})
        prepared_payload = {
            "reduced_output": raw.reduced_output,
            "raw_reducer_rows": raw.raw_reducer_rows,
            "per_ray_u64": raw.per_ray_u64,
            "role_counters": raw.role_counters,
            "physical": raw.traversal_receipt[
                "physical_executor_classification"],
        }
    cold = app.run_v4_complete(**kwargs)
    result = {
        "schema": "rtdl.goal5773.raydb_prepared_diagnostic.v1",
        "native_library_sha256": _sha(args.native),
        "input_sha256": prepared_input.input_sha256,
        "group_values": prepared_input.group_values,
        "primitive_metadata": prepared_input.metadata,
        "expected_keyed_rows": prepared_input.expected_keyed_rows,
        "prepared": prepared_payload,
        "cold": {
            "matched": cold["matched"],
            "output": cold["output"],
            "physical": cold["traversal_receipt"][
                "physical_executor_classification"],
        },
        "formal_performance_row_created": False,
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
