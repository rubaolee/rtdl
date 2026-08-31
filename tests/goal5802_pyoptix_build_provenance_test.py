"""Hostile tests for portable PyOptiX build/header provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts import goal5802_materialize_pyoptix_build_provenance as subject
from experiments.goal5802_premeasurement import independent_recount as independent


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        [shutil.which("git") or "git", *args], cwd=cwd, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return completed.stdout.decode("ascii").strip()


class PyOptixBuildProvenanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.headers = self.root / "headers-source"
        (self.headers / "include").mkdir(parents=True)
        (self.headers / "include" / "optix.h").write_bytes(b"#define OPTIX_VERSION 90000\n")
        git(self.headers, "init", "-q")
        git(self.headers, "config", "user.name", "Goal5802 Test")
        git(self.headers, "config", "user.email", "goal5802@example.invalid")
        git(self.headers, "config", "core.autocrlf", "false")
        git(self.headers, "add", ".")
        git(self.headers, "commit", "-q", "-m", "headers")
        self.headers_commit = git(self.headers, "rev-parse", "HEAD")
        self.headers_tree = git(self.headers, "rev-parse", "HEAD^{tree}")
        self.bundle = self.root / "headers.bundle"
        git(self.headers, "bundle", "create", str(self.bundle), "HEAD")

        self.extension = b"synthetic-extension"
        self.wheel = self.root / "pyoptix-test.whl"
        with zipfile.ZipFile(self.wheel, "w", zipfile.ZIP_STORED) as archive:
            archive.writestr(subject.EXTENSION_MEMBER, self.extension)
            archive.writestr("optix/__init__.py", b"from ._optix import *\n")
        self.source_commit = "1" * 40
        self.source_tree = "2" * 40
        self.receipt = self.root / "historical.json"
        value = {
            "schema": subject.ORIGINAL_SCHEMA,
            "status": "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED",
            "transaction_kind": "build_provenance_not_performance",
            "pyoptix_source": {
                "commit": self.source_commit,
                "tree": self.source_tree,
                "archive_projection_file_count": 1,
                "archive_projection_files": [{
                    "path": "src/main.cpp", "bytes": 1,
                    "sha256": sha(b"x"),
                }],
            },
            "optix_headers": {
                "api_macro": 90000,
                "commit": self.headers_commit,
                "tree": self.headers_tree,
                "root": "/historical/linux/absolute/optix-dev",
            },
            "build": {"exit_code": 0},
            "wheel": {
                "path": self.wheel.name,
                "bytes": self.wheel.stat().st_size,
                "sha256": sha(self.wheel.read_bytes()),
                "extension_member": subject.EXTENSION_MEMBER,
                "extension_bytes": len(self.extension),
                "extension_sha256": sha(self.extension),
            },
            "registered_performance_timing_count": 0,
        }
        self.receipt.write_bytes(canonical(value) + b"\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def patches(self):
        return mock.patch.multiple(
            subject,
            PYOPTIX_COMMIT=self.source_commit,
            PYOPTIX_TREE=self.source_tree,
            HEADERS_COMMIT=self.headers_commit,
            HEADERS_TREE=self.headers_tree,
            ORIGINAL_RECEIPT_SHA256=sha(self.receipt.read_bytes()),
            ORIGINAL_RECEIPT_BYTES=self.receipt.stat().st_size,
            ORIGINAL_SOURCE_PROJECTION_FILE_COUNT=1,
            ORIGINAL_SOURCE_PROJECTION_SHA256=subject._digest([{
                "path": "src/main.cpp", "bytes": 1,
                "sha256": sha(b"x"),
            }]),
            ORIGINAL_HEADERS_ROOT="/historical/linux/absolute/optix-dev",
            PYOPTIX_WHEEL_SHA256=sha(self.wheel.read_bytes()),
            PYOPTIX_WHEEL_BYTES=self.wheel.stat().st_size,
            EXTENSION_SHA256=sha(self.extension),
            EXTENSION_BYTES=len(self.extension),
        )

    def independent_patches(self):
        return mock.patch.multiple(
            independent,
            PYOPTIX_COMMIT=self.source_commit,
            PYOPTIX_TREE=self.source_tree,
            OPTIX_HEADERS_COMMIT=self.headers_commit,
            OPTIX_HEADERS_TREE=self.headers_tree,
            PYOPTIX_HISTORICAL_BUILD_RECEIPT_SHA256=sha(
                self.receipt.read_bytes()),
            PYOPTIX_HISTORICAL_BUILD_RECEIPT_BYTES=self.receipt.stat().st_size,
            PYOPTIX_HISTORICAL_SOURCE_FILE_COUNT=1,
            PYOPTIX_HISTORICAL_SOURCE_SHA256=independent._digest([{
                "path": "src/main.cpp", "bytes": 1,
                "sha256": sha(b"x"),
            }]),
            PYOPTIX_HISTORICAL_HEADERS_ROOT=(
                "/historical/linux/absolute/optix-dev"),
            PYOPTIX_WHEEL_SHA256=sha(self.wheel.read_bytes()),
            PYOPTIX_WHEEL_BYTES=self.wheel.stat().st_size,
            PYOPTIX_EXTENSION_SHA256=sha(self.extension),
            PYOPTIX_EXTENSION_BYTES=len(self.extension),
        )

    def test_materializes_and_reverifies_exact_checkout_without_network(self) -> None:
        output = self.root / "output"
        args = argparse.Namespace(
            git=Path(shutil.which("git") or "git"),
            headers_bundle=self.bundle,
            original_build_receipt=self.receipt,
            pyoptix_wheel=self.wheel,
            output_directory=output,
        )
        with self.patches():
            value = subject.materialize(args)
            self.assertEqual(
                subject.validate_materialization_receipt(output / "receipt.json"),
                value)
            self.assertFalse(value["claim_boundaries"]["historical_build_reexecuted"])
            self.assertEqual(value["formal_worker_count"], 0)
        checkout = output / "optix_headers"
        projected = self.root / "projected-optix-include"
        shutil.copytree(checkout / "include", projected)
        files = {"pyoptix_wheel": {
            "path": str(self.wheel.resolve()),
            "bytes": self.wheel.stat().st_size,
            "sha256": sha(self.wheel.read_bytes()),
        }}
        directories = {
            "optix_sdk": {"path": str(checkout.resolve())},
            "optix_include": {"path": str(projected.resolve())},
        }
        original_include = (checkout / "include").resolve()
        header_projection = {
            "command_authority": {"original_sdk_roots": {
                "optix_include": {
                    "resolved_path": str(original_include),
                },
            }},
            "root_mappings": [{
                "role": "optix_include",
                "original_root": str(original_include),
                "projected_root": str(projected.resolve()),
                "roots_distinct_and_nonoverlapping": True,
            }],
        }
        with self.independent_patches():
            historical = (
                independent
                ._validate_current_pyoptix_materialization_independently(
                    output / "receipt.json", files=files,
                    directories=directories,
                    header_projection=header_projection))
        self.assertEqual(historical["pyoptix_source"]["commit"],
                         self.source_commit)

    def test_checkout_tamper_and_create_only_fail_closed(self) -> None:
        output = self.root / "output"
        args = argparse.Namespace(
            git=Path(shutil.which("git") or "git"),
            headers_bundle=self.bundle,
            original_build_receipt=self.receipt,
            pyoptix_wheel=self.wheel,
            output_directory=output,
        )
        with self.patches():
            subject.materialize(args)
            with self.assertRaises(FileExistsError):
                subject.materialize(args)
            (output / "optix_headers" / "include" / "optix.h").write_bytes(b"tamper")
            with self.assertRaises(subject.PyOptixProvenanceError):
                subject.validate_materialization_receipt(output / "receipt.json")

    def test_resealed_historical_receipt_cannot_replace_frozen_source_projection(self) -> None:
        value = json.loads(self.receipt.read_text(encoding="utf-8"))
        value["pyoptix_source"]["archive_projection_files"] = [{
            "path": "fabricated/not_the_built_source.py", "bytes": 1,
            "sha256": sha(b"z"),
        }]
        value["optix_headers"]["root"] = "/fabricated/historical/header/root"
        self.receipt.write_bytes(canonical(value) + b"\n")
        output = self.root / "output"
        args = argparse.Namespace(
            git=Path(shutil.which("git") or "git"),
            headers_bundle=self.bundle,
            original_build_receipt=self.receipt,
            pyoptix_wheel=self.wheel,
            output_directory=output,
        )
        # Patch all scientific constants except the receipt/source/root pins:
        # those remain bound to the genuine pre-mutation bytes captured here.
        original_payload = canonical({
            **value,
            "pyoptix_source": {
                **value["pyoptix_source"],
                "archive_projection_files": [{
                    "path": "src/main.cpp", "bytes": 1,
                    "sha256": sha(b"x"),
                }],
            },
            "optix_headers": {
                **value["optix_headers"],
                "root": "/historical/linux/absolute/optix-dev",
            },
        }) + b"\n"
        with mock.patch.multiple(
                subject,
                PYOPTIX_COMMIT=self.source_commit,
                PYOPTIX_TREE=self.source_tree,
                HEADERS_COMMIT=self.headers_commit,
                HEADERS_TREE=self.headers_tree,
                ORIGINAL_RECEIPT_SHA256=sha(original_payload),
                ORIGINAL_RECEIPT_BYTES=len(original_payload),
                ORIGINAL_SOURCE_PROJECTION_FILE_COUNT=1,
                ORIGINAL_SOURCE_PROJECTION_SHA256=subject._digest([{
                    "path": "src/main.cpp", "bytes": 1,
                    "sha256": sha(b"x"),
                }]),
                ORIGINAL_HEADERS_ROOT="/historical/linux/absolute/optix-dev",
                PYOPTIX_WHEEL_SHA256=sha(self.wheel.read_bytes()),
                PYOPTIX_WHEEL_BYTES=self.wheel.stat().st_size,
                EXTENSION_SHA256=sha(self.extension),
                EXTENSION_BYTES=len(self.extension)):
            with self.assertRaises(subject.PyOptixProvenanceError):
                subject.materialize(args)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
