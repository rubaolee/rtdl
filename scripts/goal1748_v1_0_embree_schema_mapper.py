#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs" / "reports" / "goal1748_v1_0_embree_schema_mapping_2026-05-12.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1748_v1_0_embree_schema_mapping_2026-05-12.md"


RECOVERED_APPS = [
    "service_coverage_gaps",
    "event_hotspot_screening",
    "facility_knn_assignment",
    "road_hazard_screening",
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "graph_visibility_edges",
    "graph_bfs",
    "graph_triangle_count",
    "hausdorff_distance",
    "ann_candidate_search",
    "barnes_hut_force_app",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
]

PHASE_MAPPINGS: dict[str, list[dict[str, str]]] = {
    "road_hazard_screening": [
        {
            "label": "native_query_or_materialize",
            "baseline_path": "run_phases.query_and_materialize_sec",
            "current_path": "timings_sec.backend_query_sec.median_sec",
            "boundary": "App-level v1.0 materialized row query compared with current generic backend query median.",
        }
    ],
    "hausdorff_distance": [
        {
            "label": "native_directed_or_query",
            "baseline_path": "run_phases.native_directed_summary_sec",
            "current_path": "scenario.timings_sec.backend_query_sec.median_sec",
            "boundary": "Directed summary continuation compared with current backend query median; validation/input phases excluded.",
        }
    ],
    "polygon_pair_overlap_area_rows": [
        {
            "label": "rt_candidate_discovery",
            "baseline_path": "run_phases.rt_candidate_discovery_sec",
            "current_path": "phases.embree_total_sec",
            "boundary": "Closest available current Embree total includes more than candidate discovery, so ratio is diagnostic only.",
        },
        {
            "label": "native_exact_continuation",
            "baseline_path": "run_phases.native_exact_continuation_sec",
            "current_path": "phases.native_exact_continuation_sec",
            "boundary": "Native exact continuation fields are directly named on both sides.",
        },
    ],
    "polygon_set_jaccard": [
        {
            "label": "rt_candidate_discovery",
            "baseline_path": "run_phases.rt_candidate_discovery_sec",
            "current_path": "phases.embree_total_sec",
            "boundary": "Closest available current Embree total includes more than candidate discovery, so ratio is diagnostic only.",
        },
        {
            "label": "native_exact_continuation",
            "baseline_path": "run_phases.native_exact_continuation_sec",
            "current_path": "phases.native_exact_continuation_sec",
            "boundary": "Native exact continuation fields are directly named on both sides.",
        },
    ],
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _get_path(payload: dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _artifact(app: str, version: str) -> Path:
    if version == "v1_0":
        return ROOT / "docs" / "reports" / f"goal1746_v1_0_{app}_embree.json"
    return ROOT / "docs" / "reports" / f"goal1660_v1_6_11_{app}_embree.json"


def _timing_keys(payload: dict[str, Any] | None) -> list[str]:
    if payload is None:
        return []
    keys: list[str] = []

    def walk(obj: Any, prefix: str = "") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                lower = key.lower()
                if any(token in lower for token in ("time", "sec", "phase", "elapsed")):
                    keys.append(path)
                walk(value, path)
        elif isinstance(obj, list):
            for index, value in enumerate(obj[:2]):
                walk(value, f"{prefix}[{index}]")

    walk(payload)
    return keys


def _classify_row(app: str) -> dict[str, Any]:
    baseline_path = _artifact(app, "v1_0")
    current_path = _artifact(app, "v1_6_11")
    baseline = _read_json(baseline_path)
    current = _read_json(current_path)
    row: dict[str, Any] = {
        "app": app,
        "engine": "embree",
        "baseline_artifact": str(baseline_path.relative_to(ROOT)),
        "current_artifact": str(current_path.relative_to(ROOT)),
        "baseline_artifact_present": baseline is not None,
        "current_artifact_present": current is not None,
        "baseline_timing_keys": _timing_keys(baseline),
        "current_timing_keys": _timing_keys(current),
        "phase_mappings": [],
        "direct_speedup_claim_authorized": False,
        "public_claim_authorized": False,
    }
    if baseline is None:
        row["classification"] = "missing_baseline_artifact"
        return row
    if current is None:
        row["classification"] = "missing_current_artifact"
        row["reason"] = "Recovered v1.0 row exists, but there is no same-name current Embree artifact."
        return row
    mappings = PHASE_MAPPINGS.get(app, [])
    for mapping in mappings:
        baseline_value = _as_number(_get_path(baseline, mapping["baseline_path"]))
        current_value = _as_number(_get_path(current, mapping["current_path"]))
        result = dict(mapping)
        result["baseline_sec"] = baseline_value
        result["current_sec"] = current_value
        if baseline_value is not None and current_value is not None and current_value > 0:
            result["baseline_over_current_ratio"] = baseline_value / current_value
        else:
            result["baseline_over_current_ratio"] = None
        row["phase_mappings"].append(result)
    if row["phase_mappings"]:
        usable = [
            mapping
            for mapping in row["phase_mappings"]
            if mapping["baseline_sec"] is not None and mapping["current_sec"] is not None
        ]
        row["classification"] = "phase_mapped_diagnostic" if usable else "mapping_fields_missing"
        row["phase_mapping_required"] = True
        row["diagnostic_ratio_count"] = len(usable)
        return row
    if row["baseline_timing_keys"] or row["current_timing_keys"]:
        row["classification"] = "timing_schema_mismatch"
        row["reason"] = "Timing fields exist, but no same-contract phase mapping is defined yet."
    else:
        row["classification"] = "summary_only"
        row["reason"] = "Recovered artifact has no timing fields; use it for implementation presence and summary evidence only."
    return row


def build_report() -> dict[str, Any]:
    rows = [_classify_row(app) for app in RECOVERED_APPS]
    classes: dict[str, int] = {}
    for row in rows:
        classes[row["classification"]] = classes.get(row["classification"], 0) + 1
    return {
        "goal": "Goal1748",
        "date": "2026-05-12",
        "verdict": "embree_schema_mapping_ready_without_public_speedup_claim",
        "baseline": "v1.0 recovered Embree app artifacts from Goal1746",
        "current": "v1.6.11/current generic Embree artifacts from Goal1660",
        "row_count": len(rows),
        "class_counts": classes,
        "rows": rows,
        "public_claim_authorized": False,
        "release_authorized": False,
        "boundary": (
            "This report classifies recovered v1.0 Embree artifacts against current generic Embree artifacts. "
            "Ratios are diagnostic only unless a row has exact same-contract phase evidence and external review."
        ),
    }


def _fmt_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}x"


def write_report(payload: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal1748 v1.0 Embree Schema Mapping",
        "",
        "## Verdict",
        "",
        f"`{payload['verdict']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- Rows classified: `{payload['row_count']}`",
        f"- Public claim authorized: `{payload['public_claim_authorized']}`",
        f"- Release authorized: `{payload['release_authorized']}`",
    ]
    for name, count in sorted(payload["class_counts"].items()):
        lines.append(f"- `{name}`: `{count}`")
    lines.extend(["", "## Rows", "", "| App | Classification | Diagnostic mappings |", "| --- | --- | --- |"])
    for row in payload["rows"]:
        mappings = []
        for mapping in row["phase_mappings"]:
            mappings.append(
                f"{mapping['label']}={_fmt_ratio(mapping['baseline_over_current_ratio'])}"
            )
        lines.append(
            f"| `{row['app']}` | `{row['classification']}` | {', '.join(mappings) if mappings else row.get('reason', '')} |"
        )
    lines.extend(
        [
            "",
            "## ANN Long-Run Resolution",
            "",
            "`ann_candidate_search` is present in the recovered v1.0 Embree set. The resolved command uses `--output-mode rerank_summary`; the rejected `quality_summary` path would perform roughly 7.2 billion Python exact-distance checks at Goal1660 scale and is not used as the baseline recovery surface.",
            "",
            "## Boundary",
            "",
            "This mapping does not authorize public speedup wording. Rows with diagnostic ratios still need exact same-contract confirmation before any performance claim, and rows classified as `summary_only`, `timing_schema_mismatch`, or `missing_current_artifact` cannot support a timing comparison.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    payload = build_report()
    write_report(payload)
    print(json.dumps({"goal": payload["goal"], "class_counts": payload["class_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
