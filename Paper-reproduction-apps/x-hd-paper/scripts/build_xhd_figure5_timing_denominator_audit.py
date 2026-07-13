#!/usr/bin/env python3
"""Build the Goal5288 Figure 5 timing denominator audit.

The audit summarizes author run_all timing-log coverage for Figure 5 and
compares it with the current RTDL evidence level.  It intentionally does not
compute an author-vs-RTDL speedup because the denominator is not aligned.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


FIGURE5_CATEGORIES = ("BraTS2020_ValidationData", "geo", "graphics")
FIGURE5_SECTIONS = ("auto_tune", "eb_gpu", "hybrid_gpu", "rt_gpu")


def _load_json(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"could not parse JSON: {path}") from exc


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _file_pair(record: Mapping[str, Any]) -> str:
    files = record["input"]["files"]
    return f"{files[0]['basename']} -> {files[1]['basename']}"


def _input_statuses(record: Mapping[str, Any]) -> list[str]:
    return sorted({str(item.get("exact_status")) for item in record["input"]["files"]})


def _record_stats(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    running = [float(r["running"]["avg_time"]) for r in records if r.get("running", {}).get("avg_time") is not None]
    reported = [
        float(r["running"]["reported_time_median"])
        for r in records
        if r.get("running", {}).get("reported_time_median") is not None
    ]
    repeat_counts = sorted({
        int(r["running"]["repeat_count"])
        for r in records
        if r.get("running", {}).get("repeat_count") is not None
    })
    point_counts = [
        int(item["num_points"])
        for r in records
        for item in r["input"]["files"]
        if item.get("num_points") is not None
    ]
    gpu_names = sorted({
        str(r.get("gpu", {}).get("name"))
        for r in records
        if r.get("gpu", {}).get("name")
    })
    return {
        "record_count": len(records),
        "unique_pair_count": len({_file_pair(r) for r in records}),
        "running_avg_time_median": _median(running),
        "reported_time_median_median": _median(reported),
        "repeat_counts": repeat_counts,
        "gpu_names": gpu_names,
        "point_count_min": min(point_counts) if point_counts else None,
        "point_count_max": max(point_counts) if point_counts else None,
    }


def build_figure5_audit(*, log_index_path: Path, coverage_gap_path: Path, date: str) -> dict[str, Any]:
    log_index = _load_json(log_index_path)
    coverage = _load_json(coverage_gap_path)
    records = [
        r
        for r in log_index["run_all_records"]
        if r.get("category") in FIGURE5_CATEGORIES and r.get("section") in FIGURE5_SECTIONS
    ]

    by_category: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_section: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    by_category_section: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    pair_records: dict[str, list[Mapping[str, Any]]] = defaultdict(list)

    for record in records:
        category = str(record["category"])
        section = str(record["section"])
        pair = _file_pair(record)
        by_category[category].append(record)
        by_section[section].append(record)
        by_category_section[(category, section)].append(record)
        pair_records[pair].append(record)

    pair_section_counts: dict[str, Counter[str]] = {}
    pair_config_counts: dict[str, Counter[str]] = {}
    pair_categories: dict[str, str] = {}
    pair_exact_statuses: dict[str, list[str]] = {}
    for pair, pair_recs in pair_records.items():
        pair_section_counts[pair] = Counter(str(r["section"]) for r in pair_recs)
        pair_config_counts[pair] = Counter(str(r["config"]) for r in pair_recs)
        pair_categories[pair] = str(pair_recs[0]["category"])
        pair_exact_statuses[pair] = sorted({status for r in pair_recs for status in _input_statuses(r)})

    complete_author_pairs = [
        pair
        for pair, counts in pair_section_counts.items()
        if counts["auto_tune"] == 2
        and counts["eb_gpu"] == 1
        and counts["hybrid_gpu"] == 1
        and counts["rt_gpu"] == 1
    ]
    incomplete_author_pairs = sorted(set(pair_records) - set(complete_author_pairs))

    category_summary = {}
    for category in FIGURE5_CATEGORIES:
        category_summary[category] = {
            **_record_stats(by_category.get(category, [])),
            "by_section": {
                section: _record_stats(by_category_section.get((category, section), []))
                for section in FIGURE5_SECTIONS
            },
        }

    rtdl_entrypoint = coverage.get("current_entrypoint_evidence", {})
    covered_workloads = rtdl_entrypoint.get("covered_workloads", [])
    rtdl_coverage = {
        "modelnet40_all400_present_but_not_figure5_category": any(
            "ModelNet40" in str(item.get("name")) for item in covered_workloads
        ),
        "graphics_representative_count": sum(
            1
            for item in covered_workloads
            if any(name in str(item.get("name")) for name in ("Dragon", "ThaiStatuette"))
        ),
        "brats_full_workload_gate_present": False,
        "geo_full_workload_gate_present": False,
        "figure5_full_matrix_gate_present": False,
        "source_artifact": str(coverage_gap_path),
    }

    claim_boundary = {
        "figure5_reproduced": False,
        "performance_ratio_claimed": False,
        "author_rt_core_parity_claimed": False,
        "exact_paper_dataset_reproduction_claimed": False,
        "full_paper_reproduction_claimed": False,
    }

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5288.figure5_timing_denominator_audit.v1",
        "goal": "Goal5288",
        "date": date,
        "status": "figure5_author_timing_denominator_audit_ready__figure5_not_reproduced",
        "inputs": {
            "log_index": str(log_index_path),
            "coverage_gap_matrix": str(coverage_gap_path),
        },
        "author_figure5_log_denominator": {
            "categories": list(FIGURE5_CATEGORIES),
            "sections": list(FIGURE5_SECTIONS),
            "record_count": len(records),
            "unique_pair_count": len(pair_records),
            "complete_author_pair_count": len(complete_author_pairs),
            "incomplete_author_pair_count": len(incomplete_author_pairs),
            "category_summary": category_summary,
            "section_summary": {section: _record_stats(by_section.get(section, [])) for section in FIGURE5_SECTIONS},
            "example_pairs": [
                {
                    "file_pair": pair,
                    "category": pair_categories[pair],
                    "section_counts": dict(pair_section_counts[pair]),
                    "config_counts": dict(pair_config_counts[pair]),
                    "exact_statuses": pair_exact_statuses[pair],
                }
                for pair in sorted(pair_records)[:8]
            ],
        },
        "timing_denominator": {
            "author_available_fields": [
                "Running.AvgTime",
                "Running.ReportedTime median",
                "Running.repeat_count",
                "GPU name in author log",
            ],
            "author_missing_fields_for_fair_wall_ratio": [
                "author process wall time under current reproducible build",
                "same hardware RTDL route timing for every Figure 5 category",
                "exact input file bytes/hashes or externally accepted same-source provenance",
            ],
            "author_gpu_names": sorted({
                name
                for summary in category_summary.values()
                for name in summary["gpu_names"]
            }),
            "rtdl_current_coverage": rtdl_coverage,
            "same_denominator_author_rtdl_performance": False,
        },
        "decision": {
            "figure5_reproduced": False,
            "performance_ratio_allowed": False,
            "why_not_reproduced": [
                "Author logs cover Figure 5 workload families but do not provide exact input bytes or hashes.",
                "Current RTDL evidence covers ModelNet40 and selected graphics representatives, not BraTS and geospatial Figure 5 full workloads.",
                "Author internal Running.AvgTime / ReportedTime medians are not the same denominator as RTDL route wall or process wall.",
                "No denominator-aligned RTDL/author performance matrix exists for all Figure 5 categories.",
            ],
            "next_options": [
                "Acquire or reconstruct Figure 5 inputs with provenance for BraTS, geo, and graphics.",
                "Run author hd_exec and RTDL hd_exec-compatible routes on the same POD for a bounded Figure 5 subset.",
                "Build a denominator-aligned Figure 5 matrix only after matching input provenance and timing phases.",
            ],
            "forbidden_summaries": [
                "Figure 5 reproduced",
                "RTDL/author Figure 5 speedup",
                "author Running.AvgTime equals RTDL route wall",
                "ModelNet40 all400 proves Figure 5",
            ],
        },
        "claim_boundary": claim_boundary,
        "matched": (
            len(records) == 2535
            and len(pair_records) == 507
            and len(complete_author_pairs) == 507
            and not incomplete_author_pairs
            and all(value is False for value in claim_boundary.values())
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Figure 5 timing denominator audit.")
    parser.add_argument("--log-index", required=True)
    parser.add_argument("--coverage-gap-matrix", required=True)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    artifact = build_figure5_audit(
        log_index_path=Path(args.log_index),
        coverage_gap_path=Path(args.coverage_gap_matrix),
        date=args.date,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "status": artifact["status"], "matched": artifact["matched"]}, indent=2))
    return 0 if artifact["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
