#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-04"
GOAL = "Goal1258 v1.1 Embree/OptiX pod result intake"
DEFAULT_INPUT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal1257_live_pod_2026-05-04"
    / "docs"
    / "reports"
    / "goal1257_v1_1_embree_optix_pod_results"
)
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1258_v1_1_embree_optix_pod_intake_2026-05-04.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1258_v1_1_embree_optix_pod_intake_2026-05-04.md"


def _load_optional(input_dir: Path, name: str) -> dict[str, Any] | None:
    path = input_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any] | None, path: tuple[str, ...]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float(data: dict[str, Any] | None, path: tuple[str, ...]) -> float | None:
    value = _nested(data, path)
    return float(value) if isinstance(value, (int, float)) else None


def _status(input_dir: Path, label: str) -> dict[str, Any] | None:
    return _load_optional(input_dir, f"{label}.status.json")


def _ratio(embree_sec: float | None, optix_sec: float | None) -> float | None:
    if embree_sec is None or optix_sec is None or optix_sec <= 0.0:
        return None
    return embree_sec / optix_sec


def _result0(data: dict[str, Any] | None) -> dict[str, Any] | None:
    results = data.get("results") if isinstance(data, dict) else None
    if isinstance(results, list) and results and isinstance(results[0], dict):
        return results[0]
    return None


def _db_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"db_embree_{copies}.json")
    o = _load_optional(input_dir, f"db_optix_{copies}.json")
    e_result = _result0(e)
    o_result = _result0(o)
    e_sec = _float(e_result, ("prepared_session_warm_query_sec", "median_sec"))
    o_sec = _float(o_result, ("prepared_session_warm_query_sec", "median_sec"))
    return {
        "copies": copies,
        "embree_status": _nested(_status(input_dir, f"db_embree_{copies}"), ("status",)),
        "optix_status": _nested(_status(input_dir, f"db_optix_{copies}"), ("status",)),
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "embree_review_status": _nested(e_result, ("db_review_observation", "status")),
        "optix_review_status": _nested(o_result, ("db_review_observation", "status")),
        "embree_row_materializing_ops": _nested(e_result, ("db_review_observation", "row_materializing_operation_count")),
        "optix_row_materializing_ops": _nested(o_result, ("db_review_observation", "row_materializing_operation_count")),
    }


def _graph_optix_anyhit_record(data: dict[str, Any] | None) -> dict[str, Any] | None:
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("label") == "optix_visibility_anyhit":
            return record
    return None


def _graph_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"graph_embree_visibility_{copies}.json")
    o = _load_optional(input_dir, f"graph_optix_visibility_{copies}.json")
    record = _graph_optix_anyhit_record(o)
    e_sec = _float(e, ("graph_phase_totals_sec", "query_visibility_pair_rows_sec"))
    o_total = _float(record, ("sec",))
    o_kernel = _float(record, ("section_run_phases", "query_anyhit_count_sec"))
    return {
        "copies": copies,
        "embree_sec": e_sec,
        "optix_total_sec": o_total,
        "optix_anyhit_kernel_sec": o_kernel,
        "ratio_embree_over_optix_total": _ratio(e_sec, o_total),
        "ratio_embree_over_optix_kernel": _ratio(e_sec, o_kernel),
        "optix_status": None if o is None else o.get("status"),
        "optix_strict_pass": None if o is None else o.get("strict_pass"),
        "optix_record_status": None if record is None else record.get("status"),
    }


def _polygon_pair_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"polygon_pair_embree_{copies}.json")
    o = _load_optional(input_dir, f"polygon_pair_optix_{copies}.json")
    e_sec = _float(e, ("run_phases", "rt_candidate_discovery_sec"))
    o_sec = _float(o, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": copies,
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "optix_status": None if o is None else o.get("status"),
        "parity_vs_cpu": None if o is None else o.get("parity_vs_cpu"),
        "candidate_count_matches_expected": _nested(o, ("candidate_diagnostics", "candidate_count_matches_expected")),
    }


def _jaccard_row(input_dir: Path, copies: int) -> dict[str, Any]:
    e = _load_optional(input_dir, f"polygon_jaccard_embree_{copies}.json")
    o = _load_optional(input_dir, f"polygon_jaccard_optix_{copies}.json")
    e_sec = _float(e, ("run_phases", "rt_candidate_discovery_sec"))
    o_sec = _float(o, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": copies,
        "chunk_copies": _nested(o, ("chunk_copies",)),
        "chunk_policy": _nested(o, ("chunk_policy", "policy")),
        "chunk_public_safe": _nested(o, ("chunk_policy", "public_safe")),
        "embree_sec": e_sec,
        "optix_sec": o_sec,
        "ratio_embree_over_optix": _ratio(e_sec, o_sec),
        "optix_status": None if o is None else o.get("status"),
        "parity_vs_cpu": None if o is None else o.get("parity_vs_cpu"),
        "candidate_count_matches_expected": _nested(o, ("candidate_diagnostics", "candidate_count_matches_expected")),
    }


def _best_ratio(rows: list[dict[str, Any]], key: str) -> float | None:
    ratios = [row.get(key) for row in rows if isinstance(row.get(key), (int, float))]
    return max(ratios) if ratios else None


def _classify_speed(rows: list[dict[str, Any]], ratio_key: str = "ratio_embree_over_optix") -> str:
    best = _best_ratio(rows, ratio_key)
    if best is None:
        return "baseline_contract_incomplete"
    if best > 1.0:
        return "optix_improved"
    return "optix_still_slower_with_reason"


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    status_summary = _load_optional(input_dir, "goal1257_status_summary.json") or {}
    db = [_db_row(input_dir, copies) for copies in (30000, 100000)]
    graph = [_graph_row(input_dir, copies) for copies in (30000, 60000)]
    polygon_pair = [_polygon_pair_row(input_dir, copies) for copies in (10000, 40000)]
    jaccard = [_jaccard_row(input_dir, copies) for copies in (4096, 8192)]
    decisions = {
        "database_analytics": _classify_speed(db),
        "graph_analytics": _classify_speed(graph, "ratio_embree_over_optix_total"),
        "polygon_pair_overlap_area_rows": _classify_speed(polygon_pair),
        "polygon_set_jaccard": _classify_speed(jaccard),
    }
    missing_artifacts = []
    expected = [
        "goal1257_status_summary.json",
        *(f"db_{backend}_{copies}.json" for backend in ("embree", "optix") for copies in (30000, 100000)),
        *(f"graph_{backend}_visibility_{copies}.json" for backend in ("embree", "optix") for copies in (30000, 60000)),
        *(f"polygon_pair_{backend}_{copies}.json" for backend in ("embree", "optix") for copies in (10000, 40000)),
        *(f"polygon_jaccard_{backend}_{copies}.json" for backend in ("embree", "optix") for copies in (4096, 8192)),
    ]
    for name in expected:
        if not (input_dir / name).exists():
            missing_artifacts.append(name)
    valid = not missing_artifacts and not status_summary.get("failed_count")
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "input_dir": str(input_dir),
        "status_summary": {
            "status_count": status_summary.get("status_count"),
            "failed_count": status_summary.get("failed_count"),
            "failed_labels": status_summary.get("failed_labels", []),
        },
        "missing_artifacts": missing_artifacts,
        "database_analytics": db,
        "graph_analytics": graph,
        "polygon_pair_overlap_area_rows": polygon_pair,
        "polygon_set_jaccard": jaccard,
        "decisions": decisions,
        "public_wording_authorized": False,
        "consensus_requirement": (
            "Goal1258 is result intake only. Any public wording, release gate, "
            "architecture commitment, or major performance conclusion is a key goal "
            "and requires 3-AI consensus unless the user explicitly classifies it lower."
        ),
        "boundary": (
            "Goal1258 interprets copied Goal1257 pod artifacts only. It does not run cloud, "
            "does not change public docs, and does not authorize public RTX speedup wording."
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
        "# Goal1258 v1.1 Embree/OptiX Pod Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"Public wording authorized: `{payload['public_wording_authorized']}`",
        "",
        payload["boundary"],
        "",
        "## Status",
        "",
        f"- status count: `{payload['status_summary']['status_count']}`",
        f"- failed count: `{payload['status_summary']['failed_count']}`",
        f"- missing artifacts: `{len(payload['missing_artifacts'])}`",
        "",
        "## Decisions",
        "",
    ]
    for app, decision in payload["decisions"].items():
        lines.append(f"- `{app}`: `{decision}`")
    lines.extend(["", "## Database", "", "| Copies | Embree sec | OptiX sec | Ratio | Embree review | OptiX review |", "| ---: | ---: | ---: | ---: | --- | --- |"])
    for row in payload["database_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | "
            f"`{_fmt(row['ratio_embree_over_optix'])}` | `{row['embree_review_status']}` | `{row['optix_review_status']}` |"
        )
    lines.extend(["", "## Graph", "", "| Copies | Embree sec | OptiX total sec | OptiX kernel sec | Total ratio | Kernel ratio |", "| ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in payload["graph_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_total_sec'])}` | "
            f"`{_fmt(row['optix_anyhit_kernel_sec'])}` | `{_fmt(row['ratio_embree_over_optix_total'])}` | "
            f"`{_fmt(row['ratio_embree_over_optix_kernel'])}` |"
        )
    lines.extend(["", "## Polygon Pair", "", "| Copies | Embree sec | OptiX sec | Ratio | Parity | Candidate count |", "| ---: | ---: | ---: | ---: | --- | --- |"])
    for row in payload["polygon_pair_overlap_area_rows"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | "
            f"`{_fmt(row['ratio_embree_over_optix'])}` | `{row['parity_vs_cpu']}` | `{row['candidate_count_matches_expected']}` |"
        )
    lines.extend(["", "## Polygon Jaccard", "", "| Copies | Chunk | Safe | Embree sec | OptiX sec | Ratio | Parity |", "| ---: | ---: | --- | ---: | ---: | ---: | --- |"])
    for row in payload["polygon_set_jaccard"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['chunk_copies'])}` | `{row['chunk_public_safe']}` | "
            f"`{_fmt(row['embree_sec'])}` | `{_fmt(row['optix_sec'])}` | `{_fmt(row['ratio_embree_over_optix'])}` | "
            f"`{row['parity_vs_cpu']}` |"
        )
    lines.extend(["", "## Consensus Requirement", "", payload["consensus_requirement"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1257 v1.1 Embree/OptiX pod artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "missing_artifacts": len(payload["missing_artifacts"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
