from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

import cupy
import numpy as np

from examples.benchmark_apps.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as app,
)
from examples.benchmark_apps.triangle_counting.rt_graph_contract import (
    build_rt_graph_triangle_summary_contract_cupy_binary,
)


INPUTS = {
    "com_lj": Path("build/goal2593_snap_edges/com-lj.edge"),
    "soc_livejournal1": Path("build/goal2593_snap_edges/soc-LiveJournal1.edge"),
    "com_orkut": Path("build/goal2593_snap_edges/com-orkut.edge"),
}
THRESHOLDS = (64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 65536)
OUT_JSON = Path("docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.jsonl")


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


def _quantiles(values: np.ndarray) -> dict[str, int]:
    if values.size == 0:
        return {str(q): 0 for q in (50, 75, 90, 95, 99, 99.9)}
    return {str(q): int(np.percentile(values, q)) for q in (50, 75, 90, 95, 99, 99.9)}


def _case(dataset: str, edge_file: Path) -> dict[str, object]:
    started = time.perf_counter()
    if not edge_file.exists():
        raise FileNotFoundError(edge_file)
    contract = build_rt_graph_triangle_summary_contract_cupy_binary(
        edge_file,
        materialize_host_columns=False,
        materialize_two_hop_summary=False,
    )
    arrays = app._require_directed_csr_device_arrays(contract, partner="cupy")
    row_offsets = cupy.asnumpy(arrays["row_offsets"].astype(cupy.int64, copy=False))
    counts = cupy.asnumpy(arrays["two_hop_counts_per_directed_edge"].astype(cupy.int64, copy=False))
    prefix = np.empty(counts.size + 1, dtype=np.int64)
    prefix[0] = 0
    if counts.size:
        prefix[1:] = np.cumsum(counts, dtype=np.int64)
    source_two_hop = prefix[row_offsets[1:]] - prefix[row_offsets[:-1]]
    total_two_hop = int(source_two_hop.sum())
    source_count = int(source_two_hop.size)
    coverage: dict[str, object] = {}
    for threshold in THRESHOLDS:
        mask = source_two_hop <= int(threshold)
        covered_sources = int(mask.sum())
        covered_rows = int(source_two_hop[mask].sum())
        coverage[str(threshold)] = {
            "source_count": covered_sources,
            "source_pct": (covered_sources / source_count * 100.0) if source_count else 100.0,
            "two_hop_rows": covered_rows,
            "two_hop_pct": (covered_rows / total_two_hop * 100.0) if total_two_hop else 100.0,
        }
    row = {
        "status": "ok",
        "dataset": dataset,
        "edge_file": str(edge_file),
        "edge_count": int(edge_file.stat().st_size // 8),
        "build_contract_wall_sec": time.perf_counter() - started,
        "source_count": source_count,
        "directed_edge_count": int(counts.size),
        "total_two_hop_rows": total_two_hop,
        "max_source_two_hop_rows": int(source_two_hop.max()) if source_two_hop.size else 0,
        "source_two_hop_quantiles": _quantiles(source_two_hop),
        "bounded_source_group_coverage": coverage,
        "local_unique_kernel_reading": (
            "single small-bound local unique is insufficient for the largest rows; "
            "a hybrid small-source local path plus large-source sort/RLE fallback is the plausible next shape"
        ),
    }
    del contract, arrays
    cupy.get_default_memory_pool().free_all_blocks()
    return row


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    for dataset, edge_file in INPUTS.items():
        case_start = time.perf_counter()
        try:
            row = _case(dataset, edge_file)
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "dataset": dataset,
                "edge_file": str(edge_file),
                "error": repr(exc),
                "wall_sec": time.perf_counter() - case_start,
            }
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "dataset": dataset,
                    "status": row["status"],
                    "max_source_two_hop_rows": row.get("max_source_two_hop_rows"),
                    "coverage_8192": row.get("bounded_source_group_coverage", {}).get("8192", {}),
                    "coverage_16384": row.get("bounded_source_group_coverage", {}).get("16384", {}),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.triangle_source_group_unique_feasibility.goal4492.v1",
        "goal": "Goal4492 / V3 M96",
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "thresholds": THRESHOLDS,
        "hardware": _gpu_info(),
        "summary": {
            "all_cases_ok": len(ok_rows) == len(rows),
            "max_source_two_hop_rows": {
                row["dataset"]: row["max_source_two_hop_rows"]
                for row in ok_rows
            },
            "two_hop_pct_covered_at_8192": {
                row["dataset"]: row["bounded_source_group_coverage"]["8192"]["two_hop_pct"]
                for row in ok_rows
            },
            "two_hop_pct_covered_at_16384": {
                row["dataset"]: row["bounded_source_group_coverage"]["16384"]["two_hop_pct"]
                for row in ok_rows
            },
            "two_hop_pct_covered_at_65536": {
                row["dataset"]: row["bounded_source_group_coverage"]["65536"]["two_hop_pct"]
                for row in ok_rows
            },
        },
        "decision": (
            "Implementing a single small bounded local unique-count kernel is not justified. "
            "The next credible optimization is a hybrid/two-pass strategy: small source groups "
            "use local unique-count, while large tail groups retain sort/RLE fallback with explicit compaction."
        ),
        "claim_boundary": {
            "feasibility_only": True,
            "route_changed": False,
            "public_speedup_claim_authorized": False,
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()
