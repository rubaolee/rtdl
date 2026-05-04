#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1166 post-Goal1165 next RTX pod packet"
REPORT_DIR = "docs/reports/goal1166_post_goal1165_next_rtx_pod_packet"


def _command(*parts: str) -> list[str]:
    return list(parts)


def _row(
    *,
    label: str,
    app: str,
    path_name: str,
    phase: str,
    output_name: str,
    command: list[str],
    purpose: str,
    requires_validation: bool,
    timing_floor_sec: float | None,
    expected_goal1165_effect: str,
) -> dict[str, Any]:
    output_json = f"{REPORT_DIR}/{output_name}"
    return {
        "label": label,
        "app": app,
        "path_name": path_name,
        "phase": phase,
        "purpose": purpose,
        "requires_validation": requires_validation,
        "contains_skip_validation": "--skip-validation" in command,
        "timing_floor_sec": timing_floor_sec,
        "expected_goal1165_effect": expected_goal1165_effect,
        "output_json": output_json,
        "command": command + ["--output-json", output_json],
    }


def build_manifest() -> dict[str, Any]:
    rows = [
        _row(
            label="ann_candidate_validation",
            app="ann_candidate_search",
            path_name="candidate_threshold_prepared",
            phase="correctness_validation",
            output_name="ann_candidate_8192_validation.json",
            purpose="Validate the post-Goal1165 tiled-oracle shortcut on RTX at the recovery scale.",
            requires_validation=True,
            timing_floor_sec=None,
            expected_goal1165_effect="Validation should use single-tile projection instead of expanded O(copies^2) oracle.",
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "ann_candidate_coverage",
                "--mode",
                "optix",
                "--copies",
                "8192",
                "--iterations",
                "3",
                "--radius",
                "0.2",
            ),
        ),
        _row(
            label="ann_candidate_large_timing",
            app="ann_candidate_search",
            path_name="candidate_threshold_prepared",
            phase="large_timing_repeat",
            output_name="ann_candidate_65536_timing.json",
            purpose="Rerun the Goal1164 timeout scale after removing accidental O(copies^2) validation.",
            requires_validation=False,
            timing_floor_sec=0.100,
            expected_goal1165_effect="Should complete without the previous 600 s validation timeout.",
            command=_command(
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "ann_candidate_coverage",
                "--mode",
                "optix",
                "--copies",
                "65536",
                "--iterations",
                "7",
                "--radius",
                "0.2",
                "--skip-validation",
            ),
        ),
        _row(
            label="robot_pose_flags_validation",
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="correctness_validation",
            output_name="robot_pose_flags_32768_validation.json",
            purpose="Validate scaled robot pose flags with the analytic fixture oracle.",
            requires_validation=True,
            timing_floor_sec=None,
            expected_goal1165_effect="Should validate without CPU any-hit oracle row materialization.",
            command=_command(
                "python3",
                "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                "--mode",
                "optix",
                "--pose-count",
                "32768",
                "--obstacle-count",
                "64",
                "--iterations",
                "3",
                "--input-mode",
                "python_objects",
                "--result-mode",
                "pose_flags",
            ),
        ),
        _row(
            label="robot_pose_flags_large_timing",
            app="robot_collision_screening",
            path_name="prepared_pose_flags",
            phase="large_timing_repeat",
            output_name="robot_pose_flags_262144_timing.json",
            purpose="Rerun the Goal1164 timeout scale using packed arrays and timing-only validation policy.",
            requires_validation=False,
            timing_floor_sec=0.100,
            expected_goal1165_effect="Should avoid CPU oracle and public-app Python object overhead.",
            command=_command(
                "python3",
                "scripts/goal760_optix_robot_pose_flags_phase_profiler.py",
                "--mode",
                "optix",
                "--pose-count",
                "262144",
                "--obstacle-count",
                "64",
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
            label="jaccard_safe_chunk_validation",
            app="polygon_set_jaccard",
            path_name="optix_native_assisted_candidate_discovery",
            phase="safe_chunk_validation",
            output_name="polygon_jaccard_8192_chunk1024_validation.json",
            purpose="Confirm the superseding safe default chunk size on RTX at the Goal1164 Jaccard scale.",
            requires_validation=True,
            timing_floor_sec=None,
            expected_goal1165_effect="Should pass parity with chunk_copies=1024.",
            command=_command(
                "python3",
                "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                "--app",
                "jaccard",
                "--mode",
                "optix",
                "--copies",
                "8192",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "1024",
            ),
        ),
        _row(
            label="jaccard_boundary_diagnostic_small_chunk",
            app="polygon_set_jaccard",
            path_name="optix_native_assisted_candidate_discovery",
            phase="boundary_diagnostic",
            output_name="polygon_jaccard_8192_chunk256_diagnostic.json",
            purpose="Retain one known-risk chunk-boundary diagnostic so future fixes can prove the bug is gone.",
            requires_validation=True,
            timing_floor_sec=None,
            expected_goal1165_effect="Expected to fail until arbitrary chunk-boundary semantics are fixed.",
            command=_command(
                "python3",
                "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                "--app",
                "jaccard",
                "--mode",
                "optix",
                "--copies",
                "8192",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "256",
            ),
        ),
    ]
    validation_rows = [row for row in rows if row["requires_validation"]]
    timing_rows = [row for row in rows if row["phase"] == "large_timing_repeat"]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "source_artifacts": [
            "docs/reports/goal1164_rtx_pod_batch_2026-04-30/goal1164_rtx_pod_batch_report_2026-04-30.md",
            "docs/reports/goal1165_local_rtx_app_perf_followup_2026-04-30.md",
            "docs/reports/goal1165_two_ai_consensus_2026-04-30.md",
        ],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "app_count": len({row["app"] for row in rows}),
            "validation_row_count": len(validation_rows),
            "timing_row_count": len(timing_rows),
            "timing_rows_without_skip_validation": [
                row["output_json"] for row in timing_rows if not row["contains_skip_validation"]
            ],
            "timing_rows_without_floor": [
                row["output_json"] for row in timing_rows if row["timing_floor_sec"] is None
            ],
            "expected_boundary_failures": ["polygon_jaccard_8192_chunk256_diagnostic.json"],
        },
        "global_preconditions": [
            "Run only from an already-running RTX-class NVIDIA pod checkout.",
            "Build OptiX with driver-compatible headers before running the packet.",
            "For driver 550/CUDA 13, use OptiX headers v8.0.0 and RTDL_OPTIX_PTX_COMPILER=nvcc.",
            "Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.",
            "Copy the whole report directory back before stopping or terminating the pod.",
        ],
        "valid": True,
        "boundary": (
            "Goal1166 prepares one focused post-Goal1165 RTX pod batch. It does not create "
            "cloud resources, does not authorize public wording, and does not turn timing-only "
            "skip-validation artifacts into correctness evidence."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1166 Post-Goal1165 Next RTX Pod Packet",
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
            "| Label | App | Phase | Skip validation | Timing floor | Output | Command |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        floor = "" if row["timing_floor_sec"] is None else f"{row['timing_floor_sec']:.3f}"
        lines.append(
            f"| `{row['label']}` | `{row['app']}` | `{row['phase']}` | "
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
        "# Goal1166 generated runner for an already-running RTX-class Linux pod.",
        "# Boundary: does not create cloud resources and does not authorize speedup claims.",
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        'export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"',
        'export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"',
        'export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"',
        'export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"',
        'export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"',
        'export LD_LIBRARY_PATH="${CUDA_PREFIX}/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"',
        'export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"',
        "",
        'if [ -z "${RTDL_SOURCE_COMMIT}" ]; then',
        '  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2',
        "  exit 2",
        "fi",
        "",
        f"mkdir -p {payload['report_dir']}",
        'echo "Goal1166 post-Goal1165 next RTX pod packet"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["label"]}"')
        if row["label"] == "jaccard_boundary_diagnostic_small_chunk":
            lines.append("set +e")
            lines.append(" ".join(row["command"]))
            lines.append("status=$?")
            lines.append("set -e")
            lines.append('echo "Boundary diagnostic exit status=${status} (non-zero is expected until fixed)"')
        else:
            lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1166 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1166 post-Goal1165 RTX pod packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1166_post_goal1165_next_rtx_pod_packet_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1166_post_goal1165_next_rtx_pod_packet_2026-04-30.md")
    parser.add_argument("--output-sh", default="scripts/goal1166_post_goal1165_next_rtx_pod_packet_runner.sh")
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
