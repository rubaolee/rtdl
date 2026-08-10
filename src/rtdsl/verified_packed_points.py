"""Generic one-pass proof for immutable packed point records.

The certificate is a compiler/runtime capability, not caller-provided
metadata.  It snapshots one packed 2-D or 3-D point array into immutable
``bytes``, validates unique U32 IDs once, and lets one downstream native owner
consume the exact snapshot without rescanning its contents.
"""

from __future__ import annotations

import ctypes
import hashlib
import hmac
import os
import secrets

import numpy as np

from .embree_runtime import (
    PackedPoints,
    _RtdlPoint,
    _RtdlPoint3D,
)
from .optix_runtime import pack_points


_CERTIFICATE_SECRET = secrets.token_bytes(32)
_ISSUER_AUTHORITY = object()
_CONSUMER_AUTHORITY = object()

_PY_BYTES_AS_STRING = ctypes.pythonapi.PyBytes_AsString
_PY_BYTES_AS_STRING.argtypes = [ctypes.py_object]
_PY_BYTES_AS_STRING.restype = ctypes.c_void_p


def _record_type(dimension: int):
    if dimension == 2:
        return _RtdlPoint
    if dimension == 3:
        return _RtdlPoint3D
    raise ValueError("packed points dimension must be 2 or 3")


def _bytes_address(storage: bytes) -> int:
    address = _PY_BYTES_AS_STRING(storage)
    if not address:
        raise RuntimeError("immutable packed-point storage has no address")
    return int(address)


class VerifiedUniqueU32PackedPoints:
    """Single-consumer proof over one immutable packed-points ABI snapshot.

    Supported Python APIs cannot mutate the bytes-backed snapshot.  Arbitrary
    raw-memory writes by code with unrestricted ``ctypes`` process authority
    are outside this Python certificate's threat model, as they are for the
    existing immutable point-column-domain certificate.
    """

    __slots__ = (
        "_storage",
        "_storage_sha256",
        "_storage_object_id",
        "_native_address",
        "_dimension",
        "_count",
        "_record_size",
        "_record_alignment",
        "_process_id",
        "_generation",
        "_generation_sha256",
        "_consumed",
        "_facts",
        "_seal",
        "_identity_digest",
        "_validation_count",
    )

    contract = "rtdl.verified_unique_u32_packed_points.v1"

    def __init__(
        self,
        storage: bytes,
        *,
        dimension: int,
        count: int,
        record_size: int,
        record_alignment: int,
        _authority,
    ) -> None:
        if _authority is not _ISSUER_AUTHORITY:
            raise RuntimeError(
                "verified packed-points capability requires compiler authority"
            )
        if type(storage) is not bytes:
            raise TypeError("verified packed-points storage must be exact bytes")
        object.__setattr__(self, "_storage", storage)
        object.__setattr__(
            self, "_storage_sha256", hashlib.sha256(storage).hexdigest()
        )
        object.__setattr__(self, "_storage_object_id", id(storage))
        object.__setattr__(self, "_native_address", _bytes_address(storage))
        object.__setattr__(self, "_dimension", int(dimension))
        object.__setattr__(self, "_count", int(count))
        object.__setattr__(self, "_record_size", int(record_size))
        object.__setattr__(self, "_record_alignment", int(record_alignment))
        object.__setattr__(self, "_process_id", os.getpid())
        generation = secrets.token_bytes(32)
        object.__setattr__(self, "_generation", generation)
        object.__setattr__(
            self, "_generation_sha256", hashlib.sha256(generation).hexdigest()
        )
        object.__setattr__(self, "_consumed", False)
        object.__setattr__(self, "_validation_count", 1)
        object.__setattr__(self, "_facts", self._current_facts())
        object.__setattr__(self, "_seal", self._issue_seal())
        object.__setattr__(
            self,
            "_identity_digest",
            hashlib.sha256(self._binding_payload()).hexdigest(),
        )
        self.validate()

    def __setattr__(self, name, value) -> None:
        raise AttributeError(
            "verified packed-points capability cannot be modified"
        )

    def __copy__(self):
        raise TypeError("verified packed-points capability is not copyable")

    def __deepcopy__(self, memo):
        raise TypeError("verified packed-points capability is not copyable")

    def __reduce_ex__(self, protocol):
        raise TypeError("verified packed-points capability is not serializable")

    def _current_facts(self) -> tuple[object, ...]:
        return (
            self.contract,
            id(self._storage),
            len(self._storage),
            self._storage_sha256,
            _bytes_address(self._storage),
            self._dimension,
            self._count,
            self._record_size,
            self._record_alignment,
            self._process_id,
            self._generation_sha256,
            self._consumed,
            self._validation_count,
        )

    def _binding_payload(self) -> bytes:
        return (
            repr(self._facts) + "\x00" + self._generation.hex()
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _CERTIFICATE_SECRET,
            self._binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def validate(self, *, require_fresh: bool = True) -> None:
        record_type = _record_type(self._dimension)
        if (
            type(self) is not VerifiedUniqueU32PackedPoints
            or type(self._storage) is not bytes
            or self._dimension not in {2, 3}
            or self._count < 0
            or self._record_size != ctypes.sizeof(record_type)
            or self._record_alignment != ctypes.alignment(record_type)
            or len(self._storage) != self._count * self._record_size
            or id(self._storage) != self._storage_object_id
            or _bytes_address(self._storage) != self._native_address
            or self._native_address % self._record_alignment != 0
            or os.getpid() != self._process_id
            or hashlib.sha256(self._generation).hexdigest()
            != self._generation_sha256
            or self._current_facts() != self._facts
            or not isinstance(self._seal, str)
            or not hmac.compare_digest(self._seal, self._issue_seal())
            or not hmac.compare_digest(
                self._identity_digest,
                hashlib.sha256(self._binding_payload()).hexdigest(),
            )
            or self._validation_count != 1
            or (require_fresh and self._consumed)
        ):
            raise RuntimeError(
                "verified packed-points capability binding changed or was consumed"
            )

    @property
    def count(self) -> int:
        self.validate()
        return self._count

    @property
    def dimension(self) -> int:
        self.validate()
        return self._dimension

    @property
    def identity_digest(self) -> str:
        self.validate()
        return self._identity_digest

    def to_metadata(self) -> dict[str, object]:
        self.validate()
        return {
            "contract": self.contract,
            "dimension": self._dimension,
            "count": self._count,
            "record_size": self._record_size,
            "record_alignment": self._record_alignment,
            "storage_byte_count": len(self._storage),
            "storage_sha256": self._storage_sha256,
            "generation_sha256": self._generation_sha256,
            "identity_digest": self._identity_digest,
            "unique_u32_validation_count": 1,
            "immutable_storage_kind": "python_bytes_packed_abi_snapshot",
            "caller_alias_retained": False,
            "content_rescan_required_after_issue": False,
            "duplicate_id_scan_repeated_after_issue": False,
            "single_consumer": True,
            "process_bound": True,
        }

    def _consume(self, *, _authority):
        if _authority is not _CONSUMER_AUTHORITY:
            raise RuntimeError(
                "verified packed-points capability requires native-owner authority"
            )
        self.validate()
        metadata = self.to_metadata()
        lease = _ConsumedVerifiedPackedPoints(
            storage=self._storage,
            native_address=self._native_address,
            count=self._count,
            dimension=self._dimension,
            identity_digest=self._identity_digest,
            metadata=metadata,
        )
        object.__setattr__(self, "_consumed", True)
        object.__setattr__(self, "_facts", self._current_facts())
        object.__setattr__(self, "_seal", self._issue_seal())
        object.__setattr__(
            self,
            "_identity_digest",
            hashlib.sha256(self._binding_payload()).hexdigest(),
        )
        self.validate(require_fresh=False)
        return lease


class _ConsumedVerifiedPackedPoints:
    """Internal strong-reference lease for one synchronous native call."""

    __slots__ = (
        "storage",
        "native_address",
        "count",
        "dimension",
        "identity_digest",
        "metadata",
    )

    def __init__(
        self,
        *,
        storage: bytes,
        native_address: int,
        count: int,
        dimension: int,
        identity_digest: str,
        metadata: dict[str, object],
    ) -> None:
        self.storage = storage
        self.native_address = native_address
        self.count = count
        self.dimension = dimension
        self.identity_digest = identity_digest
        self.metadata = metadata

    @property
    def native_pointer(self) -> ctypes.c_void_p:
        if (
            type(self.storage) is not bytes
            or _bytes_address(self.storage) != self.native_address
        ):
            raise RuntimeError("consumed packed-points storage binding changed")
        return ctypes.c_void_p(self.native_address)


def issue_verified_unique_u32_packed_points(
    points,
    *,
    dimension: int,
    path: str,
) -> VerifiedUniqueU32PackedPoints:
    """Snapshot, validate once, and seal packed points for one consumer."""

    if dimension not in {2, 3}:
        raise ValueError("dimension must be 2 or 3")
    packed = (
        points
        if isinstance(points, PackedPoints)
        else pack_points(records=points, dimension=dimension)
    )
    if type(packed) is not PackedPoints:
        raise TypeError(f"{path} requires exact PackedPoints")
    if packed.dimension != dimension:
        raise ValueError(f"{path} requires {dimension}-D points")
    if (
        not isinstance(packed.count, int)
        or isinstance(packed.count, bool)
        or packed.count < 0
    ):
        raise ValueError(f"{path} point count must be a nonnegative integer")
    record_type = _record_type(dimension)
    record_size = ctypes.sizeof(record_type)
    byte_count = int(packed.count) * record_size
    try:
        if ctypes.sizeof(packed.records) != byte_count:
            raise ValueError(f"{path} packed ABI length differs from point count")
        source_address = ctypes.addressof(packed.records)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{path} requires a contiguous ctypes packed ABI") from exc
    storage = ctypes.string_at(source_address, byte_count)
    ids = np.ndarray(
        shape=(int(packed.count),),
        dtype=np.uint32,
        buffer=storage,
        offset=0,
        strides=(record_size,),
    )
    if int(np.unique(ids).size) != int(packed.count):
        raise ValueError(f"{path} point IDs must be unique")
    return VerifiedUniqueU32PackedPoints(
        storage,
        dimension=dimension,
        count=int(packed.count),
        record_size=record_size,
        record_alignment=ctypes.alignment(record_type),
        _authority=_ISSUER_AUTHORITY,
    )


def consume_verified_unique_u32_packed_points(
    capability: VerifiedUniqueU32PackedPoints,
    *,
    dimension: int,
):
    """Consume an exact capability for one synchronous native owner."""

    if type(capability) is not VerifiedUniqueU32PackedPoints:
        raise TypeError(
            "native packed-points owner requires exact "
            "VerifiedUniqueU32PackedPoints"
        )
    capability.validate()
    if capability.dimension != dimension:
        raise ValueError(f"verified packed points require dimension {dimension}")
    return capability._consume(_authority=_CONSUMER_AUTHORITY)


__all__ = [
    "VerifiedUniqueU32PackedPoints",
    "consume_verified_unique_u32_packed_points",
    "issue_verified_unique_u32_packed_points",
]
