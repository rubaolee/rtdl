#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1170 clean-source RTX claim-grade batch manifest"
REPORT_DIR = "docs/reports/goal1170_clean_source_rtx_claim_grade_batch"
DEFAULT_JSON = ROOT / "docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1170_clean_source_rtx_batch_manifest_2026-04-30.md"
DEFAULT_RUNNER = ROOT / "scripts/goal1170_clean_source_rtx_batch_runner.sh"


def _row(
    label: str,
    app: str,
    public_wording_state: str,
    purpose: str,
    output_name: str,
    command: list[str],
    *,
    requires_validation: bool = True,
    expected_failure: bool = False,
) -> dict[str, Any]:
    output_json = f"{REPORT_DIR}/{output_name}"
    return {
        "label": label,
        "app": app,
        "public_wording_state": public_wording_state,
        "purpose": purpose,
        "requires_validation": requires_validation,
        "contains_skip_validation": "--skip-validation" in command,
        "expected_failure": expected_failure,
        "output_json": output_json,
        "command": command + ["--output-json", output_json],
    }


def build_manifest() -> dict[str, Any]:
    rows = [
        _row(
            "database_compact_summary",
            "database_analytics",
            "public_wording_not_reviewed",
            "Collect clean-source compact-summary DB traversal/filter/grouping evidence.",
            "database_compact_summary.json",
            [
                "python3",
                "scripts/goal756_db_prepared_session_perf.py",
                "--backend",
                "optix",
                "--scenario",
                "sales_risk",
                "--copies",
                "20000",
                "--iterations",
                "10",
                "--output-mode",
                "compact_summary",
                "--strict",
            ],
        ),
        _row(
            "graph_visibility_edges",
            "graph_analytics",
            "public_wording_not_reviewed",
            "Collect clean-source bounded graph visibility any-hit evidence.",
            "graph_visibility_edges.json",
            [
                "python3",
                "scripts/goal889_graph_visibility_optix_gate.py",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "0",
                "--strict",
            ],
        ),
        _row(
            "road_hazard_native_summary",
            "road_hazard_screening",
            "public_wording_not_reviewed",
            "Collect clean-source prepared native road-hazard compact-summary evidence.",
            "road_hazard_native_summary.json",
            [
                "python3",
                "scripts/goal933_prepared_segment_polygon_optix_profiler.py",
                "--scenario",
                "road_hazard_prepared_summary",
                "--copies",
                "20000",
                "--iterations",
                "5",
                "--mode",
                "run",
            ],
        ),
        _row(
            "polygon_pair_candidate_discovery",
            "polygon_pair_overlap_area_rows",
            "public_wording_not_reviewed",
            "Collect clean-source LSI/PIP candidate-discovery evidence split from exact area continuation.",
            "polygon_pair_candidate_discovery.json",
            [
                "python3",
                "scripts/goal877_polygon_overlap_optix_phase_profiler.py",
                "--app",
                "pair_overlap",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--output-mode",
                "summary",
                "--validation-mode",
                "analytic_summary",
                "--chunk-copies",
                "100",
            ],
        ),
        _row(
            "polygon_jaccard_safe_chunk",
            "polygon_set_jaccard",
            "public_wording_not_reviewed",
            "Collect clean-source safe chunk Jaccard candidate-discovery evidence.",
            "polygon_jaccard_safe_chunk.json",
            [
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
                "512",
            ],
        ),
        _row(
            "hausdorff_threshold_prepared",
            "hausdorff_distance",
            "public_wording_not_reviewed",
            "Collect clean-source prepared Hausdorff threshold-decision evidence.",
            "hausdorff_threshold_prepared.json",
            [
                "python3",
                "scripts/goal887_prepared_decision_phase_profiler.py",
                "--scenario",
                "hausdorff_threshold",
                "--mode",
                "optix",
                "--copies",
                "20000",
                "--iterations",
                "10",
                "--radius",
                "0.4",
            ],
        ),
        _row(
            "ann_candidate_large_timing_replacement",
            "ann_candidate_search",
            "public_wording_reviewed",
            "Replace dirty Goal1166 ANN large timing with clean-source timing paired with prior validation row.",
            "ann_candidate_65536_timing.json",
            [
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
            ],
            requires_validation=False,
        ),
        _row(
            "robot_pose_count_large_timing_replacement",
            "robot_collision_screening",
            "public_wording_reviewed",
            "Replace dirty Goal1166 robot pose-count timing with clean-source normalized timing.",
            "robot_pose_count_262144_timing.json",
            [
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
            ],
            requires_validation=False,
        ),
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "report_dir": REPORT_DIR,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "not_reviewed_public_wording_rows": sum(
                row["public_wording_state"] == "public_wording_not_reviewed" for row in rows
            ),
            "clean_replacement_rows": sum(
                row["public_wording_state"] == "public_wording_reviewed" for row in rows
            ),
            "skip_validation_rows": [row["label"] for row in rows if row["contains_skip_validation"]],
        },
        "source_policy": (
            "Runner refuses claim-grade collection if git status is dirty. Dirty or pod-patched "
            "runs are engineering evidence only and must not be used for public wording."
        ),
        "valid": True,
        "boundary": (
            "This manifest prepares one clean-source RTX pod batch. It does not create cloud "
            "resources and does not authorize public speedup wording."
        ),
    }


def to_runner(payload: dict[str, Any]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1170 clean-source RTX batch runner.",
        "# Run from a clean pushed checkout on an already-running RTX-class pod.",
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        'export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"',
        'export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"',
        'export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"',
        'export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"',
        'export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"',
        'export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-${RTDL_OPTIX_LIBRARY}}"',
        'export LD_LIBRARY_PATH="${CUDA_PREFIX}/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"',
        'export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(git rev-parse HEAD)}"',
        "",
        'if [ -n "$(git status --short)" ]; then',
        '  echo "Refusing claim-grade run: git working tree is dirty." >&2',
        "  git status --short >&2",
        "  exit 2",
        "fi",
        "",
        'mkdir -p "docs/reports/goal1170_clean_source_rtx_claim_grade_batch"',
        'echo "Goal1170 clean-source RTX claim-grade batch"',
        'echo "source_commit=${RTDL_SOURCE_COMMIT}"',
        "nvidia-smi",
        "python3 scripts/goal1171_clean_source_rtx_pod_preflight.py "
        "--output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.json "
        "--output-md docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.md",
        "",
    ]
    total = len(payload["rows"])
    for idx, row in enumerate(payload["rows"], start=1):
        lines.append(f'echo "Running {idx}/{total}: {row["label"]}"')
        if row["expected_failure"]:
            lines.append("set +e")
        lines.append(" ".join(row["command"]))
        if row["expected_failure"]:
            lines.append("status=$?")
            lines.append("set -e")
            lines.append('echo "Expected diagnostic exit status=${status}"')
        lines.append(f'echo "Completed {row["output_json"]}"')
        lines.append("")
    lines.append('echo "Goal1170 batch complete. Copy back docs/reports/goal1170_clean_source_rtx_claim_grade_batch."')
    return "\n".join(lines) + "\n"


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1170 Clean-Source RTX Batch Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| Label | App | Public wording state | Validation | Output |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['app']}` | `{row['public_wording_state']}` | "
            f"`{row['requires_validation']}` | `{row['output_json']}` |"
        )
    lines.extend(
        [
            "",
            "## Source Policy",
            "",
            payload["source_policy"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Goal1170 clean-source RTX batch manifest.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--output-runner", type=Path, default=DEFAULT_RUNNER)
    args = parser.parse_args(argv)
    payload = build_manifest()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    args.output_runner.write_text(to_runner(payload), encoding="utf-8")
    args.output_runner.chmod(0o755)
    print(json.dumps({"valid": payload["valid"], "row_count": len(payload["rows"])}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
