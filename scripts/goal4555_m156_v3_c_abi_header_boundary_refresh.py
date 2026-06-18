from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_header_boundary_refresh.goal4555.v1"
OUT_JSON = Path("docs/reports/goal4555_v3_0_m156_c_abi_header_boundary_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4555_v3_0_m156_c_abi_header_boundary_refresh_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
GOAL4552_SCRIPT = Path("scripts/goal4552_m153_v3_c_abi_stub_library.py")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    doc = (root / DOC).read_text(encoding="utf-8")
    goal4552_script = (root / GOAL4552_SCRIPT).read_text(encoding="utf-8")
    checks = {
        "header_exists": (root / HEADER).exists(),
        "header_mentions_minimal_lifecycle_stub": "minimal lifecycle stub implementation" in header,
        "header_blocks_frozen_backend_claim": "not" in header
        and "frozen or backend-capable shared-library contract" in header,
        "header_removed_stale_no_implementation_wording": "not yet an implemented shared-library contract" not in header,
        "learn_doc_mentions_makefile_target": "Goal4554 wires the lifecycle stub" in doc
        and "make build-c-api" in doc,
        "goal4552_gate_tracks_new_header_wording": "header_marks_draft_stub_boundary" in goal4552_script
        and "not yet an implemented shared-library contract" not in goal4552_script,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4555 / V3 M156",
        "status": "c_abi_header_boundary_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "backend_query_implemented": False,
            "binary_compatibility_frozen": False,
            "install_package_target_implemented": False,
            "dlpack_support_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4555 refreshes the public V3 C ABI header wording after the "
            "Goal4552-Goal4554 implementation steps. The header now says the ABI "
            "has a minimal lifecycle stub implementation while still blocking "
            "frozen-ABI, backend-query, package-install, DLPack, and release claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4555 / V3 M156 C ABI Header Boundary Refresh",
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
            "- This is wording and guardrail maintenance for the C ABI draft header.",
            "- No backend query, install/package target, DLPack bridge, frozen ABI, or release claim is authorized.",
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
