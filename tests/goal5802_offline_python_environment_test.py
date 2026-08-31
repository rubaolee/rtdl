"""Hostile tests for the Goal5802 offline Python dependency entry."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts import goal5802_build_combined_runtime_untimed as combined
from scripts import goal5802_build_offline_python_wheelhouse as wheelhouse
from scripts import goal5802_clean_install_pyoptix_offline as installer
from scripts import goal5802_build_target_runtime_manifest as runtime_manifest
from experiments.goal5802_premeasurement.independent_recount import (
    _validate_combined_runtime_root_independently,
    _validate_current_offline_pyoptix_install_independently,
)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def build_wheel(
        path: Path, *, name: str, version: str,
        pth_marker: Path | None = None,
        include_script_interfaces: bool = False) -> None:
    token = name.replace("-", "_")
    dist_info = f"{token}-{version}.dist-info"
    members = {
        f"{token}/__init__.py": f"__version__ = {version!r}\n".encode(),
        f"{dist_info}/METADATA": (
            f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\n"
        ).encode(),
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\nGenerator: goal5802-hostile-test\n"
            "Root-Is-Purelib: true\nTag: py3-none-any\n\n"
        ).encode(),
        f"{dist_info}/top_level.txt": f"{token}\n".encode(),
    }
    if pth_marker is not None:
        members["goal5802_hostile_startup.pth"] = (
            "import pathlib;pathlib.Path("
            f"{str(pth_marker)!r}).write_text('EXECUTED',encoding='utf-8')\n"
        ).encode("utf-8")
    if include_script_interfaces:
        members[f"{dist_info}/entry_points.txt"] = (
            "[console_scripts]\n"
            "goal5802-hostile-cli = pyoptix:main\n"
        ).encode("utf-8")
        members[
            f"{token}-{version}.data/scripts/goal5802_hostile_script"
        ] = b"#!/usr/bin/env python\nraise SystemExit('MUST_NOT_RUN')\n"
    record_name = f"{dist_info}/RECORD"
    rows = []
    for member, payload in members.items():
        encoded = base64.urlsafe_b64encode(
            hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
        rows.append([member, f"sha256={encoded}", str(len(payload))])
    rows.append([record_name, "", ""])
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    members[record_name] = stream.getvalue().encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for directory in (f"{token}/", f"{dist_info}/"):
            info = zipfile.ZipInfo(directory, date_time=(2026, 8, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o40755 << 16
            archive.writestr(info, b"")
        for member, payload in members.items():
            info = zipfile.ZipInfo(member, date_time=(2026, 8, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)


class OfflinePythonEnvironmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        self.pth_marker = self.root / "HOSTILE_PTH_EXECUTED.txt"
        self.paths: dict[str, Path] = {}
        for name, version in wheelhouse.REQUIRED_DISTRIBUTIONS:
            path = self.sources / (
                f"{name.replace('-', '_')}-{version}-py3-none-any.whl")
            build_wheel(
                path, name=name, version=version,
                pth_marker=self.pth_marker if name == "pyoptix" else None,
                include_script_interfaces=name == "pyoptix")
            self.paths[name] = path
        self.bootstrap = self.root / "bootstrap"
        (self.bootstrap / "virtualenv").mkdir(parents=True)
        (self.bootstrap / "virtualenv/__main__.py").write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "import venv\n"
            "app_data = Path(sys.argv[sys.argv.index('--app-data') + 1])\n"
            "app_data.mkdir(parents=True)\n"
            "(app_data / 'stdlib_venv_test_seed.txt').write_text('seed\\n')\n"
            "venv.EnvBuilder(with_pip=True, symlinks=False).create(sys.argv[-1])\n",
            encoding="utf-8")
        for name, version in installer.BOOTSTRAP_DISTRIBUTIONS:
            dist_info = self.bootstrap / (
                f"{name.replace('-', '_')}-{version}.dist-info")
            dist_info.mkdir()
            (dist_info / "METADATA").write_text(
                f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\n",
                encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def specs(self) -> list[str]:
        return [
            f"{name}={self.paths[name]}"
            for name, _ in wheelhouse.REQUIRED_DISTRIBUTIONS
        ]

    def collect(self, name: str = "wheelhouse") -> tuple[Path, dict[str, object]]:
        output = self.root / name
        return output, wheelhouse.collect(output, self.specs())

    def test_collect_is_portable_deterministic_exact_and_create_only(self) -> None:
        first_root, first = self.collect("first")
        second_root, second = self.collect("second")
        self.assertEqual(first, wheelhouse.verify(first_root))
        self.assertEqual(second, wheelhouse.verify(second_root))
        self.assertEqual(first, second)
        self.assertEqual(
            (first_root / "wheelhouse_manifest.json").read_bytes(),
            (second_root / "wheelhouse_manifest.json").read_bytes())
        self.assertEqual(first["wheel_count"], 8)
        self.assertEqual(first["required_distributions"],
                         wheelhouse.REQUIRED_VERSION_MAP)
        self.assertEqual(first["collection_policy"], {
            "explicit_local_wheel_inputs_only": True,
            "implicit_download_allowed": False,
            "network_access_attempt_count": 0,
            "subprocess_invocation_count": 0,
            "package_install_count": 0,
            "wheel_import_or_execution_count": 0,
        })
        with self.assertRaises(FileExistsError):
            wheelhouse.collect(first_root, self.specs())

    def test_missing_duplicate_and_version_mismatch_fail_before_output(self) -> None:
        with self.assertRaises(wheelhouse.OfflineWheelhouseError):
            wheelhouse.collect(self.root / "missing", self.specs()[:-1])
        duplicate = self.specs()[:-1] + [self.specs()[0]]
        with self.assertRaises(wheelhouse.OfflineWheelhouseError):
            wheelhouse.collect(self.root / "duplicate", duplicate)
        wrong = self.root / "wrong_numpy.whl"
        build_wheel(wrong, name="numpy", version="2.4.3")
        mismatch = [
            f"{name}={wrong if name == 'numpy' else self.paths[name]}"
            for name, _ in wheelhouse.REQUIRED_DISTRIBUTIONS
        ]
        with self.assertRaises(wheelhouse.OfflineWheelhouseError):
            wheelhouse.collect(self.root / "version_mismatch", mismatch)
        self.assertFalse((self.root / "missing").exists())
        self.assertFalse((self.root / "duplicate").exists())
        self.assertFalse((self.root / "version_mismatch").exists())

    def test_collected_wheel_drift_and_extra_member_fail_verification(self) -> None:
        output, manifest = self.collect()
        target = output / str(manifest["wheels"][0]["saved_path"])
        target.write_bytes(target.read_bytes() + b"drift")
        with self.assertRaises(wheelhouse.OfflineWheelhouseError):
            wheelhouse.verify(output)

        second, _ = self.collect("extra")
        (second / "unregistered.txt").write_text("not allowed\n", encoding="utf-8")
        with self.assertRaises(wheelhouse.OfflineWheelhouseError):
            wheelhouse.verify(second)

    def test_wheelhouse_copy_uses_one_opened_payload(self) -> None:
        source = self.paths["pyoptix"]
        projection = wheelhouse._wheel_projection(source, 1)
        destination = self.root / "single_open" / source.name
        original = source.read_bytes()

        def vulnerable_two_read_probe(*_args, **_kwargs):
            source.write_bytes(b"MUTATED_AFTER_CHECK")
            raise AssertionError("wheelhouse _copy_exact must not rehash/reopen")

        with mock.patch.object(
                wheelhouse, "_sha_file", side_effect=vulnerable_two_read_probe):
            wheelhouse._copy_exact(source, destination, projection)
        self.assertEqual(destination.read_bytes(), original)

    def test_specialized_plan_has_exact_offline_pip_and_zero_execution(self) -> None:
        manifest_root, _ = self.collect()
        output = self.root / "future_runtime"
        plan = installer.build_plan(
            output=output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)
        self.assertEqual(installer._validate_plan(
            plan, require_live_inputs=True), plan)
        install = plan["commands"][1]["argv"]
        self.assertEqual(
            install[1:6], ["-I", "-S", "-B", "-P", "-c"])
        self.assertEqual(install[7:9], ["--isolated", "install"])
        self.assertIn(
            "runpy.run_module('pip',run_name='__main__')", install[6])
        for command in plan["commands"]:
            self.assertEqual(
                command["argv"][1:5], ["-I", "-S", "-B", "-P"])
        for flag in ("--no-index", "--no-deps", "--no-cache-dir",
                     "--no-compile", "--disable-pip-version-check", "--target"):
            self.assertEqual(install.count(flag), 1)
        self.assertEqual(
            install[install.index("--target") + 1],
            str(output / combined._venv_site_packages_relative(os.name)))
        self.assertNotIn("--prefix", install)
        specialization = plan[installer.SPECIALIZATION_KEY]
        self.assertEqual(specialization["required_distributions"],
                         wheelhouse.REQUIRED_VERSION_MAP)
        self.assertEqual(specialization["validation_boundary"], {
            "installed_measured_runtime_distribution_import_count": 0,
            "pyoptix_import_count": 0,
            "cupy_import_count": 0,
            "device_query_count": 0,
            "gpu_kernel_launch_count": 0,
            "registered_measurement_clock_read_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "execution_authority_consumed": False,
            "self_hash_is_execution_authority": False,
            "caller_must_bind_exact_plan_before_run": True,
        })
        self.assertEqual(specialization["pip_policy"], {
            "python_interpreter_executes_pip_module_without_script_or_shebang": (
                True),
            "pip_loaded_via_runpy_with_site_disabled": True,
            "safe_path_enabled_for_every_build_command": True,
            "isolated": True,
            "no_index": True,
            "no_deps": True,
            "no_cache_dir": True,
            "no_compile": True,
            "exact_venv_site_packages_target": True,
            "prefix_mode_allowed": False,
            "implicit_download_allowed": False,
            "pip_script_or_shebang_invocation_allowed": False,
        })
        script_boundary = specialization["entrypoint_and_script_boundary"]
        self.assertEqual(
            script_boundary["goal5802_runtime_interface"],
            "PYTHON_IMPORTS_ONLY")
        self.assertEqual(
            script_boundary["goal5802_required_console_entry_point_count"], 0)
        self.assertEqual(
            script_boundary["observed_console_entry_point_count"], 1)
        self.assertEqual(
            script_boundary["observed_wheel_data_script_count"], 1)
        self.assertFalse(script_boundary["script_absence_claimed"])

    def test_resealed_network_flag_is_rejected(self) -> None:
        manifest_root, _ = self.collect()
        plan = installer.build_plan(
            output=self.root / "runtime", base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)
        plan["commands"][1]["argv"].insert(
            6, "--index-url=https://host.invalid/simple")
        body = dict(plan)
        body.pop("plan_sha256")
        plan["plan_sha256"] = combined._digest(body)
        with self.assertRaises(installer.OfflinePyOptiXInstallError):
            installer._validate_plan(plan, require_live_inputs=True)

    def test_non_python_base_and_wrong_bootstrap_version_are_rejected(self) -> None:
        manifest_root, _ = self.collect()
        not_python = self.root / "not_python.txt"
        not_python.write_text("not an executable CPython\n", encoding="utf-8")
        with self.assertRaises(installer.OfflinePyOptiXInstallError):
            installer.build_plan(
                output=self.root / "bad_base_runtime", base_python=not_python,
                bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)

        wrong_bootstrap = self.root / "wrong_bootstrap"
        shutil.copytree(self.bootstrap, wrong_bootstrap)
        metadata = wrong_bootstrap / "virtualenv-20.35.4.dist-info/METADATA"
        metadata.write_text(
            "Metadata-Version: 2.1\nName: virtualenv\nVersion: 20.35.3\n\n",
            encoding="utf-8")
        with self.assertRaises(installer.OfflinePyOptiXInstallError):
            installer.build_plan(
                output=self.root / "bad_bootstrap_runtime",
                base_python=Path(sys.executable),
                bootstrap_root=wrong_bootstrap, wheelhouse_root=manifest_root)

    def test_manifest_drift_and_existing_runtime_fail_closed(self) -> None:
        manifest_root, manifest = self.collect()
        output = self.root / "runtime"
        plan = installer.build_plan(
            output=output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)
        plan_path = self.root / "install_plan.json"
        installer.write_plan(plan_path, plan)
        target = manifest_root / str(manifest["wheels"][-1]["saved_path"])
        target.write_bytes(target.read_bytes() + b"drift")
        with self.assertRaises(installer.OfflinePyOptiXInstallError):
            installer._validate_plan(plan, require_live_inputs=True)

        clean_root, _ = self.collect("clean_for_existing")
        existing_output = self.root / "existing_runtime"
        existing_plan = installer.build_plan(
            output=existing_output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=clean_root)
        existing_plan_path = self.root / "existing_plan.json"
        installer.write_plan(existing_plan_path, existing_plan)
        existing_output.mkdir()
        with self.assertRaises(FileExistsError):
            installer.run(existing_plan_path)

    def test_wrong_raw_plan_file_sha_fails_before_output(self) -> None:
        manifest_root, _ = self.collect()
        output = self.root / "sha_bound_runtime"
        plan = installer.build_plan(
            output=output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)
        plan_path = self.root / "sha_bound_plan.json"
        installer.write_plan(plan_path, plan)
        with self.assertRaises(combined.CombinedRuntimeError):
            combined.run_plan(
                plan_path, expected_plan_file_sha256="0" * 64)
        self.assertFalse(output.exists())

    def test_full_create_only_install_and_independent_verify(self) -> None:
        manifest_root, _ = self.collect()
        output = self.root / "installed_runtime"
        plan = installer.build_plan(
            output=output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheelhouse_root=manifest_root)
        plan_path = self.root / "full_install_plan.json"
        installer.write_plan(plan_path, plan)
        base_site_before = combined._base_site_boundary(plan)
        try:
            receipt = installer.run(plan_path)
        except Exception as error:
            stderr = output / "command_receipts/02_install_explicit_wheels/stderr"
            detail = stderr.read_text(encoding="utf-8", errors="replace") \
                if stderr.is_file() else "<no install stderr>"
            self.fail(f"offline synthetic installation failed: {error}\n{detail}")
        self.assertEqual(receipt, installer.verify(output))
        self.assertEqual(
            runtime_manifest._validate_offline_pyoptix_manifest_projection(
                receipt), receipt)
        self.assertEqual(
            _validate_current_offline_pyoptix_install_independently(
                output / "offline_pyoptix_clean_install_receipt.json"),
            receipt)
        rtdl_wheel = (
            self.sources / "rtdl_source_tree-4.0.0rc1-py3-none-any.whl")
        build_wheel(
            rtdl_wheel, name="rtdl-source-tree", version="4.0.0rc1")
        final_output = self.root / "distinct_final_combined_runtime"
        final_plan = combined.build_plan(
            output=final_output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap,
            wheel_specs=[
                *[
                    f"{name.replace('-', '_')}={self.paths[name]}"
                    for name, _ in wheelhouse.REQUIRED_DISTRIBUTIONS
                ],
                f"rtdl={rtdl_wheel}",
            ],
        )
        final_plan_path = self.root / "distinct_final_combined_plan.json"
        combined.write_plan(final_plan_path, final_plan)
        try:
            final_receipt = combined.run_plan(
                final_plan_path,
                expected_plan_file_sha256=hashlib.sha256(
                    final_plan_path.read_bytes()).hexdigest(),
            )
        except Exception as error:
            stderr = (
                final_output
                / "command_receipts/02_install_explicit_wheels/stderr"
            )
            detail = stderr.read_text(encoding="utf-8", errors="replace") \
                if stderr.is_file() else "<no install stderr>"
            self.fail(
                "distinct combined runtime installation failed: "
                f"{error}\n{detail}")
        self.assertEqual(
            _validate_combined_runtime_root_independently(final_output),
            final_receipt)
        self.assertNotEqual(
            receipt["generic_combined_runtime_receipt_sha256"],
            final_receipt["receipt_sha256"])
        self.assertNotEqual(
            receipt["generic_venv_member_tree_sha256"],
            final_receipt["venv_member_tree_sha256"])
        self.assertEqual(
            final_receipt["expected_explicit_distributions"]
            ["rtdl-source-tree"], "4.0.0rc1")
        self.assertEqual(
            receipt["status"],
            "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED")
        self.assertEqual(receipt["required_distributions"],
                         wheelhouse.REQUIRED_VERSION_MAP)
        self.assertEqual(
            receipt["generic_base_python_site_boundary"], base_site_before)
        self.assertEqual(combined._base_site_boundary(plan), base_site_before)
        site_packages = output / combined._venv_site_packages_relative(os.name)
        bytecode_members = [
            path
            for name, _ in wheelhouse.REQUIRED_DISTRIBUTIONS
            for path in (site_packages / name.replace("-", "_")).rglob("*")
            if path.is_file() and (
                path.suffix == ".pyc" or "__pycache__" in path.parts)
        ]
        self.assertEqual(bytecode_members, [])
        self.assertEqual(receipt["validation_boundary"]
                         ["gpu_kernel_launch_count"], 0)
        self.assertFalse(
            self.pth_marker.exists(),
            "a wheel-supplied .pth executed during the offline build")
        self.assertGreater(receipt["generic_venv_member_count"], 0)
        self.assertRegex(
            receipt["generic_venv_member_tree_sha256"], r"\A[0-9a-f]{64}\Z")
        self.assertRegex(
            receipt["generic_base_python_site_boundary"]["projection_sha256"],
            r"\A[0-9a-f]{64}\Z")
        with self.assertRaises(FileExistsError):
            installer.run(plan_path)
        hostile = output / "venv/UNRECEIPTED_HOSTILE_PAYLOAD.txt"
        hostile.write_text("not registered\n", encoding="utf-8")
        with self.assertRaises(installer.OfflinePyOptiXInstallError):
            installer.verify(output)


if __name__ == "__main__":
    unittest.main()
