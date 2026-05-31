from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .partner_continuation_protocol import V2_5_ALLOWED_PARTNERS
from .partner_continuation_protocol import V2_5_CONFORMANCE_PARTNER
from .partner_continuation_protocol import V2_5_FALLBACK_PARTNER
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER
from .partner_continuation_protocol import V2_5_REFERENCE_PARTNER
from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_DESCRIPTOR
from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_PREVIEW
from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_REFERENCE
from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_UNSUPPORTED
from .v2_5_partner_support_matrix import plan_v2_5_partner_support


V2_5_PARTNER_CONFORMANCE_MATRIX_VERSION = "rtdl.v2_5.partner_conformance_matrix.v1"
V2_5_CONFORMANCE_STATUS_REFERENCE = "reference_contract_unit_tested"
V2_5_CONFORMANCE_STATUS_POD_RUNTIME = "pod_cuda_runtime_smoke_recorded"
V2_5_CONFORMANCE_STATUS_CUDA_SMOKE_PRESENT = "cuda_runtime_smoke_present_not_current_pod_indexed"
V2_5_CONFORMANCE_STATUS_DESCRIPTOR = "descriptor_only_no_generic_kernel"
V2_5_CONFORMANCE_STATUS_UNSUPPORTED = "unsupported_fail_closed"
V2_5_CONFORMANCE_STATUS_RUNTIME_GAP = "preview_runtime_conformance_gap"
V2_5_CONFORMANCE_STATUSES = (
    V2_5_CONFORMANCE_STATUS_REFERENCE,
    V2_5_CONFORMANCE_STATUS_POD_RUNTIME,
    V2_5_CONFORMANCE_STATUS_CUDA_SMOKE_PRESENT,
    V2_5_CONFORMANCE_STATUS_DESCRIPTOR,
    V2_5_CONFORMANCE_STATUS_UNSUPPORTED,
    V2_5_CONFORMANCE_STATUS_RUNTIME_GAP,
)
V2_5_PARTNER_CONFORMANCE_CLAIM_BOUNDARY = (
    "v2.5 partner conformance rows index evidence only. They do not authorize "
    "release, public speedup claims, broad RT-core claims, whole-app claims, "
    "true zero-copy claims, or Triton preview auto-selection."
)

_REFERENCE_EVIDENCE = (
    "tests.goal2662_v2_5_partner_continuation_contract_test",
    "tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test",
)
_TRITON_POD_RUNTIME_EVIDENCE: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "segmented_count_i64": (
        "Goal2874",
        ("tests.goal2663_v2_5_triton_segmented_sum_test",),
        (
            "docs/reports/goal2663_v2_5_triton_segmented_sum_preview_2026-05-27.md",
            "docs/reports/goal2664_v2_5_triton_segmented_count_preview_2026-05-27.md",
            "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
        ),
    ),
    "segmented_sum_f64": (
        "Goal2872",
        ("tests.goal2872_triton_tie_break_conformance_smoke_test",),
        ("docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",),
    ),
    "grouped_vector_sum_f64x2": (
        "Goal2872",
        ("tests.goal2872_triton_tie_break_conformance_smoke_test",),
        ("docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",),
    ),
    "grouped_argmin_f64": (
        "Goal2872",
        ("tests.goal2872_triton_tie_break_conformance_smoke_test",),
        ("docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",),
    ),
    "grouped_argmax_f64": (
        "Goal2872",
        ("tests.goal2872_triton_tie_break_conformance_smoke_test",),
        ("docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",),
    ),
    "grouped_topk_f64": (
        "Goal2872",
        ("tests.goal2872_triton_tie_break_conformance_smoke_test",),
        ("docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",),
    ),
    "segmented_min_f64": (
        "Goal2874",
        ("tests.goal2677_v2_5_triton_segmented_minmax_preview_test",),
        (
            "docs/reports/goal2677_v2_5_triton_segmented_minmax_preview_2026-05-27.md",
            "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
        ),
    ),
    "segmented_max_f64": (
        "Goal2874",
        ("tests.goal2677_v2_5_triton_segmented_minmax_preview_test",),
        (
            "docs/reports/goal2677_v2_5_triton_segmented_minmax_preview_2026-05-27.md",
            "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
        ),
    ),
    "compact_mask_i64": (
        "Goal2874",
        ("tests.goal2678_v2_5_triton_compact_mask_preview_test",),
        (
            "docs/reports/goal2678_v2_5_triton_compact_mask_preview_2026-05-27.md",
            "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
        ),
    ),
    "edge_list_components_i64": (
        "Goal2779",
        ("tests.goal2779_v2_5_triton_edge_list_components_preview_test",),
        (
            "docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md",
            "docs/reports/goal2779_v2_5_edge_list_components_consensus_2026-05-31.md",
        ),
    ),
    "bounded_collect_finalize_i64": (
        "Goal2874",
        ("tests.goal2680_v2_5_triton_bounded_collect_preview_test",),
        (
            "docs/reports/goal2680_v2_5_triton_bounded_collect_preview_2026-05-27.md",
            "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
        ),
    ),
}
_TRITON_CUDA_SMOKE_PRESENT_EVIDENCE: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {}
_CUPY_POD_RUNTIME_EVIDENCE = {
    "hit_stream_grouped_ray_id_primitive_i64": (
        "Goal2771/Goal2772",
        (
            "tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test",
            "tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test",
        ),
        (
            "docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_2026-05-31.md",
            "docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md",
        ),
    )
}


@dataclass(frozen=True)
class V25PartnerConformanceCell:
    operation: str
    partner: str
    support_status: str
    conformance_status: str
    evidence_goal: str
    test_modules: tuple[str, ...]
    report_paths: tuple[str, ...]
    release_blocker: bool
    notes: str
    public_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    triton_preview_auto_selection_authorized: bool = False

    def __post_init__(self) -> None:
        if self.operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            raise ValueError("conformance cell operation is not a v2.5 continuation operation")
        if self.partner not in V2_5_ALLOWED_PARTNERS:
            raise ValueError("conformance cell partner is not allowed")
        if self.conformance_status not in V2_5_CONFORMANCE_STATUSES:
            raise ValueError("unsupported v2.5 conformance status")
        for flag_name in (
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "triton_preview_auto_selection_authorized",
        ):
            if getattr(self, flag_name):
                raise ValueError(f"conformance matrix must not authorize {flag_name}")
        if self.conformance_status == V2_5_CONFORMANCE_STATUS_RUNTIME_GAP and not self.release_blocker:
            raise ValueError("runtime conformance gaps must block release")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "matrix_version": V2_5_PARTNER_CONFORMANCE_MATRIX_VERSION,
            "operation": self.operation,
            "partner": self.partner,
            "support_status": self.support_status,
            "conformance_status": self.conformance_status,
            "evidence_goal": self.evidence_goal,
            "test_modules": self.test_modules,
            "report_paths": self.report_paths,
            "release_blocker": bool(self.release_blocker),
            "notes": self.notes,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "triton_preview_auto_selection_authorized": self.triton_preview_auto_selection_authorized,
            "claim_boundary": V2_5_PARTNER_CONFORMANCE_CLAIM_BOUNDARY,
        }


def v2_5_partner_conformance_cells() -> tuple[V25PartnerConformanceCell, ...]:
    rows: list[V25PartnerConformanceCell] = []
    for operation in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        for partner in V2_5_ALLOWED_PARTNERS:
            rows.append(_conformance_cell(operation, partner))
    return tuple(rows)


def v2_5_partner_conformance_matrix() -> dict[str, Any]:
    cells = tuple(cell.to_metadata() for cell in v2_5_partner_conformance_cells())
    release_blockers = tuple(
        cell
        for cell in cells
        if cell["release_blocker"] is True
        or cell["conformance_status"] == V2_5_CONFORMANCE_STATUS_RUNTIME_GAP
    )
    return {
        "matrix_version": V2_5_PARTNER_CONFORMANCE_MATRIX_VERSION,
        "allowed_partners": V2_5_ALLOWED_PARTNERS,
        "operations": V2_5_PARTNER_CONTINUATION_OPERATION_NAMES,
        "statuses": V2_5_CONFORMANCE_STATUSES,
        "cell_count": len(cells),
        "cells": cells,
        "release_conformance_complete": False,
        "runtime_conformance_gap_count": sum(
            1
            for cell in cells
            if cell["conformance_status"] == V2_5_CONFORMANCE_STATUS_RUNTIME_GAP
        ),
        "release_blocker_count": len(release_blockers),
        "release_blockers": release_blockers,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "triton_preview_auto_selection_authorized": False,
        "claim_boundary": V2_5_PARTNER_CONFORMANCE_CLAIM_BOUNDARY,
    }


def plan_v2_5_partner_conformance(operation: str, partner: str) -> dict[str, Any]:
    normalized_operation = str(operation).strip()
    normalized_partner = _normalize_partner(partner)
    for cell in v2_5_partner_conformance_cells():
        if cell.operation == normalized_operation and cell.partner == normalized_partner:
            return cell.to_metadata()
    raise ValueError("unknown v2.5 partner conformance cell")


def validate_v2_5_partner_conformance_matrix(matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    matrix = v2_5_partner_conformance_matrix() if matrix is None else matrix
    errors: list[str] = []
    cells = tuple(matrix.get("cells", ()))
    expected_count = len(V2_5_ALLOWED_PARTNERS) * len(V2_5_PARTNER_CONTINUATION_OPERATION_NAMES)
    if matrix.get("matrix_version") != V2_5_PARTNER_CONFORMANCE_MATRIX_VERSION:
        errors.append("unexpected v2.5 partner conformance matrix version")
    if tuple(matrix.get("allowed_partners", ())) != V2_5_ALLOWED_PARTNERS:
        errors.append("allowed partner list changed")
    if tuple(matrix.get("operations", ())) != V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        errors.append("operation set changed")
    if int(matrix.get("cell_count", -1)) != expected_count or len(cells) != expected_count:
        errors.append("conformance matrix must contain every partner x operation cell")
    seen = set()
    for cell in cells:
        if not isinstance(cell, dict):
            errors.append("conformance matrix cells must be metadata dictionaries")
            continue
        key = (cell.get("operation"), cell.get("partner"))
        if key in seen:
            errors.append(f"duplicate conformance cell: {key}")
        seen.add(key)
        support = plan_v2_5_partner_support(str(cell.get("operation")), str(cell.get("partner")))
        if cell.get("support_status") != support["status"]:
            errors.append(f"{key} conformance/support status mismatch")
        conformance_status = cell.get("conformance_status")
        if support["status"] == V2_5_SUPPORT_STATUS_UNSUPPORTED:
            if conformance_status != V2_5_CONFORMANCE_STATUS_UNSUPPORTED:
                errors.append(f"{key} unsupported support cell must fail closed in conformance")
        if support["status"] == V2_5_SUPPORT_STATUS_DESCRIPTOR:
            if conformance_status != V2_5_CONFORMANCE_STATUS_DESCRIPTOR:
                errors.append(f"{key} descriptor support cell must stay descriptor-only")
        if support["status"] == V2_5_SUPPORT_STATUS_REFERENCE:
            if conformance_status != V2_5_CONFORMANCE_STATUS_REFERENCE:
                errors.append(f"{key} reference support cell must use reference conformance")
        if conformance_status == V2_5_CONFORMANCE_STATUS_RUNTIME_GAP and cell.get("release_blocker") is not True:
            errors.append(f"{key} runtime gap must be a release blocker")
        for claim_field in (
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "triton_preview_auto_selection_authorized",
        ):
            if cell.get(claim_field) is not False:
                errors.append(f"{key} must not authorize {claim_field}")
    for operation in ("grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"):
        triton = _cell(cells, operation, V2_5_PRIMARY_PARTNER)
        if not triton or triton.get("conformance_status") != V2_5_CONFORMANCE_STATUS_POD_RUNTIME:
            errors.append(f"{operation} must keep Triton pod tie-break conformance evidence")
        elif "tests.goal2872_triton_tie_break_conformance_smoke_test" not in triton.get("test_modules", ()):
            errors.append(f"{operation} must point at Goal2872 tie-break smoke")
    for operation in ("segmented_count_i64", "segmented_sum_f64"):
        numba = _cell(cells, operation, V2_5_FALLBACK_PARTNER)
        if not numba or numba.get("conformance_status") != V2_5_CONFORMANCE_STATUS_RUNTIME_GAP:
            errors.append(f"{operation} Numba preview must remain an explicit runtime conformance gap")
    cupy_hit = _cell(cells, "hit_stream_grouped_ray_id_primitive_i64", V2_5_CONFORMANCE_PARTNER)
    if not cupy_hit or cupy_hit.get("conformance_status") != V2_5_CONFORMANCE_STATUS_POD_RUNTIME:
        errors.append("CuPy hit-stream grouped reduction must keep pod runtime conformance evidence")
    if matrix.get("release_conformance_complete") is not False:
        errors.append("v2.5 conformance matrix must not mark release conformance complete")
    if int(matrix.get("runtime_conformance_gap_count", -1)) <= 0:
        errors.append("runtime conformance gaps must remain explicit until fully closed")
    for claim_field in (
        "public_speedup_claim_authorized",
        "broad_rt_core_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "triton_preview_auto_selection_authorized",
    ):
        if matrix.get(claim_field) is not False:
            errors.append(f"top-level conformance matrix must not authorize {claim_field}")
    return {
        "status": "accept" if not errors else "reject",
        "matrix_version": matrix.get("matrix_version"),
        "cell_count": matrix.get("cell_count"),
        "runtime_conformance_gap_count": matrix.get("runtime_conformance_gap_count"),
        "release_blocker_count": matrix.get("release_blocker_count"),
        "errors": tuple(errors),
    }


def _conformance_cell(operation: str, partner: str) -> V25PartnerConformanceCell:
    support = plan_v2_5_partner_support(operation, partner)
    support_status = str(support["status"])
    if partner == V2_5_REFERENCE_PARTNER:
        return V25PartnerConformanceCell(
            operation=operation,
            partner=partner,
            support_status=support_status,
            conformance_status=V2_5_CONFORMANCE_STATUS_REFERENCE,
            evidence_goal="Goal2662/Goal2774",
            test_modules=_REFERENCE_EVIDENCE,
            report_paths=(
                "docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md",
            ),
            release_blocker=False,
            notes="same-contract Python reference is the baseline for every operation",
        )
    if support_status == V2_5_SUPPORT_STATUS_UNSUPPORTED:
        return V25PartnerConformanceCell(
            operation=operation,
            partner=partner,
            support_status=support_status,
            conformance_status=V2_5_CONFORMANCE_STATUS_UNSUPPORTED,
            evidence_goal="support-matrix",
            test_modules=("tests.goal2696_v2_5_partner_support_matrix_test",),
            report_paths=("docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md",),
            release_blocker=False,
            notes="unsupported cells fail closed and must not be invoked as executable partners",
        )
    if support_status == V2_5_SUPPORT_STATUS_DESCRIPTOR:
        return V25PartnerConformanceCell(
            operation=operation,
            partner=partner,
            support_status=support_status,
            conformance_status=V2_5_CONFORMANCE_STATUS_DESCRIPTOR,
            evidence_goal="support-matrix",
            test_modules=("tests.goal2696_v2_5_partner_support_matrix_test",),
            report_paths=("docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md",),
            release_blocker=False,
            notes="descriptor-only interop row; no generic executable kernel is claimed",
        )
    if support_status != V2_5_SUPPORT_STATUS_PREVIEW:
        raise ValueError(f"unexpected support status for conformance cell: {support_status}")
    if partner == V2_5_PRIMARY_PARTNER:
        if operation in _TRITON_POD_RUNTIME_EVIDENCE:
            goal, tests, reports = _TRITON_POD_RUNTIME_EVIDENCE[operation]
            return V25PartnerConformanceCell(
                operation=operation,
                partner=partner,
                support_status=support_status,
                conformance_status=V2_5_CONFORMANCE_STATUS_POD_RUNTIME,
                evidence_goal=goal,
                test_modules=tests,
                report_paths=reports,
                release_blocker=False,
                notes="Triton preview has CUDA runtime conformance evidence recorded in the source tree",
            )
        if operation in _TRITON_CUDA_SMOKE_PRESENT_EVIDENCE:
            goal, tests, reports = _TRITON_CUDA_SMOKE_PRESENT_EVIDENCE[operation]
            return V25PartnerConformanceCell(
                operation=operation,
                partner=partner,
                support_status=support_status,
                conformance_status=V2_5_CONFORMANCE_STATUS_CUDA_SMOKE_PRESENT,
                evidence_goal=goal,
                test_modules=tests,
                report_paths=reports,
                release_blocker=True,
                notes=(
                    "CUDA-gated smoke exists, but this row still needs a current "
                    "pod-indexed conformance record before release"
                ),
            )
    if partner == V2_5_FALLBACK_PARTNER:
        return V25PartnerConformanceCell(
            operation=operation,
            partner=partner,
            support_status=support_status,
            conformance_status=V2_5_CONFORMANCE_STATUS_RUNTIME_GAP,
            evidence_goal="Goal2666",
            test_modules=("tests.goal2666_v2_5_numba_segmented_preview_test",),
            report_paths=("docs/reports/goal2666_v2_5_numba_segmented_preview_2026-05-27.md",),
            release_blocker=True,
            notes="Numba preview descriptors exist; CUDA runtime conformance remains to be recorded",
        )
    if partner == V2_5_CONFORMANCE_PARTNER and operation in _CUPY_POD_RUNTIME_EVIDENCE:
        goal, tests, reports = _CUPY_POD_RUNTIME_EVIDENCE[operation]
        return V25PartnerConformanceCell(
            operation=operation,
            partner=partner,
            support_status=support_status,
            conformance_status=V2_5_CONFORMANCE_STATUS_POD_RUNTIME,
            evidence_goal=goal,
            test_modules=tests,
            report_paths=reports,
            release_blocker=False,
            notes="CuPy RawKernel consumer is scoped to the event-ordered hit-stream preview",
        )
    raise ValueError(f"preview conformance row is not classified: {partner}/{operation}")


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
