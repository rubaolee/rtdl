#!/usr/bin/env python3
"""Independently verify a Goal5802 exact shallow-Git source packet.

The verifier extracts only an allowlisted regular-file Git database into a
fresh temporary directory, verifies the complete commit/tree/path/mode/blob
authority and shallow boundary, then checks out with ``core.autocrlf=false``.
Every work-tree file is matched to its Git blob (SHA-1, SHA-256, and length),
the index modes are exact, POSIX execute bits are checked where representable,
and Git status must be clean.

Actual private-key bytes and values are supplied out of band for a value-based
scan.  Source code is allowed to mention private-key field names; names alone
are not evidence of leaked material.
"""

from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
from typing import Iterable
import zipfile


MANIFEST_SCHEMA = "rtdl.goal5802.exact_shallow_git_source_packet_manifest.v1"
PACKET_SCHEMA = "rtdl.goal5802.exact_shallow_git_source_packet.v1"
RECEIPT_SCHEMA = "rtdl.goal5802.exact_shallow_git_source_packet_verification.v1"
ALLOWED_MODES = {"100644", "100755"}
PRIVATE_COMPONENT_KEYS = {
    "d",
    "private_exponent",
    "private_exponent_base64",
    "private_key",
    "private_key_base64",
    "private_key_pem",
    "rsa_d",
    "rsa_private_exponent",
    "rsa_private_exponent_base64",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ARCHIVE_SUFFIXES = (".tar.gz", ".tgz", ".tar", ".zip", ".whl", ".gz")
UNSUPPORTED_CONTAINER_SUFFIXES = (
    ".7z", ".rar", ".tar.bz2", ".tbz2", ".bz2", ".tar.xz", ".txz", ".xz", ".zst",
)
MAX_PRIVATE_SCAN_BYTES = 16 * 1024 * 1024 * 1024
MAX_PRIVATE_SCAN_PAYLOADS = 1_000_000
MAX_PRIVATE_SCAN_DEPTH = 8
BARE_CONFIG = (
    b"[core]\n"
    b"\trepositoryformatversion = 0\n"
    b"\tfilemode = true\n"
    b"\tbare = true\n"
    b"\tlogallrefupdates = false\n"
    b"\tautocrlf = false\n"
    b"\teol = lf\n"
    b"\tsafecrlf = true\n"
    b"[pack]\n"
    b"\twriteReverseIndex = false\n"
)
DIRECTORIES = {
    "repository",
    "repository/objects",
    "repository/objects/pack",
    "repository/refs",
    "repository/refs/heads",
}
MANIFEST_KEYS = {
    "forbidden_private_key_file_count",
    "forbidden_private_key_file_sha256",
    "forbidden_private_value_sha256",
    "packet_bytes",
    "packet_member_count",
    "packet_members",
    "packet_pax_comment",
    "packet_schema",
    "packet_sha256",
    "private_material_scan_container_count",
    "private_material_scan_expanded_bytes",
    "private_material_scan_payload_count",
    "registered_performance_timing_count",
    "schema",
    "source_commit",
    "source_entry_count",
    "source_full_ls_tree_z_bytes",
    "source_full_ls_tree_z_sha256",
    "source_inventory",
    "source_inventory_sha256",
    "source_object_format",
    "source_tree",
    "status",
    "unregistered_timing_count",
    "worker_count",
}
RECEIPT_KEYS = {
    "checkout_clean",
    "checkout_core_autocrlf",
    "checkout_file_blob_match_count",
    "checkout_index_mode_match_count",
    "detached_private_scan_authority_bytes",
    "detached_private_scan_authority_sha256",
    "forbidden_private_key_file_count",
    "forbidden_private_key_file_sha256",
    "forbidden_private_key_value_match_count",
    "forbidden_private_value_sha256",
    "manifest_bytes",
    "manifest_sha256",
    "materialize_root",
    "materialized_checkout_relative_path",
    "materialized_repository_relative_path",
    "materialized_source_root",
    "materialized_source_tree",
    "packet_bytes",
    "packet_sha256",
    "posix_filesystem_mode_match_count",
    "posix_filesystem_modes_verified",
    "private_material_scan_container_count",
    "private_material_scan_expanded_bytes",
    "private_material_scan_payload_count",
    "private_material_value_scan_executed",
    "private_material_value_scan_mode",
    "registered_performance_timing_count",
    "schema",
    "shallow_commit_count",
    "source_commit",
    "source_entry_count",
    "source_tree",
    "status",
    "unregistered_timing_count",
    "worker_count",
}


def _git_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for key in tuple(environment):
        if key.startswith("GIT_"):
            environment.pop(key)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _read_manifest(path: Path) -> dict[str, object]:
    payload = path.resolve(strict=True).read_bytes()
    if not payload.endswith(b"\n") or payload.endswith(b"\n\n"):
        raise RuntimeError("manifest must be canonical JSON plus one terminal LF")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("manifest is not valid UTF-8 JSON") from error
    if not isinstance(value, dict) or _canonical(value) + b"\n" != payload:
        raise RuntimeError("manifest is not canonical JSON")
    if set(value) != MANIFEST_KEYS:
        raise RuntimeError("manifest key set mismatch")
    return value


def _safe_path(value: str, *, prefix: str | None = None) -> PurePosixPath:
    if not isinstance(value, str):
        raise RuntimeError("path must be a string")
    path = PurePosixPath(value)
    parts = value.split("/")
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or "\r" in value
        or "\n" in value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
        or (prefix is not None and (not path.parts or path.parts[0] != prefix))
    ):
        raise RuntimeError(f"unsafe packet path: {value!r}")
    return path


def _validate_manifest(manifest: dict[str, object]) -> tuple[list[dict[str, str]], dict[str, dict[str, object]]]:
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["packet_schema"] != PACKET_SCHEMA:
        raise RuntimeError("source packet schema mismatch")
    if manifest["status"] != "PASS__EXACT_SELF_CONTAINED_DEPTH_ONE_GIT_SOURCE_PACKET":
        raise RuntimeError("source packet status mismatch")
    for key in (
        "registered_performance_timing_count", "unregistered_timing_count", "worker_count",
    ):
        if type(manifest[key]) is not int or manifest[key] != 0:
            raise RuntimeError(f"nonzero or invalid {key}")
    for key in (
        "private_material_scan_container_count",
        "private_material_scan_expanded_bytes",
        "private_material_scan_payload_count",
    ):
        if type(manifest[key]) is not int or manifest[key] < 0:
            raise RuntimeError(f"invalid {key}")
    commit = manifest["source_commit"]
    tree = manifest["source_tree"]
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        raise RuntimeError("invalid source commit")
    if not isinstance(tree, str) or not HEX40.fullmatch(tree):
        raise RuntimeError("invalid source tree")
    if manifest["source_object_format"] != "sha1":
        raise RuntimeError("unsupported source object format")
    if manifest["packet_pax_comment"] != commit:
        raise RuntimeError("packet PAX commit does not bind source commit")
    if type(manifest["packet_bytes"]) is not int or manifest["packet_bytes"] <= 0:
        raise RuntimeError("invalid packet byte count")
    if not isinstance(manifest["packet_sha256"], str) or not HEX64.fullmatch(manifest["packet_sha256"]):
        raise RuntimeError("invalid packet SHA-256")
    for key in ("source_full_ls_tree_z_bytes", "source_entry_count"):
        if type(manifest[key]) is not int or manifest[key] <= 0:
            raise RuntimeError(f"invalid {key}")
    for key in (
        "source_full_ls_tree_z_sha256", "source_inventory_sha256",
    ):
        if not isinstance(manifest[key], str) or not HEX64.fullmatch(manifest[key]):
            raise RuntimeError(f"invalid {key}")
    for key in (
        "forbidden_private_key_file_sha256", "forbidden_private_value_sha256",
    ):
        values = manifest[key]
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(value, str) or not HEX64.fullmatch(value) for value in values)
            or values != sorted(set(values))
        ):
            raise RuntimeError(f"invalid {key}")
    if (
        type(manifest["forbidden_private_key_file_count"]) is not int
        or manifest["forbidden_private_key_file_count"]
        != len(manifest["forbidden_private_key_file_sha256"])
    ):
        raise RuntimeError("invalid forbidden private-key file count")

    raw_rows = manifest["source_inventory"]
    if not isinstance(raw_rows, list) or not raw_rows:
        raise RuntimeError("empty or invalid source inventory")
    rows: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict) or set(raw_row) != {"mode", "object_id", "path", "type"}:
            raise RuntimeError("source inventory row schema mismatch")
        mode = raw_row["mode"]
        object_id = raw_row["object_id"]
        path = raw_row["path"]
        object_type = raw_row["type"]
        if mode not in ALLOWED_MODES or object_type != "blob":
            raise RuntimeError("source inventory contains non-regular entry")
        if not isinstance(object_id, str) or not HEX40.fullmatch(object_id):
            raise RuntimeError("source inventory object id mismatch")
        if not isinstance(path, str):
            raise RuntimeError("source inventory path type mismatch")
        safe = _safe_path(path)
        if ".git" in safe.parts:
            raise RuntimeError("source inventory contains .git path")
        if path in seen_paths:
            raise RuntimeError("duplicate source inventory path")
        seen_paths.add(path)
        rows.append({
            "mode": mode,
            "object_id": object_id,
            "path": path,
            "type": object_type,
        })
    if rows != sorted(rows, key=lambda row: row["path"].encode("utf-8")):
        raise RuntimeError("source inventory is not path ordered")
    if type(manifest["source_entry_count"]) is not int or manifest["source_entry_count"] != len(rows):
        raise RuntimeError("source entry count mismatch")
    if manifest["source_inventory_sha256"] != _sha256(_canonical(rows)):
        raise RuntimeError("source inventory digest mismatch")

    raw_members = manifest["packet_members"]
    if not isinstance(raw_members, list) or not raw_members:
        raise RuntimeError("empty or invalid packet member manifest")
    members: dict[str, dict[str, object]] = {}
    for raw_member in raw_members:
        if not isinstance(raw_member, dict) or set(raw_member) != {"bytes", "mode", "path", "sha256"}:
            raise RuntimeError("packet member schema mismatch")
        path = raw_member["path"]
        if not isinstance(path, str):
            raise RuntimeError("packet member path type mismatch")
        _safe_path(path, prefix="repository")
        if path in members:
            raise RuntimeError("duplicate packet member path")
        if type(raw_member["bytes"]) is not int or raw_member["bytes"] < 0:
            raise RuntimeError("packet member size mismatch")
        if raw_member["mode"] not in {"0444", "0644"}:
            raise RuntimeError("packet member mode mismatch")
        if not isinstance(raw_member["sha256"], str) or not HEX64.fullmatch(raw_member["sha256"]):
            raise RuntimeError("packet member SHA-256 mismatch")
        members[path] = raw_member
    if type(manifest["packet_member_count"]) is not int or manifest["packet_member_count"] != len(members):
        raise RuntimeError("packet member count mismatch")
    required = {
        "repository/HEAD", "repository/config", "repository/shallow",
        "repository/refs/heads/packet",
    }
    if not required.issubset(members):
        raise RuntimeError("packet is missing required Git database files")
    pack_paths = [path for path in members if path.startswith("repository/objects/pack/")]
    if len([path for path in pack_paths if path.endswith(".pack")]) != 1:
        raise RuntimeError("packet must contain exactly one pack")
    if len([path for path in pack_paths if path.endswith(".idx")]) != 1:
        raise RuntimeError("packet must contain exactly one pack index")
    if any(not path.endswith((".pack", ".idx")) for path in pack_paths):
        raise RuntimeError("unexpected pack-side file")
    if any(path not in required and path not in pack_paths for path in members):
        raise RuntimeError("unexpected Git database file in packet")
    return rows, members


def _walk_private_components(value: object) -> Iterable[bytes]:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                continue
            normalized = key.strip().lower().replace("-", "_")
            if normalized in PRIVATE_COMPONENT_KEYS:
                if isinstance(child, str):
                    yield child.encode("utf-8")
                elif isinstance(child, int) and not isinstance(child, bool):
                    yield str(child).encode("ascii")
            yield from _walk_private_components(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_private_components(child)


def _private_material(path: Path) -> tuple[bytes, list[bytes]]:
    payload = path.resolve(strict=True).read_bytes()
    if not payload:
        raise RuntimeError(f"empty forbidden private-key file: {path}")
    tokens: set[bytes] = {payload}
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        document = None
    if document is not None:
        tokens.update(
            token for token in _walk_private_components(document) if len(token) >= 16)
    for match in re.finditer(
        rb"-----BEGIN [^-\r\n]*PRIVATE KEY-----.*?"
        rb"-----END [^-\r\n]*PRIVATE KEY-----",
        payload,
        flags=re.DOTALL,
    ):
        tokens.add(match.group(0))
    if len(tokens) == 1 and len(payload) < 32:
        raise RuntimeError("forbidden private-key file has no safely matchable material")
    return payload, sorted(tokens, key=lambda item: (_sha256(item), len(item)))


def _looks_like_container(label: str, prefix: bytes) -> bool:
    lowered = label.lower()
    return (
        lowered.endswith(ARCHIVE_SUFFIXES)
        or prefix.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08", b"\x1f\x8b"))
        or (len(prefix) >= 263 and prefix[257:263] in {b"ustar\x00", b"ustar "})
    )


def _reject_unsupported_container(label: str, prefix: bytes) -> None:
    lowered = label.lower()
    if (
        lowered.endswith(UNSUPPORTED_CONTAINER_SUFFIXES)
        or prefix.startswith((b"7z\xbc\xaf'\x1c", b"Rar!\x1a\x07", b"BZh", b"\xfd7zXZ\x00", b"(\xb5/\xfd"))
    ):
        raise RuntimeError(
            f"unsupported compressed container cannot be private-value scanned: {label}")


def _scan_private_stream(
    stream: object,
    label: str,
    private_file_hashes: set[str],
    private_tokens: list[bytes],
    statistics: dict[str, int],
    depth: int,
) -> None:
    if depth > MAX_PRIVATE_SCAN_DEPTH:
        raise RuntimeError(f"private-material archive nesting exceeds limit at {label}")
    statistics["payload_count"] += 1
    if statistics["payload_count"] > MAX_PRIVATE_SCAN_PAYLOADS:
        raise RuntimeError("private-material scan payload-count limit exceeded")
    digest = hashlib.sha256()
    nonempty = [token for token in private_tokens if token]
    overlap = max((len(token) for token in nonempty), default=1) - 1
    tail = b""
    spool: object | None = None
    first = True
    try:
        while True:
            chunk = stream.read(1024 * 1024)  # type: ignore[attr-defined]
            if not chunk:
                break
            if first:
                first = False
                _reject_unsupported_container(label, chunk)
                if _looks_like_container(label, chunk):
                    spool = tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024)
            if spool is not None:
                spool.write(chunk)  # type: ignore[attr-defined]
            statistics["bytes"] += len(chunk)
            if statistics["bytes"] > MAX_PRIVATE_SCAN_BYTES:
                raise RuntimeError("private-material expanded-byte scan limit exceeded")
            digest.update(chunk)
            window = tail + chunk
            if any(token in window for token in nonempty):
                raise RuntimeError(f"actual private-key value present in {label}")
            tail = window[-overlap:] if overlap else b""
        if digest.hexdigest() in private_file_hashes:
            raise RuntimeError(f"exact private-key file present in {label}")
        if spool is not None:
            spool.seek(0)  # type: ignore[attr-defined]
            _scan_private_container(
                spool, label, private_file_hashes, private_tokens, statistics, depth)
    finally:
        if spool is not None:
            spool.close()  # type: ignore[attr-defined]


def _scan_private_container(
    stream: object,
    label: str,
    private_file_hashes: set[str],
    private_tokens: list[bytes],
    statistics: dict[str, int],
    depth: int,
) -> None:
    statistics["container_count"] += 1
    stream.seek(0)  # type: ignore[attr-defined]
    if zipfile.is_zipfile(stream):
        stream.seek(0)  # type: ignore[attr-defined]
        with zipfile.ZipFile(stream) as archive:
            occurrences: dict[str, int] = {}
            for info in archive.infolist():
                occurrence = occurrences.get(info.filename, 0) + 1
                occurrences[info.filename] = occurrence
                if info.is_dir():
                    continue
                if info.flag_bits & 0x1:
                    raise RuntimeError(f"encrypted nested ZIP member in {label}")
                with archive.open(info, "r") as member_stream:
                    _scan_private_stream(
                        member_stream,
                        f"{label}!{info.filename}[occurrence={occurrence}]",
                        private_file_hashes,
                        private_tokens,
                        statistics,
                        depth + 1,
                    )
        return
    stream.seek(0)  # type: ignore[attr-defined]
    try:
        archive = tarfile.open(fileobj=stream, mode="r:*")
    except tarfile.ReadError:
        archive = None
    if archive is not None:
        with archive:
            occurrences = {}
            for member in archive:
                occurrence = occurrences.get(member.name, 0) + 1
                occurrences[member.name] = occurrence
                if not member.isfile():
                    continue
                member_stream = archive.extractfile(member)
                if member_stream is None:
                    raise RuntimeError(f"unreadable nested TAR member in {label}")
                with member_stream:
                    _scan_private_stream(
                        member_stream,
                        f"{label}!{member.name}[occurrence={occurrence}]",
                        private_file_hashes,
                        private_tokens,
                        statistics,
                        depth + 1,
                    )
        return
    stream.seek(0)  # type: ignore[attr-defined]
    prefix = stream.read(2)  # type: ignore[attr-defined]
    stream.seek(0)  # type: ignore[attr-defined]
    if prefix == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=stream, mode="rb") as uncompressed:
            _scan_private_stream(
                uncompressed,
                f"{label}!gzip-payload",
                private_file_hashes,
                private_tokens,
                statistics,
                depth + 1,
            )
        return
    raise RuntimeError(f"recognized archive payload is malformed or unsupported: {label}")


def _hash_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def _file_contains_any(path: Path, tokens: list[bytes]) -> bool:
    nonempty = [token for token in tokens if token]
    if not nonempty:
        return False
    overlap = max(len(token) for token in nonempty) - 1
    tail = b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            window = tail + chunk
            if any(token in window for token in nonempty):
                return True
            tail = window[-overlap:] if overlap else b""
    return False


def _extract_packet(
    packet_path: Path,
    commit: str,
    expected_members: dict[str, dict[str, object]],
    destination: Path,
) -> Path:
    seen: set[str] = set()
    seen_directories: set[str] = set()
    with tarfile.open(packet_path, mode="r:gz") as archive:
        if archive.pax_headers != {
            "comment": commit,
            "rtdl.goal5802.schema": PACKET_SCHEMA,
        }:
            raise RuntimeError("packet global PAX commit/schema mismatch")
        for member in archive:
            normalized = member.name.rstrip("/")
            _safe_path(normalized, prefix="repository")
            if normalized in seen:
                raise RuntimeError("duplicate packet archive member")
            seen.add(normalized)
            if (
                member.pax_headers != archive.pax_headers
                or member.mtime != 0
                or member.uid != 0
                or member.gid != 0
                or member.uname != ""
                or member.gname != ""
            ):
                raise RuntimeError("packet archive canonical metadata mismatch")
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                raise RuntimeError("packet archive contains link or special member")
            if member.isdir():
                if normalized not in DIRECTORIES or member.size != 0 or (member.mode & 0o7777) != 0o755:
                    raise RuntimeError("packet archive directory mismatch")
                seen_directories.add(normalized)
                (destination / Path(*PurePosixPath(normalized).parts)).mkdir(
                    parents=True, exist_ok=False)
                continue
            if not member.isreg() or normalized not in expected_members:
                raise RuntimeError("unexpected non-regular packet archive member")
            expected = expected_members[normalized]
            if member.size != expected["bytes"] or f"{member.mode & 0o7777:04o}" != expected["mode"]:
                raise RuntimeError("packet archive member metadata mismatch")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError("packet archive member has no payload")
            target = destination / Path(*PurePosixPath(normalized).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                raise RuntimeError("packet archive target already exists")
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, member.mode & 0o777)
            digest = hashlib.sha256()
            size = 0
            with os.fdopen(descriptor, "wb") as output:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            if size != expected["bytes"] or digest.hexdigest() != expected["sha256"]:
                raise RuntimeError("packet archive member payload mismatch")
        if seen_directories != DIRECTORIES:
            raise RuntimeError("packet archive directory set mismatch")
        if seen - seen_directories != set(expected_members):
            raise RuntimeError("packet archive file set mismatch")
    return destination / "repository"


def _run_git(git_directory: Path, *arguments: str, work_tree: Path | None = None) -> bytes:
    command = [
        "git",
        "-c", "core.autocrlf=false",
        "-c", "core.safecrlf=true",
        # Required for exact checkouts of already-committed paths beyond the
        # legacy Windows MAX_PATH boundary; harmless and non-persistent on
        # Linux.  This changes no packet-local configuration byte.
        "-c", "core.longpaths=true",
        "--git-dir", str(git_directory),
    ]
    if work_tree is not None:
        command.extend(["-c", "core.bare=false", "--work-tree", str(work_tree)])
    command.extend(arguments)
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=_git_environment(),
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _parse_git_inventory(payload: bytes) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_row in payload.split(b"\0"):
        if not raw_row:
            continue
        try:
            left, raw_path = raw_row.split(b"\t", 1)
            mode, object_type, object_id = (
                item.decode("ascii") for item in left.split(b" ", 2))
            path = raw_path.decode("utf-8", errors="strict")
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("malformed packet Git inventory") from error
        _safe_path(path)
        rows.append({
            "mode": mode,
            "object_id": object_id,
            "path": path,
            "type": object_type,
        })
    return rows


def _all_reachable_object_ids(git_directory: Path, commit: str) -> set[str]:
    payload = _run_git(
        git_directory, "ls-tree", "-r", "-t", "-z", "--full-tree", commit)
    root_tree = _run_git(git_directory, "rev-parse", f"{commit}^{{tree}}") \
        .decode("ascii").strip()
    object_ids = {commit, root_tree}
    for raw_row in payload.split(b"\0"):
        if not raw_row:
            continue
        try:
            left, raw_path = raw_row.split(b"\t", 1)
            _mode, object_type, object_id = left.split(b" ", 2)
            path = raw_path.decode("utf-8", errors="strict")
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("malformed packet recursive object inventory") from error
        _safe_path(path)
        if object_type not in {b"tree", b"blob"}:
            raise RuntimeError("unsupported packet Git object type")
        decoded = object_id.decode("ascii")
        if not HEX40.fullmatch(decoded):
            raise RuntimeError("invalid packet Git object id")
        object_ids.add(decoded)
    return object_ids


def _stored_object_ids(git_directory: Path) -> set[str]:
    payload = _run_git(
        git_directory,
        "cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)",
    )
    result: set[str] = set()
    for line in payload.splitlines():
        parts = line.split(b" ")
        if len(parts) != 2 or parts[1] not in {b"commit", b"tree", b"blob"}:
            raise RuntimeError("unexpected stored Git object")
        object_id = parts[0].decode("ascii")
        if not HEX40.fullmatch(object_id) or object_id in result:
            raise RuntimeError("invalid or duplicate stored Git object")
        result.add(object_id)
    return result


def _scan_git_blobs(
    git_directory: Path,
    rows: list[dict[str, str]],
    private_files: list[bytes],
    private_tokens: list[bytes],
) -> tuple[dict[str, tuple[int, str]], dict[str, int]]:
    object_to_path: dict[str, str] = {}
    for row in rows:
        object_to_path.setdefault(row["object_id"], row["path"])
    process = subprocess.Popen(
        ["git", "--git-dir", str(git_directory), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_git_environment(),
    )
    assert process.stdin is not None and process.stdout is not None
    result: dict[str, tuple[int, str]] = {}
    statistics = {"bytes": 0, "container_count": 0, "payload_count": 0}
    private_file_hashes = {_sha256(payload) for payload in private_files}
    try:
        for object_id in sorted(object_to_path):
            process.stdin.write(object_id.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().rstrip(b"\n").split(b" ")
            if len(header) != 3 or header[0].decode("ascii") != object_id or header[1] != b"blob":
                raise RuntimeError("packet cat-file response mismatch")
            size = int(header[2])
            payload = process.stdout.read(size)
            trailer = process.stdout.read(1)
            if len(payload) != size or trailer != b"\n" or _git_blob_sha1(payload) != object_id:
                raise RuntimeError("packet Git blob payload mismatch")
            path = object_to_path[object_id]
            _scan_private_stream(
                io.BytesIO(payload),
                path,
                private_file_hashes,
                private_tokens,
                statistics,
                0,
            )
            result[object_id] = (size, _sha256(payload))
        process.stdin.close()
        return_code = process.wait()
        if return_code != 0:
            error = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
            raise RuntimeError(f"git cat-file failed: {error}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()
    return result, statistics


def _parse_index(payload: bytes) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_row in payload.split(b"\0"):
        if not raw_row:
            continue
        try:
            left, raw_path = raw_row.split(b"\t", 1)
            mode, object_id, stage = (part.decode("ascii") for part in left.split(b" ", 2))
            path = raw_path.decode("utf-8", errors="strict")
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("malformed checkout index row") from error
        if stage != "0":
            raise RuntimeError("non-stage-zero checkout index entry")
        _safe_path(path)
        rows.append({"mode": mode, "object_id": object_id, "path": path, "type": "blob"})
    return rows


def _host_inspection_root(path: Path) -> Path:
    """Return an exact Windows extended-length spelling for local inspection."""
    absolute = path.absolute()
    if os.name != "nt":
        return absolute
    value = str(absolute)
    if value.startswith("\\\\?\\"):
        return absolute
    if value.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + value[2:])
    return Path("\\\\?\\" + value)


@contextlib.contextmanager
def _temporary_directory(*, prefix: str, directory: str | None):
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=directory))
    try:
        yield str(path)
    finally:
        if path.exists():
            def remove_readonly(function, target, _exception):
                os.chmod(target, stat.S_IRWXU)
                function(target)

            shutil.rmtree(
                _host_inspection_root(path), onexc=remove_readonly)


def _working_paths(work_tree: Path) -> set[str]:
    paths: set[str] = set()
    for directory, directory_names, file_names in os.walk(work_tree, followlinks=False):
        root = Path(directory)
        for name in directory_names:
            candidate = root / name
            if candidate.is_symlink():
                raise RuntimeError("checkout contains a symlink directory")
        for name in file_names:
            candidate = root / name
            if candidate.is_symlink() or not candidate.is_file():
                raise RuntimeError("checkout contains a link or non-regular file")
            relative = candidate.relative_to(work_tree).as_posix()
            _safe_path(relative)
            if relative in paths:
                raise RuntimeError("duplicate checkout path")
            paths.add(relative)
    return paths


def _verify_working_files(
    work_tree: Path,
    rows: list[dict[str, str]],
    blob_hashes: dict[str, tuple[int, str]],
) -> tuple[int, int]:
    work_tree = _host_inspection_root(work_tree)
    expected_paths = {row["path"] for row in rows}
    if _working_paths(work_tree) != expected_paths:
        raise RuntimeError("checkout path set mismatch")
    posix_mode_checks = 0
    for row in rows:
        path = work_tree / Path(*PurePosixPath(row["path"]).parts)
        stat_result = path.stat()
        expected_size, expected_sha256 = blob_hashes[row["object_id"]]
        if stat_result.st_size != expected_size:
            raise RuntimeError(f"checkout file size mismatch: {row['path']}")
        sha1 = hashlib.sha1(f"blob {stat_result.st_size}\0".encode("ascii"))
        sha256 = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha1.update(chunk)
                sha256.update(chunk)
        if sha1.hexdigest() != row["object_id"] or sha256.hexdigest() != expected_sha256:
            raise RuntimeError(f"checkout bytes differ from Git blob: {row['path']}")
        if os.name != "nt":
            executable = bool(stat_result.st_mode & 0o111)
            if executable != (row["mode"] == "100755"):
                raise RuntimeError(f"checkout executable mode mismatch: {row['path']}")
            posix_mode_checks += 1
    return len(rows), posix_mode_checks


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _read_detached_private_scan_authority(
    path: Path,
    expected_sha256: str,
    manifest: dict[str, object],
    manifest_bytes: int,
    manifest_sha256: str,
) -> tuple[int, str]:
    if not HEX64.fullmatch(expected_sha256):
        raise RuntimeError("invalid expected detached private-scan authority SHA-256")
    payload = path.resolve(strict=True).read_bytes()
    if _sha256(payload) != expected_sha256:
        raise RuntimeError("detached private-scan authority byte identity mismatch")
    if not payload.endswith(b"\n") or payload.endswith(b"\n\n"):
        raise RuntimeError("detached private-scan authority is not canonical-LF JSON")
    try:
        authority = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError("detached private-scan authority is not UTF-8 JSON") from error
    if (
        not isinstance(authority, dict)
        or set(authority) != RECEIPT_KEYS
        or _canonical(authority) + b"\n" != payload
    ):
        raise RuntimeError("detached private-scan authority schema/canonicalization mismatch")
    exact = {
        "checkout_clean": True,
        "checkout_core_autocrlf": False,
        "checkout_file_blob_match_count": manifest["source_entry_count"],
        "checkout_index_mode_match_count": manifest["source_entry_count"],
        "detached_private_scan_authority_bytes": None,
        "detached_private_scan_authority_sha256": None,
        "forbidden_private_key_file_count": manifest["forbidden_private_key_file_count"],
        "forbidden_private_key_file_sha256": manifest["forbidden_private_key_file_sha256"],
        "forbidden_private_key_value_match_count": 0,
        "forbidden_private_value_sha256": manifest["forbidden_private_value_sha256"],
        "manifest_bytes": manifest_bytes,
        "manifest_sha256": manifest_sha256,
        "packet_bytes": manifest["packet_bytes"],
        "packet_sha256": manifest["packet_sha256"],
        "private_material_scan_container_count": manifest[
            "private_material_scan_container_count"],
        "private_material_scan_expanded_bytes": manifest[
            "private_material_scan_expanded_bytes"],
        "private_material_scan_payload_count": manifest[
            "private_material_scan_payload_count"],
        "private_material_value_scan_executed": True,
        "private_material_value_scan_mode": (
            "EXECUTED_WITH_EXACT_OWNER_LOCAL_PRIVATE_KEY"),
        "registered_performance_timing_count": 0,
        "schema": RECEIPT_SCHEMA,
        "shallow_commit_count": 1,
        "source_commit": manifest["source_commit"],
        "source_entry_count": manifest["source_entry_count"],
        "source_tree": manifest["source_tree"],
        "status": "PASS__INDEPENDENT_EXACT_SHALLOW_GIT_CHECKOUT_VERIFIED",
        "unregistered_timing_count": 0,
        "worker_count": 0,
    }
    for key, expected in exact.items():
        if authority.get(key) != expected:
            raise RuntimeError(f"detached private-scan authority mismatch: {key}")
    return len(payload), expected_sha256


def verify(
    packet_path: Path,
    manifest_path: Path,
    forbidden_private_key_paths: list[Path] | None = None,
    *,
    private_scan_authority_path: Path | None = None,
    private_scan_authority_sha256: str | None = None,
    materialize_root: Path | None = None,
) -> dict[str, object]:
    packet_path = packet_path.resolve(strict=True)
    manifest_path = manifest_path.resolve(strict=True)
    manifest = _read_manifest(manifest_path)
    manifest_bytes, manifest_sha256 = _hash_file(manifest_path)
    rows, members = _validate_manifest(manifest)
    packet_size, packet_sha256 = _hash_file(packet_path)
    if packet_size != manifest["packet_bytes"] or packet_sha256 != manifest["packet_sha256"]:
        raise RuntimeError("packet byte identity mismatch")
    key_paths = list(forbidden_private_key_paths or [])
    local_private_scan = bool(key_paths)
    detached_private_scan = private_scan_authority_path is not None
    if local_private_scan == detached_private_scan:
        raise RuntimeError(
            "choose exactly one private scan mode: exact local keys or detached authority")
    if local_private_scan and private_scan_authority_sha256 is not None:
        raise RuntimeError("detached authority SHA-256 is invalid in exact local-key mode")
    if detached_private_scan and private_scan_authority_sha256 is None:
        raise RuntimeError("detached private-scan authority requires its exact SHA-256")
    private_files: list[bytes] = []
    private_tokens: list[bytes] = []
    private_file_hashes: list[str] = []
    detached_authority_bytes: int | None = None
    detached_authority_sha256: str | None = None
    if local_private_scan:
        resolved_key_paths = [path.resolve(strict=True) for path in key_paths]
        if len(set(resolved_key_paths)) != len(resolved_key_paths):
            raise RuntimeError("duplicate forbidden private-key path")
        for path in resolved_key_paths:
            payload, tokens = _private_material(path)
            private_files.append(payload)
            private_tokens.extend(tokens)
            private_file_hashes.append(_sha256(payload))
        if len(set(private_file_hashes)) != len(private_file_hashes):
            raise RuntimeError("duplicate forbidden private-key identity")
        private_tokens = sorted(
            set(private_tokens), key=lambda item: (_sha256(item), len(item)))
        if sorted(private_file_hashes) != manifest["forbidden_private_key_file_sha256"]:
            raise RuntimeError("forbidden private-key file authority mismatch")
        if sorted(_sha256(token) for token in private_tokens) != manifest[
                "forbidden_private_value_sha256"]:
            raise RuntimeError("forbidden private-key value authority mismatch")
        if manifest["forbidden_private_key_file_count"] != len(private_file_hashes):
            raise RuntimeError("forbidden private-key file count mismatch")
        if _file_contains_any(packet_path, private_tokens):
            raise RuntimeError("raw packet bytes contain actual private-key material")
    else:
        assert private_scan_authority_path is not None
        assert private_scan_authority_sha256 is not None
        detached_authority_bytes, detached_authority_sha256 = (
            _read_detached_private_scan_authority(
                private_scan_authority_path,
                private_scan_authority_sha256,
                manifest,
                manifest_bytes,
                manifest_sha256,
            ))

    materialized_root: Path | None = None
    temporary_parent: str | None = None
    if materialize_root is not None:
        materialized_root = materialize_root.resolve()
        if materialized_root.exists() or materialized_root.is_symlink():
            raise FileExistsError(materialized_root)
        materialized_root.parent.mkdir(parents=True, exist_ok=True)
        temporary_parent = str(materialized_root.parent)

    with _temporary_directory(
        prefix=".goal5802-source-verify-",
        directory=temporary_parent,
    ) as temporary:
        temporary_root = Path(temporary)
        git_directory = _extract_packet(
            packet_path,
            str(manifest["source_commit"]),
            members,
            temporary_root,
        )
        if (git_directory / "config").read_bytes() != BARE_CONFIG:
            raise RuntimeError("packet Git configuration byte identity mismatch")
        for key, expected in (
            ("core.bare", "true"),
            ("core.autocrlf", "false"),
            ("core.eol", "lf"),
            ("core.filemode", "true"),
            ("core.safecrlf", "true"),
            ("pack.writeReverseIndex", "false"),
        ):
            observed = _run_git(git_directory, "config", "--local", "--get", key) \
                .decode("utf-8").strip()
            if observed != expected:
                raise RuntimeError(f"packet Git configuration mismatch: {key}")
        commit = _run_git(git_directory, "rev-parse", "HEAD").decode("ascii").strip()
        tree = _run_git(git_directory, "rev-parse", "HEAD^{tree}").decode("ascii").strip()
        if commit != manifest["source_commit"] or tree != manifest["source_tree"]:
            raise RuntimeError("packet HEAD/tree mismatch")
        commit_payload = _run_git(git_directory, "cat-file", "commit", commit)
        if any(commit_payload == forbidden for forbidden in private_files):
            raise RuntimeError("exact private-key file used as Git commit object")
        if any(token and token in commit_payload for token in private_tokens):
            raise RuntimeError("actual private-key value present in Git commit object")
        for row in rows:
            encoded_path = row["path"].encode("utf-8")
            if any(token and token in encoded_path for token in private_tokens):
                raise RuntimeError("actual private-key value present in Git path")
        if (git_directory / "shallow").read_bytes() != commit.encode("ascii") + b"\n":
            raise RuntimeError("packet shallow boundary file mismatch")
        if _run_git(git_directory, "rev-parse", "--is-shallow-repository").strip() != b"true":
            raise RuntimeError("packet repository is not shallow")
        if _run_git(git_directory, "rev-list", "--count", "HEAD").strip() != b"1":
            raise RuntimeError("packet repository exposes more than one commit")
        if _run_git(git_directory, "rev-list", "--parents", "HEAD").strip() != commit.encode("ascii"):
            raise RuntimeError("packet shallow history boundary mismatch")
        _run_git(git_directory, "fsck", "--full", "--strict", "--no-reflogs")

        inventory_bytes = _run_git(
            git_directory, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
        if (
            len(inventory_bytes) != manifest["source_full_ls_tree_z_bytes"]
            or _sha256(inventory_bytes) != manifest["source_full_ls_tree_z_sha256"]
        ):
            raise RuntimeError("packet recursive ls-tree byte authority mismatch")
        if _parse_git_inventory(inventory_bytes) != rows:
            raise RuntimeError("packet recursive ls-tree inventory mismatch")
        if _stored_object_ids(git_directory) != _all_reachable_object_ids(git_directory, commit):
            raise RuntimeError("packet Git database has missing or unreachable extra objects")
        blob_hashes, private_scan = _scan_git_blobs(
            git_directory, rows, private_files, private_tokens)
        if private_scan != {
            "bytes": manifest["private_material_scan_expanded_bytes"],
            "container_count": manifest["private_material_scan_container_count"],
            "payload_count": manifest["private_material_scan_payload_count"],
        }:
            raise RuntimeError("private-material recursive scan recount mismatch")

        work_tree = temporary_root / "checkout"
        work_tree.mkdir()
        _run_git(git_directory, "checkout", "--force", "HEAD", "--", ".", work_tree=work_tree)
        index_rows = _parse_index(
            _run_git(git_directory, "ls-files", "--stage", "-z", work_tree=work_tree))
        if index_rows != rows:
            raise RuntimeError("checkout index path/mode/blob inventory mismatch")
        file_checks, posix_mode_checks = _verify_working_files(work_tree, rows, blob_hashes)
        status_arguments = ["status", "--porcelain=v1", "--untracked-files=all"]
        if os.name == "nt":
            # Windows has no POSIX execute bit.  Index modes remain exact and
            # are checked above; filemode=false only prevents a false dirty
            # status caused by the host filesystem.
            status_arguments = ["-c", "core.filemode=false", *status_arguments]
        if _run_git(git_directory, *status_arguments, work_tree=work_tree):
            raise RuntimeError("reconstructed checkout is not clean")
        if materialized_root is not None:
            # The temporary root was created beside the requested destination;
            # rename is therefore a create-only same-filesystem publication.
            if materialized_root.exists() or materialized_root.is_symlink():
                raise FileExistsError(materialized_root)
            os.rename(temporary_root, materialized_root)

    receipt: dict[str, object] = {
        "checkout_clean": True,
        "checkout_core_autocrlf": False,
        "checkout_file_blob_match_count": file_checks,
        "checkout_index_mode_match_count": len(rows),
        "detached_private_scan_authority_bytes": detached_authority_bytes,
        "detached_private_scan_authority_sha256": detached_authority_sha256,
        "forbidden_private_key_file_count": manifest[
            "forbidden_private_key_file_count"],
        "forbidden_private_key_file_sha256": manifest[
            "forbidden_private_key_file_sha256"],
        "forbidden_private_key_value_match_count": 0,
        "forbidden_private_value_sha256": manifest[
            "forbidden_private_value_sha256"],
        "manifest_bytes": manifest_bytes,
        "manifest_sha256": manifest_sha256,
        "materialize_root": (
            str(materialized_root) if materialized_root is not None else None),
        "materialized_checkout_relative_path": (
            "checkout" if materialized_root is not None else None),
        "materialized_repository_relative_path": (
            "repository" if materialized_root is not None else None),
        "materialized_source_root": materialized_root is not None,
        "materialized_source_tree": (
            manifest["source_tree"] if materialized_root is not None else None),
        "packet_bytes": packet_size,
        "packet_sha256": packet_sha256,
        "posix_filesystem_mode_match_count": posix_mode_checks,
        "posix_filesystem_modes_verified": os.name != "nt",
        "private_material_scan_container_count": private_scan["container_count"],
        "private_material_scan_expanded_bytes": private_scan["bytes"],
        "private_material_scan_payload_count": private_scan["payload_count"],
        "private_material_value_scan_executed": local_private_scan,
        "private_material_value_scan_mode": (
            "EXECUTED_WITH_EXACT_OWNER_LOCAL_PRIVATE_KEY"
            if local_private_scan
            else "NOT_REEXECUTED__DETACHED_LOCAL_AUTHORITY_VERIFIED"),
        "registered_performance_timing_count": 0,
        "schema": RECEIPT_SCHEMA,
        "shallow_commit_count": 1,
        "source_commit": manifest["source_commit"],
        "source_entry_count": len(rows),
        "source_tree": manifest["source_tree"],
        "status": "PASS__INDEPENDENT_EXACT_SHALLOW_GIT_CHECKOUT_VERIFIED",
        "unregistered_timing_count": 0,
        "worker_count": 0,
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    private_mode = parser.add_mutually_exclusive_group(required=True)
    private_mode.add_argument(
        "--forbidden-private-key-file",
        type=Path,
        action="append",
        dest="forbidden_private_key_files",
    )
    private_mode.add_argument("--private-scan-authority", type=Path)
    parser.add_argument("--private-scan-authority-sha256")
    parser.add_argument("--materialize-root", type=Path)
    args = parser.parse_args()
    receipt = verify(
        args.packet,
        args.manifest,
        args.forbidden_private_key_files,
        private_scan_authority_path=args.private_scan_authority,
        private_scan_authority_sha256=args.private_scan_authority_sha256,
        materialize_root=args.materialize_root,
    )
    payload = _canonical(receipt) + b"\n"
    _write_create_only(args.receipt.resolve(), payload)
    print(json.dumps(receipt, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
