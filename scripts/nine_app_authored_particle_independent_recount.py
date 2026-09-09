#!/usr/bin/env python3
"""Independently reconstruct the authored Particle formal comparison."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import struct


SCHEMA = "rtdl.nine_app.authored_particle.independent_recount.v1"
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 9_202_609


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, object]:
    value = Path(path).resolve(strict=True)
    return {
        "path": str(value),
        "bytes": value.stat().st_size,
        "sha256": sha256(value),
    }


def read_json(path: str | Path) -> dict[str, object]:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON value is forbidden: {value}")

    value = json.loads(
        Path(path).read_text(encoding="utf-8"),
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def write_new(path: str | Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False,
    ) + "\n").encode("utf-8")
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def bootstrap_interval(values: list[float]) -> list[float]:
    generator = random.Random(BOOTSTRAP_SEED)
    draws = sorted(statistics.median(
        generator.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS))
    return [draws[249], draws[9749]]


def _single_directory(root: Path, prefix: str) -> Path:
    matches = sorted(
        path for path in root.iterdir()
        if path.is_dir() and path.name.startswith(prefix)
    )
    if len(matches) != 1:
        raise ValueError(f"expected one {prefix} directory, found {matches!r}")
    return matches[0]


def _resolve_recorded_path(root: Path, recorded: str) -> Path:
    parts = Path(recorded).parts
    matches: list[Path] = []
    for child in root.iterdir():
        if not child.is_dir() or child.name not in parts:
            continue
        index = parts.index(child.name)
        matches.append(child.joinpath(*parts[index + 1:]))
    if len(matches) != 1:
        raise ValueError(f"cannot map recorded path into archive: {recorded}")
    return matches[0]


def _check_recorded_binding(
    root: Path, row: dict[str, object],
) -> Path:
    if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
        raise ValueError("exact file binding required")
    path = _resolve_recorded_path(root, str(row["path"])).resolve(strict=True)
    if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
        raise ValueError(f"recorded binding differs: {path}")
    return path


def _same_float(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=1e-15)


def _expected_public_output_bytes(path: Path) -> bytes:
    payload = path.read_bytes()
    if payload[:6] != b"\x93NUMPY" or payload[6:8] != b"\x01\x00":
        raise ValueError("expected Particle output must be NPY v1")
    header_size = struct.unpack_from("<H", payload, 8)[0]
    data_offset = 10 + header_size
    header = ast.literal_eval(payload[10:data_offset].decode("latin1").strip())
    if header != {
        "descr": "<u4", "fortran_order": False, "shape": (5000, 3),
    }:
        raise ValueError(f"unexpected Particle expected-output header: {header!r}")
    rows = payload[data_offset:]
    if len(rows) != 5000 * 3 * 4:
        raise ValueError("Particle expected-output byte count differs")
    output = bytearray()
    for selected, neighbor, face in struct.iter_unpack("<III", rows):
        output.extend(struct.pack("<III", face, selected, neighbor))
    return bytes(output)


def recount(
    *, root: Path, archive: Path, data_manifest: Path, expected_output: Path,
) -> dict[str, object]:
    root = root.resolve(strict=True)
    archive = archive.resolve(strict=True)
    data_manifest = data_manifest.resolve(strict=True)
    expected_output = expected_output.resolve(strict=True)
    formal_root = _single_directory(root, "rtdl-authored-particle-formal-")
    _single_directory(root, "rtdl-authored-particle-native-")
    _single_directory(root, "rtdl-authored-particle-ptx-")
    result_path = formal_root / "formal/RESULT.json"
    result = read_json(result_path)
    preregistration_path = _check_recorded_binding(
        root, result["preregistration"])
    preregistration = read_json(preregistration_path)
    for key in (
        "calibration", "native_build", "native_library", "pyoptix_build",
        "pyoptix_ptx",
    ):
        _check_recorded_binding(root, preregistration[key])

    manifest = read_json(data_manifest)
    if binding(data_manifest)["sha256"] \
            != preregistration["data_manifest"]["sha256"]:
        raise ValueError("preserved Particle data manifest differs")
    expected_member = manifest["members"]["expected_u32.npy"]
    if expected_output.stat().st_size != expected_member["size_bytes"] \
            or sha256(expected_output) != expected_member["sha256"]:
        raise ValueError("preserved Particle complete expected output differs")
    oracle_sha256 = hashlib.sha256(json.dumps(
        {
            "construction": manifest["queries"]["construction"],
            "query_cells_sha256": manifest["members"][
                "query_cells_u32.npy"]["sha256"],
            "expected_sha256": expected_member["sha256"],
            "source_sha256": manifest["source"]["sha256"],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()).hexdigest()
    expected_public_output = _expected_public_output_bytes(expected_output)
    output_digest = hashlib.sha256()
    output_digest.update(b"<u4")
    output_digest.update(b"(5000, 3)")
    output_digest.update(expected_public_output)
    expected_output_sha256 = output_digest.hexdigest()
    if oracle_sha256 != preregistration["independent_oracle_sha256"] \
            or expected_output_sha256 != preregistration["output_sha256"]:
        raise ValueError("independent oracle or complete output digest differs")

    if result["source_commit"] != preregistration["source_commit"] \
            or result["source_tree"] != preregistration["source_tree"]:
        raise ValueError("result and preregistration source identities differ")
    if result["input_sha256"] != preregistration["data_manifest"]["sha256"] \
            or result["output_sha256"] != preregistration["output_sha256"]:
        raise ValueError("result input/output identity differs")
    if result["retry_count"] != 0 or result["discard_count"] != 0:
        raise ValueError("formal transaction contains retry or discard")

    worker_records = result["worker_records"]
    if len(worker_records) != 18:
        raise ValueError("formal transaction must contain exactly 18 workers")
    primary = [row for row in worker_records if row["endpoint"] == "primary"]
    lifecycle = [row for row in worker_records if row["endpoint"] == "lifecycle"]
    if len(primary) != 16 or len(lifecycle) != 2:
        raise ValueError("formal primary/lifecycle worker count differs")

    true_optix_rtdl_workers = 0
    true_optix_pyoptix_workers = 0
    for record in worker_records:
        stdout = _check_recorded_binding(root, record["stdout"])
        _check_recorded_binding(root, record["stderr"])
        worker = read_json(stdout)
        if worker != record["worker_result"]:
            raise ValueError("embedded worker result differs from raw stdout")
        samples = worker["samples_ns"]
        if len(samples) != record["samples"] \
                or any(type(value) is not int or value <= 0 for value in samples) \
                or statistics.median(samples) != worker["median_ns"]:
            raise ValueError("worker samples or reconstructed median differ")
        if worker["output_sha256"] != result["output_sha256"] \
                or worker["independent_oracle_sha256"] \
                    != preregistration["independent_oracle_sha256"] \
                or worker["query_count"] != 5_000 \
                or worker["output_shape"] != [5_000, 3]:
            raise ValueError("worker complete output contract differs")
        try:
            retained_output = base64.b64decode(
                worker["output_u32_le_base64"], validate=True)
        except (KeyError, ValueError, TypeError) as error:
            raise ValueError("worker complete output bytes are absent") from error
        if retained_output != expected_public_output:
            raise ValueError("worker complete output bytes differ from oracle")
        if record["arm"] == "rtdl":
            evidence = worker["last_execution_evidence"]
            if evidence["physical_executor_classification"] \
                    != "optix_traversal_observed" \
                    or evidence["role_counters"] \
                    != [0, 5000, 0, 0, 5000, 0, 5000] \
                    or worker["metadata"][
                        "prepared_query_batch_device_resident"] is not True:
                raise ValueError("RTDL worker lacks required traversal evidence")
            true_optix_rtdl_workers += 1
        elif record["arm"] == "pyoptix":
            prepared = worker["metadata"][
                "prepared_query_batch_operation_counts"]
            execute = worker["last_execution_evidence"]["operation_counts"]
            if prepared["query_h2d_copy_call_count"] != 7 \
                    or prepared["query_h2d_bytes"] != 140_000 \
                    or execute["query_h2d_copy_call_count"] != 0 \
                    or execute["query_h2d_bytes"] != 0 \
                    or execute["optix_launch_call_count"] != 1 \
                    or execute["output_d2h_bytes"] != 60_000:
                raise ValueError("PyOptiX worker operation evidence differs")
            true_optix_pyoptix_workers += 1
        else:
            raise ValueError(f"unknown worker arm: {record['arm']}")

    reconstructed_blocks: list[dict[str, object]] = []
    orders = preregistration["orders"]
    for block in range(8):
        rows = sorted(
            (row for row in primary if row["block"] == block),
            key=lambda row: row["position"],
        )
        if len(rows) != 2 or [row["arm"] for row in rows] != orders[block]:
            raise ValueError(f"paired block {block} schedule differs")
        by_arm = {row["arm"]: row["worker_result"] for row in rows}
        ratio = by_arm["rtdl"]["median_ns"] / by_arm["pyoptix"]["median_ns"]
        reconstructed_blocks.append({
            "block": block,
            "order": orders[block],
            "rtdl_median_ns": by_arm["rtdl"]["median_ns"],
            "pyoptix_median_ns": by_arm["pyoptix"]["median_ns"],
            "rtdl_over_pyoptix": ratio,
        })
    if reconstructed_blocks != result["block_rows"]:
        raise ValueError("reconstructed block rows differ from controller result")
    ratios = [row["rtdl_over_pyoptix"] for row in reconstructed_blocks]
    paired_median = statistics.median(ratios)
    worst_block = max(ratios)
    bootstrap = bootstrap_interval(ratios)
    if not _same_float(
            paired_median, result["paired_median_rtdl_over_pyoptix"]) \
            or not _same_float(
                worst_block, result["worst_block_rtdl_over_pyoptix"]) \
            or any(not _same_float(left, right) for left, right in zip(
                bootstrap, result["block_bootstrap_95_percent"], strict=True)):
        raise ValueError("independent statistics differ from controller result")
    lifecycle_by_arm = {
        row["arm"]: row["worker_result"]["lifecycle_ns"]
        for row in lifecycle
    }
    lifecycle_ratio = lifecycle_by_arm["rtdl"] / lifecycle_by_arm["pyoptix"]
    if lifecycle_by_arm != result["lifecycle_ns"] \
            or not _same_float(
                lifecycle_ratio, result["lifecycle_rtdl_over_pyoptix"]):
        raise ValueError("independent lifecycle reconstruction differs")
    targets = preregistration["engineering_targets"]
    passed = paired_median <= targets[
        "paired_median_rtdl_over_pyoptix_at_most"] and worst_block <= targets[
            "every_block_rtdl_over_pyoptix_at_most"]
    expected_status = (
        "PASS__INTERNAL_ENGINEERING_TARGETS__EXTERNAL_REVIEW_PENDING"
        if passed else "FAILED_ENGINEERING_TARGETS__ADVERSE_RESULT_RETAINED"
    )
    if result["status"] != expected_status:
        raise ValueError("controller status differs from reconstructed gates")
    return {
        "schema": SCHEMA,
        "status": "PASS__INDEPENDENT_RAW_RECONSTRUCTION",
        "archive": binding(archive),
        "data_manifest": binding(data_manifest),
        "complete_expected_output": binding(expected_output),
        "controller_result": binding(result_path),
        "source_commit": result["source_commit"],
        "source_tree": result["source_tree"],
        "gpu": result["gpu"],
        "input_sha256": result["input_sha256"],
        "independent_oracle_sha256": oracle_sha256,
        "output_sha256": expected_output_sha256,
        "worker_count": len(worker_records),
        "primary_worker_count": len(primary),
        "primary_timed_call_count": sum(row["samples"] for row in primary),
        "lifecycle_worker_count": len(lifecycle),
        "true_optix_rtdl_worker_count": true_optix_rtdl_workers,
        "true_optix_pyoptix_worker_count": true_optix_pyoptix_workers,
        "block_rows": reconstructed_blocks,
        "paired_median_rtdl_over_pyoptix": paired_median,
        "worst_block_rtdl_over_pyoptix": worst_block,
        "block_bootstrap_95_percent": bootstrap,
        "lifecycle_ns": lifecycle_by_arm,
        "lifecycle_rtdl_over_pyoptix": lifecycle_ratio,
        "retry_count": result["retry_count"],
        "discard_count": result["discard_count"],
        "engineering_targets_passed": passed,
        "claim_boundary": {
            "prepared_5000_query_task_only": True,
            "natural_at_least_one_second_task": False,
            "external_review_completed": False,
            "paper_claim_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--data-manifest", type=Path, required=True)
    parser.add_argument("--expected-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_new(args.output, recount(
        root=args.root,
        archive=args.archive,
        data_manifest=args.data_manifest,
        expected_output=args.expected_output,
    ))
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
