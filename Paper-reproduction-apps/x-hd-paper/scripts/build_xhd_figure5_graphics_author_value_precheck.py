#!/usr/bin/env python3
"""Build Goal5290 Figure 5 graphics author-value precheck.

This consumes a cheap POD author-only probe for available Dragon -> AsianDragon
input variants and compares those values to the paper-branch Figure 5 graphics
author log.  It intentionally does not run RTDL and does not produce a
performance ratio.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


TARGET_PAIR = ("dragon.ply", "asian_dragon.ply")
TOLERANCE = 1e-5


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def _parse_stdout_tail(text: str) -> dict[str, float | None]:
    distance_match = re.search(r"HausdorffDistance:\s+distance is\s+([0-9eE+\-.]+)", text)
    avg_match = re.search(r"Avg Running Time\s+([0-9eE+\-.]+)\s+ms", text)
    return {
        "stdout_hd_result": float(distance_match.group(1)) if distance_match else None,
        "stdout_avg_time_ms": float(avg_match.group(1)) if avg_match else None,
    }


def _paper_log_rows(log_index: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for record in log_index.get("run_all_records", []):
        files = tuple(item.get("basename") for item in record.get("input", {}).get("files", []))
        if files == TARGET_PAIR and record.get("category") == "graphics":
            rows.append(record)
    return rows


def build_precheck(*, log_index_path: Path, raw_probe_path: Path, date: str) -> dict[str, Any]:
    log_index = _load_json(log_index_path)
    raw_probe = _load_json(raw_probe_path)
    if not isinstance(raw_probe, list):
        raise ValueError("raw POD probe must be a list of author run rows")

    paper_rows = _paper_log_rows(log_index)
    if not paper_rows:
        raise ValueError("paper log has no Dragon -> AsianDragon graphics rows")
    paper_values = sorted({
        float(row["hd_result"])
        for row in paper_rows
        if row.get("hd_result") is not None
    })
    if len(paper_values) != 1:
        raise ValueError(f"expected exactly one paper HDResult, got {paper_values}")
    paper_hd = paper_values[0]

    candidates: list[dict[str, Any]] = []
    for row in raw_probe:
        parsed = _parse_stdout_tail(str(row.get("stdout_tail", "")))
        observed = parsed["stdout_hd_result"]
        abs_diff = abs(observed - paper_hd) if observed is not None else None
        candidates.append(
            {
                "label": row.get("label"),
                "returncode": row.get("returncode"),
                "wall_sec": row.get("wall_sec"),
                "stdout_hd_result": observed,
                "stdout_avg_time_ms": parsed["stdout_avg_time_ms"],
                "abs_diff_vs_paper_log": abs_diff,
                "matches_paper_log_value": bool(
                    row.get("returncode") == 0
                    and observed is not None
                    and abs_diff is not None
                    and abs_diff <= TOLERANCE
                ),
                "json_files": row.get("json_files", []),
            }
        )

    matching = [row for row in candidates if row["matches_paper_log_value"]]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5290.figure5_graphics_author_value_precheck.v1",
        "goal": "Goal5290",
        "date": date,
        "status": (
            "figure5_graphics_author_value_precheck_ready__no_available_candidate_matches_paper_log"
            if not matching
            else "figure5_graphics_author_value_precheck_ready__candidate_matches_paper_log"
        ),
        "inputs": {
            "log_index": str(log_index_path),
            "raw_pod_author_probe": str(raw_probe_path),
        },
        "paper_log_target": {
            "category": "graphics",
            "pair": list(TARGET_PAIR),
            "record_count": len(paper_rows),
            "sections": sorted({str(row.get("section")) for row in paper_rows}),
            "paper_log_hd_result": paper_hd,
            "point_counts": [
                item.get("num_points")
                for item in paper_rows[0].get("input", {}).get("files", [])
            ],
            "paths": [
                item.get("path")
                for item in paper_rows[0].get("input", {}).get("files", [])
            ],
        },
        "candidate_author_runs": candidates,
        "decision": {
            "candidate_count": len(candidates),
            "matching_candidate_labels": [str(row["label"]) for row in matching],
            "continue_to_rtdl_timing": bool(matching),
            "why": (
                "No available POD author input variant reproduced the paper-log HDResult within tolerance."
                if not matching
                else "At least one available POD author input variant reproduced the paper-log HDResult within tolerance."
            ),
            "next_options": [
                "recover the exact author graphics input files or conversion provenance",
                "find another Figure 5 pair with available value-matched inputs",
                "move to another figure/blocker rather than timing a value-mismatched candidate",
            ],
        },
        "claim_boundary": {
            "figure5_reproduced": False,
            "performance_ratio_claimed": False,
            "rtdl_timing_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
        "matched": bool(
            paper_hd
            and len(candidates) == 2
            and not matching
            and all(value is False for value in {
                "figure5_reproduced": False,
                "performance_ratio_claimed": False,
                "rtdl_timing_claimed": False,
                "exact_paper_dataset_reproduction_claimed": False,
                "full_paper_reproduction_claimed": False,
            }.values())
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 5 graphics author-value precheck.")
    parser.add_argument("--log-index", required=True)
    parser.add_argument("--raw-pod-author-probe", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_precheck(
        log_index_path=Path(args.log_index),
        raw_probe_path=Path(args.raw_pod_author_probe),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "status": artifact["status"], "matched": artifact["matched"]}, indent=2))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
