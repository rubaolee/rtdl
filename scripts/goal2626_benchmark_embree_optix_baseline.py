#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2626_benchmark_embree_optix_baseline_pod"

PROMOTED_BENCHMARK_APPS = (
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
    "contact_manifold",
)


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    app_id: str
    app_name: str
    comparison_group: str
    backend: str
    command: tuple[str, ...] | None
    primary_metric_path: tuple[str, ...] = ()
    setup_commands: tuple[tuple[str, ...], ...] = ()
    json_out: Path | None = None
    unsupported_reason: str | None = None
    notes: str = ""

    @property
    def supported(self) -> bool:
        return self.command is not None


def _scale_value(scale: str, *, quick: int, standard: int, large: int) -> int:
    if scale == "quick":
        return quick
    if scale == "standard":
        return standard
    if scale == "large":
        return large
    raise ValueError(f"unknown scale: {scale}")


def _py(path: str, *args: object) -> tuple[str, ...]:
    return ("python3", path, *(str(arg) for arg in args))


def build_cases(scale: str, artifact_dir: Path) -> tuple[BenchmarkCase, ...]:
    hausdorff_copies = _scale_value(scale, quick=16, standard=4096, large=16384)
    robot_poses = _scale_value(scale, quick=128, standard=8192, large=32768)
    robot_obstacles = _scale_value(scale, quick=16, standard=1024, large=2048)
    dbscan_points = _scale_value(scale, quick=512, standard=32768, large=65536)
    barnes_bodies = _scale_value(scale, quick=256, standard=8192, large=32768)
    librts_boxes = _scale_value(scale, quick=256, standard=32768, large=262144)
    librts_queries = _scale_value(scale, quick=128, standard=8192, large=65536)
    rtnn_points = _scale_value(scale, quick=4096, standard=65536, large=262144)
    triangle_copies = _scale_value(scale, quick=16, standard=5000, large=20000)
    contact_grid = _scale_value(scale, quick=64, standard=4096, large=8192)

    app = "examples/v2_0/research_benchmarks"
    rtnn_point_file = artifact_dir / f"rtnn_uniform_{rtnn_points}.csv"
    rtnn_gen_json = artifact_dir / f"rtnn_generate_{rtnn_points}.json"
    rtnn_optix_json = artifact_dir / f"rtnn_optix_{rtnn_points}.json"

    cases: list[BenchmarkCase] = [
        BenchmarkCase(
            case_id="hausdorff_embree_threshold",
            app_id="hausdorff_xhd",
            app_name="Hausdorff / X-HD-style",
            comparison_group="hausdorff_threshold_decision",
            backend="embree",
            command=_py(
                f"{app}/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                "--backend",
                "embree",
                "--copies",
                hausdorff_copies,
                "--optix-summary-mode",
                "directed_threshold_prepared",
                "--hausdorff-threshold",
                "0.4",
            ),
            primary_metric_path=("run_phases", "query_fixed_radius_threshold_reached_count_sec"),
            notes="Same threshold-decision contract as OptiX; despite option name, the prepared threshold path supports Embree.",
        ),
        BenchmarkCase(
            case_id="hausdorff_optix_threshold",
            app_id="hausdorff_xhd",
            app_name="Hausdorff / X-HD-style",
            comparison_group="hausdorff_threshold_decision",
            backend="optix",
            command=_py(
                f"{app}/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                "--backend",
                "optix",
                "--copies",
                hausdorff_copies,
                "--optix-summary-mode",
                "directed_threshold_prepared",
                "--hausdorff-threshold",
                "0.4",
                "--require-rt-core",
            ),
            primary_metric_path=("run_phases", "query_fixed_radius_threshold_reached_count_sec"),
        ),
        BenchmarkCase(
            case_id="spatial_rayjoin_embree_generic",
            app_id="spatial_rayjoin",
            app_name="Spatial RayJoin-style",
            comparison_group="rayjoin_all_generic_summary",
            backend="embree",
            command=_py(
                f"{app}/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
                "--workload",
                "all",
                "--backend",
                "embree",
                "--no-rows",
            ),
        ),
        BenchmarkCase(
            case_id="spatial_rayjoin_optix_generic",
            app_id="spatial_rayjoin",
            app_name="Spatial RayJoin-style",
            comparison_group="rayjoin_all_generic_summary",
            backend="optix",
            command=_py(
                f"{app}/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
                "--workload",
                "all",
                "--backend",
                "optix",
                "--no-rows",
            ),
        ),
        BenchmarkCase(
            case_id="rt_dbscan_embree_grouped_stream",
            app_id="rt_dbscan",
            app_name="RT-DBSCAN-style",
            comparison_group="dbscan_grouped_stream_blocked_column_signature",
            backend="embree",
            command=None,
            unsupported_reason=(
                "The promoted app front door has no Embree grouped fixed-radius continuation mode; "
                "current comparable row is OptiX-only."
            ),
        ),
        BenchmarkCase(
            case_id="rt_dbscan_optix_grouped_stream",
            app_id="rt_dbscan",
            app_name="RT-DBSCAN-style",
            comparison_group="dbscan_grouped_stream_blocked_column_signature",
            backend="optix",
            command=_py(
                f"{app}/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
                "--mode",
                "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
                "--dataset",
                "clustered3d",
                "--point-count",
                dbscan_points,
                "--partner",
                "cupy",
                "--grouped-union-query-block-size",
                "4096",
                "--no-validation",
            ),
        ),
        BenchmarkCase(
            case_id="robot_collision_embree_prepared_buffers",
            app_id="robot_collision",
            app_name="Robot collision",
            comparison_group="prepared_collision_flags",
            backend="embree",
            command=_py(
                f"{app}/robot_collision/rtdl_robot_collision_benchmark_app.py",
                "--mode",
                "embree_prepared_buffers",
                "--dataset",
                "scaled",
                "--pose-count",
                robot_poses,
                "--obstacle-count",
                robot_obstacles,
                "--link-count",
                "2",
                "--repeats",
                "5",
                "--warmup",
                "1",
            ),
            primary_metric_path=("tail_medians", "total_run_seconds"),
        ),
        BenchmarkCase(
            case_id="robot_collision_optix_prepared_device_buffers",
            app_id="robot_collision",
            app_name="Robot collision",
            comparison_group="prepared_collision_flags",
            backend="optix",
            command=_py(
                f"{app}/robot_collision/rtdl_robot_collision_benchmark_app.py",
                "--mode",
                "optix_prepared_device_buffers",
                "--dataset",
                "scaled",
                "--pose-count",
                robot_poses,
                "--obstacle-count",
                robot_obstacles,
                "--link-count",
                "2",
                "--repeats",
                "5",
                "--warmup",
                "1",
            ),
            primary_metric_path=("tail_medians", "total_run_seconds"),
        ),
    ]

    for mode in ("count", "sum"):
        cases.extend(
            [
                BenchmarkCase(
                    case_id=f"raydb_embree_{mode}",
                    app_id="raydb_style",
                    app_name="RayDB-style grouped aggregate",
                    comparison_group=f"raydb_grouped_{mode}",
                    backend="embree",
                    command=_py(
                        f"{app}/raydb_style/rtdl_raydb_style_benchmark_app.py",
                        "--mode",
                        mode,
                        "--backend",
                        "embree",
                    ),
                    notes="This app currently exposes parity rows without internal timing, so process wall median is the fallback metric.",
                ),
                BenchmarkCase(
                    case_id=f"raydb_optix_{mode}",
                    app_id="raydb_style",
                    app_name="RayDB-style grouped aggregate",
                    comparison_group=f"raydb_grouped_{mode}",
                    backend="optix",
                    command=_py(
                        f"{app}/raydb_style/rtdl_raydb_style_benchmark_app.py",
                        "--mode",
                        mode,
                        "--backend",
                        "optix",
                    ),
                    notes="This app currently exposes parity rows without internal timing, so process wall median is the fallback metric.",
                ),
            ]
        )

    cases.extend(
        [
            BenchmarkCase(
                case_id="barnes_hut_embree_node_coverage",
                app_id="barnes_hut",
                app_name="Barnes-Hut / RT-BarnesHut-style",
                comparison_group="node_coverage_candidate_summary",
                backend="embree",
                command=_py(
                    f"{app}/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
                    "--mode",
                    "embree_rows",
                    "--body-count",
                    barnes_bodies,
                    "--skip-validation",
                ),
            ),
            BenchmarkCase(
                case_id="barnes_hut_optix_node_coverage",
                app_id="barnes_hut",
                app_name="Barnes-Hut / RT-BarnesHut-style",
                comparison_group="node_coverage_candidate_summary",
                backend="optix",
                command=_py(
                    f"{app}/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
                    "--mode",
                    "optix_node_coverage_prepared",
                    "--body-count",
                    barnes_bodies,
                    "--skip-validation",
                    "--require-rt-core",
                ),
            ),
            BenchmarkCase(
                case_id="librts_embree_aabb_index",
                app_id="librts_spatial_index",
                app_name="LibRTS-style spatial index",
                comparison_group="aabb_index_all_count_only",
                backend="embree",
                command=None,
                unsupported_reason=(
                    "AABB_INDEX_QUERY_2D is currently implemented as generic CPU reference and OptiX native paths; "
                    "there is no Embree AABB index front door."
                ),
            ),
            BenchmarkCase(
                case_id="librts_optix_aabb_index",
                app_id="librts_spatial_index",
                app_name="LibRTS-style spatial index",
                comparison_group="aabb_index_all_count_only",
                backend="optix",
                command=_py(
                    f"{app}/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
                    "--mode",
                    "optix_aabb_index",
                    "--dataset",
                    "uniform",
                    "--operation",
                    "all",
                    "--box-count",
                    librts_boxes,
                    "--query-count",
                    librts_queries,
                ),
                primary_metric_path=("elapsed_sec",),
            ),
            BenchmarkCase(
                case_id="rtnn_embree_prepared_3d_ranked_summary",
                app_id="rtnn",
                app_name="RTNN neighbor search",
                comparison_group="prepared_3d_ranked_summary",
                backend="embree",
                command=None,
                unsupported_reason=(
                    "The promoted RTNN benchmark path is a prepared 3-D OptiX fixed-radius ranked-summary row; "
                    "no same-contract Embree front door exists."
                ),
            ),
            BenchmarkCase(
                case_id="rtnn_optix_prepared_3d_ranked_summary",
                app_id="rtnn",
                app_name="RTNN neighbor search",
                comparison_group="prepared_3d_ranked_summary",
                backend="optix",
                setup_commands=(
                    _py(
                        "scripts/goal2348_rtnn_v2_2_external_runner.py",
                        "generate",
                        "--point-file",
                        rtnn_point_file,
                        "--point-count",
                        rtnn_points,
                        "--dimension",
                        "3",
                        "--distribution",
                        "uniform",
                        "--json-out",
                        rtnn_gen_json,
                    ),
                ),
                command=_py(
                    "scripts/goal2348_rtnn_v2_2_external_runner.py",
                    "run-rtdl-batched-3d-neighbors",
                    "--point-file",
                    rtnn_point_file,
                    "--radius",
                    "0.02",
                    "--k-max",
                    "50",
                    "--query-batch-size",
                    min(rtnn_points, 65536),
                    "--result-mode",
                    "ranked-summary-raw",
                    "--repeat",
                    "3",
                    "--json-out",
                    rtnn_optix_json,
                ),
                json_out=rtnn_optix_json,
                primary_metric_path=("elapsed_sec",),
            ),
            BenchmarkCase(
                case_id="triangle_counting_embree_summary",
                app_id="triangle_counting",
                app_name="Triangle counting",
                comparison_group="triangle_count_summary",
                backend="embree",
                command=_py(
                    f"{app}/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
                    "--mode",
                    "run",
                    "--backend",
                    "embree",
                    "--copies",
                    triangle_copies,
                    "--output-mode",
                    "summary",
                ),
                primary_metric_path=("section", "timing_ms", "run_backend"),
            ),
            BenchmarkCase(
                case_id="triangle_counting_optix_summary",
                app_id="triangle_counting",
                app_name="Triangle counting",
                comparison_group="triangle_count_summary",
                backend="optix",
                command=_py(
                    f"{app}/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
                    "--mode",
                    "run",
                    "--backend",
                    "optix",
                    "--copies",
                    triangle_copies,
                    "--output-mode",
                    "summary",
                    "--optix-graph-mode",
                    "native",
                ),
                primary_metric_path=("section", "timing_ms", "run_backend"),
            ),
            BenchmarkCase(
                case_id="contact_manifold_embree_native_collect_k",
                app_id="contact_manifold",
                app_name="Bounded contact witness / contact-manifold",
                comparison_group="native_collect_k_i64",
                backend="embree",
                command=_py(
                    f"{app}/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
                    "--mode",
                    "native_collect_k",
                    "--dataset",
                    "grid",
                    "--grid-count",
                    contact_grid,
                    "--witness-capacity",
                    contact_grid,
                    "--backend",
                    "embree",
                ),
                primary_metric_path=("native_collect_elapsed_sec",),
                notes="Measures the generic native COLLECT_K_BOUNDED i64 collector over Python oracle rows, not collision-specific engine logic.",
            ),
            BenchmarkCase(
                case_id="contact_manifold_optix_native_collect_k",
                app_id="contact_manifold",
                app_name="Bounded contact witness / contact-manifold",
                comparison_group="native_collect_k_i64",
                backend="optix",
                command=_py(
                    f"{app}/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
                    "--mode",
                    "native_collect_k",
                    "--dataset",
                    "grid",
                    "--grid-count",
                    contact_grid,
                    "--witness-capacity",
                    contact_grid,
                    "--backend",
                    "optix",
                ),
                primary_metric_path=("native_collect_elapsed_sec",),
                notes="Measures the generic native COLLECT_K_BOUNDED i64 collector over Python oracle rows, not collision-specific engine logic.",
            ),
        ]
    )
    return tuple(cases)


def _base_env() -> dict[str, str]:
    env = os.environ.copy()
    py_path = f"{ROOT / 'src'}:{ROOT}"
    if env.get("PYTHONPATH"):
        py_path = f"{py_path}:{env['PYTHONPATH']}"
    env["PYTHONPATH"] = py_path
    embree_lib = ROOT / "build" / "librtdl_embree.so"
    optix_lib = ROOT / "build" / "librtdl_optix.so"
    if embree_lib.exists():
        env.setdefault("RTDL_EMBREE_LIBRARY", str(embree_lib))
    if optix_lib.exists():
        env.setdefault("RTDL_OPTIX_LIBRARY", str(optix_lib))
    return env


def _run_process(
    command: tuple[str, ...],
    *,
    env: dict[str, str],
    timeout_sec: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )


def _probe_command(command: tuple[str, ...], *, env: dict[str, str], timeout_sec: int = 30) -> dict[str, object]:
    try:
        completed = _run_process(command, env=env, timeout_sec=timeout_sec)
        return {
            "command": list(command),
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"command": list(command), "error": repr(exc)}


def collect_environment_probe(env: dict[str, str]) -> dict[str, object]:
    optix_candidates = [
        Path(env.get("OPTIX_PREFIX", "")) if env.get("OPTIX_PREFIX") else None,
        Path("/opt/optix"),
        Path("/usr/local/optix"),
        Path.home() / "vendor" / "optix-dev",
        Path.home() / "vendor" / "optix",
        Path.home() / "NVIDIA-OptiX-SDK",
        Path.home() / "NVIDIA-OptiX-SDK-9.0.0-linux64-x86_64",
    ]
    optix_headers = [
        str(candidate / "include" / "optix.h")
        for candidate in optix_candidates
        if candidate is not None and (candidate / "include" / "optix.h").exists()
    ]
    return {
        "repo_root": str(ROOT),
        "git_commit": _probe_command(("git", "rev-parse", "HEAD"), env=env).get("stdout", ""),
        "git_status_short": _probe_command(("git", "status", "--short"), env=env).get("stdout", ""),
        "uname": _probe_command(("uname", "-a"), env=env).get("stdout", ""),
        "python": _probe_command(("python3", "--version"), env=env).get("stdout", ""),
        "nvidia_smi": _probe_command(
            (
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ),
            env=env,
        ),
        "nvcc": _probe_command(("nvcc", "--version"), env=env),
        "optix_headers": optix_headers,
        "native_libraries": {
            "embree": str(ROOT / "build" / "librtdl_embree.so"),
            "embree_exists": (ROOT / "build" / "librtdl_embree.so").exists(),
            "optix": str(ROOT / "build" / "librtdl_optix.so"),
            "optix_exists": (ROOT / "build" / "librtdl_optix.so").exists(),
        },
        "env_subset": {
            key: env[key]
            for key in sorted(env)
            if key
            in {
                "CUDA_HOME",
                "CUDA_PATH",
                "CUDA_PREFIX",
                "LD_LIBRARY_PATH",
                "OPTIX_PREFIX",
                "RTDL_EMBREE_LIBRARY",
                "RTDL_OPTIX_LIBRARY",
            }
        },
    }


def _extract_json_from_text(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if not stripped:
        return None
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first < 0 or last < first:
        return None
    try:
        return json.loads(stripped[first : last + 1])
    except json.JSONDecodeError:
        return None


def _get_path(payload: Any, path: tuple[str, ...]) -> Any:
    current = payload
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _metric_from_hint(payload: dict[str, Any], path: tuple[str, ...]) -> tuple[float | None, str | None]:
    if not path:
        return None, None
    value = _numeric(_get_path(payload, path))
    if value is None:
        return None, None
    source = ".".join(path)
    if source.endswith("_ms") or ".timing_ms." in f".{source}.":
        return value / 1000.0, f"{source} converted-ms-to-sec"
    return value, source


def _walk_metrics(value: Any, path: tuple[str, ...] = ()) -> list[tuple[str, float]]:
    metrics: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            metrics.extend(_walk_metrics(child, (*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if index >= 8:
                break
            metrics.extend(_walk_metrics(child, (*path, str(index))))
    else:
        number = _numeric(value)
        if number is not None:
            key = path[-1] if path else ""
            source = ".".join(path)
            if key.endswith("_sec") or key.endswith("_seconds"):
                metrics.append((source, number))
            elif key.endswith("_ms") or "timing_ms" in path:
                metrics.append((f"{source} converted-ms-to-sec", number / 1000.0))
    return metrics


def _choose_primary_metric(
    payload: dict[str, Any] | None,
    *,
    hint: tuple[str, ...],
    wall_median_sec: float,
) -> tuple[float, str, list[tuple[str, float]]]:
    if payload is None:
        return wall_median_sec, "process_wall_median_sec", []
    hinted, hinted_source = _metric_from_hint(payload, hint)
    metrics = _walk_metrics(payload)
    if hinted is not None and hinted_source is not None:
        return hinted, hinted_source, metrics
    preferred_names = (
        "elapsed_sec",
        "native_collect_elapsed_sec",
        "tail_median_total_run_seconds",
        "cpu_reference_best_sec",
        "aabb_broadphase_collect_k_best_sec",
    )
    metric_by_source = dict(metrics)
    for preferred in preferred_names:
        for source, value in metric_by_source.items():
            if source.endswith(preferred):
                return value, source, metrics
    return wall_median_sec, "process_wall_median_sec", metrics


def _tail(text: str, limit: int = 4000) -> str:
    return text[-limit:] if len(text) > limit else text


def run_case(
    case: BenchmarkCase,
    *,
    env: dict[str, str],
    timeout_sec: int,
    repeat: int,
    dry_run: bool,
) -> dict[str, Any]:
    base = {
        "case_id": case.case_id,
        "app_id": case.app_id,
        "app_name": case.app_name,
        "comparison_group": case.comparison_group,
        "backend": case.backend,
        "notes": case.notes,
    }
    if not case.supported:
        return base | {
            "status": "unsupported",
            "unsupported_reason": case.unsupported_reason,
            "command": None,
            "primary_metric_sec": None,
            "primary_metric_source": None,
        }
    assert case.command is not None
    if dry_run:
        return base | {
            "status": "dry_run",
            "setup_commands": [list(command) for command in case.setup_commands],
            "command": list(case.command),
            "json_out": str(case.json_out) if case.json_out else None,
        }

    setup_results = []
    for setup in case.setup_commands:
        completed = _run_process(setup, env=env, timeout_sec=timeout_sec)
        setup_results.append(
            {
                "command": list(setup),
                "returncode": completed.returncode,
                "stdout_tail": _tail(completed.stdout),
                "stderr_tail": _tail(completed.stderr),
            }
        )
        if completed.returncode != 0:
            return base | {
                "status": "failed",
                "stage": "setup",
                "setup_results": setup_results,
                "command": list(case.command),
                "primary_metric_sec": None,
                "primary_metric_source": None,
            }

    run_results = []
    payload: dict[str, Any] | None = None
    wall_elapsed_values = []
    for _ in range(max(1, repeat)):
        started = time.perf_counter()
        try:
            completed = _run_process(case.command, env=env, timeout_sec=timeout_sec)
            wall_elapsed = time.perf_counter() - started
        except subprocess.TimeoutExpired as exc:
            return base | {
                "status": "timeout",
                "command": list(case.command),
                "timeout_sec": timeout_sec,
                "stdout_tail": _tail(exc.stdout or ""),
                "stderr_tail": _tail(exc.stderr or ""),
                "primary_metric_sec": None,
                "primary_metric_source": None,
            }
        wall_elapsed_values.append(wall_elapsed)
        parsed = _extract_json_from_text(completed.stdout)
        if case.json_out is not None and case.json_out.exists():
            parsed = json.loads(case.json_out.read_text(encoding="utf-8"))
        if parsed is not None:
            payload = parsed
        run_results.append(
            {
                "command": list(case.command),
                "returncode": completed.returncode,
                "wall_elapsed_sec": wall_elapsed,
                "stdout_tail": _tail(completed.stdout),
                "stderr_tail": _tail(completed.stderr),
            }
        )
        if completed.returncode != 0:
            return base | {
                "status": "failed",
                "stage": "run",
                "setup_results": setup_results,
                "runs": run_results,
                "payload": parsed,
                "primary_metric_sec": None,
                "primary_metric_source": None,
            }

    wall_median_sec = statistics.median(wall_elapsed_values)
    primary_metric_sec, primary_metric_source, timing_metrics = _choose_primary_metric(
        payload,
        hint=case.primary_metric_path,
        wall_median_sec=wall_median_sec,
    )
    return base | {
        "status": "ok",
        "setup_results": setup_results,
        "runs": run_results,
        "wall_median_sec": wall_median_sec,
        "primary_metric_sec": primary_metric_sec,
        "primary_metric_source": primary_metric_source,
        "timing_metrics": timing_metrics,
        "payload": payload,
    }


def compute_ratios(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ratios = []
    groups: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        metric = row.get("primary_metric_sec")
        if not isinstance(metric, (int, float)) or metric <= 0:
            continue
        key = (str(row["app_id"]), str(row["comparison_group"]))
        groups.setdefault(key, {})[str(row["backend"])] = row
    for (app_id, comparison_group), by_backend in sorted(groups.items()):
        embree = by_backend.get("embree")
        optix = by_backend.get("optix")
        if not embree or not optix:
            continue
        embree_metric = float(embree["primary_metric_sec"])
        optix_metric = float(optix["primary_metric_sec"])
        ratios.append(
            {
                "app_id": app_id,
                "comparison_group": comparison_group,
                "embree_sec": embree_metric,
                "optix_sec": optix_metric,
                "optix_speedup_vs_embree": embree_metric / optix_metric,
                "embree_speedup_vs_optix": optix_metric / embree_metric,
                "metric_sources": {
                    "embree": embree.get("primary_metric_source"),
                    "optix": optix.get("primary_metric_source"),
                },
            }
        )
    return ratios


def render_markdown(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    ratios = payload["ratios"]
    lines = [
        "# Goal2626 Embree vs OptiX Baseline",
        "",
        "This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.",
        "It is not a public speedup claim.",
        "",
        f"- Commit: `{payload['environment'].get('git_commit', '')}`",
        f"- Scale: `{payload['scale']}`",
        f"- Case repeat: `{payload['case_repeat']}`",
        f"- Generated: `{payload['generated_at']}`",
        "",
        "## Ratios",
        "",
        "| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for ratio in ratios:
        lines.append(
            "| {app} | {group} | {embree:.6g} | {optix:.6g} | {speedup:.3g}x | {sources} |".format(
                app=ratio["app_id"],
                group=ratio["comparison_group"],
                embree=ratio["embree_sec"],
                optix=ratio["optix_sec"],
                speedup=ratio["optix_speedup_vs_embree"],
                sources=json.dumps(ratio["metric_sources"], sort_keys=True),
            )
        )
    if not ratios:
        lines.append("| none | no comparable successful Embree/OptiX pairs |  |  |  |  |")
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| App | Case | Backend | Status | Primary sec | Source or reason |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in rows:
        if row.get("status") == "unsupported":
            source = str(row.get("unsupported_reason", ""))
            metric = ""
        else:
            source = str(row.get("primary_metric_source", ""))
            metric_value = row.get("primary_metric_sec")
            metric = f"{float(metric_value):.6g}" if isinstance(metric_value, (int, float)) else ""
        lines.append(
            f"| {row['app_id']} | {row['case_id']} | {row['backend']} | {row['status']} | {metric} | {source} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.",
            "- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.",
            "- Rows with different comparison groups are not ratioed.",
            "- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "summary.md").write_text(render_markdown(payload), encoding="utf-8")


def _filter_cases(
    cases: tuple[BenchmarkCase, ...],
    *,
    only_app: tuple[str, ...],
    only_case: tuple[str, ...],
) -> tuple[BenchmarkCase, ...]:
    filtered = list(cases)
    if only_app:
        selected = set(only_app)
        filtered = [case for case in filtered if case.app_id in selected]
    if only_case:
        selected = set(only_case)
        filtered = [case for case in filtered if case.case_id in selected]
    return tuple(filtered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", choices=("quick", "standard", "large"), default="standard")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--case-repeat", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=900)
    parser.add_argument("--only-app", action="append", default=[])
    parser.add_argument("--only-case", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build-native", action="store_true")
    args = parser.parse_args(argv)

    env = _base_env()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    if args.build_native and not args.dry_run:
        for command in (("make", "build-embree"), ("make", "build-optix")):
            completed = _run_process(command, env=env, timeout_sec=args.timeout_sec)
            if completed.returncode != 0:
                print(completed.stdout, end="")
                print(completed.stderr, end="", file=sys.stderr)
                return completed.returncode
        env = _base_env()

    cases = _filter_cases(
        build_cases(args.scale, args.artifact_dir),
        only_app=tuple(args.only_app),
        only_case=tuple(args.only_case),
    )
    rows = []
    for case in cases:
        print(f"[goal2626] {case.case_id} ({case.backend})", flush=True)
        rows.append(
            run_case(
                case,
                env=env,
                timeout_sec=args.timeout_sec,
                repeat=args.case_repeat,
                dry_run=args.dry_run,
            )
        )
    payload = {
        "goal": "Goal2626",
        "purpose": "Embree vs OptiX/RT baseline across promoted benchmark apps before Triton/Numba partner work.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "scale": args.scale,
        "case_repeat": args.case_repeat,
        "dry_run": args.dry_run,
        "promoted_benchmark_apps": list(PROMOTED_BENCHMARK_APPS),
        "environment": collect_environment_probe(env) if not args.dry_run else {"repo_root": str(ROOT)},
        "rows": rows,
        "ratios": compute_ratios(rows),
        "claim_boundary": {
            "internal_baseline_only": True,
            "public_speedup_claim_authorized": False,
            "future_partner_baseline": "Triton/Numba no-new-C++ path",
        },
    }
    write_outputs(payload, args.artifact_dir)
    print(f"[goal2626] wrote {args.artifact_dir / 'summary.json'}", flush=True)
    print(f"[goal2626] wrote {args.artifact_dir / 'summary.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
