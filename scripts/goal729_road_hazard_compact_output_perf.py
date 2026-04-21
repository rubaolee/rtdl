from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

from examples import rtdl_road_hazard_screening as app


def _time_json_payload(fn, *, repeats: int) -> tuple[float, list[float], dict[str, object], int]:
    payload = fn()
    encoded = json.dumps(payload, sort_keys=True)
    values: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        payload = fn()
        encoded = json.dumps(payload, sort_keys=True)
        values.append(time.perf_counter() - start)
    return min(values), values, payload, len(encoded)


def run(*, backend: str, copies: tuple[int, ...], repeats: int) -> dict[str, object]:
    cases = []
    for copy_count in copies:
        rows_best, rows_values, rows_payload, rows_bytes = _time_json_payload(
            lambda copy_count=copy_count: app.run_case(backend, copies=copy_count, output_mode="rows"),
            repeats=repeats,
        )
        compact_best, compact_values, compact_payload, compact_bytes = _time_json_payload(
            lambda copy_count=copy_count: app.run_case(backend, copies=copy_count, output_mode="priority_segments"),
            repeats=repeats,
        )
        cases.append(
            {
                "copies": copy_count,
                "backend": backend,
                "rows_best_sec": rows_best,
                "priority_segments_best_sec": compact_best,
                "speedup_vs_rows": rows_best / compact_best if compact_best > 0 else None,
                "rows_json_bytes": rows_bytes,
                "priority_segments_json_bytes": compact_bytes,
                "json_size_reduction": rows_bytes / compact_bytes if compact_bytes > 0 else None,
                "row_count": rows_payload["row_count"],
                "priority_segment_count": compact_payload["priority_segment_count"],
                "rows_all_sec": rows_values,
                "priority_segments_all_sec": compact_values,
            }
        )
    return {
        "suite": "goal729_road_hazard_compact_output_perf",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "backend": backend,
        "repeats": repeats,
        "cases": cases,
        "geomean_speedup_vs_rows": statistics.geometric_mean(
            case["speedup_vs_rows"] for case in cases if case["speedup_vs_rows"]
        ),
        "geomean_json_size_reduction": statistics.geometric_mean(
            case["json_size_reduction"] for case in cases if case["json_size_reduction"]
        ),
        "boundary": (
            "Measures app payload generation plus JSON serialization. Compact "
            "road-hazard modes do not change backend traversal; they avoid "
            "returning full per-road rows when only priority road ids/counts "
            "are needed."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="embree", choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"))
    parser.add_argument("--copies", nargs="+", type=int, default=(1024, 4096, 16384))
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
        "geomean_json_size_reduction": payload["geomean_json_size_reduction"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
