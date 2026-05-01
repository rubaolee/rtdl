#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.goal1173_staged_source_archive_manifest import build_manifest as build_source_manifest
from scripts.goal1175_staged_source_archive_builder import build_archive, verify_archive


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1204 repaired RTX pod packet"
ARCHIVE = ROOT / "docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.json"
DEFAULT_MD = ROOT / "docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.md"
REMOTE_ARCHIVE = "/tmp/goal1204_rtdl_source_2026-05-01.tar.gz"
REMOTE_RESULT = "/tmp/goal1204_repaired_rtx_pod.tgz"
REMOTE_RESULT_SHA = "/tmp/goal1204_repaired_rtx_pod.tgz.sha256"
LOCAL_COPYBACK_DIR = "docs/reports/goal1204_live_pod_2026-05-01"


ROWS: tuple[dict[str, Any], ...] = (
    {
        "label": "db_embree_100000_chunked_repair",
        "app": "database_analytics",
        "purpose": "Verify the previously failing 100k DB Embree scale now passes with compact-summary chunking.",
        "command": "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 100000 --iterations 3 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_100000_chunked_repair.json",
    },
    {
        "label": "db_optix_100000_chunked_repair",
        "app": "database_analytics",
        "purpose": "Verify the previously failing 100k DB OptiX scale now passes with compact-summary chunking.",
        "command": "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 100000 --iterations 3 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_100000_chunked_repair.json",
    },
    {
        "label": "db_embree_300000_chunked_repair",
        "app": "database_analytics",
        "purpose": "Collect same-scale 300k DB Embree control for the repaired compact-summary path.",
        "command": "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 300000 --iterations 2 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_embree_300000_chunked_repair.json",
    },
    {
        "label": "db_optix_300000_chunked_repair",
        "app": "database_analytics",
        "purpose": "Verify the previous 300k OptiX row-ceiling failure is repaired by chunking.",
        "command": "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 300000 --iterations 2 --output-mode compact_summary --strict --output-json ${RESULT_DIR}/db_optix_300000_chunked_repair.json",
    },
    {
        "label": "jaccard_optix_8192_public_safe_chunk_512",
        "app": "polygon_set_jaccard",
        "purpose": "Collect Jaccard claim-path evidence using the reviewed public-safe chunk policy.",
        "command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json ${RESULT_DIR}/jaccard_optix_8192_public_safe_chunk_512.json",
    },
    {
        "label": "jaccard_optix_8192_diagnostic_chunk_64",
        "app": "polygon_set_jaccard",
        "purpose": "Confirm the formerly failing chunk-64 shape is classified diagnostic-only, not claim-ready.",
        "command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 64 --output-json ${RESULT_DIR}/jaccard_optix_8192_diagnostic_chunk_64.json",
    },
    {
        "label": "road_hazard_embree_control_40000",
        "app": "road_hazard_screening",
        "purpose": "Collect same-scale Embree control for the larger road-hazard floor repair.",
        "command": "python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 40000 --output-mode summary > ${RESULT_DIR}/road_hazard_embree_control_40000.json",
    },
    {
        "label": "road_hazard_optix_control_40000",
        "app": "road_hazard_screening",
        "purpose": "Rerun road hazard at larger scale so OptiX query time can clear the 0.1s timing floor.",
        "command": "python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 40000 --iterations 5 --mode run --output-json ${RESULT_DIR}/road_hazard_optix_control_40000.json",
    },
)


def build_packet(archive_path: Path = ARCHIVE) -> dict[str, Any]:
    source_manifest = build_source_manifest()
    archive_payload = build_archive(archive_path)
    verification = verify_archive(archive_path, archive_payload["archive_sha256"])
    executor = "scripts/goal1204_repaired_rtx_pod_executor.sh"
    run_command = (
        "ARCHIVE={archive} EXPECTED_SHA256={sha} WORKDIR=/workspace/rtdl_goal1204 "
        "RESULT_TGZ={result} RESULT_SHA={result_sha} bash /tmp/goal1204_executor.sh"
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
        "rows": list(ROWS),
        "pod_batch": {
            "pod_executor": executor,
            "remote_archive": REMOTE_ARCHIVE,
            "remote_result": REMOTE_RESULT,
            "remote_result_sha": REMOTE_RESULT_SHA,
            "local_copyback_dir": LOCAL_COPYBACK_DIR,
            "target_repairs": [
                "database_analytics chunked compact-summary",
                "polygon_set_jaccard public-safe chunk policy",
                "road_hazard_screening floor-safe scale",
            ],
        },
        "commands": {
            "upload": [
                f"scp -P <pod_port> -i <ssh_key> {archive_path} root@<pod_host>:{REMOTE_ARCHIVE}",
                f"scp -P <pod_port> -i <ssh_key> {ROOT / executor} root@<pod_host>:/tmp/goal1204_executor.sh",
            ],
            "run_on_pod": run_command,
            "copy_back": [
                f"mkdir -p {LOCAL_COPYBACK_DIR}",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT} {LOCAL_COPYBACK_DIR}/",
                f"scp -P <pod_port> -i <ssh_key> root@<pod_host>:{REMOTE_RESULT_SHA} {LOCAL_COPYBACK_DIR}/",
                f"tar -xzf {LOCAL_COPYBACK_DIR}/goal1204_repaired_rtx_pod.tgz -C {LOCAL_COPYBACK_DIR}",
            ],
        },
        "preconditions": [
            "Run only after local Goal1202 and Goal1203 tests pass.",
            "Use one RTX-class Linux pod session; do not restart per app.",
            "Install GEOS/Embree/CUDA/OptiX once, then run all rows.",
            "Copy back the result tgz and sha256 before interpretation.",
            "A separate intake/review goal must interpret results after copy-back.",
        ],
        "boundary": (
            "Goal1204 prepares a future repaired-path pod batch only. It does not run cloud, "
            "authorize public docs, release, or public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1204 Repaired RTX Pod Packet",
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
        "## Rows",
        "",
        "| Label | App | Purpose |",
        "| --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(f"| `{row['label']}` | `{row['app']}` | {row['purpose']} |")
    lines.extend(["", "## Preconditions", ""])
    lines.extend(f"- {item}" for item in payload["preconditions"])
    lines.extend(["", "## Run On Pod", "", f"```bash\n{payload['commands']['run_on_pod']}\n```"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1204 repaired RTX pod packet.")
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
