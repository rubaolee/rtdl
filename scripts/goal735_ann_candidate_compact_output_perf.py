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

from examples import rtdl_ann_candidate_app as app


def _time_payload(backend: str, copies: int, output_mode: str) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_app(backend, copies=copies, output_mode=output_mode)
    encoded = json.dumps(payload, sort_keys=True)
    return time.perf_counter() - start, len(encoded)


def _bench(backend: str, copies: int, output_mode: str, repeats: int) -> dict[str, object]:
    seconds: list[float] = []
    sizes: list[int] = []
    for _ in range(repeats):
        elapsed, size = _time_payload(backend, copies, output_mode)
        seconds.append(elapsed)
        sizes.append(size)
    return {
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "query_count": copies * 3,
        "candidate_count": copies * 3,
        "search_count": copies * 6,
        "repeats": repeats,
        "median_seconds": statistics.median(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "json_bytes_median": int(statistics.median(sizes)),
    }


def run_benchmark(copies_values: list[int], quality_copies_values: list[int], repeats: int) -> dict[str, object]:
    quality_copies = set(quality_copies_values)
    cases: list[dict[str, object]] = []
    for copies in copies_values:
        cpu = _bench("cpu_python_reference", copies, "rerank_summary", repeats)
        embree = _bench("embree", copies, "rerank_summary", repeats)
        cpu_seconds = float(cpu["median_seconds"])
        embree_seconds = float(embree["median_seconds"])
        embree["speedup_vs_cpu_python_reference"] = cpu_seconds / embree_seconds if embree_seconds else None
        case: dict[str, object] = {
            "copies": copies,
            "cpu_rerank_summary": cpu,
            "embree_rerank_summary": embree,
        }
        if copies in quality_copies:
            quality = _bench("embree", copies, "quality_summary", repeats)
            quality["slowdown_vs_rerank_summary"] = (
                float(quality["median_seconds"]) / embree_seconds if embree_seconds else None
            )
            case["embree_quality_summary"] = quality
        else:
            case["embree_quality_summary"] = {
                "status": "skipped",
                "reason": "Python exact full-set comparison is intentionally capped to --quality-copies.",
            }
        cases.append(case)
    return {
        "goal": 735,
        "app": "ann_candidate_search",
        "repeats": repeats,
        "quality_copies": sorted(quality_copies),
        "measurement": "run_app plus json.dumps wall-clock seconds",
        "boundary": (
            "rerank_summary measures only RTDL candidate-subset KNN reranking. "
            "quality_summary includes Python exact full-set comparison for recall and distance metrics. "
            "This is not a full ANN index or recall/latency optimizer."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--quality-copies", nargs="+", type=int, default=[256])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    report = run_benchmark(args.copies, args.quality_copies, args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
