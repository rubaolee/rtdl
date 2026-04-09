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
    cpu_pairs = sorted((int(row["left_id"]), int(row["right_id"])) for row in cpu_rows)
    embree_pairs = sorted((int(row["left_id"]), int(row["right_id"])) for row in embree_rows)
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
    cpu_triplets = sorted((int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in cpu_rows)
    embree_triplets = sorted(
        (int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in embree_rows
    )
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
    lakes = summary["lakes"]
    parks = summary["parks"]
    lsi = summary["lsi"]
    pip = summary["pip"]
    lines = [
        "# Goal 37 LKAU PKAU Exact-Source-Derived Linux Slice",
        "",
        f"Host label: `{summary['host_label']}`",
        f"BBox label: `{summary['bbox_label']}`",
        f"BBox: `{summary['bbox']}`",
        "",
        "## Converted Inputs",
        "",
        f"- lakes source elements: `{lakes['element_count']}`",
        f"- lakes closed ways: `{lakes['closed_way_count']}`",
        f"- lakes converted features: `{lakes['feature_count']}`",
        f"- lakes chains: `{lakes['chain_count']}`",
        f"- parks source elements: `{parks['element_count']}`",
        f"- parks closed ways: `{parks['closed_way_count']}`",
        f"- parks converted features: `{parks['feature_count']}`",
        f"- parks chains: `{parks['chain_count']}`",
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
        "- this is a bounded Australia regional slice derived from live OSM Overpass data, not a continent-scale download",
        "- the current path uses closed OSM ways only and does not yet reconstruct multipolygon relations",
        "- this closes the first real `LKAU ⊲⊳ PKAU` Embree slice, not the whole Lakes/Parks family matrix",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert and run Goal 37 LKAU/PKAU bounded Linux slice.")
    parser.add_argument("--lakes-json", required=True)
    parser.add_argument("--parks-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bbox", required=True)
    parser.add_argument("--bbox-label", default="custom")
    parser.add_argument("--host-label", default="unknown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lakes_elements = rt.load_overpass_elements(args.lakes_json)
    parks_elements = rt.load_overpass_elements(args.parks_json)
    lakes_stats = rt.overpass_elements_stats(lakes_elements)
    parks_stats = rt.overpass_elements_stats(parks_elements)
    lakes = rt.overpass_elements_to_cdb(lakes_elements, name="lkau_slice")
    parks = rt.overpass_elements_to_cdb(parks_elements, name="pkau_slice")

    rt.write_cdb(lakes, output_dir / "lkau_slice.cdb")
    rt.write_cdb(parks, output_dir / "pkau_slice.cdb")

    lake_segments = rt.chains_to_segments(lakes)
    park_segments = rt.chains_to_segments(parks)
    park_polygons = rt.chains_to_polygons(parks)
    lake_points = rt.chains_to_probe_points(lakes)

    lsi_cpu_rows, lsi_cpu_sec = time_call(
        rt.run_cpu,
        county_zip_join_reference,
        left=lake_segments,
        right=park_segments,
    )
    lsi_embree_rows, lsi_embree_sec = time_call(
        rt.run_embree,
        county_zip_join_reference,
        left=lake_segments,
        right=park_segments,
    )
    pip_cpu_rows, pip_cpu_sec = time_call(
        rt.run_cpu,
        point_in_counties_reference,
        points=lake_points,
        polygons=park_polygons,
    )
    pip_embree_rows, pip_embree_sec = time_call(
        rt.run_embree,
        point_in_counties_reference,
        points=lake_points,
        polygons=park_polygons,
    )

    summary = {
        "host_label": args.host_label,
        "bbox_label": args.bbox_label,
        "bbox": args.bbox,
        "lakes": {
            "element_count": lakes_stats.element_count,
            "polygon_like_count": lakes_stats.polygon_like_count,
            "closed_way_count": lakes_stats.closed_way_count,
            "skipped_non_way_count": lakes_stats.skipped_non_way_count,
            "skipped_short_geometry_count": lakes_stats.skipped_short_geometry_count,
            "skipped_open_way_count": lakes_stats.skipped_open_way_count,
            "feature_count": len(lakes.face_ids()),
            "chain_count": len(lakes.chains),
        },
        "parks": {
            "element_count": parks_stats.element_count,
            "polygon_like_count": parks_stats.polygon_like_count,
            "closed_way_count": parks_stats.closed_way_count,
            "skipped_non_way_count": parks_stats.skipped_non_way_count,
            "skipped_short_geometry_count": parks_stats.skipped_short_geometry_count,
            "skipped_open_way_count": parks_stats.skipped_open_way_count,
            "feature_count": len(parks.face_ids()),
            "chain_count": len(parks.chains),
        },
        "lsi": summarize_lsi(lsi_cpu_rows, lsi_embree_rows, lsi_cpu_sec, lsi_embree_sec),
        "pip": summarize_pip(pip_cpu_rows, pip_embree_rows, pip_cpu_sec, pip_embree_sec),
    }
    (output_dir / "goal37_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "goal37_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
