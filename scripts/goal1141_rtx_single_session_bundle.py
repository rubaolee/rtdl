#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any

from scripts import goal1116_current_source_rtx_rerun_packet as goal1116
from scripts import goal1135_changed_path_rtx_pod_plan as goal1135


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1141 RTX single-session pod bundle"
REPORT_DIR = "docs/reports/goal1141_rtx_single_session_bundle"


def _shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def build_bundle() -> dict[str, Any]:
    current_source = goal1116.build_packet()
    changed_path = goal1135.build_plan()
    entries: list[dict[str, Any]] = []
    for row in current_source["rows"]:
        entries.append(
            {
                "label": f"goal1116_{row['app']}_{row['phase']}",
                "source_goal": "goal1116",
                "app": row["app"],
                "reason": row["purpose"],
                "command": row["command"],
                "output_json": row["output_json"],
            }
        )
    for row in changed_path["entries"]:
        entries.append(
            {
                "label": f"goal1135_{row['label']}",
                "source_goal": "goal1135",
                "app": ",".join(row["apps"]),
                "reason": row["reason"],
                "command": row["command"],
                "output_json": row["command"][-1],
            }
        )
    setup_commands = [
        [
            "bash",
            "-lc",
            "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config",
        ],
        [
            "python3",
            "scripts/goal763_rtx_cloud_bootstrap_check.py",
            "--skip-tests",
            "--output-json",
            f"{REPORT_DIR}/bootstrap_preflight.json",
        ],
        [
            "python3",
            "scripts/goal763_rtx_cloud_bootstrap_check.py",
            "--output-json",
            f"{REPORT_DIR}/bootstrap_full.json",
        ],
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "setup_commands": setup_commands,
        "entries": entries,
        "summary": {
            "setup_count": len(setup_commands),
            "entry_count": len(entries),
            "goal1116_entry_count": sum(1 for entry in entries if entry["source_goal"] == "goal1116"),
            "goal1135_entry_count": sum(1 for entry in entries if entry["source_goal"] == "goal1135"),
            "public_speedup_claim_authorized_count": 0,
        },
        "valid": (
            len(setup_commands) == 3
            and len(entries) == 11
            and any("libgeos-dev" in " ".join(command) for command in setup_commands)
            and any("goal763_rtx_cloud_bootstrap_check.py" in command for command in setup_commands[1])
            and all(entry["output_json"].endswith(".json") for entry in entries)
        ),
        "boundary": (
            "Goal1141 prepares one consolidated RTX pod session for Goal1116 current-source "
            "reruns plus Goal1135 changed-path artifacts. It does not create cloud resources, "
            "does not run cloud locally, does not authorize release, and does not authorize "
            "public RTX speedup or broad whole-app acceleration claims."
        ),
        "cloud_policy": (
            "Run this bundle only after a pod is already running. Do not start/stop a pod per app. "
            "The generated shell keeps going after individual entry failures, writes a status TSV, "
            "and asks for copying back the whole report directory before stopping the pod."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1141 RTX Single-Session Pod Bundle",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Cloud Policy",
        "",
        payload["cloud_policy"],
        "",
        "## Setup Commands",
        "",
    ]
    for command in payload["setup_commands"]:
        lines.append(f"- `{_shell_join(command)}`")
    lines.extend(
        [
            "",
            "## Entries",
            "",
            "| Label | Source | App | Output | Command |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for entry in payload["entries"]:
        lines.append(
            f"| `{entry['label']}` | `{entry['source_goal']}` | `{entry['app']}` | "
            f"`{entry['output_json']}` | `{_shell_join(entry['command'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -uo pipefail",
        "",
        "# Goal1141 consolidated RTX pod runner.",
        "# Boundary: evidence collection only; no public speedup claims are authorized.",
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        'export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"',
        'export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"',
        'export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"',
        'export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"',
        'export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"',
        'export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"',
        'export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"',
        "",
        'if [ -z "${RTDL_SOURCE_COMMIT}" ]; then',
        '  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-review artifacts." >&2',
        "  exit 2",
        "fi",
        "",
        f"mkdir -p {payload['report_dir']}",
        f'STATUS_FILE="{payload["report_dir"]}/goal1141_status.tsv"',
        f'LOG_FILE="{payload["report_dir"]}/goal1141_runner.log"',
        'printf "label\\tstatus\\trc\\tutc\\n" > "${STATUS_FILE}"',
        'exec > >(tee -a "${LOG_FILE}") 2>&1',
        'echo "Goal1141 RTX single-session pod bundle"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        'echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"',
        'date -u +"utc_start=%Y-%m-%dT%H:%M:%SZ"',
        "nvidia-smi || true",
        "",
        "run_step() {",
        "  local label=\"$1\"",
        "  shift",
        "  echo \"BEGIN ${label}\"",
        "  date -u +\"${label}_utc_start=%Y-%m-%dT%H:%M:%SZ\"",
        "  \"$@\"",
        "  local rc=$?",
        "  local status=ok",
        "  if [ \"${rc}\" -ne 0 ]; then",
        "    status=failed",
        "  fi",
        "  printf \"%s\\t%s\\t%s\\t%s\\n\" \"${label}\" \"${status}\" \"${rc}\" \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" >> \"${STATUS_FILE}\"",
        "  echo \"END ${label} status=${status} rc=${rc}\"",
        "  return 0",
        "}",
        "",
    ]
    for index, command in enumerate(payload["setup_commands"], start=1):
        lines.append(f"run_step setup_{index} {_shell_join(command)}")
    lines.append("")
    for index, entry in enumerate(payload["entries"], start=1):
        lines.append(f"run_step entry_{index}_{entry['label']} {_shell_join(entry['command'])}")
    lines.extend(
        [
            "",
            'date -u +"utc_end=%Y-%m-%dT%H:%M:%SZ"',
            'echo "Goal1141 complete. Review ${STATUS_FILE} and copy back docs/reports/goal1141_rtx_single_session_bundle, docs/reports/goal1116_current_source_rtx_rerun_packet, and docs/reports/goal1135_changed_path_rtx_pod before stopping the pod."',
            'if grep -q $\'\\tfailed\\t\' "${STATUS_FILE}"; then',
            '  echo "One or more Goal1141 steps failed; keep the pod only if same-pod targeted retry is useful." >&2',
            "  exit 1",
            "fi",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a consolidated RTX pod session bundle.")
    parser.add_argument("--output-json", default=f"{REPORT_DIR}_2026-04-29.json")
    parser.add_argument("--output-md", default=f"{REPORT_DIR}_2026-04-29.md")
    parser.add_argument("--output-sh", default="scripts/goal1141_rtx_single_session_runner.sh")
    args = parser.parse_args(argv)
    payload = build_bundle()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    sh_path = ROOT / args.output_sh
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"json": str(json_path), "md": str(md_path), "sh": str(sh_path), "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
