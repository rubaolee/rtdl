#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


DATE = "2026-04-28"
GOAL = "Goal1076 Barnes-Hut rich RTX pod candidate"
REPORT_DIR = "docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate"


def _command(*parts: str) -> list[str]:
    return list(parts)


def _row(
    *,
    phase: str,
    output_name: str,
    command: list[str],
    purpose: str,
    requires_validation: bool,
    timing_floor_sec: float | None,
) -> dict[str, Any]:
    wording = rt.rtx_public_wording_status("barnes_hut_force_app")
    return {
        "app": "barnes_hut_force_app",
        "path_name": "node_coverage_prepared_rich",
        "phase": phase,
        "source_goal": "Goal1075",
        "purpose": purpose,
        "current_public_wording_status": wording.status,
        "current_public_wording_boundary": wording.boundary,
        "requires_validation": requires_validation,
        "contains_skip_validation": "--skip-validation" in command,
        "timing_floor_sec": timing_floor_sec,
        "output_json": f"{REPORT_DIR}/{output_name}",
        "command": command + ["--output-json", f"{REPORT_DIR}/{output_name}"],
    }


def build_manifest() -> dict[str, Any]:
    rows = [
        _row(
            phase="correctness_validation",
            output_name="barnes_hut_rich_node_coverage_validation.json",
            purpose="Validate the richer Barnes-Hut node-coverage contract with a manageable oracle.",
            requires_validation=True,
            timing_floor_sec=None,
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "barnes_hut_node_coverage",
                "--mode",
                "optix",
                "--body-count",
                "1024",
                "--iterations",
                "3",
                "--radius",
                "0.1",
                "--barnes-tree-depth",
                "6",
                "--hit-threshold",
                "4",
            ),
        ),
        _row(
            phase="large_timing_repeat",
            output_name="barnes_hut_rich_node_coverage_large_timing.json",
            purpose="Collect timing-only RTX traversal evidence for the richer Barnes-Hut node contract.",
            requires_validation=False,
            timing_floor_sec=0.100,
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "barnes_hut_node_coverage",
                "--mode",
                "optix",
                "--body-count",
                "1000000",
                "--iterations",
                "5",
                "--radius",
                "0.1",
                "--barnes-tree-depth",
                "8",
                "--hit-threshold",
                "4",
                "--skip-validation",
            ),
        ),
    ]
    validation_rows = [row for row in rows if row["phase"] == "correctness_validation"]
    timing_rows = [row for row in rows if row["phase"] == "large_timing_repeat"]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "source_artifacts": [
            "docs/reports/goal1075_barnes_hut_rich_contract_design_2026-04-28.md",
            "docs/reports/goal1075_barnes_hut_rich_contract_dry_run_2026-04-28.json",
            "docs/reports/goal1075_two_ai_consensus_2026-04-28.md",
        ],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "validation_row_count": len(validation_rows),
            "timing_row_count": len(timing_rows),
            "validation_rows_with_skip_validation": [
                row["output_json"] for row in validation_rows if row["contains_skip_validation"]
            ],
            "timing_rows_without_floor": [
                row["output_json"] for row in timing_rows if row["timing_floor_sec"] is None
            ],
        },
        "valid": (
            len(rows) == 2
            and len(validation_rows) == 1
            and len(timing_rows) == 1
            and not any(row["contains_skip_validation"] for row in validation_rows)
            and all(row["contains_skip_validation"] for row in timing_rows)
            and all(row["timing_floor_sec"] == 0.100 for row in timing_rows)
            and any("1024" in row["command"] and "6" in row["command"] for row in validation_rows)
            and any("1000000" in row["command"] and "8" in row["command"] for row in timing_rows)
        ),
        "boundary": (
            "Goal1076 prepares a separate Barnes-Hut rich-contract pod candidate. It does not run cloud, "
            "does not change public wording, does not authorize release, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1076 Barnes-Hut Rich RTX Pod Candidate",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| App | Path | Phase | Skip validation | Timing floor | Output | Command |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['contains_skip_validation']}` | `{floor}` | `{row['output_json']}` | "
            f"`{' '.join(row['command'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1076 generated runner for an already-running RTX-class Linux pod.",
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
        'echo "Goal1076 Barnes-Hut rich RTX pod candidate"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1076 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1076 Barnes-Hut rich RTX pod candidate.")
    parser.add_argument("--output-json", default="docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate_2026-04-28.md")
    parser.add_argument("--output-sh", default="scripts/goal1076_barnes_hut_rich_rtx_pod_candidate_runner.sh")
    args = parser.parse_args(argv)
    payload = build_manifest()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    sh_path = ROOT / args.output_sh
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"json": str(json_path), "md": str(md_path), "sh": str(sh_path), "valid": payload["valid"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
