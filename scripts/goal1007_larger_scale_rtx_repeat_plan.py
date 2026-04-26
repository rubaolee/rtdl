#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-26"
GOAL = "Goal1007 larger-scale RTX repeat plan"
SOURCE = ROOT / "docs" / "reports" / "goal1006_public_rtx_claim_wording_gate_2026-04-26.json"


TARGETS: tuple[dict[str, Any], ...] = (
    {
        "app": "robot_collision_screening",
        "path_name": "prepared_pose_flags",
        "scale_reason": "Increase ray count enough that warm pose-count query should exceed the 100 ms wording floor.",
        "risk_note": "High memory run: 8M poses means 32M packed rays; intended for 24GB+ RTX pods and may need downscaling if VRAM pressure appears.",
        "command": [
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
            "--output-json",
            "docs/reports/goal1007_robot_pose_flags_large_rtx.json",
        ],
    },
    {
        "app": "outlier_detection",
        "path_name": "prepared_fixed_radius_density_summary",
        "scale_reason": "Raise tiled point count for scalar threshold-count traversal.",
        "risk_note": "Moderate memory run: 3.2M points; if pod memory is tight, reduce copies before changing semantics.",
        "command": [
            "python3",
            "scripts/goal757_optix_fixed_radius_prepared_perf.py",
            "--copies",
            "400000",
            "--iterations",
            "7",
            "--result-mode",
            "threshold_count",
            "--skip-validation",
            "--output-json",
            "docs/reports/goal1007_outlier_dbscan_large_rtx.json",
        ],
    },
    {
        "app": "dbscan_clustering",
        "path_name": "prepared_fixed_radius_core_flags",
        "scale_reason": "Same fixed-radius command emits both outlier and DBSCAN scalar summaries.",
        "risk_note": "No separate command; validate both app records from the shared fixed-radius JSON.",
        "command_ref": "outlier_detection/prepared_fixed_radius_density_summary",
        "reused_output_json": "docs/reports/goal1007_outlier_dbscan_large_rtx.json",
    },
    {
        "app": "facility_knn_assignment",
        "path_name": "coverage_threshold_prepared",
        "scale_reason": "Raise facility service-coverage copies for a stable threshold query phase.",
        "risk_note": "Moderate memory run: 3.2M build/query points; validation is skipped for cost control.",
        "command": [
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
            "--output-json",
            "docs/reports/goal1007_facility_service_coverage_large_rtx.json",
        ],
    },
    {
        "app": "segment_polygon_hitcount",
        "path_name": "segment_polygon_hitcount_native_experimental",
        "scale_reason": "Raise segment/polygon copies for native hitcount traversal while keeping validation skipped for cost control.",
        "risk_note": "Output is scalar hitcount summary, so memory risk is mostly geometry/ray staging.",
        "command": [
            "python3",
            "scripts/goal933_prepared_segment_polygon_optix_profiler.py",
            "--scenario",
            "segment_polygon_hitcount_prepared",
            "--copies",
            "8192",
            "--iterations",
            "7",
            "--mode",
            "run",
            "--skip-validation",
            "--output-json",
            "docs/reports/goal1007_segment_polygon_hitcount_large_rtx.json",
        ],
    },
    {
        "app": "segment_polygon_anyhit_rows",
        "path_name": "segment_polygon_anyhit_rows_prepared_bounded_gate",
        "scale_reason": "Raise bounded pair-row copies and capacity; output remains bounded and overflow must stay false.",
        "risk_note": "Bounded output capacity is raised to 131072; any overflow keeps this row out of public wording.",
        "command": [
            "python3",
            "scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py",
            "--copies",
            "8192",
            "--iterations",
            "7",
            "--output-capacity",
            "131072",
            "--mode",
            "run",
            "--skip-validation",
            "--output-json",
            "docs/reports/goal1007_segment_polygon_anyhit_rows_large_rtx.json",
        ],
    },
    {
        "app": "ann_candidate_search",
        "path_name": "candidate_threshold_prepared",
        "scale_reason": "Raise ANN candidate copies for stable threshold-query timing.",
        "risk_note": "Moderate memory run: 2.4M query/candidate points; validation is skipped for cost control.",
        "command": [
            "python3",
            "scripts/goal887_prepared_decision_phase_profiler.py",
            "--scenario",
            "ann_candidate_coverage",
            "--mode",
            "optix",
            "--copies",
            "800000",
            "--iterations",
            "7",
            "--radius",
            "0.2",
            "--skip-validation",
            "--output-json",
            "docs/reports/goal1007_ann_candidate_coverage_large_rtx.json",
        ],
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_plan(source: Path = SOURCE) -> dict[str, Any]:
    source_payload = _load_json(source)
    held = {
        (row["app"], row["path_name"])
        for row in source_payload["rows"]
        if row["public_wording_status"] == "candidate_but_needs_larger_scale_repeat"
    }
    target_keys = {(row["app"], row["path_name"]) for row in TARGETS}
    missing = sorted(f"{app}/{path}" for app, path in held - target_keys)
    extra = sorted(f"{app}/{path}" for app, path in target_keys - held)
    executable = [row for row in TARGETS if "command" in row]
    return {
        "goal": GOAL,
        "date": DATE,
        "source": str(source.relative_to(ROOT)),
        "held_candidate_count": len(held),
        "target_count": len(TARGETS),
        "executable_command_count": len(executable),
        "missing_held_candidates": missing,
        "extra_targets": extra,
        "targets": TARGETS,
        "status": "ok" if not missing and not extra else "needs_attention",
        "boundary": (
            "Goal1007 prepares larger-scale RTX repeats for held Goal1006 candidates. "
            "It does not start cloud resources and does not authorize speedup claims."
        ),
    }


def _shell_line(command: list[str]) -> str:
    return " ".join(command)


def write_shell(plan: dict[str, Any], output: Path) -> None:
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Goal1007 larger-scale RTX repeat commands.",
        "# Run only from an already-running RTX pod checkout.",
        "# Boundary: does not create cloud resources and does not authorize speedup claims.",
        "",
        'export PYTHONPATH="${PYTHONPATH:-src:.}"',
        'export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"',
        'export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12.4}"',
        'export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"',
        'export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"',
        'export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"',
        'export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"',
        "",
        "mkdir -p docs/reports",
        "",
        'echo "Goal1007 larger-scale RTX repeats"',
        "nvidia-smi",
        "",
    ]
    for target in plan["targets"]:
        command = target.get("command")
        if not command:
            lines.append(f"# {target['app']} / {target['path_name']} reuses {target['reused_output_json']}")
            continue
        lines.append(f"echo 'Running {target['app']} / {target['path_name']}'")
        lines.append(_shell_line(command))
        lines.append("")
    lines.extend(
        [
            "python3 scripts/goal1007_larger_scale_rtx_repeat_plan.py \\",
            "  --audit-existing \\",
            "  --output-json docs/reports/goal1007_larger_scale_rtx_repeat_plan_pod_audit.json \\",
            "  --output-md docs/reports/goal1007_larger_scale_rtx_repeat_plan_pod_audit.md",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output.chmod(0o755)


def _existing_outputs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in plan["targets"]:
        output = None
        command = target.get("command")
        if isinstance(command, list):
            for index, token in enumerate(command):
                if token == "--output-json" and index + 1 < len(command):
                    output = command[index + 1]
                    break
        else:
            output = target.get("reused_output_json")
        path = ROOT / str(output)
        rows.append(
            {
                "app": target["app"],
                "path_name": target["path_name"],
                "output_json": output,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return rows


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1007 Larger-Scale RTX Repeat Plan",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- status: `{payload['status']}`",
        f"- held candidates: `{payload['held_candidate_count']}`",
        f"- targets: `{payload['target_count']}`",
        f"- executable commands: `{payload['executable_command_count']}`",
        "",
        "## Targets",
        "",
        "| App | Path | Command? | Reason | Risk note |",
        "|---|---|---:|---|---|",
    ]
    for target in payload["targets"]:
        lines.append(
            f"| `{target['app']}` | `{target['path_name']}` | "
            f"`{'command' in target}` | {target['scale_reason']} | {target['risk_note']} |"
        )
    if "existing_outputs" in payload:
        lines.extend(["", "## Existing Output Audit", "", "| App | Path | Exists | Size |", "|---|---|---:|---:|"])
        for row in payload["existing_outputs"]:
            lines.append(
                f"| `{row['app']}` | `{row['path_name']}` | `{row['exists']}` | {row['size_bytes']} |"
            )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build larger-scale RTX repeat plan for held candidates.")
    parser.add_argument("--source", default=str(SOURCE))
    parser.add_argument("--output-json", default="docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1007_larger_scale_rtx_repeat_plan_2026-04-26.md")
    parser.add_argument("--output-sh")
    parser.add_argument("--audit-existing", action="store_true")
    args = parser.parse_args()
    plan = build_plan(Path(args.source))
    if args.audit_existing:
        plan = {**plan, "existing_outputs": _existing_outputs(plan)}
    Path(args.output_json).write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(plan), encoding="utf-8")
    if args.output_sh:
        write_shell(plan, Path(args.output_sh))
    print(to_markdown(plan))
    return 0 if plan["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
