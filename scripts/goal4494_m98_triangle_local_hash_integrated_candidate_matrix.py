from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time


PACKET_VERSION = "rtdl.v3_0.triangle_local_hash_integrated_candidate.goal4494.v1"
OUT_DIR = Path("docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17")
OUT_JSON = Path("docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4494_v3_0_m98_triangle_local_hash_integrated_candidate_2026-06-17.jsonl")
APP = Path("examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py")
DATASETS = {
    "com_lj": {
        "edge_file": "build/goal2593_snap_edges/com-lj.edge",
        "expected": 177_820_130,
        "mode": "rt_graph_2a1_segmented_generic_rt",
    },
    "soc_livejournal1": {
        "edge_file": "build/goal2593_snap_edges/soc-LiveJournal1.edge",
        "expected": 285_730_264,
        "mode": "rt_graph_2a1_segmented_scene_generic_rt",
    },
    "com_orkut": {
        "edge_file": "build/goal2593_snap_edges/com-orkut.edge",
        "expected": 627_584_181,
        "mode": "rt_graph_2a1_segmented_scene_generic_rt",
    },
}
BUILDERS = ("numba_direct_sort_rle", "numba_direct_sort_rle_local_hash_2048")


def _numba_env() -> dict[str, str]:
    env = os.environ.copy()
    prefix = env.get("NUMBA_CUDA_PREFIX", "/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc")
    env["NUMBA_CUDA_PREFIX"] = prefix
    env["CUDA_HOME"] = prefix
    env["CUDA_PATH"] = prefix
    env["NUMBA_CUDA_DRIVER"] = env.get("NUMBA_CUDA_DRIVER", "/lib/x86_64-linux-gnu/libcuda.so.1")
    env["PATH"] = f"{prefix}/bin:/usr/local/cuda-12/bin:{env.get('PATH', '')}"
    env["LD_LIBRARY_PATH"] = (
        f"{prefix}/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:"
        f"/usr/local/cuda-12/lib64:{env.get('LD_LIBRARY_PATH', '')}"
    )
    env["PYTHONPATH"] = "src:."
    return env


def _gpu_info() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _ptxas_version(env: dict[str, str]) -> str:
    try:
        return subprocess.check_output(["ptxas", "--version"], env=env, text=True).strip().splitlines()[-1]
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _run_case(dataset: str, config: dict[str, object], builder: str, env: dict[str, str]) -> dict[str, object]:
    raw_name = f"{dataset}_{builder}.json"
    stdout_name = f"{dataset}_{builder}.stdout.txt"
    stderr_name = f"{dataset}_{builder}.stderr.txt"
    cmd = [
        sys.executable,
        str(APP),
        "--mode",
        str(config["mode"]),
        "--edge-file",
        str(config["edge_file"]),
        "--edge-format",
        "binary",
        "--backend",
        "optix",
        "--detail",
        "summary",
        "--partner",
        "cupy",
        "--segment-max-two-hop-rows",
        "15000000",
        "--scene-max-directed-edges",
        "2000000",
        "--segment-ray-representation",
        "unique_weighted",
        "--segment-query-schedule",
        "prepared_segment_replay",
        "--segment-unique-key-builder",
        builder,
        "--warmup",
        "0",
        "--repeat",
        "1",
        "--segment-ray-build-telemetry",
        "sync_subphases",
    ]
    started = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=900)
    wall_sec = time.perf_counter() - started
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / stdout_name).write_text(proc.stdout, encoding="utf-8")
    (OUT_DIR / stderr_name).write_text(proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        return {
            "status": "error",
            "dataset": dataset,
            "builder": builder,
            "returncode": proc.returncode,
            "wall_sec": wall_sec,
            "stdout_file": str(OUT_DIR / stdout_name),
            "stderr_file": str(OUT_DIR / stderr_name),
        }
    payload = json.loads(proc.stdout)
    (OUT_DIR / raw_name).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    timing = payload["timing_ms"]
    phase_summary = timing.get("segment_ray_build_phase_summary_ms", {})
    phases = phase_summary.get("phases", {})
    observed = int(payload["generic_rt_weighted_triangle_count"])
    expected = int(config["expected"])
    row = {
        "status": "ok",
        "dataset": dataset,
        "builder": builder,
        "mode": payload["mode"],
        "edge_file": config["edge_file"],
        "expected_triangle_count": expected,
        "observed_triangle_count": observed,
        "count_matches_expected": observed == expected,
        "wall_sec": wall_sec,
        "raw_payload_file": str(OUT_DIR / raw_name),
        "stdout_file": str(OUT_DIR / stdout_name),
        "stderr_file": str(OUT_DIR / stderr_name),
        "segment_count": payload["segmentation"].get(
            "segment_count",
            payload["segmentation"].get("ray_segment_count"),
        ),
        "scene_count": payload["segmentation"].get("scene_count"),
        "logical_ray_count": payload["logical_ray_count"],
        "lowered_ray_count": payload["ray_count"],
        "run_backend_ms": timing["run_backend"],
        "total_ms": timing["total"],
        "segment_ray_build_total_ms": timing["segment_ray_build_total_ms"],
        "prepared_ray_batch_build_total_ms": timing.get("prepared_ray_batch_build_total_ms"),
        "prepare_scene_ms": timing.get("prepare_scene_ms", timing.get("prepare_scene_median_ms")),
        "prepare_scene_total_ms": timing.get("prepare_scene_total_ms"),
        "query_median_ms": timing["query_median_ms"],
        "phase_totals_ms": {
            name: phase.get("total_ms")
            for name, phase in phases.items()
            if name
            in {
                "cupy_sort_rle_counts",
                "numba_key_fill",
                "hybrid_local_hash_counts",
                "hybrid_large_sort_rle_counts",
                "hybrid_source_group_plan",
                "hybrid_unique_concat",
                "hybrid_unique_decode_weights",
                "ray_column_projection_full",
            }
        },
        "claim_boundary": {
            "candidate_only": True,
            "route_changed": False,
            "public_speedup_claim_authorized": False,
            "native_engine_customization": False,
            "app_specific_native_engine_callback": False,
        },
    }
    if not row["count_matches_expected"]:
        row["status"] = "mismatch"
    return row


def _comparison(rows: list[dict[str, object]]) -> dict[str, object]:
    by_key = {(row["dataset"], row["builder"]): row for row in rows if row["status"] == "ok"}
    comparisons = {}
    for dataset in DATASETS:
        base = by_key.get((dataset, "numba_direct_sort_rle"))
        hybrid = by_key.get((dataset, "numba_direct_sort_rle_local_hash_2048"))
        if not base or not hybrid:
            continue
        comparisons[dataset] = {
            "count_matches": bool(base["count_matches_expected"] and hybrid["count_matches_expected"]),
            "baseline_total_ms": base["total_ms"],
            "hybrid_total_ms": hybrid["total_ms"],
            "baseline_run_backend_ms": base["run_backend_ms"],
            "hybrid_run_backend_ms": hybrid["run_backend_ms"],
            "baseline_segment_ray_build_ms": base["segment_ray_build_total_ms"],
            "hybrid_segment_ray_build_ms": hybrid["segment_ray_build_total_ms"],
            "baseline_over_hybrid_total": base["total_ms"] / hybrid["total_ms"],
            "baseline_over_hybrid_backend": base["run_backend_ms"] / hybrid["run_backend_ms"],
            "baseline_over_hybrid_segment_ray_build": (
                base["segment_ray_build_total_ms"] / hybrid["segment_ray_build_total_ms"]
            ),
            "decision": "reject_hybrid_candidate" if hybrid["run_backend_ms"] > base["run_backend_ms"] else "investigate",
        }
    return comparisons


def main() -> int:
    env = _numba_env()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    for dataset, config in DATASETS.items():
        for builder in BUILDERS:
            row = _run_case(dataset, config, builder, env)
            rows.append(row)
            with OUT_JSONL.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
            print(
                json.dumps(
                    {
                        "dataset": dataset,
                        "builder": builder,
                        "status": row["status"],
                        "run_backend_ms": row.get("run_backend_ms"),
                        "segment_ray_build_total_ms": row.get("segment_ray_build_total_ms"),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    comparisons = _comparison(rows)
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4494 / V3 M98",
        "case_count": len(rows),
        "ok_count": sum(1 for row in rows if row["status"] == "ok"),
        "hardware": _gpu_info(),
        "ptxas_version": _ptxas_version(env),
        "parameters": {
            "warmup": 0,
            "repeat": 1,
            "segment_max_two_hop_rows": 15_000_000,
            "scene_max_directed_edges": 2_000_000,
            "builders": BUILDERS,
        },
        "summary": {
            "all_counts_match": all(bool(row.get("count_matches_expected")) for row in rows if row["status"] == "ok"),
            "comparisons": comparisons,
        },
        "decision": (
            "The integrated local-hash candidate is explicit and correct when rows pass, "
            "but it is rejected unless it beats the current numba_direct_sort_rle route "
            "on run_backend_ms and segment_ray_build_total_ms."
        ),
        "claim_boundary": {
            "internal_candidate_matrix": True,
            "route_changed": False,
            "public_speedup_claim_authorized": False,
            "native_engine_customization": False,
            "app_specific_native_engine_callback": False,
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
