from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from experiments.goal5848_strong_baseline import device_artifacts
from experiments.goal5848_strong_baseline.contracts import digest
from scripts import goal5848_build_transaction_authority as authority


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


class Goal5848DeviceArtifactProvenanceTest(unittest.TestCase):
    def _git_repository(self, root: Path, files: dict[str, bytes]) -> str:
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        _git(root, "config", "user.email", "goal5848@example.invalid")
        _git(root, "config", "user.name", "Goal5848 Test")
        for relative, payload in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        _git(root, "add", ".")
        _git(root, "commit", "-qm", "Create fixture")
        return _git(root, "rev-parse", "HEAD")

    def _fixture(self, root: Path) -> dict[str, object]:
        root.mkdir(parents=True, exist_ok=True)
        repository = root / "source"
        source_commit = self._git_repository(
            repository,
            {
                device_artifacts.DEVICE_SOURCE_RELATIVE.as_posix(): b"device\n",
                device_artifacts.COMPACTION_SOURCE_RELATIVE.as_posix(): (
                    b"compaction\n"
                ),
                device_artifacts.COMPILER_CHILD_RELATIVE.as_posix(): b"child\n",
            },
        )
        optix = root / "optix"
        self._git_repository(
            optix,
            {"include/optix.h": b"#define OPTIX_VERSION 80000\n"},
        )
        optix_include = (optix / "include").resolve()
        cuda_include = root / "cuda-include"
        cuda_include.mkdir()
        artifact_root = root / "artifacts"
        artifact_root.mkdir()
        ptx = artifact_root / "matched.ptx"
        ptx.write_bytes(b"// frozen\n.version 8.0\n.target sm_89\n")
        cubin = artifact_root / "compaction.cubin"
        cubin.write_bytes(b"\x7fELFfrozen")
        nvrtc = root / "libnvrtc.so.12"
        nvrtc.write_bytes(b"nvrtc")
        builtins = root / "libnvrtc-builtins.so.12"
        builtins.write_bytes(b"builtins")
        loaded_nvrtc = {
            "library": {
                **device_artifacts._file_identity(nvrtc),
                "canonical_regular_file": True,
                "symlink": False,
            },
            "builtins": {
                **device_artifacts._file_identity(builtins),
                "canonical_regular_file": True,
                "symlink": False,
            },
            "version": [12, 9],
        }
        sources = {
            "device_source": device_artifacts._source_identity(
                repository, device_artifacts.DEVICE_SOURCE_RELATIVE
            ),
            "compaction_source": device_artifacts._source_identity(
                repository, device_artifacts.COMPACTION_SOURCE_RELATIVE
            ),
            "compiler_child": device_artifacts._source_identity(
                repository, device_artifacts.COMPILER_CHILD_RELATIVE
            ),
        }
        outputs = {
            "precompiled_ptx": device_artifacts._file_identity(ptx),
            "compaction_cubin": device_artifacts._file_identity(cubin),
        }
        builder_pid = 500
        children = {}
        processes = {}
        for index, (label, mode, source_label, output_label) in enumerate(
            (
                ("ptx", "ptx", "device_source", "precompiled_ptx"),
                (
                    "compaction_cubin",
                    "cubin",
                    "compaction_source",
                    "compaction_cubin",
                ),
            )
        ):
            options, target = device_artifacts._expected_child_options(
                mode=mode,
                compute_capability="8.9",
                optix_include=optix_include,
                cuda_include=cuda_include.resolve(),
            )
            source = sources[source_label]
            child = {
                "schema": device_artifacts.CHILD_SCHEMA,
                "status": device_artifacts.CHILD_STATUS,
                "pid": 600 + index,
                "parent_pid": builder_pid,
                "argv": ["child.py", "--mode", mode],
                "cwd": str(repository.resolve()),
                "mode": mode,
                "source": {
                    "path": source["path"],
                    "bytes": source["bytes"],
                    "sha256": source["sha256"],
                },
                "include_roots": {
                    "optix": str(optix_include) if mode == "ptx" else None,
                    "cuda": (
                        str(cuda_include.resolve()) if mode == "ptx" else None
                    ),
                },
                "compute_capability": "8.9",
                "compile_options": options,
                "target": target,
                "product": outputs[output_label],
                "loaded_nvrtc": copy.deepcopy(loaded_nvrtc),
                "clock_read_count": 0,
                "gpu_kernel_launch_count": 0,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
            }
            child["receipt_sha256"] = digest(child)
            child_path = artifact_root / f"{label}.child.json"
            _write(child_path, child)
            stdout = json.dumps(
                {
                    "pid": child["pid"],
                    "product_sha256": child["product"]["sha256"],
                    "receipt_sha256": child["receipt_sha256"],
                    "status": device_artifacts.CHILD_STATUS,
                },
                sort_keys=True,
            ) + "\n"
            children[label] = child
            processes[label] = {
                "command": [str(Path(sys.executable).resolve()), *child["argv"]],
                "exit_code": 0,
                "stdout_utf8": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                "stderr_utf8": "",
                "stderr_sha256": hashlib.sha256(b"").hexdigest(),
                "child_receipt_file": device_artifacts._file_identity(child_path),
            }
        python_path = Path(sys.executable).resolve()
        value = {
            "schema": device_artifacts.DEVICE_ARTIFACT_RECEIPT_SCHEMA,
            "status": device_artifacts.DEVICE_ARTIFACT_RECEIPT_STATUS,
            "source_identity": device_artifacts._git_identity(repository),
            "sources": sources,
            "python": {
                "invocation_path": str(python_path),
                **device_artifacts._file_identity(python_path),
            },
            "optix_headers_identity": device_artifacts._git_identity(optix),
            "optix_include_path": str(optix_include),
            "cuda_include_path": str(cuda_include.resolve()),
            "expected_optix_sdk": "8.0.0",
            "compute_capability": "8.9",
            "compute_architecture": "compute_89",
            "sm_architecture": "sm_89",
            "builder_pid": builder_pid,
            "compiler_processes": processes,
            "compiler_receipts": children,
            "outputs": outputs,
            "derivation_scope": (
                "SOURCE_AND_PRODUCT_BOUND__NOT_A_HERMETIC_CUDA_HEADER_CLOSURE"
            ),
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
            "retry_count": 0,
            "discard_count": 0,
            "public_or_manuscript_claim_authorized": False,
        }
        value["receipt_sha256"] = digest(value)
        receipt = artifact_root / "device_artifacts.json"
        _write(receipt, value)
        return {
            "repository": repository,
            "source_commit": source_commit,
            "ptx": ptx,
            "cubin": cubin,
            "nvrtc": nvrtc,
            "receipt": receipt,
            "value": value,
        }

    def test_complete_receipt_and_independent_recount_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            observed = device_artifacts.load_device_artifact_receipt(
                fixture["receipt"],
                precompiled_ptx=fixture["ptx"],
                compaction_cubin=fixture["cubin"],
                expected_source_commit=fixture["source_commit"],
                expected_optix_sdk="8.0.0",
                expected_compute_capability="8.9",
                repository_root=fixture["repository"],
            )
            self.assertEqual(
                observed["status"], device_artifacts.DEVICE_ARTIFACT_RECEIPT_STATUS
            )
            artifacts = {
                "device_artifact_build_receipt": authority._file_identity(
                    fixture["receipt"]
                ),
                "precompiled_ptx": authority._file_identity(fixture["ptx"]),
                "compaction_cubin": authority._file_identity(fixture["cubin"]),
            }
            independent = authority._validate_device_artifacts_independently(
                artifacts,
                expected_source_commit=fixture["source_commit"],
                expected_compute_capability="8.9",
            )
            self.assertEqual(independent, artifacts["device_artifact_build_receipt"])

    def test_product_nvrtc_and_target_mutations_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            common = {
                "precompiled_ptx": fixture["ptx"],
                "compaction_cubin": fixture["cubin"],
                "expected_source_commit": fixture["source_commit"],
                "expected_optix_sdk": "8.0.0",
                "expected_compute_capability": "8.9",
                "repository_root": fixture["repository"],
            }
            fixture["ptx"].write_bytes(b"// changed\n.version 8.0\n")
            with self.assertRaisesRegex(RuntimeError, "output bytes"):
                device_artifacts.load_device_artifact_receipt(
                    fixture["receipt"], **common
                )
            fixture = self._fixture(Path(temporary) / "second")
            common.update(
                {
                    "precompiled_ptx": fixture["ptx"],
                    "compaction_cubin": fixture["cubin"],
                    "expected_source_commit": fixture["source_commit"],
                    "repository_root": fixture["repository"],
                }
            )
            fixture["nvrtc"].write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "NVRTC bytes"):
                device_artifacts.load_device_artifact_receipt(
                    fixture["receipt"], **common
                )
            fixture = self._fixture(Path(temporary) / "third")
            common.update(
                {
                    "precompiled_ptx": fixture["ptx"],
                    "compaction_cubin": fixture["cubin"],
                    "expected_source_commit": fixture["source_commit"],
                    "repository_root": fixture["repository"],
                    "expected_compute_capability": "8.6",
                }
            )
            with self.assertRaisesRegex(RuntimeError, "target differs"):
                device_artifacts.load_device_artifact_receipt(
                    fixture["receipt"], **common
                )


if __name__ == "__main__":
    unittest.main()
