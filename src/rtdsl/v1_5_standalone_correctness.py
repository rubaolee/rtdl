from __future__ import annotations

from pathlib import Path
from typing import Any

from .app_support_matrix import public_apps
from .v1_5_standalone_app_classification import (
    validate_v1_5_standalone_app_classification_matrix,
)


V1_5_STANDALONE_CORRECTNESS_STATUSES = (
    "covered_by_existing_local_tests",
    "defined_pending_execution",
    "excluded_from_standalone_v1_5",
)
V1_5_STANDALONE_CORRECTNESS_REQUIRED_BACKENDS = ("embree", "optix")
V1_5_STANDALONE_CORRECTNESS_COMMAND = (
    "PYTHONPATH=src:. python3 -m unittest "
    "tests.goal1289_v1_5_graph_visibility_generic_dispatch_test "
    "tests.goal1297_v1_5_graph_visibility_reusable_scene_batches_test "
    "tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test "
    "tests.goal1300_v1_5_ann_facility_generic_migration_test "
    "tests.goal1301_v1_5_outlier_dbscan_generic_migration_test "
    "tests.goal1306_v1_5_robot_pose_flags_generic_migration_test "
    "tests.goal1307_v1_5_db_compact_summary_generic_migration_test "
    "tests.goal1309_v1_5_polygon_pair_generic_area_summary_test "
    "tests.goal1402_v1_5_pending_app_correctness_closure_test"
)
V1_5_STANDALONE_CORRECTNESS_PENDING_APPS: tuple[str, ...] = ()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _covered(
    *,
    surface: str,
    test_modules: tuple[str, ...],
    boundary: str,
) -> dict[str, Any]:
    return {
        "correctness_status": "covered_by_existing_local_tests",
        "same_contract_surface": surface,
        "required_backends": V1_5_STANDALONE_CORRECTNESS_REQUIRED_BACKENDS,
        "evidence_kind": "local_unittest_same_contract_or_generic_wrapper",
        "test_modules": test_modules,
        "command": V1_5_STANDALONE_CORRECTNESS_COMMAND,
        "release_gate_counts_as_passed": True,
        "boundary": boundary,
    }


def _pending(*, surface: str, required_evidence: str, boundary: str) -> dict[str, Any]:
    return {
        "correctness_status": "defined_pending_execution",
        "same_contract_surface": surface,
        "required_backends": V1_5_STANDALONE_CORRECTNESS_REQUIRED_BACKENDS,
        "evidence_kind": "pending_same_contract_embree_optix_execution",
        "test_modules": (),
        "command": (
            "PYTHONPATH=src:. python3 -m unittest "
            "<app-specific Embree/OptiX same-contract correctness test>"
        ),
        "release_gate_counts_as_passed": False,
        "required_evidence": required_evidence,
        "boundary": boundary,
    }


def _excluded(*, surface: str, boundary: str) -> dict[str, Any]:
    return {
        "correctness_status": "excluded_from_standalone_v1_5",
        "same_contract_surface": surface,
        "required_backends": (),
        "evidence_kind": "excluded_scope",
        "test_modules": (),
        "command": "",
        "release_gate_counts_as_passed": False,
        "boundary": boundary,
    }


def v1_5_standalone_correctness_matrix() -> dict[str, dict[str, Any]]:
    """Return per-app correctness evidence status for standalone v1.5.

    This matrix records evidence readiness, not release approval. Apps without
    exact Embree/OptiX same-contract evidence remain pending so the release gate
    cannot be accidentally satisfied by nearby tests.
    """
    classification = validate_v1_5_standalone_app_classification_matrix()
    rows: dict[str, dict[str, Any]] = {
        "database_analytics": _covered(
            surface="DB_COMPACT_SUMMARY + REDUCE_INT(COUNT|SUM)",
            test_modules=("tests.goal1307_v1_5_db_compact_summary_generic_migration_test",),
            boundary="compact DB summary wrapper only; SQL/DBMS behavior remains outside",
        ),
        "graph_analytics": _covered(
            surface="ANY_HIT + COUNT_HITS graph visibility dispatch",
            test_modules=(
                "tests.goal1289_v1_5_graph_visibility_generic_dispatch_test",
                "tests.goal1297_v1_5_graph_visibility_reusable_scene_batches_test",
            ),
            boundary="graph visibility any-hit/count only; graph-system analytics remain outside",
        ),
        "service_coverage_gaps": _covered(
            surface="FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            test_modules=("tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test",),
            boundary="fixed-radius gap summary only; no whole service optimization claim",
        ),
        "event_hotspot_screening": _covered(
            surface="FIXED_RADIUS_COUNT_THRESHOLD_2D + REDUCE_INT(COUNT)",
            test_modules=("tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test",),
            boundary="fixed-radius hotspot summary only; no whole hotspot analytics claim",
        ),
        "facility_knn_assignment": _covered(
            surface="coverage threshold prepared fixed-radius count",
            test_modules=("tests.goal1300_v1_5_ann_facility_generic_migration_test",),
            boundary="coverage-threshold decision only; ranked KNN remains outside",
        ),
        "ann_candidate_search": _covered(
            surface="candidate threshold prepared fixed-radius count",
            test_modules=("tests.goal1300_v1_5_ann_facility_generic_migration_test",),
            boundary="candidate coverage decision only; ANN indexing/ranking remains outside",
        ),
        "outlier_detection": _covered(
            surface="density fixed-radius count summary",
            test_modules=("tests.goal1301_v1_5_outlier_dbscan_generic_migration_test",),
            boundary="density count summary only; row labels remain outside",
        ),
        "dbscan_clustering": _covered(
            surface="core-point fixed-radius count summary",
            test_modules=("tests.goal1301_v1_5_outlier_dbscan_generic_migration_test",),
            boundary="core-count summary only; cluster expansion remains outside",
        ),
        "robot_collision_screening": _covered(
            surface="pose-flag any-hit/count prepared summary",
            test_modules=("tests.goal1306_v1_5_robot_pose_flags_generic_migration_test",),
            boundary="prepared pose-flag summaries only; full robot planning remains outside",
        ),
        "polygon_pair_overlap_area_rows": _covered(
            surface="POLYGON_PAIR_EXACT_AREA_SUMMARY + REDUCE_FLOAT(SUM)",
            test_modules=("tests.goal1309_v1_5_polygon_pair_generic_area_summary_test",),
            boundary="candidate discovery plus exact-area summary only; broad overlay remains outside",
        ),
        "road_hazard_screening": _covered(
            surface="segment/polygon compact count summary wrapper",
            test_modules=("tests.goal1402_v1_5_pending_app_correctness_closure_test",),
            boundary="compact hazard summary only; full GIS/routing remains outside",
        ),
        "segment_polygon_hitcount": _covered(
            surface="segment/polygon hit-count summary wrapper",
            test_modules=("tests.goal1402_v1_5_pending_app_correctness_closure_test",),
            boundary="compact hit-count summary only; pair-row output remains outside",
        ),
        "hausdorff_distance": _covered(
            surface="threshold decision fixed-radius count summary",
            test_modules=("tests.goal1402_v1_5_pending_app_correctness_closure_test",),
            boundary="threshold decision only; exact Hausdorff rows remain outside",
        ),
        "barnes_hut_force_app": _covered(
            surface="node-coverage fixed-radius count summary",
            test_modules=("tests.goal1402_v1_5_pending_app_correctness_closure_test",),
            boundary="node-coverage decision only; force-vector reduction remains outside",
        ),
        "segment_polygon_anyhit_rows": _excluded(
            surface="COLLECT_K_BOUNDED candidate rows",
            boundary="row-returning app excluded unless COLLECT_K_BOUNDED promotion gates pass",
        ),
        "polygon_set_jaccard": _excluded(
            surface="COLLECT_K_BOUNDED + REDUCE_FLOAT(SUM)",
            boundary="excluded unless COLLECT_K_BOUNDED promotion gates pass",
        ),
        "apple_rt_demo": _excluded(
            surface="none",
            boundary="Apple RT is frozen before v2.1 and outside standalone v1.5 scope",
        ),
        "hiprt_ray_triangle_hitcount": _excluded(
            surface="none",
            boundary="HIPRT is frozen before v2.1 and outside standalone v1.5 scope",
        ),
    }
    for app, row in rows.items():
        row["app"] = app
        row["standalone_included"] = bool(classification[app]["standalone_included"])
        row["classification"] = classification[app]["classification"]
        row["classification_surface"] = classification[app]["generic_surface"]
    return rows


def v1_5_standalone_correctness_summary() -> dict[str, Any]:
    matrix = validate_v1_5_standalone_correctness_matrix()
    status_counts: dict[str, int] = {}
    pending_apps = []
    covered_apps = []
    excluded_apps = []
    for app, row in matrix.items():
        status = str(row["correctness_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
        if row["standalone_included"] and row["release_gate_counts_as_passed"]:
            covered_apps.append(app)
        elif row["standalone_included"]:
            pending_apps.append(app)
        else:
            excluded_apps.append(app)
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "covered_apps": tuple(sorted(covered_apps)),
        "pending_apps": tuple(sorted(pending_apps)),
        "excluded_apps": tuple(sorted(excluded_apps)),
        "covered_app_count": len(covered_apps),
        "pending_app_count": len(pending_apps),
        "excluded_app_count": len(excluded_apps),
        "included_app_count": len(covered_apps) + len(pending_apps),
        "release_gate_complete": not pending_apps,
        "command": V1_5_STANDALONE_CORRECTNESS_COMMAND,
    }


def validate_v1_5_standalone_correctness_matrix() -> dict[str, dict[str, Any]]:
    matrix = v1_5_standalone_correctness_matrix()
    classification = validate_v1_5_standalone_app_classification_matrix()
    expected_apps = set(public_apps())
    if set(matrix) != expected_apps:
        missing = sorted(expected_apps - set(matrix))
        extra = sorted(set(matrix) - expected_apps)
        raise ValueError(f"v1.5 standalone correctness mismatch: missing={missing}, extra={extra}")
    repo_root = _repo_root()
    for app, row in matrix.items():
        for field in (
            "app",
            "standalone_included",
            "classification",
            "correctness_status",
            "same_contract_surface",
            "required_backends",
            "evidence_kind",
            "test_modules",
            "command",
            "release_gate_counts_as_passed",
            "boundary",
        ):
            if field not in row:
                raise ValueError(f"missing v1.5 standalone correctness field: {app}.{field}")
        if row["app"] != app:
            raise ValueError(f"v1.5 standalone correctness app key mismatch: {app}")
        if row["correctness_status"] not in V1_5_STANDALONE_CORRECTNESS_STATUSES:
            raise ValueError(f"invalid v1.5 standalone correctness status: {app}")
        if row["standalone_included"] != classification[app]["standalone_included"]:
            raise ValueError(f"standalone correctness inclusion mismatch: {app}")
        if row["classification"] != classification[app]["classification"]:
            raise ValueError(f"standalone correctness classification mismatch: {app}")
        if not row["same_contract_surface"]:
            raise ValueError(f"same-contract surface must be non-empty: {app}")
        if not isinstance(row["release_gate_counts_as_passed"], bool):
            raise ValueError(f"release gate pass marker must be boolean: {app}")
        status = row["correctness_status"]
        if row["standalone_included"]:
            if tuple(row["required_backends"]) != V1_5_STANDALONE_CORRECTNESS_REQUIRED_BACKENDS:
                raise ValueError(f"included app must require Embree and OptiX correctness: {app}")
            if not row["command"]:
                raise ValueError(f"included app must have a correctness command: {app}")
            if status == "excluded_from_standalone_v1_5":
                raise ValueError(f"included app cannot be correctness-excluded: {app}")
        else:
            if status != "excluded_from_standalone_v1_5":
                raise ValueError(f"excluded app must be marked correctness-excluded: {app}")
            if row["required_backends"]:
                raise ValueError(f"excluded app must not require active backends: {app}")
        if status == "covered_by_existing_local_tests":
            if row["release_gate_counts_as_passed"] is not True:
                raise ValueError(f"covered app must count as correctness-passed: {app}")
            if not tuple(row["test_modules"]):
                raise ValueError(f"covered app must list test modules: {app}")
            for module in row["test_modules"]:
                rel_path = Path(*str(module).split(".")).with_suffix(".py")
                if not (repo_root / rel_path).exists():
                    raise ValueError(f"covered app references missing test module: {app}.{module}")
        if status == "defined_pending_execution":
            if row["release_gate_counts_as_passed"] is not False:
                raise ValueError(f"pending app must not count as correctness-passed: {app}")
            if "required_evidence" not in row or not row["required_evidence"]:
                raise ValueError(f"pending app must define required evidence: {app}")
        if status == "excluded_from_standalone_v1_5":
            if row["release_gate_counts_as_passed"] is not False:
                raise ValueError(f"excluded app must not count as correctness-passed: {app}")
    return matrix


def validate_v1_5_standalone_correctness_summary() -> dict[str, Any]:
    summary = v1_5_standalone_correctness_summary()
    if summary["included_app_count"] != 14:
        raise ValueError("v1.5 standalone correctness summary must track 14 included apps")
    if summary["excluded_app_count"] != 4:
        raise ValueError("v1.5 standalone correctness summary must track 4 excluded apps")
    if summary["covered_app_count"] + summary["pending_app_count"] != summary["included_app_count"]:
        raise ValueError("v1.5 standalone correctness included counts mismatch")
    if tuple(summary["pending_apps"]) != tuple(sorted(V1_5_STANDALONE_CORRECTNESS_PENDING_APPS)):
        raise ValueError("v1.5 standalone correctness pending app list mismatch")
    if summary["release_gate_complete"] is not True:
        raise ValueError("v1.5 standalone correctness gate must be complete")
    return summary
