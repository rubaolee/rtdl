#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Goal 47 large C-oracle vs OptiX checks on the same larger real-data families used by Goal 41."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--blockgroup-dir", required=True)
    parser.add_argument("--waterbodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    return parser.parse_args()


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def lsi_pairs(rows) -> list[tuple[int, int]]:
    return sorted((int(row["left_id"]), int(row["right_id"])) for row in rows)


def pip_rows(rows) -> list[tuple[int, int, int]]:
    return sorted((int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in rows)


def render_markdown(summary: dict[str, object]) -> str:
    county = summary["county_zipcode"]
    block = summary["blockgroup_waterbodies"]
    lines = [
        "# Goal 47 Large C-Oracle vs OptiX Checks",
        "",
        f"Host label: `{summary['host_label']}`",
        f"OptiX version: `{summary['optix_version']}`",
        "",
        "## County/Zipcode `top4_tx_ca_ny_pa`",
        "",
        f"- county features: `{county['county_feature_count']}`",
        f"- zipcode features: `{county['zipcode_feature_count']}`",
        f"- county chains: `{county['county_chain_count']}`",
        f"- zipcode chains: `{county['zipcode_chain_count']}`",
        "",
        "### LSI",
        "",
        f"- pair parity: `{county['lsi']['pair_parity']}`",
        f"- C oracle: `{county['lsi']['cpu_sec']:.9f} s`",
        f"- OptiX: `{county['lsi']['optix_sec']:.9f} s`",
        f"- row count: `{county['lsi']['cpu_row_count']}`",
        "",
        "### PIP",
        "",
        f"- row parity: `{county['pip']['row_parity']}`",
        f"- C oracle: `{county['pip']['cpu_sec']:.9f} s`",
        f"- OptiX: `{county['pip']['optix_sec']:.9f} s`",
        f"- row count: `{county['pip']['cpu_row_count']}`",
        "",
        "## BlockGroup/WaterBodies `county2300_s10`",
        "",
        f"- blockgroup features: `{block['blockgroup_feature_count']}`",
        f"- waterbodies features: `{block['waterbodies_feature_count']}`",
        f"- blockgroup chains: `{block['blockgroup_chain_count']}`",
        f"- waterbodies chains: `{block['waterbodies_chain_count']}`",
        "",
        "### LSI",
        "",
        f"- pair parity: `{block['lsi']['pair_parity']}`",
        f"- C oracle: `{block['lsi']['cpu_sec']:.9f} s`",
        f"- OptiX: `{block['lsi']['optix_sec']:.9f} s`",
        f"- row count: `{block['lsi']['cpu_row_count']}`",
        "",
        "### PIP",
        "",
        f"- row parity: `{block['pip']['row_parity']}`",
        f"- C oracle: `{block['pip']['cpu_sec']:.9f} s`",
        f"- OptiX: `{block['pip']['optix_sec']:.9f} s`",
        f"- row count: `{block['pip']['cpu_row_count']}`",
        "",
        "## Boundary",
        "",
        "- this extends the Goal 41 large-check pattern from C-oracle-vs-Embree to C-oracle-vs-OptiX",
        "- it uses the same larger real-data families already accepted in Goal 41",
        "- it is a correctness/performance check, not a full paper-scale GPU reproduction",
        "",
    ]
    return "\n".join(lines)


def summarize_lsi(cpu_rows, optix_rows, cpu_sec: float, optix_sec: float) -> dict[str, object]:
    cpu_pairs = lsi_pairs(cpu_rows)
    optix_pairs = lsi_pairs(optix_rows)
    return {
        "cpu_row_count": len(cpu_rows),
        "optix_row_count": len(optix_rows),
        "cpu_sec": cpu_sec,
        "optix_sec": optix_sec,
        "pair_parity": cpu_pairs == optix_pairs,
        "sample_cpu_pairs": cpu_pairs[:10],
        "sample_optix_pairs": optix_pairs[:10],
    }


def summarize_pip(cpu_rows, optix_rows, cpu_sec: float, optix_sec: float) -> dict[str, object]:
    cpu_triplets = pip_rows(cpu_rows)
    optix_triplets = pip_rows(optix_rows)
    return {
        "cpu_row_count": len(cpu_rows),
        "optix_row_count": len(optix_rows),
        "cpu_sec": cpu_sec,
        "optix_sec": optix_sec,
        "row_parity": cpu_triplets == optix_triplets,
        "sample_cpu_rows": cpu_triplets[:10],
        "sample_optix_rows": optix_triplets[:10],
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = rt.arcgis_pages_to_cdb(args.county_dir, name="county_top4", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(args.zipcode_dir, name="zipcode_top4", ignore_invalid_tail=True)
    blockgroup = rt.arcgis_pages_to_cdb(args.blockgroup_dir, name="blockgroup_county2300_s10", ignore_invalid_tail=True)
    waterbodies = rt.arcgis_pages_to_cdb(args.waterbodies_dir, name="waterbodies_county2300_s10", ignore_invalid_tail=True)

    county_segments = rt.chains_to_segments(county)
    zipcode_segments = rt.chains_to_segments(zipcode)
    county_polygons = rt.chains_to_polygons(county)
    zipcode_points = rt.chains_to_probe_points(zipcode)

    blockgroup_segments = rt.chains_to_segments(blockgroup)
    water_segments = rt.chains_to_segments(waterbodies)
    blockgroup_polygons = rt.chains_to_polygons(blockgroup)
    water_points = rt.chains_to_probe_points(waterbodies)

    county_lsi_cpu, county_lsi_cpu_sec = time_call(
        rt.run_cpu,
        county_zip_join_reference,
        left=zipcode_segments,
        right=county_segments,
    )
    county_lsi_optix, county_lsi_optix_sec = time_call(
        rt.run_optix,
        county_zip_join_reference,
        left=zipcode_segments,
        right=county_segments,
    )
    county_pip_cpu, county_pip_cpu_sec = time_call(
        rt.run_cpu,
        point_in_counties_reference,
        points=zipcode_points,
        polygons=county_polygons,
    )
    county_pip_optix, county_pip_optix_sec = time_call(
        rt.run_optix,
        point_in_counties_reference,
        points=zipcode_points,
        polygons=county_polygons,
    )

    block_lsi_cpu, block_lsi_cpu_sec = time_call(
        rt.run_cpu,
        county_zip_join_reference,
        left=water_segments,
        right=blockgroup_segments,
    )
    block_lsi_optix, block_lsi_optix_sec = time_call(
        rt.run_optix,
        county_zip_join_reference,
        left=water_segments,
        right=blockgroup_segments,
    )
    block_pip_cpu, block_pip_cpu_sec = time_call(
        rt.run_cpu,
        point_in_counties_reference,
        points=water_points,
        polygons=blockgroup_polygons,
    )
    block_pip_optix, block_pip_optix_sec = time_call(
        rt.run_optix,
        point_in_counties_reference,
        points=water_points,
        polygons=blockgroup_polygons,
    )

    summary = {
        "host_label": args.host_label,
        "optix_version": rt.optix_version(),
        "county_zipcode": {
            "county_feature_count": len(county.face_ids()),
            "zipcode_feature_count": len(zipcode.face_ids()),
            "county_chain_count": len(county.chains),
            "zipcode_chain_count": len(zipcode.chains),
            "lsi": summarize_lsi(county_lsi_cpu, county_lsi_optix, county_lsi_cpu_sec, county_lsi_optix_sec),
            "pip": summarize_pip(county_pip_cpu, county_pip_optix, county_pip_cpu_sec, county_pip_optix_sec),
        },
        "blockgroup_waterbodies": {
            "blockgroup_feature_count": len(blockgroup.face_ids()),
            "waterbodies_feature_count": len(waterbodies.face_ids()),
            "blockgroup_chain_count": len(blockgroup.chains),
            "waterbodies_chain_count": len(waterbodies.chains),
            "lsi": summarize_lsi(block_lsi_cpu, block_lsi_optix, block_lsi_cpu_sec, block_lsi_optix_sec),
            "pip": summarize_pip(block_pip_cpu, block_pip_optix, block_pip_cpu_sec, block_pip_optix_sec),
        },
    }

    (output_dir / "goal47_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal47_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
