from __future__ import annotations

import time
from typing import Any

from . import api as rt
from .layout_types import Ray2DLayout
from .layout_types import Ray3DLayout
from .layout_types import Rays
from .layout_types import Rays3D
from .layout_types import Triangle2DLayout
from .layout_types import Triangle3DLayout
from .layout_types import Triangles
from .layout_types import Triangles3D
from .grouped_reduction_contracts import V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT
from .reference import Ray2D
from .reference import Ray3D
from .reference import Triangle
from .reference import Triangle3D
from .reference import _finite_ray_hits_triangle
from .reference import _triangle_dimension
from .reference import ray_triangle_any_hit_cpu
from .reference import ray_triangle_closest_hit_cpu
from .reduction_runtime import run_generic_scalar_reduction


ACTIVE_V1_5_GENERIC_PRIMITIVE_BACKENDS = ("cpu", "embree", "optix")
FROZEN_BEFORE_V2_1_GENERIC_BACKENDS = ("vulkan", "hiprt", "apple_rt")
GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE = "RAY_TRIANGLE_HIT_STREAM_3D"
GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA = ("ray_id", "primitive_id")
GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_CONTRACT = {
    "primitive": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
    "row_schema": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
    "semantics": (
        "Emit app-free 3-D ray/triangle hit rows. A row records only the query "
        "ray id and hit primitive index. App-owned adapters may map primitive "
        "indices to group ids or payload values after RT traversal."
    ),
    "overflow_policy": "fail_closed_bounded_rows",
    "native_engine_app_semantics": False,
}


@rt.kernel(backend="rtdl", precision="float_approx")
def _generic_ray_triangle_any_hit_2d_kernel():
    rays = rt.input("rays", Rays, layout=Ray2DLayout, role="probe")
    triangles = rt.input("triangles", Triangles, layout=Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _generic_ray_triangle_any_hit_3d_kernel():
    rays = rt.input("rays", Rays3D, layout=Ray3DLayout, role="probe")
    triangles = rt.input("triangles", Triangles3D, layout=Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _generic_ray_triangle_closest_hit_2d_kernel():
    rays = rt.input("rays", Rays, layout=Ray2DLayout, role="probe")
    triangles = rt.input("triangles", Triangles, layout=Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _generic_ray_triangle_closest_hit_3d_kernel():
    rays = rt.input("rays", Rays3D, layout=Ray3DLayout, role="probe")
    triangles = rt.input("triangles", Triangles3D, layout=Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


def _normalize_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    aliases = {
        "python": "cpu",
        "cpu_python_reference": "cpu",
        "apple": "apple_rt",
        "metal": "apple_rt",
    }
    return aliases.get(normalized, normalized)


def _packed_runtime_types() -> tuple[type | None, type | None]:
    try:
        from .embree_runtime import PackedRays
        from .embree_runtime import PackedTriangles
    except Exception:
        return None, None
    return PackedRays, PackedTriangles


def _unpack_packed_rays_3d(packed: Any) -> tuple[Ray3D, ...]:
    if int(packed.dimension) != 3:
        raise TypeError("generic ray/triangle hit stream 3D requires 3-D rays")
    return tuple(
        Ray3D(
            id=int(record.id),
            ox=float(record.ox),
            oy=float(record.oy),
            oz=float(record.oz),
            dx=float(record.dx),
            dy=float(record.dy),
            dz=float(record.dz),
            tmax=float(record.tmax),
        )
        for record in packed.records[: int(packed.count)]
    )


def _unpack_packed_triangles_3d(packed: Any) -> tuple[Triangle3D, ...]:
    if int(packed.dimension) != 3:
        raise TypeError("generic ray/triangle hit stream 3D requires 3-D triangles")
    return tuple(
        Triangle3D(
            id=int(record.id),
            x0=float(record.x0),
            y0=float(record.y0),
            z0=float(record.z0),
            x1=float(record.x1),
            y1=float(record.y1),
            z1=float(record.z1),
            x2=float(record.x2),
            y2=float(record.y2),
            z2=float(record.z2),
        )
        for record in packed.records[: int(packed.count)]
    )


def _ray_dimension(rays: tuple[Ray2D | Ray3D, ...]) -> int | None:
    if not rays:
        return None
    first_is_3d = isinstance(rays[0], Ray3D)
    if any(isinstance(ray, Ray3D) != first_is_3d for ray in rays):
        raise ValueError("generic ray_triangle_any_hit requires all rays to share one dimensionality")
    return 3 if first_is_3d else 2


def _validate_triangle_dimension(
    triangles: tuple[Triangle | Triangle3D, ...],
    dimension: int | None,
) -> None:
    if dimension is None or not triangles:
        return
    if any(_triangle_dimension(triangle) != dimension for triangle in triangles):
        raise ValueError("generic ray_triangle_any_hit requires rays and triangles to share dimensionality")


def _zero_any_hit_rows(rays: tuple[Ray2D | Ray3D, ...]) -> tuple[dict[str, int], ...]:
    return tuple({"ray_id": int(ray.id), "any_hit": 0} for ray in rays)


def _validate_prepared_anyhit_count_backend(backend: str) -> str:
    normalized_backend = _normalize_backend(backend)
    if normalized_backend in FROZEN_BEFORE_V2_1_GENERIC_BACKENDS:
        raise ValueError(
            f"{normalized_backend} is frozen before v2.1; v1.5 prepared generic primitives are OptiX-focused"
        )
    if normalized_backend != "optix":
        raise ValueError("prepared generic ray_triangle_any_hit_count currently supports backend='optix'")
    return normalized_backend


def _validate_fixed_radius_count_backend(backend: str) -> str:
    normalized_backend = _normalize_backend(backend)
    if normalized_backend in FROZEN_BEFORE_V2_1_GENERIC_BACKENDS:
        raise ValueError(
            f"{normalized_backend} is frozen before v2.1; v1.5 generic primitives are Embree/OptiX only"
        )
    if normalized_backend not in ACTIVE_V1_5_GENERIC_PRIMITIVE_BACKENDS:
        raise ValueError("generic fixed_radius_count_threshold backend must be one of: cpu, embree, optix")
    return normalized_backend


def _validate_prepared_fixed_radius_count_backend(backend: str) -> str:
    normalized_backend = _validate_fixed_radius_count_backend(backend)
    if normalized_backend == "cpu":
        raise ValueError("prepared generic fixed_radius_count_threshold currently supports embree and optix")
    return normalized_backend


def _point_xy(point: Any) -> tuple[float, float]:
    try:
        return float(point.x), float(point.y)
    except AttributeError:
        if len(point) >= 2:
            return float(point[0]), float(point[1])
        raise TypeError("generic fixed_radius_count_threshold requires 2-D point-like inputs") from None


def _cpu_fixed_radius_count_threshold_rows(
    query_points: Any,
    search_points: Any,
    *,
    radius: float,
    threshold: int,
) -> tuple[dict[str, int], ...]:
    radius_sq = float(radius) * float(radius)
    search_xy = [_point_xy(point) for point in search_points]
    rows = []
    for query_index, query_point in enumerate(query_points):
        qx, qy = _point_xy(query_point)
        query_id = int(getattr(query_point, "id", query_index))
        neighbor_count = 0
        for sx, sy in search_xy:
            dx = qx - sx
            dy = qy - sy
            if dx * dx + dy * dy <= radius_sq:
                neighbor_count += 1
                if threshold > 0 and neighbor_count >= threshold:
                    break
        rows.append(
            {
                "query_id": query_id,
                "neighbor_count": neighbor_count,
                "threshold_reached": 1 if threshold > 0 and neighbor_count >= threshold else 0,
            }
        )
    return tuple(rows)


def _threshold_reached_scalar_summary(rows: Any) -> dict[str, Any]:
    threshold_rows = tuple(row for row in rows if bool(int(row["threshold_reached"])))
    return run_generic_scalar_reduction(threshold_rows, summary_primitive="REDUCE_INT(COUNT)")


def _scalar_reduction_metadata(scalar_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in scalar_summary.items()
        if key not in {"result", "row_count"}
    }


def run_generic_ray_triangle_any_hit(
    rays: tuple[Ray2D | Ray3D, ...],
    triangles: tuple[Triangle | Triangle3D, ...],
    *,
    backend: str = "cpu",
) -> tuple[dict[str, int], ...]:
    """Run the v1.5 app-name-free `ANY_HIT` ray/triangle primitive."""
    normalized_backend = _normalize_backend(backend)
    if normalized_backend in FROZEN_BEFORE_V2_1_GENERIC_BACKENDS:
        raise ValueError(
            f"{normalized_backend} is frozen before v2.1; v1.5 generic primitives are Embree/OptiX only"
        )
    if normalized_backend not in ACTIVE_V1_5_GENERIC_PRIMITIVE_BACKENDS:
        raise ValueError("generic ray_triangle_any_hit backend must be one of: cpu, embree, optix")

    dimension = _ray_dimension(rays)
    _validate_triangle_dimension(triangles, dimension)
    if not rays:
        return ()
    if not triangles:
        return _zero_any_hit_rows(rays)
    if normalized_backend == "cpu":
        return ray_triangle_any_hit_cpu(rays, triangles)

    kernel = _generic_ray_triangle_any_hit_3d_kernel if dimension == 3 else _generic_ray_triangle_any_hit_2d_kernel
    inputs = {"rays": rays, "triangles": triangles}
    if normalized_backend == "embree":
        from .embree_runtime import run_embree

        rows = run_embree(kernel, **inputs)
    else:
        from .optix_runtime import run_optix

        rows = run_optix(kernel, **inputs)
    return tuple({"ray_id": int(row["ray_id"]), "any_hit": int(row["any_hit"])} for row in rows)


def run_generic_ray_triangle_any_hit_count(
    rays: tuple[Ray2D | Ray3D, ...],
    triangles: tuple[Triangle | Triangle3D, ...],
    *,
    backend: str = "cpu",
    include_rows: bool = False,
) -> dict[str, Any]:
    """Run app-name-free `ANY_HIT` and reduce the result with `COUNT_HITS`."""
    normalized_backend = _normalize_backend(backend)
    rows = run_generic_ray_triangle_any_hit(rays, triangles, backend=normalized_backend)
    scalar_summary = run_generic_scalar_reduction(rows, summary_primitive="COUNT_HITS")
    result: dict[str, Any] = {
        "primitive": "ANY_HIT",
        "summary_primitive": "COUNT_HITS",
        "backend": normalized_backend,
        "active_v1_5_backend": normalized_backend in {"embree", "optix"},
        "row_count": len(rows),
        "hit_count": scalar_summary["result"],
        "result_layout": "aggregate_any_hit_count",
        "scalar_reduction": _scalar_reduction_metadata(scalar_summary),
        "claim_boundary": (
            "Generic v1.5 raw ray/triangle ANY_HIT plus COUNT_HITS only; "
            "no app-specific visibility, graph, DB, polygon, or public speedup claim."
        ),
    }
    if include_rows:
        result["rows"] = rows
    return result


def run_generic_ray_triangle_closest_hit(
    rays: tuple[Ray2D | Ray3D, ...],
    triangles: tuple[Triangle | Triangle3D, ...],
    *,
    backend: str = "cpu",
) -> tuple[dict[str, float | int], ...]:
    """Run app-name-free ray/triangle `CLOSEST_HIT` rows.

    This is the generic primitive shape needed by RMQ-style RT lowerings: the
    engine sees only rays and triangles and returns ray id, primitive id, and
    hit distance. RMQ/domain interpretation stays outside the engine.
    """
    normalized_backend = _normalize_backend(backend)
    if normalized_backend in FROZEN_BEFORE_V2_1_GENERIC_BACKENDS:
        raise ValueError(
            f"{normalized_backend} is frozen before v2.1; active generic primitives are Embree/OptiX focused"
        )
    if normalized_backend not in ACTIVE_V1_5_GENERIC_PRIMITIVE_BACKENDS:
        raise ValueError("generic ray_triangle_closest_hit backend must be one of: cpu, embree, optix")

    dimension = _ray_dimension(rays)
    _validate_triangle_dimension(triangles, dimension)
    if not rays or not triangles:
        return ()
    if normalized_backend == "cpu":
        return ray_triangle_closest_hit_cpu(rays, triangles)
    if dimension != 3:
        raise ValueError(f"generic ray_triangle_closest_hit backend={normalized_backend!r} currently requires 3-D rays and triangles")

    if normalized_backend == "embree":
        from .embree_runtime import run_embree

        rows = run_embree(
            _generic_ray_triangle_closest_hit_3d_kernel,
            rays=rays,
            triangles=triangles,
        )
    else:
        from .optix_runtime import run_optix

        rows = run_optix(
            _generic_ray_triangle_closest_hit_3d_kernel,
            rays=rays,
            triangles=triangles,
        )
    return tuple(
        {
            "ray_id": int(row["ray_id"]),
            "triangle_id": int(row["triangle_id"]),
            "t": float(row["t"]),
        }
        for row in rows
    )


def run_generic_ray_triangle_hit_stream_3d(
    rays: tuple[Ray3D, ...],
    triangles: tuple[Triangle3D, ...],
    *,
    max_rows: int | None = None,
    deduplicate_primitives: bool = True,
    backend: str = "cpu",
) -> dict[str, Any]:
    """Emit a generic bounded 3-D ray/triangle hit stream.

    The native/app boundary is intentionally narrow: RTDL emits ray ids and
    primitive ids only. Mapping primitive ids to group keys, SQL predicates, or
    aggregate payloads is app-owned continuation work.
    """
    normalized_backend = _normalize_backend(backend)
    if normalized_backend not in {"cpu", "embree", "optix"}:
        raise ValueError("generic ray/triangle hit stream backend must be one of: cpu, embree, optix")
    if max_rows is not None and int(max_rows) < 0:
        raise ValueError("max_rows must be non-negative")
    packed_rays_type, packed_triangles_type = _packed_runtime_types()
    rays_are_packed = packed_rays_type is not None and isinstance(rays, packed_rays_type)
    triangles_are_packed = packed_triangles_type is not None and isinstance(triangles, packed_triangles_type)
    triangle_count = int(triangles.count) if packed_triangles_type is not None and isinstance(triangles, packed_triangles_type) else len(triangles)
    ray_count = int(rays.count) if packed_rays_type is not None and isinstance(rays, packed_rays_type) else len(rays)
    if rays_are_packed:
        if rays.dimension != 3:
            raise TypeError("generic ray/triangle hit stream 3D requires 3-D rays")
    elif any(not isinstance(ray, Ray3D) for ray in rays):
        raise TypeError("generic ray/triangle hit stream 3D requires Ray3D inputs")
    if triangles_are_packed:
        if triangles.dimension != 3:
            raise TypeError("generic ray/triangle hit stream 3D requires 3-D triangles")
    elif any(not isinstance(triangle, Triangle3D) for triangle in triangles):
        raise TypeError("generic ray/triangle hit stream 3D requires Triangle3D inputs")

    if normalized_backend == "embree":
        from .embree_runtime import ray_triangle_hit_stream_3d_embree

        return ray_triangle_hit_stream_3d_embree(
            rays,
            triangles,
            max_rows=max_rows,
            deduplicate_primitives=deduplicate_primitives,
        )
    if normalized_backend == "optix":
        from .optix_runtime import ray_triangle_hit_stream_3d_optix

        return ray_triangle_hit_stream_3d_optix(
            rays,
            triangles,
            max_rows=max_rows,
            deduplicate_primitives=deduplicate_primitives,
        )

    if rays_are_packed:
        rays = _unpack_packed_rays_3d(rays)
    if triangles_are_packed:
        triangles = _unpack_packed_triangles_3d(triangles)

    started = time.perf_counter()
    hit_event_count = 0
    candidate_rows: list[dict[str, int]] = []
    seen_indices: set[int] = set()
    for ray in rays:
        for primitive_index, triangle in enumerate(triangles):
            if not _finite_ray_hits_triangle(ray, triangle):
                continue
            hit_event_count += 1
            if deduplicate_primitives:
                if primitive_index in seen_indices:
                    continue
                seen_indices.add(primitive_index)
            candidate_rows.append({"ray_id": int(ray.id), "primitive_id": int(primitive_index)})
    candidate_rows.sort(key=lambda row: (row["primitive_id"], row["ray_id"]))
    capacity = (
        triangle_count
        if max_rows is None and deduplicate_primitives
        else int(max_rows if max_rows is not None else max(1, ray_count * triangle_count))
    )
    overflow = len(candidate_rows) > capacity
    rows = () if overflow else tuple(candidate_rows)
    elapsed = time.perf_counter() - started
    return {
        "primitive": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
        "backend": normalized_backend,
        "row_schema": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
        "rows": rows,
        "ray_count": ray_count,
        "triangle_count": triangle_count,
        "max_rows": capacity,
        "row_count": 0 if overflow else len(rows),
        "attempted_row_count": len(candidate_rows),
        "overflow": overflow,
        "deduplicate_primitives": bool(deduplicate_primitives),
        "hit_event_count_before_dedup": hit_event_count,
        "rt_core_accelerated": False,
        "native_lowering_ready": False,
        "phase_timing_seconds": {
            "traversal": elapsed,
            "hit_stream_materialization": 0.0,
            "native_call": elapsed,
        },
        "claim_boundary": {
            "native_app_api": False,
            "raydb_semantics_embedded": False,
            "row_schema": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
            "fail_closed_overflow": True,
            "public_speedup_claim": False,
        },
    }


def run_generic_ray_triangle_hit_stream_device_columns_3d(
    rays: tuple[Ray3D, ...],
    triangles: tuple[Triangle3D, ...],
    *,
    max_rows: int | None = None,
    deduplicate_primitives: bool = True,
    backend: str = "optix",
):
    """Emit a generic 3-D ray/triangle hit stream as device columns.

    This is the experimental v2.5 native-device-column front door. It keeps the
    primitive generic and currently has only an OptiX implementation.
    """

    normalized_backend = _normalize_backend(backend)
    if normalized_backend != "optix":
        raise ValueError("device-column ray/triangle hit streams currently require backend='optix'")
    if max_rows is not None and int(max_rows) < 0:
        raise ValueError("max_rows must be non-negative")
    packed_rays_type, packed_triangles_type = _packed_runtime_types()
    rays_are_packed = packed_rays_type is not None and isinstance(rays, packed_rays_type)
    triangles_are_packed = packed_triangles_type is not None and isinstance(triangles, packed_triangles_type)
    if rays_are_packed:
        if rays.dimension != 3:
            raise TypeError("generic ray/triangle device-column hit stream requires 3-D rays")
    elif any(not isinstance(ray, Ray3D) for ray in rays):
        raise TypeError("generic ray/triangle device-column hit stream requires Ray3D inputs")
    if triangles_are_packed:
        if triangles.dimension != 3:
            raise TypeError("generic ray/triangle device-column hit stream requires 3-D triangles")
    elif any(not isinstance(triangle, Triangle3D) for triangle in triangles):
        raise TypeError("generic ray/triangle device-column hit stream requires Triangle3D inputs")

    from .optix_runtime import ray_triangle_hit_stream_device_columns_3d_optix

    return ray_triangle_hit_stream_device_columns_3d_optix(
        rays,
        triangles,
        max_rows=max_rows,
        deduplicate_primitives=deduplicate_primitives,
    )


def run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(
    rays: tuple[Ray3D, ...],
    triangles: tuple[Triangle3D, ...],
    *,
    group_count: int | None = None,
    max_rows: int | None = None,
    deduplicate_primitives: bool = False,
    backend: str = "optix",
    partner: str = "cupy",
    return_device_buffers: bool = False,
) -> dict[str, Any]:
    """Run generic RT hit-stream rows into an event-ordered grouped reduction.

    This is a v2.5 user-facing convenience front door over the generic OptiX
    hit-stream grouped-reduction consumer. It deliberately groups by the generic
    `ray_id` column and reduces the generic `primitive_id` column. App logic can
    interpret those ids outside the native engine.
    """

    normalized_backend = _normalize_backend(backend)
    if normalized_backend != "optix":
        raise ValueError("event-ordered hit-stream grouped reductions currently require backend='optix'")

    from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_PREVIEW
    from .v2_5_partner_support_matrix import plan_v2_5_partner_support

    operation = "hit_stream_grouped_ray_id_primitive_i64"
    support = plan_v2_5_partner_support(operation, partner)
    if support["partner"] != "cupy_conformance" or support["status"] != V2_5_SUPPORT_STATUS_PREVIEW:
        raise ValueError(
            "event-ordered hit-stream grouped reduction execution currently requires "
            "partner='cupy' or partner='cupy_conformance'; other partners fail closed "
            f"through the support matrix with status {support['status']!r}"
        )

    normalized_rays = _normalize_ray3d_sequence_for_front_door(rays)
    normalized_triangles = _normalize_triangle3d_sequence_for_front_door(triangles)
    resolved_group_count = (
        _infer_ray_id_group_count(normalized_rays) if group_count is None else int(group_count)
    )
    if resolved_group_count < 0:
        raise ValueError("group_count must be non-negative")
    if max_rows is None:
        max_rows = len(normalized_rays) * len(normalized_triangles)
    max_rows = int(max_rows)
    if max_rows < 0:
        raise ValueError("max_rows must be non-negative")

    from .optix_runtime import prepare_optix_static_triangle_scene_3d

    with prepare_optix_static_triangle_scene_3d(normalized_triangles) as scene:
        hit_buffers = scene.prepare_ray_triangle_hit_stream_device_column_buffers(max_rows)
        group_buffers = scene.prepare_ray_triangle_hit_stream_grouped_reduction_buffers(
            resolved_group_count
        )
        try:
            result = scene.ray_triangle_hit_stream_event_ordered_grouped_ray_id_reduction(
                normalized_rays,
                hit_buffers,
                group_buffers,
                max_rows=max_rows,
                deduplicate_primitives=deduplicate_primitives,
            )
            metadata = dict(result["metadata"])
            metadata.update(
                {
                    "front_door": (
                        "run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d"
                    ),
                    "operation": operation,
                    "requested_partner": str(partner),
                    "selected_partner": support["partner"],
                    "support_cell": support,
                    "backend": normalized_backend,
                    "grouping_key": "ray_id",
                    "reduced_value": "primitive_id",
                    "generic_user_facing_primitive": True,
                    "native_engine_app_specific_vocab_allowed": False,
                    "rt_traversal_replacement_allowed": False,
                    "return_device_buffers": bool(return_device_buffers),
                    "caller_must_close_returned_buffers": bool(return_device_buffers),
                    "public_speedup_claim_authorized": False,
                    "true_zero_copy_authorized": False,
                }
            )
            payload = {
                "summary": result["summary"],
                "metadata": metadata,
            }
            if return_device_buffers:
                payload["hit_buffers"] = hit_buffers
                payload["group_buffers"] = group_buffers
            else:
                group_buffers.close()
                hit_buffers.close()
            return payload
        except Exception:
            group_buffers.close()
            hit_buffers.close()
            raise


class GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D:
    """Prepared generic RT hit stream plus partner primitive-payload grouped sum."""

    contract = "GENERIC_PREPARED_RAY_TRIANGLE_EVENT_ORDERED_PAYLOAD_GROUPED_SUM_3D_V1"

    def __init__(
        self,
        triangles: Any,
        *,
        primitive_group_ids: Any,
        primitive_values: Any | None = None,
        group_count: int | None = None,
        backend: str = "optix",
        partner: str = "cupy",
        group_id_bounds_validation: str | None = None,
    ) -> None:
        normalized_backend = _normalize_backend(backend)
        if normalized_backend != "optix":
            raise ValueError("event-ordered primitive-payload grouped sums currently require backend='optix'")
        from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_PREVIEW
        from .v2_5_partner_support_matrix import plan_v2_5_partner_support

        self.operation = "hit_stream_primitive_payload_grouped_sum_f64"
        self.requested_partner = str(partner)
        self.support = plan_v2_5_partner_support(self.operation, partner)
        if self.support["partner"] != "cupy_conformance" or self.support["status"] != V2_5_SUPPORT_STATUS_PREVIEW:
            raise ValueError(
                "event-ordered primitive-payload grouped sum execution currently requires "
                "partner='cupy' or partner='cupy_conformance'; other partners fail closed "
                f"through the support matrix with status {self.support['status']!r}"
            )

        from .hit_stream_handoff import prepare_generic_typed_primitive_payload_columns
        from .optix_runtime import prepare_optix_static_triangle_scene_3d

        self.backend = normalized_backend
        self.triangles = _normalize_triangle3d_input_for_front_door(triangles)
        self.triangle_count = _front_door_record_count(self.triangles)
        self._scene_cm = None
        self._prepared_scene = None
        self._closed = False

        payload_prepare_start = time.perf_counter()
        self.payload_columns = prepare_generic_typed_primitive_payload_columns(
            primitive_group_ids,
            primitive_values,
            primitive_count=self.triangle_count,
            group_count=group_count,
            prefer_torch_cuda=True,
            require_torch_cuda=True,
            group_id_bounds_validation=group_id_bounds_validation,
        )
        self.payload_prepare_sec = time.perf_counter() - payload_prepare_start
        scene_prepare_start = time.perf_counter()
        self._scene_cm = prepare_optix_static_triangle_scene_3d(self.triangles)
        self._prepared_scene = self._scene_cm.__enter__()
        self.scene_prepare_sec = time.perf_counter() - scene_prepare_start

    @property
    def group_count(self) -> int:
        return int(self.payload_columns.group_count)

    def run(
        self,
        rays: Any,
        *,
        max_rows: int | None = None,
        deduplicate_primitives: bool = False,
        return_device_buffers: bool = False,
    ) -> dict[str, Any]:
        if self._closed or self._prepared_scene is None:
            raise RuntimeError("prepared event-ordered primitive-payload grouped sum is closed")
        normalized_rays = _normalize_ray3d_input_for_front_door(rays)
        ray_count = _front_door_record_count(normalized_rays)
        if max_rows is None:
            max_rows = ray_count * self.triangle_count
        max_rows = int(max_rows)
        if max_rows < 0:
            raise ValueError("max_rows must be non-negative")

        hit_buffers = self._prepared_scene.prepare_ray_triangle_hit_stream_device_column_buffers(max_rows)
        output_buffers = self._prepared_scene.prepare_ray_triangle_hit_stream_primitive_payload_grouped_sum_buffers(
            self.group_count
        )
        try:
            result = self._prepared_scene.ray_triangle_hit_stream_event_ordered_primitive_payload_grouped_sum(
                normalized_rays,
                hit_buffers,
                self.payload_columns,
                output_buffers,
                max_rows=max_rows,
                deduplicate_primitives=deduplicate_primitives,
            )
            group_hit_counts = [int(value) for value in output_buffers.group_hit_counts.detach().cpu().tolist()]
            group_payload_sums = [
                float(value) for value in output_buffers.group_payload_sums.detach().cpu().tolist()
            ]
            metadata = dict(result["metadata"])
            timings = dict(metadata.get("phase_timing_seconds", {}))
            timings["generic_scene_prepare"] = float(self.scene_prepare_sec)
            timings["generic_payload_prepare"] = float(self.payload_prepare_sec)
            metadata.update(
                {
                    "front_door": "prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d",
                    "operation": self.operation,
                    "requested_partner": self.requested_partner,
                    "selected_partner": self.support["partner"],
                    "support_cell": self.support,
                    "backend": self.backend,
                    "grouping_key": "primitive_group_ids[primitive_id]",
                    "reduced_value": "primitive_values[primitive_id]",
                    "generic_user_facing_primitive": True,
                    "native_engine_app_specific_vocab_allowed": False,
                    "rt_traversal_replacement_allowed": False,
                    "return_device_buffers": bool(return_device_buffers),
                    "caller_must_close_returned_buffers": bool(return_device_buffers),
                    "public_speedup_claim_authorized": False,
                    "true_zero_copy_authorized": False,
                    "phase_timing_seconds": timings,
                }
            )
            payload: dict[str, Any] = {
                "summary": result["summary"],
                "group_hit_counts": tuple(group_hit_counts),
                "group_payload_sums": tuple(group_payload_sums),
                "metadata": metadata,
            }
            if return_device_buffers:
                payload["hit_buffers"] = hit_buffers
                payload["output_buffers"] = output_buffers
            else:
                output_buffers.close()
                hit_buffers.close()
            return payload
        except Exception:
            output_buffers.close()
            hit_buffers.close()
            raise

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._scene_cm is not None:
            self._scene_cm.__exit__(None, None, None)
            self._scene_cm = None
            self._prepared_scene = None

    def __enter__(self) -> "GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
    triangles: Any,
    *,
    primitive_group_ids: Any,
    primitive_values: Any | None = None,
    group_count: int | None = None,
    backend: str = "optix",
    partner: str = "cupy",
    group_id_bounds_validation: str | None = None,
) -> GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D:
    """Prepare a generic RT hit-stream front door for partner payload sums."""
    return GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D(
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        group_count=group_count,
        backend=backend,
        partner=partner,
        group_id_bounds_validation=group_id_bounds_validation,
    )


def run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
    rays: Any,
    triangles: Any,
    *,
    primitive_group_ids: Any,
    primitive_values: Any | None = None,
    group_count: int | None = None,
    max_rows: int | None = None,
    deduplicate_primitives: bool = False,
    backend: str = "optix",
    partner: str = "cupy",
    return_device_buffers: bool = False,
    group_id_bounds_validation: str | None = None,
) -> dict[str, Any]:
    """Run generic RT hit rows into a partner primitive-payload grouped sum."""
    with prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        group_count=group_count,
        backend=backend,
        partner=partner,
        group_id_bounds_validation=group_id_bounds_validation,
    ) as prepared:
        return prepared.run(
            rays,
            max_rows=max_rows,
            deduplicate_primitives=deduplicate_primitives,
            return_device_buffers=return_device_buffers,
        )


def plan_v2_5_ray_triangle_payload_grouped_reduction_execution(
    *,
    reduction: str,
    requested_partner: str = "cupy",
    user_requires_event_ordered_hit_stream: bool = False,
    fused_generic_reduction_available: bool = True,
) -> dict[str, Any]:
    """Explain whether to use fused RTDL reduction or a partner hit stream.

    This helper is deliberately a planner/explain surface. It does not launch
    kernels and does not override the caller's explicit partner choice.
    """
    normalized_reduction = str(reduction).strip().lower()
    if normalized_reduction not in {"count", "sum", "min", "max", "sum_count"}:
        raise ValueError("reduction must be one of: count, sum, min, max, sum_count")
    from .v2_5_partner_support_matrix import plan_v2_5_partner_support

    operation = "hit_stream_primitive_payload_grouped_sum_f64"
    support = plan_v2_5_partner_support(operation, requested_partner)
    hit_stream_can_express = normalized_reduction in {"count", "sum", "sum_count"}
    if (
        fused_generic_reduction_available
        and not user_requires_event_ordered_hit_stream
    ):
        selected_path = "prepared_fused_generic_grouped_reduction"
        selected_operation = "generic_ray_triangle_primitive_grouped_i64_reduction_3d"
        reason = (
            "primitive-first: the requested reduction is exactly expressible by "
            "an app-agnostic fused RTDL primitive, so exposing a hit stream to a "
            "partner would add unnecessary continuation overhead"
        )
        partner_continuation_required = False
    elif not hit_stream_can_express:
        selected_path = "unsupported_hit_stream_payload_reduction"
        selected_operation = operation
        reason = (
            "the current payload-mapped event-ordered hit-stream front door only "
            "returns grouped hit counts and grouped payload sums"
        )
        partner_continuation_required = True
    else:
        selected_path = "event_ordered_payload_hit_stream_continuation"
        selected_operation = operation
        reason = (
            "caller explicitly requested an event-ordered hit stream or no fused "
            "generic reduction is available; use the bounded partner continuation "
            "with the requested partner support cell"
        )
        partner_continuation_required = True

    return {
        "planner_version": "rtdl.v2_5.ray_triangle_payload_grouped_reduction_execution_plan.v1",
        "reduction": normalized_reduction,
        "requested_partner": str(requested_partner),
        "selected_path": selected_path,
        "selected_operation": selected_operation,
        "partner_support": support,
        "partner_continuation_required": partner_continuation_required,
        "hit_stream_can_express_reduction": hit_stream_can_express,
        "fused_generic_reduction_available": bool(fused_generic_reduction_available),
        "user_requires_event_ordered_hit_stream": bool(user_requires_event_ordered_hit_stream),
        "typed_hit_stream_forced": bool(user_requires_event_ordered_hit_stream),
        "selection_reason": reason,
        "goal2950_pod_evidence_summary": (
            "RayDB count/sum pod evidence showed the payload hit-stream front door "
            "is correct but much slower than the fused primitive for reductions "
            "already covered by generic RTDL grouped reduction."
        ),
        "native_engine_app_specific_vocab_allowed": False,
        "rt_traversal_replacement_allowed": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
    }


def _is_packed_3d_records(value: Any) -> bool:
    return hasattr(value, "records") and hasattr(value, "count") and hasattr(value, "dimension")


def _front_door_record_count(value: Any) -> int:
    count = getattr(value, "count", None)
    if count is not None and not callable(count):
        return int(count)
    return len(value)


def _normalize_ray3d_input_for_front_door(rays: Any) -> Any:
    if _is_packed_3d_records(rays):
        if int(rays.dimension) != 3:
            raise TypeError("event-ordered hit-stream grouped reductions require 3-D rays")
        return rays
    return _normalize_ray3d_sequence_for_front_door(rays)


def _normalize_triangle3d_input_for_front_door(triangles: Any) -> Any:
    if _is_packed_3d_records(triangles):
        if int(triangles.dimension) != 3:
            raise TypeError("event-ordered hit-stream grouped reductions require 3-D triangles")
        return triangles
    return _normalize_triangle3d_sequence_for_front_door(triangles)


def _normalize_ray3d_sequence_for_front_door(rays: Any) -> tuple[Ray3D, ...]:
    if hasattr(rays, "records") and hasattr(rays, "count") and hasattr(rays, "dimension"):
        if int(rays.dimension) != 3:
            raise TypeError("event-ordered hit-stream grouped reductions require 3-D rays")
        return tuple(
            Ray3D(
                id=int(rays.records[index].id),
                ox=float(rays.records[index].ox),
                oy=float(rays.records[index].oy),
                oz=float(rays.records[index].oz),
                dx=float(rays.records[index].dx),
                dy=float(rays.records[index].dy),
                dz=float(rays.records[index].dz),
                tmax=float(rays.records[index].tmax),
            )
            for index in range(int(rays.count))
        )
    ray_tuple = tuple(rays)
    if any(not isinstance(ray, Ray3D) for ray in ray_tuple):
        raise TypeError("event-ordered hit-stream grouped reductions require Ray3D inputs")
    return ray_tuple


def _normalize_triangle3d_sequence_for_front_door(triangles: Any) -> tuple[Triangle3D, ...]:
    if hasattr(triangles, "records") and hasattr(triangles, "count") and hasattr(triangles, "dimension"):
        if int(triangles.dimension) != 3:
            raise TypeError("event-ordered hit-stream grouped reductions require 3-D triangles")
        return tuple(
            Triangle3D(
                id=int(triangles.records[index].id),
                x0=float(triangles.records[index].x0),
                y0=float(triangles.records[index].y0),
                z0=float(triangles.records[index].z0),
                x1=float(triangles.records[index].x1),
                y1=float(triangles.records[index].y1),
                z1=float(triangles.records[index].z1),
                x2=float(triangles.records[index].x2),
                y2=float(triangles.records[index].y2),
                z2=float(triangles.records[index].z2),
            )
            for index in range(int(triangles.count))
        )
    triangle_tuple = tuple(triangles)
    if any(not isinstance(triangle, Triangle3D) for triangle in triangle_tuple):
        raise TypeError("event-ordered hit-stream grouped reductions require Triangle3D inputs")
    return triangle_tuple


def _infer_ray_id_group_count(rays: tuple[Ray3D, ...]) -> int:
    if not rays:
        return 0
    max_id = max(int(ray.id) for ray in rays)
    if max_id < 0:
        raise ValueError("ray ids must be non-negative for grouped ray-id reduction")
    return max_id + 1


def run_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
    rays: tuple[Ray3D, ...],
    triangles: tuple[Triangle3D, ...],
    *,
    primitive_group_ids: tuple[int, ...],
    primitive_values: tuple[int, ...] | None = None,
    reduction: str = "sum",
    deduplicate_primitives: bool = True,
    backend: str = "cpu",
    include_hit_primitive_indices: bool = False,
) -> dict[str, Any]:
    """Run a generic all-hit primitive-id grouped i64 reduction contract.

    The engine-facing contract is deliberately app-name-free: all app semantics
    have already been lowered to rays, triangles, primitive group ids, and
    primitive integer payloads.
    """
    normalized_backend = _normalize_backend(backend)
    if normalized_backend not in {"cpu", "embree", "optix"}:
        raise ValueError("generic grouped ray/triangle i64 reduction backend must be one of: cpu, embree, optix")
    if reduction not in {"count", "sum", "min", "max", "sum_count"}:
        raise ValueError("reduction must be one of: count, sum, min, max, sum_count")
    packed_rays_type = None
    packed_triangles_type = None
    if normalized_backend in {"embree", "optix"}:
        from .embree_runtime import PackedRays as _PackedRays
        from .embree_runtime import PackedTriangles as _PackedTriangles

        packed_rays_type = _PackedRays
        packed_triangles_type = _PackedTriangles
    triangle_count = int(triangles.count) if packed_triangles_type is not None and isinstance(triangles, packed_triangles_type) else len(triangles)
    ray_count = int(rays.count) if packed_rays_type is not None and isinstance(rays, packed_rays_type) else len(rays)
    if len(primitive_group_ids) != triangle_count:
        raise ValueError("primitive_group_ids length must match triangles length")
    if primitive_values is None:
        primitive_values = tuple(1 for _ in range(triangle_count))
    if len(primitive_values) != triangle_count:
        raise ValueError("primitive_values length must match triangles length")
    if packed_rays_type is not None and isinstance(rays, packed_rays_type):
        if rays.dimension != 3:
            raise TypeError("generic grouped reduction 3D requires 3-D rays")
    elif any(not isinstance(ray, Ray3D) for ray in rays):
        raise TypeError("generic grouped reduction 3D requires Ray3D inputs")
    if packed_triangles_type is not None and isinstance(triangles, packed_triangles_type):
        if triangles.dimension != 3:
            raise TypeError("generic grouped reduction 3D requires 3-D triangles")
    elif any(not isinstance(triangle, Triangle3D) for triangle in triangles):
        raise TypeError("generic grouped reduction 3D requires Triangle3D inputs")
    if any(int(group_id) < 0 for group_id in primitive_group_ids):
        raise ValueError("primitive_group_ids must be non-negative")
    if normalized_backend == "embree":
        from .embree_runtime import ray_triangle_primitive_grouped_i64_reduction_3d_embree

        group_count = max((int(group_id) for group_id in primitive_group_ids), default=-1) + 1
        return ray_triangle_primitive_grouped_i64_reduction_3d_embree(
            rays,
            triangles,
            primitive_group_ids=primitive_group_ids,
            primitive_values=primitive_values,
            group_count=group_count,
            reduction=reduction,
        )
    if normalized_backend == "optix":
        from .optix_runtime import prepare_optix_static_triangle_scene_3d

        group_count = max((int(group_id) for group_id in primitive_group_ids), default=-1) + 1
        with prepare_optix_static_triangle_scene_3d(triangles) as prepared_scene:
            return prepared_scene.ray_triangle_primitive_grouped_i64_reduction(
                rays,
                primitive_group_ids=primitive_group_ids,
                primitive_values=primitive_values,
                group_count=group_count,
                reduction=reduction,
            )

    hit_event_count = 0
    hit_indices: list[int] = []
    seen_indices: set[int] = set()
    for ray in rays:
        for primitive_index, triangle in enumerate(triangles):
            if not _finite_ray_hits_triangle(ray, triangle):
                continue
            hit_event_count += 1
            if deduplicate_primitives:
                if primitive_index in seen_indices:
                    continue
                seen_indices.add(primitive_index)
            hit_indices.append(primitive_index)

    grouped_values: dict[int, list[int]] = {}
    for primitive_index in hit_indices:
        group_id = int(primitive_group_ids[primitive_index])
        grouped_values.setdefault(group_id, []).append(int(primitive_values[primitive_index]))

    rows: list[dict[str, int]] = []
    for group_id in sorted(grouped_values):
        values = grouped_values[group_id]
        row = {"group_id": group_id}
        if reduction == "count":
            row["count"] = len(values)
        elif reduction == "sum":
            row["sum"] = int(sum(values))
        elif reduction == "min":
            row["min"] = int(min(values))
        elif reduction == "max":
            row["max"] = int(max(values))
        else:
            row["sum"] = int(sum(values))
            row["count"] = len(values)
        rows.append(row)

    result: dict[str, Any] = {
        "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
        "backend": normalized_backend,
        "reduction": reduction,
        "deduplicate_primitives": bool(deduplicate_primitives),
        "ray_count": ray_count,
        "triangle_count": triangle_count,
        "hit_event_count_before_dedup": hit_event_count,
        "deduplicated_primitive_hit_count": len(set(hit_indices)) if deduplicate_primitives else len(hit_indices),
        "rows": tuple(rows),
        "rt_core_accelerated": False,
        "native_lowering_ready": False,
        "claim_boundary": (
            "CPU reference for generic all-hit ray/triangle primitive-id grouped "
            "i64 reduction. App semantics must be expressed before this primitive; "
            "no native RT-core performance claim is authorized."
        ),
    }
    if include_hit_primitive_indices:
        result["hit_primitive_indices"] = tuple(sorted(set(hit_indices)) if deduplicate_primitives else hit_indices)
    return result


class GenericPreparedRayTrianglePrimitiveGroupedI64Reduction3D:
    """App-name-free prepared scene plus device-resident primitive grouped payload."""

    contract = "GENERIC_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_V1"

    def __init__(
        self,
        triangles,
        *,
        primitive_group_ids,
        primitive_values=None,
        group_count: int | None = None,
        backend: str = "optix",
    ) -> None:
        normalized_backend = _normalize_backend(backend)
        if normalized_backend not in {"embree", "optix"}:
            raise ValueError("prepared generic primitive grouped i64 reduction supports backend='embree' or 'optix'")
        from .embree_runtime import PackedTriangles as _PackedTriangles

        self.backend = normalized_backend
        self._scene_cm = None
        self._payload_cm = None
        self._prepared_scene = None
        self._prepared_payload = None
        triangle_count = int(triangles.count) if isinstance(triangles, _PackedTriangles) else len(triangles)
        if len(primitive_group_ids) != triangle_count:
            raise ValueError("primitive_group_ids length must match triangles length")
        if primitive_values is None:
            primitive_values = tuple(1 for _ in range(triangle_count))
        if len(primitive_values) != triangle_count:
            raise ValueError("primitive_values length must match triangles length")
        if group_count is None:
            inferred_group_count = max((int(group_id) for group_id in primitive_group_ids), default=-1) + 1
            group_count = inferred_group_count
        if int(group_count) < 0:
            raise ValueError("group_count must be non-negative")

        self.triangle_count = triangle_count
        self.group_count = int(group_count)
        scene_prepare_start = time.perf_counter()
        if normalized_backend == "optix":
            from .optix_runtime import prepare_optix_primitive_grouped_i64_payload_3d
            from .optix_runtime import prepare_optix_static_triangle_scene_3d

            self._scene_cm = prepare_optix_static_triangle_scene_3d(triangles)
        else:
            from .embree_runtime import prepare_embree_static_triangle_scene_3d

            self._scene_cm = prepare_embree_static_triangle_scene_3d(triangles)
        self._prepared_scene = self._scene_cm.__enter__()
        self.scene_prepare_sec = time.perf_counter() - scene_prepare_start
        payload_prepare_start = time.perf_counter()
        if normalized_backend == "optix":
            self._payload_cm = prepare_optix_primitive_grouped_i64_payload_3d(
                primitive_group_ids,
                primitive_values,
                primitive_count=triangle_count,
                group_count=self.group_count,
            )
            self._prepared_payload = self._payload_cm.__enter__()
        else:
            self._prepared_payload = self._prepared_scene.prepare_primitive_grouped_i64_payload(
                primitive_group_ids,
                primitive_values,
                group_count=self.group_count,
            )
        self.payload_prepare_sec = time.perf_counter() - payload_prepare_start

    def run(self, rays, *, reduction: str) -> dict[str, Any]:
        if self._prepared_scene is None or self._prepared_payload is None:
            raise RuntimeError("prepared generic primitive grouped i64 reduction scene is closed")
        result = self._prepared_scene.ray_triangle_prepared_primitive_grouped_i64_reduction(
            rays,
            self._prepared_payload,
            reduction=reduction,
        )
        timings = dict(result.get("phase_timing_seconds", {}))
        timings["generic_scene_prepare"] = float(self.scene_prepare_sec)
        timings["generic_payload_prepare"] = float(self.payload_prepare_sec)
        return {
            **result,
            "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "prepared_generic_payload_used": True,
            "backend": self.backend,
            "phase_timing_seconds": timings,
        }

    def prepare_ray_batch(self, rays):
        if self._prepared_scene is None:
            raise RuntimeError("prepared generic primitive grouped i64 reduction scene is closed")
        return self._prepared_scene.prepare_ray_batch(rays)

    def prepare_ray_batch_device_columns(self, ray_columns: dict):
        if self._prepared_scene is None:
            raise RuntimeError("prepared generic primitive grouped i64 reduction scene is closed")
        if not hasattr(self._prepared_scene, "prepare_ray_batch_device_columns"):
            raise RuntimeError("prepared ray batch device-column creation is not available for this backend")
        return self._prepared_scene.prepare_ray_batch_device_columns(ray_columns)

    def run_prepared_rays(self, prepared_rays, *, reduction: str) -> dict[str, Any]:
        if self._prepared_scene is None or self._prepared_payload is None:
            raise RuntimeError("prepared generic primitive grouped i64 reduction scene is closed")
        if not hasattr(self._prepared_scene, "ray_batch_prepared_primitive_grouped_i64_reduction"):
            raise RuntimeError("prepared ray-batch grouped i64 reduction is not available for this backend")
        result = self._prepared_scene.ray_batch_prepared_primitive_grouped_i64_reduction(
            prepared_rays,
            self._prepared_payload,
            reduction=reduction,
        )
        timings = dict(result.get("phase_timing_seconds", {}))
        timings["generic_scene_prepare"] = float(self.scene_prepare_sec)
        timings["generic_payload_prepare"] = float(self.payload_prepare_sec)
        return {
            **result,
            "primitive": "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D",
            "prepared_generic_payload_used": True,
            "prepared_generic_ray_batch_used": True,
            "backend": self.backend,
            "phase_timing_seconds": timings,
        }

    def close(self) -> None:
        if self._payload_cm is not None:
            self._payload_cm.__exit__(None, None, None)
            self._payload_cm = None
        self._prepared_payload = None
        if self._scene_cm is not None:
            self._scene_cm.__exit__(None, None, None)
            self._scene_cm = None
            self._prepared_scene = None

    def __enter__(self) -> "GenericPreparedRayTrianglePrimitiveGroupedI64Reduction3D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
    triangles,
    *,
    primitive_group_ids,
    primitive_values=None,
    group_count: int | None = None,
    backend: str = "optix",
) -> GenericPreparedRayTrianglePrimitiveGroupedI64Reduction3D:
    """Prepare a reusable generic 3-D ray/triangle grouped i64 reduction scene."""
    return GenericPreparedRayTrianglePrimitiveGroupedI64Reduction3D(
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        group_count=group_count,
        backend=backend,
    )


def run_generic_fixed_radius_count_threshold_2d(
    query_points: Any,
    search_points: Any | None = None,
    *,
    radius: float,
    threshold: int = 0,
    backend: str = "cpu",
) -> dict[str, Any]:
    """Run app-name-free 2-D fixed-radius counts with optional threshold flags."""
    normalized_backend = _validate_fixed_radius_count_backend(backend)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    if search_points is None:
        search_points = query_points

    query_start = time.perf_counter()
    if normalized_backend == "cpu":
        rows = _cpu_fixed_radius_count_threshold_rows(
            query_points,
            search_points,
            radius=radius,
            threshold=threshold,
        )
    elif normalized_backend == "embree":
        from .embree_runtime import fixed_radius_count_threshold_2d_embree

        rows = fixed_radius_count_threshold_2d_embree(
            query_points,
            search_points,
            radius=radius,
            threshold=threshold,
        )
    else:
        from .optix_runtime import fixed_radius_count_threshold_2d_optix

        rows = fixed_radius_count_threshold_2d_optix(
            query_points,
            search_points,
            radius=radius,
            threshold=threshold,
        )
    query_sec = time.perf_counter() - query_start
    scalar_summary = _threshold_reached_scalar_summary(rows)
    return {
        "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
        "summary_primitive": "REDUCE_INT(COUNT)",
        "backend": normalized_backend,
        "active_v1_5_backend": normalized_backend in {"embree", "optix"},
        "radius": float(radius),
        "threshold": int(threshold),
        "row_count": len(rows),
        "threshold_reached_count": scalar_summary["result"],
        "rows": rows,
        "scalar_reduction": _scalar_reduction_metadata(scalar_summary),
        "run_phases": {
            "query_fixed_radius_count_threshold_sec": query_sec,
        },
        "claim_boundary": (
            "Generic v1.5 2-D fixed-radius count-threshold primitive only; "
            "not app-specific ANN, DBSCAN, coverage, Hausdorff, Barnes-Hut, or public speedup wording."
        ),
    }


class GenericPreparedRayTriangleAnyHitScene:
    """App-name-free prepared scene for amortized `ANY_HIT` plus `COUNT_HITS` queries."""

    def __init__(
        self,
        *,
        triangles: Any,
        backend: str = "optix",
        prepare_scene=None,
        prepare_rays=None,
    ) -> None:
        self.backend = _validate_prepared_anyhit_count_backend(backend)
        if prepare_scene is None:
            from .optix_runtime import prepare_optix_ray_triangle_any_hit_2d as prepare_scene
        if prepare_rays is None:
            from .optix_runtime import prepare_optix_rays_2d as prepare_rays

        self._prepare_rays = prepare_rays
        self._scene_cm = None
        self._prepared_scene = None
        self._closed = False
        self.query_batch_count = 0

        scene_prepare_start = time.perf_counter()
        self._scene_cm = prepare_scene(triangles)
        self._prepared_scene = self._scene_cm.__enter__()
        self.scene_prepare_sec = time.perf_counter() - scene_prepare_start

    def count(
        self,
        rays: Any,
        *,
        query_repeats: int = 1,
        prepare_rays=None,
    ) -> dict[str, Any]:
        """Count ray any-hit results against the already prepared scene."""
        if self._closed:
            raise RuntimeError("generic prepared ray/triangle scene is closed")
        if query_repeats <= 0:
            raise ValueError("query_repeats must be positive")
        if prepare_rays is None:
            prepare_rays = self._prepare_rays

        ray_prepare_start = time.perf_counter()
        with prepare_rays(rays) as prepared_rays:
            ray_prepare_sec = time.perf_counter() - ray_prepare_start
            query_times = []
            hit_count = 0
            for _ in range(query_repeats):
                query_start = time.perf_counter()
                hit_count = int(self._prepared_scene.count(prepared_rays))
                query_times.append(time.perf_counter() - query_start)
            query_sec = sum(query_times)

        self.query_batch_count += 1
        return {
            "primitive": "ANY_HIT",
            "summary_primitive": "COUNT_HITS",
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "query_batch_index": self.query_batch_count,
            "query_repeats": query_repeats,
            "hit_count": hit_count,
            "run_phases": {
                "scene_prepare_sec": self.scene_prepare_sec,
                "scene_prepare_sec_this_batch": 0.0,
                "ray_prepare_sec": ray_prepare_sec,
                "query_anyhit_count_sec": query_sec,
                "query_anyhit_count_first_sec": float(query_times[0]) if query_times else 0.0,
                "query_anyhit_count_mean_sec": float(query_sec / len(query_times)) if query_times else 0.0,
                "query_anyhit_count_min_sec": float(min(query_times)) if query_times else 0.0,
            },
            "claim_boundary": (
                "Generic v1.5 reusable prepared raw ray/triangle ANY_HIT plus COUNT_HITS only; "
                "currently OptiX-focused and not public speedup wording."
            ),
        }

    def grouped_count_threshold_bool(
        self,
        rays: Any,
        group_indices: Any,
        *,
        group_count: int,
        threshold: int = 1,
        query_repeats: int = 1,
        prepare_rays=None,
        prepare_group_indices=None,
    ) -> dict[str, Any]:
        """Return grouped boolean flags as `REDUCE_INT(COUNT)` threshold output."""
        if self._closed:
            raise RuntimeError("generic prepared ray/triangle scene is closed")
        if group_count < 0:
            raise ValueError("group_count must be non-negative")
        if threshold != 1:
            raise ValueError("grouped_count_threshold_bool currently supports threshold=1")
        if query_repeats <= 0:
            raise ValueError("query_repeats must be positive")
        if prepare_rays is None:
            prepare_rays = self._prepare_rays
        if prepare_group_indices is None and self.backend == "optix":
            from .optix_runtime import prepare_optix_group_indices_2d as prepare_group_indices

        normalized_group_indices = tuple(int(index) for index in group_indices)
        if any(index < 0 or index >= group_count for index in normalized_group_indices):
            raise ValueError("group_indices entries must be within [0, group_count)")

        ray_prepare_start = time.perf_counter()
        group_prepare_sec = 0.0
        with prepare_rays(rays) as prepared_rays:
            ray_prepare_sec = time.perf_counter() - ray_prepare_start
            query_times = []
            group_flags: tuple[bool, ...] = tuple(False for _ in range(group_count))

            if prepare_group_indices is not None and hasattr(self._prepared_scene, "group_flags_prepared_indices"):
                group_prepare_start = time.perf_counter()
                with prepare_group_indices(normalized_group_indices) as prepared_group_indices:
                    group_prepare_sec = time.perf_counter() - group_prepare_start
                    for _ in range(query_repeats):
                        query_start = time.perf_counter()
                        group_flags = tuple(
                            bool(flag)
                            for flag in self._prepared_scene.group_flags_prepared_indices(
                                prepared_rays,
                                prepared_group_indices,
                                group_count=group_count,
                            )
                        )
                        query_times.append(time.perf_counter() - query_start)
            else:
                for _ in range(query_repeats):
                    query_start = time.perf_counter()
                    group_flags = tuple(
                        bool(flag)
                        for flag in self._prepared_scene.group_flags_packed(
                            prepared_rays,
                            normalized_group_indices,
                            group_count=group_count,
                        )
                    )
                    query_times.append(time.perf_counter() - query_start)

        query_sec = sum(query_times)
        scalar_summary = run_generic_scalar_reduction(
            tuple({"threshold_reached": int(flag)} for flag in group_flags if flag),
            summary_primitive="REDUCE_INT(COUNT)",
        )
        self.query_batch_count += 1
        return {
            "primitive": "ANY_HIT",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "result_layout": V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT,
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "query_batch_index": self.query_batch_count,
            "query_repeats": query_repeats,
            "group_count": int(group_count),
            "threshold": int(threshold),
            "group_flags": group_flags,
            "threshold_reached_count": scalar_summary["result"],
            "scalar_reduction": _scalar_reduction_metadata(scalar_summary),
            "run_phases": {
                "scene_prepare_sec": self.scene_prepare_sec,
                "scene_prepare_sec_this_batch": 0.0,
                "ray_prepare_sec": ray_prepare_sec,
                "group_index_prepare_sec": group_prepare_sec,
                "query_grouped_count_threshold_bool_sec": query_sec,
                "query_grouped_count_threshold_bool_first_sec": float(query_times[0]) if query_times else 0.0,
                "query_grouped_count_threshold_bool_mean_sec": (
                    float(query_sec / len(query_times)) if query_times else 0.0
                ),
                "query_grouped_count_threshold_bool_min_sec": float(min(query_times)) if query_times else 0.0,
            },
            "claim_boundary": (
                "Generic v1.5 reusable prepared raw ray/triangle ANY_HIT plus grouped "
                "REDUCE_INT(COUNT) threshold-bool result layout only; not whole-app collision planning "
                "or public speedup wording."
            ),
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._scene_cm is not None:
            self._scene_cm.__exit__(None, None, None)

    def __enter__(self) -> "GenericPreparedRayTriangleAnyHitScene":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


class GenericPreparedFixedRadiusCountThreshold2D:
    """App-name-free prepared 2-D fixed-radius threshold-count scene."""

    def __init__(
        self,
        *,
        search_points: Any,
        backend: str = "optix",
        max_radius: float | None = None,
        prepare_scene=None,
    ) -> None:
        self.backend = _validate_prepared_fixed_radius_count_backend(backend)
        if max_radius is not None and max_radius < 0:
            raise ValueError("max_radius must be non-negative")
        if prepare_scene is None:
            if self.backend == "embree":
                from .embree_runtime import prepare_embree_fixed_radius_count_threshold_2d as prepare_scene
            else:
                from .optix_runtime import prepare_optix_fixed_radius_count_threshold_2d as prepare_scene

        self._scene_cm = None
        self._prepared_scene = None
        self._closed = False
        self.query_batch_count = 0

        scene_prepare_start = time.perf_counter()
        if self.backend == "optix":
            if max_radius is None:
                raise ValueError("max_radius is required for prepared generic fixed_radius_count_threshold optix")
            self._scene_cm = prepare_scene(search_points, max_radius=max_radius)
        else:
            self._scene_cm = prepare_scene(search_points)
        self._prepared_scene = self._scene_cm.__enter__()
        self.scene_prepare_sec = time.perf_counter() - scene_prepare_start

    def run(
        self,
        query_points: Any,
        *,
        radius: float,
        threshold: int = 0,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("generic prepared fixed-radius count-threshold scene is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        query_start = time.perf_counter()
        rows = self._prepared_scene.run(query_points, radius=radius, threshold=threshold)
        query_sec = time.perf_counter() - query_start
        self.query_batch_count += 1
        scalar_summary = _threshold_reached_scalar_summary(rows)
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "query_batch_index": self.query_batch_count,
            "radius": float(radius),
            "threshold": int(threshold),
            "row_count": len(rows),
            "threshold_reached_count": scalar_summary["result"],
            "rows": rows,
            "scalar_reduction": _scalar_reduction_metadata(scalar_summary),
            "run_phases": {
                "scene_prepare_sec": self.scene_prepare_sec,
                "scene_prepare_sec_this_batch": 0.0,
                "query_fixed_radius_count_threshold_sec": query_sec,
            },
            "claim_boundary": (
                "Generic v1.5 reusable prepared 2-D fixed-radius count-threshold primitive only; "
                "not app-specific ANN, DBSCAN, coverage, Hausdorff, Barnes-Hut, or public speedup wording."
            ),
        }

    def count_threshold_reached(
        self,
        query_points: Any,
        *,
        radius: float,
        threshold: int,
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("generic prepared fixed-radius count-threshold scene is closed")
        if radius < 0:
            raise ValueError("radius must be non-negative")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        query_start = time.perf_counter()
        if hasattr(self._prepared_scene, "count_threshold_reached"):
            threshold_reached_count = int(
                self._prepared_scene.count_threshold_reached(query_points, radius=radius, threshold=threshold)
            )
            scalar_summary = None
        else:
            rows = self._prepared_scene.run(query_points, radius=radius, threshold=threshold)
            scalar_summary = _threshold_reached_scalar_summary(rows)
            threshold_reached_count = scalar_summary["result"]
        query_sec = time.perf_counter() - query_start
        self.query_batch_count += 1
        result = {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "query_batch_index": self.query_batch_count,
            "radius": float(radius),
            "threshold": int(threshold),
            "threshold_reached_count": threshold_reached_count,
            "result_layout": "aggregate_threshold_reached_count",
            "run_phases": {
                "scene_prepare_sec": self.scene_prepare_sec,
                "scene_prepare_sec_this_batch": 0.0,
                "query_fixed_radius_threshold_reached_count_sec": query_sec,
            },
            "claim_boundary": (
                "Generic v1.5 reusable prepared scalar threshold-reached count only; "
                "not app-specific ANN, DBSCAN, coverage, Hausdorff, Barnes-Hut, or public speedup wording."
            ),
        }
        if scalar_summary is not None:
            result["scalar_reduction"] = _scalar_reduction_metadata(scalar_summary)
        return result

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._scene_cm is not None:
            self._scene_cm.__exit__(None, None, None)

    def __enter__(self) -> "GenericPreparedFixedRadiusCountThreshold2D":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_generic_fixed_radius_count_threshold_2d(
    *,
    search_points: Any,
    backend: str = "optix",
    max_radius: float | None = None,
    prepare_scene=None,
) -> GenericPreparedFixedRadiusCountThreshold2D:
    """Prepare an app-name-free reusable 2-D fixed-radius threshold-count scene."""
    return GenericPreparedFixedRadiusCountThreshold2D(
        search_points=search_points,
        backend=backend,
        max_radius=max_radius,
        prepare_scene=prepare_scene,
    )


def run_generic_prepared_fixed_radius_threshold_reached_count_2d(
    *,
    search_points: Any,
    query_points: Any,
    radius: float,
    threshold: int,
    backend: str = "optix",
    max_radius: float | None = None,
    prepare_scene=None,
) -> dict[str, Any]:
    """Run prepared fixed-radius threshold-reached scalar count once."""
    with prepare_generic_fixed_radius_count_threshold_2d(
        search_points=search_points,
        backend=backend,
        max_radius=max_radius,
        prepare_scene=prepare_scene,
    ) as prepared_scene:
        return prepared_scene.count_threshold_reached(query_points, radius=radius, threshold=threshold)


def prepare_generic_ray_triangle_any_hit_scene(
    *,
    triangles: Any,
    backend: str = "optix",
    prepare_scene=None,
    prepare_rays=None,
) -> GenericPreparedRayTriangleAnyHitScene:
    """Prepare an app-name-free reusable ray/triangle `ANY_HIT` scene."""
    return GenericPreparedRayTriangleAnyHitScene(
        triangles=triangles,
        backend=backend,
        prepare_scene=prepare_scene,
        prepare_rays=prepare_rays,
    )


def run_generic_prepared_ray_triangle_any_hit_count(
    *,
    triangles: Any,
    rays: Any,
    backend: str = "optix",
    query_repeats: int = 1,
    prepare_scene=None,
    prepare_rays=None,
) -> dict[str, Any]:
    """Run prepared app-name-free `ANY_HIT` plus `COUNT_HITS` for repeated probes."""
    if query_repeats <= 0:
        raise ValueError("query_repeats must be positive")
    with prepare_generic_ray_triangle_any_hit_scene(
        triangles=triangles,
        backend=backend,
        prepare_scene=prepare_scene,
        prepare_rays=prepare_rays,
    ) as prepared_scene:
        return prepared_scene.count(
            rays,
            query_repeats=query_repeats,
            prepare_rays=prepare_rays,
        )


def run_generic_prepared_ray_triangle_any_hit_grouped_count_threshold_bool(
    *,
    triangles: Any,
    rays: Any,
    group_indices: Any,
    group_count: int,
    backend: str = "optix",
    threshold: int = 1,
    query_repeats: int = 1,
    prepare_scene=None,
    prepare_rays=None,
    prepare_group_indices=None,
) -> dict[str, Any]:
    """Run prepared `ANY_HIT` with grouped `REDUCE_INT(COUNT)` bool output."""
    if query_repeats <= 0:
        raise ValueError("query_repeats must be positive")
    with prepare_generic_ray_triangle_any_hit_scene(
        triangles=triangles,
        backend=backend,
        prepare_scene=prepare_scene,
        prepare_rays=prepare_rays,
    ) as prepared_scene:
        return prepared_scene.grouped_count_threshold_bool(
            rays,
            group_indices,
            group_count=group_count,
            threshold=threshold,
            query_repeats=query_repeats,
            prepare_rays=prepare_rays,
            prepare_group_indices=prepare_group_indices,
        )
