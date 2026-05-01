#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1091 robot pose-offset Embree smoke intake"
SMOKE_ARTIFACT = "docs/reports/goal1091_robot_embree_pose_offset_smoke_2026-04-29.json"


def build_intake() -> dict[str, Any]:
    artifact = json.loads((ROOT / SMOKE_ARTIFACT).read_text(encoding="utf-8"))
    scale = artifact["benchmark_scale"]
    summary = artifact["summary"]
    checks = {
        "status_ok": artifact["status"] == "ok",
        "correctness_parity": artifact["correctness_parity"] is True,
        "source_backend_embree": artifact["source_backend"] == "embree",
        "pose_id_start_recorded": scale["pose_id_start"] == 200001,
        "pose_count_recorded": scale["pose_count"] == 1000,
        "sample_uses_offset_range": min(summary["colliding_pose_ids_sample"]) >= 200001,
        "claim_authorized_false": artifact["authorizes_public_speedup_claim"] is False,
    }
    return {
        "goal": GOAL,
        "date": DATE,
        "source_artifact": SMOKE_ARTIFACT,
        "checks": checks,
        "phase_seconds": artifact["phase_seconds"],
        "summary": summary,
        "status": "ok" if all(checks.values()) else "blocked",
        "public_speedup_claim_authorized": False,
        "valid": all(checks.values()),
        "boundary": (
            "Goal1091 is a small local Embree smoke intake for pose-id offsets. It does not run the heavy 36M baseline, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1091 Robot Pose-Offset Embree Smoke Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Status: `{payload['status']}`",
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
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Pose count: `{payload['summary']['pose_count']}`",
            f"- Colliding pose count: `{payload['summary']['colliding_pose_count']}`",
            f"- Colliding sample: `{payload['summary']['colliding_pose_ids_sample']}`",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write Goal1091 robot pose-offset smoke intake.")
    parser.add_argument("--output-json", default="docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1091_robot_pose_offset_smoke_intake_2026-04-29.md")
    args = parser.parse_args()
    payload = build_intake()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "status": payload["status"], **payload["checks"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
