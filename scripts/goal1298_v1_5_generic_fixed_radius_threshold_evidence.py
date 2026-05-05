from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def _source_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def make_fixed_radius_case(copies: int) -> dict[str, tuple[rt.Point, ...]]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    query_points = []
    search_points = []
    for copy_index in range(copies):
        offset = float(copy_index * 10)
        id_offset = copy_index * 10
        query_points.extend(
            (
                rt.Point(id=id_offset + 1, x=offset + 0.0, y=0.0),
                rt.Point(id=id_offset + 2, x=offset + 5.0, y=0.0),
            )
        )
        search_points.extend(
            (
                rt.Point(id=id_offset + 100, x=offset + 0.0, y=0.0),
                rt.Point(id=id_offset + 101, x=offset + 0.5, y=0.0),
            )
        )
    return {
        "query_points": tuple(query_points),
        "search_points": tuple(search_points),
    }


def run_evidence(*, copies: int, radius: float, threshold: int, backends: tuple[str, ...]) -> dict[str, Any]:
    case = make_fixed_radius_case(copies)
    payload: dict[str, Any] = {
        "goal": "Goal1298 v1.5 generic fixed-radius threshold-count evidence",
        "source_commit": _source_commit(),
        "copies": copies,
        "radius": radius,
        "threshold": threshold,
        "query_count": len(case["query_points"]),
        "search_count": len(case["search_points"]),
        "expected_threshold_reached_count": copies,
        "results": {},
        "parity": {},
        "boundary": (
            "Generic 2-D fixed-radius count-threshold primitive only; no app-specific ANN, "
            "DBSCAN, coverage, Hausdorff, Barnes-Hut, whole-app, or public speedup claim."
        ),
    }

    cpu_result = None
    if "cpu" in backends:
        cpu_result = rt.run_generic_fixed_radius_count_threshold_2d(
            case["query_points"],
            case["search_points"],
            radius=radius,
            threshold=threshold,
            backend="cpu",
        )
        payload["results"]["cpu_direct"] = cpu_result
        payload["parity"]["cpu_matches_expected"] = (
            int(cpu_result["threshold_reached_count"]) == payload["expected_threshold_reached_count"]
        )

    for backend in backends:
        if backend == "cpu":
            continue
        direct_start = time.perf_counter()
        direct_result = rt.run_generic_fixed_radius_count_threshold_2d(
            case["query_points"],
            case["search_points"],
            radius=radius,
            threshold=threshold,
            backend=backend,
        )
        direct_wall_sec = time.perf_counter() - direct_start
        payload["results"][f"{backend}_direct"] = direct_result
        payload["results"][f"{backend}_direct"]["run_phases"]["wall_sec"] = direct_wall_sec
        payload["parity"][f"{backend}_direct_matches_expected"] = (
            int(direct_result["threshold_reached_count"]) == payload["expected_threshold_reached_count"]
        )
        if cpu_result is not None:
            payload["parity"][f"{backend}_direct_matches_cpu_rows"] = (
                tuple(direct_result["rows"]) == tuple(cpu_result["rows"])
            )

        prepare_kwargs = {"max_radius": radius} if backend == "optix" else {}
        prepared_start = time.perf_counter()
        with rt.prepare_generic_fixed_radius_count_threshold_2d(
            search_points=case["search_points"],
            backend=backend,
            **prepare_kwargs,
        ) as prepared:
            prepared_scalar = prepared.count_threshold_reached(
                case["query_points"],
                radius=radius,
                threshold=threshold,
            )
            prepared_rows = prepared.run(
                case["query_points"],
                radius=radius,
                threshold=threshold,
            )
        prepared_wall_sec = time.perf_counter() - prepared_start
        payload["results"][f"{backend}_prepared_scalar"] = prepared_scalar
        payload["results"][f"{backend}_prepared_rows"] = prepared_rows
        payload["results"][f"{backend}_prepared_scalar"]["run_phases"]["wall_sec"] = prepared_wall_sec
        payload["parity"][f"{backend}_prepared_scalar_matches_expected"] = (
            int(prepared_scalar["threshold_reached_count"]) == payload["expected_threshold_reached_count"]
        )
        payload["parity"][f"{backend}_prepared_rows_matches_expected"] = (
            int(prepared_rows["threshold_reached_count"]) == payload["expected_threshold_reached_count"]
        )
        payload["parity"][f"{backend}_prepared_rows_match_direct"] = (
            tuple(prepared_rows["rows"]) == tuple(direct_result["rows"])
        )

    payload["all_parity_checks_passed"] = all(bool(value) for value in payload["parity"].values())
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copies", type=int, default=512)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--threshold", type=int, default=2)
    parser.add_argument(
        "--backends",
        nargs="+",
        default=("cpu", "embree", "optix"),
        choices=("cpu", "embree", "optix"),
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    payload = run_evidence(
        copies=args.copies,
        radius=args.radius,
        threshold=args.threshold,
        backends=tuple(args.backends),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "all_parity_checks_passed": payload["all_parity_checks_passed"]}))
    return 0 if payload["all_parity_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
