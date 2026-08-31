#!/usr/bin/env python3
"""Create one qualification-only TEST_ONLY trust root and pre-use custody.

This owner-local helper exists so a Home-Linux qualification cannot claim that
diagnostic signing happened merely because a hand-written JSON literal says it
did.  It creates a fresh keypair, performs exactly two domain-separated RSA
diagnostic signatures, verifies both with the public exponent, and then emits
the diagnostic and pre-use custody receipts.  It never creates a trust package
or head and never imports CUDA or runs a formal worker.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Mapping, NoReturn


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for import_root in (REPO_ROOT, SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from scripts import goal5801_rtdlexe_trust as trust  # noqa: E402


DIAGNOSTIC_SCHEMA = "rtdl.goal5802.qualification_trust_diagnostic.v1"
DIAGNOSTIC_STATUS = "PASS__EXACT_TWO_QUALIFICATION_ONLY_SIGNATURES_VERIFIED"
DIAGNOSTIC_MESSAGE_SCHEMA = (
    "rtdl.goal5802.qualification_trust_diagnostic_message.v1")
DIAGNOSTIC_PURPOSE = "QUALIFICATION_ONLY__NOT_TRUST_PACKAGE_OR_HEAD"
PREUSE_SCHEMA = "rtdl.goal5802.qualification_trust_key_custody_receipt.v1"
PREUSE_STATUS = (
    "TEST_ONLY_PRETARGET_CUSTODY_SNAPSHOT__ZERO_TRUST_SEQUENCE_MATERIALIZED")
QUALIFICATION_ONLY_KEY_PREFIX = (
    "TEST_ONLY_goal5802_final_home_qualification_")
QUALIFICATION_EXPECTED_TARGET_COMPUTE_CAPABILITY = [6, 1]
DIAGNOSTIC_DOMAIN = b"RTDL_GOAL5802_QUALIFICATION_KEY_DIAGNOSTIC_V1\0"
RSA_DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
RESERVED_MEASUREMENT_PRIVATE_SHA256 = (
    "3b8124dc238a88e38fdd6bd02d135d54fa9168f682f8af1888d85692fd9b715f")
RESERVED_MEASUREMENT_PUBLIC_SHA256 = (
    "3364f744a637e27710319001c2fa505bd6c54f75904b51429de253bcd4da8dc4")
RESERVED_MEASUREMENT_KEY_ID = (
    "TEST_ONLY_goal5802_rtx_measurement_root_v5_20260826")
RESERVED_MEASUREMENT_TRUST_ROOT_SHA256 = (
    "b7e6ba3a75f7602efe343683003faa99c20bc063c80b604d76465969b37cdd92")


class QualificationTrustError(RuntimeError):
    """Fail-closed qualification-key or custody error."""


def _fail(message: str) -> NoReturn:
    raise QualificationTrustError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest(value: object) -> str:
    return _sha(_canonical(value))


def _read_regular(path: Path, label: str) -> tuple[Path, bytes]:
    supplied = path.expanduser().absolute()
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    elif supplied.is_symlink():
        _fail(f"{label} may not be a symlink")
    descriptor = -1
    try:
        resolved = supplied.resolve(strict=True)
        descriptor = os.open(supplied, flags)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            _fail(f"{label} must be a regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            payload = stream.read()
        after = os.fstat(descriptor)
    except OSError as error:
        raise QualificationTrustError(f"{label} is unreadable") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if (before.st_dev, before.st_ino, before.st_mode, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev, after.st_ino, after.st_mode, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns) or len(payload) != before.st_size:
        _fail(f"{label} changed during its single read")
    if not payload:
        _fail(f"{label} must be a nonempty regular file")
    return resolved, payload


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            _fail(f"duplicate JSON key: {key}")
        value[key] = child
    return value


def _reject_constant(value: str) -> NoReturn:
    _fail(f"non-finite JSON value is forbidden: {value}")


def _strict_json(path: Path, label: str) -> tuple[Path, dict[str, Any], bytes]:
    resolved, payload = _read_regular(path, label)
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise QualificationTrustError(f"{label} is not UTF-8 JSON") from error
    if not isinstance(value, dict) or payload != _canonical(value) + b"\n":
        _fail(f"{label} must be canonical JSON plus terminal LF")
    return resolved, value, payload


def _forbidden_private_json(
        path: Path, label: str) -> tuple[Path, dict[str, Any], bytes]:
    """Read a historical identity without rewriting its original JSON byte."""
    resolved, payload = _read_regular(path, label)
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise QualificationTrustError(f"{label} is not UTF-8 JSON") from error
    if not isinstance(value, dict):
        _fail(f"{label} must be a strict JSON object")
    return resolved, value, payload


def _private_modulus_identity(value: Mapping[str, Any], label: str) -> str:
    current = value.get("rsa_modulus_base64")
    legacy = value.get("modulus")
    if isinstance(current, str) and current and legacy is None:
        return current
    if isinstance(legacy, str) and legacy and current is None:
        return legacy
    _fail(f"{label} has no unique public modulus identity")


def _write_new(path: Path, value: Mapping[str, Any], *, private: bool = False) \
        -> bytes:
    payload = _canonical(value) + b"\n"
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600 if private else 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return payload


def _outside_repository(path: Path, repository: Path, label: str) -> Path:
    supplied = path.expanduser().absolute()
    try:
        supplied = supplied.parent.resolve(strict=True) / supplied.name
    except OSError as error:
        raise QualificationTrustError(
            f"{label} parent is not an existing directory") from error
    try:
        supplied.relative_to(repository)
    except ValueError:
        return supplied
    _fail(f"{label} must remain outside the repository")


def _verify_signature(message: bytes, signature: bytes, *, modulus: int,
                      exponent: int) -> None:
    width = (modulus.bit_length() + 7) // 8
    if len(signature) != width:
        _fail("diagnostic signature width differs")
    digest_info = RSA_DIGEST_INFO + hashlib.sha256(message).digest()
    padding = width - len(digest_info) - 3
    if padding < 8:
        _fail("diagnostic RSA modulus is too small")
    expected = b"\x00\x01" + b"\xff" * padding + b"\x00" + digest_info
    observed = pow(
        int.from_bytes(signature, "big"), exponent, modulus).to_bytes(
            width, "big")
    if observed != expected:
        _fail("diagnostic signature failed public-exponent verification")


def _file_record(path: Path, payload: bytes, role: str) -> dict[str, object]:
    return {
        "role": role,
        # All qualification public outputs share one owner-local directory.
        # A basename keeps the evidence relocatable without weakening its
        # byte/length identity.
        "path": path.resolve(strict=True).name,
        "bytes": len(payload),
        "sha256": _sha(payload),
    }


def _validate_observation_time(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise QualificationTrustError(
            "owner-supplied observation time is not ISO-8601") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("owner-supplied observation time must carry a UTC offset")


def _exact_keys(value: object, expected: set[str], label: str) \
        -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        _fail(f"{label} keys differ")
    return value


def _require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(f"{label} must be a lowercase SHA-256")
    return value


def _validate_portable_record(
        value: object, *, expected_role: str, expected_path: Path,
        expected_payload: bytes, label: str) -> Mapping[str, Any]:
    row = _exact_keys(value, {"role", "path", "bytes", "sha256"}, label)
    path = row["path"]
    if row["role"] != expected_role or not isinstance(path, str) \
            or not path or path != Path(path).name or path in {".", ".."} \
            or row["bytes"] != len(expected_payload) \
            or type(row["bytes"]) is not int \
            or row["sha256"] != _sha(expected_payload) \
            or expected_path.name != path:
        _fail(f"{label} does not bind the expected portable artifact")
    return row


def validate_qualification_preuse(
        preuse: Mapping[str, Any], *, preuse_path: Path,
        public_root_path: Path, root_payload: bytes,
        root: Mapping[str, object]) -> tuple[int, int] | None:
    """Validate every qualification-only claim and both real signatures.

    Legacy formal-measurement v3 receipts return ``None`` and remain under
    their own validator.  A qualification-looking key can never fall through
    to that legacy path merely by deleting its marker.
    """
    key_id = preuse.get("key_id")
    marked = preuse.get("qualification_only_not_formal_measurement_root") is True
    prefixed = isinstance(key_id, str) and key_id.startswith(
        QUALIFICATION_ONLY_KEY_PREFIX)
    if not marked and not prefixed and preuse.get("schema") != PREUSE_SCHEMA:
        return None
    if not marked or not prefixed or preuse.get("schema") != PREUSE_SCHEMA:
        _fail("qualification pre-use marker/schema/key-id binding differs")

    expected_preuse_keys = {
        "schema", "status", "custody_observed_at_utc",
        "observation_host_label", "custody_state_at_receipt_snapshot",
        "key_id", "trust_root_sha256", "public_root_file_sha256",
        "private_key_file_sha256",
        "private_key_material_existed_in_owner_local_custody_at_receipt_snapshot",
        "private_key_committed_or_embedded_at_receipt_snapshot",
        "production_key_custody_attested", "diagnostic_receipt",
        "diagnostic_keypair_signing_occurred_before_receipt_snapshot",
        "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot",
        "diagnostic_keypair_signing_invocation_count_exactly_attested",
        "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot",
        "trust_package_signing_invocation_count_at_receipt_snapshot",
        "trust_head_signing_invocation_count_at_receipt_snapshot",
        "materialized_trust_sequence_count_at_receipt_snapshot",
        "formal_worker_count_at_receipt_snapshot",
        "registered_performance_timing_count_at_receipt_snapshot",
        "post_use_run_local_receipt_required", "future_state_not_claimed",
        "unmaterialized_sequence_claimed",
        "owner_provided_modern_rtx_target_observed_at_receipt_snapshot",
        "qualification_only_not_formal_measurement_root",
        "reserved_real_measurement_key_used",
        "forbidden_reserved_private_key_file_sha256",
        "expected_target_compute_capability", "final_package_plan",
        "observation_scope",
        "tracked_source_receipt_must_not_be_reinterpreted_as_current_after_pod",
        "custody_receipt_sha256",
    }
    _exact_keys(preuse, expected_preuse_keys, "qualification pre-use receipt")
    preuse_body = dict(preuse)
    preuse_seal = preuse_body.pop("custody_receipt_sha256")
    if _require_sha256(preuse_seal, "qualification pre-use seal") \
            != _digest(preuse_body):
        _fail("qualification pre-use seal differs")
    _validate_observation_time(str(preuse["custody_observed_at_utc"]))
    if not isinstance(preuse["observation_host_label"], str) \
            or not preuse["observation_host_label"].strip():
        _fail("qualification pre-use host label differs")
    if preuse["status"] != PREUSE_STATUS \
            or preuse["key_id"] != root["key_id"] \
            or preuse["trust_root_sha256"] != root["trust_root_sha256"] \
            or preuse["public_root_file_sha256"] != _sha(root_payload):
        _fail("qualification pre-use public-root binding differs")
    private_sha = _require_sha256(
        preuse["private_key_file_sha256"],
        "qualification pre-use private-key identity")
    if preuse["custody_state_at_receipt_snapshot"] != (
            "PRIVATE_KEY_RETAINED_OUTSIDE_REPOSITORY__ZERO_TRUST_PACKAGE_OR_"
            "HEAD_SIGNATURES") \
            or preuse[
                "private_key_material_existed_in_owner_local_custody_at_receipt_snapshot"] \
            is not True \
            or preuse["private_key_committed_or_embedded_at_receipt_snapshot"] \
            is not False \
            or preuse["production_key_custody_attested"] is not False \
            or preuse[
                "diagnostic_keypair_signing_occurred_before_receipt_snapshot"] \
            is not True \
            or preuse[
                "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot"] \
            != 2 \
            or type(preuse[
                "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot"]) \
            is not int \
            or preuse[
                "diagnostic_keypair_signing_invocation_count_exactly_attested"] \
            is not True \
            or preuse[
                "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot"] \
            != 2 \
            or type(preuse[
                "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot"]) \
            is not int:
        _fail("qualification pre-use diagnostic/custody claims differ")
    for key in (
            "trust_package_signing_invocation_count_at_receipt_snapshot",
            "trust_head_signing_invocation_count_at_receipt_snapshot",
            "materialized_trust_sequence_count_at_receipt_snapshot",
            "formal_worker_count_at_receipt_snapshot",
            "registered_performance_timing_count_at_receipt_snapshot"):
        if preuse[key] != 0 or type(preuse[key]) is not int:
            _fail(f"qualification pre-use zero counter differs: {key}")
    if preuse["post_use_run_local_receipt_required"] is not True \
            or preuse["future_state_not_claimed"] is not True \
            or preuse["unmaterialized_sequence_claimed"] is not False \
            or preuse[
                "owner_provided_modern_rtx_target_observed_at_receipt_snapshot"] \
            is not False \
            or preuse["reserved_real_measurement_key_used"] is not False \
            or preuse[
                "tracked_source_receipt_must_not_be_reinterpreted_as_current_after_pod"] \
            is not True \
            or preuse["expected_target_compute_capability"] \
            != QUALIFICATION_EXPECTED_TARGET_COMPUTE_CAPABILITY \
            or any(type(item) is not int for item in preuse[
                "expected_target_compute_capability"]):
        _fail("qualification pre-use scope/target boundary differs")
    if preuse["final_package_plan"] != (
            "HOME_QUALIFICATION_ONLY__SEQ1_RELATION_GENESIS__SEQ2_TRIANGLE_"
            "APPEND__NEVER_REUSED_FOR_FORMAL_MEASUREMENT") \
            or preuse["observation_scope"] != (
                "OWNER_LOCAL_QUALIFICATION_KEY_OUTSIDE_REPOSITORY__NO_GLOBAL_"
                "ABSENCE_CLAIM"):
        _fail("qualification pre-use frozen plan/scope differs")

    forbidden = preuse["forbidden_reserved_private_key_file_sha256"]
    if not isinstance(forbidden, list) or not forbidden \
            or forbidden != sorted(set(forbidden)) \
            or any(not isinstance(item, str) or not SHA256_RE.fullmatch(item)
                   for item in forbidden) \
            or RESERVED_MEASUREMENT_PRIVATE_SHA256 not in forbidden \
            or private_sha in forbidden:
        _fail("qualification pre-use forbidden-key identities differ")

    diagnostic_record = _exact_keys(
        preuse["diagnostic_receipt"], {"role", "path", "bytes", "sha256"},
        "qualification diagnostic record")
    diagnostic_name = diagnostic_record["path"]
    if not isinstance(diagnostic_name, str) or not diagnostic_name \
            or diagnostic_name != Path(diagnostic_name).name \
            or diagnostic_name in {".", ".."}:
        _fail("qualification diagnostic path is not a portable basename")
    diagnostic_path = preuse_path.resolve(strict=True).parent / diagnostic_name
    _, diagnostic, diagnostic_payload = _strict_json(
        diagnostic_path, "qualification diagnostic receipt")
    _validate_portable_record(
        diagnostic_record,
        expected_role="qualification_diagnostic_receipt",
        expected_path=diagnostic_path,
        expected_payload=diagnostic_payload,
        label="qualification diagnostic record")

    expected_diagnostic_keys = {
        "schema", "status", "key_id", "trust_root_sha256", "public_root",
        "private_key_file_sha256", "forbidden_reserved_private_keys",
        "reserved_private_key_reused", "diagnostic_domain_base64",
        "diagnostic_signing_invocation_exact_count", "diagnostic_signatures",
        "trust_package_signing_invocation_count",
        "trust_head_signing_invocation_count",
        "materialized_trust_sequence_count", "formal_worker_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "clock_read_count", "receipt_sha256",
    }
    _exact_keys(
        diagnostic, expected_diagnostic_keys,
        "qualification diagnostic receipt")
    diagnostic_body = dict(diagnostic)
    diagnostic_seal = diagnostic_body.pop("receipt_sha256")
    if _require_sha256(diagnostic_seal, "qualification diagnostic seal") \
            != _digest(diagnostic_body):
        _fail("qualification diagnostic seal differs")
    public_root_path = public_root_path.resolve(strict=True)
    _validate_portable_record(
        diagnostic["public_root"], expected_role="public_root",
        expected_path=public_root_path, expected_payload=root_payload,
        label="qualification diagnostic public root")
    if diagnostic["schema"] != DIAGNOSTIC_SCHEMA \
            or diagnostic["status"] != DIAGNOSTIC_STATUS \
            or diagnostic["key_id"] != root["key_id"] \
            or diagnostic["trust_root_sha256"] != root["trust_root_sha256"] \
            or diagnostic["private_key_file_sha256"] != private_sha \
            or diagnostic["reserved_private_key_reused"] is not False \
            or diagnostic["diagnostic_domain_base64"] != base64.b64encode(
                DIAGNOSTIC_DOMAIN).decode("ascii") \
            or diagnostic["diagnostic_signing_invocation_exact_count"] != 2 \
            or type(diagnostic[
                "diagnostic_signing_invocation_exact_count"]) is not int:
        _fail("qualification diagnostic envelope/binding differs")
    for key in (
            "trust_package_signing_invocation_count",
            "trust_head_signing_invocation_count",
            "materialized_trust_sequence_count", "formal_worker_count",
            "registered_performance_timing_count", "gpu_kernel_launch_count",
            "clock_read_count"):
        if diagnostic[key] != 0 or type(diagnostic[key]) is not int:
            _fail(f"qualification diagnostic zero counter differs: {key}")
    forbidden_rows = diagnostic["forbidden_reserved_private_keys"]
    if not isinstance(forbidden_rows, list) or not forbidden_rows:
        _fail("qualification diagnostic has no forbidden-key rows")
    seen_paths: set[str] = set()
    seen_hashes: set[str] = set()
    for index, raw_row in enumerate(forbidden_rows):
        row = _exact_keys(
            raw_row, {"path", "bytes", "sha256"},
            f"qualification forbidden key row {index}")
        path = row["path"]
        sha = _require_sha256(
            row["sha256"], f"qualification forbidden key row {index} sha256")
        if not isinstance(path, str) or not path \
                or type(row["bytes"]) is not int or row["bytes"] <= 0 \
                or path in seen_paths or sha in seen_hashes:
            _fail("qualification forbidden-key row differs")
        seen_paths.add(path)
        seen_hashes.add(sha)
    if [row["path"] for row in forbidden_rows] != sorted(seen_paths) \
            or sorted(seen_hashes) != forbidden \
            or RESERVED_MEASUREMENT_PRIVATE_SHA256 not in seen_hashes \
            or private_sha in seen_hashes:
        _fail("qualification diagnostic/pre-use forbidden identities differ")

    signatures = diagnostic["diagnostic_signatures"]
    if not isinstance(signatures, list) or len(signatures) != 2:
        _fail("qualification diagnostic must carry exactly two signatures")
    try:
        modulus = int(root["_rsa_modulus"])
        exponent = int(root["rsa_exponent"])
    except (KeyError, TypeError, ValueError) as error:
        raise QualificationTrustError(
            "qualification public root lacks verified RSA values") from error
    for ordinal, raw_row in enumerate(signatures, 1):
        row = _exact_keys(raw_row, {
            "diagnostic_ordinal", "message_body", "message_sha256",
            "signature_algorithm", "signature_base64", "signature_sha256",
            "verified_with_public_exponent",
        }, f"qualification diagnostic signature {ordinal}")
        message_body = _exact_keys(row["message_body"], {
            "schema", "key_id", "public_root_file_sha256",
            "diagnostic_ordinal", "purpose",
        }, f"qualification diagnostic message {ordinal}")
        if row["diagnostic_ordinal"] != ordinal \
                or type(row["diagnostic_ordinal"]) is not int \
                or message_body != {
                    "schema": DIAGNOSTIC_MESSAGE_SCHEMA,
                    "key_id": root["key_id"],
                    "public_root_file_sha256": _sha(root_payload),
                    "diagnostic_ordinal": ordinal,
                    "purpose": DIAGNOSTIC_PURPOSE,
                } \
                or row["signature_algorithm"] != "rsa-pkcs1-v1_5-sha256" \
                or row["verified_with_public_exponent"] is not True:
            _fail("qualification diagnostic message/signature metadata differs")
        message = DIAGNOSTIC_DOMAIN + _canonical(message_body)
        if row["message_sha256"] != _sha(message):
            _fail("qualification diagnostic message digest differs")
        try:
            signature = base64.b64decode(
                row["signature_base64"], validate=True)
        except (TypeError, ValueError) as error:
            raise QualificationTrustError(
                "qualification diagnostic signature is not canonical base64") \
                from error
        if base64.b64encode(signature).decode("ascii") \
                != row["signature_base64"] \
                or row["signature_sha256"] != _sha(signature):
            _fail("qualification diagnostic signature identity differs")
        _verify_signature(
            message, signature, modulus=modulus, exponent=exponent)
    return tuple(QUALIFICATION_EXPECTED_TARGET_COMPUTE_CAPABILITY)


def create(args: argparse.Namespace) -> dict[str, Any]:
    repository = args.repository.expanduser().resolve(strict=True)
    if not repository.is_dir() or repository != REPO_ROOT.resolve(strict=True):
        _fail("repository root must equal the helper's actual source repository")
    outputs = {
        "private_key": _outside_repository(
            args.private_key, repository, "qualification private key"),
        "public_root": _outside_repository(
            args.public_root, repository, "qualification public root"),
        "diagnostic_receipt": _outside_repository(
            args.diagnostic_receipt, repository, "diagnostic receipt"),
        "preuse_custody": _outside_repository(
            args.preuse_custody, repository, "pre-use custody receipt"),
    }
    if len(set(outputs.values())) != len(outputs):
        _fail("qualification output paths must be distinct")
    parents = {path.parent.resolve(strict=True) for path in outputs.values()}
    if len(parents) != 1:
        _fail("qualification outputs must share one existing owner-local directory")
    if any(path.exists() or path.is_symlink() for path in outputs.values()):
        raise FileExistsError("qualification output already exists")
    _validate_observation_time(args.observed_at_utc)
    if not args.observation_host_label.strip():
        _fail("observation host label must be nonempty")
    if not isinstance(args.key_id, str) or not args.key_id.startswith(
            QUALIFICATION_ONLY_KEY_PREFIX):
        _fail("qualification key id has the wrong TEST_ONLY prefix")
    if args.bits != 3072:
        _fail("qualification key must use the frozen 3072-bit size")

    forbidden_rows: list[dict[str, object]] = []
    forbidden_moduli: set[str] = set()
    forbidden_hashes: set[str] = set()
    forbidden_paths: set[Path] = set()
    reserved_private_path, reserved_private, reserved_private_payload = \
        _strict_json(
            args.reserved_measurement_private_key,
            "reserved formal measurement private key")
    reserved_public_path, reserved_public, reserved_public_payload = _strict_json(
        args.reserved_measurement_public_root,
        "reserved formal measurement public root")
    if _sha(reserved_private_payload) != RESERVED_MEASUREMENT_PRIVATE_SHA256 \
            or _sha(reserved_public_payload) \
            != RESERVED_MEASUREMENT_PUBLIC_SHA256 \
            or reserved_public.get("key_id") != RESERVED_MEASUREMENT_KEY_ID \
            or reserved_public.get("trust_root_sha256") \
            != RESERVED_MEASUREMENT_TRUST_ROOT_SHA256:
        _fail("reserved formal measurement key authority differs")
    try:
        reserved_root = trust.runtime._read_trust_root(reserved_public_path)
        trust._private_key(reserved_private_path, reserved_root)
    except Exception as error:
        raise QualificationTrustError(
            "reserved formal measurement private/public key binding failed") \
            from error
    reserved_modulus = reserved_private.get("rsa_modulus_base64")
    if not isinstance(reserved_modulus, str) or not reserved_modulus:
        _fail("reserved formal measurement key has no modulus")

    all_forbidden = [
        args.reserved_measurement_private_key,
        *args.forbidden_private_key_file,
    ]
    for path in all_forbidden:
        resolved, value, payload = _forbidden_private_json(
            path, "forbidden private key")
        if resolved in forbidden_paths:
            _fail("duplicate forbidden private-key path")
        forbidden_paths.add(resolved)
        modulus = _private_modulus_identity(value, "forbidden private key")
        payload_sha = _sha(payload)
        if payload_sha in forbidden_hashes or modulus in forbidden_moduli:
            _fail("duplicate forbidden private-key identity")
        forbidden_hashes.add(payload_sha)
        forbidden_moduli.add(modulus)
        forbidden_rows.append({
            "path": str(resolved), "bytes": len(payload), "sha256": payload_sha,
        })
    if not forbidden_rows:
        _fail("at least one reserved key must be named as forbidden")
    forbidden_rows.sort(key=lambda row: str(row["path"]))

    with contextlib.redirect_stdout(io.StringIO()):
        trust.create_root(
            private_path=outputs["private_key"],
            public_path=outputs["public_root"],
            key_id=args.key_id,
            bits=args.bits,
        )
    private_path, private, private_payload = _strict_json(
        outputs["private_key"], "new qualification private key")
    public_path, public, public_payload = _strict_json(
        outputs["public_root"], "new qualification public root")
    try:
        verified_root = trust.runtime._read_trust_root(public_path)
        modulus, exponent, private_exponent = trust._private_key(
            private_path, verified_root)
    except Exception as error:
        raise QualificationTrustError(
            "new qualification keypair failed exact validation") from error
    if private.get("rsa_modulus_base64") in forbidden_moduli \
            or _sha(private_payload) in {str(row["sha256"]) for row in forbidden_rows}:
        _fail("new qualification key reuses a forbidden reserved key identity")

    diagnostic_rows: list[dict[str, object]] = []
    signing_invocation_count = 0
    for ordinal in (1, 2):
        message_body = {
            "schema": DIAGNOSTIC_MESSAGE_SCHEMA,
            "key_id": public["key_id"],
            "public_root_file_sha256": _sha(public_payload),
            "diagnostic_ordinal": ordinal,
            "purpose": DIAGNOSTIC_PURPOSE,
        }
        message = DIAGNOSTIC_DOMAIN + _canonical(message_body)
        signature = trust._sign(
            message, modulus=modulus, private_exponent=private_exponent)
        signing_invocation_count += 1
        _verify_signature(
            message, signature, modulus=modulus, exponent=exponent)
        diagnostic_rows.append({
            "diagnostic_ordinal": ordinal,
            "message_body": message_body,
            "message_sha256": _sha(message),
            "signature_algorithm": "rsa-pkcs1-v1_5-sha256",
            "signature_base64": base64.b64encode(signature).decode("ascii"),
            "signature_sha256": _sha(signature),
            "verified_with_public_exponent": True,
        })
    if signing_invocation_count != 2 or len(diagnostic_rows) != 2:
        _fail("qualification diagnostic signing count differs from exactly two")

    diagnostic_body: dict[str, Any] = {
        "schema": DIAGNOSTIC_SCHEMA,
        "status": DIAGNOSTIC_STATUS,
        "key_id": public["key_id"],
        "trust_root_sha256": public["trust_root_sha256"],
        "public_root": _file_record(public_path, public_payload, "public_root"),
        "private_key_file_sha256": _sha(private_payload),
        "forbidden_reserved_private_keys": forbidden_rows,
        "reserved_private_key_reused": False,
        "diagnostic_domain_base64": base64.b64encode(
            DIAGNOSTIC_DOMAIN).decode("ascii"),
        "diagnostic_signing_invocation_exact_count": signing_invocation_count,
        "diagnostic_signatures": diagnostic_rows,
        "trust_package_signing_invocation_count": 0,
        "trust_head_signing_invocation_count": 0,
        "materialized_trust_sequence_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "clock_read_count": 0,
    }
    diagnostic = {
        **diagnostic_body, "receipt_sha256": _digest(diagnostic_body)}
    diagnostic_payload = _write_new(
        outputs["diagnostic_receipt"], diagnostic)

    preuse_body: dict[str, Any] = {
        "schema": PREUSE_SCHEMA,
        "status": PREUSE_STATUS,
        "custody_observed_at_utc": args.observed_at_utc,
        "observation_host_label": args.observation_host_label,
        "custody_state_at_receipt_snapshot": (
            "PRIVATE_KEY_RETAINED_OUTSIDE_REPOSITORY__ZERO_TRUST_PACKAGE_OR_"
            "HEAD_SIGNATURES"),
        "key_id": public["key_id"],
        "trust_root_sha256": public["trust_root_sha256"],
        "public_root_file_sha256": _sha(public_payload),
        "private_key_file_sha256": _sha(private_payload),
        "private_key_material_existed_in_owner_local_custody_at_receipt_snapshot": True,
        "private_key_committed_or_embedded_at_receipt_snapshot": False,
        "production_key_custody_attested": False,
        "diagnostic_receipt": _file_record(
            outputs["diagnostic_receipt"], diagnostic_payload,
            "qualification_diagnostic_receipt"),
        "diagnostic_keypair_signing_occurred_before_receipt_snapshot": True,
        "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot": 2,
        "diagnostic_keypair_signing_invocation_count_exactly_attested": True,
        "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot": 2,
        "trust_package_signing_invocation_count_at_receipt_snapshot": 0,
        "trust_head_signing_invocation_count_at_receipt_snapshot": 0,
        "materialized_trust_sequence_count_at_receipt_snapshot": 0,
        "formal_worker_count_at_receipt_snapshot": 0,
        "registered_performance_timing_count_at_receipt_snapshot": 0,
        "post_use_run_local_receipt_required": True,
        "future_state_not_claimed": True,
        "unmaterialized_sequence_claimed": False,
        "owner_provided_modern_rtx_target_observed_at_receipt_snapshot": False,
        "qualification_only_not_formal_measurement_root": True,
        "reserved_real_measurement_key_used": False,
        "forbidden_reserved_private_key_file_sha256": sorted(
            str(row["sha256"]) for row in forbidden_rows),
        "expected_target_compute_capability":
            QUALIFICATION_EXPECTED_TARGET_COMPUTE_CAPABILITY,
        "final_package_plan": (
            "HOME_QUALIFICATION_ONLY__SEQ1_RELATION_GENESIS__SEQ2_TRIANGLE_"
            "APPEND__NEVER_REUSED_FOR_FORMAL_MEASUREMENT"),
        "observation_scope": (
            "OWNER_LOCAL_QUALIFICATION_KEY_OUTSIDE_REPOSITORY__NO_GLOBAL_"
            "ABSENCE_CLAIM"),
        "tracked_source_receipt_must_not_be_reinterpreted_as_current_after_pod": True,
    }
    preuse = {**preuse_body, "custody_receipt_sha256": _digest(preuse_body)}
    preuse_payload = _canonical(preuse) + b"\n"
    private_exponent = str(
        private["rsa_private_exponent_base64"]).encode("ascii")
    for label, payload in (
            ("public root", public_payload),
            ("diagnostic receipt", diagnostic_payload),
            ("pre-use custody receipt", preuse_payload)):
        if private_payload in payload or private_exponent in payload:
            _fail(f"qualification private material leaked into {label}")
    _write_new(outputs["preuse_custody"], preuse)
    return preuse


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a qualification-only Goal5802 trust pre-use receipt")
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--diagnostic-receipt", type=Path, required=True)
    parser.add_argument("--preuse-custody", type=Path, required=True)
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--bits", type=int, default=3072)
    parser.add_argument(
        "--reserved-measurement-private-key", type=Path, required=True)
    parser.add_argument(
        "--reserved-measurement-public-root", type=Path, required=True)
    parser.add_argument(
        "--forbidden-private-key-file", action="append", type=Path,
        default=[])
    parser.add_argument("--observed-at-utc", required=True)
    parser.add_argument("--observation-host-label", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    receipt = create(args)
    print(json.dumps({
        "status": receipt["status"],
        "key_id": receipt["key_id"],
        "public_root_file_sha256": receipt["public_root_file_sha256"],
        "private_key_file_sha256": receipt["private_key_file_sha256"],
        "custody_receipt_sha256": receipt["custody_receipt_sha256"],
        "diagnostic_exact_count": 2,
        "trust_package_count": 0,
        "trust_head_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
