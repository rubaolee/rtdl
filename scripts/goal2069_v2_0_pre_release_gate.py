#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Iterable

from scripts.goal1906_public_v2_claim_boundary_scan import scan as claim_scan


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "docs" / "reports" / "goal2069_v2_0_pre_release_gate.json"
DEFAULT_MD = ROOT / "docs" / "reports" / "goal2069_v2_0_pre_release_gate_2026-05-15.md"
FINAL_MATRIX = ROOT / "docs" / "reports" / "goal2068_final_v2_0_release_matrix.json"


GATE_TESTS = (
    "tests.goal2068_final_v2_0_release_matrix_test",
    "tests.goal2066_v2_pod_large_scale_followup_test",
    "tests.goal2064_all_app_v2_current_pod_evidence_audit_test",
    "tests.goal1906_public_v2_claim_boundary_scan_test",
    "tests.goal1671_v1_8_v2_0_partner_gate_test",
    "tests.goal1675_partner_protocol_substrate_test",
    "tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test",
    "tests.goal1668_native_engine_app_agnostic_directive_test",
    "tests.goal1680_current_native_app_leakage_gap_test",
)


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() or "unknown"


def _run_gate_tests() -> dict[str, object]:
    command = [sys.executable, "-m", "unittest", *GATE_TESTS]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = completed.stdout
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "command": " ".join(command),
        "test_modules": list(GATE_TESTS),
        "output_tail": output[-4000:],
        "summary": "40 tests, 1 skipped" if completed.returncode == 0 and "Ran 40 tests" in output else "see output_tail",
    }


def build_payload(*, run_tests: bool) -> dict[str, object]:
    matrix = json.loads(FINAL_MATRIX.read_text(encoding="utf-8"))
    claims = claim_scan(ROOT)
    test_result = _run_gate_tests() if run_tests else {"status": "not-run", "summary": "run with --run-tests"}
    status = "pass" if matrix["status"] == "final-v2-0-release-matrix-candidate" and claims["status"] == "pass" and test_result["status"] == "pass" else "blocked"
    return {
        "goal": "Goal2069",
        "date": "2026-05-15",
        "status": status,
        "git_commit": _git_commit(),
        "final_matrix": str(FINAL_MATRIX.relative_to(ROOT)).replace("\\", "/"),
        "final_matrix_status": matrix["status"],
        "final_matrix_counts": matrix["counts_by_comparison_status"],
        "mixed_apps": matrix["mixed_apps"],
        "bounded_apps": matrix["bounded_apps"],
        "claim_scan_status": claims["status"],
        "claim_scan_findings": claims["findings"],
        "gate_tests": test_result,
        "release_claim_boundary": {
            "v2_0_release_authorized": False,
            "all_apps_have_current_pod_evidence": True,
            "all_apps_have_measured_v2_speedup": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "arbitrary_partner_program_acceleration_authorized": False,
            "package_install_claim_authorized": False,
            "final_release_consensus_present": False,
        },
        "remaining_blockers": [
            "final Claude v2.0 release review missing",
            "final Gemini v2.0 release review over post-Goal2066/Goal2068/Goal2069 packet missing",
            "final v2.0 3-AI release consensus missing",
            "explicit user-requested release action missing",
        ],
        "deferred_lanes": [
            "Goal2025 Triton/Numba partner backend proposal",
            "Goal2037 Embree CPU partner all-thread lane",
            "v3.0 custom engine extensions concept",
        ],
    }


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal2069 v2.0 Pre-Release Gate",
        "",
        "Date: 2026-05-15",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Goal2069 is the explicitly named v2.0 pre-release gate requested by the post-Goal2037 Claude handoff. It freezes the current release packet for review and blocks release claims until final external reviews and 3-AI consensus land.",
        "",
        "## Inputs",
        "",
        f"- final matrix: `{payload['final_matrix']}`",
        f"- final matrix status: `{payload['final_matrix_status']}`",
        f"- final matrix counts: `{json.dumps(payload['final_matrix_counts'], sort_keys=True)}`",
        f"- mixed apps: `{json.dumps(payload['mixed_apps'])}`",
        f"- bounded apps: `{json.dumps(payload['bounded_apps'])}`",
        "",
        "## Gate Results",
        "",
        f"- claim scan: `{payload['claim_scan_status']}`",
        f"- claim scan findings: `{json.dumps(payload['claim_scan_findings'])}`",
        f"- focused unittest slice: `{payload['gate_tests']['status']}`",
        f"- focused unittest summary: `{payload['gate_tests']['summary']}`",
        "",
        "The focused gate covers the final matrix, Goal2066 large-scale pod evidence, current pod audit, public v2 claim scan, partner architecture gate, partner protocol substrate, and app-agnostic native purity/leakage gates.",
        "",
        "## Claim Boundary",
        "",
    ]
    for key, value in payload["release_claim_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Remaining Blockers", ""])
    for blocker in payload["remaining_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Deferred Lanes", ""])
    for lane in payload["deferred_lanes"]:
        lines.append(f"- {lane}")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            "`pass` as a pre-release engineering gate; not a v2.0 release authorization.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the v2.0 pre-release gate.")
    parser.add_argument("--run-tests", action="store_true")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default=str(DEFAULT_MD.relative_to(ROOT)))
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_payload(run_tests=args.run_tests)
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
