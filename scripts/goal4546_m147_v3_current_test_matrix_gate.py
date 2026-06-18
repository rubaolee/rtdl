from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from scripts import run_test_matrix


PACKET_VERSION = "rtdl.v3_0.current_test_matrix.goal4546.v1"
GROUP = "v3_current"
OUT_JSON = Path("docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.md")
PROCESS_DOC = Path("docs/audit/process/development_reliability_process.md")


def _summarize_output(output: str) -> dict[str, Any]:
    lines = [line for line in output.splitlines() if line.strip()]
    match = re.search(r"Ran (\d+) tests?", output)
    ran_tests = int(match.group(1)) if match else None
    return {
        "line_count": len(lines),
        "contains_ok": "OK" in output,
        "ran_tests": ran_tests,
        "ran_at_least_original_134": ran_tests is not None and ran_tests >= 134,
        "tail": tuple(lines[-8:]),
    }


def build_packet(root: Path = Path("."), *, run_suite: bool = False) -> dict[str, Any]:
    modules = run_test_matrix.group_modules(GROUP)
    process_doc = (root / PROCESS_DOC).read_text(encoding="utf-8")
    suite = run_test_matrix.run_group(GROUP) if run_suite else None
    suite_summary = _summarize_output(str(suite["output"])) if suite else None
    checks = {
        "group_registered": GROUP in run_test_matrix.TEST_GROUPS,
        "module_count_is_71": len(modules) == 71,
        "starts_at_goal4508": modules[0] == "tests.goal4508_v3_0_m112_rtnn_clean_target_closeout_test",
        "ends_at_goal4581": modules[-1] == "tests.goal4581_v3_0_m182_c_abi_python_ctypes_example_test",
        "excludes_self_referential_goal4546": (
            "tests.goal4546_v3_0_m147_current_test_matrix_gate_test" not in modules
        ),
        "includes_stale_barnes_hut_tests": (
            "tests.goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_test" in modules
            and "tests.goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_test" in modules
        ),
        "process_doc_names_group": "--group v3_current" in process_doc,
        "process_doc_notes_default_discovery_gap": "default unittest discovery" in process_doc,
    }
    if suite is not None:
        checks.update(
            {
                "suite_ok": bool(suite["ok"]),
                "suite_module_count_matches": suite["module_count"] == len(modules),
                "suite_reports_at_least_original_134_tests": bool(
                    suite_summary and suite_summary["ran_at_least_original_134"]
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4546 / V3 M147",
        "status": "v3_current_test_matrix_checked",
        "date": "2026-06-17",
        "group": GROUP,
        "modules": modules,
        "checks": checks,
        "failed_checks": failed,
        "suite_run": suite,
        "suite_summary": suite_summary,
        "claim_boundary": {
            "benchmark_executed": False,
            "native_runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
        },
        "conclusion": (
            "Goal4546 adds a canonical `v3_current` test-matrix group for the "
            "current V3 closure surface. It covers the explicit Goal4508-Goal4581 "
            "modules except for the self-referential Goal4546 generator test, because "
            "default unittest discovery does not include every `goal*_test.py` file. "
            "The gate is a source-tree reliability check, not benchmark evidence."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    suite = packet["suite_run"] or {}
    lines = [
        "# Goal4546 / V3 M147 Current Test Matrix Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Suite",
        "",
        f"- Group: `{packet['group']}`",
        f"- Module count: `{len(packet['modules'])}`",
        f"- Suite ok: `{suite.get('ok')}`",
        f"- Command: `{suite.get('command')}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No benchmark or native runtime was executed.",
            "- No release, public speedup, or broad RT-core wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet(run_suite=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "group": packet["group"],
                "module_count": len(packet["modules"]),
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
