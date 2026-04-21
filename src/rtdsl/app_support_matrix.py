from __future__ import annotations

from dataclasses import dataclass


APP_ENGINES = ("cpu_python_reference", "embree", "optix", "vulkan", "hiprt", "apple_rt")

DIRECT_CLI_NATIVE = "direct_cli_native"
DIRECT_CLI_NATIVE_ASSISTED = "direct_cli_native_assisted"
DIRECT_CLI_COMPATIBILITY_FALLBACK = "direct_cli_compatibility_fallback"
PORTABLE_CPU_ORACLE = "portable_cpu_oracle"
PARTIAL_CPU_ORACLE = "partial_cpu_oracle"
NOT_EXPOSED_BY_APP_CLI = "not_exposed_by_app_cli"
APPLE_SPECIFIC = "apple_specific"

APP_SUPPORT_STATUSES = (
    DIRECT_CLI_NATIVE,
    DIRECT_CLI_NATIVE_ASSISTED,
    DIRECT_CLI_COMPATIBILITY_FALLBACK,
    PORTABLE_CPU_ORACLE,
    PARTIAL_CPU_ORACLE,
    NOT_EXPOSED_BY_APP_CLI,
    APPLE_SPECIFIC,
)


@dataclass(frozen=True)
class AppEngineSupport:
    app: str
    engine: str
    status: str
    note: str


def _support(app: str, engine: str, status: str, note: str) -> AppEngineSupport:
    return AppEngineSupport(app=app, engine=engine, status=status, note=note)


def _row(
    app: str,
    *,
    cpu_python_reference: str,
    embree: str,
    optix: str,
    vulkan: str,
    hiprt: str,
    apple_rt: str,
    note: str,
) -> dict[str, AppEngineSupport]:
    statuses = {
        "cpu_python_reference": cpu_python_reference,
        "embree": embree,
        "optix": optix,
        "vulkan": vulkan,
        "hiprt": hiprt,
        "apple_rt": apple_rt,
    }
    return {engine: _support(app, engine, status, note) for engine, status in statuses.items()}


_CPU = PORTABLE_CPU_ORACLE
_NATIVE = DIRECT_CLI_NATIVE
_ASSISTED = DIRECT_CLI_NATIVE_ASSISTED
_COMPAT = DIRECT_CLI_COMPATIBILITY_FALLBACK
_NOCLI = NOT_EXPOSED_BY_APP_CLI
_APPLE = APPLE_SPECIFIC


_APP_MATRIX: dict[str, dict[str, AppEngineSupport]] = {
    "database_analytics": _row(
        "database_analytics",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Primary DB app exposes CPU/Embree/OptiX/Vulkan; HIPRT and Apple DB feature paths exist below the app layer but are not exposed by this app CLI.",
    ),
    "graph_analytics": _row(
        "graph_analytics",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios.",
    ),
    "apple_rt_demo": _row(
        "apple_rt_demo",
        cpu_python_reference=PARTIAL_CPU_ORACLE,
        embree=_APPLE,
        optix=_APPLE,
        vulkan=_APPLE,
        hiprt=_APPLE,
        apple_rt=_ASSISTED,
        note="Primary Apple RT demo is Apple-specific; closest-hit has CPU reference parity, visibility-count is hardware-gated and may skip if Apple RT is unavailable.",
    ),
    "service_coverage_gaps": _row(
        "service_coverage_gaps",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial radius-join app currently exposes CPU, Embree, and SciPy baseline; other RT engines are not app CLI options.",
    ),
    "event_hotspot_screening": _row(
        "event_hotspot_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial self-join app currently exposes CPU, Embree, and SciPy baseline.",
    ),
    "facility_knn_assignment": _row(
        "facility_knn_assignment",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial KNN app currently exposes CPU, Embree, and SciPy baseline.",
    ),
    "road_hazard_screening": _row(
        "road_hazard_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "segment_polygon_hitcount": _row(
        "segment_polygon_hitcount",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "segment_polygon_anyhit_rows": _row(
        "segment_polygon_anyhit_rows",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "polygon_pair_overlap_area_rows": _row(
        "polygon_pair_overlap_area_rows",
        cpu_python_reference=_CPU,
        embree=_NOCLI,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Current public script is CPU-reference only.",
    ),
    "polygon_set_jaccard": _row(
        "polygon_set_jaccard",
        cpu_python_reference=_CPU,
        embree=_NOCLI,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Current public script is CPU-reference only.",
    ),
    "hausdorff_distance": _row(
        "hausdorff_distance",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="KNN app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "ann_candidate_search": _row(
        "ann_candidate_search",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Candidate-search app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "outlier_detection": _row(
        "outlier_detection",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Density app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "dbscan_clustering": _row(
        "dbscan_clustering",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="DBSCAN app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "robot_collision_screening": _row(
        "robot_collision_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Discrete collision app exposes CPU, Embree, and OptiX; Vulkan is intentionally not exposed until a dedicated any-hit app gate exists.",
    ),
    "barnes_hut_force_app": _row(
        "barnes_hut_force_app",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Candidate-generation app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "sales_risk_screening": _row(
        "sales_risk_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Scenario-specific DB app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "regional_order_dashboard": _row(
        "regional_order_dashboard",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Scenario-specific prepared DB app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "regional_order_dashboard_kernel_form": _row(
        "regional_order_dashboard_kernel_form",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Kernel-form DB demo exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "apple_rt_closest_hit": _row(
        "apple_rt_closest_hit",
        cpu_python_reference=_CPU,
        embree=_APPLE,
        optix=_APPLE,
        vulkan=_APPLE,
        hiprt=_APPLE,
        apple_rt=_NATIVE,
        note="Scenario-specific Apple RT closest-hit demo.",
    ),
    "apple_rt_visibility_count": _row(
        "apple_rt_visibility_count",
        cpu_python_reference=PARTIAL_CPU_ORACLE,
        embree=_APPLE,
        optix=_APPLE,
        vulkan=_APPLE,
        hiprt=_APPLE,
        apple_rt=_ASSISTED,
        note="Scenario-specific prepared/prepacked Apple RT visibility-count demo.",
    ),
    "hiprt_ray_triangle_hitcount": _row(
        "hiprt_ray_triangle_hitcount",
        cpu_python_reference=_CPU,
        embree=_NOCLI,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NATIVE,
        apple_rt=_NOCLI,
        note="Scenario-specific HIPRT hit-count demo; HIPRT evidence is SDK/Orochi on tested hosts, not AMD GPU validation.",
    ),
}


def public_apps() -> tuple[str, ...]:
    return tuple(_APP_MATRIX)


def app_engine_support(app: str, engine: str) -> AppEngineSupport:
    try:
        return _APP_MATRIX[app][engine]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL app/engine pair: app={app!r}, engine={engine!r}") from exc


def app_engine_support_matrix() -> dict[str, dict[str, AppEngineSupport]]:
    return {app: dict(entries) for app, entries in _APP_MATRIX.items()}
