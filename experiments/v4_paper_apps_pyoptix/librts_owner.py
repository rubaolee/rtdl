"""Competent public-PyOptiX count owner for the LibRTS paper-app stage."""

from __future__ import annotations

import ctypes
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Self

import numpy as np

from .public_runtime import (
    PublicRuntime,
    build_pipeline,
    compile_ptx,
    copy_params_and_launch,
    load_runtime,
    make_context,
    make_sbt,
    pinned_array,
)

DEVICE_SOURCE = Path(__file__).with_name("librts_device.cu")
OPERATION_CODES = {"point_contains": 1, "range_contains": 2}
PARAM_DTYPE = np.dtype(
    {
        "names": (
            "traversable",
            "indexed_min_x",
            "indexed_min_y",
            "indexed_max_x",
            "indexed_max_y",
            "query_min_x",
            "query_min_y",
            "query_max_x",
            "query_max_y",
            "query_counts",
            "status",
            "indexed_count",
            "query_count",
            "operation",
            "reserved",
        ),
        "formats": (
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u8",
            "u4",
            "u4",
            "u4",
            "u4",
        ),
        "align": True,
    }
)
if PARAM_DTYPE.itemsize != 104:
    raise RuntimeError(f"LibRTS PyOptiX parameter ABI drift: {PARAM_DTYPE.itemsize}")


@dataclass(frozen=True, slots=True)
class LibRTSCountResult:
    operation: str
    checked_u64: int
    query_count: int
    indexed_count: int
    device_status: int


@dataclass(frozen=True, slots=True)
class LibRTSStreamCountResult:
    operation: str
    checked_u64: int
    query_count: int
    indexed_count: int
    chunk_rows: int
    chunk_counts: tuple[int, ...]
    device_statuses: tuple[int, ...]


def _as_f32_column(label: str, value: Any, count: int | None = None) -> np.ndarray:
    result = np.ascontiguousarray(np.asarray(value, dtype=np.float32))
    if result.ndim != 1 or (count is not None and result.size != count):
        raise ValueError(f"{label} must be a one-dimensional column of length {count}")
    if not bool(np.isfinite(result).all()):
        raise ValueError(f"{label} contains nonfinite values")
    return result


def normalize_indexed_columns(indexed_columns: Any) -> tuple[np.ndarray, ...]:
    required = ("min_x", "min_y", "max_x", "max_y")
    if isinstance(indexed_columns, Mapping):
        values = indexed_columns
    elif all(hasattr(indexed_columns, name) for name in required):
        values = {name: getattr(indexed_columns, name) for name in required}
    else:
        raise TypeError("indexed_columns must expose min_x/min_y/max_x/max_y")
    minimum_x = _as_f32_column("indexed.min_x", values["min_x"])
    count = int(minimum_x.size)
    if count <= 0 or count > 0xFFFFFFFF:
        raise ValueError("indexed box cardinality is outside nonzero U32")
    minimum_y = _as_f32_column("indexed.min_y", values["min_y"], count)
    maximum_x = _as_f32_column("indexed.max_x", values["max_x"], count)
    maximum_y = _as_f32_column("indexed.max_y", values["max_y"], count)
    if bool((maximum_x < minimum_x).any()) or bool((maximum_y < minimum_y).any()):
        raise ValueError("indexed box bounds are inverted after float32 lowering")
    return minimum_x, minimum_y, maximum_x, maximum_y


def normalize_queries(
    operation: str, queries: Iterable[Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if operation not in OPERATION_CODES:
        raise ValueError("LibRTS operation must be point_contains or range_contains")
    rows = tuple(queries)
    if not rows or len(rows) > 0xFFFFFFFF:
        raise ValueError("LibRTS query cardinality is outside nonzero U32")
    if operation == "point_contains":
        values = np.asarray(rows, dtype=np.float64)
        if values.shape != (len(rows), 2):
            raise ValueError("point_contains queries must be XY pairs")
        minimum_x = maximum_x = _as_f32_column("query.x", values[:, 0])
        minimum_y = maximum_y = _as_f32_column("query.y", values[:, 1])
    else:
        values = np.asarray(rows, dtype=np.float64)
        if values.shape != (len(rows), 4):
            raise ValueError("range_contains queries must be minx/miny/maxx/maxy rows")
        minimum_x = _as_f32_column("query.min_x", values[:, 0])
        minimum_y = _as_f32_column("query.min_y", values[:, 1])
        maximum_x = _as_f32_column("query.max_x", values[:, 2])
        maximum_y = _as_f32_column("query.max_y", values[:, 3])
        if bool((maximum_x < minimum_x).any()) or bool((maximum_y < minimum_y).any()):
            raise ValueError("range_contains query bounds are inverted")
    return minimum_x, minimum_y, maximum_x, maximum_y


class PublicPyOptixLibRTSCountOwner:
    """Retains the 11M-box GAS and executes point/range containment batches."""

    def __init__(
        self,
        *,
        runtime: PublicRuntime,
        context: Any,
        module: Any,
        pipeline: Any,
        groups: tuple[Any, Any, Any],
        sbt: Any,
        sbt_keepalive: Any,
        indexed_device: tuple[Any, ...],
        traversable: int,
        gas_keepalive: tuple[Any, ...],
        ptx: bytes,
    ) -> None:
        self.runtime = runtime
        self.context = context
        self.module = module
        self.pipeline = pipeline
        self.groups = groups
        self.sbt = sbt
        self.sbt_keepalive = sbt_keepalive
        self.indexed_device = indexed_device
        self.indexed_count = int(indexed_device[0].size)
        self.traversable = int(traversable)
        self.gas_keepalive = gas_keepalive
        self.ptx = ptx
        self.stream = runtime.cp.cuda.Stream(non_blocking=True)
        self.host_params, self.host_params_keepalive = pinned_array(
            runtime, (1,), PARAM_DTYPE
        )
        self.host_total, self.host_total_keepalive = pinned_array(
            runtime, (1,), np.dtype(np.uint64)
        )
        self.host_status, self.host_status_keepalive = pinned_array(
            runtime, (1,), np.dtype(np.uint32)
        )
        self.device_params = runtime.cp.cuda.alloc(PARAM_DTYPE.itemsize)
        self.query_operation: str | None = None
        self.query_device: tuple[Any, ...] = ()
        self.query_count = 0
        self.query_counts = None
        self.query_status = None
        self.query_layout: str | None = None
        self._closed = False

    @classmethod
    def prepare(
        cls,
        indexed_columns: Any,
        *,
        prebuilt_ptx: bytes | None = None,
        optix_include: str | Path | None = None,
        cuda_include: str | Path | None = None,
        compute_capability: tuple[int, int] | None = None,
        runtime: PublicRuntime | None = None,
    ) -> PublicPyOptixLibRTSCountOwner:
        runtime = load_runtime() if runtime is None else runtime
        if prebuilt_ptx is None:
            if (
                optix_include is None
                or cuda_include is None
                or compute_capability is None
            ):
                raise ValueError(
                    "PTX compilation requires include paths and compute capability"
                )
            prebuilt_ptx = compile_ptx(
                runtime,
                DEVICE_SOURCE,
                optix_include=optix_include,
                cuda_include=cuda_include,
                compute_capability=compute_capability,
            )
        if (
            not isinstance(prebuilt_ptx, bytes)
            or b".version" not in prebuilt_ptx[:4096]
        ):
            raise ValueError("LibRTS owner requires nonempty prebuilt PTX bytes")
        context = make_context(runtime)
        pipeline, groups, module, _ = build_pipeline(
            runtime,
            context,
            prebuilt_ptx,
            raygen_entry="__raygen__paper_librts_count",
            miss_entry="__miss__paper_librts_count",
            intersection_entry="__intersection__paper_librts_count",
            custom_primitive=True,
        )
        sbt, sbt_keepalive = make_sbt(runtime, groups)
        cp = runtime.cp
        stream = cp.cuda.Stream(non_blocking=True)
        indexed_host = normalize_indexed_columns(indexed_columns)
        with stream:
            indexed_device = tuple(cp.asarray(column) for column in indexed_host)
            aabbs = cp.stack(
                (
                    cp.minimum(indexed_device[0], indexed_device[2])
                    - cp.float32(1.0e-6),
                    cp.minimum(indexed_device[1], indexed_device[3])
                    - cp.float32(1.0e-6),
                    cp.full(indexed_host[0].size, -1.0e-4, dtype=cp.float32),
                    cp.maximum(indexed_device[0], indexed_device[2])
                    + cp.float32(1.0e-6),
                    cp.maximum(indexed_device[1], indexed_device[3])
                    + cp.float32(1.0e-6),
                    cp.full(indexed_host[0].size, 1.0e-4, dtype=cp.float32),
                ),
                axis=1,
            )
            build_input = runtime.optix.BuildInputCustomPrimitiveArray(
                aabbBuffers=[int(aabbs.data.ptr)],
                numPrimitives=int(indexed_host[0].size),
                flags=[runtime.optix.GEOMETRY_FLAG_NONE],
                numSbtRecords=1,
            )
            options = runtime.optix.AccelBuildOptions(
                buildFlags=int(runtime.optix.BUILD_FLAG_PREFER_FAST_TRACE),
                operation=runtime.optix.BUILD_OPERATION_BUILD,
            )
            sizes = context.accelComputeMemoryUsage([options], [build_input])
            temporary = cp.cuda.alloc(int(sizes.tempSizeInBytes))
            output = cp.cuda.alloc(int(sizes.outputSizeInBytes))
            traversable = context.accelBuild(
                int(stream.ptr),
                [options],
                [build_input],
                int(temporary.ptr),
                int(sizes.tempSizeInBytes),
                int(output.ptr),
                int(sizes.outputSizeInBytes),
                [],
            )
        stream.synchronize()
        return cls(
            runtime=runtime,
            context=context,
            module=module,
            pipeline=pipeline,
            groups=groups,
            sbt=sbt,
            sbt_keepalive=sbt_keepalive,
            indexed_device=indexed_device,
            traversable=int(traversable),
            gas_keepalive=(aabbs, temporary, output, build_input),
            ptx=prebuilt_ptx,
        )

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("LibRTS PyOptiX owner is closed")

    def bind_queries(self, *, operation: str, queries: Iterable[Any]) -> None:
        """Retain one normalized device query batch for prepared replay."""

        self._guard()
        if self.query_operation is not None:
            raise RuntimeError("LibRTS PyOptiX queries are already bound")
        query_host = normalize_queries(operation, queries)
        query_count = int(query_host[0].size)
        cp = self.runtime.cp
        with self.stream:
            self.query_device = tuple(cp.asarray(column) for column in query_host)
            self.query_counts = cp.zeros(query_count, dtype=cp.uint32)
            self.query_status = cp.zeros(1, dtype=cp.uint32)
        self.stream.synchronize()
        self.query_operation = operation
        self.query_count = query_count
        self.query_layout = "legacy_python_rows"

    def bind_query_columns(
        self, *, operation: str, columns: Mapping[str, Any],
    ) -> None:
        """Retain one typed float32 query-column batch for prepared replay."""

        self._guard()
        if self.query_operation is not None:
            raise RuntimeError("LibRTS PyOptiX queries are already bound")
        if operation not in OPERATION_CODES:
            raise ValueError("LibRTS operation must be point_contains or range_contains")
        names = (
            ("x", "y")
            if operation == "point_contains"
            else ("min_x", "min_y", "max_x", "max_y")
        )
        if set(columns) != set(names):
            raise ValueError(f"{operation} query columns must be exactly {names!r}")
        query_host = tuple(_as_f32_column(name, columns[name]) for name in names)
        query_count = int(query_host[0].size)
        if query_count <= 0 or query_count > 0xFFFFFFFF:
            raise ValueError("LibRTS query cardinality is outside nonzero U32")
        if any(int(column.size) != query_count for column in query_host):
            raise ValueError("LibRTS query columns have unequal lengths")
        if operation != "point_contains":
            if bool((query_host[2] < query_host[0]).any()) or bool(
                (query_host[3] < query_host[1]).any()
            ):
                raise ValueError("range_contains query column bounds are inverted")
        cp = self.runtime.cp
        with self.stream:
            uploaded = tuple(cp.asarray(column) for column in query_host)
            self.query_device = (
                (uploaded[0], uploaded[1], uploaded[0], uploaded[1])
                if operation == "point_contains"
                else uploaded
            )
            self.query_counts = cp.zeros(query_count, dtype=cp.uint32)
            self.query_status = cp.zeros(1, dtype=cp.uint32)
        self.stream.synchronize()
        self.query_operation = operation
        self.query_count = query_count
        self.query_layout = "device_f32_soa"

    def execute_count(
        self,
        *,
        operation: str | None = None,
        queries: Iterable[Any] | None = None,
        expected_count: int | None = None,
    ) -> LibRTSCountResult:
        self._guard()
        cp = self.runtime.cp
        if self.query_operation is not None:
            if queries is not None:
                raise ValueError("bound PyOptiX queries reject per-execution inputs")
            if operation is not None and operation != self.query_operation:
                raise ValueError("bound PyOptiX query operation differs")
            operation = self.query_operation
            query_device = self.query_device
            query_count = self.query_count
            counts = self.query_counts
            status = self.query_status
        else:
            if operation is None or queries is None:
                raise ValueError("unbound PyOptiX execution requires operation and queries")
            query_host = normalize_queries(operation, queries)
            query_count = int(query_host[0].size)
            query_device = tuple(cp.asarray(column) for column in query_host)
            counts = cp.zeros(query_count, dtype=cp.uint32)
            status = cp.zeros(1, dtype=cp.uint32)
        assert operation is not None and counts is not None and status is not None
        with self.stream:
            counts.fill(0)
            status.fill(0)
            params = self.host_params[0]
            params["traversable"] = np.uint64(self.traversable)
            for name, column in zip(
                ("indexed_min_x", "indexed_min_y", "indexed_max_x", "indexed_max_y"),
                self.indexed_device,
            ):
                params[name] = np.uint64(column.data.ptr)
            for name, column in zip(
                ("query_min_x", "query_min_y", "query_max_x", "query_max_y"),
                query_device,
            ):
                params[name] = np.uint64(column.data.ptr)
            params["query_counts"] = np.uint64(counts.data.ptr)
            params["status"] = np.uint64(status.data.ptr)
            params["indexed_count"] = np.uint32(self.indexed_count)
            params["query_count"] = np.uint32(query_count)
            params["operation"] = np.uint32(OPERATION_CODES[operation])
            params["reserved"] = np.uint32(0)
            copy_params_and_launch(
                self.runtime,
                pipeline=self.pipeline,
                sbt=self.sbt,
                stream=self.stream,
                params=self.host_params,
                device_params=self.device_params,
                width=query_count,
            )
            total = cp.sum(counts, dtype=cp.uint64)
            total.data.copy_to_host_async(
                ctypes.c_void_p(int(self.host_total.ctypes.data)),
                int(self.host_total.nbytes),
                self.stream,
            )
            status.data.copy_to_host_async(
                ctypes.c_void_p(int(self.host_status.ctypes.data)),
                int(self.host_status.nbytes),
                self.stream,
            )
        self.stream.synchronize()
        observed_status = int(self.host_status[0])
        if observed_status:
            raise RuntimeError(
                f"LibRTS PyOptiX device status failed: {observed_status}"
            )
        value = int(self.host_total[0])
        if expected_count is not None and value != int(expected_count):
            raise RuntimeError(
                f"LibRTS PyOptiX oracle mismatch: expected={expected_count} observed={value}"
            )
        return LibRTSCountResult(
            operation=operation,
            checked_u64=value,
            query_count=query_count,
            indexed_count=self.indexed_count,
            device_status=observed_status,
        )

    def _release_query_batch(self) -> None:
        self.query_operation = None
        self.query_device = ()
        self.query_count = 0
        self.query_layout = None
        self.query_counts = None
        self.query_status = None

    def execute_count_query_column_stream(
        self,
        *,
        operation: str,
        columns: Mapping[str, Any],
        chunk_rows: int,
        expected_count: int | None = None,
    ) -> LibRTSStreamCountResult:
        """Execute one logical column batch through bounded device chunks."""

        self._guard()
        if self.query_operation is not None:
            raise RuntimeError("streamed queries require no bound query batch")
        if isinstance(chunk_rows, bool) or not isinstance(chunk_rows, int) \
                or not 0 < chunk_rows <= 0xFFFFFFFF:
            raise ValueError("chunk_rows must be inside nonzero U32")
        names = (
            ("x", "y")
            if operation == "point_contains"
            else ("min_x", "min_y", "max_x", "max_y")
        )
        if operation not in OPERATION_CODES or set(columns) != set(names):
            raise ValueError("streamed query columns do not match the operation")
        query_count = len(columns[names[0]])
        if query_count <= 0 or any(len(columns[name]) != query_count for name in names):
            raise ValueError("query-column stream must contain equal nonempty columns")

        total = 0
        chunk_counts = []
        statuses = []
        for start in range(0, query_count, chunk_rows):
            stop = min(start + chunk_rows, query_count)
            chunk = {name: columns[name][start:stop] for name in names}
            try:
                self.bind_query_columns(operation=operation, columns=chunk)
                if self.query_layout != "device_f32_soa" \
                        or self.query_count != stop - start:
                    raise RuntimeError("streamed query preparation returned an invalid layout")
                result = self.execute_count(operation=operation)
            finally:
                self._release_query_batch()
            value = int(result.checked_u64)
            if value < 0 or total > 0xFFFFFFFFFFFFFFFF - value:
                raise OverflowError("streamed LibRTS count exceeds U64")
            total += value
            chunk_counts.append(value)
            statuses.append(int(result.device_status))
        if expected_count is not None and total != int(expected_count):
            raise RuntimeError(
                f"LibRTS PyOptiX stream oracle mismatch: "
                f"expected={expected_count} observed={total}"
            )
        return LibRTSStreamCountResult(
            operation=operation,
            checked_u64=total,
            query_count=query_count,
            indexed_count=self.indexed_count,
            chunk_rows=chunk_rows,
            chunk_counts=tuple(chunk_counts),
            device_statuses=tuple(statuses),
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.stream = None
        self.device_params = None
        self._release_query_batch()
        self.host_params_keepalive = None
        self.host_params = None
        self.host_total_keepalive = None
        self.host_total = None
        self.host_status_keepalive = None
        self.host_status = None
        self.gas_keepalive = ()
        self.indexed_device = ()
        self.sbt_keepalive = None
        self.sbt = None
        self.groups = ()
        self.pipeline = None
        self.module = None
        self.context = None

    def __enter__(self) -> Self:
        self._guard()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


__all__ = [
    "DEVICE_SOURCE",
    "PARAM_DTYPE",
    "LibRTSCountResult",
    "LibRTSStreamCountResult",
    "PublicPyOptixLibRTSCountOwner",
    "normalize_indexed_columns",
    "normalize_queries",
]
