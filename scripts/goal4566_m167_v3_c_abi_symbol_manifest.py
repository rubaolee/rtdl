from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_symbol_manifest.goal4566.v1"
OUT_JSON = Path("docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4566_v3_0_m167_c_abi_symbol_manifest_2026-06-17.md")
MANIFEST = Path("docs/learn/v3_0_c_abi_symbol_manifest_v0_1_1.json")
HEADER = Path("include/rtdl/rtdl.h")
GOAL4556 = Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json")
POLICY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")


def _header_symbols(header: str) -> tuple[str, ...]:
    return tuple(re.findall(r"RTDL_API\s+[^;]*?\b(rtdl_[A-Za-z0-9_]+)\s*\(", header))


def _header_abi_version(header: str) -> str:
    values = {}
    for key in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(rf"#define\s+RTDL_ABI_VERSION_{key}\s+(\d+)", header)
        values[key.lower()] = match.group(1) if match else "missing"
    return f"{values['major']}.{values['minor']}.{values['patch']}"


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    header = (root / HEADER).read_text(encoding="utf-8")
    goal4556 = json.loads((root / GOAL4556).read_text(encoding="utf-8"))
    policy = (root / POLICY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    manifest_symbols = tuple(manifest["symbols"])
    header_symbols = _header_symbols(header)
    exported_symbols = tuple(goal4556["audit"]["exported_symbols"])
    checks = {
        "manifest_declares_draft_not_stable": manifest["status"] == "draft_source_tree_manifest"
        and manifest["stable"] is False,
        "manifest_abi_version_matches_header": manifest["abi_version"] == _header_abi_version(header),
        "manifest_has_15_symbols": len(manifest_symbols) == 15,
        "manifest_symbols_match_header_order": manifest_symbols == header_symbols,
        "manifest_symbols_match_goal4556_export_set": set(manifest_symbols) == set(exported_symbols),
        "manifest_names_header_and_build_target": manifest["header"] == "include/rtdl/rtdl.h"
        and manifest["build_target"] == "make build-c-api",
        "policy_links_symbol_manifest": "v3_0_c_abi_symbol_manifest_v0_1_1.json" in policy,
        "c_abi_draft_links_symbol_manifest": "v3_0_c_abi_symbol_manifest_v0_1_1.json" in c_abi,
        "goal4556_export_audit_passed": goal4556["audit"]["ok"] and not goal4556["failed_checks"],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4566 / V3 M167",
        "status": "c_abi_symbol_manifest_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "manifest_symbols": manifest_symbols,
        "header_symbols": header_symbols,
        "goal4556_exported_symbols": exported_symbols,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "symbol_manifest_frozen": False,
            "cross_version_compatibility_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4566 checks the current draft machine-readable C ABI symbol manifest "
            "against the public header plus the Goal4556 "
            "export audit. This gives the V3 ABI a concrete change-tracking "
            "surface without freezing binary compatibility."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4566 / V3 M167 C ABI Symbol Manifest",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Symbols",
        "",
    ]
    for symbol in packet["manifest_symbols"]:
        lines.append(f"- `{symbol}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This is a draft source-tree manifest, not a frozen ABI promise.",
            "- No cross-version compatibility, package/release, or stable-SDK claim is authorized.",
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
