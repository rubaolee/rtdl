"""Competent public-PyOptiX owner for the real RT-Graph RT-2A1 app stage."""

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

DEVICE_SOURCE = Path(__file__).with_name("triangle_counting_device.cu")
UINT64_MAX = (1 << 64) - 1
PARAM_DTYPE = np.dtype(
    {
        "names": (
            "traversable",
            "rays",
            "weights",
            "weighted_sum",
            "status",
            "query_count",
            "tmin",
            "tmax",
        ),
        "formats": ("u8", "u8", "u8", "u8", "u8", "u4", "f4", "f4"),
        "offsets": (0, 8, 16, 24, 32, 40, 44, 48),
        "itemsize": 56,
        "align": True,
    }
)
if PARAM_DTYPE.itemsize != 56:
    raise RuntimeError(f"triangle PyOptiX parameter ABI drift: {PARAM_DTYPE.itemsize}")


@dataclass(frozen=True, slots=True)
class TriangleSegmentResult:
    checked_u64: int
    query_count: int
    primitive_count: int
    device_status: int


def _required_columns(
    label: str, columns: Mapping[str, Any], required: Iterable[str]
) -> int:
    names = tuple(required)
    missing = [name for name in names if name not in columns]
    if missing:
        raise ValueError(f"{label} lacks columns: {', '.join(missing)}")
    lengths = {int(columns[name].size) for name in names}
    if len(lengths) != 1:
        raise ValueError(f"{label} columns have unequal lengths")
    count = lengths.pop()
    if count <= 0 or count > 0xFFFFFFFF:
        raise ValueError(f"{label} cardinality is outside nonzero U32")
    return count


class PublicPyOptixTriangleCountingOwner:
    """Retains public OptiX program objects; each app segment owns a new GAS."""

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
        ptx: bytes,
    ) -> None:
        self.runtime = runtime
        self.context = context
        self.module = module
        self.pipeline = pipeline
        self.groups = groups
        self.sbt = sbt
        self.sbt_keepalive = sbt_keepalive
        self.ptx = ptx
        self.stream = runtime.cp.cuda.Stream(non_blocking=True)
        self.device_params = runtime.cp.cuda.alloc(PARAM_DTYPE.itemsize)
        self.host_params, self.host_params_keepalive = pinned_array(
            runtime, (1,), PARAM_DTYPE
        )
        self.host_weighted_sum, self.host_weighted_sum_keepalive = pinned_array(
            runtime, (1,), np.dtype(np.uint64)
        )
        self.host_status, self.host_status_keepalive = pinned_array(
            runtime, (1,), np.dtype(np.uint32)
        )
        self._closed = False

    @classmethod
    def prepare(
        cls,
        *,
        prebuilt_ptx: bytes | None = None,
        optix_include: str | Path | None = None,
        cuda_include: str | Path | None = None,
        compute_capability: tuple[int, int] | None = None,
        runtime: PublicRuntime | None = None,
    ) -> PublicPyOptixTriangleCountingOwner:
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
            raise ValueError("triangle owner requires nonempty prebuilt PTX bytes")
        context = make_context(runtime)
        pipeline, groups, module, _ = build_pipeline(
            runtime,
            context,
            prebuilt_ptx,
            raygen_entry="__raygen__paper_triangle_count",
            miss_entry="__miss__paper_triangle_count",
            any_hit_entry="__anyhit__paper_triangle_count",
            custom_primitive=False,
        )
        sbt, keepalive = make_sbt(runtime, groups)
        return cls(
            runtime=runtime,
            context=context,
            module=module,
            pipeline=pipeline,
            groups=groups,
            sbt=sbt,
            sbt_keepalive=keepalive,
            ptx=prebuilt_ptx,
        )

    def _guard(self) -> None:
        if self._closed:
            raise RuntimeError("triangle PyOptiX owner is closed")

    def _build_gas(
        self, vertices: Any, primitive_count: int
    ) -> tuple[int, tuple[Any, ...]]:
        optix = self.runtime.optix
        build_input = optix.BuildInputTriangleArray()
        build_input.vertexFormat = optix.VERTEX_FORMAT_FLOAT3
        build_input.vertexStrideInBytes = 12
        build_input.numVertices = primitive_count * 3
        build_input.vertexBuffers = [int(vertices.data.ptr)]
        single_any_hit = getattr(
            optix, "GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL", None
        )
        if single_any_hit is None:
            raise RuntimeError(
                "public PyOptiX lacks required single-any-hit geometry delivery"
            )
        build_input.flags = [single_any_hit]
        build_input.numSbtRecords = 1
        options = optix.AccelBuildOptions(
            buildFlags=int(optix.BUILD_FLAG_PREFER_FAST_TRACE),
            operation=optix.BUILD_OPERATION_BUILD,
        )
        sizes = self.context.accelComputeMemoryUsage([options], [build_input])
        temporary = self.runtime.cp.cuda.alloc(int(sizes.tempSizeInBytes))
        output = self.runtime.cp.cuda.alloc(int(sizes.outputSizeInBytes))
        handle = self.context.accelBuild(
            int(self.stream.ptr),
            [options],
            [build_input],
            int(temporary.ptr),
            int(sizes.tempSizeInBytes),
            int(output.ptr),
            int(sizes.outputSizeInBytes),
            [],
        )
        return int(handle), (vertices, temporary, output, build_input)

    def execute_segment(
        self,
        triangles: Mapping[str, Any],
        rays: Mapping[str, Any],
        *,
        ray_weights: Any,
        tmin: float = 0.0,
        tmax: float = 0.2,
    ) -> TriangleSegmentResult:
        self._guard()
        cp = self.runtime.cp
        primitive_count = _required_columns(
            "triangles",
            triangles,
            ("x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2"),
        )
        query_count = _required_columns(
            "rays", rays, ("ox", "oy", "oz", "dx", "dy", "dz", "tmax")
        )
        if ray_weights is None or int(ray_weights.size) != query_count:
            raise ValueError("RT-2A1 requires one U64 weight per ray")
        if not np.isfinite(tmin) or not np.isfinite(tmax) or not (0.0 <= tmin < tmax):
            raise ValueError("triangle trace interval is invalid")

        with self.stream:
            vertices = (
                cp.stack(
                    tuple(
                        triangles[name]
                        for corner in range(3)
                        for name in (f"x{corner}", f"y{corner}", f"z{corner}")
                    ),
                    axis=1,
                )
                .astype(cp.float32, copy=False)
                .reshape((-1, 3))
            )
            ray_rows = cp.stack(
                tuple(
                    rays[name] for name in ("ox", "oy", "oz", "dx", "dy", "dz", "tmax")
                ),
                axis=1,
            ).astype(cp.float32, copy=False)
            weights = cp.asarray(ray_weights, dtype=cp.uint64)
            weighted_sum = cp.zeros(1, dtype=cp.uint64)
            status = cp.zeros(1, dtype=cp.uint32)
            handle, gas_keepalive = self._build_gas(vertices, primitive_count)
            params = self.host_params[0]
            params["traversable"] = np.uint64(handle)
            params["rays"] = np.uint64(ray_rows.data.ptr)
            params["weights"] = np.uint64(weights.data.ptr)
            params["weighted_sum"] = np.uint64(weighted_sum.data.ptr)
            params["status"] = np.uint64(status.data.ptr)
            params["query_count"] = np.uint32(query_count)
            params["tmin"] = np.float32(tmin)
            params["tmax"] = np.float32(tmax)
            copy_params_and_launch(
                self.runtime,
                pipeline=self.pipeline,
                sbt=self.sbt,
                stream=self.stream,
                params=self.host_params,
                device_params=self.device_params,
                width=query_count,
            )
            weighted_sum.data.copy_to_host_async(
                ctypes.c_void_p(int(self.host_weighted_sum.ctypes.data)),
                int(self.host_weighted_sum.nbytes),
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
                f"triangle PyOptiX device status failed: {observed_status}"
            )
        value = int(self.host_weighted_sum[0])
        if value < 0 or value > UINT64_MAX:
            raise OverflowError("triangle PyOptiX result is outside U64")
        _ = gas_keepalive
        return TriangleSegmentResult(
            checked_u64=value,
            query_count=query_count,
            primitive_count=primitive_count,
            device_status=observed_status,
        )

    def execute_graph(
        self,
        *,
        graph_contract: Any,
        segment_iterator: Any,
        max_relation_rows: int,
    ) -> dict[str, Any]:
        """Execute every deterministic RT-2A1 segment and return one scalar."""

        if max_relation_rows <= 0:
            raise ValueError("max_relation_rows must be positive")
        total = 0
        rows = []
        for segment in segment_iterator(
            graph_contract,
            paper_algorithm="RT-2A1",
            max_relation_rows=max_relation_rows,
            max_directed_edge_rows=max_relation_rows,
        ):
            observed = self.execute_segment(
                segment["triangles"],
                segment["rays"],
                ray_weights=segment["ray_weights"],
            )
            if total > UINT64_MAX - observed.checked_u64:
                raise OverflowError("triangle app segment total overflows U64")
            total += observed.checked_u64
            rows.append(
                {
                    "segment_id": int(segment["segment_id"]),
                    "query_count": observed.query_count,
                    "primitive_count": observed.primitive_count,
                    "checked_u64": observed.checked_u64,
                    "device_status": observed.device_status,
                }
            )
        if not rows:
            raise RuntimeError("triangle app produced no physical segment")
        expected = int(graph_contract.expected_triangle_count)
        if total != expected:
            raise RuntimeError(
                f"triangle PyOptiX oracle mismatch: expected={expected} observed={total}"
            )
        return {
            "schema": "rtdl.v4_paper_apps_pyoptix.triangle_counting.v1",
            "paper_algorithm": "RT-2A1",
            "output": {"triangle_count": total},
            "expected": {"triangle_count": expected},
            "matched": True,
            "segment_count": len(rows),
            "segments": rows,
            "public_pyoptix_host_api": True,
            "private_rtdl_native_called": False,
            "device_checked_u64_reduction": True,
            "full_graph_stage_returned": True,
        }

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.stream = None
        self.device_params = None
        self.host_params_keepalive = None
        self.host_params = None
        self.host_weighted_sum_keepalive = None
        self.host_weighted_sum = None
        self.host_status_keepalive = None
        self.host_status = None
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
    "PublicPyOptixTriangleCountingOwner",
    "TriangleSegmentResult",
]
