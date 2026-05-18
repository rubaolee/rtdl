#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1197 OptiX slower-app investigation manifest"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal1197_optix_slower_app_investigation_manifest_2026-04-30.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal1197_optix_slower_app_investigation_manifest_2026-04-30.md"


SLOWER_APPS: tuple[dict[str, Any], ...] = (
    {
        "app": "database_analytics",
        "observed_ratio_embree_over_optix": 0.791844,
        "hypothesis": "OptiX traversal is real, but compact-summary timing may be dominated by Python/ctypes packing, candidate bitset transfer, or grouping continuation overhead.",
        "scales": [
            {"copies": 30000, "iterations": 10},
            {"copies": 100000, "iterations": 10},
            {"copies": 300000, "iterations": 5},
        ],
        "phase_fields": [
            "results.0.prepared_session_warm_query_sec.median_sec",
            "results.0.prepared_session_prepare_sec.median_sec",
            "results.0.one_shot_total_sec.median_sec",
        ],
        "commands": [
            {
                "label": "db_embree_scale_sweep",
                "template": "python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies {copies} --iterations {iterations} --output-mode compact_summary --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
            {
                "label": "db_optix_scale_sweep",
                "template": "python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies {copies} --iterations {iterations} --output-mode compact_summary --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
        ],
        "decision_rule": "If OptiX remains slower at 100k and 300k on warm-query phase, classify current DB compact-summary OptiX as interface/continuation limited and keep positive wording blocked.",
    },
    {
        "app": "graph_analytics",
        "observed_ratio_embree_over_optix": 0.500014,
        "hypothesis": "The OptiX visibility any-hit path may be doing more launch/setup work than the Embree summary path, or the graph edge mapping is too sparse/branchy to amortize GPU traversal overhead.",
        "scales": [
            {"copies": 30000},
            {"copies": 60000},
            {"copies": 120000},
        ],
        "phase_fields": [
            "graph_phase_totals_sec.query_visibility_pair_rows_sec",
            "records_by_label.optix_visibility_anyhit.sec",
            "records.0.sec",
        ],
        "commands": [
            {
                "label": "graph_embree_visibility_sweep",
                "template": "python3 examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
            {
                "label": "graph_optix_visibility_sweep",
                "template": "python3 scripts/goal889_graph_visibility_optix_gate.py --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
        ],
        "decision_rule": "If OptiX remains about 2x slower while phase fields are comparable, classify graph visibility as current-implementation GPU-overhead dominated and do not promote positive wording.",
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "observed_ratio_embree_over_optix": 0.839019,
        "hypothesis": "Native-assisted candidate discovery may be correct but not enough to beat Embree because exact continuation and chunk handling dominate.",
        "scales": [
            {"copies": 10000, "chunk_copies": 100},
            {"copies": 20000, "chunk_copies": 100},
            {"copies": 40000, "chunk_copies": 100},
        ],
        "phase_fields": [
            "run_phases.rt_candidate_discovery_sec",
            "phases.optix_candidate_discovery_sec",
            "candidate_diagnostics.optix_positive_candidate_rows",
        ],
        "commands": [
            {
                "label": "polygon_pair_embree_sweep",
                "template": "python3 examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
            {
                "label": "polygon_pair_optix_sweep",
                "template": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies {chunk_copies} --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}.json",
            },
        ],
        "decision_rule": "If OptiX only loses by a small margin while chunk_copies is held constant, inspect chunk overhead and candidate count parity before deciding whether native batching can plausibly flip the result.",
    },
    {
        "app": "polygon_set_jaccard",
        "observed_ratio_embree_over_optix": 0.548760,
        "hypothesis": "The Jaccard path has both performance loss and observed chunk-sensitive/nondeterministic parity behavior; stability must be proven before any future positive wording.",
        "scales": [
            {"copies": 8192, "chunk_copies": 1},
            {"copies": 8192, "chunk_copies": 8},
            {"copies": 8192, "chunk_copies": 64},
            {"copies": 8192, "chunk_copies": 512},
        ],
        "phase_fields": [
            "run_phases.rt_candidate_discovery_sec",
            "phases.optix_candidate_discovery_sec",
            "parity_vs_cpu",
            "candidate_diagnostics.optix_positive_candidate_rows",
        ],
        "commands": [
            {
                "label": "polygon_jaccard_embree_reference",
                "template": "python3 examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py --backend embree --copies {copies} --output-mode summary > docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}_{chunk_copies}.json",
                "run_once_per_copies": True,
            },
            {
                "label": "polygon_jaccard_optix_chunk_stability",
                "template": "python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies {copies} --output-mode summary --validation-mode analytic_summary --chunk-copies {chunk_copies} --output-json docs/reports/goal1197_optix_slower_app_investigation/{label}_{copies}_{chunk_copies}.json",
            },
        ],
        "decision_rule": "If any chunk configuration fails parity, keep Jaccard blocked and file a correctness/stability task before more performance tuning.",
    },
)

CONTROL_APPS: tuple[dict[str, Any], ...] = (
    {
        "app": "road_hazard_screening",
        "role": "positive_control",
        "observed_ratio_embree_over_optix": 4.014155,
        "reason": "Should remain faster if the pod and measurement setup are sane.",
    },
)

SAME_SCALE_REPAIR_APPS: tuple[dict[str, Any], ...] = (
    {
        "app": "hausdorff_distance",
        "role": "same_scale_repair",
        "observed_issue": "Goal1195 final bundle used Embree copies=2000 and OptiX copies=1200000, so the raw 13.7x ratio is not a valid same-scale speedup.",
        "required_next_evidence": "Collect same-scale or explicitly normalized Hausdorff Embree/OptiX evidence before any positive public ratio wording.",
        "candidate_scales": [
            {"copies": 200000, "note": "OptiX was 0.0073s at 200k and below floor; Embree 200k was too expensive in prior attempt"},
            {"copies": 1200000, "note": "OptiX cleared floor; Embree likely too expensive without a new baseline strategy"},
        ],
    },
)


def build_manifest() -> dict[str, Any]:
    blockers: list[str] = []
    for row in SLOWER_APPS:
        if row["observed_ratio_embree_over_optix"] >= 1.0:
            blockers.append(f"{row['app']} is not an OptiX-slower investigation row")
        if not row["commands"]:
            blockers.append(f"{row['app']} has no commands")
        if "decision_rule" not in row:
            blockers.append(f"{row['app']} has no decision rule")
        if not row["phase_fields"]:
            blockers.append(f"{row['app']} has no phase fields")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "source_evidence": [
            "docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json",
            "docs/reports/goal1195_two_ai_consensus_2026-04-30.md",
            "docs/reports/goal1196_two_ai_consensus_2026-04-30.md",
        ],
        "slower_app_count": len(SLOWER_APPS),
        "control_app_count": len(CONTROL_APPS),
        "same_scale_repair_app_count": len(SAME_SCALE_REPAIR_APPS),
        "slower_apps": [row["app"] for row in SLOWER_APPS],
        "control_apps": [row["app"] for row in CONTROL_APPS],
        "same_scale_repair_apps": [row["app"] for row in SAME_SCALE_REPAIR_APPS],
        "rows": list(SLOWER_APPS),
        "controls": list(CONTROL_APPS),
        "same_scale_repairs": list(SAME_SCALE_REPAIR_APPS),
        "pod_ready_after_review": True,
        "pod_policy": (
            "Run this as one batched pod session only after review. Do not restart a pod per app. "
            "Preserve all artifacts, logs, and failed JSON files; copy them back before interpreting results."
        ),
        "boundary": (
            "Goal1197 is an investigation manifest for OptiX-slower app paths. It does not authorize "
            "public wording changes, release, or speedup claims."
        ),
        "blockers": blockers,
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1197 OptiX Slower-App Investigation Manifest",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- slower app count: `{payload['slower_app_count']}`",
        f"- control app count: `{payload['control_app_count']}`",
        f"- same-scale repair app count: `{payload['same_scale_repair_app_count']}`",
        f"- pod ready after review: `{payload['pod_ready_after_review']}`",
        "",
        "## Pod Policy",
        "",
        payload["pod_policy"],
        "",
        "## Slower App Investigation Rows",
        "",
        "| App | Observed ratio | Hypothesis | Scales | Decision rule |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['observed_ratio_embree_over_optix']}` | "
            f"{row['hypothesis']} | `{json.dumps(row['scales'], sort_keys=True)}` | {row['decision_rule']} |"
        )
    lines.extend(["", "## Commands", ""])
    for row in payload["rows"]:
        lines.extend([f"### {row['app']}", ""])
        for command in row["commands"]:
            lines.extend(
                [
                    f"- `{command['label']}`",
                    "",
                    f"  `{command['template']}`",
                    "",
                ]
            )
    lines.extend(["## Positive Controls", ""])
    for row in payload["controls"]:
        lines.append(
            f"- `{row['app']}`: `{row['role']}`, observed ratio `{row['observed_ratio_embree_over_optix']}`. {row['reason']}"
        )
    lines.extend(["", "## Same-Scale Repair Targets", ""])
    for row in payload["same_scale_repairs"]:
        lines.append(
            f"- `{row['app']}`: `{row['role']}`. {row['observed_issue']} {row['required_next_evidence']}"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Goal1197 OptiX slower-app investigation manifest.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    args = parser.parse_args()
    payload = build_manifest()
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": payload["valid"],
                "slower_app_count": payload["slower_app_count"],
                "control_app_count": payload["control_app_count"],
                "same_scale_repair_app_count": payload["same_scale_repair_app_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
