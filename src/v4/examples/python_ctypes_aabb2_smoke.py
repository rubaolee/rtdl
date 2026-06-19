#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

RTDL_STATUS_OK = 0
RTDL_STATUS_RESULT_TRUNCATED = 3

RTDL_BACKEND_CPU = 1
RTDL_DEVICE_HOST = 0
RTDL_DTYPE_U64 = 3
RTDL_DTYPE_F32 = 6
RTDL_PRIMITIVE_AABB2 = 1
RTDL_QUERY_AABB_OVERLAP = 1
RTDL_OUTPUT_RTDL_OWNED_RESULT = 1
RTDL_OUTPUT_CALLER_PROVIDED_BUFFER = 2
RTDL_OWNERSHIP_BORROWED = 1


ReleaseFn = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
Int64x8 = ctypes.c_int64 * 8


class ExternalRuntimeDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("device_type", ctypes.c_int),
        ("device_id", ctypes.c_int32),
        ("context", ctypes.c_void_p),
        ("stream", ctypes.c_void_p),
        ("stream_mode", ctypes.c_int),
        ("user_data", ctypes.c_void_p),
    ]


class ContextDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("requested_abi_major", ctypes.c_uint32),
        ("requested_abi_minor", ctypes.c_uint32),
        ("requested_abi_patch", ctypes.c_uint32),
        ("backend", ctypes.c_int),
        ("external_runtime", ExternalRuntimeDesc),
        ("user_data", ctypes.c_void_p),
    ]


class RouteDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("primitive_kind", ctypes.c_int),
        ("query_kind", ctypes.c_int),
        ("backend", ctypes.c_int),
        ("device_type", ctypes.c_int),
        ("dtype", ctypes.c_int),
    ]


class BufferDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("data", ctypes.c_void_p),
        ("byte_count", ctypes.c_uint64),
        ("device_type", ctypes.c_int),
        ("device_id", ctypes.c_int32),
        ("dtype", ctypes.c_int),
        ("ndim", ctypes.c_uint32),
        ("shape", Int64x8),
        ("strides", Int64x8),
        ("ownership", ctypes.c_int),
        ("release", ReleaseFn),
        ("user_data", ctypes.c_void_p),
        ("flags", ctypes.c_uint64),
        ("producer_object", ctypes.c_void_p),
    ]


class IndexDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("primitive_kind", ctypes.c_int),
        ("primitives", ctypes.c_void_p),
        ("primitive_count", ctypes.c_uint64),
    ]


class OutputDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("mode", ctypes.c_int),
        ("caller_buffer", BufferDesc),
        ("capacity_count", ctypes.c_uint64),
        ("required_count_out", ctypes.POINTER(ctypes.c_uint64)),
        ("written_count_out", ctypes.POINTER(ctypes.c_uint64)),
    ]


class QueryDesc(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_size_t),
        ("query_kind", ctypes.c_int),
        ("inputs", ctypes.c_void_p),
        ("input_count", ctypes.c_uint64),
        ("output", OutputDesc),
    ]


def _load(library: Path) -> ctypes.CDLL:
    lib = ctypes.CDLL(str(library))
    lib.rtdl_context_create.argtypes = [ctypes.POINTER(ContextDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_context_create.restype = ctypes.c_int
    lib.rtdl_context_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_buffer_import.argtypes = [ctypes.c_void_p, ctypes.POINTER(BufferDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_buffer_import.restype = ctypes.c_int
    lib.rtdl_buffer_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_index_build.argtypes = [ctypes.c_void_p, ctypes.POINTER(IndexDesc), ctypes.POINTER(ctypes.c_void_p)]
    lib.rtdl_index_build.restype = ctypes.c_int
    lib.rtdl_index_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_query_plan_create.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(RouteDesc),
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    lib.rtdl_query_plan_create.restype = ctypes.c_int
    lib.rtdl_query_plan_destroy.argtypes = [ctypes.c_void_p]
    lib.rtdl_query_execute.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(QueryDesc),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    lib.rtdl_query_execute.restype = ctypes.c_int
    lib.rtdl_result_row_count.argtypes = [ctypes.c_void_p]
    lib.rtdl_result_row_count.restype = ctypes.c_uint64
    lib.rtdl_result_get_buffer.argtypes = [ctypes.c_void_p, ctypes.POINTER(BufferDesc)]
    lib.rtdl_result_get_buffer.restype = ctypes.c_int
    lib.rtdl_result_destroy.argtypes = [ctypes.c_void_p]
    return lib


def _host_buffer(array: ctypes.Array, dtype: int, rows: int, cols: int, item_size: int) -> BufferDesc:
    desc = BufferDesc()
    desc.struct_size = ctypes.sizeof(BufferDesc)
    desc.data = ctypes.cast(array, ctypes.c_void_p)
    desc.byte_count = ctypes.sizeof(array)
    desc.device_type = RTDL_DEVICE_HOST
    desc.device_id = 0
    desc.dtype = dtype
    desc.ndim = 2
    desc.shape = Int64x8(rows, cols, 0, 0, 0, 0, 0, 0)
    desc.strides = Int64x8(cols * item_size, item_size, 0, 0, 0, 0, 0, 0)
    desc.ownership = RTDL_OWNERSHIP_BORROWED
    return desc


def _pairs_from_desc(desc: BufferDesc, row_count: int) -> list[list[int]]:
    if row_count == 0:
        return []
    raw = ctypes.cast(desc.data, ctypes.POINTER(ctypes.c_uint64 * (row_count * 2))).contents
    values = list(raw)
    return [[int(values[i]), int(values[i + 1])] for i in range(0, len(values), 2)]


def _check(status: int, expected: int, label: str) -> None:
    if status != expected:
        raise RuntimeError(f"{label}: expected status {expected}, got {status}")


def run(library: Path) -> dict[str, object]:
    lib = _load(library)
    context = ctypes.c_void_p()
    context_desc = ContextDesc()
    context_desc.struct_size = ctypes.sizeof(ContextDesc)
    context_desc.requested_abi_major = 0
    context_desc.requested_abi_minor = 2
    context_desc.requested_abi_patch = 0
    context_desc.backend = RTDL_BACKEND_CPU
    _check(lib.rtdl_context_create(ctypes.byref(context_desc), ctypes.byref(context)), RTDL_STATUS_OK, "context")

    primitives_array = (ctypes.c_float * 8)(0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0)
    queries_array = (
        ctypes.c_float * 12
    )(0.5, 0.5, 0.6, 0.6, 2.5, 2.5, 2.6, 2.6, 0.0, 0.0, 3.0, 3.0)

    primitives_buffer = ctypes.c_void_p()
    queries_buffer = ctypes.c_void_p()
    primitive_desc = _host_buffer(primitives_array, RTDL_DTYPE_F32, 2, 4, ctypes.sizeof(ctypes.c_float))
    query_buffer_desc = _host_buffer(queries_array, RTDL_DTYPE_F32, 3, 4, ctypes.sizeof(ctypes.c_float))
    _check(lib.rtdl_buffer_import(context, ctypes.byref(primitive_desc), ctypes.byref(primitives_buffer)), RTDL_STATUS_OK, "primitive import")
    _check(lib.rtdl_buffer_import(context, ctypes.byref(query_buffer_desc), ctypes.byref(queries_buffer)), RTDL_STATUS_OK, "query import")

    index = ctypes.c_void_p()
    index_desc = IndexDesc(ctypes.sizeof(IndexDesc), RTDL_PRIMITIVE_AABB2, primitives_buffer, 2)
    _check(lib.rtdl_index_build(context, ctypes.byref(index_desc), ctypes.byref(index)), RTDL_STATUS_OK, "index")

    route = RouteDesc(
        ctypes.sizeof(RouteDesc),
        RTDL_PRIMITIVE_AABB2,
        RTDL_QUERY_AABB_OVERLAP,
        RTDL_BACKEND_CPU,
        RTDL_DEVICE_HOST,
        RTDL_DTYPE_F32,
    )
    plan = ctypes.c_void_p()
    _check(lib.rtdl_query_plan_create(context, ctypes.byref(route), index, ctypes.byref(plan)), RTDL_STATUS_OK, "plan")

    result = ctypes.c_void_p()
    owned_query = QueryDesc()
    owned_query.struct_size = ctypes.sizeof(QueryDesc)
    owned_query.query_kind = RTDL_QUERY_AABB_OVERLAP
    owned_query.inputs = queries_buffer
    owned_query.input_count = 3
    owned_query.output.struct_size = ctypes.sizeof(OutputDesc)
    owned_query.output.mode = RTDL_OUTPUT_RTDL_OWNED_RESULT
    _check(lib.rtdl_query_execute(context, plan, ctypes.byref(owned_query), ctypes.byref(result)), RTDL_STATUS_OK, "owned query")
    owned_count = int(lib.rtdl_result_row_count(result))
    owned_desc = BufferDesc()
    _check(lib.rtdl_result_get_buffer(result, ctypes.byref(owned_desc)), RTDL_STATUS_OK, "result export")
    owned_pairs = _pairs_from_desc(owned_desc, owned_count)

    required = ctypes.c_uint64(0)
    written = ctypes.c_uint64(0)
    truncated_array = (ctypes.c_uint64 * 2)()
    truncated_query = QueryDesc()
    truncated_query.struct_size = ctypes.sizeof(QueryDesc)
    truncated_query.query_kind = RTDL_QUERY_AABB_OVERLAP
    truncated_query.inputs = queries_buffer
    truncated_query.input_count = 3
    truncated_query.output.struct_size = ctypes.sizeof(OutputDesc)
    truncated_query.output.mode = RTDL_OUTPUT_CALLER_PROVIDED_BUFFER
    truncated_query.output.caller_buffer = _host_buffer(truncated_array, RTDL_DTYPE_U64, 1, 2, ctypes.sizeof(ctypes.c_uint64))
    truncated_query.output.capacity_count = 1
    truncated_query.output.required_count_out = ctypes.pointer(required)
    truncated_query.output.written_count_out = ctypes.pointer(written)
    truncated_status = lib.rtdl_query_execute(context, plan, ctypes.byref(truncated_query), None)
    _check(truncated_status, RTDL_STATUS_RESULT_TRUNCATED, "truncated query")

    exact_required = ctypes.c_uint64(0)
    exact_written = ctypes.c_uint64(0)
    exact_array = (ctypes.c_uint64 * (owned_count * 2))()
    exact_query = QueryDesc()
    exact_query.struct_size = ctypes.sizeof(QueryDesc)
    exact_query.query_kind = RTDL_QUERY_AABB_OVERLAP
    exact_query.inputs = queries_buffer
    exact_query.input_count = 3
    exact_query.output.struct_size = ctypes.sizeof(OutputDesc)
    exact_query.output.mode = RTDL_OUTPUT_CALLER_PROVIDED_BUFFER
    exact_query.output.caller_buffer = _host_buffer(exact_array, RTDL_DTYPE_U64, owned_count, 2, ctypes.sizeof(ctypes.c_uint64))
    exact_query.output.capacity_count = owned_count
    exact_query.output.required_count_out = ctypes.pointer(exact_required)
    exact_query.output.written_count_out = ctypes.pointer(exact_written)
    _check(lib.rtdl_query_execute(context, plan, ctypes.byref(exact_query), None), RTDL_STATUS_OK, "exact query")
    exact_pairs = [[int(exact_array[i]), int(exact_array[i + 1])] for i in range(0, len(exact_array), 2)]

    expected = [[0, 0], [1, 1], [2, 0], [2, 1]]
    if owned_pairs != expected or exact_pairs != expected:
        raise RuntimeError(f"unexpected pairs: owned={owned_pairs}, exact={exact_pairs}")

    lib.rtdl_result_destroy(result)
    lib.rtdl_query_plan_destroy(plan)
    lib.rtdl_index_destroy(index)
    lib.rtdl_buffer_destroy(queries_buffer)
    lib.rtdl_buffer_destroy(primitives_buffer)
    lib.rtdl_context_destroy(context)

    return {
        "library": str(library),
        "route": "host_f32_aabb2_overlap",
        "owned_result": {"row_count": owned_count, "pairs": owned_pairs},
        "caller_output_truncated": {
            "status": truncated_status,
            "required_count": int(required.value),
            "written_count": int(written.value),
            "pairs": [[int(truncated_array[0]), int(truncated_array[1])]],
        },
        "caller_output_exact": {
            "required_count": int(exact_required.value),
            "written_count": int(exact_written.value),
            "pairs": exact_pairs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=ROOT / "build" / "librtdl_v4_c_api.so")
    args = parser.parse_args()
    print(json.dumps(run(args.library), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
