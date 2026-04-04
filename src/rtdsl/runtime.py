from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import is_dataclass

from .api import compile_kernel
from .ir import CompiledKernel
from .oracle_runtime import run_oracle
from .reference import lsi_cpu
from .reference import overlay_compose_cpu
from .reference import pip_cpu
from .reference import Point
from .reference import point_nearest_segment_cpu
from .reference import Polygon
from .reference import Ray2D
from .reference import ray_triangle_hit_count_cpu
from .reference import Segment
from .reference import segment_polygon_hitcount_cpu
from .reference import Triangle


def _identity_cache_token(geometry_name: str, payload) -> tuple[object, ...] | None:
    if not isinstance(payload, tuple):
        return None

    expected_type = {
        "segments": Segment,
        "points": Point,
        "polygons": Polygon,
        "triangles": Triangle,
        "rays": Ray2D,
    }.get(geometry_name)
    if expected_type is None:
        return None

    if any(not isinstance(item, expected_type) for item in payload):
        return None
    return ("identity", geometry_name, id(payload), len(payload))


def run_cpu(kernel_fn_or_compiled, **inputs) -> tuple[dict[str, object], ...]:
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL simulator inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL simulator inputs: {', '.join(sorted(unexpected))}")

    normalized_inputs = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }

    return _project_rows(compiled, run_oracle(compiled, normalized_inputs))


def run_cpu_python_reference(kernel_fn_or_compiled, **inputs) -> tuple[dict[str, object], ...]:
    compiled = _resolve_kernel(kernel_fn_or_compiled)
    _validate_kernel_for_cpu(compiled)
    expected_inputs = {item.name: item for item in compiled.inputs}

    missing = [name for name in expected_inputs if name not in inputs]
    unexpected = [name for name in inputs if name not in expected_inputs]
    if missing:
        raise ValueError(f"missing RTDL simulator inputs: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"unexpected RTDL simulator inputs: {', '.join(sorted(unexpected))}")

    normalized_inputs = {
        name: _normalize_records(name, expected_inputs[name].geometry.name, payload)
        for name, payload in inputs.items()
    }
    return _run_cpu_python_reference_from_normalized(compiled, normalized_inputs)


def _resolve_kernel(kernel_fn_or_compiled) -> CompiledKernel:
    if isinstance(kernel_fn_or_compiled, CompiledKernel):
        return kernel_fn_or_compiled
    return compile_kernel(kernel_fn_or_compiled)


def _validate_kernel_for_cpu(compiled: CompiledKernel) -> None:
    if compiled.precision != "float_approx":
        raise ValueError("RTDL CPU simulator currently supports only precision='float_approx'")
    if compiled.candidates is None or compiled.refine_op is None or compiled.emit_op is None:
        raise ValueError("RTDL CPU simulator requires a fully compiled kernel with traverse/refine/emit")


def _run_cpu_python_reference_from_normalized(
    compiled: CompiledKernel,
    normalized_inputs,
) -> tuple[dict[str, object], ...]:
    predicate_name = compiled.refine_op.predicate.name
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name

    if predicate_name == "segment_intersection":
        rows = lsi_cpu(normalized_inputs[left_name], normalized_inputs[right_name])
    elif predicate_name == "point_in_polygon":
        rows = pip_cpu(
            normalized_inputs[left_name],
            normalized_inputs[right_name],
            boundary_mode=compiled.refine_op.predicate.options.get("boundary_mode", "inclusive"),
            result_mode=compiled.refine_op.predicate.options.get("result_mode", "full_matrix"),
        )
    elif predicate_name == "overlay_compose":
        rows = overlay_compose_cpu(normalized_inputs[left_name], normalized_inputs[right_name])
    elif predicate_name == "ray_triangle_hit_count":
        rows = ray_triangle_hit_count_cpu(normalized_inputs[left_name], normalized_inputs[right_name])
    elif predicate_name == "segment_polygon_hitcount":
        rows = segment_polygon_hitcount_cpu(normalized_inputs[left_name], normalized_inputs[right_name])
    elif predicate_name == "point_nearest_segment":
        rows = point_nearest_segment_cpu(normalized_inputs[left_name], normalized_inputs[right_name])
    else:
        raise ValueError(f"unsupported RTDL CPU simulator predicate: {predicate_name}")

    return _project_rows(compiled, rows)


def _project_rows(compiled: CompiledKernel, rows) -> tuple[dict[str, object], ...]:
    emit_fields = compiled.emit_op.fields
    projected_rows = []
    for row in rows:
        missing_fields = [field for field in emit_fields if field not in row]
        if missing_fields:
            raise ValueError(
                "CPU simulator row is missing emitted fields: "
                + ", ".join(missing_fields)
            )
        projected_rows.append({field: row[field] for field in emit_fields})
    return tuple(projected_rows)


def _normalize_records(name: str, geometry_name: str, payload) -> tuple[object, ...]:
    if isinstance(payload, (str, bytes)) or not isinstance(payload, Iterable):
        raise ValueError(f"simulator input `{name}` must be an iterable of records")

    if geometry_name == "segments":
        return tuple(_coerce_segment(name, item) for item in payload)
    if geometry_name == "points":
        return tuple(_coerce_point(name, item) for item in payload)
    if geometry_name == "polygons":
        return tuple(_coerce_polygon(name, item) for item in payload)
    if geometry_name == "triangles":
        return tuple(_coerce_triangle(name, item) for item in payload)
    if geometry_name == "rays":
        return tuple(_coerce_ray(name, item) for item in payload)
    raise ValueError(f"unsupported RTDL simulator geometry: {geometry_name}")


def _coerce_segment(input_name: str, record) -> Segment:
    if isinstance(record, Segment):
        return record
    data = _extract_record_fields(input_name, record, ("id", "x0", "y0", "x1", "y1"))
    return Segment(
        id=int(data["id"]),
        x0=float(data["x0"]),
        y0=float(data["y0"]),
        x1=float(data["x1"]),
        y1=float(data["y1"]),
    )


def _coerce_point(input_name: str, record) -> Point:
    if isinstance(record, Point):
        return record
    data = _extract_record_fields(input_name, record, ("id", "x", "y"))
    return Point(
        id=int(data["id"]),
        x=float(data["x"]),
        y=float(data["y"]),
    )


def _coerce_triangle(input_name: str, record) -> Triangle:
    if isinstance(record, Triangle):
        return record
    data = _extract_record_fields(input_name, record, ("id", "x0", "y0", "x1", "y1", "x2", "y2"))
    return Triangle(
        id=int(data["id"]),
        x0=float(data["x0"]),
        y0=float(data["y0"]),
        x1=float(data["x1"]),
        y1=float(data["y1"]),
        x2=float(data["x2"]),
        y2=float(data["y2"]),
    )


def _coerce_ray(input_name: str, record) -> Ray2D:
    if isinstance(record, Ray2D):
        return record
    data = _extract_record_fields(input_name, record, ("id", "ox", "oy", "dx", "dy", "tmax"))
    return Ray2D(
        id=int(data["id"]),
        ox=float(data["ox"]),
        oy=float(data["oy"]),
        dx=float(data["dx"]),
        dy=float(data["dy"]),
        tmax=float(data["tmax"]),
    )


def _coerce_polygon(input_name: str, record) -> Polygon:
    if isinstance(record, Polygon):
        return record

    data = _extract_record_fields(
        input_name,
        record,
        ("id", "vertices"),
        hint="CPU simulator polygons must provide logical polygon records with `id` and `vertices`.",
    )
    vertices = data["vertices"]
    if isinstance(vertices, (str, bytes)) or not isinstance(vertices, Iterable):
        raise ValueError(f"simulator polygon input `{input_name}` must provide iterable `vertices`")

    normalized_vertices = []
    for vertex in vertices:
        if not isinstance(vertex, Iterable) or isinstance(vertex, (str, bytes)):
            raise ValueError(f"simulator polygon input `{input_name}` has invalid vertex: {vertex!r}")
        coords = tuple(vertex)
        if len(coords) != 2:
            raise ValueError(f"simulator polygon input `{input_name}` vertex must have 2 coordinates")
        normalized_vertices.append((float(coords[0]), float(coords[1])))

    if len(normalized_vertices) < 3:
        raise ValueError(f"simulator polygon input `{input_name}` requires at least 3 vertices")

    return Polygon(id=int(data["id"]), vertices=tuple(normalized_vertices))


def _extract_record_fields(
    input_name: str,
    record,
    field_names: tuple[str, ...],
    *,
    hint: str | None = None,
) -> dict[str, object]:
    if isinstance(record, Mapping):
        missing = [name for name in field_names if name not in record]
        if missing:
            message = f"simulator input `{input_name}` record is missing fields: {', '.join(missing)}"
            if hint is not None:
                message = f"{message}. {hint}"
            raise ValueError(message)
        return {name: record[name] for name in field_names}

    if is_dataclass(record) or all(hasattr(record, name) for name in field_names):
        return {name: getattr(record, name) for name in field_names}

    message = f"simulator input `{input_name}` record must be a mapping or dataclass-like object"
    if hint is not None:
        message = f"{message}. {hint}"
    raise ValueError(message)
