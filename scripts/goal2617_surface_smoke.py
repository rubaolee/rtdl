from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SmokeCase:
    name: str
    kind: str
    path: str
    args: tuple[str, ...] = ()
    timeout: int = 60
    command_type: str = "script"
    note: str = ""


@dataclass(frozen=True)
class SmokeResult:
    name: str
    kind: str
    path: str
    command: list[str]
    status: str
    returncode: int | None
    elapsed_sec: float
    stdout_tail: str
    stderr_tail: str
    note: str


def _visual_output(name: str) -> str:
    return str(ROOT / "build" / "goal2617_surface_smoke" / name)


SMOKE_CASES: tuple[SmokeCase, ...] = (
    SmokeCase("getting_started_hello_world", "tutorial", "examples/v2_0/getting_started/rtdl_hello_world.py"),
    SmokeCase(
        "getting_started_hello_world_backends",
        "tutorial",
        "examples/v2_0/getting_started/rtdl_hello_world_backends.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "getting_started_feature_cookbook",
        "tutorial",
        "examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py",
    ),
    SmokeCase("ray_triangle_any_hit", "example", "examples/v2_0/features/ray_queries/rtdl_ray_triangle_any_hit.py"),
    SmokeCase("ray_reduce_rows", "example", "examples/v2_0/features/ray_queries/rtdl_reduce_rows.py"),
    SmokeCase("ray_visibility_rows", "example", "examples/v2_0/features/ray_queries/rtdl_visibility_rows.py"),
    SmokeCase(
        "fixed_radius_neighbors",
        "example",
        "examples/v2_0/features/neighbors/rtdl_fixed_radius_neighbors.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "knn_rows",
        "example",
        "examples/v2_0/features/neighbors/rtdl_knn_rows.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "db_conjunctive_scan",
        "example",
        "examples/v2_0/features/database/rtdl_db_conjunctive_scan.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "db_grouped_count",
        "example",
        "examples/v2_0/features/database/rtdl_db_grouped_count.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "db_grouped_sum",
        "example",
        "examples/v2_0/features/database/rtdl_db_grouped_sum.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "graph_bfs",
        "example",
        "examples/v2_0/features/graph/rtdl_graph_bfs.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "graph_triangle_count",
        "example",
        "examples/v2_0/features/graph/rtdl_graph_triangle_count.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "segment_polygon_hitcount",
        "example",
        "examples/v2_0/features/spatial/rtdl_segment_polygon_hitcount.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "segment_polygon_anyhit_rows",
        "example",
        "examples/v2_0/features/spatial/rtdl_segment_polygon_anyhit_rows.py",
        ("--backend", "cpu_python_reference", "--output-mode", "segment_counts"),
    ),
    SmokeCase(
        "polygon_pair_overlap_area",
        "example",
        "examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "polygon_set_jaccard",
        "example",
        "examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "database_analytics_app",
        "app",
        "examples/v2_0/apps/analytics/rtdl_database_analytics_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "graph_analytics_app",
        "app",
        "examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "event_hotspot_app",
        "app",
        "examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "facility_knn_app",
        "app",
        "examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "road_hazard_app",
        "app",
        "examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "sales_risk_app",
        "app",
        "examples/v2_0/apps/geospatial/rtdl_sales_risk_screening.py",
        ("--backend", "cpu_python_reference", "--output-mode", "summary"),
    ),
    SmokeCase(
        "service_coverage_app",
        "app",
        "examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "ann_candidate_app",
        "app",
        "examples/v2_0/apps/ml/rtdl_ann_candidate_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "quality_summary"),
    ),
    SmokeCase(
        "dbscan_clustering_app",
        "app",
        "examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "core_count"),
    ),
    SmokeCase(
        "outlier_detection_app",
        "app",
        "examples/v2_0/apps/ml/rtdl_outlier_detection_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "density_count"),
    ),
    SmokeCase(
        "robot_collision_screening_app",
        "app",
        "examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "hit_count"),
    ),
    SmokeCase(
        "barnes_hut_force_app",
        "app",
        "examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py",
        ("--backend", "cpu_python_reference", "--output-mode", "force_summary"),
    ),
    SmokeCase(
        "continuous_frechet_app",
        "app",
        "examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py",
        ("--backend", "cpu_python_reference", "--iterations", "4", "--candidate-mode", "all_cells"),
    ),
    SmokeCase(
        "control_apps_rawkernel_cpu_fallback",
        "partner",
        "examples/v2_0/partners/rtdl_control_apps_cupy_rawkernel.py",
        ("--partner", "cpu_fallback", "--app", "all"),
    ),
    SmokeCase(
        "hausdorff_user_cpp_continuation",
        "partner",
        "examples/v2_0/partners/rtdl_hausdorff_user_cpp_continuation.py",
        ("--backend", "cpu_python_reference", "--continuation", "python"),
    ),
    SmokeCase(
        "partner_anyhit",
        "partner",
        "examples/v2_0/partners/rtdl_partner_anyhit.py",
        ("--partner", "numpy", "--backend", "embree"),
    ),
    SmokeCase(
        "barnes_hut_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
        ("--mode", "cpu_reference", "--body-count", "8"),
    ),
    SmokeCase(
        "gpu_rmq_learner",
        "learner",
        "examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py",
        ("--mode", "cpu_reference", "--value-count", "64", "--query-count", "16", "--max-width", "16"),
    ),
    SmokeCase(
        "hausdorff_distance_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
        ("--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "hausdorff_v2_function",
        "benchmark",
        "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py",
        ("--method", "openmp_cpu", "--points-a", "32", "--points-b", "32", "--warmup", "0"),
    ),
    SmokeCase(
        "hausdorff_v2_language_lab",
        "benchmark",
        "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py",
        ("--method", "openmp_cpu", "--points-a", "32", "--points-b", "32", "--warmup", "0"),
    ),
    SmokeCase(
        "hausdorff_v2_user_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py",
        (
            "--points-a",
            "32",
            "--points-b",
            "32",
            "--skip-cuda-ctypes",
            "--skip-cupy",
            "--skip-builtin-partner",
            "--warmup",
            "0",
        ),
    ),
    SmokeCase(
        "librts_spatial_index_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
        ("--mode", "cpu_reference", "--dataset", "tiny", "--box-count", "16", "--query-count", "8"),
    ),
    SmokeCase(
        "raydb_style_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
        ("--mode", "all", "--backend", "cpu_python_reference"),
    ),
    SmokeCase(
        "robot_collision_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py",
        ("--mode", "cpu_reference", "--dataset", "tiny", "--repeats", "1", "--warmup", "0"),
    ),
    SmokeCase(
        "rt_dbscan_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
        ("--mode", "cpu_reference", "--dataset", "tiny", "--include-rows"),
    ),
    SmokeCase(
        "rtnn_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py",
        ("--mode", "scope"),
    ),
    SmokeCase(
        "spatial_rayjoin_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
        ("--workload", "all", "--backend", "cpu_python_reference", "--no-rows"),
    ),
    SmokeCase(
        "triangle_counting_contract_import",
        "benchmark",
        "examples/v2_0/research_benchmarks/triangle_counting/rt_graph_contract.py",
        command_type="module_import",
        note="Contract module import smoke; this file is a library surface, not a CLI.",
    ),
    SmokeCase(
        "triangle_counting_benchmark",
        "benchmark",
        "examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
        ("--mode", "rt_graph_contract", "--fixture", "degree_oriented_two_triangles"),
    ),
    SmokeCase(
        "visual_lit_ball",
        "demo",
        "examples/visual_demo/rtdl_lit_ball_demo.py",
        ("--backend", "cpu_python_reference", "--width", "8", "--height", "8", "--triangles", "8", "--output", _visual_output("lit_ball.pgm")),
    ),
    SmokeCase(
        "visual_hidden_star",
        "demo",
        "examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--latitude-bands",
            "4",
            "--longitude-bands",
            "8",
            "--frames",
            "1",
            "--jobs",
            "1",
            "--shadow-mode",
            "analytic",
            "--output-dir",
            _visual_output("hidden_star"),
        ),
    ),
    SmokeCase(
        "visual_hidden_star_chunked_video",
        "demo",
        "examples/visual_demo/render_hidden_star_chunked_video.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--latitude-bands",
            "4",
            "--longitude-bands",
            "8",
            "--frames",
            "1",
            "--chunk-frames",
            "1",
            "--jobs",
            "1",
            "--shadow-mode",
            "analytic",
            "--output-dir",
            _visual_output("hidden_star_video"),
        ),
        timeout=90,
    ),
    SmokeCase(
        "visual_orbit_lights",
        "demo",
        "examples/visual_demo/rtdl_orbit_lights_ball_demo.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--triangles",
            "8",
            "--frames",
            "1",
            "--vertical-samples",
            "2",
            "--output-dir",
            _visual_output("orbit_lights"),
        ),
    ),
    SmokeCase(
        "visual_orbiting_star",
        "demo",
        "examples/visual_demo/rtdl_orbiting_star_ball_demo.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--latitude-bands",
            "4",
            "--longitude-bands",
            "8",
            "--frames",
            "1",
            "--jobs",
            "1",
            "--output-dir",
            _visual_output("orbiting_star"),
        ),
    ),
    SmokeCase(
        "visual_smooth_camera_orbit",
        "demo",
        "examples/visual_demo/rtdl_smooth_camera_orbit_demo.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--latitude-bands",
            "4",
            "--longitude-bands",
            "8",
            "--frames",
            "1",
            "--jobs",
            "1",
            "--output-dir",
            _visual_output("smooth_camera"),
        ),
    ),
    SmokeCase(
        "visual_spinning_ball",
        "demo",
        "examples/visual_demo/rtdl_spinning_ball_3d_demo.py",
        (
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "8",
            "--height",
            "8",
            "--latitude-bands",
            "4",
            "--longitude-bands",
            "8",
            "--frames",
            "1",
            "--output-dir",
            _visual_output("spinning_ball"),
        ),
    ),
)


def _tail(text: str, limit: int = 2200) -> str:
    return text[-limit:] if len(text) > limit else text


def _module_name(path: str) -> str:
    rel = Path(path).with_suffix("")
    return ".".join(rel.parts)


def _command(case: SmokeCase) -> list[str]:
    if case.command_type == "module_import":
        return [sys.executable, "-c", f"import {_module_name(case.path)}"]
    if case.command_type != "script":
        raise ValueError(f"unsupported command type: {case.command_type}")
    return [sys.executable, str(ROOT / case.path), *case.args]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    project_path = f"{ROOT / 'src'}:{ROOT}"
    env["PYTHONPATH"] = f"{project_path}:{existing}" if existing else project_path
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def expected_public_code_files() -> set[str]:
    files = set()
    for prefix in ("examples/v2_0", "examples/visual_demo"):
        for path in (ROOT / prefix).rglob("*.py"):
            if path.name == "__init__.py":
                continue
            files.add(path.relative_to(ROOT).as_posix())
    return files


def validate_manifest() -> list[str]:
    covered = {case.path for case in SMOKE_CASES}
    expected = expected_public_code_files()
    return sorted(expected - covered)


def run_case(case: SmokeCase, timeout_override: int | None) -> SmokeResult:
    cmd = _command(case)
    timeout = timeout_override if timeout_override is not None else case.timeout
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            cwd=ROOT,
            env=_env(),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        status = "ok" if completed.returncode == 0 else "failed"
        returncode: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        returncode = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    return SmokeResult(
        name=case.name,
        kind=case.kind,
        path=case.path,
        command=cmd,
        status=status,
        returncode=returncode,
        elapsed_sec=time.perf_counter() - started,
        stdout_tail=_tail(stdout),
        stderr_tail=_tail(stderr),
        note=case.note,
    )


def write_markdown(payload: dict[str, object], output: Path) -> None:
    results = payload["results"]
    assert isinstance(results, list)
    lines = [
        "# Goal2617 Runnable Surface Smoke Report",
        "",
        "Generated by `scripts/goal2617_surface_smoke.py`.",
        "",
        "## Summary",
        "",
        f"- Version: `{payload['version']}`",
        f"- Total cases: `{payload['total_cases']}`",
        f"- Passed: `{payload['passed']}`",
        f"- Failed: `{payload['failed']}`",
        f"- Missing manifest entries: `{len(payload['missing_manifest_entries'])}`",
        "",
        "## Cases",
        "",
        "| Name | Kind | File | Status | Seconds | Note |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for result in results:
        assert isinstance(result, dict)
        note = str(result["note"]).replace("|", "\\|") or "-"
        lines.append(
            "| "
            f"`{result['name']}` | "
            f"`{result['kind']}` | "
            f"`{result['path']}` | "
            f"`{result['status']}` | "
            f"{float(result['elapsed_sec']):.3f} | "
            f"{note} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run current public RTDL examples, demos, apps, and benchmarks.")
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=None, help="Override per-case timeout in seconds.")
    parser.add_argument("--list", action="store_true", help="List manifest cases without running them.")
    args = parser.parse_args()

    missing = validate_manifest()
    if args.list:
        for case in SMOKE_CASES:
            print(f"{case.kind}\t{case.name}\t{case.path}")
        if missing:
            print("MISSING:")
            for path in missing:
                print(path)
        return 1 if missing else 0

    results = [run_case(case, args.timeout) for case in SMOKE_CASES]
    failed = [result for result in results if result.status != "ok"]
    payload = {
        "goal": "Goal2617",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "total_cases": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "missing_manifest_entries": missing,
        "results": [asdict(result) for result in results],
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown)
    return 1 if failed or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
