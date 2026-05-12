#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "docs" / "reports" / "goal1756_embree_same_surface_wall_clock_2026-05-12.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1756_embree_same_surface_wall_clock_2026-05-12.md"


def _cmd(app: str, *args: str, timeout_sec: int = 1800) -> dict[str, Any]:
    return {
        "app": app,
        "engine": "embree",
        "command": [sys.executable, *args],
        "timeout_sec": timeout_sec,
    }


COMMANDS: list[dict[str, Any]] = [
    _cmd("service_coverage_gaps", "examples/rtdl_service_coverage_gaps.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "gap_summary"),
    _cmd("event_hotspot_screening", "examples/rtdl_event_hotspot_screening.py", "--backend", "embree", "--copies", "20000", "--embree-summary-mode", "count_summary"),
    _cmd("facility_knn_assignment", "examples/rtdl_facility_knn_assignment.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
    _cmd("road_hazard_screening", "examples/rtdl_road_hazard_screening.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
    _cmd("segment_polygon_hitcount", "examples/rtdl_segment_polygon_hitcount.py", "--backend", "embree", "--copies", "256"),
    _cmd("segment_polygon_anyhit_rows", "examples/rtdl_segment_polygon_anyhit_rows.py", "--backend", "embree", "--copies", "256", "--output-mode", "rows", "--output-capacity", "4096"),
    _cmd("graph_visibility_edges", "examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "visibility_edges", "--copies", "20000", "--output-mode", "summary"),
    _cmd("graph_bfs", "examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "bfs", "--copies", "20000", "--output-mode", "summary"),
    _cmd("graph_triangle_count", "examples/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "triangle_count", "--copies", "20000", "--output-mode", "summary"),
    _cmd("hausdorff_distance", "examples/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--copies", "20000", "--embree-result-mode", "directed_summary"),
    _cmd("ann_candidate_search", "examples/rtdl_ann_candidate_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "rerank_summary"),
    _cmd("barnes_hut_force_app", "examples/rtdl_barnes_hut_force_app.py", "--backend", "embree", "--body-count", "200000", "--output-mode", "candidate_summary"),
    _cmd("polygon_pair_overlap_area_rows", "examples/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "embree", "--copies", "20000", "--output-mode", "summary"),
    _cmd("polygon_set_jaccard", "examples/rtdl_polygon_set_jaccard.py", "--backend", "embree", "--copies", "2000", timeout_sec=900),
    _cmd("outlier_detection", "examples/rtdl_outlier_detection_app.py", "--backend", "embree", "--copies", "20000", "--output-mode", "density_count"),
    _cmd("robot_collision_screening", "examples/rtdl_robot_collision_screening_app.py", "--backend", "embree", "--pose-count", "20000", "--obstacle-count", "1024", "--output-mode", "hit_count", timeout_sec=900),
]


def _artifact(version: str, app: str, output_root: Path = ROOT) -> Path:
    return output_root / "docs" / "reports" / f"goal1756_{version}_{app}_embree.json"


def _run_one(version: str, workdir: Path, row: dict[str, Any], output_root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    env["LD_LIBRARY_PATH"] = str(workdir / "build") + ":" + env.get("LD_LIBRARY_PATH", "")
    output = _artifact(version, row["app"], output_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    print(f"[goal1756] start {version} {row['app']}", flush=True)
    try:
        completed = subprocess.run(
            row["command"],
            cwd=workdir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=row["timeout_sec"],
            check=False,
        )
        elapsed = time.perf_counter() - start
        parsed: dict[str, Any] | None = None
        if completed.returncode == 0:
            try:
                parsed = json.loads(completed.stdout)
            except json.JSONDecodeError:
                parsed = None
        payload = parsed if parsed is not None else {}
        payload["_goal1756_wall_clock"] = {
            "version": version,
            "app": row["app"],
            "engine": "embree",
            "workdir": str(workdir),
            "command": row["command"],
            "elapsed_sec": elapsed,
            "returncode": completed.returncode,
            "stdout_json": parsed is not None,
            "stderr_tail": completed.stderr[-2000:],
            "stdout_tail": "" if parsed is not None else completed.stdout[-2000:],
            "timing_scope": "same app-level command wall clock including process startup, input construction, native query, and JSON serialization",
        }
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[goal1756] done {version} {row['app']} rc={completed.returncode} json={parsed is not None} elapsed={elapsed:.3f}", flush=True)
        return payload["_goal1756_wall_clock"] | {"artifact": str(output.relative_to(output_root))}
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        payload = {
            "_goal1756_wall_clock": {
                "version": version,
                "app": row["app"],
                "engine": "embree",
                "workdir": str(workdir),
                "command": row["command"],
                "elapsed_sec": elapsed,
                "returncode": None,
                "stdout_json": False,
                "timeout": True,
                "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
                "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
                "timing_scope": "timed out before producing same app-level command wall clock artifact",
            }
        }
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[goal1756] timeout {version} {row['app']} elapsed={elapsed:.3f}", flush=True)
        return payload["_goal1756_wall_clock"] | {"artifact": str(output.relative_to(output_root))}


def _read_wall(version: str, app: str, root: Path = ROOT) -> dict[str, Any] | None:
    path = _artifact(version, app, root)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    wall = payload.get("_goal1756_wall_clock")
    if isinstance(wall, dict):
        return wall | {"artifact": str(path.relative_to(root))}
    return None


def build_report(root: Path = ROOT) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for command in COMMANDS:
        app = command["app"]
        baseline = _read_wall("v1_0", app, root)
        current = _read_wall("current", app, root)
        row: dict[str, Any] = {
            "app": app,
            "engine": "embree",
            "baseline_artifact": baseline.get("artifact") if baseline else None,
            "current_artifact": current.get("artifact") if current else None,
            "baseline_elapsed_sec": baseline.get("elapsed_sec") if baseline else None,
            "current_elapsed_sec": current.get("elapsed_sec") if current else None,
            "baseline_returncode": baseline.get("returncode") if baseline else None,
            "current_returncode": current.get("returncode") if current else None,
            "baseline_stdout_json": baseline.get("stdout_json") if baseline else None,
            "current_stdout_json": current.get("stdout_json") if current else None,
            "public_claim_authorized": False,
        }
        if (
            isinstance(row["baseline_elapsed_sec"], (int, float))
            and isinstance(row["current_elapsed_sec"], (int, float))
            and row["baseline_returncode"] == 0
            and row["current_returncode"] == 0
            and row["baseline_stdout_json"] is True
            and row["current_stdout_json"] is True
            and row["current_elapsed_sec"] > 0
        ):
            row["classification"] = "same_surface_app_wall_clock_ratio"
            row["baseline_over_current_ratio"] = row["baseline_elapsed_sec"] / row["current_elapsed_sec"]
        else:
            row["classification"] = "missing_or_failed_same_surface_artifact"
            row["baseline_over_current_ratio"] = None
        rows.append(row)
    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["classification"]] = class_counts.get(row["classification"], 0) + 1
    return {
        "goal": "Goal1756",
        "date": "2026-05-12",
        "verdict": "embree_same_surface_wall_clock_column_ready_without_public_speedup_claim",
        "row_count": len(rows),
        "class_counts": class_counts,
        "rows": rows,
        "methodology_notes": [
            "Both versions run through the same app-level CLI command for each row, then the adapter normalizes the elapsed wall-clock field into one schema.",
            "The current checkout requires tests/fixtures/rayjoin/br_county_subset.cdb for the segment-polygon examples; the fixture directory was synced to the Linux run root before the repaired pass.",
            "polygon_set_jaccard uses --copies 2000 for both versions because the current generic path raised MemoryError at the earlier --copies 20000 attempt.",
            "robot_collision_screening uses --pose-count 20000 for both versions because --pose-count 200000 remained CPU-bound for more than 26 minutes on v1.0 and was not a practical complete-column workload.",
        ],
        "public_claim_authorized": False,
        "release_authorized": False,
        "boundary": (
            "This finishes the Embree column as same app-level command wall-clock evidence. "
            "It is broader than native subphase timing and includes process startup, input construction, native work, and JSON serialization. "
            "It must not be used as public speedup wording without separate review."
        ),
    }


def write_report(payload: dict[str, Any], root: Path = ROOT) -> None:
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal1756 Embree Same-Surface Wall-Clock Column",
        "",
        "## Verdict",
        "",
        f"`{payload['verdict']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- Rows: `{payload['row_count']}`",
        f"- Public claim authorized: `{payload['public_claim_authorized']}`",
        f"- Release authorized: `{payload['release_authorized']}`",
    ]
    for name, count in sorted(payload["class_counts"].items()):
        lines.append(f"- `{name}`: `{count}`")
    lines.extend(["", "## Methodology Notes", ""])
    for note in payload["methodology_notes"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Embree Column", "", "| App | Classification | v1.0 sec | Current sec | v1.0/current |", "| --- | --- | ---: | ---: | ---: |"])
    for row in payload["rows"]:
        ratio = row["baseline_over_current_ratio"]
        ratio_text = f"{ratio:.3f}x" if isinstance(ratio, float) else "n/a"
        lines.append(
            f"| `{row['app']}` | `{row['classification']}` | "
            f"{row['baseline_elapsed_sec'] if row['baseline_elapsed_sec'] is not None else 'n/a'} | "
            f"{row['current_elapsed_sec'] if row['current_elapsed_sec'] is not None else 'n/a'} | "
            f"{ratio_text} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These ratios answer the user's practical v1.0 customized-engine versus current generic-engine Embree question at the same app-command level. They do not replace Goal1750's stricter native/subphase same-contract summary and do not authorize public performance wording.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-workdir", type=Path)
    parser.add_argument("--current-workdir", type=Path)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--only-app", action="append", default=[])
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    selected = [row for row in COMMANDS if not args.only_app or row["app"] in set(args.only_app)]
    if args.run:
        if args.baseline_workdir is None or args.current_workdir is None:
            raise SystemExit("--baseline-workdir and --current-workdir are required with --run")
        for row in selected:
            for version, workdir in (("v1_0", args.baseline_workdir), ("current", args.current_workdir)):
                artifact = _artifact(version, row["app"], args.output_root)
                if args.resume and artifact.exists() and artifact.stat().st_size > 0:
                    print(f"[goal1756] skip {version} {row['app']} existing={artifact}", flush=True)
                    continue
                _run_one(version, workdir, row, args.output_root)
    payload = build_report(args.output_root)
    write_report(payload, args.output_root)
    print(json.dumps({"goal": payload["goal"], "class_counts": payload["class_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
