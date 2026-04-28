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
GOAL = "Goal1068 next RTX pod efficiency batch"
REPORT_DIR = "docs/reports/goal1068_next_rtx_pod_efficiency_batch"
GOAL1067 = ROOT / "docs/reports/goal1067_scale_contract_repair_audit_2026-04-28.json"


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
) -> dict[str, Any]:
    wording = rt.rtx_public_wording_status(app)
    return {
        "app": app,
        "path_name": path_name,
        "phase": phase,
        "source_goal": source_goal,
        "purpose": purpose,
        "current_public_wording_status": wording.status,
        "current_public_wording_boundary": wording.boundary,
        "requires_validation": requires_validation,
        "contains_skip_validation": "--skip-validation" in command,
        "timing_floor_sec": timing_floor_sec,
        "output_json": f"{REPORT_DIR}/{output_name}",
        "command": command + ["--output-json", f"{REPORT_DIR}/{output_name}"],
    }


def _goal1067_barnes_ready() -> bool:
    payload = json.loads(GOAL1067.read_text(encoding="utf-8"))
    rows = {row["app"]: row for row in payload["rows"]}
    barnes = rows.get("barnes_hut_force_app")
    return bool(
        payload.get("valid")
        and barnes
        and barnes["decision"] == "pod_candidate_after_review"
        and barnes["recommended_cloud_scale"]["body_count"] == 1_000_000
    )


def build_manifest() -> dict[str, Any]:
    barnes_ready = _goal1067_barnes_ready()
    rows = [
        _row(
            app="facility_knn_assignment",
            path_name="coverage_threshold_prepared",
            phase="correctness_validation",
            output_name="facility_coverage_threshold_validation.json",
            purpose="Reconfirm oracle parity for prepared facility service-coverage decision.",
            requires_validation=True,
            timing_floor_sec=None,
            source_goal="Goal1062",
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
            output_name="facility_coverage_threshold_large_timing.json",
            purpose="Collect large timing repeat for the prepared facility service-coverage decision.",
            requires_validation=False,
            timing_floor_sec=0.100,
            source_goal="Goal1062",
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "facility_service_coverage",
                "--mode",
                "optix",
                "--copies",
                "800000",
                "--iterations",
                "7",
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
            source_goal="Goal1062",
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
            output_name="robot_prepared_pose_flags_large_timing.json",
            purpose="Collect large timing repeat for packed pose-count prepared ray/triangle path.",
            requires_validation=False,
            timing_floor_sec=0.100,
            source_goal="Goal1062",
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
            path_name="node_coverage_prepared",
            phase="correctness_validation",
            output_name="barnes_hut_node_coverage_validation.json",
            purpose="Run one smaller validated RTX pass before the 1M timing repeat.",
            requires_validation=True,
            timing_floor_sec=None,
            source_goal="Goal1067",
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "barnes_hut_node_coverage",
                "--mode",
                "optix",
                "--body-count",
                "200000",
                "--iterations",
                "3",
                "--radius",
                "10.0",
            ),
        ),
        _row(
            app="barnes_hut_force_app",
            path_name="node_coverage_prepared",
            phase="large_timing_repeat",
            output_name="barnes_hut_node_coverage_1m_timing.json",
            purpose="Collect reviewed 1M-body node-coverage timing repeat after Goal1067 scale-contract repair.",
            requires_validation=False,
            timing_floor_sec=0.100,
            source_goal="Goal1067",
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
                "7",
                "--radius",
                "10.0",
                "--skip-validation",
            ),
        ),
    ]
    validation_rows = [row for row in rows if row["phase"] == "correctness_validation"]
    timing_rows = [row for row in rows if row["phase"] == "large_timing_repeat"]
    validation_skip = [row["output_json"] for row in validation_rows if row["contains_skip_validation"]]
    timing_without_floor = [row["output_json"] for row in timing_rows if row["timing_floor_sec"] is None]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "source_artifacts": [
            "docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.json",
            "docs/reports/goal1067_scale_contract_repair_audit_2026-04-28.json",
        ],
        "goal1067_barnes_ready": barnes_ready,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "app_count": len({row["app"] for row in rows}),
            "validation_row_count": len(validation_rows),
            "timing_row_count": len(timing_rows),
            "validation_rows_with_skip_validation": validation_skip,
            "timing_rows_without_floor": timing_without_floor,
        },
        "global_preconditions": [
            "Run only from an already-running RTX-class NVIDIA pod checkout.",
            "Build the OptiX backend from the checked-out commit before commands.",
            "Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.",
            "Copy the whole report directory back before stopping or terminating the pod.",
            "Treat this as evidence collection only; no public wording changes are authorized by this runner.",
        ],
        "valid": (
            barnes_ready
            and len(rows) == 6
            and len(validation_rows) == 3
            and len(timing_rows) == 3
            and not validation_skip
            and not timing_without_floor
            and all(row["timing_floor_sec"] == 0.100 for row in timing_rows)
        ),
        "boundary": (
            "Goal1068 prepares a larger one-pod evidence batch for facility, robot, and Barnes-Hut. "
            "It does not run cloud, does not create resources, does not authorize release, "
            "does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1068 Next RTX Pod Efficiency Batch",
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
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1068 generated runner for an already-running RTX-class Linux pod.",
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
        'echo "Goal1068 next RTX pod efficiency batch"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["path_name"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1068 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1068 next RTX pod efficiency batch.")
    parser.add_argument("--output-json", default="docs/reports/goal1068_next_rtx_pod_efficiency_batch_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1068_next_rtx_pod_efficiency_batch_2026-04-28.md")
    parser.add_argument("--output-sh", default="scripts/goal1068_next_rtx_pod_efficiency_batch_runner.sh")
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
