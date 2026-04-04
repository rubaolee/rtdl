#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assemble the Linux performance reproduction matrix from accepted Goal 69/70/71/77 artifacts."
    )
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(goal69: dict[str, object], goal70: dict[str, object], goal71: dict[str, object], goal77_optix: dict[str, object], goal77_embree: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    county69 = goal69["county_zipcode"]["pip"]
    rows.append(
        {
            "surface": "county_zipcode",
            "workload": "positive_hit_pip",
            "timing_boundary": "end_to_end",
            "dataset_label": "top4_tx_ca_ny_pa",
            "postgis_sec": county69["postgis_sec"],
            "embree_sec": county69["embree"]["sec"],
            "optix_sec": county69["optix"]["sec"],
            "row_count": county69["postgis"]["row_count"],
            "parity_embree": county69["embree"]["parity_vs_postgis"],
            "parity_optix": county69["optix"]["parity_vs_postgis"],
            "artifact_sources": [
                "docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json",
            ],
        }
    )

    block69 = goal69["blockgroup_waterbodies"]["pip"]
    rows.append(
        {
            "surface": "blockgroup_waterbodies",
            "workload": "positive_hit_pip",
            "timing_boundary": "end_to_end",
            "dataset_label": "county2300_s10",
            "postgis_sec": block69["postgis_sec"],
            "embree_sec": block69["embree"]["sec"],
            "optix_sec": block69["optix"]["sec"],
            "row_count": block69["postgis"]["row_count"],
            "parity_embree": block69["embree"]["parity_vs_postgis"],
            "parity_optix": block69["optix"]["parity_vs_postgis"],
            "artifact_sources": [
                "docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json",
            ],
        }
    )

    goal70_runs = goal70["runs"]
    rows.append(
        {
            "surface": "county_zipcode",
            "workload": "positive_hit_pip",
            "timing_boundary": "prepared_execution",
            "dataset_label": "top4_tx_ca_ny_pa",
            "backend": "optix",
            "postgis_sec_best": min(run["postgis_sec"] for run in goal70_runs),
            "postgis_sec_worst": max(run["postgis_sec"] for run in goal70_runs),
            "backend_sec_best": min(run["optix_sec"] for run in goal70_runs),
            "backend_sec_worst": max(run["optix_sec"] for run in goal70_runs),
            "row_count": goal70["best_run"]["row_count"],
            "parity_all_reruns": goal70["result"]["parity_preserved"],
            "beats_postgis_all_reruns": goal70["result"]["beats_postgis_on_long_workload"],
            "artifact_sources": [
                "docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.json",
            ],
        }
    )

    goal71_runs = goal71["runs"]
    rows.append(
        {
            "surface": "county_zipcode",
            "workload": "positive_hit_pip",
            "timing_boundary": "prepared_execution",
            "dataset_label": "top4_tx_ca_ny_pa",
            "backend": "embree",
            "postgis_sec_best": min(run["postgis_sec"] for run in goal71_runs),
            "postgis_sec_worst": max(run["postgis_sec"] for run in goal71_runs),
            "backend_sec_best": min(run["backend_sec"] for run in goal71_runs),
            "backend_sec_worst": max(run["backend_sec"] for run in goal71_runs),
            "row_count": goal71["postgis"]["row_count"],
            "parity_all_reruns": goal71["result"]["parity_preserved_all_reruns"],
            "beats_postgis_all_reruns": goal71["result"]["beats_postgis_all_reruns"],
            "artifact_sources": [
                "docs/reports/goal71_embree_long_county_prepared_exec_artifacts_2026-04-04/summary.json",
            ],
        }
    )

    rows.append(
        {
            "surface": "county_zipcode_selected_cdb",
            "workload": "positive_hit_pip",
            "timing_boundary": "cached_repeated_call",
            "dataset_label": "goal28d_selected_cdb_slice",
            "backend": "optix",
            "postgis_sec_first": goal77_optix["runs"][0]["postgis_sec"],
            "postgis_sec_best_repeated": min(run["postgis_sec"] for run in goal77_optix["runs"][1:]),
            "backend_sec_first": goal77_optix["result"]["first_run_sec"],
            "backend_sec_best_repeated": goal77_optix["result"]["best_repeated_run_sec"],
            "row_count": goal77_optix["postgis"]["row_count"],
            "parity_all_reruns": goal77_optix["result"]["parity_preserved_all_reruns"],
            "artifact_sources": [
                "docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/optix/summary.json",
            ],
        }
    )

    rows.append(
        {
            "surface": "county_zipcode_selected_cdb",
            "workload": "positive_hit_pip",
            "timing_boundary": "cached_repeated_call",
            "dataset_label": "goal28d_selected_cdb_slice",
            "backend": "embree",
            "postgis_sec_first": goal77_embree["runs"][0]["postgis_sec"],
            "postgis_sec_best_repeated": min(run["postgis_sec"] for run in goal77_embree["runs"][1:]),
            "backend_sec_first": goal77_embree["result"]["first_run_sec"],
            "backend_sec_best_repeated": goal77_embree["result"]["best_repeated_run_sec"],
            "row_count": goal77_embree["postgis"]["row_count"],
            "parity_all_reruns": goal77_embree["result"]["parity_preserved_all_reruns"],
            "artifact_sources": [
                "docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/embree/summary.json",
            ],
        }
    )

    return rows


def build_skipped_rows() -> list[dict[str, str]]:
    return [
        {
            "surface": "lakes_parks_continent_families",
            "reason": "dataset acquisition unavailable or unstable in current project environment",
        },
        {
            "surface": "vulkan_performance_matrix",
            "reason": "explicitly out of scope for Goal 79; backend not performance-competitive",
        },
        {
            "surface": "oracle_backends_performance",
            "reason": "oracles are correctness references, not performance targets",
        },
        {
            "surface": "lsi_or_overlay_postgis_matrix",
            "reason": "current available comparison package is limited to positive-hit pip timing surfaces with explicit PostGIS contract",
        },
    ]


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    winners = {"postgis": [], "embree": [], "optix": []}
    for row in rows:
        boundary = row["timing_boundary"]
        surface = row["surface"]
        if boundary == "end_to_end":
            times = {
                "postgis": row["postgis_sec"],
                "embree": row["embree_sec"],
                "optix": row["optix_sec"],
            }
            winner = min(times, key=times.get)
        elif row["backend"] == "embree":
            if boundary == "prepared_execution":
                winner = "embree" if row["backend_sec_best"] < row["postgis_sec_best"] else "postgis"
            else:
                winner = "embree" if row["backend_sec_best_repeated"] < row["postgis_sec_best_repeated"] else "postgis"
        else:
            if boundary == "prepared_execution":
                winner = "optix" if row["backend_sec_best"] < row["postgis_sec_best"] else "postgis"
            else:
                winner = "optix" if row["backend_sec_best_repeated"] < row["postgis_sec_best_repeated"] else "postgis"
        winners[winner].append(f"{surface}:{boundary}")
    return winners


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Goal 79 Linux Performance Reproduction Matrix",
        "",
        f"Host label: `{summary['host_label']}`",
        "",
        "This package aggregates the accepted Linux-measured performance surfaces currently available in the RTDL repo.",
        "",
        "Important boundary:",
        "",
        "- rows are grouped by timing boundary",
        "- end-to-end, prepared-execution, and cached repeated-call numbers are not interchangeable",
        "- skipped surfaces are listed explicitly below",
        "",
        "## Included Rows",
        "",
    ]
    for row in summary["rows"]:
        lines.append(f"### {row['surface']} / {row['timing_boundary']}")
        lines.append("")
        lines.append(f"- workload: `{row['workload']}`")
        lines.append(f"- dataset label: `{row['dataset_label']}`")
        if row["timing_boundary"] == "end_to_end":
            lines.append(f"- PostGIS: `{row['postgis_sec']:.9f} s`")
            lines.append(f"- Embree: `{row['embree_sec']:.9f} s`")
            lines.append(f"- OptiX: `{row['optix_sec']:.9f} s`")
            lines.append(f"- parity: `embree={row['parity_embree']}, optix={row['parity_optix']}`")
        elif row["timing_boundary"] == "prepared_execution":
            lines.append(f"- backend: `{row['backend']}`")
            lines.append(f"- backend best/worst: `{row['backend_sec_best']:.9f} / {row['backend_sec_worst']:.9f} s`")
            lines.append(f"- PostGIS best/worst: `{row['postgis_sec_best']:.9f} / {row['postgis_sec_worst']:.9f} s`")
            lines.append(f"- beats PostGIS all reruns: `{row['beats_postgis_all_reruns']}`")
            lines.append(f"- parity all reruns: `{row['parity_all_reruns']}`")
        else:
            lines.append(f"- backend: `{row['backend']}`")
            lines.append(f"- first raw-input run: `{row['backend_sec_first']:.9f} s`")
            lines.append(f"- best repeated run: `{row['backend_sec_best_repeated']:.9f} s`")
            lines.append(f"- PostGIS first / best repeated: `{row['postgis_sec_first']:.9f} / {row['postgis_sec_best_repeated']:.9f} s`")
            lines.append(f"- parity all reruns: `{row['parity_all_reruns']}`")
        lines.append(f"- row count: `{row['row_count']}`")
        lines.append("")

    lines.extend(
        [
            "## Winners By Boundary",
            "",
            f"- PostGIS wins: `{', '.join(summary['winners']['postgis']) or 'none'}`",
            f"- Embree wins: `{', '.join(summary['winners']['embree']) or 'none'}`",
            f"- OptiX wins: `{', '.join(summary['winners']['optix']) or 'none'}`",
            "",
            "## Skipped Surfaces",
            "",
        ]
    )
    for row in summary["skipped_rows"]:
        lines.append(f"- `{row['surface']}`: {row['reason']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = repo_root()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    goal69 = load_json(root / "docs/reports/goal69_final_measured_artifacts_2026-04-04/goal69_summary.json")
    goal70 = load_json(root / "docs/reports/goal70_optix_long_county_prepared_exec_artifacts_2026-04-04/goal70_summary.json")
    goal71 = load_json(root / "docs/reports/goal71_embree_long_county_prepared_exec_artifacts_2026-04-04/summary.json")
    goal77_optix = load_json(root / "docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/optix/summary.json")
    goal77_embree = load_json(root / "docs/reports/goal77_runtime_cache_measurement_artifacts_2026-04-04/embree/summary.json")

    rows = build_rows(goal69, goal70, goal71, goal77_optix, goal77_embree)
    summary = {
        "date": "2026-04-04",
        "host_label": "lestat-lx1",
        "included_row_count": len(rows),
        "rows": rows,
        "skipped_rows": build_skipped_rows(),
    }
    summary["winners"] = summarize(rows)

    (output_dir / "goal79_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal79_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
