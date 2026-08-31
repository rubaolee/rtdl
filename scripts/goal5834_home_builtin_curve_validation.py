#!/usr/bin/env python3
"""Functional-only Home validation for Goal5834 round-linear curves.

No timing is taken.  The expected rows come from the stdlib-only capsule
oracle before the public RTDL lifecycle is entered.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve import (
    BuiltinCurveStaticInput,
    CurveMotionSegmentBatch,
    CurvePhysicalSchemaError,
    V4CurveTarget,
    curve_first_contact_source,
)
from rtdsl.v4_curve_physical_schema import (
    verify_curve_first_contact_expected_outputs,
    verify_curve_motion_segments,
    verify_reference_curve_contents,
)


ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "examples/first_contact_curve/first_contact_oracle.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_f32_evidence(values):
    projected, bits = [], []
    for value in values:
        raw = struct.pack("<f", float(value))
        bits.append(struct.unpack("<I", raw)[0])
        projected.append(None if math.isnan(float(value)) else float(value))
    return projected, bits


def _load_oracle():
    spec = importlib.util.spec_from_file_location(
        "goal5834_independent_curve_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Goal5834 independent oracle is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture():
    # A and A' are byte-identical capsules with different application IDs.
    # B has a smaller radius but an earlier entry than C, whose application ID
    # is smaller.  D is contacted through the round start cap only.
    return {
        "control_points": (
            (0.0, -1.0, 0.0), (0.0, 1.0, 0.0),
            (0.0, -1.0, 0.0), (0.0, 1.0, 0.0),
            (-0.5, -1.0, 3.0), (-0.5, 1.0, 3.0),
            (0.5, -1.0, 3.0), (0.5, 1.0, 3.0),
            (2.0, 0.0, 6.0), (3.0, 0.0, 6.0),
        ),
        "widths": (
            0.25, 0.25, 0.25, 0.25, 0.125,
            0.125, 0.25, 0.25, 0.5, 0.5,
        ),
        "segment_indices": (0, 2, 4, 6, 8),
        "application_ids": (100, 50, 900, 1, 77),
        "queries": (
            ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
            ((-1.0, 2.0, 0.0), (1.0, 2.0, 0.0)),
            ((-1.0, 0.0, 3.0), (1.0, 0.0, 3.0)),
            ((1.75, 1.0, 6.0), (1.75, -1.0, 6.0)),
        ),
        "fixture_names": (
            "side_hit_equal_time_stable_application_id",
            "miss",
            "earlier_time_precedes_smaller_application_id",
            "round_endcap_only_hit",
        ),
    }


def _write_artifacts(root: Path, verified, materialized) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=False)
    executable = materialized.executable
    bodies = {
        "callback_source.py": verified.source._source.encode("utf-8"),
        "wrapper.cu": executable.wrapper.source.encode("utf-8"),
        "wrapper.ptx": executable.wrapper_ptx.encode("utf-8"),
        "composed.ptx": executable.composed.ptx.encode("utf-8"),
        "nvrtc.log": materialized.compiler_log.encode("utf-8"),
    }
    for index, leaf in enumerate(executable.generated_leaves):
        bodies[f"leaf_{index}_{leaf.role.value}.py"] = \
            leaf.generated_source.encode("utf-8")
    for index, leaf in enumerate(executable.compiled_leaves):
        bodies[f"leaf_{index}_{leaf.role}.ptx"] = leaf.ptx.encode("utf-8")
    members = []
    for name, body in sorted(bodies.items()):
        (root / name).write_bytes(body)
        members.append({
            "path": name, "size": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
    manifest = {
        "schema": "rtdl.goal5834.curve_executable_artifacts.v1",
        "executable_sha256": executable.executable_sha256,
        "member_count": len(members),
        "members": members,
    }
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    (root / "manifest.json").write_bytes(payload)
    return {
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
        **manifest,
    }


def validate(args) -> dict[str, object]:
    native = args.native.resolve(strict=True)
    oracle = _load_oracle()
    fixture = _fixture()
    expected = oracle.first_contact(
        fixture["control_points"], fixture["widths"],
        fixture["segment_indices"], fixture["application_ids"],
        fixture["queries"])
    required_expected = (
        (1, struct.unpack("<I", struct.pack("<f", 0.375))[0], 50),
        (0, struct.unpack("<I", struct.pack("<f", 1.0))[0], 0xFFFFFFFF),
        (1, struct.unpack("<I", struct.pack("<f", 0.1875))[0], 900),
        (1, 1049699860, 77),
    )
    if expected != required_expected:
        raise RuntimeError("Goal5834 independent fixture expectation drift")

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
    source = curve_first_contact_source()
    verified = source.compile(target=target)
    materialized = verified.materialize(toolchain=toolchain)
    artifacts = _write_artifacts(
        args.artifact_dir.resolve() / "accepted", verified, materialized)
    prepared = materialized.prepare(BuiltinCurveStaticInput(
        fixture["control_points"], fixture["widths"],
        fixture["segment_indices"], fixture["application_ids"]))
    with prepared:
        before = prepared.lifecycle_receipt
        result = prepared.execute(CurveMotionSegmentBatch(fixture["queries"]))
        if result.outputs != expected:
            raise RuntimeError(
                "curve GPU output differs from independent oracle: "
                f"observed={result.outputs!r}, expected={expected!r}")
        normalized_static = verify_reference_curve_contents(
            fixture["control_points"], fixture["widths"],
            fixture["segment_indices"], fixture["application_ids"])
        normalized_queries = verify_curve_motion_segments(
            tuple(row[0] for row in fixture["queries"]),
            tuple(row[1] for row in fixture["queries"]),
            control_points=normalized_static[0], widths=normalized_static[1],
            segment_indices=normalized_static[2])
        comparison_policies = verify_curve_first_contact_expected_outputs(
            result.outputs, expected, normalized_queries,
            control_points=normalized_static[0], widths=normalized_static[1],
            segment_indices=normalized_static[2],
            application_ids=normalized_static[3])
        after_first = prepared.lifecycle_receipt
        reversed_queries = tuple(reversed(fixture["queries"]))
        reversed_expected = oracle.first_contact(
            fixture["control_points"], fixture["widths"],
            fixture["segment_indices"], fixture["application_ids"],
            reversed_queries)
        repeated = prepared.execute(
            CurveMotionSegmentBatch(reversed_queries),
            expected_output=reversed_expected)
        after_second = prepared.lifecycle_receipt

        # Exact tangency is a mathematically defined capsule contact, but is
        # deliberately outside the provider-stable numeric domain.  It must
        # fail before native launch and leave the execution count unchanged.
        tangent = (((-1.0, 1.25, 0.0), (1.0, 1.25, 0.0)),)
        tangent_error = None
        try:
            prepared.execute(CurveMotionSegmentBatch(tangent))
        except CurvePhysicalSchemaError as exc:
            tangent_error = {"code": exc.code, "message": str(exc)}
        if tangent_error is None or tangent_error["code"] != \
                "near_tangent_curve_contact":
            raise RuntimeError("exact tangent did not fail before curve launch")
        after_tangent = prepared.lifecycle_receipt

        # The first hardware attempt showed that an exactly axial ray can be
        # missed by the built-in round-linear provider even though the closed
        # capsule oracle intersects the round endcap.  It is therefore an
        # explicit post-observation exclusion, enforced before launch.
        axial = (((1.0, 0.0, 6.0), (2.5, 0.0, 6.0)),)
        axial_oracle = oracle.first_contact(
            fixture["control_points"], fixture["widths"],
            fixture["segment_indices"], fixture["application_ids"], axial)
        axial_error = None
        try:
            prepared.execute(CurveMotionSegmentBatch(axial))
        except CurvePhysicalSchemaError as exc:
            axial_error = {"code": exc.code, "message": str(exc)}
        if axial_oracle[0][0] != 1 or axial_error is None \
                or axial_error["code"] != "near_parallel_curve_query":
            raise RuntimeError("axial curve/provider boundary was not enforced")
        after_axial = prepared.lifecycle_receipt

    use_after_close_rejected = False
    try:
        prepared.execute(CurveMotionSegmentBatch(fixture["queries"]))
    except RuntimeError:
        use_after_close_rejected = True
    if not use_after_close_rejected:
        raise RuntimeError("curve lifecycle allowed use after close")
    if before["execution_count"] != 0 \
            or after_first["execution_count"] != 1 \
            or after_second["execution_count"] != 2 \
            or after_tangent["execution_count"] != 2 \
            or after_axial["execution_count"] != 2:
        raise RuntimeError("curve lifecycle execution count differs")
    if result.outputs != expected or repeated.outputs != reversed_expected:
        raise RuntimeError("curve GPU output differs from independent oracle")
    if result.traversal_receipt["physical_executor_classification"] != \
            "optix_traversal_observed":
        raise RuntimeError("curve execution did not observe OptiX traversal")
    descriptor = result.physical_receipt["native_descriptor"]
    required_descriptor = {
        "build_input_type": 0x2145,
        "primitive_type": 0x2503,
        "primitive_type_flags": 1 << 3,
        "builtin_is_build_flags": 1 << 2,
        "builtin_is_curve_endcap_flags": 0,
        "build_flags": 1 << 2,
        "geometry_flags": 1 << 1,
        "primitive_index_offset": 0,
        "sbt_record_count": 1,
        "gas_count": 1,
        "motion_key_count": 0,
        "endcap_flags": 0,
        "max_trace_depth": 1,
        "program_group_count": 3,
    }
    if any(descriptor.get(key) != value
           for key, value in required_descriptor.items()):
        raise RuntimeError("curve native descriptor differs from frozen leaves")
    if descriptor["builtin_is_module"] is not True \
            or descriptor["user_intersection_program"] is not False \
            or descriptor["uses_motion_blur"] is not False:
        raise RuntimeError("curve built-in intersection identity differs")
    observed_t_json, observed_t_bits = _raw_f32_evidence(
        result.observed_t_values)

    return {
        "schema": "rtdl.goal5834.home_builtin_curve_validation.v1",
        "status": "PASS",
        "scope": "functional_only_no_performance",
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "prospective_generalization_claimed": False,
        "paper_app_claimed": False,
        "native_path": str(native),
        "native_sha256": _sha(native),
        "oracle_path": str(ORACLE_PATH),
        "oracle_sha256": _sha(ORACLE_PATH),
        "source_sha256": source.source_sha256,
        "callback_ir_sha256": verified.authority.callback.ir_sha256,
        "callback_effect_digest": verified.authority.callback.effect_digest,
        "physical_schema_sha256": verified.authority.schema.schema_sha256,
        "canonical_plan_sha256": verified.authority.canonical_plan.plan_sha256,
        "callback_abi_sha256": verified.abi.abi_sha256,
        "wrapper_source_sha256": verified.wrapper.source_sha256,
        "executable_sha256": materialized.executable.executable_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "fixture_names": list(fixture["fixture_names"]),
        "control_points": [list(row) for row in fixture["control_points"]],
        "widths": list(fixture["widths"]),
        "segment_indices": list(fixture["segment_indices"]),
        "application_ids": list(fixture["application_ids"]),
        "queries": [[list(start), list(end)]
                    for start, end in fixture["queries"]],
        "expected": [list(row) for row in expected],
        "observed": [list(row) for row in result.outputs],
        "expected_comparison_policies": list(
            comparison_policies),
        "observed_primitive_indices": list(
            result.observed_primitive_indices),
        "observed_hit_kinds": list(result.observed_hit_kinds),
        "observed_t": observed_t_json,
        "observed_t_f32_bits": observed_t_bits,
        "device_status": list(result.statuses),
        "role_counters": list(result.counters),
        "physical_receipt": result.physical_receipt,
        "traversal_receipt": result.traversal_receipt,
        "repeat_observed": [list(row) for row in repeated.outputs],
        "tangent_prelaunch_rejection": tangent_error,
        "axial_provider_boundary": {
            "status": "POST_OBSERVATION_FAIL_CLOSED_EXCLUSION",
            "independent_closed_capsule_oracle": list(axial_oracle[0]),
            "rejection": axial_error,
            "native_launch_occurred": False,
        },
        "lifecycle_counts": {
            "before": before["execution_count"],
            "after_first": after_first["execution_count"],
            "after_second": after_second["execution_count"],
            "after_tangent": after_tangent["execution_count"],
            "after_axial": after_axial["execution_count"],
        },
        "use_after_close_rejected": use_after_close_rejected,
        "artifacts": artifacts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", default="6.1")
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "native_sha256": result["native_sha256"],
        "executable_sha256": result["executable_sha256"],
        "observed": result["observed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
