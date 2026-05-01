#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1178 Goal1177 public RTX status sync audit"

DOC_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/v1_0_rtx_app_status.md": (
        "Goal1177",
        "external-review input only",
        "Goal1177 does not add a new reviewed public wording row",
        "does not authorize new public wording",
        "reviewed public RTX sub-path wording rows: `11`",
        "Goal1208 adds exactly one reviewed public wording row",
        "broad or whole-app public speedup claim authorized: `False`",
    ),
    "docs/app_engine_support_matrix.md": (
        "Goal1164-Goal1177",
        "external-review input only",
        "Goal1177 does not add any new reviewed public",
        "public_wording_reviewed",
        "not whole-app speedup",
    ),
    "docs/reports/goal1177_two_ai_consensus_2026-04-30.md": (
        "ACCEPT_FOR_EXTERNAL_REVIEW_INPUT",
        "Public RTX speedup wording remains `NOT_AUTHORIZED`",
        "timing-only artifacts",
        "candidate-count mismatch",
    ),
    "docs/reports/goal1177_gemini_live_pod_recovery_review_2026-04-30.md": (
        "VERDICT: ACCEPT",
        "does not authorize public RTX speedup wording",
        "timing-only",
        "external-review input",
    ),
}

FORBIDDEN_DOC_PHRASES: tuple[str, ...] = (
    "Goal1177 authorizes public",
    "Goal1177 authorized public",
    "Goal1177 reviewed public RTX sub-path wording rows: `11`",
    "Goal1177 public speedup",
)


def build_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel_path, phrases in DOC_REQUIREMENTS.items():
        path = ROOT / rel_path
        exists = path.exists()
        text = path.read_text(encoding="utf-8") if exists else ""
        missing = [phrase for phrase in phrases if phrase not in text]
        forbidden = [phrase for phrase in FORBIDDEN_DOC_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": exists,
                "required_phrase_count": len(phrases),
                "missing_phrases": missing,
                "forbidden_phrases": forbidden,
                "status": "ok" if exists and not missing and not forbidden else "boundary_sync_failure",
            }
        )
    failing = [row for row in rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not failing,
        "doc_count": len(rows),
        "passing_doc_count": len(rows) - len(failing),
        "failing_doc_count": len(failing),
        "rows": rows,
        "boundary": (
            "This audit checks that Goal1177 is reflected as accepted clean-source "
            "RTX evidence for external-review input only, without promoting public "
            "RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1178 Goal1177 Public RTX Status Sync Audit",
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
        "",
        "## Rows",
        "",
        "| Doc | Status | Missing | Forbidden |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} | {len(row['forbidden_phrases'])} |"
        )
    failing = [row for row in payload["rows"] if row["status"] != "ok"]
    if failing:
        lines.extend(["", "## Failure Detail", ""])
        for row in failing:
            lines.append(f"### {row['path']}")
            lines.append("")
            for phrase in row["missing_phrases"]:
                lines.append(f"- missing: `{phrase}`")
            for phrase in row["forbidden_phrases"]:
                lines.append(f"- forbidden: `{phrase}`")
            lines.append("")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Goal1177 public RTX status sync.")
    parser.add_argument("--output-json", default="docs/reports/goal1178_goal1177_public_status_sync_audit_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1178_goal1177_public_status_sync_audit_2026-04-30.md")
    args = parser.parse_args()

    payload = build_audit()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "json": str(output_json), "md": str(output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
