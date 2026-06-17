from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.rtnn_clean_target_closeout.goal4508.v1"
OUT_JSON = Path("docs/reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.md")

M104_PACKET = Path("docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json")
M106_PACKET = Path("docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json")
M107_PACKET = Path("docs/reports/goal4503_v3_0_m107_rtnn_point_file_front_door_2026-06-17.json")
M111_PACKET = Path("docs/reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.json")


def _read_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _seconds(value: Any) -> float:
    return float(value)


def _fmt(value: float) -> str:
    return f"{value:.6f}s"


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    m104 = _read_json(root, M104_PACKET)
    m106 = _read_json(root, M106_PACKET)
    m107 = _read_json(root, M107_PACKET)
    m111 = _read_json(root, M111_PACKET)

    m104_optix = m104["results"]["optix"]["payload"]["elapsed_median_sec"]
    m104_embree = m104["results"]["embree"]["payload"]["elapsed_median_sec"]
    m106_best = m106["rtdl"]["optix_full_batch_direct_aggregate"]
    m107_front = m107["app_front_door"]
    author = m106["author_rtnn"]
    chunk_rows = tuple(m111["rows"])

    contract_rows = (
        {
            "lane": "RTDL OptiX vs Embree same-input backend gate",
            "evidence": "Goal4500 / V3 M104",
            "contract": "exact float64 prepared fixed-radius ranked-summary aggregate",
            "dataset": "Goal4500 bounded KITTI-1M paper-family CSV",
            "primary_measure": f"OptiX {_fmt(_seconds(m104_optix))}; Embree {_fmt(_seconds(m104_embree))}",
            "reading": (
                f"RTDL/OptiX is {_seconds(m104['results']['optix_over_embree_speedup']):.2f}x "
                "faster than RTDL/Embree for this same-input, same-contract gate."
            ),
            "boundary": (
                "RTDL-internal backend comparison only; strict kth-id checksum remains "
                "tie-sensitive, and this is not exact RTNN paper reproduction."
            ),
        },
        {
            "lane": "Current RTDL aggregate-only route",
            "evidence": "Goal4502 / V3 M106",
            "contract": "hot prepared float32 ranked-summary aggregate, no full neighbor-id materialization",
            "dataset": "same Goal4500 bounded KITTI-1M CSV",
            "primary_measure": (
                f"hot query {_fmt(_seconds(m106_best['median_query_sec']))}; "
                f"cold load+pack+prepare+query {_fmt(_seconds(m106_best['cold_load_pack_prepare_query_sec']))}"
            ),
            "reading": (
                "Full-batch non-graph prepared direct aggregate is the current fastest "
                "RTDL aggregate-only route; graph/device partials are not the aggregate-only default."
            ),
            "boundary": (
                "Aggregate output surface differs from the author full K-id materialization surface; "
                "do not collapse these rows into author-output equivalence."
            ),
        },
        {
            "lane": "RTNN app front door",
            "evidence": "Goal4503 / V3 M107",
            "contract": "benchmark app `--point-file` path into the M106 full-batch aggregate route",
            "dataset": "same Goal4500 bounded KITTI-1M CSV",
            "primary_measure": (
                f"hot query {_fmt(_seconds(m107_front['median_query_sec']))}; "
                f"cold load+pack+prepare+query {_fmt(_seconds(m107_front['cold_load_pack_prepare_query_sec']))}"
            ),
            "reading": (
                "The promoted RTNN app can ingest an external point file and reaches "
                "the current full-batch aggregate route without regenerating synthetic data."
            ),
            "boundary": "Front-door proof only; it does not change paper-reproduction or public-speedup boundaries.",
        },
        {
            "lane": "Author-code diagnostic comparison",
            "evidence": "Goal4501 / V3 M105 plus Goal4502 / V3 M106",
            "contract": "same input, different output surfaces: author full K-id buffer vs RTDL aggregate",
            "dataset": "same Goal4500 bounded KITTI-1M CSV",
            "primary_measure": (
                f"author total-search {_fmt(_seconds(author['median_total_search_sec']))}; "
                f"author pure compute {_fmt(_seconds(author['median_search_compute_sec']))}; "
                f"author cold process {_fmt(_seconds(author['median_process_elapsed_sec']))}; "
                f"RTDL aggregate hot {_fmt(_seconds(m106_best['median_query_sec']))}"
            ),
            "reading": (
                "RTDL's aggregate query is faster than the author synchronized total-search timer "
                "for this aggregate surface, while the author remains much faster in pure compute "
                "and cold whole-process timing."
            ),
            "boundary": "Useful diagnostic, not an RTDL-beats-author same-output claim.",
        },
        {
            "lane": "Partner-continuation chunked runtime",
            "evidence": "Goal4505 / V3 M109 through Goal4507 / V3 M111",
            "contract": "prepared graph plus same-stream CuPy/Numba device reductions over 16 explicit chunks",
            "dataset": "current synthetic M19 uniform, shell, and clustered 1,048,576-query family",
            "primary_measure": (
                "uniform CuPy 0.082908s / Numba 0.083390s; "
                "shell CuPy 0.609413s / Numba 0.609404s; "
                "clustered CuPy 2.041410s / Numba 2.036964s"
            ),
            "reading": (
                "Large partner continuation now has real runtime evidence for both partners, "
                "with signatures matching and materialization outside the hot window."
            ),
            "boundary": (
                "Partner-continuation evidence only; not an aggregate-only full-batch direct comparison "
                "and not a paper dataset substitute."
            ),
        },
    )

    readiness = {
        "internal_clean_target_closed": True,
        "same_input_rtdl_optix_embree_gate_ready": bool(m104["summary"]["live_rtdl_pair_ready"]),
        "current_aggregate_route_selected": bool(m106["claim_boundary"]["rtdl_best_is_hot_prepared_aggregate"]),
        "point_file_app_front_door_ready": bool(m107["claim_boundary"]["external_point_file_front_door_proven"]),
        "author_same_input_diagnostic_ready": bool(m106["claim_boundary"]["same_input_author_rtdl_comparison"]),
        "dual_partner_chunked_runtime_ready": bool(m111["matrix_summary"]["all_signature_match"])
        and bool(m111["matrix_summary"]["all_hot_no_hidden_column_copy_ready"]),
        "official_paper_dataset_reproduction_ready": False,
        "same_output_author_comparison_ready": False,
        "public_rt_core_speedup_claim_ready": False,
    }

    chunk_matrix = tuple(
        {
            "distribution": row["distribution"],
            "chunk_count": row["chunk_count"],
            "cupy_hot_device_run_seconds_median_sum": row["cupy_hot_device_run_seconds_median_sum"],
            "numba_hot_device_run_seconds_median_sum": row["numba_hot_device_run_seconds_median_sum"],
            "signature_match": row["signature_match"],
            "hot_no_hidden_column_copy_ready": row["hot_no_hidden_column_copy_ready"],
        }
        for row in chunk_rows
    )

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4508 / V3 M112",
        "status": "rtnn_clean_target_internally_closed_with_public_claim_gates",
        "source_packets": tuple(
            path.as_posix() for path in (M104_PACKET, M106_PACKET, M107_PACKET, M111_PACKET)
        ),
        "input_contract": m106["input_contract"],
        "contract_rows": contract_rows,
        "chunked_partner_matrix": chunk_matrix,
        "readiness": readiness,
        "implementation_strategy": {
            "native_engine_contract": (
                "generic prepared fixed-radius 3-D ranked-summary primitives; no RTNN-specific native ABI"
            ),
            "aggregate_only_choice": (
                "use the full-batch prepared direct aggregate route when the app needs only the final ranked summary"
            ),
            "partner_continuation_choice": (
                "use the explicit prepared graph chunk plan when the app needs same-stream device partials "
                "for CuPy or Numba continuation"
            ),
            "cpu_choice": (
                "use Embree as the same-contract CPU fallback/proof route, not as the primary RT-core target"
            ),
            "author_comparison_choice": (
                "compare author RTNN as a diagnostic baseline only until same-output full K-id materialization "
                "or an agreed aggregate-output contract is implemented on both sides"
            ),
        },
        "remaining_debt": (
            "freeze/acquire exact RTNN paper datasets and frame/scan recipes",
            "keep author-code comparison contract-explicit or add a same-output full K-id RTDL route if needed",
            "lift the M19 chunked graph/partner pattern into an app-agnostic prepared graph chunk executor",
            "do not publish RT-core speedup or RTDL-beats-author wording from this closeout alone",
        ),
        "next_v3_target": (
            "abstract the M19 chunked partner runtime into a reusable prepared graph chunk executor, "
            "then use the same audit style on RT-DBSCAN and Triangle Counting."
        ),
        "conclusion": (
            "RTNN is internally closed as a V3 clean target: RTDL has a same-input OptiX/Embree gate, "
            "a current full-batch aggregate-only OptiX route, an app front door for external point files, "
            "a same-input author-code diagnostic comparison, and measured CuPy plus Numba chunked "
            "partner-continuation runtime at 1,048,576 queries. The closeout is intentionally not a "
            "public RTNN paper-reproduction or RTDL-beats-author claim."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4508 / V3 M112 RTNN Clean-Target Closeout",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Closeout Matrix",
        "",
        "| Lane | Evidence | Primary measure | Reading | Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["contract_rows"]:
        lines.append(
            "| {lane} | {evidence} | {measure} | {reading} | {boundary} |".format(
                lane=row["lane"],
                evidence=row["evidence"],
                measure=row["primary_measure"],
                reading=row["reading"],
                boundary=row["boundary"],
            )
        )
    lines.extend(
        [
            "",
            "## Partner Matrix",
            "",
            "| Distribution | Chunks | CuPy hot median-sum | Numba hot median-sum | Signature | No hidden copy |",
            "| --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in packet["chunked_partner_matrix"]:
        lines.append(
            "| {distribution} | {chunk_count} | {cupy} | {numba} | `{signature}` | `{copy}` |".format(
                distribution=row["distribution"],
                chunk_count=row["chunk_count"],
                cupy=_fmt(_seconds(row["cupy_hot_device_run_seconds_median_sum"])),
                numba=_fmt(_seconds(row["numba_hot_device_run_seconds_median_sum"])),
                signature=row["signature_match"],
                copy=row["hot_no_hidden_column_copy_ready"],
            )
        )
    lines.extend(
        [
            "",
            "## What Closed",
            "",
            "- RTDL OptiX and Embree now have a same-input same-contract RTNN-shaped gate on the bounded KITTI-1M CSV.",
            "- The current RTDL aggregate-only route is the full-batch prepared direct aggregate, not the capped graph path.",
            "- The RTNN benchmark app can run the real point-file front door into that current route.",
            "- Author RTNN has a same-input diagnostic row, with output-contract caveats stated inline.",
            "- Partner continuation has large 1,048,576-query runtime evidence for both CuPy and Numba.",
            "",
            "## Still Blocked",
            "",
            "- Exact RTNN paper reproduction is blocked until the official dataset recipes are frozen or acquired.",
            "- Same-output author comparison is blocked because author RTNN materializes a full K-id buffer while RTDL's best route returns ranked-summary aggregates.",
            "- Public RT-core speedup, whole-app speedup, automatic partner selection, and RTDL-beats-author wording remain blocked.",
            "",
            "## Next Step",
            "",
            packet["next_v3_target"],
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
