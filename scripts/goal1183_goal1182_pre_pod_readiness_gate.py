#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1183 Goal1182 pre-pod readiness gate"
PACKET_JSON = ROOT / "docs/reports/goal1182_next_pod_packet_2026-04-30.json"
ARCHIVE = ROOT / "docs/reports/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz"
EXECUTOR = ROOT / "scripts/goal1176_pod_archive_batch_executor.sh"
INTAKE_SCRIPT = ROOT / "scripts/goal1170_clean_source_rtx_batch_intake.py"
CONSENSUS_FILES = (
    "docs/reports/goal1180_two_ai_consensus_2026-04-30.md",
    "docs/reports/goal1181_two_ai_consensus_2026-04-30.md",
    "docs/reports/goal1182_two_ai_consensus_2026-04-30.md",
)
DEFAULT_JSON = ROOT / "docs/reports/goal1183_goal1182_pre_pod_readiness_gate_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1183_goal1182_pre_pod_readiness_gate_2026-04-30.md"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_gate() -> dict[str, Any]:
    packet = json.loads(PACKET_JSON.read_text(encoding="utf-8")) if PACKET_JSON.exists() else {}
    archive_sha = _sha256(ARCHIVE) if ARCHIVE.exists() else ""
    packet_sha = packet.get("archive", {}).get("archive_sha256", "")
    run_command = packet.get("commands", {}).get("run_on_pod", "")
    upload_commands = packet.get("commands", {}).get("upload", [])
    copy_back_commands = packet.get("commands", {}).get("copy_back", [])
    executor_text = _text(EXECUTOR)
    consensus_text = "\n".join(_text(ROOT / path) for path in CONSENSUS_FILES)
    checks = {
        "packet_json_exists": PACKET_JSON.exists(),
        "packet_valid": bool(packet.get("valid")),
        "archive_exists": ARCHIVE.exists(),
        "archive_sha_matches_packet": bool(archive_sha and archive_sha == packet_sha),
        "archive_sha_used_in_run_command": bool(packet_sha and f"EXPECTED_SHA256={packet_sha}" in run_command),
        "run_command_overrides_goal1175_defaults": (
            "ARCHIVE=/tmp/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz" in run_command
            and "WORKDIR=/workspace/rtdl_goal1182" in run_command
            and "RESULT_TGZ=/tmp/goal1182_goal1170_results.tgz" in run_command
        ),
        "upload_commands_cover_archive_and_executor": (
            len(upload_commands) == 2
            and any("goal1182_rtdl_current_source_for_next_pod" in command for command in upload_commands)
            and any("goal1182_executor.sh" in command for command in upload_commands)
        ),
        "copy_back_commands_cover_result_and_sha": (
            len(copy_back_commands) == 2
            and any("goal1182_goal1170_results.tgz " in command for command in copy_back_commands)
            and any("goal1182_goal1170_results.tgz.sha256" in command for command in copy_back_commands)
        ),
        "executor_verifies_archive_sha": "actual_sha256" in executor_text and "Archive SHA256 mismatch" in executor_text,
        "executor_installs_geos": "libgeos-dev" in executor_text and "pkg-config" in executor_text,
        "executor_generates_manifest_before_run": "goal1170_clean_source_rtx_batch_manifest.py" in executor_text,
        "executor_packs_result_archive": 'tar -czf "${RESULT_TGZ}"' in executor_text,
        "intake_script_exists": INTAKE_SCRIPT.exists(),
        "required_consensus_files_exist": all((ROOT / path).exists() for path in CONSENSUS_FILES),
        "consensus_accepts_goal1182": "Goal1182" in consensus_text and "ACCEPT" in consensus_text,
        "no_local_cloud_execution": "does not run cloud benchmarks" in packet.get("boundary", ""),
        "no_release_or_public_speedup_authorization": (
            "authorize release" in packet.get("boundary", "")
            and "authorize public RTX speedup wording" in packet.get("boundary", "")
        ),
    }
    blockers = [name for name, ok in checks.items() if not ok]
    return {
        "goal": GOAL,
        "date": DATE,
        "ready_for_pod": not blockers,
        "checks": checks,
        "blockers": blockers,
        "archive_path": str(ARCHIVE),
        "archive_sha256": archive_sha,
        "packet_sha256": packet_sha,
        "next_action": (
            "Start one RTX-class pod session and run the Goal1182 packet commands verbatim."
            if not blockers
            else "Fix the listed local pre-pod blockers before starting a pod."
        ),
        "post_pod_required_action": (
            "Copy back the result TGZ and SHA, extract under docs/reports/goal1182_live_pod_2026-04-30/, "
            "then run scripts/goal1170_clean_source_rtx_batch_intake.py before interpreting evidence."
        ),
        "boundary": (
            "Goal1183 is a local readiness gate. It does not start cloud resources, run benchmarks, "
            "authorize release, or authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1183 Goal1182 Pre-Pod Readiness Gate",
        "",
        f"Date: {payload['date']}",
        "",
        f"Ready for pod: `{str(payload['ready_for_pod']).lower()}`",
        f"Archive SHA256: `{payload['archive_sha256']}`",
        "",
        f"Next action: {payload['next_action']}",
        "",
        f"Post-pod required action: {payload['post_pod_required_action']}",
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
        lines.extend(f"- `{blocker}`" for blocker in payload["blockers"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal1182 local pre-pod readiness gate.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_gate()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"ready_for_pod": payload["ready_for_pod"], "blockers": payload["blockers"]}, sort_keys=True))
    return 0 if payload["ready_for_pod"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
