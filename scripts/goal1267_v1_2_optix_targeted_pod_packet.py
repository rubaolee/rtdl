#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.goal1175_staged_source_archive_builder import build_archive, verify_archive


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-05"
GOAL = "Goal1267 v1.2 targeted OptiX pod packet"
PLAN = "docs/reports/goal1266_v1_2_optix_plan_after_v1_1_findings_2026-05-05.md"
DEFAULT_ARCHIVE = ROOT / "docs/reports/goal1267_rtdl_source_2026-05-05.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1267_v1_2_optix_targeted_pod_packet_2026-05-05.json"
DEFAULT_MD = ROOT / "docs/reports/goal1267_v1_2_optix_targeted_pod_packet_2026-05-05.md"
REMOTE_ARCHIVE = "/tmp/goal1267_rtdl_source_2026-05-05.tar.gz"
REMOTE_EXECUTOR = "/tmp/goal1267_executor.sh"
REMOTE_RESULT = "/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz.sha256"
LOCAL_COPYBACK_DIR = "docs/reports/goal1267_live_pod_2026-05-05"


TARGETS = [
    {
        "row": "graph_analytics",
        "priority": 1,
        "current_state": "fast OptiX any-hit kernel, slower total path",
        "question": "Can prepared-scene reuse amortize scene/ray preparation enough to improve total timing?",
        "scales": [30000, 60000],
        "expected_metadata": {
            "ray_pack_mode": "numpy_packed_rays",
            "blocker_pack_mode": "numpy_packed_triangles",
            "visibility_query_repeats": 100,
        },
        "required_fields": [
            "ray_pack_mode",
            "blocker_pack_mode",
            "blocker_pack_sec",
            "ray_pack_sec",
            "scene_prepare_sec",
            "ray_prepare_sec",
            "query_anyhit_count_sec",
            "query_anyhit_count_first_sec",
            "query_anyhit_count_mean_sec",
            "query_anyhit_count_min_sec",
            "visibility_query_repeats",
            "summary_postprocess_sec",
        ],
    },
    {
        "row": "polygon_pair_overlap_area_rows",
        "priority": 2,
        "current_state": "bounded positive wording exists; Goal1270 clarified candidate diagnostics",
        "question": "Does the pod artifact preserve positive-pair parity while keeping candidate upper-bound mismatch explicit?",
        "scales": [40000, 80000, 160000],
        "required_fields": [
            "candidate_count_matches_expected",
            "candidate_count_delta_vs_expected",
            "positive_pair_count_matches_expected",
            "expected_positive_pair_count",
            "optix_positive_pair_count",
            "candidate_discovery_seconds",
            "native_exact_continuation_seconds",
            "output_seconds",
        ],
    },
    {
        "row": "database_analytics",
        "priority": 3,
        "current_state": "sales_risk reaches 300k, warm-query median still favors Embree",
        "question": "Can warm-query OptiX timing improve under the retained compact-summary contract?",
        "scales": [100000, 300000],
        "required_fields": [
            "warm_query_median_seconds",
            "prepare_seconds",
            "one_shot_seconds",
            "row_materializing_operation_count",
        ],
    },
    {
        "row": "polygon_set_jaccard",
        "priority": 4,
        "current_state": "chunk 1024 is the safe correctness default; OptiX remains slower",
        "question": "Can candidate-discovery timing improve while preserving chunk 1024 correctness?",
        "scales": [4096, 8192],
        "required_fields": [
            "chunk_copies",
            "candidate_discovery_seconds",
            "native_exact_continuation_seconds",
            "output_seconds",
        ],
    },
]


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
    executor = "scripts/goal1267_v1_2_optix_targeted_pod_executor.sh"
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1267 "
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
            "plan_source": PLAN,
            "pod_executor": executor,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_executor": REMOTE_EXECUTOR,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
            "local_copyback_dir": LOCAL_COPYBACK_DIR,
            "target_rows": [target["row"] for target in TARGETS],
            "active_backends": ["embree", "optix"],
            "frozen_backends": ["vulkan", "hiprt", "apple_rt"],
            "targets": TARGETS,
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
                f"tar -xzf {LOCAL_COPYBACK_DIR}/goal1267_v1_2_optix_targeted_pod_results.tgz -C {LOCAL_COPYBACK_DIR}",
            ],
        },
        "preconditions": [
            "Run only after local inspection says pod timing is needed.",
            "Use one RTX-class Linux pod session and reuse it for all four target rows.",
            "Run scripts/rtdl_pod_env_probe.sh on the pod and preserve rtdl_pod_env.json with the copied artifacts.",
            "Collect same-contract Embree and OptiX artifacts before interpretation.",
            "Run the graph prepared-repeat probe from Goal1269 to separate repeated query cost from one-time scene/ray preparation.",
            "Preserve Goal1270 candidate diagnostics for polygon-pair and Jaccard artifacts.",
            "Do not open Vulkan, HIPRT, or Apple RT implementation work before v2.1.",
            "Copy back result tgz and sha256 before any intake report.",
        ],
        "boundary": (
            "This packet is execution-only v1.2 evidence collection. It does not authorize "
            "public wording, release claims, or positive speedup claims. Slower OptiX results "
            "may close only as optix_still_slower_with_reason when correctness and bottleneck "
            "evidence are preserved."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1267 v1.2 Targeted OptiX Pod Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"Source commit: `{payload['source_commit']}`",
        f"Plan source: `{payload['pod_batch']['plan_source']}`",
        "",
        "## Archive",
        "",
        f"- path: `{payload['archive']['archive_path']}`",
        f"- sha256: `{payload['archive']['archive_sha256']}`",
        f"- bytes: `{payload['archive']['archive_bytes']}`",
        "",
        "## Targets",
        "",
        "| Priority | Row | Scales | Required evidence |",
        "| --- | --- | --- | --- |",
    ]
    for target in payload["pod_batch"]["targets"]:
        fields = ", ".join(f"`{field}`" for field in target["required_fields"])
        scales = ", ".join(str(scale) for scale in target["scales"])
        lines.append(f"| {target['priority']} | `{target['row']}` | {scales} | {fields} |")
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
    parser = argparse.ArgumentParser(description="Build Goal1267 targeted v1.2 OptiX pod packet.")
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
