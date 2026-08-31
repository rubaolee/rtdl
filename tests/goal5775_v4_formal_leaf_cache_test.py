from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import (
    FORMAL_NUMBA_CACHE_ENV,
    FORMAL_NUMBA_CACHE_MANIFEST_ENV,
    FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV,
    CallbackCodegenError,
    GeneratedFormalNumbaLeaf,
    compile_formal_numba_leaf_isolated,
    materialize_formal_numba_leaf_cache_manifest,
)


class Goal5775FormalLeafCacheTest(unittest.TestCase):
    def leaf(self) -> GeneratedFormalNumbaLeaf:
        source = "def rtdl_v4_test():\n    return\n"
        return GeneratedFormalNumbaLeaf(
            schema="rtdl.v4.generated_formal_numba_leaf.v1",
            role=CallbackRole.MAKE_RAY,
            abi_name="rtdl_v4_test",
            parameter_order=(),
            parameter_types=(),
            generated_source=source,
            generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
            callback_ir_sha256="1" * 64,
            callback_effect_digest="2" * 64,
            callback_abi_sha256="3" * 64,
            nonce_word=17,
            numeric_mode="strict",
            error_sites=(),
            compiler_function_count=1,
        )

    @staticmethod
    def ptx() -> str:
        return (
            ".version 8.0\n.target sm_61\n.address_size 64\n"
            ".visible .func rtdl_v4_test() {\n    ret;\n}\n"
        )

    def compile(self, leaf: GeneratedFormalNumbaLeaf):
        return compile_formal_numba_leaf_isolated(
            leaf,
            compute_capability=(6, 1),
            accepted_ptx_isa=("8.0", "8.9"),
            allowed_external_symbols=frozenset(),
            expected_python_version=platform.python_version(),
            expected_numba_version="0.65.1",
            expected_numpy_version="2.4.4",
            python_executable=sys.executable,
        )

    def compiler(self):
        def run(argv, **kwargs):
            request = json.loads(Path(argv[-2]).read_text(encoding="utf-8"))
            response = {
                "schema": "rtdl.v4.numba_compile_response.v1",
                "generated_source_sha256": request["generated_source_sha256"],
                "ptx": self.ptx(),
                "numba_version": "0.65.1",
                "numpy_version": "2.4.4",
                "python_version": platform.python_version(),
                "cuda_available_was_queried": False,
                "explicit_compute_capability": [6, 1],
            }
            Path(argv[-1]).write_text(json.dumps(response), encoding="utf-8")
            return mock.Mock(returncode=0, stdout="", stderr="")

        return mock.Mock(side_effect=run)

    def test_exact_entry_is_compiled_once_then_reaudited(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            os.environ, {FORMAL_NUMBA_CACHE_ENV: directory}, clear=False
        ):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                first = self.compile(self.leaf())
                second = self.compile(self.leaf())
            self.assertEqual(compiler.call_count, 1)
            self.assertEqual(first, second)
            entries = [item for item in Path(directory).iterdir() if item.is_dir()]
            self.assertEqual(len(entries), 1)
            self.assertEqual([item.name for item in entries[0].iterdir()], ["artifact.json"])

    def test_ptx_mutation_fails_closed_instead_of_recompiling(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            os.environ, {FORMAL_NUMBA_CACHE_ENV: directory}, clear=False
        ):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                self.compile(self.leaf())
            artifact_path = next(Path(directory).glob("*/artifact.json"))
            document = json.loads(artifact_path.read_text(encoding="utf-8"))
            document["artifact"]["ptx"] += "// mutation\n"
            artifact_path.write_text(json.dumps(document), encoding="utf-8")
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run") as forbidden:
                with self.assertRaises(Exception):
                    self.compile(self.leaf())
                forbidden.assert_not_called()

    def test_cache_key_binds_target_and_toolchain(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            os.environ, {FORMAL_NUMBA_CACHE_ENV: directory}, clear=False
        ):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                self.compile(self.leaf())
                with self.assertRaises(CallbackCodegenError):
                    compile_formal_numba_leaf_isolated(
                        self.leaf(),
                        compute_capability=(8, 9),
                        accepted_ptx_isa=("8.0", "8.9"),
                        allowed_external_symbols=frozenset(),
                        expected_python_version=platform.python_version(),
                        expected_numba_version="0.65.1",
                        expected_numpy_version="2.4.4",
                        python_executable=sys.executable,
                    )
            self.assertEqual(compiler.call_count, 2)

    def test_cache_is_disabled_without_explicit_root(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                self.compile(self.leaf())
                self.compile(self.leaf())
            self.assertEqual(compiler.call_count, 2)

    def test_sealed_manifest_binds_exact_entry_bytes_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            os.environ,
            {
                FORMAL_NUMBA_CACHE_ENV: directory,
                FORMAL_NUMBA_CACHE_MANIFEST_ENV: "",
                FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV: "",
            },
            clear=False,
        ):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                expected = self.compile(self.leaf())
            manifest = Path(directory).parent / (Path(directory).name + "-manifest.json")
            materialize_formal_numba_leaf_cache_manifest(directory, manifest)
            authority = {
                FORMAL_NUMBA_CACHE_MANIFEST_ENV: str(manifest),
                FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV: hashlib.sha256(
                    manifest.read_bytes()).hexdigest(),
            }
            with mock.patch.dict(os.environ, authority, clear=False), mock.patch(
                "rtdsl.v4_callback_numba_codegen.subprocess.run"
            ) as forbidden:
                self.assertEqual(expected, self.compile(self.leaf()))
                forbidden.assert_not_called()

                artifact_path = next(Path(directory).glob("*/artifact.json"))
                document = json.loads(artifact_path.read_text(encoding="utf-8"))
                document["artifact"]["ptx"] += "// attacker\n"
                document["artifact"]["ptx_sha256"] = hashlib.sha256(
                    document["artifact"]["ptx"].encode()).hexdigest()
                artifact_path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaises(CallbackCodegenError) as caught:
                    self.compile(self.leaf())
                self.assertEqual(caught.exception.code, "formal_leaf_cache_manifest_entry")
                forbidden.assert_not_called()

    def test_manifest_rejects_extra_cache_members_and_missing_target(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            os.environ,
            {
                FORMAL_NUMBA_CACHE_ENV: directory,
                FORMAL_NUMBA_CACHE_MANIFEST_ENV: "",
                FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV: "",
            },
            clear=False,
        ):
            compiler = self.compiler()
            with mock.patch("rtdsl.v4_callback_numba_codegen.subprocess.run", compiler):
                self.compile(self.leaf())
            extra = Path(directory) / "unexpected"
            extra.mkdir()
            with self.assertRaises(CallbackCodegenError):
                materialize_formal_numba_leaf_cache_manifest(
                    directory, Path(directory).parent / "invalid-manifest.json"
                )
            extra.rmdir()
            manifest = Path(directory).parent / (Path(directory).name + "-manifest.json")
            materialize_formal_numba_leaf_cache_manifest(directory, manifest)
            with mock.patch.dict(os.environ, {
                FORMAL_NUMBA_CACHE_MANIFEST_ENV: str(manifest),
                FORMAL_NUMBA_CACHE_MANIFEST_SHA256_ENV: hashlib.sha256(
                    manifest.read_bytes()).hexdigest(),
            }, clear=False), mock.patch(
                "rtdsl.v4_callback_numba_codegen.subprocess.run"
            ) as forbidden:
                with self.assertRaises(CallbackCodegenError) as caught:
                    compile_formal_numba_leaf_isolated(
                        self.leaf(), compute_capability=(8, 9),
                        accepted_ptx_isa=("8.0", "8.9"),
                        allowed_external_symbols=frozenset(),
                        expected_python_version=platform.python_version(),
                        expected_numba_version="0.65.1",
                        expected_numpy_version="2.4.4",
                        python_executable=sys.executable,
                    )
                self.assertEqual(caught.exception.code, "formal_leaf_cache_manifest_miss")
                forbidden.assert_not_called()


if __name__ == "__main__":
    unittest.main()
