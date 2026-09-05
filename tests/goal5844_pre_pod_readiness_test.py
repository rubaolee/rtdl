"""Offline and hostile tests for the Goal5844 pod transaction."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from experiments.goal5798_premeasurement.compatibility import (
    PYOPTIX_COMMIT,
    PYOPTIX_REPOSITORY,
    PYOPTIX_TREE,
    frozen_registry,
)
from experiments.goal5842_causal_admission.contracts import TRIANGLE_TASK, digest
from experiments.goal5844_compact_execution import provenance, worker
from scripts import goal5838_build_selected_sphere_optix_provider as native_builder
from scripts import goal5844_launch_pod_transaction as launcher
from scripts import goal5844_run_gpu_engineering_comparison as comparison
from scripts import goal5844_verify_gpu_engineering_result as verifier

SOURCE_COMMIT = "a" * 40
OPTIX_API = "9.0.0"
COMPUTE_CAPABILITY = "8.6"


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _make_git_archive(path: Path, *, commit: str, members: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(
        path,
        "w:",
        format=tarfile.PAX_FORMAT,
        pax_headers={"comment": commit},
    ) as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))


def _make_pyoptix_receipt(root: Path) -> Path:
    stack = next(
        row for row in frozen_registry() if row["optix_api_version"] == OPTIX_API
    )
    builder = root / "inputs" / "goal5844_build_install_pyoptix.py"
    source_archive = root / "inputs" / "otk-pyoptix.tar"
    header_archive = root / "inputs" / "optix-dev.tar"
    initializer = root / "installed" / "optix___init__.py"
    extension = root / "installed" / "_optix.cpython-312-x86_64-linux-gnu.so"
    wheel = root / "wheelhouse" / "pyoptix-9.1.0-cp312-linux.whl"
    _write(
        builder,
        (
            comparison.ROOT / "scripts" / "goal5844_build_install_pyoptix.py"
        ).read_bytes(),
    )
    _make_git_archive(
        source_archive,
        commit=PYOPTIX_COMMIT,
        members={"pyproject.toml": b"[project]\nname='pyoptix'\n"},
    )
    optix_header = b"#define OPTIX_VERSION 90000\n"
    optix_device_header = b"// synthetic optix device header\n"
    _make_git_archive(
        header_archive,
        commit=str(stack["optix_header_commit"]),
        members={
            "include/optix.h": optix_header,
            "include/optix_device.h": optix_device_header,
        },
    )
    _write(initializer, b"from ._optix import *\n")
    extension_payload = b"fake ELF extension bytes"
    _write(extension, extension_payload)
    wheel.parent.mkdir(parents=True, exist_ok=True)
    extension_member = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(extension_member, extension_payload)
    logs = {}
    dependency_rows = [
        {
            "metadata": {"name": package, "version": version},
            "download_info": {"archive_info": {"hashes": {"sha256": "9" * 64}}},
        }
        for package, version in provenance.REQUIRED_DEPENDENCIES.items()
    ]
    for name, payload in (
        ("build_stdout", b"built\n"),
        ("build_stderr", b""),
        ("install_stdout", b"installed\n"),
        ("install_stderr", b""),
        (
            "dependency_install_report",
            (
                json.dumps(
                    {
                        "version": "1",
                        "pip_version": "26.2.1",
                        "install": dependency_rows,
                    }
                )
                + "\n"
            ).encode("utf-8"),
        ),
        ("pip_freeze", b"pyoptix==9.1.0\n"),
    ):
        path = root / "logs" / f"{name}.txt"
        _write(path, payload)
        logs[name] = provenance.file_record(path, root)
    value: dict[str, object] = {
        "schema": provenance.PYOPTIX_BUILD_SCHEMA,
        "status": provenance.PYOPTIX_BUILD_STATUS,
        "transaction_kind": "build_install_provenance_not_performance",
        "registered_performance_timing_count": 0,
        "builder": provenance.file_record(builder, root),
        "pyoptix_source": {
            "repository_url": PYOPTIX_REPOSITORY,
            "checkout_path": "/pod/upstream/otk-pyoptix",
            "commit": PYOPTIX_COMMIT,
            "tree": PYOPTIX_TREE,
            "clean": True,
            "archive": provenance.file_record(source_archive, root),
        },
        "optix_headers": {
            "repository_url": "https://github.com/NVIDIA/optix-dev.git",
            "checkout_path": "/pod/upstream/optix-dev",
            "commit": stack["optix_header_commit"],
            "tree": "b" * 40,
            "clean": True,
            "api_version": OPTIX_API,
            "api_macro": 90000,
            "archive": provenance.file_record(header_archive, root),
            "key_header_sha256": {
                "optix.h": hashlib.sha256(optix_header).hexdigest(),
                "optix_device.h": hashlib.sha256(optix_device_header).hexdigest(),
            },
        },
        "build": {
            "python_executable": "/pod/venv/bin/python",
            "python_sha256": "e" * 64,
            "python_version": "3.12.11",
            "platform": "Linux-test",
            "cmake_args": (
                "-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=/pod/upstream/optix-dev"
            ),
            "build_environment": {
                "CMAKE_ARGS": (
                    "-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=/pod/upstream/optix-dev"
                ),
                "PYOPTIX_CMAKE_ARGS": (
                    "-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=/pod/upstream/optix-dev"
                ),
                "CXX": "/usr/bin/g++",
                "CUDACXX": "/usr/local/cuda/bin/nvcc",
                "CUDA_VISIBLE_DEVICES": "0",
            },
            "tools": {
                "cmake": {
                    "path": "/usr/bin/cmake",
                    "bytes": 1,
                    "sha256": "1" * 64,
                    "version": "cmake 3.30",
                },
                "cxx": {
                    "path": "/usr/bin/g++",
                    "bytes": 1,
                    "sha256": "2" * 64,
                    "version": "g++ 13",
                },
                "ninja": {
                    "path": "/usr/bin/ninja",
                    "bytes": 1,
                    "sha256": "3" * 64,
                    "version": "1.13",
                },
                "nvcc": {
                    "path": "/usr/local/cuda/bin/nvcc",
                    "bytes": 1,
                    "sha256": "4" * 64,
                    "version": "CUDA 12.8",
                },
            },
            "wheel_command": [
                "/pod/venv/bin/python",
                "-m",
                "pip",
                "wheel",
                "--no-build-isolation",
                "--no-deps",
            ],
            "install_command": [
                "/pod/venv/bin/python",
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                "--no-deps",
            ],
            "installed_dependencies": provenance.REQUIRED_RUNTIME_DEPENDENCIES,
            **logs,
        },
        "wheel": {
            "file": provenance.file_record(wheel, root),
            "extension_member": extension_member,
            "extension_bytes": len(extension_payload),
            "extension_sha256": provenance.sha256_file(extension),
        },
        "installed": {
            "distribution_name": "pyoptix",
            "distribution_version": "9.1.0",
            "optix_api_version": OPTIX_API,
            "package_initializer": provenance.file_record(initializer, root),
            "loaded_extension": provenance.file_record(extension, root),
            "loaded_extension_source_path": "/pod/venv/site-packages/optix/_optix.so",
            "installed_distributions": {
                **provenance.REQUIRED_RUNTIME_DEPENDENCIES,
                "pyoptix": "9.1.0",
            },
        },
        "claim_boundary": {
            "clean_source_build_bound": True,
            "loaded_extension_bound_to_wheel_member": True,
            "performance_measurement_in_receipt": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    value["receipt_sha256"] = provenance.digest(value)
    receipt = root / "build_receipt.json"
    provenance.write_json_create(receipt, value)
    return receipt


def _make_native_manifest(path: Path, native: Path, build_log: Path) -> None:
    value: dict[str, object] = {
        "schema": "rtdl.goal5838.selected_sphere_optix_provider_build.v2",
        "status": "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED",
        "repository": {
            "expected_commit": SOURCE_COMMIT,
            "head_before": SOURCE_COMMIT,
            "head_after": SOURCE_COMMIT,
            "clean_before": True,
            "clean_after": True,
        },
        "native_output": {
            "path": "/pod/native.so",
            "bytes": native.stat().st_size,
            "sha256": provenance.sha256_file(native),
        },
        "build_input": {
            "expected_optix_sdk": OPTIX_API,
            "compute_capability": COMPUTE_CAPABILITY,
        },
        "build_log": {
            "path": "/pod/build.log",
            "bytes": build_log.stat().st_size,
            "sha256": provenance.sha256_file(build_log),
        },
        "result_sha256": "",
    }
    value["result_sha256"] = native_builder._sealed_sha256(value)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _timing(samples: list[int]) -> dict[str, object]:
    ordered = sorted(samples)
    return {
        "sample_count": len(samples),
        "samples_ns": samples,
        "minimum_ns": min(samples),
        "median_ns": ordered[len(ordered) // 2],
        "maximum_ns": max(samples),
    }


def _row(item: dict[str, object], hardware: dict[str, object]) -> dict[str, object]:
    base = 120 if item["arm"] == comparison.RTDL_ARM else 100
    row: dict[str, object] = {
        "arm": item["arm"],
        "block": item["block"],
        "task": TRIANGLE_TASK,
        "hardware": hardware,
        "measurements": {"steady_public": _timing([base, base + 2, base + 4])},
    }
    row["result_sha256"] = digest(row)
    return row


def _make_result_root(root: Path) -> tuple[Path, list[dict[str, object]]]:
    result = root / "result"
    result.mkdir()
    native = result / "provenance" / "rtdl_native" / "librtdl_optix.so"
    build_log = result / "provenance" / "rtdl_native" / "build.log"
    manifest = result / "provenance" / "rtdl_native" / "build_manifest.json"
    symbols = result / "provenance" / "rtdl_native" / "symbols.txt"
    source = result / "provenance" / "matched_device.cu"
    _write(native, b"fake native DSO")
    _write(build_log, b"build output\n")
    _make_native_manifest(manifest, native, build_log)
    _write(symbols, f"000 T {comparison.V8_SYMBOL}\n".encode("ascii"))
    _write(source, b"// device source\n")
    receipt = _make_pyoptix_receipt(result / "provenance" / "pyoptix_build")
    artifacts = {
        "native_library": provenance.file_record(native, result),
        "native_build_manifest": provenance.file_record(manifest, result),
        "native_build_log": provenance.file_record(build_log, result),
        "native_dynamic_defined_symbols": provenance.file_record(symbols, result),
        "required_v8_symbol": comparison.V8_SYMBOL,
        "required_v8_symbol_present": True,
        "device_source": provenance.file_record(source, result),
        "pyoptix_build_receipt": provenance.file_record(receipt, result),
    }
    schedule = comparison.expected_schedule(4)
    hardware = {
        "gpu_name": "Synthetic GPU",
        "gpu_uuid": "GPU-test",
        "driver_version": "570.0",
        "memory_mib": 1,
        "compute_capability": COMPUTE_CAPABILITY,
    }
    rows = [_row(item, hardware) for item in schedule]
    worker_root = result / "workers"
    worker_root.mkdir()
    for item, row in zip(schedule, rows, strict=True):
        name = (
            f"block_{int(item['block']):02d}_{int(item['position'])}_{item['arm']}.json"
        )
        (worker_root / name).write_text(
            json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    args = SimpleNamespace(
        source_commit=SOURCE_COMMIT,
        optix_sdk=OPTIX_API,
        compute_capability=COMPUTE_CAPABILITY,
        pyoptix_distribution="pyoptix",
        blocks=4,
        warmups=1,
        repetitions=3,
        layer_warmups=1,
        layer_repetitions=1,
    )
    summary = comparison.build_summary(
        args, rows, schedule=schedule, hardware=hardware, provenance=artifacts
    )
    provenance.write_json_create(result / "SUMMARY.json", summary)
    provenance.write_evidence_manifest(result)
    return result, rows


class Goal5844PrePodReadinessTest(unittest.TestCase):
    def test_clean_build_receipt_binds_wheel_and_loaded_extension(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            receipt = _make_pyoptix_receipt(Path(name))
            value = provenance.validate_pyoptix_build_receipt(receipt)
            self.assertEqual(
                value["wheel"]["extension_sha256"],
                value["installed"]["loaded_extension"]["sha256"],
            )

    def test_resealed_extension_substitution_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            receipt = _make_pyoptix_receipt(root)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            extension = root / value["installed"]["loaded_extension"]["path"]
            extension.write_bytes(b"attacker replacement")
            value["installed"]["loaded_extension"] = provenance.file_record(
                extension, root
            )
            value.pop("receipt_sha256")
            value["receipt_sha256"] = provenance.digest(value)
            receipt.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                provenance.Goal5844EvidenceError, "not the wheel member"
            ):
                provenance.validate_pyoptix_build_receipt(receipt)

    def test_resealed_dependency_report_version_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            receipt = _make_pyoptix_receipt(root)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            report = root / value["build"]["dependency_install_report"]["path"]
            report_value = json.loads(report.read_text(encoding="utf-8"))
            report_value["install"][0]["metadata"]["version"] = "0.0.0"
            report.write_text(
                json.dumps(report_value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            value["build"]["dependency_install_report"] = provenance.file_record(
                report, root
            )
            value.pop("receipt_sha256")
            value["receipt_sha256"] = provenance.digest(value)
            receipt.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                provenance.Goal5844EvidenceError, "dependency versions"
            ):
                provenance.validate_pyoptix_build_receipt(receipt)

    def test_resealed_runtime_dependency_map_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            receipt = _make_pyoptix_receipt(Path(name))
            value = json.loads(receipt.read_text(encoding="utf-8"))
            value["build"]["installed_dependencies"]["numpy"] = "0.0.0"
            value.pop("receipt_sha256")
            value["receipt_sha256"] = provenance.digest(value)
            receipt.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                provenance.Goal5844EvidenceError, "build metadata"
            ):
                provenance.validate_pyoptix_build_receipt(receipt)

    def test_resealed_source_archive_commit_substitution_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            receipt = _make_pyoptix_receipt(root)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            source_archive = root / value["pyoptix_source"]["archive"]["path"]
            _make_git_archive(
                source_archive,
                commit="f" * 40,
                members={"pyproject.toml": b"[project]\nname='foreign'\n"},
            )
            value["pyoptix_source"]["archive"] = provenance.file_record(
                source_archive, root
            )
            value.pop("receipt_sha256")
            value["receipt_sha256"] = provenance.digest(value)
            receipt.write_text(
                json.dumps(value, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                provenance.Goal5844EvidenceError, "commit annotation"
            ):
                provenance.validate_pyoptix_build_receipt(receipt)

    def test_evidence_manifest_rejects_payload_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            _write(root / "payload.txt", b"before")
            provenance.write_evidence_manifest(root)
            provenance.validate_evidence_manifest(root)
            (root / "payload.txt").write_bytes(b"after")
            with self.assertRaisesRegex(provenance.Goal5844EvidenceError, "inventory"):
                provenance.validate_evidence_manifest(root)

    def test_file_record_rejects_intermediate_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            root = base / "root"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            _write(outside / "payload", b"secret")
            (root / "linked").symlink_to(outside, target_is_directory=True)
            row = {
                "path": "linked/payload",
                "bytes": 6,
                "sha256": provenance.sha256_file(outside / "payload"),
            }
            with self.assertRaisesRegex(provenance.Goal5844EvidenceError, "escapes"):
                provenance.validate_file_record(root, row, "attack")

    def test_controller_validates_real_pyoptix_receipt_projection(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            receipt_path = _make_pyoptix_receipt(root / "pyoptix")
            receipt = provenance.validate_pyoptix_build_receipt(receipt_path)
            device_source = root / "matched_device.cu"
            native = root / "native.so"
            _write(device_source, b"// source\n")
            _write(native, b"native")
            extension = receipt_path.parent / str(
                receipt["installed"]["loaded_extension"]["path"]
            )
            source_identity = {
                "path": "/pod/upstream/otk-pyoptix",
                "commit": PYOPTIX_COMMIT,
                "tree": PYOPTIX_TREE,
                "status": "",
                "clean": True,
            }
            args = SimpleNamespace(
                warmups=1,
                repetitions=3,
                layer_repetitions=1,
                native=native,
                device_source=device_source,
                optix_sdk=OPTIX_API,
                pyoptix_build_receipt=receipt_path,
            )
            row: dict[str, object] = {
                "schema": "rtdl.goal5844.compact_execution.worker.v2",
                "status": "PASS__INTERNAL_ENGINEERING_WORKER",
                "source_commit": SOURCE_COMMIT,
                "arm": comparison.PYOPTIX_ARM,
                "block": 0,
                "python": "3.12.11",
                "hardware": {"gpu": "synthetic"},
                "task": TRIANGLE_TASK,
                "query_count": 16_384,
                "expected_scalar": 65_530,
                "warmups": 1,
                "repetitions": 3,
                "measurements": {
                    "steady_public": _timing([100, 102, 104]),
                    "attribution": None,
                    "identity": {
                        "device_source_sha256": provenance.sha256_file(device_source),
                        "optix_api_version": OPTIX_API,
                        "pyoptix_repository_commit": PYOPTIX_COMMIT,
                        "pyoptix_source": source_identity,
                        "loaded_extension": {
                            "path": str(extension),
                            "bytes": extension.stat().st_size,
                            "sha256": provenance.sha256_file(extension),
                        },
                        "pyoptix_build_receipt": {
                            "path": str(receipt_path),
                            "bytes": receipt_path.stat().st_size,
                            "sha256": provenance.sha256_file(receipt_path),
                            "receipt_sha256": receipt["receipt_sha256"],
                            "wheel_sha256": receipt["wheel"]["file"]["sha256"],
                            "extension_sha256": receipt["wheel"]["extension_sha256"],
                        },
                    },
                    "evidence": {
                        "latest_public_output": {
                            "device_status": 0,
                            "weighted_sum": 65_530,
                        }
                    },
                },
                "claim_boundary": {
                    "engineering_evidence_only": True,
                    "public_or_manuscript_claim_authorized": False,
                    "external_review_complete": False,
                },
            }
            row["result_sha256"] = digest(row)
            comparison._validate_worker_result(
                row,
                args=args,
                arm=comparison.PYOPTIX_ARM,
                block=0,
                source_commit=SOURCE_COMMIT,
            )
            forged = copy.deepcopy(row)
            forged["measurements"]["identity"]["loaded_extension"]["sha256"] = "f" * 64
            forged.pop("result_sha256")
            forged["result_sha256"] = digest(forged)
            with self.assertRaisesRegex(RuntimeError, "provenance"):
                comparison._validate_worker_result(
                    forged,
                    args=args,
                    arm=comparison.PYOPTIX_ARM,
                    block=0,
                    source_commit=SOURCE_COMMIT,
                )

    def test_offline_verifier_recomputes_complete_synthetic_result(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root, _ = _make_result_root(Path(name))
            with mock.patch.object(comparison, "_validate_worker_result"):
                result = verifier.verify_result_root(
                    root, expected_source_commit=SOURCE_COMMIT
                )
            self.assertEqual(
                result["status"],
                "PASS__DOWNLOADED_RESULT_RECOMPUTED_FROM_HASHED_PAYLOADS",
            )
            self.assertEqual(result["worker_count"], 8)

    def test_offline_verifier_rejects_resealed_foreign_builder(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root, _ = _make_result_root(Path(name))
            manifest_path = root / provenance.EVIDENCE_MANIFEST_NAME
            manifest_path.unlink()
            summary_path = root / "SUMMARY.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            receipt_path = root / summary["provenance"]["pyoptix_build_receipt"]["path"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            builder = receipt_path.parent / receipt["builder"]["path"]
            builder.write_bytes(b"foreign but self-resealed builder\n")
            receipt["builder"] = provenance.file_record(builder, receipt_path.parent)
            receipt.pop("receipt_sha256")
            receipt["receipt_sha256"] = provenance.digest(receipt)
            receipt_path.write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary["provenance"]["pyoptix_build_receipt"] = provenance.file_record(
                receipt_path, root
            )
            summary.pop("result_sha256")
            summary["result_sha256"] = digest(summary)
            summary_path.write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            provenance.write_evidence_manifest(root)
            with self.assertRaisesRegex(
                provenance.Goal5844EvidenceError, "current source commit"
            ):
                verifier.verify_result_root(root, expected_source_commit=SOURCE_COMMIT)

    def test_resealed_worker_tamper_fails_summary_recomputation(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root, _ = _make_result_root(Path(name))
            manifest = root / provenance.EVIDENCE_MANIFEST_NAME
            manifest.unlink()
            worker_path = min((root / "workers").glob("*.json"))
            row = json.loads(worker_path.read_text(encoding="utf-8"))
            row["measurements"]["steady_public"] = _timing([900, 902, 904])
            row.pop("result_sha256")
            row["result_sha256"] = digest(row)
            worker_path.write_text(
                json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            provenance.write_evidence_manifest(root)
            with (
                mock.patch.object(comparison, "_validate_worker_result"),
                self.assertRaisesRegex(
                    provenance.Goal5844EvidenceError, "does not recompute"
                ),
            ):
                verifier.verify_result_root(root, expected_source_commit=SOURCE_COMMIT)

    def test_schedule_is_balanced_and_deterministic(self) -> None:
        schedule = comparison.expected_schedule(8)
        self.assertEqual(len(schedule), 16)
        for block in range(8):
            rows = [item for item in schedule if item["block"] == block]
            self.assertEqual({item["arm"] for item in rows}, set(worker.ARMS))
            self.assertNotEqual(rows[0]["arm"], rows[1]["arm"])
            if block:
                previous = [item for item in schedule if item["block"] == block - 1]
                self.assertNotEqual(rows[0]["arm"], previous[0]["arm"])

    def test_gpu_probe_explicitly_selects_physical_gpu_zero(self) -> None:
        completed = SimpleNamespace(stdout="RTX A4000, GPU-id, 570.0, 16384, 8.6\n")
        with mock.patch.object(worker.subprocess, "run", return_value=completed) as run:
            value = worker._hardware()
        self.assertEqual(value["compute_capability"], COMPUTE_CAPABILITY)
        self.assertIn("--id=0", run.call_args.args[0])

    def test_remote_command_fetches_exact_commit_and_runs_one_entrypoint(self) -> None:
        command = launcher.build_remote_command(
            repository_url="https://github.com/rubaolee/rtdl",
            expected_commit=SOURCE_COMMIT,
            remote_checkout="/workspace/source path",
            remote_output="/workspace/result path",
        )
        self.assertIn(f"fetch -q --depth 1 origin {SOURCE_COMMIT}", command)
        self.assertIn("goal5844_pod_prepare_and_run.sh", command)
        self.assertNotIn("checkout main", command)
        self.assertNotIn("rm -rf", command)

    def test_return_archive_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            archive_path = root / "attack.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                info = tarfile.TarInfo("../escape")
                payload = b"attack"
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                launcher._safe_extract(archive_path, root / "output")

    def test_return_archive_rejects_special_members(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            archive_path = root / "attack.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                info = tarfile.TarInfo("named-pipe")
                info.type = tarfile.FIFOTYPE
                archive.addfile(info)
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                launcher._safe_extract(archive_path, root / "output")

    def test_return_archive_rejects_normalized_duplicate_members(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            archive_path = root / "attack.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                for member_name in ("payload", "./payload"):
                    info = tarfile.TarInfo(member_name)
                    payload = member_name.encode("ascii")
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))
            destination = root / "output"
            with self.assertRaisesRegex(RuntimeError, "unsafe"):
                launcher._safe_extract(archive_path, destination)
            self.assertFalse(destination.exists())

    def test_return_archive_accepts_canonical_regular_tree(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            archive_path = root / "result.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                directory = tarfile.TarInfo("logs/")
                directory.type = tarfile.DIRTYPE
                archive.addfile(directory)
                payload = b"verified\n"
                info = tarfile.TarInfo("logs/result.txt")
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            destination = root / "output"
            launcher._safe_extract(archive_path, destination)
            self.assertEqual(
                (destination / "logs" / "result.txt").read_bytes(), payload
            )

    def test_repository_escape_check_resolves_symbolic_parent(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            linked = Path(name) / "repo"
            linked.symlink_to(comparison.ROOT, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "outside the Git tree"):
                comparison._require_outside_repository(
                    linked / "forbidden-result", "test output"
                )

    def test_pod_script_has_no_gpu_model_or_single_driver_requirement(self) -> None:
        path = comparison.ROOT / "scripts" / "goal5844_pod_prepare_and_run.sh"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("RTX 4000", text)
        self.assertNotIn("R570", text)
        self.assertNotIn("astral.sh/uv/install.sh", text)
        self.assertIn('UV_VERSION="0.12.10"', text)
        self.assertIn("'pip==26.2.1'", text)
        self.assertIn("'cmake==3.31.6'", text)
        self.assertIn("'packaging==26.3'", text)
        self.assertIn("'pathspec==1.1.1'", text)
        self.assertIn("'virtualenv==20.35.4'", text)
        self.assertIn("'distlib==0.4.0'", text)
        self.assertIn("pip_upgrade_install_report.json", text)
        self.assertIn("pip uninstall -y setuptools", text)
        self.assertIn("compatibility.py", text)
        self.assertIn("goal5844_build_install_pyoptix.py", text)
        self.assertIn("goal5844_verify_gpu_engineering_result.py", text)
        self.assertIn("FAILED_STAGE.txt", text)
        self.assertIn("dependency_install_report.json", text)
        self.assertIn("active compute processes", text)
        self.assertIn('[[ -n "$NVCC" ]] && break', text)
        self.assertIn(comparison.V8_SYMBOL, text)


if __name__ == "__main__":
    unittest.main()
