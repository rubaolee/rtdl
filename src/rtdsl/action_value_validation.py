from __future__ import annotations

from collections.abc import Sequence
import hashlib
import hmac
from numbers import Integral
import secrets

import numpy as np


UINT32_MAX = (1 << 32) - 1
_SIGNED_I64_MIN = -(1 << 63)
_SIGNED_I64_MAX = (1 << 63) - 1
_GROUPED_I64_HOST_COLUMN_CERTIFICATE_SECRET = secrets.token_bytes(32)
_GROUPED_I64_HOST_COLUMN_ISSUER_AUTHORITY = object()


class VerifiedGroupedI64HostColumns:
    """Sealed exact-array proof for compiler-owned grouped-i64 host columns."""

    __slots__ = (
        "_groups",
        "_values",
        "_group_storage",
        "_value_storage",
        "_group_storage_sha256",
        "_value_storage_sha256",
        "_primitive_count",
        "_group_count",
        "_value_minimum",
        "_value_maximum",
        "_generation",
        "_generation_sha256",
        "_facts",
        "_seal",
        "_identity_digest",
    )
    contract = "rtdl.verified_grouped_i64_host_columns.v1"

    def __init__(
        self,
        groups: np.ndarray,
        values: np.ndarray,
        *,
        group_storage: bytes,
        value_storage: bytes,
        primitive_count: int,
        group_count: int,
        value_minimum: int | None,
        value_maximum: int | None,
        _authority,
    ) -> None:
        if _authority is not _GROUPED_I64_HOST_COLUMN_ISSUER_AUTHORITY:
            raise RuntimeError("verified grouped-i64 columns require compiler authority")
        self._groups = groups
        self._values = values
        self._group_storage = group_storage
        self._value_storage = value_storage
        self._group_storage_sha256 = hashlib.sha256(group_storage).hexdigest()
        self._value_storage_sha256 = hashlib.sha256(value_storage).hexdigest()
        self._primitive_count = primitive_count
        self._group_count = group_count
        self._value_minimum = value_minimum
        self._value_maximum = value_maximum
        self._generation = secrets.token_bytes(32)
        self._generation_sha256 = hashlib.sha256(self._generation).hexdigest()
        self._facts = self._current_facts()
        self._seal = self._issue_seal()
        self._identity_digest = hashlib.sha256(self._binding_payload()).hexdigest()
        self.validate()

    @staticmethod
    def _array_facts(array: np.ndarray) -> tuple[object, ...]:
        return (
            id(array),
            int(array.ctypes.data),
            array.dtype.str,
            tuple(int(value) for value in array.shape),
            tuple(int(value) for value in array.strides),
            bool(array.flags.c_contiguous),
            bool(array.flags.owndata),
            bool(array.flags.writeable),
            id(array.base) if array.base is not None else None,
        )

    def _current_facts(self) -> tuple[object, ...]:
        return (
            self.contract,
            self._primitive_count,
            self._group_count,
            self._value_minimum,
            self._value_maximum,
            id(self._group_storage),
            len(self._group_storage),
            self._group_storage_sha256,
            id(self._value_storage),
            len(self._value_storage),
            self._value_storage_sha256,
            self._array_facts(self._groups),
            self._array_facts(self._values),
        )

    def _binding_payload(self) -> bytes:
        return (
            repr(self._facts) + "\x00" + self._generation.hex()
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _GROUPED_I64_HOST_COLUMN_CERTIFICATE_SECRET,
            self._binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    @property
    def primitive_count(self) -> int:
        return self._primitive_count

    @property
    def group_count(self) -> int:
        return self._group_count

    @property
    def identity_digest(self) -> str:
        self.validate()
        return self._identity_digest

    @property
    def sum_domain_validation_count(self) -> int:
        return 1

    def validate(self) -> None:
        if (
            type(self) is not VerifiedGroupedI64HostColumns
            or type(self._groups) is not np.ndarray
            or type(self._values) is not np.ndarray
            or self._groups.dtype != np.dtype(np.uint32)
            or self._values.dtype != np.dtype(np.int64)
            or self._groups.shape != (self._primitive_count,)
            or self._values.shape != (self._primitive_count,)
            or type(self._group_storage) is not bytes
            or type(self._value_storage) is not bytes
            or not isinstance(self._group_storage_sha256, str)
            or not isinstance(self._value_storage_sha256, str)
            or self._groups.base is not self._group_storage
            or self._values.base is not self._value_storage
            or not self._groups.flags.c_contiguous
            or not self._values.flags.c_contiguous
            or self._groups.flags.owndata
            or self._values.flags.owndata
            or self._groups.flags.writeable
            or self._values.flags.writeable
            or hashlib.sha256(self._generation).hexdigest()
            != self._generation_sha256
            or self._current_facts() != self._facts
            or not isinstance(self._seal, str)
            or not hmac.compare_digest(self._seal, self._issue_seal())
            or not hmac.compare_digest(
                self._identity_digest,
                hashlib.sha256(self._binding_payload()).hexdigest(),
            )
        ):
            raise RuntimeError("verified grouped-i64 host-column binding changed")

    def validated_columns(self) -> tuple[np.ndarray, np.ndarray]:
        self.validate()
        return self._groups, self._values

    def to_metadata(self) -> dict[str, object]:
        self.validate()
        return {
            "contract": self.contract,
            "primitive_count": self._primitive_count,
            "group_count": self._group_count,
            "group_dtype": self._groups.dtype.str,
            "value_dtype": self._values.dtype.str,
            "value_minimum": self._value_minimum,
            "value_maximum": self._value_maximum,
            "sum_domain_validation_count": 1,
            "caller_alias_retained": False,
            "immutable_storage_kind": "python_bytes_backed_numpy_view",
            "arrays_contiguous_read_only": True,
            "content_rescan_required_after_issue": False,
            "identity_digest": self._identity_digest,
            "generation_sha256": self._generation_sha256,
        }


def _issue_verified_grouped_i64_host_columns(
    groups,
    values,
    *,
    primitive_count: int,
    group_count: int,
    primitive_includes=None,
    sink_group: int | None = None,
) -> VerifiedGroupedI64HostColumns:
    """Snapshot, validate, and seal immutable grouped-i64 host columns.

    Content is validated only after it has been copied into immutable ``bytes``
    storage.  Exact C-contiguous U32/I64 inputs therefore take one host copy;
    wider or non-contiguous integral inputs use a slower conversion path.
    """

    def immutable_integral_column(
        source,
        *,
        target_dtype,
        label: str,
        minimum: int,
        maximum: int,
    ) -> tuple[bytes, np.ndarray, int | None, int | None]:
        raw = np.asarray(source)
        if raw.ndim != 1 or raw.shape != (primitive_count,):
            raise ValueError(f"{label} must be a length-matched 1-D column")
        if raw.dtype.kind not in {"i", "u"}:
            raise TypeError(f"{label} entries must be lossless integers")
        contiguous = np.ascontiguousarray(raw)
        source_storage = contiguous.tobytes(order="C")
        snapshot = np.frombuffer(source_storage, dtype=contiguous.dtype)
        observed_minimum = int(snapshot.min()) if primitive_count else None
        observed_maximum = int(snapshot.max()) if primitive_count else None
        if primitive_count and (
            observed_minimum < minimum or observed_maximum > maximum
        ):
            raise OverflowError(f"{label} entries exceed target integer domain")
        target = np.dtype(target_dtype)
        if snapshot.dtype == target:
            storage = source_storage
        else:
            converted = np.asarray(snapshot, dtype=target, order="C")
            storage = converted.tobytes(order="C")
        immutable = np.frombuffer(storage, dtype=target)
        return storage, immutable, observed_minimum, observed_maximum

    if (
        not isinstance(primitive_count, int)
        or isinstance(primitive_count, bool)
        or primitive_count < 0
        or not isinstance(group_count, int)
        or isinstance(group_count, bool)
        or group_count < 0
    ):
        raise ValueError("primitive_count and group_count must be nonnegative integers")
    group_storage, immutable_groups, _, group_maximum = immutable_integral_column(
        groups,
        target_dtype=np.uint32,
        label="primitive_group_ids",
        minimum=0,
        maximum=UINT32_MAX,
    )
    value_storage, immutable_values, value_minimum, value_maximum = (
        immutable_integral_column(
            values,
            target_dtype=np.int64,
            label="primitive_values",
            minimum=_SIGNED_I64_MIN,
            maximum=_SIGNED_I64_MAX,
        )
    )
    logical_group_count = group_count if sink_group is None else sink_group
    if (
        not isinstance(logical_group_count, int)
        or isinstance(logical_group_count, bool)
        or logical_group_count < 0
        or (sink_group is not None and group_count != sink_group + 1)
    ):
        raise ValueError("sink-group encoding differs from physical group count")
    if primitive_count and group_maximum >= logical_group_count:
        raise ValueError("primitive_group_ids entries exceed logical group count")
    if primitive_includes is not None:
        includes = np.array(
            primitive_includes,
            dtype=np.bool_,
            order="C",
            copy=True,
        )
        if includes.ndim != 1 or includes.shape != (primitive_count,):
            raise ValueError("primitive_includes must be a length-matched 1-D column")
        include_storage = includes.tobytes(order="C")
        immutable_includes = np.frombuffer(include_storage, dtype=np.bool_)
        effective_groups = np.where(
            immutable_includes,
            immutable_groups,
            logical_group_count,
        ).astype(np.uint32, copy=False)
        group_storage = effective_groups.tobytes(order="C")
        immutable_groups = np.frombuffer(group_storage, dtype=np.uint32)
    if primitive_count:
        if max(0, value_maximum) * primitive_count > _SIGNED_I64_MAX:
            raise OverflowError(
                "grouped-i64 sum cannot be proven safe within signed int64"
            )
        if min(0, value_minimum) * primitive_count < _SIGNED_I64_MIN:
            raise OverflowError(
                "grouped-i64 sum cannot be proven safe within signed int64"
            )
    return VerifiedGroupedI64HostColumns(
        immutable_groups,
        immutable_values,
        group_storage=group_storage,
        value_storage=value_storage,
        primitive_count=primitive_count,
        group_count=group_count,
        value_minimum=value_minimum,
        value_maximum=value_maximum,
        _authority=_GROUPED_I64_HOST_COLUMN_ISSUER_AUTHORITY,
    )


def strict_u32_column(
    values,
    *,
    expected_length: int | None = None,
    require_unique: bool = False,
) -> np.ndarray:
    """Return a copied I64 column after validating the *original* U32 type.

    NumPy's dtype conversion is deliberately not used as validation: doing so
    would silently accept floats, booleans, strings, and object values by
    coercing them to integers.  Native integer arrays and ordinary Python
    integer sequences are accepted; booleans are never integers here.
    """

    if isinstance(values, np.ndarray):
        original = values
        if original.dtype.kind not in {"i", "u"}:
            raise ValueError("values must have an original integer dtype")
    elif isinstance(values, Sequence) and not isinstance(
        values, (str, bytes, bytearray)
    ):
        for value in values:
            if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
                raise ValueError(
                    "values must contain integers and must not contain booleans"
                )
        original = np.asarray(values)
        if original.dtype.kind not in {"i", "u"}:
            # A Python integer sequence can become object only when one of its
            # values cannot fit a native integer dtype.  Such a value cannot be
            # in the U32 domain, so fail before any narrowing conversion.
            raise ValueError("values must fit an original native integer dtype")
    else:
        original = np.asarray(values)
        if original.dtype.kind not in {"i", "u"}:
            raise ValueError("values must have an original integer dtype")

    if original.ndim != 1:
        raise ValueError("values must be a one-dimensional column")
    if expected_length is not None and original.shape != (expected_length,):
        raise ValueError(f"values must have shape ({expected_length},)")
    if original.size:
        if original.dtype.kind == "i" and bool(np.any(original < 0)):
            raise ValueError("values escaped the U32 domain")
        if bool(np.any(original > UINT32_MAX)):
            raise ValueError("values escaped the U32 domain")
    result = np.array(original, dtype=np.int64, order="C", copy=True)
    if require_unique and int(np.unique(result).size) != int(result.size):
        raise ValueError("values must be unique")
    return result


__all__ = [
    "UINT32_MAX",
    "VerifiedGroupedI64HostColumns",
    "strict_u32_column",
]
