from __future__ import annotations

from . import api as rt
from .layout_types import Ray2DLayout
from .layout_types import Ray3DLayout
from .layout_types import Rays
from .layout_types import Rays3D
from .layout_types import Triangle2DLayout
from .layout_types import Triangle3DLayout
from .layout_types import Triangles
from .layout_types import Triangles3D
from .reference import Point
from .reference import Point3D
from .reference import Ray3D
from .reference import Triangle
from .reference import Triangle3D
from .reference import visibility_ray_pairs
from .reference import visibility_rows_cpu
from .reference import visibility_rows_from_any_hit


@rt.kernel(backend="rtdl", precision="float_approx")
def _visibility_any_hit_2d_kernel():
    rays = rt.input("rays", Rays, layout=Ray2DLayout, role="probe")
    triangles = rt.input("triangles", Triangles, layout=Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _visibility_any_hit_3d_kernel():
    rays = rt.input("rays", Rays3D, layout=Ray3DLayout, role="probe")
    triangles = rt.input("triangles", Triangles3D, layout=Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def visibility_rows(
    observers: tuple[Point | Point3D, ...],
    targets: tuple[Point | Point3D, ...],
    blockers: tuple[Triangle | Triangle3D, ...],
    *,
    backend: str = "cpu",
    native_only: bool = False,
) -> tuple[dict[str, int], ...]:
    """Return visibility rows using CPU or a real RTDL backend any-hit path.

    OptiX, Embree, and HIPRT use native ray-triangle any-hit dispatch when the
    loaded backend libraries export it. Other non-CPU backends currently
    execute through compatibility dispatch, proving backend execution and row
    parity but not native early-exit performance.
    """
    normalized_backend = backend.lower().replace("-", "_")
    if normalized_backend in {"cpu", "cpu_python_reference", "python"}:
        return visibility_rows_cpu(observers, targets, blockers)

    rays, ray_pairs = visibility_ray_pairs(observers, targets, blockers)
    if not rays:
        return ()
    kernel = _visibility_any_hit_3d_kernel if isinstance(rays[0], Ray3D) else _visibility_any_hit_2d_kernel
    inputs = {"rays": rays, "triangles": blockers}

    if normalized_backend == "embree":
        from .embree_runtime import run_embree

        any_hit_rows = run_embree(kernel, **inputs)
    elif normalized_backend == "optix":
        from .optix_runtime import run_optix

        any_hit_rows = run_optix(kernel, **inputs)
    elif normalized_backend == "vulkan":
        from .vulkan_runtime import run_vulkan

        any_hit_rows = run_vulkan(kernel, **inputs)
    elif normalized_backend == "hiprt":
        from .hiprt_runtime import run_hiprt

        any_hit_rows = run_hiprt(kernel, **inputs)
    elif normalized_backend in {"apple", "apple_rt", "metal"}:
        from .apple_rt_runtime import run_apple_rt

        any_hit_rows = run_apple_rt(kernel, native_only=native_only, **inputs)
    else:
        raise ValueError(
            "visibility_rows backend must be one of: cpu, embree, optix, vulkan, hiprt, apple_rt"
        )

    any_hit_by_ray = {int(row["ray_id"]): int(row["any_hit"]) for row in any_hit_rows}
    return visibility_rows_from_any_hit(ray_pairs, any_hit_by_ray)
