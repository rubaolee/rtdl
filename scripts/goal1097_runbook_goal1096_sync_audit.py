#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1097 runbook Goal1096 sync audit"
RUNBOOK = ROOT / "docs" / "rtx_cloud_single_session_runbook.md"


def build_audit() -> dict[str, Any]:
    text = RUNBOOK.read_text(encoding="utf-8")
    checks = {
        "copies_goal1084_dir": "goal1084_facility_recentered_rtx_pod_packet" in text,
        "copies_goal1093_dir": "goal1093_barnes_hut_20m_contract" in text,
        "runs_goal1096_intake": "scripts/goal1096_current_rtx_pod_artifact_intake.py" in text,
        "tests_goal1096_intake": "tests.goal1096_current_rtx_pod_artifact_intake_test" in text,
        "states_engineering_evidence_only": "engineering evidence only" in text,
        "preserves_no_claim_boundary": (
            "does not authorize public wording" in text
            and "public RTX speedup claims" in text
        ),
        "removes_pending_goal1084_intake_placeholder": "scripts/goal1085_goal1084_artifact_intake.py" not in text,
    }
    return {
        "goal": GOAL,
        "date": DATE,
        "runbook": str(RUNBOOK.relative_to(ROOT)),
        "checks": checks,
        "valid": all(checks.values()),
        "boundary": (
            "Goal1097 audits runbook text only. It does not run cloud, does not change public wording, "
            "does not authorize release, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1097 Runbook Goal1096 Sync Audit",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Checks",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in payload["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit that the RTX cloud runbook references Goal1096 intake.")
    parser.add_argument("--output-json", default="docs/reports/goal1097_runbook_goal1096_sync_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1097_runbook_goal1096_sync_audit_2026-04-29.md")
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["checks"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
