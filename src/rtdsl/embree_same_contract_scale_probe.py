from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EMBREE_SAME_CONTRACT_SCALE_PROBE_VERSION = "rtdl.v2_11.embree_same_contract_scale_probe.goal4344.v1"
EMBREE_SAME_CONTRACT_SCALE_PROBE_STATUS = (
    "internal_embree_same_contract_scale_probe_not_public_speedup_authorization"
)
EMBREE_SAME_CONTRACT_SCALE_PROBE_CLAIM_BOUNDARY = (
    "Goal4344 records fresh Embree CPU scale artifacts for the five rows that "
    "Goal4343 previously marked as needing same-contract scale evidence. It "
    "does not authorize release action, public speedup wording, whole-app "
    "acceleration wording, Intel GPU performance wording, paper reproduction "
    "wording, true-zero-copy wording, automatic partner selection, or "
    "app-specific native-engine logic."
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROBE_DIR = ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe"


CASE_SPECS: dict[str, dict[str, Any]] = {
    "hausdorff_xhd": {
        "artifact_name": "hausdorff_embree_threshold_1024",
        "comparison_class": "same_contract_query_ratio_candidate",
        "contract": "directed_threshold_prepared_fixed_radius_count",
        "scale": "copies=1024, threshold=0.25, repeat=5, warmup=1",
        "metric_name": "max_directed_query_fixed_radius_threshold_reached_count_sec",
        "boundary": (
            "Same prepared fixed-radius threshold decision contract as the current "
            "OptiX row. This is still smoke/internal timing evidence."
        ),
    },
    "robot_collision": {
        "artifact_name": "robot_embree_prepared_buffers_1024_128_4_50000",
        "comparison_class": "same_scene_query_scale_output_residency_boundary",
        "contract": "prepared_triangle_scene_grouped_segment_any_hit_flags",
        "scale": "poses=1024, obstacles=128, links=4, repeat=50000, warmup=100",
        "metric_name": "tail_median_traversal_sec",
        "boundary": (
            "Same scene/query scale as the current OptiX row, but Embree returns "
            "host compact flags while the current OptiX row uses an OptiX-only "
            "device-count path. Traversal phase is useful internally; total/output "
            "ratios are not clean backend ratios."
        ),
    },
    "contact_manifold": {
        "artifact_name": "contact_embree_grid64_witness128",
        "comparison_class": "same_contract_query_ratio_candidate",
        "contract": "native_collect_k_bounded_witness_rows",
        "scale": "grid=64, witness_capacity=128, repeat=3",
        "metric_name": "native_collect_elapsed_sec",
        "boundary": "Same bounded collect-k contract, grid size, witness capacity, and repeat count as OptiX.",
    },
    "raydb_style": {
        "artifact_name": "raydb_embree_count_generated_262144_1024",
        "comparison_class": "same_scale_prepared_residency_boundary",
        "contract": "raydb_style_generated_grouped_count_primitive_first",
        "scale": "generated_rows=262144, generated_groups=1024, repeat=5000, warmup=50",
        "metric_name": "native_grouped_reduction_traversal_sec",
        "boundary": (
            "Same generated row/group scale and grouped-count result contract as the "
            "current OptiX row, but the OptiX scale row is a prepared resident "
            "v2.5 primitive-first path while this Embree row is a non-resident "
            "native grouped-reduction run. Clean end-to-end ratios are withheld."
        ),
    },
    "triangle_counting": {
        "artifact_name": "triangle_embree_rtgraph2a1_2048",
        "comparison_class": "same_contract_query_ratio_candidate",
        "contract": "rt_graph_2a1_generic_ray_triangle_any_hit",
        "scale": "fixture=degree_oriented_two_triangles, rt_graph_copies=2048, repeat=3, warmup=1",
        "metric_name": "query_median_ms",
        "boundary": "Same RT-Graph 2A1 fixture, copy count, detail mode, repeat, and warmup as OptiX.",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _dig(payload: dict[str, Any], *keys: str) -> Any:
    node: Any = payload
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            raise KeyError("missing field: " + ".".join(keys))
        node = node[key]
    return node


def _float(payload: dict[str, Any], *keys: str) -> float:
    return float(_dig(payload, *keys))


def _status_for(base: Path, name: str) -> dict[str, Any]:
    return _load_json(base / f"{name}.status.json")


def _artifact_for(base: Path, name: str) -> dict[str, Any]:
    return _load_json(base / f"{name}.json")


def _hausdorff_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    ab = _float(payload, "directed_a_to_b", "run_phases", "query_fixed_radius_threshold_reached_count_sec")
    ba = _float(payload, "directed_b_to_a", "run_phases", "query_fixed_radius_threshold_reached_count_sec")
    return {
        "value": max(ab, ba),
        "unit": "sec",
        "secondary": {
            "directed_a_to_b_sec": ab,
            "directed_b_to_a_sec": ba,
            "query_repeat": int(_dig(payload, "directed_a_to_b", "run_phases", "query_repeat")),
            "query_warmup": int(_dig(payload, "directed_a_to_b", "run_phases", "query_warmup")),
        },
        "correctness": {
            "matches_oracle": bool(payload.get("matches_oracle")),
            "oracle_decision_matches": bool(payload.get("oracle_decision_matches")),
        },
    }


def _robot_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": _float(payload, "tail_medians", "phase_timing_seconds", "traversal"),
        "unit": "sec",
        "secondary": {
            "tail_total_run_sec": _float(payload, "tail_medians", "total_run_seconds"),
            "measured_traversal_total_sec": _float(
                payload,
                "run_summary",
                "phase_timing_seconds",
                "traversal",
                "total_sec",
            ),
            "measured_total_run_sec": _float(payload, "run_summary", "total_run_seconds", "total_sec"),
            "group_count": int(_dig(payload, "case_shape", "group_count")),
            "segment_count": int(_dig(payload, "case_shape", "segment_count")),
        },
        "correctness": {
            "probe_reference_validated": bool(_dig(payload, "reuse_metadata", "probe_reference_validated")),
            "all_run_signatures_identical": bool(_dig(payload, "reuse_metadata", "all_run_signatures_identical")),
            "no_probe_reference_matches_current_optix_scale_policy": True,
        },
    }


def _contact_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": _float(payload, "native_collect_elapsed_sec"),
        "unit": "sec",
        "secondary": {
            "native_collect_min_sec": _float(payload, "native_collect_min_sec"),
            "native_collect_max_sec": _float(payload, "native_collect_max_sec"),
            "native_collect_total_sec": _float(payload, "native_collect_total_sec"),
            "repeat_count": int(payload.get("repeat_count", payload.get("native_collect_repeat_count", 0))),
            "witness_capacity": int(payload.get("witness_capacity", 0)),
        },
        "correctness": {
            "matches_cpu_reference": bool(payload.get("matches_cpu_reference")),
            "complete_candidate_coverage": bool(payload.get("complete_candidate_coverage")),
            "overflowed": bool(payload.get("overflowed")),
        },
    }


def _raydb_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": _float(payload, "metadata", "timings", "traversal"),
        "unit": "sec",
        "secondary": {
            "elapsed_sec": _float(payload, "elapsed_sec"),
            "row_count": int(payload.get("row_count", 0)),
            "triangle_count": int(_dig(payload, "metadata", "triangle_count")),
            "ray_count": int(_dig(payload, "metadata", "ray_count")),
            "materialization_sec": _float(
                payload,
                "metadata",
                "v2_4_phase_timing",
                "phases_sec",
                "materialization",
            ),
        },
        "correctness": {
            "matches_cpu_reference": bool(payload.get("matches_cpu_reference")),
            "embree_same_contract_baseline": bool(_dig(payload, "metadata", "embree_same_contract_baseline")),
        },
    }


def _triangle_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "value": _float(payload, "timing_ms", "query_median_ms"),
        "unit": "ms",
        "secondary": {
            "query_min_ms": _float(payload, "timing_ms", "query_min_ms"),
            "query_max_ms": _float(payload, "timing_ms", "query_max_ms"),
            "query_repeat": int(_dig(payload, "timing_ms", "query_repeat")),
            "query_warmup": int(_dig(payload, "timing_ms", "query_warmup")),
            "primitive_count": int(payload.get("primitive_count", 0)),
            "ray_count": int(payload.get("ray_count", 0)),
        },
        "correctness": {
            "triangle_count_matches_oracle": bool(payload.get("triangle_count_matches_oracle")),
            "generic_rt_weighted_triangle_count": int(payload.get("generic_rt_weighted_triangle_count", -1)),
            "oracle_triangle_count": int(payload.get("oracle_triangle_count", -2)),
        },
    }


METRIC_EXTRACTORS = {
    "hausdorff_xhd": _hausdorff_metrics,
    "robot_collision": _robot_metrics,
    "contact_manifold": _contact_metrics,
    "raydb_style": _raydb_metrics,
    "triangle_counting": _triangle_metrics,
}


def embree_same_contract_scale_probe(*, probe_dir: Path | None = None) -> dict[str, Any]:
    base = probe_dir or DEFAULT_PROBE_DIR
    summary = _load_json(base / "summary.json")
    summary_cases = {case["name"]: case for case in summary.get("cases", [])}
    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for app, spec in CASE_SPECS.items():
        name = str(spec["artifact_name"])
        status = _status_for(base, name)
        artifact = _artifact_for(base, name)
        case_summary = summary_cases.get(name)
        if case_summary is None:
            errors.append(f"{app}: missing case in summary.json")
            case_summary = {}
        if int(status.get("status", -1)) != 0:
            errors.append(f"{app}: probe process status was not zero")
        if case_summary.get("json_parseable") is not True:
            errors.append(f"{app}: summary did not mark JSON parseable")

        extracted = METRIC_EXTRACTORS[app](artifact)
        correctness = dict(extracted["correctness"])
        if app == "hausdorff_xhd":
            if not (correctness["matches_oracle"] and correctness["oracle_decision_matches"]):
                errors.append(f"{app}: oracle parity failed")
        elif app == "robot_collision":
            if not correctness["all_run_signatures_identical"]:
                errors.append(f"{app}: repeated signatures were not identical")
        elif app == "contact_manifold":
            if not (correctness["matches_cpu_reference"] and correctness["complete_candidate_coverage"]):
                errors.append(f"{app}: CPU reference or coverage parity failed")
            if correctness["overflowed"]:
                errors.append(f"{app}: collect-k overflowed")
        elif app == "raydb_style":
            if not (correctness["matches_cpu_reference"] and correctness["embree_same_contract_baseline"]):
                errors.append(f"{app}: CPU reference or Embree baseline flag failed")
        elif app == "triangle_counting":
            if not correctness["triangle_count_matches_oracle"]:
                errors.append(f"{app}: triangle oracle parity failed")
            if correctness["generic_rt_weighted_triangle_count"] != correctness["oracle_triangle_count"]:
                errors.append(f"{app}: weighted triangle count did not match oracle")

        rows.append(
            {
                "app": app,
                "artifact_name": name,
                "artifact_path": _relative(base / f"{name}.json"),
                "status_path": _relative(base / f"{name}.status.json"),
                "stderr_path": _relative(base / f"{name}.stderr"),
                "process_status": int(status.get("status", -1)),
                "wall_sec": int(status.get("wall_sec", case_summary.get("wall_sec", -1))),
                "backend": artifact.get("backend"),
                "mode": artifact.get("mode"),
                "comparison_class": spec["comparison_class"],
                "contract": spec["contract"],
                "scale": spec["scale"],
                "metric_name": spec["metric_name"],
                "metric_value": extracted["value"],
                "metric_unit": extracted["unit"],
                "secondary_metrics": extracted["secondary"],
                "correctness": correctness,
                "boundary": spec["boundary"],
                "query_ratio_candidate": spec["comparison_class"] == "same_contract_query_ratio_candidate",
                "clean_end_to_end_ratio_authorized": False,
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )

    if summary.get("all_status_zero") is not True:
        errors.append("summary.json did not report all_status_zero")

    query_ratio_candidates = [row for row in rows if row["query_ratio_candidate"]]
    boundary_limited = [row for row in rows if not row["query_ratio_candidate"]]
    return {
        "version": EMBREE_SAME_CONTRACT_SCALE_PROBE_VERSION,
        "status": EMBREE_SAME_CONTRACT_SCALE_PROBE_STATUS,
        "claim_boundary": EMBREE_SAME_CONTRACT_SCALE_PROBE_CLAIM_BOUNDARY,
        "source_dir": _relative(base),
        "rows": tuple(rows),
        "summary": {
            "case_count": len(rows),
            "embree_scale_artifact_count": len(rows),
            "same_contract_query_ratio_candidate_count": len(query_ratio_candidates),
            "boundary_limited_scale_artifact_count": len(boundary_limited),
            "all_status_zero": bool(summary.get("all_status_zero")),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "intel_gpu_performance_claim_authorized": False,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "intel_gpu_performance_claim_authorized": False,
    }


def validate_embree_same_contract_scale_probe() -> dict[str, Any]:
    return embree_same_contract_scale_probe()["validation"]
