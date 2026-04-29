#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1135 changed-path RTX pod plan"


def _cmd(*parts: str) -> list[str]:
    return list(parts)


def build_plan(*, report_dir: str = "docs/reports/goal1135_changed_path_rtx_pod") -> dict[str, Any]:
    entries = [
        {
            "label": "database_analytics_compact_summary",
            "apps": ["database_analytics"],
            "reason": "Goal1128 changed compact-summary row-materialization behavior.",
            "command": _cmd(
                "python3",
                "scripts/goal756_db_prepared_session_perf.py",
                "--backend",
                "optix",
                "--scenario",
                "all",
                "--copies",
                "20000",
                "--iterations",
                "5",
                "--output-mode",
                "compact_summary",
                "--strict",
                "--output-json",
                f"{report_dir}/database_analytics_compact_summary.json",
            ),
        },
        {
            "label": "graph_visibility_edges_gate",
            "apps": ["graph_analytics"],
            "reason": "Goal1129 added graph phase splits; retest bounded graph RT sub-paths.",
            "command": _cmd(
                "python3",
                "scripts/goal889_graph_visibility_optix_gate.py",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "0",
                "--strict",
                "--output-json",
                f"{report_dir}/graph_visibility_edges_gate.json",
            ),
        },
        {
            "label": "road_hazard_native_summary_count",
            "apps": ["road_hazard_screening"],
            "reason": "Goal1130 changed native summary to use prepared threshold count.",
            "command": _cmd(
                "python3",
                "scripts/goal888_road_hazard_native_optix_gate.py",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--strict",
                "--output-json",
                f"{report_dir}/road_hazard_native_summary_count.json",
            ),
        },
        {
            "label": "polygon_pair_overlap_phase_gate",
            "apps": ["polygon_pair_overlap_area_rows"],
            "reason": "Goal1131 exposed candidate-discovery vs exact-continuation phase split.",
            "command": _cmd(
                "python3",
                "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                "--app",
                "pair_overlap",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "20",
                "--output-json",
                f"{report_dir}/polygon_pair_overlap_phase_gate.json",
            ),
        },
        {
            "label": "polygon_set_jaccard_phase_gate",
            "apps": ["polygon_set_jaccard"],
            "reason": "Goal1131 added compact Jaccard summary and phase split.",
            "command": _cmd(
                "python3",
                "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                "--app",
                "jaccard",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "20",
                "--output-json",
                f"{report_dir}/polygon_set_jaccard_phase_gate.json",
            ),
        },
        {
            "label": "hausdorff_threshold_phase_gate",
            "apps": ["hausdorff_distance"],
            "reason": "Goals1132-1134 clarified app/profiler phase contracts; collect capability-phase evidence only.",
            "command": _cmd(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "hausdorff_threshold",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--iterations",
                "5",
                "--radius",
                "0.4",
                "--output-json",
                f"{report_dir}/hausdorff_threshold_phase_gate.json",
            ),
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": report_dir,
        "entry_count": len(entries),
        "entries": entries,
        "setup_commands": [
            _cmd("mkdir", "-p", report_dir),
            _cmd("export", "PYTHONPATH=src:."),
        ],
        "cloud_policy": (
            "Run these entries in one pod session after building/installing the current source. "
            "Do not start/stop cloud per app. If one entry OOMs, lower only that entry's scale "
            "and continue the remaining entries."
        ),
        "non_claim": (
            "This plan collects changed-path RTX artifacts only. It does not authorize public "
            "RTX speedup wording, release, or broad whole-app acceleration claims."
        ),
        "valid": len(entries) == 6 and all(entry["command"][-2] == "--output-json" for entry in entries),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1135 Changed-Path RTX Pod Plan",
        "",
        f"Date: {payload['date']}",
        "",
        payload["non_claim"],
        "",
        "## Policy",
        "",
        payload["cloud_policy"],
        "",
        "## Entries",
        "",
        "| Label | Apps | Reason | Command |",
        "|---|---|---|---|",
    ]
    for entry in payload["entries"]:
        lines.append(
            f"| `{entry['label']}` | `{', '.join(entry['apps'])}` | {entry['reason']} | "
            f"`{' '.join(entry['command'])}` |"
        )
    lines.extend(["", f"Valid: `{str(payload['valid']).lower()}`", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a changed-path RTX pod command plan.")
    parser.add_argument("--report-dir", default="docs/reports/goal1135_changed_path_rtx_pod")
    parser.add_argument("--output-json", default="docs/reports/goal1135_changed_path_rtx_pod_plan_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1135_changed_path_rtx_pod_plan_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_plan(report_dir=args.report_dir)
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
