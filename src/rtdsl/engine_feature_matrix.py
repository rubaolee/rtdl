from __future__ import annotations

from dataclasses import dataclass


NATIVE = "native"
NATIVE_ASSISTED = "native_assisted"
COMPATIBILITY_FALLBACK = "compatibility_fallback"
UNSUPPORTED_EXPLICIT = "unsupported_explicit"

ENGINE_SUPPORT_STATUSES = (
    NATIVE,
    NATIVE_ASSISTED,
    COMPATIBILITY_FALLBACK,
    UNSUPPORTED_EXPLICIT,
)

RTDL_ENGINES = ("embree", "optix", "vulkan", "hiprt", "apple_rt")


@dataclass(frozen=True)
class EngineFeatureSupport:
    feature: str
    engine: str
    status: str
    note: str


def _support(feature: str, engine: str, status: str, note: str) -> EngineFeatureSupport:
    return EngineFeatureSupport(feature=feature, engine=engine, status=status, note=note)


_FEATURE_MATRIX: dict[str, dict[str, EngineFeatureSupport]] = {
    "line_segment_intersection_2d": {
        "embree": _support("line_segment_intersection_2d", "embree", NATIVE, "Embree BVH traversal plus exact segment refinement."),
        "optix": _support("line_segment_intersection_2d", "optix", NATIVE, "OptiX native 2D segment workload path."),
        "vulkan": _support("line_segment_intersection_2d", "vulkan", NATIVE, "Vulkan RT native 2D segment workload path."),
        "hiprt": _support("line_segment_intersection_2d", "hiprt", NATIVE, "HIPRT native 2D segment workload path when the library is available."),
        "apple_rt": _support("line_segment_intersection_2d", "apple_rt", NATIVE_ASSISTED, "Apple MPS/Metal path with exact 2D acceptance where available."),
    },
    "point_in_polygon_2d": {
        "embree": _support("point_in_polygon_2d", "embree", NATIVE, "Embree ray-crossing traversal path."),
        "optix": _support("point_in_polygon_2d", "optix", NATIVE, "OptiX native PIP workload path."),
        "vulkan": _support("point_in_polygon_2d", "vulkan", NATIVE, "Vulkan RT native PIP workload path."),
        "hiprt": _support("point_in_polygon_2d", "hiprt", NATIVE, "HIPRT native PIP workload path when the library is available."),
        "apple_rt": _support("point_in_polygon_2d", "apple_rt", NATIVE_ASSISTED, "Apple RT/Metal path is bounded and exactness-preserving, not a broad speedup claim."),
    },
    "overlay_compose_2d": {
        "embree": _support("overlay_compose_2d", "embree", NATIVE, "Embree overlap candidate traversal plus exact refinement."),
        "optix": _support("overlay_compose_2d", "optix", NATIVE, "OptiX bounded overlay workload path."),
        "vulkan": _support("overlay_compose_2d", "vulkan", NATIVE, "Vulkan bounded overlay workload path."),
        "hiprt": _support("overlay_compose_2d", "hiprt", NATIVE, "HIPRT bounded overlay workload path when available."),
        "apple_rt": _support("overlay_compose_2d", "apple_rt", NATIVE_ASSISTED, "Apple bounded overlap path uses native-assisted traversal/refinement where available."),
    },
    "ray_triangle_hit_count_2d": {
        "embree": _support("ray_triangle_hit_count_2d", "embree", NATIVE, "Embree ray/triangle hit-count traversal."),
        "optix": _support("ray_triangle_hit_count_2d", "optix", NATIVE, "OptiX ray/triangle hit-count traversal."),
        "vulkan": _support("ray_triangle_hit_count_2d", "vulkan", NATIVE, "Vulkan RT ray/triangle hit-count traversal."),
        "hiprt": _support("ray_triangle_hit_count_2d", "hiprt", NATIVE, "HIPRT 2D ray/triangle hit-count path."),
        "apple_rt": _support("ray_triangle_hit_count_2d", "apple_rt", NATIVE_ASSISTED, "Apple MPS-prism traversal plus exact 2D acceptance."),
    },
    "ray_triangle_hit_count_3d": {
        "embree": _support("ray_triangle_hit_count_3d", "embree", NATIVE, "Embree 3D ray/triangle hit-count traversal."),
        "optix": _support("ray_triangle_hit_count_3d", "optix", NATIVE, "OptiX 3D ray/triangle hit-count traversal."),
        "vulkan": _support("ray_triangle_hit_count_3d", "vulkan", NATIVE, "Vulkan RT 3D ray/triangle hit-count traversal."),
        "hiprt": _support("ray_triangle_hit_count_3d", "hiprt", NATIVE, "HIPRT 3D ray/triangle hit-count traversal."),
        "apple_rt": _support("ray_triangle_hit_count_3d", "apple_rt", NATIVE, "Apple MPS RT 3D ray/triangle hit-count path."),
    },
    "ray_triangle_any_hit_2d": {
        "embree": _support("ray_triangle_any_hit_2d", "embree", NATIVE, "Embree native early-exit any-hit via occlusion traversal."),
        "optix": _support("ray_triangle_any_hit_2d", "optix", NATIVE, "OptiX native early-exit any-hit using ray termination."),
        "vulkan": _support("ray_triangle_any_hit_2d", "vulkan", NATIVE, "Vulkan native early-exit any-hit using ray termination."),
        "hiprt": _support("ray_triangle_any_hit_2d", "hiprt", NATIVE, "HIPRT traversal-loop early-exit path."),
        "apple_rt": _support("ray_triangle_any_hit_2d", "apple_rt", NATIVE_ASSISTED, "Apple MPS-prism traversal with per-ray early exit plus exact 2D acceptance."),
    },
    "ray_triangle_any_hit_3d": {
        "embree": _support("ray_triangle_any_hit_3d", "embree", NATIVE, "Embree native early-exit any-hit via occlusion traversal."),
        "optix": _support("ray_triangle_any_hit_3d", "optix", NATIVE, "OptiX native early-exit any-hit using ray termination."),
        "vulkan": _support("ray_triangle_any_hit_3d", "vulkan", NATIVE, "Vulkan native early-exit any-hit using ray termination."),
        "hiprt": _support("ray_triangle_any_hit_3d", "hiprt", NATIVE, "HIPRT traversal-loop early-exit path."),
        "apple_rt": _support("ray_triangle_any_hit_3d", "apple_rt", NATIVE, "Apple MPS RT nearest-intersection existence path."),
    },
    "ray_triangle_closest_hit_3d": {
        "embree": _support("ray_triangle_closest_hit_3d", "embree", NATIVE, "Embree closest-hit traversal."),
        "optix": _support("ray_triangle_closest_hit_3d", "optix", NATIVE, "OptiX closest-hit traversal."),
        "vulkan": _support("ray_triangle_closest_hit_3d", "vulkan", NATIVE, "Vulkan RT closest-hit traversal where the backend is built."),
        "hiprt": _support("ray_triangle_closest_hit_3d", "hiprt", NATIVE, "HIPRT closest-hit traversal where the backend is built."),
        "apple_rt": _support("ray_triangle_closest_hit_3d", "apple_rt", NATIVE, "Apple MPS RT closest-hit traversal."),
    },
    "visibility_rows": {
        "embree": _support("visibility_rows", "embree", NATIVE, "Dispatches to Embree any-hit and emits visibility rows."),
        "optix": _support("visibility_rows", "optix", NATIVE, "Dispatches to OptiX any-hit and emits visibility rows."),
        "vulkan": _support("visibility_rows", "vulkan", NATIVE, "Dispatches to Vulkan any-hit and emits visibility rows."),
        "hiprt": _support("visibility_rows", "hiprt", NATIVE, "Dispatches to HIPRT any-hit and emits visibility rows."),
        "apple_rt": _support("visibility_rows", "apple_rt", NATIVE_ASSISTED, "Dispatches to Apple RT any-hit; 2D exact acceptance remains native-assisted."),
    },
    "prepared_scalar_visibility_count_2d": {
        "embree": _support("prepared_scalar_visibility_count_2d", "embree", COMPATIBILITY_FALLBACK, "Counts emitted prepared rows; no dedicated scalar-count native export."),
        "optix": _support("prepared_scalar_visibility_count_2d", "optix", NATIVE, "Prepared/prepacked scalar count path."),
        "vulkan": _support("prepared_scalar_visibility_count_2d", "vulkan", NATIVE, "Prepared/prepacked compact any-hit path followed by count."),
        "hiprt": _support("prepared_scalar_visibility_count_2d", "hiprt", NATIVE, "Prepared 2D any-hit reuse followed by count."),
        "apple_rt": _support("prepared_scalar_visibility_count_2d", "apple_rt", NATIVE_ASSISTED, "Prepared/prepacked scalar blocked-ray count path over MPS-prism traversal."),
    },
    "fixed_radius_neighbors_2d": {
        "embree": _support("fixed_radius_neighbors_2d", "embree", NATIVE, "Embree bounded neighbor traversal."),
        "optix": _support("fixed_radius_neighbors_2d", "optix", NATIVE, "OptiX bounded neighbor traversal."),
        "vulkan": _support("fixed_radius_neighbors_2d", "vulkan", NATIVE, "Vulkan bounded neighbor traversal."),
        "hiprt": _support("fixed_radius_neighbors_2d", "hiprt", NATIVE, "HIPRT bounded 2D neighbor traversal."),
        "apple_rt": _support("fixed_radius_neighbors_2d", "apple_rt", NATIVE_ASSISTED, "Apple bounded neighbor path is native-assisted where available."),
    },
    "fixed_radius_neighbors_3d": {
        "embree": _support("fixed_radius_neighbors_3d", "embree", NATIVE, "Embree bounded 3D neighbor traversal."),
        "optix": _support("fixed_radius_neighbors_3d", "optix", NATIVE, "OptiX bounded 3D neighbor traversal."),
        "vulkan": _support("fixed_radius_neighbors_3d", "vulkan", NATIVE, "Vulkan bounded 3D neighbor traversal."),
        "hiprt": _support("fixed_radius_neighbors_3d", "hiprt", NATIVE, "HIPRT bounded 3D neighbor traversal."),
        "apple_rt": _support("fixed_radius_neighbors_3d", "apple_rt", NATIVE_ASSISTED, "Apple bounded 3D neighbor path is native-assisted where available."),
    },
    "knn_rows_2d": {
        "embree": _support("knn_rows_2d", "embree", NATIVE, "Embree bounded nearest-neighbor rows."),
        "optix": _support("knn_rows_2d", "optix", NATIVE, "OptiX bounded nearest-neighbor rows."),
        "vulkan": _support("knn_rows_2d", "vulkan", NATIVE, "Vulkan bounded nearest-neighbor rows."),
        "hiprt": _support("knn_rows_2d", "hiprt", NATIVE, "HIPRT bounded nearest-neighbor rows."),
        "apple_rt": _support("knn_rows_2d", "apple_rt", NATIVE_ASSISTED, "Apple bounded KNN rows are native-assisted where available."),
    },
    "knn_rows_3d": {
        "embree": _support("knn_rows_3d", "embree", NATIVE, "Embree bounded 3D nearest-neighbor rows."),
        "optix": _support("knn_rows_3d", "optix", NATIVE, "OptiX bounded 3D nearest-neighbor rows."),
        "vulkan": _support("knn_rows_3d", "vulkan", NATIVE, "Vulkan bounded 3D nearest-neighbor rows."),
        "hiprt": _support("knn_rows_3d", "hiprt", NATIVE, "HIPRT bounded 3D nearest-neighbor rows."),
        "apple_rt": _support("knn_rows_3d", "apple_rt", NATIVE_ASSISTED, "Apple bounded 3D KNN rows are native-assisted where available."),
    },
    "bounded_db_conjunctive_scan": {
        "embree": _support("bounded_db_conjunctive_scan", "embree", NATIVE, "Embree user-primitive RT candidate discovery plus DB refinement."),
        "optix": _support("bounded_db_conjunctive_scan", "optix", NATIVE, "OptiX custom-primitive BVH candidate discovery plus DB refinement."),
        "vulkan": _support("bounded_db_conjunctive_scan", "vulkan", NATIVE, "Vulkan bounded DB candidate discovery path."),
        "hiprt": _support("bounded_db_conjunctive_scan", "hiprt", COMPATIBILITY_FALLBACK, "HIPRT DB surface is bounded; no AMD GPU performance claim."),
        "apple_rt": _support("bounded_db_conjunctive_scan", "apple_rt", NATIVE_ASSISTED, "Apple DB path is Metal compute/native-assisted, not Apple MPS RT traversal."),
    },
    "bounded_db_grouped_count": {
        "embree": _support("bounded_db_grouped_count", "embree", NATIVE, "Embree bounded RT-DB candidate discovery plus grouped count."),
        "optix": _support("bounded_db_grouped_count", "optix", NATIVE, "OptiX bounded RT-DB candidate discovery plus grouped count."),
        "vulkan": _support("bounded_db_grouped_count", "vulkan", NATIVE, "Vulkan bounded DB grouped-count path."),
        "hiprt": _support("bounded_db_grouped_count", "hiprt", COMPATIBILITY_FALLBACK, "HIPRT DB surface is bounded; no AMD GPU performance claim."),
        "apple_rt": _support("bounded_db_grouped_count", "apple_rt", NATIVE_ASSISTED, "Apple DB path is Metal compute/native-assisted, not Apple MPS RT traversal."),
    },
    "bounded_db_grouped_sum": {
        "embree": _support("bounded_db_grouped_sum", "embree", NATIVE, "Embree bounded RT-DB candidate discovery plus grouped sum."),
        "optix": _support("bounded_db_grouped_sum", "optix", NATIVE, "OptiX bounded RT-DB candidate discovery plus grouped sum."),
        "vulkan": _support("bounded_db_grouped_sum", "vulkan", NATIVE, "Vulkan bounded DB grouped-sum path."),
        "hiprt": _support("bounded_db_grouped_sum", "hiprt", COMPATIBILITY_FALLBACK, "HIPRT DB surface is bounded; no AMD GPU performance claim."),
        "apple_rt": _support("bounded_db_grouped_sum", "apple_rt", NATIVE_ASSISTED, "Apple DB path is Metal compute/native-assisted, not Apple MPS RT traversal."),
    },
    "graph_bfs": {
        "embree": _support("graph_bfs", "embree", NATIVE, "Embree bounded graph traversal mapping."),
        "optix": _support("graph_bfs", "optix", NATIVE, "OptiX bounded graph traversal mapping."),
        "vulkan": _support("graph_bfs", "vulkan", NATIVE, "Vulkan bounded graph traversal mapping."),
        "hiprt": _support("graph_bfs", "hiprt", COMPATIBILITY_FALLBACK, "HIPRT graph surface exists but has known memory-scaling limits; no large-graph claim."),
        "apple_rt": _support("graph_bfs", "apple_rt", NATIVE_ASSISTED, "Apple graph path is Metal compute/native-assisted, not Apple MPS RT traversal."),
    },
    "graph_triangle_count": {
        "embree": _support("graph_triangle_count", "embree", NATIVE, "Embree bounded graph triangle-probe mapping."),
        "optix": _support("graph_triangle_count", "optix", NATIVE, "OptiX bounded graph triangle-probe mapping."),
        "vulkan": _support("graph_triangle_count", "vulkan", NATIVE, "Vulkan bounded graph triangle-probe mapping."),
        "hiprt": _support("graph_triangle_count", "hiprt", COMPATIBILITY_FALLBACK, "HIPRT graph surface exists but has known memory-scaling limits; no large-graph claim."),
        "apple_rt": _support("graph_triangle_count", "apple_rt", NATIVE_ASSISTED, "Apple graph path is Metal compute/native-assisted, not Apple MPS RT traversal."),
    },
    "reduce_rows": {
        "embree": _support("reduce_rows", "embree", COMPATIBILITY_FALLBACK, "Python standard-library helper over emitted rows; not a backend-native reduction."),
        "optix": _support("reduce_rows", "optix", COMPATIBILITY_FALLBACK, "Python standard-library helper over emitted rows; not a backend-native reduction."),
        "vulkan": _support("reduce_rows", "vulkan", COMPATIBILITY_FALLBACK, "Python standard-library helper over emitted rows; not a backend-native reduction."),
        "hiprt": _support("reduce_rows", "hiprt", COMPATIBILITY_FALLBACK, "Python standard-library helper over emitted rows; not a backend-native reduction."),
        "apple_rt": _support("reduce_rows", "apple_rt", COMPATIBILITY_FALLBACK, "Python standard-library helper over emitted rows; not a backend-native reduction."),
    },
}


def public_engine_features() -> tuple[str, ...]:
    return tuple(_FEATURE_MATRIX)


def engine_feature_support(feature: str, engine: str) -> EngineFeatureSupport:
    try:
        return _FEATURE_MATRIX[feature][engine]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL feature/engine pair: feature={feature!r}, engine={engine!r}") from exc


def engine_feature_support_matrix() -> dict[str, dict[str, EngineFeatureSupport]]:
    return {feature: dict(entries) for feature, entries in _FEATURE_MATRIX.items()}


def assert_engine_feature_supported(feature: str, engine: str) -> EngineFeatureSupport:
    support = engine_feature_support(feature, engine)
    if support.status == UNSUPPORTED_EXPLICIT:
        raise NotImplementedError(f"RTDL feature {feature!r} is explicitly unsupported on engine {engine!r}: {support.note}")
    return support
