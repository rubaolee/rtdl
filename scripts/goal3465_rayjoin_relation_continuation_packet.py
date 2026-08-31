from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def run_packet(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    relation_times: list[float] = []
    grouped_times: list[float] = []
    bounds_times: list[float] = []
    witness_times: list[float] = []
    total_times: list[float] = []
    row_counts: list[int] = []
    grouped_sums: list[int] = []
    group_counts: list[int] = []
    area_sums: list[float] = []
    witness_unresolved_counts: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3465 combined RayJoin relation-continuation packet.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        group_capacity = int(args.group_capacity or packed_left.id_capacity)
        for index in range(int(args.iterations)):
            total_start = time.perf_counter()
            relation_start = time.perf_counter()
            with prepared.active_relation_device_columns(
                packed_left,
                max_rows=int(args.max_rows),
            ) as columns:
                cp.cuda.Stream.null.synchronize()
                relation_sec = time.perf_counter() - relation_start
                grouped_start = time.perf_counter()
                with columns.grouped_count_by_id_compact_device_columns(
                    id_axis="left",
                    group_capacity=group_capacity,
                ) as grouped:
                    cp.cuda.Stream.null.synchronize()
                    grouped_sec = time.perf_counter() - grouped_start
                    grouped_count_sum = int(cp.sum(grouped.as_cupy_counts()).get())
                    grouped_row_count = int(grouped.row_count)
                    grouped_metadata = grouped.to_metadata()

                bounds_start = time.perf_counter()
                bounds = rt.shape_pair_relation_bounds_overlap_area_cupy(columns, group_by="left")
                cp.cuda.Stream.null.synchronize()
                bounds_sec = time.perf_counter() - bounds_start
                bounds_area_sum = float(cp.sum(bounds.row_areas).get()) if int(columns.row_count) else 0.0

                witness_start = time.perf_counter()
                witness = rt.shape_pair_relation_witness_cupy(columns)
                cp.cuda.Stream.null.synchronize()
                witness_sec = time.perf_counter() - witness_start
                witness_metadata = witness.to_metadata()

                total_sec = time.perf_counter() - total_start
                relation_times.append(relation_sec)
                grouped_times.append(grouped_sec)
                bounds_times.append(bounds_sec)
                witness_times.append(witness_sec)
                total_times.append(total_sec)
                row_counts.append(int(columns.row_count))
                grouped_sums.append(grouped_count_sum)
                group_counts.append(grouped_row_count)
                area_sums.append(bounds_area_sum)
                unresolved = int(witness_metadata["witness_kind_counts"].get("0", 0)) + int(
                    witness_metadata["witness_kind_counts"].get("4", 0)
                ) + int(witness_metadata["witness_kind_counts"].get("5", 0))
                witness_unresolved_counts.append(unresolved)
                run = {
                    "iteration": index,
                    "row_count": int(columns.row_count),
                    "grouped_count_sum": grouped_count_sum,
                    "grouped_left_row_count": grouped_row_count,
                    "bounds_overlap_area_sum": bounds_area_sum,
                    "witness_kind_counts": witness_metadata["witness_kind_counts"],
                    "unresolved_witness_count": unresolved,
                    "relation_columns_sec": relation_sec,
                    "grouped_count_sec": grouped_sec,
                    "bounds_overlap_area_sec": bounds_sec,
                    "witness_continuation_sec": witness_sec,
                    "total_relation_plus_continuations_sec": total_sec,
                    "grouped_metadata": grouped_metadata,
                    "bounds_metadata": bounds.to_metadata(),
                    "witness_metadata": witness_metadata,
                    "claim_boundary": _claim_boundary(),
                }
                runs.append(run)
                print(
                    "[goal3465] "
                    f"iteration={index} rows={run['row_count']} grouped_sum={grouped_count_sum} "
                    f"groups={grouped_row_count} area_sum={bounds_area_sum:.6f} "
                    f"unresolved={unresolved} relation={relation_sec:.6f}s grouped={grouped_sec:.6f}s "
                    f"bounds={bounds_sec:.6f}s witness={witness_sec:.6f}s total={total_sec:.6f}s",
                    flush=True,
                )

    return {
        "schema": "rtdl.goal3465.rayjoin_relation_continuation_packet.v1",
        "goal": 3465,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "group_capacity": int(args.group_capacity or group_capacity),
        "row_counts": row_counts,
        "grouped_count_sums": grouped_sums,
        "grouped_left_row_counts": group_counts,
        "bounds_overlap_area_sums": area_sums,
        "witness_unresolved_counts": witness_unresolved_counts,
        "all_row_counts_stable": len(set(row_counts)) == 1,
        "all_grouped_sums_match_rows": all(row == grouped for row, grouped in zip(row_counts, grouped_sums)),
        "all_group_counts_stable": len(set(group_counts)) == 1,
        "all_bounds_area_sums_stable": max(area_sums) - min(area_sums) <= 1.0e-6 if area_sums else True,
        "all_witnesses_resolved": all(count == 0 for count in witness_unresolved_counts),
        "relation_columns_sec": _stats(relation_times),
        "grouped_count_sec": _stats(grouped_times),
        "bounds_overlap_area_sec": _stats(bounds_times),
        "witness_continuation_sec": _stats(witness_times),
        "total_relation_plus_continuations_sec": _stats(total_times),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3465 combined RayJoin relation-continuation packet.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--group-capacity", type=int, default=0)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_packet(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if (
        not payload["all_row_counts_stable"]
        or not payload["all_grouped_sums_match_rows"]
        or not payload["all_witnesses_resolved"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
