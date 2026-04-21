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

from examples import rtdl_barnes_hut_force_app as app


def _time_payload(backend: str, body_count: int, output_mode: str) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_app(backend, body_count=body_count, output_mode=output_mode)
    encoded = json.dumps(payload, sort_keys=True)
    return time.perf_counter() - start, len(encoded)


def _bench(backend: str, body_count: int, output_mode: str, repeats: int) -> dict[str, object]:
    seconds: list[float] = []
    sizes: list[int] = []
    for _ in range(repeats):
        elapsed, json_size = _time_payload(backend, body_count, output_mode)
        seconds.append(elapsed)
        sizes.append(json_size)
    return {
        "backend": backend,
        "body_count": body_count,
        "output_mode": output_mode,
        "repeats": repeats,
        "median_seconds": statistics.median(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "json_bytes_median": int(statistics.median(sizes)),
    }


def run_benchmark(body_counts: list[int], repeats: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for body_count in body_counts:
        cpu = _bench("cpu_python_reference", body_count, "candidate_summary", repeats)
        embree = _bench("embree", body_count, "candidate_summary", repeats)
        full = _bench("embree", body_count, "force_summary", repeats)
        cpu_seconds = float(cpu["median_seconds"])
        embree_seconds = float(embree["median_seconds"])
        embree["speedup_vs_cpu_python_reference"] = cpu_seconds / embree_seconds if embree_seconds else None
        full_seconds = float(full["median_seconds"])
        full["slowdown_vs_candidate_summary"] = full_seconds / embree_seconds if embree_seconds else None
        cases.append(
            {
                "body_count": body_count,
                "cpu_candidate_summary": cpu,
                "embree_candidate_summary": embree,
                "embree_force_summary": full,
            }
        )
    return {
        "goal": 734,
        "app": "barnes_hut_force_app",
        "repeats": repeats,
        "measurement": "run_app plus json.dumps wall-clock seconds",
        "boundary": (
            "candidate_summary measures the RTDL candidate-generation slice only. "
            "force_summary includes Python Barnes-Hut opening-rule and force reduction. "
            "This is not a fully native Barnes-Hut force engine."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body-counts", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    report = run_benchmark(args.body_counts, args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
