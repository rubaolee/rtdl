#!/usr/bin/env python3
"""Build the local byte-custody closeout for Goal5801-N-A1.

This program imports no RTDL, PyOptiX, CUDA, or OptiX module.  It checks the
preserved v1/v2/v3 bytes, independently repeats the v2 PTX filename-only
normalization, requires the separate v3 verifier to have passed, and emits a
complete manifest of the bounded evidence directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


V1_STDERR_SHA = "38cf4bd1aba01f10a0eac2a3cf80872153ebaa80b57ab93f8061741e6a12f90d"
V2_RESULT_SHA = "09fbe3b0054de6328814864fafc0dccf55afd8347764a4158a1edd44151b8c0e"
V3_RESULT_SHA = "8699fff641d5ef998b31507360fb05ba3b704873af13df1862bd11dad59b9fe7"
V3_PREACTION_SHA = "51a8c1604c37f62cb76f814882de487edeb4e729f2699ceba28c81a785ea1b1e"
V2_DIFF_RECEIPT_SHA = "8683be507e3b820f087cd2bb4c4d5ead6fe4efd66873e4f69a3350287642344e"
INDEPENDENT_SHA = "12f8f36c4b68ab4c86304578351788786a42de7883558c1062b0aae37c7e9d33"
BINDING_SHA = "36659588c00d715c07c46254c580b468e9bc9f839e2b7b4ec2cd4de9790dd1a2"
ATTACKS = {
    "role_effect_closure",
    "payload_attribute_abi_ownership",
    "physical_geometry_binding",
    "device_status_continuation",
    "checked_program_executable_identity",
}


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def ident(path: Path) -> dict[str, Any]:
    value = path.read_bytes()
    return {"bytes": len(value), "sha256": sha(value)}


def require(condition: bool, label: str, failures: list[str]) -> None:
    if not condition:
        failures.append(label)


def load_exact(path: Path, expected_sha: str, label: str,
               failures: list[str]) -> tuple[bytes, dict[str, Any]]:
    value = path.read_bytes()
    require(sha(value) == expected_sha, f"{label}_sha256", failures)
    return value, json.loads(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--v3-preaction", type=Path, required=True)
    parser.add_argument("--v2-diff-receipt", type=Path, required=True)
    parser.add_argument("--independent-verification", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--classifier-test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Goal5801-N-A1 closeout is create-only")
    failures: list[str] = []
    evidence = args.evidence_root.resolve(strict=True)

    v1_stdout = evidence / "artifacts/native_typed_stdout.json"
    v1_stderr = evidence / "artifacts/native_typed_stderr.txt"
    require(ident(v1_stdout) == {
        "bytes": 0,
        "sha256": hashlib.sha256(b"").hexdigest(),
    }, "v1_stdout", failures)
    require(ident(v1_stderr) == {
        "bytes": 506, "sha256": V1_STDERR_SHA,
    }, "v1_stderr", failures)
    require(not (evidence / "artifacts/native_typed_result.json").exists(),
            "v1_result_absence", failures)

    v2_bytes, v2 = load_exact(
        evidence / "artifacts/v2_native_typed_result.json",
        V2_RESULT_SHA, "v2_result", failures)
    require(v2.get("status") == "INVALID__CONTROL_OR_ATTACK_OUTCOME_DRIFT",
            "v2_terminal_status", failures)
    require(v2.get("invalid_cases") == [
        "native_negative_missing_anyhit_rights"],
        "v2_invalid_partition", failures)

    v3_bytes, v3 = load_exact(
        evidence / "artifacts/v3_native_typed_result.json",
        V3_RESULT_SHA, "v3_result", failures)
    require(v3.get("status") ==
            "PASS__UNCONDITIONAL_NATIVE_TYPED_PAYLOAD_SURVIVAL_RESULT",
            "v3_status", failures)
    require(v3.get("invalid_cases") == [], "v3_invalid_partition", failures)
    require(set(v3.get("residual_surviving_mechanisms", [])) == ATTACKS,
            "v3_residual_partition", failures)
    require(v3.get("native_collision_mechanisms") == [],
            "v3_collision_partition", failures)
    require(v3.get("required_validity_controls_pass") is True,
            "v3_control_gate", failures)
    identity_control = v3.get("native_negative_identity_control", {})
    require(identity_control.get("pass") is True and
            identity_control.get("source_byte_identical_to_nearby_valid_triangle")
            is True and
            identity_control.get("ptx_byte_identical_to_nearby_valid_triangle")
            is True, "v3_identity_control", failures)
    rows = {row["id"]: row for row in v3.get("cases", [])}
    require(set(rows) == ATTACKS | {
        "nearby_valid_relation",
        "nearby_valid_triangle",
        "native_negative_missing_anyhit_rights",
    }, "v3_case_population", failures)
    negative = rows.get("native_negative_missing_anyhit_rights", {})
    require(negative.get("terminal_phase") == "module" and
            negative.get("classification") ==
            "PASS__NATIVE_TYPED_SEMANTICS_REJECTED_NEGATIVE",
            "v3_negative_liveness", failures)
    require(all(rows[name].get("classification") ==
                "NATIVE_ACCEPTED_AND_EXECUTED_EXACT_COUNTEREXAMPLE__RESIDUAL_SURVIVES"
                for name in ATTACKS), "v3_attack_execution", failures)

    preaction_bytes, preaction = load_exact(
        args.v3_preaction, V3_PREACTION_SHA, "v3_preaction", failures)
    require(preaction.get("blindness", {}).get(
        "v2_all_row_outcomes_already_observed") is True and
        preaction.get("blindness", {}).get("v3_blind_or_held_out_claimed")
        is False, "outcome_known_disclosure", failures)
    diff_bytes, diff_receipt = load_exact(
        args.v2_diff_receipt, V2_DIFF_RECEIPT_SHA,
        "v2_diff_receipt", failures)
    require(diff_receipt.get("independent_byte_diff", {}).get(
        "normalized_byte_equal") is True,
        "v2_diff_receipt_conclusion", failures)

    v2_ptx_root = evidence / "v2_gpu_evidence/ptx"
    near_v2 = (v2_ptx_root / "nearby_valid_triangle.ptx").read_bytes()
    negative_v2 = (
        v2_ptx_root / "native_negative_missing_anyhit_rights.ptx").read_bytes()
    near_token = (
        b"_ZN55_INTERNAL_00000000_24_nearby_valid_triangle_cu_cd7464392")
    negative_token = (
        b"_ZN71_INTERNAL_00000000_40_"
        b"native_negative_missing_anyhit_rights_cu_cd7464392")
    canonical = b"_ZNXX_INTERNAL_00000000_XX_CANONICAL_SOURCE_NAME_cu_cd7464392"
    normalized_near = near_v2.replace(near_token, canonical)
    normalized_negative = negative_v2.replace(negative_token, canonical)
    require(near_v2.count(near_token) == 38 and
            negative_v2.count(negative_token) == 38 and
            normalized_near == normalized_negative and
            sha(normalized_near) ==
            "e06246e309fb621a11b5d38fdf18f729b8c5f6ad0a85fdffbcfa7330835fa8c4",
            "v2_ptx_filename_only_recount", failures)

    v3_ptx_root = evidence / "v3_gpu_evidence/ptx"
    near_v3 = v3_ptx_root / "nearby_valid_triangle.ptx"
    negative_v3 = v3_ptx_root / "native_negative_missing_anyhit_rights.ptx"
    require(ident(near_v3) == ident(negative_v3) == {
        "bytes": 13815,
        "sha256": "e7ba27e9c757ac999b781caaf634bf9cedec15e81faef05b531676f6d1fa204b",
    }, "v3_ptx_identity", failures)

    binding_bytes, binding = load_exact(
        evidence / "artifacts/binding_receipt.json", BINDING_SHA,
        "binding_receipt", failures)
    require(binding.get("status") ==
            "PASS__TWO_LINE_FFI_PAYLOAD_TYPE_REPAIR__UNTIMED" and
            binding.get("scope", {}).get(
                "stock_or_unmodified_pyoptix_claimed") is False,
            "binding_scope", failures)
    require(ident(evidence /
                  "artifacts/binding_stage/patched_source/main.cpp") ==
            {"bytes": 155527,
             "sha256": "fc206c3932cc32a91dad39354d23b532c402bc6cd649f7c5501fe3de57e20fd3"},
            "patched_binding_source", failures)
    require(ident(evidence /
                  "artifacts/binding_stage/wheel/"
                  "pyoptix-9.1.0-cp312-cp312-linux_x86_64.whl") ==
            {"bytes": 621648,
             "sha256": "50fc6d7ce82f56d780a4187db511fab632f33d6ad1877ae501e7eccf99d75661"},
            "binding_wheel", failures)
    require(ident(evidence /
                  "artifacts/binding_stage/site/optix/"
                  "_optix.cpython-312-x86_64-linux-gnu.so") ==
            {"bytes": 2630648,
             "sha256": "6523d40aea623d4729400bffac93a944e42c97acb7bf537bc0a27cd350277cfa"},
            "binding_extension", failures)

    independent_bytes, independent = load_exact(
        args.independent_verification, INDEPENDENT_SHA,
        "independent_verification", failures)
    require(independent.get("status") == "PASS" and
            independent.get("failures") == [] and
            independent.get("independence", {}).get("gpu_api_calls") == 0,
            "independent_verification_status", failures)

    static = subprocess.run([
        sys.executable, str(args.runner), "--static-check",
        "--base-device-source", str(evidence / "inputs/matched_device.cu"),
    ], check=False, capture_output=True, text=True)
    require(static.returncode == 0, "static_source_reconstruction", failures)
    focused = subprocess.run([
        sys.executable, "-m", "unittest", str(args.classifier_test),
    ], check=False, capture_output=True, text=True)
    require(focused.returncode == 0 and "Ran 9 tests" in focused.stderr,
            "focused_classifier_tests", failures)

    scope = v3.get("scope", {})
    require(scope.get("registered_performance_timing_count") == 0 and
            scope.get("formal_worker_count") == 0 and
            scope.get("pod_count") == 0 and
            scope.get("wsl_used") is False,
            "v3_zero_scope", failures)

    manifest = []
    for path in sorted(evidence.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts \
                or path.suffix == ".pyc":
            continue
        row = ident(path)
        row["path"] = path.relative_to(evidence).as_posix()
        manifest.append(row)
    manifest_projection = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n"
        for row in manifest).encode("utf-8")

    output = {
        "schema": "rtdl.goal5801_n_a1.native_typed_payload_closeout.v1",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "scientific_result": {
            "native_typed_payload_mechanism_active": True,
            "native_collision_mechanisms": v3.get(
                "native_collision_mechanisms"),
            "rtdl_residual_surviving_mechanisms": v3.get(
                "residual_surviving_mechanisms"),
            "case_count": len(rows),
            "designed_task_count": 2,
            "v3_outcome_known_control_repair": True,
        },
        "claim_ceilings": {
            "stock_or_unmodified_pyoptix": False,
            "generalization_evidence": False,
            "usability_evidence": False,
            "performance_evidence": False,
            "owl_capability_or_performance_evidence": False,
            "native_optix_typed_payload_residual_on_two_designed_tasks": True,
        },
        "lineages": {
            "v1": "TERMINAL_ZERO_CONTEXT_HARNESS_ADMISSION_FAILURE",
            "v2": v2.get("status"),
            "v3": v3.get("status"),
        },
        "key_inputs": {
            "v2_result": {"bytes": len(v2_bytes), "sha256": sha(v2_bytes)},
            "v3_result": {"bytes": len(v3_bytes), "sha256": sha(v3_bytes)},
            "v3_preaction": {
                "bytes": len(preaction_bytes), "sha256": sha(preaction_bytes)},
            "v2_diff_receipt": {
                "bytes": len(diff_bytes), "sha256": sha(diff_bytes)},
            "binding_receipt": {
                "bytes": len(binding_bytes), "sha256": sha(binding_bytes)},
            "independent_verification": {
                "bytes": len(independent_bytes),
                "sha256": sha(independent_bytes)},
        },
        "local_checks": {
            "static_source_reconstruction_returncode": static.returncode,
            "static_source_reconstruction_stdout_sha256": sha(
                static.stdout.encode("utf-8")),
            "focused_classifier_test_returncode": focused.returncode,
            "focused_classifier_test_count": 9,
            "focused_classifier_stderr_sha256": sha(
                focused.stderr.encode("utf-8")),
            "gpu_api_calls": 0,
        },
        "evidence_manifest": {
            "file_count": len(manifest),
            "payload_bytes": sum(row["bytes"] for row in manifest),
            "projection_bytes": len(manifest_projection),
            "projection_sha256": sha(manifest_projection),
            "files": manifest,
        },
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
        "pod_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(output, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": output["status"],
        "failures": failures,
        "manifest_file_count": len(manifest),
        "manifest_payload_bytes": output["evidence_manifest"]["payload_bytes"],
        "manifest_projection_sha256": output["evidence_manifest"][
            "projection_sha256"],
    }, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
