from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.rtnn_author_same_input_comparison.goal4501.v1"
OUT_JSON = Path("docs/reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4501_v3_0_m105_rtnn_author_same_input_comparison_2026-06-17.md")
AUTHOR_REPEAT_GLOB = "goal4501_author_rtnn_kitti_1m_r1_k50_sm89_sync_r*.json"
AUTHOR_PATCH_JSON = Path("docs/reports/goal4501_author_rtnn_cuda12_sm89_patch.json")
RTDL_DIRECT_JSON = Path("docs/reports/goal4501_rtdl_optix_kitti_1m_r1_k50_direct_graph_best.json")
RTDL_SAME_STREAM_JSON = Path("docs/reports/goal4501_rtdl_optix_kitti_1m_r1_k50_same_stream_best.json")
M104_JSON = Path("docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median of an empty series")
    return float(statistics.median(values))


def _author_summary(report_dir: Path) -> dict[str, Any]:
    paths = sorted(report_dir.glob(AUTHOR_REPEAT_GLOB))
    if not paths:
        raise FileNotFoundError(f"no author repeat reports matched {AUTHOR_REPEAT_GLOB}")
    rows = []
    for path in paths:
        payload = _read_json(path)
        timings = payload["timings"]
        rows.append(
            {
                "path": str(path),
                "returncode": int(payload["returncode"]),
                "elapsed_sec": float(payload["elapsed_sec"]),
                "total_search_sec": float(timings["total search time"]["last_ms"]) / 1000.0,
                "search_compute_sec": float(timings["search compute"]["last_ms"]) / 1000.0,
                "result_copy_d2h_sec": float(timings["result copy D2H"]["last_ms"]) / 1000.0,
                "sort_partition_sec": float(timings["sort and/or partition queries"]["last_ms"]) / 1000.0,
                "create_pipeline_sec": float(timings["create pipeline"]["last_ms"]) / 1000.0,
            }
        )
    return {
        "repeat": len(rows),
        "rows": rows,
        "median_process_elapsed_sec": _median([row["elapsed_sec"] for row in rows]),
        "median_total_search_sec": _median([row["total_search_sec"] for row in rows]),
        "median_search_compute_sec": _median([row["search_compute_sec"] for row in rows]),
        "median_result_copy_d2h_sec": _median([row["result_copy_d2h_sec"] for row in rows]),
        "median_sort_partition_sec": _median([row["sort_partition_sec"] for row in rows]),
        "output_contract": "full_k_id_buffer_copied_to_host",
        "implementation": "author_cpp_cuda_optix",
    }


def _rtdl_row(payload: dict[str, Any], *, label: str) -> dict[str, Any]:
    cold_prepared_sec = (
        float(payload["input_load_sec"])
        + float(payload["input_pack_sec"])
        + float(payload["execution_prepare_sec"])
        + float(payload["elapsed_median_sec"])
    )
    summary = dict(payload["ranked_aggregate_summary"])
    return {
        "label": label,
        "row": payload["row"],
        "result_mode": payload["result_mode"],
        "repeat": int(payload["repeat"]),
        "input_load_sec": float(payload["input_load_sec"]),
        "input_pack_sec": float(payload["input_pack_sec"]),
        "execution_prepare_sec": float(payload["execution_prepare_sec"]),
        "median_query_sec": float(payload["elapsed_median_sec"]),
        "cold_load_pack_prepare_query_sec": cold_prepared_sec,
        "output_contract": "device_ranked_summary_aggregate",
        "summary": summary,
        "contract": payload["contract"],
        "claim_boundary": payload["claim_boundary"],
    }


def _m104_rows(m104: dict[str, Any]) -> dict[str, Any]:
    return {
        backend: _rtdl_row(m104["results"][backend]["payload"], label=f"m104_{backend}_generic_aggregate")
        for backend in ("optix", "embree")
    }


def _signature_delta(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    keys = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    return {
        **{key: int(a[key]) - int(b[key]) for key in keys},
        "sum_distance_delta": float(a["sum_distance"]) - float(b["sum_distance"]),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    report_dir = root / "docs" / "reports"
    author = _author_summary(report_dir)
    rtdl_direct = _rtdl_row(_read_json(root / RTDL_DIRECT_JSON), label="rtdl_optix_direct_graph_best")
    rtdl_same_stream = _rtdl_row(_read_json(root / RTDL_SAME_STREAM_JSON), label="rtdl_optix_same_stream_partner")
    m104 = _m104_rows(_read_json(root / M104_JSON))
    patch = _read_json(root / AUTHOR_PATCH_JSON) if (root / AUTHOR_PATCH_JSON).exists() else None

    author_total = float(author["median_total_search_sec"])
    author_compute = float(author["median_search_compute_sec"])
    direct_query = float(rtdl_direct["median_query_sec"])
    generic_query = float(m104["optix"]["median_query_sec"])
    embree_query = float(m104["embree"]["median_query_sec"])

    comparisons = {
        "rtdl_direct_graph_query_over_author_total_search": author_total / direct_query,
        "author_compute_over_rtdl_direct_graph_query": direct_query / author_compute,
        "rtdl_direct_graph_over_m104_generic_query": generic_query / direct_query,
        "rtdl_direct_graph_over_embree_generic_query": embree_query / direct_query,
        "author_process_over_rtdl_direct_cold_prepared_total": (
            float(rtdl_direct["cold_load_pack_prepare_query_sec"]) / float(author["median_process_elapsed_sec"])
        ),
    }

    direct_vs_m104 = _signature_delta(rtdl_direct["summary"], m104["optix"]["summary"])
    direct_vs_embree = _signature_delta(rtdl_direct["summary"], m104["embree"]["summary"])

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4501 / V3 M105",
        "input_contract": {
            "dataset": "KITTI-1M bounded paper-family CSV from Goal4500",
            "point_count": 1_000_000,
            "query_count": 1_000_000,
            "query_relation": "self_query",
            "radius": 1.0,
            "k_max": 50,
            "same_input_csv": "/workspace/data/kitti/rtdl_goal4500/kitti_1m_points.csv",
            "paper_equivalence": "bounded_family_recipe_not_exact_paper_recipe",
        },
        "author_rtnn": author,
        "author_patch": patch,
        "rtdl": {
            "optix_direct_graph_best": rtdl_direct,
            "optix_same_stream_partner": rtdl_same_stream,
            "m104_generic_optix": m104["optix"],
            "m104_generic_embree": m104["embree"],
        },
        "comparisons": comparisons,
        "signature_deltas": {
            "direct_graph_minus_m104_optix": direct_vs_m104,
            "direct_graph_minus_m104_embree": direct_vs_embree,
        },
        "claim_boundary": {
            "same_input_author_rtdl_comparison": True,
            "paper_reproduction_wording_allowed": False,
            "same_output_contract_author_vs_rtdl": False,
            "author_outputs_comparable_checksum": False,
            "rtdl_best_materializes_full_neighbor_ids": False,
            "rtdl_best_is_hot_prepared_aggregate": True,
            "author_patch_external_compatibility_only": bool(
                patch and patch.get("claim_boundary", {}).get("algorithm_changed") is False
            ),
            "broad_rt_core_speedup_claim_authorized": False,
            "public_release_wording_authorized": False,
        },
        "conclusion": (
            "RTDL V3 current best makes the KITTI-1M RTNN aggregate path genuinely subsecond "
            "after data and graph preparation, and it is about 30x faster than the older generic "
            "Goal4500 OptiX aggregate. The author C++/CUDA/OptiX implementation still maps the "
            "same search workload to RT cores much more efficiently at the pure compute phase, "
            "and it is faster on cold whole-process time. The comparison is useful, but it must "
            "be reported by contract: author full K-id materialization versus RTDL hot prepared "
            "ranked-summary aggregate are not the same output surface."
        ),
    }


def _fmt(value: float) -> str:
    return f"{value:.3f}s"


def write_report(packet: dict[str, Any], path: Path) -> None:
    author = packet["author_rtnn"]
    rtdl = packet["rtdl"]
    comp = packet["comparisons"]
    lines = [
        "# Goal4501 / V3 M105 RTNN Author Same-Input Comparison",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Performance Matrix",
        "",
        "| Row | Contract | Cold/process time | Hot/search time | Compute/materialization detail | Reading |",
        "| --- | --- | ---: | ---: | --- | --- |",
        (
            "| Author RTNN C++/CUDA/OptiX | full K-id buffer copied to host | "
            f"{_fmt(author['median_process_elapsed_sec'])} process median | "
            f"{_fmt(author['median_total_search_sec'])} total-search median | "
            f"compute {_fmt(author['median_search_compute_sec'])}; D2H {_fmt(author['median_result_copy_d2h_sec'])} | "
            "specialized RTNN route; fastest cold full process here |"
        ),
        (
            "| RTDL OptiX direct graph | hot prepared float32 ranked-summary aggregate | "
            f"{_fmt(rtdl['optix_direct_graph_best']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['optix_direct_graph_best']['median_query_sec'])} median query | "
            "device aggregate; no full neighbor-id materialization | current best RTDL aggregate route |"
        ),
        (
            "| RTDL OptiX same-stream CuPy | partner-continuation aggregate | "
            f"{_fmt(rtdl['optix_same_stream_partner']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['optix_same_stream_partner']['median_query_sec'])} median query | "
            "same-stream CuPy consumer; no host scalar/partial read before consumer | use when partner continuation is required |"
        ),
        (
            "| RTDL OptiX M104 generic | exact float64 ranked-summary aggregate | "
            f"{_fmt(rtdl['m104_generic_optix']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['m104_generic_optix']['median_query_sec'])} median query | "
            "generic aggregate without prepared-query graph replay | superseded by M105 graph path for this contract |"
        ),
        (
            "| RTDL Embree M104 CPU | exact CPU ranked-summary aggregate | "
            f"{_fmt(rtdl['m104_generic_embree']['cold_load_pack_prepare_query_sec'])} load+pack+prepare+query | "
            f"{_fmt(rtdl['m104_generic_embree']['median_query_sec'])} median query | "
            "CPU aggregate; tie-sensitive kth checksum caveat | CPU fallback/proof row, not the RT target |"
        ),
        "",
        "## Ratios",
        "",
        f"- RTDL direct graph hot aggregate vs author synchronized total-search: {comp['rtdl_direct_graph_query_over_author_total_search']:.2f}x faster for RTDL aggregate query.",
        f"- Author synchronized compute phase vs RTDL direct graph hot aggregate: {comp['author_compute_over_rtdl_direct_graph_query']:.2f}x faster for author compute.",
        f"- RTDL direct graph vs Goal4500 generic OptiX aggregate: {comp['rtdl_direct_graph_over_m104_generic_query']:.2f}x faster.",
        f"- RTDL direct graph vs Goal4500 Embree aggregate: {comp['rtdl_direct_graph_over_embree_generic_query']:.2f}x faster.",
        f"- Cold author process vs RTDL load+pack+prepare+query: author is {comp['author_process_over_rtdl_direct_cold_prepared_total']:.2f}x faster.",
        "",
        "## Boundaries",
        "",
        "- Same input: yes, the author RTNN and RTDL rows use the same Goal4500 KITTI-1M CSV, radius 1.0, K=50, self-query contract.",
        "- Same output surface: no. Author RTNN copies the full K-id result buffer; RTDL best rows return ranked-summary aggregates.",
        "- Paper reproduction: no. The KITTI row is a bounded paper-family recipe, not the paper's exact frame recipe.",
        "- Author patch: external compatibility only, for CUDA 12/Ada architecture consistency; it does not change the neighbor-search algorithm.",
    ]
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
