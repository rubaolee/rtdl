#!/usr/bin/env python3
"""Synthetic-only certificate/signature/output/chain harness for X2.

The harness exercises the exact failure boundaries required by S0 without
claiming that its test serialization is the normative NIST IR 8213 cipherSuite
0 serialization.  The production verifier remains blocked until the exact
pinned IR/XSD bytes are present and independently implemented.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x2_offline_core import X2Error, validate_pulse_structure


SYNTHETIC_DOMAIN = "rtdl.goal5793.x2.synthetic-pulse-signature-harness.v1"
SIGNED_FIELDS = (
    "uri",
    "version",
    "cipherSuite",
    "period",
    "certificateId",
    "chainIndex",
    "pulseIndex",
    "timeStamp",
    "localRandomValue",
    "external",
    "listValues",
    "precommitmentValue",
    "statusCode",
)


def certificate_id(certificate: x509.Certificate) -> str:
    return hashlib.sha512(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()


def signed_pulse_bytes(pulse: Mapping[str, Any]) -> bytes:
    if any(field not in pulse for field in SIGNED_FIELDS):
        raise X2Error("SYNTHETIC_SIGNED_FIELD_MISSING")
    projection = {field: pulse[field] for field in SIGNED_FIELDS}
    return SYNTHETIC_DOMAIN.encode("utf-8") + b"\0" + canonical_json_bytes(projection)


def synthetic_output_value(pulse: Mapping[str, Any], signature: bytes) -> str:
    return hashlib.sha512(signed_pulse_bytes(pulse) + b"\0" + signature).hexdigest()


def _verify_certificate_signature(certificate: x509.Certificate, issuer_public_key: rsa.RSAPublicKey) -> None:
    try:
        issuer_public_key.verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            certificate.signature_hash_algorithm,
        )
    except InvalidSignature as exc:
        raise X2Error("SYNTHETIC_CERTIFICATE_TRUST_PATH_INVALID") from exc


def verify_synthetic_pulse(
    response: Mapping[str, Any],
    *,
    leaf_certificate_pem: bytes,
    root_certificate_pem: bytes,
    trusted_root_sha256: str,
) -> dict[str, Any]:
    structural = validate_pulse_structure(response)
    pulse = structural["raw_pulse"]
    try:
        leaf = x509.load_pem_x509_certificate(leaf_certificate_pem)
        root = x509.load_pem_x509_certificate(root_certificate_pem)
    except ValueError as exc:
        raise X2Error("SYNTHETIC_CERTIFICATE_PARSE_INVALID") from exc
    root_der = root.public_bytes(serialization.Encoding.DER)
    if hashlib.sha256(root_der).hexdigest() != trusted_root_sha256:
        raise X2Error("SYNTHETIC_TRUST_ROOT_PIN_MISMATCH")
    if leaf.issuer != root.subject or root.issuer != root.subject:
        raise X2Error("SYNTHETIC_CERTIFICATE_TRUST_PATH_INVALID")
    root_key = root.public_key()
    leaf_key = leaf.public_key()
    if not isinstance(root_key, rsa.RSAPublicKey) or not isinstance(leaf_key, rsa.RSAPublicKey):
        raise X2Error("SYNTHETIC_CERTIFICATE_ALGORITHM_INVALID")
    _verify_certificate_signature(root, root_key)
    _verify_certificate_signature(leaf, root_key)
    pulse_time = datetime.fromtimestamp(structural["timestamp_ms"] / 1000, tz=timezone.utc)
    if not (leaf.not_valid_before_utc <= pulse_time <= leaf.not_valid_after_utc):
        raise X2Error("SYNTHETIC_CERTIFICATE_TIME_INVALID")
    try:
        key_usage = leaf.extensions.get_extension_for_class(x509.KeyUsage).value
    except x509.ExtensionNotFound as exc:
        raise X2Error("SYNTHETIC_CERTIFICATE_KEY_USAGE_INVALID") from exc
    if not key_usage.digital_signature:
        raise X2Error("SYNTHETIC_CERTIFICATE_KEY_USAGE_INVALID")
    if pulse["certificateId"].lower() != certificate_id(leaf):
        raise X2Error("SYNTHETIC_CERTIFICATE_IDENTIFIER_MISMATCH")
    try:
        signature = bytes.fromhex(pulse["signatureValue"])
    except (TypeError, ValueError) as exc:
        raise X2Error("SYNTHETIC_SIGNATURE_ENCODING_INVALID") from exc
    try:
        leaf_key.verify(signature, signed_pulse_bytes(pulse), padding.PKCS1v15(), hashes.SHA512())
    except InvalidSignature as exc:
        raise X2Error("SYNTHETIC_PULSE_SIGNATURE_INVALID") from exc
    expected_output = synthetic_output_value(pulse, signature)
    if pulse["outputValue"].lower() != expected_output:
        raise X2Error("SYNTHETIC_OUTPUT_RECOMPUTATION_MISMATCH")
    expected_precommitment = hashlib.sha512(bytes.fromhex(pulse["localRandomValue"])).hexdigest()
    if pulse["precommitmentValue"].lower() != expected_precommitment:
        raise X2Error("SYNTHETIC_PRECOMMITMENT_MISMATCH")
    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.synthetic_pulse_crypto_receipt.v1",
        "status": "SYNTHETIC_CERTIFICATE_SIGNATURE_OUTPUT_AND_PRECOMMITMENT_PASS",
        "synthetic_only": True,
        "nist_ir_8213_normative_serialization_claimed": False,
        "usable_for_live_nist_pulse_acceptance": False,
        "certificate": {
            "leaf_id_sha512": certificate_id(leaf),
            "leaf_der_sha256": hashlib.sha256(leaf.public_bytes(serialization.Encoding.DER)).hexdigest(),
            "root_der_sha256": hashlib.sha256(root_der).hexdigest(),
            "pulse_time_valid": True,
            "digital_signature_key_usage": True,
        },
        "pulse": {
            "chain_index": structural["chain_index"],
            "pulse_index": structural["pulse_index"],
            "timestamp_ms": structural["timestamp_ms"],
            "output_value": structural["output_value"],
            "signature_verified": True,
            "output_recomputed": True,
            "precommitment_verified": True,
        },
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = seal_document(
        receipt,
        seal_field="receipt_sha256",
        domain="rtdl.goal5793.x2.synthetic_pulse_crypto_receipt",
        version=1,
    )
    return receipt

