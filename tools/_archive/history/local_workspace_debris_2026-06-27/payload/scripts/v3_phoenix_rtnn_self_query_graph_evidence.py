from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "rtnn_self_query_graph_20260621"
DIRECT_JSON = EVIDENCE_ROOT / "self_query_batch_1048576_warm_seq_r5.json"
GRAPH_JSON = EVIDENCE_ROOT / "self_query_graph_1048576_warm_seq_r5.json"
POLICY_SOURCE = ROOT / "src" / "rtdsl" / "v2_5_execution_path_policy.py"
WORKLOADS_SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OUT_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.json"
OUT_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.md"

MATERIAL_FLOOR = 2.0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _median(payload: dict[str, Any]) -> float:
    values = [float(value) for value in payload.get("elapsed_runs_sec", ())]
    if not values:
        return float(payload["elapsed_sec"])
    values = sorted(values)
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2.0


def _ratio(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return float("inf")
    return numerator / denominator


def _cold_plus_query(payload: dict[str, Any]) -> float:
    return (
        float(payload.get("input_pack_sec", 0.0))
        + float(payload.get("execution_prepare_sec", 0.0))
        + _median(payload)
    )


def _summarize_route(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_mode": payload["result_mode"],
        "query_count": int(payload["query_count"]),
        "search_count": int(payload["search_count"]),
        "repeat": int(payload["repeat"]),
        "hot_median_sec": _median(payload),
        "input_load_sec": float(payload["input_load_sec"]),
        "input_pack_sec": float(payload["input_pack_sec"]),
        "execution_prepare_sec": float(payload["execution_prepare_sec"]),
        "cold_plus_query_sec": _cold_plus_query(payload),
        "claim_boundary": payload["claim_boundary"],
        "contract": payload["contract"],
        "ranked_aggregate_summary": payload["ranked_aggregate_summary"],
        "ranked_aggregate_batch_summaries": payload["ranked_aggregate_batch_summaries"],
    }


def _summaries_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    int_fields = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    for field in int_fields:
        if int(left[field]) != int(right[field]):
            return False
    return abs(float(left["sum_distance"]) - float(right["sum_distance"])) <= 1.0e-6


def build_payload() -> dict[str, Any]:
    direct = _load_json(DIRECT_JSON)
    graph = _load_json(GRAPH_JSON)
    direct_summary = _summarize_route(direct)
    graph_summary = _summarize_route(graph)
    policy_source = POLICY_SOURCE.read_text(encoding="utf-8")
    workloads_source = WORKLOADS_SOURCE.read_text(encoding="utf-8")

    comparisons = {
        "graph_over_direct_hot_speedup": _ratio(
            direct_summary["hot_median_sec"], graph_summary["hot_median_sec"]
        ),
        "graph_over_direct_prepare_speedup": _ratio(
            direct_summary["execution_prepare_sec"], graph_summary["execution_prepare_sec"]
        ),
        "graph_over_direct_cold_plus_query_speedup": _ratio(
            direct_summary["cold_plus_query_sec"], graph_summary["cold_plus_query_sec"]
        ),
        "graph_over_direct_input_pack_speedup": _ratio(
            direct_summary["input_pack_sec"], graph_summary["input_pack_sec"]
        ),
    }
    checks = {
        "direct_evidence_exists": DIRECT_JSON.exists(),
        "graph_evidence_exists": GRAPH_JSON.exists(),
        "point_count_is_serious_1m": graph_summary["query_count"] == 1_048_576,
        "same_contract_summary_parity": _summaries_match(
            direct_summary["ranked_aggregate_summary"],
            graph_summary["ranked_aggregate_summary"],
        ),
        "graph_uses_prepared_search_as_query_points": (
            graph_summary["contract"].get("prepared_search_as_query_points") is True
            and graph_summary["ranked_aggregate_batch_summaries"][0].get("query_source")
            == "prepared_search"
        ),
        "graph_replay_is_explicit": graph_summary["contract"].get("prepared_cuda_graph_replay") is True,
        "native_65536_graph_cap_removed": (
            "graph path currently supports query_count <= 65536" not in workloads_source
            and "fixed_radius_neighbors_3d graph query_count exceeds uint32 limit" in workloads_source
        ),
        "policy_no_fixed_65536_cap": (
            "V2_5_FIXED_RADIUS_AGGREGATE_GRAPH_QUERY_COUNT_CAP: int | None = None"
            in policy_source
        ),
        "material_speedup_floor_not_met": (
            comparisons["graph_over_direct_cold_plus_query_speedup"] < MATERIAL_FLOOR
        ),
    }
    failed_checks = [
        key
        for key, value in checks.items()
        if key != "material_speedup_floor_not_met" and not bool(value)
    ]
    status = (
        "fail"
        if failed_checks
        else "rtnn_self_query_graph_large_scale_functional_not_m7_material_floor_not_met"
    )
    return {
        "tool": "v3_phoenix_rtnn_self_query_graph_evidence",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_prepared_self_query_cuda_graph_replay",
        "candidate_scope": (
            "generic prepared fixed-radius self-query aggregate graph replay; RTNN is only the "
            "large-scale evidence harness"
        ),
        "material_speedup_floor": MATERIAL_FLOOR,
        "release_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "evidence": {
            "direct_self_query": str(DIRECT_JSON.relative_to(ROOT)).replace("\\", "/"),
            "self_query_graph": str(GRAPH_JSON.relative_to(ROOT)).replace("\\", "/"),
        },
        "measurements": {
            "direct_self_query": direct_summary,
            "self_query_graph": graph_summary,
        },
        "comparisons": comparisons,
        "checks": checks,
        "failed_checks": failed_checks,
        "conclusion": (
            "The self-query CUDA graph route is now functional at 1,048,576 queries and "
            "keeps prepared search columns resident as query columns, but it is not a material "
            "performance win over the direct self-query batch route. It adds a generic engine "
            "surface and removes the stale 65,536 graph cap; it does not reopen RTNN M7."
        ),
        "next_action": (
            "Keep RTNN open on the larger wall-path blocker: input/file residency and prepared "
            "session amortization. Do not promote graph replay unless a future route clears the "
            "material floor on cold-plus-query or a repeated prepared-session scope is reviewed."
        ),
        "forbidden_public_wording": [
            "RTNN is solved",
            "self-query graph is a public speedup row",
            "V3 beats V2 for nearest-neighbor because of graph replay",
            "large fixed-radius graph replay is M7",
        ],
        "goal_level_decision_audit": {
            "decision": (
                "Add and test a generic prepared self-query graph route, then block promotion "
                "because the 1M warm evidence is only about 1.01x on cold-plus-query."
            ),
            "was_i_foolish": "No. The code change was tested on POD and the evidence blocks overclaiming.",
            "foolish_actions": (
                "It would have been foolish to call this a performance breakthrough after seeing "
                "only a near-neutral cold-plus-query ratio."
            ),
            "other_path": (
                "Skip graph replay and work only on file/input residency. That may still be the "
                "main path, but it would leave the stale 65,536 graph cap and self-query graph gap unresolved."
            ),
            "different_path_now": (
                "Use the functional route as a guarded engine capability while moving RTNN work back "
                "to input residency/prepared-session amortization for material V3 performance."
            ),
        },
    }


def write_markdown(payload: dict[str, Any]) -> str:
    c = payload["comparisons"]
    m = payload["measurements"]
    lines = [
        "# Phoenix V3 RTNN Self-Query Graph Evidence",
        "",
        "## Verdict",
        "",
        payload["conclusion"],
        "",
        "## Measurements",
        "",
        "| Route | Hot median sec | Input pack sec | Prepare sec | Cold+query sec |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            "| Direct self-query batch | "
            f"{m['direct_self_query']['hot_median_sec']:.6f} | "
            f"{m['direct_self_query']['input_pack_sec']:.6f} | "
            f"{m['direct_self_query']['execution_prepare_sec']:.6f} | "
            f"{m['direct_self_query']['cold_plus_query_sec']:.6f} |"
        ),
        (
            "| Self-query graph replay | "
            f"{m['self_query_graph']['hot_median_sec']:.6f} | "
            f"{m['self_query_graph']['input_pack_sec']:.6f} | "
            f"{m['self_query_graph']['execution_prepare_sec']:.6f} | "
            f"{m['self_query_graph']['cold_plus_query_sec']:.6f} |"
        ),
        "",
        "## Comparisons",
        "",
        f"- Graph over direct hot speedup: `{c['graph_over_direct_hot_speedup']:.3f}x`",
        f"- Graph over direct prepare speedup: `{c['graph_over_direct_prepare_speedup']:.3f}x`",
        f"- Graph over direct cold+query speedup: `{c['graph_over_direct_cold_plus_query_speedup']:.3f}x`",
        "",
        "## Boundary",
        "",
        "- Functional generic route: yes.",
        "- M7 promotion: no.",
        "- Public speedup wording: no.",
        "- Broad V3-over-V2 wording: no.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "failed_checks": payload["failed_checks"]}, indent=2))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
