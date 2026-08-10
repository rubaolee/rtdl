"""Exact, app-neutral dense ordinal encodings for integral host columns."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Sequence


@dataclass(frozen=True)
class ExactDenseOrdinalEncoding:
    """Sorted unique values and one exact dense ordinal per input row."""

    unique_values: object
    ordinals: object
    strategy: str
    input_row_count: int
    input_column_count: int
    value_dtype: str
    ordinal_dtype: str
    domain_minimum: int | None
    domain_maximum: int | None
    domain_span: int | None
    certificate_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.exact_dense_ordinal_encoding.v1",
            "strategy": self.strategy,
            "input_row_count": self.input_row_count,
            "input_column_count": self.input_column_count,
            "unique_value_count": int(self.unique_values.shape[0]),
            "value_dtype": self.value_dtype,
            "ordinal_dtype": self.ordinal_dtype,
            "domain_minimum": self.domain_minimum,
            "domain_maximum": self.domain_maximum,
            "domain_span": self.domain_span,
            "certificate_digest": self.certificate_digest,
            "sorted_unique_values": True,
            "dense_zero_based_ordinals": True,
            "exact_numpy_semantics": True,
            "application_identity_used": False,
            "fallback_available": True,
        }


def _readonly(array):
    import numpy as np

    value = np.ascontiguousarray(array)
    value.setflags(write=False)
    return value


def _ordinal_dtype(dtype):
    import numpy as np

    resolved = np.dtype(dtype)
    if resolved.kind != "u" or resolved.itemsize not in {1, 2, 4, 8}:
        raise ValueError("ordinal_dtype must be uint8, uint16, uint32, or uint64")
    return resolved


def _certificate(
    *,
    strategy: str,
    input_row_count: int,
    input_column_count: int,
    value_dtype: str,
    ordinal_dtype: str,
    unique_value_count: int,
    domain_minimum: int | None,
    domain_maximum: int | None,
    domain_span: int | None,
) -> str:
    payload = {
        "contract": "rtdl.exact_dense_ordinal_encoding.v1",
        "strategy": strategy,
        "input_row_count": input_row_count,
        "input_column_count": input_column_count,
        "value_dtype": value_dtype,
        "ordinal_dtype": ordinal_dtype,
        "unique_value_count": unique_value_count,
        "domain_minimum": domain_minimum,
        "domain_maximum": domain_maximum,
        "domain_span": domain_span,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def exact_dense_ordinal_encode_integral(
    values,
    *,
    ordinal_dtype="uint64",
    max_lookup_span: int = 1 << 20,
    max_lookup_span_to_rows: int = 8,
) -> ExactDenseOrdinalEncoding:
    """Encode one integral column with exact sorted-unique NumPy semantics.

    Constant and bounded-domain columns avoid comparison sorting.  Sparse or
    large domains fall back to ``np.unique(..., return_inverse=True)``.
    """

    import numpy as np

    source = np.asarray(values)
    if source.ndim != 1 or source.dtype.kind not in {"i", "u"}:
        raise ValueError("values must be a one-dimensional integral column")
    if (
        not isinstance(max_lookup_span, int)
        or isinstance(max_lookup_span, bool)
        or max_lookup_span <= 0
        or not isinstance(max_lookup_span_to_rows, int)
        or isinstance(max_lookup_span_to_rows, bool)
        or max_lookup_span_to_rows <= 0
    ):
        raise ValueError("lookup bounds must be positive integers")
    target_dtype = _ordinal_dtype(ordinal_dtype)
    row_count = int(source.shape[0])
    if row_count == 0:
        unique_values = np.empty(0, dtype=source.dtype)
        ordinals = np.empty(0, dtype=target_dtype)
        strategy = "empty"
        minimum = maximum = span = None
    else:
        minimum = int(source.min())
        maximum = int(source.max())
        span = maximum - minimum + 1
        if minimum == maximum:
            unique_values = np.asarray([minimum], dtype=source.dtype)
            ordinals = np.zeros(row_count, dtype=target_dtype)
            strategy = "constant"
        elif (
            span <= max_lookup_span
            and span <= max(4_096, row_count * max_lookup_span_to_rows)
        ):
            if source.dtype.kind == "u":
                # Keep arithmetic in the source's unsigned domain.  Passing a
                # Python integer above INT64_MAX to ``np.subtract`` is not
                # portable across NumPy versions even when the true span is
                # tiny and exactly representable.
                source_minimum = np.asarray(minimum, dtype=source.dtype)
                offsets = np.subtract(source, source_minimum).astype(
                    np.uint32,
                    copy=False,
                )
            else:
                offsets = np.empty(row_count, dtype=np.uint32)
                np.subtract(source, minimum, out=offsets, casting="unsafe")
            present = np.zeros(span, dtype=np.bool_)
            present[offsets] = True
            unique_offsets = np.flatnonzero(present)
            unique_count = int(unique_offsets.shape[0])
            if unique_count - 1 > int(np.iinfo(target_dtype).max):
                raise OverflowError(
                    "unique value count exceeds requested ordinal dtype"
                )
            lookup = np.zeros(span, dtype=target_dtype)
            lookup[unique_offsets] = np.arange(
                unique_count, dtype=target_dtype
            )
            ordinals = lookup[offsets]
            if source.dtype.kind == "u":
                unique_values = (
                    unique_offsets.astype(source.dtype, copy=False)
                    + np.asarray(minimum, dtype=source.dtype)
                )
            else:
                unique_values = (unique_offsets + minimum).astype(
                    source.dtype, copy=False
                )
            strategy = "bounded_integer_presence_rank"
        else:
            unique_values, inverse = np.unique(source, return_inverse=True)
            if int(unique_values.shape[0]) - 1 > int(np.iinfo(target_dtype).max):
                raise OverflowError(
                    "unique value count exceeds requested ordinal dtype"
                )
            ordinals = inverse.astype(target_dtype, copy=False)
            strategy = "numpy_unique_fallback"
    unique_values = _readonly(unique_values)
    ordinals = _readonly(ordinals)
    digest = _certificate(
        strategy=strategy,
        input_row_count=row_count,
        input_column_count=1,
        value_dtype=str(source.dtype),
        ordinal_dtype=str(target_dtype),
        unique_value_count=int(unique_values.shape[0]),
        domain_minimum=minimum,
        domain_maximum=maximum,
        domain_span=span,
    )
    return ExactDenseOrdinalEncoding(
        unique_values=unique_values,
        ordinals=ordinals,
        strategy=strategy,
        input_row_count=row_count,
        input_column_count=1,
        value_dtype=str(source.dtype),
        ordinal_dtype=str(target_dtype),
        domain_minimum=minimum,
        domain_maximum=maximum,
        domain_span=span,
        certificate_digest=digest,
    )


def exact_dense_row_ordinal_encode_integral(
    columns: Sequence[object],
    *,
    ordinal_dtype="uint32",
    max_lookup_span: int = 1 << 20,
) -> ExactDenseOrdinalEncoding:
    """Encode integral row keys; compose the fast single-column primitive."""

    import numpy as np

    values = tuple(np.asarray(column) for column in columns)
    if not values:
        raise ValueError("at least one integral key column is required")
    row_count = int(values[0].shape[0]) if values[0].ndim == 1 else -1
    if any(
        value.ndim != 1
        or value.dtype.kind not in {"i", "u"}
        or int(value.shape[0]) != row_count
        for value in values
    ):
        raise ValueError(
            "key columns must be equal-length one-dimensional integral arrays"
        )
    if len(values) == 1:
        scalar = exact_dense_ordinal_encode_integral(
            values[0],
            ordinal_dtype=ordinal_dtype,
            max_lookup_span=max_lookup_span,
        )
        unique_rows = _readonly(scalar.unique_values.reshape(-1, 1))
        digest = _certificate(
            strategy=scalar.strategy,
            input_row_count=row_count,
            input_column_count=1,
            value_dtype=scalar.value_dtype,
            ordinal_dtype=scalar.ordinal_dtype,
            unique_value_count=int(unique_rows.shape[0]),
            domain_minimum=scalar.domain_minimum,
            domain_maximum=scalar.domain_maximum,
            domain_span=scalar.domain_span,
        )
        return ExactDenseOrdinalEncoding(
            unique_values=unique_rows,
            ordinals=scalar.ordinals,
            strategy=scalar.strategy,
            input_row_count=row_count,
            input_column_count=1,
            value_dtype=scalar.value_dtype,
            ordinal_dtype=scalar.ordinal_dtype,
            domain_minimum=scalar.domain_minimum,
            domain_maximum=scalar.domain_maximum,
            domain_span=scalar.domain_span,
            certificate_digest=digest,
        )
    matrix = np.column_stack(values)
    unique_rows, inverse = np.unique(matrix, axis=0, return_inverse=True)
    target_dtype = _ordinal_dtype(ordinal_dtype)
    if int(unique_rows.shape[0]) - 1 > int(np.iinfo(target_dtype).max):
        raise OverflowError("unique row count exceeds requested ordinal dtype")
    ordinals = inverse.astype(target_dtype, copy=False)
    unique_rows = _readonly(unique_rows)
    ordinals = _readonly(ordinals)
    digest = _certificate(
        strategy="numpy_unique_rows_fallback",
        input_row_count=row_count,
        input_column_count=len(values),
        value_dtype=str(matrix.dtype),
        ordinal_dtype=str(target_dtype),
        unique_value_count=int(unique_rows.shape[0]),
        domain_minimum=None,
        domain_maximum=None,
        domain_span=None,
    )
    return ExactDenseOrdinalEncoding(
        unique_values=unique_rows,
        ordinals=ordinals,
        strategy="numpy_unique_rows_fallback",
        input_row_count=row_count,
        input_column_count=len(values),
        value_dtype=str(matrix.dtype),
        ordinal_dtype=str(target_dtype),
        domain_minimum=None,
        domain_maximum=None,
        domain_span=None,
        certificate_digest=digest,
    )


__all__ = (
    "ExactDenseOrdinalEncoding",
    "exact_dense_ordinal_encode_integral",
    "exact_dense_row_ordinal_encode_integral",
)
