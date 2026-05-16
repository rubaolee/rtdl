from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from rtdsl.partner_adapters import directed_hausdorff_2d_partner_columns, point_rows_to_partner_columns
from rtdsl.reference import Point


@dataclass(frozen=True)
class DirectedResult:
    distance: float
    source_index: int
    target_index: int
    elapsed_sec: float


def make_point_columns(n: int, *, seed: int, offset_x: float = 0.0, offset_y: float = 0.0) -> dict[str, np.ndarray]:
    if n <= 0:
        raise ValueError("point count must be positive")
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0.0, 2.0 * math.pi, size=n)
    radius = 1.0 + 0.18 * np.sin(np.arange(n, dtype=np.float64) * 0.017) + rng.normal(0.0, 0.015, size=n)
    x = (radius * np.cos(theta) + offset_x).astype(np.float64)
    y = (radius * np.sin(theta) + offset_y).astype(np.float64)
    ids = np.arange(n, dtype=np.int64)
    return {"ids": ids, "x": x, "y": y}


def columns_to_points(columns: dict[str, np.ndarray]) -> tuple[Point, ...]:
    ids = columns["ids"]
    x = columns["x"]
    y = columns["y"]
    return tuple(Point(id=int(ids[i]), x=float(x[i]), y=float(y[i])) for i in range(int(ids.size)))


CPU_CPP = r"""
#include <cmath>
#include <cstdint>
#include <limits>

extern "C" {
struct DirectedHausdorffResult {
    double distance;
    int64_t source_index;
    int64_t target_index;
};

DirectedHausdorffResult directed_hausdorff_openmp(
    const double* sx,
    const double* sy,
    int64_t source_count,
    const double* tx,
    const double* ty,
    int64_t target_count
) {
    double best_min_sq = -1.0;
    int64_t best_source = -1;
    int64_t best_target = -1;

    #pragma omp parallel
    {
        double local_best_min_sq = -1.0;
        int64_t local_best_source = -1;
        int64_t local_best_target = -1;

        #pragma omp for schedule(static)
        for (int64_t i = 0; i < source_count; ++i) {
            double nearest_sq = std::numeric_limits<double>::infinity();
            int64_t nearest_j = 0;
            const double x = sx[i];
            const double y = sy[i];
            for (int64_t j = 0; j < target_count; ++j) {
                const double dx = x - tx[j];
                const double dy = y - ty[j];
                const double d2 = dx * dx + dy * dy;
                if (d2 < nearest_sq || (d2 == nearest_sq && j < nearest_j)) {
                    nearest_sq = d2;
                    nearest_j = j;
                }
            }
            if (
                nearest_sq > local_best_min_sq ||
                (nearest_sq == local_best_min_sq && i < local_best_source)
            ) {
                local_best_min_sq = nearest_sq;
                local_best_source = i;
                local_best_target = nearest_j;
            }
        }

        #pragma omp critical
        {
            if (
                local_best_min_sq > best_min_sq ||
                (local_best_min_sq == best_min_sq && local_best_source < best_source)
            ) {
                best_min_sq = local_best_min_sq;
                best_source = local_best_source;
                best_target = local_best_target;
            }
        }
    }

    DirectedHausdorffResult result;
    result.distance = std::sqrt(best_min_sq);
    result.source_index = best_source;
    result.target_index = best_target;
    return result;
}
}
"""


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    if sys.platform == "darwin":
        return ".dylib"
    return ".so"


def build_cpu_openmp_library(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    source = cache_dir / "hausdorff_openmp.cpp"
    library = cache_dir / f"hausdorff_openmp{_shared_suffix()}"
    source.write_text(CPU_CPP, encoding="utf-8")
    if library.exists() and library.stat().st_mtime >= source.stat().st_mtime:
        return library

    if os.name == "nt":
        raise RuntimeError("OpenMP C++ baseline is intended for Linux/macOS in this benchmark script")
    cmd = [
        os.environ.get("CXX", "g++"),
        "-O3",
        "-std=c++17",
        "-fopenmp",
        "-shared",
        "-fPIC",
        str(source),
        "-o",
        str(library),
    ]
    subprocess.run(cmd, check=True)
    return library


def run_cpu_openmp(source: dict[str, np.ndarray], target: dict[str, np.ndarray], *, cache_dir: Path) -> DirectedResult:
    library = build_cpu_openmp_library(cache_dir)
    lib = ctypes.CDLL(str(library))

    class CResult(ctypes.Structure):
        _fields_ = [
            ("distance", ctypes.c_double),
            ("source_index", ctypes.c_int64),
            ("target_index", ctypes.c_int64),
        ]

    func = lib.directed_hausdorff_openmp
    func.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int64,
    ]
    func.restype = CResult
    sx = np.ascontiguousarray(source["x"], dtype=np.float64)
    sy = np.ascontiguousarray(source["y"], dtype=np.float64)
    tx = np.ascontiguousarray(target["x"], dtype=np.float64)
    ty = np.ascontiguousarray(target["y"], dtype=np.float64)
    start = time.perf_counter()
    result = func(
        sx.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        sy.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int64(sx.size),
        tx.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ty.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int64(tx.size),
    )
    elapsed = time.perf_counter() - start
    return DirectedResult(float(result.distance), int(result.source_index), int(result.target_index), elapsed)


CUDA_KERNEL = r"""
extern "C" __global__
void directed_hausdorff_tiled(
    const double* sx,
    const double* sy,
    const long long source_count,
    const double* tx,
    const double* ty,
    const long long target_count,
    double* block_values,
    long long* block_sources,
    long long* block_targets
) {
    extern __shared__ unsigned char shared_raw[];
    double* s_tx = reinterpret_cast<double*>(shared_raw);
    double* s_ty = s_tx + blockDim.x;

    const long long source_index = static_cast<long long>(blockIdx.x) * blockDim.x + threadIdx.x;
    double nearest_sq = 1.0 / 0.0;
    long long nearest_target = 0;
    const bool active = source_index < source_count;
    const double x = active ? sx[source_index] : 0.0;
    const double y = active ? sy[source_index] : 0.0;

    for (long long tile = 0; tile < target_count; tile += blockDim.x) {
        const long long target_index = tile + threadIdx.x;
        if (target_index < target_count) {
            s_tx[threadIdx.x] = tx[target_index];
            s_ty[threadIdx.x] = ty[target_index];
        }
        __syncthreads();
        const long long limit = min(static_cast<long long>(blockDim.x), target_count - tile);
        if (active) {
            for (long long j = 0; j < limit; ++j) {
                const double dx = x - s_tx[j];
                const double dy = y - s_ty[j];
                const double d2 = dx * dx + dy * dy;
                const long long candidate_target = tile + j;
                if (d2 < nearest_sq || (d2 == nearest_sq && candidate_target < nearest_target)) {
                    nearest_sq = d2;
                    nearest_target = candidate_target;
                }
            }
        }
        __syncthreads();
    }

    __shared__ double local_values[256];
    __shared__ long long local_sources[256];
    __shared__ long long local_targets[256];
    local_values[threadIdx.x] = active ? nearest_sq : -1.0;
    local_sources[threadIdx.x] = active ? source_index : 9223372036854775807LL;
    local_targets[threadIdx.x] = active ? nearest_target : 9223372036854775807LL;
    __syncthreads();

    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride) {
            const int other = threadIdx.x + stride;
            const double other_value = local_values[other];
            const long long other_source = local_sources[other];
            if (
                other_value > local_values[threadIdx.x] ||
                (other_value == local_values[threadIdx.x] && other_source < local_sources[threadIdx.x])
            ) {
                local_values[threadIdx.x] = other_value;
                local_sources[threadIdx.x] = other_source;
                local_targets[threadIdx.x] = local_targets[other];
            }
        }
        __syncthreads();
    }

    if (threadIdx.x == 0) {
        block_values[blockIdx.x] = local_values[0];
        block_sources[blockIdx.x] = local_sources[0];
        block_targets[blockIdx.x] = local_targets[0];
    }
}
"""


CUDA_CPP = r"""
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cuda_runtime.h>

extern "C" {
struct DirectedHausdorffResult {
    double distance;
    int64_t source_index;
    int64_t target_index;
};

static DirectedHausdorffResult make_cuda_error_result(cudaError_t status, int64_t stage) {
    DirectedHausdorffResult result;
    result.distance = NAN;
    result.source_index = -stage;
    result.target_index = -static_cast<int64_t>(status);
    return result;
}

__global__ void directed_hausdorff_tiled_kernel(
    const double* sx,
    const double* sy,
    const long long source_count,
    const double* tx,
    const double* ty,
    const long long target_count,
    double* block_values,
    long long* block_sources,
    long long* block_targets
) {
    extern __shared__ unsigned char shared_raw[];
    double* s_tx = reinterpret_cast<double*>(shared_raw);
    double* s_ty = s_tx + blockDim.x;

    const long long source_index = static_cast<long long>(blockIdx.x) * blockDim.x + threadIdx.x;
    double nearest_sq = INFINITY;
    long long nearest_target = 0;
    const bool active = source_index < source_count;
    const double x = active ? sx[source_index] : 0.0;
    const double y = active ? sy[source_index] : 0.0;

    for (long long tile = 0; tile < target_count; tile += blockDim.x) {
        const long long target_index = tile + threadIdx.x;
        if (target_index < target_count) {
            s_tx[threadIdx.x] = tx[target_index];
            s_ty[threadIdx.x] = ty[target_index];
        }
        __syncthreads();
        const long long limit = min(static_cast<long long>(blockDim.x), target_count - tile);
        if (active) {
            for (long long j = 0; j < limit; ++j) {
                const double dx = x - s_tx[j];
                const double dy = y - s_ty[j];
                const double d2 = dx * dx + dy * dy;
                const long long candidate_target = tile + j;
                if (d2 < nearest_sq || (d2 == nearest_sq && candidate_target < nearest_target)) {
                    nearest_sq = d2;
                    nearest_target = candidate_target;
                }
            }
        }
        __syncthreads();
    }

    __shared__ double local_values[256];
    __shared__ long long local_sources[256];
    __shared__ long long local_targets[256];
    local_values[threadIdx.x] = active ? nearest_sq : -1.0;
    local_sources[threadIdx.x] = active ? source_index : 9223372036854775807LL;
    local_targets[threadIdx.x] = active ? nearest_target : 9223372036854775807LL;
    __syncthreads();

    for (int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (threadIdx.x < stride) {
            const int other = threadIdx.x + stride;
            const double other_value = local_values[other];
            const long long other_source = local_sources[other];
            if (
                other_value > local_values[threadIdx.x] ||
                (other_value == local_values[threadIdx.x] && other_source < local_sources[threadIdx.x])
            ) {
                local_values[threadIdx.x] = other_value;
                local_sources[threadIdx.x] = other_source;
                local_targets[threadIdx.x] = local_targets[other];
            }
        }
        __syncthreads();
    }

    if (threadIdx.x == 0) {
        block_values[blockIdx.x] = local_values[0];
        block_sources[blockIdx.x] = local_sources[0];
        block_targets[blockIdx.x] = local_targets[0];
    }
}

DirectedHausdorffResult directed_hausdorff_cuda(
    const double* h_sx,
    const double* h_sy,
    int64_t source_count,
    const double* h_tx,
    const double* h_ty,
    int64_t target_count
) {
    const int threads = 256;
    const int blocks = static_cast<int>((source_count + threads - 1) / threads);
    double* d_sx = nullptr;
    double* d_sy = nullptr;
    double* d_tx = nullptr;
    double* d_ty = nullptr;
    double* d_values = nullptr;
    long long* d_sources = nullptr;
    long long* d_targets = nullptr;
    cudaError_t status = cudaMalloc(&d_sx, source_count * sizeof(double));
    if (status != cudaSuccess) return make_cuda_error_result(status, 1);
    status = cudaMalloc(&d_sy, source_count * sizeof(double));
    if (status != cudaSuccess) return make_cuda_error_result(status, 2);
    status = cudaMalloc(&d_tx, target_count * sizeof(double));
    if (status != cudaSuccess) return make_cuda_error_result(status, 3);
    status = cudaMalloc(&d_ty, target_count * sizeof(double));
    if (status != cudaSuccess) return make_cuda_error_result(status, 4);
    status = cudaMalloc(&d_values, blocks * sizeof(double));
    if (status != cudaSuccess) return make_cuda_error_result(status, 5);
    status = cudaMalloc(&d_sources, blocks * sizeof(long long));
    if (status != cudaSuccess) return make_cuda_error_result(status, 6);
    status = cudaMalloc(&d_targets, blocks * sizeof(long long));
    if (status != cudaSuccess) return make_cuda_error_result(status, 7);
    status = cudaMemcpy(d_sx, h_sx, source_count * sizeof(double), cudaMemcpyHostToDevice);
    if (status != cudaSuccess) return make_cuda_error_result(status, 8);
    status = cudaMemcpy(d_sy, h_sy, source_count * sizeof(double), cudaMemcpyHostToDevice);
    if (status != cudaSuccess) return make_cuda_error_result(status, 9);
    status = cudaMemcpy(d_tx, h_tx, target_count * sizeof(double), cudaMemcpyHostToDevice);
    if (status != cudaSuccess) return make_cuda_error_result(status, 10);
    status = cudaMemcpy(d_ty, h_ty, target_count * sizeof(double), cudaMemcpyHostToDevice);
    if (status != cudaSuccess) return make_cuda_error_result(status, 11);
    directed_hausdorff_tiled_kernel<<<blocks, threads, threads * 2 * sizeof(double)>>>(
        d_sx,
        d_sy,
        source_count,
        d_tx,
        d_ty,
        target_count,
        d_values,
        d_sources,
        d_targets
    );
    status = cudaGetLastError();
    if (status != cudaSuccess) return make_cuda_error_result(status, 12);
    status = cudaDeviceSynchronize();
    if (status != cudaSuccess) return make_cuda_error_result(status, 13);
    double* h_values = static_cast<double*>(std::malloc(blocks * sizeof(double)));
    long long* h_sources = static_cast<long long*>(std::malloc(blocks * sizeof(long long)));
    long long* h_targets = static_cast<long long*>(std::malloc(blocks * sizeof(long long)));
    if (h_values == nullptr || h_sources == nullptr || h_targets == nullptr) return make_cuda_error_result(cudaErrorMemoryAllocation, 14);
    status = cudaMemcpy(h_values, d_values, blocks * sizeof(double), cudaMemcpyDeviceToHost);
    if (status != cudaSuccess) return make_cuda_error_result(status, 15);
    status = cudaMemcpy(h_sources, d_sources, blocks * sizeof(long long), cudaMemcpyDeviceToHost);
    if (status != cudaSuccess) return make_cuda_error_result(status, 16);
    status = cudaMemcpy(h_targets, d_targets, blocks * sizeof(long long), cudaMemcpyDeviceToHost);
    if (status != cudaSuccess) return make_cuda_error_result(status, 17);
    double best = -1.0;
    long long best_source = -1;
    long long best_target = -1;
    for (int i = 0; i < blocks; ++i) {
        if (h_values[i] > best || (h_values[i] == best && h_sources[i] < best_source)) {
            best = h_values[i];
            best_source = h_sources[i];
            best_target = h_targets[i];
        }
    }
    std::free(h_values);
    std::free(h_sources);
    std::free(h_targets);
    cudaFree(d_sx);
    cudaFree(d_sy);
    cudaFree(d_tx);
    cudaFree(d_ty);
    cudaFree(d_values);
    cudaFree(d_sources);
    cudaFree(d_targets);
    DirectedHausdorffResult result;
    result.distance = std::sqrt(best);
    result.source_index = best_source;
    result.target_index = best_target;
    return result;
}
}
"""


def build_cuda_ctypes_library(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    source = cache_dir / "hausdorff_cuda_baseline.cu"
    library = cache_dir / f"hausdorff_cuda_baseline{_shared_suffix()}"
    source.write_text(CUDA_CPP, encoding="utf-8")
    if library.exists() and library.stat().st_mtime >= source.stat().st_mtime:
        return library
    nvcc = os.environ.get("NVCC", "nvcc")
    cuda_arch = os.environ.get("RTDL_HAUSDORFF_CUDA_ARCH")
    cmd = [
        nvcc,
        "-O3",
        "-std=c++17",
        "--shared",
        "-Xcompiler",
        "-fPIC",
        str(source),
        "-o",
        str(library),
    ]
    if cuda_arch:
        cmd.insert(1, f"-arch={cuda_arch}")
    subprocess.run(cmd, check=True)
    return library


def run_cuda_ctypes_baseline(source: dict[str, np.ndarray], target: dict[str, np.ndarray], *, cache_dir: Path) -> DirectedResult:
    library = build_cuda_ctypes_library(cache_dir)
    lib = ctypes.CDLL(str(library))

    class CResult(ctypes.Structure):
        _fields_ = [
            ("distance", ctypes.c_double),
            ("source_index", ctypes.c_int64),
            ("target_index", ctypes.c_int64),
        ]

    func = lib.directed_hausdorff_cuda
    func.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int64,
    ]
    func.restype = CResult
    sx = np.ascontiguousarray(source["x"], dtype=np.float64)
    sy = np.ascontiguousarray(source["y"], dtype=np.float64)
    tx = np.ascontiguousarray(target["x"], dtype=np.float64)
    ty = np.ascontiguousarray(target["y"], dtype=np.float64)
    start = time.perf_counter()
    result = func(
        sx.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        sy.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int64(sx.size),
        tx.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ty.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_int64(tx.size),
    )
    elapsed = time.perf_counter() - start
    if math.isnan(float(result.distance)):
        raise RuntimeError(
            "CUDA C++ Hausdorff baseline failed: "
            f"stage={-int(result.source_index)} cuda_status={-int(result.target_index)}"
        )
    return DirectedResult(float(result.distance), int(result.source_index), int(result.target_index), elapsed)


def run_cuda_rawkernel(
    source: dict[str, object],
    target: dict[str, object],
    *,
    source_is_device: bool = False,
    target_is_device: bool = False,
) -> DirectedResult:
    import cupy

    sx = source["x"] if source_is_device else cupy.asarray(source["x"], dtype=cupy.float64)
    sy = source["y"] if source_is_device else cupy.asarray(source["y"], dtype=cupy.float64)
    tx = target["x"] if target_is_device else cupy.asarray(target["x"], dtype=cupy.float64)
    ty = target["y"] if target_is_device else cupy.asarray(target["y"], dtype=cupy.float64)
    source_count = int(sx.size)
    target_count = int(tx.size)
    threads = 256
    blocks = (source_count + threads - 1) // threads
    values = cupy.empty((blocks,), dtype=cupy.float64)
    sources = cupy.empty((blocks,), dtype=cupy.int64)
    targets = cupy.empty((blocks,), dtype=cupy.int64)
    kernel = cupy.RawKernel(CUDA_KERNEL, "directed_hausdorff_tiled")
    shared_bytes = threads * 2 * np.dtype(np.float64).itemsize
    cupy.cuda.runtime.deviceSynchronize()
    start = time.perf_counter()
    kernel(
        (blocks,),
        (threads,),
        (sx, sy, source_count, tx, ty, target_count, values, sources, targets),
        shared_mem=shared_bytes,
    )
    best_block = int(cupy.argmax(values).item())
    distance = float(cupy.sqrt(values[best_block]).item())
    source_index = int(sources[best_block].item())
    target_index = int(targets[best_block].item())
    cupy.cuda.runtime.deviceSynchronize()
    elapsed = time.perf_counter() - start
    return DirectedResult(distance, source_index, target_index, elapsed)


def run_rtdl_v2_user_cuda(source: dict[str, np.ndarray], target: dict[str, np.ndarray]) -> DirectedResult:
    points_source = columns_to_points(source)
    points_target = columns_to_points(target)
    source_columns = point_rows_to_partner_columns(points_source, partner="cupy")
    target_columns = point_rows_to_partner_columns(points_target, partner="cupy")
    return run_cuda_rawkernel(source_columns, target_columns, source_is_device=True, target_is_device=True)


def run_rtdl_partner_builtin(source: dict[str, np.ndarray], target: dict[str, np.ndarray]) -> DirectedResult:
    points_source = columns_to_points(source)
    points_target = columns_to_points(target)
    source_columns = point_rows_to_partner_columns(points_source, partner="cupy")
    target_columns = point_rows_to_partner_columns(points_target, partner="cupy")
    start = time.perf_counter()
    result = directed_hausdorff_2d_partner_columns(source_columns, target_columns, partner="cupy", return_metadata=True)
    elapsed = time.perf_counter() - start
    metadata = result["metadata"]
    source_index = int(np.where(source["ids"] == int(metadata["source_id"]))[0][0])
    target_index = int(np.where(target["ids"] == int(metadata["target_id"]))[0][0])
    return DirectedResult(float(metadata["distance"]), source_index, target_index, elapsed)


def undirected(run_directed, points_a, points_b, *, warmup: int = 0) -> dict[str, object]:
    for _ in range(max(0, int(warmup))):
        run_directed(points_a, points_b)
        run_directed(points_b, points_a)
    ab = run_directed(points_a, points_b)
    ba = run_directed(points_b, points_a)
    if (ab.distance, "a_to_b") >= (ba.distance, "b_to_a"):
        distance = ab.distance
        direction = "a_to_b"
    else:
        distance = ba.distance
        direction = "b_to_a"
    return {
        "distance": distance,
        "direction": direction,
        "directed_a_to_b": ab.__dict__,
        "directed_b_to_a": ba.__dict__,
        "elapsed_sec": ab.elapsed_sec + ba.elapsed_sec,
    }


def compare_distance(a: float, b: float, *, tolerance: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "User-level v2.0 Hausdorff benchmark: RTDL partner columns plus a "
            "learner-owned tiled CUDA continuation, checked against OpenMP CPU "
            "and independent CUDA baselines."
        )
    )
    parser.add_argument("--points-a", type=int, default=8192)
    parser.add_argument("--points-b", type=int, default=8192)
    parser.add_argument("--seed-a", type=int, default=11)
    parser.add_argument("--seed-b", type=int, default=29)
    parser.add_argument("--skip-cpu", action="store_true")
    parser.add_argument("--skip-cuda-ctypes", action="store_true")
    parser.add_argument("--skip-cupy", action="store_true")
    parser.add_argument("--skip-builtin-partner", action="store_true")
    parser.add_argument("--warmup", type=int, default=1, help="warmup iterations for GPU-like paths")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "build" / "hausdorff_v2_user_benchmark")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)

    print(f"[hausdorff] generating deterministic point clouds A={args.points_a} B={args.points_b}", flush=True)
    points_a = make_point_columns(args.points_a, seed=args.seed_a, offset_x=0.0, offset_y=0.0)
    points_b = make_point_columns(args.points_b, seed=args.seed_b, offset_x=0.08, offset_y=-0.06)

    results: dict[str, object] = {
        "app": "hausdorff_distance",
        "role": "user_level_v2_0_benchmark_no_rtdl_runtime_mutation",
        "points_a": args.points_a,
        "points_b": args.points_b,
        "methods": {},
    }

    oracle_distance = None
    if not args.skip_cpu:
        print("[hausdorff] running multithreaded OpenMP CPU baseline", flush=True)
        cpu = undirected(lambda s, t: run_cpu_openmp(s, t, cache_dir=args.cache_dir), points_a, points_b)
        results["methods"]["openmp_cpu"] = cpu
        oracle_distance = float(cpu["distance"])
        print(f"[hausdorff] OpenMP CPU distance={oracle_distance:.12g} sec={cpu['elapsed_sec']:.6f}", flush=True)

    if not args.skip_cuda_ctypes:
        print("[hausdorff] running independent nvcc CUDA C++ baseline", flush=True)
        cuda = undirected(
            lambda s, t: run_cuda_ctypes_baseline(s, t, cache_dir=args.cache_dir),
            points_a,
            points_b,
            warmup=args.warmup,
        )
        results["methods"]["cuda_ctypes_baseline"] = cuda
        if oracle_distance is None:
            oracle_distance = float(cuda["distance"])
        results["methods"]["cuda_ctypes_baseline"]["matches_oracle"] = compare_distance(
            float(cuda["distance"]),
            float(oracle_distance),
            tolerance=args.tolerance,
        )
        print(
            f"[hausdorff] CUDA C++ baseline distance={float(cuda['distance']):.12g} "
            f"sec={cuda['elapsed_sec']:.6f}",
            flush=True,
        )

    if not args.skip_cupy:
        print("[hausdorff] running independent CuPy RawKernel baseline", flush=True)
        cupy_cuda = undirected(run_cuda_rawkernel, points_a, points_b, warmup=args.warmup)
        results["methods"]["cupy_rawkernel_baseline"] = cupy_cuda
        if oracle_distance is None:
            oracle_distance = float(cupy_cuda["distance"])
        results["methods"]["cupy_rawkernel_baseline"]["matches_oracle"] = compare_distance(
            float(cupy_cuda["distance"]),
            float(oracle_distance),
            tolerance=args.tolerance,
        )
        print(
            f"[hausdorff] CuPy CUDA baseline distance={float(cupy_cuda['distance']):.12g} "
            f"sec={cupy_cuda['elapsed_sec']:.6f}",
            flush=True,
        )
        print("[hausdorff] running RTDL v2.0 user app path: partner columns + user CUDA continuation", flush=True)
        v2 = undirected(run_rtdl_v2_user_cuda, points_a, points_b, warmup=args.warmup)
        results["methods"]["rtdl_v2_partner_columns_user_cuda"] = v2
        if oracle_distance is None:
            oracle_distance = float(v2["distance"])
        results["methods"]["rtdl_v2_partner_columns_user_cuda"]["matches_oracle"] = compare_distance(
            float(v2["distance"]),
            float(oracle_distance),
            tolerance=args.tolerance,
        )
        print(
            f"[hausdorff] RTDL v2 user CUDA distance={float(v2['distance']):.12g} "
            f"sec={v2['elapsed_sec']:.6f}",
            flush=True,
        )

    if not args.skip_builtin_partner:
        print("[hausdorff] running built-in v2 CuPy partner exact path", flush=True)
        builtin = undirected(run_rtdl_partner_builtin, points_a, points_b, warmup=args.warmup)
        results["methods"]["rtdl_v2_builtin_cupy_partner_exact"] = builtin
        if oracle_distance is None:
            oracle_distance = float(builtin["distance"])
        results["methods"]["rtdl_v2_builtin_cupy_partner_exact"]["matches_oracle"] = compare_distance(
            float(builtin["distance"]),
            float(oracle_distance),
            tolerance=args.tolerance,
        )
        print(
            f"[hausdorff] built-in v2 CuPy distance={float(builtin['distance']):.12g} "
            f"sec={builtin['elapsed_sec']:.6f}",
            flush=True,
        )

    results["oracle_distance"] = oracle_distance
    methods = results["methods"]
    if "openmp_cpu" in methods and "rtdl_v2_partner_columns_user_cuda" in methods:
        results["speedup_rtdl_v2_user_cuda_vs_openmp_cpu"] = float(methods["openmp_cpu"]["elapsed_sec"]) / float(
            methods["rtdl_v2_partner_columns_user_cuda"]["elapsed_sec"]
        )
    if "cupy_rawkernel_baseline" in methods and "rtdl_v2_partner_columns_user_cuda" in methods:
        results["ratio_rtdl_v2_user_cuda_vs_cupy_cuda_baseline"] = float(
            methods["rtdl_v2_partner_columns_user_cuda"]["elapsed_sec"]
        ) / float(methods["cupy_rawkernel_baseline"]["elapsed_sec"])

    rendered = json.dumps(results, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
