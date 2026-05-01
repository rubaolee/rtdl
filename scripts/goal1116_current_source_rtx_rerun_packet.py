#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1116 current-source RTX rerun packet"
REPORT_DIR = "docs/reports/goal1116_current_source_rtx_rerun_packet"


def _command(*parts: str) -> list[str]:
    return list(parts)


def _row(
    *,
    app: str,
    path_name: str,
    phase: str,
    output_name: str,
    command: list[str],
    purpose: str,
    requires_validation: bool,
    timing_floor_sec: float | None,
) -> dict[str, Any]:
    return {
        "app": app,
        "path_name": path_name,
        "phase": phase,
        "purpose": purpose,
        "requires_validation": requires_validation,
        "contains_skip_validation": "--skip-validation" in command,
        "timing_floor_sec": timing_floor_sec,
        "output_json": f"{REPORT_DIR}/{output_name}",
        "command": command + ["--output-json", f"{REPORT_DIR}/{output_name}"],
    }


def build_packet() -> dict[str, Any]:
    rows = [
        _row(
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared_recentered",
            phase="same_scale_validation_and_timing",
            output_name="facility_recentered_coverage_threshold_2_5m_optix_validation.json",
            purpose="Current-source rerun of the recentered facility contract used by Goal1084 and Goal1108.",
            requires_validation=True,
            timing_floor_sec=0.100,
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "facility_service_coverage_recentered",
                "--mode",
                "optix",
                "--copies",
                "2500000",
                "--iterations",
                "5",
                "--radius",
                "1.0",
            ),
        ),
        _row(
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="correctness_validation",
            output_name="robot_prepared_pose_flags_validation.json",
            purpose="Current-source oracle parity check for prepared robot pose flags.",
            requires_validation=True,
            timing_floor_sec=None,
            command=_command(
                "python3",
                "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                "--mode",
                "optix",
                "--pose-count",
                "4096",
                "--obstacle-count",
                "256",
                "--iterations",
                "3",
                "--input-mode",
                "python_objects",
                "--result-mode",
                "pose_flags",
            ),
        ),
        _row(
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="large_timing_repeat",
            output_name="robot_prepared_pose_flags_8m_timing.json",
            purpose=(
                "Current-source large packed robot timing repeat. This is the safe cloud timing target; "
                "the 36M Embree baseline enables later scale-normalized review but not automatic public wording."
            ),
            requires_validation=False,
            timing_floor_sec=0.100,
            command=_command(
                "python3",
                "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                "--mode",
                "optix",
                "--pose-count",
                "8000000",
                "--obstacle-count",
                "4096",
                "--iterations",
                "7",
                "--input-mode",
                "packed_arrays",
                "--result-mode",
                "pose_count",
                "--skip-validation",
            ),
        ),
        _row(
            app="barnes_hut_force_app",
            path_name="node_coverage_prepared_rich",
            phase="correctness_validation",
            output_name="barnes_hut_depth8_4096_validation.json",
            purpose="Current-source validation for the corrected Barnes-Hut depth-8/radius-0.1 contract.",
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
                "4096",
                "--iterations",
                "3",
                "--radius",
                "0.1",
                "--barnes-tree-depth",
                "8",
                "--hit-threshold",
                "4",
            ),
        ),
        _row(
            app="barnes_hut_force_app",
            path_name="node_coverage_prepared_rich",
            phase="large_timing_repeat",
            output_name="barnes_hut_depth8_20m_timing.json",
            purpose="Current-source rerun of the 20M Barnes-Hut timing contract used by Goal1093 and Goal1108.",
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
                "20000000",
                "--iterations",
                "3",
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
    validation_rows = [row for row in rows if row["requires_validation"]]
    timing_rows = [row for row in rows if row["timing_floor_sec"] is not None]
    validation_with_skip = [row["output_json"] for row in validation_rows if row["contains_skip_validation"]]
    timing_without_floor = [
        row["output_json"]
        for row in rows
        if row["phase"].endswith("timing_repeat") and row["timing_floor_sec"] is None
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "app_count": len({row["app"] for row in rows}),
            "validation_row_count": len(validation_rows),
            "timing_floor_row_count": len(timing_rows),
            "validation_rows_with_skip_validation": validation_with_skip,
            "timing_rows_without_floor": timing_without_floor,
            "public_speedup_claim_authorized_count": 0,
        },
        "source_artifacts": [
            "docs/reports/goal1109_v1_rtx_readiness_status_after_baselines_2026-04-29.json",
            "docs/reports/goal1114_two_ai_consensus_2026-04-29.md",
        ],
        "global_preconditions": [
            "Run only from an already-running RTX-class NVIDIA pod checkout.",
            "Use the current branch/commit containing Goal1114 and Goal1115.",
            "Build the OptiX backend before running the packet.",
            "Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.",
            "Copy the whole report directory back before stopping or terminating the pod.",
            "Treat all outputs as evidence only until 2+ AI review and public wording review.",
        ],
        "valid": (
            len(rows) == 5
            and len({row["app"] for row in rows}) == 3
            and len(validation_rows) == 3
            and not validation_with_skip
            and not timing_without_floor
        ),
        "boundary": (
            "Goal1116 prepares current-source RTX reruns for Facility, Robot, and Barnes-Hut. "
            "It does not create cloud resources, does not run cloud locally, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1116 Current-Source RTX Rerun Packet",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Preconditions",
        "",
    ]
    for item in payload["global_preconditions"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| App | Path | Phase | Validation | Timing floor | Output | Command |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['requires_validation']}` | `{floor}` | `{row['output_json']}` | "
            f"`{' '.join(row['command'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1116 generated runner for an already-running RTX-class Linux pod.",
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
        f'exec > >(tee -a "{payload["report_dir"]}/goal1116_runner.log") 2>&1',
        'echo "Goal1116 current-source RTX rerun packet"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        'echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"',
        'date -u +"utc_start=%Y-%m-%dT%H:%M:%SZ"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["path_name"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append('date -u +"utc_end=%Y-%m-%dT%H:%M:%SZ"')
    lines.append(f'echo "Goal1116 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1116 current-source RTX rerun packet.")
    parser.add_argument("--output-json", default=f"{REPORT_DIR}_2026-04-29.json")
    parser.add_argument("--output-md", default=f"{REPORT_DIR}_2026-04-29.md")
    parser.add_argument("--output-sh", default="scripts/goal1116_current_source_rtx_rerun_runner.sh")
    args = parser.parse_args(argv)
    payload = build_packet()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    sh_path = ROOT / args.output_sh
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"json": str(json_path), "md": str(md_path), "sh": str(sh_path), "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
