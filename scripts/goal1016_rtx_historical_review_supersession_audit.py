#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1016 RTX historical review supersession audit"

HISTORICAL_REVIEW_FILES = [
    "docs/reports/goal978_claude_review_2026-04-26.md",
    "docs/reports/goal979_claude_review_2026-04-26.md",
    "docs/reports/goal983_claude_review_2026-04-26.md",
]

SUPERSEDING_PUBLIC_WORDING_FILES = [
    "docs/reports/goal1014_public_wording_pipeline_source_sync_2026-04-26.md",
    "docs/reports/goal1015_upstream_speedup_evidence_public_wording_sync_2026-04-26.md",
    "docs/reports/goal1014_two_ai_consensus_2026-04-26.md",
    "docs/reports/goal1015_two_ai_consensus_2026-04-26.md",
]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def build_audit() -> dict[str, Any]:
    superseding_text = "\n".join(_read(path) for path in SUPERSEDING_PUBLIC_WORDING_FILES)
    superseding_ok = (
        "robot_collision_screening" in superseding_text
        and "public_wording_blocked" in superseding_text
        and "rtdsl.rtx_public_wording_matrix()" in superseding_text
    )

    rows: list[dict[str, Any]] = []
    for path in HISTORICAL_REVIEW_FILES:
        text = _read(path)
        mentions_robot_candidate = (
            "robot_collision_screening" in text
            and "candidate_for_separate_2ai_public_claim_review" in text
        )
        carries_current_block = "public_wording_blocked" in text
        rows.append(
            {
                "path": path,
                "mentions_robot_candidate": mentions_robot_candidate,
                "carries_current_public_wording_block": carries_current_block,
                "requires_supersession_context": mentions_robot_candidate and not carries_current_block,
                "superseded_by": SUPERSEDING_PUBLIC_WORDING_FILES if mentions_robot_candidate and not carries_current_block else [],
                "current_public_wording_status": "public_wording_blocked" if mentions_robot_candidate else None,
            }
        )

    required = [row for row in rows if row["requires_supersession_context"]]
    return {
        "goal": GOAL,
        "date": DATE,
        "historical_review_count": len(rows),
        "historical_review_requires_supersession_count": len(required),
        "superseding_public_wording_files": SUPERSEDING_PUBLIC_WORDING_FILES,
        "superseding_public_wording_ok": superseding_ok,
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "boundary": (
            "This audit does not rewrite historical external review text. It records that older review files "
            "are historical and that release-facing wording is superseded by Goal1014/Goal1015 and "
            "rtdsl.rtx_public_wording_matrix()."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1016 RTX Historical Review Supersession Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- historical reviews checked: `{payload['historical_review_count']}`",
        f"- historical reviews requiring supersession context: `{payload['historical_review_requires_supersession_count']}`",
        f"- superseding public wording files valid: `{payload['superseding_public_wording_ok']}`",
        f"- current public wording source: `{payload['current_public_wording_source']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Historical Review Rows",
        "",
        "| Historical file | Mentions robot candidate? | Carries current block? | Requires supersession context? | Current status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['mentions_robot_candidate']}` | "
            f"`{row['carries_current_public_wording_block']}` | "
            f"`{row['requires_supersession_context']}` | "
            f"`{row['current_public_wording_status'] or ''}` |"
        )
    lines.extend(
        [
            "",
            "## Superseding Files",
            "",
        ]
    )
    for path in payload["superseding_public_wording_files"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Release-Facing Boundary",
            "",
            "`robot_collision_screening` remains `public_wording_blocked` for public speedup wording. "
            "Historical candidate classifications in older review files are not release-facing wording.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit historical RTX review files against superseding public wording docs.")
    parser.add_argument("--output-json", default="docs/reports/goal1016_rtx_historical_review_supersession_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1016_rtx_historical_review_supersession_audit_2026-04-26.md")
    args = parser.parse_args()

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["superseding_public_wording_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
