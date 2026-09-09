#!/usr/bin/env python3
"""Independently recount a completed LibRTS long-workload transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
from typing import Any


SCHEMA = "rtdl.v4.librts.long_query_independent_recount.v1"
FORMAL_SCHEMA = "rtdl.v4.librts.long_query_formal.v1"
PREREG_SCHEMA = f"{FORMAL_SCHEMA}.preregistration"
OPERATIONS = ("point_contains", "range_contains")
ENDPOINTS = ("complete", "prepared")
ORDERS = (
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
)


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, Any]:
    value = Path(path).resolve(strict=True)
    return {"path": str(value), "bytes": value.stat().st_size, "sha256": sha256(value)}


def read_json_value(path: str | Path) -> Any:
    def reject(value: str) -> None:
        raise ValueError(f"nonfinite JSON value is forbidden: {value}")

    return json.loads(
        Path(path).read_text(encoding="utf-8"), parse_constant=reject
    )


def read_json(path: str | Path) -> dict[str, Any]:
    result = read_json_value(path)
    if not isinstance(result, dict):
        raise TypeError(f"JSON object required: {path}")
    return result


def read_command(path: str | Path) -> list[str]:
    result = read_json_value(path)
    if not isinstance(result, list) or not result or any(
        not isinstance(value, str) or not value for value in result
    ):
        raise TypeError(f"nonempty JSON string array required: {path}")
    return result


def write_new(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with target.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def git(repo: Path, *arguments: str, binary: bool = False):
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments], check=True,
        capture_output=True, text=not binary,
    )
    return completed.stdout if binary else completed.stdout.strip()


def same_float(left: Any, right: Any) -> bool:
    return isinstance(left, (int, float)) and isinstance(right, (int, float)) \
        and math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-15)


def verify_source(prereg: dict[str, Any], repo: Path) -> None:
    commit = prereg["source_commit"]
    if git(repo, "rev-parse", f"{commit}^{{tree}}") != prereg["source_tree"]:
        raise ValueError("recount source commit/tree differs")
    for row in prereg["source_files"]:
        relative = Path(row["path"]).relative_to(Path(prereg["source_root"]))
        payload = git(repo, "show", f"{commit}:{relative.as_posix()}", binary=True)
        if len(payload) != row["bytes"] or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError(f"recount source bytes differ: {relative}")


def expected_worker_command(
    prereg: dict[str, Any], transaction: Path, operation: str,
    endpoint: str, block: int, arm: str,
) -> list[str]:
    closure = prereg[
        "point_queries" if operation == OPERATIONS[0] else "range_queries"
    ]
    output = (
        transaction / "workers" / operation / endpoint / f"block-{block}"
        / arm / "WORKER_RESULT.json"
    )
    return [
        prereg["python"]["path"],
        str(Path(prereg["source_root"]) / "scripts/v4_librts_long_worker.py"),
        "--source-root", prereg["source_root"],
        "--arm", arm,
        "--endpoint", endpoint,
        "--operation", operation,
        "--indexed-npz", prereg["indexed_npz"]["path"],
        "--query-manifest", closure["manifest"]["path"],
        "--native", prereg["native_library"]["path"],
        "--pyoptix-ptx", prereg["pyoptix_ptx"]["path"],
        "--optix-sdk", prereg["optix_sdk"],
        "--compute-capability", prereg["gpu"]["compute_capability"],
        "--warmups", str(prereg[f"{endpoint}_warmups"]),
        "--repetitions", str(prereg[f"{endpoint}_repetitions"]),
        "--output", str(output),
    ]


def validate_worker(
    prereg: dict[str, Any], transaction: Path, operation: str,
    endpoint: str, block: int, arm: str,
) -> tuple[dict[str, Any], int]:
    directory = transaction / "workers" / operation / endpoint / f"block-{block}" / arm
    command = read_command(directory / "COMMAND.json")
    exit_record = read_json(directory / "EXIT.json")
    worker = read_json(directory / "WORKER_RESULT.json")
    stdout = (directory / "STDOUT.bin").read_bytes()
    stderr = (directory / "STDERR.bin").read_bytes()
    expected_command = expected_worker_command(
        prereg, transaction, operation, endpoint, block, arm
    )
    try:
        stdout_value = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(
            f"recount worker stdout is not one JSON document: "
            f"{operation}/{endpoint}/{block}/{arm}"
        ) from error
    if command != expected_command or exit_record.get("returncode") != 0 \
            or exit_record.get("timed_out") is not False \
            or not stdout or stderr or stdout_value != worker:
        raise ValueError(f"recount worker process record differs: {operation}/{endpoint}/{block}/{arm}")
    manifest = read_json(
        prereg["point_queries" if operation == OPERATIONS[0] else "range_queries"]
        ["manifest"]["path"]
    )
    samples = worker.get("samples_ns", [])
    expected_warmups = prereg[f"{endpoint}_warmups"]
    expected_repetitions = prereg[f"{endpoint}_repetitions"]
    if worker.get("schema") != "rtdl.v4.librts.long_query_worker.v1" \
            or worker.get("status") != "PASS__LIBRTS_LONG_QUERY_WORKER" \
            or worker.get("arm") != arm \
            or worker.get("operation") != operation \
            or worker.get("endpoint") != endpoint \
            or worker.get("source", {}).get("commit") != prereg["source_commit"] \
            or worker.get("source", {}).get("tree") != prereg["source_tree"] \
            or worker.get("source", {}).get("dirty") is not False \
            or worker.get("query_count") != manifest["query_count"] \
            or worker.get("expected_count_u64") != manifest["expected_count_u64"] \
            or worker.get("all_queries_distinct") is not True \
            or worker.get("warmup_count") != expected_warmups \
            or worker.get("timed_repetition_count") != expected_repetitions \
            or len(samples) != expected_repetitions \
            or any(type(sample) is not int or sample <= 0 for sample in samples) \
            or worker.get("median_ns") != int(statistics.median(samples)):
        raise ValueError(f"recount worker contract differs: {operation}/{endpoint}/{block}/{arm}")
    if endpoint == "complete":
        metric = worker["prepare_and_bind_ns"] + samples[0] + worker["close_ns"]
        if worker.get("complete_task_ns") != metric:
            raise ValueError("recount complete endpoint decomposition differs")
    else:
        metric = worker["median_ns"]
        if worker.get("complete_task_ns") is not None:
            raise ValueError("recount prepared endpoint unexpectedly reports complete task")
    if any(int(output["count"]) != manifest["expected_count_u64"] for output in worker["outputs"]):
        raise ValueError("recount output scalar differs")
    return worker, metric


def recount(args) -> dict[str, Any]:
    transaction = args.transaction.resolve(strict=True)
    result = read_json(transaction / "RESULT.json")
    prereg_binding = read_json(transaction / "PREREGISTRATION_BINDING.json")
    prereg_path = Path(prereg_binding["path"]).resolve(strict=True)
    if binding(prereg_path) != prereg_binding:
        raise ValueError("recount preregistration binding differs")
    prereg = read_json(prereg_path)
    if prereg.get("schema") != PREREG_SCHEMA \
            or result.get("schema") != FORMAL_SCHEMA \
            or result.get("preregistration") != prereg_binding:
        raise ValueError("recount formal schema/binding differs")
    verify_source(prereg, args.repository.resolve(strict=True))
    cells = []
    worker_count = 0
    for operation in OPERATIONS:
        for endpoint in ENDPOINTS:
            for block, order in enumerate(ORDERS):
                metrics = {}
                for arm in order:
                    _, metrics[arm] = validate_worker(
                        prereg, transaction, operation, endpoint, block, arm
                    )
                    worker_count += 1
                cells.append({
                    "operation": operation,
                    "endpoint": endpoint,
                    "block": block,
                    "order": list(order),
                    "rtdl_ns": metrics["rtdl"],
                    "pyoptix_ns": metrics["pyoptix"],
                    "rtdl_over_pyoptix": metrics["rtdl"] / metrics["pyoptix"],
                })
    if worker_count != 64 or len(cells) != 32:
        raise ValueError("recount worker/cell cardinality differs")
    if len(result.get("cells", ())) != len(cells):
        raise ValueError("recount controller cell cardinality differs")
    for expected, observed in zip(cells, result["cells"], strict=True):
        for key in ("operation", "endpoint", "block", "order", "rtdl_ns", "pyoptix_ns"):
            if expected[key] != observed.get(key):
                raise ValueError(f"recount controller cell differs: {key}")
        if not same_float(expected["rtdl_over_pyoptix"], observed.get("rtdl_over_pyoptix")):
            raise ValueError("recount controller ratio differs")
    summaries = []
    passed = True
    for operation in OPERATIONS:
        for endpoint in ENDPOINTS:
            selected = [row for row in cells if row["operation"] == operation and row["endpoint"] == endpoint]
            ratios = [row["rtdl_over_pyoptix"] for row in selected]
            summary = {
                "operation": operation,
                "endpoint": endpoint,
                "paired_ratio_median": statistics.median(ratios),
                "paired_ratio_min": min(ratios),
                "paired_ratio_max": max(ratios),
                "rtdl_time_median_ns": statistics.median(row["rtdl_ns"] for row in selected),
                "pyoptix_time_median_ns": statistics.median(row["pyoptix_ns"] for row in selected),
                "median_gate_passed": statistics.median(ratios) <= 1.20,
                "every_block_gate_passed": max(ratios) <= 1.35,
            }
            passed = passed and summary["median_gate_passed"] and summary["every_block_gate_passed"]
            summaries.append(summary)
    if len(result.get("summaries", ())) != len(summaries):
        raise ValueError("recount controller summary cardinality differs")
    for expected, observed in zip(summaries, result["summaries"], strict=True):
        for key, value in expected.items():
            if isinstance(value, float):
                if not same_float(value, observed.get(key)):
                    raise ValueError(f"recount controller summary differs: {key}")
            elif value != observed.get(key):
                raise ValueError(f"recount controller summary differs: {key}")
    return {
        "schema": SCHEMA,
        "status": (
            "PASS__INDEPENDENT_RECOUNT__INTERNAL_ENGINEERING_TARGETS_MET"
            if passed else "PASS__INDEPENDENT_RECOUNT__ENGINEERING_TARGETS_NOT_MET"
        ),
        "transaction": binding(transaction / "RESULT.json"),
        "preregistration": prereg_binding,
        "worker_count": worker_count,
        "cell_count": len(cells),
        "cells": cells,
        "summaries": summaries,
        "controller_status": result["status"],
        "controller_projection_equal": True,
        "public_claim_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--transaction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = recount(args)
    write_new(args.output, value)
    print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
