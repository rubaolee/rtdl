from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import subprocess
import sys


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    plan_rt_dbscan_continuation_execution,
    plan_rt_dbscan_execution,
    run_rt_dbscan_benchmark,
)
from scripts.goal2403_rt_dbscan_repeat_probe import (  # noqa: E402
    PREPARED_CUPY_GRID_MODE,
    PREPARED_GRID_MODE,
    run_repeat_probe,
)
from scripts.goal2467_grouped_stream_baseline_pod_runner import (  # noqa: E402
    _run_grouped_stream_repeats,
)


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _tail_median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute a median for an empty list")
    tail = values[1:] if len(values) > 1 else values
    return float(statistics.median(tail))


def _nvcc_version_line() -> str | None:
    output = _check_output(["nvcc", "--version"])
    if not output:
        return None
    lines = output.splitlines()
    return lines[-1] if lines else None


def _summarize_repeat_probe(probe: dict[str, object]) -> dict[str, object]:
    modes = list(probe["modes"])
    rows = list(probe["rows"])
    summaries: dict[str, dict[str, object]] = {}
    for mode in modes:
        mode_rows = [row for row in rows if row.get("mode") == mode]
        elapsed = [float(row["outer_elapsed_sec"]) for row in mode_rows]
        summaries[mode] = {
            "mode": mode,
            "tail_median_sec": _tail_median(elapsed),
            "repeat_count": len(mode_rows),
            "rt_core_accelerated": bool(mode_rows[-1].get("rt_core_accelerated")) if mode_rows else False,
            "materializes_neighbor_rows": bool(mode_rows[-1].get("materializes_neighbor_rows")) if mode_rows else False,
            "signatures_match_probe": bool(probe.get("signatures_match")),
        }
    if PREPARED_CUPY_GRID_MODE in summaries and PREPARED_GRID_MODE in summaries:
        cupy = float(summaries[PREPARED_CUPY_GRID_MODE]["tail_median_sec"])
        rt = float(summaries[PREPARED_GRID_MODE]["tail_median_sec"])
        summaries[PREPARED_GRID_MODE]["speedup_vs_prepared_cupy_grid"] = cupy / rt if rt > 0 else None
    return summaries


def run_project_close_matrix(
    *,
    output_dir: pathlib.Path,
    point_counts: tuple[int, ...],
    repeat_count: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset = "clustered3d"
    summaries = []
    raw_artifacts = {}
    for point_count in point_counts:
        repeat_probe = run_repeat_probe(
            dataset=dataset,
            point_count=point_count,
            repeat_count=repeat_count,
            modes=(PREPARED_CUPY_GRID_MODE, PREPARED_GRID_MODE),
        )
        grouped = _run_grouped_stream_repeats(
            point_count=point_count,
            repeat_count=repeat_count,
            signature_mode="column",
            grouped_union_same_root_culling=True,
            grouped_union_direct_side_effect=False,
        )
        planned = run_rt_dbscan_benchmark(
            mode="planned_rt_dbscan",
            dataset=dataset,
            point_count=point_count,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=False,
        )
        continuation_planned = run_rt_dbscan_benchmark(
            mode="planned_rt_dbscan_continuation",
            dataset=dataset,
            point_count=point_count,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=False,
        )
        repeat_summary = _summarize_repeat_probe(repeat_probe)
        grouped_summary = {
            "mode": "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "tail_median_sec": grouped["tail_median_sec"],
            "grouped_native_tail_median_sec": grouped["grouped_native_tail_median_sec"],
            "repeat_count": repeat_count,
            "rt_core_accelerated": True,
            "materializes_neighbor_rows": False,
            "materializes_directed_adjacency_stream": False,
            "signatures_match_probe": grouped["signatures_match"],
        }
        cupy_median = float(repeat_summary[PREPARED_CUPY_GRID_MODE]["tail_median_sec"])
        grouped_median = float(grouped_summary["tail_median_sec"])
        grouped_summary["speedup_vs_prepared_cupy_grid"] = cupy_median / grouped_median if grouped_median > 0 else None
        point_summary = {
            "dataset": dataset,
            "point_count": point_count,
            "repeat_probe_summary": repeat_summary,
            "grouped_stream_summary": grouped_summary,
            "planned_rt_dbscan_selected_mode": planned.get("selected_mode"),
            "planned_rt_dbscan_reason": planned.get("metadata", {}).get("execution_plan", {}).get("reason"),
            "planned_continuation_selected_mode": continuation_planned.get("selected_mode"),
            "planned_continuation_reason": continuation_planned.get("metadata", {}).get("execution_plan", {}).get("reason"),
            "planned_continuation_policy": plan_rt_dbscan_continuation_execution(dataset, point_count),
            "planned_high_level_policy": plan_rt_dbscan_execution(dataset, point_count),
        }
        summaries.append(point_summary)
        raw_artifacts[str(point_count)] = {
            "repeat_probe": repeat_probe,
            "grouped_stream": grouped,
            "planned_rt_dbscan": planned,
            "planned_rt_dbscan_continuation": continuation_planned,
        }
        (output_dir / f"clustered3d_{point_count}_project_close.json").write_text(
            json.dumps(raw_artifacts[str(point_count)], indent=2, sort_keys=True),
            encoding="utf-8",
        )

    summary = {
        "app": "rt_dbscan_project_close_matrix",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_tree_is_git_checkout": (ROOT / ".git").exists(),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cuda_nvcc": _nvcc_version_line(),
        "dataset": dataset,
        "point_counts": list(point_counts),
        "repeat_count": repeat_count,
        "summaries": summaries,
        "claim_boundary": {
            "paper_dataset_reproduction": False,
            "paper_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "project_close_internal_evidence": True,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect RT-DBSCAN project-close pod evidence.")
    parser.add_argument("--output-dir", default="docs/reports/goal2478_rt_dbscan_project_close_pod")
    parser.add_argument("--point-count", action="append", type=int, dest="point_counts")
    parser.add_argument("--repeat-count", type=int, default=3)
    args = parser.parse_args(argv)
    if args.repeat_count < 2:
        raise ValueError("repeat-count must be at least 2 so the close matrix can drop the first timing row")
    point_counts = tuple(args.point_counts) if args.point_counts else (32768, 65536, 131072)
    print(
        json.dumps(
            run_project_close_matrix(
                output_dir=pathlib.Path(args.output_dir),
                point_counts=point_counts,
                repeat_count=args.repeat_count,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
