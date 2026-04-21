from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_polygon_pair_overlap_area_rows as app


def _time_payload(backend: str, copies: int, output_mode: str) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_case(backend, copies=copies, output_mode=output_mode)
    encoded = json.dumps(payload, sort_keys=True)
    return time.perf_counter() - start, len(encoded)


def _bench(backend: str, copies: int, output_mode: str, repeats: int) -> dict[str, object]:
    seconds: list[float] = []
    sizes: list[int] = []
    for _ in range(repeats):
        elapsed, json_size = _time_payload(backend, copies, output_mode)
        seconds.append(elapsed)
        sizes.append(json_size)
    return {
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "left_polygon_count": copies * 2,
        "right_polygon_count": copies * 3,
        "repeats": repeats,
        "median_seconds": statistics.median(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "json_bytes_median": int(statistics.median(sizes)),
    }


def run_benchmark(backend: str, copies_values: list[int], repeats: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for copies in copies_values:
        rows = _bench(backend, copies, "rows", repeats)
        summary = _bench(backend, copies, "summary", repeats)
        rows_seconds = float(rows["median_seconds"])
        summary_seconds = float(summary["median_seconds"])
        rows_json = int(rows["json_bytes_median"])
        summary_json = int(summary["json_bytes_median"])
        summary["speedup_vs_rows"] = rows_seconds / summary_seconds if summary_seconds else None
        summary["json_reduction_vs_rows"] = rows_json / summary_json if summary_json else None
        cases.append({"copies": copies, "rows": rows, "summary": summary})
    return {
        "goal": 732,
        "app": "polygon_pair_overlap_area_rows",
        "backend": backend,
        "repeats": repeats,
        "measurement": "run_case plus json.dumps wall-clock seconds",
        "boundary": (
            "Summary mode omits full overlap rows from the JSON payload. Embree "
            "still provides native-assisted candidate discovery and CPU/Python "
            "exact grid-cell area refinement."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="embree", choices=("cpu_python_reference", "cpu", "embree"))
    parser.add_argument("--copies", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    report = run_benchmark(args.backend, args.copies, args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
