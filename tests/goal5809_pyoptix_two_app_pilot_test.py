from __future__ import annotations

import argparse
import hashlib
import inspect
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import numpy as np

from experiments import goal5809_pyoptix_bulk_input as bulk_input
from experiments.goal5802_premeasurement import pyoptix_scalar_arm as real_arm
from scripts import goal5809_pyoptix_two_app_pilot as pilot


_FAKE_PTX = b".version 8.0\n"
_FAKE_CUBIN = b"cubin"


class _Clock:
    def __init__(self) -> None:
        self.value = 10_000

    def __call__(self) -> int:
        self.value += 50
        return self.value


class _Adapter:
    def __init__(
        self, task: str, workload: dict[str, object], *,
        ptx_path: Path, compaction_cubin_path: Path | None,
        preloaded_runtime: object, runtime_preload_receipt: dict[str, object],
        events: list[str], wrong_task: str | None,
    ) -> None:
        del task, ptx_path, runtime_preload_receipt
        self.task_key = (
            "relation" if compaction_cubin_path is not None else "triangle")
        self.workload = workload
        self.baseline = preloaded_runtime
        self.events = events
        self.wrong_task = wrong_task
        self.ptx: bytes | None = None
        self.owner: object | None = None
        self._loaded = False
        self.context: object | None = None
        self.logger = None
        self.pipeline = None
        self.pipeline_keepalive = None
        self.sbt = None
        self.sbt_keepalive = None
        self.compaction_cubin = (
            _FAKE_CUBIN if self.task_key == "relation" else None)
        self._compaction_cubin_memfd = (
            {"proc_fd_path": "/proc/self/fd/99"}
            if self.task_key == "relation" else None)
        self.compaction_module = None
        self.compaction_kernel = None
        self.record_operation_evidence = False
        self._measurement_execute = None
        self._relation_loader_closed = False

    def load(self) -> None:
        self.events.append(f"load:{self.task_key}")
        self.ptx = _FAKE_PTX
        self._loaded = True

    def execute(self) -> object:
        return self._measurement_execute()

    def close(self) -> None:
        self.events.append(f"close:{self.task_key}")
        if self.owner is not None:
            self.owner.close()
        self.owner = None
        if self.task_key == "relation":
            self._relation_loader_closed = True

    @property
    def compaction_cubin_loader_closed(self) -> bool | None:
        return (
            self._relation_loader_closed
            if self.task_key == "relation" else None)


class _Context:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.cache_values: list[bool] = []

    def setCacheEnabled(self, value: bool) -> None:
        self.events.append(f"context.cache:{value}")
        self.cache_values.append(value)


class _Owner:
    def __init__(
        self, task_key: str, events: list[str], *, wrong: bool,
        context: object,
    ) -> None:
        self.task_key = task_key
        self.events = events
        self.wrong = wrong
        self.context = context

    def execute(self) -> object:
        self.events.append(f"execute:{self.task_key}")
        if self.task_key == "relation":
            return SimpleNamespace(
                output=[[99, 99]] if self.wrong else [[7, 7]],
                device_status=0, device_overflow=0)
        return SimpleNamespace(
            reduced_u64=999 if self.wrong else 5, device_status=0)

    def close(self) -> None:
        pass


class _RawModule:
    def get_function(self, name: str) -> object:
        return ("kernel", name)


class _Baseline(SimpleNamespace):
    def __init__(self) -> None:
        box_dtype = np.dtype([
            ("lower_x", "f4"), ("lower_y", "f4"), ("lower_z", "f4"),
            ("upper_x", "f4"), ("upper_y", "f4"), ("upper_z", "f4"),
            ("item_id", "u4"),
        ], align=True)
        ray_dtype = np.dtype([
            ("origin_x", "f4"), ("origin_y", "f4"),
            ("origin_z", "f4"), ("direction_x", "f4"),
            ("direction_y", "f4"), ("direction_z", "f4"),
        ], align=True)
        super().__init__(
            __name__="goal5796.pyoptix_baseline",
            np=np, BOX_DTYPE=box_dtype, RAY_DTYPE=ray_dtype,
            optix=SimpleNamespace(),
            cp=SimpleNamespace(
                __version__="13.0.0",
                RawModule=lambda **_kwargs: _RawModule()))

    @staticmethod
    def make_sbt(keepalive: object) -> tuple[object, object]:
        return ("sbt", keepalive), ("sbt-keepalive", keepalive)


class _Arm:
    __name__ = "experiments.goal5802_premeasurement.pyoptix_scalar_arm"

    def __init__(
        self, events: list[str], *, wrong_task: str | None = None,
    ) -> None:
        self.events = events
        self.wrong_task = wrong_task
        self.context_calls = 0
        self.context: _Context | None = None
        self.owner_calls = {"relation": 0, "triangle": 0}
        self.host_inputs: dict[str, object] = {}
        self.relation_validate_expected_rows: bool | None = None

    def PyOptixScalarAdapter(self, *args: object, **kwargs: object) -> _Adapter:
        return _Adapter(
            *args, **kwargs, events=self.events, wrong_task=self.wrong_task)

    def _make_validation_off_context(
        self, _baseline: object,
    ) -> tuple[_Context, None]:
        self.context_calls += 1
        self.events.append("context.create")
        self.context = _Context(self.events)
        return self.context, None

    @staticmethod
    def _build_comparative_pipeline(
        _baseline: object, context: object, _ptx: bytes, *, task: str,
    ) -> tuple[object, object, dict[str, object]]:
        return ("pipeline", task, context), ("keepalive", task), {}

    @staticmethod
    def _validate_write_sealed_memfd(_row: object) -> None:
        return None

    def DeferredRelationPrepared(
        self, _baseline: object, context: object, _pipeline: object,
        _sbt: object, _fixture: object, **_kwargs: object,
    ) -> _Owner:
        self.owner_calls["relation"] += 1
        self.host_inputs["relation"] = _kwargs["host_inputs"]
        self.relation_validate_expected_rows = bool(
            _kwargs["validate_expected_rows"])
        self.events.append("prepare:relation")
        return _Owner(
            "relation", self.events, wrong=self.wrong_task == "relation",
            context=context)

    def ScalarTrianglePrepared(
        self, _baseline: object, context: object, _pipeline: object,
        _sbt: object, _workload: object, **_kwargs: object,
    ) -> _Owner:
        self.owner_calls["triangle"] += 1
        self.host_inputs["triangle"] = _kwargs["host_inputs"]
        self.events.append("prepare:triangle")
        return _Owner(
            "triangle", self.events, wrong=self.wrong_task == "triangle",
            context=context)


class _Workloads:
    __file__ = __file__

    @staticmethod
    def relation_workload() -> dict[str, object]:
        return {
            "task": "RELATION",
            "indexed": [[0.0, 0.0, 1.0, 1.0, 7]],
            "sources": [[0.0, 0.0, 1.0, 1.0, 7]],
            "minimum_overlap_f32": 1.0,
            "semantic_capacity": 1,
            "expected_rows": [[7, 7]],
        }

    @staticmethod
    def triangle_workload() -> dict[str, object]:
        return {
            "task": "TRIANGLE",
            "vertices": [
                [-1.0, -1.0, 1.0],
                [1.0, -1.0, 1.0],
                [0.0, 1.0, 1.0],
            ],
            "queries": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 2.0]],
            "weights": [5],
            "expected_reduced_u64": 5,
        }


def _admitted(root: Path) -> dict[str, object]:
    return {
        "target_path": root / "target.json",
        "target_file_sha256": "a" * 64,
        "target": {
            "target_manifest_sha256": "b" * 64,
            "files": {
                "matched_ptx": {
                    "path": str(root / "matched.ptx"),
                    "sha256": hashlib.sha256(_FAKE_PTX).hexdigest(),
                },
                "relation_compaction_cubin": {
                    "path": str(root / "compact.cubin"),
                    "sha256": hashlib.sha256(_FAKE_CUBIN).hexdigest(),
                },
            },
        },
    }


class PyOptixTwoAppPilotTest(unittest.TestCase):
    def _run(
        self, root: Path, *, first_app: str,
        wrong_task: str | None = None,
    ) -> tuple[dict[str, object], list[str], _Arm]:
        events: list[str] = []
        arm = _Arm(events, wrong_task=wrong_task)
        baseline = _Baseline()
        args = argparse.Namespace(
            target_manifest=root / "target.json",
            expected_target_manifest_sha256="a" * 64,
            execution_identity_manifest=root / "execution_identity.json",
            expected_execution_identity_manifest_sha256="b" * 64,
            first_app=first_app,
        )
        with mock.patch.object(
                pilot, "_admit_target",
                return_value=_admitted(root)), mock.patch.object(
                pilot, "_preload_runtime",
                return_value=(
                    _Workloads, arm, baseline,
                    {"status": "PASS__SYNTHETIC_PRELOAD"}, bulk_input)), \
                mock.patch.object(
                    pilot, "admit_execution_identity",
                    return_value={
                        "manifest_file_sha256": "b" * 64,
                        "execution_identity_sha256": "c" * 64,
                        "file_count": 27,
                        "files_rehashed": True,
                        "runtime_environment_admission": {
                            "environment_identity_sha256": "7" * 64,
                        },
                    }), mock.patch.object(
                    pilot, "verify_loaded_pyoptix",
                    return_value={
                        "pyoptix_loaded_identity_verified": True,
                        "distribution_version": "9.1.0",
                        "api_version": "9.0.0",
                    }), mock.patch.object(
                    pilot, "verify_loaded_modules",
                    return_value={
                        "loaded_module_identity_verified": True,
                        "loaded_modules": {},
                    }), mock.patch.object(
                    pilot, "verify_loaded_runtime_dependencies",
                    return_value={
                        "loaded_dependency_identity_sha256": "8" * 64,
                    }), mock.patch.object(
                    pilot.importlib.metadata, "version",
                    return_value="12.9.0"), mock.patch.dict(pilot.sys.modules, {
                    }), mock.patch.dict(pilot.sys.modules, {
                        "experiments.goal5800_pyoptix_owl."
                        "pyoptix_idiomatic_arm": SimpleNamespace(
                            __file__=str(root / "idiomatic.py")),
                    }):
            result = pilot._run(args, clock=_Clock())
        return result, events, arm

    def test_natural_owners_execute_both_apps_once_in_requested_order(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, events, _arm = self._run(
                Path(temporary), first_app="triangle")

        self.assertEqual(events, [
            "load:relation", "load:triangle",
            "context.create", "context.cache:False",
            "prepare:triangle", "execute:triangle",
            "prepare:relation", "execute:relation",
            "close:relation", "close:triangle",
        ])
        self.assertEqual(result["lifecycle"]["app_order"], [
            "triangle", "relation"])
        self.assertEqual(result["lifecycle"]["runtime_preload_call_count"], 1)
        self.assertEqual(result["lifecycle"]["runtime_session_count"], 0)
        self.assertEqual(
            result["lifecycle"]["runtime_session_admission_phase"],
            "NOT_APPLICABLE__ONE_SHARED_OPTIX_DEVICE_CONTEXT_INSTEAD")
        self.assertEqual(
            result["lifecycle"][
                "shared_optix_device_context_admission_call_count"], 1)
        self.assertEqual(result["lifecycle"][
            "natural_device_context_owner_count"], 1)
        self.assertEqual(_arm.context_calls, 1)
        self.assertEqual(_arm.owner_calls, {"relation": 1, "triangle": 1})
        self.assertIs(_arm.relation_validate_expected_rows, False)
        self.assertIsInstance(
            _arm.host_inputs["relation"], bulk_input.RelationBulkHostInputs)
        self.assertIsInstance(
            _arm.host_inputs["triangle"], bulk_input.TriangleBulkHostInputs)
        self.assertEqual(result["lifecycle"]["execute_call_count"], 2)
        self.assertEqual(result["lifecycle"]["warmup_execute_call_count"], 0)
        self.assertEqual(
            result["phase_times_absolute"]["phase_order"],
            list(pilot.REQUIRED_PHASES))
        for row in result["phase_times_absolute"]["phases"].values():
            self.assertEqual(row["duration_ns"], 50)
        self.assertTrue(result["applications"]["relation"][
            "exact_oracle_passed"])
        self.assertTrue(result["applications"]["triangle"][
            "exact_oracle_passed"])
        self.assertEqual(
            result["status"],
            "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
            "TWO_APPLICATION_PILOT")
        self.assertEqual(
            result["schema"], "rtdl.goal5809.pyoptix_two_app_pilot.v2")
        self.assertFalse(result["scope"]["paper_evidence"])
        self.assertEqual(result["scope"]["direct_arm_count"], 0)
        self.assertFalse(result["scope"]["direct_arm_present"])
        self.assertFalse(result["scope"]["host_language_control_present"])
        self.assertFalse(result["scope"]["design_attribution_authorized"])
        self.assertEqual(result["direct_arm_count"], 0)
        self.assertFalse(result["direct_arm_present"])
        self.assertFalse(result["host_language_control_present"])
        self.assertFalse(result["design_attribution_authorized"])
        self.assertFalse(result["scope"]["ratio_computation_authorized"])
        self.assertEqual(result["registered_performance_timing_count"], 0)
        self.assertTrue(result["execution_identity"][
            "pyoptix_loaded_identity_verified"])

    def test_oracle_failure_still_closes_both_loaded_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events: list[str] = []
            arm = _Arm(events, wrong_task="triangle")
            args = argparse.Namespace(
                target_manifest=root / "target.json",
                expected_target_manifest_sha256="a" * 64,
                execution_identity_manifest=root / "execution_identity.json",
                expected_execution_identity_manifest_sha256="b" * 64,
                first_app="triangle",
            )
            with mock.patch.object(
                    pilot, "_admit_target",
                    return_value=_admitted(root)), mock.patch.object(
                    pilot, "_preload_runtime",
                    return_value=(
                        _Workloads, arm,
                        _Baseline(),
                        {"status": "PASS__SYNTHETIC_PRELOAD"}, bulk_input)), \
                    mock.patch.object(
                        pilot, "admit_execution_identity",
                        return_value={
                            "manifest_file_sha256": "b" * 64,
                            "execution_identity_sha256": "c" * 64,
                            "file_count": 27,
                            "files_rehashed": True,
                            "runtime_environment_admission": {
                                "environment_identity_sha256": "7" * 64,
                            },
                        }):
                with self.assertRaisesRegex(
                        RuntimeError, "triangle PyOptiX exact oracle mismatch"):
                    pilot._run(args, clock=_Clock())
        self.assertEqual(events, [
            "load:relation", "load:triangle",
            "context.create", "context.cache:False",
            "prepare:triangle", "execute:triangle",
            "close:relation", "close:triangle",
        ])

    def test_wrong_relation_rows_fail_at_single_worker_oracle_and_close(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events: list[str] = []
            arm = _Arm(events, wrong_task="relation")
            args = argparse.Namespace(
                target_manifest=root / "target.json",
                expected_target_manifest_sha256="a" * 64,
                execution_identity_manifest=root / "execution_identity.json",
                expected_execution_identity_manifest_sha256="b" * 64,
                first_app="relation",
            )
            with mock.patch.object(
                    pilot, "_admit_target",
                    return_value=_admitted(root)), mock.patch.object(
                    pilot, "_preload_runtime",
                    return_value=(
                        _Workloads, arm, _Baseline(),
                        {"status": "PASS__SYNTHETIC_PRELOAD"}, bulk_input)), \
                    mock.patch.object(
                        pilot, "admit_execution_identity",
                        return_value={
                            "manifest_file_sha256": "b" * 64,
                            "execution_identity_sha256": "c" * 64,
                            "file_count": 27,
                            "files_rehashed": True,
                            "runtime_environment_admission": {
                                "environment_identity_sha256": "7" * 64,
                            },
                        }):
                with self.assertRaisesRegex(
                        RuntimeError,
                        "relation PyOptiX exact oracle mismatch"):
                    pilot._run(args, clock=_Clock())
        self.assertIs(arm.relation_validate_expected_rows, False)
        self.assertEqual(events, [
            "load:relation", "load:triangle",
            "context.create", "context.cache:False",
            "prepare:relation", "execute:relation",
            "close:triangle", "close:relation",
        ])

    def test_source_uses_natural_adapter_and_forbids_worker_ratio(self) -> None:
        text = Path(pilot.__file__).read_text(encoding="utf-8")
        self.assertEqual(text.count("arm.PyOptixScalarAdapter("), 1)
        self.assertNotIn("adapter.prepare()", text)
        self.assertEqual(text.count("arm._make_validation_off_context("), 1)
        self.assertNotIn("open_runtime_session", text)
        self.assertNotIn("bind_provider", text)
        self.assertIn('"ratio_computation_authorized": False', text)
        self.assertIn('"registered_performance_timing_count": 0', text)
        self.assertNotIn('"first_app_prepare_execute"', text)
        self.assertNotIn('"second_app_prepare_execute"', text)
        self.assertEqual(text.count("validate_expected_rows=False"), 1)
        parameter = inspect.signature(
            real_arm.DeferredRelationPrepared.__init__).parameters[
                "validate_expected_rows"]
        self.assertIs(parameter.default, True)


if __name__ == "__main__":
    unittest.main()
