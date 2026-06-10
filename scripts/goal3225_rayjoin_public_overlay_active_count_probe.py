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

from examples.current.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as rayjoin
from scripts.goal2159_rayjoin_public_cdb_runner import CASES
from scripts.goal2159_rayjoin_public_cdb_runner import DEFAULT_DATA_DIR
from scripts.goal2159_rayjoin_public_cdb_runner import _materialize_slices
from scripts.goal2159_rayjoin_public_cdb_runner import _maybe_download_samples
from scripts.goal2159_rayjoin_public_cdb_runner import _resolve_dataset_template


DEFAULT_CASES = (
    "overlay_county128_soil128",
    "overlay_county256_soil256",
)

CANONICAL_CLAIM_BOUNDARY = {
    "public_speedup_claim_authorized": False,
    "rt_core_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "release_authorized": False,
}


def _command_text(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT, text=True).strip()
    except Exception:
        return None


def _first_command_text(commands: tuple[list[str], ...]) -> str | None:
    for command in commands:
        value = _command_text(command)
        if value:
            return value
    return None


def _commit() -> str:
    return _command_text(["git", "rev-parse", "HEAD"]) or "unknown"


def _hardware_metadata() -> dict[str, object]:
    return {
        "nvidia_smi": _first_command_text(
            (
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                ["/usr/bin/nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            )
        ),
        "cuda_driver_query": _first_command_text(
            (
                ["nvidia-smi", "--query", "--display=COMPUTE"],
                ["/usr/bin/nvidia-smi", "--query", "--display=COMPUTE"],
            )
        ),
        "nvcc_version": _first_command_text(
            (
                ["nvcc", "--version"],
                ["/usr/local/cuda/bin/nvcc", "--version"],
            )
        ),
        "rtdl_optix_library": os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB"),
    }


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _active_seed_count(summary: dict[str, Any]) -> int:
    if "active_seed_count" not in summary:
        raise KeyError("overlay CPU summary missing active_seed_count")
    return int(summary["active_seed_count"])


def _run_prepared_count(dataset: str) -> dict[str, Any]:
    start = time.perf_counter()
    payload = rayjoin.run_rayjoin_prepared_optix_workload(
        "overlay_seed",
        dataset=dataset,
        result_mode="count",
        include_rows=False,
    )
    return {
        "total_seconds": time.perf_counter() - start,
        "row_count": int(payload["row_count"]),
        "summary": payload.get("summary", {}),
        "phases_sec": payload.get("phases_sec", {}),
        "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
    }


def _run_case(case_name: str, *, dataset: str, warmups: int, repeats: int) -> dict[str, object]:
    cpu_payload = rayjoin.run_rayjoin_workload(
        "overlay_seed",
        backend="cpu_python_reference",
        dataset=dataset,
        include_rows=False,
    )
    expected_active_count = _active_seed_count(dict(cpu_payload["summary"]))
    for index in range(warmups):
        sample = _run_prepared_count(dataset)
        print(
            f"[goal3225] warmup {case_name}/prepared_overlay_active_count {index + 1}/{warmups} "
            f"sec={sample['total_seconds']:.6f} rows={sample['row_count']}",
            flush=True,
        )
    measurements: list[dict[str, Any]] = []
    for index in range(repeats):
        sample = _run_prepared_count(dataset)
        measurements.append(sample)
        print(
            f"[goal3225] repeat {case_name}/prepared_overlay_active_count {index + 1}/{repeats} "
            f"sec={sample['total_seconds']:.6f} rows={sample['row_count']}",
            flush=True,
        )

    seconds = [float(row["total_seconds"]) for row in measurements]
    observed_counts = [int(row["row_count"]) for row in measurements]
    return {
        "case": case_name,
        "dataset": dataset,
        "dataset_note": rayjoin._load_rayjoin_case("overlay_seed", dataset).note,
        "expected_active_seed_count": expected_active_count,
        "observed_counts": observed_counts,
        "counts_match": bool(observed_counts) and all(count == expected_active_count for count in observed_counts),
        "measurements": {
            "include_rows_measured": False,
            "prepared_overlay_active_count": measurements,
        },
        "medians": {
            "prepared_total_seconds": _median(seconds),
        },
        "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
    }


def build_artifact(args: argparse.Namespace) -> dict[str, object]:
    selected = tuple(CASES[name] for name in args.cases.split(",") if name)
    for case in selected:
        if case.workload != "overlay_seed":
            raise ValueError("goal3225 probe supports only overlay_seed cases")
    data_dir = Path(args.data_dir)
    _maybe_download_samples(data_dir, download=args.download)
    slices = _materialize_slices(data_dir, selected)
    rows = []
    for case in selected:
        dataset = _resolve_dataset_template(case.dataset, slices)
        rows.append(_run_case(case.label, dataset=dataset, warmups=args.warmups, repeats=args.repeats))
    return {
        "goal": 3225,
        "schema": "rtdl.goal3225.rayjoin_public_overlay_active_count_probe.v1",
        "commit": _commit(),
        "hardware": _hardware_metadata(),
        "data_dir": str(data_dir),
        "slices": slices,
        "warmups": args.warmups,
        "repeats": args.repeats,
        "rows": rows,
        "status": "pass" if rows and all(row["counts_match"] for row in rows) else "fail",
        "claim_boundary": dict(CANONICAL_CLAIM_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe public RayJoin overlay active-count slices with prepared OptiX.")
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
    print(f"[goal3225] wrote {output}", flush=True)
    if artifact["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
