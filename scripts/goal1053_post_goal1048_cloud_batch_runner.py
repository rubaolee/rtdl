#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from shlex import quote
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal1052_post_goal1048_cloud_batch_manifest import build_manifest


DATE = "2026-04-28"
GOAL = "Goal1053 post-Goal1048 cloud batch runner"


def _shell_join(parts: list[str]) -> str:
    return " ".join(quote(str(part)) for part in parts)


def build_runner() -> dict[str, Any]:
    manifest = build_manifest()
    rows = manifest["diagnostic_validation_reruns"] + manifest["same_semantics_review_candidates"]
    commands: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        commands.append(
            {
                "index": index,
                "app": row["app"],
                "path_name": row["path_name"],
                "batch": row["batch"],
                "command": row["command"],
                "output_json": row["output_json"],
                "contains_skip_validation": row["contains_skip_validation"],
            }
        )
    return {
        "goal": GOAL,
        "date": DATE,
        "manifest_goal": manifest["goal"],
        "report_dir": "docs/reports/goal1052_post_goal1048_cloud_batch",
        "bootstrap_command": manifest["bootstrap_command"],
        "commands": commands,
        "valid": (
            manifest["valid"]
            and len(commands) == 11
            and not any(command["contains_skip_validation"] for command in commands[:2])
        ),
        "boundary": (
            "This runner is a pod-side command script generator. It does not create "
            "cloud resources, copy credentials, authorize release, or authorize public "
            "RTX speedup wording."
        ),
    }


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1053 generated pod-side runner for an already-running RTX-class Linux pod.",
        "# Boundary: does not create cloud resources and does not authorize speedup claims.",
        "",
        'OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-8.0.0}"',
        'CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12.4}"',
        'NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"',
        f'REPORT_DIR="${{REPORT_DIR:-{payload["report_dir"]}}}"',
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        "export OPTIX_PREFIX",
        "export CUDA_PREFIX",
        "export NVCC",
        'export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"',
        'export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"',
        'export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"',
        'export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"',
        "",
        'if [ -z "${RTDL_SOURCE_COMMIT}" ]; then',
        '  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2',
        "  exit 2",
        "fi",
        "",
        'mkdir -p "${REPORT_DIR}"',
        'echo "Goal1053 post-Goal1048 RTX cloud batch runner"',
        'echo "repo=$(pwd)"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        'echo "report_dir=${REPORT_DIR}"',
        "",
        "if ! command -v nvidia-smi >/dev/null 2>&1; then",
        '  echo "nvidia-smi is missing. Use an RTX-class NVIDIA GPU pod image." >&2',
        "  exit 2",
        "fi",
        "nvidia-smi",
        "",
        f"{_shell_join(payload['bootstrap_command'])}",
        "",
    ]
    for command in payload["commands"]:
        lines.extend(
            [
                f'echo "Running {command["index"]}/{len(payload["commands"])}: {command["app"]}:{command["path_name"]}"',
                _shell_join(command["command"]),
                f'echo "Completed {command["app"]}:{command["path_name"]}; copy back {command["output_json"]}"',
                "",
            ]
        )
    lines.extend(
        [
            'echo "Goal1053 batch complete. Copy back ${REPORT_DIR} before stopping the pod."',
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Goal1053 pod-side runner.")
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1053_post_goal1048_cloud_batch_runner_2026-04-28.json",
    )
    parser.add_argument(
        "--output-sh",
        default="scripts/goal1053_post_goal1048_cloud_batch_runner.sh",
    )
    args = parser.parse_args()
    payload = build_runner()
    output_json = ROOT / args.output_json
    output_sh = ROOT / args.output_sh
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_sh.write_text(to_shell(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_json), "sh": str(output_sh), "valid": payload["valid"]}))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
