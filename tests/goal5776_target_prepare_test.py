from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from goal5776_real_scale_formal_contract import schedule, statistical_rows
import goal5776_target_prepare as prepare_module
from goal5776_target_prepare import _validate_authority


ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "scripts/goal5776_target_prepare.py"
BUILDER = ROOT / "scripts/goal5776_build_pre_pod_bundle.py"
FUNCTIONAL = ROOT / "scripts/goal5776_target_real_scale_functional_prepare.py"
REAL_EXECUTION_SCRIPTS = tuple(
    ROOT / "scripts" / name for name in (
        "goal5776_target_prepare.py",
        "goal5776_target_real_scale_functional_prepare.py",
        "goal5776_real_scale_formal_controller.py",
        "goal5776_real_scale_formal_worker.py",
        "goal5776_evaluate_real_scale_v2_v4.py",
        "goal5776_recount_real_scale_v2_v4_raw.py",
        "goal5776_close_formal_result.py",
        "goal5776_build_formal_result_evidence.py",
    )
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _authority():
    body = {
        "schema": "rtdl.goal5776.owner_create_only_prepare_authority.v2",
        "bundle_sha256": "a" * 64,
        "source_archive_sha256": "b" * 64,
        "data_archive_sha256": "c" * 64,
        "expected_value_statement_sha256": "e" * 64,
        "required_gpu_name": "GPU",
        "required_gpu_uuid": "uuid",
        "required_driver_version": "driver",
        "required_compute_capability": "89",
        "required_cuda_toolkit": "12.8",
        "required_optix_sdk": "9.0.0",
        "required_python_executable_sha256": "d" * 64,
        "required_python_version": "3.12.3",
        "required_numba_version": "0.65.1",
        "required_numpy_version": "2.4.4",
        "required_cupy_version": "14.0.1",
        "required_scipy_version": "1.16.1",
        "owner_authorized_create_only_prepare": True,
        "formal_worker_allowed": False,
        "registered_formal_timing_allowed": False,
    }
    return {**body, "authority_sha256": _digest(body)}


class Goal5776TargetPrepareTest(unittest.TestCase):
    PYTHON_IDENTITY = {
        "python_executable_sha256": "d" * 64,
        "python": "3.12.3", "numba": "0.65.1", "numpy": "2.4.4",
        "cupy": "14.0.1", "scipy": "1.16.1",
    }
    def test_contract_shape_is_exact(self):
        self.assertEqual(len(schedule()), 464)
        self.assertEqual(len(statistical_rows()), 34)

    def test_builder_and_target_prepare_require_same_bundle_version(self):
        builder = BUILDER.read_text(encoding="utf-8")
        prepare = PREPARE.read_text(encoding="utf-8")
        self.assertIn('"goal": 5776, "bundle_version": 9', builder)
        self.assertIn('manifest.get("bundle_version") != 9', prepare)

    def test_prepare_process_cannot_write_bytecode_after_source_seal(self):
        prepare = PREPARE.read_text(encoding="utf-8")
        disable = prepare.index("sys.dont_write_bytecode = True")
        seal = prepare.index("_seal_read_only(source)", disable)
        post_seal_import = prepare.index(
            "from goal5776_real_scale_formal_contract import contract_sha256",
            seal,
        )
        self.assertLess(disable, seal)
        self.assertLess(seal, post_seal_import)

    def test_prepare_authority_accepts_exact_and_rejects_extra_field(self):
        authority = _authority()
        _validate_authority(
            authority, bundle_sha="a" * 64, source_sha="b" * 64,
            data_sha="c" * 64, expected_value_statement_sha="e" * 64,
            gpu=("GPU", "uuid", "driver", "8.9"), cc="89",
            python_identity=self.PYTHON_IDENTITY)
        bad = dict(authority)
        bad["unexpected"] = True
        body = dict(bad)
        body.pop("authority_sha256")
        bad["authority_sha256"] = _digest(body)
        with self.assertRaisesRegex(PermissionError, "fields are not exact"):
            _validate_authority(
                bad, bundle_sha="a" * 64, source_sha="b" * 64,
                data_sha="c" * 64, expected_value_statement_sha="e" * 64,
                gpu=("GPU", "uuid", "driver", "8.9"), cc="89",
                python_identity=self.PYTHON_IDENTITY)

    def test_prepare_authority_rejects_partner_version_drift(self):
        authority = _authority()
        drifted = dict(self.PYTHON_IDENTITY)
        drifted["cupy"] = "14.0.2"
        with self.assertRaisesRegex(PermissionError, "required_cupy_version"):
            _validate_authority(
                authority, bundle_sha="a" * 64, source_sha="b" * 64,
                data_sha="c" * 64, expected_value_statement_sha="e" * 64,
                gpu=("GPU", "uuid", "driver", "8.9"), cc="89",
                python_identity=drifted)

    def test_prepare_phase_timeout_is_terminal_and_logged(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "phase.log"
            with mock.patch.object(
                prepare_module.subprocess, "run",
                side_effect=prepare_module.subprocess.TimeoutExpired(
                    cmd=["phase"], timeout=19, output="partial"),
            ):
                with self.assertRaisesRegex(RuntimeError, "19 seconds terminally"):
                    prepare_module._run(
                        ["phase"], cwd=Path(directory), env={}, log=log,
                        timeout_seconds=19)
            self.assertEqual(log.read_text(encoding="utf-8"), "partial")

    def test_prepare_is_functional_only_and_requires_second_authority(self):
        prepare = PREPARE.read_text(encoding="utf-8")
        functional = FUNCTIONAL.read_text(encoding="utf-8")
        for script in REAL_EXECUTION_SCRIPTS:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        self.assertIn('"formal_worker_count": 0', prepare)
        self.assertIn('"registered_formal_timing_count": 0', prepare)
        self.assertIn('"formal_requires_second_exact_owner_authority": True', prepare)
        self.assertIn("_seal_read_only(cache)", prepare)
        self.assertIn("_seal_read_only(functional_root)", prepare)
        self.assertIn("timeout_seconds=7_200", prepare)
        self.assertIn("prepare command exceeded", prepare)
        for field in (
            '"source_root"', '"execution_source_path"', '"data_archive_path"',
            '"data_root"', '"data_manifest_path"',
            '"data_manifest_sha256"', '"rtdbscan_evidence_path"',
        ):
            self.assertIn(field, prepare)
        self.assertIn('"formal_performance_result_created": False', functional)
        self.assertIn('functional.get("functional_trial_count") != 126', prepare)


if __name__ == "__main__":
    unittest.main()
