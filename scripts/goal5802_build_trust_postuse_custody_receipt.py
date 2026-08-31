#!/usr/bin/env python3
"""Build a truthful post-use TEST_ONLY trust-key custody receipt.

All counters and the observed private-key state are explicit operator inputs.
The helper verifies the public signed chain but never signs, deletes, moves, or
copies the private key.  In particular, absence at one path is never promoted
to an erasure, non-recovery, or global-absence claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Mapping, NoReturn


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rtdsl import v4_rtdlexe as runtime  # noqa: E402


SCHEMA = "rtdl.goal5802.test_trust_postuse_custody_receipt.v1"
PRESENT = "PRESENT_RETAINED_OUTSIDE_REPOSITORY"
ABSENT = "ABSENT_AT_DECLARED_PATH__NO_ERASURE_OR_NONRECOVERY_CLAIM"
PRIVATE_SCHEMA = "rtdl.v4.rtdlexe.signer_private_key.v1"
PRIVATE_NOTICE = "SECRET__STORE_OUTSIDE_REPOSITORY_AND_DEPLOYMENT_ARTIFACTS"
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


class TrustPostuseError(RuntimeError):
    """Fail-closed custody-observation error."""


def _fail(message: str) -> NoReturn:
    raise TrustPostuseError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_create_only(path: Path, payload: bytes) -> None:
    path = path.expanduser().absolute()
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _regular_bytes(path: Path, label: str) -> tuple[Path, bytes]:
    supplied = path.expanduser().absolute()
    if supplied.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        resolved = supplied.resolve(strict=True)
        metadata = resolved.stat()
        payload = resolved.read_bytes()
    except OSError as error:
        raise TrustPostuseError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    return resolved, payload


def _strict_json(path: Path, label: str) -> tuple[Path, dict[str, Any], bytes]:
    resolved, payload = _regular_bytes(path, label)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise TrustPostuseError(f"{label} is not UTF-8 JSON") from error
    if not isinstance(value, dict) or payload != _canonical(value) + b"\n":
        _fail(f"{label} is not a canonical JSON object plus LF")
    return resolved, value, payload


def _artifact(path: Path, payload: bytes, role: str) -> dict[str, object]:
    return {
        "role": role, "path": str(path),
        "bytes": len(payload), "sha256": _sha(payload),
    }


def _nonnegative(value: int, label: str) -> int:
    if type(value) is not int or value < 0:
        _fail(f"{label} must be a nonnegative integer")
    return value


def _validate_preuse(
        preuse: Mapping[str, Any], *, root_payload: bytes,
        root: Mapping[str, object], preuse_path: Path,
        public_root_path: Path) -> tuple[int, int] | None:
    # Qualification receipts use an exact, independently sealed schema whose
    # two diagnostic signatures are decision-bearing.  Import lazily so the
    # historical formal-measurement v3 receipt keeps its original path.
    from scripts import goal5802_create_qualification_trust_preuse \
        as qualification
    qualification_target = qualification.validate_qualification_preuse(
        preuse, preuse_path=preuse_path, public_root_path=public_root_path,
        root_payload=root_payload, root=root)
    if qualification_target is not None:
        return qualification_target
    if preuse.get("schema") \
            != "rtdl.goal5802.test_trust_key_custody_receipt.v3":
        _fail("pre-use custody receipt schema differs")
    if preuse.get("key_id") != root["key_id"] \
            or preuse.get("trust_root_sha256") != root["trust_root_sha256"] \
            or preuse.get("public_root_file_sha256") != _sha(root_payload):
        _fail("pre-use custody receipt does not bind the supplied public root")
    if preuse.get("post_use_run_local_receipt_required") is not True \
            or preuse.get("future_state_not_claimed") is not True:
        _fail("pre-use custody receipt did not require this post-use snapshot")
    if not SHA_RE.fullmatch(str(preuse.get("private_key_file_sha256"))):
        _fail("pre-use custody receipt has no exact private-key file identity")
    return None


def _validate_private_key(
        path: Path, payload: bytes, *, root: Mapping[str, object],
        preuse: Mapping[str, Any]) -> dict[str, object]:
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise TrustPostuseError("private key is not UTF-8 JSON") from error
    expected = {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "rsa_private_exponent_base64", "security_notice",
    }
    if not isinstance(value, dict) or set(value) != expected \
            or payload != _canonical(value) + b"\n" \
            or value["schema"] != PRIVATE_SCHEMA \
            or value["security_notice"] != PRIVATE_NOTICE \
            or value["key_id"] != root["key_id"] \
            or value["rsa_modulus_base64"] != root["rsa_modulus_base64"] \
            or value["rsa_exponent"] != root["rsa_exponent"]:
        _fail("private key envelope does not match the public root")
    observed_sha = _sha(payload)
    expected_sha = preuse.get("private_key_file_sha256")
    if not SHA_RE.fullmatch(str(expected_sha)) or observed_sha != expected_sha:
        _fail("retained private key differs from the pre-use custody snapshot")
    return {
        "declared_path": str(path),
        "observed_state": PRESENT,
        "regular_file_observed": True,
        "bytes": len(payload),
        "sha256": observed_sha,
        "copied_or_embedded_in_receipt": False,
    }


def build_receipt(args: argparse.Namespace) -> dict[str, object]:
    if not isinstance(args.observed_at_utc, str) or not args.observed_at_utc \
            or not isinstance(args.observation_host_label, str) \
            or not args.observation_host_label.strip():
        _fail("owner-supplied observation time and host label must be nonempty")
    try:
        observed_time = datetime.fromisoformat(
            args.observed_at_utc.replace("Z", "+00:00"))
    except ValueError as error:
        raise TrustPostuseError(
            "owner-supplied observation time is not ISO-8601") from error
    if observed_time.tzinfo is None or observed_time.utcoffset() is None:
        _fail("owner-supplied observation time must carry a UTC offset")
    root_path, _, root_payload = _strict_json(args.public_root, "public root")
    try:
        root = runtime._read_trust_root(root_path)
    except Exception as error:
        raise TrustPostuseError("public root validation failed") from error
    preuse_path, preuse, preuse_payload = _strict_json(
        args.preuse_custody, "pre-use custody receipt")
    _validate_preuse(
        preuse, root_payload=root_payload, root=root,
        preuse_path=preuse_path, public_root_path=root_path)

    package_rows = []
    prior_sha: str | None = None
    package_shas: list[str] = []
    final_entries: tuple[Mapping[str, object], ...] = ()
    for expected_sequence, supplied in enumerate(args.trust_package, 1):
        path, _, payload = _strict_json(
            supplied, f"trust package sequence {expected_sequence}")
        try:
            package, entries = runtime._verify_trust_package(path, root=root)
        except Exception as error:
            raise TrustPostuseError(
                f"trust package sequence {expected_sequence} validation failed") \
                from error
        observed_sha = _sha(payload)
        if package["sequence"] != expected_sequence \
                or package["previous_package_sha256"] != prior_sha \
                or len(entries) != expected_sequence:
            _fail("trust package sequence/append chain differs")
        package_rows.append({
            **_artifact(path, payload, f"trust_package_seq{expected_sequence}"),
            "sequence": expected_sequence,
            "authority_count": len(entries),
            "deployment_ids": [str(row["deployment_id"]) for row in entries],
        })
        prior_sha = observed_sha
        package_shas.append(observed_sha)
        final_entries = entries
    if not package_rows:
        _fail("at least one materialized trust package is required post-use")

    head_rows = []
    if len(args.trust_head) != len(package_rows):
        _fail("every materialized package requires its preserved signed head")
    for expected_sequence, supplied in enumerate(args.trust_head, 1):
        head_path, _, head_payload = _strict_json(
            supplied, f"trust head sequence {expected_sequence}")
        try:
            head = runtime._verify_trust_head(head_path, root=root)
        except Exception as error:
            raise TrustPostuseError(
                f"trust head sequence {expected_sequence} validation failed") \
                from error
        if head["current_sequence"] != expected_sequence \
                or head["current_package_sha256"] != package_shas[
                    expected_sequence - 1]:
            _fail("trust head does not bind its same-sequence package")
        head_rows.append({
            **_artifact(head_path, head_payload,
                        f"trust_head_seq{expected_sequence}"),
            "current_sequence": expected_sequence,
            "current_package_sha256": head["current_package_sha256"],
        })
    actual_deployments = [str(row["deployment_id"]) for row in final_entries]
    if args.expected_deployment_id:
        expected_deployments = sorted(args.expected_deployment_id)
        if len(expected_deployments) != len(set(expected_deployments)) \
                or actual_deployments != expected_deployments:
            _fail("final trust-package deployment set differs from expectation")

    package_signings = _nonnegative(
        args.trust_package_signing_count, "trust-package signing count")
    head_signings = _nonnegative(
        args.trust_head_signing_count, "trust-head signing count")
    diagnostic_minimum = _nonnegative(
        args.diagnostic_signing_known_minimum,
        "diagnostic signing known minimum")
    diagnostic_exact = args.diagnostic_signing_exact_count
    if diagnostic_exact is not None:
        diagnostic_exact = _nonnegative(
            diagnostic_exact, "diagnostic exact signing count")
        if diagnostic_exact < diagnostic_minimum:
            _fail("diagnostic exact signing count is below its known minimum")
    if package_signings < len(package_rows) or head_signings < len(head_rows):
        _fail("explicit signing counters are below the preserved signed outputs")
    if args.formal_worker_count != 0 or args.registered_timing_count != 0:
        _fail("POD-S0 post-use custody requires zero formal workers and timings")
    gpu_launches = _nonnegative(
        args.untimed_gpu_kernel_launch_count, "untimed GPU-kernel launch count")

    declared_private = args.private_key.expanduser().absolute()
    if args.private_key_state == PRESENT:
        private_path, private_payload = _regular_bytes(
            args.private_key, "retained private key")
        private_observation = _validate_private_key(
            private_path, private_payload, root=root, preuse=preuse)
    elif args.private_key_state == ABSENT:
        if declared_private.exists() or declared_private.is_symlink():
            _fail("private key was declared absent but the path exists")
        private_observation = {
            "declared_path": str(declared_private),
            "observed_state": ABSENT,
            "regular_file_observed": False,
            "preuse_sha256_retained_as_historical_identity": preuse.get(
                "private_key_file_sha256"),
            "copied_or_embedded_in_receipt": False,
        }
    else:
        _fail("unsupported private-key state")

    body: dict[str, object] = {
        "schema": SCHEMA,
        "status": "TEST_ONLY_POSTUSE_CUSTODY_SNAPSHOT__SIGNED_CHAIN_VERIFIED",
        "observed_at_utc_owner_supplied": args.observed_at_utc,
        "observation_host_label_owner_supplied": args.observation_host_label,
        "preuse_custody_receipt": _artifact(
            preuse_path, preuse_payload, "preuse_custody_receipt"),
        "public_root": {
            **_artifact(root_path, root_payload, "public_root"),
            "key_id": root["key_id"],
            "trust_root_sha256": root["trust_root_sha256"],
        },
        "materialized_trust_chain": {
            "packages": package_rows,
            "heads": head_rows,
            "final_head": head_rows[-1],
            "materialized_sequence_count": len(package_rows),
            "final_deployment_ids": actual_deployments,
            "all_signatures_verified_against_public_root": True,
        },
        "explicit_actual_counters": {
            "diagnostic_keypair_signing_invocation_known_minimum": diagnostic_minimum,
            "diagnostic_keypair_signing_invocation_count_exactly_attested": (
                diagnostic_exact is not None),
            "diagnostic_keypair_signing_invocation_exact_count": diagnostic_exact,
            "trust_package_signing_invocation_count": package_signings,
            "trust_head_signing_invocation_count": head_signings,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "untimed_gpu_kernel_launch_count": gpu_launches,
            "trust_package_signing_invocations_without_preserved_package": (
                package_signings - len(package_rows)),
            "trust_head_signing_invocations_without_preserved_head": (
                head_signings - len(head_rows)),
        },
        "private_key_observation": private_observation,
        "claim_boundaries": {
            "test_only_not_production_key": True,
            "private_key_committed_or_embedded": False,
            "private_key_erasure_attested": False,
            "private_key_nonrecoverability_attested": False,
            "global_private_key_absence_attested": False,
            "absence_at_declared_path_is_not_erasure": True,
            "future_state_not_claimed": True,
            "receipt_is_snapshot_not_continuous_monitoring": True,
            "execution_authority_consumed": False,
            "performance_claim_authorized": False,
        },
        "clock_read_count_by_helper": 0,
        "create_only": True,
    }
    return {**body, "receipt_sha256": _digest(body)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a create-only Goal5802 TEST_ONLY post-use custody receipt")
    parser.add_argument("--preuse-custody", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument(
        "--private-key-state", choices=(PRESENT, ABSENT), required=True)
    parser.add_argument("--trust-package", action="append", type=Path, required=True)
    parser.add_argument("--trust-head", action="append", type=Path, required=True)
    parser.add_argument("--expected-deployment-id", action="append")
    parser.add_argument("--observed-at-utc", required=True)
    parser.add_argument("--observation-host-label", required=True)
    parser.add_argument(
        "--diagnostic-signing-known-minimum", type=int, required=True)
    parser.add_argument("--diagnostic-signing-exact-count", type=int)
    parser.add_argument("--trust-package-signing-count", type=int, required=True)
    parser.add_argument("--trust-head-signing-count", type=int, required=True)
    parser.add_argument("--formal-worker-count", type=int, required=True)
    parser.add_argument("--registered-timing-count", type=int, required=True)
    parser.add_argument(
        "--untimed-gpu-kernel-launch-count", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    receipt = build_receipt(args)
    _write_create_only(args.output, _canonical(receipt) + b"\n")
    print(json.dumps({
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "materialized_sequence_count": receipt["materialized_trust_chain"][
            "materialized_sequence_count"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
