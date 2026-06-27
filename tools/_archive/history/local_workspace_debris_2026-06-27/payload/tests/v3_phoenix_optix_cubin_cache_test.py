import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"


class V3PhoenixOptixCubinCacheTest(unittest.TestCase):
    def test_cubin_compile_path_has_disk_cache_controls(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        for phrase in (
            "RTDL_OPTIX_CUBIN_CACHE_DIR",
            "RTDL_OPTIX_DISABLE_CUBIN_CACHE",
            "cubin_cache_path(",
            "read_cached_cubin(",
            "write_cached_cubin(",
            "compile_to_cubin_with_nvcc(",
        ):
            self.assertIn(phrase, core)

    def test_cache_key_includes_source_options_and_arch(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index("static std::filesystem::path cubin_cache_path")
        end = core.index("static std::string read_cached_cubin", start)
        block = core[start:end]

        for phrase in (
            "rtdl_optix_cubin_cache_v1",
            "cuda_src",
            "name",
            "arch",
            "include_opts",
            "extra_opts",
            ".cubin",
        ):
            self.assertIn(phrase, block)

    def test_compile_to_cubin_reads_cache_before_nvcc_and_writes_after(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index("static std::string compile_to_cubin(")
        end = core.index("std::string compile_to_ptx", start)
        block = core[start:end]

        self.assertLess(block.index("read_cached_cubin"), block.index("compile_to_cubin_with_nvcc"))
        self.assertLess(block.index("compile_to_cubin_with_nvcc"), block.index("write_cached_cubin"))
        self.assertIn("default_cuda_cubin_arch()", block)
        self.assertIn("RTDL_OPTIX_DISABLE_CUBIN_CACHE", block)

    def test_prelude_documents_cross_process_cubin_cache(self) -> None:
        text = PRELUDE.read_text(encoding="utf-8")
        self.assertIn("content-addressed disk cache", text)
        self.assertIn("same source, options, and target arch", text)


if __name__ == "__main__":
    unittest.main()
