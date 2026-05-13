#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX_JSON = ROOT / "docs" / "reports" / "goal1930_all_app_v2_matrix_2026-05-13.json"


def _read_json(path: pathlib.Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _median(section: dict, key: str) -> float | None:
    item = section.get(key)
    if not isinstance(item, dict):
        return None
    value = item.get("median_s")
    return float(value) if isinstance(value, (int, float)) else None


def _ratio(v2: float | None, v18: float | None) -> float | None:
    if v2 is None or v18 is None or v18 == 0:
        return None
    return v2 / v18


def _fixed_radius_rows() -> list[dict[str, object]]:
    artifact = _read_json(ROOT / "docs" / "reports" / "goal1903_fixed_radius_batch_pod.json")
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    for result in artifact.get("results", []):
        if not isinstance(result, dict):
            continue
        size = int(result.get("size", 0) or 0)
        partner = str(result.get("partner", "unknown"))
        if size != 16384:
            continue
        for app, label in (
            ("service_coverage_gaps", "service coverage gaps"),
            ("event_hotspot_screening", "event hotspot screening"),
        ):
            section = result.get(app)
            if not isinstance(section, dict):
                continue
            v18 = _median(section, "v1_8_prepared_optix")
            reused = _median(section, "v1_8_reused_prepared_optix")
            v2 = _median(section, "goal1879_v2_prepared_native_optix_partner")
            rows.append(
                {
                    "app": app,
                    "label": label,
                    "size": size,
                    "partner": partner,
                    "v18_prepared_s": v18,
                    "v18_reused_prepared_s": reused,
                    "v2_prepared_partner_s": v2,
                    "ratio_vs_v18_prepared": _ratio(v2, v18),
                    "ratio_vs_v18_reused_prepared": _ratio(v2, reused),
                    "classification": "positive" if _ratio(v2, v18) is not None and _ratio(v2, v18) < 1.0 else "pending",
                    "insight": "Prepared fixed-radius native work plus partner-owned threshold columns amortize very well at the larger row size.",
                    "artifact": "docs/reports/goal1903_fixed_radius_batch_pod.json",
                }
            )
    return rows


def _segment_or_road_row(path: str, app: str, label: str) -> list[dict[str, object]]:
    artifact = _read_json(ROOT / path)
    if not artifact:
        return []
    rows: list[dict[str, object]] = []
    v18 = _median(artifact.get("prepared_baseline", {}), "query_summary")
    if v18 is None:
        prepared = artifact.get("prepared_baseline", {})
        if isinstance(prepared, dict) and isinstance(prepared.get("query_summary"), dict):
            v18 = float(prepared["query_summary"].get("median_s", 0.0) or 0.0)
    for partner, section in artifact.get("partners", {}).items():
        if not isinstance(section, dict):
            continue
        reuse = section.get("goal1886_prepared_reuse") or section.get("goal1889_prepared_reuse")
        if not isinstance(reuse, dict):
            continue
        summary = reuse.get("query_summary")
        v2 = float(summary.get("median_s", 0.0) or 0.0) if isinstance(summary, dict) else None
        ratio = _ratio(v2, v18)
        rows.append(
            {
                "app": app,
                "label": label,
                "size": int(artifact.get("count", 0) or 0),
                "partner": str(partner),
                "v18_prepared_s": v18,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": v2,
                "ratio_vs_v18_prepared": ratio,
                "ratio_vs_v18_reused_prepared": None,
                "classification": "positive" if ratio is not None and ratio < 1.0 else "mixed",
                "insight": "Prepared reuse and partner-owned compact outputs matter; row materialization or tiny cases are much less favorable.",
                "artifact": path,
            }
        )
    return rows


def _best_measured(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    best: dict[str, dict[str, object]] = {}
    for row in rows:
        app = str(row["app"])
        ratio = row.get("ratio_vs_v18_prepared")
        if not isinstance(ratio, (int, float)):
            continue
        current = best.get(app)
        current_ratio = current.get("ratio_vs_v18_prepared") if current else None
        if current is None or not isinstance(current_ratio, (int, float)) or ratio < current_ratio:
            best[app] = row
    return best


def build_analysis() -> dict[str, object]:
    matrix = _read_json(MATRIX_JSON)
    if matrix is None:
        raise FileNotFoundError(MATRIX_JSON)
    measured_rows = []
    measured_rows.extend(_fixed_radius_rows())
    measured_rows.extend(
        _segment_or_road_row(
            "docs/reports/goal1903_segment_polygon_batch_pod_2048.json",
            "segment_polygon_hitcount",
            "segment polygon hitcount",
        )
    )
    measured_rows.extend(
        _segment_or_road_row(
            "docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json",
            "road_hazard_screening",
            "road hazard screening",
        )
    )
    best = _best_measured(measured_rows)
    rows: list[dict[str, object]] = []
    for matrix_row in matrix["rows"]:
        app = str(matrix_row["app"])
        if app in best:
            entry = dict(best[app])
            entry["matrix_state"] = matrix_row["v2_state"]
            entry["claim_class"] = matrix_row["claim_class"]
            rows.append(entry)
            continue
        status = str(matrix_row["comparison_status"])
        rows.append(
            {
                "app": app,
                "label": app.replace("_", " "),
                "size": None,
                "partner": None,
                "v18_prepared_s": None,
                "v18_reused_prepared_s": None,
                "v2_prepared_partner_s": None,
                "ratio_vs_v18_prepared": None,
                "ratio_vs_v18_reused_prepared": None,
                "classification": (
                    "control" if status == "evidence-only-control" else "pending-pod"
                ),
                "matrix_state": matrix_row["v2_state"],
                "claim_class": matrix_row["claim_class"],
                "insight": matrix_row["analysis_hint"],
                "artifact": matrix_row["v2_evidence"],
            }
        )
    counts: dict[str, int] = {}
    for row in rows:
        classification = str(row["classification"])
        counts[classification] = counts.get(classification, 0) + 1
    return {
        "goal": "Goal1931",
        "status": "current-evidence-analysis-final-pod-batch-needed",
        "matrix_source": str(MATRIX_JSON.relative_to(ROOT)),
        "row_count": len(rows),
        "rows": rows,
        "classification_counts": counts,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "all_apps_have_final_pod_timing": False,
            "whole_app_speedup_claim_authorized": False,
            "control_rows_are_speedup_evidence": False,
        },
    }


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "pending"
    return str(value)


def to_markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, list)
    lines = [
        "# Goal1931 - Current All-App v1.8 vs v2.0 Performance Analysis",
        "",
        "Status: current-evidence-analysis-final-pod-batch-needed",
        "",
        "Date: 2026-05-13",
        "",
        "This report is the current all-app performance analysis layer on top of Goal1930. It uses existing accepted pod artifacts where they exist and marks the remaining rows as pending or evidence-only controls. It does not authorize v2.0 release and it does not claim every app has a measured v2 speedup.",
        "",
        "## Current Table",
        "",
        "| App | Class | Partner | Size | v1.8 prepared s | v2 prepared partner s | Ratio | Insight |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['app']}`",
                    f"`{row['classification']}`",
                    _fmt(row["partner"]),
                    _fmt(row["size"]),
                    _fmt(row["v18_prepared_s"]),
                    _fmt(row["v2_prepared_partner_s"]),
                    _fmt(row["ratio_vs_v18_prepared"]),
                    str(row["insight"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## What The Table Says",
            "",
            "- The strongest measured v2 rows are prepared fixed-radius and prepared compact output rows, where native work is reused and the app result stays in partner-owned columns.",
            "- Segment/polygon and road-hazard become convincing at larger rows; small rows remain setup-bound and must be described as mixed.",
            "- The six additional fixed-radius-family apps and robot collision now have local harnesses, but they still need current RTX pod timing before they can move from `pending-pod` to measured.",
            "- Database, graph, and exact polygon metrics are intentionally marked as controls/fallbacks. They are important evidence rows, but they are not v2 partner speedup rows until their app continuations move into reviewed partner tensor contracts.",
            "",
            "## Release Boundary",
            "",
            "This is a performance-analysis scaffold and partial evidence report. Final v2.0 still needs the current pod batch for pending rows, external review of the all-app conclusion, and final release consensus.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build current all-app v1.8-vs-v2 analysis.")
    parser.add_argument("--output-json", default="docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json")
    parser.add_argument("--output-md", default="docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.md")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_analysis()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
