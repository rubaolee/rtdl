#!/usr/bin/env python3
"""Acquire and verify exact Goal5836 A0 paper/source bytes without execution."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_RELATIVE = (
    "history/internal_docs/goal5836_a0_source_acquisition_20260901"
)
DEFAULT_OUTPUT = ROOT / OUTPUT_RELATIVE
PREACTION_PATH = (
    "history/internal_docs/"
    "goal5836_sui_same_input_preaction_authority_20260901.json"
)
OWNER_AUTHORIZATION_PATH = (
    "history/internal_docs/goal5836_a0_owner_authorization_20260901.md"
)
PREACTION_PIN = (
    13229,
    "7e021a874a13454488bf056c44402225bc1deadfc990cf2a8aeb48eaed9c7f40",
)
OWNER_AUTHORIZATION_PIN = (
    1169,
    "ec7f820ec9691ee3d62ce0dcb280a9f04e80c9a320aedef138c3e17189f56982",
)
PREDECESSOR_COMMIT = "92923035a676768a967b2b22d9592c4d712cd0ad"
AUTHOR_REPOSITORY = "https://github.com/Ssz990220/RTCollisionDetection.git"
AUTHOR_COMMIT = "bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7"
AUTHOR_ROOT_TREE = "3e5e1c3a2a128148eae61bc94a22eaae491e496f"
PAPER_URL = "https://arxiv.org/pdf/2409.09918v2"
PAPER_ABS_URL = "https://arxiv.org/abs/2409.09918v2"
PAPER_SHA256 = "9a0003bda2ce176415389c99af0e91aea0fc1564a3bfb7388b8054760993c9c0"
PAPER_BYTES = 34726851
ARXIV_ID = "2409.09918v2"
ICRA_DOI = "10.1109/ICRA55743.2025.11128528"
DOMAIN = b"rtdl.goal5836.a0.source_acquisition_authority.v1\0"

PRESERVED_FILENAMES = (
    "PAPER_ARXIV_2409.09918V2.pdf",
    "PAPER_ABS_V2.html",
    "PAPER_PDF_HTTP_HEADERS.txt",
    "PAPER_ABS_HTTP_HEADERS.txt",
    "PAPER_PDFINFO.txt",
    "AUTHOR_COMMIT_OBJECT.txt",
    "AUTHOR_LICENSE.txt",
    "AUTHOR_SOURCE_TREE_INVENTORY.json",
    "AUTHOR_SELECTED_SOURCE_MANIFEST.json",
    "AUTHOR_SELECTED_SOURCE.tar.gz",
    "FETCH_RECEIPT.json",
)
AUTHORITY_FILENAME = "SOURCE_ACQUISITION_AUTHORITY.json"
IMPLEMENTATION_PATHS = (
    "scripts/goal5836_a0_build_source_acquisition.py",
    "tests/goal5836_a0_source_acquisition_test.py",
)
SELECTED_BASENAMES = {
    ".clang-format",
    ".gitattributes",
    ".gitignore",
    "CMakeLists.txt",
    "LICENSE",
    "README.md",
    "requirements.txt",
}
SELECTED_SUFFIXES = {
    ".bat",
    ".c",
    ".cc",
    ".cmake",
    ".cpp",
    ".cu",
    ".cuh",
    ".h",
    ".hpp",
    ".in",
    ".inl",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".toml",
    ".urdf",
    ".yaml",
    ".yml",
}
AUTHORIZATION = {
    "a0_owner_authorized": True,
    "a0_acquisition_completed": True,
    "a0_authorization_consumed": True,
    "a1_source_fidelity_inspection_authorized": False,
    "a2_input_freeze_authorized": False,
    "a3_route_materialization_authorized": False,
    "a4_modern_rtx_execution_authorized": False,
    "a5_paper_app_decision_authorized": False,
    "author_build_or_execution_authorized": False,
    "product_or_case_study_mutation_authorized": False,
    "pod_or_gpu_authorized": False,
    "timing_or_performance_authorized": False,
    "external_review_authorized": False,
    "public_claim_authorized": False,
}
CLAIM_BOUNDARY = {
    "paper_app_status": "NOT_A_PAPER_APP",
    "source_relation": "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES",
    "goal5836_functional_result_claimed": False,
    "paper_app_claimed": False,
    "performance_claimed": False,
    "complete_rtccd_claimed": False,
}


class A0Error(RuntimeError):
    """Raised when exact A0 source custody cannot be established."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _pretty_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii") + b"\n"


def _seal(document: dict[str, Any]) -> str:
    payload = dict(document)
    payload["source_acquisition_authority_sha256"] = ""
    return hashlib.sha256(DOMAIN + canonical_json_bytes(payload)).hexdigest()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_oid(kind: str, data: bytes) -> str:
    header = f"{kind} {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _identity(path: Path, relative: str) -> dict[str, Any]:
    logical = PurePosixPath(relative)
    if logical.is_absolute() or ".." in logical.parts:
        raise A0Error(f"NON_PORTABLE_IDENTITY_PATH:{relative}")
    data = path.read_bytes()
    return {
        "path": logical.as_posix(),
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _repo_identity(relative: str) -> dict[str, Any]:
    return _identity(ROOT / relative, relative)


def _verify_static_pins() -> None:
    for relative, expected in (
        (PREACTION_PATH, PREACTION_PIN),
        (OWNER_AUTHORIZATION_PATH, OWNER_AUTHORIZATION_PIN),
    ):
        row = _repo_identity(relative)
        if (row["bytes"], row["sha256"]) != expected:
            raise A0Error(f"STATIC_PIN_MISMATCH:{relative}")


def _git(repo: Path, *args: str) -> bytes:
    process = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise A0Error(f"GIT_COMMAND_FAILED:{args!r}:{detail}")
    return process.stdout


def _parse_tree_rows(author_repo: Path) -> tuple[list[dict[str, Any]], bytes]:
    raw_listing = _git(author_repo, "ls-tree", "-r", "-z", "-l", AUTHOR_COMMIT)
    rows: list[dict[str, Any]] = []
    for record in raw_listing.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, oid, size_text = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8", errors="strict")
        logical = PurePosixPath(path)
        if logical.is_absolute() or ".." in logical.parts or logical.as_posix() != path:
            raise A0Error(f"INVALID_AUTHOR_TREE_PATH:{path}")
        if object_type != "blob" or size_text == "-":
            raise A0Error(f"UNSUPPORTED_AUTHOR_TREE_ENTRY:{path}:{object_type}")
        data = _git(author_repo, "cat-file", "blob", oid)
        size = int(size_text)
        if len(data) != size or _git_oid("blob", data) != oid:
            raise A0Error(f"AUTHOR_BLOB_IDENTITY_MISMATCH:{path}")
        rows.append(
            {
                "path": path,
                "mode": mode,
                "object_type": "blob",
                "git_oid_sha1": oid,
                "bytes": size,
                "sha256": _sha256(data),
            }
        )
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    if len({row["path"] for row in rows}) != len(rows):
        raise A0Error("DUPLICATE_AUTHOR_TREE_PATH")
    return rows, raw_listing


def _rederive_tree_oid(rows: list[dict[str, Any]]) -> str:
    root: dict[str, Any] = {}
    for row in rows:
        parts = PurePosixPath(row["path"]).parts
        cursor = root
        for part in parts[:-1]:
            existing = cursor.setdefault(part, {})
            if not isinstance(existing, dict):
                raise A0Error(f"TREE_FILE_DIRECTORY_CONFLICT:{row['path']}")
            cursor = existing
        if parts[-1] in cursor:
            raise A0Error(f"TREE_DUPLICATE_ENTRY:{row['path']}")
        cursor[parts[-1]] = ("blob", row)

    def encode_tree(node: dict[str, Any]) -> str:
        entries: list[tuple[bytes, bytes]] = []
        for name, value in node.items():
            raw_name = name.encode("utf-8")
            if isinstance(value, dict):
                oid = encode_tree(value)
                sort_key = raw_name + b"/"
                entry = b"40000 " + raw_name + b"\0" + bytes.fromhex(oid)
            else:
                marker, row = value
                if marker != "blob":
                    raise A0Error(f"TREE_UNKNOWN_LEAF:{name}")
                oid = row["git_oid_sha1"]
                sort_key = raw_name + b"\0"
                entry = row["mode"].encode("ascii") + b" " + raw_name + b"\0" + bytes.fromhex(oid)
            entries.append((sort_key, entry))
        body = b"".join(entry for _, entry in sorted(entries, key=lambda item: item[0]))
        return _git_oid("tree", body)

    return encode_tree(root)


def _selected(row: dict[str, Any]) -> bool:
    logical = PurePosixPath(row["path"])
    return logical.name in SELECTED_BASENAMES or logical.suffix.lower() in SELECTED_SUFFIXES


def _tar_info(name: str, data: bytes, mode: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    info.type = tarfile.REGTYPE
    return info


def _build_selected_capsule(author_repo: Path, rows: list[dict[str, Any]]) -> tuple[bytes, dict[str, Any]]:
    selected = [row for row in rows if _selected(row)]
    prefix = f"RTCollisionDetection-{AUTHOR_COMMIT}"
    raw_tar = io.BytesIO()
    with tarfile.open(fileobj=raw_tar, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for row in selected:
            data = _git(author_repo, "cat-file", "blob", row["git_oid_sha1"])
            name = f"{prefix}/{row['path']}"
            info = _tar_info(name, data, int(row["mode"], 8) & 0o777)
            archive.addfile(info, io.BytesIO(data))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=0) as stream:
        stream.write(raw_tar.getvalue())
    manifest = {
        "schema": "rtdl.goal5836.a0.author_selected_source_manifest.v1",
        "selection_rule": {
            "kind": "MECHANICAL_BASENAME_OR_SUFFIX__NO_SEMANTIC_INSPECTION",
            "basenames": sorted(SELECTED_BASENAMES),
            "suffixes": sorted(SELECTED_SUFFIXES),
            "excluded_examples": ["binary .bin", "images/GIFs", "OBJ meshes", "notebooks"],
        },
        "repository": AUTHOR_REPOSITORY,
        "commit": AUTHOR_COMMIT,
        "root_tree_git_oid_sha1": AUTHOR_ROOT_TREE,
        "archive_prefix": prefix,
        "selected_file_count": len(selected),
        "selected_blob_bytes": sum(row["bytes"] for row in selected),
        "rows": selected,
    }
    return compressed.getvalue(), manifest


def _write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def _artifact_rows(output_dir: Path) -> list[dict[str, Any]]:
    return [
        _identity(output_dir / name, f"{OUTPUT_RELATIVE}/{name}")
        for name in PRESERVED_FILENAMES
    ]


def _fetch_receipt() -> dict[str, Any]:
    return {
        "schema": "rtdl.goal5836.a0.fetch_receipt.v1",
        "date": "2026-09-01",
        "paper": {
            "selected_identity": "OFFICIAL_ARXIV_V2_AUTHOR_SUBMITTED_REVISION",
            "publisher_pdf_claimed": False,
            "pdf_url": PAPER_URL,
            "abstract_url": PAPER_ABS_URL,
            "arxiv_id": ARXIV_ID,
            "related_icra_doi": ICRA_DOI,
            "http_status_required": 200,
        },
        "git": {
            "repository": AUTHOR_REPOSITORY,
            "planned_commit": AUTHOR_COMMIT,
            "attempts": [
                {
                    "attempt": 1,
                    "transport": "git default HTTP transport",
                    "outcome": "INFRASTRUCTURE_FAILURE__CONNECTION_RESET__NO_COMMIT_INFERENCE",
                    "stderr": (
                        "error: RPC failed; curl 56 Recv failure: Connection reset by peer; "
                        "fetch-pack: unexpected disconnect; fatal: early EOF; "
                        "fatal: invalid index-pack output"
                    ),
                },
                {
                    "attempt": 2,
                    "transport": "git HTTP/1.1",
                    "outcome": "SUCCESS__EXACT_PLANNED_COMMIT_FETCHED",
                    "observed_commit": AUTHOR_COMMIT,
                },
            ],
            "pin_changed_after_fetch": False,
        },
        "registered_byte_acquisition_network_action_count": 4,
        "registered_byte_acquisition_network_actions": [
            "one failed exact Git fetch",
            "one successful exact Git fetch retry",
            "one arXiv v2 PDF fetch",
            "one arXiv v2 abstract-page fetch",
        ],
        "metadata_discovery_browsing_included_in_acquisition_count": False,
        "metadata_discovery_browsing_disclosed_separately": True,
    }


def _inventory_document(rows: list[dict[str, Any]], raw_listing: bytes) -> dict[str, Any]:
    return {
        "schema": "rtdl.goal5836.a0.author_source_tree_inventory.v1",
        "repository": AUTHOR_REPOSITORY,
        "commit_git_oid_sha1": AUTHOR_COMMIT,
        "root_tree_git_oid_sha1": AUTHOR_ROOT_TREE,
        "recursive_listing_sha256": _sha256(raw_listing),
        "file_count": len(rows),
        "submodule_count": 0,
        "total_blob_bytes": sum(row["bytes"] for row in rows),
        "all_blob_oids_recomputed_from_bytes_at_acquisition": True,
        "root_tree_oid_recomputed_from_inventory": True,
        "author_source_semantics_inspected": False,
        "source_fidelity_classification_made": False,
        "rows": rows,
    }


def _build_authority(output_dir: Path) -> dict[str, Any]:
    _verify_static_pins()
    inventory = json.loads((output_dir / "AUTHOR_SOURCE_TREE_INVENTORY.json").read_text(encoding="ascii"))
    selected = json.loads((output_dir / "AUTHOR_SELECTED_SOURCE_MANIFEST.json").read_text(encoding="ascii"))
    fetch = json.loads((output_dir / "FETCH_RECEIPT.json").read_text(encoding="ascii"))
    document: dict[str, Any] = {
        "schema": "rtdl.goal5836.a0.source_acquisition_authority.v1",
        "date": "2026-09-01",
        "goal": "5836-A0",
        "status": "PASS__EXACT_SOURCE_BYTES_ACQUIRED_AND_HASHED__A1_LOCKED",
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessors": [
            _repo_identity(PREACTION_PATH),
            _repo_identity(OWNER_AUTHORIZATION_PATH),
        ],
        "implementation_and_tests": [_repo_identity(path) for path in IMPLEMENTATION_PATHS],
        "artifacts": _artifact_rows(output_dir),
        "paper_identity": {
            "kind": "OFFICIAL_ARXIV_V2_AUTHOR_SUBMITTED_REVISION__NOT_IEEE_PUBLISHER_PDF",
            "title": "Hardware-Accelerated Ray Tracing for Discrete and Continuous Collision Detection on GPUs",
            "authors": ["Sizhe Sui", "Luis Sentis", "Andrew Bylard"],
            "arxiv_id": ARXIV_ID,
            "related_icra_doi": ICRA_DOI,
            "pdf_url": PAPER_URL,
            "bytes": PAPER_BYTES,
            "sha256": PAPER_SHA256,
            "page_count": 10,
            "publisher_pdf_acquired": False,
        },
        "author_source_identity": {
            "repository": AUTHOR_REPOSITORY,
            "planned_commit": AUTHOR_COMMIT,
            "observed_commit": AUTHOR_COMMIT,
            "commit_pin_changed": False,
            "root_tree_git_oid_sha1": AUTHOR_ROOT_TREE,
            "file_count": inventory["file_count"],
            "total_blob_bytes": inventory["total_blob_bytes"],
            "selected_source_file_count": selected["selected_file_count"],
            "selected_source_blob_bytes": selected["selected_blob_bytes"],
            "license_label": "MIT",
            "license_blob_git_oid_sha1": "0ec3c9a8cb0bb8fe2de6ad03ca465ccd12e1c4a5",
            "license_bytes": 1066,
            "license_sha256": _sha256((output_dir / "AUTHOR_LICENSE.txt").read_bytes()),
            "complete_tree_bytes_preserved_in_rtdl_git": False,
            "complete_tree_identity_preserved": True,
            "selected_text_source_bytes_preserved": True,
            "large_binary_assets_reacquired_only_by_exact_commit": True,
        },
        "fetch_receipt": {
            "registered_byte_acquisition_network_action_count": fetch[
                "registered_byte_acquisition_network_action_count"
            ],
            "metadata_discovery_browsing_included_in_acquisition_count": False,
            "paper_method_text_incidentally_returned_by_metadata_lookup": True,
            "first_git_attempt_was_infrastructure_failure": True,
            "exact_retry_succeeded": True,
            "pin_changed_after_fetch": False,
        },
        "a0_observation": {
            "paper_pdf_count": 1,
            "author_commit_count": 1,
            "license_count": 1,
            "paper_identity_metadata_inspected": True,
            "paper_method_text_incidentally_exposed_by_discovery_tool": True,
            "author_source_semantics_inspected": False,
            "source_fidelity_classification_made": False,
            "author_build_count": 0,
            "author_execution_count": 0,
            "rtdl_goal5836_execution_count": 0,
            "gpu_worker_count": 0,
            "timing_count": 0,
            "performance_result_count": 0,
        },
        "authorization": dict(AUTHORIZATION),
        "next_owner_gate": "AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY",
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "source_acquisition_authority_sha256": "",
    }
    document["source_acquisition_authority_sha256"] = _seal(document)
    validate_policy(document)
    return document


def acquire_build(
    *,
    author_repo: Path,
    paper_pdf: Path,
    paper_abs_html: Path,
    paper_pdf_headers: Path,
    paper_abs_headers: Path,
    paper_pdfinfo: Path,
    output_dir: Path,
) -> dict[str, Any]:
    _verify_static_pins()
    if output_dir.exists() or output_dir.is_symlink():
        raise A0Error("CREATE_ONLY_OUTPUT_EXISTS")
    remote = _git(author_repo, "remote", "get-url", "origin").decode("utf-8").strip()
    if remote.rstrip("/") != AUTHOR_REPOSITORY.rstrip("/"):
        raise A0Error(f"AUTHOR_REMOTE_MISMATCH:{remote}")
    observed_commit = _git(author_repo, "rev-parse", f"{AUTHOR_COMMIT}^{{commit}}").decode("ascii").strip()
    observed_tree = _git(author_repo, "rev-parse", f"{AUTHOR_COMMIT}^{{tree}}").decode("ascii").strip()
    if observed_commit != AUTHOR_COMMIT or observed_tree != AUTHOR_ROOT_TREE:
        raise A0Error("AUTHOR_COMMIT_OR_TREE_MISMATCH")
    commit_object = _git(author_repo, "cat-file", "commit", AUTHOR_COMMIT)
    if _git_oid("commit", commit_object) != AUTHOR_COMMIT:
        raise A0Error("AUTHOR_COMMIT_OBJECT_MISMATCH")
    rows, raw_listing = _parse_tree_rows(author_repo)
    if _rederive_tree_oid(rows) != AUTHOR_ROOT_TREE:
        raise A0Error("AUTHOR_ROOT_TREE_REDERIVATION_MISMATCH")
    inventory = _inventory_document(rows, raw_listing)
    selected_capsule, selected_manifest = _build_selected_capsule(author_repo, rows)
    license_row = next((row for row in rows if row["path"] == "LICENSE"), None)
    if license_row is None:
        raise A0Error("AUTHOR_LICENSE_MISSING")
    license_bytes = _git(author_repo, "cat-file", "blob", license_row["git_oid_sha1"])

    paper_bytes = paper_pdf.read_bytes()
    if len(paper_bytes) != PAPER_BYTES or _sha256(paper_bytes) != PAPER_SHA256:
        raise A0Error("PAPER_PDF_PIN_MISMATCH")
    output_dir.mkdir(parents=True, exist_ok=False)
    for destination, source in (
        ("PAPER_ARXIV_2409.09918V2.pdf", paper_pdf),
        ("PAPER_ABS_V2.html", paper_abs_html),
        ("PAPER_PDF_HTTP_HEADERS.txt", paper_pdf_headers),
        ("PAPER_ABS_HTTP_HEADERS.txt", paper_abs_headers),
        ("PAPER_PDFINFO.txt", paper_pdfinfo),
    ):
        _write_create_only(output_dir / destination, source.read_bytes())
    _write_create_only(output_dir / "AUTHOR_COMMIT_OBJECT.txt", commit_object)
    _write_create_only(output_dir / "AUTHOR_LICENSE.txt", license_bytes)
    _write_create_only(output_dir / "AUTHOR_SOURCE_TREE_INVENTORY.json", _pretty_json_bytes(inventory))
    _write_create_only(output_dir / "AUTHOR_SELECTED_SOURCE_MANIFEST.json", _pretty_json_bytes(selected_manifest))
    _write_create_only(output_dir / "AUTHOR_SELECTED_SOURCE.tar.gz", selected_capsule)
    _write_create_only(output_dir / "FETCH_RECEIPT.json", _pretty_json_bytes(_fetch_receipt()))
    authority = _build_authority(output_dir)
    _write_create_only(output_dir / AUTHORITY_FILENAME, _pretty_json_bytes(authority))
    verify_stored(output_dir)
    return authority


def _verify_inventory(output_dir: Path) -> dict[str, Any]:
    inventory = json.loads((output_dir / "AUTHOR_SOURCE_TREE_INVENTORY.json").read_text(encoding="ascii"))
    rows = inventory.get("rows")
    if not isinstance(rows, list) or not rows:
        raise A0Error("INVENTORY_ROWS_MISSING")
    if [row["path"] for row in rows] != sorted(row["path"] for row in rows):
        raise A0Error("INVENTORY_PATH_ORDER_MISMATCH")
    if len({row["path"] for row in rows}) != len(rows):
        raise A0Error("INVENTORY_DUPLICATE_PATH")
    for row in rows:
        if set(row) != {"path", "mode", "object_type", "git_oid_sha1", "bytes", "sha256"}:
            raise A0Error(f"INVENTORY_ROW_SCHEMA_MISMATCH:{row.get('path')}")
        if row["object_type"] != "blob" or row["mode"] not in {"100644", "100755", "120000"}:
            raise A0Error(f"INVENTORY_ROW_TYPE_MISMATCH:{row['path']}")
        if not re.fullmatch(r"[0-9a-f]{40}", row["git_oid_sha1"]):
            raise A0Error(f"INVENTORY_GIT_OID_INVALID:{row['path']}")
        if not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise A0Error(f"INVENTORY_SHA256_INVALID:{row['path']}")
    if inventory["file_count"] != len(rows):
        raise A0Error("INVENTORY_FILE_COUNT_MISMATCH")
    if inventory["total_blob_bytes"] != sum(row["bytes"] for row in rows):
        raise A0Error("INVENTORY_BYTE_COUNT_MISMATCH")
    if _rederive_tree_oid(rows) != AUTHOR_ROOT_TREE:
        raise A0Error("INVENTORY_ROOT_TREE_MISMATCH")
    return inventory


def _verify_selected_capsule(output_dir: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    manifest = json.loads((output_dir / "AUTHOR_SELECTED_SOURCE_MANIFEST.json").read_text(encoding="ascii"))
    expected_rows = [row for row in inventory["rows"] if _selected(row)]
    if manifest.get("rows") != expected_rows:
        raise A0Error("SELECTED_SOURCE_ROWS_MISMATCH")
    if manifest.get("selected_file_count") != len(expected_rows):
        raise A0Error("SELECTED_SOURCE_COUNT_MISMATCH")
    if manifest.get("selected_blob_bytes") != sum(row["bytes"] for row in expected_rows):
        raise A0Error("SELECTED_SOURCE_BYTES_MISMATCH")
    prefix = manifest["archive_prefix"]
    expected_names = [f"{prefix}/{row['path']}" for row in expected_rows]
    with tarfile.open(output_dir / "AUTHOR_SELECTED_SOURCE.tar.gz", mode="r:gz") as archive:
        members = archive.getmembers()
        if [member.name for member in members] != expected_names:
            raise A0Error("SELECTED_SOURCE_ARCHIVE_PATH_SET_MISMATCH")
        for member, row in zip(members, expected_rows, strict=True):
            if not member.isfile() or member.size != row["bytes"]:
                raise A0Error(f"SELECTED_SOURCE_ARCHIVE_MEMBER_SHAPE:{member.name}")
            stream = archive.extractfile(member)
            if stream is None or _sha256(stream.read()) != row["sha256"]:
                raise A0Error(f"SELECTED_SOURCE_ARCHIVE_MEMBER_HASH:{member.name}")
    return manifest


def _verify_paper_and_license(output_dir: Path) -> None:
    pdf = (output_dir / "PAPER_ARXIV_2409.09918V2.pdf").read_bytes()
    if len(pdf) != PAPER_BYTES or _sha256(pdf) != PAPER_SHA256:
        raise A0Error("STORED_PAPER_PDF_MISMATCH")
    if not pdf.startswith(b"%PDF-") or not pdf.rstrip().endswith(b"%%EOF"):
        raise A0Error("STORED_PAPER_NOT_COMPLETE_PDF")
    html = (output_dir / "PAPER_ABS_V2.html").read_text(encoding="utf-8")
    for marker in (
        "[2409.09918v2] Hardware-Accelerated Ray Tracing",
        "arXiv:2409.09918v2",
        ICRA_DOI,
        'citation_author" content="Sui, Sizhe"',
        'citation_author" content="Sentis, Luis"',
        'citation_author" content="Bylard, Andrew"',
    ):
        if marker not in html:
            raise A0Error(f"PAPER_ABS_MARKER_MISSING:{marker}")
    pdf_headers = (output_dir / "PAPER_PDF_HTTP_HEADERS.txt").read_text(encoding="utf-8")
    if "HTTP/2 200" not in pdf_headers or f"content-length: {PAPER_BYTES}" not in pdf_headers:
        raise A0Error("PAPER_PDF_HTTP_RECEIPT_MISMATCH")
    pdfinfo = (output_dir / "PAPER_PDFINFO.txt").read_text(encoding="utf-8")
    for marker in ("Pages:           10", "Encrypted:       no", "JavaScript:      no"):
        if marker not in pdfinfo:
            raise A0Error(f"PAPER_PDFINFO_MISMATCH:{marker}")
    license_bytes = (output_dir / "AUTHOR_LICENSE.txt").read_bytes()
    if len(license_bytes) != 1066 or _git_oid("blob", license_bytes) != "0ec3c9a8cb0bb8fe2de6ad03ca465ccd12e1c4a5":
        raise A0Error("AUTHOR_LICENSE_BLOB_MISMATCH")
    license_text = license_bytes.decode("utf-8")
    if not license_text.startswith("MIT License\n") or "Copyright (c) 2025 Sizhe Sui" not in license_text:
        raise A0Error("AUTHOR_LICENSE_NOT_EXPECTED_MIT_TEXT")


def validate_policy(document: dict[str, Any]) -> None:
    if document.get("schema") != "rtdl.goal5836.a0.source_acquisition_authority.v1":
        raise A0Error("AUTHORITY_SCHEMA_MISMATCH")
    if document.get("status") != "PASS__EXACT_SOURCE_BYTES_ACQUIRED_AND_HASHED__A1_LOCKED":
        raise A0Error("AUTHORITY_STATUS_MISMATCH")
    authorization = document.get("authorization", {})
    if authorization != AUTHORIZATION:
        raise A0Error("AUTHORIZATION_DOCUMENT_MISMATCH")
    expected_true = {"a0_owner_authorized", "a0_acquisition_completed", "a0_authorization_consumed"}
    if {key for key, value in authorization.items() if value} != expected_true:
        raise A0Error("AUTHORITY_SCOPE_EXPANSION")
    if document.get("next_owner_gate") != "AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY":
        raise A0Error("NEXT_OWNER_GATE_MISMATCH")
    observation = document.get("a0_observation", {})
    for field in (
        "author_build_count",
        "author_execution_count",
        "rtdl_goal5836_execution_count",
        "gpu_worker_count",
        "timing_count",
        "performance_result_count",
    ):
        if observation.get(field) != 0:
            raise A0Error(f"UNAUTHORIZED_A0_OBSERVATION:{field}")
    if observation.get("author_source_semantics_inspected") is not False:
        raise A0Error("A1_SEMANTIC_INSPECTION_LEAKED_INTO_A0")
    if observation.get("source_fidelity_classification_made") is not False:
        raise A0Error("A1_CLASSIFICATION_LEAKED_INTO_A0")
    if observation.get("paper_method_text_incidentally_exposed_by_discovery_tool") is not True:
        raise A0Error("PAPER_DISCOVERY_EXPOSURE_NOT_DISCLOSED")
    paper = document.get("paper_identity", {})
    if paper.get("publisher_pdf_acquired") is not False or paper.get("sha256") != PAPER_SHA256:
        raise A0Error("PAPER_CLAIM_BOUNDARY_MISMATCH")
    source = document.get("author_source_identity", {})
    if source.get("planned_commit") != AUTHOR_COMMIT or source.get("observed_commit") != AUTHOR_COMMIT:
        raise A0Error("AUTHOR_COMMIT_AUTHORITY_MISMATCH")
    if source.get("root_tree_git_oid_sha1") != AUTHOR_ROOT_TREE or source.get("commit_pin_changed") is not False:
        raise A0Error("AUTHOR_TREE_AUTHORITY_MISMATCH")
    claim = document.get("claim_boundary", {})
    if claim != CLAIM_BOUNDARY:
        raise A0Error("SCIENTIFIC_LABEL_OR_CLAIM_DRIFT")
    seal = document.get("source_acquisition_authority_sha256")
    if not isinstance(seal, str) or not re.fullmatch(r"[0-9a-f]{64}", seal) or seal != _seal(document):
        raise A0Error("AUTHORITY_SEAL_MISMATCH")


def verify_stored(output_dir: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    _verify_static_pins()
    if not output_dir.is_dir() or output_dir.is_symlink():
        raise A0Error("STORED_OUTPUT_NOT_DIRECTORY")
    actual_names = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected_names = sorted((*PRESERVED_FILENAMES, AUTHORITY_FILENAME))
    if actual_names != expected_names:
        raise A0Error("STORED_OUTPUT_PATH_SET_MISMATCH")
    _verify_paper_and_license(output_dir)
    inventory = _verify_inventory(output_dir)
    selected = _verify_selected_capsule(output_dir, inventory)
    commit_object = (output_dir / "AUTHOR_COMMIT_OBJECT.txt").read_bytes()
    if _git_oid("commit", commit_object) != AUTHOR_COMMIT:
        raise A0Error("STORED_COMMIT_OBJECT_MISMATCH")
    if f"tree {AUTHOR_ROOT_TREE}\n".encode("ascii") not in commit_object:
        raise A0Error("STORED_COMMIT_TREE_LINK_MISMATCH")
    fetch = json.loads((output_dir / "FETCH_RECEIPT.json").read_text(encoding="ascii"))
    if fetch != _fetch_receipt():
        raise A0Error("FETCH_RECEIPT_MISMATCH")
    authority_path = output_dir / AUTHORITY_FILENAME
    authority = json.loads(authority_path.read_text(encoding="ascii"))
    validate_policy(authority)
    expected = _build_authority(output_dir)
    if authority != expected:
        raise A0Error("STORED_AUTHORITY_EXACT_DOCUMENT_MISMATCH")
    if selected["root_tree_git_oid_sha1"] != inventory["root_tree_git_oid_sha1"]:
        raise A0Error("SELECTED_SOURCE_TREE_BINDING_MISMATCH")
    return authority


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-stored", action="store_true")
    parser.add_argument("--acquire-build", action="store_true")
    parser.add_argument("--author-repo", type=Path)
    parser.add_argument("--paper-pdf", type=Path)
    parser.add_argument("--paper-abs-html", type=Path)
    parser.add_argument("--paper-pdf-headers", type=Path)
    parser.add_argument("--paper-abs-headers", type=Path)
    parser.add_argument("--paper-pdfinfo", type=Path)
    args = parser.parse_args()
    if args.verify_stored == args.acquire_build:
        parser.error("choose exactly one of --verify-stored or --acquire-build")
    if args.acquire_build:
        required = (
            args.author_repo,
            args.paper_pdf,
            args.paper_abs_html,
            args.paper_pdf_headers,
            args.paper_abs_headers,
            args.paper_pdfinfo,
        )
        if any(value is None for value in required):
            parser.error("--acquire-build requires all source input paths")
        authority = acquire_build(
            author_repo=args.author_repo,
            paper_pdf=args.paper_pdf,
            paper_abs_html=args.paper_abs_html,
            paper_pdf_headers=args.paper_pdf_headers,
            paper_abs_headers=args.paper_abs_headers,
            paper_pdfinfo=args.paper_pdfinfo,
            output_dir=args.output_dir,
        )
        status = "CREATE_ONLY_GOAL5836_A0_ACQUISITION_PASS__A1_LOCKED"
    else:
        authority = verify_stored(args.output_dir)
        status = "POSTWRITE_GOAL5836_A0_VERIFY_PASS__A1_LOCKED"
    print(
        json.dumps(
            {
                "status": status,
                "authority_sha256": _sha256((args.output_dir / AUTHORITY_FILENAME).read_bytes()),
                "authority_seal": authority["source_acquisition_authority_sha256"],
                "paper_sha256": authority["paper_identity"]["sha256"],
                "author_commit": authority["author_source_identity"]["observed_commit"],
                "author_root_tree": authority["author_source_identity"]["root_tree_git_oid_sha1"],
                "author_file_count": authority["author_source_identity"]["file_count"],
                "authorized_next_stage_count": 0,
                "worker_count": 0,
                "timing_count": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
