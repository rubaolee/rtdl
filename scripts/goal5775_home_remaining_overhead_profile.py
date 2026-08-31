#!/usr/bin/env python3
"""Observation-only host profile for the largest post-Goal5775 residuals."""

from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
from pathlib import Path
import platform
import pstats
import statistics

from goal5774_prepared_three_way_frontdoors import V4, prepare_three_way


LANES = ("rayjoin__grouped_events", "rtbh__force", "triangle__rt_1a2")


def run(runtime_path: Path, output: Path, repeat: int) -> Path:
    if repeat < 4:
        raise ValueError("repeat must be at least four")
    runtime = json.loads(runtime_path.read_text())
    rows = []
    for lane_id in LANES:
        owner = prepare_three_way(lane_id, V4, runtime=runtime)
        try:
            activation = owner.execute(2)
            if activation["matched"] is not True:
                raise RuntimeError(f"{lane_id}: activation mismatch")
            profiler = cProfile.Profile()
            calls = []
            profiler.enable()
            try:
                for index in range(repeat):
                    call = owner.execute(index % 2)
                    if call["matched"] is not True:
                        raise RuntimeError(f"{lane_id}: output mismatch")
                    calls.append(float(call["registered_prepared_execution_seconds"]))
            finally:
                profiler.disable()
            stats = pstats.Stats(profiler)
            functions = []
            for (filename, line, function), values in stats.stats.items():
                primitive_calls, total_calls, total_time, cumulative_time, _ = values
                functions.append({
                    "file": filename,
                    "line": line,
                    "function": function,
                    "primitive_calls": primitive_calls,
                    "total_calls": total_calls,
                    "total_seconds": total_time,
                    "cumulative_seconds": cumulative_time,
                })
            functions.sort(key=lambda row: row["cumulative_seconds"], reverse=True)
            rows.append({
                "lane_id": lane_id,
                "repeat": repeat,
                "registered_seconds_median": statistics.median(calls),
                "registered_seconds": calls,
                "profile_total_calls": stats.total_calls,
                "profile_total_seconds": stats.total_tt,
                "top_by_cumulative_seconds": functions[:80],
            })
        finally:
            owner.close()
    payload = {
        "schema": "rtdl.goal5775.home_remaining_overhead_profile.v1",
        "observation_only": True,
        "profiler_perturbed_not_formal": True,
        "predicted_saving_claimed": False,
        "python_version": platform.python_version(),
        "native_library_sha256": runtime["native_library_sha256"],
        "rows": rows,
    }
    payload["result_sha256"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=20)
    args = parser.parse_args()
    print(run(args.runtime, args.output, args.repeat))


if __name__ == "__main__":
    main()
