from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.triangle_device_key_payload_merge.goal4530.v1"
OUT_JSON = Path("docs/reports/goal4530_v3_0_m133_triangle_device_key_payload_merge_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4530_v3_0_m133_triangle_device_key_payload_merge_2026-06-17.md")


def _list_i64(column: Any) -> list[int]:
    return [int(value) for value in column.get().tolist()]


def build_packet() -> dict[str, Any]:
    import cupy

    chunk_payloads = (
        {
            "keys": cupy.asarray([11, 17, 23, 29], dtype=cupy.int64),
            "counts": cupy.asarray([1, 2, 1, 1], dtype=cupy.int64),
        },
        {
            "keys": cupy.asarray([17, 23, 31], dtype=cupy.int64),
            "counts": cupy.asarray([3, 4, 1], dtype=cupy.int64),
        },
        {
            "keys": cupy.asarray([11, 37], dtype=cupy.int64),
            "counts": cupy.asarray([5, 1], dtype=cupy.int64),
        },
    )
    result = rt.combine_v3_chunked_unique_count_key_payloads_cupy(chunk_payloads)
    cupy.cuda.get_current_stream().synchronize()
    unique_keys = _list_i64(result["columns"]["unique_keys"])
    counts = _list_i64(result["columns"]["counts"])
    host_reference = rt.combine_v3_chunked_unique_count_key_payloads(
        (
            {"keys": tuple((int(key),) for key in [11, 17, 23, 29]), "counts": (1, 2, 1, 1)},
            {"keys": tuple((int(key),) for key in [17, 23, 31]), "counts": (3, 4, 1)},
            {"keys": tuple((int(key),) for key in [11, 37]), "counts": (5, 1)},
        )
    )
    expected_unique_keys = [11, 17, 23, 29, 31, 37]
    expected_counts = [6, 5, 5, 1, 1, 1]
    validation_errors: list[str] = []
    if unique_keys != expected_unique_keys:
        validation_errors.append("unique key order/content mismatch")
    if counts != expected_counts:
        validation_errors.append("merged count mismatch")
    if int(result["total_weight"]) != 19:
        validation_errors.append("total weight mismatch")
    if int(result["cross_chunk_duplicate_delta"]) != 3:
        validation_errors.append("cross-chunk duplicate delta mismatch")
    if result["host_key_materialization_before_merge"]:
        validation_errors.append("key materialization before merge was reported")
    if result["host_count_materialization_before_merge"]:
        validation_errors.append("count materialization before merge was reported")

    current_readiness = rt.assess_v3_chunked_unique_count_continuation_readiness(
        app_id="triangle_counting",
        contract_key="rt_graph_2a1_unique_weighted_summary_v1",
        operation="prepared_segment_replay_unique_count_continuation",
        item_count=8_579_930_671,
        max_item_count=15_000_000,
        prepared_scene_reuse_available=True,
        prepared_item_handle_per_chunk_available=True,
        prepared_graph_capture_validated=False,
        per_chunk_unique_payload_available=True,
        key_payload_carries_counts=True,
        duplicate_keys_can_cross_chunk_boundaries=True,
        chunk_key_ranges_disjoint=False,
        final_key_payload_merge_validated=not validation_errors,
        host_materialization_before_partner=False,
    )
    current_validation = rt.validate_v3_chunked_unique_count_continuation_readiness(
        current_readiness
    )
    future_readiness = rt.assess_v3_chunked_unique_count_continuation_readiness(
        app_id="triangle_counting",
        contract_key="rt_graph_2a1_unique_weighted_summary_v1",
        operation="prepared_segment_replay_unique_count_continuation",
        item_count=45_000_000,
        max_item_count=15_000_000,
        prepared_scene_reuse_available=True,
        prepared_item_handle_per_chunk_available=True,
        prepared_graph_capture_validated=True,
        per_chunk_unique_payload_available=True,
        key_payload_carries_counts=True,
        duplicate_keys_can_cross_chunk_boundaries=True,
        chunk_key_ranges_disjoint=False,
        final_key_payload_merge_validated=not validation_errors,
        host_materialization_before_partner=False,
    )
    future_validation = rt.validate_v3_chunked_unique_count_continuation_readiness(
        future_readiness
    )

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4530 / V3 M133",
        "status": "triangle_device_key_payload_merge_validated",
        "date": "2026-06-17",
        "runtime": {
            "runtime_executed": True,
            "partner": "cupy",
            "cupy_version": str(cupy.__version__),
            "device_backend": "cuda",
            "chunk_count": len(chunk_payloads),
        },
        "device_merge": {
            "status": result["status"],
            "key_encoding": result["key_encoding"],
            "unique_keys": unique_keys,
            "counts": counts,
            "unique_key_count": int(result["unique_key_count"]),
            "total_weight": int(result["total_weight"]),
            "scalar_chunk_sum": int(result["scalar_chunk_sum"]),
            "cross_chunk_duplicate_delta": int(result["cross_chunk_duplicate_delta"]),
            "host_key_materialization_before_merge": bool(
                result["host_key_materialization_before_merge"]
            ),
            "host_count_materialization_before_merge": bool(
                result["host_count_materialization_before_merge"]
            ),
        },
        "host_reference": {
            "unique_keys": [int(key[0]) for key in host_reference["unique_keys"]],
            "counts": [int(value) for value in host_reference["counts"]],
            "unique_key_count": int(host_reference["unique_key_count"]),
            "total_weight": int(host_reference["total_weight"]),
        },
        "validation": {
            "status": "accept" if not validation_errors else "reject",
            "errors": validation_errors,
            "current_triangle_readiness": current_validation,
            "future_generic_payload_readiness": future_validation,
        },
        "claim_boundary": {
            "current_route_changed": False,
            "device_key_payload_merge_validated": not validation_errors,
            "prepared_graph_capture_validated": False,
            "m113_promotion_authorized_for_current_triangle": False,
            "app_specific_native_callback_required": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "M133 validates the app-agnostic device-side key/count payload merge "
            "needed by Triangle Counting when duplicate logical keys cross chunk "
            "boundaries. This removes the key-payload final-merge debt, but the "
            "current Triangle M113 gate remains blocked on prepared graph capture "
            "for the weighted prepared replay path."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    merge = packet["device_merge"]
    current = packet["validation"]["current_triangle_readiness"]
    future = packet["validation"]["future_generic_payload_readiness"]
    lines = [
        "# Goal4530 / V3 M133 Triangle Device Key-Payload Merge",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Device Merge",
        "",
        f"- Runtime executed: `{packet['runtime']['runtime_executed']}`",
        f"- Partner: `{packet['runtime']['partner']}`",
        f"- Unique keys: `{merge['unique_keys']}`",
        f"- Counts: `{merge['counts']}`",
        f"- Total weight: `{merge['total_weight']}`",
        f"- Cross-chunk duplicate delta: `{merge['cross_chunk_duplicate_delta']}`",
        f"- Host key materialization before merge: `{merge['host_key_materialization_before_merge']}`",
        "",
        "## M113 Gate",
        "",
        f"- Current Triangle ready: `{current['ready_for_m113_plan']}`",
        f"- Current blockers: `{', '.join(current['blockers'])}`",
        f"- Future gate with graph capture: `{future['ready_for_m113_plan']}`",
        "",
        "## Boundary",
        "",
        "- No current Triangle Counting route changed.",
        "- No app-specific native callback was introduced.",
        "- No automatic partner selection, public speedup, or RT-core speedup wording is authorized.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["validation"], indent=2, sort_keys=True))
    return 0 if packet["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
