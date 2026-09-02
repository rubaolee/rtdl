#!/usr/bin/env python3
"""Select the Goal5838 challenge from one exact future NIST pulse."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import tempfile
from typing import Any, Mapping
import urllib.request

from scripts.goal5838_freeze_generic_core import (
    CALIBRATION_CERTIFICATE_PATH,
    CALIBRATION_PATH,
    OUT_DIR,
    PINNED_CERTIFICATE_ID,
    PREVIOUS_PULSE_URI,
    SEAL_PATH,
    TABLE_PATH,
    TARGET_PULSE_URI,
    TARGET_TIMESTAMP_MS,
    Goal5838SealError,
    canonical_json_bytes,
    pretty_json_bytes,
    seal_document,
    sha256_bytes,
    verify_stored as verify_core_seal,
)


SELECTION_PATH = OUT_DIR / "CHALLENGE_SELECTION_RESULT.json"
TARGET_RAW_PATH = OUT_DIR / "NIST_TARGET_PULSE.json"
PREVIOUS_RAW_PATH = OUT_DIR / "NIST_PREVIOUS_PULSE.json"
CERTIFICATE_PATH = OUT_DIR / "NIST_TARGET_CERTIFICATE.pem"
_DOMAIN = b"rtdl.goal5838.nist_challenge_selection.v1\0"
CALIBRATION_TIMESTAMP_MS = 1_788_372_600_000
CALIBRATION_PULSE_URI = (
    "https://beacon.nist.gov/beacon/2.0/pulse/time/1788372600000"
)


class Goal5838SelectionError(RuntimeError):
    pass


def _hex_bytes(value: object, expected_bytes: int, label: str) -> bytes:
    if not isinstance(value, str) or len(value) != expected_bytes * 2:
        raise Goal5838SelectionError(f"{label} must be {expected_bytes} bytes of hex")
    try:
        payload = bytes.fromhex(value)
    except ValueError as exc:
        raise Goal5838SelectionError(f"{label} is not hex") from exc
    return payload


def _u32(value: object, label: str) -> bytes:
    if type(value) is not int or not 0 <= value < 1 << 32:
        raise Goal5838SelectionError(f"{label} is not u32")
    return value.to_bytes(4, "big")


def _u64(value: object, label: str) -> bytes:
    if type(value) is not int or not 0 <= value < 1 << 64:
        raise Goal5838SelectionError(f"{label} is not u64")
    return value.to_bytes(8, "big")


def _length4(payload: bytes) -> bytes:
    if len(payload) >= 1 << 32:
        raise Goal5838SelectionError("serialized field too large")
    return len(payload).to_bytes(4, "big") + payload


def _text(value: object, label: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise Goal5838SelectionError(f"{label} is not text")
    return _length4(value.encode("utf-8"))


def _hash_value(value: object, label: str) -> bytes:
    return _length4(_hex_bytes(value, 64, label))


def serialize_live_nist_signed_fields(pulse: Mapping[str, Any]) -> bytes:
    """Serialize the live Beacon 2.0 cipher-suite-0 F1..F19 fields.

    The running service uses four-byte non-integer length prefixes and a
    four-byte external status. This variant is frozen before the target pulse.
    """

    required = {
        "uri", "version", "cipherSuite", "period", "certificateId",
        "chainIndex", "pulseIndex", "timeStamp", "localRandomValue",
        "external", "listValues", "precommitmentValue", "statusCode",
        "signatureValue", "outputValue",
    }
    if set(pulse) != required:
        raise Goal5838SelectionError("pulse field set mismatch")
    external = pulse["external"]
    if not isinstance(external, Mapping) or set(external) != {"sourceId", "statusCode", "value"}:
        raise Goal5838SelectionError("external field set mismatch")
    list_values = pulse["listValues"]
    expected_types = ("previous", "hour", "day", "month", "year")
    if not isinstance(list_values, list) or len(list_values) != len(expected_types):
        raise Goal5838SelectionError("listValues field set mismatch")
    for expected, item in zip(expected_types, list_values, strict=True):
        if not isinstance(item, Mapping) or set(item) != {"uri", "type", "value"}:
            raise Goal5838SelectionError("listValues row mismatch")
        if item["type"] != expected:
            raise Goal5838SelectionError("listValues order mismatch")
    return b"".join(
        [
            _text(pulse["uri"], "uri"),
            _text(pulse["version"], "version"),
            _u32(pulse["cipherSuite"], "cipherSuite"),
            _u32(pulse["period"], "period"),
            _hash_value(pulse["certificateId"], "certificateId"),
            _u64(pulse["chainIndex"], "chainIndex"),
            _u64(pulse["pulseIndex"], "pulseIndex"),
            _text(pulse["timeStamp"], "timeStamp"),
            _hash_value(pulse["localRandomValue"], "localRandomValue"),
            _hash_value(external["sourceId"], "external.sourceId"),
            _u32(external["statusCode"], "external.statusCode"),
            _hash_value(external["value"], "external.value"),
            *[
                _hash_value(item["value"], f"listValues.{item['type']}")
                for item in list_values
            ],
            _hash_value(pulse["precommitmentValue"], "precommitmentValue"),
            _u32(pulse["statusCode"], "statusCode"),
        ]
    )


def _openssl_verify_signature(
    certificate_pem: bytes,
    signed_fields: bytes,
    signature: bytes,
) -> None:
    with tempfile.TemporaryDirectory(prefix="goal5838-nist-") as directory:
        root = Path(directory)
        cert_path = root / "certificate.pem"
        pubkey_path = root / "public.pem"
        message_path = root / "message.bin"
        signature_path = root / "signature.bin"
        cert_path.write_bytes(certificate_pem)
        message_path.write_bytes(signed_fields)
        signature_path.write_bytes(signature)
        public = subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-pubkey", "-noout"],
            check=True,
            capture_output=True,
        )
        pubkey_path.write_bytes(public.stdout)
        verified = subprocess.run(
            [
                "openssl", "dgst", "-sha512", "-verify", str(pubkey_path),
                "-signature", str(signature_path), str(message_path),
            ],
            capture_output=True,
            text=True,
        )
        if verified.returncode != 0 or "Verified OK" not in verified.stdout:
            raise Goal5838SelectionError("NIST pulse signature verification failed")


def _parse_timestamp_ms(value: object) -> int:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise Goal5838SelectionError("invalid pulse timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise Goal5838SelectionError("invalid pulse timestamp") from exc
    return int(parsed.timestamp() * 1000)


def verify_signed_pulse(
    response: Mapping[str, Any],
    certificate_pem: bytes,
    *,
    expected_timestamp_ms: int,
) -> dict[str, Any]:
    if set(response) != {"pulse"} or not isinstance(response["pulse"], Mapping):
        raise Goal5838SelectionError("NIST response schema mismatch")
    pulse = response["pulse"]
    if _parse_timestamp_ms(pulse.get("timeStamp")) != expected_timestamp_ms:
        raise Goal5838SelectionError("next-closest or wrong timestamp rejected")
    if pulse.get("version") != "2.0" or pulse.get("cipherSuite") != 0:
        raise Goal5838SelectionError("unsupported NIST pulse version or cipher suite")
    if pulse.get("period") != 60_000 or pulse.get("statusCode") != 0:
        raise Goal5838SelectionError("NIST pulse status or period rejected")
    if str(pulse.get("certificateId", "")).lower() != PINNED_CERTIFICATE_ID:
        raise Goal5838SelectionError("target signing certificate changed")
    try:
        der_bytes = ssl.PEM_cert_to_DER_cert(certificate_pem.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Goal5838SelectionError("invalid NIST certificate PEM") from exc
    if not isinstance(der_bytes, bytes):
        raise Goal5838SelectionError("certificate conversion did not return DER bytes")
    if hashlib.sha512(der_bytes).hexdigest() != PINNED_CERTIFICATE_ID:
        raise Goal5838SelectionError("certificate DER identity mismatch")
    signed_fields = serialize_live_nist_signed_fields(pulse)
    signature = _hex_bytes(pulse.get("signatureValue"), 512, "signatureValue")
    _openssl_verify_signature(certificate_pem, signed_fields, signature)
    local_random = _hex_bytes(pulse.get("localRandomValue"), 64, "localRandomValue")
    _hex_bytes(pulse.get("outputValue"), 64, "outputValue")
    return {
        "chain_index": pulse["chainIndex"],
        "pulse_index": pulse["pulseIndex"],
        "timestamp_ms": expected_timestamp_ms,
        "certificate_id": PINNED_CERTIFICATE_ID,
        "certificate_der_sha256": sha256_bytes(der_bytes),
        "signed_fields_bytes": len(signed_fields),
        "signed_fields_sha512": hashlib.sha512(signed_fields).hexdigest(),
        "signature_sha256": sha256_bytes(signature),
        "signature_verified": True,
        "local_random_value": local_random.hex(),
        "output_value": str(pulse["outputValue"]).lower(),
    }


def verify_adjacent_precommitment(
    previous_response: Mapping[str, Any],
    target_response: Mapping[str, Any],
) -> None:
    previous = previous_response["pulse"]
    target = target_response["pulse"]
    if target["chainIndex"] != previous["chainIndex"]:
        raise Goal5838SelectionError("adjacent chain index mismatch")
    if target["pulseIndex"] != previous["pulseIndex"] + 1:
        raise Goal5838SelectionError("adjacent pulse index mismatch")
    if target["listValues"][0] != {
        "uri": previous["uri"],
        "type": "previous",
        "value": previous["outputValue"],
    }:
        raise Goal5838SelectionError("previous-output chain link mismatch")
    target_random = _hex_bytes(target["localRandomValue"], 64, "localRandomValue")
    expected = hashlib.sha512(target_random).hexdigest()
    if str(previous["precommitmentValue"]).lower() != expected:
        raise Goal5838SelectionError("target random value violates prior precommitment")


def select_index(
    *,
    table_sha256: str,
    core_seal_sha256: str,
    local_random_value: str,
    candidate_count: int,
) -> dict[str, Any]:
    if candidate_count <= 0:
        raise Goal5838SelectionError("candidate table is empty")
    fields = (
        table_sha256,
        core_seal_sha256,
        str(TARGET_TIMESTAMP_MS),
        TARGET_PULSE_URI,
        local_random_value.lower(),
    )
    limit = (1 << 256) - ((1 << 256) % candidate_count)
    for counter in range(1 << 32):
        framed = b"".join(
            len(field.encode("ascii")).to_bytes(8, "big") + field.encode("ascii")
            for field in (*fields, str(counter))
        )
        digest = hashlib.sha256(_DOMAIN + framed).digest()
        value = int.from_bytes(digest, "big")
        if value < limit:
            return {
                "counter": counter,
                "digest_sha256": digest.hex(),
                "rejection_limit_hex": f"{limit:064x}",
                "selected_index": value % candidate_count,
            }
    raise Goal5838SelectionError("rejection sampler exhausted")


def build_selection_result(
    table: Mapping[str, Any],
    seal: Mapping[str, Any],
    previous_response: Mapping[str, Any],
    target_response: Mapping[str, Any],
    certificate_pem: bytes,
) -> dict[str, Any]:
    previous = verify_signed_pulse(
        previous_response,
        certificate_pem,
        expected_timestamp_ms=TARGET_TIMESTAMP_MS - 60_000,
    )
    target = verify_signed_pulse(
        target_response,
        certificate_pem,
        expected_timestamp_ms=TARGET_TIMESTAMP_MS,
    )
    verify_adjacent_precommitment(previous_response, target_response)
    candidates = table["eligible_candidates"]
    mapping = select_index(
        table_sha256=table["challenge_table_sha256"],
        core_seal_sha256=seal["seal_sha256"],
        local_random_value=target["local_random_value"],
        candidate_count=len(candidates),
    )
    selected = candidates[mapping["selected_index"]]
    result: dict[str, Any] = {
        "schema": "rtdl.goal5838.challenge_selection_result.v1",
        "status": "PASS__INDEPENDENT_CHALLENGE_SELECTED__IMPLEMENTATION_NOT_STARTED",
        "challenge_table_sha256": table["challenge_table_sha256"],
        "generic_core_seal_sha256": seal["seal_sha256"],
        "target_timestamp_ms": TARGET_TIMESTAMP_MS,
        "target_pulse_uri": TARGET_PULSE_URI,
        "previous_pulse_uri": PREVIOUS_PULSE_URI,
        "transport": "HTTPS_WITH_PLATFORM_CA_VALIDATION",
        "certificate_identity_rule": "SHA512_OF_X509_DER__FROZEN_BEFORE_TARGET",
        "signed_field_serialization": (
            "LIVE_BEACON_2_CIPHER_SUITE_0__U32_LENGTHS_AND_EXTERNAL_STATUS__"
            "FROZEN_BEFORE_TARGET"
        ),
        "previous_pulse": previous,
        "target_pulse": target,
        "adjacent_previous_output_link_verified": True,
        "target_local_random_precommitment_verified": True,
        "entropy_field_used": "target.pulse.localRandomValue",
        "nist_output_value_used_for_selection": False,
        "mapping": mapping,
        "selected_candidate": selected,
        "activity_at_selection": {
            "candidate_implementation_count": 0,
            "candidate_execution_count": 0,
            "gpu_receipt_count": 0,
            "prospective_success_count": 0,
        },
        "claim_boundary": {
            "selection_is_not_implementation_success": True,
            "selection_is_not_gpu_evidence": True,
            "frozen_core_edit_after_selection_allowed": False,
            "ordinary_extension_bug_is_scientific_failure": False,
        },
        "selection_result_sha256": "",
    }
    result["selection_result_sha256"] = seal_document(
        result,
        "selection_result_sha256",
        "rtdl.goal5838.challenge_selection_result.v1",
    )
    return result


def _fetch(uri: str) -> bytes:
    request = urllib.request.Request(uri, headers={"User-Agent": "RTDL-Goal5838/1"})
    with urllib.request.urlopen(request, timeout=30, context=ssl.create_default_context()) as response:
        if response.status != 200:
            raise Goal5838SelectionError(f"HTTP {response.status}: {uri}")
        return response.read()


def write_live_calibration() -> dict[str, Any]:
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    if now_ms >= TARGET_TIMESTAMP_MS:
        raise Goal5838SelectionError("pretarget calibration attempted after target")
    if CALIBRATION_PATH.exists() or CALIBRATION_CERTIFICATE_PATH.exists():
        raise Goal5838SelectionError("pretarget calibration already exists")
    response_bytes = _fetch(CALIBRATION_PULSE_URI)
    certificate_uri = (
        "https://beacon.nist.gov/beacon/2.0/certificate/" + PINNED_CERTIFICATE_ID
    )
    certificate_pem = _fetch(certificate_uri)
    response = json.loads(response_bytes)
    verification = verify_signed_pulse(
        response,
        certificate_pem,
        expected_timestamp_ms=CALIBRATION_TIMESTAMP_MS,
    )
    calibration: dict[str, Any] = {
        "schema": "rtdl.goal5838.nist_pretarget_calibration.v1",
        "status": "PASS__LIVE_SIGNATURE_SERIALIZATION_CALIBRATED_BEFORE_TARGET",
        "calibration_pulse_uri": CALIBRATION_PULSE_URI,
        "calibration_timestamp_ms": CALIBRATION_TIMESTAMP_MS,
        "target_timestamp_ms": TARGET_TIMESTAMP_MS,
        "calibration_precedes_target": True,
        "transport": "HTTPS_WITH_PLATFORM_CA_VALIDATION",
        "certificate_sha256": sha256_bytes(certificate_pem),
        "verification": verification,
        "raw_response": response,
        "selection_made": False,
        "entropy_used": False,
        "calibration_sha256": "",
    }
    calibration["calibration_sha256"] = seal_document(
        calibration,
        "calibration_sha256",
        "rtdl.goal5838.nist_pretarget_calibration.v1",
    )
    CALIBRATION_CERTIFICATE_PATH.write_bytes(certificate_pem)
    CALIBRATION_PATH.write_bytes(pretty_json_bytes(calibration))
    return calibration


def verify_stored_calibration() -> dict[str, Any]:
    calibration = json.loads(CALIBRATION_PATH.read_text(encoding="ascii"))
    certificate_pem = CALIBRATION_CERTIFICATE_PATH.read_bytes()
    if calibration.get("calibration_sha256") != seal_document(
        calibration,
        "calibration_sha256",
        "rtdl.goal5838.nist_pretarget_calibration.v1",
    ):
        raise Goal5838SelectionError("pretarget calibration seal mismatch")
    if calibration.get("certificate_sha256") != sha256_bytes(certificate_pem):
        raise Goal5838SelectionError("pretarget certificate hash mismatch")
    rebuilt = verify_signed_pulse(
        calibration["raw_response"],
        certificate_pem,
        expected_timestamp_ms=CALIBRATION_TIMESTAMP_MS,
    )
    if canonical_json_bytes(rebuilt) != canonical_json_bytes(calibration["verification"]):
        raise Goal5838SelectionError("pretarget calibration verification drift")
    return {
        "status": "PASS__GOAL5838_PRETARGET_CALIBRATION_VERIFIED",
        "calibration_sha256": calibration["calibration_sha256"],
        "selection_made": False,
    }


def write_live_selection() -> dict[str, Any]:
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    if now_ms < TARGET_TIMESTAMP_MS:
        raise Goal5838SelectionError("target pulse is still in the future")
    verify_core_seal()
    verify_stored_calibration()
    if any(path.exists() for path in (SELECTION_PATH, TARGET_RAW_PATH, PREVIOUS_RAW_PATH, CERTIFICATE_PATH)):
        raise Goal5838SelectionError("selection evidence already exists; overwrite forbidden")
    table = json.loads(TABLE_PATH.read_text(encoding="ascii"))
    seal = json.loads(SEAL_PATH.read_text(encoding="ascii"))
    previous_bytes = _fetch(PREVIOUS_PULSE_URI)
    target_bytes = _fetch(TARGET_PULSE_URI)
    certificate_uri = (
        "https://beacon.nist.gov/beacon/2.0/certificate/" + PINNED_CERTIFICATE_ID
    )
    certificate_pem = _fetch(certificate_uri)
    previous_response = json.loads(previous_bytes)
    target_response = json.loads(target_bytes)
    result = build_selection_result(
        table, seal, previous_response, target_response, certificate_pem
    )
    PREVIOUS_RAW_PATH.write_bytes(pretty_json_bytes(previous_response))
    TARGET_RAW_PATH.write_bytes(pretty_json_bytes(target_response))
    CERTIFICATE_PATH.write_bytes(certificate_pem)
    SELECTION_PATH.write_bytes(pretty_json_bytes(result))
    return result


def verify_stored_selection() -> dict[str, Any]:
    verify_core_seal()
    verify_stored_calibration()
    table = json.loads(TABLE_PATH.read_text(encoding="ascii"))
    seal = json.loads(SEAL_PATH.read_text(encoding="ascii"))
    previous = json.loads(PREVIOUS_RAW_PATH.read_text(encoding="ascii"))
    target = json.loads(TARGET_RAW_PATH.read_text(encoding="ascii"))
    certificate = CERTIFICATE_PATH.read_bytes()
    stored = json.loads(SELECTION_PATH.read_text(encoding="ascii"))
    rebuilt = build_selection_result(table, seal, previous, target, certificate)
    if canonical_json_bytes(stored) != canonical_json_bytes(rebuilt):
        raise Goal5838SelectionError("stored selection result drift")
    return {
        "status": "PASS__GOAL5838_STORED_SELECTION_VERIFIED",
        "selection_result_sha256": stored["selection_result_sha256"],
        "selected_candidate_id": stored["selected_candidate"]["candidate_id"],
        "frozen_core_byte_changes": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-live-calibration", action="store_true")
    group.add_argument("--verify-calibration", action="store_true")
    group.add_argument("--write-live-selection", action="store_true")
    group.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_live_calibration:
        result = write_live_calibration()
    elif args.verify_calibration:
        result = verify_stored_calibration()
    elif args.write_live_selection:
        result = write_live_selection()
    else:
        result = verify_stored_selection()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
