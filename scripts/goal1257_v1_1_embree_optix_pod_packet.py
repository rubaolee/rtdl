#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.goal1175_staged_source_archive_builder import build_archive, verify_archive


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-04"
GOAL = "Goal1257 v1.1 Embree/OptiX current-source pod packet"
DEFAULT_ARCHIVE = ROOT / "docs/reports/goal1257_rtdl_source_2026-05-04.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1257_v1_1_embree_optix_pod_packet_2026-05-04.json"
DEFAULT_MD = ROOT / "docs/reports/goal1257_v1_1_embree_optix_pod_packet_2026-05-04.md"
REMOTE_ARCHIVE = "/tmp/goal1257_rtdl_source_2026-05-04.tar.gz"
REMOTE_EXECUTOR = "/tmp/goal1257_executor.sh"
REMOTE_RESULT = "/tmp/goal1257_v1_1_embree_optix_pod_results.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1257_v1_1_embree_optix_pod_results.tgz.sha256"
LOCAL_COPYBACK_DIR = "docs/reports/goal1257_live_pod_2026-05-04"


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def build_packet(archive_path: Path = DEFAULT_ARCHIVE) -> dict[str, Any]:
    archive_payload = build_archive(archive_path)
    verification = verify_archive(archive_path, archive_payload["archive_sha256"])
    executor = "scripts/goal1257_v1_1_embree_optix_pod_executor.sh"
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1257 "
        "RESULT_TGZ={result} RESULT_SHA={result_sha} bash {executor}"
    ).format(
        archive=REMOTE_ARCHIVE,
        sha=archive_payload["archive_sha256"],
        result=REMOTE_RESULT,
        result_sha=REMOTE_RESULT_SHA,
        executor=REMOTE_EXECUTOR,
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "source_commit": _git_head(),
        "valid": bool(archive_payload["valid"] and verification["valid"]),
        "archive": archive_payload,
        "verification": verification,
        "pod_batch": {
            "triage_report": "docs/reports/goal1256_v1_1_embree_optix_triage_2026-05-04.md",
            "pod_executor": executor,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_executor": REMOTE_EXECUTOR,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
            "local_copyback_dir": LOCAL_COPYBACK_DIR,
            "target_rows": [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
            "active_backends": ["embree", "optix"],
            "frozen_backends": ["vulkan", "hiprt", "apple_rt"],
        },
        "commands": {
            "upload": [
                f"scp -P <pod_port> -i <ssh_key> {archive_path} root@<pod_host>:{REMOTE_ARCHIVE}",
                f"scp -P <pod_port> -i <ssh_key> {ROOT / executor} root@<pod_host>:{REMOTE_EXECUTOR}",
            ],
            "run_on_pod": run_command,
            "copy_back": [
                f"mkdir -p {LOCAL_COPYBACK_DIR}",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT} {LOCAL_COPYBACK_DIR}/",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT_SHA} {LOCAL_COPYBACK_DIR}/",
                f"tar -xzf {LOCAL_COPYBACK_DIR}/goal1257_v1_1_embree_optix_pod_results.tgz -C {LOCAL_COPYBACK_DIR}",
            ],
        },
        "preconditions": [
            "Use one RTX-class Linux pod session and reuse it for all rows.",
            "Do not open Vulkan, HIPRT, or Apple RT implementation work.",
            "Copy back result tgz and sha256 before interpretation.",
            "Interpretation must be a separate intake/review step before any public wording.",
        ],
        "boundary": (
            "This packet prepares current-source v1.1 Embree/OptiX timing collection. "
            "It does not run cloud, change public docs, authorize release, or authorize public RTX wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1257 v1.1 Embree/OptiX Pod Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"Source commit: `{payload['source_commit']}`",
        "",
        "## Archive",
        "",
        f"- path: `{payload['archive']['archive_path']}`",
        f"- sha256: `{payload['archive']['archive_sha256']}`",
        f"- bytes: `{payload['archive']['archive_bytes']}`",
        "",
        "## Pod Batch",
        "",
    ]
    for key in ("triage_report", "pod_executor", "remote_result", "local_copyback_dir"):
        lines.append(f"- {key}: `{payload['pod_batch'][key]}`")
    lines.extend(["", "## Target Rows", ""])
    lines.extend(f"- `{row}`" for row in payload["pod_batch"]["target_rows"])
    lines.extend(["", "## Preconditions", ""])
    lines.extend(f"- {item}" for item in payload["preconditions"])
    lines.extend(["", "## Upload", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["upload"])
    lines.extend(["", "## Run On Pod", "", f"```bash\n{payload['commands']['run_on_pod']}\n```"])
    lines.extend(["", "## Copy Back", ""])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in payload["commands"]["copy_back"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1257 v1.1 Embree/OptiX pod packet.")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_packet(args.archive)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "sha256": payload["archive"]["archive_sha256"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
