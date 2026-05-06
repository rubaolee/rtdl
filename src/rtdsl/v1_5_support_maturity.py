from __future__ import annotations

from typing import Any

from .app_support_matrix import app_engine_support_matrix
from .app_support_matrix import optix_app_benchmark_readiness_matrix
from .app_support_matrix import public_apps
from .app_support_matrix import rt_core_app_maturity_matrix
from .v1_5_standalone_app_classification import (
    validate_v1_5_standalone_app_classification_matrix,
)
from .v1_5_standalone_correctness import (
    validate_v1_5_standalone_correctness_matrix,
)


V1_5_SUPPORT_MATURITY_STATUSES = (
    "standalone_v1_5_supported",
    "excluded_from_standalone_v1_5",
)
V1_5_SUPPORT_MATURITY_REQUIRED_BACKENDS = ("embree", "optix")


def v1_5_support_maturity_matrix() -> dict[str, dict[str, Any]]:
    """Return the v1.5-specific support/maturity matrix.

    This is narrower than the public app support matrix. It records only the
    standalone-v1.5 release surface: included Embree+OptiX app contracts and
    explicit exclusions.
    """
    classification = validate_v1_5_standalone_app_classification_matrix()
    correctness = validate_v1_5_standalone_correctness_matrix()
    support = app_engine_support_matrix()
    maturity = rt_core_app_maturity_matrix()
    benchmark = optix_app_benchmark_readiness_matrix()
    matrix: dict[str, dict[str, Any]] = {}
    for app in public_apps():
        class_row = classification[app]
        correctness_row = correctness[app]
        included = bool(class_row["standalone_included"])
        app_support = support[app]
        row = {
            "app": app,
            "standalone_included": included,
            "classification": class_row["classification"],
            "generic_surface": class_row["generic_surface"],
            "release_boundary": class_row["release_boundary"],
            "support_status": (
                "standalone_v1_5_supported"
                if included
                else "excluded_from_standalone_v1_5"
            ),
            "required_backends": V1_5_SUPPORT_MATURITY_REQUIRED_BACKENDS if included else (),
            "embree_support_status": app_support["embree"].status,
            "optix_support_status": app_support["optix"].status,
            "rt_core_maturity_status": maturity[app].current_status,
            "benchmark_readiness_status": benchmark[app].status,
            "correctness_status": correctness_row["correctness_status"],
            "test_backed_by": (
                "validate_v1_5_standalone_app_classification_matrix",
                "validate_v1_5_standalone_correctness_matrix",
                "app_engine_support_matrix",
                "rt_core_app_maturity_matrix",
                "optix_app_benchmark_readiness_matrix",
            ),
            "release_gate_counts_as_passed": included
            and correctness_row["release_gate_counts_as_passed"]
            and app_support["embree"].status != "not_exposed_by_app_cli"
            and app_support["optix"].status != "not_exposed_by_app_cli",
        }
        if not included:
            row["release_gate_counts_as_passed"] = True
        matrix[app] = row
    return matrix


def v1_5_support_maturity_summary() -> dict[str, Any]:
    matrix = validate_v1_5_support_maturity_matrix()
    status_counts: dict[str, int] = {}
    included_apps = []
    excluded_apps = []
    failed_apps = []
    for app, row in matrix.items():
        status = str(row["support_status"])
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
        "test_backed": True,
    }


def validate_v1_5_support_maturity_matrix() -> dict[str, dict[str, Any]]:
    matrix = v1_5_support_maturity_matrix()
    expected_apps = set(public_apps())
    if set(matrix) != expected_apps:
        missing = sorted(expected_apps - set(matrix))
        extra = sorted(set(matrix) - expected_apps)
        raise ValueError(f"v1.5 support/maturity mismatch: missing={missing}, extra={extra}")
    for app, row in matrix.items():
        for field in (
            "app",
            "standalone_included",
            "classification",
            "generic_surface",
            "release_boundary",
            "support_status",
            "required_backends",
            "embree_support_status",
            "optix_support_status",
            "rt_core_maturity_status",
            "benchmark_readiness_status",
            "correctness_status",
            "test_backed_by",
            "release_gate_counts_as_passed",
        ):
            if field not in row:
                raise ValueError(f"missing v1.5 support/maturity field: {app}.{field}")
        if row["app"] != app:
            raise ValueError(f"v1.5 support/maturity app key mismatch: {app}")
        if row["support_status"] not in V1_5_SUPPORT_MATURITY_STATUSES:
            raise ValueError(f"invalid v1.5 support/maturity status: {app}")
        if row["standalone_included"]:
            if row["support_status"] != "standalone_v1_5_supported":
                raise ValueError(f"included app must be v1.5-supported: {app}")
            if tuple(row["required_backends"]) != V1_5_SUPPORT_MATURITY_REQUIRED_BACKENDS:
                raise ValueError(f"included app must require Embree and OptiX: {app}")
            if row["correctness_status"] != "covered_by_existing_local_tests":
                raise ValueError(f"included app must have correctness coverage: {app}")
            for backend_field in ("embree_support_status", "optix_support_status"):
                if row[backend_field] == "not_exposed_by_app_cli":
                    raise ValueError(f"included app lacks backend exposure: {app}.{backend_field}")
        else:
            if row["support_status"] != "excluded_from_standalone_v1_5":
                raise ValueError(f"excluded app must be marked excluded: {app}")
            if tuple(row["required_backends"]) != ():
                raise ValueError(f"excluded app must not require active backends: {app}")
        if not tuple(row["test_backed_by"]):
            raise ValueError(f"v1.5 support/maturity row must list validators: {app}")
        if not isinstance(row["release_gate_counts_as_passed"], bool):
            raise ValueError(f"release pass marker must be boolean: {app}")
    return matrix


def validate_v1_5_support_maturity_summary() -> dict[str, Any]:
    summary = v1_5_support_maturity_summary()
    if summary["included_app_count"] != 14:
        raise ValueError("v1.5 support/maturity must include 14 apps")
    if summary["excluded_app_count"] != 4:
        raise ValueError("v1.5 support/maturity must exclude 4 apps")
    if summary["failed_apps"] != ():
        raise ValueError("v1.5 support/maturity must have no failed rows")
    if summary["release_gate_complete"] is not True:
        raise ValueError("v1.5 support/maturity gate must be complete")
    if summary["test_backed"] is not True:
        raise ValueError("v1.5 support/maturity summary must be test-backed")
    return summary
