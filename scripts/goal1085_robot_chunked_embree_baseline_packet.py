#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1085 robot chunked Embree baseline packet"
REPORT_DIR = "docs/reports/goal1085_robot_chunked_embree_baseline"
TOTAL_POSE_COUNT = 36_000_000
CHUNK_POSE_COUNT = 200_000
OBSTACLE_COUNT = 4096
ITERATIONS = 3
WORKER_COUNT = 8


def build_packet() -> dict[str, Any]:
    chunk_count = TOTAL_POSE_COUNT // CHUNK_POSE_COUNT
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "source_artifacts": [
            "docs/reports/goal1080_post_pod_public_wording_readiness_audit_2026-04-29.json",
            "docs/reports/goal1081_same_scale_baseline_execution_packet_2026-04-29.json",
        ],
        "target_rtx_artifact": "docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_36m_timing.json",
        "scale": {
            "total_pose_count": TOTAL_POSE_COUNT,
            "chunk_pose_count": CHUNK_POSE_COUNT,
            "chunk_count": chunk_count,
            "obstacle_count": OBSTACLE_COUNT,
            "iterations_per_chunk": ITERATIONS,
            "worker_count": WORKER_COUNT,
        },
        "command_template": (
            "PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py "
            "--backend embree --pose-count {chunk_pose_count} --obstacle-count {obstacle_count} "
            "--iterations {iterations} --worker-count {worker_count} "
            "--output-json {report_dir}/chunk_${{chunk_index}}.json"
        ).format(
            chunk_pose_count=CHUNK_POSE_COUNT,
            obstacle_count=OBSTACLE_COUNT,
            iterations=ITERATIONS,
            worker_count=WORKER_COUNT,
            report_dir=REPORT_DIR,
        ),
        "public_speedup_claim_authorized": False,
        "baseline_interpretation": (
            "Chunked Embree baseline repeats a 200k-pose workload 180 times to cover the same total pose-count "
            "as the 36M RTX timing artifact without requiring one huge resident Python object graph. It is a "
            "same-total-work engineering baseline, not a same-single-launch baseline, until artifact intake and "
            "2+ AI review decide whether the comparison boundary is acceptable."
        ),
        "valid": (
            TOTAL_POSE_COUNT % CHUNK_POSE_COUNT == 0
            and chunk_count == 180
            and OBSTACLE_COUNT == 4096
            and ITERATIONS == 3
        ),
        "boundary": (
            "Goal1085 prepares a non-cloud robot Embree baseline runner only. It does not run the heavy baseline, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    scale = payload["scale"]
    return "\n".join(
        [
            "# Goal1085 Robot Chunked Embree Baseline Packet",
            "",
            f"Date: {payload['date']}",
            "",
            f"Valid: `{str(payload['valid']).lower()}`",
            "",
            payload["boundary"],
            "",
            "## Scale",
            "",
            f"- Total poses: `{scale['total_pose_count']}`",
            f"- Chunk poses: `{scale['chunk_pose_count']}`",
            f"- Chunk count: `{scale['chunk_count']}`",
            f"- Obstacles: `{scale['obstacle_count']}`",
            f"- Iterations per chunk: `{scale['iterations_per_chunk']}`",
            "",
            "## Interpretation",
            "",
            payload["baseline_interpretation"],
            "",
            "## Command Template",
            "",
            "```bash",
            payload["command_template"],
            "```",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )


def to_shell(payload: dict[str, Any]) -> str:
    scale = payload["scale"]
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1085 generated runner for a local/Linux/Windows non-cloud Embree baseline host.",
        "# Boundary: does not authorize public RTX speedup claims.",
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        f"mkdir -p {payload['report_dir']}",
        f"for chunk_index in $(seq 0 {scale['chunk_count'] - 1}); do",
        '  echo "Running robot Embree baseline chunk ${chunk_index}"',
        "  " + payload["command_template"],
        "done",
        f'echo "Goal1085 complete. Review {payload["report_dir"]}/chunk_*.json before any comparison."',
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1085 robot chunked Embree baseline packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1085_robot_chunked_embree_baseline_packet_2026-04-29.md")
    parser.add_argument("--output-sh", default="scripts/goal1085_robot_chunked_embree_baseline_runner.sh")
    args = parser.parse_args(argv)
    payload = build_packet()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    sh_path = ROOT / args.output_sh
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"json": str(json_path), "md": str(md_path), "sh": str(sh_path), "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
