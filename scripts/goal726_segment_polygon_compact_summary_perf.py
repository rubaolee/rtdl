from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

from examples import rtdl_segment_polygon_anyhit_rows as app


def _time_call(fn, *, repeats: int) -> tuple[float, list[float], dict[str, object]]:
    payload = fn()
    values: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        payload = fn()
        values.append(time.perf_counter() - start)
    return min(values), values, payload


def run(*, backend: str, copies: tuple[int, ...], repeats: int) -> dict[str, object]:
    cases = []
    for copy_count in copies:
        dataset = f"derived/br_county_subset_segment_polygon_tiled_x{copy_count}"
        rows_best, rows_values, rows_payload = _time_call(
            lambda dataset=dataset: app.run_case(backend, dataset, "rows"),
            repeats=repeats,
        )
        counts_best, counts_values, counts_payload = _time_call(
            lambda dataset=dataset: app.run_case(backend, dataset, "segment_counts"),
            repeats=repeats,
        )
        cases.append(
            {
                "copies": copy_count,
                "dataset": dataset,
                "backend": backend,
                "rows_best_sec": rows_best,
                "segment_counts_best_sec": counts_best,
                "speedup_vs_rows": rows_best / counts_best if counts_best > 0 else None,
                "rows_row_count": rows_payload["row_count"],
                "segment_counts_row_count": counts_payload["row_count"],
                "rows_summary_source": rows_payload["summary_source"],
                "segment_counts_summary_source": counts_payload["summary_source"],
                "rows_all_sec": rows_values,
                "segment_counts_all_sec": counts_values,
            }
        )
    return {
        "suite": "goal726_segment_polygon_compact_summary_perf",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "backend": backend,
        "repeats": repeats,
        "cases": cases,
        "geomean_speedup_vs_rows": statistics.geometric_mean(
            case["speedup_vs_rows"] for case in cases if case["speedup_vs_rows"]
        ),
        "boundary": (
            "Compares segment_polygon_anyhit_rows rows mode against compact "
            "segment_counts mode. Compact mode now uses the RTDL "
            "segment_polygon_hitcount primitive and does not emit pair rows."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="embree", choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"))
    parser.add_argument("--copies", nargs="+", type=int, default=(256, 1024, 4096))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run(backend=args.backend, copies=tuple(args.copies), repeats=args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "backend": payload["backend"],
        "cases": len(payload["cases"]),
        "geomean_speedup_vs_rows": payload["geomean_speedup_vs_rows"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
