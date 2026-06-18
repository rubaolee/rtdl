from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_status_refresh.goal4562.v1"
OUT_JSON = Path("docs/reports/goal4562_v3_0_m163_embeddability_status_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4562_v3_0_m163_embeddability_status_refresh_2026-06-17.md")
STRATEGY = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
C_ABI_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    strategy = (root / STRATEGY).read_text(encoding="utf-8")
    c_abi_doc = (root / C_ABI_DOC).read_text(encoding="utf-8")
    checks = {
        "strategy_has_current_progress_section": "## Current Implementation Progress" in strategy,
        "strategy_names_public_header_and_make_target": "include/rtdl/rtdl.h" in strategy
        and "make build-c-api" in strategy,
        "strategy_names_non_python_c_client": "Non-Python C client validation" in strategy,
        "strategy_names_host_aabb2_query_proof": "host `F32` AABB2 overlap query proof" in strategy,
        "strategy_links_c_abi_contract_doc": "V3.0 C ABI Draft" in strategy
        and "v3_0_c_abi_draft.md" in strategy,
        "strategy_blocks_still_unauthorized_claims": "Still not authorized" in strategy
        and "OptiX/Embree query" in strategy
        and "DLPack" in strategy
        and "release wording" in strategy,
        "c_abi_doc_contains_current_contract": "Current Host AABB2 Query Contract" in c_abi_doc,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4562 / V3 M163",
        "status": "embeddability_status_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "stable_c_abi_authorized": False,
            "packaged_sdk_released": False,
            "dlpack_support_implemented": False,
            "optix_embree_c_abi_query_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4562 refreshes the V3 embeddability strategy with the actual "
            "Goal4550-Goal4561 implementation progress while preserving the claim "
            "boundary: the C ABI has a source-tree host AABB2 proof, but no stable "
            "ABI, packaged SDK, DLPack, OptiX/Embree C ABI query, or release claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4562 / V3 M163 Embeddability Status Refresh",
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
            "- This refreshes strategy/status wording for V3 embeddability.",
            "- No stable ABI, packaged SDK, DLPack, OptiX/Embree C ABI query, or release claim is authorized.",
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
