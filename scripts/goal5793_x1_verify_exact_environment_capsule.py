"""Independently verify the Goal5793 X1 exact-environment capsule."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any
import zlib

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


MANIFEST_SCHEMA = "rtdl.goal5793.x1.exact_environment_capsule_manifest.v1"
AUDIT_SCHEMA = "rtdl.goal5793.x1.exact_environment_capsule_audit.v1"
EMBEDDED_MANIFEST = "GOAL5793_X1_EXACT_ENVIRONMENT_CAPSULE_MANIFEST.json"
GZIP_HEADER = bytes.fromhex("1f8b08000000000002ff")


class VerificationError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _safe_name(name: str) -> bool:
    return bool(name) and "\\" not in name and all(part not in ("", ".", "..") for part in name.split("/"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _verify_single_canonical_gzip(path: Path) -> None:
    with path.open("rb") as handle:
        _require(handle.read(10) == GZIP_HEADER, "gzip_header_not_canonical")
        handle.seek(0)
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            inflater.decompress(chunk)
            _require(not inflater.unused_data, "gzip_trailing_or_concatenated_stream")
        inflater.flush()
        _require(inflater.eof, "gzip_stream_incomplete")
        _require(not inflater.unused_data and not inflater.unconsumed_tail, "gzip_stream_not_single_exact")


def _payload_set_digest(rows: list[dict[str, Any]]) -> str:
    projection = [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in rows]
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def verify(*, archive_path: Path, twin_path: Path, manifest_path: Path, audit_path: Path) -> dict[str, Any]:
    for path in (archive_path, twin_path, manifest_path, audit_path):
        _require(path.is_file() and not path.is_symlink(), f"input_not_regular:{path}")
    archive_identity = _identity(archive_path)
    twin_identity = _identity(twin_path)
    _require(archive_identity == twin_identity, "archive_twin_identity_mismatch")
    _verify_single_canonical_gzip(archive_path)
    _verify_single_canonical_gzip(twin_path)

    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    _require(manifest_bytes == canonical_json_bytes(manifest) + b"\n", "manifest_not_canonical")
    _require(manifest.get("schema") == MANIFEST_SCHEMA, "manifest_schema_mismatch")
    expected_manifest_seal = seal_document(
        manifest, seal_field="manifest_sha256",
        domain="rtdl.goal5793.x1.exact_environment_capsule_manifest", version=1,
    )
    _require(manifest.get("manifest_sha256") == expected_manifest_seal, "manifest_seal_mismatch")
    rows = manifest.get("rows")
    _require(isinstance(rows, list), "manifest_rows_not_list")
    expected_row_keys = {"path", "bytes", "sha256", "source_path"}
    _require(all(isinstance(row, dict) and set(row) == expected_row_keys for row in rows), "manifest_row_schema_mismatch")
    names = [row["path"] for row in rows]
    _require(all(isinstance(name, str) and _safe_name(name) for name in names), "manifest_unsafe_path")
    _require(names == sorted(names, key=lambda value: value.encode("utf-8")), "manifest_rows_not_sorted")
    _require(len(names) == len(set(names)), "manifest_duplicate_path")
    _require(all(isinstance(row["bytes"], int) and row["bytes"] >= 0 for row in rows), "manifest_invalid_bytes")
    _require(all(isinstance(row["sha256"], str) and len(row["sha256"]) == 64 for row in rows), "manifest_invalid_sha")
    _require(manifest.get("payload_count") == len(rows), "manifest_payload_count_mismatch")
    _require(manifest.get("payload_bytes") == sum(row["bytes"] for row in rows), "manifest_payload_bytes_mismatch")
    _require(manifest.get("payload_set_sha256") == _payload_set_digest(rows), "manifest_payload_set_mismatch")
    _require(manifest.get("claim_boundary") == {
        "execution_result_count": 0,
        "generality_exam_count": 0,
        "native_build_environment_vector_fully_reconstructed": False,
        "usability_evidence_count": 0,
    }, "manifest_claim_boundary_mismatch")
    expected_authorization = {
        "execution": False,
        "gpu_home_pod_ssh": False,
        "publication_or_submission": False,
        "registered_or_performance_timing": False,
        "search_entropy_selection": False,
    }
    _require(manifest.get("authorization") == expected_authorization, "manifest_authorization_mismatch")

    row_by_name = {row["path"]: row for row in rows}
    observed_names: list[str] = []
    embedded: bytes | None = None
    inner: dict[str, bytes] = {}
    wanted = {
        "authority/request.json", "authority/exact_environment.json",
        "evidence/native_trace.tar.gz", "evidence/native_trace_twin.tar.gz",
    }
    with tarfile.open(archive_path, mode="r:gz") as archive:
        _require(not archive.pax_headers, "archive_global_pax_forbidden")
        members = archive.getmembers()
        _require([member.name for member in members] == names + [EMBEDDED_MANIFEST], "archive_member_order_or_set_mismatch")
        for member in members:
            _require(member.isfile(), f"archive_nonregular_member:{member.name}")
            _require(_safe_name(member.name), f"archive_unsafe_member:{member.name}")
            _require((member.mode, member.uid, member.gid, member.mtime) == (0o444, 0, 0, 0), f"archive_metadata_mismatch:{member.name}")
            _require((member.uname, member.gname) == ("", ""), f"archive_names_metadata_mismatch:{member.name}")
            _require(not member.pax_headers, f"archive_member_pax_forbidden:{member.name}")
            extracted = archive.extractfile(member)
            _require(extracted is not None, f"archive_member_unreadable:{member.name}")
            digest = hashlib.sha256()
            count = 0
            retained = bytearray() if member.name in wanted or member.name == EMBEDDED_MANIFEST else None
            for chunk in iter(lambda: extracted.read(1024 * 1024), b""):
                digest.update(chunk)
                count += len(chunk)
                if retained is not None:
                    retained.extend(chunk)
            if member.name == EMBEDDED_MANIFEST:
                embedded = bytes(retained or b"")
                _require(count == len(manifest_bytes) and digest.hexdigest() == hashlib.sha256(manifest_bytes).hexdigest(), "embedded_manifest_identity_mismatch")
            else:
                observed_names.append(member.name)
                row = row_by_name[member.name]
                _require(count == row["bytes"] and digest.hexdigest() == row["sha256"], f"archive_payload_identity_mismatch:{member.name}")
                if retained is not None:
                    inner[member.name] = bytes(retained)
    _require(observed_names == names and embedded == manifest_bytes, "archive_projection_mismatch")
    _require(inner["evidence/native_trace.tar.gz"] == inner["evidence/native_trace_twin.tar.gz"], "embedded_trace_twin_mismatch")
    environment = json.loads(inner["authority/exact_environment.json"])
    request = json.loads(inner["authority/request.json"])
    _require(environment.get("schema") == "rtdl.goal5793.x1.exact_environment_capture.v2", "embedded_environment_schema_mismatch")
    expected_environment_seal = seal_document(
        environment, seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.exact_environment_capture", version=2,
    )
    _require(environment.get("authority_sha256") == expected_environment_seal, "embedded_environment_seal_mismatch")
    _require(environment.get("request_sha256") == hashlib.sha256(canonical_json_bytes(request)).hexdigest(), "embedded_request_crossbind_mismatch")

    audit_bytes = audit_path.read_bytes()
    audit = json.loads(audit_bytes)
    _require(audit_bytes == canonical_json_bytes(audit) + b"\n", "audit_not_canonical")
    _require(audit.get("schema") == AUDIT_SCHEMA, "audit_schema_mismatch")
    expected_audit_seal = seal_document(
        audit, seal_field="audit_sha256",
        domain="rtdl.goal5793.x1.exact_environment_capsule_audit", version=1,
    )
    _require(audit.get("audit_sha256") == expected_audit_seal, "audit_seal_mismatch")
    _require(audit.get("archive") == {"path": archive_path.name, **archive_identity}, "audit_archive_identity_mismatch")
    _require(audit.get("twin") == {"path": twin_path.name, **twin_identity}, "audit_twin_identity_mismatch")
    _require(audit.get("manifest") == {"path": manifest_path.name, **_identity(manifest_path), "manifest_sha256": manifest["manifest_sha256"]}, "audit_manifest_identity_mismatch")
    _require(audit.get("archive_twin_byte_identical") is True, "audit_twin_claim_mismatch")
    for key in ("payload_count", "payload_bytes", "payload_set_sha256"):
        _require(audit.get(key) == manifest.get(key), f"audit_manifest_{key}_mismatch")
    _require(audit.get("authorization") == expected_authorization, "audit_authorization_mismatch")
    return {
        "status": "INDEPENDENT_EXACT_ENVIRONMENT_CAPSULE_VERIFICATION_PASS",
        "archive": archive_identity,
        "manifest": _identity(manifest_path),
        "audit": _identity(audit_path),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "payload_set_sha256": manifest["payload_set_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(archive_path=args.archive, twin_path=args.twin,
                            manifest_path=args.manifest, audit_path=args.audit), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
