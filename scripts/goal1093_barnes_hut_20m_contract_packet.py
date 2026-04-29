#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1093 Barnes-Hut 20M contract packet"
REPORT_DIR = "docs/reports/goal1093_barnes_hut_20m_contract"


def _command(*parts: str) -> list[str]:
    return list(parts)


def build_packet() -> dict[str, Any]:
    rows = [
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "phase": "depth8_contract_validation",
            "body_count": 4096,
            "node_count": 65_536,
            "barnes_tree_depth": 8,
            "hit_threshold": 4,
            "radius": 0.1,
            "iterations": 3,
            "requires_validation": True,
            "contains_skip_validation": False,
            "timing_floor_sec": None,
            "output_json": f"{REPORT_DIR}/barnes_hut_depth8_4096_validation.json",
            "purpose": (
                "Validate the same depth-8 / threshold-4 / radius-0.1 node-coverage contract used by the 20M timing row, "
                "but with a manageable 4,096-body oracle."
            ),
            "command": _command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "barnes_hut_node_coverage",
                "--mode",
                "optix",
                "--body-count",
                "4096",
                "--iterations",
                "3",
                "--radius",
                "0.1",
                "--barnes-tree-depth",
                "8",
                "--hit-threshold",
                "4",
                "--output-json",
                f"{REPORT_DIR}/barnes_hut_depth8_4096_validation.json",
            ),
        },
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared_rich",
            "phase": "depth8_20m_timing_repeat",
            "body_count": 20_000_000,
            "node_count": 65_536,
            "barnes_tree_depth": 8,
            "hit_threshold": 4,
            "radius": 0.1,
            "iterations": 5,
            "requires_validation": False,
            "contains_skip_validation": True,
            "timing_floor_sec": 0.100,
            "output_json": f"{REPORT_DIR}/barnes_hut_depth8_20m_timing.json",
            "purpose": (
                "Repeat the Goal1079 20M timing row under the superseding depth-8 contract. This remains timing-only "
                "and requires the depth8_contract_validation row plus later intake/review."
            ),
            "command": _command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "barnes_hut_node_coverage",
                "--mode",
                "optix",
                "--body-count",
                "20000000",
                "--iterations",
                "5",
                "--radius",
                "0.1",
                "--barnes-tree-depth",
                "8",
                "--hit-threshold",
                "4",
                "--skip-validation",
                "--output-json",
                f"{REPORT_DIR}/barnes_hut_depth8_20m_timing.json",
            ),
        },
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "supersedes": [
            "docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate_2026-04-28.json",
            "docs/reports/goal1078_goal1076_artifact_intake_after_pod_2026-04-29.json",
        ],
        "source_artifacts": [
            "docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json",
            "docs/reports/goal1079_two_ai_consensus_2026-04-29.md",
        ],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "validation_row_count": sum(1 for row in rows if row["requires_validation"]),
            "timing_row_count": sum(1 for row in rows if not row["requires_validation"]),
            "validation_rows_with_skip_validation": [
                row["output_json"] for row in rows if row["requires_validation"] and row["contains_skip_validation"]
            ],
            "public_speedup_claim_authorized_count": 0,
        },
        "valid": (
            len(rows) == 2
            and rows[0]["barnes_tree_depth"] == rows[1]["barnes_tree_depth"] == 8
            and rows[0]["node_count"] == rows[1]["node_count"] == 65_536
            and rows[0]["hit_threshold"] == rows[1]["hit_threshold"] == 4
            and rows[0]["radius"] == rows[1]["radius"] == 0.1
            and rows[0]["requires_validation"]
            and not rows[0]["contains_skip_validation"]
            and rows[1]["contains_skip_validation"]
            and rows[1]["timing_floor_sec"] == 0.100
        ),
        "boundary": (
            "Goal1093 prepares a superseding Barnes-Hut contract packet only. It does not run cloud, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1093 Barnes-Hut 20M Contract Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| Phase | Bodies | Nodes | Depth | Threshold | Skip validation | Timing floor | Command |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['phase']}` | `{row['body_count']}` | `{row['node_count']}` | "
            f"`{row['barnes_tree_depth']}` | `{row['hit_threshold']}` | `{row['contains_skip_validation']}` | "
            f"`{floor}` | `{' '.join(row['command'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1093 generated runner for an already-running RTX-class Linux pod.",
        "# Boundary: does not create cloud resources and does not authorize speedup claims.",
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
        '  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2',
        "  exit 2",
        "fi",
        "",
        f"mkdir -p {payload['report_dir']}",
        'echo "Goal1093 Barnes-Hut 20M contract packet"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1093 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Barnes-Hut 20M superseding contract packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.md")
    parser.add_argument("--output-sh", default="scripts/goal1093_barnes_hut_20m_contract_runner.sh")
    args = parser.parse_args()
    payload = build_packet()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    sh_path = ROOT / args.output_sh
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
