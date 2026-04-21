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

from examples import rtdl_event_hotspot_screening


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
        lambda: rtdl_event_hotspot_screening.run_case("embree", copies=copies),
        repeats,
    )
    summary_sec, summary_result = _median_time(
        lambda: rtdl_event_hotspot_screening.run_case(
            "embree",
            copies=copies,
            embree_summary_mode="count_summary",
        ),
        repeats,
    )
    if row_result["neighbor_count_by_event"] != summary_result["neighbor_count_by_event"]:
        raise AssertionError("event hotspot summary counts differ from row mode")
    if row_result["hotspots"] != summary_result["hotspots"]:
        raise AssertionError("event hotspot summary hotspots differ from row mode")
    return {
        "app": "event_hotspot_screening",
        "copies": copies,
        "event_count": row_result["event_count"],
        "row_mode_sec": row_sec,
        "count_summary_sec": summary_sec,
        "summary_speedup_vs_rows": row_sec / summary_sec if summary_sec else None,
        "row_count": len(row_result["rows"]),
        "summary_row_count": len(summary_result["summary_rows"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal723 event-hotspot Embree summary perf harness.")
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
        "goal": 723,
        "description": "Embree fixed-radius count summary for event hotspot screening.",
        "repeats": args.repeats,
        "results": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
