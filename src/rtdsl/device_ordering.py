from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from .device_column_row_buffer import DeviceColumnBuffer


DEVICE_ORDER_BY_CONTRACT_VERSION = "rtdl.device_order_by.v2_14_4.public.v1"
DEVICE_ORDER_BY_API_MATURITY = "public_contract_device_columnar_prepared_pipeline"
DEVICE_ORDER_BY_SUPPORTED_SIGNATURES = ("i64_f64_i64_i64_lex",)
DEVICE_ORDER_BY_BACKENDS = ("cpu_reference", "native_cuda")
DEVICE_ORDER_BY_CLAIM_BOUNDARY = (
    "device_order_by is a generic RTDL ordering contract over typed columns. "
    "v2.14.4 publicly supports the i64,f64,i64,i64 lexicographic signature, "
    "with deterministic tie behavior supplied by an explicit final order key. "
    "It does not authorize public speedup wording, true-zero-copy wording, "
    "app-specific ordering semantics, or public device_group_by promotion."
)

_I64_TYPESTRINGS = {"<i8", ">i8", "|i8"}
_F64_TYPESTRINGS = {"<f8", ">f8", "|f8"}
_SUPPORTED_SIGNATURE_COLUMNS = {
    "i64_f64_i64_i64_lex": ("int64", "float64", "int64", "int64"),
}


@dataclass(frozen=True)
class DeviceOrderByResult:
    backend: str
    signature: str
    keys: tuple[str, ...]
    row_count: int
    order_indices: Any = field(default=None, compare=False)
    sorted_columns: Mapping[str, Any] | None = field(default=None, compare=False)
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": DEVICE_ORDER_BY_CONTRACT_VERSION,
            "api_maturity": DEVICE_ORDER_BY_API_MATURITY,
            "backend": self.backend,
            "signature": self.signature,
            "keys": self.keys,
            "row_count": int(self.row_count),
            "has_order_indices": self.order_indices is not None,
            "has_sorted_columns": self.sorted_columns is not None,
            "metadata": dict(self.metadata),
            "lexicographic_ascending": True,
            "explicit_final_tie_key_required": True,
            "stable_sort_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_schema_allowed": False,
            "device_group_by_public_claim_authorized": False,
            "claim_boundary": DEVICE_ORDER_BY_CLAIM_BOUNDARY,
        }


def describe_device_order_by_contract() -> dict[str, Any]:
    return {
        "contract_version": DEVICE_ORDER_BY_CONTRACT_VERSION,
        "api_maturity": DEVICE_ORDER_BY_API_MATURITY,
        "supported_signatures": DEVICE_ORDER_BY_SUPPORTED_SIGNATURES,
        "supported_backends": DEVICE_ORDER_BY_BACKENDS,
        "semantics": "lexicographic ascending over declared key columns",
        "explicit_final_tie_key_required": True,
        "supports_public_device_order_by": True,
        "supports_public_device_group_by": False,
        "native_cuda_backend": "rtdl_cuda_sort_i64_f64_i64_i64_lex",
        "native_cuda_backend_optional": True,
        "cpu_reference_available": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_schema_allowed": False,
        "device_group_by_public_claim_authorized": False,
        "claim_boundary": DEVICE_ORDER_BY_CLAIM_BOUNDARY,
    }


def validate_device_order_by_contract(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict(contract or describe_device_order_by_contract())
    errors: list[str] = []
    if metadata.get("contract_version") != DEVICE_ORDER_BY_CONTRACT_VERSION:
        errors.append("unexpected device_order_by contract version")
    if tuple(metadata.get("supported_signatures", ())) != DEVICE_ORDER_BY_SUPPORTED_SIGNATURES:
        errors.append("device_order_by supported signatures changed")
    if tuple(metadata.get("supported_backends", ())) != DEVICE_ORDER_BY_BACKENDS:
        errors.append("device_order_by supported backends changed")
    if not metadata.get("explicit_final_tie_key_required"):
        errors.append("device_order_by must require an explicit final tie key")
    for flag in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "app_specific_schema_allowed",
        "device_group_by_public_claim_authorized",
    ):
        if metadata.get(flag):
            errors.append(f"{flag} must remain false")
    return {
        "contract_version": DEVICE_ORDER_BY_CONTRACT_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "claim_boundary": DEVICE_ORDER_BY_CLAIM_BOUNDARY,
    }


def device_order_by(
    columns: DeviceColumnBuffer | Mapping[str, Any],
    *,
    keys: Sequence[str],
    signature: str = "i64_f64_i64_i64_lex",
    backend: str = "cpu_reference",
) -> DeviceOrderByResult:
    """Order typed columns by explicit lexicographic keys.

    The public v2.14.4 surface supports one proven signature:
    ``int64, float64, int64, int64``.  The fourth column is the explicit final
    tie/order key; callers that need stable behavior must provide it.
    """

    resolved_keys = tuple(str(key) for key in keys)
    _validate_order_by_request(signature=signature, backend=backend, keys=resolved_keys)
    source_columns = columns.columns if isinstance(columns, DeviceColumnBuffer) else dict(columns)
    ordered_columns = _resolve_key_columns(source_columns, resolved_keys)
    if backend == "cpu_reference":
        return _device_order_by_reference_i64_f64_i64_i64(resolved_keys, ordered_columns)
    return _device_order_by_native_cuda(columns, resolved_keys, ordered_columns)


def device_order_by_reference_i64_f64_i64_i64(
    *,
    key0: Any,
    key1: Any,
    key2: Any,
    order_key: Any,
    key_names: Sequence[str] = ("key0", "key1", "key2", "order_key"),
) -> DeviceOrderByResult:
    keys = tuple(str(key) for key in key_names)
    if len(keys) != 4:
        raise ValueError("i64_f64_i64_i64 reference order requires exactly four key names")
    return _device_order_by_reference_i64_f64_i64_i64(
        keys,
        {
            keys[0]: key0,
            keys[1]: key1,
            keys[2]: key2,
            keys[3]: order_key,
        },
    )


def _device_order_by_reference_i64_f64_i64_i64(
    keys: tuple[str, ...],
    columns: Mapping[str, Any],
) -> DeviceOrderByResult:
    arrays = tuple(np.asarray(columns[key]) for key in keys)
    row_count = _validate_signature_columns(keys, arrays, signature="i64_f64_i64_i64_lex")
    order = np.lexsort((arrays[3], arrays[2], arrays[1], arrays[0])).astype(np.int64, copy=False)
    sorted_columns = {key: np.asarray(columns[key])[order] for key in keys}
    return DeviceOrderByResult(
        backend="cpu_reference",
        signature="i64_f64_i64_i64_lex",
        keys=keys,
        row_count=row_count,
        order_indices=order,
        sorted_columns=sorted_columns,
        metadata={
            "reference_backend": "numpy_lexsort",
            "device_resident_candidate": False,
            "materializes_host_rows_for_bridge": True,
        },
    )


def _device_order_by_native_cuda(
    columns: DeviceColumnBuffer | Mapping[str, Any],
    keys: tuple[str, ...],
    key_columns: Mapping[str, Any],
) -> DeviceOrderByResult:
    if not isinstance(columns, DeviceColumnBuffer):
        raise ValueError("native_cuda device_order_by requires a DeviceColumnBuffer")
    if not columns.device_resident_candidate or columns.materializes_host_rows_for_bridge:
        raise ValueError("native_cuda device_order_by requires device-resident columns")
    row_count = _validate_signature_columns(
        keys,
        tuple(key_columns[key] for key in keys),
        signature="i64_f64_i64_i64_lex",
        require_cuda=True,
    )
    from . import optix_runtime

    metadata = optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device(
        edge_key_device_ptr=_cuda_device_pointer(key_columns[keys[0]], keys[0]),
        dist_key_device_ptr=_cuda_device_pointer(key_columns[keys[1]], keys[1]),
        tie_key_device_ptr=_cuda_device_pointer(key_columns[keys[2]], keys[2]),
        order_key_device_ptr=_cuda_device_pointer(key_columns[keys[3]], keys[3]),
        count=row_count,
    )
    metadata = dict(metadata)
    metadata.update(
        {
            "public_device_order_by_contract_version": DEVICE_ORDER_BY_CONTRACT_VERSION,
            "input_device_column_buffer": columns.to_metadata(),
            "device_resident_candidate": True,
            "materializes_host_rows_for_bridge": False,
            "input_key_columns_mutated_in_place": True,
        }
    )
    return DeviceOrderByResult(
        backend="native_cuda",
        signature="i64_f64_i64_i64_lex",
        keys=keys,
        row_count=row_count,
        metadata=metadata,
    )


def _validate_order_by_request(*, signature: str, backend: str, keys: tuple[str, ...]) -> None:
    if signature not in DEVICE_ORDER_BY_SUPPORTED_SIGNATURES:
        raise ValueError("unsupported device_order_by signature")
    if backend not in DEVICE_ORDER_BY_BACKENDS:
        raise ValueError("unsupported device_order_by backend")
    if len(keys) != 4:
        raise ValueError("i64_f64_i64_i64 device_order_by requires exactly four keys")
    if len(set(keys)) != len(keys):
        raise ValueError("device_order_by key names must be unique")


def _resolve_key_columns(
    columns: Mapping[str, Any],
    keys: tuple[str, ...],
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key in keys:
        if key not in columns:
            raise ValueError(f"device_order_by key {key!r} is missing from columns")
        resolved[key] = columns[key]
    return resolved


def _validate_signature_columns(
    keys: tuple[str, ...],
    columns: Sequence[Any],
    *,
    signature: str,
    require_cuda: bool = False,
) -> int:
    expected = _SUPPORTED_SIGNATURE_COLUMNS[signature]
    lengths = [_column_length(column) for column in columns]
    if len(set(lengths)) != 1:
        raise ValueError("device_order_by key columns must have identical lengths")
    for key, column, dtype in zip(keys, columns, expected):
        if not _column_matches_dtype(column, dtype):
            raise ValueError(f"device_order_by key {key!r} must be {dtype}")
        if require_cuda and not _has_cuda_array_interface(column):
            raise ValueError(f"device_order_by key {key!r} must expose __cuda_array_interface__")
    return int(lengths[0])


def _column_length(column: Any) -> int:
    shape = getattr(column, "shape", None)
    if shape is not None:
        if len(shape) == 0:
            raise ValueError("device_order_by key columns must be one-dimensional")
        return int(shape[0])
    return len(column)


def _column_matches_dtype(column: Any, dtype: str) -> bool:
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        typestr = str(cuda_interface.get("typestr", ""))
        return typestr in (_I64_TYPESTRINGS if dtype == "int64" else _F64_TYPESTRINGS)
    try:
        return str(np.asarray(column).dtype) == dtype
    except Exception:
        return False


def _has_cuda_array_interface(column: Any) -> bool:
    return isinstance(getattr(column, "__cuda_array_interface__", None), Mapping)


def _cuda_device_pointer(column: Any, key: str) -> int:
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if not isinstance(cuda_interface, Mapping):
        raise ValueError(f"device_order_by key {key!r} does not expose __cuda_array_interface__")
    data = cuda_interface.get("data")
    if not (isinstance(data, tuple) and data):
        raise ValueError(f"device_order_by key {key!r} has no CUDA data pointer")
    pointer = int(data[0])
    if pointer <= 0:
        raise ValueError(f"device_order_by key {key!r} has an invalid CUDA data pointer")
    return pointer


__all__ = [
    "DEVICE_ORDER_BY_API_MATURITY",
    "DEVICE_ORDER_BY_BACKENDS",
    "DEVICE_ORDER_BY_CLAIM_BOUNDARY",
    "DEVICE_ORDER_BY_CONTRACT_VERSION",
    "DEVICE_ORDER_BY_SUPPORTED_SIGNATURES",
    "DeviceOrderByResult",
    "describe_device_order_by_contract",
    "device_order_by",
    "device_order_by_reference_i64_f64_i64_i64",
    "validate_device_order_by_contract",
]
