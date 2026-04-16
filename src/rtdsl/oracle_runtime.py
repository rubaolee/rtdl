from __future__ import annotations

import ctypes
import functools
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import NoReturn

from .db_reference import GroupedAggregateQuery
from .db_reference import PredicateClause
from .ir import CompiledKernel
from .db_reference import grouped_count_cpu
from .db_reference import grouped_sum_cpu
from .reference import Point3D


def _pkg_config_flags(package: str, option: str) -> list[str]:
    try:
        result = subprocess.run(
            ["pkg-config", option, package],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return result.stdout.split()


def _geos_pkg_config_flags(option: str) -> list[str]:
    if platform.system() == "Windows":
        return []
    flags = _pkg_config_flags("geos", option)
    if flags:
        return flags
    flags = _pkg_config_flags("geos_c", option)
    if flags:
        return flags
    return ["-lgeos_c"] if option == "--libs" else []


def _run_windows_compile(command: list[str], *, vcvars: Path, cwd: Path) -> None:
    script = "\r\n".join(
        (
            "@echo off",
            f'call "{vcvars}" >nul 2>&1',
            "if errorlevel 1 exit /b %errorlevel%",
            subprocess.list2cmdline(command),
        )
    )
    with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False, encoding="utf-8", newline="") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["cmd", "/c", str(script_path)], check=True, cwd=cwd)
    finally:
        script_path.unlink(missing_ok=True)


class _RtdlSegment(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
    ]


class _RtdlPoint(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]


class _RtdlPoint3D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
    ]


class _RtdlPolygonRef(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("vertex_offset", ctypes.c_uint32),
        ("vertex_count", ctypes.c_uint32),
    ]


class _RtdlTriangle(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
    ]


class _RtdlRay2D(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint32),
        ("ox", ctypes.c_double),
        ("oy", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("tmax", ctypes.c_double),
    ]


class _RtdlLsiRow(ctypes.Structure):
    _fields_ = [
        ("left_id", ctypes.c_uint32),
        ("right_id", ctypes.c_uint32),
        ("intersection_point_x", ctypes.c_double),
        ("intersection_point_y", ctypes.c_double),
    ]


class _RtdlPipRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
        ("contains", ctypes.c_uint32),
    ]


class _RtdlOverlayRow(ctypes.Structure):
    _fields_ = [
        ("left_polygon_id", ctypes.c_uint32),
        ("right_polygon_id", ctypes.c_uint32),
        ("requires_lsi", ctypes.c_uint32),
        ("requires_pip", ctypes.c_uint32),
    ]


class _RtdlRayHitCountRow(ctypes.Structure):
    _fields_ = [
        ("ray_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonHitCountRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("hit_count", ctypes.c_uint32),
    ]


class _RtdlSegmentPolygonAnyHitRow(ctypes.Structure):
    _fields_ = [
        ("segment_id", ctypes.c_uint32),
        ("polygon_id", ctypes.c_uint32),
    ]


class _RtdlPolygonPairOverlapAreaRow(ctypes.Structure):
    _fields_ = [
        ("left_polygon_id", ctypes.c_uint32),
        ("right_polygon_id", ctypes.c_uint32),
        ("intersection_area", ctypes.c_uint32),
        ("left_area", ctypes.c_uint32),
        ("right_area", ctypes.c_uint32),
        ("union_area", ctypes.c_uint32),
    ]


class _RtdlPolygonSetJaccardRow(ctypes.Structure):
    _fields_ = [
        ("intersection_area", ctypes.c_uint32),
        ("left_area", ctypes.c_uint32),
        ("right_area", ctypes.c_uint32),
        ("union_area", ctypes.c_uint32),
        ("jaccard_similarity", ctypes.c_double),
    ]


class _RtdlPointNearestSegmentRow(ctypes.Structure):
    _fields_ = [
        ("point_id", ctypes.c_uint32),
        ("segment_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlFixedRadiusNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
    ]


class _RtdlKnnNeighborRow(ctypes.Structure):
    _fields_ = [
        ("query_id", ctypes.c_uint32),
        ("neighbor_id", ctypes.c_uint32),
        ("distance", ctypes.c_double),
        ("neighbor_rank", ctypes.c_uint32),
    ]


class _RtdlFrontierVertex(ctypes.Structure):
    _fields_ = [
        ("vertex_id", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlBfsExpandRow(ctypes.Structure):
    _fields_ = [
        ("src_vertex", ctypes.c_uint32),
        ("dst_vertex", ctypes.c_uint32),
        ("level", ctypes.c_uint32),
    ]


class _RtdlEdgeSeed(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
    ]


class _RtdlTriangleRow(ctypes.Structure):
    _fields_ = [
        ("u", ctypes.c_uint32),
        ("v", ctypes.c_uint32),
        ("w", ctypes.c_uint32),
    ]


class _RtdlDbField(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("kind", ctypes.c_uint32),
    ]


class _RtdlDbScalar(ctypes.Structure):
    _fields_ = [
        ("kind", ctypes.c_uint32),
        ("int_value", ctypes.c_int64),
        ("double_value", ctypes.c_double),
        ("string_value", ctypes.c_char_p),
    ]


class _RtdlDbClause(ctypes.Structure):
    _fields_ = [
        ("field", ctypes.c_char_p),
        ("op", ctypes.c_uint32),
        ("value", _RtdlDbScalar),
        ("value_hi", _RtdlDbScalar),
    ]


class _RtdlDbRowIdRow(ctypes.Structure):
    _fields_ = [
        ("row_id", ctypes.c_uint32),
    ]


class _RtdlDbGroupedCountRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("count", ctypes.c_int64),
    ]


class _RtdlDbGroupedSumRow(ctypes.Structure):
    _fields_ = [
        ("group_key", ctypes.c_int64),
        ("sum", ctypes.c_double),
    ]


def oracle_version() -> tuple[int, int, int]:
    library = _load_oracle_library()
    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    _check_status(library.rtdl_oracle_get_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)))
    return major.value, minor.value, patch.value


def run_oracle(compiled: CompiledKernel, normalized_inputs) -> tuple[dict[str, object], ...]:
    predicate_name = compiled.refine_op.predicate.name
    if predicate_name == "conjunctive_scan":
        library = _load_oracle_library()
        return _run_conjunctive_scan_oracle(compiled, normalized_inputs, library)
    if predicate_name == "grouped_count":
        library = _load_oracle_library()
        return _run_grouped_count_oracle(compiled, normalized_inputs, library)
    if predicate_name == "grouped_sum":
        library = _load_oracle_library()
        return _run_grouped_sum_oracle(compiled, normalized_inputs, library)
    library = _load_oracle_library()
    if predicate_name == "bfs_discover":
        return _run_bfs_expand_oracle(compiled, normalized_inputs, library)
    if predicate_name == "triangle_match":
        return _run_triangle_probe_oracle(compiled, normalized_inputs, library)
    if predicate_name == "segment_intersection":
        return _run_lsi_oracle(compiled, normalized_inputs, library)
    if predicate_name == "point_in_polygon":
        return _run_pip_oracle(compiled, normalized_inputs, library)
    if predicate_name == "overlay_compose":
        return _run_overlay_oracle(compiled, normalized_inputs, library)
    if predicate_name == "ray_triangle_hit_count":
        return _run_ray_hitcount_oracle(compiled, normalized_inputs, library)
    if predicate_name == "segment_polygon_hitcount":
        return _run_segment_polygon_hitcount_oracle(compiled, normalized_inputs, library)
    if predicate_name == "segment_polygon_anyhit_rows":
        return _run_segment_polygon_anyhit_rows_oracle(compiled, normalized_inputs, library)
    if predicate_name == "polygon_pair_overlap_area_rows":
        return _run_polygon_pair_overlap_area_rows_oracle(compiled, normalized_inputs, library)
    if predicate_name == "polygon_set_jaccard":
        return _run_polygon_set_jaccard_oracle(compiled, normalized_inputs, library)
    if predicate_name == "point_nearest_segment":
        return _run_point_nearest_segment_oracle(compiled, normalized_inputs, library)
    if predicate_name == "fixed_radius_neighbors":
        return _run_fixed_radius_neighbors_oracle(compiled, normalized_inputs, library)
    if predicate_name == "knn_rows":
        return _run_knn_rows_oracle(compiled, normalized_inputs, library)
    if predicate_name == "bounded_knn_rows":
        return _run_bounded_knn_rows_oracle(compiled, normalized_inputs, library)
    raise ValueError(f"unsupported RTDL native oracle predicate: {predicate_name}")


def _run_conjunctive_scan_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    predicates_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    table_rows = normalized_inputs[table_name]
    predicates = normalized_inputs[predicates_name]
    fields_array, row_values_array, row_count = _encode_db_table(table_rows)
    clauses_array = _encode_db_clauses(predicates.clauses)
    rows_ptr = ctypes.POINTER(_RtdlDbRowIdRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_conjunctive_scan(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        row_values_array,
        ctypes.c_size_t(row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.c_size_t(len(error)),
    )
    _check_status(status, error)
    try:
        row_count_value = row_count_out.value
        return tuple({"row_id": int(rows_ptr[index].row_id)} for index in range(row_count_value))
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_grouped_count_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    query = normalized_inputs[query_name]
    table_rows = normalized_inputs[table_name]
    if len(query.group_keys) != 1:
        return grouped_count_cpu(table_rows, query)
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=query.group_keys,
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedCountRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    group_field = query.group_keys[0]
    status = library.rtdl_oracle_run_grouped_count(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        row_values_array,
        ctypes.c_size_t(row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_field.encode("utf-8"),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.c_size_t(len(error)),
    )
    _check_status(status, error)
    try:
        reverse_map = reverse_maps.get(group_field)
        rows = []
        for index in range(row_count_out.value):
            group_key = _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key))
            rows.append({group_field: group_key, "count": int(rows_ptr[index].count)})
        return tuple(rows)
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_grouped_sum_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    table_name = compiled.candidates.right.name
    query = normalized_inputs[query_name]
    table_rows = normalized_inputs[table_name]
    if len(query.group_keys) != 1:
        return grouped_sum_cpu(table_rows, query)
    encoded_rows, encoded_predicates, reverse_maps = _encode_db_text_fields(
        table_rows,
        query.predicates,
        extra_fields=query.group_keys,
    )
    fields_array, row_values_array, row_count = _encode_db_table(encoded_rows)
    clauses_array = _encode_db_clauses(encoded_predicates)
    rows_ptr = ctypes.POINTER(_RtdlDbGroupedSumRow)()
    row_count_out = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    group_field = query.group_keys[0]
    status = library.rtdl_oracle_run_grouped_sum(
        fields_array,
        ctypes.c_size_t(len(fields_array)),
        row_values_array,
        ctypes.c_size_t(row_count),
        clauses_array,
        ctypes.c_size_t(len(clauses_array)),
        group_field.encode("utf-8"),
        str(query.value_field).encode("utf-8"),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count_out),
        error,
        ctypes.c_size_t(len(error)),
    )
    _check_status(status, error)
    try:
        reverse_map = reverse_maps.get(group_field)
        rows = []
        for index in range(row_count_out.value):
            group_key = _decode_db_group_key(reverse_map, int(rows_ptr[index].group_key))
            total = float(rows_ptr[index].sum)
            rows.append({group_field: group_key, "sum": int(total) if float(total).is_integer() else total})
        return tuple(rows)
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


_DB_KIND_INT64 = 1
_DB_KIND_FLOAT64 = 2
_DB_KIND_BOOL = 3
_DB_KIND_TEXT = 4

_DB_OP_EQ = 1
_DB_OP_LT = 2
_DB_OP_LE = 3
_DB_OP_GT = 4
_DB_OP_GE = 5
_DB_OP_BETWEEN = 6


def _encode_db_scalar(value) -> _RtdlDbScalar:
    if isinstance(value, bool):
        return _RtdlDbScalar(kind=_DB_KIND_BOOL, int_value=1 if value else 0)
    if isinstance(value, int) and not isinstance(value, bool):
        return _RtdlDbScalar(kind=_DB_KIND_INT64, int_value=int(value))
    if isinstance(value, float):
        return _RtdlDbScalar(kind=_DB_KIND_FLOAT64, double_value=float(value))
    return _RtdlDbScalar(kind=_DB_KIND_TEXT, string_value=str(value).encode("utf-8"))


def _encode_db_field_kind(value) -> int:
    if isinstance(value, bool):
        return _DB_KIND_BOOL
    if isinstance(value, int) and not isinstance(value, bool):
        return _DB_KIND_INT64
    if isinstance(value, float):
        return _DB_KIND_FLOAT64
    return _DB_KIND_TEXT


def _encode_db_table(table_rows) -> tuple[object, object, int]:
    if not table_rows:
        raise ValueError("native oracle DB path requires at least one denormalized table row")
    field_names = tuple(str(name) for name in table_rows[0].keys())
    if "row_id" not in field_names:
        raise ValueError("native oracle DB path requires a `row_id` field")
    for index, row in enumerate(table_rows):
        if tuple(str(name) for name in row.keys()) != field_names:
            raise ValueError(f"denorm table row {index} does not match the first-row schema")
    field_records = [_RtdlDbField(name=name.encode("utf-8"), kind=_encode_db_field_kind(table_rows[0][name])) for name in field_names]
    fields_array = (_RtdlDbField * len(field_records))(*field_records)
    scalar_records = []
    for row in table_rows:
        for name in field_names:
            scalar_records.append(_encode_db_scalar(row[name]))
    row_values_array = (_RtdlDbScalar * len(scalar_records))(*scalar_records)
    return fields_array, row_values_array, len(table_rows)


def _encode_db_text_fields(table_rows, clauses, *, extra_fields=()):
    encode_fields: set[str] = set()
    all_fields = set(extra_fields)
    all_fields.update(str(clause.field) for clause in clauses)
    for field in all_fields:
        values = [row[field] for row in table_rows if field in row]
        if any(isinstance(value, str) for value in values):
            encode_fields.add(field)
        for clause in clauses:
            if str(clause.field) != field:
                continue
            if isinstance(clause.value, str) or isinstance(clause.value_hi, str):
                encode_fields.add(field)
    reverse_maps: dict[str, dict[int, object]] = {}
    field_maps: dict[str, dict[object, int]] = {}
    for field in sorted(encode_fields):
        unique_values = sorted({row[field] for row in table_rows})
        encode_map = {value: index + 1 for index, value in enumerate(unique_values)}
        field_maps[field] = encode_map
        reverse_maps[field] = {code: value for value, code in encode_map.items()}
    encoded_rows = []
    for row in table_rows:
        encoded = dict(row)
        for field, encode_map in field_maps.items():
            encoded[field] = encode_map[row[field]]
        encoded_rows.append(encoded)
    encoded_clauses = []
    for clause in clauses:
        field = str(clause.field)
        if field in field_maps:
            encode_map = field_maps[field]
            value = encode_map[clause.value]
            value_hi = encode_map[clause.value_hi] if clause.value_hi is not None else None
            encoded_clauses.append(PredicateClause(field=field, op=clause.op, value=value, value_hi=value_hi))
        else:
            encoded_clauses.append(clause)
    return tuple(encoded_rows), tuple(encoded_clauses), reverse_maps


def _decode_db_group_key(reverse_map, encoded_value: int):
    if reverse_map is None:
        return encoded_value
    return reverse_map[encoded_value]


def _encode_db_clause(clause) -> _RtdlDbClause:
    op_map = {
        "eq": _DB_OP_EQ,
        "lt": _DB_OP_LT,
        "le": _DB_OP_LE,
        "gt": _DB_OP_GT,
        "ge": _DB_OP_GE,
        "between": _DB_OP_BETWEEN,
    }
    return _RtdlDbClause(
        field=str(clause.field).encode("utf-8"),
        op=op_map[str(clause.op)],
        value=_encode_db_scalar(clause.value),
        value_hi=_encode_db_scalar(clause.value_hi),
    )


def _encode_db_clauses(clauses) -> object:
    records = [_encode_db_clause(clause) for clause in clauses]
    return (_RtdlDbClause * len(records))(*records)


def _run_bfs_expand_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    frontier_name = compiled.candidates.left.name
    graph_name = compiled.candidates.right.name
    visited_name = str(compiled.refine_op.predicate.options["visited_input"])
    frontier = normalized_inputs[frontier_name]
    graph = normalized_inputs[graph_name]
    visited = normalized_inputs[visited_name]

    row_offsets = (ctypes.c_uint32 * len(graph.row_offsets))(*graph.row_offsets)
    column_indices = (ctypes.c_uint32 * len(graph.column_indices))(*graph.column_indices)
    frontier_array = (_RtdlFrontierVertex * len(frontier))(*[
        _RtdlFrontierVertex(item.vertex_id, item.level) for item in frontier
    ])
    visited_array = (ctypes.c_uint32 * len(visited))(*visited)
    rows_ptr = ctypes.POINTER(_RtdlBfsExpandRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_bfs_expand(
        row_offsets,
        len(graph.row_offsets),
        column_indices,
        len(graph.column_indices),
        frontier_array,
        len(frontier),
        visited_array,
        len(visited),
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("dedupe", True) else 0),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "src_vertex": rows_ptr[index].src_vertex,
                "dst_vertex": rows_ptr[index].dst_vertex,
                "level": rows_ptr[index].level,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_triangle_probe_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    seeds_name = compiled.candidates.left.name
    graph_name = compiled.candidates.right.name
    seeds = normalized_inputs[seeds_name]
    graph = normalized_inputs[graph_name]

    row_offsets = (ctypes.c_uint32 * len(graph.row_offsets))(*graph.row_offsets)
    column_indices = (ctypes.c_uint32 * len(graph.column_indices))(*graph.column_indices)
    seed_array = (_RtdlEdgeSeed * len(seeds))(*[
        _RtdlEdgeSeed(item.u, item.v) for item in seeds
    ])
    rows_ptr = ctypes.POINTER(_RtdlTriangleRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_triangle_probe(
        row_offsets,
        len(graph.row_offsets),
        column_indices,
        len(graph.column_indices),
        seed_array,
        len(seeds),
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("order", "id_ascending") == "id_ascending" else 0),
        ctypes.c_uint32(1 if compiled.refine_op.predicate.options.get("unique", True) else 0),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "u": rows_ptr[index].u,
                "v": rows_ptr[index].v,
                "w": rows_ptr[index].w,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_lsi_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = normalized_inputs[left_name]
    right = normalized_inputs[right_name]
    left_array = (_RtdlSegment * len(left))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in left
    ])
    right_array = (_RtdlSegment * len(right))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in right
    ])
    rows_ptr = ctypes.POINTER(_RtdlLsiRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_lsi(
        left_array,
        len(left),
        right_array,
        len(right),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "left_id": rows_ptr[index].left_id,
                "right_id": rows_ptr[index].right_id,
                "intersection_point_x": rows_ptr[index].intersection_point_x,
                "intersection_point_y": rows_ptr[index].intersection_point_y,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_pip_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    boundary_mode = compiled.refine_op.predicate.options.get("boundary_mode", "inclusive")
    if boundary_mode != "inclusive":
        raise ValueError("the current native oracle PIP runtime supports only boundary_mode='inclusive'")
    result_mode = compiled.refine_op.predicate.options.get("result_mode", "full_matrix")
    if result_mode not in {"full_matrix", "positive_hits"}:
        raise ValueError("the current native oracle PIP runtime supports only result_mode='full_matrix' or 'positive_hits'")
    points_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    points = normalized_inputs[points_name]
    polygons = normalized_inputs[polygons_name]
    point_array = (_RtdlPoint * len(points))(*[
        _RtdlPoint(item.id, item.x, item.y) for item in points
    ])
    polygon_refs, vertex_array = _encode_polygons(polygons)
    rows_ptr = ctypes.POINTER(_RtdlPipRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_pip(
        point_array,
        len(points),
        polygon_refs,
        len(polygons),
        vertex_array,
        len(vertex_array),
        1 if result_mode == "positive_hits" else 0,
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "point_id": rows_ptr[index].point_id,
                "polygon_id": rows_ptr[index].polygon_id,
                "contains": rows_ptr[index].contains,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_overlay_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left = normalized_inputs[left_name]
    right = normalized_inputs[right_name]
    left_refs, left_vertices = _encode_polygons(left)
    right_refs, right_vertices = _encode_polygons(right)
    rows_ptr = ctypes.POINTER(_RtdlOverlayRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_overlay(
        left_refs,
        len(left),
        left_vertices,
        len(left_vertices),
        right_refs,
        len(right),
        right_vertices,
        len(right_vertices),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "left_polygon_id": rows_ptr[index].left_polygon_id,
                "right_polygon_id": rows_ptr[index].right_polygon_id,
                "requires_lsi": rows_ptr[index].requires_lsi,
                "requires_pip": rows_ptr[index].requires_pip,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_ray_hitcount_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    rays_name = compiled.candidates.left.name
    triangles_name = compiled.candidates.right.name
    rays = normalized_inputs[rays_name]
    triangles = normalized_inputs[triangles_name]
    ray_array = (_RtdlRay2D * len(rays))(*[
        _RtdlRay2D(item.id, item.ox, item.oy, item.dx, item.dy, item.tmax) for item in rays
    ])
    triangle_array = (_RtdlTriangle * len(triangles))(*[
        _RtdlTriangle(item.id, item.x0, item.y0, item.x1, item.y1, item.x2, item.y2)
        for item in triangles
    ])
    rows_ptr = ctypes.POINTER(_RtdlRayHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_ray_hitcount(
        ray_array,
        len(rays),
        triangle_array,
        len(triangles),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "ray_id": rows_ptr[index].ray_id,
                "hit_count": rows_ptr[index].hit_count,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_segment_polygon_hitcount_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    segments_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    segments = normalized_inputs[segments_name]
    polygons = normalized_inputs[polygons_name]
    segment_array = (_RtdlSegment * len(segments))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments
    ])
    polygon_refs, vertex_array = _encode_polygons(polygons)
    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_segment_polygon_hitcount(
        segment_array,
        len(segments),
        polygon_refs,
        len(polygons),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "segment_id": rows_ptr[index].segment_id,
                "hit_count": rows_ptr[index].hit_count,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_segment_polygon_anyhit_rows_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    segments_name = compiled.candidates.left.name
    polygons_name = compiled.candidates.right.name
    segments = normalized_inputs[segments_name]
    polygons = normalized_inputs[polygons_name]
    segment_array = (_RtdlSegment * len(segments))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments
    ])
    polygon_refs, vertex_array = _encode_polygons(polygons)
    rows_ptr = ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_segment_polygon_anyhit_rows(
        segment_array,
        len(segments),
        polygon_refs,
        len(polygons),
        vertex_array,
        len(vertex_array),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "segment_id": rows_ptr[index].segment_id,
                "polygon_id": rows_ptr[index].polygon_id,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_polygon_pair_overlap_area_rows_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left_polygons = normalized_inputs[left_name]
    right_polygons = normalized_inputs[right_name]
    left_refs, left_vertices = _encode_polygons(left_polygons)
    right_refs, right_vertices = _encode_polygons(right_polygons)
    rows_ptr = ctypes.POINTER(_RtdlPolygonPairOverlapAreaRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_polygon_pair_overlap_area_rows(
        left_refs,
        len(left_polygons),
        left_vertices,
        len(left_vertices),
        right_refs,
        len(right_polygons),
        right_vertices,
        len(right_vertices),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "left_polygon_id": rows_ptr[index].left_polygon_id,
                "right_polygon_id": rows_ptr[index].right_polygon_id,
                "intersection_area": rows_ptr[index].intersection_area,
                "left_area": rows_ptr[index].left_area,
                "right_area": rows_ptr[index].right_area,
                "union_area": rows_ptr[index].union_area,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_polygon_set_jaccard_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    left_name = compiled.candidates.left.name
    right_name = compiled.candidates.right.name
    left_polygons = normalized_inputs[left_name]
    right_polygons = normalized_inputs[right_name]
    left_refs, left_vertices = _encode_polygons(left_polygons)
    right_refs, right_vertices = _encode_polygons(right_polygons)
    rows_ptr = ctypes.POINTER(_RtdlPolygonSetJaccardRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_polygon_set_jaccard(
        left_refs,
        len(left_polygons),
        left_vertices,
        len(left_vertices),
        right_refs,
        len(right_polygons),
        right_vertices,
        len(right_vertices),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "intersection_area": rows_ptr[index].intersection_area,
                "left_area": rows_ptr[index].left_area,
                "right_area": rows_ptr[index].right_area,
                "union_area": rows_ptr[index].union_area,
                "jaccard_similarity": rows_ptr[index].jaccard_similarity,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_point_nearest_segment_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    points_name = compiled.candidates.left.name
    segments_name = compiled.candidates.right.name
    points = normalized_inputs[points_name]
    segments = normalized_inputs[segments_name]
    point_array = (_RtdlPoint * len(points))(*[
        _RtdlPoint(item.id, item.x, item.y) for item in points
    ])
    segment_array = (_RtdlSegment * len(segments))(*[
        _RtdlSegment(item.id, item.x0, item.y0, item.x1, item.y1) for item in segments
    ])
    rows_ptr = ctypes.POINTER(_RtdlPointNearestSegmentRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    status = library.rtdl_oracle_run_point_nearest_segment(
        point_array,
        len(points),
        segment_array,
        len(segments),
        ctypes.byref(rows_ptr),
        ctypes.byref(row_count),
        error,
        len(error),
    )
    _check_status(status, error)
    try:
        return tuple(
            {
                "point_id": rows_ptr[index].point_id,
                "segment_id": rows_ptr[index].segment_id,
                "distance": rows_ptr[index].distance,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_fixed_radius_neighbors_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = normalized_inputs[query_name]
    search_points = normalized_inputs[search_name]
    rows_ptr = ctypes.POINTER(_RtdlFixedRadiusNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    radius = ctypes.c_double(float(compiled.refine_op.predicate.options["radius"]))
    k_max = ctypes.c_uint32(int(compiled.refine_op.predicate.options["k_max"]))
    if query_points and isinstance(query_points[0], Point3D):
        query_array = (_RtdlPoint3D * len(query_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_points
        ])
        search_array = (_RtdlPoint3D * len(search_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_points
        ])
        status = library.rtdl_oracle_run_fixed_radius_neighbors_3d(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        query_array = (_RtdlPoint * len(query_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in query_points
        ])
        search_array = (_RtdlPoint * len(search_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in search_points
        ])
        status = library.rtdl_oracle_run_fixed_radius_neighbors(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    try:
        return tuple(
            {
                "query_id": rows_ptr[index].query_id,
                "neighbor_id": rows_ptr[index].neighbor_id,
                "distance": rows_ptr[index].distance,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_knn_rows_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = normalized_inputs[query_name]
    search_points = normalized_inputs[search_name]
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    k = ctypes.c_uint32(int(compiled.refine_op.predicate.options["k"]))
    if query_points and isinstance(query_points[0], Point3D):
        query_array = (_RtdlPoint3D * len(query_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_points
        ])
        search_array = (_RtdlPoint3D * len(search_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_points
        ])
        status = library.rtdl_oracle_run_knn_rows_3d(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            k,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        query_array = (_RtdlPoint * len(query_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in query_points
        ])
        search_array = (_RtdlPoint * len(search_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in search_points
        ])
        status = library.rtdl_oracle_run_knn_rows(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            k,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    try:
        return tuple(
            {
                "query_id": rows_ptr[index].query_id,
                "neighbor_id": rows_ptr[index].neighbor_id,
                "distance": rows_ptr[index].distance,
                "neighbor_rank": rows_ptr[index].neighbor_rank,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _run_bounded_knn_rows_oracle(compiled: CompiledKernel, normalized_inputs, library) -> tuple[dict[str, object], ...]:
    query_name = compiled.candidates.left.name
    search_name = compiled.candidates.right.name
    query_points = normalized_inputs[query_name]
    search_points = normalized_inputs[search_name]
    rows_ptr = ctypes.POINTER(_RtdlKnnNeighborRow)()
    row_count = ctypes.c_size_t()
    error = ctypes.create_string_buffer(4096)
    radius = ctypes.c_double(float(compiled.refine_op.predicate.options["radius"]))
    k_max = ctypes.c_uint32(int(compiled.refine_op.predicate.options["k_max"]))
    if query_points and isinstance(query_points[0], Point3D):
        query_array = (_RtdlPoint3D * len(query_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in query_points
        ])
        search_array = (_RtdlPoint3D * len(search_points))(*[
            _RtdlPoint3D(item.id, item.x, item.y, item.z) for item in search_points
        ])
        status = library.rtdl_oracle_run_bounded_knn_rows_3d(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    else:
        query_array = (_RtdlPoint * len(query_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in query_points
        ])
        search_array = (_RtdlPoint * len(search_points))(*[
            _RtdlPoint(item.id, item.x, item.y) for item in search_points
        ])
        status = library.rtdl_oracle_run_bounded_knn_rows(
            query_array,
            len(query_points),
            search_array,
            len(search_points),
            radius,
            k_max,
            ctypes.byref(rows_ptr),
            ctypes.byref(row_count),
            error,
            len(error),
        )
    _check_status(status, error)
    try:
        return tuple(
            {
                "query_id": rows_ptr[index].query_id,
                "neighbor_id": rows_ptr[index].neighbor_id,
                "distance": rows_ptr[index].distance,
                "neighbor_rank": rows_ptr[index].neighbor_rank,
            }
            for index in range(row_count.value)
        )
    finally:
        library.rtdl_oracle_free_rows(rows_ptr)


def _encode_polygons(polygons):
    refs = []
    vertices = []
    offset = 0
    for polygon in polygons:
        refs.append(_RtdlPolygonRef(polygon.id, offset, len(polygon.vertices)))
        for vertex in polygon.vertices:
            vertices.extend([float(vertex[0]), float(vertex[1])])
        offset += len(polygon.vertices)
    ref_array = (_RtdlPolygonRef * len(refs))(*refs)
    vertex_array = (ctypes.c_double * len(vertices))(*vertices) if vertices else (ctypes.c_double * 0)()
    return ref_array, vertex_array


def _check_status(status: int, error=None) -> None:
    if status == 0:
        return
    if error is not None:
        message = error.value.decode("utf-8", errors="replace").strip()
    else:
        message = ""
    if not message:
        message = f"native oracle call failed with status {status}"
    raise RuntimeError(message)


def _oracle_build_help_text(*, system: str) -> str:
    if system == "Darwin":
        return (
            "Install GEOS and pkg-config so the native oracle can link successfully "
            "(for example with Homebrew: `brew install geos pkg-config`)."
        )
    if system == "Linux":
        return (
            "Install GEOS development headers and pkg-config so the native oracle can link "
            "successfully (for example `libgeos-dev` plus `pkg-config`)."
        )
    if system == "Windows":
        return (
            "Install the required native toolchain and ensure RTDL_VCVARS64 points to "
            "vcvars64.bat before building the native oracle."
        )
    return "Install the native oracle dependencies and retry."


def _raise_oracle_build_failure(
    *,
    command: list[str],
    system: str,
    error: BaseException,
) -> NoReturn:
    detail = ""
    if isinstance(error, subprocess.CalledProcessError):
        if error.stderr:
            detail = error.stderr.strip()
        elif error.stdout:
            detail = error.stdout.strip()
        else:
            detail = str(error)
    else:
        detail = str(error)

    message = [
        "RTDL native oracle build failed while preparing run_cpu(...).",
        _oracle_build_help_text(system=system),
        f"Compiler command: {subprocess.list2cmdline(command)}",
    ]
    if detail:
        message.append(f"Tool output: {detail}")
    raise RuntimeError(" ".join(message))


@functools.lru_cache(maxsize=1)
def _load_oracle_library():
    library_path = _ensure_oracle_library()
    library = ctypes.CDLL(str(library_path))
    library.rtdl_oracle_get_version.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    library.rtdl_oracle_get_version.restype = ctypes.c_int
    library.rtdl_oracle_free_rows.argtypes = [ctypes.c_void_p]
    library.rtdl_oracle_free_rows.restype = None

    library.rtdl_oracle_run_lsi.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlLsiRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_lsi.restype = ctypes.c_int

    library.rtdl_oracle_run_pip.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlPipRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_pip.restype = ctypes.c_int

    library.rtdl_oracle_run_overlay.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlOverlayRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_overlay.restype = ctypes.c_int

    library.rtdl_oracle_run_ray_hitcount.argtypes = [
        ctypes.POINTER(_RtdlRay2D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlTriangle),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlRayHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_ray_hitcount.restype = ctypes.c_int

    library.rtdl_oracle_run_segment_polygon_hitcount.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonHitCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_segment_polygon_hitcount.restype = ctypes.c_int

    library.rtdl_oracle_run_segment_polygon_anyhit_rows.argtypes = [
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlSegmentPolygonAnyHitRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_segment_polygon_anyhit_rows.restype = ctypes.c_int

    library.rtdl_oracle_run_polygon_pair_overlap_area_rows.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPolygonPairOverlapAreaRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_polygon_pair_overlap_area_rows.restype = ctypes.c_int

    library.rtdl_oracle_run_polygon_set_jaccard.argtypes = [
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPolygonRef),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPolygonSetJaccardRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_polygon_set_jaccard.restype = ctypes.c_int

    library.rtdl_oracle_run_point_nearest_segment.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlSegment),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlPointNearestSegmentRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_point_nearest_segment.restype = ctypes.c_int
    library.rtdl_oracle_run_fixed_radius_neighbors.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_fixed_radius_neighbors.restype = ctypes.c_int
    library.rtdl_oracle_run_fixed_radius_neighbors_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlFixedRadiusNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_fixed_radius_neighbors_3d.restype = ctypes.c_int
    library.rtdl_oracle_run_knn_rows.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_knn_rows.restype = ctypes.c_int
    library.rtdl_oracle_run_knn_rows_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_knn_rows_3d.restype = ctypes.c_int
    library.rtdl_oracle_run_bounded_knn_rows.argtypes = [
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_bounded_knn_rows.restype = ctypes.c_int
    library.rtdl_oracle_run_bounded_knn_rows_3d.argtypes = [
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlPoint3D),
        ctypes.c_size_t,
        ctypes.c_double,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlKnnNeighborRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_bounded_knn_rows_3d.restype = ctypes.c_int
    library.rtdl_oracle_run_bfs_expand.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlFrontierVertex),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlBfsExpandRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_bfs_expand.restype = ctypes.c_int
    library.rtdl_oracle_run_triangle_probe.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlEdgeSeed),
        ctypes.c_size_t,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.POINTER(_RtdlTriangleRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_triangle_probe.restype = ctypes.c_int
    library.rtdl_oracle_run_conjunctive_scan.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbRowIdRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_conjunctive_scan.restype = ctypes.c_int
    library.rtdl_oracle_run_grouped_count.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedCountRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_grouped_count.restype = ctypes.c_int
    library.rtdl_oracle_run_grouped_sum.argtypes = [
        ctypes.POINTER(_RtdlDbField),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbScalar),
        ctypes.c_size_t,
        ctypes.POINTER(_RtdlDbClause),
        ctypes.c_size_t,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(_RtdlDbGroupedSumRow)),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    library.rtdl_oracle_run_grouped_sum.restype = ctypes.c_int
    return library


def _ensure_oracle_library() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    build_dir = repo_root / "build"
    build_dir.mkdir(exist_ok=True)
    source_path = repo_root / "src" / "native" / "rtdl_oracle.cpp"
    source_paths = (source_path, *sorted((repo_root / "src" / "native" / "oracle").glob("*")))
    system = platform.system()
    if system == "Darwin":
        library_ext = ".dylib"
    elif system == "Windows":
        library_ext = ".dll"
    else:
        library_ext = ".so"
    library_path = build_dir / f"librtdl_oracle{library_ext}"
    if system == "Darwin":
        compiler = os.environ.get("CXX", "clang++")
        shared_flags = ["-dynamiclib", "-fPIC"]
    elif system == "Windows":
        compiler = os.environ.get("CXX", r"C:\Program Files\LLVM\bin\clang++.exe")
        shared_flags = ["-shared"]
    else:
        compiler = os.environ.get("CXX", "g++")
        shared_flags = ["-shared", "-fPIC"]
    geos_cflags = _geos_pkg_config_flags("--cflags")
    geos_libs = _geos_pkg_config_flags("--libs")
    newest_source_mtime = max(path.stat().st_mtime for path in source_paths)
    needs_build = not library_path.exists() or library_path.stat().st_mtime < newest_source_mtime
    if needs_build:
        command = [
            compiler,
            "-std=c++17",
            "-O2",
            *shared_flags,
            *geos_cflags,
            str(source_path),
            *geos_libs,
            "-o",
            str(library_path),
        ]
        if system == "Windows":
            vcvars = Path(
                os.environ.get(
                    "RTDL_VCVARS64",
                    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
                )
            )
            if not vcvars.exists():
                raise RuntimeError(
                    "Windows oracle build requires vcvars64.bat. Set RTDL_VCVARS64 to the Visual Studio Build Tools vcvars64.bat path."
                )
            try:
                _run_windows_compile(command, vcvars=vcvars, cwd=repo_root)
            except (OSError, subprocess.CalledProcessError) as exc:
                _raise_oracle_build_failure(command=command, system=system, error=exc)
        else:
            try:
                subprocess.run(command, check=True, cwd=repo_root, capture_output=True, text=True)
            except (OSError, subprocess.CalledProcessError) as exc:
                _raise_oracle_build_failure(command=command, system=system, error=exc)
    return library_path
