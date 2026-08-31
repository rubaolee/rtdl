#!/usr/bin/env python3
"""Functional-only counterexamples for Goal5834's withdrawn CPU-capsule claim.

The public curve route defines ordering over OptiX-provider float32 hit events.
These cases preserve why that result must not be relabelled as a universal
closed-capsule CPU-oracle equivalence result.  No timing is taken.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve import (
    BuiltinCurveStaticInput,
    CurveMotionSegmentBatch,
    V4CurveTarget,
    curve_first_contact_source,
)


ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "examples/first_contact_curve/first_contact_oracle.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _f32_from_bits(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


def _load_oracle():
    spec = importlib.util.spec_from_file_location(
        "goal5834_counterexample_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Goal5834 independent oracle is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CASES = (
    {
        "id": "FLOAT32_TIE_ORDERS_APPLICATION_ID",
        "control_points": (
            (0.0, -1.0, 0.0), (0.0, 1.0, 0.0),
            (0.01, -1.0, 0.0), (0.01, 1.0, 0.0),
        ),
        "widths": (0.25, 0.25, 0.25, 0.25),
        "segment_indices": (0, 2),
        "application_ids": (100, 1),
        "queries": (((-1.0e6, 0.0, 0.0), (1.0e6, 0.0, 0.0)),),
        "required_cpu_capsule_reference": ((1, 1056964604, 1),),
        "required_provider_output": ((1, 1056964604, 1),),
        "required_relation": "EXACT_MATCH_AFTER_F32_ORACLE_ORDER_REPAIR",
    },
    {
        "id": "ORDINARY_SCALE_PROVIDER_T_DIFFERS_FROM_CPU_ROOT",
        "control_points": ((-2.0, -1.0, 1.0), (-1.0, 1.0, 2.0)),
        "widths": (0.2, 0.2),
        "segment_indices": (0,),
        "application_ids": (555,),
        "queries": (((
            -0.9590878702997561, 1.1931053085886383, 1.9541103637013393,
        ), (
            2.4671945820539714, -2.85371731402841, -1.7223614664107387,
        )),),
        "required_cpu_capsule_reference": ((1, 983336707, 555),),
        "required_provider_output": ((1, 983337432, 555),),
        "required_relation": "SAME_HIT_AND_ID__DIFFERENT_PROVIDER_T_BITS",
    },
    {
        "id": "NEAR_COINCIDENT_CAPSULES_REORDER_APPLICATION_ID",
        "control_points": (
            (-2.0, -1.0, 1.0), (-1.0, 1.0, 2.0),
            (-2.0, -1.0, 1.0), (-1.0, 1.0, 2.0),
        ),
        "widths": (
            _f32_from_bits(0x3E4CCCCE), _f32_from_bits(0x3E4CCCCE),
            _f32_from_bits(0x3E4CCCCD), _f32_from_bits(0x3E4CCCCD),
        ),
        "segment_indices": (0, 2),
        "application_ids": (1000, 1),
        "queries": (((
            -2.391265976033713, -1.1123559085756902, 0.9287584731586094,
        ), (
            1.7186848663858152, -1.1347605412858597, 0.9746184002928722,
        )),),
        "required_cpu_capsule_reference": ((1, 1030805664, 1000),),
        "required_provider_output": ((1, 1030805698, 1),),
        "required_relation": "PROVIDER_AND_CPU_ORACLE_APPLICATION_ID_DIFFER",
    },
    {
        "id": "UNNORMALIZED_LARGE_TRANSLATION_PROVIDER_MISS",
        "control_points": (
            (999999995904.0, -81920.0, 0.0),
            (999999995904.0, 81920.0, 0.0),
        ),
        "widths": (8192.0, 8192.0),
        "segment_indices": (0,),
        "application_ids": (4,),
        "queries": (((999998947328.0, 0.0, 0.0),
                     (1000001044480.0, 0.0, 0.0)),),
        "required_cpu_capsule_reference": ((1, 1056833536, 4),),
        "required_provider_output": ((0, 1065353216, 0xFFFFFFFF),),
        "required_relation": "CPU_CAPSULE_HIT__PROVIDER_MISS",
    },
)


def _classify(expected, observed) -> str:
    if expected == observed:
        return "EXACT_MATCH_AFTER_F32_ORACLE_ORDER_REPAIR"
    if expected[0][0] == observed[0][0] == 1 \
            and expected[0][2] == observed[0][2] \
            and expected[0][1] != observed[0][1]:
        return "SAME_HIT_AND_ID__DIFFERENT_PROVIDER_T_BITS"
    if expected[0][0] == observed[0][0] == 1 \
            and expected[0][2] != observed[0][2]:
        return "PROVIDER_AND_CPU_ORACLE_APPLICATION_ID_DIFFER"
    if expected[0][0] == 1 and observed[0][0] == 0:
        return "CPU_CAPSULE_HIT__PROVIDER_MISS"
    return "UNEXPECTED_RELATION"


def validate(args) -> dict[str, object]:
    native = args.native.resolve(strict=True)
    oracle = _load_oracle()
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4CurveTarget.from_native(
        native, optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability)
    toolchain = V4Toolchain.current(
        compute_capability=tuple(
            int(value) for value in args.compute_capability.split(".")),
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    rows = []
    for case in CASES:
        expected = oracle.first_contact(
            case["control_points"], case["widths"],
            case["segment_indices"], case["application_ids"],
            case["queries"])
        source = curve_first_contact_source()
        program = source.compile(target=target)
        materialized = program.materialize(toolchain=toolchain)
        prepared = materialized.prepare(BuiltinCurveStaticInput(
            case["control_points"], case["widths"],
            case["segment_indices"], case["application_ids"]))
        with prepared:
            result = prepared.execute(CurveMotionSegmentBatch(case["queries"]))
        if expected != case["required_cpu_capsule_reference"]:
            raise RuntimeError(
                f"CPU capsule reference drift for {case['id']}: "
                f"{expected!r}")
        if result.outputs != case["required_provider_output"]:
            raise RuntimeError(
                f"provider output drift for {case['id']}: "
                f"{result.outputs!r}")
        relation = _classify(expected, result.outputs)
        if relation != case["required_relation"]:
            raise RuntimeError(
                f"counterexample relation drift for {case['id']}: {relation}")
        rows.append({
            "id": case["id"],
            "required_relation": case["required_relation"],
            "cpu_capsule_reference": [list(row) for row in expected],
            "provider_output": [list(row) for row in result.outputs],
            "absolute_t_bits_delta": (
                abs(expected[0][1] - result.outputs[0][1])
                if expected[0][0] == result.outputs[0][0] == 1 else None),
            "public_admission": "ACCEPT",
            "traversal_receipt": result.traversal_receipt,
            "physical_receipt": result.physical_receipt,
            "authority_nonce": program.authority.authority_nonce,
            "physical_schema_sha256": program.authority.schema.schema_sha256,
            "canonical_plan_sha256":
                program.authority.canonical_plan.plan_sha256,
            "executable_sha256": materialized.executable.executable_sha256,
        })
    return {
        "schema": "rtdl.goal5834.numeric_counterexample_validation.v2",
        "status": "PASS__COUNTEREXAMPLES_REPRODUCED",
        "scope": "functional_only_no_performance",
        "registered_performance_timing_count": 0,
        "native_sha256": _sha(native),
        "oracle_sha256": _sha(ORACLE_PATH),
        "conclusion": (
            "CPU_CLOSED_CAPSULE_EQUIVALENCE_IS_NOT_A_SUPPORTED_DOMAIN_CLAIM__"
            "PUBLIC_OUTPUT_ORDERS_PROVIDER_REPORTED_FLOAT32_EVENTS"),
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", default="6.1")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "native_sha256": result["native_sha256"],
        "relations": [row["required_relation"] for row in result["cases"]],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
