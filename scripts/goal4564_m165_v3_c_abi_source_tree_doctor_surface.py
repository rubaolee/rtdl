from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_source_tree_doctor_surface.goal4564.v1"
OUT_JSON = Path("docs/reports/goal4564_v3_0_m165_c_abi_source_tree_doctor_surface_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4564_v3_0_m165_c_abi_source_tree_doctor_surface_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
PROCESS_DOC = Path("docs/audit/process/development_reliability_process.md")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4564", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load source-tree doctor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor = _load_doctor(root)
    payload = doctor.gather_checks(run_smoke=False)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    surface = checks_by_name.get("V4 preparatory C ABI surface", {})
    doctor_text = (root / DOCTOR).read_text(encoding="utf-8")
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    process_text = (root / PROCESS_DOC).read_text(encoding="utf-8")
    checks = {
        "doctor_ok": payload["ok"],
        "c_abi_surface_check_present": "V4 preparatory C ABI surface" in checks_by_name,
        "c_abi_surface_check_passes": surface.get("status") == "pass",
        "c_abi_surface_detail_names_header": "include/rtdl/rtdl.h" in str(surface.get("detail", "")),
        "c_abi_surface_detail_names_make_target": "make build-c-api" in str(surface.get("detail", "")),
        "doctor_checks_header_source_make_and_example": "c_api_aabb2_overlap_client.c" in doctor_text
        and "rtdl_c_api.cpp" in doctor_text
        and "rtdl.h" in doctor_text
        and "build-c-api:" in doctor_text,
        "doctor_doc_explains_c_abi_surface_boundary": "V4 preparatory C ABI surface" in doc_text
        and "It does not" in doc_text
        and "make build-c-api" in doc_text,
        "process_doc_avoids_stale_goal_span": "starting at Goal4508" in process_text
        and "Goal4508-Goal4545" not in process_text,
        "required_failures_empty": tuple(payload["required_failures"]) == (),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4564 / V3 M165",
        "status": "c_abi_source_tree_doctor_surface_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_payload": payload,
        "claim_boundary": {
            "c_abi_library_built_by_doctor": False,
            "runtime_executed": False,
            "benchmark_executed": False,
            "release_authorized": False,
            "stable_abi_authorized": False,
        },
        "conclusion": (
            "Goal4564 records the C ABI source-tree surface as V4 preparatory "
            "doctor context, not as a V3 release criterion. The doctor now verifies "
            "that the public header, source implementation, Makefile target, and "
            "embedding example are discoverable, while still leaving actual library "
            "builds and runtime validation to the dedicated C ABI evidence packets."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4564 / V3 M165 C ABI Source-Tree Doctor Surface",
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
            "- The doctor checks source-tree files and entrypoints only.",
            "- It does not build the C ABI shared library or execute runtime/benchmark code.",
            "- No release or stable-ABI wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet()
    if not args.no_write:
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
