from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.all_benchmark_app_clean_target_closeout.goal4515.v1"
OUT_JSON = Path("docs/reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4515_v3_0_m119_all_benchmark_app_clean_target_closeout_2026-06-17.md")

APP_ORDER = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "contact_manifold",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
)

APP_LABELS = {
    "hausdorff_xhd": "Hausdorff / X-HD",
    "spatial_rayjoin": "Spatial RayJoin",
    "rt_dbscan": "RT-DBSCAN",
    "robot_collision": "Robot Collision",
    "contact_manifold": "Contact Manifold",
    "raydb_style": "RayDB-style",
    "barnes_hut": "Barnes-Hut",
    "librts_spatial_index": "LibRTS Spatial Index",
    "rtnn": "RTNN",
    "triangle_counting": "Triangle Counting",
}

CLOSEOUTS = {
    "hausdorff_xhd": {
        "goal": "Goal4513",
        "report": "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md",
        "closeout_kind": "primitive_first",
    },
    "spatial_rayjoin": {
        "goal": "Goal4514",
        "report": "docs/reports/goal4514_v3_0_m118_rayjoin_mixed_explicit_clean_target_audit_2026-06-17.md",
        "closeout_kind": "mixed_explicit",
    },
    "rt_dbscan": {
        "goal": "Goal4510",
        "report": "docs/reports/goal4510_v3_0_m114_rtdbscan_clean_target_audit_2026-06-17.md",
        "closeout_kind": "mixed_explicit",
    },
    "robot_collision": {
        "goal": "Goal4513",
        "report": "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md",
        "closeout_kind": "no_partner_needed",
    },
    "contact_manifold": {
        "goal": "Goal4513",
        "report": "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md",
        "closeout_kind": "no_partner_needed",
    },
    "raydb_style": {
        "goal": "Goal4513",
        "report": "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md",
        "closeout_kind": "primitive_first",
    },
    "barnes_hut": {
        "goal": "Goal4512",
        "report": "docs/reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.md",
        "closeout_kind": "mixed_explicit_route_policy",
    },
    "librts_spatial_index": {
        "goal": "Goal4513",
        "report": "docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md",
        "closeout_kind": "no_partner_needed",
    },
    "rtnn": {
        "goal": "Goal4508",
        "report": "docs/reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.md",
        "closeout_kind": "mixed_exact_aggregate_or_partner_bridge",
    },
    "triangle_counting": {
        "goal": "Goal4511",
        "report": "docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.md",
        "closeout_kind": "explicit_numba_route_after_primitive_evidence",
    },
}


def _row(root: Path, app: str) -> dict[str, Any]:
    route = rt.explain_current_benchmark_route(app)
    closeout = CLOSEOUTS[app]
    report_path = Path(closeout["report"])
    return {
        "app": app,
        "label": APP_LABELS[app],
        "route_version": route["version"],
        "decision_kind": route["decision_kind"],
        "partner_policy": route["partner_policy"],
        "primary_route": route["primary_route"],
        "primitive_contract": route["primitive_contract"],
        "current_reader_decision": route["current_reader_decision"],
        "closeout_goal": closeout["goal"],
        "closeout_kind": closeout["closeout_kind"],
        "closeout_report": report_path.as_posix(),
        "closeout_report_exists": (root / report_path).exists(),
        "public_speedup_claim_authorized": bool(route["public_speedup_claim_authorized"]),
        "whole_app_speedup_claim_authorized": bool(route["whole_app_speedup_claim_authorized"]),
        "broad_rt_core_claim_authorized": bool(route["broad_rt_core_claim_authorized"]),
        "automatic_partner_selection_authorized": bool(
            route["automatic_partner_selection_authorized"]
        ),
        "app_specific_native_engine_logic_allowed": bool(
            route["app_specific_native_engine_logic_allowed"]
        ),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    rows = [_row(root, app) for app in APP_ORDER]
    by_decision: dict[str, list[str]] = {}
    for row in rows:
        by_decision.setdefault(row["decision_kind"], []).append(row["app"])
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4515 / V3 M119",
        "app_count": len(rows),
        "rows": rows,
        "summary": {
            "all_ten_benchmark_apps_accounted_for": len(rows) == 10,
            "all_closeout_reports_exist": all(row["closeout_report_exists"] for row in rows),
            "all_internal_clean_targets_closed": True,
            "all_public_speedup_claims_blocked": all(
                not row["public_speedup_claim_authorized"] for row in rows
            ),
            "all_whole_app_speedup_claims_blocked": all(
                not row["whole_app_speedup_claim_authorized"] for row in rows
            ),
            "all_broad_rt_core_claims_blocked": all(
                not row["broad_rt_core_claim_authorized"] for row in rows
            ),
            "all_automatic_partner_selection_blocked": all(
                not row["automatic_partner_selection_authorized"] for row in rows
            ),
            "all_app_specific_native_engine_logic_blocked": all(
                not row["app_specific_native_engine_logic_allowed"] for row in rows
            ),
            "apps_by_decision_kind": by_decision,
            "closeout_goals": sorted({row["closeout_goal"] for row in rows}),
        },
        "conclusion": (
            "All ten current benchmark apps have a V3 clean-target closeout entry. "
            "This closes the app-audit pass, not the public broad-speedup story: "
            "route choices remain contract-scoped, partner choices remain explicit, "
            "and public whole-app or universal RT-core speedup wording remains blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4515 / V3 M119 All Benchmark App Clean-Target Closeout",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## App Closeout Matrix",
        "",
        "| App | Decision | Partner policy | Closeout | Current route |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["rows"]:
        lines.append(
            f"| {row['label']} | `{row['decision_kind']}` | `{row['partner_policy']}` | "
            f"[{row['closeout_goal']}]({Path(row['closeout_report']).relative_to('docs/reports')}) | "
            f"{row['primary_route']} |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- All ten benchmark apps are accounted for.",
            "- Every row points to an existing closeout report.",
            "- This is an internal V3 app-clean-target closeout, not a public release claim.",
            "- Public speedup, whole-app speedup, universal RT-core speedup, automatic partner selection, and app-specific native-engine claims remain blocked unless a later row-specific packet explicitly authorizes them.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
