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
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import secrets
from typing import Any, Iterable


_ERROR_CAPACITY = 2048
_RECEIPT_SCHEMA = "rtdl.physical_execution.traversal_receipt.v1"


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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def physical_program_bundle_id(name: str) -> int:
    """Return the stable FNV-1a id used by the native audit layer."""

    if type(name) is not str or not name:
        raise ValueError("physical program bundle name must be a nonempty string")
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _register_audit_abi(library: object) -> None:
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


@dataclass
class OptixTraversalAuditSession:
    """One nonce-bound, thread-local native launch observation."""

    library: object
    library_path: Path
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
            raw_path = getattr(library, "_rtdl_library_path", None)
            if not raw_path:
                raise RuntimeError("native traversal audit library path is unavailable")
            library_path = Path(raw_path).resolve()
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
            library_path=Path(library_path).resolve(),
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

    def finish(
        self,
        *,
        semantic_digest: str,
        output_digest: str,
        route_identity: str,
        expected_program_bundles: Iterable[str] = (),
    ) -> dict[str, Any]:
        if not self._active:
            raise RuntimeError("traversal audit session is not active")
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
        raw = _snapshot_dict(snapshot)
        if (
            raw["nonce_hi"] != self.nonce_hi
            or raw["nonce_lo"] != self.nonce_lo
        ):
            raise RuntimeError("native traversal audit returned the wrong nonce")

        expected_names = tuple(expected_program_bundles)
        expected_ids = tuple(
            physical_program_bundle_id(name) for name in expected_names
        )
        observed_edge_ids = {
            raw["first_program_bundle_id"],
            raw["last_program_bundle_id"],
        } - {0}
        expected_program_observed = (
            bool(observed_edge_ids.intersection(expected_ids))
            if expected_ids
            else None
        )

        if raw["session_error"] or raw["pending_context_at_finish"]:
            classification = "invalid_traversal_audit_session"
        elif raw["successful_launch_count"] == 0:
            classification = "no_optix_launch_observed"
        elif raw["complete_context_launch_count"] == 0:
            classification = "optix_launch_observed_without_bound_traversable_context"
        elif raw["incomplete_context_launch_count"] != 0:
            classification = "optix_traversal_observed_with_unbound_launches"
        elif expected_program_observed is False:
            classification = "optix_traversal_observed_but_expected_program_not_bound"
        else:
            classification = "optix_traversal_observed"

        receipt: dict[str, Any] = {
            "schema": _RECEIPT_SCHEMA,
            "provider_library": "librtdl_optix",
            "provider_library_path": str(self.library_path),
            "provider_library_sha256": _sha256(self.library_path),
            "route_identity": route_identity,
            "semantic_digest": semantic_digest,
            "output_digest": output_digest,
            "nonce": {
                "hi": self.nonce_hi,
                "lo": self.nonce_lo,
            },
            "physical_executor_classification": classification,
            "expected_program_bundles": list(expected_names),
            "expected_program_bundle_ids": list(expected_ids),
            "expected_program_observed_at_receipt_edge": expected_program_observed,
            "native_snapshot": raw,
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

    def __enter__(self) -> "OptixTraversalAuditSession":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if self._active:
            self.abort()
        return False


__all__ = [
    "OptixTraversalAuditSession",
    "physical_program_bundle_id",
]
