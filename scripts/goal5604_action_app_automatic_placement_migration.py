from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_FILES = (
    ("rtnn", "rtnn-paper/rtdl3_action_migration.py"),
    ("raydb", "raydb-paper/rtdl3_action_migration.py"),
    ("librts", "librts-paper/rtdl3_action_migration.py"),
    ("x_hd", "x-hd-paper/rtdl3_action_migration.py"),
    ("rt_dbscan", "rt-dbscan-paper/rtdl3_action_migration.py"),
    ("rayjoin", "rayjoin-paper/rtdl3_action_migration.py"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _call_names(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.append(node.func.attr)
    return tuple(names)


def build_matrix() -> dict[str, object]:
    apps = []
    for app, relative in APP_FILES:
        path = ROOT / "Paper-reproduction-apps" / relative
        calls = _call_names(path)
        compile_count = (
            calls.count("compile_bound_action_for_target")
            + calls.count("plan_registered_point_bounded_selection")
            + calls.count("plan_registered_fixed_radius_graph_components_3d")
        )
        probe_count = calls.count("detect_action_target_profile")
        apps.append(
            {
                "app": app,
                "path": path.relative_to(ROOT).as_posix(),
                "source_sha256": _sha256(path),
                "compiler_plan_lower_call_count": compile_count,
                "runtime_target_probe_call_count": probe_count,
                "manual_lower_action_call_count": calls.count("lower_action"),
                "app_constructed_target_profile_count": calls.count("ActionTargetProfile"),
                "automatic_placement_consumed": compile_count > 0
                and compile_count == probe_count,
            }
        )

    rtbh_whole = (
        ROOT
        / "Paper-reproduction-apps"
        / "rt-barneshut-paper"
        / "rtdl3_whole_app.py"
    )
    rtbh_adapter = rtbh_whole.parent / "aggregate_hierarchy_adapter.py"
    rtbh_source = rtbh_whole.read_text(encoding="utf-8")
    rtbh_adapter_source = rtbh_adapter.read_text(encoding="utf-8")
    return {
        "schema": "rtdl.research.v3.action_app_automatic_placement_migration.v1",
        "goal": 5604,
        "date": "2026-07-16",
        "action_apps": apps,
        "counts": {
            "action_app_count": len(apps),
            "automatic_placement_app_count": sum(
                bool(row["automatic_placement_consumed"]) for row in apps
            ),
            "compiler_plan_lower_call_count": sum(
                int(row["compiler_plan_lower_call_count"]) for row in apps
            ),
            "runtime_target_probe_call_count": sum(
                int(row["runtime_target_probe_call_count"]) for row in apps
            ),
            "manual_lower_action_call_count": sum(
                int(row["manual_lower_action_call_count"]) for row in apps
            ),
            "app_constructed_target_profile_count": sum(
                int(row["app_constructed_target_profile_count"]) for row in apps
            ),
        },
        "rt_barneshut": {
            "action_migration_required": False,
            "retained_operator": "generic_aggregate_hierarchy_numba",
            "whole_app_sha256": _sha256(rtbh_whole),
            "adapter_sha256": _sha256(rtbh_adapter),
            "operator_frontdoor_present": "generic_aggregate_hierarchy_numba" in rtbh_source,
            "numba_operator_execution_present": "aggregate_frontier_reduce_numba_3d"
            in rtbh_adapter_source,
        },
        "application_backend_argument_required": False,
        "compiler_owns_placement_selection": True,
        "runtime_performance_claimed": False,
        "whole_paper_reproduction_claimed": False,
        "public_v2_release_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = build_matrix()
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
