#!/usr/bin/env python3
"""Map X-HD paper targets to author paper-branch run_all logs.

This script consumes the Goal5130 paper target matrix and the Goal5176
paper-branch log index. It does not reproduce any paper figure. Its job is to
turn the author logs into a machine-readable coverage map: which paper targets
have run_all timing evidence, which targets are only partially covered, and
which remain blocked on input bytes, phase metrics, or script semantics.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def _file_pair_key(record: dict[str, Any]) -> str:
    files = record.get("input", {}).get("files", [])
    names = [str(item.get("basename", "")) for item in files if isinstance(item, dict)]
    return " -> ".join(names)


def _record_brief(record: dict[str, Any]) -> dict[str, Any]:
    files = record.get("input", {}).get("files", [])
    return {
        "section": record.get("section"),
        "category": record.get("category"),
        "config": record.get("config"),
        "file_pair": _file_pair_key(record),
        "relative_log_path": record.get("relative_log_path"),
        "hd_result": record.get("hd_result"),
        "running_avg_time": record.get("running", {}).get("avg_time"),
        "reported_time_median": record.get("running", {}).get("reported_time_median"),
        "num_dims": record.get("input", {}).get("num_dims"),
        "input_point_counts": [
            item.get("num_points") for item in files if isinstance(item, dict)
        ],
        "exact_status": sorted(
            {
                str(item.get("exact_status"))
                for item in files
                if isinstance(item, dict) and item.get("exact_status") is not None
            }
        ),
    }


def _summarize_records(
    records: Iterable[dict[str, Any]],
    *,
    max_examples: int,
) -> dict[str, Any]:
    rows = list(records)
    by_section = Counter(str(row.get("section")) for row in rows)
    by_category = Counter(str(row.get("category")) for row in rows)
    by_pair = Counter(_file_pair_key(row) for row in rows)
    by_config = Counter(str(row.get("config")) for row in rows)
    sections_by_pair: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        sections_by_pair[_file_pair_key(row)].add(str(row.get("section")))
    return {
        "record_count": len(rows),
        "unique_pair_count": len(by_pair),
        "by_section": dict(sorted(by_section.items())),
        "by_category": dict(sorted(by_category.items())),
        "top_pairs": [
            {"file_pair": key, "record_count": value, "sections": sorted(sections_by_pair[key])}
            for key, value in by_pair.most_common(max_examples)
        ],
        "top_configs": [
            {"config": key, "record_count": value}
            for key, value in by_config.most_common(max_examples)
        ],
        "examples": [_record_brief(row) for row in rows[:max_examples]],
    }


def _has_pair(record: dict[str, Any], required_basenames: set[str]) -> bool:
    names = {
        str(item.get("basename"))
        for item in record.get("input", {}).get("files", [])
        if isinstance(item, dict)
    }
    return required_basenames.issubset(names)


def _category(records: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return [row for row in records if row.get("category") == category]


def _pair(records: list[dict[str, Any]], *basenames: str) -> list[dict[str, Any]]:
    return [row for row in records if _has_pair(row, set(basenames))]


def _auto_tune(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in records if row.get("section") == "auto_tune"]


def _sections_present(records: list[dict[str, Any]]) -> list[str]:
    return sorted({str(row.get("section")) for row in records})


def _figure_entry(
    *,
    figure: str,
    subject: str,
    coverage_status: str,
    evidence_records: list[dict[str, Any]],
    max_examples: int,
    available_evidence: list[str],
    missing_evidence: list[str],
    interpretation: str,
) -> dict[str, Any]:
    return {
        "figure": figure,
        "subject": subject,
        "coverage_status": coverage_status,
        "record_summary": _summarize_records(evidence_records, max_examples=max_examples),
        "available_evidence": available_evidence,
        "missing_evidence": missing_evidence,
        "interpretation": interpretation,
    }


def _priority_subset(
    *,
    name: str,
    purpose: str,
    records: list[dict[str, Any]],
    max_examples: int,
    blocker: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "purpose": purpose,
        "status": "paper_log_workload_identified__input_files_missing",
        "record_summary": _summarize_records(records, max_examples=max_examples),
        "blocker": blocker,
        "authorized_next_step": "Acquire or reconstruct the named input files only as Level B unless file/hash provenance proves Level C exact dataset identity.",
    }


def build_mapping(
    target_matrix: dict[str, Any],
    log_index: dict[str, Any],
    *,
    max_examples: int = 5,
) -> dict[str, Any]:
    records = list(log_index.get("run_all_records", []))
    graphics = _category(records, "graphics")
    geo = _category(records, "geo")
    brats = _category(records, "BraTS2020_ValidationData")
    modelnet = _category(records, "ModelNet40")
    dragon_asian = _pair(records, "dragon.ply", "asian_dragon.ply")
    dragon_buddha = _pair(records, "dragon.ply", "happy_buddha.ply")
    thai_asian = _pair(records, "thai_statuette.ply", "asian_dragon.ply")
    thai_buddha = _pair(records, "thai_statuette.ply", "happy_buddha.ply")
    lakes_parks = _pair(records, "lakes.bz2.wkt", "parks.bz2.wkt")
    county_zip = _pair(records, "dtl_cnty.wkt", "uszipcode.wkt")
    water_census = _pair(
        records,
        "USADetailedWaterBodies.wkt",
        "USACensusBlockGroupBoundaries.wkt",
    )

    figure5_records = brats + geo + graphics
    figure6_records = dragon_asian
    figure7_records = lakes_parks + graphics
    figure9_records = _auto_tune(records)
    figure10_records = brats + modelnet + geo + graphics
    first_brats_pair: list[dict[str, Any]] = []
    if brats:
        first_files = brats[0].get("input", {}).get("files", [])
        first_names = [
            str(item.get("basename"))
            for item in first_files
            if isinstance(item, dict) and item.get("basename") is not None
        ]
        if len(first_names) >= 2:
            first_brats_pair = _pair(records, first_names[0], first_names[1])

    figures = [
        _figure_entry(
            figure="Figure 5",
            subject="Overall performance across MRI, geospatial, and graphics datasets",
            coverage_status="run_all_timing_logs_cover_required_workload_families__inputs_missing",
            evidence_records=figure5_records,
            max_examples=max_examples,
            available_evidence=[
                "run_all records for BraTS, geospatial, and Stanford graphics workloads",
                "author HDResult",
                "author Running.AvgTime and per-repeat ReportedTime median",
                "GPU name",
                "logged point counts and MBRs",
            ],
            missing_evidence=[
                "input file bytes and hashes",
                "proof reconstructed public data are exact paper inputs",
                "process wall time under a reproducible local build",
                "denominator-aligned RTDL route matrix on the same hardware",
            ],
            interpretation="Figure 5 has the strongest paper-log workload coverage, but it remains blocked from figure reproduction by missing exact input files and fair RTDL/author denominator alignment.",
        ),
        _figure_entry(
            figure="Figure 6",
            subject="Pruning effectiveness on Dragon-AsianDragon",
            coverage_status="partially_covered_by_run_all_timing_logs__phase_counters_missing",
            evidence_records=figure6_records,
            max_examples=max_examples,
            available_evidence=[
                "Dragon-AsianDragon run_all records across rt_gpu, eb_gpu, hybrid_gpu, and auto_tune sections",
                "author HDResult and Running.AvgTime for those records",
            ],
            missing_evidence=[
                "No-Opt / EB / EB+Prune / RT-HDIST phase mapping",
                "intersection counts",
                "visited point-pair counts",
                "input file bytes and hashes",
            ],
            interpretation="The target pair is present, but Figure 6 cannot be reproduced from run_all timing logs alone because required pruning counters and phase semantics are absent.",
        ),
        _figure_entry(
            figure="Figure 7",
            subject="Load balance / heavy-cell offload effectiveness",
            coverage_status="partially_covered_by_run_all_workloads__load_balance_metrics_missing",
            evidence_records=figure7_records,
            max_examples=max_examples,
            available_evidence=[
                "OSM Lakes-Parks run_all records",
                "selected graphics run_all records",
                "author HDResult and Running.AvgTime",
            ],
            missing_evidence=[
                "RT shader time",
                "CUDA offload kernel time",
                "with/without load-balancing phase split",
                "large geospatial input bytes and hashes",
            ],
            interpretation="The large Lakes-Parks workload exists in run_all logs, but load-balance phase metrics are not present in the extracted records.",
        ),
        _figure_entry(
            figure="Figure 8",
            subject="Radius-growing strategy",
            coverage_status="not_covered_by_run_all_timing_logs",
            evidence_records=[],
            max_examples=max_examples,
            available_evidence=[],
            missing_evidence=[
                "paper-selected radius strategy workloads",
                "radius-growth strategy labels",
                "iteration or radius diagnostics",
                "input file bytes and hashes",
            ],
            interpretation="No explicit radius-growing strategy evidence was identified in the run_all log index; this target remains script/algorithm mapping work.",
        ),
        _figure_entry(
            figure="Figure 9",
            subject="Adaptive grid sizing",
            coverage_status="partially_covered_by_auto_tune_logs__grid_sweep_semantics_missing",
            evidence_records=figure9_records,
            max_examples=max_examples,
            available_evidence=[
                "auto_tune run_all records for BraTS, ModelNet40, geo, and graphics categories",
                "two observed configs: n_points_cell_false_max_hit_false and n_points_cell_true_max_hit_true",
                "NumPointsPerCell value recorded in Running",
            ],
            missing_evidence=[
                "full adaptive-grid parameter sweep semantics",
                "paper's exact selected grid-size choices",
                "input file bytes and hashes",
            ],
            interpretation="Auto-tune logs are present and useful, but their config labels are not yet a full Figure 9 adaptive-grid semantics map.",
        ),
        _figure_entry(
            figure="Figure 10",
            subject="Scalability and overlap sensitivity",
            coverage_status="workload_families_present__scale_overlap_labels_missing",
            evidence_records=figure10_records,
            max_examples=max_examples,
            available_evidence=[
                "many BraTS and ModelNet40 run_all pairs plus smaller geo/graphics sets",
                "logged point counts for every input file",
                "author HDResult and Running.AvgTime",
            ],
            missing_evidence=[
                "paper scalability subset selection",
                "overlap-controlled input generation details",
                "overlap/selectivity diagnostics",
                "input file bytes and hashes",
            ],
            interpretation="The log index contains enough records to choose scale candidates, but it does not identify the paper's overlap/scalability subsets.",
        ),
        _figure_entry(
            figure="Figure 11",
            subject="Memory footprint",
            coverage_status="not_covered_by_run_all_timing_logs",
            evidence_records=[],
            max_examples=max_examples,
            available_evidence=[],
            missing_evidence=[
                "GPU memory footprint measurements",
                "author memory accounting boundary",
                "paper-selected workloads",
            ],
            interpretation="The extracted run_all records do not contain memory metrics, so Figure 11 remains blocked on instrumentation or author-script evidence.",
        ),
    ]

    priority_subsets = [
        _priority_subset(
            name="graphics_dragon_happy_buddha",
            purpose="Small Stanford graphics Level B workload already used by the RTDL representative route; useful for first end-to-end paper-log-to-route rehearsal.",
            records=dragon_buddha,
            max_examples=max_examples,
            blocker="Need author/exact converted dragon.ply and happy_buddha.ply bytes or documented same-source reconstruction; current logs only provide paths/statistics/HDResult.",
        ),
        _priority_subset(
            name="graphics_dragon_asian_dragon",
            purpose="Figure 6 pruning-effectiveness target pair; smallest direct bridge from paper target matrix to a named run_all pair.",
            records=dragon_asian,
            max_examples=max_examples,
            blocker="Need phase counter semantics plus input bytes/hashes; timing logs alone do not reproduce Figure 6.",
        ),
        _priority_subset(
            name="geo_county_zipcode",
            purpose="Moderate geospatial Figure 5 family target with explicit run_all path names.",
            records=county_zip,
            max_examples=max_examples,
            blocker="Need WKT source snapshot/conversion proof; count/statistics alone are not exact paper input identity.",
        ),
        _priority_subset(
            name="geo_lakes_parks",
            purpose="Large Figure 7 / Figure 5 geospatial stress target present in run_all logs.",
            records=lakes_parks,
            max_examples=max_examples,
            blocker="Need large WKT input files and load-balance phase metrics before any Figure 7 reproduction claim.",
        ),
        _priority_subset(
            name="brats_first_logged_pair",
            purpose="MRI Figure 5 family smoke target; choose the first paper-branch logged BraTS pair only after access/licensing is resolved.",
            records=first_brats_pair,
            max_examples=max_examples,
            blocker="Need BraTS access/license plus exact validation image list or same-source labeling.",
        ),
    ]

    status_counts = Counter(row["coverage_status"] for row in figures)
    return {
        "schema": "rtdl.paper_reproduction.xhd.paper_target_log_mapping.v1",
        "goal": "Goal5177",
        "status": "xhd_paper_target_log_mapping_ready__no_figure_reproduction_claim",
        "sources": {
            "target_matrix_goal": target_matrix.get("goal"),
            "target_matrix_status": target_matrix.get("status"),
            "log_index_goal": log_index.get("goal"),
            "paper_branch_commit": log_index.get("author_repo", {}).get("head"),
        },
        "run_all_summary": {
            "record_count": len(records),
            "by_section": dict(sorted(Counter(str(row.get("section")) for row in records).items())),
            "by_category": dict(sorted(Counter(str(row.get("category")) for row in records).items())),
            "unique_pair_count": len({_file_pair_key(row) for row in records}),
            "sections_present": _sections_present(records),
            "modelnet_note": "ModelNet40 appears in paper-branch run_all logs but was not a named Goal5130 Table 1 target; keep it as paper-branch workload evidence until target matrix is revised.",
        },
        "figure_mappings": figures,
        "coverage_status_counts": dict(sorted(status_counts.items())),
        "priority_subsets": priority_subsets,
        "exact_dataset_rule": {
            "logs_provide": [
                "author path names",
                "dataset basenames",
                "HDResult",
                "Running.AvgTime",
                "ReportedTime medians",
                "point counts and MBRs when logged",
            ],
            "logs_do_not_provide": [
                "input file bytes",
                "input file hashes",
                "public source snapshot hashes",
                "proof that reconstructed public data are exact paper inputs",
            ],
            "statistics_matching_is_not_exact_identity": True,
        },
        "claim_boundary": {
            "full_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "paper_input_bytes_available": False,
        },
        "authorized_next_steps": [
            "Use priority_subsets to decide the first exact-input acquisition target.",
            "Do not implement more route code for figures whose blockers are input provenance or missing author phase counters.",
            "If inputs are reconstructed from public sources, label them Level B unless file/hash provenance proves Level C.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-matrix", required=True, type=Path)
    parser.add_argument("--log-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-examples", type=int, default=5)
    args = parser.parse_args()

    target_matrix = json.loads(args.target_matrix.read_text())
    log_index = json.loads(args.log_index.read_text())
    mapping = build_mapping(
        target_matrix,
        log_index,
        max_examples=args.max_examples,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(mapping, indent=2, sort_keys=True))
    print(
        "wrote",
        args.output,
        "figures=",
        len(mapping["figure_mappings"]),
        "run_all_records=",
        mapping["run_all_summary"]["record_count"],
    )


if __name__ == "__main__":
    main()
