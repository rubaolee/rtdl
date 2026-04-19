"""Adaptive RTDL backend skeleton.

Goal585 establishes the public contract for a future performance backend.  The
current implementation is deliberately a compatibility dispatcher: all workload
results come from the CPU Python reference path, while the support matrix and
mode strings make that fact visible to callers.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass

from .ir import CompiledKernel
from .runtime import _resolve_kernel
from .runtime import run_cpu_python_reference


ADAPTIVE_BACKEND_NAME = "adaptive"
ADAPTIVE_COMPAT_MODE = "cpu_reference_compat"


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

    return tuple(row.to_dict() for row in _ADAPTIVE_WORKLOADS)


def adaptive_predicate_mode(kernel_fn_or_compiled) -> dict[str, object]:
    """Return the adaptive dispatch decision for a compiled kernel."""

    compiled = _resolve_kernel(kernel_fn_or_compiled)
    workload = _classify_workload(compiled)
    row = _WORKLOAD_BY_NAME[workload]
    return {
        "backend": ADAPTIVE_BACKEND_NAME,
        "workload": row.workload,
        "predicate": row.predicate,
        "family": row.family,
        "mode": row.mode,
        "native": row.native,
        "prepared_context": row.prepared_context,
    }


def run_adaptive(kernel_fn_or_compiled, **inputs) -> tuple[dict[str, object], ...]:
    """Run an RTDL kernel through the adaptive backend surface.

    Goal585 does not provide native adaptive kernels yet.  It validates that the
    workload is inside the 18-workload matrix and then calls the CPU Python
    reference path.  The public mode APIs expose this as `cpu_reference_compat`.
    """

    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _classify_workload(compiled)
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
