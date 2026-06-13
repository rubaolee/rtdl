from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .current_benchmark_scale_profiles import (
    CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
    current_benchmark_scale_profiles,
)
from .current_embree_cpu_partner_reference import (
    CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
    current_embree_cpu_partner_reference_rows,
)
from .embree_same_contract_scale_probe import embree_same_contract_scale_probe
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


GOAL4341_OPTIMIZED_OPTIX_EMBREE_COMPARISON_PACKET_VERSION = (
    "rtdl.v2_12.optimized_optix_embree_comparison_packet.goal4361.v1"
)
GOAL4341_STATUS = "internal_optimized_embree_vs_optix_comparison_packet_not_public_speedup_authorization"
GOAL4341_CLAIM_BOUNDARY = (
    "Goal4361 extends the Goal4360 optimized/same-scale Embree-vs-OptiX packet "
    "with the RT-DBSCAN OptiX RT-core count-threshold plus Numba column-signature "
    "same-contract pair. It separates clean same-contract query-ratio rows, "
    "RayJoin same-stream scalar-count rows, RTNN raw-row backend rows, "
    "RT-DBSCAN configured-route rows, boundary-limited same-scale rows, and "
    "the remaining contract-split/configured route. This "
    "packet does not authorize release action, public speedup wording, "
    "whole-app acceleration wording, broad RT-core wording, paper reproduction "
    "wording, true-zero-copy wording, automatic partner selection, or "
    "app-specific native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GOAL4340_SAME_SCALE_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal4340_embree_optix_same_scale_comparison_2026-06-11.json"
)
DEFAULT_GOAL4340_EMBREE_SUMMARY = (
    ROOT / "docs" / "reports" / "goal4340_embree_native_aabb_index_local_linux" / "summary.json"
)
DEFAULT_GOAL4339_PRE_OPTIMIZATION_SUMMARY = (
    ROOT / "docs" / "reports" / "goal4339_librts_skip_counts_local_linux" / "summary.json"
)
DEFAULT_OPTIX_SCALE_SUMMARY = ROOT / "docs" / "reports" / "goal4329_current_pod_validation" / "scale_summary_allpass.json"
DEFAULT_RAYJOIN_SAME_STREAM_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
    / "summary.json"
)
DEFAULT_RTNN_SAME_CONTRACT_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4360_rtx_a4000_v2_12_rtnn_same_contract_2026-06-13"
    / "summary.json"
)
DEFAULT_RT_DBSCAN_SAME_CONTRACT_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4361_rtx_a4000_v2_12_rt_dbscan_same_contract_2026-06-13"
    / "summary.json"
)


APP_COMPARISON_PLAN: dict[str, dict[str, str]] = {
    "hausdorff_xhd": {
        "goal4341_status": "internal_query_ratio_candidate_ready",
        "reason": (
            "Goal4344 supplies the Embree prepared threshold-decision row at the "
            "same copies, threshold, repeat, and warmup as the current OptiX scale row."
        ),
        "next_action": (
            "use query-phase ratio internally only; keep exact-distance and public "
            "speedup wording outside this packet"
        ),
    },
    "spatial_rayjoin": {
        "goal4341_status": "same_stream_scalar_count_pairs_available",
        "reason": (
            "Goal4358 supplies RayJoin-exported same-stream LSI and PIP scalar-count "
            "pairs for RTDL OptiX and RTDL Embree. The broad current registry row "
            "remains mixed, so these ratios are scoped to split scalar-count contracts."
        ),
        "next_action": (
            "use the same-stream LSI/PIP scalar-count rows internally; keep overlay "
            "active-count and whole-app wording separate"
        ),
    },
    "rt_dbscan": {
        "goal4341_status": "same_contract_configured_numba_route_available",
        "reason": (
            "Goal4361 supplies a same-scale/same-seed clustered3d 65,536-point "
            "configured-route pair: OptiX RT-core count-threshold flags plus "
            "Numba prepared-grid column signature versus Embree threshold-capped "
            "rows plus the same Numba continuation."
        ),
        "next_action": (
            "use this configured-route ratio internally only; keep public whole-app "
            "and paper-speedup wording blocked"
        ),
    },
    "robot_collision": {
        "goal4341_status": "same_scale_boundary_limited",
        "reason": (
            "Goal4344 supplies the Embree row at the same scene/query scale as "
            "OptiX, but the OptiX scale row uses the OptiX-only device-count path "
            "while Embree returns host compact flags."
        ),
        "next_action": (
            "show traversal-only internal phase comparison, or run an OptiX "
            "prepared-buffer flags row before reporting a clean output-contract ratio"
        ),
    },
    "contact_manifold": {
        "goal4341_status": "internal_query_ratio_candidate_ready",
        "reason": (
            "Goal4344 supplies the Embree native collect-k row at the same grid "
            "size, witness capacity, repeat count, and correctness policy as OptiX."
        ),
        "next_action": (
            "use native collect-k median internally only; keep public claims blocked"
        ),
    },
    "raydb_style": {
        "goal4341_status": "same_scale_boundary_limited",
        "reason": (
            "Goal4344 supplies the Embree generated 262144-row / 1024-group count "
            "row, but the current OptiX scale row is prepared/resident while the "
            "Embree row is a non-resident native grouped-reduction run."
        ),
        "next_action": (
            "show traversal/native-call phases as boundary-limited internal evidence; "
            "add prepared Embree residency before clean end-to-end ratios"
        ),
    },
    "barnes_hut": {
        "goal4341_status": "contract_split_pair_required",
        "reason": (
            "Current OptiX scale evidence is a Numba exact-force partner route; "
            "current Embree evidence is a prepared node-coverage route."
        ),
        "next_action": (
            "choose exact-force partner continuation or prepared node coverage as the "
            "comparison contract, then run that contract on both sides"
        ),
    },
    "librts_spatial_index": {
        "goal4341_status": "measured_same_contract_optimized_pair",
        "reason": (
            "Goal4340 supplies a fresh same-scale AABB_INDEX_QUERY_2D prepared-query "
            "row after replacing the old Embree columnar fallback with a native "
            "Embree collision route."
        ),
        "next_action": (
            "scale the same prepared-query row to larger box/query counts and report "
            "scene-prepare amortization separately from query median"
        ),
    },
    "rtnn": {
        "goal4341_status": "same_contract_raw_rows_available_not_rt_core_proof",
        "reason": (
            "Goal4360 supplies a same-scale/same-seed prepared 3-D fixed-radius "
            "bounded ranked-summary raw-row pair for OptiX and Embree, with "
            "matching aggregate row signatures."
        ),
        "next_action": (
            "use this as an internal backend row only; keep RT-core wording blocked "
            "because the current OptiX RTNN phase is the prepared uniform-cell "
            "ranked-summary implementation"
        ),
    },
    "triangle_counting": {
        "goal4341_status": "internal_query_ratio_candidate_ready",
        "reason": (
            "Goal4344 supplies the Embree RT-Graph 2A1 row at the same fixture, "
            "copy count, detail mode, repeat, and warmup as the OptiX scale row."
        ),
        "next_action": (
            "use query-median ratio internally only; keep public claims blocked"
        ),
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _required_float(payload: dict[str, Any], *keys: str) -> float:
    node: Any = payload
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            raise KeyError("missing numeric field: " + ".".join(keys))
        node = node[key]
    return float(node)


def _registry_rows() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    optix = {row["app"]: row for row in current_benchmark_scale_profiles()}
    embree = {row["app"]: row for row in current_embree_cpu_partner_reference_rows()}
    return optix, embree


def _scale_summary_rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return {}
    return {str(row.get("app")): row for row in rows if isinstance(row, dict) and row.get("app")}


def _load_optix_stdout(scale_summary: dict[str, Any], app: str) -> tuple[dict[str, Any], str]:
    row = _scale_summary_rows(scale_summary)[app]
    stdout_path = str(row["stdout_path"])
    payload = _load_json(ROOT / stdout_path)
    return payload, stdout_path


def _load_embree_probe_payload(probe_payload: dict[str, Any], app: str) -> tuple[dict[str, Any], dict[str, Any]]:
    row = {str(item["app"]): item for item in probe_payload["rows"]}[app]
    return _load_json(ROOT / str(row["artifact_path"])), row


def _ratio_row(
    *,
    app: str,
    contract: str,
    metric_name: str,
    metric_unit: str,
    embree_metric: float,
    optix_metric: float,
    ratio_authorization: str,
    optix_source: str,
    embree_source: str,
    correctness: dict[str, Any],
    boundary: str,
    comparison_table: str = "pure_rtdl_primitive",
) -> dict[str, Any]:
    ratio = embree_metric / optix_metric if optix_metric else float("inf")
    faster_backend = "optix" if ratio > 1.0 else ("embree" if ratio < 1.0 else "tie")
    return {
        "app": app,
        "comparison_table": comparison_table,
        "contract": contract,
        "metric_name": metric_name,
        "metric_unit": metric_unit,
        "embree_metric": embree_metric,
        "optix_metric": optix_metric,
        "embree_metric_divided_by_optix_metric": ratio,
        "faster_backend_for_metric": faster_backend,
        "ratio_authorization": ratio_authorization,
        "optix_source": optix_source,
        "embree_source": embree_source,
        "correctness": correctness,
        "boundary": boundary,
        "public_speedup_claim_authorized": False,
        "release_authorized": False,
    }


def _hausdorff_comparison_row(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> dict[str, Any]:
    optix, optix_source = _load_optix_stdout(scale_summary, "hausdorff_xhd")
    embree, embree_row = _load_embree_probe_payload(probe_payload, "hausdorff_xhd")
    optix_metric = max(
        _required_float(optix, "directed_a_to_b", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
        _required_float(optix, "directed_b_to_a", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
    )
    embree_metric = max(
        _required_float(embree, "directed_a_to_b", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
        _required_float(embree, "directed_b_to_a", "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
    )
    return _ratio_row(
        app="hausdorff_xhd",
        contract="directed_threshold_prepared_fixed_radius_count",
        metric_name="max_directed_query_fixed_radius_threshold_reached_count_sec",
        metric_unit="sec",
        embree_metric=embree_metric,
        optix_metric=optix_metric,
        ratio_authorization="internal_query_phase_ratio_only_not_public_claim",
        optix_source=optix_source,
        embree_source=str(embree_row["artifact_path"]),
        correctness={
            "optix_matches_oracle": bool(optix.get("matches_oracle")),
            "embree_matches_oracle": bool(embree.get("matches_oracle")),
            "optix_oracle_decision_matches": bool(optix.get("oracle_decision_matches")),
            "embree_oracle_decision_matches": bool(embree.get("oracle_decision_matches")),
        },
        boundary=str(embree_row["boundary"]),
    )


def _contact_comparison_row(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> dict[str, Any]:
    optix, optix_source = _load_optix_stdout(scale_summary, "contact_manifold")
    embree, embree_row = _load_embree_probe_payload(probe_payload, "contact_manifold")
    return _ratio_row(
        app="contact_manifold",
        contract="native_collect_k_bounded_witness_rows",
        metric_name="native_collect_elapsed_sec",
        metric_unit="sec",
        embree_metric=_required_float(embree, "native_collect_elapsed_sec"),
        optix_metric=_required_float(optix, "native_collect_elapsed_sec"),
        ratio_authorization="internal_query_phase_ratio_only_not_public_claim",
        optix_source=optix_source,
        embree_source=str(embree_row["artifact_path"]),
        correctness={
            "optix_matches_cpu_reference": bool(optix.get("matches_cpu_reference")),
            "embree_matches_cpu_reference": bool(embree.get("matches_cpu_reference")),
            "optix_complete_candidate_coverage": bool(optix.get("complete_candidate_coverage")),
            "embree_complete_candidate_coverage": bool(embree.get("complete_candidate_coverage")),
        },
        boundary=str(embree_row["boundary"]),
    )


def _triangle_comparison_row(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> dict[str, Any]:
    optix, optix_source = _load_optix_stdout(scale_summary, "triangle_counting")
    embree, embree_row = _load_embree_probe_payload(probe_payload, "triangle_counting")
    return _ratio_row(
        app="triangle_counting",
        contract="rt_graph_2a1_generic_ray_triangle_any_hit",
        metric_name="query_median_ms",
        metric_unit="ms",
        embree_metric=_required_float(embree, "timing_ms", "query_median_ms"),
        optix_metric=_required_float(optix, "timing_ms", "query_median_ms"),
        ratio_authorization="internal_query_phase_ratio_only_not_public_claim",
        optix_source=optix_source,
        embree_source=str(embree_row["artifact_path"]),
        correctness={
            "optix_triangle_count_matches_oracle": bool(optix.get("triangle_count_matches_oracle")),
            "embree_triangle_count_matches_oracle": bool(embree.get("triangle_count_matches_oracle")),
            "optix_weighted_count": int(optix.get("generic_rt_weighted_triangle_count", -1)),
            "embree_weighted_count": int(embree.get("generic_rt_weighted_triangle_count", -2)),
        },
        boundary=str(embree_row["boundary"]),
    )


def _robot_boundary_row(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> dict[str, Any]:
    optix, optix_source = _load_optix_stdout(scale_summary, "robot_collision")
    embree, embree_row = _load_embree_probe_payload(probe_payload, "robot_collision")
    return _ratio_row(
        app="robot_collision",
        comparison_table="pure_rtdl_primitive_boundary_limited",
        contract="prepared_triangle_scene_grouped_segment_any_hit_same_scene_query_scale",
        metric_name="traversal_phase_median_sec",
        metric_unit="sec",
        embree_metric=_required_float(embree, "tail_medians", "phase_timing_seconds", "traversal"),
        optix_metric=_required_float(optix, "tail_medians", "phase_timing_seconds", "traversal"),
        ratio_authorization="boundary_limited_traversal_phase_only_no_end_to_end_ratio",
        optix_source=optix_source,
        embree_source=str(embree_row["artifact_path"]),
        correctness={
            "same_case_shape": embree.get("case_shape") == optix.get("case_shape"),
            "optix_probe_reference_validated": bool(_dig_optional(optix, "reuse_metadata", "probe_reference_validated")),
            "embree_probe_reference_validated": bool(_dig_optional(embree, "reuse_metadata", "probe_reference_validated")),
            "both_use_current_no_probe_reference_scale_policy": True,
        },
        boundary=str(embree_row["boundary"]),
    )


def _raydb_boundary_row(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> dict[str, Any]:
    optix, optix_source = _load_optix_stdout(scale_summary, "raydb_style")
    embree, embree_row = _load_embree_probe_payload(probe_payload, "raydb_style")
    return _ratio_row(
        app="raydb_style",
        comparison_table="pure_rtdl_primitive_boundary_limited",
        contract="generated_grouped_count_same_rows_groups_boundary_limited_residency",
        metric_name="native_rt_traversal_sec",
        metric_unit="sec",
        embree_metric=_required_float(embree, "metadata", "timings", "traversal"),
        optix_metric=_required_float(optix, "metadata", "timings", "traversal"),
        ratio_authorization="boundary_limited_traversal_phase_only_no_end_to_end_ratio",
        optix_source=optix_source,
        embree_source=str(embree_row["artifact_path"]),
        correctness={
            "optix_matches_cpu_reference": bool(optix.get("matches_cpu_reference")),
            "embree_matches_cpu_reference": bool(embree.get("matches_cpu_reference")),
            "same_row_count": int(optix.get("row_count", -1)) == int(embree.get("row_count", -2)),
        },
        boundary=str(embree_row["boundary"]),
    )


def _dig_optional(payload: dict[str, Any], *keys: str) -> Any:
    node: Any = payload
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _scale_comparison_rows(scale_summary: dict[str, Any], probe_payload: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return (
        _hausdorff_comparison_row(scale_summary, probe_payload),
        _robot_boundary_row(scale_summary, probe_payload),
        _contact_comparison_row(scale_summary, probe_payload),
        _raydb_boundary_row(scale_summary, probe_payload),
        _triangle_comparison_row(scale_summary, probe_payload),
    )


def _rayjoin_same_stream_comparison_rows(
    payload: dict[str, Any],
    *,
    source_path: Path,
) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    rtdl = payload.get("rtdl")
    if not isinstance(rtdl, dict):
        return ()
    for workload in ("lsi", "pip"):
        workload_payload = rtdl.get(workload)
        if not isinstance(workload_payload, dict):
            continue
        backends = workload_payload.get("backends")
        if not isinstance(backends, dict):
            continue
        optix = backends.get("optix")
        embree = backends.get("embree")
        if not isinstance(optix, dict) or not isinstance(embree, dict):
            continue
        optix_ms = float(optix["hot_median_sec"]) * 1000.0
        embree_ms = float(embree["hot_median_sec"]) * 1000.0
        rows.append(
            _ratio_row(
                app="spatial_rayjoin",
                comparison_table="rayjoin_same_stream_scalar_count",
                contract=f"{workload}_same_stream_scalar_count",
                metric_name="hot_query_median_ms",
                metric_unit="ms",
                embree_metric=embree_ms,
                optix_metric=optix_ms,
                ratio_authorization="internal_same_stream_scalar_count_only_not_public_claim",
                optix_source=_relative(source_path),
                embree_source=_relative(source_path),
                correctness={
                    "workload": workload,
                    "optix_row_count": int(optix["row_count"]),
                    "embree_row_count": int(embree["row_count"]),
                    "cross_backend_count_match": int(optix["row_count"]) == int(embree["row_count"]),
                    "row_stream_materialized": bool(optix.get("row_stream_materialized"))
                    or bool(embree.get("row_stream_materialized")),
                },
                boundary=(
                    "Same RayJoin-exported query stream, scalar-count hot query "
                    "phase only, no RTDL row materialization, and no whole-app or "
                    "RayJoin-paper reproduction claim."
                ),
            )
        )
        rows[-1]["workload"] = workload
    return tuple(rows)


def _rtnn_same_contract_backend_comparison_rows(
    payload: dict[str, Any],
    *,
    source_path: Path,
) -> tuple[dict[str, Any], ...]:
    rows_payload = payload.get("rows")
    comparison = payload.get("comparison")
    if not isinstance(rows_payload, dict) or not isinstance(comparison, dict):
        return ()
    optix = rows_payload.get("optix")
    embree = rows_payload.get("embree")
    if not isinstance(optix, dict) or not isinstance(embree, dict):
        return ()
    optix_aggregate = optix.get("raw_ranked_summary_aggregate")
    embree_aggregate = embree.get("raw_ranked_summary_aggregate")
    if not isinstance(optix_aggregate, dict) or not isinstance(embree_aggregate, dict):
        return ()
    row = _ratio_row(
        app="rtnn",
        comparison_table="rtnn_same_contract_raw_ranked_summary",
        contract=str(payload["contract"]),
        metric_name="query_median_sec",
        metric_unit="sec",
        embree_metric=float(embree["query_median_sec"]),
        optix_metric=float(optix["query_median_sec"]),
        ratio_authorization="internal_same_contract_raw_row_query_only_not_public_rt_core_claim",
        optix_source=_relative(source_path),
        embree_source=_relative(source_path),
        correctness={
            "optix_ok": bool(optix["ok"]),
            "embree_ok": bool(embree["ok"]),
            "optix_row_count": int(optix["row_count"]),
            "embree_row_count": int(embree["row_count"]),
            "row_count_match": int(optix["row_count"]) == int(embree["row_count"]),
            "integer_signature_match": bool(comparison["integer_signature_match"]),
            "sum_distance_delta": float(comparison["sum_distance_delta"]),
            "sum_distance_match_exact": bool(comparison["sum_distance_match_exact"]),
            "bounded_neighbor_count": int(optix_aggregate["bounded_neighbor_count"]),
            "nearest_id_checksum": int(optix_aggregate["nearest_id_checksum"]),
            "kth_id_checksum": int(optix_aggregate["kth_id_checksum"]),
            "rt_core_neighbor_search_claim_authorized": bool(
                comparison["rt_core_neighbor_search_claim_authorized"]
            ),
        },
        boundary=(
            "Same seed, point count, radius, k, repeat, query-batch size, and "
            "prepared 3-D fixed-radius ranked-summary raw-row output contract. "
            "Internal backend query-median row only; no RT-core claim because "
            "the current OptiX phase is reported as prepared uniform-cell "
            "ranked-summary rows."
        ),
    )
    row["rt_core_neighbor_search_claim_authorized"] = bool(
        comparison["rt_core_neighbor_search_claim_authorized"]
    )
    return (row,)


def _rt_dbscan_same_contract_backend_comparison_rows(
    payload: dict[str, Any],
    *,
    source_path: Path,
) -> tuple[dict[str, Any], ...]:
    rows_payload = payload.get("rows")
    comparison = payload.get("comparison")
    if not isinstance(rows_payload, dict) or not isinstance(comparison, dict):
        return ()
    optix = rows_payload.get("optix")
    embree = rows_payload.get("embree")
    if not isinstance(optix, dict) or not isinstance(embree, dict):
        return ()
    optix_phase = dict(optix["phase_median_sec"])
    embree_phase = dict(embree["phase_median_sec"])
    row = _ratio_row(
        app="rt_dbscan",
        comparison_table="rt_dbscan_same_contract_configured_numba_column_signature",
        contract=str(payload["contract"]),
        metric_name="elapsed_median_sec",
        metric_unit="sec",
        embree_metric=float(embree["elapsed_median_sec"]),
        optix_metric=float(optix["elapsed_median_sec"]),
        ratio_authorization="internal_same_contract_configured_numba_route_only_not_public_claim",
        optix_source=_relative(source_path),
        embree_source=_relative(source_path),
        correctness={
            "signature_match": bool(comparison["signature_match"]),
            "same_numba_continuation": bool(comparison["same_numba_continuation"]),
            "same_output_contract": bool(comparison["same_output_contract"]),
            "same_dataset_radius_min_neighbors_seed_repeat_warmup": bool(
                comparison["same_dataset_radius_min_neighbors_seed_repeat_warmup"]
            ),
            "optix_rt_core_accelerated": bool(optix["rt_core_accelerated"]),
            "embree_rt_core_accelerated": bool(embree["rt_core_accelerated"]),
            "optix_threshold_sec": float(optix_phase["optix_rt_count_threshold_sec"]),
            "embree_threshold_sec": float(embree_phase["embree_threshold_capped_rows_sec"]),
            "threshold_phase_ratio": float(
                comparison["embree_threshold_phase_divided_by_optix_threshold_phase"]
            ),
        },
        boundary=(
            "Same clustered3d point count, radius, min-neighbor threshold, seed, "
            "repeat/warmup, output component-size signature, and Numba prepared-grid "
            "continuation. Internal configured-route backend ratio only; no public "
            "whole-app or paper reproduction speedup claim."
        ),
    )
    row["rt_core_threshold_phase_claim_authorized_internal"] = bool(
        comparison["rt_core_threshold_phase_claim_authorized_internal"]
    )
    return (row,)


def _librts_measured_pair(
    *,
    same_scale: dict[str, Any],
    embree_summary: dict[str, Any],
    pre_optimization_summary: dict[str, Any],
) -> dict[str, Any]:
    embree_query_sec = _required_float(same_scale, "embree", "query_median_sec")
    optix_query_sec = _required_float(same_scale, "optix", "query_median_sec")
    old_embree_query_sec = _required_float(
        pre_optimization_summary,
        "embree_1024_skip_counts",
        "query_median_sec",
    )
    optimized_speedup_vs_old = old_embree_query_sec / embree_query_sec
    optix_faster_than_embree = embree_query_sec / optix_query_sec
    return {
        "app": "librts_spatial_index",
        "contract": "generic_prepared_aabb_index_query_2d",
        "row": same_scale["row"],
        "scale": {
            "box_count": 1024,
            "query_count": 1024,
            "operation": "all",
            "repeat": 2,
            "warmup": 1,
            "cpu_reference_skipped": True,
        },
        "embree_cpu_optimized": {
            "backend": same_scale["embree"]["backend"],
            "host": same_scale["embree"]["host"],
            "native_index": same_scale["embree"]["native_index"],
            "query_median_sec": embree_query_sec,
            "elapsed_sec": _required_float(same_scale, "embree", "elapsed_sec"),
            "rt_core_accelerated": bool(same_scale["embree"]["rt_core_accelerated"]),
        },
        "optix_rt": {
            "backend": same_scale["optix"]["backend"],
            "host": same_scale["optix"]["host"],
            "native_index": same_scale["optix"]["native_index"],
            "query_median_sec": optix_query_sec,
            "elapsed_sec": _required_float(same_scale, "optix", "elapsed_sec"),
            "scene_prepare_sec": _required_float(same_scale, "optix", "scene_prepare_sec"),
            "rt_core_accelerated": bool(same_scale["optix"]["rt_core_accelerated"]),
        },
        "pre_goal4340_embree_fallback": {
            "native_index": "embree_generic_columnar_payload",
            "query_median_sec": old_embree_query_sec,
            "source": _relative(DEFAULT_GOAL4339_PRE_OPTIMIZATION_SUMMARY),
        },
        "goal4340_embree_validation": {
            "small_validated_matches_cpu_reference": bool(
                embree_summary["small_validated"]["matches_cpu_reference"]
            ),
            "large_native_index": embree_summary["large_1024_skip_counts"]["native_index"],
            "query_median_speedup_vs_columnar_fallback": _required_float(
                embree_summary,
                "query_median_speedup_vs_columnar_fallback",
            ),
        },
        "optimized_embree_query_median_speedup_vs_old_columnar_fallback": optimized_speedup_vs_old,
        "optix_query_median_faster_than_optimized_embree": optix_faster_than_embree,
        "query_median_ratio_authorized_for_internal_packet": True,
        "elapsed_total_ratio_authorized": False,
        "public_speedup_claim_authorized": False,
        "release_authorized": False,
        "boundary": (
            "Same app runner, same 1024x1024 AABB query shape, and same operation "
            "policy. Query median is the comparable prepared-query phase. Elapsed "
            "totals are not a clean backend ratio because scene preparation and "
            "hardware differ."
        ),
    }


def _planning_rows(measured_pair: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    optix_registry, embree_registry = _registry_rows()
    rows: list[dict[str, Any]] = []
    for app in V2_8_PROMOTED_BENCHMARK_APPS:
        plan = APP_COMPARISON_PLAN[app]
        optix = optix_registry[app]
        embree = embree_registry[app]
        row = {
            "app": app,
            "optix_registry": {
                "version": CURRENT_BENCHMARK_SCALE_PROFILE_VERSION,
                "row_id": optix["row_id"],
                "purpose": optix["purpose"],
            },
            "embree_cpu_registry": {
                "version": CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION,
                "row_id": embree["row_id"],
                "route_class": embree["route_class"],
                "purpose": embree["purpose"],
            },
            "goal4341_status": plan["goal4341_status"],
            "evidence_or_reason": plan["reason"],
            "next_action": plan["next_action"],
            "query_median_ratio_authorized_for_internal_packet": plan["goal4341_status"]
            in {
                "internal_query_ratio_candidate_ready",
                "measured_same_contract_optimized_pair",
                "same_stream_scalar_count_pairs_available",
                "same_contract_raw_rows_available_not_rt_core_proof",
                "same_contract_configured_numba_route_available",
            },
            "boundary_limited_phase_ratio_only": plan["goal4341_status"] == "same_scale_boundary_limited",
            "public_speedup_claim_authorized": False,
            "release_authorized": False,
        }
        if app == "librts_spatial_index":
            row["measured_pair_row"] = measured_pair["row"]
            row["query_median_ratio_authorized_for_internal_packet"] = True
            row["optix_query_median_faster_than_optimized_embree"] = measured_pair[
                "optix_query_median_faster_than_optimized_embree"
            ]
        rows.append(row)
    return tuple(rows)


def optimized_optix_embree_comparison_packet(
    *,
    same_scale_artifact_path: Path | None = None,
    embree_summary_path: Path | None = None,
    pre_optimization_summary_path: Path | None = None,
    optix_scale_summary_path: Path | None = None,
    rayjoin_same_stream_artifact_path: Path | None = None,
    rtnn_same_contract_artifact_path: Path | None = None,
    rt_dbscan_same_contract_artifact_path: Path | None = None,
) -> dict[str, Any]:
    same_scale_path = same_scale_artifact_path or DEFAULT_GOAL4340_SAME_SCALE_ARTIFACT
    embree_summary_path = embree_summary_path or DEFAULT_GOAL4340_EMBREE_SUMMARY
    pre_optimization_path = pre_optimization_summary_path or DEFAULT_GOAL4339_PRE_OPTIMIZATION_SUMMARY
    optix_scale_path = optix_scale_summary_path or DEFAULT_OPTIX_SCALE_SUMMARY
    rayjoin_path = rayjoin_same_stream_artifact_path or DEFAULT_RAYJOIN_SAME_STREAM_ARTIFACT
    rtnn_path = rtnn_same_contract_artifact_path or DEFAULT_RTNN_SAME_CONTRACT_ARTIFACT
    rt_dbscan_path = rt_dbscan_same_contract_artifact_path or DEFAULT_RT_DBSCAN_SAME_CONTRACT_ARTIFACT
    same_scale = _load_json(same_scale_path)
    embree_summary = _load_json(embree_summary_path)
    pre_optimization_summary = _load_json(pre_optimization_path)
    optix_scale_summary = _load_json(optix_scale_path)
    rayjoin_same_stream = _load_json(rayjoin_path)
    rtnn_same_contract = _load_json(rtnn_path)
    rt_dbscan_same_contract = _load_json(rt_dbscan_path)
    embree_probe = embree_same_contract_scale_probe()

    measured_pair = _librts_measured_pair(
        same_scale=same_scale,
        embree_summary=embree_summary,
        pre_optimization_summary=pre_optimization_summary,
    )
    scale_comparison_rows = _scale_comparison_rows(optix_scale_summary, embree_probe)
    same_stream_comparison_rows = _rayjoin_same_stream_comparison_rows(
        rayjoin_same_stream,
        source_path=rayjoin_path,
    )
    same_contract_backend_comparison_rows = _rtnn_same_contract_backend_comparison_rows(
        rtnn_same_contract,
        source_path=rtnn_path,
    ) + _rt_dbscan_same_contract_backend_comparison_rows(
        rt_dbscan_same_contract,
        source_path=rt_dbscan_path,
    )
    planning_rows = _planning_rows(measured_pair)

    errors: list[str] = []
    if len(planning_rows) != len(V2_8_PROMOTED_BENCHMARK_APPS):
        errors.append("planning row count does not match promoted benchmark app count")
    if measured_pair["embree_cpu_optimized"]["native_index"] != "embree_native_aabb_collision_index":
        errors.append("LibRTS measured pair is not using optimized native Embree AABB index")
    if measured_pair["optix_rt"]["native_index"] != "optix_prepared_aabb_index":
        errors.append("LibRTS measured pair is not using prepared OptiX AABB index")
    if measured_pair["optimized_embree_query_median_speedup_vs_old_columnar_fallback"] < 1000.0:
        errors.append("optimized Embree improvement versus old fallback is unexpectedly small")
    if measured_pair["optix_query_median_faster_than_optimized_embree"] <= 1.0:
        errors.append("OptiX query median is not faster than optimized Embree in the paired row")
    if not measured_pair["goal4340_embree_validation"]["small_validated_matches_cpu_reference"]:
        errors.append("Goal4340 small Embree validation row did not match CPU reference")
    internal_ratio_rows = [
        row for row in planning_rows if row["query_median_ratio_authorized_for_internal_packet"]
    ]
    expected_internal_ratio_apps = {
        "hausdorff_xhd",
        "rt_dbscan",
        "spatial_rayjoin",
        "contact_manifold",
        "librts_spatial_index",
        "rtnn",
        "triangle_counting",
    }
    if {row["app"] for row in internal_ratio_rows} != expected_internal_ratio_apps:
        errors.append("unexpected internal query-ratio app set in Goal4341")
    boundary_limited_rows = [
        row for row in planning_rows if row["boundary_limited_phase_ratio_only"]
    ]
    if {row["app"] for row in boundary_limited_rows} != {"robot_collision", "raydb_style"}:
        errors.append("unexpected boundary-limited app set in Goal4341")
    if len(same_stream_comparison_rows) != 2:
        errors.append("expected exactly two RayJoin same-stream comparison rows")
    for row in same_stream_comparison_rows:
        if row["app"] != "spatial_rayjoin":
            errors.append("RayJoin same-stream comparison row has wrong app")
        if not bool(row["correctness"]["cross_backend_count_match"]):
            errors.append(f"RayJoin {row.get('workload')}: OptiX and Embree counts differ")
        if bool(row["correctness"]["row_stream_materialized"]):
            errors.append(f"RayJoin {row.get('workload')}: row stream was materialized")
    if len(same_contract_backend_comparison_rows) != 2:
        errors.append("expected exactly two same-contract backend/configured comparison rows")
    for row in same_contract_backend_comparison_rows:
        if row["app"] not in {"rtnn", "rt_dbscan"}:
            errors.append("same-contract backend comparison row has unexpected app")
        correctness = row["correctness"]
        if row["app"] == "rtnn" and (
            not bool(correctness["optix_ok"]) or not bool(correctness["embree_ok"])
        ):
            errors.append("RTNN same-contract row did not pass on both backends")
        if row["app"] == "rtnn" and not bool(correctness["row_count_match"]):
            errors.append("RTNN same-contract row counts differ")
        if row["app"] == "rtnn" and not bool(correctness["integer_signature_match"]):
            errors.append("RTNN same-contract integer signatures differ")
        if row["app"] == "rtnn" and not bool(correctness["sum_distance_match_exact"]):
            errors.append("RTNN same-contract sum_distance differs")
        if row["app"] == "rtnn" and bool(correctness["rt_core_neighbor_search_claim_authorized"]):
            errors.append("RTNN same-contract row unexpectedly authorizes RT-core wording")
        if row["app"] == "rt_dbscan":
            if not bool(correctness["signature_match"]):
                errors.append("RT-DBSCAN same-contract signatures differ")
            if not bool(correctness["same_numba_continuation"]):
                errors.append("RT-DBSCAN row does not hold Numba continuation fixed")
            if not bool(correctness["optix_rt_core_accelerated"]):
                errors.append("RT-DBSCAN OptiX row is not marked RT-core accelerated")
            if bool(correctness["embree_rt_core_accelerated"]):
                errors.append("RT-DBSCAN Embree row is unexpectedly RT-core accelerated")
    for row in scale_comparison_rows:
        if float(row["embree_metric"]) <= 0.0 or float(row["optix_metric"]) <= 0.0:
            errors.append(f"{row['app']}: comparison metric must be positive")
        if row["ratio_authorization"].startswith("internal") and row["app"] not in expected_internal_ratio_apps:
            errors.append(f"{row['app']}: unexpected clean internal ratio authorization")
        if row["ratio_authorization"].startswith("boundary_limited") and row["app"] not in {"robot_collision", "raydb_style"}:
            errors.append(f"{row['app']}: unexpected boundary-limited ratio row")

    return {
        "version": GOAL4341_OPTIMIZED_OPTIX_EMBREE_COMPARISON_PACKET_VERSION,
        "status": GOAL4341_STATUS,
        "claim_boundary": GOAL4341_CLAIM_BOUNDARY,
        "sources": {
            "same_scale_artifact": _relative(same_scale_path),
            "embree_summary": _relative(embree_summary_path),
            "pre_optimization_summary": _relative(pre_optimization_path),
            "optix_scale_summary": _relative(optix_scale_path),
            "rayjoin_same_stream_summary": _relative(rayjoin_path),
            "rtnn_same_contract_summary": _relative(rtnn_path),
            "rt_dbscan_same_contract_summary": _relative(rt_dbscan_path),
            "embree_same_contract_scale_probe": embree_probe["source_dir"],
        },
        "measured_pairs": (measured_pair,),
        "scale_comparison_rows": scale_comparison_rows,
        "same_stream_comparison_rows": same_stream_comparison_rows,
        "same_contract_backend_comparison_rows": same_contract_backend_comparison_rows,
        "planning_rows": planning_rows,
        "summary": {
            "app_count": len(planning_rows),
            "measured_pair_count": 1,
            "internal_query_median_ratio_count": len(internal_ratio_rows),
            "optimized_embree_pairs_count": 1,
            "scale_comparison_row_count": len(scale_comparison_rows),
            "same_stream_comparison_row_count": len(same_stream_comparison_rows),
            "same_contract_backend_comparison_row_count": len(same_contract_backend_comparison_rows),
            "boundary_limited_phase_ratio_count": len(boundary_limited_rows),
            "same_contract_scale_pair_required_count": sum(
                1 for row in planning_rows if row["goal4341_status"] == "same_contract_scale_pair_required"
            ),
            "contract_split_pair_required_count": sum(
                1 for row in planning_rows if row["goal4341_status"] == "contract_split_pair_required"
            ),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def validate_optimized_optix_embree_comparison_packet() -> dict[str, Any]:
    return optimized_optix_embree_comparison_packet()["validation"]
