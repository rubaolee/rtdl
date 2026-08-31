#!/usr/bin/env python3
"""Observation-only device diagnostic for the Goal5769 particle tie."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rtdsl.v4_builtin_triangle_standard_library import (
    compile_standard_builtin_triangle_program,
)
from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py"


def _load_app():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "goal5769_triangle_tie_diagnostic_app", APP)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load particle V4 app")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runtime = json.loads(args.runtime.read_text(encoding="utf-8"))
    module = _load_app()
    data = module.build_v4_input()
    target = ReferenceTargetProfile(**runtime["target"])
    program = compile_standard_builtin_triangle_program(
        target,
        source_semantics_sha256=module.AUTHOR_SOURCE_SHA256,
        independent_oracle_sha256=data["independent_oracle_sha256"],
        compute_capability=tuple(runtime["compute_capability"]),
        optix_include=Path(runtime["optix_include"]),
        cuda_include=Path(runtime["cuda_include"]),
        expected_python_version=runtime["expected_python_version"],
        expected_numba_version=runtime["expected_numba_version"],
        expected_numpy_version=runtime["expected_numpy_version"],
    )
    result = run_builtin_triangle_callback(
        program.authority, program.plan, program.abi, program.executable,
        vertices=data["vertices"], triangles=data["triangles"],
        front_values=data["front_values"], back_values=data["back_values"],
        queries=data["queries"], expected_output=None,
        native_library_path=runtime["native_library_path"],
    )
    payload = {
        "schema": "rtdl.goal5769.triangle_tie_diagnostic.v1",
        "expected": data["expected"],
        "observed": result.output,
        "hit_observations": result.hit_observations,
        "correct": result.output == data["expected"],
        "behavioral_receipt": result.traversal_receipt,
        "performance_claimed": False,
    }
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
