#!/usr/bin/env python3
"""Uninstrumented fresh-process wall-time diagnostic for one prepared arm.

This tool is development evidence only. It deliberately does not implement the
preregistered paired-block controller and its output must not be pooled into a
formal transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
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
        "--app", choices=("particle_tracking", "triangle_counting", "librts"),
        required=True,
    )
    parser.add_argument("--arm", choices=("v4", "pyoptix"), required=True)
    parser.add_argument("--operation", choices=("point_contains", "range_contains"))
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=32)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _source_identity(root: Path) -> dict[str, object]:
    def git(*arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments], cwd=root, check=True, text=True,
            capture_output=True,
        ).stdout.strip()

    return {
        "root": str(root),
        "commit": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "status": git("status", "--porcelain=v1", "--untracked-files=all"),
        "diff_sha256": hashlib.sha256(subprocess.run(
            ["git", "diff", "--binary"], cwd=root, check=True,
            capture_output=True,
        ).stdout).hexdigest(),
    }


def main() -> int:
    args = _parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.warmups < 0 or args.repetitions <= 0:
        raise ValueError("invalid diagnostic repetition count")
    root = args.source_root.resolve(strict=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    config = dict(config)
    config["source_root"] = str(root)

    from scripts import v4_paper_apps_pyoptix_worker as worker

    data, input_identity = worker._load_input(
        args.app, config, operation=args.operation)
    execute, close, method = worker._prepare_case(
        args.app, args.arm, config, data)
    samples: list[int] = []
    digests: list[str] = []
    try:
        for _ in range(args.warmups):
            observed = execute()
            if observed.get("matched") is not True:
                raise RuntimeError("diagnostic warmup output mismatch")
        for _ in range(args.repetitions):
            started = time.perf_counter_ns()
            observed = execute()
            samples.append(time.perf_counter_ns() - started)
            if observed.get("matched") is not True:
                raise RuntimeError("diagnostic execution output mismatch")
            digests.append(str(observed["output_sha256"]))
    finally:
        close()
    if len(set(digests)) != 1:
        raise RuntimeError("diagnostic output changed across repetitions")

    result = {
        "schema": "rtdl.v4_long_workload.prepared_wall_diagnostic.v1",
        "formal_evidence": False,
        "pooling_into_formal_transaction_forbidden": True,
        "app": args.app,
        "operation": args.operation,
        "arm": args.arm,
        "input_identity": input_identity,
        "method": method,
        "runtime_source_identity": _source_identity(root),
        "config_sha256": _sha256(args.config),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "samples_ns": samples,
        "median_ns": int(statistics.median(samples)),
        "minimum_ns": min(samples),
        "maximum_ns": max(samples),
        "output_sha256": digests[0],
        "notes": [
            "One fresh process owns exactly one arm.",
            "No profiler or nested timer instrumentation is installed.",
            "This is a diagnostic, not a preregistered paired-block result.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS", "arm": args.arm,
        "median_ns": result["median_ns"], "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
