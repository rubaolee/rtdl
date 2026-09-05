"""Content-addressed deployment artifacts for checked RTDL V4 programs.

``.rtdlexe`` is a deployment format, not a source or compiler cache.  The
artifact contains the exact checked protocol projection and composed PTX.  A
detached authority identifies an untrusted build candidate.  A separately
installed project trust root signs the deployment slot that is allowed to
consume that candidate.  Artifact/request data can therefore neither replace
the trust root nor supply a newly computed "expected hash".

The cache-hit import path intentionally uses only the Python standard library.
Compiler, Numba, NVRTC, source-frontend, and legacy OptiX runtime modules are
loaded only by :func:`build_rtdlexe`, which is the cache-miss/build operation.
Deployment is deliberately split into an offline authorization step and a
read-only runtime step::

    build_rtdlexe(...) -> freeze/sign outside the loader
    install_rtdlexe_deployment(...) -> load_rtdlexe(...) -> prepare(...) -> execute(...) -> close()

The current closed deployment families are the public custom-AABB bounded
relation and built-in-triangle checked U64 reduction protocols.
"""

from __future__ import annotations

import base64
import ctypes
from array import array
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import numbers
import operator
import os
from pathlib import Path
import re
import stat
import struct
import sys
import tempfile
import threading
import time
from itertools import chain
from types import MappingProxyType
from typing import Iterator, Mapping, Sequence
import weakref


_ARTIFACT_SCHEMA = "rtdl.v4.rtdlexe.v1"
_AUTHORITY_SCHEMA = "rtdl.v4.rtdlexe.detached_authority.v1"
_PROJECTION_SCHEMA = "rtdl.v4.rtdlexe.product_projection.v1"
_FAMILY_ARTIFACT_SCHEMA = "rtdl.v4.rtdlexe.v2"
_FAMILY_AUTHORITY_SCHEMA = "rtdl.v4.rtdlexe.detached_authority.v2"
_FAMILY_PROJECTION_SCHEMA = "rtdl.v4.rtdlexe.product_projection.v2"
_FAMILY_BINDING_SCHEMA = "rtdl.generic_family_deployment_binding.v1"
_FAMILY_DEPLOYMENT_FORMAT_ID = "rtdl.v4.rtdlexe.v2"
_STATUS_SCHEMA = "rtdl.v4.fixed_device_status.v2"
_NATIVE_DESCRIPTOR_SCHEMA = "rtdl.v4.rtdlexe.native_producer_descriptor.v1"
_AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V1\x00"
_FAMILY_AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V2\x00"
_TRUST_ROOT_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_root.v1"
_TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
_TRUST_PACKAGE_SCHEMA = "rtdl.v4.rtdlexe.deployment_trust_package.v1"
_TRUST_PACKAGE_DOMAIN = b"RTDL-V4-RTDLEXE-DEPLOYMENT-TRUST-PACKAGE-V1\x00"
_TRUST_HEAD_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_head.v1"
_TRUST_HEAD_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-HEAD-V1\x00"
_SHA256_DIGEST_INFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_BOUNDED = "custom_aabb_bounded_relation_v1"
_TRIANGLE = "builtin_triangle_reduction_v1"
_TRIANGLE_MODES = {"all_hit_count", "weighted_hit_count"}
_FAST_STATUS_CAPACITY_INVALID = 0xffff5102
_NATIVE_ALIAS_LOCK = threading.Lock()
_NATIVE_ALIAS_PATHS_SEEN: set[str] = set()
_NATIVE_IMAGE_CACHE_LOCK = threading.RLock()
_NATIVE_IMAGE_CACHE_PID = os.getpid()
_NATIVE_IMAGE_CACHE_FORK_POISONED = False
_NATIVE_IMAGE_CACHE_LOAD_POISONED = False
_NATIVE_IMAGE_CACHE_LOAD_FAILURE: str | None = None
_NATIVE_IMAGE_CACHE_NEXT_LEASE = 0
# Sticky process evidence: once Python has crossed either the CUDA-driver or
# native-DSO FFI boundary, a forked child must never attempt a second runtime
# admission.  The cache can still be empty while ``cuInit`` or ``dlopen`` is in
# flight, so cache publication alone is not a sufficient fork predicate.
_NATIVE_RUNTIME_TOUCHED = False
# The CUDA primary context is process state, just like the CUDA/OptiX native
# image cached below.  Provider capabilities borrow this process-lifetime
# readiness state; they do not retain/release the primary context independently.
# Besides matching the actual runtime ownership model, this removes an
# impossible-to-make-atomic Python window between a successful external
# retain/release side effect and publication of a Python flag.
_CUDA_PRIMARY_READY_LOCK = threading.RLock()
_CUDA_PRIMARY_READY_PID = os.getpid()
_CUDA_PRIMARY_READY_STATE = None


@dataclass
class _NativeImageCacheEntry:
    """One process-lifetime, content-addressed sealed DSO image.

    Explicit ``dlclose`` is deliberately not part of this state machine.
    CUDA/OptiX DSOs can own static process state whose teardown order is not
    safe at an arbitrary Python object boundary.  The cache retains exactly
    one dynamic-loader image (which can span several VMAs) and one sealed
    descriptor per content digest until process exit; prepared tokens and
    per-call leases still have bounded lifetimes.
    """

    library: object
    sha256: str
    source_path: Path
    image_descriptor: int
    image_seals: int
    loader_alias: str
    owner_pid: int
    active_lease_ids: set[int] = field(default_factory=set)
    acquisition_count: int = 0
    usable: bool = False
    load_failure: str | None = None


@dataclass(frozen=True)
class _ProviderReadyNativeBinding:
    """Exact immutable cache facts captured by one provider bind."""

    entry: _NativeImageCacheEntry
    library_object: object
    cache_entry_identity: str
    digest: str
    owner_pid: int
    source_path: Path
    provenance_path: Path
    image_descriptor: int
    descriptor_identity: tuple[int, int, int, int]
    image_seals: int
    loader_handle: int
    loader_alias: str
    binding_lease_id: int


class _NativeLibraryLease:
    """Per-acquisition capability for one process-cached native image."""

    def __init__(
        self, *, entry: _NativeImageCacheEntry, lease_id: int, source_path: Path,
    ) -> None:
        self._rtdl_native_cache_entry = entry
        self._rtdl_native_cache_key = entry.sha256
        self._rtdl_native_cache_entry_identity = (
            f"{entry.owner_pid}:{entry.sha256}")
        self._rtdl_native_cache_owner_pid = entry.owner_pid
        self._rtdl_native_cache_lease_id = lease_id
        self._rtdl_native_cache_source_path = str(source_path)
        self._rtdl_library_path = str(source_path)
        self._rtdl_loaded_library_path = str(source_path)
        self._rtdl_loaded_library_sha256 = entry.sha256
        self._rtdl_native_loader_alias = entry.loader_alias
        self._rtdl_native_image_release_started = False
        self._rtdl_native_image_released = False
        self._rtdl_native_image_release_error = None
        self._rtdl_native_image_release_phase = "ACTIVE"

    @property
    def _handle(self) -> int:
        if self._rtdl_native_image_released:
            return 0
        return int(getattr(self._rtdl_native_cache_entry.library, "_handle", 0))

    @property
    def _rtdl_native_image_fd(self) -> int:
        if self._rtdl_native_image_released:
            return -1
        return self._rtdl_native_cache_entry.image_descriptor

    @property
    def _rtdl_native_image_seals(self) -> int:
        if self._rtdl_native_image_released:
            return 0
        return self._rtdl_native_cache_entry.image_seals

    @property
    def _rtdl_native_cache_active_lease_count(self) -> int:
        with _NATIVE_IMAGE_CACHE_LOCK:
            return len(self._rtdl_native_cache_entry.active_lease_ids)

    @property
    def _rtdl_native_cache_acquisition_count(self) -> int:
        with _NATIVE_IMAGE_CACHE_LOCK:
            return self._rtdl_native_cache_entry.acquisition_count

    def __getattr__(self, name: str) -> object:
        if self._rtdl_native_image_released:
            _fail("RX037_USE_AFTER_CLOSE", "native.lease", "released")
        return getattr(self._rtdl_native_cache_entry.library, name)


class _NativeImageLeaseHandoff:
    """Caller-owned publication cell spanning a Python CALL/STORE boundary.

    A native lease can be returned by a callee and then stranded if an
    asynchronous exception lands before the caller's STORE_FAST.  The callee
    publishes the exact lease into this pre-existing cell before returning, so
    the caller's exception handler can always find and close it.
    """

    __slots__ = ("lease",)

    def __init__(self) -> None:
        self.lease: _NativeLibraryLease | None = None

    def publish(self, lease: _NativeLibraryLease) -> None:
        if self.lease is not None and self.lease is not lease:
            _fail(
                "RX048_NATIVE_CACHE_QUARANTINED", "native.lease_handoff",
                "handoff cell already contains another lease")
        self.lease = lease


class _PreparedOwnerHandoff:
    """Caller-owned cleanup cell published before native owner construction."""

    __slots__ = ("owner",)

    def __init__(self) -> None:
        self.owner: object | None = None

    def publish(self, owner: object) -> None:
        if self.owner is not None and self.owner is not owner:
            _fail(
                "RX046_NATIVE_RELEASE_INCOMPLETE", "prepared.owner_handoff",
                "handoff cell already contains another owner")
        self.owner = owner


_NATIVE_IMAGE_CACHE: dict[str, _NativeImageCacheEntry] = {}


def _native_image_cache_after_fork_child() -> None:
    """Replace inherited locks and poison a child that touched native state."""

    global _NATIVE_ALIAS_LOCK, _NATIVE_IMAGE_CACHE_LOCK
    global _NATIVE_IMAGE_CACHE_PID, _NATIVE_IMAGE_CACHE_FORK_POISONED
    global _CUDA_PRIMARY_READY_LOCK, _CUDA_PRIMARY_READY_PID
    global _CUDA_PRIMARY_READY_STATE
    inherited_native_runtime = _NATIVE_RUNTIME_TOUCHED or bool(
        _NATIVE_IMAGE_CACHE)
    _NATIVE_ALIAS_LOCK = threading.Lock()
    _NATIVE_IMAGE_CACHE_LOCK = threading.RLock()
    _CUDA_PRIMARY_READY_LOCK = threading.RLock()
    _CUDA_PRIMARY_READY_PID = os.getpid()
    # An inherited CUcontext handle belongs to the parent's CUDA runtime
    # instance.  Never publish it as usable child state.
    _CUDA_PRIMARY_READY_STATE = None
    _NATIVE_IMAGE_CACHE_PID = os.getpid()
    _NATIVE_IMAGE_CACHE_FORK_POISONED = inherited_native_runtime


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_native_image_cache_after_fork_child)


class RTDLExecutableError(RuntimeError):
    """Stable fail-closed error for the frozen deployment boundary."""

    def __init__(self, code: str, path: str, detail: str) -> None:
        self.code = code
        self.path = path
        self.detail = detail
        super().__init__(f"{code}@{path}: {detail}")


def _fail(code: str, path: str, detail: object) -> None:
    raise RTDLExecutableError(code, path, str(detail))


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        _fail("RX001_CANONICAL_VALUE_INVALID", "document", error)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _deep_freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _absolute_unresolved_path(value: str | os.PathLike[str]) -> Path:
    """Return an absolute spelling without following the final component.

    Security-sensitive inputs must reach :func:`os.lstat` before any
    ``Path.resolve`` call.  Resolving first turns a caller-supplied symlink into
    its regular-file target and makes the final-component symlink check inert.
    """

    return Path(os.path.abspath(os.fspath(Path(value).expanduser())))


def _require_sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail("RX002_SHA256_REQUIRED", path, repr(value))
    return value


def _require_string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("RX003_STRING_REQUIRED", path, repr(value))
    return value


def _require_exact_bool(value: object, path: str, *, code: str) -> bool:
    if type(value) is not bool:
        _fail(code, path, repr(value))
    return value


def _require_uint(value: object, path: str, *, bits: int, code: str) -> int:
    if isinstance(value, bool):
        _fail(code, path, repr(value))
    try:
        normalized = operator.index(value)
    except (TypeError, ValueError, OverflowError) as error:
        _fail(code, path, error)
    if not 0 <= normalized < (1 << bits):
        _fail(code, path, repr(value))
    return normalized


def _require_f32(value: object, path: str, *, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        _fail(code, path, repr(value))
    try:
        normalized = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    except (OverflowError, struct.error, TypeError, ValueError) as error:
        _fail(code, path, error)
    if not math.isfinite(normalized):
        _fail(code, path, repr(value))
    return normalized


def _require_packed_le_bytes(
        value: object, path: str, *, expected_size: int, code: str) -> bytes:
    """Freeze one contiguous little-endian typed-buffer projection.

    The element interpretation is carried by the public field name and its
    exact byte count.  Scalar semantic checks stay at the native boundary,
    which already validates every vertex/index/ray before any OptiX launch.
    This keeps the buffer front door independent of NumPy while avoiding a
    second Python object graph and per-element conversion pass.
    """

    if sys.byteorder != "little":
        _fail(code, path, "packed little-endian input requires a little-endian host")
    try:
        view = memoryview(value)
    except (TypeError, ValueError) as error:
        _fail(code, path, error)
    if not view.c_contiguous:
        _fail(code, path, "C-contiguous buffer required")
    try:
        raw = view.cast("B").tobytes()
    except (TypeError, ValueError) as error:
        _fail(code, path, error)
    if len(raw) != expected_size:
        _fail(code, path, {
            "expected_size": expected_size,
            "actual_size": len(raw),
        })
    return raw


def _require_exact_keys(
    value: object, expected: set[str], path: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        observed = sorted(value) if isinstance(value, Mapping) else type(value).__name__
        _fail("RX004_SCHEMA_FIELDS_INVALID", path, observed)
    return value


def _open_regular_readonly(path: Path, *, code: str) -> tuple[int, os.stat_result]:
    """Open exactly one regular-file inode without following a path swap.

    ``Path.is_file()`` followed by ``Path.read_bytes()`` is a classic
    check/use race.  Compare the opened descriptor with the lstat result as
    well as requesting ``O_NOFOLLOW`` where the platform provides it.  The
    returned descriptor, not the path, is the authority for all later reads.
    """

    try:
        before = os.lstat(path)
    except OSError as error:
        _fail(code, str(path), error)
    if not stat.S_ISREG(before.st_mode):
        _fail(code, str(path), "regular non-symlink file required")
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        _fail(code, str(path), error)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) \
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            _fail(code, str(path), "path changed while opening regular file")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, opened


def _read_descriptor_bytes(
    descriptor: int, *, code: str, path: Path,
) -> tuple[bytes, os.stat_result]:
    try:
        before = os.fstat(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    except OSError as error:
        _fail(code, str(path), error)
    stable_fields = ("st_dev", "st_ino", "st_mode", "st_size",
                     "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field)
           for field in stable_fields):
        _fail(code, str(path), "regular file changed while reading")
    raw = b"".join(chunks)
    if len(raw) != after.st_size:
        _fail(code, str(path), "regular file size changed while reading")
    return raw, after


def _read_regular_bytes_once(path: Path, *, code: str) -> bytes:
    descriptor, _ = _open_regular_readonly(path, code=code)
    try:
        raw, _ = _read_descriptor_bytes(descriptor, code=code, path=path)
        return raw
    finally:
        os.close(descriptor)


def _parse_canonical_json(
    raw: bytes, path: Path, *, code: str,
) -> Mapping[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        _fail(code, str(path), error)
    if not isinstance(value, Mapping) or raw != _canonical(value) + b"\n":
        _fail(code, str(path), "bytes are not exact canonical JSON plus terminal LF")
    return value


def _read_canonical_json_with_raw(
    path: Path, *, code: str,
) -> tuple[Mapping[str, object], bytes]:
    raw = _read_regular_bytes_once(path, code=code)
    return _parse_canonical_json(raw, path, code=code), raw


def _read_canonical_json(path: Path, *, code: str) -> Mapping[str, object]:
    value, _ = _read_canonical_json_with_raw(path, code=code)
    return value


def _write_create_or_exact(path: Path, payload: bytes, *, code: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        _fail(code, str(path), "output may not be a symlink")
    if path.exists():
        if _read_regular_bytes_once(path, code=code) != payload:
            _fail(code, str(path), "existing path has different exact bytes")
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _rsa_pkcs1_v15_sha256_verify(
    signature: bytes, message: bytes, *, modulus: int, exponent: int,
) -> bool:
    """Verify one installed RSA root without a crypto/compiler dependency."""

    width = (modulus.bit_length() + 7) // 8
    if len(signature) != width:
        return False
    encoded = pow(
        int.from_bytes(signature, "big"),
        exponent,
        modulus,
    ).to_bytes(width, "big")
    digest_info = _SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(message).digest()
    padding_length = width - len(digest_info) - 3
    if padding_length < 8:
        return False
    expected = b"\x00\x01" + b"\xff" * padding_length + b"\x00" + digest_info
    return hmac.compare_digest(encoded, expected)


def _read_trust_root(
    path: Path, *, _raw: bytes | None = None,
) -> Mapping[str, object]:
    root = (_parse_canonical_json(
        _raw, path, code="RX045_TRUST_ROOT_INVALID")
        if _raw is not None else
        _read_canonical_json(path, code="RX045_TRUST_ROOT_INVALID"))
    root = _require_exact_keys(root, {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "trust_root_sha256",
    }, "trust_root")
    if root["schema"] != _TRUST_ROOT_SCHEMA:
        _fail("RX046_TRUST_ROOT_SCHEMA_INVALID", "trust_root.schema", root["schema"])
    body = dict(root); seal = body.pop("trust_root_sha256")
    if _require_sha(seal, "trust_root.trust_root_sha256") != \
            _sha_bytes(_TRUST_ROOT_DOMAIN + _canonical(body)):
        _fail("RX047_TRUST_ROOT_IDENTITY_INVALID", "trust_root.trust_root_sha256", seal)
    _require_string(root["key_id"], "trust_root.key_id")
    exponent = root["rsa_exponent"]
    if not isinstance(exponent, int) or isinstance(exponent, bool) or exponent < 3 \
            or exponent % 2 == 0:
        _fail("RX046_TRUST_ROOT_SCHEMA_INVALID", "trust_root.rsa_exponent", exponent)
    try:
        modulus_bytes = base64.b64decode(root["rsa_modulus_base64"], validate=True)
    except (TypeError, ValueError) as error:
        _fail("RX046_TRUST_ROOT_SCHEMA_INVALID", "trust_root.rsa_modulus_base64", error)
    modulus = int.from_bytes(modulus_bytes, "big")
    if len(modulus_bytes) < 256 or modulus.bit_length() < 2040 or modulus % 2 == 0:
        _fail("RX046_TRUST_ROOT_SCHEMA_INVALID", "trust_root.rsa_modulus_base64", "RSA >= 2048 bits required")
    return {**root, "_rsa_modulus": modulus}


def _verify_trust_package(
    path: Path, *, root: Mapping[str, object], _raw: bytes | None = None,
) -> tuple[Mapping[str, object], tuple[Mapping[str, object], ...]]:
    package = (_parse_canonical_json(
        _raw, path, code="RX045_TRUST_PACKAGE_INVALID")
        if _raw is not None else
        _read_canonical_json(path, code="RX045_TRUST_PACKAGE_INVALID"))
    package = _require_exact_keys(package, {
        "schema", "key_id", "sequence", "previous_package_sha256",
        "authorities", "signature_algorithm", "signature_base64",
    }, "trust_package")
    if package["schema"] != _TRUST_PACKAGE_SCHEMA \
            or package["key_id"] != root["key_id"] \
            or package["signature_algorithm"] != "rsa-pkcs1-v1_5-sha256":
        _fail("RX046_TRUST_PACKAGE_SCHEMA_INVALID", "trust_package", package["schema"])
    if not isinstance(package["sequence"], int) or isinstance(package["sequence"], bool) \
            or package["sequence"] <= 0:
        _fail("RX046_TRUST_PACKAGE_SCHEMA_INVALID", "trust_package.sequence", package["sequence"])
    previous = package["previous_package_sha256"]
    if previous is not None:
        _require_sha(previous, "trust_package.previous_package_sha256")
    entries = package["authorities"]
    if not isinstance(entries, list) or not entries:
        _fail("RX046_TRUST_PACKAGE_SCHEMA_INVALID", "trust_package.authorities", entries)
    normalized = []
    for index, entry in enumerate(entries):
        entry = _require_exact_keys(entry, {
            "deployment_id", "family", "task_semantics_sha256",
            "authority_sha256", "artifact_sha256", "executable_identity_sha256",
            "target_sha256", "native_library_sha256", "compute_capability",
        }, f"trust_package.authorities[{index}]")
        row = {
            "deployment_id": _require_string(
                entry["deployment_id"], f"trust_package.authorities[{index}].deployment_id"),
            "family": _require_string(
                entry["family"], f"trust_package.authorities[{index}].family"),
            "compute_capability": entry["compute_capability"],
        }
        for key in (
            "task_semantics_sha256", "authority_sha256", "artifact_sha256",
            "executable_identity_sha256", "target_sha256", "native_library_sha256",
        ):
            row[key] = _require_sha(entry[key], f"trust_package.authorities[{index}].{key}")
        compute = row["compute_capability"]
        if not isinstance(compute, list) or len(compute) != 2 \
                or any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in compute):
            _fail("RX046_TRUST_PACKAGE_SCHEMA_INVALID",
                  f"trust_package.authorities[{index}].compute_capability", compute)
        normalized.append(row)
    if normalized != sorted(normalized, key=lambda row: row["deployment_id"]) \
            or len({row["deployment_id"] for row in normalized}) != len(normalized) \
            or len({row["authority_sha256"] for row in normalized}) != len(normalized):
        _fail("RX046_TRUST_PACKAGE_SCHEMA_INVALID", "trust_package.authorities", "must be unique/sorted")
    try:
        signature = base64.b64decode(package["signature_base64"], validate=True)
    except (TypeError, ValueError) as error:
        _fail("RX047_TRUST_PACKAGE_SIGNATURE_INVALID", "trust_package.signature", error)
    signed_body = dict(package); signed_body.pop("signature_base64")
    if not _rsa_pkcs1_v15_sha256_verify(
            signature, _TRUST_PACKAGE_DOMAIN + _canonical(signed_body),
            modulus=int(root["_rsa_modulus"]), exponent=int(root["rsa_exponent"])):
        _fail("RX047_TRUST_PACKAGE_SIGNATURE_INVALID", "trust_package.signature", "installed-root signature rejected")
    return package, tuple(normalized)


def _verify_trust_head(
    path: Path, *, root: Mapping[str, object], _raw: bytes | None = None,
) -> Mapping[str, object]:
    head = (_parse_canonical_json(
        _raw, path, code="RX053_TRUST_HEAD_INVALID")
        if _raw is not None else
        _read_canonical_json(path, code="RX053_TRUST_HEAD_INVALID"))
    head = _require_exact_keys(head, {
        "schema", "key_id", "current_package_sha256", "current_sequence",
        "signature_algorithm", "signature_base64",
    }, "trust_head")
    if head["schema"] != _TRUST_HEAD_SCHEMA or head["key_id"] != root["key_id"] \
            or head["signature_algorithm"] != "rsa-pkcs1-v1_5-sha256" \
            or not isinstance(head["current_sequence"], int) \
            or isinstance(head["current_sequence"], bool) or head["current_sequence"] <= 0:
        _fail("RX053_TRUST_HEAD_INVALID", "trust_head", "schema/key/sequence invalid")
    _require_sha(head["current_package_sha256"], "trust_head.current_package_sha256")
    try:
        signature = base64.b64decode(head["signature_base64"], validate=True)
    except (TypeError, ValueError) as error:
        _fail("RX053_TRUST_HEAD_INVALID", "trust_head.signature", error)
    body = dict(head); body.pop("signature_base64")
    if not _rsa_pkcs1_v15_sha256_verify(
            signature, _TRUST_HEAD_DOMAIN + _canonical(body),
            modulus=int(root["_rsa_modulus"]), exponent=int(root["rsa_exponent"])):
        _fail("RX053_TRUST_HEAD_INVALID", "trust_head.signature", "installed-root signature rejected")
    return head


def _coerce_mapping(value: object, path: str) -> dict[str, object]:
    if isinstance(value, Mapping):
        return dict(value)
    method = getattr(value, "to_mapping", None) or getattr(value, "to_dict", None)
    if not callable(method):
        _fail("RX005_BUILD_INPUT_INVALID", path, type(value).__name__)
    result = method()
    if not isinstance(result, Mapping):
        _fail("RX005_BUILD_INPUT_INVALID", path, "mapping projection required")
    return dict(result)


@dataclass(frozen=True)
class BuiltRTDLExecutable:
    artifact_path: Path
    artifact_sha256: str
    authority_path: Path
    authority_sha256: str
    executable_identity_sha256: str
    family_executable_identity_sha256: str | None = None


@dataclass(frozen=True)
class FrozenRTDLTrustPackage:
    path: Path
    sha256: str
    sequence: int
    authority_count: int


_DEPLOYMENT_CAPABILITY_TOKEN = object()


class InstalledRTDLDeployment:
    """Verified read-only deployment slot selected during trusted install.

    The loader accepts this capability instead of a caller-provided public key,
    trust-package path, expected hash, family, or task intent.  Python code that
    already controls the process remains inside the trusted computing base;
    the boundary protects against artifact/request-controlled substitution.
    """

    __slots__ = ("trust_root_path", "trust_root_sha256", "trust_head_path",
                 "trust_head_sha256", "trust_package_path", "trust_package_sha256",
                 "deployment_id", "entry", "_token")

    def __setattr__(self, name: str, value: object) -> None:
        if hasattr(self, name):
            _fail("RX048_DEPLOYMENT_CAPABILITY_INVALID", f"deployment.{name}", "immutable")
        object.__setattr__(self, name, value)

    def __init__(self, *, _token: object, trust_root_path: Path,
                 trust_root_sha256: str, trust_package_path: Path,
                 trust_package_sha256: str, trust_head_path: Path,
                 trust_head_sha256: str, deployment_id: str,
                 entry: Mapping[str, object]) -> None:
        if _token is not _DEPLOYMENT_CAPABILITY_TOKEN:
            _fail("RX048_DEPLOYMENT_CAPABILITY_INVALID", "deployment", "use install_rtdlexe_deployment")
        self._token = _token
        self.trust_root_path = trust_root_path
        self.trust_root_sha256 = trust_root_sha256
        self.trust_head_path = trust_head_path
        self.trust_head_sha256 = trust_head_sha256
        self.trust_package_path = trust_package_path
        self.trust_package_sha256 = trust_package_sha256
        self.deployment_id = deployment_id
        frozen_entry = dict(entry)
        frozen_entry["compute_capability"] = tuple(frozen_entry["compute_capability"])
        self.entry = MappingProxyType(frozen_entry)

    def begin_provider_initialization(
        self, native_library_path: str | os.PathLike[str],
    ) -> "InitializingRTDLProvider":
        """Start app-free provider admission while an artifact is verified.

        The native identity and device target come only from this installed,
        signed deployment slot.  The returned capability cannot prepare or
        execute anything until :meth:`InitializingRTDLProvider.bind` receives
        the exact result of :func:`load_rtdlexe` for the same slot.
        """

        return InitializingRTDLProvider(
            deployment=self, native_library_path=native_library_path,
            _token=_INITIALIZING_PROVIDER_CAPABILITY_TOKEN)


def install_rtdlexe_deployment(
    *, trust_root_path: str | os.PathLike[str],
    trust_head_path: str | os.PathLike[str],
    trust_package_path: str | os.PathLike[str], deployment_id: str,
) -> InstalledRTDLDeployment:
    """Install one signed deployment slot before processing artifact requests.

    Choosing the trust-root path and deployment id is an administrator action,
    not an artifact/request field.  The returned capability is immutable and
    binds exactly one slot.  Updating it requires a separate install call.
    """

    root_path = _absolute_unresolved_path(trust_root_path)
    head_path = _absolute_unresolved_path(trust_head_path)
    package_path = _absolute_unresolved_path(trust_package_path)
    slot = _require_string(deployment_id, "deployment_id")
    root_raw = _read_regular_bytes_once(
        root_path, code="RX045_TRUST_ROOT_INVALID")
    head_raw = _read_regular_bytes_once(
        head_path, code="RX053_TRUST_HEAD_INVALID")
    package_raw = _read_regular_bytes_once(
        package_path, code="RX045_TRUST_PACKAGE_INVALID")
    root = _read_trust_root(root_path, _raw=root_raw)
    head = _verify_trust_head(head_path, root=root, _raw=head_raw)
    package, entries = _verify_trust_package(
        package_path, root=root, _raw=package_raw)
    if head["current_package_sha256"] != _sha_bytes(package_raw) \
            or head["current_sequence"] != package["sequence"]:
        _fail("RX054_TRUST_PACKAGE_ROLLBACK", "trust_package", {
            "installed_head_sequence": head["current_sequence"],
            "observed_sequence": package["sequence"],
        })
    matches = [entry for entry in entries if entry["deployment_id"] == slot]
    if len(matches) != 1:
        _fail("RX049_DEPLOYMENT_SLOT_NOT_FROZEN", "deployment_id", slot)
    return InstalledRTDLDeployment(
        _token=_DEPLOYMENT_CAPABILITY_TOKEN,
        trust_root_path=root_path,
        trust_root_sha256=_sha_bytes(root_raw),
        trust_head_path=head_path,
        trust_head_sha256=_sha_bytes(head_raw),
        trust_package_path=package_path,
        trust_package_sha256=_sha_bytes(package_raw),
        deployment_id=slot,
        entry=matches[0],
    )


@dataclass(frozen=True)
class RTDLExecutableBuildRoots:
    """Build roots absent from the historical public ``V4Toolchain`` object.

    The compiler options, role sources/PTX, ABI, wrapper and target are read
    from the actual materialized executable.  These remaining environment/link
    values are explicit build inputs and are bound by the detached authority;
    they are not claimed to be independently discovered runtime facts.
    """

    llvmlite_version: str
    cuda_toolkit_version: str
    link_options: tuple[str, ...]
    wrapper_numeric_policy: str = "strict"
    leaf_numeric_policy: str = "strict"
    composer_schema: str = "rtdl.v4.composed_callback_ptx.v1"

    def __post_init__(self) -> None:
        for name in (
            "llvmlite_version", "cuda_toolkit_version", "wrapper_numeric_policy",
            "leaf_numeric_policy", "composer_schema",
        ):
            _require_string(getattr(self, name), f"build_roots.{name}")
        options = tuple(_require_string(item, "build_roots.link_options")
                        for item in self.link_options)
        if not options or len(options) != len(set(options)):
            _fail("RX005_BUILD_INPUT_INVALID", "build_roots.link_options", options)
        object.__setattr__(self, "link_options", options)


@dataclass(frozen=True)
class BoundedRelationStaticInput:
    indexed_boxes: tuple[tuple[object, ...], ...]

    def __post_init__(self) -> None:
        rows = tuple(tuple(row) for row in self.indexed_boxes)
        if not rows:
            _fail("RX006_INPUT_INVALID", "static.indexed_boxes", "nonempty required")
        normalized_rows = []
        for index, row in enumerate(rows):
            if len(row) != 5:
                _fail("RX006_INPUT_INVALID", f"static.indexed_boxes[{index}]", "arity five")
            bounds = tuple(_require_f32(
                item, f"static.indexed_boxes[{index}][{axis}]",
                code="RX006_INPUT_INVALID") for axis, item in enumerate(row[:4]))
            item_id = _require_uint(
                row[4], f"static.indexed_boxes[{index}][4]", bits=32,
                code="RX006_INPUT_INVALID")
            if bounds[0] > bounds[2] or bounds[1] > bounds[3]:
                _fail("RX006_INPUT_INVALID", f"static.indexed_boxes[{index}]", row)
            normalized_rows.append((*bounds, item_id))
        object.__setattr__(self, "indexed_boxes", tuple(normalized_rows))


@dataclass(frozen=True)
class BoundedRelationBatch:
    source_boxes: tuple[tuple[object, ...], ...]
    expected_rows: tuple[tuple[int, int], ...] | None = None
    _packed_bounds_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_ids_u32: bytes = field(init=False, repr=False, compare=False)
    _device_input_sha256: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        rows = tuple(tuple(row) for row in self.source_boxes)
        if not rows:
            _fail("RX006_INPUT_INVALID", "batch.source_boxes", "nonempty required")
        bounds = bytearray(); ids = bytearray(); normalized_rows = []
        for index, row in enumerate(rows):
            if len(row) != 5:
                _fail("RX006_INPUT_INVALID", f"batch.source_boxes[{index}]", "arity five")
            try:
                normalized = tuple(_require_f32(
                    item, f"batch.source_boxes[{index}][{axis}]",
                    code="RX006_INPUT_INVALID") for axis, item in enumerate(row[:4]))
                packed = struct.pack("<4f", *normalized)
                normalized = struct.unpack("<4f", packed)
                item_id = _require_uint(
                    row[4], f"batch.source_boxes[{index}][4]", bits=32,
                    code="RX006_INPUT_INVALID")
            except (TypeError, ValueError, OverflowError, struct.error) as exc:
                _fail("RX006_INPUT_INVALID", f"batch.source_boxes[{index}]", exc)
            if not all(math.isfinite(item) for item in normalized) \
                    or normalized[0] > normalized[2] or normalized[1] > normalized[3] \
                    or not 0 <= item_id < 1 << 32:
                _fail("RX006_INPUT_INVALID", f"batch.source_boxes[{index}]", row)
            bounds.extend(packed); ids.extend(struct.pack("<I", item_id))
            normalized_rows.append((*normalized, item_id))
        object.__setattr__(self, "source_boxes", tuple(normalized_rows))
        object.__setattr__(self, "_packed_bounds_f32", bytes(bounds))
        object.__setattr__(self, "_packed_ids_u32", bytes(ids))
        object.__setattr__(self, "_device_input_sha256", _sha_bytes(
            b"RTDL-V4-BOUNDED-BATCH-V1\x00" + bytes(bounds) + bytes(ids)))
        if self.expected_rows is not None:
            expected = []
            for index, raw_row in enumerate(self.expected_rows):
                try:
                    row = tuple(raw_row)
                except TypeError as error:
                    _fail("RX006_INPUT_INVALID", f"batch.expected_rows[{index}]", error)
                if len(row) != 2:
                    _fail("RX006_INPUT_INVALID", f"batch.expected_rows[{index}]", "arity two")
                expected.append((
                    _require_uint(row[0], f"batch.expected_rows[{index}][0]",
                                  bits=32, code="RX006_INPUT_INVALID"),
                    _require_uint(row[1], f"batch.expected_rows[{index}][1]",
                                  bits=32, code="RX006_INPUT_INVALID"),
                ))
            object.__setattr__(self, "expected_rows", tuple(expected))


@dataclass(frozen=True)
class BoundedRelationBufferStaticInput:
    """Immutable packed-buffer front door for indexed 2D AABBs."""

    indexed_bounds_f32le: object = field(repr=False, compare=False)
    indexed_ids_u32le: object = field(repr=False, compare=False)
    indexed_count: int
    _packed_bounds_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_ids_u32: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        count = _require_uint(
            self.indexed_count, "static.indexed_count", bits=32,
            code="RX006_INPUT_INVALID")
        if not count:
            _fail("RX006_INPUT_INVALID", "static.indexed_count",
                  "positive count required")
        bounds = _require_packed_le_bytes(
            self.indexed_bounds_f32le, "static.indexed_bounds_f32le",
            expected_size=16 * count, code="RX006_INPUT_INVALID")
        ids = _require_packed_le_bytes(
            self.indexed_ids_u32le, "static.indexed_ids_u32le",
            expected_size=4 * count, code="RX006_INPUT_INVALID")
        object.__setattr__(self, "indexed_bounds_f32le", bounds)
        object.__setattr__(self, "indexed_ids_u32le", ids)
        object.__setattr__(self, "indexed_count", count)
        object.__setattr__(self, "_packed_bounds_f32", bounds)
        object.__setattr__(self, "_packed_ids_u32", ids)


@dataclass(frozen=True)
class BoundedRelationBufferBatch:
    """Immutable packed-buffer front door for source 2D AABBs."""

    source_bounds_f32le: object = field(repr=False, compare=False)
    source_ids_u32le: object = field(repr=False, compare=False)
    source_count: int
    expected_rows: tuple[tuple[int, int], ...] | None = None
    _packed_bounds_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_ids_u32: bytes = field(init=False, repr=False, compare=False)
    _device_input_sha256: str = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        count = _require_uint(
            self.source_count, "batch.source_count", bits=32,
            code="RX006_INPUT_INVALID")
        if not count:
            _fail("RX006_INPUT_INVALID", "batch.source_count",
                  "positive count required")
        bounds = _require_packed_le_bytes(
            self.source_bounds_f32le, "batch.source_bounds_f32le",
            expected_size=16 * count, code="RX006_INPUT_INVALID")
        ids = _require_packed_le_bytes(
            self.source_ids_u32le, "batch.source_ids_u32le",
            expected_size=4 * count, code="RX006_INPUT_INVALID")
        expected = self.expected_rows
        if expected is not None:
            expected = tuple((
                _require_uint(row[0], f"batch.expected_rows[{index}][0]",
                              bits=32, code="RX006_INPUT_INVALID"),
                _require_uint(row[1], f"batch.expected_rows[{index}][1]",
                              bits=32, code="RX006_INPUT_INVALID"),
            ) for index, row in enumerate(expected) if len(row) == 2)
            if len(expected) != len(self.expected_rows):
                _fail("RX006_INPUT_INVALID", "batch.expected_rows", "arity two")
        object.__setattr__(self, "source_bounds_f32le", bounds)
        object.__setattr__(self, "source_ids_u32le", ids)
        object.__setattr__(self, "source_count", count)
        object.__setattr__(self, "expected_rows", expected)
        object.__setattr__(self, "_packed_bounds_f32", bounds)
        object.__setattr__(self, "_packed_ids_u32", ids)
        object.__setattr__(self, "_device_input_sha256", _sha_bytes(
            b"RTDL-V4-BOUNDED-BATCH-V1\x00" + bounds + ids))


@dataclass(frozen=True)
class TriangleReductionStaticInput:
    vertices: tuple[tuple[object, object, object], ...]
    triangles: tuple[tuple[int, int, int], ...]
    event_capacity: int = 1
    _packed_vertices_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_triangles_u32: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        vertices = tuple(tuple(row) for row in self.vertices)
        if not vertices or any(len(row) != 3 for row in vertices):
            _fail("RX006_INPUT_INVALID", "static.vertices", "nonempty arity three")
        builtin_vertices = all(
            type(item) in (int, float) for row in vertices for item in row)
        vertex_array = None
        if builtin_vertices:
            try:
                candidate = array("f", chain.from_iterable(vertices))
                if candidate.itemsize == 4:
                    vertex_array = candidate
            except (TypeError, ValueError, OverflowError):
                vertex_array = None
        if vertex_array is None or not all(
                math.isfinite(item) for item in vertex_array):
            vertex_flat: list[float] = []
            for row_index, row in enumerate(vertices):
                for axis, item in enumerate(row):
                    vertex_flat.append(_require_f32(
                        item, f"static.vertices[{row_index}][{axis}]",
                        code="RX006_INPUT_INVALID"))
            vertex_array = array("f", vertex_flat)
        packed_vertex_array = vertex_array
        if sys.byteorder != "little":
            packed_vertex_array = array("f", vertex_array)
            packed_vertex_array.byteswap()
        packed_vertices = packed_vertex_array.tobytes()
        vertex_iterator = iter(vertex_array)
        normalized_vertices = tuple(zip(
            vertex_iterator, vertex_iterator, vertex_iterator))

        triangle_rows = []
        for row_index, raw_row in enumerate(self.triangles):
            try:
                row = tuple(raw_row)
            except TypeError as error:
                _fail("RX006_INPUT_INVALID", f"static.triangles[{row_index}]", error)
            if len(row) != 3:
                _fail("RX006_INPUT_INVALID", f"static.triangles[{row_index}]", "arity three")
            triangle_rows.append(row)
        builtin_triangles = all(
            type(item) is int for row in triangle_rows for item in row)
        triangle_array = None
        if builtin_triangles:
            try:
                candidate = array("I", chain.from_iterable(triangle_rows))
                if candidate.itemsize == 4:
                    triangle_array = candidate
            except (TypeError, ValueError, OverflowError):
                triangle_array = None
        triangles = []
        triangle_flat: list[int] = []
        if triangle_array is not None \
                and (not triangle_array or max(triangle_array) < len(normalized_vertices)):
            triangles = triangle_rows
            triangle_flat = list(triangle_array)
        else:
            for row_index, row in enumerate(triangle_rows):
                normalized_items = []
                for axis, item in enumerate(row):
                    if type(item) is int and 0 <= item <= 0xffffffff:
                        normalized_items.append(item)
                    else:
                        normalized_items.append(_require_uint(
                            item, f"static.triangles[{row_index}][{axis}]", bits=32,
                            code="RX006_INPUT_INVALID"))
                normalized = tuple(normalized_items)
                if any(item >= len(normalized_vertices) for item in normalized):
                    _fail("RX006_INPUT_INVALID", f"static.triangles[{row_index}]", row)
                triangles.append(normalized)
                triangle_flat.extend(normalized)
        if not triangles:
            _fail("RX006_INPUT_INVALID", "static.triangles", "nonempty required")
        capacity = _require_uint(
            self.event_capacity, "static.event_capacity", bits=32,
            code="RX006_INPUT_INVALID")
        if capacity == 0:
            _fail("RX006_INPUT_INVALID", "static.event_capacity", repr(capacity))
        object.__setattr__(self, "vertices", normalized_vertices)
        object.__setattr__(self, "triangles", tuple(triangles))
        object.__setattr__(self, "event_capacity", capacity)
        object.__setattr__(self, "_packed_vertices_f32", packed_vertices)
        if triangle_array is None or triangles is not triangle_rows:
            triangle_array = array("I", triangle_flat)
        packed_triangle_array = triangle_array
        if sys.byteorder != "little":
            packed_triangle_array = array("I", triangle_array)
            packed_triangle_array.byteswap()
        object.__setattr__(self, "_packed_triangles_u32",
                           packed_triangle_array.tobytes())


@dataclass(frozen=True)
class TriangleReductionBatch:
    queries: tuple[tuple[object, object, object], ...]
    query_weights: tuple[int, ...] | None = None
    expected_reduced_u64: int | None = None
    _packed_origins_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_directions_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_tmax_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_weights_u64: bytes | None = field(init=False, repr=False, compare=False)
    _device_input_sha256: str = field(init=False, repr=False, compare=False)
    _device_input_digest_u8: object = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        rows = tuple((tuple(origin), tuple(direction), tmax)
                     for origin, direction, tmax in self.queries)
        if not rows:
            _fail("RX006_INPUT_INVALID", "batch.queries", "nonempty required")
        for index, (origin, direction, _maximum) in enumerate(rows):
            if len(origin) != 3 or len(direction) != 3:
                _fail("RX006_INPUT_INVALID", f"batch.queries[{index}]", "ray arity")
        builtin_queries = all(
            type(item) in (int, float)
            for origin, direction, maximum in rows
            for item in (*origin, *direction, maximum))
        origin_array = direction_array = maximum_array = None
        if builtin_queries:
            try:
                candidate_origins = array(
                    "f", chain.from_iterable(origin for origin, _, _ in rows))
                candidate_directions = array(
                    "f", chain.from_iterable(direction for _, direction, _ in rows))
                candidate_maxima = array("f", (maximum for _, _, maximum in rows))
                if candidate_origins.itemsize == candidate_directions.itemsize \
                        == candidate_maxima.itemsize == 4:
                    origin_array = candidate_origins
                    direction_array = candidate_directions
                    maximum_array = candidate_maxima
            except (TypeError, ValueError, OverflowError):
                origin_array = direction_array = maximum_array = None
        if origin_array is None or direction_array is None or maximum_array is None \
                or not all(math.isfinite(item) for item in chain(
                    origin_array, direction_array, maximum_array)):
            origin_values: list[float] = []
            direction_values: list[float] = []
            maximum_values: list[float] = []
            for index, (origin, direction, maximum) in enumerate(rows):
                for axis, item in enumerate(origin):
                    origin_values.append(_require_f32(
                        item, f"batch.queries[{index}].origin[{axis}]",
                        code="RX006_INPUT_INVALID"))
                for axis, item in enumerate(direction):
                    direction_values.append(_require_f32(
                        item, f"batch.queries[{index}].direction[{axis}]",
                        code="RX006_INPUT_INVALID"))
                maximum_values.append(_require_f32(
                    maximum, f"batch.queries[{index}].tmax",
                    code="RX006_INPUT_INVALID"))
            origin_array = array("f", origin_values)
            direction_array = array("f", direction_values)
            maximum_array = array("f", maximum_values)
        for index, maximum_value in enumerate(maximum_array):
            offset = 3 * index
            if maximum_value <= 0.0 or all(
                    item == 0.0
                    for item in direction_array[offset:offset + 3]):
                _fail("RX006_INPUT_INVALID", f"batch.queries[{index}]",
                      "invalid f32 ray")
        packed_origins = origin_array
        packed_directions = direction_array
        packed_maxima = maximum_array
        if sys.byteorder != "little":
            packed_origins = array("f", origin_array); packed_origins.byteswap()
            packed_directions = array("f", direction_array); packed_directions.byteswap()
            packed_maxima = array("f", maximum_array); packed_maxima.byteswap()
        origins = packed_origins.tobytes()
        directions = packed_directions.tobytes()
        maxima = packed_maxima.tobytes()
        object.__setattr__(self, "queries", rows)
        object.__setattr__(self, "_packed_origins_f32", origins)
        object.__setattr__(self, "_packed_directions_f32", directions)
        object.__setattr__(self, "_packed_tmax_f32", maxima)
        weight_bytes = None
        if self.query_weights is not None:
            raw_weights = tuple(self.query_weights)
            builtin_weights = all(
                type(item) is int for item in raw_weights)
            weight_array = None
            if builtin_weights:
                try:
                    candidate_weights = array("Q", raw_weights)
                    if candidate_weights.itemsize == 8:
                        weight_array = candidate_weights
                except (TypeError, ValueError, OverflowError):
                    weight_array = None
            if weight_array is None:
                weights = tuple(_require_uint(
                    item, f"batch.query_weights[{index}]", bits=64,
                    code="RX006_INPUT_INVALID")
                    for index, item in enumerate(raw_weights))
                weight_array = array("Q", weights)
            else:
                weights = raw_weights
            if len(weights) != len(rows):
                _fail("RX006_INPUT_INVALID", "batch.query_weights", "exact U64 weights required")
            packed_weights = weight_array
            if sys.byteorder != "little":
                packed_weights = array("Q", weight_array); packed_weights.byteswap()
            weight_bytes = packed_weights.tobytes()
            object.__setattr__(self, "query_weights", weights)
        if self.expected_reduced_u64 is not None:
            object.__setattr__(
                self, "expected_reduced_u64",
                _require_uint(
                    self.expected_reduced_u64,
                    "batch.expected_reduced_u64",
                    bits=64,
                    code="RX006_INPUT_INVALID",
                ),
            )
        object.__setattr__(self, "_packed_weights_u64", weight_bytes)
        digest_hex = _sha_bytes(
            b"RTDL-V4-TRIANGLE-BATCH-V1\x00" + bytes(origins) + bytes(directions) +
            bytes(maxima) + (weight_bytes or b"<UNIT>"))
        object.__setattr__(self, "_device_input_sha256", digest_hex)
        # The v7 native reuse boundary consumes the exact same 32-byte value on
        # every execute.  Materialize its stable ctypes storage with the batch,
        # outside both prepare and execute timing, rather than constructing a
        # temporary pointer on every cache hit.
        object.__setattr__(self, "_device_input_digest_u8",
                           (ctypes.c_uint8 * 32).from_buffer_copy(
                               bytes.fromhex(digest_hex)))


@dataclass(frozen=True)
class TriangleReductionBufferStaticInput:
    """Immutable packed-buffer front door for large triangle inputs.

    Buffers are exact C-contiguous little-endian ``float32``/``uint32``
    projections.  The native prepare boundary performs the same finite-vertex
    and in-range-index validation as the tuple front door before building an
    acceleration structure.
    """

    vertices_f32le: object = field(repr=False, compare=False)
    triangles_u32le: object = field(repr=False, compare=False)
    vertex_count: int
    triangle_count: int
    event_capacity: int = 1
    _packed_vertices_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_triangles_u32: bytes = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        vertex_count = _require_uint(
            self.vertex_count, "static.vertex_count", bits=32,
            code="RX006_INPUT_INVALID")
        triangle_count = _require_uint(
            self.triangle_count, "static.triangle_count", bits=32,
            code="RX006_INPUT_INVALID")
        capacity = _require_uint(
            self.event_capacity, "static.event_capacity", bits=32,
            code="RX006_INPUT_INVALID")
        if not vertex_count or not triangle_count or not capacity:
            _fail("RX006_INPUT_INVALID", "static.packed_triangle",
                  "positive vertex, triangle, and event counts required")
        vertices = _require_packed_le_bytes(
            self.vertices_f32le, "static.vertices_f32le",
            expected_size=12 * vertex_count, code="RX006_INPUT_INVALID")
        triangles = _require_packed_le_bytes(
            self.triangles_u32le, "static.triangles_u32le",
            expected_size=12 * triangle_count, code="RX006_INPUT_INVALID")
        object.__setattr__(self, "vertices_f32le", vertices)
        object.__setattr__(self, "triangles_u32le", triangles)
        object.__setattr__(self, "vertex_count", vertex_count)
        object.__setattr__(self, "triangle_count", triangle_count)
        object.__setattr__(self, "event_capacity", capacity)
        object.__setattr__(self, "_packed_vertices_f32", vertices)
        object.__setattr__(self, "_packed_triangles_u32", triangles)


@dataclass(frozen=True)
class TriangleReductionBufferBatch:
    """Immutable packed-buffer front door for a triangle query batch."""

    query_origins_f32le: object = field(repr=False, compare=False)
    query_directions_f32le: object = field(repr=False, compare=False)
    query_tmax_f32le: object = field(repr=False, compare=False)
    query_count: int
    query_weights_u64le: object | None = field(default=None, repr=False, compare=False)
    expected_reduced_u64: int | None = None
    _packed_origins_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_directions_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_tmax_f32: bytes = field(init=False, repr=False, compare=False)
    _packed_weights_u64: bytes | None = field(init=False, repr=False, compare=False)
    _device_input_sha256: str = field(init=False, repr=False, compare=False)
    _device_input_digest_u8: object = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        count = _require_uint(
            self.query_count, "batch.query_count", bits=32,
            code="RX006_INPUT_INVALID")
        if not count:
            _fail("RX006_INPUT_INVALID", "batch.query_count", "positive count required")
        origins = _require_packed_le_bytes(
            self.query_origins_f32le, "batch.query_origins_f32le",
            expected_size=12 * count, code="RX006_INPUT_INVALID")
        directions = _require_packed_le_bytes(
            self.query_directions_f32le, "batch.query_directions_f32le",
            expected_size=12 * count, code="RX006_INPUT_INVALID")
        maxima = _require_packed_le_bytes(
            self.query_tmax_f32le, "batch.query_tmax_f32le",
            expected_size=4 * count, code="RX006_INPUT_INVALID")
        weights = None
        if self.query_weights_u64le is not None:
            weights = _require_packed_le_bytes(
                self.query_weights_u64le, "batch.query_weights_u64le",
                expected_size=8 * count, code="RX006_INPUT_INVALID")
        expected = self.expected_reduced_u64
        if expected is not None:
            expected = _require_uint(
                expected, "batch.expected_reduced_u64", bits=64,
                code="RX006_INPUT_INVALID")
        object.__setattr__(self, "query_origins_f32le", origins)
        object.__setattr__(self, "query_directions_f32le", directions)
        object.__setattr__(self, "query_tmax_f32le", maxima)
        object.__setattr__(self, "query_weights_u64le", weights)
        object.__setattr__(self, "query_count", count)
        object.__setattr__(self, "expected_reduced_u64", expected)
        object.__setattr__(self, "_packed_origins_f32", origins)
        object.__setattr__(self, "_packed_directions_f32", directions)
        object.__setattr__(self, "_packed_tmax_f32", maxima)
        object.__setattr__(self, "_packed_weights_u64", weights)
        digest_hex = _sha_bytes(
            b"RTDL-V4-TRIANGLE-BATCH-V1\x00" + origins + directions + maxima +
            (weights or b"<UNIT>"))
        object.__setattr__(self, "_device_input_sha256", digest_hex)
        object.__setattr__(self, "_device_input_digest_u8",
                           (ctypes.c_uint8 * 32).from_buffer_copy(
                               bytes.fromhex(digest_hex)))


@dataclass(frozen=True, slots=True)
class RTDLExecutionResult:
    output: object
    # Forensic output hashing is opt-in with ``include_diagnostics=True``.
    # The application fast path returns ``None`` so hashing cannot silently
    # re-enter a timed execute boundary.
    output_sha256: str | None
    executable_identity_sha256: str
    device_status: Mapping[str, object]
    role_counters: tuple[int, ...]
    traversal_receipt: Mapping[str, object] | None


def _target_projection(materialized: object) -> dict[str, object]:
    target = getattr(materialized, "_target", None)
    profile = getattr(target, "profile", None)
    toolchain = getattr(materialized, "_toolchain", None)
    if profile is None or toolchain is None:
        _fail("RX005_BUILD_INPUT_INVALID", "materialized.target", "target/toolchain unavailable")
    compute = tuple(_require_uint(
        item, f"toolchain.compute_capability[{index}]", bits=32,
        code="RX005_BUILD_INPUT_INVALID")
        for index, item in enumerate(getattr(toolchain, "compute_capability", ())))
    if len(compute) != 2:
        _fail("RX005_BUILD_INPUT_INVALID", "toolchain.compute_capability", compute)
    max_graph_depth = _require_uint(
        getattr(profile, "max_graph_depth", None), "target.max_graph_depth",
        bits=32, code="RX005_BUILD_INPUT_INVALID")
    if max_graph_depth == 0:
        _fail("RX005_BUILD_INPUT_INVALID", "target.max_graph_depth", max_graph_depth)
    return {
        "schema": "rtdl.v4.rtdlexe.target_toolchain_binding.v1",
        "target_sha256": _require_sha(getattr(profile, "target_sha256", None), "target.target_sha256"),
        "native_library_sha256": _require_sha(
            getattr(profile, "native_sha256", None), "target.native_library_sha256"),
        "provider": _require_string(getattr(profile, "provider", None), "target.provider"),
        "optix_sdk": _require_string(getattr(profile, "optix_sdk", None), "target.optix_sdk"),
        "compute_capability": list(compute),
        "supports_custom_aabb": _require_exact_bool(
            getattr(profile, "supports_custom_aabb", None),
            "target.supports_custom_aabb", code="RX005_BUILD_INPUT_INVALID"),
        "supports_builtin_triangle": _require_exact_bool(
            getattr(profile, "supports_builtin_triangle", None),
            "target.supports_builtin_triangle", code="RX005_BUILD_INPUT_INVALID"),
        "max_graph_depth": max_graph_depth,
        "python_version": _require_string(
            getattr(toolchain, "expected_python_version", None), "toolchain.python_version"),
        "numba_version": _require_string(
            getattr(toolchain, "expected_numba_version", None), "toolchain.numba_version"),
        "numpy_version": _require_string(
            getattr(toolchain, "expected_numpy_version", None), "toolchain.numpy_version"),
    }


def _runtime_projection(materialized: object, family: str) -> dict[str, object]:
    program = getattr(materialized, "_program", None)
    protocol = getattr(program, "protocol", None)
    if family == _BOUNDED:
        capacity = _require_uint(
            getattr(protocol, "capacity", None), "protocol.capacity", bits=64,
            code="RX005_BUILD_INPUT_INVALID")
        minimum = _require_f32(
            getattr(protocol, "minimum_overlap_f32", None),
            "protocol.minimum_overlap_f32", code="RX005_BUILD_INPUT_INVALID")
        if capacity <= 0:
            _fail("RX005_BUILD_INPUT_INVALID", "protocol.capacity", repr(capacity))
        if minimum < 0.0:
            _fail("RX005_BUILD_INPUT_INVALID", "protocol.minimum_overlap_f32", repr(minimum))
        return {
            "family": family,
            "native_abi": "rtdl.v4.prepared_bounded_relation_callback.v7",
            "capacity": capacity,
            "minimum_overlap_f32": minimum,
            "triangle_mode": None,
            "dynamic_status": "static_protocol_checked_compact_device_status_v5",
        }
    if family == _TRIANGLE:
        mode = getattr(getattr(protocol, "mode", None), "value", None)
        if mode not in _TRIANGLE_MODES:
            _fail("RX005_BUILD_INPUT_INVALID", "protocol.mode", repr(mode))
        return {
            "family": family,
            "native_abi": "rtdl.v4.prepared_triangle_reduction_callback.v7",
            "capacity": None,
            "minimum_overlap_f32": None,
            "triangle_mode": mode,
            "dynamic_status": "static_protocol_checked_compact_device_status_v5",
        }
    _fail("RX007_FAMILY_UNSUPPORTED", "program.family", family)


def _validate_native_producer_descriptor(
    value: object, *, family: str, native_abi: str, program_bundle: str,
) -> Mapping[str, object]:
    descriptor = _require_exact_keys(value, {
        "schema", "family", "native_abi", "program_bundle",
        "module_compile", "pipeline_compile", "pipeline_link",
        "program_groups", "sbt", "launch_parameters", "status", "product_output",
    }, "native_producer_descriptor")
    if descriptor["schema"] != _NATIVE_DESCRIPTOR_SCHEMA \
            or descriptor["family"] != family \
            or descriptor["native_abi"] != native_abi \
            or descriptor["program_bundle"] != program_bundle:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor", "family/ABI/bundle drift")
    module = _require_exact_keys(descriptor["module_compile"], {
        "max_register_count", "optimization_level", "debug_level",
    }, "native_producer_descriptor.module_compile")
    pipeline = _require_exact_keys(descriptor["pipeline_compile"], {
        "uses_motion_blur", "traversable_graph_flags", "payload_values",
        "attribute_values", "exception_flags", "launch_params_symbol",
        "primitive_type_flags",
    }, "native_producer_descriptor.pipeline_compile")
    link = _require_exact_keys(descriptor["pipeline_link"], {
        "max_trace_depth", "direct_callable_depth",
        "continuation_callable_depth", "max_traversable_graph_depth",
    }, "native_producer_descriptor.pipeline_link")
    groups = _require_exact_keys(descriptor["program_groups"], {
        "count", "raygen", "miss", "intersection", "any_hit", "closest_hit",
    }, "native_producer_descriptor.program_groups")
    sbt = _require_exact_keys(descriptor["sbt"], {
        "header_bytes", "alignment", "raygen_record_bytes",
        "miss_record_bytes", "hitgroup_record_bytes", "raygen_record_count",
        "miss_record_count", "hitgroup_record_count",
    }, "native_producer_descriptor.sbt")
    launch = _require_exact_keys(descriptor["launch_parameters"], {
        "struct_bytes", "layout",
    }, "native_producer_descriptor.launch_parameters")
    status = _require_exact_keys(descriptor["status"], {
        "device_row_bytes", "product_summary_bytes",
        "product_summary_schema_version", "required_invocation_mask",
        "terminal_invocation_mask", "success_transfer_is_constant_size",
        "fast_control_bytes", "fast_host_blocking_boundaries",
        "fast_host_blocking_boundary_scope",
        "fast_receipt_bytes", "fast_receipt_schema_version",
        "fast_receipt_semantic_field_count", "fast_receipt_field_offsets",
        "optix_validation_mode", "fast_semantic_compaction_algorithm",
        "fast_semantic_compaction_launch_count",
        "fast_callback_status_kernel_launch_count",
        "fast_checked_product_kernel_launch_count",
        "fast_compact_control_finalizer_kernel_launch_count",
        "fast_total_auxiliary_cuda_kernel_launch_count",
        "fast_execution_parameter_h2d_copy_call_count",
        "fast_execution_parameter_h2d_bytes",
        "fast_stream_ordered_memset_call_count",
        "fast_status_d2h_copy_call_count",
        "fast_dynamic_setup_separately_accounted",
        "fast_role_counters_materialized",
        "diagnostic_role_counters_materialized", "fast_status_before_output",
    }, "native_producer_descriptor.status")
    if family == _BOUNDED:
        product_output = _require_exact_keys(descriptor["product_output"], {
            "schema", "row_bytes", "capacity_bounded",
        }, "native_producer_descriptor.product_output")
    else:
        product_output = _require_exact_keys(descriptor["product_output"], {
            "schema", "scalar_bytes", "checked_result_bytes",
            "per_ray_detail_d2h_on_product_success",
            "event_row_detail_d2h_on_product_success", "unit_or_u64_multiplier",
        }, "native_producer_descriptor.product_output")
    legacy_abi = (
        "rtdl.v4.prepared_bounded_relation_callback.v5"
        if family == _BOUNDED else
        "rtdl.v4.prepared_triangle_reduction_callback.v5")
    online_abi = (
        "rtdl.v4.prepared_bounded_relation_callback.v6"
        if family == _BOUNDED else
        "rtdl.v4.prepared_triangle_reduction_callback.v6")
    lean_abi = (
        "rtdl.v4.prepared_bounded_relation_callback.v7"
        if family == _BOUNDED else
        "rtdl.v4.prepared_triangle_reduction_callback.v7")
    if native_abi not in {legacy_abi, online_abi, lean_abi}:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor.native_abi", native_abi)
    online_monitor = native_abi in {online_abi, lean_abi}
    expected_fast_control_bytes = (
        (28 if family == _BOUNDED else (12 if native_abi == lean_abi else 88))
        if online_monitor else (16 if family == _BOUNDED else 4))
    expected_callback_status_launches = (
        0 if online_monitor else (5 if family == _BOUNDED else 3))
    expected_checked_product_launches = (
        0 if online_monitor or family == _BOUNDED else 2)
    expected_control_finalizer_launches = 0 if online_monitor else 1
    expected_total_auxiliary_launches = (
        (1 if family == _BOUNDED else 0) if online_monitor
        else (7 if family == _BOUNDED else 6))
    expected_parameter_bytes = (
        (240 if family == _BOUNDED else 224) if online_monitor
        else (224 if family == _BOUNDED else 200))
    expected_memset_calls = (
        (4 if family == _BOUNDED else 2) if online_monitor
        else (9 if family == _BOUNDED else 4))
    expected_fast_role_counters = bool(
        native_abi == online_abi and family == _TRIANGLE)
    integer_values = [*module.values(),
        *[pipeline[key] for key in pipeline if key != "launch_params_symbol"],
        *link.values(), groups["count"],
        *[sbt[key] for key in sbt], launch["struct_bytes"],
        status["device_row_bytes"], status["product_summary_bytes"],
        status["product_summary_schema_version"], status["required_invocation_mask"],
        status["terminal_invocation_mask"], status["fast_control_bytes"],
        status["fast_host_blocking_boundaries"], status["fast_receipt_bytes"],
        status["fast_receipt_schema_version"],
        status["fast_receipt_semantic_field_count"],
        status["fast_semantic_compaction_launch_count"],
        status["fast_callback_status_kernel_launch_count"],
        status["fast_checked_product_kernel_launch_count"],
        status["fast_compact_control_finalizer_kernel_launch_count"],
        status["fast_total_auxiliary_cuda_kernel_launch_count"],
        status["fast_execution_parameter_h2d_copy_call_count"],
        status["fast_execution_parameter_h2d_bytes"],
        status["fast_stream_ordered_memset_call_count"],
        status["fast_status_d2h_copy_call_count"]]
    if any(not isinstance(item, int) or isinstance(item, bool) or item < 0
           for item in integer_values) \
            or pipeline["launch_params_symbol"] != "params" \
            or link != {"max_trace_depth": 1, "direct_callable_depth": 0,
                        "continuation_callable_depth": 0,
                        "max_traversable_graph_depth": 1} \
            or groups["count"] != 3 \
            or any(sbt[key] != 1 for key in (
                "raygen_record_count", "miss_record_count", "hitgroup_record_count")) \
            or not isinstance(launch["layout"], list) or not launch["layout"] \
            or any(not isinstance(item, str) or not re.fullmatch(
                r"[a-z0-9_]+:[0-9]+:[0-9]+", item)
                   for item in launch["layout"]) \
            or status["product_summary_schema_version"] != 2 \
            or status["required_invocation_mask"] != ((1 << 1) | (1 << 6)) \
            or status["terminal_invocation_mask"] != (
                ((1 << 4) | (1 << 5)) if family == _BOUNDED else (1 << 5)) \
            or status["success_transfer_is_constant_size"] is not True \
            or status["fast_control_bytes"] != expected_fast_control_bytes \
            or status["fast_host_blocking_boundaries"] != 2 \
            or status["fast_host_blocking_boundary_scope"] != \
                "status_and_output__dynamic_setup_separate" \
            or status["fast_receipt_bytes"] != ctypes.sizeof(_FastPathReceipt) \
            or status["fast_receipt_schema_version"] != 2 \
            or status["fast_receipt_semantic_field_count"] != len(
                _FAST_PATH_RECEIPT_FIELD_OFFSETS) \
            or status["fast_receipt_field_offsets"] != \
                _FAST_PATH_RECEIPT_FIELD_OFFSETS \
            or status["optix_validation_mode"] != "OFF" \
            or status["fast_semantic_compaction_algorithm"] != (
                "u64_atomiccas_linear_probe_v1"
                if family == _BOUNDED else "NONE") \
            or status["fast_semantic_compaction_launch_count"] != (
                1 if family == _BOUNDED else 0) \
            or status["fast_callback_status_kernel_launch_count"] != \
                expected_callback_status_launches \
            or status["fast_checked_product_kernel_launch_count"] != \
                expected_checked_product_launches \
            or status["fast_compact_control_finalizer_kernel_launch_count"] != \
                expected_control_finalizer_launches \
            or status["fast_total_auxiliary_cuda_kernel_launch_count"] != \
                expected_total_auxiliary_launches \
            or status["fast_execution_parameter_h2d_copy_call_count"] != (
                2 if family == _BOUNDED else 1) \
            or status["fast_execution_parameter_h2d_bytes"] != \
                expected_parameter_bytes \
            or status["fast_stream_ordered_memset_call_count"] != \
                expected_memset_calls \
            or status["fast_status_d2h_copy_call_count"] != 1 \
            or status["fast_dynamic_setup_separately_accounted"] is not True \
            or status["fast_role_counters_materialized"] is not \
                expected_fast_role_counters \
            or status["diagnostic_role_counters_materialized"] is not True \
            or status["fast_status_before_output"] is not True:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor", "native producer facts invalid")
    product_invalid = (
        product_output["schema"] != "rtdl.v4.bounded_relation_rows.v1"
        or product_output["row_bytes"] != 8
        or product_output["capacity_bounded"] is not True
    ) if family == _BOUNDED else (
        product_output["schema"] != "rtdl.v4.checked_u64_device_product_sum.v1"
        or product_output["scalar_bytes"] != 8
        or not isinstance(product_output["checked_result_bytes"], int)
        or isinstance(product_output["checked_result_bytes"], bool)
        or product_output["checked_result_bytes"] <= 0
        or product_output["per_ray_detail_d2h_on_product_success"] is not False
        or product_output["event_row_detail_d2h_on_product_success"] is not False
        or product_output["unit_or_u64_multiplier"] is not True
    )
    if product_invalid:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor.product_output", "product output drift")
    status_row_type = globals().get("_DeviceStatusRow")
    summary_type = globals().get("_ProductStatusSummary")
    if status_row_type is not None and summary_type is not None \
            and (status["device_row_bytes"] != ctypes.sizeof(status_row_type)
                 or status["product_summary_bytes"] != ctypes.sizeof(summary_type)):
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor.status", "ctypes/native layout mismatch")
    checked_result_type = globals().get("_CheckedProductResult")
    if family == _TRIANGLE and checked_result_type is not None \
            and product_output["checked_result_bytes"] != ctypes.sizeof(checked_result_type):
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native_producer_descriptor.product_output",
              "checked product result layout mismatch")
    return descriptor


def _query_native_producer_descriptor(
    library: object, *, family: str, native_abi: str, program_bundle: str,
) -> Mapping[str, object]:
    query = getattr(library, "rtdl_optix_v4_rtdlexe_producer_descriptor_v1", None)
    if query is None:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native.producer_descriptor", "export missing")
    query.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t,
                      ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_char),
                      ctypes.c_size_t]
    query.restype = ctypes.c_int
    output = ctypes.create_string_buffer(65536)
    output_bytes = ctypes.c_size_t()
    error = ctypes.create_string_buffer(16384)
    _raise_native(int(query(
        family.encode("utf-8"), output, len(output), ctypes.byref(output_bytes),
        error, len(error))), error, "native.producer_descriptor")
    raw = bytes(output.raw[:output_bytes.value])
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH",
              "native.producer_descriptor", exc)
    return _validate_native_producer_descriptor(
        parsed, family=family, native_abi=native_abi,
        program_bundle=program_bundle)


def _build_native_producer_descriptor(
    materialized: object, *, target: Mapping[str, object], runtime: Mapping[str, object],
) -> Mapping[str, object]:
    target_object = getattr(materialized, "_target", None)
    path = _absolute_unresolved_path(
        getattr(target_object, "native_library_path", ""))
    try:
        library = _load_verified_native_file_descriptor(
            path, expected_sha256=str(target["native_library_sha256"]),
            code="RX005_BUILD_INPUT_INVALID",
            identity_path="materialized.target.native_library_path")
        bundle = ("v4_custom_aabb_bounded_relation_composed"
                  if runtime["family"] == _BOUNDED
                  else "v4_builtin_triangle_checked_reduction_composed")
        return _query_native_producer_descriptor(
            library, family=str(runtime["family"]),
            native_abi=str(runtime["native_abi"]), program_bundle=bundle)
    finally:
        if "library" in locals():
            _release_native_library_image(library)


def _provider_key_projection(
    materialized: object,
    *,
    roots: RTDLExecutableBuildRoots,
    target: Mapping[str, object],
) -> dict[str, object]:
    backend = getattr(materialized, "_backend")
    executable = backend["executable"]
    abi_object = backend["abi"]
    abi = _coerce_mapping(abi_object, "materialized.backend.abi")
    generated = tuple(getattr(executable, "generated_leaves", ()))
    compiled = tuple(getattr(executable, "compiled_leaves", ()))
    generated_rows = [[
        _require_string(getattr(getattr(item, "role", None), "value", None), "generated.role"),
        _require_sha(getattr(item, "generated_source_sha256", None), "generated.source_sha256"),
    ] for item in generated]
    compiled_rows = [[
        _require_string(getattr(item, "role", None), "compiled.role"),
        _require_sha(getattr(item, "ptx_sha256", None), "compiled.ptx_sha256"),
    ] for item in compiled]
    required_roles = [
        _require_string(row.get("role") if isinstance(row, Mapping) else None,
                        f"provider_key.roles[{index}].role")
        for index, row in enumerate(abi.get("roles", []))
    ]
    if not required_roles or [row[0] for row in generated_rows] != required_roles \
            or [row[0] for row in compiled_rows] != required_roles:
        _fail("RX005_BUILD_INPUT_INVALID", "provider_key.role_order", {
            "required": required_roles, "generated": generated_rows, "compiled": compiled_rows})
    wrapper = getattr(executable, "wrapper", None)
    composed = getattr(executable, "composed", None)
    wrapper_source_sha = _require_sha(
        getattr(wrapper, "source_sha256", None), "wrapper.source_sha256")
    canonical_abi = _canonical(abi)
    payload_layout = _sha_bytes(b"payload-layout-v1\x00" + canonical_abi)
    attribute_layout = _sha_bytes(b"attribute-layout-v1\x00" + canonical_abi)
    family = _require_string(
        getattr(getattr(materialized.identity, "program", None), "family", None),
        "materialized.identity.program.family")
    hitgroup_roles = (
        ["intersection", "any_hit", "closest_hit"]
        if family == _BOUNDED else ["any_hit", "closest_hit"]
    )
    sbt_layout_body = {
        "schema": "rtdl.v4.rtdlexe.sbt_layout_projection.v1",
        "evidence_kind": "compiler_and_native_schema_identity__not_runtime_record_bytes",
        "raygen_records": 1,
        "miss_records": 1,
        "hitgroup_records": 1,
        "hitgroup_program_roles": hitgroup_roles,
        "trace_depth": 1,
        "callback_abi_sha256": abi["abi_sha256"],
        "physical_template": getattr(wrapper, "physical_template", None),
    }
    body = {
        "schema": "rtdl.v4.rtdlexe.provider_key.v1",
        "callback_ir_sha256": abi["callback_ir_sha256"],
        "callback_abi_sha256": abi["abi_sha256"],
        "callback_abi_projection": abi,
        "generated_source_sha256_by_role": generated_rows,
        "leaf_ptx_sha256_by_role": compiled_rows,
        "wrapper_source_sha256": wrapper_source_sha,
        "wrapper_template": _require_string(getattr(wrapper, "schema", None), "wrapper.schema"),
        "physical_template": _require_string(
            getattr(wrapper, "physical_template", None), "wrapper.physical_template"),
        "wrapper_role_symbols": [list(item) for item in getattr(wrapper, "role_symbols", ())],
        "payload_layout_sha256": payload_layout,
        "attribute_layout_sha256": attribute_layout,
        "sbt_layout_projection": sbt_layout_body,
        "sbt_layout_sha256": _digest(sbt_layout_body),
        "native_provider_sha256": target["native_library_sha256"],
        "target_compute_capability": list(target["compute_capability"]),
        "python_version": target["python_version"],
        "numba_version": target["numba_version"],
        "numpy_version": target["numpy_version"],
        "llvmlite_version": roots.llvmlite_version,
        "cuda_toolkit_version": roots.cuda_toolkit_version,
        "optix_sdk_version": target["optix_sdk"],
        "ptx_isa": _require_string(getattr(composed, "ptx_version", None), "composed.ptx_version"),
        "ptx_target": _require_string(getattr(composed, "ptx_target", None), "composed.ptx_target"),
        "address_size": _require_string(getattr(composed, "address_size", None), "composed.address_size"),
        "wrapper_numeric_policy": roots.wrapper_numeric_policy,
        "leaf_numeric_policy": roots.leaf_numeric_policy,
        "composer_schema": roots.composer_schema,
        "compile_options": [
            _require_string(item, f"executable.compiler_options[{index}]")
            for index, item in enumerate(getattr(executable, "compiler_options", ()))
        ],
        "link_options": list(roots.link_options),
        "composed_leaf_bindings": [list(item) for item in getattr(composed, "leaf_bindings", ())],
    }
    return {**body, "provider_key_sha256": _digest(body)}


def _execution_schema_projection(
    *,
    provider_key: Mapping[str, object],
    executable: object,
    protocol_declaration: object,
    runtime: Mapping[str, object],
    target: Mapping[str, object],
    composed_ptx_sha256: str,
    native_producer_descriptor: Mapping[str, object],
) -> dict[str, object]:
    wrapper = getattr(executable, "wrapper", None)
    declaration_mapping = _coerce_mapping(
        protocol_declaration, "protocol.declaration")
    program_bundle = (
        "v4_custom_aabb_bounded_relation_composed"
        if runtime["family"] == _BOUNDED else
        "v4_builtin_triangle_checked_reduction_composed"
    )
    common = {
        "callback_abi_sha256": provider_key["callback_abi_sha256"],
        "wrapper_source_sha256": provider_key["wrapper_source_sha256"],
        "wrapper_role_symbols": provider_key["wrapper_role_symbols"],
        "contract_sha256": declaration_mapping.get("contract_sha256"),
        "composed_ptx_sha256": composed_ptx_sha256,
        "native_provider_sha256": target["native_library_sha256"],
        "compiler_options": provider_key["compile_options"],
        "link_options": provider_key["link_options"],
    }
    module_body = {"kind": "module_schema_identity", **common}
    program_group_body = {
        "kind": "program_group_schema_identity", **common,
        "physical_template": provider_key["physical_template"],
        "program_bundle": program_bundle,
    }
    pipeline_body = {
        "kind": "pipeline_schema_identity", **common,
        "program_group_schema_sha256": _digest(program_group_body),
        "trace_depth": 1,
    }
    sbt_body = {
        "kind": "sbt_schema_identity", **common,
        "sbt_layout_sha256": provider_key["sbt_layout_sha256"],
        "program_group_schema_sha256": _digest(program_group_body),
    }
    launch_body = {
        "kind": "launch_parameter_schema_identity", **common,
        "callback_abi_projection_sha256": _digest(provider_key["callback_abi_projection"]),
        "runtime_native_abi": runtime["native_abi"],
    }
    status_body = {
        "kind": "status_schema_identity", **common,
        "dynamic_status": runtime["dynamic_status"],
        "runtime_status_codes": provider_key["callback_abi_projection"].get("runtime_status_codes"),
    }
    body = {
        "schema": "rtdl.v4.rtdlexe.execution_schema_projection.v1",
        "evidence_kind": "native_exported_producer_descriptor_plus_compiler_identity",
        "actual_runtime_handle_bytes_bound": False,
        "actual_runtime_handle_bytes_unavailable_reason": (
            "OptiX module/program-group/pipeline/SBT handles are process-local; "
            "the artifact binds their producer schemas and later proves the native program bundle at execution"),
        "native_program_bundle": program_bundle,
        "native_producer_descriptor": dict(native_producer_descriptor),
        "native_producer_descriptor_sha256": _digest(native_producer_descriptor),
        "module_schema_sha256": _digest(module_body),
        "program_group_schema_sha256": _digest(program_group_body),
        "pipeline_schema_sha256": _digest(pipeline_body),
        "sbt_schema_sha256": _digest(sbt_body),
        "launch_parameter_schema_sha256": _digest(launch_body),
        "status_schema_sha256": _digest(status_body),
        "producer_inputs": {
            "module": module_body, "program_group": program_group_body,
            "pipeline": pipeline_body, "sbt": sbt_body,
            "launch_parameters": launch_body, "status": status_body,
        },
    }
    return {**body, "execution_schema_sha256": _digest(body)}


def _build_product_projection(
    *, executable_identity: Mapping[str, object], declaration: Mapping[str, object],
    compiler_projection: Mapping[str, object], decision: Mapping[str, object],
    runtime: Mapping[str, object], target: Mapping[str, object], ptx_sha256: str,
    compiler_options: Sequence[str], ptx_metadata: Mapping[str, object],
    provider_key: Mapping[str, object], execution_schema: Mapping[str, object],
    deployment_id: str,
    generic_family_binding: Mapping[str, object] | None = None,
) -> dict[str, object]:
    result = {
        "schema": (
            _FAMILY_PROJECTION_SCHEMA
            if generic_family_binding is not None
            else _PROJECTION_SCHEMA
        ),
        "deployment_id": deployment_id,
        "family": runtime["family"],
        "executable_identity": dict(executable_identity),
        "protocol_contract_sha256": declaration["contract_sha256"],
        "compiler_projection_sha256": compiler_projection["projection_sha256"],
        "protocol_decision_sha256": decision["decision_sha256"],
        "runtime": dict(runtime),
        "target_toolchain": dict(target),
        "composed_ptx_sha256": ptx_sha256,
        "compiler_options": list(compiler_options),
        "ptx_metadata": dict(ptx_metadata),
        "provider_key": dict(provider_key),
        "execution_schema": dict(execution_schema),
    }
    if generic_family_binding is not None:
        result["generic_family_binding"] = dict(generic_family_binding)
    return result


def _verify_generic_family_binding(
    value: object,
    *,
    family: str,
    executable_identity: Mapping[str, object],
    target: Mapping[str, object],
    composed_ptx_sha256: str,
) -> Mapping[str, object]:
    binding = _require_exact_keys(value, {
        "schema", "format_id", "plan_sha256",
        "provider_descriptor_sha256", "provider_projection_sha256",
        "artifact_bundle_sha256", "family_executable_identity",
        "binding_sha256",
    }, "generic_family_binding")
    if binding["schema"] != _FAMILY_BINDING_SCHEMA \
            or binding["format_id"] != _FAMILY_DEPLOYMENT_FORMAT_ID:
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "generic_family_binding.schema",
            binding.get("schema"),
        )
    body = dict(binding)
    binding_sha256 = body.pop("binding_sha256")
    if _require_sha(
        binding_sha256, "generic_family_binding.binding_sha256"
    ) != _digest(body):
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "generic_family_binding.binding_sha256",
            "seal differs",
        )
    for key in (
        "plan_sha256", "provider_descriptor_sha256",
        "provider_projection_sha256", "artifact_bundle_sha256",
    ):
        _require_sha(binding[key], f"generic_family_binding.{key}")
    identity = _require_exact_keys(binding["family_executable_identity"], {
        "schema", "provider_descriptor_sha256",
        "provider_projection_sha256", "plan_sha256", "target_sha256",
        "executable_sha256", "provider_artifact_sha256",
        "generated_artifact_sha256", "identity_sha256",
    }, "generic_family_binding.family_executable_identity")
    identity_body = dict(identity)
    identity_sha256 = identity_body.pop("identity_sha256")
    if identity_body.pop("schema", None) != \
            "rtdl.family_executable_identity.v1" \
            or _require_sha(
                identity_sha256,
                "generic_family_binding.family_executable_identity.identity_sha256",
            ) != _digest({
                "schema": "rtdl.family_executable_identity.v1",
                **identity_body,
            }):
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "generic_family_binding.family_executable_identity",
            "identity seal differs",
        )
    for key in identity_body:
        _require_sha(
            identity_body[key],
            f"generic_family_binding.family_executable_identity.{key}",
        )
    if (
        identity_body["provider_descriptor_sha256"]
            != binding["provider_descriptor_sha256"]
        or identity_body["provider_projection_sha256"]
            != binding["provider_projection_sha256"]
        or identity_body["plan_sha256"] != binding["plan_sha256"]
        or identity_body["target_sha256"] != target["target_sha256"]
        or identity_body["provider_artifact_sha256"]
            != target["native_library_sha256"]
        or identity_body["generated_artifact_sha256"]
            != composed_ptx_sha256
        or identity_body["executable_sha256"]
            != executable_identity.get("generated_executable_sha256")
    ):
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "generic_family_binding",
            f"family/provider/product chain differs for {family}",
        )
    return binding


def _build_rtdlexe_impl(
    materialized: object,
    *,
    artifact_directory: str | os.PathLike[str],
    authority_path: str | os.PathLike[str],
    build_roots: RTDLExecutableBuildRoots,
    deployment_id: str,
    generic_family_binding: Mapping[str, object] | None,
) -> BuiltRTDLExecutable:
    """Freeze one already-checked materialized program for deployment.

    This function is intentionally the only compiler-side entry point in this
    module.  It may import the build graph; :func:`load_rtdlexe` never does.
    """

    if not isinstance(build_roots, RTDLExecutableBuildRoots):
        _fail("RX005_BUILD_INPUT_INVALID", "build_roots", type(build_roots).__name__)
    deployment_id = _require_string(deployment_id, "deployment_id")
    decision_object = getattr(materialized, "protocol_contract_decision", None)
    decision = _coerce_mapping(decision_object, "materialized.protocol_contract_decision")
    if decision.get("verdict") != "ACCEPT" or decision.get("findings") != []:
        _fail("RX008_PROTOCOL_NOT_ACCEPTED", "materialized.protocol_contract_decision", decision)
    identity_object = getattr(materialized, "identity", None)
    executable_identity = _coerce_mapping(identity_object, "materialized.identity")
    executable_identity_sha = _require_sha(
        getattr(identity_object, "identity_sha256", None),
        "materialized.identity.identity_sha256",
    )
    program_identity = getattr(identity_object, "program", None)
    family = _require_string(getattr(program_identity, "family", None), "program.family")
    backend = getattr(materialized, "_backend", None)
    if not isinstance(backend, Mapping):
        _fail("RX005_BUILD_INPUT_INVALID", "materialized.backend", type(backend).__name__)
    executable = backend.get("executable")
    composed = getattr(executable, "composed", None)
    ptx = getattr(composed, "ptx", None)
    if not isinstance(ptx, str) or not ptx:
        _fail("RX005_BUILD_INPUT_INVALID", "materialized.executable.composed.ptx", repr(ptx))
    ptx_bytes = ptx.encode("utf-8")
    ptx_sha = _sha_bytes(ptx_bytes)
    if ptx_sha != executable_identity.get("composed_ptx_sha256") \
            or ptx_sha != getattr(composed, "ptx_sha256", None):
        _fail("RX009_PTX_IDENTITY_MISMATCH", "materialized.executable", ptx_sha)

    # Build-only import: rederive both sides from the accepted compiler graph.
    from .v4_callback_lifecycle import (  # pylint: disable=import-outside-toplevel
        _compiled_protocol_projection,
        _declared_protocol_contract,
    )

    program = getattr(materialized, "_program")
    declaration_object = _declared_protocol_contract(
        program, executable_sha256=executable_identity["generated_executable_sha256"])
    projection_object = _compiled_protocol_projection(
        program,
        authority=backend["authority"],
        contract=backend["contract"],
        abi=backend["abi"],
        executable_sha256=executable_identity["generated_executable_sha256"],
        composed_ptx_sha256=ptx_sha,
    )
    declaration = _coerce_mapping(declaration_object, "protocol.declaration")
    compiler_projection = _coerce_mapping(projection_object, "protocol.compiler_projection")
    if decision.get("contract_sha256") != declaration.get("contract_sha256") \
            or decision.get("projection_sha256") != compiler_projection.get("projection_sha256"):
        _fail("RX010_DECISION_CHAIN_MISMATCH", "protocol.decision", "build rederivation drift")
    runtime = _runtime_projection(materialized, family)
    target = _target_projection(materialized)
    provider_key = _provider_key_projection(
        materialized, roots=build_roots, target=target)
    native_producer_descriptor = _build_native_producer_descriptor(
        materialized, target=target, runtime=runtime)
    execution_schema = _execution_schema_projection(
        provider_key=provider_key,
        executable=executable,
        protocol_declaration=declaration,
        runtime=runtime,
        target=target,
        composed_ptx_sha256=ptx_sha,
        native_producer_descriptor=native_producer_descriptor,
    )
    compiler_options = tuple(
        _require_string(item, f"executable.compiler_options[{index}]")
        for index, item in enumerate(getattr(executable, "compiler_options", ())))
    ptx_metadata = {
        "version": _require_string(getattr(composed, "ptx_version", None), "ptx.version"),
        "target": _require_string(getattr(composed, "ptx_target", None), "ptx.target"),
        "address_size": _require_string(getattr(composed, "address_size", None), "ptx.address_size"),
    }
    product_projection = _build_product_projection(
        executable_identity=executable_identity,
        declaration=declaration,
        compiler_projection=compiler_projection,
        decision=decision,
        runtime=runtime,
        target=target,
        ptx_sha256=ptx_sha,
        compiler_options=compiler_options,
        ptx_metadata=ptx_metadata,
        provider_key=provider_key,
        execution_schema=execution_schema,
        deployment_id=deployment_id,
        generic_family_binding=generic_family_binding,
    )
    family_binding = None
    family_identity_sha = None
    if generic_family_binding is not None:
        family_binding = _verify_generic_family_binding(
            product_projection["generic_family_binding"],
            family=family,
            executable_identity=executable_identity,
            target=target,
            composed_ptx_sha256=ptx_sha,
        )
        family_identity = family_binding["family_executable_identity"]
        assert isinstance(family_identity, Mapping)
        family_identity_sha = _require_sha(
            family_identity["identity_sha256"],
            "generic_family_binding.family_executable_identity.identity_sha256",
        )
    artifact = {
        "schema": (
            _FAMILY_ARTIFACT_SCHEMA
            if family_binding is not None
            else _ARTIFACT_SCHEMA
        ),
        "format_version": 2 if family_binding is not None else 1,
        "product_projection": product_projection,
        "protocol_declaration": declaration,
        "compiler_projection": compiler_projection,
        "protocol_decision": decision,
        "composed_ptx_base64": base64.b64encode(ptx_bytes).decode("ascii"),
    }
    artifact_bytes = _canonical(artifact) + b"\n"
    artifact_sha = _sha_bytes(artifact_bytes)
    artifact_path = Path(artifact_directory).expanduser().resolve() / f"{artifact_sha}.rtdlexe"
    _write_create_or_exact(
        artifact_path, artifact_bytes, code="RX011_ARTIFACT_COLLISION")

    authority_body = {
        "schema": (
            _FAMILY_AUTHORITY_SCHEMA
            if family_binding is not None
            else _AUTHORITY_SCHEMA
        ),
        "authority_version": 2 if family_binding is not None else 1,
        "artifact_sha256": artifact_sha,
        "artifact_bytes": len(artifact_bytes),
        "product_projection_sha256": _digest(product_projection),
        "protocol_decision_sha256": decision["decision_sha256"],
        "executable_identity_sha256": executable_identity_sha,
        "native_library_sha256": target["native_library_sha256"],
        "target_sha256": target["target_sha256"],
        "deployment_id": deployment_id,
        "family": family,
        "task_semantics_sha256": declaration["task_semantics_sha256"],
        "target_compute_capability": list(target["compute_capability"]),
    }
    if family_binding is not None:
        authority_body["generic_family_binding_sha256"] = _require_sha(
            family_binding["binding_sha256"],
            "generic_family_binding.binding_sha256",
        )
        authority_body["family_executable_identity_sha256"] = \
            family_identity_sha
    authority = {
        **authority_body,
        "authority_seal": _sha_bytes(
            (
                _FAMILY_AUTHORITY_DOMAIN
                if family_binding is not None
                else _AUTHORITY_DOMAIN
            ) + _canonical(authority_body)
        ),
    }
    authority_bytes = _canonical(authority) + b"\n"
    authority_output = _absolute_unresolved_path(authority_path)
    if authority_output == artifact_path:
        _fail("RX012_AUTHORITY_NOT_DETACHED", "authority_path", authority_output)
    _write_create_or_exact(
        authority_output, authority_bytes, code="RX013_AUTHORITY_COLLISION")
    return BuiltRTDLExecutable(
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha,
        authority_path=authority_output,
        authority_sha256=_sha_bytes(authority_bytes),
        executable_identity_sha256=executable_identity_sha,
        family_executable_identity_sha256=family_identity_sha,
    )


def build_rtdlexe(
    materialized: object,
    *,
    artifact_directory: str | os.PathLike[str],
    authority_path: str | os.PathLike[str],
    build_roots: RTDLExecutableBuildRoots,
    deployment_id: str,
) -> BuiltRTDLExecutable:
    """Freeze one accepted legacy V4 materialization as a V1 artifact."""

    return _build_rtdlexe_impl(
        materialized,
        artifact_directory=artifact_directory,
        authority_path=authority_path,
        build_roots=build_roots,
        deployment_id=deployment_id,
        generic_family_binding=None,
    )


def build_family_rtdlexe(
    materialized: object,
    *,
    artifact_directory: str | os.PathLike[str],
    authority_path: str | os.PathLike[str],
    build_roots: RTDLExecutableBuildRoots,
    deployment_id: str,
) -> BuiltRTDLExecutable:
    """Freeze a public generic-family materialization as a family-bound artifact."""

    from .v4_generic_family_lifecycle import (  # build-side import only
        FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2,
        FamilyDeploymentExportV1,
        MaterializedGenericFamilyProgram,
    )

    if not isinstance(materialized, MaterializedGenericFamilyProgram):
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "materialized",
            "MaterializedGenericFamilyProgram required",
        )
    exported = materialized.export_deployment(
        FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2
    )
    if not isinstance(exported, FamilyDeploymentExportV1):
        _fail(
            "RX058_FAMILY_BINDING_INVALID",
            "materialized.export_deployment",
            type(exported).__name__,
        )
    exported.revalidate()
    built = _build_rtdlexe_impl(
        exported.provider_payload,
        artifact_directory=artifact_directory,
        authority_path=authority_path,
        build_roots=build_roots,
        deployment_id=deployment_id,
        generic_family_binding=exported.family_binding,
    )
    exported.revalidate()
    return built


def _verify_contract_pair(
    declaration: Mapping[str, object], projection: Mapping[str, object],
) -> tuple[str, ...]:
    declaration = _require_exact_keys(declaration, {
        "schema", "family", "task_semantics_sha256", "role_effects",
        "attribute_abi_ownership", "physical_bindings", "continuation_policy",
        "checked_executable_sha256", "contract_sha256",
    }, "artifact.protocol_declaration")
    projection = _require_exact_keys(projection, {
        "schema", "family", "task_semantics_sha256", "role_effects",
        "attribute_abi_ownership", "physical_bindings", "continuation_policy",
        "actual_executable_sha256", "generated_device_source_sha256",
        "generated_host_source_sha256", "projection_sha256",
    }, "artifact.compiler_projection")
    declaration_body = dict(declaration); declaration_seal = declaration_body.pop("contract_sha256")
    projection_body = dict(projection); projection_seal = projection_body.pop("projection_sha256")
    if _require_sha(declaration_seal, "declaration.contract_sha256") != _digest(declaration_body):
        _fail("RX014_PROTOCOL_SEAL_MISMATCH", "declaration.contract_sha256", declaration_seal)
    if _require_sha(projection_seal, "projection.projection_sha256") != _digest(projection_body):
        _fail("RX014_PROTOCOL_SEAL_MISMATCH", "projection.projection_sha256", projection_seal)
    mismatches: list[str] = []
    if (declaration["family"], declaration["task_semantics_sha256"], declaration["physical_bindings"]) != \
            (projection["family"], projection["task_semantics_sha256"], projection["physical_bindings"]):
        mismatches.append("CP003_PHYSICAL_BINDING_MISMATCH")
    if declaration["role_effects"] != projection["role_effects"]:
        mismatches.append("CP001_ROLE_EFFECT_MISMATCH")
    if declaration["attribute_abi_ownership"] != projection["attribute_abi_ownership"]:
        mismatches.append("CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH")
    if declaration["continuation_policy"] != projection["continuation_policy"]:
        mismatches.append("CP004_CONTINUATION_STATUS_MISMATCH")
    if declaration["checked_executable_sha256"] != projection["actual_executable_sha256"]:
        mismatches.append("CP005_EXECUTABLE_IDENTITY_MISMATCH")
    return tuple(mismatches)


def _validate_runtime(runtime: object) -> Mapping[str, object]:
    runtime = _require_exact_keys(runtime, {
        "family", "native_abi", "capacity", "minimum_overlap_f32",
        "triangle_mode", "dynamic_status",
    }, "product_projection.runtime")
    family = runtime["family"]
    if family == _BOUNDED:
        capacity = _require_uint(
            runtime["capacity"], "product_projection.runtime.capacity", bits=64,
            code="RX015_RUNTIME_SCHEMA_INVALID")
        minimum = _require_f32(
            runtime["minimum_overlap_f32"],
            "product_projection.runtime.minimum_overlap_f32",
            code="RX015_RUNTIME_SCHEMA_INVALID")
        if runtime["native_abi"] not in {
                    "rtdl.v4.prepared_bounded_relation_callback.v5",
                    "rtdl.v4.prepared_bounded_relation_callback.v6",
                    "rtdl.v4.prepared_bounded_relation_callback.v7"} \
                or capacity <= 0 or runtime["capacity"] != capacity \
                or runtime["minimum_overlap_f32"] != minimum or minimum < 0.0 \
                or runtime["triangle_mode"] is not None:
            _fail("RX015_RUNTIME_SCHEMA_INVALID", "product_projection.runtime", runtime)
    elif family == _TRIANGLE:
        if runtime["native_abi"] not in {
                    "rtdl.v4.prepared_triangle_reduction_callback.v5",
                    "rtdl.v4.prepared_triangle_reduction_callback.v6",
                    "rtdl.v4.prepared_triangle_reduction_callback.v7"} \
                or runtime["capacity"] is not None \
                or runtime["minimum_overlap_f32"] is not None \
                or runtime["triangle_mode"] not in _TRIANGLE_MODES:
            _fail("RX015_RUNTIME_SCHEMA_INVALID", "product_projection.runtime", runtime)
    else:
        _fail("RX007_FAMILY_UNSUPPORTED", "product_projection.runtime.family", family)
    if str(runtime["native_abi"]).endswith(".v7"):
        expected_dynamic_status = "static_protocol_checked_compact_device_status_v5"
    elif str(runtime["native_abi"]).endswith(".v6"):
        expected_dynamic_status = "fused_online_monitor_compact_status_v4"
    else:
        expected_dynamic_status = "device_validated_compact_status_v3"
    if runtime["dynamic_status"] != expected_dynamic_status:
        _fail("RX015_RUNTIME_SCHEMA_INVALID", "product_projection.runtime.dynamic_status", runtime)
    return runtime


def _verify_provider_key(value: object) -> Mapping[str, object]:
    provider = _require_exact_keys(value, {
        "schema", "callback_ir_sha256", "callback_abi_sha256",
        "callback_abi_projection", "generated_source_sha256_by_role",
        "leaf_ptx_sha256_by_role", "wrapper_source_sha256", "wrapper_template",
        "physical_template", "wrapper_role_symbols", "payload_layout_sha256",
        "attribute_layout_sha256", "sbt_layout_projection", "sbt_layout_sha256",
        "native_provider_sha256", "target_compute_capability", "python_version",
        "numba_version", "numpy_version", "llvmlite_version", "cuda_toolkit_version",
        "optix_sdk_version", "ptx_isa", "ptx_target", "address_size",
        "wrapper_numeric_policy", "leaf_numeric_policy", "composer_schema",
        "compile_options", "link_options", "composed_leaf_bindings",
        "provider_key_sha256",
    }, "product_projection.provider_key")
    if provider["schema"] != "rtdl.v4.rtdlexe.provider_key.v1":
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key.schema", provider["schema"])
    body = dict(provider); seal = body.pop("provider_key_sha256")
    if _require_sha(seal, "provider_key.provider_key_sha256") != _digest(body):
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key.provider_key_sha256", seal)
    abi = _require_exact_keys(provider["callback_abi_projection"], {
        "schema_id", "schema_version", "callback_ir_sha256", "callback_effect_digest",
        "any_hit_proof_sha256", "any_hit_proof_kind", "any_hit_delivery_contract",
        "runtime_status_codes", "roles", "abi_sha256",
    }, "provider_key.callback_abi_projection")
    abi_body = dict(abi); abi_seal = abi_body.pop("abi_sha256")
    if _require_sha(abi_seal, "provider_key.callback_abi_projection.abi_sha256") != _digest(abi_body) \
            or abi_seal != provider["callback_abi_sha256"] \
            or abi["callback_ir_sha256"] != provider["callback_ir_sha256"]:
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key.callback_abi_projection", "ABI chain drift")
    roles = abi["roles"]
    if not isinstance(roles, list) or not roles \
            or any(not isinstance(row, Mapping) or not isinstance(row.get("role"), str) for row in roles):
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key.callback_abi_projection.roles", roles)
    expected_roles = [row["role"] for row in roles]
    for key in ("generated_source_sha256_by_role", "leaf_ptx_sha256_by_role"):
        rows = provider[key]
        if not isinstance(rows, list) or len(rows) != len(expected_roles) \
                or any(not isinstance(row, list) or len(row) != 2 for row in rows) \
                or [row[0] for row in rows] != expected_roles:
            _fail("RX051_PROVIDER_KEY_INVALID", f"provider_key.{key}", rows)
        for index, row in enumerate(rows):
            _require_sha(row[1], f"provider_key.{key}[{index}][1]")
    sbt = _require_exact_keys(provider["sbt_layout_projection"], {
        "schema", "evidence_kind", "raygen_records", "miss_records",
        "hitgroup_records", "hitgroup_program_roles", "trace_depth",
        "callback_abi_sha256", "physical_template",
    }, "provider_key.sbt_layout_projection")
    if provider["sbt_layout_sha256"] != _digest(sbt) \
            or sbt["callback_abi_sha256"] != abi_seal \
            or sbt["physical_template"] != provider["physical_template"]:
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key.sbt_layout_projection", "SBT chain drift")
    for key in (
        "callback_ir_sha256", "callback_abi_sha256", "wrapper_source_sha256",
        "payload_layout_sha256", "attribute_layout_sha256", "sbt_layout_sha256",
        "native_provider_sha256",
    ):
        _require_sha(provider[key], f"provider_key.{key}")
    for key in ("compile_options", "link_options", "composed_leaf_bindings",
                "wrapper_role_symbols", "target_compute_capability"):
        if not isinstance(provider[key], list):
            _fail("RX051_PROVIDER_KEY_INVALID", f"provider_key.{key}", provider[key])
    return provider


def _verify_execution_schema(value: object) -> Mapping[str, object]:
    execution = _require_exact_keys(value, {
        "schema", "evidence_kind", "actual_runtime_handle_bytes_bound",
        "actual_runtime_handle_bytes_unavailable_reason", "native_program_bundle",
        "native_producer_descriptor", "native_producer_descriptor_sha256",
        "module_schema_sha256", "program_group_schema_sha256",
        "pipeline_schema_sha256", "sbt_schema_sha256",
        "launch_parameter_schema_sha256", "status_schema_sha256",
        "producer_inputs", "execution_schema_sha256",
    }, "product_projection.execution_schema")
    body = dict(execution); seal = body.pop("execution_schema_sha256")
    if execution["schema"] != "rtdl.v4.rtdlexe.execution_schema_projection.v1" \
            or execution["evidence_kind"] != \
                "native_exported_producer_descriptor_plus_compiler_identity" \
            or execution["actual_runtime_handle_bytes_bound"] is not False \
            or _require_sha(seal, "execution_schema.execution_schema_sha256") != _digest(body):
        _fail("RX052_EXECUTION_SCHEMA_INVALID", "execution_schema", "schema/seal drift")
    inputs = _require_exact_keys(execution["producer_inputs"], {
        "module", "program_group", "pipeline", "sbt", "launch_parameters", "status",
    }, "execution_schema.producer_inputs")
    digest_keys = {
        "module": "module_schema_sha256",
        "program_group": "program_group_schema_sha256",
        "pipeline": "pipeline_schema_sha256", "sbt": "sbt_schema_sha256",
        "launch_parameters": "launch_parameter_schema_sha256",
        "status": "status_schema_sha256",
    }
    for name, digest_key in digest_keys.items():
        if not isinstance(inputs[name], Mapping) or execution[digest_key] != _digest(inputs[name]):
            _fail("RX052_EXECUTION_SCHEMA_INVALID", f"execution_schema.producer_inputs.{name}", "digest drift")
    descriptor = execution["native_producer_descriptor"]
    if not isinstance(descriptor, Mapping) \
            or _require_sha(execution["native_producer_descriptor_sha256"],
                            "execution_schema.native_producer_descriptor_sha256") != \
                _digest(descriptor):
        _fail("RX052_EXECUTION_SCHEMA_INVALID", "execution_schema.native_producer_descriptor",
              "native descriptor digest drift")
    return execution


_LOADED_EXECUTABLE_CAPABILITY_TOKEN = object()


class _LoadedRuntimeSessionAdmissionCapsule(tuple):
    """Immutable loader-issued identity snapshot for session reuse.

    ``LoadedRTDLExecutable`` recursively freezes ``product_projection`` in
    ``__post_init__``.  Consequently, retaining the exact projection object
    and the exact immutable top-level field objects is sufficient to bind the
    complete checked loader result: no nested value can change without first
    replacing a captured top-level field.  The owner weak reference prevents
    a capsule copied by ``dataclasses.replace`` or ``object.__setattr__`` from
    admitting a different loaded object.

    A tuple subclass is used deliberately.  Its payload has no instance
    dictionary and cannot itself be rewritten through ``object.__setattr__``.
    Equality and hashing are identity-based so the capsule is also an O(1),
    exact-object descriptor-admission cache key.
    """

    __slots__ = ()
    _FIELD_NAMES = (
        "artifact_path", "authority_path", "authority_sha256",
        "deployment_id", "trust_root_sha256", "trust_package_sha256",
        "artifact_sha256", "executable_identity_sha256", "family",
        "composed_ptx", "product_projection",
        "family_executable_identity_sha256",
    )

    def __new__(
        cls, issuer_token: object, value: "LoadedRTDLExecutable",
    ) -> "_LoadedRuntimeSessionAdmissionCapsule":
        if issuer_token is not _LOADED_EXECUTABLE_CAPABILITY_TOKEN:
            raise TypeError("loader-issued admission capsule required")
        return tuple.__new__(cls, (
            weakref.ref(value),
            *(getattr(value, name) for name in cls._FIELD_NAMES),
        ))

    __hash__ = object.__hash__
    __eq__ = object.__eq__

    def admits(self, value: object) -> bool:
        if self[0]() is not value:
            return False
        return all(
            getattr(value, name, None) is expected
            for name, expected in zip(self._FIELD_NAMES, self[1:])
        )


def _loaded_runtime_session_snapshot_seal(
    value: "LoadedRTDLExecutable",
) -> _LoadedRuntimeSessionAdmissionCapsule:
    """Issue the legacy-named, constant-time admission capsule once.

    The name is retained for diagnostic compatibility.  Unlike the former
    implementation, this function performs no canonicalization or hashing and
    is never called by capability revalidation.
    """

    return _LoadedRuntimeSessionAdmissionCapsule(
        _LOADED_EXECUTABLE_CAPABILITY_TOKEN, value)


def _issue_loaded_runtime_session_capability(
    value: "LoadedRTDLExecutable",
) -> "LoadedRTDLExecutable":
    """Mark one already validated immutable loader result for session reuse."""

    if getattr(value, "_token", None) is not None \
            or getattr(value, "_runtime_session_snapshot_seal", None) is not None:
        _fail(
            "RX056_LOADED_CAPABILITY_INVALID", "runtime_session.loaded",
            "loaded capability was already issued")
    object.__setattr__(value, "_token", _LOADED_EXECUTABLE_CAPABILITY_TOKEN)
    object.__setattr__(
        value, "_runtime_session_snapshot_seal",
        _loaded_runtime_session_snapshot_seal(value))
    return value


def _require_runtime_session_loaded_capability(
    value: object, *, identity_path: str,
) -> None:
    capsule = getattr(value, "_runtime_session_snapshot_seal", None)
    if not isinstance(value, LoadedRTDLExecutable) \
            or getattr(value, "_token", None) is not \
                _LOADED_EXECUTABLE_CAPABILITY_TOKEN \
            or not isinstance(
                capsule, _LoadedRuntimeSessionAdmissionCapsule) \
            or not capsule.admits(value):
        _fail(
            "RX056_LOADED_CAPABILITY_INVALID", identity_path,
            "runtime-session reuse requires load_rtdlexe output")


@dataclass(frozen=True)
class LoadedRTDLExecutable:
    artifact_path: Path
    authority_path: Path
    authority_sha256: str
    deployment_id: str
    trust_root_sha256: str
    trust_package_sha256: str
    artifact_sha256: str
    executable_identity_sha256: str
    family: str
    composed_ptx: str
    product_projection: Mapping[str, object]
    family_executable_identity_sha256: str | None = None
    _token: object = field(default=None, repr=False, compare=False)
    _runtime_session_snapshot_seal: \
        _LoadedRuntimeSessionAdmissionCapsule | None = field(
        default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        # ``LoadedRTDLExecutable`` is public and frozen only at the dataclass
        # field level.  Snapshot the complete checked projection even for
        # direct construction so a caller cannot mutate a nested mapping
        # between runtime-session identity admission, descriptor validation,
        # and native owner construction.  ``load_rtdlexe`` deliberately relies
        # on this single freeze as well, avoiding a redundant second traversal
        # while keeping the public-constructor TOCTOU boundary closed.
        object.__setattr__(
            self, "product_projection", _deep_freeze(self.product_projection))

    def _native_admission_parameters(self) -> tuple[str, tuple[int, int]]:
        target = self.product_projection["target_toolchain"]
        assert isinstance(target, Mapping)
        return (
            _require_sha(
                target["native_library_sha256"],
                "target.native_library_sha256"),
            tuple(target["compute_capability"]),
        )

    def _validate_native_provider_descriptor(
        self, library: object, *, identity_path: str,
    ) -> None:
        runtime = self.product_projection["runtime"]
        assert isinstance(runtime, Mapping)
        execution_schema = self.product_projection["execution_schema"]
        assert isinstance(execution_schema, Mapping)
        expected_descriptor = execution_schema["native_producer_descriptor"]
        assert isinstance(expected_descriptor, Mapping)
        bundle = ("v4_custom_aabb_bounded_relation_composed"
                  if self.family == _BOUNDED
                  else "v4_builtin_triangle_checked_reduction_composed")
        actual_descriptor = _query_native_producer_descriptor(
            library, family=self.family, native_abi=str(runtime["native_abi"]),
            program_bundle=bundle)
        if _canonical(actual_descriptor) != _canonical(_plain(expected_descriptor)):
            _fail("RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH", identity_path, {
                "expected": _digest(_plain(expected_descriptor)),
                "actual": _digest(actual_descriptor),
            })

    def _build_prepared_owner(
        self,
        static_input: BoundedRelationStaticInput | BoundedRelationBufferStaticInput |
            TriangleReductionStaticInput | TriangleReductionBufferStaticInput,
        *,
        library: object,
        native_source_path: Path,
        owner_handoff: _PreparedOwnerHandoff | None = None,
    ) -> object:
        runtime = self.product_projection["runtime"]
        assert isinstance(runtime, Mapping)
        if self.family == _BOUNDED:
            if not isinstance(static_input, (
                    BoundedRelationStaticInput,
                    BoundedRelationBufferStaticInput)):
                _fail(
                    "RX016_STATIC_INPUT_MISMATCH", "static_input",
                    type(static_input).__name__)
            return _PreparedBoundedOwner(
                library=library, native_path=native_source_path,
                ptx=self.composed_ptx, runtime=runtime,
                static_input=static_input,
                artifact_identity=self.executable_identity_sha256,
                construction_handoff=owner_handoff,
            )
        if not isinstance(static_input, (
                TriangleReductionStaticInput,
                TriangleReductionBufferStaticInput)):
            _fail(
                "RX016_STATIC_INPUT_MISMATCH", "static_input",
                type(static_input).__name__)
        return _PreparedTriangleOwner(
            library=library, native_path=native_source_path,
            ptx=self.composed_ptx, runtime=runtime,
            static_input=static_input,
            artifact_identity=self.executable_identity_sha256,
            construction_handoff=owner_handoff,
        )

    def prepare(
        self,
        static_input: BoundedRelationStaticInput | BoundedRelationBufferStaticInput |
            TriangleReductionStaticInput | TriangleReductionBufferStaticInput,
        *,
        native_library_path: str | os.PathLike[str],
    ) -> "PreparedRTDLExecutable":
        path = _absolute_unresolved_path(native_library_path)
        expected_native, expected_compute_capability = (
            self._native_admission_parameters())
        library = _load_native_library(
            path,
            expected_sha256=expected_native,
            expected_compute_capability=expected_compute_capability,
        )
        owner_handoff = _PreparedOwnerHandoff()
        owner = None
        try:
            self._validate_native_provider_descriptor(
                library, identity_path="prepare.native_producer_descriptor")
            owner = self._build_prepared_owner(
                static_input, library=library, native_source_path=path,
                owner_handoff=owner_handoff)
            return PreparedRTDLExecutable(
                family=self.family,
                executable_identity_sha256=self.executable_identity_sha256,
                owner=owner,
            )
        except BaseException:
            admitted_owner = (
                owner if owner is not None else owner_handoff.owner)
            if admitted_owner is not None:
                admitted_owner.close()
            else:
                _release_native_library_image(library)
            raise

    def bind_provider(
        self, native_library_path: str | os.PathLike[str],
    ) -> "ProviderReadyRTDLExecutable":
        """Verify and bind one exact native provider for repeated prepare.

        Binding performs the same path, SHA-256, compute-capability, and native
        producer-descriptor admission as raw :meth:`prepare`.  The returned
        capability subsequently admits only the exact sealed cache entry and
        never reopens the mutable source pathname.
        """

        path = _absolute_unresolved_path(native_library_path)
        expected_native, expected_compute_capability = (
            self._native_admission_parameters())
        readiness = _acquire_cuda_primary_context_readiness(
            expected_compute_capability=expected_compute_capability)
        library = None
        lease_handoff = _NativeImageLeaseHandoff()
        try:
            library = _load_verified_native_file_descriptor(
                path, expected_sha256=expected_native,
                code="RX032_NATIVE_IDENTITY_MISMATCH",
                identity_path="native_library_path",
                lease_handoff=lease_handoff)
            # Test doubles predating the handoff parameter can return a lease
            # without publishing it.  Real admission publishes before return.
            lease_handoff.publish(library)
            self._validate_native_provider_descriptor(
                library,
                identity_path="bind_provider.native_producer_descriptor")
            return ProviderReadyRTDLExecutable(
                loaded=self, binding_library=library,
                bind_source_path=path, cuda_readiness=readiness)
        except BaseException:
            admitted_library = (
                library if isinstance(library, _NativeLibraryLease)
                else lease_handoff.lease)
            if admitted_library is not None:
                try:
                    _release_native_library_image(admitted_library)
                finally:
                    readiness.close()
            else:
                readiness.close()
            raise

    def open_runtime_session(
        self, native_library_path: str | os.PathLike[str],
    ) -> "RTDLRuntimeSession":
        """Admit one process provider for this and later executables.

        The first executable supplies the exact native-image and compute-
        capability identity.  A session may then prepare other loaded
        executables only when they name that same provider identity; each
        executable's native producer descriptor is still checked before its
        first owner is constructed.  The mutable provider pathname is opened
        only by the initial :meth:`bind_provider` call.
        """

        _require_runtime_session_loaded_capability(
            self, identity_path="runtime_session.seed")
        expected_native, expected_compute_capability = (
            self._native_admission_parameters())
        provider = self.bind_provider(native_library_path)
        try:
            return RTDLRuntimeSession(
                provider=provider,
                expected_native_sha256=expected_native,
                expected_compute_capability=expected_compute_capability,
            )
        except BaseException:
            provider.close()
            raise


_INITIALIZING_PROVIDER_CAPABILITY_TOKEN = object()


class InitializingRTDLProvider:
    """One-shot overlap capability for signed provider admission.

    Provider hashing/loading and CUDA/OptiX initialization may overlap the
    independent artifact/authority verification in :func:`load_rtdlexe`.
    This object never consumes artifact-controlled native identity and cannot
    construct an owner.  ``bind`` is the only transfer point and rechecks the
    complete loaded/deployment identity before issuing a provider capability.
    """

    __slots__ = (
        "_deployment", "_native_path", "_expected_native",
        "_expected_compute_capability", "_pid", "_state", "_error",
        "_library", "_readiness", "_timings_ns", "_lock", "_active",
        "_thread",
    )

    def __init__(
        self, *, deployment: InstalledRTDLDeployment,
        native_library_path: str | os.PathLike[str], _token: object,
    ) -> None:
        if _token is not _INITIALIZING_PROVIDER_CAPABILITY_TOKEN \
                or not isinstance(deployment, InstalledRTDLDeployment) \
                or getattr(deployment, "_token", None) is not \
                    _DEPLOYMENT_CAPABILITY_TOKEN:
            _fail(
                "RX057_PROVIDER_INITIALIZATION_INVALID", "initializing_provider",
                "use InstalledRTDLDeployment.begin_provider_initialization")
        self._deployment = deployment
        self._native_path = _absolute_unresolved_path(native_library_path)
        self._expected_native = _require_sha(
            deployment.entry["native_library_sha256"],
            "deployment.entry.native_library_sha256")
        self._expected_compute_capability = tuple(
            deployment.entry["compute_capability"])
        self._pid = os.getpid()
        self._state = "INITIALIZING"
        self._error: BaseException | None = None
        self._library: _NativeLibraryLease | None = None
        self._readiness: _CudaPrimaryContextReadinessLease | None = None
        self._timings_ns: dict[str, int] = {}
        self._lock = threading.Lock()
        self._active = threading.Lock()
        self._thread = threading.Thread(
            target=self._initialize,
            name="rtdl-provider-initialization",
            daemon=True,
        )
        self._thread.start()

    def _check_pid(self) -> None:
        if os.getpid() != self._pid:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "initializing_provider",
                "provider initialization belongs to a different process")

    def _initialize(self) -> None:
        total_started = time.perf_counter_ns()
        readiness = None
        library = None
        lease_handoff = _NativeImageLeaseHandoff()
        timings: dict[str, int] = {}
        try:
            phase_started = time.perf_counter_ns()
            readiness = _acquire_cuda_primary_context_readiness(
                expected_compute_capability=(
                    self._expected_compute_capability))
            timings["cuda_primary_context"] = (
                time.perf_counter_ns() - phase_started)

            phase_started = time.perf_counter_ns()
            library = _load_verified_native_file_descriptor(
                self._native_path,
                expected_sha256=self._expected_native,
                code="RX032_NATIVE_IDENTITY_MISMATCH",
                identity_path="native_library_path",
                lease_handoff=lease_handoff,
            )
            lease_handoff.publish(library)
            timings["sealed_native_image"] = (
                time.perf_counter_ns() - phase_started)

            phase_started = time.perf_counter_ns()
            _warm_native_provider_runtime(library)
            timings["native_runtime_warm"] = (
                time.perf_counter_ns() - phase_started)
            timings["total"] = time.perf_counter_ns() - total_started
            with self._lock:
                self._readiness = readiness
                self._library = library
                self._timings_ns = timings
                self._state = "READY"
            readiness = None
            library = None
        except BaseException as error:
            admitted_library = (
                library if isinstance(library, _NativeLibraryLease)
                else lease_handoff.lease)
            cleanup_error = None
            try:
                if admitted_library is not None:
                    _release_native_library_image(admitted_library)
            except BaseException as observed:
                cleanup_error = observed
            try:
                if readiness is not None:
                    readiness.close()
            except BaseException as observed:
                cleanup_error = cleanup_error or observed
            if cleanup_error is not None:
                error.add_note(
                    "provider initialization cleanup also failed: " +
                    repr(cleanup_error))
            timings["total"] = time.perf_counter_ns() - total_started
            with self._lock:
                self._error = error
                self._timings_ns = timings
                self._state = "FAILED"

    @property
    def state(self) -> str:
        self._check_pid()
        with self._lock:
            return self._state

    @property
    def phase_timings_ns(self) -> Mapping[str, int]:
        """Return completed phase timings without granting runtime authority."""

        self._check_pid()
        with self._lock:
            return MappingProxyType(dict(self._timings_ns))

    def bind(
        self, loaded: LoadedRTDLExecutable,
    ) -> "ProviderReadyRTDLExecutable":
        """Wait for initialization and bind the exact loaded slot once."""

        self._check_pid()
        if not self._active.acquire(blocking=False):
            _fail(
                "RX040_REENTRANT", "initializing_provider.bind", "already active")
        library = None
        readiness = None
        try:
            self._thread.join()
            self._check_pid()
            with self._lock:
                if self._state == "FAILED":
                    assert self._error is not None
                    self._state = "CLOSED"
                    raise self._error
                if self._state != "READY":
                    _fail(
                        "RX057_PROVIDER_INITIALIZATION_INVALID",
                        "initializing_provider.bind", self._state)
                library = self._library
                readiness = self._readiness
                self._state = "BINDING"
            if not isinstance(library, _NativeLibraryLease) \
                    or not isinstance(
                        readiness, _CudaPrimaryContextReadinessLease):
                _fail(
                    "RX057_PROVIDER_INITIALIZATION_INVALID",
                    "initializing_provider.bind", "ready resources absent")
            _require_runtime_session_loaded_capability(
                loaded, identity_path="initializing_provider.loaded")
            expected_native, expected_compute = (
                loaded._native_admission_parameters())
            entry = self._deployment.entry
            if loaded.deployment_id != self._deployment.deployment_id \
                    or loaded.trust_root_sha256 != \
                        self._deployment.trust_root_sha256 \
                    or loaded.trust_package_sha256 != \
                        self._deployment.trust_package_sha256 \
                    or loaded.authority_sha256 != entry["authority_sha256"] \
                    or loaded.artifact_sha256 != entry["artifact_sha256"] \
                    or loaded.executable_identity_sha256 != \
                        entry["executable_identity_sha256"] \
                    or loaded.family != entry["family"] \
                    or expected_native != self._expected_native \
                    or not hmac.compare_digest(
                        expected_native, entry["native_library_sha256"]) \
                    or tuple(expected_compute) != \
                        self._expected_compute_capability:
                _fail(
                    "RX050_DEPLOYMENT_INTENT_MISMATCH",
                    "initializing_provider.loaded", "slot identity differs")
            loaded._validate_native_provider_descriptor(
                library,
                identity_path=(
                    "initializing_provider.native_producer_descriptor"))
            provider = ProviderReadyRTDLExecutable(
                loaded=loaded,
                binding_library=library,
                bind_source_path=self._native_path,
                cuda_readiness=readiness,
            )
            with self._lock:
                self._library = None
                self._readiness = None
                self._state = "BOUND"
            library = None
            readiness = None
            return provider
        except BaseException:
            if library is not None:
                try:
                    _release_native_library_image(library)
                finally:
                    if readiness is not None:
                        readiness.close()
            elif readiness is not None:
                readiness.close()
            with self._lock:
                self._library = None
                self._readiness = None
                if self._state not in {"BOUND", "CLOSED"}:
                    self._state = "CLOSED"
            raise
        finally:
            self._active.release()

    def close(self) -> None:
        """Wait for in-flight admission and release an unbound capability."""

        self._check_pid()
        if not self._active.acquire(blocking=False):
            _fail(
                "RX040_REENTRANT", "initializing_provider.close", "already active")
        try:
            self._thread.join()
            self._check_pid()
            with self._lock:
                if self._state in {"BOUND", "CLOSED"}:
                    return
                library = self._library
                readiness = self._readiness
                self._library = None
                self._readiness = None
                self._state = "CLOSED"
            if library is not None:
                try:
                    _release_native_library_image(library)
                finally:
                    if readiness is not None:
                        readiness.close()
            elif readiness is not None:
                readiness.close()
        finally:
            self._active.release()

    def __enter__(self) -> "InitializingRTDLProvider":
        self._check_pid()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def __del__(self) -> None:
        # A caller can lose the returned capability at the CALL/STORE boundary.
        # The worker temporarily owns ``self`` through its bound target, so the
        # last reference may disappear on that same worker immediately after
        # initialization.  Avoid joining the current thread and release the
        # unpublished lease directly; every failure is deliberately suppressed
        # because destructors cannot report a retryable error to a caller.
        try:
            if not hasattr(self, "_thread"):
                return
            if threading.current_thread() is self._thread:
                with self._lock:
                    if self._state != "READY":
                        return
                    library = self._library
                    readiness = self._readiness
                    self._library = None
                    self._readiness = None
                    self._state = "CLOSED"
                if library is not None:
                    try:
                        _release_native_library_image(library)
                    finally:
                        if readiness is not None:
                            readiness.close()
                elif readiness is not None:
                    readiness.close()
            else:
                self.close()
        except BaseException:
            pass


def begin_rtdlexe_provider_initialization(
    *, deployment: InstalledRTDLDeployment,
    native_library_path: str | os.PathLike[str],
) -> InitializingRTDLProvider:
    """Public function form of deployment provider initialization."""

    if not isinstance(deployment, InstalledRTDLDeployment):
        _fail(
            "RX057_PROVIDER_INITIALIZATION_INVALID", "deployment",
            type(deployment).__name__)
    return deployment.begin_provider_initialization(native_library_path)


class ProviderReadyRTDLExecutable:
    """PID-bound capability for one already verified sealed native provider."""

    __slots__ = (
        "_loaded", "_binding_library", "_binding", "_pid", "_closed",
        "_close_failure", "_active", "_cuda_readiness",
        "_binding_released", "_closing",
        "_seed_descriptor_admission_seal",
    )

    def __init__(
        self, *, loaded: LoadedRTDLExecutable,
        binding_library: _NativeLibraryLease, bind_source_path: Path,
        cuda_readiness: _CudaPrimaryContextReadinessLease,
    ) -> None:
        self._loaded = loaded
        # ``LoadedRTDLExecutable.bind_provider`` validates this exact loaded
        # snapshot's producer descriptor immediately before constructing the
        # provider capability.  Capture the snapshot seal here so a runtime
        # session may reuse that completed check, while a substituted loaded
        # executable (even another valid loader result) cannot inherit it.
        self._seed_descriptor_admission_seal = (
            loaded._runtime_session_snapshot_seal)
        self._binding_library = binding_library
        self._binding = _capture_provider_ready_native_binding(
            binding_library, source_path=bind_source_path)
        self._cuda_readiness = cuda_readiness
        self._pid = self._binding.owner_pid
        if cuda_readiness.owner_pid != self._pid:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                "native and CUDA readiness capabilities have different owners")
        self._closed = False
        self._close_failure = None
        self._active = threading.RLock()
        self._binding_released = False
        self._closing = False

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def native_library_path(self) -> Path:
        """Bind-time source spelling; it is never recomputed from later state."""

        return self._binding.source_path

    @property
    def native_library_sha256(self) -> str:
        return self._binding.digest

    @property
    def cache_entry_identity(self) -> str:
        return self._binding.cache_entry_identity

    @property
    def owner_pid(self) -> int:
        return self._binding.owner_pid

    @property
    def runtime_compiler_attempt_count(self) -> int:
        """Return the exact bound provider's app-free compiler-attempt counter."""

        self._check_owner_pid_without_lock()
        with self._active:
            self._check()
            counter = getattr(
                self._binding_library,
                "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
                None,
            )
            if counter is None:
                _fail(
                    "RX036_NATIVE_ABI_MISSING",
                    "native.runtime_compiler_attempt_count",
                    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
                )
            counter.argtypes = []
            counter.restype = ctypes.c_uint64
            return int(counter())

    def _check(self) -> None:
        if self._closed or self._closing:
            _fail(
                "RX037_USE_AFTER_CLOSE", "provider_ready",
                "closed" if self._closed else "close incomplete")
        if os.getpid() != self._pid:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready",
                "provider capability belongs to a different process")
        self._cuda_readiness.check()

    def _check_owner_pid_without_lock(self) -> None:
        """Reject an inherited capability before touching its inherited lock."""

        if os.getpid() != self._pid:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready",
                "provider capability belongs to a different process")

    def prepare(
        self,
        static_input: BoundedRelationStaticInput | BoundedRelationBufferStaticInput |
            TriangleReductionStaticInput | TriangleReductionBufferStaticInput,
    ) -> "PreparedRTDLExecutable":
        return self._prepare_loaded(
            self._loaded, static_input, validate_native_descriptor=False)

    def _prepare_loaded(
        self,
        loaded: LoadedRTDLExecutable,
        static_input: BoundedRelationStaticInput | BoundedRelationBufferStaticInput |
            TriangleReductionStaticInput | TriangleReductionBufferStaticInput,
        *,
        validate_native_descriptor: bool,
        descriptor_admission_seals: set[
            _LoadedRuntimeSessionAdmissionCapsule] | None = None,
    ) -> "PreparedRTDLExecutable":
        """Construct an owner from this exact provider without path admission."""

        # A thread other than the forking thread may have held ``_active`` at
        # fork.  The child must reject the inherited capability before trying
        # to acquire that permanently orphaned lock, then repeat the check
        # under the lock to close a test-induced PID-drift race.
        self._check_owner_pid_without_lock()
        with self._active:
            self._check()
            if validate_native_descriptor:
                if descriptor_admission_seals is None:
                    _fail(
                        "RX056_LOADED_CAPABILITY_INVALID",
                        "runtime_session.native_producer_descriptor",
                        "session-local descriptor admission cache is absent")
                admission_seal = loaded._runtime_session_snapshot_seal
                if not isinstance(
                        admission_seal,
                        _LoadedRuntimeSessionAdmissionCapsule):
                    _fail(
                        "RX056_LOADED_CAPABILITY_INVALID",
                        "runtime_session.native_producer_descriptor",
                        "loaded executable admission capsule is absent")
                if admission_seal not in descriptor_admission_seals:
                    loaded._validate_native_provider_descriptor(
                        self._binding_library,
                        identity_path=(
                            "runtime_session.native_producer_descriptor"))
                    # Publish only after the exact immutable producer
                    # descriptor has matched.  ``_active`` serializes this
                    # check and publication with concurrent prepare calls, so
                    # a session pays one descriptor FFI per executable while
                    # no later-executable admission transfers into another
                    # session-local cache.
                    descriptor_admission_seals.add(admission_seal)
            lease_handoff = _NativeImageLeaseHandoff()
            owner_handoff = _PreparedOwnerHandoff()
            library = None
            owner = None
            try:
                library = _admit_provider_ready_native_image_lease(
                    self._binding, binding_library=self._binding_library,
                    lease_handoff=lease_handoff)
                lease_handoff.publish(library)
                # Keep the provider lifecycle lock through native owner
                # construction.  close() must not release the readiness retain
                # while the DSO initializes its process singleton.
                owner = loaded._build_prepared_owner(
                    static_input, library=library,
                    native_source_path=self._binding.source_path,
                    owner_handoff=owner_handoff)
                prepared = PreparedRTDLExecutable(
                    family=loaded.family,
                    executable_identity_sha256=(
                        loaded.executable_identity_sha256),
                    owner=owner,
                )
                return prepared
            except BaseException:
                admitted_owner = (
                    owner if owner is not None else owner_handoff.owner)
                if admitted_owner is not None:
                    admitted_owner.close()
                else:
                    admitted_library = (
                        library if isinstance(library, _NativeLibraryLease)
                        else lease_handoff.lease)
                    if admitted_library is not None:
                        _release_native_library_image(admitted_library)
                raise

    def close(self) -> None:
        self._check_owner_pid_without_lock()
        with self._active:
            if self._closed:
                return
            if os.getpid() != self._pid:
                _fail(
                    "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready",
                    "provider capability belongs to a different process")
            if not self._closing:
                self._check()
                self._closing = True
            try:
                if not self._binding_released:
                    _release_native_library_image(self._binding_library)
                    self._binding_released = True
                self._cuda_readiness.close()
                self._closed = True
                self._closing = False
                self._close_failure = None
                self._binding_library = None
                self._cuda_readiness = None
            except BaseException as error:
                self._close_failure = repr(error)
                raise

    def __enter__(self) -> "ProviderReadyRTDLExecutable":
        self._check_owner_pid_without_lock()
        with self._active:
            self._check()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def _abandon_runtime_session(
    provider: ProviderReadyRTDLExecutable, owner_pid: int,
) -> None:
    """Close a session capability lost across the public CALL/STORE boundary."""

    # A finalizer inherited by a fork child must not touch the parent's CUDA,
    # DSO, lock, or lease state.  Normal explicit close remains the observable,
    # retryable path; this callback is only the abandonment safety net.
    if os.getpid() != owner_pid:
        return
    try:
        provider.close()
    except BaseException:
        # Finalizers cannot return an error to a caller.  Provider close keeps
        # its phase markers retryable for any surviving owner reference.
        pass


class RTDLRuntimeSession:
    """Process-scoped exact-provider capability shared by many executables.

    Opening the session performs the expensive CUDA-primary and sealed-native
    admission exactly once.  ``prepare`` never reopens the provider pathname;
    it accepts a loaded executable only when its frozen native SHA-256 and
    compute capability match the session and its family-specific producer
    descriptor matches the already admitted DSO.  The seed executable reuses
    the descriptor check completed by ``bind_provider`` for that exact loaded
    snapshot; every other executable is checked once on first use in this
    session.

    Construct sessions through :meth:`LoadedRTDLExecutable.open_runtime_session`.
    """

    __slots__ = (
        "_provider", "_expected_native_sha256",
        "_expected_compute_capability", "_descriptor_admission_seals",
        "_abandon_finalizer", "__weakref__",
    )

    def __init__(
        self, *, provider: ProviderReadyRTDLExecutable,
        expected_native_sha256: str,
        expected_compute_capability: tuple[int, int],
    ) -> None:
        if not isinstance(provider, ProviderReadyRTDLExecutable):
            _fail(
                "RX006_INPUT_INVALID", "runtime_session.provider",
                type(provider).__name__)
        exact_native = _require_sha(
            expected_native_sha256,
            "runtime_session.native_library_sha256")
        exact_capability = tuple(expected_compute_capability)
        provider._check_owner_pid_without_lock()
        with provider._active:
            provider._check()
            _require_runtime_session_loaded_capability(
                provider._loaded, identity_path="runtime_session.seed")
            seed_admission_seal = (
                provider._loaded._runtime_session_snapshot_seal)
            if not isinstance(
                    seed_admission_seal,
                    _LoadedRuntimeSessionAdmissionCapsule) \
                    or not isinstance(
                        provider._seed_descriptor_admission_seal,
                        _LoadedRuntimeSessionAdmissionCapsule) \
                    or seed_admission_seal is not \
                        provider._seed_descriptor_admission_seal:
                _fail(
                    "RX056_LOADED_CAPABILITY_INVALID",
                    "runtime_session.seed.native_producer_descriptor",
                    "provider seed differs from bind-time validated snapshot")
            seed_native, seed_capability = (
                provider._loaded._native_admission_parameters())
            if not hmac.compare_digest(
                    seed_native, provider.native_library_sha256) \
                    or not hmac.compare_digest(seed_native, exact_native):
                _fail(
                    "RX032_NATIVE_IDENTITY_MISMATCH",
                    "runtime_session.provider.native_library_sha256", {
                        "seed": seed_native,
                        "provider": provider.native_library_sha256,
                        "requested": exact_native,
                    })
            if tuple(seed_capability) != exact_capability:
                _fail(
                    "RX033_DEVICE_SUBSTITUTION",
                    "runtime_session.provider.compute_capability", {
                        "seed": tuple(seed_capability),
                        "requested": exact_capability,
                    })
        self._provider = provider
        self._expected_native_sha256 = exact_native
        self._expected_compute_capability = exact_capability
        # This cache is deliberately session-local.  The seed seal is safe to
        # prepopulate because bind_provider already checked that exact
        # snapshot against the same immutable DSO, and the equality guard
        # above rejects provider._loaded substitution.  Every other exact
        # executable remains unadmitted until its first prepare in this
        # session.
        self._descriptor_admission_seals: set[
            _LoadedRuntimeSessionAdmissionCapsule] = {
            seed_admission_seal}
        self._abandon_finalizer = weakref.finalize(
            self, _abandon_runtime_session, provider, provider.owner_pid)

    @property
    def closed(self) -> bool:
        return self._provider.closed

    @property
    def native_library_path(self) -> Path:
        return self._provider.native_library_path

    @property
    def native_library_sha256(self) -> str:
        return self._provider.native_library_sha256

    @property
    def cache_entry_identity(self) -> str:
        return self._provider.cache_entry_identity

    @property
    def owner_pid(self) -> int:
        return self._provider.owner_pid

    def prepare(
        self,
        loaded: LoadedRTDLExecutable,
        static_input: BoundedRelationStaticInput | BoundedRelationBufferStaticInput |
            TriangleReductionStaticInput | TriangleReductionBufferStaticInput,
    ) -> "PreparedRTDLExecutable":
        if not isinstance(loaded, LoadedRTDLExecutable):
            _fail(
                "RX006_INPUT_INVALID", "runtime_session.loaded",
                type(loaded).__name__)
        _require_runtime_session_loaded_capability(
            loaded, identity_path="runtime_session.loaded")
        expected_native, expected_compute_capability = (
            loaded._native_admission_parameters())
        if not hmac.compare_digest(
                expected_native, self._expected_native_sha256):
            _fail(
                "RX032_NATIVE_IDENTITY_MISMATCH",
                "runtime_session.loaded.target.native_library_sha256",
                expected_native)
        if tuple(expected_compute_capability) != \
                self._expected_compute_capability:
            _fail(
                "RX033_DEVICE_SUBSTITUTION",
                "runtime_session.loaded.target.compute_capability",
                tuple(expected_compute_capability))
        return self._provider._prepare_loaded(
            loaded, static_input, validate_native_descriptor=True,
            descriptor_admission_seals=self._descriptor_admission_seals)

    def close(self) -> None:
        self._provider.close()
        # Detach only after provider.close succeeds.  If close is interrupted,
        # the explicit caller may retry and an abandoned session retains its
        # final cleanup path.
        self._abandon_finalizer.detach()

    def __enter__(self) -> "RTDLRuntimeSession":
        self._provider.__enter__()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def load_rtdlexe(
    artifact_path: str | os.PathLike[str],
    *,
    authority_path: str | os.PathLike[str],
    deployment: InstalledRTDLDeployment,
) -> LoadedRTDLExecutable:
    """Load only the authority frozen for an installed deployment slot.

    There is deliberately no ``expected_authority_sha256`` parameter.  A
    request cannot authorize a coherent forgery by supplying the forgery's
    newly computed digest, key, package, family, task semantics, or slot id.
    """

    artifact_file = _absolute_unresolved_path(artifact_path)
    authority_file = _absolute_unresolved_path(authority_path)
    if not isinstance(deployment, InstalledRTDLDeployment) \
            or getattr(deployment, "_token", None) is not _DEPLOYMENT_CAPABILITY_TOKEN:
        _fail("RX048_DEPLOYMENT_CAPABILITY_INVALID", "deployment", type(deployment).__name__)
    try:
        current_root = _read_regular_bytes_once(
            deployment.trust_root_path, code="RX048_DEPLOYMENT_CAPABILITY_INVALID")
        current_head = _read_regular_bytes_once(
            deployment.trust_head_path, code="RX048_DEPLOYMENT_CAPABILITY_INVALID")
        current_package = _read_regular_bytes_once(
            deployment.trust_package_path, code="RX048_DEPLOYMENT_CAPABILITY_INVALID")
    except RTDLExecutableError:
        raise
    if _sha_bytes(current_root) != deployment.trust_root_sha256 \
            or _sha_bytes(current_head) != deployment.trust_head_sha256 \
            or _sha_bytes(current_package) != deployment.trust_package_sha256:
        _fail("RX048_DEPLOYMENT_CAPABILITY_INVALID", "deployment", "installed trust bytes changed")
    if artifact_file == authority_file:
        _fail("RX012_AUTHORITY_NOT_DETACHED", "authority_path", authority_file)
    authority, authority_raw = _read_canonical_json_with_raw(
        authority_file, code="RX018_AUTHORITY_INVALID")
    authority_sha = _sha_bytes(authority_raw)
    authority_schema = authority.get("schema") if isinstance(authority, Mapping) else None
    authority_version = authority.get("authority_version") \
        if isinstance(authority, Mapping) else None
    family_bound = (
        authority_schema == _FAMILY_AUTHORITY_SCHEMA
        and type(authority_version) is int
        and authority_version == 2
    )
    authority_keys = {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }
    if family_bound:
        authority_keys.update({
            "generic_family_binding_sha256",
            "family_executable_identity_sha256",
        })
    authority = _require_exact_keys(authority, authority_keys, "authority")
    if not family_bound and (
        authority["schema"] != _AUTHORITY_SCHEMA
        or type(authority["authority_version"]) is not int
        or authority["authority_version"] != 1
    ):
        _fail("RX019_AUTHORITY_SCHEMA_ROLLBACK", "authority.schema", authority["schema"])
    authority_body = dict(authority); authority_seal = authority_body.pop("authority_seal")
    if _require_sha(authority_seal, "authority.authority_seal") != \
            _sha_bytes(
                (_FAMILY_AUTHORITY_DOMAIN if family_bound else _AUTHORITY_DOMAIN)
                + _canonical(authority_body)
            ):
        _fail("RX020_AUTHORITY_SEAL_MISMATCH", "authority.authority_seal", authority_seal)
    for key in (
        "artifact_sha256", "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "task_semantics_sha256",
    ):
        _require_sha(authority[key], f"authority.{key}")
    if family_bound:
        for key in (
            "generic_family_binding_sha256",
            "family_executable_identity_sha256",
        ):
            _require_sha(authority[key], f"authority.{key}")
    for key in ("deployment_id", "family"):
        _require_string(authority[key], f"authority.{key}")
    if not isinstance(authority["target_compute_capability"], list) \
            or len(authority["target_compute_capability"]) != 2 \
            or any(not isinstance(item, int) or isinstance(item, bool) or item < 0
                   for item in authority["target_compute_capability"]):
        _fail("RX018_AUTHORITY_INVALID", "authority.target_compute_capability",
              authority["target_compute_capability"])
    if type(authority["artifact_bytes"]) is not int or authority["artifact_bytes"] <= 0:
        _fail("RX018_AUTHORITY_INVALID", "authority.artifact_bytes", authority["artifact_bytes"])

    artifact, artifact_raw = _read_canonical_json_with_raw(
        artifact_file, code="RX023_ARTIFACT_INVALID")
    artifact_sha = _sha_bytes(artifact_raw)
    if artifact_sha != authority["artifact_sha256"] \
            or len(artifact_raw) != authority["artifact_bytes"]:
        _fail("RX021_ARTIFACT_IDENTITY_MISMATCH", "artifact", "bytes/hash differ from authority")
    if artifact_file.name != f"{artifact_sha}.rtdlexe":
        _fail("RX022_CONTENT_ADDRESS_MISMATCH", "artifact.path", artifact_file.name)
    artifact_schema = artifact.get("schema") if isinstance(artifact, Mapping) else None
    artifact_version = artifact.get("format_version") \
        if isinstance(artifact, Mapping) else None
    artifact_family_bound = (
        artifact_schema == _FAMILY_ARTIFACT_SCHEMA
        and type(artifact_version) is int
        and artifact_version == 2
    )
    artifact = _require_exact_keys(artifact, {
        "schema", "format_version", "product_projection", "protocol_declaration",
        "compiler_projection", "protocol_decision", "composed_ptx_base64",
    }, "artifact")
    if artifact_family_bound != family_bound or (
        not artifact_family_bound
        and (
            artifact["schema"] != _ARTIFACT_SCHEMA
            or type(artifact["format_version"]) is not int
            or artifact["format_version"] != 1
        )
    ):
        _fail("RX024_ARTIFACT_SCHEMA_ROLLBACK", "artifact.schema", artifact["schema"])
    declaration = artifact["protocol_declaration"]
    projection = artifact["compiler_projection"]
    if not isinstance(declaration, Mapping) or not isinstance(projection, Mapping):
        _fail("RX023_ARTIFACT_INVALID", "artifact.protocol", "mappings required")
    mismatches = _verify_contract_pair(declaration, projection)
    decision = _require_exact_keys(artifact["protocol_decision"], {
        "schema", "verdict", "findings", "contract_sha256", "projection_sha256",
        "executable_capability_issued", "decision_sha256",
    }, "artifact.protocol_decision")
    decision_body = dict(decision); decision_seal = decision_body.pop("decision_sha256")
    if _require_sha(decision_seal, "decision.decision_sha256") != _digest(decision_body):
        _fail("RX014_PROTOCOL_SEAL_MISMATCH", "decision.decision_sha256", decision_seal)
    if mismatches or decision["verdict"] != "ACCEPT" or decision["findings"] != [] \
            or decision["executable_capability_issued"] is not False \
            or decision["contract_sha256"] != declaration["contract_sha256"] \
            or decision["projection_sha256"] != projection["projection_sha256"]:
        _fail("RX025_PROTOCOL_DECISION_REJECTED", "artifact.protocol_decision", mismatches)
    if decision_seal != authority["protocol_decision_sha256"]:
        _fail("RX010_DECISION_CHAIN_MISMATCH", "authority.protocol_decision_sha256", decision_seal)

    product_keys = {
        "schema", "deployment_id", "family", "executable_identity", "protocol_contract_sha256",
        "compiler_projection_sha256", "protocol_decision_sha256", "runtime",
        "target_toolchain", "composed_ptx_sha256", "compiler_options", "ptx_metadata",
        "provider_key", "execution_schema",
    }
    if family_bound:
        product_keys.add("generic_family_binding")
    product = _require_exact_keys(
        artifact["product_projection"], product_keys,
        "artifact.product_projection",
    )
    expected_product_schema = (
        _FAMILY_PROJECTION_SCHEMA if family_bound else _PROJECTION_SCHEMA
    )
    if product["schema"] != expected_product_schema \
            or _digest(product) != authority["product_projection_sha256"]:
        _fail("RX026_PRODUCT_PROJECTION_MISMATCH", "artifact.product_projection", "outer binding failed")
    runtime = _validate_runtime(product["runtime"])
    target = _require_exact_keys(product["target_toolchain"], {
        "schema", "target_sha256", "native_library_sha256", "provider", "optix_sdk",
        "compute_capability", "supports_custom_aabb", "supports_builtin_triangle",
        "max_graph_depth", "python_version", "numba_version", "numpy_version",
    }, "product_projection.target_toolchain")
    if target["schema"] != "rtdl.v4.rtdlexe.target_toolchain_binding.v1" \
            or target["native_library_sha256"] != authority["native_library_sha256"] \
            or target["target_sha256"] != authority["target_sha256"] \
            or not isinstance(target["compute_capability"], list) \
            or len(target["compute_capability"]) != 2 \
            or any(not isinstance(item, int) or isinstance(item, bool) or item < 0
                   or item >= 1 << 32 for item in target["compute_capability"]):
        _fail("RX027_TARGET_BINDING_MISMATCH", "product_projection.target_toolchain", target)
    if target["provider"] != "optix" or not isinstance(target["max_graph_depth"], int) \
            or isinstance(target["max_graph_depth"], bool) or target["max_graph_depth"] < 1 \
            or target["max_graph_depth"] >= 1 << 32 \
            or type(target["supports_custom_aabb"]) is not bool \
            or type(target["supports_builtin_triangle"]) is not bool \
            or (runtime["family"] == _BOUNDED and target["supports_custom_aabb"] is not True) \
            or (runtime["family"] == _TRIANGLE and target["supports_builtin_triangle"] is not True):
        _fail("RX027_TARGET_BINDING_MISMATCH", "product_projection.target_toolchain",
              "family target capability missing")
    metadata = _require_exact_keys(product["ptx_metadata"], {
        "version", "target", "address_size",
    }, "product_projection.ptx_metadata")
    if not isinstance(product["compiler_options"], list) \
            or any(not isinstance(item, str) or not item for item in product["compiler_options"]):
        _fail("RX026_PRODUCT_PROJECTION_MISMATCH", "product.compiler_options",
              product["compiler_options"])
    provider = _verify_provider_key(product["provider_key"])
    execution_schema = _verify_execution_schema(product["execution_schema"])
    if provider["native_provider_sha256"] != target["native_library_sha256"] \
            or provider["target_compute_capability"] != target["compute_capability"] \
            or provider["python_version"] != target["python_version"] \
            or provider["numba_version"] != target["numba_version"] \
            or provider["numpy_version"] != target["numpy_version"] \
            or provider["optix_sdk_version"] != target["optix_sdk"] \
            or provider["compile_options"] != product["compiler_options"] \
            or provider["ptx_isa"] != metadata["version"] \
            or provider["ptx_target"] != metadata["target"] \
            or provider["address_size"] != metadata["address_size"]:
        _fail("RX051_PROVIDER_KEY_INVALID", "provider_key", "target/compiler projection drift")
    if product["family"] != runtime["family"] \
            or product["deployment_id"] != authority["deployment_id"] \
            or declaration["family"] != product["family"] \
            or projection["family"] != product["family"] \
            or product["protocol_contract_sha256"] != declaration["contract_sha256"] \
            or product["compiler_projection_sha256"] != projection["projection_sha256"] \
            or product["protocol_decision_sha256"] != decision_seal:
        _fail("RX026_PRODUCT_PROJECTION_MISMATCH", "artifact.product_projection", "nested chain drift")
    identity = product["executable_identity"]
    if not isinstance(identity, Mapping) or _digest(identity) != authority["executable_identity_sha256"]:
        _fail("RX028_EXECUTABLE_IDENTITY_MISMATCH", "product_projection.executable_identity", identity)
    try:
        ptx_bytes = base64.b64decode(artifact["composed_ptx_base64"], validate=True)
        ptx = ptx_bytes.decode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        _fail("RX029_PTX_INVALID", "artifact.composed_ptx_base64", error)
    ptx_sha = _sha_bytes(ptx_bytes)
    if not ptx or ptx_sha != product["composed_ptx_sha256"] \
            or ptx_sha != projection["generated_device_source_sha256"] \
            or ptx_sha != identity.get("composed_ptx_sha256"):
        _fail("RX009_PTX_IDENTITY_MISMATCH", "artifact.composed_ptx", ptx_sha)
    if declaration["checked_executable_sha256"] != identity.get("generated_executable_sha256"):
        _fail("RX028_EXECUTABLE_IDENTITY_MISMATCH", "protocol.checked_executable", identity)
    if family_bound:
        family_binding = _verify_generic_family_binding(
            product["generic_family_binding"],
            family=str(product["family"]),
            executable_identity=identity,
            target=target,
            composed_ptx_sha256=ptx_sha,
        )
        family_identity = family_binding["family_executable_identity"]
        assert isinstance(family_identity, Mapping)
        if family_binding["binding_sha256"] != \
                authority["generic_family_binding_sha256"] \
                or family_identity["identity_sha256"] != \
                authority["family_executable_identity_sha256"]:
            _fail(
                "RX058_FAMILY_BINDING_INVALID",
                "authority.generic_family_binding",
                "authority and artifact family identities differ",
            )
    producer_inputs = execution_schema["producer_inputs"]
    assert isinstance(producer_inputs, Mapping)
    for name, row in producer_inputs.items():
        if not isinstance(row, Mapping) \
                or row.get("callback_abi_sha256") != provider["callback_abi_sha256"] \
                or row.get("wrapper_source_sha256") != provider["wrapper_source_sha256"] \
                or row.get("contract_sha256") != declaration["contract_sha256"] \
                or row.get("composed_ptx_sha256") != ptx_sha \
                or row.get("native_provider_sha256") != target["native_library_sha256"] \
                or row.get("compiler_options") != provider["compile_options"] \
                or row.get("link_options") != provider["link_options"]:
            _fail("RX052_EXECUTION_SCHEMA_INVALID", f"execution_schema.producer_inputs.{name}",
                  "producer chain drift")
    expected_bundle = (
        "v4_custom_aabb_bounded_relation_composed"
        if runtime["family"] == _BOUNDED else
        "v4_builtin_triangle_checked_reduction_composed"
    )
    _validate_native_producer_descriptor(
        execution_schema["native_producer_descriptor"],
        family=str(runtime["family"]), native_abi=str(runtime["native_abi"]),
        program_bundle=expected_bundle)
    module_input = producer_inputs["module"]
    program_group_input = producer_inputs["program_group"]
    pipeline_input = producer_inputs["pipeline"]
    sbt_input = producer_inputs["sbt"]
    launch_input = producer_inputs["launch_parameters"]
    status_input = producer_inputs["status"]
    if execution_schema["native_program_bundle"] != expected_bundle \
            or module_input.get("kind") != "module_schema_identity" \
            or program_group_input.get("kind") != "program_group_schema_identity" \
            or program_group_input.get("physical_template") != provider["physical_template"] \
            or program_group_input.get("program_bundle") != expected_bundle \
            or pipeline_input.get("kind") != "pipeline_schema_identity" \
            or pipeline_input.get("program_group_schema_sha256") != _digest(program_group_input) \
            or pipeline_input.get("trace_depth") != 1 \
            or sbt_input.get("kind") != "sbt_schema_identity" \
            or sbt_input.get("sbt_layout_sha256") != provider["sbt_layout_sha256"] \
            or sbt_input.get("program_group_schema_sha256") != _digest(program_group_input) \
            or launch_input.get("kind") != "launch_parameter_schema_identity" \
            or launch_input.get("callback_abi_projection_sha256") != \
                _digest(provider["callback_abi_projection"]) \
            or launch_input.get("runtime_native_abi") != runtime["native_abi"] \
            or status_input.get("kind") != "status_schema_identity" \
            or status_input.get("dynamic_status") != runtime["dynamic_status"] \
            or status_input.get("runtime_status_codes") != \
                provider["callback_abi_projection"].get("runtime_status_codes"):
        _fail("RX052_EXECUTION_SCHEMA_INVALID", "execution_schema.producer_inputs",
              "producer semantics drift")
    exact_entry = {
        "deployment_id": product["deployment_id"],
        "family": product["family"],
        "task_semantics_sha256": declaration["task_semantics_sha256"],
        "authority_sha256": authority_sha,
        "artifact_sha256": artifact_sha,
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "target_sha256": target["target_sha256"],
        "native_library_sha256": target["native_library_sha256"],
        "compute_capability": tuple(target["compute_capability"]),
    }
    if authority["family"] != exact_entry["family"] \
            or authority["task_semantics_sha256"] != exact_entry["task_semantics_sha256"] \
            or tuple(authority["target_compute_capability"]) != exact_entry["compute_capability"] \
            or deployment.deployment_id != exact_entry["deployment_id"] \
            or deployment.entry != exact_entry:
        _fail("RX050_DEPLOYMENT_INTENT_MISMATCH", "deployment", exact_entry)
    return _issue_loaded_runtime_session_capability(LoadedRTDLExecutable(
        artifact_path=artifact_file,
        authority_path=authority_file,
        authority_sha256=authority_sha,
        deployment_id=deployment.deployment_id,
        trust_root_sha256=deployment.trust_root_sha256,
        trust_package_sha256=deployment.trust_package_sha256,
        artifact_sha256=artifact_sha,
        executable_identity_sha256=authority["executable_identity_sha256"],
        family=str(product["family"]),
        composed_ptx=ptx,
        product_projection=product,
        family_executable_identity_sha256=(
            str(authority["family_executable_identity_sha256"])
            if family_bound
            else None
        ),
    ))


class _DeviceStatusRow(ctypes.Structure):
    _fields_ = [
        ("first_error_claimed", ctypes.c_uint32), ("error_code", ctypes.c_uint32),
        ("stage", ctypes.c_uint32), ("role", ctypes.c_uint32),
        ("launch_index", ctypes.c_uint64), ("error_site", ctypes.c_uint32),
        ("effect_tag", ctypes.c_uint32), ("nonce_word", ctypes.c_uint32),
        ("invocation_mask", ctypes.c_uint32),
    ]


class _ProductStatusSummary(ctypes.Structure):
    _fields_ = [
        ("schema_version", ctypes.c_uint32), ("ok", ctypes.c_uint32),
        ("first_error_claimed", ctypes.c_uint32), ("error_code", ctypes.c_uint32),
        ("validated_row_count", ctypes.c_uint64),
        ("required_invocation_mask", ctypes.c_uint32),
        ("terminal_invocation_mask", ctypes.c_uint32),
        ("invalid_row_count", ctypes.c_uint32),
        ("first_invalid_row", ctypes.c_uint64),
        ("role_counters", ctypes.c_uint64 * 7),
        ("success_status_d2h_bytes", ctypes.c_uint64),
    ]


class _CheckedProductResult(ctypes.Structure):
    _fields_ = [
        ("value", ctypes.c_uint64), ("overflowed", ctypes.c_uint32),
        ("schema_version", ctypes.c_uint32), ("input_count", ctypes.c_uint64),
        ("success_result_d2h_bytes", ctypes.c_uint64),
    ]


class _FastPathReceipt(ctypes.Structure):
    _fields_ = [
        ("schema_version", ctypes.c_uint32),
        ("optix_launch_count", ctypes.c_uint32),
        ("host_blocking_boundary_count", ctypes.c_uint32),
        ("control_d2h_bytes", ctypes.c_uint32),
        ("output_d2h_bytes", ctypes.c_uint64),
        ("status_before_output", ctypes.c_uint32),
        ("output_d2h_after_status_failure", ctypes.c_uint32),
        ("role_counters_materialized", ctypes.c_uint32),
        ("prepared_input_reused", ctypes.c_uint32),
        ("dynamic_device_upload_call_count", ctypes.c_uint32),
        ("dynamic_accel_build_count", ctypes.c_uint32),
        ("dynamic_explicit_sync_count", ctypes.c_uint32),
        ("dynamic_blocking_upload_call_count", ctypes.c_uint32),
        ("dynamic_device_upload_bytes", ctypes.c_uint64),
        ("dynamic_input_generation", ctypes.c_uint64),
        ("semantic_compaction_launch_count", ctypes.c_uint32),
        ("semantic_compaction_key_capacity", ctypes.c_uint32),
        ("semantic_compaction_scratch_bytes", ctypes.c_uint64),
        ("callback_status_kernel_launch_count", ctypes.c_uint32),
        ("checked_product_kernel_launch_count", ctypes.c_uint32),
        ("compact_control_finalizer_kernel_launch_count", ctypes.c_uint32),
        ("total_auxiliary_cuda_kernel_launch_count", ctypes.c_uint32),
        ("execution_parameter_h2d_bytes", ctypes.c_uint64),
        ("execution_parameter_h2d_copy_call_count", ctypes.c_uint32),
        ("stream_ordered_memset_call_count", ctypes.c_uint32),
        ("status_d2h_copy_call_count", ctypes.c_uint32),
        ("output_d2h_copy_call_count", ctypes.c_uint32),
    ]


_FAST_PATH_RECEIPT_FIELD_OFFSETS = {
    field: getattr(_FastPathReceipt, field).offset
    for field, _ctype in _FastPathReceipt._fields_
}


def _raise_native(status: int, error, label: str) -> None:
    if status:
        detail = error.value.decode("utf-8", errors="replace")
        _fail("RX030_NATIVE_FAILURE", label, detail or f"status {status}")


def _warm_native_provider_runtime(library: object) -> None:
    """Initialize only the app-free CUDA/OptiX provider singleton."""

    warm = getattr(library, "rtdl_optix_v4_warm_runtime_v1", None)
    if warm is None:
        _fail(
            "RX036_NATIVE_ABI_MISSING", "native.warm_runtime",
            "rtdl_optix_v4_warm_runtime_v1")
    warm.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
    warm.restype = ctypes.c_int
    error = ctypes.create_string_buffer(4096)
    _raise_native(
        int(warm(error, len(error))), error,
        "rtdl_optix_v4_warm_runtime_v1")


def _mark_native_runtime_touched() -> None:
    """Publish a sticky pre-FFI fork-safety marker."""

    global _NATIVE_RUNTIME_TOUCHED
    _NATIVE_RUNTIME_TOUCHED = True


@dataclass(frozen=True)
class _CudaPrimaryContextReadinessState:
    """One admitted process-lifetime primary-context retain."""

    driver: object
    device: int
    context: int
    compute_capability: tuple[int, int]
    owner_pid: int


class _CudaPrimaryContextReadinessLease:
    """PID-bound local reference to process-lifetime CUDA readiness.

    Closing a provider closes only this local capability.  The single CUDA
    primary-context retain remains owned by the process until CUDA driver
    teardown, matching the process-lifetime sealed native-image cache.  No
    external release side effect occurs at an arbitrary Python object boundary.
    """

    __slots__ = ("_state", "_pid", "_released", "_active")

    def __init__(self, *, state: _CudaPrimaryContextReadinessState) -> None:
        self._state = state
        self._pid = os.getpid()
        self._released = False
        self._active = threading.Lock()

    @property
    def released(self) -> bool:
        return self._released

    @property
    def owner_pid(self) -> int:
        return self._pid

    @property
    def context_handle(self) -> int:
        self.check()
        return self._state.context

    def check(self) -> None:
        if self._released:
            _fail("RX037_USE_AFTER_CLOSE", "provider_ready.cuda", "released")
        if os.getpid() != self._pid:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                "primary-context readiness belongs to a different process")
        if _CUDA_PRIMARY_READY_PID != self._pid \
                or _CUDA_PRIMARY_READY_STATE is not self._state:
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                "process CUDA readiness identity changed")

    def close(self) -> None:
        if self._released:
            return
        self.check()
        if not self._active.acquire(blocking=False):
            _fail("RX040_REENTRANT", "provider_ready.cuda.close", "active")
        try:
            # This is deliberately a local, idempotent state transition.  The
            # process retain cannot be safely released while other Python or
            # native CUDA/OptiX objects may still reference the context.
            self._released = True
        finally:
            self._active.release()


def _configure_cuda_primary_context_api(cuda: object) -> None:
    cuda.cuInit.argtypes = [ctypes.c_uint]
    cuda.cuInit.restype = ctypes.c_int
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceGet.restype = ctypes.c_int
    cuda.cuDeviceComputeCapability.argtypes = [
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceComputeCapability.restype = ctypes.c_int
    cuda.cuCtxGetCurrent.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    cuda.cuCtxGetCurrent.restype = ctypes.c_int
    cuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
    cuda.cuCtxSetCurrent.restype = ctypes.c_int
    cuda.cuDevicePrimaryCtxRetain.argtypes = [
        ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
    cuda.cuDevicePrimaryCtxRetain.restype = ctypes.c_int
    cuda.cuDevicePrimaryCtxRelease.argtypes = [ctypes.c_int]
    cuda.cuDevicePrimaryCtxRelease.restype = ctypes.c_int


def _acquire_cuda_primary_context_readiness(
    *, expected_compute_capability: tuple[int, int],
) -> _CudaPrimaryContextReadinessLease:
    """Borrow one exact process-ready primary context, restoring caller state."""

    global _CUDA_PRIMARY_READY_STATE

    _native_image_cache_guard(
        code="RX047_NATIVE_CACHE_FORK_POISONED",
        identity_path="provider_ready.cuda")
    expected = tuple(expected_compute_capability)
    with _CUDA_PRIMARY_READY_LOCK:
        # A waiter can pass the outer guard before another thread poisons the
        # process during failed CUDA admission.  Recheck after serialization
        # and before any second external driver call or retain.
        _native_image_cache_guard(
            code="RX047_NATIVE_CACHE_FORK_POISONED",
            identity_path="provider_ready.cuda")
        if _CUDA_PRIMARY_READY_PID != os.getpid():
            _fail(
                "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                "process CUDA readiness owner changed")
        existing = _CUDA_PRIMARY_READY_STATE
        if existing is not None:
            if existing.owner_pid != os.getpid():
                _fail(
                    "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.cuda",
                    "process CUDA readiness belongs to another process")
            if existing.compute_capability != expected:
                _fail(
                    "RX033_DEVICE_SUBSTITUTION", "cuda.compute_capability",
                    existing.compute_capability)
            return _CudaPrimaryContextReadinessLease(state=existing)

        name = "nvcuda.dll" if os.name == "nt" else "libcuda.so.1"
        _mark_native_runtime_touched()
        try:
            cuda = ctypes.CDLL(name)
        except OSError as error:
            _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda", error)
        _configure_cuda_primary_context_api(cuda)
        if int(cuda.cuInit(0)) != 0:
            _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuInit", "nonzero status")
        device = ctypes.c_int()
        if int(cuda.cuDeviceGet(ctypes.byref(device), 0)) != 0:
            _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuDeviceGet", "nonzero status")
        major = ctypes.c_int(); minor = ctypes.c_int()
        if int(cuda.cuDeviceComputeCapability(
                ctypes.byref(major), ctypes.byref(minor), device.value)) != 0:
            _fail(
                "RX031_CUDA_DRIVER_UNAVAILABLE",
                "cuda.cuDeviceComputeCapability", "nonzero status")
        actual_capability = (major.value, minor.value)
        if actual_capability != expected:
            _fail(
                "RX033_DEVICE_SUBSTITUTION", "cuda.compute_capability",
                actual_capability)

        previous = ctypes.c_void_p()
        if int(cuda.cuCtxGetCurrent(ctypes.byref(previous))) != 0:
            _fail(
                "RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuCtxGetCurrent",
                "nonzero status")
        primary = ctypes.c_void_p()
        candidate = None
        try:
            # ``primary.value`` is the external side-effect witness.  It is
            # populated by CUDA before a test-injected asynchronous exception
            # can escape from the call, unlike a Python ``retained`` flag set
            # on the following line.
            retain_status = int(cuda.cuDevicePrimaryCtxRetain(
                ctypes.byref(primary), device.value))
            if retain_status != 0 or not primary.value:
                _fail(
                    "RX031_CUDA_DRIVER_UNAVAILABLE",
                    "cuda.cuDevicePrimaryCtxRetain",
                    "nonzero status or null context")
            if primary.value != previous.value:
                if int(cuda.cuCtxSetCurrent(primary)) != 0:
                    _fail(
                        "RX031_CUDA_DRIVER_UNAVAILABLE",
                        "cuda.cuCtxSetCurrent", "primary selection failed")
                if int(cuda.cuCtxSetCurrent(previous)) != 0:
                    _fail(
                        "RX031_CUDA_DRIVER_UNAVAILABLE",
                        "cuda.cuCtxSetCurrent", "caller restoration failed")
            candidate = _CudaPrimaryContextReadinessState(
                driver=cuda, device=device.value, context=int(primary.value),
                compute_capability=actual_capability, owner_pid=os.getpid())
            # Publication transfers the retain to process lifetime.  If an
            # asynchronous exception lands immediately after this assignment,
            # the exception path recognizes the published identity and must
            # not release it.
            _CUDA_PRIMARY_READY_STATE = candidate
            return _CudaPrimaryContextReadinessLease(state=candidate)
        except BaseException as admission_error:
            if candidate is not None and _CUDA_PRIMARY_READY_STATE is candidate:
                # The process owns the successfully published retain.  Preserve
                # it for the next borrower and propagate the interruption.
                raise
            restore_status = None
            release_status = None
            if primary.value:
                try:
                    # A failing foreign selection can still mutate current
                    # context.  Always restore before dropping the unpublished
                    # retain.
                    restore_status = int(cuda.cuCtxSetCurrent(previous))
                except BaseException as cleanup_error:
                    restore_status = repr(cleanup_error)
                try:
                    # Exactly one cleanup attempt.  If the foreign call performs
                    # its side effect and then raises, poison the process cache;
                    # never retry an externally ambiguous release.
                    release_status = int(
                        cuda.cuDevicePrimaryCtxRelease(device.value))
                except BaseException as cleanup_error:
                    release_status = repr(cleanup_error)
            if restore_status not in (None, 0) \
                    or release_status not in (None, 0):
                cleanup_failure = RTDLExecutableError(
                    "RX031_CUDA_DRIVER_UNAVAILABLE",
                    "cuda.primary_context_admission_cleanup", str({
                        "admission_error": repr(admission_error),
                        "restore_status": restore_status,
                        "release_status": release_status,
                    }))
                _poison_native_image_cache(cleanup_failure)
                raise cleanup_failure
            raise


def _initialize_cuda_and_get_capability() -> tuple[int, int]:
    # Deterministic driver names avoid ``ctypes.util.find_library`` invoking
    # ldconfig or another subprocess on the compiler-free cache-hit path.
    name = "nvcuda.dll" if os.name == "nt" else "libcuda.so.1"
    # Publish before ``CDLL``: its loader and constructors are foreign runtime
    # work even if the call raises before a DSO cache entry can be published.
    _mark_native_runtime_touched()
    try:
        cuda = ctypes.CDLL(name)
    except OSError as error:
        _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda", error)
    cuda.cuInit.argtypes = [ctypes.c_uint]; cuda.cuInit.restype = ctypes.c_int
    if int(cuda.cuInit(0)) != 0:
        _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuInit", "nonzero status")
    device = ctypes.c_int()
    cuda.cuDeviceGet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceGet.restype = ctypes.c_int
    if int(cuda.cuDeviceGet(ctypes.byref(device), 0)) != 0:
        _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuDeviceGet", "nonzero status")
    major = ctypes.c_int(); minor = ctypes.c_int()
    cuda.cuDeviceComputeCapability.argtypes = [
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.c_int]
    cuda.cuDeviceComputeCapability.restype = ctypes.c_int
    if int(cuda.cuDeviceComputeCapability(
            ctypes.byref(major), ctypes.byref(minor), device.value)) != 0:
        _fail("RX031_CUDA_DRIVER_UNAVAILABLE", "cuda.cuDeviceComputeCapability", "nonzero status")
    # Capability admission does not retain or install a CUDA context.  The
    # exact native deployment owns one process-level primary-context retain;
    # duplicating that retain here would leak one reference per prepare.
    return major.value, minor.value


def _load_native_library(
    path: Path, *, expected_sha256: str, expected_compute_capability: tuple[int, int],
):
    # A forked child that inherited any cached native image must fail before
    # touching libcuda or a CUDA context.  The descriptor loader repeats this
    # guard after path verification to close the intervening TOCTOU window.
    _native_image_cache_guard(
        code="RX047_NATIVE_CACHE_FORK_POISONED",
        identity_path="native_library_path")
    actual_capability = _initialize_cuda_and_get_capability()
    if actual_capability != tuple(expected_compute_capability):
        _fail("RX033_DEVICE_SUBSTITUTION", "cuda.compute_capability", actual_capability)
    return _load_verified_native_file_descriptor(
        path, expected_sha256=expected_sha256,
        code="RX032_NATIVE_IDENTITY_MISMATCH",
        identity_path="native_library_path")


def _load_verified_native_file_descriptor(
    path: Path, *, expected_sha256: str, code: str, identity_path: str,
    lease_handoff: _NativeImageLeaseHandoff | None = None,
):
    """Acquire a lease on one immutable, content-addressed native image.

    Merely passing ``/proc/self/fd/N`` to ``dlopen`` is not sufficient.  glibc
    caches a loaded DSO by that *path string*, so after descriptor ``N`` is
    closed and reused it can return the old handle while the caller has hashed
    a different new inode.  Copy the verified bytes into a write-sealed memfd
    and expose the first acquisition through a fresh private alias whose full
    spelling is never reused in this process.  The DSO and sealed descriptor
    are then retained in a process/PID-bound cache keyed by the verified byte
    digest.  Every later acquisition still rereads and hashes the caller's
    specified path before it can receive an independent lease.  Thus a digest
    has exactly one executable image, different digests cannot alias through
    the loader cache, and prepared close never invokes unsafe mid-process DSO
    teardown.  Platforms without Linux memfd, seals, procfs, and symlinks fail
    closed.
    """

    _native_image_cache_guard(code=code, identity_path=identity_path)
    path = _absolute_unresolved_path(path)
    source_descriptor, _ = _open_regular_readonly(path, code=code)
    image_descriptor = -1
    alias_path: Path | None = None
    alias_directory: Path | None = None
    loaded_library = None
    entry_published = False
    library = None
    try:
        native_bytes, _ = _read_descriptor_bytes(
            source_descriptor, code=code, path=path)
        observed_sha256 = _sha_bytes(native_bytes)
        if not hmac.compare_digest(observed_sha256, expected_sha256):
            _fail(code, identity_path, observed_sha256)
        os.close(source_descriptor)
        source_descriptor = -1

        with _NATIVE_IMAGE_CACHE_LOCK:
            _native_image_cache_guard(code=code, identity_path=identity_path)
            entry = _NATIVE_IMAGE_CACHE.get(observed_sha256)
            if entry is None:
                image_descriptor, required_seals = _sealed_native_image_descriptor(
                    native_bytes, expected_sha256=observed_sha256,
                    code=code, identity_path=identity_path)
                alias_directory, alias_path = _create_unique_native_loader_alias(
                    image_descriptor, observed_sha256=observed_sha256,
                    code=code, identity_path=identity_path)
                loader_alias_spelling = str(alias_path)
                try:
                    # As with CUDA admission, mark the process before dlopen or
                    # any DSO constructor can run.  atfork must poison a child
                    # even if publication below never completes.
                    _mark_native_runtime_touched()
                    loaded_library = ctypes.CDLL(loader_alias_spelling)
                except OSError as error:
                    _fail(code, identity_path, error)
                entry = _NativeImageCacheEntry(
                    library=loaded_library,
                    sha256=observed_sha256,
                    source_path=path,
                    image_descriptor=image_descriptor,
                    image_seals=required_seals,
                    loader_alias=loader_alias_spelling,
                    owner_pid=os.getpid(),
                )
                _NATIVE_IMAGE_CACHE[observed_sha256] = entry
                entry_published = True
                image_descriptor = -1
                try:
                    _remove_native_loader_alias(
                        alias_path, alias_directory,
                        code=code, identity_path=identity_path)
                    alias_path = None
                    alias_directory = None
                    after_bytes, _ = _read_descriptor_bytes(
                        entry.image_descriptor, code=code, path=path)
                    if not hmac.compare_digest(native_bytes, after_bytes):
                        _fail(code, identity_path,
                              "sealed native image changed during load")
                    observed_seals = _native_image_seals(
                        entry.image_descriptor, code=code,
                        identity_path=identity_path)
                    if observed_seals & required_seals != required_seals:
                        _fail(code, identity_path,
                              "sealed native image lost required seals")
                    loaded_library._rtdl_library_path = str(path)
                    loaded_library._rtdl_loaded_library_path = str(path)
                    loaded_library._rtdl_loaded_library_sha256 = observed_sha256
                    entry.image_seals = observed_seals
                    entry.usable = True
                except BaseException as error:
                    entry.load_failure = repr(error)
                    _poison_native_image_cache(error)
                    raise
            else:
                _validate_cached_native_image(
                    entry, native_bytes=native_bytes, source_path=path,
                    code=code, identity_path=identity_path)
        library = _admit_native_image_lease(
            entry, source_path=path, register_provenance=(
                code == "RX032_NATIVE_IDENTITY_MISMATCH"),
            lease_handoff=lease_handoff)
        if lease_handoff is not None:
            lease_handoff.publish(library)
        return library
    except BaseException as error:
        if isinstance(library, _NativeLibraryLease) \
                and not library._rtdl_native_image_released:
            try:
                _release_native_library_image(library)
            except BaseException:
                # Keep the original admission error authoritative.  The lease
                # abandonment finalizer still removes its cache id when no
                # provenance registry owns the object.
                pass
        if loaded_library is not None and not entry_published:
            # An exception can land immediately after dlopen returns but
            # before the entry publication bytecode.  The DSO may now be
            # mapped without a trustworthy cache record.  Poison the process
            # so no second untracked mapping can be admitted.
            _poison_native_image_cache(error)
        if alias_path is not None and alias_directory is not None:
            try:
                _remove_native_loader_alias(
                    alias_path, alias_directory,
                    code=code, identity_path=identity_path)
            except BaseException:
                pass
        # A successfully published cache entry owns its descriptor until
        # process exit.  Only an unpublished pre-load descriptor is closed.
        if image_descriptor >= 0:
            os.close(image_descriptor)
        if source_descriptor >= 0:
            os.close(source_descriptor)
        raise


def _native_image_cache_guard(*, code: str, identity_path: str) -> None:
    if _NATIVE_IMAGE_CACHE_LOAD_POISONED:
        _fail(
            "RX048_NATIVE_CACHE_QUARANTINED", identity_path,
            _NATIVE_IMAGE_CACHE_LOAD_FAILURE
            or "a post-dlopen cache publication failed in this process",
        )
    if _NATIVE_IMAGE_CACHE_FORK_POISONED:
        _fail(
            "RX047_NATIVE_CACHE_FORK_POISONED", identity_path,
            "child process inherited a loaded native-image cache",
        )
    if _NATIVE_IMAGE_CACHE_PID != os.getpid():
        _fail(
            "RX047_NATIVE_CACHE_FORK_POISONED", identity_path,
            "native-image cache belongs to a different process",
        )


def _poison_native_image_cache(error: BaseException) -> None:
    global _NATIVE_IMAGE_CACHE_LOAD_POISONED, _NATIVE_IMAGE_CACHE_LOAD_FAILURE
    _NATIVE_IMAGE_CACHE_LOAD_POISONED = True
    _NATIVE_IMAGE_CACHE_LOAD_FAILURE = repr(error)


def _validate_cached_native_image(
    entry: _NativeImageCacheEntry, *, native_bytes: bytes, source_path: Path,
    code: str, identity_path: str,
) -> None:
    if entry.owner_pid != os.getpid():
        _fail("RX047_NATIVE_CACHE_FORK_POISONED", identity_path,
              "cached native image belongs to a different process")
    if not entry.usable:
        _fail("RX048_NATIVE_CACHE_QUARANTINED", identity_path,
              entry.load_failure or "cached native image did not finish validation")
    if not hmac.compare_digest(entry.sha256, _sha_bytes(native_bytes)):
        _fail(code, identity_path, "cache key differs from caller bytes")
    handle = getattr(entry.library, "_handle", None)
    if type(handle) is not int or handle <= 0:
        _fail(code, identity_path, "cached native image handle is invalid")
    try:
        os.fstat(entry.image_descriptor)
    except OSError as error:
        _fail(code, identity_path, f"cached sealed descriptor is invalid: {error}")
    cached_bytes, _ = _read_descriptor_bytes(
        entry.image_descriptor, code=code, path=source_path)
    if not hmac.compare_digest(cached_bytes, native_bytes):
        _fail(code, identity_path, "cached native image bytes differ from caller bytes")
    observed_seals = _native_image_seals(
        entry.image_descriptor, code=code, identity_path=identity_path)
    if observed_seals != entry.image_seals or observed_seals & 15 != 15:
        _fail(code, identity_path, "cached native image seals changed")


def _acquire_native_image_lease(
    entry: _NativeImageCacheEntry, *, source_path: Path,
) -> _NativeLibraryLease:
    global _NATIVE_IMAGE_CACHE_NEXT_LEASE
    with _NATIVE_IMAGE_CACHE_LOCK:
        _NATIVE_IMAGE_CACHE_NEXT_LEASE += 1
        lease_id = _NATIVE_IMAGE_CACHE_NEXT_LEASE
        lease = _NativeLibraryLease(
            entry=entry, lease_id=lease_id, source_path=source_path)
        previous_acquisition_count = entry.acquisition_count
        try:
            entry.active_lease_ids.add(lease_id)
            entry.acquisition_count = previous_acquisition_count + 1
            lease._rtdl_native_lease_abandon_finalizer = weakref.finalize(
                lease, _abandon_unpublished_native_image_lease,
                entry, lease_id, os.getpid())
            return lease
        except BaseException:
            entry.active_lease_ids.discard(lease_id)
            entry.acquisition_count = previous_acquisition_count
            raise


def _abandon_unpublished_native_image_lease(
    entry: _NativeImageCacheEntry, lease_id: int, owner_pid: int,
) -> None:
    if owner_pid != os.getpid():
        return
    with _NATIVE_IMAGE_CACHE_LOCK:
        entry.active_lease_ids.discard(lease_id)


def _admit_native_image_lease(
    entry: _NativeImageCacheEntry, *, source_path: Path,
    register_provenance: bool,
    lease_handoff: _NativeImageLeaseHandoff | None = None,
) -> _NativeLibraryLease:
    library = None
    try:
        library = _acquire_native_image_lease(entry, source_path=source_path)
        if register_provenance:
            _register_native_image_lease_provenance(
                library, source_path=source_path, digest=entry.sha256)
        _native_image_lease_handoff(library)
        if lease_handoff is not None:
            lease_handoff.publish(library)
        return library
    except BaseException:
        if isinstance(library, _NativeLibraryLease) \
                and not library._rtdl_native_image_released:
            _release_native_library_image(library)
        raise


def _native_descriptor_identity(descriptor: int) -> tuple[int, int, int, int]:
    try:
        row = os.fstat(descriptor)
    except OSError as error:
        _fail(
            "RX048_NATIVE_CACHE_QUARANTINED", "provider_ready.native_image",
            f"cached sealed descriptor is invalid: {error}")
    return (int(row.st_dev), int(row.st_ino), int(row.st_mode), int(row.st_size))


def _capture_provider_ready_native_binding(
    library: _NativeLibraryLease, *, source_path: Path,
) -> _ProviderReadyNativeBinding:
    """Freeze the exact cache entry and bind-time provenance of one live lease."""

    if not isinstance(library, _NativeLibraryLease) \
            or library._rtdl_native_image_released:
        _fail(
            "RX048_NATIVE_CACHE_QUARANTINED", "provider_ready.native_image",
            "binding object is not a live native cache lease")
    _native_image_cache_guard(
        code="RX047_NATIVE_CACHE_FORK_POISONED",
        identity_path="provider_ready.native_image")
    from .physical_execution_provenance import (  # pylint: disable=import-outside-toplevel
        _registered_loaded_provider_identity,
    )
    registered = _registered_loaded_provider_identity(library)
    if registered is None:
        _fail(
            "RX048_NATIVE_CACHE_QUARANTINED", "provider_ready.provenance",
            "bind-time source provenance is absent")
    provenance_path, provenance_digest = registered
    entry = library._rtdl_native_cache_entry
    with _NATIVE_IMAGE_CACHE_LOCK:
        cached = _NATIVE_IMAGE_CACHE.get(entry.sha256)
        handle = int(getattr(entry.library, "_handle", 0))
        seals = _native_image_seals(
            entry.image_descriptor,
            code="RX048_NATIVE_CACHE_QUARANTINED",
            identity_path="provider_ready.native_image")
        entry_identity = f"{entry.owner_pid}:{entry.sha256}"
        if cached is not entry \
                or not entry.usable or entry.load_failure is not None \
                or entry.owner_pid != os.getpid() \
                or library._rtdl_native_cache_entry_identity != entry_identity \
                or library._rtdl_native_cache_key != entry.sha256 \
                or library._rtdl_native_cache_owner_pid != entry.owner_pid \
                or library._rtdl_native_cache_lease_id not in entry.active_lease_ids \
                or library._rtdl_native_image_fd != entry.image_descriptor \
                or library._handle != handle or handle <= 0 \
                or seals != entry.image_seals or seals & 15 != 15 \
                or provenance_digest != entry.sha256:
            _fail(
                "RX048_NATIVE_CACHE_QUARANTINED",
                "provider_ready.native_image", "bind-time cache facts drifted")
        return _ProviderReadyNativeBinding(
            entry=entry,
            library_object=entry.library,
            cache_entry_identity=entry_identity,
            digest=entry.sha256,
            owner_pid=entry.owner_pid,
            source_path=Path(source_path),
            provenance_path=Path(provenance_path),
            image_descriptor=entry.image_descriptor,
            descriptor_identity=_native_descriptor_identity(
                entry.image_descriptor),
            image_seals=seals,
            loader_handle=handle,
            loader_alias=entry.loader_alias,
            binding_lease_id=library._rtdl_native_cache_lease_id,
        )


def _validate_provider_ready_native_binding(
    binding: _ProviderReadyNativeBinding,
    *, binding_library: _NativeLibraryLease,
) -> None:
    """Revalidate a provider capability without reopening its source path."""

    _native_image_cache_guard(
        code="RX047_NATIVE_CACHE_FORK_POISONED",
        identity_path="provider_ready.native_image")
    entry = binding.entry
    if not isinstance(binding_library, _NativeLibraryLease) \
            or binding_library._rtdl_native_image_released:
        _fail(
            "RX037_USE_AFTER_CLOSE", "provider_ready.native_image",
            "binding lease is released")
    if binding.owner_pid != os.getpid() \
            or binding.entry.owner_pid != os.getpid() \
            or binding_library._rtdl_native_cache_owner_pid != os.getpid():
        _fail(
            "RX047_NATIVE_CACHE_FORK_POISONED", "provider_ready.native_image",
            "provider cache entry belongs to a different process")
    cached = _NATIVE_IMAGE_CACHE.get(binding.digest)
    current_handle = int(getattr(entry.library, "_handle", 0))
    current_seals = _native_image_seals(
        entry.image_descriptor,
        code="RX048_NATIVE_CACHE_QUARANTINED",
        identity_path="provider_ready.native_image")
    if cached is not entry \
            or entry.library is not binding.library_object \
            or entry.sha256 != binding.digest \
            or f"{entry.owner_pid}:{entry.sha256}" != binding.cache_entry_identity \
            or not entry.usable or entry.load_failure is not None \
            or entry.image_descriptor != binding.image_descriptor \
            or _native_descriptor_identity(entry.image_descriptor) != \
                binding.descriptor_identity \
            or current_seals != binding.image_seals \
            or current_seals != entry.image_seals \
            or current_seals & 15 != 15 \
            or current_handle != binding.loader_handle or current_handle <= 0 \
            or entry.loader_alias != binding.loader_alias \
            or binding_library._rtdl_native_cache_entry is not entry \
            or binding_library._rtdl_native_cache_entry_identity != \
                binding.cache_entry_identity \
            or binding_library._rtdl_native_cache_key != binding.digest \
            or binding_library._rtdl_native_cache_owner_pid != binding.owner_pid \
            or Path(binding_library._rtdl_native_cache_source_path) != \
                binding.source_path \
            or binding_library._rtdl_loaded_library_sha256 != binding.digest \
            or binding_library._rtdl_native_cache_lease_id != \
                binding.binding_lease_id \
            or binding.binding_lease_id not in entry.active_lease_ids:
        _fail(
            "RX048_NATIVE_CACHE_QUARANTINED", "provider_ready.native_image",
            "sealed cache-entry identity, handle, seals, or PID drifted")


def _register_native_image_lease_frozen_provenance(
    library: _NativeLibraryLease, *, provenance_path: Path, digest: str,
) -> None:
    """Register bind-time resolved provenance without resolving a later path."""

    # The ordinary loader intentionally resolves a caller path at its one
    # verification boundary.  Provider-ready prepare must not repeat that
    # resolution after a directory or symlink spelling could have changed, so
    # publish the already frozen row under the same registry invariants.
    from . import physical_execution_provenance as provenance  # pylint: disable=import-outside-toplevel
    frozen_path = Path(provenance_path)
    exact_digest = _require_sha(digest, "provider_ready.provenance.sha256")
    key = id(library)
    with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
        current = provenance._LOADED_PROVIDER_IDENTITIES.get(key)
        if current is not None:
            current_library, current_path, current_digest = current
            if current_library is not library \
                    or current_path != frozen_path \
                    or current_digest != exact_digest:
                _fail(
                    "RX048_NATIVE_CACHE_QUARANTINED",
                    "provider_ready.provenance", "lease provenance changed")
            return
        provenance._LOADED_PROVIDER_IDENTITIES[key] = (
            library, frozen_path, exact_digest)


def _admit_provider_ready_native_image_lease(
    binding: _ProviderReadyNativeBinding,
    *, binding_library: _NativeLibraryLease,
    lease_handoff: _NativeImageLeaseHandoff | None = None,
) -> _NativeLibraryLease:
    """Acquire one independent owner lease from an exact provider binding."""

    library = None
    try:
        with _NATIVE_IMAGE_CACHE_LOCK:
            _validate_provider_ready_native_binding(
                binding, binding_library=binding_library)
            library = _acquire_native_image_lease(
                binding.entry, source_path=binding.source_path)
        _register_native_image_lease_frozen_provenance(
            library, provenance_path=binding.provenance_path,
            digest=binding.digest)
        _native_image_lease_handoff(library)
        if lease_handoff is not None:
            lease_handoff.publish(library)
        return library
    except BaseException:
        if isinstance(library, _NativeLibraryLease) \
                and not library._rtdl_native_image_released:
            _release_native_library_image(library)
        raise


def _register_native_image_lease_provenance(
    library: _NativeLibraryLease, *, source_path: Path, digest: str,
) -> None:
    from .physical_execution_provenance import (  # pylint: disable=import-outside-toplevel
        _register_loaded_provider_identity,
    )
    _register_loaded_provider_identity(library, source_path, digest)


def _native_image_lease_handoff(library: _NativeLibraryLease) -> None:
    """Injection point immediately before a verified lease is returned."""


def _native_image_cache_snapshot() -> dict[str, dict[str, object]]:
    """Return primitive cache state for untimed internal verification."""

    with _NATIVE_IMAGE_CACHE_LOCK:
        return {
            digest: {
                "entry_identity": f"{entry.owner_pid}:{digest}",
                "owner_pid": entry.owner_pid,
                "image_descriptor": entry.image_descriptor,
                "image_seals": entry.image_seals,
                "loader_alias": entry.loader_alias,
                "active_lease_count": len(entry.active_lease_ids),
                "acquisition_count": entry.acquisition_count,
                "first_source_path": str(entry.source_path),
                "loader_handle": int(getattr(entry.library, "_handle", 0)),
                "usable": entry.usable,
                "load_failure": entry.load_failure,
            }
            for digest, entry in sorted(_NATIVE_IMAGE_CACHE.items())
        }


def _native_image_seals(
    descriptor: int, *, code: str, identity_path: str,
) -> int:
    try:
        import fcntl  # pylint: disable=import-outside-toplevel
        return int(fcntl.fcntl(descriptor, fcntl.F_GET_SEALS))
    except (AttributeError, ImportError, OSError) as error:
        _fail(code, identity_path, f"Linux native-image seals unavailable: {error}")


def _sealed_native_image_descriptor(
    native_bytes: bytes, *, expected_sha256: str, code: str, identity_path: str,
) -> tuple[int, int]:
    if os.name != "posix" or not Path("/proc/self/fd").is_dir() \
            or not hasattr(os, "memfd_create"):
        _fail(code, identity_path,
              "secure Linux memfd/procfs native loading is unavailable")
    try:
        import fcntl  # pylint: disable=import-outside-toplevel
        required_seals = (
            fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW |
            fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL)
        flags = int(getattr(os, "MFD_CLOEXEC")) | int(
            getattr(os, "MFD_ALLOW_SEALING"))
        descriptor = os.memfd_create(
            f"rtdl-native-{expected_sha256[:16]}", flags)
    except (AttributeError, ImportError, OSError) as error:
        _fail(code, identity_path, f"sealed memfd creation failed: {error}")
    try:
        written = 0
        while written < len(native_bytes):
            count = os.write(descriptor, native_bytes[written:])
            if count <= 0:
                _fail(code, identity_path, "sealed memfd write made no progress")
            written += count
        os.fsync(descriptor)
        fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, required_seals)
        observed_seals = _native_image_seals(
            descriptor, code=code, identity_path=identity_path)
        if observed_seals & required_seals != required_seals:
            _fail(code, identity_path, "sealed memfd lacks required seals")
        copied_bytes, _ = _read_descriptor_bytes(
            descriptor, code=code, path=Path(identity_path))
        if not hmac.compare_digest(_sha_bytes(copied_bytes), expected_sha256) \
                or not hmac.compare_digest(copied_bytes, native_bytes):
            _fail(code, identity_path, "sealed memfd bytes differ from verified source")
        return descriptor, required_seals
    except BaseException:
        os.close(descriptor)
        raise


def _create_unique_native_loader_alias(
    descriptor: int, *, observed_sha256: str, code: str, identity_path: str,
) -> tuple[Path, Path]:
    directory: Path | None = None
    try:
        directory = Path(tempfile.mkdtemp(
            prefix=f"rtdl-native-{os.getpid()}-"))
        os.chmod(directory, 0o700)
        alias = directory / f"image-{observed_sha256}.so"
        with _NATIVE_ALIAS_LOCK:
            spelling = str(alias)
            if spelling in _NATIVE_ALIAS_PATHS_SEEN:
                _fail(code, identity_path, "native loader alias spelling was reused")
            _NATIVE_ALIAS_PATHS_SEEN.add(spelling)
        os.symlink(f"/proc/self/fd/{descriptor}", alias)
        return directory, alias
    except (OSError, RTDLExecutableError) as error:
        if directory is not None:
            try:
                directory.rmdir()
            except OSError:
                pass
        if isinstance(error, RTDLExecutableError):
            raise
        _fail(code, identity_path, f"private native loader alias failed: {error}")


def _remove_native_loader_alias(
    alias: Path, directory: Path, *, code: str, identity_path: str,
) -> None:
    try:
        alias.unlink()
        directory.rmdir()
    except OSError as error:
        _fail(code, identity_path, f"private native loader alias cleanup failed: {error}")


def _release_native_library_image(library: object) -> None:
    """Release one lease while retaining its sealed DSO cache entry.

    Public owner close has already destroyed the prepared native token and
    cleared every owner-held function pointer before entering here.  This
    function unregisters the per-lease provenance identity and removes exactly
    one active lease id.  It intentionally does *not* call ``dlclose`` or close
    the cache-owned memfd: arbitrary CUDA/OptiX DSO teardown caused process-exit
    crashes, while process-lifetime retention bounds the mapping to one per
    distinct content digest.  ``release_started`` remains a sticky audit marker,
    while the explicit release phase is resumable.  Because every step is pure
    Python bookkeeping and idempotent, a later close may resume after
    ``BaseException`` at any publication boundary without making a partial
    release look successfully closed.
    """

    if library is None:
        return
    if getattr(library, "_rtdl_native_image_released", False) is True \
            and getattr(library, "_rtdl_native_image_release_phase", None) \
                == "COMPLETE" \
            and getattr(library, "_rtdl_native_image_release_error", None) is None:
        return

    if not isinstance(library, _NativeLibraryLease):
        _fail(
            "RX046_NATIVE_RELEASE_INCOMPLETE", "native.close",
            "native image object is not a cache lease",
        )
    entry = library._rtdl_native_cache_entry
    lease_id = library._rtdl_native_cache_lease_id
    if library._rtdl_native_cache_owner_pid != os.getpid() \
            or entry.owner_pid != os.getpid():
        _fail("RX047_NATIVE_CACHE_FORK_POISONED", "native.close",
              "native lease belongs to a different process")

    library._rtdl_native_image_release_started = True
    try:
        if library._rtdl_native_image_release_phase == "ACTIVE":
            from .physical_execution_provenance import (  # pylint: disable=import-outside-toplevel
                _unregister_loaded_provider_identity,
            )
            _unregister_loaded_provider_identity(library)
            library._rtdl_native_image_release_phase = "PROVENANCE_UNREGISTERED"
        if library._rtdl_native_image_release_phase == "PROVENANCE_UNREGISTERED":
            _remove_native_cache_lease(entry, lease_id)
            library._rtdl_native_image_release_phase = "LEASE_REMOVED"
        if library._rtdl_native_image_release_phase in {
                "LEASE_REMOVED", "COMPLETE"}:
            _complete_native_cache_lease_release(library)
    except BaseException as error:
        library._rtdl_native_image_release_error = repr(error)
        raise


def _remove_native_cache_lease(
    entry: _NativeImageCacheEntry, lease_id: int,
) -> None:
    """Idempotently remove one lease id from its retained cache entry."""

    with _NATIVE_IMAGE_CACHE_LOCK:
        _native_image_cache_release_guard()
        cached = _NATIVE_IMAGE_CACHE.get(entry.sha256)
        if cached is not entry:
            _fail("RX046_NATIVE_RELEASE_INCOMPLETE", "native.close",
                  "native cache entry identity changed")
        entry.active_lease_ids.discard(lease_id)


def _native_image_cache_release_guard() -> None:
    """Allow cleanup during load quarantine, but never across a fork."""

    if _NATIVE_IMAGE_CACHE_FORK_POISONED \
            or _NATIVE_IMAGE_CACHE_PID != os.getpid():
        _fail("RX047_NATIVE_CACHE_FORK_POISONED", "native.close",
              "native lease belongs to a different process")


def _complete_native_cache_lease_release(library: _NativeLibraryLease) -> None:
    """Publish the final release state in a retry-safe order."""

    library._rtdl_native_image_release_phase = "COMPLETE"
    finalizer = getattr(library, "_rtdl_native_lease_abandon_finalizer", None)
    if finalizer is not None and getattr(finalizer, "alive", False):
        finalizer.detach()
    library._rtdl_native_image_release_error = None
    library._rtdl_native_image_released = True


def _boxes(values: Sequence[Sequence[object]], path: str):
    if not values:
        _fail("RX006_INPUT_INVALID", path, "nonempty boxes required")
    flat: list[float] = []; ids: list[int] = []
    for index, row in enumerate(values):
        if len(row) != 5:
            _fail("RX006_INPUT_INVALID", f"{path}[{index}]", "(x0,y0,x1,y1,id) required")
        try:
            x0, y0, x1, y1 = tuple(_require_f32(
                item, f"{path}[{index}][{axis}]", code="RX006_INPUT_INVALID")
                for axis, item in enumerate(row[:4]))
            item_id = _require_uint(
                row[4], f"{path}[{index}][4]", bits=32,
                code="RX006_INPUT_INVALID")
        except (TypeError, ValueError, OverflowError) as error:
            _fail("RX006_INPUT_INVALID", f"{path}[{index}]", error)
        if not all(math.isfinite(item) for item in (x0, y0, x1, y1)) \
                or x0 > x1 or y0 > y1 or not 0 <= item_id < 1 << 32:
            _fail("RX006_INPUT_INVALID", f"{path}[{index}]", row)
        flat.extend((x0, y0, x1, y1)); ids.append(item_id)
    return (ctypes.c_float * len(flat))(*flat), (ctypes.c_uint32 * len(ids))(*ids)


def _open_audit(library):
    from .physical_execution_provenance import OptixTraversalAuditSession
    return OptixTraversalAuditSession.open(library=library)


def _validate_product_summary(
    summary: _ProductStatusSummary, counters: Sequence[int], *, launch_count: int,
    terminal_invocation_mask: int,
) -> tuple[Mapping[str, object], tuple[int, ...]]:
    counter_rows = tuple(int(item) for item in counters)
    summary_counters = tuple(int(item) for item in summary.role_counters)
    if int(summary.schema_version) != 2 or int(summary.ok) != 1 \
            or int(summary.first_error_claimed) != 0 \
            or int(summary.error_code) != 0 \
            or int(summary.validated_row_count) != launch_count \
            or int(summary.required_invocation_mask) != ((1 << 1) | (1 << 6)) \
            or int(summary.terminal_invocation_mask) != terminal_invocation_mask \
            or int(summary.invalid_row_count) != 0 \
            or int(summary.first_invalid_row) != (1 << 64) - 1 \
            or int(summary.success_status_d2h_bytes) != ctypes.sizeof(_ProductStatusSummary) \
            or len(counter_rows) != 7 or counter_rows != summary_counters \
            or counter_rows[1] != launch_count \
            or counter_rows[6] != launch_count \
            or counter_rows[4] + counter_rows[5] != launch_count:
        _fail("RX035_DEVICE_STATUS_INVALID", "execute.product_status", {
            "schema_version": int(summary.schema_version),
            "ok": int(summary.ok),
            "first_error_claimed": int(summary.first_error_claimed),
            "error_code": int(summary.error_code),
            "validated_row_count": int(summary.validated_row_count),
            "invalid_row_count": int(summary.invalid_row_count),
            "first_invalid_row": int(summary.first_invalid_row),
            "role_counters": summary_counters,
            "returned_counters": counter_rows,
        })
    status = {
        "schema": _STATUS_SCHEMA,
        "ok": True,
        "first_error_claimed": 0,
        "error_code": 0,
        "validated_row_count": launch_count,
        "invalid_row_count": 0,
        "required_invocation_mask": int(summary.required_invocation_mask),
        "terminal_invocation_mask": int(summary.terminal_invocation_mask),
        "success_status_d2h_bytes": ctypes.sizeof(_ProductStatusSummary),
    }
    return status, counter_rows


def _validate_fast_operation_receipt(
    receipt: _FastPathReceipt, *, family: str, compact_status: int,
    expected_output_d2h_bytes: int, expected_prepared_input_reused: bool,
    expected_semantic_capacity: int | None = None,
    online_monitor: bool = False, lean_monitor: bool = False,
) -> Mapping[str, object]:
    """Validate the host receipt emitted at the actual native call sites.

    This receipt is not a substitute for device status.  The compact status is
    produced by a device finalizer after the full product summary and role
    counters have been checked.  The receipt records only which transfers and
    host-blocking boundaries the native owner actually executed around that
    status gate.
    """

    expected_launches = 2 if family == _BOUNDED else 1
    expected_control = (
        (28 if family == _BOUNDED else (12 if lean_monitor else 88))
        if online_monitor else (16 if family == _BOUNDED else 4))
    success = compact_status == 0
    # These ABI fields are uint32 booleans, not merely truthy integers.  Keep
    # their raw values until after domain validation so a corrupt value such as
    # 2 cannot be laundered into True by bool(...).
    raw_status_before_output = int(receipt.status_before_output)
    raw_role_counters_materialized = int(receipt.role_counters_materialized)
    raw_prepared_input_reused = int(receipt.prepared_input_reused)
    observed_output = int(receipt.output_d2h_bytes)
    values = {
        "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
        "optix_launch_count": int(receipt.optix_launch_count),
        "host_blocking_boundary_count": int(
            receipt.host_blocking_boundary_count),
        "control_d2h_bytes": int(receipt.control_d2h_bytes),
        "output_d2h_bytes": observed_output,
        "status_before_output": bool(raw_status_before_output),
        "output_d2h_after_status_failure": int(
            receipt.output_d2h_after_status_failure),
        "role_counters_materialized": bool(
            raw_role_counters_materialized),
        "prepared_input_reused": bool(raw_prepared_input_reused),
        "dynamic_device_upload_call_count": int(
            receipt.dynamic_device_upload_call_count),
        "dynamic_device_upload_bytes": int(
            receipt.dynamic_device_upload_bytes),
        "dynamic_accel_build_count": int(receipt.dynamic_accel_build_count),
        "dynamic_explicit_sync_count": int(
            receipt.dynamic_explicit_sync_count),
        "dynamic_blocking_upload_call_count": int(
            receipt.dynamic_blocking_upload_call_count),
        "dynamic_input_generation": int(receipt.dynamic_input_generation),
        "semantic_compaction_launch_count": int(
            receipt.semantic_compaction_launch_count),
        "semantic_compaction_key_capacity": int(
            receipt.semantic_compaction_key_capacity),
        "semantic_compaction_scratch_bytes": int(
            receipt.semantic_compaction_scratch_bytes),
        "callback_status_kernel_launch_count": int(
            receipt.callback_status_kernel_launch_count),
        "checked_product_kernel_launch_count": int(
            receipt.checked_product_kernel_launch_count),
        "compact_control_finalizer_kernel_launch_count": int(
            receipt.compact_control_finalizer_kernel_launch_count),
        "total_auxiliary_cuda_kernel_launch_count": int(
            receipt.total_auxiliary_cuda_kernel_launch_count),
        "execution_parameter_h2d_bytes": int(
            receipt.execution_parameter_h2d_bytes),
        "execution_parameter_h2d_copy_call_count": int(
            receipt.execution_parameter_h2d_copy_call_count),
        "stream_ordered_memset_call_count": int(
            receipt.stream_ordered_memset_call_count),
        "status_d2h_copy_call_count": int(
            receipt.status_d2h_copy_call_count),
        "output_d2h_copy_call_count": int(
            receipt.output_d2h_copy_call_count),
    }
    if family == _BOUNDED:
        if type(expected_semantic_capacity) is not int \
                or expected_semantic_capacity <= 0:
            _fail("RX035_DEVICE_STATUS_INVALID",
                  "execute.fast_operation_receipt.semantic_capacity",
                  expected_semantic_capacity)
        expected_key_capacity = 1
        while expected_key_capacity < 2 * expected_semantic_capacity:
            expected_key_capacity <<= 1
        expected_compaction = {
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": expected_key_capacity,
            "semantic_compaction_scratch_bytes": (
                8 * expected_key_capacity
                + 8 * expected_semantic_capacity
                + 2 * ctypes.sizeof(ctypes.c_uint32)),
            "callback_status_kernel_launch_count": 0 if online_monitor else 5,
            "checked_product_kernel_launch_count": 0,
            "compact_control_finalizer_kernel_launch_count": 0 if online_monitor else 1,
            "total_auxiliary_cuda_kernel_launch_count": 1 if online_monitor else 7,
            "execution_parameter_h2d_bytes": 240 if online_monitor else 224,
            "execution_parameter_h2d_copy_call_count": 2,
            "stream_ordered_memset_call_count": 4 if online_monitor else 9,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": (
                1 if success and expected_output_d2h_bytes > 0 else 0),
        }
    else:
        if expected_semantic_capacity is not None:
            _fail("RX035_DEVICE_STATUS_INVALID",
                  "execute.fast_operation_receipt.semantic_capacity",
                  expected_semantic_capacity)
        expected_compaction = {
            "semantic_compaction_launch_count": 0,
            "semantic_compaction_key_capacity": 0,
            "semantic_compaction_scratch_bytes": 0,
            "callback_status_kernel_launch_count": 0 if online_monitor else 3,
            "checked_product_kernel_launch_count": 0 if online_monitor else 2,
            "compact_control_finalizer_kernel_launch_count": 0 if online_monitor else 1,
            "total_auxiliary_cuda_kernel_launch_count": 0 if online_monitor else 6,
            "execution_parameter_h2d_bytes": 224 if online_monitor else 200,
            "execution_parameter_h2d_copy_call_count": 1,
            "stream_ordered_memset_call_count": 2 if online_monitor else 4,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1 if success else 0,
        }
    dynamic_zero = values["prepared_input_reused"] is True
    expected_dynamic_zero = (
        values["dynamic_device_upload_call_count"] == 0
        and values["dynamic_device_upload_bytes"] == 0
        and values["dynamic_accel_build_count"] == 0
        and values["dynamic_explicit_sync_count"] == 0
        and values["dynamic_blocking_upload_call_count"] == 0
    )
    expected_boundaries = (
        (2 if success else 1)
        + values["dynamic_blocking_upload_call_count"]
        + values["dynamic_explicit_sync_count"]
    )
    expected_role_counters_materialized = int(
        online_monitor and not lean_monitor and family == _TRIANGLE)
    if int(receipt.schema_version) != 2 \
            or ctypes.sizeof(_FastPathReceipt) != 128 \
            or raw_status_before_output not in (0, 1) \
            or raw_role_counters_materialized not in (0, 1) \
            or raw_prepared_input_reused not in (0, 1) \
            or raw_status_before_output != 1 \
            or raw_role_counters_materialized \
                != expected_role_counters_materialized \
            or raw_prepared_input_reused \
                != int(expected_prepared_input_reused) \
            or values["optix_launch_count"] != expected_launches \
            or values["control_d2h_bytes"] != expected_control \
            or values["status_before_output"] is not True \
            or values["role_counters_materialized"] is not bool(
                expected_role_counters_materialized) \
            or values["prepared_input_reused"] is not expected_prepared_input_reused \
            or values["dynamic_input_generation"] <= 0 \
            or any(values[key] != expected
                   for key, expected in expected_compaction.items()) \
            or dynamic_zero is not expected_dynamic_zero \
            or not 0 <= values["dynamic_blocking_upload_call_count"] \
                <= values["dynamic_device_upload_call_count"] \
            or (not dynamic_zero and (
                values["dynamic_device_upload_call_count"] <= 0
                or values["dynamic_device_upload_bytes"] <= 0
                or (family == _BOUNDED and (
                    values["dynamic_accel_build_count"] != 1
                    or values["dynamic_explicit_sync_count"] != 0
                    or values["dynamic_blocking_upload_call_count"] != 0))
                or (family == _TRIANGLE and (
                    values["dynamic_accel_build_count"] != 0
                    or values["dynamic_explicit_sync_count"] != 0
                    or values["dynamic_blocking_upload_call_count"] != 0)))) \
            or values["output_d2h_after_status_failure"] != 0 \
            or values["host_blocking_boundary_count"] != expected_boundaries \
            or observed_output != (expected_output_d2h_bytes if success else 0):
        _fail("RX035_DEVICE_STATUS_INVALID", "execute.fast_operation_receipt", {
            **values, "compact_status": compact_status,
            "expected_output_d2h_bytes": expected_output_d2h_bytes,
        })
    # Forensic sealing belongs outside a timed application execute.  The
    # immutable field projection is returned directly; diagnostics or the
    # worker may hash it after the timer closes.
    return MappingProxyType(dict(values))


def _bounded_compact_capacity_failure(
    *, raw_event_count: int | None, unique_event_count: int | None,
    overflowed: int | None, semantic_capacity: int | None,
    raw_event_capacity: int | None,
) -> tuple[bool, Mapping[str, object]]:
    """Validate the fixed relation control without touching its receipt."""

    control = {
        "raw_event_count": raw_event_count,
        "unique_event_count": unique_event_count,
        "overflowed": overflowed,
        "semantic_capacity": semantic_capacity,
        "raw_event_capacity": raw_event_capacity,
    }
    if type(raw_event_count) is not int or raw_event_count < 0 \
            or raw_event_count > (1 << 32) - 1 \
            or type(unique_event_count) is not int \
            or unique_event_count < 0 \
            or unique_event_count > (1 << 32) - 1 \
            or type(overflowed) is not int or overflowed not in {0, 1} \
            or type(semantic_capacity) is not int \
            or semantic_capacity <= 0 \
            or type(raw_event_capacity) is not int \
            or raw_event_capacity <= 0 \
            or raw_event_capacity > 2 * semantic_capacity \
            or raw_event_capacity > (1 << 32) - 1 \
            or unique_event_count > min(raw_event_count, raw_event_capacity):
        _fail("RX035_DEVICE_STATUS_INVALID",
              "execute.compact_control", control)
    # This mirrors the native bounded-capacity finalizer exactly.  The
    # overflow bit also covers a bounded scratch/probe exhaustion for which
    # the two counters alone need not cross their public limits.
    return (
        overflowed == 1
        or raw_event_count > raw_event_capacity
        or unique_event_count > semantic_capacity,
        MappingProxyType(control),
    )


def _validated_compact_device_status(
    *, family: str, compact_status: int, launch_count: int,
    operation_receipt: Mapping[str, object], raw_event_count: int | None = None,
    unique_event_count: int | None = None,
    overflowed: int | None = None, semantic_capacity: int | None = None,
    raw_event_capacity: int | None = None,
) -> Mapping[str, object]:
    capacity_failure = False
    if family == _BOUNDED:
        capacity_failure, control = _bounded_compact_capacity_failure(
            raw_event_count=raw_event_count,
            unique_event_count=unique_event_count,
            overflowed=overflowed,
            semantic_capacity=semantic_capacity,
            raw_event_capacity=raw_event_capacity)
        if compact_status == _FAST_STATUS_CAPACITY_INVALID \
                and capacity_failure:
            # Before presenting an expected public capacity failure, validate
            # that native really observed status before output and transferred
            # no partial application result.  A forged/malformed receipt must
            # retain the stronger RX035 classification.
            dict(operation_receipt)
            _fail("RX041_OUTPUT_OVERFLOW", "bounded.output", control)
        if compact_status != 0 or capacity_failure:
            _fail("RX035_DEVICE_STATUS_INVALID", "execute.compact_status", {
                "compact_status": compact_status,
                "compact_control": control,
                "operation_receipt": dict(operation_receipt),
            })
    if compact_status != 0:
        _fail("RX035_DEVICE_STATUS_INVALID", "execute.compact_status", {
            "compact_status": compact_status,
            "operation_receipt": dict(operation_receipt),
        })
    control_bytes = int(operation_receipt["control_d2h_bytes"])
    dynamic_setup_boundaries = (
        int(operation_receipt["dynamic_blocking_upload_call_count"])
        + int(operation_receipt["dynamic_explicit_sync_count"])
    )
    status = {
        "schema": _STATUS_SCHEMA,
        "ok": True,
        "compact_status": 0,
        "validated_row_count": launch_count,
        "required_invocation_mask": (1 << 1) | (1 << 6),
        "terminal_invocation_mask": (
            (1 << 4) | (1 << 5) if family == _BOUNDED else (1 << 5)),
        "success_status_d2h_bytes": control_bytes,
        "success_host_blocking_boundary_count": int(
            operation_receipt["host_blocking_boundary_count"]),
        "status_output_host_blocking_boundary_count": 2,
        "dynamic_setup_host_blocking_boundary_count": dynamic_setup_boundaries,
        "dynamic_device_upload_call_count": operation_receipt[
            "dynamic_device_upload_call_count"],
        "dynamic_device_upload_bytes": operation_receipt[
            "dynamic_device_upload_bytes"],
        "dynamic_accel_build_count": operation_receipt[
            "dynamic_accel_build_count"],
        "dynamic_explicit_sync_count": operation_receipt[
            "dynamic_explicit_sync_count"],
        "dynamic_blocking_upload_call_count": operation_receipt[
            "dynamic_blocking_upload_call_count"],
        "dynamic_input_generation": operation_receipt[
            "dynamic_input_generation"],
        "role_counters_materialized": operation_receipt[
            "role_counters_materialized"],
        "fast_path_applied": True,
        "execution_path": (
            "application_fast_online_monitor_v1"
            if int(operation_receipt["callback_status_kernel_launch_count"]) == 0
            else "application_fast_v5"),
        "prepared_input_reused": operation_receipt["prepared_input_reused"],
        "operation_receipt": operation_receipt,
    }
    if raw_event_count is not None:
        status["validated_raw_event_count"] = raw_event_count
    if unique_event_count is not None:
        status["validated_unique_event_count"] = unique_event_count
    return MappingProxyType(status)


class _DeferredFastOperationReceipt(Mapping[str, object]):
    """Validate measurement-only native counters on first observation.

    The native execute already enforces the semantic status-before-output
    boundary.  The 128-byte receipt records how that boundary was traversed;
    expanding and validating its Python dictionary is measurement evidence,
    not application work.  Keeping the raw, per-call ctypes object alive lets
    a worker inspect the exact receipt after its primary timer closes without
    charging only RTDL for Python bookkeeping that the matched arms also emit
    after timing.
    """

    __slots__ = (
        "_receipt", "_family", "_compact_status",
        "_expected_output_d2h_bytes", "_expected_prepared_input_reused",
        "_expected_semantic_capacity", "_online_monitor", "_lean_monitor",
        "_materialized",
    )

    def __init__(
            self, receipt: _FastPathReceipt, *, family: str,
            compact_status: int, expected_output_d2h_bytes: int,
            expected_prepared_input_reused: bool,
            expected_semantic_capacity: int | None = None,
            online_monitor: bool = False, lean_monitor: bool = False) -> None:
        self._receipt = receipt
        self._family = family
        self._compact_status = compact_status
        self._expected_output_d2h_bytes = expected_output_d2h_bytes
        self._expected_prepared_input_reused = expected_prepared_input_reused
        self._expected_semantic_capacity = expected_semantic_capacity
        self._online_monitor = online_monitor
        self._lean_monitor = lean_monitor
        self._materialized: Mapping[str, object] | None = None

    def _get(self) -> Mapping[str, object]:
        if self._materialized is None:
            self._materialized = _validate_fast_operation_receipt(
                self._receipt, family=self._family,
                compact_status=self._compact_status,
                expected_output_d2h_bytes=self._expected_output_d2h_bytes,
                expected_prepared_input_reused=(
                    self._expected_prepared_input_reused),
                expected_semantic_capacity=self._expected_semantic_capacity,
                online_monitor=self._online_monitor,
                lean_monitor=self._lean_monitor)
        return self._materialized

    def __getitem__(self, key: str) -> object:
        return self._get()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._get())

    def __len__(self) -> int:
        return len(self._get())


class _DeferredCompactDeviceStatus(Mapping[str, object]):
    """Expose the semantic success bit eagerly and evidence lazily."""

    __slots__ = (
        "_family", "_launch_count", "_operation_receipt",
        "_raw_event_count", "_unique_event_count", "_extras",
        "_overflowed", "_semantic_capacity", "_raw_event_capacity",
        "_materialized",
    )

    def __init__(
        self, *, family: str, compact_status: int, launch_count: int,
        operation_receipt: Mapping[str, object],
        raw_event_count: int | None = None,
        unique_event_count: int | None = None,
        overflowed: int | None = None,
        semantic_capacity: int | None = None,
        raw_event_capacity: int | None = None,
        extras: Mapping[str, object] | None = None,
    ) -> None:
        # Failure must remain synchronous: a caller can never observe an
        # output from a failed device status merely by declining diagnostics.
        if compact_status != 0:
            _validated_compact_device_status(
                family=family, compact_status=compact_status,
                launch_count=launch_count,
                operation_receipt=operation_receipt,
                raw_event_count=raw_event_count,
                unique_event_count=unique_event_count,
                overflowed=overflowed,
                semantic_capacity=semantic_capacity,
                raw_event_capacity=raw_event_capacity)
            raise AssertionError("unreachable compact-status failure")
        if family == _BOUNDED:
            # Validate every structural relation synchronously, including on
            # the ordinary success path, before output can escape.  This is a
            # fixed-size integer check and deliberately does not materialize
            # the deferred operation receipt.
            bounded_capacity_failure, _control = (
                _bounded_compact_capacity_failure(
                    raw_event_count=raw_event_count,
                    unique_event_count=unique_event_count,
                    overflowed=overflowed,
                    semantic_capacity=semantic_capacity,
                    raw_event_capacity=raw_event_capacity))
            if bounded_capacity_failure:
                _validated_compact_device_status(
                    family=family, compact_status=compact_status,
                    launch_count=launch_count,
                    operation_receipt=operation_receipt,
                    raw_event_count=raw_event_count,
                    unique_event_count=unique_event_count,
                    overflowed=overflowed,
                    semantic_capacity=semantic_capacity,
                    raw_event_capacity=raw_event_capacity)
        self._family = family
        self._launch_count = launch_count
        self._operation_receipt = operation_receipt
        self._raw_event_count = raw_event_count
        self._unique_event_count = unique_event_count
        self._overflowed = overflowed
        self._semantic_capacity = semantic_capacity
        self._raw_event_capacity = raw_event_capacity
        self._extras = extras if extras is not None else MappingProxyType({})
        self._materialized: Mapping[str, object] | None = None

    def _get(self) -> Mapping[str, object]:
        if self._materialized is None:
            status = _validated_compact_device_status(
                family=self._family, compact_status=0,
                launch_count=self._launch_count,
                operation_receipt=self._operation_receipt,
                raw_event_count=self._raw_event_count,
                unique_event_count=self._unique_event_count,
                overflowed=self._overflowed,
                semantic_capacity=self._semantic_capacity,
                raw_event_capacity=self._raw_event_capacity)
            self._materialized = MappingProxyType({
                **dict(status), **self._extras})
        return self._materialized

    def __getitem__(self, key: str) -> object:
        # This is the sole field required by the timed public application path.
        # It is safe to expose because native has already returned a successful
        # compact status and withheld output on every failure path.
        if key == "ok":
            return True
        return self._get()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._get())

    def __len__(self) -> int:
        return len(self._get())


class _PreparedBoundedOwner:
    def __init__(self, *, library, native_path: Path, ptx: str,
                 runtime: Mapping[str, object],
                 static_input: BoundedRelationStaticInput |
                    BoundedRelationBufferStaticInput,
                 artifact_identity: str,
                 construction_handoff: _PreparedOwnerHandoff | None = None,
                 ) -> None:
        # Publish a minimally closable owner before the first operation that
        # can fail or create a native token.  The native prepare writes directly
        # into this zero-initialized token cell, so an asynchronous exception
        # after the external side effect remains recoverable by the caller.
        self._library = library
        self._token_cell = ctypes.c_uint64()
        self._token = 0
        self._destroy = None
        self._closed = False
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._release_complete = False
        self._close_failure = None
        if construction_handoff is not None:
            construction_handoff.publish(self)
        prepare = getattr(library, "rtdl_optix_v4_prepare_bounded_relation_callback_v1", None)
        abi_version = str(runtime["native_abi"]).rsplit(".", 1)[-1]
        self._online_monitor = abi_version in {"v6", "v7"}
        self._lean_monitor = abi_version == "v7"
        execute_fast = getattr(
            library,
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_"
            + (abi_version if self._online_monitor else "v5"), None)
        execute_diagnostic = getattr(
            library, "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v4", None)
        build_count = getattr(
            library,
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_build_count_v1",
            None,
        )
        commit = getattr(
            library,
            "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2",
            None,
        )
        cache_digest = getattr(
            library,
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1",
            None,
        )
        destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v2", None)
        if any(symbol is None for symbol in (
                prepare, execute_fast, execute_diagnostic, build_count,
                commit, cache_digest, destroy)):
            _fail(
                "RX036_NATIVE_ABI_MISSING", "native.bounded_relation",
                "prepare/execute-v5/diagnostic-v4/build_count/commit/destroy-v2")
        prepare.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.c_float,
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        execute_fast.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_FastPathReceipt),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        execute_diagnostic.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(_ProductStatusSummary), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        build_count.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64),
                                ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        commit.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8),
                           ctypes.c_size_t, ctypes.POINTER(ctypes.c_char),
                           ctypes.c_size_t]
        cache_digest.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8),
                                 ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        destroy.argtypes = [ctypes.POINTER(ctypes.c_uint64),
                            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        for symbol in (
                prepare, execute_fast, execute_diagnostic, build_count,
                commit, cache_digest, destroy):
            symbol.restype = ctypes.c_int
        if isinstance(static_input, BoundedRelationBufferStaticInput):
            self._indexed_count = static_input.indexed_count
            indexed = (ctypes.c_float * (len(static_input._packed_bounds_f32) // 4)).from_buffer_copy(
                static_input._packed_bounds_f32)
            indexed_ids = (ctypes.c_uint32 * self._indexed_count).from_buffer_copy(
                static_input._packed_ids_u32)
        else:
            indexed, indexed_ids = _boxes(
                static_input.indexed_boxes, "static.indexed_boxes")
            self._indexed_count = len(static_input.indexed_boxes)
        self._capacity = int(runtime["capacity"])
        # Retain the exact normalized scalar that is passed to the native
        # prepared owner.  This is evidence-only state: it does not change the
        # public API or execution value, but lets an untimed verifier prove
        # that the executed threshold is the sealed product threshold rather
        # than merely trusting the product projection.
        self._minimum_overlap = float(runtime["minimum_overlap_f32"])
        self._execute_fast = execute_fast
        self._execute_diagnostic = execute_diagnostic
        self._build_count = build_count; self._commit = commit
        self._cache_digest = cache_digest
        self._destroy = destroy
        self._native_sha = _require_sha(
            getattr(library, "_rtdl_loaded_library_sha256", None),
            "native.loaded_library_sha256")
        self._ptx = ptx
        self._ptx_sha = _sha_bytes(ptx.encode()); self._artifact_identity = artifact_identity
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(prepare(
            ptx.encode(), indexed, indexed_ids, self._indexed_count,
            self._minimum_overlap, self._capacity,
            ctypes.byref(self._token_cell), error, len(error))),
            error, "bounded.prepare")
        if not self._token_cell.value:
            _fail("RX030_NATIVE_FAILURE", "bounded.prepare", "zero token")
        self._token = int(self._token_cell.value)
        # This flag closes the token+lease lifetime only.  The sealed DSO cache
        # entry is intentionally process-lifetime and is not claimed unmapped.
        self._last_batch_key = None
        self._last_source_arrays = None
        self._last_fast_operation_receipt = None
        # Evidence harnesses may inspect the exact compact control returned by
        # the native call after a public failure.  This remains private: the
        # application API still exposes only accepted device status/results.
        self._last_fast_compact_control = None
        # The owner is thread-bound and rejects reentrancy, so successful calls
        # can reuse fixed ABI storage.  Native already returns canonical packed
        # rows; retaining their immutable Python decoding avoids rebuilding
        # thousands of identical tuples for a repeated prepared batch.
        self._row_storage = (ctypes.c_uint32 * (self._capacity * 2))()
        self._fast_raw_count = ctypes.c_uint64()
        self._fast_unique_count = ctypes.c_uint64()
        self._fast_overflowed = ctypes.c_uint32()
        self._fast_compact_status = ctypes.c_uint32()
        self._call_error = ctypes.create_string_buffer(16384)
        self._cached_output_packed: bytes | None = None
        self._cached_output_rows: tuple[tuple[int, int], ...] | None = None
        self._cached_output_sha: str | None = None

    def _native_source_build_count(self) -> int:
        count = ctypes.c_uint64()
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(self._build_count(
            self._token, ctypes.byref(count), error, len(error))),
            error, "bounded.source_cache_build_count")
        return int(count.value)

    def _commit_source_cache(self, digest_hex: str) -> None:
        digest = (ctypes.c_uint8 * 32).from_buffer_copy(bytes.fromhex(digest_hex))
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(self._commit(
            self._token, digest, 32, error, len(error))), error,
            "bounded.source_cache_commit")

    def _native_source_cache_digest(self) -> str | None:
        digest = (ctypes.c_uint8 * 32)(); present = ctypes.c_uint32()
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(self._cache_digest(
            self._token, digest, 32, ctypes.byref(present), error, len(error))),
            error, "bounded.source_cache_digest")
        return bytes(digest).hex() if present.value else None

    def _source_cache_reusable(self, batch_key, digest_hex: str) -> bool:
        return (batch_key == self._last_batch_key
                and self._last_source_arrays is not None
                and self._native_source_cache_digest() == digest_hex)

    def _check(self) -> None:
        if self._closed: _fail("RX037_USE_AFTER_CLOSE", "prepared", "closed")
        if os.getpid() != self._pid: _fail("RX038_PROCESS_BOUNDARY", "prepared", "different process")
        if threading.get_ident() != self._thread: _fail("RX039_THREAD_BOUNDARY", "prepared", "different thread")

    def _publish_destroyed_token(self) -> None:
        self._token = int(self._token_cell.value)
        if self._token != 0:
            return
        # Publish ``closed`` only after all owner-held raw addresses have been
        # cleared.  If BaseException interrupts this Python sequence, the
        # native-zero token cell makes the same publication retryable without
        # a second native destroy.
        self._execute_fast = None; self._execute_diagnostic = None
        self._build_count = None
        self._commit = None; self._cache_digest = None; self._destroy = None
        self._closed = True

    def _destroy_native_token(self) -> None:
        if self._token_cell.value == 0:
            self._publish_destroyed_token()
            return
        error = ctypes.create_string_buffer(16384)
        try:
            status = int(self._destroy(
                ctypes.byref(self._token_cell), error, len(error)))
            _raise_native(status, error, "bounded.close")
        finally:
            self._publish_destroyed_token()

    def execute(
            self,
            batch: BoundedRelationBatch | BoundedRelationBufferBatch,
            *, diagnostics: bool):
        self._check()
        if not self._active.acquire(blocking=False): _fail("RX040_REENTRANT", "execute", "active")
        try:
            source_count = (batch.source_count
                            if isinstance(batch, BoundedRelationBufferBatch)
                            else len(batch.source_boxes))
            # This exactly mirrors the native bounded owner.  Each Cartesian
            # pair can emit once in each of two diagonal passes, while the
            # semantic design never needs more than 2*K raw rows.  Small
            # source/indexed domains therefore have a raw capacity below 2*K.
            raw_event_capacity = min(
                2 * self._capacity,
                2 * source_count * self._indexed_count)
            batch_key = (batch._device_input_sha256, source_count,
                         len(batch._packed_bounds_f32), len(batch._packed_ids_u32))
            reused = self._source_cache_reusable(
                batch_key, batch._device_input_sha256)
            if reused:
                sources, source_ids = self._last_source_arrays
            else:
                sources = (ctypes.c_float * (len(batch._packed_bounds_f32) // 4)).from_buffer_copy(
                    batch._packed_bounds_f32)
                source_ids = (ctypes.c_uint32 * (len(batch._packed_ids_u32) // 4)).from_buffer_copy(
                    batch._packed_ids_u32)
            rows_native = self._row_storage
            if diagnostics:
                raw_count = ctypes.c_uint64()
                unique_count = ctypes.c_uint64()
                overflowed = ctypes.c_uint32()
                summary = _ProductStatusSummary()
                counters = (ctypes.c_uint64 * 7)()
                compact_status = ctypes.c_uint32()
                error = ctypes.create_string_buffer(16384)
            else:
                raw_count = self._fast_raw_count
                unique_count = self._fast_unique_count
                overflowed = self._fast_overflowed
                compact_status = self._fast_compact_status
                error = self._call_error
                error[0] = 0
            fast_receipt = _FastPathReceipt()
            audit = _open_audit(self._library) if diagnostics else None
            next_output_cache = None
            try:
                launch_count = source_count + self._indexed_count
                # Full role counters remain an explicit diagnostic request.
                # The application v5 path also handles a first batch, but its
                # receipt separately accounts for every dynamic upload, GAS
                # build and explicit setup synchronization before the compact
                # status/output pair.
                if diagnostics:
                    native_build_count_before = self._native_source_build_count()
                    _raise_native(int(self._execute_diagnostic(
                        self._token, sources, source_ids, source_count,
                        int(reused), ctypes.byref(raw_count),
                        ctypes.byref(unique_count), ctypes.byref(overflowed),
                        rows_native, ctypes.byref(summary), counters,
                        error, len(error))), error, "bounded.execute_diagnostic")
                    native_build_count_after = self._native_source_build_count()
                    native_build_delta = (
                        native_build_count_after - native_build_count_before)
                    if native_build_delta != (0 if reused else 1):
                        _fail("RX044_NATIVE_REUSE_MISMATCH", "bounded.source_cache", {
                            "reuse_requested": reused,
                            "native_build_count_before": native_build_count_before,
                            "native_build_count_after": native_build_count_after,
                        })
                    status_value, counter_rows = _validate_product_summary(
                        summary, counters, launch_count=launch_count,
                        terminal_invocation_mask=(1 << 4) | (1 << 5))
                    status = {
                        **status_value,
                        "role_counters_materialized": True,
                        "role_counters_internally_materialized": True,
                        "fast_path_applied": False,
                        "execution_path": "diagnostic_v4",
                        "host_blocking_boundary_count_claimed": False,
                        "prepared_input_reused": native_build_delta == 0,
                        "validated_raw_event_count": int(raw_count.value),
                        "native_source_build_count_before": native_build_count_before,
                        "native_source_build_count_after": native_build_count_after,
                        "native_source_build_count_delta": native_build_delta,
                    }
                else:
                    self._last_fast_compact_control = None
                    _raise_native(int(self._execute_fast(
                        self._token, sources, source_ids, source_count,
                        int(reused), ctypes.byref(raw_count),
                        ctypes.byref(unique_count), ctypes.byref(overflowed),
                        rows_native, ctypes.byref(compact_status),
                        ctypes.byref(fast_receipt), error, len(error))),
                        error, "bounded.execute_fast")
                    self._last_fast_compact_control = MappingProxyType({
                        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
                        "raw_event_count": int(raw_count.value),
                        "unique_event_count": int(unique_count.value),
                        "overflowed": int(overflowed.value),
                        "status": int(compact_status.value),
                        "semantic_capacity": int(self._capacity),
                        "raw_event_capacity": int(raw_event_capacity),
                        "control_d2h_bytes": (
                            28 if getattr(self, "_online_monitor", False) else 16),
                    })
                    operation_receipt = _DeferredFastOperationReceipt(
                        fast_receipt, family=_BOUNDED,
                        compact_status=int(compact_status.value),
                        expected_output_d2h_bytes=int(unique_count.value) * 8,
                        expected_prepared_input_reused=reused,
                        expected_semantic_capacity=self._capacity,
                        online_monitor=getattr(self, "_online_monitor", False),
                        lean_monitor=getattr(self, "_lean_monitor", False))
                    self._last_fast_operation_receipt = operation_receipt
                    status = _DeferredCompactDeviceStatus(
                        family=_BOUNDED,
                        compact_status=int(compact_status.value),
                        launch_count=launch_count,
                        operation_receipt=operation_receipt,
                        raw_event_count=int(raw_count.value),
                        unique_event_count=int(unique_count.value),
                        overflowed=int(overflowed.value),
                        semantic_capacity=self._capacity,
                        raw_event_capacity=raw_event_capacity)
                    counter_rows = ()
                if overflowed.value or unique_count.value > self._capacity:
                    _fail("RX041_OUTPUT_OVERFLOW", "bounded.output", unique_count.value)
                # The trusted native boundary has already sorted and uniqued
                # these rows and checked its device-reported unique count.
                # Decode the contiguous ABI buffer in C instead of performing
                # thousands of scalar ctypes reads and a second Python
                # set/sort over an output that is already canonical.
                row_count = int(unique_count.value)
                packed_rows = ctypes.string_at(
                    ctypes.addressof(rows_native), row_count * 8)
                cached_rows_reused = (
                    packed_rows == self._cached_output_packed
                    and self._cached_output_rows is not None
                )
                if cached_rows_reused:
                    rows = self._cached_output_rows
                else:
                    rows = tuple(struct.iter_unpack("<II", packed_rows))
                if batch.expected_rows is not None and rows != tuple(sorted(batch.expected_rows)):
                    _fail("RX043_ORACLE_MISMATCH", "bounded.output", rows)
                if diagnostics:
                    output_sha = (
                        self._cached_output_sha
                        if cached_rows_reused
                        and self._cached_output_sha is not None
                        else _digest(rows)
                    )
                else:
                    output_sha = None
                if not cached_rows_reused or (
                    diagnostics and self._cached_output_sha is None
                ):
                    next_output_cache = (
                        packed_rows,
                        rows,
                        output_sha,
                    )
                receipt = None
                if diagnostics:
                    receipt = audit.finish(
                        semantic_digest=_digest({"artifact": self._artifact_identity,
                            "ptx": self._ptx_sha, "native": self._native_sha}),
                        output_digest=output_sha,
                        route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
                        expected_program_bundles=(
                            "v4_custom_aabb_bounded_relation_composed",))
                if not reused:
                    self._commit_source_cache(batch._device_input_sha256)
                self._last_batch_key = batch_key
                self._last_source_arrays = (sources, source_ids)
                if next_output_cache is not None:
                    (
                        self._cached_output_packed,
                        self._cached_output_rows,
                        self._cached_output_sha,
                    ) = next_output_cache
            # Asynchronous Python control-flow exits (KeyboardInterrupt,
            # SystemExit) must not strand a newly committed native generation
            # behind the preceding Python batch key.
            except BaseException:
                self._last_batch_key = None; self._last_source_arrays = None
                if audit is not None:
                    audit.abort()
                raise
            return rows, output_sha, status, counter_rows, receipt
        finally:
            self._active.release()

    def close(self) -> None:
        if self._closed:
            if self._release_complete:
                return
            if os.getpid() != self._pid:
                _fail("RX038_PROCESS_BOUNDARY", "prepared", "different process")
            if threading.get_ident() != self._thread:
                _fail("RX039_THREAD_BOUNDARY", "prepared", "different thread")
            if not self._active.acquire(blocking=False):
                _fail("RX040_REENTRANT", "close", "active")
            try:
                try:
                    _release_native_library_image(self._library)
                    self._release_complete = True
                    self._close_failure = None
                    self._library = None
                except BaseException as error:
                    self._close_failure = repr(error)
                    raise
            finally:
                self._active.release()
            return
        self._check()
        if not self._active.acquire(blocking=False): _fail("RX040_REENTRANT", "close", "active")
        try:
            self._destroy_native_token()
            if not self._closed:
                _fail("RX046_NATIVE_RELEASE_INCOMPLETE", "bounded.close",
                      "native destroy returned without zeroing its token cell")
            library = self._library
            try:
                _release_native_library_image(library)
                self._release_complete = True
                self._close_failure = None
                self._library = None
            except BaseException as error:
                self._close_failure = repr(error)
                raise
        finally:
            self._active.release()


class _PreparedTriangleOwner:
    def __init__(self, *, library, native_path: Path, ptx: str,
                 runtime: Mapping[str, object],
                 static_input: TriangleReductionStaticInput |
                    TriangleReductionBufferStaticInput,
                 artifact_identity: str,
                 construction_handoff: _PreparedOwnerHandoff | None = None,
                 ) -> None:
        self._library = library
        self._token_cell = ctypes.c_uint64()
        self._token = 0
        self._destroy = None
        self._closed = False
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._release_complete = False
        self._close_failure = None
        if construction_handoff is not None:
            construction_handoff.publish(self)
        prepare = getattr(library, "rtdl_optix_v4_prepare_triangle_reduction_callback_v1", None)
        abi_version = str(runtime["native_abi"]).rsplit(".", 1)[-1]
        self._online_monitor = abi_version in {"v6", "v7"}
        self._lean_monitor = abi_version == "v7"
        execute_fast = getattr(
            library,
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_"
            + (abi_version if self._online_monitor else "v5"), None)
        execute_diagnostic = getattr(
            library, "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v4", None)
        commit = getattr(
            library,
            "rtdl_optix_v4_commit_prepared_triangle_reduction_cache_v1",
            None,
        )
        cache_digest = getattr(
            library,
            "rtdl_optix_v4_prepared_triangle_reduction_cache_digest_v1",
            None,
        )
        destroy = getattr(library, "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v2", None)
        if any(item is None for item in (
                prepare, execute_fast, execute_diagnostic,
                commit, cache_digest, destroy)):
            _fail(
                "RX036_NATIVE_ABI_MISSING", "native.triangle",
                "prepare/execute-v5/diagnostic-v4/commit/cache_digest/destroy-v2")
        prepare.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        execute_fast_argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        if self._lean_monitor:
            execute_fast_argtypes.extend([
                ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t])
        execute_fast_argtypes.extend([
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(_FastPathReceipt),
            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t])
        # ctypes/libffi snapshots a function's call interface when argtypes is
        # assigned.  Mutating that list in place can leave a 32-bit converter
        # cached for the newly appended size_t and leak undefined high bits on
        # later calls.  Publish the complete ABI atomically.
        execute_fast.argtypes = execute_fast_argtypes
        execute_diagnostic.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_size_t,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(_ProductStatusSummary),
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        commit.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8),
                           ctypes.c_size_t, ctypes.POINTER(ctypes.c_char),
                           ctypes.c_size_t]
        cache_digest.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8),
                                 ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        destroy.argtypes = [ctypes.POINTER(ctypes.c_uint64),
                            ctypes.POINTER(ctypes.c_char), ctypes.c_size_t]
        for symbol in (
                prepare, execute_fast, execute_diagnostic,
                commit, cache_digest, destroy):
            symbol.restype = ctypes.c_int
        if isinstance(static_input, TriangleReductionBufferStaticInput):
            vertex_count = static_input.vertex_count
            triangle_count = static_input.triangle_count
        else:
            vertex_count = len(static_input.vertices)
            triangle_count = len(static_input.triangles)
        if not vertex_count or not triangle_count \
                or len(static_input._packed_vertices_f32) != 12 * vertex_count \
                or len(static_input._packed_triangles_u32) != 12 * triangle_count:
            _fail("RX006_INPUT_INVALID", "static.triangle", "nonempty arity-three geometry required")
        # TriangleReductionStaticInput has already normalized and range-checked
        # every leaf.  Consume its immutable packed projection rather than
        # repeating 98,304 Python scalar visits at the native boundary.
        vertices = (ctypes.c_float * (3 * vertex_count)).from_buffer_copy(
            static_input._packed_vertices_f32)
        triangles = (ctypes.c_uint32 * (3 * triangle_count)).from_buffer_copy(
            static_input._packed_triangles_u32)
        null_u64 = ctypes.POINTER(ctypes.c_uint64)(); null_i64 = ctypes.POINTER(ctypes.c_int64)()
        null_u32 = ctypes.POINTER(ctypes.c_uint32)()
        error = ctypes.create_string_buffer(16384)
        # Install the destroy function before native prepare can publish a
        # token into the caller-owned cell.
        self._destroy = destroy
        _raise_native(int(prepare(ptx.encode(), vertices, vertex_count,
            triangles, triangle_count, null_u64, null_i64, null_u32,
            static_input.event_capacity, ctypes.byref(self._token_cell),
            error, len(error))),
            error, "triangle.prepare")
        if not self._token_cell.value:
            _fail("RX030_NATIVE_FAILURE", "triangle.prepare", "zero token")
        self._token = int(self._token_cell.value)
        self._execute_fast = execute_fast
        self._execute_diagnostic = execute_diagnostic
        self._commit = commit; self._cache_digest = cache_digest
        self._event_capacity = static_input.event_capacity
        self._native_sha = _require_sha(
            getattr(library, "_rtdl_loaded_library_sha256", None),
            "native.loaded_library_sha256")
        self._ptx_sha = _sha_bytes(ptx.encode()); self._mode = str(runtime["triangle_mode"])
        self._artifact_identity = artifact_identity
        # Token+lease completion does not mean the process cache was unmapped.
        self._last_batch_key = None
        self._last_query_arrays = None
        self._last_fast_operation_receipt = None
        # The owner is process/thread bound and rejects reentrancy, so these
        # scalar/error ABI cells can be safely reused.  Allocating a fresh
        # 16-KiB error buffer and diagnostic-only structs on every successful
        # application execute is neither semantic work nor evidence.
        self._fast_reduced = ctypes.c_uint64()
        self._fast_compact_status = ctypes.c_uint32()
        self._call_error = ctypes.create_string_buffer(16384)

    def _commit_query_cache(self, digest_hex: str) -> None:
        digest = (ctypes.c_uint8 * 32).from_buffer_copy(bytes.fromhex(digest_hex))
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(self._commit(
            self._token, digest, 32, error, len(error))), error,
            "triangle.query_cache_commit")

    def _native_query_cache_digest(self) -> str | None:
        digest = (ctypes.c_uint8 * 32)(); present = ctypes.c_uint32()
        error = ctypes.create_string_buffer(16384)
        _raise_native(int(self._cache_digest(
            self._token, digest, 32, ctypes.byref(present), error, len(error))),
            error, "triangle.query_cache_digest")
        return bytes(digest).hex() if present.value else None

    def _query_cache_reusable(self, batch_key, digest_hex: str) -> bool:
        local_match = (batch_key == self._last_batch_key
                       and self._last_query_arrays is not None)
        if not local_match:
            return False
        if getattr(self, "_lean_monitor", False):
            # v7 validates this exact digest inside the execute call while
            # holding the same native owner lock; no separate TOCTOU-prone
            # digest query or blocking FFI boundary is needed.
            return True
        return self._native_query_cache_digest() == digest_hex

    def _check(self) -> None:
        if self._closed: _fail("RX037_USE_AFTER_CLOSE", "prepared", "closed")
        if os.getpid() != self._pid: _fail("RX038_PROCESS_BOUNDARY", "prepared", "different process")
        if threading.get_ident() != self._thread: _fail("RX039_THREAD_BOUNDARY", "prepared", "different thread")

    def _publish_destroyed_token(self) -> None:
        self._token = int(self._token_cell.value)
        if self._token != 0:
            return
        self._execute_fast = None; self._execute_diagnostic = None
        self._commit = None
        self._cache_digest = None; self._destroy = None
        self._closed = True

    def _destroy_native_token(self) -> None:
        if self._token_cell.value == 0:
            self._publish_destroyed_token()
            return
        error = ctypes.create_string_buffer(16384)
        try:
            status = int(self._destroy(
                ctypes.byref(self._token_cell), error, len(error)))
            _raise_native(status, error, "triangle.close")
        finally:
            self._publish_destroyed_token()

    def execute(
            self,
            batch: TriangleReductionBatch | TriangleReductionBufferBatch,
            *, diagnostics: bool):
        self._check()
        if not self._active.acquire(blocking=False): _fail("RX040_REENTRANT", "execute", "active")
        try:
            count = (batch.query_count
                     if isinstance(batch, TriangleReductionBufferBatch)
                     else len(batch.queries))
            batch_key = (batch._device_input_sha256, count,
                         len(batch._packed_origins_f32),
                         len(batch._packed_directions_f32),
                         len(batch._packed_tmax_f32),
                         len(batch._packed_weights_u64 or b""))
            reused = self._query_cache_reusable(
                batch_key, batch._device_input_sha256)
            if reused:
                origin_native, direction_native, tmax_native, multipliers = \
                    self._last_query_arrays
            else:
                origin_native = (ctypes.c_float * (len(batch._packed_origins_f32) // 4)).from_buffer_copy(
                    batch._packed_origins_f32)
                direction_native = (ctypes.c_float * (len(batch._packed_directions_f32) // 4)).from_buffer_copy(
                    batch._packed_directions_f32)
                tmax_native = (ctypes.c_float * count).from_buffer_copy(
                    batch._packed_tmax_f32)
                multipliers = ((ctypes.c_uint64 * count).from_buffer_copy(
                    batch._packed_weights_u64)
                    if batch._packed_weights_u64 is not None
                    else ctypes.POINTER(ctypes.c_uint64)())
            if self._mode == "weighted_hit_count":
                if batch._packed_weights_u64 is None:
                    _fail("RX006_INPUT_INVALID", "batch.query_weights", "exact U64 weights required")
                use_multipliers = 1
            else:
                has_weights = batch._packed_weights_u64 is not None
                if has_weights:
                    _fail("RX006_INPUT_INVALID", "batch.query_weights", "not admitted for all-hit count")
                multipliers = ctypes.POINTER(ctypes.c_uint64)()
                use_multipliers = 0
            # Some narrow fault-injection tests construct an owner without
            # calling __init__; keep that path valid without adding a branch to
            # ordinary initialized owners beyond these attribute reads.
            reduced = getattr(self, "_fast_reduced", None)
            if reduced is None:
                reduced = ctypes.c_uint64()
                self._fast_reduced = reduced
            error = getattr(self, "_call_error", None)
            if error is None:
                error = ctypes.create_string_buffer(16384)
                self._call_error = error
            audit = _open_audit(self._library) if diagnostics else None
            try:
                # Full role counters remain opt-in.  v5 handles both the first
                # dynamic input generation and later exact-byte reuse while
                # exposing setup costs separately in its native receipt.
                if diagnostics:
                    summary = _ProductStatusSummary()
                    counters = (ctypes.c_uint64 * 7)()
                    _raise_native(int(self._execute_diagnostic(
                        self._token, origin_native, direction_native,
                        tmax_native, count, int(reused), use_multipliers,
                        int(reused and use_multipliers), multipliers,
                        ctypes.byref(reduced), ctypes.byref(summary), counters,
                        error, len(error))),
                        error, "triangle.execute_diagnostic")
                    status_value, counter_rows = _validate_product_summary(
                        summary, counters, launch_count=count,
                        terminal_invocation_mask=(1 << 5))
                    status = {
                        **status_value,
                        "role_counters_materialized": True,
                        "role_counters_internally_materialized": True,
                        "fast_path_applied": False,
                        "execution_path": "diagnostic_v4",
                        "host_blocking_boundary_count_claimed": False,
                        "prepared_input_reused": reused,
                        "success_event_count_d2h_bytes": ctypes.sizeof(ctypes.c_uint64),
                        "success_scalar_d2h_bytes": ctypes.sizeof(_CheckedProductResult),
                        "success_total_product_d2h_bytes": (
                            ctypes.sizeof(_ProductStatusSummary)
                            + ctypes.sizeof(ctypes.c_uint64)
                            + ctypes.sizeof(_CheckedProductResult)
                        ),
                    }
                else:
                    compact_status = getattr(self, "_fast_compact_status", None)
                    if compact_status is None:
                        compact_status = ctypes.c_uint32()
                        self._fast_compact_status = compact_status
                    fast_receipt = _FastPathReceipt()
                    if getattr(self, "_lean_monitor", False):
                        native_status = int(self._execute_fast(
                            self._token, origin_native, direction_native,
                            tmax_native, count, int(reused), use_multipliers,
                            int(reused and use_multipliers),
                            batch._device_input_digest_u8, 32, multipliers,
                            ctypes.byref(reduced), ctypes.byref(compact_status),
                            ctypes.byref(fast_receipt), error, len(error)))
                    else:
                        native_status = int(self._execute_fast(
                            self._token, origin_native, direction_native,
                            tmax_native, count, int(reused), use_multipliers,
                            int(reused and use_multipliers), multipliers,
                            ctypes.byref(reduced), ctypes.byref(compact_status),
                            ctypes.byref(fast_receipt), error, len(error)))
                    _raise_native(native_status,
                        error, "triangle.execute_fast")
                    operation_receipt = _DeferredFastOperationReceipt(
                        fast_receipt, family=_TRIANGLE,
                        compact_status=int(compact_status.value),
                        expected_output_d2h_bytes=ctypes.sizeof(ctypes.c_uint64),
                        expected_prepared_input_reused=reused,
                        online_monitor=getattr(self, "_online_monitor", False),
                        lean_monitor=getattr(self, "_lean_monitor", False))
                    self._last_fast_operation_receipt = operation_receipt
                    status = _DeferredCompactDeviceStatus(
                        family=_TRIANGLE,
                        compact_status=int(compact_status.value),
                        launch_count=count,
                        operation_receipt=operation_receipt,
                        extras={
                            "success_event_count_d2h_bytes": 0,
                            "success_scalar_d2h_bytes": ctypes.sizeof(ctypes.c_uint64),
                            "success_total_product_d2h_bytes": (
                                20 if getattr(self, "_lean_monitor", False)
                                else (96 if getattr(self, "_online_monitor", False)
                                      else 12)),
                        })
                    counter_rows = ()
                output = int(reduced.value)
                output_sha = _digest(output) if diagnostics else None
                if batch.expected_reduced_u64 is not None \
                        and output != batch.expected_reduced_u64:
                    _fail("RX043_ORACLE_MISMATCH", "triangle.output", output)
                receipt = None
                if diagnostics:
                    receipt = audit.finish(
                        semantic_digest=_digest({"artifact": self._artifact_identity,
                            "ptx": self._ptx_sha, "native": self._native_sha}),
                        output_digest=output_sha,
                        route_identity=(
                            "v4_builtin_triangle_callback_ir:checked_reduction_v1"),
                        expected_program_bundles=(
                            "v4_builtin_triangle_checked_reduction_composed",))
                if not reused:
                    self._commit_query_cache(batch._device_input_sha256)
                # Publish the Python half while it is still protected by the
                # same BaseException handler as native commit.  The native
                # digest is nevertheless authoritative for later reuse.
                self._last_batch_key = batch_key
                self._last_query_arrays = (
                    origin_native, direction_native, tmax_native, multipliers)
            except BaseException:
                self._last_batch_key = None; self._last_query_arrays = None
                if audit is not None:
                    audit.abort()
                raise
            return output, output_sha, status, counter_rows, receipt
        finally:
            self._active.release()

    def close(self) -> None:
        if self._closed:
            if self._release_complete:
                return
            if os.getpid() != self._pid:
                _fail("RX038_PROCESS_BOUNDARY", "prepared", "different process")
            if threading.get_ident() != self._thread:
                _fail("RX039_THREAD_BOUNDARY", "prepared", "different thread")
            if not self._active.acquire(blocking=False):
                _fail("RX040_REENTRANT", "close", "active")
            try:
                try:
                    _release_native_library_image(self._library)
                    self._release_complete = True
                    self._close_failure = None
                    self._library = None
                except BaseException as error:
                    self._close_failure = repr(error)
                    raise
            finally:
                self._active.release()
            return
        self._check()
        if not self._active.acquire(blocking=False): _fail("RX040_REENTRANT", "close", "active")
        try:
            self._destroy_native_token()
            if not self._closed:
                _fail("RX046_NATIVE_RELEASE_INCOMPLETE", "triangle.close",
                      "native destroy returned without zeroing its token cell")
            library = self._library
            try:
                _release_native_library_image(library)
                self._release_complete = True
                self._close_failure = None
                self._library = None
            except BaseException as error:
                self._close_failure = repr(error)
                raise
        finally:
            self._active.release()


class PreparedRTDLExecutable:
    """Process/thread-bound prepared deployment with idempotent close."""

    __slots__ = (
        "_family", "_identity", "_owner", "_closed", "_batch_types")

    def __init__(self, *, family: str, executable_identity_sha256: str, owner: object) -> None:
        self._family = family; self._identity = executable_identity_sha256; self._owner = owner
        self._closed = False
        self._batch_types = (
            (BoundedRelationBatch, BoundedRelationBufferBatch)
            if family == _BOUNDED else
            (TriangleReductionBatch, TriangleReductionBufferBatch))

    @property
    def closed(self) -> bool:
        return self._closed

    def execute(
        self,
        batch: BoundedRelationBatch | BoundedRelationBufferBatch |
            TriangleReductionBatch | TriangleReductionBufferBatch,
        *,
        include_diagnostics: bool = False,
    ) -> RTDLExecutionResult:
        if self._closed: _fail("RX037_USE_AFTER_CLOSE", "prepared", "closed")
        if not isinstance(batch, self._batch_types):
            _fail("RX044_BATCH_MISMATCH", "batch", type(batch).__name__)
        if include_diagnostics is False:
            diagnostics = False
        elif include_diagnostics is True:
            diagnostics = True
        else:
            _fail(
                "RX006_INPUT_INVALID", "include_diagnostics",
                "exact bool required")
        output, output_sha, status, counters, receipt = self._owner.execute(
            batch, diagnostics=diagnostics)
        return RTDLExecutionResult(
            output=output,
            output_sha256=output_sha,
            executable_identity_sha256=self._identity,
            device_status=status,
            role_counters=counters,
            traversal_receipt=receipt,
        )

    def close(self) -> None:
        if self._closed: return
        self._owner.close()
        self._closed = True

    def __enter__(self) -> "PreparedRTDLExecutable":
        if self._closed: _fail("RX037_USE_AFTER_CLOSE", "prepared", "closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


__all__ = [
    "BoundedRelationBatch", "BoundedRelationStaticInput",
    "BoundedRelationBufferBatch", "BoundedRelationBufferStaticInput",
    "BuiltRTDLExecutable",
    "FrozenRTDLTrustPackage", "InstalledRTDLDeployment",
    "InitializingRTDLProvider", "LoadedRTDLExecutable",
    "PreparedRTDLExecutable", "ProviderReadyRTDLExecutable", "RTDLRuntimeSession",
    "RTDLExecutableBuildRoots", "RTDLExecutableError",
    "RTDLExecutionResult", "TriangleReductionBatch", "TriangleReductionStaticInput",
    "TriangleReductionBufferBatch", "TriangleReductionBufferStaticInput",
    "begin_rtdlexe_provider_initialization", "build_family_rtdlexe", "build_rtdlexe",
    "install_rtdlexe_deployment", "load_rtdlexe",
]
