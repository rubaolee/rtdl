#!/usr/bin/env python3
"""Close Goal5776 statistics from one immutable raw cohort without workers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from goal5776_evaluate_real_scale_v2_v4 import evaluate
from goal5776_recount_real_scale_v2_v4_raw import recount
from goal5776_real_scale_formal_contract import schedule, statistical_rows


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _row_core(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row["lifecycle"], row["unit_id"], row["row_id"],
        row["paired_ratio_median"], tuple(row["bootstrap_ci95"]),
        row["no_slower_pass"],
    )


def close(raw_root: Path, output_root: Path) -> Path:
    raw = raw_root.resolve()
    output = output_root.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=False)
    primary_path = evaluate(raw, output / "EVALUATION.json")
    recount_path = recount(raw, output / "INDEPENDENT_RECOUNT.json")
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    independent = json.loads(recount_path.read_text(encoding="utf-8"))
    primary_rows = [_row_core(row) for row in primary["rows"]]
    recount_rows = [_row_core(row) for row in independent["rows"]]
    if primary_rows != recount_rows:
        raise RuntimeError("Goal5776 primary and independent recount disagree")
    if (
        primary.get("worker_count") != len(schedule())
        or primary.get("independent_row_count") != len(statistical_rows())
        or independent.get("worker_count") != len(schedule())
        or independent.get("row_count") != len(statistical_rows())
    ):
        raise RuntimeError("Goal5776 result cardinality mismatch")
    pass_count = sum(bool(row["no_slower_pass"]) for row in primary["rows"])
    fail_count = len(statistical_rows()) - pass_count
    final = {
        "schema": "rtdl.goal5776.real_scale_v2_v4_final.v1",
        "measurement_complete": True,
        "worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "all_row_no_slower": fail_count == 0,
        "lifecycle_results": primary["lifecycle_results"],
        "evaluation_sha256": _sha(primary_path),
        "independent_recount_sha256": _sha(recount_path),
        "primary_and_independent_rows_exactly_match": True,
        "ratio_direction": "v2_direct_over_v4__greater_than_one_favors_v4",
        "cross_app_compensation_used": False,
        "cross_lifecycle_compensation_used": False,
        "prepared_result_replaces_cold": False,
        "fixed_speedup_target_used": False,
        "repair_retry_resume_replacement_row_drop_relabel_used": False,
        "claim_boundary": {
            "v2_v4_scoped_measurement_reported": True,
            "v3_required_or_executed": False,
            "author_performance_claimed": False,
            "hardware_rt_core_utilization_claimed": False,
            "universal_performance_claimed": False,
            "production_or_submission_ready_claimed": False,
        },
    }
    destination = output / "FINAL.json"
    destination.write_text(
        json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    print(close(args.raw_root, args.output_root))


if __name__ == "__main__":
    main()
