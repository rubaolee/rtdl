from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtdbscan_chunk_handle_gate.goal4519.v1"
OUT_JSON = Path("docs/reports/goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_2026-06-17.md")
DIRECT_STATUS_SOURCE = Path("src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py")


def _source_audit(root: Path) -> dict[str, Any]:
    text = (root / DIRECT_STATUS_SOURCE).read_text(encoding="utf-8")
    return {
        "source_path": DIRECT_STATUS_SOURCE.as_posix(),
        "whole_dataset_prepared_handle_api_present": (
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d"
            in text
        ),
        "caller_owned_point_columns_prepare_api_present": (
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d"
            in text
        ),
        "prepared_predicate_direct_status_handle_class_present": (
            "V28PreparedFixedRadiusPartitionConvergencePredicateDirectStatusUnionCupyPreview3D"
            in text
        ),
        "runtime_columns_reused": "prepared_direct_status_runtime_columns_reused" in text,
        "pair_materialization_avoided": "pair_materialization_avoided" in text,
        "native_abi_added_false_boundary_present": '"native_abi_added": False' in text,
        "graph_capture_api_present": "cuda_graph" in text or "graph_capture" in text,
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    source_audit = _source_audit(root)
    readiness = rt.assess_v3_chunk_local_prepared_handle_readiness(
        app_id="rt_dbscan",
        contract_key="fixed_radius_compact_status_continuation_v1",
        operation="prepared_graph_partner_continuation",
        item_count=2_000_000,
        max_item_count=65_536,
        whole_dataset_prepared_handle_available=source_audit[
            "whole_dataset_prepared_handle_api_present"
        ],
        caller_owned_item_columns_available=source_audit[
            "caller_owned_point_columns_prepare_api_present"
        ],
        chunk_slice_prepare_api_available=source_audit[
            "caller_owned_point_columns_prepare_api_present"
        ],
        live_chunk_handle_smoke_validated=False,
        prepared_graph_capture_validated=False,
        partner_continuation_explicit=True,
        partner_continuation_associative=True,
        host_materialization_before_partner=False,
    )
    validation = rt.validate_v3_chunk_local_prepared_handle_readiness(readiness)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4519 / V3 M123",
        "status": "rt_dbscan_chunk_handle_api_shape_ready_runtime_blocked",
        "date": "2026-06-17",
        "source_audit": source_audit,
        "readiness": readiness,
        "validation": validation,
        "m120_blocker_refinement": {
            "missing_prepared_item_handle_per_chunk": (
                "refined_to_api_shape_ready_but_live_chunk_smoke_missing"
            ),
            "prepared_graph_capture_not_validated": "still_blocking",
            "current_route_should_use_m113": False,
        },
        "claim_boundary": {
            "runtime_executed": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "current_route_changed": False,
            "m113_promotion_authorized": False,
        },
        "conclusion": (
            "M123 refines the RT-DBSCAN M120 blocker. The existing direct-status "
            "code has the API shape needed to prepare from caller-owned CuPy point "
            "columns, so chunk-local handles are plausible. It is still not an M113 "
            "route: no live chunk-handle smoke and no prepared graph capture have "
            "been validated, and the current compact-signature route remains the "
            "Goal4510 predicate direct-status path."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    audit = packet["source_audit"]
    validation = packet["validation"]
    lines = [
        "# Goal4519 / V3 M123 RT-DBSCAN Chunk-Handle Gate",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Source Audit",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in audit.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            f"- API shape ready: `{validation['api_shape_ready']}`",
            f"- Ready for M113 plan: `{validation['ready_for_m113_plan']}`",
            f"- Blockers: `{', '.join(validation['blockers'])}`",
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current RT-DBSCAN route changed.",
            "- M113 promotion remains blocked until a live chunk-handle smoke and graph capture validation exist.",
            "- Automatic partner selection and public speedup wording remain blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["validation"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
