"""Fail-closed content-addressed reuse for complete RTDL AOT deployments.

The cache sits before compiler/materializer invocation.  It does not decide
what a route means and cannot compile anything itself.  A caller supplies one
fully bound request plus a miss-only producer and an always-run verifier.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

try:
    import fcntl
except ImportError:  # pragma: no cover - Linux formal evidence is mandatory.
    fcntl = None


REQUEST_SCHEMA = "rtdl.v4.exact_aot_build_request.v1"
CACHE_ENTRY_SCHEMA = "rtdl.v4.exact_aot_cache_entry.v1"
REQUIRED_OUTPUT_ROLES = (
    "artifact",
    "authority",
    "trust_head",
    "trust_package",
    "trust_root",
)
_HEX40 = re.compile(r"[0-9a-f]{40}")
_HEX64 = re.compile(r"[0-9a-f]{64}")


class ExactAOTCacheError(RuntimeError):
    """An exact build request or cached deployment failed admission."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _strict_json_loads(payload: bytes) -> object:
    """Decode a cache manifest without ambiguous JSON values."""

    def object_from_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ExactAOTCacheError(
                    f"AOT cache manifest contains duplicate JSON key: {key}"
                )
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise ExactAOTCacheError(
            f"AOT cache manifest contains non-finite JSON value: {value}"
        )

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_from_pairs,
            parse_constant=reject_constant,
        )
    except ExactAOTCacheError:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ExactAOTCacheError("AOT cache manifest is invalid JSON") from error


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _require_sha(value: object, label: str) -> str:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise ExactAOTCacheError(f"{label} is not a SHA-256 identity")
    return value


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\0" in value:
        raise ExactAOTCacheError(f"{label} is not a nonempty string")
    return value


@dataclass(frozen=True, slots=True)
class ExactAOTBuildRequest:
    source_commit: str
    source_tree: str
    family: str
    route_identity: str
    deployment_id: str
    task_semantics_sha256: str
    native_library_sha256: str
    target_sha256: str
    toolchain_sha256: str
    build_roots_sha256: str
    compiler_source_manifest_sha256: str
    signing_policy_sha256: str
    trust_root_file_sha256: str

    def __post_init__(self) -> None:
        if _HEX40.fullmatch(self.source_commit) is None \
                or _HEX40.fullmatch(self.source_tree) is None:
            raise ExactAOTCacheError("AOT request Git identity differs")
        for name in ("family", "route_identity", "deployment_id"):
            _require_string(getattr(self, name), f"request.{name}")
        for name in (
            "task_semantics_sha256",
            "native_library_sha256",
            "target_sha256",
            "toolchain_sha256",
            "build_roots_sha256",
            "compiler_source_manifest_sha256",
            "signing_policy_sha256",
            "trust_root_file_sha256",
        ):
            _require_sha(getattr(self, name), f"request.{name}")

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema": REQUEST_SCHEMA,
            "source_commit": self.source_commit,
            "source_tree": self.source_tree,
            "family": self.family,
            "route_identity": self.route_identity,
            "deployment_id": self.deployment_id,
            "task_semantics_sha256": self.task_semantics_sha256,
            "native_library_sha256": self.native_library_sha256,
            "target_sha256": self.target_sha256,
            "toolchain_sha256": self.toolchain_sha256,
            "build_roots_sha256": self.build_roots_sha256,
            "compiler_source_manifest_sha256": (
                self.compiler_source_manifest_sha256
            ),
            "signing_policy_sha256": self.signing_policy_sha256,
            "trust_root_file_sha256": self.trust_root_file_sha256,
        }

    @property
    def identity_sha256(self) -> str:
        return _sha256_bytes(_canonical(self.to_mapping()))


@dataclass(frozen=True, slots=True)
class VerifiedAOTCacheEntry:
    request_identity_sha256: str
    entry_path: Path
    output_paths: Mapping[str, Path]
    output_sha256: Mapping[str, str]
    cache_hit: bool
    producer_invoked: bool
    verification: object


def _regular_file(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise ExactAOTCacheError(f"{label} is symbolic")
    try:
        metadata = path.stat()
    except OSError as error:
        raise ExactAOTCacheError(f"{label} is absent") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ExactAOTCacheError(f"{label} is not a regular file")
    return path.resolve(strict=True)


def _write_create(path: Path, payload: bytes, *, mode: int = 0o400) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        mode,
    )
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _validate_cache_root(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    absolute.mkdir(parents=True, exist_ok=True)
    if absolute.is_symlink() or not absolute.is_dir():
        raise ExactAOTCacheError("AOT cache root is symbolic or not a directory")
    for name in ("entries", "locks", "staging"):
        child = absolute / name
        child.mkdir(exist_ok=True)
        if child.is_symlink() or not child.is_dir():
            raise ExactAOTCacheError(f"AOT cache {name} root differs")
    return absolute.resolve(strict=True)


def _manifest_payload(
    request: ExactAOTBuildRequest,
    outputs: Mapping[str, Mapping[str, object]],
) -> bytes:
    unsigned = {
        "schema": CACHE_ENTRY_SCHEMA,
        "request": request.to_mapping(),
        "request_identity_sha256": request.identity_sha256,
        "outputs": dict(outputs),
    }
    value = {
        **unsigned,
        "entry_sha256": _sha256_bytes(_canonical(unsigned)),
    }
    return _canonical(value) + b"\n"


def _validate_entry(
    entry: Path,
    request: ExactAOTBuildRequest,
) -> tuple[dict[str, Path], dict[str, str]]:
    if entry.is_symlink() or not entry.is_dir():
        raise ExactAOTCacheError("AOT cache entry is symbolic or absent")
    manifest_path = _regular_file(entry / "manifest.json", "cache manifest")
    raw = manifest_path.read_bytes()
    value = _strict_json_loads(raw)
    if not isinstance(value, dict) or set(value) != {
        "schema",
        "request",
        "request_identity_sha256",
        "outputs",
        "entry_sha256",
    }:
        raise ExactAOTCacheError("AOT cache manifest fields differ")
    unsigned = dict(value)
    seal = unsigned.pop("entry_sha256")
    outputs = value["outputs"]
    if (
        raw != _canonical(value) + b"\n"
        or value["schema"] != CACHE_ENTRY_SCHEMA
        or value["request"] != request.to_mapping()
        or value["request_identity_sha256"] != request.identity_sha256
        or seal != _sha256_bytes(_canonical(unsigned))
        or not isinstance(outputs, dict)
        or set(outputs) != set(REQUIRED_OUTPUT_ROLES)
    ):
        raise ExactAOTCacheError("AOT cache manifest identity differs")
    paths = {}
    hashes = {}
    payload_root = entry / "payloads"
    if payload_root.is_symlink() or not payload_root.is_dir():
        raise ExactAOTCacheError("AOT cache payload root differs")
    for role in REQUIRED_OUTPUT_ROLES:
        row = outputs[role]
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise ExactAOTCacheError(f"AOT cache output row differs: {role}")
        expected_name = f"{role}.bin"
        if row["path"] != f"payloads/{expected_name}":
            raise ExactAOTCacheError(f"AOT cache output path differs: {role}")
        path = _regular_file(payload_root / expected_name, f"cache output {role}")
        expected_sha = _require_sha(row["sha256"], f"cache output {role}")
        if (
            type(row["bytes"]) is not int
            or row["bytes"] < 0
            or path.stat().st_size != row["bytes"]
            or _sha256_file(path) != expected_sha
        ):
            raise ExactAOTCacheError(f"AOT cache output bytes differ: {role}")
        paths[role] = path
        hashes[role] = expected_sha
    if {path.name for path in payload_root.iterdir()} != {
        f"{role}.bin" for role in REQUIRED_OUTPUT_ROLES
    }:
        raise ExactAOTCacheError("AOT cache contains unexpected payloads")
    return paths, hashes


def _publish_entry(
    staging: Path,
    request: ExactAOTBuildRequest,
    produced: Mapping[str, os.PathLike[str] | str],
) -> None:
    if set(produced) != set(REQUIRED_OUTPUT_ROLES):
        raise ExactAOTCacheError("AOT producer output roles differ")
    payload_root = staging / "payloads"
    payload_root.mkdir()
    rows = {}
    for role in REQUIRED_OUTPUT_ROLES:
        source = _regular_file(Path(produced[role]), f"producer output {role}")
        payload = source.read_bytes()
        destination = payload_root / f"{role}.bin"
        _write_create(destination, payload)
        rows[role] = {
            "path": f"payloads/{role}.bin",
            "bytes": len(payload),
            "sha256": _sha256_bytes(payload),
        }
    _write_create(staging / "manifest.json", _manifest_payload(request, rows))


def resolve_exact_aot(
    request: ExactAOTBuildRequest,
    *,
    cache_root: os.PathLike[str] | str,
    producer: Callable[[Path], Mapping[str, os.PathLike[str] | str]],
    verifier: Callable[[Mapping[str, Path]], object],
) -> VerifiedAOTCacheEntry:
    """Return one byte-verified deployment, invoking ``producer`` only on miss."""

    if not isinstance(request, ExactAOTBuildRequest):
        raise TypeError("ExactAOTBuildRequest required")
    if not callable(producer) or not callable(verifier):
        raise TypeError("AOT producer and verifier must be callable")
    if fcntl is None:
        raise ExactAOTCacheError("exact AOT cache requires POSIX flock")
    root = _validate_cache_root(Path(cache_root))
    identity = request.identity_sha256
    entry = root / "entries" / identity
    lock_path = root / "locks" / f"{identity}.lock"
    try:
        lock_descriptor = os.open(
            lock_path,
            os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except OSError as error:
        raise ExactAOTCacheError("AOT cache lock cannot be opened") from error
    producer_invoked = False
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        if entry.exists() or entry.is_symlink():
            paths, hashes = _validate_entry(entry, request)
            cache_hit = True
        else:
            staging = Path(tempfile.mkdtemp(
                prefix=f"{identity}.", dir=root / "staging"
            ))
            try:
                produced = producer(staging / "producer")
                producer_invoked = True
                if not isinstance(produced, Mapping):
                    raise TypeError("AOT producer must return a mapping")
                publish = staging / "entry"
                publish.mkdir()
                _publish_entry(publish, request, produced)
                # Harden payload containment before publication. macOS rejects
                # moving a 0500 directory across parents, so harden the entry
                # root after rename and atomically roll it back on failure.
                (publish / "payloads").chmod(0o500)
                os.rename(publish, entry)
                try:
                    entry.chmod(0o500)
                except BaseException:
                    os.rename(entry, publish)
                    raise
            finally:
                shutil.rmtree(staging, ignore_errors=True)
            paths, hashes = _validate_entry(entry, request)
            cache_hit = False
        if hashes["trust_root"] != request.trust_root_file_sha256:
            raise ExactAOTCacheError("AOT cache trust root identity differs")
        verification = verifier(MappingProxyType(paths))
        if verification is None:
            raise ExactAOTCacheError("AOT verifier returned no capability")
        return VerifiedAOTCacheEntry(
            request_identity_sha256=identity,
            entry_path=entry,
            output_paths=MappingProxyType(paths),
            output_sha256=MappingProxyType(hashes),
            cache_hit=cache_hit,
            producer_invoked=producer_invoked,
            verification=verification,
        )
    finally:
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        finally:
            os.close(lock_descriptor)


__all__ = [
    "CACHE_ENTRY_SCHEMA",
    "REQUEST_SCHEMA",
    "REQUIRED_OUTPUT_ROLES",
    "ExactAOTBuildRequest",
    "ExactAOTCacheError",
    "VerifiedAOTCacheEntry",
    "resolve_exact_aot",
]
