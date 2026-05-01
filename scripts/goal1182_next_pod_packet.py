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
GOAL = "Goal1182 next consolidated RTX pod packet"
ARCHIVE = ROOT / "docs/reports/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1182_next_pod_packet_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1182_next_pod_packet_2026-04-30.md"
REMOTE_ARCHIVE = "/tmp/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz"
REMOTE_RESULT = "/tmp/goal1182_goal1170_results.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1182_goal1170_results.tgz.sha256"


def build_packet(archive_path: Path = ARCHIVE) -> dict[str, Any]:
    source_manifest = build_source_manifest()
    archive_payload = build_archive(archive_path)
    verification = verify_archive(archive_path, archive_payload["archive_sha256"])
    executor = "scripts/goal1176_pod_archive_batch_executor.sh"
    upload_commands = [
        f"scp -P <pod_port> -i <ssh_key> {archive_path} root@<pod_host>:{REMOTE_ARCHIVE}",
        f"scp -P <pod_port> -i <ssh_key> {ROOT / executor} root@<pod_host>:/tmp/goal1182_executor.sh",
    ]
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1182 "
        "RESULT_TGZ={result} RESULT_SHA={result_sha} bash /tmp/goal1182_executor.sh"
    ).format(
        archive=REMOTE_ARCHIVE,
        sha=archive_payload["archive_sha256"],
        result=REMOTE_RESULT,
        result_sha=REMOTE_RESULT_SHA,
    )
    copy_back_commands = [
        f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT} docs/reports/goal1182_live_pod_2026-04-30/",
        f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT_SHA} docs/reports/goal1182_live_pod_2026-04-30/",
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
            "base_manifest": "scripts/goal1170_clean_source_rtx_batch_manifest.py",
            "pod_executor": executor,
            "expected_rows": 8,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
        },
        "commands": {
            "upload": upload_commands,
            "run_on_pod": run_command,
            "copy_back": copy_back_commands,
        },
        "preconditions": [
            "Use an RTX-class Linux pod with NVIDIA driver visible through nvidia-smi.",
            "Do not patch source on the pod; the executor creates a synthetic clean git commit from this archive.",
            "Executor installs GEOS/pkg-config and CUDA dev packages before strict correctness gates.",
            "Run the full batch once per pod session and copy back the result archive plus SHA file.",
        ],
        "boundary": (
            "This packet prepares the next consolidated pod run. It creates a source archive "
            "and replay commands only; it does not run cloud benchmarks, authorize release, "
            "or authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1182 Next Consolidated RTX Pod Packet",
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
        f"- base manifest: `{payload['pod_batch']['base_manifest']}`",
        f"- pod executor: `{payload['pod_batch']['pod_executor']}`",
        f"- expected rows: `{payload['pod_batch']['expected_rows']}`",
        "",
        "## Preconditions",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["preconditions"])
    lines.extend(["", "## Upload", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["upload"])
    lines.extend(["", "## Run On Pod", "", f"```bash\n{payload['commands']['run_on_pod']}\n```"])
    lines.extend(["", "## Copy Back", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["copy_back"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the next consolidated RTX pod packet.")
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
