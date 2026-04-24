#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest
from scripts.goal860_spatial_partial_ready_gate import build_spatial_gate


GOAL = "Goal862 spatial RTX collection packet"
DATE = "2026-04-23"
SPATIAL_APPS = {"service_coverage_gaps", "event_hotspot_screening"}


def build_packet() -> dict[str, Any]:
    gate = build_spatial_gate()
    manifest = build_manifest()
    rows = {str(row["app"]): row for row in gate["rows"]}
    deferred = [
        entry
        for entry in manifest.get("deferred_entries", [])
        if str(entry.get("app")) in SPATIAL_APPS
    ]
    deferred_by_app = {str(entry["app"]): entry for entry in deferred}

    packet_rows: list[dict[str, Any]] = []
    for app in sorted(SPATIAL_APPS):
        gate_row = rows[app]
        manifest_entry = deferred_by_app[app]
        packet_rows.append(
            {
                "app": app,
                "path_name": gate_row["path_name"],
                "gate_status": gate_row["row_status"],
                "claim_limit": gate_row["claim_limit"],
                "required_local_baselines": [
                    {
                        "baseline": item["baseline"],
                        "status": item["status"],
                        "path": item["path"],
                    }
                    for item in gate_row["required_checks"]
                ],
                "optional_local_baselines": [
                    {
                        "baseline": item["baseline"],
                        "status": item["status"],
                        "path": item["path"],
                    }
                    for item in gate_row["optional_checks"]
                ],
                "rtx_output_json": manifest_entry["command"][-1],
                "rtx_command": list(manifest_entry["command"]),
                "claim_scope": manifest_entry["claim_scope"],
                "non_claim": manifest_entry["non_claim"],
                "reason_deferred": manifest_entry["reason_deferred"],
                "activation_gate": manifest_entry["activation_gate"],
            }
        )

    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_goal860_status": gate["status"],
        "row_count": len(packet_rows),
        "rows": packet_rows,
        "one_shot_runner_example": [
            "python3",
            "scripts/goal769_rtx_pod_one_shot.py",
            "--only",
            "service_coverage_gaps",
            "--only",
            "event_hotspot_screening",
            "--include-deferred",
        ],
        "boundary": (
            "This packet requests real RTX collection only for the two spatial prepared-summary apps. "
            "It does not promote them automatically and does not authorize a public speedup claim."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal862 Spatial RTX Collection Packet",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- source Goal860 status: `{payload['source_goal860_status']}`",
        f"- rows packaged: `{payload['row_count']}`",
        "",
        "## One-Shot Runner Example",
        "",
        "```bash",
        " ".join(payload["one_shot_runner_example"]),
        "```",
        "",
        "## App Packets",
        "",
    ]
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['app']} / {row['path_name']}",
                "",
                f"- gate status: `{row['gate_status']}`",
                f"- claim scope: {row['claim_scope']}",
                f"- non-claim: {row['non_claim']}",
                f"- claim limit: {row['claim_limit']}",
                f"- RTX output artifact: `{row['rtx_output_json']}`",
                "",
                "Required local baselines:",
            ]
        )
        for item in row["required_local_baselines"]:
            lines.append(f"- `{item['baseline']}`: `{item['status']}` at `{item['path']}`")
        lines.extend(["", "Optional local baselines:"])
        for item in row["optional_local_baselines"]:
            lines.append(f"- `{item['baseline']}`: `{item['status']}` at `{item['path']}`")
        lines.extend(
            [
                "",
                "RTX command:",
                "```bash",
                " ".join(row["rtx_command"]),
                "```",
                "",
                f"- reason deferred: {row['reason_deferred']}",
                f"- activation gate: {row['activation_gate']}",
                "",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the next RTX collection packet for spatial prepared-summary apps.")
    parser.add_argument("--output-json", default="docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal862_spatial_rtx_collection_packet_2026-04-23.md")
    args = parser.parse_args(argv)
    payload = build_packet()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
