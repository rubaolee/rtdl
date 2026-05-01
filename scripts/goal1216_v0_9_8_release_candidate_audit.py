#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1216 v0.9.8 release-candidate audit"

REQUIRED_CLOSURE_FILES: dict[str, tuple[str, ...]] = {
    "Goal1204": (
        "docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.md",
        "docs/reports/goal1204_gemini_repaired_rtx_pod_packet_review_2026-05-01.md",
        "docs/reports/goal1204_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1205": (
        "docs/reports/goal1205_repaired_rtx_pod_intake_2026-05-01.md",
        "docs/reports/goal1205_gemini_repaired_rtx_pod_intake_fix_review_2026-05-01.md",
        "docs/reports/goal1205_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1206": (
        "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md",
        "docs/reports/goal1206_gemini_live_pod_merged_evidence_review_2026-05-01.md",
        "docs/reports/goal1206_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1207": (
        "docs/reports/goal1207_linux_embree_prefix_env_fix_2026-05-01.md",
        "docs/reports/goal1207_gemini_linux_embree_prefix_fix_review_2026-05-01.md",
        "docs/reports/goal1207_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1208": (
        "docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md",
        "docs/reports/goal1208_claude_public_wording_decision_review_2026-05-01.md",
        "docs/reports/goal1208_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1209": (
        "docs/reports/goal1209_public_status_sync_after_goal1208_2026-05-01.md",
        "docs/reports/goal1209_claude_public_status_sync_review_2026-05-01.md",
        "docs/reports/goal1209_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1210": (
        "docs/reports/goal1210_v0_9_8_release_readiness_audit_2026-05-01.md",
        "docs/reports/goal1210_claude_v0_9_8_release_readiness_review_2026-05-01.md",
        "docs/reports/goal1210_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1211": (
        "docs/reports/goal1211_local_release_window_smoke_2026-05-01.md",
        "docs/reports/goal1211_claude_local_release_window_smoke_review_2026-05-01.md",
        "docs/reports/goal1211_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1212": (
        "docs/reports/goal1212_public_release_hygiene_sweep_2026-05-01.md",
        "docs/reports/goal1212_claude_public_release_hygiene_sweep_review_2026-05-01.md",
        "docs/reports/goal1212_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1213": (
        "docs/reports/goal1213_full_discovery_stale_audit_repair_2026-05-01.md",
        "docs/reports/goal1213_claude_full_discovery_stale_audit_repair_review_2026-05-01.md",
        "docs/reports/goal1213_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1214": (
        "docs/reports/goal1214_full_local_discovery_after_goal1213_2026-05-01.md",
        "docs/reports/goal1214_claude_full_local_discovery_review_2026-05-01.md",
        "docs/reports/goal1214_two_ai_consensus_2026-05-01.md",
    ),
    "Goal1215": (
        "docs/reports/goal1215_release_surface_doc_audit_2026-05-01.md",
        "docs/reports/goal1215_claude_release_surface_doc_audit_review_2026-05-01.md",
        "docs/reports/goal1215_two_ai_consensus_2026-05-01.md",
    ),
}

REQUIRED_EVIDENCE_PHRASES: dict[str, tuple[str, ...]] = {
    "docs/reports/goal1214_full_local_discovery_after_goal1213_2026-05-01.md": (
        "Tests run: `2366`",
        "Failures: `0`",
        "Errors: `0`",
        "Result: `OK`",
    ),
    "docs/reports/goal1215_release_surface_doc_audit_2026-05-01.md": (
        "Tests run: `64`",
        "Result: `OK`",
        "Current reviewed public RTX wording rows: `11`",
        "database_analytics` remains blocked from public speedup wording",
        "polygon_set_jaccard` remains blocked from public speedup wording",
    ),
    "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md": (
        "database_analytics",
        "polygon_set_jaccard",
        "road_hazard_screening",
        "ratio embree/optix: `3.53225`",
    ),
    "docs/reports/goal1208_public_wording_decision_after_goal1206_2026-05-01.md": (
        "road_hazard_screening",
        "public_wording_reviewed",
        "database_analytics",
        "polygon_set_jaccard",
    ),
    "docs/v1_0_rtx_app_status.md": (
        "reviewed public RTX sub-path wording rows: `11`",
        "road_hazard_screening / prepared_native_compact_summary_40k",
        "broad or whole-app public speedup claim authorized: `False`",
    ),
}

FORBIDDEN_PUBLIC_PHRASES: tuple[str, ...] = (
    "reviewed public RTX sub-path wording rows: `10`",
    "Goal1208 authorizes full GIS",
    "Goal1208 authorizes whole-app",
    "database_analytics / public speedup",
    "polygon_set_jaccard / public speedup",
)


def _read_text(rel_path: str) -> str:
    path = ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _closure_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal, rel_paths in REQUIRED_CLOSURE_FILES.items():
        files = [{"path": rel_path, "exists": (ROOT / rel_path).exists()} for rel_path in rel_paths]
        missing = [row["path"] for row in files if not row["exists"]]
        has_external_review = any(
            ("claude" in row["path"] or "gemini" in row["path"]) and row["exists"] for row in files
        )
        has_consensus = any("two_ai_consensus" in row["path"] and row["exists"] for row in files)
        status = "ok" if not missing and has_external_review and has_consensus else "incomplete"
        rows.append(
            {
                "goal": goal,
                "files": files,
                "missing_files": missing,
                "has_external_review": has_external_review,
                "has_two_ai_consensus": has_consensus,
                "status": status,
            }
        )
    return rows


def _evidence_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path, phrases in REQUIRED_EVIDENCE_PHRASES.items():
        text = _read_text(rel_path)
        missing = [phrase for phrase in phrases if phrase not in text]
        forbidden = [phrase for phrase in FORBIDDEN_PUBLIC_PHRASES if phrase in text]
        rows.append(
            {
                "path": rel_path,
                "exists": bool(text),
                "missing_phrases": missing,
                "forbidden_phrases": forbidden,
                "status": "ok" if text and not missing and not forbidden else "evidence_failure",
            }
        )
    return rows


def build_audit() -> dict[str, Any]:
    closure_rows = _closure_rows()
    evidence_rows = _evidence_rows()
    closure_failures = [row for row in closure_rows if row["status"] != "ok"]
    evidence_failures = [row for row in evidence_rows if row["status"] != "ok"]
    valid = not closure_failures and not evidence_failures
    recommendation = (
        "local_release_candidate_ready_for_final_external_release_decision"
        if valid
        else "blocked_pending_missing_closure_or_evidence"
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "recommendation": recommendation,
        "pod_needed_now": False,
        "pod_decision": (
            "No immediate pod is required for the local v0.9.8 release-candidate audit. "
            "The next pod run should be a single batched final RTX replay only if the final "
            "release decision requires fresh hardware evidence beyond the saved Goal1206/Goal1208 artifacts."
        ),
        "closure_goal_count": len(closure_rows),
        "closure_failure_count": len(closure_failures),
        "evidence_file_count": len(evidence_rows),
        "evidence_failure_count": len(evidence_failures),
        "closure_rows": closure_rows,
        "evidence_rows": evidence_rows,
        "current_public_state": {
            "reviewed_public_rtx_wording_rows": 11,
            "new_reviewed_row_after_goal1208": "road_hazard_screening / prepared_native_compact_summary_40k",
            "database_analytics_public_speedup": "blocked",
            "polygon_set_jaccard_public_speedup": "blocked",
            "road_hazard_boundary": (
                "prepared native compact-summary traversal/count sub-path at 40k copies only; "
                "not default app behavior, GIS/routing, row output, Python orchestration, or whole-app speedup"
            ),
        },
        "validated_local_checks": {
            "full_unittest_discovery": {
                "goal": "Goal1214",
                "tests": 2366,
                "skips": 196,
                "failures": 0,
                "errors": 0,
                "result": "OK",
            },
            "release_surface_docs": {
                "goal": "Goal1215",
                "tests": 64,
                "result": "OK",
            },
        },
        "boundary": (
            "Goal1216 is a local release-candidate audit. It does not tag, publish, "
            "upload packages, authorize new public RTX wording, or require a cloud pod by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1216 v0.9.8 Release-Candidate Audit",
        "",
        f"Date: {payload['date']}",
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- recommendation: `{payload['recommendation']}`",
        f"- pod needed now: `{payload['pod_needed_now']}`",
        f"- closure goals audited: `{payload['closure_goal_count']}`",
        f"- closure failures: `{payload['closure_failure_count']}`",
        f"- evidence files audited: `{payload['evidence_file_count']}`",
        f"- evidence failures: `{payload['evidence_failure_count']}`",
        "",
        "## Public State",
        "",
        f"- reviewed public RTX wording rows: `{payload['current_public_state']['reviewed_public_rtx_wording_rows']}`",
        f"- new reviewed row: `{payload['current_public_state']['new_reviewed_row_after_goal1208']}`",
        "- `database_analytics` public speedup wording: `blocked`",
        "- `polygon_set_jaccard` public speedup wording: `blocked`",
        f"- road-hazard boundary: {payload['current_public_state']['road_hazard_boundary']}",
        "",
        "## Local Validation",
        "",
        "| Check | Tests | Result |",
        "| --- | ---: | --- |",
        "| Goal1214 full unittest discovery | `2366` | `OK` |",
        "| Goal1215 release-surface docs | `64` | `OK` |",
        "",
        "## Closure Rows",
        "",
        "| Goal | Status | External review | 2-AI consensus | Missing files |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in payload["closure_rows"]:
        lines.append(
            f"| `{row['goal']}` | `{row['status']}` | `{row['has_external_review']}` | "
            f"`{row['has_two_ai_consensus']}` | `{len(row['missing_files'])}` |"
        )
    lines.extend(
        [
            "",
            "## Evidence Rows",
            "",
            "| Path | Status | Missing phrases | Forbidden phrases |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in payload["evidence_rows"]:
        lines.append(
            f"| `{row['path']}` | `{row['status']}` | "
            f"`{len(row['missing_phrases'])}` | `{len(row['forbidden_phrases'])}` |"
        )
    lines.extend(["", "## Pod Decision", "", payload["pod_decision"], "", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local v0.9.8 release-candidate readiness.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1216_v0_9_8_release_candidate_audit_2026-05-01.md",
    )
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
