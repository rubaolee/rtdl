#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def chain_bbox(chain: rt.CdbChain) -> tuple[float, float, float, float]:
    xs = [point.x for point in chain.points]
    ys = [point.y for point in chain.points]
    return min(xs), min(ys), max(xs), max(ys)


def merge_bbox(
    lhs: tuple[float, float, float, float],
    rhs: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    return (
        min(lhs[0], rhs[0]),
        min(lhs[1], rhs[1]),
        max(lhs[2], rhs[2]),
        max(lhs[3], rhs[3]),
    )


def bbox_overlaps(
    lhs: tuple[float, float, float, float],
    rhs: tuple[float, float, float, float],
) -> bool:
    return not (
        lhs[2] < rhs[0] or
        rhs[2] < lhs[0] or
        lhs[3] < rhs[1] or
        rhs[3] < lhs[1]
    )


def face_records(dataset: rt.CdbDataset) -> tuple[dict[str, object], ...]:
    grouped: dict[int, list[rt.CdbChain]] = defaultdict(list)
    for chain in dataset.chains:
        if chain.left_face_id != 0:
            grouped[chain.left_face_id].append(chain)

    records = []
    for face_id, chains in grouped.items():
        bbox = chain_bbox(chains[0])
        point_count = 0
        for chain in chains[1:]:
            bbox = merge_bbox(bbox, chain_bbox(chain))
        for chain in chains:
            point_count += chain.point_count
        records.append(
            {
                "face_id": face_id,
                "chain_count": len(chains),
                "segment_count": sum(max(0, chain.point_count - 1) for chain in chains),
                "point_count": point_count,
                "bbox": bbox,
            }
        )
    return tuple(sorted(records, key=lambda record: int(record["face_id"])))


def subset_by_face_ids(dataset: rt.CdbDataset, face_ids: set[int], *, name: str) -> rt.CdbDataset:
    chains = tuple(chain for chain in dataset.chains if chain.left_face_id in face_ids)
    return rt.CdbDataset(name=name, chains=chains)


def select_county_zipcode_slice(
    county: rt.CdbDataset,
    zipcode: rt.CdbDataset,
    *,
    min_zip_matches: int,
    target_zip_matches: int,
) -> dict[str, object]:
    county_records = face_records(county)
    zipcode_records = face_records(zipcode)

    best: dict[str, object] | None = None
    for county_record in county_records:
        overlaps = [
            record for record in zipcode_records
            if bbox_overlaps(county_record["bbox"], record["bbox"])
        ]
        if len(overlaps) < min_zip_matches:
            continue
        overlaps.sort(key=lambda record: (int(record["segment_count"]), int(record["face_id"])))
        chosen = overlaps[:target_zip_matches]
        total_segments = int(county_record["segment_count"]) + sum(int(record["segment_count"]) for record in chosen)
        candidate = {
            "county_face_id": int(county_record["face_id"]),
            "county_bbox": county_record["bbox"],
            "county_chain_count": int(county_record["chain_count"]),
            "county_segment_count": int(county_record["segment_count"]),
            "zipcode_face_ids": [int(record["face_id"]) for record in chosen],
            "zipcode_match_count": len(overlaps),
            "zipcode_selected_count": len(chosen),
            "zipcode_selected_segment_count": sum(int(record["segment_count"]) for record in chosen),
            "estimated_total_segments": total_segments,
        }
        if best is None or (
            int(candidate["estimated_total_segments"]) < int(best["estimated_total_segments"]) or
            (
                int(candidate["estimated_total_segments"]) == int(best["estimated_total_segments"]) and
                int(candidate["zipcode_match_count"]) > int(best["zipcode_match_count"])
            )
        ):
            best = candidate

    if best is None:
        raise RuntimeError(
            "no county face had enough overlapping zipcode faces for the requested slice; "
            "lower min_zip_matches or target_zip_matches"
        )
    return best


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
    selection = summary["selection"]
    lsi = summary["lsi"]
    pip = summary["pip"]
    lines = [
        "# Goal 28D County/Zipcode Linux Larger Execution Summary",
        "",
        f"Host label: `{summary['host_label']}`",
        "",
        "## Converted Inputs",
        "",
        f"- county pages loaded: `{summary['county']['page_count']}`",
        f"- county features: `{summary['county']['feature_count']}`",
        f"- county chains: `{summary['county']['chain_count']}`",
        f"- zipcode pages loaded: `{summary['zipcode']['page_count']}`",
        f"- zipcode features: `{summary['zipcode']['feature_count']}`",
        f"- zipcode chains: `{summary['zipcode']['chain_count']}`",
        "",
        "## Selected Slice",
        "",
        f"- county face id: `{selection['county_face_id']}`",
        f"- county bbox: `{tuple(selection['county_bbox'])}`",
        f"- county chain count: `{selection['county_chain_count']}`",
        f"- county segment count: `{selection['county_segment_count']}`",
        f"- zipcode overlapping matches found: `{selection['zipcode_match_count']}`",
        f"- zipcode selected ids: `{selection['zipcode_face_ids']}`",
        f"- zipcode selected count: `{selection['zipcode_selected_count']}`",
        f"- zipcode selected segment count: `{selection['zipcode_selected_segment_count']}`",
        f"- estimated total segments: `{selection['estimated_total_segments']}`",
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
        "- county input is full exact-source conversion from staged ArcGIS pages",
        "- zipcode input is full exact-source conversion if staging completed before this run; otherwise the report must be treated as a checkpoint conversion",
        "- the slice is chosen by bounding-box overlap and low estimated segment cost, not by paper ordering",
        "- this report closes a larger Linux-host exact-source slice, not paper-scale reproduction",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal 28D larger Linux County/Zipcode exact-source execution slice.")
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--county-max-pages", type=int, default=None)
    parser.add_argument("--zipcode-max-pages", type=int, default=None)
    parser.add_argument("--min-zip-matches", type=int, default=5)
    parser.add_argument("--target-zip-matches", type=int, default=8)
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
        name="zipcode_full",
        max_pages=args.zipcode_max_pages,
        ignore_invalid_tail=True,
    )

    selection = select_county_zipcode_slice(
        county,
        zipcode,
        min_zip_matches=args.min_zip_matches,
        target_zip_matches=args.target_zip_matches,
    )
    county_exec = subset_by_face_ids(county, {int(selection["county_face_id"])}, name="uscounty_selected")
    zipcode_exec = subset_by_face_ids(
        zipcode,
        set(int(face_id) for face_id in selection["zipcode_face_ids"]),
        name="zipcode_selected",
    )

    county_cdb_path = rt.write_cdb(county_exec, output_dir / "uscounty_selected.cdb")
    zipcode_cdb_path = rt.write_cdb(zipcode_exec, output_dir / "zipcode_selected.cdb")

    county_segments = rt.chains_to_segments(county_exec)
    zipcode_segments = rt.chains_to_segments(zipcode_exec)
    county_polygons = rt.chains_to_polygons(county_exec)
    zipcode_points = rt.chains_to_probe_points(zipcode_exec)

    lsi_cpu_rows, lsi_cpu_sec = time_call(rt.run_cpu, county_zip_join_reference, left=zipcode_segments, right=county_segments)
    lsi_embree_rows, lsi_embree_sec = time_call(rt.run_embree, county_zip_join_reference, left=zipcode_segments, right=county_segments)
    pip_cpu_rows, pip_cpu_sec = time_call(rt.run_cpu, point_in_counties_reference, points=zipcode_points, polygons=county_polygons)
    pip_embree_rows, pip_embree_sec = time_call(rt.run_embree, point_in_counties_reference, points=zipcode_points, polygons=county_polygons)

    summary = {
        "host_label": args.host_label,
        "county": {
            "page_count": rt.count_arcgis_loaded_pages(args.county_dir, max_pages=args.county_max_pages, ignore_invalid_tail=True),
            "feature_count": len(county.face_ids()),
            "chain_count": len(county.chains),
        },
        "zipcode": {
            "page_count": rt.count_arcgis_loaded_pages(args.zipcode_dir, max_pages=args.zipcode_max_pages, ignore_invalid_tail=True),
            "feature_count": len(zipcode.face_ids()),
            "chain_count": len(zipcode.chains),
        },
        "selection": {
            **selection,
            "county_exec_cdb_path": str(county_cdb_path),
            "zipcode_exec_cdb_path": str(zipcode_cdb_path),
            "county_exec_chain_count": len(county_exec.chains),
            "zipcode_exec_chain_count": len(zipcode_exec.chains),
            "county_exec_feature_count": len(county_exec.face_ids()),
            "zipcode_exec_feature_count": len(zipcode_exec.face_ids()),
        },
        "lsi": summarize_lsi(lsi_cpu_rows, lsi_embree_rows, lsi_cpu_sec, lsi_embree_sec),
        "pip": summarize_pip(pip_cpu_rows, pip_embree_rows, pip_cpu_sec, pip_embree_sec),
    }
    (output_dir / "goal28d_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal28d_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
