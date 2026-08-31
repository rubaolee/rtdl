"""One fresh-process, one-regime, one-arm Goal5814 formal worker.

Import/runtime admission, target validation, durable input loading, and the
seven-column common-input construction occur before any primary clock.  The
formal CLI has fixed public B/D factories and exposes no factory override.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib
import json
import os
from pathlib import Path
import statistics
import time
from typing import Any, Callable, Mapping

import numpy as np

from .measurement_protocol import (
    ARMS,
    ARM_B,
    ARM_D,
    EXECUTABLE_MANIFEST_BYTES,
    EXECUTABLE_MANIFEST_SHA256,
    REGIMES,
    PROJECT_CLOSURE_ENV,
    SCHEDULE_SHA256,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    WorkerSpec,
    canonical_document,
    file_record,
    require_worker_spec,
    validate_execution_authority,
    validate_authority_window,
    validate_live_target,
    validate_preaction,
    validate_target_manifest,
)
from .untimed_dual_arm_kat import (
    DeploymentCapability,
    ExpectedAssetAuthority,
    KatArmSuccess,
    KatAssetPaths,
    KatContractError,
    KatExecutionLedger,
    LoadedParticleKat,
    UINT32_MAX,
    _require_borrowed_output,
    _validate_ledger,
    load_durable_particle_kat,
)
from .public_pyoptix_owner import (
    PrevalidatedParticleExecutionInput,
    PublicPyOptixRuntime,
    prevalidate_formal_particle_execution_input,
    prepare_formal_particle_owner,
)


WORKER_RESULT_SCHEMA = "rtdl.goal5814.particle_formal_worker_result.v2"
Clock = Callable[[], int]
ArmFactory = Callable[[LoadedParticleKat], Any]


class FormalWorkerError(RuntimeError):
    """A measured owner or worker receipt violated the exact contract."""


@dataclass(frozen=True)
class SymmetricPublicRuntimes:
    module_names: tuple[str, ...]
    pyoptix: PublicPyOptixRuntime
    public_rtdlexe: Any


def preload_symmetric_public_runtimes() -> SymmetricPublicRuntimes:
    """Admit the same Python/runtime graph before every arm's clocks."""

    names = (
        "cupy",
        "optix",
        "rtdsl",
        "rtdsl.v4_particle_rtdlexe",
    )
    modules = {name: importlib.import_module(name) for name in names}
    return SymmetricPublicRuntimes(
        module_names=names,
        pyoptix=PublicPyOptixRuntime(
            cp=modules["cupy"], optix=modules["optix"]),
        public_rtdlexe=modules["rtdsl.v4_particle_rtdlexe"],
    )


def _b_execution_ledger(counts: Any) -> KatExecutionLedger:
    """Map public-B counters only after the measured end clock."""

    return KatExecutionLedger(
        h2d_copy_call_count=int(counts.h2d_copy_call_count),
        h2d_bytes=int(counts.h2d_copy_bytes),
        query_h2d_copy_call_count=int(counts.query_h2d_copy_call_count),
        query_h2d_bytes=int(counts.query_h2d_bytes),
        control_reset_h2d_copy_call_count=int(
            counts.control_reset_h2d_copy_call_count),
        control_reset_h2d_bytes=int(counts.control_reset_h2d_bytes),
        parameter_h2d_copy_call_count=int(
            counts.parameter_h2d_copy_call_count),
        parameter_h2d_bytes=int(counts.parameter_h2d_bytes),
        optix_launch_call_count=int(counts.optix_launch_call_count),
        raygen_invocation_count=int(counts.raygen_invocation_count),
        control_d2h_copy_call_count=int(counts.control_d2h_copy_call_count),
        control_d2h_bytes=int(counts.control_d2h_bytes),
        output_d2h_copy_call_count=int(counts.output_d2h_copy_call_count),
        output_d2h_bytes=int(counts.output_d2h_bytes),
        status_before_output=bool(counts.status_before_output),
        output_d2h_after_status_failure=int(
            counts.output_d2h_after_status_failure),
        blocking_boundary_count=int(counts.explicit_stream_sync_call_count),
    )


def _d_execution_ledger(receipt: Mapping[str, int]) -> KatExecutionLedger:
    """Map the public native-validated D receipt after the end clock."""

    required = {
        "boundary_owner_table_bytes", "control_d2h_bytes",
        "control_d2h_copy_call_count", "control_reset_h2d_bytes",
        "control_reset_h2d_copy_call_count", "host_blocking_boundary_count",
        "optix_launch_count", "output_d2h_after_status_failure",
        "output_d2h_bytes", "output_d2h_copy_call_count",
        "parameter_h2d_bytes", "parameter_h2d_copy_call_count", "query_count",
        "query_h2d_bytes", "query_h2d_copy_call_count", "schema_version",
        "status_before_output",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != required \
            or any(type(receipt[name]) is not int for name in receipt) \
            or receipt["schema_version"] != 1 \
            or receipt["boundary_owner_table_bytes"] != 0:
        raise FormalWorkerError("Goal5814 public D native receipt differs")
    query_calls = receipt["query_h2d_copy_call_count"]
    reset_calls = receipt["control_reset_h2d_copy_call_count"]
    parameter_calls = receipt["parameter_h2d_copy_call_count"]
    query_bytes = receipt["query_h2d_bytes"]
    reset_bytes = receipt["control_reset_h2d_bytes"]
    parameter_bytes = receipt["parameter_h2d_bytes"]
    return KatExecutionLedger(
        h2d_copy_call_count=query_calls + reset_calls + parameter_calls,
        h2d_bytes=query_bytes + reset_bytes + parameter_bytes,
        query_h2d_copy_call_count=query_calls,
        query_h2d_bytes=query_bytes,
        control_reset_h2d_copy_call_count=reset_calls,
        control_reset_h2d_bytes=reset_bytes,
        parameter_h2d_copy_call_count=parameter_calls,
        parameter_h2d_bytes=parameter_bytes,
        optix_launch_call_count=receipt["optix_launch_count"],
        raygen_invocation_count=receipt["query_count"],
        control_d2h_copy_call_count=receipt["control_d2h_copy_call_count"],
        control_d2h_bytes=receipt["control_d2h_bytes"],
        output_d2h_copy_call_count=receipt["output_d2h_copy_call_count"],
        output_d2h_bytes=receipt["output_d2h_bytes"],
        status_before_output=bool(receipt["status_before_output"]),
        output_d2h_after_status_failure=receipt[
            "output_d2h_after_status_failure"],
        blocking_boundary_count=receipt["host_blocking_boundary_count"],
    )


class _FormalPublicPyOptixArm:
    label = ARM_B

    def __init__(
            self, owner: Any,
            deployment_capability: DeploymentCapability) -> None:
        self._owner = owner
        self.deployment_capability = deployment_capability

    def execute_exact_core(
            self, admitted: PrevalidatedParticleExecutionInput) -> Any:
        return self._owner.execute_exact_core_prevalidated(admitted)

    def materialize_exact_core(self, completion: Any) -> KatArmSuccess:
        result = self._owner.materialize_exact_core_completion(completion)
        return KatArmSuccess(
            arm=self.label, output=result.output,
            control=tuple(result.control),
            ledger=_b_execution_ledger(result.operation_counts),
        )

    def close(self) -> None:
        self._owner.close()


class _FormalPublicRTDLExecutableArm:
    label = ARM_D

    def __init__(
            self, *, loaded: Any, prepared: Any,
            deployment_capability: DeploymentCapability) -> None:
        self._loaded = loaded
        self._prepared = prepared
        self.deployment_capability = deployment_capability
        self._closed = False

    def execute_exact_core(
            self, admitted: Any) -> Any:
        return self._prepared.execute_exact_core_prevalidated(admitted)

    def materialize_exact_core(self, completion: Any) -> KatArmSuccess:
        result = self._prepared.materialize_exact_core_completion(completion)
        if result.artifact_sha256 != \
                self.deployment_capability.artifact.sha256 \
                or result.ptx_sha256 != self.deployment_capability.ptx.sha256:
            raise FormalWorkerError(
                "Goal5814 public D executable result identity differs")
        return KatArmSuccess(
            arm=self.label, output=result.output_u32x3,
            control=tuple(result.control),
            ledger=_d_execution_ledger(result.receipt),
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._prepared.close()
        finally:
            self._loaded.close()


def _validate_arm(
        arm: Any, *, expected_label: str, bundle: LoadedParticleKat) -> None:
    if getattr(arm, "label", None) != expected_label:
        raise FormalWorkerError("Goal5814 formal factory returned wrong arm")
    if getattr(arm, "deployment_capability", None) \
            != bundle.deployment_capability:
        raise FormalWorkerError(
            "Goal5814 formal arm deployment capability differs")


def _validate_success(
        result: Any, *, arm: Any, bundle: LoadedParticleKat,
        phase: str, repetition: int) -> dict[str, Any]:
    if not isinstance(result, KatArmSuccess) or result.arm != arm.label:
        raise FormalWorkerError(
            "Goal5814 measured execute success type/arm differs")
    output = _require_borrowed_output(
        f"{arm.label} measured output",
        result.output,
        query_count=bundle.shape.query_count,
    )
    if output.flags.writeable:
        raise FormalWorkerError(
            "Goal5814 measured output is not borrowed read-only")
    expected_control = (bundle.shape.query_count, UINT32_MAX, 0, 0)
    if result.control != expected_control:
        raise FormalWorkerError(
            "Goal5814 measured success control differs")
    _validate_ledger(result.ledger, shape=bundle.shape, success=True)
    # The public complete-execute methods already perform the frozen exact
    # array_equal before returning.  This independent worker-side check occurs
    # only after the end clock and guards the receipt boundary.
    if not np.array_equal(output, bundle.expected_output):
        raise FormalWorkerError("Goal5814 measured output differs from oracle")
    return {
        "phase": phase,
        "repetition": repetition,
        "control": list(result.control),
        "ledger": asdict(result.ledger),
        "exact_worker_check_after_end_clock": True,
        "output_borrowed_read_only": True,
        "output_shape": list(output.shape),
        "output_strides": list(output.strides),
    }


def _elapsed(start: int, end: int, label: str) -> int:
    if type(start) is not int or type(end) is not int or end <= start:
        raise FormalWorkerError(f"Goal5814 {label} clock interval differs")
    return end - start


def run_regime(
        *, bundle: LoadedParticleKat, arm_label: str, regime: str,
        factory: ArmFactory,
        admitted_input: Any,
        clock: Clock = time.perf_counter_ns,
        ) -> dict[str, Any]:
    """Run one frozen regime; callers must finish common input first."""

    if arm_label not in ARMS or regime not in REGIMES:
        raise FormalWorkerError("Goal5814 arm/regime differs")
    arm: Any | None = None
    receipts: list[dict[str, Any]] = []
    primary_samples: list[int] = []
    first_execute_outside_primary: int | None = None
    clock_reads = 0
    try:
        if regime == "DEPLOYMENT_COLD":
            start = clock()
            clock_reads += 1
            arm = factory(bundle)
            completion = arm.execute_exact_core(admitted_input)
            end = clock()
            clock_reads += 1
            primary_samples.append(_elapsed(start, end, "cold"))
            result = arm.materialize_exact_core(completion)
            _validate_arm(arm, expected_label=arm_label, bundle=bundle)
            receipts.append(_validate_success(
                result, arm=arm, bundle=bundle,
                phase="COLD_FIRST_COMPLETE_EXECUTE", repetition=0))

        elif regime == "PREPARE":
            start = clock()
            clock_reads += 1
            arm = factory(bundle)
            end = clock()
            clock_reads += 1
            primary_samples.append(_elapsed(start, end, "prepare"))
            _validate_arm(arm, expected_label=arm_label, bundle=bundle)

            first_start = clock()
            clock_reads += 1
            completion = arm.execute_exact_core(admitted_input)
            first_end = clock()
            clock_reads += 1
            first_execute_outside_primary = _elapsed(
                first_start, first_end, "first execute after prepare")
            result = arm.materialize_exact_core(completion)
            receipts.append(_validate_success(
                result, arm=arm, bundle=bundle,
                phase="FIRST_COMPLETE_EXECUTE_OUTSIDE_PREPARE_PRIMARY",
                repetition=0))

        else:
            arm = factory(bundle)
            _validate_arm(arm, expected_label=arm_label, bundle=bundle)
            for repetition in range(STEADY_WARMUPS):
                completion = arm.execute_exact_core(admitted_input)
                result = arm.materialize_exact_core(completion)
                receipts.append(_validate_success(
                    result, arm=arm, bundle=bundle,
                    phase="STEADY_WARMUP", repetition=repetition))
            for repetition in range(STEADY_REPETITIONS):
                start = clock()
                clock_reads += 1
                completion = arm.execute_exact_core(admitted_input)
                end = clock()
                clock_reads += 1
                primary_samples.append(_elapsed(
                    start, end, f"steady repetition {repetition}"))
                result = arm.materialize_exact_core(completion)
                receipts.append(_validate_success(
                    result, arm=arm, bundle=bundle,
                    phase="STEADY_TIMED", repetition=repetition))
    finally:
        if arm is not None:
            arm.close()

    if regime == "STEADY_DYNAMIC_E2E":
        primary_value: int | float = statistics.median(primary_samples)
        registered = STEADY_REPETITIONS
        warmups = STEADY_WARMUPS
    else:
        primary_value = primary_samples[0]
        registered = 2 if regime == "PREPARE" else 1
        warmups = 0
    return {
        "regime": regime,
        "arm": arm_label,
        "primary_value_ns": primary_value,
        "primary_samples_ns": primary_samples,
        "first_execute_outside_primary_ns": first_execute_outside_primary,
        "warmup_execute_count": warmups,
        "complete_execute_count": len(receipts),
        "execution_receipts": receipts,
        "clock": "time.perf_counter_ns",
        "clock_read_count": clock_reads,
        "registered_performance_timing_count": registered,
        "close_after_all_registered_end_clocks": True,
    }


def _bundle_paths(target: Mapping[str, Any]) -> KatAssetPaths:
    files = target["files"]
    return KatAssetPaths(
        scientific_input_directory=Path(target["scientific_input_directory"]),
        prebuilt_ptx=Path(files["prebuilt_ptx"]["path"]),
        native_dso=Path(files["native_dso"]["path"]),
        rtdlexe=Path(files["rtdlexe"]["path"]),
        executable_manifest=Path(files["executable_manifest"]["path"]),
        executable_manifest_identity=ExpectedAssetAuthority(
            bytes=EXECUTABLE_MANIFEST_BYTES,
            sha256=EXECUTABLE_MANIFEST_SHA256,
        ),
    )


def _prepare_public_pyoptix_formal_arm(
        bundle: LoadedParticleKat,
        runtimes: SymmetricPublicRuntimes) -> _FormalPublicPyOptixArm:
    if bundle.shape.query_count != 5_000:
        raise FormalWorkerError("Goal5814 formal B shape differs")
    static = bundle.static_input
    owner = prepare_formal_particle_owner(
        prebuilt_ptx=bundle.prebuilt_ptx,
        vertices=static.vertices,
        triangles=static.triangles,
        front_values=static.front_values,
        back_values=static.back_values,
        runtime=runtimes.pyoptix,
    )
    return _FormalPublicPyOptixArm(owner, bundle.deployment_capability)


def _prepare_public_verified_rtdlexe_formal_arm(
        bundle: LoadedParticleKat,
        runtimes: SymmetricPublicRuntimes,
        ) -> _FormalPublicRTDLExecutableArm:
    if bundle.shape.query_count != 5_000:
        raise FormalWorkerError("Goal5814 formal D shape differs")
    public = runtimes.public_rtdlexe
    capability = bundle.deployment_capability
    deployment = public.install_particle_rtdlexe_deployment(
        deployment_id=(
            "goal5814/formal-measurement/"
            f"{capability.manifest.sha256}"),
        expected_artifact_sha256=capability.artifact.sha256,
        expected_native_sha256=capability.native.sha256,
        expected_protocol_decision_sha256=capability.protocol_decision.sha256,
        expected_template_semantic_sha256=capability.template_semantic.sha256,
    )
    loaded = public.load_particle_rtdlexe(
        bundle.paths.rtdlexe,
        deployment=deployment,
        native_library_path=bundle.paths.native_dso,
    )
    prepared = None
    try:
        if loaded.artifact_sha256 != capability.artifact.sha256 \
                or loaded.ptx_sha256 != capability.ptx.sha256 \
                or loaded.ptx_bytes != bundle.prebuilt_ptx:
            raise FormalWorkerError("Goal5814 public D loaded identity differs")
        static = bundle.static_input
        prepared = loaded.prepare(public.ParticleStaticInput(
            vertices_f32=static.vertices,
            triangles_u32=static.triangles,
            front_values_u32=static.front_values,
            back_values_u32=static.back_values,
        ))
        return _FormalPublicRTDLExecutableArm(
            loaded=loaded, prepared=prepared,
            deployment_capability=capability)
    except BaseException:
        if prepared is not None:
            prepared.close()
        loaded.close()
        raise


def _factory(arm: str, runtimes: SymmetricPublicRuntimes) -> ArmFactory:
    # This fixed mapping is deliberately not caller-selectable.
    if arm == ARM_B:
        return lambda bundle: _prepare_public_pyoptix_formal_arm(
            bundle, runtimes)
    if arm == ARM_D:
        return lambda bundle: _prepare_public_verified_rtdlexe_formal_arm(
            bundle, runtimes)
    raise FormalWorkerError("Goal5814 formal arm differs")


def validate_worker_result(
        value: Mapping[str, Any], *, expected: WorkerSpec) -> None:
    required = {
        "schema", "status", "worker_id", "ordinal", "regime", "block",
        "position", "arm", "pid", "parent_pid", "preaction_file",
        "target_manifest_file", "execution_request_file",
        "project_closure_file", "target_observation",
        "deployment_capability", "schedule_sha256", "measurement",
        "timed", "retry_count", "resume_count", "replacement_count",
        "row_drop_count", "formal_worker_count",
        "registered_performance_timing_count",
    }
    if set(value) != required \
            or value.get("schema") != WORKER_RESULT_SCHEMA \
            or value.get("status") != "PASS__ONE_FRESH_PROCESS_FORMAL_ROW" \
            or value.get("worker_id") != expected.worker_id \
            or value.get("ordinal") != expected.ordinal \
            or value.get("regime") != expected.regime \
            or value.get("block") != expected.block \
            or value.get("position") != expected.position \
            or value.get("arm") != expected.arm \
            or type(value.get("pid")) is not int or value["pid"] <= 0 \
            or type(value.get("parent_pid")) is not int \
            or value["parent_pid"] <= 0 \
            or value.get("schedule_sha256") != SCHEDULE_SHA256 \
            or value.get("timed") is not True \
            or any(value.get(key) != 0 for key in (
                "retry_count", "resume_count", "replacement_count",
                "row_drop_count")) \
            or value.get("formal_worker_count") != 1:
        raise FormalWorkerError("Goal5814 formal worker envelope differs")
    measurement = value.get("measurement")
    if not isinstance(measurement, Mapping) \
            or measurement.get("regime") != expected.regime \
            or measurement.get("arm") != expected.arm \
            or value.get("registered_performance_timing_count") \
            != measurement.get("registered_performance_timing_count"):
        raise FormalWorkerError("Goal5814 formal worker measurement differs")


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--preaction", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--execution-request", type=Path, required=True)
    parser.add_argument("--ordinal", type=int, required=True)
    parser.add_argument("--regime", choices=REGIMES, required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--position", type=int, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--worker-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.root.resolve(strict=True)
    preaction_path = args.preaction.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    request_path = args.execution_request.resolve(strict=True)
    closure_raw = os.environ.get(PROJECT_CLOSURE_ENV)
    if not closure_raw:
        raise FormalWorkerError(
            "Goal5814 worker lacks controller-bound project closure")
    closure_path = Path(closure_raw)
    if not closure_path.is_absolute():
        raise FormalWorkerError(
            "Goal5814 worker project closure path is not absolute")
    closure_path = closure_path.resolve(strict=True)
    expected = require_worker_spec(
        ordinal=args.ordinal, regime=args.regime, block=args.block,
        position=args.position, arm=args.arm, worker_id=args.worker_id)
    validate_preaction(preaction_path)
    # The controller rehashes the three preserved wheels once before worker
    # zero.  Each fresh worker rehashes all active modules, including the real
    # PyOptiX C extension, without rereading ~152 MB of wheel custody.
    target = validate_target_manifest(
        target_path, root=root, rehash=True, rehash_wheels=False)
    closure = validate_execution_authority(
        request_path, preaction_path=preaction_path,
        target_manifest_path=target_path, target_manifest=target)
    validate_authority_window(closure)
    live_target = validate_live_target(target)

    # Both public runtime module graphs and every durable/common input are
    # admitted before run_regime can read its first clock.
    runtimes = preload_symmetric_public_runtimes()
    bundle = load_durable_particle_kat(_bundle_paths(target))
    common_columns = bundle.success_queries.native_order()
    # Both arm-specific immutable-byte capabilities are admitted from the
    # same common arrays before run_regime can read its first clock.  The D
    # capability is what authorizes only the native v3 no-rescan execute ABI;
    # ordinary public execute methods retain defensive native value scans.
    admitted_b = prevalidate_formal_particle_execution_input(
        *common_columns, bundle.expected_output)
    admitted_d = runtimes.public_rtdlexe.\
        prevalidate_particle_rtdlexe_exact_core_input(
            *common_columns, expected_u32x3=bundle.expected_output)
    admitted_input = admitted_b if expected.arm == ARM_B else admitted_d
    measurement = run_regime(
        bundle=bundle, arm_label=expected.arm, regime=expected.regime,
        factory=_factory(expected.arm, runtimes),
        admitted_input=admitted_input)

    result = {
        "schema": WORKER_RESULT_SCHEMA,
        "status": "PASS__ONE_FRESH_PROCESS_FORMAL_ROW",
        "worker_id": expected.worker_id,
        "ordinal": expected.ordinal,
        "regime": expected.regime,
        "block": expected.block,
        "position": expected.position,
        "arm": expected.arm,
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "preaction_file": file_record(preaction_path),
        "target_manifest_file": file_record(target_path),
        "execution_request_file": file_record(request_path),
        "project_closure_file": file_record(closure_path),
        "target_observation": live_target,
        "deployment_capability": asdict(bundle.deployment_capability),
        "schedule_sha256": SCHEDULE_SHA256,
        "measurement": measurement,
        "timed": True,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "formal_worker_count": 1,
        "registered_performance_timing_count": measurement[
            "registered_performance_timing_count"],
    }
    validate_worker_result(result, expected=expected)
    print(canonical_document(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
