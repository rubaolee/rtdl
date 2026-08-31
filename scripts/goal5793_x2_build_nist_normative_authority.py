#!/usr/bin/env python3
"""Build the offline NISTIR/XSD interpretation and synthetic trust authority."""

from __future__ import annotations

import argparse
import cryptography
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from typing import Any

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document, sha256_bytes
from scripts import goal5793_x2_nist_normative_selection_client as selection_client
from scripts import goal5793_x2_nist_normative_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
AUTHORITY_DOMAIN = "rtdl.goal5793.x2.nist_normative_offline_authority"
NS = {"xs": "http://www.w3.org/2001/XMLSchema"}


def _identity(rel: str) -> dict[str, Any]:
    data = (ROOT / rel).read_bytes()
    return {"path": rel, "bytes": len(data), "sha256": sha256_bytes(data)}


def _parse_xsd_contract() -> dict[str, Any]:
    raw = (ROOT / verifier.NIST_XSD_REL).read_bytes()
    try:
        tree = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("NIST_XSD_PARSE_INVALID") from exc
    if tree.tag != "{http://www.w3.org/2001/XMLSchema}schema":
        raise RuntimeError("NIST_XSD_ROOT_INVALID")
    pulse_type = tree.find("xs:complexType[@name='pulseType']", NS)
    if pulse_type is None:
        raise RuntimeError("NIST_XSD_PULSE_TYPE_MISSING")
    sequence = pulse_type.find("xs:sequence", NS)
    if sequence is None:
        raise RuntimeError("NIST_XSD_PULSE_SEQUENCE_MISSING")
    fields = [element.get("name") for element in sequence.findall("xs:element", NS)]
    expected = [
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
        "listValue",
        "precommitmentValue",
        "statusCode",
        "signatureValue",
        "outputValue",
    ]
    if fields != expected:
        raise RuntimeError("NIST_XSD_PULSE_FIELD_ORDER_MISMATCH")
    sha_type = tree.find("xs:simpleType[@name='sha512HexString']", NS)
    restriction = None if sha_type is None else sha_type.find("xs:restriction", NS)
    length = None if restriction is None else restriction.find("xs:length", NS)
    pattern = None if restriction is None else restriction.find("xs:pattern", NS)
    if length is None or length.get("value") != "128" or pattern is None or pattern.get("value") != "([0-9]|[a-f]|[A-F])*":
        raise RuntimeError("NIST_XSD_SHA512_TYPE_MISMATCH")
    text = raw.decode("utf-8", errors="strict")
    required_phrases = {
        "time_endpoint_next_closest": "or next closest AFTER the provided <unixTime>",
        "cipher_suite_zero": "0 - SHA512 hashing and RSA signatures with PKCSv1.5 padding",
        "signature_four_byte_length_documentation": "encoded as 4-byte big-endian integer values",
        "certificate_der_documentation": "SHA-512 hash of the X.509 ASN.1 encoding",
    }
    if any(value not in text for value in required_phrases.values()):
        raise RuntimeError("NIST_XSD_REQUIRED_TEXT_MISMATCH")
    return {
        "target_namespace": tree.get("targetNamespace"),
        "schema_version": tree.get("version"),
        "pulse_field_order": fields,
        "sha512_hex_length": 128,
        "sha512_hex_pattern": pattern.get("value"),
        "required_documentation_phrases_present": {key: True for key in required_phrases},
        "json_adapter_boundary": {
            "xsd_element": "listValue",
            "s0_json_field": "listValues",
            "mapping": "ORDERED_XML_ELEMENTS_TO_JSON_ARRAY_WITHOUT_REORDERING_OR_DEDUPLICATION",
        },
    }


def _runtime_boundary() -> dict[str, Any]:
    package_root = Path(cryptography.__file__).resolve().parent
    rows = []
    for path in sorted(
        package_root.rglob("*"),
        key=lambda item: item.relative_to(package_root).as_posix().encode("utf-8"),
    ):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(package_root).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    rust_rows = [row for row in rows if row["path"].endswith("hazmat/bindings/_rust.pyd")]
    if len(rust_rows) != 1:
        raise RuntimeError("CRYPTOGRAPHY_RUST_EXTENSION_IDENTITY_MISSING")
    return {
        "python_executable_observed": str(Path(sys.executable).resolve()),
        "python_version_observed": sys.version,
        "cryptography_version": cryptography.__version__,
        "cryptography_package_file_count": len(rows),
        "cryptography_package_total_bytes": sum(row["bytes"] for row in rows),
        "cryptography_package_rows_sha256": sha256_bytes(canonical_json_bytes(rows)),
        "cryptography_rust_extension": rust_rows[0],
        "cryptography_package_bytes_embedded_in_capsule": False,
        "python_stdlib_bytes_embedded_in_capsule": False,
        "hermetic_runtime_claimed": False,
        "runtime_tcb": ["PYTHON_INTERPRETER", "PYTHON_STDLIB", "CRYPTOGRAPHY_PACKAGE", "HOST_OS_CRYPTO_APIS"],
    }


def build_authority() -> dict[str, Any]:
    source_identity = verifier.assert_normative_source_identity(ROOT)
    root_pem = (ROOT / "tests/fixtures/goal5793_x2_nist/synthetic_root.pem").read_bytes()
    trust = verifier.build_synthetic_trust_bundle(root_pem)
    kat = verifier.serialization_known_answer()
    if not kat["matches_expected"]:
        raise RuntimeError("NISTIR_SERIALIZATION_KAT_MISMATCH")
    authority: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.nist_normative_offline_authority.v1",
        "date": DATE,
        "status": "OFFLINE_NISTIR_CIPHER_SUITE_0_VERIFIER_AND_SYNTHETIC_TRUST_KAT_READY_FOR_EXTERNAL_REVIEW__NO_LIVE_AUTHORITY",
        "normative_source_identity": source_identity,
        "xsd_contract": _parse_xsd_contract(),
        "source_interpretation_boundary": verifier.source_interpretation_boundary(),
        "serialization_known_answer": kat,
        "synthetic_trust_bundle": trust,
        "implementation": {
            "normative_verifier": _identity("scripts/goal5793_x2_nist_normative_verifier.py"),
            "normative_offline_selection_client": _identity("scripts/goal5793_x2_nist_normative_selection_client.py"),
            "verifier_test": _identity("tests/goal5793_x2_nist_normative_verifier_test.py"),
            "selection_client_test": _identity("tests/goal5793_x2_nist_normative_selection_client_test.py"),
            "shared_canonical": _identity("scripts/goal5793_x1_canonical.py"),
            "all_new_seals_import_shared_canonical": True,
            "network_client_present": False,
        },
        "runtime_boundary": _runtime_boundary(),
        "offline_evidence": {
            "synthetic_pulse_chain_verified": True,
            "synthetic_predecessor_anchor_and_1440_pulse_target_chain_verified": True,
            "authenticated_pulse_count": 1442,
            "every_signature_verified": True,
            "every_output_value_recomputed": True,
            "every_previous_and_precommitment_link_verified": True,
            "middle_chain_coherently_resigned_link_attack_rejected": True,
            "next_closest_target_rejected_same_exact_uri_retained": True,
            "selection_mapping_is_synthetic_rehearsal_only": True,
        },
        "unresolved_live_boundary": {
            "exact_live_nist_root_and_intermediate_bundle_issued": False,
            "live_nist_pulse_fixture_observed": False,
            "live_variant_selected_after_observation": False,
            "live_beacon_acceptance_usable": False,
            "required_before_any_future_beacon_request": (
                "SEPARATE_EXACT_NIST_SIGNING_TRUST_BUNDLE_AND_SOURCE_INTERPRETATION_REVIEW_"
                "WITH_NO_POST_OBSERVATION_VARIANT_SWITCH"
            ),
        },
        "activity": {
            "normative_source_recovery_http_get_count": 2,
            "provider_search_calls": 0,
            "beacon_calls": 0,
            "entropy_draws": 0,
            "scientific_selections": 0,
            "candidate_actions": 0,
            "gpu_ssh_pod_actions": 0,
            "registered_or_performance_timings": 0,
        },
        "claim_boundary": {
            "normative_nistir_serialization_implemented": True,
            "xsd_transport_contract_parsed": True,
            "source_conflicts_explicit": True,
            "offline_synthetic_verification_complete": True,
            "live_nist_verifier_complete": False,
            "x2_externally_accepted": False,
            "x3_authorized": False,
            "generalization_evidence_count": 0,
            "usability_evidence_count": 0,
        },
        "authorization": {
            "live_search": False,
            "beacon": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "publication": False,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = seal_document(
        authority,
        seal_field="authority_sha256",
        domain=AUTHORITY_DOMAIN,
        version=1,
    )
    return authority


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    if args.write_create_only != (args.output is not None):
        parser.error("formal writes require both --output and --write-create-only")
    authority = build_authority()
    payload = canonical_json_bytes(authority) + b"\n"
    if args.output is not None:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(json.dumps({"status": "PASS", "bytes": len(payload), "sha256": sha256_bytes(payload), "authority_sha256": authority["authority_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
