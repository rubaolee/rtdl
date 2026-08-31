from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import sys


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Goal5776FormalControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = _load(
            "goal5776_controller_test_contract",
            "scripts/goal5776_real_scale_formal_contract.py",
        )
        cls.controller = _load(
            "goal5776_controller_test_module",
            "scripts/goal5776_real_scale_formal_controller.py",
        )

    def test_authority_rejects_any_identity_mismatch_before_worker(self):
        c = self.contract
        runtime = {
            key: value for key, value in {
                "bundle_sha256": "1" * 64,
                "execution_source_sha256": "2" * 64,
                "data_archive_sha256": "9" * 64,
                "rtdbscan_evidence_sha256": "0" * 64,
                "native_library_sha256": "3" * 64,
                "target_identity_sha256": "4" * 64,
                "prepared_identity_sha256": "a" * 64,
                "plan_sha256": "5" * 64,
                "formal_identity_sha256": "6" * 64,
                "leaf_cache_manifest_sha256": "7" * 64,
                "runtime_budget_sha256": "c" * 64,
                "expected_value_statement_sha256": "d" * 64,
                "formal_contract_sha256": c.contract_sha256(),
            }.items()
        }
        runtime["conservative_budget_seconds"] = 123.0
        body = {
            "schema": "rtdl.goal5776.owner_formal_authority.v2",
            **{key: value for key, value in runtime.items()
               if key != "conservative_budget_seconds"},
            "owner_confirmed_conservative_budget_seconds": 123.0,
            "expected_worker_count": len(c.schedule()),
            "expected_independent_row_count": len(c.statistical_rows()),
            "owner_authorized_exactly_once": True,
            "repair_retry_resume_replacement_allowed": False,
            "runtime_sha256": "b" * 64,
        }
        body["authority_sha256"] = self.controller._digest(body)
        bad = dict(body)
        bad["native_library_sha256"] = "8" * 64
        bad_body = dict(bad)
        bad_body.pop("authority_sha256")
        bad["authority_sha256"] = self.controller._digest(bad_body)
        with self.assertRaisesRegex(PermissionError, "authority/runtime mismatch"):
            self.controller._validate_authority(
                bad, runtime, runtime_sha256="b" * 64)

    def test_authority_cannot_omit_expected_value_statement(self):
        source = (ROOT / "scripts/goal5776_real_scale_formal_controller.py").read_text(
            encoding="utf-8")
        self.assertIn('"expected_value_statement_sha256"', source)
        self.assertIn('owner_formal_authority.v2', source)

    def test_create_only_output_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "existing"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                self.controller.run(
                    runtime_path=root / "missing_runtime.json",
                    plan_path=root / "missing_plan.json",
                    authorization_path=root / "missing_authority.json",
                    output_root=output,
                )

    def test_worker_timeout_is_frozen_and_terminal(self):
        process = mock.Mock(pid=1717)
        process.wait.side_effect = [
            self.controller.subprocess.TimeoutExpired(
                cmd=["python", "worker.py"], timeout=1_800),
            0,
        ]
        with mock.patch.object(
            self.controller.subprocess, "Popen", return_value=process,
        ) as launched, mock.patch.object(
            self.controller.os, "name", "posix",
        ), mock.patch.object(
            self.controller.os, "killpg", create=True,
        ) as killed, mock.patch.object(
            self.controller.signal, "SIGKILL", 9, create=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "1800-second limit terminally"):
                self.controller._run_worker(
                    ["python", "worker.py"], worker_environment={}, worker_index=17)
        launched.assert_called_once()
        self.assertTrue(launched.call_args.kwargs["start_new_session"])
        killed.assert_called_once_with(1717, 9)
        self.assertEqual(process.wait.call_args_list[0].kwargs["timeout"], 1_800)

    def test_controller_preserves_admitted_venv_entrypoint_for_workers(self):
        source = (ROOT / "scripts/goal5776_real_scale_formal_controller.py").read_text(
            encoding="utf-8")
        configured = Path("admitted") / "venv" / "bin" / "python"
        expected = Path.cwd() / configured
        self.assertEqual(
            self.controller._preserve_python_entrypoint(configured), expected)
        self.assertIn(
            'worker_python = _validate_worker_python_environment(', source)
        self.assertNotIn(
            'runtime["python_executable"])).resolve()', source)
        self.assertIn('worker_python, str(worker), "--runtime"', source)
        self.assertNotIn(
            'sys.executable, str(worker), "--runtime"', source)
        runtime = {
            "python_executable": str(configured),
            "python_version": "3.12.3",
            "numba_version": "0.65.1",
            "numpy_version": "2.2.6",
            "cupy_version": "14.0.1",
            "scipy_version": "1.16.1",
        }
        observed = {
            **{key: value for key, value in runtime.items()
               if key != "python_executable"},
            "python_executable": str(expected),
        }
        with mock.patch.object(
            self.controller.subprocess, "run",
            return_value=mock.Mock(stdout=json.dumps(observed)),
        ) as probe:
            selected = self.controller._validate_worker_python_environment(
                runtime, {"FROZEN": "1"})
        self.assertEqual(selected, str(expected))
        self.assertEqual(probe.call_args.args[0][0], str(expected))
        self.assertEqual(probe.call_args.kwargs["env"], {"FROZEN": "1"})
        drift = dict(observed, numba_version="0.0")
        with mock.patch.object(
            self.controller.subprocess, "run",
            return_value=mock.Mock(stdout=json.dumps(drift)),
        ), self.assertRaisesRegex(PermissionError, "environment drifted"):
            self.controller._validate_worker_python_environment(runtime, {})

    def test_plan_bytes_and_runtime_identity_are_both_enforced(self):
        c = self.contract
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = {
                "schema": "rtdl.goal5776.real_scale_plan.v1",
                "bundle_sha256": "1" * 64,
                "data_archive_sha256": "9" * 64,
                "prepared_identity_sha256": "2" * 64,
                "target_identity_sha256": "3" * 64,
                "formal_identity_sha256": "4" * 64,
                "runtime_budget_sha256": "6" * 64,
                "expected_value_statement_sha256": "7" * 64,
                "conservative_budget_seconds": 123.0,
                "formal_sources": {},
                "formal_worker_count": len(c.schedule()),
                "independent_row_count": len(c.statistical_rows()),
                "v3_required_or_executed": False,
                "formal_worker_executed": False,
                "registered_formal_timing_created": False,
                "formal_requires_second_exact_owner_authority": True,
            }
            path = root / "PLAN.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            runtime = {
                "bundle_sha256": "1" * 64,
                "data_archive_sha256": "9" * 64,
                "prepared_identity_sha256": "2" * 64,
                "target_identity_sha256": "3" * 64,
                "formal_identity_sha256": "4" * 64,
                "runtime_budget_sha256": "6" * 64,
                "expected_value_statement_sha256": "7" * 64,
                "conservative_budget_seconds": 123.0,
                "plan_sha256": self.controller._sha(path),
            }
            self.controller._validate_plan(path, runtime)
            runtime["plan_sha256"] = "5" * 64
            with self.assertRaisesRegex(PermissionError, "plan bytes are absent"):
                self.controller._validate_plan(path, runtime)


if __name__ == "__main__":
    unittest.main()
