from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/numba_partner_continuation.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal4437_v3_0_m40_numba_cuda_toolchain_autoconfig_2026-06-16.md"

sys.path.insert(0, str(ROOT / "src"))


class Goal4437V30M40NumbaCudaToolchainAutoconfigTest(unittest.TestCase):
    def test_autoconfig_helper_is_exported(self) -> None:
        import rtdsl as rt

        self.assertTrue(hasattr(rt, "configure_numba_cuda_toolchain_environment"))
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "configure_numba_cuda_toolchain_environment",
            "nvidia",
            "cuda_nvcc",
            "NUMBA_CUDA_PREFIX",
            "CUDA_HOME",
            "CUDA_PATH",
            "LD_LIBRARY_PATH",
            "NUMBA_CUDA_DRIVER",
            "ptxas",
        ):
            self.assertIn(phrase, source)
        self.assertIn("configure_numba_cuda_toolchain_environment", init)

    def test_autoconfig_helper_is_environment_only(self) -> None:
        import rtdsl as rt

        result = rt.configure_numba_cuda_toolchain_environment()
        self.assertIn("configured", result)
        self.assertIn("does_not_install_packages", SOURCE.read_text(encoding="utf-8"))
        self.assertIn("does_not_configure_rtdl_native_optix", SOURCE.read_text(encoding="utf-8"))

    def test_import_stack_calls_autoconfig_before_numba_cuda_import(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def _import_numba_stack")
        body = source[start : source.index("def _activate_numba_cuda_redirector")]
        self.assertIn("_activate_numba_cuda_redirector()", body)
        redirector = source[source.index("def _activate_numba_cuda_redirector") :]
        self.assertIn("configure_numba_cuda_toolchain_environment()", redirector)

    def test_report_records_m40_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "auto-detects the pip CUDA compiler package",
            "does not install packages",
            "does not configure RTDL native OptiX",
            "PTX 8.7 versus PTX 8.4",
            "live Numba partner runs still need process-level exports",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
