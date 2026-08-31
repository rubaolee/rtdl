from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import goal5793_x1_capture_exact_environment as capture
from scripts.goal5793_x1_canonical import seal_document


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ExactEnvironmentCaptureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="goal5793_x1_env_capture_")
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "source"
        self.source_src = self.source / "src"
        self.cuda = self.root / "cuda"
        self.optix = self.root / "optix"
        self.cache = self.root / "cache"
        self.python_home = self.root / "python_home"
        self.python = self.python_home / "bin/python3.12"
        self.loader = self.python_home / "runtime_deps/ld-linux-x86-64.so.2"
        for directory in (
            self.source_src, self.cuda, self.optix, self.cache,
            self.python.parent, self.loader.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        (self.source_src / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.cuda / "cuda.h").write_text("#define CUDA_VERSION 12000\n", encoding="utf-8")
        (self.optix / "optix.h").write_text("#define OPTIX_VERSION 90000\n", encoding="utf-8")
        (self.optix / "optix_function_table.h").write_text("#define OPTIX_ABI_VERSION 105\n", encoding="utf-8")
        for index in range(12):
            (self.optix / f"header_{index:02d}.h").write_text(f"// {index}\n", encoding="utf-8")
        (self.cache / "artifact.json").write_text("{}\n", encoding="utf-8")
        self.python.write_bytes(b"python")
        self.loader.write_bytes(b"loader")

        self.native_root = self.root / "native"
        self.dependency_root = self.native_root / "goal5793_x1_deps"
        self.dependency_root.mkdir(parents=True)
        self.files: dict[str, Path] = {}
        for name in sorted(capture.EXPECTED_RUNTIME_KEYS | capture.EXPECTED_DLOPEN_KEYS):
            path = self.dependency_root / name
            path.write_bytes((name + "\n").encode("utf-8"))
            self.files[name] = path
        self.linker = self.root / "ld"
        self.native = self.native_root / "librtdl_optix.so"
        self.source_authority = self.root / "source_authority.json"
        self.source_bundle = self.root / "source326.tar.gz"
        self.trace_authority = self.root / "trace_authority.json"
        self.trace_evidence = self.root / "trace.tar.gz"
        self.trace_twin = self.root / "trace_twin.tar.gz"
        for path in (self.linker, self.source_authority, self.source_bundle, self.trace_authority):
            path.write_bytes(path.name.encode("utf-8"))
        self.trace_evidence.write_bytes(b"trace")
        self.trace_twin.write_bytes(b"trace")
        self.build_id = "goal5793-x1-sm61"
        self.gnu_build_id = "a" * 40
        self.native.write_bytes(b"ELF fixture " + self.build_id.encode("ascii"))
        self.environment = {
            "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
            "PYTHONHOME": str(self.python_home), "PYTHONPATH": str(self.source_src),
            "LD_LIBRARY_PATH": str(self.loader.parent), "LD_PRELOAD": None,
            "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1", "PYTHONSAFEPATH": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.request = {
            "schema": capture.REQUEST_SCHEMA, "stage_id": "goal5793-x1-test",
            "python_executable": str(self.python), "python_loader": str(self.loader),
            "python_home": str(self.python_home), "source_root": str(self.source),
            "source_authority_file": str(self.source_authority), "source_bundle": str(self.source_bundle),
            "source_sys_path_entries": [str(self.source_src)], "cuda_entry_header_root": str(self.cuda),
            "optix_header_root": str(self.optix), "linker": str(self.linker),
            "native_library": str(self.native), "numba_cache_root": str(self.cache),
            "native_trace_authority": str(self.trace_authority),
            "native_trace_evidence": str(self.trace_evidence),
            "native_trace_evidence_twin": str(self.trace_twin),
            "runtime_libraries": {name: str(self.files[name]) for name in capture.EXPECTED_RUNTIME_KEYS},
            "dlopen_libraries": {name: str(self.files[name]) for name in capture.EXPECTED_DLOPEN_KEYS},
            "expected_rtdl_build_id": self.build_id, "expected_gnu_build_id": self.gnu_build_id,
            "expected_cuda_arch": "sm_61", "environment": deepcopy(self.environment),
        }
        self.elf = {
            "dt_needed": sorted(capture.EXPECTED_RUNTIME_KEYS), "rpath": [],
            "runpath": [capture.EXPECTED_RUNPATH], "gnu_build_id": self.gnu_build_id,
        }
        self.trace_document = {
            "source": {"bundle": {"sha256": sha256(self.source_bundle)}},
            "native_rebuilds": {
                "reference_stripped": {"sha256": sha256(self.native)},
                "traced_stripped": {"sha256": sha256(self.native)},
            },
            "top_level_nvcc": {"argv": ["nvcc", "-arch=sm_61"]},
            "surviving_external_inputs": {
                "content_rows": [{"sha256": sha256(self.cuda / "cuda.h")}, {"sha256": sha256(self.linker)}],
                "declared_paths": [
                    {"declared_path": f"/home/lestat/vendor/optix-dev/include/{path.name}", "sha256": sha256(path)}
                    for path in sorted(self.optix.iterdir())
                ],
            },
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self):
        probe = {
            "prefix": str(self.python_home), "executable": str(self.python), "sys_path": [str(self.source_src)],
            "numpy": ["2.4.4", str(self.python_home / "numpy.py")],
            "numba": ["0.65.1", str(self.python_home / "numba.py")],
            "llvmlite": ["0.47.0", str(self.python_home / "llvmlite.py")],
        }
        numba = {
            "root": str(self.cache), "file_count": 44, "total_bytes": 1, "rows": [],
            "rows_sha256": "b" * 64, "validated_artifacts": [],
            "role_counts": capture.EXPECTED_ROLE_COUNTS, "validated_artifact_set_sha256": "c" * 64,
        }
        with patch.object(capture, "_elf_identity", return_value=deepcopy(self.elf)), patch.object(
            capture, "_verify_source_authority", return_value={"file": {}, "source_authority_sha256": "d" * 64, "summary": {}}
        ), patch.object(
            capture, "_verify_trace_authority", return_value=({"authority": {}}, deepcopy(self.trace_document))
        ), patch.object(capture, "_verify_numba_cache", return_value=numba), patch.object(
            capture, "_capture_python_environment", return_value=probe
        ):
            return capture.capture(deepcopy(self.request))

    def test_complete_explicit_fixture_captures_and_seals(self) -> None:
        result = self.build()
        self.assertEqual(
            result["status"],
            "EXACT_TARGET_EXECUTION_ENVIRONMENT_CAPTURED__REVIEW_REQUIRED__NO_EXECUTION_AUTHORIZATION",
        )
        self.assertEqual(
            result["authority_sha256"],
            seal_document(result, seal_field="authority_sha256",
                          domain="rtdl.goal5793.x1.exact_environment_capture", version=2),
        )
        self.assertFalse(result["scope"]["execution_authorized"])
        self.assertEqual(result["scope"]["gpu_calls"], 0)

    def test_ambient_environment_is_rejected_even_if_resealed_upstream(self) -> None:
        self.request["environment"]["LD_LIBRARY_PATH"] = "/ambient"
        with self.assertRaisesRegex(capture.CaptureError, "environment_vector_mismatch"):
            self.build()

    def test_time_like_or_unstructured_build_id_is_rejected(self) -> None:
        self.request["expected_rtdl_build_id"] = "20260822T010203"
        with self.assertRaisesRegex(capture.CaptureError, "deterministic_build_identity_invalid"):
            self.build()

    def test_missing_runtime_dependency_is_rejected(self) -> None:
        self.request["runtime_libraries"].pop("libcuda.so.1")
        with self.assertRaisesRegex(capture.CaptureError, "runtime_library_keyset_mismatch"):
            self.build()

    def test_native_without_relative_runpath_is_rejected(self) -> None:
        self.elf["runpath"] = []
        with self.assertRaisesRegex(capture.CaptureError, "native_dynamic_contract_mismatch"):
            self.build()

    def test_native_with_extra_needed_dependency_is_rejected(self) -> None:
        self.elf["dt_needed"].append("libhostile.so")
        with self.assertRaisesRegex(capture.CaptureError, "native_dynamic_contract_mismatch"):
            self.build()

    def test_empty_numba_cache_is_rejected(self) -> None:
        (self.cache / "artifact.json").unlink()
        with self.assertRaisesRegex(capture.CaptureError, "numba_cache_empty"):
            capture._verify_numba_cache(self.cache, self.source, sha256(self.python))

    def test_symlinked_dependency_is_rejected(self) -> None:
        target = self.files["libcuda.so.1"]
        with patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaisesRegex(capture.CaptureError, "not_explicit_regular_file"):
                capture._absolute_regular(str(target), "runtime_libcuda")


if __name__ == "__main__":
    unittest.main()
