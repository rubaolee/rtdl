from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    plan_rt_dbscan_continuation_execution,
)
from scripts.goal2403_rt_dbscan_repeat_probe import (  # noqa: E402
    PREPARED_CUPY_GRID_MODE,
    PREPARED_GRID_MODE,
)
from scripts.goal2478_rt_dbscan_project_close_pod_runner import (  # noqa: E402
    run_project_close_matrix,
)


GOAL2802_ENTRYPOINT_VERSION = "rtdl.goal2802.rt_dbscan_v2_5_live_grouped_stream_harness.v1"
DEFAULT_POINT_COUNTS = (32768, 65536, 131072)
DEFAULT_REPEAT_COUNT = 3
CLAIM_BOUNDARY = {
    "canonical_live_harness": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "paper_speedup_claim_authorized": False,
    "broad_dbscan_speedup_claim_authorized": False,
    "pure_triton_components_claim_authorized": False,
    "native_engine_customization": False,
}


def _tail_speedup(row: dict[str, object], mode: str) -> float | None:
    repeat_summary = row["repeat_probe_summary"]  # type: ignore[index]
    mode_summary = repeat_summary[mode]  # type: ignore[index]
    return mode_summary.get("speedup_vs_prepared_cupy_grid")  # type: ignore[union-attr]


def _mode_tail_sec(row: dict[str, object], mode: str) -> float:
    repeat_summary = row["repeat_probe_summary"]  # type: ignore[index]
    mode_summary = repeat_summary[mode]  # type: ignore[index]
    return float(mode_summary["tail_median_sec"])  # type: ignore[index]


def _compact_point_row(row: dict[str, object]) -> dict[str, Any]:
    point_count = int(row["point_count"])
    grouped = row["grouped_stream_summary"]  # type: ignore[index]
    continuation_plan = plan_rt_dbscan_continuation_execution("clustered3d", point_count)
    return {
        "dataset": row["dataset"],
        "point_count": point_count,
        "prepared_cupy_grid_tail_median_sec": _mode_tail_sec(row, PREPARED_CUPY_GRID_MODE),
        "rt_count_prepared_grid_tail_median_sec": _mode_tail_sec(row, PREPARED_GRID_MODE),
        "rt_count_speedup_vs_prepared_cupy_grid": _tail_speedup(row, PREPARED_GRID_MODE),
        "grouped_stream_tail_median_sec": float(grouped["tail_median_sec"]),  # type: ignore[index]
        "grouped_stream_native_tail_median_sec": float(grouped["grouped_native_tail_median_sec"]),  # type: ignore[index]
        "grouped_stream_speedup_vs_prepared_cupy_grid": grouped.get("speedup_vs_prepared_cupy_grid"),  # type: ignore[union-attr]
        "prepared_cupy_signature_match": bool(
            row["repeat_probe_summary"][PREPARED_CUPY_GRID_MODE]["signatures_match_probe"]  # type: ignore[index]
        ),
        "rt_count_signature_match": bool(
            row["repeat_probe_summary"][PREPARED_GRID_MODE]["signatures_match_probe"]  # type: ignore[index]
        ),
        "grouped_stream_signature_match": bool(grouped["signatures_match_probe"]),  # type: ignore[index]
        "grouped_stream_rt_core_accelerated": bool(grouped["rt_core_accelerated"]),  # type: ignore[index]
        "grouped_stream_materializes_neighbor_rows": bool(grouped["materializes_neighbor_rows"]),  # type: ignore[index]
        "grouped_stream_materializes_directed_adjacency_stream": bool(
            grouped["materializes_directed_adjacency_stream"]  # type: ignore[index]
        ),
        "planned_high_level_mode": row["planned_rt_dbscan_selected_mode"],
        "planned_continuation_mode": row["planned_continuation_selected_mode"],
        "planned_continuation_full_stream_fits_budget": bool(continuation_plan["full_stream_fits_budget"]),
        "planned_continuation_estimated_directed_edges": int(continuation_plan["estimated_directed_edge_count"]),
    }


def run_goal2802_rt_dbscan_live_harness(
    *,
    point_counts: tuple[int, ...] = DEFAULT_POINT_COUNTS,
    repeat_count: int = DEFAULT_REPEAT_COUNT,
    raw_output_dir: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    if repeat_count < 2:
        raise ValueError("repeat_count must be at least 2 so the harness can drop the first timing row")
    temp_dir = None
    if raw_output_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="goal2802_rt_dbscan_raw_")
        raw_path = Path(temp_dir)
    else:
        raw_path = Path(raw_output_dir)
    try:
        project_close = run_project_close_matrix(
            output_dir=raw_path,
            point_counts=tuple(int(value) for value in point_counts),
            repeat_count=int(repeat_count),
        )
        compact_rows = [_compact_point_row(row) for row in project_close["summaries"]]  # type: ignore[index]
        signature_ok = all(
            row["prepared_cupy_signature_match"]
            and row["rt_count_signature_match"]
            and row["grouped_stream_signature_match"]
            for row in compact_rows
        )
        grouped_uses_rt = all(row["grouped_stream_rt_core_accelerated"] for row in compact_rows)
        grouped_avoids_large_stream = all(
            not row["grouped_stream_materializes_neighbor_rows"]
            and not row["grouped_stream_materializes_directed_adjacency_stream"]
            for row in compact_rows
        )
        grouped_speedups = [
            float(row["grouped_stream_speedup_vs_prepared_cupy_grid"])
            for row in compact_rows
            if row["grouped_stream_speedup_vs_prepared_cupy_grid"] is not None
        ]
        status = "pass" if signature_ok and grouped_uses_rt and grouped_avoids_large_stream else "mismatch"
        return {
            "goal": "Goal2802",
            "entrypoint_version": GOAL2802_ENTRYPOINT_VERSION,
            "status": status,
            "app": "rt_dbscan",
            "benchmark_track": "live_grouped_stream_continuation",
            "dataset": "clustered3d",
            "point_counts": list(point_counts),
            "repeat_count": int(repeat_count),
            "source_commit": project_close.get("source_commit"),
            "source_dirty": project_close.get("source_dirty"),
            "gpu": project_close.get("gpu"),
            "cuda_nvcc": project_close.get("cuda_nvcc"),
            "rows": compact_rows,
            "min_grouped_stream_speedup_vs_prepared_cupy_grid": min(grouped_speedups) if grouped_speedups else None,
            "max_grouped_stream_speedup_vs_prepared_cupy_grid": max(grouped_speedups) if grouped_speedups else None,
            "signatures_match": signature_ok,
            "grouped_stream_rt_core_accelerated": grouped_uses_rt,
            "grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream": grouped_avoids_large_stream,
            "raw_artifacts_retained": raw_output_dir is not None,
            "claim_boundary": CLAIM_BOUNDARY,
            "elapsed_sec": time.perf_counter() - started,
        }
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2802 RT-DBSCAN v2.5 live grouped-stream harness.")
    parser.add_argument("--point-count", action="append", type=int, dest="point_counts")
    parser.add_argument("--repeat-count", type=int, default=DEFAULT_REPEAT_COUNT)
    parser.add_argument("--raw-output-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    point_counts = tuple(args.point_counts) if args.point_counts else DEFAULT_POINT_COUNTS
    payload = run_goal2802_rt_dbscan_live_harness(
        point_counts=point_counts,
        repeat_count=args.repeat_count,
        raw_output_dir=args.raw_output_dir,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
