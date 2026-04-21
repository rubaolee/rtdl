from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_service_coverage_gaps


def _median_time(fn: Callable[[], object], repeats: int) -> tuple[float, object]:
    timings: list[float] = []
    value = None
    for _ in range(repeats):
        start = time.perf_counter()
        value = fn()
        timings.append(time.perf_counter() - start)
    return statistics.median(timings), value


def _case(copies: int, repeats: int) -> dict[str, object]:
    row_sec, row_result = _median_time(
        lambda: rtdl_service_coverage_gaps.run_case("embree", copies=copies),
        repeats,
    )
    summary_sec, summary_result = _median_time(
        lambda: rtdl_service_coverage_gaps.run_case(
            "embree",
            copies=copies,
            embree_summary_mode="gap_summary",
        ),
        repeats,
    )
    if row_result["uncovered_household_ids"] != summary_result["uncovered_household_ids"]:
        raise AssertionError("service coverage gap summary differs from row mode")
    return {
        "app": "service_coverage_gaps",
        "copies": copies,
        "household_count": row_result["household_count"],
        "clinic_count": row_result["clinic_count"],
        "row_mode_sec": row_sec,
        "gap_summary_sec": summary_sec,
        "summary_speedup_vs_rows": row_sec / summary_sec if summary_sec else None,
        "row_count": len(row_result["rows"]),
        "summary_row_count": len(summary_result["coverage_summary_rows"]),
        "uncovered_count": len(summary_result["uncovered_household_ids"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal724 service-coverage Embree gap summary perf harness.")
    parser.add_argument("--copies", type=int, nargs="+", default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    results = []
    for copies in args.copies:
        result = _case(copies, args.repeats)
        results.append(result)
        print(json.dumps(result, sort_keys=True))
    payload = {
        "goal": 724,
        "description": "Embree fixed-radius count-threshold gap summary for service coverage gaps.",
        "repeats": args.repeats,
        "results": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
