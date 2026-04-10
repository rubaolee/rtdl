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

from examples import rtdl_event_hotspot_screening
from examples import rtdl_facility_knn_assignment
from examples import rtdl_service_coverage_gaps


APP_RUNNERS = {
    "service_coverage_gaps": rtdl_service_coverage_gaps.run_case,
    "event_hotspot_screening": rtdl_event_hotspot_screening.run_case,
    "facility_knn_assignment": rtdl_facility_knn_assignment.run_case,
}


def run_benchmark(*, apps: tuple[str, ...], backends: tuple[str, ...], copies: tuple[int, ...], iterations: int) -> dict[str, object]:
    measurements: list[dict[str, object]] = []
    for app_name in apps:
        runner = APP_RUNNERS[app_name]
        for backend in backends:
            for copy_count in copies:
                samples_ms: list[float] = []
                last_payload = None
                for _ in range(iterations):
                    start = time.perf_counter()
                    last_payload = runner(backend, copies=copy_count)
                    samples_ms.append((time.perf_counter() - start) * 1000.0)
                assert last_payload is not None
                measurements.append(
                    {
                        "app": app_name,
                        "backend": backend,
                        "copies": copy_count,
                        "iterations": iterations,
                        "median_ms": round(statistics.median(samples_ms), 3),
                        "min_ms": round(min(samples_ms), 3),
                        "max_ms": round(max(samples_ms), 3),
                        "row_count": len(last_payload["rows"]),
                    }
                )
    return {"measurements": measurements}


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 214 Bounded Linux Nearest-Neighbor Application Scaling",
        "",
        "| App | Backend | Copies | Rows | Median ms | Min ms | Max ms |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["measurements"]:
        lines.append(
            f"| {item['app']} | {item['backend']} | {item['copies']} | {item['row_count']} | {item['median_ms']} | {item['min_ms']} | {item['max_ms']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bounded performance harness for the v0.4 nearest-neighbor application examples."
    )
    parser.add_argument("--apps", nargs="+", default=tuple(APP_RUNNERS), choices=tuple(APP_RUNNERS))
    parser.add_argument("--backends", nargs="+", default=("cpu", "embree", "scipy"))
    parser.add_argument("--copies", nargs="+", type=int, default=(8, 32, 128))
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output-dir", default="build/goal214_v0_4_application_perf")
    args = parser.parse_args(argv)

    payload = run_benchmark(
        apps=tuple(args.apps),
        backends=tuple(args.backends),
        copies=tuple(args.copies),
        iterations=args.iterations,
    )
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "summary.json"
    md_path = output_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
