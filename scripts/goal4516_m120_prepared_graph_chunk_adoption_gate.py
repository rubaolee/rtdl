from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.prepared_graph_chunk_adoption_gate.goal4516.v1"
OUT_JSON = Path("docs/reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.md")


SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "app_id": "rtnn",
        "label": "RTNN M19/M113 chunked graph partner bridge",
        "graph_id": "prepared_graph_chunk_adoption_gate_reference",
        "contract_key": "ranked_summary_device_partial_reduction_v1",
        "operation": "prepared_graph_partner_continuation",
        "item_count": 1_048_576,
        "max_item_count": 65_536,
        "prepared_scene_reuse_available": True,
        "prepared_item_handle_per_chunk_available": True,
        "prepared_graph_capture_validated": True,
        "partner_continuation_explicit": True,
        "partner_continuation_associative": True,
        "host_materialization_before_partner": False,
        "reader_action": "Use M113 planning for explicit same-stream partner partials.",
    },
    {
        "app_id": "rt_dbscan",
        "label": "RT-DBSCAN future compact-status graph continuation",
        "graph_id": "prepared_graph_chunk_adoption_gate_reference",
        "contract_key": "fixed_radius_compact_status_continuation_v1",
        "operation": "prepared_graph_partner_continuation",
        "item_count": 2_000_000,
        "max_item_count": 65_536,
        "prepared_scene_reuse_available": True,
        "prepared_item_handle_per_chunk_available": False,
        "prepared_graph_capture_validated": False,
        "partner_continuation_explicit": True,
        "partner_continuation_associative": True,
        "host_materialization_before_partner": False,
        "reader_action": (
            "Do not promote M113 as the RT-DBSCAN route until a chunk-local direct-status "
            "handle and validated graph capture exist."
        ),
    },
    {
        "app_id": "triangle_counting",
        "label": "Triangle prepared replay with unique-count continuation",
        "graph_id": "prepared_graph_chunk_adoption_gate_reference",
        "contract_key": "graph_relationship_unique_summary_replay_v1",
        "operation": "prepared_graph_partner_continuation",
        "item_count": 117_185_083,
        "max_item_count": 65_536,
        "prepared_scene_reuse_available": True,
        "prepared_item_handle_per_chunk_available": False,
        "prepared_graph_capture_validated": False,
        "partner_continuation_explicit": True,
        "partner_continuation_associative": False,
        "host_materialization_before_partner": False,
        "reader_action": (
            "Keep the current direct sort/RLE path; use M113 discipline only after "
            "chunk-boundary duplicate handling is proven associative."
        ),
    },
    {
        "app_id": "spatial_rayjoin",
        "label": "Spatial RayJoin repeated PIP graph replay",
        "graph_id": "prepared_graph_chunk_adoption_gate_reference",
        "contract_key": "closed_shape_batch_count_replay_v1",
        "operation": "prepared_graph_partner_continuation",
        "item_count": 100_000,
        "max_item_count": 65_536,
        "prepared_scene_reuse_available": True,
        "prepared_item_handle_per_chunk_available": True,
        "prepared_graph_capture_validated": False,
        "partner_continuation_explicit": False,
        "partner_continuation_associative": True,
        "host_materialization_before_partner": False,
        "reader_action": (
            "Use the prepared batch executor; Goal4451 quarantines prepared-points "
            "CUDA graph replay."
        ),
    },
    {
        "app_id": "barnes_hut",
        "label": "Barnes-Hut aggregate-frontier row route",
        "graph_id": "prepared_graph_chunk_adoption_gate_reference",
        "contract_key": "aggregate_tree_weighted_vector_sum_v1",
        "operation": "prepared_graph_partner_continuation",
        "item_count": 131_072,
        "max_item_count": 65_536,
        "prepared_scene_reuse_available": False,
        "prepared_item_handle_per_chunk_available": False,
        "prepared_graph_capture_validated": False,
        "partner_continuation_explicit": True,
        "partner_continuation_associative": True,
        "host_materialization_before_partner": True,
        "reader_action": (
            "Do not force M113 onto the frontier-row route; implement the future "
            "generic fused weighted-vector primitive instead."
        ),
    },
)


def _assess(scenario: dict[str, Any]) -> dict[str, Any]:
    assessment = rt.assess_v3_prepared_graph_chunk_executor_adoption(
        app_id=scenario["app_id"],
        graph_id=scenario["graph_id"],
        contract_key=scenario["contract_key"],
        operation=scenario["operation"],
        item_count=scenario["item_count"],
        max_item_count=scenario["max_item_count"],
        prepared_scene_reuse_available=scenario["prepared_scene_reuse_available"],
        prepared_item_handle_per_chunk_available=scenario[
            "prepared_item_handle_per_chunk_available"
        ],
        prepared_graph_capture_validated=scenario["prepared_graph_capture_validated"],
        partner_continuation_explicit=scenario["partner_continuation_explicit"],
        partner_continuation_associative=scenario["partner_continuation_associative"],
        host_materialization_before_partner=scenario["host_materialization_before_partner"],
    )
    validation = rt.validate_v3_prepared_graph_chunk_executor_adoption(assessment)
    return {
        "label": scenario["label"],
        "reader_action": scenario["reader_action"],
        "assessment": assessment,
        "validation": validation,
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    del root
    rows = [_assess(scenario) for scenario in SCENARIOS]
    ready = [row for row in rows if row["assessment"]["ready_for_m113_plan"]]
    blocked = [row for row in rows if not row["assessment"]["ready_for_m113_plan"]]
    blocker_counts: dict[str, int] = {}
    for row in blocked:
        for blocker in row["assessment"]["blockers"]:
            blocker_counts[str(blocker)] = blocker_counts.get(str(blocker), 0) + 1
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4516 / V3 M120",
        "rows": rows,
        "summary": {
            "scenario_count": len(rows),
            "ready_count": len(ready),
            "blocked_count": len(blocked),
            "ready_apps": [row["assessment"]["app_id"] for row in ready],
            "blocked_apps": [row["assessment"]["app_id"] for row in blocked],
            "blocker_counts": blocker_counts,
            "all_validated": all(row["validation"]["status"] == "accept" for row in rows),
            "automatic_partner_selection_authorized": False,
            "public_speedup_claim_authorized": False,
            "runtime_executed": False,
        },
        "conclusion": (
            "M120 turns M113 from a single RTNN-derived plan into a reusable adoption "
            "gate. RTNN is ready for M113 planning; RT-DBSCAN, Triangle Counting, "
            "Spatial RayJoin, and Barnes-Hut remain blocked for distinct runtime "
            "reasons. This is a core/runtime safety gate, not automatic dispatch or "
            "new performance evidence."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4516 / V3 M120 Prepared Graph Chunk Adoption Gate",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Adoption Matrix",
        "",
        "| Scenario | Ready | Plan chunks | Blockers | Reader action |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in packet["rows"]:
        assessment = row["assessment"]
        plan = assessment["plan"]
        chunks = plan["chunk_count"] if isinstance(plan, dict) else 0
        blockers = ", ".join(str(blocker) for blocker in assessment["blockers"]) or "none"
        lines.append(
            f"| {row['label']} | `{assessment['ready_for_m113_plan']}` | "
            f"{chunks} | {blockers} | {row['reader_action']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This gate does not execute runtime work.",
            "- It does not authorize public speedup wording.",
            "- It does not authorize automatic partner selection or hidden dispatch.",
            "- A blocked app must remove every listed blocker before using M113 as a promoted route.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
