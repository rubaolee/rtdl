from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

from scripts import goal5809_execution_identity as identity


def _pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


class Goal5809ExecutionIdentityTest(unittest.TestCase):
    def _identity(self, root: Path) -> tuple[Path, dict[str, object]]:
        roles = sorted(identity.REQUIRED_BASE_FILE_ROLES | {"bulk_helper_00"})
        files = {}
        for role in roles:
            path = root / "files" / role
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((role + "\n").encode())
            files[role] = {
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": identity.sha256_file(path),
                "provenance": "TEST_AUTHORITY",
            }
        body = {
            "schema": identity.SCHEMA,
            "status": identity.STATUS,
            "scope": {
                "claim_authorized": False,
                "formal_worker_count": 0,
                "nonformal_pilot_only": True,
                "registered_performance_timing_count": 0,
            },
            "predecessor_runtime_manifest": {
                "dependency_source_only": True,
                "is_goal5809_execution_identity": False,
            },
            "pyoptix": {
                "api_version": "9.0.0",
                "distribution_name": "pyoptix",
                "distribution_version": "9.1.0",
                "extension_module": "optix._optix",
                "extension_role": "pyoptix_extension",
                "initializer_module": "optix",
                "initializer_role": "pyoptix_initializer",
            },
            "required_file_roles": sorted(files),
            "files": files,
        }
        value = {
            **body,
            "execution_identity_sha256": identity.digest(body),
        }
        path = root / "execution_identity.json"
        path.write_bytes(_pretty(value))
        return path, value

    def _strict_identity(
        self, root: Path,
    ) -> tuple[Path, dict[str, object], Path, Path]:
        path, value = self._identity(root)
        source_worker = root / "source/scripts/goal5809_worker.py"
        source_worker.parent.mkdir(parents=True)
        (root / "source/src").mkdir(parents=True)
        source_worker.write_bytes(b"# exact Goal5809 test worker\n")
        value["files"]["goal5809_rtdl_worker"].update({
            "path": str(source_worker.resolve()),
            "bytes": source_worker.stat().st_size,
            "sha256": identity.sha256_file(source_worker),
        })
        combined = root / "combined_runtime"
        interpreter = combined / "venv/bin/python"
        numpy_init = combined / "venv/lib/python3.12/site-packages/numpy.py"
        frozen_base_bin = root / "frozen_base/bin"
        interpreter.parent.mkdir(parents=True)
        numpy_init.parent.mkdir(parents=True)
        frozen_base_bin.mkdir(parents=True)
        interpreter.write_bytes(b"exact-test-cpython\n")
        numpy_init.write_bytes(b"__version__ = '2.2.6'\n")
        (combined / "venv/pyvenv.cfg").write_text(
            f"home = {frozen_base_bin.resolve()}\n"
            "include-system-site-packages = false\n"
            "version = 3.12.3\n",
            encoding="utf-8")
        rows = identity._runtime_member_tree(combined)
        runtime_body = {
            "schema": identity._RUNTIME_MANIFEST_SCHEMA,
            "status": identity._RUNTIME_MANIFEST_STATUS,
            "files": {
                "clean_python": {
                    "path": str(interpreter.resolve()),
                    "path_kind": "REGULAR_FILE",
                    "bytes": interpreter.stat().st_size,
                    "sha256": identity.sha256_file(interpreter),
                },
            },
            "build_provenance": {
                "combined_runtime_full_venv_member_tree_sha256": (
                    identity.digest(rows)),
                "combined_runtime_path_projection": {
                    "root_path": str(combined.resolve()),
                    "clean_python_relative": "venv/bin/python",
                    "site_packages_relative": (
                        "venv/lib/python3.12/site-packages"),
                    "rtdsl_package_relative": (
                        "venv/lib/python3.12/site-packages/rtdsl"),
                    "pyoptix_initializer_relative": (
                        "venv/lib/python3.12/site-packages/optix/__init__.py"),
                    "pyoptix_extension_relative": (
                        "venv/lib/python3.12/site-packages/optix/_optix.so"),
                    "all_runtime_paths_inside_receipted_combined_root": True,
                },
            },
            "target_observation": {
                "loader_environment": {
                    "LD_LIBRARY_PATH": None,
                    "LD_PRELOAD": None,
                },
            },
        }
        runtime = {
            **runtime_body,
            "manifest_sha256": identity.digest(runtime_body),
        }
        runtime_path = Path(value["files"][
            "runtime_manifest_dependency_source"]["path"])
        runtime_path.write_bytes(_pretty(runtime))
        value["files"]["runtime_manifest_dependency_source"].update({
            "bytes": runtime_path.stat().st_size,
            "sha256": identity.sha256_file(runtime_path),
        })
        value["predecessor_runtime_manifest"]["semantic_sha256"] = runtime[
            "manifest_sha256"]
        body = dict(value)
        body.pop("execution_identity_sha256")
        value = {**body, "execution_identity_sha256": identity.digest(body)}
        path.write_bytes(_pretty(value))
        return path, value, interpreter, numpy_init

    @staticmethod
    def _controlled_startup(root: Path) -> dict[str, object]:
        return {
            "flags": {
                "isolated": 1,
                "no_site": 1,
                "dont_write_bytecode": 1,
                "safe_path": 1,
                "ignore_environment": 1,
                "no_user_site": 1,
            },
            "sys_path_prefix": [
                str((root / "source/src").resolve()),
                str((root / "source").resolve()),
                str((root / "combined_runtime/venv/lib/python3.12/"
                     "site-packages").resolve()),
            ],
            "environment": {
                "PYTHONPATH": None,
                "PYTHONHOME": None,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONNOUSERSITE": "1",
                "PYTHONHASHSEED": None,
                "LD_LIBRARY_PATH": None,
                "LD_PRELOAD": None,
            },
        }

    def test_static_and_loaded_module_identity_are_both_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path, value = self._identity(Path(temporary))
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"):
                admitted = identity.admit_execution_identity(
                    path, expected_file_sha256=identity.sha256_file(path))
            files = value["files"]
            rtdl = types.SimpleNamespace(
                __file__=files["rtdl_init"]["path"])
            implementation = types.SimpleNamespace(
                __file__=files["rtdlexe_module"]["path"])
            self.assertTrue(identity.verify_loaded_rtdl(
                admitted, rtdl_module=rtdl,
                implementation_module=implementation,
            )["rtdl_loaded_identity_verified"])

            optix = types.SimpleNamespace(
                __file__=files["pyoptix_initializer"]["path"],
                version=lambda: (9, 0, 0),
            )
            extension = types.SimpleNamespace(
                __file__=files["pyoptix_extension"]["path"])
            with mock.patch.dict(
                    sys.modules, {"optix._optix": extension}):
                observed = identity.verify_loaded_pyoptix(
                    admitted, optix_module=optix)
            self.assertTrue(observed["pyoptix_loaded_identity_verified"])
            self.assertEqual(
                admitted["file_count"], len(identity.REQUIRED_BASE_FILE_ROLES) + 1)

    def test_bound_file_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path, value = self._identity(Path(temporary))
            Path(value["files"]["workload_source"]["path"]).write_bytes(
                b"changed")
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"):
                with self.assertRaisesRegex(
                        RuntimeError, "execution file differs: workload_source"):
                    identity.admit_execution_identity(
                        path,
                        expected_file_sha256=identity.sha256_file(path))

    def test_loaded_same_named_module_from_other_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, _value = self._identity(root)
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"):
                admitted = identity.admit_execution_identity(
                    path, expected_file_sha256=identity.sha256_file(path))
            other = root / "other_rtdsl.py"
            other.write_bytes(b"same module name, wrong path")
            with self.assertRaisesRegex(
                    RuntimeError, "loaded module differs: rtdl_init"):
                identity.verify_loaded_rtdl(
                    admitted,
                    rtdl_module=types.SimpleNamespace(__file__=str(other)),
                    implementation_module=types.SimpleNamespace(
                        __file__=admitted["manifest"]["files"][
                            "rtdlexe_module"]["path"]),
                )

    def test_active_protocol_and_provenance_loaded_paths_are_checked(self) \
            -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, value = self._identity(root)
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"):
                admitted = identity.admit_execution_identity(
                    path, expected_file_sha256=identity.sha256_file(path))
            files = value["files"]
            observed = identity.verify_loaded_modules(
                admitted,
                modules_by_role={
                    "goal5805_protocol_source": types.SimpleNamespace(
                        __file__=files["goal5805_protocol_source"]["path"]),
                    "physical_execution_provenance_module": (
                        types.SimpleNamespace(__file__=files[
                            "physical_execution_provenance_module"]["path"])),
                    "goal5800_pyoptix_idiomatic_arm_source": (
                        types.SimpleNamespace(__file__=files[
                            "goal5800_pyoptix_idiomatic_arm_source"]["path"])),
                })
            self.assertTrue(observed["loaded_module_identity_verified"])
            wrong = root / "wrong_protocol.py"
            wrong.write_bytes(b"wrong path")
            with self.assertRaisesRegex(
                    RuntimeError,
                    "loaded module differs: goal5805_protocol_source"):
                identity.verify_loaded_modules(
                    admitted,
                    modules_by_role={
                        "goal5805_protocol_source": types.SimpleNamespace(
                            __file__=str(wrong)),
                    })

    def test_exact_interpreter_full_venv_and_loaded_dependency_are_rehashed(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, _value, interpreter, numpy_init = self._strict_identity(root)
            venv = interpreter.parents[1]
            frozen_base = (root / "frozen_base").resolve()
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"), mock.patch.object(
                    identity.sys, "executable", str(interpreter)), \
                    mock.patch.object(
                        identity.sys, "prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity.sys, "base_prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity, "_startup_observation",
                        return_value=self._controlled_startup(root)):
                admitted = identity.admit_execution_identity(
                    path, expected_file_sha256=identity.sha256_file(path),
                    require_runtime_environment=True)
            environment = admitted["runtime_environment_admission"]
            self.assertTrue(environment[
                "complete_venv_member_tree_live_rehashed"])
            self.assertEqual(
                environment["admitted_interpreter_sha256"],
                identity.sha256_file(interpreter))
            self.assertEqual(environment["sys_prefix"], str(frozen_base))
            self.assertNotEqual(environment["sys_prefix"], str(venv))
            module = types.SimpleNamespace(
                __file__=str(numpy_init), __version__="2.2.6")
            with mock.patch.dict(
                    identity.sys.modules, {"numpy": module}, clear=True):
                observed = identity.verify_loaded_runtime_dependencies(
                    admitted, required_module_roots=("numpy",),
                    observed_versions={"numpy": "2.2.6"})
            self.assertEqual(observed["loaded_dependency_file_count"], 1)
            self.assertEqual(
                observed["loaded_module_files"]["numpy"]["sha256"],
                identity.sha256_file(numpy_init))

            # The old implementation accepted this exact attack: mutate a
            # dependency after admission, report an arbitrary new version,
            # and simply seal the newly observed bytes.  It must now compare
            # the loaded file to the admission-time member row.
            numpy_init.write_bytes(b"__version__ = 'evil'\n")
            evil = types.SimpleNamespace(
                __file__=str(numpy_init), __version__="evil")
            with mock.patch.dict(
                    identity.sys.modules, {"numpy": evil}, clear=True):
                with self.assertRaisesRegex(
                        RuntimeError, "differs from admission"):
                    identity.verify_loaded_runtime_dependencies(
                        admitted, required_module_roots=("numpy",),
                        observed_versions={"numpy": "evil"})

            numpy_init.write_bytes(b"__version__ = '2.2.6'\n")
            (numpy_init.parent / "unloaded_drift.py").write_bytes(b"drift\n")
            with mock.patch.dict(
                    identity.sys.modules, {"numpy": module}, clear=True):
                with self.assertRaisesRegex(
                        RuntimeError, "tree changed after admission"):
                    identity.verify_loaded_runtime_dependencies(
                        admitted, required_module_roots=("numpy",),
                        observed_versions={"numpy": "2.2.6"})

    def test_wrong_interpreter_or_venv_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, _value, interpreter, numpy_init = self._strict_identity(root)
            venv = interpreter.parents[1]
            frozen_base = (root / "frozen_base").resolve()
            wrong = root / "wrong_python"
            wrong.write_bytes(interpreter.read_bytes())
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"), mock.patch.object(
                    identity.sys, "executable", str(wrong)), \
                    mock.patch.object(
                        identity.sys, "prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity.sys, "base_prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity, "_startup_observation",
                        return_value=self._controlled_startup(root)):
                with self.assertRaisesRegex(
                        RuntimeError, "did not use the admitted clean"):
                    identity.admit_execution_identity(
                        path, expected_file_sha256=identity.sha256_file(path),
                        require_runtime_environment=True)

            numpy_init.write_bytes(b"drift\n")
            with mock.patch.object(
                    identity.importlib.metadata, "version",
                    return_value="9.1.0"), mock.patch.object(
                    identity.sys, "executable", str(interpreter)), \
                    mock.patch.object(
                        identity.sys, "prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity.sys, "base_prefix", str(frozen_base)), \
                    mock.patch.object(
                        identity, "_startup_observation",
                        return_value=self._controlled_startup(root)):
                with self.assertRaisesRegex(
                        RuntimeError, "live combined runtime tree differs"):
                    identity.admit_execution_identity(
                        path, expected_file_sha256=identity.sha256_file(path),
                        require_runtime_environment=True)

    def test_controlled_startup_rejects_flags_path_and_environment_injection(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (
                    "source/src", "source",
                    "combined_runtime/venv/lib/python3.12/site-packages",
                    "attacker"):
                (root / relative).mkdir(parents=True, exist_ok=True)
            observed = self._controlled_startup(root)
            expected_roots = list(observed["sys_path_prefix"])
            loader = {"LD_LIBRARY_PATH": None, "LD_PRELOAD": None}
            accepted = identity._validate_controlled_startup(
                observed, expected_import_roots=expected_roots,
                expected_loader_environment=loader)
            self.assertTrue(accepted[
                "python_environment_injection_sources_absent"])

            for hostile in (
                    {**observed, "flags": {
                        **observed["flags"], "isolated": 0}},
                    {**observed, "sys_path_prefix": [
                        str(root / "attacker"), *expected_roots[1:]]},
                    {**observed, "environment": {
                        **observed["environment"],
                        "PYTHONPATH": str(root / "attacker")}},
                    {**observed, "environment": {
                        **observed["environment"],
                        "LD_PRELOAD": str(root / "evil.so")}},
            ):
                with self.subTest(hostile=hostile):
                    with self.assertRaisesRegex(
                            RuntimeError, "controlled Python startup differs"):
                        identity._validate_controlled_startup(
                            hostile, expected_import_roots=expected_roots,
                            expected_loader_environment=loader)

if __name__ == "__main__":
    unittest.main()
