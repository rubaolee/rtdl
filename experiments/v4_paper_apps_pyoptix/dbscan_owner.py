"""Strong application-specialized public-PyOptiX RT-DBSCAN baseline."""

from __future__ import annotations

import hashlib
from pathlib import Path
import threading

import numpy as np

from .public_runtime import (
    build_pipeline,
    copy_params_and_launch,
    host_to_raw_device,
    load_runtime,
    make_context,
    make_sbt,
    pinned_array,
)


POINT_DTYPE = np.dtype([
    ("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("id", "<u4"),
])
POINTERS = (
    "traversable", "points", "counts", "core", "parent", "roots",
    "border", "status",
)
PARAM_DTYPE = np.dtype({
    "names": POINTERS + (
        "count", "min_points", "mode", "reserved", "radius", "trace_tmax",
    ),
    "formats": ("<u8",) * 8 + ("<u4",) * 4 + ("<f4",) * 2,
    "offsets": tuple(range(0, 64, 8)) + (64, 68, 72, 76, 80, 84),
    "itemsize": 88,
    "align": True,
})
KERNELS = (
    "initialize", "extract_core_roots", "assign_roots_and_first",
    "mark_first", "write_labels",
)

if POINT_DTYPE.itemsize != 16 or PARAM_DTYPE.itemsize != 88:
    raise RuntimeError("public-PyOptiX DBSCAN ABI mismatch")


def _normalize_points(points: object) -> np.ndarray:
    value = np.asarray(points)
    if value.dtype != np.float32 or value.ndim != 2 or value.shape[1] != 3:
        raise TypeError("points must be a float32 Nx3 array")
    if not 0 < len(value) < 2**31 or not np.isfinite(value).all():
        raise ValueError("points must be finite and non-empty")
    return np.ascontiguousarray(value)


class PublicPyOptixDbscanOwner:
    """Prepared fixed scene; every execute recomputes all public outputs."""

    def __init__(
        self,
        *,
        points: object,
        epsilon: float,
        min_points: int,
        device_ptx: bytes,
        continuation_ptx: str | Path,
        runtime: object | None = None,
    ) -> None:
        points = _normalize_points(points)
        radius = np.float32(epsilon)
        if not np.isfinite(radius) or radius <= 0 \
                or not np.isfinite(np.float32(radius * radius)):
            raise ValueError("epsilon must have a finite positive float32 square")
        if type(min_points) is not int or not 1 <= min_points <= 0xFFFFFFFF:
            raise ValueError("min_points must be a positive uint32 integer")
        if not isinstance(device_ptx, bytes) or b".version" not in device_ptx[:4096] \
                or b"\0" in device_ptx:
            raise ValueError("canonical independent OptiX PTX is required")
        continuation_path = Path(continuation_ptx).resolve(strict=True)
        continuation_bytes = continuation_path.read_bytes()
        if b".version" not in continuation_bytes[:4096] \
                or b"\0" in continuation_bytes:
            raise ValueError("canonical continuation PTX is required")

        self.closed = False
        self.lock = threading.Lock()
        self._counts_and_core_ready = False
        self.count = len(points)
        self.min_points = min_points
        self.epsilon = float(radius)
        self.input_sha256 = hashlib.sha256(points.tobytes()).hexdigest()
        self.device_ptx_sha256 = hashlib.sha256(device_ptx).hexdigest()
        self.continuation_ptx_sha256 = hashlib.sha256(
            continuation_bytes).hexdigest()
        self.runtime = load_runtime() if runtime is None else runtime
        self.context = make_context(self.runtime)
        (
            self.pipeline,
            self.groups,
            self.module,
            self.logs,
        ) = build_pipeline(
            self.runtime,
            self.context,
            device_ptx,
            raygen_entry="__raygen__dbscan",
            miss_entry="__miss__dbscan",
            intersection_entry="__intersection__dbscan",
            any_hit_entry="__anyhit__dbscan",
            custom_primitive=True,
        )
        self.sbt, self.sbt_keepalive = make_sbt(self.runtime, self.groups)
        cp = self.runtime.cp
        optix = self.runtime.optix
        self.stream = cp.cuda.Stream(non_blocking=True)
        self.cuda_module = cp.RawModule(path=str(continuation_path))
        self.kernels = {
            name: self.cuda_module.get_function(name) for name in KERNELS
        }

        packed = np.empty(self.count, dtype=POINT_DTYPE)
        for axis, name in enumerate(("x", "y", "z")):
            packed[name] = points[:, axis]
        packed["id"] = np.arange(self.count, dtype=np.uint32)
        padded = np.float32(radius + np.float32(1e-4))
        bounds = np.concatenate((
            np.subtract(points, padded, dtype=np.float32),
            np.add(points, padded, dtype=np.float32),
        ), axis=1)
        if not np.isfinite(bounds).all():
            raise ValueError("radius-expanded AABBs must be finite")
        if not ((bounds[:, :3] < points).all() and
                (bounds[:, 3:] > points).all()):
            raise ValueError("radius-expanded AABB collapsed at this scale")

        with self.stream:
            self.points = host_to_raw_device(self.runtime, packed)
            device_bounds = cp.asarray(bounds)
            self.counts = cp.empty(self.count, dtype=cp.uint32)
            self.core = cp.empty(self.count, dtype=cp.uint8)
            for name in (
                "parent", "roots", "border", "first", "markers", "prefix",
                "labels",
            ):
                setattr(self, name, cp.empty(self.count, dtype=cp.int32))
            self.status = cp.zeros(1, dtype=cp.uint32)
            single_hit = getattr(
                optix, "GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL", None)
            if single_hit is None:
                raise RuntimeError("public single-any-hit geometry flag is required")
            build_input = optix.BuildInputCustomPrimitiveArray(
                aabbBuffers=[int(device_bounds.data.ptr)],
                numPrimitives=self.count,
                flags=[int(single_hit)],
                numSbtRecords=1,
            )
            options = optix.AccelBuildOptions(
                buildFlags=int(optix.BUILD_FLAG_PREFER_FAST_TRACE),
                operation=optix.BUILD_OPERATION_BUILD,
            )
            sizes = self.context.accelComputeMemoryUsage([options], [build_input])
            temporary = cp.cuda.alloc(int(sizes.tempSizeInBytes))
            self.gas = cp.cuda.alloc(int(sizes.outputSizeInBytes))
            self.handle = self.context.accelBuild(
                int(self.stream.ptr), [options], [build_input], int(temporary.ptr),
                int(sizes.tempSizeInBytes), int(self.gas.ptr),
                int(sizes.outputSizeInBytes), [],
            )
        self.stream.synchronize()

        # Each launch mode has immutable pinned parameters, preventing races.
        self.params = []
        for mode in range(3):
            host, keepalive = pinned_array(self.runtime, (1,), PARAM_DTYPE)
            device = cp.cuda.alloc(PARAM_DTYPE.itemsize)
            row = host[0]
            row["traversable"] = self.handle
            for name in POINTERS[1:]:
                value = getattr(self, name)
                row[name] = value.data.ptr if hasattr(value, "data") else value.ptr
            row["count"] = self.count
            row["min_points"] = min_points
            row["mode"] = mode
            row["reserved"] = 0
            row["radius"] = radius
            row["trace_tmax"] = max(
                np.float32(1e-6), np.float32(2) * padded)
            self.params.append((host, keepalive, device))

    @classmethod
    def prepare(cls, **kwargs: object) -> "PublicPyOptixDbscanOwner":
        return cls(**kwargs)

    def _kernel(self, name: str, *args: object) -> None:
        self.kernels[name](
            ((self.count + 255) // 256,),
            (256,),
            args + (np.uint32(self.count),),
            stream=self.stream,
        )

    def _trace(self, mode: int) -> None:
        host, _keepalive, device = self.params[mode]
        copy_params_and_launch(
            self.runtime,
            pipeline=self.pipeline,
            sbt=self.sbt,
            stream=self.stream,
            params=host,
            device_params=device,
            width=self.count,
        )

    def execute(self) -> dict[str, object]:
        with self.lock:
            if self.closed:
                raise RuntimeError("prepared public-PyOptiX DBSCAN owner is closed")
            cp = self.runtime.cp
            count_and_core_reused = self._counts_and_core_ready
            with self.stream:
                self.status.fill(0)
                self._kernel(
                    "initialize", self.parent, self.border, self.roots,
                    self.first, self.markers, self.labels)
                if not count_and_core_reused:
                    self._trace(0)
                self._trace(1)
                self._kernel(
                    "extract_core_roots", self.parent, self.core, self.roots,
                    self.status)
                self._trace(2)
                self._kernel(
                    "assign_roots_and_first", self.core, self.border,
                    self.roots, self.first, self.status)
                self._kernel(
                    "mark_first", self.roots, self.first, self.markers)
                cp.cumsum(self.markers, dtype=cp.int32, out=self.prefix)
                self._kernel(
                    "write_labels", self.roots, self.first, self.prefix,
                    self.labels)
            self.stream.synchronize()

            status = int(self.status.get()[0])
            if status:
                raise RuntimeError(
                    f"public-PyOptiX DBSCAN continuation failed: {status}")
            counts = self.counts.get()
            core = self.core.get()
            labels = self.labels.get()
            if not np.array_equal(
                    core, (counts >= self.min_points).astype(np.uint8)):
                raise RuntimeError("count/core output contract violated")
            if (counts < 1).any() or (counts > self.count).any() \
                    or ((labels < 0) & (core != 0)).any():
                raise RuntimeError("count/label output domain violated")
            self._counts_and_core_ready = True
            output = {
                "canonical_component_labels": tuple(map(int, labels)),
                "core_flags": tuple(bool(value) for value in core),
                "neighbor_counts": tuple(map(int, counts)),
            }
            return {
                "schema": "rtdl.public_pyoptix.dbscan.complete_output.v1",
                "output": output,
                "directed_edge_count": int(counts.sum(dtype=np.uint64)),
                "successful_optix_launches": (
                    2 if count_and_core_reused else 3),
                "exact_count_and_core_cache_reused": count_and_core_reused,
                "device_status": status,
                "boundary_assignment": "lowest_adjacent_core_component_root",
                "canonical_labels": "dense_first_appearance_in_input_order",
                "neighbor_count_policy": "exact_full_degree_including_self",
                "device_ptx_sha256": self.device_ptx_sha256,
                "continuation_ptx_sha256": self.continuation_ptx_sha256,
            }

    def close(self) -> None:
        with self.lock:
            if self.closed:
                return
            self.stream.synchronize()
            self.closed = True
            self.params = []
            self.kernels = {}
            for name in (
                "points", "gas", "counts", "core", "parent", "roots",
                "border", "first", "markers", "prefix", "labels", "status",
                "cuda_module", "sbt_keepalive", "sbt", "pipeline", "groups",
                "module", "context", "stream",
            ):
                setattr(self, name, None)

    def __enter__(self) -> "PublicPyOptixDbscanOwner":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


__all__ = ["PublicPyOptixDbscanOwner"]
