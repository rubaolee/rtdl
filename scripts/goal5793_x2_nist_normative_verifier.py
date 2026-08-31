#!/usr/bin/env python3
"""Offline NISTIR 8213 cipherSuite-0 pulse verification for Goal5793 X2.

This module implements the byte serialization, SHA-512, RSA-PKCS1-v1_5,
certificate-identifier, output-value, previous-output, and precommitment rules
from the exact recovered NISTIR 8213 draft.  The companion Beacon 2.0 XSD is
used only as a transport/schema authority because three of its documentation
sentences conflict with the NISTIR algorithms.  Those conflicts are exposed by
``source_interpretation_boundary`` and are never silently resolved after a
real pulse is observed.

The verifier is offline.  It contains no HTTP client, beacon request, entropy,
selection, candidate, GPU, SSH, POD, or timing path.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import ExtensionOID

from scripts.goal5793_x1_canonical import seal_document, sha256_bytes
from scripts.goal5793_x2_offline_core import X2Error, validate_pulse_structure


NIST_IR_REL = (
    "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/"
    "NIST.IR.8213-draft.pdf"
)
NIST_XSD_REL = (
    "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/"
    "beacon-2.0.xsd"
)
NIST_IR_BYTES = 762_001
NIST_IR_SHA256 = "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183"
NIST_XSD_BYTES = 19_033
NIST_XSD_SHA256 = "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6"

TRUST_BUNDLE_DOMAIN = "rtdl.goal5793.x2.nist_cipher_suite_0.synthetic_trust_bundle"
RECEIPT_DOMAIN = "rtdl.goal5793.x2.nist_cipher_suite_0.offline_verification_receipt"
LIST_VALUE_ORDER = ("previous", "hour", "day", "month", "year")


def _fail(reason: str) -> None:
    raise X2Error(reason)


def _exact_keys(value: Mapping[str, Any], keys: Sequence[str], reason: str) -> None:
    if set(value) != set(keys):
        _fail(reason)


def _plain_uint(value: Any, bits: int, reason: str) -> int:
    if type(value) is not int or value < 0 or value >= 1 << bits:
        _fail(reason)
    return value


def _utf8(value: Any, reason: str) -> bytes:
    if not isinstance(value, str) or not value:
        _fail(reason)
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise X2Error(reason) from exc


def _hex_bytes(value: Any, expected_bytes: int | None, reason: str) -> bytes:
    if not isinstance(value, str) or not value or len(value) % 2:
        _fail(reason)
    try:
        decoded = bytes.fromhex(value)
    except ValueError as exc:
        raise X2Error(reason) from exc
    if expected_bytes is not None and len(decoded) != expected_bytes:
        _fail(reason)
    return decoded


def _u32(value: Any, reason: str) -> bytes:
    return _plain_uint(value, 32, reason).to_bytes(4, "big")


def _u64(value: Any, reason: str) -> bytes:
    return _plain_uint(value, 64, reason).to_bytes(8, "big")


def _length_prefixed(payload: bytes) -> bytes:
    # NISTIR 8213 §4.1.2, BytLen: uint64 big-endian byte length.
    return len(payload).to_bytes(8, "big") + payload


def _string(value: Any, reason: str) -> bytes:
    return _length_prefixed(_utf8(value, reason))


def _hash_value(value: Any, reason: str) -> bytes:
    return _length_prefixed(_hex_bytes(value, 64, reason))


def assert_normative_source_identity(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    rows = []
    for rel, expected_bytes, expected_sha in (
        (NIST_IR_REL, NIST_IR_BYTES, NIST_IR_SHA256),
        (NIST_XSD_REL, NIST_XSD_BYTES, NIST_XSD_SHA256),
    ):
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            _fail("NIST_NORMATIVE_SOURCE_PATH_ESCAPE")
        # Keep the logical path.  ``history`` is an explicitly controlled
        # workspace junction on this Windows host; resolving the final target
        # would incorrectly classify that known junction as a path escape.
        path = root / rel_path
        payload = path.read_bytes()
        observed_sha = sha256_bytes(payload)
        if len(payload) != expected_bytes or observed_sha != expected_sha:
            _fail("NIST_NORMATIVE_SOURCE_IDENTITY_MISMATCH")
        rows.append({"path": rel, "bytes": len(payload), "sha256": observed_sha})
    return {"status": "EXACT_RECOVERED_NORMATIVE_SOURCE_BYTES_MATCH", "files": rows}


def source_interpretation_boundary() -> dict[str, Any]:
    """Return the frozen, reviewer-visible resolution of source conflicts."""

    return {
        "controlling_cryptographic_serialization": (
            "NISTIR_8213_DRAFT_SECTIONS_4_1_2_4_2_3_4_8_1_4_8_2_4_9_"
            "ALGORITHMS_1_2_EQUATIONS_4_TO_8_AND_14_TO_18"
        ),
        "xsd_scope": "TRANSPORT_STRUCTURE_AND_FIELD_LEXICAL_CONSTRAINTS_ONLY",
        "conflicts": [
            {
                "axis": "noninteger_length_prefix",
                "nistir": "uint64_big_endian_8_bytes",
                "xsd_documentation": "uint32_big_endian_4_bytes",
                "resolution": "NISTIR_CONTROLS_CRYPTOGRAPHIC_PREIMAGE",
            },
            {
                "axis": "external_statusCode_serialization",
                "nistir": "uint64_big_endian_8_bytes",
                "xsd_documentation": "uint32_big_endian_4_bytes",
                "resolution": "NISTIR_CONTROLS_CRYPTOGRAPHIC_PREIMAGE",
            },
            {
                "axis": "certificate_identifier_preimage",
                "nistir": "SHA512_OF_EXACT_RETURNED_PEM_FILE_BYTES",
                "xsd_documentation": "SHA512_OF_X509_ASN1_DER_BYTES",
                "resolution": "NISTIR_CONTROLS_AND_DER_ONLY_MATCH_IS_REJECTED",
            },
        ],
        "source_conflict_hidden": False,
        "post_observation_variant_choice_allowed": False,
        "live_beacon_request_authorized": False,
        "entropy_or_selection_authorized": False,
    }


def _ordered_list_values(pulse: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    values = pulse.get("listValues")
    if not isinstance(values, list) or len(values) != len(LIST_VALUE_ORDER):
        _fail("NISTIR_LIST_VALUE_SET_INVALID")
    result: list[Mapping[str, Any]] = []
    for expected_type, value in zip(LIST_VALUE_ORDER, values, strict=True):
        if not isinstance(value, Mapping):
            _fail("NISTIR_LIST_VALUE_SET_INVALID")
        _exact_keys(value, ("uri", "type", "value"), "NISTIR_LIST_VALUE_SET_INVALID")
        if value.get("type") != expected_type:
            _fail("NISTIR_LIST_VALUE_ORDER_INVALID")
        _utf8(value.get("uri"), "NISTIR_LIST_VALUE_URI_INVALID")
        _hex_bytes(value.get("value"), 64, "NISTIR_LIST_VALUE_HEX_INVALID")
        result.append(value)
    return result


def serialize_signed_fields(pulse: Mapping[str, Any]) -> bytes:
    """Serialize pulse fields F1..F19 using NISTIR 8213 Algorithm 2."""

    # Reuse the separately implemented S0 response-shape parser first.
    structural = validate_pulse_structure({"pulse": dict(pulse)})
    raw = structural["raw_pulse"]
    values = _ordered_list_values(raw)
    external = raw["external"]
    parts = [
        _string(raw["uri"], "NISTIR_URI_INVALID"),
        _string(raw["version"], "NISTIR_VERSION_INVALID"),
        _u32(raw["cipherSuite"], "NISTIR_CIPHER_SUITE_INVALID"),
        _u32(raw["period"], "NISTIR_PERIOD_INVALID"),
        _hash_value(raw["certificateId"], "NISTIR_CERTIFICATE_ID_INVALID"),
        _u64(raw["chainIndex"], "NISTIR_CHAIN_INDEX_INVALID"),
        _u64(raw["pulseIndex"], "NISTIR_PULSE_INDEX_INVALID"),
        _string(raw["timeStamp"], "NISTIR_TIMESTAMP_INVALID"),
        _hash_value(raw["localRandomValue"], "NISTIR_LOCAL_RANDOM_INVALID"),
        _hash_value(external["sourceId"], "NISTIR_EXTERNAL_SOURCE_INVALID"),
        _u64(external["statusCode"], "NISTIR_EXTERNAL_STATUS_INVALID"),
        _hash_value(external["value"], "NISTIR_EXTERNAL_VALUE_INVALID"),
    ]
    parts.extend(_hash_value(value["value"], "NISTIR_LIST_VALUE_HEX_INVALID") for value in values)
    parts.extend(
        [
            _hash_value(raw["precommitmentValue"], "NISTIR_PRECOMMITMENT_INVALID"),
            _u32(raw["statusCode"], "NISTIR_STATUS_INVALID"),
        ]
    )
    return b"".join(parts)


def serialize_output_preimage(pulse: Mapping[str, Any]) -> bytes:
    signed = serialize_signed_fields(pulse)
    signature = _hex_bytes(pulse.get("signatureValue"), None, "NISTIR_SIGNATURE_ENCODING_INVALID")
    return signed + _length_prefixed(signature)


def recompute_output_value(pulse: Mapping[str, Any]) -> str:
    return hashlib.sha512(serialize_output_preimage(pulse)).hexdigest()


def serialization_known_answer() -> dict[str, Any]:
    """Return a fixed source-independent NISTIR Algorithm-2 KAT."""

    previous_uri = "https://synthetic.invalid/chain/2/pulse/0"
    pulse = {
        "uri": "https://synthetic.invalid/chain/2/pulse/100",
        "version": "2.0",
        "cipherSuite": 0,
        "period": 60000,
        "certificateId": "55" * 64,
        "chainIndex": 2,
        "pulseIndex": 100,
        "timeStamp": "2027-01-01T00:00:00.000Z",
        "localRandomValue": "11" * 64,
        "external": {"sourceId": "33" * 64, "statusCode": 0, "value": "44" * 64},
        "listValues": [
            {"uri": previous_uri, "type": kind, "value": "00" * 64}
            for kind in LIST_VALUE_ORDER
        ],
        "precommitmentValue": hashlib.sha512(bytes([0x22]) * 64).hexdigest(),
        "statusCode": 0,
        "signatureValue": "00" * 256,
        "outputValue": "00" * 64,
    }
    serialized = serialize_signed_fields(pulse)
    return {
        "kat_id": "goal5793-x2-nistir8213-algorithm2-cipher0-v1",
        "pulse": pulse,
        "serialized_bytes": len(serialized),
        "serialized_sha512": hashlib.sha512(serialized).hexdigest(),
        "expected_serialized_bytes": 850,
        "expected_serialized_sha512": "9ffc956e1ed81385c949d8a6ed6066f633b3006dd5d525a89636011d01381ecec88e7718bf3d34d6caacb0e17424f8d931ba1365ed175500f429e32eccff9ae5",
        "matches_expected": len(serialized) == 850
        and hashlib.sha512(serialized).hexdigest()
        == "9ffc956e1ed81385c949d8a6ed6066f633b3006dd5d525a89636011d01381ecec88e7718bf3d34d6caacb0e17424f8d931ba1365ed175500f429e32eccff9ae5",
    }


def pem_certificate_id(certificate_pem: bytes) -> str:
    if not isinstance(certificate_pem, bytes) or not certificate_pem:
        _fail("NISTIR_CERTIFICATE_PEM_INVALID")
    try:
        x509.load_pem_x509_certificate(certificate_pem)
    except ValueError as exc:
        raise X2Error("NISTIR_CERTIFICATE_PEM_INVALID") from exc
    return hashlib.sha512(certificate_pem).hexdigest()


def der_certificate_id(certificate_pem: bytes) -> str:
    certificate = x509.load_pem_x509_certificate(certificate_pem)
    return hashlib.sha512(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()


def build_synthetic_trust_bundle(root_certificate_pem: bytes) -> dict[str, Any]:
    """Build an exact synthetic-only trust authority for offline tests."""

    try:
        root = x509.load_pem_x509_certificate(root_certificate_pem)
    except ValueError as exc:
        raise X2Error("NISTIR_TRUST_ROOT_PARSE_INVALID") from exc
    root_key = root.public_key()
    if not isinstance(root_key, rsa.RSAPublicKey):
        _fail("NISTIR_TRUST_ROOT_ALGORITHM_INVALID")
    authority: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.nist_cipher_suite_0.synthetic_trust_bundle.v1",
        "status": "SYNTHETIC_ONLY__EXACT_OFFLINE_KAT_TRUST_ROOT__NOT_LIVE_NIST_AUTHORITY",
        "normative_sources": [
            {"path": NIST_IR_REL, "bytes": NIST_IR_BYTES, "sha256": NIST_IR_SHA256},
            {"path": NIST_XSD_REL, "bytes": NIST_XSD_BYTES, "sha256": NIST_XSD_SHA256},
        ],
        "source_interpretation_boundary": source_interpretation_boundary(),
        "path_policy": {
            "algorithm": "EXACT_TWO_CERT_PATH__LEAF_SIGNED_DIRECTLY_BY_ONE_PINNED_SELF_SIGNED_ROOT",
            "allowed_pulse_cipher_suite": 0,
            "allowed_leaf_public_key": "RSA_AT_LEAST_2048_BITS",
            "allowed_pulse_signature": "RSASSA_PKCS1_V1_5_WITH_SHA512",
            "root_basic_constraints_ca_required": True,
            "root_key_cert_sign_required": True,
            "leaf_basic_constraints_ca_required": False,
            "leaf_digital_signature_required": True,
            "leaf_valid_at_pulse_time_required": True,
            "ambiguous_or_longer_path_allowed": False,
        },
        "root": {
            "pem_bytes": len(root_certificate_pem),
            "pem_sha256": sha256_bytes(root_certificate_pem),
            "der_sha256": sha256_bytes(root.public_bytes(serialization.Encoding.DER)),
            "subject_rfc4514": root.subject.rfc4514_string(),
            "issuer_rfc4514": root.issuer.rfc4514_string(),
            "rsa_modulus_bits": root_key.key_size,
            "certificate_signature_oid": root.signature_algorithm_oid.dotted_string,
        },
        "activity": {
            "live_search_calls": 0,
            "beacon_calls": 0,
            "entropy_draws": 0,
            "selections": 0,
            "candidate_actions": 0,
            "gpu_ssh_pod_actions": 0,
            "registered_or_performance_timings": 0,
        },
        "authorization": {
            "live_nist": False,
            "search": False,
            "beacon": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "publication": False,
        },
        "trust_bundle_sha256": "",
    }
    authority["trust_bundle_sha256"] = seal_document(
        authority,
        seal_field="trust_bundle_sha256",
        domain=TRUST_BUNDLE_DOMAIN,
        version=1,
    )
    return authority


def _extension(certificate: x509.Certificate, oid: x509.ObjectIdentifier, reason: str) -> Any:
    try:
        return certificate.extensions.get_extension_for_oid(oid).value
    except x509.ExtensionNotFound as exc:
        raise X2Error(reason) from exc


def _verify_cert_signature(certificate: x509.Certificate, issuer_key: rsa.RSAPublicKey) -> None:
    try:
        issuer_key.verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm,
        )
    except InvalidSignature as exc:
        raise X2Error("NISTIR_CERTIFICATE_SIGNATURE_INVALID") from exc


def _verify_trust_path(
    leaf_pem: bytes,
    root_pem: bytes,
    trust_bundle: Mapping[str, Any],
    trusted_trust_bundle_sha256: str,
    pulse_time: datetime,
) -> tuple[x509.Certificate, x509.Certificate]:
    recomputed_bundle_sha = seal_document(
        trust_bundle,
        seal_field="trust_bundle_sha256",
        domain=TRUST_BUNDLE_DOMAIN,
        version=1,
    )
    if trust_bundle.get("trust_bundle_sha256") != recomputed_bundle_sha:
        _fail("NISTIR_TRUST_BUNDLE_SEAL_MISMATCH")
    if (
        not isinstance(trusted_trust_bundle_sha256, str)
        or len(trusted_trust_bundle_sha256) != 64
        or trusted_trust_bundle_sha256 != recomputed_bundle_sha
    ):
        _fail("NISTIR_OUT_OF_BAND_TRUST_BUNDLE_PIN_MISMATCH")
    if trust_bundle.get("schema") != "rtdl.goal5793.x2.nist_cipher_suite_0.synthetic_trust_bundle.v1":
        _fail("NISTIR_TRUST_BUNDLE_SCHEMA_INVALID")
    if trust_bundle.get("status") != "SYNTHETIC_ONLY__EXACT_OFFLINE_KAT_TRUST_ROOT__NOT_LIVE_NIST_AUTHORITY":
        _fail("NISTIR_TRUST_BUNDLE_SCOPE_INVALID")
    if any(trust_bundle.get("authorization", {}).values()):
        _fail("NISTIR_TRUST_BUNDLE_AUTHORIZATION_ESCALATION")
    try:
        leaf = x509.load_pem_x509_certificate(leaf_pem)
        root = x509.load_pem_x509_certificate(root_pem)
    except ValueError as exc:
        raise X2Error("NISTIR_CERTIFICATE_PARSE_INVALID") from exc
    if sha256_bytes(root_pem) != trust_bundle.get("root", {}).get("pem_sha256"):
        _fail("NISTIR_TRUST_ROOT_PEM_PIN_MISMATCH")
    root_der = root.public_bytes(serialization.Encoding.DER)
    if sha256_bytes(root_der) != trust_bundle.get("root", {}).get("der_sha256"):
        _fail("NISTIR_TRUST_ROOT_DER_PIN_MISMATCH")
    root_key = root.public_key()
    leaf_key = leaf.public_key()
    if not isinstance(root_key, rsa.RSAPublicKey) or not isinstance(leaf_key, rsa.RSAPublicKey):
        _fail("NISTIR_CERTIFICATE_PUBLIC_KEY_ALGORITHM_INVALID")
    if root_key.key_size < 2048 or leaf_key.key_size < 2048:
        _fail("NISTIR_CERTIFICATE_RSA_MODULUS_TOO_SMALL")
    if root.subject != root.issuer or leaf.issuer != root.subject:
        _fail("NISTIR_CERTIFICATE_PATH_INVALID")
    root_bc = _extension(root, ExtensionOID.BASIC_CONSTRAINTS, "NISTIR_ROOT_BASIC_CONSTRAINTS_INVALID")
    root_ku = _extension(root, ExtensionOID.KEY_USAGE, "NISTIR_ROOT_KEY_USAGE_INVALID")
    leaf_bc = _extension(leaf, ExtensionOID.BASIC_CONSTRAINTS, "NISTIR_LEAF_BASIC_CONSTRAINTS_INVALID")
    leaf_ku = _extension(leaf, ExtensionOID.KEY_USAGE, "NISTIR_LEAF_KEY_USAGE_INVALID")
    if not root_bc.ca or not root_ku.key_cert_sign:
        _fail("NISTIR_ROOT_CA_POLICY_INVALID")
    if leaf_bc.ca or not leaf_ku.digital_signature:
        _fail("NISTIR_LEAF_KEY_USAGE_INVALID")
    _verify_cert_signature(root, root_key)
    _verify_cert_signature(leaf, root_key)
    if not (root.not_valid_before_utc <= pulse_time <= root.not_valid_after_utc):
        _fail("NISTIR_ROOT_CERTIFICATE_TIME_INVALID")
    if not (leaf.not_valid_before_utc <= pulse_time <= leaf.not_valid_after_utc):
        _fail("NISTIR_LEAF_CERTIFICATE_TIME_INVALID")
    return leaf, root


def verify_normative_pulse(
    response: Mapping[str, Any],
    *,
    leaf_certificate_pem: bytes,
    root_certificate_pem: bytes,
    trust_bundle: Mapping[str, Any],
    trusted_trust_bundle_sha256: str,
) -> dict[str, Any]:
    """Verify one synthetic pulse under the exact NISTIR cipherSuite-0 rules."""

    structural = validate_pulse_structure(response)
    pulse = structural["raw_pulse"]
    if pulse["cipherSuite"] != 0:
        _fail("NISTIR_CIPHER_SUITE_UNSUPPORTED")
    pulse_time = datetime.fromtimestamp(structural["timestamp_ms"] / 1000, tz=timezone.utc)
    leaf, root = _verify_trust_path(
        leaf_certificate_pem,
        root_certificate_pem,
        trust_bundle,
        trusted_trust_bundle_sha256,
        pulse_time,
    )
    expected_pem_id = pem_certificate_id(leaf_certificate_pem)
    observed_id = pulse["certificateId"].lower()
    if observed_id != expected_pem_id:
        if observed_id == der_certificate_id(leaf_certificate_pem):
            _fail("NISTIR_CERTIFICATE_IDENTIFIER_MISMATCH__XSD_DER_VARIANT_NOT_ACCEPTED")
        _fail("NISTIR_CERTIFICATE_IDENTIFIER_MISMATCH")
    signature = _hex_bytes(pulse["signatureValue"], leaf.public_key().key_size // 8, "NISTIR_SIGNATURE_ENCODING_INVALID")
    signed_preimage = serialize_signed_fields(pulse)
    try:
        leaf.public_key().verify(signature, signed_preimage, padding.PKCS1v15(), hashes.SHA512())
    except InvalidSignature as exc:
        raise X2Error("NISTIR_PULSE_SIGNATURE_INVALID") from exc
    expected_output = hashlib.sha512(signed_preimage + _length_prefixed(signature)).hexdigest()
    if pulse["outputValue"].lower() != expected_output:
        _fail("NISTIR_OUTPUT_RECOMPUTATION_MISMATCH")
    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.nist_cipher_suite_0.offline_pulse_verification_receipt.v1",
        "status": "PASS__EXACT_NISTIR_8213_CIPHER_SUITE_0_OFFLINE_PULSE_VERIFICATION",
        "synthetic_fixture_only": True,
        "usable_for_live_nist_pulse_acceptance": False,
        "source_interpretation_boundary": source_interpretation_boundary(),
        "certificate": {
            "identifier_rule": "SHA512_OF_EXACT_RETURNED_PEM_FILE_BYTES",
            "certificate_id": expected_pem_id,
            "leaf_pem_sha256": sha256_bytes(leaf_certificate_pem),
            "leaf_der_sha256": sha256_bytes(leaf.public_bytes(serialization.Encoding.DER)),
            "root_pem_sha256": sha256_bytes(root_certificate_pem),
            "root_der_sha256": sha256_bytes(root.public_bytes(serialization.Encoding.DER)),
            "trust_path_verified": True,
            "valid_at_pulse_time": True,
        },
        "pulse": {
            "chain_index": structural["chain_index"],
            "pulse_index": structural["pulse_index"],
            "timestamp_ms": structural["timestamp_ms"],
            "output_value": expected_output,
            "signed_preimage_bytes": len(signed_preimage),
            "signed_preimage_sha512": hashlib.sha512(signed_preimage).hexdigest(),
            "signature_bytes": len(signature),
            "signature_verified": True,
            "output_recomputed": True,
        },
        "authorization": {
            "live_nist": False,
            "search": False,
            "beacon": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "publication": False,
        },
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = seal_document(
        receipt,
        seal_field="receipt_sha256",
        domain=RECEIPT_DOMAIN,
        version=1,
    )
    return receipt


def verify_adjacent_pulses(previous_response: Mapping[str, Any], current_response: Mapping[str, Any]) -> dict[str, Any]:
    """Verify previous-output and precommitment relations for adjacent pulses."""

    previous = validate_pulse_structure(previous_response)
    current = validate_pulse_structure(current_response)
    prev_raw = previous["raw_pulse"]
    cur_raw = current["raw_pulse"]
    if current["chain_index"] != previous["chain_index"]:
        _fail("NISTIR_ADJACENT_CHAIN_INDEX_MISMATCH")
    if current["pulse_index"] != previous["pulse_index"] + 1:
        _fail("NISTIR_ADJACENT_PULSE_INDEX_MISMATCH")
    if current["timestamp_ms"] != previous["timestamp_ms"] + prev_raw["period"]:
        _fail("NISTIR_ADJACENT_TIMESTAMP_MISMATCH")
    previous_values = _ordered_list_values(prev_raw)
    current_values = _ordered_list_values(cur_raw)
    _ = previous_values
    current_previous = current_values[0]
    if current_previous["value"].lower() != prev_raw["outputValue"].lower():
        _fail("NISTIR_PREVIOUS_OUTPUT_LINK_MISMATCH")
    if current_previous["uri"] != prev_raw["uri"]:
        _fail("NISTIR_PREVIOUS_URI_LINK_MISMATCH")
    expected_preimage = hashlib.sha512(bytes.fromhex(cur_raw["localRandomValue"])).hexdigest()
    if prev_raw["precommitmentValue"].lower() != expected_preimage:
        _fail("NISTIR_PRECOMMITMENT_LINK_MISMATCH")
    return {
        "status": "PASS__NISTIR_ADJACENT_PREVIOUS_OUTPUT_AND_PRECOMMITMENT_LINK",
        "chain_index": current["chain_index"],
        "previous_pulse_index": previous["pulse_index"],
        "current_pulse_index": current["pulse_index"],
        "previous_output_link_verified": True,
        "precommitment_link_verified": True,
    }


def verify_normative_chain(
    pulse_bundles: Sequence[Mapping[str, Any]],
    *,
    root_certificate_pem: bytes,
    trust_bundle: Mapping[str, Any],
    trusted_trust_bundle_sha256: str,
) -> dict[str, Any]:
    """Verify every pulse and every adjacent link in an offline synthetic chain."""

    if not isinstance(pulse_bundles, Sequence) or isinstance(pulse_bundles, (str, bytes)) or len(pulse_bundles) < 2:
        _fail("NISTIR_CHAIN_CARDINALITY_INVALID")
    receipts = []
    responses = []
    for bundle in pulse_bundles:
        if not isinstance(bundle, Mapping):
            _fail("NISTIR_CHAIN_BUNDLE_SCHEMA_INVALID")
        _exact_keys(bundle, ("response", "leaf_certificate_pem"), "NISTIR_CHAIN_BUNDLE_SCHEMA_INVALID")
        response = bundle["response"]
        leaf_pem = bundle["leaf_certificate_pem"]
        if not isinstance(response, Mapping) or not isinstance(leaf_pem, bytes):
            _fail("NISTIR_CHAIN_BUNDLE_SCHEMA_INVALID")
        receipts.append(
            verify_normative_pulse(
                response,
                leaf_certificate_pem=leaf_pem,
                root_certificate_pem=root_certificate_pem,
                trust_bundle=trust_bundle,
                trusted_trust_bundle_sha256=trusted_trust_bundle_sha256,
            )
        )
        responses.append(response)
    links = [verify_adjacent_pulses(left, right) for left, right in zip(responses, responses[1:])]
    return {
        "status": "PASS__ALL_NISTIR_PULSES_AND_ADJACENT_LINKS_VERIFIED",
        "pulse_count": len(receipts),
        "adjacent_link_count": len(links),
        "pulse_receipt_sha256": [receipt["receipt_sha256"] for receipt in receipts],
        "all_signatures_verified": True,
        "all_outputs_recomputed": True,
        "all_previous_links_verified": True,
        "all_precommitments_verified": True,
        "synthetic_fixture_only": True,
        "usable_for_live_nist_pulse_acceptance": False,
    }
