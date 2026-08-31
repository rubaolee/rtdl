#!/usr/bin/env python3
"""Post-failure diagnostic for the Goal5833 Home tangent mismatch.

This is not a formal-result runner.  It deliberately omits expected-output
admission so the already-launched native rows can be recorded for root-cause
analysis after the first formal attempt failed at expected row 3.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_sphere import (
    BuiltinSphereStaticInput,
    MotionSegmentBatch,
    V4SphereTarget,
    first_contact_source,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load diagnostic dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runner = _load(
        ROOT / "scripts/goal5833_home_builtin_sphere_validation.py",
        "goal5833_failed_runner_bytes",
    )
    oracle = _load(
        ROOT / "examples/first_contact_sphere/first_contact_oracle.py",
        "goal5833_independent_oracle_bytes",
    )
    fixture = runner._first_contact_fixture()
    centers = fixture["centers"]
    radii = fixture["radii"]
    application_ids = fixture["application_ids"]
    queries = fixture["queries"]
    expected = tuple(
        oracle.first_contact(start, end, centers, radii, application_ids)
        for start, end in queries
    )

    native = args.native.resolve(strict=True)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4SphereTarget.from_native(
        native, optix_sdk="9.0.0", compute_capability="6.1")
    toolchain = V4Toolchain.current(
        compute_capability=(6, 1),
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    prepared = first_contact_source().compile(target=target).materialize(
        toolchain=toolchain).prepare(BuiltinSphereStaticInput(
            centers, radii, application_ids))
    try:
        result = prepared.execute(MotionSegmentBatch(queries))
        payload = {
            "schema": "rtdl.goal5833.postfailure_diagnostic.v1",
            "formal_result_claimed": False,
            "reason": "formal_attempt_expected_output_3_identity_mismatch",
            "fixture_names": list(fixture["fixture_names"]),
            "expected": [list(row) for row in expected],
            "observed": [list(row) for row in result.outputs],
            "hit_rows": list(result.hit_rows),
            "observed_primitive_indices_raw": list(
                result.observed_primitive_indices),
            "observed_hit_kinds_raw": list(result.observed_hit_kinds),
            "observed_t_values_raw": list(result.observed_t_values),
            "device_status": list(result.statuses),
            "role_counters": list(result.counters),
            "physical_receipt": result.physical_receipt,
            "traversal_receipt": result.traversal_receipt,
        }
    finally:
        prepared.close()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "expected": payload["expected"], "observed": payload["observed"],
        "hit_rows": payload["hit_rows"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
