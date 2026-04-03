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
from scripts.goal28d_complete_and_run_county_zipcode import select_county_zipcode_slice
from scripts.goal28d_complete_and_run_county_zipcode import subset_by_face_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Goal 45 bounded real-data OptiX validation on County/Zipcode exact-source slices."
    )
    parser.add_argument("--county-dir", required=True)
    parser.add_argument("--zipcode-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--sizes", default="4,5,6,8,10,12")
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    return parser.parse_args()


def run_timed(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def benchmark_cpu(fn, *args, warmup: int, iterations: int, **kwargs) -> tuple[list[float], object]:
    result = None
    for _ in range(warmup):
        result = fn(*args, **kwargs)
    times: list[float] = []
    for _ in range(iterations):
        result, elapsed = run_timed(fn, *args, **kwargs)
        times.append(elapsed)
    return times, result


def benchmark_optix(fn, *args, warmup: int, iterations: int, **kwargs) -> dict[str, object]:
    jit_result, jit_sec = run_timed(fn, *args, **kwargs)
    for _ in range(warmup):
        fn(*args, **kwargs)
    warm_times: list[float] = []
    warm_result = jit_result
    for _ in range(iterations):
        warm_result, elapsed = run_timed(fn, *args, **kwargs)
        warm_times.append(elapsed)
    return {
        "jit_result": jit_result,
        "jit_sec": jit_sec,
        "warm_result": warm_result,
        "warm_times": warm_times,
    }


def lsi_rows(rows) -> list[tuple[int, int]]:
    return sorted((int(row["left_id"]), int(row["right_id"])) for row in rows)


def pip_rows(rows) -> list[tuple[int, int, int]]:
    return sorted(
        (int(row["point_id"]), int(row["polygon_id"]), int(row["contains"]))
        for row in rows
    )


def summarize_times(times: list[float]) -> dict[str, float]:
    return {
        "min_sec": min(times),
        "median_sec": statistics.median(times),
        "max_sec": max(times),
        "mean_sec": statistics.fmean(times),
    }


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Goal 45 OptiX County/Zipcode Real-Data Validation",
        "",
        f"Host label: `{summary['host_label']}`",
        "",
        "## Setup",
        "",
        f"- county page count: `{summary['county_page_count']}`",
        f"- county feature count: `{summary['county_feature_count']}`",
        f"- county chain count: `{summary['county_chain_count']}`",
        f"- zipcode page count: `{summary['zipcode_page_count']}`",
        f"- zipcode feature count: `{summary['zipcode_feature_count']}`",
        f"- zipcode chain count: `{summary['zipcode_chain_count']}`",
        f"- warmup: `{summary['warmup']}`",
        f"- iterations: `{summary['iterations']}`",
        "",
        "## Accepted Points",
        "",
        "| Slice | Estimated Segments | LSI Parity | LSI CPU Median (s) | LSI OptiX JIT (s) | LSI OptiX Warm Median (s) | LSI Speedup | PIP Parity | PIP CPU Median (s) | PIP OptiX JIT (s) | PIP OptiX Warm Median (s) | PIP Speedup |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]

    for point in summary["accepted_points"]:
        lines.append(
            "| `{slice_label}` | `{estimated_total_segments}` | `{lsi_parity}` | `{lsi_cpu:.9f}` | `{lsi_jit:.9f}` | `{lsi_warm:.9f}` | `{lsi_speedup:.2f}x` | `{pip_parity}` | `{pip_cpu:.9f}` | `{pip_jit:.9f}` | `{pip_warm:.9f}` | `{pip_speedup:.2f}x` |".format(
                slice_label=point["slice_label"],
                estimated_total_segments=point["selection"]["estimated_total_segments"],
                lsi_parity=point["lsi"]["exact_row_parity"],
                lsi_cpu=point["lsi"]["cpu_times"]["median_sec"],
                lsi_jit=point["lsi"]["optix_jit_sec"],
                lsi_warm=point["lsi"]["optix_warm_times"]["median_sec"],
                lsi_speedup=point["lsi"]["cpu_times"]["median_sec"] / point["lsi"]["optix_warm_times"]["median_sec"],
                pip_parity=point["pip"]["exact_row_parity"],
                pip_cpu=point["pip"]["cpu_times"]["median_sec"],
                pip_jit=point["pip"]["optix_jit_sec"],
                pip_warm=point["pip"]["optix_warm_times"]["median_sec"],
                pip_speedup=point["pip"]["cpu_times"]["median_sec"] / point["pip"]["optix_warm_times"]["median_sec"],
            )
        )

    lines.extend(["", "## Rejected Points", ""])
    rejected = summary["rejected_points"]
    if not rejected:
        lines.append("- none")
    else:
        for point in rejected:
            lines.append(
                "- `{}` rejected: `lsi_exact_row_parity={}`, `pip_exact_row_parity={}`".format(
                    point["slice_label"],
                    point["lsi"]["exact_row_parity"],
                    point["pip"]["exact_row_parity"],
                )
            )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- accepted points are exact-source slices that remained exact-row parity-clean for both `lsi` and `pip`",
            "- this is the first real-data OptiX validation/performance package for a RayJoin family on `192.168.1.20`",
            "- it is still bounded to co-located `1xN` slices rather than whole-dataset or state-scale execution",
            "- the trusted OptiX path on this host still uses the `nvcc` PTX fallback",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county = rt.arcgis_pages_to_cdb(args.county_dir, name="uscounty_full", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(args.zipcode_dir, name="zipcode_full", ignore_invalid_tail=True)

    accepted_points = []
    rejected_points = []

    for size in [int(part) for part in args.sizes.split(",") if part.strip()]:
        selection = select_county_zipcode_slice(
            county,
            zipcode,
            min_zip_matches=size,
            target_zip_matches=size,
        )
        county_exec = subset_by_face_ids(county, {int(selection["county_face_id"])}, name=f"uscounty_{size}")
        zipcode_exec = subset_by_face_ids(
            zipcode,
            {int(face_id) for face_id in selection["zipcode_face_ids"]},
            name=f"zipcode_{size}",
        )

        county_segments = rt.chains_to_segments(county_exec)
        zipcode_segments = rt.chains_to_segments(zipcode_exec)
        county_polygons = rt.chains_to_polygons(county_exec)
        zipcode_points = rt.chains_to_probe_points(zipcode_exec)

        lsi_cpu_times, lsi_cpu_rows = benchmark_cpu(
            rt.run_cpu,
            county_zip_join_reference,
            left=zipcode_segments,
            right=county_segments,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        lsi_optix = benchmark_optix(
            rt.run_optix,
            county_zip_join_reference,
            left=zipcode_segments,
            right=county_segments,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        pip_cpu_times, pip_cpu_rows = benchmark_cpu(
            rt.run_cpu,
            point_in_counties_reference,
            points=zipcode_points,
            polygons=county_polygons,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        pip_optix = benchmark_optix(
            rt.run_optix,
            point_in_counties_reference,
            points=zipcode_points,
            polygons=county_polygons,
            warmup=args.warmup,
            iterations=args.iterations,
        )

        point = {
            "slice_label": f"1x{size}",
            "selection": selection,
            "lsi": {
                "cpu_row_count": len(lsi_cpu_rows),
                "optix_jit_row_count": len(lsi_optix["jit_result"]),
                "optix_warm_row_count": len(lsi_optix["warm_result"]),
                "exact_row_parity": (
                    lsi_rows(lsi_cpu_rows)
                    == lsi_rows(lsi_optix["jit_result"])
                    == lsi_rows(lsi_optix["warm_result"])
                ),
                "cpu_times": summarize_times(lsi_cpu_times),
                "optix_jit_sec": lsi_optix["jit_sec"],
                "optix_warm_times": summarize_times(lsi_optix["warm_times"]),
            },
            "pip": {
                "cpu_row_count": len(pip_cpu_rows),
                "optix_jit_row_count": len(pip_optix["jit_result"]),
                "optix_warm_row_count": len(pip_optix["warm_result"]),
                "exact_row_parity": (
                    pip_rows(pip_cpu_rows)
                    == pip_rows(pip_optix["jit_result"])
                    == pip_rows(pip_optix["warm_result"])
                ),
                "cpu_times": summarize_times(pip_cpu_times),
                "optix_jit_sec": pip_optix["jit_sec"],
                "optix_warm_times": summarize_times(pip_optix["warm_times"]),
            },
        }
        if point["lsi"]["exact_row_parity"] and point["pip"]["exact_row_parity"]:
            accepted_points.append(point)
        else:
            rejected_points.append(point)

    summary = {
        "host_label": args.host_label,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "county_page_count": rt.count_arcgis_loaded_pages(args.county_dir, ignore_invalid_tail=True),
        "county_feature_count": len(county.face_ids()),
        "county_chain_count": len(county.chains),
        "zipcode_page_count": rt.count_arcgis_loaded_pages(args.zipcode_dir, ignore_invalid_tail=True),
        "zipcode_feature_count": len(zipcode.face_ids()),
        "zipcode_chain_count": len(zipcode.chains),
        "accepted_points": accepted_points,
        "rejected_points": rejected_points,
        "optix_version": rt.optix_version(),
    }

    (output_dir / "goal45_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal45_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
