#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLASSIFICATION = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_classification_2026-06-22.json"
)
DEFAULT_SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_serious_v2x_paired_20260622_074100"
    / "summary.json"
)
DEFAULT_JSON_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json"
)
DEFAULT_MD_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _geomean(values: list[float]) -> float | None:
    positives = [value for value in values if value > 0.0]
    if not positives:
        return None
    return math.exp(sum(math.log(value) for value in positives) / len(positives))


def _row_id(row: dict[str, Any]) -> str:
    return "|".join(
        str(row.get(key, ""))
        for key in ("suite", "app_id", "comparison_group", "backend", "case_id")
    )


def _classify_rows(
    rows: list[dict[str, Any]],
    app_classification: dict[str, dict[str, Any]],
    approved_case_ids_by_app: dict[str, list[str]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    classified: list[dict[str, Any]] = []
    unclassified: list[dict[str, Any]] = []
    unapproved_case_rows: list[dict[str, Any]] = []
    for row in rows:
        app_id = str(row.get("app_id"))
        case_id = str(row.get("case_id"))
        app_rule = app_classification.get(app_id)
        if not app_rule:
            unclassified.append({"row_id": _row_id(row), "app_id": app_id})
            continue
        approved_case_ids = set((approved_case_ids_by_app or {}).get(app_id, []))
        case_id_whitelisted = not approved_case_ids_by_app or case_id in approved_case_ids
        if not case_id_whitelisted:
            unapproved_case_rows.append(
                {"row_id": _row_id(row), "app_id": app_id, "case_id": case_id}
            )
        classified.append(
            {
                "row_id": _row_id(row),
                "suite": row.get("suite"),
                "app_id": app_id,
                "comparison_group": row.get("comparison_group"),
                "backend": row.get("backend"),
                "case_id": case_id,
                "case_id_whitelisted": case_id_whitelisted,
                "set": app_rule.get("set"),
                "label": app_rule.get("label"),
                "rationale": app_rule.get("rationale"),
                "v3_speedup_vs_v2": row.get("v3_speedup_vs_v2"),
            }
        )
    return classified, unclassified, unapproved_case_rows


def _verified_focused_probes(classification: dict[str, Any]) -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []
    for probe in classification.get("current_precondition_state", {}).get(
        "focused_productized_material_probes", []
    ):
        path_text = probe.get("path")
        path = ROOT / path_text if isinstance(path_text, str) else None
        probes.append(
            {
                **probe,
                "path_exists": bool(path and path.exists()),
            }
        )
    return probes


def _app_geomeans(classified_rows: list[dict[str, Any]], set_name: str) -> dict[str, float]:
    by_app: dict[str, list[float]] = {}
    for row in classified_rows:
        if row.get("set") != set_name:
            continue
        value = row.get("v3_speedup_vs_v2")
        if not isinstance(value, (int, float)) or value <= 0:
            continue
        by_app.setdefault(str(row.get("app_id")), []).append(float(value))
    out: dict[str, float] = {}
    for app_id, values in by_app.items():
        geomean = _geomean(values)
        if geomean is not None:
            out[app_id] = geomean
    return out


def _set_geomean(classified_rows: list[dict[str, Any]], set_name: str) -> float | None:
    values = [
        float(row["v3_speedup_vs_v2"])
        for row in classified_rows
        if row.get("set") == set_name
        and isinstance(row.get("v3_speedup_vs_v2"), (int, float))
        and float(row["v3_speedup_vs_v2"]) > 0
    ]
    return _geomean(values)


def build_payload(
    summary_path: Path = DEFAULT_SUMMARY,
    classification_path: Path = DEFAULT_CLASSIFICATION,
) -> dict[str, Any]:
    classification = _read_json(classification_path)
    summary = _read_json(summary_path)
    thresholds = classification.get("thresholds", {})
    app_classification = classification.get("app_classification", {})
    approved_case_ids_by_app = classification.get("approved_case_ids_by_app", {})
    rows = list(summary.get("same_metric_rows", []))
    classified_rows, unclassified_rows, unapproved_case_rows = _classify_rows(
        rows, app_classification, approved_case_ids_by_app
    )

    set_a_app_geomeans = _app_geomeans(classified_rows, "A")
    set_b_app_geomeans = _app_geomeans(classified_rows, "B")
    set_a_geomean = _set_geomean(classified_rows, "A")
    set_b_geomean = _set_geomean(classified_rows, "B")
    set_a_win_threshold = float(thresholds.get("set_a_app_geomean_win_threshold", 1.05))
    set_a_severe_floor = float(thresholds.get("set_a_app_severe_regression_floor", 0.90))
    set_a_required_fraction = float(
        thresholds.get("set_a_required_fraction_apps_over_threshold", 0.75)
    )
    set_a_required_app_wins = math.ceil(set_a_required_fraction * len(set_a_app_geomeans))
    set_a_apps_over_threshold = sum(
        1 for value in set_a_app_geomeans.values() if value > set_a_win_threshold
    )
    set_a_severe_regression_apps = {
        app_id: value for app_id, value in set_a_app_geomeans.items() if value < set_a_severe_floor
    }
    set_b_row_floor = float(thresholds.get("set_b_row_regression_floor", 0.95))
    set_b_rows_below_floor = [
        row
        for row in classified_rows
        if row.get("set") == "B"
        and isinstance(row.get("v3_speedup_vs_v2"), (int, float))
        and float(row["v3_speedup_vs_v2"]) < set_b_row_floor
    ]
    current_preconditions = classification.get("current_precondition_state", {})
    claimed_focused_count = int(current_preconditions.get("focused_productized_material_probe_count", 0))
    verified_focused_probes = _verified_focused_probes(classification)
    verified_focused_count = sum(1 for probe in verified_focused_probes if probe.get("path_exists") is True)
    required_focused_count = int(
        thresholds.get("required_focused_productized_material_probe_count_before_full_all_app_pod_run", 2)
    )
    all_app_pod_spend_authorized = (
        verified_focused_count >= required_focused_count
        and not set_b_rows_below_floor
        and not set_a_severe_regression_apps
        and not unclassified_rows
        and not unapproved_case_rows
    )

    set_a_pass = (
        set_a_geomean is not None
        and set_a_geomean >= float(thresholds.get("set_a_geomean_v3_vs_v2_min", 1.2))
        and set_a_apps_over_threshold >= set_a_required_app_wins
    )
    set_b_pass = (
        set_b_geomean is not None
        and set_b_geomean >= float(thresholds.get("set_b_geomean_v3_vs_v2_min", 0.98))
        and not set_b_rows_below_floor
    )
    release_candidate_under_two_number_bar = (
        classification.get("classification_frozen_before_next_full_paired_run") is True
        and not unclassified_rows
        and not unapproved_case_rows
        and all_app_pod_spend_authorized
        and set_a_pass
        and set_b_pass
    )

    checks = {
        "classification_file_exists": classification_path.exists(),
        "summary_file_exists": summary_path.exists(),
        "classification_frozen_before_next_full_paired_run": (
            classification.get("classification_frozen_before_next_full_paired_run") is True
        ),
        "case_id_whitelist_frozen": classification.get("case_id_whitelist_frozen") is True,
        "release_authorized_false": classification.get("release_authorized") is False,
        "public_speedup_claim_authorized_false": (
            classification.get("public_speedup_claim_authorized") is False
        ),
        "broad_v3_faster_than_v2_claim_authorized_false": (
            classification.get("broad_v3_faster_than_v2_claim_authorized") is False
        ),
        "all_current_rows_classified": not unclassified_rows,
        "all_current_case_ids_whitelisted": not unapproved_case_rows,
        "focused_probe_count_verified_from_artifacts": (
            verified_focused_count == claimed_focused_count
            and all(probe.get("path_exists") is True for probe in verified_focused_probes)
        ),
        "both_sets_present": bool(set_a_app_geomeans) and bool(set_b_app_geomeans),
        "set_a_current_scorecard_blocks_release": not set_a_pass,
        "set_a_severe_regressions_identified": bool(set_a_severe_regression_apps),
        "set_a_severe_regressions_block_pod_spend": (
            bool(set_a_severe_regression_apps) and not all_app_pod_spend_authorized
        ),
        "set_b_current_regressions_identified": bool(set_b_rows_below_floor),
        "set_b_regressions_block_pod_spend": (
            bool(set_b_rows_below_floor) and not all_app_pod_spend_authorized
        ),
        "pod_spend_precondition_currently_blocks_full_run": not all_app_pod_spend_authorized,
        "release_candidate_under_two_number_bar_false": not release_candidate_under_two_number_bar,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_set_ab_scorecard_gate",
        "status": "classification_frozen_current_scorecard_not_release",
        "classification_path": str(classification_path.relative_to(ROOT)),
        "summary_path": str(summary_path.relative_to(ROOT)),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_spend_authorized": all_app_pod_spend_authorized,
        "release_candidate_under_two_number_bar": release_candidate_under_two_number_bar,
        "failed_checks": failed_checks,
        "checks": checks,
        "scorecard": {
            "row_count": len(rows),
            "classified_row_count": len(classified_rows),
            "unclassified_row_count": len(unclassified_rows),
            "set_a_row_count": sum(1 for row in classified_rows if row.get("set") == "A"),
            "set_b_row_count": sum(1 for row in classified_rows if row.get("set") == "B"),
            "set_a_geomean_v3_vs_v2": set_a_geomean,
            "set_b_geomean_v3_vs_v2": set_b_geomean,
            "set_a_app_geomeans_v3_vs_v2": dict(sorted(set_a_app_geomeans.items())),
            "set_b_app_geomeans_v3_vs_v2": dict(sorted(set_b_app_geomeans.items())),
            "set_a_apps_over_1_05x": set_a_apps_over_threshold,
            "set_a_required_apps_over_1_05x": set_a_required_app_wins,
            "set_a_severe_regression_floor": set_a_severe_floor,
            "set_a_severe_regression_apps": dict(sorted(set_a_severe_regression_apps.items())),
            "set_b_rows_below_0_95x": len(set_b_rows_below_floor),
            "set_b_rows_below_0_95x_ids": [row["row_id"] for row in set_b_rows_below_floor],
            "focused_productized_material_probe_count_claimed": claimed_focused_count,
            "focused_productized_material_probe_count_verified": verified_focused_count,
            "verified_focused_productized_material_probes": verified_focused_probes,
            "required_focused_productized_material_probe_count_before_full_all_app_pod_run": (
                required_focused_count
            ),
            "missing_focused_productized_material_probe_count": max(
                0, required_focused_count - verified_focused_count
            ),
        },
        "row_classifications": classified_rows,
        "unclassified_rows": unclassified_rows,
        "unapproved_case_rows": unapproved_case_rows,
        "goal_level_decision_audit": classification.get("goal_level_decision_audit", {}),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    scorecard = payload["scorecard"]
    focused_verified = scorecard["focused_productized_material_probe_count_verified"]
    focused_required = scorecard["required_focused_productized_material_probe_count_before_full_all_app_pod_run"]
    missing_focused = scorecard["missing_focused_productized_material_probe_count"]
    if missing_focused:
        pod_precondition_lines = [
            "an identified sub-0.95x control row, and the precondition for another",
            "full all-app pod run is not met because focused material productized",
            f"probes are only {focused_verified}/{focused_required}.",
        ]
    else:
        pod_precondition_lines = [
            "an identified sub-0.95x control row. The focused material",
            f"productized-probe precondition is closed at {focused_verified}/{focused_required}, but",
            "full all-app pod spend remains blocked by the Set-A severe regression,",
            "the Set-A app-win/geomean shortfall, and the Set-B parity row.",
        ]
    lines = [
        "# Phoenix V3 Set A / Set B Scorecard Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}",
        f"all_app_pod_spend_authorized: {str(payload['all_app_pod_spend_authorized']).lower()}",
        f"release_candidate_under_two_number_bar: {str(payload['release_candidate_under_two_number_bar']).lower()}",
        "```",
        "",
        "## Current Scorecard",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Rows classified | {scorecard['classified_row_count']} / {scorecard['row_count']} |",
        f"| Set A rows | {scorecard['set_a_row_count']} |",
        f"| Set B rows | {scorecard['set_b_row_count']} |",
        f"| Set A geomean | {scorecard['set_a_geomean_v3_vs_v2']:.3f}x |",
        f"| Set B geomean | {scorecard['set_b_geomean_v3_vs_v2']:.3f}x |",
        f"| Set A apps over 1.05x | {scorecard['set_a_apps_over_1_05x']} / {scorecard['set_a_required_apps_over_1_05x']} required |",
        f"| Set A severe regressions below {scorecard['set_a_severe_regression_floor']:.2f}x | {len(scorecard['set_a_severe_regression_apps'])} |",
        f"| Set B rows below 0.95x | {scorecard['set_b_rows_below_0_95x']} |",
        f"| Focused material productized probes | {scorecard['focused_productized_material_probe_count_verified']} / {scorecard['required_focused_productized_material_probe_count_before_full_all_app_pod_run']} required |",
        "",
        "## Set A App Geomeans",
        "",
        "| App | V3 vs V2.14 |",
        "| --- | ---: |",
    ]
    for app_id, value in scorecard["set_a_app_geomeans_v3_vs_v2"].items():
        lines.append(f"| `{app_id}` | {value:.3f}x |")
    lines.extend(["", "## Set B App Geomeans", "", "| App | V3 vs V2.14 |", "| --- | ---: |"])
    for app_id, value in scorecard["set_b_app_geomeans_v3_vs_v2"].items():
        lines.append(f"| `{app_id}` | {value:.3f}x |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The frozen classification makes the current failure more precise:",
            "Set A does not show material productized-path superiority, Set B has",
            *pod_precondition_lines,
            "",
            "This gate does not authorize release or public performance wording.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phoenix V3 Set A / Set B scorecard gate.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.summary, args.classification)
    json_text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json_text)
    return 2 if payload["failed_checks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
