#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1201 OptiX slower-app investigation intake"
DEFAULT_INPUT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal1200_live_pod_2026-04-30"
    / "extracted"
    / "docs"
    / "reports"
    / "goal1200_optix_slower_app_investigation"
)
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal1201_optix_slower_investigation_intake_2026-05-01.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal1201_optix_slower_investigation_intake_2026-05-01.md"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float(data: dict[str, Any], path: tuple[str, ...]) -> float | None:
    value = _nested(data, path)
    return float(value) if isinstance(value, (int, float)) else None


def _load_optional(input_dir: Path, name: str) -> dict[str, Any] | None:
    path = input_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return None
    return _load(path)


def _status(input_dir: Path, label: str) -> dict[str, Any] | None:
    return _load_optional(input_dir, f"{label}.status.json")


def _ratio(embree_sec: float | None, optix_sec: float | None) -> float | None:
    if embree_sec is None or optix_sec is None or optix_sec <= 0:
        return None
    return embree_sec / optix_sec


def _db_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e_status = _status(input_dir, f"db_embree_{copies}")
    o_status = _status(input_dir, f"db_optix_{copies}")
    e = _load_optional(input_dir, f"db_embree_{copies}.json")
    o = _load_optional(input_dir, f"db_optix_{copies}.json")
    e_sec = _float((e.get("results") or [{}])[0] if e else {}, ("prepared_session_warm_query_sec", "median_sec"))
    o_sec = _float((o.get("results") or [{}])[0] if o else {}, ("prepared_session_warm_query_sec", "median_sec"))
    return {
        "copies": copies,
        "embree_status": None if e_status is None else e_status["status"],
        "optix_status": None if o_status is None else o_status["status"],
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
    }


def _graph_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"graph_embree_visibility_{copies}.json")
    o = _load_optional(input_dir, f"graph_optix_visibility_{copies}.json")
    e_sec = _float(e or {}, ("graph_phase_totals_sec", "query_visibility_pair_rows_sec"))
    o_sec = _float(o or {}, ("records_by_label", "optix_visibility_anyhit", "sec"))
    if o_sec is None and o:
        records = o.get("records")
        if isinstance(records, list) and records:
            o_sec = float(records[0]["sec"]) if isinstance(records[0].get("sec"), (int, float)) else None
    optix_kernel_sec = None
    records = o.get("records") if o else None
    if isinstance(records, list):
        for record in records:
            if record.get("label") == "optix_visibility_anyhit":
                optix_kernel_sec = _float(record, ("section_run_phases", "query_anyhit_count_sec"))
    return {
        "copies": copies,
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "optix_anyhit_kernel_sec": optix_kernel_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "ratio_embree_over_optix_kernel": _ratio(e_sec, optix_kernel_sec),
        "optix_status": None if o is None else o.get("status"),
    }


def _polygon_pair_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"polygon_pair_embree_{copies}.json")
    o = _load_optional(input_dir, f"polygon_pair_optix_{copies}.json")
    e_sec = _float(e or {}, ("run_phases", "rt_candidate_discovery_sec"))
    o_sec = _float(o or {}, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": copies,
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "optix_status": None if o is None else o.get("status"),
        "parity_vs_cpu": None if o is None else o.get("parity_vs_cpu"),
    }


def _jaccard_row(input_dir: Path, chunk: int) -> dict[str, Any]:
    e = _load_optional(input_dir, "polygon_jaccard_embree_8192.json")
    o = _load_optional(input_dir, f"polygon_jaccard_optix_8192_chunk_{chunk}.json")
    status = _status(input_dir, f"polygon_jaccard_optix_8192_chunk_{chunk}")
    e_sec = _float(e or {}, ("run_phases", "rt_candidate_discovery_sec"))
    o_sec = _float(o or {}, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": 8192,
        "chunk_copies": chunk,
        "status": None if status is None else status["status"],
        "exit_code": None if status is None else status["exit_code"],
        "chunk_policy": None if o is None else o.get("chunk_policy"),
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "parity_vs_cpu": None if o is None else o.get("parity_vs_cpu"),
    }


def _road_hazard(input_dir: Path) -> dict[str, Any]:
    e = _load_optional(input_dir, "road_hazard_embree_control_20000.json")
    o = _load_optional(input_dir, "road_hazard_optix_control_20000.json")
    e_sec = _float(e or {}, ("run_phases", "query_and_materialize_sec"))
    o_sec = _float(o or {}, ("timings_sec", "optix_query_sec", "median_sec"))
    return {
        "copies": 20000,
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "timing_floor_met": bool(o_sec is not None and o_sec >= 0.1),
        "public_positive_ratio_safe": bool(e_sec is not None and o_sec is not None and e_sec > o_sec and o_sec >= 0.1),
        "optix_status": None if o is None else o.get("status"),
    }


def _hausdorff(input_dir: Path) -> dict[str, Any]:
    embree_rows = []
    for copies in (2000, 10000, 20000):
        d = _load_optional(input_dir, f"hausdorff_embree_repair_{copies}.json")
        sec = _float(d or {}, ("run_phases", "native_directed_summary_sec"))
        points = d.get("point_count_a") if d else None
        embree_rows.append(
            {
                "copies": copies,
                "point_count_a": points,
                "sec": sec,
                "points_per_sec": None if sec in (None, 0) or not isinstance(points, int) else points / sec,
                "matches_oracle": None if d is None else d.get("matches_oracle"),
            }
        )
    optix_rows = []
    for copies in (200000, 1200000):
        d = _load_optional(input_dir, f"hausdorff_optix_repair_{copies}.json")
        scenario = d.get("scenario") if d else {}
        result = scenario.get("result") if isinstance(scenario, dict) else {}
        points = result.get("point_count_a") if isinstance(result, dict) else None
        sec = _float(d or {}, ("scenario", "timings_sec", "optix_query_sec", "median_sec"))
        optix_rows.append(
            {
                "copies": copies,
                "point_count_a": points,
                "sec": sec,
                "points_per_sec": None if sec in (None, 0) or not isinstance(points, int) else points / sec,
                "matches_oracle": None if not isinstance(result, dict) else result.get("matches_oracle"),
            }
        )
    best_embree = max((r for r in embree_rows if r["points_per_sec"] is not None), key=lambda r: r["points_per_sec"], default=None)
    best_optix = max((r for r in optix_rows if r["points_per_sec"] is not None), key=lambda r: r["points_per_sec"], default=None)
    normalized = None
    if best_embree and best_optix:
        normalized = best_optix["points_per_sec"] / best_embree["points_per_sec"]
    return {
        "embree_rows": embree_rows,
        "optix_rows": optix_rows,
        "best_embree_points_per_sec": None if best_embree is None else best_embree["points_per_sec"],
        "best_optix_points_per_sec": None if best_optix is None else best_optix["points_per_sec"],
        "normalized_optix_over_embree_throughput": normalized,
        "same_scale_pair_available": False,
    }


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    summary = _load_optional(input_dir, "goal1200_status_summary.json") or {}
    db = [_db_row(input_dir, copies) for copies in (30000, 100000, 300000)]
    graph = [_graph_row(input_dir, copies) for copies in (30000, 60000, 120000)]
    polygon_pair = [_polygon_pair_row(input_dir, copies) for copies in (10000, 20000, 40000)]
    jaccard = [_jaccard_row(input_dir, chunk) for chunk in (1, 8, 64, 512)]
    road = _road_hazard(input_dir)
    haus = _hausdorff(input_dir)
    decisions = {
        "database_analytics": "blocked_scale_ceiling_and_no_positive_speedup",
        "graph_analytics": "rt_subpaths_completed_but_total_pack_prepare_dominated",
        "polygon_pair_overlap_area_rows": "stable_rt_path_evidence_largest_scale_near_parity_no_public_positive_claim",
        "polygon_set_jaccard": "blocked_existing_artifact_has_chunk64_failure_future_runs_must_use_public_safe_chunk_policy",
        "road_hazard_screening": "positive_control_reproduced_but_public_floor_not_met_in_this_run",
        "hausdorff_distance": "normalized_repair_evidence_collected_same_scale_still_missing",
    }
    public_positive_candidates = [
        app
        for app, status in {"road_hazard_screening": road.get("public_positive_ratio_safe")}.items()
        if status
    ]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": True,
        "input_dir": str(input_dir.relative_to(ROOT)),
        "archive": "docs/reports/goal1200_live_pod_2026-04-30/goal1200_optix_slower_app_investigation.tgz",
        "archive_sha256": "4e7409a0ad3015662026956696bca22ba832a5a3c7719e73e3c9a5a23e5d5079",
        "status_summary": {
            "status_count": summary.get("status_count"),
            "failed_count": summary.get("failed_count"),
            "failed_labels": summary.get("failed_labels", []),
        },
        "database_analytics": db,
        "graph_analytics": graph,
        "polygon_pair_overlap_area_rows": polygon_pair,
        "polygon_set_jaccard": jaccard,
        "road_hazard_screening": road,
        "hausdorff_distance": haus,
        "decisions": decisions,
        "timing_floor_sec": 0.1,
        "public_positive_candidates_from_this_batch": public_positive_candidates,
        "followups": [
            "database_analytics needs chunked/streamed RT lowering before larger-scale DB claims",
            "polygon_set_jaccard needs chunk-stable OptiX correctness before promotion",
            "road_hazard_screening needs a larger floor-safe positive-control rerun",
            "hausdorff_distance needs same-scale or formally reviewed normalized evidence",
            "graph_analytics should keep kernel/pack/prepare/bookkeeping wording separated",
            "polygon_pair_overlap_area_rows needs additional tuning before public positive wording",
        ],
        "boundary": (
            "Goal1201 intakes Goal1200 cloud artifacts only. It does not authorize public docs, "
            "release, or public RTX speedup claims."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1201 OptiX Slower-App Investigation Intake",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- status count: `{payload['status_summary']['status_count']}`",
        f"- failed count: `{payload['status_summary']['failed_count']}`",
        f"- failed labels: `{', '.join(payload['status_summary']['failed_labels'])}`",
        f"- archive sha256: `{payload['archive_sha256']}`",
        f"- public positive candidates from this batch: `{', '.join(payload['public_positive_candidates_from_this_batch']) or 'none'}`",
        "",
        "## Decisions",
        "",
    ]
    for app, decision in payload["decisions"].items():
        lines.append(f"- `{app}`: `{decision}`")
    lines.extend(["", "## Database", "", "| Copies | Embree status | OptiX status | Embree sec | OptiX sec | Ratio |", "| ---: | --- | --- | ---: | ---: | ---: |"])
    for row in payload["database_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{row['embree_status']}` | `{row['optix_status']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | `{_fmt(row['ratio_embree_over_optix'])}` |"
        )
    lines.extend(
        [
            "",
            "## Graph Visibility",
            "",
            "| Copies | Embree sec | OptiX total sec | OptiX any-hit kernel sec | Total ratio | Kernel ratio | OptiX status |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["graph_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | "
            f"`{_fmt(row['optix_anyhit_kernel_sec'])}` | `{_fmt(row['ratio_embree_over_optix'])}` | "
            f"`{_fmt(row['ratio_embree_over_optix_kernel'])}` | `{row['optix_status']}` |"
        )
    lines.extend(["", "## Polygon Pair", "", "| Copies | Embree sec | OptiX sec | Ratio | Parity |", "| ---: | ---: | ---: | ---: | --- |"])
    for row in payload["polygon_pair_overlap_area_rows"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | `{_fmt(row['ratio_embree_over_optix'])}` | `{row['parity_vs_cpu']}` |"
        )
    lines.extend(
        [
            "",
            "## Polygon Jaccard",
            "",
            "| Chunk | Status | Exit | Chunk policy | Embree sec | OptiX sec | Ratio | Parity |",
            "| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["polygon_set_jaccard"]:
        policy = row["chunk_policy"]["policy"] if isinstance(row.get("chunk_policy"), dict) else "legacy_unclassified"
        lines.append(
            f"| `{row['chunk_copies']}` | `{row['status']}` | `{row['exit_code']}` | `{policy}` | "
            f"`{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | "
            f"`{_fmt(row['ratio_embree_over_optix'])}` | `{row['parity_vs_cpu']}` |"
        )
    road = payload["road_hazard_screening"]
    lines.extend(
        [
            "",
            "## Road Hazard Control",
            "",
            f"- Embree sec: `{_fmt(road['embree_sec'])}`",
            f"- OptiX sec: `{_fmt(road['optix_sec'])}`",
            f"- Ratio Embree/OptiX: `{_fmt(road['ratio_embree_over_optix'])}`",
            f"- OptiX timing floor met: `{road['timing_floor_met']}`",
            f"- Public positive ratio safe: `{road['public_positive_ratio_safe']}`",
            "",
            "## Hausdorff Normalized Repair",
            "",
            f"- Same-scale pair available: `{payload['hausdorff_distance']['same_scale_pair_available']}`",
            f"- Best Embree points/sec: `{_fmt(payload['hausdorff_distance']['best_embree_points_per_sec'])}`",
            f"- Best OptiX points/sec: `{_fmt(payload['hausdorff_distance']['best_optix_points_per_sec'])}`",
            f"- Normalized OptiX/Embree throughput: `{_fmt(payload['hausdorff_distance']['normalized_optix_over_embree_throughput'])}`",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
            "## Follow-Ups",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["followups"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "This pod run is useful engineering evidence, but it adds no new public positive RTX speedup "
            "candidate under the current timing-floor and same-scale rules. The next work is local code "
            "improvement plus one batched pod rerun after DB chunking, Jaccard stability, road-hazard scale, "
            "and Hausdorff comparison repairs are ready.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1200 OptiX slower-app investigation artifacts.")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    args = parser.parse_args()
    payload = build_intake(Path(args.input_dir))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "failed_count": payload["status_summary"]["failed_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
