#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports"
DATE = "2026-04-29"
GOAL_RANGE = range(1120, 1139)


def _first(patterns: list[str]) -> str | None:
    for pattern in patterns:
        matches = sorted(REPORTS.glob(pattern))
        if matches:
            return str(matches[0].relative_to(ROOT))
    return None


def _primary_report(goal: str) -> str | None:
    excluded_tokens = (
        "two_ai_consensus",
        "three_ai_consensus",
        "second_ai_review",
        "claude_review",
        "gemini_review",
    )
    for path in sorted(REPORTS.glob(f"{goal}_*_2026-04-29.md")):
        if not any(token in path.name for token in excluded_tokens):
            return str(path.relative_to(ROOT))
    return None


def build_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for goal_id in GOAL_RANGE:
        goal = f"goal{goal_id}"
        primary = _primary_report(goal)
        external = _first(
            [
                f"{goal}_second_ai_review_2026-04-29.md",
                f"{goal}_claude_review_2026-04-29.md",
                f"{goal}_gemini_review_2026-04-29.md",
                f"{goal}_*_claude_review_2026-04-29.md",
                f"{goal}_*_gemini_review_2026-04-29.md",
            ]
        )
        consensus = _first(
            [
                f"{goal}_two_ai_consensus_2026-04-29.md",
                f"{goal}_three_ai_consensus_2026-04-29.md",
            ]
        )
        closed = bool(primary and external and consensus)
        rows.append(
            {
                "goal": goal,
                "primary_report": primary,
                "external_review": external,
                "consensus": consensus,
                "closed": closed,
            }
        )
    blockers = [row["goal"] for row in rows if not row["closed"]]
    return {
        "goal": "Goal1139 current-window consensus audit",
        "date": DATE,
        "audited_goals": [f"goal{goal_id}" for goal_id in GOAL_RANGE],
        "rows": rows,
        "summary": {
            "goal_count": len(rows),
            "closed_count": sum(1 for row in rows if row["closed"]),
            "blocker_count": len(blockers),
            "blockers": blockers,
        },
        "valid": not blockers,
        "boundary": (
            "This audit checks saved primary reports, external Claude/Gemini-style reviews, "
            "and two- or three-AI consensus files for the current RTX-readiness window. "
            "It does not rerun cloud, authorize release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Goal1139 Current-Window Consensus Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Goals audited: `{summary['goal_count']}`",
        f"- Closed with required artifacts: `{summary['closed_count']}`",
        f"- Blockers: `{summary['blocker_count']}`",
        "",
        "## Rows",
        "",
        "| Goal | Closed | Primary report | External review | Consensus |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['goal']}` | `{row['closed']}` | "
            f"`{row['primary_report'] or ''}` | "
            f"`{row['external_review'] or ''}` | "
            f"`{row['consensus'] or ''}` |"
        )
    lines.extend(["", "## Blockers", ""])
    if summary["blockers"]:
        for blocker in summary["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit current RTX-readiness goals for 2+ AI consensus artifacts.")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "docs/reports/goal1139_current_window_consensus_audit_2026-04-29.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "docs/reports/goal1139_current_window_consensus_audit_2026-04-29.md",
    )
    args = parser.parse_args(argv)
    payload = build_audit()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
