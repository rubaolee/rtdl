from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.triangle_unique_count_gate.goal4521.v1"
OUT_JSON = Path("docs/reports/goal4521_v3_0_m125_triangle_unique_count_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4521_v3_0_m125_triangle_unique_count_gate_2026-06-17.md")


def _payload(keys: tuple[tuple[int, int], ...], counts: tuple[int, ...] | None = None) -> dict[str, Any]:
    return {
        "keys": keys,
        "counts": counts if counts is not None else tuple(1 for _ in keys),
    }


def _associativity_packet() -> dict[str, Any]:
    chunk_a = _payload(((1, 2), (1, 3)))
    chunk_b = _payload(((1, 3), (2, 4)))
    chunk_c = _payload(((3, 5),))
    chunks = (chunk_a, chunk_b, chunk_c)
    merged_all = rt.combine_v3_chunked_unique_count_key_payloads(chunks)
    merged_ab = rt.combine_v3_chunked_unique_count_key_payloads((chunk_a, chunk_b))
    merged_ab_c = rt.combine_v3_chunked_unique_count_key_payloads((
        _payload(merged_ab["unique_keys"], merged_ab["counts"]),
        chunk_c,
    ))
    merged_bc = rt.combine_v3_chunked_unique_count_key_payloads((chunk_b, chunk_c))
    merged_a_bc = rt.combine_v3_chunked_unique_count_key_payloads((
        chunk_a,
        _payload(merged_bc["unique_keys"], merged_bc["counts"]),
    ))
    scalar_chunk_sum = sum(len(chunk["keys"]) for chunk in chunks)
    global_unique_count = int(merged_all["unique_key_count"])
    return {
        "chunk_payloads": chunks,
        "scalar_chunk_sum": scalar_chunk_sum,
        "global_unique_count": global_unique_count,
        "scalar_sum_matches_global_unique": scalar_chunk_sum == global_unique_count,
        "cross_chunk_duplicate_delta": int(merged_all["cross_chunk_duplicate_delta"]),
        "key_payload_merge": merged_all,
        "associative_merge_validated": (
            merged_all["unique_keys"] == merged_ab_c["unique_keys"] == merged_a_bc["unique_keys"]
            and merged_all["counts"] == merged_ab_c["counts"] == merged_a_bc["counts"]
        ),
    }


def build_packet() -> dict[str, Any]:
    associativity = _associativity_packet()
    current_triangle_readiness = (
        rt.assess_v3_chunked_unique_count_continuation_readiness(
            app_id="triangle_counting",
            contract_key="rt_graph_2a1_unique_weighted_summary_v1",
            operation="prepared_segment_replay_unique_count_continuation",
            item_count=8_579_930_671,
            max_item_count=15_000_000,
            prepared_scene_reuse_available=True,
            prepared_item_handle_per_chunk_available=True,
            prepared_graph_capture_validated=False,
            per_chunk_unique_payload_available=True,
            key_payload_carries_counts=False,
            duplicate_keys_can_cross_chunk_boundaries=True,
            chunk_key_ranges_disjoint=False,
            final_key_payload_merge_validated=False,
            host_materialization_before_partner=False,
        )
    )
    current_validation = rt.validate_v3_chunked_unique_count_continuation_readiness(
        current_triangle_readiness
    )
    future_payload_readiness = rt.assess_v3_chunked_unique_count_continuation_readiness(
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
        final_key_payload_merge_validated=bool(associativity["associative_merge_validated"]),
        host_materialization_before_partner=False,
    )
    future_validation = rt.validate_v3_chunked_unique_count_continuation_readiness(
        future_payload_readiness
    )
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4521 / V3 M125",
        "status": "triangle_chunked_unique_count_continuation_gate",
        "date": "2026-06-17",
        "associativity_counterexample": associativity,
        "current_triangle_readiness": current_triangle_readiness,
        "current_triangle_validation": current_validation,
        "future_generic_payload_readiness": future_payload_readiness,
        "future_generic_payload_validation": future_validation,
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "m113_promotion_authorized_for_current_triangle": False,
            "app_specific_native_callback_required": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "conclusion": (
            "M125 explains the Triangle Counting M113 blocker in app-agnostic "
            "terms. Per-chunk scalar unique counts are not associative when the "
            "same key can appear in more than one chunk. The generic fix is not "
            "an app-specific OptiX callback: carry key/count payloads to a final "
            "associative merge, or prove disjoint chunk key ranges. The current "
            "Triangle route remains blocked for M113 because graph capture and "
            "key-payload final merge are not both validated."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    current = packet["current_triangle_validation"]
    future = packet["future_generic_payload_validation"]
    associativity = packet["associativity_counterexample"]
    lines = [
        "# Goal4521 / V3 M125 Triangle Unique-Count Gate",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Counterexample",
        "",
        f"- Scalar chunk sum: `{associativity['scalar_chunk_sum']}`",
        f"- Global unique count: `{associativity['global_unique_count']}`",
        f"- Scalar sum matches global unique: `{associativity['scalar_sum_matches_global_unique']}`",
        f"- Key-payload associative merge validated: `{associativity['associative_merge_validated']}`",
        "",
        "## Triangle Current Gate",
        "",
        f"- Ready for M113 plan: `{current['ready_for_m113_plan']}`",
        f"- Blockers: `{', '.join(current['blockers'])}`",
        "",
        "## Generic Future Gate",
        "",
        f"- Ready for M113 plan with key payload and graph capture: `{future['ready_for_m113_plan']}`",
        f"- Plan status: `{future['plan_status']}`",
        f"- Chunk count: `{future['chunk_count']}`",
        "",
        "## Boundary",
        "",
        "- No runtime was executed.",
        "- No current Triangle Counting route changed.",
        "- The fix remains app-agnostic: key/count payload merge or disjoint key ranges.",
        "- No app-specific native callbacks, automatic partner selection, public speedup, or RT-core speedup wording is authorized.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["current_triangle_validation"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
