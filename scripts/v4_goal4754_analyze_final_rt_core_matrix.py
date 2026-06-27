#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "future" / "v4" / "evidence" / "v4_goal4756_serious_all30_generated_spatial_2026-06-26"
DEFAULT_JSON = ROOT / "future" / "v4" / "evidence" / "v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json"
DEFAULT_MD = ROOT / "future" / "v4" / "v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md"

APP_ORDER = (
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "rtnn",
    "spatial_rayjoin",
    "barnes_hut",
)
VERSIONS = ("v2_14", "v3_0_2", "v4_0")


def _get(data: dict[str, Any], *path: str) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _num(value: Any) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _first(*values: Any) -> float | None:
    for value in values:
        number = _num(value)
        if number is not None and number > 0.0:
            return number
    return None


def _ratio(old: float | None, new: float | None) -> float | None:
    if old is None or new is None or old <= 0.0 or new <= 0.0:
        return None
    return old / new


def _sum_numbers(values: list[Any]) -> float | None:
    numbers = [_num(value) for value in values]
    if any(value is None for value in numbers):
        return None
    return float(sum(value for value in numbers if value is not None))


def _extract(app: str, payload: dict[str, Any]) -> dict[str, Any]:
    if app == "rt_dbscan":
        hot = _first(
            _get(payload, "metadata", "prepared_execution_session_runner_last_metadata", "measured_median_sec"),
            _get(payload, "metadata", "benchmark_timing_breakdown", "host_observed_sec", "adapter_run_sec"),
            _get(payload, "metadata", "benchmark_timing_breakdown", "derived_sec", "grouped_native_sec"),
            payload.get("elapsed_sec"),
        )
        wall = _first(payload.get("elapsed_sec"), hot)
        parity = payload.get("matches_reference")
        return {
            "hot_sec": hot,
            "wall_sec": wall,
            "parity": True if parity is True else "reference_skipped_or_not_emitted",
            "metric_source": "prepared_runner_median_or_adapter_run_sec",
            "route": payload.get("mode"),
        }
    if app == "raydb_style":
        hot = _first(
            _get(payload, "metadata", "prepared_iteration_wall_summary", "median_sec"),
            _get(payload, "metadata", "timings", "native_call_wall"),
            payload.get("elapsed_sec"),
        )
        return {
            "hot_sec": hot,
            "wall_sec": _first(payload.get("elapsed_sec"), hot),
            "parity": payload.get("matches_cpu_reference") is True,
            "metric_source": "prepared_iteration_wall_summary.median_sec",
            "route": payload.get("backend"),
        }
    if app == "triangle_counting":
        query_ms = _first(
            _get(payload, "timing_ms", "query_median_ms"),
            _get(payload, "phase_split_ms", "measured_replay_query_median_ms"),
        )
        hot = query_ms / 1000.0 if query_ms is not None else None
        one_shot_ms = _first(_get(payload, "phase_split_ms", "one_shot_backend_estimate_ms"))
        wall = one_shot_ms / 1000.0 if one_shot_ms is not None else hot
        return {
            "hot_sec": hot,
            "wall_sec": wall,
            "parity": payload.get("triangle_count_matches_oracle") is True,
            "metric_source": "timing_ms.query_median_ms; wall=phase_split_ms.one_shot_backend_estimate_ms",
            "route": payload.get("mode"),
        }
    if app == "librts_spatial_index":
        hot = _first(
            _get(payload, "repeat_protocol", "query_sec_median"),
            _get(payload, "run_phases", "query_median_sec"),
        )
        return {
            "hot_sec": hot,
            "wall_sec": _first(payload.get("elapsed_sec"), hot),
            "parity": payload.get("matches_cpu_reference") is True or payload.get("cpu_reference_skipped") is True,
            "metric_source": "repeat_protocol.query_sec_median",
            "route": payload.get("mode"),
        }
    if app == "hausdorff_xhd":
        hot = _first(
            _get(payload, "repeat_protocol", "measured_query_total_sec"),
            _get(payload, "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
            _get(payload, "run_phases", "optix_query_sec"),
        )
        wall = _sum_numbers([
            _get(payload, "run_phases", "input_construction_sec"),
            _get(payload, "run_phases", "scene_prepare_sec"),
            _get(payload, "run_phases", "query_fixed_radius_threshold_reached_count_sec"),
            _get(payload, "run_phases", "python_postprocess_sec"),
        ])
        return {
            "hot_sec": hot,
            "wall_sec": wall or hot,
            "parity": payload.get("matches_oracle") is True and payload.get("oracle_decision_matches") is True,
            "metric_source": "threshold repeat_protocol.measured_query_total_sec",
            "route": f"{payload.get('backend')}:{payload.get('optix_summary_mode')}",
        }
    if app == "robot_collision":
        hot = _first(
            _get(payload, "tail_medians", "total_run_seconds"),
            _get(payload, "tail_medians", "phase_timing_seconds", "traversal"),
        )
        return {
            "hot_sec": hot,
            "wall_sec": hot,
            "parity": "probe_reference_skipped_for_serious_timing",
            "metric_source": "tail_medians.total_run_seconds with no_probe_reference",
            "route": payload.get("mode"),
        }
    if app == "contact_manifold":
        phases = payload.get("run_phases", {}) if isinstance(payload.get("run_phases"), dict) else {}
        hot = _sum_numbers([
            phases.get("generic_aabb_broadphase_sec"),
            phases.get("collect_k_bounded_rows_sec"),
            phases.get("python_exact_refinement_sec"),
        ])
        wall = _sum_numbers([value for key, value in phases.items() if key.endswith("_sec")])
        return {
            "hot_sec": hot,
            "wall_sec": wall or hot,
            "parity": payload.get("matches_cpu_reference") is True,
            "metric_source": "generic_aabb_broadphase+collect_k+python_exact_refinement",
            "route": f"{payload.get('mode')}:{payload.get('candidate_discovery_backend')}",
        }
    if app == "rtnn":
        hot = _first(
            _get(payload, "timing_sec", "hot_query_median"),
            _get(payload, "timing_sec", "runner_measured_median"),
            _get(payload, "runner_payload", "elapsed_median_sec"),
            _get(payload, "runner_payload", "elapsed_sec"),
        )
        wall = _first(
            _get(payload, "timing_sec", "runner_wall"),
            _get(payload, "runner_payload", "elapsed_sec"),
            hot,
        )
        parity = payload.get("signature_match_status")
        return {
            "hot_sec": hot,
            "wall_sec": wall,
            "parity": True if isinstance(parity, dict) and parity.get("query_count_ok") is True else "signature_or_legacy_payload",
            "metric_source": "V4 timing_sec.hot_query_median; old runner_payload.elapsed_median_sec",
            "route": payload.get("mode"),
        }
    if app == "spatial_rayjoin":
        hot = _first(_get(payload, "repeat_protocol", "measured_query_total_sec"))
        return {
            "hot_sec": hot,
            "wall_sec": hot,
            "parity": "count_contract_json_emitted",
            "metric_source": "repeat_protocol.measured_query_total_sec",
            "route": payload.get("execution_route"),
        }
    if app == "barnes_hut":
        hot = _first(_get(payload, "medians", "hot_seconds"))
        wall = _first(_get(payload, "medians", "wall_seconds"), hot)
        validation = payload.get("validation", {}) if isinstance(payload.get("validation"), dict) else {}
        return {
            "hot_sec": hot,
            "wall_sec": wall,
            "parity": True if validation.get("passed") is True else validation.get("reason", "validation_skipped"),
            "metric_source": "medians.hot_seconds",
            "route": payload.get("route"),
        }
    raise ValueError(f"unknown app: {app}")


def analyze(input_dir: Path) -> dict[str, Any]:
    raw = input_dir / "raw"
    rows: list[dict[str, Any]] = []
    by_app_version: dict[tuple[str, str], dict[str, Any]] = {}
    for app in APP_ORDER:
        for version in VERSIONS:
            path = raw / f"{version}_{app}.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            metrics = _extract(app, payload)
            row = {
                "app": app,
                "version": version,
                "path": str(path),
                **metrics,
            }
            rows.append(row)
            by_app_version[(app, version)] = row

    app_rows: list[dict[str, Any]] = []
    for app in APP_ORDER:
        v2 = by_app_version[(app, "v2_14")]
        v3 = by_app_version[(app, "v3_0_2")]
        v4 = by_app_version[(app, "v4_0")]
        v4_vs_v2 = _ratio(v2["hot_sec"], v4["hot_sec"])
        v4_vs_v3 = _ratio(v3["hot_sec"], v4["hot_sec"])
        v3_vs_v2 = _ratio(v2["hot_sec"], v3["hot_sec"])
        claim_class = "parity_or_control"
        v4_vs_v2_wall = _ratio(v2["wall_sec"], v4["wall_sec"])
        v4_vs_v3_wall = _ratio(v3["wall_sec"], v4["wall_sec"])
        if app == "triangle_counting" and v4_vs_v3 is not None and v4_vs_v3 < 0.98 and v4_vs_v2_wall is not None and v4_vs_v2_wall >= 1.20:
            claim_class = "wall_win_hot_replay_regression"
        elif v4_vs_v2 is not None and v4_vs_v2 >= 1.20 and v4_vs_v3 is not None and v4_vs_v3 >= 0.98:
            claim_class = "material_v4_over_v2_candidate"
        elif v4_vs_v2 is not None and v4_vs_v2 < 0.98:
            claim_class = "v4_regression_vs_v2"
        elif v4_vs_v3 is not None and v4_vs_v3 < 0.98:
            claim_class = "v4_regression_vs_v3"
        app_rows.append(
            {
                "app": app,
                "v2_14_hot_sec": v2["hot_sec"],
                "v3_0_2_hot_sec": v3["hot_sec"],
                "v4_0_hot_sec": v4["hot_sec"],
                "v4_over_v2_14_hot_speedup": v4_vs_v2,
                "v4_over_v3_0_2_hot_speedup": v4_vs_v3,
                "v3_over_v2_14_hot_speedup": v3_vs_v2,
                "v2_14_wall_sec": v2["wall_sec"],
                "v3_0_2_wall_sec": v3["wall_sec"],
                "v4_0_wall_sec": v4["wall_sec"],
                "v4_over_v2_14_wall_speedup": v4_vs_v2_wall,
                "v4_over_v3_0_2_wall_speedup": v4_vs_v3_wall,
                "parity_v2_14": v2["parity"],
                "parity_v3_0_2": v3["parity"],
                "parity_v4_0": v4["parity"],
                "metric_source": v4["metric_source"],
                "v4_route": v4["route"],
                "claim_class": claim_class,
            }
        )
    candidates = [row["app"] for row in app_rows if row["claim_class"] == "material_v4_over_v2_candidate"]
    regressions = [
        row["app"]
        for row in app_rows
        if str(row["claim_class"]).startswith("v4_regression")
        or row["claim_class"] == "wall_win_hot_replay_regression"
    ]
    speedups = [row["v4_over_v2_14_hot_speedup"] for row in app_rows if isinstance(row["v4_over_v2_14_hot_speedup"], float)]
    geomean = math.prod(speedups) ** (1.0 / len(speedups)) if speedups else None
    return {
        "schema": "rtdl.v4.goal4754.final_rt_core_matrix_analysis.v1",
        "status": "analysis_complete_not_release_authorization",
        "source_matrix": str(input_dir),
        "app_rows": app_rows,
        "raw_rows": rows,
        "summary": {
            "app_count": len(app_rows),
            "material_candidate_apps": candidates,
            "regression_apps": regressions,
            "v4_over_v2_14_hot_geomean": geomean,
            "all_rows_have_v2_v3_v4": len(app_rows) == 10,
            "embree_primary_denominator_used": False,
        },
        "claim_boundary": {
            "release_authorized": False,
            "public_speed_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
        },
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4756 Final RT-Core Matrix Analysis",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Primary denominator: NVIDIA OptiX/RT-core rows only. Embree is not used as a primary denominator.",
        "",
        "| app | V2.14 hot s | V3 hot s | V4 hot s | V4/V2 hot | V4/V3 hot | V4/V2 wall | V4/V3 wall | class | metric source |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["app_rows"]:
        lines.append(
            "| `{app}` | {v2} | {v3} | {v4} | {r2} | {r3} | {wr2} | {wr3} | `{cls}` | {src} |".format(
                app=row["app"],
                v2=_fmt(row["v2_14_hot_sec"]),
                v3=_fmt(row["v3_0_2_hot_sec"]),
                v4=_fmt(row["v4_0_hot_sec"]),
                r2=_fmt(row["v4_over_v2_14_hot_speedup"]),
                r3=_fmt(row["v4_over_v3_0_2_hot_speedup"]),
                wr2=_fmt(row["v4_over_v2_14_wall_speedup"]),
                wr3=_fmt(row["v4_over_v3_0_2_wall_speedup"]),
                cls=row["claim_class"],
                src=row["metric_source"],
            )
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- material candidate apps: `{summary['material_candidate_apps']}`",
            f"- regression apps: `{summary['regression_apps']}`",
            f"- V4/V2.14 hot geomean: `{_fmt(summary['v4_over_v2_14_hot_geomean'])}`",
            f"- all rows have V2/V3/V4: `{summary['all_rows_have_v2_v3_v4']}`",
            f"- Embree primary denominator used: `{summary['embree_primary_denominator_used']}`",
            "",
            "## Non-Authorization",
            "",
            "This analysis does not authorize release, broad public speedup wording, or whole-app high-performance claims.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze the final V4.0 RT-core POD matrix.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    payload = analyze(args.input_dir)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(args.json_out)
    print(args.md_out)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
