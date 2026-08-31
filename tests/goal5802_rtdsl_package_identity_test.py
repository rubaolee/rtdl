from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from experiments.goal5802_premeasurement import controller
from experiments.goal5802_premeasurement.runtime_manifest import (
    rtdsl_package_identity,
    rtdsl_wheel_package_identity,
)
from experiments.goal5802_premeasurement.independent_recount import (
    _independent_rtdsl_wheel_package_identity,
)


def _write_package(root: Path) -> Path:
    package = root / "rtdsl"
    package.mkdir()
    (package / "__init__.py").write_bytes(b"PACKAGE = 'rtdsl'\n")
    (package / "v4_callback_lifecycle.py").write_bytes(
        b"LIFECYCLE = 'prepare'\n")
    (package / "v4_bounded_relation_optix_compiler.py").write_bytes(
        b"COMPILER = 'bounded'\n")
    return package


def _write_wheel(path: Path, package: Path, *, extra=None) -> None:
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    members = {
        f"rtdsl/{item.relative_to(package).as_posix()}": item.read_bytes()
        for item in package.rglob("*") if item.is_file()
    }
    members.update({
        f"{dist}/METADATA": b"Metadata-Version: 2.1\n",
        f"{dist}/WHEEL": b"Wheel-Version: 1.0\n",
        f"{dist}/top_level.txt": b"rtdsl\n",
        f"{dist}/RECORD": b"",
    })
    if extra:
        members.update(extra)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)


class Goal5802RtdslPackageIdentityTest(unittest.TestCase):
    def test_wheel_package_tree_equals_installed_package_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = _write_package(root)
            wheel = root / "rtdl.whl"
            _write_wheel(wheel, package)
            installed = rtdsl_package_identity(package)
            self.assertEqual(rtdsl_wheel_package_identity(wheel), installed)
            self.assertEqual(
                _independent_rtdsl_wheel_package_identity(wheel), installed)

            (package / "v4_callback_lifecycle.py").write_bytes(
                b"LIFECYCLE = 'drifted'\n")
            self.assertNotEqual(
                rtdsl_wheel_package_identity(wheel),
                rtdsl_package_identity(package))

    def test_wheel_package_boundary_is_fail_closed(self) -> None:
        hostile_members = (
            {"outside.py": b"escape\n"},
            {"../escape.py": b"escape\n"},
            {"rtdsl/__pycache__/bad.pyc": b"bytecode\n"},
        )
        for extra in hostile_members:
            with self.subTest(extra=next(iter(extra))), \
                    tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                package = _write_package(root)
                wheel = root / "hostile.whl"
                _write_wheel(wheel, package, extra=extra)
                with self.assertRaises(RuntimeError):
                    rtdsl_wheel_package_identity(wheel)
                with self.assertRaises(RuntimeError):
                    _independent_rtdsl_wheel_package_identity(wheel)

    def test_valid_complete_package_tree_has_stable_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = _write_package(Path(temporary))

            first = rtdsl_package_identity(package)
            second = rtdsl_package_identity(package)

            self.assertEqual(first, second)
            self.assertEqual(first["file_count"], 3)
            self.assertEqual(
                [row["path"] for row in first["files"]],
                [
                    "rtdsl/__init__.py",
                    "rtdsl/v4_bounded_relation_optix_compiler.py",
                    "rtdsl/v4_callback_lifecycle.py",
                ],
            )
            self.assertEqual(len(first["tree_sha256"]), 64)

    def test_one_byte_compiler_or_lifecycle_drift_breaks_frozen_identity(
            self) -> None:
        mutations = (
            ("v4_bounded_relation_optix_compiler.py", b"bounded", b"boundee"),
            ("v4_callback_lifecycle.py", b"prepare", b"preparf"),
        )
        for filename, before, after in mutations:
            with self.subTest(filename=filename), \
                    tempfile.TemporaryDirectory() as temporary:
                package = _write_package(Path(temporary))
                frozen = rtdsl_package_identity(package)
                path = package / filename
                payload = path.read_bytes()
                self.assertEqual(len(before), len(after))
                self.assertEqual(payload.count(before), 1)
                path.write_bytes(payload.replace(before, after))

                observed = rtdsl_package_identity(package)

                self.assertEqual(observed["file_count"], frozen["file_count"])
                self.assertEqual(
                    observed["payload_bytes"], frozen["payload_bytes"])
                self.assertNotEqual(
                    observed["tree_sha256"], frozen["tree_sha256"])
                self.assertNotEqual(observed, frozen)

    def test_extra_python_source_breaks_frozen_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = _write_package(Path(temporary))
            frozen = rtdsl_package_identity(package)
            (package / "unexpected_override.py").write_bytes(b"ACTIVE = True\n")

            observed = rtdsl_package_identity(package)

            self.assertEqual(
                observed["file_count"], int(frozen["file_count"]) + 1)
            self.assertNotEqual(
                observed["tree_sha256"], frozen["tree_sha256"])
            self.assertIn(
                "rtdsl/unexpected_override.py",
                [row["path"] for row in observed["files"]],
            )

    def test_bytecode_cache_is_rejected_fail_closed(self) -> None:
        cache_locations = (
            Path("__pycache__") / "v4_callback_lifecycle.cpython-312.pyc",
            Path("unexpected.pyc"),
        )
        for relative in cache_locations:
            with self.subTest(relative=relative.as_posix()), \
                    tempfile.TemporaryDirectory() as temporary:
                package = _write_package(Path(temporary))
                cache = package / relative
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_bytes(b"synthetic-bytecode")

                with self.assertRaisesRegex(RuntimeError, "bytecode cache"):
                    rtdsl_package_identity(package)

    def test_runtime_manifest_failure_stops_before_preflight_or_worker(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            freeze_path = root / "freeze.json"
            authority_path = root / "authority.json"
            runtime_path = root / "runtime.json"
            output_directory = root / "formal-output"
            for path in (freeze_path, authority_path, runtime_path):
                path.write_text(json.dumps({}) + "\n", encoding="utf-8")

            with mock.patch.object(controller, "validate_freeze"), \
                    mock.patch.object(
                        controller, "validate_runtime_manifest",
                        side_effect=RuntimeError("live package drift")), \
                    mock.patch.object(
                        controller, "_formal_runtime_preflight") as preflight, \
                    mock.patch.object(controller, "_execute_one") as worker:
                with self.assertRaisesRegex(RuntimeError, "live package drift"):
                    controller.execute_formal(
                        root=root,
                        freeze_path=freeze_path,
                        authority_path=authority_path,
                        runtime_path=runtime_path,
                        output_directory=output_directory,
                        timeout_seconds=1,
                    )

            preflight.assert_not_called()
            worker.assert_not_called()
            self.assertFalse(output_directory.exists())


if __name__ == "__main__":
    unittest.main()
