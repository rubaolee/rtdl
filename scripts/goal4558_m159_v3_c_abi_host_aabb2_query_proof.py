from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_host_aabb2_query_proof.goal4558.v1"
OUT_JSON = Path("docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.md")
HEADER = Path("docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h")
SOURCE = Path("src/native/rtdl_c_api.cpp")
CLIENT_SMOKE_REPORT = Path("docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    client_smoke = json.loads((root / CLIENT_SMOKE_REPORT).read_text(encoding="utf-8"))
    checks = {
        "header_declares_aabb2_and_overlap_query": "RTDL_PRIMITIVE_AABB2" in header
        and "RTDL_QUERY_AABB_OVERLAP" in header,
        "header_declares_index_and_query_entrypoints": "rtdl_index_build" in header
        and "rtdl_query_execute" in header,
        "source_copies_host_aabb2_primitives": "index->aabb2.assign" in source,
        "source_executes_aabb2_overlap_pairs": "aabb2_overlaps" in source
        and "pairs.push_back(query_id)" in source
        and "pairs.push_back(primitive_id)" in source,
        "source_returns_u64_pair_buffer": "RTDL_DTYPE_U64" in source
        and "result->view.shape[1] = 2" in source,
        "source_keeps_unsupported_routes_fail_closed": "RTDL_STATUS_ERROR_UNSUPPORTED" in source
        and "only host F32 AABB2" in source,
        "c_client_validated_host_aabb2_query": bool(
            client_smoke["validated_capabilities"].get("host_f32_aabb2_overlap_query_validated")
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4558 / V3 M159",
        "status": "c_abi_host_aabb2_query_proof_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "optix_backend_query_implemented": False,
            "embree_backend_query_implemented": False,
            "general_query_semantics_validated": False,
            "device_buffer_query_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4558 records the first real V3 C ABI query proof: a non-Python "
            "C client can build a host F32 AABB2 index, execute an AABB overlap "
            "query, and read a host U64 pair buffer. This is deliberately narrow: "
            "it is not OptiX, Embree, device-buffer execution, broad query semantics, "
            "or release readiness."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4558 / V3 M159 C ABI Host AABB2 Query Proof",
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
            "- This proves only host F32 AABB2 overlap through the draft C ABI.",
            "- No OptiX, Embree, device-buffer query, broad semantics, frozen ABI, or release claim is authorized.",
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
