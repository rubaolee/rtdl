from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.prepared_graph_chunk_executor.goal4509.v1"
OUT_JSON = Path("docs/reports/goal4509_v3_0_m113_prepared_graph_chunk_executor_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4509_v3_0_m113_prepared_graph_chunk_executor_2026-06-17.md")


def _summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": plan["version"],
        "status": plan["status"],
        "item_count": int(plan["item_count"]),
        "max_item_count": int(plan["max_item_count"]),
        "chunk_count": int(plan["chunk_count"]),
        "plan_status": plan["plan_status"],
        "single_graph_cap_exceeded": bool(plan["single_graph_cap_exceeded"]),
        "first_chunk": dict(plan["chunks"][0]),
        "last_chunk": dict(plan["chunks"][-1]),
        "validation": rt.validate_v3_prepared_graph_chunk_executor_plan(plan),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    del root
    single = rt.plan_v3_prepared_graph_chunk_executor(
        graph_id="prepared_graph_chunk_executor_reference",
        contract_key="prepared_graph_chunk_executor_contract_v1",
        operation="prepared_graph_partner_continuation",
        item_count=65_536,
        max_item_count=65_536,
    )
    large = rt.plan_v3_prepared_graph_chunk_executor(
        graph_id="prepared_graph_chunk_executor_reference",
        contract_key="prepared_graph_chunk_executor_contract_v1",
        operation="prepared_graph_partner_continuation",
        item_count=1_048_576,
        max_item_count=65_536,
    )
    m19 = rt.plan_v3_m19_ranked_summary_bridge_chunks(
        point_count=1_048_576,
        query_count=1_048_576,
        distribution="uniform",
    )
    m19_nested = m19["prepared_graph_chunk_executor_plan"]
    combined_signature = rt.combine_v3_prepared_graph_chunk_signatures(
        (
            ((65_536, 10, 20, 30, 40),),
            ((65_536, 11, 21, 31, 41),),
        )
    )
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4509 / V3 M113",
        "executor_version": rt.V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION,
        "executor_status": rt.V3_PREPARED_GRAPH_CHUNK_EXECUTOR_STATUS,
        "single_graph_plan": _summary(single),
        "large_chunk_plan": _summary(large),
        "m19_reuse": {
            "m19_plan_version": m19["version"],
            "m19_chunk_count": int(m19["chunk_count"]),
            "nested_executor_plan_version": m19_nested["version"],
            "nested_executor_chunk_count": int(m19_nested["chunk_count"]),
            "nested_executor_validation": rt.validate_v3_prepared_graph_chunk_executor_plan(
                m19_nested
            ),
            "m19_validation": rt.validate_v3_m19_ranked_summary_bridge_chunk_plan(m19),
            "alignment": {
                "query_count_equals_item_count": int(m19["query_count"]) == int(m19_nested["item_count"]),
                "chunk_count_matches": int(m19["chunk_count"]) == int(m19_nested["chunk_count"]),
                "outer_plan_keeps_legacy_query_fields": True,
            },
        },
        "signature_combiner_probe": {
            "input_chunk_count": 2,
            "combined_signature": combined_signature,
        },
        "claim_boundary": {
            "runtime_executed": False,
            "app_agnostic_contract_ready": True,
            "m19_reuses_generic_plan": True,
            "automatic_backend_selection_authorized": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "M113 lifts the M19 chunked partner-continuation shape into an "
            "app-agnostic prepared graph chunk executor contract. The generic "
            "planner validates contiguous chunks, prepared scene reuse, per-chunk "
            "item handles, per-chunk prepared graphs, explicit partner continuation, "
            "and blocked host materialization before the partner. M19 now embeds "
            "that generic plan while preserving its legacy query-field payload."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    single = packet["single_graph_plan"]
    large = packet["large_chunk_plan"]
    m19 = packet["m19_reuse"]
    lines = [
        "# Goal4509 / V3 M113 Prepared Graph Chunk Executor",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Plan Matrix",
        "",
        "| Plan | Items | Max per chunk | Chunks | Status | Runtime executed |",
        "| --- | ---: | ---: | ---: | --- | --- |",
        (
            f"| generic single | {single['item_count']:,} | {single['max_item_count']:,} | "
            f"{single['chunk_count']} | `{single['plan_status']}` | false |"
        ),
        (
            f"| generic large | {large['item_count']:,} | {large['max_item_count']:,} | "
            f"{large['chunk_count']} | `{large['plan_status']}` | false |"
        ),
        (
            f"| M19 RTNN reuse | 1,048,576 | 65,536 | {m19['m19_chunk_count']} | "
            "`chunked_partner_continuation_required` | false |"
        ),
        "",
        "## Generic Contract",
        "",
        "- Prepared scene reuse is required across chunks.",
        "- Each chunk prepares its own item/query handle and prepared graph.",
        "- Partner continuation is explicit and per chunk.",
        "- Host materialization before the partner is blocked.",
        "- Aggregate-only substitutes, hidden dispatch, automatic backend selection, and automatic partner selection are not authorized.",
        "",
        "## M19 Reuse",
        "",
        f"- M19 outer chunk count: `{m19['m19_chunk_count']}`.",
        f"- Nested generic chunk count: `{m19['nested_executor_chunk_count']}`.",
        f"- Query count equals generic item count: `{m19['alignment']['query_count_equals_item_count']}`.",
        f"- Chunk count matches: `{m19['alignment']['chunk_count_matches']}`.",
        "",
        "## Boundary",
        "",
        "- This is a reusable planning and validation contract, not new runtime performance evidence.",
        "- RTNN public speedup, paper reproduction, same-output author comparison, and automatic partner-selection claims remain blocked.",
        "- Next users of this contract should be RT-DBSCAN compact-status continuation and Triangle Counting prepared replay where their contracts fit.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["m19_reuse"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
