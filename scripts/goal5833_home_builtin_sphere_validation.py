#!/usr/bin/env python3
"""Functional-only Home-Linux validation for Goal5833 First Contact.

The runner records no timing.  Expected rows are computed by the independent
stdlib-only oracle in ``examples/first_contact_sphere`` before the public RTDL
lifecycle is entered.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import pickle
from pathlib import Path
import struct
import threading

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_sphere import (
    BuiltinSphereStaticInput,
    MotionSegmentBatch,
    SpherePhysicalSchemaError,
    V4SphereTarget,
    first_contact_source,
    verify_builtin_sphere_callback_source,
)
from rtdsl.v4_builtin_sphere_standard_library import (
    FIRST_CONTACT_SOURCE,
    first_contact_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "examples/first_contact_sphere/first_contact_oracle.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _load_oracle():
    spec = importlib.util.spec_from_file_location(
        "goal5833_independent_first_contact_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("independent First Contact oracle is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_executable_artifacts(
    root: Path, materialized, verified, *, compiler_log: str,
) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=False)
    executable = materialized.executable
    payloads: dict[str, bytes] = {
        "callback_source.py": verified.source._source.encode("utf-8"),
        "wrapper.cu": executable.wrapper.source.encode("utf-8"),
        "wrapper.ptx": executable.wrapper_ptx.encode("utf-8"),
        "composed.ptx": executable.composed.ptx.encode("utf-8"),
        "nvrtc.log": compiler_log.encode("utf-8"),
        "compiler_options.json": (
            json.dumps(list(executable.compiler_options), indent=2) + "\n"
        ).encode("utf-8"),
    }
    for index, leaf in enumerate(executable.generated_leaves):
        payloads[f"leaf_{index}_{leaf.role.value}.py"] = \
            leaf.generated_source.encode("utf-8")
    for index, leaf in enumerate(executable.compiled_leaves):
        payloads[f"leaf_{index}_{leaf.role}.ptx"] = leaf.ptx.encode("utf-8")
    members = []
    for name, body in sorted(payloads.items()):
        path = root / name
        path.write_bytes(body)
        members.append({
            "path": name, "size": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
    authority = verified.authority
    target_projection = {
        "provider": authority.target.provider,
        "optix_sdk": authority.target.optix_sdk,
        "compute_capability": authority.target.compute_capability,
        "native_sha256": authority.target.native_sha256,
        "supports_builtin_sphere": authority.target.supports_builtin_sphere,
        "max_graph_depth": authority.target.max_graph_depth,
    }
    authority_projection = {
        "callback_ir_sha256": authority.callback.ir_sha256,
        "callback_effect_digest": authority.callback.effect_digest,
        "schema_sha256": authority.schema.schema_sha256,
        "target_sha256": authority.target.target_sha256,
        "authority_nonce": authority.authority_nonce,
    }
    executable_record = {
        "schema": executable.schema,
        "authority_sha256": _canonical_sha256(authority_projection),
        "plan_sha256": authority.canonical_plan.plan_sha256,
        "abi_sha256": verified.abi.abi_sha256,
        "wrapper_source_sha256": executable.wrapper.source_sha256,
        "wrapper_ptx_sha256": executable.wrapper_ptx_sha256,
        "generated_leaf_sha256": [
            item.generated_source_sha256 for item in executable.generated_leaves],
        "compiled_leaf_sha256": [
            item.ptx_sha256 for item in executable.compiled_leaves],
        "composed_ptx_sha256": executable.composed.ptx_sha256,
        "compiler_options": list(executable.compiler_options),
        "nvrtc_log_sha256": hashlib.sha256(
            compiler_log.encode("utf-8")).hexdigest(),
    }
    compiler_identity = {
        "schema": "rtdl.goal5833.sphere_compiler_identity_projection.v1",
        "callback_program": authority.callback.program.to_dict(),
        "public_source_sha256": verified.source.source_sha256,
        "verified_callback": authority.callback.to_dict(),
        "physical_schema": authority.schema.semantic_dict(),
        "target": target_projection,
        "canonical_plan": authority.canonical_plan.semantic_dict(),
        "callback_abi": verified.abi.to_dict(),
        "authority": authority_projection,
        "authority_sha256": _canonical_sha256(authority_projection),
        "executable_record": executable_record,
    }
    if _canonical_sha256(executable_record) != executable.executable_sha256:
        raise RuntimeError("exported executable record does not rederive identity")
    manifest = {
        "schema": "rtdl.goal5833.generated_executable_artifacts.v2",
        "executable_sha256": executable.executable_sha256,
        "compiler_identity": compiler_identity,
        "member_count": len(members),
        "members": members,
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (root / "manifest.json").write_bytes(manifest_bytes)
    return {
        "subdirectory": root.name,
        "executable_sha256": executable.executable_sha256,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "compiler_identity": compiler_identity,
        "member_count": len(members),
        "members": members,
    }


def _comparison_outcomes(observed, expected, policies):
    return [{
        "row": index,
        "policy": policy,
        "exact_bits": tuple(actual) == tuple(gold),
        "toi_ulp_distance": abs(int(actual[1]) - int(gold[1])),
    } for index, (actual, gold, policy) in enumerate(
        zip(observed, expected, policies))]


def _raw_t_evidence(values) -> tuple[list[float | None], list[int]]:
    """Preserve f32 identity without serializing non-standard JSON NaNs."""

    projected: list[float | None] = []
    bits: list[int] = []
    for value in values:
        raw = struct.pack("<f", float(value))
        bits.append(struct.unpack("<I", raw)[0])
        projected.append(None if math.isnan(float(value)) else float(value))
    return projected, bits


def _first_contact_fixture() -> dict[str, tuple]:
    """Return the frozen A3 hardware fixture without importing the oracle."""

    # Five static spheres exercise different radii in one GAS.  The final
    # sphere has a binary-exact, nondegenerate grazing front-face entry for the
    # y=8 segment.  Exact tangency is tested separately as a prelaunch reject:
    # OptiX's built-in sphere contract does not guarantee D dot N == 0 as a hit.
    return {
        "centers": (
            (3.0, 0.0, 0.0),
            (3.0, 0.0, 0.0),
            (3.0, 4.0, 0.0),
            (6.0, 4.0, 0.0),
            (2.0, 9.0, 0.0),
        ),
        "radii": (1.0, 1.0, 0.5, 1.5, 1.25),
        "application_ids": (9, 2, 99, 1, 11),
        "queries": (
            ((0.0, 0.0, 0.0), (4.0, 0.0, 0.0)),
            ((0.0, 2.0, 0.0), (8.0, 2.0, 0.0)),
            ((0.0, 4.0, 0.0), (8.0, 4.0, 0.0)),
            ((0.0, 8.0, 0.0), (4.0, 8.0, 0.0)),
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ),
        "fixture_names": (
            "equal_time_stable_application_id",
            "transverse_miss",
            "nearer_time_precedes_application_id",
            "grazing_front_face_entry",
            "beyond_tmax_miss",
        ),
    }


def validate(args: argparse.Namespace) -> dict[str, object]:
    native = args.native.resolve(strict=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    oracle = _load_oracle()

    fixture = _first_contact_fixture()
    centers = fixture["centers"]
    radii = fixture["radii"]
    application_ids = fixture["application_ids"]
    queries = fixture["queries"]
    expected = tuple(
        oracle.first_contact(start, end, centers, radii, application_ids)
        for start, end in queries
    )
    fixture_names = fixture["fixture_names"]

    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4SphereTarget.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )
    source = first_contact_source()
    verified = source.compile(target=target)
    materialized = verified.materialize(toolchain=toolchain)
    accepted_artifacts = _write_executable_artifacts(
        args.artifact_dir.resolve() / "accepted",
        materialized, verified, compiler_log=materialized.compiler_log)
    prepared = materialized.prepare(BuiltinSphereStaticInput(
        centers, radii, application_ids))
    with prepared:
        before = prepared.lifecycle_receipt
        result = prepared.execute(
            MotionSegmentBatch(queries), expected_output=expected)
        after_first = prepared.lifecycle_receipt

        repeat_queries = tuple(reversed(queries[2:]))
        repeat_expected = tuple(
            oracle.first_contact(start, end, centers, radii, application_ids)
            for start, end in repeat_queries)
        repeat_result = prepared.execute(
            MotionSegmentBatch(repeat_queries), expected_output=repeat_expected)
        after = prepared.lifecycle_receipt

        # Keep the mathematical closed-sphere tangent in the independent
        # oracle, but require the public GPU path to reject it before launch.
        exact_tangent_queries = (
            ((0.0, 7.75, 0.0), (4.0, 7.75, 0.0)),
        )
        exact_tangent_expected = tuple(
            oracle.first_contact(start, end, centers, radii, application_ids)
            for start, end in exact_tangent_queries)
        tangent_before = prepared.lifecycle_receipt
        exact_tangent_error = None
        try:
            prepared.execute(MotionSegmentBatch(exact_tangent_queries))
        except SpherePhysicalSchemaError as exc:
            exact_tangent_error = str(exc)
            if exc.code != \
                    "exact_tangent_unsupported_by_optix9_front_face_contract":
                raise
        tangent_after = prepared.lifecycle_receipt
        if exact_tangent_error is None:
            raise RuntimeError("exact tangent reached the native sphere path")
        if tangent_before["execution_count"] != 2 \
                or tangent_after["execution_count"] != 2:
            raise RuntimeError("exact tangent changed native execution count")

        # A front-face entry immediately outside tmax can round onto the
        # closed OptiX trace interval.  Preserve the exact oracle miss and
        # require the public path to reject the numerically ambiguous pair
        # before any native launch.
        endpoint_queries = (
            ((0.0, 0.0, 0.0), (
                struct.unpack("<f", struct.pack("<I", 0x3FFFFFFF))[0],
                0.0, 0.0)),
        )
        endpoint_expected = tuple(
            oracle.first_contact(start, end, centers, radii, application_ids)
            for start, end in endpoint_queries)
        if endpoint_expected != ((0, oracle.f32_bits(1.0), oracle.U32_MAX),):
            raise RuntimeError("trace-endpoint independent oracle is not MISS")
        endpoint_before = prepared.lifecycle_receipt
        endpoint_error = None
        try:
            prepared.execute(MotionSegmentBatch(endpoint_queries))
        except SpherePhysicalSchemaError as exc:
            endpoint_error = str(exc)
            if exc.code != "front_entry_near_closed_trace_interval_boundary":
                raise
        endpoint_after = prepared.lifecycle_receipt
        if endpoint_error is None:
            raise RuntimeError("trace-endpoint ambiguity reached native sphere path")
        if endpoint_before["execution_count"] != 2 \
                or endpoint_after["execution_count"] != 2:
            raise RuntimeError("trace-endpoint ambiguity changed native execution count")

        # Test exact tmax separately: fail-fast validation means putting this
        # in the previous batch would only prove that one of the two rows was
        # rejected.  The closed-sphere oracle calls this a hit, while the
        # bounded built-in-sphere provider deliberately excludes the endpoint.
        exact_tmax_queries = (
            ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0)),
        )
        exact_tmax_expected = tuple(
            oracle.first_contact(start, end, centers, radii, application_ids)
            for start, end in exact_tmax_queries)
        if exact_tmax_expected != ((1, oracle.f32_bits(1.0), 2),):
            raise RuntimeError("exact-tmax independent oracle is not the stable hit")
        exact_tmax_before = prepared.lifecycle_receipt
        exact_tmax_error = None
        try:
            prepared.execute(MotionSegmentBatch(exact_tmax_queries))
        except SpherePhysicalSchemaError as exc:
            exact_tmax_error = str(exc)
            if exc.code != "front_entry_near_closed_trace_interval_boundary":
                raise
        exact_tmax_after = prepared.lifecycle_receipt
        if exact_tmax_error is None:
            raise RuntimeError("exact-tmax contact reached native sphere path")
        if exact_tmax_before["execution_count"] != 2 \
                or exact_tmax_after["execution_count"] != 2:
            raise RuntimeError("exact-tmax contact changed native execution count")

        serialization_rejected = False
        try:
            pickle.dumps(prepared)
        except (RuntimeError, TypeError, pickle.PicklingError):
            serialization_rejected = True
        if not serialization_rejected:
            raise RuntimeError("prepared sphere program was serializable")

        cross_thread_errors: list[str] = []

        def cross_thread_probe() -> None:
            try:
                prepared.lifecycle_receipt
            except RuntimeError as exc:
                cross_thread_errors.append(str(exc))

        probe = threading.Thread(target=cross_thread_probe)
        probe.start(); probe.join()
        thread_boundary_rejected = (
            cross_thread_errors
            == ["prepared built-in sphere owner crossed thread boundary"])
        if not thread_boundary_rejected:
            raise RuntimeError(
                "prepared sphere thread boundary did not fail closed: "
                + repr(cross_thread_errors))

    use_after_close_rejected = False
    try:
        prepared.execute(MotionSegmentBatch(queries), expected_output=expected)
    except RuntimeError:
        use_after_close_rejected = True
    if not use_after_close_rejected:
        raise RuntimeError("prepared sphere program allowed use after close")
    double_close_rejected = False
    try:
        prepared.close()
    except RuntimeError:
        double_close_rejected = True
    if not double_close_rejected:
        raise RuntimeError("prepared sphere program allowed double close")

    # Regression for the A3 failure path: a post-launch expected-output
    # exception must unwind through the context manager and release the native
    # token instead of crashing in libnvoptix during DSO teardown.
    # A materialized executable is intentionally single-consume.  Build an
    # independent executable for this cleanup regression instead of forging a
    # second owner from the accepted executable that produced the main result.
    cleanup_source = first_contact_source()
    cleanup_verified = cleanup_source.compile(target=target)
    cleanup_materialized = cleanup_verified.materialize(toolchain=toolchain)
    mismatch_prepared = cleanup_materialized.prepare(BuiltinSphereStaticInput(
        centers, radii, application_ids))
    wrong_expected = ((expected[0][0], expected[0][1], expected[0][2] ^ 1),)
    mismatch_error = None
    try:
        with mismatch_prepared:
            mismatch_prepared.execute(
                MotionSegmentBatch((queries[0],)),
                expected_output=wrong_expected,
            )
    except SpherePhysicalSchemaError as exc:
        mismatch_error = str(exc)
    if mismatch_error is None:
        raise RuntimeError("intentional expected-output mismatch was accepted")
    mismatch_cleanup_closed = False
    try:
        mismatch_prepared.lifecycle_receipt
    except RuntimeError:
        mismatch_cleanup_closed = True
    if not mismatch_cleanup_closed:
        raise RuntimeError("expected-output exception leaked its prepared owner")

    if len(result.expected_comparison_policies) != len(expected) \
            or len(repeat_result.expected_comparison_policies) != len(repeat_expected):
        raise RuntimeError("policy-aware expected-output comparison was not recorded")
    if result.traversal_receipt["physical_executor_classification"] \
            != "optix_traversal_observed":
        raise RuntimeError("true OptiX traversal was not observed")
    if result.traversal_receipt["expected_program_observed_at_receipt_edge"] \
            is not True:
        raise RuntimeError("expected sphere program was not observed")
    if before["execution_count"] != 0 \
            or after_first["execution_count"] != 1 \
            or after["execution_count"] != 2:
        raise RuntimeError("prepared lifecycle execution count differs")

    observed_t_values_raw, observed_t_f32_bits_raw = _raw_t_evidence(
        result.observed_t_values)
    repeat_t_values_raw, repeat_t_f32_bits_raw = _raw_t_evidence(
        repeat_result.observed_t_values)

    hostile_text = FIRST_CONTACT_SOURCE.replace(
        "tmax=ONE_F32", "tmax=ZERO_F32", 1)
    if hostile_text == FIRST_CONTACT_SOURCE:
        raise RuntimeError("hostile ZERO_F32 source mutation did not apply")
    hostile_source = verify_builtin_sphere_callback_source(
        hostile_text, first_contact_manifest())
    hostile_verified = hostile_source.compile(target=target)
    hostile_materialized = hostile_verified.materialize(toolchain=toolchain)
    hostile_artifacts = _write_executable_artifacts(
        args.artifact_dir.resolve() / "hostile_zero_tmax",
        hostile_materialized, hostile_verified,
        compiler_log=hostile_materialized.compiler_log)
    hostile_error = None
    hostile_prepared = hostile_materialized.prepare(BuiltinSphereStaticInput(
        centers, radii, application_ids))
    with hostile_prepared:
        try:
            hostile_prepared.execute(MotionSegmentBatch((queries[0],)))
        except RuntimeError as exc:
            hostile_error = str(exc)
        hostile_failure_receipt = hostile_prepared.last_failure_receipt
    if hostile_error is None or hostile_failure_receipt is None:
        raise RuntimeError("hostile ZERO_F32 execution did not fail on device")
    hostile_descriptor = hostile_failure_receipt["physical_receipt"][
        "native_descriptor"]
    if hostile_descriptor["last_status_failed"] is not True \
            or hostile_descriptor["last_status_d2h_call_count"] != 1 \
            or hostile_descriptor["last_application_output_d2h_call_count"] != 0 \
            or hostile_descriptor["last_output_after_status_failure_count"] != 0:
        raise RuntimeError(
            "hostile ZERO_F32 status-before-output telemetry differs")

    return {
        "schema": "rtdl.goal5833.home_builtin_sphere_validation.v1",
        "status": "PASS",
        "scope": "functional_only_no_performance",
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "prospective_generalization_claimed": False,
        "paper_app_claimed": False,
        "provider": "optix",
        "optix_sdk": args.optix_sdk,
        "compute_capability": args.compute_capability,
        "native_path": str(native),
        "native_sha256": _sha256(native),
        "oracle_path": str(ORACLE_PATH),
        "oracle_sha256": _sha256(ORACLE_PATH),
        "oracle_numeric_policy": oracle.NUMERIC_POLICY,
        "source_sha256": source.source_sha256,
        "callback_ir_sha256": verified.authority.callback.ir_sha256,
        "callback_effect_digest": verified.authority.callback.effect_digest,
        "physical_schema_sha256": verified.authority.schema.schema_sha256,
        "canonical_plan_sha256": verified.authority.canonical_plan.plan_sha256,
        "callback_abi_sha256": verified.abi.abi_sha256,
        "target_sha256": verified.authority.target.target_sha256,
        "authority_sha256": accepted_artifacts["compiler_identity"][
            "authority_sha256"],
        "wrapper_source_sha256": verified.wrapper.source_sha256,
        "executable_sha256": materialized.executable.executable_sha256,
        "composed_ptx_sha256": result.composed_ptx_sha256,
        "centers": [list(row) for row in centers],
        "radii": list(radii),
        "application_ids": list(application_ids),
        "queries": [[list(start), list(end)] for start, end in queries],
        "fixture_names": list(fixture_names),
        "expected": [list(row) for row in expected],
        "observed": [list(row) for row in result.outputs],
        "hit_rows": list(result.hit_rows),
        "observed_primitive_indices_raw": list(
            result.observed_primitive_indices),
        "observed_hit_kinds_raw": list(result.observed_hit_kinds),
        "observed_t_values_raw": observed_t_values_raw,
        "observed_t_f32_bits_raw": observed_t_f32_bits_raw,
        "device_status": list(result.statuses),
        "expected_comparison_policies": list(result.expected_comparison_policies),
        "expected_comparison_outcomes": _comparison_outcomes(
            result.outputs, expected, result.expected_comparison_policies),
        "role_counters": list(result.counters),
        "physical_receipt": result.physical_receipt,
        "traversal_receipt": result.traversal_receipt,
        "lifecycle_before": before,
        "lifecycle_after_first": after_first,
        "lifecycle_after": after,
        "exact_tangent_boundary": {
            "queries": [[list(start), list(end)]
                        for start, end in exact_tangent_queries],
            "independent_closed_sphere_expected": [
                list(row) for row in exact_tangent_expected],
            "error": exact_tangent_error,
            "execution_count_before": tangent_before["execution_count"],
            "execution_count_after": tangent_after["execution_count"],
            "native_launch_occurred": False,
        },
        "trace_endpoint_boundary": {
            "queries": [[list(start), list(end)]
                        for start, end in endpoint_queries],
            "independent_closed_segment_expected": [
                list(row) for row in endpoint_expected],
            "error": endpoint_error,
            "execution_count_before": endpoint_before["execution_count"],
            "execution_count_after": endpoint_after["execution_count"],
            "native_launch_occurred": False,
        },
        "exact_tmax_boundary": {
            "queries": [[list(start), list(end)]
                        for start, end in exact_tmax_queries],
            "independent_closed_segment_expected": [
                list(row) for row in exact_tmax_expected],
            "error": exact_tmax_error,
            "execution_count_before": exact_tmax_before["execution_count"],
            "execution_count_after": exact_tmax_after["execution_count"],
            "native_launch_occurred": False,
        },
        "repeat_execution": {
            "queries": [[list(start), list(end)]
                        for start, end in repeat_queries],
            "expected": [list(row) for row in repeat_expected],
            "observed": [list(row) for row in repeat_result.outputs],
            "expected_comparison_policies": list(
                repeat_result.expected_comparison_policies),
            "expected_comparison_outcomes": _comparison_outcomes(
                repeat_result.outputs, repeat_expected,
                repeat_result.expected_comparison_policies),
            "observed_primitive_indices_raw": list(
                repeat_result.observed_primitive_indices),
            "observed_hit_kinds_raw": list(repeat_result.observed_hit_kinds),
            "observed_t_values_raw": repeat_t_values_raw,
            "observed_t_f32_bits_raw": repeat_t_f32_bits_raw,
            "device_status": list(repeat_result.statuses),
            "role_counters": list(repeat_result.counters),
            "physical_receipt": repeat_result.physical_receipt,
            "traversal_receipt": repeat_result.traversal_receipt,
        },
        "hostile_zero_tmax": {
            "queries": [[list(queries[0][0]), list(queries[0][1])]],
            "source_sha256": hostile_source.source_sha256,
            "callback_ir_sha256": hostile_verified.authority.callback.ir_sha256,
            "callback_effect_digest":
                hostile_verified.authority.callback.effect_digest,
            "physical_schema_sha256": hostile_verified.authority.schema.schema_sha256,
            "target_sha256": hostile_verified.authority.target.target_sha256,
            "canonical_plan_sha256":
                hostile_verified.authority.canonical_plan.plan_sha256,
            "callback_abi_sha256": hostile_verified.abi.abi_sha256,
            "wrapper_source_sha256": hostile_verified.wrapper.source_sha256,
            "authority_sha256": hostile_artifacts["compiler_identity"][
                "authority_sha256"],
            "executable_sha256": hostile_materialized.executable.executable_sha256,
            "composed_ptx_sha256":
                hostile_failure_receipt["physical_receipt"][
                    "composed_ptx_sha256"],
            "error": hostile_error,
            "failure_receipt": hostile_failure_receipt,
            "artifacts": hostile_artifacts,
        },
        "accepted_artifacts": accepted_artifacts,
        "serialization_rejected": serialization_rejected,
        "thread_boundary_rejected": thread_boundary_rejected,
        "use_after_close_rejected": use_after_close_rejected,
        "double_close_rejected": double_close_rejected,
        "expected_mismatch_cleanup": {
            "error": mismatch_error,
            "owner_closed_after_exception": mismatch_cleanup_closed,
            "independent_executable_sha256":
                cleanup_materialized.executable.executable_sha256,
        },
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
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "native_sha256": result["native_sha256"],
        "callback_ir_sha256": result["callback_ir_sha256"],
        "canonical_plan_sha256": result["canonical_plan_sha256"],
        "composed_ptx_sha256": result["composed_ptx_sha256"],
        "observed": result["observed"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
