from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded KITTI three-way scaling sweep across RTDL, PostGIS, and cuNSearch."
    )
    parser.add_argument("source_root")
    parser.add_argument("cunsearch_source_root")
    parser.add_argument("cunsearch_build_root")
    parser.add_argument("postgis_dsn")
    parser.add_argument(
        "--point-counts",
        default="512,1024",
        help="Comma-separated max_total_points values to sweep.",
    )
    parser.add_argument("--output-dir", default="build/goal284_kitti_three_way_scaling_sweep")
    parser.add_argument("--query-start-index", type=int, default=0)
    parser.add_argument("--search-start-index", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=1)
    parser.add_argument("--radius", type=float, default=1.0)
    parser.add_argument("--k-max", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    return parser.parse_args()


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sizes = tuple(int(item.strip()) for item in args.point_counts.split(",") if item.strip())
    if not sizes:
        raise ValueError("point-counts must contain at least one positive integer")

    runs = []
    for point_count in sizes:
        run_dir = output_dir / f"points_{point_count}"
        run_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            "scripts/goal283_kitti_three_way_performance.py",
            args.source_root,
            args.cunsearch_source_root,
            args.cunsearch_build_root,
            args.postgis_dsn,
            "--output-dir",
            str(run_dir),
            "--query-start-index",
            str(args.query_start_index),
            "--search-start-index",
            str(args.search_start_index),
            "--max-frames",
            str(args.max_frames),
            "--max-points-per-frame",
            str(point_count),
            "--max-total-points",
            str(point_count),
            "--radius",
            str(args.radius),
            "--k-max",
            str(args.k_max),
            "--repeats",
            str(args.repeats),
        ]
        subprocess.run(cmd, check=True)

        report = json.loads((run_dir / "three_way_report.json").read_text(encoding="utf-8"))
        query_points = rt.load_kitti_bounded_point_package(run_dir / "query_points.json").points
        search_points = rt.load_kitti_bounded_point_package(run_dir / "search_points.json").points
        reference_rows = tuple(
            rt.fixed_radius_neighbors_cpu(
                query_points,
                search_points,
                radius=args.radius,
                k_max=args.k_max,
            )
        )
        candidate_rows = tuple(rt.load_cunsearch_fixed_radius_response(run_dir / "response.json").rows)
        mismatch = rt.summarize_fixed_radius_mismatch(
            reference_rows,
            candidate_rows,
            strict_parity_ok=bool(report["cunsearch"]["parity_ok"]),
        )
        report["cunsearch"]["mismatch_summary"] = {
            "strict_parity_ok": mismatch.strict_parity_ok,
            "reference_row_count": mismatch.reference_row_count,
            "candidate_row_count": mismatch.candidate_row_count,
            "missing_pair_count": mismatch.missing_pair_count,
            "extra_pair_count": mismatch.extra_pair_count,
            "first_missing_pair": list(mismatch.first_missing_pair) if mismatch.first_missing_pair else None,
            "first_extra_pair": list(mismatch.first_extra_pair) if mismatch.first_extra_pair else None,
            "first_reference_row": mismatch.first_reference_row,
            "first_candidate_row": mismatch.first_candidate_row,
        }
        (run_dir / "three_way_report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        runs.append(
            {
                "point_count": point_count,
                "reference_median_sec": _median(report["reference"]["times_sec"]),
                "postgis_median_sec": _median(report["postgis"]["times_sec"]),
                "postgis_parity_ok": bool(report["postgis"]["parity_ok"]),
                "cunsearch_median_sec": _median(report["cunsearch"]["times_sec"]),
                "cunsearch_parity_ok": bool(report["cunsearch"]["parity_ok"]),
                "cunsearch_mismatch_summary": report["cunsearch"]["mismatch_summary"],
                "row_count": int(report["reference"]["row_count"]),
            }
        )

    payload = {
        "report_kind": "goal284_kitti_three_way_scaling_sweep_v1",
        "source_root": str(Path(args.source_root).expanduser().resolve()),
        "radius": args.radius,
        "k_max": args.k_max,
        "repeats": args.repeats,
        "point_counts": list(sizes),
        "runs": runs,
    }
    summary_path = output_dir / "scaling_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(summary_path)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
