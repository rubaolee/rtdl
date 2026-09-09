#!/usr/bin/env python3
"""One-process diagnostic worker for source-authored Particle versus PyOptiX."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

import numpy as np

from experiments.v4_authored_particle.program import (
    FACE_FIRST_SOURCE,
    build_face_first_physical_plan,
    face_first_expected,
    face_first_manifest,
)
from experiments.v4_paper_apps_pyoptix.inputs import load_particle
from experiments.v4_paper_apps_pyoptix.particle_adapter import (
    validate_particle_app_input,
)


ROOT = Path(__file__).resolve().parents[1]


def validate_repetition_counts(*, warmups: int, samples: int) -> None:
    if warmups < 0:
        raise ValueError("warmups must be nonnegative")
    if samples < 1:
        raise ValueError("samples must be positive")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _output_digest(value: np.ndarray) -> str:
    value = np.ascontiguousarray(value, dtype=np.uint32)
    digest = hashlib.sha256()
    digest.update(value.dtype.str.encode("ascii"))
    digest.update(str(tuple(value.shape)).encode("ascii"))
    digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _machine() -> dict[str, object]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,uuid,driver_version,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError(f"worker requires exactly one visible GPU: {rows!r}")
    name, uuid, driver, capability = (item.strip() for item in rows[0].split(","))
    return {
        "hostname": platform.node(),
        "python": platform.python_version(),
        "gpu_name": name,
        "gpu_uuid": uuid,
        "driver": driver,
        "compute_capability": capability,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def _git_identity() -> dict[str, str]:
    def capture(*arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    if capture("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("authored Particle worker requires clean tracked source")
    return {
        "commit": capture("rev-parse", "HEAD"),
        "tree": capture("rev-parse", "HEAD^{tree}"),
    }


def _prepare_rtdl(args: argparse.Namespace, data: dict[str, object]):
    from rtdsl import v4

    native = args.native.resolve(strict=True)
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    verified = v4.verify_builtin_triangle_callback_source(
        FACE_FIRST_SOURCE, face_first_manifest())
    physical_plan = build_face_first_physical_plan(
        verified,
        independent_cpu_oracle_sha256=str(data["independent_oracle_sha256"]),
    )
    target = v4.V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    toolchain = v4.V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    program = verified.compile(physical_plan=physical_plan, target=target)
    materialized = program.materialize(toolchain=toolchain)
    arrays = validate_particle_app_input(data)
    static_input = v4.BuiltinTriangleCallbackStaticInput(
        vertices=arrays["vertices"],
        triangles=arrays["triangles"],
        first_primitive_values=arrays["front_values"],
        second_primitive_values=arrays["back_values"],
    )
    owner = materialized.prepare(static_input)
    batch = v4.BuiltinTriangleCallbackBatch(queries=arrays["queries"])
    prepared_batch = owner.prepare_batch(batch)
    expected = face_first_expected(arrays["expected"])

    def invoke() -> tuple[np.ndarray, object]:
        result = owner.execute(prepared_batch)
        output = np.asarray(result.output, dtype=np.uint32)
        if not np.array_equal(output, expected):
            raise RuntimeError("source-authored RTDL Particle output mismatch")
        return output, result

    def finish(pending: tuple[np.ndarray, object]) -> tuple[np.ndarray, object]:
        return pending

    def observe(result: object) -> dict[str, object]:
        return {
            "output_sha256": result.output_sha256,
            "traversal_receipt_sha256": result.traversal_receipt["receipt_sha256"],
            "physical_executor_classification": result.traversal_receipt[
                "physical_executor_classification"
            ],
            "role_counters": list(result.role_counters),
        }

    return owner, invoke, finish, observe, {
        "source_sha256": verified.source_sha256,
        "callback_ir_sha256": verified.callback.ir_sha256,
        "program_identity_sha256": program.identity.identity_sha256,
        "executable_identity_sha256": materialized.identity.identity_sha256,
        "composed_ptx_sha256": materialized.identity.composed_ptx_sha256,
        "wrapper_source_sha256": materialized.identity.wrapper_source_sha256,
        "native_library_sha256": materialized.identity.native_library_sha256,
        "protocol_contract_verdict": materialized.protocol_contract_decision.verdict,
        "path_class": "public_source_verify_compile_materialize_prepare_execute",
        "prepared_query_batch_used": True,
        "prepared_query_batch_device_resident": prepared_batch.device_resident,
        "timed_endpoint": (
            "public_execute_complete_u32x3_d2h_sync_and_external_oracle"),
        "declared_optix_sdk": args.optix_sdk,
    }


def _prepare_pyoptix(args: argparse.Namespace, data: dict[str, object]):
    from experiments.goal5814_particle.public_pyoptix_owner import (
        prevalidate_formal_particle_execution_input,
        prepare_formal_particle_owner,
    )

    arrays = validate_particle_app_input(data)
    expected = face_first_expected(arrays["expected"])
    ptx = args.pyoptix_ptx.resolve(strict=True).read_bytes()
    owner = prepare_formal_particle_owner(
        prebuilt_ptx=ptx,
        vertices=arrays["vertices"],
        triangles=arrays["triangles"],
        front_values=arrays["front_values"],
        back_values=arrays["back_values"],
    )
    columns = tuple(
        np.ascontiguousarray(arrays["queries"][:, index]) for index in range(7)
    )
    for column in columns:
        column.setflags(write=False)
    prevalidated = prevalidate_formal_particle_execution_input(
        *columns, expected)
    resident = owner.prepare_exact_core_prevalidated(prevalidated)
    prepared_counts = owner.prepared_input_operation_counts
    if prepared_counts is None:
        raise RuntimeError("PyOptiX resident query preparation lacked counters")

    def invoke() -> object:
        return owner.execute_prepared_exact_core(resident)

    def finish(completion: object) -> tuple[np.ndarray, object]:
        result = owner.materialize_exact_core_completion(completion)
        output = np.asarray(result.output, dtype=np.uint32)
        if not np.array_equal(output, expected):
            raise RuntimeError("PyOptiX Particle face-first output mismatch")
        return output, result

    def observe(result: object) -> dict[str, object]:
        return {
            "control": list(result.control),
            "operation_counts": {
                name: int(getattr(result.operation_counts, name))
                for name in result.operation_counts.__dataclass_fields__
            },
        }

    return owner, invoke, finish, observe, {
        "pyoptix_ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "pyoptix_device_source_sha256": _sha(
            Path(__file__).resolve().parents[1]
            / "experiments/v4_authored_particle/pyoptix_device.cu"
        ),
        "path_class": "public_pyoptix_handwritten_cuda_precompiled_ptx",
        "prevalidated_execution_input_used": True,
        "prepared_query_batch_used": True,
        "prepared_query_batch_device_resident": True,
        "prepared_query_batch_operation_counts": {
            name: int(getattr(prepared_counts, name))
            for name in prepared_counts.__dataclass_fields__
        },
        "timed_endpoint": (
            "exact_core_complete_u32x3_d2h_sync_and_internal_oracle"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--compute-capability", default="8.9")
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--pyoptix-ptx", type=Path)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--samples", type=int, default=12)
    args = parser.parse_args()
    try:
        validate_repetition_counts(warmups=args.warmups, samples=args.samples)
    except ValueError as error:
        parser.error(str(error))
    if args.arm == "rtdl" and any(
        value is None for value in (args.native, args.optix_include, args.cuda_include)
    ):
        parser.error("RTDL arm requires --native, --optix-include, and --cuda-include")
    if args.arm == "pyoptix" and args.pyoptix_ptx is None:
        parser.error("PyOptiX arm requires --pyoptix-ptx")

    data = load_particle(args.data_root)
    prepare_started = time.perf_counter_ns()
    if args.arm == "rtdl":
        owner, invoke, finish, observe, metadata = _prepare_rtdl(args, data)
    else:
        owner, invoke, finish, observe, metadata = _prepare_pyoptix(args, data)
    prepare_ns = time.perf_counter_ns() - prepare_started
    close_ns = None
    try:
        for _ in range(args.warmups):
            finish(invoke())
        samples = []
        last_output = None
        last_execution = None
        for _ in range(args.samples):
            started = time.perf_counter_ns()
            pending = invoke()
            elapsed_ns = time.perf_counter_ns() - started
            last_output, last_execution = finish(pending)
            samples.append(elapsed_ns)
        if last_output is not None:
            last_output = np.array(
                last_output, dtype=np.uint32, order="C", copy=True)
            last_output.setflags(write=False)
    finally:
        close_started = time.perf_counter_ns()
        owner.close()
        close_ns = time.perf_counter_ns() - close_started
    lifecycle_ns = time.perf_counter_ns() - prepare_started
    if last_output is None or last_execution is None:
        raise AssertionError("worker retained no output")
    last_evidence = observe(last_execution)
    result = {
        "schema": "rtdl.v4.authored_particle_worker.v2",
        "status": "PASS",
        "arm": args.arm,
        "source": _git_identity(),
        "machine": _machine(),
        "input_sha256": data["input_sha256"],
        "independent_oracle_sha256": data["independent_oracle_sha256"],
        "query_count": int(last_output.shape[0]),
        "output_shape": list(last_output.shape),
        "output_sha256": _output_digest(last_output),
        "output_u32_le_base64": base64.b64encode(
            memoryview(last_output).cast("B")).decode("ascii"),
        "prepare_ns": prepare_ns,
        "close_ns": close_ns,
        "lifecycle_ns": lifecycle_ns,
        "warmup_count": args.warmups,
        "sample_count": args.samples,
        "samples_ns": samples,
        "median_ns": int(statistics.median(samples)),
        "minimum_ns": min(samples),
        "maximum_ns": max(samples),
        "metadata": metadata,
        "last_execution_evidence": last_evidence,
        "retained_output_owned": bool(last_output.flags.owndata),
        "retained_output_read_only": not bool(last_output.flags.writeable),
    }
    print(json.dumps(result, allow_nan=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
