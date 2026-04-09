#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_soil_overlay_reference
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.reference.rtdl_language_reference import point_in_counties_reference
from scripts.goal28d_complete_and_run_county_zipcode import select_county_zipcode_slice
from scripts.goal28d_complete_and_run_county_zipcode import subset_by_face_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Goal 65 Vulkan vs OptiX comparison on accepted Linux workload packages."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--blockgroup-dir")
    parser.add_argument("--waterbodies-dir")
    parser.add_argument("--blockgroup-base-dir")
    parser.add_argument("--blockgroup-labels", default="county2300_s04,county2300_s05")
    parser.add_argument("--lakes-json", required=True)
    parser.add_argument("--parks-json", required=True)
    parser.add_argument("--bbox", required=True)
    parser.add_argument("--bbox-label", default="sunshine_tiny")
    parser.add_argument("--county-sizes", default="4,5,6,8,10,12")
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def canonical_rows(workload: str, rows) -> list[tuple[int, ...]]:
    if workload == "lsi":
        return sorted((int(row["left_id"]), int(row["right_id"])) for row in rows)
    if workload == "pip":
        return sorted((int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in rows)
    if workload == "overlay":
        return sorted(
            (
                int(row["left_polygon_id"]),
                int(row["right_polygon_id"]),
                int(row["requires_lsi"]),
                int(row["requires_pip"]),
            )
            for row in rows
        )
    raise ValueError(f"unsupported workload: {workload}")


def hash_rows(rows: list[tuple[int, ...]]) -> dict[str, object]:
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update(("\t".join(str(value) for value in row) + "\n").encode("utf-8"))
    return {"row_count": len(rows), "sha256": hasher.hexdigest()}


def backend_payload(
    *,
    workload: str,
    rows,
    reference_hash: str,
    reference_row_count: int,
    run_sec: float,
    prepare_sec: float | None = None,
) -> dict[str, object]:
    canonical = canonical_rows(workload, rows)
    hashed = hash_rows(canonical)
    payload = {
        "row_count": hashed["row_count"],
        "sha256": hashed["sha256"],
        "parity_vs_cpu": hashed["sha256"] == reference_hash and hashed["row_count"] == reference_row_count,
        "run_sec": run_sec,
    }
    if prepare_sec is not None:
        payload["prepare_sec"] = prepare_sec
        payload["total_sec"] = prepare_sec + run_sec
    return payload


def prepared_backend_payload(
    *,
    prepare_fn,
    workload: str,
    kernel,
    inputs: dict[str, object],
    reference_hash: str,
    reference_row_count: int,
) -> dict[str, object]:
    prepared, prepare_sec = time_call(prepare_fn, kernel)
    bound = prepared.bind(**inputs)
    cold_rows, cold_run_sec = time_call(bound.run)
    warm_rows, warm_run_sec = time_call(bound.run)
    payload = backend_payload(
        workload=workload,
        rows=warm_rows,
        reference_hash=reference_hash,
        reference_row_count=reference_row_count,
        run_sec=warm_run_sec,
        prepare_sec=prepare_sec,
    )
    cold_canonical = canonical_rows(workload, cold_rows)
    cold_hashed = hash_rows(cold_canonical)
    payload["cold_run_sec"] = cold_run_sec
    payload["cold_row_count"] = cold_hashed["row_count"]
    payload["cold_parity_vs_cpu"] = (
        cold_hashed["sha256"] == reference_hash and cold_hashed["row_count"] == reference_row_count
    )
    return payload


def compare_case(
    *,
    workload: str,
    kernel,
    cpu_inputs: dict[str, object],
) -> dict[str, object]:
    cpu_rows, cpu_sec = time_call(rt.run_cpu, kernel, **cpu_inputs)
    cpu_canonical = canonical_rows(workload, cpu_rows)
    cpu_hashed = hash_rows(cpu_canonical)

    embree_rows, embree_sec = time_call(rt.run_embree, kernel, **cpu_inputs)
    optix = prepared_backend_payload(
        prepare_fn=rt.prepare_optix,
        workload=workload,
        kernel=kernel,
        inputs=cpu_inputs,
        reference_hash=cpu_hashed["sha256"],
        reference_row_count=cpu_hashed["row_count"],
    )
    vulkan = prepared_backend_payload(
        prepare_fn=rt.prepare_vulkan,
        workload=workload,
        kernel=kernel,
        inputs=cpu_inputs,
        reference_hash=cpu_hashed["sha256"],
        reference_row_count=cpu_hashed["row_count"],
    )

    return {
        "cpu": {
            "row_count": cpu_hashed["row_count"],
            "sha256": cpu_hashed["sha256"],
            "run_sec": cpu_sec,
        },
        "embree": backend_payload(
            workload=workload,
            rows=embree_rows,
            reference_hash=cpu_hashed["sha256"],
            reference_row_count=cpu_hashed["row_count"],
            run_sec=embree_sec,
        ),
        "optix": optix,
        "vulkan": vulkan,
    }


def load_county_zipcode_case(county_dir: str, zipcode_dir: str, county_sizes: str) -> dict[str, object]:
    county = rt.arcgis_pages_to_cdb(county_dir, name="county_top4", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(zipcode_dir, name="zipcode_top4", ignore_invalid_tail=True)
    slices = []
    for size in [int(part) for part in county_sizes.split(",") if part.strip()]:
        selection = select_county_zipcode_slice(
            county,
            zipcode,
            min_zip_matches=size,
            target_zip_matches=size,
        )
        county_exec = subset_by_face_ids(county, {int(selection["county_face_id"])}, name=f"county_{size}")
        zipcode_exec = subset_by_face_ids(
            zipcode,
            {int(face_id) for face_id in selection["zipcode_face_ids"]},
            name=f"zipcode_{size}",
        )
        slices.append(
            {
                "slice_label": f"1x{size}",
                "selection": selection,
                "lsi_inputs": {
                    "left": rt.chains_to_segments(zipcode_exec),
                    "right": rt.chains_to_segments(county_exec),
                },
                "pip_inputs": {
                    "points": rt.chains_to_probe_points(zipcode_exec),
                    "polygons": rt.chains_to_polygons(county_exec),
                },
            }
        )
    return {
        "metadata": {
            "county_feature_count": len(county.face_ids()),
            "zipcode_feature_count": len(zipcode.face_ids()),
            "county_chain_count": len(county.chains),
            "zipcode_chain_count": len(zipcode.chains),
        },
        "slices": slices,
    }


def load_blockgroup_waterbodies_case(
    *,
    blockgroup_dir: str | None,
    waterbodies_dir: str | None,
    blockgroup_base_dir: str | None,
    blockgroup_labels: str,
) -> dict[str, object]:
    slices = []
    if blockgroup_base_dir:
        labels = [part for part in (label.strip() for label in blockgroup_labels.split(",")) if part]
        for label in labels:
            block_dir = str(Path(blockgroup_base_dir) / label / "blockgroup_feature_layer")
            water_dir = str(Path(blockgroup_base_dir) / label / "waterbodies_feature_layer")
            blockgroup = rt.arcgis_pages_to_cdb(block_dir, name=f"{label}_blockgroup", ignore_invalid_tail=True)
            waterbodies = rt.arcgis_pages_to_cdb(water_dir, name=f"{label}_waterbodies", ignore_invalid_tail=True)
            slices.append(
                {
                    "slice_label": label,
                    "metadata": {
                        "blockgroup_feature_count": len(blockgroup.face_ids()),
                        "waterbodies_feature_count": len(waterbodies.face_ids()),
                        "blockgroup_chain_count": len(blockgroup.chains),
                        "waterbodies_chain_count": len(waterbodies.chains),
                    },
                    "lsi_inputs": {
                        "left": rt.chains_to_segments(waterbodies),
                        "right": rt.chains_to_segments(blockgroup),
                    },
                    "pip_inputs": {
                        "points": rt.chains_to_probe_points(waterbodies),
                        "polygons": rt.chains_to_polygons(blockgroup),
                    },
                }
            )
        return {"metadata": {"comparison_surface": labels}, "slices": slices}

    if not blockgroup_dir or not waterbodies_dir:
        raise ValueError("either blockgroup_base_dir or both blockgroup_dir and waterbodies_dir are required")

    blockgroup = rt.arcgis_pages_to_cdb(blockgroup_dir, name="blockgroup_single", ignore_invalid_tail=True)
    waterbodies = rt.arcgis_pages_to_cdb(waterbodies_dir, name="waterbodies_single", ignore_invalid_tail=True)
    return {
        "metadata": {"comparison_surface": ["custom"]},
        "slices": [
            {
                "slice_label": "custom",
                "metadata": {
                    "blockgroup_feature_count": len(blockgroup.face_ids()),
                    "waterbodies_feature_count": len(waterbodies.face_ids()),
                    "blockgroup_chain_count": len(blockgroup.chains),
                    "waterbodies_chain_count": len(waterbodies.chains),
                },
                "lsi_inputs": {
                    "left": rt.chains_to_segments(waterbodies),
                    "right": rt.chains_to_segments(blockgroup),
                },
                "pip_inputs": {
                    "points": rt.chains_to_probe_points(waterbodies),
                    "polygons": rt.chains_to_polygons(blockgroup),
                },
            }
        ],
    }


def load_lkau_pkau_overlay_case(lakes_json: str, parks_json: str) -> dict[str, object]:
    lakes_elements = rt.load_overpass_elements(lakes_json)
    parks_elements = rt.load_overpass_elements(parks_json)
    lakes_stats = rt.overpass_elements_stats(lakes_elements)
    parks_stats = rt.overpass_elements_stats(parks_elements)
    lakes = rt.overpass_elements_to_cdb(lakes_elements, name="lkau_slice")
    parks = rt.overpass_elements_to_cdb(parks_elements, name="pkau_slice")
    return {
        "metadata": {
            "lakes_element_count": lakes_stats.element_count,
            "lakes_closed_way_count": lakes_stats.closed_way_count,
            "lakes_feature_count": len(lakes.face_ids()),
            "parks_element_count": parks_stats.element_count,
            "parks_closed_way_count": parks_stats.closed_way_count,
            "parks_feature_count": len(parks.face_ids()),
        },
        "overlay_inputs": {
            "left": rt.chains_to_polygons(lakes),
            "right": rt.chains_to_polygons(parks),
        },
    }


def render_markdown(summary: dict[str, object]) -> str:
    def backend_lines(label: str, payload: dict[str, object]) -> list[str]:
        lines = [
            f"- {label}: run `{payload['run_sec']:.9f} s`, rows `{payload['row_count']}`, parity vs cpu `{payload.get('parity_vs_cpu', True)}`",
        ]
        if "prepare_sec" in payload:
            lines.append(
                f"  prepare `{payload['prepare_sec']:.9f} s`, cold `{payload['cold_run_sec']:.9f} s`, warm total `{payload['total_sec']:.9f} s`"
            )
        return lines

    def case_lines(title: str, metadata: dict[str, object], workloads: dict[str, dict[str, object]]) -> list[str]:
        lines = [f"## {title}", ""]
        for key, value in metadata.items():
            lines.append(f"- {key.replace('_', ' ')}: `{value}`")
        lines.append("")
        for workload_name, payload in workloads.items():
            lines.append(f"### {workload_name.upper()}")
            lines.append("")
            lines.extend(backend_lines("cpu", payload["cpu"]))
            lines.extend(backend_lines("embree", payload["embree"]))
            lines.extend(backend_lines("optix", payload["optix"]))
            lines.extend(backend_lines("vulkan", payload["vulkan"]))
            lines.append("")
            if workload_name in ("lsi", "pip"):
                lines.append(
                    f"- warm Vulkan vs warm OptiX speed ratio: `{payload['optix']['run_sec'] / payload['vulkan']['run_sec']:.6f}x optix/vulkan`"
                )
            else:
                lines.append(
                    f"- warm Vulkan vs warm OptiX speed ratio: `{payload['optix']['run_sec'] / payload['vulkan']['run_sec']:.6f}x optix/vulkan`"
                )
            lines.append("")
        return lines

    def county_slice_lines(county_payload: dict[str, object]) -> list[str]:
        lines = [
            "## County/Zipcode bounded `1xN` ladder from `top4_tx_ca_ny_pa`",
            "",
        ]
        for key, value in county_payload["metadata"].items():
            lines.append(f"- {key.replace('_', ' ')}: `{value}`")
        lines.extend(
            [
                "- reason for bounded ladder:",
                "  Vulkan `lsi` currently cannot represent the whole `top4` package because its current output-capacity contract is `uint32`-bounded",
                "",
            ]
        )
        for slice_summary in county_payload["slices"]:
            lines.append(f"### {slice_summary['slice_label']}")
            lines.append("")
            lines.append(f"- estimated total segments: `{slice_summary['selection']['estimated_total_segments']}`")
            lines.append(f"- zipcode face count: `{len(slice_summary['selection']['zipcode_face_ids'])}`")
            lines.append("")
            for workload_name, payload in slice_summary["workloads"].items():
                lines.append(f"#### {workload_name.upper()}")
                lines.append("")
                lines.extend(backend_lines("cpu", payload["cpu"]))
                lines.extend(backend_lines("embree", payload["embree"]))
                lines.extend(backend_lines("optix", payload["optix"]))
                lines.extend(backend_lines("vulkan", payload["vulkan"]))
                lines.append("")
                lines.append(
                    f"- warm Vulkan vs warm OptiX speed ratio: `{payload['optix']['run_sec'] / payload['vulkan']['run_sec']:.6f}x optix/vulkan`"
                )
                lines.append("")
        return lines

    def block_slice_lines(block_payload: dict[str, object]) -> list[str]:
        lines = [
            "## BlockGroup/WaterBodies bounded ladder",
            "",
            f"- comparison surface: `{', '.join(block_payload['metadata']['comparison_surface'])}`",
            "- reason for bounded ladder:",
            "  Vulkan `lsi` currently exceeds its 512 MiB output guardrail at `county2300_s06` and above, so the accepted comparison surface here is the largest feasible bounded ladder on this host: `county2300_s04` and `county2300_s05`.",
            "",
        ]
        for slice_summary in block_payload["slices"]:
            lines.append(f"### {slice_summary['slice_label']}")
            lines.append("")
            for key, value in slice_summary["metadata"].items():
                lines.append(f"- {key.replace('_', ' ')}: `{value}`")
            lines.append("")
            for workload_name, payload in slice_summary["workloads"].items():
                lines.append(f"#### {workload_name.upper()}")
                lines.append("")
                lines.extend(backend_lines("cpu", payload["cpu"]))
                lines.extend(backend_lines("embree", payload["embree"]))
                lines.extend(backend_lines("optix", payload["optix"]))
                lines.extend(backend_lines("vulkan", payload["vulkan"]))
                lines.append("")
                lines.append(
                    f"- warm Vulkan vs warm OptiX speed ratio: `{payload['optix']['run_sec'] / payload['vulkan']['run_sec']:.6f}x optix/vulkan`"
                )
                lines.append("")
        return lines

    lines = [
        "# Goal 65 Vulkan vs OptiX Linux Comparison",
        "",
        f"Host label: `{summary['host_label']}`",
        f"OptiX version: `{summary['optix_version']}`",
        f"Vulkan version: `{summary['vulkan_version']}`",
        "",
        "Boundary:",
        "",
        "- this compares accepted RTDL backends on the same Linux GPU host and the same already-staged workload packages",
        "- correctness is judged against the native C oracle (`run_cpu(...)`)",
        "- performance emphasis is the true warm Vulkan vs warm OptiX comparison, after one executed cold run per prepared backend",
        "- this is not a new PostGIS closure round",
        "",
    ]
    lines.extend(county_slice_lines(summary["county_zipcode"]))
    lines.extend(block_slice_lines(summary["blockgroup_waterbodies"]))
    lines.extend(
        case_lines(
            f"LKAU/PKAU overlay-seed `{summary['lkau_pkau_overlay']['bbox_label']}`",
            summary["lkau_pkau_overlay"]["metadata"],
            summary["lkau_pkau_overlay"]["workloads"],
        )
    )
    lines.extend(
        [
            "## Conclusion",
            "",
            "- this round determines whether Vulkan is parity-clean on the accepted Linux packages already used for OptiX and Embree validation",
            "- the main performance comparison is warm Vulkan vs warm OptiX on the same GTX 1070 host",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county_zipcode = load_county_zipcode_case(args.county_dir, args.zipcode_dir, args.county_sizes)
    blockgroup_waterbodies = load_blockgroup_waterbodies_case(
        blockgroup_dir=args.blockgroup_dir,
        waterbodies_dir=args.waterbodies_dir,
        blockgroup_base_dir=args.blockgroup_base_dir,
        blockgroup_labels=args.blockgroup_labels,
    )
    lkau_pkau_overlay = load_lkau_pkau_overlay_case(args.lakes_json, args.parks_json)

    summary = {
        "host_label": args.host_label,
        "bbox": args.bbox,
        "optix_version": rt.optix_version(),
        "vulkan_version": rt.vulkan_version(),
        "county_zipcode": {
            "metadata": county_zipcode["metadata"],
            "slices": [
                {
                    "slice_label": slice_case["slice_label"],
                    "selection": slice_case["selection"],
                    "workloads": {
                        "lsi": compare_case(
                            workload="lsi",
                            kernel=county_zip_join_reference,
                            cpu_inputs=slice_case["lsi_inputs"],
                        ),
                        "pip": compare_case(
                            workload="pip",
                            kernel=point_in_counties_reference,
                            cpu_inputs=slice_case["pip_inputs"],
                        ),
                    },
                }
                for slice_case in county_zipcode["slices"]
            ],
        },
        "blockgroup_waterbodies": {
            "metadata": blockgroup_waterbodies["metadata"],
            "slices": [
                {
                    "slice_label": slice_case["slice_label"],
                    "metadata": slice_case["metadata"],
                    "workloads": {
                        "lsi": compare_case(
                            workload="lsi",
                            kernel=county_zip_join_reference,
                            cpu_inputs=slice_case["lsi_inputs"],
                        ),
                        "pip": compare_case(
                            workload="pip",
                            kernel=point_in_counties_reference,
                            cpu_inputs=slice_case["pip_inputs"],
                        ),
                    },
                }
                for slice_case in blockgroup_waterbodies["slices"]
            ],
        },
        "lkau_pkau_overlay": {
            "bbox_label": args.bbox_label,
            "metadata": lkau_pkau_overlay["metadata"],
            "workloads": {
                "overlay": compare_case(
                    workload="overlay",
                    kernel=county_soil_overlay_reference,
                    cpu_inputs=lkau_pkau_overlay["overlay_inputs"],
                ),
            },
        },
    }

    (output_dir / "goal65_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal65_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
