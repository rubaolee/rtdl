#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from scripts.goal35_stage_blockgroup_waterbodies_bbox import stage_asset


SEED_BBOX = (-76.701624, 40.495434, -75.757807, 40.9497400000001)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Goal 36 Linux Embree performance characterization on exact-source BlockGroup/WaterBodies bbox slices."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--scale-factors", default="0.4,0.5,0.6,0.75,1.0")
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--gzip", action="store_true")
    parser.add_argument("--response-format", choices=("json",), default="json")
    parser.add_argument("--sleep-sec", type=float, default=0.0)
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--iterations", type=int, default=1)
    return parser.parse_args()


def run_timed(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def benchmark(fn, *args, warmup: int, iterations: int, **kwargs) -> tuple[list[float], object]:
    result = None
    for _ in range(warmup):
        result = fn(*args, **kwargs)
    times: list[float] = []
    for _ in range(iterations):
        result, elapsed = run_timed(fn, *args, **kwargs)
        times.append(elapsed)
    return times, result


def summarize_times(times: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(times),
        "median_sec": statistics.median(times),
        "max_sec": max(times),
        "mean_sec": statistics.fmean(times),
    }


def scale_bbox(
    bbox: tuple[float, float, float, float],
    scale_factor: float,
) -> tuple[float, float, float, float]:
    xmin, ymin, xmax, ymax = bbox
    center_x = (xmin + xmax) / 2.0
    center_y = (ymin + ymax) / 2.0
    half_width = (xmax - xmin) * scale_factor / 2.0
    half_height = (ymax - ymin) * scale_factor / 2.0
    return (
        center_x - half_width,
        center_y - half_height,
        center_x + half_width,
        center_y + half_height,
    )


def bbox_to_string(bbox: tuple[float, float, float, float]) -> str:
    return ",".join(f"{value:.12f}" for value in bbox)


def pair_rows(rows) -> list[tuple[int, int]]:
    return sorted((int(row["left_id"]), int(row["right_id"])) for row in rows)


def pip_rows(rows) -> list[tuple[int, int, int]]:
    return sorted(
        (int(row["point_id"]), int(row["polygon_id"]), int(row["contains"]))
        for row in rows
    )


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Goal 36 Linux BlockGroup/WaterBodies Embree Performance",
        "",
        f"Host label: `{summary['host_label']}`",
        "",
        "## Setup",
        "",
        f"- seed bbox label: `{summary['seed_bbox_label']}`",
        f"- seed bbox: `{summary['seed_bbox']}`",
        f"- warmup: `{summary['warmup']}`",
        f"- iterations: `{summary['iterations']}`",
        "",
        "## Accepted Points",
        "",
        "| Slice | BlockGroup Features | WaterBodies Features | LSI Parity | LSI CPU Median (s) | LSI Embree Median (s) | LSI Speedup | PIP Parity | PIP CPU Median (s) | PIP Embree Median (s) | PIP Speedup |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]

    accepted = summary["accepted_points"]
    for point in accepted:
        lines.append(
            "| `{slice_label}` | `{blockgroup_features}` | `{water_features}` | `{lsi_pair_parity}` | `{lsi_cpu:.9f}` | `{lsi_embree:.9f}` | `{lsi_speedup:.2f}x` | `{pip_row_parity}` | `{pip_cpu:.9f}` | `{pip_embree:.9f}` | `{pip_speedup:.2f}x` |".format(
                slice_label=point["slice_label"],
                blockgroup_features=point["blockgroup"]["feature_count"],
                water_features=point["waterbodies"]["feature_count"],
                lsi_pair_parity=point["lsi"]["pair_parity"],
                lsi_cpu=point["lsi"]["cpu_times"]["median_sec"],
                lsi_embree=point["lsi"]["embree_times"]["median_sec"],
                lsi_speedup=point["lsi"]["cpu_times"]["median_sec"] / point["lsi"]["embree_times"]["median_sec"],
                pip_row_parity=point["pip"]["row_parity"],
                pip_cpu=point["pip"]["cpu_times"]["median_sec"],
                pip_embree=point["pip"]["embree_times"]["median_sec"],
                pip_speedup=point["pip"]["cpu_times"]["median_sec"] / point["pip"]["embree_times"]["median_sec"],
            )
        )

    rejected = summary["rejected_points"]
    lines.extend(["", "## Rejected Points", ""])
    if not rejected:
        lines.append("- none")
    else:
        for point in rejected:
            lines.append(
                "- `{}` rejected: `lsi_pair_parity={}`, `pip_row_parity={}`".format(
                    point["slice_label"],
                    point["lsi"]["pair_parity"],
                    point["pip"]["row_parity"],
                )
            )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- accepted points are exact-source regional slices derived from a frozen seed bbox and scale factors",
            "- this is Linux-host Embree characterization for `BlockGroup ⊲⊳ WaterBodies`, not nationwide/full-family reproduction",
            "- single measured pass per point is intentional because the Python `lsi` oracle is already minutes-long at the top accepted scale",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets = {asset.asset_id: asset for asset in rt.rayjoin_feature_service_layers()}
    blockgroup_asset = assets["blockgroup_feature_layer"]
    waterbodies_asset = assets["waterbodies_feature_layer"]

    accepted_points = []
    rejected_points = []
    scale_factors = [float(part) for part in args.scale_factors.split(",") if part.strip()]

    for scale_factor in scale_factors:
        bbox = scale_bbox(SEED_BBOX, scale_factor)
        bbox_label = f"county2300_s{str(scale_factor).replace('.', '')}"
        slice_dir = output_dir / bbox_label
        slice_dir.mkdir(parents=True, exist_ok=True)
        bbox_string = bbox_to_string(bbox)

        blockgroup_manifest = stage_asset(
            blockgroup_asset,
            output_dir=slice_dir,
            bbox=bbox_string,
            page_size=args.page_size,
            use_gzip=args.gzip,
            response_format=args.response_format,
            sleep_sec=args.sleep_sec,
        )
        waterbodies_manifest = stage_asset(
            waterbodies_asset,
            output_dir=slice_dir,
            bbox=bbox_string,
            page_size=args.page_size,
            use_gzip=args.gzip,
            response_format=args.response_format,
            sleep_sec=args.sleep_sec,
        )

        blockgroup = rt.arcgis_pages_to_cdb(
            slice_dir / "blockgroup_feature_layer",
            name=f"{bbox_label}_blockgroup",
            ignore_invalid_tail=True,
        )
        waterbodies = rt.arcgis_pages_to_cdb(
            slice_dir / "waterbodies_feature_layer",
            name=f"{bbox_label}_waterbodies",
            ignore_invalid_tail=True,
        )

        blockgroup_segments = rt.chains_to_segments(blockgroup)
        water_segments = rt.chains_to_segments(waterbodies)
        blockgroup_polygons = rt.chains_to_polygons(blockgroup)
        water_points = rt.chains_to_probe_points(waterbodies)

        lsi_cpu_times, lsi_cpu_rows = benchmark(
            rt.run_cpu,
            county_zip_join_reference,
            left=water_segments,
            right=blockgroup_segments,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        lsi_embree_times, lsi_embree_rows = benchmark(
            rt.run_embree,
            county_zip_join_reference,
            left=water_segments,
            right=blockgroup_segments,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        pip_cpu_times, pip_cpu_rows = benchmark(
            rt.run_cpu,
            point_in_counties_reference,
            points=water_points,
            polygons=blockgroup_polygons,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        pip_embree_times, pip_embree_rows = benchmark(
            rt.run_embree,
            point_in_counties_reference,
            points=water_points,
            polygons=blockgroup_polygons,
            warmup=args.warmup,
            iterations=args.iterations,
        )

        point = {
            "slice_label": bbox_label,
            "scale_factor": scale_factor,
            "bbox": bbox,
            "blockgroup": {
                "service_feature_count": blockgroup_manifest["expected_feature_count"],
                "feature_count": len(blockgroup.face_ids()),
                "chain_count": len(blockgroup.chains),
            },
            "waterbodies": {
                "service_feature_count": waterbodies_manifest["expected_feature_count"],
                "feature_count": len(waterbodies.face_ids()),
                "chain_count": len(waterbodies.chains),
            },
            "lsi": {
                "cpu_row_count": len(lsi_cpu_rows),
                "embree_row_count": len(lsi_embree_rows),
                "pair_parity": pair_rows(lsi_cpu_rows) == pair_rows(lsi_embree_rows),
                "cpu_times": summarize_times(lsi_cpu_times),
                "embree_times": summarize_times(lsi_embree_times),
            },
            "pip": {
                "cpu_row_count": len(pip_cpu_rows),
                "embree_row_count": len(pip_embree_rows),
                "row_parity": pip_rows(pip_cpu_rows) == pip_rows(pip_embree_rows),
                "cpu_times": summarize_times(pip_cpu_times),
                "embree_times": summarize_times(pip_embree_times),
            },
        }
        if point["lsi"]["pair_parity"] and point["pip"]["row_parity"]:
            accepted_points.append(point)
        else:
            rejected_points.append(point)

    summary = {
        "host_label": args.host_label,
        "seed_bbox_label": "county2300_bbox",
        "seed_bbox": SEED_BBOX,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "accepted_points": accepted_points,
        "rejected_points": rejected_points,
    }

    (output_dir / "goal36_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "goal36_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
