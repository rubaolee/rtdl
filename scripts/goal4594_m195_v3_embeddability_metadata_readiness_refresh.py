from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_metadata_readiness.goal4594.v1"
OUT_JSON = Path("docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.md")
REPORTS = {
    "shipping_readiness": Path("docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.json"),
    "architecture_status": Path("docs/reports/goal4590_v3_0_m191_embeddability_architecture_status_refresh_2026-06-17.json"),
    "host_external_runtime": Path("docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.json"),
    "cuda_buffer_metadata": Path("docs/reports/goal4592_v3_0_m193_c_abi_cuda_buffer_metadata_gate_2026-06-17.json"),
    "python_cuda_metadata_bridge": Path("docs/reports/goal4593_v3_0_m194_python_ctypes_cuda_metadata_bridge_2026-06-17.json"),
    "staging_inventory": Path("docs/reports/goal4585_v3_0_m186_c_abi_staging_inventory_refresh_2026-06-17.json"),
}


def _load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    reports = {name: _load_json(root, path) for name, path in REPORTS.items()}
    examples = tuple(reports["staging_inventory"]["examples"])
    status_matrix = {
        "source_tree_stage_archive": reports["shipping_readiness"]["status_matrix"]["source_tree_stage_archive"],
        "host_external_runtime_metadata": reports["host_external_runtime"]["support_matrix"][
            "host_external_runtime_metadata"
        ],
        "cuda_buffer_descriptor_import_export": reports["cuda_buffer_metadata"]["support_matrix"][
            "cuda_buffer_descriptor_import_export"
        ],
        "python_ctypes_cuda_metadata_bridge": reports["python_cuda_metadata_bridge"]["support_matrix"][
            "python_ctypes_cuda_descriptor_import_export"
        ],
        "cuda_descriptor_host_aabb2_query_route": reports["python_cuda_metadata_bridge"]["support_matrix"][
            "cuda_descriptor_host_aabb2_query_route"
        ],
        "external_cuda_stream_ordering": "blocked",
        "device_buffer_query_route": "blocked",
        "public_true_zero_copy_claim": "blocked",
        "generated_language_bindings": "blocked",
        "packaged_sdk": "blocked",
        "stable_abi": "blocked_until_1_0_gates",
        "release": "blocked",
    }
    checks = {
        "all_required_reports_accept": all(not tuple(report.get("failed_checks", ())) for report in reports.values()),
        "architecture_status_reaches_goal4593": reports["architecture_status"]["checks"][
            "architecture_doc_status_at_or_beyond_goal4589"
        ],
        "host_external_runtime_validated": status_matrix["host_external_runtime_metadata"] == "validated",
        "cuda_metadata_descriptor_validated": status_matrix["cuda_buffer_descriptor_import_export"]
        == "validated_metadata_only",
        "python_cuda_metadata_bridge_validated": status_matrix["python_ctypes_cuda_metadata_bridge"] == "validated",
        "cuda_query_route_still_rejected": status_matrix["cuda_descriptor_host_aabb2_query_route"]
        == "rejected_invalid_argument",
        "staging_inventory_includes_python_cuda_metadata_example": "python_ctypes_cuda_buffer_metadata_client.py"
        in examples,
        "stage_archive_remains_not_sdk": reports["shipping_readiness"]["claim_boundary"]["packaged_sdk_authorized"]
        is False,
        "true_zero_copy_claim_still_blocked": reports["python_cuda_metadata_bridge"]["claim_boundary"][
            "public_true_zero_copy_claim_authorized"
        ]
        is False,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4594 / V3 M195",
        "status": "embeddability_metadata_readiness_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "status_matrix": status_matrix,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "claim_boundary": {
            "device_buffer_query_route_authorized": False,
            "external_cuda_stream_authorized": False,
            "cuda_pointer_ownership_validated": False,
            "public_true_zero_copy_claim_authorized": False,
            "generated_language_binding_authorized": False,
            "packaged_sdk_authorized": False,
            "stable_abi_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4594 refreshes the embeddability ledger after the host-runtime "
            "and CUDA-metadata slices. The source tree now validates a movable "
            "C ABI stage archive, host runtime metadata, C-level CUDA buffer "
            "descriptor import/export, and a Python ctypes bridge from a "
            "`__cuda_array_interface__`-style object into that descriptor path. "
            "The CUDA descriptor still cannot enter a query route, and no CUDA "
            "pointer ownership, external stream ordering, public true-zero-copy, "
            "generated binding, SDK, stable ABI, release, or performance claim is "
            "authorized."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4594 / V3 M195 Embeddability Metadata Readiness Refresh",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Status Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
    for name, status in packet["status_matrix"].items():
        lines.append(f"| `{name}` | `{status}` |")
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
            "- This is a source-tree readiness refresh, not release authorization.",
            "- Device-buffer query execution, CUDA pointer ownership validation, external stream ordering, public true-zero-copy wording, generated bindings, packaged SDK, stable ABI, performance wording, and release claims remain blocked.",
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
