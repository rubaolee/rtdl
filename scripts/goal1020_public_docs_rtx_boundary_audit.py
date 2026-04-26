#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1020 public docs RTX boundary audit"

REQUIRED_PHRASES: dict[str, tuple[str, ...]] = {
    "README.md": (
        "not automatic public speedup claims",
        "robot_collision_screening / prepared_pose_flags",
        "larger RTX repeats stayed below the 100 ms",
        "docs/v1_0_rtx_app_status.md",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "not release authorization and not a public speedup claim",
        "blocked_for_public_speedup_wording",
        "rtdsl.rtx_public_wording_matrix()",
        "larger RTX repeats stayed below the 100 ms",
    ),
    "docs/app_engine_support_matrix.md": (
        "The machine-readable source of truth is `rtdsl.rtx_public_wording_matrix()`",
        "public_wording_blocked",
        "blocked_for_public_speedup_wording",
        "larger repeat clears the 100 ms timing floor",
    ),
    "docs/application_catalog.md": (
        "is not by itself a NVIDIA RT-core claim",
        "These rows are claim-review candidates, not release authorization and not",
        "rtdsl.rtx_public_wording_matrix()",
        "robot_collision_screening / prepared_pose_flags",
        "remains blocked for public RTX speedup wording",
    ),
    "docs/release_facing_examples.md": (
        "`--backend optix` is a backend-selection flag, not an automatic NVIDIA RT-core",
        "These commands are bounded sub-paths, not broad speedup claims",
        "robot_collision_screening / prepared_pose_flags",
        "remains excluded from public",
        "100 ms",
    ),
    "docs/rtdl_feature_guide.md": (
        "`--backend optix` is not enough for a public",
        "rtdsl.rtx_public_wording_matrix()",
        "public_wording_blocked",
        "100 ms public-review timing floor",
    ),
    "docs/quick_tutorial.md": (
        "`--backend optix` selects an OptiX-capable path; it is not by itself",
        "use `--require-rt-core` only in claim-sensitive app runs",
        "docs/application_catalog.md",
        "docs/app_engine_support_matrix.md",
    ),
}


def build_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel_path, phrases in REQUIRED_PHRASES.items():
        path = ROOT / rel_path
        exists = path.exists()
        text = path.read_text(encoding="utf-8") if exists else ""
        missing = [phrase for phrase in phrases if phrase not in text]
        rows.append(
            {
                "path": rel_path,
                "exists": exists,
                "required_phrase_count": len(phrases),
                "missing_phrases": missing,
                "status": "ok" if exists and not missing else "missing_required_boundary",
            }
        )
    failing = [row for row in rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "doc_count": len(rows),
        "passing_doc_count": len(rows) - len(failing),
        "failing_doc_count": len(failing),
        "valid": not failing,
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "boundary": (
            "This audit checks release-facing docs for RTX claim-boundary wording. "
            "It does not authorize public speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1020 Public Docs RTX Boundary Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- docs checked: `{payload['doc_count']}`",
        f"- passing docs: `{payload['passing_doc_count']}`",
        f"- failing docs: `{payload['failing_doc_count']}`",
        f"- current public wording source: `{payload['current_public_wording_source']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| Doc | Status | Missing phrases |",
        "|---|---|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} |"
        )
    missing_rows = [row for row in payload["rows"] if row["missing_phrases"]]
    if missing_rows:
        lines.extend(["", "## Missing Detail", ""])
        for row in missing_rows:
            lines.append(f"### {row['path']}")
            lines.append("")
            for phrase in row["missing_phrases"]:
                lines.append(f"- `{phrase}`")
            lines.append("")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit public docs for RTX claim-boundary wording.")
    parser.add_argument("--output-json", default="docs/reports/goal1020_public_docs_rtx_boundary_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1020_public_docs_rtx_boundary_audit_2026-04-26.md")
    args = parser.parse_args()

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
