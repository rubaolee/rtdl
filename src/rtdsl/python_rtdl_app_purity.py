from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from .v1_5_standalone_app_classification import (
    v1_5_standalone_app_classification_matrix,
)


PYTHON_RTDL_PRODUCT_TARGET = "v2.5_python_rtdl_product_checkpoint"
PYTHON_RTDL_OPTIMIZATION_FREEZE_UNTIL = "v2.5"
PYTHON_RTDL_FASTEST_COLLECT_K_ENV = "RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1"

PURE_APP_READY = "pure_python_rtdl_ready"
LEGACY_ENGINE_CUSTOMIZED = "legacy_engine_customized"
EXPERIMENTAL_PRIMITIVE_BLOCKED = "experimental_primitive_blocked"
FROZEN_OR_DEMO_ONLY = "frozen_or_demo_only"

APP_PURITY_STATUSES = (
    PURE_APP_READY,
    LEGACY_ENGINE_CUSTOMIZED,
    EXPERIMENTAL_PRIMITIVE_BLOCKED,
    FROZEN_OR_DEMO_ONLY,
)

_APP_SHAPED_NATIVE_SYMBOL_FRAGMENTS = (
    "_run_lsi",
    "_run_pip",
    "_run_overlay",
    "_segment_polygon_",
    "_polygon_pair_",
    "_polygon_set_jaccard",
    "_point_polygon_",
    "_db_dataset_",
    "_db_table",
    "_db_match",
    "_db_conjunctive_scan",
    "_run_db",
    "_db_compact_summary",
    "_fill_db_compact_summary",
    "_pose_flags_",
    "_prepare_pose_indices_",
    "_directed_hausdorff_",
    "_run_bfs_expand",
    "_run_knn_rows",
    "_knn_rows_",
    "_bounded_knn_rows",
    "_summarize_knn_rows",
    "_run_triangle_probe",
)

_GENERIC_NATIVE_SYMBOL_FRAGMENTS = (
    "_get_version",
    "_run_ray_anyhit",
    "_run_ray_hitcount",
    "_prepare_ray_anyhit",
    "_prepare_ray_anyhit_2d_device_triangles",
    "_prepare_rays_",
    "_count_prepared_ray_anyhit",
    "_count_prepared_ray_anyhit_2d_device_rays",
    "_run_fixed_radius_neighbors",
    "_run_fixed_radius_count_threshold",
    "_prepare_fixed_radius_count_threshold",
    "_run_prepared_fixed_radius_count_threshold",
    "_count_prepared_fixed_radius_threshold",
    "_run_k_closest_hits",
    "_run_bounded_k_closest_hits",
    "_k_closest_hits_2d",
    "_summarize_k_closest_hits",
    "_run_grouped_count",
    "_run_grouped_sum",
    "_run_conjunctive_scan",
    "_columnar_payload_",
    "_prepare_columnar_payload",
    "_destroy_prepared_columnar_payload",
    "_multi_predicate_scan",
    "_predicate_match",
    "_grouped_reduction_",
    "_columnar_compact_summary_",
    "_fill_columnar_compact_summary_",
    "_collect_k_bounded_i64",
    "_run_point_primitive_anyhit_packet",
    "_run_max_distance_nearest_candidate_2d",
    "_run_segment_pair_intersection",
    "_run_shape_pair_relation_flags",
    "_run_edge_neighbor_intersection_packet",
    "_segment_shape_",
    "_point_shape_",
    "_shape_pair_",
    "_shape_set_overlap_ratio",
    "_reduce_shape_pair_exact_area_summary",
    "_run_frontier_edge_traversal_packet",
    "_run_prepared_frontier_edge_traversal_packet",
    "_summarize_frontier_traversal_rows",
    "_run_triangle_cycle_candidates",
    "_run_prepared_triangle_cycle_candidates",
    "_run_frontier_discover_compute",
)


@dataclass(frozen=True)
class NativeSymbolClassification:
    symbol: str
    source: str
    line: int
    classification: str
    reason: str


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]


def _native_api_paths(root: Path) -> tuple[Path, ...]:
    return (
        root / "src" / "native" / "embree" / "rtdl_embree_api.cpp",
        root / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
    )


def _exported_symbols(path: Path) -> tuple[tuple[str, int], ...]:
    if not path.exists():
        return ()
    pattern = re.compile(
        r'(?:extern\s+"C"\s+[A-Za-z_][A-Za-z0-9_:<>\s\*&]*|'
        r'RTDL_EMBREE_EXPORT\s+[A-Za-z_][A-Za-z0-9_:<>\s\*&]*)\s+'
        r'(rtdl_[A-Za-z0-9_]+)\s*\('
    )
    symbols: list[tuple[str, int]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.search(line)
        if match:
            symbols.append((match.group(1), line_number))
    return tuple(symbols)


def classify_native_symbol(symbol: str) -> tuple[str, str]:
    if any(fragment in symbol for fragment in _APP_SHAPED_NATIVE_SYMBOL_FRAGMENTS):
        return (
            LEGACY_ENGINE_CUSTOMIZED,
            "app-shaped native ABI or native continuation; not a pure Python+RTDL app contract",
        )
    if any(fragment in symbol for fragment in _GENERIC_NATIVE_SYMBOL_FRAGMENTS):
        return (PURE_APP_READY, "generic primitive-shaped native ABI")
    if "_probe" in symbol or "_smoke" in symbol or "_capability" in symbol:
        return ("diagnostic", "diagnostic/probe ABI, not a public app contract")
    return ("unclassified", "native export needs explicit purity classification")


def native_symbol_purity_audit(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    classifications: list[NativeSymbolClassification] = []
    for path in _native_api_paths(root):
        for symbol, line in _exported_symbols(path):
            classification, reason = classify_native_symbol(symbol)
            classifications.append(
                NativeSymbolClassification(
                    symbol=symbol,
                    source=str(path.relative_to(root)),
                    line=line,
                    classification=classification,
                    reason=reason,
                )
            )

    blockers = tuple(
        row
        for row in classifications
        if row.classification in {LEGACY_ENGINE_CUSTOMIZED, "unclassified"}
    )
    return {
        "target": PYTHON_RTDL_PRODUCT_TARGET,
        "optimization_freeze_until": PYTHON_RTDL_OPTIMIZATION_FREEZE_UNTIL,
        "fastest_collect_k_env": PYTHON_RTDL_FASTEST_COLLECT_K_ENV,
        "native_symbols": tuple(classifications),
        "blockers": blockers,
        "legacy_engine_customized_symbols": tuple(
            row for row in classifications if row.classification == LEGACY_ENGINE_CUSTOMIZED
        ),
        "unclassified_symbols": tuple(
            row for row in classifications if row.classification == "unclassified"
        ),
        "pure_native_app_contract_ready": not blockers,
    }


def python_rtdl_app_purity_matrix() -> dict[str, dict[str, Any]]:
    # This intentionally reuses the v1.5 standalone classification as the
    # current app inventory, then overlays the stricter Python+RTDL product rule.
    matrix = v1_5_standalone_app_classification_matrix()
    result: dict[str, dict[str, Any]] = {}
    for app, row in matrix.items():
        classification = row["classification"]
        if classification in {"fully_generic", "scalar_only"}:
            status = PURE_APP_READY
            blocker = ""
        elif classification == "collection_dependent":
            status = EXPERIMENTAL_PRIMITIVE_BLOCKED
            blocker = "depends on experimental COLLECT_K_BOUNDED promotion boundary"
        elif classification in {"frozen", "demo_only"}:
            status = FROZEN_OR_DEMO_ONLY
            blocker = "outside active Embree+OptiX Python+RTDL product target"
        else:
            status = LEGACY_ENGINE_CUSTOMIZED
            blocker = "uses wrapper-backed or app-shaped native continuation"
        result[app] = {
            "status": status,
            "generic_surface": row["generic_surface"],
            "blocker": blocker,
            "target_rule": (
                "app logic must stay in Python and call generic RTDL primitives; "
                "engines must not encode app names or app-specific continuation semantics"
            ),
        }
    return result


def python_rtdl_product_checkpoint(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    symbol_audit = native_symbol_purity_audit(repo_root=repo_root)
    app_matrix = python_rtdl_app_purity_matrix()
    app_blockers = {
        app: row
        for app, row in app_matrix.items()
        if row["status"] != PURE_APP_READY
    }
    return {
        "target": PYTHON_RTDL_PRODUCT_TARGET,
        "optimization_freeze_until": PYTHON_RTDL_OPTIMIZATION_FREEZE_UNTIL,
        "fastest_collect_k_env": PYTHON_RTDL_FASTEST_COLLECT_K_ENV,
        "app_matrix": app_matrix,
        "app_blockers": app_blockers,
        "native_symbol_audit": symbol_audit,
        "product_ready": not app_blockers and symbol_audit["pure_native_app_contract_ready"],
        "rule": (
            "Before v2.5, keep the accepted fastest collect-k solution and stop "
            "new optimization studies. Use the remaining work window to migrate "
            "public apps to pure Python orchestration over generic RTDL primitives."
        ),
    }


def validate_python_rtdl_product_checkpoint(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    checkpoint = python_rtdl_product_checkpoint(repo_root=repo_root)
    if checkpoint["optimization_freeze_until"] != "v2.5":
        raise ValueError("optimization freeze boundary must remain v2.5")
    if checkpoint["fastest_collect_k_env"] != PYTHON_RTDL_FASTEST_COLLECT_K_ENV:
        raise ValueError("fastest collect-k environment contract changed")
    if checkpoint["product_ready"]:
        raise ValueError("checkpoint must not claim product-ready while blockers remain")
    if not checkpoint["app_blockers"]:
        raise ValueError("checkpoint unexpectedly has no app blockers")
    symbol_audit = checkpoint["native_symbol_audit"]
    if symbol_audit["pure_native_app_contract_ready"]:
        raise ValueError("native symbol audit unexpectedly has no blockers")
    return checkpoint
