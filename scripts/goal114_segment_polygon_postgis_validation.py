#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run large-scale segment_polygon_hitcount validation against PostGIS."
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=64,
        help="Number of deterministic county-fixture tiles to use.",
    )
    parser.add_argument(
        "--backends",
        default="cpu,embree,optix",
        help="Comma-separated RTDL backends to validate: cpu,embree,optix,vulkan",
    )
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset = rt.segment_polygon_large_dataset_name(copies=args.copies)
    backends = tuple(part.strip() for part in args.backends.split(",") if part.strip())
    payload = rt.run_goal114_segment_polygon_postgis_validation(
        dataset=dataset,
        backends=backends,
        db_name=args.db_name,
        db_user=args.db_user,
    )
    if args.output_dir:
        artifacts = rt.write_goal114_artifacts(payload, Path(args.output_dir))
        payload["artifacts"] = {key: str(path) for key, path in artifacts.items()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
