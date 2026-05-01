#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL_RANGE = range(1100, 1120)


def _glob_one(pattern: str) -> str | None:
    matches = sorted((ROOT / "docs/reports").glob(pattern))
    if not matches:
        return None
    return str(matches[0].relative_to(ROOT))


def build_audit() -> dict[str, Any]:
    rows = []
    for goal_id in GOAL_RANGE:
        prefix = f"goal{goal_id}"
        consensus = _glob_one(f"{prefix}_two_ai_consensus_2026-04-29.md")
        external_review = (
            _glob_one(f"{prefix}_second_ai_review_2026-04-29.md")
            or _glob_one(f"{prefix}_claude_review_2026-04-29.md")
            or _glob_one(f"{prefix}_gemini_review_2026-04-29.md")
        )
        primary_report = next(
            (
                str(path.relative_to(ROOT))
                for path in sorted((ROOT / "docs/reports").glob(f"{prefix}_*_2026-04-29.md"))
                if "two_ai_consensus" not in path.name
                and "second_ai_review" not in path.name
                and "claude_review" not in path.name
                and "gemini_review" not in path.name
            ),
            None,
        )
        closed = bool(consensus and external_review and primary_report)
        rows.append(
            {
                "goal": prefix,
                "primary_report": primary_report,
                "external_review": external_review,
                "two_ai_consensus": consensus,
                "closed": closed,
            }
        )
    blockers = [row["goal"] for row in rows if not row["closed"]]
    return {
        "goal": "Goal1120 recent RTX-readiness consensus audit",
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
            "This audit verifies saved review/consensus artifacts for recent RTX-readiness goals. "
            "It does not rerun cloud, authorize release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Goal1120 Recent Goal Consensus Audit",
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
        "| Goal | Closed | Primary report | External-style review | Two-AI consensus |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['goal']}` | `{row['closed']}` | "
            f"`{row['primary_report'] or ''}` | `{row['external_review'] or ''}` | `{row['two_ai_consensus'] or ''}` |"
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
    parser = argparse.ArgumentParser(description="Audit recent RTX-readiness goals for 2-AI consensus artifacts.")
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs/reports/goal1120_recent_goal_consensus_audit_2026-04-29.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs/reports/goal1120_recent_goal_consensus_audit_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_audit()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
