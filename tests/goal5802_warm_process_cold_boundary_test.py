"""Host-only tests for Goal5802's warm-process deployment-cold boundary."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

from experiments.goal5802_premeasurement.controller import _execute_one
from experiments.goal5802_premeasurement import pyoptix_scalar_arm
from experiments.goal5802_premeasurement import rtdlexe_arm
from experiments.goal5802_premeasurement.python_worker import (
    run_adapter,
    validate_warm_process_import_source_boundary,
)


ROOT = Path(__file__).resolve().parents[1]


class _Clock:
    def __init__(self, events: list[str]):
        self.events = events
        self.value = 0

    def __call__(self) -> int:
        self.events.append("clock")
        self.value += 10
        return self.value


class _BoundaryAdapter:
    def __init__(self, events: list[str], forbidden_import: str | None = None):
        self.events = events
        self.forbidden_import = forbidden_import

    def constructor_runtime_preload_receipt(self):
        self.events.append("constructor_evidence")
        return {
            "schema": "rtdl.goal5802.python_runtime_preload.v1",
            "status": "PASS__BEFORE_PRIMARY_CLOCK",
            "runtime_import_inside_primary_timer": False,
        }

    def primary_timer_import_contract(self):
        self.events.append("import_contract")
        return {"required_preloaded_modules": [],
                "forbidden_absent_modules": []}

    def load(self):
        self.events.append("load")
        if self.forbidden_import is not None:
            importlib.import_module(self.forbidden_import)

    def prepare(self):
        self.events.append("prepare")

    def execute(self):
        self.events.append("execute")
        return {"dynamic_input_receipt": {"prepared_input_reused": False}}

    def close(self):
        self.events.append("close")


class Goal5802WarmProcessColdBoundaryTest(unittest.TestCase):
    def test_constructor_evidence_precedes_first_primary_clock(self):
        events: list[str] = []
        result = run_adapter(
            _BoundaryAdapter(events), "DEPLOYMENT_COLD",
            clock=_Clock(events), input_materialization_ns=7,
            process_startup_and_admission_ns=9)
        self.assertLess(events.index("constructor_evidence"),
                        events.index("clock"))
        self.assertLess(events.index("import_contract"), events.index("clock"))
        self.assertEqual(result["primary_estimator_name"],
                         "WARM_PROCESS_DEPLOYMENT_COLD")
        self.assertFalse(result["constructor_evidence_inside_primary_timer"])
        self.assertEqual(
            result["phase_durations_ns"]["process_startup_and_admission"], 9)

    def test_forbidden_new_module_loads_fail_inside_primary_boundary(self):
        parents = {
            "cuda": types.ModuleType("cuda"),
            "cuda.bindings": types.ModuleType("cuda.bindings"),
        }
        parents["cuda"].__path__ = []
        parents["cuda.bindings"].__path__ = []
        saved = {name: sys.modules.get(name) for name in parents}
        sys.modules.update(parents)
        try:
            for target in (
                    "cuda.bindings.nvrtc",
                    "goal5802_arbitrary_lazy_probe",
                    "cupy.__goal5802_forbidden_probe",
                    "numpy.__goal5802_forbidden_probe",
                    "optix.__goal5802_forbidden_probe",
                    "rtdsl.__goal5802_forbidden_probe",
                    "experiments.goal5796_matched.pyoptix_baseline"):
                saved_target = sys.modules.pop(target, None)
                try:
                    with self.subTest(target=target), self.assertRaisesRegex(
                            RuntimeError, "forbidden new module load"):
                        run_adapter(
                            _BoundaryAdapter([], target), "DEPLOYMENT_COLD",
                            clock=_Clock([]), input_materialization_ns=7,
                            process_startup_and_admission_ns=9)
                finally:
                    if saved_target is not None:
                        sys.modules[target] = saved_target
        finally:
            for name, value in saved.items():
                if value is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value

    def test_runtime_preload_failures_are_not_recovered(self):
        with mock.patch.object(
                pyoptix_scalar_arm.importlib, "import_module",
                side_effect=ModuleNotFoundError("hostile PyOptiX absence")):
            with self.assertRaisesRegex(RuntimeError, "preload failed"):
                pyoptix_scalar_arm.preload_pyoptix_runtime()
        with mock.patch.object(
                rtdlexe_arm.importlib, "import_module",
                side_effect=ModuleNotFoundError("hostile RTDL absence")):
            with self.assertRaisesRegex(RuntimeError, "preload failed"):
                rtdlexe_arm.preload_rtdl_runtime()

    def test_source_boundary_rejects_cached_import_escape(self):
        result = validate_warm_process_import_source_boundary()
        self.assertEqual(result["status"], "PASS__SOURCE_ONLY__ZERO_TIMINGS")
        source = (ROOT / "experiments" / "goal5802_premeasurement"
                  / "pyoptix_scalar_arm.py").read_text(encoding="utf-8")
        marker = "    def load(self) -> None:\n"
        self.assertIn(marker, source)
        mutant = source.replace(marker, marker + "        import rtdsl\n", 1)
        with self.assertRaisesRegex(RuntimeError, "warm_process_import"):
            validate_warm_process_import_source_boundary({"pyoptix": mutant})
        baseline = (ROOT / "experiments" / "goal5796_matched"
                    / "pyoptix_baseline.py").read_text(encoding="utf-8")
        baseline_marker = "def make_sbt(groups):\n"
        self.assertIn(baseline_marker, baseline)
        baseline_mutant = baseline.replace(
            baseline_marker, baseline_marker + "    import numpy\n", 1)
        with self.assertRaisesRegex(RuntimeError, "warm_process_import"):
            validate_warm_process_import_source_boundary({
                "baseline": baseline_mutant})

    def test_controller_publishes_all_three_admission_boundaries(self):
        digest_environment = {
            "GOAL5802_FREEZE_FILE_SHA256": "a" * 64,
            "GOAL5802_EXECUTION_AUTHORITY_SHA256": "b" * 64,
            "GOAL5802_RUNTIME_MANIFEST_SHA256": "c" * 64,
            "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256": "d" * 64,
            "GOAL5802_RUNTIME_PREFLIGHT_SHA256": "e" * 64,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        arms = (
            "A_DIRECT_CUDA_OPTIX",
            pyoptix_scalar_arm.ARM,
            rtdlexe_arm.ARM,
        )
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary).resolve()
            for ordinal, arm in enumerate(arms):
                worker = {
                    "status": "PASS", "arm": arm,
                    "worker_id": f"worker-{ordinal}",
                    "task": "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
                    "regime": "DEPLOYMENT_COLD",
                    "freeze_file_sha256": "a" * 64,
                    "execution_authority_sha256": "b" * 64,
                    "runtime_manifest_sha256": "c" * 64,
                    "phase_durations_ns": {
                        "process_startup_and_admission": 17,
                    },
                }
                if arm != "A_DIRECT_CUDA_OPTIX":
                    preload = (
                        {
                            "schema": "rtdl.goal5802.python_runtime_preload.v1",
                            "status": "PASS__BEFORE_PRIMARY_CLOCK",
                            "arm": arm,
                            "runtime_module": (
                                "experiments.goal5796_matched.pyoptix_baseline"),
                            "required_preloaded_modules": [
                                "experiments.goal5796_matched.pyoptix_baseline",
                                "cupy", "numpy", "optix", "optix._optix",
                            ],
                            "forbidden_absent_modules": [
                                "cuda.bindings.nvrtc"],
                            "compiler_only_nvrtc_loaded": False,
                            "prebuilt_ptx_deployment": True,
                            "runtime_import_inside_primary_timer": False,
                        }
                        if arm == pyoptix_scalar_arm.ARM else
                        {
                            "schema": "rtdl.goal5802.python_runtime_preload.v1",
                            "status": "PASS__BEFORE_PRIMARY_CLOCK",
                            "arm": arm,
                            "runtime_module": "rtdsl",
                            "implementation_module": "rtdsl.v4_rtdlexe",
                            "required_preloaded_modules": [
                                "rtdsl", "rtdsl.v4_rtdlexe",
                                "rtdsl.physical_execution_provenance",
                                "atexit",
                                *(["fcntl"] if os.name == "posix" else []),
                            ],
                            "forbidden_absent_modules": [
                                "cuda.bindings.nvrtc",
                                "experiments.goal5796_matched.pyoptix_baseline",
                            ],
                            "public_symbol_identity_match_count": 6,
                            "legacy_rtdsl_v4_loaded": False,
                            "runtime_import_inside_primary_timer": False,
                        })
                    worker.update({
                        "primary_estimator_name":
                            "WARM_PROCESS_DEPLOYMENT_COLD",
                        "new_forbidden_module_load_inside_primary_timer": False,
                        "primary_timer_new_module_load_policy":
                            "REJECT_ALL_NOT_PRELOADED",
                        "constructor_evidence_inside_primary_timer": False,
                        "constructor_runtime_preload_receipt": preload,
                    })
                program = "import json; print(json.dumps(" + repr(worker) + "))"
                row = {
                    "arm": arm, "worker_id": f"worker-{ordinal}",
                    "task": "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
                    "regime": "DEPLOYMENT_COLD",
                }
                receipt = _execute_one(
                    row=row, command=[sys.executable, "-c", program],
                    root=temporary_root, environment={
                        **os.environ, **digest_environment},
                    worker_dir=temporary_root / f"worker-{ordinal}",
                    timeout_seconds=10,
                    receipt_schema=(
                        "rtdl.goal5802.comparative_controller_worker_receipt.v1"),
                )
                self.assertEqual(receipt["status"], "PASS")
                boundary = receipt["comparative_measurement_boundary"]
                self.assertTrue(boundary["boundary_valid"])
                self.assertEqual(boundary["process_startup_and_admission_ns"], 17)
                self.assertEqual(boundary["primary_estimator_name"],
                                 "WARM_PROCESS_DEPLOYMENT_COLD")


if __name__ == "__main__":
    unittest.main()
