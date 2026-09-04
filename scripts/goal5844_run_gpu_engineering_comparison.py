#!/usr/bin/env python3
"""Run balanced isolated RTDL-v8 versus pinned-PyOptiX engineering blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

from experiments.goal5842_causal_admission.contracts import digest
from experiments.goal5844_compact_execution.worker import (
    PYOPTIX_ARM,
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    RTDL_ARM,
    _hardware as _gpu_hardware,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _validate_timing_summary(
    summary: object, *, expected_count: int, label: str
) -> None:
    required = {
        "sample_count", "samples_ns", "minimum_ns", "median_ns", "maximum_ns"
    }
    if not isinstance(summary, dict) or set(summary) != required:
        raise RuntimeError(f"Goal5844 {label} timing schema differs")
    samples = summary["samples_ns"]
    if (
        summary["sample_count"] != expected_count
        or not isinstance(samples, list)
        or len(samples) != expected_count
        or any(type(value) is not int or value <= 0 for value in samples)
        or summary["minimum_ns"] != min(samples)
        or summary["median_ns"] != int(statistics.median(samples))
        or summary["maximum_ns"] != max(samples)
    ):
        raise RuntimeError(f"Goal5844 {label} timing values differ")


def _validate_worker_result(
    row: dict[str, object],
    *,
    args: argparse.Namespace,
    arm: str,
    block: int,
    source_commit: str,
) -> None:
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    if not isinstance(row, dict):
        raise RuntimeError("Goal5844 worker result must be a mapping")
    observed_seal = row.get("result_sha256")
    body = dict(row)
    body.pop("result_sha256", None)
    if type(observed_seal) is not str or observed_seal != digest(body):
        raise RuntimeError("Goal5844 worker result seal differs")
    expected_scalar = 65_530
    exact = {
        "schema": "rtdl.goal5844.compact_execution.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source_commit,
        "arm": arm,
        "block": block,
        "task": "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
        "query_count": 16_384,
        "expected_scalar": expected_scalar,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
    }
    for key, expected in exact.items():
        if row.get(key) != expected:
            raise RuntimeError(f"Goal5844 worker field differs: {key}")
    claim = row.get("claim_boundary")
    if claim != {
        "engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
        "external_review_complete": False,
    }:
        raise RuntimeError("Goal5844 worker claim boundary differs")
    measurements = row.get("measurements")
    if not isinstance(measurements, dict):
        raise RuntimeError("Goal5844 worker measurements missing")
    _validate_timing_summary(
        measurements.get("steady_public"),
        expected_count=args.repetitions,
        label=f"{arm}.steady_public",
    )
    evidence = measurements.get("evidence")
    identity = measurements.get("identity")
    if not isinstance(evidence, dict) or not isinstance(identity, dict):
        raise RuntimeError("Goal5844 worker evidence or identity missing")
    if arm == RTDL_ARM:
        attribution = measurements.get("attribution")
        if not isinstance(attribution, dict):
            raise RuntimeError("Goal5844 RTDL attribution missing")
        for key in (
            "provider_owner_v8_compact",
            "direct_native_abi_v8_integrated_audit",
            "explicit_full_forensic_expansion",
        ):
            _validate_timing_summary(
                attribution.get(key),
                expected_count=args.layer_repetitions,
                label=f"RTDL.{key}",
            )
        native_sha = _sha256_file(args.native.resolve(strict=True))
        if identity.get("native_library_sha256") != native_sha:
            raise RuntimeError("Goal5844 RTDL native identity differs")
        executable = identity.get("generic_executable_identity")
        if (
            not isinstance(executable, dict)
            or executable.get("provider_artifact_sha256") != native_sha
        ):
            raise RuntimeError("Goal5844 generic executable identity differs")
        output_sha = digest(expected_scalar)
        for receipt_key in (
            "latest_public_compact_receipt",
            "latest_provider_compact_receipt",
        ):
            receipt = evidence.get(receipt_key)
            if not isinstance(receipt, dict):
                raise RuntimeError(f"Goal5844 {receipt_key} missing")
            validate_traversal_receipt(
                receipt,
                provider_library_sha256=native_sha,
                route_identity=(
                    "v4_builtin_triangle_callback_ir:checked_reduction_v1"
                ),
                output_digest=output_sha,
                expected_program_bundles=(
                    "v4_builtin_triangle_checked_reduction_composed",
                ),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=16_384,
            )
        forensic = evidence.get("latest_full_forensic_receipt")
        if (
            not isinstance(forensic, dict)
            or forensic.get("output_digest") != output_sha
            or forensic.get("physical_executor_classification")
                != "optix_traversal_observed"
        ):
            raise RuntimeError("Goal5844 full forensic receipt differs")
        validate_traversal_receipt(
            forensic,
            provider_library_sha256=native_sha,
            route_identity="v4_builtin_triangle_callback_ir:checked_reduction_v1",
            output_digest=output_sha,
            expected_program_bundles=(
                "v4_builtin_triangle_checked_reduction_composed",
            ),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=16_384,
        )
        boundary = evidence.get("execution_boundary")
        if (
            not isinstance(boundary, dict)
            or boundary.get("execution_path")
                != "device_resident_checked_u64_scalar_v8_integrated_audit"
            or boundary.get("prepared_query_input_reused") is not True
            or boundary.get("per_ray_u64_materialized_on_host") is not False
            or boundary.get("event_rows_materialized_on_host") is not False
            or boundary.get("public_output_scalar_bytes") != 8
        ):
            raise RuntimeError("Goal5844 RTDL execution boundary differs")
    elif arm == PYOPTIX_ARM:
        if measurements.get("attribution") is not None:
            raise RuntimeError("Goal5844 PyOptiX attribution must be absent")
        latest = evidence.get("latest_public_output")
        if (
            not isinstance(latest, dict)
            or latest.get("device_status") != 0
            or latest.get("weighted_sum") != expected_scalar
            or identity.get("device_source_sha256")
                != _sha256_file(args.device_source.resolve(strict=True))
            or identity.get("optix_api_version") != args.optix_sdk
        ):
            raise RuntimeError("Goal5844 PyOptiX evidence differs")
        source = identity.get("pyoptix_source")
        extension = identity.get("loaded_extension")
        if (
            identity.get("pyoptix_repository_commit") != PYOPTIX_COMMIT
            or not isinstance(source, dict)
            or source.get("commit") != PYOPTIX_COMMIT
            or source.get("tree") != PYOPTIX_TREE
            or source.get("clean") is not True
            or not isinstance(extension, dict)
            or type(extension.get("bytes")) is not int
            or extension["bytes"] <= 0
            or extension.get("sha256")
                != _sha256_file(
                    Path(str(extension.get("path"))).resolve(strict=True)
                )
        ):
            raise RuntimeError("Goal5844 loaded PyOptiX provenance differs")
    else:  # pragma: no cover - guarded by the controller schedule.
        raise RuntimeError(f"unsupported Goal5844 arm: {arm}")


def _run_worker(
    args: argparse.Namespace,
    *,
    arm: str,
    block: int,
    output: Path,
) -> dict[str, object]:
    command = [
        args.python,
        "-m",
        "experiments.goal5844_compact_execution.worker",
        "--arm",
        arm,
        "--block",
        str(block),
        "--native",
        str(args.native.resolve()),
        "--device-source",
        str(args.device_source.resolve()),
        "--optix-include",
        str(args.optix_include.resolve()),
        "--cuda-include",
        str(args.cuda_include.resolve()),
        "--optix-sdk",
        args.optix_sdk,
        "--compute-capability",
        args.compute_capability,
        "--cache-root",
        str(args.cache_root.resolve()),
        "--pyoptix-distribution",
        args.pyoptix_distribution,
        "--pyoptix-source",
        str(args.pyoptix_source.resolve()),
        "--warmups",
        str(args.warmups),
        "--repetitions",
        str(args.repetitions),
        "--layer-warmups",
        str(args.layer_warmups),
        "--layer-repetitions",
        str(args.layer_repetitions),
        "--output",
        str(output.resolve()),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    (output.parent / f"{output.stem}.stdout.txt").write_text(
        completed.stdout, encoding="utf-8"
    )
    (output.parent / f"{output.stem}.stderr.txt").write_text(
        completed.stderr, encoding="utf-8"
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Goal5844 worker failed: block={block} arm={arm} "
            f"returncode={completed.returncode}"
        )
    row = json.loads(output.read_text(encoding="utf-8"))
    _validate_worker_result(
        row,
        args=args,
        arm=arm,
        block=block,
        source_commit=args.source_commit,
    )
    return row


def _worker_median(row: dict[str, object]) -> int:
    return int(row["measurements"]["steady_public"]["median_ns"])


def _samples(rows: list[dict[str, object]], arm: str) -> list[int]:
    values: list[int] = []
    for row in rows:
        if row["arm"] == arm:
            values.extend(
                int(item)
                for item in row["measurements"]["steady_public"]["samples_ns"]
            )
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=8)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--layer-warmups", type=int, default=8)
    parser.add_argument("--layer-repetitions", type=int, default=64)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks < 4 or args.blocks % 2:
        raise ValueError("Goal5844 requires an even block count of at least four")
    if args.output_root.exists():
        raise FileExistsError(args.output_root)
    if args.cache_root.exists():
        raise FileExistsError(args.cache_root)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise RuntimeError("Goal5844 comparison requires a clean source checkout")
    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    args.source_commit = source_commit
    controller_hardware_before = _gpu_hardware()
    args.output_root.mkdir(parents=True)
    worker_root = args.output_root / "workers"
    worker_root.mkdir()
    rows: list[dict[str, object]] = []
    schedule: list[dict[str, object]] = []
    for block in range(args.blocks):
        order = (RTDL_ARM, PYOPTIX_ARM) if block % 2 == 0 else (
            PYOPTIX_ARM,
            RTDL_ARM,
        )
        for position, arm in enumerate(order):
            schedule.append({"block": block, "position": position, "arm": arm})
            output = worker_root / f"block_{block:02d}_{position}_{arm}.json"
            rows.append(_run_worker(args, arm=arm, block=block, output=output))

    controller_hardware_after = _gpu_hardware()
    if controller_hardware_after != controller_hardware_before:
        raise RuntimeError("Goal5844 controller GPU identity changed during run")
    hardware = {json.dumps(row["hardware"], sort_keys=True) for row in rows}
    commits = {row["source_commit"] for row in rows}
    if (
        hardware != {json.dumps(controller_hardware_before, sort_keys=True)}
        or commits != {source_commit}
    ):
        raise RuntimeError("Goal5844 workers differ in hardware or source identity")
    by_block: list[dict[str, object]] = []
    for block in range(args.blocks):
        block_rows = {row["arm"]: row for row in rows if row["block"] == block}
        if set(block_rows) != {RTDL_ARM, PYOPTIX_ARM}:
            raise RuntimeError(f"Goal5844 block {block} is incomplete")
        rtdl_ns = _worker_median(block_rows[RTDL_ARM])
        pyoptix_ns = _worker_median(block_rows[PYOPTIX_ARM])
        by_block.append(
            {
                "block": block,
                "rtdl_median_ns": rtdl_ns,
                "pyoptix_median_ns": pyoptix_ns,
                "rtdl_over_pyoptix": rtdl_ns / pyoptix_ns,
            }
        )
    rtdl_samples = _samples(rows, RTDL_ARM)
    pyoptix_samples = _samples(rows, PYOPTIX_ARM)
    block_ratios = [float(row["rtdl_over_pyoptix"]) for row in by_block]
    median_ratio = float(statistics.median(block_ratios))
    result: dict[str, object] = {
        "schema": "rtdl.goal5844.compact_execution.engineering_comparison.v1",
        "status": (
            "PASS__INTERNAL_ENGINEERING_TARGET_MET"
            if median_ratio <= 1.25
            else "ADVERSE__CONTINUE_PERFORMANCE_ENGINEERING"
        ),
        "source_commit": source_commit,
        "schedule": schedule,
        "hardware": rows[0]["hardware"],
        "task": rows[0]["task"],
        "blocks": args.blocks,
        "warmups_per_worker": args.warmups,
        "repetitions_per_worker": args.repetitions,
        "all_samples_retained": True,
        "aggregate": {
            "rtdl_sample_count": len(rtdl_samples),
            "pyoptix_sample_count": len(pyoptix_samples),
            "rtdl_median_ns": int(statistics.median(rtdl_samples)),
            "pyoptix_median_ns": int(statistics.median(pyoptix_samples)),
            "median_within_block_ratio": median_ratio,
            "engineering_target_ratio": 1.25,
            "engineering_target_met": median_ratio <= 1.25,
        },
        "within_block": by_block,
        "worker_result_sha256": [row["result_sha256"] for row in rows],
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "formal_baseline": False,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "goal5843_rows_reused_or_pooled": False,
        },
    }
    result["result_sha256"] = digest(result)
    (args.output_root / "SUMMARY.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
