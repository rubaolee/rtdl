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

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
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
    return {
        "min": min(values),
        "median": statistics.median(values),
        "max": max(values),
    }


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
    runs: list[dict[str, object]] = []
    active_counts: list[int] = []
    active_count_seconds: list[float] = []
    left_prepare_seconds: list[float] = []
    left_upload_seconds: list[float] = []
    containment_seconds: list[float] = []
    active_scan_seconds: list[float] = []
    traversal_seconds: list[float] = []
    download_seconds: list[float] = []
    measured_phase_sum_seconds: list[float] = []
    unattributed_seconds: list[float] = []

    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3441 generic shape-pair active-count phase timing probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for index in range(int(args.iterations)):
            payload = prepared.run_packed_left_host_exact(packed_left)
            timings = dict(payload["native_phase_timings"] or {})
            active_count = int(payload["row_count"])
            elapsed = float(payload["phases_sec"]["active_count_sec"])
            measured_sum = sum(
                float(timings.get(key, 0.0))
                for key in (
                    "left_prepare",
                    "left_upload",
                    "traversal",
                    "flag_download",
                    "containment",
                    "active_scan",
                )
            )
            active_counts.append(active_count)
            active_count_seconds.append(elapsed)
            left_prepare_seconds.append(float(timings.get("left_prepare", 0.0)))
            left_upload_seconds.append(float(timings.get("left_upload", 0.0)))
            containment_seconds.append(float(timings.get("containment", 0.0)))
            active_scan_seconds.append(float(timings.get("active_scan", 0.0)))
            traversal_seconds.append(float(timings.get("traversal", 0.0)))
            download_seconds.append(float(timings.get("flag_download", 0.0)))
            measured_phase_sum_seconds.append(measured_sum)
            unattributed_seconds.append(max(0.0, elapsed - measured_sum))
            runs.append(
                {
                    "iteration": index,
                    "active_count": active_count,
                    "active_count_sec": elapsed,
                    "measured_native_phase_sum_sec": measured_sum,
                    "unattributed_host_orchestration_sec": max(0.0, elapsed - measured_sum),
                    "native_phase_timings": timings,
                    "claim_boundary": payload["claim_boundary"],
                }
            )
            print(
                "[goal3441] "
                f"iteration={index} active_count={active_count} total={elapsed:.6f}s "
                f"traversal={float(timings.get('traversal', 0.0)):.6f}s "
                f"download={float(timings.get('flag_download', 0.0)):.6f}s "
                f"containment={float(timings.get('containment', 0.0)):.6f}s "
                f"active_scan={float(timings.get('active_scan', 0.0)):.6f}s "
                f"residual={max(0.0, elapsed - measured_sum):.6f}s",
                flush=True,
            )

    return {
        "schema": "rtdl.goal3441.shape_pair_active_count_phase_timings.v1",
        "goal": 3441,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "iterations": int(args.iterations),
        "active_counts": active_counts,
        "active_count_sec": _stats(active_count_seconds),
        "left_prepare_sec": _stats(left_prepare_seconds),
        "left_upload_sec": _stats(left_upload_seconds),
        "containment_sec": _stats(containment_seconds),
        "active_scan_sec": _stats(active_scan_seconds),
        "traversal_sec": _stats(traversal_seconds),
        "flag_download_sec": _stats(download_seconds),
        "measured_native_phase_sum_sec": _stats(measured_phase_sum_seconds),
        "unattributed_host_orchestration_sec": _stats(unattributed_seconds),
        "last_native_phase_timings": runs[-1]["native_phase_timings"] if runs else None,
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3441 shape-pair active-count phase timing probe.")
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
