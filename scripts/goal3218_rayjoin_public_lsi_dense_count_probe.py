from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.benchmark_apps.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as rayjoin
from scripts.goal2159_rayjoin_public_cdb_runner import CASES
from scripts.goal2159_rayjoin_public_cdb_runner import DEFAULT_DATA_DIR
from scripts.goal2159_rayjoin_public_cdb_runner import _materialize_slices
from scripts.goal2159_rayjoin_public_cdb_runner import _maybe_download_samples
from scripts.goal2159_rayjoin_public_cdb_runner import _resolve_dataset_template


DEFAULT_CASES = (
    "lsi_county256_soil256_count48",
    "lsi_county256_soil256_count128",
    "lsi_county256_soil256_count192",
    "lsi_county256_soil256_count256",
    "lsi_county256_soil256_count384",
    "lsi_county256_soil256_count512",
)


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _command_text(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()
    except Exception:
        return None


def _hardware_metadata() -> dict[str, object]:
    nvidia_smi = _command_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version",
            "--format=csv,noheader",
        ]
    )
    if nvidia_smi is None and Path("/usr/bin/nvidia-smi").exists():
        nvidia_smi = _command_text(
            [
                "/usr/bin/nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ]
        )
    cuda_driver = _command_text(["nvidia-smi", "--query", "--display=COMPUTE"])
    if cuda_driver is None and Path("/usr/bin/nvidia-smi").exists():
        cuda_driver = _command_text(["/usr/bin/nvidia-smi", "--query", "--display=COMPUTE"])
    nvcc = _command_text(["nvcc", "--version"])
    if nvcc is None and Path("/usr/local/cuda/bin/nvcc").exists():
        nvcc = _command_text(["/usr/local/cuda/bin/nvcc", "--version"])
    return {
        "nvidia_smi": nvidia_smi,
        "cuda_driver_query": cuda_driver,
        "nvcc_version": nvcc,
        "rtdl_optix_library": os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB"),
    }


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _run_once(prepared, packed_left, *, route: str, include_rows: bool) -> dict[str, Any]:
    start = time.perf_counter()
    if route == "dense":
        payload = prepared.run_packed_left_dense_count(packed_left, include_rows=include_rows)
    elif route == "compact":
        payload = prepared.run_packed_left(packed_left, include_rows=include_rows)
    else:
        raise ValueError("route must be dense or compact")
    return {
        "total_seconds": time.perf_counter() - start,
        "row_count": int(payload["row_count"]),
        "has_rows": "rows" in payload,
        "phases_sec": payload.get("phases_sec", {}),
        "summary": payload.get("summary", {}),
        "claim_boundary": payload.get("claim_boundary", {}),
    }


def _run_case(case_name: str, *, dataset: str, warmups: int, repeats: int) -> dict[str, object]:
    case = rayjoin._load_rayjoin_case("lsi", dataset)
    with rayjoin.prepare_rayjoin_optix_compact_grouped_count_segments(
        case.inputs["right"],
        dataset=dataset,
        dataset_note=case.note,
    ) as prepared:
        packed_left = rayjoin.pack_rayjoin_optix_compact_grouped_count_left_segments(case.inputs["left"])
        validation = {
            "dense": _run_once(prepared, packed_left, route="dense", include_rows=True),
            "compact": _run_once(prepared, packed_left, route="compact", include_rows=True),
        }
        dense_rows = validation["dense"]["summary"].get("intersection_count")
        compact_rows = validation["compact"]["summary"].get("intersection_count")
        for route in ("dense", "compact"):
            for index in range(warmups):
                sample = _run_once(prepared, packed_left, route=route, include_rows=False)
                print(
                    f"[goal3218] warmup {case_name}/{route} {index + 1}/{warmups} "
                    f"sec={sample['total_seconds']:.6f} rows={sample['row_count']}",
                    flush=True,
                )
        measurements: dict[str, list[dict[str, Any]]] = {"dense": [], "compact": []}
        for route in ("dense", "compact"):
            for index in range(repeats):
                sample = _run_once(prepared, packed_left, route=route, include_rows=False)
                measurements[route].append(sample)
                print(
                    f"[goal3218] repeat {case_name}/{route} {index + 1}/{repeats} "
                    f"sec={sample['total_seconds']:.6f} rows={sample['row_count']}",
                    flush=True,
                )

    dense_seconds = [float(row["total_seconds"]) for row in measurements["dense"]]
    compact_seconds = [float(row["total_seconds"]) for row in measurements["compact"]]
    dense_median = _median(dense_seconds)
    compact_median = _median(compact_seconds)
    ratio = (dense_median / compact_median) if dense_median is not None and compact_median else None
    return {
        "case": case_name,
        "dataset": dataset,
        "dataset_note": case.note,
        "left_segment_count": len(case.inputs["left"]),
        "right_segment_count": len(case.inputs["right"]),
        "prepare_static_scene_sec": prepared.prepare_static_scene_sec,
        "packed_left": {
            "left_segment_count": packed_left.count,
            "pack_seconds": packed_left.pack_seconds,
        },
        "validation": {
            "include_rows": True,
            "dense_intersection_count": dense_rows,
            "compact_intersection_count": compact_rows,
            "counts_match": dense_rows == compact_rows,
        },
        "measurements": {
            "include_rows_measured": False,
            "dense": measurements["dense"],
            "compact": measurements["compact"],
        },
        "medians": {
            "dense_total_seconds": dense_median,
            "compact_total_seconds": compact_median,
            "dense_over_compact_ratio": ratio,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "release_authorized": False,
        },
    }


def build_artifact(args: argparse.Namespace) -> dict[str, object]:
    selected = tuple(CASES[name] for name in args.cases.split(",") if name)
    for case in selected:
        if case.workload != "lsi":
            raise ValueError("goal3218 probe supports only LSI cases")
    data_dir = Path(args.data_dir)
    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected)
    rows = []
    for case in selected:
        dataset = _resolve_dataset_template(case.dataset, slices)
        rows.append(_run_case(case.label, dataset=dataset, warmups=args.warmups, repeats=args.repeats))
    return {
        "goal": 3218,
        "schema": "rtdl.goal3218.rayjoin_public_lsi_dense_count_probe.v1",
        "commit": _commit(),
        "hardware": _hardware_metadata(),
        "data_dir": str(data_dir),
        "slices": slices,
        "warmups": args.warmups,
        "repeats": args.repeats,
        "rows": rows,
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "release_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe RayJoin public LSI slices with compact vs fused dense count routes.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output", required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--cases", default=",".join(DEFAULT_CASES))
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = build_artifact(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rayjoin._json_ready(artifact), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[goal3218] wrote {output}", flush=True)


if __name__ == "__main__":
    main()
