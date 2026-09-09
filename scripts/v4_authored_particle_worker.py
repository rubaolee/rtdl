#!/usr/bin/env python3
"""One-process diagnostic worker for source-authored Particle versus PyOptiX."""

from __future__ import annotations

import argparse
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
        optix_sdk="9.0.0",
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

    def execute() -> tuple[np.ndarray, dict[str, object]]:
        result = owner.execute(prepared_batch)
        output = np.asarray(result.output, dtype=np.uint32)
        if not np.array_equal(output, expected):
            raise RuntimeError("source-authored RTDL Particle output mismatch")
        return output, {
            "output_sha256": result.output_sha256,
            "traversal_receipt_sha256": result.traversal_receipt["receipt_sha256"],
            "physical_executor_classification": result.traversal_receipt[
                "physical_executor_classification"
            ],
            "role_counters": list(result.role_counters),
        }

    return owner, execute, {
        "source_sha256": verified.source_sha256,
        "callback_ir_sha256": verified.callback.ir_sha256,
        "program_identity_sha256": program.identity.identity_sha256,
        "executable_identity_sha256": materialized.identity.identity_sha256,
        "composed_ptx_sha256": materialized.identity.composed_ptx_sha256,
        "wrapper_source_sha256": materialized.identity.wrapper_source_sha256,
        "protocol_contract_verdict": materialized.protocol_contract_decision.verdict,
        "path_class": "public_source_verify_compile_materialize_prepare_execute",
        "prepared_query_batch_used": True,
    }


def _prepare_pyoptix(args: argparse.Namespace, data: dict[str, object]):
    from experiments.goal5814_particle.public_pyoptix_owner import (
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

    def execute() -> tuple[np.ndarray, dict[str, object]]:
        result = owner.execute_complete(*columns, expected)
        output = np.asarray(result.output, dtype=np.uint32)
        if not np.array_equal(output, expected):
            raise RuntimeError("PyOptiX Particle face-first output mismatch")
        return output, {
            "control": list(result.control),
            "operation_counts": {
                name: int(getattr(result.operation_counts, name))
                for name in result.operation_counts.__dataclass_fields__
            },
        }

    return owner, execute, {
        "pyoptix_ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "pyoptix_device_source_sha256": _sha(
            Path(__file__).resolve().parents[1]
            / "experiments/v4_authored_particle/pyoptix_device.cu"
        ),
        "path_class": "public_pyoptix_handwritten_cuda_precompiled_ptx",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--compute-capability", default="8.9")
    parser.add_argument("--pyoptix-ptx", type=Path)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--samples", type=int, default=12)
    args = parser.parse_args()
    if args.warmups < 1 or args.samples < 1:
        parser.error("warmups and samples must be positive")
    if args.arm == "rtdl" and any(
        value is None for value in (args.native, args.optix_include, args.cuda_include)
    ):
        parser.error("RTDL arm requires --native, --optix-include, and --cuda-include")
    if args.arm == "pyoptix" and args.pyoptix_ptx is None:
        parser.error("PyOptiX arm requires --pyoptix-ptx")

    data = load_particle(args.data_root)
    prepare_started = time.perf_counter_ns()
    if args.arm == "rtdl":
        owner, execute, metadata = _prepare_rtdl(args, data)
    else:
        owner, execute, metadata = _prepare_pyoptix(args, data)
    prepare_ns = time.perf_counter_ns() - prepare_started
    try:
        for _ in range(args.warmups):
            execute()
        samples = []
        last_output = None
        last_evidence = None
        for _ in range(args.samples):
            started = time.perf_counter_ns()
            last_output, last_evidence = execute()
            samples.append(time.perf_counter_ns() - started)
    finally:
        owner.close()
    if last_output is None or last_evidence is None:
        raise AssertionError("worker retained no output")
    result = {
        "schema": "rtdl.v4.authored_particle_worker.v1",
        "status": "PASS",
        "arm": args.arm,
        "machine": _machine(),
        "input_sha256": data["input_sha256"],
        "independent_oracle_sha256": data["independent_oracle_sha256"],
        "query_count": int(last_output.shape[0]),
        "output_shape": list(last_output.shape),
        "output_sha256": _output_digest(last_output),
        "prepare_ns": prepare_ns,
        "warmup_count": args.warmups,
        "sample_count": args.samples,
        "samples_ns": samples,
        "median_ns": int(statistics.median(samples)),
        "minimum_ns": min(samples),
        "maximum_ns": max(samples),
        "metadata": metadata,
        "last_execution_evidence": last_evidence,
    }
    print(json.dumps(result, allow_nan=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
