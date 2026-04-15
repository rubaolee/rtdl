from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps

from .ir import CandidateSet
from .ir import CompiledKernel
from .ir import EmitOp
from .ir import GeometryInput
from .ir import Predicate
from .ir import RefineOp
from .layout_types import GeometryType
from .layout_types import Layout


@dataclass
class _KernelContext:
    name: str
    backend: str
    precision: str
    inputs: list[GeometryInput] = field(default_factory=list)
    candidates: CandidateSet | None = None
    refine_op: RefineOp | None = None
    emit_op: EmitOp | None = None

    def compile(self) -> CompiledKernel:
        return CompiledKernel(
            name=self.name,
            backend=self.backend,
            precision=self.precision,
            inputs=tuple(self.inputs),
            candidates=self.candidates,
            refine_op=self.refine_op,
            emit_op=self.emit_op,
            lowering_plan=(
                "Normalize geometry roles, layouts, and kernel constraints.",
                f"Select the `{self.precision}` precision policy for `{self.backend}`.",
                "Choose acceleration ownership, launch parameter schema, and payload register mapping.",
                "Lower traversal and refine stages into RTDL backend-plan operations.",
                "Materialize the declared output record schema.",
            ),
        )


_context_stack: list[_KernelContext] = []


def _current_context() -> _KernelContext:
    if not _context_stack:
        raise RuntimeError("RTDL operations must run inside @rt.kernel compilation")
    return _context_stack[-1]


def kernel(*, backend: str, precision: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper():
            context = _KernelContext(
                name=fn.__name__,
                backend=backend,
                precision=precision,
            )
            _context_stack.append(context)
            try:
                result = fn()
                if not isinstance(result, EmitOp):
                    raise TypeError("kernel function must return rt.emit(...)")
                return context.compile()
            finally:
                _context_stack.pop()

        wrapper._rtdsl_kernel = True
        return wrapper

    return decorator


def input(
    name: str,
    geometry: GeometryType,
    *,
    layout: Layout | None = None,
    role: str | None = None,
) -> GeometryInput:
    context = _current_context()
    if role is not None and role not in {"build", "probe"}:
        raise ValueError("input role must be one of: build, probe")
    if any(existing.name == name for existing in context.inputs):
        raise ValueError(f"duplicate input name in kernel: {name}")
    resolved_layout = layout or geometry.default_layout
    if geometry.required_fields:
        resolved_layout.require_fields(geometry.required_fields)
    node = GeometryInput(
        name=name,
        geometry=geometry,
        layout=resolved_layout,
        role=role,
    )
    context.inputs.append(node)
    return node


def traverse(
    left: GeometryInput,
    right: GeometryInput,
    *,
    accel: str = "bvh",
    mode: str | None = None,
) -> CandidateSet:
    context = _current_context()
    if mode is not None and mode not in {"graph_expand", "graph_intersect"}:
        raise ValueError("traverse mode must be one of: graph_expand, graph_intersect")
    node = CandidateSet(left=left, right=right, accel=accel, mode=mode)
    context.candidates = node
    return node


def segment_intersection(*, exact: bool = False) -> Predicate:
    return Predicate(name="segment_intersection", options={"exact": exact})


def point_in_polygon(
    *,
    exact: bool = False,
    boundary_mode: str = "inclusive",
    result_mode: str = "full_matrix",
) -> Predicate:
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("point_in_polygon result_mode must be 'full_matrix' or 'positive_hits'")
    return Predicate(
        name="point_in_polygon",
        options={"exact": exact, "boundary_mode": boundary_mode, "result_mode": result_mode},
    )


def overlay_compose() -> Predicate:
    return Predicate(name="overlay_compose", options={})


def ray_triangle_hit_count(*, exact: bool = False) -> Predicate:
    return Predicate(name="ray_triangle_hit_count", options={"exact": exact})


def segment_polygon_hitcount(*, exact: bool = False) -> Predicate:
    return Predicate(name="segment_polygon_hitcount", options={"exact": exact})


def segment_polygon_anyhit_rows(*, exact: bool = False) -> Predicate:
    return Predicate(name="segment_polygon_anyhit_rows", options={"exact": exact})


def polygon_pair_overlap_area_rows(*, exact: bool = False) -> Predicate:
    return Predicate(name="polygon_pair_overlap_area_rows", options={"exact": exact})


def polygon_set_jaccard(*, exact: bool = False) -> Predicate:
    return Predicate(name="polygon_set_jaccard", options={"exact": exact})


def point_nearest_segment(*, exact: bool = False) -> Predicate:
    return Predicate(name="point_nearest_segment", options={"exact": exact})


def fixed_radius_neighbors(*, radius: float, k_max: int) -> Predicate:
    if radius < 0.0:
        raise ValueError("fixed_radius_neighbors radius must be non-negative")
    if k_max <= 0:
        raise ValueError("fixed_radius_neighbors k_max must be positive")
    return Predicate(
        name="fixed_radius_neighbors",
        options={"radius": float(radius), "k_max": int(k_max)},
    )


def knn_rows(*, k: int) -> Predicate:
    if k <= 0:
        raise ValueError("knn_rows k must be positive")
    return Predicate(
        name="knn_rows",
        options={"k": int(k)},
    )


def bounded_knn_rows(*, radius: float, k_max: int) -> Predicate:
    if radius < 0.0:
        raise ValueError("bounded_knn_rows radius must be non-negative")
    if k_max <= 0:
        raise ValueError("bounded_knn_rows k_max must be positive")
    return Predicate(
        name="bounded_knn_rows",
        options={"radius": float(radius), "k_max": int(k_max)},
    )


def bfs_discover(*, visited, dedupe: bool = True) -> Predicate:
    visited_name = visited.name if hasattr(visited, "name") else str(visited)
    if not visited_name:
        raise ValueError("bfs_discover requires a visited input reference")
    return Predicate(
        name="bfs_discover",
        options={"visited_input": visited_name, "dedupe": bool(dedupe)},
    )


def triangle_match(*, order: str = "id_ascending", unique: bool = True) -> Predicate:
    if order not in {"id_ascending"}:
        raise ValueError("triangle_match order must be 'id_ascending'")
    return Predicate(
        name="triangle_match",
        options={"order": order, "unique": bool(unique)},
    )


def contains(
    *,
    exact: bool = False,
    boundary_mode: str = "inclusive",
    result_mode: str = "full_matrix",
) -> Predicate:
    """Alias for point_in_polygon, for use in PIP kernels and demos."""
    return point_in_polygon(exact=exact, boundary_mode=boundary_mode, result_mode=result_mode)


def refine(candidates: CandidateSet, *, predicate: Predicate) -> RefineOp:
    context = _current_context()
    node = RefineOp(candidates=candidates, predicate=predicate)
    context.refine_op = node
    return node


def emit(source: RefineOp, *, fields: list[str]) -> EmitOp:
    context = _current_context()
    node = EmitOp(source=source, fields=tuple(fields))
    context.emit_op = node
    return node


def compile_kernel(fn) -> CompiledKernel:
    if not callable(fn):
        raise TypeError("compile_kernel expects a kernel function")
    return fn()
