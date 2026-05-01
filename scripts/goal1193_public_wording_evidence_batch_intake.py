#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1193 public wording evidence batch intake"
DEFAULT_INPUT_DIR = ROOT / "docs/reports/goal1192_public_wording_evidence_batch"
DEFAULT_JSON = ROOT / "docs/reports/goal1193_public_wording_evidence_batch_intake_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1193_public_wording_evidence_batch_intake_2026-04-30.md"
TIMING_FLOOR_SEC = 0.1


def _nested(data: Any, path: tuple[Any, ...]) -> Any:
    value = data
    for key in path:
        value = value[key]
    return value


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _first_float(data: Any, paths: tuple[tuple[Any, ...], ...]) -> tuple[float | None, str]:
    for path in paths:
        try:
            value = _float_or_none(_nested(data, path))
        except Exception:
            continue
        if value is not None:
            return value, ".".join(map(str, path))
    return None, ""


def _load_json(path: Path) -> tuple[Any, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:  # pragma: no cover - diagnostic path.
        return None, str(exc)


ARTIFACTS: dict[str, dict[str, Any]] = {
    "database_compact_summary_embree.json": {
        "app": "database_analytics",
        "backend": "embree",
        "status_paths": (("results", 0, "status"),),
        "ok_statuses": {"ok"},
        "phase_paths": (("results", 0, "prepared_session_warm_query_sec", "median_sec"),),
        "required_paths": (
            ("results", 0, "prepared_session_warm_query_sec", "median_sec"),
            ("results", 0, "reported_run_phase_totals_sec", "compact_summary_operation_count"),
        ),
    },
    "database_compact_summary_optix.json": {
        "app": "database_analytics",
        "backend": "optix",
        "status_paths": (("results", 0, "status"),),
        "ok_statuses": {"ok"},
        "phase_paths": (("results", 0, "prepared_session_warm_query_sec", "median_sec"),),
        "required_paths": (
            ("results", 0, "prepared_session_warm_query_sec", "median_sec"),
            ("results", 0, "reported_native_db_phase_totals_sec", "counter_status"),
        ),
    },
    "graph_visibility_edges_embree.json": {
        "app": "graph_analytics",
        "backend": "embree",
        "phase_paths": (("graph_phase_totals_sec", "query_visibility_pair_rows_sec"),),
        "required_paths": (
            ("graph_phase_totals_sec", "query_visibility_pair_rows_sec"),
            ("sections", "visibility_edges", "summary", "blocked_edge_count"),
        ),
    },
    "graph_visibility_edges_optix.json": {
        "app": "graph_analytics",
        "backend": "optix",
        "status_paths": (("status",),),
        "ok_statuses": {"pass"},
        "phase_paths": (("records_by_label", "optix_visibility_anyhit", "sec"), ("records", 0, "sec")),
        "required_paths": (
            ("status",),
            ("strict_pass",),
            ("records_by_label", "optix_visibility_anyhit", "status"),
            ("records_by_label", "optix_visibility_anyhit", "digest", "summary", "blocked_edge_count"),
        ),
        "must_be_true_paths": (("strict_pass",),),
    },
    "road_hazard_native_summary_embree.json": {
        "app": "road_hazard_screening",
        "backend": "embree",
        "phase_paths": (("run_phases", "query_and_materialize_sec"),),
        "required_paths": (("run_phases", "query_and_materialize_sec"), ("priority_segment_count",)),
    },
    "road_hazard_native_summary_optix.json": {
        "app": "road_hazard_screening",
        "backend": "optix",
        "status_paths": (("status",),),
        "ok_statuses": {"pass"},
        "phase_paths": (("timings_sec", "optix_query_sec", "median_sec"),),
        "required_paths": (
            ("status",),
            ("strict_pass",),
            ("timings_sec", "optix_query_sec", "median_sec"),
            ("result", "matches_oracle"),
        ),
        "must_be_true_paths": (("strict_pass",), ("result", "matches_oracle")),
    },
    "polygon_pair_candidate_discovery_embree.json": {
        "app": "polygon_pair_overlap_area_rows",
        "backend": "embree",
        "phase_paths": (("run_phases", "rt_candidate_discovery_sec"),),
        "required_paths": (
            ("run_phases", "rt_candidate_discovery_sec"),
            ("run_phases", "native_exact_continuation_sec"),
            ("candidate_row_count",),
        ),
    },
    "polygon_pair_candidate_discovery_optix.json": {
        "app": "polygon_pair_overlap_area_rows",
        "backend": "optix",
        "status_paths": (("status",),),
        "ok_statuses": {"pass"},
        "phase_paths": (("phases", "optix_candidate_discovery_sec"),),
        "required_paths": (
            ("status",),
            ("parity_vs_cpu",),
            ("phases", "optix_candidate_discovery_sec"),
            ("optix_metadata", "rt_core_candidate_discovery_active"),
        ),
        "must_be_true_paths": (("parity_vs_cpu",), ("optix_metadata", "rt_core_candidate_discovery_active")),
    },
    "polygon_jaccard_safe_chunk_embree.json": {
        "app": "polygon_set_jaccard",
        "backend": "embree",
        "phase_paths": (("run_phases", "rt_candidate_discovery_sec"),),
        "required_paths": (
            ("run_phases", "rt_candidate_discovery_sec"),
            ("run_phases", "native_exact_continuation_sec"),
            ("candidate_row_count",),
        ),
    },
    "polygon_jaccard_safe_chunk_optix.json": {
        "app": "polygon_set_jaccard",
        "backend": "optix",
        "status_paths": (("status",),),
        "ok_statuses": {"pass"},
        "phase_paths": (("phases", "optix_candidate_discovery_sec"),),
        "required_paths": (
            ("status",),
            ("parity_vs_cpu",),
            ("phases", "optix_candidate_discovery_sec"),
            ("optix_metadata", "rt_core_candidate_discovery_active"),
        ),
        "must_be_true_paths": (("parity_vs_cpu",), ("optix_metadata", "rt_core_candidate_discovery_active")),
    },
    "hausdorff_threshold_prepared_embree.json": {
        "app": "hausdorff_distance",
        "backend": "embree",
        "phase_paths": (("run_phases", "native_directed_summary_sec"),),
        "required_paths": (("run_phases", "native_directed_summary_sec"), ("matches_oracle",)),
        "must_be_true_paths": (("matches_oracle",),),
    },
    "hausdorff_threshold_prepared_optix.json": {
        "app": "hausdorff_distance",
        "backend": "optix",
        "phase_paths": (("scenario", "timings_sec", "optix_query_sec", "median_sec"), ("timings_sec", "optix_query_sec", "median_sec")),
        "required_paths": (
            ("scenario", "mode"),
            ("scenario", "timings_sec", "optix_query_sec", "median_sec"),
            ("scenario", "result", "matches_oracle"),
        ),
        "must_be_true_paths": (("scenario", "result", "matches_oracle"),),
    },
}


PAIRS: dict[str, tuple[str, str]] = {
    "database_analytics": ("database_compact_summary_embree.json", "database_compact_summary_optix.json"),
    "graph_analytics": ("graph_visibility_edges_embree.json", "graph_visibility_edges_optix.json"),
    "road_hazard_screening": ("road_hazard_native_summary_embree.json", "road_hazard_native_summary_optix.json"),
    "polygon_pair_overlap_area_rows": (
        "polygon_pair_candidate_discovery_embree.json",
        "polygon_pair_candidate_discovery_optix.json",
    ),
    "polygon_set_jaccard": ("polygon_jaccard_safe_chunk_embree.json", "polygon_jaccard_safe_chunk_optix.json"),
    "hausdorff_distance": ("hausdorff_threshold_prepared_embree.json", "hausdorff_threshold_prepared_optix.json"),
}


def _normalize_graph_records(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    records = data.get("records")
    if not isinstance(records, list):
        return data
    data = dict(data)
    data["records_by_label"] = {
        str(record.get("label")): record
        for record in records
        if isinstance(record, dict) and record.get("label") is not None
    }
    return data


def _read_artifact(input_dir: Path, name: str) -> dict[str, Any]:
    spec = ARTIFACTS[name]
    path = input_dir / name
    row: dict[str, Any] = {
        "artifact": name,
        "app": spec["app"],
        "backend": spec["backend"],
        "path": str(path),
        "exists": path.exists(),
        "parse_error": "",
        "missing_required_paths": [],
        "failed_truth_paths": [],
        "unexpected_status": "",
        "phase_sec": None,
        "phase_path": "",
        "timing_floor_met": False,
        "valid_schema": False,
    }
    if not path.exists():
        row["missing_required_paths"] = ["artifact"]
        return row
    data, parse_error = _load_json(path)
    row["parse_error"] = parse_error
    if parse_error:
        return row
    data = _normalize_graph_records(data)
    status_paths = spec.get("status_paths", ())
    ok_statuses = spec.get("ok_statuses")
    for status_path in status_paths:
        try:
            status = _nested(data, status_path)
        except Exception:
            continue
        row["status"] = status
        if ok_statuses is not None and status not in ok_statuses:
            row["unexpected_status"] = f"{'.'.join(map(str, status_path))}={status!r}"
        break
    for required_path in spec["required_paths"]:
        try:
            _nested(data, required_path)
        except Exception:
            row["missing_required_paths"].append(".".join(map(str, required_path)))
    for truth_path in spec.get("must_be_true_paths", ()):
        try:
            if _nested(data, truth_path) is not True:
                row["failed_truth_paths"].append(".".join(map(str, truth_path)))
        except Exception:
            row["failed_truth_paths"].append(".".join(map(str, truth_path)))
    phase_sec, phase_path = _first_float(data, spec["phase_paths"])
    row["phase_sec"] = phase_sec
    row["phase_path"] = phase_path
    row["timing_floor_met"] = bool(phase_sec is not None and phase_sec >= TIMING_FLOOR_SEC)
    row["valid_schema"] = not (
        row["parse_error"]
        or row["missing_required_paths"]
        or row["failed_truth_paths"]
        or row["unexpected_status"]
        or phase_sec is None
    )
    return row


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or numerator <= 0:
        return None
    return denominator / numerator


def _review_archive(input_dir: Path) -> dict[str, Any]:
    archive = Path(str(input_dir) + ".tgz")
    sha = Path(str(input_dir) + ".tgz.sha256")
    return {
        "archive": str(archive),
        "archive_exists": archive.exists(),
        "archive_readable": _tar_readable(archive) if archive.exists() else False,
        "sha256_file": str(sha),
        "sha256_file_exists": sha.exists(),
    }


def _tar_readable(path: Path) -> bool:
    try:
        with tarfile.open(path, "r:gz") as archive:
            archive.getmembers()
        return True
    except Exception:
        return False


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    rows = [_read_artifact(input_dir, name) for name in ARTIFACTS]
    by_name = {row["artifact"]: row for row in rows}
    pairs: list[dict[str, Any]] = []
    for app, (embree_name, optix_name) in PAIRS.items():
        embree = by_name[embree_name]
        optix = by_name[optix_name]
        ratio = _safe_ratio(optix["phase_sec"], embree["phase_sec"])
        pairs.append(
            {
                "app": app,
                "embree_artifact": embree_name,
                "optix_artifact": optix_name,
                "embree_phase_sec": embree["phase_sec"],
                "optix_phase_sec": optix["phase_sec"],
                "embree_timing_floor_met": embree["timing_floor_met"],
                "optix_timing_floor_met": optix["timing_floor_met"],
                "same_contract_pair_schema_valid": embree["valid_schema"] and optix["valid_schema"],
                "timing_floor_pair_met": embree["timing_floor_met"] and optix["timing_floor_met"],
                "raw_phase_ratio_embree_over_optix": ratio,
                "public_wording_review_ready": (
                    embree["valid_schema"]
                    and optix["valid_schema"]
                    and embree["timing_floor_met"]
                    and optix["timing_floor_met"]
                ),
            }
        )
    schema_valid = all(row["valid_schema"] for row in rows)
    ready_pairs = [row["app"] for row in pairs if row["public_wording_review_ready"]]
    not_ready_pairs = [row["app"] for row in pairs if not row["public_wording_review_ready"]]
    return {
        "goal": GOAL,
        "date": DATE,
        "input_dir": str(input_dir),
        "valid": schema_valid,
        "artifact_count": len(rows),
        "valid_schema_artifact_count": sum(1 for row in rows if row["valid_schema"]),
        "pair_count": len(pairs),
        "public_wording_review_ready_pair_count": len(ready_pairs),
        "public_wording_review_ready_apps": ready_pairs,
        "not_ready_apps": not_ready_pairs,
        "archive": _review_archive(input_dir),
        "rows": rows,
        "pairs": pairs,
        "timing_floor_sec": TIMING_FLOOR_SEC,
        "boundary": (
            "This intake validates copied Goal1192 evidence artifacts only. It does not run cloud, "
            "does not authorize release, and does not authorize public RTX speedup wording by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1193 Public Wording Evidence Batch Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid schema: `{payload['valid']}`",
        f"Input dir: `{payload['input_dir']}`",
        f"Timing floor: `{payload['timing_floor_sec']}` seconds",
        "",
        "## Pair Readiness",
        "",
        "| App | Schema valid | Timing floor met | Embree phase sec | OptiX phase sec | Raw ratio | Public wording review ready |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload["pairs"]:
        ratio = row["raw_phase_ratio_embree_over_optix"]
        ratio_text = "n/a" if ratio is None else f"{ratio:.6g}"
        lines.append(
            f"| `{row['app']}` | `{row['same_contract_pair_schema_valid']}` | `{row['timing_floor_pair_met']}` | "
            f"`{row['embree_phase_sec']}` | `{row['optix_phase_sec']}` | `{ratio_text}` | "
            f"`{row['public_wording_review_ready']}` |"
        )
    lines.extend(
        [
            "",
            "## Artifact Schema",
            "",
            "| Artifact | Exists | Schema valid | Phase path | Phase sec | Timing floor | Problems |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        problems = []
        if row["parse_error"]:
            problems.append(f"parse={row['parse_error']}")
        if row["missing_required_paths"]:
            problems.append(f"missing={row['missing_required_paths']}")
        if row["failed_truth_paths"]:
            problems.append(f"false={row['failed_truth_paths']}")
        if row["unexpected_status"]:
            problems.append(f"status={row['unexpected_status']}")
        problems_text = "; ".join(problems) or "none"
        lines.append(
            f"| `{row['artifact']}` | `{row['exists']}` | `{row['valid_schema']}` | "
            f"`{row['phase_path']}` | `{row['phase_sec']}` | `{row['timing_floor_met']}` | {problems_text} |"
        )
    lines.extend(["", "## Archive", ""])
    archive = payload["archive"]
    lines.append(f"- archive exists: `{archive['archive_exists']}`")
    lines.append(f"- archive readable: `{archive['archive_readable']}`")
    lines.append(f"- sha256 file exists: `{archive['sha256_file_exists']}`")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake copied Goal1192 public wording evidence artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": payload["valid"],
                "artifact_count": payload["artifact_count"],
                "ready_pairs": payload["public_wording_review_ready_pair_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
