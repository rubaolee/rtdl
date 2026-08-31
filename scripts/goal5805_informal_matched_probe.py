#!/usr/bin/env python3
"""Unregistered same-host probe for the Goal5802 matched RTDL/PyOptiX arms."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK,
    TRIANGLE_TASK,
    relation_workload,
    triangle_workload,
)


def _measure(callable_):
    start = time.perf_counter_ns()
    value = callable_()
    return value, time.perf_counter_ns() - start


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument("--task", choices=("relation", "triangle"), required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--trust-root", type=Path)
    parser.add_argument("--trust-head", type=Path)
    parser.add_argument("--trust-package", type=Path)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--ptx", type=Path)
    parser.add_argument("--compaction-cubin", type=Path)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    parser.add_argument("--triangle-size", type=int)
    parser.add_argument(
        "--summary-only", action="store_true",
        help="omit the potentially large operation/output evidence from stdout")
    parser.add_argument(
        "--rtdl-layer",
        choices=("adapter", "matched", "prepared", "owner", "all"),
        default="adapter",
        help="diagnostic-only RTDL Python-layer decomposition")
    parser.add_argument(
        "--pyoptix-layer", choices=("adapter", "matched", "owner"),
        default="adapter",
        help="diagnostic-only PyOptiX Python-layer decomposition")
    args = parser.parse_args()
    if args.warmups < 1 or args.repetitions < 3:
        raise ValueError("probe requires positive warmups and at least three samples")
    if args.arm != "rtdl" and args.rtdl_layer != "adapter":
        raise ValueError("rtdl-layer is valid only for the RTDL arm")
    if args.arm != "pyoptix" and args.pyoptix_layer != "adapter":
        raise ValueError("pyoptix-layer is valid only for the PyOptiX arm")

    task = RELATION_TASK if args.task == "relation" else TRIANGLE_TASK
    workload = relation_workload() if args.task == "relation" else triangle_workload()
    if args.triangle_size is not None:
        if args.task != "triangle" or not 1 <= args.triangle_size <= len(workload["queries"]):
            raise ValueError("triangle-size is valid only for a nonempty triangle prefix")
        count = args.triangle_size
        workload = dict(workload)
        workload["vertices"] = workload["vertices"][:3 * count]
        workload["queries"] = workload["queries"][:count]
        workload["weights"] = workload["weights"][:count]
        workload["expected_reduced_u64"] = sum(workload["weights"])
    if args.arm == "rtdl":
        from experiments.goal5802_premeasurement.rtdlexe_arm import (
            RTDLDeploymentPaths,
            RTDLExecutableAdapter,
            preload_rtdl_runtime,
        )

        required = (args.manifest, args.trust_root, args.trust_head,
                    args.trust_package, args.native)
        if any(value is None for value in required):
            raise ValueError("RTDL probe paths are incomplete")
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        candidate = manifest["candidates"][args.task]
        runtime, implementation, preload = preload_rtdl_runtime()
        adapter = RTDLExecutableAdapter(
            task, workload,
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
            runtime_preload_receipt=preload,
        )
    else:
        from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
            PyOptixScalarAdapter,
            preload_pyoptix_runtime,
        )

        if args.ptx is None or (args.task == "relation" and args.compaction_cubin is None):
            raise ValueError("PyOptiX probe products are incomplete")
        baseline, preload = preload_pyoptix_runtime()
        adapter = PyOptixScalarAdapter(
            task, workload, ptx_path=args.ptx,
            compaction_cubin_path=(
                args.compaction_cubin if args.task == "relation" else None),
            preloaded_runtime=baseline, runtime_preload_receipt=preload,
        )

    _, load_ns = _measure(adapter.load)
    _, prepare_ns = _measure(adapter.prepare)
    if args.rtdl_layer == "all":
        executors = {
            "adapter": adapter.execute,
            "prepared": lambda: adapter.prepared.execute(adapter.batch),
            "owner": lambda: adapter.prepared._owner.execute(
                adapter.batch, diagnostics=False),
        }
        layer_results = {}
        last_adapter = None
        # Run in both directions so a one-way frequency or thermal trend
        # cannot masquerade as Python wrapper cost.
        for pass_index, names in enumerate((
                tuple(executors), tuple(reversed(tuple(executors))))):
            for name in names:
                callable_ = executors[name]
                for _ in range(args.warmups):
                    value = callable_()
                    if name == "adapter":
                        adapter.measurement_lifecycle_receipt(value)
                        last_adapter = value
                samples = []
                for _ in range(args.repetitions):
                    value, elapsed = _measure(callable_)
                    samples.append(elapsed)
                    if name == "adapter":
                        adapter.measurement_lifecycle_receipt(value)
                        last_adapter = value
                layer_results[f"{pass_index}:{name}"] = {
                    "median_ns": int(statistics.median(samples)),
                    "min_ns": min(samples),
                    "max_ns": max(samples),
                }
        assert last_adapter is not None
        evidence = adapter.finalize_measurement_evidence(last_adapter)
        adapter.close()
        print(json.dumps({
            "schema": "rtdl.goal5805.informal_layer_decomposition.v1",
            "registered_performance_timing_count": 0,
            "scientific_claim_authorized": False,
            "task": args.task,
            "load_ns": load_ns,
            "prepare_ns": prepare_ns,
            "warmups": args.warmups,
            "repetitions": args.repetitions,
            "layers": layer_results,
            "operation": evidence.get("native_operation_receipt", evidence),
        }, sort_keys=True))
        return 0
    execute = adapter.execute
    if args.arm == "rtdl" and args.rtdl_layer != "adapter":
        if args.rtdl_layer == "matched":
            execute = adapter.measurement_execution_callable()
        elif args.rtdl_layer == "prepared":
            execute = lambda: adapter.prepared.execute(adapter.batch)
        else:
            execute = lambda: adapter.prepared._owner.execute(
                adapter.batch, diagnostics=False)
    elif args.arm == "pyoptix" and args.pyoptix_layer != "adapter":
        execute = (
            adapter.measurement_execution_callable()
            if args.pyoptix_layer == "matched" else adapter.owner.execute)
    last = None
    for _ in range(args.warmups):
        last = execute()
        if args.rtdl_layer == "adapter":
            adapter.measurement_lifecycle_receipt(last)
    samples = []
    for _ in range(args.repetitions):
        last, elapsed = _measure(execute)
        samples.append(elapsed)
        if args.rtdl_layer == "adapter":
            adapter.measurement_lifecycle_receipt(last)
    assert last is not None
    evidence = (adapter.finalize_measurement_evidence(last)
                if args.rtdl_layer == "adapter" else {})
    adapter.close()
    result = {
        "schema": "rtdl.goal5805.informal_matched_probe.v1",
        "registered_performance_timing_count": 0,
        "scientific_claim_authorized": False,
        "arm": args.arm,
        "task": args.task,
        "rtdl_layer": args.rtdl_layer,
        "pyoptix_layer": args.pyoptix_layer,
        "triangle_size": args.triangle_size,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "load_ns": load_ns,
        "prepare_ns": prepare_ns,
        "steady_median_ns": int(statistics.median(samples)),
        "steady_min_ns": min(samples),
        "steady_max_ns": max(samples),
    }
    if not args.summary_only:
        result["operation"] = evidence.get("native_operation_receipt", evidence)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
