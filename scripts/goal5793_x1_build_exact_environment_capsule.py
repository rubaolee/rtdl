"""Build a deterministic, self-contained Goal5793 X1 environment capsule."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
from typing import Any, Iterable

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


MANIFEST_SCHEMA = "rtdl.goal5793.x1.exact_environment_capsule_manifest.v1"
AUDIT_SCHEMA = "rtdl.goal5793.x1.exact_environment_capsule_audit.v1"
EMBEDDED_MANIFEST = "GOAL5793_X1_EXACT_ENVIRONMENT_CAPSULE_MANIFEST.json"


class CapsuleError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _safe_name(name: str) -> None:
    parts = name.split("/")
    if not name or "\\" in name or any(part in ("", ".", "..") for part in parts):
        raise CapsuleError(f"unsafe_member_name:{name}")


def _regular_tree(root: Path, prefix: str) -> Iterable[tuple[str, Path, str]]:
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise CapsuleError(f"tree_root_invalid:{root}")
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().encode("utf-8")):
        if path.is_symlink():
            raise CapsuleError(f"tree_symlink_forbidden:{path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise CapsuleError(f"tree_nonregular_forbidden:{path}")
        relative = path.relative_to(root).as_posix()
        yield f"{prefix}/{relative}", path, str(path)


def _add_file(archive: tarfile.TarFile, name: str, path: Path) -> None:
    info = tarfile.TarInfo(name)
    info.size = path.stat().st_size
    info.mode = 0o444
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    with path.open("rb") as handle:
        archive.addfile(info, handle)


def _add_bytes(archive: tarfile.TarFile, name: str, payload: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    info.mode = 0o444
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(payload))


def _payload_set_digest(rows: list[dict[str, object]]) -> str:
    projection = [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in rows]
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def build(
    *,
    request_path: Path,
    environment_path: Path,
    source_authority_path: Path,
    source_bundle_path: Path,
    trace_authority_path: Path,
    trace_evidence_path: Path,
    trace_twin_path: Path,
    python_home: Path,
    numba_cache: Path,
    cuda_headers: Path,
    optix_headers: Path,
    shared_native: Path,
    tool_paths: list[Path],
    archive_output: Path,
    twin_output: Path,
    manifest_output: Path,
    audit_output: Path,
) -> dict[str, Any]:
    outputs = (archive_output, twin_output, manifest_output, audit_output)
    if any(path.exists() or path.is_symlink() for path in outputs):
        raise CapsuleError("create_only_output_exists")
    exact_files = [
        ("authority/request.json", request_path),
        ("authority/exact_environment.json", environment_path),
        ("authority/s0_source.json", source_authority_path),
        ("authority/native_trace.json", trace_authority_path),
        ("evidence/native_trace.tar.gz", trace_evidence_path),
        ("evidence/native_trace_twin.tar.gz", trace_twin_path),
        ("source/source326.tar.gz", source_bundle_path),
    ]
    for index, path in enumerate(tool_paths):
        exact_files.append((f"tools/{index:02d}_{path.name}", path))
    entries: list[tuple[str, Path, str]] = [(name, path, str(path)) for name, path in exact_files]
    entries.extend(_regular_tree(python_home, "runtime/python_home"))
    entries.extend(_regular_tree(numba_cache, "runtime/numba_cache"))
    entries.extend(_regular_tree(cuda_headers, "runtime/cuda_entry_headers"))
    entries.extend(_regular_tree(optix_headers, "runtime/optix_headers"))
    entries.extend(_regular_tree(shared_native, "runtime/shared_native"))
    entries.sort(key=lambda row: row[0].encode("utf-8"))
    names: set[str] = set()
    rows: list[dict[str, object]] = []
    for name, path, source in entries:
        _safe_name(name)
        if name in names:
            raise CapsuleError(f"duplicate_member_name:{name}")
        names.add(name)
        if not path.is_file() or path.is_symlink():
            raise CapsuleError(f"payload_not_regular:{path}")
        rows.append({"path": name, "bytes": path.stat().st_size, "sha256": _sha256(path), "source_path": source})

    environment = json.loads(environment_path.read_text(encoding="utf-8"))
    if environment.get("schema") != "rtdl.goal5793.x1.exact_environment_capture.v2":
        raise CapsuleError("environment_schema_mismatch")
    expected_seal = seal_document(environment, seal_field="authority_sha256",
                                  domain="rtdl.goal5793.x1.exact_environment_capture", version=2)
    if environment.get("authority_sha256") != expected_seal:
        raise CapsuleError("environment_seal_mismatch")
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if hashlib.sha256(canonical_json_bytes(request)).hexdigest() != environment.get("request_sha256"):
        raise CapsuleError("request_environment_crossbind_mismatch")
    if _sha256(trace_evidence_path) != _sha256(trace_twin_path):
        raise CapsuleError("trace_evidence_twin_mismatch")

    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "status": "EXACT_ENVIRONMENT_BYTES_SELF_CONTAINED__NO_EXECUTION_AUTHORIZATION",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payload_set_sha256": _payload_set_digest(rows),
        "rows": rows,
        "claim_boundary": {
            "execution_result_count": 0,
            "generality_exam_count": 0,
            "usability_evidence_count": 0,
            "native_build_environment_vector_fully_reconstructed": False,
        },
        "authorization": {
            "execution": False,
            "search_entropy_selection": False,
            "gpu_home_pod_ssh": False,
            "registered_or_performance_timing": False,
            "publication_or_submission": False,
        },
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = seal_document(
        manifest, seal_field="manifest_sha256",
        domain="rtdl.goal5793.x1.exact_environment_capsule_manifest", version=1,
    )
    manifest_bytes = canonical_json_bytes(manifest) + b"\n"

    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="goal5793_x1_env_capsule_", suffix=".tar.gz", dir=archive_output.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with temp_path.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
                with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
                    for name, path, _source in entries:
                        _add_file(archive, name, path)
                    _add_bytes(archive, EMBEDDED_MANIFEST, manifest_bytes)
        archive_identity = _identity(temp_path)
        os.replace(temp_path, archive_output)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    shutil.copyfile(archive_output, twin_output)
    manifest_output.write_bytes(manifest_bytes)
    audit: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "status": "EXACT_ENVIRONMENT_CAPSULE_BUILT__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION",
        "archive": {"path": archive_output.name, **archive_identity},
        "twin": {"path": twin_output.name, **_identity(twin_output)},
        "manifest": {"path": manifest_output.name, **_identity(manifest_output), "manifest_sha256": manifest["manifest_sha256"]},
        "archive_twin_byte_identical": _sha256(archive_output) == _sha256(twin_output),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "payload_set_sha256": manifest["payload_set_sha256"],
        "embedded_manifest_name": EMBEDDED_MANIFEST,
        "authorization": manifest["authorization"],
        "audit_sha256": "",
    }
    if not audit["archive_twin_byte_identical"]:
        raise CapsuleError("capsule_twin_mismatch")
    audit["audit_sha256"] = seal_document(
        audit, seal_field="audit_sha256",
        domain="rtdl.goal5793.x1.exact_environment_capsule_audit", version=1,
    )
    audit_output.write_bytes(canonical_json_bytes(audit) + b"\n")
    return audit


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "request", "environment", "source-authority", "source-bundle", "trace-authority",
        "trace-evidence", "trace-twin", "python-home", "numba-cache", "cuda-headers",
        "optix-headers", "shared-native", "archive-output", "twin-output", "manifest-output", "audit-output",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--tool", type=Path, action="append", default=[])
    args = parser.parse_args()
    audit = build(
        request_path=args.request, environment_path=args.environment,
        source_authority_path=args.source_authority, source_bundle_path=args.source_bundle,
        trace_authority_path=args.trace_authority, trace_evidence_path=args.trace_evidence,
        trace_twin_path=args.trace_twin, python_home=args.python_home, numba_cache=args.numba_cache,
        cuda_headers=args.cuda_headers, optix_headers=args.optix_headers, shared_native=args.shared_native,
        tool_paths=args.tool, archive_output=args.archive_output, twin_output=args.twin_output,
        manifest_output=args.manifest_output, audit_output=args.audit_output,
    )
    print(audit["status"], audit["audit_sha256"], audit["archive"]["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
