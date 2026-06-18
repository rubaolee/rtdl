from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_patch_version_refresh.goal4574.v1"
OUT_JSON = Path("docs/reports/goal4574_v3_0_m175_c_abi_patch_version_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4574_v3_0_m175_c_abi_patch_version_refresh_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
CURRENT_MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_3.json")
M175_MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_1.json")
PREVIOUS_MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_0.json")
POLICY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
OWNERSHIP = Path("docs/learn/v3_0_c_abi_ownership_threading_contract.md")
GOAL4552 = Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json")
GOAL4566 = Path("docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.json")
GOAL4573 = Path("docs/reports/goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_2026-06-17.json")


def _header_version(header: str) -> str:
    values = {}
    for key in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(rf"#define\s+RTDL_ABI_VERSION_{key}\s+(\d+)", header)
        values[key.lower()] = match.group(1) if match else "missing"
    return f"{values['major']}.{values['minor']}.{values['patch']}"


def _version_tuple(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    current_manifest = json.loads((root / CURRENT_MANIFEST).read_text(encoding="utf-8"))
    m175_manifest = json.loads((root / M175_MANIFEST).read_text(encoding="utf-8"))
    previous_manifest = json.loads((root / PREVIOUS_MANIFEST).read_text(encoding="utf-8"))
    policy = (root / POLICY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    ownership = (root / OWNERSHIP).read_text(encoding="utf-8")
    goal4552 = json.loads((root / GOAL4552).read_text(encoding="utf-8"))
    goal4566 = json.loads((root / GOAL4566).read_text(encoding="utf-8"))
    goal4573 = json.loads((root / GOAL4573).read_text(encoding="utf-8"))
    checks = {
        "header_version_is_at_least_0_1_1": _version_tuple(_header_version(header)) >= (0, 1, 1),
        "m175_manifest_is_0_1_1": m175_manifest["abi_version"] == "0.1.1"
        and m175_manifest["stable"] is False,
        "current_manifest_matches_current_header": current_manifest["abi_version"] == _header_version(header)
        and current_manifest["stable"] is False,
        "previous_manifest_retained_as_history": previous_manifest["abi_version"] == "0.1.0"
        and previous_manifest["symbols"] == m175_manifest["symbols"],
        "policy_and_draft_link_current_manifest": CURRENT_MANIFEST.name in policy
        and CURRENT_MANIFEST.name in c_abi,
        "ownership_contract_names_current_version": f"`{current_manifest['abi_version']}`" in ownership,
        "goal4552_runtime_checked_current_patch": goal4552["build_result"]["ctypes_smoke"]["checks"].get("patch_is_three")
        is True,
        "goal4566_manifest_gate_accepts_current_manifest": not goal4566["failed_checks"]
        and goal4566["checks"]["manifest_abi_version_matches_header"],
        "goal4573_semantic_change_has_runtime_evidence": not goal4573["failed_checks"]
        and goal4573["checks"]["runtime_validated_all_cases"],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4574 / V3 M175",
        "status": "c_abi_patch_version_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "current_abi_version": _header_version(header),
        "current_manifest": CURRENT_MANIFEST.as_posix(),
        "m175_manifest": M175_MANIFEST.as_posix(),
        "previous_manifest": PREVIOUS_MANIFEST.as_posix(),
        "claim_boundary": {
            "stable_abi_authorized": False,
            "binary_compatibility_frozen": False,
            "packaged_sdk_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
        },
        "conclusion": (
            "Goal4574 refreshes the draft C ABI patch version to `0.1.1` after "
            "the Goal4573 backend/runtime fail-closed semantic change. The symbol "
            "set remains unchanged from `0.1.0`, and the `0.1.1` manifest remains "
            "as historical evidence even after later current ABI refreshes."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4574 / V3 M175 C ABI Patch Version Refresh",
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
            "- This refreshes a draft source-tree ABI version marker.",
            "- It does not freeze binary compatibility, publish a package, authorize release wording, or authorize performance claims.",
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
