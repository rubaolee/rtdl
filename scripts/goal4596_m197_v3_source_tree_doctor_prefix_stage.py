from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.source_tree_doctor_prefix_stage.goal4596.v1"
OUT_JSON = Path("docs/reports/goal4596_v3_0_m197_source_tree_doctor_prefix_stage_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4596_v3_0_m197_source_tree_doctor_prefix_stage_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
PREFIX_STAGE_REPORT = Path("docs/reports/goal4595_v3_0_m196_c_abi_prefix_stage_2026-06-17.json")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4596", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load rtdl_source_tree_doctor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor_module = _load_doctor(root)
    payload = doctor_module.gather_checks(run_smoke=False, include_v4_prep=True)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    surface = checks_by_name.get("V4 preparatory C ABI surface", {})
    doctor_text = (root / DOCTOR).read_text(encoding="utf-8")
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    prefix_packet = json.loads((root / PREFIX_STAGE_REPORT).read_text(encoding="utf-8"))
    checks = {
        "doctor_surface_check_passes": surface.get("status") == "pass",
        "surface_detail_names_prefix_stage_target": "stage-c-api-prefix" in surface.get("detail", ""),
        "doctor_requires_prefix_stage_target": "stage-c-api-prefix:" in doctor_text,
        "doctor_doc_explains_prefix_stage_boundary": "make stage-c-api-prefix" in doc_text
        and "It does not build" in doc_text,
        "prefix_stage_report_accepts": not tuple(prefix_packet.get("failed_checks", ())),
        "prefix_stage_report_authorizes_only_prefix_layout": prefix_packet["claim_boundary"][
            "prefix_layout_stage_authorized"
        ]
        is True
        and prefix_packet["claim_boundary"]["system_install_authorized"] is False,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4596 / V3 M197",
        "status": "source_tree_doctor_prefix_stage_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_surface": surface,
        "prefix_stage_report": PREFIX_STAGE_REPORT.as_posix(),
        "claim_boundary": {
            "doctor_builds_prefix_stage": False,
            "system_install_authorized": False,
            "package_manager_artifact_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4596 refreshes the source-tree doctor so its V4 preparatory C ABI "
            "surface check includes the new `stage-c-api-prefix` target. The "
            "doctor remains a presence/sanity check only: it verifies the target "
            "and docs exist, but it does not build the prefix stage, install "
            "RTDL, package an SDK, freeze the ABI, or authorize release wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4596 / V3 M197 Source-Tree Doctor Prefix Stage",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Doctor Surface",
        "",
        f"- Status: `{packet['doctor_surface'].get('status')}`",
        f"- Detail: `{packet['doctor_surface'].get('detail')}`",
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
            "- The doctor checks source-tree target/file presence only.",
            "- It does not build the prefix stage, install RTDL, package an SDK, freeze ABI, or authorize release claims.",
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
