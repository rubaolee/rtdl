from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


def detect_backends() -> dict[str, bool]:
    availability = {"cpu_python_reference": True}
    probes = {
        "oracle": rt.oracle_version,
        "cpu": rt.oracle_version,
        "embree": rt.embree_version,
        "optix": rt.optix_version,
        "vulkan": rt.vulkan_version,
    }
    for name, probe in probes.items():
        try:
            probe()
        except Exception:
            availability[name] = False
        else:
            availability[name] = True
    return availability


def python_command() -> list[str]:
    return [sys.executable]


def build_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"src{os.pathsep}."
    return env


def output_dir(name: str) -> str:
    return str(ROOT / "build" / "goal410" / name)


def output_file(name: str, filename: str) -> str:
    return str(ROOT / "build" / "goal410" / name / filename)


def case(
    name: str,
    category: str,
    args: list[str],
    requires: tuple[str, ...] = (),
    linux_only: bool = False,
    python_modules: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "name": name,
        "category": category,
        "args": args,
        "requires": requires,
        "linux_only": linux_only,
        "python_modules": python_modules,
    }


def public_cases() -> list[dict[str, object]]:
    return [
        case("hello_world", "tutorial", ["examples/rtdl_hello_world.py"]),
        case("hello_world_cpu_python_reference", "tutorial", ["examples/rtdl_hello_world_backends.py", "--backend", "cpu_python_reference"]),
        case("hello_world_cpu", "tutorial", ["examples/rtdl_hello_world_backends.py", "--backend", "cpu"], requires=("cpu",)),
        case("hello_world_embree", "tutorial", ["examples/rtdl_hello_world_backends.py", "--backend", "embree"], requires=("embree",)),
        case("hello_world_optix", "tutorial", ["examples/rtdl_hello_world_backends.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("hello_world_vulkan", "tutorial", ["examples/rtdl_hello_world_backends.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("feature_quickstart_cookbook", "tutorial", ["examples/rtdl_feature_quickstart_cookbook.py"]),
        case("ray_triangle_any_hit", "tutorial", ["examples/rtdl_ray_triangle_any_hit.py"]),
        case("visibility_rows", "tutorial", ["examples/rtdl_visibility_rows.py"]),
        case("reduce_rows", "tutorial", ["examples/rtdl_reduce_rows.py"]),
        case("sorting_demo", "tutorial", ["scripts/rtdl_sorting_demo.py", "--backend", "cpu_python_reference", "3", "1", "4", "1", "5", "0", "2", "5"]),
        case("segment_polygon_hitcount", "tutorial", ["examples/rtdl_segment_polygon_hitcount.py", "--backend", "cpu_python_reference", "--copies", "4"]),
        case("segment_polygon_anyhit_rows", "tutorial", ["examples/rtdl_segment_polygon_anyhit_rows.py", "--backend", "cpu_python_reference", "--copies", "4"]),
        case("polygon_pair_overlap_area_rows", "tutorial", ["examples/rtdl_polygon_pair_overlap_area_rows.py"]),
        case("polygon_set_jaccard", "tutorial", ["examples/rtdl_polygon_set_jaccard.py"]),
        case("fixed_radius_neighbors_cpu_python_reference", "tutorial", ["examples/rtdl_fixed_radius_neighbors.py", "--backend", "cpu_python_reference"]),
        case("fixed_radius_neighbors_cpu", "tutorial", ["examples/rtdl_fixed_radius_neighbors.py", "--backend", "cpu"], requires=("cpu",)),
        case("fixed_radius_neighbors_embree", "tutorial", ["examples/rtdl_fixed_radius_neighbors.py", "--backend", "embree"], requires=("embree",)),
        case("knn_rows_cpu_python_reference", "tutorial", ["examples/rtdl_knn_rows.py", "--backend", "cpu_python_reference"]),
        case("knn_rows_cpu", "tutorial", ["examples/rtdl_knn_rows.py", "--backend", "cpu"], requires=("cpu",)),
        case("knn_rows_embree", "tutorial", ["examples/rtdl_knn_rows.py", "--backend", "embree"], requires=("embree",)),
        case("hausdorff_distance_app_cpu_python_reference", "example", ["examples/rtdl_hausdorff_distance_app.py", "--backend", "cpu_python_reference"]),
        case("hausdorff_distance_app_cpu", "example", ["examples/rtdl_hausdorff_distance_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("hausdorff_distance_app_embree", "example", ["examples/rtdl_hausdorff_distance_app.py", "--backend", "embree"], requires=("embree",)),
        case("hausdorff_distance_app_optix", "example", ["examples/rtdl_hausdorff_distance_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("hausdorff_distance_app_vulkan", "example", ["examples/rtdl_hausdorff_distance_app.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("ann_candidate_app_cpu_python_reference", "example", ["examples/rtdl_ann_candidate_app.py", "--backend", "cpu_python_reference"]),
        case("ann_candidate_app_cpu", "example", ["examples/rtdl_ann_candidate_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("ann_candidate_app_embree", "example", ["examples/rtdl_ann_candidate_app.py", "--backend", "embree"], requires=("embree",)),
        case("ann_candidate_app_optix", "example", ["examples/rtdl_ann_candidate_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("ann_candidate_app_vulkan", "example", ["examples/rtdl_ann_candidate_app.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("outlier_detection_app_cpu_python_reference", "example", ["examples/rtdl_outlier_detection_app.py", "--backend", "cpu_python_reference"]),
        case("outlier_detection_app_cpu", "example", ["examples/rtdl_outlier_detection_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("outlier_detection_app_embree", "example", ["examples/rtdl_outlier_detection_app.py", "--backend", "embree"], requires=("embree",)),
        case("outlier_detection_app_optix", "example", ["examples/rtdl_outlier_detection_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("outlier_detection_app_vulkan", "example", ["examples/rtdl_outlier_detection_app.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("dbscan_clustering_app_cpu_python_reference", "example", ["examples/rtdl_dbscan_clustering_app.py", "--backend", "cpu_python_reference"]),
        case("dbscan_clustering_app_cpu", "example", ["examples/rtdl_dbscan_clustering_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("dbscan_clustering_app_embree", "example", ["examples/rtdl_dbscan_clustering_app.py", "--backend", "embree"], requires=("embree",)),
        case("dbscan_clustering_app_optix", "example", ["examples/rtdl_dbscan_clustering_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("dbscan_clustering_app_vulkan", "example", ["examples/rtdl_dbscan_clustering_app.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("robot_collision_screening_app_cpu_python_reference", "example", ["examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu_python_reference"]),
        case("robot_collision_screening_app_cpu", "example", ["examples/rtdl_robot_collision_screening_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("robot_collision_screening_app_embree", "example", ["examples/rtdl_robot_collision_screening_app.py", "--backend", "embree"], requires=("embree",)),
        case("robot_collision_screening_app_optix", "example", ["examples/rtdl_robot_collision_screening_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("barnes_hut_force_app_cpu_python_reference", "example", ["examples/rtdl_barnes_hut_force_app.py", "--backend", "cpu_python_reference"]),
        case("barnes_hut_force_app_cpu", "example", ["examples/rtdl_barnes_hut_force_app.py", "--backend", "cpu"], requires=("cpu",)),
        case("barnes_hut_force_app_embree", "example", ["examples/rtdl_barnes_hut_force_app.py", "--backend", "embree"], requires=("embree",)),
        case("barnes_hut_force_app_optix", "example", ["examples/rtdl_barnes_hut_force_app.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("barnes_hut_force_app_vulkan", "example", ["examples/rtdl_barnes_hut_force_app.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("graph_bfs_cpu_python_reference", "tutorial", ["examples/rtdl_graph_bfs.py", "--backend", "cpu_python_reference"]),
        case("graph_bfs_cpu", "tutorial", ["examples/rtdl_graph_bfs.py", "--backend", "cpu"], requires=("cpu",)),
        case("graph_bfs_embree", "tutorial", ["examples/rtdl_graph_bfs.py", "--backend", "embree"], requires=("embree",)),
        case("graph_bfs_optix", "tutorial", ["examples/rtdl_graph_bfs.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("graph_bfs_vulkan", "tutorial", ["examples/rtdl_graph_bfs.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("graph_triangle_cpu_python_reference", "tutorial", ["examples/rtdl_graph_triangle_count.py", "--backend", "cpu_python_reference"]),
        case("graph_triangle_cpu", "tutorial", ["examples/rtdl_graph_triangle_count.py", "--backend", "cpu"], requires=("cpu",)),
        case("graph_triangle_embree", "tutorial", ["examples/rtdl_graph_triangle_count.py", "--backend", "embree"], requires=("embree",)),
        case("graph_triangle_optix", "tutorial", ["examples/rtdl_graph_triangle_count.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("graph_triangle_vulkan", "tutorial", ["examples/rtdl_graph_triangle_count.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("db_conjunctive_scan_cpu_python_reference", "tutorial", ["examples/rtdl_db_conjunctive_scan.py", "--backend", "cpu_python_reference"]),
        case("db_conjunctive_scan_cpu", "tutorial", ["examples/rtdl_db_conjunctive_scan.py", "--backend", "cpu"], requires=("cpu",)),
        case("db_conjunctive_scan_embree", "tutorial", ["examples/rtdl_db_conjunctive_scan.py", "--backend", "embree"], requires=("embree",)),
        case("db_conjunctive_scan_optix", "tutorial", ["examples/rtdl_db_conjunctive_scan.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("db_conjunctive_scan_vulkan", "tutorial", ["examples/rtdl_db_conjunctive_scan.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("db_grouped_count_cpu_python_reference", "tutorial", ["examples/rtdl_db_grouped_count.py", "--backend", "cpu_python_reference"]),
        case("db_grouped_count_cpu", "tutorial", ["examples/rtdl_db_grouped_count.py", "--backend", "cpu"], requires=("cpu",)),
        case("db_grouped_count_embree", "tutorial", ["examples/rtdl_db_grouped_count.py", "--backend", "embree"], requires=("embree",)),
        case("db_grouped_count_optix", "tutorial", ["examples/rtdl_db_grouped_count.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("db_grouped_count_vulkan", "tutorial", ["examples/rtdl_db_grouped_count.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("db_grouped_sum_cpu_python_reference", "tutorial", ["examples/rtdl_db_grouped_sum.py", "--backend", "cpu_python_reference"]),
        case("db_grouped_sum_cpu", "tutorial", ["examples/rtdl_db_grouped_sum.py", "--backend", "cpu"], requires=("cpu",)),
        case("db_grouped_sum_embree", "tutorial", ["examples/rtdl_db_grouped_sum.py", "--backend", "embree"], requires=("embree",)),
        case("db_grouped_sum_optix", "tutorial", ["examples/rtdl_db_grouped_sum.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("db_grouped_sum_vulkan", "tutorial", ["examples/rtdl_db_grouped_sum.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("sales_risk_screening_cpu_python_reference", "example", ["examples/rtdl_sales_risk_screening.py", "--backend", "cpu_python_reference"]),
        case("sales_risk_screening_cpu", "example", ["examples/rtdl_sales_risk_screening.py", "--backend", "cpu"], requires=("cpu",)),
        case("sales_risk_screening_embree", "example", ["examples/rtdl_sales_risk_screening.py", "--backend", "embree"], requires=("embree",)),
        case("sales_risk_screening_optix", "example", ["examples/rtdl_sales_risk_screening.py", "--backend", "optix"], requires=("optix",), linux_only=True),
        case("sales_risk_screening_vulkan", "example", ["examples/rtdl_sales_risk_screening.py", "--backend", "vulkan"], requires=("vulkan",), linux_only=True),
        case("v0_7_db_app_demo_auto", "example", ["examples/rtdl_v0_7_db_app_demo.py", "--backend", "auto"]),
        case("v0_7_db_kernel_app_demo_auto", "example", ["examples/rtdl_v0_7_db_kernel_app_demo.py", "--backend", "auto"]),
        case("service_coverage_gaps", "example", ["examples/rtdl_service_coverage_gaps.py", "--backend", "cpu_python_reference", "--copies", "2"]),
        case("event_hotspot_screening", "example", ["examples/rtdl_event_hotspot_screening.py", "--backend", "cpu_python_reference", "--copies", "2"]),
        case("facility_knn_assignment", "example", ["examples/rtdl_facility_knn_assignment.py", "--backend", "cpu_python_reference", "--copies", "2"]),
        case("road_hazard_screening", "example", ["examples/rtdl_road_hazard_screening.py", "--backend", "cpu_python_reference"]),
        case(
            "lit_ball_demo",
            "example",
            [
                "examples/visual_demo/rtdl_lit_ball_demo.py",
                "--backend",
                "cpu_python_reference",
                "--compare-backend",
                "none",
                "--width",
                "64",
                "--height",
                "64",
                "--triangles",
                "128",
                "--output",
                output_file("lit_ball_demo", "demo.pgm"),
            ],
        ),
        case(
            "hidden_star_demo",
            "example",
            [
                "examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py",
                "--backend",
                "cpu_python_reference",
                "--compare-backend",
                "none",
                "--width",
                "48",
                "--height",
                "48",
                "--latitude-bands",
                "6",
                "--longitude-bands",
                "12",
                "--frames",
                "1",
                "--jobs",
                "1",
                "--shadow-mode",
                "rtdl_light_to_surface",
                "--output-dir",
                output_dir("hidden_star_demo"),
            ],
        ),
        case(
            "smooth_camera_demo",
            "example",
            [
                "examples/visual_demo/rtdl_smooth_camera_orbit_demo.py",
                "--backend",
                "cpu_python_reference",
                "--compare-backend",
                "none",
                "--width",
                "48",
                "--height",
                "48",
                "--latitude-bands",
                "6",
                "--longitude-bands",
                "12",
                "--frames",
                "1",
                "--jobs",
                "1",
                "--output-dir",
                output_dir("smooth_camera_demo"),
            ],
        ),
        case(
            "render_hidden_star_chunked_video",
            "example",
            [
                "examples/visual_demo/render_hidden_star_chunked_video.py",
                "--backend",
                "cpu_python_reference",
                "--compare-backend",
                "none",
                "--width",
                "48",
                "--height",
                "48",
                "--latitude-bands",
                "6",
                "--longitude-bands",
                "12",
                "--frames",
                "1",
                "--chunk-frames",
                "1",
                "--jobs",
                "1",
                "--fps",
                "12",
                "--output-dir",
                output_dir("render_hidden_star_chunked_video"),
            ],
            python_modules=("imageio", "imageio_ffmpeg"),
        ),
        case(
            "generate_only_polygon_set_jaccard_bundle",
            "example",
            [
                "scripts/rtdl_generate_only.py",
                "--workload",
                "polygon_set_jaccard",
                "--dataset",
                "authored_polygon_set_jaccard_minimal",
                "--backend",
                "cpu_python_reference",
                "--output-mode",
                "rows",
                "--artifact-shape",
                "handoff_bundle",
                "--output",
                output_dir("generated_polygon_set_jaccard_bundle"),
            ],
        ),
    ]


def should_skip(entry: dict[str, object], backend_status: dict[str, bool], system: str) -> str | None:
    if entry["linux_only"] and system != "Linux":
        return "linux_only"
    for requirement in entry["requires"]:
        if not backend_status.get(str(requirement), False):
            return f"missing_{requirement}"
    for module_name in entry["python_modules"]:
        if importlib.util.find_spec(str(module_name)) is None:
            return f"missing_python_module_{module_name}"
    return None


def run_case(entry: dict[str, object], env: dict[str, str]) -> dict[str, object]:
    command = python_command() + list(entry["args"])
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    duration = time.perf_counter() - start
    return {
        "name": entry["name"],
        "category": entry["category"],
        "command": command,
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "duration_seconds": round(duration, 6),
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the public tutorial/example command surface.")
    parser.add_argument("--machine", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    shutil.rmtree(ROOT / "build" / "goal410", ignore_errors=True)
    (ROOT / "build" / "goal410").mkdir(parents=True, exist_ok=True)

    system = platform.system()
    env = build_env()
    backend_status = detect_backends()

    results: list[dict[str, object]] = []
    for entry in public_cases():
        reason = should_skip(entry, backend_status, system)
        if reason is not None:
            results.append(
                {
                    "name": entry["name"],
                    "category": entry["category"],
                    "command": python_command() + list(entry["args"]),
                    "status": "skipped",
                    "skip_reason": reason,
                }
            )
            continue
        results.append(run_case(entry, env))

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")
    skipped = sum(1 for item in results if item["status"] == "skipped")
    payload = {
        "machine": args.machine,
        "system": system,
        "python": sys.version.split()[0],
        "backend_status": backend_status,
        "summary": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": len(results),
        },
        "results": results,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
