#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1190 next RTX pod contract manifest supersession"


ROWS: tuple[dict[str, Any], ...] = (
    {
        "app": "database_analytics",
        "status": "local_dry_run_required",
        "claim_contract": "prepared compact-summary DB sales-risk traversal/filter/grouping summary only",
        "phase_to_compare": "warm/query compact-summary timing",
        "scale_choice": {"copies": 30000, "iterations": 10},
        "optix_command": "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/database_compact_summary_optix.json",
        "baseline_command": "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/database_compact_summary_embree.json",
        "boundary": "no whole-app speedup claim, SQL, DBMS, row-materializing, or full dashboard claim",
    },
    {
        "app": "graph_analytics",
        "status": "local_dry_run_required",
        "claim_contract": "visibility_edges prepared any-hit summary only",
        "phase_to_compare": "Embree graph_phase_totals_sec.query_visibility_pair_rows_sec versus OptiX prepared visibility count/query phase",
        "scale_choice": {"copies": 30000},
        "optix_command": "python3 scripts/goal889_graph_visibility_optix_gate.py --copies 30000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/graph_visibility_edges_optix.json",
        "baseline_command": "python3 examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 30000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/graph_visibility_edges_embree.json",
        "boundary": "no whole-app speedup claim, BFS orchestration, triangle set-intersection, shortest-path, distributed graph, or graph database claim",
    },
    {
        "app": "road_hazard_screening",
        "status": "local_dry_run_required",
        "claim_contract": "prepared native road-hazard compact hit-count summary only",
        "phase_to_compare": "prepared segment/polygon hit-count query phase versus Embree summary traversal phase",
        "scale_choice": {"copies": 20000, "iterations": 5},
        "optix_command": "python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/road_hazard_native_summary_optix.json",
        "baseline_command": "python3 examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/road_hazard_native_summary_embree.json",
        "boundary": "no whole-app speedup claim, full GIS, routing, default app, or broad road-hazard claim",
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "status": "local_dry_run_required",
        "claim_contract": "native-assisted LSI/PIP candidate discovery only",
        "phase_to_compare": "run_phases.rt_candidate_discovery_sec; exact area continuation excluded",
        "scale_choice": {"copies": 20000, "chunk_copies": 100},
        "optix_command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_optix.json",
        "baseline_command": "python3 examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_embree.json",
        "boundary": "no whole-app speedup claim, exact area, overlay matrix, or monolithic polygon-area claim",
    },
    {
        "app": "polygon_set_jaccard",
        "status": "local_dry_run_required",
        "claim_contract": "safe-chunk native-assisted LSI/PIP candidate discovery only",
        "phase_to_compare": "run_phases.rt_candidate_discovery_sec; exact set-area/Jaccard continuation excluded",
        "scale_choice": {"copies": 8192, "chunk_copies": 1024},
        "optix_command": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 1024 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_optix.json",
        "baseline_command": "python3 examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py --backend embree --copies 8192 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_embree.json",
        "boundary": "no whole-app speedup claim, exact Jaccard, exact set-area, or whole polygon-set app claim",
    },
    {
        "app": "hausdorff_distance",
        "status": "local_dry_run_required",
        "claim_contract": "prepared Hausdorff <= radius decision only",
        "phase_to_compare": "prepared threshold query phase versus Embree directed_summary traversal/reduction",
        "scale_choice": {"copies": 200000, "iterations": 10, "radius": 0.4, "watch_item": "may still be below timing floor; local dry-run must adjust if needed"},
        "optix_command": "python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 200000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_optix.json",
        "baseline_command": "python3 examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend embree --copies 200000 --embree-result-mode directed_summary --hausdorff-threshold 0.4 > docs/reports/goal1190_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_embree.json",
        "boundary": "no whole-app speedup claim, exact Hausdorff distance, nearest-neighbor ranking, or KNN-row claim",
    },
)


def build_manifest() -> dict[str, Any]:
    blockers: list[str] = []
    for row in ROWS:
        if row["status"] != "local_dry_run_required":
            blockers.append(f"{row['app']} status must remain local_dry_run_required")
        if not row["optix_command"] or not row["baseline_command"]:
            blockers.append(f"{row['app']} missing command")
        if "whole-app speedup claim" not in row["boundary"]:
            blockers.append(f"{row['app']} missing whole-app boundary")
        if not row["phase_to_compare"]:
            blockers.append(f"{row['app']} missing phase-to-compare")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "supersedes": "Goal1189 blocked baseline-harness classification for graph and polygon rows",
        "row_count": len(ROWS),
        "local_dry_run_required_count": len(ROWS),
        "pod_ready_now": False,
        "rows": list(ROWS),
        "blockers": blockers,
        "local_next_step": (
            "Run small local command-shape dry-runs for all baseline commands, then build "
            "a pod executor only after the JSON schemas and comparable phase fields are verified."
        ),
        "pod_recommendation": (
            "Do not use a paid pod yet. The manifest is now command-complete, but local "
            "dry-runs and schema checks must pass before cloud execution."
        ),
        "boundary": (
            "This supersession changes planning status only. It does not authorize public "
            "RTX speedup wording, release, tagging, or cloud execution by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1190 Next RTX Pod Contract Manifest Supersession",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- supersedes: {payload['supersedes']}",
        f"- rows: `{payload['row_count']}`",
        f"- local dry-run required rows: `{payload['local_dry_run_required_count']}`",
        f"- pod ready now: `{payload['pod_ready_now']}`",
        "",
        "## Local Next Step",
        "",
        payload["local_next_step"],
        "",
        "## Pod Recommendation",
        "",
        payload["pod_recommendation"],
        "",
        "## Rows",
        "",
        "| App | Status | Contract | Phase to compare | Scale | OptiX command | Baseline command | Boundary |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        scale = json.dumps(row["scale_choice"], sort_keys=True)
        lines.append(
            f"| `{row['app']}` | `{row['status']}` | {row['claim_contract']} | {row['phase_to_compare']} | "
            f"`{scale}` | `{row['optix_command']}` | `{row['baseline_command']}` | {row['boundary']} |"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1190 next RTX pod contract supersession.")
    parser.add_argument("--output-json", default="docs/reports/goal1190_next_rtx_pod_contract_manifest_supersession_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1190_next_rtx_pod_contract_manifest_supersession_2026-04-30.md")
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
