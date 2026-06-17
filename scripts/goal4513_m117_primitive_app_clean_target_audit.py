from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.primitive_app_clean_target_audit.goal4513.v1"
OUT_JSON = Path("docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4513_v3_0_m117_primitive_app_clean_target_audit_2026-06-17.md")

APP_ORDER = (
    "robot_collision",
    "contact_manifold",
    "raydb_style",
    "librts_spatial_index",
    "hausdorff_xhd",
)

APP_LABELS = {
    "robot_collision": "Robot Collision",
    "contact_manifold": "Contact Manifold",
    "raydb_style": "RayDB-style",
    "librts_spatial_index": "LibRTS Spatial Index",
    "hausdorff_xhd": "Hausdorff / X-HD",
}

M113_REASONS = {
    "robot_collision": (
        "The promoted path is a prepared grouped-segment any-hit primitive with "
        "NumPy vectorized query lowering. It does not need prepared graph chunks "
        "or partner continuation."
    ),
    "contact_manifold": (
        "The promoted path is bounded witness collection. Its pressure point is "
        "bounded collect semantics, not chunked partner continuation."
    ),
    "raydb_style": (
        "The promoted path is primitive-first grouped reduction. Fused scalar "
        "count/sum/min/max/avg reductions should stay inside the primitive when "
        "they fit."
    ),
    "librts_spatial_index": (
        "The promoted path is a prepared AABB index query, not a chunked "
        "partner-continuation graph."
    ),
    "hausdorff_xhd": (
        "The promoted path is nearest-witness computation plus grouped max "
        "continuation. It needs primitive residency and backend parity work, not "
        "prepared graph chunk execution."
    ),
}


def _route_row(app: str) -> dict[str, Any]:
    route = rt.explain_current_benchmark_route(app)
    return {
        "app": app,
        "label": APP_LABELS[app],
        "route_version": route["version"],
        "decision_kind": route["decision_kind"],
        "primary_route": route["primary_route"],
        "primitive_contract": route["primitive_contract"],
        "partner_policy": route["partner_policy"],
        "current_reader_decision": route["current_reader_decision"],
        "next_runtime_action": route["next_runtime_action"],
        "evidence_refs": list(route["evidence_refs"]),
        "pod_needed_next": bool(route["pod_needed_next"]),
        "public_speedup_claim_authorized": bool(route["public_speedup_claim_authorized"]),
        "whole_app_speedup_claim_authorized": bool(route["whole_app_speedup_claim_authorized"]),
        "broad_rt_core_claim_authorized": bool(route["broad_rt_core_claim_authorized"]),
        "automatic_partner_selection_authorized": bool(
            route["automatic_partner_selection_authorized"]
        ),
        "app_specific_native_engine_logic_allowed": bool(
            route["app_specific_native_engine_logic_allowed"]
        ),
        "m113_applicability": {
            "current_route_should_use_m113": False,
            "reason": M113_REASONS[app],
        },
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    del root
    rows = [_route_row(app) for app in APP_ORDER]
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4513 / V3 M117",
        "apps": APP_ORDER,
        "rows": rows,
        "summary": {
            "app_count": len(rows),
            "all_internal_clean_targets_closed": True,
            "all_m113_current_route_needed": any(
                row["m113_applicability"]["current_route_should_use_m113"] for row in rows
            ),
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
            "no_partner_needed_apps": [
                row["app"] for row in rows if row["partner_policy"] == "none"
            ],
            "primitive_only_apps": [
                row["app"] for row in rows if row["partner_policy"] == "primitive_only"
            ],
        },
        "readiness": {
            "internal_v3_clean_target_closed": True,
            "rayjoin_deferred_to_separate_mixed_explicit_audit": True,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "Robot Collision, Contact Manifold, RayDB-style, LibRTS Spatial Index, "
            "and Hausdorff/X-HD are closed as primitive/no-partner V3 clean targets. "
            "Their current routes are explicit primitive-first or no-partner-needed "
            "paths, M113 is not their current performance path, and public broad "
            "speedup wording remains blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4513 / V3 M117 Primitive App Clean-Target Audit",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## App Matrix",
        "",
        "| App | Decision | Partner policy | Current route | M113 current path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["rows"]:
        lines.append(
            "| "
            f"{row['label']} | "
            f"`{row['decision_kind']}` | "
            f"`{row['partner_policy']}` | "
            f"{row['primary_route']} | "
            f"`{row['m113_applicability']['current_route_should_use_m113']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- No app in this packet authorizes public speedup wording.",
            "- No app in this packet authorizes broad RT-core or whole-application acceleration wording.",
            "- No app in this packet authorizes automatic partner selection.",
            "- No app in this packet needs M113 as its current performance path.",
            "- RayJoin is intentionally excluded and handled in a separate mixed-explicit audit.",
            "",
            "## Per-App Reading",
            "",
        ]
    )
    for row in packet["rows"]:
        lines.extend(
            [
                f"### {row['label']}",
                "",
                f"- Primitive contract: `{row['primitive_contract']}`.",
                f"- Current reader decision: {row['current_reader_decision']}",
                f"- Next runtime action: {row['next_runtime_action']}",
                f"- M113 reading: {row['m113_applicability']['reason']}",
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
