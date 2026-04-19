"""Adaptive RTDL backend skeleton.

Goal585 establishes the public contract for a future performance backend.  The
current implementation is deliberately a compatibility dispatcher: all workload
results come from the CPU Python reference path, while the support matrix and
mode strings make that fact visible to callers.
"""

from __future__ import annotations

import ctypes
import functools
import platform
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from .ir import CompiledKernel
from .reference import Ray3D
from .reference import Triangle3D
from .runtime import _normalize_records
from .runtime import _project_rows
from .runtime import _resolve_kernel
from .runtime import run_cpu_python_reference


ADAPTIVE_BACKEND_NAME = "adaptive"
ADAPTIVE_COMPAT_MODE = "cpu_reference_compat"
ADAPTIVE_NATIVE_RAY_HITCOUNT_3D_MODE = "native_adaptive_cpu_soa_3d"
_ERROR_BUFFER_SIZE = 512


class _RtdlAdaptiveRay3D(ctypes.Structure):
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


class _RtdlAdaptiveTriangle3D(ctypes.Structure):
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


class _RtdlAdaptiveRayHitCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class AdaptiveWorkloadSupport:
    workload: str
    predicate: str
    family: str
    mode: str
    native: bool
    prepared_context: bool
    layout_strategy: str
    branch_strategy: str
    cache_strategy: str
    thread_safety: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_ADAPTIVE_WORKLOADS: tuple[AdaptiveWorkloadSupport, ...] = (
    AdaptiveWorkloadSupport(
        "segment_intersection",
        "segment_intersection",
        "geometry_2d",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: SoA segment endpoints plus bounding-box tiles",
        "future: bbox mask before exact segment test",
        "future: L1 segment-pair tiles, L2 build-side segment blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "point_in_polygon",
        "point_in_polygon",
        "geometry_2d",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: packed polygon refs plus contiguous vertex rings",
        "future: bbox rejection mask before winding/parity refinement",
        "future: vertex-ring blocks reused across point batches",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "overlay_compose",
        "overlay_compose",
        "geometry_2d",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: polygon bbox tiles plus ring metadata",
        "future: split overlap, LSI-needed, and PIP-needed flags",
        "future: tile candidate polygons before exact composition flags",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "ray_triangle_hit_count_2d",
        "ray_triangle_hit_count",
        "ray_triangle",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: SoA rays and 2D triangle blocks",
        "future: masked ray/triangle candidate tests",
        "future: ray microbatches against triangle cache blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "ray_triangle_hit_count_3d",
        "ray_triangle_hit_count",
        "ray_triangle",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: SoA 3D rays and triangle vertex blocks",
        "future: branch-reduced Moller-Trumbore candidate loop",
        "future: prepared triangle blocks reused across ray batches",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "segment_polygon_hitcount",
        "segment_polygon_hitcount",
        "geometry_2d",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: segment SoA plus polygon ring blocks",
        "future: bbox masks and separated boundary slow path",
        "future: polygon tile reuse across segment batches",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "segment_polygon_anyhit_rows",
        "segment_polygon_anyhit_rows",
        "geometry_2d",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: segment SoA plus polygon ring blocks",
        "future: early-exit any-hit loop after bbox mask",
        "future: polygon tile reuse across segment batches",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "point_nearest_segment",
        "point_nearest_segment",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: point SoA plus segment endpoint SoA",
        "future: min-distance update with predictable loop body",
        "future: segment blocks reused across point batches",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "fixed_radius_neighbors_2d",
        "fixed_radius_neighbors",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: 2D point SoA plus cell/Morton buckets",
        "future: squared-distance mask before row emission",
        "future: query tiles against bucket-local point blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "fixed_radius_neighbors_3d",
        "fixed_radius_neighbors",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: 3D point SoA plus cell/Morton buckets",
        "future: squared-distance mask before row emission",
        "future: query tiles against bucket-local point blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "bounded_knn_rows_3d",
        "bounded_knn_rows",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: 3D point SoA plus bounded candidate buckets",
        "future: fixed-size candidate slots before final rank emission",
        "future: query tiles against bucket-local point blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "knn_rows_2d",
        "knn_rows",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: 2D point SoA plus search buckets",
        "future: fixed-size rank slots with predictable updates",
        "future: query tiles against reusable point blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "knn_rows_3d",
        "knn_rows",
        "nearest_neighbor",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: 3D point SoA plus search buckets",
        "future: fixed-size rank slots with predictable updates",
        "future: query tiles against reusable point blocks",
        "read-only inputs; no shared mutable scratch in Goal585",
    ),
    AdaptiveWorkloadSupport(
        "bfs_discover",
        "bfs_discover",
        "graph",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: CSR plus frontier and visited bitsets",
        "future: split already-visited and newly-discovered paths",
        "future: frontier batches over contiguous CSR edge ranges",
        "read-only graph; per-call visited/frontier scratch only",
    ),
    AdaptiveWorkloadSupport(
        "triangle_match",
        "triangle_match",
        "graph",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: CSR with degree-ordered edge seeds",
        "future: merge/intersection loops with predictable short-side choice",
        "future: adjacency blocks reused across seed batches",
        "read-only graph; per-call output scratch only",
    ),
    AdaptiveWorkloadSupport(
        "conjunctive_scan",
        "conjunctive_scan",
        "db_analytics",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: columnar hot fields plus text dictionaries",
        "future: predicate bytecode and row masks instead of nested branches",
        "future: column blocks and reusable predicate metadata",
        "read-only table; per-call masks and output scratch only",
    ),
    AdaptiveWorkloadSupport(
        "grouped_count",
        "grouped_count",
        "db_analytics",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: columnar hot fields plus compact group-key dictionary",
        "future: predicate masks before aggregation slot update",
        "future: column blocks and reusable group slots",
        "read-only table; per-call aggregation scratch only",
    ),
    AdaptiveWorkloadSupport(
        "grouped_sum",
        "grouped_sum",
        "db_analytics",
        ADAPTIVE_COMPAT_MODE,
        False,
        False,
        "future: columnar hot fields plus compact group-key/value columns",
        "future: predicate masks before sum-slot update",
        "future: column blocks and reusable group slots",
        "read-only table; per-call aggregation scratch only",
    ),
)

_WORKLOAD_BY_NAME = {row.workload: row for row in _ADAPTIVE_WORKLOADS}
_WORKLOADS_BY_PREDICATE: dict[str, tuple[AdaptiveWorkloadSupport, ...]] = {}
for _row in _ADAPTIVE_WORKLOADS:
    _WORKLOADS_BY_PREDICATE.setdefault(_row.predicate, ())
    _WORKLOADS_BY_PREDICATE[_row.predicate] = _WORKLOADS_BY_PREDICATE[_row.predicate] + (_row,)


def adaptive_support_matrix() -> tuple[dict[str, object], ...]:
    """Return the Goal585 adaptive backend workload matrix.

    The matrix is intentionally explicit that Goal585 is compatibility-only.
    Native adaptive acceleration must flip `native` to true in later goals.
    """

    return tuple(_support_row_with_runtime_mode(row) for row in _ADAPTIVE_WORKLOADS)


def adaptive_predicate_mode(kernel_fn_or_compiled) -> dict[str, object]:
    """Return the adaptive dispatch decision for a compiled kernel."""

    compiled = _resolve_kernel(kernel_fn_or_compiled)
    workload = _classify_workload(compiled)
    row = _WORKLOAD_BY_NAME[workload]
    runtime_row = _support_row_with_runtime_mode(row)
    return {
        "backend": ADAPTIVE_BACKEND_NAME,
        "workload": runtime_row["workload"],
        "predicate": runtime_row["predicate"],
        "family": runtime_row["family"],
        "mode": runtime_row["mode"],
        "native": runtime_row["native"],
        "prepared_context": runtime_row["prepared_context"],
    }


def run_adaptive(kernel_fn_or_compiled, **inputs) -> tuple[dict[str, object], ...]:
    """Run an RTDL kernel through the adaptive backend surface.

    Goal585 does not provide native adaptive kernels yet.  It validates that the
    workload is inside the 18-workload matrix and then calls the CPU Python
    reference path.  The public mode APIs expose this as `cpu_reference_compat`.
    """

    compiled = _resolve_kernel(kernel_fn_or_compiled)
    workload = _classify_workload(compiled)
    if workload == "ray_triangle_hit_count_3d" and adaptive_available():
        return _run_ray_triangle_hit_count_3d_native(compiled, inputs)
    return run_cpu_python_reference(compiled, **inputs)


def prepare_adaptive(kernel_fn_or_compiled, **inputs) -> "PreparedAdaptiveExecution":
    """Create a Goal585 prepared adaptive compatibility execution."""

    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _classify_workload(compiled)
    mode = adaptive_predicate_mode(compiled)
    return PreparedAdaptiveExecution(compiled=compiled, inputs=dict(inputs), mode=mode)


@dataclass(frozen=True)
class PreparedAdaptiveExecution:
    compiled: CompiledKernel
    inputs: dict[str, object]
    mode: dict[str, object]

    def run(self) -> tuple[dict[str, object], ...]:
        return run_adaptive(self.compiled, **self.inputs)


def _classify_workload(compiled: CompiledKernel) -> str:
    if compiled.refine_op is None:
        raise ValueError("adaptive backend requires a compiled kernel with a refine predicate")
    predicate = compiled.refine_op.predicate.name
    rows = _WORKLOADS_BY_PREDICATE.get(predicate)
    if not rows:
        raise ValueError(f"unsupported adaptive backend predicate: {predicate!r}")
    if len(rows) == 1:
        return rows[0].workload
    return _classify_dimensional_workload(compiled, predicate)


def _classify_dimensional_workload(compiled: CompiledKernel, predicate: str) -> str:
    layout_names = {item.layout.name for item in compiled.inputs}
    has_3d = any(name.endswith("3D") for name in layout_names)
    if predicate == "ray_triangle_hit_count":
        return "ray_triangle_hit_count_3d" if has_3d else "ray_triangle_hit_count_2d"
    if predicate == "fixed_radius_neighbors":
        return "fixed_radius_neighbors_3d" if has_3d else "fixed_radius_neighbors_2d"
    if predicate == "knn_rows":
        return "knn_rows_3d" if has_3d else "knn_rows_2d"
    if predicate == "bounded_knn_rows":
        if not has_3d:
            raise ValueError("adaptive backend Goal585 matrix supports bounded_knn_rows_3d only")
        return "bounded_knn_rows_3d"
    raise ValueError(f"ambiguous adaptive backend predicate: {predicate!r}")


def adaptive_available() -> bool:
    try:
        _adaptive_lib()
    except Exception:
        return False
    return True


def adaptive_version() -> tuple[int, int, int]:
    lib = _adaptive_lib()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = lib.rtdl_adaptive_get_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
    if status != 0:
        raise RuntimeError(f"rtdl_adaptive_get_version failed with status {status}")
    return int(major.value), int(minor.value), int(patch.value)


def _support_row_with_runtime_mode(row: AdaptiveWorkloadSupport) -> dict[str, object]:
    payload = row.to_dict()
    if row.workload == "ray_triangle_hit_count_3d" and adaptive_available():
        payload["mode"] = ADAPTIVE_NATIVE_RAY_HITCOUNT_3D_MODE
        payload["native"] = True
    return payload


def _run_ray_triangle_hit_count_3d_native(
    compiled: CompiledKernel,
    inputs: dict[str, object],
) -> tuple[dict[str, object], ...]:
    expected_inputs = {item.name: item for item in compiled.inputs}
    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL adaptive inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL adaptive inputs: {', '.join(sorted(unexpected))}")

    normalized_inputs = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }
    rays_name = compiled.candidates.left.name
    triangles_name = compiled.candidates.right.name
    rays = normalized_inputs[rays_name]
    triangles = normalized_inputs[triangles_name]
    if any(not isinstance(item, Ray3D) for item in rays):
        raise TypeError("native adaptive ray_triangle_hit_count_3d requires Ray3D inputs")
    if any(not isinstance(item, Triangle3D) for item in triangles):
        raise TypeError("native adaptive ray_triangle_hit_count_3d requires Triangle3D inputs")

    ray_array = (_RtdlAdaptiveRay3D * len(rays))(
        *(
            _RtdlAdaptiveRay3D(
                int(ray.id),
                float(ray.ox),
                float(ray.oy),
                float(ray.oz),
                float(ray.dx),
                float(ray.dy),
                float(ray.dz),
                float(ray.tmax),
            )
            for ray in rays
        )
    )
    triangle_array = (_RtdlAdaptiveTriangle3D * len(triangles))(
        *(
            _RtdlAdaptiveTriangle3D(
                int(triangle.id),
                float(triangle.x0),
                float(triangle.y0),
                float(triangle.z0),
                float(triangle.x1),
                float(triangle.y1),
                float(triangle.z1),
                float(triangle.x2),
                float(triangle.y2),
                float(triangle.z2),
            )
            for triangle in triangles
        )
    )
    rows_ptr = ctypes.POINTER(_RtdlAdaptiveRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(_ERROR_BUFFER_SIZE)
    status = _adaptive_lib().rtdl_adaptive_run_ray_hitcount_3d(
        ray_array,
        len(rays),
        triangle_array,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        _ERROR_BUFFER_SIZE,
    )
    if status != 0:
        detail = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_adaptive_run_ray_hitcount_3d failed with status {status}: {detail}")
    try:
        rows = tuple(
            {"ray_id": int(rows_ptr[index].ray_id), "hit_count": int(rows_ptr[index].hit_count)}
            for index in range(row_count.value)
        )
    finally:
        _adaptive_lib().rtdl_adaptive_free_rows(rows_ptr)
    return _project_rows(compiled, rows)


@functools.lru_cache(maxsize=1)
def _adaptive_lib():
    path = _adaptive_library_path()
    lib = ctypes.CDLL(str(path))
    lib.rtdl_adaptive_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.rtdl_adaptive_get_version.restype = ctypes.c_int
    lib.rtdl_adaptive_free_rows.argtypes = [ctypes.c_void_p]
    lib.rtdl_adaptive_free_rows.restype = None
    lib.rtdl_adaptive_run_ray_hitcount_3d.argtypes = [
        ctypes.POINTER(_RtdlAdaptiveRay3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlAdaptiveTriangle3D),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlAdaptiveRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_adaptive_run_ray_hitcount_3d.restype = ctypes.c_int
    return lib


def _adaptive_library_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    extension = ".dylib" if platform.system() == "Darwin" else ".dll" if platform.system() == "Windows" else ".so"
    path = repo_root / "build" / f"librtdl_adaptive{extension}"
    if not path.exists():
        raise RuntimeError(f"RTDL adaptive backend library is not built at {path}; run `make build-adaptive`")
    return path
