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

from examples import rtdl_polygon_set_jaccard as app


def _time_case(backend: str, copies: int) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_case(backend, copies=copies)
    encoded = json.dumps(payload, sort_keys=True)
    return time.perf_counter() - start, len(encoded)


def _bench(backend: str, copies: int, repeats: int) -> dict[str, object]:
    seconds: list[float] = []
    json_sizes: list[int] = []
    for _ in range(repeats):
        elapsed, json_size = _time_case(backend, copies)
        seconds.append(elapsed)
        json_sizes.append(json_size)
    return {
        "backend": backend,
        "copies": copies,
        "left_polygon_count": copies * 2,
        "right_polygon_count": copies * 2,
        "repeats": repeats,
        "median_seconds": statistics.median(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "json_bytes_median": int(statistics.median(json_sizes)),
    }


def run_benchmark(copies_values: list[int], repeats: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for copies in copies_values:
        cpu = _bench("cpu_python_reference", copies, repeats)
        embree = _bench("embree", copies, repeats)
        cpu_seconds = float(cpu["median_seconds"])
        embree_seconds = float(embree["median_seconds"])
        embree["speedup_vs_cpu_python_reference"] = cpu_seconds / embree_seconds if embree_seconds else None
        cases.append({"copies": copies, "cpu_python_reference": cpu, "embree": embree})
    return {
        "goal": 733,
        "app": "polygon_set_jaccard",
        "repeats": repeats,
        "measurement": "run_case plus json.dumps wall-clock seconds",
        "boundary": (
            "This characterizes scalable polygon-set Jaccard fixtures. Embree "
            "uses native LSI/PIP positive candidate discovery; exact grid-cell "
            "set-area refinement remains CPU/Python-owned."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", nargs="+", type=int, default=[64, 256, 1024])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    report = run_benchmark(args.copies, args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
