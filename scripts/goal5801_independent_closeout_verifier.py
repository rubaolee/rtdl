#!/usr/bin/env python3
"""Independently verify the Goal5801 untimed ``.rtdlexe`` closeout.

This verifier intentionally imports no RTDL module.  It checks the evidence
packet from raw bytes with only the Python standard library: the packet
manifest, RSA trust chain, detached authorities, artifact bindings, the
terminal v1 lineage, the successful v2 result, traversal receipts, lifecycle
locks, fixed device-status observations, and the NVRTC interposition KAT.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from typing import Mapping, Sequence


SCHEMA = "rtdl.goal5801.independent_closeout_verification.v1"
PACKET_SCHEMA = "rtdl.goal5801.local_evidence_manifest.v1"
ARTIFACT_SCHEMA = "rtdl.v4.rtdlexe.v1"
AUTHORITY_SCHEMA = "rtdl.v4.rtdlexe.detached_authority.v1"
TRUST_ROOT_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_root.v1"
TRUST_PACKAGE_SCHEMA = "rtdl.v4.rtdlexe.deployment_trust_package.v1"
TRUST_HEAD_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_head.v1"
AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V1\x00"
TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
TRUST_PACKAGE_DOMAIN = b"RTDL-V4-RTDLEXE-DEPLOYMENT-TRUST-PACKAGE-V1\x00"
TRUST_HEAD_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-HEAD-V1\x00"
DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")
SEMANTIC_PROOF_SHA256 = (
    "88bc8468c78302ed18cb3176e70a6c1dea65bc8306bf5e747bc18dea1e3fac4b"
)
SHA256 = re.compile(r"[0-9a-f]{64}")
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


class VerificationError(RuntimeError):
    """One stable independent-verification failure."""


def _require(condition: object, label: str) -> None:
    if not condition:
        raise VerificationError(label)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest(value: object) -> str:
    return _sha_bytes(_canonical(value))


def _read_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    try:
        return json.loads(raw.decode("utf-8")), raw
    except (UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"{path}: invalid UTF-8 JSON: {error}") from error


def _mapping(value: object, label: str) -> Mapping[str, object]:
    _require(isinstance(value, Mapping), f"{label}: mapping required")
    return value  # type: ignore[return-value]


def _exact_keys(value: Mapping[str, object], keys: set[str], label: str) -> None:
    _require(set(value) == keys, f"{label}: exact keys differ")


def _sha(value: object, label: str) -> str:
    _require(isinstance(value, str) and SHA256.fullmatch(value) is not None,
             f"{label}: lowercase SHA-256 required")
    return value  # type: ignore[return-value]


def _canonical_lf(value: object, raw: bytes, label: str) -> None:
    _require(raw == _canonical(value) + b"\n", f"{label}: canonical JSON plus LF required")


def _strict_b64(value: object, label: str) -> bytes:
    _require(isinstance(value, str), f"{label}: base64 string required")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise VerificationError(f"{label}: invalid base64") from error
    _require(bool(raw), f"{label}: empty base64")
    return raw


def _verify_manifest(root: Path) -> tuple[Mapping[str, object], str]:
    path = root / "manifest.json"
    value, raw = _read_json(path)
    manifest = _mapping(value, "manifest")
    _require(raw == _canonical(manifest), "manifest: canonical JSON required")
    _exact_keys(manifest, {
        "date", "file_count", "files", "private_signing_key_included",
        "schema", "total_payload_bytes",
    }, "manifest")
    _require(manifest["schema"] == PACKET_SCHEMA, "manifest: schema")
    _require(manifest["private_signing_key_included"] is False,
             "manifest: private signing key must be absent")
    rows = manifest["files"]
    _require(isinstance(rows, list), "manifest.files: list required")
    recorded: dict[str, tuple[int, str]] = {}
    observed_order: list[str] = []
    for index, raw_row in enumerate(rows):
        row = _mapping(raw_row, f"manifest.files[{index}]")
        _exact_keys(row, {"bytes", "path", "sha256"}, f"manifest.files[{index}]")
        relative = row["path"]
        _require(isinstance(relative, str), f"manifest.files[{index}].path")
        posix = PurePosixPath(relative)
        _require(not posix.is_absolute() and relative == posix.as_posix()
                 and ".." not in posix.parts and "." not in posix.parts,
                 f"manifest.files[{index}].path: unsafe/noncanonical")
        _require(relative != "manifest.json" and relative not in recorded,
                 f"manifest.files[{index}].path: duplicate/self")
        observed_order.append(relative)
        size = row["bytes"]
        _require(type(size) is int and size >= 0, f"manifest.files[{index}].bytes")
        recorded[relative] = (size, _sha(row["sha256"], f"manifest.files[{index}].sha256"))
    _require(observed_order == sorted(observed_order), "manifest.files: not sorted")
    actual: dict[str, Path] = {}
    for item in root.rglob("*"):
        if not item.is_file() or item == path:
            continue
        _require(not item.is_symlink(), f"packet contains symlink: {item}")
        relative = item.relative_to(root).as_posix()
        actual[relative] = item
    _require(set(actual) == set(recorded), "manifest: payload set differs from directory")
    total = 0
    for relative, item in actual.items():
        payload = item.read_bytes()
        size, expected = recorded[relative]
        _require(len(payload) == size and _sha_bytes(payload) == expected,
                 f"manifest payload mismatch: {relative}")
        total += len(payload)
    _require(manifest["file_count"] == len(recorded), "manifest.file_count")
    _require(manifest["total_payload_bytes"] == total, "manifest.total_payload_bytes")
    return manifest, _sha_bytes(raw)


def _verify_rsa(signature: object, message: bytes, *, modulus: int,
                exponent: int, label: str) -> None:
    raw = _strict_b64(signature, f"{label}.signature_base64")
    width = (modulus.bit_length() + 7) // 8
    _require(len(raw) == width, f"{label}: RSA signature width")
    signature_integer = int.from_bytes(raw, "big")
    _require(signature_integer < modulus, f"{label}: RSA signature out of range")
    encoded = pow(signature_integer, exponent, modulus).to_bytes(width, "big")
    expected_tail = DIGEST_INFO + hashlib.sha256(message).digest()
    padding = width - len(expected_tail) - 3
    _require(padding >= 8, f"{label}: RSA modulus too small")
    expected = b"\x00\x01" + b"\xff" * padding + b"\x00" + expected_tail
    _require(encoded == expected, f"{label}: RSA PKCS#1 v1.5 signature invalid")


def _verify_trust(root: Path) -> tuple[list[Mapping[str, object]], str]:
    trust = root / "test_trust_public"
    root_value, root_raw = _read_json(trust / "root.json")
    certificate = _mapping(root_value, "trust_root")
    _exact_keys(certificate, {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "trust_root_sha256",
    }, "trust_root")
    _canonical_lf(certificate, root_raw, "trust_root")
    _require(certificate["schema"] == TRUST_ROOT_SCHEMA, "trust_root.schema")
    body = dict(certificate); seal = body.pop("trust_root_sha256")
    _require(seal == _sha_bytes(TRUST_ROOT_DOMAIN + _canonical(body)),
             "trust_root: domain-separated seal")
    modulus = int.from_bytes(_strict_b64(
        certificate["rsa_modulus_base64"], "trust_root.rsa_modulus_base64"), "big")
    exponent = certificate["rsa_exponent"]
    _require(type(exponent) is int and exponent >= 3 and exponent % 2 == 1,
             "trust_root.rsa_exponent")
    _require(modulus.bit_length() >= 2048, "trust_root: RSA modulus <2048 bits")

    package_sequences = sorted(
        int(match.group(1))
        for path in trust.glob("package_seq*.json")
        if (match := re.fullmatch(r"package_seq([1-9][0-9]*)\.json", path.name))
    )
    head_sequences = sorted(
        int(match.group(1))
        for path in trust.glob("head_seq*.json")
        if (match := re.fullmatch(r"head_seq([1-9][0-9]*)\.json", path.name))
    )
    _require(package_sequences == head_sequences
             == list(range(1, len(package_sequences) + 1)),
             "trust sequence files must be contiguous from one")
    packages: list[Mapping[str, object]] = []
    previous_entries: list[Mapping[str, object]] = []
    previous_sha: str | None = None
    for sequence in package_sequences:
        package_path = trust / f"package_seq{sequence}.json"
        package_value, package_raw = _read_json(package_path)
        package = _mapping(package_value, f"trust_package[{sequence}]")
        _canonical_lf(package, package_raw, f"trust_package[{sequence}]")
        _exact_keys(package, {
            "schema", "key_id", "sequence", "previous_package_sha256",
            "authorities", "signature_algorithm", "signature_base64",
        }, f"trust_package[{sequence}]")
        _require(package["schema"] == TRUST_PACKAGE_SCHEMA
                 and package["key_id"] == certificate["key_id"]
                 and type(package["sequence"]) is int
                 and package["sequence"] == sequence
                 and package["previous_package_sha256"] == previous_sha
                 and package["signature_algorithm"] == "rsa-pkcs1-v1_5-sha256",
                 f"trust_package[{sequence}]: chain/schema")
        signed = dict(package); signature = signed.pop("signature_base64")
        _verify_rsa(signature, TRUST_PACKAGE_DOMAIN + _canonical(signed),
                    modulus=modulus, exponent=exponent,
                    label=f"trust_package[{sequence}]")
        entries = package["authorities"]
        _require(isinstance(entries, list) and len(entries) == len(previous_entries) + 1,
                 f"trust_package[{sequence}].authorities")
        ids: list[str] = []
        for index, raw_entry in enumerate(entries):
            entry = _mapping(raw_entry, f"trust_package[{sequence}].authorities[{index}]")
            _exact_keys(entry, {
                "deployment_id", "family", "task_semantics_sha256",
                "authority_sha256", "artifact_sha256",
                "executable_identity_sha256", "target_sha256",
                "native_library_sha256", "compute_capability",
            }, f"trust_package[{sequence}].authorities[{index}]")
            for key in ("task_semantics_sha256", "authority_sha256", "artifact_sha256",
                        "executable_identity_sha256", "target_sha256",
                        "native_library_sha256"):
                _sha(entry[key], f"trust entry.{key}")
            _require(isinstance(entry["deployment_id"], str)
                     and isinstance(entry["family"], str), "trust entry strings")
            capability = entry["compute_capability"]
            _require(isinstance(capability, list) and len(capability) == 2
                     and all(type(item) is int and item >= 0 for item in capability),
                     "trust entry.compute_capability")
            ids.append(entry["deployment_id"])  # type: ignore[arg-type]
        _require(ids == sorted(ids) and len(ids) == len(set(ids)),
                 f"trust_package[{sequence}]: authorities not sorted/unique")
        current_by_id = {
            str(_mapping(item, "trust entry")["deployment_id"]): item
            for item in entries
        }
        for prior in previous_entries:
            prior_id = str(prior["deployment_id"])
            _require(current_by_id.get(prior_id) == prior,
                     f"trust_package[{sequence}]: prior authority changed")

        head_value, head_raw = _read_json(trust / f"head_seq{sequence}.json")
        head = _mapping(head_value, f"trust_head[{sequence}]")
        _canonical_lf(head, head_raw, f"trust_head[{sequence}]")
        _exact_keys(head, {
            "schema", "key_id", "current_package_sha256", "current_sequence",
            "signature_algorithm", "signature_base64",
        }, f"trust_head[{sequence}]")
        package_sha = _sha_bytes(package_raw)
        _require(head["schema"] == TRUST_HEAD_SCHEMA
                 and head["key_id"] == certificate["key_id"]
                 and head["current_package_sha256"] == package_sha
                 and type(head["current_sequence"]) is int
                 and head["current_sequence"] == sequence
                 and head["signature_algorithm"] == "rsa-pkcs1-v1_5-sha256",
                 f"trust_head[{sequence}]: binding/schema")
        head_body = dict(head); head_signature = head_body.pop("signature_base64")
        _verify_rsa(head_signature, TRUST_HEAD_DOMAIN + _canonical(head_body),
                    modulus=modulus, exponent=exponent,
                    label=f"trust_head[{sequence}]")
        packages = list(entries)  # last package is controlling
        previous_entries = list(entries)
        previous_sha = package_sha
    return packages, _sha_bytes(root_raw)


def _authority_entry(authority: Mapping[str, object], authority_sha: str) -> dict[str, object]:
    return {
        "deployment_id": authority["deployment_id"],
        "family": authority["family"],
        "task_semantics_sha256": authority["task_semantics_sha256"],
        "authority_sha256": authority_sha,
        "artifact_sha256": authority["artifact_sha256"],
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "target_sha256": authority["target_sha256"],
        "native_library_sha256": authority["native_library_sha256"],
        "compute_capability": authority["target_compute_capability"],
    }


def _verify_artifact_authority(artifact_path: Path, authority_path: Path, *,
                               exact_execution_contract: bool) -> tuple[dict[str, object], int, str]:
    authority_value, authority_raw = _read_json(authority_path)
    authority = _mapping(authority_value, f"authority:{authority_path.name}")
    _canonical_lf(authority, authority_raw, f"authority:{authority_path.name}")
    _exact_keys(authority, {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }, f"authority:{authority_path.name}")
    _require(authority["schema"] == AUTHORITY_SCHEMA
             and type(authority["authority_version"]) is int
             and authority["authority_version"] == 1,
             f"authority:{authority_path.name}: schema/version")
    _require(type(authority["artifact_bytes"]) is int
             and authority["artifact_bytes"] > 0,
             f"authority:{authority_path.name}: artifact_bytes")
    authority_body = dict(authority); seal = authority_body.pop("authority_seal")
    _require(seal == _sha_bytes(AUTHORITY_DOMAIN + _canonical(authority_body)),
             f"authority:{authority_path.name}: seal")
    artifact_raw = artifact_path.read_bytes()
    artifact_sha = _sha_bytes(artifact_raw)
    _require(artifact_sha == authority["artifact_sha256"]
             and len(artifact_raw) == authority["artifact_bytes"]
             and artifact_path.name == f"{artifact_sha}.rtdlexe",
             f"artifact:{artifact_path.name}: content address")
    artifact_value = json.loads(artifact_raw.decode("utf-8"))
    artifact = _mapping(artifact_value, f"artifact:{artifact_path.name}")
    _require(artifact_raw == _canonical(artifact) + b"\n",
             f"artifact:{artifact_path.name}: canonical bytes")
    _exact_keys(artifact, {
        "schema", "format_version", "product_projection", "protocol_declaration",
        "compiler_projection", "protocol_decision", "composed_ptx_base64",
    }, f"artifact:{artifact_path.name}")
    _require(artifact["schema"] == ARTIFACT_SCHEMA
             and type(artifact["format_version"]) is int
             and artifact["format_version"] == 1,
             f"artifact:{artifact_path.name}: schema/version")

    declaration = _mapping(artifact["protocol_declaration"], "protocol_declaration")
    projection = _mapping(artifact["compiler_projection"], "compiler_projection")
    decision = _mapping(artifact["protocol_decision"], "protocol_decision")
    product = _mapping(artifact["product_projection"], "product_projection")
    declaration_body = dict(declaration); declaration_seal = declaration_body.pop("contract_sha256")
    projection_body = dict(projection); projection_seal = projection_body.pop("projection_sha256")
    decision_body = dict(decision); decision_seal = decision_body.pop("decision_sha256")
    _require(declaration_seal == _digest(declaration_body), "protocol declaration seal")
    _require(projection_seal == _digest(projection_body), "compiler projection seal")
    _require(decision_seal == _digest(decision_body), "protocol decision seal")
    _require(decision["verdict"] == "ACCEPT" and decision["findings"] == []
             and decision["executable_capability_issued"] is False
             and decision["contract_sha256"] == declaration_seal
             and decision["projection_sha256"] == projection_seal
             and decision_seal == authority["protocol_decision_sha256"],
             "protocol decision binding")
    _require(_digest(product) == authority["product_projection_sha256"],
             "product projection binding")
    identity = _mapping(product["executable_identity"], "product.executable_identity")
    _require(_digest(identity) == authority["executable_identity_sha256"],
             "executable identity binding")
    target = _mapping(product["target_toolchain"], "product.target_toolchain")
    _require(product["deployment_id"] == authority["deployment_id"]
             and product["family"] == authority["family"] == declaration["family"] == projection["family"]
             and declaration["task_semantics_sha256"] == authority["task_semantics_sha256"]
             and target["native_library_sha256"] == authority["native_library_sha256"]
             and target["target_sha256"] == authority["target_sha256"]
             and target["compute_capability"] == authority["target_compute_capability"],
             "artifact/authority semantic binding")
    ptx = _strict_b64(artifact["composed_ptx_base64"], "artifact.composed_ptx_base64")
    ptx_sha = _sha_bytes(ptx)
    _require(ptx_sha == product["composed_ptx_sha256"]
             == projection["generated_device_source_sha256"]
             == identity["composed_ptx_sha256"], "composed PTX binding")

    execution = _mapping(product["execution_schema"], "product.execution_schema")
    execution_body = dict(execution); execution_seal = execution_body.pop("execution_schema_sha256")
    _require(execution_seal == _digest(execution_body), "execution schema seal")
    inputs = _mapping(execution["producer_inputs"], "execution.producer_inputs")
    expected_names = {"module", "program_group", "pipeline", "sbt", "launch_parameters", "status"}
    _require(set(inputs) == expected_names, "execution producer input names")
    digest_keys = {
        "module": "module_schema_sha256", "program_group": "program_group_schema_sha256",
        "pipeline": "pipeline_schema_sha256", "sbt": "sbt_schema_sha256",
        "launch_parameters": "launch_parameter_schema_sha256",
        "status": "status_schema_sha256",
    }
    contract_mismatches = 0
    for name in sorted(expected_names):
        row = _mapping(inputs[name], f"execution.producer_inputs.{name}")
        _require(_digest(row) == execution[digest_keys[name]],
                 f"execution.producer_inputs.{name}: digest")
        if row.get("contract_sha256") != declaration_seal:
            contract_mismatches += 1
    descriptor = _mapping(execution["native_producer_descriptor"], "native descriptor")
    _require(_digest(descriptor) == execution["native_producer_descriptor_sha256"],
             "native producer descriptor digest")
    if exact_execution_contract:
        _require(contract_mismatches == 0, "execution producer contract chain drift")
    return (
        _authority_entry(authority, _sha_bytes(authority_raw)),
        contract_mismatches,
        ptx_sha,
    )


def _verify_candidates(root: Path, trusted: Sequence[Mapping[str, object]]) -> dict[str, object]:
    proof = root / "semantic_proof" / "semantic_spec.json"
    _require(_sha_bytes(proof.read_bytes()) == SEMANTIC_PROOF_SHA256,
             "semantic proof identity")
    native_by_version = {
        "v9": _sha_bytes((root / "native" / "librtdl_optix.so").read_bytes()),
        "v10": _sha_bytes((root / "native" / "librtdl_optix.so").read_bytes()),
    }
    if (root / "native_final_v11" / "librtdl_optix.so").is_file():
        native_by_version["v11"] = _sha_bytes(
            (root / "native_final_v11" / "librtdl_optix.so").read_bytes())
    all_trusted_entries: list[dict[str, object]] = []
    semantic_digests_by_version: dict[str, dict[str, str]] = {}
    v9_mismatches = 0
    version_directories: dict[str, list[Path]] = {
        "v9": [root / "candidates_v9"],
        "v10": [root / "candidates_v10"],
    }
    v11_directories = [
        root / f"candidate_v11_seed{seed}" for seed in ("1", "777", "2026")
    ]
    if all(path.is_dir() for path in v11_directories):
        version_directories["v11"] = v11_directories
    for version, directories in version_directories.items():
        seed_identities: list[dict[str, object]] = []
        first_entries: list[dict[str, object]] = []
        first_semantics: dict[str, str] = {}
        for directory in directories:
            manifest_value, _ = _read_json(directory / "candidate_manifest.json")
            candidate = _mapping(manifest_value, f"candidate_manifest.{directory.name}")
            _require(candidate["schema"] == "rtdl.goal5801.lx1_untimed_candidate_manifest.v1"
                     and candidate["status"] == "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED"
                     and candidate["registered_timing_count"] == 0
                     and candidate["native_sha256"] == native_by_version[version]
                     and candidate["proof_sha256"] == SEMANTIC_PROOF_SHA256,
                     f"candidate_manifest.{directory.name}: fixed roots")
            rows = _mapping(candidate["candidates"], f"candidate_manifest.{directory.name}.candidates")
            _require(set(rows) == {"relation", "triangle"},
                     f"candidate_manifest.{directory.name}: labels")
            identity: dict[str, object] = {}
            current_entries: list[dict[str, object]] = []
            current_semantics: dict[str, str] = {}
            for label in ("relation", "triangle"):
                row = _mapping(rows[label], f"candidate_manifest.{directory.name}.{label}")
                artifact_sha = _sha(
                    row["artifact_sha256"], f"candidate.{directory.name}.{label}.artifact")
                entry, mismatches, ptx_sha = _verify_artifact_authority(
                    directory / "artifacts" / f"{artifact_sha}.rtdlexe",
                    directory / f"{label}.authority.json",
                    exact_execution_contract=version != "v9")
                _require(Path(str(row["artifact_path"])).name == f"{artifact_sha}.rtdlexe"
                         and Path(str(row["authority_path"])).name == f"{label}.authority.json"
                         and row["authority_sha256"] == entry["authority_sha256"]
                         and row["deployment_id"] == entry["deployment_id"]
                         and row["executable_identity_sha256"] == entry["executable_identity_sha256"],
                         f"candidate_manifest.{directory.name}.{label}: authority row")
                identity[label] = {
                    "artifact_sha256": artifact_sha,
                    "authority_sha256": entry["authority_sha256"],
                    "deployment_id": entry["deployment_id"],
                    "executable_identity_sha256": entry["executable_identity_sha256"],
                    "ptx_sha256": ptx_sha,
                }
                current_entries.append(entry)
                current_semantics[label] = _digest({
                    "artifact": entry["executable_identity_sha256"],
                    "ptx": ptx_sha,
                    "native": native_by_version[version],
                })
                if version == "v9":
                    v9_mismatches += mismatches
            seed_identities.append(identity)
            if not first_entries:
                first_entries = current_entries
                first_semantics = current_semantics
        _require(all(item == seed_identities[0] for item in seed_identities),
                 f"candidate {version}: hash-seed identities differ")
        if version != "v9":
            all_trusted_entries.extend(first_entries)
            semantic_digests_by_version[version] = first_semantics
    all_trusted_entries.sort(key=lambda item: str(item["deployment_id"]))
    _require(all_trusted_entries == list(trusted),
             "controlling trust package != ordered v10/v11 authorities")
    _require(v9_mismatches == 12, "v9 lineage must retain six producer drifts per artifact")
    return {
        "semantic_proof_sha256": SEMANTIC_PROOF_SHA256,
        "native_sha256": native_by_version["v11" if "v11" in native_by_version else "v10"],
        "native_sha256_by_version": native_by_version,
        "trusted_authority_count": len(all_trusted_entries),
        "v9_producer_contract_mismatch_count": v9_mismatches,
        "v11_hash_seed_reproduction_count": len(version_directories.get("v11", [])),
        "execution_semantic_digests_by_version": semantic_digests_by_version,
    }


def _fnv1a(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _verify_receipt(receipt_value: object, *, output_sha: str, native_sha: str,
                    semantic_sha: str, bundle: str, route: str,
                    launches: int, raygen: int) -> None:
    receipt = _mapping(receipt_value, f"receipt:{route}")
    body = dict(receipt); seal = body.pop("receipt_sha256")
    _require(seal == _digest(body), f"receipt:{route}: seal")
    snapshot = _mapping(receipt["native_snapshot"], f"receipt:{route}.native_snapshot")
    expected_bundle_id = _fnv1a(bundle)
    _require(receipt["schema"] == "rtdl.physical_execution.traversal_receipt.v1"
             and receipt["provider_library"] == "librtdl_optix"
             and receipt["provider_library_sha256"] == native_sha
             and receipt["route_identity"] == route
             and receipt["semantic_digest"] == semantic_sha
             and receipt["output_digest"] == output_sha
             and receipt["physical_executor_classification"] == "optix_traversal_observed"
             and receipt["expected_program_bundles"] == [bundle]
             and receipt["expected_program_bundle_ids"] == [expected_bundle_id]
             and receipt["expected_program_observed_at_receipt_edge"] is True,
             f"receipt:{route}: outer facts")
    _require(receipt["claim_rules"] == {
        "provider_name_alone_proves_traversal": False,
        "selected_template_alone_proves_traversal": False,
        "successful_optix_launch_required": True,
        "nonzero_traversable_binding_required": True,
        "program_bundle_binding_required": True,
        "output_digest_bound": True,
    }, f"receipt:{route}: claim rules")
    nonce = _mapping(receipt["nonce"], f"receipt:{route}.nonce")
    _require(snapshot["nonce_hi"] == nonce["hi"] and snapshot["nonce_lo"] == nonce["lo"],
             f"receipt:{route}: nonce")
    _require(snapshot["attempted_launch_count"] == launches
             and snapshot["successful_launch_count"] == launches
             and snapshot["complete_context_launch_count"] == launches
             and snapshot["context_bind_count"] == launches
             and snapshot["raygen_invocation_count"] == raygen
             and snapshot["failed_launch_count"] == 0
             and snapshot["incomplete_context_launch_count"] == 0
             and snapshot["pending_context_at_finish"] == 0
             and snapshot["session_error"] == 0
             and snapshot["incomplete_callsite_record_count"] == 0
             and snapshot["first_program_bundle_id"] == expected_bundle_id
             and snapshot["last_program_bundle_id"] == expected_bundle_id
             and snapshot["first_traversable"] != 0
             and snapshot["last_traversable"] != 0,
             f"receipt:{route}: native traversal facts")


def _verify_status(value: object, *, rows: int, terminal_mask: int,
                   reused: bool, triangle: bool) -> None:
    status = _mapping(value, "device_status")
    required = {
        "schema", "ok", "first_error_claimed", "error_code",
        "validated_row_count", "invalid_row_count", "required_invocation_mask",
        "terminal_invocation_mask", "success_status_d2h_bytes",
        "prepared_input_reused",
    }
    if triangle:
        required |= {"success_event_count_d2h_bytes", "success_scalar_d2h_bytes",
                     "success_total_product_d2h_bytes"}
    _exact_keys(status, required, "device_status")
    _require(status["schema"] == "rtdl.v4.fixed_device_status.v2"
             and status["ok"] is True
             and status["first_error_claimed"] == 0
             and status["error_code"] == 0
             and status["validated_row_count"] == rows
             and status["invalid_row_count"] == 0
             and status["required_invocation_mask"] == 66
             and status["terminal_invocation_mask"] == terminal_mask
             and status["success_status_d2h_bytes"] == 112
             and status["prepared_input_reused"] is reused,
             "device_status: fixed success facts")
    if triangle:
        _require(status["success_event_count_d2h_bytes"] == 8
                 and status["success_scalar_d2h_bytes"] == 32
                 and status["success_total_product_d2h_bytes"] == 152,
                 "device_status: triangle product transfer facts")


def _verify_v1_terminal(root: Path) -> None:
    evidence = root / "evidence_v1"
    _require((evidence / "lifecycle.exit_code").read_bytes() == b"1\n",
             "v1 lifecycle exit must be 1")
    _require((evidence / "lifecycle.stdout").read_bytes() == b"",
             "v1 lifecycle stdout must be empty")
    stderr = (evidence / "lifecycle.stderr").read_text(encoding="utf-8")
    _require("RX052_EXECUTION_SCHEMA_INVALID" in stderr
             and "execution_schema.producer_inputs.launch_parameters" in stderr
             and "producer chain drift" in stderr,
             "v1 terminal reason")
    _require((evidence / "nvrtc_kat.exit_code").read_bytes() == b"97\n"
             and (evidence / "nvrtc_kat.log").read_bytes() == b"nvrtcCreateProgram\n"
             and (evidence / "nvrtc_kat.stdout").read_bytes() == b""
             and (evidence / "nvrtc_kat.stderr").read_bytes() == b""
             and (evidence / "nvrtc_lifecycle.log").read_bytes() == b"",
             "v1 NVRTC KAT/lifecycle trap")


def _verify_v3_calibration_failure(root: Path) -> None:
    evidence = root / "evidence_v3"
    if not evidence.is_dir():
        return
    _require((evidence / "nvrtc_kat.exit_code").read_bytes() == b"0\n"
             and (evidence / "nvrtc_kat.expected").read_bytes()
                == b"nvrtcCreateProgram\n"
             and not (evidence / "nvrtc_kat.log").exists()
             and (evidence / "nvrtc_kat.stdout").read_bytes() == b""
             and (evidence / "nvrtc_kat.stderr").read_bytes() == b""
             and (evidence / "nvrtc_lifecycle.log").read_bytes() == b"",
             "v3 calibrated-trap harness failure lineage")


def _verify_postrun_closeout(root: Path) -> dict[str, object]:
    versions = sorted(
        (int(match.group(1)), path)
        for path in root.glob("postrun_closeout_v*") if path.is_dir()
        if (match := re.fullmatch(r"postrun_closeout_v([1-9][0-9]*)", path.name))
    )
    _require(bool(versions), "postrun closeout receipt is absent")
    _require([item[0] for item in versions] == list(range(1, versions[-1][0] + 1)),
             "postrun closeout versions are not contiguous")
    _, closeout = versions[-1]
    captured = (closeout / "captured_at_utc.txt").read_text(encoding="ascii").strip()
    _require(re.fullmatch(r"2026-08-24T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", captured) is not None,
             "postrun capture timestamp")
    query = (closeout / "nvidia_smi_query.txt").read_text(encoding="utf-8").strip().split(", ")
    _require(len(query) == 4 and query[0] == "NVIDIA GeForce GTX 1070"
             and query[1].startswith("GPU-") and query[2] == "580.126.09"
             and query[3] == "6.1", "postrun GPU/driver/CC receipt")
    _require((closeout / "python_version.txt").read_text(encoding="ascii").strip()
             == "Python 3.12.3", "postrun Python receipt")
    _require((closeout / "uname.txt").read_text(encoding="utf-8").startswith("Linux lx1 "),
             "postrun machine receipt")
    _require("release 12.0, V12.0.140" in
             (closeout / "nvcc_version.txt").read_text(encoding="utf-8"),
             "postrun NVCC receipt")

    core_rows: dict[str, str] = {}
    for line in (closeout / "closeout_core.sha256").read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        core_rows[Path(name).name] = _sha(digest, "postrun closeout core")
    _require(core_rows.get("librtdl_optix.so") ==
             _sha_bytes((root / "native" / "librtdl_optix.so").read_bytes())
             and core_rows.get("goal5801_nvrtc_forbidden_preload.so") ==
             _sha_bytes((root / "native" / "goal5801_nvrtc_forbidden_preload.so").read_bytes()),
             "postrun native/preload core identity")
    archive = closeout / "exact_postrun_source_snapshot.tar.gz"
    _require(core_rows.get(archive.name) == _sha_bytes(archive.read_bytes()),
             "postrun source archive identity")

    source_rows: dict[str, str] = {}
    source_manifest = (closeout / "postrun_source_manifest.sha256").read_text(
        encoding="utf-8").splitlines()
    for line in source_manifest:
        digest, name = line.split("  ", 1)
        posix = PurePosixPath(name)
        _require(not posix.is_absolute() and ".." not in posix.parts
                 and name == posix.as_posix() and name not in source_rows,
                 "postrun source manifest path")
        source_rows[name] = _sha(digest, f"postrun source:{name}")
    _require(list(source_rows) == sorted(source_rows), "postrun source manifest not sorted")
    archived: dict[str, str] = {}
    with tarfile.open(archive, "r:gz") as stream:
        for member in stream.getmembers():
            posix = PurePosixPath(member.name)
            _require(not posix.is_absolute() and ".." not in posix.parts
                     and member.name == posix.as_posix(),
                     "postrun source archive unsafe path")
            _require(member.isdir() or member.isfile(),
                     "postrun source archive contains link/special member")
            if member.isfile():
                _require(member.name not in archived, "postrun source archive duplicate")
                handle = stream.extractfile(member)
                _require(handle is not None, "postrun source archive unreadable member")
                archived[member.name] = _sha_bytes(handle.read())
    _require(archived == source_rows, "postrun source archive/manifest mismatch")
    return {
        "postrun_receipt_directory": closeout.name,
        "postrun_capture_is_after_execution_not_in_timer": True,
        "postrun_gpu_name": query[0],
        "postrun_compute_capability": query[3],
        "postrun_driver_version": query[2],
        "postrun_source_archive_sha256": _sha_bytes(archive.read_bytes()),
        "postrun_source_file_count": len(source_rows),
    }


def _sha_listing(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        parts = line.split("  ", 1)
        _require(len(parts) == 2, f"{path.name}[{index}]: SHA listing framing")
        rows.append((_sha(parts[0], f"{path.name}[{index}]"), parts[1]))
    _require(bool(rows), f"{path.name}: empty SHA listing")
    return rows


def _verify_v11_custody(root: Path) -> dict[str, object]:
    closeout = root / "successor_v11_final"
    if not closeout.is_dir():
        return {"v11_custody_present": False}
    archive = closeout / "exact_prebuild_source_snapshot.tar.gz"
    snapshot_rows = _sha_listing(closeout / "exact_prebuild_source_snapshot.sha256")
    _require(len(snapshot_rows) == 1
             and snapshot_rows[0][0] == _sha_bytes(archive.read_bytes())
             and Path(snapshot_rows[0][1]).name == archive.name,
             "v11 exact prebuild source snapshot identity")
    source_rows = {
        name: digest
        for digest, name in _sha_listing(
            closeout / "exact_prebuild_source_manifest.sha256")
    }
    _require(len(source_rows) >= 500, "v11 prebuild source manifest is not complete enough")
    essentials = {
        "scripts/goal5801_lx1_untimed_smoke.py",
        "scripts/goal5801_rtdlexe_trust.py",
        "src/rtdsl/v4_rtdlexe.py",
        "src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py",
        "src/native/optix/rtdl_optix_core.cpp",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        "tests/goal5801_rtdlexe_runtime_test.py",
    }
    _require(essentials <= set(source_rows), "v11 prebuild source essentials absent")
    archived: dict[str, str] = {}
    with tarfile.open(archive, "r:gz") as stream:
        for member in stream.getmembers():
            posix = PurePosixPath(member.name)
            _require(not posix.is_absolute() and ".." not in posix.parts
                     and member.name == posix.as_posix(),
                     "v11 prebuild source archive unsafe path")
            _require(member.isdir() or member.isfile(),
                     "v11 prebuild source archive contains link/special member")
            if member.isfile():
                _require(member.name not in archived, "v11 prebuild source archive duplicate")
                handle = stream.extractfile(member)
                _require(handle is not None, "v11 prebuild source member unreadable")
                archived[member.name] = _sha_bytes(handle.read())
    _require(archived == source_rows, "v11 prebuild source archive/manifest mismatch")

    native_command = (closeout / "native_build_command.txt").read_text(encoding="utf-8").strip()
    native_stdout = (closeout / "native_build.stdout").read_text(encoding="utf-8")
    _require((closeout / "native_build.exit_code").read_bytes() == b"0\n"
             and (closeout / "native_build.stderr").read_bytes() == b""
             and "build_goal5801_final_v1" in native_command
             and "RTDL_OPTIX_BUILD_ID=goal5801_final_canonical_v1" in native_command
             and "OPTIX_CUDA_ARCH=sm_61" in native_command
             and native_command.endswith(" build-optix")
             and "/usr/bin/nvcc -std=c++17 -O3 -shared" in native_stdout
             and '-DRTDL_OPTIX_BUILD_ID=\\"goal5801_final_canonical_v1\\"' in native_stdout
             and "-arch=sm_61" in native_stdout
             and "src/native/rtdl_optix.cpp" in native_stdout
             and "src/native/optix/rtdl_optix_cuda_helpers.cu" in native_stdout
             and native_stdout.rstrip().endswith(
                 "-o build_goal5801_final_v1/librtdl_optix.so"),
             "v11 native build command/exit")
    final_binary_paths = {
        "librtdl_optix.so": root / "native_final_v11" / "librtdl_optix.so",
        "goal5801_nvrtc_forbidden_preload.so":
            root / "native_final_v11" / "goal5801_nvrtc_forbidden_preload.so",
        "goal5801_nvrtc_positive_kat":
            root / "native_final_v11" / "goal5801_nvrtc_positive_kat",
    }
    for digest, remote in _sha_listing(closeout / "final_binaries.sha256"):
        local = final_binary_paths.get(Path(remote).name)
        _require(local is not None and _sha_bytes(local.read_bytes()) == digest,
                 "v11 final binary identity")

    seed_identity: list[list[tuple[str, str]]] = []
    for seed in ("1", "777", "2026"):
        prefix = f"candidate_seed{seed}"
        command = (closeout / f"{prefix}.command").read_text(encoding="utf-8").strip()
        _require((closeout / f"{prefix}.exit_code").read_bytes() == b"0\n"
                 and (closeout / f"{prefix}.stderr").read_bytes() == b""
                 and command.startswith(f"PYTHONHASHSEED={seed} ")
                 and " --deployment-generation v2 " in command
                 and "build_goal5801_final_v1/librtdl_optix.so" in command
                 and f"--output /home/lestat/work/goal5801_rtdlexe_lx1_20260824_v1/candidate_v11_seed{seed}" in command,
                 f"v11 candidate seed {seed} command/exit")
        directory = root / f"candidate_v11_seed{seed}"
        candidate_stdout, candidate_stdout_raw = _read_json(
            closeout / f"{prefix}.stdout")
        candidate_manifest, _ = _read_json(directory / "candidate_manifest.json")
        _require(candidate_stdout == candidate_manifest
                 and candidate_stdout_raw.endswith(b"\n"),
                 f"v11 candidate seed {seed} stdout/manifest")
        identity = []
        for relative in ("relation.authority.json", "triangle.authority.json"):
            identity.append((relative, _sha_bytes((directory / relative).read_bytes())))
        for artifact in sorted((directory / "artifacts").glob("*.rtdlexe")):
            identity.append((artifact.name, _sha_bytes(artifact.read_bytes())))
        seed_identity.append(identity)
    _require(seed_identity[0] == seed_identity[1] == seed_identity[2],
             "v11 three-seed candidate bytes differ")
    _require((closeout / "candidate_reproducibility.status").read_text(
        encoding="ascii").strip()
        == "PASS__THREE_HASH_SEEDS_ARTIFACTS_AND_AUTHORITIES_BYTE_IDENTICAL",
        "v11 candidate reproducibility status")
    for digest, remote in _sha_listing(closeout / "candidate_reproducibility.sha256"):
        parts = PurePosixPath(remote).parts
        marker = next((index for index, item in enumerate(parts)
                       if item.startswith("candidate_v11_seed")), None)
        _require(marker is not None, "v11 candidate reproducibility path")
        local = root.joinpath(*parts[marker:])
        _require(_sha_bytes(local.read_bytes()) == digest,
                 "v11 candidate reproducibility listed hash")

    for sequence, label in ((3, "relation"), (4, "triangle")):
        prefix = f"trust_seq{sequence}"
        command = (closeout / f"{prefix}.command").read_text(encoding="utf-8").strip()
        _require((closeout / f"{prefix}.exit_code").read_bytes() == b"0\n"
                 and (closeout / f"{prefix}.stderr").read_bytes() == b""
                 and f"/{label}.authority.json" in command
                 and f"package_seq{sequence}.json" in command
                 and f"head_seq{sequence}.json" in command
                 and f"--previous /home/lestat/work/goal5801_rtdlexe_lx1_20260824_v1/test_trust_v4/package_seq{sequence - 1}.json" in command,
                 f"v11 trust seq{sequence} command/exit")
        trust_stdout_value, trust_stdout_raw = _read_json(
            closeout / f"{prefix}.stdout")
        trust_stdout = _mapping(trust_stdout_value, f"v11 trust seq{sequence} stdout")
        trust_package_value, _ = _read_json(
            root / "test_trust_public" / f"package_seq{sequence}.json")
        trust_package = _mapping(
            trust_package_value, f"v11 trust package seq{sequence}")
        package_authorities = trust_package["authorities"]
        _require(trust_stdout_raw.endswith(b"\n")
                 and type(trust_stdout["sequence"]) is int
                 and trust_stdout["sequence"] == sequence
                 and type(trust_stdout["authority_count"]) is int
                 and isinstance(package_authorities, list)
                 and trust_stdout["authority_count"] == len(package_authorities)
                 and trust_stdout["deployment_id"] == f"goal5801/lx1/{label}/v2"
                 and trust_stdout["production_key_custody_attested"] is False
                 and trust_stdout["trust_package_sha256"] == _sha_bytes(
                     (root / "test_trust_public" / f"package_seq{sequence}.json").read_bytes())
                 and trust_stdout["trust_head_sha256"] == _sha_bytes(
                     (root / "test_trust_public" / f"head_seq{sequence}.json").read_bytes()),
                 f"v11 trust seq{sequence} stdout/files")
    for digest, remote in _sha_listing(closeout / "trust_chain.sha256"):
        local = root / "test_trust_public" / Path(remote).name
        _require(_sha_bytes(local.read_bytes()) == digest, "v11 trust chain listed hash")

    build_commands = {
        "preload_build": (
            "scripts/goal5801_nvrtc_forbidden_preload.c",
            "build_goal5801_final_v1/goal5801_nvrtc_forbidden_preload.so"),
        "nvrtc_kat_build": (
            "scripts/goal5801_nvrtc_positive_kat.c",
            "build_goal5801_final_v1/goal5801_nvrtc_positive_kat"),
    }
    for prefix, (source_name, output_name) in build_commands.items():
        command = (closeout / f"{prefix}.command").read_text(
            encoding="utf-8").strip()
        _require((closeout / f"{prefix}.exit_code").read_bytes() == b"0\n",
                 f"v11 {prefix} exit")
        _require(command.startswith("cc -std=c11 -O2 ")
                 and source_name in command and command.endswith(output_name),
                 f"v11 {prefix} command")
    for digest, remote in _sha_listing(closeout / "preload_build.sha256") \
            + _sha_listing(closeout / "nvrtc_kat_build.sha256"):
        local = final_binary_paths.get(Path(remote).name)
        _require(local is not None and _sha_bytes(local.read_bytes()) == digest,
                 "v11 preload/KAT build identity")
    lifecycle_command = (closeout / "lifecycle_v4.command").read_text(
        encoding="utf-8").strip()
    _require("RTDL_GOAL5801_NVRTC_TRAP_LOG=" in lifecycle_command
             and " LD_PRELOAD=" in lifecycle_command
             and "/evidence_v4/nvrtc_lifecycle.log" in lifecycle_command
             and "/candidate_v11_seed1/candidate_manifest.json" in lifecycle_command
             and "/test_trust_v4/head_seq4.json" in lifecycle_command
             and "/test_trust_v4/package_seq4.json" in lifecycle_command
             and "/build_goal5801_final_v1/librtdl_optix.so" in lifecycle_command
             and lifecycle_command.endswith("/evidence_v4/lifecycle_result.json"),
             "v11 controlling lifecycle command/env")
    for digest, remote in _sha_listing(closeout / "evidence_lineages.sha256"):
        parts = PurePosixPath(remote).parts
        marker = next((index for index, item in enumerate(parts)
                       if item in {"evidence_v3", "evidence_v4"}), None)
        _require(marker is not None, "v11 evidence lineage path")
        local = root.joinpath(*parts[marker:])
        _require(_sha_bytes(local.read_bytes()) == digest,
                 "v11 evidence lineage listed hash")
    environment = closeout / "postrun_environment"
    query = (environment / "nvidia_smi_query.txt").read_text(
        encoding="utf-8").strip().split(", ")
    _require(len(query) == 4 and query[0] == "NVIDIA GeForce GTX 1070"
             and query[2] == "580.126.09" and query[3] == "6.1"
             and (environment / "uname.txt").read_text(encoding="utf-8").startswith("Linux lx1 ")
             and (environment / "python_version.txt").read_text(
                 encoding="ascii").strip() == "Python 3.12.3",
             "v11 postrun environment")
    source_snapshot = root / "source_snapshot"
    verifier_source = Path(__file__).resolve()
    verifier_test_source = verifier_source.parents[1] / "tests" / (
        "goal5801_independent_closeout_verifier_test.py")
    _require(verifier_test_source.is_file(),
             "local independent verifier test source absent")
    _require(
        (source_snapshot / "scripts" /
         "goal5801_independent_closeout_verifier.py").read_bytes()
        == verifier_source.read_bytes(),
        "postrun source snapshot does not contain this exact verifier")
    _require(
        (source_snapshot / "tests" /
         "goal5801_independent_closeout_verifier_test.py").read_bytes()
        == verifier_test_source.read_bytes(),
        "postrun source snapshot does not contain the exact verifier test")
    return {
        "v11_custody_present": True,
        "v11_prebuild_source_archive_sha256": _sha_bytes(archive.read_bytes()),
        "v11_prebuild_source_file_count": len(source_rows),
        "v11_postrun_verifier_and_test_source_bound": True,
        "v11_candidate_hash_seed_count": 3,
        "v11_native_build_exit_zero": True,
        "v11_native_build_stdout_sha256": _sha_bytes(
            (closeout / "native_build.stdout").read_bytes()),
        "v11_candidate_build_exit_zero_count": 3,
        "v11_trust_append_count": 2,
        "v11_auxiliary_build_exit_zero_count": 2,
        "v11_lifecycle_command_bound": True,
    }


def _verify_success_result(evidence: Path, *, native_sha: str,
                           semantic_digests: Mapping[str, str]) -> dict[str, object]:
    result_value, result_raw = _read_json(evidence / "lifecycle_result.json")
    result = _mapping(result_value, "lifecycle_result")
    stdout_value, stdout_raw = _read_json(evidence / "lifecycle.stdout")
    _require(stdout_value == result and stdout_raw.endswith(b"\n"),
             "v2 lifecycle stdout/result mismatch")
    _require((evidence / "lifecycle.exit_code").read_bytes() == b"0\n",
             "v2 lifecycle exit must be 0")
    stderr = (evidence / "lifecycle.stderr").read_text(encoding="utf-8")
    _require("Traceback" not in stderr and "RuntimeError" not in stderr
             and "RTDLExecutableError" not in stderr,
             "v2 lifecycle stderr contains failure")
    _require(result["schema"] == "rtdl.goal5801.lx1_untimed_functional_result.v1"
             and result["status"] == "PASS__TWO_FAMILY_PUBLIC_RTDLEXE_LIFECYCLES"
             and result["registered_timing_count"] == 0
             and result["performance_claim_authorized"] is False
             and result["rt_core_claim_authorized"] is False,
             "v2 result scope/status")
    for key in ("cache_hit_forbidden_imports_after_load",
                "cache_hit_forbidden_imports_after_close", "cache_hit_attempted_imports",
                "cache_hit_attempted_processes", "cache_hit_attempted_libraries"):
        _require(result[key] == [], f"v2 result {key}")
    _require(result["native_compiler_attempts_before"] == 0
             and result["native_compiler_attempts_after"] == 0
             and result["nvrtc_preload_trap_bytes"] == 0,
             "v2 frontend/codegen/NVRTC counters")

    context = _mapping(result["cuda_context_preservation"], "cuda_context_preservation")
    events = [
        "relation.prepare", "relation.execute.initial", "relation.execute.repeat",
        "relation.execute.changed", "relation.close", "triangle.prepare",
        "triangle.execute.initial", "triangle.execute.repeat",
        "triangle.execute.changed", "triangle.close",
    ]
    _require(context == {
        "null_reducer_probe_cases": 12,
        "null_preserved_after_all_reducer_probes": True,
        "foreign_boundary_events": events,
        "foreign_boundary_event_count": 10,
        "foreign_preserved_after_every_boundary": True,
        "final_context_is_null": True,
    }, "CUDA context preservation KAT")
    matrix = result["compiled_product_status_reducer_matrix"]
    _require(isinstance(matrix, list) and len(matrix) == 12,
             "compiled reducer matrix size")
    for case_id, raw_row in enumerate(matrix):
        row = _mapping(raw_row, f"reducer[{case_id}]")
        good = case_id in {0, 9}
        _require(row == {
            "case_id": case_id,
            "ok": good,
            "error_code": 0 if good else 0xFFFF5001,
            "invalid_row_count": 0 if good else 1,
        }, f"compiled reducer[{case_id}]")

    relation = _mapping(result["relation"], "relation")
    triangle = _mapping(result["triangle"], "triangle")
    _require(relation["output"] == [[10, 100]], "relation output")
    relation_sha = _digest(relation["output"])
    triangle_sha = _digest(7)
    _require(relation["output_sha256"] == relation_sha, "relation output digest")
    _require(triangle["output"] == 7 and triangle["output_sha256"] == triangle_sha,
             "triangle output/digest")
    _verify_status(relation["device_status"], rows=4, terminal_mask=48,
                   reused=False, triangle=False)
    _verify_status(relation["repeat_device_status"], rows=4, terminal_mask=48,
                   reused=True, triangle=False)
    _verify_status(relation["changed_device_status"], rows=3, terminal_mask=48,
                   reused=False, triangle=False)
    _verify_status(triangle["device_status"], rows=1, terminal_mask=32,
                   reused=False, triangle=True)
    _verify_status(triangle["repeat_device_status"], rows=1, terminal_mask=32,
                   reused=True, triangle=True)
    _verify_status(triangle["changed_device_status"], rows=1, terminal_mask=32,
                   reused=False, triangle=True)
    _require(relation["role_counters"] == [2, 4, 2, 2, 2, 2, 4],
             "relation role counters")
    _require(triangle["role_counters"] == [0, 1, 0, 1, 0, 1, 1],
             "triangle role counters")
    _require(relation["process_boundary"] == "RX038_PROCESS_BOUNDARY"
             and relation["reentrant"] == "RX040_REENTRANT"
             and relation["use_after_close"] == "RX037_USE_AFTER_CLOSE"
             and triangle["use_after_close"] == "RX037_USE_AFTER_CLOSE",
             "public lifecycle locks")
    _verify_receipt(
        relation["traversal_receipt"], output_sha=relation_sha, native_sha=native_sha,
        semantic_sha=semantic_digests["relation"],
        bundle="v4_custom_aabb_bounded_relation_composed",
        route="v4_callback_ir:custom_aabb_bounded_relation_v1", launches=2, raygen=4)
    _verify_receipt(
        triangle["traversal_receipt"], output_sha=triangle_sha, native_sha=native_sha,
        semantic_sha=semantic_digests["triangle"],
        bundle="v4_builtin_triangle_checked_reduction_composed",
        route="v4_builtin_triangle_callback_ir:checked_reduction_v1", launches=1, raygen=1)

    expected = (evidence / "nvrtc_kat.expected").read_bytes()
    kat_log = (evidence / "nvrtc_kat.log").read_bytes()
    _require(bool(expected) and expected == kat_log == b"nvrtcCreateProgram\n"
             and (evidence / "nvrtc_kat.exit_code").read_bytes() == b"97\n"
             and (evidence / "nvrtc_kat.stdout").read_bytes() == b""
             and (evidence / "nvrtc_kat.stderr").read_bytes() == b""
             and (evidence / "nvrtc_lifecycle.log").read_bytes() == b"",
             "v2 NVRTC positive KAT / empty lifecycle trap")
    return {
        "evidence_directory": evidence.name,
        "lifecycle_result_sha256": _sha_bytes(result_raw),
        "output_digest_count": 2,
        "fixed_status_observation_count": 6,
        "context_boundary_count": 10,
        "compiled_reducer_case_count": 12,
        "lifecycle_lock_count": 4,
        "nvrtc_positive_kat": True,
        "nvrtc_lifecycle_trap_empty": True,
    }


def verify(root: Path) -> dict[str, object]:
    root = root.resolve()
    _require(root.is_dir(), "packet root is not a directory")
    manifest, manifest_sha = _verify_manifest(root)
    trusted, trust_root_sha = _verify_trust(root)
    candidate = _verify_candidates(root, trusted)
    _verify_v1_terminal(root)
    _verify_v3_calibration_failure(root)
    postrun = _verify_postrun_closeout(root)
    v11_custody = _verify_v11_custody(root)
    semantic_by_version = _mapping(
        candidate.pop("execution_semantic_digests_by_version"),
        "execution_semantic_digests_by_version")
    native_by_version = _mapping(
        candidate.pop("native_sha256_by_version"), "native_sha256_by_version")
    evidence_results: list[dict[str, object]] = []
    for version, evidence_name in (("v10", "evidence_v2"), ("v11", "evidence_v4")):
        evidence = root / evidence_name
        if evidence.is_dir():
            semantic = _mapping(semantic_by_version[version], f"semantic:{version}")
            evidence_results.append(_verify_success_result(
                evidence, native_sha=str(native_by_version[version]),
                semantic_digests=semantic,  # type: ignore[arg-type]
            ))
    _require(bool(evidence_results), "no successful lifecycle evidence")
    result = dict(evidence_results[-1])
    result["successful_lifecycle_evidence_count"] = len(evidence_results)
    result["successful_lifecycle_result_sha256s"] = [
        item["lifecycle_result_sha256"] for item in evidence_results
    ]
    result["v3_calibrated_trap_harness_failure_preserved"] = (
        root / "evidence_v3").is_dir()
    return {
        "schema": SCHEMA,
        "status": "PASS__INDEPENDENT_RAW_CLOSEOUT_VERIFICATION",
        "packet_manifest_sha256": manifest_sha,
        "packet_file_count": manifest["file_count"],
        "packet_payload_bytes": manifest["total_payload_bytes"],
        "trust_root_file_sha256": trust_root_sha,
        **candidate,
        **result,
        **postrun,
        **v11_custody,
        "imports_rtdsl": False,
        "registered_timing_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet_root", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.packet_root)
    except (OSError, KeyError, TypeError, ValueError, VerificationError) as error:
        print(json.dumps({
            "schema": SCHEMA,
            "status": "FAIL__INDEPENDENT_RAW_CLOSEOUT_VERIFICATION",
            "error": str(error),
        }, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
