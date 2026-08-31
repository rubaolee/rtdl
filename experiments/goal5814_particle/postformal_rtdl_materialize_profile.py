"""Untimed-for-claims engineering profile of Goal5814 D materialization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time

from .formal_worker import (
    ARM_D,
    _bundle_paths,
    _factory,
    preload_symmetric_public_runtimes,
)
from .measurement_protocol import canonical_document, file_record, validate_target_manifest
from .untimed_dual_arm_kat import load_durable_particle_kat


WARMUPS = 64
SAMPLES = 10_000


def _measure(function, count: int = SAMPLES) -> dict[str, float | int]:
    values: list[int] = []
    for _ in range(count):
        start = time.perf_counter_ns()
        function()
        end = time.perf_counter_ns()
        values.append(end - start)
    ordered = sorted(values)
    return {
        "sample_count": count,
        "median_ns": statistics.median(values),
        "p10_ns": ordered[count // 10],
        "p90_ns": ordered[(count * 9) // 10],
        "minimum_ns": ordered[0],
        "maximum_ns": ordered[-1],
    }


def profile(root: Path, target: Path) -> dict[str, object]:
    target_value = validate_target_manifest(
        target, root=root, rehash=True, rehash_wheels=True)
    runtimes = preload_symmetric_public_runtimes()
    public = runtimes.public_rtdlexe
    bundle = load_durable_particle_kat(_bundle_paths(target_value))
    columns = bundle.success_queries.native_order()
    admitted = public.prevalidate_particle_rtdlexe_exact_core_input(
        *columns, expected_u32x3=bundle.expected_output)
    arm = _factory(ARM_D, runtimes)(bundle)
    try:
        for _ in range(WARMUPS):
            completion = arm.execute_exact_core(admitted)
            arm.materialize_exact_core(completion)
        completion = arm.execute_exact_core(admitted)
        prepared = arm._prepared
        control = completion._control
        receipt = completion._receipt
        pointer = completion._output_pointer
        rows = completion._output_rows
        receipt_map = public._validate_receipt(
            control, receipt, output_pointer=pointer, output_rows=rows)
        control_tuple = (
            int(control.validated_row_count), int(control.first_error),
            int(control.error_code), int(control.status))

        def bytes_snapshots():
            return bytes(control), bytes(receipt)

        def receipt_dict_only():
            return {
                name: int(getattr(receipt, name))
                for name, _ctype in public._ParticleFastReceipt._fields_
            }

        def validate_receipt_only():
            return public._validate_receipt(
                control, receipt, output_pointer=pointer, output_rows=rows)

        def result_construction_only():
            return public.ParticleExecutionResult(
                output_u32x3=completion._output_u32x3,
                control=control_tuple,
                receipt=receipt_map,
                artifact_sha256=prepared._loaded.artifact_sha256,
                ptx_sha256=prepared._loaded.ptx_sha256)

        measurements = {
            "bytes_control_and_receipt": _measure(bytes_snapshots),
            "receipt_dict_comprehension": _measure(receipt_dict_only),
            "validate_receipt": _measure(validate_receipt_only),
            "result_construction": _measure(result_construction_only),
            "locked_materialize_direct": _measure(
                lambda: prepared._materialize_exact_core_locked(completion)),
            "public_materialize_with_lock": _measure(
                lambda: prepared.materialize_exact_core_completion(completion)),
            "formal_adapter_materialize": _measure(
                lambda: arm.materialize_exact_core(completion)),
        }
    finally:
        arm.close()
    return {
        "schema": "rtdl.goal5814.postformal_rtdl_materialize_profile.v1",
        "status": "ENGINEERING_PROFILE_ONLY__NOT_REGISTERED_PERFORMANCE_EVIDENCE",
        "target_manifest": file_record(target),
        "source": file_record(Path(__file__).resolve(strict=True)),
        "warmup_gpu_execute_count": WARMUPS,
        "profile_gpu_execute_count": 1,
        "registered_performance_timing_count": 0,
        "measurements": measurements,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    value = profile(
        args.root.resolve(strict=True), args.target.resolve(strict=True))
    print(canonical_document(value).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
