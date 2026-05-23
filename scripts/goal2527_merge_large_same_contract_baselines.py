from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GOAL = "goal2527_large_same_contract_performance_matrix"
CLAIM_BOUNDARY = (
    "Merged large same-contract diagnostic matrix for PostgreSQL, DuckDB, cuDF, and RTDL. "
    "Only same-row-count internal timing ratios are reported. This artifact does not authorize "
    "public speedup, whole-DBMS, authors-code, RayDB reproduction, or true-zero-copy claims."
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def row_count_matrix(external: dict[str, Any], rtdl: dict[str, Any]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    all_rows = sorted({int(item["row_count"]) for item in external["performance_matrix"] + rtdl["performance_matrix"]})
    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    for item in external["performance_matrix"] + rtdl["performance_matrix"]:
        by_key[(int(item["row_count"]), str(item["system"]))] = item
    for row_count in all_rows:
        rtdl_full = by_key.get((row_count, "rtdl_optix_partner_resident_full_contract"))
        rtdl_sum_count = by_key.get((row_count, "rtdl_optix_partner_resident_sum_count_only"))
        rtdl_three_launch = by_key.get((row_count, "rtdl_optix_partner_resident_full_contract_three_launch"))
        row: dict[str, Any] = {
            "row_count": row_count,
            "postgresql_ms": _median(by_key, row_count, "postgresql"),
            "duckdb_ms": _median(by_key, row_count, "duckdb"),
            "cudf_ms": _median(by_key, row_count, "cudf"),
            "rtdl_sum_count_only_ms": rtdl_sum_count["median_ms"] if rtdl_sum_count else None,
            "rtdl_full_contract_ms": rtdl_full["median_ms"] if rtdl_full else None,
            "rtdl_three_launch_full_contract_ms": (
                rtdl_three_launch["median_ms"] if rtdl_three_launch else None
            ),
            "full_contract_ratios_vs_rtdl": {},
            "rtdl_fused_vs_three_launch_speedup": (
                rtdl_three_launch["median_ms"] / rtdl_full["median_ms"]
                if rtdl_three_launch and rtdl_full and rtdl_full["median_ms"]
                else None
            ),
        }
        if rtdl_full and rtdl_full["median_ms"]:
            for system_name in ("postgresql", "duckdb", "cudf"):
                item = by_key.get((row_count, system_name))
                if item:
                    row["full_contract_ratios_vs_rtdl"][system_name] = item["median_ms"] / rtdl_full["median_ms"]
        matrix.append(row)
    return matrix


def _median(by_key: dict[tuple[int, str], dict[str, Any]], row_count: int, system_name: str) -> float | None:
    item = by_key.get((row_count, system_name))
    return None if item is None else float(item["median_ms"])


def merge(external: dict[str, Any], rtdl: dict[str, Any]) -> dict[str, Any]:
    merged = {
        "goal": GOAL,
        "app": "raydb_style_columnar_aggregate",
        "status": "ok",
        "row_counts": external["row_counts"],
        "group_capacity": external["group_capacity"],
        "warmup": external["warmup"],
        "repeats": external["repeats"],
        "query_contract": external["query_contract"],
        "input_contract": external["input_contract"],
        "external_artifact_goal": external["goal"],
        "rtdl_artifact_goal": rtdl["goal"],
        "all_external_results_match_expected": external.get("all_available_results_match_expected", False),
        "all_rtdl_results_match_expected": rtdl.get("all_available_results_match_expected", False),
        "performance_matrix": external["performance_matrix"] + rtdl["performance_matrix"],
        "row_count_matrix": row_count_matrix(external, rtdl),
        "claim_boundary": CLAIM_BOUNDARY,
        "performance_claim_authorized": False,
    }
    merged["all_available_results_match_expected"] = (
        merged["all_external_results_match_expected"] and merged["all_rtdl_results_match_expected"]
    )
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge Goal2527 external and RTDL artifacts.")
    parser.add_argument("--external", type=Path, required=True)
    parser.add_argument("--rtdl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = merge(load(args.external), load(args.rtdl))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" and payload["all_available_results_match_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
