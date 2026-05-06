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
from .reference import Ray2D
from .reference import Ray3D
from .reference import Triangle
from .reference import Triangle3D
from .reference import _triangle_dimension
from .reference import ray_triangle_any_hit_cpu
from .reduction_runtime import run_generic_scalar_reduction


ACTIVE_V1_5_GENERIC_PRIMITIVE_BACKENDS = ("cpu", "embree", "optix")
FROZEN_BEFORE_V2_1_GENERIC_BACKENDS = ("vulkan", "hiprt", "apple_rt")


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


def _normalize_backend(backend: str) -> str:
    normalized = backend.lower().replace("-", "_")
    aliases = {
        "python": "cpu",
        "cpu_python_reference": "cpu",
        "apple": "apple_rt",
        "metal": "apple_rt",
    }
    return aliases.get(normalized, normalized)


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
        "scalar_reduction": {
            key: value
            for key, value in scalar_summary.items()
            if key not in {"result", "row_count"}
        },
        "claim_boundary": (
            "Generic v1.5 raw ray/triangle ANY_HIT plus COUNT_HITS only; "
            "no app-specific visibility, graph, DB, polygon, or public speedup claim."
        ),
    }
    if include_rows:
        result["rows"] = rows
    return result


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
        "scalar_reduction": {
            key: value
            for key, value in scalar_summary.items()
            if key not in {"result", "row_count"}
        },
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
            from .optix_runtime import prepare_optix_pose_indices_2d as prepare_group_indices

        normalized_group_indices = tuple(int(index) for index in group_indices)
        if any(index < 0 or index >= group_count for index in normalized_group_indices):
            raise ValueError("group_indices entries must be within [0, group_count)")

        ray_prepare_start = time.perf_counter()
        group_prepare_sec = 0.0
        with prepare_rays(rays) as prepared_rays:
            ray_prepare_sec = time.perf_counter() - ray_prepare_start
            query_times = []
            group_flags: tuple[bool, ...] = tuple(False for _ in range(group_count))

            if prepare_group_indices is not None and hasattr(self._prepared_scene, "pose_flags_prepared_indices"):
                group_prepare_start = time.perf_counter()
                with prepare_group_indices(normalized_group_indices) as prepared_group_indices:
                    group_prepare_sec = time.perf_counter() - group_prepare_start
                    for _ in range(query_repeats):
                        query_start = time.perf_counter()
                        group_flags = tuple(
                            bool(flag)
                            for flag in self._prepared_scene.pose_flags_prepared_indices(
                                prepared_rays,
                                prepared_group_indices,
                                pose_count=group_count,
                            )
                        )
                        query_times.append(time.perf_counter() - query_start)
            else:
                for _ in range(query_repeats):
                    query_start = time.perf_counter()
                    group_flags = tuple(
                        bool(flag)
                        for flag in self._prepared_scene.pose_flags_packed(
                            prepared_rays,
                            normalized_group_indices,
                            pose_count=group_count,
                        )
                    )
                    query_times.append(time.perf_counter() - query_start)

        query_sec = sum(query_times)
        threshold_reached_count = sum(1 for flag in group_flags if flag)
        self.query_batch_count += 1
        return {
            "primitive": "ANY_HIT",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "result_layout": "grouped_threshold_bool",
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "query_batch_index": self.query_batch_count,
            "query_repeats": query_repeats,
            "group_count": int(group_count),
            "threshold": int(threshold),
            "group_flags": group_flags,
            "threshold_reached_count": threshold_reached_count,
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
            "scalar_reduction": {
                key: value
                for key, value in scalar_summary.items()
                if key not in {"result", "row_count"}
            },
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
        else:
            rows = self._prepared_scene.run(query_points, radius=radius, threshold=threshold)
            threshold_reached_count = sum(int(row["threshold_reached"]) for row in rows)
        query_sec = time.perf_counter() - query_start
        self.query_batch_count += 1
        return {
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
