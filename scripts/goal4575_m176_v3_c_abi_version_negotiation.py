from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from scripts import goal4552_m153_v3_c_abi_stub_library as stub_library


PACKET_VERSION = "rtdl.v3_0.c_abi_version_negotiation.goal4575.v1"
OUT_JSON = Path("docs/reports/goal4575_v3_0_m176_c_abi_version_negotiation_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4575_v3_0_m176_c_abi_version_negotiation_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
SOURCE = Path("src/native/rtdl_c_api.cpp")
POLICY = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
CURRENT_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_3.json")
M176_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_2.json")
PREVIOUS_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_1.json")
GOAL4552 = Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json")
GOAL4556 = Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json")
GOAL4566 = Path("docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.json")
GOAL4574 = Path("docs/reports/goal4574_v3_0_m175_c_abi_patch_version_refresh_2026-06-17.json")


def _header_version(header: str) -> str:
    values = {}
    for key in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(rf"#define\s+RTDL_ABI_VERSION_{key}\s+(\d+)", header)
        values[key.lower()] = match.group(1) if match else "missing"
    return f"{values['major']}.{values['minor']}.{values['patch']}"


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _version_tuple(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def _compat_smoke_checks(goal4552: dict[str, Any]) -> dict[str, bool]:
    return goal4552["build_result"]["ctypes_smoke"]["checks"]


def build_packet(root: Path = Path("."), *, run_runtime: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    policy = (root / POLICY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    manifest = _load_json(root, CURRENT_MANIFEST)
    m176_manifest = _load_json(root, M176_MANIFEST)
    previous_manifest = _load_json(root, PREVIOUS_MANIFEST)
    goal4552 = _load_json(root, GOAL4552)
    goal4556 = _load_json(root, GOAL4556)
    goal4566 = _load_json(root, GOAL4566)
    goal4574 = _load_json(root, GOAL4574)
    smoke = _compat_smoke_checks(goal4552)
    runtime_build = stub_library.build_shared_library(root) if run_runtime else None
    runtime_smoke = runtime_build["ctypes_smoke"]["checks"] if runtime_build and runtime_build["ctypes_smoke"] else {}
    checks = {
        "header_version_is_at_least_0_1_2": _version_tuple(_header_version(header)) >= (0, 1, 2),
        "header_declares_compatibility_function": "rtdl_abi_is_compatible" in header,
        "source_implements_patch_compatible_guard": "patch <= RTDL_ABI_VERSION_PATCH" in source
        and "abi_version_is_compatible" in source,
        "descriptor_entrypoints_use_minor_guard": source.count(
            "descriptor_abi_is_supported(desc->abi_version_major, desc->abi_version_minor)"
        )
        >= 3,
        "policy_documents_0x_compatibility_rule": "Current Draft Compatibility Rule" in policy
        and "rtdl_abi_is_compatible" in policy
        and "patch <= RTDL_ABI_VERSION_PATCH" in policy,
        "draft_mentions_compatibility_guard": "rtdl_abi_is_compatible(major, minor, patch)" in c_abi,
        "m176_manifest_is_0_1_2_with_16_symbols": m176_manifest["abi_version"] == "0.1.2"
        and len(m176_manifest["symbols"]) == 16
        and "rtdl_abi_is_compatible" in m176_manifest["symbols"],
        "current_manifest_matches_current_header": manifest["abi_version"] == _header_version(header)
        and len(manifest["symbols"]) >= len(m176_manifest["symbols"]),
        "previous_manifest_retained_as_history": previous_manifest["abi_version"] == "0.1.1"
        and "rtdl_abi_is_compatible" not in previous_manifest["symbols"],
        "goal4552_report_has_runtime_compatibility_checks": all(
            smoke.get(name) is True
            for name in (
                "patch_is_three",
                "current_abi_is_compatible",
                "previous_patch_is_compatible",
                "m176_patch_is_compatible",
                "future_patch_is_not_compatible",
                "future_minor_is_not_compatible",
                "future_major_is_not_compatible",
                "future_minor_context_rejected",
                "current_minor_context_still_created",
            )
        ),
        "goal4556_export_audit_includes_compat_symbol": not goal4556["failed_checks"]
        and "rtdl_abi_is_compatible" in goal4556["audit"]["exported_symbols"],
        "goal4566_manifest_gate_accepts_current_manifest": not goal4566["failed_checks"]
        and goal4566["checks"]["manifest_abi_version_matches_header"],
        "goal4574_retains_m175_history": not goal4574["failed_checks"]
        and goal4574["checks"]["m175_manifest_is_0_1_1"],
    }
    if runtime_build is not None:
        checks.update(
            {
                "runtime_shared_library_ok": bool(runtime_build["ok"]),
                "runtime_compatibility_smoke_ok": all(
                    runtime_smoke.get(name) is True
                    for name in (
                        "current_abi_is_compatible",
                        "previous_patch_is_compatible",
                        "future_patch_is_not_compatible",
                        "future_minor_context_rejected",
                    )
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4575 / V3 M176",
        "status": "c_abi_version_negotiation_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "current_abi_version": _header_version(header),
        "current_manifest": CURRENT_MANIFEST.as_posix(),
        "m176_manifest": M176_MANIFEST.as_posix(),
        "previous_manifest": PREVIOUS_MANIFEST.as_posix(),
        "runtime_build": runtime_build,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "binary_compatibility_frozen": False,
            "cross_minor_0x_compatibility_promised": False,
            "packaged_sdk_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4575 adds a draft C ABI version-negotiation guard. Clients can "
            "call `rtdl_abi_is_compatible(major, minor, patch)` before using the "
            "library; current descriptor entrypoints also reject mismatched "
            "major/minor values. The rule is intentionally fail-closed for the "
            "0.x source-tree ABI and does not authorize stable SDK wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4575 / V3 M176 C ABI Version Negotiation",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Version Surface",
        "",
        f"- Current ABI: `{packet['current_abi_version']}`",
        f"- Current manifest: `{packet['current_manifest']}`",
        f"- Previous manifest: `{packet['previous_manifest']}`",
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
            "- This is a draft 0.x fail-closed compatibility guard.",
            "- It does not freeze binary compatibility, publish a packaged SDK, promise cross-minor compatibility, or authorize release wording.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-runtime", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_runtime=not args.no_runtime)
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
