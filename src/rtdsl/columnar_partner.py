from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from . import partner as _partner


PARTNER_RESIDENT_COLUMNAR_BACKENDS = ("optix",)
PARTNER_RESIDENT_COLUMNAR_TRANSFER_MODE = "partner_resident_column_descriptor_only"
PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_TARGET = (
    "optix_partner_resident_columnar_payload_native_execution"
)
PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_STATUS = (
    "blocked_pending_optix_device_column_abi"
)
PARTNER_RESIDENT_COLUMNAR_REQUIRED_OPTIX_SYMBOL = (
    "rtdl_optix_columnar_payload_create_from_device_columns"
)


@dataclass(frozen=True)
class PartnerResidentColumnHandoff:
    name: str
    logical_kind: str
    handoff: _partner.RtdlDevicePointerHandoff

    def to_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "logical_kind": self.logical_kind,
            **self.handoff.to_metadata(),
        }


@dataclass(frozen=True)
class PartnerResidentColumnarRecordSet:
    backend: str
    row_count: int
    device_type: str
    device_id: int
    fields: tuple[PartnerResidentColumnHandoff, ...]
    row_id_uniqueness_validated: bool = False
    native_execution_authorized: bool = False
    true_zero_copy_authorized: bool = False
    transfer_mode: str = PARTNER_RESIDENT_COLUMNAR_TRANSFER_MODE

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "row_count": int(self.row_count),
            "device": f"{self.device_type}:{self.device_id}",
            "field_names": self.field_names,
            "fields": tuple(field.to_metadata() for field in self.fields),
            "source_protocols": tuple(sorted({field.handoff.source_protocol for field in self.fields})),
            "transfer_mode": self.transfer_mode,
            "row_id_uniqueness_validated": self.row_id_uniqueness_validated,
            "native_execution_authorized": self.native_execution_authorized,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "claim_boundary": (
                "Descriptor-only partner-resident columnar handoff. Native OptiX execution, "
                "row-id uniqueness validation, true zero-copy, speedup, SQL, DBMS, and "
                "whole-app claims are not authorized."
            ),
        }


def partner_resident_columnar_native_execution_requirements() -> dict[str, Any]:
    return {
        "target": PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_TARGET,
        "backend": "optix",
        "status": PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_STATUS,
        "required_native_symbols": (
            PARTNER_RESIDENT_COLUMNAR_REQUIRED_OPTIX_SYMBOL,
        ),
        "current_blockers": (
            "Current executable OptiX columnar payload ABI accepts host RtdlPayloadField pointers.",
            "Device-column OptiX symbol is a fail-closed scaffold only.",
            "Current OptiX DB dataset stores host RtdlDbScalar row_values.",
            "Current OptiX exact filtering and grouped count/sum reductions read host row_values.",
            "Goal2505 descriptors explicitly set native_execution_authorized=False.",
        ),
        "required_device_column_abi": (
            "column name",
            "logical kind",
            "dtype token",
            "CUDA device pointer",
            "row count",
            "CUDA device id",
            "contiguous layout contract",
        ),
        "first_executable_slice": (
            "numeric RayDB-style columns only",
            "row_id dtype int64 or uint32",
            "data column dtype int64, uint32, or float64",
            "count and int64 sum aggregates only",
            "single int64-compatible group key",
            "device-side exact predicate evaluation",
            "device-side grouped reduction with host result materialization only at the boundary",
        ),
        "excluded_scope": (
            "text columns",
            "bool columns",
            "min/max/avg aggregates",
            "SQL or DBMS claim",
            "whole-app speedup claim",
            "true zero-copy public claim",
        ),
        "claim_boundary": (
            "Partner-resident columnar descriptors are not executable by the OptiX native DB "
            "path until a device-column ABI and device-side predicate/reduction path exist. "
            "Do not fall back to hidden device-to-host table staging while claiming native "
            "partner-resident execution."
        ),
    }


def plan_partner_resident_columnar_native_execution(
    descriptor: PartnerResidentColumnarRecordSet,
) -> dict[str, Any]:
    if not isinstance(descriptor, PartnerResidentColumnarRecordSet):
        raise ValueError("native execution planning requires a PartnerResidentColumnarRecordSet")
    requirements = partner_resident_columnar_native_execution_requirements()
    blocked_reasons = list(requirements["current_blockers"])
    if descriptor.backend != "optix":
        blocked_reasons.append("only the OptiX backend is in native-execution design scope")
    if descriptor.native_execution_authorized:
        blocked_reasons.append("native symbol and device-side execution path are not validated")
    return {
        "target": requirements["target"],
        "backend": descriptor.backend,
        "status": requirements["status"],
        "native_execution_allowed": False,
        "required_native_symbols": requirements["required_native_symbols"],
        "blocked_reasons": tuple(blocked_reasons),
        "descriptor_field_names": descriptor.field_names,
        "descriptor_row_count": descriptor.row_count,
        "descriptor_device": f"{descriptor.device_type}:{descriptor.device_id}",
        "claim_boundary": requirements["claim_boundary"],
    }


def prepare_partner_resident_columnar_record_set(
    record_set: Mapping[str, Any],
    *,
    backend: str = "optix",
) -> PartnerResidentColumnarRecordSet:
    normalized_backend = str(backend).strip().lower()
    if normalized_backend not in PARTNER_RESIDENT_COLUMNAR_BACKENDS:
        raise ValueError(
            "partner-resident columnar record sets currently support only backend='optix'"
        )
    if not isinstance(record_set, Mapping):
        raise ValueError("partner-resident columnar record set must be a mapping")
    row_ids = record_set.get("row_ids")
    raw_columns = record_set.get("columns")
    if row_ids is None:
        raise ValueError("partner-resident columnar record set requires `row_ids`")
    if not isinstance(raw_columns, Mapping):
        raise ValueError("partner-resident columnar record set requires a `columns` mapping")
    if "row_id" in {str(name) for name in raw_columns.keys()}:
        raise ValueError("partner-resident columnar record set reserves the `row_id` field name")
    if not raw_columns:
        raise ValueError("partner-resident columnar record set requires at least one data column")

    field_inputs = {"row_id": row_ids, **{str(name): value for name, value in raw_columns.items()}}
    fields: list[PartnerResidentColumnHandoff] = []
    expected_count: int | None = None
    expected_device: tuple[str, int] | None = None
    for name, value in field_inputs.items():
        handoff = _partner.prepare_direct_device_pointer_handoff(value, access="read")
        if handoff.device_type != "cuda":
            raise ValueError("partner-resident columnar record sets require CUDA partner columns")
        if len(handoff.shape) != 1:
            raise ValueError(f"partner-resident column `{name}` must be one-dimensional")
        dtype = _dtype_token(handoff.dtype)
        logical_kind = _logical_kind_for_field(name, dtype)
        if not _contiguous_1d_strides(handoff.strides, itemsize=_dtype_itemsize(dtype)):
            raise ValueError(f"partner-resident column `{name}` must be contiguous")
        count = int(handoff.shape[0])
        if expected_count is None:
            expected_count = count
            if expected_count <= 0:
                raise ValueError("partner-resident columnar record set requires at least one row")
        elif count != expected_count:
            raise ValueError("partner-resident columns must have matching lengths")
        device = (handoff.device_type, handoff.device_id)
        if expected_device is None:
            expected_device = device
        elif device != expected_device:
            raise ValueError("partner-resident columns must live on the same CUDA device")
        fields.append(PartnerResidentColumnHandoff(name=name, logical_kind=logical_kind, handoff=handoff))

    assert expected_count is not None
    assert expected_device is not None
    return PartnerResidentColumnarRecordSet(
        backend=normalized_backend,
        row_count=expected_count,
        device_type=expected_device[0],
        device_id=expected_device[1],
        fields=tuple(fields),
    )


def _logical_kind_for_field(name: str, dtype: str) -> str:
    if name == "row_id":
        if dtype not in {"int64", "uint32"}:
            raise ValueError("partner-resident row_ids must use dtype int64 or uint32")
        return "row_id"
    if dtype in {"int64", "uint32"}:
        return "int64"
    if dtype in {"float64", "double"}:
        return "float64"
    raise ValueError(
        f"partner-resident column `{name}` must use dtype int64, uint32, or float64"
    )


def _dtype_token(dtype: str) -> str:
    normalized = str(dtype).strip().lower()
    if normalized.startswith("torch."):
        normalized = normalized.removeprefix("torch.")
    if normalized.startswith("numpy."):
        normalized = normalized.removeprefix("numpy.")
    aliases = {
        "int64_t": "int64",
        "longlong": "int64",
        "long long": "int64",
        "uint32_t": "uint32",
        "unsigned int": "uint32",
        "float64": "float64",
        "double": "double",
    }
    return aliases.get(normalized, normalized)


def _dtype_itemsize(dtype: str) -> int:
    if dtype in {"int64", "float64", "double"}:
        return 8
    if dtype == "uint32":
        return 4
    raise ValueError(f"unsupported partner-resident dtype: {dtype}")


def _contiguous_1d_strides(strides: tuple[int, ...] | None, *, itemsize: int) -> bool:
    return strides in (None, (1,), (itemsize,))
