#!/usr/bin/env python3
"""Diagnostic-only profiler for the retained V4 paper-application front doors.

The output from this script is not formal evidence and must never be pooled
with a preregistered transaction.  It exists to identify inclusive host-side
costs before changing executable code.
"""

from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import pstats
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wrap(
    owner: object,
    name: str,
    counters: dict[str, dict[str, int]],
    *,
    label: str | None = None,
) -> None:
    original = getattr(owner, name)
    counter_name = label or f"{getattr(owner, '__name__', type(owner).__name__)}.{name}"

    def measured(*args: object, **kwargs: object) -> object:
        started = time.perf_counter_ns()
        try:
            return original(*args, **kwargs)
        finally:
            row = counters[counter_name]
            row["calls"] += 1
            row["inclusive_ns"] += time.perf_counter_ns() - started

    setattr(owner, name, measured)


def _install_instrumentation() -> dict[str, dict[str, int]]:
    from rtdsl import physical_execution_provenance as provenance

    counters: dict[str, dict[str, int]] = defaultdict(
        lambda: {"calls": 0, "inclusive_ns": 0}
    )

    original_resolve = Path.resolve

    def measured_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        started = time.perf_counter_ns()
        try:
            return original_resolve(self, *args, **kwargs)
        finally:
            row = counters["pathlib.Path.resolve"]
            row["calls"] += 1
            row["inclusive_ns"] += time.perf_counter_ns() - started

    Path.resolve = measured_resolve  # type: ignore[method-assign]
    for name in (
        "_registered_loaded_provider_identity",
        "_loaded_provider_sha256",
        "_captured_snapshot_items",
        "_classify_snapshot",
        "captured_traversal_observation_from_snapshot",
    ):
        _wrap(provenance, name, counters, label=f"provenance.{name}")
    _wrap(
        provenance.CapturedTraversalObservation,
        "build_receipt",
        counters,
        label="provenance.CapturedTraversalObservation.build_receipt",
    )

    original_open = provenance.OptixTraversalAuditSession.open.__func__

    def measured_open(cls: type, *args: object, **kwargs: object) -> object:
        started = time.perf_counter_ns()
        try:
            return original_open(cls, *args, **kwargs)
        finally:
            row = counters["provenance.OptixTraversalAuditSession.open"]
            row["calls"] += 1
            row["inclusive_ns"] += time.perf_counter_ns() - started

    provenance.OptixTraversalAuditSession.open = classmethod(measured_open)
    for name in ("capture", "finish"):
        _wrap(
            provenance.OptixTraversalAuditSession,
            name,
            counters,
            label=f"provenance.OptixTraversalAuditSession.{name}",
        )
    return counters


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--app", choices=("particle_tracking", "triangle_counting", "librts"),
        required=True,
    )
    parser.add_argument("--operation", choices=("point_contains", "range_contains"))
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile-output", type=Path, required=True)
    parser.add_argument("--profile-text", type=Path, required=True)
    parser.add_argument("--source-root", type=Path)
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
        "diff_sha256": hashlib.sha256(
            subprocess.run(
                ["git", "diff", "--binary"], cwd=root, check=True,
                capture_output=True,
            ).stdout
        ).hexdigest(),
    }


def main() -> int:
    args = _parse_args()
    for path in (args.output, args.profile_output, args.profile_text):
        if path.exists():
            raise FileExistsError(path)
    if args.repetitions <= 0 or args.warmups < 0:
        raise ValueError("invalid diagnostic repetition count")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    source_root = (
        Path(config["source_root"]).resolve(strict=True)
        if args.source_root is None
        else args.source_root.resolve(strict=True)
    )
    config = dict(config)
    config["source_root"] = str(source_root)
    from scripts import v4_paper_apps_pyoptix_worker as worker

    data, input_identity = worker._load_input(
        args.app, config, operation=args.operation
    )
    execute, close, method = worker._prepare_case(args.app, "v4", config, data)
    try:
        for _ in range(args.warmups):
            if execute().get("matched") is not True:
                raise RuntimeError("diagnostic warmup output mismatch")

        counters = _install_instrumentation()
        profiler = cProfile.Profile()
        samples_ns: list[int] = []
        output_digests: list[str] = []
        profiler.enable()
        for _ in range(args.repetitions):
            started = time.perf_counter_ns()
            observed = execute()
            ended = time.perf_counter_ns()
            if observed.get("matched") is not True:
                raise RuntimeError("diagnostic execution output mismatch")
            samples_ns.append(ended - started)
            output_digests.append(str(observed["output_sha256"]))
        profiler.disable()
        if len(set(output_digests)) != 1:
            raise RuntimeError("diagnostic output changed across repetitions")
        profiler.dump_stats(str(args.profile_output))
        with args.profile_text.open("w", encoding="utf-8") as stream:
            pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats(
                "cumulative"
            ).print_stats(160)
    finally:
        close()

    rows = {
        name: {
            **row,
            "inclusive_ms_total": row["inclusive_ns"] / 1_000_000.0,
            "inclusive_ms_per_call": (
                row["inclusive_ns"] / row["calls"] / 1_000_000.0
                if row["calls"]
                else None
            ),
        }
        for name, row in sorted(counters.items())
    }
    result: dict[str, Any] = {
        "schema": "rtdl.v4_long_workload.hot_path_diagnostic.v1",
        "formal_evidence": False,
        "pooling_into_formal_transaction_forbidden": True,
        "app": args.app,
        "operation": args.operation,
        "input_identity": input_identity,
        "method": method,
        "registered_config_source_commit": config["source_commit"],
        "registered_config_source_tree": config["source_tree"],
        "runtime_source_identity": _source_identity(source_root),
        "config_sha256": _sha256(args.config),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "samples_ns": samples_ns,
        "median_ns": int(statistics.median(samples_ns)),
        "minimum_ns": min(samples_ns),
        "maximum_ns": max(samples_ns),
        "output_sha256": output_digests[0],
        "inclusive_nested_counters": rows,
        "profile_output": str(args.profile_output),
        "profile_text": str(args.profile_text),
        "notes": [
            "Inclusive counters overlap and must not be summed.",
            "Instrumentation changes timing and these samples are diagnostic only.",
            "The script profiles the existing public V4 app front door after one warmup.",
        ],
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
