#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
GOAL = "Goal1205 repaired RTX pod intake"
DEFAULT_INPUT_DIR = ROOT / "docs/reports/goal1204_live_pod_2026-05-01/docs/reports/goal1204_repaired_rtx_pod"
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1205_repaired_rtx_pod_intake_2026-05-01.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1205_repaired_rtx_pod_intake_2026-05-01.md"
TIMING_FLOOR_SEC = 0.1


def _load_optional(input_dir: Path, name: str) -> dict[str, Any] | None:
    path = input_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float(data: dict[str, Any] | None, keys: tuple[str, ...]) -> float | None:
    if data is None:
        return None
    value = _nested(data, keys)
    return float(value) if isinstance(value, (int, float)) else None


def _status(input_dir: Path, label: str) -> dict[str, Any] | None:
    return _load_optional(input_dir, f"{label}.status.json")


def _status_value(input_dir: Path, label: str) -> str | None:
    status = _status(input_dir, label)
    return None if status is None else str(status.get("status"))


def _ratio(control_sec: float | None, optix_sec: float | None) -> float | None:
    if control_sec is None or optix_sec is None or optix_sec <= 0:
        return None
    return control_sec / optix_sec


def _db_warm_query(data: dict[str, Any] | None) -> float | None:
    if data is None:
        return None
    results = data.get("results")
    if not isinstance(results, list) or not results:
        return None
    return _float(results[0], ("prepared_session_warm_query_sec", "median_sec"))


def _db_chunked(data: dict[str, Any] | None) -> bool:
    if data is None:
        return False
    for path in (
        ("prepared_dataset",),
        ("session",),
        ("prepared_session_output", "prepared_dataset"),
        ("prepared_session_output", "session"),
        ("prepared_session_output", "sections", "sales_risk", "prepared_dataset"),
        ("prepared_session_output", "sections", "sales_risk", "session"),
    ):
        value = _nested(data, path)
        if isinstance(value, dict) and value.get("chunked_compact_summary") is True:
            return True
        if isinstance(value, dict) and value.get("transfer") == "chunked_columnar":
            return True
    reported_prepare = data.get("reported_prepare_phases_sec")
    if isinstance(reported_prepare, dict) and reported_prepare.get("chunked_compact_summary") is True:
        return True
    results = data.get("results")
    if isinstance(results, list) and results:
        return _db_chunked(results[0])
    return False


def _db_row(input_dir: Path, copies: int) -> dict[str, Any]:
    embree_label = f"db_embree_{copies}_chunked_repair"
    optix_label = f"db_optix_{copies}_chunked_repair"
    embree = _load_optional(input_dir, f"{embree_label}.json")
    optix = _load_optional(input_dir, f"{optix_label}.json")
    embree_sec = _db_warm_query(embree)
    optix_sec = _db_warm_query(optix)
    return {
        "copies": copies,
        "embree_status": _status_value(input_dir, embree_label),
        "optix_status": _status_value(input_dir, optix_label),
        "embree_sec": embree_sec,
        "optix_sec": optix_sec,
        "ratio_embree_over_optix": _ratio(embree_sec, optix_sec),
        "embree_chunked": _db_chunked(embree),
        "optix_chunked": _db_chunked(optix),
        "repair_passed": bool(
            _status_value(input_dir, embree_label) == "ok"
            and _status_value(input_dir, optix_label) == "ok"
            and _db_chunked(embree)
            and _db_chunked(optix)
        ),
    }


def _jaccard_row(input_dir: Path, chunk: int) -> dict[str, Any]:
    label = f"jaccard_optix_8192_{'public_safe_chunk_512' if chunk == 512 else 'diagnostic_chunk_64'}"
    data = _load_optional(input_dir, f"{label}.json")
    policy = data.get("chunk_policy") if data else None
    return {
        "copies": 8192,
        "chunk_copies": chunk,
        "label": label,
        "status": _status_value(input_dir, label),
        "chunk_policy": policy,
        "parity_vs_cpu": None if data is None else data.get("parity_vs_cpu"),
        "public_safe": bool(isinstance(policy, dict) and policy.get("public_safe") is True),
        "diagnostic_only": bool(
            isinstance(policy, dict)
            and (policy.get("policy") == "diagnostic_only" or policy.get("classification") == "diagnostic_only")
        ),
        "optix_candidate_sec": _float(data, ("phases", "optix_candidate_discovery_sec")),
    }


def _road_hazard(input_dir: Path) -> dict[str, Any]:
    embree_label = "road_hazard_embree_control_40000"
    optix_label = "road_hazard_optix_control_40000"
    embree = _load_optional(input_dir, f"{embree_label}.json")
    optix = _load_optional(input_dir, f"{optix_label}.json")
    embree_sec = _float(embree, ("run_phases", "query_and_materialize_sec"))
    optix_sec = _float(optix, ("timings_sec", "optix_query_sec", "median_sec"))
    return {
        "copies": 40000,
        "embree_status": _status_value(input_dir, embree_label),
        "optix_status": _status_value(input_dir, optix_label),
        "embree_sec": embree_sec,
        "optix_sec": optix_sec,
        "ratio_embree_over_optix": _ratio(embree_sec, optix_sec),
        "timing_floor_met": bool(optix_sec is not None and optix_sec >= TIMING_FLOOR_SEC),
        "same_scale_public_positive_candidate": bool(
            embree_sec is not None and optix_sec is not None and embree_sec > optix_sec and optix_sec >= TIMING_FLOOR_SEC
        ),
    }


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    summary = _load_optional(input_dir, "goal1204_status_summary.json") or {}
    database_rows = [_db_row(input_dir, copies) for copies in (100000, 300000)]
    jaccard_rows = [_jaccard_row(input_dir, chunk) for chunk in (512, 64)]
    road = _road_hazard(input_dir)
    failed_labels = summary.get("failed_labels", [])
    if not isinstance(failed_labels, list):
        failed_labels = []
    decisions = {
        "database_analytics": "repair_passed" if all(row["repair_passed"] for row in database_rows) else "blocked_or_incomplete",
        "polygon_set_jaccard": (
            "public_safe_chunk_ready"
            if jaccard_rows[0]["status"] == "ok" and jaccard_rows[0]["public_safe"] and jaccard_rows[1]["diagnostic_only"]
            else "blocked_or_incomplete"
        ),
        "road_hazard_screening": (
            "same_scale_public_positive_candidate"
            if road["same_scale_public_positive_candidate"]
            else "blocked_or_floor_not_met"
        ),
    }
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": bool(input_dir.exists()),
        "input_dir": str(input_dir),
        "status_summary": {
            "status_count": summary.get("status_count"),
            "failed_count": summary.get("failed_count"),
            "failed_labels": failed_labels,
        },
        "database_analytics": database_rows,
        "polygon_set_jaccard": jaccard_rows,
        "road_hazard_screening": road,
        "decisions": decisions,
        "public_positive_candidates_from_this_batch": [
            app for app, decision in decisions.items() if decision in {"same_scale_public_positive_candidate", "public_safe_chunk_ready"}
        ],
        "boundary": (
            "Goal1205 intakes Goal1204 pod artifacts only. It does not authorize public docs, "
            "release, or public RTX speedup wording without a separate review decision."
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
        "# Goal1205 Repaired RTX Pod Intake",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Status",
        "",
        f"- valid: `{payload['valid']}`",
        f"- failed count: `{payload['status_summary']['failed_count']}`",
        f"- failed labels: `{', '.join(payload['status_summary']['failed_labels']) or 'none'}`",
        "",
        "## Database Analytics",
        "",
        "| Copies | Embree status | OptiX status | Embree sec | OptiX sec | Ratio | Repair passed |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["database_analytics"]:
        lines.append(
            "| {copies} | {embree_status} | {optix_status} | {embree_sec} | {optix_sec} | {ratio} | {repair} |".format(
                copies=row["copies"],
                embree_status=_fmt(row["embree_status"]),
                optix_status=_fmt(row["optix_status"]),
                embree_sec=_fmt(row["embree_sec"]),
                optix_sec=_fmt(row["optix_sec"]),
                ratio=_fmt(row["ratio_embree_over_optix"]),
                repair=_fmt(row["repair_passed"]),
            )
        )
    lines.extend(
        [
            "",
            "## Polygon Jaccard",
            "",
            "| Chunk | Status | Public safe | Diagnostic only | Parity | OptiX candidate sec |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["polygon_set_jaccard"]:
        lines.append(
            f"| {row['chunk_copies']} | {_fmt(row['status'])} | {_fmt(row['public_safe'])} | {_fmt(row['diagnostic_only'])} | {_fmt(row['parity_vs_cpu'])} | {_fmt(row['optix_candidate_sec'])} |"
        )
    road = payload["road_hazard_screening"]
    lines.extend(
        [
            "",
            "## Road Hazard",
            "",
            f"- embree status: `{_fmt(road['embree_status'])}`",
            f"- optix status: `{_fmt(road['optix_status'])}`",
            f"- embree sec: `{_fmt(road['embree_sec'])}`",
            f"- optix sec: `{_fmt(road['optix_sec'])}`",
            f"- ratio embree/optix: `{_fmt(road['ratio_embree_over_optix'])}`",
            f"- timing floor met: `{_fmt(road['timing_floor_met'])}`",
            f"- same-scale public positive candidate: `{_fmt(road['same_scale_public_positive_candidate'])}`",
            "",
            "## Decisions",
            "",
        ]
    )
    for app, decision in payload["decisions"].items():
        lines.append(f"- `{app}`: `{decision}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1204 repaired RTX pod artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "decisions": payload["decisions"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
