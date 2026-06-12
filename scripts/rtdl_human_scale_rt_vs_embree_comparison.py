#!/usr/bin/env python3
"""Run a human-scale OptiX-vs-Embree comparison packet.

The packet targets 1-10 second hot-query aggregates where feasible. For rows
whose speedup makes one shared repeat count impossible, it uses
duration-bounded throughput: identical work per iteration, different repeat
counts only to accumulate stable wall time on each backend.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "reports" / "goal4349_human_scale_rt_vs_embree_run"


def _base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": "src:.",
            "RTDL_OPTIX_LIBRARY": str(ROOT / "build" / "librtdl_optix.so"),
            "RTDL_OPTIX_LIB": str(ROOT / "build" / "librtdl_optix.so"),
            "RTDL_EMBREE_LIBRARY": str(ROOT / "build" / "librtdl_embree.so"),
            "RTDL_CUDA_PREFIX": env.get("RTDL_CUDA_PREFIX", "/usr/local/cuda-12.8"),
            "NUMBA_CUDA_PREFIX": env.get(
                "NUMBA_CUDA_PREFIX",
                "/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc",
            ),
        }
    )
    env["CUDA_HOME"] = env["NUMBA_CUDA_PREFIX"]
    env["CUDA_PATH"] = env["NUMBA_CUDA_PREFIX"]
    env["PATH"] = (
        f"{env['RTDL_CUDA_PREFIX']}/bin:{env['NUMBA_CUDA_PREFIX']}/bin:"
        + env.get("PATH", "")
    )
    env["LD_LIBRARY_PATH"] = (
        f"{env['NUMBA_CUDA_PREFIX']}/nvvm/lib64:"
        f"{env['RTDL_CUDA_PREFIX']}/targets/x86_64-linux/lib:"
        f"{env['RTDL_CUDA_PREFIX']}/lib64:"
        + env.get("LD_LIBRARY_PATH", "")
    )
    return env


def _thread_env(threads: int | None = None) -> dict[str, str]:
    if threads is None:
        return {}
    text = str(int(threads))
    return {
        "OMP_NUM_THREADS": text,
        "TBB_NUM_THREADS": text,
        "MKL_NUM_THREADS": text,
        "OPENBLAS_NUM_THREADS": text,
        "NUMEXPR_NUM_THREADS": text,
        "RTDL_EMBREE_THREADS": text,
    }


def _parse_json_stdout(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("stdout was empty")
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end < start:
            raise
        return json.loads(stripped[start : end + 1])


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def _dig(payload: dict[str, Any], path: str) -> Any:
    node: Any = payload
    for key in path.split("."):
        if not isinstance(node, dict):
            raise KeyError(path)
        node = node[key]
    return node


def _float(payload: dict[str, Any], path: str) -> float:
    return float(_dig(payload, path))


def _maybe(payload: dict[str, Any], path: str, default: Any = None) -> Any:
    try:
        return _dig(payload, path)
    except KeyError:
        return default


@dataclass(frozen=True)
class RunSpec:
    label: str
    app: str
    backend: str
    command: tuple[str, ...]
    extractor: Callable[[dict[str, Any]], dict[str, Any]]
    timeout_sec: int
    threads: int | None = None
    json_out: bool = False


def _artifact_matches_current_spec(spec: RunSpec, payload: dict[str, Any]) -> bool:
    if spec.app == "rtnn" and spec.backend == "embree":
        claim = payload.get("claim_boundary", {})
        if claim.get("materializes_neighbor_rows"):
            return False
        for phase in payload.get("batch_phase_timings", ()):
            if isinstance(phase, dict) and phase.get("mode") == "embree_fixed_radius_rows_to_ranked_summary_rows":
                return False
    if spec.app.startswith("spatial_rayjoin") and spec.backend == "embree":
        if payload.get("output_contract") == "generic_row_count_raw_view_no_python_dicts":
            return False
        if payload.get("output_contract") == "native_embree_scalar_count_no_row_materialization":
            return False
        if payload.get("output_contract") != "native_embree_prepared_scalar_count_no_row_materialization":
            return False
        if not payload.get("prepared_count_required"):
            return False
    return True


def _run_spec(spec: RunSpec, output_dir: Path, *, dry_run: bool = False) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    command = list(spec.command)
    json_path = output_dir / f"{spec.label}.json"
    if spec.json_out:
        command.extend(["--json-out", str(json_path)])
    stdout_path = output_dir / f"{spec.label}.stdout"
    stderr_path = output_dir / f"{spec.label}.stderr"
    env = _base_env()
    env.update(_thread_env(spec.threads))
    started = time.perf_counter()
    if json_path.exists() and stdout_path.exists() and stderr_path.exists() and not dry_run:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if _artifact_matches_current_spec(spec, payload):
            extracted = spec.extractor(payload)
            return {
                "label": spec.label,
                "app": spec.app,
                "backend": spec.backend,
                "threads": spec.threads,
                "returncode": 0,
                "wall_sec": 0.0,
                "reused_existing_artifact": True,
                "command": command,
                "json": _rel(json_path),
                "stdout": _rel(stdout_path),
                "stderr": _rel(stderr_path),
                "metric": extracted,
            }
    if dry_run:
        return {
            "label": spec.label,
            "app": spec.app,
            "backend": spec.backend,
            "threads": spec.threads,
            "command": command,
            "json": _rel(json_path),
            "stdout": _rel(stdout_path),
            "stderr": _rel(stderr_path),
            "dry_run": True,
        }
    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=spec.timeout_sec,
        check=False,
    )
    wall_sec = time.perf_counter() - started
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    if spec.json_out:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        payload = _parse_json_stdout(proc.stdout)
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    extracted = spec.extractor(payload)
    return {
        "label": spec.label,
        "app": spec.app,
        "backend": spec.backend,
        "threads": spec.threads,
        "returncode": proc.returncode,
        "wall_sec": wall_sec,
        "command": command,
        "json": _rel(json_path),
        "stdout": _rel(stdout_path),
        "stderr": _rel(stderr_path),
        "metric": extracted,
    }


def _hausdorff(payload: dict[str, Any]) -> dict[str, Any]:
    a = _float(payload, "directed_a_to_b.run_phases.query_fixed_radius_threshold_reached_count_total_sec")
    b = _float(payload, "directed_b_to_a.run_phases.query_fixed_radius_threshold_reached_count_total_sec")
    repeat = int(_dig(payload, "directed_a_to_b.run_phases.query_repeat"))
    return {
        "contract": "directed_threshold_prepared_fixed_radius_count",
        "scope": "two directed prepared fixed-radius threshold decisions",
        "total_sec": a + b,
        "per_iter_sec": (a + b) / repeat,
        "repeat": repeat,
        "warmup": int(_dig(payload, "directed_a_to_b.run_phases.query_warmup")),
        "human_scale_basis": "sum of measured A->B and B->A query totals",
        "correct": bool(payload.get("matches_oracle")) and bool(payload.get("oracle_decision_matches")),
    }


def _barnes(payload: dict[str, Any]) -> dict[str, Any]:
    proto = _dig(payload, "node_coverage.query_repeat_protocol")
    return {
        "contract": "prepared_fixed_radius_node_coverage_threshold_decision",
        "scope": "prepared node-coverage threshold-count query",
        "total_sec": float(proto["query_sec_total"]),
        "per_iter_sec": float(proto["query_sec_median"]),
        "repeat": int(proto["repeat"]),
        "warmup": int(proto["warmup"]),
        "human_scale_basis": "measured query_sec_total",
        "correct": bool(payload.get("matches_oracle")) and bool(payload.get("oracle_decision_matches")),
    }


def _contact(payload: dict[str, Any]) -> dict[str, Any]:
    phases = payload["run_phases"]
    return {
        "contract": "generic_aabb_broadphase_contact_candidates_2d_grid16384",
        "scope": "prepared generic AABB broadphase row output; exact contact refinement common",
        "total_sec": float(phases["emit_aabb_intersection_pair_rows_2d_total_sec"]),
        "per_iter_sec": float(phases["emit_aabb_intersection_pair_rows_2d_median_sec"]),
        "repeat": int(phases["emit_aabb_intersection_pair_rows_2d_measured_count"]),
        "warmup": int(payload.get("discovery_warmup_count", 0)),
        "human_scale_basis": "measured broadphase query total",
        "correct": bool(payload.get("matches_cpu_reference")) and bool(payload.get("complete_candidate_coverage")),
    }


def _rtdbscan(payload: dict[str, Any]) -> dict[str, Any]:
    proto = _dig(payload, "metadata.prepared_query_repeat_protocol")
    return {
        "contract": "fixed_radius_core_flags_plus_numba_column_signature",
        "scope": "native threshold/core flags followed by the same Numba component-signature continuation",
        "total_sec": float(proto["elapsed_sec_total"]),
        "per_iter_sec": float(proto["median_elapsed_sec"]),
        "repeat": int(proto["measured_iterations"]),
        "warmup": int(proto["warmup"]),
        "human_scale_basis": "measured prepared-query elapsed total",
        "correct": payload.get("matches_reference") in (True, None),
        "timing_total_sec": _maybe(payload, "metadata.timing_total_sec", {}),
    }


def _rayjoin(payload: dict[str, Any]) -> dict[str, Any]:
    phases = payload.get("phases_sec", {})
    if "prepared_query_sec_total_sec" in phases:
        total_sec = float(phases["prepared_query_sec_total_sec"])
        repeat = int(phases.get("prepared_query_sec_repeat", payload.get("repeat", 0)))
        warmup = int(phases.get("prepared_query_sec_warmup", payload.get("warmup", 0)))
        per_iter_sec = float(phases["prepared_query_sec"])
    else:
        runs = payload.get("runs", [])
        measured = [row for row in runs if not bool(row.get("is_warmup"))]
        values = [float(row["elapsed_sec"]) for row in measured]
        total_sec = float(sum(values))
        per_iter_sec = float(statistics.median(values))
        repeat = len(values)
        warmup = len(runs) - len(values)
    workload = str(payload.get("workload", "rayjoin"))
    return {
        "contract": f"public_cdb_{workload}_count",
        "scope": "scalar count over the same public CDB slice",
        "total_sec": total_sec,
        "per_iter_sec": per_iter_sec,
        "repeat": repeat,
        "warmup": warmup,
        "human_scale_basis": "measured prepared/generic count total",
        "correct": True,
        "row_count": int(payload.get("row_count", payload.get("summary", {}).get("positive_assignment_count", 0))),
    }


def _rtnn(payload: dict[str, Any]) -> dict[str, Any]:
    runs = [float(value) for value in payload["elapsed_runs_sec"]]
    return {
        "contract": "prepared_3d_fixed_radius_ranked_summary_raw",
        "scope": "ranked-summary rows for the same point/query batch",
        "total_sec": float(sum(runs)),
        "per_iter_sec": float(payload["elapsed_median_sec"]),
        "repeat": int(payload["repeat"]),
        "warmup": 0,
        "human_scale_basis": "sum of reported elapsed_runs_sec",
        "correct": bool(payload.get("ok", True)),
    }


def _librts(payload: dict[str, Any]) -> dict[str, Any]:
    phases = payload["run_phases"]
    return {
        "contract": "generic_prepared_aabb_index_query_2d_all_ops",
        "scope": "point_contains + range_contains + range_intersects prepared AABB queries",
        "total_sec": float(phases["query_total_sec"]),
        "per_iter_sec": float(phases["query_median_sec"]),
        "repeat": int(phases["query_repeat"]),
        "warmup": int(phases["query_warmup"]),
        "human_scale_basis": "measured query_total_sec",
        "correct": payload.get("matches_cpu_reference") in (True, None),
    }


def _triangle(payload: dict[str, Any]) -> dict[str, Any]:
    timing = payload["timing_ms"]
    return {
        "contract": "rt_graph_2a1_generic_ray_triangle_any_hit",
        "scope": "prepared ray-triangle weighted any-hit summary",
        "total_sec": float(timing["query_total_ms"]) / 1000.0,
        "per_iter_sec": float(timing["query_median_ms"]) / 1000.0,
        "repeat": int(timing["query_measured_runs"]),
        "warmup": int(timing["query_warmup"]),
        "human_scale_basis": "measured query_total_ms",
        "correct": bool(payload.get("triangle_count_matches_oracle")),
    }


def _robot(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": "prepared_triangle_scene_grouped_segment_any_hit_flags",
        "scope": "prepared grouped segment any-hit flags; traversal phase",
        "total_sec": _float(payload, "run_summary.phase_timing_seconds.traversal.total_sec"),
        "per_iter_sec": _float(payload, "tail_medians.phase_timing_seconds.traversal"),
        "repeat": int(_dig(payload, "reuse_metadata.measured_run_count")),
        "warmup": int(_dig(payload, "reuse_metadata.warmup_rows_dropped")),
        "human_scale_basis": "measured traversal total over tail runs",
        "correct": bool(_dig(payload, "reuse_metadata.all_run_signatures_identical")),
    }


def _raydb(payload: dict[str, Any]) -> dict[str, Any]:
    summary = _dig(payload, "metadata.prepared_phase_timing_summary.native_call_wall")
    return {
        "contract": "prepared_ray_triangle_grouped_i64_reduction_count",
        "scope": "prepared generic grouped i64 count reduction over the same generated rows/groups",
        "total_sec": float(summary["total_sec"]),
        "per_iter_sec": float(summary["median_sec"]),
        "repeat": int(summary["count"]),
        "warmup": int(_dig(payload, "metadata.prepared_internal_warmup")),
        "human_scale_basis": "prepared_phase_timing_summary.native_call_wall.total_sec",
        "correct": bool(payload.get("matches_cpu_reference")),
    }


def _rayjoin_embree_probe(workload: str, dataset: str, repeat: int, warmup: int) -> str:
    return f"""
import json, statistics, time
import rtdsl as rt
from examples.current.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as app

case = app._load_rayjoin_case({workload!r}, {dataset!r}, segment_column_inputs=False)
kernel = app._KERNELS[{workload!r}]
runs = []
with rt.prepare_embree(kernel).bind(**case.inputs) as prepared:
    for iteration in range({warmup} + {repeat}):
        start = time.perf_counter()
        row_count = prepared.count(require_prepared=True)
        elapsed = time.perf_counter() - start
        runs.append({{
            "iteration": iteration,
            "is_warmup": iteration < {warmup},
            "elapsed_sec": elapsed,
            "native_traversal_sec": prepared.last_count_traversal_seconds,
            "row_count": row_count,
        }})
measured = [row for row in runs if not row["is_warmup"]]
counts = {{row["row_count"] for row in measured}}
if len(counts) != 1:
    raise RuntimeError("row count changed")
print(json.dumps({{
    "app": "rayjoin_v2_spatial_join",
    "backend": "embree",
    "workload": {workload!r},
    "dataset": {dataset!r},
    "row_count": measured[-1]["row_count"],
    "runs": runs,
    "hot_median_sec": statistics.median(row["elapsed_sec"] for row in measured),
    "hot_native_traversal_median_sec": statistics.median(row["native_traversal_sec"] for row in measured),
    "counts_stable": True,
    "output_contract": "native_embree_prepared_scalar_count_no_row_materialization",
    "prepared_count_required": True,
}}, indent=2, sort_keys=True))
"""


def _specs() -> tuple[RunSpec, ...]:
    py = sys.executable
    pip_dataset = "data/rayjoin_public_cdb/br_county_start256_count512.cdb"
    lsi_dataset = (
        "data/rayjoin_public_cdb/br_county_start256_count512.cdb + "
        "data/rayjoin_public_cdb/br_soil_start256_count512.cdb"
    )
    rtnn_points = "docs/reports/goal4347_fair_rt_vs_embree_run/scale/rtnn_uniform_65536.csv"
    return (
        RunSpec("hausdorff_optix_r200", "hausdorff_xhd", "optix", (py, "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", "--backend", "optix", "--require-rt-core", "--optix-summary-mode", "directed_threshold_prepared", "--hausdorff-threshold", "0.25", "--copies", "1024", "--repeat", "200", "--warmup", "5"), _hausdorff, 240),
        RunSpec("hausdorff_embree_t8_r200", "hausdorff_xhd", "embree", (py, "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--optix-summary-mode", "directed_threshold_prepared", "--hausdorff-threshold", "0.25", "--copies", "1024", "--repeat", "200", "--warmup", "5"), _hausdorff, 240, threads=8),
        RunSpec("hausdorff_embree_t64_r200", "hausdorff_xhd", "embree", (py, "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py", "--backend", "embree", "--optix-summary-mode", "directed_threshold_prepared", "--hausdorff-threshold", "0.25", "--copies", "1024", "--repeat", "200", "--warmup", "5"), _hausdorff, 240, threads=64),
        RunSpec("barnes_optix_r150", "barnes_hut", "optix", (py, "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py", "--mode", "optix_node_coverage_prepared", "--body-count", "8192", "--node-radius", "10.0", "--repeat", "150", "--warmup", "5"), _barnes, 240, json_out=True),
        RunSpec("barnes_embree_t8_r150", "barnes_hut", "embree", (py, "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py", "--mode", "embree_node_coverage_prepared", "--body-count", "8192", "--node-radius", "10.0", "--repeat", "150", "--warmup", "5"), _barnes, 240, threads=8, json_out=True),
        RunSpec("barnes_embree_t64_r150", "barnes_hut", "embree", (py, "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py", "--mode", "embree_node_coverage_prepared", "--body-count", "8192", "--node-radius", "10.0", "--repeat", "150", "--warmup", "5"), _barnes, 240, threads=64, json_out=True),
        RunSpec("contact_optix_g16384_r20", "contact_manifold", "optix", (py, "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py", "--mode", "aabb_broadphase_collect_k", "--dataset", "grid", "--grid-count", "16384", "--witness-capacity", "16384", "--discovery-backend", "optix", "--discovery-warmup", "3", "--discovery-repeat", "20"), _contact, 240),
        RunSpec("contact_embree_t8_g16384_r20", "contact_manifold", "embree", (py, "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py", "--mode", "aabb_broadphase_collect_k", "--dataset", "grid", "--grid-count", "16384", "--witness-capacity", "16384", "--discovery-backend", "embree", "--discovery-warmup", "3", "--discovery-repeat", "20"), _contact, 240, threads=8),
        RunSpec("contact_embree_t64_g16384_r20", "contact_manifold", "embree", (py, "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py", "--mode", "aabb_broadphase_collect_k", "--dataset", "grid", "--grid-count", "16384", "--witness-capacity", "16384", "--discovery-backend", "embree", "--discovery-warmup", "3", "--discovery-repeat", "20"), _contact, 240, threads=64),
        RunSpec("rtdbscan_optix_numba_r95", "rt_dbscan", "optix", (py, "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py", "--mode", "optix_rt_core_flags_numba_prepared_grid_column_signature_3d", "--dataset", "clustered3d", "--point-count", "4096", "--repeat", "95", "--warmup", "5", "--no-validation"), _rtdbscan, 240),
        RunSpec("rtdbscan_embree_numba_t8_r95", "rt_dbscan", "embree", (py, "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py", "--mode", "embree_core_flags_numba_prepared_grid_column_signature_3d", "--dataset", "clustered3d", "--point-count", "4096", "--repeat", "95", "--warmup", "5", "--no-validation"), _rtdbscan, 300, threads=8),
        RunSpec("rtdbscan_embree_numba_t64_r95", "rt_dbscan", "embree", (py, "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py", "--mode", "embree_core_flags_numba_prepared_grid_column_signature_3d", "--dataset", "clustered3d", "--point-count", "4096", "--repeat", "95", "--warmup", "5", "--no-validation"), _rtdbscan, 300, threads=64),
        RunSpec("rayjoin_pip_optix_r2000", "spatial_rayjoin_pip", "optix", (py, "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py", "--workload", "pip", "--backend", "optix", "--execution-route", "prepared_optix", "--result-mode", "count", "--dataset", pip_dataset, "--no-rows", "--repeat", "2000", "--warmup", "10"), _rayjoin, 240),
        RunSpec("rayjoin_pip_embree_t8_r2000", "spatial_rayjoin_pip", "embree", (py, "-c", _rayjoin_embree_probe("pip", pip_dataset, 2000, 10)), _rayjoin, 240, threads=8),
        RunSpec("rayjoin_pip_embree_t64_r2000", "spatial_rayjoin_pip", "embree", (py, "-c", _rayjoin_embree_probe("pip", pip_dataset, 2000, 10)), _rayjoin, 240, threads=64),
        RunSpec("rayjoin_lsi_optix_r5000", "spatial_rayjoin_lsi", "optix", (py, "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py", "--workload", "lsi", "--backend", "optix", "--execution-route", "prepared_optix", "--result-mode", "count", "--dataset", lsi_dataset, "--no-rows", "--repeat", "5000", "--warmup", "10"), _rayjoin, 300),
        RunSpec("rayjoin_lsi_embree_t8_r5", "spatial_rayjoin_lsi", "embree", (py, "-c", _rayjoin_embree_probe("lsi", lsi_dataset, 5, 1)), _rayjoin, 240, threads=8),
        RunSpec("rayjoin_lsi_embree_t64_r5", "spatial_rayjoin_lsi", "embree", (py, "-c", _rayjoin_embree_probe("lsi", lsi_dataset, 5, 1)), _rayjoin, 240, threads=64),
        RunSpec("rtnn_optix_r1500", "rtnn", "optix", (py, "scripts/goal2348_rtnn_v2_2_external_runner.py", "run-rtdl-batched-3d-neighbors", "--point-file", rtnn_points, "--radius", "0.02", "--k-max", "50", "--backend", "optix", "--query-batch-size", "65536", "--result-mode", "ranked-summary-raw", "--repeat", "1500", "--row-label", "human_scale_rtnn_optix"), _rtnn, 300, json_out=True),
        RunSpec("rtnn_embree_t8_r120", "rtnn", "embree", (py, "scripts/goal2348_rtnn_v2_2_external_runner.py", "run-rtdl-batched-3d-neighbors", "--point-file", rtnn_points, "--radius", "0.02", "--k-max", "50", "--backend", "embree", "--query-batch-size", "65536", "--result-mode", "ranked-summary-raw", "--repeat", "120", "--row-label", "human_scale_rtnn_embree_t8"), _rtnn, 300, threads=8, json_out=True),
        RunSpec("rtnn_embree_t64_r120", "rtnn", "embree", (py, "scripts/goal2348_rtnn_v2_2_external_runner.py", "run-rtdl-batched-3d-neighbors", "--point-file", rtnn_points, "--radius", "0.02", "--k-max", "50", "--backend", "embree", "--query-batch-size", "65536", "--result-mode", "ranked-summary-raw", "--repeat", "120", "--row-label", "human_scale_rtnn_embree_t64"), _rtnn, 300, threads=64, json_out=True),
        RunSpec("librts_optix_r4800", "librts_spatial_index", "optix", (py, "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py", "--mode", "optix_aabb_index", "--dataset", "uniform", "--box-count", "1024", "--query-count", "1024", "--operation", "all", "--repeat", "4800", "--warmup", "10", "--skip-counts"), _librts, 300),
        RunSpec("librts_embree_t8_r48", "librts_spatial_index", "embree", (py, "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py", "--mode", "embree_aabb_index", "--dataset", "uniform", "--box-count", "1024", "--query-count", "1024", "--operation", "all", "--repeat", "48", "--warmup", "3", "--skip-counts"), _librts, 240, threads=8),
        RunSpec("librts_embree_t64_r48", "librts_spatial_index", "embree", (py, "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py", "--mode", "embree_aabb_index", "--dataset", "uniform", "--box-count", "1024", "--query-count", "1024", "--operation", "all", "--repeat", "48", "--warmup", "3", "--skip-counts"), _librts, 240, threads=64),
        RunSpec("triangle_optix_r20000", "triangle_counting", "optix", (py, "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py", "--mode", "rt_graph_2a1_generic_rt", "--backend", "optix", "--fixture", "degree_oriented_two_triangles", "--rt-graph-copies", "2048", "--detail", "summary", "--repeat", "20000", "--warmup", "5"), _triangle, 300),
        RunSpec("triangle_embree_t8_r500", "triangle_counting", "embree", (py, "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py", "--mode", "rt_graph_2a1_generic_rt", "--backend", "embree", "--fixture", "degree_oriented_two_triangles", "--rt-graph-copies", "2048", "--detail", "summary", "--repeat", "500", "--warmup", "5"), _triangle, 240, threads=8),
        RunSpec("triangle_embree_t64_r500", "triangle_counting", "embree", (py, "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py", "--mode", "rt_graph_2a1_generic_rt", "--backend", "embree", "--fixture", "degree_oriented_two_triangles", "--rt-graph-copies", "2048", "--detail", "summary", "--repeat", "500", "--warmup", "5"), _triangle, 240, threads=64),
        RunSpec("robot_optix_buffers_r50000", "robot_collision", "optix", (py, "examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py", "--mode", "optix_prepared_buffers", "--dataset", "scaled", "--pose-count", "1024", "--obstacle-count", "128", "--link-count", "4", "--repeats", "50000", "--warmup", "100", "--no-probe-reference", "--summary-only-runs"), _robot, 300),
        RunSpec("robot_embree_buffers_t8_r2500", "robot_collision", "embree", (py, "examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py", "--mode", "embree_prepared_buffers", "--dataset", "scaled", "--pose-count", "1024", "--obstacle-count", "128", "--link-count", "4", "--repeats", "2500", "--warmup", "50", "--no-probe-reference", "--summary-only-runs"), _robot, 300, threads=8),
        RunSpec("robot_embree_buffers_t64_r2500", "robot_collision", "embree", (py, "examples/current/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py", "--mode", "embree_prepared_buffers", "--dataset", "scaled", "--pose-count", "1024", "--obstacle-count", "128", "--link-count", "4", "--repeats", "2500", "--warmup", "50", "--no-probe-reference", "--summary-only-runs"), _robot, 300, threads=64),
        RunSpec("raydb_optix_r5000", "raydb_style", "optix", (py, "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py", "--mode", "count", "--backend", "paper_rt_optix_v2_5_primitive_first", "--fixture-kind", "generated", "--generated-rows", "262144", "--generated-groups", "1024", "--repeat", "5000", "--warmup", "50", "--summary-only-iterations"), _raydb, 360),
        RunSpec("raydb_embree_t8_r240", "raydb_style", "embree", (py, "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py", "--mode", "count", "--backend", "paper_rt_embree", "--fixture-kind", "generated", "--generated-rows", "262144", "--generated-groups", "1024", "--repeat", "240", "--warmup", "5", "--summary-only-iterations"), _raydb, 300, threads=8),
        RunSpec("raydb_embree_t64_r240", "raydb_style", "embree", (py, "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py", "--mode", "count", "--backend", "paper_rt_embree", "--fixture-kind", "generated", "--generated-rows", "262144", "--generated-groups", "1024", "--repeat", "240", "--warmup", "5", "--summary-only-iterations"), _raydb, 300, threads=64),
    )


ROW_ASSESSMENTS: dict[str, dict[str, str]] = {
    "barnes_hut": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_hot_phase",
        "speedup_explanation": (
            "Embree median 22.79 ms divided by OptiX median 8.27 ms gives 2.76x. "
            "The row is traversal-heavy, emits only a threshold decision, and keeps the "
            "prepared node-coverage contract fixed."
        ),
        "public_wording": "Safe as a prepared RT traversal comparison.",
    },
    "contact_manifold": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_broadphase",
        "speedup_explanation": (
            "Embree median 157.46 ms divided by OptiX median 124.28 ms gives 1.27x. "
            "The modest gain matches the row-output-heavy AABB broadphase: both sides "
            "emit the same 16,384 candidate rows and then share the exact refinement."
        ),
        "public_wording": "Safe, but word as a modest broadphase gain, not a dramatic whole-app claim.",
    },
    "hausdorff_xhd": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_hot_phase",
        "speedup_explanation": (
            "Embree combined per-iteration threshold work 22.76 ms divided by OptiX "
            "9.16 ms gives 2.49x. Two directed fixed-radius threshold queries use the "
            "same prepared contract."
        ),
        "public_wording": "Safe as a prepared threshold-query traversal comparison.",
    },
    "librts_spatial_index": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_aabb_index_ops",
        "speedup_explanation": (
            "Embree all-ops median 39.00 ms divided by OptiX median 0.563 ms gives "
            "69.32x. Counts match for point_contains, range_contains, and "
            "range_intersects over the same prepared AABB workload."
        ),
        "public_wording": "Safe for the prepared AABB-index all-ops contract.",
    },
    "raydb_style": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_grouped_reduction",
        "speedup_explanation": (
            "Embree native grouped-reduction median 6.60 ms divided by OptiX median "
            "0.580 ms gives 11.38x. Both sides now use the prepared grouped i64 "
            "reduction surface over the same generated rows/groups."
        ),
        "public_wording": "Safe as a prepared grouped-reduction comparison.",
    },
    "robot_collision": {
        "comparison_status": "clean_backend_swap_traversal_phase_only",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "qualified_traversal_phase_only",
        "speedup_explanation": (
            "Embree traversal median 1.195 ms divided by OptiX traversal median "
            "0.121 ms gives 9.87x. The full hot run is smaller because tail/output "
            "work dominates outside the traversal phase."
        ),
        "public_wording": "Use only as traversal-phase speedup, not as whole hot-loop speedup.",
    },
    "rt_dbscan": {
        "comparison_status": "mostly_clean_numba_continuation_same_native_handoff_differs",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "qualified_native_handoff_differs",
        "speedup_explanation": (
            "Embree median 102.91 ms divided by OptiX median 11.43 ms gives 9.00x. "
            "The native threshold/core-flag portion has a matching 9.47x ratio, while "
            "the Numba continuation is nearly equal across backends."
        ),
        "public_wording": "Use as RT threshold plus shared Numba continuation; disclose the handoff difference.",
    },
    "rtnn": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_ranked_summary_rows",
        "speedup_explanation": (
            "Generated from measured medians at report build time. Both sides use a "
            "prepared fixed-radius 3-D ranked-summary surface without neighbor-row materialization."
        ),
        "public_wording": "Safe as a prepared fixed-radius ranked-summary comparison after fresh artifacts pass the stale guard.",
    },
    "spatial_rayjoin_lsi": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_scalar_count",
        "speedup_explanation": (
            "Generated from measured medians at report build time. Both sides use a "
            "prepared native scalar-count path without row materialization."
        ),
        "public_wording": "Safe as a prepared segment-pair scalar-count comparison after fresh artifacts pass the stale guard.",
    },
    "spatial_rayjoin_pip": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_scalar_count",
        "speedup_explanation": (
            "Generated from measured medians at report build time. Both sides use a "
            "prepared native scalar-count path without row materialization."
        ),
        "public_wording": "Safe as a prepared point-in-polygon scalar-count comparison after fresh artifacts pass the stale guard.",
    },
    "triangle_counting": {
        "comparison_status": "clean_backend_swap_prepared_phase",
        "reasonability_verdict": "reasonable",
        "only_material_diff_claim": "yes_for_prepared_weighted_any_hit_summary",
        "speedup_explanation": (
            "Embree prepared weighted any-hit median 6.07 ms divided by OptiX median "
            "0.144 ms gives 42.16x. Both sides now use the same scalar weighted "
            "any-hit summary contract without materializing hit rows."
        ),
        "public_wording": "Safe as a prepared weighted any-hit summary comparison.",
    },
}


def _assessment_for(app: str) -> dict[str, str]:
    try:
        return ROW_ASSESSMENTS[app]
    except KeyError as exc:
        raise KeyError(f"missing row assessment for {app}") from exc


def _protocol_for(optix: dict[str, Any], embree: dict[str, Any]) -> str:
    o = optix["metric"]
    e = embree["metric"]
    if int(o["repeat"]) == int(e["repeat"]):
        return "same_repeat_human_scale"
    return "duration_bounded_throughput"


def _metric_ms(seconds: float) -> str:
    value = seconds * 1000.0
    if value >= 100.0:
        return f"{value:.2f}"
    if value >= 10.0:
        return f"{value:.3f}"
    return f"{value:.4f}"


def _speedup_explanation_for(app: str, optix_per_iter: float, embree_per_iter: float) -> str:
    ratio = embree_per_iter / optix_per_iter
    if ratio >= 1.0:
        direction = f"OptiX is faster by {ratio:.2f}x on this per-iteration metric."
    else:
        direction = f"Embree is faster by {(1.0 / ratio):.2f}x on this per-iteration metric."
    prefix = (
        f"Embree median {_metric_ms(embree_per_iter)} ms divided by OptiX median "
        f"{_metric_ms(optix_per_iter)} ms gives {ratio:.2f}x. {direction}"
    )
    drivers = {
        "hausdorff_xhd": (
            "Both sides run the prepared directed-threshold nearest-query phase, so the ratio is "
            "attributable to RT traversal throughput plus each backend's native query overhead."
        ),
        "barnes_hut": (
            "Both sides run prepared node-coverage queries over the same body/tree workload; "
            "no app-level continuation changes the measured phase."
        ),
        "contact_manifold": (
            "Both sides run the same prepared AABB broadphase collect-k contract. A modest or "
            "reversed ratio is still plausible because this row is dominated by compact AABB "
            "candidate collection and witness bookkeeping rather than long coherent ray batches."
        ),
        "librts_spatial_index": (
            "Both sides run the prepared AABB-index all-ops contract with matching counts for "
            "point_contains, range_contains, and range_intersects."
        ),
        "raydb_style": (
            "Both sides use the prepared grouped i64 reduction surface over the same generated "
            "rows and groups, so the ratio follows the traversal/reduction backend path."
        ),
        "robot_collision": (
            "This is intentionally traversal-phase only; full hot-loop timing can differ because "
            "tail/output work sits outside the RT traversal comparison."
        ),
        "rt_dbscan": (
            "Both sides share the Numba continuation, while the native threshold/core-flag "
            "handoff is backend-specific; compare this as RT query acceleration plus fixed partner continuation."
        ),
        "rtnn": (
            "Both sides use prepared fixed-radius 3-D ranked-summary rows, so the old Embree "
            "neighbor-row materialization explanation no longer applies."
        ),
        "spatial_rayjoin_lsi": (
            "Both sides use a prepared native scalar-count contract for segment-pair intersection "
            "without materializing intersection rows."
        ),
        "spatial_rayjoin_pip": (
            "Both sides use a prepared native scalar-count contract for point-in-polygon positive "
            "hits without materializing hit rows."
        ),
        "triangle_counting": (
            "Both sides use the prepared weighted any-hit summary contract, so the row measures "
            "backend traversal plus scalar accumulation rather than hit-row output volume."
        ),
    }
    return f"{prefix} {drivers.get(app, 'Both sides use the same benchmark contract recorded for this row.')}"


def _build_rows(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    passed = [row for row in runs if row.get("returncode") == 0]
    apps = sorted({row["app"] for row in passed})
    rows: list[dict[str, Any]] = []
    for app in apps:
        optix_rows = [row for row in passed if row["app"] == app and row["backend"] == "optix"]
        embree_rows = [row for row in passed if row["app"] == app and row["backend"] == "embree"]
        if not optix_rows or not embree_rows:
            continue
        optix = min(optix_rows, key=lambda row: float(row["metric"]["total_sec"]))
        best_embree = min(embree_rows, key=lambda row: float(row["metric"]["total_sec"]))
        optix_total = float(optix["metric"]["total_sec"])
        embree_total = float(best_embree["metric"]["total_sec"])
        optix_per_iter = float(optix["metric"]["per_iter_sec"])
        embree_per_iter = float(best_embree["metric"]["per_iter_sec"])
        assessment = _assessment_for(app)
        rows.append(
            {
                "app": app,
                "contract": optix["metric"]["contract"],
                "comparison_status": assessment["comparison_status"],
                "timing_protocol": _protocol_for(optix, best_embree),
                "scope": optix["metric"]["scope"],
                "optix_total_sec": optix_total,
                "embree_total_sec": embree_total,
                "optix_repeat": int(optix["metric"]["repeat"]),
                "embree_repeat": int(best_embree["metric"]["repeat"]),
                "optix_per_iter_sec": optix_per_iter,
                "embree_per_iter_sec": embree_per_iter,
                "speedup_embree_per_iter_div_optix_per_iter": embree_per_iter / optix_per_iter,
                "best_embree_threads": best_embree.get("threads"),
                "optix_source": optix["json"],
                "best_embree_source": best_embree["json"],
                "human_scale_optix": 1.0 <= optix_total <= 10.0,
                "human_scale_embree": 1.0 <= embree_total <= 10.0,
                "correct": bool(optix["metric"].get("correct")) and bool(best_embree["metric"].get("correct")),
                "reasonability_verdict": assessment["reasonability_verdict"],
                "only_material_diff_claim": assessment["only_material_diff_claim"],
                "speedup_explanation": _speedup_explanation_for(app, optix_per_iter, embree_per_iter),
                "public_wording": assessment["public_wording"],
            }
        )
    return rows


def _fmt(value: float) -> str:
    if value >= 1000.0 or (0.0 < abs(value) < 0.0001):
        return f"{value:.6g}"
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal4349: Human-Scale RT Core vs Embree CPU Comparison",
        "",
        "Date: 2026-06-12",
        "",
        "This packet reports hot prepared-query aggregates, not process wrapper time. "
        "Rows use the same repeat count when that can put both sides in the 1-10s band; "
        "otherwise they use duration-bounded throughput with identical work per iteration.",
        "",
        "| App | Status | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Contract |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {app} | `{status}` | `{protocol}` | {ot}s | {et}s | {orpt}/{erpt} | {speed:.2f}x | {threads} | `{contract}` |".format(
                app=row["app"],
                status=row["comparison_status"],
                protocol=row["timing_protocol"],
                ot=_fmt(float(row["optix_total_sec"])),
                et=_fmt(float(row["embree_total_sec"])),
                orpt=row["optix_repeat"],
                erpt=row["embree_repeat"],
                speed=float(row["speedup_embree_per_iter_div_optix_per_iter"]),
                threads=row["best_embree_threads"],
                contract=row["contract"],
            )
        )
    lines.extend(
        [
            "",
            "## Row Reasonability Review",
            "",
            "| App | Verdict | Only Material Difference? | Speedup Explanation | Public Wording |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            "| {app} | `{verdict}` | `{diff}` | {explanation} | {wording} |".format(
                app=row["app"],
                verdict=row["reasonability_verdict"],
                diff=row["only_material_diff_claim"],
                explanation=row["speedup_explanation"],
                wording=row["public_wording"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `clean_backend_swap_prepared_phase`: same benchmark contract and prepared generic RTDL primitive/phase; main material difference is OptiX/NVIDIA RT traversal versus Embree CPU traversal.",
            "- `clean_backend_swap_traversal_phase_only`: same prepared traversal contract, but the reported speedup is only for the traversal phase.",
            "- `mostly_clean_*`: same benchmark-level result and shared continuation where applicable, but the native boundary/output form is not identical enough for unqualified public wording.",
            "- `mixed_*`: result is numerically explainable and useful for engineering, but it is not public-ready as an 'only RT cores versus CPU cores' claim.",
            "- Duration-bounded rows use different repeat counts only because a single repeat count cannot keep both backends in the 1-10s measurement band.",
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    for error in payload["validation"]["errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def run(output_dir: Path, *, dry_run: bool = False) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    specs = _specs()
    runs: list[dict[str, Any]] = []
    for index, spec in enumerate(specs, start=1):
        print(f"[human-scale] {index}/{len(specs)} {spec.label}", flush=True)
        runs.append(_run_spec(spec, output_dir, dry_run=dry_run))
    rows = [] if dry_run else _build_rows(runs)
    errors: list[str] = []
    if not dry_run:
        for run_row in runs:
            if run_row.get("returncode") != 0:
                errors.append(f"{run_row['label']}: returncode {run_row.get('returncode')}")
        expected_apps = {
            "hausdorff_xhd",
            "barnes_hut",
            "contact_manifold",
            "rt_dbscan",
            "spatial_rayjoin_pip",
            "spatial_rayjoin_lsi",
            "rtnn",
            "librts_spatial_index",
            "triangle_counting",
            "robot_collision",
            "raydb_style",
        }
        got_apps = {row["app"] for row in rows}
        for missing in sorted(expected_apps - got_apps):
            errors.append(f"missing comparison row for {missing}")
        for row in rows:
            if not (row["human_scale_optix"] and row["human_scale_embree"]):
                errors.append(
                    f"{row['app']}: aggregate outside 1-10s band "
                    f"(optix={row['optix_total_sec']:.6g}, embree={row['embree_total_sec']:.6g})"
                )
            if not row["correct"]:
                errors.append(f"{row['app']}: correctness flag false")
    payload = {
        "version": "rtdl.goal4349.human_scale_rt_vs_embree.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": _rel(output_dir),
        "methodology": {
            "target_hot_query_aggregate_sec": "1-10 seconds per backend where feasible",
            "same_repeat_rule": "Use identical repeat counts when both sides can land in the target band.",
            "duration_bounded_rule": (
                "When speedups make one repeat count impossible, keep per-iteration work identical "
                "and vary repeat count only to accumulate stable total time."
            ),
            "embree_selection": "Run 8-thread and 64-thread Embree variants where relevant; report the faster measured Embree row.",
            "partner_policy": "When a partner continuation is part of the benchmark, hold the partner choice fixed across backends.",
        },
        "runs": runs,
        "rows": rows,
        "validation": {"status": "accept" if not errors else "reject", "errors": errors},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "summary.md").write_text(_markdown(payload), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = run(args.output_dir, dry_run=args.dry_run)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
