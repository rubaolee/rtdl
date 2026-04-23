#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts import goal811_spatial_optix_summary_phase_profiler as profiler


GOAL = "Goal849 spatial prepared-summary promotion packet"
DATE = "2026-04-23"
SCENARIOS = {
    "service_coverage_gaps": {
        "require_rt_core_mode": "gap_summary_prepared",
        "next_goal": "Goal810/811 local packet -> future RTX run",
        "claim_scope": "prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries",
    },
    "event_hotspot_screening": {
        "require_rt_core_mode": "count_summary_prepared",
        "next_goal": "Goal810/811 local packet -> future RTX run",
        "claim_scope": "prepared OptiX fixed-radius count traversal for hotspot compact summaries",
    },
}


def _scenario_packet(app: str) -> dict[str, object]:
    dry_run = profiler.run_profile(scenario=app, mode="dry-run", copies=1)
    readiness = rt.optix_app_benchmark_readiness(app)
    maturity = rt.rt_core_app_maturity(app)
    performance = rt.optix_app_performance_support(app)
    return {
        "app": app,
        "performance_class": performance.performance_class,
        "readiness_status": readiness.status,
        "current_maturity": maturity.current_status,
        "target_maturity": maturity.target_status,
        "required_action": maturity.required_action,
        "cloud_policy": maturity.cloud_policy,
        "require_rt_core_mode": SCENARIOS[app]["require_rt_core_mode"],
        "claim_scope": SCENARIOS[app]["claim_scope"],
        "local_dry_run_timings_sec": dry_run["scenario"]["timings_sec"],
        "local_dry_run_result": dry_run["scenario"]["result"],
        "promotion_blocker": readiness.blocker,
        "promotion_condition": (
            "real RTX optix-mode phase artifact must exist and be reviewed before readiness or maturity promotion"
        ),
        "next_goal": SCENARIOS[app]["next_goal"],
    }


def build_packet() -> dict[str, object]:
    apps = [_scenario_packet(app) for app in SCENARIOS]
    return {
        "goal": GOAL,
        "date": DATE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "apps": apps,
        "ready_for_local_promotion_packet": True,
        "ready_for_rtx_claim_review_now": False,
        "boundary": (
            "This packet proves local claim-path readiness only. "
            "It does not promote either app to ready_for_rtx_claim_review and does not authorize a public RTX speedup claim."
        ),
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal849: Spatial Prepared-Summary Promotion Packet",
        "",
        f"Date: {payload['date']}",
        "",
        "## Purpose",
        "",
        "Package the existing local evidence for the two partial-ready spatial apps so they can enter a future consolidated RTX batch without ambiguity.",
        "",
    ]
    for app in payload["apps"]:
        lines.extend(
            [
                f"## {app['app']}",
                "",
                f"- Performance class: `{app['performance_class']}`",
                f"- Benchmark readiness: `{app['readiness_status']}`",
                f"- Current maturity: `{app['current_maturity']}`",
                f"- Target maturity: `{app['target_maturity']}`",
                f"- Required OptiX mode: `{app['require_rt_core_mode']}`",
                f"- Claim scope: {app['claim_scope']}",
                f"- Promotion blocker: {app['promotion_blocker']}",
                f"- Promotion condition: {app['promotion_condition']}",
                "",
                "Dry-run timings:",
                "",
            ]
        )
        for key, value in app["local_dry_run_timings_sec"].items():
            lines.append(f"- `{key}`: `{value}`")
        lines.extend(["", "Dry-run result keys:", ""])
        for key in sorted(app["local_dry_run_result"].keys()):
            lines.append(f"- `{key}`")
        lines.append("")
    lines.extend(["## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    payload = build_packet()
    json_path = ROOT / "docs/reports/goal849_spatial_promotion_packet_2026-04-23.json"
    md_path = ROOT / "docs/reports/goal849_spatial_promotion_packet_2026-04-23.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
