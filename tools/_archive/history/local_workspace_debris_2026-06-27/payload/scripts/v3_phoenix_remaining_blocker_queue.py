from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FROZEN_SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_serious_v2x_paired_20260622_074100"
    / "summary.json"
)
CLASSIFICATION = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_set_a_set_b_classification_2026-06-22.json"
)
BARNES_INTAKE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.json"
)
LIBRTS_REPEAT9_CURRENT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_librts_aabb_count_cache_repeat9_20260622_140402"
    / "current_patched_goal2626_large"
    / "summary.json"
)
LIBRTS_REPEAT9_V2 = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_librts_aabb_count_cache_repeat9_20260622_140402"
    / "v2_14_goal2626_large"
    / "summary.json"
)
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m8_remaining_blocker_queue_2026-06-22.json"
DEFAULT_MD_OUT = ROOT / "docs" / "reports" / "phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _geomean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute geomean for empty values")
    if any(value <= 0.0 for value in values):
        raise ValueError("geomean values must be positive")
    return math.exp(sum(math.log(value) for value in values) / len(values))


def _row_id(row: dict[str, Any]) -> str:
    return "|".join(
        str(row[field])
        for field in ("suite", "app_id", "comparison_group", "backend", "case_id")
    )


def _app_geomeans(rows: list[dict[str, Any]]) -> dict[str, float]:
    by_app: dict[str, list[float]] = {}
    for row in rows:
        by_app.setdefault(str(row["app_id"]), []).append(float(row["v3_speedup_vs_v2"]))
    return {app_id: _geomean(values) for app_id, values in sorted(by_app.items())}


def _set_for_app(classification: dict[str, Any], app_id: str) -> str:
    return str(classification["app_classification"][app_id]["set"])


def _extract_librts_repeat9_rows(current: dict[str, Any], v2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    v2_by_key = {_row_id(row | {"suite": "goal2626_large"}): row for row in v2["rows"]}
    replacements: dict[str, dict[str, Any]] = {}
    for row in current["rows"]:
        compact = {
            "suite": "goal2626_large",
            "app_id": row["app_id"],
            "backend": row["backend"],
            "case_id": row["case_id"],
            "comparison_group": row["comparison_group"],
        }
        key = _row_id(compact)
        v2_row = v2_by_key[key]
        current_sec = float(row["primary_metric_sec"])
        v2_sec = float(v2_row["primary_metric_sec"])
        replacements[key] = {
            **compact,
            "focused_v2_sec": v2_sec,
            "focused_patched_v3_sec": current_sec,
            "focused_patched_v3_speedup_vs_v2": v2_sec / current_sec,
            "primary_metric_source": row["primary_metric_source"],
            "source": "librts_repeat9_focused_generic_count_cache",
        }
    return replacements


def build_payload(
    frozen_summary_path: Path = FROZEN_SUMMARY,
    classification_path: Path = CLASSIFICATION,
    barnes_intake_path: Path = BARNES_INTAKE,
    librts_current_path: Path = LIBRTS_REPEAT9_CURRENT,
    librts_v2_path: Path = LIBRTS_REPEAT9_V2,
) -> dict[str, Any]:
    frozen_summary = _load_json(frozen_summary_path)
    classification = _load_json(classification_path)
    barnes = _load_json(barnes_intake_path)
    librts_replacements = _extract_librts_repeat9_rows(
        _load_json(librts_current_path),
        _load_json(librts_v2_path),
    )

    rows = [dict(row) for row in frozen_summary["same_metric_rows"]]
    projected_rows = [dict(row) for row in rows]
    covered_rows: list[dict[str, Any]] = []
    watch_rows: list[dict[str, Any]] = []

    barnes_replacements = {row["row_id"]: row for row in barnes["replacement_rows"]}
    for row in projected_rows:
        key = _row_id(row)
        if key in barnes_replacements:
            replacement = barnes_replacements[key]
            row["v2_sec"] = replacement["focused_v2_sec"]
            row["v3_sec"] = replacement["focused_patched_v3_sec"]
            row["v3_speedup_vs_v2"] = replacement["focused_patched_v3_speedup_vs_v2"]
            row["planning_status"] = "covered_pending_full_suite_validation"
            row["planning_source"] = "barnes_hut_m7_focused_generic_symbol_cache"
            covered_rows.append(
                {
                    "row_id": key,
                    "app_id": row["app_id"],
                    "case_id": row["case_id"],
                    "frozen_speedup": replacement["frozen_v3_speedup_vs_v2"],
                    "planning_speedup": replacement["focused_patched_v3_speedup_vs_v2"],
                    "source": row["planning_source"],
                }
            )
            continue
        if key in librts_replacements:
            replacement = librts_replacements[key]
            replacement_speedup = replacement["focused_patched_v3_speedup_vs_v2"]
            if row["backend"] == "embree" and replacement_speedup >= 0.98:
                row["v2_sec"] = replacement["focused_v2_sec"]
                row["v3_sec"] = replacement["focused_patched_v3_sec"]
                row["v3_speedup_vs_v2"] = replacement_speedup
                row["planning_status"] = "covered_pending_full_suite_validation"
                row["planning_source"] = "librts_repeat9_focused_generic_count_cache"
                covered_rows.append(
                    {
                        "row_id": key,
                        "app_id": row["app_id"],
                        "case_id": row["case_id"],
                        "frozen_speedup": float(
                            next(old["v3_speedup_vs_v2"] for old in rows if _row_id(old) == key)
                        ),
                        "planning_speedup": replacement_speedup,
                        "source": row["planning_source"],
                    }
                )
            elif row["backend"] == "optix":
                watch_rows.append(
                    {
                        "row_id": key,
                        "app_id": row["app_id"],
                        "case_id": row["case_id"],
                        "frozen_speedup": float(row["v3_speedup_vs_v2"]),
                        "repeat9_focused_speedup": replacement_speedup,
                        "status": "unstable_watch_not_current_primary_target",
                        "reason": "Original frozen row was near parity, but repeat=9 focused rerun regressed; profile separately before spending large POD time.",
                    }
                )

    app_geomeans = _app_geomeans(projected_rows)
    set_a_rows = [row for row in projected_rows if _set_for_app(classification, row["app_id"]) == "A"]
    set_b_rows = [row for row in projected_rows if _set_for_app(classification, row["app_id"]) == "B"]
    active_row_losses: list[dict[str, Any]] = []
    for row in projected_rows:
        row_set = _set_for_app(classification, row["app_id"])
        speedup = float(row["v3_speedup_vs_v2"])
        if row.get("planning_status") == "covered_pending_full_suite_validation":
            continue
        if row_set == "A" and speedup < 0.98:
            active_row_losses.append(
                {
                    "row_id": _row_id(row),
                    "set": row_set,
                    "app_id": row["app_id"],
                    "case_id": row["case_id"],
                    "backend": row["backend"],
                    "suite": row["suite"],
                    "speedup": speedup,
                    "loss_fraction": 1.0 - speedup,
                    "recommended_target": row["app_id"] == "spatial_rayjoin"
                    and row["case_id"] == "rayjoin_optix_promoted_lsi_tiled_x2048",
                }
            )
    active_row_losses.sort(key=lambda row: row["loss_fraction"], reverse=True)

    set_a_app_wins = {
        app_id: value for app_id, value in app_geomeans.items() if _set_for_app(classification, app_id) == "A" and value > 1.05
    }
    next_target = {
        "id": "spatial_rayjoin_lsi_optix_topology_stream",
        "row_id": "goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048",
        "reason": (
            "Largest uncovered Set-A row loss after Barnes-Hut and LibRTS Embree "
            "focused fixes; architecture-bearing Spatial/RayJoin LSI/topology route."
        ),
        "initial_action": "non-POD local intake of Spatial/RayJoin LSI OptiX route mechanics and existing topology-stream evidence",
        "pod_authorized_now": False,
    }
    checks = {
        "barnes_hut_covered_rows_present": len([row for row in covered_rows if row["app_id"] == "barnes_hut"]) == 6,
        "librts_embree_covered": any(
            row["row_id"].endswith("|embree|librts_embree_aabb_index") and row["planning_speedup"] >= 0.98
            for row in covered_rows
        ),
        "librts_optix_watch_recorded": any(row["case_id"] == "librts_optix_aabb_index" for row in watch_rows),
        "spatial_lsi_optix_is_top_active_row_loss": bool(active_row_losses)
        and active_row_losses[0]["row_id"] == next_target["row_id"],
        "release_still_false": True,
        "pod_spend_still_false": True,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_remaining_blocker_queue",
        "status": "m8_remaining_blocker_queue_not_release_not_pod",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "full_all_app_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "failed_checks": failed_checks,
        "checks": checks,
        "score_projection_for_planning_only": {
            "frozen_all_rows_geomean": _geomean([float(row["v3_speedup_vs_v2"]) for row in rows]),
            "planning_all_rows_geomean_after_covered_fixes": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in projected_rows]
            ),
            "planning_set_a_geomean_after_covered_fixes": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in set_a_rows]
            ),
            "planning_set_b_geomean_after_covered_fixes": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in set_b_rows]
            ),
            "planning_set_a_app_wins_over_1_05x": len(set_a_app_wins),
            "planning_set_a_app_wins_required": 5,
            "planning_set_a_app_geomeans": {
                app_id: value
                for app_id, value in app_geomeans.items()
                if _set_for_app(classification, app_id) == "A"
            },
            "planning_set_b_app_geomeans": {
                app_id: value
                for app_id, value in app_geomeans.items()
                if _set_for_app(classification, app_id) == "B"
            },
        },
        "covered_pending_full_suite_validation": covered_rows,
        "active_row_losses": active_row_losses,
        "watch_rows": watch_rows,
        "next_target_recommendation": next_target,
        "interpretation": {
            "why_not_all_app_pod_now": (
                "Planning projection is still far below the V3 release bar: Set-A "
                "geomean is not near 1.20x and Set-A app wins remain below the required count."
            ),
            "why_not_barnes_or_librts_embree_now": (
                "Both are already covered by focused generic runtime fixes for planning, "
                "pending full-suite validation."
            ),
            "why_spatial_next": (
                "Spatial/RayJoin LSI OptiX is the largest uncovered architecture-bearing "
                "row loss and targets topology/stream mechanics rather than app-specific tuning."
            ),
        },
        "goal_level_decision_audit": {
            "decision": "Choose Spatial/RayJoin LSI OptiX as the next non-POD investigation target after M7.",
            "was_i_foolish": "No for this decision.",
            "foolish_actions": "It would be foolish to keep burning effort on Barnes-Hut or LibRTS Embree after focused generic fixes already cover them for planning, or to run all-app POD before the remaining blockers move.",
            "other_path": "Attack RTNN clustered Embree first. That is plausible, but RTNN symbol-cache work already measured no material gain, while Spatial/RayJoin has the larger uncovered row loss.",
            "different_path_now": "Do a local Spatial/RayJoin LSI OptiX mechanics intake and seek review before any implementation or POD spend.",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    projection = payload["score_projection_for_planning_only"]
    target = payload["next_target_recommendation"]
    lines = [
        "# Phoenix V3 M8 Remaining Blocker Queue",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is a planning queue, not a release scorecard update.",
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "broad_v3_faster_than_v2_claim_authorized: false",
        "full_all_app_pod_spend_authorized: false",
        "focused_pod_spend_authorized: false",
        "```",
        "",
        "## Planning Projection",
        "",
        f"- Frozen all-row geomean: `{projection['frozen_all_rows_geomean']:.6f}x`",
        f"- Planning all-row geomean after covered fixes: `{projection['planning_all_rows_geomean_after_covered_fixes']:.6f}x`",
        f"- Planning Set-A geomean after covered fixes: `{projection['planning_set_a_geomean_after_covered_fixes']:.6f}x`",
        f"- Planning Set-B geomean after covered fixes: `{projection['planning_set_b_geomean_after_covered_fixes']:.6f}x`",
        f"- Planning Set-A app wins over 1.05x: `{projection['planning_set_a_app_wins_over_1_05x']} / {projection['planning_set_a_app_wins_required']}`",
        "",
        "## Covered Pending Full-Suite Validation",
        "",
        "| row | frozen | planning | source |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in payload["covered_pending_full_suite_validation"]:
        lines.append(
            f"| `{row['row_id']}` | {row['frozen_speedup']:.3f}x | "
            f"{row['planning_speedup']:.3f}x | `{row['source']}` |"
        )
    lines.extend(["", "## Active Row Losses", "", "| row | speedup | next target |", "| --- | ---: | --- |"])
    for row in payload["active_row_losses"]:
        marker = "yes" if row["recommended_target"] else ""
        lines.append(f"| `{row['row_id']}` | {row['speedup']:.3f}x | {marker} |")
    lines.extend(["", "## Watch Rows", "", "| row | frozen | focused repeat9 | status |", "| --- | ---: | ---: | --- |"])
    for row in payload["watch_rows"]:
        lines.append(
            f"| `{row['row_id']}` | {row['frozen_speedup']:.3f}x | "
            f"{row['repeat9_focused_speedup']:.3f}x | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Next Target",
            "",
            f"- id: `{target['id']}`",
            f"- row: `{target['row_id']}`",
            f"- reason: {target['reason']}",
            f"- initial action: {target['initial_action']}",
            f"- pod authorized now: `{str(target['pod_authorized_now']).lower()}`",
            "",
            "## Goal-Level Decision Audit",
            "",
        ]
    )
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made it foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phoenix V3 M8 remaining blocker queue.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    json_text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json_text + "\n", encoding="utf-8")
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json_text)
    return 2 if payload["failed_checks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
