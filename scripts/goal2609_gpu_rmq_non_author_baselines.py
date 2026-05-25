from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import tempfile
import textwrap
from typing import Any

import numpy as np

from examples.v2_0.learner_apps.gpu_rmq import rtdl_gpu_rmq_learner_app as app


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
CUDA_SOURCE = BUILD_DIR / "goal2609_gpu_rmq_baseline.cu"
CUDA_EXE = BUILD_DIR / "goal2609_gpu_rmq_baseline"

WORKLOADS = (
    ("repeated", 4096, 1000, 64, 123),
    ("random", 16384, 4000, 256, 123),
    ("repeated", 65536, 8000, 512, 123),
)

CUDA_BASELINE_SOURCE = r"""
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

#include <cuda_runtime.h>

#define CUDA_CHECK(call) do { \
    cudaError_t err = (call); \
    if (err != cudaSuccess) { \
        std::cerr << "CUDA error: " << cudaGetErrorString(err) << " at " << __LINE__ << std::endl; \
        std::exit(2); \
    } \
} while (0)

struct SparseTable {
    uint32_t block_count = 0;
    uint32_t block_size = 0;
    uint32_t levels = 0;
    std::vector<float> values;
    std::vector<uint32_t> indices;
    double build_ms = 0.0;
};

static std::vector<float> read_float_file(const std::string& path, size_t count) {
    std::vector<float> out(count);
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("failed to open values file");
    in.read(reinterpret_cast<char*>(out.data()), static_cast<std::streamsize>(count * sizeof(float)));
    if (!in) throw std::runtime_error("failed to read values file");
    return out;
}

static std::vector<uint32_t> read_u32_file(const std::string& path, size_t count) {
    std::vector<uint32_t> out(count);
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("failed to open queries file");
    in.read(reinterpret_cast<char*>(out.data()), static_cast<std::streamsize>(count * sizeof(uint32_t)));
    if (!in) throw std::runtime_error("failed to read queries file");
    return out;
}

static SparseTable build_sparse_table(const std::vector<float>& values, uint32_t block_size) {
    auto t0 = std::chrono::steady_clock::now();
    const uint32_t n = static_cast<uint32_t>(values.size());
    SparseTable table;
    table.block_size = block_size;
    table.block_count = (n + block_size - 1u) / block_size;
    table.levels = 1u;
    while ((1u << table.levels) <= table.block_count) ++table.levels;
    table.values.assign(static_cast<size_t>(table.levels) * table.block_count, std::numeric_limits<float>::infinity());
    table.indices.assign(static_cast<size_t>(table.levels) * table.block_count, 0xffffffffu);

    for (uint32_t block = 0; block < table.block_count; ++block) {
        const uint32_t start = block * block_size;
        const uint32_t stop = std::min<uint32_t>(start + block_size, n);
        float best_value = values[start];
        uint32_t best_index = start;
        for (uint32_t index = start + 1u; index < stop; ++index) {
            const float value = values[index];
            if (value < best_value || (value == best_value && index < best_index)) {
                best_value = value;
                best_index = index;
            }
        }
        table.values[block] = best_value;
        table.indices[block] = best_index;
    }

    uint32_t span = 1u;
    for (uint32_t level = 1u; level < table.levels; ++level) {
        if (table.block_count < span * 2u) break;
        const uint32_t valid = table.block_count - span * 2u + 1u;
        const size_t prev = static_cast<size_t>(level - 1u) * table.block_count;
        const size_t curr = static_cast<size_t>(level) * table.block_count;
        for (uint32_t block = 0; block < valid; ++block) {
            const float left_value = table.values[prev + block];
            const uint32_t left_index = table.indices[prev + block];
            const float right_value = table.values[prev + block + span];
            const uint32_t right_index = table.indices[prev + block + span];
            const bool take_right = (right_value < left_value) || (right_value == left_value && right_index < left_index);
            table.values[curr + block] = take_right ? right_value : left_value;
            table.indices[curr + block] = take_right ? right_index : left_index;
        }
        span <<= 1u;
    }
    auto t1 = std::chrono::steady_clock::now();
    table.build_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    return table;
}

static void query_cpu(
    const std::vector<float>& values,
    const std::vector<uint32_t>& queries,
    const SparseTable& table,
    std::vector<uint32_t>& out_indices,
    std::vector<float>& out_values,
    int threads) {
    const uint32_t q = static_cast<uint32_t>(out_indices.size());
    const uint32_t n = static_cast<uint32_t>(values.size());
    #ifdef _OPENMP
    omp_set_num_threads(threads);
    #pragma omp parallel for schedule(static)
    #endif
    for (int64_t query_id_i = 0; query_id_i < static_cast<int64_t>(q); ++query_id_i) {
        const uint32_t query_id = static_cast<uint32_t>(query_id_i);
        const uint32_t left = queries[2u * query_id];
        const uint32_t right = queries[2u * query_id + 1u];
        float best_value = std::numeric_limits<float>::infinity();
        uint32_t best_index = 0xffffffffu;
        if (left > right || right >= n) {
            out_indices[query_id] = best_index;
            out_values[query_id] = best_value;
            continue;
        }
        const uint32_t left_block = left / table.block_size;
        const uint32_t right_block = right / table.block_size;
        uint32_t edge_stop = right;
        if (left_block != right_block) edge_stop = (left_block + 1u) * table.block_size - 1u;
        for (uint32_t index = left; index <= edge_stop; ++index) {
            const float value = values[index];
            if (value < best_value || (value == best_value && index < best_index)) {
                best_value = value;
                best_index = index;
            }
        }
        if (left_block != right_block) {
            const uint32_t right_start = right_block * table.block_size;
            for (uint32_t index = right_start; index <= right; ++index) {
                const float value = values[index];
                if (value < best_value || (value == best_value && index < best_index)) {
                    best_value = value;
                    best_index = index;
                }
            }
            if (left_block + 1u <= right_block - 1u) {
                const uint32_t first_full = left_block + 1u;
                const uint32_t last_full = right_block - 1u;
                const uint32_t full_count = last_full - first_full + 1u;
                const uint32_t level = 31u - static_cast<uint32_t>(__builtin_clz(full_count));
                const uint32_t width = 1u << level;
                const uint32_t right_full = last_full - width + 1u;
                const size_t offset = static_cast<size_t>(level) * table.block_count;
                const float left_value = table.values[offset + first_full];
                const uint32_t left_index = table.indices[offset + first_full];
                if (left_value < best_value || (left_value == best_value && left_index < best_index)) {
                    best_value = left_value;
                    best_index = left_index;
                }
                const float right_value = table.values[offset + right_full];
                const uint32_t right_index = table.indices[offset + right_full];
                if (right_value < best_value || (right_value == best_value && right_index < best_index)) {
                    best_value = right_value;
                    best_index = right_index;
                }
            }
        }
        out_indices[query_id] = best_index;
        out_values[query_id] = best_value;
    }
}

static void query_exact_cpu(
    const std::vector<float>& values,
    const std::vector<uint32_t>& queries,
    std::vector<uint32_t>& out_indices,
    std::vector<float>& out_values,
    int threads) {
    const uint32_t q = static_cast<uint32_t>(out_indices.size());
    const uint32_t n = static_cast<uint32_t>(values.size());
    #ifdef _OPENMP
    omp_set_num_threads(threads);
    #pragma omp parallel for schedule(static)
    #endif
    for (int64_t query_id_i = 0; query_id_i < static_cast<int64_t>(q); ++query_id_i) {
        const uint32_t query_id = static_cast<uint32_t>(query_id_i);
        const uint32_t left = queries[2u * query_id];
        const uint32_t right = queries[2u * query_id + 1u];
        float best_value = std::numeric_limits<float>::infinity();
        uint32_t best_index = 0xffffffffu;
        if (left <= right && right < n) {
            for (uint32_t index = left; index <= right; ++index) {
                const float value = values[index];
                if (value < best_value || (value == best_value && index < best_index)) {
                    best_value = value;
                    best_index = index;
                }
            }
        }
        out_indices[query_id] = best_index;
        out_values[query_id] = best_value;
    }
}

__global__ void rmq_hier_query_kernel(
    const float* values,
    uint32_t n,
    const uint32_t* queries,
    uint32_t q,
    uint32_t block_size,
    uint32_t block_count,
    const float* sparse_values,
    const uint32_t* sparse_indices,
    uint32_t* out_indices,
    float* out_values) {
    const uint32_t query_id = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_id >= q) return;
    const uint32_t left = queries[2u * query_id];
    const uint32_t right = queries[2u * query_id + 1u];
    float best_value = 3.402823466e+38F;
    uint32_t best_index = 0xffffffffu;
    if (left > right || right >= n) {
        out_indices[query_id] = best_index;
        out_values[query_id] = best_value;
        return;
    }
    const uint32_t left_block = left / block_size;
    const uint32_t right_block = right / block_size;
    uint32_t edge_stop = right;
    if (left_block != right_block) edge_stop = (left_block + 1u) * block_size - 1u;
    for (uint32_t index = left; index <= edge_stop; ++index) {
        const float value = values[index];
        if (value < best_value || (value == best_value && index < best_index)) {
            best_value = value;
            best_index = index;
        }
    }
    if (left_block != right_block) {
        const uint32_t right_start = right_block * block_size;
        for (uint32_t index = right_start; index <= right; ++index) {
            const float value = values[index];
            if (value < best_value || (value == best_value && index < best_index)) {
                best_value = value;
                best_index = index;
            }
        }
        if (left_block + 1u <= right_block - 1u) {
            const uint32_t first_full = left_block + 1u;
            const uint32_t last_full = right_block - 1u;
            const uint32_t full_count = last_full - first_full + 1u;
            uint32_t level = 0u;
            uint32_t remaining = full_count;
            while (remaining >>= 1u) {
                ++level;
            }
            const uint32_t width = 1u << level;
            const uint32_t right_full = last_full - width + 1u;
            const uint32_t offset = level * block_count;
            const float left_value = sparse_values[offset + first_full];
            const uint32_t left_index = sparse_indices[offset + first_full];
            if (left_value < best_value || (left_value == best_value && left_index < best_index)) {
                best_value = left_value;
                best_index = left_index;
            }
            const float right_value = sparse_values[offset + right_full];
            const uint32_t right_index = sparse_indices[offset + right_full];
            if (right_value < best_value || (right_value == best_value && right_index < best_index)) {
                best_value = right_value;
                best_index = right_index;
            }
        }
    }
    out_indices[query_id] = best_index;
    out_values[query_id] = best_value;
}

static double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    const size_t n = values.size();
    return (n % 2 == 0) ? (values[n / 2 - 1] + values[n / 2]) * 0.5 : values[n / 2];
}

static void print_array(const std::vector<double>& values) {
    std::cout << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i) std::cout << ",";
        std::cout << std::fixed << std::setprecision(6) << values[i];
    }
    std::cout << "]";
}

int main(int argc, char** argv) {
    if (argc != 7) {
        std::cerr << "usage: baseline values.bin queries.bin n q block_size repeats" << std::endl;
        return 2;
    }
    const std::string values_path = argv[1];
    const std::string queries_path = argv[2];
    const uint32_t n = static_cast<uint32_t>(std::stoul(argv[3]));
    const uint32_t q = static_cast<uint32_t>(std::stoul(argv[4]));
    const uint32_t block_size = static_cast<uint32_t>(std::stoul(argv[5]));
    const int repeats = std::stoi(argv[6]);
    const int threads = std::max(1, std::stoi(std::getenv("OMP_NUM_THREADS") ? std::getenv("OMP_NUM_THREADS") : "1"));

    auto values = read_float_file(values_path, n);
    auto queries = read_u32_file(queries_path, static_cast<size_t>(q) * 2u);
    auto table = build_sparse_table(values, block_size);

    std::vector<uint32_t> cpu_indices(q);
    std::vector<float> cpu_values(q);
    query_cpu(values, queries, table, cpu_indices, cpu_values, threads);
    std::vector<uint32_t> exact_indices(q);
    std::vector<float> exact_values(q);
    query_exact_cpu(values, queries, exact_indices, exact_values, threads);
    uint32_t cpu_sparse_mismatches = 0;
    for (uint32_t i = 0; i < q; ++i) {
        if (cpu_indices[i] != exact_indices[i] || std::fabs(cpu_values[i] - exact_values[i]) > 1e-6f) {
            ++cpu_sparse_mismatches;
        }
    }

    std::vector<double> cpu_runs_ms;
    for (int r = 0; r < repeats; ++r) {
        auto t0 = std::chrono::steady_clock::now();
        query_cpu(values, queries, table, cpu_indices, cpu_values, threads);
        auto t1 = std::chrono::steady_clock::now();
        cpu_runs_ms.push_back(std::chrono::duration<double, std::milli>(t1 - t0).count());
    }

    float* d_values = nullptr;
    uint32_t* d_queries = nullptr;
    float* d_sparse_values = nullptr;
    uint32_t* d_sparse_indices = nullptr;
    uint32_t* d_out_indices = nullptr;
    float* d_out_values = nullptr;
    CUDA_CHECK(cudaMalloc(&d_values, static_cast<size_t>(n) * sizeof(float)));
    CUDA_CHECK(cudaMalloc(&d_queries, static_cast<size_t>(q) * 2u * sizeof(uint32_t)));
    CUDA_CHECK(cudaMalloc(&d_sparse_values, table.values.size() * sizeof(float)));
    CUDA_CHECK(cudaMalloc(&d_sparse_indices, table.indices.size() * sizeof(uint32_t)));
    CUDA_CHECK(cudaMalloc(&d_out_indices, static_cast<size_t>(q) * sizeof(uint32_t)));
    CUDA_CHECK(cudaMalloc(&d_out_values, static_cast<size_t>(q) * sizeof(float)));
    CUDA_CHECK(cudaMemcpy(d_values, values.data(), static_cast<size_t>(n) * sizeof(float), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_queries, queries.data(), static_cast<size_t>(q) * 2u * sizeof(uint32_t), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_sparse_values, table.values.data(), table.values.size() * sizeof(float), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_sparse_indices, table.indices.data(), table.indices.size() * sizeof(uint32_t), cudaMemcpyHostToDevice));

    const uint32_t threads_per_block = 256u;
    const uint32_t grid = (q + threads_per_block - 1u) / threads_per_block;
    rmq_hier_query_kernel<<<grid, threads_per_block>>>(
        d_values, n, d_queries, q, block_size, table.block_count, d_sparse_values, d_sparse_indices, d_out_indices, d_out_values);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());

    std::vector<double> cuda_runs_ms;
    for (int r = 0; r < repeats; ++r) {
        cudaEvent_t start, stop;
        CUDA_CHECK(cudaEventCreate(&start));
        CUDA_CHECK(cudaEventCreate(&stop));
        CUDA_CHECK(cudaEventRecord(start));
        rmq_hier_query_kernel<<<grid, threads_per_block>>>(
            d_values, n, d_queries, q, block_size, table.block_count, d_sparse_values, d_sparse_indices, d_out_indices, d_out_values);
        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaEventRecord(stop));
        CUDA_CHECK(cudaEventSynchronize(stop));
        float elapsed_ms = 0.0f;
        CUDA_CHECK(cudaEventElapsedTime(&elapsed_ms, start, stop));
        cuda_runs_ms.push_back(static_cast<double>(elapsed_ms));
        CUDA_CHECK(cudaEventDestroy(start));
        CUDA_CHECK(cudaEventDestroy(stop));
    }

    std::vector<uint32_t> cuda_indices(q);
    std::vector<float> cuda_values(q);
    CUDA_CHECK(cudaMemcpy(cuda_indices.data(), d_out_indices, static_cast<size_t>(q) * sizeof(uint32_t), cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(cuda_values.data(), d_out_values, static_cast<size_t>(q) * sizeof(float), cudaMemcpyDeviceToHost));
    bool cuda_matches_cpu = true;
    uint32_t cuda_mismatches = 0;
    uint32_t first_mismatch_query = 0xffffffffu;
    uint32_t first_cpu_index = 0xffffffffu;
    uint32_t first_cuda_index = 0xffffffffu;
    uint32_t first_query_left = 0xffffffffu;
    uint32_t first_query_right = 0xffffffffu;
    float first_cpu_value = 0.0f;
    float first_cuda_value = 0.0f;
    for (uint32_t i = 0; i < q; ++i) {
        if (cuda_indices[i] != cpu_indices[i] || std::fabs(cuda_values[i] - cpu_values[i]) > 1e-6f) {
            cuda_matches_cpu = false;
            ++cuda_mismatches;
            if (first_mismatch_query == 0xffffffffu) {
                first_mismatch_query = i;
                first_cpu_index = cpu_indices[i];
                first_cuda_index = cuda_indices[i];
                first_query_left = queries[2u * i];
                first_query_right = queries[2u * i + 1u];
                first_cpu_value = cpu_values[i];
                first_cuda_value = cuda_values[i];
            }
        }
    }

    CUDA_CHECK(cudaFree(d_values));
    CUDA_CHECK(cudaFree(d_queries));
    CUDA_CHECK(cudaFree(d_sparse_values));
    CUDA_CHECK(cudaFree(d_sparse_indices));
    CUDA_CHECK(cudaFree(d_out_indices));
    CUDA_CHECK(cudaFree(d_out_values));

    std::cout << "{";
    std::cout << "\"cpu_threads\":" << threads << ",";
    std::cout << "\"cpu_build_ms\":" << std::fixed << std::setprecision(6) << table.build_ms << ",";
    std::cout << "\"cpu_sparse_matches_exact_scan\":" << (cpu_sparse_mismatches == 0 ? "true" : "false") << ",";
    std::cout << "\"cpu_sparse_exact_mismatches\":" << cpu_sparse_mismatches << ",";
    std::cout << "\"cpu_query_runs_ms\":"; print_array(cpu_runs_ms); std::cout << ",";
    std::cout << "\"cpu_query_median_ms\":" << median(cpu_runs_ms) << ",";
    std::cout << "\"cuda_query_runs_ms\":"; print_array(cuda_runs_ms); std::cout << ",";
    std::cout << "\"cuda_query_median_ms\":" << median(cuda_runs_ms) << ",";
    std::cout << "\"cuda_matches_cpu\":" << (cuda_matches_cpu ? "true" : "false") << ",";
    std::cout << "\"cuda_mismatches\":" << cuda_mismatches << ",";
    std::cout << "\"cuda_first_mismatch_query\":" << first_mismatch_query << ",";
    std::cout << "\"cuda_first_mismatch_cpu_index\":" << first_cpu_index << ",";
    std::cout << "\"cuda_first_mismatch_cuda_index\":" << first_cuda_index << ",";
    std::cout << "\"cuda_first_mismatch_query_left\":" << first_query_left << ",";
    std::cout << "\"cuda_first_mismatch_query_right\":" << first_query_right << ",";
    std::cout << "\"cuda_first_mismatch_cpu_value\":" << first_cpu_value << ",";
    std::cout << "\"cuda_first_mismatch_cuda_value\":" << first_cuda_value << ",";
    std::cout << "\"cuda_uses_cpu_built_sparse_table\":true,";
    std::cout << "\"block_count\":" << table.block_count << ",";
    std::cout << "\"levels\":" << table.levels;
    std::cout << "}" << std::endl;
    return cuda_matches_cpu ? 0 : 1;
}
"""


def _find_nvcc() -> str:
    candidates = [
        os.environ.get("NVCC"),
        shutil.which("nvcc"),
        "/usr/local/cuda/bin/nvcc",
        "/usr/local/cuda-12.8/bin/nvcc",
        "/usr/local/cuda-12.6/bin/nvcc",
        "/usr/local/cuda-12.4/bin/nvcc",
        "/usr/local/cuda-12/bin/nvcc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise RuntimeError("nvcc not found; set NVCC or install CUDA compiler tooling")


def _cuda_gencode(nvcc: str) -> str:
    if os.environ.get("CUDA_ARCH") or os.environ.get("CUDA_CODE"):
        return (
            "arch="
            + os.environ.get("CUDA_ARCH", "compute_86")
            + ",code="
            + os.environ.get("CUDA_CODE", "sm_86")
        )
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            text=True,
            capture_output=True,
            check=False,
        )
        compute_cap = result.stdout.splitlines()[0].strip()
        major, minor = compute_cap.split(".", 1)
        detected_arch = f"compute_{int(major)}{int(minor)}"
        detected_code = f"sm_{int(major)}{int(minor)}"
        supported = subprocess.run(
            [nvcc, "--list-gpu-arch"],
            text=True,
            capture_output=True,
            check=False,
        ).stdout.split()
        if detected_arch in supported:
            return f"arch={detected_arch},code={detected_code}"
    except Exception:
        pass
    return "arch=compute_86,code=sm_86"


def compile_cuda_baseline() -> dict[str, Any]:
    BUILD_DIR.mkdir(exist_ok=True)
    CUDA_SOURCE.write_text(CUDA_BASELINE_SOURCE, encoding="utf-8")
    nvcc = _find_nvcc()
    command = [
        nvcc,
        "-O3",
        "-std=c++17",
        "-gencode",
        _cuda_gencode(nvcc),
        "-Xcompiler",
        "-fopenmp",
        str(CUDA_SOURCE),
        "-o",
        str(CUDA_EXE),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "failed to compile CUDA baseline\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    return {"command": command, "stdout": result.stdout, "stderr": result.stderr}


def run_native_baseline(
    fixture: app.RMQFixture,
    *,
    block_size: int,
    repeats: int,
    threads: int,
) -> dict[str, Any]:
    values = np.asarray(fixture.values, dtype=np.float32)
    queries = np.asarray(fixture.queries, dtype=np.uint32)
    with tempfile.TemporaryDirectory(prefix="goal2609_gpu_rmq_") as tmp:
        tmp_path = Path(tmp)
        values_path = tmp_path / "values.bin"
        queries_path = tmp_path / "queries.bin"
        values.tofile(values_path)
        queries.tofile(queries_path)
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = str(threads)
        command = [
            str(CUDA_EXE),
            str(values_path),
            str(queries_path),
            str(values.size),
            str(len(fixture.queries)),
            str(block_size),
            str(repeats),
        ]
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "native baseline failed\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )
    payload = json.loads(result.stdout)
    payload["command"] = command
    payload["stderr"] = result.stderr
    return payload


def median_seconds_from_ms(values_ms: list[float]) -> float:
    return statistics.median(values_ms) / 1000.0


def run_workload(
    dataset: str,
    value_count: int,
    query_count: int,
    block_size: int,
    seed: int,
    *,
    repeats: int,
    threads: int,
    reduction_factor: int,
    scan_threshold: int,
    rt_top_block_size: int,
) -> dict[str, Any]:
    fixture = app.make_fixture(
        dataset=dataset,
        value_count=value_count,
        query_count=query_count,
        seed=seed,
        max_width=value_count,
    )
    rtdl_payload = app.paper_rt_prepared_reuse_payload(
        fixture,
        block_size=block_size,
        sample=False,
        reuse_repeats=repeats,
    )
    hybrid_payload = app.paper_hybrid_rtdl_partner_payload(
        fixture,
        reduction_factor=reduction_factor,
        scan_threshold=scan_threshold,
        rt_top_block_size=rt_top_block_size,
        sample=False,
        reuse_repeats=repeats,
    )
    native_payload = run_native_baseline(
        fixture,
        block_size=block_size,
        repeats=repeats,
        threads=threads,
    )
    rtdl_sec = float(rtdl_payload["query_sec"]["median"])
    hybrid_sec = float(hybrid_payload["query_sec"]["median"])
    cpu_sec = float(native_payload["cpu_query_median_ms"]) / 1000.0
    cuda_sec = float(native_payload["cuda_query_median_ms"]) / 1000.0
    return {
        "dataset": dataset,
        "value_count": value_count,
        "query_count": query_count,
        "block_size": block_size,
        "seed": seed,
        "rtdl": {
            "mode": "paper_rt_prepared_reuse",
            "matches_cpu_reference": bool(rtdl_payload["matches_cpu_reference"]),
            "query_median_ms": rtdl_sec * 1000.0,
            "query_runs_ms": [value * 1000.0 for value in rtdl_payload["query_sec"]["runs"]],
            "row_format": rtdl_payload["row_format"],
            "combined_scene": bool(rtdl_payload["last_query_metadata"].get("native_combined_scene_grouped_argmin")),
            "prepare_ms": float(rtdl_payload["prepare_sec"]) * 1000.0,
            "query_batch_prepare_ms": float(rtdl_payload["prepare_sec_query_batch"]) * 1000.0,
        },
        "rtdl_paper_hybrid": {
            "mode": "paper_hybrid_rtdl_partner",
            "matches_cpu_reference": bool(hybrid_payload["matches_cpu_reference"]),
            "query_median_ms": hybrid_sec * 1000.0,
            "query_runs_ms": [value * 1000.0 for value in hybrid_payload["query_sec"]["runs"]],
            "prepare_ms": float(hybrid_payload["prepare_sec"]) * 1000.0,
            "query_batch_prepare_ms": float(hybrid_payload["prepare_sec_query_batch"]) * 1000.0,
            "hierarchy": hybrid_payload["hierarchy"],
            "rt_used": bool(hybrid_payload["execution_metadata"]["rt"]["rt_used"]),
            "rt_query_count": int(hybrid_payload["execution_metadata"]["rt"]["rt_query_count"]),
            "partner_mode": str(hybrid_payload["execution_metadata"]["partner"]["mode"]),
            "partner_candidate_count": int(hybrid_payload["execution_metadata"]["partner"]["candidate_count"]),
            "partner_candidate_finalize": hybrid_payload["execution_metadata"]["partner"].get(
                "candidate_finalize",
                {},
            ),
        },
        "cpu_openmp_sparse": {
            "threads": int(native_payload["cpu_threads"]),
            "build_ms": float(native_payload["cpu_build_ms"]),
            "query_median_ms": float(native_payload["cpu_query_median_ms"]),
            "query_runs_ms": native_payload["cpu_query_runs_ms"],
            "matches_exact_scan": bool(native_payload["cpu_sparse_matches_exact_scan"]),
            "exact_mismatches": int(native_payload["cpu_sparse_exact_mismatches"]),
        },
        "cuda_sparse_query": {
            "query_median_ms": float(native_payload["cuda_query_median_ms"]),
            "query_runs_ms": native_payload["cuda_query_runs_ms"],
            "matches_cpu_openmp_sparse": bool(native_payload["cuda_matches_cpu"]),
            "uses_cpu_built_sparse_table": bool(native_payload["cuda_uses_cpu_built_sparse_table"]),
        },
        "speedups_query_median": {
            "rtdl_vs_cpu_openmp_sparse": cpu_sec / rtdl_sec if rtdl_sec > 0 else math.inf,
            "cuda_sparse_vs_rtdl": rtdl_sec / cuda_sec if cuda_sec > 0 else math.inf,
            "rtdl_vs_cuda_sparse": cuda_sec / rtdl_sec if rtdl_sec > 0 else math.inf,
            "hybrid_vs_cpu_openmp_sparse": cpu_sec / hybrid_sec if hybrid_sec > 0 else math.inf,
            "cuda_sparse_vs_hybrid": hybrid_sec / cuda_sec if cuda_sec > 0 else math.inf,
            "hybrid_vs_cuda_sparse": cuda_sec / hybrid_sec if hybrid_sec > 0 else math.inf,
            "hybrid_vs_previous_rtdl": rtdl_sec / hybrid_sec if hybrid_sec > 0 else math.inf,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/reports/goal2609_gpu_rmq_non_author_baselines_2026-05-25.json")
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--threads", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--reduction-factor", type=int, default=32)
    parser.add_argument("--scan-threshold", type=int, default=64)
    parser.add_argument("--rt-top-block-size", type=int, default=1)
    args = parser.parse_args()

    compile_payload = compile_cuda_baseline()
    results = [
        run_workload(
            dataset,
            value_count,
            query_count,
            block_size,
            seed,
            repeats=args.repeats,
            threads=args.threads,
            reduction_factor=args.reduction_factor,
            scan_threshold=args.scan_threshold,
            rt_top_block_size=args.rt_top_block_size,
        )
        for dataset, value_count, query_count, block_size, seed in WORKLOADS
    ]
    payload = {
        "goal": "goal2609_gpu_rmq_non_author_baselines",
        "author_code_excluded": True,
        "baseline_scope": (
            "Same generated fixtures; RTDL prepared RT query-only median versus "
            "OpenMP CPU sparse-table query and standalone CUDA sparse-table query. "
            "CUDA baseline uses a CPU-built sparse table uploaded to GPU, so it is a "
            "query-kernel baseline, not an end-to-end GPU construction baseline. "
            "The RTDL paper-hybrid path uses the generic grouped candidate argmin "
            "primitive when the native OptiX runtime exports it."
        ),
        "compile": compile_payload,
        "repeats": int(args.repeats),
        "threads_requested": int(args.threads),
        "paper_hybrid_parameters": {
            "reduction_factor": int(args.reduction_factor),
            "scan_threshold": int(args.scan_threshold),
            "rt_top_block_size": int(args.rt_top_block_size),
        },
        "workloads": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
