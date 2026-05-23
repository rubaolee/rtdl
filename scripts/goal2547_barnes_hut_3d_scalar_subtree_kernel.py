from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


CONTRACT = "generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1"


@dataclass(frozen=True)
class Point3D:
    id: int
    x: float
    y: float
    z: float
    mass: float


@dataclass(frozen=True)
class TreeNode3D:
    id: int
    cx: float
    cy: float
    cz: float
    half_size: float
    mass: float
    member_ids: tuple[int, ...]
    child_ids: tuple[int, ...]
    depth: int
    dfs_index: int
    resume_index: int | None
    cell_cx: float
    cell_cy: float
    cell_cz: float
    is_leaf: bool


def read_treelogy_points(path: Path, *, limit: int | None = None) -> tuple[Point3D, ...]:
    lines = path.read_text().splitlines()
    if len(lines) < 5:
        raise ValueError("treelogy input must have at least five header lines")
    count = int(float(lines[0].strip()))
    rows = lines[5:]
    if limit is not None:
        count = min(count, limit)
    points: list[Point3D] = []
    for index, line in enumerate(rows[:count]):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"invalid point row {index}: {line!r}")
        mass, x, y, z = (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
        points.append(Point3D(id=len(points) + 1, x=x, y=y, z=z, mass=mass))
    if len(points) != count:
        raise ValueError(f"expected {count} points, read {len(points)}")
    return tuple(points)


def make_generated_points_3d(body_count: int) -> tuple[Point3D, ...]:
    if body_count < 1:
        raise ValueError("body_count must be positive")
    side = int(math.ceil(body_count ** (1.0 / 3.0)))
    points: list[Point3D] = []
    for index in range(body_count):
        gx = index % side
        gy = (index // side) % side
        gz = index // (side * side)
        denom = max(1, side - 1)
        x = (gx / denom) * 10.0 - 5.0
        y = (gy / denom) * 10.0 - 5.0
        z = (gz / denom) * 10.0 - 5.0
        x += ((index * 17) % 11 - 5) * 0.001
        y += ((index * 31) % 13 - 6) * 0.001
        z += ((index * 43) % 17 - 8) * 0.001
        mass = 10.0 + (index % 1991)
        points.append(Point3D(id=index + 1, x=x, y=y, z=z, mass=mass))
    return tuple(points)


def _morton_code_3d(point: Point3D, *, min_x: float, min_y: float, min_z: float, span: float, bits: int) -> int:
    scale = (1 << bits) - 1

    def quantize(value: float, minimum: float) -> int:
        normalized = 0.0 if span == 0.0 else (value - minimum) / span
        normalized = min(1.0, max(0.0, normalized))
        return int(normalized * scale)

    x = quantize(point.x, min_x)
    y = quantize(point.y, min_y)
    z = quantize(point.z, min_z)
    code = 0
    for bit in range(bits):
        code |= ((x >> bit) & 1) << (3 * bit)
        code |= ((y >> bit) & 1) << (3 * bit + 1)
        code |= ((z >> bit) & 1) << (3 * bit + 2)
    return code


def build_bucketized_aggregate_tree_3d(
    points: tuple[Point3D, ...],
    *,
    bucket_size: int,
    max_depth: int,
    morton_bits: int = 10,
) -> dict[str, object]:
    if not points:
        raise ValueError("points must not be empty")
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    min_z = min(point.z for point in points)
    max_z = max(point.z for point in points)
    span = max(max_x - min_x, max_y - min_y, max_z - min_z)
    if span == 0.0:
        span = 1.0
    span += 1.0e-9 * 2.0
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0
    half_size = span / 2.0
    square_min_x = center_x - half_size
    square_min_y = center_y - half_size
    square_min_z = center_z - half_size
    ordered = tuple(
        sorted(
            points,
            key=lambda point: (
                _morton_code_3d(
                    point,
                    min_x=square_min_x,
                    min_y=square_min_y,
                    min_z=square_min_z,
                    span=span,
                    bits=morton_bits,
                ),
                point.id,
            ),
        )
    )
    mutable_nodes: list[dict[str, object]] = []

    def add_node(
        members: tuple[Point3D, ...],
        *,
        cell_cx: float,
        cell_cy: float,
        cell_cz: float,
        node_half_size: float,
        depth: int,
    ) -> int:
        mass = sum(point.mass for point in members)
        if mass == 0.0:
            center_mass_x = sum(point.x for point in members) / len(members)
            center_mass_y = sum(point.y for point in members) / len(members)
            center_mass_z = sum(point.z for point in members) / len(members)
        else:
            center_mass_x = sum(point.x * point.mass for point in members) / mass
            center_mass_y = sum(point.y * point.mass for point in members) / mass
            center_mass_z = sum(point.z * point.mass for point in members) / mass
        node_id = len(mutable_nodes) + 1
        dfs_index = len(mutable_nodes)
        is_leaf = len(members) <= bucket_size or depth >= max_depth or node_half_size == 0.0
        mutable_nodes.append(
            {
                "id": node_id,
                "cx": center_mass_x,
                "cy": center_mass_y,
                "cz": center_mass_z,
                "half_size": node_half_size,
                "mass": mass,
                "member_ids": tuple(point.id for point in members),
                "child_ids": (),
                "depth": depth,
                "dfs_index": dfs_index,
                "resume_index": None,
                "cell_cx": cell_cx,
                "cell_cy": cell_cy,
                "cell_cz": cell_cz,
                "is_leaf": is_leaf,
            }
        )
        if not is_leaf:
            octants: list[list[Point3D]] = [[] for _ in range(8)]
            for point in members:
                octant = (1 if point.x >= cell_cx else 0) + (2 if point.y >= cell_cy else 0) + (4 if point.z >= cell_cz else 0)
                octants[octant].append(point)
            child_half_size = node_half_size / 2.0
            child_ids: list[int] = []
            for octant, octant_members in enumerate(octants):
                if not octant_members:
                    continue
                offset_x = child_half_size if octant & 1 else -child_half_size
                offset_y = child_half_size if octant & 2 else -child_half_size
                offset_z = child_half_size if octant & 4 else -child_half_size
                child_ids.append(
                    add_node(
                        tuple(octant_members),
                        cell_cx=cell_cx + offset_x,
                        cell_cy=cell_cy + offset_y,
                        cell_cz=cell_cz + offset_z,
                        node_half_size=child_half_size,
                        depth=depth + 1,
                    )
                )
            mutable_nodes[dfs_index]["child_ids"] = tuple(child_ids)
            mutable_nodes[dfs_index]["is_leaf"] = not child_ids
        return node_id

    add_node(ordered, cell_cx=center_x, cell_cy=center_y, cell_cz=center_z, node_half_size=half_size, depth=0)
    id_to_index = {int(node["id"]): index for index, node in enumerate(mutable_nodes)}

    def subtree_end_index(index: int) -> int:
        child_ids = tuple(int(child_id) for child_id in mutable_nodes[index]["child_ids"])
        if not child_ids:
            return index + 1
        return max(subtree_end_index(id_to_index[child_id]) for child_id in child_ids)

    for index, node in enumerate(mutable_nodes):
        end_index = subtree_end_index(index)
        node["resume_index"] = end_index if end_index < len(mutable_nodes) else None

    nodes = tuple(
        TreeNode3D(
            id=int(node["id"]),
            cx=float(node["cx"]),
            cy=float(node["cy"]),
            cz=float(node["cz"]),
            half_size=float(node["half_size"]),
            mass=float(node["mass"]),
            member_ids=tuple(int(item) for item in node["member_ids"]),
            child_ids=tuple(int(item) for item in node["child_ids"]),
            depth=int(node["depth"]),
            dfs_index=int(node["dfs_index"]),
            resume_index=None if node["resume_index"] is None else int(node["resume_index"]),
            cell_cx=float(node["cell_cx"]),
            cell_cy=float(node["cell_cy"]),
            cell_cz=float(node["cell_cz"]),
            is_leaf=bool(node["is_leaf"]),
        )
        for node in mutable_nodes
    )
    return {"nodes": nodes, "ordered_source_ids": tuple(point.id for point in ordered)}


def reference_scalar_sum_3d(
    points: tuple[Point3D, ...],
    nodes: tuple[TreeNode3D, ...],
    *,
    theta: float,
    softening: float,
) -> dict[str, object]:
    point_by_id = {point.id: point for point in points}
    node_by_id = {node.id: node for node in nodes}
    node_member_sets = {node.id: set(node.member_ids) for node in nodes}
    child_ids = {child_id for node in nodes for child_id in node.child_ids}
    root_ids = tuple(node.id for node in nodes if node.id not in child_ids)
    total_visited = 0
    total_accepted = 0
    total_exact = 0
    rows: list[dict[str, object]] = []

    for source in points:
        scalar_sum = 0.0
        visited = 0
        accepted = 0
        exact = 0

        def visit(node: TreeNode3D) -> None:
            nonlocal scalar_sum, visited, accepted, exact
            visited += 1
            dx = node.cx - source.x
            dy = node.cy - source.y
            dz = node.cz - source.z
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            contains_source = source.id in node_member_sets[node.id]
            if not contains_source and node.half_size < distance * theta:
                dist_sq = dx * dx + dy * dy + dz * dz + softening * softening
                if dist_sq != 0.0:
                    scalar_sum += source.mass * node.mass / dist_sq
                accepted += 1
                return
            if node.child_ids:
                for child_id in node.child_ids:
                    visit(node_by_id[child_id])
                return
            for target_id in node.member_ids:
                if target_id == source.id:
                    continue
                target = point_by_id[target_id]
                ex = target.x - source.x
                ey = target.y - source.y
                ez = target.z - source.z
                dist_sq = ex * ex + ey * ey + ez * ez + softening * softening
                if dist_sq != 0.0:
                    scalar_sum += source.mass * target.mass / dist_sq
                exact += 1

        for root_id in root_ids:
            visit(node_by_id[root_id])
        total_visited += visited
        total_accepted += accepted
        total_exact += exact
        rows.append(
            {
                "source_id": source.id,
                "scalar_force": scalar_sum,
                "visited_node_count": visited,
                "aggregate_contribution_count": accepted,
                "exact_contribution_count": exact,
            }
        )
    return {
        "scalar_sum_rows": tuple(rows),
        "summary": {
            "source_count": len(points),
            "tree_node_count": len(nodes),
            "root_count": len(root_ids),
            "leaf_node_count": sum(1 for node in nodes if node.is_leaf),
            "visited_node_total": total_visited,
            "aggregate_contribution_row_count": total_accepted,
            "exact_contribution_row_count": total_exact,
            "contribution_row_count": total_accepted + total_exact,
        },
    }


CPP_SOURCE = r"""
#include <torch/extension.h>

std::vector<torch::Tensor> scalar_sum_3d_cuda(
    torch::Tensor point_x,
    torch::Tensor point_y,
    torch::Tensor point_z,
    torch::Tensor point_mass,
    torch::Tensor node_cx,
    torch::Tensor node_cy,
    torch::Tensor node_cz,
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

__global__ void scalar_sum_3d_kernel(
    int64_t source_count,
    const float* __restrict__ point_x,
    const float* __restrict__ point_y,
    const float* __restrict__ point_z,
    const float* __restrict__ point_mass,
    int64_t node_count,
    const float* __restrict__ node_cx,
    const float* __restrict__ node_cy,
    const float* __restrict__ node_cz,
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
    float* __restrict__ out_scalar,
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
    const float sz = point_z[source_index];
    const float smass = point_mass[source_index];
    float scalar_sum = 0.0f;
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
        const float dz = node_cz[node_index] - sz;
        const float distance = sqrtf(dx * dx + dy * dy + dz * dz);
        const int64_t subtree_end = node_subtree_end_index[node_index];
        const bool contains_source = node_index <= source_leaf && source_leaf < subtree_end;

        if (!contains_source && node_half_size[node_index] < distance * theta) {
            const float dist_sq = dx * dx + dy * dy + dz * dz + softening * softening;
            if (dist_sq != 0.0f) {
                scalar_sum += smass * node_mass[node_index] / dist_sq;
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
            const float ez = point_z[target_index] - sz;
            const float dist_sq = ex * ex + ey * ey + ez * ez + softening * softening;
            if (dist_sq != 0.0f) {
                scalar_sum += smass * point_mass[target_index] / dist_sq;
            }
            exact_count += 1;
        }
        node_index = node_resume_index[node_index];
    }

    out_scalar[source_index] = scalar_sum;
    out_visited[source_index] = visited;
    out_aggregate_count[source_index] = aggregate_count;
    out_exact_count[source_index] = exact_count;
}

}  // namespace

std::vector<torch::Tensor> scalar_sum_3d_cuda(
    torch::Tensor point_x,
    torch::Tensor point_y,
    torch::Tensor point_z,
    torch::Tensor point_mass,
    torch::Tensor node_cx,
    torch::Tensor node_cy,
    torch::Tensor node_cz,
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
    const auto source_count = point_x.size(0);
    const auto node_count = node_cx.size(0);
    auto float_options = point_x.options();
    auto int64_options = torch::TensorOptions().dtype(torch::kInt64).device(point_x.device());
    auto status_options = torch::TensorOptions().dtype(torch::kInt32).device(point_x.device());
    auto out_scalar = torch::empty({source_count}, float_options);
    auto out_visited = torch::empty({source_count}, int64_options);
    auto out_aggregate = torch::empty({source_count}, int64_options);
    auto out_exact = torch::empty({source_count}, int64_options);
    auto status = torch::zeros({1}, status_options);

    const int blocks = static_cast<int>((source_count + kThreadsPerBlock - 1) / kThreadsPerBlock);
    scalar_sum_3d_kernel<<<blocks, kThreadsPerBlock, 0, at::cuda::getCurrentCUDAStream()>>>(
        source_count,
        point_x.data_ptr<float>(),
        point_y.data_ptr<float>(),
        point_z.data_ptr<float>(),
        point_mass.data_ptr<float>(),
        node_count,
        node_cx.data_ptr<float>(),
        node_cy.data_ptr<float>(),
        node_cz.data_ptr<float>(),
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
        out_scalar.data_ptr<float>(),
        out_visited.data_ptr<int64_t>(),
        out_aggregate.data_ptr<int64_t>(),
        out_exact.data_ptr<int64_t>(),
        status.data_ptr<int32_t>()
    );
    C10_CUDA_KERNEL_LAUNCH_CHECK();
    return {out_scalar, out_visited, out_aggregate, out_exact, status};
}
"""


def prepare_arrays_3d(points: tuple[Point3D, ...], *, bucket_size: int, max_depth: int) -> dict[str, Any]:
    tree = build_bucketized_aggregate_tree_3d(points, bucket_size=bucket_size, max_depth=max_depth)
    nodes = tuple(tree["nodes"])
    id_to_index = {point.id: index for index, point in enumerate(points)}
    node_id_to_index = {node.id: index for index, node in enumerate(nodes)}
    member_offsets = [0]
    member_indices: list[int] = []
    child_offsets = [0]
    child_indices: list[int] = []
    source_leaf_node_index = [-1 for _ in points]
    for node_index, node in enumerate(nodes):
        member_indices.extend(id_to_index[int(member_id)] for member_id in node.member_ids)
        member_offsets.append(len(member_indices))
        child_indices.extend(node_id_to_index[int(child_id)] for child_id in node.child_ids)
        child_offsets.append(len(child_indices))
        if node.is_leaf:
            for member_id in node.member_ids:
                source_leaf_node_index[id_to_index[int(member_id)]] = node_index
    if any(index < 0 for index in source_leaf_node_index):
        raise RuntimeError("every source must map to a leaf")
    return {
        "points": points,
        "tree": tree,
        "nodes": nodes,
        "point_x": [point.x for point in points],
        "point_y": [point.y for point in points],
        "point_z": [point.z for point in points],
        "point_mass": [point.mass for point in points],
        "node_cx": [node.cx for node in nodes],
        "node_cy": [node.cy for node in nodes],
        "node_cz": [node.cz for node in nodes],
        "node_half_size": [node.half_size for node in nodes],
        "node_mass": [node.mass for node in nodes],
        "node_resume_index": [-1 if node.resume_index is None else int(node.resume_index) for node in nodes],
        "node_subtree_end_index": [len(nodes) if node.resume_index is None else int(node.resume_index) for node in nodes],
        "source_leaf_node_index": source_leaf_node_index,
        "member_offsets": member_offsets,
        "member_indices": member_indices,
        "child_offsets": child_offsets,
        "child_indices": child_indices,
    }


def run_scalar_3d_kernel(
    *,
    body_count: int,
    input_file: Path | None,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    repeats: int,
    skip_reference: bool,
) -> dict[str, Any]:
    import torch
    from torch.utils.cpp_extension import load_inline

    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is required for this 3-D prototype")
    os.environ.setdefault("MAX_JOBS", "2")
    os.environ.setdefault("TORCH_CUDA_ARCH_LIST", "8.6")

    points = read_treelogy_points(input_file, limit=body_count) if input_file is not None else make_generated_points_3d(body_count)
    prepare_start = time.perf_counter()
    prepared = prepare_arrays_3d(points, bucket_size=bucket_size, max_depth=max_depth)
    tree_prepare_ms = (time.perf_counter() - prepare_start) * 1000.0

    compile_start = time.perf_counter()
    module = load_inline(
        name="rtdl_goal2547_scalar_sum_3d",
        cpp_sources=[CPP_SOURCE],
        cuda_sources=[CUDA_SOURCE],
        functions=["scalar_sum_3d_cuda"],
        extra_cuda_cflags=["--use_fast_math"],
        verbose=False,
    )
    compile_ms = (time.perf_counter() - compile_start) * 1000.0

    device = torch.device("cuda:0")
    tensor_start = time.perf_counter()
    tensors = {
        "point_x": torch.tensor(prepared["point_x"], dtype=torch.float32, device=device).contiguous(),
        "point_y": torch.tensor(prepared["point_y"], dtype=torch.float32, device=device).contiguous(),
        "point_z": torch.tensor(prepared["point_z"], dtype=torch.float32, device=device).contiguous(),
        "point_mass": torch.tensor(prepared["point_mass"], dtype=torch.float32, device=device).contiguous(),
        "node_cx": torch.tensor(prepared["node_cx"], dtype=torch.float32, device=device).contiguous(),
        "node_cy": torch.tensor(prepared["node_cy"], dtype=torch.float32, device=device).contiguous(),
        "node_cz": torch.tensor(prepared["node_cz"], dtype=torch.float32, device=device).contiguous(),
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
        return module.scalar_sum_3d_cuda(
            tensors["point_x"],
            tensors["point_y"],
            tensors["point_z"],
            tensors["point_mass"],
            tensors["node_cx"],
            tensors["node_cy"],
            tensors["node_cz"],
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
    out_scalar, out_visited, out_aggregate, out_exact, status = output
    status_value = int(status.cpu().item())
    if status_value != 0:
        raise RuntimeError(f"CUDA 3-D scalar kernel returned status {status_value}")
    out_scalar_cpu = out_scalar.cpu().double()
    visited_total = int(out_visited.sum().cpu().item())
    aggregate_total = int(out_aggregate.sum().cpu().item())
    exact_total = int(out_exact.sum().cpu().item())

    payload: dict[str, Any] = {
        "benchmark": "barnes_hut_ppopp2025_style",
        "backend": "torch_cuda_extension_subtree_containment_float32_scalar_3d",
        "contract": CONTRACT,
        "body_count": len(points),
        "input_file": None if input_file is None else str(input_file),
        "bucket_size": bucket_size,
        "theta": theta,
        "softening": softening,
        "repeats": repeats,
        "device": torch.cuda.get_device_name(0),
        "timing_ms": {
            "tree_prepare_cpu": tree_prepare_ms,
            "extension_compile": compile_ms,
            "tensor_prepare_host_to_device": tensor_prepare_ms,
            "resident_kernel_min": min(kernel_times),
            "resident_kernel_mean": sum(kernel_times) / len(kernel_times),
            "resident_kernel_runs": kernel_times,
        },
        "result": {
            "checksum_scalar_force": float(out_scalar_cpu.sum().item()),
            "visited_node_total": visited_total,
            "aggregate_contribution_row_count": aggregate_total,
            "exact_contribution_row_count": exact_total,
            "contribution_row_count": aggregate_total + exact_total,
        },
        "tree_summary": {
            "tree_node_count": len(prepared["nodes"]),
            "leaf_node_count": sum(1 for node in prepared["nodes"] if node.is_leaf),
        },
        "metadata": {
            "same_dimension_as_authors": True,
            "same_scalar_inverse_square_force_shape_as_authors": True,
            "same_tree_contract_as_authors": False,
            "partner_resident_kernel": True,
            "native_engine_app_specific": False,
            "authors_code_comparison": input_file is not None,
            "paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "3-D scalar inverse-square subtree-containment prototype. Same dimensionality and force shape as authors' sample, "
                "but not yet the exact same tree construction or RT traversal contract."
            ),
        },
    }
    if not skip_reference:
        reference = reference_scalar_sum_3d(points, tuple(prepared["nodes"]), theta=theta, softening=softening)
        reference_values = torch.tensor(
            [float(row["scalar_force"]) for row in reference["scalar_sum_rows"]],
            dtype=torch.float64,
        )
        abs_error = (out_scalar_cpu - reference_values).abs()
        rel_error = abs_error / reference_values.abs().clamp_min(1.0e-30)
        payload["reference"] = {
            "checksum_scalar_force": float(reference_values.sum().item()),
            "summary": reference["summary"],
        }
        payload["deltas"] = {
            "checksum_scalar_force_abs": abs(float(out_scalar_cpu.sum().item()) - float(reference_values.sum().item())),
            "visited_node_total": visited_total - int(reference["summary"]["visited_node_total"]),
            "contribution_row_count": (aggregate_total + exact_total) - int(reference["summary"]["contribution_row_count"]),
            "max_scalar_abs_error": float(abs_error.max().item()),
            "mean_scalar_abs_error": float(abs_error.mean().item()),
            "max_scalar_relative_error": float(rel_error.max().item()),
            "mean_scalar_relative_error": float(rel_error.mean().item()),
        }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="3-D scalar inverse-square subtree-containment prototype.")
    parser.add_argument("--body-count", type=int, default=32768)
    parser.add_argument("--input-file", type=Path, default=None)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--softening", type=float, default=0.0)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--skip-reference", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    payload = run_scalar_3d_kernel(
        body_count=args.body_count,
        input_file=args.input_file,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        theta=args.theta,
        softening=args.softening,
        repeats=args.repeats,
        skip_reference=args.skip_reference,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
