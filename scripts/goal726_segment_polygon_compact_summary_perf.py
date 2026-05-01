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


def run(*, backend: str, copies: tuple[int, ...], repeats: int, optix_mode: str = "auto") -> dict[str, object]:
    if optix_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError("optix_mode must be 'auto', 'host_indexed', or 'native'")
    cases = []
    for copy_count in copies:
        dataset = f"derived/br_county_subset_segment_polygon_tiled_x{copy_count}"
        rows_best, rows_values, rows_payload = _time_call(
            lambda dataset=dataset: app.run_case(backend, dataset, "rows", optix_mode=optix_mode),
            repeats=repeats,
        )
        counts_best, counts_values, counts_payload = _time_call(
            lambda dataset=dataset: app.run_case(backend, dataset, "segment_counts", optix_mode=optix_mode),
            repeats=repeats,
        )
        cases.append(
            {
                "copies": copy_count,
                "dataset": dataset,
                "backend": backend,
                "optix_mode": optix_mode if backend == "optix" else "not_applicable",
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
        "optix_mode": optix_mode if backend == "optix" else "not_applicable",
        "repeats": repeats,
        "cases": cases,
        "geomean_speedup_vs_rows": statistics.geometric_mean(
            case["speedup_vs_rows"] for case in cases if case["speedup_vs_rows"]
        ),
        "boundary": (
            "Compares segment_polygon_anyhit_rows rows mode against compact "
            "segment_counts mode. Compact mode now uses the RTDL "
            "segment_polygon_hitcount primitive and does not emit pair rows. "
            "When backend=optix, optix_mode selects default behavior, forced "
            "host-indexed fallback, or experimental native custom-AABB mode. "
            "This script does not authorize any RT-core claim by itself."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="embree", choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"))
    parser.add_argument("--optix-mode", default="auto", choices=("auto", "host_indexed", "native"))
    parser.add_argument("--copies", nargs="+", type=int, default=(256, 1024, 4096))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run(
        backend=args.backend,
        copies=tuple(args.copies),
        repeats=args.repeats,
        optix_mode=args.optix_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "backend": payload["backend"],
        "optix_mode": payload["optix_mode"],
        "cases": len(payload["cases"]),
        "geomean_speedup_vs_rows": payload["geomean_speedup_vs_rows"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
