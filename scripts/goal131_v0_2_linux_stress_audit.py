#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("at least one copy count is required")
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the v0.2 Linux large-scale stress audit for hitcount and anyhit workloads."
    )
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--perf-iterations", type=int, default=3)
    parser.add_argument("--copies", default="64,256,512,1024,2048,4096")
    parser.add_argument("--prepared-copies", default="64,256")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copies = _parse_int_list(args.copies)
    prepared_copies = _parse_int_list(args.prepared_copies)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    hitcount = rt.run_goal118_segment_polygon_linux_large_perf(
        copies=copies,
        prepared_copies=prepared_copies,
        perf_iterations=args.perf_iterations,
        db_name=args.db_name,
        db_user=args.db_user,
    )
    anyhit = rt.run_goal128_segment_polygon_anyhit_linux_large_perf(
        copies=copies,
        prepared_copies=prepared_copies,
        perf_iterations=args.perf_iterations,
        db_name=args.db_name,
        db_user=args.db_user,
    )

    rt.write_goal118_artifacts(hitcount, output_root / "hitcount")
    rt.write_goal128_linux_artifacts(anyhit, output_root / "anyhit")

    payload = {
        "suite": "goal131_v0_2_linux_stress_audit",
        "copies": copies,
        "prepared_copies": prepared_copies,
        "perf_iterations": args.perf_iterations,
        "hitcount": hitcount,
        "anyhit": anyhit,
    }
    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
