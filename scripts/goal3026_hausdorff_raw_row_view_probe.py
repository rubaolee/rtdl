from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


METHODS = (
    "rtdl_rt_grouped_adaptive_nearest_witness",
    "rtdl_rt_grouped_adaptive_raw_nearest_witness",
    "cupy_grouped_grid_rawkernel",
)


def _result_payload(result) -> dict[str, object]:
    if is_dataclass(result):
        return asdict(result)
    if hasattr(result, "__dict__"):
        return dict(result.__dict__)
    return dict(result)


def _run_method(points_a, points_b, method: str):
    if method == "rtdl_rt_grouped_adaptive_nearest_witness":
        return hd.hausdorff_distance_2d_rt_grouped_adaptive_nearest_witness(
            points_a,
            points_b,
            max_iterations=32,
        )
    if method == "rtdl_rt_grouped_adaptive_raw_nearest_witness":
        return hd.hausdorff_distance_2d_rt_grouped_adaptive_raw_nearest_witness(
            points_a,
            points_b,
            max_iterations=32,
        )
    if method == "cupy_grouped_grid_rawkernel":
        return hd.hausdorff_distance_2d(
            points_a,
            points_b,
            method="cupy_grouped_grid_rawkernel",
            warmup=1,
        )
    raise ValueError(f"unsupported method {method!r}")


def _git_output(args: list[str]) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def _gpu_description() -> str:
    try:
        return _git_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"])
    except Exception as exc:
        return f"unavailable: {exc}"


def run_probe(points: tuple[int, ...], *, warmup: int, repeats: int) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for point_count in points:
        points_a = hd.make_demo_points(point_count, seed=11)
        points_b = hd.make_demo_points(point_count, seed=29, offset=(0.08, -0.06))
        for method in METHODS:
            for warm_index in range(warmup):
                print(f"[goal3026] warmup points={point_count} method={method} iter={warm_index + 1}", flush=True)
                _run_method(points_a, points_b, method)
            samples: list[float] = []
            payloads: list[dict[str, object]] = []
            for repeat_index in range(repeats):
                print(f"[goal3026] run points={point_count} method={method} iter={repeat_index + 1}", flush=True)
                result = _run_method(points_a, points_b, method)
                payload = _result_payload(result)
                elapsed = float(payload["elapsed_sec"])
                samples.append(elapsed)
                payloads.append(payload)
                print(
                    f"[goal3026] done points={point_count} method={method} "
                    f"iter={repeat_index + 1} elapsed={elapsed}",
                    flush=True,
                )
            median_sample = statistics.median(samples)
            selected_index = min(range(len(samples)), key=lambda index: abs(samples[index] - median_sample))
            selected = payloads[selected_index]
            rows.append(
                {
                    "points": point_count,
                    "method": method,
                    "median_elapsed_sec": statistics.median(samples),
                    "min_elapsed_sec": min(samples),
                    "max_elapsed_sec": max(samples),
                    "samples_sec": samples,
                    "distance": float(selected["distance"]),
                    "direction": str(selected["direction"]),
                    "source_index": int(selected["source_index"]),
                    "target_index": int(selected["target_index"]),
                    "rt_core_accelerated": bool(selected.get("rt_core_accelerated", False)),
                    "exact_value": bool(selected.get("exact_value", method.startswith("cupy"))),
                    "threshold_iterations": selected.get("threshold_iterations"),
                    "witness_radius": selected.get("witness_radius"),
                    "radius_strategy": selected.get("radius_strategy"),
                }
            )

    by_key = {(row["points"], row["method"]): row for row in rows}
    ratios: dict[str, float] = {}
    for point_count in points:
        old = float(by_key[(point_count, "rtdl_rt_grouped_adaptive_nearest_witness")]["median_elapsed_sec"])
        raw = float(by_key[(point_count, "rtdl_rt_grouped_adaptive_raw_nearest_witness")]["median_elapsed_sec"])
        cupy = float(by_key[(point_count, "cupy_grouped_grid_rawkernel")]["median_elapsed_sec"])
        ratios[f"raw_vs_old_ratio_{point_count}"] = raw / old
        ratios[f"raw_vs_cupy_ratio_{point_count}"] = raw / cupy

    return {
        "goal": "Goal3026",
        "purpose": "Measure generic point-group nearest-witness raw row-view output for exact Hausdorff adaptive RT path.",
        "source_commit": _git_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": _git_output(["git", "status", "--short"]).splitlines(),
        "gpu": _gpu_description(),
        "cuda_prefix": os.environ.get("CUDA_HOME"),
        "methods": METHODS,
        "warmup": warmup,
        "repeats": repeats,
        "rows": rows,
        "ratios": ratios,
        "promote_raw_row_view_path": all(
            ratios[f"raw_vs_old_ratio_{point_count}"] < 1.0 for point_count in points
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_native_engine_logic_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3026 Hausdorff raw row-view pod probe")
    parser.add_argument("--points", type=int, nargs="+", default=[512, 4096])
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.warmup < 0:
        raise ValueError("warmup must be non-negative")
    if args.repeats <= 0:
        raise ValueError("repeats must be positive")
    payload = run_probe(tuple(args.points), warmup=args.warmup, repeats=args.repeats)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3026] wrote {args.json_out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
