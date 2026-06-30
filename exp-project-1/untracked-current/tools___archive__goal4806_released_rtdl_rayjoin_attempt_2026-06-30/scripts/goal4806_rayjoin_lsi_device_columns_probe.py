from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rayjoin_overlay import _PreparedLsiRowsRunner
from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs
from rtdsl.rayjoin_paper_suite import dataset_file
from rtdsl.rayjoin_paper_suite import paper_cases


def _case_by_id(case_id: str):
    for case in paper_cases():
        if case.case_id == case_id:
            return case
    raise SystemExit(f"unknown RayJoin paper case id: {case_id}")


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Goal4806 RayJoin LSI device-column row-output probe"
    )
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    case = _case_by_id(args.case_id)
    if case.program.program_id != "lsi":
        raise SystemExit("device-column LSI probe requires an lsi case")

    base_inputs = load_cdb_overlay_packed_inputs(dataset_file(args.dataset_root, case.pair.left_relative_path))
    query_inputs = load_cdb_overlay_packed_inputs(dataset_file(args.dataset_root, case.pair.right_relative_path))
    runs = []
    with _PreparedLsiRowsRunner(
        "optix",
        base_inputs.segments,
        query_inputs.segments,
        None,
        None,
        left_coords=base_inputs.segment_coords,
        right_coords=query_inputs.segment_coords,
    ) as runner:
        for iteration in range(int(args.warmup) + int(args.repeat)):
            is_warmup = iteration < int(args.warmup)
            start = time.perf_counter()
            count, count_timings = runner.count()
            count_wall_sec = time.perf_counter() - start

            emit_start = time.perf_counter()
            columns = runner.prepared.exact_device_columns_prepared_left(
                runner.prepared_left,
                max_rows=int(count),
            )
            emit_wall_sec = time.perf_counter() - emit_start
            try:
                columns.raise_if_overflowed(operation="goal4806_lsi_device_columns_probe")
                copy_start = time.perf_counter()
                cupy_columns = columns.as_cupy_columns()
                import cupy as cp  # type: ignore

                left_ids = cp.asnumpy(cupy_columns["left_id"])
                right_ids = cp.asnumpy(cupy_columns["right_id"])
                copy_wall_sec = time.perf_counter() - copy_start
                row_count = int(columns.row_count)
                first_pair = None
                if row_count:
                    first_pair = [int(left_ids[0]), int(right_ids[0])]
            finally:
                columns.close()
            total_sec = time.perf_counter() - start
            runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": is_warmup,
                    "count": int(count),
                    "row_count": int(row_count),
                    "first_pair": first_pair,
                    "count_wall_sec": float(count_wall_sec),
                    "emit_wall_sec": float(emit_wall_sec),
                    "copy_wall_sec": float(copy_wall_sec),
                    "total_sec": float(total_sec),
                    "count_native_timings": count_timings,
                    "device_columns": {
                        "row_count": int(columns.row_count),
                        "candidate_event_count": int(columns.candidate_event_count),
                        "capacity": int(columns.capacity),
                        "overflow": bool(columns.overflow),
                        "device_ordinal": int(columns.device_ordinal),
                        "traversal_seconds": float(columns.traversal_seconds),
                        "native_symbol": columns.native_symbol,
                        "has_intersection_point_columns": bool(columns.has_intersection_point_columns),
                    },
                }
            )

    hot = [run for run in runs if not run["is_warmup"]]
    payload = {
        "schema": "rtdl.goal4806.rayjoin_lsi_device_columns_probe.v1",
        "case_id": case.case_id,
        "pair_id": case.pair.pair_id,
        "paper_label": case.pair.paper_label,
        "program": "lsi",
        "input_shape": {
            "base_segments": int(base_inputs.edge_count),
            "query_segments": int(query_inputs.edge_count),
        },
        "prepare_seconds": {
            "left": float(runner.prepare_left_sec),
            "right": float(runner.prepare_right_sec),
            "total": float(runner.prepare_total_sec),
        },
        "hot_median_seconds": {
            "count": _median([float(run["count_wall_sec"]) for run in hot]),
            "emit": _median([float(run["emit_wall_sec"]) for run in hot]),
            "copy": _median([float(run["copy_wall_sec"]) for run in hot]),
            "total": _median([float(run["total_sec"]) for run in hot]),
        },
        "count": int(hot[0]["count"]) if hot else None,
        "counts_stable": len({int(run["count"]) for run in hot}) <= 1 if hot else None,
        "row_counts_stable": len({int(run["row_count"]) for run in hot}) <= 1 if hot else None,
        "claim_boundary": {
            "diagnostic_only": True,
            "full_overlay_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
        "runs": runs,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
