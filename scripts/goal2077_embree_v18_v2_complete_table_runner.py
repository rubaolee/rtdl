#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2077_embree_v18_v2_complete_table_local_linux"
REPORT_JSON = ROOT / "docs" / "reports" / "goal2077_complete_v18_v2_perf_tables_2026-05-15.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal2077_complete_v18_v2_perf_tables_2026-05-15.md"


@dataclass(frozen=True)
class RowSpec:
    app: str
    scale_note: str
    v18_command: tuple[str, ...]
    v2_command: tuple[str, ...]
    v2_contract: str
    boundary: str
    timeout_sec: int = 900


def _py(*args: str) -> tuple[str, ...]:
    return (sys.executable, *args)


def _scale_value(scale: str, smoke: str, evidence: str) -> str:
    return smoke if scale == "smoke" else evidence


def build_rows(scale: str) -> tuple[RowSpec, ...]:
    fixed_copies = _scale_value(scale, "128", "2000")
    graph_copies = _scale_value(scale, "128", "2000")
    db_copies = _scale_value(scale, "128", "4000")
    polygon_copies = _scale_value(scale, "128", "5000")
    jaccard_copies = _scale_value(scale, "128", "1000")
    segment_copies = _scale_value(scale, "128", "1024")
    road_copies = _scale_value(scale, "128", "2000")
    robot_poses = _scale_value(scale, "512", "2000")
    robot_obstacles = _scale_value(scale, "128", "512")
    bodies = _scale_value(scale, "4096", "50000")
    capacity = _scale_value(scale, "2048", "16384")

    fixed_boundary = "threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation"
    return (
        RowSpec(
            "database_analytics",
            f"copies={db_copies}",
            _py("examples/v2_0/apps/analytics/rtdl_database_analytics_app.py", "--backend", "embree", "--copies", db_copies, "--output-mode", "compact_summary"),
            _py("examples/v2_0/apps/analytics/rtdl_database_analytics_app.py", "--backend", "embree", "--copies", db_copies, "--output-mode", "compact_summary"),
            "v1.8-way Embree compact-summary command reused as the current Embree CPU evidence cell",
            "filled by re-implementing/running the v1.8 Python+RTDL Embree path in the current tree; no distinct v2 CPU partner DB adapter claim",
        ),
        RowSpec(
            "graph_analytics",
            f"scenario=all copies={graph_copies}",
            _py("examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "all", "--copies", graph_copies, "--output-mode", "summary"),
            _py("examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py", "--backend", "embree", "--scenario", "all", "--copies", graph_copies, "--output-mode", "summary"),
            "v1.8-way Embree graph app command reused as the current Embree CPU evidence cell",
            "filled by measuring the complete graph app instead of leaving split graph rows or blank cells; reusable v2 graph partner primitive remains future work",
        ),
        RowSpec(
            "service_coverage_gaps",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py", "--backend", "embree", "--copies", fixed_copies, "--embree-summary-mode", "gap_summary"),
            _py("examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py", "--backend", "embree", "--copies", fixed_copies, "--embree-summary-mode", "gap_summary"),
            "Embree fixed-radius gap summary; CPU partner continuation not separately timed in this row",
            fixed_boundary,
        ),
        RowSpec(
            "event_hotspot_screening",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py", "--backend", "embree", "--copies", fixed_copies, "--embree-summary-mode", "count_summary"),
            _py("examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py", "--backend", "embree", "--copies", fixed_copies, "--embree-summary-mode", "count_summary"),
            "Embree fixed-radius count summary; CPU partner continuation not separately timed in this row",
            fixed_boundary,
        ),
        RowSpec(
            "facility_knn_assignment",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "summary"),
            _py("examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "summary"),
            "Embree coverage-threshold summary",
            fixed_boundary,
        ),
        RowSpec(
            "road_hazard_screening",
            f"copies={road_copies}",
            _py("examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py", "--backend", "embree", "--copies", road_copies, "--output-mode", "summary"),
            _py("examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py", "--backend", "embree", "--copies", road_copies, "--output-mode", "summary"),
            "Embree segment/polygon compact road-hazard summary",
            "same Embree evidence cell; v2 GPU partner speedup is an OptiX/CuPy result, not an Embree CPU claim",
        ),
        RowSpec(
            "segment_polygon_hitcount",
            f"copies={segment_copies}",
            _py("examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py", "--backend", "embree", "--copies", segment_copies),
            _py("examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py", "--backend", "embree", "--copies", segment_copies),
            "Embree hit-count output",
            "same Embree evidence cell; compact count is the desired v2 shape but this local row is CPU Embree",
        ),
        RowSpec(
            "segment_polygon_anyhit_rows",
            f"copies={segment_copies} capacity={capacity}",
            _py("examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py", "--backend", "embree", "--copies", segment_copies, "--output-mode", "rows", "--output-capacity", capacity),
            _py("examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py", "--backend", "embree", "--copies", segment_copies, "--output-mode", "rows", "--output-capacity", capacity),
            "Embree bounded witness-row materialization",
            "full row materialization remains the weak output shape; no compact-count substitution in this row",
        ),
        RowSpec(
            "polygon_pair_overlap_area_rows",
            f"copies={polygon_copies}",
            _py("examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "embree", "--copies", polygon_copies, "--output-mode", "summary", "--candidate-mode", "rt_positive"),
            _py("examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py", "--backend", "embree", "--copies", polygon_copies, "--output-mode", "summary", "--candidate-mode", "partner_bbox"),
            "CPU partner bbox candidate broadphase plus native exact summary",
            "filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay",
        ),
        RowSpec(
            "polygon_set_jaccard",
            f"copies={jaccard_copies}",
            _py("examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py", "--backend", "embree", "--copies", jaccard_copies, "--output-mode", "summary", "--candidate-mode", "rt_positive"),
            _py("examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py", "--backend", "embree", "--copies", jaccard_copies, "--output-mode", "summary", "--candidate-mode", "partner_bbox"),
            "CPU partner bbox candidate broadphase plus native Jaccard summary",
            "filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay",
        ),
        RowSpec(
            "hausdorff_distance",
            f"copies={fixed_copies}",
            _py("examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--copies", fixed_copies, "--embree-result-mode", "directed_summary"),
            _py("examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--copies", fixed_copies, "--embree-result-mode", "directed_summary"),
            "Embree directed summary",
            "exact directed summary, not a GPU partner threshold proxy in this Embree table",
        ),
        RowSpec(
            "ann_candidate_search",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/ml/rtdl_ann_candidate_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "rerank_summary"),
            _py("examples/v2_0/apps/ml/rtdl_ann_candidate_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "rerank_summary"),
            "Embree rerank summary",
            "candidate coverage/rerank summary only; not a general ANN index claim",
        ),
        RowSpec(
            "outlier_detection",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/ml/rtdl_outlier_detection_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "density_count"),
            _py("examples/v2_0/apps/ml/rtdl_outlier_detection_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "density_count"),
            "Embree density count",
            fixed_boundary,
        ),
        RowSpec(
            "dbscan_clustering",
            f"copies={fixed_copies}",
            _py("examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "core_count"),
            _py("examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py", "--backend", "embree", "--copies", fixed_copies, "--output-mode", "core_count"),
            "Embree core-count summary",
            "core-count only; full cluster expansion remains app/partner graph work",
        ),
        RowSpec(
            "robot_collision_screening",
            f"poses={robot_poses} obstacles={robot_obstacles}",
            _py("examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py", "--backend", "embree", "--pose-count", robot_poses, "--obstacle-count", robot_obstacles, "--output-mode", "hit_count"),
            _py("examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py", "--backend", "embree", "--pose-count", robot_poses, "--obstacle-count", robot_obstacles, "--output-mode", "hit_count"),
            "Embree pose hit-count summary",
            "pose flags/count only; no whole-planner acceleration claim",
        ),
        RowSpec(
            "barnes_hut_force_app",
            f"body-count={bodies}",
            _py("examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py", "--backend", "embree", "--body-count", bodies, "--output-mode", "candidate_summary"),
            _py("examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py", "--backend", "embree", "--body-count", bodies, "--output-mode", "candidate_summary"),
            "Embree node coverage candidate summary",
            "node coverage only; force-vector reduction remains outside this row",
        ),
    )


def _cpu_count() -> int:
    try:
        result = subprocess.run(["nproc"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        count = int(result.stdout.strip())
        if count > 0:
            return count
    except Exception:
        pass
    return os.cpu_count() or 1


def _git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() or "unknown"


def _run_command(command: tuple[str, ...], *, env: dict[str, str], timeout_sec: int, label: str) -> dict[str, Any]:
    start = time.perf_counter()
    print(f"[goal2077] start {label}", flush=True)
    try:
        completed = subprocess.run(
            list(command),
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            check=False,
        )
        elapsed = time.perf_counter() - start
        stdout_json = False
        parsed: dict[str, Any] | None = None
        if completed.returncode == 0:
            try:
                parsed = json.loads(completed.stdout)
                stdout_json = isinstance(parsed, dict)
            except json.JSONDecodeError:
                parsed = None
        print(f"[goal2077] done {label} rc={completed.returncode} json={stdout_json} elapsed_s={elapsed:.6f}", flush=True)
        return {
            "elapsed_sec": elapsed,
            "returncode": completed.returncode,
            "stdout_json": stdout_json,
            "stdout_tail": "" if stdout_json else completed.stdout[-2000:],
            "stderr_tail": completed.stderr[-2000:],
            "parsed_keys": sorted(parsed.keys()) if isinstance(parsed, dict) else [],
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        print(f"[goal2077] timeout {label} elapsed_s={elapsed:.6f}", flush=True)
        return {
            "elapsed_sec": elapsed,
            "returncode": None,
            "timeout": True,
            "stdout_json": False,
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
        }


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def run_row(row: RowSpec, *, env: dict[str, str], artifact_dir: Path, repeats: int) -> dict[str, Any]:
    attempts: dict[str, list[dict[str, Any]]] = {"v1_8_way_embree": [], "v2_embree_cpu_partner": []}
    for repeat in range(repeats):
        attempts["v1_8_way_embree"].append(
            _run_command(row.v18_command, env=env, timeout_sec=row.timeout_sec, label=f"{row.app} v1_8 repeat={repeat + 1}/{repeats}")
        )
        attempts["v2_embree_cpu_partner"].append(
            _run_command(row.v2_command, env=env, timeout_sec=row.timeout_sec, label=f"{row.app} v2 repeat={repeat + 1}/{repeats}")
        )
    v18_ok = [a["elapsed_sec"] for a in attempts["v1_8_way_embree"] if a.get("returncode") == 0 and a.get("stdout_json")]
    v2_ok = [a["elapsed_sec"] for a in attempts["v2_embree_cpu_partner"] if a.get("returncode") == 0 and a.get("stdout_json")]
    v18 = _median(v18_ok) if v18_ok else None
    v2 = _median(v2_ok) if v2_ok else None
    ratio = (v2 / v18) if isinstance(v18, float) and isinstance(v2, float) and v18 > 0 else None
    status = "measured" if isinstance(ratio, float) else "failed_or_timeout"
    payload = {
        "app": row.app,
        "status": status,
        "scale_note": row.scale_note,
        "v1_8_way_embree_sec": v18,
        "v2_embree_cpu_partner_sec": v2,
        "v2_over_v1_8_ratio": ratio,
        "v1_8_command": list(row.v18_command),
        "v2_command": list(row.v2_command),
        "v2_contract": row.v2_contract,
        "boundary": row.boundary,
        "attempts": attempts,
    }
    row_path = artifact_dir / "rows" / f"{row.app}.json"
    row_path.parent.mkdir(parents=True, exist_ok=True)
    row_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload | {"artifact": str(row_path.relative_to(ROOT))}


def build_summary(rows: list[dict[str, Any]], *, artifact_dir: Path, scale: str, thread_count: int) -> dict[str, Any]:
    return {
        "goal": "Goal2077",
        "status": "embree-v18-v2-complete-table-evidence",
        "scale": scale,
        "git_commit": _git_commit(),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "logical_cpu_count": thread_count,
            "thread_env": {
                "OMP_NUM_THREADS": str(thread_count),
                "TBB_NUM_THREADS": str(thread_count),
                "MKL_NUM_THREADS": str(thread_count),
                "OPENBLAS_NUM_THREADS": str(thread_count),
                "NUMEXPR_NUM_THREADS": str(thread_count),
                "RTDL_EMBREE_THREADS": str(thread_count),
            },
            "tools": {"python": sys.executable, "make": shutil.which("make"), "gcc": shutil.which("gcc")},
        },
        "row_count": len(rows),
        "all_cells_filled": all(isinstance(row.get("v1_8_way_embree_sec"), float) and isinstance(row.get("v2_embree_cpu_partner_sec"), float) for row in rows),
        "rows": rows,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "broad_all_app_speedup_claim_authorized": False,
            "embree_rows_are_local_linux_wall_clock_evidence": True,
            "optix_rows_require_pod_for_new_timing": True,
        },
        "artifact_dir": str(artifact_dir.relative_to(ROOT)),
    }


def write_report(summary: dict[str, Any]) -> None:
    REPORT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal2077 Complete v1.8/v2.0 Performance Tables",
        "",
        "Date: 2026-05-15",
        "",
        f"Status: `{summary['status']}`",
        "",
        "Goal2077 fills the Embree v1.8-way cells that had previously been left blank, especially `database_analytics` and `graph_analytics`, by measuring current-tree v1.8-style Python+RTDL+Embree commands. The v2 Embree cells are measured with the current Embree CPU evidence command for the same app row.",
        "",
        "## Boundary",
        "",
        "- This is evidence-only local Linux wall-clock timing, not public release wording.",
        "- The table has no `n/a` cells when `all_cells_filled` is true.",
        "- Some v2 Embree rows currently reuse the same public Embree app surface because the distinct CPU-partner continuation is not yet implemented for that app.",
        "- OptiX/RT rows still require fresh pod timing for new Goal2075 polygon changes.",
        "",
        "## Embree Table",
        "",
        f"- scale: `{summary['scale']}`",
        f"- all cells filled: `{summary['all_cells_filled']}`",
        "",
        "| App | Scale | v1.8-way Embree sec | v2 Embree/CPU-partner sec | v2/v1.8 | Evidence note |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in summary["rows"]:
        ratio = row["v2_over_v1_8_ratio"]
        ratio_text = f"{ratio:.3f}x" if isinstance(ratio, float) else "failed"
        v18_text = f"{row['v1_8_way_embree_sec']:.6f}" if isinstance(row["v1_8_way_embree_sec"], float) else "failed"
        v2_text = f"{row['v2_embree_cpu_partner_sec']:.6f}" if isinstance(row["v2_embree_cpu_partner_sec"], float) else "failed"
        lines.append(
            f"| `{row['app']}` | {row['scale_note']} | {v18_text} | {v2_text} | {ratio_text} | {row['boundary']} |"
        )
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run complete Embree v1.8-way/v2 CPU-partner comparison table.")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument("--scale", choices=("smoke", "evidence"), default="smoke")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--apps", default="all")
    args = parser.parse_args()
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    artifact_dir = Path(args.artifact_dir)
    if not artifact_dir.is_absolute():
        artifact_dir = ROOT / artifact_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    app_filter = None if args.apps == "all" else set(args.apps.split(","))
    selected = [row for row in build_rows(args.scale) if app_filter is None or row.app in app_filter]
    if not selected:
        raise ValueError("no apps selected")

    thread_count = _cpu_count()
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    env["LD_LIBRARY_PATH"] = str(ROOT / "build") + ":" + env.get("LD_LIBRARY_PATH", "")
    for key in ("OMP_NUM_THREADS", "TBB_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "RTDL_EMBREE_THREADS"):
        env[key] = str(thread_count)

    rows = [run_row(row, env=env, artifact_dir=artifact_dir, repeats=args.repeats) for row in selected]
    summary = build_summary(rows, artifact_dir=artifact_dir, scale=args.scale, thread_count=thread_count)
    (artifact_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary)
    print(json.dumps({"goal": "Goal2077", "all_cells_filled": summary["all_cells_filled"], "row_count": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
