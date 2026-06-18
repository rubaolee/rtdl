from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import goal15_compare_embree
from scripts import run_test_matrix


PACKET_VERSION = "rtdl.v3_0.legacy_full_runner_repair.goal4548.v1"
OUT_JSON = Path("docs/reports/goal4548_v3_0_m149_legacy_full_runner_repair_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4548_v3_0_m149_legacy_full_runner_repair_2026-06-17.md")
GOAL15_SCRIPT = Path("scripts/goal15_compare_embree.py")
GOAL15_TEST = Path("tests/goal15_compare_test.py")


def _summarize_output(output: str) -> dict[str, Any]:
    lines = [line for line in output.splitlines() if line.strip()]
    return {
        "line_count": len(lines),
        "contains_ok": "OK" in output,
        "contains_ran_296": "Ran 296 tests" in output,
        "contains_skipped_2": "skipped=2" in output,
        "tail": tuple(lines[-8:]),
    }


def build_packet(root: Path = Path("."), *, run_suite: bool = False) -> dict[str, Any]:
    suite = run_test_matrix.run_group("full") if run_suite else None
    suite_summary = _summarize_output(str(suite["output"])) if suite else None
    lsi_source = goal15_compare_embree.native_source_path("goal15_lsi_native.cpp")
    pip_source = goal15_compare_embree.native_source_path("goal15_pip_native.cpp")
    script_text = (root / GOAL15_SCRIPT).read_text(encoding="utf-8")
    test_text = (root / GOAL15_TEST).read_text(encoding="utf-8")
    checks = {
        "archive_lsi_source_resolves": lsi_source.exists() and "docs/history/source_archive/apps" in lsi_source.as_posix(),
        "archive_pip_source_resolves": pip_source.exists() and "docs/history/source_archive/apps" in pip_source.as_posix(),
        "legacy_shim_maps_lsi_symbol": "rtdl_embree_run_lsi" in script_text
        and "rtdl_embree_run_segment_pair_intersection" in script_text,
        "legacy_shim_maps_pip_symbol": "rtdl_embree_run_pip" in script_text
        and "rtdl_embree_run_point_primitive_anyhit_packet" in script_text,
        "local_embree_library_preferred": "local_embree_link_args" in script_text,
        "resolver_test_added": "test_native_compare_sources_resolve_from_archive" in test_text,
    }
    if suite is not None:
        checks.update(
            {
                "full_runner_ok": bool(suite["ok"]),
                "full_runner_module_count_41": suite["module_count"] == 41,
                "full_runner_reports_296_tests": bool(suite_summary and suite_summary["contains_ran_296"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4548 / V3 M149",
        "status": "legacy_full_runner_repaired",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "suite_run": suite,
        "suite_summary": suite_summary,
        "claim_boundary": {
            "benchmark_executed": False,
            "performance_claim_authorized": False,
            "release_authorized": False,
            "native_public_abi_restored": False,
        },
        "conclusion": (
            "Goal4548 repairs the legacy canonical `run_test_matrix.py --group full` "
            "path. Goal15 native comparison now resolves archived source files, "
            "uses a private compatibility shim for old `rtdl_embree_run_lsi/pip` "
            "app symbols, and prefers the local `librtdl_embree` build artifact "
            "instead of recompiling the whole native API into each smoke exe."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    suite = packet["suite_run"] or {}
    lines = [
        "# Goal4548 / V3 M149 Legacy Full Runner Repair",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Suite",
        "",
        f"- Group: `full`",
        f"- Module count: `{suite.get('module_count')}`",
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
            "- This repairs a test runner and native-compare smoke path.",
            "- It does not add legacy `rtdl_embree_run_lsi/pip` symbols back to the public native ABI.",
            "- It does not authorize benchmark or performance claims.",
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
                "full_runner_ok": None if packet["suite_run"] is None else packet["suite_run"]["ok"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
