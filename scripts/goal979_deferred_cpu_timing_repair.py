#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_ann_candidate_app as ann_app
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app


GOAL = "Goal979 deferred CPU timing repair"
DATE = "2026-04-26"

TARGETS = {
    "hausdorff_distance": {
        "path": "docs/reports/goal835_baseline_hausdorff_distance_directed_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json",
        "timer": "hausdorff",
    },
    "ann_candidate_search": {
        "path": "docs/reports/goal835_baseline_ann_candidate_search_candidate_threshold_prepared_cpu_oracle_same_semantics_2026-04-23.json",
        "timer": "ann",
    },
    "barnes_hut_force_app": {
        "path": "docs/reports/goal835_baseline_barnes_hut_force_app_node_coverage_prepared_cpu_oracle_same_semantics_2026-04-23.json",
        "timer": "barnes_hut",
    },
}


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _median(samples: list[float]) -> float:
    return float(statistics.median(samples)) if samples else 0.0


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _time_hausdorff(copies: int, repeats: int) -> tuple[dict[str, Any], float]:
    samples: list[float] = []
    last: dict[str, Any] = {}
    for _ in range(repeats):
        raw, sec = _time(lambda: hausdorff_app.expected_tiled_hausdorff(copies=copies))
        last = {
            "radius": 0.4,
            "within_threshold": float(raw["hausdorff_distance"]) <= 0.4,
            "hausdorff_distance": raw["hausdorff_distance"],
            "point_count_a": 4 * copies,
            "point_count_b": 4 * copies,
        }
        samples.append(sec)
    return last, _median(samples)


def _time_ann(copies: int, repeats: int) -> tuple[dict[str, Any], float]:
    samples: list[float] = []
    last: dict[str, Any] = {}
    for _ in range(repeats):
        last, sec = _time(lambda: ann_app.expected_tiled_candidate_threshold(copies=copies, radius=0.2))
        samples.append(sec)
    return last, _median(samples)


def _time_barnes_hut(body_count: int, repeats: int) -> tuple[dict[str, Any], float]:
    bodies = barnes_app.make_generated_bodies(body_count)
    nodes = barnes_app.build_one_level_quadtree(bodies)
    samples: list[float] = []
    last: dict[str, Any] = {}
    for _ in range(repeats):
        last, sec = _time(lambda: barnes_app.node_coverage_oracle(
            bodies,
            nodes,
            radius=barnes_app.NODE_DISCOVERY_RADIUS,
        ))
        samples.append(sec)
    return last, _median(samples)


def _repair_artifact(path: Path, *, write: bool) -> dict[str, Any]:
    artifact = _load(path)
    scale = artifact.get("benchmark_scale", {})
    repeats = int(scale.get("iterations", artifact.get("repeated_runs", 1)))
    app = str(artifact["app"])
    timer = TARGETS[app]["timer"]

    if timer == "hausdorff":
        summary, native_query = _time_hausdorff(int(scale["copies"]), repeats)
    elif timer == "ann":
        summary, native_query = _time_ann(int(scale["copies"]), repeats)
    elif timer == "barnes_hut":
        summary, native_query = _time_barnes_hut(int(scale["body_count"]), repeats)
    else:  # pragma: no cover - guarded by TARGETS
        raise AssertionError(timer)

    phases = dict(artifact.get("phase_seconds", {}))
    old_native_query = phases.get("native_query")
    phases["native_query"] = native_query
    artifact["phase_seconds"] = phases
    artifact.setdefault("notes", []).append(
        "Goal979 repaired CPU oracle comparable timing; previous artifact used native_query=0.0."
    )
    artifact["validation"] = {
        **dict(artifact.get("validation", {})),
        "goal979_timing_repair": {
            "old_native_query": old_native_query,
            "new_native_query": native_query,
            "repeats": repeats,
            "summary_matches_existing": summary == artifact.get("summary"),
        },
    }

    if write:
        _write(path, artifact)
    return artifact


def run(*, write: bool) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for app, info in TARGETS.items():
        path = ROOT / str(info["path"])
        repaired = _repair_artifact(path, write=write)
        repair = repaired["validation"]["goal979_timing_repair"]
        rows.append(
            {
                "app": app,
                "path": str(path),
                "old_native_query": repair["old_native_query"],
                "new_native_query": repair["new_native_query"],
                "summary_matches_existing": repair["summary_matches_existing"],
                "status": "ok" if repair["new_native_query"] > 0 else "failed",
            }
        )
    return {
        "goal": GOAL,
        "date": DATE,
        "status": "ok" if all(row["status"] == "ok" and row["summary_matches_existing"] for row in rows) else "failed",
        "write": write,
        "rows": rows,
        "boundary": (
            "Goal979 repairs zero CPU oracle timing fields for deferred decision baselines. "
            "It does not collect cloud data, repair graph same-scale timing, or authorize public RTX speedup claims."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repair zero CPU oracle timing in deferred decision baselines.")
    parser.add_argument("--write", action="store_true", help="write repaired baseline artifacts")
    parser.add_argument("--output-json", default="docs/reports/goal979_deferred_cpu_timing_repair_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal979_deferred_cpu_timing_repair_2026-04-26.md")
    args = parser.parse_args(argv)

    payload = run(write=args.write)
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal979 Deferred CPU Timing Repair",
        "",
        f"Date: {DATE}",
        "",
        payload["boundary"],
        "",
        f"- status: `{payload['status']}`",
        f"- wrote baseline artifacts: `{payload['write']}`",
        "",
        "| App | Old native_query (s) | New native_query (s) | Summary Match | Status |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | {row['old_native_query']} | {row['new_native_query']:.6f} | "
            f"`{row['summary_matches_existing']}` | `{row['status']}` |"
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
