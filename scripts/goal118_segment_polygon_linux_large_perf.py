#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Linux large-scale/PostGIS performance package for segment_polygon_hitcount."
    )
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--perf-iterations", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = rt.run_goal118_segment_polygon_linux_large_perf(
        perf_iterations=args.perf_iterations,
        db_name=args.db_name,
        db_user=args.db_user,
    )
    if args.output_dir:
        artifacts = rt.write_goal118_artifacts(payload, Path(args.output_dir))
        payload["artifacts"] = {key: str(path) for key, path in artifacts.items()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
