#!/usr/bin/env python3
"""Independent byte/result verifier for Goal5801-N-A1.

This verifier imports neither RTDL, PyOptiX, CuPy nor the executed experiment.
It reconstructs all five typed device variants from the frozen base bytes,
checks the two-line binding repair, and recomputes the native-collision versus
surviving-residual partition from raw per-case phase/output records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASE_SHA = "dcfb335a2a63ab609d21ce0361d0d530f148d157bd98b122989df0dab51f17a8"
MAIN_SHA = "a6626e2c78dbf561a9cb3297b0bed3e04128360443cacb14d552cd1e1ebcafdb"
ATTACKS = {
    "role_effect_closure",
    "payload_attribute_abi_ownership",
    "physical_geometry_binding",
    "device_status_continuation",
    "checked_program_executable_identity",
}


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"bytes": len(value), "sha256": sha(value)}


def reconstruct(base: bytes) -> dict[str, bytes]:
    if sha(base) != BASE_SHA:
        raise RuntimeError("base source mismatch")
    text = base.decode("utf-8")
    values = {"valid_a": text}
    old = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixIgnoreIntersection();\n}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}")
    new = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixTerminateRay();\n}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}")
    if text.count(old) != 1:
        raise RuntimeError("effect anchor mismatch")
    values["role_effect_closure"] = text.replace(old, new, 1)
    old = "optixReportIntersection(0.0f, 0u, item.item_id);"
    if text.count(old) != 1:
        raise RuntimeError("ABI anchor mismatch")
    values["payload_attribute_abi_ownership"] = text.replace(
        old, "optixReportIntersection(0.0f, 0u, primitive_index);", 1)
    rg = "extern \"C\" __global__ void __raygen__goal5796_relation() {"
    helper = r'''static __forceinline__ __device__ Box goal5797_swap_xy(Box value) {
    const float lower_x = value.lower_x;
    const float upper_x = value.upper_x;
    value.lower_x = value.lower_y;
    value.lower_y = lower_x;
    value.upper_x = value.upper_y;
    value.upper_y = upper_x;
    return value;
}

extern "C" __global__ void __raygen__goal5796_relation() {'''
    if text.count(rg) != 1:
        raise RuntimeError("physical helper anchor mismatch")
    physical = text.replace(rg, helper, 1)
    q = "const Box query = params.queries[query_index];"
    if physical.count(q) != 2:
        raise RuntimeError("physical query anchor mismatch")
    values["physical_geometry_binding"] = physical.replace(
        q, "const Box query = goal5797_swap_xy(params.queries[query_index]);")
    old = "set_payload_u64(before + 1ull);"
    if text.count(old) != 1:
        raise RuntimeError("identity anchor mismatch")
    values["checked_program_executable_identity"] = text.replace(
        old, "set_payload_u64(before + 2ull);", 1)
    typed = {}
    for name, value in values.items():
        anchor = "    optixTrace(\n"
        if value.count(anchor) != 2:
            raise RuntimeError(f"trace anchor mismatch: {name}")
        value = value.replace(
            anchor, "    optixTrace(\n        OPTIX_PAYLOAD_TYPE_ID_0,\n")
        typed[name] = value.encode("utf-8")
    return typed


def recompute_case(row: dict[str, Any]) -> str:
    name = row["id"]
    launched = row.get("terminal_phase") == "launch_completed"
    native_rejection = native_payload_specific_rejection(row)
    if name == "native_negative_missing_anyhit_rights":
        if launched:
            return "INVALID__NATIVE_NEGATIVE_WAS_NOT_REJECTED"
        return ("PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE"
                if native_rejection else
                "INVALID__INFRA_OR_TRANSCRIPTION_FAILURE")
    if name == "nearby_valid_relation":
        expected = {
            "output": [[100, 10], [101, 20]], "raw_event_count": 2,
            "device_overflow": 0, "device_status": 0}
        return ("PASS__NEARBY_VALID" if launched and
                row.get("observation") == expected
                else "INVALID__NEARBY_VALID_RELATION_FAILED")
    if name == "nearby_valid_triangle":
        expected = {"per_ray": [3, 2, 0, 1], "weighted_sum": 16}
        return ("PASS__NEARBY_VALID" if launched and
                row.get("observation") == expected
                else "INVALID__NEARBY_VALID_TRIANGLE_FAILED")
    if not launched:
        return ("NATIVE_TYPED_SEMANTICS_REJECTED_ATTACK__RTDL_CLAIM_MUST_NARROW"
                if native_rejection else
                "INVALID__INFRA_OR_TRANSCRIPTION_FAILURE")
    exact = {
        "role_effect_closure": {
            "per_ray": [1, 1, 0, 1], "weighted_sum": 11},
        "payload_attribute_abi_ownership": {
            "output": [[100, 0], [101, 1]], "raw_event_count": 2,
            "device_overflow": 0, "device_status": 0},
        "physical_geometry_binding": {
            "output": [[100, 20], [101, 10]], "raw_event_count": 2,
            "device_overflow": 0, "device_status": 0},
        "checked_program_executable_identity": {
            "per_ray": [6, 4, 0, 2], "weighted_sum": 32},
    }
    observed = row.get("observation")
    if name == "device_status_continuation":
        valid = (
            observed.get("status_observed_before_application_output_copy") is True
            and observed.get("application_output_copied_despite_failure") is True
            and observed.get("application_result_consumed") is True
            and observed.get("raw_capacity") == 7
            and observed.get("raw_event_count") == 8
            and observed.get("device_overflow") == 1
            and observed.get("device_status") == 0
            and observed.get("returned_row_count") == 7)
    else:
        valid = observed == exact[name]
    return ("NATIVE_ACCEPTED_AND_EXECUTED_EXACT_COUNTEREXAMPLE__RESIDUAL_SURVIVES"
            if valid else "INVALID__ATTACK_OUTCOME_DRIFT")


def native_payload_specific_rejection(row: dict[str, Any]) -> bool:
    phases = row.get("phases", {})
    if phases.get("nvrtc", {}).get("verdict") != "PASS" \
            or phases.get("context", {}).get("verdict") != "PASS":
        return False
    failing_phase = first_failing_native_phase(row)
    if failing_phase is None:
        return False
    failing = phases[failing_phase]
    values = []
    if isinstance(failing.get("log"), str):
        values.append(failing["log"])
    exception = failing.get("exception", {})
    if isinstance(exception, dict):
        for key in ("message", "repr"):
            if isinstance(exception.get(key), str):
                values.append(exception[key])
    for message in row.get("optix_validation_messages", []):
        if isinstance(message, dict):
            for key in ("tag", "message"):
                if isinstance(message.get(key), str):
                    values.append(message[key])
    evidence = "\n".join(values).lower()
    return any(marker in evidence for marker in (
        "optix_error_payload_type_mismatch",
        "optix_error_payload_type_resolution_failed",
        "payload type mismatch",
        "payload type resolution",
        "payload semantics",
        "payload access",
        "payload register",
        "payload value"))


def first_failing_native_phase(row: dict[str, Any]) -> str | None:
    phases = row.get("phases", {})
    for name in ("module", "program_groups", "pipeline_link"):
        verdict = phases.get(name, {}).get("verdict")
        if verdict == "REJECT_OR_ERROR":
            return name
        if verdict != "PASS":
            return None
    return None


def locate(root: Path, recorded: dict[str, Any]) -> Path:
    name = Path(str(recorded["path"])).name
    candidates = [path for path in root.rglob(name) if path.is_file()]
    matches = [path for path in candidates if identity(path) == {
        "bytes": recorded["bytes"], "sha256": recorded["sha256"]}]
    if len(matches) != 1:
        raise RuntimeError({"identity_not_unique": recorded, "matches": matches})
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preaction", type=Path, required=True)
    parser.add_argument("--base-device-source", type=Path, required=True)
    parser.add_argument("--upstream-main", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("independent result is create-only")
    preaction_bytes = args.preaction.read_bytes()
    preaction = json.loads(preaction_bytes)
    binding_bytes = args.binding_receipt.read_bytes()
    binding = json.loads(binding_bytes)
    result_bytes = args.result.read_bytes()
    result = json.loads(result_bytes)
    failures = []

    if preaction.get("status") != "FROZEN_BEFORE_ANY_NEW_GPU_RESULT":
        failures.append("preaction_status")
    if sha(args.base_device_source.read_bytes()) != BASE_SHA:
        failures.append("base_source")
    upstream = args.upstream_main.read_bytes()
    if sha(upstream) != MAIN_SHA:
        failures.append("upstream_main")
    old = b"    void sync()\n    {\n        return;\n#if OPTIX_VERSION >= 70200\n"
    new = b"    void sync()\n    {\n#if OPTIX_VERSION >= 70200\n"
    constructor_old = (b"    PayloadType( const py::list&  payload_semantics )\n"
                       b"    {\n"
                       b"        setPayloadSemantics( payload_semantics );\n"
                       b"    }\n")
    constructor_new = (b"    PayloadType( const py::list&  payload_semantics )\n"
                       b"    {\n"
                       b"        setPayloadSemantics( payload_semantics );\n"
                       b"        sync();\n"
                       b"    }\n")
    if upstream.count(old) != 1:
        failures.append("binding_defect_anchor")
    if upstream.count(constructor_old) != 1:
        failures.append("payload_constructor_anchor")
    patched = upstream.replace(old, new, 1)
    patched = patched.replace(constructor_old, constructor_new, 1)
    patched_record = binding.get("repair", {}).get("patched_main_cpp", {})
    if sha(patched) != patched_record.get("sha256") \
            or len(patched) != patched_record.get("bytes"):
        failures.append("two_line_repair")
    if binding.get("scope", {}).get("stock_or_unmodified_pyoptix_claimed") \
            is not False:
        failures.append("binding_label")

    generated = reconstruct(args.base_device_source.read_bytes())
    rows = result.get("cases", [])
    if len(rows) != 8 or len({row.get("id") for row in rows}) != 8:
        failures.append("case_population")
    for row in rows:
        expected_nvrtc_source_name = (
            "goal5801_n_a1_valid_a_identity_control.cu"
            if row.get("id") in {
                "nearby_valid_triangle",
                "native_negative_missing_anyhit_rights",
            }
            else f"{row.get('id')}.cu"
        )
        if row.get("nvrtc_source_name") != expected_nvrtc_source_name:
            failures.append(f"nvrtc_source_name:{row.get('id')}")
        source_name = row.get("source_variant")
        if source_name not in generated:
            failures.append(f"source_variant:{row.get('id')}")
            continue
        recorded_source = row.get("source", {})
        if sha(generated[source_name]) != recorded_source.get("sha256") \
                or len(generated[source_name]) != recorded_source.get("bytes"):
            failures.append(f"source_bytes:{row.get('id')}")
        else:
            try:
                locate(args.evidence_root, recorded_source)
            except RuntimeError:
                failures.append(f"source_preservation:{row.get('id')}")
        if row.get("classification") != recompute_case(row):
            failures.append(f"classification:{row.get('id')}")
        ptx = row.get("ptx")
        if ptx is not None:
            try:
                locate(args.evidence_root, ptx)
            except RuntimeError:
                failures.append(f"ptx_preservation:{row.get('id')}")

    by_id = {row.get("id"): row for row in rows}
    nearby = by_id.get("nearby_valid_triangle", {})
    negative = by_id.get("native_negative_missing_anyhit_rights", {})
    identity_control = result.get("native_negative_identity_control", {})
    source_same = (
        nearby.get("source", {}).get("bytes") == negative.get("source", {}).get("bytes")
        and nearby.get("source", {}).get("sha256") == negative.get("source", {}).get("sha256"))
    ptx_same = (
        nearby.get("ptx", {}).get("bytes") == negative.get("ptx", {}).get("bytes")
        and nearby.get("ptx", {}).get("sha256") == negative.get("ptx", {}).get("sha256"))
    if not source_same or not ptx_same \
            or identity_control.get("pass") is not True:
        failures.append("native_negative_identity_control")

    collisions = sorted(
        row["id"] for row in rows if row.get("id") in ATTACKS and
        recompute_case(row).startswith("NATIVE_TYPED"))
    residuals = sorted(
        row["id"] for row in rows if row.get("id") in ATTACKS and
        recompute_case(row).startswith("NATIVE_ACCEPTED"))
    invalid = sorted(
        row["id"] for row in rows if recompute_case(row).startswith("INVALID"))
    if collisions != sorted(result.get("native_collision_mechanisms", [])):
        failures.append("collision_partition")
    if residuals != sorted(result.get("residual_surviving_mechanisms", [])):
        failures.append("residual_partition")
    if invalid != sorted(result.get("invalid_cases", [])):
        failures.append("invalid_partition")
    controls_pass = (
        by_id.get("nearby_valid_relation", {}).get("classification")
        == "PASS__NEARBY_VALID"
        and by_id.get("nearby_valid_triangle", {}).get("classification")
        == "PASS__NEARBY_VALID"
        and by_id.get("native_negative_missing_anyhit_rights", {}).get(
            "classification")
        == "PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE")
    if result.get("required_validity_controls_pass") is not controls_pass:
        failures.append("validity_control_gate")
    expected_status = (
        "PASS__UNCONDITIONAL_NATIVE_TYPED_PAYLOAD_SURVIVAL_RESULT"
        if controls_pass and not invalid
        and sorted(collisions + residuals) == sorted(ATTACKS)
        else "INVALID__CONTROL_OR_ATTACK_OUTCOME_DRIFT")
    if result.get("status") != expected_status:
        failures.append("global_status")
    scope = result.get("scope", {})
    if scope.get("registered_performance_timing_count") != 0 \
            or scope.get("formal_worker_count") != 0 \
            or scope.get("pod_count") != 0 \
            or scope.get("wsl_used") is not False:
        failures.append("scope")

    output = {
        "schema": "rtdl.goal5801_n_a1.independent_verification.v1",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "inputs": {
            "preaction_sha256": sha(preaction_bytes),
            "binding_receipt_sha256": sha(binding_bytes),
            "result_sha256": sha(result_bytes),
        },
        "recomputed": {
            "native_collision_mechanisms": collisions,
            "residual_surviving_mechanisms": residuals,
            "invalid_cases": invalid,
            "typed_source_sha256": {
                key: sha(value) for key, value in generated.items()},
        },
        "independence": {
            "imports_rtdl": False, "imports_pyoptix": False,
            "imports_executed_harness": False, "gpu_api_calls": 0,
        },
        "registered_performance_timing_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(output, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
