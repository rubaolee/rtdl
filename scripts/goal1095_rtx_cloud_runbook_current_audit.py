#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1095 RTX cloud runbook current audit"
RUNBOOK = ROOT / "docs/rtx_cloud_single_session_runbook.md"


def build_audit() -> dict[str, Any]:
    text = RUNBOOK.read_text(encoding="utf-8")
    compact_text = " ".join(text.split())
    checks = {
        "mentions_current_post_goal1094": "Current Post-Goal1094 Runner" in text,
        "runs_goal1084_facility": "goal1084_facility_recentered_rtx_pod_packet_runner.sh" in text,
        "runs_goal1093_barnes": "goal1093_barnes_hut_20m_contract_runner.sh" in text,
        "marks_goal1072_historical": "older Goal1072 runner is historical" in compact_text,
        "marks_goal1076_historical": "Goal1093 supersedes" in compact_text and "older Goal1076" in compact_text,
        "robot_is_not_cloud_gpu_task": "Robot is intentionally absent" in text and "non-OptiX baseline" in text,
        "barnes_validation_no_skip": "without `--skip-validation`" in text,
        "barnes_timing_skip": "with `--skip-validation`" in text,
        "no_public_claim_boundary": "public wording can change" in text and "2+ AI review" in text,
    }
    return {
        "goal": GOAL,
        "date": DATE,
        "runbook": str(RUNBOOK.relative_to(ROOT)),
        "checks": checks,
        "valid": all(checks.values()),
        "boundary": (
            "Goal1095 audits the cloud runbook text only. It does not run cloud, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1095 RTX Cloud Runbook Current Audit",
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
    parser = argparse.ArgumentParser(description="Audit current RTX cloud runbook text.")
    parser.add_argument("--output-json", default="docs/reports/goal1095_rtx_cloud_runbook_current_audit_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1095_rtx_cloud_runbook_current_audit_2026-04-29.md")
    args = parser.parse_args()
    payload = build_audit()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["checks"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
