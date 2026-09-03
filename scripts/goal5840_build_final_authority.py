#!/usr/bin/env python3
"""Build or verify the deterministic Goal5840 final authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
GPU_ROOT = EVIDENCE_ROOT / "FINAL_GPU_EVIDENCE"
RESULT_PATH = GPU_ROOT / "RESULT.json"
TRUST_ROOTS_PATH = GPU_ROOT / "RUNTIME_TRUST_ROOTS.json"
MUTATION_PATH = GPU_ROOT / "EXACT_BUNDLE_MUTATION_RESULT.json"
BUILD_PATH = EVIDENCE_ROOT / "FINAL_NATIVE_BUILD_MANIFEST.json"
VERIFICATION_PATH = EVIDENCE_ROOT / "FINAL_GPU_EVIDENCE_VERIFICATION.json"
VERIFICATION_REPLAY_PATH = (
    EVIDENCE_ROOT / "FINAL_GPU_EVIDENCE_VERIFICATION_REPLAY.json"
)
EXECUTION_LOG_PATH = EVIDENCE_ROOT / "ATTEMPT_07_EXECUTION_LOG.jsonl"
PREREGISTRATION_PATH = EVIDENCE_ROOT / "GOAL5840_PREREGISTRATION.json"
PRE_POD_AUTHORITY_PATH = EVIDENCE_ROOT / "PRE_POD_INPUT_AUTHORITY.json"
AUTHORITY_PATH = EVIDENCE_ROOT / "FINAL_AUTHORITY.json"

AUTHORITY_DOMAIN = b"rtdl.goal5840.final_authority.v1\0"
SUMMARY_DOMAIN = b"rtdl.goal5840.true_optix_target_evidence.v7\0"
VERIFICATION_DOMAIN = (
    b"rtdl.goal5840.downloaded_gpu_evidence_verification.v7\0"
)
BUILD_DOMAIN = b"rtdl.goal5838.selected_sphere_optix_provider_build.v2\0"
TRUST_ROOTS_DOMAIN = b"rtdl.goal5840.runtime_trust_roots.v1\0"
MUTATION_DOMAIN = b"rtdl.goal5840.exact_bundle_mutation_suite.v1\0"
BUNDLE_DOMAIN = b"rtdl.v4.target_evidence_bundle.v2\0"
CHECK_DOMAIN = b"rtdl.goal5840.independent_target_check.v1\0"

EVIDENCE_COMMIT = "79fdbb61c2afd602a16e8fc01b27d0cf8a576e7b"
SUMMARY_SHA256 = "ff2a71ca1331219da5a89dd0f4f847637ebe406fb9403ac95d7b9c34830b3049"
VERIFICATION_SHA256 = (
    "574b46be2a2d65a27cb3c3e2b1cdbf2371998ab8d2f5ecc8626b06a0d5448f60"
)
NATIVE_SHA256 = "8060367df223bbcedd45bf8002820ee45338047c977dde93a4951ce67a27de4c"
NATIVE_BYTES = 7_181_936
RAW_CAPSULE_SHA256 = (
    "adfe14c69913c8234f5b301ea32bb4ceb231683058ee81009c740cfc2d027347"
)
RAW_CAPSULE_BYTES = 3_170_210
FROZEN_CORE_SEAL_SHA256 = (
    "c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae"
)

PROPERTIES = (
    "CP001_ROLE_EFFECT_CLOSURE",
    "CP002_SEMANTIC_ABI_OWNERSHIP",
    "CP003_PHYSICAL_BINDING",
    "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS",
    "CP005_EXECUTABLE_IDENTITY_CHAIN",
)

MODE_ROWS = (
    {
        "key": (
            "stable::bounded_relation::canonical_bounded_pair_collection::"
            "capacity_fail_closed_collection"
        ),
        "route_id": "stable::bounded_relation::canonical_bounded_pair_collection",
        "mode": "capacity_fail_closed_collection",
        "bundle_file": "mode_01_capacity_fail_closed_collection_bundle.json",
        "bundle_sha256": (
            "634a26222322c6129ff495e68ed87f2e54e9648ea7a314d169fb9c1ab86f325f"
        ),
        "bundle_file_sha256": (
            "2a7deddadfdca35ea4ec535d5bfce4a4859f270ec021792ed570c628c8a73593"
        ),
        "checker_file": (
            "mode_01_capacity_fail_closed_collection_independent_check.json"
        ),
        "checker_sha256": (
            "1c690ea6c252608a149ee8565f33fe7f08040460e6cf97645912aee0c7b35fe8"
        ),
        "checker_file_sha256": (
            "4d53878c79d5f14130e8c7fe47abfa2153cd949e9510144ede2260dccc2ad4d3"
        ),
    },
    {
        "key": "stable::triangle_reduction::checked_u64_reduction::all_hit_count",
        "route_id": "stable::triangle_reduction::checked_u64_reduction",
        "mode": "all_hit_count",
        "bundle_file": "mode_02_all_hit_count_bundle.json",
        "bundle_sha256": (
            "b382db723210f3e13efd400f70c84c796b12257fde13bad79609004a0a8739c8"
        ),
        "bundle_file_sha256": (
            "52d3cb8f6649fca6171d491be5b8c0f98796d963d0cc6f1429a29be4b4e90f78"
        ),
        "checker_file": "mode_02_all_hit_count_independent_check.json",
        "checker_sha256": (
            "5d8f2d64038b6dcb24a3f456d2377243c367a9d6f6de6fd8d9faa6e8133fd863"
        ),
        "checker_file_sha256": (
            "299086a27e6df0ea6928b68300c74cba95859bdf728c55bbe513573ece19bccb"
        ),
    },
    {
        "key": (
            "stable::triangle_reduction::checked_u64_reduction::"
            "weighted_hit_count"
        ),
        "route_id": "stable::triangle_reduction::checked_u64_reduction",
        "mode": "weighted_hit_count",
        "bundle_file": "mode_03_weighted_hit_count_bundle.json",
        "bundle_sha256": (
            "cd0751be6e1efa595bcdf437a5d85bde609f4af9e2ea5b16b8be9ffb3d00f595"
        ),
        "bundle_file_sha256": (
            "d067b750df01477f31fef153d15dda0939ecec7def0683486cd66a95015f8e1a"
        ),
        "checker_file": "mode_03_weighted_hit_count_independent_check.json",
        "checker_sha256": (
            "6e25ecb1684c4e96f6b0f3e69bf3409b3b7d47b2c1bd370867d2e6cb3662c14c"
        ),
        "checker_file_sha256": (
            "71d3b02820d6bcb5f1e537af77587d1e26ed67e858e857d0005b283f59407104"
        ),
    },
    {
        "key": (
            "prospective::builtin_sphere::any_hit_count_continue_u64_per_query::"
            "accept_every_hit_and_continue"
        ),
        "route_id": (
            "prospective::builtin_sphere::any_hit_count_continue_u64_per_query"
        ),
        "mode": "accept_every_hit_and_continue",
        "bundle_file": "mode_04_accept_every_hit_and_continue_bundle.json",
        "bundle_sha256": (
            "72a7a954e94c6704bcc17092af44a091b63c1fc92cf479900845f5c9d02269a1"
        ),
        "bundle_file_sha256": (
            "42cd7cf9d53ba85b3679458f9caf5886c0c3bd44beed2157aa3415ec8ef219cf"
        ),
        "checker_file": (
            "mode_04_accept_every_hit_and_continue_independent_check.json"
        ),
        "checker_sha256": (
            "abeee916066b4028b21c48c82b1cdc4bda5da718704adf88c8232397fd243093"
        ),
        "checker_file_sha256": (
            "89080369c3002b1ef1da8652a5393e7c4d2c3b57633dcbc393ce6833cae60420"
        ),
    },
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="ascii"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _domain_seal(value: Mapping[str, object], field: str, domain: bytes) -> str:
    body = dict(value)
    body[field] = ""
    return hashlib.sha256(domain + _canonical_bytes(body)).hexdigest()


def _authority_seal(value: Mapping[str, object]) -> str:
    return _domain_seal(value, "authority_sha256", AUTHORITY_DOMAIN)


def _evidence_row(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": _file_sha256(path),
    }


def _git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"cannot resolve evidence source {commit}:{path}: "
            f"{completed.stderr.decode(errors='replace').strip()}"
        )
    return completed.stdout


def _validate_source_rows(rows: object, label: str) -> None:
    _require(isinstance(rows, list) and rows, f"{label} source rows absent")
    observed_paths: set[str] = set()
    for row in rows:
        _require(isinstance(row, dict), f"{label} source row is not an object")
        path = row.get("path")
        _require(isinstance(path, str) and path, f"{label} source path invalid")
        _require(path not in observed_paths, f"{label} duplicate source path: {path}")
        observed_paths.add(path)
        blob = _git_blob(EVIDENCE_COMMIT, path)
        _require(row.get("bytes") == len(blob), f"{label} source bytes differ: {path}")
        _require(
            row.get("sha256") == hashlib.sha256(blob).hexdigest(),
            f"{label} source SHA-256 differs: {path}",
        )


def _validate_repository(repository: object, label: str) -> dict[str, object]:
    _require(isinstance(repository, dict), f"{label} repository absent")
    _require(
        repository.get("expected_commit") == EVIDENCE_COMMIT
        and repository.get("head_before") == EVIDENCE_COMMIT
        and repository.get("head_after") == EVIDENCE_COMMIT
        and repository.get("clean_before") is True
        and repository.get("clean_after") is True,
        f"{label} repository custody differs",
    )
    _validate_source_rows(repository.get("source_files"), label)
    return repository


def _validate_build(build: Mapping[str, object]) -> None:
    _require(
        build.get("schema") == "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
        and build.get("status")
        == "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        and build.get("result_sha256")
        == _domain_seal(build, "result_sha256", BUILD_DOMAIN)
        and build.get("all_required_symbols_exported") is True,
        "native build contract differs",
    )
    _validate_repository(build.get("repository"), "native build")
    native = build.get("native_output")
    _require(
        isinstance(native, dict)
        and native.get("bytes") == NATIVE_BYTES
        and native.get("sha256") == NATIVE_SHA256,
        "native output identity differs",
    )


def _validate_checker(path: Path, expected: Mapping[str, str]) -> dict[str, object]:
    report = _load(path)
    _require(_file_sha256(path) == expected["checker_file_sha256"], "checker file differs")
    checks = report.get("property_checks")
    _require(
        report.get("schema") == "rtdl.goal5840.independent_target_check.v1"
        and report.get("route_id") == expected["route_id"]
        and report.get("verdict") == "ACCEPT"
        and report.get("pass_count") == 5
        and report.get("reject_count") == 0
        and report.get("report_sha256") == expected["checker_sha256"]
        and report.get("report_sha256")
        == _domain_seal(report, "report_sha256", CHECK_DOMAIN)
        and isinstance(checks, list)
        and tuple(row.get("property_id") for row in checks if isinstance(row, dict))
        == PROPERTIES
        and all(
            isinstance(row, dict)
            and row.get("verdict") == "PASS"
            and row.get("reason_id") == "PASS__BOUNDED_TARGET_FACTS_MATCH"
            for row in checks
        ),
        f"independent checker result differs: {path.name}",
    )
    claims = report.get("claim_boundary")
    _require(
        isinstance(claims, dict)
        and claims.get("bounded_three_route_target_check_only") is True
        and claims.get("general_compiler_soundness") is False
        and claims.get("application_correctness") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("external_review_or_consensus") is False,
        f"checker claim boundary differs: {path.name}",
    )
    return report


def _validate_bundle(path: Path, expected: Mapping[str, str]) -> dict[str, object]:
    bundle = _load(path)
    _require(
        _file_sha256(path) == expected["bundle_file_sha256"]
        and bundle.get("schema") == "rtdl.v4.target_evidence_bundle.v2"
        and bundle.get("route_id") == expected["route_id"]
        and bundle.get("bundle_sha256") == expected["bundle_sha256"]
        and bundle.get("bundle_sha256")
        == _domain_seal(bundle, "bundle_sha256", BUNDLE_DOMAIN),
        f"target evidence bundle differs: {path.name}",
    )
    return bundle


def _validate_result(result: Mapping[str, object]) -> None:
    _require(
        result.get("schema") == "rtdl.goal5840.true_optix_target_evidence.v7"
        and result.get("status")
        == "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED"
        and result.get("formal_attempt_number") == 7
        and result.get("summary_sha256") == SUMMARY_SHA256
        and result.get("summary_sha256")
        == _domain_seal(result, "summary_sha256", SUMMARY_DOMAIN)
        and result.get("route_bundle_group_count") == 3
        and result.get("required_mode_bundle_count") == 4
        and result.get("true_optix_mode_count") == 4
        and result.get("independent_property_pass_count") == 20
        and result.get("preregistered_unique_mutation_count") == 15
        and result.get("mode_replication_mutation_count") == 20,
        "final GPU result summary differs",
    )
    _validate_repository(result.get("repository"), "GPU result")
    frozen = result.get("frozen_core")
    _require(
        isinstance(frozen, dict)
        and frozen.get("changed_file_count") == 0
        and frozen.get("seal_sha256") == FROZEN_CORE_SEAL_SHA256
        and isinstance(frozen.get("files"), list)
        and len(frozen["files"]) == 3,
        "frozen-core result differs",
    )
    native = result.get("native")
    build = _load(BUILD_PATH)
    build_summary = native.get("build_manifest") if isinstance(native, dict) else None
    _require(
        isinstance(native, dict)
        and native.get("bytes") == NATIVE_BYTES
        and native.get("sha256") == NATIVE_SHA256
        and isinstance(build_summary, dict)
        and build_summary.get("bytes") == BUILD_PATH.stat().st_size
        and build_summary.get("sha256") == _file_sha256(BUILD_PATH)
        and build_summary.get("schema") == build.get("schema")
        and build_summary.get("status") == build.get("status")
        and build_summary.get("result_sha256") == build.get("result_sha256"),
        "GPU result native identity differs",
    )
    machine = result.get("machine")
    _require(
        isinstance(machine, dict)
        and machine.get("name") == "NVIDIA RTX 2000 Ada Generation"
        and machine.get("compute_capability") == "8.9"
        and machine.get("driver") == "580.159.04",
        "GPU target profile differs",
    )
    claims = result.get("claim_boundary")
    _require(
        isinstance(claims, dict)
        and claims.get("three_bounded_routes_only") is True
        and claims.get("four_required_modes") is True
        and claims.get("target_side_structural_refinement_evidence") is True
        and claims.get("sphere_two_level_physical_plan_refinement_independently_derived")
        is True
        and claims.get("exact_native_dso_bound_to_runtime_lookup") is True
        and claims.get("general_compiler_soundness") is False
        and claims.get("application_correctness") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("external_review_or_consensus") is False,
        "GPU result claim boundary differs",
    )
    modes = result.get("mode_cases")
    _require(isinstance(modes, list) and len(modes) == 4, "mode denominator differs")
    for mode, expected in zip(modes, MODE_ROWS, strict=True):
        _require(isinstance(mode, dict), "mode result is not an object")
        _require(
            mode.get("key") == expected["key"]
            and mode.get("route_id") == expected["route_id"]
            and mode.get("mode") == expected["mode"]
            and mode.get("bundle_file") == expected["bundle_file"]
            and mode.get("bundle_sha256") == expected["bundle_sha256"]
            and mode.get("independent_check_file") == expected["checker_file"]
            and mode.get("independent_check_sha256") == expected["checker_sha256"]
            and mode.get("independent_property_pass_count") == 5
            and mode.get("true_optix") is True
            and mode.get("expected_output") == mode.get("observed_output")
            and mode.get("expected_output_sha256")
            == mode.get("observed_output_sha256"),
            f"mode result differs: {expected['key']}",
        )


def _validate_mutations(mutation: Mapping[str, object]) -> None:
    applications = mutation.get("applications")
    _require(
        mutation.get("schema") == "rtdl.goal5840.exact_bundle_mutation_suite.v1"
        and mutation.get("status")
        == "PASS__ALL_FROZEN_MUTATIONS_REJECTED_BEFORE_GPU_LAUNCH"
        and mutation.get("report_sha256")
        == _domain_seal(mutation, "report_sha256", MUTATION_DOMAIN)
        and mutation.get("preregistered_claim_unit_count") == 15
        and mutation.get("mode_replication_application_count") == 20
        and mutation.get("rejected_application_count") == 20
        and mutation.get("all_rejected_before_gpu_launch") is True
        and isinstance(applications, list)
        and len(applications) == 20,
        "mutation result summary differs",
    )
    unique_units = set()
    for row in applications:
        _require(isinstance(row, dict), "mutation row is not an object")
        unique_units.add((row.get("route_id"), row.get("property_id")))
        _require(
            row.get("property_id") in PROPERTIES
            and row.get("checker_verdict") == "REJECT"
            and row.get("target_property_verdict") == "REJECT"
            and row.get("gpu_launch_required_for_rejection") is False,
            "mutation was not rejected before GPU launch",
        )
    _require(len(unique_units) == 15, "unique mutation denominator differs")


def _validate_trust_roots(trust: Mapping[str, object]) -> None:
    roots = trust.get("trust_roots")
    _require(
        trust.get("schema") == "rtdl.goal5840.runtime_trust_roots.v1"
        and trust.get("trust_roots_sha256")
        == _domain_seal(trust, "trust_roots_sha256", TRUST_ROOTS_DOMAIN)
        and isinstance(roots, dict)
        and set(roots) == {row["key"] for row in MODE_ROWS},
        "runtime trust roots differ",
    )
    claims = trust.get("claim_boundary")
    _require(
        isinstance(claims, dict)
        and claims.get("pre_pod_declaration_and_control_roots") is True
        and claims.get("post_materialization_executable_identity_root") is True
        and claims.get("independent_hardware_attestation") is False,
        "runtime trust-root claim boundary differs",
    )


def _validate_verification(
    verification: Mapping[str, object], result: Mapping[str, object]
) -> None:
    _require(
        verification.get("schema")
        == "rtdl.goal5840.downloaded_gpu_evidence_verification.v7"
        and verification.get("status")
        == "PASS__DOWNLOADED_GOAL5840_EVIDENCE_REPLAYED_AND_BOUND"
        and verification.get("verification_sha256") == VERIFICATION_SHA256
        and verification.get("verification_sha256")
        == _domain_seal(
            verification, "verification_sha256", VERIFICATION_DOMAIN
        )
        and verification.get("source_commit") == EVIDENCE_COMMIT
        and verification.get("result_file_sha256") == _file_sha256(RESULT_PATH)
        and verification.get("summary_sha256") == result.get("summary_sha256")
        and verification.get("native_file_sha256") == NATIVE_SHA256
        and verification.get("native_required_symbol_count") == 17
        and verification.get("native_exported_symbol_count") == 861
        and verification.get("native_build_manifest_file_sha256")
        == _file_sha256(BUILD_PATH)
        and verification.get("runtime_trust_roots_file_sha256")
        == _file_sha256(TRUST_ROOTS_PATH)
        and verification.get("mutation_result_file_sha256")
        == _file_sha256(MUTATION_PATH)
        and verification.get("verified_route_group_count") == 3
        and verification.get("verified_mode_count") == 4
        and verification.get("replayed_property_pass_count") == 20
        and verification.get("verified_unique_mutation_count") == 15
        and verification.get("verified_mutation_application_count") == 20,
        "downloaded evidence verification differs",
    )
    claims = verification.get("claim_boundary")
    _require(
        isinstance(claims, dict)
        and claims.get("downloaded_exact_artifact_verification_only") is True
        and claims.get("three_bounded_routes_only") is True
        and claims.get("sphere_two_level_physical_plan_refinement_independently_derived")
        is True
        and claims.get("general_compiler_soundness") is False
        and claims.get("application_correctness") is False
        and claims.get("performance_or_speedup") is False
        and claims.get("external_review_or_consensus") is False,
        "verification claim boundary differs",
    )


def _validate_execution_log(path: Path) -> None:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    stages = [row["stage"] for row in rows if "stage" in row]
    expected_stages = ["preflight_started", "preflight_passed"]
    for _ in MODE_ROWS:
        expected_stages.extend(("mode_started", "mode_passed"))
    expected_stages.extend(("mutation_suite_passed", "capture_passed"))
    _require(stages == expected_stages, "Attempt-07 execution stage order differs")
    _require(
        len(rows) == len(expected_stages) + 1
        and rows[-1].get("status")
        == "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED"
        and rows[-1].get("summary_sha256") == SUMMARY_SHA256,
        "Attempt-07 terminal execution log differs",
    )


def build_authority() -> dict[str, object]:
    build = _load(BUILD_PATH)
    result = _load(RESULT_PATH)
    trust = _load(TRUST_ROOTS_PATH)
    mutation = _load(MUTATION_PATH)
    verification = _load(VERIFICATION_PATH)
    replay = _load(VERIFICATION_REPLAY_PATH)

    _validate_build(build)
    _validate_result(result)
    _validate_trust_roots(trust)
    _validate_mutations(mutation)
    _validate_verification(verification, result)
    _require(verification == replay, "Mac verification replay is not byte-equivalent")
    _require(
        VERIFICATION_PATH.read_bytes() == VERIFICATION_REPLAY_PATH.read_bytes(),
        "Mac verification replay bytes differ",
    )
    _validate_execution_log(EXECUTION_LOG_PATH)

    mode_evidence = []
    for expected in MODE_ROWS:
        bundle_path = GPU_ROOT / expected["bundle_file"]
        checker_path = GPU_ROOT / expected["checker_file"]
        _validate_bundle(bundle_path, expected)
        _validate_checker(checker_path, expected)
        mode_evidence.append({
            "key": expected["key"],
            "route_id": expected["route_id"],
            "mode": expected["mode"],
            "bundle": _evidence_row(bundle_path),
            "bundle_sha256": expected["bundle_sha256"],
            "independent_check": _evidence_row(checker_path),
            "independent_check_sha256": expected["checker_sha256"],
            "independent_property_pass_count": 5,
            "true_optix": True,
        })

    document: dict[str, object] = {
        "schema": "rtdl.goal5840.final_authority.v1",
        "goal": 5840,
        "date": "2026-09-03",
        "status": (
            "PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE"
        ),
        "reviewer_attack": "R3__SAME_IMPLEMENTATION_PROJECTION_IS_NOT_SOUNDNESS",
        "scientific_question": (
            "whether_three_bounded_callback_ir_routes_preserve_five_declared_"
            "properties_through_generated_artifacts_and_true_optix_execution_"
            "under_a_separate_target_side_checker"
        ),
        "answer": "YES__FOR_EXACTLY_THREE_ROUTES_AND_FOUR_MODES",
        "evidence_commit": EVIDENCE_COMMIT,
        "pod_target": {
            "ssh_endpoint": "root@213.173.108.100:12943",
            "gpu": "NVIDIA RTX 2000 Ada Generation",
            "driver": "580.159.04",
            "compute_capability": "8.9",
            "optix_sdk": "9.0.0",
        },
        "native_provider": {
            "bytes": NATIVE_BYTES,
            "sha256": NATIVE_SHA256,
            "committed_to_git": False,
            "bytes_reverified_after_download": True,
            "required_dynamic_symbol_count": 17,
            "exported_dynamic_symbol_count": 861,
        },
        "result": {
            "formal_attempt_number": 7,
            "route_group_count": 3,
            "mode_count": 4,
            "true_optix_mode_count": 4,
            "output_match_count": 4,
            "independent_property_pass_count": 20,
            "unique_mutation_count": 15,
            "mutation_application_count": 20,
            "mutation_rejection_count": 20,
            "frozen_core_changed_file_count": 0,
            "summary_sha256": SUMMARY_SHA256,
            "verification_sha256": VERIFICATION_SHA256,
        },
        "properties": list(PROPERTIES),
        "mode_evidence": mode_evidence,
        "committed_evidence": {
            "preregistration": _evidence_row(PREREGISTRATION_PATH),
            "pre_pod_authority": _evidence_row(PRE_POD_AUTHORITY_PATH),
            "native_build": _evidence_row(BUILD_PATH),
            "gpu_result": _evidence_row(RESULT_PATH),
            "runtime_trust_roots": _evidence_row(TRUST_ROOTS_PATH),
            "mutation_result": _evidence_row(MUTATION_PATH),
            "mac_verification": _evidence_row(VERIFICATION_PATH),
            "mac_verification_replay": _evidence_row(VERIFICATION_REPLAY_PATH),
            "attempt_07_execution_log": _evidence_row(EXECUTION_LOG_PATH),
        },
        "off_repository_raw_capsule": {
            "bytes": RAW_CAPSULE_BYTES,
            "sha256": RAW_CAPSULE_SHA256,
            "contains_native_dso": True,
            "committed_to_git": False,
            "rebuild_required_if_raw_bytes_are_not_retained": True,
        },
        "trusted_computing_base": [
            "evidence_capture_and_runtime_trust_root_recorder",
            "separate_target_checker_implementation",
            "python_runtime_and_standard_library",
            "git_object_database_for_caller_supplied_commit",
            "host_compiler_nvrtc_nvvm_ptx_optix_cuda_driver_and_gpu",
            "sha256_as_integrity_commitment_not_signature",
        ],
        "completion": {
            "preregistered_pass_condition_satisfied": True,
            "goal5840_complete": True,
            "scientific_failure_claimed": False,
            "external_review_deferred_by_owner": True,
            "next_gate": "GOAL5841_EXTERNAL_HUMAN_AUTHORING_CASE_SERIES",
        },
        "claim_boundary": {
            "three_bounded_routes_four_modes_only": True,
            "five_bounded_properties_only": True,
            "separate_target_side_structural_refinement_evidence": True,
            "generated_artifact_mutation_liveness": True,
            "general_compiler_soundness_theorem": False,
            "arbitrary_callback_ir": False,
            "application_correctness": False,
            "performance_or_speedup": False,
            "independent_hardware_attestation": False,
            "external_review_or_consensus": False,
        },
        "authority_sha256": "",
    }
    document["authority_sha256"] = _authority_seal(document)
    return document


def _write_exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii", closefd=True) as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()

    expected = build_authority()
    if args.write:
        if AUTHORITY_PATH.exists():
            raise FileExistsError(AUTHORITY_PATH)
        _write_exclusive(AUTHORITY_PATH, expected)
    else:
        observed = _load(AUTHORITY_PATH)
        _require(observed == expected, "stored final authority does not rederive")
        _require(
            observed.get("authority_sha256") == _authority_seal(observed),
            "stored final authority seal differs",
        )
    print(json.dumps({
        "authority_sha256": expected["authority_sha256"],
        "goal5840_complete": True,
        "mode_count": 4,
        "mutation_application_count": 20,
        "property_pass_count": 20,
        "status": expected["status"],
        "true_optix_mode_count": 4,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
