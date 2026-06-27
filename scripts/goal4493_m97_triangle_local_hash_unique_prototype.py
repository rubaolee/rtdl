from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import time

import numpy as np

from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment


configure_numba_cuda_toolchain_environment()

import cupy as cp
from numba import cuda
from numba import int32

from examples.benchmark_apps.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as app,
)
from examples.benchmark_apps.triangle_counting.rt_graph_contract import (
    build_rt_graph_triangle_summary_contract_cupy_binary,
)


PACKET_VERSION = "rtdl.v3_0.triangle_local_hash_unique_prototype.goal4493.v1"
INPUTS = {
    "com_lj": Path("build/goal2593_snap_edges/com-lj.edge"),
    "soc_livejournal1": Path("build/goal2593_snap_edges/soc-LiveJournal1.edge"),
    "com_orkut": Path("build/goal2593_snap_edges/com-orkut.edge"),
}
OUT_JSON = Path("docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.jsonl")
LOCAL_HASH_CAPACITY = 4096
LOCAL_HASH_BOUND = 2048


@cuda.jit
def _local_hash_count_kernel(
    row_offsets,
    column_indices,
    directed_src,
    group_starts,
    group_ends,
    unique_counts,
    overflow,
):
    keys = cuda.shared.array(LOCAL_HASH_CAPACITY, int32)
    counts = cuda.shared.array(LOCAL_HASH_CAPACITY, int32)
    total = cuda.shared.array(1, int32)
    tid = cuda.threadIdx.x
    group_id = cuda.blockIdx.x
    for idx in range(tid, LOCAL_HASH_CAPACITY, cuda.blockDim.x):
        keys[idx] = -1
        counts[idx] = 0
    if tid == 0:
        total[0] = 0
    cuda.syncthreads()

    start_edge = group_starts[group_id]
    end_edge = group_ends[group_id]
    for edge_idx in range(start_edge, end_edge):
        mid = column_indices[edge_idx]
        dst_start = row_offsets[mid]
        dst_end = row_offsets[mid + 1]
        for pos in range(dst_start + tid, dst_end, cuda.blockDim.x):
            dst = int32(column_indices[pos])
            slot = (dst * 1103515245 + 12345) & (LOCAL_HASH_CAPACITY - 1)
            guard = 0
            while True:
                old = cuda.atomic.cas(keys, slot, -1, dst)
                if old == -1 or old == dst:
                    cuda.atomic.add(counts, slot, 1)
                    break
                slot = (slot + 1) & (LOCAL_HASH_CAPACITY - 1)
                guard += 1
                if guard >= LOCAL_HASH_CAPACITY:
                    overflow[group_id] = 1
                    break

    cuda.syncthreads()
    for idx in range(tid, LOCAL_HASH_CAPACITY, cuda.blockDim.x):
        if keys[idx] != -1:
            cuda.atomic.add(total, 0, 1)
    cuda.syncthreads()
    if tid == 0:
        unique_counts[group_id] = total[0]


@cuda.jit
def _local_hash_emit_kernel(
    row_offsets,
    column_indices,
    directed_src,
    group_starts,
    group_ends,
    out_offsets,
    key_base,
    unique_keys,
    unique_weights,
    overflow,
):
    keys = cuda.shared.array(LOCAL_HASH_CAPACITY, int32)
    counts = cuda.shared.array(LOCAL_HASH_CAPACITY, int32)
    write = cuda.shared.array(1, int32)
    tid = cuda.threadIdx.x
    group_id = cuda.blockIdx.x
    for idx in range(tid, LOCAL_HASH_CAPACITY, cuda.blockDim.x):
        keys[idx] = -1
        counts[idx] = 0
    if tid == 0:
        write[0] = 0
    cuda.syncthreads()

    start_edge = group_starts[group_id]
    end_edge = group_ends[group_id]
    src = directed_src[start_edge]
    for edge_idx in range(start_edge, end_edge):
        mid = column_indices[edge_idx]
        dst_start = row_offsets[mid]
        dst_end = row_offsets[mid + 1]
        for pos in range(dst_start + tid, dst_end, cuda.blockDim.x):
            dst = int32(column_indices[pos])
            slot = (dst * 1103515245 + 12345) & (LOCAL_HASH_CAPACITY - 1)
            guard = 0
            while True:
                old = cuda.atomic.cas(keys, slot, -1, dst)
                if old == -1 or old == dst:
                    cuda.atomic.add(counts, slot, 1)
                    break
                slot = (slot + 1) & (LOCAL_HASH_CAPACITY - 1)
                guard += 1
                if guard >= LOCAL_HASH_CAPACITY:
                    overflow[group_id] = 1
                    break

    cuda.syncthreads()
    base = out_offsets[group_id]
    for idx in range(tid, LOCAL_HASH_CAPACITY, cuda.blockDim.x):
        if keys[idx] != -1:
            pos = cuda.atomic.add(write, 0, 1)
            unique_keys[base + pos] = src * key_base + keys[idx]
            unique_weights[base + pos] = counts[idx]


@cuda.jit
def _fill_duplicate_group_keys_kernel(
    row_offsets,
    column_indices,
    directed_src,
    group_starts,
    group_ends,
    row_offsets_out,
    key_base,
    out_keys,
):
    tid = cuda.threadIdx.x
    group_id = cuda.blockIdx.x
    start_edge = group_starts[group_id]
    end_edge = group_ends[group_id]
    src = directed_src[start_edge]
    out_base = row_offsets_out[group_id]
    local_base = 0
    for edge_idx in range(start_edge, end_edge):
        mid = column_indices[edge_idx]
        dst_start = row_offsets[mid]
        dst_end = row_offsets[mid + 1]
        for pos in range(dst_start + tid, dst_end, cuda.blockDim.x):
            out_keys[out_base + local_base + (pos - dst_start)] = src * key_base + column_indices[pos]
        local_base += dst_end - dst_start


def _gpu_info() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _ptxas_version() -> str:
    try:
        return subprocess.check_output(["ptxas", "--version"], text=True).strip().splitlines()[-1]
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _unique_counts_sort_rle(keys):
    if int(keys.size) == 0:
        return keys, cp.empty(0, dtype=cp.int64)
    keys.sort()
    boundary = cp.empty(keys.shape, dtype=cp.bool_)
    boundary[0] = True
    boundary[1:] = keys[1:] != keys[:-1]
    starts = cp.nonzero(boundary)[0]
    ends = cp.empty(int(starts.size) + 1, dtype=starts.dtype)
    ends[:-1] = starts
    ends[-1] = int(keys.size)
    return keys[starts], (ends[1:] - ends[:-1]).astype(cp.int64, copy=False)


def _select_source_groups(row_offsets_host: np.ndarray, counts_host: np.ndarray, *, target_rows: int) -> dict[str, object]:
    starts: list[int] = []
    ends: list[int] = []
    rows: list[int] = []
    total_rows = 0
    for source in range(int(row_offsets_host.size) - 1):
        start = int(row_offsets_host[source])
        end = int(row_offsets_host[source + 1])
        if end <= start:
            continue
        two_hop_rows = int(counts_host[start:end].sum())
        if two_hop_rows <= 0 or two_hop_rows > LOCAL_HASH_BOUND:
            continue
        starts.append(start)
        ends.append(end)
        rows.append(two_hop_rows)
        total_rows += two_hop_rows
        if total_rows >= target_rows:
            break
    return {
        "group_starts": starts,
        "group_ends": ends,
        "group_rows": rows,
        "selected_group_count": len(starts),
        "selected_two_hop_rows": total_rows,
        "selected_max_group_rows": max(rows, default=0),
    }


def _run_local_hash_once(
    *,
    row_offsets,
    column_indices,
    directed_src,
    group_starts,
    group_ends,
    key_base: int,
    threads: int,
) -> tuple[object, object, float, int, int]:
    group_count = int(group_starts.size)
    unique_counts = cp.empty(group_count, dtype=cp.int64)
    overflow = cp.zeros(group_count, dtype=cp.int32)
    cp.cuda.Stream.null.synchronize()
    started = time.perf_counter()
    _local_hash_count_kernel[group_count, threads](
        row_offsets,
        column_indices,
        directed_src,
        group_starts,
        group_ends,
        unique_counts,
        overflow,
    )
    cuda.synchronize()
    offsets = cp.empty(group_count + 1, dtype=cp.int64)
    offsets[0] = 0
    offsets[1:] = cp.cumsum(unique_counts)
    cp.cuda.Stream.null.synchronize()
    unique_total = int(offsets[-1].get())
    unique_keys = cp.empty(unique_total, dtype=cp.int64)
    unique_weights = cp.empty(unique_total, dtype=cp.int64)
    _local_hash_emit_kernel[group_count, threads](
        row_offsets,
        column_indices,
        directed_src,
        group_starts,
        group_ends,
        offsets,
        np.int64(key_base),
        unique_keys,
        unique_weights,
        overflow,
    )
    cuda.synchronize()
    wall_sec = time.perf_counter() - started
    return unique_keys, unique_weights, wall_sec, unique_total, int(overflow.sum().get())


def _run_reference_once(
    *,
    row_offsets,
    column_indices,
    directed_src,
    group_starts,
    group_ends,
    group_rows,
    key_base: int,
    threads: int,
) -> tuple[object, object, float]:
    row_offsets_out = cp.empty(int(group_rows.size) + 1, dtype=cp.int64)
    row_offsets_out[0] = 0
    row_offsets_out[1:] = cp.cumsum(group_rows)
    cp.cuda.Stream.null.synchronize()
    duplicate_count = int(row_offsets_out[-1].get())
    cp.cuda.Stream.null.synchronize()
    started = time.perf_counter()
    duplicate_keys = cp.empty(duplicate_count, dtype=cp.int64)
    _fill_duplicate_group_keys_kernel[int(group_starts.size), threads](
        row_offsets,
        column_indices,
        directed_src,
        group_starts,
        group_ends,
        row_offsets_out,
        np.int64(key_base),
        duplicate_keys,
    )
    cuda.synchronize()
    unique_keys, unique_weights = _unique_counts_sort_rle(duplicate_keys)
    cp.cuda.Stream.null.synchronize()
    wall_sec = time.perf_counter() - started
    return unique_keys, unique_weights, wall_sec


def _validate_outputs(local_keys, local_weights, reference_keys, reference_weights) -> bool:
    local_order = cp.argsort(local_keys)
    sorted_local_keys = local_keys[local_order]
    sorted_local_weights = local_weights[local_order].astype(cp.int64, copy=False)
    return bool(
        cp.all(sorted_local_keys == reference_keys).get()
        and cp.all(sorted_local_weights == reference_weights.astype(cp.int64, copy=False)).get()
    )


def _case(dataset: str, edge_file: Path, *, target_rows: int, repeat: int, threads: int) -> dict[str, object]:
    if not edge_file.exists():
        raise FileNotFoundError(edge_file)
    contract_started = time.perf_counter()
    contract = build_rt_graph_triangle_summary_contract_cupy_binary(
        edge_file,
        materialize_host_columns=False,
        materialize_two_hop_summary=False,
    )
    arrays = app._require_directed_csr_device_arrays(contract, partner="cupy")
    row_offsets = arrays["row_offsets"].astype(cp.int64, copy=False)
    column_indices = arrays["column_indices"].astype(cp.int64, copy=False)
    directed_src = arrays["directed_src"].astype(cp.int64, copy=False)
    counts = arrays["two_hop_counts_per_directed_edge"].astype(cp.int64, copy=False)
    row_offsets_host = cp.asnumpy(row_offsets)
    counts_host = cp.asnumpy(counts)
    selection = _select_source_groups(row_offsets_host, counts_host, target_rows=target_rows)
    if selection["selected_group_count"] == 0:
        raise RuntimeError(f"{dataset}: no source groups selected")
    group_starts = cp.asarray(selection["group_starts"], dtype=cp.int64)
    group_ends = cp.asarray(selection["group_ends"], dtype=cp.int64)
    group_rows = cp.asarray(selection["group_rows"], dtype=cp.int64)
    contract_wall_sec = time.perf_counter() - contract_started

    warm_local_keys, warm_local_weights, _, _, warm_overflow = _run_local_hash_once(
        row_offsets=row_offsets,
        column_indices=column_indices,
        directed_src=directed_src,
        group_starts=group_starts,
        group_ends=group_ends,
        key_base=int(contract.vertex_count),
        threads=threads,
    )
    warm_reference_keys, warm_reference_weights, _ = _run_reference_once(
        row_offsets=row_offsets,
        column_indices=column_indices,
        directed_src=directed_src,
        group_starts=group_starts,
        group_ends=group_ends,
        group_rows=group_rows,
        key_base=int(contract.vertex_count),
        threads=threads,
    )
    validation_ok = _validate_outputs(
        warm_local_keys,
        warm_local_weights,
        warm_reference_keys,
        warm_reference_weights,
    )
    if warm_overflow:
        validation_ok = False

    local_times: list[float] = []
    reference_times: list[float] = []
    local_unique_total = int(warm_local_keys.size)
    reference_unique_total = int(warm_reference_keys.size)
    overflow_total = int(warm_overflow)
    for _ in range(repeat):
        local_keys, local_weights, local_sec, local_unique_total, overflow_count = _run_local_hash_once(
            row_offsets=row_offsets,
            column_indices=column_indices,
            directed_src=directed_src,
            group_starts=group_starts,
            group_ends=group_ends,
            key_base=int(contract.vertex_count),
            threads=threads,
        )
        reference_keys, reference_weights, reference_sec = _run_reference_once(
            row_offsets=row_offsets,
            column_indices=column_indices,
            directed_src=directed_src,
            group_starts=group_starts,
            group_ends=group_ends,
            group_rows=group_rows,
            key_base=int(contract.vertex_count),
            threads=threads,
        )
        local_times.append(local_sec)
        reference_times.append(reference_sec)
        overflow_total += overflow_count
        validation_ok = validation_ok and _validate_outputs(local_keys, local_weights, reference_keys, reference_weights)
        reference_unique_total = int(reference_keys.size)

    local_median = statistics.median(local_times)
    reference_median = statistics.median(reference_times)
    row = {
        "status": "ok",
        "dataset": dataset,
        "edge_file": str(edge_file),
        "contract_build_wall_sec": contract_wall_sec,
        "target_two_hop_rows": int(target_rows),
        "selected_group_count": int(selection["selected_group_count"]),
        "selected_two_hop_rows": int(selection["selected_two_hop_rows"]),
        "selected_max_group_rows": int(selection["selected_max_group_rows"]),
        "local_hash_bound": LOCAL_HASH_BOUND,
        "local_hash_capacity": LOCAL_HASH_CAPACITY,
        "threads_per_block": int(threads),
        "repeat": int(repeat),
        "local_hash_median_sec": local_median,
        "reference_fill_sort_rle_median_sec": reference_median,
        "local_hash_speedup_vs_reference": reference_median / local_median if local_median else None,
        "local_unique_total": int(local_unique_total),
        "reference_unique_total": int(reference_unique_total),
        "overflow_total": int(overflow_total),
        "validation_ok": bool(validation_ok),
        "prototype_boundary": {
            "selected_small_source_groups_only": True,
            "route_changed": False,
            "hybrid_large_tail_fallback_implemented": False,
            "public_speedup_claim_authorized": False,
            "native_engine_customization": False,
            "app_specific_native_engine_callback": False,
        },
    }
    del contract, arrays
    cp.get_default_memory_pool().free_all_blocks()
    return row


def run_matrix(*, target_rows: int, repeat: int, threads: int) -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    for dataset, edge_file in INPUTS.items():
        try:
            row = _case(dataset, edge_file, target_rows=target_rows, repeat=repeat, threads=threads)
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {"status": "error", "dataset": dataset, "edge_file": str(edge_file), "error": repr(exc)}
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "dataset": dataset,
                    "status": row["status"],
                    "selected_two_hop_rows": row.get("selected_two_hop_rows"),
                    "speedup": row.get("local_hash_speedup_vs_reference"),
                    "validation_ok": row.get("validation_ok"),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4493 / V3 M97",
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "ptxas_version": _ptxas_version(),
        "numba_toolchain_environment": configure_numba_cuda_toolchain_environment(),
        "parameters": {
            "target_two_hop_rows": int(target_rows),
            "repeat": int(repeat),
            "threads_per_block": int(threads),
            "local_hash_bound": LOCAL_HASH_BOUND,
            "local_hash_capacity": LOCAL_HASH_CAPACITY,
        },
        "summary": {
            "all_cases_ok": len(ok_rows) == len(rows),
            "all_validated": all(bool(row.get("validation_ok")) for row in ok_rows),
            "speedups": {
                row["dataset"]: row["local_hash_speedup_vs_reference"]
                for row in ok_rows
            },
            "selected_two_hop_rows": {
                row["dataset"]: row["selected_two_hop_rows"]
                for row in ok_rows
            },
        },
        "decision": (
            "The bounded local-hash kernel is a real small-source-group candidate only if "
            "validation passes and speedups exceed the duplicate-key fill plus sort/RLE reference. "
            "This packet does not implement the large-tail fallback or change the current route."
        ),
        "claim_boundary": {
            "prototype_only": True,
            "selected_small_source_groups_only": True,
            "route_changed": False,
            "public_speedup_claim_authorized": False,
            "native_engine_customization": False,
            "app_specific_native_engine_callback": False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-two-hop-rows", type=int, default=20_000_000)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--threads", type=int, default=256)
    args = parser.parse_args()
    run_matrix(target_rows=args.target_two_hop_rows, repeat=args.repeat, threads=args.threads)


if __name__ == "__main__":
    main()
