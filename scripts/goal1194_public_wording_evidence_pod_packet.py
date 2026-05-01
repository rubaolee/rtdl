#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.goal1173_staged_source_archive_manifest import build_manifest as build_source_manifest
from scripts.goal1175_staged_source_archive_builder import build_archive, verify_archive


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1194 public wording evidence pod packet"
ARCHIVE = ROOT / "docs/reports/goal1194_rtdl_source_2026-04-30.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1194_public_wording_evidence_pod_packet_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1194_public_wording_evidence_pod_packet_2026-04-30.md"
REMOTE_ARCHIVE = "/tmp/goal1194_rtdl_source_2026-04-30.tar.gz"
REMOTE_RESULT = "/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz.sha256"
LOCAL_COPYBACK_DIR = "docs/reports/goal1194_live_pod_2026-04-30"


def build_packet(archive_path: Path = ARCHIVE) -> dict[str, Any]:
    source_manifest = build_source_manifest()
    archive_payload = build_archive(archive_path)
    verification = verify_archive(archive_path, archive_payload["archive_sha256"])
    executor = "scripts/goal1194_public_wording_evidence_pod_executor.sh"
    upload_commands = [
        f"scp -P <pod_port> -i <ssh_key> {archive_path} root@<pod_host>:{REMOTE_ARCHIVE}",
        f"scp -P <pod_port> -i <ssh_key> {ROOT / executor} root@<pod_host>:/tmp/goal1194_executor.sh",
    ]
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1194 "
        "RESULT_TGZ={result} RESULT_SHA={result_sha} bash /tmp/goal1194_executor.sh"
    ).format(
        archive=REMOTE_ARCHIVE,
        sha=archive_payload["archive_sha256"],
        result=REMOTE_RESULT,
        result_sha=REMOTE_RESULT_SHA,
    )
    copy_back_commands = [
        f"mkdir -p {LOCAL_COPYBACK_DIR}",
        f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT} {LOCAL_COPYBACK_DIR}/",
        f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT_SHA} {LOCAL_COPYBACK_DIR}/",
        (
            f"tar -xzf {LOCAL_COPYBACK_DIR}/goal1194_goal1192_public_wording_evidence_batch.tgz "
            f"-C {LOCAL_COPYBACK_DIR}"
        ),
        (
            "PYTHONPATH=src:. python3 scripts/goal1193_public_wording_evidence_batch_intake.py "
            f"--input-dir {LOCAL_COPYBACK_DIR}/docs/reports/goal1192_public_wording_evidence_batch "
            "--output-json docs/reports/goal1194_goal1192_public_wording_evidence_batch_intake_2026-04-30.json "
            "--output-md docs/reports/goal1194_goal1192_public_wording_evidence_batch_intake_2026-04-30.md"
        ),
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": bool(source_manifest["valid"] and archive_payload["valid"] and verification["valid"]),
        "archive": archive_payload,
        "verification": verification,
        "source_manifest": {
            "file_count": source_manifest["file_count"],
            "aggregate_sha256": source_manifest["aggregate_sha256"],
            "include_dirs": source_manifest["include_dirs"],
            "include_files": source_manifest["include_files"],
        },
        "pod_batch": {
            "runner": "scripts/goal1192_public_wording_evidence_batch_runner.sh",
            "intake": "scripts/goal1193_public_wording_evidence_batch_intake.py",
            "pod_executor": executor,
            "expected_artifacts": 12,
            "expected_app_pairs": 6,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
            "local_copyback_dir": LOCAL_COPYBACK_DIR,
        },
        "commands": {
            "upload": upload_commands,
            "run_on_pod": run_command,
            "copy_back_and_intake": copy_back_commands,
        },
        "preconditions": [
            "Use one RTX-class Linux pod session and run the full batch once.",
            "Use the local key that actually exists, usually ~/.ssh/id_ed25519_rtdl_codex on this Mac.",
            "Do not patch source on the pod; the executor creates a synthetic clean git commit from the archive.",
            "Executor installs GEOS/pkg-config before Embree/geometry baselines.",
            "Executor builds OptiX before running Goal1192.",
            "Copy the result tgz and sha256 back, then run Goal1193 intake locally before interpreting timing.",
        ],
        "boundary": (
            "This packet prepares a future pod execution path for Goal1192 evidence. "
            "It creates a source archive and replay commands only; it does not run cloud, "
            "does not authorize release, and does not authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1194 Public Wording Evidence Pod Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        "## Archive",
        "",
        f"- path: `{payload['archive']['archive_path']}`",
        f"- sha256: `{payload['archive']['archive_sha256']}`",
        f"- bytes: `{payload['archive']['archive_bytes']}`",
        f"- manifest file count: `{payload['archive']['manifest_file_count']}`",
        f"- manifest aggregate sha256: `{payload['archive']['manifest_aggregate_sha256']}`",
        "",
        "## Pod Batch",
        "",
        f"- runner: `{payload['pod_batch']['runner']}`",
        f"- intake: `{payload['pod_batch']['intake']}`",
        f"- pod executor: `{payload['pod_batch']['pod_executor']}`",
        f"- expected artifacts: `{payload['pod_batch']['expected_artifacts']}`",
        f"- expected app pairs: `{payload['pod_batch']['expected_app_pairs']}`",
        "",
        "## Preconditions",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["preconditions"])
    lines.extend(["", "## Upload", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["upload"])
    lines.extend(["", "## Run On Pod", "", f"```bash\n{payload['commands']['run_on_pod']}\n```"])
    lines.extend(["", "## Copy Back And Intake", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["copy_back_and_intake"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1194 public wording evidence pod packet.")
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_packet(args.archive)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": payload["valid"],
                "archive": payload["archive"]["archive_path"],
                "sha256": payload["archive"]["archive_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
