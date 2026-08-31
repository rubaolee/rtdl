#!/usr/bin/env python3
"""Standalone verifier for the Goal5834 Home curve result.

This verifier imports no RTDL package.  It rehashes every preserved generated
artifact and invokes only the independent stdlib capsule oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strict_json(path: Path):
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")),
    )


def _load_oracle(path: Path):
    text = path.read_text(encoding="utf-8")
    if "rtdsl" in text.lower():
        raise RuntimeError("independent oracle imports or names RTDL")
    spec = importlib.util.spec_from_file_location(
        "goal5834_standalone_capsule_oracle", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("independent oracle cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(args) -> dict[str, object]:
    result_path = args.result.resolve(strict=True)
    native = args.native.resolve(strict=True)
    oracle_path = args.oracle.resolve(strict=True)
    artifact_dir = args.artifact_dir.resolve(strict=True)
    result = _strict_json(result_path)
    if result.get("schema") != \
            "rtdl.goal5834.home_builtin_curve_validation.v1" \
            or result.get("status") != "PASS" \
            or result.get("scope") != "functional_only_no_performance" \
            or result.get("registered_performance_timing_count") != 0 \
            or result.get("performance_claimed") is not False \
            or result.get("prospective_generalization_claimed") is not False \
            or result.get("paper_app_claimed") is not False:
        raise RuntimeError("Goal5834 result scope or status differs")
    if _sha(native) != result["native_sha256"]:
        raise RuntimeError("preserved native identity differs")
    if _sha(oracle_path) != result["oracle_sha256"]:
        raise RuntimeError("preserved oracle identity differs")

    oracle = _load_oracle(oracle_path)
    queries = tuple((tuple(row[0]), tuple(row[1]))
                    for row in result["queries"])
    recomputed = oracle.first_contact(
        tuple(tuple(row) for row in result["control_points"]),
        tuple(result["widths"]), tuple(result["segment_indices"]),
        tuple(result["application_ids"]), queries)
    expected = tuple(tuple(row) for row in result["expected"])
    observed = tuple(tuple(row) for row in result["observed"])
    if recomputed != expected or observed != expected:
        raise RuntimeError("independent oracle/output mismatch")
    if result["fixture_names"] != [
            "side_hit_equal_time_stable_application_id", "miss",
            "earlier_time_precedes_smaller_application_id",
            "round_endcap_only_hit"]:
        raise RuntimeError("mandatory fixture set differs")
    if len(set(result["widths"])) < 3:
        raise RuntimeError("varying-radius fixture is absent")
    if result["repeat_observed"] != list(reversed(result["observed"])):
        raise RuntimeError("repeat execution does not preserve reversed rows")
    if result["tangent_prelaunch_rejection"].get("code") != \
            "near_tangent_curve_contact" \
            or result["lifecycle_counts"] != {
                "before": 0, "after_first": 1,
                "after_second": 2, "after_tangent": 2,
                "after_axial": 2} \
            or result["use_after_close_rejected"] is not True:
        raise RuntimeError("negative/lifecycle evidence differs")
    axial = result.get("axial_provider_boundary", {})
    if axial.get("status") != "POST_OBSERVATION_FAIL_CLOSED_EXCLUSION" \
            or axial.get("native_launch_occurred") is not False \
            or axial.get("independent_closed_capsule_oracle", [0])[0] != 1 \
            or axial.get("rejection", {}).get("code") != \
                "near_parallel_curve_query":
        raise RuntimeError("axial provider boundary disclosure differs")

    physical = result["physical_receipt"]
    descriptor = physical["native_descriptor"]
    required_descriptor = {
        "schema": "rtdl.v4.native_builtin_curve_descriptor.v1",
        "build_input_type": 0x2145,
        "primitive_type": 0x2503,
        "primitive_type_flags": 1 << 3,
        "builtin_is_build_flags": 1 << 2,
        "builtin_is_curve_endcap_flags": 0,
        "builtin_is_module": True,
        "user_intersection_program": False,
        "uses_motion_blur": False,
        "build_flags": 1 << 2,
        "geometry_flags": 1 << 1,
        "vertex_stride_bytes": 12,
        "width_stride_bytes": 4,
        "index_stride_bytes": 4,
        "normal_buffers_present": False,
        "primitive_index_offset": 0,
        "sbt_record_count": 1,
        "gas_count": 1,
        "primitive_count": 5,
        "vertex_count": 10,
        "motion_key_count": 0,
        "endcap_flags": 0,
        "max_payload_values": 8,
        "max_attribute_values": 0,
        "max_trace_depth": 1,
        "program_group_count": 3,
        "last_execution_present": True,
        "last_status_failed": False,
        "last_query_count": 4,
        "last_status_d2h_call_count": 1,
        "last_application_output_d2h_call_count": 6,
        "last_output_after_status_failure_count": 0,
        "last_query_device_pointer_nonzero_count": 6,
        "last_output_device_pointer_nonzero_count": 8,
    }
    for key, value in required_descriptor.items():
        if descriptor.get(key) != value:
            raise RuntimeError(f"native descriptor differs at {key}")
    for key in (
            "vertex_device_pointer", "width_device_pointer",
            "index_device_pointer", "application_id_device_pointer",
            "traversable_identity", "traversable_graph_flags"):
        if not isinstance(descriptor.get(key), int) or descriptor[key] == 0:
            raise RuntimeError(f"native identity is absent at {key}")
    if descriptor["static_input_fingerprint"] != \
            descriptor["device_static_input_fingerprint"] \
            or descriptor["last_query_fingerprint"] != \
            descriptor["last_device_query_fingerprint"]:
        raise RuntimeError("host/device content identity differs")
    if physical["native_library_sha256"] != result["native_sha256"] \
            or physical["composed_ptx_sha256"] != \
            result["composed_ptx_sha256"] \
            or physical["status_before_output"] is not True:
        raise RuntimeError("physical receipt binding differs")
    statuses = result["device_status"]
    if len(statuses) != 4 or any(
            row.get("error_code") != 0
            or row.get("first_error_claimed") != 0
            or row.get("launch_index") != index
            or row.get("invocation_mask", 0) == 0
            for index, row in enumerate(statuses)):
        raise RuntimeError("device status is not four successful rows")
    if result.get("role_counters") != [0, 4, 0, 0, 3, 1, 4]:
        raise RuntimeError(
            "role counters do not show 4 make-ray, 3 closest-hit, "
            "1 miss, and 4 finalize invocations")
    if result.get("expected_comparison_policies") != [
            "exact_provider_t_bits", "miss_exact_bits",
            "exact_provider_t_bits", "exact_provider_t_bits"]:
        raise RuntimeError("expected-output comparison policy differs")
    traversal = result["traversal_receipt"]
    snapshot = traversal.get("native_snapshot", {})
    if traversal.get("physical_executor_classification") != \
            "optix_traversal_observed" \
            or traversal.get("expected_program_observed_at_receipt_edge") \
                is not True \
            or snapshot.get("successful_launch_count") != 1 \
            or snapshot.get("failed_launch_count") != 0 \
            or snapshot.get("raygen_invocation_count") != 4:
        raise RuntimeError("OptiX traversal receipt differs")

    manifest_path = artifact_dir / "manifest.json"
    manifest = _strict_json(manifest_path)
    members = manifest["members"]
    if manifest["member_count"] != len(members) \
            or manifest["executable_sha256"] != result["executable_sha256"] \
            or _sha(manifest_path) != result["artifacts"]["manifest_sha256"]:
        raise RuntimeError("generated-artifact manifest differs")
    names = set()
    for member in members:
        name = member["path"]
        if name in names or Path(name).is_absolute() or ".." in Path(name).parts:
            raise RuntimeError("unsafe or duplicate artifact member")
        names.add(name)
        path = artifact_dir / name
        if path.stat().st_size != member["size"] \
                or _sha(path) != member["sha256"]:
            raise RuntimeError(f"artifact member differs: {name}")
    if _sha(artifact_dir / "wrapper.cu") != result["wrapper_source_sha256"] \
            or _sha(artifact_dir / "composed.ptx") != \
            result["composed_ptx_sha256"]:
        raise RuntimeError("published executable bytes differ")
    return {
        "schema": "rtdl.goal5834.independent_verification.v1",
        "status": "PASS",
        "result_sha256": _sha(result_path),
        "native_sha256": _sha(native),
        "oracle_sha256": _sha(oracle_path),
        "artifact_member_count": len(members),
        "observed": [list(row) for row in observed],
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    verified = verify(args)
    text = json.dumps(verified, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
