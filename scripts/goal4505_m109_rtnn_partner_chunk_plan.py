from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt
from examples.current.research_benchmarks.rtnn import rtdl_rtnn_benchmark_app as app


PACKET_VERSION = "rtdl.v3_0.rtnn_partner_chunk_plan.goal4505.v1"
OUT_JSON = Path("docs/reports/goal4505_v3_0_m109_rtnn_partner_chunk_plan_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4505_v3_0_m109_rtnn_partner_chunk_plan_2026-06-17.md")


def _plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": plan["version"],
        "plan_status": plan["plan_status"],
        "point_count": int(plan["point_count"]),
        "query_count": int(plan["query_count"]),
        "max_query_count": int(plan["max_query_count"]),
        "chunk_count": int(plan["chunk_count"]),
        "first_chunk": dict(plan["chunks"][0]),
        "last_chunk": dict(plan["chunks"][-1]),
        "single_graph_cap_exceeded": bool(plan["single_graph_cap_exceeded"]),
        "large_chunk_runtime_evidence_required": bool(
            plan["large_chunk_runtime_evidence_required"]
        ),
        "aggregate_only_full_batch_direct_substitute_allowed": bool(
            plan["aggregate_only_full_batch_direct_substitute_allowed"]
        ),
        "hidden_auto_dispatch_allowed": bool(plan["hidden_auto_dispatch_allowed"]),
        "public_speedup_claim_authorized": bool(plan["public_speedup_claim_authorized"]),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    del root
    single = app.rtnn_prepared_ranked_summary_graph_partner_bridge_plan_payload(
        point_count=65_536,
        query_count=65_536,
        distribution="uniform",
    )
    large = app.rtnn_prepared_ranked_summary_graph_partner_bridge_plan_payload(
        point_count=1_048_576,
        query_count=1_048_576,
        distribution="uniform",
    )
    large_plan = large["execution_path_plan"]
    single_plan = single["execution_path_plan"]
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4505 / V3 M109",
        "app_mode": "prepared_ranked_summary_graph_partner_bridge_plan",
        "planner": "plan_v3_m19_ranked_summary_bridge_chunks",
        "single_graph_plan": _plan_summary(single_plan),
        "large_partner_continuation_plan": _plan_summary(large_plan),
        "large_plan_validation": large["validation"],
        "single_plan_validation": single["validation"],
        "chunk_contract": {
            "prepared_scene_reused": all(
                bool(chunk["prepared_scene_reused"]) for chunk in large_plan["chunks"]
            ),
            "prepared_query_points_per_chunk": all(
                bool(chunk["prepared_query_points_per_chunk"]) for chunk in large_plan["chunks"]
            ),
            "cuda_graph_per_chunk": all(
                bool(chunk["cuda_graph_per_chunk"]) for chunk in large_plan["chunks"]
            ),
            "same_stream_partner_device_reduction_per_chunk": all(
                bool(chunk["same_stream_partner_device_reduction_per_chunk"])
                for chunk in large_plan["chunks"]
            ),
            "host_materialization_before_partner": any(
                bool(chunk["host_materialization_before_partner"]) for chunk in large_plan["chunks"]
            ),
        },
        "claim_boundary": {
            "runtime_executed": False,
            "planner_only": True,
            "large_runtime_evidence_required": True,
            "aggregate_only_full_batch_direct_substitute_allowed": False,
            "hidden_auto_dispatch_allowed": False,
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "conclusion": (
            "The RTNN same-stream partner-continuation route now has an explicit "
            "front-door chunk plan. A 1,048,576-query partner-continuation workload "
            "is planned as 16 chunks of at most 65,536 queries, reusing the prepared "
            "scene but preparing query points, a CUDA graph, and the same-stream "
            "partner reduction per chunk. This is planner evidence only; large "
            "chunked runtime evidence remains required before performance wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    large = packet["large_partner_continuation_plan"]
    single = packet["single_graph_plan"]
    lines = [
        "# Goal4505 / V3 M109 RTNN Partner-Continuation Chunk Plan",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Plan Matrix",
        "",
        "| Scenario | Query count | Chunk count | Status | Runtime executed |",
        "| --- | ---: | ---: | --- | --- |",
        (
            f"| single graph | {single['query_count']:,} | {single['chunk_count']} | "
            f"`{single['plan_status']}` | false |"
        ),
        (
            f"| large partner continuation | {large['query_count']:,} | {large['chunk_count']} | "
            f"`{large['plan_status']}` | false |"
        ),
        "",
        "## Large Chunk Contract",
        "",
        f"- First chunk: `{large['first_chunk']}`.",
        f"- Last chunk: `{large['last_chunk']}`.",
        "- Prepared scene reuse is required across chunks.",
        "- Prepared query points, CUDA graph capture, and same-stream partner reduction are per chunk.",
        "- Host materialization before the partner is blocked.",
        "- Full-batch aggregate-only direct mode is not a substitute for partner continuation.",
        "",
        "## Boundary",
        "",
        "- This packet is planner evidence only.",
        "- It does not execute the chunked runtime path.",
        "- It does not authorize automatic dispatch, automatic partner selection, public speedup wording, or RT-core speedup wording.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["large_partner_continuation_plan"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
