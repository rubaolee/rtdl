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
    device_times: list[float] = []
    host_counts: list[int] = []
    device_counts: list[int] = []
    runs: list[dict[str, object]] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3442 generic shape-pair active-count device-continuation probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            host_payload = prepared.run_packed_left(packed_left)
            device_payload = prepared.run_packed_left_device_continuation(packed_left)
            host_count = int(host_payload["row_count"])
            device_count = int(device_payload["row_count"])
            host_time = float(host_payload["phases_sec"]["active_count_sec"])
            device_time = float(device_payload["phases_sec"]["active_count_device_continuation_sec"])
            host_counts.append(host_count)
            device_counts.append(device_count)
            host_times.append(host_time)
            device_times.append(device_time)
            counts_match = host_count == device_count
            runs.append(
                {
                    "iteration": index,
                    "host_count": host_count,
                    "device_count": device_count,
                    "counts_match": counts_match,
                    "host_active_count_sec": host_time,
                    "device_active_count_sec": device_time,
                    "device_speedup_vs_host": host_time / device_time if device_time > 0.0 else None,
                    "host_native_phase_timings": host_payload["native_phase_timings"],
                    "device_native_phase_timings": device_payload["native_phase_timings"],
                    "claim_boundary": _claim_boundary(),
                }
            )
            print(
                "[goal3442] "
                f"iteration={index} host_count={host_count} device_count={device_count} "
                f"match={counts_match} host={host_time:.6f}s device={device_time:.6f}s "
                f"speedup={(host_time / device_time if device_time > 0.0 else 0.0):.3f}x",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3442.shape_pair_active_count_device_continuation.v1",
        "goal": 3442,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "all_counts_match": all(h == d for h, d in zip(host_counts, device_counts)),
        "host_counts": host_counts,
        "device_counts": device_counts,
        "host_active_count_sec": _stats(host_times),
        "device_active_count_sec": _stats(device_times),
        "device_speedup_vs_host": _stats(
            [h / d for h, d in zip(host_times, device_times) if d > 0.0]
        ),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3442 shape-pair active-count device-continuation probe.")
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
