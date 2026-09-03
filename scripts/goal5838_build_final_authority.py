#!/usr/bin/env python3
"""Build or verify the deterministic Goal5838 final authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT / "history" / "internal_docs" / "goal5838_generic_core_exam_20260902"
)
PREFLIGHT_PATH = EVIDENCE_ROOT / "FINAL_POD_PREFLIGHT.json"
BUILD_PATH = EVIDENCE_ROOT / "FINAL_NATIVE_BUILD_MANIFEST.json"
GPU_PATH = EVIDENCE_ROOT / "FINAL_GPU_EXAM.json"
VERIFICATION_PATH = EVIDENCE_ROOT / "FINAL_GPU_EXAM_VERIFICATION.json"
SEAL_PATH = EVIDENCE_ROOT / "GENERIC_CORE_SEAL.json"
TABLE_PATH = EVIDENCE_ROOT / "CHALLENGE_TABLE.json"
SELECTION_PATH = EVIDENCE_ROOT / "CHALLENGE_SELECTION_RESULT.json"
REPAIR_LOG_PATH = EVIDENCE_ROOT / "FIRST_POD_EXECUTION_REPAIR_LOG.md"
AUTHORITY_PATH = EVIDENCE_ROOT / "FINAL_AUTHORITY.json"

AUTHORITY_DOMAIN = "rtdl.goal5838.final_authority.v1"
BUILD_DOMAIN = "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
EVIDENCE_COMMIT = "7da68056550818d8e2f6cdb4d7aa3e9029cc4524"
BASELINE_COMMIT = "0f5c9d4297f73e412732e5a8ab133423fe4cfd21"
SELECTED_CANDIDATE_ID = "builtin_sphere::any_hit_count_continue_u64_per_query"
GENERIC_CORE_SEAL_SHA256 = (
    "c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae"
)
SELECTION_RESULT_SHA256 = (
    "9f543f52cd9453e0410766aa79c3f302a6a0e39314487279842fa5ad5e57ed61"
)
CHALLENGE_TABLE_SHA256 = (
    "0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345"
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha(value: object, label: str) -> str:
    _require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        f"{label} is not lowercase SHA-256",
    )
    return value


def _empty_field_seal(value: dict[str, object], field: str) -> str:
    body = dict(value)
    body[field] = ""
    return _digest(body)


def _absent_field_seal(value: dict[str, object], field: str) -> str:
    body = dict(value)
    body.pop(field, None)
    return _digest(body)


def _build_seal(value: dict[str, object]) -> str:
    body = dict(value)
    body["result_sha256"] = ""
    return hashlib.sha256(
        BUILD_DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()


def _authority_seal(value: dict[str, object]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return hashlib.sha256(
        AUTHORITY_DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()


def _domain_seal(value: dict[str, object], field: str, domain: str) -> str:
    body = dict(value)
    body[field] = ""
    return hashlib.sha256(
        domain.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()


def _evidence_row(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def build_authority() -> dict[str, object]:
    preflight = _load(PREFLIGHT_PATH)
    build = _load(BUILD_PATH)
    gpu = _load(GPU_PATH)
    verification = _load(VERIFICATION_PATH)
    seal = _load(SEAL_PATH)
    table = _load(TABLE_PATH)
    selection = _load(SELECTION_PATH)

    _require(
        preflight.get("schema") == "rtdl.goal5838.pod_preflight.v2"
        and preflight.get("status")
        == "PASS__GOAL5838_POD_READY_FOR_FROZEN_GPU_EXAM__NO_GPU_EXECUTION_CLAIM"
        and preflight.get("ready_for_gpu_exam") is True
        and preflight.get("repair_required_checks") == []
        and preflight.get("scientific_failure_claimed") is False
        and preflight.get("gpu_execution_performed") is False
        and preflight.get("performance_claim_authorized") is False
        and preflight.get("expected_commit") == EVIDENCE_COMMIT
        and preflight.get("baseline_commit") == BASELINE_COMMIT
        and preflight.get("result_sha256")
        == _empty_field_seal(preflight, "result_sha256"),
        "final preflight identity differs",
    )
    checks = preflight.get("checks")
    _require(
        isinstance(checks, list)
        and checks
        and all(
            isinstance(row, dict)
            and (row.get("passed") is True or row.get("required") is False)
            for row in checks
        ),
        "final preflight contains a required failure",
    )
    callback_probe = preflight.get("probes", {}).get(
        "selected_callback_compiler"
    )
    _require(
        isinstance(callback_probe, dict)
        and callback_probe.get("passed") is True
        and callback_probe.get("gpu_execution_performed") is False
        and callback_probe.get("native_prepare_called") is False
        and callback_probe.get("optix_launch_count") == 0,
        "selected callback preflight boundary differs",
    )

    build_repository = build.get("repository")
    build_input = build.get("build_input")
    _require(
        build.get("schema") == BUILD_DOMAIN
        and build.get("status")
        == "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        and build.get("result_sha256") == _build_seal(build)
        and build.get("all_required_symbols_exported") is True
        and isinstance(build_repository, dict)
        and build_repository.get("expected_commit") == EVIDENCE_COMMIT
        and build_repository.get("head_before") == EVIDENCE_COMMIT
        and build_repository.get("head_after") == EVIDENCE_COMMIT
        and build_repository.get("clean_before") is True
        and build_repository.get("clean_after") is True
        and isinstance(build_input, dict)
        and build.get("dynamic_nvrtc")
        == {
            "path": build_input.get("nvrtc_library_path"),
            "bytes": build_input.get("nvrtc_library_bytes"),
            "sha256": build_input.get("nvrtc_library_sha256"),
        },
        "final native build identity differs",
    )

    expected_summary = {
        "frozen_core_changed_file_count": 0,
        "oracle_case_count": 12,
        "oracle_exact_match_count": 12,
        "true_optix_launch_count": 2,
    }
    gpu_repository = gpu.get("repository")
    _require(
        gpu.get("schema") == "rtdl.goal5838.selected_sphere_gpu_exam.v1"
        and gpu.get("status")
        == "PASS__BOUNDED_PROSPECTIVE_FROZEN_CORE_TOPOLOGY"
        and gpu.get("result_sha256")
        == _absent_field_seal(gpu, "result_sha256")
        and gpu.get("summary") == expected_summary
        and gpu.get("native_build") == build
        and isinstance(gpu_repository, dict)
        and gpu_repository.get("expected_commit") == EVIDENCE_COMMIT
        and gpu_repository.get("head_commit") == EVIDENCE_COMMIT
        and gpu_repository.get("head_after_execution") == EVIDENCE_COMMIT
        and gpu_repository.get("clean_before_execution") is True
        and gpu_repository.get("clean_after_execution") is True
        and gpu.get("selection", {}).get("candidate_id")
        == SELECTED_CANDIDATE_ID
        and gpu.get("selection", {}).get("selection_result_sha256")
        == SELECTION_RESULT_SHA256
        and gpu.get("frozen_core", {}).get("generic_core_seal_sha256")
        == GENERIC_CORE_SEAL_SHA256,
        "final GPU artifact identity differs",
    )
    _require(
        gpu.get("claim_boundary")
        == {
            "one_bounded_prospective_result": True,
            "arbitrary_callback_ir_gpu_execution": False,
            "universal_provider_portability": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "final GPU claim boundary differs",
    )

    _require(
        verification.get("schema")
        == "rtdl.goal5838.selected_sphere_gpu_exam_verification.v1"
        and verification.get("status")
        == "PASS__INDEPENDENT_ARTIFACT_REDERIVATION"
        and verification.get("verification_sha256")
        == _absent_field_seal(verification, "verification_sha256")
        and verification.get("artifact_file_sha256") == _file_sha256(GPU_PATH)
        and verification.get("artifact_result_sha256")
        == gpu.get("result_sha256")
        and verification.get("repository_commit") == EVIDENCE_COMMIT
        and verification.get("selected_candidate_id") == SELECTED_CANDIDATE_ID
        and verification.get("source_file_count") == 34
        and verification.get("frozen_core_changed_file_count") == 0
        and verification.get("true_optix_launch_count") == 2
        and verification.get("oracle_exact_match_count") == 12
        and verification.get("native_library_bytes_reverified") is True
        and verification.get("performance_claim_authorized") is False
        and verification.get("external_review_or_consensus_claimed") is False,
        "final independent verification identity differs",
    )
    _require(
        table.get("schema") == "rtdl.goal5838.prospective_challenge_table.v1"
        and table.get("status") == "FROZEN_COMPLETE_TABLE__NO_CHALLENGE_SELECTED"
        and table.get("challenge_table_sha256") == CHALLENGE_TABLE_SHA256
        and table.get("challenge_table_sha256")
        == _domain_seal(
            table,
            "challenge_table_sha256",
            "rtdl.goal5838.prospective_challenge_table.v1",
        )
        and table.get("eligible_candidate_count") == 10
        and table.get("selection", {}).get("selected_candidate_id") is None,
        "frozen challenge-table authority differs",
    )
    _require(
        seal.get("schema") == "rtdl.goal5838.generic_core_seal.v1"
        and seal.get("seal_sha256") == GENERIC_CORE_SEAL_SHA256
        and seal.get("seal_sha256")
        == _domain_seal(
            seal,
            "seal_sha256",
            "rtdl.goal5838.generic_core_seal.v1",
        )
        and seal.get("challenge_table", {}).get("authority_sha256")
        == CHALLENGE_TABLE_SHA256
        and seal.get("challenge_table", {}).get("selected_candidate_count") == 0,
        "frozen generic-core authority differs",
    )
    selected = selection.get("selected_candidate")
    mapping = selection.get("mapping")
    _require(
        selection.get("schema") == "rtdl.goal5838.challenge_selection_result.v1"
        and selection.get("status")
        == "PASS__INDEPENDENT_CHALLENGE_SELECTED__IMPLEMENTATION_NOT_STARTED"
        and selection.get("selection_result_sha256") == SELECTION_RESULT_SHA256
        and selection.get("selection_result_sha256")
        == _domain_seal(
            selection,
            "selection_result_sha256",
            "rtdl.goal5838.challenge_selection_result.v1",
        )
        and selection.get("challenge_table_sha256") == CHALLENGE_TABLE_SHA256
        and selection.get("generic_core_seal_sha256") == GENERIC_CORE_SEAL_SHA256
        and isinstance(selected, dict)
        and selected.get("candidate_id") == SELECTED_CANDIDATE_ID
        and selected.get("stable_index") == 3
        and isinstance(mapping, dict)
        and mapping.get("selected_index") == 3
        and selection.get("activity_at_selection")
        == {
            "candidate_execution_count": 0,
            "candidate_implementation_count": 0,
            "gpu_receipt_count": 0,
            "prospective_success_count": 0,
        },
        "independent challenge-selection authority differs",
    )

    target = gpu["target"]
    compiler_environment = gpu["toolchain"]["compiler_environment"]
    native_output = build["native_output"]
    document = {
        "schema": AUTHORITY_DOMAIN,
        "goal": 5838,
        "date": "2026-09-03",
        "status": "PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE",
        "scientific_question": (
            "schema_driven_frozen_core_executes_independently_selected_new_"
            "topology_without_core_change"
        ),
        "answer": "YES__ONE_BOUNDED_PROSPECTIVE_TRUE_OPTIX_RESULT",
        "evidence_commit": EVIDENCE_COMMIT,
        "baseline_commit": BASELINE_COMMIT,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "frozen_authorities": {
            "generic_core_seal_sha256": GENERIC_CORE_SEAL_SHA256,
            "challenge_table_sha256": CHALLENGE_TABLE_SHA256,
            "selection_result_sha256": SELECTION_RESULT_SHA256,
            "frozen_core_changed_file_count": 0,
            "authority_files": [
                _evidence_row(path)
                for path in (TABLE_PATH, SEAL_PATH, SELECTION_PATH)
            ],
        },
        "pod_target": {
            "ssh_endpoint": "root@213.173.108.100:12943",
            "gpu": target["gpu"],
            "optix_sdk": target["optix_sdk"],
            "compute_capability": target["compute_capability"],
            "compiler_environment_identity_sha256": compiler_environment[
                "identity_sha256"
            ],
        },
        "native_provider": {
            "bytes": native_output["bytes"],
            "sha256": native_output["sha256"],
            "committed_to_git": False,
            "bytes_reverified_by_independent_verifier": True,
            "all_required_symbols_exported": True,
        },
        "prospective_result": expected_summary,
        "evidence_files": [
            _evidence_row(path)
            for path in (PREFLIGHT_PATH, BUILD_PATH, GPU_PATH, VERIFICATION_PATH)
        ],
        "repair_log": _evidence_row(REPAIR_LOG_PATH),
        "completion": {
            "preregistered_success_condition_satisfied": True,
            "goal5838_complete": True,
            "scientific_failure_claimed": False,
            "external_review_deferred_by_owner": True,
        },
        "claim_boundary": {
            "one_bounded_prospective_frozen_core_topology_result": True,
            "arbitrary_callback_ir_gpu_execution": False,
            "universal_provider_portability": False,
            "performance_or_speedup": False,
            "paper_app": False,
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
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=True) as stream:
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
    print(
        json.dumps(
            {
                "authority_sha256": expected["authority_sha256"],
                "evidence_commit": EVIDENCE_COMMIT,
                "frozen_core_changed_file_count": 0,
                "goal5838_complete": True,
                "oracle_exact_match_count": 12,
                "status": expected["status"],
                "true_optix_launch_count": 2,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
