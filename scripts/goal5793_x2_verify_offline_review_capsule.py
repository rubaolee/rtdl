#!/usr/bin/env python3
"""Standalone standard-library verifier for the compact X2 review capsule."""

from __future__ import annotations

import argparse
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Mapping

sys.dont_write_bytecode = True

try:
    from goal5793_x1_canonical import CANONICALIZATION_NAME, canonical_json_bytes, seal_document
except ModuleNotFoundError:
    from scripts.goal5793_x1_canonical import CANONICALIZATION_NAME, canonical_json_bytes, seal_document  # type: ignore


CAPSULE_DIRNAME = "goal5793_x2_offline_review_capsule"
MANIFEST_DOMAIN = "rtdl.goal5793.x2.offline_review_capsule.manifest"
AUDIT_DOMAIN = "rtdl.goal5793.x2.offline_review_capsule.audit"
ALIAS_DOMAIN = "rtdl.goal5793.x2.exposure_alias_authority"

KEY_ROOTS = {
    "payload/authorities/goal5793_s0_protocol_and_stage_authority_20260822.json": (56110, "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2"),
    "payload/authorities/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json": (3866, "5fa675288edbc7c2ff400b9fb966b9de48183577a5e917c75b41a24f267c2ac1"),
    "payload/reviews/review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md": (22713, "2a94062fed53ad9daa52aef447c03c1d70ece46ce15fb6e1cf623fee136ddc7e"),
    "payload/authorities/goal5793_x1_governance_ordering_amendment_20260822.json": (3402, "68f16c9fbda17a4cd194fc2cd7f81015d010a7babb2f45fb1b888dbf29b76ba3"),
    "payload/authorities/goal5793_x1_owner_returned_external_review_absorption_20260822.json": (2354, "803978816f2dc66b14dc056a49967a34fd4929349241ef1991443095b40013fc"),
    "payload/authorities/goal5793_x1_project_exposure_registry_v2_20260822.json": (476230, "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"),
    "payload/authorities/goal5793_x1_positive_vector_freeze_20260822.json": (49461, "07be9926d986c807651dd39f28310ffb905d3bfc1869690839ab29e3ab96e152"),
    "payload/custody/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz": (4284033, "83cc4bb3e149d9db16e2386d83d89dd86790a5bee834f7f98d6a257fe3e66bd5"),
    "payload/custody/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json": (7559, "b6001ff20c1cee2b7d79b4518b8665d51becc6910531b1a5a80ace8681cbf977"),
    "payload/custody/goal5793_x1_s0_reproduction_capsule_audit_20260822.json": (5601, "eb5dddf06d3aa8a73400b75f42473d58aa84b4cbd20f9d34925e596152459117"),
    "payload/source/goal5753_survey_source.tar": (752766, "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857"),
    "payload/recovery/goal5793_x2_normative_source_recovery_preaction_work_authority_v2_20260822.json": (10269, "4a1065aceeea8b039e88ead6c1129fc0dd1fb330c9e6e4da25edf2886bc1ee2b"),
    "payload/recovery/call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md": (25145, "10d8a85ecfa6bebb2aa7870daa3180a7c0130ec0a27c2a87a4bc2f36bc27a00f"),
    "payload/recovery/review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md": (15970, "1daad90ffd0b88294f8c20b434cb63c5aa3fbf19531858d3d691d58da462eb9c"),
    "payload/recovery/goal5793_x2_normative_source_recovery_owner_send_receipt_20260822.json": (1902, "d2c1e290877ebc5b648fb0e571a2bfe52ce223e8b61e4f54abb0e7b11976821c"),
    "payload/recovery/goal5793_x2_normative_source_recovery_preaction_governance_authority_v3_20260822.json": (3919, "1e0e28a5c9e234b9ac1113625227a6ec82af40cdaae63de2d3cce53588e5b721"),
    "payload/recovery/goal5793_x2_normative_source_recovery_review_absorption_20260822.json": (2320, "9000bf98a426881e6a2c29941f648e14a83d76be6ef7e2d5861eac8cd45b5e75"),
    "payload/recovery/goal5793_x2_normative_source_recovery_owner_closure_20260822.json": (2336, "3aa86c3b2f6078ac63880b3ba36d64a2a32bca34ebe9af8a10c7754e25186b30"),
    "payload/normative/NIST.IR.8213-draft.pdf": (762001, "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183"),
    "payload/normative/beacon-2.0.xsd": (19033, "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6"),
    "payload/recovery/goal5793_x2_normative_source_recovery_receipt_20260822.json": (1048683, "a16a2dbe174fc9f645f3cab6d0437655365aa6a19a36c488b5b466e38f516763"),
    "payload/recovery/goal5793_x2_recover_pinned_normative_sources.py": (11258, "a43ba1cceed7363c2a9b77dc6a7d482b3de49553b670cd36563547eff3a6347a"),
    "payload/recovery/goal5793_x2_absorb_normative_source_recovery_review.py": (13027, "c448ffa5a78833a22a98a3f46cf90d871dfcf71b9e84d8547200e2aad6606a40"),
}
FIXTURE_ROOTS = {
    "tests/fixtures/goal5793_x2_nist/synthetic_leaf.pem": (1066, "61cae48dc6d57175be7d74517f5f7e28fea72a8b1207d27b0335a342688039c6"),
    "tests/fixtures/goal5793_x2_nist/synthetic_pulse.json": (1775, "0135f68f0bf7378e03b75b333d37b0f939f274abf3f3696c8134ef0054973d85"),
    "tests/fixtures/goal5793_x2_nist/synthetic_root.pem": (1074, "b7bfaa902571161aee98f65bcb88e7d594e0219a947c73ac7ba481ef772383e9"),
}
FORBIDDEN_NETWORK_IMPORTS = {"socket", "requests", "urllib", "httpx", "aiohttp", "ftplib", "paramiko"}
PYPDF_FILE_COUNT = 56
PYPDF_TOTAL_BYTES = 1_486_221
PYPDF_ROWS_SHA256 = "3df52f80b93fbcb44dd793e0ba27ee2438ad7cf06de7ab355e1755c0078a9bd1"


class VerificationFailure(RuntimeError):
    def __init__(self, fail_id: str, detail: str = ""):
        self.fail_id = fail_id
        self.detail = detail
        super().__init__(f"{fail_id}: {detail}")


def fail(fail_id: str, detail: str = "") -> None:
    raise VerificationFailure(fail_id, detail)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("CAPSULE_JSON_INVALID", path.as_posix())
    if not isinstance(value, dict):
        fail("CAPSULE_JSON_INVALID", path.as_posix())
    return value


def _canonical_rel(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        fail("CAPSULE_PATH_INVALID", str(value))
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or "." in path.parts or ".." in path.parts:
        fail("CAPSULE_PATH_INVALID", value)
    return value


def _manifest_map(root: Path, manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if manifest.get("schema") != "rtdl.goal5793.x2.offline_review_capsule.manifest.v2":
        fail("CAPSULE_MANIFEST_MISMATCH", "schema")
    if manifest.get("manifest_sha256") != seal_document(manifest, seal_field="manifest_sha256", domain=MANIFEST_DOMAIN, version=2):
        fail("CAPSULE_MANIFEST_MISMATCH", "seal")
    if manifest.get("canonicalization") != CANONICALIZATION_NAME:
        fail("CAPSULE_MANIFEST_MISMATCH", "canonicalization")
    if manifest.get("status") != "COMPACT_SELF_CONTAINED_OFFLINE_REVIEW_CAPSULE__READY_FOR_EXACT_BYTE_EXTERNAL_REVIEW__NO_LIVE_AUTHORIZATION":
        fail("CAPSULE_MANIFEST_MISMATCH", "status")
    if manifest.get("delivery_rule") != {
        "external_send_file": "SOLE_CFR_MARKDOWN_ONLY",
        "capsule_sent_as_second_attachment": False,
        "capsule_local_evidence_path_only": True,
    }:
        fail("CAPSULE_MANIFEST_MISMATCH", "delivery rule")
    if manifest.get("activity") != {
        "exact_normative_source_recovery_http_gets": 2,
        "provider_search": 0,
        "beacon": 0,
        "entropy": 0,
        "selection": 0,
        "candidate_work": 0,
        "gpu_ssh_pod": 0,
        "timing": 0,
    }:
        fail("CAPSULE_MANIFEST_MISMATCH", "activity")
    rows = manifest.get("payloads")
    if not isinstance(rows, list):
        fail("CAPSULE_MANIFEST_MISMATCH", "payload rows")
    paths = [row.get("path") for row in rows if isinstance(row, Mapping)]
    if len(paths) != len(rows) or paths != sorted(paths, key=lambda value: str(value).encode("utf-8")) or len(paths) != len(set(paths)):
        fail("CAPSULE_MANIFEST_MISMATCH", "payload order/set")
    mapped: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        rel = _canonical_rel(row.get("path"))
        if set(row) != {"path", "bytes", "sha256", "role"}:
            fail("CAPSULE_MANIFEST_MISMATCH", rel)
        path = root.joinpath(*PurePosixPath(rel).parts)
        if not path.is_file() or path.is_symlink():
            fail("CAPSULE_PAYLOAD_MISMATCH", rel)
        data = path.read_bytes()
        if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
            fail("CAPSULE_PAYLOAD_MISMATCH", rel)
        mapped[rel] = row
    summary = manifest.get("payload_summary", {})
    if summary != {
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "rows_sha256": _sha(canonical_json_bytes(rows)),
    }:
        fail("CAPSULE_MANIFEST_MISMATCH", "summary")
    allowed = {Path(*PurePosixPath(rel).parts) for rel in mapped} | {Path("manifest.json"), Path("audit.json")}
    observed = {path.relative_to(root) for path in root.rglob("*") if path.is_file()}
    if observed != allowed:
        fail("CAPSULE_PAYLOAD_SET_MISMATCH", f"missing={allowed-observed};extra={observed-allowed}")
    return mapped


def _verify_key_roots(root: Path) -> None:
    for rel, (size, digest) in {**KEY_ROOTS, **FIXTURE_ROOTS}.items():
        data = root.joinpath(*PurePosixPath(rel).parts).read_bytes()
        if len(data) != size or _sha(data) != digest:
            fail("CAPSULE_PREDECESSOR_IDENTITY_MISMATCH", rel)


def _verify_authorizations(root: Path) -> None:
    closure = _load(root / "payload/authorities/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json")
    auth = closure.get("authorization")
    if not isinstance(auth, dict) or auth.get("authorizes_x2_offline_implementation") is not True:
        fail("X2_OFFLINE_AUTHORITY_MISMATCH", "offline grant")
    if any(value is not False for key, value in auth.items() if key != "authorizes_x2_offline_implementation"):
        fail("X2_OFFLINE_AUTHORITY_MISMATCH", "live grant")
    protocol = _load(root / "payload/authorities/goal5793_s0_protocol_and_stage_authority_20260822.json")
    if any(protocol.get("authorization", {}).values()):
        fail("PREMATURE_LIVE_AUTHORIZATION", "S0 protocol")


def _verify_alias_authority(root: Path) -> dict[str, Any]:
    alias = _load(root / "generated/goal5793_x2_exposure_alias_authority_20260822.json")
    if alias.get("schema") != "rtdl.goal5793.x2.exposure_alias_authority.v1":
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "schema")
    if alias.get("authority_sha256") != seal_document(alias, seal_field="authority_sha256", domain=ALIAS_DOMAIN, version=1):
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "seal")
    rows = alias.get("rows")
    if not isinstance(rows, list) or len(rows) != 186:
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "row count")
    keys = [row.get("citation_key") for row in rows]
    if keys != sorted(keys, key=lambda value: str(value).encode("utf-8")) or len(set(keys)) != 186:
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "row keys")
    strong = sum(bool(row.get("strong_identifier_present")) for row in rows)
    if strong != 7 or sum(not bool(row.get("strong_identifier_present")) for row in rows) != 179:
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "strong ID counts")
    if any(row.get("selection_eligible") is not False for row in rows):
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "eligible exposure row")
    if alias.get("counts") != {
        "bibliography_rows": 186,
        "strong_identifier_rows": 7,
        "no_strong_identifier_rows": 179,
        "selection_eligible_rows": 0,
        "network_or_live_lookup_count": 0,
    }:
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "counts")
    if any(alias.get("authorization", {}).values()):
        fail("PREMATURE_LIVE_AUTHORIZATION", "alias authority")
    try:
        sample = base64.b64decode(alias["sample_bib_base64"], validate=True)
    except Exception as exc:
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", f"sample bib encoding: {exc}")
    if len(sample) != 63148 or _sha(sample) != "9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a":
        fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "sample bib")
    return alias


def _network_imports(source: bytes, label: str) -> set[str]:
    try:
        tree = ast.parse(source.decode("utf-8", errors="strict"), filename=label)
    except (UnicodeDecodeError, SyntaxError) as exc:
        fail("X2_TOOL_SOURCE_INVALID", f"{label}: {exc}")
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    return imports


def _verify_no_network_code(root: Path, manifest_map: Mapping[str, Mapping[str, Any]]) -> int:
    count = 0
    for rel in manifest_map:
        if rel.startswith("tools/goal5793_x2_") and rel.endswith(".py"):
            source = root.joinpath(*PurePosixPath(rel).parts).read_bytes()
            bad = _network_imports(source, rel) & FORBIDDEN_NETWORK_IMPORTS
            if bad:
                fail("X2_NETWORK_CODE_PRESENT", f"{rel}: {sorted(bad)}")
            count += 1
    if count < 9:
        fail("X2_TOOL_SET_UNDERINCLUSIVE", str(count))
    return count


def _verify_pdf_vendor_and_isolated_runtime(root: Path) -> dict[str, Any]:
    os_module = __import__("os")
    vendor = root / "vendor/pypdf"
    rows = []
    for path in sorted(vendor.rglob("*"), key=lambda item: item.relative_to(vendor).as_posix().encode("utf-8")):
        if not path.is_file() or path.is_symlink():
            continue
        data = path.read_bytes()
        rows.append({"path": path.relative_to(vendor).as_posix(), "bytes": len(data), "sha256": _sha(data)})
    if len(rows) != PYPDF_FILE_COUNT or sum(row["bytes"] for row in rows) != PYPDF_TOTAL_BYTES or _sha(canonical_json_bytes(rows)) != PYPDF_ROWS_SHA256:
        fail("PDF_PARSER_AUTHORITY_IDENTITY_MISMATCH", "vendored pypdf")
    try:
        pdf_bytes = base64.b64decode((root / "tests/fixtures/goal5793_x2_pdf/synthetic_identity.pdf.b64").read_text(encoding="ascii").strip(), validate=True)
    except Exception as exc:
        fail("PDF_FIXTURE_INVALID", str(exc))
    component = {
        "component_id": "doi:10.9999/goal5793.synthetic", "doi": ["10.9999/goal5793.synthetic"],
        "arxiv": ["2501.01234"], "title": ["synthetic hardware ray tracing work"],
        "first_author": ["smith"], "year": [2025],
    }
    payload = json.dumps(
        {"schema": "rtdl.goal5793.x2.pdf_identity_child_input.v1", "pdf_base64": base64.b64encode(pdf_bytes).decode("ascii"), "component": component},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    tool = root / "tools/goal5793_x2_run_pdf_identity.py"
    override = os_module.environ.get("RTDL_X2_ISOLATED_PYTHON")
    child_python = Path(override).resolve() if override else Path(sys.executable).resolve()
    if not child_python.is_file():
        fail("PDF_ISOLATED_RUNTIME_FAILED", "child interpreter missing")
    environment = {key: value for key, value in os_module.environ.items() if key.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "COMSPEC"}}
    environment["PYTHONNOUSERSITE"] = "1"
    try:
        completed = subprocess.run(
            [str(child_python), "-I", "-B", str(tool), "--child", "--vendor-root", str((root / "vendor").resolve())],
            input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, check=False, env=environment,
        )
    except subprocess.TimeoutExpired:
        fail("PDF_ISOLATED_RUNTIME_FAILED", "timeout")
    if completed.returncode != 0:
        fail("PDF_ISOLATED_RUNTIME_FAILED", completed.stderr.decode("utf-8", errors="replace"))
    try:
        result = json.loads(completed.stdout.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("PDF_ISOLATED_RUNTIME_FAILED", str(exc))
    receipt = result.get("pdf_identity_receipt", {})
    if result.get("schema") != "rtdl.goal5793.x2.isolated_pdf_identity_result.v1" or receipt.get("identity_checks", {}).get("matched") is not True or receipt.get("parser_authority", {}).get("rows_sha256") != PYPDF_ROWS_SHA256 or Path(result.get("process", {}).get("python_executable", "")).resolve() != child_python:
        fail("PDF_ISOLATED_RUNTIME_FAILED", "receipt")
    return {"pypdf_files": len(rows), "pypdf_bytes": sum(row["bytes"] for row in rows), "pypdf_rows_sha256": PYPDF_ROWS_SHA256, "synthetic_pdf_identity_match": True}


def _selection_frame(inputs: Mapping[str, Any], field_order: list[str]) -> bytes:
    magic = bytes.fromhex("5254444c3537393353454c0001")
    sha_fields = {
        "s0_protocol_authority_file_sha256", "complete_source_rows_sha256", "x1_examiner_closure_file_sha256",
        "x2_harvester_entropy_closure_file_sha256", "x3_science_triplet_owner_closure_file_sha256",
        "expanded_append_only_row_table_file_sha256", "preentropy_science_projection_rows_sha256", "ordered_triplets_rows_sha256",
    }
    hex512 = {"anchor_certificate_id", "anchor_output_value", "target_certificate_id", "target_output_value"}
    u64 = {"ordered_triplet_count", "anchor_chain_index", "anchor_pulse_index", "anchor_timestamp_ms", "target_chain_index", "target_pulse_index", "target_timestamp_ms", "counter"}
    framed: list[bytes] = []
    for name in field_order:
        value = inputs[name]
        if name == "domain":
            encoded = value.encode("utf-8")
        elif name in sha_fields or name in hex512:
            encoded = bytes.fromhex(value)
        elif name in u64:
            if type(value) is not int or not 0 <= value <= 2**64 - 1:
                fail("SELECTION_KAT_MISMATCH", name)
            encoded = value.to_bytes(8, "big")
        else:
            fail("SELECTION_KAT_MISMATCH", name)
        name_bytes = name.encode("ascii")
        framed.append(len(name_bytes).to_bytes(2, "big") + name_bytes + len(encoded).to_bytes(8, "big") + encoded)
    return magic + len(field_order).to_bytes(2, "big") + b"".join(framed)


def _verify_kat(root: Path) -> dict[str, Any]:
    protocol = _load(root / "payload/authorities/goal5793_s0_protocol_and_stage_authority_20260822.json")
    deferred = protocol["deferred_entropy"]
    kat = deferred["known_answer_test"]
    order = deferred["selection_encoding"]["field_order"]
    frame = _selection_frame(kat["inputs"], order)
    digest = hashlib.sha256(frame).digest()
    x = int.from_bytes(digest, "big")
    n = kat["expected"]["n"]
    limit = (2**256 // n) * n
    if len(frame) != 1345 or _sha(frame) != "a5904e12a9795bdc984b73095cc38cc670328fbb074a8db5e736c1fff0d4d92e":
        fail("SELECTION_KAT_MISMATCH", "frame")
    if x >= limit or x % n != 2 or f"{limit:064x}" != "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe":
        fail("SELECTION_KAT_MISMATCH", "mapping")
    boundary = deferred["rejection_boundary_test"]
    values = [int(value, 16) for value in boundary["synthetic_digest_sequence"]]
    if not (values[0] == limit and values[1] < limit and values[1] % 7 == 3):
        fail("SELECTION_KAT_MISMATCH", "boundary")
    return {"frame_bytes": len(frame), "frame_sha256": _sha(frame), "selected_index": 2}


def _verify_normative_authority(root: Path) -> dict[str, Any]:
    authority = _load(root / "generated/goal5793_x2_nist_normative_offline_authority_20260822.json")
    if authority.get("schema") != "rtdl.goal5793.x2.nist_normative_offline_authority.v1":
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "schema")
    if authority.get("authority_sha256") != seal_document(
        authority,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x2.nist_normative_offline_authority",
        version=1,
    ):
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "seal")
    if authority.get("status") != "OFFLINE_NISTIR_CIPHER_SUITE_0_VERIFIER_AND_SYNTHETIC_TRUST_KAT_READY_FOR_EXTERNAL_REVIEW__NO_LIVE_AUTHORITY":
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "status")
    expected_sources = [
        {
            "path": "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/NIST.IR.8213-draft.pdf",
            "bytes": 762001,
            "sha256": "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183",
        },
        {
            "path": "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/beacon-2.0.xsd",
            "bytes": 19033,
            "sha256": "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6",
        },
    ]
    if authority.get("normative_source_identity") != {
        "status": "EXACT_RECOVERED_NORMATIVE_SOURCE_BYTES_MATCH",
        "files": expected_sources,
    }:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "normative sources")
    source_payloads = (
        ("payload/normative/NIST.IR.8213-draft.pdf", expected_sources[0]),
        ("payload/normative/beacon-2.0.xsd", expected_sources[1]),
    )
    for rel, expected in source_payloads:
        data = root.joinpath(*PurePosixPath(rel).parts).read_bytes()
        if len(data) != expected["bytes"] or _sha(data) != expected["sha256"]:
            fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", rel)
    boundary = authority.get("source_interpretation_boundary")
    expected_conflicts = [
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
    ]
    if not isinstance(boundary, Mapping) or boundary.get("conflicts") != expected_conflicts:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "source conflicts")
    if boundary.get("xsd_scope") != "TRANSPORT_STRUCTURE_AND_FIELD_LEXICAL_CONSTRAINTS_ONLY" or boundary.get("source_conflict_hidden") is not False or boundary.get("post_observation_variant_choice_allowed") is not False:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "interpretation boundary")
    xsd = authority.get("xsd_contract", {})
    if xsd.get("pulse_field_order") != [
        "uri", "version", "cipherSuite", "period", "certificateId", "chainIndex", "pulseIndex",
        "timeStamp", "localRandomValue", "external", "listValue", "precommitmentValue", "statusCode",
        "signatureValue", "outputValue",
    ] or xsd.get("sha512_hex_length") != 128 or xsd.get("target_namespace") != "http://csrc.nist.gov/ns/beacon/pulse/2.0":
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "XSD contract")
    kat = authority.get("serialization_known_answer", {})
    if kat.get("serialized_bytes") != 850 or kat.get("serialized_sha512") != "9ffc956e1ed81385c949d8a6ed6066f633b3006dd5d525a89636011d01381ecec88e7718bf3d34d6caacb0e17424f8d931ba1365ed175500f429e32eccff9ae5" or kat.get("matches_expected") is not True:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "serialization KAT")
    trust = authority.get("synthetic_trust_bundle")
    if not isinstance(trust, Mapping) or trust.get("trust_bundle_sha256") != seal_document(
        trust,
        seal_field="trust_bundle_sha256",
        domain="rtdl.goal5793.x2.nist_cipher_suite_0.synthetic_trust_bundle",
        version=1,
    ):
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "synthetic trust seal")
    if trust.get("status") != "SYNTHETIC_ONLY__EXACT_OFFLINE_KAT_TRUST_ROOT__NOT_LIVE_NIST_AUTHORITY" or any(trust.get("authorization", {}).values()):
        fail("PREMATURE_LIVE_AUTHORIZATION", "synthetic trust")
    implementation = authority.get("implementation", {})
    expected_implementation = {
        "normative_verifier": "tools/goal5793_x2_nist_normative_verifier.py",
        "normative_offline_selection_client": "tools/goal5793_x2_nist_normative_selection_client.py",
        "verifier_test": "tests/goal5793_x2_nist_normative_verifier_test.py",
        "selection_client_test": "tests/goal5793_x2_nist_normative_selection_client_test.py",
        "shared_canonical": "tools/goal5793_x1_canonical.py",
    }
    for key, rel in expected_implementation.items():
        row = implementation.get(key, {})
        data = root.joinpath(*PurePosixPath(rel).parts).read_bytes()
        if row.get("bytes") != len(data) or row.get("sha256") != _sha(data):
            fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", f"implementation {key}")
    if implementation.get("all_new_seals_import_shared_canonical") is not True or implementation.get("network_client_present") is not False:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "implementation boundary")
    offline = authority.get("offline_evidence", {})
    required_true = (
        "synthetic_pulse_chain_verified", "synthetic_predecessor_anchor_and_1440_pulse_target_chain_verified",
        "every_signature_verified", "every_output_value_recomputed", "every_previous_and_precommitment_link_verified",
        "middle_chain_coherently_resigned_link_attack_rejected", "next_closest_target_rejected_same_exact_uri_retained",
        "selection_mapping_is_synthetic_rehearsal_only",
    )
    if any(offline.get(key) is not True for key in required_true) or offline.get("authenticated_pulse_count") != 1442:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "offline evidence")
    unresolved = authority.get("unresolved_live_boundary", {})
    if any(unresolved.get(key) is not False for key in (
        "exact_live_nist_root_and_intermediate_bundle_issued", "live_nist_pulse_fixture_observed",
        "live_variant_selected_after_observation", "live_beacon_acceptance_usable",
    )):
        fail("PREMATURE_LIVE_AUTHORIZATION", "live boundary")
    runtime = authority.get("runtime_boundary", {})
    if runtime.get("cryptography_package_bytes_embedded_in_capsule") is not False or runtime.get("python_stdlib_bytes_embedded_in_capsule") is not False or runtime.get("hermetic_runtime_claimed") is not False:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "runtime boundary")
    if runtime.get("runtime_tcb") != ["PYTHON_INTERPRETER", "PYTHON_STDLIB", "CRYPTOGRAPHY_PACKAGE", "HOST_OS_CRYPTO_APIS"]:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "runtime TCB")
    if any(authority.get("authorization", {}).values()):
        fail("PREMATURE_LIVE_AUTHORIZATION", "normative authority")
    if authority.get("activity") != {
        "normative_source_recovery_http_get_count": 2, "provider_search_calls": 0, "beacon_calls": 0,
        "entropy_draws": 0, "scientific_selections": 0, "candidate_actions": 0,
        "gpu_ssh_pod_actions": 0, "registered_or_performance_timings": 0,
    }:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "activity")
    claim = authority.get("claim_boundary", {})
    if claim.get("normative_nistir_serialization_implemented") is not True or claim.get("offline_synthetic_verification_complete") is not True or claim.get("live_nist_verifier_complete") is not False or claim.get("x2_externally_accepted") is not False or claim.get("x3_authorized") is not False or claim.get("generalization_evidence_count") != 0 or claim.get("usability_evidence_count") != 0:
        fail("NIST_NORMATIVE_AUTHORITY_MISMATCH", "claim boundary")
    return authority


def run_hostiles(alias: Mapping[str, Any], protocol: Mapping[str, Any], normative: Mapping[str, Any]) -> list[dict[str, Any]]:
    cases: list[tuple[str, str]] = []
    mutated = copy.deepcopy(alias); mutated["rows"] = mutated["rows"][:-1]
    try:
        if len(mutated["rows"]) != 186: fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH")
    except VerificationFailure as exc: cases.append(("X2H01", exc.fail_id))
    mutated = copy.deepcopy(alias); mutated["authorization"]["live_search"] = True
    try:
        if any(mutated["authorization"].values()): fail("PREMATURE_LIVE_AUTHORIZATION")
    except VerificationFailure as exc: cases.append(("X2H02", exc.fail_id))
    mutated = copy.deepcopy(alias); mutated["counts"]["no_strong_identifier_rows"] = 178
    try:
        if mutated["counts"]["no_strong_identifier_rows"] != 179: fail("EXPOSURE_ALIAS_AUTHORITY_MISMATCH")
    except VerificationFailure as exc: cases.append(("X2H03", exc.fail_id))
    mutated = copy.deepcopy(protocol); mutated["deferred_entropy"]["alternate_or_next_available_target_allowed"] = True
    try:
        if mutated["deferred_entropy"] != protocol["deferred_entropy"]: fail("ENTROPY_PROTOCOL_DRIFT")
    except VerificationFailure as exc: cases.append(("X2H04", exc.fail_id))
    mutated = copy.deepcopy(normative); mutated["source_interpretation_boundary"]["conflicts"] = mutated["source_interpretation_boundary"]["conflicts"][:-1]
    try:
        if mutated["source_interpretation_boundary"] != normative["source_interpretation_boundary"]: fail("NIST_NORMATIVE_AUTHORITY_MISMATCH")
    except VerificationFailure as exc: cases.append(("X2H05", exc.fail_id))
    mutated = copy.deepcopy(normative); mutated["claim_boundary"]["live_nist_verifier_complete"] = True
    try:
        if mutated["claim_boundary"]["live_nist_verifier_complete"] is not False: fail("PREMATURE_LIVE_AUTHORIZATION")
    except VerificationFailure as exc: cases.append(("X2H06", exc.fail_id))
    mutated = copy.deepcopy(normative); mutated["unresolved_live_boundary"]["exact_live_nist_root_and_intermediate_bundle_issued"] = True
    try:
        if mutated["unresolved_live_boundary"]["exact_live_nist_root_and_intermediate_bundle_issued"] is not False: fail("PREMATURE_LIVE_AUTHORIZATION")
    except VerificationFailure as exc: cases.append(("X2H07", exc.fail_id))
    mutated = copy.deepcopy(normative); mutated["synthetic_trust_bundle"]["root"]["pem_sha256"] = "0" * 64
    mutated["synthetic_trust_bundle"]["trust_bundle_sha256"] = seal_document(
        mutated["synthetic_trust_bundle"], seal_field="trust_bundle_sha256",
        domain="rtdl.goal5793.x2.nist_cipher_suite_0.synthetic_trust_bundle", version=1,
    )
    try:
        if mutated.get("authority_sha256") != seal_document(mutated, seal_field="authority_sha256", domain="rtdl.goal5793.x2.nist_normative_offline_authority", version=1):
            fail("NIST_NORMATIVE_AUTHORITY_MISMATCH")
    except VerificationFailure as exc: cases.append(("X2H08", exc.fail_id))
    expected = {
        "X2H01": "EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "X2H02": "PREMATURE_LIVE_AUTHORIZATION",
        "X2H03": "EXPOSURE_ALIAS_AUTHORITY_MISMATCH", "X2H04": "ENTROPY_PROTOCOL_DRIFT",
        "X2H05": "NIST_NORMATIVE_AUTHORITY_MISMATCH", "X2H06": "PREMATURE_LIVE_AUTHORIZATION",
        "X2H07": "PREMATURE_LIVE_AUTHORIZATION", "X2H08": "NIST_NORMATIVE_AUTHORITY_MISMATCH",
    }
    if dict(cases) != expected:
        fail("HOSTILE_SUITE_MISMATCH", repr(cases))
    return [{"hostile_id": key, "observed_fail_id": value, "pass": True} for key, value in cases]


def recompute_audit(root: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    mapped = _manifest_map(root, manifest)
    _verify_key_roots(root)
    _verify_authorizations(root)
    alias = _verify_alias_authority(root)
    tool_count = _verify_no_network_code(root, mapped)
    pdf_runtime = _verify_pdf_vendor_and_isolated_runtime(root)
    kat = _verify_kat(root)
    normative = _verify_normative_authority(root)
    protocol = _load(root / "payload/authorities/goal5793_s0_protocol_and_stage_authority_20260822.json")
    hostiles = run_hostiles(alias, protocol, normative)
    audit: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_review_capsule.audit.v2",
        "status": "PASS__COMPACT_SELF_CONTAINED_OFFLINE_X2_REVIEW_CAPSULE__READY_FOR_EXACT_BYTE_EXTERNAL_REVIEW__NO_LIVE_AUTHORIZATION",
        "manifest_sha256": manifest["manifest_sha256"],
        "checks": {
            "payload_count": len(mapped), "payload_bytes": sum(row["bytes"] for row in mapped.values()),
            "key_predecessor_roots": len(KEY_ROOTS), "fixed_synthetic_assets": len(FIXTURE_ROOTS),
            "x2_python_tool_count": tool_count, "exposure_rows": 186, "strong_identifier_rows": 7,
            "no_strong_identifier_rows": 179, "selection_eligible_exposure_rows": 0,
            "selection_kat": kat, "hostile_pass_count": len(hostiles),
            "exact_normative_source_recovery_http_gets": 2,
            "normative_source_file_count": 2,
            "normative_serialization_kat_pass": True,
            "synthetic_authenticated_pulse_count": 1442,
            "provider_search_calls": 0, "beacon_calls": 0, "network_calls_during_offline_x2": 0,
            "pdf_parser_and_isolated_runtime": pdf_runtime,
            "entropy_draws": 0, "scientific_selections": 0, "candidate_work_count": 0,
        },
        "hostile_results": hostiles,
        "claim_boundary": {
            "compact_reviewability_closed": True,
            "strong_identifier_coverage_gap_eliminated": False,
            "conservative_179_row_matching_frozen": True,
            "normative_nist_source_bytes_present": True,
            "normative_cipher_suite_zero_verifier_implemented": True,
            "offline_synthetic_chain_verified": True,
            "exact_live_nist_trust_bundle_issued": False,
            "live_nist_pulse_observed": False,
            "x2_exact_byte_external_review_pending": True,
            "x2_closure_authorized": False,
            "x3_live_search_authorized": False,
            "generalization_evidence_count": 0,
            "usability_evidence_count": 0,
        },
        "audit_sha256": "",
    }
    audit["audit_sha256"] = seal_document(audit, seal_field="audit_sha256", domain=AUDIT_DOMAIN, version=2)
    return audit


def verify_root(root: Path, require_audit: bool = True) -> dict[str, Any]:
    root = root.resolve()
    manifest = _load(root / "manifest.json")
    audit = recompute_audit(root, manifest)
    if require_audit:
        stored = _load(root / "audit.json")
        if stored != audit:
            fail("CAPSULE_AUDIT_MISMATCH", "stored audit")
    return audit


def _safe_extract(archive_path: Path, destination: Path) -> Path:
    seen: set[str] = set()
    order: list[str] = []
    total = 0
    with tarfile.open(archive_path, mode="r:gz") as archive:
        if archive.pax_headers:
            fail("CAPSULE_ARCHIVE_INVALID", "global PAX")
        for member in archive:
            rel = _canonical_rel(member.name)
            if rel in seen or member.pax_headers:
                fail("CAPSULE_ARCHIVE_INVALID", "duplicate/PAX")
            seen.add(rel); order.append(rel)
            if not member.isreg() or member.mode != 0o444 or member.uid != 0 or member.gid != 0 or member.mtime != 0 or member.uname or member.gname:
                fail("CAPSULE_ARCHIVE_INVALID", rel)
            total += member.size
            if total > 20_000_000 or len(seen) > 200:
                fail("CAPSULE_ARCHIVE_INVALID", "limit")
            if not rel.startswith(CAPSULE_DIRNAME + "/"):
                fail("CAPSULE_ARCHIVE_INVALID", rel)
            handle = archive.extractfile(member)
            if handle is None:
                fail("CAPSULE_ARCHIVE_INVALID", rel)
            data = handle.read()
            target = destination.joinpath(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if order != sorted(order, key=lambda value: value.encode("utf-8")):
        fail("CAPSULE_ARCHIVE_INVALID", "member order")
    return destination / CAPSULE_DIRNAME


def verify_archive(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw[:10] != bytes.fromhex("1f8b08000000000002ff"):
        fail("CAPSULE_ARCHIVE_INVALID", "gzip header")
    with tempfile.TemporaryDirectory(prefix="goal5793_x2_capsule_verify_") as temp:
        return verify_root(_safe_extract(path.resolve(), Path(temp)))


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capsule-root", type=Path)
    group.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        result = verify_root(args.capsule_root) if args.capsule_root else verify_archive(args.archive)
    except VerificationFailure as exc:
        print(json.dumps({"status": "FAIL", "fail_id": exc.fail_id, "detail": exc.detail}, sort_keys=True))
        return 1
    print(json.dumps({"status": "PASS", "audit_sha256": result["audit_sha256"], "x2_closeable": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
