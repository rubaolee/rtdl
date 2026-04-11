from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.goal228_v0_4_nearest_neighbor_perf import default_postgis_dsn
from rtdsl.goal228_v0_4_nearest_neighbor_perf import run_heavy_benchmark
from rtdsl.goal228_v0_4_nearest_neighbor_perf import write_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Heavy Linux v0.4 nearest-neighbor benchmark across cpu, embree, optix, vulkan, and indexed PostGIS."
    )
    parser.add_argument(
        "--dataset-path",
        default=str(ROOT / "build" / "datasets" / "natural_earth_populated_places_full.geojson"),
    )
    parser.add_argument("--min-seconds", type=float, default=10.0)
    parser.add_argument("--fixed-radius-copies", type=int, default=16)
    parser.add_argument("--fixed-radius-query-stride", type=int, default=4)
    parser.add_argument("--knn-copies", type=int, default=1)
    parser.add_argument("--knn-query-stride", type=int, default=16)
    parser.add_argument("--postgis-dsn", default=default_postgis_dsn())
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "build" / "goal228_v0_4_nearest_neighbor_perf"),
    )
    args = parser.parse_args(argv)

    payload = run_heavy_benchmark(
        dataset_path=args.dataset_path,
        min_seconds=args.min_seconds,
        postgis_dsn=args.postgis_dsn,
        fixed_radius_copies=args.fixed_radius_copies,
        fixed_radius_query_stride=args.fixed_radius_query_stride,
        knn_copies=args.knn_copies,
        knn_query_stride=args.knn_query_stride,
    )
    json_path, md_path = write_outputs(payload, args.output_dir)
    print(
        json.dumps(
            {
                "json": str(json_path),
                "markdown": str(md_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
