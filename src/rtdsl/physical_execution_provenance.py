"""Behavior-level physical execution provenance for RTDL native routes.

Backend/provider names describe an implementation boundary; they do not prove
that one concrete execution traversed an acceleration structure.  This module
opens a nonce-bound native audit session around an application execution and
combines the native ``optixLaunch`` observation with the exact native binary,
semantic identity, and output digest.

The API is intentionally application-neutral.  Paper applications may retain
the resulting receipt as evidence, but they cannot declare a launch or a
traversable in Python.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import secrets
import threading
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any


_ERROR_CAPACITY = 2048
_RECEIPT_SCHEMA = "rtdl.physical_execution.traversal_receipt.v1"
_COMPACT_RECEIPT_SCHEMA = "rtdl.physical_execution.compact_traversal_receipt.v1"
_COMPACT_STAMP_FIELDS = (
    "nonce_hi",
    "nonce_lo",
    "execution_sequence",
    "attempted_launch_count",
    "successful_launch_count",
    "failed_launch_count",
    "complete_context_launch_count",
    "incomplete_context_launch_count",
    "context_bind_count",
    "raygen_invocation_count",
    "first_program_bundle_id",
    "last_program_bundle_id",
    "first_traversable",
    "last_traversable",
    "pending_context_at_finish",
    "session_error",
    "incomplete_callsite_record_count",
    "program_bundle_mix",
    "traversable_mix",
)
_LOADED_PROVIDER_IDENTITIES: dict[int, tuple[object, Path, str]] = {}
_LOADED_PROVIDER_IDENTITIES_LOCK = threading.Lock()
_AUDIT_ABI_REGISTERED: dict[int, object] = {}


class _NativeTraversalAuditSnapshot(ctypes.Structure):
    _fields_ = [
        ("nonce_hi", ctypes.c_uint64),
        ("nonce_lo", ctypes.c_uint64),
        ("attempted_launch_count", ctypes.c_uint64),
        ("successful_launch_count", ctypes.c_uint64),
        ("failed_launch_count", ctypes.c_uint64),
        ("complete_context_launch_count", ctypes.c_uint64),
        ("incomplete_context_launch_count", ctypes.c_uint64),
        ("context_bind_count", ctypes.c_uint64),
        ("raygen_invocation_count", ctypes.c_uint64),
        ("program_bundle_mix", ctypes.c_uint64),
        ("traversable_mix", ctypes.c_uint64),
        ("pipeline_mix", ctypes.c_uint64),
        ("sbt_mix", ctypes.c_uint64),
        ("stream_mix", ctypes.c_uint64),
        ("params_mix", ctypes.c_uint64),
        ("callsite_mix", ctypes.c_uint64),
        ("first_program_bundle_id", ctypes.c_uint64),
        ("last_program_bundle_id", ctypes.c_uint64),
        ("first_traversable", ctypes.c_uint64),
        ("last_traversable", ctypes.c_uint64),
        ("pending_context_at_finish", ctypes.c_uint32),
        ("session_error", ctypes.c_uint32),
        ("incomplete_callsite_record_count", ctypes.c_uint32),
        ("incomplete_callsite_lines", ctypes.c_uint32 * 32),
    ]


NativeTraversalAuditSnapshot = _NativeTraversalAuditSnapshot
COMPACT_TRAVERSAL_RECEIPT_SCHEMA = _COMPACT_RECEIPT_SCHEMA
COMPACT_TRAVERSAL_STAMP_FIELDS = _COMPACT_STAMP_FIELDS


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@lru_cache(maxsize=4096)
def _is_canonical_sha256(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _require_sha256(value: object, *, label: str) -> str:
    if type(value) is not str or not _is_canonical_sha256(value):
        raise RuntimeError(f"{label} SHA-256 is malformed")
    return value


def _register_loaded_provider_identity(
    library: object, library_path: Path, provider_sha256: str
) -> str:
    """Bind one immutable provider identity to one in-process library handle."""

    resolved = Path(library_path).resolve()
    digest = _require_sha256(provider_sha256, label="loaded native provider")
    key = id(library)
    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _LOADED_PROVIDER_IDENTITIES.get(key)
        if current is not None:
            current_library, current_path, current_digest = current
            if current_library is not library:
                raise RuntimeError("native provider handle identity was reused")
            if current_path != resolved or current_digest != digest:
                raise RuntimeError("loaded native provider identity changed")
            return current_digest
        _LOADED_PROVIDER_IDENTITIES[key] = (library, resolved, digest)
    return digest


def _loaded_provider_sha256(library: object, library_path: Path) -> str:
    """Return the exact provider identity frozen on this loaded handle.

    RTDL's own loader records the digest when it creates the ``ctypes`` handle.
    Externally supplied handles are hashed once on first audited use.  A fresh
    behavioral receipt must still be produced for every execution, but rereading
    the same multi-megabyte provider file is not part of that per-call evidence.
    """

    resolved = Path(library_path).resolve()
    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _LOADED_PROVIDER_IDENTITIES.get(id(library))
        if current is not None:
            current_library, current_path, current_digest = current
            if current_library is not library:
                raise RuntimeError("native provider handle identity was reused")
            if current_path != resolved:
                raise RuntimeError(
                    "cached native provider identity belongs to a different library path"
                )
            return current_digest
    loaded_path = getattr(library, "_rtdl_loaded_library_path", None)
    if loaded_path is not None and Path(str(loaded_path)).resolve() != resolved:
        raise RuntimeError(
            "cached native provider identity belongs to a different library path"
        )
    cached = getattr(library, "_rtdl_loaded_library_sha256", None)
    if cached is None:
        cached = _sha256(resolved)
        try:
            setattr(library, "_rtdl_loaded_library_path", str(resolved))
            setattr(library, "_rtdl_loaded_library_sha256", cached)
        except Exception as exc:
            raise RuntimeError(
                "native provider handle cannot retain its frozen identity"
            ) from exc
    digest = _require_sha256(cached, label="cached native provider")
    return _register_loaded_provider_identity(library, resolved, digest)


def _registered_loaded_provider_identity(
    library: object,
) -> tuple[Path, str] | None:
    """Return an RTDL-loader identity without touching the filesystem.

    The registry retains the exact library object, so an integer ``id`` reuse
    cannot substitute another handle.  Explicit caller-supplied paths still go
    through the resolving comparison in ``_loaded_provider_sha256``.
    """

    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _LOADED_PROVIDER_IDENTITIES.get(id(library))
        if current is None:
            return None
        current_library, current_path, current_digest = current
        if current_library is not library:
            raise RuntimeError("native provider handle identity was reused")
        return current_path, current_digest


def _unregister_loaded_provider_identity(library: object) -> None:
    """Release strong registry references for one closed provider lease.

    The provider and audit registries intentionally retain the exact Python
    lease object while a prepared deployment is live so an ``id`` reuse cannot
    substitute another lease.  A successful prepared close is the matching
    per-lease lifetime boundary.  The RTDL executable loader may separately
    retain one content-addressed, sealed DSO mapping per digest for the process
    lifetime; unregistering a lease neither claims nor attempts to unload that
    cache entry.
    """

    key = id(library)
    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _LOADED_PROVIDER_IDENTITIES.get(key)
        if current is not None:
            current_library, _current_path, _current_digest = current
            if current_library is not library:
                raise RuntimeError("native provider handle identity was reused")
            del _LOADED_PROVIDER_IDENTITIES[key]
        audit_library = _AUDIT_ABI_REGISTERED.get(key)
        if audit_library is not None:
            if audit_library is not library:
                raise RuntimeError("native audit ABI handle identity was reused")
            del _AUDIT_ABI_REGISTERED[key]


def _stable_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@lru_cache(maxsize=256)
def _cached_physical_program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def physical_program_bundle_id(name: str) -> int:
    """Return the stable FNV-1a id used by the native audit layer."""

    if type(name) is not str or not name:
        raise ValueError("physical program bundle name must be a nonempty string")
    return _cached_physical_program_bundle_id(name)


def _native_audit_mix_u64(state: int, value: int) -> int:
    """Reproduce ``rtdl_audit_mix`` from the exact native audit producer."""

    mask = (1 << 64) - 1
    state &= mask
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value ^= value >> 31
    value &= mask
    return (
        state
        ^ (
            value
            + 0x9E3779B97F4A7C15
            + ((state << 6) & mask)
            + (state >> 2)
        )
    ) & mask


def _register_audit_abi(library: object) -> None:
    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _AUDIT_ABI_REGISTERED.get(id(library))
        if current is not None:
            if current is not library:
                raise RuntimeError("native audit ABI handle identity was reused")
            return
    begin = getattr(library, "rtdl_optix_traversal_audit_begin", None)
    finish = getattr(library, "rtdl_optix_traversal_audit_finish", None)
    abort = getattr(library, "rtdl_optix_traversal_audit_abort", None)
    if begin is None or finish is None or abort is None:
        raise RuntimeError(
            "loaded native library lacks the behavior-level traversal audit ABI"
        )
    begin.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    begin.restype = ctypes.c_int
    finish.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(_NativeTraversalAuditSnapshot),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    finish.restype = ctypes.c_int
    abort.argtypes = [
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    abort.restype = ctypes.c_int
    with _LOADED_PROVIDER_IDENTITIES_LOCK:
        current = _AUDIT_ABI_REGISTERED.get(id(library))
        if current is not None and current is not library:
            raise RuntimeError("native audit ABI handle identity was reused")
        _AUDIT_ABI_REGISTERED[id(library)] = library


def _call_status(symbol: object, *args: object) -> None:
    error = ctypes.create_string_buffer(_ERROR_CAPACITY)
    status = int(symbol(*args, error, len(error)))
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(detail or f"native traversal audit call failed: {status}")


def _snapshot_dict(snapshot: _NativeTraversalAuditSnapshot) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, _ctype in _NativeTraversalAuditSnapshot._fields_:
        value = getattr(snapshot, name)
        if isinstance(value, ctypes.Array):
            result[name] = [int(item) for item in value]
        else:
            result[name] = int(value)
    return result


_CapturedSnapshotValue = int | tuple[int, ...]


def _captured_snapshot_items(
    snapshot: _NativeTraversalAuditSnapshot,
) -> tuple[tuple[str, _CapturedSnapshotValue], ...]:
    """Freeze one native snapshot without constructing receipt JSON state."""

    items: list[tuple[str, _CapturedSnapshotValue]] = []
    for name, _ctype in _NativeTraversalAuditSnapshot._fields_:
        value = getattr(snapshot, name)
        if isinstance(value, ctypes.Array):
            items.append((name, tuple(int(item) for item in value)))
        else:
            items.append((name, int(value)))
    return tuple(items)


def _captured_snapshot_dict(
    items: tuple[tuple[str, _CapturedSnapshotValue], ...],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in items:
        result[name] = list(value) if isinstance(value, tuple) else value
    return result


def _classify_snapshot(
    snapshot: _NativeTraversalAuditSnapshot,
    expected_program_bundle_ids: tuple[int, ...],
) -> tuple[str, bool | None]:
    observed_edge_ids = {
        int(snapshot.first_program_bundle_id),
        int(snapshot.last_program_bundle_id),
    } - {0}
    expected_program_observed = (
        bool(observed_edge_ids.intersection(expected_program_bundle_ids))
        if expected_program_bundle_ids
        else None
    )
    if snapshot.session_error or snapshot.pending_context_at_finish:
        classification = "invalid_traversal_audit_session"
    elif snapshot.successful_launch_count == 0:
        classification = "no_optix_launch_observed"
    elif snapshot.complete_context_launch_count == 0:
        classification = "optix_launch_observed_without_bound_traversable_context"
    elif snapshot.incomplete_context_launch_count != 0:
        classification = "optix_traversal_observed_with_unbound_launches"
    elif expected_program_observed is False:
        classification = "optix_traversal_observed_but_expected_program_not_bound"
    else:
        classification = "optix_traversal_observed"
    return classification, expected_program_observed


def captured_traversal_observation_from_snapshot(
    snapshot: _NativeTraversalAuditSnapshot,
    *,
    provider_library_path: str | Path,
    provider_library_sha256: str,
    nonce: tuple[int, int],
    expected_program_bundles: Iterable[str] = (),
) -> "CapturedTraversalObservation":
    """Freeze an audit snapshot already returned by an integrated native call."""

    if not isinstance(snapshot, _NativeTraversalAuditSnapshot):
        raise TypeError("native traversal audit snapshot required")
    nonce_hi, nonce_lo = nonce
    if (
        int(snapshot.nonce_hi) != nonce_hi
        or int(snapshot.nonce_lo) != nonce_lo
    ):
        raise RuntimeError("native traversal audit returned the wrong nonce")
    expected_names = tuple(expected_program_bundles)
    expected_ids = tuple(
        physical_program_bundle_id(name) for name in expected_names
    )
    classification, expected_program_observed = _classify_snapshot(
        snapshot, expected_ids
    )
    return CapturedTraversalObservation(
        provider_library_path=Path(provider_library_path).resolve(),
        provider_library_sha256=_require_sha256(
            provider_library_sha256, label="loaded native provider"
        ),
        nonce_hi=nonce_hi,
        nonce_lo=nonce_lo,
        physical_executor_classification=classification,
        expected_program_bundles=expected_names,
        expected_program_bundle_ids=expected_ids,
        expected_program_observed_at_receipt_edge=expected_program_observed,
        native_snapshot_items=_captured_snapshot_items(snapshot),
    )


def _compact_stamp_values(
    snapshot: _NativeTraversalAuditSnapshot,
    execution_sequence: int,
) -> list[int]:
    return [
        int(snapshot.nonce_hi),
        int(snapshot.nonce_lo),
        execution_sequence,
        int(snapshot.attempted_launch_count),
        int(snapshot.successful_launch_count),
        int(snapshot.failed_launch_count),
        int(snapshot.complete_context_launch_count),
        int(snapshot.incomplete_context_launch_count),
        int(snapshot.context_bind_count),
        int(snapshot.raygen_invocation_count),
        int(snapshot.first_program_bundle_id),
        int(snapshot.last_program_bundle_id),
        int(snapshot.first_traversable),
        int(snapshot.last_traversable),
        int(snapshot.pending_context_at_finish),
        int(snapshot.session_error),
        int(snapshot.incomplete_callsite_record_count),
        int(snapshot.program_bundle_mix),
        int(snapshot.traversable_mix),
    ]


def _validate_compact_stamp(
    values: object,
    *,
    expected_program_bundle_id: int,
    expected_successful_launch_count: int,
    expected_raygen_invocation_count: int,
) -> None:
    if (
        not isinstance(values, (list, tuple))
        or len(values) != len(_COMPACT_STAMP_FIELDS)
        or any(type(value) is not int or not 0 <= value < 1 << 64 for value in values)
    ):
        raise RuntimeError("compact traversal native stamp differs")
    (
        nonce_hi,
        nonce_lo,
        execution_sequence,
        attempted_launch_count,
        successful_launch_count,
        failed_launch_count,
        complete_context_launch_count,
        incomplete_context_launch_count,
        context_bind_count,
        raygen_invocation_count,
        first_program_bundle_id,
        last_program_bundle_id,
        first_traversable,
        last_traversable,
        pending_context_at_finish,
        session_error,
        incomplete_callsite_record_count,
        program_bundle_mix,
        traversable_mix,
    ) = values
    if (
        nonce_hi == 0
        or nonce_lo == 0
        or execution_sequence == 0
        or nonce_lo != execution_sequence
        or attempted_launch_count != expected_successful_launch_count
        or successful_launch_count != expected_successful_launch_count
        or failed_launch_count != 0
        or complete_context_launch_count != expected_successful_launch_count
        or incomplete_context_launch_count != 0
        or context_bind_count != expected_successful_launch_count
        or raygen_invocation_count != expected_raygen_invocation_count
        or first_program_bundle_id != expected_program_bundle_id
        or last_program_bundle_id != expected_program_bundle_id
        or first_traversable == 0
        or last_traversable != first_traversable
        or pending_context_at_finish != 0
        or session_error != 0
        or incomplete_callsite_record_count != 0
        or program_bundle_mix
            != _native_audit_mix_u64(0, expected_program_bundle_id)
        or traversable_mix != _native_audit_mix_u64(0, first_traversable)
    ):
        raise RuntimeError("compact traversal native stamp differs")


_VALIDATED_COMPACT_RECEIPT_TOKEN = object()


class ValidatedCompactTraversalReceipt(Mapping[str, object]):
    """Immutable proof whose JSON envelope is expanded only when inspected.

    Native launch facts are copied and validated eagerly.  Deferring the
    canonical mapping and its transport seal therefore changes representation
    cost, not the fail-closed execution decision.
    """

    __slots__ = (
        "_document",
        "_expected_program_bundle",
        "_expected_program_bundle_id",
        "_expected_raygen_invocation_count",
        "_native_stamp",
        "_output_digest",
        "_provider_library_sha256",
        "_route_identity",
        "_semantic_digest",
    )

    def __init__(
        self,
        *,
        provider_library_sha256: str,
        route_identity: str,
        semantic_digest: str,
        output_digest: str,
        expected_program_bundle: str,
        expected_program_bundle_id: int,
        expected_raygen_invocation_count: int,
        native_stamp: tuple[int, ...],
        _token: object,
    ) -> None:
        if _token is not _VALIDATED_COMPACT_RECEIPT_TOKEN:
            raise RuntimeError("validated compact receipt requires its factory")
        object.__setattr__(self, "_provider_library_sha256", provider_library_sha256)
        object.__setattr__(self, "_route_identity", route_identity)
        object.__setattr__(self, "_semantic_digest", semantic_digest)
        object.__setattr__(self, "_output_digest", output_digest)
        object.__setattr__(
            self, "_expected_program_bundle", expected_program_bundle
        )
        object.__setattr__(
            self, "_expected_program_bundle_id", expected_program_bundle_id
        )
        object.__setattr__(
            self,
            "_expected_raygen_invocation_count",
            expected_raygen_invocation_count,
        )
        object.__setattr__(self, "_native_stamp", native_stamp)
        object.__setattr__(self, "_document", None)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("validated compact traversal receipt is immutable")

    @property
    def materialized(self) -> bool:
        """Report whether an observer requested the transport document."""

        return self._document is not None

    def _materialize(self) -> Mapping[str, object]:
        current = self._document
        if current is not None:
            return current
        body: dict[str, object] = {
            "schema": _COMPACT_RECEIPT_SCHEMA,
            "provider_library_sha256": self._provider_library_sha256,
            "route_identity": self._route_identity,
            "semantic_digest": self._semantic_digest,
            "output_digest": self._output_digest,
            "physical_executor_classification": "optix_traversal_observed",
            "expected_program_bundle": self._expected_program_bundle,
            "expected_program_bundle_id": self._expected_program_bundle_id,
            "expected_program_observed_at_receipt_edge": True,
            "native_stamp": self._native_stamp,
        }
        body["receipt_sha256"] = _stable_digest(body)
        current = MappingProxyType(body)
        object.__setattr__(self, "_document", current)
        return current

    def __getitem__(self, key: str) -> object:
        return self._materialize()[key]

    def __iter__(self):
        return iter(self._materialize())

    def __len__(self) -> int:
        return 11


def build_validated_compact_traversal_receipt(
    snapshot: _NativeTraversalAuditSnapshot,
    *,
    provider_library_sha256: str,
    route_identity: str,
    semantic_digest: str,
    output_digest: str,
    expected_program_bundle: str,
    expected_raygen_invocation_count: int,
    execution_sequence: int,
) -> ValidatedCompactTraversalReceipt:
    """Validate native facts now and defer only the export representation."""

    if not isinstance(snapshot, _NativeTraversalAuditSnapshot):
        raise TypeError("native traversal audit snapshot required")
    if type(route_identity) is not str or not route_identity:
        raise ValueError("route_identity must be a nonempty string")
    if type(expected_program_bundle) is not str or not expected_program_bundle:
        raise ValueError("expected_program_bundle must be a nonempty string")
    if type(execution_sequence) is not int or not 0 < execution_sequence < 1 << 64:
        raise ValueError("execution_sequence must be a positive uint64")
    if (
        type(expected_raygen_invocation_count) is not int
        or not 0 < expected_raygen_invocation_count < 1 << 64
    ):
        raise ValueError("expected raygen invocation count must be a positive uint64")
    provider_digest = _require_sha256(
        provider_library_sha256, label="loaded native provider"
    )
    semantic = _require_sha256(semantic_digest, label="receipt semantic")
    output = _require_sha256(output_digest, label="receipt output")
    bundle_id = physical_program_bundle_id(expected_program_bundle)
    native_stamp = tuple(_compact_stamp_values(snapshot, execution_sequence))
    _validate_compact_stamp(
        native_stamp,
        expected_program_bundle_id=bundle_id,
        expected_successful_launch_count=1,
        expected_raygen_invocation_count=expected_raygen_invocation_count,
    )
    return ValidatedCompactTraversalReceipt(
        provider_library_sha256=provider_digest,
        route_identity=route_identity,
        semantic_digest=semantic,
        output_digest=output,
        expected_program_bundle=expected_program_bundle,
        expected_program_bundle_id=bundle_id,
        expected_raygen_invocation_count=expected_raygen_invocation_count,
        native_stamp=native_stamp,
        _token=_VALIDATED_COMPACT_RECEIPT_TOKEN,
    )


def validate_bound_compact_traversal_receipt(
    receipt: object,
    *,
    provider_library_sha256: str,
    route_identity: str,
    output_digest: str,
    expected_program_bundle: str,
    expected_raygen_invocation_count: int,
) -> ValidatedCompactTraversalReceipt:
    """Check an unexpanded receipt against its immediate public boundary."""

    if type(receipt) is not ValidatedCompactTraversalReceipt:
        raise TypeError("validated compact traversal receipt required")
    expected_bundle_id = physical_program_bundle_id(expected_program_bundle)
    if (
        receipt._provider_library_sha256 != provider_library_sha256
        or receipt._route_identity != route_identity
        or receipt._output_digest != output_digest
        or receipt._expected_program_bundle != expected_program_bundle
        or receipt._expected_program_bundle_id != expected_bundle_id
        or receipt._expected_raygen_invocation_count
            != expected_raygen_invocation_count
    ):
        raise RuntimeError("validated compact traversal receipt binding differs")
    return receipt


def build_compact_traversal_receipt(
    snapshot: _NativeTraversalAuditSnapshot,
    *,
    provider_library_sha256: str,
    route_identity: str,
    semantic_digest: str,
    output_digest: str,
    expected_program_bundle: str,
    expected_raygen_invocation_count: int,
    execution_sequence: int,
) -> dict[str, object]:
    """Validate one integrated audit snapshot and emit its compact proof."""

    if not isinstance(snapshot, _NativeTraversalAuditSnapshot):
        raise TypeError("native traversal audit snapshot required")
    if type(route_identity) is not str or not route_identity:
        raise ValueError("route_identity must be a nonempty string")
    if type(expected_program_bundle) is not str or not expected_program_bundle:
        raise ValueError("expected_program_bundle must be a nonempty string")
    if type(execution_sequence) is not int or not 0 < execution_sequence < 1 << 64:
        raise ValueError("execution_sequence must be a positive uint64")
    if (
        type(expected_raygen_invocation_count) is not int
        or not 0 < expected_raygen_invocation_count < 1 << 64
    ):
        raise ValueError("expected raygen invocation count must be a positive uint64")
    provider_digest = _require_sha256(
        provider_library_sha256, label="loaded native provider"
    )
    semantic = _require_sha256(semantic_digest, label="receipt semantic")
    output = _require_sha256(output_digest, label="receipt output")
    bundle_id = physical_program_bundle_id(expected_program_bundle)
    native_stamp = _compact_stamp_values(snapshot, execution_sequence)
    _validate_compact_stamp(
        native_stamp,
        expected_program_bundle_id=bundle_id,
        expected_successful_launch_count=1,
        expected_raygen_invocation_count=expected_raygen_invocation_count,
    )
    receipt: dict[str, object] = {
        "schema": _COMPACT_RECEIPT_SCHEMA,
        "provider_library_sha256": provider_digest,
        "route_identity": route_identity,
        "semantic_digest": semantic,
        "output_digest": output,
        "physical_executor_classification": "optix_traversal_observed",
        "expected_program_bundle": expected_program_bundle,
        "expected_program_bundle_id": bundle_id,
        "expected_program_observed_at_receipt_edge": True,
        "native_stamp": native_stamp,
    }
    receipt["receipt_sha256"] = _stable_digest(receipt)
    return receipt


def validate_compact_traversal_receipt(
    receipt: Mapping[str, object],
    *,
    provider_library_sha256: str,
    route_identity: str,
    output_digest: str,
    expected_program_bundles: tuple[str, ...],
    expected_successful_launch_count: int,
    expected_raygen_invocation_count: int,
) -> None:
    """Independently revalidate a compact integrated traversal proof."""

    if (
        type(expected_successful_launch_count) is not int
        or expected_successful_launch_count != 1
        or type(expected_raygen_invocation_count) is not int
        or not 0 < expected_raygen_invocation_count < 1 << 64
    ):
        raise RuntimeError("compact traversal expected counts are invalid")
    expected_fields = {
        "schema", "provider_library_sha256", "route_identity",
        "semantic_digest", "output_digest", "physical_executor_classification",
        "expected_program_bundle", "expected_program_bundle_id",
        "expected_program_observed_at_receipt_edge", "native_stamp",
        "receipt_sha256",
    }
    if set(receipt) != expected_fields or len(expected_program_bundles) != 1:
        raise RuntimeError("compact traversal receipt field set differs")
    body = dict(receipt)
    observed_seal = body.pop("receipt_sha256", None)
    bundle = expected_program_bundles[0]
    bundle_id = physical_program_bundle_id(bundle)
    if (
        receipt.get("schema") != _COMPACT_RECEIPT_SCHEMA
        or receipt.get("provider_library_sha256")
            != _require_sha256(
                provider_library_sha256, label="expected native provider"
            )
        or receipt.get("route_identity") != route_identity
        or _require_sha256(
            receipt.get("semantic_digest"), label="receipt semantic"
        ) != receipt.get("semantic_digest")
        or receipt.get("output_digest")
            != _require_sha256(output_digest, label="expected output")
        or receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
        or receipt.get("expected_program_bundle") != bundle
        or receipt.get("expected_program_bundle_id") != bundle_id
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or type(observed_seal) is not str
        or observed_seal != _stable_digest(body)
    ):
        raise RuntimeError("compact traversal receipt envelope differs")
    _validate_compact_stamp(
        receipt.get("native_stamp"),
        expected_program_bundle_id=bundle_id,
        expected_successful_launch_count=expected_successful_launch_count,
        expected_raygen_invocation_count=expected_raygen_invocation_count,
    )


def validate_traversal_receipt(
    receipt: Mapping[str, object],
    *,
    provider_library_sha256: str,
    route_identity: str,
    output_digest: str,
    expected_program_bundles: tuple[str, ...],
    expected_successful_launch_count: int,
    expected_raygen_invocation_count: int,
) -> None:
    """Validate one complete, rehashable native traversal receipt.

    This is intentionally stricter than checking the classification string.
    It rejects self-sealed partial receipts that omit the native launch and
    context counters from which that classification is derived.
    """

    if receipt.get("schema") == _COMPACT_RECEIPT_SCHEMA:
        validate_compact_traversal_receipt(
            receipt,
            provider_library_sha256=provider_library_sha256,
            route_identity=route_identity,
            output_digest=output_digest,
            expected_program_bundles=expected_program_bundles,
            expected_successful_launch_count=expected_successful_launch_count,
            expected_raygen_invocation_count=expected_raygen_invocation_count,
        )
        return

    expected_top_level = {
        "schema", "provider_library", "provider_library_path",
        "provider_library_sha256", "route_identity", "semantic_digest",
        "output_digest", "nonce", "physical_executor_classification",
        "expected_program_bundles", "expected_program_bundle_ids",
        "expected_program_observed_at_receipt_edge", "native_snapshot",
        "claim_rules", "receipt_sha256",
    }
    expected_snapshot = {
        name for name, _ctype in _NativeTraversalAuditSnapshot._fields_}
    expected_rules = {
        "provider_name_alone_proves_traversal": False,
        "selected_template_alone_proves_traversal": False,
        "successful_optix_launch_required": True,
        "nonzero_traversable_binding_required": True,
        "program_bundle_binding_required": True,
        "output_digest_bound": True,
    }
    if set(receipt) != expected_top_level:
        raise RuntimeError("traversal receipt field set differs")
    body = dict(receipt)
    observed_seal = body.pop("receipt_sha256", None)
    snapshot = receipt.get("native_snapshot")
    nonce = receipt.get("nonce")
    bundles = list(expected_program_bundles)
    if (
        type(expected_successful_launch_count) is not int
        or expected_successful_launch_count != 1
        or len(bundles) != 1
    ):
        raise RuntimeError(
            "this traversal receipt validator requires one launch and one bundle")
    bundle_ids = [physical_program_bundle_id(item) for item in bundles]
    if (
        receipt.get("schema") != _RECEIPT_SCHEMA
        or receipt.get("provider_library") != "librtdl_optix"
        or not isinstance(receipt.get("provider_library_path"), str)
        or not receipt.get("provider_library_path")
        or receipt.get("provider_library_sha256")
            != _require_sha256(
                provider_library_sha256, label="expected native provider")
        or receipt.get("route_identity") != route_identity
        or not isinstance(receipt.get("semantic_digest"), str)
        or _require_sha256(
            receipt.get("semantic_digest"), label="receipt semantic")
            != receipt.get("semantic_digest")
        or receipt.get("output_digest")
            != _require_sha256(output_digest, label="expected output")
        or receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
        or receipt.get("expected_program_bundles") != bundles
        or receipt.get("expected_program_bundle_ids") != bundle_ids
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or receipt.get("claim_rules") != expected_rules
        or not isinstance(observed_seal, str)
        or observed_seal != _stable_digest(body)
        or not isinstance(nonce, Mapping)
        or set(nonce) != {"hi", "lo"}
        or any(not isinstance(nonce.get(key), int)
               or isinstance(nonce.get(key), bool)
               or not 0 <= int(nonce[key]) < 1 << 64
               for key in ("hi", "lo"))
        or (int(nonce["hi"]), int(nonce["lo"])) == (0, 0)
        or not isinstance(snapshot, Mapping)
        or set(snapshot) != expected_snapshot
    ):
        raise RuntimeError("traversal receipt envelope differs")
    scalar_snapshot = {
        key: value for key, value in snapshot.items()
        if key != "incomplete_callsite_lines"
    }
    scalar_widths: dict[str, int] = {}
    for field_name, field_type in _NativeTraversalAuditSnapshot._fields_:
        if field_name == "incomplete_callsite_lines":
            continue
        if field_type is ctypes.c_uint64:
            scalar_widths[field_name] = 64
        elif field_type is ctypes.c_uint32:
            scalar_widths[field_name] = 32
        else:  # pragma: no cover - guarded by the frozen native ABI layout.
            raise RuntimeError("unsupported native snapshot scalar width")
    lines = snapshot.get("incomplete_callsite_lines")
    if (
        any(not isinstance(value, int) or isinstance(value, bool)
            or not 0 <= value < (1 << scalar_widths[key])
            for key, value in scalar_snapshot.items())
        or not isinstance(lines, list)
        or len(lines) != 32
        or any(not isinstance(value, int) or isinstance(value, bool)
               or not 0 <= value < 1 << 32 for value in lines)
        or snapshot["nonce_hi"] != nonce["hi"]
        or snapshot["nonce_lo"] != nonce["lo"]
        or snapshot["attempted_launch_count"]
            != expected_successful_launch_count
        or snapshot["successful_launch_count"]
            != expected_successful_launch_count
        or snapshot["failed_launch_count"] != 0
        or snapshot["complete_context_launch_count"]
            != expected_successful_launch_count
        or snapshot["incomplete_context_launch_count"] != 0
        or snapshot["context_bind_count"] != expected_successful_launch_count
        or snapshot["raygen_invocation_count"]
            != expected_raygen_invocation_count
        or snapshot["pending_context_at_finish"] != 0
        or snapshot["session_error"] != 0
        or snapshot["incomplete_callsite_record_count"] != 0
        or any(lines)
        or snapshot["first_program_bundle_id"] != bundle_ids[0]
        or snapshot["last_program_bundle_id"] != bundle_ids[-1]
        or snapshot["first_traversable"] == 0
        or snapshot["last_traversable"] == 0
        or snapshot["first_traversable"] != snapshot["last_traversable"]
        or snapshot["program_bundle_mix"]
            != _native_audit_mix_u64(0, bundle_ids[0])
        or snapshot["traversable_mix"]
            != _native_audit_mix_u64(0, snapshot["first_traversable"])
    ):
        raise RuntimeError("traversal receipt native snapshot differs")


@dataclass(frozen=True)
class CapturedTraversalObservation:
    """Immutable native audit observation awaiting receipt sealing.

    Capture closes the native audit session and freezes only primitive values.
    Receipt dictionaries and their SHA-256 digest are deliberately constructed
    later by :meth:`build_receipt`, so a caller can keep evidence sealing out of
    a registered execution timer.
    """

    provider_library_path: Path
    provider_library_sha256: str
    nonce_hi: int
    nonce_lo: int
    physical_executor_classification: str
    expected_program_bundles: tuple[str, ...]
    expected_program_bundle_ids: tuple[int, ...]
    expected_program_observed_at_receipt_edge: bool | None
    native_snapshot_items: tuple[tuple[str, _CapturedSnapshotValue], ...]

    def build_receipt(
        self,
        *,
        semantic_digest: str,
        output_digest: str,
        route_identity: str,
    ) -> dict[str, Any]:
        """Bind semantic/output identities and seal the captured observation."""

        for name, value in (
            ("semantic_digest", semantic_digest),
            ("output_digest", output_digest),
        ):
            if (
                type(value) is not str
                or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)
            ):
                raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
        if type(route_identity) is not str or not route_identity:
            raise ValueError("route_identity must be a nonempty string")

        receipt: dict[str, Any] = {
            "schema": _RECEIPT_SCHEMA,
            "provider_library": "librtdl_optix",
            "provider_library_path": str(self.provider_library_path),
            "provider_library_sha256": self.provider_library_sha256,
            "route_identity": route_identity,
            "semantic_digest": semantic_digest,
            "output_digest": output_digest,
            "nonce": {
                "hi": self.nonce_hi,
                "lo": self.nonce_lo,
            },
            "physical_executor_classification": (
                self.physical_executor_classification
            ),
            "expected_program_bundles": list(self.expected_program_bundles),
            "expected_program_bundle_ids": list(
                self.expected_program_bundle_ids
            ),
            "expected_program_observed_at_receipt_edge": (
                self.expected_program_observed_at_receipt_edge
            ),
            "native_snapshot": _captured_snapshot_dict(
                self.native_snapshot_items
            ),
            "claim_rules": {
                "provider_name_alone_proves_traversal": False,
                "selected_template_alone_proves_traversal": False,
                "successful_optix_launch_required": True,
                "nonzero_traversable_binding_required": True,
                "program_bundle_binding_required": True,
                "output_digest_bound": True,
            },
        }
        receipt["receipt_sha256"] = _stable_digest(receipt)
        return receipt


@dataclass
class OptixTraversalAuditSession:
    """One nonce-bound, thread-local native launch observation."""

    library: object
    library_path: Path
    provider_library_sha256: str
    nonce_hi: int
    nonce_lo: int
    _active: bool = False

    @classmethod
    def open(
        cls,
        *,
        library: object | None = None,
        library_path: Path | None = None,
        nonce: tuple[int, int] | None = None,
    ) -> "OptixTraversalAuditSession":
        if library is None:
            from . import optix_runtime

            library = optix_runtime._load_optix_library()
        if library_path is None:
            registered = _registered_loaded_provider_identity(library)
            if registered is not None:
                resolved_library_path, provider_library_sha256 = registered
            else:
                raw_path = getattr(library, "_rtdl_library_path", None)
                if not raw_path:
                    raise RuntimeError(
                        "native traversal audit library path is unavailable")
                resolved_library_path = Path(raw_path).resolve()
                provider_library_sha256 = _loaded_provider_sha256(
                    library, resolved_library_path)
        else:
            resolved_library_path = Path(library_path).resolve()
            provider_library_sha256 = _loaded_provider_sha256(
                library, resolved_library_path)
        if nonce is None:
            nonce = (secrets.randbits(64), secrets.randbits(64))
            if nonce == (0, 0):
                nonce = (0, 1)
        nonce_hi, nonce_lo = nonce
        if not (0 <= nonce_hi < 1 << 64 and 0 <= nonce_lo < 1 << 64):
            raise ValueError("traversal audit nonce words must be uint64")
        if nonce_hi == 0 and nonce_lo == 0:
            raise ValueError("traversal audit nonce must be nonzero")

        _register_audit_abi(library)
        session = cls(
            library=library,
            library_path=resolved_library_path,
            provider_library_sha256=provider_library_sha256,
            nonce_hi=nonce_hi,
            nonce_lo=nonce_lo,
        )
        _call_status(
            library.rtdl_optix_traversal_audit_begin,
            nonce_hi,
            nonce_lo,
        )
        session._active = True
        return session

    def abort(self) -> None:
        if not self._active:
            return
        try:
            _call_status(
                self.library.rtdl_optix_traversal_audit_abort,
                self.nonce_hi,
                self.nonce_lo,
            )
        finally:
            self._active = False

    def capture(
        self,
        *,
        expected_program_bundles: Iterable[str] = (),
    ) -> CapturedTraversalObservation:
        """Close and freeze the native audit without hashing a receipt."""

        if not self._active:
            raise RuntimeError("traversal audit session is not active")

        snapshot = _NativeTraversalAuditSnapshot()
        try:
            _call_status(
                self.library.rtdl_optix_traversal_audit_finish,
                self.nonce_hi,
                self.nonce_lo,
                ctypes.byref(snapshot),
            )
        finally:
            self._active = False
        return captured_traversal_observation_from_snapshot(
            snapshot,
            provider_library_path=self.library_path,
            provider_library_sha256=self.provider_library_sha256,
            nonce=(self.nonce_hi, self.nonce_lo),
            expected_program_bundles=expected_program_bundles,
        )

    def finish(
        self,
        *,
        semantic_digest: str,
        output_digest: str,
        route_identity: str,
        expected_program_bundles: Iterable[str] = (),
    ) -> dict[str, Any]:
        return self.capture(
            expected_program_bundles=expected_program_bundles,
        ).build_receipt(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity=route_identity,
        )

    def __enter__(self) -> "OptixTraversalAuditSession":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if self._active:
            self.abort()
        return False


__all__ = [
    "COMPACT_TRAVERSAL_RECEIPT_SCHEMA",
    "COMPACT_TRAVERSAL_STAMP_FIELDS",
    "CapturedTraversalObservation",
    "NativeTraversalAuditSnapshot",
    "OptixTraversalAuditSession",
    "ValidatedCompactTraversalReceipt",
    "build_compact_traversal_receipt",
    "build_validated_compact_traversal_receipt",
    "captured_traversal_observation_from_snapshot",
    "physical_program_bundle_id",
    "validate_bound_compact_traversal_receipt",
    "validate_compact_traversal_receipt",
    "validate_traversal_receipt",
]
