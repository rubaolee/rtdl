#!/usr/bin/env python3
"""Sign exactly one Goal5802 POD-S0 TEST_ONLY trust request offline.

This entrypoint is deliberately owner-side only.  It consumes the canonical
request and the two detached candidate authorities copied back from the target,
uses the retained TEST_ONLY private key to materialize exactly sequence 1
(relation genesis) and sequence 2 (triangle successor), and emits a portable
response directory.  It never imports CUDA, launches a GPU, creates a formal
worker, records a performance timing, or emits an execution authority.

The private key is read in place and is never copied into the response.  The
response contains the signed public chain, a truthful post-use custody snapshot,
and relative outer file records so the whole directory can be copied to the POD.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
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

from scripts import goal5801_rtdlexe_trust as trust  # noqa: E402
from scripts import goal5802_build_trust_postuse_custody_receipt as custody  # noqa: E402


REQUEST_SCHEMA = "rtdl.goal5802.pod_s0_trust_request.v1"
RESPONSE_SCHEMA = "rtdl.goal5802.pod_s0_signed_trust_response.v1"
REQUEST_STATUS = "PREPARED__OFFLINE_TEST_ONLY_SIGNING_REQUIRED"
RESPONSE_STATUS = "PASS__EXACT_TWO_SEQUENCE_TEST_ONLY_TRUST_RESPONSE"
AUTHORITY_SCHEMA = "rtdl.v4.rtdlexe.detached_authority.v1"
RELATION_FAMILY = "custom_aabb_bounded_relation_v1"
TRIANGLE_FAMILY = "builtin_triangle_reduction_v1"
FORMAL_MEASUREMENT_KEY_ID = (
    "TEST_ONLY_goal5802_rtx_measurement_root_v5_20260826")
FORMAL_MEASUREMENT_PREUSE_SHA256 = (
    "977b91702d9859e69e8f084ff1deeea072fa1d7fb09ee4299a69d182bc50f7a6")
FORMAL_MEASUREMENT_PREUSE_PATH = REPO_ROOT / (
    "history/internal_docs/"
    "goal5802_rtx_measurement_test_trust_key_custody_v5_20260826.json")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")


class OfflineSigningError(RuntimeError):
    """Fail-closed request, custody, or response error."""


def _fail(message: str) -> NoReturn:
    raise OfflineSigningError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_constant(value: str) -> NoReturn:
    _fail(f"non-finite JSON value is forbidden: {value}")


def _regular_bytes(path: Path, label: str) -> tuple[Path, bytes]:
    supplied = path.expanduser().absolute()
    if supplied.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        resolved = supplied.resolve(strict=True)
        metadata = resolved.stat()
        payload = resolved.read_bytes()
    except OSError as error:
        raise OfflineSigningError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    return resolved, payload


def _strict_json(path: Path, label: str) -> tuple[Path, dict[str, Any], bytes]:
    resolved, payload = _regular_bytes(path, label)
    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfflineSigningError(f"{label} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict) or payload != _canonical(value) + b"\n":
        _fail(f"{label} must be a canonical JSON object plus terminal LF")
    return resolved, value, payload


def _exact_keys(value: object, expected: set[str], label: str) \
        -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        _fail(f"{label} keys differ")
    return value


def _sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(f"{label} must be a lowercase SHA-256")
    return value


def _sha1(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA1_RE.fullmatch(value):
        _fail(f"{label} must be a lowercase Git SHA-1")
    return value


def _request_file_record(value: object, label: str) -> Mapping[str, Any]:
    row = _exact_keys(value, {"path", "bytes", "sha256"}, label)
    if not isinstance(row["path"], str) or not row["path"] \
            or "\\" in row["path"]:
        _fail(f"{label} path must be a nonempty POSIX path")
    remote = PurePosixPath(row["path"])
    if not remote.is_absolute() or any(part in {"", ".", ".."}
                                       for part in remote.parts):
        _fail(f"{label} path must be an absolute non-traversing POD path")
    if type(row["bytes"]) is not int or row["bytes"] <= 0:
        _fail(f"{label} byte count must be a positive integer")
    _sha256(row["sha256"], f"{label} sha256")
    return row


def _record_matches(row: Mapping[str, Any], payload: bytes, label: str) -> None:
    if row["bytes"] != len(payload) or row["sha256"] != _sha(payload):
        _fail(f"{label} bytes differ from the frozen request")


def _enforce_formal_preuse_identity(
        root: Mapping[str, object], preuse_path: Path,
        preuse_payload: bytes) -> None:
    """Bind the reserved real-measurement key to its tracked pre-use byte."""
    if root.get("key_id") != FORMAL_MEASUREMENT_KEY_ID:
        return
    try:
        expected_path = FORMAL_MEASUREMENT_PREUSE_PATH.resolve(strict=True)
    except OSError as error:
        raise OfflineSigningError(
            "tracked formal-measurement pre-use receipt is absent") from error
    if preuse_path.resolve(strict=True) != expected_path \
            or _sha(preuse_payload) != FORMAL_MEASUREMENT_PREUSE_SHA256:
        _fail("reserved formal-measurement pre-use receipt identity differs")


def _validate_authority(path: Path, slot: str) -> tuple[Path, dict[str, Any], bytes]:
    resolved, value, payload = _strict_json(path, f"{slot} authority")
    expected = {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }
    _exact_keys(value, expected, f"{slot} authority")
    if value["schema"] != AUTHORITY_SCHEMA \
            or type(value["authority_version"]) is not int \
            or value["authority_version"] != 1 \
            or type(value["artifact_bytes"]) is not int \
            or value["artifact_bytes"] <= 0:
        _fail(f"{slot} authority envelope differs")
    expected_family = {
        "relation": RELATION_FAMILY,
        "triangle": TRIANGLE_FAMILY,
    }[slot]
    if value["family"] != expected_family \
            or not isinstance(value["deployment_id"], str) \
            or f"/{slot}/" not in value["deployment_id"]:
        _fail(f"{slot} authority family/deployment slot differs")
    for key in (
            "artifact_sha256", "product_projection_sha256",
            "protocol_decision_sha256", "executable_identity_sha256",
            "native_library_sha256", "target_sha256", "task_semantics_sha256",
            "authority_seal"):
        _sha256(value[key], f"{slot} authority {key}")
    body = dict(value)
    seal = body.pop("authority_seal")
    if seal != _sha(trust.runtime._AUTHORITY_DOMAIN + _canonical(body)):
        _fail(f"{slot} authority seal differs")
    capability = value["target_compute_capability"]
    if not isinstance(capability, list) or len(capability) != 2 \
            or any(type(item) is not int or item < 0 for item in capability):
        _fail(f"{slot} authority compute capability differs")
    return resolved, value, payload


def _authority_entry(value: Mapping[str, Any], payload: bytes) -> dict[str, Any]:
    """Project already-opened authority bytes into the signed-package row."""
    return {
        "deployment_id": value["deployment_id"],
        "family": value["family"],
        "task_semantics_sha256": value["task_semantics_sha256"],
        "authority_sha256": _sha(payload),
        "artifact_sha256": value["artifact_sha256"],
        "executable_identity_sha256": value["executable_identity_sha256"],
        "target_sha256": value["target_sha256"],
        "native_library_sha256": value["native_library_sha256"],
        "compute_capability": value["target_compute_capability"],
    }


def _validate_request(
        request_path: Path, relation_path: Path, triangle_path: Path,
        public_root_path: Path, private_key_path: Path,
        preuse_path: Path) -> tuple[
            dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], int,
            int | None, bytes, bytes]:
    _, request, _ = _strict_json(request_path, "POD trust request")
    expected = {
        "schema", "status", "prepared_state", "source_commit", "source_tree",
        "public_trust_root", "private_key_sha256", "sequence_1", "sequence_2",
        "candidate_double_seed_sha256", "required_package_signatures",
        "required_head_signatures", "private_key_must_never_enter_pod",
        "registered_performance_timing_count", "formal_worker_count",
        "execution_authority_consumed", "request_sha256",
    }
    _exact_keys(request, expected, "POD trust request")
    seal = request["request_sha256"]
    _sha256(seal, "request_sha256")
    body = dict(request)
    body.pop("request_sha256")
    if seal != _digest(body):
        _fail("POD trust request seal differs")
    if request["schema"] != REQUEST_SCHEMA or request["status"] != REQUEST_STATUS:
        _fail("POD trust request envelope differs")
    _sha1(request["source_commit"], "source_commit")
    _sha1(request["source_tree"], "source_tree")
    _sha256(request["candidate_double_seed_sha256"],
            "candidate_double_seed_sha256")
    if request["required_package_signatures"] != 2 \
            or type(request["required_package_signatures"]) is not int \
            or request["required_head_signatures"] != 2 \
            or type(request["required_head_signatures"]) is not int \
            or request["private_key_must_never_enter_pod"] is not True \
            or request["registered_performance_timing_count"] != 0 \
            or type(request["registered_performance_timing_count"]) is not int \
            or request["formal_worker_count"] != 0 \
            or type(request["formal_worker_count"]) is not int \
            or request["execution_authority_consumed"] is not False:
        _fail("POD trust request signing/zero locks differ")
    _request_file_record(request["prepared_state"], "prepared state record")

    _, root, root_payload = _strict_json(public_root_path, "public trust root")
    try:
        verified_root = trust.runtime._read_trust_root(public_root_path.resolve())
    except Exception as error:
        raise OfflineSigningError("public trust root validation failed") from error
    root_record = _request_file_record(
        request["public_trust_root"], "public trust root record")
    _record_matches(root_record, root_payload, "public trust root")

    _, relation, relation_payload = _validate_authority(
        relation_path, "relation")
    _, triangle, triangle_payload = _validate_authority(
        triangle_path, "triangle")
    if relation["deployment_id"] == triangle["deployment_id"] \
            or relation["native_library_sha256"] \
            != triangle["native_library_sha256"] \
            or relation["target_sha256"] != triangle["target_sha256"] \
            or relation["target_compute_capability"] \
            != triangle["target_compute_capability"]:
        _fail("relation/triangle authorities do not share one exact target/native")
    sequence_1 = _exact_keys(
        request["sequence_1"], {"family", "authority", "previous_package_sha256"},
        "sequence 1")
    sequence_2 = _exact_keys(
        request["sequence_2"], {"family", "authority", "previous_sequence"},
        "sequence 2")
    if sequence_1["family"] != "relation" \
            or sequence_1["previous_package_sha256"] is not None \
            or sequence_2["family"] != "triangle" \
            or sequence_2["previous_sequence"] != 1 \
            or type(sequence_2["previous_sequence"]) is not int:
        _fail("POD trust request sequence order differs")
    _record_matches(
        _request_file_record(sequence_1["authority"], "sequence 1 authority record"),
        relation_payload, "relation authority")
    _record_matches(
        _request_file_record(sequence_2["authority"], "sequence 2 authority record"),
        triangle_payload, "triangle authority")

    private_resolved, private_payload = _regular_bytes(private_key_path, "private key")
    private_sha = _sha(private_payload)
    if request["private_key_sha256"] != private_sha:
        _fail("private key differs from the frozen POD request")
    # Validate the private envelope/root match before creating any signed output.
    try:
        trust._private_key(private_resolved, verified_root)
    except Exception as error:
        raise OfflineSigningError("private key/public root validation failed") from error

    _, preuse, preuse_payload = _strict_json(preuse_path, "pre-use custody receipt")
    _enforce_formal_preuse_identity(
        verified_root, preuse_path, preuse_payload)
    try:
        qualification_target = custody._validate_preuse(
            preuse, root_payload=root_payload, root=verified_root,
            preuse_path=preuse_path.resolve(),
            public_root_path=public_root_path.resolve())
        custody._validate_private_key(
            private_resolved, private_payload, root=verified_root, preuse=preuse)
    except Exception as error:
        raise OfflineSigningError("pre-use custody/private-key binding failed") from error
    diagnostic_minimum = preuse.get(
        "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot")
    if type(diagnostic_minimum) is not int or diagnostic_minimum < 0:
        _fail("pre-use custody diagnostic signing minimum differs")
    diagnostic_exact: int | None = None
    if preuse.get(
            "diagnostic_keypair_signing_invocation_count_exactly_attested") \
            is True:
        diagnostic_exact = preuse.get(
            "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot")
        if type(diagnostic_exact) is not int \
                or diagnostic_exact < diagnostic_minimum:
            _fail("pre-use custody exact diagnostic signing count differs")
    if qualification_target is not None:
        expected_capability = list(qualification_target)
        if relation["target_compute_capability"] != expected_capability \
                or triangle["target_compute_capability"] != expected_capability:
            _fail(
                "qualification-only trust key is restricted to the frozen "
                "Home compute capability")
    if _sha(preuse_payload) == private_sha:
        _fail("pre-use receipt unexpectedly equals the private-key bytes")
    return (
        request, relation, triangle, dict(verified_root), diagnostic_minimum,
        diagnostic_exact, relation_payload, triangle_payload,
    )


def _write_new(path: Path, value: object) -> None:
    payload = _canonical(value) + b"\n"
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
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


def _portable_record(path: Path) -> dict[str, object]:
    if path.parent != path.parent.resolve() or path.name != str(path.relative_to(path.parent)):
        _fail("response artifact name is not portable")
    payload = path.read_bytes()
    return {"path": path.name, "bytes": len(payload), "sha256": _sha(payload)}


def _validate_custody_receipt(
        value: object, *, root_payload_sha: str, private_sha: str,
        relation_deployment: str, triangle_deployment: str,
        diagnostic_minimum: int, diagnostic_exact: int | None) -> None:
    outer = {
        "schema", "status", "observed_at_utc_owner_supplied",
        "observation_host_label_owner_supplied", "preuse_custody_receipt",
        "public_root", "materialized_trust_chain", "explicit_actual_counters",
        "private_key_observation", "claim_boundaries",
        "clock_read_count_by_helper", "create_only", "receipt_sha256",
    }
    _exact_keys(value, outer, "post-use custody receipt")
    assert isinstance(value, Mapping)
    if value.get("schema") != custody.SCHEMA \
            or value.get("status") \
            != "TEST_ONLY_POSTUSE_CUSTODY_SNAPSHOT__SIGNED_CHAIN_VERIFIED":
        _fail("post-use custody envelope differs")
    seal = value.get("receipt_sha256")
    body = dict(value)
    body.pop("receipt_sha256", None)
    if not SHA256_RE.fullmatch(str(seal)) or seal != _digest(body):
        _fail("post-use custody seal differs")
    chain = value.get("materialized_trust_chain")
    counters = value.get("explicit_actual_counters")
    private = value.get("private_key_observation")
    claims = value.get("claim_boundaries")
    public = value.get("public_root")
    if not all(isinstance(item, Mapping) for item in (
            chain, counters, private, claims, public)):
        _fail("post-use custody sections are absent")
    _exact_keys(chain, {
        "packages", "heads", "final_head", "materialized_sequence_count",
        "final_deployment_ids", "all_signatures_verified_against_public_root",
    }, "post-use custody chain")
    _exact_keys(public, {
        "role", "path", "bytes", "sha256", "key_id", "trust_root_sha256",
    }, "post-use custody public root")
    _exact_keys(private, {
        "declared_path", "observed_state", "regular_file_observed", "bytes",
        "sha256", "copied_or_embedded_in_receipt",
    }, "post-use custody private observation")
    expected_deployments = sorted((relation_deployment, triangle_deployment))
    packages = chain.get("packages")
    heads = chain.get("heads")
    if not isinstance(packages, list) or not isinstance(heads, list) \
            or chain.get("materialized_sequence_count") != 2 \
            or type(chain.get("materialized_sequence_count")) is not int \
            or len(packages) != 2 or len(heads) != 2 \
            or chain.get("final_deployment_ids") != expected_deployments \
            or chain.get("all_signatures_verified_against_public_root") is not True:
        _fail("post-use custody materialized chain differs")
    if public.get("sha256") != root_payload_sha:
        _fail("post-use custody public-root file identity differs")
    expected_counters = {
        "diagnostic_keypair_signing_invocation_known_minimum": diagnostic_minimum,
        "diagnostic_keypair_signing_invocation_count_exactly_attested": (
            diagnostic_exact is not None),
        "diagnostic_keypair_signing_invocation_exact_count": diagnostic_exact,
        "trust_package_signing_invocation_count": 2,
        "trust_head_signing_invocation_count": 2,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "untimed_gpu_kernel_launch_count": 0,
        "trust_package_signing_invocations_without_preserved_package": 0,
        "trust_head_signing_invocations_without_preserved_head": 0,
    }
    if dict(counters) != expected_counters:
        _fail("post-use custody exact counters differ")
    integer_counters = {
        "diagnostic_keypair_signing_invocation_known_minimum",
        "trust_package_signing_invocation_count",
        "trust_head_signing_invocation_count", "formal_worker_count",
        "registered_performance_timing_count", "untimed_gpu_kernel_launch_count",
        "trust_package_signing_invocations_without_preserved_package",
        "trust_head_signing_invocations_without_preserved_head",
    }
    if diagnostic_exact is not None:
        integer_counters.add(
            "diagnostic_keypair_signing_invocation_exact_count")
    if any(type(counters[key]) is not int for key in integer_counters) \
            or type(counters[
                "diagnostic_keypair_signing_invocation_count_exactly_attested"]) \
            is not bool:
        _fail("post-use custody counter scalar types differ")
    if private.get("observed_state") != custody.PRESENT \
            or private.get("regular_file_observed") is not True \
            or private.get("sha256") != private_sha \
            or private.get("copied_or_embedded_in_receipt") is not False:
        _fail("post-use custody private-key observation differs")
    expected_claims = {
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
    }
    if dict(claims) != expected_claims \
            or any(type(claims[key]) is not bool for key in expected_claims) \
            or value.get("clock_read_count_by_helper") != 0 \
            or type(value.get("clock_read_count_by_helper")) is not int \
            or value.get("create_only") is not True:
        _fail("post-use custody claim boundary differs")


def _validate_response_envelope(value: object) -> None:
    expected = {
        "schema", "status", "request_sha256", "public_trust_root_sha256",
        "package_seq1", "head_seq1", "package_seq2", "head_seq2",
        "custody_receipt", "private_key_sha256", "response_sha256",
    }
    _exact_keys(value, expected, "signed trust response")
    assert isinstance(value, Mapping)
    seal = value["response_sha256"]
    body = dict(value)
    body.pop("response_sha256")
    if value["schema"] != RESPONSE_SCHEMA or value["status"] != RESPONSE_STATUS \
            or not SHA256_RE.fullmatch(str(seal)) or seal != _digest(body):
        _fail("signed trust response envelope/seal differs")
    for label in (
            "package_seq1", "head_seq1", "package_seq2", "head_seq2",
            "custody_receipt"):
        row = _exact_keys(value[label], {"path", "bytes", "sha256"}, label)
        if not isinstance(row["path"], str) or not row["path"] \
                or Path(row["path"]).is_absolute() or "/" in row["path"] \
                or "\\" in row["path"] or row["path"] in {".", ".."} \
                or type(row["bytes"]) is not int or row["bytes"] <= 0 \
                or not SHA256_RE.fullmatch(str(row["sha256"])):
            _fail(f"{label} portable record differs")


def sign_request(args: argparse.Namespace) -> dict[str, Any]:
    request_path = args.request.expanduser().resolve()
    relation_path = args.relation_authority.expanduser().resolve()
    triangle_path = args.triangle_authority.expanduser().resolve()
    root_path = args.public_root.expanduser().resolve()
    private_path = args.private_key.expanduser().resolve()
    preuse_path = args.preuse_custody.expanduser().resolve()
    output = args.output_directory.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    (request, relation, triangle, verified_root, diagnostic_minimum,
     diagnostic_exact, relation_payload, triangle_payload) = _validate_request(
         request_path, relation_path, triangle_path, root_path, private_path,
         preuse_path)
    if not isinstance(args.observed_at_utc, str) or not args.observed_at_utc \
            or not isinstance(args.observation_host_label, str) \
            or not args.observation_host_label.strip():
        _fail("owner-supplied observation time/host label must be nonempty")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    package1 = output / "package_seq1.json"
    head1 = output / "head_seq1.json"
    package2 = output / "package_seq2.json"
    head2 = output / "head_seq2.json"
    receipt_path = output / "custody_receipt.json"
    response_path = output / "signed_trust_response.json"

    # The library function prints a diagnostic summary.  Suppress it so this
    # entrypoint emits exactly one machine-readable public summary of its own.
    # If a signing/write failure occurs, the create-only directory is retained
    # intentionally: a blind rerun would invalidate the exact signing counters.
    with contextlib.redirect_stdout(io.StringIO()):
        trust.freeze(
            private_path=private_path, root_path=root_path,
            authority_path=relation_path, output_path=package1,
            head_output_path=head1, previous_path=None)
        trust.freeze(
            private_path=private_path, root_path=root_path,
            authority_path=triangle_path, output_path=package2,
            head_output_path=head2, previous_path=package1)

    # Reconstruct expected package rows from the already-opened authority bytes,
    # not by reopening the paths.  This turns an authority-path swap between
    # validation and signing into a terminal local failure instead of exporting
    # a chain that merely fails later on the POD.
    try:
        package_1_value, entries_1 = trust.runtime._verify_trust_package(
            package1, root=verified_root)
        package_2_value, entries_2 = trust.runtime._verify_trust_package(
            package2, root=verified_root)
        trust.runtime._verify_trust_head(head1, root=verified_root)
        trust.runtime._verify_trust_head(head2, root=verified_root)
    except Exception as error:
        raise OfflineSigningError("new signed chain failed immediate verification") \
            from error
    expected_relation = _authority_entry(relation, relation_payload)
    expected_triangle = _authority_entry(triangle, triangle_payload)
    if package_1_value["sequence"] != 1 \
            or tuple(entries_1) != (expected_relation,) \
            or package_2_value["sequence"] != 2 \
            or list(entries_2) != sorted(
                (expected_relation, expected_triangle),
                key=lambda row: str(row["deployment_id"])):
        _fail("new signed chain differs from the validated request authorities")

    receipt_args = argparse.Namespace(
        preuse_custody=preuse_path,
        public_root=root_path,
        private_key=private_path,
        private_key_state=custody.PRESENT,
        trust_package=[package1, package2],
        trust_head=[head1, head2],
        expected_deployment_id=[
            str(relation["deployment_id"]), str(triangle["deployment_id"])],
        observed_at_utc=args.observed_at_utc,
        observation_host_label=args.observation_host_label,
        diagnostic_signing_known_minimum=diagnostic_minimum,
        diagnostic_signing_exact_count=diagnostic_exact,
        trust_package_signing_count=2,
        trust_head_signing_count=2,
        formal_worker_count=0,
        registered_timing_count=0,
        untimed_gpu_kernel_launch_count=0,
    )
    receipt = custody.build_receipt(receipt_args)
    private_payload = private_path.read_bytes()
    root_payload = root_path.read_bytes()
    _validate_custody_receipt(
        receipt, root_payload_sha=_sha(root_payload),
        private_sha=_sha(private_payload),
        relation_deployment=str(relation["deployment_id"]),
        triangle_deployment=str(triangle["deployment_id"]),
        diagnostic_minimum=diagnostic_minimum,
        diagnostic_exact=diagnostic_exact)
    _write_new(receipt_path, receipt)

    private_value = json.loads(private_payload.decode("utf-8"))
    private_exponent = str(private_value["rsa_private_exponent_base64"]).encode()
    for path in (package1, head1, package2, head2, receipt_path):
        payload = path.read_bytes()
        if private_payload in payload or private_exponent in payload:
            _fail(f"private key material leaked into response artifact: {path.name}")

    body: dict[str, Any] = {
        "schema": RESPONSE_SCHEMA,
        "status": RESPONSE_STATUS,
        "request_sha256": request["request_sha256"],
        "public_trust_root_sha256": _sha(root_payload),
        "package_seq1": _portable_record(package1),
        "head_seq1": _portable_record(head1),
        "package_seq2": _portable_record(package2),
        "head_seq2": _portable_record(head2),
        "custody_receipt": _portable_record(receipt_path),
        "private_key_sha256": _sha(private_payload),
    }
    response = {**body, "response_sha256": _digest(body)}
    _validate_response_envelope(response)
    _write_new(response_path, response)

    # A private exponent or the complete private-key envelope in any response
    # artifact would be a fatal custody violation.  Public modulus/key-id and
    # the key file SHA are intentionally retained as non-secret identities.
    for path in (response_path,):
        payload = path.read_bytes()
        if private_payload in payload or private_exponent in payload:
            _fail(f"private key material leaked into response artifact: {path.name}")
    return response


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sign one exact Goal5802 POD-S0 TEST_ONLY request offline")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--relation-authority", type=Path, required=True)
    parser.add_argument("--triangle-authority", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--preuse-custody", type=Path, required=True)
    parser.add_argument("--observed-at-utc", required=True)
    parser.add_argument("--observation-host-label", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    response = sign_request(args)
    print(json.dumps({
        "status": response["status"],
        "request_sha256": response["request_sha256"],
        "response_sha256": response["response_sha256"],
        "trust_package_signing_invocation_count": 2,
        "trust_head_signing_invocation_count": 2,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "untimed_gpu_kernel_launch_count_by_signer": 0,
        "execution_authority_consumed": False,
        "private_key_copied_to_response": False,
        "production_authority_claimed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
