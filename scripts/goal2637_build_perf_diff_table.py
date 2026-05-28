#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal2637_all_benchmark_perf_diffs_2026-05-27.json"

STANDARD_ARTIFACT = ROOT / "docs" / "reports" / "goal2634_full_standard_prepared_contact_pod" / "summary_slim.json"
STRENGTHENED_ARTIFACT = ROOT / "docs" / "reports" / "goal2636_strengthened_rows_pod_fixed" / "summary.json"
STRENGTHENED_STRESS_ARTIFACT = ROOT / "docs" / "reports" / "goal2636_strengthened_rows_stress_pod_fixed" / "summary.json"
ROBOT_STRESS_ARTIFACT = ROOT / "docs" / "reports" / "goal2626_robot_collision_stress_pod_32768x512" / "compact_summary.json"
CONTACT_STRESS_ARTIFACT = ROOT / "docs" / "reports" / "goal2626_contact_aabb_collect_stress_pod_65536" / "summary.json"
RTNN_LARGE_ARTIFACT = ROOT / "docs" / "reports" / "goal2628_rtnn_large_envfixed_pod" / "summary.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _summarize_speedups(rows: list[dict[str, Any]]) -> dict[str, Any]:
    speedups = [float(row["optix_speedup_vs_embree"]) for row in rows]
    return {
        "row_count": len(speedups),
        "optix_win_count": sum(1 for value in speedups if value > 1.0),
        "min_speedup": min(speedups),
        "median_speedup": statistics.median(speedups),
        "geomean_speedup": math.exp(sum(math.log(value) for value in speedups) / len(speedups)),
        "max_speedup": max(speedups),
    }


def _ratio_rows(source_matrix: str, artifact: Path, ratios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ratio in ratios:
        rows.append(
            {
                "source_matrix": source_matrix,
                "artifact": _relative(artifact),
                "app_id": ratio["app_id"],
                "comparison_group": ratio["comparison_group"],
                "embree_sec": float(ratio["embree_sec"]),
                "optix_sec": float(ratio["optix_sec"]),
                "optix_speedup_vs_embree": float(ratio["optix_speedup_vs_embree"]),
                "metric_sources": ratio.get("metric_sources", {}),
            }
        )
    return rows


def _supporting_stress_rows() -> list[dict[str, Any]]:
    robot = _load_json(ROBOT_STRESS_ARTIFACT)
    contact = _load_json(CONTACT_STRESS_ARTIFACT)
    rtnn = _load_json(RTNN_LARGE_ARTIFACT)
    rtnn_ratio = rtnn["ratios"][0]
    return [
        {
            "source_matrix": "supporting_stress",
            "artifact": _relative(ROBOT_STRESS_ARTIFACT),
            "app_id": "robot_collision",
            "comparison_group": "prepared_collision_flags_32768x512_stress",
            "embree_sec": float(robot["embree_sec"]),
            "optix_sec": float(robot["optix_sec"]),
            "optix_speedup_vs_embree": float(robot["optix_speedup_vs_embree"]),
            "metric_sources": {"embree": "embree_sec", "optix": "optix_sec"},
        },
        {
            "source_matrix": "supporting_stress",
            "artifact": _relative(CONTACT_STRESS_ARTIFACT),
            "app_id": "contact_manifold",
            "comparison_group": "contact_aabb_collect_grid_65536",
            "embree_sec": float(contact["cpu_total_sec"]),
            "optix_sec": float(contact["optix_total_sec"]),
            "optix_speedup_vs_embree": float(contact["optix_speedup_vs_cpu_discovery"]),
            "metric_sources": {"embree": "cpu_total_sec", "optix": "optix_total_sec"},
        },
        {
            "source_matrix": "supporting_stress",
            "artifact": _relative(RTNN_LARGE_ARTIFACT),
            "app_id": "rtnn",
            "comparison_group": rtnn_ratio["comparison_group"],
            "embree_sec": float(rtnn_ratio["embree_sec"]),
            "optix_sec": float(rtnn_ratio["optix_sec"]),
            "optix_speedup_vs_embree": float(rtnn_ratio["optix_speedup_vs_embree"]),
            "metric_sources": rtnn_ratio.get("metric_sources", {}),
        },
    ]


def _optix_only_rows(strengthened: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in strengthened["rows"]:
        if row["app_id"] != "hausdorff_xhd":
            continue
        if not row["case_id"].startswith("hausdorff_optix_exact_grouped_seeded_pruned"):
            continue
        rows.append(
            {
                "source_matrix": "optix_only",
                "artifact": _relative(STRENGTHENED_ARTIFACT),
                "app_id": row["app_id"],
                "case_id": row["case_id"],
                "backend": row["backend"],
                "optix_sec": float(row["primary_metric_sec"]),
                "metric_source": row["primary_metric_source"],
                "why_not_ratioed": "No same exact-witness Embree route in the current harness.",
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    standard = _load_json(STANDARD_ARTIFACT)
    strengthened = _load_json(STRENGTHENED_ARTIFACT)
    stress = _load_json(STRENGTHENED_STRESS_ARTIFACT)
    standard_rows = _ratio_rows("goal2634_standard", STANDARD_ARTIFACT, standard["ratios"])
    strengthened_rows = _ratio_rows("goal2636_strengthened", STRENGTHENED_ARTIFACT, strengthened["ratios"])
    stress_rows = _ratio_rows("goal2636_stress", STRENGTHENED_STRESS_ARTIFACT, stress["ratios"])
    supporting_rows = _supporting_stress_rows()
    benchmark_apps = sorted({row["app_id"] for row in standard_rows})
    return {
        "goal": "Goal2637",
        "status": "internal measured performance diffs; not public speedup wording",
        "source_artifacts": {
            "standard": _relative(STANDARD_ARTIFACT),
            "strengthened": _relative(STRENGTHENED_ARTIFACT),
            "strengthened_stress": _relative(STRENGTHENED_STRESS_ARTIFACT),
            "supporting_stress": [
                _relative(ROBOT_STRESS_ARTIFACT),
                _relative(CONTACT_STRESS_ARTIFACT),
                _relative(RTNN_LARGE_ARTIFACT),
            ],
        },
        "benchmark_app_count": len(benchmark_apps),
        "benchmark_apps": benchmark_apps,
        "standard_summary": _summarize_speedups(standard_rows),
        "strengthened_summary": _summarize_speedups(strengthened_rows),
        "strengthened_stress_summary": _summarize_speedups(stress_rows),
        "standard_rows": standard_rows,
        "strengthened_rows": strengthened_rows,
        "strengthened_stress_rows": stress_rows,
        "supporting_stress_rows": supporting_rows,
        "optix_only_rows": _optix_only_rows(strengthened),
        "claim_boundary": {
            "internal_baseline_only": True,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "exact_subpath_boundaries_required": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Goal2637 machine-readable benchmark perf diff table.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
