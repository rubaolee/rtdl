#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


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
    county = summary["county"]
    zipcode = summary["zipcode"]
    execution = summary["execution_subset"]
    lsi = summary["lsi"]
    pip = summary["pip"]
    lines = [
        "# Goal 28C County/Zipcode Linux Execution Summary",
        "",
        f"Host label: `{summary['host_label']}`",
        "",
        "## Inputs",
        "",
        f"- county source pages used: `{county['page_count']}`",
        f"- zipcode source pages used: `{zipcode['page_count']}`",
        f"- county converted feature count: `{county['feature_count']}`",
        f"- county converted chain count: `{county['chain_count']}`",
        f"- zipcode feature count: `{zipcode['feature_count']}`",
        f"- zipcode chain count: `{zipcode['chain_count']}`",
        "",
        "## Execution Subset",
        "",
        f"- county execution feature limit: `{execution['county_feature_limit']}`",
        f"- zipcode execution feature limit: `{execution['zipcode_feature_limit']}`",
        f"- county execution feature count: `{execution['county_feature_count']}`",
        f"- zipcode execution feature count: `{execution['zipcode_feature_count']}`",
        f"- county execution chain count: `{execution['county_chain_count']}`",
        f"- zipcode execution chain count: `{execution['zipcode_chain_count']}`",
        "",
        "## LSI",
        "",
        f"- cpu rows: `{lsi['cpu_row_count']}`",
        f"- embree rows: `{lsi['embree_row_count']}`",
        f"- cpu sec: `{lsi['cpu_sec']:.6f}`",
        f"- embree sec: `{lsi['embree_sec']:.6f}`",
        f"- pair parity: `{lsi['pair_parity']}`",
        "",
        "## PIP",
        "",
        f"- cpu rows: `{pip['cpu_row_count']}`",
        f"- embree rows: `{pip['embree_row_count']}`",
        f"- cpu sec: `{pip['cpu_sec']:.6f}`",
        f"- embree sec: `{pip['embree_sec']:.6f}`",
        f"- row parity: `{pip['row_parity']}`",
        "",
        "## Boundary",
        "",
        "- county input is full exact-source from the staged ArcGIS pages used in Goal 28B",
        "- zipcode input is partial exact-source from the current staged checkpoint pages",
        "- polygon inputs are still chain-derived polygons, not a topologically exact face reconstruction",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert staged County/Zipcode pages to CDB and run the first Linux exact-source slice.")
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--county-max-pages", type=int, default=None)
    parser.add_argument("--zipcode-max-pages", type=int, default=None)
    parser.add_argument("--county-exec-max-features", type=int, default=1)
    parser.add_argument("--zipcode-exec-max-features", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = rt.arcgis_pages_to_cdb(
        args.county_dir,
        name="uscounty_full",
        max_pages=args.county_max_pages,
        ignore_invalid_tail=True,
    )
    zipcode = rt.arcgis_pages_to_cdb(
        args.zipcode_dir,
        name="zipcode_partial",
        max_pages=args.zipcode_max_pages,
        ignore_invalid_tail=True,
    )
    county_exec = rt.arcgis_pages_to_cdb(
        args.county_dir,
        name="uscounty_exec",
        max_pages=args.county_max_pages,
        max_features=args.county_exec_max_features,
        ignore_invalid_tail=True,
    )
    zipcode_exec = rt.arcgis_pages_to_cdb(
        args.zipcode_dir,
        name="zipcode_exec",
        max_pages=args.zipcode_max_pages,
        max_features=args.zipcode_exec_max_features,
        ignore_invalid_tail=True,
    )

    county_cdb_path = rt.write_cdb(county, output_dir / "uscounty_full.cdb")
    zipcode_cdb_path = rt.write_cdb(zipcode, output_dir / "zipcode_partial.cdb")
    county_exec_cdb_path = rt.write_cdb(county_exec, output_dir / "uscounty_exec.cdb")
    zipcode_exec_cdb_path = rt.write_cdb(zipcode_exec, output_dir / "zipcode_exec.cdb")

    county_segments = rt.chains_to_segments(county_exec)
    zipcode_segments = rt.chains_to_segments(zipcode_exec)
    county_polygons = rt.chains_to_polygons(county_exec)
    zipcode_points = rt.chains_to_probe_points(zipcode_exec)

    lsi_cpu_rows, lsi_cpu_sec = time_call(rt.run_cpu, county_zip_join_reference, left=zipcode_segments, right=county_segments)
    lsi_embree_rows, lsi_embree_sec = time_call(
        rt.run_embree,
        county_zip_join_reference,
        left=zipcode_segments,
        right=county_segments,
    )
    pip_cpu_rows, pip_cpu_sec = time_call(
        rt.run_cpu,
        point_in_counties_reference,
        points=zipcode_points,
        polygons=county_polygons,
    )
    pip_embree_rows, pip_embree_sec = time_call(
        rt.run_embree,
        point_in_counties_reference,
        points=zipcode_points,
        polygons=county_polygons,
    )

    summary = {
        "host_label": args.host_label,
        "county": {
            "page_count": rt.count_arcgis_loaded_pages(
                args.county_dir,
                max_pages=args.county_max_pages,
                ignore_invalid_tail=True,
            ),
            "feature_count": len(county.face_ids()),
            "chain_count": len(county.chains),
            "cdb_path": str(county_cdb_path),
        },
        "zipcode": {
            "page_count": rt.count_arcgis_loaded_pages(
                args.zipcode_dir,
                max_pages=args.zipcode_max_pages,
                ignore_invalid_tail=True,
            ),
            "feature_count": len(zipcode.face_ids()),
            "chain_count": len(zipcode.chains),
            "cdb_path": str(zipcode_cdb_path),
        },
        "execution_subset": {
            "county_feature_limit": args.county_exec_max_features,
            "zipcode_feature_limit": args.zipcode_exec_max_features,
            "county_feature_count": len(county_exec.face_ids()),
            "zipcode_feature_count": len(zipcode_exec.face_ids()),
            "county_chain_count": len(county_exec.chains),
            "zipcode_chain_count": len(zipcode_exec.chains),
            "county_exec_cdb_path": str(county_exec_cdb_path),
            "zipcode_exec_cdb_path": str(zipcode_exec_cdb_path),
        },
        "lsi": summarize_lsi(lsi_cpu_rows, lsi_embree_rows, lsi_cpu_sec, lsi_embree_sec),
        "pip": summarize_pip(pip_cpu_rows, pip_embree_rows, pip_cpu_sec, pip_embree_sec),
    }

    (output_dir / "goal28c_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal28c_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
