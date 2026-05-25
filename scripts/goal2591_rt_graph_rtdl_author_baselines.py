from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as app,
)


AUTHOR_RT_TC = ROOT / "scratch" / "external" / "RT-Graph" / "tc" / "bin" / "rt_tc"
AUTHOR_BS_TC = ROOT / "scratch" / "external" / "RT-Graph" / "tc" / "bin" / "bs_tc"


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _run(command: list[str], *, env: dict[str, str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    return completed.stdout + completed.stderr


def _float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def _author_rt_tc_once(edge_file: Path, env: dict[str, str]) -> dict[str, object]:
    output = _run([str(AUTHOR_RT_TC), str(edge_file), "0"], env=env)
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
    }


def _author_bs_tc_once(edge_file: Path, env: dict[str, str]) -> dict[str, object]:
    output = _run([str(AUTHOR_BS_TC), str(edge_file), "0"], env=env)
    tc_pre = _float(r"TC Preprocessing Time = ([0-9.]+) ms", output)
    csr = _float(r"CSR converting time = ([0-9.]+) ms", output)
    gpu_pre = _float(r"BSTC: preprocessing time = ([0-9.]+) ms", output)
    counting = _float(r"BSTC: counting time = ([0-9.]+) ms", output)
    triangle_count = _int(r"counting result = ([0-9]+)", output)
    pipeline = sum(value or 0.0 for value in (tc_pre, csr, gpu_pre, counting))
    return {
        "triangle_count": triangle_count,
        "tc_preprocessing_ms": tc_pre,
        "csr_ms": csr,
        "gpu_preprocessing_ms": gpu_pre,
        "counting_ms": counting,
        "pipeline_excluding_file_read_ms": pipeline,
    }


def _summarize_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    keys = [key for key, value in runs[0].items() if isinstance(value, (int, float))]
    summary: dict[str, object] = {"runs": runs}
    for key in keys:
        values = [float(run[key]) for run in runs if run[key] is not None]
        if values:
            summary[f"median_{key}"] = _median(values)
    return summary


def _rtdl_once(mode: str, edge_file: Path) -> dict[str, object]:
    payload = app.run_app(
        mode=mode,
        edge_file=str(edge_file),
        edge_format="binary",
        backend="optix",
        detail="summary",
        partner="cupy",
    )
    result = {
        "matches": bool(payload["triangle_count_matches_oracle"]),
        "oracle_triangle_count": int(payload["oracle_triangle_count"]),
        "primitive_count": int(payload["primitive_count"]),
        "ray_count": int(payload["ray_count"]),
        "total_ms": float(payload["timing_ms"]["total"]),
        "build_contract_ms": float(payload["timing_ms"]["build_contract"]),
        "build_geometry_ms": float(payload["timing_ms"]["build_geometry"]),
        "run_backend_ms": float(payload["timing_ms"]["run_backend"]),
        "native_traversal_ms": float(payload["generic_rt_summary"]["phase_timing_seconds"]["traversal"]) * 1000.0,
    }
    if mode == "rt_graph_2a1_generic_rt":
        result["triangle_count"] = int(payload["generic_rt_weighted_triangle_count"])
    else:
        result["triangle_count"] = int(payload["generic_rt_triangle_count"])
    return result


def run_suite(inputs: list[tuple[str, Path]], *, repeats: int, warmup: int) -> dict[str, object]:
    env = os.environ.copy()
    cuda_paths = ["/usr/local/cuda-12.8/compat", "/usr/local/cuda-12.8/lib64"]
    env["LD_LIBRARY_PATH"] = ":".join(cuda_paths + [env.get("LD_LIBRARY_PATH", "")])
    results: dict[str, object] = {}
    for name, edge_file in inputs:
        measured = max(1, repeats - warmup)
        rtdl_2a1 = [_rtdl_once("rt_graph_2a1_generic_rt", edge_file) for _ in range(repeats)][warmup:]
        rtdl_1a2 = [_rtdl_once("rt_graph_1a2_generic_rt", edge_file) for _ in range(repeats)][warmup:]
        author_rt = [_author_rt_tc_once(edge_file, env) for _ in range(repeats)][warmup:]
        author_bs = [_author_bs_tc_once(edge_file, env) for _ in range(repeats)][warmup:]
        results[name] = {
            "input_file": str(edge_file),
            "repeats": repeats,
            "warmup": warmup,
            "measured_runs": measured,
            "rtdl_cupy_2a1": _summarize_runs(rtdl_2a1),
            "rtdl_cupy_1a2": _summarize_runs(rtdl_1a2),
            "authors_rt_tc": _summarize_runs(author_rt),
            "authors_bs_tc_gpu": _summarize_runs(author_bs),
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare RTDL RT-Graph with authors' rt_tc and bs_tc.")
    parser.add_argument("--input", action="append", nargs=2, metavar=("NAME", "EDGE_FILE"), required=True)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    results = run_suite(
        [(name, Path(edge_file)) for name, edge_file in args.input],
        repeats=args.repeats,
        warmup=args.warmup,
    )
    payload = json.dumps(results, indent=2, sort_keys=True)
    print(payload)
    if args.json_out:
        Path(args.json_out).write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
