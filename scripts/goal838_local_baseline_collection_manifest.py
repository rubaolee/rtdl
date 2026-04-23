#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal835_rtx_baseline_collection_plan import build_plan
from scripts.goal836_rtx_baseline_readiness_gate import expected_artifact_path


GOAL = "Goal838 local RTX baseline collection manifest"
DATE = "2026-04-23"


def _raw_output_path(row: dict[str, Any], baseline: str) -> str:
    return str(expected_artifact_path(row, baseline).with_suffix(".raw.json").relative_to(ROOT))


def _artifact_path(row: dict[str, Any], baseline: str) -> str:
    return str(expected_artifact_path(row, baseline).relative_to(ROOT))


def _db_command(row: dict[str, Any], backend: str, baseline: str) -> list[str]:
    scale = row.get("scale") or {}
    scenario = str(row["path_name"]).removeprefix("prepared_db_session_")
    return [
        "python3",
        "scripts/goal840_db_prepared_baseline.py",
        "--backend",
        backend,
        "--scenario",
        scenario,
        "--copies",
        str(scale.get("copies", 20000)),
        "--iterations",
        str(scale.get("iterations", 10)),
        "--output-json",
        _artifact_path(row, baseline),
    ]


def _db_postgresql_command(row: dict[str, Any], baseline: str) -> list[str]:
    scale = row.get("scale") or {}
    scenario = str(row["path_name"]).removeprefix("prepared_db_session_")
    return [
        "python3",
        "scripts/goal842_postgresql_db_prepared_baseline.py",
        "--scenario",
        scenario,
        "--copies",
        str(scale.get("copies", 20000)),
        "--iterations",
        str(scale.get("iterations", 10)),
        "--output-json",
        _artifact_path(row, baseline),
    ]


def _fixed_radius_command(row: dict[str, Any], baseline: str) -> list[str]:
    scale = row.get("scale") or {}
    backend = "cpu" if baseline == "cpu_scalar_threshold_count_oracle" else "embree"
    return [
        "python3",
        "scripts/goal839_fixed_radius_baseline.py",
        "--app",
        str(row["app"]),
        "--backend",
        backend,
        "--copies",
        str(scale.get("copies", 20000)),
        "--iterations",
        str(scale.get("iterations", 10)),
        "--output-json",
        _artifact_path(row, baseline),
    ]


def _robot_command(row: dict[str, Any], backend: str, baseline: str) -> list[str]:
    scale = row.get("scale") or {}
    return [
        "python3",
        "scripts/goal839_robot_pose_count_baseline.py",
        "--backend",
        backend,
        "--pose-count",
        str(scale.get("pose_count", 200000)),
        "--obstacle-count",
        str(scale.get("obstacle_count", 1024)),
        "--iterations",
        str(scale.get("iterations", 10)),
        "--output-json",
        _artifact_path(row, baseline),
    ]


def _row_actions(row: dict[str, Any]) -> list[dict[str, Any]]:
    app = str(row["app"])
    path_name = str(row["path_name"])
    actions: list[dict[str, Any]] = []
    for baseline in row.get("required_baselines", ()):
        baseline_name = str(baseline)
        action: dict[str, Any] = {
            "section": row["section"],
            "app": app,
            "path_name": path_name,
            "baseline": baseline_name,
            "artifact_path": _artifact_path(row, baseline_name),
            "benchmark_scale": row.get("scale"),
            "required_phases": row.get("required_phases"),
            "comparable_metric_scope": row.get("comparable_metric_scope"),
            "status": "unsupported_local",
            "reason": "no local collector has been assigned for this baseline yet",
            "command": None,
        }
        if app == "database_analytics" and baseline_name == "cpu_oracle_compact_summary":
            action.update(
                {
                    "status": "local_command_ready",
                    "collector_kind": "goal840_db_prepared_baseline",
                    "command": _db_command(row, "cpu", baseline_name),
                    "normalization_required": "none; the collector writes the Goal836 baseline artifact schema directly",
                }
            )
        elif app == "database_analytics" and baseline_name == "embree_compact_summary":
            action.update(
                {
                    "status": "local_command_ready",
                    "collector_kind": "goal840_db_prepared_baseline",
                    "command": _db_command(row, "embree", baseline_name),
                    "normalization_required": "none; the collector writes the Goal836 baseline artifact schema directly",
                }
            )
        elif app == "database_analytics" and baseline_name == "postgresql_same_semantics_on_linux_when_available":
            action.update(
                {
                    "status": "linux_postgresql_required",
                    "collector_kind": "goal842_postgresql_db_prepared_baseline",
                    "command": _db_postgresql_command(row, baseline_name),
                    "reason": "project policy says live PostgreSQL baseline collection is required on Linux, not on this macOS host",
                    "normalization_required": "none; the collector writes the Goal836 baseline artifact schema directly",
                }
            )
        elif app in {"outlier_detection", "dbscan_clustering"} and baseline_name == "embree_scalar_or_summary_path":
            action.update(
                {
                    "status": "local_command_ready",
                    "collector_kind": "goal839_fixed_radius_baseline",
                    "command": _fixed_radius_command(row, baseline_name),
                }
            )
        elif app in {"outlier_detection", "dbscan_clustering"} and baseline_name == "cpu_scalar_threshold_count_oracle":
            action.update(
                {
                    "status": "local_command_ready",
                    "collector_kind": "goal839_fixed_radius_baseline",
                    "command": _fixed_radius_command(row, baseline_name),
                }
            )
        elif app in {"outlier_detection", "dbscan_clustering"} and baseline_name == "scipy_or_reference_neighbor_baseline_when_used_in_app_report":
            action.update(
                {
                    "status": "optional_dependency_or_reference_required",
                    "reason": "SciPy/reference neighbor baseline should be collected only if used in the app report",
                }
            )
        elif app == "robot_collision_screening" and baseline_name == "cpu_oracle_pose_count":
            action.update(
                {
                    "status": "linux_preferred_for_large_exact_oracle",
                    "collector_kind": "goal839_robot_pose_count_baseline",
                    "command": _robot_command(row, "cpu", baseline_name),
                    "reason": "collector exists, but this exact large-scale robot oracle is too expensive for an efficient unattended macOS local batch",
                }
            )
        elif app == "robot_collision_screening" and baseline_name == "embree_anyhit_pose_count_or_equivalent_compact_summary":
            action.update(
                {
                    "status": "linux_preferred_for_large_exact_oracle",
                    "collector_kind": "goal839_robot_pose_count_baseline",
                    "command": _robot_command(row, "embree", baseline_name),
                    "reason": "collector exists, but this exact large-scale robot Embree validation is better collected on Linux in the same batch as the CPU oracle",
                }
            )
        elif row["section"] == "deferred":
            action.update(
                {
                    "status": "deferred_until_app_gate_active",
                    "reason": "deferred baseline should not be collected until the corresponding app activation gate is selected for the batch",
                }
            )
        actions.append(action)
    return actions


def build_collection_manifest() -> dict[str, Any]:
    plan = build_plan()
    actions = [action for row in plan["rows"] for action in _row_actions(row)]
    counts: dict[str, int] = {}
    for action in actions:
        counts[action["status"]] = counts.get(action["status"], 0) + 1
    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_plan_goal": plan["goal"],
        "action_count": len(actions),
        "status_counts": counts,
        "actions": actions,
        "boundary": (
            "This is a local collection manifest only. It does not run heavy benchmarks, "
            "write valid baseline artifacts, start cloud, or authorize speedup claims."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal838 Local RTX Baseline Collection Manifest",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
    ]
    for status, count in sorted(payload["status_counts"].items()):
        lines.append(f"- {status}: `{count}`")
    lines.extend(
        [
            "",
            "## Actions",
            "",
            "| Status | App | Path | Baseline | Scale | Artifact |",
            "|---|---|---|---|---|---|",
        ]
    )
    for action in payload["actions"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(action["status"]),
                    _fmt(action["app"]),
                    _fmt(action["path_name"]),
                    _fmt(action["baseline"]),
                    _fmt(action["benchmark_scale"]),
                    _fmt(action["artifact_path"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Ready Local Commands", ""])
    for action in payload["actions"]:
        if action["status"] != "local_command_ready":
            continue
        lines.append(f"### {action['app']} / {action['path_name']} / {action['baseline']}")
        lines.append("")
        lines.append("```bash")
        lines.append(_fmt(action["command"]))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a local collection manifest for Goal835 baseline artifacts.")
    parser.add_argument("--output-json", default="docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.generated.md")
    args = parser.parse_args(argv)
    payload = build_collection_manifest()
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    (ROOT / args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
