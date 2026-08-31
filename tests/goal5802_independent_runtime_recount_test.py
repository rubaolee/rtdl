from __future__ import annotations

import hashlib
import json
import os
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experiments.goal5802_premeasurement.independent_recount import (
    OFFLINE_PYOPTIX_PIP_POLICY,
    OFFLINE_PYOPTIX_VALIDATION_BOUNDARY,
    PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES,
    PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256,
    PYOPTIX_HISTORICAL_HEADERS_ROOT,
    PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT,
    PYOPTIX_HISTORICAL_SOURCE_SHA256,
    PYOPTIX_REQUIRED_DISTRIBUTIONS,
    _digest,
    _independent_combined_venv_members,
    _independent_controlled_python_command,
    _validate_combined_runtime_independently,
    _validate_current_offline_pyoptix_envelope_independently,
    _validate_current_pyoptix_materialization_envelope_independently,
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(value) + b"\n")


def _file_row(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path), "path_kind": "REGULAR_FILE",
        "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
    }


class Goal5802IndependentRuntimeRecountTest(unittest.TestCase):
    @staticmethod
    def offline_receipt() -> dict[str, object]:
        body: dict[str, object] = {
            "schema": (
                "rtdl.goal5802.offline_pyoptix_clean_install_receipt.v1"),
            "status": "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED",
            "plan_sha256": "1" * 64,
            "specialization_sha256": "2" * 64,
            "plan_file_sha256": "3" * 64,
            "wheelhouse_manifest_sha256": "4" * 64,
            "wheel_set_sha256": "5" * 64,
            "required_distributions": dict(PYOPTIX_REQUIRED_DISTRIBUTIONS),
            "generic_combined_runtime_receipt": {},
            "generic_combined_runtime_receipt_sha256": "6" * 64,
            "installed_package_snapshot": {},
            "installed_package_snapshot_sha256": "7" * 64,
            "generic_input_tree_sha256": "8" * 64,
            "generic_commands_sha256": "9" * 64,
            "generic_venv_member_count": 1,
            "generic_venv_member_tree_sha256": "a" * 64,
            "generic_base_python_site_boundary": {},
            "install_command": [],
            "provenance_files": [],
            "provenance_tree_sha256": "b" * 64,
            "pip_policy": dict(OFFLINE_PYOPTIX_PIP_POLICY),
            "validation_boundary": dict(OFFLINE_PYOPTIX_VALIDATION_BOUNDARY),
            "create_only": True,
        }
        return {**body, "receipt_sha256": _digest(body)}

    @staticmethod
    def materialization_receipt() -> dict[str, object]:
        body: dict[str, object] = {
            "schema": (
                "rtdl.goal5802."
                "pyoptix_wheel_build_materialization_receipt.v1"),
            "status": (
                "PASS__HISTORICAL_BUILD_PRESERVED__EXACT_HEADERS_MATERIALIZED"),
            "original_build_receipt": {},
            "headers_bundle": {},
            "git_tool": {},
            "frozen_historical_receipt_authority": {
                "bytes": PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES,
                "sha256": PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256,
                "source_projection_file_count": (
                    PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT),
                "source_projection_sha256": (
                    PYOPTIX_HISTORICAL_SOURCE_SHA256),
                "historical_headers_root": PYOPTIX_HISTORICAL_HEADERS_ROOT,
            },
            "historical_build_projection": {},
            "materialized_headers": {},
            "pyoptix_wheel": {},
            "claim_boundaries": {
                "historical_build_path_rewritten": False,
                "historical_build_reexecuted": False,
                "target_header_materialization_is_not_a_rebuild": True,
                "network_access_required_on_target": False,
                "performance_claim_authorized": False,
                "execution_authority_consumed": False,
            },
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
        }
        return {**body, "receipt_sha256": _digest(body)}

    def test_current_receipt_envelopes_reject_resealed_scalar_aliases(
            self) -> None:
        offline = self.offline_receipt()
        self.assertEqual(
            _validate_current_offline_pyoptix_envelope_independently(offline),
            offline)
        for key, expected in OFFLINE_PYOPTIX_VALIDATION_BOUNDARY.items():
            hostile = copy.deepcopy(offline)
            hostile["validation_boundary"][key] = (
                False if type(expected) is int else
                0 if expected is False else 1)
            hostile_body = dict(hostile)
            hostile_body.pop("receipt_sha256")
            hostile["receipt_sha256"] = _digest(hostile_body)
            with self.assertRaises(RuntimeError, msg=key):
                _validate_current_offline_pyoptix_envelope_independently(
                    hostile)
        weakened = copy.deepcopy(offline)
        weakened["pip_policy"]["no_compile"] = False
        weakened_body = dict(weakened)
        weakened_body.pop("receipt_sha256")
        weakened["receipt_sha256"] = _digest(weakened_body)
        with self.assertRaises(RuntimeError):
            _validate_current_offline_pyoptix_envelope_independently(weakened)
        rollback = copy.deepcopy(offline)
        rollback["schema"] = "rtdl.goal5800.pyoptix_clean_install_receipt.v1"
        rollback_body = dict(rollback)
        rollback_body.pop("receipt_sha256")
        rollback["receipt_sha256"] = _digest(rollback_body)
        with self.assertRaises(RuntimeError):
            _validate_current_offline_pyoptix_envelope_independently(rollback)

        materialization = self.materialization_receipt()
        self.assertEqual(
            _validate_current_pyoptix_materialization_envelope_independently(
                materialization), materialization)
        for key in (
                "formal_worker_count", "registered_performance_timing_count",
                "gpu_kernel_launch_count", "clock_read_count"):
            hostile = copy.deepcopy(materialization)
            hostile[key] = False
            hostile_body = dict(hostile)
            hostile_body.pop("receipt_sha256")
            hostile["receipt_sha256"] = _digest(hostile_body)
            with self.assertRaises(RuntimeError, msg=key):
                _validate_current_pyoptix_materialization_envelope_independently(
                    hostile)
        hostile = copy.deepcopy(materialization)
        hostile["claim_boundaries"]["execution_authority_consumed"] = 0
        hostile_body = dict(hostile)
        hostile_body.pop("receipt_sha256")
        hostile["receipt_sha256"] = _digest(hostile_body)
        with self.assertRaises(RuntimeError):
            _validate_current_pyoptix_materialization_envelope_independently(
                hostile)

    def test_controlled_command_executes_module_without_pth(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "source"
            site = root / "site-packages"
            package = site / "rtdsl"
            optix = site / "optix"
            source.mkdir()
            package.mkdir(parents=True)
            optix.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            initializer = optix / "__init__.py"
            initializer.write_text("", encoding="utf-8")
            marker = root / "pth-executed"
            (site / "hostile.pth").write_text(
                "import pathlib;pathlib.Path(" + repr(str(marker))
                + ").write_text('BAD',encoding='utf-8')\n",
                encoding="utf-8")
            (source / "probe.py").write_text(
                "import sys\n"
                "assert 'site' not in sys.modules\n"
                "print('PASS')\n",
                encoding="utf-8")
            runtime = {
                "files": {
                    "clean_python": {"path": sys.executable},
                    "pyoptix_initializer": {"path": str(initializer)},
                },
                "directories": {"rtdsl_package": {"path": str(package)}},
            }
            command = _independent_controlled_python_command(
                runtime, import_root=source, module="probe")
            self.assertEqual(command[1:6], ["-I", "-S", "-B", "-P", "-c"])
            completed = subprocess.run(
                command, cwd=root, check=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stdout.strip(), b"PASS")
            self.assertFalse(marker.exists())

    def test_complete_venv_recount_rejects_extra_member(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            combined = Path(temporary).resolve() / "combined"
            venv = combined / "venv"
            python = (venv / "Scripts/python.exe" if os.name == "nt"
                      else venv / "bin/python")
            site = (venv / "Lib/site-packages" if os.name == "nt"
                    else venv / "lib/python3.12/site-packages")
            rtdsl = site / "rtdsl"
            optix = site / "optix"
            for path, payload in (
                    (python, b"python"),
                    (rtdsl / "__init__.py", b"rtdsl"),
                    (rtdsl / "v4_rtdlexe.py", b"rtdlexe"),
                    (optix / "__init__.py", b"optix"),
                    (optix / "_optix.so", b"extension")):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)

            inputs = combined / "inputs"
            app_data = combined / "virtualenv_app_data"
            command_receipts = combined / "command_receipts"
            inputs.mkdir()
            app_data.mkdir()
            command_receipts.mkdir()
            app_package = app_data / "image/demo/demo"
            app_package.mkdir(parents=True)
            (app_package / "__init__.py").write_bytes(b"# app-data\n")
            (app_data / "image/demo/demo.lock").write_bytes(b"")
            runner = inputs / "runner.py"
            runner.write_bytes(b"# synthetic controlled runner\n")
            common = ["python", "-I", "-S", "-B", "-P"]
            commands = [
                {"label": "01_create", "argv": [*common, "-c", "pass"]},
                {"label": "02_install", "argv": [
                    *common, "-c",
                    "import runpy;runpy.run_module('pip',run_name='__main__')",
                    "--isolated", "install", "--no-index", "--no-deps",
                    "--no-cache-dir", "--no-compile",
                    "--disable-pip-version-check", "--target", str(site),
                ]},
                {"label": "03_check", "argv": [*common, "-c", "pass"]},
                {"label": "04_snapshot", "argv": [*common, "-c", "pass"]},
            ]
            policy = {
                "pip_bytecode_compilation_during_install_forbidden": True,
                "site_initialization_disabled_for_every_build_command": True,
                "pth_execution_during_build_forbidden": True,
            }
            plan_body = {
                "schema": "rtdl.goal5802.combined_runtime_plan.v1",
                "status": (
                    "FROZEN_LOCAL_INTEGRITY_PLAN__"
                    "EXTERNAL_INPUT_AUTHORITY_REQUIRED"),
                "output_directory": str(combined),
                "commands": commands,
                "pip_invocation_policy": policy,
                "authority_boundary": {},
                "virtualenv_bootstrap": {
                    "saved_root": "inputs/bootstrap", "files": []},
                "wheels": [],
                "runner_source": {
                    "saved_path": "inputs/runner.py",
                    "bytes": runner.stat().st_size,
                    "sha256": hashlib.sha256(
                        runner.read_bytes()).hexdigest(),
                },
            }
            plan = {**plan_body, "plan_sha256": _digest(plan_body)}
            _write_json(combined / "plan.json", plan)
            snapshot_body = {
                "schema": (
                    "rtdl.goal5802.combined_runtime_package_snapshot.v1"),
                "status": "PASS__COMPLETE_INSTALLED_DISTRIBUTION_SNAPSHOT",
                "venv_root": str(venv),
                "site_packages": str(site),
                "site_module_imported": False,
                "python_executable": {},
                "package_count": 0,
                "packages": [],
            }
            snapshot = {
                **snapshot_body, "snapshot_sha256": _digest(snapshot_body)}
            _write_json(combined / "installed_packages.json", snapshot)
            members = _independent_combined_venv_members(combined)
            input_rows = [{
                "path": "inputs/runner.py", "bytes": runner.stat().st_size,
                "sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
            }]
            app_data_rows = []
            for path in sorted(app_data.rglob("*")):
                if path.is_file():
                    payload = path.read_bytes()
                    app_data_rows.append({
                        "path": path.relative_to(combined).as_posix(),
                        "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    })
            self.assertNotEqual(
                app_data_rows,
                sorted(app_data_rows, key=lambda row: str(row["path"])))
            plan_path = combined / "plan.json"
            snapshot_path = combined / "installed_packages.json"
            evidence_rows = [{
                "path": "plan.json", "bytes": plan_path.stat().st_size,
                "sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
            }, {
                "path": "installed_packages.json",
                "bytes": snapshot_path.stat().st_size,
                "sha256": hashlib.sha256(
                    snapshot_path.read_bytes()).hexdigest(),
            }]
            receipt_body = {
                "schema": "rtdl.goal5802.combined_runtime_build_receipt.v1",
                "status": "PASS__OFFLINE_CREATE_ONLY_COMBINED_RUNTIME_BUILT",
                "plan_sha256": plan["plan_sha256"],
                "plan_file_sha256": hashlib.sha256(
                    (combined / "plan.json").read_bytes()).hexdigest(),
                "input_file_count": 1,
                "input_tree_sha256": _digest(input_rows),
                "input_files": input_rows,
                "virtualenv_app_data_file_count": len(app_data_rows),
                "virtualenv_app_data_tree_sha256": _digest(app_data_rows),
                "virtualenv_app_data_files": app_data_rows,
                "command_count": 4,
                "commands_sha256": _digest(commands),
                "installed_package_snapshot_sha256": snapshot[
                    "snapshot_sha256"],
                "venv_member_count": len(members),
                "venv_member_tree_sha256": _digest(members),
                "venv_members": members,
                "expected_explicit_distributions": {},
                "unexpected_installed_distribution_count": 0,
                "evidence_files": evidence_rows,
                "pip_invocation_policy": policy,
                "authority_boundary": {}, "base_python_site_boundary": {},
                "execution_scope": {
                    "formal_worker_count": 0,
                    "registered_performance_timing_count": 0,
                    "gpu_kernel_launch_count": 0, "clock_read_count": 0,
                    "measured_arm_import_count": 0,
                    "execution_authority_consumed": False,
                },
                "create_only": True,
            }
            receipt = {
                **receipt_body, "receipt_sha256": _digest(receipt_body)}
            receipt_path = combined / "combined_runtime_receipt.json"
            _write_json(receipt_path, receipt)
            runtime = {
                "files": {
                    "combined_runtime_receipt": _file_row(receipt_path),
                    "clean_python": _file_row(python),
                    "rtdsl_init": _file_row(rtdsl / "__init__.py"),
                    "rtdlexe_module": _file_row(rtdsl / "v4_rtdlexe.py"),
                    "pyoptix_initializer": _file_row(optix / "__init__.py"),
                    "pyoptix_extension": _file_row(optix / "_optix.so"),
                },
                "directories": {"rtdsl_package": {"path": str(rtdsl)}},
            }
            observed = _validate_combined_runtime_independently(runtime)
            self.assertEqual(
                observed["venv_member_tree_sha256"], _digest(members))

            extra_app_data = app_data / "post-receipt-extra"
            extra_app_data.write_bytes(b"drift")
            with self.assertRaisesRegex(
                    RuntimeError, "virtualenv app-data"):
                _validate_combined_runtime_independently(runtime)
            extra_app_data.unlink()

            original_plan_bytes = (combined / "plan.json").read_bytes()
            original_receipt_bytes = receipt_path.read_bytes()
            forged_plan = json.loads(original_plan_bytes)
            forged_plan["commands"][1]["argv"].remove("--no-compile")
            forged_plan_body = dict(forged_plan)
            forged_plan_body.pop("plan_sha256")
            forged_plan["plan_sha256"] = _digest(forged_plan_body)
            _write_json(combined / "plan.json", forged_plan)
            forged_receipt = json.loads(original_receipt_bytes)
            forged_receipt["plan_sha256"] = forged_plan["plan_sha256"]
            forged_receipt["plan_file_sha256"] = hashlib.sha256(
                (combined / "plan.json").read_bytes()).hexdigest()
            forged_receipt["commands_sha256"] = _digest(
                forged_plan["commands"])
            forged_receipt_body = dict(forged_receipt)
            forged_receipt_body.pop("receipt_sha256")
            forged_receipt["receipt_sha256"] = _digest(forged_receipt_body)
            _write_json(receipt_path, forged_receipt)
            runtime["files"]["combined_runtime_receipt"] = _file_row(
                receipt_path)
            with self.assertRaisesRegex(
                    RuntimeError, "plan/policy|no-bytecode install policy"):
                _validate_combined_runtime_independently(runtime)

            (combined / "plan.json").write_bytes(original_plan_bytes)
            receipt_path.write_bytes(original_receipt_bytes)
            runtime["files"]["combined_runtime_receipt"] = _file_row(
                receipt_path)
            (site / "post-receipt-extra.py").write_bytes(b"drift")
            with self.assertRaisesRegex(RuntimeError, "complete member tree"):
                _validate_combined_runtime_independently(runtime)


if __name__ == "__main__":
    unittest.main()
