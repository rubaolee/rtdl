#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
from typing import Any


SUITES = ("goal2626_large", "goal2636_stress", "goal3828_full")
EXPECTED_TREES = ("v2_14", "current")
EXPECTED_BENCHMARK_APPS = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
    "contact_manifold",
)
RELEASE_CONSIDERATION_MIN_GEOMEAN = 1.20
RELEASE_CONSIDERATION_MIN_APP_WINS = 8
APP_WIN_THRESHOLD = 1.05
APP_REGRESSION_FLOOR = 0.95


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _geomean(values: list[float]) -> float | None:
    positives = [value for value in values if value > 0.0]
    if not positives:
        return None
    return math.exp(sum(math.log(value) for value in positives) / len(positives))


def _read_status_tsv(run_dir: Path) -> list[dict[str, str]]:
    path = run_dir / "status.tsv"
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        tree, suite, rc, started, ended = parts
        rows.append(
            {
                "tree": tree,
                "suite": suite,
                "rc": rc,
                "started": started,
                "ended": ended,
            }
        )
    return rows


def _suite_summary(run_dir: Path, tree: str, suite: str) -> dict[str, Any]:
    if suite == "goal3828_full":
        path = run_dir / f"{tree}_{suite}.json"
        if not path.exists():
            return {"rows": 0, "ok": 0, "failed": 0, "missing": True}
        payload = _read_json(path)
        rows = payload.get("rows", [])
        return {
            "rows": len(rows),
            "pass": sum(1 for row in rows if row.get("status") == "pass"),
            "failed": sum(1 for row in rows if row.get("status") != "pass"),
            "all_pass": payload.get("all_pass") is True,
            "json_pass_count": payload.get("json_pass_count"),
        }

    path = run_dir / f"{tree}_{suite}" / "summary.json"
    if not path.exists():
        return {"rows": 0, "ok": 0, "failed": 0, "missing": True}
    payload = _read_json(path)
    rows = payload.get("rows", [])
    return {
        "rows": len(rows),
        "ok": sum(1 for row in rows if row.get("status") == "ok"),
        "failed": sum(1 for row in rows if row.get("status") != "ok"),
    }


def _all_required_suites_finished(status_rows: list[dict[str, str]]) -> bool:
    by_pair = {(row["tree"], row["suite"]): row for row in status_rows}
    for tree in EXPECTED_TREES:
        for suite in SUITES:
            row = by_pair.get((tree, suite))
            if row is None or row.get("rc") != "0":
                return False
    return True


def _primary_rows(run_dir: Path, tree: str, suite: str) -> list[dict[str, Any]]:
    if suite == "goal3828_full":
        return []
    path = run_dir / f"{tree}_{suite}" / "summary.json"
    if not path.exists():
        return []
    return list(_read_json(path).get("rows", []))


def _row_key(suite: str, row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        suite,
        str(row.get("app_id")),
        str(row.get("comparison_group")),
        str(row.get("backend")),
        str(row.get("case_id")),
    )


def _build_same_metric_rows(run_dir: Path) -> list[dict[str, Any]]:
    pairs: dict[tuple[str, str, str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for suite in ("goal2626_large", "goal2636_stress"):
        for tree in ("v2_14", "current"):
            for row in _primary_rows(run_dir, tree, suite):
                pairs[_row_key(suite, row)][tree] = row

    out: list[dict[str, Any]] = []
    for key, by_tree in sorted(pairs.items()):
        v2 = by_tree.get("v2_14")
        v3 = by_tree.get("current")
        if not v2 or not v3:
            continue
        v2_metric = v2.get("primary_metric_sec")
        v3_metric = v3.get("primary_metric_sec")
        if not isinstance(v2_metric, (int, float)) or not isinstance(v3_metric, (int, float)):
            continue
        if v2_metric <= 0 or v3_metric <= 0:
            continue
        suite, app_id, comparison_group, backend, case_id = key
        out.append(
            {
                "suite": suite,
                "app_id": app_id,
                "comparison_group": comparison_group,
                "backend": backend,
                "case_id": case_id,
                "v2_sec": float(v2_metric),
                "v3_sec": float(v3_metric),
                "v3_speedup_vs_v2": float(v2_metric) / float(v3_metric),
                "primary_metric_source_v2": v2.get("primary_metric_source"),
                "primary_metric_source_v3": v3.get("primary_metric_source"),
            }
        )
    return out


def _build_ratio_change_rows(run_dir: Path) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, dict[str, dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for suite in ("goal2626_large", "goal2636_stress"):
        for tree in ("v2_14", "current"):
            for row in _primary_rows(run_dir, tree, suite):
                metric = row.get("primary_metric_sec")
                if row.get("status") != "ok" or not isinstance(metric, (int, float)) or metric <= 0:
                    continue
                key = (suite, str(row.get("app_id")), str(row.get("comparison_group")))
                grouped[key][tree][str(row.get("backend"))] = row

    out: list[dict[str, Any]] = []
    for (suite, app_id, comparison_group), by_tree in sorted(grouped.items()):
        v2 = by_tree.get("v2_14", {})
        v3 = by_tree.get("current", {})
        if not {"embree", "optix"}.issubset(v2) or not {"embree", "optix"}.issubset(v3):
            continue
        v2_ratio = float(v2["embree"]["primary_metric_sec"]) / float(v2["optix"]["primary_metric_sec"])
        v3_ratio = float(v3["embree"]["primary_metric_sec"]) / float(v3["optix"]["primary_metric_sec"])
        out.append(
            {
                "suite": suite,
                "app_id": app_id,
                "comparison_group": comparison_group,
                "v2_optix_vs_embree": v2_ratio,
                "v3_optix_vs_embree": v3_ratio,
                "v3_ratio_change_vs_v2": v3_ratio / v2_ratio if v2_ratio > 0 else None,
                "interpretation": _ratio_interpretation(v2_ratio, v3_ratio),
            }
        )
    return out


def _ratio_interpretation(v2_ratio: float, v3_ratio: float) -> str:
    if v2_ratio < 1.0 and v3_ratio < 1.0:
        return "OptiX slower than Embree in both V2.14 and V3; investigate workload/route fit before blaming the V3 delta."
    if v2_ratio >= 1.0 and v3_ratio < 1.0:
        return "OptiX regressed from faster-than-Embree in V2.14 to slower-than-Embree in V3."
    if v2_ratio < 1.0 and v3_ratio >= 1.0:
        return "OptiX crossed from slower-than-Embree in V2.14 to faster-than-Embree in V3."
    if v3_ratio >= v2_ratio * 1.05:
        return "OptiX remains faster than Embree and improved its relative margin in V3."
    if v3_ratio <= v2_ratio * 0.95:
        return "OptiX remains faster than Embree but lost relative margin in V3."
    return "OptiX-vs-Embree relative margin is broadly unchanged."


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Serious V2.x Paired Benchmark",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This packet compares V2.14 and current Phoenix V3 on the same RT hardware",
        "using serious all-benchmark-app suites. It does not authorize release by itself.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        "public_speedup_claim_authorized: false",
        "broad_v3_faster_than_v2_claim_authorized: false",
        f"same_metric_comparison_count: {payload['same_metric_comparison_count']}",
        f"V3 faster by >5%: {payload['v3_faster_count_gt_5pct']}",
        f"Within +/-5%: {payload['similar_count_within_5pct']}",
        f"V3 slower by >5%: {payload['v3_slower_count_gt_5pct']}",
        f"Geomean V3 speedup vs V2.14: {payload['v3_geomean_speedup_vs_v2']:.3f}x",
        f"release_consideration_eligible: {str(payload['release_consideration_eligible']).lower()}",
        "```",
        "",
        "## Preregistered Bar",
        "",
        "```text",
        "overall_geomean_v3_speedup_vs_v2 >= 1.20x",
        "at least 8 of 10 app geomeans > 1.05x",
        "no app geomean < 0.95x without accepted explanation",
        "all required suites must finish with rc=0",
        "```",
        "",
        "## Suite Status",
        "",
        "| Suite | V2.14 | Current V3 |",
        "| --- | --- | --- |",
    ]
    for suite in SUITES:
        lines.append(
            f"| `{suite}` | `{payload['suite_status'].get('v2_14_' + suite)}` | "
            f"`{payload['suite_status'].get('current_' + suite)}` |"
        )

    lines.extend(["", "## App Geomean", "", "| App | V3 speedup vs V2.14 |", "| --- | ---: |"])
    for app, value in sorted(payload["app_geomean_speedup_vs_v2"].items()):
        lines.append(f"| `{app}` | {value:.3f}x |")

    lines.extend(
        [
            "",
            "## App Coverage",
            "",
            "```text",
            f"expected_promoted_app_count: {payload['release_consideration_bar']['expected_promoted_app_count']}",
            f"actual_promoted_app_count: {payload['release_consideration_bar']['actual_promoted_app_count']}",
            f"missing_promoted_apps: {payload['release_consideration_bar']['missing_promoted_apps']}",
            f"primary_metric_source_mismatch_count: {payload['primary_metric_source_mismatch_count']}",
            "```",
        ]
    )

    lines.extend(["", "## Strongest V3 Wins", "", "| Suite | App | Case | Backend | Speedup |", "| --- | --- | --- | --- | ---: |"])
    for row in payload["top_v3_faster_rows"][:12]:
        lines.append(
            f"| `{row['suite']}` | `{row['app_id']}` | `{row['case_id']}` | `{row['backend']}` | "
            f"{row['v3_speedup_vs_v2']:.3f}x |"
        )

    lines.extend(["", "## Strongest V3 Losses", "", "| Suite | App | Case | Backend | Speedup |", "| --- | --- | --- | --- | ---: |"])
    for row in payload["top_v3_slower_rows"][:12]:
        lines.append(
            f"| `{row['suite']}` | `{row['app_id']}` | `{row['case_id']}` | `{row['backend']}` | "
            f"{row['v3_speedup_vs_v2']:.3f}x |"
        )

    lines.extend(
        [
            "",
            "## OptiX vs Embree Explanation Rows",
            "",
            "| Suite | App | Group | V2.14 OptiX/Embree | V3 OptiX/Embree | Change | Interpretation |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["optix_vs_embree_ratio_change_rows"]:
        change = row.get("v3_ratio_change_vs_v2")
        change_text = "n/a" if change is None else f"{change:.3f}x"
        lines.append(
            f"| `{row['suite']}` | `{row['app_id']}` | `{row['comparison_group']}` | "
            f"{row['v2_optix_vs_embree']:.3f}x | {row['v3_optix_vs_embree']:.3f}x | "
            f"{change_text} | {row['interpretation']} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is serious evidence, not a release claim. If the geomean and app-level",
            "results do not show broad material V3 superiority, Phoenix V3 remains",
            "`redo_required` and the losing rows define the next generic runtime work.",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(run_dir: Path) -> dict[str, Any]:
    same_rows = _build_same_metric_rows(run_dir)
    speedups = [row["v3_speedup_vs_v2"] for row in same_rows]
    by_app: dict[str, list[float]] = defaultdict(list)
    for row in same_rows:
        by_app[row["app_id"]].append(row["v3_speedup_vs_v2"])

    app_geomean = {app: value for app, values in by_app.items() if (value := _geomean(values)) is not None}
    missing_apps = sorted(set(EXPECTED_BENCHMARK_APPS) - set(app_geomean))
    top_faster = sorted(same_rows, key=lambda row: row["v3_speedup_vs_v2"], reverse=True)
    top_slower = sorted(same_rows, key=lambda row: row["v3_speedup_vs_v2"])
    geomean = _geomean(speedups) or 0.0
    status_rows = _read_status_tsv(run_dir)
    all_required_suites_finished = _all_required_suites_finished(status_rows)
    app_win_count = sum(1 for value in app_geomean.values() if value > APP_WIN_THRESHOLD)
    app_regression_count = sum(1 for value in app_geomean.values() if value < APP_REGRESSION_FLOOR)
    source_mismatch_rows = [
        row
        for row in same_rows
        if row.get("primary_metric_source_v2") != row.get("primary_metric_source_v3")
    ]
    release_consideration_eligible = (
        all_required_suites_finished
        and not missing_apps
        and not source_mismatch_rows
        and geomean >= RELEASE_CONSIDERATION_MIN_GEOMEAN
        and app_win_count >= RELEASE_CONSIDERATION_MIN_APP_WINS
        and app_regression_count == 0
    )

    return {
        "tool": "phoenix_v3_serious_v2x_paired_analysis",
        "artifact": str(run_dir),
        "status": "serious_paired_evidence_not_release",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "release_consideration_eligible": release_consideration_eligible,
        "release_consideration_bar": {
            "all_required_suites_finished": all_required_suites_finished,
            "expected_promoted_apps": list(EXPECTED_BENCHMARK_APPS),
            "expected_promoted_app_count": len(EXPECTED_BENCHMARK_APPS),
            "actual_promoted_apps": sorted(app_geomean),
            "actual_promoted_app_count": len(app_geomean),
            "missing_promoted_apps": missing_apps,
            "min_overall_geomean_v3_speedup_vs_v2": RELEASE_CONSIDERATION_MIN_GEOMEAN,
            "actual_overall_geomean_v3_speedup_vs_v2": geomean,
            "min_app_geomean_wins_gt_1_05x": RELEASE_CONSIDERATION_MIN_APP_WINS,
            "actual_app_geomean_wins_gt_1_05x": app_win_count,
            "app_regression_floor": APP_REGRESSION_FLOOR,
            "actual_app_geomean_regressions_lt_0_95x": app_regression_count,
            "primary_metric_source_mismatch_count": len(source_mismatch_rows),
        },
        "suite_status": {
            f"{tree}_{suite}": _suite_summary(run_dir, tree, suite)
            for tree in EXPECTED_TREES
            for suite in SUITES
        },
        "status_tsv_rows": status_rows,
        "same_metric_comparison_count": len(same_rows),
        "same_metric_rows": same_rows,
        "primary_metric_source_mismatch_count": len(source_mismatch_rows),
        "primary_metric_source_mismatch_rows": source_mismatch_rows,
        "v3_faster_count_gt_5pct": sum(1 for value in speedups if value > 1.05),
        "similar_count_within_5pct": sum(1 for value in speedups if 0.95 <= value <= 1.05),
        "v3_slower_count_gt_5pct": sum(1 for value in speedups if value < 0.95),
        "v3_geomean_speedup_vs_v2": geomean,
        "app_geomean_speedup_vs_v2": app_geomean,
        "top_v3_faster_rows": top_faster[:20],
        "top_v3_slower_rows": top_slower[:20],
        "optix_vs_embree_ratio_change_rows": _build_ratio_change_rows(run_dir),
        "decision_audit": {
            "decision": "Use serious same-RT-hardware V2.14 vs Phoenix V3 paired evidence as a release blocker or release enabler.",
            "was_i_foolish": "No for this decision; it directly tests the user's major-performance requirement.",
            "foolish_actions": "It would be foolish to hide failed rows, count wrapper elapsed as hot-path speed, or treat runability repair as broad performance superiority.",
            "other_path": "Only rerun row-scoped V3 OptiX-vs-Embree candidates. That would not answer whether V3 is better than V2.x.",
            "different_path_now": "Keep V3 redo_required unless this serious paired packet proves broad material V3 superiority.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize Phoenix V3 serious V2.x paired benchmark artifacts.")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    payload = build_payload(args.run_dir)
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    print(json_text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json_text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(_render_markdown(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
