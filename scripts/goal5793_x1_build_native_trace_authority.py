"""Freeze the exact non-GPU native-build trace and every surviving input byte.

The builder consumes an already completed ``strace -ff`` directory.  It does
not build, execute the native library, access a GPU, or use the network.  Every
successful read/exec path which still exists is either cross-bound to the
frozen source root or copied into a deterministic evidence archive.  Missing
non-temporary inputs fail closed.
"""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


SCHEMA = "rtdl.goal5793.x1.native_trace_authority.v1"
FORBIDDEN_GPU_MARKERS = ("nvidia-smi", "/dev/nvidia", "libnvidia-ml")
OPEN_RE = re.compile(r'openat\([^,]+, "((?:\\.|[^"\\])*)", ([^)]*)\) = (-?\d+)')
EXEC_RE = re.compile(r'execve\("((?:\\.|[^"\\])*)", (\[.*\]), .*\) = 0$')
CHDIR_RE = re.compile(r'chdir\("((?:\\.|[^"\\])*)"\) = 0$')


class TraceAuthorityError(ValueError):
    pass


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_strace_string(payload: str) -> str:
    try:
        value = ast.literal_eval('"' + payload + '"')
    except (SyntaxError, ValueError) as exc:
        raise TraceAuthorityError("strace_string_decode_failed") from exc
    if not isinstance(value, str) or "..." in value:
        raise TraceAuthorityError("strace_string_truncated_or_invalid")
    return value


def _regular(path: Path, context: str) -> Path:
    if not path.is_absolute() or not path.exists():
        raise TraceAuthorityError(f"{context}_absent")
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise TraceAuthorityError(f"{context}_not_regular")
    return resolved


def _record(path: Path, declared: str) -> dict[str, object]:
    resolved = _regular(path, "record")
    return {
        "declared_path": declared,
        "resolved_path": str(resolved),
        "declared_path_is_symlink": path.is_symlink(),
        "declared_symlink_target": os.readlink(path) if path.is_symlink() else None,
        "bytes": resolved.stat().st_size,
        "sha256": _sha256(resolved),
    }


def _tar_bytes(payloads: dict[str, bytes]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name in sorted(payloads, key=lambda value: value.encode("utf-8")):
            data = payloads[name]
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o444
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    output = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=0, compresslevel=9) as stream:
        stream.write(raw.getvalue())
    return output.getvalue()


def _relative_or_none(path: Path, root: Path) -> str | None:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return None


def _parse_trace(trace_root: Path, initial_cwd: Path) -> dict[str, Any]:
    traces = sorted(
        (path for path in trace_root.iterdir() if path.is_file() and not path.is_symlink()),
        key=lambda value: value.name.encode("utf-8"),
    )
    if not traces:
        raise TraceAuthorityError("trace_set_empty")
    trace_rows: list[dict[str, object]] = []
    accesses: list[dict[str, object]] = []
    successful_execs: list[dict[str, object]] = []
    forbidden_hits: list[dict[str, object]] = []
    for trace in traces:
        payload = trace.read_bytes()
        trace_rows.append({"path": trace.name, "bytes": len(payload), "sha256": _sha256_bytes(payload)})
        text = payload.decode("utf-8", errors="strict")
        cwd = initial_cwd
        for line_number, line in enumerate(text.splitlines(), 1):
            lowered = line.lower()
            for marker in FORBIDDEN_GPU_MARKERS:
                if marker in lowered:
                    forbidden_hits.append({"trace": trace.name, "line": line_number, "marker": marker})
            match = CHDIR_RE.search(line)
            if match:
                value = Path(_decode_strace_string(match.group(1)))
                cwd = value if value.is_absolute() else cwd / value
                cwd = cwd.resolve(strict=False)
                continue
            match = EXEC_RE.search(line)
            if match:
                declared = _decode_strace_string(match.group(1))
                try:
                    argv = ast.literal_eval(match.group(2))
                except (SyntaxError, ValueError) as exc:
                    raise TraceAuthorityError("exec_argv_parse_failed") from exc
                if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
                    raise TraceAuthorityError("exec_argv_not_string_list")
                path = Path(declared)
                absolute = path if path.is_absolute() else cwd / path
                successful_execs.append(
                    {"trace": trace.name, "line": line_number, "path": str(absolute), "argv": argv}
                )
                accesses.append({"kind": "exec", "path": str(absolute), "trace": trace.name, "line": line_number})
                continue
            match = OPEN_RE.search(line)
            if match and int(match.group(3)) >= 0:
                flags = match.group(2)
                if "O_WRONLY" in flags and "O_RDWR" not in flags:
                    continue
                declared = _decode_strace_string(match.group(1))
                path = Path(declared)
                absolute = path if path.is_absolute() else cwd / path
                accesses.append({"kind": "read", "path": str(absolute), "trace": trace.name, "line": line_number})
    if forbidden_hits:
        raise TraceAuthorityError("gpu_or_discovery_access_in_trace")
    return {
        "trace_files": trace_rows,
        "trace_file_set_sha256": _sha256_bytes(canonical_json_bytes(trace_rows)),
        "accesses": accesses,
        "successful_execs": successful_execs,
        "forbidden_gpu_marker_hits": forbidden_hits,
    }


def build(
    *,
    trace_root: Path,
    initial_cwd: Path,
    source_root: Path,
    source_bundle: Path,
    reference_native: Path,
    traced_native: Path,
    reference_stripped: Path,
    traced_stripped: Path,
) -> tuple[dict[str, Any], bytes]:
    trace_root = trace_root.resolve(strict=True)
    initial_cwd = initial_cwd.resolve(strict=True)
    source_root = source_root.resolve(strict=True)
    source_bundle = _regular(source_bundle, "source_bundle")
    native_paths = {
        "reference_unstripped": _regular(reference_native, "reference_native"),
        "traced_unstripped": _regular(traced_native, "traced_native"),
        "reference_stripped": _regular(reference_stripped, "reference_stripped"),
        "traced_stripped": _regular(traced_stripped, "traced_stripped"),
    }
    if _sha256(native_paths["reference_stripped"]) != _sha256(native_paths["traced_stripped"]):
        raise TraceAuthorityError("stripped_rebuilds_not_byte_identical")

    parsed = _parse_trace(trace_root, initial_cwd)
    top_nvcc = [
        row
        for row in parsed["successful_execs"]
        if row["path"] == "/usr/bin/nvcc" and "-shared" in row["argv"] and "-arch=sm_61" in row["argv"]
    ]
    if len(top_nvcc) != 1:
        raise TraceAuthorityError("exact_top_level_nvcc_exec_not_unique")

    by_declared: dict[str, dict[str, object]] = {}
    ephemeral: set[str] = set()
    source_rows: dict[str, dict[str, object]] = {}
    snapshot_rows: dict[str, dict[str, object]] = {}
    snapshot_payloads: dict[str, bytes] = {}
    native_resolved = {value.resolve(strict=True) for value in native_paths.values()}
    for access in parsed["accesses"]:
        declared = str(access["path"])
        candidate = Path(declared)
        if declared.startswith("/tmp/"):
            ephemeral.add(declared)
            continue
        if not candidate.exists():
            raise TraceAuthorityError(f"non_temporary_access_missing_after_trace:{declared}")
        resolved = candidate.resolve(strict=True)
        if not resolved.is_file():
            continue
        if resolved in native_resolved:
            continue
        source_rel = _relative_or_none(resolved, source_root)
        row = _record(candidate, declared)
        row["access_kinds"] = sorted(
            {str(item["kind"]) for item in parsed["accesses"] if str(item["path"]) == declared}
        )
        if source_rel is not None:
            row["source_relative_path"] = source_rel
            source_rows[declared] = row
            continue
        digest = str(row["sha256"])
        member = f"inputs/{digest}"
        row["snapshot_member"] = member
        by_declared[declared] = row
        snapshot_rows[digest] = {
            "member": member,
            "bytes": row["bytes"],
            "sha256": digest,
        }
        if member not in snapshot_payloads:
            snapshot_payloads[member] = resolved.read_bytes()

    trace_payloads = {
        f"traces/{path.name}": path.read_bytes()
        for path in sorted(trace_root.iterdir(), key=lambda value: value.name.encode("utf-8"))
        if path.is_file() and not path.is_symlink()
    }
    artifact_payloads = {
        f"artifacts/{role}.so": path.read_bytes() for role, path in native_paths.items()
    }
    source_payloads = {"source/source326.tar.gz": source_bundle.read_bytes()}
    payloads = {**snapshot_payloads, **trace_payloads, **artifact_payloads, **source_payloads}

    input_rows = sorted(by_declared.values(), key=lambda row: str(row["declared_path"]).encode("utf-8"))
    source_input_rows = sorted(source_rows.values(), key=lambda row: str(row["declared_path"]).encode("utf-8"))
    content_rows = sorted(snapshot_rows.values(), key=lambda row: str(row["member"]).encode("utf-8"))
    archive = _tar_bytes(payloads)
    authority: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "NON_GPU_DIRECT_BUILD_TRACE_AND_SURVIVING_INPUT_BYTES_FROZEN__NO_EXECUTION_AUTHORIZATION",
        "trace": {
            "root": str(trace_root),
            "file_count": len(parsed["trace_files"]),
            "files": parsed["trace_files"],
            "file_set_sha256": parsed["trace_file_set_sha256"],
            "forbidden_gpu_markers": list(FORBIDDEN_GPU_MARKERS),
            "forbidden_gpu_marker_hit_count": 0,
        },
        "top_level_nvcc": top_nvcc[0],
        "source": {
            "root": str(source_root),
            "bundle": _record(source_bundle, str(source_bundle)),
            "accessed_file_count": len(source_input_rows),
            "accessed_files": source_input_rows,
        },
        "surviving_external_inputs": {
            "declared_path_count": len(input_rows),
            "unique_content_count": len(content_rows),
            "declared_paths": input_rows,
            "content_rows": content_rows,
            "declared_path_set_sha256": _sha256_bytes(canonical_json_bytes(input_rows)),
            "content_set_sha256": _sha256_bytes(canonical_json_bytes(content_rows)),
        },
        "ephemeral_intermediates": {
            "policy": "TMP_PATHS_ARE_BUILD_GENERATED_INTERMEDIATES__NOT_PREEXISTING_INPUT_AUTHORITY",
            "path_count": len(ephemeral),
            "paths": sorted(ephemeral, key=lambda value: value.encode("utf-8")),
        },
        "native_rebuilds": {
            role: _record(path, str(path)) for role, path in sorted(native_paths.items())
        },
        "stripped_rebuilds_byte_identical": True,
        "evidence_archive": {
            "payload_count": len(payloads),
            "payload_bytes": sum(len(value) for value in payloads.values()),
            "bytes": len(archive),
            "sha256": _sha256_bytes(archive),
        },
        "scope": {
            "build_performed_by_this_builder": False,
            "network_calls": 0,
            "gpu_calls": 0,
            "candidate_work": 0,
            "registered_timing": 0,
            "execution_authorized": False,
            "search_entropy_selection_authorized": False,
            "publication_authorized": False,
            "symlink_topology_reconstructed": False,
            "resolved_input_bytes_preserved": True,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = seal_document(
        authority,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.native_trace_authority",
        version=1,
    )
    return authority, archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--initial-cwd", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-bundle", type=Path, required=True)
    parser.add_argument("--reference-native", type=Path, required=True)
    parser.add_argument("--traced-native", type=Path, required=True)
    parser.add_argument("--reference-stripped", type=Path, required=True)
    parser.add_argument("--traced-stripped", type=Path, required=True)
    parser.add_argument("--output-authority", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument("--output-twin", type=Path, required=True)
    args = parser.parse_args()
    outputs = (args.output_authority, args.output_archive, args.output_twin)
    if any(path.exists() or path.is_symlink() for path in outputs):
        raise TraceAuthorityError("create_only_output_exists")
    authority, archive = build(
        trace_root=args.trace_root,
        initial_cwd=args.initial_cwd,
        source_root=args.source_root,
        source_bundle=args.source_bundle,
        reference_native=args.reference_native,
        traced_native=args.traced_native,
        reference_stripped=args.reference_stripped,
        traced_stripped=args.traced_stripped,
    )
    authority_bytes = canonical_json_bytes(authority) + b"\n"
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_authority.open("xb") as handle:
        handle.write(authority_bytes)
    with args.output_archive.open("xb") as handle:
        handle.write(archive)
    with args.output_twin.open("xb") as handle:
        handle.write(archive)
    print(authority["status"], authority["authority_sha256"], authority["evidence_archive"]["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
