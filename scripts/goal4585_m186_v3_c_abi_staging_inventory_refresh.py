from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts import goal4576_m177_v3_c_abi_staging_bundle as staging


PACKET_VERSION = "rtdl.v3_0.c_abi_staging_inventory_refresh.goal4585.v1"
OUT_JSON = Path("docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/learn/v3_0_c_abi_staging_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
EXAMPLES = (
    "c_api_aabb2_overlap_client.c",
    "c_api_direct_link_client.c",
    "python_ctypes_client.py",
    "python_ctypes_aabb2_query_client.py",
)


def run_stage_inventory(root: Path) -> dict[str, Any]:
    stage_result = staging.run_stage(root)
    stage_examples = root / "build" / "c_api_stage" / "examples"
    staged_examples = {
        name: {
            "path": (stage_examples / name).as_posix(),
            "exists": (stage_examples / name).exists(),
            "size_bytes": (stage_examples / name).stat().st_size if (stage_examples / name).exists() else 0,
        }
        for name in EXAMPLES
    }
    return {
        "stage_result": stage_result,
        "staged_examples": staged_examples,
        "all_examples_staged": all(item["exists"] and item["size_bytes"] > 0 for item in staged_examples.values()),
        "ok": bool(stage_result["ok"])
        and all(item["exists"] and item["size_bytes"] > 0 for item in staged_examples.values()),
    }


def build_packet(root: Path = Path("."), *, run_stage: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    inventory = run_stage_inventory(root) if run_stage else None
    checks = {
        "makefile_stages_all_current_examples": all(f"examples/current/embedding/{name}" in makefile for name in EXAMPLES),
        "staging_contract_lists_all_current_examples": all(name in staging_contract for name in EXAMPLES),
        "embedding_readme_names_all_current_examples": all(name in embedding for name in EXAMPLES),
        "stage_target_still_builds_c_api_first": "stage-c-api: build-c-api" in makefile,
    }
    if inventory is not None:
        checks.update(
            {
                "stage_bundle_smoke_ok": bool(inventory["stage_result"]["ok"]),
                "all_current_examples_are_staged": bool(inventory["all_examples_staged"]),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4585 / V3 M186",
        "status": "c_abi_staging_inventory_refresh_checked",
        "date": "2026-06-17",
        "examples": EXAMPLES,
        "checks": checks,
        "failed_checks": failed,
        "stage_inventory": inventory,
        "claim_boundary": {
            "packaged_sdk_authorized": False,
            "install_prefix_authorized": False,
            "stable_abi_authorized": False,
            "generated_language_binding_authorized": False,
            "device_buffer_c_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4585 refreshes the staging inventory after adding direct-link "
            "and Python ctypes embedding examples. The pod evidence runs "
            "`make stage-c-api` and verifies the staged bundle contains all four "
            "current examples: C dlopen AABB2, C direct-link lifecycle, Python "
            "ctypes lifecycle, and Python ctypes host AABB2 query. This remains "
            "a source-tree staging bundle, not an installed SDK or stable ABI."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    inventory = packet["stage_inventory"] or {}
    lines = [
        "# Goal4585 / V3 M186 C ABI Staging Inventory Refresh",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Examples",
        "",
        "| Example | Staged | Size Bytes |",
        "| --- | --- | --- |",
    ]
    staged_examples = inventory.get("staged_examples") or {}
    for name in packet["examples"]:
        item = staged_examples.get(name) or {}
        lines.append(f"| `{name}` | `{item.get('exists')}` | `{item.get('size_bytes')}` |")
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
            "- This validates the current source-tree staging inventory only.",
            "- It does not authorize an installed SDK, install prefix, stable ABI, generated binding, device-buffer C ABI, OptiX/Embree C ABI execution, or release claim.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-stage", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_stage=not args.no_stage)
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
