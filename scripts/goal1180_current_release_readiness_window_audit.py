#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1180 current release-readiness window audit"

REQUIRED_FILES: tuple[str, ...] = (
    "docs/reports/goal1177_live_pod_goal1176_goal1170_recovery_intake_2026-04-30.md",
    "docs/reports/goal1177_gemini_live_pod_recovery_review_2026-04-30.md",
    "docs/reports/goal1177_two_ai_consensus_2026-04-30.md",
    "docs/reports/goal1178_goal1177_public_status_sync_audit_2026-04-30.md",
    "docs/reports/goal1178_gemini_public_status_sync_review_2026-04-30.md",
    "docs/reports/goal1178_two_ai_consensus_2026-04-30.md",
    "docs/reports/goal1179_public_docs_goal1177_boundary_audit_2026-04-30.md",
    "docs/reports/goal1179_gemini_public_doc_boundary_review_2026-04-30.md",
    "docs/reports/goal1179_two_ai_consensus_2026-04-30.md",
)

CURRENT_SURFACE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/application_catalog.md": (
        "Goal1177",
        "external-review input only",
        "does not authorize public speedup wording",
    ),
    "docs/release_facing_examples.md": (
        "Goal1177",
        "Neither goal adds a new reviewed public wording row",
        "These commands are bounded sub-paths, not broad speedup claims",
    ),
    "docs/rtdl_feature_guide.md": (
        "Goal1177",
        "Neither goal adds a new reviewed public wording row",
        "authorizes public speedup wording",
    ),
    "docs/quick_tutorial.md": (
        "Goal1177",
        "external-review input only",
        "do not authorize",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "Goal1177",
        "Goal1177 does not add a new reviewed public wording row",
        "reviewed public RTX sub-path wording rows: `13`",
        "Goal1208 adds exactly one reviewed public wording row",
    ),
    "docs/app_engine_support_matrix.md": (
        "Goal1177",
        "Goal1177 and Goal1184 do not add any new reviewed public",
        "Current reviewed public wording rows after Goal1263: `13`",
    ),
    "src/rtdsl/app_support_matrix.py": (
        "Goal1177",
        "external-review input only",
        "public wording still requires same-semantics baseline review",
    ),
    "scripts/goal947_v1_rtx_app_status_page.py": (
        "Goal1177",
        "external-review input only",
        "does not authorize new public wording",
    ),
}

GUARDRAIL_SCRIPT_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "scripts/goal1178_goal1177_public_status_sync_audit.py": (
        "Goal1177",
        "without promoting public",
        "FORBIDDEN_DOC_PHRASES",
    ),
    "scripts/goal1179_public_docs_goal1177_boundary_audit.py": (
        "Goal1177",
        "must not become public RTX speedup wording",
        "FORBIDDEN_PHRASES",
    ),
}

CONSENSUS_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "docs/reports/goal1177_two_ai_consensus_2026-04-30.md": (
        "Consensus Verdict",
        "ACCEPT_FOR_EXTERNAL_REVIEW_INPUT",
        "Public RTX speedup wording remains `NOT_AUTHORIZED`",
    ),
    "docs/reports/goal1178_two_ai_consensus_2026-04-30.md": (
        "Consensus Verdict",
        "ACCEPT",
        "The reviewed public RTX sub-path wording",
        "row count remains `10`",
    ),
    "docs/reports/goal1179_two_ai_consensus_2026-04-30.md": (
        "Consensus Verdict",
        "ACCEPT",
        "The reviewed public RTX sub-path wording row count remains `10`",
    ),
}

FORBIDDEN_PUBLIC_SURFACE_PHRASES: tuple[str, ...] = (
    "Goal1177 authorizes public",
    "Goal1177 authorized public",
    "Goal1177 public speedup",
    "Goal1177 adds public speedup",
    "Goal1177 adds a reviewed public wording row",
    "no readiness pod needed",
)


def _check_file_requirements(rel_path: str, phrases: tuple[str, ...]) -> dict[str, Any]:
    path = ROOT / rel_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    missing = [phrase for phrase in phrases if phrase not in text]
    forbidden = [phrase for phrase in FORBIDDEN_PUBLIC_SURFACE_PHRASES if phrase in text]
    return {
        "path": rel_path,
        "exists": exists,
        "required_phrase_count": len(phrases),
        "missing_phrases": missing,
        "forbidden_phrases": forbidden,
        "status": "ok" if exists and not missing and not forbidden else "surface_failure",
    }


def _check_consensus(rel_path: str, phrases: tuple[str, ...]) -> dict[str, Any]:
    path = ROOT / rel_path
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    missing = [phrase for phrase in phrases if phrase not in text]
    return {
        "path": rel_path,
        "exists": exists,
        "required_phrase_count": len(phrases),
        "missing_phrases": missing,
        "status": "ok" if exists and not missing else "consensus_failure",
    }


def build_audit() -> dict[str, Any]:
    file_rows = [{"path": rel_path, "exists": (ROOT / rel_path).exists()} for rel_path in REQUIRED_FILES]
    missing_files = [row["path"] for row in file_rows if not row["exists"]]
    surface_rows = [
        _check_file_requirements(rel_path, phrases)
        for rel_path, phrases in CURRENT_SURFACE_REQUIREMENTS.items()
    ]
    guardrail_rows = [
        _check_consensus(rel_path, phrases)
        for rel_path, phrases in GUARDRAIL_SCRIPT_REQUIREMENTS.items()
    ]
    consensus_rows = [
        _check_consensus(rel_path, phrases)
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
        "consensus_file_count": len(consensus_rows),
        "consensus_failure_count": len(consensus_failures),
        "guardrail_script_count": len(guardrail_rows),
        "guardrail_failure_count": len(guardrail_failures),
        "required_files": file_rows,
        "surface_rows": surface_rows,
        "guardrail_rows": guardrail_rows,
        "consensus_rows": consensus_rows,
        "boundary": (
            "Goal1180 audits only the current release-readiness surface for the "
            "Goal1177-Goal1179 window. Historical reports are intentionally excluded; "
            "changed conclusions must be represented by supersession reports and current docs."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1180 Current Release-Readiness Window Audit",
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
        f"- guardrail scripts checked: `{payload['guardrail_script_count']}`",
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
    lines.extend(["", "## Guardrail Scripts", "", "| File | Status | Missing |", "| --- | --- | ---: |"])
    for row in payload["guardrail_rows"]:
        lines.append(f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} |")
    lines.extend(["", "## Consensus Chain", "", "| File | Status | Missing |", "| --- | --- | ---: |"])
    for row in payload["consensus_rows"]:
        lines.append(f"| `{row['path']}` | `{row['status']}` | {len(row['missing_phrases'])} |")
    if payload["missing_files"]:
        lines.extend(["", "## Missing Files", ""])
        lines.extend(f"- `{path}`" for path in payload["missing_files"])
    failures = [row for row in payload["surface_rows"] if row["status"] != "ok"]
    failures.extend(row for row in payload["guardrail_rows"] if row["status"] != "ok")
    failures.extend(row for row in payload["consensus_rows"] if row["status"] != "ok")
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
    parser = argparse.ArgumentParser(description="Audit current Goal1177-1179 release-readiness surface.")
    parser.add_argument("--output-json", default="docs/reports/goal1180_current_release_readiness_window_audit_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1180_current_release_readiness_window_audit_2026-04-30.md")
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
