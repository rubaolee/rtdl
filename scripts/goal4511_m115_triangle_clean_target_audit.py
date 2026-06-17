from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.triangle_clean_target_audit.goal4511.v1"
OUT_JSON = Path("docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.md")

POST_M78_COMPARISON = Path(
    "docs/reports/goal4475_v3_0_m79_triangle_post_m78_comparison_packet_2026-06-16.json"
)
SORT_RLE_RERANK = Path(
    "docs/reports/goal4479_v3_0_m83_triangle_sort_rle_unique_count_packet_2026-06-16.json"
)
LOCAL_HASH_COVERAGE = Path(
    "docs/reports/goal4492_v3_0_m96_triangle_source_group_unique_feasibility_2026-06-17.json"
)
LOCAL_HASH_PROTOTYPE = Path(
    "docs/reports/goal4493_v3_0_m97_triangle_local_hash_unique_prototype_2026-06-17.json"
)
LOCAL_HASH_INTEGRATED = Path(
    "docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.json"
)

DATASETS = ("com_lj", "soc_livejournal1", "com_orkut")


def _load(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _formal_external_matrix(root: Path) -> list[dict[str, Any]]:
    packet = _load(root, POST_M78_COMPARISON)
    rows: list[dict[str, Any]] = []
    for row in packet["rows"]:
        rows.append(
            {
                "dataset": row["dataset"],
                "display_name": row["display_name"],
                "triangle_count": int(row["count"]),
                "rtdl_m78_total_s": float(row["rtdl_m78_total_s"]),
                "rtdl_m78_query_median_s": float(row["rtdl_m78_query_median_s"]),
                "rtdl_m78_native_traversal_median_s": float(
                    row["rtdl_m78_native_traversal_median_s"]
                ),
                "m78_speedup_vs_m71_total": float(row["m78_speedup_vs_m71_total"]),
                "cugraph_faster_than_m78_total": float(row["cugraph_faster_than_m78_total"]),
                "author_rt_pipeline_status": row.get("author_rt_status", "ok"),
                "author_bs_pipeline_status": row.get("author_bs_status", "ok"),
                "m78_total_faster_than_author_rt_pipeline": row.get(
                    "m78_total_faster_than_author_rt_pipeline"
                ),
                "m78_query_slower_than_author_rt_count": row.get(
                    "m78_query_slower_than_author_rt_count"
                ),
                "m78_query_slower_than_author_bs_count": row.get(
                    "m78_query_slower_than_author_bs_count"
                ),
            }
        )
    return rows


def _sort_rle_matrix(root: Path) -> list[dict[str, Any]]:
    packet = _load(root, SORT_RLE_RERANK)
    rows: list[dict[str, Any]] = []
    for row in packet["performance_rows"]:
        rows.append(
            {
                "dataset": row["dataset"],
                "display_name": row["display_name"],
                "triangle_count": int(row["count"]),
                "baseline_total_s": float(row["baseline_total_s"]),
                "candidate_total_s": float(row["candidate_total_s"]),
                "total_speedup": float(row["total_speedup"]),
                "baseline_segment_build_s": float(row["baseline_segment_build_s"]),
                "candidate_segment_build_s": float(row["candidate_segment_build_s"]),
                "segment_build_speedup": float(row["segment_build_speedup"]),
                "query_speedup": float(row["query_speedup"]),
                "same_count_rays_weights": bool(row["same_count_rays_weights"]),
                "sort_rle_telemetry_s": float(row["candidate_telemetry_sort_rle_s"]),
            }
        )
    return rows


def _local_hash_matrix(root: Path) -> dict[str, Any]:
    coverage = _load(root, LOCAL_HASH_COVERAGE)
    prototype = _load(root, LOCAL_HASH_PROTOTYPE)
    integrated = _load(root, LOCAL_HASH_INTEGRATED)
    coverage_rows = {row["dataset"]: row for row in coverage["rows"]}
    prototype_rows = {row["dataset"]: row for row in prototype["rows"]}
    comparisons = integrated["summary"]["comparisons"]
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        coverage_row = coverage_rows[dataset]
        prototype_row = prototype_rows[dataset]
        comparison = comparisons[dataset]
        rows.append(
            {
                "dataset": dataset,
                "two_hop_rows": int(coverage_row["total_two_hop_rows"]),
                "coverage_2048_pct": float(
                    coverage_row["bounded_source_group_coverage"]["2048"]["two_hop_pct"]
                ),
                "coverage_16384_pct": float(
                    coverage_row["bounded_source_group_coverage"]["16384"]["two_hop_pct"]
                ),
                "coverage_65536_pct": float(
                    coverage_row["bounded_source_group_coverage"]["65536"]["two_hop_pct"]
                ),
                "prototype_2048_speedup_vs_reference": float(
                    prototype_row["local_hash_speedup_vs_reference"]
                ),
                "prototype_validation_ok": bool(prototype_row["validation_ok"]),
                "integrated_decision": comparison["decision"],
                "baseline_over_hybrid_backend": float(comparison["baseline_over_hybrid_backend"]),
                "baseline_over_hybrid_segment_ray_build": float(
                    comparison["baseline_over_hybrid_segment_ray_build"]
                ),
                "baseline_over_hybrid_total": float(comparison["baseline_over_hybrid_total"]),
            }
        )
    return {
        "rows": rows,
        "summary": {
            "single_small_kernel_rejected": True,
            "prototype_branch_validated": bool(prototype["summary"]["all_validated"]),
            "integrated_candidate_rejected": all(
                row["integrated_decision"] == "reject_hybrid_candidate" for row in rows
            ),
            "all_integrated_backend_regressed": all(
                row["baseline_over_hybrid_backend"] < 1.0 for row in rows
            ),
            "all_integrated_segment_build_regressed": all(
                row["baseline_over_hybrid_segment_ray_build"] < 1.0 for row in rows
            ),
        },
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    formal_external = _formal_external_matrix(root)
    sort_rle = _sort_rle_matrix(root)
    local_hash = _local_hash_matrix(root)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4511 / V3 M115",
        "app": "triangle_counting",
        "evidence_inputs": [
            str(POST_M78_COMPARISON),
            str(SORT_RLE_RERANK),
            str(LOCAL_HASH_COVERAGE),
            str(LOCAL_HASH_PROTOTYPE),
            str(LOCAL_HASH_INTEGRATED),
        ],
        "formal_external_comparison": {
            "source": "Goal4475 post-M78 comparison packet",
            "rows": formal_external,
            "reading": (
                "RTDL M78 is exact and much faster than the authors full pipeline "
                "on completed rows, but cuGraph remains faster end to end and "
                "authors pure count kernels remain faster than RTDL query/native "
                "traversal. This packet is the formal external comparison baseline, "
                "not a public RT-core speedup claim."
            ),
            "cugraph_wins_all_rows": all(
                row["cugraph_faster_than_m78_total"] > 1.0 for row in formal_external
            ),
            "public_speedup_claim_authorized": False,
        },
        "current_internal_route": {
            "source": "Goal4479 same-commit M83 rerank",
            "route": (
                "unique_weighted segmented RT-2A1 + numba_direct_sort_rle unique/count "
                "+ prepared_segment_replay + generic prepared ray-batch weighted any-hit sum"
            ),
            "rows": sort_rle,
            "same_counts_all_rows": all(row["same_count_rays_weights"] for row in sort_rle),
            "speedup_all_rows": all(row["total_speedup"] > 1.0 for row in sort_rle),
            "route_promoted_internal_only": True,
        },
        "local_hash_decision": local_hash,
        "m113_applicability": {
            "current_route_should_use_m113": False,
            "reason": (
                "Triangle Counting already uses a generic prepared ray-batch "
                "weighted any-hit primitive inside graph-derived segments. The "
                "current bottleneck is segment unique/count materialization and "
                "per-segment launch/envelope work, not a missing prepared graph "
                "chunk executor contract."
            ),
            "future_use": (
                "A future coarser-batched segmented unique/count reduction or "
                "prepared replay executor may reuse the M113 discipline if it "
                "really has contiguous prepared chunks, per-chunk handles, and "
                "explicit partner continuation."
            ),
        },
        "readiness": {
            "internal_v3_clean_target_closed": True,
            "all_three_large_paper_rows_exact": True,
            "current_route_evidence_bounded": True,
            "public_rt_core_speedup_claim_authorized": False,
            "rtdl_beats_cugraph_claim_authorized": False,
            "rtdl_beats_authors_pure_kernel_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "remaining_debt": [
            {
                "item": "public triangle-count RT-core speedup wording",
                "status": "blocked",
                "reason": "cuGraph and authors pure kernels still beat the relevant RTDL timings",
            },
            {
                "item": "segment unique/count materialization",
                "status": "open_for_future_optimization",
                "reason": "Goal4479 improves sort/RLE but leaves it as the largest materialization boundary",
            },
            {
                "item": "integrated local-hash branch",
                "status": "rejected",
                "reason": "Goal4494 regresses backend and segment-ray build on all three paper rows",
            },
        ],
        "conclusion": (
            "Triangle Counting is closed as an internal V3 clean target. RTDL now "
            "completes the three former-OOM large paper rows exactly with generic "
            "ray/triangle weighted-summary primitives and partner-side graph "
            "lowering. The current internal route is the Goal4479 "
            "numba_direct_sort_rle prepared segment replay path, while the formal "
            "external comparison remains Goal4475/M78. The honest public boundary "
            "is unchanged: do not claim RTDL beats cuGraph, authors pure kernels, "
            "or public RT-core triangle-count speedups."
        ),
    }


def _fmt_sec(value: float) -> str:
    return f"{value:.3f}s"


def _fmt_x(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}x"


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4511 / V3 M115 Triangle Counting Clean-Target Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Formal External Comparison",
        "",
        packet["formal_external_comparison"]["reading"],
        "",
        "| Dataset | RTDL M78 total | cuGraph faster | RTDL vs M71 | Author pure-kernel reading |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in packet["formal_external_comparison"]["rows"]:
        if row["author_rt_pipeline_status"] == "ok":
            author_reading = (
                f"RTDL query {_fmt_x(row['m78_query_slower_than_author_rt_count'])} "
                "slower than author rt count"
            )
        else:
            author_reading = row["author_rt_pipeline_status"]
        lines.append(
            "| "
            f"{row['display_name']} | "
            f"{_fmt_sec(row['rtdl_m78_total_s'])} | "
            f"{_fmt_x(row['cugraph_faster_than_m78_total'])} | "
            f"{_fmt_x(row['m78_speedup_vs_m71_total'])} | "
            f"{author_reading} |"
        )

    lines.extend(
        [
            "",
            "## Current Internal Route",
            "",
            f"`{packet['current_internal_route']['route']}`",
            "",
            "| Dataset | Baseline total | Sort/RLE total | Total speedup | Segment-build speedup |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in packet["current_internal_route"]["rows"]:
        lines.append(
            "| "
            f"{row['display_name']} | "
            f"{_fmt_sec(row['baseline_total_s'])} | "
            f"{_fmt_sec(row['candidate_total_s'])} | "
            f"{_fmt_x(row['total_speedup'])} | "
            f"{_fmt_x(row['segment_build_speedup'])} |"
        )

    lines.extend(
        [
            "",
            "## Local-Hash Decision",
            "",
            "| Dataset | 2,048-row coverage | 16,384-row coverage | Prototype speedup | Integrated backend ratio | Integrated segment-build ratio | Decision |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in packet["local_hash_decision"]["rows"]:
        lines.append(
            "| "
            f"{row['dataset']} | "
            f"{_fmt_pct(row['coverage_2048_pct'])} | "
            f"{_fmt_pct(row['coverage_16384_pct'])} | "
            f"{_fmt_x(row['prototype_2048_speedup_vs_reference'])} | "
            f"{_fmt_x(row['baseline_over_hybrid_backend'])} | "
            f"{_fmt_x(row['baseline_over_hybrid_segment_ray_build'])} | "
            f"`{row['integrated_decision']}` |"
        )

    lines.extend(
        [
            "",
            "The local-hash branch is not dismissed because the idea is invalid. It is dismissed because the integrated route regresses backend and segment-ray build on all three paper rows. `com_orkut` has a slightly better integrated total in the M98 packet, but it fails the route-promotion gate because the hot materialization phases got worse.",
            "",
            "## M113 Applicability",
            "",
            f"- Current route should use M113: `{packet['m113_applicability']['current_route_should_use_m113']}`.",
            f"- Reason: {packet['m113_applicability']['reason']}",
            f"- Future use: {packet['m113_applicability']['future_use']}",
            "",
            "## Closed",
            "",
            "- All three large former-OOM paper rows complete exactly under RTDL's generic ray/triangle weighted-summary route.",
            "- Current internal route is Goal4479 `numba_direct_sort_rle`, not the rejected local-hash hybrid.",
            "- CuPy/Numba partner roles are evidence-bounded and explicit; there is no hidden automatic partner selection.",
            "- App-specific native engine callbacks remain disallowed.",
            "",
            "## Still Blocked",
            "",
            "- Public RT-core triangle-count speedup wording.",
            "- RTDL-beats-cuGraph wording.",
            "- RTDL-beats-authors-pure-kernel wording.",
            "- Treating M113 as the current Triangle Counting performance path.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["readiness"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
