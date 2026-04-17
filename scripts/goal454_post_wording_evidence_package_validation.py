#!/usr/bin/env python3
"""Validate post-Goal-453 v0.7 DB evidence and wording package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "docs/reports/linux_correctness_db_sweep_with_postgresql_2026-04-16.log",
    "docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json",
    "docs/reports/goal450_v0_7_linux_correctness_and_performance_refresh_2026-04-16.md",
    "docs/reports/goal450_external_review_2026-04-16.md",
    "docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json",
    "docs/reports/goal451_v0_7_postgresql_baseline_index_audit_2026-04-16.md",
    "docs/reports/goal451_external_review_2026-04-16.md",
    "docs/reports/goal452_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.json",
    "docs/reports/goal452_v0_7_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.md",
    "docs/reports/goal452_external_review_2026-04-16.md",
    "docs/reports/goal453_v0_7_release_facing_performance_wording_refresh_2026-04-16.md",
    "docs/reports/goal453_external_review_2026-04-16.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal450-v0_7-linux-correctness-and-performance-refresh.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal451-v0_7-postgresql-baseline-index-audit.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal452-v0_7-rtdl-vs-best-tested-postgresql-perf-rebase.md",
    "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal453-v0_7-release-facing-performance-wording-refresh.md",
]

RELEASE_FACING_DOCS = [
    "README.md",
    "docs/features/db_workloads/README.md",
    "docs/tutorials/db_workloads.md",
    "docs/release_facing_examples.md",
    "docs/release_reports/v0_7/release_statement.md",
    "docs/release_reports/v0_7/support_matrix.md",
    "docs/release_reports/v0_7/audit_report.md",
    "docs/release_reports/v0_7/tag_preparation.md",
]

STALE_PATTERNS = [
    "Goal 443",
    "setup/index plus repeated",
    "setup/index plus query",
    "fresh setup plus 10-query total against PostgreSQL",
    "PostgreSQL temp-table setup/index",
]

REQUIRED_PATTERNS = [
    "Goal 452",
    "query-only results are mixed",
]


def _load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def _check_required_files(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    return {
        "required_count": len(REQUIRED_FILES),
        "missing_count": len(missing),
        "missing": missing,
    }


def _check_correctness_log(root: Path) -> dict[str, Any]:
    text = (root / "docs/reports/linux_correctness_db_sweep_with_postgresql_2026-04-16.log").read_text()
    return {
        "contains_ran_75_tests": "Ran 75 tests" in text,
        "contains_ok": "\nOK\n" in text or text.rstrip().endswith("\nOK"),
        "contains_failed": "FAILED" in text,
        "contains_error": "ERROR" in text,
    }


def _check_goal450(root: Path) -> dict[str, Any]:
    data = _load_json(root, "docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json")
    hash_matches = [
        backend["row_hash"] == backend["postgresql_row_hash"]
        for workload in data["workloads"].values()
        for backend in workload["backends"].values()
    ]
    return {
        "row_count": data["row_count"],
        "repeated_query_count": data["repeated_query_count"],
        "postgresql_dsn": data["postgresql_dsn"],
        "all_hash_match": all(hash_matches),
    }


def _check_goal451(root: Path) -> dict[str, Any]:
    data = _load_json(root, "docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json")
    hash_consistency = {}
    for name, workload in data["workloads"].items():
        hashes = {mode["row_hash"] for mode in workload["modes"].values()}
        hash_consistency[name] = len(hashes) == 1
    return {
        "row_count": data["row_count"],
        "repeated_query_count": data["repeated_query_count"],
        "postgresql_dsn": data["postgresql_dsn"],
        "index_modes": list(data["index_modes"]),
        "hash_consistency": hash_consistency,
        "all_hash_consistent": all(hash_consistency.values()),
    }


def _check_goal452(root: Path) -> dict[str, Any]:
    data = _load_json(root, "docs/reports/goal452_rtdl_vs_best_tested_postgresql_perf_rebase_2026-04-16.json")
    entries = [
        entry
        for workload in data["workloads"].values()
        for entry in workload["backends"].values()
    ]
    query_speedups = [entry["query_speedup_vs_best_tested_postgresql"] for entry in entries]
    total_speedups = [entry["total_speedup_vs_best_tested_postgresql"] for entry in entries]
    return {
        "row_count": data["row_count"],
        "repeated_query_count": data["repeated_query_count"],
        "postgresql_dsn": data["postgresql_dsn"],
        "all_hash_match": all(entry["hash_match"] for entry in entries),
        "has_query_loss": any(value < 1.0 for value in query_speedups),
        "all_total_wins": all(value > 1.0 for value in total_speedups),
        "min_query_speedup": min(query_speedups),
        "min_total_speedup": min(total_speedups),
    }


def _check_docs(root: Path) -> dict[str, Any]:
    stale_hits: list[dict[str, str]] = []
    required_hits = {pattern: [] for pattern in REQUIRED_PATTERNS}
    for rel in RELEASE_FACING_DOCS:
        text = (root / rel).read_text()
        for pattern in STALE_PATTERNS:
            if pattern in text:
                stale_hits.append({"file": rel, "pattern": pattern})
        for pattern in REQUIRED_PATTERNS:
            if pattern in text:
                required_hits[pattern].append(rel)
    return {
        "release_doc_count": len(RELEASE_FACING_DOCS),
        "stale_hit_count": len(stale_hits),
        "stale_hits": stale_hits,
        "required_hits": required_hits,
        "all_required_present": all(required_hits[pattern] for pattern in REQUIRED_PATTERNS),
    }


def validate(root: Path) -> dict[str, Any]:
    result = {
        "goal": 454,
        "repo_root": str(root),
        "required_files": _check_required_files(root),
        "correctness_log": _check_correctness_log(root),
        "goal450": _check_goal450(root),
        "goal451": _check_goal451(root),
        "goal452": _check_goal452(root),
        "release_docs": _check_docs(root),
        "release_authorization": False,
    }
    result["valid"] = (
        result["required_files"]["missing_count"] == 0
        and result["correctness_log"]["contains_ran_75_tests"]
        and result["correctness_log"]["contains_ok"]
        and not result["correctness_log"]["contains_failed"]
        and not result["correctness_log"]["contains_error"]
        and result["goal450"]["row_count"] == 200000
        and result["goal450"]["repeated_query_count"] == 10
        and result["goal450"]["postgresql_dsn"] == "dbname=postgres"
        and result["goal450"]["all_hash_match"]
        and result["goal451"]["row_count"] == 200000
        and result["goal451"]["repeated_query_count"] == 10
        and result["goal451"]["postgresql_dsn"] == "dbname=postgres"
        and set(result["goal451"]["index_modes"]) == {"no_index", "single_column", "composite", "covering"}
        and result["goal451"]["all_hash_consistent"]
        and result["goal452"]["row_count"] == 200000
        and result["goal452"]["repeated_query_count"] == 10
        and result["goal452"]["postgresql_dsn"] == "dbname=postgres"
        and result["goal452"]["all_hash_match"]
        and result["goal452"]["has_query_loss"]
        and result["goal452"]["all_total_wins"]
        and result["release_docs"]["stale_hit_count"] == 0
        and result["release_docs"]["all_required_present"]
        and not result["release_authorization"]
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    result = validate(root)
    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
