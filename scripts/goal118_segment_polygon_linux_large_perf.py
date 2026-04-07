#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt
from rtdsl.goal118_segment_polygon_linux_large_perf import LARGE_COPIES
from rtdsl.goal118_segment_polygon_linux_large_perf import PREPARED_COPIES


def _parse_int_list(raw: str | None) -> tuple[int, ...] | None:
    if raw is None:
        return None
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    return values or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Linux large-scale/PostGIS performance package for segment_polygon_hitcount."
    )
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--perf-iterations", type=int, default=3)
    parser.add_argument(
        "--copies",
        default=None,
        help="Comma-separated dataset copy counts to validate, e.g. 64,256,1024,2048",
    )
    parser.add_argument(
        "--prepared-copies",
        default=None,
        help="Comma-separated dataset copy counts to measure prepared reuse on.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copies = _parse_int_list(args.copies)
    prepared_copies = _parse_int_list(args.prepared_copies)
    payload = rt.run_goal118_segment_polygon_linux_large_perf(
        copies=copies if copies is not None else LARGE_COPIES,
        prepared_copies=prepared_copies if prepared_copies is not None else PREPARED_COPIES,
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
