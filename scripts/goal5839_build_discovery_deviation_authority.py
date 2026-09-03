#!/usr/bin/env python3
"""Build or verify Goal5839's discovery execution-deviation authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5839_real_artifact_protocol_census_20260903"
)
OUTPUT_PATH = EVIDENCE_ROOT / "DISCOVERY_EXECUTION_DEVIATIONS.json"
SCHEMA = "rtdl.goal5839.discovery_execution_deviations.v1"
DOMAIN = b"rtdl.goal5839.discovery_execution_deviations.v1\0"
FROZEN_AT_UTC = "2026-09-03T07:27:17Z"

PREREGISTRATION_PATH = EVIDENCE_ROOT / "GOAL5839_PREREGISTRATION.json"
PREREGISTRATION_FILE_SHA256 = (
    "995dbbf1e23cb561a97472a83e240a1c29d7972899bf586e8748f7b8a0ba26f3"
)
BINDING_PATH = EVIDENCE_ROOT / "DISCOVERY_EXECUTION_BINDING.json"
BINDING_FILE_SHA256 = (
    "f6753da2ac417a77f842c71ec3e519c13ee91b8b69736fb2bf0077d4c2d390ed"
)
GITHUB_RESULT_PATH = EVIDENCE_ROOT / "DISCOVERY_GITHUB_RESULTS.json"
GITHUB_RESULT_FILE_SHA256 = (
    "6965ab45cf3a5d525ddfc1552bd4c0651c60b5d91b0eb08281153767f260bc8f"
)


class DiscoveryDeviationError(RuntimeError):
    """Fail-closed discovery deviation authority error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiscoveryDeviationError(message)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _seal(value: dict[str, Any]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return _sha256(DOMAIN + _canonical_bytes(body))


def _load_exact(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = path.read_bytes()
    _require(_sha256(payload) == expected_sha256, f"PARENT_FILE_MISMATCH:{path.name}")
    value = json.loads(payload.decode("ascii"))
    _require(isinstance(value, dict), f"PARENT_NOT_OBJECT:{path.name}")
    return value


def build_authority() -> dict[str, Any]:
    preregistration = _load_exact(
        PREREGISTRATION_PATH, PREREGISTRATION_FILE_SHA256)
    binding = _load_exact(BINDING_PATH, BINDING_FILE_SHA256)
    github = _load_exact(GITHUB_RESULT_PATH, GITHUB_RESULT_FILE_SHA256)
    _require(preregistration.get("goal") == 5839, "PREREGISTRATION_GOAL_MISMATCH")
    _require(binding.get("query_rows") is not None, "BINDING_QUERIES_MISSING")
    _require(github.get("query_count") == 29, "GITHUB_QUERY_COUNT_MISMATCH")
    _require(github.get("returned_item_count") == 69, "GITHUB_ITEM_COUNT_MISMATCH")

    authority: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5839,
        "stage": "DISCOVERY_EXECUTION_DEVIATION_REGISTRATION",
        "status": (
            "RECORDED_NONFATAL_EXECUTION_DEVIATIONS__"
            "NO_FIELD_CLASSIFICATION_OR_PAPER_CLAIM"
        ),
        "frozen_at_utc": FROZEN_AT_UTC,
        "parents": {
            "preregistration": {
                "commit": "17c189c0fac5b7d5e9c58cd04c0e81c66e574443",
                "file_sha256": PREREGISTRATION_FILE_SHA256,
                "authority_sha256": preregistration["authority_sha256"],
            },
            "discovery_binding": {
                "commit": "7da8488ce39b3368549e5612483143e81bef08df",
                "file_sha256": BINDING_FILE_SHA256,
                "binding_sha256": binding["binding_sha256"],
            },
            "github_result": {
                "commit": "3726d2af27d05ff02778bcdd19f1e0e3cbaade8f",
                "file_sha256": GITHUB_RESULT_FILE_SHA256,
                "result_sha256": github["result_sha256"],
                "query_count": 29,
                "returned_item_count": 69,
            },
        },
        "deviations": [
            {
                "id": "D001_DISCOVERY_ORDER_NONCONFORMANCE",
                "classification": "PREREGISTERED_EXECUTION_ORDER_VIOLATION",
                "observed": (
                    "GitHub metadata collection started at 2026-09-03T07:08:20Z "
                    "before a paper/publisher result set had been collected."
                ),
                "required": (
                    "PREREGISTRATION.md section 3 orders bibliography and canonical "
                    "paper/publisher inspection before GitHub and general-web results."
                ),
                "effect_assessment": {
                    "denominator_changed": False,
                    "provider_or_query_changed": False,
                    "candidate_source_inspected_before_detection": False,
                    "property_classified_before_detection": False,
                    "fully_preregistered_execution_order_claim_allowed": False,
                    "reason": (
                        "The fixed 29-work denominator and queries did not change, but "
                        "literal order compliance is false and must remain adjacent to results."
                    ),
                },
                "disposition": (
                    "CONTINUE_WITH_FROZEN_DENOMINATOR_AND_QUERIES__"
                    "REPORT_ORDER_DEVIATION_IN_ALL_GOAL5839_CLOSEOUTS"
                ),
            },
            {
                "id": "D002_GENERAL_WEB_FIRST_RUN_ABORTED",
                "classification": "COLLECTOR_TRANSPORT_EXCEPTION_DEFECT",
                "collector": {
                    "commit": "394a05f6ed48421df4fe27679b6074ee2cca5835",
                    "source_sha256": (
                        "6ec128d346189e5c03449385eb76434b00765c588423f5b3de5f919273aa56c0"
                    ),
                },
                "observed": {
                    "completed_progress_rows": 26,
                    "completed_progress_row_status": "TERMINAL_REQUEST_FAILURE",
                    "crashed_work_index": 27,
                    "crash_exception_type": "http.client.RemoteDisconnected",
                    "crash_message": (
                        "Remote end closed connection without response"
                    ),
                    "crash_attempt_index": "UNRESOLVED__IN_MEMORY_ATTEMPTS_LOST",
                    "unattempted_work_indices": [28, 29],
                    "result_file_created": False,
                    "detailed_attempt_records_recoverable": False,
                },
                "effect_assessment": {
                    "first_run_is_a_result_set": False,
                    "empty_results_inferred": False,
                    "query_attempts_repeated_by_repaired_run": True,
                    "reason": (
                        "The collector writes only after all rows complete; the process "
                        "terminated before serialization and its in-memory attempt ledger "
                        "cannot be reconstructed."
                    ),
                },
                "disposition": (
                    "ABORTED_NO_RESULT_ARTIFACT__PRESERVE_INCIDENT__"
                    "RUN_COMPLETE_QUERY_SET_AFTER_NARROW_REPAIR"
                ),
            },
            {
                "id": "D003_RELAUNCH_IMPORT_ENVIRONMENT_FAILURE",
                "classification": "PRE_REQUEST_COMMAND_ENVIRONMENT_FAILURE",
                "observed": (
                    "One relaunch omitted PYTHONPATH=src:. and failed importing the "
                    "scripts package before collect() was entered."
                ),
                "effect_assessment": {
                    "network_request_issued": False,
                    "frozen_attempt_consumed": False,
                    "result_impact": False,
                },
                "disposition": "RELAUNCH_WITH_REPOSITORY_SOURCE_TREE_ENVIRONMENT",
            },
            {
                "id": "D004_POST_FREEZE_TRANSPORT_EXCEPTION_REPAIR",
                "classification": "NARROW_POST_FREEZE_EXECUTOR_REPAIR",
                "repair": {
                    "commit": "9c32aa3387fdefbfea4d2b9b379eb1d90aa76faf",
                    "source_sha256": (
                        "793f43d510ffc39990b66147dbe404f85ed0570f8acd50676a6e4ebb1b7a58f7"
                    ),
                    "test": (
                        "RemoteDisconnected is recorded through exactly the existing "
                        "0/5/30-second retry sequence"
                    ),
                },
                "unchanged": [
                    "29-work denominator",
                    "provider endpoint",
                    "query bytes",
                    "result cap and ordering",
                    "HTML parser",
                    "HTTP-200 success definition",
                    "three-attempt 0/5/30-second retry schedule",
                ],
                "changed": (
                    "http.client.HTTPException now enters the existing recorded failure "
                    "path instead of terminating the process."
                ),
                "effect_assessment": {
                    "collector_source_remained_prefrozen": False,
                    "outcome_dependent_query_change": False,
                    "transport_failure_recording_changed": True,
                    "paper_claim_requires_deviation_disclosure": True,
                },
                "disposition": (
                    "USE_REPAIRED_COLLECTOR_FOR_ONE_COMPLETE_RUN__"
                    "DO_NOT_DESCRIBE_AS_UNDEVIATED_PREREGISTERED_EXECUTION"
                ),
            },
        ],
        "continuation_authority": {
            "fixed_denominator_and_queries_remain_authoritative": True,
            "one_repaired_complete_general_web_run_allowed": True,
            "provider_substitution_allowed": False,
            "query_substitution_allowed": False,
            "failed_first_run_may_be_reported_as_empty_results": False,
            "candidate_source_classification_allowed_by_this_authority": False,
        },
        "claim_boundary": {
            "execution_incident_and_deviation_record_only": True,
            "fully_preregistered_execution_order": False,
            "complete_general_web_result": False,
            "artifact_eligibility": False,
            "protocol_property_classification": False,
            "field_prevalence": False,
            "paper_ready_result": False,
            "external_review_or_consensus": False,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = _seal(authority)
    validate_authority(authority)
    return authority


def validate_authority(authority: dict[str, Any]) -> None:
    _require(authority.get("schema") == SCHEMA, "AUTHORITY_SCHEMA_MISMATCH")
    _require(
        authority.get("authority_sha256") == _seal(authority),
        "AUTHORITY_SEAL_MISMATCH",
    )
    deviations = authority.get("deviations")
    _require(isinstance(deviations, list) and len(deviations) == 4, "DEVIATION_COUNT_MISMATCH")
    _require(
        [row.get("id") for row in deviations]
        == [
            "D001_DISCOVERY_ORDER_NONCONFORMANCE",
            "D002_GENERAL_WEB_FIRST_RUN_ABORTED",
            "D003_RELAUNCH_IMPORT_ENVIRONMENT_FAILURE",
            "D004_POST_FREEZE_TRANSPORT_EXCEPTION_REPAIR",
        ],
        "DEVIATION_ID_MISMATCH",
    )
    boundary = authority.get("claim_boundary")
    _require(
        isinstance(boundary, dict)
        and boundary.get("execution_incident_and_deviation_record_only") is True
        and all(
            value is False
            for key, value in boundary.items()
            if key != "execution_incident_and_deviation_record_only"
        ),
        "CLAIM_BOUNDARY_MISMATCH",
    )
    continuation = authority.get("continuation_authority")
    _require(
        isinstance(continuation, dict)
        and continuation.get("one_repaired_complete_general_web_run_allowed") is True
        and continuation.get("provider_substitution_allowed") is False
        and continuation.get("query_substitution_allowed") is False,
        "CONTINUATION_AUTHORITY_MISMATCH",
    )


def _serialized(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()

    expected = build_authority()
    if args.verify_stored:
        stored = json.loads(args.output.read_text(encoding="ascii"))
        validate_authority(stored)
        _require(_serialized(stored) == _serialized(expected), "STORED_REBUILD_MISMATCH")
        print(json.dumps({
            "authority_sha256": stored["authority_sha256"],
            "file_sha256": _sha256(args.output.read_bytes()),
            "status": "PASS__GOAL5839_DISCOVERY_DEVIATIONS_VERIFIED",
        }, sort_keys=True))
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_serialized(expected))
    print(json.dumps({
        "authority_sha256": expected["authority_sha256"],
        "file_sha256": _sha256(args.output.read_bytes()),
        "status": expected["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
