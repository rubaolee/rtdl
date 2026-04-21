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

from examples import rtdl_facility_knn_assignment as app


def _timed_json_payload(backend: str, copies: int, output_mode: str) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_case(backend, copies=copies, output_mode=output_mode)
    encoded = json.dumps(payload, sort_keys=True)
    elapsed = time.perf_counter() - start
    return elapsed, len(encoded)


def _bench_mode(backend: str, copies: int, output_mode: str, repeats: int) -> dict[str, object]:
    samples: list[float] = []
    json_sizes: list[int] = []
    for _ in range(repeats):
        elapsed, json_size = _timed_json_payload(backend, copies, output_mode)
        samples.append(elapsed)
        json_sizes.append(json_size)
    return {
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "repeats": repeats,
        "customer_count": copies * 4,
        "depot_count": copies * 4,
        "median_seconds": statistics.median(samples),
        "min_seconds": min(samples),
        "max_seconds": max(samples),
        "json_bytes_median": int(statistics.median(json_sizes)),
    }


def run_benchmark(backend: str, copies_values: list[int], repeats: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for copies in copies_values:
        by_mode = {
            mode: _bench_mode(backend, copies, mode, repeats)
            for mode in ("rows", "primary_assignments", "summary")
        }
        rows_seconds = float(by_mode["rows"]["median_seconds"])
        rows_json = int(by_mode["rows"]["json_bytes_median"])
        for mode in ("primary_assignments", "summary"):
            mode_seconds = float(by_mode[mode]["median_seconds"])
            mode_json = int(by_mode[mode]["json_bytes_median"])
            by_mode[mode]["speedup_vs_rows"] = rows_seconds / mode_seconds if mode_seconds else None
            by_mode[mode]["json_reduction_vs_rows"] = rows_json / mode_json if mode_json else None
        cases.append({"copies": copies, "modes": by_mode})
    return {
        "goal": 730,
        "app": "facility_knn_assignment",
        "backend": backend,
        "repeats": repeats,
        "measurement": "run_case plus json.dumps wall-clock seconds",
        "boundary": (
            "Rows mode keeps K=3 fallback choices. Compact modes run the K=1 "
            "primary-assignment RTDL kernel and omit fallback-choice rows from "
            "the app JSON payload."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="embree", choices=("cpu_python_reference", "cpu", "embree", "scipy"))
    parser.add_argument("--copies", nargs="+", type=int, default=[1024, 4096, 16384])
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
