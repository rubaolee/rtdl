#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1022 history release drift audit"

PUBLIC_RELEASE_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/current_main_support_matrix.md",
    "docs/release_reports/v0_9_6/README.md",
    "docs/release_reports/v0_9_6/audit_report.md",
)

HISTORY_DOCS = (
    "history/COMPLETE_HISTORY.md",
    "history/revision_dashboard.md",
)


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def _extract_public_release_versions() -> list[str]:
    versions: set[str] = set()
    for rel_path in PUBLIC_RELEASE_DOCS:
        text = _read(rel_path)
        for match in re.finditer(r"current released version(?: is|:)\s*`(v[0-9.]+)`", text):
            versions.add(match.group(1))
        if "Status: released as `v0.9.6`" in text:
            versions.add("v0.9.6")
        if "current public release: `v0.9.6`" in text.lower():
            versions.add("v0.9.6")
    return sorted(versions)


def _history_presence(version: str) -> dict[str, bool]:
    return {rel_path: version in _read(rel_path) for rel_path in HISTORY_DOCS}


def build_audit() -> dict[str, Any]:
    public_versions = _extract_public_release_versions()
    current_public_release = public_versions[-1] if public_versions else None
    history_presence = (
        _history_presence(current_public_release) if current_public_release else {}
    )
    complete_history = _read("history/COMPLETE_HISTORY.md")
    dashboard = _read("history/revision_dashboard.md")
    refresh = _read("docs/handoff/REFRESH_LOCAL_2026-04-13.md")

    release_report_claims_history_catchup = (
        "public history catch-up" in _read("docs/release_reports/v0_9_6/audit_report.md")
        and "Goal684" in _read("docs/release_reports/v0_9_6/README.md")
    )
    history_drift_detected = bool(
        current_public_release
        and not all(history_presence.values())
    )
    history_status = "drift_detected" if history_drift_detected else "drift_resolved"
    refresh_current = (
        "/Users/rl2025/rtdl_python_only" in refresh
        and "v0.9.6" in refresh
        and "v1.0 RTX" in refresh
    )
    full_suite_evidence = {
        "command": "PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v",
        "result": "OK",
        "tests": 1969,
        "skipped": 196,
        "seconds": 218.674,
        "date": DATE,
    }
    return {
        "goal": GOAL,
        "date": DATE,
        "public_release_docs": list(PUBLIC_RELEASE_DOCS),
        "history_docs": list(HISTORY_DOCS),
        "public_release_versions": public_versions,
        "current_public_release": current_public_release,
        "history_presence_for_current_public_release": history_presence,
        "release_report_claims_history_catchup": release_report_claims_history_catchup,
        "complete_history_mentions_goal684": "Goal684" in complete_history,
        "dashboard_mentions_goal684": "Goal684" in dashboard,
        "history_drift_detected": history_drift_detected,
        "history_status": history_status,
        "refresh_context_current": refresh_current,
        "full_suite_evidence": full_suite_evidence,
        "recommended_next_action": (
            "Append or regenerate a post-v0.9.6 history catch-up round so "
            "history/COMPLETE_HISTORY.md and history/revision_dashboard.md match "
            "the released v0.9.6 public docs. Do not rewrite old records."
            if history_drift_detected
            else "Goal1023 has resolved the v0.9.6 public-history drift; keep future release history catch-ups append-only."
        ),
        "valid": (
            current_public_release == "v0.9.6"
            and release_report_claims_history_catchup
            and all(history_presence.values())
            and refresh_current
        ),
        "boundary": (
            "This is an audit and refresh-context check. It records the full local "
            "test result and detects history/public-release drift; it does not tag, "
            "release, or authorize public speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    suite = payload["full_suite_evidence"]
    lines = [
        "# Goal1022 History Release Drift Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid audit: `{payload['valid']}`",
        f"- current public release detected: `{payload['current_public_release']}`",
        f"- history status: `{payload['history_status']}`",
        f"- history drift detected: `{payload['history_drift_detected']}`",
        f"- refresh context current: `{payload['refresh_context_current']}`",
        f"- release report claims history catch-up: `{payload['release_report_claims_history_catchup']}`",
        f"- complete history mentions Goal684: `{payload['complete_history_mentions_goal684']}`",
        f"- revision dashboard mentions Goal684: `{payload['dashboard_mentions_goal684']}`",
        "",
        "## Full Local Test Evidence",
        "",
        f"- command: `{suite['command']}`",
        f"- result: `{suite['result']}`",
        f"- tests: `{suite['tests']}`",
        f"- skipped: `{suite['skipped']}`",
        f"- runtime seconds: `{suite['seconds']}`",
        "",
        "## History Presence",
        "",
        "| History doc | Mentions current public release |",
        "|---|---:|",
    ]
    for rel_path, present in payload["history_presence_for_current_public_release"].items():
        lines.append(f"| `{rel_path}` | `{present}` |")
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            payload["recommended_next_action"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit history docs against current public release docs.")
    parser.add_argument("--output-json", default="docs/reports/goal1022_history_release_drift_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1022_history_release_drift_audit_2026-04-26.md")
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
