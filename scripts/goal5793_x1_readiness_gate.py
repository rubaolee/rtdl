"""Fail-closed readiness gate for the single-file Goal5793 X1 review packet."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DISCLOSURE_PATH = HISTORY / "goal5793_x1_owner_off_repository_exposure_disclosure_20260822.json"
NO_ATTESTATION_PATH = HISTORY / "goal5793_x1_no_owner_memory_attestation_boundary_20260822.json"
EXACT_ENV_PATH = HISTORY / "goal5793_x1_exact_environment_capture_20260822.json"
EXACT_ENV_CAPSULE_PATH = HISTORY / "goal5793_x1_exact_environment_capsule_20260822.tar.gz"
EXACT_ENV_CAPSULE_TWIN_PATH = HISTORY / "goal5793_x1_exact_environment_capsule_twin_20260822.tar.gz"
EXACT_ENV_CAPSULE_MANIFEST_PATH = HISTORY / "goal5793_x1_exact_environment_capsule_manifest_20260822.json"
EXACT_ENV_CAPSULE_AUDIT_PATH = HISTORY / "goal5793_x1_exact_environment_capsule_audit_20260822.json"
EXACT_ENV_CAPSULE_VERIFIER_PATH = ROOT / "scripts/goal5793_x1_verify_exact_environment_capsule.py"
EXACT_ENV_CAPSULE_VERIFIER_SHA256 = "ecaea34441d0f505739030c62a04e474757cbf233ab714147d4b7c443cd5af9c"
DISCLOSURE_VALIDATOR_PATH = ROOT / "scripts/goal5793_x1_validate_owner_exposure_disclosure.py"
DISCLOSURE_VALIDATOR_SHA256 = "26af5b7b69a9d3f96e6aee28b9020ccdab15c51a57b74d943d610d5fa8ed48a8"
NO_ATTESTATION_VALIDATOR_PATH = ROOT / "scripts/goal5793_x1_build_no_attestation_boundary.py"
NO_ATTESTATION_VALIDATOR_SHA256 = "bde26a0140095d86c36b8ffd3895a204b678d6f379d9b9b9a8b255ead5aea1aa"

FIXED_ROOTS = {
    "s0_closure": (
        "history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json",
        9317,
        "4d6e37bc19c0f541537e2f9fc36a31b4d35a20bc0fb080ba495629c0d9fd1f41",
    ),
    "declared_exposure_blocker": (
        "history/internal_docs/goal5793_x1_declared_project_exposure_registry_blocker_20260822.json",
        246627536,
        "35b23233d38d0167895b9b4c84d753ccb82db84b4571e981ec3b09ce006a0de2",
    ),
    "survey_exposure": (
        "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json",
        476230,
        "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804",
    ),
    "blocked_environment_v4": (
        "history/internal_docs/goal5793_x1_environment_shared_native_authority_v4_20260822.json",
        15831,
        "2508b82caac38def77dfe8c5ab37ade4ae4d04c1f891c14b271cf4e31350a249",
    ),
    "positive_vectors": (
        "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json",
        49461,
        "07be9926d986c807651dd39f28310ffb905d3bfc1869690839ab29e3ab96e152",
    ),
    "historical_registry": (
        "history/internal_docs/goal5793_x1_historical_registry_authority_20260822.json",
        73828,
        "0d32d6935761d1327a4a9aa86aa3fcbffc1922ee697ee057e012193b613c652f",
    ),
    "historical_stage_pin": (
        "history/internal_docs/goal5793_x1_historical_registry_stage_pin_20260822.json",
        883,
        "3b7c97e68bb436bc5cd709b71867396b7b529b837b319de45042a8f99cd61477",
    ),
    "historical_fixtures": (
        "history/internal_docs/goal5793_x1_historical_registry_fixtures_20260822.json",
        303226,
        "3bf8ef44028510ebcb258e94594fac22a5cc5b070caf37a8579cca0b136b61a3",
    ),
    "historical_runner_receipt": (
        "history/internal_docs/goal5793_x1_historical_fresh_process_exam_receipt_20260822.json",
        8762,
        "fdd38ca118eb9ccac85fc58833023e3e6757209f7e8d11fe809d0c56e4659882",
    ),
    "s0_capsule": (
        "history/internal_docs/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz",
        4284033,
        "83cc4bb3e149d9db16e2386d83d89dd86790a5bee834f7f98d6a257fe3e66bd5",
    ),
    "s0_capsule_twin": (
        "history/internal_docs/goal5793_x1_s0_reproduction_capsule_twin_20260822.tar.gz",
        4284033,
        "83cc4bb3e149d9db16e2386d83d89dd86790a5bee834f7f98d6a257fe3e66bd5",
    ),
    "s0_capsule_manifest": (
        "history/internal_docs/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json",
        7559,
        "b6001ff20c1cee2b7d79b4518b8665d51becc6910531b1a5a80ace8681cbf977",
    ),
    "s0_capsule_audit": (
        "history/internal_docs/goal5793_x1_s0_reproduction_capsule_audit_20260822.json",
        5601,
        "eb5dddf06d3aa8a73400b75f42473d58aa84b4cbd20f9d34925e596152459117",
    ),
}


class ReadinessError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReadinessError(f"json_root_not_object:{path}")
    return value


def _verify_seal(value: Mapping[str, Any], field: str, domain: str, version: int) -> None:
    expected = seal_document(value, seal_field=field, domain=domain, version=version)
    if value.get(field) != expected:
        raise ReadinessError(f"internal_seal_mismatch:{field}")


def _load_exact_module(path: Path, expected_sha256: str, name: str):
    if _sha256(path) != expected_sha256:
        raise ReadinessError(f"module_hash_mismatch:{path}")
    spec = importlib.util.spec_from_file_location(name, path.resolve(strict=True))
    if spec is None or spec.loader is None:
        raise ReadinessError(f"module_spec_unavailable:{path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    return module


def _verify_fixed_roots() -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    for role, (relative, expected_bytes, expected_sha256) in FIXED_ROOTS.items():
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ReadinessError(f"fixed_root_absent_or_nonregular:{role}")
        observed_bytes = path.stat().st_size
        observed_sha256 = _sha256(path)
        if observed_bytes != expected_bytes or observed_sha256 != expected_sha256:
            raise ReadinessError(f"fixed_root_identity_mismatch:{role}")
        records[role] = {"path": relative, "bytes": observed_bytes, "sha256": observed_sha256}

    exposure = _json(ROOT / FIXED_ROOTS["declared_exposure_blocker"][0])
    _verify_seal(
        exposure,
        "authority_sha256",
        "rtdl.goal5793.x1.declared_exposure.successor_authority",
        1,
    )
    if exposure["counts"]["selection_eligible_registry_rows"] != 0:
        raise ReadinessError("exposure_selection_eligible_nonzero")
    survey = _json(ROOT / FIXED_ROOTS["survey_exposure"][0])
    _verify_seal(
        survey,
        "registry_sha256",
        "rtdl.goal5793.x1.survey_exposure.registry_document",
        1,
    )
    if survey["counts"]["bibliography_entries"] != 186:
        raise ReadinessError("survey_bibliography_count_mismatch")
    environment = _json(ROOT / FIXED_ROOTS["blocked_environment_v4"][0])
    _verify_seal(
        environment,
        "authority_sha256",
        "rtdl.goal5793.x1.environment_shared_native_authority",
        4,
    )
    if environment["status"] != "BLOCKS_EXAM_EXECUTION__EXACT_ENVIRONMENT_INCOMPLETE":
        raise ReadinessError("blocked_environment_status_mismatch")
    positive = _json(ROOT / FIXED_ROOTS["positive_vectors"][0])
    _verify_seal(
        positive,
        "authority_sha256",
        "rtdl.goal5793.x1.positive_vector_freeze",
        1,
    )
    if positive["positive_row_count"] != 7 or positive["unique_structural_vector_count"] != 4:
        raise ReadinessError("positive_vector_count_mismatch")
    registry = _json(ROOT / FIXED_ROOTS["historical_registry"][0])
    _verify_seal(
        registry,
        "authority_sha256",
        "rtdl.goal5793.x1.registry_derivation_authority",
        1,
    )
    pin = _json(ROOT / FIXED_ROOTS["historical_stage_pin"][0])
    _verify_seal(
        pin,
        "stage_pin_sha256",
        "rtdl.goal5793.x1.presearch_registry_stage_pin",
        1,
    )
    fixtures = _json(ROOT / FIXED_ROOTS["historical_fixtures"][0])
    _verify_seal(
        fixtures,
        "fixtures_sha256",
        "rtdl.goal5793.x1.historical_registry_fixtures",
        1,
    )
    if fixtures["historical_fixture_count"] != 7:
        raise ReadinessError("historical_fixture_count_mismatch")
    runner = _json(ROOT / FIXED_ROOTS["historical_runner_receipt"][0])
    _verify_seal(
        runner,
        "receipt_sha256",
        "rtdl.goal5793.x1.fresh_process_exam_receipt",
        1,
    )
    if runner["examiner_result"]["status"] != "VALID_LAYERED_EXAMINATION":
        raise ReadinessError("historical_runner_status_mismatch")
    return records


def _verify_environment_capsule() -> dict[str, Any]:
    paths = (
        EXACT_ENV_CAPSULE_PATH,
        EXACT_ENV_CAPSULE_TWIN_PATH,
        EXACT_ENV_CAPSULE_MANIFEST_PATH,
        EXACT_ENV_CAPSULE_AUDIT_PATH,
    )
    if any(not path.is_file() or path.is_symlink() for path in paths):
        raise ReadinessError("exact_environment_capsule_absent_or_nonregular")
    verifier = _load_exact_module(
        EXACT_ENV_CAPSULE_VERIFIER_PATH,
        EXACT_ENV_CAPSULE_VERIFIER_SHA256,
        "_goal5793_x1_readiness_environment_capsule_verifier",
    )
    result = verifier.verify(
        archive_path=EXACT_ENV_CAPSULE_PATH,
        twin_path=EXACT_ENV_CAPSULE_TWIN_PATH,
        manifest_path=EXACT_ENV_CAPSULE_MANIFEST_PATH,
        audit_path=EXACT_ENV_CAPSULE_AUDIT_PATH,
    )
    if result.get("status") != "INDEPENDENT_EXACT_ENVIRONMENT_CAPSULE_VERIFICATION_PASS":
        raise ReadinessError("exact_environment_capsule_verification_failed")
    return result


def readiness() -> dict[str, Any]:
    roots = _verify_fixed_roots()
    blockers: list[str] = []
    optional: dict[str, object] = {}
    memory_attestation_used = False
    if DISCLOSURE_PATH.is_file() and not DISCLOSURE_PATH.is_symlink():
        validator = _load_exact_module(
            DISCLOSURE_VALIDATOR_PATH,
            DISCLOSURE_VALIDATOR_SHA256,
            "_goal5793_x1_readiness_disclosure_validator",
        )
        disclosure = validator.validate(_json(DISCLOSURE_PATH))
        optional["owner_disclosure"] = {
            "path": DISCLOSURE_PATH.relative_to(ROOT).as_posix(),
            "bytes": DISCLOSURE_PATH.stat().st_size,
            "sha256": _sha256(DISCLOSURE_PATH),
            "statement": disclosure["statement"],
            "disclosure_sha256": disclosure["disclosure_sha256"],
        }
        memory_attestation_used = True
    elif NO_ATTESTATION_PATH.is_file() and not NO_ATTESTATION_PATH.is_symlink():
        validator = _load_exact_module(
            NO_ATTESTATION_VALIDATOR_PATH,
            NO_ATTESTATION_VALIDATOR_SHA256,
            "_goal5793_x1_readiness_no_attestation_validator",
        )
        boundary = validator.validate(_json(NO_ATTESTATION_PATH))
        optional["no_owner_memory_attestation_boundary"] = {
            "path": NO_ATTESTATION_PATH.relative_to(ROOT).as_posix(),
            "bytes": NO_ATTESTATION_PATH.stat().st_size,
            "sha256": _sha256(NO_ATTESTATION_PATH),
            "status": boundary["status"],
            "boundary_sha256": boundary["boundary_sha256"],
            "external_review_acceptance_required_before_x2": True,
        }
    else:
        blockers.append("OWNER_DISCLOSURE_OR_CONSERVATIVE_NO_ATTESTATION_BOUNDARY_NOT_PROVIDED")
    if not EXACT_ENV_PATH.is_file() or EXACT_ENV_PATH.is_symlink():
        blockers.append("EXACT_ENVIRONMENT_CAPTURE_NOT_PROVIDED")
    else:
        exact_env = _json(EXACT_ENV_PATH)
        if exact_env.get("schema") != "rtdl.goal5793.x1.exact_environment_capture.v2":
            raise ReadinessError("exact_environment_schema_mismatch")
        _verify_seal(
            exact_env,
            "authority_sha256",
            "rtdl.goal5793.x1.exact_environment_capture",
            2,
        )
        if exact_env.get("status") != "EXACT_TARGET_EXECUTION_ENVIRONMENT_CAPTURED__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION":
            raise ReadinessError("exact_environment_status_mismatch")
        expected_scope = {
            "network_calls": 0,
            "gpu_calls": 0,
            "candidate_work": 0,
            "registered_timing": 0,
            "native_build_performed_by_collector": False,
            "execution_authorized": False,
            "search_entropy_selection_authorized": False,
            "publication_authorized": False,
        }
        if exact_env.get("scope") != expected_scope:
            raise ReadinessError("exact_environment_execution_escalation")
        claim_boundary = exact_env.get("claim_boundary", {})
        if (
            claim_boundary.get("exact_target_execution_environment_frozen") is not True
            or claim_boundary.get("generality_exam_count") != 0
            or claim_boundary.get("usability_evidence_count") != 0
        ):
            raise ReadinessError("exact_environment_claim_boundary_mismatch")
        optional["exact_environment"] = {
            "path": EXACT_ENV_PATH.relative_to(ROOT).as_posix(),
            "bytes": EXACT_ENV_PATH.stat().st_size,
            "sha256": _sha256(EXACT_ENV_PATH),
            "authority_sha256": exact_env["authority_sha256"],
        }
        capsule = _verify_environment_capsule()
        optional["exact_environment_capsule"] = {
            "archive": {
                "path": _display_path(EXACT_ENV_CAPSULE_PATH),
                **capsule["archive"],
            },
            "twin_path": _display_path(EXACT_ENV_CAPSULE_TWIN_PATH),
            "manifest": {
                "path": _display_path(EXACT_ENV_CAPSULE_MANIFEST_PATH),
                **capsule["manifest"],
            },
            "audit": {
                "path": _display_path(EXACT_ENV_CAPSULE_AUDIT_PATH),
                **capsule["audit"],
            },
            "payload_count": capsule["payload_count"],
            "payload_bytes": capsule["payload_bytes"],
            "payload_set_sha256": capsule["payload_set_sha256"],
        }
    ready_status = (
        "READY_FOR_SINGLE_FILE_X1_EXTERNAL_REVIEW"
        if memory_attestation_used
        else "READY_FOR_SINGLE_FILE_X1_EXTERNAL_REVIEW_WITH_NO_MEMORY_ATTESTATION"
    )
    return {
        "status": ready_status if not blockers else "X1_NOT_READY_FOR_REVIEW",
        "fixed_roots": roots,
        "optional_required_roots": optional,
        "blockers": blockers,
        "mechanism_and_historical_evidence_ready": True,
        "x1_complete": False,
        "x2_authorized": False,
        "owner_memory_attestation_used_as_eligibility_evidence": memory_attestation_used,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    result = readiness()
    print(json.dumps(result, sort_keys=True))
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
