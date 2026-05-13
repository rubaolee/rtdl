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
    payload = {
        "goal": "Goal1908",
        "status": status,
        "test_modules": list(TEST_MODULES),
        "runs": runs,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "pod_evidence_collected": False,
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
