#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


GOAL = "Goal848 v1.0 RT-core goal series"
DATE = "2026-04-23"
RT_CORE_READY = "rt_core_ready"
RT_CORE_PARTIAL_READY = "rt_core_partial_ready"
NEEDS_RT_CORE_REDESIGN = "needs_rt_core_redesign"
NEEDS_OPTIX_APP_SURFACE = "needs_optix_app_surface"
NOT_NVIDIA_RT_CORE_TARGET = "not_nvidia_rt_core_target"


def _bucketed_apps() -> dict[str, list[str]]:
    maturity = rt.rt_core_app_maturity_matrix()
    buckets = {
        "already_ready_keep_and_optimize": [],
        "must_finish_first": [],
        "second_wave": [],
        "major_redesign_wave": [],
        "out_of_scope_for_nvidia_rt": [],
    }
    for app in rt.public_apps():
        current = maturity[app].current_status
        if app in {
            "database_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "robot_collision_screening",
        }:
            buckets["must_finish_first"].append(app)
        elif current == RT_CORE_READY:
            buckets["already_ready_keep_and_optimize"].append(app)
        elif app in {
            "graph_analytics",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
        }:
            buckets["second_wave"].append(app)
        elif current == NOT_NVIDIA_RT_CORE_TARGET:
            buckets["out_of_scope_for_nvidia_rt"].append(app)
        else:
            buckets["major_redesign_wave"].append(app)
    return buckets


def build_goal_series() -> dict[str, object]:
    maturity = rt.rt_core_app_maturity_matrix()
    readiness = rt.optix_app_benchmark_readiness_matrix()
    performance = rt.optix_app_performance_matrix()
    public_wording = rt.rtx_public_wording_matrix()
    buckets = _bucketed_apps()

    goal_series = [
        {
            "goal_id": "Goal848",
            "title": "Lock the v1.0 all-in-RT app migration plan",
            "scope": "Use the canonical app maturity matrix to define promotion order, acceptance rules, and claim boundaries.",
            "acceptance": [
                "Every public app is assigned to a v1.0 bucket.",
                "Each bucket has an explicit engineering purpose and claim boundary.",
                "The plan is machine-readable and reviewable.",
            ],
            "consensus_requirement": "3-AI for planning significance",
        },
        {
            "goal_id": "Goal849",
            "title": "Promote spatial prepared-summary apps to promotion-ready candidates",
            "scope": "Package local evidence for service coverage and event hotspot prepared OptiX summary paths using existing profiler and CLI guards.",
            "acceptance": [
                "Dry-run phase packet exists for both apps.",
                "Prepared OptiX summary modes remain guarded by --require-rt-core.",
                "Cloud inclusion criteria are explicit and bounded.",
            ],
            "consensus_requirement": "2-AI before completion",
        },
        {
            "goal_id": "Goal850",
            "title": "Reduce DB app host/interface overhead on the OptiX path",
            "scope": "Push compact prepared DB outputs and native phase accounting until Python is orchestration only.",
            "acceptance": [
                "Prepared DB compact-summary path has phase-clean counters.",
                "Internal review package shows the dominant app path is no longer materialization-driven.",
                "Claim remains bounded to prepared DB summary paths.",
            ],
            "consensus_requirement": "2-AI before completion",
        },
        {
            "goal_id": "Goal851",
            "title": "Promote segment/polygon compact native OptiX paths",
            "scope": "Run strict native-vs-host-indexed gating for hit-count and compact outputs before any row-output claim.",
            "acceptance": [
                "Explicit native mode passes strict correctness gate.",
                "Compact summary/count outputs are separated from pair-row output.",
                "No row-output claim is made without a native row emitter.",
            ],
            "consensus_requirement": "2-AI before completion",
        },
        {
            "goal_id": "Goal852",
            "title": "Validate graph analytics native RT-core sub-paths",
            "scope": (
                "Run the combined graph gate for visibility any-hit plus explicit "
                "native BFS/triangle graph-ray candidate generation on RTX hardware."
            ),
            "acceptance": [
                "Strict RTX artifact proves row-digest parity for visibility, native BFS, and native triangle-count sub-paths.",
                "Host-indexed fallback remains the default until the native graph-ray path passes review.",
                "Shortest-path, graph database, distributed graph analytics, and whole-app graph-system claims remain excluded.",
            ],
            "consensus_requirement": "3-AI because it changes strategic scope",
        },
        {
            "goal_id": "Goal853",
            "title": "Redesign CUDA-through-OptiX apps into true traversal apps or demote them permanently",
            "scope": "Hausdorff, ANN candidate search, and Barnes-Hut require true RT traversal formulations or permanent non-RT-core classification.",
            "acceptance": [
                "Each app has a true traversal design or a permanent non-RT-core decision.",
                "Public docs stop conflating CUDA-through-OptiX with RT-core use.",
            ],
            "consensus_requirement": "3-AI because it changes flagship app scope",
        },
        {
            "goal_id": "Goal854",
            "title": "Expose or explicitly retire missing OptiX app surfaces",
            "scope": "Facility KNN, polygon overlap, and polygon Jaccard need either real OptiX surfaces or explicit retirement from NVIDIA RT-core targets.",
            "acceptance": [
                "Each app has a surface decision with rationale.",
                "Any new OptiX surface has a local correctness gate.",
            ],
            "consensus_requirement": "2-AI before completion",
        },
        {
            "goal_id": "Goal855",
            "title": "Run one consolidated RTX cloud validation batch after local closure",
            "scope": "Use the single-session cloud procedure only after local work is ready.",
            "acceptance": [
                "All active-candidate apps have local readiness packets.",
                "The cloud run is one batched session with preserved artifacts.",
                "Interpretation stays bounded to exact measured sub-paths.",
            ],
            "consensus_requirement": "2-AI before completion",
        },
    ]

    app_rows = []
    for app in rt.public_apps():
        app_rows.append(
            {
                "app": app,
                "current_status": maturity[app].current_status,
                "target_status": maturity[app].target_status,
                "performance_class": performance[app].performance_class,
                "benchmark_readiness": readiness[app].status,
                "public_wording_status": public_wording[app].status,
                "public_wording_boundary": public_wording[app].boundary,
                "required_action": maturity[app].required_action,
                "cloud_policy": maturity[app].cloud_policy,
            }
        )

    return {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "public_app_count": len(rt.public_apps()),
            "rt_core_ready_now": sum(
                1 for row in app_rows if row["current_status"] == RT_CORE_READY
            ),
            "rt_core_partial_ready_now": sum(
                1 for row in app_rows if row["current_status"] == RT_CORE_PARTIAL_READY
            ),
            "needs_redesign_or_new_surface": sum(
                1
                for row in app_rows
                if row["current_status"] in {NEEDS_RT_CORE_REDESIGN, NEEDS_OPTIX_APP_SURFACE}
            ),
            "out_of_scope_for_nvidia_rt": sum(
                1 for row in app_rows if row["current_status"] == NOT_NVIDIA_RT_CORE_TARGET
            ),
            "reviewed_public_wording": sum(
                1 for row in app_rows if row["public_wording_status"] == "public_wording_reviewed"
            ),
            "blocked_public_wording": sum(
                1 for row in app_rows if row["public_wording_status"] == "public_wording_blocked"
            ),
        },
        "bucketing_note": (
            "Priority buckets are execution buckets, not pure status buckets. "
            "An app can already be rt_core_ready and still appear in must_finish_first "
            "when it is a flagship path with required optimization or claim-packaging work; "
            "robot_collision_screening is the current example. Public speedup wording is "
            "tracked separately by rtdsl.rtx_public_wording_matrix()."
        ),
        "priority_buckets": buckets,
        "goal_series": goal_series,
        "apps": app_rows,
        "boundary": (
            "This plan defines the v1.0 NVIDIA RT-core migration order. "
            "It is a planning artifact, not a release authorization and not a public speedup claim."
        ),
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal848: v1.0 RT-Core Goal Series",
        "",
        f"Date: {payload['date']}",
        "",
        "## Summary",
        "",
        f"- Public apps: `{payload['summary']['public_app_count']}`",
        f"- RT-core ready now: `{payload['summary']['rt_core_ready_now']}`",
        f"- RT-core partial-ready now: `{payload['summary']['rt_core_partial_ready_now']}`",
        f"- Need redesign or new surface: `{payload['summary']['needs_redesign_or_new_surface']}`",
        f"- Out of NVIDIA RT scope: `{payload['summary']['out_of_scope_for_nvidia_rt']}`",
        f"- Reviewed public wording rows: `{payload['summary']['reviewed_public_wording']}`",
        f"- Blocked public wording rows: `{payload['summary']['blocked_public_wording']}`",
        "",
        payload["bucketing_note"],
        "",
        "## Priority Buckets",
        "",
    ]
    for bucket, apps in payload["priority_buckets"].items():
        lines.append(f"### {bucket}")
        lines.append("")
        for app in apps:
            lines.append(f"- `{app}`")
        lines.append("")
    lines.extend(["## Goal Series", ""])
    for item in payload["goal_series"]:
        lines.append(f"### {item['goal_id']}: {item['title']}")
        lines.append("")
        lines.append(item["scope"])
        lines.append("")
        lines.append("Acceptance:")
        lines.append("")
        for point in item["acceptance"]:
            lines.append(f"- {point}")
        lines.append("")
        lines.append(f"Consensus: `{item['consensus_requirement']}`")
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    payload = build_goal_series()
    json_path = ROOT / "docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json"
    md_path = ROOT / "docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
