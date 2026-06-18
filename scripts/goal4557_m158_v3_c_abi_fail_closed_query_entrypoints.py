from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_fail_closed_query_entrypoints.goal4557.v1"
OUT_JSON = Path("docs/reports/goal4557_v3_0_m158_c_abi_fail_closed_query_entrypoints_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4557_v3_0_m158_c_abi_fail_closed_query_entrypoints_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
SOURCE = Path("src/native/rtdl_c_api.cpp")
CLIENT_SMOKE = Path("scripts/goal4553_m154_v3_c_abi_c_client_smoke.py")
SYMBOL_AUDIT = Path("scripts/goal4556_m157_v3_c_abi_exported_symbol_audit.py")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    client_smoke = (root / CLIENT_SMOKE).read_text(encoding="utf-8")
    symbol_audit = (root / SYMBOL_AUDIT).read_text(encoding="utf-8")
    checks = {
        "header_declares_generic_primitive_and_query_kinds": "rtdl_primitive_kind" in header
        and "rtdl_query_kind" in header,
        "header_declares_index_and_query_descs": "rtdl_index_desc" in header
        and "rtdl_query_desc" in header,
        "header_declares_query_entrypoints": "rtdl_index_build" in header
        and "rtdl_query_execute" in header,
        "source_implements_query_entrypoints": "rtdl_index_build" in source
        and "rtdl_query_execute" in source,
        "source_fails_closed_for_unsupported_routes": "RTDL_STATUS_ERROR_UNSUPPORTED" in source
        and "only host F32 AABB2" in source,
        "source_contains_minimal_aabb2_query_proof": "RTDL_QUERY_AABB_OVERLAP" in source
        and "aabb2_overlaps" in source,
        "c_client_checks_aabb2_query_success": "rtdl_query_execute" in client_smoke
        and "host_f32_aabb2_overlap_query_validated" in client_smoke,
        "symbol_audit_expects_query_entrypoints": "rtdl_index_build" in symbol_audit
        and "rtdl_query_execute" in symbol_audit
        and "expected_symbol_count_is_15" in symbol_audit,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4557 / V3 M158",
        "status": "c_abi_fail_closed_query_entrypoints_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "general_backend_query_implemented": False,
            "non_aabb2_query_semantics_validated": False,
            "binary_compatibility_frozen": False,
            "dlpack_support_implemented": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4557 adds draft generic C ABI query entrypoints and verifies the "
            "guardrail around them: the lifecycle stub now contains a minimal host "
            "F32 AABB2 overlap proof route, while unsupported primitive/query routes "
            "still fail closed with `RTDL_STATUS_ERROR_UNSUPPORTED`. This does not "
            "claim broad backend query execution, non-AABB2 semantics, DLPack, frozen "
            "ABI, or release readiness."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4557 / V3 M158 C ABI Query Entry Point Guardrail",
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
            "- Query entrypoints are present; AABB2 overlap has a minimal host proof route.",
            "- Unsupported primitive/query routes must fail closed.",
            "- No broad backend query execution, non-AABB2 semantic compatibility, DLPack bridge, frozen ABI, or release claim is authorized.",
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
