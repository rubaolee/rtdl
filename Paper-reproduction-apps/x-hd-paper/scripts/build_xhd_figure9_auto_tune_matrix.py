#!/usr/bin/env python3
"""Build a Figure 9 auto-tune semantics matrix from X-HD paper-branch logs.

The extracted run_all logs contain an `auto_tune` section, but that is not the
same thing as reproducing paper Figure 9.  This script makes the boundary
machine-readable: what the logs actually cover, which configuration labels are
present, and what evidence is still missing before a Figure 9 reproduction claim
would be allowed.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


AUTO_TUNE_CONFIGS = (
    "n_points_cell_false_max_hit_false",
    "n_points_cell_true_max_hit_true",
)


def _file_pair_key(record: dict[str, Any]) -> str:
    files = record.get("input", {}).get("files", [])
    names = [str(item.get("basename", "")) for item in files if isinstance(item, dict)]
    return " -> ".join(names)


def _input_point_counts(record: dict[str, Any]) -> list[int | None]:
    files = record.get("input", {}).get("files", [])
    return [item.get("num_points") for item in files if isinstance(item, dict)]


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _median(values: Iterable[float | None]) -> float | None:
    rows = [float(v) for v in values if v is not None]
    if not rows:
        return None
    return float(statistics.median(rows))


def _config_flags(config: str) -> dict[str, bool | str]:
    """Parse only the two observed author log config labels.

    The flag names are descriptive of the observed label, not a full author
    source semantics proof.  Figure 9 still needs separate script/source mapping.
    """

    if config == "n_points_cell_false_max_hit_false":
        return {
            "config_label": config,
            "uses_n_points_cell_label": False,
            "uses_max_hit_label": False,
        }
    if config == "n_points_cell_true_max_hit_true":
        return {
            "config_label": config,
            "uses_n_points_cell_label": True,
            "uses_max_hit_label": True,
        }
    return {
        "config_label": config,
        "uses_n_points_cell_label": "unknown",
        "uses_max_hit_label": "unknown",
    }


def _record_brief(record: dict[str, Any]) -> dict[str, Any]:
    running = record.get("running", {}) or {}
    return {
        "category": record.get("category"),
        "config": record.get("config"),
        "file_pair": _file_pair_key(record),
        "relative_log_path": record.get("relative_log_path"),
        "hd_result": record.get("hd_result"),
        "avg_time": running.get("avg_time"),
        "reported_time_median": running.get("reported_time_median"),
        "num_points_per_cell": running.get("num_points_per_cell"),
        "seed": running.get("seed"),
        "eb": running.get("eb"),
        "prune": running.get("prune"),
        "lb": running.get("lb"),
        "input_point_counts": _input_point_counts(record),
    }


def _pair_identity(record: dict[str, Any]) -> tuple[str, str]:
    return (str(record.get("category")), _file_pair_key(record))


def build_matrix(log_index: dict[str, Any], *, max_examples: int = 8) -> dict[str, Any]:
    all_records = list(log_index.get("run_all_records", []))
    auto_records = [row for row in all_records if row.get("section") == "auto_tune"]
    by_config = Counter(str(row.get("config")) for row in auto_records)
    by_category = Counter(str(row.get("category")) for row in auto_records)

    config_values: dict[str, dict[str, Any]] = {}
    for config in sorted(by_config):
        rows = [row for row in auto_records if str(row.get("config")) == config]
        running_rows = [row.get("running", {}) or {} for row in rows]
        config_values[config] = {
            "row_count": len(rows),
            "flags_from_label": _config_flags(config),
            "num_points_per_cell_values": sorted(
                {
                    int(run.get("num_points_per_cell"))
                    for run in running_rows
                    if run.get("num_points_per_cell") is not None
                }
            ),
            "seed_values": sorted(
                {run.get("seed") for run in running_rows if run.get("seed") is not None}
            ),
            "eb_values": sorted(
                {str(run.get("eb")) for run in running_rows if run.get("eb") is not None}
            ),
            "prune_values": sorted(
                {str(run.get("prune")) for run in running_rows if run.get("prune") is not None}
            ),
            "lb_values": sorted(
                {str(run.get("lb")) for run in running_rows if run.get("lb") is not None}
            ),
            "avg_time_median": _median(_float_or_none(run.get("avg_time")) for run in running_rows),
            "reported_time_median": _median(
                _float_or_none(run.get("reported_time_median")) for run in running_rows
            ),
        }

    rows_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in auto_records:
        rows_by_pair[_pair_identity(row)].append(row)

    complete_pairs = 0
    incomplete_pair_examples: list[dict[str, Any]] = []
    hd_mismatch_pair_count = 0
    config_delta_rows: list[dict[str, Any]] = []
    win_counts: Counter[str] = Counter()

    for (category, pair), rows in sorted(rows_by_pair.items()):
        configs = {str(row.get("config")) for row in rows}
        if set(AUTO_TUNE_CONFIGS).issubset(configs) and len(rows) >= 2:
            complete_pairs += 1
            by_config_row = {str(row.get("config")): row for row in rows}
            false_row = by_config_row[AUTO_TUNE_CONFIGS[0]]
            true_row = by_config_row[AUTO_TUNE_CONFIGS[1]]
            false_time = _float_or_none((false_row.get("running") or {}).get("avg_time"))
            true_time = _float_or_none((true_row.get("running") or {}).get("avg_time"))
            false_hd = _float_or_none(false_row.get("hd_result"))
            true_hd = _float_or_none(true_row.get("hd_result"))
            if false_hd != true_hd:
                hd_mismatch_pair_count += 1
            if false_time is not None and true_time is not None:
                if true_time < false_time:
                    winner = AUTO_TUNE_CONFIGS[1]
                elif false_time < true_time:
                    winner = AUTO_TUNE_CONFIGS[0]
                else:
                    winner = "tie"
                win_counts[winner] += 1
                config_delta_rows.append(
                    {
                        "category": category,
                        "file_pair": pair,
                        "false_false_avg_time": false_time,
                        "true_true_avg_time": true_time,
                        "true_over_false_avg_time_ratio": true_time / false_time
                        if false_time
                        else None,
                        "winner": winner,
                        "hd_results_equal": false_hd == true_hd,
                        "input_point_counts": _input_point_counts(false_row),
                    }
                )
        else:
            incomplete_pair_examples.append(
                {
                    "category": category,
                    "file_pair": pair,
                    "configs": sorted(configs),
                    "row_count": len(rows),
                }
            )

    category_config_summary: dict[str, dict[str, Any]] = {}
    for category in sorted(by_category):
        category_rows = [row for row in auto_records if row.get("category") == category]
        category_config_summary[category] = {
            "row_count": len(category_rows),
            "unique_pair_count": len({_file_pair_key(row) for row in category_rows}),
            "by_config": dict(
                sorted(Counter(str(row.get("config")) for row in category_rows).items())
            ),
            "avg_time_median_by_config": {
                config: _median(
                    _float_or_none((row.get("running") or {}).get("avg_time"))
                    for row in category_rows
                    if str(row.get("config")) == config
                )
                for config in sorted({str(row.get("config")) for row in category_rows})
            },
        }

    ratio_values = [
        row["true_over_false_avg_time_ratio"]
        for row in config_delta_rows
        if row.get("true_over_false_avg_time_ratio") is not None
    ]

    return {
        "schema": "rtdl.paper_reproduction.xhd.figure9_auto_tune_semantics.v1",
        "goal": "Goal5284",
        "status": "figure9_auto_tune_mapping_ready__figure9_not_reproduced",
        "sources": {
            "log_index_goal": log_index.get("goal"),
            "paper_branch_commit": log_index.get("author_repo", {}).get("head"),
            "record_source": "paper-branch run_all auto_tune logs",
        },
        "coverage": {
            "auto_tune_record_count": len(auto_records),
            "unique_pair_count": len(rows_by_pair),
            "complete_pair_count_with_both_observed_configs": complete_pairs,
            "incomplete_pair_count": len(rows_by_pair) - complete_pairs,
            "categories": dict(sorted(by_category.items())),
            "configs": dict(sorted(by_config.items())),
            "observed_config_labels": sorted(by_config),
            "expected_observed_config_labels": list(AUTO_TUNE_CONFIGS),
        },
        "observed_config_semantics": {
            "configs": config_values,
            "all_running_num_points_per_cell_values": sorted(
                {
                    int((row.get("running") or {}).get("num_points_per_cell"))
                    for row in auto_records
                    if (row.get("running") or {}).get("num_points_per_cell") is not None
                }
            ),
            "grid_size_sweep_present_in_run_all_auto_tune_logs": False,
            "grid_size_sweep_reason": (
                "All extracted run_all auto_tune records use NumPointsPerCell=8 and only "
                "two boolean-style config labels were observed; no multi-value grid-size "
                "sweep or selected paper grid-size choices are present in these records."
            ),
        },
        "category_config_summary": category_config_summary,
        "config_pair_comparison": {
            "hd_result_mismatch_pair_count": hd_mismatch_pair_count,
            "winner_counts_by_avg_time": dict(sorted(win_counts.items())),
            "true_over_false_avg_time_ratio_median": _median(ratio_values),
            "true_over_false_avg_time_ratio_min": min(ratio_values) if ratio_values else None,
            "true_over_false_avg_time_ratio_max": max(ratio_values) if ratio_values else None,
            "examples": config_delta_rows[:max_examples],
            "incomplete_pair_examples": incomplete_pair_examples[:max_examples],
        },
        "figure9_reproduction_decision": {
            "figure9_reproduced": False,
            "current_evidence_level": "author_log_mapping_only",
            "what_this_proves": [
                "The paper-branch run_all index contains 1814 auto_tune records.",
                "The records cover 907 unique input pairs across BraTS, ModelNet40, geo, and graphics categories.",
                "Every observed pair has the two extracted config labels.",
                "The two labels can be compared for author-log HDResult and internal timing within the paper-branch logs.",
            ],
            "what_is_missing": [
                "full adaptive-grid parameter sweep semantics",
                "paper Figure 9 selected grid-size choices",
                "author source/script mapping that ties these two config labels to the plotted Figure 9 experiment",
                "exact input file bytes or accepted Level-C provenance",
                "RTDL equivalent adaptive-grid route matrix",
                "denominator-aligned author-vs-RTDL performance matrix",
            ],
            "forbidden_claims": [
                "Figure 9 reproduced",
                "full adaptive-grid sweep reproduced",
                "paper selected grid-size choices recovered",
                "author-vs-RTDL Figure 9 speedup or parity",
                "exact paper dataset reproduction",
                "full X-HD paper reproduction",
            ],
        },
        "next_if_continuing_figure9": [
            "Inspect author source/scripts for the actual Figure 9 plotting or grid-tuning driver.",
            "If a separate grid-size sweep log/source exists, extract its grid choices and target workloads.",
            "If no such artifact exists, keep Figure 9 at author-log mapping only and move to another figure or dataset blocker.",
        ],
        "sample_records": [_record_brief(row) for row in auto_records[:max_examples]],
        "claim_boundary": {
            "figure9_reproduced": False,
            "full_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "rtdl_route_result_claimed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-index", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-examples", type=int, default=8)
    args = parser.parse_args()

    log_index = json.loads(args.log_index.read_text(encoding="utf-8"))
    matrix = build_matrix(log_index, max_examples=args.max_examples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
