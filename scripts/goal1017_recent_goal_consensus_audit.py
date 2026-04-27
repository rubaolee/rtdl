#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1017 recent goal consensus audit"

GOALS = {
    1011: "RTX public wording matrix",
    1012: "status generator public wording sync",
    1013: "claim packet public wording sync",
    1014: "public wording pipeline source sync",
    1015: "upstream speedup evidence public wording sync",
    1016: "historical review supersession audit",
    1018: "Goal1007 repeat plan public wording sync",
    1020: "public docs RTX boundary refresh",
    1022: "history release drift audit",
    1023: "v0.9.6 history catch-up",
    1024: "final public-surface audit",
    1025: "pre-cloud RTX app batch readiness",
    1026: "pre-cloud RTX runner dry-run audit",
    1027: "public release hygiene v0.9.6 repair",
    1028: "A5000 RTX cloud batch evidence",
    1029: "RTX baseline promotion plan",
    1030: "local RTX baseline manifest",
    1031: "local baseline smoke runner",
    1032: "baseline manifest correction",
    1033: "SciPy threshold-count baseline",
    1034: "SciPy-enabled local baseline smoke",
    1035: "local baseline scale-ramp runner",
    1036: "outlier density-count oracle fix",
    1037: "local baseline manifest SciPy wording sync",
    1038: "next RTX ready-app rerun packet",
}

REQUIRED_SUFFIXES = {
    "claude_review": "claude",
    "gemini_review": "gemini",
    "two_ai_consensus": "consensus",
}


def _matching_files(goal: int, token: str) -> list[str]:
    reports = ROOT / "docs" / "reports"
    return sorted(
        str(path.relative_to(ROOT))
        for path in reports.glob(f"goal{goal}*{token}*2026-04-26.md")
    )


def build_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for goal, title in GOALS.items():
        files_by_requirement: dict[str, list[str]] = {}
        missing: list[str] = []
        for requirement, token in REQUIRED_SUFFIXES.items():
            matches = _matching_files(goal, token)
            files_by_requirement[requirement] = matches
            if not matches:
                missing.append(requirement)
        rows.append(
            {
                "goal": goal,
                "title": title,
                "status": "complete" if not missing else "missing_review_trail",
                "missing_requirements": missing,
                "files": files_by_requirement,
            }
        )

    incomplete = [row for row in rows if row["status"] != "complete"]
    return {
        "goal": GOAL,
        "date": DATE,
        "audited_goal_count": len(rows),
        "complete_goal_count": len(rows) - len(incomplete),
        "incomplete_goal_count": len(incomplete),
        "required_review_trail": sorted(REQUIRED_SUFFIXES),
        "rows": rows,
        "valid": not incomplete,
        "boundary": (
            "This audit checks that recent bounded goals have saved Claude review, "
            "Gemini review, and two-AI consensus files. It does not authorize public speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1017 Recent Goal Consensus Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- audited goals: `{payload['audited_goal_count']}`",
        f"- complete goals: `{payload['complete_goal_count']}`",
        f"- incomplete goals: `{payload['incomplete_goal_count']}`",
        f"- valid: `{payload['valid']}`",
        "",
        "## Rows",
        "",
        "| Goal | Title | Status | Claude | Gemini | Consensus |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        files = row["files"]
        lines.append(
            f"| {row['goal']} | {row['title']} | `{row['status']}` | "
            f"{len(files['claude_review'])} | {len(files['gemini_review'])} | "
            f"{len(files['two_ai_consensus'])} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit recent bounded goals for saved two-AI review trails.")
    parser.add_argument("--output-json", default="docs/reports/goal1017_recent_goal_consensus_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1017_recent_goal_consensus_audit_2026-04-26.md")
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
