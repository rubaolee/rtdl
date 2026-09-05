"""One fresh RTDL or pinned-PyOptiX bounded-relation startup worker."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from experiments.goal5842_causal_admission.contracts import RELATION_TASK, digest
from experiments.goal5842_causal_admission.tasks import build_task
from experiments.goal5844_compact_execution.provenance import write_json_create
from experiments.goal5845_relation_compact_execution.worker import (
    PYOPTIX_ARM,
    _git_identity,
    _hardware,
    _measure,
    _run_pyoptix,
    _sample,
    _summary,
)
from scripts.goal5844_run_gpu_engineering_comparison import (
    _validate_native_build_manifest,
)


RTDL_ARM = "RTDL_PUBLIC_RELATION_OVERLAPPED_WARM_CACHE_V1"
ARMS = (RTDL_ARM, PYOPTIX_ARM)


def _sha256_file(path: Path) -> str:
    digest_value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest_value.update(block)
    return digest_value.hexdigest()


def _cache_snapshot(root: Path) -> tuple[tuple[str, int, str], ...]:
    resolved = root.resolve(strict=True)
    rows = []
    for path in sorted(resolved.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"Goal5846 cache contains a symlink: {path}")
        if path.is_file():
            rows.append((
                path.relative_to(resolved).as_posix(),
                path.stat().st_size,
                _sha256_file(path),
            ))
    if not rows:
        raise RuntimeError(f"Goal5846 sealed cache is empty: {resolved}")
    return tuple(rows)


def _run_rtdl(args: argparse.Namespace, task: object) -> dict[str, object]:
    from rtdsl import v4_bounded_relation_prepared_runtime as relation_runtime
    from rtdsl.physical_execution_provenance import (
        validate_bound_compact_traversal_receipt,
    )
    from rtdsl.v4 import (
        FormalNumbaLeafCachePolicy,
        V4ExecutableCachePolicy,
        V4Target,
        V4Toolchain,
    )

    leaf_before = _cache_snapshot(args.leaf_cache_root)
    executable_before = _cache_snapshot(args.executable_cache_root)
    native = args.native.resolve(strict=True)
    native_build_manifest = args.native_build_manifest.resolve(strict=True)
    _validate_native_build_manifest(
        native_build_manifest,
        native,
        source_commit=args.expected_source_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    capability = tuple(int(part) for part in args.compute_capability.split("."))
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=FormalNumbaLeafCachePolicy(
            args.leaf_cache_root,
            args.leaf_cache_manifest.resolve(strict=True),
            args.leaf_cache_manifest_sha256,
        ),
        executable_cache=V4ExecutableCachePolicy(
            args.executable_cache_root,
            args.executable_cache_manifest.resolve(strict=True),
            args.executable_cache_manifest_sha256,
        ),
    )
    toolchain, initialization_start_ns = _measure(
        lambda: toolchain.begin_native_initialization(target)
    )
    route, route_ns = _measure(task.route_factory)
    program, admission_ns = _measure(route.compile)
    materialized, materialize_ns = _measure(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    prepared, prepare_ns = _measure(
        lambda: materialized.prepare(task.static_input)
    )
    expected = task.expected_output
    expected_sha256 = digest(expected)
    raygen_count = len(task.batch.source_boxes) + len(
        task.static_input.indexed_boxes
    )

    def validate(result: object) -> None:
        if (
            type(result.output) is not relation_runtime.ValidatedBoundedRelationRows
            or result.output != expected
            or result.output_sha256 != expected_sha256
        ):
            raise RuntimeError("Goal5846 RTDL output differs from exact oracle")
        relation_runtime.validate_bound_relation_rows(
            result.output, output_sha256=expected_sha256
        )
        validate_bound_compact_traversal_receipt(
            result.traversal_receipt,
            provider_library_sha256=materialized.identity.provider_artifact_sha256,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=expected_sha256,
            expected_program_bundle="v4_custom_aabb_bounded_relation_composed",
            expected_raygen_invocation_count=raygen_count,
            expected_successful_launch_count=2,
        )

    try:
        first, first_ns = _measure(lambda: prepared.execute(task.batch))
        validate(first)
        retained_output = first.output
        steady_samples, latest = _sample(
            lambda: prepared.execute(task.batch),
            validate,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        if latest.output is not retained_output:
            raise RuntimeError("Goal5846 RTDL immutable output was not reused")
        latest_receipt = dict(latest.traversal_receipt)
    finally:
        prepared.close()

    phases = {
        "native_initialization_start": initialization_start_ns,
        "route_declaration": route_ns,
        "generic_admission": admission_ns,
        "materialize": materialize_ns,
        "prepare": prepare_ns,
        "first_public_execution": first_ns,
    }
    leaf_after = _cache_snapshot(args.leaf_cache_root)
    executable_after = _cache_snapshot(args.executable_cache_root)
    if leaf_after != leaf_before or executable_after != executable_before:
        raise RuntimeError("Goal5846 sealed cache changed during worker")
    return {
        "setup_plus_first_ns": sum(phases.values()),
        "setup_ns": phases,
        "first_execution_ns": first_ns,
        "steady_public": _summary(steady_samples),
        "identity": {
            "native_library_sha256": _sha256_file(native),
            "native_build_manifest_sha256": _sha256_file(
                native_build_manifest
            ),
            "generic_executable_identity": materialized.identity.to_dict(),
            "leaf_cache_manifest_sha256": args.leaf_cache_manifest_sha256,
            "executable_cache_manifest_sha256": (
                args.executable_cache_manifest_sha256
            ),
        },
        "evidence": {
            "public_output_sha256": expected_sha256,
            "public_row_count": len(expected),
            "latest_compact_receipt": latest_receipt,
            "immutable_output_reused": True,
            "two_actual_optix_launches": True,
            "sealed_caches_unchanged": True,
        },
    }


def _run_pinned_pyoptix(
    args: argparse.Namespace, task: object
) -> dict[str, object]:
    result = _run_pyoptix(args, task)
    setup = result["setup_ns"]
    result["setup_plus_first_ns"] = (
        int(setup["device_compile"])
        + int(setup["pipeline"])
        + int(setup["prepare"])
        + int(result["first_execution_ns"])
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--expected-source-commit", required=True)
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
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--layer-warmups", type=int, default=1)
    parser.add_argument("--layer-repetitions", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.block < 0 or min(args.warmups, args.repetitions) <= 0:
        raise ValueError("Goal5846 timing arguments are invalid")
    root = Path(__file__).resolve().parents[2]
    source = _git_identity(root)
    if source["clean"] is not True or source["commit"] != args.expected_source_commit:
        raise RuntimeError("Goal5846 worker requires exact clean source commit")
    hardware_before = _hardware()
    if hardware_before["compute_capability"] != args.compute_capability:
        raise RuntimeError("Goal5846 compute capability differs")
    task = build_task(RELATION_TASK)
    measurements = (
        _run_rtdl(args, task)
        if args.arm == RTDL_ARM
        else _run_pinned_pyoptix(args, task)
    )
    if _hardware() != hardware_before:
        raise RuntimeError("Goal5846 GPU identity changed during worker")
    result: dict[str, object] = {
        "schema": "rtdl.goal5846.relation_startup.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source["commit"],
        "source_tree": source["tree"],
        "arm": args.arm,
        "block": args.block,
        "python": sys.version.split()[0],
        "hardware": hardware_before,
        "task": RELATION_TASK,
        "query_count": len(task.batch.source_boxes),
        "row_count": len(task.expected_output),
        "output_sha256": digest(task.expected_output),
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "measurements": measurements,
        "claim_boundary": {
            "engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    write_json_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
