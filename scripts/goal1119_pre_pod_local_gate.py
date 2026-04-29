#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1119 pre-pod local gate"


def _exists(path: str) -> bool:
    return (ROOT / path).exists()


def build_gate() -> dict[str, Any]:
    required_paths = [
        "scripts/goal1116_current_source_rtx_rerun_runner.sh",
        "docs/reports/goal1116_current_source_rtx_rerun_packet_2026-04-29.json",
        "docs/reports/goal1116_two_ai_consensus_2026-04-29.md",
        "docs/reports/goal1116_runner_logging_followup_review_2026-04-29.md",
        "docs/reports/goal1117_two_ai_consensus_2026-04-29.md",
        "scripts/goal1118_current_source_rtx_rerun_intake.py",
        "docs/reports/goal1118_two_ai_consensus_2026-04-29.md",
    ]
    packet = json.loads((ROOT / "docs/reports/goal1116_current_source_rtx_rerun_packet_2026-04-29.json").read_text(encoding="utf-8"))
    intake = json.loads((ROOT / "docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.json").read_text(encoding="utf-8"))
    rows = packet["rows"]
    command_text = "\n".join(" ".join(row["command"]) for row in rows)
    checks = {
        "required_paths_exist": all(_exists(path) for path in required_paths),
        "packet_valid": bool(packet["valid"]),
        "packet_has_three_apps": packet["summary"]["app_count"] == 3,
        "packet_has_no_public_claim": packet["summary"]["public_speedup_claim_authorized_count"] == 0,
        "facility_uses_recentered_contract": "facility_service_coverage_recentered" in command_text,
        "barnes_uses_radius_0_1": "--radius 0.1" in command_text,
        "barnes_uses_depth_8": "--barnes-tree-depth 8" in command_text,
        "robot_uses_packed_8m_timing": "--pose-count 8000000" in command_text and "--input-mode packed_arrays" in command_text,
        "runner_logs_output": "goal1116_runner.log" in (ROOT / "scripts/goal1116_current_source_rtx_rerun_runner.sh").read_text(encoding="utf-8"),
        "intake_exists_and_blocks_until_pod": intake["valid"] is False and intake["summary"]["missing_row_count"] == 5,
        "intake_has_no_public_claim": intake["summary"]["public_speedup_claim_authorized"] is False,
    }
    blockers = [key for key, value in checks.items() if not value]
    ready_for_pod = not blockers
    return {
        "goal": GOAL,
        "date": DATE,
        "checks": checks,
        "blockers": blockers,
        "ready_for_pod": ready_for_pod,
        "next_action": (
            "Start an RTX pod and run scripts/goal1116_current_source_rtx_rerun_runner.sh"
            if ready_for_pod
            else "Fix local pre-pod blockers before starting an RTX pod"
        ),
        "boundary": (
            "Goal1119 is a local pre-pod gate. It does not run cloud, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1119 Pre-Pod Local Gate",
        "",
        f"Date: {payload['date']}",
        "",
        f"Ready for pod: `{str(payload['ready_for_pod']).lower()}`",
        "",
        f"Next action: {payload['next_action']}",
        "",
        payload["boundary"],
        "",
        "## Checks",
        "",
        "| Check | Pass |",
        "| --- | --- |",
    ]
    for key, value in payload["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Blockers", ""])
    if payload["blockers"]:
        for blocker in payload["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local pre-pod gate for current-source RTX rerun.")
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs/reports/goal1119_pre_pod_local_gate_2026-04-29.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs/reports/goal1119_pre_pod_local_gate_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_gate()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"ready_for_pod": payload["ready_for_pod"], "blockers": payload["blockers"]}, sort_keys=True))
    return 0 if payload["ready_for_pod"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
