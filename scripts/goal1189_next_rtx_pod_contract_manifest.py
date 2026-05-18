#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1189 next RTX pod contract manifest"


ROWS: tuple[dict[str, Any], ...] = (
    {
        "app": "database_analytics",
        "status": "pod_ready_after_local_dry_run",
        "claim_contract": "prepared compact-summary DB sales-risk traversal/filter/grouping summary only",
        "scale_choice": {"copies": 30000, "iterations": 10, "reason": "Goal1184 copies=20000 was 0.09356s, just below 0.1s; 30000 should clear floor with margin"},
        "optix_command": "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/database_compact_summary_optix.json",
        "baseline_command": "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/database_compact_summary_embree.json",
        "boundary": "no SQL, DBMS, row-materializing, full dashboard, or whole-app speedup claim",
    },
    {
        "app": "graph_analytics",
        "status": "needs_baseline_harness_before_pod",
        "claim_contract": "visibility_edges prepared any-hit summary plus native graph-ray candidate path only",
        "scale_choice": {"copies": 30000, "reason": "raise work above previous copies=20000 while preserving summary semantics"},
        "optix_command": "python3 scripts/goal889_graph_visibility_optix_gate.py --copies 30000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/graph_visibility_edges_optix.json",
        "baseline_command": "",
        "missing_work": "add a same-contract CPU/Embree summary baseline artifact for visibility_edges that emits comparable blocked/visible counts and timing without full row materialization",
        "boundary": "no whole-app speedup claim, whole graph-system, BFS orchestration, triangle set-intersection, or distributed graph claim",
    },
    {
        "app": "road_hazard_screening",
        "status": "pod_ready_after_local_dry_run",
        "claim_contract": "prepared native road-hazard compact hit-count summary only",
        "scale_choice": {"copies": 20000, "iterations": 5, "reason": "Goal1184 already cleared floor with median 0.108167s"},
        "optix_command": "python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/road_hazard_native_summary_optix.json",
        "baseline_command": "python3 examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary",
        "boundary": "no whole-app speedup claim, full GIS, routing, default app, or broad road-hazard speedup claim",
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "status": "needs_candidate_baseline_harness_before_pod",
        "claim_contract": "native-assisted LSI/PIP candidate discovery only",
        "scale_choice": {"copies": 20000, "chunk_copies": 100, "reason": "Goal1184 candidate-discovery phase was 2.950786s and reviewable if baseline contract is split cleanly"},
        "optix_command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_optix.json",
        "baseline_command": "",
        "missing_work": "add a same-contract candidate-discovery-only CPU/Embree baseline; full exact area continuation is not an acceptable baseline for the candidate-only claim",
        "boundary": "no whole-app speedup claim, exact area, overlay matrix, or monolithic polygon-area speedup claim",
    },
    {
        "app": "polygon_set_jaccard",
        "status": "needs_candidate_baseline_harness_before_pod",
        "claim_contract": "safe-chunk native-assisted LSI/PIP candidate discovery only",
        "scale_choice": {"copies": 8192, "chunk_copies": 1024, "reason": "Goal1262 supersedes the older chunk-512 assumption; chunk 1024 passed parity on the live RTX A5000 rerun"},
        "optix_command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 1024 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_optix.json",
        "baseline_command": "",
        "missing_work": "add a same-contract candidate-discovery-only CPU/Embree baseline; exact set-area/Jaccard continuation remains outside the claim",
        "boundary": "no exact Jaccard, exact set-area, or whole app speedup claim",
    },
    {
        "app": "hausdorff_distance",
        "status": "pod_ready_after_local_dry_run",
        "claim_contract": "prepared Hausdorff <= radius decision only",
        "scale_choice": {"copies": 200000, "iterations": 10, "radius": 0.4, "reason": "Goal1184 copies=20000 was 0.001296s, far below floor; 10x scale targets reviewable timing while preserving threshold semantics"},
        "optix_command": "python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 200000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_optix.json",
        "baseline_command": "python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend embree --copies 200000 --embree-result-mode directed_summary --hausdorff-threshold 0.4",
        "boundary": "no exact Hausdorff distance, nearest-neighbor ranking, KNN rows, or whole-app speedup claim",
    },
)


def build_manifest() -> dict[str, Any]:
    ready = [row for row in ROWS if row["status"] == "pod_ready_after_local_dry_run"]
    needs_harness = [row for row in ROWS if row["status"] != "pod_ready_after_local_dry_run"]
    blockers = []
    for row in ROWS:
        if not row["optix_command"]:
            blockers.append(f"{row['app']} missing optix command")
        if row["status"] == "pod_ready_after_local_dry_run" and not row["baseline_command"]:
            blockers.append(f"{row['app']} missing baseline command")
        if "whole-app speedup claim" not in row["boundary"] and "whole app speedup claim" not in row["boundary"]:
            blockers.append(f"{row['app']} missing whole-app boundary")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "row_count": len(ROWS),
        "pod_ready_after_local_dry_run_count": len(ready),
        "needs_baseline_harness_count": len(needs_harness),
        "ready_apps": [row["app"] for row in ready],
        "needs_harness_apps": [row["app"] for row in needs_harness],
        "rows": list(ROWS),
        "blockers": blockers,
        "pod_recommendation": (
            "Do not run the next public-wording pod batch yet. First add candidate-only "
            "baseline harnesses for graph visibility, polygon pair overlap, and polygon "
            "Jaccard; then run local dry-runs for all six rows and package one pod batch."
        ),
        "boundary": (
            "This manifest defines contracts and commands only. It does not authorize public "
            "RTX speedup wording, release, tagging, or cloud execution by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1189 Next RTX Pod Contract Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- rows: `{payload['row_count']}`",
        f"- pod-ready after local dry run: `{payload['pod_ready_after_local_dry_run_count']}`",
        f"- needs baseline harness: `{payload['needs_baseline_harness_count']}`",
        "",
        "## Recommendation",
        "",
        payload["pod_recommendation"],
        "",
        "## Rows",
        "",
        "| App | Status | Contract | Scale | OptiX command | Baseline command / missing work | Boundary |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        scale = json.dumps(row["scale_choice"], sort_keys=True)
        baseline = row["baseline_command"] or row.get("missing_work", "")
        lines.append(
            f"| `{row['app']}` | `{row['status']}` | {row['claim_contract']} | `{scale}` | "
            f"`{row['optix_command']}` | `{baseline}` | {row['boundary']} |"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build next RTX pod contract manifest.")
    parser.add_argument("--output-json", default="docs/reports/goal1189_next_rtx_pod_contract_manifest_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1189_next_rtx_pod_contract_manifest_2026-04-30.md")
    args = parser.parse_args()

    payload = build_manifest()
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "json": str(output_json), "md": str(output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
