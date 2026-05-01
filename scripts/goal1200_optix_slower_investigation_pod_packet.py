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
GOAL = "Goal1200 OptiX slower-app investigation pod packet"
ARCHIVE = ROOT / "docs/reports/goal1200_rtdl_source_2026-04-30.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1200_optix_slower_investigation_pod_packet_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1200_optix_slower_investigation_pod_packet_2026-04-30.md"
REMOTE_ARCHIVE = "/tmp/goal1200_rtdl_source_2026-04-30.tar.gz"
REMOTE_RESULT = "/tmp/goal1200_optix_slower_app_investigation.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1200_optix_slower_app_investigation.tgz.sha256"
LOCAL_COPYBACK_DIR = "docs/reports/goal1200_live_pod_2026-04-30"


def build_packet(archive_path: Path = ARCHIVE) -> dict[str, Any]:
    source_manifest = build_source_manifest()
    archive_payload = build_archive(archive_path)
    verification = verify_archive(archive_path, archive_payload["archive_sha256"])
    executor = "scripts/goal1200_optix_slower_investigation_pod_executor.sh"
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1200 "
        "RESULT_TGZ={result} RESULT_SHA={result_sha} bash /tmp/goal1200_executor.sh"
    ).format(
        archive=REMOTE_ARCHIVE,
        sha=archive_payload["archive_sha256"],
        result=REMOTE_RESULT,
        result_sha=REMOTE_RESULT_SHA,
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": bool(source_manifest["valid"] and archive_payload["valid"] and verification["valid"]),
        "archive": archive_payload,
        "verification": verification,
        "source_manifest": {
            "file_count": source_manifest["file_count"],
            "aggregate_sha256": source_manifest["aggregate_sha256"],
        },
        "pod_batch": {
            "reviewed_plan": "docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.md",
            "post_same_scale_sync": "docs/reports/goal1199_two_ai_consensus_2026-04-30.md",
            "pod_executor": executor,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
            "local_copyback_dir": LOCAL_COPYBACK_DIR,
            "target_rows": [
                "database_analytics",
                "graph_analytics",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
            ],
            "positive_controls": ["road_hazard_screening"],
            "same_scale_repairs": ["hausdorff_distance"],
        },
        "commands": {
            "upload": [
                f"scp -P <pod_port> -i <ssh_key> {archive_path} root@<pod_host>:{REMOTE_ARCHIVE}",
                f"scp -P <pod_port> -i <ssh_key> {ROOT / executor} root@<pod_host>:/tmp/goal1200_executor.sh",
            ],
            "run_on_pod": run_command,
            "copy_back": [
                f"mkdir -p {LOCAL_COPYBACK_DIR}",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT} {LOCAL_COPYBACK_DIR}/",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT_SHA} {LOCAL_COPYBACK_DIR}/",
                f"tar -xzf {LOCAL_COPYBACK_DIR}/goal1200_optix_slower_app_investigation.tgz -C {LOCAL_COPYBACK_DIR}",
            ],
        },
        "preconditions": [
            "Use one RTX-class Linux pod session; do not restart per app.",
            "Use the local key that exists on this Mac, usually ~/.ssh/id_ed25519_rtdl_codex.",
            "Executor preserves failed status JSON and logs instead of aborting the whole batch.",
            "Copy the result tgz and sha256 back before interpretation.",
            "A separate intake/review goal must interpret results after copy-back.",
        ],
        "boundary": (
            "This packet prepares a future pod execution path for Goal1200 investigation evidence. "
            "It creates a source archive and replay commands only; it does not run cloud, edit public docs, "
            "authorize release, or authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1200 OptiX Slower-App Investigation Pod Packet",
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
        "",
        "## Pod Batch",
        "",
    ]
    for key in ("reviewed_plan", "post_same_scale_sync", "pod_executor", "remote_result", "local_copyback_dir"):
        lines.append(f"- {key}: `{payload['pod_batch'][key]}`")
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
    parser = argparse.ArgumentParser(description="Build Goal1200 OptiX slower-app investigation pod packet.")
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
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
