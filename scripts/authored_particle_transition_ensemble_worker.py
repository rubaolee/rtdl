#!/usr/bin/env python3
"""Variable-scale Particle transition worker for RTDL and public PyOptiX."""

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
from experiments.v4_paper_apps_pyoptix.inputs import load_particle, sha256


ROOT = Path(__file__).resolve().parents[1]


def _output_digest(value: np.ndarray) -> str:
    value = np.ascontiguousarray(value, dtype=np.uint32)
    digest = hashlib.sha256()
    digest.update(value.dtype.str.encode("ascii"))
    digest.update(str(tuple(value.shape)).encode("ascii"))
    digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def _git_identity() -> dict[str, str]:
    def capture(*arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    if capture("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Particle ensemble worker requires clean tracked source")
    return {
        "commit": capture("rev-parse", "HEAD"),
        "tree": capture("rev-parse", "HEAD^{tree}"),
    }


def _machine() -> dict[str, object]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,uuid,driver_version,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        check=True, capture_output=True, text=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("Particle ensemble worker requires one visible GPU")
    name, uuid, driver, capability = (
        field.strip() for field in rows[0].split(","))
    return {
        "hostname": platform.node(),
        "python": platform.python_version(),
        "gpu_name": name,
        "gpu_uuid": uuid,
        "driver": driver,
        "compute_capability": capability,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def _load_ensemble(
    root: Path, query_count: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, object], str]:
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble.v1" \
            or manifest["queries"]["count"] < query_count \
            or manifest["queries"]["distinct_origin_count"] \
                != manifest["queries"]["count"] \
            or manifest["claim_boundary"][
                "distinct_strict_interior_queries"] is not True:
        raise ValueError("Particle transition ensemble manifest differs")
    arrays = {}
    for name in ("queries_f32.npy", "expected_u32.npy"):
        path = root / name
        row = manifest["members"][name]
        if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
            raise RuntimeError(f"Particle transition ensemble member differs: {name}")
        value = np.load(path, mmap_mode="r", allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"Particle transition ensemble shape differs: {name}")
        arrays[name] = value
    queries = np.ascontiguousarray(
        arrays["queries_f32.npy"][:query_count], dtype=np.float32)
    expected = face_first_expected(
        arrays["expected_u32.npy"][:query_count])
    identity = hashlib.sha256(json.dumps({
        "base_manifest_sha256": manifest["base_particle"]["manifest_sha256"],
        "ensemble_manifest_sha256": sha256(manifest_path),
        "query_count": query_count,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return queries, expected, manifest, identity


def _prepare_rtdl(args, base, queries, expected, oracle_sha256):
    from rtdsl import v4

    verified = v4.verify_builtin_triangle_callback_source(
        FACE_FIRST_SOURCE, face_first_manifest())
    physical_plan = build_face_first_physical_plan(
        verified, independent_cpu_oracle_sha256=oracle_sha256)
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    native = args.native.resolve(strict=True)
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
    static = v4.BuiltinTriangleCallbackStaticInput(
        vertices=base["vertices"],
        triangles=base["triangles"],
        first_primitive_values=base["front_values"],
        second_primitive_values=base["back_values"],
    )
    owner = materialized.prepare(static)
    expected_output_sha256 = _output_digest(expected)
    try:
        prepared = owner.prepare_batch(
            v4.BuiltinTriangleCallbackBatch(queries=queries))
    except BaseException:
        # A failed batch admission still owns native program state.  Close it
        # deterministically instead of leaving registry teardown to process
        # finalization, where the CUDA context may already be disappearing.
        owner.close()
        raise

    def invoke():
        result = owner.execute(prepared)
        output = np.asarray(result.output, dtype=np.uint32)
        if output.shape != expected.shape \
                or result.output_sha256 != expected_output_sha256:
            raise RuntimeError("RTDL Particle ensemble output mismatch")
        return output, result

    def finish(pending):
        return pending

    return owner, invoke, finish, {
        "path_class": "public_rtdl_provider_native_closest_prepared",
        "native_library_sha256": materialized.identity.native_library_sha256,
        "prepared_query_batch_device_resident": prepared.device_resident,
        "program_identity_sha256": program.identity.identity_sha256,
        "executable_identity_sha256": materialized.identity.identity_sha256,
        "oracle_validation": "canonical_u32x3_sha256",
    }


def _prepare_pyoptix(args, base, queries, expected):
    from experiments.goal5814_particle.public_pyoptix_owner import (
        ParticleProblemShape,
        PublicPyOptixParticleOwner,
        prevalidate_particle_execution_input,
    )

    shape = ParticleProblemShape(
        vertex_count=len(base["vertices"]),
        triangle_count=len(base["triangles"]),
        query_count=len(queries),
    )
    owner = PublicPyOptixParticleOwner.prepare(
        prebuilt_ptx=args.pyoptix_ptx.resolve(strict=True).read_bytes(),
        vertices=base["vertices"],
        triangles=base["triangles"],
        front_values=base["front_values"],
        back_values=base["back_values"],
        shape=shape,
    )
    columns = tuple(
        np.ascontiguousarray(queries[:, index], dtype=np.float32)
        for index in range(7)
    )
    for value in (*columns, expected):
        value.setflags(write=False)
    admitted = prevalidate_particle_execution_input(
        *columns, expected, shape=shape)
    resident = owner.prepare_exact_core_prevalidated(admitted)
    prepared_counts = owner.prepared_input_operation_counts
    if prepared_counts is None:
        raise RuntimeError("PyOptiX Particle ensemble preparation lacked counters")

    def invoke():
        return owner.execute_prepared_exact_core(resident)

    def finish(completion):
        result = owner.materialize_exact_core_completion(completion)
        output = np.asarray(result.output, dtype=np.uint32)
        if not np.array_equal(output, expected):
            raise RuntimeError("PyOptiX Particle ensemble output mismatch")
        return output, result

    return owner, invoke, finish, {
        "path_class": "public_pyoptix_native_closest_prepared",
        "pyoptix_ptx_sha256": sha256(args.pyoptix_ptx),
        "prepared_query_batch_device_resident": True,
        "prepared_query_batch_operation_counts": {
            name: int(getattr(prepared_counts, name))
            for name in prepared_counts.__dataclass_fields__
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument("--base-particle-dir", type=Path, required=True)
    parser.add_argument("--ensemble-dir", type=Path, required=True)
    parser.add_argument("--query-count", type=int, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--compute-capability", default="8.9")
    parser.add_argument("--optix-sdk", default="8.0.0")
    parser.add_argument("--pyoptix-ptx", type=Path)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--samples", type=int, default=1)
    args = parser.parse_args()
    if args.query_count < 1 or args.warmups < 0 or args.samples < 1:
        parser.error("query count/samples must be positive and warmups nonnegative")
    if args.arm == "rtdl" and any(
            value is None for value in (
                args.native, args.optix_include, args.cuda_include)):
        parser.error("RTDL arm requires native and toolchain headers")
    if args.arm == "pyoptix" and args.pyoptix_ptx is None:
        parser.error("PyOptiX arm requires prebuilt PTX")

    base_root = args.base_particle_dir.resolve(strict=True)
    base = load_particle(base_root.parent)
    queries, expected, ensemble, input_sha256 = _load_ensemble(
        args.ensemble_dir.resolve(strict=True), args.query_count)
    oracle_sha256 = hashlib.sha256(json.dumps({
        "ensemble_construction": ensemble["queries"]["construction"],
        "ensemble_expected_sha256": ensemble["members"][
            "expected_u32.npy"]["sha256"],
        "query_count": args.query_count,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    prepare_started = time.perf_counter_ns()
    if args.arm == "rtdl":
        owner, invoke, finish, metadata = _prepare_rtdl(
            args, base, queries, expected, oracle_sha256)
    else:
        owner, invoke, finish, metadata = _prepare_pyoptix(
            args, base, queries, expected)
    prepare_ns = time.perf_counter_ns() - prepare_started
    close_ns = None
    samples = []
    last_output = None
    last_result = None
    try:
        for _ in range(args.warmups):
            finish(invoke())
        for _ in range(args.samples):
            started = time.perf_counter_ns()
            pending = invoke()
            samples.append(time.perf_counter_ns() - started)
            last_output, last_result = finish(pending)
    finally:
        close_started = time.perf_counter_ns()
        owner.close()
        close_ns = time.perf_counter_ns() - close_started
    if last_output is None or last_result is None:
        raise AssertionError("Particle ensemble worker retained no result")
    if args.arm == "rtdl":
        execution = {
            "output_sha256": last_result.output_sha256,
            "physical_executor_classification": last_result.traversal_receipt[
                "physical_executor_classification"],
            "role_counters": list(last_result.role_counters),
        }
    else:
        execution = {
            "control": list(last_result.control),
            "operation_counts": {
                name: int(getattr(last_result.operation_counts, name))
                for name in last_result.operation_counts.__dataclass_fields__
            },
        }
    result = {
        "schema": "rtdl.v4.authored_particle.transition_ensemble_worker.v1",
        "status": "PASS",
        "arm": args.arm,
        "source": _git_identity(),
        "machine": _machine(),
        "base_manifest_sha256": base["input_sha256"],
        "ensemble_manifest_sha256": sha256(
            args.ensemble_dir / "MANIFEST.json"),
        "input_sha256": input_sha256,
        "independent_oracle_sha256": oracle_sha256,
        "query_count": args.query_count,
        "output_shape": list(last_output.shape),
        "output_sha256": _output_digest(last_output),
        "prepare_ns": prepare_ns,
        "close_ns": close_ns,
        "warmup_count": args.warmups,
        "sample_count": args.samples,
        "samples_ns": samples,
        "median_ns": statistics.median(samples),
        "metadata": metadata,
        "last_execution_evidence": execution,
        "claim_boundary": {
            "diagnostic_only": True,
            "natural_single_transition_ensemble": True,
            "temporal_particle_simulation": False,
            "formal_worker_zero_reached": False,
        },
    }
    print(json.dumps(result, sort_keys=True, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
