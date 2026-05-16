from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from examples import rtdl_hausdorff_v2_function as hd


METHODS = (
    "openmp_cpu",
    "cuda_cpp",
    "cupy_rawkernel",
    "rtdl_v2_user_cuda",
    "rtdl_rt_threshold_search",
    "rtdl_rt_nearest_witness",
    "rtdl_rt_nearest_witness_oracle_radius",
)


METHOD_METADATA = {
    "openmp_cpu": {
        "role": "baseline",
        "uses_rtdl": False,
        "uses_partner": False,
        "uses_rt_cores": False,
        "exact_value": True,
        "notes": "multi-threaded C++/OpenMP double loop",
    },
    "cuda_cpp": {
        "role": "baseline",
        "uses_rtdl": False,
        "uses_partner": False,
        "uses_rt_cores": False,
        "exact_value": True,
        "notes": "standalone CUDA C++ tiled double loop",
    },
    "cupy_rawkernel": {
        "role": "baseline",
        "uses_rtdl": False,
        "uses_partner": True,
        "uses_rt_cores": False,
        "exact_value": True,
        "notes": "CuPy RawKernel exact nearest-neighbor continuation",
    },
    "rtdl_v2_user_cuda": {
        "role": "rtdl_v2_language",
        "uses_rtdl": True,
        "uses_partner": True,
        "uses_rt_cores": False,
        "exact_value": True,
        "notes": "RTDL converts rows to partner columns; CuPy continuation computes exact HD",
    },
    "rtdl_rt_threshold_search": {
        "role": "rtdl_v2_language",
        "uses_rtdl": True,
        "uses_partner": False,
        "uses_rt_cores": True,
        "exact_value": False,
        "notes": "OptiX fixed-radius decision search returns a tolerance-bounded interval",
    },
    "rtdl_rt_nearest_witness": {
        "role": "rtdl_v2_language",
        "uses_rtdl": True,
        "uses_partner": False,
        "uses_rt_cores": True,
        "exact_value": True,
        "notes": "OptiX nearest-witness traversal seeded by threshold-search upper bound",
    },
    "rtdl_rt_nearest_witness_oracle_radius": {
        "role": "diagnostic_lower_bound",
        "uses_rtdl": True,
        "uses_partner": False,
        "uses_rt_cores": True,
        "exact_value": True,
        "notes": "OptiX nearest-witness traversal using exact-reference radius plus slack; diagnostic only",
    },
}


def _run_method(method: str, points_a, points_b, args, exact_reference: dict[str, object] | None) -> dict[str, object]:
    start = time.perf_counter()
    try:
        if method == "rtdl_rt_threshold_search":
            result = hd.hausdorff_distance_2d_rt_threshold_search(
                points_a,
                points_b,
                backend=args.rt_backend,
                tolerance=args.rt_tolerance,
                max_iterations=args.rt_max_iterations,
            )
            payload = asdict(result)
            payload["distance_for_compare"] = result.distance_upper_bound
        elif method == "rtdl_rt_nearest_witness":
            result = hd.hausdorff_distance_2d_rt_nearest_witness(
                points_a,
                points_b,
                backend=args.rt_backend,
                radius=args.rt_nearest_radius,
                seed_with_threshold=not args.rt_nearest_no_threshold_seed,
                threshold_tolerance=args.rt_tolerance,
                threshold_max_iterations=args.rt_max_iterations,
            )
            payload = asdict(result)
            payload["distance_for_compare"] = result.distance
        elif method == "rtdl_rt_nearest_witness_oracle_radius":
            if args.rt_nearest_radius is not None:
                oracle_radius = float(args.rt_nearest_radius)
                radius_source = "explicit_radius"
            else:
                if exact_reference is None:
                    raise RuntimeError(
                        "rtdl_rt_nearest_witness_oracle_radius requires an earlier exact reference method "
                        "or --rt-nearest-radius"
                    )
                oracle_radius = float(exact_reference["distance"]) + float(args.oracle_radius_slack)
                radius_source = "exact_reference_plus_slack"
            result = hd.hausdorff_distance_2d_rt_nearest_witness(
                points_a,
                points_b,
                backend=args.rt_backend,
                radius=oracle_radius,
                seed_with_threshold=False,
                threshold_tolerance=args.rt_tolerance,
                threshold_max_iterations=args.rt_max_iterations,
            )
            payload = asdict(result)
            payload["base_method"] = result.method
            payload["method"] = "rtdl_rt_nearest_witness_oracle_radius"
            payload["distance_for_compare"] = result.distance
            payload["oracle_radius"] = oracle_radius
            payload["oracle_radius_source"] = radius_source
        else:
            result = hd.hausdorff_distance_2d(points_a, points_b, method=method, warmup=args.warmup)
            payload = asdict(result)
            payload["distance_for_compare"] = result.distance
        payload["ok"] = True
    except Exception as exc:
        payload = {"ok": False, "error": repr(exc), "elapsed_sec": time.perf_counter() - start}
    payload["metadata"] = METHOD_METADATA[method]
    return payload


def run_lab(args) -> dict[str, object]:
    points_a = hd.make_demo_points(args.points_a, seed=args.seed_a)
    points_b = hd.make_demo_points(args.points_b, seed=args.seed_b, offset=(args.offset_x, args.offset_y))
    methods = tuple(args.methods or METHODS)
    results = {}
    exact_reference = None
    for method in methods:
        print(f"[hausdorff-lab] running {method} for {args.points_a}x{args.points_b}", flush=True)
        result = _run_method(method, points_a, points_b, args, exact_reference)
        results[method] = result
        if result.get("ok") and METHOD_METADATA[method]["exact_value"] and exact_reference is None:
            exact_reference = {
                "method": method,
                "distance": float(result["distance_for_compare"]),
                "direction": result.get("direction"),
                "source_index": result.get("source_index"),
                "target_index": result.get("target_index"),
            }
    if exact_reference is not None:
        for method, result in results.items():
            if not result.get("ok"):
                continue
            tolerance = args.rt_tolerance if not METHOD_METADATA[method]["exact_value"] else args.exact_tolerance
            result["matches_exact_reference"] = math.isclose(
                float(result["distance_for_compare"]),
                float(exact_reference["distance"]),
                rel_tol=tolerance,
                abs_tol=tolerance,
            )
    return {
        "scenario": {
            "methods": list(methods),
            "points_a": args.points_a,
            "points_b": args.points_b,
            "seed_a": args.seed_a,
            "seed_b": args.seed_b,
            "offset_x": args.offset_x,
            "offset_y": args.offset_y,
            "rt_backend": args.rt_backend,
            "rt_tolerance": args.rt_tolerance,
            "rt_nearest_seed_strategy": "bbox_upper_bound" if args.rt_nearest_no_threshold_seed else "rt_threshold_upper_bound",
            "oracle_radius_slack": args.oracle_radius_slack,
        },
        "exact_reference": exact_reference,
        "results": results,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL v2.0 Hausdorff language-level comparison lab.")
    parser.add_argument("--points-a", type=int, default=2048)
    parser.add_argument("--points-b", type=int, default=2048)
    parser.add_argument("--seed-a", type=int, default=11)
    parser.add_argument("--seed-b", type=int, default=29)
    parser.add_argument("--offset-x", type=float, default=0.08)
    parser.add_argument("--offset-y", type=float, default=-0.06)
    parser.add_argument("--method", dest="methods", action="append", choices=METHODS)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--rt-backend", choices=("optix",), default="optix")
    parser.add_argument("--rt-tolerance", type=float, default=1e-4)
    parser.add_argument("--rt-max-iterations", type=int, default=32)
    parser.add_argument("--rt-nearest-radius", type=float, default=None)
    parser.add_argument("--rt-nearest-no-threshold-seed", action="store_true")
    parser.add_argument(
        "--oracle-radius-slack",
        type=float,
        default=1e-7,
        help="extra radius added to the exact reference for the oracle-radius RT diagnostic",
    )
    parser.add_argument("--exact-tolerance", type=float, default=1e-9)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = run_lab(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
