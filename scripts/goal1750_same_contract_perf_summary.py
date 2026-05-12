#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOAL1723_JSON = ROOT / "docs" / "reports" / "goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json"
GOAL1748_JSON = ROOT / "docs" / "reports" / "goal1748_v1_0_embree_schema_mapping_2026-05-12.json"
REPORT_JSON = ROOT / "docs" / "reports" / "goal1750_same_contract_perf_summary_2026-05-12.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1750_same_contract_perf_summary_2026-05-12.md"


PRIMARY_PHASE_PATHS: dict[tuple[str, str], tuple[str, str, str]] = {
    ("database_analytics", "embree"): (
        "prepared_session_warm_query_median",
        "results[0].prepared_session_warm_query_sec.median_sec",
        "results[0].prepared_session_warm_query_sec.median_sec",
    ),
    ("database_analytics", "optix"): (
        "prepared_session_warm_query_median",
        "results[0].prepared_session_warm_query_sec.median_sec",
        "results[0].prepared_session_warm_query_sec.median_sec",
    ),
    ("service_coverage_gaps", "optix"): (
        "optix_query",
        "scenario.timings_sec.optix_query",
        "scenario.timings_sec.optix_query",
    ),
    ("event_hotspot_screening", "optix"): (
        "optix_query",
        "scenario.timings_sec.optix_query",
        "scenario.timings_sec.optix_query",
    ),
    ("facility_knn_assignment", "optix"): (
        "query_median",
        "scenario.timings_sec.optix_query_sec.median_sec",
        "scenario.timings_sec.optix_query_sec.median_sec",
    ),
    ("road_hazard_screening", "optix"): (
        "query_median",
        "timings_sec.optix_query_sec.median_sec",
        "timings_sec.optix_query_sec.median_sec",
    ),
    ("segment_polygon_hitcount", "optix"): (
        "query_median",
        "timings_sec.optix_query_sec.median_sec",
        "timings_sec.optix_query_sec.median_sec",
    ),
    ("segment_polygon_anyhit_rows", "optix"): (
        "query_median",
        "timings_sec.optix_query_sec.median_sec",
        "timings_sec.optix_query_sec.median_sec",
    ),
    ("polygon_pair_overlap_area_rows", "optix"): (
        "candidate_discovery",
        "phases.optix_candidate_discovery_sec",
        "phases.optix_candidate_discovery_sec",
    ),
    ("polygon_set_jaccard", "optix"): (
        "candidate_discovery",
        "phases.optix_candidate_discovery_sec",
        "phases.optix_candidate_discovery_sec",
    ),
    ("hausdorff_distance", "optix"): (
        "query_median",
        "scenario.timings_sec.optix_query_sec.median_sec",
        "scenario.timings_sec.optix_query_sec.median_sec",
    ),
    ("ann_candidate_search", "optix"): (
        "query_median",
        "scenario.timings_sec.optix_query_sec.median_sec",
        "scenario.timings_sec.optix_query_sec.median_sec",
    ),
    ("outlier_detection", "optix"): (
        "warm_query_median",
        "results[0].prepared_optix_warm_query_sec.median_sec",
        "results[0].prepared_optix_warm_query_sec.median_sec",
    ),
    ("robot_collision_screening", "optix"): (
        "prepared_pose_flags_warm_query_median",
        "phases.prepared_pose_flags_warm_query_sec.median_sec",
        "phases.prepared_pose_flags_warm_query_sec.median_sec",
    ),
    ("barnes_hut_force_app", "optix"): (
        "query_median",
        "scenario.timings_sec.optix_query_sec.median_sec",
        "scenario.timings_sec.optix_query_sec.median_sec",
    ),
}


DERIVED_OPTIX_GRAPH_ROWS: tuple[tuple[str, int], ...] = (
    ("graph_visibility_edges", 0),
    ("graph_bfs", 1),
    ("graph_triangle_count", 2),
)


def _load(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


def _parse_part(part: str) -> tuple[str, int | None]:
    if "[" not in part:
        return part, None
    name, rest = part.split("[", 1)
    return name, int(rest.rstrip("]"))


def _get_path(payload: dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        key, index = _parse_part(part)
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
        if index is not None:
            if not isinstance(current, list) or index >= len(current):
                return None
            current = current[index]
    return current


def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _ratio_row(row: dict[str, Any]) -> dict[str, Any]:
    app = row["app"]
    engine = row["engine"]
    result: dict[str, Any] = {
        "app": app,
        "engine": engine,
        "baseline_artifact": row["baseline_artifact"],
        "current_artifact": row["current_artifact"],
        "parity_evidence_clean": row.get("parity_evidence_clean"),
        "boundary_resolved_by_companion": row.get("boundary_resolved_by_companion"),
        "public_claim_authorized": False,
    }
    mapping = PRIMARY_PHASE_PATHS.get((app, engine))
    if mapping is None:
        result["classification"] = "evidence_pair_no_single_primary_ratio"
        result["reason"] = "Artifact pair is present, but this summary has no single same-contract primary phase mapping for the row."
        return result
    label, baseline_path, current_path = mapping
    baseline = _load(row["baseline_artifact"])
    current = _load(row["current_artifact"])
    baseline_sec = _num(_get_path(baseline, baseline_path))
    current_sec = _num(_get_path(current, current_path))
    result.update(
        {
            "classification": "same_contract_primary_ratio"
            if baseline_sec is not None and current_sec is not None and current_sec > 0
            else "mapped_primary_ratio_missing_numeric_value",
            "phase_label": label,
            "baseline_path": baseline_path,
            "current_path": current_path,
            "baseline_sec": baseline_sec,
            "current_sec": current_sec,
            "baseline_over_current_ratio": (
                baseline_sec / current_sec
                if baseline_sec is not None and current_sec is not None and current_sec > 0
                else None
            ),
        }
    )
    return result


def _derived_optix_graph_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    graph_row = next(
        (row for row in rows if row["engine"] == "optix" and row["app"] == "graph_analytics"),
        None,
    )
    if graph_row is None:
        return []
    baseline = _load(graph_row["baseline_artifact"])
    current = _load(graph_row["current_artifact"])
    derived: list[dict[str, Any]] = []
    for app, index in DERIVED_OPTIX_GRAPH_ROWS:
        baseline_path = f"records[{index}].sec"
        current_path = f"records[{index}].sec"
        baseline_sec = _num(_get_path(baseline, baseline_path))
        current_sec = _num(_get_path(current, current_path))
        derived.append(
            {
                "app": app,
                "engine": "optix",
                "baseline_artifact": graph_row["baseline_artifact"],
                "current_artifact": graph_row["current_artifact"],
                "parity_evidence_clean": graph_row.get("parity_evidence_clean"),
                "boundary_resolved_by_companion": graph_row.get("boundary_resolved_by_companion"),
                "public_claim_authorized": False,
                "classification": "same_contract_primary_ratio"
                if baseline_sec is not None and current_sec is not None and current_sec > 0
                else "mapped_primary_ratio_missing_numeric_value",
                "phase_label": "graph_section_wall",
                "baseline_path": baseline_path,
                "current_path": current_path,
                "baseline_sec": baseline_sec,
                "current_sec": current_sec,
                "baseline_over_current_ratio": (
                    baseline_sec / current_sec
                    if baseline_sec is not None and current_sec is not None and current_sec > 0
                    else None
                ),
                "derived_from": "graph_analytics",
                "derivation_boundary": "Split from the ordered graph_analytics OptiX records: visibility_edges, bfs, triangle_count.",
            }
        )
    return derived


def build_report() -> dict[str, Any]:
    comparable = _load(GOAL1723_JSON)
    embree_mapping = _load(GOAL1748_JSON)
    optix_source_rows = [
        row
        for row in comparable["rows"]
        if row["engine"] == "optix" and row["app"] != "graph_analytics"
    ]
    optix_rows = [_ratio_row(row) for row in optix_source_rows]
    optix_rows.extend(_derived_optix_graph_rows(comparable["rows"]))
    embree_same_contract_rows = [
        _ratio_row(row)
        for row in comparable["rows"]
        if row["engine"] == "embree" and row["app"] == "database_analytics"
    ]
    embree_recovered_rows = embree_mapping["rows"]
    optix_class_counts: dict[str, int] = {}
    for row in optix_rows:
        optix_class_counts[row["classification"]] = optix_class_counts.get(row["classification"], 0) + 1
    payload = {
        "goal": "Goal1750",
        "date": "2026-05-12",
        "verdict": "same_contract_perf_summary_ready_without_public_claim",
        "optix": {
            "artifact_pair_rows": len(optix_rows),
            "class_counts": optix_class_counts,
            "rows": optix_rows,
        },
        "embree": {
            "same_contract_artifact_pair_rows": len(embree_same_contract_rows),
            "same_contract_rows": embree_same_contract_rows,
            "recovered_goal1746_rows": len(embree_recovered_rows),
            "goal1748_class_counts": embree_mapping["class_counts"],
            "goal1748_rows": embree_recovered_rows,
        },
        "public_claim_authorized": False,
        "release_authorized": False,
        "boundary": (
            "This summary compares available v1.0 customized-engine artifacts against current generic-engine artifacts. "
            "OptiX has broad same-contract primary ratios; Embree has one historical same-contract database row plus recovered "
            "Goal1746 app-level rows that remain diagnostic or schema-mismatched. No public speedup or release claim is authorized."
        ),
    }
    return payload


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if value is None:
        return "n/a"
    return str(value)


def write_report(payload: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal1750 Same-Contract Performance Summary",
        "",
        "## Verdict",
        "",
        f"`{payload['verdict']}`",
        "",
        payload["boundary"],
        "",
        "## OptiX",
        "",
        f"- Artifact-pair rows: `{payload['optix']['artifact_pair_rows']}`",
    ]
    for name, count in sorted(payload["optix"]["class_counts"].items()):
        lines.append(f"- `{name}`: `{count}`")
    lines.extend(["", "| App | Classification | Phase | v1.0 sec | Current sec | v1.0/current |", "| --- | --- | --- | ---: | ---: | ---: |"])
    for row in payload["optix"]["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['classification']}` | `{row.get('phase_label', '')}` | "
            f"{_fmt(row.get('baseline_sec'))} | {_fmt(row.get('current_sec'))} | {_fmt(row.get('baseline_over_current_ratio'))} |"
        )
    lines.extend(
        [
            "",
            "## Embree",
            "",
            f"- Same-contract artifact-pair rows: `{payload['embree']['same_contract_artifact_pair_rows']}`",
            f"- Goal1746 recovered app-level rows: `{payload['embree']['recovered_goal1746_rows']}`",
        ]
    )
    for name, count in sorted(payload["embree"]["goal1748_class_counts"].items()):
        lines.append(f"- Goal1748 `{name}`: `{count}`")
    lines.extend(["", "| App | Classification | Phase | v1.0 sec | Current sec | v1.0/current |", "| --- | --- | --- | ---: | ---: | ---: |"])
    for row in payload["embree"]["same_contract_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['classification']}` | `{row.get('phase_label', '')}` | "
            f"{_fmt(row.get('baseline_sec'))} | {_fmt(row.get('current_sec'))} | {_fmt(row.get('baseline_over_current_ratio'))} |"
        )
    lines.extend(
        [
            "",
            "Goal1748 recovered Embree rows remain bounded as follows:",
            "",
            "| Classification | Count | Meaning |",
            "| --- | ---: | --- |",
            f"| `phase_mapped_diagnostic` | {payload['embree']['goal1748_class_counts'].get('phase_mapped_diagnostic', 0)} | Numeric mappings exist, but they are diagnostic and not public same-contract claims. |",
            f"| `timing_schema_mismatch` | {payload['embree']['goal1748_class_counts'].get('timing_schema_mismatch', 0)} | Artifacts exist, but timing schemas do not yet support a same-contract ratio. |",
            f"| `missing_current_artifact` | {payload['embree']['goal1748_class_counts'].get('missing_current_artifact', 0)} | v1.0 split graph artifacts exist, but no same-name current Embree artifact exists. |",
            "",
            "## Boundary",
            "",
            "Use this as internal engineering evidence only. It answers whether the generic-engine rewrite caused obvious same-contract regressions where comparable timing exists; it does not authorize public speedup language, v1.8 release, or a broad statement over rows classified as diagnostic or schema-mismatched.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = build_report()
    write_report(payload)
    print(
        json.dumps(
            {
                "goal": payload["goal"],
                "optix": payload["optix"]["class_counts"],
                "embree_goal1748": payload["embree"]["goal1748_class_counts"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
