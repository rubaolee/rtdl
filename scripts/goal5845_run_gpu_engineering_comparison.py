#!/usr/bin/env python3
"""Run balanced isolated RTDL-v8 versus pinned-PyOptiX relation blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any

from experiments.goal5842_causal_admission.contracts import RELATION_TASK, digest
from experiments.goal5845_relation_compact_execution.worker import (
    PYOPTIX_ARM,
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    RTDL_ARM,
    _hardware,
)
from experiments.goal5844_compact_execution.provenance import (
    validate_pyoptix_build_receipt,
    write_json_create,
)
from scripts.goal5844_run_gpu_engineering_comparison import (
    _validate_native_build_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
V8_SYMBOL = "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8"
PRIMARY_RATIO_LIMIT = 1.25
WORST_BLOCK_RATIO_LIMIT = 1.50
PUBLIC_OVER_DIRECT_LIMIT = 1.75


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git_value(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _validate_preregistration(path: Path, args: argparse.Namespace) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Goal5845 preregistration must be a mapping")
    body = dict(value)
    observed = body.pop("preregistration_sha256", None)
    if type(observed) is not str or observed != digest(body):
        raise RuntimeError("Goal5845 preregistration seal differs")
    design = value.get("design")
    gates = value.get("pass_gates")
    if (
        value.get("schema")
            != "rtdl.goal5845.relation_public_parity_preregistration.v1"
        or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION"
        or not isinstance(design, dict)
        or design.get("blocks") != args.blocks
        or design.get("warmups_per_worker") != args.warmups
        or design.get("samples_per_worker") != args.repetitions
        or design.get("samples_per_arm") != args.blocks * args.repetitions
        or design.get("sample_discard_count") != 0
        or not isinstance(gates, dict)
        or gates.get("median_within_block_rtdl_over_pyoptix_at_most")
            != PRIMARY_RATIO_LIMIT
        or gates.get("worst_block_rtdl_over_pyoptix_at_most")
            != WORST_BLOCK_RATIO_LIMIT
        or gates.get("median_within_block_rtdl_public_over_direct_native_at_most")
            != PUBLIC_OVER_DIRECT_LIMIT
    ):
        raise RuntimeError("Goal5845 command differs from frozen design")
    return value


def _require_outside_repository(path: Path) -> None:
    candidate = path.expanduser().absolute()
    resolved = candidate.parent.resolve(strict=True) / candidate.name
    try:
        resolved.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        return
    raise RuntimeError("Goal5845 output root must be outside the Git tree")


def _validate_timing_summary(
    summary: object, *, expected_count: int, label: str
) -> None:
    required = {
        "sample_count",
        "samples_ns",
        "minimum_ns",
        "median_ns",
        "maximum_ns",
    }
    if not isinstance(summary, dict) or set(summary) != required:
        raise RuntimeError(f"Goal5845 {label} timing schema differs")
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
        raise RuntimeError(f"Goal5845 {label} timing values differ")


def expected_schedule(blocks: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for block in range(blocks):
        order = (
            (RTDL_ARM, PYOPTIX_ARM)
            if block % 2 == 0
            else (PYOPTIX_ARM, RTDL_ARM)
        )
        for position, arm in enumerate(order):
            rows.append({"block": block, "position": position, "arm": arm})
    return rows


def _validate_worker(
    row: object,
    *,
    args: argparse.Namespace,
    arm: str,
    block: int,
    hardware: dict[str, object],
) -> dict[str, object]:
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    if not isinstance(row, dict):
        raise TypeError("Goal5845 worker result must be a mapping")
    body = dict(row)
    observed_seal = body.pop("result_sha256", None)
    if type(observed_seal) is not str or observed_seal != digest(body):
        raise RuntimeError("Goal5845 worker seal differs")
    exact = {
        "schema": "rtdl.goal5845.relation_compact_execution.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": args.expected_source_commit,
        "arm": arm,
        "block": block,
        "task": RELATION_TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "hardware": hardware,
    }
    for key, expected in exact.items():
        if row.get(key) != expected:
            raise RuntimeError(f"Goal5845 worker field differs: {key}")
    if row.get("claim_boundary") != {
        "engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
        "external_review_complete": False,
    }:
        raise RuntimeError("Goal5845 worker claim boundary differs")
    measurements = row.get("measurements")
    if not isinstance(measurements, dict):
        raise RuntimeError("Goal5845 worker measurements missing")
    _validate_timing_summary(
        measurements.get("steady_public"),
        expected_count=args.repetitions,
        label=f"{arm}.steady_public",
    )
    evidence = measurements.get("evidence")
    identity = measurements.get("identity")
    if not isinstance(evidence, dict) or not isinstance(identity, dict):
        raise RuntimeError("Goal5845 worker evidence or identity missing")
    if (
        evidence.get("public_output_sha256") != row.get("output_sha256")
        or evidence.get("public_row_count") != 4096
    ):
        raise RuntimeError("Goal5845 public output evidence differs")
    if arm == RTDL_ARM:
        attribution = measurements.get("attribution")
        if not isinstance(attribution, dict):
            raise RuntimeError("Goal5845 RTDL attribution missing")
        for key in (
            "family_bridge",
            "protocol_lifecycle",
            "prepared_owner",
            "direct_native_v8",
        ):
            _validate_timing_summary(
                attribution.get(key),
                expected_count=args.layer_repetitions,
                label=f"RTDL.{key}",
            )
        if (
            type(attribution.get("explicit_full_diagnostic_ns")) is not int
            or attribution["explicit_full_diagnostic_ns"] <= 0
        ):
            raise RuntimeError("Goal5845 explicit diagnostic timing differs")
        native_sha = _sha256_file(args.native.resolve(strict=True))
        executable = identity.get("generic_executable_identity")
        if (
            identity.get("native_library_sha256") != native_sha
            or not isinstance(executable, dict)
            or executable.get("provider_artifact_sha256") != native_sha
            or evidence.get("immutable_output_reused") is not True
            or evidence.get("two_actual_optix_launches") is not True
        ):
            raise RuntimeError("Goal5845 RTDL identity/boundary differs")
        receipt = evidence.get("latest_compact_receipt")
        if not isinstance(receipt, dict):
            raise RuntimeError("Goal5845 RTDL compact receipt missing")
        validate_traversal_receipt(
            receipt,
            provider_library_sha256=native_sha,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=str(row["output_sha256"]),
            expected_program_bundles=(
                "v4_custom_aabb_bounded_relation_composed",
            ),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=8192,
        )
        fast = evidence.get("latest_fast_operation_receipt")
        required_fast = {
            "schema_version": 2,
            "optix_launch_count": 2,
            "host_blocking_boundary_count": 2,
            "control_d2h_bytes": 28,
            "output_d2h_bytes": 32768,
            "status_before_output": True,
            "output_d2h_after_status_failure": 0,
            "role_counters_materialized": False,
            "prepared_input_reused": True,
            "dynamic_device_upload_call_count": 0,
            "dynamic_accel_build_count": 0,
            "dynamic_explicit_sync_count": 0,
            "dynamic_blocking_upload_call_count": 0,
            "dynamic_device_upload_bytes": 0,
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": 8192,
            "semantic_compaction_scratch_bytes": 98312,
            "callback_status_kernel_launch_count": 0,
            "checked_product_kernel_launch_count": 0,
            "compact_control_finalizer_kernel_launch_count": 0,
            "total_auxiliary_cuda_kernel_launch_count": 1,
            "execution_parameter_h2d_bytes": 240,
            "execution_parameter_h2d_copy_call_count": 2,
            "stream_ordered_memset_call_count": 4,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1,
        }
        if not isinstance(fast, dict) or any(
            fast.get(key) != expected for key, expected in required_fast.items()
        ) or type(fast.get("dynamic_input_generation")) is not int \
                or fast["dynamic_input_generation"] <= 0:
            raise RuntimeError("Goal5845 RTDL fast receipt differs")
    elif arm == PYOPTIX_ARM:
        if measurements.get("attribution") is not None:
            raise RuntimeError("Goal5845 PyOptiX attribution must be absent")
        source = identity.get("pyoptix_repository")
        receipt = validate_pyoptix_build_receipt(
            args.pyoptix_build_receipt.resolve(strict=True)
        )
        extension = identity.get("loaded_extension")
        if (
            evidence.get("device_status") != 0
            or evidence.get("device_overflow") != 0
            or not isinstance(source, dict)
            or source.get("commit") != PYOPTIX_COMMIT
            or source.get("tree") != PYOPTIX_TREE
            or source.get("clean") is not True
            or identity.get("optix_api_version") != args.optix_sdk
            or identity.get("pyoptix_build_receipt_sha256")
                != receipt["receipt_sha256"]
            or not isinstance(extension, dict)
            or extension.get("sha256")
                != receipt["installed"]["loaded_extension"]["sha256"]
        ):
            raise RuntimeError("Goal5845 PyOptiX evidence differs")
    else:
        raise RuntimeError(f"Goal5845 unknown arm: {arm}")
    return row


def _run_worker(
    args: argparse.Namespace,
    *,
    arm: str,
    block: int,
    output: Path,
    hardware: dict[str, object],
) -> dict[str, object]:
    command = [
        args.python,
        "-m",
        "experiments.goal5845_relation_compact_execution.worker",
        "--arm",
        arm,
        "--block",
        str(block),
        "--expected-source-commit",
        args.expected_source_commit,
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
        "--pyoptix-build-receipt",
        str(args.pyoptix_build_receipt.resolve()),
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
    environment = dict(os.environ)
    environment["PYTHONPATH"] = f"{ROOT / 'src'}:{ROOT}"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
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
            f"Goal5845 worker failed: block={block} arm={arm} "
            f"returncode={completed.returncode}"
        )
    return _validate_worker(
        json.loads(output.read_text(encoding="utf-8")),
        args=args,
        arm=arm,
        block=block,
        hardware=hardware,
    )


def _worker_median(row: dict[str, object]) -> int:
    return int(row["measurements"]["steady_public"]["median_ns"])


def _samples(rows: list[dict[str, object]], arm: str) -> list[int]:
    values: list[int] = []
    for row in rows:
        if row["arm"] == arm:
            values.extend(
                int(value)
                for value in row["measurements"]["steady_public"]["samples_ns"]
            )
    return values


def build_summary(
    args: argparse.Namespace,
    rows: list[dict[str, object]],
    *,
    schedule: list[dict[str, object]],
    hardware: dict[str, object],
) -> dict[str, object]:
    blocks = []
    public_over_direct = []
    for block in range(args.blocks):
        matches = [row for row in rows if row["block"] == block]
        if len(matches) != 2:
            raise RuntimeError(f"Goal5845 block {block} is incomplete")
        by_arm = {str(row["arm"]): row for row in matches}
        if set(by_arm) != {RTDL_ARM, PYOPTIX_ARM}:
            raise RuntimeError(f"Goal5845 block {block} arms differ")
        rtdl = _worker_median(by_arm[RTDL_ARM])
        pyoptix = _worker_median(by_arm[PYOPTIX_ARM])
        direct = int(
            by_arm[RTDL_ARM]["measurements"]["attribution"][
                "direct_native_v8"
            ]["median_ns"]
        )
        ratio = rtdl / pyoptix
        overhead = rtdl / direct
        public_over_direct.append(overhead)
        blocks.append({
            "block": block,
            "rtdl_median_ns": rtdl,
            "pyoptix_median_ns": pyoptix,
            "direct_native_v8_median_ns": direct,
            "rtdl_over_pyoptix": ratio,
            "rtdl_public_over_direct_native": overhead,
            "order": [
                item["arm"]
                for item in schedule
                if item["block"] == block
            ],
        })
    ratios = [float(row["rtdl_over_pyoptix"]) for row in blocks]
    primary = float(statistics.median(ratios))
    worst = max(ratios)
    public_direct = float(statistics.median(public_over_direct))
    rtdl_samples = _samples(rows, RTDL_ARM)
    pyoptix_samples = _samples(rows, PYOPTIX_ARM)
    expected_samples = args.blocks * args.repetitions
    gates = {
        "all_workers_passed": len(rows) == args.blocks * 2,
        "all_samples_retained": (
            len(rtdl_samples) == expected_samples
            and len(pyoptix_samples) == expected_samples
        ),
        "median_within_block_ratio_at_most_1_25": (
            primary <= PRIMARY_RATIO_LIMIT
        ),
        "worst_block_ratio_at_most_1_50": worst <= WORST_BLOCK_RATIO_LIMIT,
        "median_public_over_direct_at_most_1_75": (
            public_direct <= PUBLIC_OVER_DIRECT_LIMIT
        ),
    }
    passed = all(gates.values())
    result: dict[str, object] = {
        "schema": "rtdl.goal5845.relation_compact_execution.summary.v1",
        "status": (
            "PASS__GOAL5845_INTERNAL_PERFORMANCE_TARGET_MET"
            if passed
            else "FAIL__GOAL5845_INTERNAL_PERFORMANCE_TARGET_NOT_MET"
        ),
        "source_commit": args.expected_source_commit,
        "source_tree": _git_value("rev-parse", "HEAD^{tree}"),
        "hardware": hardware,
        "task": {
            "id": RELATION_TASK,
            "query_count": 4096,
            "row_count": 4096,
            "public_contract": "canonical_u32_relation_rows",
            "same_input_and_output_contract": True,
        },
        "design": {
            "blocks": args.blocks,
            "warmups_per_worker": args.warmups,
            "samples_per_worker": args.repetitions,
            "samples_per_arm": expected_samples,
            "balanced_alternating_order": True,
            "fresh_process_per_arm_per_block": True,
            "sample_discard_count": 0,
            "schedule": schedule,
        },
        "primary_estimand": {
            "name": "median_within_block_rtdl_over_pyoptix",
            "value": primary,
            "pass_limit": PRIMARY_RATIO_LIMIT,
        },
        "secondary_estimands": {
            "worst_block_rtdl_over_pyoptix": worst,
            "worst_block_pass_limit": WORST_BLOCK_RATIO_LIMIT,
            "median_rtdl_public_over_direct_native": public_direct,
            "public_over_direct_pass_limit": PUBLIC_OVER_DIRECT_LIMIT,
            "pooled_rtdl_median_ns": int(statistics.median(rtdl_samples)),
            "pooled_pyoptix_median_ns": int(statistics.median(pyoptix_samples)),
        },
        "blocks": blocks,
        "gates": gates,
        "workers": rows,
        "provenance": {
            "preregistration": {
                "path": str(args.preregistration.resolve(strict=True)),
                "sha256": _sha256_file(args.preregistration),
                "preregistration_sha256": args.preregistration_value[
                    "preregistration_sha256"
                ],
            },
            "native_library": {
                "path": str(args.native.resolve(strict=True)),
                "bytes": args.native.stat().st_size,
                "sha256": _sha256_file(args.native),
                "required_symbol": V8_SYMBOL,
            },
            "native_build_manifest": {
                "path": str(args.native_build_manifest.resolve(strict=True)),
                "sha256": _sha256_file(args.native_build_manifest),
            },
            "device_source": {
                "path": str(args.device_source.resolve(strict=True)),
                "sha256": _sha256_file(args.device_source),
            },
            "pyoptix_source": {
                "path": str(args.pyoptix_source.resolve(strict=True)),
                "commit": PYOPTIX_COMMIT,
                "tree": PYOPTIX_TREE,
            },
            "pyoptix_build_receipt": {
                "path": str(args.pyoptix_build_receipt.resolve(strict=True)),
                "sha256": _sha256_file(args.pyoptix_build_receipt),
            },
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "cross_hardware_generalization_authorized": False,
        },
    }
    result["summary_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--blocks", type=int, default=8)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--layer-warmups", type=int, default=8)
    parser.add_argument("--layer-repetitions", type=int, default=64)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks < 2 or args.blocks % 2 or min(
        args.warmups,
        args.repetitions,
        args.layer_warmups,
        args.layer_repetitions,
    ) <= 0:
        raise ValueError("Goal5845 balanced timing design is invalid")
    if args.output_root.exists() or args.output_root.is_symlink():
        raise FileExistsError(args.output_root)
    _require_outside_repository(args.output_root)
    if _git_value("status", "--porcelain"):
        raise RuntimeError("Goal5845 controller requires a clean source checkout")
    if _git_value("rev-parse", "HEAD") != args.expected_source_commit:
        raise RuntimeError("Goal5845 source commit binding differs")
    if not Path(args.python).resolve(strict=True).is_file():
        raise RuntimeError("Goal5845 Python executable is absent")
    args.preregistration_value = _validate_preregistration(
        args.preregistration, args
    )
    _validate_native_build_manifest(
        args.native_build_manifest,
        args.native,
        source_commit=args.expected_source_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    symbols = subprocess.run(
        ["nm", "-D", "--defined-only", str(args.native.resolve(strict=True))],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if V8_SYMBOL not in {line.split()[-1] for line in symbols.splitlines() if line.split()}:
        raise RuntimeError("Goal5845 native DSO lacks relation v8")
    validate_pyoptix_build_receipt(args.pyoptix_build_receipt.resolve(strict=True))
    hardware = _hardware()
    if hardware["compute_capability"] != args.compute_capability:
        raise RuntimeError("Goal5845 controller GPU capability differs")
    args.cache_root.mkdir(parents=True, exist_ok=True)
    args.output_root.mkdir(parents=True)
    workers_root = args.output_root / "workers"
    workers_root.mkdir()
    schedule = expected_schedule(args.blocks)
    rows: list[dict[str, object]] = []
    for item in schedule:
        arm = str(item["arm"])
        block = int(item["block"])
        label = "rtdl" if arm == RTDL_ARM else "pyoptix"
        output = workers_root / f"block_{block:02d}_{label}.json"
        rows.append(
            _run_worker(
                args,
                arm=arm,
                block=block,
                output=output,
                hardware=hardware,
            )
        )
    summary = build_summary(
        args,
        rows,
        schedule=schedule,
        hardware=hardware,
    )
    summary_path = args.output_root / "SUMMARY.json"
    write_json_create(summary_path, summary)
    print(json.dumps(summary, sort_keys=True))
    if not str(summary["status"]).startswith("PASS__"):
        raise RuntimeError("Goal5845 preregistered performance target failed")


if __name__ == "__main__":
    main()
