#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1084 facility recentered RTX pod packet"
REPORT_DIR = "docs/reports/goal1084_facility_recentered_rtx_pod_packet"


def _command(*parts: str) -> list[str]:
    return list(parts)


def build_packet() -> dict[str, Any]:
    rows = [
        {
            "app": "facility_knn_assignment",
            "path_name": "coverage_threshold_prepared_recentered",
            "phase": "same_scale_validation_and_timing",
            "source_goal": "Goal1083",
            "source_evidence": "docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json",
            "purpose": (
                "Validate and time the precision-safe recentered facility service-coverage decision "
                "at the same 2.5M-copy / 10M-query scale that blocked the global-coordinate row."
            ),
            "requires_validation": True,
            "contains_skip_validation": False,
            "timing_floor_sec": 0.100,
            "output_json": f"{REPORT_DIR}/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
            "command": _command(
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
                "--output-json",
                f"{REPORT_DIR}/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
            ),
        }
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "supersedes_for_facility": [
            "docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json"
        ],
        "source_artifacts": [
            "docs/reports/goal1082_facility_same_scale_baseline_intake_2026-04-29.md",
            "docs/reports/goal1083_facility_recentered_2_5m_cpu_oracle.json",
            "docs/reports/goal1083_facility_recentered_precision_safe_profiler_2026-04-29.md",
        ],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "validation_row_count": sum(1 for row in rows if row["requires_validation"]),
            "rows_with_skip_validation": [row["output_json"] for row in rows if row["contains_skip_validation"]],
            "public_speedup_claim_authorized_count": 0,
        },
        "global_preconditions": [
            "Run only from an already-running RTX-class NVIDIA pod checkout.",
            "Build the OptiX backend from the checked-out commit before commands.",
            "Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.",
            "Do not add --skip-validation. If validation is too expensive, copy back the partial artifact and stop.",
            "Treat this as evidence collection only; no public wording changes are authorized by this runner.",
        ],
        "valid": (
            len(rows) == 1
            and rows[0]["requires_validation"]
            and not rows[0]["contains_skip_validation"]
            and rows[0]["timing_floor_sec"] == 0.100
            and "facility_service_coverage_recentered" in rows[0]["command"]
            and "2500000" in rows[0]["command"]
        ),
        "boundary": (
            "Goal1084 prepares a corrected facility RTX pod run only. It does not create cloud resources, "
            "does not run cloud locally, does not authorize release, does not change public wording, and "
            "does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1084 Facility Recentered RTX Pod Packet",
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
            "| App | Path | Phase | Skip validation | Timing floor | Output | Command |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['contains_skip_validation']}` | `{row['timing_floor_sec']:.3f}` | "
            f"`{row['output_json']}` | `{' '.join(row['command'])}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def to_shell(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1084 generated runner for an already-running RTX-class Linux pod.",
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
        'echo "Goal1084 facility recentered RTX pod packet"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "",
    ]
    for index, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {index}/{len(payload["rows"])}: {row["app"]}:{row["path_name"]}:{row["phase"]}"')
        lines.append(" ".join(row["command"]))
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append(f'echo "Goal1084 complete. Copy back {payload["report_dir"]} before stopping the pod."')
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1084 facility recentered RTX pod packet.")
    parser.add_argument("--output-json", default="docs/reports/goal1084_facility_recentered_rtx_pod_packet_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1084_facility_recentered_rtx_pod_packet_2026-04-29.md")
    parser.add_argument("--output-sh", default="scripts/goal1084_facility_recentered_rtx_pod_packet_runner.sh")
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
