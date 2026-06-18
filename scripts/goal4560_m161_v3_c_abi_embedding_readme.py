from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_embedding_readme.goal4560.v1"
OUT_JSON = Path("docs/reports/goal4560_v3_0_m161_c_abi_embedding_readme_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4560_v3_0_m161_c_abi_embedding_readme_2026-06-17.md")
README = Path("examples/current/embedding/README.md")
EXAMPLE = Path("examples/current/embedding/c_api_aabb2_overlap_client.c")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    readme = (root / README).read_text(encoding="utf-8")
    example = (root / EXAMPLE).read_text(encoding="utf-8")
    checks = {
        "readme_exists": (root / README).exists(),
        "example_exists": (root / EXAMPLE).exists(),
        "readme_names_v3_draft_boundary": "V3 draft source-tree examples" in readme,
        "readme_includes_make_build_command": "make build-c-api" in readme,
        "readme_includes_c_compile_command": "cc -std=c11 -I include" in readme
        and "c_api_aabb2_overlap_client.c" in readme,
        "readme_includes_run_command": "build/librtdl_c_api.so" in readme,
        "readme_includes_expected_output": "hit_count=1 first_pair=(0,0)" in readme,
        "readme_blocks_overclaims": "not an OptiX, Embree, device-buffer" in readme
        and "frozen-ABI" in readme,
        "example_matches_readme_route": "RTDL_QUERY_AABB_OVERLAP" in example
        and "hit_count=%lld" in example,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4560 / V3 M161",
        "status": "c_abi_embedding_readme_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "packaged_sdk_released": False,
            "optix_backend_query_implemented": False,
            "embree_backend_query_implemented": False,
            "device_buffer_query_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4560 makes the V3 C ABI example discoverable with a source-tree "
            "embedding README. It documents the exact build/run commands, expected "
            "output, and boundaries for the host AABB2 overlap example without "
            "claiming a packaged SDK, GPU backend, device-buffer route, or frozen ABI."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4560 / V3 M161 C ABI Embedding README",
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
            "- This is a source-tree documentation/readability gate for the C example.",
            "- No packaged SDK, OptiX, Embree, device-buffer query, frozen ABI, or release claim is authorized.",
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
