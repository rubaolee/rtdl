from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.source_tree_doctor_refresh.goal4545.v1"
OUT_JSON = Path("docs/reports/goal4545_v3_0_m146_source_tree_doctor_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4545_v3_0_m146_source_tree_doctor_refresh_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4545", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load source-tree doctor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor = _load_doctor(root)
    payload = doctor.gather_checks(run_smoke=False)
    v4_payload = doctor.gather_checks(run_smoke=False, include_v4_prep=True)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    v4_checks_by_name = {row["name"]: row for row in v4_payload["checks"]}
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    checks = {
        "doctor_ok": payload["ok"],
        "version_marker_is_v3_0_2": checks_by_name["version marker"]["detail"] == "v3.0.2",
        "v3_0_2_release_package_required": "v3.0.2 release package" in checks_by_name,
        "v3_strategy_doc_required": "V3 app-author strategy" in checks_by_name,
        "v3_current_test_matrix_required": "V3 current test matrix" in checks_by_name,
        "default_doctor_excludes_v4_prep": "V4 preparatory C ABI surface" not in checks_by_name
        and "V4 preparatory C ABI docs" not in checks_by_name,
        "reviewer_mode_includes_v4_prep": "V4 preparatory C ABI surface" in v4_checks_by_name
        and "V4 preparatory C ABI docs" in v4_checks_by_name,
        "doctor_doc_mentions_v3": "V3 development" in doc_text,
        "doctor_doc_mentions_reviewer_flag": "--include-v4-prep" in doc_text,
        "required_failures_empty": tuple(payload["required_failures"]) == (),
        "v4_required_failures_empty": tuple(v4_payload["required_failures"]) == (),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4545 / V3 M146",
        "status": "source_tree_doctor_v3_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_payload": payload,
        "doctor_payload_with_v4_prep": v4_payload,
        "claim_boundary": {
            "runtime_executed": False,
            "benchmark_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "Goal4545 refreshes the source-tree doctor to the current V3.0 "
            "development surface. The required layout checks now expect VERSION "
            "`v3.0.2`, the v3.0.2 release package, the V3 app-author strategy "
            "doc, and the current V3 test-matrix entrypoint. V4 preparatory C "
            "ABI checks are available only through explicit reviewer mode. This is an "
            "environment sanity gate only, not a benchmark or claim "
            "authorization."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4545 / V3 M146 Source-Tree Doctor Refresh",
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
            "- No benchmark runtime was executed.",
            "- No release, public speedup, broad RT-core, paper-reproduction, or automatic partner-selection wording is authorized.",
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
