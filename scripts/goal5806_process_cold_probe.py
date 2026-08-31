#!/usr/bin/env python3
"""Unregistered fresh-process timing probe for matched RTDL/PyOptiX arms.

This diagnostic complements, and never replaces, the frozen post-import
Goal5802 regimes.  The parent measures from process creation through one exact
execution and close.  Every child receives a private, disabled CUDA/OptiX cache
root so compiler-cache state cannot leak between arms or blocks.  A fixed-size
marker ends the parent clock immediately after ``close``; output hashing,
audit serialization, and process teardown happen after that marker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _measure(callable_):
    start = time.perf_counter_ns()
    value = callable_()
    return value, time.perf_counter_ns() - start


def _child(args: argparse.Namespace) -> int:
    from experiments.goal5802_premeasurement.workload import (
        RELATION_TASK,
        TRIANGLE_TASK,
        relation_workload,
        triangle_workload,
    )

    task = RELATION_TASK if args.task == "relation" else TRIANGLE_TASK
    workload = relation_workload() if args.task == "relation" else triangle_workload()
    phase_start = time.perf_counter_ns()
    if args.arm == "rtdl":
        from experiments.goal5802_premeasurement.rtdlexe_arm import (
            RTDLDeploymentPaths,
            RTDLExecutableAdapter,
            preload_rtdl_runtime,
        )

        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        candidate = manifest["candidates"][args.task]
        (runtime_parts, preload_ns) = _measure(preload_rtdl_runtime)
        runtime, implementation, preload_receipt = runtime_parts
        adapter = RTDLExecutableAdapter(
            task,
            workload,
            RTDLDeploymentPaths(
                artifact=Path(candidate["artifact_path"]),
                authority=Path(candidate["authority_path"]),
                trust_root=args.trust_root,
                trust_head=args.trust_head,
                trust_package=args.trust_package,
                native_library=args.native,
                deployment_id=candidate["deployment_id"],
            ),
            preloaded_runtime=runtime,
            preloaded_implementation=implementation,
            runtime_preload_receipt=preload_receipt,
        )
    else:
        from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
            PyOptixScalarAdapter,
            preload_pyoptix_runtime,
        )

        (runtime_parts, preload_ns) = _measure(preload_pyoptix_runtime)
        baseline, preload_receipt = runtime_parts
        adapter = PyOptixScalarAdapter(
            task,
            workload,
            ptx_path=args.ptx,
            compaction_cubin_path=(args.compaction_cubin if args.task == "relation" else None),
            preloaded_runtime=baseline,
            runtime_preload_receipt=preload_receipt,
        )
    _, load_ns = _measure(adapter.load)
    _, prepare_ns = _measure(adapter.prepare)
    result, execute_ns = _measure(adapter.execute)
    _, close_ns = _measure(adapter.close)
    child_total_ns = time.perf_counter_ns() - phase_start
    # This constant marker is the only child output inside the parent timer.
    # Keep all evidence materialization below it so output cardinality cannot
    # charge one arm more than another.
    print("GOAL5806_BOUNDARY", flush=True)
    lifecycle = adapter.measurement_lifecycle_receipt(result)
    if args.task == "relation":
        visible_output = result.output
        output_count = len(visible_output)
    elif args.arm == "rtdl":
        visible_output = int(result.output)
        output_count = 1
    else:
        visible_output = int(result.reduced_u64)
        output_count = 1
    if args.arm == "rtdl":
        status_ok = result.device_status.get("ok") is True
    else:
        status_ok = int(result.device_status) == 0
    output_sha256 = hashlib.sha256(_canonical(visible_output)).hexdigest()
    output = {
        "schema": "rtdl.goal5806.process_cold_child.v2",
        "registered_performance_timing_count": 0,
        "scientific_claim_authorized": False,
        "arm": args.arm,
        "task": args.task,
        "preload_ns": preload_ns,
        "load_ns": load_ns,
        "prepare_ns": prepare_ns,
        "execute_ns": execute_ns,
        "close_ns": close_ns,
        "child_measured_total_ns": child_total_ns,
        "lifecycle": lifecycle,
        "status_ok": status_ok,
        "output_count": output_count,
        "output_sha256": output_sha256,
    }
    print(_canonical(output).decode("ascii"))
    return 0


def _required_paths(args: argparse.Namespace) -> None:
    common = (args.manifest, args.trust_root, args.trust_head,
              args.trust_package, args.native, args.ptx, args.compaction_cubin)
    if any(path is None for path in common):
        raise ValueError("matrix requires all RTDL and PyOptiX product paths")
    for path in common:
        path.resolve(strict=True)


def _matrix(args: argparse.Namespace) -> int:
    _required_paths(args)
    if args.blocks < 3:
        raise ValueError("matrix requires at least three ABBA blocks")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).resolve(strict=True)
    rows: list[dict[str, object]] = []
    base_paths = [
        "--manifest", str(args.manifest.resolve()),
        "--trust-root", str(args.trust_root.resolve()),
        "--trust-head", str(args.trust_head.resolve()),
        "--trust-package", str(args.trust_package.resolve()),
        "--native", str(args.native.resolve()),
        "--ptx", str(args.ptx.resolve()),
        "--compaction-cubin", str(args.compaction_cubin.resolve()),
    ]
    for task in ("relation", "triangle"):
        for block in range(args.blocks):
            order = ("rtdl", "pyoptix") if block % 2 == 0 else ("pyoptix", "rtdl")
            for position, arm in enumerate(order):
                stem = f"{task}_b{block}_p{position}_{arm}"
                cache = output / f"cache_{stem}"
                for name in ("cuda", "cupy", "optix", "xdg"):
                    (cache / name).mkdir(parents=True, exist_ok=False)
                env = dict(os.environ)
                env.update({
                    "PYTHONHASHSEED": "0",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "CUDA_CACHE_PATH": str(cache / "cuda"),
                    "CUDA_CACHE_DISABLE": "1",
                    "CUPY_CACHE_DIR": str(cache / "cupy"),
                    "OPTIX_CACHE_PATH": str(cache / "optix"),
                    "OPTIX_CACHE_ENABLED": "0",
                    "OPTIX_CACHE_MAXSIZE": "0",
                    "XDG_CACHE_HOME": str(cache / "xdg"),
                })
                command = [sys.executable, str(script), "child", "--arm", arm,
                           "--task", task, *base_paths]
                start = time.perf_counter_ns()
                process = subprocess.Popen(
                    command, env=env, text=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, bufsize=1)
                assert process.stdout is not None and process.stderr is not None
                marker = process.stdout.readline()
                parent_boundary_ns = time.perf_counter_ns() - start
                stdout_tail = process.stdout.read()
                stderr = process.stderr.read()
                returncode = process.wait()
                raw = {
                    "schema": "rtdl.goal5806.process_cold_parent_row.v2",
                    "registered_performance_timing_count": 0,
                    "scientific_claim_authorized": False,
                    "task": task,
                    "block": block,
                    "position": position,
                    "arm": arm,
                    "parent_boundary_ns": parent_boundary_ns,
                    "boundary_marker": marker.rstrip("\n"),
                    "returncode": returncode,
                    "stderr": stderr,
                }
                if returncode != 0 or marker != "GOAL5806_BOUNDARY\n":
                    raw["stdout_tail"] = stdout_tail
                    row_path = output / f"{stem}.json"
                    row_path.write_bytes(_canonical(raw) + b"\n")
                    raise RuntimeError(f"process-cold child failed: {stem}")
                child = json.loads(stdout_tail)
                raw["child"] = child
                row_path = output / f"{stem}.json"
                row_path.write_bytes(_canonical(raw) + b"\n")
                rows.append(raw)
            print(f"{task} block {block} complete", flush=True)
    groups: dict[str, object] = {}
    for task in ("relation", "triangle"):
        groups[task] = {}
        for arm in ("rtdl", "pyoptix"):
            selected = [r for r in rows if r["task"] == task and r["arm"] == arm]
            groups[task][arm] = {
                "count": len(selected),
                "parent_boundary_median_ns": int(statistics.median(
                    int(r["parent_boundary_ns"]) for r in selected)),
                "parent_boundary_min_ns": min(
                    int(r["parent_boundary_ns"]) for r in selected),
                "parent_boundary_max_ns": max(
                    int(r["parent_boundary_ns"]) for r in selected),
            }
        groups[task]["rtdl_over_pyoptix"] = (
            groups[task]["rtdl"]["parent_boundary_median_ns"]
            / groups[task]["pyoptix"]["parent_boundary_median_ns"])
    summary = {
        "schema": "rtdl.goal5806.process_cold_matrix.v2",
        "registered_performance_timing_count": 0,
        "scientific_claim_authorized": False,
        "regime": (
            "FRESH_PROCESS_TO_ONE_EXACT_OUTPUT_CLOSE_AND_FIXED_MARKER__"
            "DIAGNOSTIC_ONLY"),
        "blocks": args.blocks,
        "row_count": len(rows),
        "cache_policy": {
            "CUDA_CACHE_DISABLE": "1",
            "OPTIX_CACHE_ENABLED": "0",
            "OPTIX_CACHE_MAXSIZE": "0",
            "private_cache_root_per_child": True,
        },
        "inputs": {
            "script_sha256": _sha(script),
            "manifest_sha256": _sha(args.manifest),
            "trust_root_sha256": _sha(args.trust_root),
            "trust_head_sha256": _sha(args.trust_head),
            "trust_package_sha256": _sha(args.trust_package),
            "native_sha256": _sha(args.native),
            "ptx_sha256": _sha(args.ptx),
            "compaction_cubin_sha256": _sha(args.compaction_cubin),
        },
        "groups": groups,
    }
    (output / "summary.json").write_bytes(_canonical(summary) + b"\n")
    print(_canonical(summary).decode("ascii"))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("child", "matrix"):
        command = commands.add_parser(name)
        command.add_argument("--manifest", type=Path, required=True)
        command.add_argument("--trust-root", type=Path, required=True)
        command.add_argument("--trust-head", type=Path, required=True)
        command.add_argument("--trust-package", type=Path, required=True)
        command.add_argument("--native", type=Path, required=True)
        command.add_argument("--ptx", type=Path, required=True)
        command.add_argument("--compaction-cubin", type=Path, required=True)
    child = commands.choices["child"]
    child.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    child.add_argument("--task", choices=("relation", "triangle"), required=True)
    matrix = commands.choices["matrix"]
    matrix.add_argument("--blocks", type=int, default=8)
    matrix.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    return _child(args) if args.command == "child" else _matrix(args)


if __name__ == "__main__":
    raise SystemExit(main())
