#!/usr/bin/env python3
"""Build ModelNet40 record-level coverage from an all-unique-pair summary.

This app-owned paper reproduction helper proves that the paper-log ModelNet40
records are covered by the all-unique-pair gate when duplicate records have the
same author contract. It does not rerun all records and does not add ModelNet40
or X-HD semantics to RTDL core.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_xhd_modelnet40_normalized_batch_gate import _algorithm_from_author_log_payload
from run_xhd_modelnet40_normalized_batch_gate import _modelnet_member_from_author_path


def _paper_log_algorithm(record: dict[str, object], *, paper_log_repo: Path | None) -> str | None:
    if paper_log_repo is None:
        return None
    blob = record.get("blob")
    if not isinstance(blob, str) or not blob:
        return None
    completed = subprocess.run(
        ["git", "-C", str(paper_log_repo), "cat-file", "-p", blob],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"failed to read paper-log blob {blob}: {completed.stderr}")
    return _algorithm_from_author_log_payload(json.loads(completed.stdout))


def _record_pair_key(record: dict[str, object]) -> tuple[str, str]:
    input_payload = record.get("input", {})
    if not isinstance(input_payload, dict):
        raise ValueError("record input payload is not an object")
    files = input_payload.get("files", [])
    if not isinstance(files, list) or len(files) != 2:
        raise ValueError("ModelNet40 record must contain exactly two input files")
    return (
        _modelnet_member_from_author_path(str(files[0]["path"])),
        _modelnet_member_from_author_path(str(files[1]["path"])),
    )


def _record_signature(record: dict[str, object], *, paper_log_repo: Path | None) -> tuple[object, ...]:
    input_payload = record.get("input", {})
    running = record.get("running", {})
    if not isinstance(input_payload, dict):
        raise ValueError("record input payload is not an object")
    if not isinstance(running, dict):
        running = {}
    files = input_payload.get("files", [])
    if not isinstance(files, list) or len(files) != 2:
        raise ValueError("ModelNet40 record must contain exactly two input files")
    return (
        float(record["hd_result"]),
        input_payload.get("normalize"),
        input_payload.get("translate"),
        input_payload.get("type"),
        tuple(int(file_payload["num_points"]) for file_payload in files),
        running.get("num_points_per_cell"),
        running.get("max_hit"),
    )


def _record_algorithm(record: dict[str, object], *, paper_log_repo: Path | None) -> str | None:
    return _paper_log_algorithm(record, paper_log_repo=paper_log_repo)


def _modelnet40_records(log_index: dict[str, object]) -> list[dict[str, object]]:
    records = log_index.get("run_all_records", [])
    if not isinstance(records, list):
        raise ValueError("log index does not contain run_all_records")
    selected: list[dict[str, object]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("category") != "ModelNet40":
            continue
        input_payload = record.get("input", {})
        if not isinstance(input_payload, dict):
            continue
        if input_payload.get("normalize") is not True:
            continue
        if input_payload.get("translate") != 0.0:
            continue
        selected.append(record)
    return selected


def _unique_case_index(unique_summary: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    cases = unique_summary.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("unique summary does not contain cases")
    index: dict[tuple[str, str], dict[str, object]] = {}
    for case in cases:
        if not isinstance(case, dict):
            continue
        members = case.get("members", [])
        if not isinstance(members, list) or len(members) != 2:
            continue
        key = (str(members[0]), str(members[1]))
        if key in index:
            raise ValueError(f"duplicate unique summary case for pair {key}")
        index[key] = case
    return index


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    log_index = json.loads(Path(args.log_index).read_text(encoding="utf-8"))
    unique_summary = json.loads(Path(args.unique_summary).read_text(encoding="utf-8"))
    paper_log_repo = Path(args.paper_log_repo) if args.paper_log_repo else None

    records = _modelnet40_records(log_index)
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for record in records:
        grouped.setdefault(_record_pair_key(record), []).append(record)

    unique_cases = _unique_case_index(unique_summary)
    duplicate_distribution = Counter(len(group) for group in grouped.values())
    duplicate_signature_mismatches: list[dict[str, object]] = []
    missing_unique_pairs: list[dict[str, object]] = []
    unmatched_unique_pairs: list[dict[str, object]] = []
    covered_records: list[dict[str, object]] = []
    algorithm_distribution: Counter[str] = Counter()
    pair_algorithm_set_distribution: Counter[str] = Counter()

    for key, group in sorted(grouped.items()):
        signatures = {_record_signature(record, paper_log_repo=paper_log_repo) for record in group}
        algorithms = [
            _record_algorithm(record, paper_log_repo=paper_log_repo) or "unknown"
            for record in group
        ]
        algorithm_distribution.update(algorithms)
        pair_algorithm_set_distribution.update([" + ".join(sorted(set(algorithms)))])
        if len(signatures) != 1:
            duplicate_signature_mismatches.append(
                {
                    "members": list(key),
                    "record_count": len(group),
                    "signature_count": len(signatures),
                }
            )
            continue
        unique_case = unique_cases.get(key)
        if unique_case is None:
            missing_unique_pairs.append({"members": list(key), "record_count": len(group)})
            continue
        if unique_case.get("case_matched") is not True:
            unmatched_unique_pairs.append(
                {
                    "members": list(key),
                    "record_count": len(group),
                    "case_index": unique_case.get("case_index"),
                    "case_name": unique_case.get("case_name"),
                }
            )
            continue
        signature = next(iter(signatures))
        unique_hd = float(unique_case.get("author_log", {}).get("hd_result"))  # type: ignore[union-attr]
        if abs(float(signature[0]) - unique_hd) > float(args.tolerance):
            duplicate_signature_mismatches.append(
                {
                    "members": list(key),
                    "record_count": len(group),
                    "reason": "unique summary author_log HDResult differs from record signature",
                    "record_hd_result": float(signature[0]),
                    "unique_hd_result": unique_hd,
                }
            )
            continue
        for record in group:
            covered_records.append(
                {
                    "relative_log_path": record.get("relative_log_path"),
                    "members": list(key),
                    "covered_by_unique_case_index": unique_case.get("case_index"),
                    "covered_by_unique_case_name": unique_case.get("case_name"),
                    "hd_result": float(record["hd_result"]),
                    "algorithm": _record_algorithm(record, paper_log_repo=paper_log_repo),
                }
            )

    all_records_covered = bool(
        len(covered_records) == len(records)
        and not duplicate_signature_mismatches
        and not missing_unique_pairs
        and not unmatched_unique_pairs
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.modelnet40_record_coverage.v1",
        "goal": str(args.goal_label),
        "status": "modelnet40_paper_log_record_coverage_from_unique_pairs",
        "log_index": str(Path(args.log_index)),
        "unique_summary": str(Path(args.unique_summary)),
        "paper_log_repo": None if paper_log_repo is None else str(paper_log_repo),
        "record_count": len(records),
        "unique_pair_count": len(grouped),
        "covered_record_count": len(covered_records),
        "duplicate_count_distribution": {str(key): value for key, value in sorted(duplicate_distribution.items())},
        "duplicate_signature_mismatch_count": len(duplicate_signature_mismatches),
        "missing_unique_pair_count": len(missing_unique_pairs),
        "unmatched_unique_pair_count": len(unmatched_unique_pairs),
        "algorithm_distribution": dict(sorted(algorithm_distribution.items())),
        "pair_algorithm_set_distribution": dict(sorted(pair_algorithm_set_distribution.items())),
        "all_records_covered": all_records_covered,
        "duplicate_signature_mismatches": duplicate_signature_mismatches,
        "missing_unique_pairs": missing_unique_pairs,
        "unmatched_unique_pairs": unmatched_unique_pairs,
        "covered_records_sample": covered_records[:10],
        "claim_boundary": {
            "modelnet40_all_2000_log_records_covered_by_unique_pair_equivalence": all_records_covered,
            "coverage_kind": "HDResult value coverage across paper-log records",
            "all_2000_records_individually_rerun": False,
            "algorithm_specific_performance_reproduced": False,
            "exact_paper_dataset_identity_proved": False,
            "author_vs_rtdl_ratio_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-index", required=True, type=Path)
    parser.add_argument("--unique-summary", required=True, type=Path)
    parser.add_argument("--paper-log-repo", type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--goal-label", default="Goal5230")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.summary,
        "covered=",
        summary["all_records_covered"],
        "records=",
        summary["covered_record_count"],
        "/",
        summary["record_count"],
    )
    return 0 if summary["all_records_covered"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
