from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .v4_goal4638_formal_scorecard_freeze import validate_v4_goal4638_formal_scorecard_freeze


V4_GOAL4639_STATUS = "goal4639_serious_release_scorecard_pod_gate_not_release"
V4_GOAL4639_DECISION_IF_PASS = "release_candidate_possible_pending_3ai"
V4_GOAL4639_DECISION_IF_FAIL = "performance_preview_only"
V4_GOAL4639_DECISION_IF_BLOCKED = "blocked_incomplete"


@dataclass(frozen=True)
class V4Goal4639Run:
    run_id: str
    surface: str
    command: tuple[str, ...]
    evidence: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "surface": self.surface,
            "command": self.command,
            "evidence": self.evidence,
        }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def v4_goal4639_run_plan(output_dir: Path, *, python_exe: str | None = None, root: Path | None = None) -> tuple[V4Goal4639Run, ...]:
    root = (root or Path.cwd()).resolve()
    output_dir = output_dir.resolve()
    py = python_exe or sys.executable

    def out(name: str) -> Path:
        return output_dir / name

    return (
        V4Goal4639Run(
            run_id="fixed_radius_count_threshold",
            surface="v4_fixed_radius_count_threshold_2d_device_arrays",
            command=(
                py,
                "scripts/v4_section8_device_array_frontdoor_validation.py",
                "--partner",
                "torch",
                "--repeat",
                "7",
                "--warmup",
                "1",
                "--progress",
                "--json-out",
                _rel(out("fixed_radius_count_threshold.json"), root),
            ),
            evidence=(_rel(out("fixed_radius_count_threshold.json"), root),),
        ),
        V4Goal4639Run(
            run_id="closest_hit_grouped_argmin",
            surface="v4_closest_hit_grouped_argmin_3d_device_arrays",
            command=(
                py,
                "scripts/v4_section8_closest_hit_grouped_argmin_device_frontdoor_validation.py",
                "--repeat",
                "7",
                "--warmup",
                "1",
                "--progress",
                "--json-out",
                _rel(out("closest_hit_grouped_argmin.json"), root),
            ),
            evidence=(_rel(out("closest_hit_grouped_argmin.json"), root),),
        ),
        V4Goal4639Run(
            run_id="ray_triangle_any_hit_flags",
            surface="v4_ray_triangle_any_hit_flags_2d_device_arrays",
            command=(
                py,
                "scripts/v4_section8_any_hit_flags_device_frontdoor_validation.py",
                "--repeat",
                "5",
                "--warmup",
                "1",
                "--max-torch-reference-count",
                "8192",
                "--progress",
                "--json-out",
                _rel(out("ray_triangle_any_hit_flags.json"), root),
            ),
            evidence=(_rel(out("ray_triangle_any_hit_flags.json"), root),),
        ),
        *(
            V4Goal4639Run(
                run_id=f"primitive_grouped_i64_width{width}",
                surface="v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
                command=(
                    py,
                    "scripts/v4_primitive_grouped_i64_device_outputs_validation.py",
                    "--ray-counts",
                    "32768,131072",
                    "--group-width",
                    str(width),
                    "--repeat",
                    "7",
                    "--warmup",
                    "2",
                    "--progress",
                    "--json-out",
                    _rel(out(f"primitive_grouped_i64_width{width}.json"), root),
                ),
                evidence=(_rel(out(f"primitive_grouped_i64_width{width}.json"), root),),
            )
            for width in (1, 16, 256)
        ),
        *(
            V4Goal4639Run(
                run_id=f"point_group_nearest_witness_{variant}",
                surface="v4_point_group_nearest_witness_2d_device_arrays",
                command=(
                    py,
                    "scripts/v4_point_group_nearest_witness_device_outputs_validation.py",
                    "--query-counts",
                    "32768,131072",
                    "--fixture-variant",
                    variant,
                    "--repeat",
                    "7",
                    "--warmup",
                    "2",
                    "--progress",
                    "--json-out",
                    _rel(out(f"point_group_nearest_witness_{variant}.json"), root),
                    "--md-out",
                    _rel(out(f"point_group_nearest_witness_{variant}.md"), root),
                ),
                evidence=(
                    _rel(out(f"point_group_nearest_witness_{variant}.json"), root),
                    _rel(out(f"point_group_nearest_witness_{variant}.md"), root),
                ),
            )
            for variant in ("mixed4", "mixed6")
        ),
        V4Goal4639Run(
            run_id="ray_triangle_any_hit_weighted_sum",
            surface="v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            command=(
                py,
                "scripts/v4_ray_triangle_weighted_sum_device_output_validation.py",
                "--goal4633-promotion-gate",
                "--progress",
                "--json-out",
                _rel(out("ray_triangle_any_hit_weighted_sum.json"), root),
                "--md-out",
                _rel(out("ray_triangle_any_hit_weighted_sum.md"), root),
            ),
            evidence=(
                _rel(out("ray_triangle_any_hit_weighted_sum.json"), root),
                _rel(out("ray_triangle_any_hit_weighted_sum.md"), root),
            ),
        ),
        V4Goal4639Run(
            run_id="fixed_radius_graph_component_union",
            surface="v4_fixed_radius_graph_component_union_3d_device_arrays",
            command=(
                py,
                "scripts/v3_phoenix_component_union_m38_pod_ab.py",
                "--output-dir",
                _rel(out("fixed_radius_graph_component_union"), root),
                "--variant",
                "all",
                "--dataset",
                "clustered3d",
                "--point-count",
                "262144",
                "--radius",
                "3.0",
                "--min-neighbors",
                "4",
                "--seed",
                "20260625",
                "--repeat",
                "5",
                "--warmup",
                "1",
                "--require-rt-hardware",
                "--heartbeat-sec",
                "30",
            ),
            evidence=(_rel(out("fixed_radius_graph_component_union/summary.json"), root),),
        ),
        V4Goal4639Run(
            run_id="aabb_index_all_ops_count",
            surface="v4_aabb_index_query_2d_all_ops_count_prepared_runner",
            command=(
                py,
                "scripts/v3_0_m30_librts_prepared_all_ops_refresh.py",
                "--box-count",
                "1000000",
                "--query-count",
                "1000",
                "--seed",
                "2025",
                "--max-box-width",
                "0.005",
                "--max-box-height",
                "0.005",
                "--max-query-width",
                "0.005",
                "--max-query-height",
                "0.005",
                "--operation",
                "all",
                "--backends",
                "embree,optix",
                "--warmup",
                "1",
                "--repeat-overrides",
                "embree=240,optix=240",
                "--output",
                _rel(out("aabb_index_all_ops_count.json"), root),
            ),
            evidence=(_rel(out("aabb_index_all_ops_count.json"), root),),
        ),
    )


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _ok(surface: str, representative_ratio: float | None, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface": surface,
        "status": "pass",
        "passed": True,
        "representative_ratio": representative_ratio,
        "details": details,
    }


def _fail(surface: str, reason: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "surface": surface,
        "status": "fail",
        "passed": False,
        "representative_ratio": None,
        "failure_reason": reason,
        "details": details or {},
    }


def _blocked(surface: str, reason: str, path: Path) -> dict[str, Any]:
    return {
        "surface": surface,
        "status": "blocked_incomplete",
        "passed": False,
        "representative_ratio": None,
        "failure_reason": reason,
        "evidence_path": path.as_posix(),
    }


def _evaluate_fixed_radius(path: Path) -> dict[str, Any]:
    surface = "v4_fixed_radius_count_threshold_2d_device_arrays"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    gate = data.get("performance_gate", {})
    results = data.get("results", [])
    passing = gate.get("passing_sizes", [])
    correctness = all(bool(row.get("correctness_passed")) for row in results)
    gaps = [float(row["comparisons"]["route_d_count_rows"]["device_array_to_route_d_rows_gap"]) for row in results]
    reductions = [
        float(row["comparisons"]["prior_prepared_summary_gap"]["device_array_gap_reduction_over_prior_summary"])
        for row in results
    ]
    passed = (
        gate.get("status") == "pass"
        and correctness
        and len(passing) >= 2
        and max(gaps) <= 100.0
        and min(reductions) >= 10.0
    )
    details = {"passing_size_count": len(passing), "max_gap": max(gaps), "min_gap_reduction": min(reductions)}
    if not passed:
        return _fail(surface, "fixed_radius_product_boundary_floor_failed", details)
    return _ok(surface, 1.0 / max(gaps), details)


def _evaluate_closest_hit(path: Path) -> dict[str, Any]:
    surface = "v4_closest_hit_grouped_argmin_3d_device_arrays"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    ratios: list[float] = []
    for row in data.get("results", []):
        device = float(row["routes"]["device_array_frontdoor"]["median_s"])
        legacy = float(row["routes"]["legacy_host_materialize"]["median_s"])
        ratios.append(legacy / device)
    correctness = all(bool(row.get("correctness_passed")) for row in data.get("results", []))
    passed = correctness and len(ratios) == 3 and min(ratios) >= 1.0
    details = {"ratios": ratios, "min_ratio": min(ratios) if ratios else None, "correctness": correctness}
    if not passed:
        return _fail(surface, "closest_hit_grouped_argmin_floor_failed", details)
    return _ok(surface, min(ratios), details)


def _evaluate_any_hit(path: Path) -> dict[str, Any]:
    surface = "v4_ray_triangle_any_hit_flags_2d_device_arrays"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    results = data.get("results", [])
    correctness = all(bool(row.get("correctness_passed")) for row in results)
    hot_path_ok = all(
        row["routes"]["device_array_frontdoor"]["metadata"].get("host_materialization_in_hot_path") is False
        for row in results
    )
    measured_ratios = [
        float(row["comparison"]["torch_reference_to_device_frontdoor_ratio"])
        for row in results
        if row.get("comparison", {}).get("torch_reference_to_device_frontdoor_ratio") is not None
    ]
    passed = correctness and hot_path_ok and len(results) == 3 and measured_ratios and min(measured_ratios) >= 1.0
    details = {"measured_reference_ratios": measured_ratios, "correctness": correctness, "hot_path_ok": hot_path_ok}
    if not passed:
        return _fail(surface, "any_hit_flags_floor_failed", details)
    return _ok(surface, min(measured_ratios), details)


def _evaluate_grouped_i64(paths: tuple[Path, ...]) -> dict[str, Any]:
    surface = "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays"
    ratios: list[float] = []
    parity = True
    missing = [path.as_posix() for path in paths if not path.exists()]
    if missing:
        return _blocked(surface, f"missing_evidence:{','.join(missing)}", paths[0])
    for path in paths:
        data = _load(path)
        for row in data.get("results", []):
            parity = parity and bool(row.get("parity_passed"))
            ratios.append(float(row["comparison"]["legacy_host_output_over_device_output_median_speedup"]))
    passed = parity and len(ratios) == 6 and min(ratios) >= 1.0
    details = {"ratios": ratios, "min_ratio": min(ratios) if ratios else None, "parity": parity}
    if not passed:
        return _fail(surface, "grouped_i64_floor_failed", details)
    return _ok(surface, min(ratios), details)


def _evaluate_point_group(paths: tuple[Path, ...]) -> dict[str, Any]:
    surface = "v4_point_group_nearest_witness_2d_device_arrays"
    ratios: list[float] = []
    parity = True
    missing = [path.as_posix() for path in paths if not path.exists()]
    if missing:
        return _blocked(surface, f"missing_evidence:{','.join(missing)}", paths[0])
    for path in paths:
        data = _load(path)
        for row in data.get("results", []):
            parity = parity and bool(row.get("parity", {}).get("passed"))
            ratios.append(float(row["same_contract_ratio_legacy_host_rows_over_direct_device_output"]))
    passed = parity and len(ratios) == 4 and min(ratios) >= 1.0
    details = {"ratios": ratios, "min_ratio": min(ratios) if ratios else None, "parity": parity}
    if not passed:
        return _fail(surface, "point_group_floor_failed", details)
    return _ok(surface, min(ratios), details)


def _evaluate_weighted_sum(path: Path) -> dict[str, Any]:
    surface = "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    ratios = [
        float(row["comparison"]["host_materialization_over_device_resident_median_ratio"])
        for row in data.get("results", [])
    ]
    parity = all(bool(row.get("parity_passed")) for row in data.get("results", []))
    geomean = math.prod(ratios) ** (1.0 / len(ratios)) if ratios else 0.0
    hot_path = all(
        row["routes"]["device_output_frontdoor"].get("host_materialization_in_hot_path") is False
        and row["routes"]["device_output_frontdoor"].get("host_scalar_read_before_consumer") is False
        and row["routes"]["device_output_frontdoor"].get("weighted_sum_downloaded_to_host_in_hot_path") is False
        for row in data.get("results", [])
    )
    passed = parity and hot_path and len(ratios) == 4 and min(ratios) >= 1.20 and geomean >= 1.50
    details = {"ratios": ratios, "min_ratio": min(ratios) if ratios else None, "geomean": geomean, "parity": parity}
    if not passed:
        return _fail(surface, "weighted_sum_floor_failed", details)
    return _ok(surface, min(ratios), details)


def _evaluate_component_union(path: Path) -> dict[str, Any]:
    surface = "v4_fixed_radius_graph_component_union_3d_device_arrays"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    comparisons = data.get("comparisons", {})
    passed = (
        comparisons.get("all_variant_canonical_component_signatures_match") is True
        and float(comparisons.get("runner_vs_embree_hot_speedup", 0.0)) >= 1.20
        and float(comparisons.get("runner_vs_embree_wall_speedup", 0.0)) >= 1.20
        and float(comparisons.get("runner_vs_legacy_wall_speedup", 0.0)) >= 0.98
    )
    ratios = [
        float(comparisons.get("runner_vs_embree_hot_speedup", 0.0)),
        float(comparisons.get("runner_vs_embree_wall_speedup", 0.0)),
        float(comparisons.get("runner_vs_legacy_wall_speedup", 0.0)),
    ]
    details = {"ratios": ratios, "comparisons": comparisons}
    if not passed:
        return _fail(surface, "component_union_floor_failed", details)
    return _ok(surface, min(ratios), details)


def _evaluate_aabb(path: Path) -> dict[str, Any]:
    surface = "v4_aabb_index_query_2d_all_ops_count_prepared_runner"
    if not path.exists():
        return _blocked(surface, "missing_evidence", path)
    data = _load(path)
    comparison = data.get("comparison", {})
    pair = comparison.get("same_contract_backend_pair", {})
    median_ratio = float(pair.get("embree_over_optix_query_median", 0.0))
    embree_total = float(pair.get("embree_query_total_sec", 0.0))
    optix_total = float(pair.get("optix_query_total_sec", 0.0))
    total_ratio = embree_total / optix_total if optix_total else 0.0
    passed = (
        comparison.get("all_counts_match_cross_backend") is True
        and comparison.get("all_same_contract_family") is True
        and median_ratio >= 10.0
        and total_ratio >= 10.0
    )
    details = {"median_ratio": median_ratio, "total_ratio": total_ratio, "comparison": comparison}
    if not passed:
        return _fail(surface, "aabb_index_floor_failed", details)
    return _ok(surface, min(median_ratio, total_ratio), details)


def evaluate_v4_goal4639_scorecard(output_dir: Path) -> dict[str, Any]:
    freeze = validate_v4_goal4638_formal_scorecard_freeze()
    output_dir = output_dir.resolve()

    surface_results = (
        _evaluate_fixed_radius(output_dir / "fixed_radius_count_threshold.json"),
        _evaluate_closest_hit(output_dir / "closest_hit_grouped_argmin.json"),
        _evaluate_any_hit(output_dir / "ray_triangle_any_hit_flags.json"),
        _evaluate_grouped_i64(
            (
                output_dir / "primitive_grouped_i64_width1.json",
                output_dir / "primitive_grouped_i64_width16.json",
                output_dir / "primitive_grouped_i64_width256.json",
            )
        ),
        _evaluate_point_group(
            (
                output_dir / "point_group_nearest_witness_mixed4.json",
                output_dir / "point_group_nearest_witness_mixed6.json",
            )
        ),
        _evaluate_weighted_sum(output_dir / "ray_triangle_any_hit_weighted_sum.json"),
        _evaluate_component_union(output_dir / "fixed_radius_graph_component_union" / "summary.json"),
        _evaluate_aabb(output_dir / "aabb_index_all_ops_count.json"),
    )
    surface_map = {row["surface"]: row for row in surface_results}

    family_surface_map = {
        "rt_dbscan": (
            "v4_fixed_radius_count_threshold_2d_device_arrays",
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
        ),
        "raydb_style": (
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            "v4_closest_hit_grouped_argmin_3d_device_arrays",
            "v4_ray_triangle_any_hit_flags_2d_device_arrays",
        ),
        "triangle_counting": (
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
        ),
        "librts_spatial_index": ("v4_aabb_index_query_2d_all_ops_count_prepared_runner",),
        "hausdorff_xhd": (
            "v4_point_group_nearest_witness_2d_device_arrays",
            "v4_fixed_radius_count_threshold_2d_device_arrays",
        ),
        "robot_collision": ("v4_ray_triangle_any_hit_flags_2d_device_arrays",),
        "contact_manifold": ("v4_point_group_nearest_witness_2d_device_arrays",),
        "rtnn": ("v4_point_group_nearest_witness_2d_device_arrays",),
    }

    family_rows: list[dict[str, Any]] = []
    families = freeze["benchmark_families"]
    for family in families["release_in_scope_strong_operator"]:
        surfaces = family_surface_map[family]
        passed = all(surface_map[surface]["passed"] for surface in surfaces)
        ratios = [surface_map[surface]["representative_ratio"] for surface in surfaces if surface_map[surface]["representative_ratio"]]
        family_rows.append(
            {
                "family": family,
                "class": "release_in_scope_strong_operator",
                "surfaces": surfaces,
                "passed": passed,
                "representative_ratio_geomean": math.prod(ratios) ** (1.0 / len(ratios)) if ratios else None,
            }
        )
    for family in families["partial_operator_control"]:
        surfaces = family_surface_map[family]
        passed = all(surface_map[surface]["passed"] for surface in surfaces)
        family_rows.append(
            {
                "family": family,
                "class": "partial_operator_control",
                "surfaces": surfaces,
                "passed": passed,
                "excluded_from_release_geomean": True,
            }
        )
    for family in families["deferred_excluded"]:
        family_rows.append(
            {
                "family": family,
                "class": "deferred_excluded",
                "surfaces": (),
                "passed": None,
                "excluded_from_release_geomean": True,
                "reason": "no V4.0 measured generic operator surface in frozen Goal4638 scorecard",
            }
        )

    strong_rows = [row for row in family_rows if row["class"] == "release_in_scope_strong_operator"]
    partial_rows = [row for row in family_rows if row["class"] == "partial_operator_control"]
    deferred_rows = [row for row in family_rows if row["class"] == "deferred_excluded"]
    strong_passed = sum(1 for row in strong_rows if row["passed"])
    surface_passed = sum(1 for row in surface_results if row["passed"])
    surface_failed = [row for row in surface_results if not row["passed"]]
    incomplete = any(row["status"] == "blocked_incomplete" for row in surface_results)
    strong_ratios = [row["representative_ratio_geomean"] for row in strong_rows if row["representative_ratio_geomean"]]
    strong_geomean = math.prod(strong_ratios) ** (1.0 / len(strong_ratios)) if strong_ratios else None

    if incomplete:
        recommendation = V4_GOAL4639_DECISION_IF_BLOCKED
    elif strong_passed == len(strong_rows) and surface_passed == len(surface_results):
        recommendation = V4_GOAL4639_DECISION_IF_PASS
    else:
        recommendation = V4_GOAL4639_DECISION_IF_FAIL

    return {
        "status": V4_GOAL4639_STATUS,
        "recommendation": recommendation,
        "freeze_decision": freeze["decision"],
        "surface_results": surface_results,
        "family_rows": tuple(family_rows),
        "summary": {
            "strong_passed": strong_passed,
            "strong_failed": len(strong_rows) - strong_passed,
            "strong_total": len(strong_rows),
            "surface_passed": surface_passed,
            "surface_failed": len(surface_results) - surface_passed,
            "surface_total": len(surface_results),
            "partial_passed": sum(1 for row in partial_rows if row["passed"]),
            "partial_failed": sum(1 for row in partial_rows if row["passed"] is False),
            "partial_total": len(partial_rows),
            "deferred_excluded": len(deferred_rows),
            "strong_representative_ratio_geomean": strong_geomean,
            "failed_surfaces": tuple(row["surface"] for row in surface_failed),
        },
        "release_authorized": False,
        "release_candidate_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4639_scorecard_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["status"] != V4_GOAL4639_STATUS:
        raise ValueError("Goal4639 status drift")
    if payload["summary"]["surface_total"] != 8:
        raise ValueError("Goal4639 must evaluate all 8 measured surfaces")
    if payload["summary"]["strong_total"] != 4:
        raise ValueError("Goal4639 must evaluate all 4 strong families")
    if payload["summary"]["partial_total"] != 4:
        raise ValueError("Goal4639 must record all 4 partial controls")
    if payload["summary"]["deferred_excluded"] != 2:
        raise ValueError("Goal4639 must record both deferred/excluded families")
    for flag in (
        "release_authorized",
        "release_candidate_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if payload[flag]:
            raise ValueError(f"Goal4639 must not authorize {flag}")
    return payload


__all__ = [
    "V4_GOAL4639_STATUS",
    "V4_GOAL4639_DECISION_IF_PASS",
    "V4_GOAL4639_DECISION_IF_FAIL",
    "V4_GOAL4639_DECISION_IF_BLOCKED",
    "V4Goal4639Run",
    "v4_goal4639_run_plan",
    "evaluate_v4_goal4639_scorecard",
    "validate_v4_goal4639_scorecard_payload",
]
