#!/usr/bin/env python3
"""Build a denominator-separated performance matrix for X-HD hd_exec evidence."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Iterable


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _cases_by_name(payload: dict[str, object], *, label: str) -> dict[str, dict[str, object]]:
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError(f"{label} payload must contain a cases list")
    cases: dict[str, dict[str, object]] = {}
    for index, case in enumerate(raw_cases):
        if not isinstance(case, dict):
            raise ValueError(f"{label} case {index} is not an object")
        name = case.get("case_name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{label} case {index} has no case_name")
        if name in cases:
            raise ValueError(f"{label} has duplicate case_name {name!r}")
        cases[name] = case
    return cases


def _float_at(mapping: dict[str, object], key: str, *, context: str) -> float:
    value = mapping.get(key)
    if value is None:
        raise ValueError(f"missing {key!r} in {context}")
    return float(value)


def _nested_dict(mapping: dict[str, object], key: str, *, context: str) -> dict[str, object]:
    value = mapping.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"missing object {key!r} in {context}")
    return value


def _stats(values: list[float], *, unit: str) -> dict[str, object]:
    if not values:
        raise ValueError("cannot summarize an empty value list")
    return {
        "count": len(values),
        "unit": unit,
        "sum": float(sum(values)),
        "median": float(statistics.median(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def _ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return float(numerator / denominator)


def build_matrix(hd_exec_batch: dict[str, object], author_baseline: dict[str, object]) -> dict[str, object]:
    batch_cases = _cases_by_name(hd_exec_batch, label="hd_exec_batch")
    author_cases = _cases_by_name(author_baseline, label="author_baseline")
    batch_names = set(batch_cases)
    author_names = set(author_cases)
    if batch_names != author_names:
        missing_from_batch = sorted(author_names - batch_names)
        missing_from_author = sorted(batch_names - author_names)
        raise ValueError(
            "case_name sets differ: "
            f"missing_from_batch={missing_from_batch[:5]}, "
            f"missing_from_author={missing_from_author[:5]}"
        )

    rows: list[dict[str, object]] = []
    for case_name in sorted(batch_names):
        batch_case = batch_cases[case_name]
        author_case = author_cases[case_name]
        author_normalized = _nested_dict(author_case, "author_normalized", context=case_name)
        legacy_route = _nested_dict(author_case, "rtdl_normalized_route", context=case_name)
        author_hd = _float_at(author_normalized, "hd_result", context=f"{case_name}.author_normalized")
        rtdl_hd = _float_at(batch_case, "rtdl_hd_result", context=f"{case_name}.hd_exec_batch")
        author_abs_diff = abs(rtdl_hd - author_hd)
        rows.append(
            {
                "case_name": case_name,
                "author_hd_result": author_hd,
                "rtdl_hd_result": rtdl_hd,
                "author_abs_diff": author_abs_diff,
                "hd_exec_matched_author": bool(batch_case.get("matched_author")),
                "hd_exec_per_source_witness_exact": bool(batch_case.get("per_source_witness_exact")),
                "hd_exec_route_wall_ms": _float_at(batch_case, "running_avg_time_ms", context=case_name),
                "hd_exec_case_wall_sec": _float_at(batch_case, "case_wall_sec", context=case_name),
                "author_process_wall_sec": _float_at(
                    author_normalized, "process_wall_sec", context=f"{case_name}.author_normalized"
                ),
                "author_internal_running_avg_time_ms": _float_at(
                    author_normalized, "running_avg_time_ms", context=f"{case_name}.author_normalized"
                ),
                "legacy_goal5253_rtdl_route_wall_sec": _float_at(
                    legacy_route, "route_wall_sec", context=f"{case_name}.rtdl_normalized_route"
                ),
                "legacy_goal5253_rtdl_total_sec": _float_at(
                    legacy_route, "total_sec", context=f"{case_name}.rtdl_normalized_route"
                ),
            }
        )

    if not rows:
        raise ValueError("no matched cases")

    hd_exec_route_ms = [float(row["hd_exec_route_wall_ms"]) for row in rows]
    hd_exec_case_wall_sec = [float(row["hd_exec_case_wall_sec"]) for row in rows]
    author_process_sec = [float(row["author_process_wall_sec"]) for row in rows]
    author_avg_ms = [float(row["author_internal_running_avg_time_ms"]) for row in rows]
    legacy_route_sec = [float(row["legacy_goal5253_rtdl_route_wall_sec"]) for row in rows]
    legacy_total_sec = [float(row["legacy_goal5253_rtdl_total_sec"]) for row in rows]
    absdiff = [float(row["author_abs_diff"]) for row in rows]

    route_sum_sec = sum(hd_exec_route_ms) / 1000.0
    route_median_sec = statistics.median(hd_exec_route_ms) / 1000.0
    author_process_sum_sec = sum(author_process_sec)
    author_process_median_sec = statistics.median(author_process_sec)
    author_avg_sum_ms = sum(author_avg_ms)
    author_avg_median_ms = statistics.median(author_avg_ms)

    return {
        "schema": "rtdl.paper_reproduction.xhd.hd_exec_entrypoint_performance_matrix.v1",
        "paper_app": "x-hd-paper",
        "case_count": len(rows),
        "matched_case_count": sum(1 for row in rows if row["hd_exec_matched_author"]),
        "per_source_witness_exact_case_count": sum(1 for row in rows if row["hd_exec_per_source_witness_exact"]),
        "all_cases_matched": all(bool(row["hd_exec_matched_author"]) for row in rows),
        "all_cases_per_source_witness_exact": all(bool(row["hd_exec_per_source_witness_exact"]) for row in rows),
        "correctness": {
            "max_author_abs_diff": max(absdiff),
            "median_author_abs_diff": float(statistics.median(absdiff)),
            "sum_author_abs_diff": float(sum(absdiff)),
        },
        "timing_semantics": {
            "rtdl_hd_exec_route_wall_ms": (
                "RTDL route wall time reported through the app-owned hd_exec-compatible "
                "JSON Running.AvgTime field; not author internal AvgTime parity."
            ),
            "rtdl_hd_exec_case_wall_sec": (
                "Wall time measured by the RTDL batch bridge around one in-process "
                "entrypoint call; includes app-owned parsing/normalization/dispatch."
            ),
            "author_process_wall_sec": (
                "Wall time to invoke the author hd_exec process for one case in the "
                "Goal5253 rerun harness."
            ),
            "author_internal_running_avg_time_ms": (
                "Author hd_exec internal Running.AvgTime from the author JSON; a "
                "different denominator from RTDL route wall time."
            ),
            "legacy_goal5253_rtdl_route_wall_sec": (
                "Older RTDL batch-harness route wall time for the same exact-witness "
                "route, before the hd_exec-compatible wrapper."
            ),
            "legacy_goal5253_rtdl_total_sec": (
                "Older RTDL batch-harness total per-case time including route-adjacent "
                "app work measured by Goal5253."
            ),
        },
        "statistics": {
            "rtdl_hd_exec_route_wall_ms": _stats(hd_exec_route_ms, unit="ms"),
            "rtdl_hd_exec_route_wall_sec_derived": _stats([value / 1000.0 for value in hd_exec_route_ms], unit="sec"),
            "rtdl_hd_exec_case_wall_sec": _stats(hd_exec_case_wall_sec, unit="sec"),
            "author_process_wall_sec": _stats(author_process_sec, unit="sec"),
            "author_internal_running_avg_time_ms": _stats(author_avg_ms, unit="ms"),
            "legacy_goal5253_rtdl_route_wall_sec": _stats(legacy_route_sec, unit="sec"),
            "legacy_goal5253_rtdl_total_sec": _stats(legacy_total_sec, unit="sec"),
            "hd_exec_batch_elapsed_sec": {
                "unit": "sec",
                "value": float(hd_exec_batch.get("elapsed_sec", 0.0)),
                "semantics": "Elapsed wall time for the full RTDL hd_exec-compatible batch bridge run.",
            },
        },
        "denominator_separated_ratios": {
            "rtdl_route_sum_sec_over_author_process_wall_sum_sec": _ratio(route_sum_sec, author_process_sum_sec),
            "rtdl_case_wall_sum_sec_over_author_process_wall_sum_sec": _ratio(
                sum(hd_exec_case_wall_sec), author_process_sum_sec
            ),
            "rtdl_route_median_sec_over_author_process_wall_median_sec": _ratio(
                route_median_sec, author_process_median_sec
            ),
            "rtdl_route_sum_ms_over_author_internal_avgtime_sum_ms": _ratio(
                sum(hd_exec_route_ms), author_avg_sum_ms
            ),
            "rtdl_route_median_ms_over_author_internal_avgtime_median_ms": _ratio(
                statistics.median(hd_exec_route_ms), author_avg_median_ms
            ),
            "legacy_goal5253_route_sum_sec_over_author_process_wall_sum_sec": _ratio(
                sum(legacy_route_sec), author_process_sum_sec
            ),
            "legacy_goal5253_total_sum_sec_over_author_process_wall_sum_sec": _ratio(
                sum(legacy_total_sec), author_process_sum_sec
            ),
            "hd_exec_route_sum_sec_over_legacy_goal5253_route_sum_sec": _ratio(
                route_sum_sec, sum(legacy_route_sec)
            ),
            "hd_exec_case_wall_sum_sec_over_legacy_goal5253_total_sum_sec": _ratio(
                sum(hd_exec_case_wall_sec), sum(legacy_total_sec)
            ),
        },
        "claim_boundary": {
            "performance_parity_claimed": False,
            "speedup_claimed": False,
            "author_internal_avgtime_comparable_without_phase_review": False,
            "exact_paper_dataset_identity_proved": False,
            "full_xhd_paper_reproduction_claimed": False,
            "all_paper_figures_reproduced": False,
        },
        "allowed_interpretation": (
            "This matrix separates denominators for the public ModelNet40 all-400 "
            "author rerun contract. It may report ratios only with denominator labels; "
            "it does not claim author performance parity or exact paper byte-input identity."
        ),
        "forbidden_interpretations": [
            "RTDL is faster than the author X-HD implementation.",
            "RTDL route wall time is directly comparable to author internal Running.AvgTime.",
            "This proves exact X-HD paper dataset identity.",
            "This completes full X-HD paper reproduction.",
        ],
        "cases": rows,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hd-exec-batch", required=True, type=Path)
    parser.add_argument("--author-baseline", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)

    matrix = build_matrix(_read_json(args.hd_exec_batch), _read_json(args.author_baseline))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": matrix["schema"],
                "case_count": matrix["case_count"],
                "matched_case_count": matrix["matched_case_count"],
                "all_cases_matched": matrix["all_cases_matched"],
            },
            sort_keys=True,
        )
    )
    return 0 if matrix["all_cases_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
