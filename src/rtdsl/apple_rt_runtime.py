"""Apple Metal/MPS ray-intersection backend for RTDL.

The v0.9.1 surface starts with a bounded 3D ray/triangle closest-hit
primitive backed by MPSRayIntersector. It intentionally does not claim parity
with the Linux GPU backends yet.
"""

from __future__ import annotations

import ctypes
import os
import platform
from pathlib import Path

from .ir import CompiledKernel
from .reference import Ray3D as _CanonicalRay3D
from .reference import Triangle3D as _CanonicalTriangle3D
from .runtime import _normalize_records
from .runtime import _run_cpu_python_reference_from_normalized
from .runtime import _resolve_kernel
from .runtime import _validate_kernel_for_cpu

APPLE_RT_NATIVE_PREDICATES = frozenset({"ray_triangle_closest_hit"})
APPLE_RT_COMPATIBILITY_PREDICATES = frozenset(
    {
        "bfs_discover",
        "bounded_knn_rows",
        "conjunctive_scan",
        "fixed_radius_neighbors",
        "grouped_count",
        "grouped_sum",
        "knn_rows",
        "overlay_compose",
        "point_in_polygon",
        "point_nearest_segment",
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
        "ray_triangle_closest_hit",
        "ray_triangle_hit_count",
        "segment_intersection",
        "segment_polygon_anyhit_rows",
        "segment_polygon_hitcount",
        "triangle_match",
    }
)


class _RtdlRay3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("ox", ctypes.c_double),
        ("oy", ctypes.c_double),
        ("oz", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("dz", ctypes.c_double),
        ("tmax", ctypes.c_double),
    ]


class _RtdlTriangle3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("z0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("z1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
        ("z2", ctypes.c_double),
    ]


class _RtdlRayClosestHitRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("triangle_id", ctypes.c_uint32),
        ("t", ctypes.c_double),
    ]


_LIBRARY: ctypes.CDLL | None = None


class AppleRtRowView:
    def __init__(self, *, library: ctypes.CDLL, rows_ptr, row_count: int, row_type, field_names: tuple[str, ...]):
        self._library = library
        self._rows_ptr = rows_ptr
        self._row_count = int(row_count)
        self._row_type = row_type
        self._field_names = field_names
        self._freed = False

    def __iter__(self):
        for index in range(self._row_count):
            row = self._rows_ptr[index]
            yield {field: getattr(row, field) for field in self._field_names}

    def __len__(self) -> int:
        return self._row_count

    def __getitem__(self, index: int) -> dict[str, object]:
        if index < 0:
            index += self._row_count
        if index < 0 or index >= self._row_count:
            raise IndexError(index)
        row = self._rows_ptr[index]
        return {field: getattr(row, field) for field in self._field_names}

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if self._freed:
            return
        if bool(self._rows_ptr):
            self._library.rtdl_apple_rt_free_rows(self._rows_ptr)
        self._freed = True


def _candidate_library_paths() -> list[Path]:
    env = os.environ.get("RTDL_APPLE_RT_LIB")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    root = Path(__file__).resolve().parents[2]
    candidates.append(root / "build" / "librtdl_apple_rt.dylib")
    return candidates


def _load_library() -> ctypes.CDLL:
    global _LIBRARY
    if _LIBRARY is not None:
        return _LIBRARY
    if platform.system() != "Darwin":
        raise RuntimeError("Apple RT backend is only available on macOS")
    errors: list[str] = []
    for path in _candidate_library_paths():
        try:
            library = ctypes.CDLL(str(path))
        except OSError as exc:
            errors.append(f"{path}: {exc}")
            continue
        _configure_library(library)
        _LIBRARY = library
        return library
    raise RuntimeError("Apple RT backend library not found; run `make build-apple-rt`. Tried: " + "; ".join(errors))


def _configure_library(library: ctypes.CDLL) -> None:
    library.rtdl_apple_rt_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    library.rtdl_apple_rt_get_version.restype = ctypes.c_int
    library.rtdl_apple_rt_free_rows.argtypes = [ctypes.c_void_p]
    library.rtdl_apple_rt_free_rows.restype = None
    library.rtdl_apple_rt_context_probe.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    library.rtdl_apple_rt_context_probe.restype = ctypes.c_int
    library.rtdl_apple_rt_run_ray_closest_hit_3d.argtypes = [
        ctypes.POINTER(_RtdlRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayClosestHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_apple_rt_run_ray_closest_hit_3d.restype = ctypes.c_int


def _check_status(status: int, error_buffer: ctypes.Array[ctypes.c_char]) -> None:
    if status == 0:
        return
    message = error_buffer.value.decode("utf-8", errors="replace") or f"Apple RT backend returned status {status}"
    raise RuntimeError(message)


def apple_rt_version() -> tuple[int, int, int]:
    library = _load_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = library.rtdl_apple_rt_get_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
    if status != 0:
        raise RuntimeError("Apple RT backend rejected version query")
    return (major.value, minor.value, patch.value)


def apple_rt_context_probe() -> str:
    library = _load_library()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_context_probe(error, len(error))
    _check_status(status, error)
    return error.value.decode("utf-8", errors="replace")


def _pack_rays_3d(rays: tuple[_CanonicalRay3D, ...]):
    records = (_RtdlRay3D * len(rays))()
    for index, ray in enumerate(rays):
        records[index] = _RtdlRay3D(ray.id, ray.ox, ray.oy, ray.oz, ray.dx, ray.dy, ray.dz, ray.tmax)
    return records


def _pack_triangles_3d(triangles: tuple[_CanonicalTriangle3D, ...]):
    records = (_RtdlTriangle3D * len(triangles))()
    for index, triangle in enumerate(triangles):
        records[index] = _RtdlTriangle3D(
            triangle.id,
            triangle.x0,
            triangle.y0,
            triangle.z0,
            triangle.x1,
            triangle.y1,
            triangle.z1,
            triangle.x2,
            triangle.y2,
            triangle.z2,
        )
    return records


def ray_triangle_closest_hit_apple_rt(
    rays: tuple[_CanonicalRay3D, ...],
    triangles: tuple[_CanonicalTriangle3D, ...],
) -> AppleRtRowView:
    if any(not isinstance(ray, _CanonicalRay3D) for ray in rays):
        raise ValueError("Apple RT ray_triangle_closest_hit currently requires 3D rays")
    if any(not isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles):
        raise ValueError("Apple RT ray_triangle_closest_hit currently requires 3D triangles")
    library = _load_library()
    ray_records = _pack_rays_3d(rays)
    triangle_records = _pack_triangles_3d(triangles)
    rows_ptr = ctypes.POINTER(_RtdlRayClosestHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_apple_rt_run_ray_closest_hit_3d(
        ray_records,
        len(rays),
        triangle_records,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    return AppleRtRowView(
        library=library,
        rows_ptr=rows_ptr,
        row_count=row_count.value,
        row_type=_RtdlRayClosestHitRow,
        field_names=("ray_id", "triangle_id", "t"),
    )


def apple_rt_predicate_mode(predicate_name: str) -> str:
    """Return the current Apple RT dispatch class for a predicate.

    `native_mps_rt` means the operation uses the Apple Metal/MPS ray
    intersector. `cpu_reference_compat` means the public Apple RT dispatcher is
    callable for parity but the operation is not yet hardware-backed.
    """
    if predicate_name in APPLE_RT_NATIVE_PREDICATES:
        return "native_mps_rt"
    if predicate_name in APPLE_RT_COMPATIBILITY_PREDICATES:
        return "cpu_reference_compat"
    return "unsupported"


def apple_rt_support_matrix() -> tuple[dict[str, str], ...]:
    return tuple(
        {"predicate": predicate_name, "mode": apple_rt_predicate_mode(predicate_name)}
        for predicate_name in sorted(APPLE_RT_COMPATIBILITY_PREDICATES)
    )


def run_apple_rt(
    kernel: CompiledKernel | object,
    *,
    native_only: bool = False,
    **inputs,
) -> tuple[dict[str, object], ...]:
    compiled = _resolve_kernel(kernel)
    _validate_kernel_for_cpu(compiled)
    _load_library()
    if compiled.candidates is None:
        raise ValueError("run_apple_rt currently requires a traversal candidate stage")
    if compiled.refine_op is None:
        raise ValueError("run_apple_rt currently requires a refine stage")
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name not in APPLE_RT_COMPATIBILITY_PREDICATES:
        raise NotImplementedError(f"Apple RT dispatcher does not support predicate `{predicate_name}`")
    expected_inputs = {item.name: item for item in compiled.inputs}
    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL Apple RT inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL Apple RT inputs: {', '.join(sorted(unexpected))}")
    normalized = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }
    rays = normalized[compiled.candidates.left.name]
    triangles = normalized[compiled.candidates.right.name]
    if predicate_name == "ray_triangle_closest_hit" and all(
        isinstance(ray, _CanonicalRay3D) for ray in rays
    ) and all(isinstance(triangle, _CanonicalTriangle3D) for triangle in triangles):
        return tuple(ray_triangle_closest_hit_apple_rt(rays, triangles))
    if native_only:
        raise NotImplementedError(
            "Apple RT native MPS execution currently supports only 3D ray_triangle_closest_hit; "
            f"`{predicate_name}` is available only through CPU reference compatibility dispatch"
        )
    return _run_cpu_python_reference_from_normalized(compiled, normalized)
