#!/usr/bin/env python3
"""Build the deterministic compact offline X2 review capsule."""

from __future__ import annotations

import argparse
import gzip
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
from typing import Any
import sys

import pypdf

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import CANONICALIZATION_NAME, canonical_json_bytes, seal_document, sha256_bytes
from scripts.goal5793_x2_build_exposure_alias_authority import build_authority
from scripts.goal5793_x2_build_nist_normative_authority import build_authority as build_nist_normative_authority
from scripts import goal5793_x2_verify_offline_review_capsule as verifier


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
ARCHIVE_NAME = "goal5793_x2_offline_review_capsule_20260822.tar.gz"
TWIN_NAME = "goal5793_x2_offline_review_capsule_twin_20260822.tar.gz"
MANIFEST_NAME = "goal5793_x2_offline_review_capsule_manifest_20260822.json"
AUDIT_NAME = "goal5793_x2_offline_review_capsule_audit_20260822.json"

STATIC_PAYLOADS = {
    "payload/authorities/goal5793_s0_protocol_and_stage_authority_20260822.json": "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json",
    "payload/authorities/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json": "history/internal_docs/goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json",
    "payload/authorities/goal5793_x1_governance_ordering_amendment_20260822.json": "history/internal_docs/goal5793_x1_governance_ordering_amendment_20260822.json",
    "payload/authorities/goal5793_x1_owner_returned_external_review_absorption_20260822.json": "history/internal_docs/goal5793_x1_owner_returned_external_review_absorption_20260822.json",
    "payload/authorities/goal5793_x1_project_exposure_registry_v2_20260822.json": "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json",
    "payload/authorities/goal5793_x1_positive_vector_freeze_20260822.json": "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json",
    "payload/reviews/review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md": "history/internal_docs/review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md",
    "payload/custody/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz": "history/internal_docs/goal5793_x1_s0_reproduction_capsule_20260822.tar.gz",
    "payload/custody/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json": "history/internal_docs/goal5793_x1_s0_reproduction_capsule_manifest_20260822.json",
    "payload/custody/goal5793_x1_s0_reproduction_capsule_audit_20260822.json": "history/internal_docs/goal5793_x1_s0_reproduction_capsule_audit_20260822.json",
    "payload/source/goal5753_survey_source.tar": "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar",
    "payload/recovery/goal5793_x2_normative_source_recovery_preaction_work_authority_v2_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_preaction_work_authority_v2_20260822.json",
    "payload/recovery/call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md": "history/internal_docs/call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md",
    "payload/recovery/review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md": "history/internal_docs/review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md",
    "payload/recovery/goal5793_x2_normative_source_recovery_owner_send_receipt_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_owner_send_receipt_20260822.json",
    "payload/recovery/goal5793_x2_normative_source_recovery_preaction_governance_authority_v3_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_preaction_governance_authority_v3_20260822.json",
    "payload/recovery/goal5793_x2_normative_source_recovery_review_absorption_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_review_absorption_20260822.json",
    "payload/recovery/goal5793_x2_normative_source_recovery_owner_closure_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_owner_closure_20260822.json",
    "payload/normative/NIST.IR.8213-draft.pdf": "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/NIST.IR.8213-draft.pdf",
    "payload/normative/beacon-2.0.xsd": "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/beacon-2.0.xsd",
    "payload/recovery/goal5793_x2_normative_source_recovery_receipt_20260822.json": "history/internal_docs/goal5793_x2_normative_source_recovery_20260822/goal5793_x2_normative_source_recovery_receipt_20260822.json",
    "payload/recovery/goal5793_x2_recover_pinned_normative_sources.py": "scripts/goal5793_x2_recover_pinned_normative_sources.py",
    "payload/recovery/goal5793_x2_absorb_normative_source_recovery_review.py": "scripts/goal5793_x2_absorb_normative_source_recovery_review.py",
}

TOOL_PATHS = [
    "scripts/goal5793_x1_canonical.py",
    "scripts/goal5793_x1_build_exposure_registry.py",
    "scripts/goal5793_x2_offline_core.py",
    "scripts/goal5793_x2_offline_harvester.py",
    "scripts/goal5793_x2_preentropy_enumerator.py",
    "scripts/goal5793_x2_build_exposure_alias_authority.py",
    "scripts/goal5793_x2_structural_friction.py",
    "scripts/goal5793_x2_nist_synthetic_crypto.py",
    "scripts/goal5793_x2_selection_client.py",
    "scripts/goal5793_x2_nist_normative_verifier.py",
    "scripts/goal5793_x2_nist_normative_selection_client.py",
    "scripts/goal5793_x2_build_nist_normative_authority.py",
    "scripts/goal5793_x2_pdf_identity.py",
    "scripts/goal5793_x2_run_pdf_identity.py",
    "scripts/goal5793_x2_offline_source_resolver.py",
    "scripts/goal5793_x2_offline_author_code.py",
    "scripts/goal5793_x2_verify_offline_review_capsule.py",
    "scripts/goal5793_x2_build_offline_review_capsule.py",
]
TEST_PATHS = [
    "tests/goal5793_x2_offline_core_test.py",
    "tests/goal5793_x2_harvester_enumerator_test.py",
    "tests/goal5793_x2_exposure_alias_authority_test.py",
    "tests/goal5793_x2_structural_friction_test.py",
    "tests/goal5793_x2_nist_synthetic_crypto_test.py",
    "tests/goal5793_x2_selection_client_test.py",
    "tests/goal5793_x2_nist_normative_verifier_test.py",
    "tests/goal5793_x2_nist_normative_selection_client_test.py",
    "tests/goal5793_x2_nist_normative_authority_test.py",
    "tests/goal5793_x2_recover_pinned_normative_sources_test.py",
    "tests/goal5793_x2_normative_source_recovery_absorption_test.py",
    "tests/goal5793_x2_pdf_identity_test.py",
    "tests/goal5793_x2_run_pdf_identity_test.py",
    "tests/goal5793_x2_offline_source_resolver_test.py",
    "tests/goal5793_x2_offline_author_code_test.py",
    "tests/goal5793_x2_offline_review_capsule_test.py",
]
FIXTURE_PATHS = [
    "tests/fixtures/goal5793_x2_nist/synthetic_root.pem",
    "tests/fixtures/goal5793_x2_nist/synthetic_leaf.pem",
    "tests/fixtures/goal5793_x2_nist/synthetic_pulse.json",
    "tests/fixtures/goal5793_x2_pdf/synthetic_identity.pdf.b64",
]


def _json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def _payloads() -> tuple[dict[str, bytes], dict[str, str]]:
    payloads: dict[str, bytes] = {}
    roles: dict[str, str] = {}
    def add(rel: str, data: bytes, role: str) -> None:
        path = PurePosixPath(rel)
        if path.is_absolute() or path.as_posix() != rel or "." in path.parts or ".." in path.parts or rel in payloads:
            raise RuntimeError(f"invalid/duplicate payload: {rel}")
        payloads[rel] = data; roles[rel] = role
    for rel, source in STATIC_PAYLOADS.items():
        add(rel, (ROOT / source).read_bytes(), "PINNED_PREDECESSOR_OR_CUSTODY")
    for source in TOOL_PATHS:
        add("tools/" + PurePosixPath(source).name, (ROOT / source).read_bytes(), "X2_FROZEN_TOOL")
    for source in TEST_PATHS:
        add("tests/" + PurePosixPath(source).name, (ROOT / source).read_bytes(), "X2_HOSTILE_TEST")
    for source in FIXTURE_PATHS:
        add(source, (ROOT / source).read_bytes(), "X2_FIXED_OFFLINE_FIXTURE")
    pypdf_root = Path(pypdf.__file__).resolve().parent
    vendor_rows = []
    for source in sorted(pypdf_root.rglob("*"), key=lambda path: path.relative_to(pypdf_root).as_posix().encode("utf-8")):
        if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
            continue
        rel = source.relative_to(pypdf_root).as_posix()
        data = source.read_bytes()
        vendor_rows.append({"path": rel, "bytes": len(data), "sha256": sha256_bytes(data)})
        add("vendor/pypdf/" + rel, data, "PINNED_PYPDF_6_14_2_SOURCE")
    if len(vendor_rows) != 56 or sum(row["bytes"] for row in vendor_rows) != 1_486_221 or sha256_bytes(canonical_json_bytes(vendor_rows)) != "3df52f80b93fbcb44dd793e0ba27ee2438ad7cf06de7ab355e1755c0078a9bd1":
        raise RuntimeError("PYPDF_VENDOR_AUTHORITY_MISMATCH")
    add("generated/goal5793_x2_exposure_alias_authority_20260822.json", _json_bytes(build_authority()), "GENERATED_EXPOSURE_ALIAS_AUTHORITY")
    add("generated/goal5793_x2_nist_normative_offline_authority_20260822.json", _json_bytes(build_nist_normative_authority()), "GENERATED_NIST_NORMATIVE_OFFLINE_AUTHORITY")
    return payloads, roles


def _manifest(payloads: dict[str, bytes], roles: dict[str, str]) -> dict[str, Any]:
    rows = [{"path": rel, "bytes": len(payloads[rel]), "sha256": sha256_bytes(payloads[rel]), "role": roles[rel]} for rel in sorted(payloads, key=lambda value: value.encode("utf-8"))]
    manifest: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_review_capsule.manifest.v2", "goal": 5793, "stage": "X2_OFFLINE_IMPLEMENTATION",
        "date": DATE, "status": "COMPACT_SELF_CONTAINED_OFFLINE_REVIEW_CAPSULE__READY_FOR_EXACT_BYTE_EXTERNAL_REVIEW__NO_LIVE_AUTHORIZATION",
        "canonicalization": CANONICALIZATION_NAME, "payloads": rows,
        "payload_summary": {"file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows), "rows_sha256": sha256_bytes(canonical_json_bytes(rows))},
        "delivery_rule": {"external_send_file": "SOLE_CFR_MARKDOWN_ONLY", "capsule_sent_as_second_attachment": False, "capsule_local_evidence_path_only": True},
        "activity": {"exact_normative_source_recovery_http_gets": 2, "provider_search": 0, "beacon": 0, "entropy": 0, "selection": 0, "candidate_work": 0, "gpu_ssh_pod": 0, "timing": 0},
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = seal_document(manifest, seal_field="manifest_sha256", domain=verifier.MANIFEST_DOMAIN, version=2)
    return manifest


def _archive_bytes(files: dict[str, bytes]) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
            for rel in sorted(files, key=lambda value: value.encode("utf-8")):
                data = files[rel]
                info = tarfile.TarInfo(f"{verifier.CAPSULE_DIRNAME}/{rel}")
                info.size = len(data); info.mode = 0o444; info.uid = 0; info.gid = 0; info.uname = ""; info.gname = ""; info.mtime = 0
                archive.addfile(info, io.BytesIO(data))
    return raw.getvalue()


def build_outputs() -> dict[str, bytes]:
    payloads, roles = _payloads()
    manifest = _manifest(payloads, roles)
    manifest_bytes = _json_bytes(manifest)
    with tempfile.TemporaryDirectory(prefix="goal5793_x2_capsule_build_") as temp:
        root = Path(temp)
        for rel, data in payloads.items():
            path = root.joinpath(*PurePosixPath(rel).parts); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        (root / "manifest.json").write_bytes(manifest_bytes); (root / "audit.json").write_bytes(b"{}\n")
        audit = verifier.recompute_audit(root, manifest)
    audit_bytes = _json_bytes(audit)
    files = dict(payloads); files["manifest.json"] = manifest_bytes; files["audit.json"] = audit_bytes
    archive = _archive_bytes(files)
    return {ARCHIVE_NAME: archive, TWIN_NAME: archive, MANIFEST_NAME: manifest_bytes, AUDIT_NAME: audit_bytes}


def summary(outputs: dict[str, bytes]) -> dict[str, Any]:
    return {"status": "DRY_RUN_PASS__READY_FOR_EXTERNAL_REVIEW__NO_LIVE_AUTHORIZATION", "outputs": [{"path": name, "bytes": len(data), "sha256": sha256_bytes(data)} for name, data in outputs.items()], "archive_twin_byte_identical": outputs[ARCHIVE_NAME] == outputs[TWIN_NAME]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path); parser.add_argument("--write-create-only", action="store_true"); args = parser.parse_args()
    if args.write_create_only != (args.output_dir is not None):
        parser.error("formal writes require both --output-dir and --write-create-only")
    outputs = build_outputs(); result = summary(outputs)
    if args.output_dir is not None:
        paths = [args.output_dir / name for name in outputs]
        if any(path.exists() or path.is_symlink() for path in paths):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items(): (args.output_dir / name).write_bytes(data)
        result["status"] = "CREATE_ONLY_WRITE_PASS__READY_FOR_EXTERNAL_REVIEW__NO_LIVE_AUTHORIZATION"
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
