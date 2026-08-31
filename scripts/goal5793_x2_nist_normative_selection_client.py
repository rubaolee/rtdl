#!/usr/bin/env python3
"""Offline rehearsal of the frozen selection path with the NISTIR verifier.

All inputs are caller-supplied synthetic fixtures.  There is deliberately no
HTTP implementation.  The client authenticates the first-next predecessor and
anchor, every one of the 1,440 adjacent pulses through the exact target, and
only then applies the frozen 21-field unbiased selection mapping.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x2_nist_normative_verifier import (
    source_interpretation_boundary,
    verify_adjacent_pulses,
    verify_normative_chain,
    verify_normative_pulse,
)
from scripts.goal5793_x2_offline_core import (
    SELECTION_FIELDS,
    X2Error,
    select_index,
    validate_anchor_first_next,
    validate_exact_target,
    validate_pulse_structure,
)
from scripts.goal5793_x2_selection_client import API_BASE, POLL_SCHEDULE_SECONDS


def _fail(reason: str) -> None:
    raise X2Error(reason)


def _exact_keys(value: Mapping[str, Any], expected: set[str], reason: str) -> None:
    if not isinstance(value, Mapping) or set(value) != expected:
        _fail(reason)


def _authenticate(
    bundle: Mapping[str, Any],
    *,
    root_certificate_pem: bytes,
    trust_bundle: Mapping[str, Any],
    trusted_trust_bundle_sha256: str,
) -> dict[str, Any]:
    _exact_keys(bundle, {"response", "leaf_certificate_pem"}, "NISTIR_AUTHENTICATION_BUNDLE_SCHEMA_MISMATCH")
    if not isinstance(bundle["response"], Mapping) or not isinstance(bundle["leaf_certificate_pem"], bytes):
        _fail("NISTIR_AUTHENTICATION_BUNDLE_SCHEMA_MISMATCH")
    receipt = verify_normative_pulse(
        bundle["response"],
        leaf_certificate_pem=bundle["leaf_certificate_pem"],
        root_certificate_pem=root_certificate_pem,
        trust_bundle=trust_bundle,
        trusted_trust_bundle_sha256=trusted_trust_bundle_sha256,
    )
    return {"receipt": receipt, "structural": validate_pulse_structure(bundle["response"])}


def _validate_target_attempts(
    attempts: Sequence[Mapping[str, Any]],
    *,
    target_ms: int,
) -> tuple[Mapping[str, Any], list[dict[str, Any]]]:
    if not isinstance(attempts, Sequence) or isinstance(attempts, (str, bytes, bytearray)):
        _fail("TARGET_ATTEMPT_SEQUENCE_INVALID")
    if not attempts or len(attempts) > len(POLL_SCHEDULE_SECONDS):
        _fail("TARGET_ATTEMPT_COUNT_INVALID")
    exact_uri = f"{API_BASE}/pulse/time/{target_ms}"
    accepted: Mapping[str, Any] | None = None
    audit: list[dict[str, Any]] = []
    for index, attempt in enumerate(attempts):
        _exact_keys(attempt, {"scheduled_offset_seconds", "request_uri", "response", "error"}, "TARGET_ATTEMPT_SCHEMA_MISMATCH")
        if attempt["scheduled_offset_seconds"] != POLL_SCHEDULE_SECONDS[index]:
            _fail("TARGET_POLL_SCHEDULE_DRIFT")
        if attempt["request_uri"] != exact_uri:
            _fail("TARGET_REQUEST_URI_DRIFT")
        response, error = attempt["response"], attempt["error"]
        if (response is None) == (error is None):
            _fail("TARGET_ATTEMPT_OUTCOME_SCHEMA_MISMATCH")
        if error is not None:
            if not isinstance(error, str) or not error:
                _fail("TARGET_ATTEMPT_ERROR_INVALID")
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
            _fail("TARGET_ATTEMPTS_AFTER_EXACT_RESPONSE_FORBIDDEN")
    if accepted is None:
        _fail("TERMINAL_INFRASTRUCTURE_FAILURE__NO_SELECTION__NO_ALTERNATE_OR_DELAYED_RETRY")
    return accepted, audit


def rehearse_normative_offline_selection(
    fixture: Mapping[str, Any],
    *,
    trusted_trust_bundle_sha256: str,
) -> dict[str, Any]:
    required = {
        "schema",
        "mode",
        "synthetic_fixture",
        "triplets",
        "base_inputs",
        "not_before_ms",
        "root_certificate_pem",
        "trust_bundle",
        "previous",
        "anchor",
        "target_chain_bundles",
        "target_attempts",
    }
    _exact_keys(fixture, required, "NISTIR_SELECTION_FIXTURE_SCHEMA_MISMATCH")
    if fixture["schema"] != "rtdl.goal5793.x2.nistir_normative_offline_selection_fixture.v1":
        _fail("NISTIR_SELECTION_FIXTURE_SCHEMA_MISMATCH")
    if fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or fixture["synthetic_fixture"] is not True:
        _fail("NISTIR_SELECTION_FIXTURE_MODE_INVALID")
    if not isinstance(fixture["root_certificate_pem"], bytes) or not isinstance(fixture["trust_bundle"], Mapping):
        _fail("NISTIR_SELECTION_TRUST_INPUT_INVALID")
    triplets = fixture["triplets"]
    if not isinstance(triplets, list):
        _fail("SELECTION_TRIPLETS_INVALID")
    for triplet in triplets:
        if not isinstance(triplet, list) or len(triplet) != 3 or any(not isinstance(value, str) or not value for value in triplet):
            _fail("SELECTION_TRIPLET_SCHEMA_MISMATCH")
    if len({tuple(row) for row in triplets}) != len(triplets):
        _fail("SELECTION_TRIPLET_DUPLICATE")
    base = fixture["base_inputs"]
    if not isinstance(base, Mapping) or set(base) != set(SELECTION_FIELDS) - {"counter"}:
        _fail("SELECTION_BASE_FIELD_SET_MISMATCH")
    if base["ordered_triplet_count"] != len(triplets):
        _fail("SELECTION_TRIPLET_COUNT_CROSSBIND_MISMATCH")

    if not triplets:
        if fixture["target_chain_bundles"] != []:
            _fail("ZERO_CARDINALITY_CHAIN_PROOF_FORBIDDEN")
        result = select_index(base, 0)
        pulse_authentication_count = 0
        pulse_evidence = None
        target_attempt_audit: list[dict[str, Any]] = []
        selected_fixture_triplet = None
    else:
        chain_bundles = fixture["target_chain_bundles"]
        if not isinstance(chain_bundles, list) or len(chain_bundles) != 1440:
            _fail("TARGET_CHAIN_PROOF_COUNT_MISMATCH")
        root_pem = fixture["root_certificate_pem"]
        trust = fixture["trust_bundle"]
        previous = _authenticate(
            fixture["previous"],
            root_certificate_pem=root_pem,
            trust_bundle=trust,
            trusted_trust_bundle_sha256=trusted_trust_bundle_sha256,
        )
        anchor = _authenticate(
            fixture["anchor"],
            root_certificate_pem=root_pem,
            trust_bundle=trust,
            trusted_trust_bundle_sha256=trusted_trust_bundle_sha256,
        )
        linked = validate_anchor_first_next(
            fixture["anchor"]["response"],
            fixture["previous"]["response"],
            fixture["not_before_ms"],
        )
        verify_adjacent_pulses(fixture["previous"]["response"], fixture["anchor"]["response"])
        target_ms = anchor["structural"]["timestamp_ms"] + 86_400_000
        target_response, target_attempt_audit = _validate_target_attempts(fixture["target_attempts"], target_ms=target_ms)
        normative_chain = verify_normative_chain(
            [fixture["anchor"], *chain_bundles],
            root_certificate_pem=root_pem,
            trust_bundle=trust,
            trusted_trust_bundle_sha256=trusted_trust_bundle_sha256,
        )
        final_response = chain_bundles[-1]["response"]
        if canonical_json_bytes(final_response) != canonical_json_bytes(target_response):
            _fail("TARGET_CHAIN_FINAL_RESPONSE_MISMATCH")
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
            "anchor_to_target_chain_pulse_count": 1440,
            "anchor_to_target_chain_verification_summary_sha256": hashlib.sha256(
                canonical_json_bytes(normative_chain)
            ).hexdigest(),
            "every_intermediate_signature_and_output_verified": True,
            "every_adjacent_previous_and_precommitment_link_verified": True,
        }

    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.nistir_normative_offline_selection_rehearsal_receipt.v1",
        "status": "PASS__OFFLINE_NISTIR_VERIFIED_SYNTHETIC_SELECTION_MAPPING_REHEARSAL__NOT_SCIENTIFIC_SELECTION",
        "synthetic_fixture_only": True,
        "live_nist_acceptance_usable": False,
        "scientific_selection_made": False,
        "source_interpretation_boundary": source_interpretation_boundary(),
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
        domain="rtdl.goal5793.x2.nistir_normative_offline_selection_rehearsal_receipt",
        version=1,
    )
    return receipt
