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
GOAL = "Goal1062 blocked RTX wording rerun manifest"
REPORT_DIR = "docs/reports/goal1062_blocked_rtx_wording_rerun"


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
    scale_note: str,
    requires_validation: bool,
    timing_floor_sec: float | None,
) -> dict[str, Any]:
    wording = rt.rtx_public_wording_status(app)
    return {
        "app": app,
        "path_name": path_name,
        "phase": phase,
        "purpose": purpose,
        "scale_note": scale_note,
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
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="correctness_validation",
            output_name="robot_prepared_pose_flags_validation.json",
            purpose="Reconfirm oracle parity for the prepared ray/triangle any-hit pose-flag path.",
            scale_note="Small validation scale using python_objects + pose_flags because packed pose_count mode intentionally rejects oracle validation.",
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
            output_name="robot_prepared_pose_flags_large_timing.json",
            purpose="Collect a claim-review timing repeat large enough to test the 100 ms floor.",
            scale_note="High-memory timing run: packed_arrays + pose_count avoids Python row/flag materialization; downscale pose-count if VRAM pressure appears.",
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
    ]
    blocked_apps = sorted(
        app for app, row in rt.rtx_public_wording_matrix().items()
        if row.status == "public_wording_blocked"
    )
    if "robot_collision_screening" not in blocked_apps:
        rows = []
    validation_rows = [row for row in rows if row["phase"] == "correctness_validation"]
    timing_rows = [row for row in rows if row["phase"] == "large_timing_repeat"]
    validation_skip = [row["output_json"] for row in validation_rows if row["contains_skip_validation"]]
    timing_without_floor = [row["output_json"] for row in timing_rows if row["timing_floor_sec"] is None]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "blocked_apps": blocked_apps,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
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
            "Do not use this manifest to authorize public wording without a later artifact-intake and 2+ AI review.",
        ],
        "valid": (
            (
                blocked_apps == []
                and len(rows) == 0
                and len(validation_rows) == 0
                and len(timing_rows) == 0
            )
            or (
                blocked_apps == ["robot_collision_screening"]
                and len(rows) == 2
                and len(validation_rows) == 1
                and len(timing_rows) == 1
                and not validation_skip
                and not timing_without_floor
                and all(row["current_public_wording_status"] == "public_wording_blocked" for row in rows)
            )
        ),
        "boundary": (
            "Goal1062 prepares one batched rerun plan for any remaining blocked NVIDIA RTX wording rows. "
            "It does not run cloud, create resources, authorize release, or authorize public speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1062 Blocked RTX Wording Rerun Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        "",
        payload["boundary"],
        "",
        "## Global Preconditions",
        "",
    ]
    for item in payload["global_preconditions"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| App | Path | Phase | Skip validation | Timing floor | Output | Command |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['contains_skip_validation']}` | `{floor}` | `{row['output_json']}` | "
            f"`{' '.join(row['command'])}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1062 generated runner for an already-running RTX-class Linux pod.",
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
        'echo "Goal1062 blocked RTX wording rerun"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["path_name"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1062 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1062 blocked RTX wording rerun manifest.")
    parser.add_argument("--output-json", default="docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.md")
    parser.add_argument("--output-sh", default="scripts/goal1062_blocked_rtx_wording_rerun_runner.sh")
    args = parser.parse_args(argv)

    payload = build_manifest()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    sh_path = ROOT / args.output_sh
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    sh_path.write_text(to_shell(payload), encoding="utf-8")
    sh_path.chmod(0o755)
    print(json.dumps({"json": str(json_path), "md": str(md_path), "sh": str(sh_path), "valid": payload["valid"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
