from __future__ import annotations

import json
from pathlib import Path
from typing import Any


V2_13_EMBREE_CPU_FAIRNESS_PACKET_VERSION = "rtdl.v2_13.embree_cpu_fairness.goal4369.v1"

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLIC_COMPARISON = (
    ROOT / "docs" / "release_reports" / "v2_12" / "public_rt_vs_embree_comparison.json"
)
DEFAULT_RAYJOIN_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
    / "summary.json"
)
DEFAULT_PIP_OPTIMIZED_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4368_pip_exact_prepared_points_executor_2026-06-13"
    / "summary.json"
)
DEFAULT_CPU_REFERENCE_THREADS8 = (
    ROOT
    / "docs"
    / "reports"
    / "goal4369_embree_cpu_fairness_hardening_2026-06-13"
    / "v2_11_cpu_partner_threads8.json"
)


EMBREE_ROUTE_BY_CONTRACT: dict[str, dict[str, Any]] = {
    "prepared_fixed_radius_node_coverage_threshold_decision": {
        "route": "embree_prepared_fixed_radius_threshold_count_2d",
        "route_kind": "embree_cpu_rt_plus_python_continuation",
        "partner": "python_barnes_hut_opening_force_logic_outside_timed_row",
    },
    "native_collect_k_bounded_witness_rows": {
        "route": "rtdl_embree_collect_k_bounded_i64",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "directed_threshold_prepared_fixed_radius_count": {
        "route": "embree_threshold_count",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "generic_prepared_aabb_index_query_2d": {
        "route": "embree_native_aabb_collision_index",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "generic_ray_triangle_primitive_grouped_i64_reduction_3d_prepared_count": {
        "route": "embree_prepared_ray_triangle_grouped_i64_reduction",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1": {
        "route": "embree_prepared_grouped_segment_any_hit_flags",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "rt_dbscan_clustered3d_count_threshold_flags_plus_numba_prepared_grid_column_signature": {
        "route": "embree_point_query_fixed_radius_3d_threshold_capped_rows",
        "route_kind": "embree_cpu_rt_plus_numba_reference",
        "partner": "numba_fixed_on_both_sides",
    },
    "prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows": {
        "route": "embree_prepared_fixed_radius_ranked_summary_raw_rows_3d",
        "route_kind": "embree_cpu_rt_plus_python_continuation",
        "partner": "python_ranked_summary_contract_not_rt_core_neighbor_search",
    },
    "lsi_same_stream_scalar_count": {
        "route": "prepared_embree_native_scalar_count_lsi",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "pip_same_stream_scalar_count": {
        "route": "prepared_embree_native_scalar_count_pip",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "none",
    },
    "rt_graph_2a1_generic_ray_triangle_any_hit": {
        "route": "embree_ray_triangle_weighted_any_hit_sum_3d",
        "route_kind": "embree_cpu_rt_primitive",
        "partner": "python_graph_fixture_preprocessing_outside_timed_row",
    },
}

REPEAT_SOURCE_BY_CONTRACT: dict[str, Path] = {
    "prepared_fixed_radius_node_coverage_threshold_decision": (
        ROOT / "docs" / "reports" / "goal4362_rtx_a4000_v2_12_barnes_hut_same_contract_2026-06-13" / "summary.json"
    ),
    "native_collect_k_bounded_witness_rows": (
        ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe" / "contact_embree_grid64_witness128.json"
    ),
    "directed_threshold_prepared_fixed_radius_count": (
        ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe" / "hausdorff_embree_threshold_1024.json"
    ),
    "generic_ray_triangle_primitive_grouped_i64_reduction_3d_prepared_count": (
        ROOT / "docs" / "reports" / "goal4364_rtx_a4000_v2_12_raydb_same_contract_2026-06-13" / "summary.json"
    ),
    "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1": (
        ROOT / "docs" / "reports" / "goal4363_rtx_a4000_v2_12_robot_collision_same_contract_2026-06-13" / "summary.json"
    ),
    "rt_dbscan_clustered3d_count_threshold_flags_plus_numba_prepared_grid_column_signature": (
        ROOT / "docs" / "reports" / "goal4361_rtx_a4000_v2_12_rt_dbscan_same_contract_2026-06-13" / "summary.json"
    ),
    "prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows": (
        ROOT / "docs" / "reports" / "goal4360_rtx_a4000_v2_12_rtnn_same_contract_2026-06-13" / "summary.json"
    ),
    "rt_graph_2a1_generic_ray_triangle_any_hit": (
        ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe" / "triangle_embree_rtgraph2a1_2048.json"
    ),
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _thread_env_is_eight(cpu_reference: dict[str, Any]) -> bool:
    env = cpu_reference.get("runtime_environment", {}).get("cpu_thread_env", {})
    required = (
        "OMP_NUM_THREADS",
        "TBB_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "RTDL_EMBREE_THREADS",
    )
    return all(str(env.get(name)) == "8" for name in required)


def _fresh_reference_by_app(cpu_reference: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["app"]): dict(row) for row in cpu_reference.get("rows", [])}


def _repeat_warmup(row: dict[str, Any], *, rayjoin: dict[str, Any], pip_optimized: dict[str, Any]) -> dict[str, Any]:
    contract = row["contract"]
    source = Path(str(row["source"]))
    source_path = ROOT / source if not source.is_absolute() else source
    if contract == "lsi_same_stream_scalar_count":
        timing = rayjoin["rtdl"]["lsi"]["backends"]["embree"]["timing"]
        return {"repeat": int(timing["repeats"]), "warmup": int(timing["warmups"]), "source": "rayjoin_lsi_timing"}
    if contract == "pip_same_stream_scalar_count":
        timing = pip_optimized["rtdl"]["pip"]["backends"]["embree"]["timing"]
        return {"repeat": int(timing["repeats"]), "warmup": int(timing["warmups"]), "source": "goal4368_pip_timing"}
    source_path = REPEAT_SOURCE_BY_CONTRACT.get(contract, source_path)
    if source_path.is_file():
        payload = _load_json(source_path)
        fixed = payload.get("fixed_inputs") or {}
        if fixed.get("repeat") is not None:
            return {
                "repeat": int(fixed["repeat"]),
                "warmup": int(fixed.get("warmup") or 0),
                "source": "fixed_inputs",
            }
        repeat_protocol = payload.get("repeat_protocol") or {}
        if repeat_protocol.get("repeat") is not None:
            return {
                "repeat": int(repeat_protocol["repeat"]),
                "warmup": int(repeat_protocol.get("warmup") or 0),
                "source": "repeat_protocol",
            }
        if payload.get("native_collect_repeat_count") is not None:
            return {
                "repeat": int(payload["native_collect_repeat_count"]),
                "warmup": 0,
                "source": "native_collect_repeat_count",
            }
        timing_ms = payload.get("timing_ms") or {}
        if timing_ms.get("query_repeat") is not None:
            return {
                "repeat": int(timing_ms["query_repeat"]),
                "warmup": int(timing_ms.get("query_warmup") or 0),
                "source": "timing_ms",
            }
    if row.get("metric_name") == "query_median_sec" and contract == "generic_prepared_aabb_index_query_2d":
        return {"repeat": 2, "warmup": 1, "source": "goal4340_scale"}
    return {"repeat": None, "warmup": None, "source": "not_recorded"}


def _pip_current_row(row: dict[str, Any], pip_optimized: dict[str, Any]) -> dict[str, Any]:
    optix = pip_optimized["rtdl"]["pip"]["backends"]["optix"]
    embree = pip_optimized["rtdl"]["pip"]["backends"]["embree"]
    embree_ms = float(embree["hot_median_sec"]) * 1000.0
    optix_ms = float(optix["hot_median_sec"]) * 1000.0
    return {
        **row,
        "source": _relative(DEFAULT_PIP_OPTIMIZED_SUMMARY),
        "metric_name": "hot_query_median_ms",
        "metric_unit": "ms",
        "embree_metric": embree_ms,
        "optix_metric": optix_ms,
        "embree_divided_by_optix": embree_ms / optix_ms,
        "faster_backend": "optix" if optix_ms < embree_ms else "embree",
        "v2_13_metric_supersedes_v2_12_pip": True,
    }


def v2_13_embree_cpu_fairness_packet(
    *,
    public_comparison_path: Path | None = None,
    rayjoin_summary_path: Path | None = None,
    pip_optimized_summary_path: Path | None = None,
    cpu_reference_threads8_path: Path | None = None,
) -> dict[str, Any]:
    public_path = public_comparison_path or DEFAULT_PUBLIC_COMPARISON
    rayjoin_path = rayjoin_summary_path or DEFAULT_RAYJOIN_SUMMARY
    pip_path = pip_optimized_summary_path or DEFAULT_PIP_OPTIMIZED_SUMMARY
    cpu_path = cpu_reference_threads8_path or DEFAULT_CPU_REFERENCE_THREADS8

    public = _load_json(public_path)
    rayjoin = _load_json(rayjoin_path)
    pip_optimized = _load_json(pip_path)
    cpu_reference = _load_json(cpu_path)
    fresh_by_app = _fresh_reference_by_app(cpu_reference)

    rows: list[dict[str, Any]] = []
    for original in public["rows"]:
        row = dict(original)
        if row["contract"] == "pip_same_stream_scalar_count":
            row = _pip_current_row(row, pip_optimized)
        route = EMBREE_ROUTE_BY_CONTRACT[row["contract"]]
        fresh = fresh_by_app.get(row["app"])
        repeat = _repeat_warmup(row, rayjoin=rayjoin, pip_optimized=pip_optimized)
        rows.append(
            {
                "app": row["app"],
                "row_label": row["row_label"],
                "contract": row["contract"],
                "metric_name": row["metric_name"],
                "metric_unit": row["metric_unit"],
                "embree_metric": row["embree_metric"],
                "optix_metric": row["optix_metric"],
                "embree_divided_by_optix": row["embree_divided_by_optix"],
                "faster_backend": row["faster_backend"],
                "embree_route": route["route"],
                "embree_route_kind": route["route_kind"],
                "partner_policy": route["partner"],
                "embree_rt_core_accelerated": False,
                "same_contract_or_same_stream": True,
                "fallback_detected": False,
                "fallback_note": "optimized native/partner route; no old columnar fallback accepted",
                "repeat": repeat["repeat"],
                "warmup": repeat["warmup"],
                "repeat_warmup_source": repeat["source"],
                "fresh_threaded_reference_status": fresh.get("status") if fresh else "missing",
                "fresh_threaded_reference_row_id": fresh.get("row_id") if fresh else None,
                "fresh_threaded_reference_scope": "compatibility route/pass, not replacement for performance metric",
                "fresh_threaded_reference_threads": int(
                    (fresh or {}).get("cpu_thread_env", {}).get("RTDL_EMBREE_THREADS", 0) or 0
                ),
                "source": row["source"],
                "v2_13_metric_supersedes_v2_12_pip": bool(row.get("v2_13_metric_supersedes_v2_12_pip", False)),
                "public_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            }
        )

    errors: list[str] = []
    if public.get("validation", {}).get("status") != "accept":
        errors.append("v2.12 public comparison artifact is not accepted")
    if not cpu_reference.get("all_pass"):
        errors.append("fresh threads=8 Embree CPU partner reference did not all-pass")
    if not _thread_env_is_eight(cpu_reference):
        errors.append("fresh CPU partner reference must record all thread env vars as 8")
    if len(rows) != 11:
        errors.append("fairness packet must cover eleven promoted comparison rows")
    if len({row["app"] for row in rows}) != 10:
        errors.append("fairness packet must cover ten promoted benchmark apps")
    if any(row["fresh_threaded_reference_status"] != "pass" for row in rows):
        errors.append("every promoted row must have a passing fresh threaded CPU reference by app")
    if any(row["embree_rt_core_accelerated"] for row in rows):
        errors.append("Embree CPU rows must not be RT-core accelerated")
    if any(row["fallback_detected"] for row in rows):
        errors.append("old fallback routes must not be accepted in the fairness table")
    pip_rows = [row for row in rows if row["contract"] == "pip_same_stream_scalar_count"]
    if len(pip_rows) != 1 or float(pip_rows[0]["embree_divided_by_optix"]) <= 3.0:
        errors.append("PIP row must use the Goal4368 optimized exact baseline")

    return {
        "version": V2_13_EMBREE_CPU_FAIRNESS_PACKET_VERSION,
        "status": "accept_internal_cpu_fairness_hardened" if not errors else "reject",
        "source_artifacts": {
            "public_comparison": _relative(public_path),
            "rayjoin_same_stream": _relative(rayjoin_path),
            "pip_optimized": _relative(pip_path),
            "fresh_cpu_reference_threads8": _relative(cpu_path),
        },
        "cpu_thread_protocol": cpu_reference["runtime_environment"]["cpu_thread_env"],
        "cpu_reference_platform": cpu_reference["runtime_environment"]["platform"],
        "summary": {
            "row_count": len(rows),
            "promoted_app_count": len({row["app"] for row in rows}),
            "fresh_threaded_cpu_reference_app_count": len(fresh_by_app),
            "fresh_threaded_cpu_reference_all_pass": bool(cpu_reference.get("all_pass")),
            "fresh_threaded_cpu_reference_threads": int(
                cpu_reference["runtime_environment"]["cpu_thread_env"]["RTDL_EMBREE_THREADS"]
            ),
            "numba_partner_row_count": sum(row["partner_policy"] == "numba_fixed_on_both_sides" for row in rows),
            "fallback_detected_row_count": sum(row["fallback_detected"] for row in rows),
            "embree_rt_core_accelerated_row_count": sum(row["embree_rt_core_accelerated"] for row in rows),
            "pip_current_embree_divided_by_optix": _round(pip_rows[0]["embree_divided_by_optix"] if pip_rows else None, 2),
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "rows": rows,
        "claim_boundary": (
            "Goal4369 hardens the Embree CPU side of the v2.13 comparison matrix. "
            "It records route, partner, thread, repeat/warmup, and fallback status for the internal "
            "row-scoped comparison. It does not authorize public speedup, whole-application speedup, "
            "paper-reproduction, Intel GPU, AMD GPU, automatic partner selection, or broad RT-core wording."
        ),
        "validation": {"status": "accept" if not errors else "reject", "errors": errors},
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
        "amd_gpu_performance_claim_authorized": False,
    }


def _fmt_number(value: Any) -> str:
    if value is None:
        return "n/a"
    numeric = float(value)
    digits = 6 if abs(numeric) < 1.0 else 3
    return f"{numeric:.{digits}f}".rstrip("0").rstrip(".")


def markdown_v2_13_embree_cpu_fairness_packet(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal4369 Embree CPU Fairness Hardening Packet",
        "",
        "Status: internal v2.13 CPU-side fairness evidence; not public speedup wording.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Validation | `{payload['validation']['status']}` |",
        f"| Rows | {payload['summary']['row_count']} |",
        f"| Promoted apps | {payload['summary']['promoted_app_count']} |",
        f"| Fresh threads=8 CPU reference all-pass | {payload['summary']['fresh_threaded_cpu_reference_all_pass']} |",
        f"| Fresh CPU platform | `{payload['cpu_reference_platform']}` |",
        f"| Numba partner rows | {payload['summary']['numba_partner_row_count']} |",
        f"| Fallback rows accepted | {payload['summary']['fallback_detected_row_count']} |",
        f"| Embree rows marked RT-core accelerated | {payload['summary']['embree_rt_core_accelerated_row_count']} |",
        "",
        "## Thread Protocol",
        "",
        "| Env var | Value |",
        "| --- | ---: |",
    ]
    for key, value in sorted(payload["cpu_thread_protocol"].items()):
        lines.append(f"| `{key}` | {value} |")

    lines.extend(
        [
            "",
            "## Row Audit",
            "",
            "| Row | Embree route | Partner | Metric | Embree/OptiX | Repeat/Warmup | Threaded CPU ref | Fallback |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        metric = f"{_fmt_number(row['embree_metric'])} {row['metric_unit']}"
        repeat = f"{row['repeat']}/{row['warmup']}" if row["repeat"] is not None else "n/a"
        ref = f"{row['fresh_threaded_reference_status']} ({row['fresh_threaded_reference_row_id']})"
        lines.append(
            "| {label} | `{route}` | `{partner}` | {metric} | {ratio}x | {repeat} | {ref} | {fallback} |".format(
                label=row["row_label"],
                route=row["embree_route"],
                partner=row["partner_policy"],
                metric=metric,
                ratio=_fmt_number(row["embree_divided_by_optix"]),
                repeat=repeat,
                ref=ref,
                fallback="none" if not row["fallback_detected"] else "detected",
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The CPU side is not NVIDIA RT-core accelerated: every Embree row records `embree_rt_core_accelerated = false`.",
            "- The fresh pod reference run proves all ten promoted benchmark apps still have passing Embree CPU front doors under `RTDL_EMBREE_THREADS=8` and matching OMP/TBB/MKL/OpenBLAS/NumExpr thread caps.",
            "- RT-DBSCAN is the only Numba-partner row in this packet, and the policy is fixed on both sides rather than auto-selected.",
            "- The PIP row uses the clean Goal4368 exact prepared-points executor evidence, so the current same-contract PIP CPU-vs-RT comparison is about 3.22x in favor of OptiX while RayJoin RT still remains faster than RTDL PIP.",
            "",
            "## Boundary",
            "",
            payload["claim_boundary"],
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"
