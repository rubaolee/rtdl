from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.source_tree_doctor_v3_matrix_hint.goal4547.v1"
OUT_JSON = Path("docs/reports/goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
RUNNER = Path("scripts/run_test_matrix.py")
GOAL4546_REPORT = Path("docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.md")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4547", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load source-tree doctor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor = _load_doctor(root)
    payload = doctor.gather_checks(run_smoke=True)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    matrix = checks_by_name.get("V3 current test matrix", {})
    smoke = checks_by_name.get("hello-world smoke", {})
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    runner_text = (root / RUNNER).read_text(encoding="utf-8")
    goal4546_report = (root / GOAL4546_REPORT).read_text(encoding="utf-8")
    checks = {
        "doctor_ok": payload["ok"],
        "v3_matrix_check_present": "V3 current test matrix" in checks_by_name,
        "v3_matrix_check_passes": matrix.get("status") == "pass",
        "v3_matrix_detail_names_group": "--group v3_current" in str(matrix.get("detail", "")),
        "hello_world_smoke_passes": smoke.get("status") == "pass",
        "doctor_doc_links_v3_runner": "scripts/run_test_matrix.py --group v3_current" in doc_text,
        "runner_group_registered": '"v3_current"' in runner_text,
        "goal4546_report_available": "Goal4546 / V3 M147" in goal4546_report,
        "required_failures_empty": tuple(payload["required_failures"]) == (),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4547 / V3 M148",
        "status": "source_tree_doctor_v3_matrix_hint_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_payload": payload,
        "claim_boundary": {
            "v3_current_suite_executed_by_doctor": False,
            "benchmark_executed": False,
            "native_runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "conclusion": (
            "Goal4547 wires the source-tree doctor to the current V3 test-matrix "
            "entrypoint. The doctor now required-checks that `v3_current` is "
            "registered and documents the command, while keeping the full "
            "closure suite as an explicit runner command instead of hiding it "
            "inside environment diagnostics."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4547 / V3 M148 Source-Tree Doctor V3 Matrix Hint",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
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
            "- The doctor smoke path runs the portable hello-world example only.",
            "- The `v3_current` suite remains an explicit `scripts/run_test_matrix.py --group v3_current` command.",
            "- No benchmark, native runtime, release, or public speedup wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
