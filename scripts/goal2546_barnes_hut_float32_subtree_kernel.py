from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app
from scripts.goal2544_barnes_hut_torch_cuda_subtree_containment import _prepare_subtree_arrays


CPP_SOURCE = r"""
#include <torch/extension.h>

std::vector<torch::Tensor> fused_frontier_vector_sum_subtree_f32_cuda(
    torch::Tensor point_x,
    torch::Tensor point_y,
    torch::Tensor point_mass,
    torch::Tensor node_cx,
    torch::Tensor node_cy,
    torch::Tensor node_half_size,
    torch::Tensor node_mass,
    torch::Tensor node_resume_index,
    torch::Tensor node_subtree_end_index,
    torch::Tensor source_leaf_node_index,
    torch::Tensor member_offsets,
    torch::Tensor member_indices,
    torch::Tensor child_offsets,
    torch::Tensor child_indices,
    double theta,
    double softening
);
"""


CUDA_SOURCE = r"""
#include <torch/extension.h>
#include <ATen/cuda/CUDAContext.h>
#include <cuda_runtime.h>

namespace {

constexpr int kThreadsPerBlock = 128;

__global__ void fused_frontier_vector_sum_subtree_f32_kernel(
    int64_t source_count,
    const float* __restrict__ point_x,
    const float* __restrict__ point_y,
    const float* __restrict__ point_mass,
    int64_t node_count,
    const float* __restrict__ node_cx,
    const float* __restrict__ node_cy,
    const float* __restrict__ node_half_size,
    const float* __restrict__ node_mass,
    const int64_t* __restrict__ node_resume_index,
    const int64_t* __restrict__ node_subtree_end_index,
    const int64_t* __restrict__ source_leaf_node_index,
    const int64_t* __restrict__ member_offsets,
    const int64_t* __restrict__ member_indices,
    const int64_t* __restrict__ child_offsets,
    const int64_t* __restrict__ child_indices,
    float theta,
    float softening,
    float* __restrict__ out_x,
    float* __restrict__ out_y,
    int64_t* __restrict__ out_visited,
    int64_t* __restrict__ out_aggregate_count,
    int64_t* __restrict__ out_exact_count,
    int32_t* __restrict__ status
) {
    const int64_t source_index = static_cast<int64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (source_index >= source_count) {
        return;
    }
    if (node_count < 1) {
        status[0] = 1;
        return;
    }

    const int64_t source_leaf = source_leaf_node_index[source_index];
    if (source_leaf < 0 || source_leaf >= node_count) {
        status[0] = 4;
        return;
    }

    const float sx = point_x[source_index];
    const float sy = point_y[source_index];
    const float smass = point_mass[source_index];
    float sum_x = 0.0f;
    float sum_y = 0.0f;
    int64_t visited = 0;
    int64_t aggregate_count = 0;
    int64_t exact_count = 0;
    int64_t node_index = 0;

    while (node_index >= 0) {
        if (node_index >= node_count) {
            status[0] = 2;
            return;
        }
        visited += 1;
        const float dx = node_cx[node_index] - sx;
        const float dy = node_cy[node_index] - sy;
        const float distance = sqrtf(dx * dx + dy * dy);
        const float opening_ratio = distance == 0.0f
            ? 3.4e38f
            : (2.0f * node_half_size[node_index]) / distance;

        const int64_t subtree_end = node_subtree_end_index[node_index];
        const bool contains_source = node_index <= source_leaf && source_leaf < subtree_end;

        if (!contains_source && opening_ratio < theta) {
            const float dist_sq = dx * dx + dy * dy + softening * softening;
            if (dist_sq != 0.0f) {
                const float inv_dist = rsqrtf(dist_sq);
                const float scale = smass * node_mass[node_index] * inv_dist * inv_dist * inv_dist;
                sum_x += dx * scale;
                sum_y += dy * scale;
            }
            aggregate_count += 1;
            node_index = node_resume_index[node_index];
            continue;
        }

        const int64_t child_begin = child_offsets[node_index];
        const int64_t child_end = child_offsets[node_index + 1];
        if (child_begin < child_end) {
            node_index = child_indices[child_begin];
            continue;
        }

        const int64_t member_begin = member_offsets[node_index];
        const int64_t member_end = member_offsets[node_index + 1];
        for (int64_t offset = member_begin; offset < member_end; ++offset) {
            const int64_t target_index = member_indices[offset];
            if (target_index == source_index) {
                continue;
            }
            const float ex = point_x[target_index] - sx;
            const float ey = point_y[target_index] - sy;
            const float dist_sq = ex * ex + ey * ey + softening * softening;
            if (dist_sq != 0.0f) {
                const float inv_dist = rsqrtf(dist_sq);
                const float scale = smass * point_mass[target_index] * inv_dist * inv_dist * inv_dist;
                sum_x += ex * scale;
                sum_y += ey * scale;
            }
            exact_count += 1;
        }
        node_index = node_resume_index[node_index];
    }

    out_x[source_index] = sum_x;
    out_y[source_index] = sum_y;
    out_visited[source_index] = visited;
    out_aggregate_count[source_index] = aggregate_count;
    out_exact_count[source_index] = exact_count;
}

}  // namespace

std::vector<torch::Tensor> fused_frontier_vector_sum_subtree_f32_cuda(
    torch::Tensor point_x,
    torch::Tensor point_y,
    torch::Tensor point_mass,
    torch::Tensor node_cx,
    torch::Tensor node_cy,
    torch::Tensor node_half_size,
    torch::Tensor node_mass,
    torch::Tensor node_resume_index,
    torch::Tensor node_subtree_end_index,
    torch::Tensor source_leaf_node_index,
    torch::Tensor member_offsets,
    torch::Tensor member_indices,
    torch::Tensor child_offsets,
    torch::Tensor child_indices,
    double theta,
    double softening
) {
    TORCH_CHECK(point_x.is_cuda(), "point_x must be CUDA");
    TORCH_CHECK(point_x.scalar_type() == torch::kFloat32, "point_x must be float32");
    TORCH_CHECK(node_resume_index.scalar_type() == torch::kInt64, "node_resume_index must be int64");
    const auto source_count = point_x.size(0);
    const auto node_count = node_cx.size(0);
    auto float_options = point_x.options();
    auto int64_options = torch::TensorOptions().dtype(torch::kInt64).device(point_x.device());
    auto status_options = torch::TensorOptions().dtype(torch::kInt32).device(point_x.device());
    auto out_x = torch::empty({source_count}, float_options);
    auto out_y = torch::empty({source_count}, float_options);
    auto out_visited = torch::empty({source_count}, int64_options);
    auto out_aggregate = torch::empty({source_count}, int64_options);
    auto out_exact = torch::empty({source_count}, int64_options);
    auto status = torch::zeros({1}, status_options);

    const int blocks = static_cast<int>((source_count + kThreadsPerBlock - 1) / kThreadsPerBlock);
    fused_frontier_vector_sum_subtree_f32_kernel<<<blocks, kThreadsPerBlock, 0, at::cuda::getCurrentCUDAStream()>>>(
        source_count,
        point_x.data_ptr<float>(),
        point_y.data_ptr<float>(),
        point_mass.data_ptr<float>(),
        node_count,
        node_cx.data_ptr<float>(),
        node_cy.data_ptr<float>(),
        node_half_size.data_ptr<float>(),
        node_mass.data_ptr<float>(),
        node_resume_index.data_ptr<int64_t>(),
        node_subtree_end_index.data_ptr<int64_t>(),
        source_leaf_node_index.data_ptr<int64_t>(),
        member_offsets.data_ptr<int64_t>(),
        member_indices.data_ptr<int64_t>(),
        child_offsets.data_ptr<int64_t>(),
        child_indices.data_ptr<int64_t>(),
        static_cast<float>(theta),
        static_cast<float>(softening),
        out_x.data_ptr<float>(),
        out_y.data_ptr<float>(),
        out_visited.data_ptr<int64_t>(),
        out_aggregate.data_ptr<int64_t>(),
        out_exact.data_ptr<int64_t>(),
        status.data_ptr<int32_t>()
    );
    C10_CUDA_KERNEL_LAUNCH_CHECK();

    return {out_x, out_y, out_visited, out_aggregate, out_exact, status};
}
"""


def run_float32_subtree_kernel(
    *,
    body_count: int,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    repeats: int,
) -> dict[str, Any]:
    import torch
    from torch.utils.cpp_extension import load_inline

    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is required for this partner-resident prototype")
    os.environ.setdefault("MAX_JOBS", "2")
    os.environ.setdefault("TORCH_CUDA_ARCH_LIST", "8.6")

    prepare_start = time.perf_counter()
    prepared = _prepare_subtree_arrays(body_count, bucket_size, max_depth)
    tree_prepare_ms = (time.perf_counter() - prepare_start) * 1000.0

    compile_start = time.perf_counter()
    module = load_inline(
        name="rtdl_goal2546_fused_frontier_subtree_vector_sum_f32",
        cpp_sources=[CPP_SOURCE],
        cuda_sources=[CUDA_SOURCE],
        functions=["fused_frontier_vector_sum_subtree_f32_cuda"],
        extra_cuda_cflags=["--use_fast_math"],
        verbose=False,
    )
    compile_ms = (time.perf_counter() - compile_start) * 1000.0

    device = torch.device("cuda:0")
    tensor_start = time.perf_counter()
    tensors = {
        "point_x": torch.tensor(prepared["point_x"], dtype=torch.float32, device=device).contiguous(),
        "point_y": torch.tensor(prepared["point_y"], dtype=torch.float32, device=device).contiguous(),
        "point_mass": torch.tensor(prepared["point_mass"], dtype=torch.float32, device=device).contiguous(),
        "node_cx": torch.tensor(prepared["node_cx"], dtype=torch.float32, device=device).contiguous(),
        "node_cy": torch.tensor(prepared["node_cy"], dtype=torch.float32, device=device).contiguous(),
        "node_half_size": torch.tensor(prepared["node_half_size"], dtype=torch.float32, device=device).contiguous(),
        "node_mass": torch.tensor(prepared["node_mass"], dtype=torch.float32, device=device).contiguous(),
        "node_resume_index": torch.tensor(prepared["node_resume_index"], dtype=torch.int64, device=device).contiguous(),
        "node_subtree_end_index": torch.tensor(prepared["node_subtree_end_index"], dtype=torch.int64, device=device).contiguous(),
        "source_leaf_node_index": torch.tensor(prepared["source_leaf_node_index"], dtype=torch.int64, device=device).contiguous(),
        "member_offsets": torch.tensor(prepared["member_offsets"], dtype=torch.int64, device=device).contiguous(),
        "member_indices": torch.tensor(prepared["member_indices"], dtype=torch.int64, device=device).contiguous(),
        "child_offsets": torch.tensor(prepared["child_offsets"], dtype=torch.int64, device=device).contiguous(),
        "child_indices": torch.tensor(prepared["child_indices"], dtype=torch.int64, device=device).contiguous(),
    }
    torch.cuda.synchronize()
    tensor_prepare_ms = (time.perf_counter() - tensor_start) * 1000.0

    def launch():
        return module.fused_frontier_vector_sum_subtree_f32_cuda(
            tensors["point_x"],
            tensors["point_y"],
            tensors["point_mass"],
            tensors["node_cx"],
            tensors["node_cy"],
            tensors["node_half_size"],
            tensors["node_mass"],
            tensors["node_resume_index"],
            tensors["node_subtree_end_index"],
            tensors["source_leaf_node_index"],
            tensors["member_offsets"],
            tensors["member_indices"],
            tensors["child_offsets"],
            tensors["child_indices"],
            float(theta),
            float(softening),
        )

    launch()
    torch.cuda.synchronize()
    kernel_times: list[float] = []
    output = None
    for _ in range(repeats):
        start_event = torch.cuda.Event(enable_timing=True)
        end_event = torch.cuda.Event(enable_timing=True)
        start_event.record()
        output = launch()
        end_event.record()
        torch.cuda.synchronize()
        kernel_times.append(float(start_event.elapsed_time(end_event)))
    assert output is not None
    out_x, out_y, out_visited, out_aggregate, out_exact, status = output
    status_value = int(status.cpu().item())
    if status_value != 0:
        raise RuntimeError(f"CUDA float32 subtree kernel returned status {status_value}")

    out_x_cpu = out_x.cpu().double()
    out_y_cpu = out_y.cpu().double()
    checksum_force_x = float(out_x_cpu.sum().item())
    checksum_force_y = float(out_y_cpu.sum().item())
    reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
        prepared["bodies"],
        prepared["bodies"],
        prepared["tree"]["nodes"],
        theta=theta,
        softening=softening,
    )
    reference_x = torch.tensor(
        [float(row["vector_x"]) for row in reference["vector_sum_rows"]],
        dtype=torch.float64,
    )
    reference_y = torch.tensor(
        [float(row["vector_y"]) for row in reference["vector_sum_rows"]],
        dtype=torch.float64,
    )
    abs_error_x = (out_x_cpu - reference_x).abs()
    abs_error_y = (out_y_cpu - reference_y).abs()
    reference_norm = torch.sqrt(reference_x * reference_x + reference_y * reference_y).clamp_min(1.0e-30)
    vector_abs_error = torch.sqrt(abs_error_x * abs_error_x + abs_error_y * abs_error_y)
    relative_error = vector_abs_error / reference_norm

    visited_total = int(out_visited.sum().cpu().item())
    aggregate_total = int(out_aggregate.sum().cpu().item())
    exact_total = int(out_exact.sum().cpu().item())

    return {
        "benchmark": "barnes_hut_ppopp2025_style",
        "backend": "torch_cuda_extension_subtree_containment_float32",
        "contract": rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
        "body_count": body_count,
        "bucket_size": bucket_size,
        "theta": theta,
        "softening": softening,
        "repeats": repeats,
        "device": torch.cuda.get_device_name(0),
        "precision": "float32_accumulation",
        "timing_ms": {
            "tree_prepare_cpu": tree_prepare_ms,
            "extension_compile": compile_ms,
            "tensor_prepare_host_to_device": tensor_prepare_ms,
            "resident_kernel_min": min(kernel_times),
            "resident_kernel_mean": sum(kernel_times) / len(kernel_times),
            "resident_kernel_runs": kernel_times,
        },
        "result": {
            "checksum_force_x": checksum_force_x,
            "checksum_force_y": checksum_force_y,
            "visited_node_total": visited_total,
            "aggregate_contribution_row_count": aggregate_total,
            "exact_contribution_row_count": exact_total,
            "contribution_row_count": aggregate_total + exact_total,
        },
        "reference": {
            "checksum_force_x": float(reference_x.sum().item()),
            "checksum_force_y": float(reference_y.sum().item()),
            "summary": reference["summary"],
        },
        "deltas": {
            "checksum_force_x_abs": abs(checksum_force_x - float(reference_x.sum().item())),
            "checksum_force_y_abs": abs(checksum_force_y - float(reference_y.sum().item())),
            "visited_node_total": visited_total - int(reference["summary"]["visited_node_total"]),
            "contribution_row_count": (aggregate_total + exact_total) - int(reference["summary"]["contribution_row_count"]),
            "max_vector_abs_error": float(vector_abs_error.max().item()),
            "mean_vector_abs_error": float(vector_abs_error.mean().item()),
            "max_vector_relative_error": float(relative_error.max().item()),
            "mean_vector_relative_error": float(relative_error.mean().item()),
        },
        "metadata": {
            "partner_resident_kernel": True,
            "native_engine_app_specific": False,
            "authors_code_comparison": False,
            "paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "Float32 Torch/CUDA subtree-containment prototype for the generic 2-D fused vector-sum contract. "
                "Accuracy is measured against the float64 Python reference."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Float32 Torch/CUDA subtree-containment fused vector-sum prototype.")
    parser.add_argument("--body-count", type=int, default=32768)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--theta", type=float, default=app.THETA)
    parser.add_argument("--softening", type=float, default=app.SOFTENING)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    payload = run_float32_subtree_kernel(
        body_count=args.body_count,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        theta=args.theta,
        softening=args.softening,
        repeats=args.repeats,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
