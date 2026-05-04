#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1186 current release-readiness after Goal1185 audit"

REQUIRED_FILES: tuple[str, ...] = (
    "docs/reports/goal1184_live_pod_goal1182_intake_2026-04-30.md",
    "docs/reports/goal1184_claude_live_pod_intake_review_2026-04-30.md",
    "docs/reports/goal1184_two_ai_consensus_2026-04-30.md",
    "docs/reports/goal1185_goal1184_public_status_sync_audit_2026-04-30.md",
    "docs/reports/goal1185_claude_public_status_sync_review_2026-04-30.md",
    "docs/reports/goal1185_two_ai_consensus_2026-04-30.md",
)

CURRENT_SURFACE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "README.md": (
        "Goal1184",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "Goal1177 does not add a new reviewed public wording row",
    ),
    "docs/application_catalog.md": (
        "Goal1184",
        "external-review input only",
        "Neither goal adds a new reviewed",
        "Goal1177 does not add",
    ),
    "docs/release_facing_examples.md": (
        "Goal1184",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "These commands are bounded sub-paths, not broad speedup claims",
    ),
    "docs/rtdl_feature_guide.md": (
        "Goal1184",
        "external-review input only",
        "Neither goal adds a new reviewed public wording row",
        "rtdsl.rtx_public_wording_matrix()",
    ),
    "docs/quick_tutorial.md": (
        "Goal1177 and Goal1184",
        "external-review input only",
        "do not authorize",
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
        "Goal1177 and Goal1184 do not add any new reviewed public",
        "Current reviewed public wording rows after Goal1224: `12`",
    ),
    "src/rtdsl/app_support_matrix.py": (
        "Goal1184",
        "external-review input only",
        "does not authorize new public wording",
    ),
    "scripts/goal947_v1_rtx_app_status_page.py": (
        "Goal1184",
        "external-review input only",
        "does not authorize new public wording",
    ),
}

GUARDRAIL_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "scripts/goal1185_goal1184_public_status_sync_audit.py": (
        "Goal1184",
        "external-review input only",
        "FORBIDDEN_PHRASES",
    ),
    "tests/goal1185_goal1184_public_status_sync_audit_test.py": (
        "Goal1184 public speedup",
        "reviewed public RTX sub-path wording rows: `12`",
        "public_wording_row_count_expected",
    ),
}

CONSENSUS_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/reports/goal1184_two_ai_consensus_2026-04-30.md": (
        "ACCEPT_FOR_EXTERNAL_REVIEW_INPUT",
        "does not authorize public speedup wording",
        "timing-only artifacts",
    ),
    "docs/reports/goal1185_claude_public_status_sync_review_2026-04-30.md": (
        "VERDICT: ACCEPT",
        "No new public speedup claim",
        "Goal1177 guardrails intact",
    ),
    "docs/reports/goal1185_two_ai_consensus_2026-04-30.md": (
        "ACCEPT",
        "Goal1184 as external-review input only",
        "Public wording row count remains `10`",
    ),
}

FORBIDDEN_PUBLIC_SURFACE_PHRASES: tuple[str, ...] = (
    "Goal1184 authorizes public",
    "Goal1184 authorized public",
    "Goal1184 public speedup",
    "Goal1184 adds public speedup",
    "Goal1184 adds a new reviewed public wording row",
    "broad or whole-app public speedup claim authorized: `True`",
)


def _check_file_requirements(
    rel_path: str,
    phrases: tuple[str, ...],
    status_name: str,
    *,
    check_forbidden: bool,
) -> dict[str, Any]:
    path = ROOT / rel_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    missing = [phrase for phrase in phrases if phrase not in text]
    forbidden = [phrase for phrase in FORBIDDEN_PUBLIC_SURFACE_PHRASES if phrase in text] if check_forbidden else []
    return {
        "path": rel_path,
        "exists": exists,
        "required_phrase_count": len(phrases),
        "missing_phrases": missing,
        "forbidden_phrases": forbidden,
        "status": "ok" if exists and not missing and not forbidden else status_name,
    }


def build_audit() -> dict[str, Any]:
    file_rows = [{"path": rel_path, "exists": (ROOT / rel_path).exists()} for rel_path in REQUIRED_FILES]
    missing_files = [row["path"] for row in file_rows if not row["exists"]]
    surface_rows = [
        _check_file_requirements(rel_path, phrases, "surface_failure", check_forbidden=True)
        for rel_path, phrases in CURRENT_SURFACE_REQUIREMENTS.items()
    ]
    guardrail_rows = [
        _check_file_requirements(rel_path, phrases, "guardrail_failure", check_forbidden=False)
        for rel_path, phrases in GUARDRAIL_REQUIREMENTS.items()
    ]
    consensus_rows = [
        _check_file_requirements(rel_path, phrases, "consensus_failure", check_forbidden=False)
        for rel_path, phrases in CONSENSUS_REQUIREMENTS.items()
    ]
    surface_failures = [row for row in surface_rows if row["status"] != "ok"]
    guardrail_failures = [row for row in guardrail_rows if row["status"] != "ok"]
    consensus_failures = [row for row in consensus_rows if row["status"] != "ok"]
    valid = not missing_files and not surface_failures and not guardrail_failures and not consensus_failures
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "required_file_count": len(file_rows),
        "missing_files": missing_files,
        "surface_file_count": len(surface_rows),
        "surface_failure_count": len(surface_failures),
        "guardrail_file_count": len(guardrail_rows),
        "guardrail_failure_count": len(guardrail_failures),
        "consensus_file_count": len(consensus_rows),
        "consensus_failure_count": len(consensus_failures),
        "required_files": file_rows,
        "surface_rows": surface_rows,
        "guardrail_rows": guardrail_rows,
        "consensus_rows": consensus_rows,
        "boundary": (
            "Goal1186 audits the current release-readiness surface after Goal1184/Goal1185. "
            "Goal1184 may be recorded only as external-review input. Public RTX wording "
            "row count is now 12 after later reviewed bounded promotions through Goal1224; "
            "Goal1177 and Goal1184 do not add new public wording rows."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1186 Current Release-Readiness After Goal1185 Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- required files: `{payload['required_file_count']}`",
        f"- missing files: `{len(payload['missing_files'])}`",
        f"- current-surface files checked: `{payload['surface_file_count']}`",
        f"- current-surface failures: `{payload['surface_failure_count']}`",
        f"- guardrail files checked: `{payload['guardrail_file_count']}`",
        f"- guardrail failures: `{payload['guardrail_failure_count']}`",
        f"- consensus files checked: `{payload['consensus_file_count']}`",
        f"- consensus failures: `{payload['consensus_failure_count']}`",
        "",
        "## Current Surface",
        "",
        "| File | Status | Missing | Forbidden |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in payload["surface_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} | {len(row['forbidden_phrases'])} |"
        )
    lines.extend(["", "## Guardrails", "", "| File | Status | Missing | Forbidden |", "| --- | --- | ---: | ---: |"])
    for row in payload["guardrail_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} | {len(row['forbidden_phrases'])} |"
        )
    lines.extend(["", "## Consensus Chain", "", "| File | Status | Missing | Forbidden |", "| --- | --- | ---: | ---: |"])
    for row in payload["consensus_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} | {len(row['forbidden_phrases'])} |"
        )
    if payload["missing_files"]:
        lines.extend(["", "## Missing Files", ""])
        lines.extend(f"- `{path}`" for path in payload["missing_files"])
    failures = [row for group in ("surface_rows", "guardrail_rows", "consensus_rows") for row in payload[group] if row["status"] != "ok"]
    if failures:
        lines.extend(["", "## Failure Detail", ""])
        for row in failures:
            lines.append(f"### {row['path']}")
            lines.append("")
            for phrase in row.get("missing_phrases", []):
                lines.append(f"- missing: `{phrase}`")
            for phrase in row.get("forbidden_phrases", []):
                lines.append(f"- forbidden: `{phrase}`")
            lines.append("")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit current release-readiness surface after Goal1185.")
    parser.add_argument("--output-json", default="docs/reports/goal1186_current_release_readiness_after_goal1185_audit_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1186_current_release_readiness_after_goal1185_audit_2026-04-30.md")
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
