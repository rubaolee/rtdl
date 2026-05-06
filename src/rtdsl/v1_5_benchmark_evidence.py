from __future__ import annotations

from typing import Any

from .app_support_matrix import EXCLUDE_FROM_RTX_APP_BENCHMARK
from .app_support_matrix import READY_FOR_RTX_CLAIM_REVIEW
from .app_support_matrix import optix_app_benchmark_readiness_matrix
from .app_support_matrix import public_apps
from .v1_5_standalone_app_classification import (
    validate_v1_5_standalone_app_classification_matrix,
)
from .v1_5_support_maturity import validate_v1_5_support_maturity_matrix


V1_5_BENCHMARK_EVIDENCE_STATUSES = (
    "covered_by_existing_same_contract_benchmark_evidence",
    "excluded_from_standalone_v1_5",
)


def _evidence_refs(next_goal: str) -> tuple[str, ...]:
    refs = []
    for part in next_goal.split("/"):
        stripped = part.strip()
        if stripped:
            refs.append(stripped)
    return tuple(refs)


def v1_5_benchmark_evidence_matrix() -> dict[str, dict[str, Any]]:
    """Return same-contract benchmark evidence status for v1.5 apps."""
    classification = validate_v1_5_standalone_app_classification_matrix()
    support = validate_v1_5_support_maturity_matrix()
    readiness = optix_app_benchmark_readiness_matrix()
    matrix: dict[str, dict[str, Any]] = {}
    for app in public_apps():
        class_row = classification[app]
        readiness_row = readiness[app]
        included = bool(class_row["standalone_included"])
        if included:
            benchmark_status = "covered_by_existing_same_contract_benchmark_evidence"
            release_gate_counts_as_passed = (
                readiness_row.status == READY_FOR_RTX_CLAIM_REVIEW
                and bool(readiness_row.next_goal)
                and bool(readiness_row.benchmark_contract)
                and support[app]["release_gate_counts_as_passed"]
            )
        else:
            benchmark_status = "excluded_from_standalone_v1_5"
            release_gate_counts_as_passed = True
        matrix[app] = {
            "app": app,
            "standalone_included": included,
            "classification": class_row["classification"],
            "generic_surface": class_row["generic_surface"],
            "benchmark_status": benchmark_status,
            "benchmark_readiness_status": readiness_row.status,
            "evidence_refs": _evidence_refs(readiness_row.next_goal),
            "benchmark_contract": readiness_row.benchmark_contract,
            "claim_boundary": readiness_row.blocker,
            "allowed_claim_boundary": readiness_row.allowed_claim,
            "release_gate_counts_as_passed": release_gate_counts_as_passed,
            "public_wording_authorized_by_this_gate": False,
        }
    return matrix


def v1_5_benchmark_evidence_summary() -> dict[str, Any]:
    matrix = validate_v1_5_benchmark_evidence_matrix()
    status_counts: dict[str, int] = {}
    included_apps = []
    excluded_apps = []
    failed_apps = []
    for app, row in matrix.items():
        status = str(row["benchmark_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["standalone_included"]:
            included_apps.append(app)
        else:
            excluded_apps.append(app)
        if not row["release_gate_counts_as_passed"]:
            failed_apps.append(app)
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "included_apps": tuple(sorted(included_apps)),
        "excluded_apps": tuple(sorted(excluded_apps)),
        "failed_apps": tuple(sorted(failed_apps)),
        "included_app_count": len(included_apps),
        "excluded_app_count": len(excluded_apps),
        "release_gate_complete": not failed_apps,
        "public_wording_authorized_by_this_gate": False,
    }


def validate_v1_5_benchmark_evidence_matrix() -> dict[str, dict[str, Any]]:
    matrix = v1_5_benchmark_evidence_matrix()
    expected_apps = set(public_apps())
    if set(matrix) != expected_apps:
        missing = sorted(expected_apps - set(matrix))
        extra = sorted(set(matrix) - expected_apps)
        raise ValueError(f"v1.5 benchmark evidence mismatch: missing={missing}, extra={extra}")
    for app, row in matrix.items():
        for field in (
            "app",
            "standalone_included",
            "classification",
            "generic_surface",
            "benchmark_status",
            "benchmark_readiness_status",
            "evidence_refs",
            "benchmark_contract",
            "claim_boundary",
            "allowed_claim_boundary",
            "release_gate_counts_as_passed",
            "public_wording_authorized_by_this_gate",
        ):
            if field not in row:
                raise ValueError(f"missing v1.5 benchmark evidence field: {app}.{field}")
        if row["app"] != app:
            raise ValueError(f"v1.5 benchmark evidence app key mismatch: {app}")
        if row["benchmark_status"] not in V1_5_BENCHMARK_EVIDENCE_STATUSES:
            raise ValueError(f"invalid v1.5 benchmark evidence status: {app}")
        if row["standalone_included"]:
            if row["benchmark_status"] != "covered_by_existing_same_contract_benchmark_evidence":
                raise ValueError(f"included app must have benchmark evidence: {app}")
            if row["benchmark_readiness_status"] != READY_FOR_RTX_CLAIM_REVIEW:
                raise ValueError(f"included app must be benchmark-ready: {app}")
            if not tuple(row["evidence_refs"]):
                raise ValueError(f"included app must list benchmark evidence refs: {app}")
            if not row["benchmark_contract"]:
                raise ValueError(f"included app must have benchmark contract: {app}")
        else:
            if row["benchmark_status"] != "excluded_from_standalone_v1_5":
                raise ValueError(f"excluded app must be benchmark-excluded: {app}")
            if row["benchmark_readiness_status"] == EXCLUDE_FROM_RTX_APP_BENCHMARK:
                pass
        if not isinstance(row["release_gate_counts_as_passed"], bool):
            raise ValueError(f"release pass marker must be boolean: {app}")
        if row["public_wording_authorized_by_this_gate"] is not False:
            raise ValueError(f"benchmark evidence must not authorize public wording: {app}")
    return matrix


def validate_v1_5_benchmark_evidence_summary() -> dict[str, Any]:
    summary = v1_5_benchmark_evidence_summary()
    if summary["included_app_count"] != 14:
        raise ValueError("v1.5 benchmark evidence must include 14 apps")
    if summary["excluded_app_count"] != 4:
        raise ValueError("v1.5 benchmark evidence must exclude 4 apps")
    if tuple(summary["failed_apps"]) != ():
        raise ValueError("v1.5 benchmark evidence must have no failed apps")
    if summary["release_gate_complete"] is not True:
        raise ValueError("v1.5 benchmark evidence gate must be complete")
    if summary["public_wording_authorized_by_this_gate"] is not False:
        raise ValueError("v1.5 benchmark evidence must not authorize public wording")
    return summary
