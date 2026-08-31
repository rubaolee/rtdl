from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import shutil
import statistics
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from experiments.goal5814_particle import controller as controller_module
from experiments.goal5814_particle import measurement_preflight as preflight_module
from experiments.goal5814_particle import measurement_protocol as protocol_module
from experiments.goal5814_particle.evaluate import (
    EvaluationError,
    _bootstrap,
    evaluate,
)
from experiments.goal5814_particle.formal_worker import run_regime
from experiments.goal5814_particle.independent_recount import (
    RecountError,
    recount,
    recount_files,
)
from experiments.goal5814_particle.measurement_protocol import (
    ARM_B,
    ARM_D,
    BOOTSTRAP_CI_INDICES,
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_SEED_BASE,
    BLOCK_COUNT,
    BLOCK_ORDER_RULE,
    BOOTSTRAP_RULE,
    CACHE_RULE,
    CLOCK_RULE,
    CUPY_WHEEL_BYTES,
    CUPY_WHEEL_SHA256,
    EXECUTABLE_MANIFEST_BYTES,
    EXECUTABLE_MANIFEST_SHA256,
    EXECUTION_REQUEST_SCHEMA,
    EXECUTION_CONCURRENCY_RULE,
    INVALID_ROW_RULE,
    NUMPY_WHEEL_BYTES,
    NUMPY_WHEEL_SHA256,
    PREACTION_RELATIVE_PATH,
    OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH,
    PROJECT_CLOSURE_ENV,
    PROJECT_CLOSURE_SCHEMA,
    PYOPTIX_EXTENSION_BYTES,
    PYOPTIX_EXTENSION_SHA256,
    PYOPTIX_WHEEL_BYTES,
    PYOPTIX_WHEEL_SHA256,
    REGIMES,
    SCHEDULE_SHA256,
    SOURCE_ROLE_PATHS,
    STEADY_MEDIAN_RULE,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TARGET_FILE_ROLES,
    TARGET_ARTIFACT_SHA256,
    TARGET_KAT_PREACTION_RELATIVE_PATH,
    TARGET_KAT_RESULT_RELATIVE_PATH,
    TARGET_MANIFEST_SCHEMA,
    TARGET_NATIVE_RELATIVE_DIRECTORY,
    TOTAL_WORKER_COUNT,
    WORKER_TIMEOUT_SECONDS,
    MeasurementProtocolError,
    canonical_document,
    digest,
    file_record,
    schedule,
    schedule_document,
    validate_authority_window,
    validate_execution_authority,
    validate_execution_request,
    validate_live_target,
    validate_owner_directive_receipt,
    validate_preaction,
    validate_project_closure,
    validate_target_manifest,
)
from experiments.goal5814_particle.untimed_dual_arm_kat import (
    KatArmSuccess,
    KatExecutionLedger,
)


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / PREACTION_RELATIVE_PATH
OWNER_RECEIPT = ROOT / OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH
SCIENTIFIC = ROOT / (
    "history/internal_docs/"
    "goal5814_particle_tracking_scientific_input_v1_20260828")
TARGET_EXECUTABLE = ROOT / TARGET_NATIVE_RELATIVE_DIRECTORY
TARGET_KAT_PREACTION = ROOT / TARGET_KAT_PREACTION_RELATIVE_PATH
TARGET_KAT_RESULT = ROOT / TARGET_KAT_RESULT_RELATIVE_PATH


SUCCESS_LEDGER = KatExecutionLedger(
    h2d_copy_call_count=9,
    h2d_bytes=140_136,
    query_h2d_copy_call_count=7,
    query_h2d_bytes=140_000,
    control_reset_h2d_copy_call_count=1,
    control_reset_h2d_bytes=16,
    parameter_h2d_copy_call_count=1,
    parameter_h2d_bytes=120,
    optix_launch_call_count=1,
    raygen_invocation_count=5_000,
    control_d2h_copy_call_count=1,
    control_d2h_bytes=16,
    output_d2h_copy_call_count=1,
    output_d2h_bytes=60_000,
    status_before_output=True,
    output_d2h_after_status_failure=0,
    blocking_boundary_count=2,
)


def _fake_record(path: Path, size: int, sha256: str) -> dict[str, object]:
    return {"path": str(path.absolute()), "bytes": size, "sha256": sha256}


def _seal_target(value: dict[str, object]) -> dict[str, object]:
    result = dict(value)
    result["target_manifest_sha256"] = digest(result)
    return result


def _seal_request(value: dict[str, object]) -> dict[str, object]:
    result = dict(value)
    result["execution_request_sha256"] = digest(result)
    return result


def _seal_closure(value: dict[str, object]) -> dict[str, object]:
    result = dict(value)
    result["project_closure_sha256"] = digest(result)
    return result


def _target_fixture(directory: Path) -> tuple[Path, dict[str, object]]:
    executable_manifest = TARGET_EXECUTABLE / "executable_manifest.json"
    ptx = TARGET_EXECUTABLE / (
        "9484a5a4e600885d335cff16130e9cbbc0d1c5d8ed6d24297e2ecb202e0c6e67."
        "compute_86.pass1.ptx")
    artifact = TARGET_EXECUTABLE / (
        f"{TARGET_ARTIFACT_SHA256}."
        "rtdlexe")
    executable = Path(sys.executable).resolve()
    numpy_module = Path(np.__file__).resolve()
    files: dict[str, object] = {
        role: file_record(ROOT / relative)
        for role, relative in SOURCE_ROLE_PATHS.items()
    }
    files.update({
        "preaction": file_record(PREACTION),
        "scientific_manifest": file_record(
            SCIENTIFIC / "SCIENTIFIC_INPUT_MANIFEST.json"),
        "executable_manifest": file_record(executable_manifest),
        "prebuilt_ptx": file_record(ptx),
        "native_dso": file_record(TARGET_EXECUTABLE / "librtdl_optix.so"),
        "rtdlexe": file_record(artifact),
        "nvidia_smi": file_record(executable),
        "python_executable": file_record(executable),
        "numpy_module": file_record(numpy_module),
        "cupy_module": file_record(executable),
        "optix_module": file_record(executable),
        "pyoptix_extension": _fake_record(
            directory / "_optix.cpython-312-x86_64-linux-gnu.so",
            PYOPTIX_EXTENSION_BYTES, PYOPTIX_EXTENSION_SHA256),
        "pyoptix_wheel": _fake_record(
            directory / "pyoptix.whl", PYOPTIX_WHEEL_BYTES,
            PYOPTIX_WHEEL_SHA256),
        "cupy_wheel": _fake_record(
            directory / "cupy.whl", CUPY_WHEEL_BYTES, CUPY_WHEEL_SHA256),
        "numpy_wheel": _fake_record(
            directory / "numpy.whl", NUMPY_WHEEL_BYTES, NUMPY_WHEEL_SHA256),
        "target_kat_preaction": file_record(TARGET_KAT_PREACTION),
        "target_kat_result": file_record(TARGET_KAT_RESULT),
    })
    assert set(files) == TARGET_FILE_ROLES
    target = {
        "schema": TARGET_MANIFEST_SCHEMA,
        "status": "PREPARED_TARGET_PRODUCTS__WORKER_ZERO",
        "target": {
            "hostname": "b7f901018414",
            "gpu_selector": "0",
            "gpu_uuid": "GPU-b7695ce1-4b15-b15c-0d4a-52da0b65213e",
            "gpu_name": "NVIDIA RTX A5000",
            "compute_capability": "8.6",
            "driver_version": "570.211.01",
            "gpu_memory_total_mib": 24_564,
            "cuda_visible_devices": "0",
            "python_version": "3.12.3",
            "numpy_version": "2.4.4",
            "cupy_version": "14.0.1",
            "pyoptix_distribution_version": "9.1.0",
            "optix_api_version": "9.0.0",
            "ld_library_path": None,
            "ld_preload": None,
        },
        "scientific_input_directory": str(SCIENTIFIC.resolve()),
        "files": files,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    target = _seal_target(target)
    path = directory / "target_manifest.json"
    path.write_bytes(canonical_document(target))
    return path, target


def _validate_fixture_target(path: Path) -> dict[str, object]:
    """Exercise target semantics while production KAT v3 remains fail-closed."""

    entry = file_record(ROOT / SOURCE_ROLE_PATHS["target_kat_entry"])
    with patch.multiple(
            protocol_module,
            TARGET_KAT_ENTRY_BYTES=entry["bytes"],
            TARGET_KAT_ENTRY_SHA256=entry["sha256"]):
        return validate_target_manifest(
            path, root=ROOT, rehash=False, rehash_wheels=False)


def _request_fixture(
        directory: Path, target_path: Path,
        target: dict[str, object]) -> tuple[Path, dict[str, object]]:
    files = target["files"]
    value = {
        "schema": EXECUTION_REQUEST_SCHEMA,
        "status": "PROJECT_PREPARED__TARGET_BOUND__NONAUTHORIZING_REQUEST",
        "owner_directive_receipt_file": file_record(OWNER_RECEIPT),
        "preaction_file": file_record(PREACTION),
        "scientific_manifest": files["scientific_manifest"],
        "executable_manifest": files["executable_manifest"],
        "target_manifest_file": file_record(target_path),
        "schedule_sha256": SCHEDULE_SHA256,
        "clock_rule": CLOCK_RULE,
        "steady_median_rule": STEADY_MEDIAN_RULE,
        "bootstrap_rule": BOOTSTRAP_RULE,
        "block_order_rule": BLOCK_ORDER_RULE,
        "execution_concurrency_rule": EXECUTION_CONCURRENCY_RULE,
        "cache_rule": CACHE_RULE,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "authorization_not_before_utc": "2026-08-28T00:00:00Z",
        "authorization_not_after_utc": "2026-08-28T08:00:00Z",
        "invalid_row_rule": INVALID_ROW_RULE,
        "owner_target_bound_exact_bytes_approval_claimed": False,
        "project_materialized_under_owner_scope": True,
        "formal_worker_zero_authorized": False,
        "pod_gpu_timing_authorized": False,
        "descriptive_unconditional_acceptance": True,
        "confirmatory_noninferiority_claim": False,
        "threshold_count": 0,
        "retry_resume_replacement_or_row_drop_allowed": False,
        "total_worker_count": TOTAL_WORKER_COUNT,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    value = _seal_request(value)
    path = directory / "execution_request.json"
    path.write_bytes(canonical_document(value))
    return path, value


def _closure_fixture(
        directory: Path, target_path: Path, target: dict[str, object],
        request_path: Path,
        request: dict[str, object]) -> tuple[Path, dict[str, object]]:
    files = target["files"]
    value = {
        "schema": PROJECT_CLOSURE_SCHEMA,
        "status": (
            "PROJECT_CLOSED_UNDER_EXACT_BROAD_OWNER_SCOPE__NOT_OWNER_"
            "EXACT_BYTE_APPROVAL"),
        "owner_directive_receipt_file": file_record(OWNER_RECEIPT),
        "preaction_file": file_record(PREACTION),
        "scientific_manifest": files["scientific_manifest"],
        "executable_manifest": files["executable_manifest"],
        "target_manifest_file": file_record(target_path),
        "execution_request_file": file_record(request_path),
        "schedule_sha256": SCHEDULE_SHA256,
        "clock_rule": CLOCK_RULE,
        "steady_median_rule": STEADY_MEDIAN_RULE,
        "bootstrap_rule": BOOTSTRAP_RULE,
        "block_order_rule": BLOCK_ORDER_RULE,
        "execution_concurrency_rule": EXECUTION_CONCURRENCY_RULE,
        "cache_rule": CACHE_RULE,
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "authorization_not_before_utc": request[
            "authorization_not_before_utc"],
        "authorization_not_after_utc": request[
            "authorization_not_after_utc"],
        "invalid_row_rule": INVALID_ROW_RULE,
        "owner_target_bound_exact_bytes_approval_claimed": False,
        "project_materialized_under_owner_scope": True,
        "formal_worker_zero_authorized_under_owner_scope": True,
        "pod_gpu_timing_authorized_under_owner_scope": True,
        "descriptive_unconditional_acceptance": True,
        "confirmatory_noninferiority_claim": False,
        "threshold_count": 0,
        "retry_resume_replacement_or_row_drop_allowed": False,
        "total_worker_count": TOTAL_WORKER_COUNT,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    value = _seal_closure(value)
    path = directory / "project_closure.json"
    path.write_bytes(canonical_document(value))
    return path, value


class _FakeArm:
    def __init__(self, label, capability, output, admitted, events):
        self.label = label
        self.deployment_capability = capability
        self.output = output
        self.admitted = admitted
        self.events = events
        self.admitted_arguments = []

    def execute_exact_core(self, admitted):
        self.events.append("execute_core")
        self.admitted_arguments.append(admitted)
        if admitted is not self.admitted:
            raise AssertionError("prevalidated input identity changed")
        return object()

    def materialize_exact_core(self, completion):
        self.events.append("materialize")
        return KatArmSuccess(
            arm=self.label,
            output=self.output,
            control=(5_000, 0xFFFFFFFF, 0, 0),
            ledger=SUCCESS_LEDGER,
        )

    def close(self):
        self.events.append("close")


def _fake_bundle():
    expected = np.zeros((5_000, 3), dtype=np.uint32)
    output = np.zeros((3, 5_000), dtype=np.uint32).T
    output.setflags(write=False)
    return SimpleNamespace(
        shape=SimpleNamespace(query_count=5_000),
        success_queries=object(),
        expected_output=expected,
        deployment_capability=object(),
    ), output


class Goal5814MeasurementProtocolTest(unittest.TestCase):
    def test_frozen_preaction_and_exact_144_schedule(self):
        validate_preaction(PREACTION)
        rows = schedule()
        self.assertEqual(len(rows), 144)
        self.assertEqual(len({row.worker_id for row in rows}), 144)
        self.assertEqual([row.ordinal for row in rows], list(range(144)))
        for regime in REGIMES:
            selected = [row for row in rows if row.regime == regime]
            self.assertEqual(len(selected), 48)
            orders = []
            for block in range(BLOCK_COUNT):
                block_rows = [row for row in selected if row.block == block]
                block_rows.sort(key=lambda row: row.position)
                orders.append(tuple(row.arm for row in block_rows))
            self.assertEqual(orders.count((ARM_B, ARM_D)), 12)
            self.assertEqual(orders.count((ARM_D, ARM_B)), 12)

    def test_target_kat_runtime_and_owner_authority_gates(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            target_path, target = _target_fixture(directory)
            observed = _validate_fixture_target(target_path)
            validate_owner_directive_receipt(OWNER_RECEIPT, root=ROOT)
            request_path, request = _request_fixture(
                directory, target_path, target)
            validate_execution_request(
                request_path,
                preaction_path=PREACTION,
                target_manifest_path=target_path,
                target_manifest=observed,
            )
            closure_path, closure = _closure_fixture(
                directory, target_path, target, request_path, request)
            validate_project_closure(
                closure_path,
                preaction_path=PREACTION,
                target_manifest_path=target_path,
                execution_request_path=request_path,
                target_manifest=observed,
                execution_request=request,
            )
            with self.assertRaises(MeasurementProtocolError):
                validate_execution_authority(
                    request_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    target_manifest=observed)
            with patch.dict(
                    os.environ, {PROJECT_CLOSURE_ENV: str(closure_path)}):
                worker_gate = validate_execution_authority(
                    request_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    target_manifest=observed)
            self.assertEqual(worker_gate, closure)
            validate_authority_window(
                closure,
                now=datetime(2026, 8, 28, 4, tzinfo=timezone.utc))
            with self.assertRaises(MeasurementProtocolError):
                validate_authority_window(
                    closure,
                    now=datetime(2026, 8, 29, tzinfo=timezone.utc))

            class Completed:
                returncode = 0
                stdout = (
                    b"GPU-b7695ce1-4b15-b15c-0d4a-52da0b65213e, "
                    b"NVIDIA RTX A5000, 8.6, "
                    b"570.211.01, 24564\n")
                stderr = b""

            runtime = {
                "numpy_version": "2.4.4",
                "cupy_version": "14.0.1",
                "pyoptix_distribution_version": "9.1.0",
                "optix_api_version": "9.0.0",
                "numpy_module": target["files"]["numpy_module"]["path"],
                "cupy_module": target["files"]["cupy_module"]["path"],
                "optix_module": target["files"]["optix_module"]["path"],
                "pyoptix_extension": target["files"][
                    "pyoptix_extension"]["path"],
            }
            live = validate_live_target(
                target,
                run=lambda *args, **kwargs: Completed(),
                hostname="b7f901018414",
                python_executable=sys.executable,
                python_version="3.12.3",
                runtime_identity=runtime,
                environment={"CUDA_VISIBLE_DEVICES": "0"},
            )
            self.assertEqual(
                live["gpu_uuid"],
                "GPU-b7695ce1-4b15-b15c-0d4a-52da0b65213e")

            tampered = deepcopy(target)
            tampered["target"]["hostname"] = "coherent-reseal-attacker"
            unsigned = dict(tampered)
            unsigned.pop("target_manifest_sha256")
            tampered["target_manifest_sha256"] = digest(unsigned)
            tampered_path = directory / "target_tampered.json"
            tampered_path.write_bytes(canonical_document(tampered))
            with self.assertRaises(MeasurementProtocolError):
                _validate_fixture_target(tampered_path)

            missing_extension = deepcopy(target)
            del missing_extension["files"]["pyoptix_extension"]
            unsigned = dict(missing_extension)
            unsigned.pop("target_manifest_sha256")
            missing_extension["target_manifest_sha256"] = digest(unsigned)
            missing_path = directory / "target_missing_extension.json"
            missing_path.write_bytes(canonical_document(missing_extension))
            with self.assertRaises(MeasurementProtocolError):
                _validate_fixture_target(missing_path)

    def test_v2_chain_rejects_downgrade_coherent_reseal_and_false_owner_claim(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            target_path, target = _target_fixture(directory)
            observed = _validate_fixture_target(target_path)
            request_path, request = _request_fixture(
                directory, target_path, target)
            closure_path, closure = _closure_fixture(
                directory, target_path, target, request_path, request)

            old_target = deepcopy(target)
            old_target["schema"] = (
                "rtdl.goal5814.particle_measurement_target.v1")
            old_target.pop("target_manifest_sha256")
            old_target = _seal_target(old_target)
            old_target_path = directory / "old_target_resealed.json"
            old_target_path.write_bytes(canonical_document(old_target))
            with self.assertRaises(MeasurementProtocolError):
                _validate_fixture_target(old_target_path)

            old_request = deepcopy(request)
            old_request["schema"] = (
                "rtdl.goal5814.particle_measurement_execution_authority.v1")
            old_request.pop("execution_request_sha256")
            old_request = _seal_request(old_request)
            old_request_path = directory / "old_request_resealed.json"
            old_request_path.write_bytes(canonical_document(old_request))
            with self.assertRaises(MeasurementProtocolError):
                validate_execution_request(
                    old_request_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    target_manifest=observed)

            bool_count_request = deepcopy(request)
            bool_count_request["threshold_count"] = False
            bool_count_request.pop("execution_request_sha256")
            bool_count_request = _seal_request(bool_count_request)
            bool_count_request_path = directory / "bool_count_request.json"
            bool_count_request_path.write_bytes(
                canonical_document(bool_count_request))
            with self.assertRaises(MeasurementProtocolError):
                validate_execution_request(
                    bool_count_request_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    target_manifest=observed)

            changed_request = deepcopy(request)
            changed_request["authorization_not_after_utc"] = (
                "2026-08-28T07:59:59Z")
            changed_request.pop("execution_request_sha256")
            changed_request = _seal_request(changed_request)
            request_path.write_bytes(canonical_document(changed_request))
            validate_execution_request(
                request_path, preaction_path=PREACTION,
                target_manifest_path=target_path,
                target_manifest=observed)
            with self.assertRaises(MeasurementProtocolError):
                validate_project_closure(
                    closure_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    execution_request_path=request_path,
                    target_manifest=observed,
                    execution_request=changed_request)

            request_path.write_bytes(canonical_document(request))
            changed_target = deepcopy(target)
            changed_target["target"]["gpu_memory_total_mib"] += 1
            changed_target.pop("target_manifest_sha256")
            changed_target = _seal_target(changed_target)
            target_path.write_bytes(canonical_document(changed_target))
            changed_observed = _validate_fixture_target(target_path)
            changed_request = deepcopy(request)
            changed_request["target_manifest_file"] = file_record(target_path)
            changed_request.pop("execution_request_sha256")
            changed_request = _seal_request(changed_request)
            request_path.write_bytes(canonical_document(changed_request))
            validate_execution_request(
                request_path, preaction_path=PREACTION,
                target_manifest_path=target_path,
                target_manifest=changed_observed)
            with self.assertRaises(MeasurementProtocolError):
                validate_project_closure(
                    closure_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    execution_request_path=request_path,
                    target_manifest=changed_observed,
                    execution_request=changed_request)

            target_path.write_bytes(canonical_document(target))
            request_path.write_bytes(canonical_document(request))
            false_claim = deepcopy(closure)
            false_claim["owner_target_bound_exact_bytes_approval_claimed"] = True
            false_claim.pop("project_closure_sha256")
            false_claim = _seal_closure(false_claim)
            false_claim_path = directory / "false_owner_claim_resealed.json"
            false_claim_path.write_bytes(canonical_document(false_claim))
            with self.assertRaises(MeasurementProtocolError):
                validate_project_closure(
                    false_claim_path, preaction_path=PREACTION,
                    target_manifest_path=target_path,
                    execution_request_path=request_path,
                    target_manifest=observed,
                    execution_request=request)

            for field, changed in (
                    ("schema", "rtdl.goal5814.project_closure.v1"),
                    ("project_materialized_under_owner_scope", False),
                    ("formal_worker_zero_authorized_under_owner_scope", False),
                    ("pod_gpu_timing_authorized_under_owner_scope", False),
                    ("retry_resume_replacement_or_row_drop_allowed", True),
                    ("threshold_count", 1),
                    ("threshold_count", False),
                    ("registered_performance_timing_count", False),
                    ("formal_worker_count", False),
                    ("total_worker_count", TOTAL_WORKER_COUNT - 1)):
                with self.subTest(project_closure_field=field):
                    downgraded = deepcopy(closure)
                    downgraded[field] = changed
                    downgraded.pop("project_closure_sha256")
                    downgraded = _seal_closure(downgraded)
                    downgraded_path = directory / f"closure_{field}.json"
                    downgraded_path.write_bytes(canonical_document(downgraded))
                    with self.assertRaises(MeasurementProtocolError):
                        validate_project_closure(
                            downgraded_path, preaction_path=PREACTION,
                            target_manifest_path=target_path,
                            execution_request_path=request_path,
                            target_manifest=observed,
                            execution_request=request)

            receipt_root = directory / "receipt_root"
            receipt_copy = receipt_root / OWNER_DIRECTIVE_RECEIPT_RELATIVE_PATH
            receipt_copy.parent.mkdir(parents=True)
            receipt_copy.write_bytes(OWNER_RECEIPT.read_bytes())
            validate_owner_directive_receipt(receipt_copy, root=receipt_root)
            receipt_copy.write_bytes(receipt_copy.read_bytes() + b" ")
            with self.assertRaises(MeasurementProtocolError):
                validate_owner_directive_receipt(
                    receipt_copy, root=receipt_root)

    def test_controller_detects_control_plane_mutation(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            paths = {}
            for index, name in enumerate((
                    "owner_directive_receipt", "preaction", "target_manifest",
                    "execution_request", "project_closure")):
                path = directory / f"{index}.json"
                path.write_bytes(f"{name}\n".encode("utf-8"))
                paths[name] = path
            expected = controller_module._control_records(paths)
            controller_module._require_control_records_unchanged(
                paths, expected)
            paths["execution_request"].write_bytes(b"coherent-reseal\n")
            with self.assertRaises(controller_module.ControllerError):
                controller_module._require_control_records_unchanged(
                    paths, expected)

            environment = {PROJECT_CLOSURE_ENV: "attacker-selected"}
            controller_module._bind_project_closure_environment(
                environment, paths["project_closure"])
            self.assertEqual(
                environment[PROJECT_CLOSURE_ENV],
                str(paths["project_closure"].resolve(strict=True)))

    def test_all_regime_clock_boundaries_and_oracle_identity_are_symmetric(self):
        for arm_label in (ARM_B, ARM_D):
            for regime in REGIMES:
                with self.subTest(arm=arm_label, regime=regime):
                    bundle, output = _fake_bundle()
                    events = []
                    arms = []
                    admitted = object()

                    def factory(observed):
                        self.assertIs(observed, bundle)
                        events.append("factory")
                        arm = _FakeArm(
                            arm_label, bundle.deployment_capability,
                            output, admitted, events)
                        arms.append(arm)
                        return arm

                    tick = 0

                    def clock():
                        nonlocal tick
                        events.append("clock")
                        tick += 10
                        return tick

                    result = run_regime(
                        bundle=bundle,
                        arm_label=arm_label,
                        regime=regime,
                        factory=factory,
                        admitted_input=admitted,
                        clock=clock,
                    )
                    self.assertEqual(events[-1], "close")
                    self.assertTrue(all(
                        item is admitted
                        for item in arms[0].admitted_arguments))
                    if regime == "DEPLOYMENT_COLD":
                        self.assertEqual(
                            events[:5], [
                                "clock", "factory", "execute_core", "clock",
                                "materialize"])
                        self.assertEqual(result["registered_performance_timing_count"], 1)
                    elif regime == "PREPARE":
                        self.assertEqual(events[:7], [
                            "clock", "factory", "clock",
                            "clock", "execute_core", "clock", "materialize"])
                        self.assertEqual(result["registered_performance_timing_count"], 2)
                    else:
                        self.assertEqual(events[0], "factory")
                        self.assertEqual(events[1:17], [
                            value for _ in range(8)
                            for value in ("execute_core", "materialize")])
                        self.assertEqual(events.count("execute_core"), 72)
                        self.assertEqual(events.count("materialize"), 72)
                        self.assertEqual(events.count("clock"), 128)
                        self.assertEqual(len(result["primary_samples_ns"]), 64)

    def test_controller_collision_is_zero_process_and_no_resume_surface(self):
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "already_exists"
            output.mkdir()
            calls = []
            with self.assertRaises(controller_module.ControllerError):
                controller_module.run_formal_controller(
                    root=ROOT,
                    preaction_path=Path(raw) / "missing-preaction",
                    target_manifest_path=Path(raw) / "missing-target",
                    execution_request_path=Path(raw) / "missing-request",
                    project_closure_path=Path(raw) / "missing-closure",
                    output_root=output,
                    process_runner=lambda *args, **kwargs: calls.append(args),
                )
            self.assertEqual(calls, [])
        parser = controller_module._argument_parser()
        option_strings = {
            option for action in parser._actions for option in action.option_strings}
        self.assertNotIn("--resume", option_strings)
        self.assertNotIn("--retry", option_strings)
        self.assertNotIn("--worker-limit", option_strings)
        self.assertIn("--project-closure", option_strings)
        self.assertIn("--execution-request", option_strings)
        self.assertNotIn("--authority", option_strings)
        preflight_options = {
            option for action in preflight_module._argument_parser()._actions
            for option in action.option_strings}
        self.assertIn("--project-closure", preflight_options)
        self.assertIn("--execution-request", preflight_options)
        self.assertNotIn("--authority", preflight_options)


def _receipt(phase: str, repetition: int) -> dict[str, object]:
    return {
        "phase": phase,
        "repetition": repetition,
        "control": [5_000, 0xFFFFFFFF, 0, 0],
        "ledger": SUCCESS_LEDGER.__dict__.copy(),
        "exact_worker_check_after_end_clock": True,
        "output_borrowed_read_only": True,
        "output_shape": [5_000, 3],
        "output_strides": [4, 20_000],
    }


def _formal_controller_fixture(
        raw_root: Path | None = None) -> dict[str, object]:
    identity = {
        "path": str((ROOT / "frozen-placeholder").resolve()),
        "bytes": 1,
        "sha256": "0" * 64,
    }
    workers = []
    timing_count = 0
    for spec in schedule():
        base = 1_000 + spec.block * 100
        multiplier = 1 if spec.arm == ARM_B else 2
        if spec.regime == "STEADY_DYNAMIC_E2E":
            samples = [multiplier * (base + index) for index in range(64)]
            primary = statistics.median(samples)
            receipts = [
                *[_receipt("STEADY_WARMUP", index) for index in range(8)],
                *[_receipt("STEADY_TIMED", index) for index in range(64)],
            ]
            first = None
            warmups = 8
            registered = 64
            reads = 128
        else:
            samples = [multiplier * base]
            primary = samples[0]
            receipts = [_receipt(
                "COLD_FIRST_COMPLETE_EXECUTE"
                if spec.regime == "DEPLOYMENT_COLD" else
                "FIRST_COMPLETE_EXECUTE_OUTSIDE_PREPARE_PRIMARY", 0)]
            first = multiplier * 777 if spec.regime == "PREPARE" else None
            warmups = 0
            registered = 2 if spec.regime == "PREPARE" else 1
            reads = registered * 2
        measurement = {
            "regime": spec.regime,
            "arm": spec.arm,
            "primary_value_ns": primary,
            "primary_samples_ns": samples,
            "first_execute_outside_primary_ns": first,
            "warmup_execute_count": warmups,
            "complete_execute_count": len(receipts),
            "execution_receipts": receipts,
            "clock": "time.perf_counter_ns",
            "clock_read_count": reads,
            "registered_performance_timing_count": registered,
            "close_after_all_registered_end_clocks": True,
        }
        result = {
            "schema": "rtdl.goal5814.particle_formal_worker_result.v2",
            "status": "PASS__ONE_FRESH_PROCESS_FORMAL_ROW",
            "worker_id": spec.worker_id,
            "ordinal": spec.ordinal,
            "regime": spec.regime,
            "block": spec.block,
            "position": spec.position,
            "arm": spec.arm,
            "pid": 10_000 + spec.ordinal,
            "parent_pid": 999,
            "preaction_file": identity,
            "target_manifest_file": identity,
            "execution_request_file": identity,
            "project_closure_file": identity,
            "target_observation": {"target": "same"},
            "deployment_capability": {"capability": "same"},
            "schedule_sha256": SCHEDULE_SHA256,
            "measurement": measurement,
            "timed": True,
            "retry_count": 0,
            "resume_count": 0,
            "replacement_count": 0,
            "row_drop_count": 0,
            "formal_worker_count": 1,
            "registered_performance_timing_count": registered,
        }
        timing_count += registered
        stdout_identity = identity
        stderr_identity = identity
        if raw_root is not None:
            worker_directory = raw_root / spec.worker_id
            worker_directory.mkdir(parents=True, exist_ok=False)
            stdout_path = worker_directory / "stdout.json"
            stderr_path = worker_directory / "stderr.bin"
            stdout_path.write_bytes(canonical_document(result))
            stderr_path.write_bytes(b"")
            stdout_identity = file_record(stdout_path)
            stderr_identity = file_record(stderr_path)
        workers.append({
            "ordinal": spec.ordinal,
            "regime": spec.regime,
            "block": spec.block,
            "position": spec.position,
            "arm": spec.arm,
            "worker_id": spec.worker_id,
            "result": result,
            "stdout_file": stdout_identity,
            "stderr_file": stderr_identity,
            "isolated_cache_files_after": [],
        })
    return {
        "schema": "rtdl.goal5814.particle_formal_controller_result.v2",
        "status": "COMPLETE__144_FRESH_PROCESSES__NO_RETRY_OR_REPLACEMENT",
        "preaction_file": identity,
        "target_manifest_file": identity,
        "execution_request_file": identity,
        "project_closure_file": identity,
        "schedule_sha256": SCHEDULE_SHA256,
        "schedule": schedule_document(),
        "workers": workers,
        "execution_concurrency": EXECUTION_CONCURRENCY_RULE,
        "invalid_row_disposition": INVALID_ROW_RULE,
        "timed": True,
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
        "formal_worker_count": 144,
        "unique_worker_pid_count": 144,
        "registered_performance_timing_count": timing_count,
    }


class Goal5814EvaluationTest(unittest.TestCase):
    def test_independent_recount_survives_output_root_relocation(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            original = base / "original"
            controller = _formal_controller_fixture(original)
            evaluation = evaluate(controller)
            for row in controller["workers"]:
                for field in ("stdout_file", "stderr_file"):
                    absolute = Path(row[field]["path"])
                    row[field]["path"] = absolute.relative_to(
                        original).as_posix()
            (original / "controller.json").write_bytes(
                canonical_document(controller))
            (original / "evaluation.json").write_bytes(
                canonical_document(evaluation))
            relocated = base / "relocated"
            shutil.move(str(original), str(relocated))
            rebuilt = recount_files(
                relocated / "controller.json",
                relocated / "evaluation.json",
                relocated / "recount.json")
            self.assertEqual(rebuilt["formal_worker_count"], 144)
            self.assertEqual(
                rebuilt["registered_performance_timing_count"], 3216)

    def test_primary_and_independent_recount_exact_descriptive_result(self):
        with tempfile.TemporaryDirectory() as raw:
            controller = _formal_controller_fixture(Path(raw))
            result = evaluate(controller)
            self.assertEqual(len(result["rows"]), 3)
            self.assertEqual(result["threshold_count"], 0)
            self.assertFalse(result["confirmatory_noninferiority_claim"])
            for row in result["rows"]:
                self.assertEqual(row["rtdl_over_pyoptix"], 2.0)
                self.assertEqual(
                    row["rtdl_over_pyoptix_ci95_fixed_indices"], [2.0, 2.0])
                self.assertIsNone(row["threshold"])
                self.assertIsNone(row["confirmatory_pass_fail"])
                self.assertEqual(len(row["blocks"]), 24)
            steady = result["rows"][2]
            self.assertEqual(steady["b_pyoptix_absolute_median_ns"] % 1, 0.5)
            independent = recount(controller, evaluation=result)
            self.assertEqual(independent["rows"], result["rows"])
            self.assertTrue(independent["primary_evaluation_compared"])
            self.assertTrue(independent["raw_worker_files_reopened"])
            self.assertEqual(independent["raw_worker_stdout_file_count"], 144)
            self.assertEqual(independent["raw_worker_stderr_file_count"], 144)
            self.assertEqual(
                independent["registered_performance_timing_count"], 3_216)
            self.assertEqual(independent["retry_count"], 0)
            controller_path = Path(raw) / "controller.json"
            evaluation_path = Path(raw) / "evaluation.json"
            recount_path = Path(raw) / "recount.json"
            controller_path.write_bytes(canonical_document(controller))
            evaluation_path.write_bytes(canonical_document(result))
            from_files = recount_files(
                controller_path, evaluation_path, recount_path)
            self.assertEqual(from_files, independent)
            self.assertEqual(
                recount_path.read_bytes(), canonical_document(independent))

    def test_independent_recount_requires_existing_raw_files(self):
        controller = _formal_controller_fixture()
        with self.assertRaises(RecountError):
            recount(controller)
        with self.assertRaises(RecountError):
            recount(controller, reopen_raw_files=False)
        with tempfile.TemporaryDirectory() as raw:
            controller = _formal_controller_fixture(Path(raw))
            Path(controller["workers"][0]["stdout_file"]["path"]).unlink()
            with self.assertRaises(RecountError):
                recount(controller)
        with tempfile.TemporaryDirectory() as raw:
            controller = _formal_controller_fixture(Path(raw))
            controller["workers"][0]["stdout_file"]["sha256"] = "f" * 64
            with self.assertRaises(RecountError):
                recount(controller)

    def test_independent_recount_rejects_resealed_worker_accounting_tamper(self):
        mutations = (
            ("retry", lambda result: result.__setitem__("retry_count", 1)),
            ("registered", lambda result: (
                result.__setitem__("registered_performance_timing_count", 999),
                result["measurement"].__setitem__(
                    "registered_performance_timing_count", 999))),
        )
        for label, mutate in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as raw:
                controller = _formal_controller_fixture(Path(raw))
                result = controller["workers"][0]["result"]
                mutate(result)
                stdout_path = Path(
                    controller["workers"][0]["stdout_file"]["path"])
                stdout_path.write_bytes(canonical_document(result))
                controller["workers"][0]["stdout_file"] = file_record(stdout_path)
                with self.assertRaises(RecountError):
                    recount(controller)

    def test_independent_recount_rejects_duplicate_or_omitted_schedule_row(self):
        for label, mutate in (
                ("duplicate", lambda workers: workers.__setitem__(
                    1, deepcopy(workers[0]))),
                ("omitted", lambda workers: workers.pop())):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as raw:
                controller = _formal_controller_fixture(Path(raw))
                mutate(controller["workers"])
                with self.assertRaises(RecountError):
                    recount(controller)

    def test_invalid_steady_median_and_duplicate_pid_rejected(self):
        controller = _formal_controller_fixture()
        controller["workers"][96]["result"]["measurement"][
            "primary_value_ns"] = int(controller["workers"][96]["result"][
                "measurement"]["primary_value_ns"])
        with self.assertRaises(EvaluationError):
            evaluate(controller)
        controller = _formal_controller_fixture()
        controller["workers"][1]["result"]["pid"] = controller[
            "workers"][0]["result"]["pid"]
        with self.assertRaises(EvaluationError):
            evaluate(controller)

    def test_bootstrap_is_exact_random_choices_fixed_indices(self):
        ratios = [1.0 + index / 100.0 for index in range(24)]
        generator = random.Random(BOOTSTRAP_SEED_BASE)
        draws = sorted(float(statistics.median(
            generator.choices(ratios, k=24))) for _ in range(BOOTSTRAP_DRAWS))
        expected = (
            draws[BOOTSTRAP_CI_INDICES[0]],
            draws[BOOTSTRAP_CI_INDICES[1]],
        )
        self.assertEqual(_bootstrap(ratios, 0), expected)

    def test_formal_source_has_fixed_factories_and_no_transpose_convenience(self):
        worker = (ROOT / "experiments/goal5814_particle/formal_worker.py").read_text(
            encoding="utf-8")
        controller = (ROOT / "experiments/goal5814_particle/controller.py").read_text(
            encoding="utf-8")
        self.assertNotIn("--factory", worker)
        self.assertNotIn("_run_success(", worker)
        self.assertNotIn("np.ascontiguousarray", worker)
        self.assertNotIn("queries.T", worker)
        self.assertNotIn("--resume", controller)
        self.assertIn("_prepare_public_pyoptix_formal_arm", worker)
        self.assertIn("_prepare_public_verified_rtdlexe_formal_arm", worker)
        self.assertNotIn("prepare_public_pyoptix_kat_arm", worker)
        self.assertNotIn("prepare_public_verified_rtdlexe_kat_arm", worker)
        self.assertIn("prevalidate_formal_particle_execution_input(", worker)
        self.assertIn(
            "prevalidate_particle_rtdlexe_exact_core_input(", worker)
        self.assertIn("execute_exact_core_prevalidated(admitted)", worker)
        self.assertIn("execute_exact_core(admitted_input)", worker)
        self.assertIn("materialize_exact_core(completion)", worker)
        admission = worker.index(
            "prevalidate_particle_rtdlexe_exact_core_input(")
        regime = worker.index("measurement = run_regime(", admission)
        self.assertLess(admission, regime)


if __name__ == "__main__":
    unittest.main()
