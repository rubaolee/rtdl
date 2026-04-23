#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal515_public_command_truth_audit import audit as public_command_audit
from scripts.goal759_rtx_cloud_benchmark_manifest import build_manifest
from scripts.goal761_rtx_cloud_run_all import run_all
from scripts.goal763_rtx_cloud_bootstrap_check import run_check


FORBIDDEN_ACTIVE_CLASSES = {"cuda_through_optix", "host_indexed_fallback", "not_optix_exposed"}
REQUIRED_EXCLUDED_APPS = {
    "graph_analytics",
    "facility_knn_assignment",
    "road_hazard_screening",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
    "hausdorff_distance",
    "ann_candidate_search",
    "barnes_hut_force_app",
    "apple_rt_demo",
    "hiprt_ray_triangle_hitcount",
}
REQUIRED_DEFERRED_APPS = {"service_coverage_gaps", "event_hotspot_screening", "segment_polygon_hitcount"}


def _probe(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "output_tail": completed.stdout[-4000:],
    }


def _check_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    active_errors: list[str] = []
    for entry in manifest["entries"]:
        maturity = rt.rt_core_app_maturity(entry["app"])
        if maturity.current_status not in {"rt_core_ready", "rt_core_partial_ready"}:
            active_errors.append(f"{entry['path_name']} has maturity {maturity.current_status}")
        if entry["optix_performance_class"] in FORBIDDEN_ACTIVE_CLASSES:
            active_errors.append(f"{entry['path_name']} has forbidden class {entry['optix_performance_class']}")
        if entry["benchmark_readiness"] in {"exclude_from_rtx_app_benchmark", "needs_native_kernel_tuning"}:
            active_errors.append(f"{entry['path_name']} has non-active readiness {entry['benchmark_readiness']}")
    excluded = set(manifest["excluded_apps"])
    deferred = {entry["app"] for entry in manifest.get("deferred_entries", ())}
    missing_excluded = sorted(REQUIRED_EXCLUDED_APPS - excluded)
    missing_deferred = sorted(REQUIRED_DEFERRED_APPS - deferred)
    return {
        "active_count": len(manifest["entries"]),
        "deferred_count": len(manifest.get("deferred_entries", ())),
        "excluded_count": len(manifest["excluded_apps"]),
        "active_errors": active_errors,
        "missing_excluded": missing_excluded,
        "missing_deferred": missing_deferred,
        "valid": not active_errors and not missing_excluded and not missing_deferred,
    }


def run_gate() -> dict[str, Any]:
    manifest = build_manifest()
    manifest_check = _check_manifest(manifest)
    command_audit = public_command_audit()
    dry_run = run_all(dry_run=True)
    deferred_dry_run = run_all(dry_run=True, include_deferred=True)
    bootstrap_dry_run = run_check(dry_run=True, skip_build=False, skip_tests=False)
    plan_path = ROOT / "docs" / "goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md"
    goal822_report = ROOT / "docs" / "reports" / "goal822_rtx_cloud_manifest_claim_boundary_audit_2026-04-23.md"
    docs_check = {
        "plan_exists": plan_path.exists(),
        "goal822_report_exists": goal822_report.exists(),
        "valid": plan_path.exists() and goal822_report.exists(),
    }
    checks = {
        "manifest": manifest_check,
        "public_command_audit": {
            "valid": bool(command_audit["valid"]),
            "command_count": command_audit["command_count"],
            "coverage_counts": command_audit["coverage_counts"],
        },
        "active_runner_dry_run": {
            "status": dry_run["status"],
            "entry_count": dry_run["entry_count"],
            "unique_command_count": dry_run["unique_command_count"],
            "dry_run": dry_run["dry_run"],
        },
        "deferred_runner_dry_run": {
            "status": deferred_dry_run["status"],
            "entry_count": deferred_dry_run["entry_count"],
            "unique_command_count": deferred_dry_run["unique_command_count"],
            "dry_run": deferred_dry_run["dry_run"],
            "include_deferred": deferred_dry_run["include_deferred"],
        },
        "bootstrap_dry_run": {
            "status": bootstrap_dry_run["status"],
            "dry_run": bootstrap_dry_run["dry_run"],
            "step_names": [step["name"] for step in bootstrap_dry_run["steps"]],
        },
        "docs": docs_check,
        "git": {
            "head": _probe(["git", "rev-parse", "HEAD"]),
            "status_short": _probe(["git", "status", "--short"]),
        },
    }
    invalid = [
        name for name, check in checks.items()
        if (
            (isinstance(check, dict) and check.get("valid") is False)
            or (isinstance(check, dict) and check.get("status") not in {None, "ok"})
        )
    ]
    return {
        "suite": "goal824_pre_cloud_rtx_readiness_gate",
        "valid": not invalid,
        "invalid_checks": invalid,
        "checks": checks,
        "next_cloud_policy": (
            "Start one RTX cloud pod only after this gate is valid. Run the active "
            "Goal759/Goal761 batch first, optionally include deferred entries only "
            "after their activation gates are met, collect artifacts, then shut down."
        ),
        "boundary": "Local readiness only; does not start cloud and does not authorize speedup claims.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local pre-cloud RTX readiness gate.")
    parser.add_argument("--output-json", default="docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json")
    args = parser.parse_args(argv)
    payload = run_gate()
    text = json.dumps(payload, indent=2, sort_keys=True)
    Path(args.output_json).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
