from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.generic_primitives import run_generic_ray_triangle_closest_hit
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D


BENCHMARK_NAME = "gpu_rmq"
PAPER = {
    "title": "GPU-RMQ: Accelerating Range Minimum Queries on Modern GPUs",
    "arxiv": "https://arxiv.org/abs/2604.01811",
    "authors": ("Lara Kreis", "Justus Henneberg", "Valentin Henkys", "Felix Schuhknecht", "Bertil Schmidt"),
    "relationship": (
        "This research/learner app records the paper's hierarchical/hybrid RMQ "
        "design pressure for RTDL, but Goal2612 rejected promotion to a closed "
        "benchmark app because the RTDL paths were still far slower than a direct "
        "CUDA sparse-query baseline."
    ),
}
AUTHOR_CODE = {
    "repo": "https://github.com/lakreis/GPU-RMQ",
    "inspected_head": "86fed1c170b7e41e8ec44e461f7220f87f492893",
    "binary": "build/rtxrmq",
    "dependencies": ("CUDA 12.9 or later", "NVIDIA OptiX 8", "OpenMP", "HRMQ library under hrmq/"),
    "cli": "./rtxrmq <n> <q> <lr> <alg>",
    "dataset_policy": (
        "The repository does not ship fixed dataset files. It generates arrays "
        "and queries from n, q, lr, and --seed; --save-input-data can persist "
        "those generated arrays, queries, and reference results."
    ),
}
AUTHOR_ALGORITHMS = {
    0: "[CPU] BASE",
    1: "[CPU] HRMQ",
    2: "[GPU] BASE / full GPU scan",
    5: "[GPU] RTX_blocks / RTXRMQ",
    16: "[GPU] GPU-RMQ (CL)",
    18: "[GPU] GPU-RMQ (CL) OptiX with RT",
    19: "[GPU] GPU-RMQ (CL) CUDA",
    20: "[GPU] GPU-RMQ (VL)",
    21: "[GPU] GPU-RMQ (CL) OptiX without RT",
    24: "[GPU] GPU-RMQ (CL) multi load",
}
AUTHOR_PAPER_WORKLOADS = {
    "query_count": "2^26 in paper scripts",
    "array_exponents": "2^20 through 2^31 in paper plot scripts",
    "range_distributions": {
        -1: "uniform / large ranges",
        -2: "lognormal / medium ranges",
        -3: "lognormal / small ranges",
        -6: "mixed large, medium, and small ranges",
    },
    "primary_gpu_rmq_algorithms": (16, 20),
    "comparison_algorithms": (1, 2, 5, 16, 20),
}
PREDECESSOR_PAPER = {
    "title": "Accelerating Range Minimum Queries with Ray Tracing Cores",
    "arxiv": "https://arxiv.org/abs/2306.03282",
    "relationship": (
        "Existing RTDL RTXRMQ-era scripts cover closest-hit and threshold-hitcount "
        "ideas. GPU-RMQ should not regress to a closest-hit-only benchmark."
    ),
}
CLAIM_BOUNDARY = {
    "benchmark_app": False,
    "front_door_only": True,
    "demoted_from_benchmark_candidate": True,
    "demotion_evidence": "docs/reports/goal2612_gpu_rmq_grouped_candidate_argmin_vs_cuda_2026-05-25.md",
    "full_gpu_rmq_reproduction": False,
    "paper_code_evidence": False,
    "author_code_available": True,
    "author_static_datasets_available": False,
    "author_generated_inputs_supported": True,
    "paper_rt_lowering_path": True,
    "optix_generic_closest_hit_source_wired": True,
    "optix_generic_closest_hit_ready": True,
    "cupy_partner_path": True,
    "native_engine_customization": False,
    "rt_core_speedup_claim_authorized": False,
    "public_speedup_claim_authorized": False,
}


_CUPY_KERNELS: dict[str, Any] = {}


@dataclass(frozen=True)
class RMQFixture:
    dataset: str
    values: tuple[float, ...]
    queries: tuple[tuple[int, int], ...]
    seed: int

    def metadata(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "value_count": len(self.values),
            "query_count": len(self.queries),
            "seed": self.seed,
            "dtype": "float64",
        }


@dataclass(frozen=True)
class BlockSparseTable:
    block_size: int
    block_min_values: tuple[float, ...]
    block_arg_indices: tuple[int, ...]
    sparse_values: tuple[tuple[float, ...], ...]
    sparse_indices: tuple[tuple[int, ...], ...]

    def metadata(self) -> dict[str, Any]:
        return {
            "block_size": self.block_size,
            "block_count": len(self.block_min_values),
            "sparse_levels": len(self.sparse_values),
            "summary_value_count": int(sum(len(level) for level in self.sparse_values)),
        }


@dataclass(frozen=True)
class PaperHybridRmqHierarchy:
    reduction_factor: int
    scan_threshold: int
    level_values: tuple[tuple[float, ...], ...]
    level_arg_indices: tuple[tuple[int, ...], ...]

    @property
    def top_level(self) -> int:
        return len(self.level_values) - 1

    @property
    def top_group_span(self) -> int:
        return self.reduction_factor ** self.top_level

    def metadata(self) -> dict[str, Any]:
        return {
            "reduction_factor": int(self.reduction_factor),
            "scan_threshold": int(self.scan_threshold),
            "level_count": len(self.level_values),
            "level_sizes": [len(level) for level in self.level_values],
            "top_level": int(self.top_level),
            "top_group_span": int(self.top_group_span),
            "paper_contract": (
                "GPU-RMQ-style hierarchy: each level stores minima over fixed-size "
                "groups from the previous level; query scheduling scans edge "
                "fragments at lower levels and uses RTDL for the coarsest fully "
                "contained range."
            ),
        }


@dataclass(frozen=True)
class RtdlRtRmqScene:
    block_size: int
    block_grid_width: int
    value_count: int
    ray_origin_x: float
    ray_tmax: float
    tie_break_epsilon: float
    combined_element_z_offset: float
    combined_block_triangle_id_offset: int
    block_min_values: tuple[float, ...]
    block_arg_indices: tuple[int, ...]
    block_triangles: tuple[Triangle3D, ...]
    element_triangles: tuple[Triangle3D, ...]
    combined_triangles: tuple[Triangle3D, ...]

    def metadata(self) -> dict[str, Any]:
        return {
            "block_size": self.block_size,
            "block_count": len(self.block_min_values),
            "block_grid_width": self.block_grid_width,
            "value_count": self.value_count,
            "block_triangle_count": len(self.block_triangles),
            "element_triangle_count": len(self.element_triangles),
            "combined_triangle_count": len(self.combined_triangles),
            "ray_origin_x": self.ray_origin_x,
            "ray_tmax": self.ray_tmax,
            "tie_break_epsilon": self.tie_break_epsilon,
            "combined_element_z_offset": self.combined_element_z_offset,
            "combined_block_triangle_id_offset": self.combined_block_triangle_id_offset,
            "geometry_contract": (
                "paper-style RT lowering: array values are encoded as triangle x/t distance; "
                "query intervals become +x rays at encoded y/z coordinates; closest-hit "
                "primitive id is decoded app-side. A tiny app-side x offset preserves "
                "leftmost-tie RMQ semantics without changing value ordering."
            ),
        }


@dataclass(frozen=True)
class RtdlRtRmqRayPhase:
    phase: str
    ray_ids: tuple[int, ...]
    ys: tuple[float, ...]
    zs: tuple[float, ...]

    @property
    def ray_count(self) -> int:
        return len(self.ray_ids)

    def as_rays(self, scene: RtdlRtRmqScene) -> tuple[Ray3D, ...]:
        return tuple(
            _paper_rt_ray(ray_id, scene, y, z)
            for ray_id, y, z in zip(self.ray_ids, self.ys, self.zs)
        )


@dataclass(frozen=True)
class RtdlRtRmqScheduledRays:
    phases: tuple[RtdlRtRmqRayPhase, ...]
    full_phase: RtdlRtRmqRayPhase
    ray_map: dict[int, tuple[int, str]]
    query_count: int
    total_ray_count: int


def _better_pair(
    left_value: float | None,
    left_index: int | None,
    right_value: float,
    right_index: int,
) -> tuple[float, int]:
    if left_value is None or left_index is None:
        return float(right_value), int(right_index)
    if right_value < left_value:
        return float(right_value), int(right_index)
    if right_value == left_value and right_index < left_index:
        return float(right_value), int(right_index)
    return float(left_value), int(left_index)


def validate_query(query: tuple[int, int], value_count: int) -> None:
    left, right = query
    if left < 0 or right < left or right >= value_count:
        raise ValueError(f"invalid RMQ query {query!r} for {value_count} values")


def make_values(count: int, *, seed: int, dataset: str) -> tuple[float, ...]:
    if count < 1:
        raise ValueError("value count must be positive")
    rng = random.Random(seed)
    if dataset == "random":
        return tuple(rng.random() for _ in range(count))
    if dataset == "repeated":
        return tuple(float(rng.randrange(max(4, count // 16))) for _ in range(count))
    if dataset == "sawtooth":
        period = max(4, int(math.sqrt(count)))
        return tuple(float(i % period) + rng.random() * 1e-6 for i in range(count))
    if dataset == "descending_blocks":
        block = max(4, int(math.sqrt(count)))
        return tuple(float((i // block) * block + (block - (i % block))) for i in range(count))
    raise ValueError(f"unsupported dataset: {dataset}")


def make_queries(count: int, value_count: int, *, seed: int, max_width: int) -> tuple[tuple[int, int], ...]:
    if count < 1:
        raise ValueError("query count must be positive")
    if value_count < 1:
        raise ValueError("value count must be positive")
    width_bound = min(max(1, max_width), value_count)
    rng = random.Random(seed)
    queries: list[tuple[int, int]] = []
    for _ in range(count):
        width = rng.randrange(1, width_bound + 1)
        left = rng.randrange(0, value_count - width + 1)
        queries.append((left, left + width - 1))
    return tuple(queries)


def _bounded_lognormal_width(rng: random.Random, *, scale: float, value_count: int) -> int:
    while True:
        width = int(rng.lognormvariate(math.log(max(1.0, scale)), 0.3))
        if 1 <= width <= value_count:
            return width


def _author_style_width(rng: random.Random, *, lr: int, value_count: int) -> int:
    if lr > 0:
        return min(lr, value_count)
    if lr == -1:
        return rng.randrange(1, value_count + 1)
    if lr == -2:
        return _bounded_lognormal_width(rng, scale=value_count**0.6, value_count=value_count)
    if lr == -3:
        return _bounded_lognormal_width(rng, scale=value_count**0.3, value_count=value_count)
    if lr == -6:
        return _author_style_width(rng, lr=-(rng.randrange(0, 3) + 1), value_count=value_count)
    raise ValueError(f"unsupported author-style lr: {lr}")


def make_author_style_queries(
    count: int,
    value_count: int,
    *,
    seed: int,
    lr: int,
) -> tuple[tuple[int, int], ...]:
    if count < 1:
        raise ValueError("query count must be positive")
    if value_count < 1:
        raise ValueError("value count must be positive")
    rng = random.Random(seed)
    queries: list[tuple[int, int]] = []
    for _ in range(count):
        width = _author_style_width(rng, lr=lr, value_count=value_count)
        left = rng.randrange(0, value_count - width + 1)
        queries.append((left, left + width - 1))
    return tuple(queries)


def make_fixture(
    *,
    dataset: str,
    value_count: int,
    query_count: int,
    seed: int,
    max_width: int,
) -> RMQFixture:
    values = make_values(value_count, seed=seed, dataset=dataset)
    queries = make_queries(query_count, value_count, seed=seed + 1, max_width=max_width)
    return RMQFixture(dataset=dataset, values=values, queries=queries, seed=seed)


def make_author_style_fixture(
    *,
    value_count: int,
    query_count: int,
    seed: int,
    lr: int,
) -> RMQFixture:
    values = make_values(value_count, seed=seed, dataset="random")
    queries = make_author_style_queries(query_count, value_count, seed=seed + 1, lr=lr)
    return RMQFixture(dataset=f"author_style_lr_{lr}", values=values, queries=queries, seed=seed)


def read_author_array_bin(path: Path, *, value_count: int | None = None) -> tuple[float, ...]:
    data = path.read_bytes()
    if len(data) % 4 != 0:
        raise ValueError(f"author array binary size must be a multiple of 4 bytes: {path}")
    count = len(data) // 4
    if value_count is not None and count != value_count:
        raise ValueError(f"author array binary has {count} float32 values, expected {value_count}")
    return tuple(float(value) for value in struct.unpack(f"<{count}f", data))


def read_author_queries_bin(
    path: Path,
    *,
    query_count: int | None = None,
    index_width: int = 32,
) -> tuple[tuple[int, int], ...]:
    data = path.read_bytes()
    if index_width == 32:
        item_size = 8
        fmt_code = "I"
    elif index_width == 64:
        item_size = 16
        fmt_code = "Q"
    else:
        raise ValueError("index_width must be 32 or 64")
    if len(data) % item_size != 0:
        raise ValueError(f"author query binary size must be a multiple of {item_size} bytes: {path}")
    count = len(data) // item_size
    if query_count is not None and count != query_count:
        raise ValueError(f"author query binary has {count} queries, expected {query_count}")
    unpacked = struct.unpack(f"<{count * 2}{fmt_code}", data)
    return tuple((int(unpacked[i]), int(unpacked[i + 1])) for i in range(0, len(unpacked), 2))


def make_author_saved_input_fixture(
    *,
    array_bin: Path,
    queries_bin: Path,
    seed: int,
    value_count: int | None = None,
    query_count: int | None = None,
    index_width: int = 32,
) -> RMQFixture:
    values = read_author_array_bin(array_bin, value_count=value_count)
    queries = read_author_queries_bin(queries_bin, query_count=query_count, index_width=index_width)
    return RMQFixture(dataset="author_saved_input", values=values, queries=queries, seed=seed)


def _argmin_range(values: tuple[float, ...], left: int, right: int) -> int:
    best_index = left
    best_value = values[left]
    for index in range(left + 1, right + 1):
        value = values[index]
        if value < best_value:
            best_value = value
            best_index = index
    return best_index


def exact_rmq_cpu(values: tuple[float, ...], queries: tuple[tuple[int, int], ...]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for query_id, (left, right) in enumerate(queries):
        validate_query((left, right), len(values))
        index = _argmin_range(values, left, right)
        rows.append(
            {
                "query_id": query_id,
                "left": int(left),
                "right": int(right),
                "index": int(index),
                "value": float(values[index]),
            }
        )
    return tuple(rows)


def build_block_sparse_table(values: tuple[float, ...], *, block_size: int) -> BlockSparseTable:
    if block_size < 1:
        raise ValueError("block_size must be positive")
    block_values: list[float] = []
    block_indices: list[int] = []
    for start in range(0, len(values), block_size):
        stop = min(start + block_size, len(values))
        index = _argmin_range(values, start, stop - 1)
        block_values.append(float(values[index]))
        block_indices.append(index)

    level_values = tuple(block_values)
    level_indices = tuple(block_indices)
    sparse_values = [level_values]
    sparse_indices = [level_indices]
    length = 1
    while length * 2 <= len(sparse_values[-1]):
        prev_values = sparse_values[-1]
        prev_indices = sparse_indices[-1]
        next_size = len(prev_values) - length
        next_values: list[float] = []
        next_indices: list[int] = []
        for i in range(next_size):
            value, index = _better_pair(
                float(prev_values[i]),
                int(prev_indices[i]),
                float(prev_values[i + length]),
                int(prev_indices[i + length]),
            )
            next_values.append(value)
            next_indices.append(index)
        sparse_values.append(tuple(next_values))
        sparse_indices.append(tuple(next_indices))
        length *= 2

    return BlockSparseTable(
        block_size=block_size,
        block_min_values=sparse_values[0],
        block_arg_indices=sparse_indices[0],
        sparse_values=tuple(sparse_values),
        sparse_indices=tuple(sparse_indices),
    )


def _scan_segment(values: tuple[float, ...], left: int, right: int) -> tuple[float, int]:
    index = _argmin_range(values, left, right)
    return float(values[index]), int(index)


def _query_block_sparse_table(table: BlockSparseTable, first_block: int, last_block: int) -> tuple[float, int]:
    if first_block > last_block:
        raise ValueError("empty full-block query")
    block_count = last_block - first_block + 1
    level = int(math.floor(math.log2(block_count)))
    width = 1 << level
    left_value = float(table.sparse_values[level][first_block])
    left_index = int(table.sparse_indices[level][first_block])
    right_start = last_block - width + 1
    right_value = float(table.sparse_values[level][right_start])
    right_index = int(table.sparse_indices[level][right_start])
    return _better_pair(left_value, left_index, right_value, right_index)


def hierarchical_rmq_local(
    values: tuple[float, ...],
    queries: tuple[tuple[int, int], ...],
    *,
    block_size: int,
) -> tuple[tuple[dict[str, Any], ...], BlockSparseTable]:
    table = build_block_sparse_table(values, block_size=block_size)
    rows: list[dict[str, Any]] = []
    for query_id, (left, right) in enumerate(queries):
        validate_query((left, right), len(values))
        left_block = left // block_size
        right_block = right // block_size
        best_value: float | None = None
        best_index: int | None = None
        if left_block == right_block:
            best_value, best_index = _scan_segment(values, left, right)
        else:
            value, index = _scan_segment(values, left, min((left_block + 1) * block_size - 1, right))
            best_value, best_index = _better_pair(best_value, best_index, value, index)
            value, index = _scan_segment(values, right_block * block_size, right)
            best_value, best_index = _better_pair(best_value, best_index, value, index)
            if left_block + 1 <= right_block - 1:
                value, index = _query_block_sparse_table(table, left_block + 1, right_block - 1)
                best_value, best_index = _better_pair(best_value, best_index, value, index)
        rows.append(
            {
                "query_id": query_id,
                "left": int(left),
                "right": int(right),
                "index": int(best_index),
                "value": float(best_value),
            }
        )
    return tuple(rows), table


def build_paper_hybrid_hierarchy(
    values: tuple[float, ...],
    *,
    reduction_factor: int,
    scan_threshold: int,
) -> PaperHybridRmqHierarchy:
    if not values:
        raise ValueError("values must be non-empty")
    if reduction_factor < 2:
        raise ValueError("reduction_factor must be at least 2")
    if scan_threshold < 2 * reduction_factor:
        raise ValueError("scan_threshold must be at least 2 * reduction_factor")

    level_values: list[tuple[float, ...]] = [tuple(float(value) for value in values)]
    level_indices: list[tuple[int, ...]] = [tuple(range(len(values)))]
    size = len(values)
    while size > scan_threshold:
        previous_values = level_values[-1]
        previous_indices = level_indices[-1]
        next_values: list[float] = []
        next_indices: list[int] = []
        for start in range(0, size, reduction_factor):
            stop = min(start + reduction_factor, size)
            best_value: float | None = None
            best_index: int | None = None
            for offset in range(start, stop):
                best_value, best_index = _better_pair(
                    best_value,
                    best_index,
                    previous_values[offset],
                    previous_indices[offset],
                )
            next_values.append(float(best_value))
            next_indices.append(int(best_index))
        level_values.append(tuple(next_values))
        level_indices.append(tuple(next_indices))
        size = len(next_values)

    return PaperHybridRmqHierarchy(
        reduction_factor=int(reduction_factor),
        scan_threshold=int(scan_threshold),
        level_values=tuple(level_values),
        level_arg_indices=tuple(level_indices),
    )


def _scan_hybrid_level_segment(
    hierarchy: PaperHybridRmqHierarchy,
    level: int,
    left: int,
    right_exclusive: int,
) -> tuple[float, int] | None:
    if right_exclusive <= left:
        return None
    values = hierarchy.level_values[level]
    indices = hierarchy.level_arg_indices[level]
    if left < 0 or right_exclusive > len(values):
        raise ValueError(f"invalid level segment [{left}, {right_exclusive}) at level {level}")
    best_value: float | None = None
    best_index: int | None = None
    for offset in range(left, right_exclusive):
        best_value, best_index = _better_pair(
            best_value,
            best_index,
            values[offset],
            indices[offset],
        )
    return (float(best_value), int(best_index))


@dataclass(frozen=True)
class _HybridLevelMinTable:
    values_by_power: tuple[Any, ...]
    indices_by_power: tuple[Any, ...]


def _build_hybrid_level_min_table(np, values: tuple[float, ...], indices: tuple[int, ...]) -> _HybridLevelMinTable:
    value_levels = [np.asarray(values, dtype=np.float64)]
    index_levels = [np.asarray(indices, dtype=np.int64)]
    width = 1
    while width * 2 <= len(values):
        left_values = value_levels[-1][:-width]
        right_values = value_levels[-1][width:]
        left_indices = index_levels[-1][:-width]
        right_indices = index_levels[-1][width:]
        take_right = (right_values < left_values) | (
            (right_values == left_values) & (right_indices < left_indices)
        )
        value_levels.append(np.where(take_right, right_values, left_values))
        index_levels.append(np.where(take_right, right_indices, left_indices))
        width *= 2
    return _HybridLevelMinTable(
        values_by_power=tuple(value_levels),
        indices_by_power=tuple(index_levels),
    )


def _query_hybrid_level_min_table(
    table: _HybridLevelMinTable,
    left: int,
    right_exclusive: int,
) -> tuple[float, int] | None:
    if right_exclusive <= left:
        return None
    length = right_exclusive - left
    power = length.bit_length() - 1
    offset = right_exclusive - (1 << power)
    values = table.values_by_power[power]
    indices = table.indices_by_power[power]
    left_value = float(values[left])
    left_index = int(indices[left])
    right_value = float(values[offset])
    right_index = int(indices[offset])
    return _better_pair(left_value, left_index, right_value, right_index)


def _query_hybrid_level_min_table_batch(np, table: _HybridLevelMinTable, lefts, rights):
    lefts = np.asarray(lefts, dtype=np.int64)
    rights = np.asarray(rights, dtype=np.int64)
    lengths = rights - lefts
    if bool((lengths <= 0).any()):
        raise ValueError("batched hierarchy segments must be non-empty")
    powers = np.floor(np.log2(lengths.astype(np.float64))).astype(np.int64)
    out_values = np.empty(lefts.shape[0], dtype=np.float64)
    out_indices = np.empty(lefts.shape[0], dtype=np.int64)
    for power in np.unique(powers):
        mask = powers == power
        width = 1 << int(power)
        offsets = rights[mask] - width
        values = table.values_by_power[int(power)]
        indices = table.indices_by_power[int(power)]
        left_values = values[lefts[mask]]
        left_indices = indices[lefts[mask]]
        right_values = values[offsets]
        right_indices = indices[offsets]
        take_right = (right_values < left_values) | (
            (right_values == left_values) & (right_indices < left_indices)
        )
        out_values[mask] = np.where(take_right, right_values, left_values)
        out_indices[mask] = np.where(take_right, right_indices, left_indices)
    return out_values, out_indices


def _paper_hybrid_top_rt_query(
    left: int,
    right: int,
    hierarchy: PaperHybridRmqHierarchy,
) -> tuple[int, int] | None:
    if hierarchy.top_level <= 0:
        return None
    span = hierarchy.top_group_span
    rt_left = (left + span - 1) // span
    rt_right = ((right + 1) // span) - 1
    if rt_left > rt_right:
        return None
    return int(rt_left), int(rt_right)


def _paper_hybrid_partner_scan_candidates(
    hierarchy: PaperHybridRmqHierarchy,
    left: int,
    right: int,
) -> tuple[tuple[float, int], ...]:
    current_left = int(left)
    current_right = int(right) + 1
    current_level = 0
    candidates: list[tuple[float, int]] = []
    factor = hierarchy.reduction_factor
    while current_level < hierarchy.top_level:
        if current_right - current_left <= hierarchy.scan_threshold:
            break
        next_left = ((current_left + factor - 1) // factor) * factor
        prev_right = (current_right // factor) * factor
        if prev_right < next_left:
            break
        left_candidate = _scan_hybrid_level_segment(
            hierarchy,
            current_level,
            current_left,
            next_left,
        )
        if left_candidate is not None:
            candidates.append(left_candidate)
        right_candidate = _scan_hybrid_level_segment(
            hierarchy,
            current_level,
            prev_right,
            current_right,
        )
        if right_candidate is not None:
            candidates.append(right_candidate)
        current_left = next_left // factor
        current_right = prev_right // factor
        current_level += 1

    if current_level < hierarchy.top_level or hierarchy.top_level == 0:
        final_candidate = _scan_hybrid_level_segment(
            hierarchy,
            current_level,
            current_left,
            current_right,
        )
        if final_candidate is not None:
            candidates.append(final_candidate)
    return tuple(candidates)


@dataclass(frozen=True)
class PreparedPaperHybridRmqQueryBatch:
    queries: tuple[tuple[int, int], ...]
    rt_query_ids: tuple[int, ...]
    rt_top_queries: tuple[tuple[int, int], ...]
    rt_query_batch: Any
    partner_qids: Any
    partner_values: Any
    partner_indices: Any
    partner_prepared_grouped_argmin: Any
    partner_candidate_count: int
    prepare_seconds: float

    @property
    def query_count(self) -> int:
        return len(self.queries)

    def close(self) -> None:
        if self.rt_query_batch is not None and hasattr(self.rt_query_batch, "close"):
            self.rt_query_batch.close()
        if self.partner_prepared_grouped_argmin is not None and hasattr(self.partner_prepared_grouped_argmin, "close"):
            self.partner_prepared_grouped_argmin.close()


class PreparedPaperHybridRtdlPartnerRmq:
    """Reusable app-side GPU-RMQ-style hierarchy plus generic RTDL top-level RT."""

    def __init__(
        self,
        values: tuple[float, ...],
        *,
        reduction_factor: int,
        scan_threshold: int,
        rt_top_block_size: int = 1,
    ) -> None:
        self.values = tuple(float(value) for value in values)
        self.hierarchy = build_paper_hybrid_hierarchy(
            self.values,
            reduction_factor=reduction_factor,
            scan_threshold=scan_threshold,
        )
        self.rt_top_block_size = int(rt_top_block_size)
        self._closed = False
        self._top_prepared: PreparedPaperRtRmq | None = None
        self._np = None
        self._level_min_tables: tuple[_HybridLevelMinTable, ...] | None = None
        self._partner_mode = "python_app_scan"
        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError:
            pass
        else:
            self._np = np
            self._level_min_tables = tuple(
                _build_hybrid_level_min_table(np, values_at_level, indices_at_level)
                for values_at_level, indices_at_level in zip(
                    self.hierarchy.level_values,
                    self.hierarchy.level_arg_indices,
                    strict=True,
                )
            )
            self._partner_mode = "numpy_level_sparse_table_batch"
        self.prepare_seconds = 0.0
        self.last_query_metadata: dict[str, Any] = {}
        if self.hierarchy.top_level > 0:
            prepare_start = time.perf_counter()
            self._top_prepared = prepare_paper_rt_lowered_rmq(
                self.hierarchy.level_values[-1],
                block_size=self.rt_top_block_size,
            )
            self.prepare_seconds += time.perf_counter() - prepare_start

    def _scan_partner_level_segment(
        self,
        level: int,
        left: int,
        right_exclusive: int,
    ) -> tuple[float, int] | None:
        if self._level_min_tables is not None:
            return _query_hybrid_level_min_table(self._level_min_tables[level], left, right_exclusive)
        return _scan_hybrid_level_segment(self.hierarchy, level, left, right_exclusive)

    def _partner_scan_candidates(self, left: int, right: int) -> tuple[tuple[float, int], ...]:
        current_left = int(left)
        current_right = int(right) + 1
        current_level = 0
        candidates: list[tuple[float, int]] = []
        factor = self.hierarchy.reduction_factor
        while current_level < self.hierarchy.top_level:
            if current_right - current_left <= self.hierarchy.scan_threshold:
                break
            next_left = ((current_left + factor - 1) // factor) * factor
            prev_right = (current_right // factor) * factor
            if prev_right < next_left:
                break
            left_candidate = self._scan_partner_level_segment(current_level, current_left, next_left)
            if left_candidate is not None:
                candidates.append(left_candidate)
            right_candidate = self._scan_partner_level_segment(current_level, prev_right, current_right)
            if right_candidate is not None:
                candidates.append(right_candidate)
            current_left = next_left // factor
            current_right = prev_right // factor
            current_level += 1

        if current_level < self.hierarchy.top_level or self.hierarchy.top_level == 0:
            final_candidate = self._scan_partner_level_segment(current_level, current_left, current_right)
            if final_candidate is not None:
                candidates.append(final_candidate)
        return tuple(candidates)

    def _partner_scan_candidate_arrays(self, queries: tuple[tuple[int, int], ...]):
        if self._np is None or self._level_min_tables is None:
            return None
        np = self._np
        qid_parts: list[int] = []
        level_parts: list[int] = []
        left_parts: list[int] = []
        right_parts: list[int] = []
        factor = self.hierarchy.reduction_factor

        def append_segment(query_id: int, level: int, left: int, right_exclusive: int) -> None:
            if right_exclusive <= left:
                return
            qid_parts.append(int(query_id))
            level_parts.append(int(level))
            left_parts.append(int(left))
            right_parts.append(int(right_exclusive))

        for query_id, (left, right) in enumerate(queries):
            current_left = int(left)
            current_right = int(right) + 1
            current_level = 0
            while current_level < self.hierarchy.top_level:
                if current_right - current_left <= self.hierarchy.scan_threshold:
                    break
                next_left = ((current_left + factor - 1) // factor) * factor
                prev_right = (current_right // factor) * factor
                if prev_right < next_left:
                    break
                append_segment(query_id, current_level, current_left, next_left)
                append_segment(query_id, current_level, prev_right, current_right)
                current_left = next_left // factor
                current_right = prev_right // factor
                current_level += 1
            if current_level < self.hierarchy.top_level or self.hierarchy.top_level == 0:
                append_segment(query_id, current_level, current_left, current_right)

        if not qid_parts:
            return (
                np.empty(0, dtype=np.int64),
                np.empty(0, dtype=np.float64),
                np.empty(0, dtype=np.int64),
            )

        qids = np.asarray(qid_parts, dtype=np.int64)
        levels = np.asarray(level_parts, dtype=np.int64)
        lefts = np.asarray(left_parts, dtype=np.int64)
        rights = np.asarray(right_parts, dtype=np.int64)
        values = np.empty(qids.shape[0], dtype=np.float64)
        indices = np.empty(qids.shape[0], dtype=np.int64)
        for level in np.unique(levels):
            mask = levels == level
            level_values, level_indices = _query_hybrid_level_min_table_batch(
                np,
                self._level_min_tables[int(level)],
                lefts[mask],
                rights[mask],
            )
            values[mask] = level_values
            indices[mask] = level_indices
        return qids, values, indices

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._top_prepared is not None:
            self._top_prepared.close()

    def __enter__(self) -> "PreparedPaperHybridRtdlPartnerRmq":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def prepare_query_batch(self, queries: tuple[tuple[int, int], ...]) -> PreparedPaperHybridRmqQueryBatch:
        if self._closed:
            raise RuntimeError("prepared paper hybrid RMQ handle is closed")
        prepare_start = time.perf_counter()
        queries_tuple = tuple(queries)
        rt_query_ids: list[int] = []
        rt_top_queries: list[tuple[int, int]] = []
        for query_id, (left, right) in enumerate(queries_tuple):
            validate_query((left, right), len(self.values))
            top_query = _paper_hybrid_top_rt_query(left, right, self.hierarchy)
            if top_query is not None:
                rt_query_ids.append(query_id)
                rt_top_queries.append(top_query)
        rt_query_batch = None
        if rt_top_queries and self._top_prepared is not None:
            rt_query_batch = self._top_prepared.prepare_query_batch(tuple(rt_top_queries))
        partner_qids = None
        partner_values = None
        partner_indices = None
        partner_prepared_grouped_argmin = None
        partner_candidate_count = 0
        if self._np is not None and self._level_min_tables is not None:
            partner_arrays = self._partner_scan_candidate_arrays(queries_tuple)
            if partner_arrays is not None:
                partner_qids, partner_values, partner_indices = partner_arrays
                partner_candidate_count = int(partner_qids.size)
                try:
                    from rtdsl.optix_runtime import prepare_optix_grouped_candidate_argmin

                    partner_prepared_grouped_argmin = prepare_optix_grouped_candidate_argmin(
                        partner_qids,
                        partner_values,
                        partner_indices,
                        group_count=len(queries_tuple),
                        allow_numpy_fallback=True,
                    )
                except RuntimeError:
                    partner_prepared_grouped_argmin = None
        return PreparedPaperHybridRmqQueryBatch(
            queries=queries_tuple,
            rt_query_ids=tuple(rt_query_ids),
            rt_top_queries=tuple(rt_top_queries),
            rt_query_batch=rt_query_batch,
            partner_qids=partner_qids,
            partner_values=partner_values,
            partner_indices=partner_indices,
            partner_prepared_grouped_argmin=partner_prepared_grouped_argmin,
            partner_candidate_count=partner_candidate_count,
            prepare_seconds=float(time.perf_counter() - prepare_start),
        )

    def query_prepared_batch(self, batch: PreparedPaperHybridRmqQueryBatch) -> tuple[tuple[int, ...], tuple[float, ...]]:
        if self._closed:
            raise RuntimeError("prepared paper hybrid RMQ handle is closed")
        query_start = time.perf_counter()
        if self._np is not None and self._level_min_tables is not None:
            np = self._np
            best_values_np = np.full(batch.query_count, np.inf, dtype=np.float64)
            best_indices_np = np.full(batch.query_count, np.iinfo(np.int64).max, dtype=np.int64)

            def accept_arrays(qids, values, indices) -> None:
                if qids.size == 0:
                    return
                order = np.lexsort((indices, values, qids))
                sorted_qids = qids[order]
                sorted_values = values[order]
                sorted_indices = indices[order]
                first = np.empty(sorted_qids.size, dtype=bool)
                first[0] = True
                first[1:] = sorted_qids[1:] != sorted_qids[:-1]
                reduced_qids = sorted_qids[first]
                reduced_values = sorted_values[first]
                reduced_indices = sorted_indices[first]
                current_values = best_values_np[reduced_qids]
                current_indices = best_indices_np[reduced_qids]
                take = (reduced_values < current_values) | (
                    (reduced_values == current_values) & (reduced_indices < current_indices)
                )
                if bool(take.any()):
                    best_values_np[reduced_qids[take]] = reduced_values[take]
                    best_indices_np[reduced_qids[take]] = reduced_indices[take]

            def accept_group_result(result: dict[str, Any]) -> None:
                has_value = np.asarray(result["has_value"], dtype=bool)
                if has_value.size == 0 or not bool(has_value.any()):
                    return
                qids = np.nonzero(has_value)[0].astype(np.int64, copy=False)
                values = np.asarray(result["value"], dtype=np.float64)[has_value]
                indices = np.asarray(result["index"], dtype=np.int64)[has_value]
                current_values = best_values_np[qids]
                current_indices = best_indices_np[qids]
                take = (values < current_values) | (
                    (values == current_values) & (indices < current_indices)
                )
                if bool(take.any()):
                    best_values_np[qids[take]] = values[take]
                    best_indices_np[qids[take]] = indices[take]

            if batch.partner_qids is None or batch.partner_values is None or batch.partner_indices is None:
                raise RuntimeError("prepared batched partner arrays unavailable despite NumPy partner mode")
            partner_candidate_count = int(batch.partner_candidate_count)
            partner_finalize_metadata: dict[str, Any] = {}
            if batch.partner_prepared_grouped_argmin is not None:
                partner_result = batch.partner_prepared_grouped_argmin.finalize()
                accept_group_result(partner_result)
                partner_finalize_metadata = dict(partner_result.get("metadata", {}))
            else:
                accept_arrays(batch.partner_qids, batch.partner_values, batch.partner_indices)
        else:
            best_values: list[float | None] = [None] * batch.query_count
            best_indices: list[int | None] = [None] * batch.query_count

            def accept(query_id: int, candidate: tuple[float, int]) -> None:
                best_values[query_id], best_indices[query_id] = _better_pair(
                    best_values[query_id],
                    best_indices[query_id],
                    candidate[0],
                    candidate[1],
                )

            partner_candidate_count = 0
            partner_finalize_metadata = {}
            for query_id, (left, right) in enumerate(batch.queries):
                for candidate in self._partner_scan_candidates(left, right):
                    partner_candidate_count += 1
                    accept(query_id, candidate)

        rt_metadata: dict[str, Any] = {"rt_query_count": 0, "rt_used": False}
        if batch.rt_query_batch is not None and self._top_prepared is not None:
            top_hit_indices, top_hit_values = self._top_prepared.query_prepared_batch_arrays(batch.rt_query_batch)
            top_indices = self.hierarchy.level_arg_indices[-1]
            if self._np is not None and self._level_min_tables is not None:
                np = self._np
                rt_qids = np.asarray(batch.rt_query_ids, dtype=np.int64)
                rt_values = np.asarray(top_hit_values, dtype=np.float64)
                rt_indices = np.asarray(
                    [int(top_indices[int(top_index)]) for top_index in top_hit_indices],
                    dtype=np.int64,
                )
                accept_arrays(rt_qids, rt_values, rt_indices)
            else:
                for row_id, query_id in enumerate(batch.rt_query_ids):
                    top_index = int(top_hit_indices[row_id])
                    accept(query_id, (float(top_hit_values[row_id]), int(top_indices[top_index])))
            rt_metadata = {
                "rt_query_count": len(batch.rt_query_ids),
                "rt_used": True,
                "rt_top_block_size": int(self.rt_top_block_size),
                "rt_top_value_count": len(self.hierarchy.level_values[-1]),
                "last_query_metadata": dict(self._top_prepared.last_query_metadata),
                "scene": self._top_prepared.scene.metadata(),
            }

        output_indices: list[int] = []
        output_values: list[float] = []
        if self._np is not None and self._level_min_tables is not None:
            np = self._np
            missing_mask = best_indices_np == np.iinfo(np.int64).max
            if bool(missing_mask.any()):
                missing = int(np.where(missing_mask)[0][0])
                raise RuntimeError(f"paper hybrid query produced no candidate for query {missing}")
            output_indices = [int(value) for value in best_indices_np]
            output_values = [float(value) for value in best_values_np]
        else:
            for query_id in range(batch.query_count):
                if best_values[query_id] is None or best_indices[query_id] is None:
                    raise RuntimeError(f"paper hybrid query produced no candidate for query {query_id}")
                output_indices.append(int(best_indices[query_id]))
                output_values.append(float(best_values[query_id]))

        self.last_query_metadata = {
            "prepared_reused": True,
            "prepared_app_handle": True,
            "prepared_query_batch": True,
            "prepare_seconds": float(self.prepare_seconds),
            "query_batch_prepare_seconds": float(batch.prepare_seconds),
            "query_total_seconds": float(time.perf_counter() - query_start),
            "query_count": int(batch.query_count),
            "hierarchy": self.hierarchy.metadata(),
            "partner": {
                "mode": (
                    "generic_grouped_candidate_argmin"
                    if partner_finalize_metadata
                    else self._partner_mode
                ),
                "candidate_count": int(partner_candidate_count),
                "candidate_finalize": partner_finalize_metadata,
                "contract": (
                    "App-side partner answers lower-level edge fragments and final "
                    "small ranges. A NumPy sparse-table partner removes per-element "
                    "Python scans when NumPy is available; the generic grouped "
                    "candidate argmin primitive finalizes raw partner candidates "
                    "without giving the native engine RMQ semantics."
                ),
            },
            "rt": rt_metadata,
            "native_engine_customization": False,
            "paper_algorithm_family": "GPU-RMQ CL/Interleaved-style hybrid hierarchy plus top-level RT",
        }
        return tuple(output_indices), tuple(output_values)

    def query(self, queries: tuple[tuple[int, int], ...]) -> tuple[dict[str, Any], ...]:
        batch = self.prepare_query_batch(queries)
        try:
            indices, values = self.query_prepared_batch(batch)
        finally:
            batch.close()
        return tuple(
            {
                "query_id": int(query_id),
                "left": int(queries[query_id][0]),
                "right": int(queries[query_id][1]),
                "index": int(indices[query_id]),
                "value": float(values[query_id]),
            }
            for query_id in range(len(queries))
        )


def paper_hybrid_rtdl_partner_rmq(
    values: tuple[float, ...],
    queries: tuple[tuple[int, int], ...],
    *,
    reduction_factor: int,
    scan_threshold: int,
    rt_top_block_size: int = 1,
) -> tuple[tuple[dict[str, Any], ...], PaperHybridRmqHierarchy, dict[str, Any]]:
    with PreparedPaperHybridRtdlPartnerRmq(
        values,
        reduction_factor=reduction_factor,
        scan_threshold=scan_threshold,
        rt_top_block_size=rt_top_block_size,
    ) as prepared:
        rows = prepared.query(queries)
        return rows, prepared.hierarchy, dict(prepared.last_query_metadata)


_PAPER_RMQ_BLOCK_SCALE = float(1 << 23)
# The native OptiX closest-hit path packs RT coordinates as f32, so interval
# boundary nudges must be large enough to survive f32 rounding at app-level
# grid coordinates while remaining far below one logical lane.
_PAPER_RMQ_EDGE_EPS = 1.0e-3
_PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD = 1


def _triangle_in_value_plane(
    triangle_id: int,
    value: float,
    yz0: tuple[float, float],
    yz1: tuple[float, float],
    yz2: tuple[float, float],
) -> Triangle3D:
    return Triangle3D(
        id=int(triangle_id),
        x0=float(value),
        y0=float(yz0[0]),
        z0=float(yz0[1]),
        x1=float(value),
        y1=float(yz1[0]),
        z1=float(yz1[1]),
        x2=float(value),
        y2=float(yz2[0]),
        z2=float(yz2[1]),
    )


def build_paper_rt_rmq_scene(values: tuple[float, ...], *, block_size: int) -> RtdlRtRmqScene:
    """Build the app-side RT geometry used by the GPU-RMQ/RTXRMQ papers.

    The native RTDL engine receives only 3-D triangles. RMQ-specific block
    decoding stays in this app.
    """
    if not values:
        raise ValueError("values must be non-empty")
    if block_size < 1:
        raise ValueError("block_size must be positive")

    sorted_unique_values = sorted({float(value) for value in values})
    positive_gaps = [
        sorted_unique_values[index + 1] - sorted_unique_values[index]
        for index in range(len(sorted_unique_values) - 1)
        if sorted_unique_values[index + 1] > sorted_unique_values[index]
    ]
    min_gap = min(positive_gaps) if positive_gaps else 1.0
    # Encode leftmost-tie semantics in x while preserving value ordering:
    # the largest possible index offset remains below half the nearest
    # positive value gap, and the per-index offset is large enough for f32
    # OptiX coordinates on the benchmark-scale fixtures.
    tie_break_epsilon = min_gap / max(2.0, 2.0 * float(len(values) + 1))

    def encoded_value(index: int) -> float:
        return float(values[index]) + tie_break_epsilon * float(index)

    block_min_values: list[float] = []
    block_arg_indices: list[int] = []
    for start in range(0, len(values), block_size):
        stop = min(start + block_size, len(values))
        index = _argmin_range(values, start, stop - 1)
        block_min_values.append(float(values[index]))
        block_arg_indices.append(int(index))

    block_count = len(block_min_values)
    grid_width = int(math.ceil(math.sqrt(block_count + 1)))
    block_triangles: list[Triangle3D] = []
    for block_id, value in enumerate(block_min_values):
        lower = float(block_id + 1) / _PAPER_RMQ_BLOCK_SCALE
        upper = float(block_id - 1) / _PAPER_RMQ_BLOCK_SCALE
        block_triangles.append(
            _triangle_in_value_plane(
                block_id,
                encoded_value(block_arg_indices[block_id]),
                (lower, upper),
                (lower, 2.0),
                (-1.0, upper),
            )
        )

    element_triangles: list[Triangle3D] = []
    for index, value in enumerate(values):
        block_id = index // block_size
        lane = index % block_size
        cell_x = (block_id + 1) % grid_width
        cell_y = (block_id + 1) // grid_width
        lower = float(lane + 1) / float(block_size) + 2.0 * float(cell_x)
        upper = float(lane - 1) / float(block_size) + 2.0 * float(cell_y)
        element_triangles.append(
            _triangle_in_value_plane(
                index,
                encoded_value(index),
                (lower, upper),
                (lower, 2.0 * float(cell_y) + 2.0),
                (2.0 * float(cell_x) - 1.0, upper),
            )
        )

    combined_element_z_offset = 3.0
    combined_block_triangle_id_offset = len(values)

    def translated_element_triangle_for_combined(triangle: Triangle3D) -> Triangle3D:
        return Triangle3D(
            id=int(triangle.id),
            x0=triangle.x0,
            y0=triangle.y0,
            z0=triangle.z0 + combined_element_z_offset,
            x1=triangle.x1,
            y1=triangle.y1,
            z1=triangle.z1 + combined_element_z_offset,
            x2=triangle.x2,
            y2=triangle.y2,
            z2=triangle.z2 + combined_element_z_offset,
        )

    def offset_block_triangle_id_for_combined(triangle: Triangle3D) -> Triangle3D:
        return Triangle3D(
            id=int(combined_block_triangle_id_offset + triangle.id),
            x0=triangle.x0,
            y0=triangle.y0,
            z0=triangle.z0,
            x1=triangle.x1,
            y1=triangle.y1,
            z1=triangle.z1,
            x2=triangle.x2,
            y2=triangle.y2,
            z2=triangle.z2,
        )

    combined_triangles = tuple(
        translated_element_triangle_for_combined(triangle)
        for triangle in element_triangles
    ) + tuple(
        offset_block_triangle_id_for_combined(triangle)
        for triangle in block_triangles
    )

    encoded_values = tuple(encoded_value(index) for index in range(len(values)))
    min_value = min(encoded_values)
    max_value = max(encoded_values)
    ray_origin_x = min_value - 1.0
    ray_tmax = (max_value - ray_origin_x) + 1.0
    return RtdlRtRmqScene(
        block_size=block_size,
        block_grid_width=grid_width,
        value_count=len(values),
        ray_origin_x=ray_origin_x,
        ray_tmax=ray_tmax,
        tie_break_epsilon=tie_break_epsilon,
        combined_element_z_offset=combined_element_z_offset,
        combined_block_triangle_id_offset=combined_block_triangle_id_offset,
        block_min_values=tuple(block_min_values),
        block_arg_indices=tuple(block_arg_indices),
        block_triangles=tuple(block_triangles),
        element_triangles=tuple(element_triangles),
        combined_triangles=combined_triangles,
    )


def _paper_rt_ray(ray_id: int, scene: RtdlRtRmqScene, y: float, z: float) -> Ray3D:
    return Ray3D(
        id=int(ray_id),
        ox=float(scene.ray_origin_x),
        oy=float(y),
        oz=float(z),
        dx=1.0,
        dy=0.0,
        dz=0.0,
        tmax=float(scene.ray_tmax),
    )


def _schedule_paper_rt_rmq_phases(
    queries: tuple[tuple[int, int], ...],
    scene: RtdlRtRmqScene,
) -> RtdlRtRmqScheduledRays:
    phase_buffers: dict[str, tuple[list[int], list[float], list[float]]] = {
        "same_block": ([], [], []),
        "left_partial": ([], [], []),
        "right_partial": ([], [], []),
        "full_blocks": ([], [], []),
    }
    ray_map: dict[int, tuple[int, str]] = {}
    next_ray_id = 0

    def add_ray(query_id: int, phase: str, yz: tuple[float, float]) -> None:
        nonlocal next_ray_id
        ray_id = next_ray_id
        next_ray_id += 1
        ray_map[ray_id] = (query_id, phase)
        ids, ys, zs = phase_buffers[phase]
        ids.append(ray_id)
        ys.append(float(yz[0]))
        zs.append(float(yz[1]))

    for query_id, (left, right) in enumerate(queries):
        validate_query((left, right), scene.value_count)
        left_block = left // scene.block_size
        right_block = right // scene.block_size
        if left_block == right_block:
            add_ray(query_id, "same_block", _same_block_ray_yz(left, right, scene))
        else:
            add_ray(query_id, "left_partial", _left_partial_ray_yz(left, scene))
            add_ray(query_id, "right_partial", _right_partial_ray_yz(right, scene))
            if left_block + 1 <= right_block - 1:
                add_ray(query_id, "full_blocks", _full_block_ray_yz(left_block, right_block))

    def phase(name: str) -> RtdlRtRmqRayPhase:
        ids, ys, zs = phase_buffers[name]
        return RtdlRtRmqRayPhase(name, tuple(ids), tuple(ys), tuple(zs))

    phases = (
        phase("same_block"),
        phase("left_partial"),
        phase("right_partial"),
    )
    full_phase = phase("full_blocks")
    return RtdlRtRmqScheduledRays(
        phases=phases,
        full_phase=full_phase,
        ray_map=ray_map,
        query_count=len(queries),
        total_ray_count=next_ray_id,
    )


def _full_block_ray_yz(left_block: int, right_block: int) -> tuple[float, float]:
    return (
        (float(left_block + 1) + _PAPER_RMQ_EDGE_EPS) / _PAPER_RMQ_BLOCK_SCALE,
        (float(right_block - 1) - _PAPER_RMQ_EDGE_EPS) / _PAPER_RMQ_BLOCK_SCALE,
    )


def _same_block_ray_yz(left: int, right: int, scene: RtdlRtRmqScene) -> tuple[float, float]:
    block_id = left // scene.block_size
    cell_x = (block_id + 1) % scene.block_grid_width
    cell_y = (block_id + 1) // scene.block_grid_width
    return (
        2.0 * float(cell_x) + (float(left % scene.block_size) + _PAPER_RMQ_EDGE_EPS) / scene.block_size,
        2.0 * float(cell_y) + (float(right % scene.block_size) - _PAPER_RMQ_EDGE_EPS) / scene.block_size,
    )


def _left_partial_ray_yz(left: int, scene: RtdlRtRmqScene) -> tuple[float, float]:
    block_id = left // scene.block_size
    cell_x = (block_id + 1) % scene.block_grid_width
    cell_y = (block_id + 1) // scene.block_grid_width
    return (
        2.0 * float(cell_x) + (float(left % scene.block_size) + _PAPER_RMQ_EDGE_EPS) / scene.block_size,
        2.0 * float(cell_y) + (float(scene.block_size - 1) - _PAPER_RMQ_EDGE_EPS) / scene.block_size,
    )


def _right_partial_ray_yz(right: int, scene: RtdlRtRmqScene) -> tuple[float, float]:
    block_id = right // scene.block_size
    cell_x = (block_id + 1) % scene.block_grid_width
    cell_y = (block_id + 1) // scene.block_grid_width
    return (
        2.0 * float(cell_x) + _PAPER_RMQ_EDGE_EPS / scene.block_size,
        2.0 * float(cell_y) + (float(right % scene.block_size) - _PAPER_RMQ_EDGE_EPS) / scene.block_size,
    )


def _closest_rows_by_ray(
    rays: tuple[Ray3D, ...],
    triangles: tuple[Triangle3D, ...],
    *,
    backend: str,
) -> dict[int, dict[str, float | int]]:
    if not rays:
        return {}
    rows = run_generic_ray_triangle_closest_hit(rays, triangles, backend=backend)
    return {int(row["ray_id"]): row for row in rows}


def _closest_rows_by_ray_phase(
    phase: RtdlRtRmqRayPhase,
    scene: RtdlRtRmqScene,
    triangles: tuple[Triangle3D, ...],
    *,
    backend: str,
) -> dict[int, dict[str, float | int]]:
    if phase.ray_count == 0:
        return {}
    return _closest_rows_by_ray(phase.as_rays(scene), triangles, backend=backend)


def _closest_rows_by_prepared_scene(
    rays: tuple[Ray3D, ...],
    prepared_scene: Any,
) -> dict[int, dict[str, float | int]]:
    if not rays:
        return {}
    rows = prepared_scene.ray_closest_hit_rows(rays)
    return {int(row["ray_id"]): row for row in rows}


def _pack_prepared_phase_rays(
    phase: RtdlRtRmqRayPhase,
    scene: RtdlRtRmqScene,
) -> Any:
    import numpy as np  # type: ignore[import-not-found]
    from rtdsl.optix_runtime import pack_rays_3d_from_arrays

    n = phase.ray_count
    return pack_rays_3d_from_arrays(
        np.asarray(phase.ray_ids, dtype=np.uint32),
        np.full(n, scene.ray_origin_x, dtype=np.float64),
        np.asarray(phase.ys, dtype=np.float64),
        np.asarray(phase.zs, dtype=np.float64),
        np.ones(n, dtype=np.float64),
        np.zeros(n, dtype=np.float64),
        np.zeros(n, dtype=np.float64),
        np.full(n, scene.ray_tmax, dtype=np.float64),
    )


def _closest_rows_by_prepared_phase(
    phase: RtdlRtRmqRayPhase,
    scene: RtdlRtRmqScene,
    prepared_scene: Any,
) -> dict[int, dict[str, float | int]]:
    if phase.ray_count == 0:
        return {}
    try:
        packed_rays = _pack_prepared_phase_rays(phase, scene)
    except (ImportError, RuntimeError):  # pragma: no cover - host-dependent optional fast path
        return _closest_rows_by_prepared_scene(phase.as_rays(scene), prepared_scene)
    rows = prepared_scene.ray_closest_hit_rows(packed_rays)
    return {int(row["ray_id"]): row for row in rows}


def _empty_closest_hit_arrays():
    import numpy as np  # type: ignore[import-not-found]

    return {
        "ray_id": np.empty(0, dtype=np.uint32),
        "triangle_id": np.empty(0, dtype=np.uint32),
        "t": np.empty(0, dtype=np.float64),
    }


def _closest_row_arrays_by_prepared_phase(
    phase: RtdlRtRmqRayPhase,
    scene: RtdlRtRmqScene,
    prepared_scene: Any,
):
    import numpy as np  # type: ignore[import-not-found]

    if phase.ray_count == 0:
        return _empty_closest_hit_arrays()
    packed_rays = _pack_prepared_phase_rays(phase, scene)
    if hasattr(prepared_scene, "ray_closest_hit_row_arrays"):
        return prepared_scene.ray_closest_hit_row_arrays(packed_rays)
    rows = prepared_scene.ray_closest_hit_rows(packed_rays)
    return {
        "ray_id": np.asarray([int(row["ray_id"]) for row in rows], dtype=np.uint32),
        "triangle_id": np.asarray([int(row["triangle_id"]) for row in rows], dtype=np.uint32),
        "t": np.asarray([float(row["t"]) for row in rows], dtype=np.float64),
    }


def _assemble_paper_rt_rmq_rows(
    values: tuple[float, ...],
    queries: tuple[tuple[int, int], ...],
    scene: RtdlRtRmqScene,
    scheduled: RtdlRtRmqScheduledRays,
    phased_rows: tuple[tuple[dict[int, dict[str, float | int]], str], ...],
    full_rows_by_ray: dict[int, dict[str, float | int]],
) -> tuple[dict[str, Any], ...]:
    candidate_by_query: dict[int, tuple[float, int] | None] = {query_id: None for query_id in range(len(queries))}

    def accept(query_id: int, value: float, index: int) -> None:
        previous = candidate_by_query[query_id]
        if previous is None:
            candidate_by_query[query_id] = (float(value), int(index))
            return
        candidate_by_query[query_id] = _better_pair(previous[0], previous[1], float(value), int(index))

    for rows_by_ray, phase in phased_rows:
        for ray_id, row in rows_by_ray.items():
            query_id, recorded_phase = scheduled.ray_map[ray_id]
            if recorded_phase != phase:
                raise RuntimeError("internal phase bookkeeping mismatch")
            index = int(row["triangle_id"])
            accept(query_id, float(values[index]), index)

    for ray_id, row in full_rows_by_ray.items():
        query_id, recorded_phase = scheduled.ray_map[ray_id]
        if recorded_phase != "full_blocks":
            raise RuntimeError("internal phase bookkeeping mismatch")
        block_id = int(row["triangle_id"])
        accept(query_id, scene.block_min_values[block_id], scene.block_arg_indices[block_id])

    rows: list[dict[str, Any]] = []
    for query_id, (left, right) in enumerate(queries):
        candidate = candidate_by_query[query_id]
        if candidate is None:
            raise RuntimeError(f"RT lowering produced no hit for non-empty RMQ query {query_id}")
        value, index = candidate
        rows.append(
            {
                "query_id": query_id,
                "left": int(left),
                "right": int(right),
                "index": int(index),
                "value": float(value),
            }
        )
    return tuple(rows)


@dataclass(frozen=True)
class PreparedPaperRtRmqQueryBatch:
    query_count: int
    ray_to_query: Any
    phases: tuple[RtdlRtRmqRayPhase, ...]
    full_phase: RtdlRtRmqRayPhase
    element_phase: RtdlRtRmqRayPhase
    combined_phase: RtdlRtRmqRayPhase
    element_packed_rays: Any
    full_packed_rays: Any
    combined_packed_rays: Any
    element_prepared_ray_batch: Any
    full_prepared_ray_batch: Any
    combined_prepared_ray_batch: Any
    element_prepared_grouped_argmin: Any
    full_prepared_grouped_argmin: Any
    combined_prepared_grouped_argmin: Any
    prepare_seconds: float

    def close(self) -> None:
        for ray_batch in (
            self.element_prepared_ray_batch,
            self.full_prepared_ray_batch,
            self.combined_prepared_ray_batch,
        ):
            if ray_batch is not None and hasattr(ray_batch, "close"):
                ray_batch.close()
        for grouped_inputs in (
            self.element_prepared_grouped_argmin,
            self.full_prepared_grouped_argmin,
            self.combined_prepared_grouped_argmin,
        ):
            if grouped_inputs is not None and hasattr(grouped_inputs, "close"):
                grouped_inputs.close()


class PreparedPaperRtRmq:
    """Reusable app-side RMQ schedule over generic prepared OptiX scenes."""

    def __init__(
        self,
        values: tuple[float, ...],
        *,
        block_size: int,
        scene: RtdlRtRmqScene | None = None,
    ) -> None:
        from rtdsl.optix_runtime import prepare_optix_static_triangle_scene_3d

        self.values = tuple(float(value) for value in values)
        self.scene = scene if scene is not None else build_paper_rt_rmq_scene(self.values, block_size=block_size)
        self._closed = False
        self._prepare_optix_static_triangle_scene_3d = prepare_optix_static_triangle_scene_3d
        self._element_scene = None
        self._block_scene = None
        self._combined_scene = None
        self.prepare_seconds = 0.0
        self.last_query_metadata: dict[str, Any] = {}
        try:
            import numpy as np  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover - optional fast path
            self._np = None
            self._values_np = None
            self._value_indices_np = None
            self._block_min_values_np = None
            self._block_arg_indices_np = None
            self._block_arg_indices_u32_np = None
            self._combined_candidate_values_np = None
            self._combined_candidate_indices_u32_np = None
        else:
            self._np = np
            self._values_np = np.asarray(self.values, dtype=np.float64)
            self._value_indices_np = np.arange(self.scene.value_count, dtype=np.uint32)
            self._block_min_values_np = np.asarray(self.scene.block_min_values, dtype=np.float64)
            self._block_arg_indices_np = np.asarray(self.scene.block_arg_indices, dtype=np.int64)
            self._block_arg_indices_u32_np = np.asarray(self.scene.block_arg_indices, dtype=np.uint32)
            self._combined_candidate_values_np = np.concatenate(
                (self._values_np, self._block_min_values_np)
            )
            self._combined_candidate_indices_u32_np = np.concatenate(
                (self._value_indices_np, self._block_arg_indices_u32_np)
            )

    def _prepare_scene(self, attr_name: str, triangles: tuple[Triangle3D, ...]):
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        prepared_scene = getattr(self, attr_name)
        if prepared_scene is None:
            prepare_start = time.perf_counter()
            prepared_scene = self._prepare_optix_static_triangle_scene_3d(triangles)
            self.prepare_seconds += time.perf_counter() - prepare_start
            setattr(self, attr_name, prepared_scene)
        return prepared_scene

    @property
    def element_scene(self):
        return self._prepare_scene("_element_scene", self.scene.element_triangles)

    @property
    def block_scene(self):
        return self._prepare_scene("_block_scene", self.scene.block_triangles)

    @property
    def combined_scene(self):
        return self._prepare_scene("_combined_scene", self.scene.combined_triangles)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        for prepared_scene in (self._element_scene, self._block_scene, self._combined_scene):
            if prepared_scene is not None and hasattr(prepared_scene, "close"):
                prepared_scene.close()

    def __enter__(self) -> "PreparedPaperRtRmq":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def prepare_query_batch(self, queries: tuple[tuple[int, int], ...]) -> PreparedPaperRtRmqQueryBatch:
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        if self._np is None or self._values_np is None:
            raise RuntimeError("PreparedPaperRtRmq.prepare_query_batch requires numpy")
        np = self._np
        prepare_start = time.perf_counter()
        query_array = np.asarray(queries, dtype=np.int64)
        if query_array.ndim != 2 or query_array.shape[1] != 2:
            raise ValueError("queries must be pairs of inclusive left/right indices")
        if query_array.size:
            invalid = (
                (query_array[:, 0] < 0)
                | (query_array[:, 1] < query_array[:, 0])
                | (query_array[:, 1] >= self.scene.value_count)
            )
            if bool(invalid.any()):
                bad = int(np.where(invalid)[0][0])
                raise ValueError(f"invalid RMQ query {queries[bad]!r} for {self.scene.value_count} values")
        qids_all = np.arange(query_array.shape[0], dtype=np.int64)
        lefts = query_array[:, 0]
        rights = query_array[:, 1]
        left_blocks = lefts // self.scene.block_size
        right_blocks = rights // self.scene.block_size
        same_mask = left_blocks == right_blocks
        cross_mask = ~same_mask
        full_mask = cross_mask & (left_blocks + 1 <= right_blocks - 1)

        next_ray_id = 0
        ray_to_query_parts: list[tuple[Any, Any]] = []

        def ray_ids_for(qids) -> Any:
            nonlocal next_ray_id
            ray_ids = np.arange(next_ray_id, next_ray_id + int(qids.size), dtype=np.uint32)
            next_ray_id += int(qids.size)
            ray_to_query_parts.append((ray_ids.astype(np.int64, copy=False), qids.astype(np.int64, copy=False)))
            return ray_ids

        def phase(name: str, mask, ys, zs) -> RtdlRtRmqRayPhase:
            qids = qids_all[mask]
            return RtdlRtRmqRayPhase(name, ray_ids_for(qids), ys.astype(np.float64), zs.astype(np.float64))

        same_blocks = left_blocks[same_mask]
        same_cell_x = (same_blocks + 1) % self.scene.block_grid_width
        same_cell_y = (same_blocks + 1) // self.scene.block_grid_width
        same_phase = phase(
            "same_block",
            same_mask,
            2.0 * same_cell_x + ((lefts[same_mask] % self.scene.block_size) + _PAPER_RMQ_EDGE_EPS) / self.scene.block_size,
            2.0 * same_cell_y + ((rights[same_mask] % self.scene.block_size) - _PAPER_RMQ_EDGE_EPS) / self.scene.block_size,
        )

        left_cross_blocks = left_blocks[cross_mask]
        left_cell_x = (left_cross_blocks + 1) % self.scene.block_grid_width
        left_cell_y = (left_cross_blocks + 1) // self.scene.block_grid_width
        left_phase = phase(
            "left_partial",
            cross_mask,
            2.0 * left_cell_x + ((lefts[cross_mask] % self.scene.block_size) + _PAPER_RMQ_EDGE_EPS) / self.scene.block_size,
            2.0 * left_cell_y + (float(self.scene.block_size - 1) - _PAPER_RMQ_EDGE_EPS) / self.scene.block_size,
        )

        right_cross_blocks = right_blocks[cross_mask]
        right_cell_x = (right_cross_blocks + 1) % self.scene.block_grid_width
        right_cell_y = (right_cross_blocks + 1) // self.scene.block_grid_width
        right_phase = phase(
            "right_partial",
            cross_mask,
            2.0 * right_cell_x + _PAPER_RMQ_EDGE_EPS / self.scene.block_size,
            2.0 * right_cell_y + ((rights[cross_mask] % self.scene.block_size) - _PAPER_RMQ_EDGE_EPS) / self.scene.block_size,
        )

        full_phase = phase(
            "full_blocks",
            full_mask,
            (left_blocks[full_mask] + 1.0 + _PAPER_RMQ_EDGE_EPS) / _PAPER_RMQ_BLOCK_SCALE,
            (right_blocks[full_mask] - 1.0 - _PAPER_RMQ_EDGE_EPS) / _PAPER_RMQ_BLOCK_SCALE,
        )
        phases = (same_phase, left_phase, right_phase)
        ray_to_query = np.empty(next_ray_id, dtype=np.int64)
        for ray_ids, qids in ray_to_query_parts:
            ray_to_query[ray_ids] = qids

        element_phase = RtdlRtRmqRayPhase(
            "element_phases",
            np.concatenate([np.asarray(phase.ray_ids, dtype=np.uint32) for phase in phases]),
            np.concatenate([np.asarray(phase.ys, dtype=np.float64) for phase in phases]),
            np.concatenate([np.asarray(phase.zs, dtype=np.float64) for phase in phases]),
        )
        element_packed_rays = (
            _pack_prepared_phase_rays(element_phase, self.scene)
            if element_phase.ray_count
            else None
        )
        full_packed_rays = (
            _pack_prepared_phase_rays(full_phase, self.scene)
            if full_phase.ray_count
            else None
        )
        combined_element_ys = np.asarray(element_phase.ys, dtype=np.float64)
        combined_element_zs = (
            np.asarray(element_phase.zs, dtype=np.float64)
            + self.scene.combined_element_z_offset
        )
        combined_phase = RtdlRtRmqRayPhase(
            "combined_element_and_full_blocks",
            np.concatenate(
                (
                    np.asarray(element_phase.ray_ids, dtype=np.uint32),
                    np.asarray(full_phase.ray_ids, dtype=np.uint32),
                )
            ),
            np.concatenate(
                (
                    combined_element_ys,
                    np.asarray(full_phase.ys, dtype=np.float64),
                )
            ),
            np.concatenate(
                (
                    combined_element_zs,
                    np.asarray(full_phase.zs, dtype=np.float64),
                )
            ),
        )
        combined_packed_rays = (
            _pack_prepared_phase_rays(combined_phase, self.scene)
            if combined_phase.ray_count
            else None
        )

        def prepare_native_ray_batch(prepared_scene, packed_rays):
            if packed_rays is None or not hasattr(prepared_scene, "prepare_ray_batch"):
                return None
            try:
                return prepared_scene.prepare_ray_batch(packed_rays)
            except RuntimeError:
                return None

        def prepare_grouped_argmin_inputs(prepared_scene, ray_count, values_np, indices_np):
            if query_array.shape[0] < _PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD:
                return None
            if ray_count == 0 or not hasattr(prepared_scene, "prepare_closest_hit_grouped_argmin_inputs"):
                return None
            try:
                return prepared_scene.prepare_closest_hit_grouped_argmin_inputs(
                    ray_to_query.astype(np.uint32, copy=False),
                    values_np,
                    indices_np,
                    group_count=int(query_array.shape[0]),
                )
            except RuntimeError:
                return None

        prefer_combined_grouped = (
            query_array.shape[0] >= _PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD
            and full_phase.ray_count > 0
        )
        combined_prepared_ray_batch = None
        combined_prepared_grouped_argmin = None
        if prefer_combined_grouped:
            combined_scene = self.combined_scene
            combined_prepared_ray_batch = prepare_native_ray_batch(combined_scene, combined_packed_rays)
            combined_prepared_grouped_argmin = prepare_grouped_argmin_inputs(
                combined_scene,
                combined_phase.ray_count,
                self._combined_candidate_values_np,
                self._combined_candidate_indices_u32_np,
            )

        combined_path_ready = (
            combined_prepared_ray_batch is not None
            and combined_prepared_grouped_argmin is not None
        )
        if combined_path_ready:
            element_prepared_ray_batch = None
            full_prepared_ray_batch = None
            element_prepared_grouped_argmin = None
            full_prepared_grouped_argmin = None
        else:
            element_scene = self.element_scene
            block_scene = self.block_scene
            element_prepared_ray_batch = prepare_native_ray_batch(element_scene, element_packed_rays)
            full_prepared_ray_batch = prepare_native_ray_batch(block_scene, full_packed_rays)
            element_prepared_grouped_argmin = prepare_grouped_argmin_inputs(
                element_scene,
                element_phase.ray_count,
                self._values_np,
                self._value_indices_np,
            )
            full_prepared_grouped_argmin = prepare_grouped_argmin_inputs(
                block_scene,
                full_phase.ray_count,
                self._block_min_values_np,
                self._block_arg_indices_u32_np,
            )
        return PreparedPaperRtRmqQueryBatch(
            query_count=int(query_array.shape[0]),
            ray_to_query=ray_to_query,
            phases=phases,
            full_phase=full_phase,
            element_phase=element_phase,
            combined_phase=combined_phase,
            element_packed_rays=element_packed_rays,
            full_packed_rays=full_packed_rays,
            combined_packed_rays=combined_packed_rays,
            element_prepared_ray_batch=element_prepared_ray_batch,
            full_prepared_ray_batch=full_prepared_ray_batch,
            combined_prepared_ray_batch=combined_prepared_ray_batch,
            element_prepared_grouped_argmin=element_prepared_grouped_argmin,
            full_prepared_grouped_argmin=full_prepared_grouped_argmin,
            combined_prepared_grouped_argmin=combined_prepared_grouped_argmin,
            prepare_seconds=float(time.perf_counter() - prepare_start),
        )

    def _query_prepared_batch_grouped_argmin(self, batch: PreparedPaperRtRmqQueryBatch):
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        if self._np is None or self._values_np is None:
            raise RuntimeError("PreparedPaperRtRmq.query_prepared_batch_arrays requires numpy")
        np = self._np
        combined_grouped_ready = (
            batch.combined_prepared_ray_batch is not None
            and batch.combined_prepared_grouped_argmin is not None
            and hasattr(self.combined_scene, "ray_closest_hit_prepared_grouped_argmin")
        )
        if not combined_grouped_ready and not hasattr(self.element_scene, "ray_closest_hit_grouped_argmin"):
            raise RuntimeError("prepared grouped argmin requires a runtime grouped-argmin boundary")
        query_start = time.perf_counter()
        ray_to_query = np.asarray(batch.ray_to_query, dtype=np.uint32)
        best_values = np.full(batch.query_count, np.inf, dtype=np.float64)
        best_indices = np.full(batch.query_count, np.iinfo(np.uint32).max, dtype=np.uint32)
        phase_metadata: dict[str, Any] = {}

        def accept_group_result(result: dict[str, Any]) -> None:
            has_value = np.asarray(result["has_value"], dtype=bool)
            if has_value.size == 0 or not bool(has_value.any()):
                return
            candidate_values = np.asarray(result["value"], dtype=np.float64)
            candidate_indices = np.asarray(result["index"], dtype=np.uint32)
            take = has_value & (
                (candidate_values < best_values)
                | ((candidate_values == best_values) & (candidate_indices < best_indices))
            )
            if bool(take.any()):
                best_values[take] = candidate_values[take]
                best_indices[take] = candidate_indices[take]

        if (
            batch.combined_phase.ray_count
            and batch.full_phase.ray_count
            and batch.combined_prepared_ray_batch is not None
            and batch.combined_prepared_grouped_argmin is not None
            and hasattr(self.combined_scene, "ray_closest_hit_prepared_grouped_argmin")
        ):
            combined_result = self.combined_scene.ray_closest_hit_prepared_grouped_argmin(
                batch.combined_prepared_ray_batch,
                batch.combined_prepared_grouped_argmin,
            )
            accept_group_result(combined_result)
            combined_metadata = dict(getattr(self.combined_scene, "last_closest_hit_metadata", {}))
            combined_metadata["batched_element_phases"] = True
            combined_metadata["combined_scene_grouped_argmin"] = True
            for phase in batch.phases:
                metadata = dict(combined_metadata)
                metadata["ray_count"] = int(phase.ray_count)
                metadata["batched_combined_ray_count"] = int(batch.element_phase.ray_count)
                metadata["combined_scene_ray_count"] = int(batch.combined_phase.ray_count)
                phase_metadata[phase.phase] = metadata
            full_metadata = dict(combined_metadata)
            full_metadata["ray_count"] = int(batch.full_phase.ray_count)
            full_metadata["combined_scene_ray_count"] = int(batch.combined_phase.ray_count)
            phase_metadata["full_blocks"] = full_metadata

            if bool((best_indices == np.iinfo(np.uint32).max).any()):
                missing = int(np.where(best_indices == np.iinfo(np.uint32).max)[0][0])
                raise RuntimeError(f"RT lowering produced no hit for non-empty RMQ query {missing}")

            self.last_query_metadata = {
                "prepared_reused": True,
                "prepared_app_handle": True,
                "prepared_query_batch": True,
                "prepared_native_ray_batches": True,
                "compact_arrays": False,
                "batched_element_phases": True,
                "runtime_grouped_argmin_available": True,
                "runtime_grouped_argmin_used": True,
                "prepared_ray_batch_grouped_argmin": True,
                "prepared_grouped_argmin_inputs": True,
                "native_combined_scene_grouped_argmin": True,
                "native_two_source_grouped_merge": False,
                "combined_scene_used": True,
                "prepare_seconds": float(self.prepare_seconds),
                "query_batch_prepare_seconds": float(batch.prepare_seconds),
                "query_total_seconds": float(time.perf_counter() - query_start),
                "query_count": int(batch.query_count),
                "total_ray_count": int(ray_to_query.size),
                "combined_scene_ray_count": int(batch.combined_phase.ray_count),
                "phase_ray_counts": {
                    phase.phase: int(phase.ray_count)
                    for phase in (*batch.phases, batch.full_phase)
                },
                "phase_metadata": phase_metadata,
                "grouped_argmin_boundary": (
                    "used as a generic combined-scene runtime boundary; native OptiX sees "
                    "one prepared triangle scene, one prepared ray batch, group maps, "
                    "values, and tie-break indices"
                ),
                "native_engine_customization": False,
            }
            return best_indices.astype(np.int64, copy=False), best_values

        if (
            batch.element_phase.ray_count
            and batch.full_phase.ray_count
            and batch.element_prepared_ray_batch is not None
            and batch.full_prepared_ray_batch is not None
            and batch.element_prepared_grouped_argmin is not None
            and batch.full_prepared_grouped_argmin is not None
            and hasattr(self.element_scene, "two_scene_ray_closest_hit_prepared_grouped_argmin")
        ):
            fused_result = self.element_scene.two_scene_ray_closest_hit_prepared_grouped_argmin(
                batch.element_prepared_ray_batch,
                batch.element_prepared_grouped_argmin,
                self.block_scene,
                batch.full_prepared_ray_batch,
                batch.full_prepared_grouped_argmin,
            )
            accept_group_result(fused_result)
            fused_metadata = dict(getattr(self.element_scene, "last_closest_hit_metadata", {}))
            fused_metadata["batched_element_phases"] = True
            for phase in batch.phases:
                metadata = dict(fused_metadata)
                metadata["ray_count"] = int(phase.ray_count)
                metadata["batched_combined_ray_count"] = int(batch.element_phase.ray_count)
                phase_metadata[phase.phase] = metadata
            full_metadata = dict(fused_metadata)
            full_metadata["ray_count"] = int(batch.full_phase.ray_count)
            phase_metadata["full_blocks"] = full_metadata

            if bool((best_indices == np.iinfo(np.uint32).max).any()):
                missing = int(np.where(best_indices == np.iinfo(np.uint32).max)[0][0])
                raise RuntimeError(f"RT lowering produced no hit for non-empty RMQ query {missing}")

            self.last_query_metadata = {
                "prepared_reused": True,
                "prepared_app_handle": True,
                "prepared_query_batch": True,
                "prepared_native_ray_batches": True,
                "compact_arrays": False,
                "batched_element_phases": True,
                "runtime_grouped_argmin_available": True,
                "runtime_grouped_argmin_used": True,
                "prepared_ray_batch_grouped_argmin": True,
                "prepared_grouped_argmin_inputs": True,
                "native_combined_scene_grouped_argmin": False,
                "native_two_source_grouped_merge": True,
                "combined_scene_used": False,
                "prepare_seconds": float(self.prepare_seconds),
                "query_batch_prepare_seconds": float(batch.prepare_seconds),
                "query_total_seconds": float(time.perf_counter() - query_start),
                "query_count": int(batch.query_count),
                "total_ray_count": int(ray_to_query.size),
                "phase_ray_counts": {
                    phase.phase: int(phase.ray_count)
                    for phase in (*batch.phases, batch.full_phase)
                },
                "phase_metadata": phase_metadata,
                "grouped_argmin_boundary": (
                    "used as a generic two-source runtime boundary; native OptiX sees "
                    "prepared scenes, ray batches, group maps, values, and tie-break indices"
                ),
                "native_engine_customization": False,
            }
            return best_indices.astype(np.int64, copy=False), best_values

        if batch.element_phase.ray_count:
            if (
                batch.element_prepared_ray_batch is not None
                and batch.element_prepared_grouped_argmin is not None
                and hasattr(self.element_scene, "ray_closest_hit_prepared_grouped_argmin")
            ):
                element_result = self.element_scene.ray_closest_hit_prepared_grouped_argmin(
                    batch.element_prepared_ray_batch,
                    batch.element_prepared_grouped_argmin,
                )
            else:
                element_rays = batch.element_prepared_ray_batch or batch.element_packed_rays
                element_result = self.element_scene.ray_closest_hit_grouped_argmin(
                    element_rays,
                    ray_to_query,
                    self._values_np,
                    self._value_indices_np,
                    group_count=batch.query_count,
                )
            accept_group_result(element_result)
            element_metadata = dict(getattr(self.element_scene, "last_closest_hit_metadata", {}))
        else:
            element_metadata = {"ray_count": 0, "rows_materialized": False, "native_grouped_argmin": False}
        element_metadata["batched_element_phases"] = True
        for phase in batch.phases:
            metadata = dict(element_metadata)
            metadata["ray_count"] = int(phase.ray_count)
            metadata["batched_combined_ray_count"] = int(batch.element_phase.ray_count)
            phase_metadata[phase.phase] = metadata

        if batch.full_phase.ray_count:
            if (
                batch.full_prepared_ray_batch is not None
                and batch.full_prepared_grouped_argmin is not None
                and hasattr(self.block_scene, "ray_closest_hit_prepared_grouped_argmin")
            ):
                full_result = self.block_scene.ray_closest_hit_prepared_grouped_argmin(
                    batch.full_prepared_ray_batch,
                    batch.full_prepared_grouped_argmin,
                )
            else:
                full_rays = batch.full_prepared_ray_batch or batch.full_packed_rays
                full_result = self.block_scene.ray_closest_hit_grouped_argmin(
                    full_rays,
                    ray_to_query,
                    self._block_min_values_np,
                    self._block_arg_indices_u32_np,
                    group_count=batch.query_count,
                )
            accept_group_result(full_result)
            full_metadata = dict(getattr(self.block_scene, "last_closest_hit_metadata", {}))
        else:
            full_metadata = {"ray_count": 0, "rows_materialized": False, "native_grouped_argmin": False}
        phase_metadata["full_blocks"] = full_metadata

        if bool((best_indices == np.iinfo(np.uint32).max).any()):
            missing = int(np.where(best_indices == np.iinfo(np.uint32).max)[0][0])
            raise RuntimeError(f"RT lowering produced no hit for non-empty RMQ query {missing}")

        self.last_query_metadata = {
            "prepared_reused": True,
            "prepared_app_handle": True,
            "prepared_query_batch": True,
            "prepared_native_ray_batches": (
                batch.element_prepared_ray_batch is not None
                or batch.full_prepared_ray_batch is not None
            ),
            "compact_arrays": False,
            "batched_element_phases": True,
            "runtime_grouped_argmin_available": True,
            "runtime_grouped_argmin_used": True,
            "prepared_ray_batch_grouped_argmin": (
                batch.element_prepared_ray_batch is not None
                or batch.full_prepared_ray_batch is not None
            ),
            "prepared_grouped_argmin_inputs": (
                batch.element_prepared_grouped_argmin is not None
                or batch.full_prepared_grouped_argmin is not None
            ),
            "native_combined_scene_grouped_argmin": False,
            "native_two_source_grouped_merge": False,
            "combined_scene_used": False,
            "prepare_seconds": float(self.prepare_seconds),
            "query_batch_prepare_seconds": float(batch.prepare_seconds),
            "query_total_seconds": float(time.perf_counter() - query_start),
            "query_count": int(batch.query_count),
            "total_ray_count": int(ray_to_query.size),
            "phase_ray_counts": {
                phase.phase: int(phase.ray_count)
                for phase in (*batch.phases, batch.full_phase)
            },
            "phase_metadata": phase_metadata,
            "grouped_argmin_boundary": (
                "used as a generic runtime boundary; native OptiX sees ray ids, "
                "triangle ids, caller-owned group ids, values, and tie-break indices"
            ),
            "native_engine_customization": False,
        }
        return best_indices.astype(np.int64, copy=False), best_values

    def _query_prepared_batch_compact_arrays(self, batch: PreparedPaperRtRmqQueryBatch):
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        if self._np is None or self._values_np is None:
            raise RuntimeError("PreparedPaperRtRmq.query_prepared_batch_arrays requires numpy")
        np = self._np
        query_start = time.perf_counter()
        phases = batch.phases
        full_phase = batch.full_phase
        element_phase = batch.element_phase
        ray_to_query = batch.ray_to_query
        best_values = np.full(batch.query_count, np.inf, dtype=np.float64)
        best_indices = np.full(batch.query_count, np.iinfo(np.int64).max, dtype=np.int64)
        phase_metadata: dict[str, Any] = {}

        def accept_arrays(
            row_arrays: dict[str, Any],
            values_np,
            indices_np,
            *,
            reduce_duplicate_qids: bool = False,
        ) -> None:
            ray_ids = np.asarray(row_arrays["ray_id"], dtype=np.int64)
            if ray_ids.size == 0:
                return
            qids = ray_to_query[ray_ids]
            candidate_values = np.asarray(values_np, dtype=np.float64)
            candidate_indices = np.asarray(indices_np, dtype=np.int64)
            if reduce_duplicate_qids and qids.size > 1:
                order = np.lexsort((candidate_indices, candidate_values, qids))
                qids = qids[order]
                candidate_values = candidate_values[order]
                candidate_indices = candidate_indices[order]
                first = np.empty(qids.size, dtype=bool)
                first[0] = True
                first[1:] = qids[1:] != qids[:-1]
                qids = qids[first]
                candidate_values = candidate_values[first]
                candidate_indices = candidate_indices[first]
            current_values = best_values[qids]
            current_indices = best_indices[qids]
            take = (candidate_values < current_values) | (
                (candidate_values == current_values) & (candidate_indices < current_indices)
            )
            if bool(take.any()):
                best_values[qids[take]] = candidate_values[take]
                best_indices[qids[take]] = candidate_indices[take]

        def phase_row_arrays(row_arrays: dict[str, Any], phase: RtdlRtRmqRayPhase) -> dict[str, Any]:
            if phase.ray_count == 0:
                return _empty_closest_hit_arrays()
            row_ray_ids = np.asarray(row_arrays["ray_id"], dtype=np.int64)
            first_ray_id = int(phase.ray_ids[0])
            mask = (row_ray_ids >= first_ray_id) & (row_ray_ids < first_ray_id + phase.ray_count)
            return {
                "ray_id": np.asarray(row_arrays["ray_id"])[mask],
                "triangle_id": np.asarray(row_arrays["triangle_id"])[mask],
                "t": np.asarray(row_arrays["t"])[mask],
            }

        if element_phase.ray_count and batch.element_prepared_ray_batch is not None:
            element_arrays = self.element_scene.ray_closest_hit_row_arrays(batch.element_prepared_ray_batch)
        elif element_phase.ray_count:
            element_arrays = self.element_scene.ray_closest_hit_row_arrays(batch.element_packed_rays)
        else:
            element_arrays = _empty_closest_hit_arrays()
        element_metadata = (
            dict(getattr(self.element_scene, "last_closest_hit_metadata", {}))
            if element_phase.ray_count
            else {"ray_count": 0, "rows_materialized": False}
        )
        element_metadata["batched_element_phases"] = True
        for phase in phases:
            row_arrays = phase_row_arrays(element_arrays, phase)
            triangle_ids = np.asarray(row_arrays["triangle_id"], dtype=np.int64)
            accept_arrays(row_arrays, self._values_np[triangle_ids], triangle_ids)
            metadata = dict(element_metadata)
            metadata["ray_count"] = int(phase.ray_count)
            metadata["batched_combined_ray_count"] = int(element_phase.ray_count)
            phase_metadata[phase.phase] = metadata

        if full_phase.ray_count and batch.full_prepared_ray_batch is not None:
            full_arrays = self.block_scene.ray_closest_hit_row_arrays(batch.full_prepared_ray_batch)
        elif full_phase.ray_count:
            full_arrays = self.block_scene.ray_closest_hit_row_arrays(batch.full_packed_rays)
        else:
            full_arrays = _empty_closest_hit_arrays()
        block_ids = np.asarray(full_arrays["triangle_id"], dtype=np.int64)
        accept_arrays(
            full_arrays,
            self._block_min_values_np[block_ids],
            self._block_arg_indices_np[block_ids],
        )
        phase_metadata["full_blocks"] = (
            dict(getattr(self.block_scene, "last_closest_hit_metadata", {}))
            if full_phase.ray_count
            else {"ray_count": 0, "rows_materialized": False}
        )

        if bool((best_indices == np.iinfo(np.int64).max).any()):
            missing = int(np.where(best_indices == np.iinfo(np.int64).max)[0][0])
            raise RuntimeError(f"RT lowering produced no hit for non-empty RMQ query {missing}")

        self.last_query_metadata = {
            "prepared_reused": True,
            "prepared_app_handle": True,
            "prepared_query_batch": True,
            "prepared_native_ray_batches": (
                batch.element_prepared_ray_batch is not None
                or batch.full_prepared_ray_batch is not None
            ),
            "compact_arrays": True,
            "batched_element_phases": True,
            "runtime_grouped_argmin_available": hasattr(self.element_scene, "ray_closest_hit_grouped_argmin"),
            "runtime_grouped_argmin_used": False,
            "prepared_ray_batch_grouped_argmin": False,
            "native_combined_scene_grouped_argmin": False,
            "native_two_source_grouped_merge": False,
            "combined_scene_used": False,
            "prepare_seconds": float(self.prepare_seconds),
            "query_batch_prepare_seconds": float(batch.prepare_seconds),
            "query_total_seconds": float(time.perf_counter() - query_start),
            "query_count": int(batch.query_count),
            "total_ray_count": int(ray_to_query.size),
            "phase_ray_counts": {
                phase.phase: int(phase.ray_count)
                for phase in (*phases, full_phase)
            },
            "phase_metadata": phase_metadata,
            "grouped_argmin_boundary": "available as a generic runtime boundary; this query used compact closest-hit arrays",
            "native_engine_customization": False,
        }
        return best_indices, best_values

    def query_prepared_batch_arrays(self, batch: PreparedPaperRtRmqQueryBatch):
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        if batch.query_count < _PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD:
            return self._query_prepared_batch_compact_arrays(batch)
        combined_grouped_ready = (
            batch.combined_prepared_ray_batch is not None
            and batch.combined_prepared_grouped_argmin is not None
            and hasattr(self.combined_scene, "ray_closest_hit_prepared_grouped_argmin")
        )
        fallback_grouped_ready = (
            not combined_grouped_ready
            and (
                batch.element_prepared_ray_batch is not None
                or batch.full_prepared_ray_batch is not None
            )
            and hasattr(self.element_scene, "ray_closest_hit_grouped_argmin")
        )
        use_grouped_argmin = combined_grouped_ready or fallback_grouped_ready
        if use_grouped_argmin:
            try:
                return self._query_prepared_batch_grouped_argmin(batch)
            except RuntimeError as exc:
                fallback_reason = str(exc)
                indices, values = self._query_prepared_batch_compact_arrays(batch)
                self.last_query_metadata["grouped_argmin_fallback_reason"] = fallback_reason
                return indices, values
        return self._query_prepared_batch_compact_arrays(batch)

    def query_arrays(self, queries: tuple[tuple[int, int], ...]):
        batch = self.prepare_query_batch(queries)
        try:
            return self.query_prepared_batch_arrays(batch)
        finally:
            batch.close()

    def query(self, queries: tuple[tuple[int, int], ...]) -> tuple[dict[str, Any], ...]:
        if self._closed:
            raise RuntimeError("prepared paper RT RMQ handle is closed")
        query_start = time.perf_counter()
        scheduled = _schedule_paper_rt_rmq_phases(queries, self.scene)
        phase_metadata: dict[str, Any] = {}
        phased_rows_list: list[tuple[dict[int, dict[str, float | int]], str]] = []
        for phase in scheduled.phases:
            rows = _closest_rows_by_prepared_phase(phase, self.scene, self.element_scene)
            phased_rows_list.append((rows, phase.phase))
            phase_metadata[phase.phase] = (
                dict(getattr(self.element_scene, "last_closest_hit_metadata", {}))
                if phase.ray_count
                else {"ray_count": 0, "rows_materialized": False}
            )
        full_rows_by_ray = _closest_rows_by_prepared_phase(scheduled.full_phase, self.scene, self.block_scene)
        phase_metadata["full_blocks"] = (
            dict(getattr(self.block_scene, "last_closest_hit_metadata", {}))
            if scheduled.full_phase.ray_count
            else {"ray_count": 0, "rows_materialized": False}
        )
        rows = _assemble_paper_rt_rmq_rows(
            self.values,
            queries,
            self.scene,
            scheduled,
            tuple(phased_rows_list),
            full_rows_by_ray,
        )
        self.last_query_metadata = {
            "prepared_reused": True,
            "prepared_app_handle": True,
            "prepare_seconds": float(self.prepare_seconds),
            "query_total_seconds": float(time.perf_counter() - query_start),
            "query_count": int(len(queries)),
            "total_ray_count": int(scheduled.total_ray_count),
            "phase_ray_counts": {
                phase.phase: int(phase.ray_count)
                for phase in (*scheduled.phases, scheduled.full_phase)
            },
            "phase_metadata": phase_metadata,
            "native_engine_customization": False,
        }
        return rows


def prepare_paper_rt_lowered_rmq(values: tuple[float, ...], *, block_size: int) -> PreparedPaperRtRmq:
    return PreparedPaperRtRmq(values, block_size=block_size)


def paper_rt_lowered_rmq(
    values: tuple[float, ...],
    queries: tuple[tuple[int, int], ...],
    *,
    block_size: int,
    backend: str = "cpu",
) -> tuple[tuple[dict[str, Any], ...], RtdlRtRmqScene]:
    scene = build_paper_rt_rmq_scene(values, block_size=block_size)
    if backend == "optix_prepared":
        with PreparedPaperRtRmq(values, block_size=block_size, scene=scene) as prepared:
            return prepared.query(queries), scene

    scheduled = _schedule_paper_rt_rmq_phases(queries, scene)
    phased_rows = tuple(
        (
            _closest_rows_by_ray_phase(phase, scene, scene.element_triangles, backend=backend),
            phase.phase,
        )
        for phase in scheduled.phases
    )
    full_rows_by_ray = _closest_rows_by_ray_phase(
        scheduled.full_phase,
        scene,
        scene.block_triangles,
        backend=backend,
    )
    return _assemble_paper_rt_rmq_rows(values, queries, scene, scheduled, phased_rows, full_rows_by_ray), scene


def _measure(fn):
    start = time.perf_counter()
    value = fn()
    elapsed = time.perf_counter() - start
    return value, elapsed


def _rows_match(left: tuple[dict[str, Any], ...], right: tuple[dict[str, Any], ...]) -> bool:
    if len(left) != len(right):
        return False
    for lrow, rrow in zip(left, right):
        if lrow["query_id"] != rrow["query_id"] or lrow["index"] != rrow["index"]:
            return False
        if abs(float(lrow["value"]) - float(rrow["value"])) > 1e-12:
            return False
    return True


def _arrays_match_cpu_rows(cpu_rows: tuple[dict[str, Any], ...], indices, values) -> bool:
    if len(cpu_rows) != len(indices):
        return False
    for query_id, row in enumerate(cpu_rows):
        if int(row["query_id"]) != query_id:
            return False
        if int(row["index"]) != int(indices[query_id]):
            return False
        if abs(float(row["value"]) - float(values[query_id])) > 1e-12:
            return False
    return True


def _sample_rows_from_arrays(
    queries: tuple[tuple[int, int], ...],
    indices,
    values,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    return [
        {
            "query_id": int(query_id),
            "left": int(queries[query_id][0]),
            "right": int(queries[query_id][1]),
            "index": int(indices[query_id]),
            "value": float(values[query_id]),
        }
        for query_id in range(min(limit, len(queries)))
    ]


def scope_payload() -> dict[str, Any]:
    return {
        "app": BENCHMARK_NAME,
        "status": "research_learner_app_not_benchmark",
        "paper_reference": PAPER,
        "predecessor_reference": PREDECESSOR_PAPER,
        "benchmark_contract": "range minimum query: return leftmost argmin and value for each inclusive interval",
        "why_benchmark": (
            "GPU-RMQ is a better RTDL benchmark target than RTXRMQ alone because it "
            "forces a hybrid hierarchy-plus-partner-plus-RT execution story rather "
            "than a single closest-hit geometric trick."
        ),
        "current_local_modes": (
            "cpu_reference",
            "local_hierarchical",
            "compare_local",
            "paper_rt_lowering_reference",
            "author_style_compare_local",
            "cupy_hierarchical",
            "cupy_generated_hierarchical",
            "cupy_author_style_hierarchical",
            "author_code_plan",
            "author_time_csv",
            "author_input_cpu_reference",
            "command_plan",
            "paper_rt_prepared_reuse",
            "paper_hybrid_rtdl_partner",
        ),
        "runtime_design_pressure": (
            "hierarchical summaries, prepared reusable range-index state, "
            "partner-resident scans, paper-style RT closest-hit subpaths, compact "
            "argmin/value rows, and explicit scheduling between CUDA-like partner "
            "work and RT traversal"
        ),
        "promotion_gate": (
            "Promotion is closed as rejected for the current RTDL design. Goal2612 "
            "showed that generic RTDL RMQ paths remain much slower than direct CUDA "
            "sparse-query code on same generated workloads. Keep this app as a "
            "research/learner case unless a future device-resident partner/runtime "
            "primitive changes the execution model. Do not add RMQ-specific formulas "
            "inside the native engine."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def command_plan_payload() -> dict[str, Any]:
    script = "examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py"
    return {
        "app": BENCHMARK_NAME,
        "mode": "command_plan",
        "local_correctness": (
            f"PYTHONPATH=src:. python3 {script} --mode compare_local "
            "--dataset random --value-count 4096 --query-count 1024 --max-width 256"
        ),
        "stress_local_hierarchy": (
            f"PYTHONPATH=src:. python3 {script} --mode local_hierarchical "
            "--dataset sawtooth --value-count 262144 --query-count 65536 --max-width 4096 "
            "--block-size 64 --no-sample"
        ),
        "future_pod_tasks": (
            "scale and tune the CuPy hierarchy/scan partner path",
            "wire and validate native OptiX for generic ray_triangle_closest_hit rows",
            "run the paper-style RT lowering against native closest-hit instead of CPU-only contract checks",
            "treat lakreis/GPU-RMQ authors-code comparison as optional archival work, not a promotion gate",
            "use author-generated saved input binaries when same-input correctness is required",
            "record same-contract throughput, index-build time, and memory footprint",
        ),
        "native_engine_rule": (
            "A future RTDL primitive may expose generic prepared range-summary or "
            "closest-hit contracts, but must not contain GPU-RMQ-specific app logic."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def author_code_plan_payload() -> dict[str, Any]:
    repo_dir = "scratch/external/GPU-RMQ"
    csv_path = "scratch/gpu_rmq_author_baseline.csv"
    return {
        "app": BENCHMARK_NAME,
        "mode": "author_code_plan",
        "author_code": AUTHOR_CODE,
        "author_algorithms": AUTHOR_ALGORITHMS,
        "paper_workloads": AUTHOR_PAPER_WORKLOADS,
        "clone": f"git clone https://github.com/lakreis/GPU-RMQ.git {repo_dir}",
        "build": (
            f"cmake -S {repo_dir} -B {repo_dir}/build -DOPTIX_HOME=$OPTIX_HOME "
            "&& cmake --build scratch/external/GPU-RMQ/build -j"
        ),
        "smoke_check": (
            f"{repo_dir}/build/rtxrmq 1048576 65536 -3 16 "
            f"--log_bs 6 --reps 3 --dev 0 --seed 27722 --randTrivialCheck --save-time={csv_path}"
        ),
        "comparison_rows": (
            {
                "n": "2^20",
                "q": "2^16 local smoke, then 2^26 paper-scale on pod",
                "lr": -3,
                "algorithms": (2, 5, 16, 20),
                "check": "randTrivialCheck for large q; full check only for small smoke rows",
            },
            {
                "n": "2^24 and above",
                "q": "2^26",
                "lr": -6,
                "algorithms": (5, 16, 20),
                "check": "randTrivialCheck; save input data if same-input RTDL replay is needed",
            },
        ),
        "saved_input_replay": {
            "author_flag": "--save-input-data",
            "author_note": (
                "The authors hardcode directory_save_aux_data in src/main.cu; patch it "
                "to a pod-local scratch directory before using --save-input-data."
            ),
            "rtdl_replay_mode": "author_input_cpu_reference",
            "query_binary_index_width": "32 for IS_LONG=0, 64 for IS_LONG=1",
        },
        "csv_fields": (
            "dev",
            "alg",
            "nt",
            "reps",
            "n",
            "q",
            "lr",
            "scan_threshold",
            "t",
            "q/s",
            "ns/q",
            "construction",
            "outbuffer",
            "tempbuffer",
            "freeGPUMem",
            "checkResult",
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def parse_author_time_csv(path: Path) -> tuple[dict[str, Any], ...]:
    base_fields = (
        "dev",
        "alg",
        "nt",
        "reps",
        "n",
        "bs",
        "nb",
        "q",
        "lr",
        "GPU_BSIZE",
        "CG_GROUP_SIZE",
        "CG_MEM_ALIGNMENT",
        "timestamp",
        "t",
        "q/s",
        "ns/q",
        "construction",
        "outbuffer",
        "tempbuffer",
        "freeGPUMemCorrect",
        "freeGPUMem",
        "checkResult",
    )
    extended_fields = (
        "dev",
        "alg",
        "nt",
        "reps",
        "n",
        "bs",
        "nb",
        "q",
        "lr",
        "GPU_BSIZE",
        "CG_GROUP_SIZE",
        "CG_MEM_ALIGNMENT",
        "timestamp",
        "scan_threshold",
        "XXX_CG_SIZE_LOG",
        "XXX_CG_AMOUNT_LOG",
        "t",
        "q/s",
        "ns/q",
        "construction",
        "outbuffer",
        "tempbuffer",
        "freeGPUMemCorrect",
        "freeGPUMem",
        "checkResult",
    )
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return ()
        for values in reader:
            if not values:
                continue
            if len(values) == len(extended_fields):
                rows.append(dict(zip(extended_fields, values)))
            elif len(values) == len(base_fields):
                rows.append(dict(zip(base_fields, values)))
            else:
                rows.append(dict(zip(header, values)))
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        parsed = dict(row)
        for key in ("nt", "reps", "n", "bs", "nb", "q", "GPU_BSIZE", "CG_GROUP_SIZE", "CG_MEM_ALIGNMENT", "scan_threshold", "XXX_CG_SIZE_LOG", "XXX_CG_AMOUNT_LOG", "checkResult"):
            if key in parsed and parsed[key] not in (None, ""):
                parsed[key] = int(float(parsed[key]))
        for key in ("t", "q/s", "ns/q", "construction", "outbuffer", "tempbuffer", "freeGPUMem", "freeGPUMemCorrect"):
            if key in parsed and parsed[key] not in (None, ""):
                parsed[key] = float(parsed[key])
        normalized.append(parsed)
    return tuple(normalized)


def author_time_csv_payload(path: Path) -> dict[str, Any]:
    rows = parse_author_time_csv(path)
    return {
        "app": BENCHMARK_NAME,
        "mode": "author_time_csv",
        "path": str(path),
        "row_count": len(rows),
        "rows": rows,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def cpu_reference_payload(fixture: RMQFixture) -> dict[str, Any]:
    rows, elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))
    return {
        "app": BENCHMARK_NAME,
        "mode": "cpu_reference",
        "fixture": fixture.metadata(),
        "elapsed_sec": elapsed,
        "row_count": len(rows),
        "sample_rows": list(rows[:5]),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def author_input_cpu_reference_payload(fixture: RMQFixture, *, sample: bool) -> dict[str, Any]:
    rows, elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))
    return {
        "app": BENCHMARK_NAME,
        "mode": "author_input_cpu_reference",
        "contract": "exact leftmost argmin RMQ over saved inputs generated by lakreis/GPU-RMQ",
        "fixture": fixture.metadata(),
        "elapsed_sec": elapsed,
        "row_count": len(rows),
        "sample_rows": list(rows[:5]) if sample else [],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def local_hierarchical_payload(fixture: RMQFixture, *, block_size: int, sample: bool) -> dict[str, Any]:
    (rows, table), elapsed = _measure(
        lambda: hierarchical_rmq_local(fixture.values, fixture.queries, block_size=block_size)
    )
    return {
        "app": BENCHMARK_NAME,
        "mode": "local_hierarchical",
        "contract": "exact leftmost argmin RMQ via block summaries plus sparse table over block minima",
        "fixture": fixture.metadata(),
        "hierarchy": table.metadata(),
        "elapsed_sec": elapsed,
        "row_count": len(rows),
        "sample_rows": list(rows[:5]) if sample else [],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def compare_local_payload(fixture: RMQFixture, *, block_size: int, sample: bool) -> dict[str, Any]:
    cpu_rows, cpu_elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))
    (hier_rows, table), hier_elapsed = _measure(
        lambda: hierarchical_rmq_local(fixture.values, fixture.queries, block_size=block_size)
    )
    return {
        "app": BENCHMARK_NAME,
        "mode": "compare_local",
        "fixture": fixture.metadata(),
        "hierarchy": table.metadata(),
        "cpu_reference_sec": cpu_elapsed,
        "local_hierarchical_sec": hier_elapsed,
        "matches_cpu_reference": _rows_match(cpu_rows, hier_rows),
        "sample_rows": list(hier_rows[:5]) if sample else [],
        "claim_boundary": CLAIM_BOUNDARY,
    }


def paper_rt_lowering_payload(
    fixture: RMQFixture,
    *,
    block_size: int,
    sample: bool,
    backend: str,
) -> dict[str, Any]:
    cpu_rows, cpu_elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))
    (rt_rows, scene), rt_elapsed = _measure(
        lambda: paper_rt_lowered_rmq(
            fixture.values,
            fixture.queries,
            block_size=block_size,
            backend=backend,
        )
    )
    return {
        "app": BENCHMARK_NAME,
        "mode": "paper_rt_lowering_reference",
        "contract": (
            "exact leftmost argmin RMQ through paper-style RT geometry and generic "
            "ray_triangle_closest_hit rows"
        ),
        "backend": backend,
        "fixture": fixture.metadata(),
        "rt_scene": scene.metadata(),
        "cpu_reference_sec": cpu_elapsed,
        "paper_rt_lowering_sec": rt_elapsed,
        "matches_cpu_reference": _rows_match(cpu_rows, rt_rows),
        "sample_rows": list(rt_rows[:5]) if sample else [],
        "rt_design_boundary": (
            "RMQ block construction, phase scheduling, and primitive-id decoding are "
            "app-side Python. The RTDL primitive is generic closest-hit over rays "
            "and triangles."
        ),
        "optix_status": (
            "This mode proves the RT lowering contract. Native OptiX execution now "
            "has a source-wired and pod-validated generic ray_triangle_closest_hit "
            "OptiX path. This authorizes correctness readiness for the primitive, "
            "not public speedup wording."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def paper_rt_prepared_reuse_payload(
    fixture: RMQFixture,
    *,
    block_size: int,
    sample: bool,
    reuse_repeats: int,
) -> dict[str, Any]:
    if reuse_repeats < 1:
        raise ValueError("reuse_repeats must be positive")
    cpu_rows, cpu_elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))

    prepare_start = time.perf_counter()
    prepared = prepare_paper_rt_lowered_rmq(fixture.values, block_size=block_size)
    query_times: list[float] = []
    rt_indices = ()
    rt_values = ()
    query_batch = None
    try:
        query_batch = prepared.prepare_query_batch(fixture.queries)
        prepare_elapsed = time.perf_counter() - prepare_start
        for _ in range(reuse_repeats):
            (rt_indices, rt_values), query_elapsed = _measure(
                lambda: prepared.query_prepared_batch_arrays(query_batch)
            )
            query_times.append(query_elapsed)
        last_query_metadata = dict(prepared.last_query_metadata)
        scene_metadata = prepared.scene.metadata()
    finally:
        if query_batch is not None:
            query_batch.close()
        prepared.close()

    query_median = statistics.median(query_times)
    return {
        "app": BENCHMARK_NAME,
        "mode": "paper_rt_prepared_reuse",
        "contract": (
            "exact leftmost argmin RMQ through reusable app-side prepared RT "
            "scenes plus generic OptiX closest-hit/grouped-argmin primitives"
        ),
        "backend": "optix_prepared",
        "row_format": (
            "native_grouped_argmin"
            if last_query_metadata.get("runtime_grouped_argmin_used")
            else "compact_numpy_arrays"
        ),
        "fixture": fixture.metadata(),
        "rt_scene": scene_metadata,
        "cpu_reference_sec": cpu_elapsed,
        "prepare_sec": float(prepare_elapsed),
        "prepare_sec_native_scenes_only": float(last_query_metadata.get("prepare_seconds", 0.0)),
        "prepare_sec_query_batch": float(last_query_metadata.get("query_batch_prepare_seconds", 0.0)),
        "query_sec": {
            "min": float(min(query_times)),
            "median": float(query_median),
            "max": float(max(query_times)),
            "runs": [float(value) for value in query_times],
        },
        "reuse_repeats": int(reuse_repeats),
        "qps_query_median": float(len(fixture.queries) / query_median) if query_median > 0.0 else math.inf,
        "ns_per_query_query_median": float(query_median * 1e9 / len(fixture.queries)),
        "matches_cpu_reference": _arrays_match_cpu_rows(cpu_rows, rt_indices, rt_values),
        "sample_rows": _sample_rows_from_arrays(fixture.queries, rt_indices, rt_values) if sample else [],
        "last_query_metadata": last_query_metadata,
        "rt_design_boundary": (
            "The reusable handle is an app-side Python scheduling object. Native "
            "OptiX still sees only prepared static triangle scenes, generic ray "
            "closest-hit rows, and generic grouped argmin over caller-owned "
            "group/value/index arrays."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def paper_hybrid_rtdl_partner_payload(
    fixture: RMQFixture,
    *,
    reduction_factor: int,
    scan_threshold: int,
    rt_top_block_size: int,
    sample: bool,
    reuse_repeats: int,
) -> dict[str, Any]:
    if reuse_repeats < 1:
        raise ValueError("reuse_repeats must be positive")
    cpu_rows, cpu_elapsed = _measure(lambda: exact_rmq_cpu(fixture.values, fixture.queries))
    indices: tuple[int, ...] = ()
    values: tuple[float, ...] = ()
    query_times: list[float] = []
    prepare_start = time.perf_counter()
    prepared = PreparedPaperHybridRtdlPartnerRmq(
        fixture.values,
        reduction_factor=reduction_factor,
        scan_threshold=scan_threshold,
        rt_top_block_size=rt_top_block_size,
    )
    batch = None
    try:
        batch = prepared.prepare_query_batch(fixture.queries)
        prepare_elapsed = time.perf_counter() - prepare_start
        for _ in range(reuse_repeats):
            (indices, values), elapsed = _measure(lambda: prepared.query_prepared_batch(batch))
            query_times.append(elapsed)
        metadata = dict(prepared.last_query_metadata)
        hierarchy = prepared.hierarchy
    finally:
        if batch is not None:
            batch.close()
        prepared.close()
    query_median = statistics.median(query_times)
    return {
        "app": BENCHMARK_NAME,
        "mode": "paper_hybrid_rtdl_partner",
        "contract": (
            "GPU-RMQ-style hybrid RMQ: app-side multi-level reduction hierarchy, "
            "partner scans for edge fragments, and generic RTDL prepared "
            "closest-hit/grouped-argmin over the coarsest fully-contained range"
        ),
        "backend": "python_partner_plus_optix_prepared",
        "fixture": fixture.metadata(),
        "cpu_reference_sec": cpu_elapsed,
        "prepare_sec": float(prepare_elapsed),
        "prepare_sec_hierarchy_and_rt_handle": float(metadata.get("prepare_seconds", 0.0)),
        "prepare_sec_query_batch": float(metadata.get("query_batch_prepare_seconds", 0.0)),
        "query_sec": {
            "min": float(min(query_times)),
            "median": float(query_median),
            "max": float(max(query_times)),
            "runs": [float(value) for value in query_times],
        },
        "reuse_repeats": int(reuse_repeats),
        "qps_query_median": float(len(fixture.queries) / query_median) if query_median > 0.0 else math.inf,
        "ns_per_query_query_median": float(query_median * 1e9 / len(fixture.queries)),
        "matches_cpu_reference": _arrays_match_cpu_rows(cpu_rows, indices, values),
        "hierarchy": hierarchy.metadata(),
        "execution_metadata": metadata,
        "sample_rows": _sample_rows_from_arrays(fixture.queries, indices, values) if sample else [],
        "design_boundary": (
            "The hierarchy, RMQ query policy, and partner scan logic are app-side. "
            "Native RTDL sees only generic prepared triangle scenes, rays, group "
            "maps, values, and tie-break indices."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _require_cupy():
    try:
        import cupy as cp  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - host-dependent optional path
        raise RuntimeError("CuPy/CUDA is required for this GPU-RMQ mode") from exc
    return cp


def _cupy_kernel(name: str):
    if name in _CUPY_KERNELS:
        return _CUPY_KERNELS[name]
    cp = _require_cupy()
    source = r"""
extern "C" __global__
void rtdl_rmq_block_min(
    const float* values,
    const unsigned int n,
    const unsigned int block_size,
    float* block_values,
    unsigned int* block_indices,
    const unsigned int block_count
) {
    unsigned int block_id = blockIdx.x * blockDim.x + threadIdx.x;
    if (block_id >= block_count) {
        return;
    }
    unsigned int start = block_id * block_size;
    unsigned int stop = start + block_size;
    if (stop > n) {
        stop = n;
    }
    float best_value = values[start];
    unsigned int best_index = start;
    for (unsigned int index = start + 1; index < stop; ++index) {
        float value = values[index];
        if (value < best_value || (value == best_value && index < best_index)) {
            best_value = value;
            best_index = index;
        }
    }
    block_values[block_id] = best_value;
    block_indices[block_id] = best_index;
}

extern "C" __global__
void rtdl_rmq_hier_query(
    const float* values,
    const unsigned int n,
    const unsigned int* lefts,
    const unsigned int* rights,
    const unsigned int q,
    const unsigned int block_size,
    const unsigned int block_count,
    const float* sparse_values,
    const unsigned int* sparse_indices,
    unsigned int* out_indices,
    float* out_values
) {
    unsigned int query_id = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_id >= q) {
        return;
    }
    unsigned int left = lefts[query_id];
    unsigned int right = rights[query_id];
    if (right >= n || left > right) {
        out_indices[query_id] = 0xffffffffu;
        out_values[query_id] = 3.402823466e+38F;
        return;
    }

    float best_value = 3.402823466e+38F;
    unsigned int best_index = 0xffffffffu;
    unsigned int left_block = left / block_size;
    unsigned int right_block = right / block_size;

    unsigned int edge_stop = right;
    if (left_block != right_block) {
        edge_stop = (left_block + 1u) * block_size - 1u;
    }
    for (unsigned int index = left; index <= edge_stop; ++index) {
        float value = values[index];
        if (value < best_value || (value == best_value && index < best_index)) {
            best_value = value;
            best_index = index;
        }
    }

    if (left_block != right_block) {
        unsigned int right_start = right_block * block_size;
        for (unsigned int index = right_start; index <= right; ++index) {
            float value = values[index];
            if (value < best_value || (value == best_value && index < best_index)) {
                best_value = value;
                best_index = index;
            }
        }
        if (left_block + 1u <= right_block - 1u) {
            unsigned int first_full = left_block + 1u;
            unsigned int last_full = right_block - 1u;
            unsigned int full_count = last_full - first_full + 1u;
            unsigned int level = 31u - __clz(full_count);
            unsigned int width = 1u << level;
            unsigned int right_full = last_full - width + 1u;
            unsigned int offset = level * block_count;

            float left_value = sparse_values[offset + first_full];
            unsigned int left_index = sparse_indices[offset + first_full];
            if (left_value < best_value || (left_value == best_value && left_index < best_index)) {
                best_value = left_value;
                best_index = left_index;
            }

            float right_value = sparse_values[offset + right_full];
            unsigned int right_index = sparse_indices[offset + right_full];
            if (right_value < best_value || (right_value == best_value && right_index < best_index)) {
                best_value = right_value;
                best_index = right_index;
            }
        }
    }

    out_indices[query_id] = best_index;
    out_values[query_id] = best_value;
}
"""
    module = cp.RawModule(code=source, options=("--std=c++11",), name_expressions=(name,))
    kernel = module.get_function(name)
    _CUPY_KERNELS[name] = kernel
    return kernel


def _cupy_synchronize_elapsed(cp, start_event, end_event) -> float:
    end_event.synchronize()
    return float(cp.cuda.get_elapsed_time(start_event, end_event) / 1000.0)


def _cupy_build_sparse(values_gpu, *, block_size: int) -> dict[str, Any]:
    cp = _require_cupy()
    if block_size < 1:
        raise ValueError("block_size must be positive")
    value_count = int(values_gpu.size)
    block_count = int((value_count + block_size - 1) // block_size)
    block_values = cp.empty(block_count, dtype=cp.float32)
    block_indices = cp.empty(block_count, dtype=cp.uint32)
    threads = 256
    grid = ((block_count + threads - 1) // threads,)
    start = cp.cuda.Event()
    end = cp.cuda.Event()
    start.record()
    _cupy_kernel("rtdl_rmq_block_min")(
        grid,
        (threads,),
        (values_gpu, value_count, int(block_size), block_values, block_indices, block_count),
    )
    end.record()
    block_min_sec = _cupy_synchronize_elapsed(cp, start, end)

    levels = max(1, int(math.floor(math.log2(block_count))) + 1)
    sparse_values = cp.empty((levels, block_count), dtype=cp.float32)
    sparse_indices = cp.empty((levels, block_count), dtype=cp.uint32)
    sparse_values.fill(cp.inf)
    sparse_indices.fill(cp.iinfo(cp.uint32).max)
    sparse_values[0, :block_count] = block_values
    sparse_indices[0, :block_count] = block_indices

    start = cp.cuda.Event()
    end = cp.cuda.Event()
    start.record()
    span = 1
    for level in range(1, levels):
        valid = block_count - (span * 2) + 1
        if valid <= 0:
            break
        left_values = sparse_values[level - 1, :valid]
        left_indices = sparse_indices[level - 1, :valid]
        right_values = sparse_values[level - 1, span : span + valid]
        right_indices = sparse_indices[level - 1, span : span + valid]
        choose_right = (right_values < left_values) | (
            (right_values == left_values) & (right_indices < left_indices)
        )
        sparse_values[level, :valid] = cp.where(choose_right, right_values, left_values)
        sparse_indices[level, :valid] = cp.where(choose_right, right_indices, left_indices)
        span *= 2
    end.record()
    sparse_sec = _cupy_synchronize_elapsed(cp, start, end)

    return {
        "block_count": block_count,
        "block_size": int(block_size),
        "levels": levels,
        "sparse_values": sparse_values,
        "sparse_indices": sparse_indices,
        "build_sec": block_min_sec + sparse_sec,
        "block_min_sec": block_min_sec,
        "sparse_sec": sparse_sec,
    }


def _cupy_query_hierarchy(values_gpu, lefts_gpu, rights_gpu, hierarchy: dict[str, Any]) -> dict[str, Any]:
    cp = _require_cupy()
    q = int(lefts_gpu.size)
    out_indices = cp.empty(q, dtype=cp.uint32)
    out_values = cp.empty(q, dtype=cp.float32)
    threads = 256
    grid = ((q + threads - 1) // threads,)
    start = cp.cuda.Event()
    end = cp.cuda.Event()
    start.record()
    _cupy_kernel("rtdl_rmq_hier_query")(
        grid,
        (threads,),
        (
            values_gpu,
            int(values_gpu.size),
            lefts_gpu,
            rights_gpu,
            q,
            int(hierarchy["block_size"]),
            int(hierarchy["block_count"]),
            hierarchy["sparse_values"],
            hierarchy["sparse_indices"],
            out_indices,
            out_values,
        ),
    )
    end.record()
    query_sec = _cupy_synchronize_elapsed(cp, start, end)
    return {"indices": out_indices, "values": out_values, "query_sec": query_sec}


def _cupy_generated_values_and_queries(
    *,
    value_count: int,
    query_count: int,
    seed: int,
    max_width: int,
    author_lr: int | None,
):
    cp = _require_cupy()
    if value_count < 1 or query_count < 1:
        raise ValueError("value_count and query_count must be positive")
    rng = cp.random.RandomState(seed)
    values = rng.random_sample(value_count).astype(cp.float32)

    if author_lr is None:
        width_bound = min(max(1, max_width), value_count)
        widths = rng.randint(1, width_bound + 1, size=query_count).astype(cp.uint32)
    elif author_lr > 0:
        widths = cp.full(query_count, min(author_lr, value_count), dtype=cp.uint32)
    elif author_lr == -1:
        widths = rng.randint(1, value_count + 1, size=query_count).astype(cp.uint32)
    elif author_lr in (-2, -3):
        scale = value_count ** (0.6 if author_lr == -2 else 0.3)
        widths = rng.lognormal(mean=math.log(max(1.0, scale)), sigma=0.3, size=query_count)
        widths = cp.clip(widths.astype(cp.uint32), 1, value_count)
    elif author_lr == -6:
        classes = rng.randint(1, 4, size=query_count).astype(cp.uint32)
        large = rng.randint(1, value_count + 1, size=query_count).astype(cp.uint32)
        medium = cp.clip(
            rng.lognormal(mean=math.log(max(1.0, value_count**0.6)), sigma=0.3, size=query_count).astype(cp.uint32),
            1,
            value_count,
        )
        small = cp.clip(
            rng.lognormal(mean=math.log(max(1.0, value_count**0.3)), sigma=0.3, size=query_count).astype(cp.uint32),
            1,
            value_count,
        )
        widths = cp.where(classes == 1, large, cp.where(classes == 2, medium, small)).astype(cp.uint32)
    else:
        raise ValueError(f"unsupported author-style lr: {author_lr}")

    spans = value_count - widths + 1
    lefts = cp.floor(rng.random_sample(query_count) * spans).astype(cp.uint32)
    rights = lefts + widths - 1
    return values, lefts, rights


def _cupy_fixture_arrays(fixture: RMQFixture):
    cp = _require_cupy()
    values = cp.asarray(fixture.values, dtype=cp.float32)
    queries = cp.asarray(fixture.queries, dtype=cp.uint32)
    return values, cp.ascontiguousarray(queries[:, 0]), cp.ascontiguousarray(queries[:, 1])


def cupy_hierarchical_payload(
    *,
    value_count: int,
    query_count: int,
    seed: int,
    max_width: int,
    block_size: int,
    sample: bool,
    verify: bool,
    author_lr: int | None = None,
    fixture: RMQFixture | None = None,
) -> dict[str, Any]:
    cp = _require_cupy()
    if fixture is None:
        values_gpu, lefts_gpu, rights_gpu = _cupy_generated_values_and_queries(
            value_count=value_count,
            query_count=query_count,
            seed=seed,
            max_width=max_width,
            author_lr=author_lr,
        )
        dataset = f"cupy_author_style_lr_{author_lr}" if author_lr is not None else "cupy_random"
    else:
        values_gpu, lefts_gpu, rights_gpu = _cupy_fixture_arrays(fixture)
        value_count = len(fixture.values)
        query_count = len(fixture.queries)
        dataset = fixture.dataset

    hierarchy = _cupy_build_sparse(values_gpu, block_size=block_size)
    result = _cupy_query_hierarchy(values_gpu, lefts_gpu, rights_gpu, hierarchy)
    total_sec = float(hierarchy["build_sec"] + result["query_sec"])
    payload: dict[str, Any] = {
        "app": BENCHMARK_NAME,
        "mode": "cupy_hierarchical",
        "contract": "exact leftmost argmin RMQ via CuPy-owned values, query columns, block summaries, and sparse-table query kernel",
        "dataset": dataset,
        "backend": "cupy",
        "value_count": int(value_count),
        "query_count": int(query_count),
        "seed": int(seed),
        "block_size": int(block_size),
        "hierarchy": {
            "block_count": int(hierarchy["block_count"]),
            "levels": int(hierarchy["levels"]),
            "build_sec": float(hierarchy["build_sec"]),
            "block_min_sec": float(hierarchy["block_min_sec"]),
            "sparse_sec": float(hierarchy["sparse_sec"]),
        },
        "query_sec": float(result["query_sec"]),
        "total_sec": total_sec,
        "qps_query_only": float(query_count / result["query_sec"]) if result["query_sec"] > 0 else math.inf,
        "ns_per_query_query_only": float(result["query_sec"] * 1e9 / query_count),
        "qps_total": float(query_count / total_sec) if total_sec > 0 else math.inf,
        "sample_rows": [],
        "verification": "not_requested",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if author_lr is not None:
        payload["author_style"] = {
            "lr": int(author_lr),
            "semantic_match": (
                "CuPy-generated approximation of the paper workload class, not "
                "bit-identical to the authors' C++ generator. Use saved-input "
                "replay for exact same-input checks."
            ),
            "range_distributions": AUTHOR_PAPER_WORKLOADS["range_distributions"],
        }
    if sample:
        take = min(5, query_count)
        left_sample = cp.asnumpy(lefts_gpu[:take]).tolist()
        right_sample = cp.asnumpy(rights_gpu[:take]).tolist()
        index_sample = cp.asnumpy(result["indices"][:take]).tolist()
        value_sample = cp.asnumpy(result["values"][:take]).tolist()
        payload["sample_rows"] = [
            {
                "query_id": int(i),
                "left": int(left_sample[i]),
                "right": int(right_sample[i]),
                "index": int(index_sample[i]),
                "value": float(value_sample[i]),
            }
            for i in range(take)
        ]
    if verify:
        values_tuple = tuple(float(v) for v in cp.asnumpy(values_gpu))
        queries_tuple = tuple(
            (int(l), int(r))
            for l, r in zip(cp.asnumpy(lefts_gpu).tolist(), cp.asnumpy(rights_gpu).tolist())
        )
        expected_fixture = RMQFixture(dataset=dataset, values=values_tuple, queries=queries_tuple, seed=seed)
        expected = exact_rmq_cpu(expected_fixture.values, expected_fixture.queries)
        actual_indices = cp.asnumpy(result["indices"]).tolist()
        actual_values = cp.asnumpy(result["values"]).tolist()
        actual = tuple(
            {
                "query_id": int(row["query_id"]),
                "left": int(row["left"]),
                "right": int(row["right"]),
                "index": int(actual_indices[int(row["query_id"])]),
                "value": float(actual_values[int(row["query_id"])]),
            }
            for row in expected
        )
        payload["verification"] = {
            "matches_cpu_reference": _rows_match(expected, actual),
            "row_count": len(expected),
        }
    return payload


def author_style_compare_local_payload(
    fixture: RMQFixture,
    *,
    block_size: int,
    sample: bool,
    author_lr: int,
) -> dict[str, Any]:
    payload = compare_local_payload(fixture, block_size=block_size, sample=sample)
    payload["mode"] = "author_style_compare_local"
    payload["author_style"] = {
        "lr": author_lr,
        "semantic_match": (
            "Matches lakreis/GPU-RMQ workload classes at the distribution level, "
            "not bit-identical C++ mt19937 generated inputs. Use "
            "author_input_cpu_reference for exact saved-input replay."
        ),
        "range_distributions": AUTHOR_PAPER_WORKLOADS["range_distributions"],
    }
    return payload


def run_app(
    mode: str = "scope",
    *,
    dataset: str = "random",
    value_count: int = 1024,
    query_count: int = 128,
    seed: int = 260401811,
    max_width: int = 128,
    block_size: int = 64,
    reduction_factor: int = 32,
    scan_threshold: int = 1024,
    rt_top_block_size: int = 1,
    author_lr: int = -3,
    rt_backend: str = "cpu",
    sample: bool = True,
    reuse_repeats: int = 5,
) -> dict[str, Any]:
    if mode == "scope":
        return scope_payload()
    if mode == "command_plan":
        return command_plan_payload()
    if mode == "author_code_plan":
        return author_code_plan_payload()
    if mode == "author_style_compare_local":
        fixture = make_author_style_fixture(
            value_count=value_count,
            query_count=query_count,
            seed=seed,
            lr=author_lr,
        )
        return author_style_compare_local_payload(
            fixture,
            block_size=block_size,
            sample=sample,
            author_lr=author_lr,
        )
    if mode == "cupy_generated_hierarchical":
        return cupy_hierarchical_payload(
            value_count=value_count,
            query_count=query_count,
            seed=seed,
            max_width=max_width,
            block_size=block_size,
            sample=sample,
            verify=False,
        )
    if mode == "cupy_author_style_hierarchical":
        return cupy_hierarchical_payload(
            value_count=value_count,
            query_count=query_count,
            seed=seed,
            max_width=max_width,
            block_size=block_size,
            sample=sample,
            verify=False,
            author_lr=author_lr,
        )

    fixture = make_fixture(
        dataset=dataset,
        value_count=value_count,
        query_count=query_count,
        seed=seed,
        max_width=max_width,
    )
    if mode == "cpu_reference":
        return cpu_reference_payload(fixture)
    if mode == "local_hierarchical":
        return local_hierarchical_payload(fixture, block_size=block_size, sample=sample)
    if mode == "compare_local":
        return compare_local_payload(fixture, block_size=block_size, sample=sample)
    if mode == "paper_rt_lowering_reference":
        return paper_rt_lowering_payload(
            fixture,
            block_size=block_size,
            sample=sample,
            backend=rt_backend,
        )
    if mode == "paper_rt_prepared_reuse":
        return paper_rt_prepared_reuse_payload(
            fixture,
            block_size=block_size,
            sample=sample,
            reuse_repeats=reuse_repeats,
        )
    if mode == "paper_hybrid_rtdl_partner":
        return paper_hybrid_rtdl_partner_payload(
            fixture,
            reduction_factor=reduction_factor,
            scan_threshold=scan_threshold,
            rt_top_block_size=rt_top_block_size,
            sample=sample,
            reuse_repeats=reuse_repeats,
        )
    if mode == "cupy_hierarchical":
        return cupy_hierarchical_payload(
            value_count=value_count,
            query_count=query_count,
            seed=seed,
            max_width=max_width,
            block_size=block_size,
            sample=sample,
            verify=True,
            fixture=fixture,
        )
    raise ValueError(f"unsupported GPU-RMQ benchmark mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GPU-RMQ-style RTDL benchmark app front door.")
    parser.add_argument(
        "--mode",
        choices=(
            "scope",
            "command_plan",
            "author_code_plan",
            "author_time_csv",
            "author_input_cpu_reference",
            "author_style_compare_local",
            "cupy_hierarchical",
            "cupy_generated_hierarchical",
            "cupy_author_style_hierarchical",
            "cpu_reference",
            "local_hierarchical",
            "compare_local",
            "paper_rt_lowering_reference",
            "paper_rt_prepared_reuse",
            "paper_hybrid_rtdl_partner",
        ),
        default="scope",
    )
    parser.add_argument("--dataset", choices=("random", "repeated", "sawtooth", "descending_blocks"), default="random")
    parser.add_argument("--value-count", type=int, default=1024)
    parser.add_argument("--query-count", type=int, default=128)
    parser.add_argument("--seed", type=int, default=260401811)
    parser.add_argument("--max-width", type=int, default=128)
    parser.add_argument("--block-size", type=int, default=64)
    parser.add_argument("--reduction-factor", type=int, default=32)
    parser.add_argument("--scan-threshold", type=int, default=1024)
    parser.add_argument("--rt-top-block-size", type=int, default=1)
    parser.add_argument("--rt-backend", choices=("cpu", "embree", "optix", "optix_prepared"), default="cpu")
    parser.add_argument("--reuse-repeats", type=int, default=5)
    parser.add_argument("--author-array-bin", type=Path)
    parser.add_argument("--author-query-bin", type=Path)
    parser.add_argument("--author-value-count", type=int)
    parser.add_argument("--author-query-count", type=int)
    parser.add_argument("--author-index-width", type=int, choices=(32, 64), default=32)
    parser.add_argument("--author-time-csv", type=Path)
    parser.add_argument("--author-lr", type=int, default=-3)
    parser.add_argument("--no-sample", action="store_true", help="omit sample rows from JSON output")
    args = parser.parse_args(argv)
    if args.mode == "author_time_csv":
        if args.author_time_csv is None:
            parser.error("--author-time-csv is required for --mode author_time_csv")
        print(json.dumps(author_time_csv_payload(args.author_time_csv), indent=2, sort_keys=True))
        return 0
    if args.mode == "author_input_cpu_reference":
        if args.author_array_bin is None or args.author_query_bin is None:
            parser.error("--author-array-bin and --author-query-bin are required for --mode author_input_cpu_reference")
        fixture = make_author_saved_input_fixture(
            array_bin=args.author_array_bin,
            queries_bin=args.author_query_bin,
            seed=args.seed,
            value_count=args.author_value_count,
            query_count=args.author_query_count,
            index_width=args.author_index_width,
        )
        print(json.dumps(author_input_cpu_reference_payload(fixture, sample=not args.no_sample), indent=2, sort_keys=True))
        return 0
    payload = run_app(
        args.mode,
        dataset=args.dataset,
        value_count=args.value_count,
        query_count=args.query_count,
        seed=args.seed,
        max_width=args.max_width,
        block_size=args.block_size,
        reduction_factor=args.reduction_factor,
        scan_threshold=args.scan_threshold,
        rt_top_block_size=args.rt_top_block_size,
        author_lr=args.author_lr,
        rt_backend=args.rt_backend,
        sample=not args.no_sample,
        reuse_repeats=args.reuse_repeats,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
