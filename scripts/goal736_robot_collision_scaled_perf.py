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

from examples import rtdl_robot_collision_screening_app as app


def _time_payload(backend: str, pose_count: int, obstacle_count: int, output_mode: str) -> tuple[float, int]:
    start = time.perf_counter()
    payload = app.run_app(
        backend,
        output_mode=output_mode,
        pose_count=pose_count,
        obstacle_count=obstacle_count,
    )
    encoded = json.dumps(payload, sort_keys=True)
    return time.perf_counter() - start, len(encoded)


def _bench(backend: str, pose_count: int, obstacle_count: int, output_mode: str, repeats: int) -> dict[str, object]:
    seconds: list[float] = []
    sizes: list[int] = []
    for _ in range(repeats):
        elapsed, size = _time_payload(backend, pose_count, obstacle_count, output_mode)
        seconds.append(elapsed)
        sizes.append(size)
    return {
        "backend": backend,
        "pose_count": pose_count,
        "obstacle_count": obstacle_count,
        "edge_ray_count": pose_count * 4,
        "obstacle_triangle_count": obstacle_count * 2,
        "output_mode": output_mode,
        "repeats": repeats,
        "median_seconds": statistics.median(seconds),
        "min_seconds": min(seconds),
        "max_seconds": max(seconds),
        "json_bytes_median": int(statistics.median(sizes)),
    }


def run_benchmark(pose_counts: list[int], obstacle_count: int, repeats: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for pose_count in pose_counts:
        cpu = _bench("cpu_python_reference", pose_count, obstacle_count, "hit_count", repeats)
        embree = _bench("embree", pose_count, obstacle_count, "hit_count", repeats)
        full = _bench("embree", pose_count, obstacle_count, "full", repeats)
        cpu_seconds = float(cpu["median_seconds"])
        embree_seconds = float(embree["median_seconds"])
        embree["speedup_vs_cpu_python_reference"] = cpu_seconds / embree_seconds if embree_seconds else None
        full["slowdown_vs_hit_count"] = float(full["median_seconds"]) / embree_seconds if embree_seconds else None
        full["json_expansion_vs_hit_count"] = (
            int(full["json_bytes_median"]) / int(embree["json_bytes_median"])
            if int(embree["json_bytes_median"])
            else None
        )
        cases.append({"pose_count": pose_count, "cpu_hit_count": cpu, "embree_hit_count": embree, "embree_full": full})
    return {
        "goal": 736,
        "app": "robot_collision_screening",
        "obstacle_count": obstacle_count,
        "repeats": repeats,
        "measurement": "run_app plus json.dumps wall-clock seconds",
        "boundary": (
            "Embree hit_count uses the native any-hit row path plus compact app output. "
            "It does not yet use a prepared Embree scalar-count ABI; full output reports witness rows and JSON materialization separately."
        ),
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose-counts", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--obstacle-count", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    report = run_benchmark(args.pose_counts, args.obstacle_count, args.repeats)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
