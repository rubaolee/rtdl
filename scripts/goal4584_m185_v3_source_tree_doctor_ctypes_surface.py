from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.source_tree_doctor_ctypes_surface.goal4584.v1"
OUT_JSON = Path("docs/reports/goal4584_v3_0_m185_source_tree_doctor_ctypes_surface_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4584_v3_0_m185_source_tree_doctor_ctypes_surface_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4584", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load rtdl_source_tree_doctor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor_module = _load_doctor(root)
    payload = doctor_module.gather_checks(run_smoke=False, include_v4_prep=True)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    doctor_text = (root / DOCTOR).read_text(encoding="utf-8")
    doc_text = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    surface = checks_by_name.get("V4 preparatory C ABI surface", {})
    checks = {
        "doctor_surface_check_passes": surface.get("status") == "pass",
        "surface_detail_names_python_ctypes_examples": "Python ctypes examples" in surface.get("detail", ""),
        "doctor_requires_lifecycle_ctypes_example": "python_ctypes_client.py" in doctor_text,
        "doctor_requires_query_ctypes_example": "python_ctypes_aabb2_query_client.py" in doctor_text,
        "doctor_requires_stage_c_api_target": "stage-c-api:" in doctor_text,
        "doctor_doc_explains_ctypes_surface": "Python `ctypes` lifecycle" in doc_text
        and "host AABB2 query examples" in doc_text,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4584 / V3 M185",
        "status": "source_tree_doctor_ctypes_surface_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_surface": surface,
        "claim_boundary": {
            "doctor_runs_c_api_build": False,
            "doctor_runs_ctypes_query": False,
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "generated_binding_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4584 refreshes the source-tree doctor so the V4 preparatory C ABI "
            "surface check covers the staged direct-link C example and the "
            "Python ctypes lifecycle/query examples added after the original C "
            "ABI doctor surface. The doctor remains a lightweight source-tree "
            "presence check; it does not build the C ABI, run the ctypes query, "
            "freeze the ABI, or authorize SDK/release wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4584 / V3 M185 Source-Tree Doctor ctypes Surface",
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
            "- The doctor checks source-tree presence only.",
            "- It does not build the C ABI, run ctypes query examples, freeze ABI, package an SDK, generate bindings, or authorize release claims.",
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
