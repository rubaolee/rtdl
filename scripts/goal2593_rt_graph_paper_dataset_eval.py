from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as app,
)
from scripts import goal2592_rt_graph_cugraph_baseline as cugraph_baseline  # noqa: E402


AUTHOR_RT_TC = ROOT / "scratch" / "external" / "RT-Graph" / "tc" / "bin" / "rt_tc"
AUTHOR_BS_TC = ROOT / "scratch" / "external" / "RT-Graph" / "tc" / "bin" / "bs_tc"


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _summary(runs: list[dict[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {"runs": runs}
    if not runs:
        return payload
    numeric_keys = [key for key, value in runs[0].items() if isinstance(value, (int, float, bool))]
    for key in numeric_keys:
        values = [float(run[key]) for run in runs if run.get(key) is not None]
        if values:
            payload[f"median_{key}"] = _median(values)
    return payload


def _run_subprocess(command: list[str], *, env: dict[str, str], timeout: int) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    return completed.stdout + completed.stderr


def _float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def _author_once(binary: Path, edge_file: Path, *, env: dict[str, str], timeout: int) -> dict[str, object]:
    started = time.perf_counter()
    output = _run_subprocess([str(binary), str(edge_file), "0"], env=env, timeout=timeout)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if binary.name == "rt_tc":
        tc_pre = _float(r"TC Preprocessing Time = ([0-9.]+) ms", output)
        csr = _float(r"CSR converting time = ([0-9.]+) ms", output)
        convert = _float(r"RTTC: time of converting graph to RT = ([0-9.]+) ms", output)
        rays = _float(r"RTTC: Time of computing rays = ([0-9.]+) ms", output)
        bvh = _float(r"BVH Building Time = ([0-9.]+) ms", output)
        count = _float(r"Counting Time = ([0-9.]+) ms", output)
        triangle_count = _int(r"Triangle Counting = ([0-9]+)", output)
        pipeline = sum(value or 0.0 for value in (tc_pre, csr, convert, rays, bvh, count))
        return {
            "triangle_count": triangle_count,
            "tc_preprocessing_ms": tc_pre,
            "csr_ms": csr,
            "convert_graph_to_rt_ms": convert,
            "compute_rays_ms": rays,
            "bvh_build_ms": bvh,
            "counting_ms": count,
            "pipeline_excluding_file_read_ms": pipeline,
            "subprocess_wall_ms": elapsed_ms,
        }
    tc_pre = _float(r"TC Preprocessing Time = ([0-9.]+) ms", output)
    csr = _float(r"CSR converting time = ([0-9.]+) ms", output)
    gpu_pre = _float(r"BSTC: preprocessing time = ([0-9.]+) ms", output)
    count = _float(r"BSTC: counting time = ([0-9.]+) ms", output)
    triangle_count = _int(r"counting result = ([0-9]+)", output)
    pipeline = sum(value or 0.0 for value in (tc_pre, csr, gpu_pre, count))
    return {
        "triangle_count": triangle_count,
        "tc_preprocessing_ms": tc_pre,
        "csr_ms": csr,
        "gpu_preprocessing_ms": gpu_pre,
        "counting_ms": count,
        "pipeline_excluding_file_read_ms": pipeline,
        "subprocess_wall_ms": elapsed_ms,
    }


def _rtdl_once(mode: str, edge_file: Path) -> dict[str, object]:
    payload = app.run_app(
        mode=mode,
        edge_file=str(edge_file),
        edge_format="binary",
        backend="optix",
        detail="summary",
        partner="cupy",
    )
    key = "generic_rt_weighted_triangle_count" if mode == "rt_graph_2a1_generic_rt" else "generic_rt_triangle_count"
    return {
        "triangle_count": int(payload[key]),
        "matches_oracle": bool(payload["triangle_count_matches_oracle"]),
        "oracle_triangle_count": int(payload["oracle_triangle_count"]),
        "primitive_count": int(payload["primitive_count"]),
        "ray_count": int(payload["ray_count"]),
        "total_ms": float(payload["timing_ms"]["total"]),
        "build_contract_ms": float(payload["timing_ms"]["build_contract"]),
        "build_geometry_ms": float(payload["timing_ms"]["build_geometry"]),
        "run_backend_ms": float(payload["timing_ms"]["run_backend"]),
        "native_traversal_ms": float(payload["generic_rt_summary"]["phase_timing_seconds"]["traversal"]) * 1000.0,
    }


def _postgres_once(name: str, edge_file: Path, *, timeout: int) -> dict[str, object]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "goal2591_rt_graph_postgres_baseline.py"),
        "--input",
        name,
        str(edge_file),
        "--tmp-dir",
        "/tmp",
    ]
    output = _run_subprocess(command, env=os.environ.copy(), timeout=timeout)
    return json.loads(output)[name]


def _run_method(
    method: str,
    name: str,
    edge_file: Path,
    *,
    repeats: int,
    warmup: int,
    env: dict[str, str],
    timeout: int,
    postgres_timeout: int,
) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    started = time.perf_counter()
    try:
        for index in range(repeats):
            if method == "rtdl_2a1":
                run = _rtdl_once("rt_graph_2a1_generic_rt", edge_file)
            elif method == "rtdl_1a2":
                run = _rtdl_once("rt_graph_1a2_generic_rt", edge_file)
            elif method == "author_rt_tc":
                run = _author_once(AUTHOR_RT_TC, edge_file, env=env, timeout=timeout)
            elif method == "author_bs_tc":
                run = _author_once(AUTHOR_BS_TC, edge_file, env=env, timeout=timeout)
            elif method == "cugraph":
                run = cugraph_baseline._run_once(edge_file)  # noqa: SLF001
            elif method == "postgres":
                run = _postgres_once(name, edge_file, timeout=postgres_timeout)
            else:
                raise ValueError(f"unknown method: {method}")
            if index >= warmup:
                runs.append(run)
        return {
            "status": "ok",
            "repeats": repeats,
            "warmup": warmup,
            "measured_runs": len(runs),
            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            **_summary(runs),
        }
    except Exception as exc:  # pragma: no cover - evidence harness needs failure capture
        return {
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "completed_measured_runs": len(runs),
            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
            **_summary(runs),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RT-Graph paper-dataset TC baseline matrix.")
    parser.add_argument("--input", action="append", nargs=3, metavar=("NAME", "EDGE_FILE", "EXPECTED_TRIANGLES"), required=True)
    parser.add_argument("--method", action="append", default=None)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--postgres-timeout", type=int, default=7200)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    methods = args.method or ["rtdl_2a1", "rtdl_1a2", "author_rt_tc", "author_bs_tc", "cugraph"]
    env = os.environ.copy()
    cuda_paths = ["/usr/local/cuda-12.8/compat", "/usr/local/cuda-12.8/lib64"]
    env["LD_LIBRARY_PATH"] = ":".join(cuda_paths + [env.get("LD_LIBRARY_PATH", "")])

    payload: dict[str, object] = {
        "methods": methods,
        "repeats": args.repeats,
        "warmup": args.warmup,
        "results": {},
    }
    for name, edge_path, expected_text in args.input:
        edge_file = Path(edge_path)
        expected = int(expected_text)
        dataset_result: dict[str, object] = {
            "input_file": str(edge_file),
            "input_edges": edge_file.stat().st_size // 8,
            "expected_triangles": expected,
            "methods": {},
        }
        for method in methods:
            result = _run_method(
                method,
                name,
                edge_file,
                repeats=args.repeats,
                warmup=args.warmup,
                env=env,
                timeout=args.timeout,
                postgres_timeout=args.postgres_timeout,
            )
            median_count = result.get("median_triangle_count")
            if median_count is not None:
                result["matches_expected_triangles"] = int(median_count) == expected
            dataset_result["methods"][method] = result
            print(json.dumps({"dataset": name, "method": method, "result": result}, sort_keys=True), flush=True)
        payload["results"][name] = dataset_result

    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
