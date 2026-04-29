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
GOAL = "Goal1072 post-scale-up RTX pod batch"
REPORT_DIR = "docs/reports/goal1072_post_scale_up_rtx_pod_batch"
FACILITY_EVIDENCE = "docs/reports/goal1071_scale_up_probes/facility_coverage_threshold_2_5m_timing.json"
ROBOT_EVIDENCE = "docs/reports/goal1071_scale_up_probes/robot_prepared_pose_flags_36m_timing.json"
BARNES_EVIDENCE = "docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_1m_timing.json"


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
    source_goal: str,
    source_evidence: str | None,
) -> dict[str, Any]:
    wording = rt.rtx_public_wording_status(app)
    return {
        "app": app,
        "path_name": path_name,
        "phase": phase,
        "source_goal": source_goal,
        "source_evidence": source_evidence,
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
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared",
            phase="correctness_validation",
            output_name="facility_coverage_threshold_validation.json",
            purpose="Reconfirm oracle parity for prepared facility service-coverage decision.",
            requires_validation=True,
            timing_floor_sec=None,
            source_goal="Goal1068",
            source_evidence="docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json",
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "facility_service_coverage",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--iterations",
                "10",
                "--radius",
                "1.0",
            ),
        ),
        _row(
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared",
            phase="large_timing_repeat",
            output_name="facility_coverage_threshold_2_5m_timing.json",
            purpose="Repeat the Goal1071 scale that crossed the 100 ms RTX-query review floor.",
            requires_validation=False,
            timing_floor_sec=0.100,
            source_goal="Goal1071",
            source_evidence=FACILITY_EVIDENCE,
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "facility_service_coverage",
                "--mode",
                "optix",
                "--copies",
                "2500000",
                "--iterations",
                "5",
                "--radius",
                "1.0",
                "--skip-validation",
            ),
        ),
        _row(
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="correctness_validation",
            output_name="robot_prepared_pose_flags_validation.json",
            purpose="Reconfirm oracle parity for prepared ray/triangle pose-flag path.",
            requires_validation=True,
            timing_floor_sec=None,
            source_goal="Goal1068",
            source_evidence="docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json",
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
            output_name="robot_prepared_pose_flags_36m_timing.json",
            purpose="Repeat the Goal1071 36M-pose scale that crossed the 100 ms warm-query review floor.",
            requires_validation=False,
            timing_floor_sec=0.100,
            source_goal="Goal1071",
            source_evidence=ROBOT_EVIDENCE,
            command=_command(
                "python3",
                "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                "--mode",
                "optix",
                "--pose-count",
                "36000000",
                "--obstacle-count",
                "4096",
                "--iterations",
                "5",
                "--input-mode",
                "packed_arrays",
                "--result-mode",
                "pose_count",
                "--skip-validation",
            ),
        ),
    ]
    excluded_rows = [
        {
            "app": "barnes_hut_force_app",
            "path_name": "node_coverage_prepared",
            "exclusion_status": "blocked_contract_reframe_required",
            "source_goal": "Goal1071",
            "source_evidence": BARNES_EVIDENCE,
            "reason": (
                "The current Barnes-Hut node-coverage contract builds only four one-level quadtree nodes. "
                "The 1M-body pod run produced a 0.004204 s median RT query, so blind body-count scaling "
                "mostly measures input construction/packing rather than meaningful RTX traversal."
            ),
            "next_move": (
                "Design a richer node/tree traversal contract before the next paid pod attempt; do not "
                "spend cloud time by simply increasing body_count under the current four-node build."
            ),
        }
    ]
    validation_rows = [row for row in rows if row["phase"] == "correctness_validation"]
    timing_rows = [row for row in rows if row["phase"] == "large_timing_repeat"]
    validation_skip = [row["output_json"] for row in validation_rows if row["contains_skip_validation"]]
    timing_without_floor = [row["output_json"] for row in timing_rows if row["timing_floor_sec"] is None]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "supersedes": [
            "docs/reports/goal1068_next_rtx_pod_efficiency_batch_2026-04-28.json",
            "docs/reports/goal1070_goal1068_artifact_intake_after_pod_2026-04-28.json",
        ],
        "source_artifacts": [
            "docs/reports/goal1071_rtx_pod_scale_up_result_2026-04-28.md",
            FACILITY_EVIDENCE,
            ROBOT_EVIDENCE,
            BARNES_EVIDENCE,
        ],
        "rows": rows,
        "excluded_rows": excluded_rows,
        "summary": {
            "row_count": len(rows),
            "app_count": len({row["app"] for row in rows}),
            "validation_row_count": len(validation_rows),
            "timing_row_count": len(timing_rows),
            "excluded_row_count": len(excluded_rows),
            "validation_rows_with_skip_validation": validation_skip,
            "timing_rows_without_floor": timing_without_floor,
        },
        "global_preconditions": [
            "Run only from an already-running RTX-class NVIDIA pod checkout.",
            "Build the OptiX backend from the checked-out commit before commands.",
            "Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.",
            "Copy the whole Goal1072 report directory back before stopping or terminating the pod.",
            "Treat this as evidence collection only; no public wording changes are authorized by this runner.",
        ],
        "valid": (
            len(rows) == 4
            and len(validation_rows) == 2
            and len(timing_rows) == 2
            and len(excluded_rows) == 1
            and excluded_rows[0]["app"] == "barnes_hut_force_app"
            and not validation_skip
            and not timing_without_floor
            and all(row["timing_floor_sec"] == 0.100 for row in timing_rows)
            and any("2500000" in row["command"] for row in timing_rows)
            and any("36000000" in row["command"] for row in timing_rows)
        ),
        "boundary": (
            "Goal1072 is a local superseding pod-batch plan based on Goal1071 evidence. It does not run cloud, "
            "does not create resources, does not authorize release, does not change public wording, and does not "
            "authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1072 Post-Scale-Up RTX Pod Batch",
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
            "## Active Rows",
            "",
            "| App | Path | Phase | Source | Skip validation | Timing floor | Output | Command |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | `{row['source_goal']}` | "
            f"`{row['contains_skip_validation']}` | `{floor}` | `{row['output_json']}` | "
            f"`{' '.join(row['command'])}` |"
        )
    lines.extend(
        [
            "",
            "## Excluded Rows",
            "",
            "| App | Path | Status | Reason | Next move |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["excluded_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['exclusion_status']}` | "
            f"{row['reason']} | {row['next_move']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1072 generated runner for an already-running RTX-class Linux pod.",
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
        'echo "Goal1072 post-scale-up RTX pod batch"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["path_name"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1072 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1072 post-scale-up RTX pod batch.")
    parser.add_argument("--output-json", default="docs/reports/goal1072_post_scale_up_rtx_pod_batch_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1072_post_scale_up_rtx_pod_batch_2026-04-28.md")
    parser.add_argument("--output-sh", default="scripts/goal1072_post_scale_up_rtx_pod_batch_runner.sh")
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
