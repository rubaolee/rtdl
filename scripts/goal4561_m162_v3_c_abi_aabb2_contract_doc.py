from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_aabb2_contract_doc.goal4561.v1"
OUT_JSON = Path("docs/reports/goal4561_v3_0_m162_c_abi_aabb2_contract_doc_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4561_v3_0_m162_c_abi_aabb2_contract_doc_2026-06-17.md")
C_ABI_DOC = Path("docs/learn/v3_0_c_abi_draft.md")
EXAMPLE_README = Path("examples/current/embedding/README.md")
EXAMPLE = Path("examples/current/embedding/c_api_aabb2_overlap_client.c")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    c_abi_doc = (root / C_ABI_DOC).read_text(encoding="utf-8")
    example_readme = (root / EXAMPLE_README).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    checks = {
        "c_abi_doc_names_current_contract_section": "Current Host AABB2 Query Contract" in c_abi_doc,
        "c_abi_doc_defines_f32_aabb2_input_layout": "RTDL_DTYPE_F32" in c_abi_doc
        and "[primitive_count, 4]" in c_abi_doc
        and "(min_x, min_y, max_x, max_y)" in c_abi_doc,
        "c_abi_doc_defines_u64_pair_result_layout": "RTDL_DTYPE_U64" in c_abi_doc
        and "[hit_count, 2]" in c_abi_doc
        and "(query_id, primitive_id)" in c_abi_doc,
        "c_abi_doc_defines_result_ordering": "ascending `query_id`" in c_abi_doc
        and "ascending `primitive_id`" in c_abi_doc,
        "c_abi_doc_defines_ownership": "caller-retained when `release == NULL`" in c_abi_doc
        and "release != NULL" in c_abi_doc
        and "rtdl_buffer_destroy" in c_abi_doc,
        "c_abi_doc_blocks_unsupported_routes": "Unsupported primitive kinds" in c_abi_doc
        and "OptiX execution" in c_abi_doc
        and "Embree execution" in c_abi_doc,
        "example_readme_repeats_layout": "[count, 4]" in example_readme
        and "[hit_count, 2]" in example_readme,
        "example_source_matches_documented_layout": "shape[1] = 4" in example
        and "result_view.shape[1] != 2" in example,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4561 / V3 M162",
        "status": "c_abi_aabb2_contract_doc_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "optix_backend_query_implemented": False,
            "embree_backend_query_implemented": False,
            "device_buffer_query_validated": False,
            "general_query_contract_frozen": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4561 documents the exact current C ABI host AABB2 overlap "
            "contract: F32 `[count,4]` input rows, U64 `[hit_count,2]` result "
            "rows, ownership, and unsupported-route boundaries. It remains a narrow "
            "source-tree V3 draft contract, not a frozen or GPU-backend claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4561 / V3 M162 C ABI AABB2 Contract Doc",
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
            "- This documents the current host AABB2 overlap C ABI contract.",
            "- No OptiX, Embree, device-buffer query, frozen general query contract, or release claim is authorized.",
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
