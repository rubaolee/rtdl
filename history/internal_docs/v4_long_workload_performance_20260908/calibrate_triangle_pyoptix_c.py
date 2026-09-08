#!/usr/bin/env python3
"""Run one diagnostic-only strong-PyOptiX RT-2A1 graph action."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--dataset", choices=("com-dblp", "cit-Patents", "soc-LiveJournal1"),
        required=True,
    )
    parser.add_argument("--expected-triangle-count", type=int, required=True)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.max_relation_rows <= 0 or args.warmups < 0:
        raise ValueError("calibration counts must be nonnegative")
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "0":
        raise RuntimeError("calibration requires CUDA_VISIBLE_DEVICES=0")
    config = json.loads(args.config.read_text(encoding="utf-8"))

    from experiments.v4_paper_apps_pyoptix import inputs
    from experiments.v4_paper_apps_pyoptix.triangle_owner import (
        PublicPyOptixTriangleCountingOwner,
    )
    from scripts import v4_paper_apps_pyoptix_worker as worker

    load_started = time.perf_counter_ns()
    data = inputs.load_triangle(
        config["source_root"],
        config["data_root"],
        dataset=args.dataset,
        expected_triangle_count=args.expected_triangle_count,
    )
    load_ns = time.perf_counter_ns() - load_started
    prepare_started = time.perf_counter_ns()
    owner = PublicPyOptixTriangleCountingOwner.prepare(
        prebuilt_ptx=worker._prebuilt_ptx(config, "triangle_counting")
    )
    prepare_ns = time.perf_counter_ns() - prepare_started
    try:
        warmup_ns = []
        for _ in range(args.warmups):
            warmup_started = time.perf_counter_ns()
            warmup = owner.execute_graph(
                graph_contract=data["graph_contract"],
                segment_iterator=data["segment_iterator"],
                max_relation_rows=args.max_relation_rows,
            )
            warmup_ns.append(time.perf_counter_ns() - warmup_started)
            if warmup.get("matched") is not True:
                raise RuntimeError("strong-PyOptiX graph warmup output mismatch")
        execute_started = time.perf_counter_ns()
        result = owner.execute_graph(
        graph_contract=data["graph_contract"],
        segment_iterator=data["segment_iterator"],
        max_relation_rows=args.max_relation_rows,
        )
        execute_ns = time.perf_counter_ns() - execute_started
    finally:
        close_started = time.perf_counter_ns()
        owner.close()
        close_ns = time.perf_counter_ns() - close_started
    if result.get("matched") is not True:
        raise RuntimeError("strong-PyOptiX graph output mismatch")
    segments = result["segments"]
    output = {
        "schema": "rtdl.v4_long_workload.triangle_c_calibration.v1",
        "formal_evidence": False,
        "pooling_into_formal_transaction_forbidden": True,
        "source_commit": config["source_commit"],
        "source_tree": config["source_tree"],
        "config_sha256": _sha256(args.config),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "dataset": args.dataset,
        "edge_file": str(data["edge_file"]),
        "edge_file_sha256": data["edge_file_sha256"],
        "expected_triangle_count": args.expected_triangle_count,
        "observed_triangle_count": int(result["output"]["triangle_count"]),
        "max_relation_rows": args.max_relation_rows,
        "warmup_count": args.warmups,
        "warmup_ns": warmup_ns,
        "matched": True,
        "segment_count": len(segments),
        "total_segment_primitives": sum(
            int(row["primitive_count"]) for row in segments
        ),
        "total_segment_queries": sum(int(row["query_count"]) for row in segments),
        "maximum_segment_primitives": max(
            int(row["primitive_count"]) for row in segments
        ),
        "maximum_segment_queries": max(int(row["query_count"]) for row in segments),
        "segments": segments,
        "phase_ns": {
            "input_load_and_graph_contract": load_ns,
            "pyoptix_owner_prepare": prepare_ns,
            "single_natural_graph_action": execute_ns,
            "close": close_ns,
        },
        "machine": {
            "hostname": platform.node(),
            "python": platform.python_version(),
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "nvidia_smi": subprocess.run(
                [
                    "nvidia-smi", "-i", "0",
                    "--query-gpu=name,uuid,compute_cap,driver_version,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip(),
        },
    }
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "dataset": args.dataset,
                "single_natural_graph_action_ns": execute_ns,
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
