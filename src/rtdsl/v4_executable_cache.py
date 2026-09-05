"""Content-addressed data cache for verified V4 compiler executables.

The cache stores canonical JSON only.  It never serializes a live capability,
native handle, Python object graph, or executable Python code.  A manifest-bound
policy is read-only and binds the exact bytes of every admitted entry.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Mapping


EXECUTABLE_CACHE_ENTRY_SCHEMA = "rtdl.v4.executable_cache_entry.v1"
EXECUTABLE_CACHE_MANIFEST_SCHEMA = "rtdl.v4.executable_cache_manifest.v1"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_MAX_ENTRY_BYTES = 64 << 20
_MAX_MANIFEST_BYTES = 8 << 20


class V4ExecutableCacheError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise V4ExecutableCacheError(f"non-canonical cache value: {exc}") from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_regular_file(path: Path, *, maximum: int, label: str) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise V4ExecutableCacheError(f"cannot open {label}: {exc}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= maximum:
            raise V4ExecutableCacheError(f"{label} size or type is invalid")
        chunks = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1 << 20, remaining))
            if not block:
                raise V4ExecutableCacheError(f"{label} ended during read")
            chunks.append(block)
            remaining -= len(block)
        after = os.fstat(descriptor)
        if (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ) != (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ):
            raise V4ExecutableCacheError(f"{label} changed during read")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _write_create_only(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o644)
    complete = False
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("create-only cache write made no progress")
            view = view[written:]
        os.fsync(descriptor)
        complete = True
    finally:
        os.close(descriptor)
        if not complete:
            path.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class V4ExecutableCachePolicy:
    root: Path
    manifest: Path | None = None
    manifest_sha256: str | None = None

    def __post_init__(self) -> None:
        root = Path(self.root).expanduser().absolute()
        manifest = (
            None
            if self.manifest is None
            else Path(self.manifest).expanduser().absolute()
        )
        if (manifest is None) != (self.manifest_sha256 is None):
            raise ValueError(
                "executable cache manifest and manifest_sha256 are required together"
            )
        if self.manifest_sha256 is not None and _SHA256.fullmatch(
            self.manifest_sha256
        ) is None:
            raise ValueError("executable cache manifest_sha256 must be lowercase SHA-256")
        object.__setattr__(self, "root", root)
        object.__setattr__(self, "manifest", manifest)


def _root(policy: V4ExecutableCachePolicy) -> Path:
    root = policy.root
    if root.is_symlink():
        raise V4ExecutableCacheError("executable cache root may not be a symlink")
    if not root.exists():
        if policy.manifest is not None:
            raise V4ExecutableCacheError("sealed executable cache root is absent")
        root.mkdir(parents=True)
    resolved = root.resolve(strict=True)
    if not resolved.is_dir() or resolved.is_symlink():
        raise V4ExecutableCacheError("executable cache root is not a directory")
    return resolved


def executable_cache_key_sha256(key: Mapping[str, object]) -> str:
    return _sha256_bytes(_canonical(dict(key)))


def _manifest_entry(
    policy: V4ExecutableCachePolicy,
    root: Path,
    key_sha256: str,
) -> Mapping[str, object] | None:
    if policy.manifest is None:
        return None
    manifest = policy.manifest
    assert policy.manifest_sha256 is not None
    manifest_bytes = _read_regular_file(
        manifest,
        maximum=_MAX_MANIFEST_BYTES,
        label="executable cache manifest",
    )
    if _sha256_bytes(manifest_bytes) != policy.manifest_sha256:
        raise V4ExecutableCacheError("executable cache manifest digest differs")
    try:
        document = json.loads(manifest_bytes.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise V4ExecutableCacheError(f"cannot read executable cache manifest: {exc}") from exc
    if not isinstance(document, dict) or set(document) != {
        "schema",
        "cache_root",
        "entry_count",
        "entries_sha256",
        "entries",
    }:
        raise V4ExecutableCacheError("executable cache manifest shape differs")
    rows = document["entries"]
    if (
        document["schema"] != EXECUTABLE_CACHE_MANIFEST_SCHEMA
        or document["cache_root"] != os.fspath(root)
        or not isinstance(rows, list)
        or document["entry_count"] != len(rows)
        or document["entries_sha256"] != _sha256_bytes(_canonical(rows))
    ):
        raise V4ExecutableCacheError("executable cache manifest identity differs")
    matches = [
        row
        for row in rows
        if isinstance(row, dict) and row.get("key_sha256") == key_sha256
    ]
    if len(matches) != 1:
        raise V4ExecutableCacheError("sealed executable cache key is absent or duplicated")
    row = matches[0]
    if set(row) != {
        "key_sha256",
        "artifact_json_sha256",
        "artifact_json_size_bytes",
    }:
        raise V4ExecutableCacheError("executable cache manifest entry shape differs")
    return row


def load_executable_cache_entry(
    policy: V4ExecutableCachePolicy,
    key: Mapping[str, object],
) -> Mapping[str, object] | None:
    root = _root(policy)
    key_document = dict(key)
    key_sha256 = executable_cache_key_sha256(key_document)
    manifest_row = _manifest_entry(policy, root, key_sha256)
    entry_dir = root / key_sha256
    path = entry_dir / "artifact.json"
    if entry_dir.is_symlink() or path.is_symlink():
        raise V4ExecutableCacheError("executable cache entry path is unsafe")
    if not path.exists():
        if manifest_row is not None:
            raise V4ExecutableCacheError("sealed executable cache entry is absent")
        return None
    if not path.is_file():
        raise V4ExecutableCacheError("executable cache entry path is unsafe")
    encoded = _read_regular_file(
        path,
        maximum=_MAX_ENTRY_BYTES,
        label="executable cache entry",
    )
    size = len(encoded)
    file_sha256 = _sha256_bytes(encoded)
    if manifest_row is not None and (
        manifest_row["artifact_json_size_bytes"] != size
        or manifest_row["artifact_json_sha256"] != file_sha256
    ):
        raise V4ExecutableCacheError("sealed executable cache entry bytes differ")
    try:
        document = json.loads(encoded.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise V4ExecutableCacheError(f"cannot read executable cache entry: {exc}") from exc
    if not isinstance(document, dict) or set(document) != {
        "schema",
        "key",
        "key_sha256",
        "payload",
        "payload_sha256",
    }:
        raise V4ExecutableCacheError("executable cache entry shape differs")
    if (
        document["schema"] != EXECUTABLE_CACHE_ENTRY_SCHEMA
        or document["key"] != key_document
        or document["key_sha256"] != key_sha256
        or document["payload_sha256"] != _sha256_bytes(
            _canonical(document["payload"])
        )
    ):
        raise V4ExecutableCacheError("executable cache entry identity differs")
    payload = document["payload"]
    if not isinstance(payload, dict):
        raise V4ExecutableCacheError("executable cache payload must be an object")
    return payload


def store_executable_cache_entry(
    policy: V4ExecutableCachePolicy,
    key: Mapping[str, object],
    payload: Mapping[str, object],
) -> Path:
    if policy.manifest is not None:
        raise V4ExecutableCacheError("sealed executable cache is read-only")
    root = _root(policy)
    key_document = dict(key)
    payload_document = dict(payload)
    key_sha256 = executable_cache_key_sha256(key_document)
    document = {
        "schema": EXECUTABLE_CACHE_ENTRY_SCHEMA,
        "key": key_document,
        "key_sha256": key_sha256,
        "payload": payload_document,
        "payload_sha256": _sha256_bytes(_canonical(payload_document)),
    }
    encoded = _canonical(document) + b"\n"
    if len(encoded) > _MAX_ENTRY_BYTES:
        raise V4ExecutableCacheError("executable cache entry exceeds size limit")
    entry_dir = root / key_sha256
    entry_dir.mkdir(exist_ok=True)
    if entry_dir.is_symlink():
        raise V4ExecutableCacheError("executable cache entry directory is a symlink")
    destination = entry_dir / "artifact.json"
    if destination.exists() or destination.is_symlink():
        existing = load_executable_cache_entry(policy, key)
        if existing != payload_document:
            raise V4ExecutableCacheError("refusing to replace a different cache entry")
        return destination
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="artifact.", suffix=".tmp", dir=entry_dir
    )
    temporary = Path(temporary_name)
    published = False
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Both paths live in one directory.  ``link`` is an atomic
            # create-if-absent publication and therefore cannot replace an
            # entry won by a concurrent compiler process.
            os.link(temporary, destination)
            published = True
        except FileExistsError:
            pass
    finally:
        if temporary.exists():
            temporary.unlink()
    loaded = load_executable_cache_entry(policy, key)
    if loaded != payload_document:
        detail = "published" if published else "concurrent"
        raise V4ExecutableCacheError(
            f"{detail} executable cache entry differs"
        )
    return destination


def materialize_executable_cache_manifest(
    cache_root: str | os.PathLike[str],
    output: str | os.PathLike[str],
) -> Path:
    root = Path(cache_root).expanduser().resolve(strict=True)
    output_path = Path(output).expanduser().absolute()
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"refusing to replace cache manifest: {output_path}")
    rows = []
    for entry_dir in sorted(root.iterdir(), key=lambda item: item.name):
        if entry_dir.is_symlink() or not entry_dir.is_dir() \
                or _SHA256.fullmatch(entry_dir.name) is None:
            raise V4ExecutableCacheError("unexpected executable cache member")
        members = tuple(sorted(item.name for item in entry_dir.iterdir()))
        if members != ("artifact.json",):
            raise V4ExecutableCacheError("unexpected executable cache entry member")
        artifact = entry_dir / "artifact.json"
        rows.append({
            "key_sha256": entry_dir.name,
            "artifact_json_sha256": _sha256_file(artifact),
            "artifact_json_size_bytes": artifact.stat().st_size,
        })
    if not rows:
        raise V4ExecutableCacheError("cannot seal an empty executable cache")
    document = {
        "schema": EXECUTABLE_CACHE_MANIFEST_SCHEMA,
        "cache_root": os.fspath(root),
        "entry_count": len(rows),
        "entries_sha256": _sha256_bytes(_canonical(rows)),
        "entries": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_create_only(output_path, _canonical(document) + b"\n")
    return output_path


__all__ = [
    "V4ExecutableCacheError",
    "V4ExecutableCachePolicy",
    "executable_cache_key_sha256",
    "load_executable_cache_entry",
    "materialize_executable_cache_manifest",
    "store_executable_cache_entry",
]
