#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1185 Goal1184 public RTX status sync audit"

DOC_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Goal1184",
        "Goal1182 RTX A4500 batch evidence",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "authorizes public speedup wording",
    ),
    "docs/application_catalog.md": (
        "Goal1184",
        "Goal1182 RTX A4500",
        "external-review input only",
        "Neither goal adds a new reviewed",
        "authorizes public speedup wording",
    ),
    "docs/release_facing_examples.md": (
        "Goal1184",
        "Goal1182 RTX A4500 batch evidence",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "These commands are bounded sub-paths, not broad speedup claims",
    ),
    "docs/rtdl_feature_guide.md": (
        "Goal1184",
        "Goal1182 RTX A4500 batch evidence",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "rtdsl.rtx_public_wording_matrix()",
    ),
    "docs/quick_tutorial.md": (
        "Goal1177 and Goal1184",
        "external-review input only",
        "do not authorize",
        "use `--require-rt-core` only in claim-sensitive app runs",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "Goal1184",
        "newer Goal1182 RTX A4500 batch accepted for external-review input (Goal1184): `True`",
        "Goal1184 does not add a new reviewed public wording row",
        "reviewed public RTX sub-path wording rows: `12`",
        "Goal1208 adds exactly one reviewed public wording row",
        "broad or whole-app public speedup claim authorized: `False`",
    ),
    "docs/app_engine_support_matrix.md": (
        "Goal1184",
        "Goal1182 RTX A4500",
        "external-review input only",
        "Goal1177 and Goal1184 do not add any new reviewed",
        "Current reviewed public wording rows after Goal1224: `12`",
    ),
    "docs/reports/goal1184_live_pod_goal1182_intake_2026-04-30.md": (
        "Goal1184 Live Pod Goal1182 Intake",
        "valid: `True`",
        "external-review input only",
        "not release authorization",
    ),
    "docs/reports/goal1184_claude_live_pod_intake_review_2026-04-30.md": (
        "VERDICT: ACCEPT",
        "external-review input",
        "does not authorize release",
        "does not authorize public speedup wording",
    ),
    "docs/reports/goal1184_two_ai_consensus_2026-04-30.md": (
        "ACCEPT_FOR_EXTERNAL_REVIEW_INPUT",
        "does not authorize release",
        "does not authorize public speedup wording",
        "timing-only artifacts",
    ),
}

FORBIDDEN_PHRASES: tuple[str, ...] = (
    "Goal1184 authorizes public",
    "Goal1184 authorized public",
    "Goal1184 public speedup",
    "Goal1184 adds public speedup",
    "Goal1184 adds a new reviewed public wording row",
    "Goal1184 reviewed public RTX sub-path wording rows: `12`",
)


def build_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel_path, phrases in DOC_REQUIREMENTS.items():
        path = ROOT / rel_path
        exists = path.exists()
        text = path.read_text(encoding="utf-8") if exists else ""
        missing = [phrase for phrase in phrases if phrase not in text]
        forbidden = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": exists,
                "required_phrase_count": len(phrases),
                "missing_phrases": missing,
                "forbidden_phrases": forbidden,
                "status": "ok" if exists and not missing and not forbidden else "goal1184_boundary_failure",
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
        "public_wording_row_count_expected": 12,
        "boundary": (
            "This audit checks that Goal1184 is reflected as newer Goal1182 RTX A4500 "
            "batch evidence for external-review input only. It must not become release "
            "authorization, public RTX speedup wording, or a new reviewed public wording row."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1185 Goal1184 Public RTX Status Sync Audit",
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
        f"- expected reviewed public wording rows: `{payload['public_wording_row_count_expected']}`",
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
    parser = argparse.ArgumentParser(description="Audit Goal1184 public RTX status sync.")
    parser.add_argument("--output-json", default="docs/reports/goal1185_goal1184_public_status_sync_audit_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1185_goal1184_public_status_sync_audit_2026-04-30.md")
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
