#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1218 v0.9.8 release-authorization gate"

REQUIRED_READY_FILES: tuple[str, ...] = (
    "docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md",
    "docs/reports/goal1216_two_ai_consensus_2026-05-01.md",
    "docs/reports/goal1217_version_marker_current_release_sync_2026-05-01.md",
    "docs/reports/goal1217_gemini_version_marker_sync_review_2026-05-01.md",
    "docs/reports/goal1217_two_ai_consensus_2026-05-01.md",
)

REQUIRED_READY_PHRASES: dict[str, tuple[str, ...]] = {
    "docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md": (
        "valid: `True`",
        "recommendation: `local_release_candidate_ready_for_final_external_release_decision`",
        "pod needed now: `False`",
        "Goal1214 full unittest discovery",
        "Goal1215 release-surface docs",
    ),
    "docs/reports/goal1216_two_ai_consensus_2026-05-01.md": (
        "`ACCEPT`",
        "Gemini CLI",
        "No immediate pod is required",
    ),
    "docs/reports/goal1217_two_ai_consensus_2026-05-01.md": (
        "`ACCEPT`",
        "`v0.9.6`",
        "does not authorize, tag, publish, or claim `v0.9.8`",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "reviewed public RTX sub-path wording rows: `13`",
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "broad or whole-app public speedup claim authorized: `False`",
    ),
}

RELEASE_PACKAGE_FILES: tuple[str, ...] = (
    "docs/release_reports/v0_9_8/README.md",
    "docs/release_reports/v0_9_8/release_statement.md",
    "docs/release_reports/v0_9_8/support_matrix.md",
    "docs/release_reports/v0_9_8/audit_report.md",
    "docs/release_reports/v0_9_8/tag_preparation.md",
)

RELEASE_PACKAGE_REVIEW_FILES: tuple[str, ...] = (
    "docs/reports/goal1219_v0_9_8_release_package_2026-05-01.md",
    "docs/reports/goal1219_gemini_v0_9_8_release_package_review_2026-05-01.md",
    "docs/reports/goal1219_two_ai_consensus_2026-05-01.md",
)

FINAL_AUTHORIZATION_FILES: tuple[str, ...] = (
    "docs/reports/goal1220_v0_9_8_final_authorization_2026-05-01.md",
    "docs/reports/goal1220_two_ai_consensus_2026-05-01.md",
)

FORBIDDEN_PUBLIC_PHRASES: tuple[str, ...] = (
    "database_analytics / public speedup",
    "polygon_set_jaccard / public speedup",
    "reviewed public RTX sub-path wording rows: `10`",
    "Goal1208 authorizes whole-app",
)


def _read(rel_path: str) -> str:
    path = ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _file_rows(paths: tuple[str, ...]) -> list[dict[str, Any]]:
    return [{"path": path, "exists": (ROOT / path).exists()} for path in paths]


def _phrase_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path, phrases in REQUIRED_READY_PHRASES.items():
        text = _read(rel_path)
        missing = [phrase for phrase in phrases if phrase not in text]
        forbidden = [phrase for phrase in FORBIDDEN_PUBLIC_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": bool(text),
                "missing_phrases": missing,
                "forbidden_phrases": forbidden,
                "status": "ok" if text and not missing and not forbidden else "failure",
            }
        )
    return rows


def build_gate() -> dict[str, Any]:
    ready_files = _file_rows(REQUIRED_READY_FILES)
    package_files = _file_rows(RELEASE_PACKAGE_FILES)
    package_review_files = _file_rows(RELEASE_PACKAGE_REVIEW_FILES)
    final_authorization_files = _file_rows(FINAL_AUTHORIZATION_FILES)
    phrase_rows = _phrase_rows()
    missing_ready = [row["path"] for row in ready_files if not row["exists"]]
    phrase_failures = [row for row in phrase_rows if row["status"] != "ok"]
    missing_package = [row["path"] for row in package_files if not row["exists"]]
    missing_package_review = [row["path"] for row in package_review_files if not row["exists"]]
    missing_final_authorization = [row["path"] for row in final_authorization_files if not row["exists"]]
    version = _read("VERSION").strip()
    release_evidence_ready = not missing_ready and not phrase_failures and version in {"v0.9.6", "v0.9.8", "v1.0"}
    release_package_ready = not missing_package
    release_package_review_ready = not missing_package_review
    final_authorization_ready = not missing_final_authorization
    release_authorized = (
        release_evidence_ready
        and release_package_ready
        and release_package_review_ready
        and final_authorization_ready
    )
    blockers: list[str] = []
    if not release_evidence_ready:
        blockers.append("release_candidate_evidence_or_version_marker_incomplete")
    if not release_package_ready:
        blockers.append("v0_9_8_release_package_missing")
    if release_package_ready and not release_package_review_ready:
        blockers.append("v0_9_8_release_package_review_pending")
    if release_evidence_ready and release_package_ready and release_package_review_ready and not final_authorization_ready:
        blockers.append("v0_9_8_final_authorization_pending")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid_gate": release_evidence_ready,
        "release_authorized": release_authorized,
        "pod_needed_before_authorization": False,
        "recommended_next_action": (
            "write_v0_9_8_release_package_and_seek_final_authorization"
            if release_evidence_ready and not release_package_ready
            else "seek_external_review_of_v0_9_8_release_package"
            if release_evidence_ready and release_package_ready and not release_package_review_ready
            else "seek_final_maintainer_authorization"
            if release_evidence_ready
            and release_package_ready
            and release_package_review_ready
            and not final_authorization_ready
            else "authorize_release_action"
            if release_authorized
            else "repair_release_candidate_evidence"
        ),
        "blockers": blockers,
        "version_marker": version,
        "ready_files": ready_files,
        "phrase_rows": phrase_rows,
        "release_package_files": package_files,
        "release_package_review_files": package_review_files,
        "final_authorization_files": final_authorization_files,
        "current_public_state": {
            "reviewed_public_rtx_wording_rows": 13,
            "road_hazard_new_public_row": "road_hazard_screening / prepared_native_compact_summary_40k",
            "database_analytics_public_speedup": "not_reviewed",
            "polygon_set_jaccard_public_speedup": "not_reviewed",
        },
        "hardware_evidence_decision": (
            "No additional pod run is required before the release-authorization "
            "paperwork gate. Existing Goal1206/Goal1208 RTX evidence is sufficient "
            "for the currently bounded public claims. If the release manager wants "
            "fresh hardware replay anyway, it should be one batched final RTX run."
        ),
        "boundary": (
            "Goal1218 is an authorization gate, not a release action. It does not "
            "tag, publish, push, upload packages, or bump VERSION to v0.9.8."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1218 v0.9.8 Release-Authorization Gate",
        "",
        f"Date: {payload['date']}",
        "",
        "## Verdict",
        "",
        f"- valid gate evidence: `{payload['valid_gate']}`",
        f"- release authorized: `{payload['release_authorized']}`",
        f"- pod needed before authorization: `{payload['pod_needed_before_authorization']}`",
        f"- recommended next action: `{payload['recommended_next_action']}`",
        f"- version marker: `{payload['version_marker']}`",
        "",
        "## Blockers",
        "",
    ]
    if payload["blockers"]:
        lines.extend(f"- `{blocker}`" for blocker in payload["blockers"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Public Claim State",
            "",
            "- reviewed public RTX wording rows: `13`",
            "- new reviewed public row: `road_hazard_screening / prepared_native_compact_summary_40k`",
            "- `database_analytics` public speedup wording: `not_reviewed`",
            "- `polygon_set_jaccard` public speedup wording: `not_reviewed`",
            "",
            "## Hardware Evidence Decision",
            "",
            payload["hardware_evidence_decision"],
            "",
            "## Release Package Files",
            "",
            "| Path | Exists |",
            "| --- | --- |",
        ]
    )
    for row in payload["release_package_files"]:
        lines.append(f"| `{row['path']}` | `{row['exists']}` |")
    lines.extend(
        [
            "",
            "## Release Package Review Files",
            "",
            "| Path | Exists |",
            "| --- | --- |",
        ]
    )
    for row in payload["release_package_review_files"]:
        lines.append(f"| `{row['path']}` | `{row['exists']}` |")
    lines.extend(
        [
            "",
            "## Final Authorization Files",
            "",
            "| Path | Exists |",
            "| --- | --- |",
        ]
    )
    for row in payload["final_authorization_files"]:
        lines.append(f"| `{row['path']}` | `{row['exists']}` |")
    lines.extend(
        [
            "",
            "## Evidence Phrase Rows",
            "",
            "| Path | Status | Missing | Forbidden |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["phrase_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | "
            f"`{len(row['missing_phrases'])}` | `{len(row['forbidden_phrases'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit v0.9.8 release authorization readiness.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1218_v0_9_8_release_authorization_gate_2026-05-01.md",
    )
    args = parser.parse_args()
    payload = build_gate()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    output_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["valid_gate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
