from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts/build_v4_optix_native_snapshot.py"
WORKLOADS_PATH = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


def _builder():
    spec = importlib.util.spec_from_file_location(
        "v4_embedded_aabb_ptx_builder_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("native snapshot builder cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EmbeddedAabbIndexPtxContractTest(unittest.TestCase):
    def test_extracted_source_contains_all_generic_entry_points(self) -> None:
        module = _builder()
        source = module._extract_aabb_index_count_source()
        self.assertTrue(source.endswith(b"\n"))
        for symbol in module._AABB_INDEX_PTX_SYMBOLS:
            self.assertIn(symbol.encode("ascii"), source)
        self.assertNotIn(b"librts", source.lower())
        self.assertNotIn(b"parks", source.lower())

    def test_generated_translation_unit_preserves_exact_ptx_bytes(self) -> None:
        module = _builder()
        ptx = b".version 8.5\n.target sm_86\n.address_size 64\n\x00\xff"
        generated = module._embedded_ptx_translation_unit(ptx).decode("ascii")
        encoded = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-f]{2})", generated))
        self.assertEqual(encoded, ptx)
        self.assertIn("visibility(\"hidden\")", generated)
        self.assertIn("rtdl_optix_embedded_aabb_index_count_ptx_v1", generated)

    def test_device_reduction_source_and_binary_embedding_are_app_free(self) -> None:
        module = _builder()
        source = module._extract_device_u32_sum_u64_source()
        self.assertIn(module._DEVICE_U32_SUM_U64_SYMBOL.encode("ascii"), source)
        self.assertNotIn(b"librts", source.lower())
        self.assertNotIn(b"aabb", source.lower())
        cubin = b"\x7fELF\x00\xffrtdl_device_u32_sum_u64"
        generated = module._embedded_binary_translation_unit(
            cubin,
            function_name="rtdl_optix_embedded_device_u32_sum_u64_cubin_v1",
            array_name="cubin",
        ).decode("ascii")
        encoded = bytes(
            int(value, 16)
            for value in re.findall(r"0x([0-9a-f]{2})", generated)
        )
        self.assertEqual(encoded, cubin)
        self.assertIn(
            "rtdl_optix_embedded_device_u32_sum_u64_cubin_v1", generated)

    def test_prepare_compiles_binds_and_refuses_reuse(self) -> None:
        module = _builder()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compiler = root / "fake-nvcc"
            entries = "\\n".join(
                f".visible .entry {symbol}() {{ ret; }}"
                for symbol in module._AABB_INDEX_PTX_SYMBOLS
            )
            compiler.write_text(
                "#!/bin/sh\n"
                "out=\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = -o ]; then shift; out=$1; fi\n"
                "  shift\n"
                "done\n"
                f"printf '%s\\n' '{entries}' > \"$out\"\n"
                "printf 'fake deterministic compile\\n'\n",
                encoding="utf-8",
            )
            compiler.chmod(0o755)
            host_compiler = root / "fake-g++"
            host_compiler.write_text("unused\n", encoding="utf-8")
            output_directory = root / "embedded"
            translation_unit, evidence = (
                module._prepare_embedded_aabb_index_count_ptx(
                    directory=output_directory,
                    nvcc=compiler,
                    host_compiler=host_compiler,
                    optix_include=root / "optix/include",
                    cuda_include=root / "cuda/include",
                    capability=(8, 6),
                )
            )
            self.assertEqual(
                evidence["schema"], "rtdl.v4.embedded_optix_program.v1")
            self.assertFalse(evidence["runtime_source_compilation_required"])
            for path_key, sha_key in (
                ("source_path", "source_sha256"),
                ("ptx_path", "ptx_sha256"),
                ("translation_unit_path", "translation_unit_sha256"),
                ("compile_log_path", "compile_log_sha256"),
            ):
                path = Path(evidence[path_key])
                self.assertTrue(path.is_file())
                self.assertEqual(module._sha(path), evidence[sha_key])
            self.assertEqual(translation_unit, Path(evidence["translation_unit_path"]))
            with self.assertRaises(FileExistsError):
                module._prepare_embedded_aabb_index_count_ptx(
                    directory=output_directory,
                    nvcc=compiler,
                    host_compiler=host_compiler,
                    optix_include=root / "optix/include",
                    cuda_include=root / "cuda/include",
                    capability=(8, 6),
                )

    def test_runtime_prefers_embedded_program_and_keeps_legacy_fallback(self) -> None:
        source = WORKLOADS_PATH.read_text(encoding="utf-8")
        start = source.index("static std::string aabb_index_count_2d_ptx()")
        end = source.index("static void ensure_aabb_index_count_2d_pipeline", start)
        body = source[start:end]
        embedded = body.index("rtdl_optix_embedded_aabb_index_count_ptx_v1")
        fallback = body.index("compile_to_ptx")
        self.assertLess(embedded, fallback)
        for symbol in (
            "__raygen__aabb_index_query",
            "__miss__aabb_index_miss",
            "__intersection__aabb_index_exact",
            "__anyhit__aabb_index_count",
        ):
            self.assertIn(symbol, body)

    def test_prepare_embeds_device_reduction_cubin_and_refuses_reuse(self) -> None:
        module = _builder()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compiler = root / "fake-nvcc"
            compiler.write_text(
                "#!/bin/sh\n"
                "out=\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = -o ]; then shift; out=$1; fi\n"
                "  shift\n"
                "done\n"
                "printf '\\177ELFrtdl_device_u32_sum_u64' > \"$out\"\n"
                "printf 'fake deterministic CUBIN compile\\n'\n",
                encoding="utf-8",
            )
            compiler.chmod(0o755)
            host_compiler = root / "fake-g++"
            host_compiler.write_text("unused\n", encoding="utf-8")
            output_directory = root / "embedded-reduction"
            translation_unit, evidence = (
                module._prepare_embedded_device_u32_sum_u64_cubin(
                    directory=output_directory,
                    nvcc=compiler,
                    host_compiler=host_compiler,
                    optix_include=root / "optix/include",
                    cuda_include=root / "cuda/include",
                    capability=(8, 6),
                )
            )
            self.assertEqual(
                evidence["schema"], "rtdl.v4.embedded_cuda_program.v1")
            self.assertEqual(
                evidence["entry_points"], [module._DEVICE_U32_SUM_U64_SYMBOL])
            self.assertFalse(evidence["runtime_source_compilation_required"])
            for path_key, sha_key in (
                ("source_path", "source_sha256"),
                ("cubin_path", "cubin_sha256"),
                ("translation_unit_path", "translation_unit_sha256"),
                ("compile_log_path", "compile_log_sha256"),
            ):
                path = Path(evidence[path_key])
                self.assertTrue(path.is_file())
                self.assertEqual(module._sha(path), evidence[sha_key])
            self.assertEqual(translation_unit, Path(evidence["translation_unit_path"]))
            with self.assertRaises(FileExistsError):
                module._prepare_embedded_device_u32_sum_u64_cubin(
                    directory=output_directory,
                    nvcc=compiler,
                    host_compiler=host_compiler,
                    optix_include=root / "optix/include",
                    cuda_include=root / "cuda/include",
                    capability=(8, 6),
                )

    def test_runtime_prefers_embedded_reduction_and_keeps_legacy_fallback(self) -> None:
        source = WORKLOADS_PATH.read_text(encoding="utf-8")
        start = source.index("static std::string device_u32_sum_u64_cubin()")
        end = source.index("static void ensure_device_u32_sum_u64", start)
        body = source[start:end]
        embedded = body.index(
            "rtdl_optix_embedded_device_u32_sum_u64_cubin_v1")
        fallback = body.index("compile_to_cubin")
        self.assertLess(embedded, fallback)
        self.assertIn("bytes[0] != 0x7fu", body)

    def test_build_manifest_binds_generated_program_artifacts(self) -> None:
        source = BUILDER_PATH.read_text(encoding="utf-8")
        for field in (
            '"source_sha256"',
            '"ptx_sha256"',
            '"translation_unit_sha256"',
            '"compile_log_sha256"',
            '"runtime_source_compilation_required": False',
            '"embedded_optix_programs"',
            '"embedded_cuda_programs"',
            '"runtime_compiler_attempts_required_by_embedded_aabb_program": 0',
        ):
            self.assertIn(field, source)


if __name__ == "__main__":
    unittest.main()
