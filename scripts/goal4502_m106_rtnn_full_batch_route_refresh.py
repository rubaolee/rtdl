from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.rtnn_full_batch_route_refresh.goal4502.v1"
OUT_JSON = Path("docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.md")
M105_PACKET = Path("docs/reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.json")
FULL_BATCH_BEST = Path(
    "docs/reports/goal4502_rtdl_optix_kitti_1m_r1_k50_prepared_batch_bs1000000_best_r10.json"
)
SWEEP_GLOB = "goal4502_rtdl_optix_kitti_1m_r1_k50_prepared_batch_bs*.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _cold_total(row: dict[str, Any]) -> float:
    return (
        float(row["input_load_sec"])
        + float(row["input_pack_sec"])
        + float(row["execution_prepare_sec"])
        + float(row["median_query_sec"])
    )


def _runner_row(payload: dict[str, Any], *, label: str) -> dict[str, Any]:
    row = {
        "label": label,
        "row": str(payload["row"]),
        "result_mode": str(payload["result_mode"]),
        "repeat": int(payload["repeat"]),
        "query_batch_size": int(payload["query_batch_size"]),
        "batch_count": int(payload["batch_count"]),
        "input_load_sec": float(payload["input_load_sec"]),
        "input_pack_sec": float(payload["input_pack_sec"]),
        "execution_prepare_sec": float(payload["execution_prepare_sec"]),
        "median_query_sec": float(payload["elapsed_median_sec"]),
        "min_query_sec": float(payload["elapsed_min_sec"]),
        "max_query_sec": float(payload["elapsed_max_sec"]),
        "elapsed_runs_sec": [float(value) for value in payload["elapsed_runs_sec"]],
        "output_contract": "device_ranked_summary_aggregate",
        "summary": dict(payload["ranked_aggregate_summary"]),
        "contract": payload["contract"],
        "claim_boundary": payload["claim_boundary"],
        "batch_phase_timings": payload.get("batch_phase_timings", []),
    }
    row["cold_load_pack_prepare_query_sec"] = _cold_total(row)
    return row


def _mean(values: list[float]) -> float:
    return float(statistics.mean(values)) if values else 0.0


def _sweep_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "docs" / "reports").glob(SWEEP_GLOB)):
        payload = _read_json(path)
        if str(path).endswith("_best_r10.json"):
            label = "full_batch_best_r10"
        else:
            label = f"batch_size_{int(payload['query_batch_size'])}"
        rows.append(_runner_row(payload, label=label))
    rows.sort(key=lambda row: (row["query_batch_size"], row["repeat"]))
    return rows


def _signature_delta(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    keys = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    return {
        **{key: int(a[key]) - int(b[key]) for key in keys},
        "sum_distance_delta": float(a["sum_distance"]) - float(b["sum_distance"]),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    m105 = _read_json(root / M105_PACKET)
    full_batch = _runner_row(_read_json(root / FULL_BATCH_BEST), label="rtdl_optix_full_batch_direct_aggregate")
    sweep_rows = _sweep_rows(root)
    direct_graph = dict(m105["rtdl"]["optix_direct_graph_best"])
    same_stream = dict(m105["rtdl"]["optix_same_stream_partner"])
    m104_optix = dict(m105["rtdl"]["m104_generic_optix"])
    m104_embree = dict(m105["rtdl"]["m104_generic_embree"])
    author = dict(m105["author_rtnn"])

    full_query = float(full_batch["median_query_sec"])
    direct_query = float(direct_graph["median_query_sec"])
    author_total = float(author["median_total_search_sec"])
    author_compute = float(author["median_search_compute_sec"])
    m104_optix_query = float(m104_optix["median_query_sec"])
    m104_embree_query = float(m104_embree["median_query_sec"])

    comparisons = {
        "rtdl_full_batch_over_direct_graph_query": direct_query / full_query,
        "rtdl_full_batch_query_over_author_total_search": author_total / full_query,
        "author_compute_over_rtdl_full_batch_query": full_query / author_compute,
        "rtdl_full_batch_over_m104_generic_optix_query": m104_optix_query / full_query,
        "rtdl_full_batch_over_m104_embree_query": m104_embree_query / full_query,
        "rtdl_full_batch_cold_prepared_total_over_author_process": (
            float(full_batch["cold_load_pack_prepare_query_sec"]) / float(author["median_process_elapsed_sec"])
        ),
        "rtdl_full_batch_over_same_stream_query": float(same_stream["median_query_sec"]) / full_query,
    }

    sweep_summary = [
        {
            "query_batch_size": int(row["query_batch_size"]),
            "repeat": int(row["repeat"]),
            "median_query_sec": float(row["median_query_sec"]),
            "min_query_sec": float(row["min_query_sec"]),
            "max_query_sec": float(row["max_query_sec"]),
            "batch_count": int(row["batch_count"]),
            "cold_load_pack_prepare_query_sec": float(row["cold_load_pack_prepare_query_sec"]),
            "mean_query_sec": _mean(row["elapsed_runs_sec"]),
        }
        for row in sweep_rows
    ]

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4502 / V3 M106",
        "input_contract": m105["input_contract"],
        "author_rtnn": author,
        "rtdl": {
            "optix_full_batch_direct_aggregate": full_batch,
            "optix_direct_graph_m105": direct_graph,
            "optix_same_stream_partner_m105": same_stream,
            "m104_generic_optix": m104_optix,
            "m104_generic_embree": m104_embree,
        },
        "query_batch_sweep": sweep_summary,
        "comparisons": comparisons,
        "signature_deltas": {
            "full_batch_minus_direct_graph": _signature_delta(full_batch["summary"], direct_graph["summary"]),
            "full_batch_minus_m104_optix": _signature_delta(full_batch["summary"], m104_optix["summary"]),
            "full_batch_minus_m104_embree": _signature_delta(full_batch["summary"], m104_embree["summary"]),
        },
        "graph_cap_audit": {
            "graph_query_count_cap": 65_536,
            "cap_is_native_wrapper_policy_not_observed_aggregate_only_best_path": True,
            "aggregate_only_best_mode": "ranked-summary-aggregate-prepared-query-batch-float32",
            "partner_continuation_graph_mode_still_relevant": True,
            "reading": (
                "For a single ranked-summary aggregate on KITTI-1M, the non-graph prepared "
                "direct aggregate can run all one million queries as one batch and is faster "
                "than replaying capped graph chunks. The graph/device-partials route remains "
                "the explicit route when a same-stream partner continuation needs device "
                "partial rows."
            ),
        },
        "claim_boundary": {
            "same_input_author_rtdl_comparison": True,
            "paper_reproduction_wording_allowed": False,
            "same_output_contract_author_vs_rtdl": False,
            "author_outputs_comparable_checksum": False,
            "rtdl_best_materializes_full_neighbor_ids": False,
            "rtdl_best_is_hot_prepared_aggregate": True,
            "rtdl_best_requires_partner": False,
            "graph_mode_required_for_aggregate_only": False,
            "same_stream_partner_required_only_for_continuation": True,
            "broad_rt_core_speedup_claim_authorized": False,
            "public_release_wording_authorized": False,
        },
        "conclusion": (
            "M106 supersedes the M105 direct-graph-as-best RTDL wording for this KITTI-1M "
            "aggregate contract. The current fastest RTDL hot prepared aggregate is the "
            "full-batch non-graph prepared direct aggregate: it measures about 0.154s median "
            "query, 1.68x faster than the M105 direct graph row and 2.26x faster than the "
            "author synchronized total-search timer, while the author pure compute timer "
            "remains about 15x faster and the author cold process remains faster. The honest "
            "route split is aggregate-only full-batch direct, partner-continuation graph."
        ),
    }


def _fmt(value: float) -> str:
    return f"{value:.3f}s"


def write_report(packet: dict[str, Any], path: Path) -> None:
    author = packet["author_rtnn"]
    rtdl = packet["rtdl"]
    comp = packet["comparisons"]
    full = rtdl["optix_full_batch_direct_aggregate"]
    graph = rtdl["optix_direct_graph_m105"]
    same_stream = rtdl["optix_same_stream_partner_m105"]
    lines = [
        "# Goal4502 / V3 M106 RTNN Full-Batch Route Refresh",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Performance Matrix",
        "",
        "| Row | Contract | Cold/process time | Hot/search time | Detail | Reading |",
        "| --- | --- | ---: | ---: | --- | --- |",
        (
            "| Author RTNN C++/CUDA/OptiX | full K-id buffer copied to host | "
            f"{_fmt(author['median_process_elapsed_sec'])} process median | "
            f"{_fmt(author['median_total_search_sec'])} total-search median | "
            f"compute {_fmt(author['median_search_compute_sec'])}; D2H {_fmt(author['median_result_copy_d2h_sec'])} | "
            "specialized author RTNN route; fastest cold process and pure compute here |"
        ),
        (
            "| RTDL OptiX full-batch prepared direct aggregate | hot prepared float32 ranked-summary aggregate | "
            f"{_fmt(full['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(full['median_query_sec'])} median query | "
            f"one query batch of {full['query_batch_size']:,}; no full neighbor-id materialization | current fastest RTDL aggregate-only route |"
        ),
        (
            "| RTDL OptiX direct graph M105 | hot prepared float32 ranked-summary aggregate | "
            f"{_fmt(graph['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(graph['median_query_sec'])} median query | "
            "65,536-query graph chunks; no full neighbor-id materialization | superseded for aggregate-only KITTI-1M |"
        ),
        (
            "| RTDL OptiX same-stream CuPy M105 | partner-continuation aggregate | "
            f"{_fmt(same_stream['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(same_stream['median_query_sec'])} median query | "
            "same-stream device partial consumer | use when the app needs partner continuation |"
        ),
        (
            "| RTDL OptiX M104 generic | exact float64 ranked-summary aggregate | "
            f"{_fmt(rtdl['m104_generic_optix']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['m104_generic_optix']['median_query_sec'])} median query | "
            "generic exact aggregate | superseded for this float32 hot aggregate contract |"
        ),
        (
            "| RTDL Embree M104 CPU | exact CPU ranked-summary aggregate | "
            f"{_fmt(rtdl['m104_generic_embree']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['m104_generic_embree']['median_query_sec'])} median query | "
            "CPU aggregate; tie-sensitive kth checksum caveat | CPU fallback/proof row |"
        ),
        "",
        "## Query Batch Sweep",
        "",
        "| Query batch size | Batches | Repeat | Median query | Min | Max | Cold load+pack+prepare+query |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in packet["query_batch_sweep"]:
        lines.append(
            "| "
            f"{row['query_batch_size']:,} | {row['batch_count']} | {row['repeat']} | "
            f"{_fmt(row['median_query_sec'])} | {_fmt(row['min_query_sec'])} | "
            f"{_fmt(row['max_query_sec'])} | {_fmt(row['cold_load_pack_prepare_query_sec'])} |"
        )
    lines.extend(
        [
            "",
            "## Ratios",
            "",
            f"- Full-batch prepared direct aggregate vs M105 direct graph: {comp['rtdl_full_batch_over_direct_graph_query']:.2f}x faster.",
            f"- Full-batch prepared direct aggregate vs author synchronized total-search: {comp['rtdl_full_batch_query_over_author_total_search']:.2f}x faster for RTDL aggregate query.",
            f"- Author synchronized compute phase vs full-batch RTDL aggregate: {comp['author_compute_over_rtdl_full_batch_query']:.2f}x faster for author compute.",
            f"- Full-batch prepared direct aggregate vs Goal4500 generic OptiX aggregate: {comp['rtdl_full_batch_over_m104_generic_optix_query']:.2f}x faster.",
            f"- Full-batch prepared direct aggregate vs Goal4500 Embree aggregate: {comp['rtdl_full_batch_over_m104_embree_query']:.2f}x faster.",
            f"- Cold author process vs RTDL full-batch load+pack+prepare+query: author is {comp['rtdl_full_batch_cold_prepared_total_over_author_process']:.2f}x faster.",
            "",
            "## Graph Cap Audit",
            "",
            "- The current graph/device-partials path rejects prepared query handles above 65,536 queries.",
            "- That cap does not block the aggregate-only best route: the non-graph prepared direct aggregate handles the full 1,000,000-query batch and is faster here.",
            "- The graph/device-partials route remains useful when a same-stream partner continuation needs device partial rows instead of a final scalar aggregate.",
            "- Next graph work should target large-query partner continuation or device partial reduction, not aggregate-only RTNN timing.",
            "",
            "## Boundaries",
            "",
            "- Same input: yes, all rows are read against the Goal4500 KITTI-1M CSV, radius 1.0, K=50, self-query contract.",
            "- Same output surface with author RTNN: no. Author RTNN copies the full K-id result buffer; RTDL best returns ranked-summary aggregates.",
            "- Paper reproduction: no. This is a bounded KITTI paper-family recipe, not the paper's exact frame recipe.",
            "- Public speedup wording: still blocked. This is current-route evidence, not a public RT-core speedup claim.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["comparisons"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
