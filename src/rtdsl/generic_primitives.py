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
    hit_count = sum(int(row["any_hit"]) for row in rows)
    result: dict[str, Any] = {
        "primitive": "ANY_HIT",
        "summary_primitive": "COUNT_HITS",
        "backend": normalized_backend,
        "active_v1_5_backend": normalized_backend in {"embree", "optix"},
        "row_count": len(rows),
        "hit_count": hit_count,
        "result_layout": "aggregate_any_hit_count",
        "claim_boundary": (
            "Generic v1.5 raw ray/triangle ANY_HIT plus COUNT_HITS only; "
            "no app-specific visibility, graph, DB, polygon, or public speedup claim."
        ),
    }
    if include_rows:
        result["rows"] = rows
    return result


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
    normalized_backend = _normalize_backend(backend)
    if normalized_backend in FROZEN_BEFORE_V2_1_GENERIC_BACKENDS:
        raise ValueError(
            f"{normalized_backend} is frozen before v2.1; v1.5 prepared generic primitives are OptiX-focused"
        )
    if normalized_backend != "optix":
        raise ValueError("prepared generic ray_triangle_any_hit_count currently supports backend='optix'")
    if query_repeats <= 0:
        raise ValueError("query_repeats must be positive")

    if prepare_scene is None:
        from .optix_runtime import prepare_optix_ray_triangle_any_hit_2d as prepare_scene
    if prepare_rays is None:
        from .optix_runtime import prepare_optix_rays_2d as prepare_rays

    scene_prepare_start = time.perf_counter()
    with prepare_scene(triangles) as prepared_scene:
        scene_prepare_sec = time.perf_counter() - scene_prepare_start
        ray_prepare_start = time.perf_counter()
        with prepare_rays(rays) as prepared_rays:
            ray_prepare_sec = time.perf_counter() - ray_prepare_start
            query_times = []
            hit_count = 0
            for _ in range(query_repeats):
                query_start = time.perf_counter()
                hit_count = int(prepared_scene.count(prepared_rays))
                query_times.append(time.perf_counter() - query_start)
            query_sec = sum(query_times)

    return {
        "primitive": "ANY_HIT",
        "summary_primitive": "COUNT_HITS",
        "backend": normalized_backend,
        "prepared": True,
        "query_repeats": query_repeats,
        "hit_count": hit_count,
        "run_phases": {
            "scene_prepare_sec": scene_prepare_sec,
            "ray_prepare_sec": ray_prepare_sec,
            "query_anyhit_count_sec": query_sec,
            "query_anyhit_count_first_sec": float(query_times[0]) if query_times else 0.0,
            "query_anyhit_count_mean_sec": float(query_sec / len(query_times)) if query_times else 0.0,
            "query_anyhit_count_min_sec": float(min(query_times)) if query_times else 0.0,
        },
        "claim_boundary": (
            "Generic v1.5 prepared raw ray/triangle ANY_HIT plus COUNT_HITS only; "
            "currently OptiX-focused and not public speedup wording."
        ),
    }
