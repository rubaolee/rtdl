#!/usr/bin/env python3
"""Run the preregistered Goal5846 fresh-process startup comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess

from experiments.goal5842_causal_admission.contracts import RELATION_TASK, digest
from experiments.goal5844_compact_execution.provenance import (
    validate_pyoptix_build_receipt,
    write_json_create,
)
from experiments.goal5845_relation_compact_execution.worker import (
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    _hardware,
)
from experiments.goal5846_relation_startup.worker import (
    PYOPTIX_ARM,
    RTDL_ARM,
)
from scripts.goal5844_run_gpu_engineering_comparison import (
    _validate_native_build_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
STARTUP_RATIO_LIMIT = 1.25
WORST_STARTUP_RATIO_LIMIT = 2.0
GOAL5845_STEADY_REFERENCE_NS = 366_340
STEADY_MEDIAN_REGRESSION_LIMIT = 1.15
STEADY_WORST_WORKER_REGRESSION_LIMIT = 1.25
WARM_SYMBOL = "rtdl_optix_v4_warm_runtime_v1"
RELATION_SYMBOL = "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8"


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _outside_repository(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    candidate = absolute.parent.resolve(strict=True) / absolute.name
    try:
        candidate.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        return candidate
    raise RuntimeError("Goal5846 formal output must remain outside Git")


def _sealed_json(path: Path, field: str, label: str) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Goal5846 {label} must be an object")
    body = dict(value)
    observed = body.pop(field, None)
    if type(observed) is not str or observed != digest(body):
        raise RuntimeError(f"Goal5846 {label} seal differs")
    return value


def _validate_preregistration(
    path: Path, args: argparse.Namespace
) -> dict[str, object]:
    value = _sealed_json(path, "preregistration_sha256", "preregistration")
    design = value.get("design")
    gates = value.get("pass_gates")
    if (
        value.get("schema")
            != "rtdl.goal5846.relation_startup_preregistration.v1"
        or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION"
        or not isinstance(design, dict)
        or design.get("blocks") != args.blocks
        or design.get("warmups_per_worker") != args.warmups
        or design.get("samples_per_worker") != args.repetitions
        or design.get("samples_per_arm") != args.blocks * args.repetitions
        or design.get("sample_discard_count") != 0
        or design.get("fresh_process_per_arm_per_block") is not True
        or design.get("balanced_alternating_order") is not True
        or not isinstance(gates, dict)
        or gates.get("median_within_block_setup_ratio_at_most")
            != STARTUP_RATIO_LIMIT
        or gates.get("worst_block_setup_ratio_at_most")
            != WORST_STARTUP_RATIO_LIMIT
        or gates.get("goal5845_steady_reference_ns")
            != GOAL5845_STEADY_REFERENCE_NS
        or gates.get("pooled_rtdl_steady_regression_at_most")
            != STEADY_MEDIAN_REGRESSION_LIMIT
        or gates.get("worst_worker_rtdl_steady_regression_at_most")
            != STEADY_WORST_WORKER_REGRESSION_LIMIT
    ):
        raise RuntimeError("Goal5846 command differs from frozen design")
    return value


def _validate_cache_preparation(
    args: argparse.Namespace,
) -> dict[str, object]:
    value = _sealed_json(
        args.cache_preparation,
        "preparation_sha256",
        "cache preparation",
    )
    leaf = value.get("leaf_cache")
    executable = value.get("executable_cache")
    native_build_manifest = value.get("native_build_manifest")
    if (
        value.get("schema")
            != "rtdl.goal5846.relation_startup_cache_preparation.v1"
        or value.get("status")
            != "PASS__FIRST_FILL_SEALED_AND_HIT_ONLY_REPLAY"
        or value.get("source_commit") != args.expected_source_commit
        or value.get("task") != RELATION_TASK
        or not isinstance(leaf, dict)
        or not isinstance(executable, dict)
        or not isinstance(native_build_manifest, dict)
        or leaf.get("root") != str(args.leaf_cache_root.resolve(strict=True))
        or leaf.get("manifest")
            != str(args.leaf_cache_manifest.resolve(strict=True))
        or leaf.get("manifest_sha256")
            != args.leaf_cache_manifest_sha256
        or executable.get("root")
            != str(args.executable_cache_root.resolve(strict=True))
        or executable.get("manifest")
            != str(args.executable_cache_manifest.resolve(strict=True))
        or executable.get("manifest_sha256")
            != args.executable_cache_manifest_sha256
        or native_build_manifest.get("path")
            != str(args.native_build_manifest.resolve(strict=True))
        or native_build_manifest.get("sha256")
            != _sha256_file(args.native_build_manifest.resolve(strict=True))
        or value.get("claim_boundary") != {
            "cache_fill_excluded_from_formal_estimand": True,
            "gpu_execution_performed": False,
            "public_or_manuscript_claim_authorized": False,
        }
    ):
        raise RuntimeError("Goal5846 cache preparation binding differs")
    for path, expected in (
        (args.leaf_cache_manifest, args.leaf_cache_manifest_sha256),
        (
            args.executable_cache_manifest,
            args.executable_cache_manifest_sha256,
        ),
    ):
        if _sha256_file(path.resolve(strict=True)) != expected:
            raise RuntimeError("Goal5846 cache manifest bytes differ")
    return value


def _validate_timing(value: object, expected_count: int, label: str) -> list[int]:
    fields = {
        "sample_count",
        "samples_ns",
        "minimum_ns",
        "median_ns",
        "maximum_ns",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise RuntimeError(f"Goal5846 {label} timing schema differs")
    samples = value.get("samples_ns")
    if (
        value.get("sample_count") != expected_count
        or not isinstance(samples, list)
        or len(samples) != expected_count
        or any(type(item) is not int or item <= 0 for item in samples)
        or value.get("minimum_ns") != min(samples)
        or value.get("median_ns") != int(statistics.median(samples))
        or value.get("maximum_ns") != max(samples)
    ):
        raise RuntimeError(f"Goal5846 {label} timing values differ")
    return [int(item) for item in samples]


def expected_schedule(blocks: int) -> list[dict[str, object]]:
    rows = []
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
    value: object,
    *,
    args: argparse.Namespace,
    arm: str,
    block: int,
    hardware: dict[str, object],
) -> dict[str, object]:
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    if not isinstance(value, dict):
        raise TypeError("Goal5846 worker must be an object")
    body = dict(value)
    observed = body.pop("result_sha256", None)
    if type(observed) is not str or observed != digest(body):
        raise RuntimeError("Goal5846 worker seal differs")
    exact = {
        "schema": "rtdl.goal5846.relation_startup.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": args.expected_source_commit,
        "arm": arm,
        "block": block,
        "hardware": hardware,
        "task": RELATION_TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
    }
    if any(value.get(key) != expected for key, expected in exact.items()):
        raise RuntimeError("Goal5846 worker exact fields differ")
    if value.get("claim_boundary") != {
        "engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
        "external_review_complete": False,
    }:
        raise RuntimeError("Goal5846 worker claim boundary differs")
    measurements = value.get("measurements")
    if not isinstance(measurements, dict):
        raise RuntimeError("Goal5846 worker measurements are absent")
    _validate_timing(
        measurements.get("steady_public"),
        args.repetitions,
        f"{arm}.steady_public",
    )
    setup = measurements.get("setup_ns")
    identity = measurements.get("identity")
    evidence = measurements.get("evidence")
    if not all(isinstance(item, dict) for item in (setup, identity, evidence)):
        raise RuntimeError("Goal5846 worker components are malformed")
    first_ns = measurements.get("first_execution_ns")
    setup_total = measurements.get("setup_plus_first_ns")
    if type(first_ns) is not int or first_ns <= 0 \
            or type(setup_total) is not int or setup_total <= 0:
        raise RuntimeError("Goal5846 setup or first timing is invalid")
    if arm == RTDL_ARM:
        expected_phases = {
            "native_initialization_start",
            "route_declaration",
            "generic_admission",
            "materialize",
            "prepare",
            "first_public_execution",
        }
        if set(setup) != expected_phases or any(
            type(setup[key]) is not int or setup[key] <= 0
            for key in expected_phases
        ) or sum(int(item) for item in setup.values()) != setup_total \
                or setup["first_public_execution"] != first_ns:
            raise RuntimeError("Goal5846 RTDL phase timing differs")
        native_sha = _sha256_file(args.native.resolve(strict=True))
        executable_identity = identity.get("generic_executable_identity")
        if (
            identity.get("native_library_sha256") != native_sha
            or identity.get("native_build_manifest_sha256")
                != _sha256_file(
                    args.native_build_manifest.resolve(strict=True)
                )
            or identity.get("leaf_cache_manifest_sha256")
                != args.leaf_cache_manifest_sha256
            or identity.get("executable_cache_manifest_sha256")
                != args.executable_cache_manifest_sha256
            or not isinstance(executable_identity, dict)
            or executable_identity.get("provider_artifact_sha256") != native_sha
            or evidence.get("public_output_sha256")
                != value.get("output_sha256")
            or evidence.get("public_row_count") != 4096
            or evidence.get("immutable_output_reused") is not True
            or evidence.get("two_actual_optix_launches") is not True
            or evidence.get("sealed_caches_unchanged") is not True
        ):
            raise RuntimeError("Goal5846 RTDL identity/evidence differs")
        receipt = evidence.get("latest_compact_receipt")
        validate_traversal_receipt(
            receipt,
            provider_library_sha256=native_sha,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=str(value["output_sha256"]),
            expected_program_bundles=(
                "v4_custom_aabb_bounded_relation_composed",
            ),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=8192,
        )
    elif arm == PYOPTIX_ARM:
        timed_phases = {"device_compile", "pipeline", "prepare"}
        if set(setup) != timed_phases | {"close"} or any(
            type(setup[key]) is not int or setup[key] <= 0
            for key in set(setup)
        ) or sum(int(setup[key]) for key in timed_phases) + first_ns \
                != setup_total:
            raise RuntimeError("Goal5846 PyOptiX phase timing differs")
        source = identity.get("pyoptix_repository")
        build = validate_pyoptix_build_receipt(
            args.pyoptix_build_receipt.resolve(strict=True)
        )
        extension = identity.get("loaded_extension")
        if (
            evidence.get("public_output_sha256")
                != value.get("output_sha256")
            or evidence.get("public_row_count") != 4096
            or evidence.get("device_status") != 0
            or evidence.get("device_overflow") != 0
            or not isinstance(source, dict)
            or source.get("commit") != PYOPTIX_COMMIT
            or source.get("tree") != PYOPTIX_TREE
            or source.get("clean") is not True
            or identity.get("optix_api_version") != args.optix_sdk
            or identity.get("pyoptix_build_receipt_sha256")
                != build["receipt_sha256"]
            or not isinstance(extension, dict)
            or extension.get("sha256")
                != build["installed"]["loaded_extension"]["sha256"]
        ):
            raise RuntimeError("Goal5846 PyOptiX identity/evidence differs")
    else:
        raise RuntimeError(f"Goal5846 unknown arm: {arm}")
    return value


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
        "experiments.goal5846_relation_startup.worker",
        "--arm", arm,
        "--block", str(block),
        "--expected-source-commit", args.expected_source_commit,
        "--native", str(args.native.resolve()),
        "--native-build-manifest", str(args.native_build_manifest.resolve()),
        "--device-source", str(args.device_source.resolve()),
        "--optix-include", str(args.optix_include.resolve()),
        "--cuda-include", str(args.cuda_include.resolve()),
        "--optix-sdk", args.optix_sdk,
        "--compute-capability", args.compute_capability,
        "--leaf-cache-root", str(args.leaf_cache_root.resolve()),
        "--leaf-cache-manifest", str(args.leaf_cache_manifest.resolve()),
        "--leaf-cache-manifest-sha256", args.leaf_cache_manifest_sha256,
        "--executable-cache-root", str(args.executable_cache_root.resolve()),
        "--executable-cache-manifest",
        str(args.executable_cache_manifest.resolve()),
        "--executable-cache-manifest-sha256",
        args.executable_cache_manifest_sha256,
        "--pyoptix-distribution", args.pyoptix_distribution,
        "--pyoptix-source", str(args.pyoptix_source.resolve()),
        "--pyoptix-build-receipt", str(args.pyoptix_build_receipt.resolve()),
        "--warmups", str(args.warmups),
        "--repetitions", str(args.repetitions),
        "--output", str(output.resolve()),
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
            f"Goal5846 worker failed: block={block} arm={arm} "
            f"returncode={completed.returncode}"
        )
    return _validate_worker(
        json.loads(output.read_text(encoding="utf-8")),
        args=args,
        arm=arm,
        block=block,
        hardware=hardware,
    )


def _worker_setup(row: dict[str, object]) -> int:
    return int(row["measurements"]["setup_plus_first_ns"])


def _worker_steady(row: dict[str, object]) -> int:
    return int(row["measurements"]["steady_public"]["median_ns"])


def _all_samples(rows: list[dict[str, object]], arm: str) -> list[int]:
    result = []
    for row in rows:
        if row["arm"] == arm:
            result.extend(
                int(item)
                for item in row["measurements"]["steady_public"]["samples_ns"]
            )
    return result


def build_summary(
    args: argparse.Namespace,
    rows: list[dict[str, object]],
    schedule: list[dict[str, object]],
    hardware: dict[str, object],
) -> dict[str, object]:
    blocks = []
    for block in range(args.blocks):
        matches = [row for row in rows if row["block"] == block]
        by_arm = {str(row["arm"]): row for row in matches}
        if len(matches) != 2 or set(by_arm) != {RTDL_ARM, PYOPTIX_ARM}:
            raise RuntimeError(f"Goal5846 block {block} is incomplete")
        rtdl_setup = _worker_setup(by_arm[RTDL_ARM])
        pyoptix_setup = _worker_setup(by_arm[PYOPTIX_ARM])
        rtdl_steady = _worker_steady(by_arm[RTDL_ARM])
        blocks.append({
            "block": block,
            "order": [
                row["arm"] for row in schedule if row["block"] == block
            ],
            "rtdl_setup_plus_first_ns": rtdl_setup,
            "pyoptix_setup_plus_first_ns": pyoptix_setup,
            "rtdl_over_pyoptix_setup_plus_first": (
                rtdl_setup / pyoptix_setup
            ),
            "rtdl_steady_median_ns": rtdl_steady,
            "rtdl_steady_over_goal5845_reference": (
                rtdl_steady / GOAL5845_STEADY_REFERENCE_NS
            ),
        })
    setup_ratios = [
        float(row["rtdl_over_pyoptix_setup_plus_first"])
        for row in blocks
    ]
    steady_regressions = [
        float(row["rtdl_steady_over_goal5845_reference"])
        for row in blocks
    ]
    rtdl_samples = _all_samples(rows, RTDL_ARM)
    pyoptix_samples = _all_samples(rows, PYOPTIX_ARM)
    expected_samples = args.blocks * args.repetitions
    primary = float(statistics.median(setup_ratios))
    worst_setup = max(setup_ratios)
    pooled_rtdl_steady = int(statistics.median(rtdl_samples))
    pooled_pyoptix_steady = int(statistics.median(pyoptix_samples))
    gates = {
        "all_workers_passed": len(rows) == args.blocks * 2,
        "all_registered_samples_retained": (
            len(rtdl_samples) == expected_samples
            and len(pyoptix_samples) == expected_samples
        ),
        "median_setup_ratio_at_most_1_25": primary <= STARTUP_RATIO_LIMIT,
        "worst_setup_ratio_at_most_2_0": (
            worst_setup <= WORST_STARTUP_RATIO_LIMIT
        ),
        "pooled_rtdl_steady_regression_at_most_1_15": (
            pooled_rtdl_steady / GOAL5845_STEADY_REFERENCE_NS
            <= STEADY_MEDIAN_REGRESSION_LIMIT
        ),
        "worst_worker_rtdl_steady_regression_at_most_1_25": (
            max(steady_regressions)
            <= STEADY_WORST_WORKER_REGRESSION_LIMIT
        ),
    }
    passed = all(gates.values())
    result: dict[str, object] = {
        "schema": "rtdl.goal5846.relation_startup.summary.v1",
        "status": (
            "PASS__GOAL5846_INTERNAL_STARTUP_TARGET_MET"
            if passed
            else "FAIL__GOAL5846_INTERNAL_STARTUP_TARGET_NOT_MET"
        ),
        "source_commit": args.expected_source_commit,
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
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
            "name": "median_within_block_rtdl_over_pyoptix_setup_plus_first",
            "value": primary,
            "pass_limit": STARTUP_RATIO_LIMIT,
        },
        "secondary_estimands": {
            "worst_block_setup_ratio": worst_setup,
            "worst_block_setup_ratio_limit": WORST_STARTUP_RATIO_LIMIT,
            "pooled_rtdl_steady_median_ns": pooled_rtdl_steady,
            "pooled_pyoptix_steady_median_ns": pooled_pyoptix_steady,
            "goal5845_rtdl_steady_reference_ns": (
                GOAL5845_STEADY_REFERENCE_NS
            ),
            "pooled_rtdl_steady_regression": (
                pooled_rtdl_steady / GOAL5845_STEADY_REFERENCE_NS
            ),
            "worst_worker_rtdl_steady_regression": max(steady_regressions),
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
            "cache_preparation": {
                "path": str(args.cache_preparation.resolve(strict=True)),
                "sha256": _sha256_file(args.cache_preparation),
                "preparation_sha256": args.cache_preparation_value[
                    "preparation_sha256"
                ],
            },
            "native_library": {
                "path": str(args.native.resolve(strict=True)),
                "bytes": args.native.stat().st_size,
                "sha256": _sha256_file(args.native),
                "required_symbols": [WARM_SYMBOL, RELATION_SYMBOL],
            },
            "native_build_manifest": {
                "path": str(args.native_build_manifest.resolve(strict=True)),
                "sha256": _sha256_file(args.native_build_manifest),
            },
            "leaf_cache_manifest": {
                "path": str(args.leaf_cache_manifest.resolve(strict=True)),
                "sha256": args.leaf_cache_manifest_sha256,
            },
            "executable_cache_manifest": {
                "path": str(args.executable_cache_manifest.resolve(strict=True)),
                "sha256": args.executable_cache_manifest_sha256,
            },
            "device_source": {
                "path": str(args.device_source.resolve(strict=True)),
                "sha256": _sha256_file(args.device_source),
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
            "precompiled_pyoptix_sensitivity_is_separate": True,
        },
    }
    result["summary_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--cache-preparation", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--leaf-cache-root", type=Path, required=True)
    parser.add_argument("--leaf-cache-manifest", type=Path, required=True)
    parser.add_argument("--leaf-cache-manifest-sha256", required=True)
    parser.add_argument("--executable-cache-root", type=Path, required=True)
    parser.add_argument("--executable-cache-manifest", type=Path, required=True)
    parser.add_argument("--executable-cache-manifest-sha256", required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--blocks", type=int, default=8)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if args.blocks < 2 or args.blocks % 2 or min(
        args.warmups, args.repetitions
    ) <= 0:
        raise ValueError("Goal5846 balanced design is invalid")
    args.output_root = _outside_repository(args.output_root)
    if args.output_root.exists() or args.output_root.is_symlink():
        raise FileExistsError(args.output_root)
    if _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5846 controller requires clean source")
    if _git("rev-parse", "HEAD") != args.expected_source_commit:
        raise RuntimeError("Goal5846 controller source differs")
    if not Path(args.python).resolve(strict=True).is_file():
        raise RuntimeError("Goal5846 Python executable is absent")
    args.preregistration_value = _validate_preregistration(
        args.preregistration, args
    )
    args.cache_preparation_value = _validate_cache_preparation(args)
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
    names = {line.split()[-1] for line in symbols.splitlines() if line.split()}
    if not {WARM_SYMBOL, RELATION_SYMBOL}.issubset(names):
        raise RuntimeError("Goal5846 native DSO lacks required symbols")
    validate_pyoptix_build_receipt(args.pyoptix_build_receipt.resolve(strict=True))
    hardware = _hardware()
    if hardware["compute_capability"] != args.compute_capability:
        raise RuntimeError("Goal5846 controller GPU capability differs")
    args.output_root.mkdir(parents=True)
    workers_root = args.output_root / "workers"
    workers_root.mkdir()
    schedule = expected_schedule(args.blocks)
    rows = []
    for item in schedule:
        arm = str(item["arm"])
        block = int(item["block"])
        label = "rtdl" if arm == RTDL_ARM else "pyoptix"
        output = workers_root / f"block_{block:02d}_{label}.json"
        rows.append(_run_worker(
            args,
            arm=arm,
            block=block,
            output=output,
            hardware=hardware,
        ))
    summary = build_summary(args, rows, schedule, hardware)
    write_json_create(args.output_root / "SUMMARY.json", summary)
    print(json.dumps(summary, sort_keys=True))
    if not str(summary["status"]).startswith("PASS__"):
        raise RuntimeError("Goal5846 preregistered performance target failed")


if __name__ == "__main__":
    main()
