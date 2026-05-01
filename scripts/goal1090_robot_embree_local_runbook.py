#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1090 robot Embree local baseline runbook"


def build_runbook() -> dict[str, Any]:
    pose_id_start_formula = "chunk_index * 200000 + 1"
    steps = [
        {
            "name": "smoke_one_small_embree_chunk",
            "purpose": "Verify local Embree/native baseline plumbing before starting the heavy 180-chunk run.",
            "command": (
                "PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py "
                "--backend embree --pose-count 1000 --obstacle-count 128 --iterations 1 "
                "--worker-count 1 --pose-id-start 1 --output-json build/goal1090_robot_embree_smoke.json"
            ),
            "heavy": False,
        },
        {
            "name": "run_one_real_chunk",
            "purpose": "Run one claim-scale chunk and confirm it writes the expected chunk artifact.",
            "command": (
                "RTDL_GOAL1085_START_CHUNK=0 RTDL_GOAL1085_END_CHUNK=0 "
                "RTDL_GOAL1085_SKIP_EXISTING=1 bash scripts/goal1085_robot_chunked_embree_baseline_runner.sh"
            ),
            "heavy": True,
        },
        {
            "name": "intake_after_partial_or_full_run",
            "purpose": "Aggregate present chunks and report missing/invalid chunk indices without authorizing claims.",
            "command": "PYTHONPATH=src:. python3 scripts/goal1086_robot_chunked_embree_baseline_intake.py",
            "heavy": False,
        },
        {
            "name": "run_remaining_chunks_when_host_is_available",
            "purpose": "Complete the same-total-work non-cloud Embree baseline over all 36M pose ids.",
            "command": (
                "RTDL_GOAL1085_SKIP_EXISTING=1 bash scripts/goal1085_robot_chunked_embree_baseline_runner.sh"
            ),
            "heavy": True,
        },
        {
            "name": "final_intake",
            "purpose": "Produce complete aggregate evidence after all 180 chunks exist.",
            "command": "PYTHONPATH=src:. python3 scripts/goal1086_robot_chunked_embree_baseline_intake.py",
            "heavy": False,
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "host_policy": "non_cloud_linux_or_windows_preferred",
        "not_pod_work": True,
        "source_artifacts": [
            "docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json",
            "docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json",
            "docs/reports/goal1089_robot_chunk_pose_id_offset_update_2026-04-29.md",
        ],
        "scale_contract": {
            "total_pose_count": 36_000_000,
            "chunk_count": 180,
            "chunk_pose_count": 200_000,
            "obstacle_count": 4096,
            "pose_id_start_formula": pose_id_start_formula,
            "resume_controls": [
                "RTDL_GOAL1085_START_CHUNK",
                "RTDL_GOAL1085_END_CHUNK",
                "RTDL_GOAL1085_SKIP_EXISTING",
            ],
        },
        "steps": steps,
        "summary": {
            "step_count": len(steps),
            "heavy_step_count": sum(1 for step in steps if step["heavy"]),
            "public_speedup_claim_authorized_count": 0,
        },
        "valid": (
            len(steps) == 5
            and any("goal1085_robot_chunked_embree_baseline_runner.sh" in step["command"] for step in steps)
            and any("goal1086_robot_chunked_embree_baseline_intake.py" in step["command"] for step in steps)
            and pose_id_start_formula == "chunk_index * 200000 + 1"
            and "RTDL_GOAL1085_SKIP_EXISTING=1" in "\n".join(step["command"] for step in steps)
        ),
        "boundary": (
            "Goal1090 is a non-cloud robot baseline execution runbook. It does not run the heavy baseline, "
            "does not create cloud resources, does not authorize release, does not change public wording, "
            "and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1090 Robot Embree Local Baseline Runbook",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Host Policy",
        "",
        f"- Host: `{payload['host_policy']}`",
        f"- Not pod work: `{payload['not_pod_work']}`",
        "",
        "## Scale Contract",
        "",
    ]
    for key, value in payload["scale_contract"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Steps",
            "",
            "| Step | Heavy | Purpose | Command |",
            "| --- | --- | --- | --- |",
        ]
    )
    for step in payload["steps"]:
        lines.append(
            f"| `{step['name']}` | `{step['heavy']}` | {step['purpose']} | `{step['command']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write robot Embree local baseline runbook.")
    parser.add_argument("--output-json", default="docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1090_robot_embree_local_runbook_2026-04-29.md")
    args = parser.parse_args()
    payload = build_runbook()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
