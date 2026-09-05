"""One fresh-process RTDL-AOT or precompiled-PyOptix relation worker."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .contracts import (
    ARMS,
    PYOPTIX_COMMIT,
    PYOPTIX_TREE,
    RELATION_TASK,
    RTDL_ARM,
    digest,
)


def _measure(action: Callable[[], Any]) -> tuple[Any, int]:
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git_identity(path: Path) -> dict[str, object]:
    values: dict[str, str] = {}
    for label, command in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        values[label] = subprocess.run(
            ["git", "-C", str(path), *command],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return {**values, "clean": values["status"] == ""}


def _hardware() -> dict[str, object]:
    row = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            "--query-gpu=name,uuid,driver_version,memory.total,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()
    if len(row) != 1:
        raise RuntimeError("Goal5847 requires exactly one visible GPU")
    parts = [item.strip() for item in row[0].split(",")]
    if len(parts) != 5:
        raise RuntimeError("Goal5847 GPU identity row differs")
    return {
        "gpu_name": parts[0],
        "gpu_uuid": parts[1],
        "driver_version": parts[2],
        "memory_mib": int(parts[3]),
        "compute_capability": parts[4],
    }


def _summary(samples: list[int]) -> dict[str, object]:
    if not samples:
        raise ValueError("Goal5847 requires retained timing samples")
    return {
        "sample_count": len(samples),
        "samples_ns": samples,
        "minimum_ns": min(samples),
        "median_ns": int(statistics.median(samples)),
        "maximum_ns": max(samples),
    }


def _sample(
    action: Callable[[], object],
    validate: Callable[[object], None],
    *,
    warmups: int,
    repetitions: int,
) -> tuple[dict[str, object], object]:
    latest = None
    for _ in range(warmups):
        latest = action()
        validate(latest)
    values = []
    for _ in range(repetitions):
        latest, elapsed = _measure(action)
        validate(latest)
        values.append(elapsed)
    if latest is None:
        raise RuntimeError("Goal5847 timing loop produced no result")
    return _summary(values), latest


def _nvrtc_mappings() -> tuple[str, ...]:
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        return ()
    paths = set()
    for line in maps.read_text(encoding="utf-8", errors="replace").splitlines():
        if "nvrtc" in line.lower():
            candidate = line.rsplit(None, 1)[-1]
            paths.add(candidate)
    return tuple(sorted(paths))


def _compiler_modules() -> tuple[str, ...]:
    package_prefixes = (
        "numba.",
        "llvmlite.",
    )
    exact_names = (
        "numba",
        "llvmlite",
        "rtdsl.v4_callback_lifecycle",
        "rtdsl.v4_generic_family_lifecycle",
    )
    return tuple(sorted(
        name for name in sys.modules
        if name in exact_names or name.startswith(package_prefixes)
    ))


def _load_manifest(path: Path) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict) \
            or value.get("schema") != "rtdl.goal5847.aot_candidates.v1":
        raise RuntimeError("Goal5847 candidate manifest differs")
    return value


def _relation_fixture() -> tuple[dict[str, object], int]:
    from experiments.goal5798_premeasurement.workload import relation_workload

    return _measure(relation_workload)


def _validate_relation_rows(result: object, expected: tuple[tuple[int, int], ...]) -> None:
    output = getattr(result, "output", None)
    if output != expected or digest(output) != digest(expected):
        raise RuntimeError("Goal5847 relation output differs from exact oracle")


def _run_rtdl(args: argparse.Namespace) -> dict[str, object]:
    imported_started = time.perf_counter_ns()
    from rtdsl import v4_rtdlexe as runtime
    from rtdsl.physical_execution_provenance import validate_traversal_receipt
    import_ns = time.perf_counter_ns() - imported_started

    manifest = _load_manifest(args.candidate_manifest)
    rows = manifest.get("rows")
    if not isinstance(rows, dict) or not isinstance(rows.get("relation"), dict):
        raise TypeError("Goal5847 relation candidate is absent")
    candidate = rows["relation"]
    native = Path(str(manifest["native"])).resolve(strict=True)

    raw, fixture_ns = _relation_fixture()
    expected = tuple(tuple(int(item) for item in row) for row in raw["expected_rows"])
    phases: dict[str, int] = {
        "implementation_import": import_ns,
        "deterministic_input_materialization": fixture_ns,
    }

    deployment, phases["signed_deployment_install"] = _measure(
        lambda: runtime.install_rtdlexe_deployment(
            trust_root_path=Path(str(candidate["public"])),
            trust_head_path=Path(str(candidate["head"])),
            trust_package_path=Path(str(candidate["package"])),
            deployment_id=str(candidate["deployment_id"]),
        )
    )
    initializing, phases["provider_initialization_start"] = _measure(
        lambda: deployment.begin_provider_initialization(native)
    )
    provider = prepared = None
    try:
        loaded, phases["artifact_authority_load"] = _measure(
            lambda: runtime.load_rtdlexe(
                Path(str(candidate["artifact"])),
                authority_path=Path(str(candidate["authority"])),
                deployment=deployment,
            )
        )
        static_input, phases["deploy_static_input"] = _measure(
            lambda: runtime.BoundedRelationStaticInput(
                tuple(tuple(row) for row in raw["indexed"])
            )
        )
        batch, phases["deploy_dynamic_input"] = _measure(
            lambda: runtime.BoundedRelationBatch(
                tuple(tuple(row) for row in raw["sources"])
            )
        )
        provider, phases["provider_bind_and_initialization_join"] = _measure(
            lambda: initializing.bind(loaded)
        )
        prepared, phases["native_prepare"] = _measure(
            lambda: provider.prepare(static_input)
        )
        first, phases["first_complete_execution"] = _measure(
            lambda: prepared.execute(batch)
        )
        _validate_relation_rows(first, expected)
        correct_result_ns = time.perf_counter_ns()

        if _sha256_file(native) != manifest.get("native_sha256"):
            raise RuntimeError("Goal5847 native provider bytes differ")
        compiler_attempt_count_before = provider.runtime_compiler_attempt_count
        steady, latest = _sample(
            lambda: prepared.execute(batch),
            lambda value: _validate_relation_rows(value, expected),
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        _validate_relation_rows(latest, expected)
        # Collect audit evidence only after the timed steady sequence so this
        # extra diagnostic execution cannot precondition RTDL alone.
        diagnostic = prepared.execute(batch, include_diagnostics=True)
        _validate_relation_rows(diagnostic, expected)
        if (
            diagnostic.traversal_receipt is None
            or diagnostic.output_sha256 != digest(expected)
        ):
            raise RuntimeError("Goal5847 RTDL traversal evidence is absent")
        validate_traversal_receipt(
            diagnostic.traversal_receipt,
            provider_library_sha256=str(manifest["native_sha256"]),
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=digest(expected),
            expected_program_bundles=(
                "v4_custom_aabb_bounded_relation_composed",
            ),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=8192,
        )
        compiler_attempt_count_after = provider.runtime_compiler_attempt_count
        initialization_phases = dict(initializing.phase_timings_ns)
    finally:
        if prepared is not None:
            prepared.close()
        if provider is not None:
            provider.close()
        elif initializing.state not in {"BOUND", "CLOSED"}:
            initializing.close()

    compiler_modules = _compiler_modules()
    nvrtc_mappings = _nvrtc_mappings()
    if compiler_attempt_count_before != 0 \
            or compiler_attempt_count_after != 0 \
            or compiler_modules or nvrtc_mappings:
        raise RuntimeError("Goal5847 RTDL AOT path touched a runtime compiler")
    return {
        "correct_result_ns": correct_result_ns,
        "post_import_to_correct_result_ns": (
            correct_result_ns - imported_started - import_ns
        ),
        "phases_ns": phases,
        "steady_complete_execution": steady,
        "identity": {
            "artifact_sha256": _sha256_file(Path(str(candidate["artifact"]))),
            "authority_sha256": _sha256_file(Path(str(candidate["authority"]))),
            "native_library_sha256": _sha256_file(native),
            "family_executable_identity_sha256": (
                loaded.family_executable_identity_sha256
            ),
        },
        "evidence": {
            "output_sha256": digest(expected),
            "row_count": len(expected),
            "runtime_compiler_attempt_count_before": (
                compiler_attempt_count_before
            ),
            "runtime_compiler_attempt_count_after": (
                compiler_attempt_count_after
            ),
            "runtime_compiler_modules": list(compiler_modules),
            "nvrtc_mappings": list(nvrtc_mappings),
            "diagnostic_traversal_receipt": dict(
                diagnostic.traversal_receipt
            ),
            "provider_initialization_phases_ns": initialization_phases,
            "full_generic_family_identity_matched": (
                loaded.family_executable_identity_sha256
                == candidate["family_executable_identity_sha256"]
            ),
        },
    }


def _run_pyoptix(args: argparse.Namespace) -> dict[str, object]:
    imported_started = time.perf_counter_ns()
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
    )
    import_ns = time.perf_counter_ns() - imported_started

    if tuple(int(item) for item in baseline.optix.version()) != tuple(
            int(item) for item in args.optix_sdk.split(".")):
        raise RuntimeError("Goal5847 PyOptix API differs")

    raw, fixture_ns = _relation_fixture()
    expected = tuple(tuple(int(item) for item in row) for row in raw["expected_rows"])
    phases: dict[str, int] = {
        "implementation_import": import_ns,
        "deterministic_input_materialization": fixture_ns,
    }
    ptx_path = args.precompiled_ptx.resolve(strict=True)
    ptx, phases["precompiled_ptx_load"] = _measure(ptx_path.read_bytes)

    def make_context():
        baseline.cp.cuda.runtime.free(0)
        if hasattr(baseline.optix, "init"):
            baseline.optix.init()
        logger = baseline.Logger()
        options = baseline.optix.DeviceContextOptions(
            logCallbackFunction=logger,
            logCallbackLevel=4,
        )
        if baseline.optix.version()[1] >= 2:
            options.validationMode = (
                baseline.optix.DEVICE_CONTEXT_VALIDATION_MODE_OFF
            )
        return baseline.optix.deviceContextCreate(0, options), logger

    context, phases["cuda_optix_context"] = _measure(make_context)

    def make_pipeline():
        pipeline, groups, logs = baseline.build_pipeline(
            context, ptx, task="relation"
        )
        sbt, keepalive = baseline.make_sbt(groups)
        return pipeline, groups, logs, sbt, keepalive

    pipeline_state, phases["module_program_pipeline_sbt"] = _measure(
        make_pipeline
    )
    pipeline, groups, _logs, sbt, keepalive = pipeline_state
    prepared, phases["native_prepare"] = _measure(
        lambda: PyOptixRelationPrepared(
            baseline, context, pipeline, sbt, raw
        )
    )
    first, phases["first_complete_execution"] = _measure(
        lambda: prepared.execute(validate_expected=False)
    )

    def validate(result: object) -> None:
        if not isinstance(result, dict):
            raise TypeError("Goal5847 PyOptix result is not a mapping")
        output = tuple(
            tuple(int(item) for item in row) for row in result["output"]
        )
        if (
            output != expected
            or digest(output) != digest(expected)
            or int(result["device_status"]) != 0
            or int(result["device_overflow"]) != 0
        ):
            raise RuntimeError("Goal5847 PyOptix output differs from oracle")

    validate(first)
    correct_result_ns = time.perf_counter_ns()
    from experiments.goal5844_compact_execution.provenance import (
        validate_pyoptix_build_receipt,
    )

    build_receipt = validate_pyoptix_build_receipt(
        args.pyoptix_build_receipt.resolve(strict=True)
    )
    source = _git_identity(args.pyoptix_source.resolve(strict=True))
    if (
        source["commit"] != PYOPTIX_COMMIT
        or source["tree"] != PYOPTIX_TREE
        or source["clean"] is not True
        or baseline.PYOPTIX_COMMIT != PYOPTIX_COMMIT
    ):
        raise RuntimeError("Goal5847 pinned PyOptix source differs")
    extension = sys.modules.get("optix._optix")
    extension_path = Path(str(getattr(extension, "__file__", ""))).resolve(
        strict=True
    )
    extension_sha256 = _sha256_file(extension_path)
    bound_extension = build_receipt["installed"]["loaded_extension"]
    if (
        extension_path.stat().st_size != bound_extension["bytes"]
        or extension_sha256 != bound_extension["sha256"]
        or extension_sha256 != build_receipt["wheel"]["extension_sha256"]
    ):
        raise RuntimeError("Goal5847 loaded PyOptix extension differs")
    steady, latest = _sample(
        lambda: prepared.execute(validate_expected=False),
        validate,
        warmups=args.warmups,
        repetitions=args.repetitions,
    )
    validate(latest)
    # These handles deliberately remain strongly referenced through all samples.
    _ = (pipeline_state, groups, _logs, keepalive, context)

    return {
        "correct_result_ns": correct_result_ns,
        "post_import_to_correct_result_ns": (
            correct_result_ns - imported_started - import_ns
        ),
        "phases_ns": phases,
        "steady_complete_execution": steady,
        "identity": {
            "precompiled_ptx_sha256": hashlib.sha256(ptx).hexdigest(),
            "pyoptix_repository": source,
            "pyoptix_distribution": args.pyoptix_distribution,
            "pyoptix_distribution_version": importlib.metadata.version(
                args.pyoptix_distribution
            ),
            "loaded_extension": {
                "path": str(extension_path),
                "bytes": extension_path.stat().st_size,
                "sha256": extension_sha256,
            },
            "pyoptix_build_receipt_file_sha256": _sha256_file(
                args.pyoptix_build_receipt.resolve(strict=True)
            ),
            "pyoptix_build_receipt_internal_seal": (
                build_receipt["receipt_sha256"]
            ),
            "optix_api_version": ".".join(
                str(item) for item in baseline.optix.version()
            ),
        },
        "evidence": {
            "output_sha256": digest(expected),
            "row_count": len(expected),
            "device_status": int(latest["device_status"]),
            "device_overflow": int(latest["device_overflow"]),
            "raw_event_count": int(latest["raw_event_count"]),
            "nvrtc_mappings": list(_nvrtc_mappings()),
            "precompiled_ptx_means_harness_did_not_compile_source": True,
            "stack_wide_no_runtime_compiler_claimed": False,
        },
    }


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--precompiled-ptx", type=Path, required=True)
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.block < 0 or args.warmups <= 0 or args.repetitions <= 0:
        raise ValueError("Goal5847 timing arguments are invalid")
    controller_start_ns = int(os.environ["GOAL5847_CONTROLLER_START_NS"])
    if controller_start_ns <= 0 or controller_start_ns > time.perf_counter_ns():
        raise RuntimeError("Goal5847 controller start clock is invalid")
    root = Path(__file__).resolve().parents[2]
    measurements = (
        _run_rtdl(args) if args.arm == RTDL_ARM else _run_pyoptix(args)
    )
    process_to_correct = int(
        measurements.pop("correct_result_ns")
    ) - controller_start_ns
    if process_to_correct <= 0:
        raise RuntimeError("Goal5847 process timer is invalid")
    # Evidence collection belongs after the primary endpoint.  Git and
    # nvidia-smi subprocesses are experiment instrumentation, not deployment
    # startup work, and therefore must never contaminate that estimand.
    source = _git_identity(root)
    if (
        source["commit"] != args.expected_source_commit
        or source["clean"] is not True
    ):
        raise RuntimeError("Goal5847 worker requires exact clean Git source")
    hardware = _hardware()
    if hardware["compute_capability"] != args.compute_capability:
        raise RuntimeError("Goal5847 visible GPU target differs")
    result: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_startup.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source["commit"],
        "source_tree": source["tree"],
        "arm": args.arm,
        "block": args.block,
        "python": sys.version.split()[0],
        "hardware": hardware,
        "task": RELATION_TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "measurements": {
            **measurements,
            "process_spawn_to_correct_result_ns": process_to_correct,
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
