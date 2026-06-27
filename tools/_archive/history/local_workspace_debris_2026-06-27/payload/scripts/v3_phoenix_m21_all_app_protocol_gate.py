#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json"
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_id(row: dict[str, Any]) -> str:
    return "|".join(
        str(row.get(key, ""))
        for key in ("suite", "app_id", "comparison_group", "backend", "case_id")
    )


def _threshold(fail_if: str) -> float:
    match = re.search(r"<\s*([0-9.]+)", fail_if)
    if not match:
        raise ValueError(f"Unsupported fail_if expression: {fail_if}")
    return float(match.group(1))


def _geomean(values: list[float]) -> float | None:
    positives = [value for value in values if value > 0.0]
    if not positives:
        return None
    return math.exp(sum(math.log(value) for value in positives) / len(positives))


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _classified_rows(
    summary: dict[str, Any],
    protocol: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    whitelist = protocol["frozen_case_id_whitelist"]
    app_sets = whitelist["app_classification"]
    approved_cases = whitelist["approved_case_ids_by_app"]
    classified: list[dict[str, Any]] = []
    scope_failures: list[dict[str, Any]] = []

    for row in summary.get("same_metric_rows", []):
        app_id = str(row.get("app_id"))
        case_id = str(row.get("case_id"))
        row_id = _row_id(row)
        if app_id not in app_sets:
            scope_failures.append(
                {"row_id": row_id, "reason": "unknown_app_id", "app_id": app_id}
            )
            continue
        if case_id not in set(approved_cases.get(app_id, [])):
            scope_failures.append(
                {
                    "row_id": row_id,
                    "reason": "unknown_case_id",
                    "app_id": app_id,
                    "case_id": case_id,
                }
            )
            continue
        speedup = row.get("v3_speedup_vs_v2")
        if not isinstance(speedup, (int, float)) or speedup <= 0:
            scope_failures.append(
                {"row_id": row_id, "reason": "missing_positive_speedup", "app_id": app_id}
            )
            continue
        classified.append({**row, "row_id": row_id, "set": app_sets[app_id]})

    return classified, scope_failures


def _app_geomeans(rows: list[dict[str, Any]]) -> dict[str, float]:
    by_app: dict[str, list[float]] = {}
    for row in rows:
        by_app.setdefault(str(row["app_id"]), []).append(float(row["v3_speedup_vs_v2"]))
    return {
        app_id: geomean
        for app_id, values in sorted(by_app.items())
        if (geomean := _geomean(values)) is not None
    }


def _set_geomean(rows: list[dict[str, Any]], set_name: str) -> float | None:
    return _geomean(
        [
            float(row["v3_speedup_vs_v2"])
            for row in rows
            if row.get("set") == set_name
        ]
    )


def _suite_correctness_failures(summary: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    release_bar = summary.get("release_consideration_bar", {})
    if release_bar.get("all_required_suites_finished") is not True:
        failures.append({"gate": "all_required_suites_finished", "actual": release_bar.get("all_required_suites_finished")})
    if release_bar.get("primary_metric_source_mismatch_count") != 0:
        failures.append(
            {
                "gate": "primary_metric_source_mismatch_count",
                "actual": release_bar.get("primary_metric_source_mismatch_count"),
            }
        )
    if release_bar.get("missing_promoted_apps") not in ([], None):
        failures.append(
            {
                "gate": "missing_promoted_apps",
                "actual": release_bar.get("missing_promoted_apps"),
            }
        )

    suite_status = summary.get("suite_status", {})
    for suite_key, status in sorted(suite_status.items()):
        if status.get("missing"):
            failures.append({"gate": "suite_status", "suite": suite_key, "reason": "missing"})
        if status.get("failed", 0) not in (0, None):
            failures.append(
                {
                    "gate": "suite_status",
                    "suite": suite_key,
                    "reason": "failed_rows",
                    "failed": status.get("failed"),
                }
            )
        if "all_pass" in status and status.get("all_pass") is not True:
            failures.append(
                {"gate": "suite_status", "suite": suite_key, "reason": "all_pass_false"}
            )
    return failures


def build_payload(summary_path: Path = DEFAULT_SUMMARY, protocol_path: Path = DEFAULT_PROTOCOL) -> dict[str, Any]:
    protocol = _read_json(protocol_path)
    summary = _read_json(summary_path)
    classified_rows, scope_failures = _classified_rows(summary, protocol)
    correctness_failures = _suite_correctness_failures(summary)
    app_geomeans = _app_geomeans(classified_rows)
    set_a_geomean = _set_geomean(classified_rows, "A")
    set_b_geomean = _set_geomean(classified_rows, "B")
    row_by_id = {row["row_id"]: row for row in classified_rows}

    bars = {bar["id"]: bar for bar in protocol["fail_closed_bars"]}
    protocol_failures: list[dict[str, Any]] = []

    barnes_threshold = _threshold(bars["barnes_hut_app_geomean_floor"]["fail_if"])
    barnes_value = app_geomeans.get("barnes_hut")
    if barnes_value is None or barnes_value < barnes_threshold:
        protocol_failures.append(
            {
                "bar": "barnes_hut_app_geomean_floor",
                "actual": barnes_value,
                "threshold": barnes_threshold,
            }
        )

    librts_bar = bars["librts_embree_aabb_index_row_floor"]
    librts_row = row_by_id.get(librts_bar["row_id"])
    librts_threshold = _threshold(librts_bar["fail_if"])
    librts_value = None if librts_row is None else float(librts_row["v3_speedup_vs_v2"])
    if librts_value is None or librts_value < librts_threshold:
        protocol_failures.append(
            {
                "bar": "librts_embree_aabb_index_row_floor",
                "row_id": librts_bar["row_id"],
                "actual": librts_value,
                "threshold": librts_threshold,
            }
        )

    set_b_threshold = _threshold(bars["set_b_geomean_floor"]["fail_if"])
    if set_b_geomean is None or set_b_geomean < set_b_threshold:
        protocol_failures.append(
            {
                "bar": "set_b_geomean_floor",
                "actual": set_b_geomean,
                "threshold": set_b_threshold,
            }
        )

    severe_threshold = _threshold(bars["new_app_level_severe_regression_floor"]["fail_if"])
    severe_app_regressions = {
        app_id: value for app_id, value in app_geomeans.items() if value < severe_threshold
    }
    for app_id, value in severe_app_regressions.items():
        protocol_failures.append(
            {
                "bar": "new_app_level_severe_regression_floor",
                "app_id": app_id,
                "actual": value,
                "threshold": severe_threshold,
            }
        )

    watch_alerts: list[dict[str, Any]] = []
    for watch in protocol.get("watch_rows", []):
        row = row_by_id.get(watch["row_id"])
        watch_value = None if row is None else float(row["v3_speedup_vs_v2"])
        alert_threshold = _threshold(watch["alert_if"])
        if watch_value is None or watch_value < alert_threshold:
            watch_alerts.append(
                {
                    "watch_row": watch["id"],
                    "row_id": watch["row_id"],
                    "actual": watch_value,
                    "threshold": alert_threshold,
                    "policy": watch["alert_policy"],
                }
            )

    set_a_app_wins_gt_1_05 = sum(1 for app_id, value in app_geomeans.items() if app_id in protocol["frozen_case_id_whitelist"]["app_classification"] and protocol["frozen_case_id_whitelist"]["app_classification"][app_id] == "A" and value > 1.05)
    correctness_or_scope_failed = bool(scope_failures or correctness_failures)
    blocking_bars_failed = bool(protocol_failures)
    if correctness_or_scope_failed:
        status = "protocol_fail_invalid_or_out_of_scope"
    elif blocking_bars_failed:
        status = "protocol_fail_blocking_bars_not_cleared"
    elif watch_alerts:
        status = "blocking_bars_cleared_watch_alerts_present_not_release"
    else:
        status = "blocking_bars_cleared_scorecard_baseline_advanced_not_release"

    return {
        "tool": "v3_phoenix_m21_all_app_protocol_gate",
        "status": status,
        "protocol_path": _rel(protocol_path),
        "summary_path": _rel(summary_path),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_run_authorized_after_result": False,
        "scope_failures": scope_failures,
        "correctness_failures": correctness_failures,
        "protocol_failures": protocol_failures,
        "watch_alerts": watch_alerts,
        "documented_values": {
            "overall_geomean_v3_vs_v2": summary.get("v3_geomean_speedup_vs_v2"),
            "set_a_geomean_v3_vs_v2": set_a_geomean,
            "set_a_apps_over_1_05x": set_a_app_wins_gt_1_05,
            "set_b_geomean_v3_vs_v2": set_b_geomean,
            "app_geomeans_v3_vs_v2": app_geomeans,
            "same_metric_comparison_count": summary.get("same_metric_comparison_count"),
        },
        "post_run_interpretation": protocol["post_run_interpretation"][status]
        if status in protocol["post_run_interpretation"]
        else (
            protocol["post_run_interpretation"]["if_case_or_correctness_gate_fails"]
            if correctness_or_scope_failed
            else protocol["post_run_interpretation"]["if_any_fail_closed_bar_fails"]
            if blocking_bars_failed
            else protocol["post_run_interpretation"]["if_all_fail_closed_bars_clear"]
        ),
        "goal_level_decision_audit": {
            "decision": "Evaluate a completed all-app POD run against the M21 protocol instead of interpreting it manually.",
            "was_i_foolish": "No for this decision.",
            "foolish_actions": "It would be foolish to rely on prose-only fail bars after a costly run produces many rows.",
            "other_path": "Use the older Set-A/B scorecard gate alone. That gate was built for the old failure baseline and is not the M21 run verdict.",
            "different_path_now": "Use this dedicated protocol gate to make run outcome interpretation fail-closed and repeatable.",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    values = payload["documented_values"]
    lines = [
        "# Phoenix V3 M21 All-App Protocol Gate Result",
        "",
        f"Status: `{payload['status']}`",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}",
        "```",
        "",
        "## Documented Values",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Overall geomean V3 vs V2.14 | {values['overall_geomean_v3_vs_v2']:.3f}x |",
        f"| Set-A geomean V3 vs V2.14 | {values['set_a_geomean_v3_vs_v2']:.3f}x |",
        f"| Set-A apps over 1.05x | {values['set_a_apps_over_1_05x']} |",
        f"| Set-B geomean V3 vs V2.14 | {values['set_b_geomean_v3_vs_v2']:.3f}x |",
        f"| Same-metric rows | {values['same_metric_comparison_count']} |",
        "",
        "## Protocol Failures",
        "",
    ]
    if payload["protocol_failures"]:
        lines.extend(["| Bar | Actual | Threshold |", "| --- | ---: | ---: |"])
        for failure in payload["protocol_failures"]:
            actual = failure.get("actual")
            actual_text = "missing" if actual is None else f"{actual:.3f}x"
            lines.append(
                f"| `{failure['bar']}` | {actual_text} | {failure['threshold']:.3f}x |"
            )
    else:
        lines.append("None.")

    lines.extend(["", "## Scope / Correctness Failures", ""])
    if payload["scope_failures"] or payload["correctness_failures"]:
        lines.append("```json")
        lines.append(
            json.dumps(
                {
                    "scope_failures": payload["scope_failures"],
                    "correctness_failures": payload["correctness_failures"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        lines.append("```")
    else:
        lines.append("None.")

    lines.extend(["", "## Watch Alerts", ""])
    if payload["watch_alerts"]:
        lines.append("```json")
        lines.append(json.dumps(payload["watch_alerts"], indent=2, sort_keys=True))
        lines.append("```")
    else:
        lines.append("None.")

    lines.extend(["", "## Interpretation", "", payload["post_run_interpretation"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate all-app result against Phoenix V3 M21 protocol.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.summary, args.protocol)
    json_text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json_text)
    return 0 if payload["status"].endswith("_not_release") and not payload["protocol_failures"] and not payload["scope_failures"] and not payload["correctness_failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
