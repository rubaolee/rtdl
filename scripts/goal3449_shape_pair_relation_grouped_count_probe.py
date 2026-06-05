from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
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
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    left_dataset = load_cdb(args.left_cdb)
    right_dataset = load_cdb(args.right_cdb)
    left_shapes = tuple(chains_to_polygons(left_dataset))
    right_shapes = tuple(chains_to_polygons(right_dataset))

    host_times: list[float] = []
    grouped_total_times: list[float] = []
    grouped_reduction_times: list[float] = []
    host_counts: list[int] = []
    grouped_sums: list[int] = []
    grouped_rows: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3449 generic shape-pair relation grouped-count continuation probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            host_payload = prepared.run_packed_left_host_exact(packed_left)
            grouped_payload = prepared.run_packed_left_active_relation_grouped_count_by_left(
                packed_left,
                max_rows=int(args.max_rows),
                group_capacity=int(args.group_capacity or packed_left.count),
            )
            host_count = int(host_payload["row_count"])
            grouped_sum = int(grouped_payload["summary"]["grouped_count_sum"])
            grouped_row_count = int(grouped_payload["summary"]["grouped_left_row_count"])
            host_time = float(host_payload["phases_sec"]["active_count_sec"])
            relation_time = float(grouped_payload["phases_sec"]["active_relation_device_columns_sec"])
            reduction_time = float(grouped_payload["phases_sec"]["active_relation_grouped_count_by_left_sec"])
            total_time = relation_time + reduction_time
            counts_match = host_count == grouped_sum
            host_counts.append(host_count)
            grouped_sums.append(grouped_sum)
            grouped_rows.append(grouped_row_count)
            host_times.append(host_time)
            grouped_total_times.append(total_time)
            grouped_reduction_times.append(reduction_time)
            runs.append(
                {
                    "iteration": index,
                    "host_count": host_count,
                    "grouped_count_sum": grouped_sum,
                    "grouped_left_row_count": grouped_row_count,
                    "counts_match": counts_match,
                    "host_active_count_sec": host_time,
                    "active_relation_device_columns_sec": relation_time,
                    "active_relation_grouped_count_by_left_sec": reduction_time,
                    "grouped_total_sec": total_time,
                    "grouped_speedup_vs_host": host_time / total_time if total_time > 0.0 else None,
                    "native_phase_timings": grouped_payload["native_phase_timings"],
                    "grouped_count_metadata": {
                        key: grouped_payload["grouped_count_metadata"][key]
                        for key in (
                            "schema",
                            "producer",
                            "device_resident",
                            "row_count",
                            "capacity",
                            "group_capacity",
                            "source_row_count",
                            "overflow",
                            "reduction_seconds",
                            "compaction_seconds",
                            "release_authorized",
                            "public_speedup_claim_authorized",
                            "rt_core_speedup_claim_authorized",
                            "true_zero_copy_authorized",
                        )
                    },
                    "claim_boundary": _claim_boundary(),
                }
            )
            print(
                "[goal3449] "
                f"iteration={index} host={host_count} grouped_sum={grouped_sum} "
                f"grouped_rows={grouped_row_count} match={counts_match} "
                f"host={host_time:.6f}s relation={relation_time:.6f}s "
                f"grouped={reduction_time:.6f}s total={total_time:.6f}s "
                f"speedup={(host_time / total_time if total_time > 0.0 else 0.0):.3f}x",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3449.shape_pair_relation_grouped_count.v1",
        "goal": 3449,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "max_rows": int(args.max_rows),
        "group_capacity": int(args.group_capacity or len(left_shapes)),
        "all_counts_match": all(h == g for h, g in zip(host_counts, grouped_sums)),
        "host_counts": host_counts,
        "grouped_count_sums": grouped_sums,
        "grouped_left_row_counts": grouped_rows,
        "host_active_count_sec": _stats(host_times),
        "grouped_total_sec": _stats(grouped_total_times),
        "grouped_reduction_sec": _stats(grouped_reduction_times),
        "grouped_speedup_vs_host": _stats(
            [h / g for h, g in zip(host_times, grouped_total_times) if g > 0.0]
        ),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3449 shape-pair relation grouped-count continuation probe.")
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
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
