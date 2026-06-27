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
FOCUSED_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_barnes_hut_symbol_cache_focused_20260622_135158"
)
RUNNER_PARITY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718"
    / "summary.json"
)
DEFAULT_JSON_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.json"
)
DEFAULT_MD_OUT = ROOT / "docs" / "reports" / "phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md"

METRIC = "query_fixed_radius_threshold_reached_count_sec"
METRIC_SOURCE = f"node_coverage.run_phases.{METRIC}"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _geomean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute geomean for empty values")
    if any(value <= 0.0 for value in values):
        raise ValueError("geomean values must be positive")
    return math.exp(sum(math.log(value) for value in values) / len(values))


def _row_key(row: dict[str, Any]) -> str:
    return "|".join(
        str(row[field])
        for field in ("suite", "app_id", "comparison_group", "backend", "case_id")
    )


def _extract_focused_rows(summary: dict[str, Any], suite: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in summary.get("rows", []):
        if row.get("app_id") != "barnes_hut":
            continue
        payload = row.get("payload") or {}
        node_coverage = payload.get("node_coverage") or {}
        run_phases = node_coverage.get("run_phases") or {}
        sec = float(run_phases[METRIC])
        compact = {
            "suite": suite,
            "app_id": "barnes_hut",
            "backend": row["backend"],
            "case_id": row["case_id"],
            "comparison_group": row["comparison_group"],
            "primary_metric_source": METRIC_SOURCE,
            "sec": sec,
        }
        rows[_row_key(compact)] = compact
    return rows


def _focused_rows(base_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    current_rows: dict[str, dict[str, Any]] = {}
    v2_rows: dict[str, dict[str, Any]] = {}
    for relative, suite in (
        ("current_patched_goal2626_large/summary.json", "goal2626_large"),
        ("current_patched_goal2636_stress/summary.json", "goal2636_stress"),
    ):
        current_rows.update(_extract_focused_rows(_load_json(base_dir / relative), suite))
    for relative, suite in (
        ("v2_14_goal2626_large/summary.json", "goal2626_large"),
        ("v2_14_goal2636_stress/summary.json", "goal2636_stress"),
    ):
        v2_rows.update(_extract_focused_rows(_load_json(base_dir / relative), suite))
    return current_rows, v2_rows


def _projected_rows(
    frozen_rows: list[dict[str, Any]],
    patched_rows: dict[str, dict[str, Any]],
    v2_rows: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    projected: list[dict[str, Any]] = []
    replacements: list[dict[str, Any]] = []
    for row in frozen_rows:
        next_row = dict(row)
        key = _row_key(row)
        if row.get("app_id") == "barnes_hut" and key in patched_rows:
            patched = patched_rows[key]
            v2 = v2_rows[key]
            patched_speedup = float(v2["sec"]) / float(patched["sec"])
            replacements.append(
                {
                    "row_id": key,
                    "suite": row["suite"],
                    "case_id": row["case_id"],
                    "backend": row["backend"],
                    "comparison_group": row["comparison_group"],
                    "frozen_v2_sec": float(row["v2_sec"]),
                    "frozen_v3_sec": float(row["v3_sec"]),
                    "frozen_v3_speedup_vs_v2": float(row["v3_speedup_vs_v2"]),
                    "focused_v2_sec": float(v2["sec"]),
                    "focused_patched_v3_sec": float(patched["sec"]),
                    "focused_patched_v3_speedup_vs_v2": patched_speedup,
                    "primary_metric_source": METRIC_SOURCE,
                }
            )
            next_row["v2_sec"] = float(v2["sec"])
            next_row["v3_sec"] = float(patched["sec"])
            next_row["v3_speedup_vs_v2"] = patched_speedup
        projected.append(next_row)
    return projected, replacements


def _app_geomeans(rows: list[dict[str, Any]]) -> dict[str, float]:
    by_app: dict[str, list[float]] = {}
    for row in rows:
        by_app.setdefault(str(row["app_id"]), []).append(float(row["v3_speedup_vs_v2"]))
    return {app_id: _geomean(values) for app_id, values in sorted(by_app.items())}


def _set_rows(rows: list[dict[str, Any]], classification: dict[str, Any], set_name: str) -> list[dict[str, Any]]:
    row_by_key = {_row_key(row): row for row in rows}
    selected: list[dict[str, Any]] = []
    for app_id, case_ids in classification.get("approved_case_ids_by_app", {}).items():
        labels = classification.get("app_classification", {}).get(app_id, {})
        if labels.get("set") != set_name:
            continue
        case_id_set = set(case_ids)
        for row in rows:
            if row.get("app_id") == app_id and row.get("case_id") in case_id_set:
                selected.append(row_by_key[_row_key(row)])
    return selected


def build_payload(
    frozen_summary: Path = FROZEN_SUMMARY,
    classification_path: Path = CLASSIFICATION,
    focused_dir: Path = FOCUSED_DIR,
    runner_parity_path: Path = RUNNER_PARITY,
) -> dict[str, Any]:
    frozen = _load_json(frozen_summary)
    classification = _load_json(classification_path)
    patched_rows, focused_v2_rows = _focused_rows(focused_dir)
    frozen_rows = list(frozen["same_metric_rows"])
    projected_rows, replacement_rows = _projected_rows(frozen_rows, patched_rows, focused_v2_rows)

    frozen_app_geomeans = _app_geomeans(frozen_rows)
    projected_app_geomeans = _app_geomeans(projected_rows)
    projected_set_a_rows = _set_rows(projected_rows, classification, "A")
    projected_set_b_rows = _set_rows(projected_rows, classification, "B")
    runner = _load_json(runner_parity_path)
    runner_summary = runner.get("summary", {})

    checks = {
        "all_six_barnes_hut_rows_replaced": len(replacement_rows) == 6,
        "focused_metric_sources_match": all(
            row["primary_metric_source"] == METRIC_SOURCE for row in replacement_rows
        ),
        "focused_patch_removes_barnes_hut_severe_regression_projection": (
            projected_app_geomeans["barnes_hut"] >= 0.95
        ),
        "runner_parity_packet_failed_checks_empty": runner.get("failed_checks") == [],
        "runner_parity_with_existing_fused_partner": bool(
            runner_summary.get("runner_parity_with_existing_fused_partner")
        ),
        "runner_claim_flags_false": runner.get("checks", {}).get("all_claim_flags_false") is True,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_barnes_hut_blocker_intake",
        "status": "barnes_hut_focused_fix_intake_not_release",
        "frozen_summary": str(frozen_summary.relative_to(ROOT)),
        "focused_evidence_dir": str(focused_dir.relative_to(ROOT)),
        "runner_parity_summary": str(runner_parity_path.relative_to(ROOT)),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
        "failed_checks": failed_checks,
        "checks": checks,
        "replacement_rows": replacement_rows,
        "projection": {
            "frozen_all_rows_geomean": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in frozen_rows]
            ),
            "projected_all_rows_geomean_if_only_barnes_hut_focused_rows_supersede": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in projected_rows]
            ),
            "frozen_barnes_hut_app_geomean": frozen_app_geomeans["barnes_hut"],
            "projected_barnes_hut_app_geomean": projected_app_geomeans["barnes_hut"],
            "projected_set_a_geomean": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in projected_set_a_rows]
            ),
            "projected_set_b_geomean": _geomean(
                [float(row["v3_speedup_vs_v2"]) for row in projected_set_b_rows]
            ),
            "projected_set_a_app_geomeans": {
                app_id: value
                for app_id, value in projected_app_geomeans.items()
                if classification.get("app_classification", {}).get(app_id, {}).get("set") == "A"
            },
            "projected_set_b_app_geomeans": {
                app_id: value
                for app_id, value in projected_app_geomeans.items()
                if classification.get("app_classification", {}).get(app_id, {}).get("set") == "B"
            },
        },
        "runner_parity": {
            "runner_vs_existing_fused_control_geomean": runner_summary.get(
                "runner_vs_existing_fused_control_geomean"
            ),
            "historical_optix_over_runner_geomean": runner_summary.get(
                "historical_optix_over_runner_geomean"
            ),
            "runner_parity_with_existing_fused_partner": runner_summary.get(
                "runner_parity_with_existing_fused_partner"
            ),
            "historical_optix_reference_is_primary_claim": runner_summary.get(
                "historical_optix_reference_is_primary_claim"
            ),
        },
        "interpretation": {
            "barnes_hut_blocker_state": "focused_generic_runtime_fix_removes_projected_severe_regression_pending_full_all_app_validation",
            "next_resource_decision": "do_not_spend_more_barnes_hut_pod_time_before_attacking_librts_spatial_rayjoin_or_rtnn_rows",
            "why_not_release": "This substitutes focused same-hardware Barnes-Hut evidence only for planning. The frozen all-app scorecard and release gate remain blocked until a reviewed full paired rerun.",
        },
        "goal_level_decision_audit": {
            "decision": "Reclassify Barnes-Hut from active severe-regression target to focused-fix-covered pending full-suite validation.",
            "was_i_foolish": "No for this decision.",
            "foolish_actions": "It would be foolish to keep tuning Barnes-Hut after the generic fixed-radius OptiX hot-path regression is already covered, or to claim release from a focused replacement projection.",
            "other_path": "Run another Barnes-Hut POD or a full all-app suite immediately. That would spend money before the remaining non-Barnes blockers are addressed.",
            "different_path_now": "Record the focused fix, preserve release non-authorization, and redirect engineering to the next unfixed shared-runtime blocker.",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    projection = payload["projection"]
    runner = payload["runner_parity"]
    rows = payload["replacement_rows"]
    lines = [
        "# Phoenix V3 Barnes-Hut Blocker Intake M7",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is a planning and evidence-intake packet, not a release packet.",
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "broad_v3_faster_than_v2_claim_authorized: false",
        "full_all_app_rerun_authorized_by_this_packet: false",
        "```",
        "",
        "## Result",
        "",
        f"- Frozen Barnes-Hut app geomean: `{projection['frozen_barnes_hut_app_geomean']:.6f}x`",
        f"- Projected Barnes-Hut app geomean after focused generic fix: `{projection['projected_barnes_hut_app_geomean']:.6f}x`",
        f"- Frozen all-row geomean: `{projection['frozen_all_rows_geomean']:.6f}x`",
        f"- Projected all-row geomean if only Barnes-Hut rows supersede: `{projection['projected_all_rows_geomean_if_only_barnes_hut_focused_rows_supersede']:.6f}x`",
        f"- Runner vs existing fused-control geomean: `{float(runner['runner_vs_existing_fused_control_geomean']):.6f}x`",
        f"- Historical OptiX frontier over runner geomean: `{float(runner['historical_optix_over_runner_geomean']):.6f}x`",
        "",
        "Interpretation: the old Barnes-Hut severe regression is covered by a",
        "generic prepared OptiX fixed-radius symbol/library-cache fix for planning",
        "purposes, pending the next reviewed full all-app paired run. This does not",
        "authorize release or public performance wording.",
        "",
        "## Replacement Rows",
        "",
        "| row | frozen speedup | focused patched speedup |",
        "| --- | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['suite']} / {row['case_id']}` | "
            f"{row['frozen_v3_speedup_vs_v2']:.3f}x | "
            f"{row['focused_patched_v3_speedup_vs_v2']:.3f}x |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| check | pass |",
            "| --- | --- |",
        ]
    )
    for name, passed in payload["checks"].items():
        lines.append(f"| `{name}` | `{str(bool(passed)).lower()}` |")
    lines.extend(
        [
            "",
            "## Next Resource Decision",
            "",
            payload["interpretation"]["next_resource_decision"],
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
    parser = argparse.ArgumentParser(description="Intake Phoenix V3 Barnes-Hut focused blocker evidence.")
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
