from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .neutral_buffer_seam import V2_5_NEUTRAL_BUFFER_SEAM_VERSION
from .partner_continuation_protocol import V2_5_ALLOWED_PARTNERS
from .partner_continuation_protocol import V2_5_CONFORMANCE_PARTNER
from .partner_continuation_protocol import V2_5_CUPY_PREVIEW_OPERATIONS
from .partner_continuation_protocol import V2_5_FALLBACK_PARTNER
from .partner_continuation_protocol import V2_5_NUMBA_PREVIEW_OPERATIONS
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS
from .partner_continuation_protocol import V2_5_REFERENCE_PARTNER
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER
from .partner_continuation_protocol import V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED


V2_5_PARTNER_SUPPORT_MATRIX_VERSION = "rtdl.v2_5.partner_support_matrix.v1"
V2_5_SUPPORT_STATUS_REFERENCE = "reference_contract"
V2_5_SUPPORT_STATUS_PREVIEW = "preview_not_promoted"
V2_5_SUPPORT_STATUS_DESCRIPTOR = "descriptor_only"
V2_5_SUPPORT_STATUS_UNSUPPORTED = "unsupported_fail_closed"
V2_5_SUPPORT_STATUSES = (
    V2_5_SUPPORT_STATUS_REFERENCE,
    V2_5_SUPPORT_STATUS_PREVIEW,
    V2_5_SUPPORT_STATUS_DESCRIPTOR,
    V2_5_SUPPORT_STATUS_UNSUPPORTED,
)
V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY = (
    "v2.5 partner support rows declare conformance envelope only. They do not "
    "authorize RT traversal replacement, public speedup claims, release claims, "
    "or true zero-copy claims."
)


@dataclass(frozen=True)
class V25PartnerSupportCell:
    operation: str
    partner: str
    status: str
    execution_backend: str
    requires_neutral_buffer_seam: bool
    requires_cuda: bool = False
    requires_sm70_plus: bool = False
    same_contract_reference_required: bool = True
    promoted_performance_path: bool = False
    rt_traversal_replacement_allowed: bool = False
    public_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if self.operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            raise ValueError("support-cell operation is not a v2.5 continuation operation")
        if self.partner not in V2_5_ALLOWED_PARTNERS:
            raise ValueError("support-cell partner is not in V2_5_ALLOWED_PARTNERS")
        if self.status not in V2_5_SUPPORT_STATUSES:
            raise ValueError("unsupported v2.5 support-cell status")
        if self.promoted_performance_path:
            raise ValueError("v2.5 support matrix must not promote performance paths")
        if self.rt_traversal_replacement_allowed:
            raise ValueError("v2.5 partners must not replace RT traversal")
        if self.public_speedup_claim_authorized:
            raise ValueError("v2.5 support matrix must not authorize public speedup claims")
        if self.true_zero_copy_claim_authorized:
            raise ValueError("v2.5 support matrix must not authorize true zero-copy claims")
        if self.partner == V2_5_PRIMARY_PARTNER and self.status == V2_5_SUPPORT_STATUS_PREVIEW:
            if self.operation not in V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS:
                raise ValueError("Triton preview row requires a preview kernel operation")
        if self.partner == V2_5_FALLBACK_PARTNER and self.status == V2_5_SUPPORT_STATUS_PREVIEW:
            if self.operation not in V2_5_NUMBA_PREVIEW_OPERATIONS:
                raise ValueError("Numba preview row requires a Numba preview operation")
        if self.partner == V2_5_CONFORMANCE_PARTNER and self.status == V2_5_SUPPORT_STATUS_PREVIEW:
            if self.operation not in V2_5_CUPY_PREVIEW_OPERATIONS:
                raise ValueError("CuPy preview row requires a CuPy preview operation")
        if self.status == V2_5_SUPPORT_STATUS_UNSUPPORTED and not self.notes:
            raise ValueError("unsupported support cells require a fail-closed reason")

    @property
    def supported(self) -> bool:
        return self.status != V2_5_SUPPORT_STATUS_UNSUPPORTED

    def to_metadata(self) -> dict[str, Any]:
        return {
            "matrix_version": V2_5_PARTNER_SUPPORT_MATRIX_VERSION,
            "continuation_contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
            "neutral_buffer_seam_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "operation": self.operation,
            "partner": self.partner,
            "status": self.status,
            "supported": self.supported,
            "execution_backend": self.execution_backend,
            "requires_neutral_buffer_seam": bool(self.requires_neutral_buffer_seam),
            "requires_cuda": bool(self.requires_cuda),
            "requires_sm70_plus": bool(self.requires_sm70_plus),
            "same_contract_reference_required": bool(self.same_contract_reference_required),
            "promoted_performance_path": bool(self.promoted_performance_path),
            "rt_traversal_replacement_allowed": bool(self.rt_traversal_replacement_allowed),
            "public_speedup_claim_authorized": bool(self.public_speedup_claim_authorized),
            "true_zero_copy_claim_authorized": bool(self.true_zero_copy_claim_authorized),
            "notes": self.notes,
            "claim_boundary": V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY,
        }


def v2_5_partner_support_cells() -> tuple[V25PartnerSupportCell, ...]:
    cells: list[V25PartnerSupportCell] = []
    for operation in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        cells.append(
            V25PartnerSupportCell(
                operation=operation,
                partner=V2_5_REFERENCE_PARTNER,
                status=V2_5_SUPPORT_STATUS_REFERENCE,
                execution_backend="cpu_python_reference",
                requires_neutral_buffer_seam=False,
                notes="universal correctness reference",
            )
        )
        if operation in V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_PRIMARY_PARTNER,
                    status=V2_5_SUPPORT_STATUS_PREVIEW,
                    execution_backend="cuda_triton_preview_sm70_plus",
                    requires_neutral_buffer_seam=True,
                    requires_cuda=True,
                    requires_sm70_plus=True,
                    notes="preview kernel exists; benchmark promotion still requires pod evidence",
                )
            )
        else:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_PRIMARY_PARTNER,
                    status=V2_5_SUPPORT_STATUS_UNSUPPORTED,
                    execution_backend="none",
                    requires_neutral_buffer_seam=True,
                    notes="Triton preview kernel is not implemented for this operation",
                )
            )
        if operation in V2_5_NUMBA_PREVIEW_OPERATIONS:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_FALLBACK_PARTNER,
                    status=V2_5_SUPPORT_STATUS_PREVIEW,
                    execution_backend="cuda_numba_preview",
                    requires_neutral_buffer_seam=True,
                    requires_cuda=True,
                    notes="Numba fallback preview exists for count/sum only",
                )
            )
        else:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_FALLBACK_PARTNER,
                    status=V2_5_SUPPORT_STATUS_UNSUPPORTED,
                    execution_backend="none",
                    requires_neutral_buffer_seam=True,
                    notes="Numba fallback kernel is not implemented for this operation",
                )
            )
        if operation in V2_5_CUPY_PREVIEW_OPERATIONS:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_CONFORMANCE_PARTNER,
                    status=V2_5_SUPPORT_STATUS_PREVIEW,
                    execution_backend="cuda_cupy_rawkernel_preview_neutral_event_stream",
                    requires_neutral_buffer_seam=True,
                    requires_cuda=True,
                    notes=(
                        "CuPy preview exists for an explicitly listed RawKernel-backed "
                        "or event-ordered conformance operation; it remains unpromoted"
                    ),
                )
            )
        else:
            cells.append(
                V25PartnerSupportCell(
                    operation=operation,
                    partner=V2_5_CONFORMANCE_PARTNER,
                    status=V2_5_SUPPORT_STATUS_DESCRIPTOR,
                    execution_backend="cuda_cupy_conformance_descriptor",
                    requires_neutral_buffer_seam=True,
                    requires_cuda=True,
                    notes=(
                        "CuPy remains an app-chosen conformance/interoperability partner; "
                        "generic v2.5 kernels are not promoted here"
                    ),
                )
            )
    return tuple(cells)


def v2_5_partner_support_matrix() -> dict[str, Any]:
    cells = v2_5_partner_support_cells()
    return {
        "matrix_version": V2_5_PARTNER_SUPPORT_MATRIX_VERSION,
        "continuation_contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "neutral_buffer_seam_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "allowed_partners": V2_5_ALLOWED_PARTNERS,
        "operations": V2_5_PARTNER_CONTINUATION_OPERATION_NAMES,
        "statuses": V2_5_SUPPORT_STATUSES,
        "cell_count": len(cells),
        "cells": tuple(cell.to_metadata() for cell in cells),
        "triton_preview_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
        "numba_preview_operations": V2_5_NUMBA_PREVIEW_OPERATIONS,
        "cupy_preview_operations": V2_5_CUPY_PREVIEW_OPERATIONS,
        "partner_choice_policy": "explicit_per_boundary_app_choice",
        "no_partner_forced": True,
        "unsupported_cells_fail_closed": True,
        "rt_traversal_replacement_allowed": V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY,
    }


def plan_v2_5_partner_support(operation: str, partner: str) -> dict[str, Any]:
    normalized_operation = str(operation).strip()
    normalized_partner = _normalize_partner(partner)
    for cell in v2_5_partner_support_cells():
        if cell.operation == normalized_operation and cell.partner == normalized_partner:
            return cell.to_metadata()
    raise ValueError("unknown v2.5 partner support cell")


def validate_v2_5_partner_support_matrix(matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    matrix = v2_5_partner_support_matrix() if matrix is None else matrix
    errors: list[str] = []
    if matrix.get("matrix_version") != V2_5_PARTNER_SUPPORT_MATRIX_VERSION:
        errors.append("unexpected v2.5 support matrix version")
    if tuple(matrix.get("allowed_partners", ())) != V2_5_ALLOWED_PARTNERS:
        errors.append("allowed partner list changed")
    if tuple(matrix.get("operations", ())) != V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        errors.append("operation set changed")
    cells = tuple(matrix.get("cells", ()))
    expected_count = len(V2_5_ALLOWED_PARTNERS) * len(V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
    if int(matrix.get("cell_count", -1)) != expected_count or len(cells) != expected_count:
        errors.append("support matrix must contain every partner x operation cell")
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict):
            errors.append("support matrix cells must be metadata dictionaries")
            continue
        key = (cell.get("operation"), cell.get("partner"))
        if key in seen:
            errors.append(f"duplicate support cell: {key}")
        seen.add(key)
        if cell.get("promoted_performance_path") is not False:
            errors.append(f"{key} promotes a performance path")
        if cell.get("rt_traversal_replacement_allowed") is not False:
            errors.append(f"{key} allows RT traversal replacement")
        if cell.get("public_speedup_claim_authorized") is not False:
            errors.append(f"{key} authorizes a speedup claim")
        if cell.get("true_zero_copy_claim_authorized") is not False:
            errors.append(f"{key} authorizes a zero-copy claim")
    for operation in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        ref = _cell(cells, operation, V2_5_REFERENCE_PARTNER)
        if ref is None or ref.get("status") != V2_5_SUPPORT_STATUS_REFERENCE:
            errors.append(f"{operation} lacks a reference contract cell")
        triton = _cell(cells, operation, V2_5_PRIMARY_PARTNER)
        if operation in V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS:
            if triton is None or triton.get("status") != V2_5_SUPPORT_STATUS_PREVIEW:
                errors.append(f"{operation} lacks a Triton preview cell")
        elif triton is None or triton.get("status") != V2_5_SUPPORT_STATUS_UNSUPPORTED:
            errors.append(f"{operation} must fail closed for Triton")
        numba = _cell(cells, operation, V2_5_FALLBACK_PARTNER)
        if operation in V2_5_NUMBA_PREVIEW_OPERATIONS:
            if numba is None or numba.get("status") != V2_5_SUPPORT_STATUS_PREVIEW:
                errors.append(f"{operation} lacks expected Numba preview cell")
        elif numba is None or numba.get("status") != V2_5_SUPPORT_STATUS_UNSUPPORTED:
            errors.append(f"{operation} must fail closed for Numba")
        cupy = _cell(cells, operation, V2_5_CONFORMANCE_PARTNER)
        if operation in V2_5_CUPY_PREVIEW_OPERATIONS:
            if cupy is None or cupy.get("status") != V2_5_SUPPORT_STATUS_PREVIEW:
                errors.append(f"{operation} lacks expected CuPy preview cell")
        elif cupy is None or cupy.get("status") != V2_5_SUPPORT_STATUS_DESCRIPTOR:
            errors.append(f"{operation} must remain descriptor-only for CuPy")
    return {
        "status": "accept" if not errors else "reject",
        "matrix_version": matrix.get("matrix_version"),
        "cell_count": matrix.get("cell_count"),
        "errors": tuple(errors),
    }


def _cell(cells: tuple[Any, ...], operation: str, partner: str) -> dict[str, Any] | None:
    for cell in cells:
        if isinstance(cell, dict) and cell.get("operation") == operation and cell.get("partner") == partner:
            return cell
    return None


def _normalize_partner(partner: str) -> str:
    normalized = str(partner).strip().lower().replace("-", "_")
    aliases = {
        "python": V2_5_REFERENCE_PARTNER,
        "reference": V2_5_REFERENCE_PARTNER,
        "cupy": V2_5_CONFORMANCE_PARTNER,
        "cupy_conformance": V2_5_CONFORMANCE_PARTNER,
    }
    return aliases.get(normalized, normalized)
