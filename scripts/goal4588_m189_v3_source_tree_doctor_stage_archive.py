from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.source_tree_doctor_stage_archive.goal4588.v1"
OUT_JSON = Path("docs/reports/goal4588_v3_0_m189_source_tree_doctor_stage_archive_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4588_v3_0_m189_source_tree_doctor_stage_archive_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4588", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load rtdl_source_tree_doctor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor_module = _load_doctor(root)
    payload = doctor_module.gather_checks(run_smoke=False)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    surface = checks_by_name.get("V3 C ABI embedding surface", {})
    doctor_text = (root / DOCTOR).read_text(encoding="utf-8")
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    checks = {
        "doctor_surface_check_passes": surface.get("status") == "pass",
        "surface_detail_names_package_stage_target": "package-c-api-stage" in surface.get("detail", ""),
        "doctor_requires_package_stage_target": "package-c-api-stage:" in doctor_text,
        "doctor_doc_explains_archive_target_boundary": "make package-c-api-stage" in doc_text
        and "not build" in doc_text,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4588 / V3 M189",
        "status": "source_tree_doctor_stage_archive_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_surface": surface,
        "claim_boundary": {
            "doctor_builds_archive": False,
            "packaged_sdk_authorized": False,
            "system_install_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4588 refreshes the source-tree doctor so its V3 C ABI embedding "
            "surface check includes the new `package-c-api-stage` target. The "
            "doctor still checks target/file presence only; it does not build the "
            "archive or authorize SDK, install, stable ABI, or release wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4588 / V3 M189 Source-Tree Doctor Stage Archive",
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
            "- It does not build the archive, package an SDK, install RTDL, freeze ABI, or authorize release claims.",
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
