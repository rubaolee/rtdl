#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from typing import Iterable


TEST_MODULES = (
    "tests.goal1898_v2_package_install_gate_audit_test",
    "tests.goal1899_v2_strict_birth_gate_current_board_test",
    "tests.goal1900_partner_acceleration_boundary_doc_test",
    "tests.goal1902_v2_source_tree_only_release_exception_proposal_test",
    "tests.goal1903_v2_partner_pod_batch_packet_test",
    "tests.goal1904_gemini_review_goal1903_batch_packet_test",
    "tests.goal1905_v2_partner_pod_batch_acceptance_test",
    "tests.goal1906_public_v2_claim_boundary_scan_test",
    "tests.goal1907_gemini_review_v2_boundary_and_source_tree_test",
    "tests.goal1908_v2_local_preflight_test",
    "tests.goal1909_v2_release_packet_skeleton_test",
    "tests.goal1910_gemini_review_v2_release_skeleton_test",
    "tests.goal1911_v2_readiness_aggregator_test",
    "tests.goal1912_post_pod_external_review_template_test",
    "tests.goal1913_v2_pod_session_runbook_test",
    "tests.goal1914_v2_pod_artifact_provenance_hardening_test",
    "tests.goal1915_gemini_review_goal1914_pod_provenance_test",
    "tests.goal1916_v2_post_pod_artifact_manifest_test",
    "tests.goal1917_gemini_review_goal1916_post_pod_manifest_test",
    "tests.goal1918_fixed_radius_reference_oom_guard_test",
    "tests.goal1919_post_pod_evidence_integration_test",
    "tests.goal1920_gemini_followup_goal1912_post_pod_review_correction_test",
    "tests.goal1921_v2_post_pod_performance_report_test",
    "tests.goal1922_numba_triton_strategy_preplanning_test",
    "tests.goal1923_claude_post_pod_review_integration_test",
    "tests.goal1924_all_app_v2_completion_and_perf_analysis_plan_test",
    "tests.goal1925_fixed_radius_family_v2_partner_perf_test",
    "tests.goal1927_robot_collision_partner_pose_flags_adapter_test",
    "tests.goal1928_robot_collision_v2_partner_perf_test",
    "tests.goal1930_all_app_v2_matrix_test",
    "tests.goal1931_current_all_app_v18_v2_perf_analysis_test",
    "tests.goal1932_all_app_v2_pod_batch_runner_test",
    "tests.goal1933_goal1934_large_scale_all_app_v2_pod_perf_test",
    "tests.goal1935_gemini_review_goal1933_1934_large_scale_perf_test",
    "tests.goal1936_claude_review_goal1933_1935_large_scale_perf_test",
    "tests.goal1937_fixed_radius_repeat3_pod_perf_test",
    "tests.goal1938_gemini_review_goal1937_repeat3_fixed_radius_test",
    "tests.goal1939_db_phase_totals_fix_test",
    "tests.goal1940_robot_segment_scaleup_pod_perf_test",
    "tests.goal1941_gemini_review_goal1940_robot_segment_scaleup_test",
    "tests.goal1942_gemini_review_all_app_v2_rollup_test",
    "tests.goal1943_v2_source_tree_only_release_decision_packet_test",
    "tests.goal1944_gemini_review_v2_source_tree_only_policy_test",
    "tests.goal1945_claude_review_v2_source_tree_only_policy_test",
    "tests.goal1946_all_app_v2_perf_deep_dive_test",
    "tests.goal1947_v2_source_tree_only_policy_consensus_test",
    "tests.goal1948_user_owned_native_continuation_example_test",
    "tests.goal1950_gemini_final_v2_release_review_test",
    "tests.goal1952_partner_rawkernel_and_user_continuation_boundary_test",
)


def _run(command: list[str], *, root: pathlib.Path) -> dict[str, object]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"src{os.pathsep}." if not existing else f"{existing}{os.pathsep}src{os.pathsep}."
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "output_tail": completed.stdout[-4000:],
    }


def _read_json_if_exists(path: pathlib.Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local non-pod v2 preflight checks.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--output", default="docs/reports/goal1908_v2_local_preflight.json")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = pathlib.Path(args.root).resolve()
    commands = [
        [args.python, "-m", "unittest", *TEST_MODULES],
        [args.python, "scripts/goal1906_public_v2_claim_boundary_scan.py", "--output", "scratch/goal1908_claim_scan.json"],
        [
            args.python,
            "scripts/goal1905_v2_partner_pod_batch_acceptance.py",
            "--allow-missing",
            "--output",
            "scratch/goal1908_pre_pod_acceptance_snapshot.json",
        ],
        [
            args.python,
            "scripts/goal1911_v2_readiness_aggregator.py",
            "--output",
            "scratch/goal1908_readiness_aggregator.json",
        ],
        [
            args.python,
            "scripts/goal1916_v2_post_pod_artifact_manifest.py",
            "--allow-missing",
            "--output",
            "scratch/goal1908_pre_pod_artifact_manifest.json",
        ],
    ]
    runs = [_run(command, root=root) for command in commands]
    status = "pass" if all(run["returncode"] == 0 for run in runs) else "fail"
    readiness = _read_json_if_exists(root / "scratch/goal1908_readiness_aggregator.json")
    readiness_boundary = readiness.get("claim_boundary", {}) if readiness else {}
    pod_evidence_collected = bool(readiness_boundary.get("pod_evidence_collected", False))
    payload = {
        "goal": "Goal1908",
        "status": status,
        "test_modules": list(TEST_MODULES),
        "runs": runs,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "pod_evidence_collected": pod_evidence_collected,
            "package_install_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
