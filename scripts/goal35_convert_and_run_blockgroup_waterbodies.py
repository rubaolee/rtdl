#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def summarize_lsi(cpu_rows, embree_rows, cpu_sec: float, embree_sec: float) -> dict[str, object]:
    cpu_pairs = sorted((row["left_id"], row["right_id"]) for row in cpu_rows)
    embree_pairs = sorted((row["left_id"], row["right_id"]) for row in embree_rows)
    return {
        "cpu_row_count": len(cpu_rows),
        "embree_row_count": len(embree_rows),
        "cpu_sec": cpu_sec,
        "embree_sec": embree_sec,
        "pair_parity": cpu_pairs == embree_pairs,
        "sample_cpu_pairs": cpu_pairs[:10],
        "sample_embree_pairs": embree_pairs[:10],
    }


def summarize_pip(cpu_rows, embree_rows, cpu_sec: float, embree_sec: float) -> dict[str, object]:
    cpu_triplets = sorted((row["point_id"], row["polygon_id"], row["contains"]) for row in cpu_rows)
    embree_triplets = sorted((row["point_id"], row["polygon_id"], row["contains"]) for row in embree_rows)
    return {
        "cpu_row_count": len(cpu_rows),
        "embree_row_count": len(embree_rows),
        "cpu_sec": cpu_sec,
        "embree_sec": embree_sec,
        "row_parity": cpu_triplets == embree_triplets,
        "sample_cpu_rows": cpu_triplets[:10],
        "sample_embree_rows": embree_triplets[:10],
    }


def render_markdown(summary: dict[str, object]) -> str:
    lsi = summary["lsi"]
    pip = summary["pip"]
    lines = [
        "# Goal 35 BlockGroup/WaterBodies Exact-Source Linux Slice",
        "",
        f"Host label: `{summary['host_label']}`",
        f"BBox label: `{summary['bbox_label']}`",
        f"BBox: `{summary['bbox']}`",
        "",
        "## Converted Inputs",
        "",
        f"- blockgroup pages loaded: `{summary['blockgroup']['page_count']}`",
        f"- blockgroup features: `{summary['blockgroup']['feature_count']}`",
        f"- blockgroup chains: `{summary['blockgroup']['chain_count']}`",
        f"- waterbodies pages loaded: `{summary['waterbodies']['page_count']}`",
        f"- waterbodies features: `{summary['waterbodies']['feature_count']}`",
        f"- waterbodies chains: `{summary['waterbodies']['chain_count']}`",
        "",
        "## LSI",
        "",
        f"- cpu rows: `{lsi['cpu_row_count']}`",
        f"- embree rows: `{lsi['embree_row_count']}`",
        f"- cpu sec: `{lsi['cpu_sec']:.9f}`",
        f"- embree sec: `{lsi['embree_sec']:.9f}`",
        f"- pair parity: `{lsi['pair_parity']}`",
        "",
        "## PIP",
        "",
        f"- cpu rows: `{pip['cpu_row_count']}`",
        f"- embree rows: `{pip['embree_row_count']}`",
        f"- cpu sec: `{pip['cpu_sec']:.9f}`",
        f"- embree sec: `{pip['embree_sec']:.9f}`",
        f"- row parity: `{pip['row_parity']}`",
        "",
        "## Boundary",
        "",
        "- this is an exact-source regional slice selected by a frozen bbox, not a nationwide run",
        "- blockgroup and waterbodies inputs are both fetched from live ArcGIS FeatureServer sources",
        "- the current report closes the first Linux exact-source BlockGroup/WaterBodies execution slice",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert and run Goal 35 BlockGroup/WaterBodies exact-source bbox slice.")
    parser.add_argument("--blockgroup-dir", required=True)
    parser.add_argument("--waterbodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bbox", required=True)
    parser.add_argument("--bbox-label", default="custom")
    parser.add_argument("--host-label", default="unknown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    blockgroup = rt.arcgis_pages_to_cdb(args.blockgroup_dir, name="blockgroup_slice", ignore_invalid_tail=True)
    waterbodies = rt.arcgis_pages_to_cdb(args.waterbodies_dir, name="waterbodies_slice", ignore_invalid_tail=True)

    rt.write_cdb(blockgroup, output_dir / "blockgroup_slice.cdb")
    rt.write_cdb(waterbodies, output_dir / "waterbodies_slice.cdb")

    blockgroup_segments = rt.chains_to_segments(blockgroup)
    water_segments = rt.chains_to_segments(waterbodies)
    blockgroup_polygons = rt.chains_to_polygons(blockgroup)
    water_points = rt.chains_to_probe_points(waterbodies)

    lsi_cpu_rows, lsi_cpu_sec = time_call(rt.run_cpu, county_zip_join_reference, left=water_segments, right=blockgroup_segments)
    lsi_embree_rows, lsi_embree_sec = time_call(rt.run_embree, county_zip_join_reference, left=water_segments, right=blockgroup_segments)
    pip_cpu_rows, pip_cpu_sec = time_call(rt.run_cpu, point_in_counties_reference, points=water_points, polygons=blockgroup_polygons)
    pip_embree_rows, pip_embree_sec = time_call(rt.run_embree, point_in_counties_reference, points=water_points, polygons=blockgroup_polygons)

    summary = {
        "host_label": args.host_label,
        "bbox_label": args.bbox_label,
        "bbox": args.bbox,
        "blockgroup": {
            "page_count": rt.count_arcgis_loaded_pages(args.blockgroup_dir, ignore_invalid_tail=True),
            "feature_count": len(blockgroup.face_ids()),
            "chain_count": len(blockgroup.chains),
        },
        "waterbodies": {
            "page_count": rt.count_arcgis_loaded_pages(args.waterbodies_dir, ignore_invalid_tail=True),
            "feature_count": len(waterbodies.face_ids()),
            "chain_count": len(waterbodies.chains),
        },
        "lsi": summarize_lsi(lsi_cpu_rows, lsi_embree_rows, lsi_cpu_sec, lsi_embree_sec),
        "pip": summarize_pip(pip_cpu_rows, pip_embree_rows, pip_cpu_sec, pip_embree_sec),
    }
    (output_dir / "goal35_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal35_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
