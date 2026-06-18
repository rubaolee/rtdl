from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_doctor_docs_surface.goal4572.v1"
OUT_JSON = Path("docs/reports/goal4572_v3_0_m173_c_abi_doctor_docs_surface_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4572_v3_0_m173_c_abi_doctor_docs_surface_2026-06-17.md")
DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
LEARN_README = Path("docs/learn/README.md")
REQUIRED_DOCS = (
    Path("docs/learn/v3_0_c_abi_draft.md"),
    Path("docs/learn/v3_0_c_abi_stability_policy.md"),
    Path("docs/learn/v3_0_c_abi_ownership_threading_contract.md"),
    Path("docs/learn/v3_0_c_abi_staging_contract.md"),
    Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_2.json"),
    Path("docs/learn/v3_0_zero_copy_interop_contract.md"),
)


def _load_doctor(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_goal4572", root / DOCTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load source-tree doctor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doctor = _load_doctor(root)
    payload = doctor.gather_checks(run_smoke=False)
    checks_by_name = {row["name"]: row for row in payload["checks"]}
    docs_surface = checks_by_name.get("V3 C ABI docs surface", {})
    doctor_text = (root / DOCTOR).read_text(encoding="utf-8")
    doctor_doc = (root / DOCTOR_DOC).read_text(encoding="utf-8")
    learn_readme = (root / LEARN_README).read_text(encoding="utf-8")
    docs_exist = {path.as_posix(): (root / path).exists() for path in REQUIRED_DOCS}
    checks = {
        "doctor_ok": payload["ok"],
        "docs_surface_check_present": "V3 C ABI docs surface" in checks_by_name,
        "docs_surface_check_passes": docs_surface.get("status") == "pass",
        "docs_surface_detail_names_expected_docs": "ownership/threading" in str(docs_surface.get("detail", ""))
        and "symbol manifest" in str(docs_surface.get("detail", "")),
        "doctor_code_requires_c_abi_docs": "v3_0_c_abi_ownership_threading_contract.md" in doctor_text
        and "v3_0_c_abi_symbol_manifest_v0_1_2.json" in doctor_text,
        "doctor_doc_explains_docs_surface": "V3 C ABI docs surface" in doctor_doc
        and "does not freeze the ABI" in doctor_doc,
        "learn_readme_links_ownership_and_zero_copy": "V3.0 C ABI Ownership And Threading Contract" in learn_readme
        and "V3.0 Zero-Copy Interop Contract" in learn_readme,
        "required_docs_exist": all(docs_exist.values()),
        "required_failures_empty": tuple(payload["required_failures"]) == (),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4572 / V3 M173",
        "status": "c_abi_doctor_docs_surface_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doctor_payload": payload,
        "required_docs": docs_exist,
        "claim_boundary": {
            "doctor_builds_c_abi_library": False,
            "doctor_executes_c_abi_runtime": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4572 adds a required source-tree doctor check for the V3 C ABI "
            "documentation surface. The doctor now verifies that draft, stability, "
            "ownership/threading, symbol manifest, zero-copy, and Learn README links "
            "are present, while runtime validation remains in dedicated evidence packets."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4572 / V3 M173 C ABI Doctor Docs Surface",
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
            "- The doctor checks file/link presence only.",
            "- It does not build the C ABI library, run C ABI runtime clients, freeze the ABI, authorize release wording, or authorize performance claims.",
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
