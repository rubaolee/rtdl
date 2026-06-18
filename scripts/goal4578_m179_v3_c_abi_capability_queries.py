from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

from scripts import goal4552_m153_v3_c_abi_stub_library as stub_library


PACKET_VERSION = "rtdl.v3_0.c_abi_capability_queries.goal4578.v1"
OUT_JSON = Path("docs/reports/goal4578_v3_0_m179_c_abi_capability_queries_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4578_v3_0_m179_c_abi_capability_queries_2026-06-17.md")
HEADER = Path("docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h")
SOURCE = Path("src/native/rtdl_c_api.cpp")
C_ABI_DRAFT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
OWNERSHIP = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_ownership_threading_contract.md")
CURRENT_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_3.json")
PREVIOUS_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_2.json")
GOAL4552 = Path("docs/reports/goal4552_v3_0_m153_c_abi_stub_library_2026-06-17.json")
GOAL4556 = Path("docs/reports/goal4556_v3_0_m157_c_abi_exported_symbol_audit_2026-06-17.json")


def _header_version(header: str) -> str:
    values = {}
    for key in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(rf"#define\s+RTDL_ABI_VERSION_{key}\s+(\d+)", header)
        values[key.lower()] = match.group(1) if match else "missing"
    return f"{values['major']}.{values['minor']}.{values['patch']}"


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path("."), *, run_runtime: bool = False) -> dict[str, Any]:
    header = (root / HEADER).read_text(encoding="utf-8")
    source = (root / SOURCE).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    ownership = (root / OWNERSHIP).read_text(encoding="utf-8")
    manifest = _load_json(root, CURRENT_MANIFEST)
    previous_manifest = _load_json(root, PREVIOUS_MANIFEST)
    goal4552 = _load_json(root, GOAL4552)
    goal4556 = _load_json(root, GOAL4556)
    smoke = goal4552["build_result"]["ctypes_smoke"]["checks"]
    runtime_build = stub_library.build_shared_library(root) if run_runtime else None
    runtime_smoke = runtime_build["ctypes_smoke"]["checks"] if runtime_build and runtime_build["ctypes_smoke"] else {}
    capability_symbols = ("rtdl_backend_is_supported", "rtdl_route_is_supported")
    checks = {
        "header_version_is_0_1_3": _header_version(header) == "0.1.3",
        "header_declares_capability_queries": all(symbol in header for symbol in capability_symbols),
        "source_implements_backend_and_route_queries": "backend_is_supported_by_host_proof" in source
        and "route_is_supported_by_host_proof" in source
        and all(symbol in source for symbol in capability_symbols),
        "source_documents_current_route_shape_in_code": "RTDL_PRIMITIVE_AABB2" in source
        and "RTDL_QUERY_AABB_OVERLAP" in source
        and "RTDL_DEVICE_HOST" in source,
        "current_manifest_has_capability_symbols": manifest["abi_version"] == "0.1.3"
        and all(symbol in manifest["symbols"] for symbol in capability_symbols),
        "previous_manifest_lacks_capability_symbols": previous_manifest["abi_version"] == "0.1.2"
        and all(symbol not in previous_manifest["symbols"] for symbol in capability_symbols),
        "goal4552_runtime_smoke_checks_capabilities": all(
            smoke.get(name) is True
            for name in (
                "auto_backend_is_supported",
                "cpu_backend_is_supported",
                "optix_backend_is_not_supported",
                "host_aabb2_overlap_route_is_supported",
                "cuda_aabb2_overlap_route_is_not_supported",
                "host_segment_ray_route_is_not_supported",
            )
        ),
        "goal4556_exports_capability_symbols": not goal4556["failed_checks"]
        and all(symbol in goal4556["audit"]["exported_symbols"] for symbol in capability_symbols),
        "docs_name_capability_queries": "Capability queries" in c_abi
        and "capability query functions" in ownership,
    }
    if runtime_build is not None:
        checks.update(
            {
                "runtime_shared_library_ok": bool(runtime_build["ok"]),
                "runtime_capability_smoke_ok": all(
                    runtime_smoke.get(name) is True
                    for name in (
                        "auto_backend_is_supported",
                        "cpu_backend_is_supported",
                        "optix_backend_is_not_supported",
                        "host_aabb2_overlap_route_is_supported",
                        "cuda_aabb2_overlap_route_is_not_supported",
                        "host_segment_ray_route_is_not_supported",
                    )
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4578 / V3 M179",
        "status": "c_abi_capability_queries_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "capability_symbols": capability_symbols,
        "runtime_build": runtime_build,
        "claim_boundary": {
            "dynamic_backend_loading_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "device_buffer_route_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4578 adds draft C ABI capability queries for the currently "
            "supported backend and primitive/query/device route surface. The runtime "
            "smoke proves AUTO/CPU and host AABB2 overlap return supported, while "
            "OptiX, CUDA-device AABB2 overlap, and segment/ray routes fail closed. "
            "This is discovery metadata for the source-tree draft, not authorization "
            "for broader backend execution."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4578 / V3 M179 C ABI Capability Queries",
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
    for symbol in packet["capability_symbols"]:
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
            "- Capability queries expose current draft support metadata only.",
            "- They do not authorize dynamic backend loading, OptiX/Embree C ABI queries, device buffers, stable ABI wording, or release claims.",
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
