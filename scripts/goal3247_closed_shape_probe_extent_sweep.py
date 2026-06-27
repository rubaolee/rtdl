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


CLAIM_BOUNDARY = {
    "release_authorized": False,
    "public_speedup_claim_authorized": False,
    "rtdl_beats_rayjoin_claim_authorized": False,
    "rayjoin_paper_reproduction_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
}


CHILD_CODE = r"""
import json
import os
import statistics

from examples.benchmark_apps.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as app,
)

dataset = os.environ["GOAL3247_DATASET"]
warmup = int(os.environ["GOAL3247_WARMUP"])
repeat = int(os.environ["GOAL3247_REPEAT"])

for _ in range(warmup):
    app.run_rayjoin_prepared_optix_workload(
        "pip",
        dataset=dataset,
        result_mode="count",
        include_rows=False,
    )

rows = []
for _ in range(repeat):
    payload = app.run_rayjoin_prepared_optix_workload(
        "pip",
        dataset=dataset,
        result_mode="count",
        include_rows=False,
    )
    rows.append(
        {
            "count": int(payload["row_count"]),
            "prepared_query_sec": float(payload["phases_sec"]["prepared_query_sec"]),
            "native": payload.get("native_phase_timings") or {},
        }
    )

def median(values):
    return float(statistics.median(values)) if values else None

phase_keys = set()
for row in rows:
    phase_keys.update(
        key
        for key, value in row["native"].items()
        if isinstance(value, (int, float))
    )

print(
    json.dumps(
        {
            "extent": os.environ.get(
                "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT",
                "default",
            ),
            "rows": rows,
            "summary": {
                "counts": [row["count"] for row in rows],
                "count_consistent": len({row["count"] for row in rows}) <= 1,
                "prepared_query_ms_median": median(
                    [row["prepared_query_sec"] * 1000.0 for row in rows]
                ),
                "phase_medians_ms": {
                    key: median(
                        [
                            float(row["native"].get(key, 0.0)) * 1000.0
                            for row in rows
                        ]
                    )
                    for key in sorted(phase_keys)
                },
            },
        },
        sort_keys=True,
    )
)
"""


def _command_output(command: list[str]) -> str | None:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _run_extent(
    *,
    extent: str,
    dataset: str,
    warmup: int,
    repeat: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["GOAL3247_DATASET"] = dataset
    env["GOAL3247_WARMUP"] = str(int(warmup))
    env["GOAL3247_REPEAT"] = str(int(repeat))
    if extent == "default":
        env.pop("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT", None)
    else:
        env["RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT"] = extent

    print(f"[goal3247] extent {extent} start", flush=True)
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-c", CHILD_CODE],
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout_seconds,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        print(f"[goal3247] extent {extent} error rc={proc.returncode}", flush=True)
        return {
            "extent": extent,
            "status": "error",
            "elapsed_sec": elapsed,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    payload["status"] = "ok"
    payload["elapsed_sec"] = elapsed
    payload["stderr_tail"] = proc.stderr[-2000:]
    summary = payload["summary"]
    print(
        "[goal3247] extent {} count={} median_ms={:.6f} candidate_write={}".format(
            extent,
            summary["counts"][-1],
            summary["prepared_query_ms_median"],
            summary["phase_medians_ms"].get("candidate_write_pass"),
        ),
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sweep closed-shape membership OptiX probe half extents."
    )
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--extents",
        nargs="+",
        default=[
            "default",
            "0.5",
            "0.35",
            "0.3",
            "0.275",
            "0.25",
            "0.225",
            "0.2",
            "0.175",
            "0.15",
            "0.125",
        ],
    )
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=240)
    args = parser.parse_args()

    results = [
        _run_extent(
            extent=extent,
            dataset=args.dataset,
            warmup=args.warmup,
            repeat=args.repeat,
            timeout_seconds=args.timeout_seconds,
        )
        for extent in args.extents
    ]

    valid = [
        result
        for result in results
        if result.get("status") == "ok"
        and result.get("summary", {}).get("count_consistent")
    ]
    expected_count = None
    for result in valid:
        if result.get("extent") == "default":
            expected_count = result["summary"]["counts"][-1]
            break
    matching = [
        result
        for result in valid
        if expected_count is not None
        and result["summary"]["counts"][-1] == expected_count
    ]
    best_matching = min(
        matching,
        key=lambda result: result["summary"]["prepared_query_ms_median"],
        default=None,
    )
    default_result = next((result for result in valid if result.get("extent") == "default"), None)

    summary: dict[str, Any] = {
        "expected_count_from_default": expected_count,
        "matching_extent_count": len(matching),
        "best_matching_extent": best_matching["extent"] if best_matching else None,
        "best_matching_median_ms": (
            best_matching["summary"]["prepared_query_ms_median"] if best_matching else None
        ),
        "default_median_ms": (
            default_result["summary"]["prepared_query_ms_median"] if default_result else None
        ),
        "best_matching_speedup_over_default": None,
    }
    if (
        best_matching
        and default_result
        and best_matching["summary"]["prepared_query_ms_median"]
    ):
        summary["best_matching_speedup_over_default"] = (
            default_result["summary"]["prepared_query_ms_median"]
            / best_matching["summary"]["prepared_query_ms_median"]
        )

    output = {
        "schema": "rtdl.goal3247.closed_shape_probe_extent_sweep.v1",
        "goal": 3247,
        "commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_command_output(["git", "status", "--short"]) or "").splitlines(),
        "dataset": args.dataset,
        "gpu": _command_output(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]
        ),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": summary,
        "results": results,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"written": str(output_path), "result_count": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
