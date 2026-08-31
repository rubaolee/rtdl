#!/usr/bin/env python3
"""Offline-only synthetic rehearsal of the frozen Goal5793 selection client.

This module has no network path.  It exercises authenticated synthetic pulses,
the exact first-next anchor and exact-target rules, and the frozen 21-field TLV
mapping.  Its output is never a scientific selection and is unusable as a live
NIST receipt until the separately pinned normative NIST source bytes and a
reviewed normative verifier exist.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x2_nist_synthetic_crypto import verify_synthetic_pulse
from scripts.goal5793_x2_offline_core import (
    SELECTION_FIELDS,
    X2Error,
    select_index,
    validate_anchor_first_next,
    validate_exact_target,
    validate_pulse_structure,
)


API_BASE = "https://beacon.nist.gov/beacon/2.0"
POLL_SCHEDULE_SECONDS = (0, 15, 30, 60, 120, 300, 600, 1200, 1800, 3600)


def _exact_keys(value: Mapping[str, Any], expected: set[str], reason: str) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise X2Error(reason)


def _authenticate(bundle: Mapping[str, Any], trusted_root_sha256: str) -> dict[str, Any]:
    _exact_keys(
        bundle,
        {"response", "leaf_certificate_pem", "root_certificate_pem"},
        "SYNTHETIC_AUTHENTICATION_BUNDLE_SCHEMA_MISMATCH",
    )
    leaf = bundle["leaf_certificate_pem"]
    root = bundle["root_certificate_pem"]
    if not isinstance(leaf, (bytes, bytearray)) or not isinstance(root, (bytes, bytearray)):
        raise X2Error("SYNTHETIC_CERTIFICATE_BYTES_REQUIRED")
    receipt = verify_synthetic_pulse(
        bundle["response"],
        leaf_certificate_pem=bytes(leaf),
        root_certificate_pem=bytes(root),
        trusted_root_sha256=trusted_root_sha256,
    )
    return {"receipt": receipt, "structural": validate_pulse_structure(bundle["response"])}


def _validate_target_attempts(
    attempts: Sequence[Mapping[str, Any]],
    *,
    target_ms: int,
) -> tuple[Mapping[str, Any], list[dict[str, Any]]]:
    if not isinstance(attempts, Sequence) or isinstance(attempts, (str, bytes, bytearray)):
        raise X2Error("TARGET_ATTEMPT_SEQUENCE_INVALID")
    if not attempts or len(attempts) > len(POLL_SCHEDULE_SECONDS):
        raise X2Error("TARGET_ATTEMPT_COUNT_INVALID")
    exact_request_uri = f"{API_BASE}/pulse/time/{target_ms}"
    audit: list[dict[str, Any]] = []
    accepted: Mapping[str, Any] | None = None
    for index, attempt in enumerate(attempts):
        _exact_keys(attempt, {"scheduled_offset_seconds", "request_uri", "response", "error"}, "TARGET_ATTEMPT_SCHEMA_MISMATCH")
        if attempt["scheduled_offset_seconds"] != POLL_SCHEDULE_SECONDS[index]:
            raise X2Error("TARGET_POLL_SCHEDULE_DRIFT")
        if attempt["request_uri"] != exact_request_uri:
            raise X2Error("TARGET_REQUEST_URI_DRIFT")
        response, error = attempt["response"], attempt["error"]
        if (response is None) == (error is None):
            raise X2Error("TARGET_ATTEMPT_OUTCOME_SCHEMA_MISMATCH")
        if error is not None:
            if not isinstance(error, str) or not error:
                raise X2Error("TARGET_ATTEMPT_ERROR_INVALID")
            audit.append({"attempt": index, "classification": "MISSING_OR_ERROR__SAME_TARGET_RETAINED"})
            continue
        structure = validate_pulse_structure(response)
        if structure["timestamp_ms"] != target_ms:
            audit.append(
                {
                    "attempt": index,
                    "classification": "NEXT_CLOSEST_OR_NONEXACT_REJECTED__SAME_TARGET_RETAINED",
                    "returned_timestamp_ms": structure["timestamp_ms"],
                }
            )
            continue
        accepted = response
        audit.append({"attempt": index, "classification": "EXACT_TARGET_CANDIDATE"})
        if index != len(attempts) - 1:
            raise X2Error("TARGET_ATTEMPTS_AFTER_EXACT_RESPONSE_FORBIDDEN")
    if accepted is None:
        raise X2Error("TERMINAL_INFRASTRUCTURE_FAILURE__NO_SELECTION__NO_ALTERNATE_OR_DELAYED_RETRY")
    return accepted, audit


def _authenticate_chain(
    responses: Sequence[Mapping[str, Any]],
    *,
    anchor_response: Mapping[str, Any],
    accepted_target_response: Mapping[str, Any],
    leaf_certificate_pem: bytes,
    root_certificate_pem: bytes,
    trusted_root_sha256: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(responses, Sequence) or isinstance(responses, (str, bytes, bytearray)) or len(responses) != 1440:
        raise X2Error("TARGET_CHAIN_PROOF_COUNT_MISMATCH")
    previous_response = anchor_response
    previous = validate_pulse_structure(previous_response)
    rows: list[dict[str, Any]] = []
    final_auth: dict[str, Any] | None = None
    for offset, response in enumerate(responses, start=1):
        current = validate_pulse_structure(response)
        if current["chain_index"] != previous["chain_index"] or current["pulse_index"] != previous["pulse_index"] + 1 or current["timestamp_ms"] != previous["timestamp_ms"] + 60_000:
            raise X2Error("TARGET_CHAIN_SEQUENCE_MISMATCH")
        links = response["pulse"]["listValues"]
        expected_link = {"uri": previous_response["pulse"]["uri"], "type": "previous", "value": previous["output_value"]}
        if links != [expected_link]:
            raise X2Error("TARGET_CHAIN_LINK_MISMATCH")
        final_auth = _authenticate(
            {"response": response, "leaf_certificate_pem": leaf_certificate_pem, "root_certificate_pem": root_certificate_pem},
            trusted_root_sha256,
        )
        rows.append(
            {
                "offset": offset,
                "chain_index": current["chain_index"],
                "pulse_index": current["pulse_index"],
                "timestamp_ms": current["timestamp_ms"],
                "output_value": current["output_value"],
                "receipt_sha256": final_auth["receipt"]["receipt_sha256"],
            }
        )
        previous_response = response
        previous = current
    if canonical_json_bytes(previous_response) != canonical_json_bytes(accepted_target_response):
        raise X2Error("TARGET_CHAIN_FINAL_RESPONSE_MISMATCH")
    assert final_auth is not None
    return final_auth, rows


def rehearse_synthetic_selection(fixture: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "schema",
        "mode",
        "synthetic_fixture",
        "triplets",
        "base_inputs",
        "not_before_ms",
        "trusted_root_sha256",
        "previous",
        "anchor",
        "target_leaf_certificate_pem",
        "target_root_certificate_pem",
        "target_chain_responses",
        "target_attempts",
    }
    _exact_keys(fixture, required, "SELECTION_FIXTURE_SCHEMA_MISMATCH")
    if fixture["schema"] != "rtdl.goal5793.x2.synthetic_selection_fixture.v1":
        raise X2Error("SELECTION_FIXTURE_SCHEMA_MISMATCH")
    if fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or fixture["synthetic_fixture"] is not True:
        raise X2Error("SELECTION_FIXTURE_MODE_INVALID")
    triplets = fixture["triplets"]
    if not isinstance(triplets, list):
        raise X2Error("SELECTION_TRIPLETS_INVALID")
    for triplet in triplets:
        if not isinstance(triplet, list) or len(triplet) != 3 or any(not isinstance(value, str) or not value for value in triplet):
            raise X2Error("SELECTION_TRIPLET_SCHEMA_MISMATCH")
    if len({tuple(row) for row in triplets}) != len(triplets):
        raise X2Error("SELECTION_TRIPLET_DUPLICATE")
    base = fixture["base_inputs"]
    if not isinstance(base, Mapping) or set(base) != set(SELECTION_FIELDS) - {"counter"}:
        raise X2Error("SELECTION_BASE_FIELD_SET_MISMATCH")
    if base["ordered_triplet_count"] != len(triplets):
        raise X2Error("SELECTION_TRIPLET_COUNT_CROSSBIND_MISMATCH")

    if not triplets:
        if fixture["target_chain_responses"] != []:
            raise X2Error("ZERO_CARDINALITY_CHAIN_PROOF_FORBIDDEN")
        result = select_index(base, 0)
        pulse_authentication_count = 0
        selected_fixture_triplet = None
        pulse_evidence = None
        target_attempt_audit: list[dict[str, Any]] = []
    else:
        trusted_root = fixture["trusted_root_sha256"]
        if not isinstance(trusted_root, str) or len(trusted_root) != 64:
            raise X2Error("SYNTHETIC_TRUST_ROOT_PIN_INVALID")
        previous = _authenticate(fixture["previous"], trusted_root)
        anchor = _authenticate(fixture["anchor"], trusted_root)
        linked = validate_anchor_first_next(
            fixture["anchor"]["response"],
            fixture["previous"]["response"],
            fixture["not_before_ms"],
        )
        target_ms = anchor["structural"]["timestamp_ms"] + 86_400_000
        target_response, target_attempt_audit = _validate_target_attempts(fixture["target_attempts"], target_ms=target_ms)
        target, chain_rows = _authenticate_chain(
            fixture["target_chain_responses"],
            anchor_response=fixture["anchor"]["response"],
            accepted_target_response=target_response,
            leaf_certificate_pem=fixture["target_leaf_certificate_pem"],
            root_certificate_pem=fixture["target_root_certificate_pem"],
            trusted_root_sha256=trusted_root,
        )
        target_structure = validate_exact_target(target_response, linked["anchor"], target_ms)
        crossbind = {
            "anchor_chain_index": anchor["structural"]["chain_index"],
            "anchor_pulse_index": anchor["structural"]["pulse_index"],
            "anchor_timestamp_ms": anchor["structural"]["timestamp_ms"],
            "anchor_certificate_id": anchor["structural"]["certificate_id"],
            "anchor_output_value": anchor["structural"]["output_value"],
            "target_chain_index": target_structure["chain_index"],
            "target_pulse_index": target_structure["pulse_index"],
            "target_timestamp_ms": target_structure["timestamp_ms"],
            "target_certificate_id": target_structure["certificate_id"],
            "target_output_value": target_structure["output_value"],
        }
        for field, observed in crossbind.items():
            if base[field] != observed:
                raise X2Error("SELECTION_PULSE_FRAME_CROSSBIND_MISMATCH", field)
        result = select_index(base, len(triplets))
        pulse_authentication_count = 1442
        selected_fixture_triplet = triplets[result["selected_index"]]
        pulse_evidence = {
            "previous_receipt_sha256": previous["receipt"]["receipt_sha256"],
            "anchor_receipt_sha256": anchor["receipt"]["receipt_sha256"],
            "target_receipt_sha256": target["receipt"]["receipt_sha256"],
            "anchor_to_target_chain_pulse_count": len(chain_rows),
            "anchor_to_target_chain_rows_sha256": hashlib.sha256(canonical_json_bytes(chain_rows)).hexdigest(),
        }

    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.synthetic_selection_rehearsal_receipt.v1",
        "status": "OFFLINE_SYNTHETIC_SELECTION_MAPPING_REHEARSAL__NOT_ENTROPY_OR_SCIENTIFIC_SELECTION",
        "synthetic_only": True,
        "nist_ir_8213_normative_serialization_claimed": False,
        "live_nist_acceptance_usable": False,
        "scientific_selection_made": False,
        "triplet_count": len(triplets),
        "triplets_file_projection_sha256": hashlib.sha256(canonical_json_bytes(triplets)).hexdigest(),
        "pulse_authentication_count": pulse_authentication_count,
        "target_attempt_audit": target_attempt_audit,
        "mapping_result": result,
        "synthetic_selected_fixture_triplet": selected_fixture_triplet,
        "pulse_evidence": pulse_evidence,
        "activity": {
            "network_calls": 0,
            "live_beacon_requests": 0,
            "entropy_draws": 0,
            "scientific_selections": 0,
            "candidate_implementations": 0,
            "candidate_executions": 0,
            "gpu_ssh_pod": 0,
            "registered_or_performance_timings": 0,
        },
        "authorization": {
            "live_search": False,
            "beacon_or_entropy": False,
            "candidate_selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
        },
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = seal_document(
        receipt,
        seal_field="receipt_sha256",
        domain="rtdl.goal5793.x2.synthetic_selection_rehearsal_receipt",
        version=1,
    )
    return receipt
